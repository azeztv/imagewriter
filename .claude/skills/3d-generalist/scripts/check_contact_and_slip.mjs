#!/usr/bin/env node
/**
 * Automated 30-fps anti-slop QA checker for Three.js / Crucible 3D scenes.
 * Checks:
 *  1. Teleport / excessive speed (>0.30 m/frame or >2.0 m/s over 0.3 s)
 *  2. Foot slip (<0.25 m/s when heel or toe is within 3 cm of ground)
 *  3. Flight (both feet >3 cm above ground outside airborne beats)
 *  4. Contact gap: a foot held still for 3+ frames sits within 2.5 cm of the surface below
 * It does not check grips, clearance, chips, exits or caption sync: run the project's own gate for those.
 *
 * Expects the page to expose `window.placeTime(t)` (or `window.renderTime(t)`)
 * and `window.debugScene.sampleQaState()` returning:
 *   { hips: [x,y,z], leftHeel: [x,y,z,groundY], leftToe: [x,y,z,groundY],
 *     rightHeel: [x,y,z,groundY], rightToe: [x,y,z,groundY], airborne?: boolean }
 *
 * Usage: node check_contact_and_slip.mjs <url> <durationSec> [fps=30]
 */

import { parseArgs } from "node:util";

const USAGE = "Usage: node check_contact_and_slip.mjs <url> <durationSec> [fps=30]";
const { positionals, values } = parseArgs({
  allowPositionals: true,
  options: { help: { type: "boolean", short: "h" } },
});

if (values.help) {
  console.log(USAGE);
  process.exit(0);
}

const [url, durStr = "60", fpsStr = "30"] = positionals;

if (!url) {
  console.error(USAGE);
  process.exit(2);
}

const duration = Number(durStr);
const fps = Number(fpsStr);
const totalFrames = Math.ceil(duration * fps);
const dt = 1 / fps;

// Playwright comes from the project, or from PLAYWRIGHT_FROM: a folder whose node_modules has it.
async function loadChromium() {
  try {
    return (await import("playwright")).chromium;
  } catch {
    const { createRequire } = await import("node:module");
    const baseFolder = (process.env.PLAYWRIGHT_FROM ?? process.cwd()).replace(/[\\/]?$/, "/");
    return createRequire(baseFolder)("playwright").chromium;
  }
}
const chromium = await loadChromium();
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();
await page.goto(url, { waitUntil: "networkidle" });

const samples = [];
for (let f = 0; f <= totalFrames; f++) {
  const t = Number((f * dt).toFixed(4));
  const s = await page.evaluate((time) => {
    if (typeof window.placeTime === "function") window.placeTime(time);
    else if (typeof window.renderTime === "function") window.renderTime(time);
    return window.debugScene?.sampleQaState ? window.debugScene.sampleQaState(time) : null;
  }, t);
  if (!s) {
    console.error("Page does not expose window.debugScene.sampleQaState(time)");
    await browser.close();
    process.exit(2);
  }
  samples.push({ f, t, ...s });
}

await browser.close();

function dist3(a, b) {
  return Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
}

function distXZ(a, b) {
  return Math.hypot(a[0] - b[0], a[2] - b[2]);
}

const teleports = [];
const speeding = [];
const hovers = [];
const windowFrames = Math.max(1, Math.round(0.3 * fps));
const stillStreak = { leftHeel: 0, leftToe: 0, rightHeel: 0, rightToe: 0 };
const hoverOpen = { leftHeel: false, leftToe: false, rightHeel: false, rightToe: false };
const flights = [];
const slips = [];
let slipStreakL = 0;
let slipStreakR = 0;

for (let i = 1; i < samples.length; i++) {
  const prev = samples[i - 1];
  const cur = samples[i];

  const stepHips = dist3(prev.hips, cur.hips);
  if (stepHips > 0.3) {
    teleports.push({ t: cur.t, stepM: Number(stepHips.toFixed(3)) });
  }

  if (i >= windowFrames) {
    const earlier = samples[i - windowFrames];
    const windowSpeed = distXZ(earlier.hips, cur.hips) / (windowFrames * dt);
    if (windowSpeed > 2.0) speeding.push({ t: cur.t, speedMs: Number(windowSpeed.toFixed(2)) });
  }

  for (const point of Object.keys(stillStreak)) {
    const movedSpeed = distXZ(prev[point], cur[point]) / dt;
    const gap = cur[point][1] - cur[point][3];
    stillStreak[point] = movedSpeed < 0.05 ? stillStreak[point] + 1 : 0;
    const hovering = !cur.airborne && stillStreak[point] >= 3 && gap > 0.025 && gap < 0.15;
    if (hovering && !hoverOpen[point]) {
      hovers.push({ t: cur.t, point, gapCm: Number((gap * 100).toFixed(1)) });
    }
    hoverOpen[point] = hovering;
  }

  const lhGap = cur.leftHeel[1] - cur.leftHeel[3];
  const ltGap = cur.leftToe[1] - cur.leftToe[3];
  const rhGap = cur.rightHeel[1] - cur.rightHeel[3];
  const rtGap = cur.rightToe[1] - cur.rightToe[3];

  if (!cur.airborne && lhGap > 0.03 && ltGap > 0.03 && rhGap > 0.03 && rtGap > 0.03) {
    flights.push({ t: cur.t, minGapCm: Number((Math.min(lhGap, ltGap, rhGap, rtGap) * 100).toFixed(1)) });
  }

  const lNear = Math.min(Math.abs(lhGap), Math.abs(ltGap)) <= 0.03;
  const rNear = Math.min(Math.abs(rhGap), Math.abs(rtGap)) <= 0.03;
  const lSpeed = Math.min(distXZ(prev.leftHeel, cur.leftHeel), distXZ(prev.leftToe, cur.leftToe)) / dt;
  const rSpeed = Math.min(distXZ(prev.rightHeel, cur.rightHeel), distXZ(prev.rightToe, cur.rightToe)) / dt;

  slipStreakL = lNear && lSpeed > 0.25 ? slipStreakL + 1 : 0;
  slipStreakR = rNear && rSpeed > 0.25 ? slipStreakR + 1 : 0;

  if (slipStreakL === 3) slips.push({ t: cur.t, foot: "left", speedMs: Number(lSpeed.toFixed(2)) });
  if (slipStreakR === 3) slips.push({ t: cur.t, foot: "right", speedMs: Number(rSpeed.toFixed(2)) });
}

const ok = [teleports, speeding, flights, slips, hovers].every((list) => list.length === 0);
console.log(
  JSON.stringify(
    {
      status: ok ? "PASS" : "FAIL",
      framesChecked: samples.length,
      teleports: teleports.slice(0, 10),
      speeding: speeding.slice(0, 10),
      hovers: hovers.slice(0, 10),
      flights: flights.slice(0, 10),
      slips: slips.slice(0, 10),
    },
    null,
    2
  )
);
process.exit(ok ? 0 : 1);
