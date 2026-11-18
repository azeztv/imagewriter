#!/usr/bin/env node
/**
 * Playtest probe for web games that expose the page hook:
 *   window.__game = { state() -> { status: 'playing'|'won'|'lost'|'title'|'paused', progress: number, tick?, dt?, ... },
 *                     restart(), seed(n), step(ticks, keysDown)? }
 * The probe never creates a canvas context: an init script records the context the page asks for,
 * and the per-frame GPU sync reads one pixel back from the page's own context on the largest canvas.
 * Frame time sync (report.json frame_time.method): webgl-readback for webgl/webgl2 pages,
 * 2d-webgl-copy for 2D pages (never getImageData), raf-only when there is no usable canvas.
 * Gate statuses: pass | fail | not_tested. Every gate that is not pass carries "why" and "try".
 * Exit 0: all pass. 1: a gate failed. 3: nothing failed but a gate was not tested. 2: the probe could not run.
 */

import { parseArgs } from "node:util";
import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const USAGE = `Usage: node probe.mjs <url-or-file> --seconds 20 --seed 1 [options]
  --input FILE          replay JSON: [{t, type:'key'|'pointer', key?, x?, y?, action:'down'|'up'|'move'}]
  --bot idle|random|script|FILE.mjs   default: script when --input is given, else random.
                        A .mjs/.js file exports act(state, elapsedMs) -> ['ArrowLeft', ...] or {keys, pointer:{x,y,down}}
  --seed N              first seed (default 1)
  --seeds N             run seeds seed..seed+N-1 and aggregate (default 1)
  --expect won|lost|both  end states gate 2 requires (default both)
  --gates 1,2,4         judge only these gates (others are not_tested)
  --stall-seconds N     softlock limit (default 30, a default)
  --viewport WxH        default 1280x720
  --refresh-hz N        display refresh rate (default 60)
  --frame-budget-ms N   p95 frame time limit (default 1.25 refresh intervals: 20.8 ms at 60 Hz)
  --max-dropped-percent N  frames over 1.5 refresh intervals allowed (default 1)
  --tile-width N        contact sheet tile width (default 480)
  --wallclock-determinism  for games without step(): compare two wall-clock runs
  --out DIR             default ./probe-out
  --autostart           append autostart=1 to the URL query (keeps an existing query), for games that wait on a title screen
  --software            use SwiftShader instead of the GPU (for tests)
  --help
Gates: 1 console_errors, 2 won_and_lost, 3 determinism, 4 frame_time_p95, 5 softlock, 6 controls.`;

const { positionals, values } = parseCommandLine();

function parseCommandLine() {
  try {
    return parseCommandLineStrict();
  } catch (error) {
    return fail(error.message.split("\n")[0]);
  }
}

function parseCommandLineStrict() {
  return parseArgs({
  allowPositionals: true,
  options: {
    seconds: { type: "string", default: "20" },
    seed: { type: "string", default: "1" },
    input: { type: "string" },
    bot: { type: "string" },
    seeds: { type: "string", default: "1" },
    expect: { type: "string", default: "both" },
    gates: { type: "string" },
    "stall-seconds": { type: "string", default: "30" },
    viewport: { type: "string", default: "1280x720" },
    "refresh-hz": { type: "string", default: "60" },
    "frame-budget-ms": { type: "string" },
    "max-dropped-percent": { type: "string", default: "1" },
    "tile-width": { type: "string", default: "480" },
    "wallclock-determinism": { type: "boolean", default: false },
    out: { type: "string", default: "probe-out" },
    software: { type: "boolean", default: false },
    autostart: { type: "boolean", default: false },
    help: { type: "boolean", short: "h" },
  },
  });
}

if (values.help) {
  console.log(USAGE);
  process.exit(0);
}
if (positionals.length === 0) {
  console.error(USAGE);
  process.exit(2);
}

const targetArgument = positionals[0];
const runSeconds = parsePositiveNumber(values.seconds, "--seconds");
const firstSeed = parseIntegerAtLeast(values.seed, -Infinity, "--seed");
const seedCount = parseIntegerAtLeast(values.seeds, 1, "--seeds");
const stallLimitSeconds = parsePositiveNumber(values["stall-seconds"], "--stall-seconds");
// Frame deltas jitter a millisecond or two around vsync without any visible stutter, so the default budget sits a
// quarter interval above the refresh, and a dropped frame (over 1.5 intervals) is counted separately.
const refreshIntervalMs = 1000 / parsePositiveNumber(values["refresh-hz"], "--refresh-hz");
const frameBudgetIsDefault = values["frame-budget-ms"] === undefined;
const frameBudgetMs = frameBudgetIsDefault
  ? Math.round(refreshIntervalMs * 1.25 * 10) / 10
  : parsePositiveNumber(values["frame-budget-ms"], "--frame-budget-ms");
// A dropped frame is one over 1.5 expected intervals; an explicit budget (a slow software run) widens the interval too.
const droppedFrameThresholdMs = 1.5 * Math.max(refreshIntervalMs, frameBudgetMs / 1.25);
const maxDroppedPercent = parsePositiveNumber(values["max-dropped-percent"], "--max-dropped-percent");
const tileWidth = Math.max(100, Number(values["tile-width"]));
if (!/^\d+x\d+$/.test(values.viewport)) fail(`--viewport must look like 1280x720, got "${values.viewport}"`);
const [viewportWidth, viewportHeight] = values.viewport.split("x").map(Number);
if (viewportWidth < 1 || viewportHeight < 1) fail(`--viewport sizes must be at least 1, got "${values.viewport}"`);
const botPathArgument = /\.(mjs|js)$/i.test(values.bot ?? "") ? values.bot : null;
const botKind = botPathArgument ? "module" : (values.bot ?? (values.input ? "script" : "random"));
const outputFolder = resolve(values.out);
const TICK_INTERVAL_MS = 50;
const RESTART_WAIT_MS = 2000;
const DEFAULT_TICK_SECONDS = 1 / 60;
const MAX_DETERMINISM_SECONDS = 10;
const GATE_NAMES = {
  1: "console_errors",
  2: "won_and_lost",
  3: "determinism",
  4: "frame_time_p95",
  5: "softlock",
  6: "controls",
};

function fail(message, code = 2) {
  console.error(message);
  process.exit(code);
}

// A failure that stops the run and exits 2 with a plain message instead of a stack trace.
class ProbeError extends Error {}

function parsePositiveNumber(text, optionName) {
  const number = Number(text);
  if (text === "" || !Number.isFinite(number) || number <= 0) fail(`${optionName} must be a number above 0, got "${text}"`);
  return number;
}

function parseIntegerAtLeast(text, minimum, optionName) {
  const number = Number(text);
  if (!Number.isInteger(number) || number < minimum) fail(`${optionName} must be an integer of at least ${minimum}, got "${text}"`);
  return number;
}

if (!["idle", "random", "script", "module"].includes(botKind)) fail(`Unknown --bot ${botKind}`);
if (botKind === "script" && !values.input) fail("--bot script needs --input replay.json");
if (!["won", "lost", "both"].includes(values.expect)) fail(`--expect must be won, lost or both`);

function parseSelectedGates(gatesArgument) {
  if (!gatesArgument) return new Set(Object.keys(GATE_NAMES).map(Number));
  const gateNumbers = gatesArgument.split(",").map((text) => {
    const trimmed = text.trim();
    const gateNumber = Number(trimmed);
    const valid = /^\d+$/.test(trimmed) && gateNumber >= 1 && gateNumber <= 6;
    if (!valid) fail(`--gates must list integers from 1 to 6, got "${trimmed}"`);
    return gateNumber;
  });
  return new Set(gateNumbers);
}
const selectedGates = parseSelectedGates(values.gates);
const isActingBot = botKind !== "idle";

// Playwright comes from the project, or from PLAYWRIGHT_FROM: a folder whose node_modules has it.
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
const chromium = await loadChromium();
if (!chromium) {
  fail(
    "playwright is not installed. Install it where you run the probe:\n" +
      "  npm install playwright && npx playwright install chromium\n" +
      "or point PLAYWRIGHT_FROM at a folder whose node_modules holds it.",
  );
}

async function loadBotModule() {
  if (!botPathArgument) return null;
  try {
    const loaded = await import(pathToFileURL(resolve(botPathArgument)).href);
    const act = loaded.act ?? loaded.default?.act ?? loaded.default;
    if (typeof act !== "function") fail(`${botPathArgument} must export act(state, elapsedMs)`);
    return act;
  } catch (error) {
    return fail(`Could not load bot module ${botPathArgument}: ${error.message}`);
  }
}
const moduleBotAct = await loadBotModule();

// A local path may carry ?query and #hash; pathToFileURL would percent-encode them into the file name.
function buildTargetUrl(argument) {
  if (/^(https?|file):/i.test(argument)) return argument;
  const suffixStart = argument.search(/[?#]/);
  const pathPart = suffixStart === -1 ? argument : argument.slice(0, suffixStart);
  const suffix = suffixStart === -1 ? "" : argument.slice(suffixStart);
  return pathToFileURL(resolve(pathPart)).href + suffix;
}

// Puts autostart=1 into the query, before any #hash, and keeps the query the caller already had.
function addAutostartParameter(url) {
  const hashStart = url.indexOf("#");
  const beforeHash = hashStart === -1 ? url : url.slice(0, hashStart);
  const hash = hashStart === -1 ? "" : url.slice(hashStart);
  const separator = beforeHash.includes("?") ? "&" : "?";
  return `${beforeHash}${separator}autostart=1${hash}`;
}
const builtTargetUrl = buildTargetUrl(targetArgument);
const targetUrl = values.autostart ? addAutostartParameter(builtTargetUrl) : builtTargetUrl;

const replayEvents = values.input ? JSON.parse(readFileSync(values.input, "utf8")) : [];

function createMulberry32(seedNumber) {
  let state = seedNumber >>> 0;
  return () => {
    state = (state + 0x6d2b79f5) >>> 0;
    let mixed = Math.imul(state ^ (state >>> 15), 1 | state);
    mixed = (mixed + Math.imul(mixed ^ (mixed >>> 7), 61 | mixed)) ^ mixed;
    return ((mixed ^ (mixed >>> 14)) >>> 0) / 4294967296;
  };
}

// Runs before page scripts. It never creates a context: it wraps getContext to remember what the
// page created (a second getContext of another type would return null and break the page), seeds
// Math.random, and times frames with a one-pixel readback from the largest visible canvas.
function buildInitScript(seedNumber) {
  return `
(() => {
  let randomState = ${seedNumber} >>> 0;
  function reseed(seedNumber) { randomState = seedNumber >>> 0; }
  window.__probeReseed = reseed;
  Math.random = () => {
    randomState = (randomState + 0x6d2b79f5) >>> 0;
    let mixed = Math.imul(randomState ^ (randomState >>> 15), 1 | randomState);
    mixed = (mixed + Math.imul(mixed ^ (mixed >>> 7), 61 | mixed)) ^ mixed;
    return ((mixed ^ (mixed >>> 14)) >>> 0) / 4294967296;
  };

  const createdContexts = new Map();
  const originalGetContext = HTMLCanvasElement.prototype.getContext;
  HTMLCanvasElement.prototype.getContext = function (contextType, ...rest) {
    const context = originalGetContext.call(this, contextType, ...rest);
    if (context && !createdContexts.has(this)) {
      const normalizedType = contextType === 'experimental-webgl' ? 'webgl' : contextType;
      createdContexts.set(this, { type: normalizedType, context });
    }
    return context;
  };

  // getImageData every frame makes Chrome move a 2D canvas off GPU acceleration, so the probe would
  // time a slower canvas than the player sees. Copying the canvas into a helper WebGL texture and
  // reading one pixel back forces the GPU to finish the frame without touching the 2D canvas.
  function buildCanvasCopySync(sourceCanvas) {
    const helperCanvas = document.createElement('canvas');
    helperCanvas.width = 1;
    helperCanvas.height = 1;
    const gl = originalGetContext.call(helperCanvas, 'webgl2', { alpha: false, antialias: false, depth: false, stencil: false, powerPreference: 'low-power' });
    if (!gl) return null;
    // One fixed 1x1 texture and framebuffer, built once. Each frame only the top-left pixel of the canvas is
    // copied in place (texSubImage2D), so no storage is reallocated and no full-size copy is made; the copy
    // still waits for the canvas to finish drawing, which is the sync wanted.
    const texture = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, texture);
    gl.texStorage2D(gl.TEXTURE_2D, 1, gl.RGBA8, 1, 1);
    const framebuffer = gl.createFramebuffer();
    gl.bindFramebuffer(gl.FRAMEBUFFER, framebuffer);
    gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, texture, 0);
    const pixel = new Uint8Array(4);
    return () => {
      gl.texSubImage2D(gl.TEXTURE_2D, 0, 0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, sourceCanvas);
      gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, pixel);
    };
  }

  function buildSync(canvas, entry) {
    if (entry.type === 'webgl' || entry.type === 'webgl2') {
      const pixel = new Uint8Array(4);
      return () => entry.context.readPixels(0, 0, 1, 1, entry.context.RGBA, entry.context.UNSIGNED_BYTE, pixel);
    }
    if (entry.type === '2d') return buildCanvasCopySync(canvas);
    return null;
  }

  function findLargestVisibleCanvas() {
    let best = null;
    let bestArea = 0;
    for (const [canvas, entry] of createdContexts) {
      if (!canvas.isConnected || canvas.width === 0 || canvas.height === 0) continue;
      const rect = canvas.getBoundingClientRect();
      const area = rect.width * rect.height;
      if (area > bestArea) {
        bestArea = area;
        best = { canvas, entry };
      }
    }
    return best;
  }

  const syncByCanvas = new WeakMap();
  const stats = { deltas: [], unsyncedDeltas: [], syncedFrames: 0, contextType: null, syncMethod: null, tainted: false };
  window.__probeFrameStats = stats;

  // The last frames of every cycle skip the sync, so the same run yields a plain rAF figure to put
  // beside the synced one. Without it a slow readback and a slow game look the same.
  const FRAMES_PER_CYCLE = 120;
  const UNSYNCED_FRAMES_PER_CYCLE = 30;
  let frameIndex = 0;

  // Returns 'synced', 'skipped' (sync was left out on purpose) or 'none' (no canvas to sync).
  function forceSync() {
    const largest = findLargestVisibleCanvas();
    if (!largest) return 'none';
    if (!syncByCanvas.has(largest.canvas)) syncByCanvas.set(largest.canvas, buildSync(largest.canvas, largest.entry));
    const sync = syncByCanvas.get(largest.canvas);
    if (!sync) return 'none';
    if (frameIndex % FRAMES_PER_CYCLE >= FRAMES_PER_CYCLE - UNSYNCED_FRAMES_PER_CYCLE) return 'skipped';
    try {
      sync();
      stats.syncedFrames += 1;
      stats.contextType = largest.entry.type;
      stats.syncMethod = largest.entry.type === '2d' ? '2d-webgl-copy' : 'webgl-readback';
    } catch (error) {
      // A canvas tainted by cross-origin sprites (file:// pages) cannot be copied: stop syncing it.
      if (error && error.name === 'SecurityError') {
        stats.tainted = true;
        syncByCanvas.set(largest.canvas, null);
        return 'none';
      }
    }
    return 'synced';
  }

  let previousTime = null;
  let previousMode = null;
  function onFrame() {
    frameIndex += 1;
    const mode = forceSync();
    const afterSync = performance.now();
    if (previousTime !== null) {
      if (mode === 'skipped' && previousMode === 'skipped') stats.unsyncedDeltas.push(afterSync - previousTime);
      else if (mode !== 'skipped' && previousMode !== 'skipped') stats.deltas.push(afterSync - previousTime);
    }
    previousTime = afterSync;
    previousMode = mode;
    requestAnimationFrame(onFrame);
  }
  requestAnimationFrame(onFrame);
})();`;
}

const RANDOM_KEYS = ["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", " "];

function buildRandomBotEvents(seedNumber, durationSeconds, { includePointer }) {
  const nextRandom = createMulberry32(seedNumber + 1000);
  const events = [];
  let timeMs = 100;
  while (timeMs < durationSeconds * 1000) {
    if (includePointer && nextRandom() < 0.25) {
      const x = Math.round(nextRandom() * viewportWidth);
      const y = Math.round(nextRandom() * viewportHeight);
      events.push({ t: timeMs, type: "pointer", x, y, action: "move" });
      events.push({ t: timeMs + 20, type: "pointer", x, y, action: "down" });
      events.push({ t: timeMs + 80, type: "pointer", x, y, action: "up" });
    } else {
      const key = RANDOM_KEYS[Math.floor(nextRandom() * RANDOM_KEYS.length)];
      const holdMs = 80 + Math.floor(nextRandom() * 400);
      events.push({ t: timeMs, type: "key", key, action: "down" });
      events.push({ t: timeMs + holdMs, type: "key", key, action: "up" });
    }
    timeMs += 100 + Math.floor(nextRandom() * 500);
  }
  return events.sort((first, second) => first.t - second.t);
}

function eventsForActingRun(seedNumber) {
  if (botKind === "script") return [...replayEvents].sort((first, second) => first.t - second.t);
  if (botKind === "random") return buildRandomBotEvents(seedNumber, runSeconds, { includePointer: true });
  return [];
}

async function dispatchEvent(page, inputEvent) {
  if (inputEvent.type === "key") {
    if (inputEvent.action === "down") await page.keyboard.down(inputEvent.key);
    else await page.keyboard.up(inputEvent.key);
    return;
  }
  if (inputEvent.action === "move") await page.mouse.move(inputEvent.x, inputEvent.y);
  else if (inputEvent.action === "down") await page.mouse.down();
  else await page.mouse.up();
}

// Presses and releases keys so the held set matches what a module bot asked for.
async function applyModuleBotOutput(page, held, botOutput) {
  const wantedKeys = new Set(Array.isArray(botOutput) ? botOutput : (botOutput?.keys ?? []));
  for (const key of [...held.keys]) {
    if (wantedKeys.has(key)) continue;
    await page.keyboard.up(key).catch(() => {});
    held.keys.delete(key);
  }
  for (const key of wantedKeys) {
    if (held.keys.has(key)) continue;
    await page.keyboard.down(key).catch(() => {});
    held.keys.add(key);
  }
  const pointer = Array.isArray(botOutput) ? null : botOutput?.pointer;
  if (!pointer) return wantedKeys.size > 0;
  if (pointer.x !== held.pointerX || pointer.y !== held.pointerY) {
    await page.mouse.move(pointer.x, pointer.y).catch(() => {});
    held.pointerX = pointer.x;
    held.pointerY = pointer.y;
  }
  const wantDown = Boolean(pointer.down);
  if (wantDown !== held.pointerDown) {
    await (wantDown ? page.mouse.down() : page.mouse.up()).catch(() => {});
    held.pointerDown = wantDown;
  }
  return wantedKeys.size > 0 || wantDown;
}

function botAsksForInput(botOutput) {
  const keys = Array.isArray(botOutput) ? botOutput : (botOutput?.keys ?? []);
  return keys.length > 0 || Boolean(botOutput?.pointer?.down);
}

const sleep = (milliseconds) => new Promise((done) => setTimeout(done, milliseconds));
const MIN_UNSYNCED_SAMPLES = 20;
const percentile = (sortedValues, fraction) =>
  sortedValues.length === 0
    ? null
    : sortedValues[Math.min(sortedValues.length - 1, Math.floor(fraction * sortedValues.length))];
const hashOf = (text) => createHash("sha256").update(String(text)).digest("hex");

async function readState(page) {
  return page.evaluate(() => (window.__game?.state ? window.__game.state() : null)).catch(() => null);
}

async function openGamePage(browser, seedNumber) {
  const context = await browser.newContext({ viewport: { width: viewportWidth, height: viewportHeight } });
  await context.addInitScript({ content: buildInitScript(seedNumber) });
  const page = await context.newPage();
  const consoleErrors = [];
  page.on("console", (message) => {
    if (message.type() !== "error") return;
    if (/favicon/i.test(message.location().url ?? "")) return;
    consoleErrors.push(message.text());
  });
  page.on("pageerror", (error) => consoleErrors.push(`pageerror: ${error.message}`));
  const loadStart = Date.now();
  try {
    await page.goto(targetUrl, { waitUntil: "load" });
  } catch (error) {
    await context.close().catch(() => {});
    throw new ProbeError(`Could not open ${targetUrl}: ${error.message.split("\n")[0]}`);
  }
  const loadMs = Date.now() - loadStart;
  const hookPresent = await page.evaluate(() => Boolean(window.__game?.state));
  return { context, page, consoleErrors, loadMs, hookPresent };
}

// Updates the end-state flags and the stall clock for one state read; restarts after an end state.
async function observeState(page, state, run) {
  run.statusesSeen.add(state.status);
  run.lastStateJson = JSON.stringify(state);
  const progress = Number(state.progress);
  if (Number.isFinite(progress)) run.maxProgress = Math.max(run.maxProgress, progress);

  if (state.status === "playing") {
    if (Number.isFinite(progress) && progress > run.roundBestProgress) {
      run.roundBestProgress = progress;
      run.stallStartMs = null;
    } else if (run.stallStartMs === null) {
      run.stallStartMs = Date.now();
    }
    if (run.stallStartMs !== null) {
      run.longestStallSeconds = Math.max(run.longestStallSeconds, (Date.now() - run.stallStartMs) / 1000);
    }
    return;
  }
  // Waiting on a title screen or a pause is not a softlock: the stall clock stops there too.
  if (state.status === "title" || state.status === "paused") {
    run.stallStartMs = null;
    return;
  }
  if (state.status !== "won" && state.status !== "lost") return;

  // The stall clock pauses on an end state, and the end state stays recorded across restarts.
  if (state.status === "won") run.reachedWon = true;
  if (state.status === "lost") run.reachedLost = true;
  run.stallStartMs = null;
  run.restartAttempts += 1;
  await page.evaluate(() => window.__game.restart?.()).catch(() => {});
  let backToPlaying = false;
  const restartDeadline = Date.now() + RESTART_WAIT_MS;
  while (Date.now() < restartDeadline && !backToPlaying) {
    await sleep(100);
    backToPlaying = (await readState(page))?.status === "playing";
  }
  if (!backToPlaying) run.restartFailures += 1;
  run.roundBestProgress = -Infinity;
}

async function runActingSeed(browser, seedNumber, { takeShots }) {
  const { context, page, consoleErrors, loadMs, hookPresent } = await openGamePage(browser, seedNumber);
  if (hookPresent) await page.evaluate((value) => window.__game.seed?.(value), seedNumber);

  const run = {
    seedNumber,
    hookPresent,
    consoleErrors,
    loadMs,
    statusesSeen: new Set(),
    reachedWon: false,
    reachedLost: false,
    lastStateJson: "null",
    maxProgress: -Infinity,
    roundBestProgress: -Infinity,
    stallStartMs: null,
    longestStallSeconds: 0,
    restartAttempts: 0,
    restartFailures: 0,
    inputResponseMs: null,
  };
  const events = eventsForActingRun(seedNumber);
  const heldByModuleBot = { keys: new Set(), pointerX: null, pointerY: null, pointerDown: false };
  const shots = [];
  let firstInputAtMs = null;
  let baselineStateJson = null;
  let nextEventIndex = 0;
  let nextShotAtMs = 0;
  const shotEveryMs = Math.max(1000, (runSeconds * 1000) / 6);
  const startedAt = Date.now();

  async function markFirstInput() {
    if (firstInputAtMs !== null) return;
    firstInputAtMs = Date.now();
    baselineStateJson = JSON.stringify(await readState(page));
  }

  while (Date.now() - startedAt < runSeconds * 1000) {
    const elapsedMs = Date.now() - startedAt;
    while (nextEventIndex < events.length && events[nextEventIndex].t <= elapsedMs) {
      await markFirstInput();
      await dispatchEvent(page, events[nextEventIndex]).catch(() => {});
      nextEventIndex += 1;
    }
    const state = hookPresent ? await readState(page) : null;
    if (state) {
      if (moduleBotAct) {
        let botOutput;
        try {
          botOutput = await moduleBotAct(state, elapsedMs);
        } catch (error) {
          await context.close().catch(() => {});
          throw new ProbeError(`bot threw: ${error.message}`);
        }
        if (botAsksForInput(botOutput)) await markFirstInput();
        await applyModuleBotOutput(page, heldByModuleBot, botOutput);
      }
      if (firstInputAtMs !== null && run.inputResponseMs === null && JSON.stringify(state) !== baselineStateJson) {
        run.inputResponseMs = Date.now() - firstInputAtMs;
      }
      await observeState(page, state, run);
    }
    if (takeShots && elapsedMs >= nextShotAtMs) {
      nextShotAtMs = elapsedMs + shotEveryMs;
      shots.push(await page.screenshot({ type: "png" }).catch(() => null));
    }
    await sleep(TICK_INTERVAL_MS);
  }

  const finalState = hookPresent ? await readState(page) : null;
  const frameStats = await page.evaluate(() => window.__probeFrameStats).catch(() => null);
  const pageText = await page.evaluate(() => document.body?.innerText ?? "").catch(() => "");
  await context.close();
  return {
    ...run,
    statusesSeen: [...run.statusesSeen],
    finalStateJson: JSON.stringify(finalState),
    frameDeltas: (frameStats?.deltas ?? []).slice(5),
    unsyncedFrameDeltas: frameStats?.unsyncedDeltas ?? [],
    syncedFrames: frameStats?.syncedFrames ?? 0,
    contextType: frameStats?.contextType ?? null,
    syncMethod: frameStats?.syncMethod ?? null,
    canvasTainted: frameStats?.tainted ?? false,
    pageText,
    shots: shots.filter(Boolean),
  };
}

// Turns timed key events into [{ticks, keys}] segments; pointer events cannot be replayed by tick.
function buildTickPlan(inputEvents, tickSeconds) {
  const keyEvents = inputEvents.filter((inputEvent) => inputEvent.type === "key");
  const skippedPointerEvents = inputEvents.length - keyEvents.length;
  const heldKeys = new Set();
  const segments = [];
  let cursorTick = 0;
  for (const keyEvent of keyEvents) {
    const targetTick = Math.round(keyEvent.t / 1000 / tickSeconds);
    if (targetTick > cursorTick) {
      segments.push({ ticks: targetTick - cursorTick, keys: [...heldKeys] });
      cursorTick = targetTick;
    }
    if (keyEvent.action === "down") heldKeys.add(keyEvent.key);
    else heldKeys.delete(keyEvent.key);
  }
  segments.push({ ticks: Math.round(1 / tickSeconds), keys: [...heldKeys] });
  return { segments, skippedPointerEvents };
}

function eventsForDeterminism(seedNumber) {
  if (botKind === "script") return [...replayEvents].sort((first, second) => first.t - second.t);
  const durationSeconds = Math.min(runSeconds, MAX_DETERMINISM_SECONDS);
  return buildRandomBotEvents(seedNumber, durationSeconds, { includePointer: false });
}

// The whole replay runs inside one evaluate, so no animation frame can advance the game between ticks.
async function replayByTicks(page, seedNumber, segments) {
  return page.evaluate(
    ({ seedNumber: seedValue, segments: plan }) => {
      window.__probeReseed?.(seedValue);
      window.__game.seed?.(seedValue);
      window.__game.restart?.();
      const initialStateJson = JSON.stringify(window.__game.state());
      for (const segment of plan) window.__game.step(segment.ticks, segment.keys);
      return { initialStateJson, finalStateJson: JSON.stringify(window.__game.state()) };
    },
    { seedNumber, segments },
  );
}

async function runStepDeterminism(browser, seedNumber) {
  const { context, page, consoleErrors } = await openGamePage(browser, seedNumber);
  const hasStep = await page.evaluate(() => typeof window.__game?.step === "function").catch(() => false);
  if (!hasStep) {
    await context.close();
    return { hasStep: false, consoleErrors };
  }
  const reportedTickSeconds = await page.evaluate(() => window.__game.state()?.dt).catch(() => null);
  const tickSeconds = reportedTickSeconds > 0 ? reportedTickSeconds : DEFAULT_TICK_SECONDS;
  const { segments, skippedPointerEvents } = buildTickPlan(eventsForDeterminism(seedNumber), tickSeconds);
  const totalTicks = segments.reduce((sum, segment) => sum + segment.ticks, 0);
  let first;
  let second;
  try {
    first = await replayByTicks(page, seedNumber, segments);
    second = await replayByTicks(page, seedNumber, segments);
  } catch (error) {
    await context.close().catch(() => {});
    return { hasStep: true, consoleErrors, seedNumber, stepError: error.message.split("\n")[0].replace(/^page\.evaluate: /, "") };
  }
  await context.close();
  return {
    hasStep: true,
    consoleErrors,
    seedNumber,
    totalTicks,
    skippedPointerEvents,
    firstHash: hashOf(first.finalStateJson),
    secondHash: hashOf(second.finalStateJson),
    stateChanged: first.finalStateJson !== first.initialStateJson,
    firstStateJson: first.finalStateJson,
    secondStateJson: second.finalStateJson,
  };
}

const README_NAMES = ["README.md", "readme.md", "README.txt"];

function findControlsInLocalReadme() {
  const targetPath = fileURLToPath(targetUrl.split("?")[0]);
  const readmePath = README_NAMES.map((name) => join(dirname(targetPath), name)).find((candidate) => existsSync(candidate));
  return Boolean(readmePath && /controls/i.test(readFileSync(readmePath, "utf8")));
}

// Over http the README beside the page is fetched from the same folder the page was served from.
async function findControlsInServedReadme() {
  for (const name of README_NAMES) {
    try {
      const response = await fetch(new URL(name, targetUrl));
      if (response.ok && /controls/i.test(await response.text())) return true;
    } catch {
      // An unreachable README is the same as no README.
    }
  }
  return false;
}

async function findControlsInReadme() {
  if (targetUrl.startsWith("file:")) return findControlsInLocalReadme();
  if (/^https?:/.test(targetUrl)) return findControlsInServedReadme();
  return false;
}

// Fills the grid row by row: columns = min(tiles, 3), so no row is ever empty.
async function writeContactSheet(browser, shots) {
  if (shots.length === 0) return;
  const columns = Math.min(shots.length, 3);
  const gap = 4;
  const images = shots.map((shot) => `<img src="data:image/png;base64,${shot.toString("base64")}">`).join("");
  const page = await browser.newPage({ viewport: { width: columns * tileWidth + (columns - 1) * gap, height: 200 } });
  await page.setContent(
    `<body style="margin:0;background:#000;display:grid;grid-template-columns:repeat(${columns},${tileWidth}px);gap:${gap}px">` +
      `${images}<style>img{width:${tileWidth}px;display:block}</style></body>`,
  );
  await page.screenshot({ path: join(outputFolder, "sheet.png"), fullPage: true });
  await page.close();
}

function makeGate(status, detail, why = null, nextAction = null) {
  const gate = { status, detail };
  if (status !== "pass") {
    gate.why = why ?? detail;
    gate.try = nextAction ?? "inspect the detail above";
  }
  return gate;
}

const notSelectedGate = (gateNumber) =>
  makeGate("not_tested", "not selected", "not selected", `add ${gateNumber} to --gates`);

const noHookGate = () =>
  makeGate(
    "not_tested",
    "window.__game hook missing",
    "window.__game.state() is missing, so the probe cannot read the game",
    "expose window.__game = { state, restart, seed } (see the hook contract)",
  );

function judgeConsoleErrors(allErrors) {
  if (allErrors.length === 0) return makeGate("pass", "none");
  const summary = `${allErrors.length}: ${allErrors.slice(0, 3).join(" | ")}`;
  return makeGate("fail", summary, `${allErrors.length} console error(s), first: ${allErrors[0]}`, "fix the first error, then rerun");
}

function judgeEndStates(runs) {
  const statuses = new Set(runs.flatMap((run) => run.statusesSeen));
  const reachedWon = runs.some((run) => run.reachedWon);
  const reachedLost = runs.some((run) => run.reachedLost);
  const restartAttempts = runs.reduce((sum, run) => sum + run.restartAttempts, 0);
  const restartFailures = runs.reduce((sum, run) => sum + run.restartFailures, 0);
  const restartStatus = restartAttempts === 0 ? "not_tested" : restartFailures === 0 ? "pass" : "fail";
  const subChecks = { reached_won: reachedWon, reached_lost: reachedLost, restart_ok: restartStatus };
  const needWon = values.expect !== "lost";
  const needLost = values.expect !== "won";
  const detail =
    `expect ${values.expect}; won ${reachedWon}, lost ${reachedLost}, restart ${restartAttempts} tries, ` +
    `${restartFailures} failed to return to playing within ${RESTART_WAIT_MS / 1000} s`;
  const missing = [];
  if (needWon && !reachedWon) missing.push("won");
  if (needLost && !reachedLost) missing.push("lost");
  let gate;
  if (missing.length > 0) {
    const lastState = runs[runs.length - 1].lastStateJson;
    gate = makeGate(
      "fail",
      detail,
      `never reached ${missing.join(" and ")}; statuses seen: ${[...statuses].join(", ")}; last state: ${lastState}`,
      "use a bot that can reach it (--bot FILE.mjs), run longer (--seconds), or set --expect to the end state that is reachable",
    );
  } else if (restartFailures > 0) {
    gate = makeGate(
      "fail",
      detail,
      `${restartFailures} of ${restartAttempts} restarts did not return status to playing within ${RESTART_WAIT_MS / 1000} s`,
      "make restart() reset status to playing synchronously",
    );
  } else {
    gate = makeGate("pass", detail);
  }
  return { ...gate, sub_checks: subChecks };
}

function judgeDeterminism(determinismRuns, wallclock, hookPresent) {
  if (!hookPresent) return noHookGate();
  if (wallclock) {
    const same = wallclock.firstHash === wallclock.secondHash;
    const detail = `wall clock: ${wallclock.firstHash.slice(0, 12)} vs ${wallclock.secondHash.slice(0, 12)}`;
    return same
      ? makeGate("pass", detail)
      : makeGate("fail", detail, "two wall-clock runs of the same seed ended in different states (expected for any game driven by frame or wall time)", "add window.__game.step() and rerun, or remove unseeded randomness and time reads");
  }
  if (determinismRuns.length === 0 || !determinismRuns[0].hasStep) {
    return makeGate(
      "not_tested",
      "window.__game.step missing",
      "window.__game.step(ticks, keysDown) is missing, and a wall-clock repeat run is not repeatable enough to judge",
      "add step(ticks, keysDown) that advances the fixed-step simulation synchronously, or pass --wallclock-determinism",
    );
  }
  const throwing = determinismRuns.find((run) => run.stepError);
  if (throwing) {
    return makeGate(
      "fail",
      `step() threw on seed ${throwing.seedNumber}`,
      `step() threw: ${throwing.stepError}`,
      "fix the exception in step()",
    );
  }
  const mismatches = determinismRuns.filter((run) => run.firstHash !== run.secondHash);
  const first = determinismRuns[0];
  const notes = [];
  if (first.skippedPointerEvents > 0) notes.push(`${first.skippedPointerEvents} pointer events skipped`);
  if (determinismRuns.every((run) => !run.stateChanged)) notes.push("state never changed, so input may not reach step()");
  const detail =
    `${determinismRuns.length} seed(s), ${first.totalTicks} ticks each: ${first.firstHash.slice(0, 12)} vs ${first.secondHash.slice(0, 12)}` +
    (notes.length > 0 ? ` (${notes.join("; ")})` : "");
  if (mismatches.length === 0) return makeGate("pass", detail);
  const bad = mismatches[0];
  return makeGate(
    "fail",
    detail,
    `seed ${bad.seedNumber} replayed twice by ticks gave ${bad.firstHash.slice(0, 12)} vs ${bad.secondHash.slice(0, 12)}; run 1 ${bad.firstStateJson.slice(0, 120)}, run 2 ${bad.secondStateJson.slice(0, 120)}`,
    "make step() depend only on the seed and the keys given; remove Date.now, performance.now and unseeded Math.random from the simulation",
  );
}

function summarizeFrames(runs) {
  const frames = runs.flatMap((run) => run.frameDeltas).sort((first, second) => first - second);
  const unsyncedFrames = runs.flatMap((run) => run.unsyncedFrameDeltas).sort((first, second) => first - second);
  const syncedFrames = runs.reduce((sum, run) => sum + run.syncedFrames, 0);
  const contextType = runs.map((run) => run.contextType).find(Boolean) ?? null;
  const syncMethod = runs.map((run) => run.syncMethod).find(Boolean) ?? null;
  const usesSync = syncedFrames > 0 && syncedFrames >= frames.length / 2;
  const canvasTainted = runs.some((run) => run.canvasTainted);
  return {
    frames,
    method: usesSync && !canvasTainted ? syncMethod : "raf-only",
    canvas_tainted: canvasTainted,
    context_type: contextType,
    samples: frames.length,
    p50: percentile(frames, 0.5),
    p95: percentile(frames, 0.95),
    p99: percentile(frames, 0.99),
    dropped_percent: frames.length > 0
      ? (100 * frames.filter((delta) => delta > droppedFrameThresholdMs).length) / frames.length
      : null,
    unsynced_samples: unsyncedFrames.length,
    unsynced_p50: percentile(unsyncedFrames, 0.5),
    unsynced_p95: percentile(unsyncedFrames, 0.95),
  };
}

function judgeFrameTime(summary) {
  if (summary.canvas_tainted) {
    return makeGate(
      "not_tested",
      "canvas tainted (file:// sprites): serve over http",
      "canvas tainted (file:// sprites): serve over http",
      "serve the folder over http and rerun",
    );
  }
  if (summary.p95 === null) {
    return makeGate("fail", "no frames recorded", "the page requested no animation frames during the run", "check the game starts rendering on load and the run lasts long enough");
  }
  const methodNote = summary.method === "raf-only"
    ? "no page-created canvas context found, so rAF deltas only (no GPU sync)"
    : summary.method === "2d-webgl-copy"
      ? "GPU sync by copying the 2d canvas into a helper WebGL texture"
      : `readback from the page's ${summary.context_type} context`;
  const budgetNote = frameBudgetIsDefault ? " (default)" : "";
  const hasUnsyncedFigure = summary.unsynced_samples >= MIN_UNSYNCED_SAMPLES;
  const unsyncedNote = hasUnsyncedFigure
    ? `; unsynced rAF p50 ${summary.unsynced_p50.toFixed(1)} ms, p95 ${summary.unsynced_p95.toFixed(1)} ms`
    : "";
  const detail =
    `p50 ${summary.p50.toFixed(1)} ms, p95 ${summary.p95.toFixed(1)} ms, p99 ${summary.p99.toFixed(1)} ms, ` +
    `budget ${frameBudgetMs} ms${budgetNote}; dropped ${summary.dropped_percent.toFixed(1)}% ` +
    `(over ${droppedFrameThresholdMs.toFixed(1)} ms, limit ${maxDroppedPercent}%); ${methodNote}${unsyncedNote}`;
  // The synced figure is the gate on every page; the unsynced rAF figure (a short sample) is advisory only.
  const droppedTooMany = summary.dropped_percent > maxDroppedPercent;
  if (summary.p95 <= frameBudgetMs && !droppedTooMany) return makeGate("pass", detail);
  const cause = droppedTooMany
    ? `${summary.dropped_percent.toFixed(1)}% of frames dropped (over ${droppedFrameThresholdMs.toFixed(1)} ms)`
    : `p95 ${summary.p95.toFixed(1)} ms is over the ${frameBudgetMs} ms budget`;
  return makeGate(
    "fail",
    detail,
    cause,
    "profile the slowest frame; on --software runs raise --frame-budget-ms, the CPU renderer is slow",
  );
}

function judgeSoftlock(runs) {
  if (!runs.every((run) => run.hookPresent)) return noHookGate();
  if (!isActingBot) {
    return makeGate(
      "not_tested",
      "idle bot never acts",
      "the idle bot presses nothing, so a lack of progress proves nothing",
      "rerun with --bot random, --bot FILE.mjs or --input replay.json",
    );
  }
  const longestStall = Math.max(...runs.map((run) => run.longestStallSeconds));
  const detail = `longest stall ${longestStall.toFixed(1)} s, limit ${stallLimitSeconds} s${values["stall-seconds"] === "30" ? " (default)" : ""}`;
  if (longestStall <= stallLimitSeconds) return makeGate("pass", detail);
  return makeGate(
    "fail",
    detail,
    `progress did not rise for ${longestStall.toFixed(1)} s while status was playing`,
    "find where the bot got stuck (sheet.png) and add a way out or a timer",
  );
}

function judgeControls(runs, readmeHasControls) {
  const found = runs.some((run) => /controls/i.test(run.pageText)) || readmeHasControls;
  if (found) return makeGate("pass", "controls listed");
  return makeGate(
    "fail",
    "no 'controls' text on the page or in a README beside the file",
    "players cannot see which keys or buttons to use",
    "show a Controls line on the title screen or in a README beside the file",
  );
}

function printPlan() {
  const secondsPerSeed = runSeconds + 3;
  const wallclockExtra = values["wallclock-determinism"] && selectedGates.has(3) ? secondsPerSeed : 0;
  const stepExtra = selectedGates.has(3) ? seedCount * 2 : 0;
  const actingTotal = [...selectedGates].some((gate) => gate !== 3) ? seedCount * secondsPerSeed : 0;
  const expected = Math.round(actingTotal + wallclockExtra + stepExtra + 5);
  console.log(`Expected wall time about ${expected} s. Plan, bot ${botKind}, gates ${[...selectedGates].join(",")}:`);
  for (let offset = 0; offset < seedCount; offset += 1) {
    const seedNumber = firstSeed + offset;
    const acting = actingTotal > 0 ? `play ${runSeconds} s` : "no play";
    const determinism = selectedGates.has(3)
      ? "; determinism by step() ticks if present (about 1 s), else not_tested"
      : "";
    console.log(`  seed ${seedNumber}: ${acting}${determinism}`);
  }
  if (wallclockExtra > 0) console.log(`  wall-clock determinism pair on seed ${firstSeed} if step() is missing`);
}

const launchArguments = values.software
  ? ["--use-gl=swiftshader", "--mute-audio"]
  : process.platform === "win32"
    ? ["--use-angle=d3d11", "--enable-gpu", "--ignore-gpu-blocklist", "--mute-audio"]
    : ["--mute-audio"];

async function collectReport(browser) {
  const seedNumbers = Array.from({ length: seedCount }, (_, offset) => firstSeed + offset);
  const needsPlay = [...selectedGates].some((gate) => gate !== 3);
  const runs = [];
  if (needsPlay) {
    for (const seedNumber of seedNumbers) {
      runs.push(await runActingSeed(browser, seedNumber, { takeShots: seedNumber === firstSeed }));
    }
    await writeContactSheet(browser, runs[0].shots);
  }

  let hookPresent = runs.length > 0 && runs.every((run) => run.hookPresent);
  const determinismRuns = [];
  let wallclock = null;
  if (selectedGates.has(3)) {
    if (!needsPlay) {
      const probePage = await openGamePage(browser, firstSeed);
      hookPresent = probePage.hookPresent;
      await probePage.context.close();
    }
    if (hookPresent) {
      for (const seedNumber of seedNumbers) {
        const result = await runStepDeterminism(browser, seedNumber);
        determinismRuns.push(result);
        if (!result.hasStep) break;
      }
      const stepMissing = determinismRuns.length > 0 && !determinismRuns[0].hasStep;
      if (stepMissing && values["wallclock-determinism"]) {
        const repeatRun = await runActingSeed(browser, firstSeed, { takeShots: false });
        const baseline = runs[0] ?? (await runActingSeed(browser, firstSeed, { takeShots: false }));
        wallclock = { firstHash: hashOf(baseline.finalStateJson), secondHash: hashOf(repeatRun.finalStateJson) };
        runs.push({ ...repeatRun, repeatOnly: true });
      }
    }
  }

  const playRuns = runs.filter((run) => !run.repeatOnly);
  const allErrors = [...runs.flatMap((run) => run.consoleErrors), ...determinismRuns.flatMap((run) => run.consoleErrors)];
  const frameSummary = playRuns.length > 0 ? summarizeFrames(playRuns) : null;
  const readmeHasControls = selectedGates.has(6) ? await findControlsInReadme() : false;
  const judges = {
    1: () => judgeConsoleErrors(allErrors),
    2: () => (hookPresent ? judgeEndStates(playRuns) : noHookGate()),
    3: () => judgeDeterminism(determinismRuns, wallclock, hookPresent),
    4: () => judgeFrameTime(frameSummary),
    5: () => judgeSoftlock(playRuns),
    6: () => judgeControls(playRuns, readmeHasControls),
  };
  const gates = {};
  for (const [gateNumber, gateName] of Object.entries(GATE_NAMES)) {
    gates[gateName] = selectedGates.has(Number(gateNumber)) ? judges[gateNumber]() : notSelectedGate(gateNumber);
  }

  return {
    target: targetUrl,
    bot: botPathArgument ?? botKind,
    expect: values.expect,
    seeds: seedNumbers,
    gates,
    frame_time: frameSummary && {
      method: frameSummary.method,
      canvas_tainted: frameSummary.canvas_tainted,
      context_type: frameSummary.context_type,
      samples: frameSummary.samples,
      p50_ms: frameSummary.p50,
      p95_ms: frameSummary.p95,
      p99_ms: frameSummary.p99,
      dropped_percent: frameSummary.dropped_percent,
      budget_ms: frameBudgetMs,
      unsynced_raf_samples: frameSummary.unsynced_samples,
      unsynced_raf_p50_ms: frameSummary.unsynced_p50,
      unsynced_raf_p95_ms: frameSummary.unsynced_p95,
    },
    advisory: {
      load_ms: playRuns[0] ? Math.round(playRuns[0].loadMs) : null,
      input_response_ms: playRuns[0]?.inputResponseMs ?? null,
      input_response_note: "polled every 50 ms, so coarse",
      max_progress: playRuns.length > 0 ? Math.max(...playRuns.map((run) => run.maxProgress)) : null,
    },
  };
}

function exitCodeFor(report) {
  // A gate left out with --gates was not asked for, so it must not turn a clean subset run into exit 3.
  const judgedGates = Object.values(report.gates).filter((gate) => gate.detail !== "not selected");
  const statuses = judgedGates.map((gate) => gate.status);
  if (statuses.includes("fail")) return 1;
  if (statuses.includes("not_tested")) return 3;
  return 0;
}

printPlan();
let browser;
try {
  browser = await chromium.launch({ headless: true, args: launchArguments });
} catch (error) {
  fail(`Could not launch chromium (${error.message}). Try: npx playwright install chromium`);
}

mkdirSync(outputFolder, { recursive: true });
let report;
try {
  report = await collectReport(browser);
} catch (error) {
  await browser.close().catch(() => {});
  fail(error instanceof ProbeError ? error.message : `probe failed: ${error.stack ?? error.message}`);
}
await browser.close();

writeFileSync(join(outputFolder, "report.json"), JSON.stringify(report, null, 2));
for (const [gateName, gate] of Object.entries(report.gates)) {
  console.log(`${gate.status.toUpperCase()}  ${gateName}: ${gate.detail}`);
  if (gate.status !== "pass") {
    console.log(`  why: ${gate.why}`);
    console.log(`  try: ${gate.try}`);
  }
}
process.exit(exitCodeFor(report));
