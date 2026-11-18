# Game feel: make a small game feel good

Use this at step 6 (feel pass first) and in polish mode. All numbers here are defaults to tune on the target device,
not rules. Feel is control and simulation first; feedback and polish come after. Fun stays a human call.

<!-- skill-navigation:start -->
## Reading Map

- [Game feel: make a small game feel good](#game-feel-make-a-small-game-feel-good)
- [Control and timing](#control-and-timing)
- [Forgiveness windows](#forgiveness-windows)
- [Feedback layers, one at a time](#feedback-layers-one-at-a-time)
- [Camera](#camera)
- [Readability](#readability)
- [Why a small game feels bad](#why-a-small-game-feels-bad)
- [Polish order](#polish-order)
<!-- skill-navigation:end -->

## Control and timing

- Run game logic on a fixed timestep (default 60 Hz). Render at the display rate and interpolate. Never scale
  movement by a raw frame delta alone.
- Read input at the start of each logic step. Two key events inside one frame must both register: queue them.
- Make controls respond on the first logic step after the event. Target: a changed frame within 2 frames of the
  input (default; the probe reports it as advisory).
- Give speed, acceleration and turn rate named constants in one tuning table. Change one number at a time.
- Seed all randomness from `window.__game.seed(n)` so a replay reproduces the run.
- Keep the loop stable at the target frame time. Measure with a sync per frame (read a pixel after each draw), never
  from the animation callback alone: headless callbacks can report a frame rate far above the real one.

## Forgiveness windows

Small windows make controls feel fair. All values are defaults in frames at 60 Hz; tune per game.

| Window | Default | What it does |
|---|---|---|
| Coyote time | 5 frames | Jump still works for a few frames after leaving a ledge |
| Input buffer | 5 frames | A press just before landing or before an action is ready fires when it can |
| Hit forgiveness | shrink the hurt box 10 to 20% under the sprite | Near misses read as misses |
| Pickup magnet | grow the pickup box 20% | Grabs read as grabs |

- Forgiveness never applies to the enemy side. The player gets the benefit of the doubt.
- Log each window in the tuning table so a tester's note ("jump felt late") maps to a number.

## Feedback layers, one at a time

Add feedback to a base that already works, one layer per round, each behind a toggle (a query flag or a settings key).

Order and caps (defaults):

1. Sound on the action. One cue per verb (see design-sound). Peak under 1.0, limiter before the output.
2. Hit-stop. Freeze the sim 2 to 6 frames on a strong hit; keep input and sound running. Never on every hit.
3. Screen shake. Decay over 150 to 300 ms; cap offset at about 2% of screen width; scale with impact; respect a "reduce
   motion" toggle that turns it off. Shake and flash wrap the scene only; draw the HUD and overlays after, unshaken.
4. Particles. Few, short, on the event only. Cap the count; check frame time after adding them. No ambient glow around
   a human-scale hand or body.
5. Squash and stretch. 10 to 20% scale change over 3 to 6 frames, volume kept.
6. Flash or tint. One or two frames on hit.

For each layer, record a before/after clip pair of the same replay with the toggle off and on. Keep the layer only if the
after clip reads better and frame time still passes. Too much feedback hides the game: cut when two layers fire together
and the player cannot tell what happened.

## Camera

- Never hide the player or the threat. Test: with the camera at its extremes, the player stays inside the safe frame.
- Lead the motion: look ahead of the player in their travel direction, with a damped follow (no snap).
- No camera shake on the player's own movement; shake is for impacts.
- Third-person cameras need a collision check against walls; fix clipping by pulling the camera in, not by hiding walls.
- Keep the horizon level unless tilt is the game.

## Readability

- The player, the threat and the goal each have a distinct silhouette and a distinct color from the background and from
  each other. Rank them: the player is the strongest color on screen.
- Check at phone size (360x640) and desktop (1920x1080): crop the frames, shrink them, and look. Contrast of 3:1 between
  each of player, threat and goal and the background is a default target (advisory).
- HUD stays small, at the edges, and never covers the play area. The controls line stays visible on the title or start screen.
- A hit, a pickup and a win each change the picture, not only the sound.
- Judge more than 5 frames through a subagent that returns text. Treat a repeated finding across two passes as real; a single
  mention is a hint.

## Why a small game feels bad

| Symptom | Likely cause | Fix |
|---|---|---|
| Controls feel late | Input read after the frame, or heavy frames | Read input first in the step; cut frame time; check p95 |
| Controls feel floaty or stiff | Acceleration and friction off | Raise acceleration, add stronger stop friction; tune one number |
| Deaths feel unfair | Hurt box too big, threat off-screen, no telegraph | Shrink hurt box, show the threat early, add a 0.3 to 0.5 s telegraph |
| No sense of impact | No feedback layers | Add sound, then hit-stop, then shake, in that order |
| Too much noise on screen | Many layers at once | Remove layers until the cause of each event is clear |
| Boring first minute | Slow start, no goal shown | First input within 10 s; show the goal at once |
| No stakes | No lose, or lose has no cost | Add a timer or a threat; make restart instant |
| Camera hides threats | Follow offset behind obstacles | Pull in, raise, or fade the occluder |
| Stuttering motion | Variable timestep or garbage collection | Fixed step; reuse objects instead of allocating each frame |

## Polish order

1. Feel: timestep, response, forgiveness, then feedback layers one at a time.
2. Readability: silhouettes, contrast, camera, HUD at phone size.
3. Audio: a cue for every player action and outcome; loudness measured; a muted run still plays.
4. UI: title, controls line, end screen, restart in one input. Pause on blur and on a hidden tab, release held keys on
   blur, resume on a press. Text over the scene gets a dim backing and a minimum on-screen size; a controls line
   stays on one line and fades after the first seconds of play.

After each stage run the hard gates again. Polish mode adds no features; a new idea goes to the cut list.

Sources: Swink, "Game Feel" (2009); Jonasson and Purho, "Juice It or Lose It" (2012); Kelly, "Don't Juice It or Lose It" (2014). Forgiveness frame counts are community defaults, not measured.
