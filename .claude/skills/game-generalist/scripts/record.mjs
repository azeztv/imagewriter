#!/usr/bin/env node
/**
 * Records a capture of real play with the game's own sound.
 * Video: Playwright recordVideo. Sound: every connection to an AudioContext destination is redirected
 * into a MediaStreamDestination feeding a MediaRecorder, so nothing reaches the machine's speakers.
 * A magenta flash plus a beep at t=0 mark the start; their offset between the two tracks is measured and
 * both tracks are trimmed to start just after the marker.
 */

import { parseArgs } from "node:util";
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { pathToFileURL } from "node:url";
import { spawnSync } from "node:child_process";
import { findBeepSeconds, findFlashMarker } from "./av_markers.mjs";

const USAGE = `Usage: node record.mjs <url-or-file> --seconds N --out capture.mp4 [options]
  --seconds N           length of the capture after the sync marker (default 10)
  --bot idle|random|FILE.mjs   default idle. A .mjs/.js file exports act(state, elapsedMs) -> ['ArrowLeft', ...] or {keys}
  --size WxH            viewport and video size (default 960x540)
  --autostart           append autostart=1 to the URL query (keeps an existing query)
  --software            use SwiftShader instead of the GPU (for tests)
  --out FILE            the mp4 to write
Sound never reaches the speakers: it goes only to the recorder.`;

// Playwright's screencast only delivers a frame when the compositor finishes one, and a software or busy GPU
// renderer can skip a short flash entirely (a 180 ms flash was missed in about 1 run in 4). 500 ms is 12.5 frames
// of the 25 fps recording: long enough to be caught, and an odd number of half frames so the flash's two edges
// together give a start time good to about half a frame (av_markers.mjs).
const MARKER_FLASH_MS = 500;
const MARKER_BEEP_MS = 100;
const SECONDS_TRIMMED_AFTER_MARKER_END = 0.1;
const SETTLE_BEFORE_MARKER_MS = 400;
// Playwright finalizes the video a little before the session ends, so the page keeps running this long
// after the bot loop; the mux then cuts both tracks to the shorter one.
const TAIL_PAD_MS = 800;
const CAPTURE_ATTEMPTS = 3;
const BOT_TICK_MS = 50;
const RANDOM_KEYS = ["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", " "];
const RANDOM_KEY_CHANGE_MS = 300;

function fail(message, code = 2) {
  console.error(message);
  process.exit(code);
}

function parseCommandLine() {
  try {
    return parseArgs({
      allowPositionals: true,
      options: {
        seconds: { type: "string", default: "10" },
        bot: { type: "string", default: "idle" },
        size: { type: "string", default: "960x540" },
        autostart: { type: "boolean", default: false },
        software: { type: "boolean", default: false },
        out: { type: "string" },
        help: { type: "boolean", short: "h" },
      },
    });
  } catch (error) {
    return fail(error.message.split("\n")[0]);
  }
}

const { positionals, values } = parseCommandLine();
if (values.help) {
  console.log(USAGE);
  process.exit(0);
}
if (positionals.length === 0 || !values.out) {
  console.error(USAGE);
  process.exit(2);
}
const captureSeconds = Number(values.seconds);
if (!Number.isFinite(captureSeconds) || captureSeconds <= 0) fail(`--seconds must be a number above 0, got "${values.seconds}"`);
if (!/^\d+x\d+$/.test(values.size)) fail(`--size must look like 960x540, got "${values.size}"`);
const [videoWidth, videoHeight] = values.size.split("x").map(Number);
const outputPath = resolve(values.out);
const botPathArgument = /\.(mjs|js)$/i.test(values.bot) ? values.bot : null;
if (!botPathArgument && !["idle", "random"].includes(values.bot)) fail(`Unknown --bot ${values.bot}`);

async function loadChromium() {
  try {
    return (await import("playwright")).chromium;
  } catch {
    try {
      const { createRequire } = await import("node:module");
      const baseFolder = (process.env.PLAYWRIGHT_FROM ?? process.cwd()).replace(/[\\/]?$/, "/");
      return createRequire(baseFolder)("playwright").chromium;
    } catch {
      return null;
    }
  }
}

function buildTargetUrl(argument) {
  if (/^(https?|file):/i.test(argument)) return argument;
  const suffixStart = argument.search(/[?#]/);
  const pathPart = suffixStart === -1 ? argument : argument.slice(0, suffixStart);
  const suffix = suffixStart === -1 ? "" : argument.slice(suffixStart);
  return pathToFileURL(resolve(pathPart)).href + suffix;
}

function addAutostartParameter(url) {
  const hashStart = url.indexOf("#");
  const beforeHash = hashStart === -1 ? url : url.slice(0, hashStart);
  const hash = hashStart === -1 ? "" : url.slice(hashStart);
  const separator = beforeHash.includes("?") ? "&" : "?";
  return `${beforeHash}${separator}autostart=1${hash}`;
}

// Runs before page scripts. A game context's destination is swapped for a tap that feeds the recorder
// context, which is muted for the game until the marker has played so the marker beep is the first sound.
function buildRecorderInitScript() {
  return `
(() => {
  const NativeAudioContext = window.AudioContext || window.webkitAudioContext;
  if (!NativeAudioContext) return;
  const nativeConnect = AudioNode.prototype.connect;
  const nativeDisconnect = AudioNode.prototype.disconnect;
  const tapByContext = new WeakMap();
  const recordedChunks = [];
  let recorderContext = null;
  let recorderDestination = null;
  let gameBus = null;
  let markerBus = null;
  let markerContext = null;
  let markerTap = null;
  let mediaRecorder = null;

  function ensureRecorderGraph() {
    if (recorderContext) return;
    recorderContext = new NativeAudioContext();
    recorderDestination = recorderContext.createMediaStreamDestination();
    gameBus = recorderContext.createGain();
    gameBus.gain.value = 0;
    nativeConnect.call(gameBus, recorderDestination);
    markerBus = recorderContext.createGain();
    nativeConnect.call(markerBus, recorderDestination);
  }

  // The marker beep takes the same hop as game sound (context, stream tap, recorder context) so both carry
  // the same delay; a beep fed straight into the recorder would sit earlier than game sound by that delay.
  function tapFor(gameContext, bus) {
    const existingTap = tapByContext.get(gameContext);
    if (existingTap) return existingTap;
    ensureRecorderGraph();
    const tap = gameContext.createMediaStreamDestination();
    const source = recorderContext.createMediaStreamSource(tap.stream);
    nativeConnect.call(source, bus ?? gameBus);
    tapByContext.set(gameContext, tap);
    return tap;
  }

  function isGameDestination(node, target) {
    return target instanceof AudioDestinationNode && node.context instanceof NativeAudioContext;
  }

  // A tap created at the moment of the first sound adds a start-up delay of its own (up to 0.7 s measured), so a
  // game context gets its tap the moment it is made and the stream is already flowing when sound arrives.
  function wrapContextClass(ContextClass) {
    return class extends ContextClass {
      constructor(...constructorArguments) {
        super(...constructorArguments);
        tapFor(this);
      }
    };
  }
  window.AudioContext = wrapContextClass(NativeAudioContext);
  if (window.webkitAudioContext) window.webkitAudioContext = window.AudioContext;

  AudioNode.prototype.connect = function (target, ...rest) {
    if (!isGameDestination(this, target)) return nativeConnect.call(this, target, ...rest);
    nativeConnect.call(this, tapFor(this.context), ...rest);
    return target;
  };
  AudioNode.prototype.disconnect = function (target, ...rest) {
    if (!isGameDestination(this, target)) return nativeDisconnect.call(this, target, ...rest);
    return nativeDisconnect.call(this, tapFor(this.context), ...rest);
  };

  function waitFor(milliseconds) {
    return new Promise((done) => setTimeout(done, milliseconds));
  }

  function nextFrame() {
    return new Promise((done) => requestAnimationFrame(() => done()));
  }

  function blobToBase64(blob) {
    return new Promise((done) => {
      const reader = new FileReader();
      reader.onloadend = () => done(String(reader.result).split(',')[1]);
      reader.readAsDataURL(blob);
    });
  }

  window.__recorderApi = {
    async start() {
      ensureRecorderGraph();
      await recorderContext.resume();
      markerContext = new NativeAudioContext();
      await markerContext.resume();
      markerTap = tapFor(markerContext, markerBus);
      mediaRecorder = new MediaRecorder(recorderDestination.stream, { mimeType: 'audio/webm;codecs=opus' });
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) recordedChunks.push(event.data);
      };
      const started = new Promise((done) => { mediaRecorder.onstart = () => done(); });
      mediaRecorder.start();
      await started;
    },
    async marker(flashMs, beepMs) {
      const overlay = document.createElement('div');
      overlay.style.cssText = 'position:fixed;inset:0;background:#ff00ff;z-index:2147483647;pointer-events:none';
      document.documentElement.appendChild(overlay);
      await nextFrame();
      const oscillator = markerContext.createOscillator();
      const beepGain = markerContext.createGain();
      oscillator.frequency.value = 1000;
      beepGain.gain.value = 0.5;
      nativeConnect.call(oscillator, beepGain);
      nativeConnect.call(beepGain, markerTap);
      oscillator.start();
      oscillator.stop(markerContext.currentTime + beepMs / 1000);
      await waitFor(flashMs);
      overlay.remove();
      gameBus.gain.value = 1;
    },
    async stop() {
      const stopped = new Promise((done) => { mediaRecorder.onstop = () => done(); });
      mediaRecorder.stop();
      await stopped;
      return blobToBase64(new Blob(recordedChunks, { type: 'audio/webm' }));
    },
  };
})();`;
}

const sleep = (milliseconds) => new Promise((done) => setTimeout(done, milliseconds));

async function loadBotAct() {
  if (!botPathArgument) return null;
  const loaded = await import(pathToFileURL(resolve(botPathArgument)).href);
  const act = loaded.act ?? loaded.default?.act ?? loaded.default;
  if (typeof act !== "function") fail(`${botPathArgument} must export act(state, elapsedMs)`);
  return act;
}

// Presses and releases keys so the held set matches what the bot asked for.
async function applyHeldKeys(page, heldKeys, wantedKeys) {
  for (const key of [...heldKeys]) {
    if (wantedKeys.has(key)) continue;
    await page.keyboard.up(key).catch(() => {});
    heldKeys.delete(key);
  }
  for (const key of wantedKeys) {
    if (heldKeys.has(key)) continue;
    await page.keyboard.down(key).catch(() => {});
    heldKeys.add(key);
  }
}

function keysFromBotOutput(botOutput) {
  return new Set(Array.isArray(botOutput) ? botOutput : (botOutput?.keys ?? []));
}

async function readState(page) {
  return page.evaluate(() => (window.__game?.state ? window.__game.state() : null)).catch(() => null);
}

function pickRandomKeys(elapsedMs) {
  const slot = Math.floor(elapsedMs / RANDOM_KEY_CHANGE_MS);
  return new Set([RANDOM_KEYS[slot % RANDOM_KEYS.length]]);
}

async function playForSeconds(page, botAct) {
  const heldKeys = new Set();
  const startedAt = Date.now();
  while (Date.now() - startedAt < captureSeconds * 1000) {
    const elapsedMs = Date.now() - startedAt;
    let wantedKeys = new Set();
    if (values.bot === "random") {
      wantedKeys = pickRandomKeys(elapsedMs);
    } else if (botAct) {
      wantedKeys = keysFromBotOutput(await botAct(await readState(page), elapsedMs));
    }
    await applyHeldKeys(page, heldKeys, wantedKeys);
    await sleep(BOT_TICK_MS);
  }
  await applyHeldKeys(page, heldKeys, new Set());
}

function readDurationSeconds(filePath) {
  const result = spawnSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", filePath], { encoding: "utf8" });
  return Number(result.stdout.trim());
}

// Cuts both tracks to start at the marker, then holds the last picture and adds silence if either track ended
// early (a heavy game can leave Playwright's video shorter than the wall time), so the file is --seconds long.
function muxAligned({ videoPath, audioPath, videoStart, audioStart }) {
  const videoShortfall = Math.max(0, videoStart + captureSeconds - readDurationSeconds(videoPath));
  const audioShortfall = Math.max(0, audioStart + captureSeconds - readDurationSeconds(audioPath));
  if (videoShortfall > 0.05) console.error(`video ended ${videoShortfall.toFixed(2)} s early; holding the last frame`);
  if (audioShortfall > 0.05) console.error(`audio ended ${audioShortfall.toFixed(2)} s early; padding with silence`);
  const result = spawnSync(
    "ffmpeg",
    [
      "-y", "-v", "error",
      "-ss", String(videoStart), "-i", videoPath,
      "-ss", String(audioStart), "-i", audioPath,
      "-map", "0:v", "-map", "1:a",
      "-t", String(captureSeconds),
      "-c:v", "libx264", "-preset", "veryfast", "-crf", "24", "-pix_fmt", "yuv420p",
      "-vf", `tpad=stop_mode=clone:stop_duration=${videoShortfall + 0.2},pad=ceil(iw/2)*2:ceil(ih/2)*2`,
      "-af", `apad=pad_dur=${audioShortfall + 0.2}`,
      "-c:a", "aac", "-b:a", "128k",
      outputPath,
    ],
    { encoding: "utf8" },
  );
  if (result.status !== 0) fail(`ffmpeg mux failed: ${result.stderr}`, 1);
}

// The marker is magenta and found on the chroma channel, so the page's own flashes and Playwright's white blank first
// frame can never be mistaken for it, however slow the machine is.
function findMarkerFlash({ videoPath }) {
  const marker = findFlashMarker(videoPath, { flashMs: MARKER_FLASH_MS, allowLeadingPartial: true, checkPulseLength: true, signal: "chroma" });
  return marker === null ? null : marker.seconds;
}

async function captureFiles(chromium, workFolder, botAct) {
  const launchArguments = values.software
    ? ["--use-gl=swiftshader", "--mute-audio", "--autoplay-policy=no-user-gesture-required"]
    : ["--use-angle=d3d11", "--enable-gpu", "--ignore-gpu-blocklist", "--mute-audio", "--autoplay-policy=no-user-gesture-required"];
  const browser = await chromium.launch({ headless: true, args: launchArguments });
  const context = await browser.newContext({
    viewport: { width: videoWidth, height: videoHeight },
    recordVideo: { dir: workFolder, size: { width: videoWidth, height: videoHeight } },
  });
  await context.addInitScript({ content: buildRecorderInitScript() });
  const page = await context.newPage();
  const builtUrl = buildTargetUrl(positionals[0]);
  await page.goto(values.autostart ? addAutostartParameter(builtUrl) : builtUrl, { waitUntil: "load" });
  await page.evaluate(() => window.__recorderApi.start());
  await sleep(SETTLE_BEFORE_MARKER_MS);
  await page.evaluate(([flashMs, beepMs]) => window.__recorderApi.marker(flashMs, beepMs), [MARKER_FLASH_MS, MARKER_BEEP_MS]);
  await playForSeconds(page, botAct);
  await sleep(TAIL_PAD_MS);
  const audioBase64 = await page.evaluate(() => window.__recorderApi.stop());
  const videoPath = await page.video().path();
  await context.close();
  await browser.close();
  const audioPath = join(workFolder, "audio.webm");
  writeFileSync(audioPath, Buffer.from(audioBase64, "base64"));
  return { videoPath, audioPath };
}

const chromium = await loadChromium();
if (!chromium) fail("playwright is not installed. Install it where you run record.mjs, or point PLAYWRIGHT_FROM at a folder whose node_modules holds it.");
const botAct = await loadBotAct();
mkdirSync(dirname(outputPath), { recursive: true });
const workFolder = mkdtempSync(join(tmpdir(), "record-"));
try {
  let capture = null;
  for (let attempt = 1; attempt <= CAPTURE_ATTEMPTS; attempt += 1) {
    const attemptFolder = join(workFolder, `attempt-${attempt}`);
    mkdirSync(attemptFolder);
    const files = await captureFiles(chromium, attemptFolder, botAct);
    const markers = { ...files, flashSeconds: findMarkerFlash(files), beepSeconds: findBeepSeconds(files.audioPath) };
    capture = markers;
    if (markers.flashSeconds !== null && markers.beepSeconds !== null) break;
    console.error(`attempt ${attempt}: sync marker not found (flash ${markers.flashSeconds}, beep ${markers.beepSeconds})${attempt < CAPTURE_ATTEMPTS ? ", capturing again" : ""}`);
  }
  const { videoPath, audioPath, flashSeconds, beepSeconds } = capture;
  if (flashSeconds === null || beepSeconds === null) {
    fail(`sync marker not found (flash ${flashSeconds}, beep ${beepSeconds}); the page may cover the flash or the audio recorder got no sound`, 1);
  }
  const markerTrimSeconds = MARKER_FLASH_MS / 1000 + SECONDS_TRIMMED_AFTER_MARKER_END;
  muxAligned({
    videoPath,
    audioPath,
    videoStart: flashSeconds + markerTrimSeconds,
    audioStart: beepSeconds + markerTrimSeconds,
  });
  const offsetMs = Math.round((flashSeconds - beepSeconds) * 1000);
  console.log(`audio-video offset used: ${offsetMs} ms (flash at ${flashSeconds.toFixed(3)} s in the video, beep at ${beepSeconds.toFixed(3)} s in the audio)`);
  console.log(`wrote ${outputPath}`);
} finally {
  // RECORD_KEEP_WORK=1 keeps the raw video and audio of every attempt, for finding why a marker was missed.
  if (process.env.RECORD_KEEP_WORK) console.error(`raw captures kept in ${workFolder}`);
  else rmSync(workFolder, { recursive: true, force: true });
}
