# Production spine: eight steps for every piece (`pipeline-spine.md`)

Every generalist skill (3D, 2D and game) runs the same eight steps, in order, for every mode. Professional animation, motion-design and
game-art pipelines share this shape: decide on paper, prove the look and timing in the cheapest medium, then build.
A change is cheapest before animation and most expensive after it, and an art pass before the blockout locks in early
mistakes. Each step below writes a file. The next step starts from those files, not from memory of the chat.

<!-- skill-navigation:start -->
## Reading Map

- [Production spine: eight steps for every piece (`pipeline-spine.md`)](#production-spine-eight-steps-for-every-piece-pipeline-spinemd)
- [The eight steps](#the-eight-steps)
- [Progress lines in `brief.md`](#progress-lines-in-briefmd)
- [Lock and reopen](#lock-and-reopen)
- [Parallel workers only after the lock](#parallel-workers-only-after-the-lock)
- [Critique loops](#critique-loops)
- [After the preview: the next round](#after-the-preview-the-next-round)
- [Steps per mode](#steps-per-mode)
<!-- skill-navigation:end -->

## The eight steps

| Step | Writes | Gate | Cheapest form for a small job |
|---|---|---|---|
| 1. Brief | `brief.md` | self: five slots filled or defaulted | five lines, no questions when inferable |
| 2. Reference | `refs/`, `refs/NOTES.md` | self: every hero subject has references, nothing guessed | one image and one line per subject |
| 3. Script and beats | `script.md`, beat table, scratch voice, cue list | self: read-aloud length fits the brief | a five-line beat list; skip for a still or an asset |
| 4. Prep and look gate | `plan.md` (sketch, tools, resources), style frames A/B/C, blockout or animatic, then `LOOK.md` and `cameras.json` | **the user picks** | a sketch and two stills on a grey block |
| 5. Assets and check | `assets/`, `CREDITS.md`, measured bounds | self: scale, silhouette and clipping measured | one line per asset inside `brief.md` |
| 6. Build and animate | per-shot renders or scene states, a WIP demo after the first finished shot | self: each shot against its style frame and board; the WIP goes to the user without waiting | one shot |
| 7. Sound | final voice, SFX, music, mix | self: cue timing and loudness measured | skip for a silent still or model |
| 8. QA, preview, final | gate report, 540p preview with sound, final | all gates pass, then **the user approves** the preview | one still instead of a preview |

The user sees the work three times per piece: the choice at step 4 and the preview at step 8 wait for an answer, the
WIP demo at step 6 does not. Every other gate is a measured self-check. After the preview, the user's answer picks the
next round (see the last sections).

### 1. Brief

Run the intent brief of the calling skill (`references/intent-brief.md` in the 3D, 2D or game skill's own folder). Inside it, check the installed
tools and report only what is missing. Ask the cast and copyright question here when the piece shows real people,
brands or characters someone owns: name the risk in one line, ask once, and follow the answer.

### 2. Reference

Look at the real thing before inventing it.

- Each hero subject (object, machine, creature, character, place) gets at least two views, plus a drawing or a
  measured size when one exists.
- A real place, period, weather or light gets real footage, aerials or photos of that place and that day. A storm
  report says overcast: the film is overcast.
- Matching a reference video or picture: copy its camera first. Estimate its lens, height and distance, render
  one grey camera test beside the reference frame, and list what fills each part of that frame (numbered build
  list on the frame) before dressing anything. A wrong lens or an empty corner found after the build costs a
  round each.
- A prop that reads wrong (a knife that is not a knife) is replaced by a real model, not reshaped.
- Search for ready resources here, in this order: an add-on or library that supplies the asset, an open online
  model, scan or photo, and only then a build from the references. Write down what was searched when nothing fits.
- `refs/NOTES.md` gives one line per file: what it is for (shape, light, motion, colour, scale), plus the measured
  values the look must hit (mean luma, saturation, palette hex).

### 3. Script and beats

Write the script with its sources on top, split it into a beat table (spoken line, picture, camera, SFX cue), and make
a scratch voice and a cue list now. Sound is planned with the picture, not added after it: walk keys and cuts that
hang on words need the voice timing early.

### 4. Prep and look gate

The one decision the user makes before anything expensive is built. Prepare first, so the user chooses between options
that can actually be made, and the build starts with everything at hand.

- Prepare: rough the piece out (thumbnails, a board or a block-in), confirm every tool the build needs runs on this
  machine, and download the resources found at step 2 into the project. Write `plan.md`: the sketch, the tool list
  with what was checked, and one line per subject naming its resource and licence, or "built from refs" with what was
  searched. Anything that needs the user (a sign-in, a paid asset, a licence trade-off) goes at the top of `plan.md`
  in one line each.
- Options may differ in approach as well as look when the brief leaves the approach open (story angle, camera idea,
  style family); otherwise they differ only in look.
- Render two or three style frames, labelled A, B and C, at final grade on the real hero assets or the closest
  sourced stand-ins, never primitive boxes. Each option differs in look (palette, light, lens, texture), not in
  subject. A game's greybox may be primitives, but its style frames are never a recolour of it (the game skill's step 4
  row).
- Add the cheapest timing proof: a grey blockout with the real cameras, or an animatic of boards or stills timed
  to the scratch voice. Shots, order and ending are fixed here.
- Send the plan summary, the options and the timing proof in one message. The user picks and gives the reason in
  one line. Never claim an option matches the user's taste. If the user says "you choose", pick, state why in one
  line, and go on.
- Write `LOOK.md` from the pick: palette hex, lens, light direction and key-to-fill ratio, grade values, character
  or subject scale, texture rules, and the measured luma and saturation of the picked frame. Write `cameras.json`
  (or the shot list with framing for 2D).
- Skip the gate only when an approved `LOOK.md` already covers the piece (a later episode of a series, a fix round).
  A new look or a series pilot always passes it.

### 5. Assets and check

Gather the rest of the assets the build needs, from the references and `LOOK.md`. Record each one's source and
licence in `CREDITS.md`, measure its real bounds, scale the world to the character, and look at a still from the
shot's camera distance for clipping, lumps and wrong scale before anything moves.

### 6. Build and animate

Execution only: no new design decisions. A decision that changes the look or the shots goes back to step 4.
Each finished shot gets three stills (first, middle, last) compared with its style frame and board before the next
shot starts.

The first finished shot (or the first finished part of a still, model or app) goes to the user as a WIP demo: a short
low-resolution clip or still with one line on what comes next. Keep building while waiting; nothing is thrown away
before an answer. Notes on the WIP start a fix round at once. When the user asked to approve the WIP first, wait.

### 7. Sound

Swap the scratch voice for the final one, give every visible event its own sound at its frame, fit the music, and mix
to the platform loudness. The `design-sound` skill owns the method and its checks.

### 8. QA, preview, final

Run the skill's gates: `qa-and-gates.md` for films and motion graphics (look match, phone check and brief drift
included), `playtest-gates.md` for games. Send the fast 540p preview with sound (for a game, the playable build plus a
short capture) only when every gate passes. Render full quality only after the user approves the preview, every
round, fixes included.

## Progress lines in `brief.md`

End `brief.md` with a `## Progress` section, one line per step, filled as each step finishes:

```
## Progress
1 brief: done
2 reference: done, refs/NOTES.md
3 script: done, script.md, 42 s scratch voice
4 look: plan.md ready, B picked ("warmer, less clutter"), LOOK.md, cameras.json
5 assets: done, CREDITS.md
6 build: WIP of shot 1 sent, shots 1-4 done, 5-6 open
7 sound: open
8 preview: open
```

Before starting a step, read the line above it. A missing line means the step was skipped: go back and do it in its
cheapest form, or write `skip: <reason>` when the mode lines below allow it.

## Lock and reopen

`LOOK.md`, `cameras.json` and the beat table are locked once the user picks. A change to a locked file goes back to
the earliest step it affects and names what downstream work it throws away, in one line, before doing it.

## Parallel workers only after the lock

Split shots or assets across workers only after step 4. Copy `LOOK.md` (palette, lens, light, grade, scale) and each
worker's cameras into its brief, give each worker its own files, and name the check that proves the shot is done.
Workers that started before the lock drift apart in scale and grade, and no later critique pulls them back.

## Critique loops

- A critic agent answers concrete questions about a frame against the style frame or reference: same light direction,
  palette within range, nothing clipping, subject readable at thumbnail size. It never scores beauty: vision
  models agree with people on visual quality far less often than people agree with each other, so taste stays with
  the user.
- At most three rounds per shot. Stop early when two rounds in a row do not improve the measured difference, and
  keep the best version so far instead of the latest.
- Read many frames through a subagent that returns text; open only the frame a decision hangs on.

## After the preview: the next round

End every preview with two or three concrete next directions (one line each, the recommended one first) and a "you
decide" choice. The user's answer picks the round:

- **Notes or changes:** a fix round. Update `brief.md` or `LOOK.md` first, then redo only the shots the notes touch,
  then rerun the gates on every shot so a fix does not bring back an old defect. A note the user gives twice becomes
  a check in `qa-and-gates.md`.
- **Approved:** render the final, then offer the next directions again.
- **Continue in a direction** (one of the offered ones or the user's own idea): start a new round at the earliest
  step the direction changes, usually step 3 (new beats) or step 4 (new look), and follow the user's direction even
  where another seems better; say the concern once in one line.
- **"You decide" / free creative mode:** the agent picks the next direction itself from the brief, the references and
  what the last round lacked, writes the choice and its reason as a new line under `## Progress`, and runs the round
  through the same steps, choosing its own option at step 4. It sends the WIP and the preview of each round without
  waiting, and keeps going until the user stops it, the brief's done condition is met, or three rounds have run;
  then it reports and offers the next directions. Free mode never publishes, spends money or deletes anything.

## Steps per mode

- 3D `cutaway`, `story`; 2D explainer (`script`, `vox-now`, `archival-collage`): all eight steps.
- 3D `world`: step 3 shrinks to a scene brief and one camera path; the look gate shows a style frame and the path.
- 3D `character`: step 3 is skipped; the look gate shows a turnaround and one posed frame; step 6 is a rig test,
  a walk and an idle; step 7 only when the character speaks.
- 3D `asset`: steps 3 and 7 are skipped; the look gate is one hero still with a material close-up.
- 2D `map`, `chart-timeline`, `thumbnail`, `texture-look`, `fx-type` alone: steps 3 and 7 shrink or skip; the
  reference step is the real data or source; the look gate is one frame.
- Game `prototype`: steps 1 to 4; the choice at step 4 is the user playing the greybox, ending in a go/kill note.
  Game `game`: all eight, with a playable greybox at step 4. Game `polish`: step 1, then 6 to 8.
- Every mode keeps steps 1, 2, 5 and 8 (game `prototype` and `polish` excepted, as above). Step 4 is kept for every
  new look.
