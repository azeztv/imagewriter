# Lessons from shipping a jam game (`lessons-from-shipping.md`)

Each rule below came from a real failure. Run them as checks at steps 6 to 8; read the section that matches the work in
hand, not the whole file.

<!-- skill-navigation:start -->
## Reading Map

- [Lessons from shipping a jam game (`lessons-from-shipping.md`)](#lessons-from-shipping-a-jam-game-lessons-from-shippingmd)
- [Scope churn kills the entry](#scope-churn-kills-the-entry)
- [Onboarding and the first minute](#onboarding-and-the-first-minute)
- [Screens the bot skips](#screens-the-bot-skips)
- [Composed pictures: generator and preview](#composed-pictures-generator-and-preview)
- [Figures and icons at low resolution](#figures-and-icons-at-low-resolution)
- [HUD discipline](#hud-discipline)
- [World readability](#world-readability)
- [Pause and voice](#pause-and-voice)
- [Mechanics and depth](#mechanics-and-depth)
- [Parallel workers on one codebase](#parallel-workers-on-one-codebase)
- [Text, splash art and rebuilds](#text-splash-art-and-rebuilds)
<!-- skill-navigation:end -->

## Scope churn kills the entry

A jam entry was dropped 36 h before its deadline after its core loop changed four times in three days (scan, ball
decoy, parkour, a blind sound-hunting monster) and its name five times.

- After the step 4 freeze, a new core idea is a restart at step 4, not a feature. Say so with the cost in hours
  against the deadline, and build it as a separate greybox while the frozen build stays shippable. Swap only after
  the owner plays the new greybox and says yes.
- A new movement mechanic (jump, parkour, climb) is a greybox room first; wire it into the level only after a yes.
- Pick the title once, from a short list at step 1. Lock the story and the voice line list before recording.
- When a mechanic is removed, grep every trigger that depends on it (voice lines, hints, counters, achievements) and
  replay a full run to count silent stretches: removing a scan once muted the whole narrator.

## Onboarding and the first minute

- The first route is linear. An open map before the player knows the rules left the owner unable to say how to play.
- Teach one mechanic at a time. A control that is not taught yet is disabled, and a physical gate (door, grate)
  stops the player from skipping a lesson.
- Every interactable shows a prompt at range with the real key or mouse-button icon for the current input device.
- A player choice is not automated away: no auto-pickup when picking up is a decision.
- Every system changes a player decision or it is cut. A charge or wake meter nobody plans around is noise.
- Check the first 10 s of a real capture: the core visual must read at once, not after a few seconds of staring.
- Every pressure curve (heart rate, noise, stress) starts slow for a new player and falls again when the player
  stops. Run the first room with a new-player bot (no optimal inputs) and check that the curve has a floor.
- Text the player must read uses a legible font; ASCII or glyph styling is decoration only.

## Screens the bot skips

- A screen the playtest bot never reaches is never seen: start menu, pause, settings, death or game over, endings.
  Give each its own capture mode (a flag or console command that jumps straight to it) and read its frames before the
  owner opens the build.
- A capture taken while the game is paused must end on real time, not on a world timer: world timers do not fire while
  paused, and a capture that waited on one hung for an hour.

## Composed pictures: generator and preview

Staged visuals designed blind fail round after round (a death tableau and a logo took four rounds). For any composed
picture (cutscene tableau, logo, HUD icon, title art):

1. Calibrate first: check that the engine honours the per-item size and colour the generator assumes. In one case the
   material ignored per-instance size and everything drew three times too large.
2. Author the picture as data in a small generator that also renders a preview with the game's real camera, field of
   view, resolution and mark or sprite size.
3. Look at the preview and iterate there, not in the engine.
4. Export the data table to the engine, then compare one captured game frame against the preview.

## Figures and icons at low resolution

- Silhouette first: a closed outer contour, 2 to 4 interior lines, figures kept apart on screen. A fresh viewer must
  name each part from one still.
- An icon must read at the size it ships: test it at that size beside real text. If people cannot name it, replace it
  with a simpler shape. When the look is a taste call, put 3 or 4 options on a sheet at real size and let the owner pick.

## HUD discipline

- No exposition text on screen; the story is told in play.
- Controls appear only where they are used or in the first lesson, never as a legend on the menu or default HUD.
- An element shows only while it matters (for example a rhythm lane only above a stress threshold).
- Icons are 1.2 to 1.3 times the height of the text beside them, on one row, centred on the same line.
- A plate or backing is centred on the letters (ascender to baseline) with equal padding on all sides.
- No two HUD blocks overlap.
- Verify with a script on captured frames (bounding boxes, paddings, centre lines), not by eye: eyes miss a 3 px drift.

## World readability

- After any change to point or sprite size or brightness, check a frame for blow-out (pure white), colour fringing,
  minimum glyph size and mean brightness.
- Change one variable at a time and re-measure. A fix for "too bright" that dimmed and shrank everything caused eye strain.

## Pause and voice

- Pause freezes everything: enemies, timers, effects, voice, music and SFX; only the pause menu runs. Test it by
  capturing two frames and the audio level 2 s apart while paused; both must match.
- One voice at a time: route every spoken line through one channel with a queue and priorities. A critical line
  interrupts, an ambient line is dropped when busy, a stale queued line is dropped. Location-triggered lines are the
  usual cause of overlap.

## Mechanics and depth

- A mechanic the owner cannot explain after playing gets cut or replaced, not explained with more text.
- Variation per death or run (a different threat rule each time, reusing the same assets) adds depth cheaply in a jam.

## Parallel workers on one codebase

- Give each worker a disjoint file set, and gate edits on "no compile or capture running".
- Before adding a symbol, grep for name clashes with shared headers; compile after merging each batch.
- Syntax-check generated source: float literals carry a decimal point, no duplicate enum entries, property names are
  verified against the engine's API before use.

## Text, splash art and rebuilds

- Player-facing text uses plain ASCII punctuation: no middle dots, bullets, em dashes, arrows or decorative separators
  (fonts lack the glyphs and they render as boxes). Rewrite the line in plain words.
- Brand or splash art drawn additively needs a black background. Check the imported image's pixel statistics (share of
  dark against bright pixels): a transparent source turned into a white box.
- Tell the owner before closing their running game to rebuild, batch fixes into one rebuild, and reopen it afterwards
  without being asked.
- Launch the game with no console window (no `cmd /K` launcher), and confirm the game window is on screen before
  saying the build is open.
