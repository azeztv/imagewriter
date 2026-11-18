// Records 3 s of a fixture that beeps and flashes, then checks the mp4 has real sound and that the
// flash and the beep line up. Exit 0 on success or skip, 1 on a failed assertion.
import { spawnSync } from "node:child_process";
import { existsSync, mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { findBeepSeconds, findFlashSeconds } from "../scripts/av_markers.mjs";

// Two frames of the 25 fps recording: a flash is only seen on whole frames (40 ms apart), so a correct alignment
// still measured 49 ms in 1 run in 40 against a 50 ms limit. The faults this guards against are 200 ms and more.
const MAX_OFFSET_SECONDS = 0.08;
const MIN_MAX_VOLUME_DB = -40;
const MAX_DURATION_GAP_SECONDS = 0.25;
const REQUESTED_SECONDS = 3;
const FIXTURE_FLASH_MS = 500;
const HEAVY_REQUESTED_SECONDS = 5;
const testsFolder = dirname(fileURLToPath(import.meta.url));
const recordPath = join(testsFolder, "..", "scripts", "record.mjs");
const fixturePath = join(testsFolder, "fixture-beep.html");
const outputPath = join(mkdtempSync(join(tmpdir(), "record-test-")), "capture.mp4");

const recording = spawnSync(
  process.execPath,
  [recordPath, fixturePath, "--seconds", String(REQUESTED_SECONDS), "--software", "--out", outputPath],
  { encoding: "utf8", env: process.env },
);
const recordingOutput = recording.stdout + recording.stderr;
if (recording.status === 2 && /playwright is not installed/.test(recordingOutput)) {
  console.log(`SKIP: playwright missing.\n${recordingOutput}`);
  process.exit(0);
}

function streamDurationSeconds(filePath, streamSelector) {
  const probe = spawnSync(
    "ffprobe",
    ["-v", "error", "-select_streams", streamSelector, "-show_entries", "stream=duration", "-of", "csv=p=0", filePath],
    { encoding: "utf8" },
  );
  return Number(probe.stdout.trim());
}

const failures = [];
function check(condition, message) {
  if (!condition) failures.push(message);
}

check(recording.status === 0, `record.mjs exit ${recording.status}\n${recordingOutput}`);
check(/audio-video offset used: -?\d+ ms/.test(recordingOutput), "record.mjs should print the offset it used");
check(existsSync(outputPath), "capture.mp4 missing");

if (existsSync(outputPath)) {
  const volume = spawnSync("ffmpeg", ["-v", "info", "-i", outputPath, "-vn", "-af", "volumedetect", "-f", "null", "-"], { encoding: "utf8" });
  const maxVolumeMatch = (volume.stderr ?? "").match(/max_volume: (-?[\d.]+) dB/);
  check(Boolean(maxVolumeMatch), `no audio track or volumedetect output\n${volume.stderr}`);
  if (maxVolumeMatch) {
    check(Number(maxVolumeMatch[1]) > MIN_MAX_VOLUME_DB, `audio is silent: max_volume ${maxVolumeMatch[1]} dB`);
  }

  const videoSeconds = streamDurationSeconds(outputPath, "v:0");
  const audioSeconds = streamDurationSeconds(outputPath, "a:0");
  check(Math.abs(videoSeconds - audioSeconds) < MAX_DURATION_GAP_SECONDS, `video ${videoSeconds} s and audio ${audioSeconds} s differ by more than ${MAX_DURATION_GAP_SECONDS} s`);
  check(videoSeconds > REQUESTED_SECONDS - MAX_DURATION_GAP_SECONDS, `video is ${videoSeconds} s, under the ${REQUESTED_SECONDS} s asked for`);

  const flashSeconds = findFlashSeconds(outputPath, { flashMs: FIXTURE_FLASH_MS });
  // The fixture repeats its event; pair the first whole flash with the beep that starts with it.
  const beepSeconds = flashSeconds === null ? null : findBeepSeconds(outputPath, { notBefore: flashSeconds - MAX_OFFSET_SECONDS * 4 });
  check(flashSeconds !== null, "no flash found in the capture");
  check(beepSeconds !== null, "no beep found in the capture");
  if (flashSeconds !== null && beepSeconds !== null) {
    const offsetSeconds = Math.abs(flashSeconds - beepSeconds);
    console.log(`flash at ${flashSeconds.toFixed(3)} s, beep at ${beepSeconds.toFixed(3)} s, offset ${(offsetSeconds * 1000).toFixed(0)} ms`);
    check(offsetSeconds < MAX_OFFSET_SECONDS, `audio-video offset ${(offsetSeconds * 1000).toFixed(0)} ms is not under ${MAX_OFFSET_SECONDS * 1000} ms`);
  }
}

// A page that redraws with heavy canvas filters every frame must still give a capture as long as asked for.
const heavyOutputPath = join(mkdtempSync(join(tmpdir(), "record-test-heavy-")), "capture.mp4");
const heavyRecording = spawnSync(
  process.execPath,
  [recordPath, join(testsFolder, "fixture-2d-filters.html"), "--seconds", String(HEAVY_REQUESTED_SECONDS), "--bot", "random", "--software", "--out", heavyOutputPath],
  { encoding: "utf8", env: process.env },
);
check(heavyRecording.status === 0, `heavy page: record.mjs exit ${heavyRecording.status}
${heavyRecording.stdout + heavyRecording.stderr}`);
if (existsSync(heavyOutputPath)) {
  const heavyVideoSeconds = streamDurationSeconds(heavyOutputPath, "v:0");
  const heavyAudioSeconds = streamDurationSeconds(heavyOutputPath, "a:0");
  check(heavyVideoSeconds > HEAVY_REQUESTED_SECONDS - MAX_DURATION_GAP_SECONDS, `heavy page: video is ${heavyVideoSeconds} s, under the ${HEAVY_REQUESTED_SECONDS} s asked for`);
  check(heavyAudioSeconds > HEAVY_REQUESTED_SECONDS - MAX_DURATION_GAP_SECONDS, `heavy page: audio is ${heavyAudioSeconds} s, under the ${HEAVY_REQUESTED_SECONDS} s asked for`);
}

if (failures.length > 0) {
  console.error(`FAIL\n${failures.join("\n")}`);
  process.exit(1);
}
console.log(`OK: capture has a non-silent audio track and flash and beep line up under ${MAX_OFFSET_SECONDS * 1000} ms`);
