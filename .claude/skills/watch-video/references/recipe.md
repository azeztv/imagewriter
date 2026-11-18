# Learn a video so it can be remade

<!-- skill-navigation:start -->
## Reading map

- [Learn a video so it can be remade](#learn-a-video-so-it-can-be-remade)
- [1. What a recipe is](#1-what-a-recipe-is)
- [2. Extract](#2-extract)
- [3. Prove](#3-prove)
- [4. Retarget to another product](#4-retarget-to-another-product)
- [5. Build](#5-build)
- [6. Verify the remake](#6-verify-the-remake)
- [7. Limits](#7-limits)
<!-- skill-navigation:end -->

Follow 1 to 6 in order; in 5 (which tool per beat) read only the techniques your brief uses.

Use this when the user wants a video understood well enough to make another one like it ("make a video like this",
"the same for <product>", "pull the recipe"). Tool: `{{SKILL_DIR}}/scripts/recipe.py`, run as
`uv run --no-project --with numpy --with pillow python <that file> <command> ...`. Worked example of a finished
recipe: `{{SKILL_DIR}}/references/example-recipe.json`.

## 1. What a recipe is

One JSON file that a renderer or another session can follow without seeing the reference.

| Field | Holds |
|---|---|
| `source` | file name, `duration` in seconds, size, whether there is a voice |
| `summary` | two sentences: what the film does, in order |
| `grammar` | the rules that survive a change of product. This is the part being learned |
| `style` | palette, type, motifs, camera, as short phrases |
| `beats[]` | `id`, `role`, `start`, `end`, `enter`, `enter_seconds`, `backdrop`, `technique`, `text`, `visual`, `motion`, `evidence`; `inner_cuts` for cuts inside a beat |
| `cues[]` | `time`, `kind`, `length`, `level` (dB below the loudest), optional `pitch`, `repeat {count, every}`, `on` (beat id), `note` |
| `silences[]` | `start`, `end`, `purpose` |
| `not_reproduced` | what belongs to the original and is not taken: footage, faces, names, the actual sounds |

- `enter`: `start`, `cut`, `fade`, `wipe`, `morph`, or `hold` (same backdrop, new content, nothing measurable).
- `backdrop`: `gradient`, `light`, `dark`, `footage`, `ui`. `technique`: `type`, `ui`, `graphic`, `image`, `3d`, `footage`.
- `kind`: `bass`, `hit`, `click`, `blip`, `riser`, `whoosh`, `tone`.
- `evidence`: `measured` (a number from `perception.json`), `seen` (read off the frames), `inferred` (a guess; say so).

## 2. Extract

1. Run `perceive.py` on the whole video, then again in windows of 6 to 9 seconds with `--fps 6 --tile-width 480`
   so every transition is covered at 6 frames per second. Look at every sheet.
2. Beats: start from the measured `cuts` and `moves` in `perception.json`. A cut starts a beat with `enter: cut`
   at that exact time; a move starts one with `fade`, `wipe` or `morph` and `enter_seconds` equal to its measured
   length. Split further where the words or the subject change (`hold`).
3. For each beat write what a builder needs: the words on screen, what is in frame, what moves and how long.
   Two neighbouring frames give an interval in which something happened, never an exact easing curve.
4. Cues: read `audio_timeline.txt` beside the spectrogram. One cue per sound that marks something on screen, at
   its measured onset, with `on` naming the beat. Runs of hits become `repeat`; when the spacing changes, use
   several cues, since the change is usually the point. Note how far each loud cue sits before or after its cut.
5. Silences: only the ones that do a job, each with its purpose.
6. Grammar: 6 to 10 rules, each true of this film and usable for a different product ("a bass hit lands on every
   hard cut or up to 0.25 s before it"). A rule that names the original's product or picture is not grammar.

## 3. Prove

1. `recipe.py check recipe.json <perceived>/perception.json` until it prints PASS. Each FIX line is a claim the
   measurements contradict: a cut that is not there, a loud sound with no cue, a silence that is not silent.
2. `recipe.py graybox recipe.json graybox.mp4`, then `perceive.py graybox.mp4` and
   `recipe.py check recipe.json <graybox-perceived>/perception.json rebuild`. PASS means the recipe alone carries
   the timing. Look at the grey box sheets: every beat must make sense to someone who never saw the reference.
3. `recipe.py compare <reference>/perception.json <graybox>/perception.json` lists what the reference has that
   the recipe left out. Add it, or leave it out on purpose.

## 4. Retarget to another product

1. Copy `recipe.json` to `brief.json` in the new project. Keep `grammar`, each beat's `role`, `enter`, timing,
   `cues` and `silences`. Rewrite `text`, `visual`, `motion` and `technique` for the new product, and `style` for
   the look the user asked for.
2. Every beat must show a real state of the product (open it and screenshot the states first, before building). A beat the product cannot fill honestly is removed and its time given to
   its neighbours; never invent a feature to keep a beat.
3. A different length: `recipe.py retime brief.json <seconds> brief.json`. It scales every time in proportion.
4. `recipe.py graybox brief.json animatic.mp4` and send that to the user before building anything expensive.

## 5. Build

One file owns every time. Whatever renders the pictures, beats and cues come from `brief.json` (or the
`reel/timeline.js` written from it), and a clip rendered elsewhere is cut to its beat's length from that file.

| Technique | Build with |
|---|---|
| `type`, `ui`, `graphic`, `image` | `snapcn` with the matching `remotion-*` workflow. Beats become scenes, `cues[]` becomes the sound cue list; pick the tempo so the cut times fall on beats |
| `3d`, sharing the page's timeline (a tilting card, a product turntable, particles) | a three.js canvas inside a Remotion scene, driven by the frame number; nothing reads the clock |
| `3d`, a world or landscape | `build-crucible-scene`, then `render-crucible-media` for the clip |
| `3d`, a rendered room, product or camera move with real lighting | Blender 5.2, headless: `blender -b <file.blend> -P <script.py>` (full path to `blender.exe` where it is not on PATH); render an image sequence at the brief's frame rate and bring it in as a footage layer. Below normal priority, through the machine's GPU queue if it has one |
| `footage` | the user's own recording or CC0 stock. It is in `not_reproduced` for a reason: ask, do not copy |
| A React project that already uses Remotion | Remotion with the same `brief.json` as its only clock. Not installed here; installing needs the user's yes |

Sound: the `design-sound` skill. Each `kind` becomes one cue; levels and silences come from
the brief.

### Build list on the reference frames

Before building any picture that must match a reference (a film shot, a tutorial result, a client frame), turn the
reference into a numbered build list drawn on its own frames. Without it the
first build comes out as flat boxes, because nobody listed what the frame holds.

1. Pull 3 to 5 full-size frames that together show every part: a wide, a mid, a close, and one per distinct set.
2. Have a subagent describe each frame part by part (ground, structures, debris, atmosphere, light
   direction and colour, effects), with a rough 0-1 box for each part, sizes relative to something known, and colours
   in plain words. It lists what is there, not what to do.
3. Write `notes.json` (boxes, a category word, one short line per part in the user's language, with diacritics) and
   run `scripts/build_list.py notes.json <out> --frames <folder>`. Each frame comes back with numbered boxes and a
   legend under it; a category keeps one colour across frames.
4. Read one sheet yourself: boxes sit on the right things, no legend line is cut. Send the sheets to the user before
   building. They correct a wrong reading in seconds, and each number becomes a task.
5. Build from the list, then put your render beside the same frame and go down the numbers one by one. A number
   with nothing matching it in the render is not done. Report by number.

Keep each line to what must be built (material, count, size, colour), never a mood word. At most about 12 boxes a
frame; split a busier frame into two crops.

## 6. Verify the remake

1. `perceive.py` on the finished video, then `recipe.py check brief.json <final>/perception.json rebuild`.
2. `recipe.py compare <reference>/perception.json <final>/perception.json`; a different length is compared in
   proportion. Read each difference and say whether it was a choice.
3. Put the reference's sheets beside the remake's and check each grammar rule by eye.
4. Report what was measured (cuts, cue timing, silences), what was only seen, and that nobody has listened yet.

## 7. Limits

- The scene score reacts to change in the amount of change. Steady movement (a slow push, a constant scroll)
  barely registers, so `moves` misses it; the frame sheets show it.
- A cut between two mostly white frames (one interface view to another) scores 0.08 to 0.18, under the 0.2 that
  counts as a cut, so `check` reports it as missing (Orglet launch film, 2026-10-12). Before changing the picture,
  print the scene score around the claimed time: a lone spike on the right frame is the cut.
- The sound timeline says what a sound does, not what made it. `kind` is a reading of the spectrogram.
- `check` in `rebuild` mode does not test soft transitions and marks cues below -20 dB as UNVERIFIED.
- A recipe written from the measurements passes `check` by construction. The proof of understanding is the grey
  box making sense on its own and the remake following the grammar, not the PASS line.
