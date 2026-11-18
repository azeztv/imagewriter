// Unit test for the flash finder in scripts/av_markers.mjs on synthetic brightness sequences (no browser, no ffmpeg).
import { flashFromFrames } from "../scripts/av_markers.mjs";

const FRAME_SECONDS = 0.04;
const DARK = 32;
const BRIGHT = 235;
const FLASH_MS = 500;
const OPTIONS = { flashMs: FLASH_MS, allowLeadingPartial: true, checkPulseLength: true };

// Builds frames at 25 fps from [seconds, luma] runs.
function framesFromRuns(runs) {
  const frames = [];
  let time = 0;
  for (const [seconds, luma] of runs) {
    for (let count = 0; count < Math.round(seconds / FRAME_SECONDS); count += 1) {
      frames.push({ time: Number(time.toFixed(3)), luma });
      time += FRAME_SECONDS;
    }
  }
  return frames;
}

const failures = [];
function check(condition, message) {
  if (!condition) failures.push(message);
}

// (a) A long bright blank lead-in, then a real full flash: the real flash is the marker.
const blankThenPulse = flashFromFrames(framesFromRuns([[0.24, BRIGHT], [0.4, DARK], [0.5, BRIGHT], [1.0, DARK]]), OPTIONS);
check(blankThenPulse !== null && !blankThenPulse.leadingPartial, "(a) should pick the full pulse, got " + JSON.stringify(blankThenPulse));
check(blankThenPulse !== null && Math.abs(blankThenPulse.seconds - 0.64) < 0.06, "(a) wrong time " + blankThenPulse?.seconds);

// (b) The capture opens inside the marker, one frame from its start: accepted, dated from the falling edge.
const partialMarker = flashFromFrames(framesFromRuns([[0.48, BRIGHT], [1.5, DARK]]), OPTIONS);
check(partialMarker !== null && partialMarker.leadingPartial, "(b) should accept the leading partial marker, got " + JSON.stringify(partialMarker));
check(partialMarker !== null && Math.abs(partialMarker.seconds) < 0.06, "(b) wrong time " + partialMarker?.seconds);

// (c) Only a long bright blank lead-in, no flash after it: no marker, so the recorder captures again.
for (const blankSeconds of [0.12, 0.24, 0.32]) {
  const blankOnly = flashFromFrames(framesFromRuns([[blankSeconds, BRIGHT], [2.0, DARK]]), OPTIONS);
  check(blankOnly === null, `(c) a ${blankSeconds} s blank start alone should give no marker, got ` + JSON.stringify(blankOnly));
}

// (d) The capture opens inside the marker and the game's own full flash follows: the marker still wins.
const partialThenGamePulse = flashFromFrames(framesFromRuns([[0.48, BRIGHT], [0.3, DARK], [0.5, BRIGHT], [1.0, DARK]]), OPTIONS);
check(partialThenGamePulse !== null && partialThenGamePulse.leadingPartial, "(d) should keep the leading marker, got " + JSON.stringify(partialThenGamePulse));

// (e) A bright start longer than the flash (a stalled screencast) is no marker even though a full pulse follows.
const stalledStart = flashFromFrames(framesFromRuns([[0.76, BRIGHT], [0.52, DARK], [0.5, BRIGHT], [1.0, DARK]]), OPTIONS);
check(stalledStart === null, "(e) a bright start longer than the flash should give no marker, got " + JSON.stringify(stalledStart));

// (f) Chroma mode: a long white blank start and the game's white flashes do not register; only the magenta marker does.
function chromaFrames(runs) {
  const frames = [];
  let time = 0;
  for (const [seconds, luma, redChroma] of runs) {
    for (let count = 0; count < Math.round(seconds / FRAME_SECONDS); count += 1) {
      frames.push({ time: Number(time.toFixed(3)), luma, redChroma });
      time += FRAME_SECONDS;
    }
  }
  return frames;
}
const NEUTRAL = 128;
const MAGENTA = 235;
const CHROMA_OPTIONS = { ...OPTIONS, signal: "chroma" };
const whiteStartThenMarker = flashFromFrames(chromaFrames([[0.44, BRIGHT, NEUTRAL], [0.4, DARK, NEUTRAL], [0.5, 105, MAGENTA], [0.5, DARK, NEUTRAL], [0.5, BRIGHT, NEUTRAL], [1.0, DARK, NEUTRAL]]), CHROMA_OPTIONS);
check(whiteStartThenMarker !== null && !whiteStartThenMarker.leadingPartial && Math.abs(whiteStartThenMarker.seconds - 0.84) < 0.06, "(f) should find the magenta marker, got " + JSON.stringify(whiteStartThenMarker));
const onlyWhite = flashFromFrames(chromaFrames([[0.44, BRIGHT, NEUTRAL], [0.4, DARK, NEUTRAL], [0.5, BRIGHT, NEUTRAL], [1.0, DARK, NEUTRAL]]), CHROMA_OPTIONS);
check(onlyWhite === null, "(f) white flashes alone should give no marker, got " + JSON.stringify(onlyWhite));
const magentaCutOff = flashFromFrames(chromaFrames([[0.48, 105, MAGENTA], [0.3, DARK, NEUTRAL], [0.5, BRIGHT, NEUTRAL], [1.0, DARK, NEUTRAL]]), CHROMA_OPTIONS);
check(magentaCutOff !== null && magentaCutOff.leadingPartial, "(f) a cut-off magenta marker should be accepted, got " + JSON.stringify(magentaCutOff));

// Without allowLeadingPartial (the record test's use) a bright start is never a marker.
check(flashFromFrames(framesFromRuns([[0.48, BRIGHT], [1.5, DARK]]), { flashMs: FLASH_MS }) === null, "bright start counted without allowLeadingPartial");

if (failures.length > 0) {
  console.error(`FAIL\n${failures.join("\n")}`);
  process.exit(1);
}
console.log("OK: av_markers picks a full pulse over a bright start, accepts a fitting partial marker, rejects a blank start");
