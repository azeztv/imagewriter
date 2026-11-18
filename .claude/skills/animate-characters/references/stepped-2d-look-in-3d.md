# 2D-style timing in 3D

How to make a 3D scene move like hand-drawn animation: poses on twos and threes, stepped shaders and a boiling outline.
Notes come (Blender). Check tags: `heard` means the voice-over only, `verified` means a frame confirmed it.
For the look itself (toon shader, outlines, painted textures) read
`model-characters` `references/npr-shading-and-painted-look.md`. Do not copy it here.
Smears and effect planes are in [smears-and-vfx-planes.md](smears-and-vfx-planes.md).

<!-- skill-navigation:start -->
## Reading Map

- [2D-style timing in 3D](#2d-style-timing-in-3d)
- [Pick the step size](#pick-the-step-size)
- [Pose workflow on twos](#pose-workflow-on-twos)
- [Fours, then twos, then threes](#fours-then-twos-then-threes)
- [Turn threes into twos](#turn-threes-into-twos)
- [Stepped shader time with floor](#stepped-shader-time-with-floor)
- [Line boil and Sketchify](#line-boil-and-sketchify)
- [Jitter with Displace and an Empty](#jitter-with-displace-and-an-empty)
- [Linear loops that run forever](#linear-loops-that-run-forever)
- [Work in a clean file](#work-in-a-clean-file)
- [WIP clips: pipeline, frame counts and beats (seen from silent clips)](#wip-clips-pipeline-frame-counts-and-beats-seen-from-silent-clips): pipeline, frame counts and beats
<!-- skill-navigation:end -->

## Pick the step size

| Shot | Step | Why |
| --- | --- | --- |
| Fast action, jumps, fights | Twos | Poses change every 2 frames, so the motion stays crisp. |
| Slow or small motion, looking around | Threes | Saves work and reads as hand drawn. |
| Close-up of a face or a hand | Twos plus extra in-betweens | A close-up on plain threes feels unpleasant. |
| Camera, water, shaders | Match the character | One step size for the whole frame, or the shot looks mixed. |

- A different step size per channel (stepped body, smooth camera) is a choice. Use the Stepped Interpolation modifier in
  [timing-and-graph-editor.md](timing-and-graph-editor.md).
- One note gives the "golden rule" that twos play at about 21 fps. He lowers the scene frame rate after he converts
  threes to twos (see below). Treat 21 as his number, not a standard. (heard)

## Pose workflow on twos

1. `Ctrl+Tab` for Pose Mode. Turn on Auto Keying.
2. For each new pose, press `A` (select all controls), move the controls you need, then press `I`. Every bone gets a key
   on every pose. Without that, some bones hold keys on some frames only and the motion drifts.
3. Select all bones and all keys. Press `T` > Constant. This is the choppy 2D look. The same `T` menu works in the Dope
   Sheet and the Timeline.
4. For one in-between, select the bones and press `Shift+E` (the Breakdowner), then drag
   the percentage. Per bone is fine.
5. Smooth a problem area in the Graph Editor, for example the main controller's X location curve.

- Verified in the Bedroom cinematic frame at 05:31 (Blender 4.5): the Dope Sheet shows keys every 2 frames
  (24, 26, 28 ... 50).

## Fours, then twos, then threes

1. Block the key poses on fours (or on eights for a long shot: one pose per 8 frames, then midpoints for fours, then twos).
2. Add in-betweens until the shot is on twos. They are not exact midpoints. Keep contrast between poses: 19 to 21 moves
   a little, 23 jumps far.
3. Use threes where little happens.
4. Turn on motion paths (Pose Mode > Animation panel or Pose > Motion Paths > Calculate) and check an even distance
   between frames on the way in and out of a pose.

Frog jump example from the 1 hour tutorial (frame numbers): 11 sit, 15 squash, 19 squash more, 23 jump (instant, no
wait), about 27 slows near the peak, 31 stretch while falling with the feet near the ground, 35 land with the body
rotated up, 39 fully squashed, 43 recover, 47 neutral. Frames 47 to 50 (the frog looks around) are on threes.
Squash and stretch itself is in [principles.md](principles.md).

## Turn threes into twos

- On the key frames use `Shift+E` (the Breakdowner). For the frame between two keys, set 66% on one and 33% on the
  next. Delete the middle key, then lower the scene frame rate. (heard)

## Stepped shader time with floor

Animated shader values move smoothly by default. Step them so water, rain and smoke match the character.

1. Type a driver expression into the value field (Wave Texture Phase Offset, Mapping location). Start with `#frame * -0.25`. A negative sign reverses the direction.
2. Step it: `floor(#frame / -3)` changes every 3 frames. Use 2 for twos and 4 for fours.
3. Slow it down with a divisor outside the floor: `(floor(#frame / -3)) / 5`. A smaller divisor is faster.
4. Alternative: lower the scene frame rate for everything at once.

- The floor part sets the step. The final divisor sets the speed. Type the `#` so the expression runs every frame.
- Verified at 50:08 in the 1 hour tutorial (Blender 4.5): Mapping Y expression `(floor((frame) / -2))/-8`.

## Line boil and Sketchify

- Boil means the outline changes a little every 2 or 3 frames, so it looks redrawn.
- Sketchify is a free add-on. Install the zip (Blender 4.2+: Edit > Preferences > Get Extensions, drop-down arrow,
  Install from Disk). In the 3D viewport press `N` > Sketchify tab > Enable Add-on, then press `Space` to play.
- Settings: line thickness, line harshness, blur, scale, spreading and colour. Colour Influence 0 lets Hue/Saturation/Value
  replace a solid colour. A Secondary Colour adds a second outline with its own blend mode (Mix replaces).
- Timing: the default is threes. Type another number and press Apply Timing: 5 is choppier, 1 or 2 is smoother.
  The Speed field is inverted: an absolute value of 500 to 600 is slow, 10 to 20 is fast. The sign does not matter.
  Press Apply Timing after each change.
- Verified at 06:00 (Blender 5.0.1): Line Strength 12, Scale 22.5, Roughness 0.5, Extra Thickness 0.07, Blur 0.3,
  Line Harshness 1.55, Spreading 0.555, Color Influence 1.0, Timing 3, Speed -100.
- Camera distance changes the look, so retune per shot. In an existing scene, if the lines look wild, lower line strength,
  roughness and extra thickness, raise blur, lower harshness.
- Cylinders need right-click > Shade Auto Smooth (Blender 4.1+). Plain Shade Smooth gives a wrong outline.
- An object on a background of its own colour loses its back edges. Add a real object outline too, so a line stays with the
  add-on off.
- Plain Blender route: the Noise modifier with a small Strength on a curve outline, stepped with the Stepped Interpolation
  modifier, or the Displace jitter below. (inferred, not shown)

## Jitter with Displace and an Empty

- Add a Displace modifier. Set Texture Coordinates to Object and pick an Empty. Move or key the Empty and the surface
  boils. Key it on twos or threes to match the shot. Use it for a fried egg or flame layers.
- The note says the egg uses this. (unverified: the frame at 01:16 shows an outline Solidify with Thickness 0.025 m,
  Offset 1.0, Flip on, Fill off, Material Offset -100, not the Displace settings.)

## Linear loops that run forever

- Right-click a Mapping value (for example Z Location) > Insert Single Keyframe. Move the timeline, change the value, insert
  another key. Select both keys, press `T` > Linear, then `Shift+E` > Linear Extrapolation. The motion never stops.
- Speed follows the distance between the two keys in time. Farther apart is slower. A wheel works the same: rotate the
  parent Empty with Linear and Linear Extrapolation. Ripples: key the Wave Texture Phase Offset the same way.
- Make materials single user (the number button) and vary the values and key timing so copies do not match.
- Key the location, not the scale. (One tutorial keyed the scale by mistake.)
- Add a Noise modifier on the Y location curve for a floating duck.

## Work in a clean file

- A heavy scene lags. Copy the rig into a new .blend, animate there, and name the action in the Action Editor.
  In the main file use File > Append > Action, then assign it to the rig by typing its name in the Action Editor.

## WIP clips: pipeline, frame counts and beats (seen from silent clips)

- **Pipeline**: model, rig, animate in Blender (grey 3D pass with keys), then draw over every frame in Clip Studio Paint, with separate named face drawings (`face13 Copy`, `face14 Copy` ...) per frame. His voice-over says the same four steps.
- **Frame counts (guessed)**: the CSP ruler labels step by 3 (28, 31, 34 ... 64) while thumbnails are named frame6, frame7 ... one drawing each. The threes reading was dropped (see the frame-rate note below).
- **Pose beats of the egg loop**: stand with egg falling at lower right (0:00), pick up egg and spatula (0:01-0:03), crack with both hands (0:04), egg open over the pan (0:05), fried egg in pan with hands lowered (0:06-0:07), turn away with hair flying (0:08). Eight to ten visible poses in 9 s at 1 fps; 1 fps samples show no smear.
- **Hair turn-around**: front (0:00), back to camera (0:02), profile with hair streaming out in long wedges (0:03), turn back with one strand across the eye (0:04-0:05), settle (0:06-0:09). Hair leads and lags the head; background and shadows stay fixed.
- **Burger assembly order** (toon 3D): bottom bun, lettuce, patty, cheese, patty, tomato, top bun, settling onto a plate with a soft round shadow. Fire ring in three flat tones (red, orange, pale yellow) with jagged edges.
- **Shot to shot**: whip pans with directional blur and film grain between shots on the dragon scene; the compositor strip is hand-labelled Sharpen, Bloom, Animated Outline, CC (settings unreadable).

- Frame-rate note: the earlier "drawn on threes" reading is dropped. 1 fps sheets cannot show drawings per second; only ruler labels stepping by 3 and one drawing per thumbnail are seen. Comedy shorts swap expression states about once per second with cross-fades.
