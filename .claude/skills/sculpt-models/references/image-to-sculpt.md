# One image to a measured sculpt

Source: gokayfem/image-to-sculpt (MIT, read 2026-11-09; its lessons came from four versions of one cartoon troll).

Use this route when the input is one picture of a character, creature, figurine, bust, toy or product and the
sculpt must match it, not just resemble it. The idea: every surface the picture shows is fitted to that picture's
own normals, outline and depth, every hidden surface comes from extra views that first had to agree with each
other, and the result is measured against the picture, never only looked at.

Not for scenes or rooms, thin structures under about 1% of the subject (hair strands, wires), glass or chrome,
or several separate objects. Say so before starting.

<!-- skill-navigation:start -->
## Reading Map

- [One image to a measured sculpt](#one-image-to-a-measured-sculpt)
- [1. Front maps](#1-front-maps)
- [2. Views of the sides the picture hides](#2-views-of-the-sides-the-picture-hides)
- [3. Register and screen before carving](#3-register-and-screen-before-carving)
- [4. Fit in stages](#4-fit-in-stages)
- [5. Rules learned the hard way](#5-rules-learned-the-hard-way)
- [6. Measure it](#6-measure-it)
- [Tools](#tools)
<!-- skill-navigation:end -->

## 1. Front maps

- Pad the image to the view generator's aspect ratio (do not crop) so every view shares one lens. Long side 1024 px.
- Write a short subject phrase yourself ("stocky cartoon troll", "ceramic owl figurine"); it goes into every view
  prompt. A vague phrase gives vague views.
- Make a mask (keep the largest blob, fill holes), a metric depth map with focal length (MoGe) and a normal map
  (Marigold). Check mask and normals before going on. A drawing is first turned into a 3D render that keeps the
  pose; that render is the reference from then on.

## 2. Views of the sides the picture hides

| Set | Angles (azimuth, elevation) |
| --- | --- |
| minimal | ±45, ±90, 180, plus one held out at (135, 0) |
| standard | minimal + −135, (0, 30), (180, 30), (−45, 30) |
| full | standard + (45, 30), (0, −20), ±65 |

- Prompt as an orbit: "the camera has orbited 45 degrees to the RIGHT, so we see more of the side that was on the
  right", same subject, pose, proportions, lens and distance, whole subject in frame, plain light grey, no shadow.
- Generate views with an image model given a prompt plus the front image as input, or render your own block-out.
  Real photos of the object beat generated views. Which generator to use is in `local.md` when it exists.
- Look at every view before using it: reject a changed pose, an extra or missing limb, a crop, a shadow joined to
  the mask, a scar or emblem on the wrong side.

## 3. Register and screen before carving

- **Never trust the requested angle.** Views asked for at +45, +90, −90 registered at +19, −123, +35. Search every
  10° of azimuth, elevation −15 to 45°, scoring silhouette IoU plus normal agreement.
- Allow left/right swaps (generators make them), forbid front/back swaps: keep |azimuth| within 60° of the request
  and elevation within 30°. On a symmetric subject a back view has the same outline as a front view.
- **Screen:** a view whose outline scores IoU under 0.80 against the hull of the others is a different pose. Reject
  it; one bad view carves away real volume.
- Carve a visual hull from the registered silhouettes. Detect a mirror plane; symmetry acts on targets, never on
  the distance field itself.
- Keep one view out of fitting entirely. It measures consistency, not truth (it is generated too).

## 4. Fit in stages

One pass: mesh the field, solve on a Taubin-smoothed copy, build per-vertex targets from each view (normals where
visible and facing, a signed silhouette push, the photo's depth only), solve silhouette and depth through a very
stiff field and normals through a flexible one, then displace the original surface with a soft step limit
(`step × tanh(t / step)`) and re-distance exactly. Units: 1 = the subject's front extent.

| Stage | Passes | Step | Normal stiffness | What moves |
| --- | --- | --- | --- | --- |
| forms | 10 | 0.003 | 3000 (~4% of subject) | proportions, big volumes |
| surface | 14 | 0.002 | 100 (~1.7%) | planes, muscles, folds |
| detail | 14 | 0.0012 | 6 (~0.5%) | noses, brows, knuckles |
| polish | 4 | 0.001 | 6 | after cuts and smoothing |
| focus | 8 | 0.001 | 3, plus a mid band | one chosen region (face, hands) |

Then cut gaps the photo shows (silhouette cut by smooth maximum, keep the largest piece), smooth by morphological
opening (removes webs and specks thinner than twice the radius), polish.

## 5. Rules learned the hard way

- The photo governs what it sees. Generated views fill in only where it does not; their depth is never used (it
  disagrees by centimetres) and their normals are never averaged over the photo's (that flattens features).
- Rotate each generated view's normals once as a whole (under 8°) before using them, or creases appear where the
  dominant view changes.
- Never blur normal targets; let stage stiffness limit detail. Where no view is sure, keep the current normal.
- Solving against raw marching-cubes facets makes staircases; displacing the smoothed copy shaves curves.
- Keep the distance field exact (exact triangle distances in a band, a distance transform beyond). Offsets, blends
  and mirrored fields turn into voxel staircases and moire rings.
- Closing fills the gaps you want open: use opening for webs, a silhouette cut for gaps.
- Cut with generated outlines only inside a chosen region; they disagree by pixels and shred fingers.
- A region that keeps failing needs a new view that looks into it (`-30:25` for armpits, `0:-20` under a chin),
  not more smoothing.
- Record every step; a fix is a new step, never an edit. That record is also the timelapse.

## 6. Measure it

Render the sculpt from every registered camera next to that view's picture, normals, normal error (blue 0°, red
45° or more) and silhouette difference. Look first, then read the numbers side by side; one number never stands
for quality (IoU rose while roughness doubled on the troll).

| Metric | Target |
| --- | --- |
| Silhouette IoU | photo ≥ 0.97, training mean ≥ 0.92, held-out ≥ 0.85 |
| Outline distance | photo ≤ 2.5 px |
| Normal angle median | photo ≤ 10°, training ≤ 18°, held-out ≤ 22° |
| Roughness vs reference | 0.75 to 1.25 (above 1.3 means lumps) |
| Photo depth error | ≤ 15 thousandths of the subject |

Set targets before fitting and do not lower them after a failure. Stop fitting when training views keep improving
but the held-out view stops. Show before/after crops of the same box before claiming a fix.

## Tools

The upstream repo ships a full CLI (registration, carving, fitting, Blender replay, films) that calls paid fal
models (about $2 a case for standard views). Where a local copy sits is in `local.md`; it is reading material
only. Running it is the user's call: ask once, naming the fal cost. Without it, apply sections 2, 3
and 6 by hand in Blender (camera per view, silhouette overlay, `scripts/check_sculpt.py` for the mesh checks).
