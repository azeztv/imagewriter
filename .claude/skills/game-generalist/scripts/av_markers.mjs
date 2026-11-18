// Finds the sync marker (white flash in the picture, beep in the sound) in a video or audio file.
// Used by record.mjs to align the two tracks, and by the record test to check the result.
import { spawnSync } from "node:child_process";

// The flash is a bright pulse over the page: a frame much brighter than the one before, followed later by a
// frame much darker again. Asking for both edges ignores the blank frame Playwright puts first (it has only a
// falling edge) and a page that is merely bright.
const MIN_EDGE_LUMA_STEP = 25;
const MAX_PULSE_SECONDS = 2;
// With checkPulseLength, a pulse whose measured length is further than this from the length the page drew is
// rejected: a stalled screencast delays one edge and would skew the start time by half the stall.
const MAX_PULSE_LENGTH_ERROR_SECONDS = 0.15;
const BEEP_AMPLITUDE_THRESHOLD = 0.1;
const PCM_SAMPLE_RATE = 16000;
const MAX_OUTPUT_BYTES = 256 * 1024 * 1024;

function runFfmpeg(argumentsList, encoding) {
  const result = spawnSync("ffmpeg", ["-v", "error", ...argumentsList], { encoding, maxBuffer: MAX_OUTPUT_BYTES });
  if (result.error) throw new Error(`ffmpeg could not start: ${result.error.message}`);
  return result;
}

// Per-frame average brightness (luma) and red-difference chroma (redChroma, about 128 for white, grey and dark, high for
// magenta) of the whole picture with each frame's own presentation time. Passthrough keeps
// ffmpeg from duplicating or dropping frames, which would shift the timeline.
export function readFrameBrightness(videoPath) {
  const result = runFfmpeg(
    ["-i", videoPath, "-an", "-fps_mode", "passthrough", "-vf", "scale=16:16,signalstats,metadata=print:file=-", "-f", "null", "-"],
    "utf8",
  );
  const frames = [];
  let currentTime = null;
  for (const line of result.stdout.split(/\r?\n/)) {
    const timeMatch = line.match(/pts_time:([\d.]+)/);
    if (timeMatch) currentTime = Number(timeMatch[1]);
    const lumaMatch = line.match(/lavfi\.signalstats\.YAVG=([\d.]+)/);
    if (lumaMatch) frames.push({ time: currentTime, luma: Number(lumaMatch[1]), redChroma: 128 });
    const chromaMatch = line.match(/lavfi\.signalstats\.VAVG=([\d.]+)/);
    if (chromaMatch && frames.length > 0) frames[frames.length - 1].redChroma = Number(chromaMatch[1]);
  }
  return frames;
}

function medianFrameInterval(frames) {
  const gaps = [];
  for (let index = 1; index < frames.length; index += 1) gaps.push(frames[index].time - frames[index - 1].time);
  if (gaps.length === 0) return 0;
  gaps.sort((first, second) => first - second);
  return gaps[Math.floor(gaps.length / 2)];
}

// Playwright's video can begin after the flash has already started, so the capture opens on a bright frame and
// the rising edge is missing. Playwright's blank first frame is also bright with only a falling edge, so a bright
// start counts as a marker that began before the capture only when its falling edge sits where a flashMs flash
// would end if it began at the first frame: the inferred start must be within this many seconds of the capture's
// start. Anything else is reported as no marker, and the recorder captures again.
const MAX_LEADING_START_ERROR_SECONDS = 0.12;

function findLeadingFall(frames) {
  if (frames.length < 2) return null;
  for (let fallIndex = 1; fallIndex < frames.length; fallIndex += 1) {
    if (frames[fallIndex].time - frames[0].time > MAX_PULSE_SECONDS) return null;
    const fellFromStart = frames[0].luma - frames[fallIndex].luma >= MIN_EDGE_LUMA_STEP;
    if (fellFromStart && frames[fallIndex - 1].luma - frames[fallIndex].luma >= MIN_EDGE_LUMA_STEP) return fallIndex;
  }
  return null;
}

function findFirstPulse(frames) {
  for (let riseIndex = 1; riseIndex < frames.length; riseIndex += 1) {
    if (frames[riseIndex].luma - frames[riseIndex - 1].luma < MIN_EDGE_LUMA_STEP) continue;
    for (let fallIndex = riseIndex + 1; fallIndex < frames.length; fallIndex += 1) {
      if (frames[fallIndex].time - frames[riseIndex].time > MAX_PULSE_SECONDS) break;
      if (frames[fallIndex - 1].luma - frames[fallIndex].luma >= MIN_EDGE_LUMA_STEP) return { riseIndex, fallIndex };
    }
  }
  return null;
}

// Marker from per-frame brightness: { seconds, leadingPartial } or null. seconds is when the flash started. A frame
// can only show the flash from its own time on, so each edge is seen up to one frame late. Both edges are seen late
// by a related amount, so their mean cancels most of it when the flash lasts an odd number of half frames (180 ms at
// 25 fps); half a frame is what is left. flashMs is the length the page drew the flash for.
// With allowLeadingPartial and a flashMs, a bright start that fits the rule above is the marker and is dated from its
// falling edge alone (seconds may then be slightly negative); any other bright start is ignored in favour of the first
// full pulse (rise and fall). checkPulseLength rejects a full pulse whose length is off from flashMs.
// signal "chroma" follows the red-difference channel instead of brightness, so only a magenta flash counts: white blank
// frames and a game's own white flashes (which load makes look like a cut-off marker) do not register at all.
export function flashFromFrames(allFrames, { flashMs, allowLeadingPartial = false, checkPulseLength = false, signal = "luma" } = {}) {
  const frames = signal === "chroma" ? allFrames.map((frame) => ({ time: frame.time, luma: frame.redChroma })) : allFrames;
  const leadingFallIndex = allowLeadingPartial && flashMs ? findLeadingFall(frames) : null;
  if (leadingFallIndex !== null) {
    const startSeconds = frames[leadingFallIndex].time - flashMs / 1000 - medianFrameInterval(frames) / 2;
    const startError = startSeconds - frames[0].time;
    // A fitting bright start is the marker even when the game's own full flash follows it. One that outlasts the
    // flash means a stalled screencast (seen: 0.76 s bright for a 0.5 s flash), so its clock cannot be trusted and
    // the next flash would be the game's own: no marker. A shorter one is a blank start and gives way to a full pulse.
    if (Math.abs(startError) <= MAX_LEADING_START_ERROR_SECONDS) return { seconds: startSeconds, leadingPartial: true };
    if (startError > MAX_LEADING_START_ERROR_SECONDS) return null;
  }
  const pulse = findFirstPulse(frames);
  if (!pulse) return null;
  const riseTime = frames[pulse.riseIndex].time;
  if (!flashMs) return { seconds: riseTime, leadingPartial: false };
  const fallTime = frames[pulse.fallIndex].time;
  if (checkPulseLength && Math.abs(fallTime - riseTime - flashMs / 1000) > MAX_PULSE_LENGTH_ERROR_SECONDS) return null;
  const halfFrame = medianFrameInterval(frames) / 2;
  return { seconds: (riseTime + fallTime - flashMs / 1000) / 2 - halfFrame, leadingPartial: false };
}

export function findFlashMarker(videoPath, options = {}) {
  return flashFromFrames(readFrameBrightness(videoPath), options);
}

// Time when the flash started, or null.
export function findFlashSeconds(videoPath, options = {}) {
  return findFlashMarker(videoPath, options)?.seconds ?? null;
}

function readMonoSamples(audioPath) {
  const result = runFfmpeg(["-i", audioPath, "-vn", "-ac", "1", "-ar", String(PCM_SAMPLE_RATE), "-f", "f32le", "-"], "buffer");
  const bytes = result.stdout;
  const sampleCount = Math.floor(bytes.length / 4);
  const samples = new Float32Array(sampleCount);
  for (let index = 0; index < sampleCount; index += 1) samples[index] = bytes.readFloatLE(index * 4);
  return samples;
}

// Time of the first sample louder than the beep threshold (at or after notBefore seconds), or null when there is none.
export function findBeepSeconds(audioPath, { notBefore = 0 } = {}) {
  const samples = readMonoSamples(audioPath);
  for (let index = Math.floor(notBefore * PCM_SAMPLE_RATE); index < samples.length; index += 1) {
    if (Math.abs(samples[index]) > BEEP_AMPLITUDE_THRESHOLD) return index / PCM_SAMPLE_RATE;
  }
  return null;
}
