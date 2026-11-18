# 2D motion-design animation

Blocking with holds, easing curves, anticipation, overshoot, secondary action, boil, shape morphs and simple character rigs,
as taught in After Effects and translated to free tools. Each entry: what it makes, the After Effects (AE) steps, the
principle, the free route (Fusion, Blender, web or Remotion), a pitfall, the source and a check tag. `verified [frame]`
means a video frame confirmed it, `heard` means the voice-over only. A route marked "untested" was not tried here.
For the 12 principles read [principles.md](principles.md). For Blender curve work read
[timing-and-graph-editor.md](timing-and-graph-editor.md). Hand-drawn frame work is in
[2d-frame-by-frame-and-cutout.md](2d-frame-by-frame-and-cutout.md). Face swaps are in [acting-and-faces.md](acting-and-faces.md).

<!-- skill-navigation:start -->
## Reading Map

- [2D motion-design animation](#2d-motion-design-animation)
- [Workflow and blocking](#workflow-and-blocking)
  1. Block with holds, ease later, then secondary
  2. Uneven spacing to sell an impact
- [Easing and the graph editor](#easing-and-the-graph-editor)
  3. Easy Ease, value graph and speed graph
  4. Steep ease recipes (cubic-bezier table)
  5. Anticipation and overshoot on a move
  6. Bounce: linear on impact, eased at the apex
  7. Arcs and spatial interpolation
  8. Loops: speed never zero, ping-pong, easy ease on a loop
  9. Retime a keyframe set and smooth spacing
  10. Hold keyframes, flashes and stepped blinks
  11. Ease Copy, graph helpers and paid tools
  12. Deliberate linear, and match cuts
- [Secondary action and overlap](#secondary-action-and-overlap)
  13. Secondary action from momentum
  14. Wave principle for cloth, hair and tails
  15. Keep a still character alive
  16. Parallax and loops from copied keys
  17. Show the result of an action: splash and drip
  18. Smears and blob transitions
- [Hand-drawn feel](#hand-drawn-feel)
  19. On twos: Posterize Time and stepped time
  20. Wiggle Paths boil and flame on twos
  21. Frame-by-frame cycles and bounces
  22. Run and walk cycle mistakes
  23. Shape-layer cleanup over roughs
  24. Frame-by-frame assembly: Sequence Layers, PSD import, stop motion
- [Shape layers and morphs](#shape-layers-and-morphs)
  25. Path morph: first vertex and in-between shape
  26. Hide the swap in the fastest frame
  27. Shape parameters that already span two shapes
  28. Mirror a half shape
  29. Per-letter stretched type
  30. Gooey blur plus alpha levels
  31. Offset Paths burst and cel spread
  32. Twist spiral, Repeater loops, impossible triangle
  33. Mattes: shine sweep, shadow, clip to a base shape
  34. Gradients: beam and animated gradient bubble
  35. Echo trail, radio waves and shards
- [Character and rigging](#character-and-rigging)
  36. Layer-per-part rig with parents and a null controller
  37. Simple eye rig with nulls
  38. Blinks: open slow, close fast
  39. Fake turn, mouth swaps and counter-rotation
  40. Puppet Pin, rigging plugins and Duik-free routes
- [Currency: renamed and removed features](#currency-renamed-and-removed-features)
- [Sources and licences](#sources-and-licences)
<!-- skill-navigation:end -->

## Currency: renamed and removed features

- Properties panel: standard since AE 2022 (Window > Properties). Use it instead of twirling every timeline group.
- Gaussian Blur (Legacy) sits in the Obsolete group: use Gaussian Blur. Set Matte still ships, but since AE 23 a track
  matte can point at any layer, which covers most Set Matte uses without its transform limits. Wiggle Paths, Offset
  Paths, Twist, Repeater and Taper are still in the shape layer menu.
- Motion v2 was replaced by Motion 3 (same developer). "Duik Ik" is now Duik Angela, free. Roto Brush 3 and Object
  Selection replace hand masks for cut-outs.
- AnimDessin 2 (the free Photoshop frame-animation panel) is unsupported on new Photoshop. Use Photoshop's native frame
  animation, Rough Animator, Krita or Grease Pencil instead.
- Puppet Pin still exists under the Pin tool. Ben prefers rebuilt shape layers over raster Puppet pins and mesh warps.

## Workflow and blocking

### 1. Block with holds, ease later, then secondary

- Makes: a character loop or hit that is cheap to fix because timing is settled before easing exists.
- AE: import the layered Illustrator or PSD file as a composition (Retain Layer Sizes), colour-label, parent parts to the
  head, head to a null controller. Key only the biggest property first (rotation carries an impact, then position) with
  hold keyframes (right-click keys, Toggle Hold Keyframes, or Ctrl+Alt click). Act the sound out loud to find the beat.
  Pass 2 detail shapes. Pass 3 convert to regular keys, add an anticipation dip and an overshoot, then F9 on the keys and
  shape handles in the graph editor. Pass 4 secondary motion (item 13). Pass 5 grit (item 20). One comp per pass
  (`a01_Blocking`, `a02_Refined`, `a03_Secondary`, `a04_Details`) works for client rounds.
- Principle: easing hides bad timing and makes later changes messy. Send blocking to the client early, before texture.
  A deliberately rough first pass with few poses already reads as motion with tension (three holds were enough in his demo).
- Free: Blender: Constant interpolation in the Dope Sheet, then Bezier and Graph Editor. Fusion: Step In/Out splines on a
  Transform, then smooth (untested). Web: CSS `steps(1)` or a quantised Remotion `interpolate`, then a `cubic-bezier`.
- Pitfall: do not ease before the timing is agreed. Use empties or bones as controllers, not parts.
- Check: verified [t6BX 02:00 hold keys, 03:30 stepped value graph; YrqT 01:25 four comps and parent column; 8dRr 02:45 stack]

### 2. Uneven spacing to sell an impact

- Makes: a swing that "claws into" its target.
- AE: key rotation so the early steps are close together and the last gap is huge, no ease into the hit, hold after it.
- Principle: evenly spaced arcs read smooth. Accelerating spacing then a stick reads as force. Centring the middle key kills it.
- Free: any ease-in curve that ends on a hold (CSS `cubic-bezier(0.7,0,1,0.4)`, my numbers, then a held end).
- Check: verified [6:50 his spacing diagram: even ticks on the left arc, bunched ticks then one long jump on the right]

## Easing and the graph editor

### 3. Easy Ease, value graph and speed graph

- Makes: soft starts and stops. Easing changes only the speed profile, not the duration: an eased layer starts behind a
  linear one, passes it mid-way and lands on the same frame.
- AE: keys, F9 (Easy Ease), Graph Editor. Value graph shows direction of travel and is the one he prefers. Speed graph
  shows one bell-shaped hump for rest-to-rest, which is the only choice for a Path (a path has no value). Separate
  X and Y (right-click Position, Separate Dimensions) before shaping. Learn the editor before using ease plugins.
- Principle: the speed curve carries the feel. Steeper hump is snappier. A slow ease-in feels floaty, so shorten the
  time before adding more ease. Linear is right for things already moving (conveyor, robot).
- Free: Blender: select keys, `T` Bezier, `V` Auto Clamped, drag handles. Fusion: Spline editor, right-click Smooth.
  Web: `cubic-bezier(0.65,0,0.35,1)` or `Easing.inOut(Easing.cubic)`.
- Check: verified [hb2b 04:40 hump frame; LcWJ 09:50 value graph]; the rest heard

### 4. Steep ease recipes (cubic-bezier table)

All move most of their travel in the first or last few frames. Shorten the distance or the trim rather than the handles.

| Use | Curve or edit | Check |
| --- | --- | --- |
| Blast-in slide of two words | `cubic-bezier(0.02, 0.96, 0.03, 0.98)`, then shorten the travel | verified [dnBq 10:40 panel values] |
| Eyelid drop, stinger gag | `cubic-bezier(0.97, 0.02, 0.98, 0.06)`, pair with a hold | verified [yNPx 0:45 panel values] |
| Snappy type arrival | First speed handle far right, last far left, small start offset | verified [jS1Y 1:03 bell speed curve] |
| Sink, 104% to 100% as text lands | Value graph, first handle straight down, last far left; add blur 20 to 0 | verified [jS1Y 7:05 104.0% to 100.0%] |
| Impact, shards burst then drift | First handle fully left, drag end keys later to stretch the tail | verified [rsqg 5:55 arch curves, 500 to 1000 px/s] |
| Ring or size hit, 400 to 800 | Value graph, first handle vertical, last horizontal | verified [rWUZ 2:15] |
| Explosion scale 0 to 100 in 22 f | F9, pull first handle so it shoots up and flattens | heard [w8mH] |
| Path morph, maximum ease | F9, speed graph, both handles far out, 12 f total | verified [n24a 09:44 one tall peak] |
| Approach from far (grid tunnel) | Slow start, near-vertical end rise on Size | verified [JXth 1:55 exponential curve] |

- Free: Blender: handle type Vector then pull; Fusion: spline handles; Remotion: `Easing.bezier(...)`. The curve numbers
  in the table are Ben's panel values only for the first two rows. Other rows give the shape, not exact numbers.

### 5. Anticipation and overshoot on a move

- Makes: a shape that winds back, whips across, overshoots and settles. Keep the whole snap under about 10 frames.
- AE: Position keys: a key near the start nudged opposite the move, the main move, a key after the target nudged past it.
  Separate Dimensions, delete Y keys. Select X keys, F9, pull the first and last handles long, point the middle handles at
  each other for a steep middle. Two-key version: pull the first key's out-handle so the curve dips below the start. Make
  the held pose never perfectly flat (tilt the handle). Anticipation can sit on Rotation (opposite way), Path or Scale.
- Principle: energy builds before the action and drains after. With several objects on screen the one that anticipates
  gets looked at, so anticipation steers attention. A dip on a parent null (shrink to 90% before a burst, null up, dip,
  hold low, rise) makes a morph read as one object.
- Free: Blender: key X location, move a key earlier and opposite, `T` Bezier, `V` Auto Clamped. Fusion: Center X spline,
  drag a key behind the start (untested). Web: `interpolate(frame,[0,a,b],[0,-d,end],{easing})` or CSS stops at -3% and 103%.
- Pitfall: with two keys only, the start accelerates suddenly. Fine for small fast moves.
- Check: verified [3EGu 02:00 flat, near-vertical rise, flat tail; LcWJ 02:05 three holds, 08:15 dip below start; n24a 21:45 parent null]

### 6. Bounce: linear on impact, eased at the apex

- Makes: a rigid ball that falls at full speed and does not ease into the ground.
- AE: key up and down positions, ease only the apex (hang time) keys, leave the bottom keys linear. For a falling drop:
  Separate Dimensions, delete the unused X keys, F9 on Y, Fit All Graphs, drag the first handle up so the fall starts fast.
- Principle: gain speed falling, arrive at full speed. Ease out at the apex, never at impact.
- Free: Blender: Auto Clamped at the apex, Linear at impact. Web: `cubic-bezier(.33,0,.67,1)` rise, `cubic-bezier(.55,0,1,.45)` fall (my numbers).
- Check: verified [8dRr 4:40 alternating diamond and hourglass keys; YrqT 01:25 X and Y rows]; the curve shape heard

### 7. Arcs and spatial interpolation

- Makes: motion that follows the path you drew, not a path AE invented.
- AE: AE bends a position path between keys by default. Set Spatial Interpolation to Linear (right-click keys, or
  Preferences > General "Default Spatial Interpolation to Linear"). Make arcs on purpose with the Convert Vertex tool on
  the motion path: eyes and limbs move on slight arcs, "very few things in the natural world move in straight lines".
  Two identical middle keys with auto-Bezier add a bump you did not key.
- Free: Blender F-curves are per axis, so no hidden arc; use motion paths to check. Fusion: Path with Linear points.
- Check: verified [3neS 40s arcing path; whFa 100s preference ticked]; eye arcs heard

### 8. Loops: speed never zero, ping-pong, easy ease on a loop

- Makes: a loop that breathes instead of stopping at every key.
- AE: copy the first key to the end (one frame past the visible end so no duplicate frame shows), then `loopOut("cycle")`
  on Position. For a figure-eight, round the path with Convert Vertex. In the value graph lift handles so speed never
  reaches 0 and add variance between fast and slow. For circles in and out, F9 on every key. Blur keyed 10, 60, 10, 60 peaks
  when things move fastest. Ping-pong pulse (square becomes circle, jellyfish base): two keys each on Position, Size 50
  to 150, Roundness 1 to 75 (never 0, no sharp frame), Stroke Width 30 to 10, F9, `loopOut("pingpong")` on Position, then
  Copy Expression Only onto the other properties. A change is then two keys.
- Principle: key only the extremes and let one expression repeat. Check the seam frame.
- Free: Blender: Cycles modifier (Mirrored for ping-pong). Fusion: Loop or ping-pong spline modifier (untested menu).
  Web: `Math.abs(((frame/period)%2)-1)` for ping-pong.
- Check: verified [Wfea 03:40 loopOut text; LUoT 2:52 expression box, 5:22 curves, 1:20 panel]; value-graph lift heard

### 9. Retime a keyframe set and smooth spacing

- Makes: a calmer or faster pass without re-keying.
- AE: select all keys, hold Alt and drag the first or last key: spacing and easing scale together. Keyframe Assistant >
  Rove Across Time evens speed along a spatial path (heard). Scaled keys can land between frames: check at 12 fps.
- Free: Blender: select all keys, `S` scales time about the current frame (scale the frame axis, see rule 10 in the
  skill). Web: multiply every offset by one factor.
- Check: verified [t6BX 09:36 keyframe grid; gBBr 06:30 strobe keys 0, 3, 6 f]; Alt-drag and Rove heard

### 10. Hold keyframes, flashes and stepped blinks

- Makes: a property that steps like a drawing instead of tweening.
- AE: right-click keys, Toggle Hold Keyframes. Opacity 100 to 0 holds flick like a loading cursor. Closed-eye layer
  opacity 0/100 holds with the open eyes keyed exactly reverse, so two eyes never show together. Eyebrow drops on close.
- Free: Blender: Constant interpolation. Fusion: Step In/Out. CSS `steps(1)`. Remotion: `Math.floor(frame/2)*2`.
- Check: verified [YrqT 02:35 mirrored opacity keys; MG84 85s hold series]

### 11. Ease Copy, graph helpers and paid tools

- Makes: one timing curve shared across Position, Scale, Rotation and Path, with offsets for overlap.
- AE: the free EaseCopy panel: Copy on source keys, Paste Ease on targets (Value and Pass-through options). Native AE
  copies keys but not the Bezier shape between properties. Flow (30 USD, aescripts) and Motion (Motion v2 65 USD, now
  Motion 3, mountmograph.com) are paid curve helpers: ideas only. Ben says to learn the graph editor first.
- Free: Blender: Ctrl+C and Ctrl+V keys in the Graph Editor keeps handles. Fusion: copy the spline. Web: one shared easing constant.
- Check: verified [X8Ji 02:36 EaseCopy panel; Ddb5 7:00 Flow curve card]; the copy workflow heard

### 12. Deliberate linear, and match cuts

- Linear, no ease for a 1970s feel: two position keys, a pause before and after, linear opacity fades. A modern eased
 scale breaks the era. Check: heard.
- Match cut with scale push: scene A scale 100 to 105% ending on the last frame before the cut, eased out of the first
  key and accelerating into the second; scene B 105 to 100% starting on its first frame, easing into the second key. 5% may
  be too much. Works on Position and Rotation too. Free: Blender VSE Transform strip with an F-curve; Remotion
  `interpolate` with `Easing.in(Easing.cubic)` on A and `Easing.out` on B. Ideas: match subject, motion or composition across
 the cut, or time a 2-frame wipe to a voice-over word.
  Check: verified [1:32 Scale 105%; 1:40 value graph flat then shooting up].

## Secondary action and overlap

### 13. Secondary action from momentum

- Makes: a sword, hair or tail that keeps moving after the body stops.
- AE: find the driver (body Y Position, 4 keys). On the child Rotation add keys at the same times, lean forward past the
  body at the low point, overshoot at the rise, settle at the end. Nudge the keys 1 to 2 frames later. Paste the driver's
  ease with Ease Copy so the curves match. Legs counter-rotate to the body. Hair and head delay from body rotation.
- Principle: car-brake analogy: the attached object has its own momentum, lags the driver by 1 to 2 frames and overshoots.
- Free: Blender: copy F-curve keys, offset them; Remotion `spring` with `delay`.
- Check: verified [YrqT 04:20 Sword Rotation keys aligned to Body Y keys]

### 14. Wave principle for cloth, hair and tails

- Makes: soft things moving as a wave that travels along the shape and loops.
- Frame by frame: draw 4 key poses of the leading edge of a cloak, rising with the hips, then in-betweens. Spend the most
  care on the leading edge. A tail whips because the base leads and the tip follows. A tear wells, drips, clings, then flies
  off over about 3 frames. Procedural: Wave Warp on a shape (Sine; calm hair Height 5, Width 80, Direction 171, Speed 0.4,
  Pinning Top Edge; strand Height 10, Width 40, Direction perpendicular to the strand, pin the root) plus a rotation key pair
  so it does not look "underwater and perfect". Animate Path from wavy to straight while Wave Height goes 0 to 30 to turn a
  static curve into an animated straight edge (Width 200, Direction 149).
- Free: Blender: Wave modifier or Simple Deform Bend with a vertex group pin at the root (untested). Web: sin offsets that grow from the root, or SVG `feTurbulence` plus `feDisplacementMap`.
- Check: verified [1gQB 04:49, t6BX 10:30, YrqT 06:25 and 06:50 panels]; frame-by-frame advice heard

### 15. Keep a still character alive

- Makes: a long hold on a character who does nothing, made interesting by many small offset moves.
- AE: parent head parts to the head, move the Anchor Point to where the neck is, key head Rotation and Position "very
  slightly". Brows, cheeks, glasses shine, a sword (anchor at the scabbard, moves opposite to the head), coat sections and
  straps (move in as if breathing out) get their own offset timing. Lips Scale about 110% to 90%, more looks broken. Add a
  slow push-in on the whole comp (78 to 79.2%). Approve before texture because grain slows edits.
- Principle: the head leads, parts counter-move, timings differ per part.
- Free: Fusion: Transform per part in a Merge chain. Blender: parent empties or bones. Web: CSS `transform-origin` at the neck, `interpolate` per part.
- Check: verified [03:21 layer list with parents, 04:49 Wave Warp]; head and lip values heard

### 16. Parallax and loops from copied keys

- Makes: depth and ambient life from one animated element, copied and offset.
- AE: Position-only parallax: parent each hill to the one in front, key the nearest hill's end position, give every layer
  the same end key, then nudge each farther layer less at the start. Ease the nearest and copy the ease to the rest. For
  snow or trees: key one flake from off-screen top to below the bottom with a smooth drift and rotation, Alt-drag the last key
  to slow it, duplicate and offset many times. All motion must agree with one wind direction. Front elements are larger and faster.
- Principle: depth is relative speed. AE 3D camera is avoided because each layer needs scale compensation.
- Free: Blender: planes at different Z with a dolly. Web: per-layer `interpolate` with a depth multiplier, or an index-based phase per flake.
- Check: verified [eHw6 02:55 and 04:15 parent column and speed graph]; flake paths heard

### 17. Show the result of an action: splash and drip

- Makes: a hit that reads as real because its consequence is drawn.
- Splash (shape layer): draw the splash at its biggest pose, key Path there; on the first visible frame shrink it; about 0.5 s
  later grow it and push the peaks out; move it under the surface so the peaks arc. Drop: rough blob, three Position keys on
  the same timings, Scale down, tiny Path nudges every couple of frames so it wobbles. Drip: circle falls (F9 on the first key
  so it accelerates), pen-draw a drippy shape over the circle where it meets the surface, key Path with points spaced
  evenly and pulled into one drop, trim both layers at the same frame to hide the cut. Needs the same vertex count in all keys.
- Water splash frame by frame: surface held; ball slower below the surface; splash asymmetrical, more frames at the top of
  each arc; sheet gets holes, tendrils bead into droplets; droplets land at different times with mini splashes; bubbles
  follow an S-wave; surface waves appear on the contact frame and flatten. Mass sets size: a pebble gives few drops over
  6 frames, rain on hard ground lasts about 8 frames.
- Free: Blender Grease Pencil or shape keys on twos; web: SVG path morph between 3 poses, droplets with random velocity and gravity.
- Check: verified [a7Ny 540s drop layer and F9 key; XaHr 03:20, 04:05 onion-skinned roughs]; splash timings heard

### 18. Smears and blob transitions

- Makes: one stretched frame for a fast limb, or a liquid transition from a drawn blob.
- AE: redraw the path elongated on the fastest frames only (one frame, subtle). For liquid, draw blobs trailing the main
  shape: slower and further apart as it decelerates, stretched as it accelerates, about 3 hard in-between frames where it
  turns to liquid. Trailing droplets must not start and stop together. Rebuild as shape layers re-posed every 2 frames.
  Sell a smear with anticipation and easing around it, not detail in the smear frame.
- Free: Blender Grease Pencil, Krita, Rough Animator. See [smears-and-vfx-planes.md](smears-and-vfx-planes.md).
- Check: heard (the keyed AE shapes are visible at _cjE 3:05)

## Hand-drawn feel

### 19. On twos: Posterize Time and stepped time

- Makes: smooth vector or CG motion that reads hand animated.
- AE: adjustment layer on top, Effect > Time > Posterize Time, Frame Rate 12 (12.5 is exact twos in a 25 fps comp; 24 fps
  comps use 12). If the character is on twos and the background on ones, one layer on top steps both. Ben's reason: 12 fps
  gives character and texture, smoothing looks like a soap opera.
- Free: Blender: output rate 12 or Stepped modifier step 2 on the F-curves. Remotion: `Math.floor(frame/2)*2`. CSS `steps(n)`.
- Pitfall: do not apply to audio-synced hits. A foot on contact moves at ground speed, and nearer ground moves faster.
- Check: verified [5mu8 7:00 Posterize Time Frame Rate 12.0; htt 8:10 12 FPS layer]

### 20. Wiggle Paths boil and flame on twos

- Makes: stop-motion boil on a simple vector shape, and a loose flame drawn on twos.
- AE: shape layer, Contents > Add > Wiggle Paths: Size 39, Detail 10 then 1 (Detail 0 moves only drawn points), Points
  Corner, Wiggles/Second 2 then 4, Correlation 50%. Add Posterize Time at 8 fps. Turbulent Displace curves lines, so it
  ruins angular styles. Flame: key Path every second frame on a rough diamond that follows an S path, select all keys,
  Toggle Hold Keyframes, add CC Wide Time (4 frames back, 2 forward) as a fake onion skin, hide it afterwards. Duplicate and
  offset for loose flames. A one-frame offset duplicate at 50% opacity cross-fades each drawing into the next.
- Free: Blender: Grease Pencil Noise modifier evaluated at `floor(frame/3)`, or Geometry Nodes noise at that frame. Grease Pencil and Krita have real onion skin.
- Check: verified [fPRd 02:00 Wiggle Paths values, 02:55 Posterize, 04:25 path keys and CC Wide Time]

### 21. Frame-by-frame cycles and bounces

- Makes: loops built from the fewest drawings first.
- Walk: draw Contact and Passing poses, each held 8 frames, and play it to judge the walk. Add Down and Up (4 frames each),
  then an in-between per pair: 8 drawings x 2 frames = 16 frames. Hips lowest at Down, highest at Up. Trace pants and feet
  over the stick figure at low opacity. Run cycle of 7 drawings: left and right legs are one drawing offset by one frame;
  make the work area a multiple of 7. Legless melon: animate body bounce first, then 4 leg poses, then a pass that draws
  the foot path as arcs, then trace each leg as a 3-point shape.
- Bounce: pass 1 rough path then extremes only; pass 2 a guide with ticks (more frames near extremes); pass 3 in-betweens
  then face and extras; colour on separate layers. Squash and stretch plus a face change per beat.
- Free: Krita animation docker, Blender Grease Pencil, Pencil2D. See [cycles-and-locomotion.md](cycles-and-locomotion.md).
- Check: verified [0cqm 02:10 reference page and 24 fps timeline; t_1s 04:45 extreme frames]; melon pacing heard

### 22. Run and walk cycle mistakes

- Mistakes: (1) limb length changes between drawings, (2) too little hip motion even in a sneak, (3) contact foot slips
  (it must move at the ground speed; nearer ground faster), (4) feet not on arcs, (5) ignoring character design (break any
  rule for the character, but one foot stays on the ground in a walk).
- Fix arcs by plotting: a dot where the foot is every frame on a new layer; walk gives a rounded teardrop (lift, lower,
  slide back at constant speed), run kicks higher. Move off-arc feet onto a smooth curve and keep contacts on the ground line.
- Free: Blender Motion Paths or Grease Pencil dots. Web: plot `x(frame)` and `y(frame)` in an SVG polyline.
- Check: verified [3:05 posterize search, 4:05 foot arc drawn]; numbered list heard

### 23. Shape-layer cleanup over roughs

- Makes: a clean vector look from rough frames.
- AE: pen shape over the rough at lowered opacity, key Contents > Path, nudge points each frame. Do one limb and offset a
  copy for the other. Order inside one limb group: Stroke, Shading, Fill (shading as its own animated path). Comp set:
  Blocking, main limbs, extras, Cleanup, Shading, Details, Smears. Same point count every frame.
- Free: Blender Grease Pencil: rough layer, clean layer, onion skin. Web: interpolated SVG `d` (equal point count).
- Check: verified [-war 04:22 Paw - Clean Path keys at 12.5 fps; WSwk 05:15 Stroke, Shading, Fill order]

### 24. Frame-by-frame assembly: Sequence Layers, PSD import, stop motion

- AE: import the PSD with Import As Composition (Retain Layer Sizes). Select all at time 0, Alt+] trims to one frame,
  right-click > Keyframe Assistant > Sequence Layers (stair-step). Draw each element on its own layer and static things 3 to
  4 times ("boil"), colour separate from line so the look changes late. Loop a short cycle by duplicating the frame layers or
  pre-comp. Painterly frames (Fresco, 12 fps comp): add a paper texture at Multiply. Stop motion: photos into a 12 fps
  comp, Sequence Layers, stabilise on a guide frame. Shoot more frames than needed.
- Pitfall: a PSD with an embedded video may fail to import. Fresco status: check before relying (route unverified).
- Free: Blender Grease Pencil with a Time Offset modifier; Krita animation; Resolve image sequence; web sprite sheet with `steps()`.
- Check: verified [zh1V 2:30 and 3:15; qWiW 9:27 layer list; BcTi 03:25 Sequence Layers menu; AEx2 00:20 12 fps dialog]

## Shape layers and morphs

### 25. Path morph: first vertex and in-between shape

- Makes: a clean morph between two paths (spade to heart to clubs, square to trapezoid).
- AE: AE matches vertices by index, so the first vertex (the one with the small square) must sit in a similar place in both
  shapes. Select the matching vertex, right-click > Mask and Shape Path > Set First Vertex. Delete extra vertices, redraw
  handles with Convert Vertex. Check winding too. Design a rounded in-between blob at the middle key, then move that key one
  frame earlier on the first half. Make both halves visually identical at the swap, and make colour changes holds. Keep the
  design language (curves, no straight edges) in the in-between: it sets the mood. Add keys between two paths to keep
  handles sane. Drawing 4 or 5 frames by hand is often faster than a morph hack.
- Free: SVG or Remotion: rotate the point array to the nearest matching start, equal point counts (`@remotion/paths`
  `interpolatePath` or flubber, untested here). Blender: shape keys need the same vertex order. Fusion: Polyline with matching points.
- Check: verified [3neS 105s and 118s first vertex; n24a 04:12 menu, 16:30 heart; 3EGu 01:06 morph comp]

### 26. Hide the swap in the fastest frame

- Makes: a cut between two shapes the eye cannot catch.
- AE: trim the outgoing layer's end and the incoming layer's start to the same frame in the fastest part of the move; parent
  one to the other. Yin-yang from two circles: a centred null (Ctrl+Alt+Shift+Y), parent both halves, key null Rotation
  with Easy Ease, slide the new layers so their first frame sits in the fastest rotation, optionally a short Path morph either side.
  Cup to circle: remove elements during the fastest movement, ellipse grows with `Size` keys, liquid is a black rectangle
  with the cup lines as Alpha Matte.
- Principle: the eye cannot track change at peak speed. Use a snap of 12 frames or fewer with maximum ease (item 4).
- Free: Fusion: two Polygon masks cross-faded at the fastest frame. Blender Grease Pencil shape keys. Web: swap elements on a frame plus a CSS blur.
- Check: verified [rWUZ 4:55 stack, 2:03 result; 3EGu 01:06]; cup steps heard

### 27. Shape parameters that already span two shapes

- Circle to square: animate Rectangle Path > Roundness from max to 0 (never key it at exactly 0 on a start where you do
  not want a sharp frame). Squash a circle with the ellipse `Size` (one axis to 0), not layer Scale, so stroke width stays.
- Free: CSS `border-radius` 50% to 0, SVG `rect rx`, SVG `vector-effect: non-scaling-stroke`, Fusion rectangle corner radius.
- Check: heard (cup Size keys CUP TOP 400,0 and COFFEE TOP 351,0 verified at 04:40)

### 28. Mirror a half shape

- AE: keep the half shape only. Better than Flip: delete keys on the copy, Alt-click the Path stopwatch, pick-whip to the
  other layer, then flip Horizontal by transform. Frame expression: `thisComp.layer("Spade Half - Right").content("Group 1").content("Path 1").path`.
  Mirror effect (Reflection Center, Angle 180) breaks when pre-comps are scaled or rotated. For mandalas: rulers to the
  centre, draw a quarter, Effect > Distort > Mirror at the centre, duplicate with Reflection Angle 90. Copy With Relative
  Property Links lets one Fill drive many layers.
- Pitfall: a thin centre gap when the mirror centre is off by a pixel.
- Free: Blender Mirror modifier or a negative-scale object sharing data; Fusion Transform X scale -1 into a Merge; SVG `<use>` with `scale(-1,1)`.
- Check: verified [n24a 12:02 and 16:30; a7Ny 810s and 830s Mirror and Mirror 2 at 200,200 angle 90]

### 29. Per-letter stretched type

- AE: Layer > Create > Create Shapes from Text, key every letter's Path, move the last key later, at the first key drag
  each letter's points off to the right. Hold keys: 2 frames partly on screen with the right points dragged far (stretch),
  2 frames later less stretch, 2 frames later at the final spot. Stagger letters by 2 frames. Alternative: two keys with
  strong ease, no holds.
- Principle: speed equals stretch. Design every hold frame to be striking alone. Use sparingly.
- Free: Remotion SVG path `d` quantised with `Math.floor(frame/2)*2`, or stepped `scaleX` with `transform-origin: left`. Blender: text to curve, lattice or shape keys on Constant (untested).
- Check: verified [1:50 five Path rows, 3:10 hold stagger, 4:22 result]

### 30. Gooey blur plus alpha levels

- Makes: text melting into a puddle, one word morphing into another, rounded corners on an animated stroke.
- AE: Gaussian Blur then Levels with Channel Alpha, Input Black and White pulled close with a small gap (about 13100 and
  13500 of 32768, Alpha Gamma 0.40; melt frame 15420 and 16191, Gamma 1.00). Touching gives hard pixel edges. Text morph:
  two layers crossfading 100/0 over 1 s to 3 s, F9; adjustment layer with Turbulent Displace (Size 50, Amount keyed 0 to 50 to 0,
  Evolution to about 180), Gaussian Blur keyed 0 to 100 to 0, then Levels. The comp needs no background layer. Melt: one text
  layer per letter, a melt mat with Set Matte (Invert), letters fall with mirrored Rotation keys (-63, -38, +35, +67), a puddle
  shape key, blur keyed 0 to 150, a Bezier Warp for momentum. Same blur on every frame or edges pop.
- Free: SVG `feGaussianBlur` then `feColorMatrix` alpha row `0 0 0 18 -7` (metaball standard); canvas `ctx.filter = "blur(Npx) contrast(20)"`. Blender compositor: Blur, then Color Ramp with tight stops on alpha (untested). Fusion: Blur then alpha curve (untested).
- Pitfall: words of similar length morph best; render time is high.
- Check: verified [5mu8 2:40 and 5:00 values; MVeV 5:25 and 8:20 levels; Pmmv 03:35 dialog]; Today Round Corners on a shape layer is simpler for rounded strokes.

### 31. Offset Paths burst and cel spread

- Offset Paths burst: trace an outline (Path key each frame, about 36 for 1.5 s), Add > Offset Paths, key Amount 10 to 150
  (up to about 850 to fill the screen). Miter joins leave points: add Gaussian Blur (about 43 to 50) then Levels Alpha to round
  them. Duplicate in 3 colours, delay each ring, duplicate the set to fill. For a seamless loop start copies before frame 0.
  Free: SVG round `stroke-linejoin` with large `stroke-width`, or the gooey filter; Fusion Erode/Dilate (untested).
- Cel spread transition: draw about 27 rough rings outward in new shape layers, Alt+] to 2 frames each, Sequence Layers, 3
  colour comps offset by 4 frames, a Stencil Alpha end layer, texture loop with `loopOut("cycle")` on Time Remap. Hold each
  drawn frame 2 frames and stagger. Free: Grease Pencil with 2-frame holds; SVG rings toggled by CSS `steps()`.

### 32. Twist spiral, Repeater loops, impossible triangle

- Spiral from a line: a straight stroke with Add > Twist (Angle 900, leave Center at 0,0) and Trim Paths (Start 0 to 50 and
  End 100 to 50 around 1:00 draws both arms outward). Stroke Taper (AE 2020, Start and End Length 25%) retracts to 0 with
  the stroke width, about 255, so the last frames are a solid cover. Ease everything at once: finish keys, select all, F9,
  Speed graph, raise influence to about 50% (heard). Free: Blender Curve Spiral plus Trim Curve; SVG polar points with `stroke-dashoffset`.
- Repeater loop: a wave with Repeater Copies 3, Position 1920, Scale X -100% so each copy flips and joins the last; animate
  Repeater Offset, not Position. A shadow copy takes alpha with Track Matte. Infinite zoom: circles offset by half the loop
  period, work area one period; Repeater Rotation `360/12`. Free: SVG `<use>` with `scale(-1,1)`; `rotate(i*30)` loop.
  Check: verified [1ndY 1:03 and 2:20; Ll1x 1:55, 2:45, 3:30].
- Impossible triangle: three identical pieces rotated 120 degrees, each a Path morph keyed in a pre-comp ("Tri Segment"),
  sequenced and rotated -120 and -240, then Simple Choker -1 to hide seams, all parented to a rotation null at the true centre
  of the triangle (not the bounding box). Pre-comp means one fix updates every copy. Free: Blender shape keys, Array of
 instances with an Empty parent. Check: verified [0:20, 3:05, 8:48, 14:00].

### 33. Mattes: shine sweep, shadow, clip to a base shape

- Shine sweep: a stroked rectangle (35 px) rotated to the reflection angle slides across the lenses over about 2 s with
  F9; clip it with Set Matte (Take Matte From Layer = the glasses, Alpha Channel; Continuously Rasterize on). Today use Track
  Matte. Impact shadow: a black shape parented to the ball with Set Matte from the ball so the shadow only shows on touch.
  Clip to a base shape: Preserve Underlying Transparency on layers above a base layer, Dissolve blend turns a gradient
  into dither grain. Hand-keyed Stencil Alpha masks cut out stop-motion objects (today Roto Brush 3).
- Free: Fusion: Merge with Stencil or Matte Control. Blender: Alpha Over with Set Alpha. Web: `mask-image`, `clip-path`, canvas `source-atop`.
- Check: verified [1gQB 03:21, 03:35, 10:50; 8dRr 4:33; htt 1:00; BcTi 04:35]

### 34. Gradients: beam and animated gradient bubble

- Gradient beam: a tall rectangle with a linear Gradient Fill and a feathered mask (Feather up to 700, then 500). Scale Y
  0 to 100 with the anchor at the bottom, a very severe ease-out then a long ease-in, opacity keyed separately. A base glow
  from layered ellipse masks, Feather 400, 200, 100, lighter layers starting later and ending sooner. Set the project to
  16 bits per channel to stop banding.
- Gradient bubble: Illustrator gradient mesh, black centre, avoid "gradient no man's land" hues; a blobby alpha matte with
  Turbulent Displace (Amount 50, Size 100, Evolution `time*250`, Feather 120) and two bubbles rotating in opposite directions;
  comp on Screen so black vanishes; loop with markers and a crossfade; Bulge Center parented to a null so a moving object
  distorts the gradient; three Glow passes (Threshold 87.1%, Radius 57, Intensity 1.3) and 5% Noise to hide banding.
- Free: CSS `linear-gradient` + `mask-image` + `transform-origin: bottom`; layered `radial-gradient` with `mix-blend-mode: screen`. Blender: Color Ramp on Gradient Texture; compositor Glare. Fusion: Gradient plus Fast Noise matte (untested).
- Check: verified [HTn_ 02:10, 03:20, 04:00, 07:00; J85x 01:15, 04:05, 06:10, 08:22, 09:36]; the mask feather values 700, 400, 200, 100 heard

### 35. Echo trail, radio waves and shards

- Echo trail worm: a circle on a figure-eight with `loopOut("cycle")`, Effect > Time > Echo (10 echoes, -0.033 s, Decay 1,
  Echo Operator Composite in Front), a copy without Echo recoloured as the head. A delayed copy behind a moving shape is a
  cheap trail. Free: canvas draws N past positions with falling alpha.
- Radio Waves starburst: a solid with Effect > Generate > Radio Waves, Wave Type Mask on a zig-zag star, Producer Point
  low, layer start moved before 0, Fade-out 0, long Lifespan, Stroke 5 (legacy built-in). Free: stepped SVG scale copies.
- Shard masks: pre-comp the object, duplicate per shard with a Mask 1 per piece (no gaps along shared edges, clockwise
  around the object), key Position from the impact point with even spacing and the impact ease of item 4. Free: CSS
 `clip-path: polygon` per shard; Blender Cell Fracture (add-on name in 5.2 untested).
  Check: verified [04:05, 05:55, 07:20].
- Spray paint and drips: Trim Paths on a round-capped wave stroke plus Roughen Edges (Scale 10, Border 75), a bigger blob
  layer, subtract masks, parented drips with Turbulent Displace; Multiply over a dark wall, Screen for pale paint. Source:
. Check: verified [1:03, 1:45, 6:55, 7:54, 8:35].
- Simple Choker rounds spiky edges: choke -8 then +8 (expand then contract), or a duplicate comp choked bigger and tinted as
  an outline. Free: SVG `feMorphology` dilate then erode; Fusion and Blender Erode/Dilate. Source:
.
  Check: verified [a7Ny 70s -4.40; _heC 375s -50].
- Luma-matte drip reveal: a drawn drip drives a reveal, a delayed copy erases it, leaving a travelling band. Free: Blender
 compositor subtract two masks. Check: heard.

## Character and rigging

### 36. Layer-per-part rig with parents and a null controller

- Makes: a character where every part moves on its own and only what changes is redrawn.
- AE: import the PSD or Illustrator file as a composition, colour-code, pick-whip parent (eyes and ears to the head, head to a
  null controller, hand to arm, neck to body, legs upper to lower). Design first: rigging after detail doubles the link work.
  Rebuild details as shape layers and animate their paths, which is more predictable than Puppet pins or mesh warps on raster.
  Lifting knee: Rectangle Path, Convert to Bezier Path, two points at the knee, key Path down then up, push the right edge
  back so the leg does not seem longer. Parent a decorative layer to the main layer with the pick whip to scale a stack from
  one key. Parallax, snow and loops: items 15 and 16.
- Free: Blender: Grease Pencil layers or an armature with Empty parents as controllers. Fusion: Transform chains (untested). Web: nested groups with `transform-origin`. For 3D rigs read the `rig-characters` skill.
- Check: verified [YrqT 01:25, 02:35; t6BX 10:30; 8dRr 2:45; atVK 04:48]; knee trick heard

### 37. Simple eye rig with nulls

- AE: eye white shape (pen), pupil circle. Set Matte on the pupil from the eye white so it cannot leave the eye. Null "Pupil
  Controller" parents both pupils (pupil Scale stays free for dilation); null "Eye White Controller" parents the whites and the
  pupil controller. A small nudge on the white controller makes the head seem to turn. Look-around: Position keys on the
  controller, F9, a hold, keys closer so pupils move fast, a severe ease, arcs on the motion path (item 7). Detail: darker lid
  duplicate, gradient iris below the pupil, dilation Scale only for dramatic close-ups, reflection stock layer on Screen with
  Set Matte from the eye white and Bulge (radius 337, Height 1.0) above Set Matte.
- Free: Blender: Grease Pencil or mesh with drivers, a bone per control (untested). Web/SVG: `clip-path` group for the white, CSS transform controller group for the pupil.
- Check: verified [4:50 pickwhip expression, 9:20 reflection stack, 10:10 three variants]; dilation values heard

### 38. Blinks: open slow, close fast

- AE: key Shape Path open, a few frames later close below halfway (top lid moves more), open again. Opening is about double
  the closing time. F9. Second eye: Alt-click the stopwatch on its Path and pick-whip to the first path
  (`content("Shape 1").content("Path 1").path`), or animate one eye, duplicate and flip the comp. Cut-out version: stepped
  opacity holds between Eyes - Closed and the open eyes (item 10), or a lid layer that drops with the extreme ease-in
  `cubic-bezier(0.97, 0.02, 0.98, 0.06)` for an uncanny, robotic blink after a long wait. Eyes alone give any object life;
  humour comes from sentience. See [acting-and-faces.md](acting-and-faces.md) for face swaps.
- Free: CSS or Remotion `scaleY` on the lid, or path morph with equal points; Blender shape key on the lid.
- Check: verified [XxnB 4:50 expression; yNPx 0:45 panel]; open-twice-as-long heard

### 39. Fake turn, mouth swaps and counter-rotation

- Fake head turn: Scale unlinked, X 100% to 89% (no 3D), front ears keyed in and out with opacity hold keys.
- Mouth: layers trimmed back to back (Smile, Closed, Open) on hold-like timing, or one mouth shape and a teeth shape with
  Set Matte so teeth show only inside the open mouth; open slightly with Path keys.
- Keep a child upright on a spinning parent: Rotation expression `thisComp.layer("Circle").transform.rotation * -1`
  (append `+ value` to add own keys). Blender: Copy Rotation constraint with Invert; Remotion: `rotate(-angle)` inside the parent.
- Check: heard (turn); verified [YrqT 02:35 Mouth Open - Teeth fx; Pmmv 01:08 expression text]

### 40. Puppet Pin, rigging plugins and Duik-free routes

- Puppet Pin: three pins on an elbow and the ends give a small arm sway; rotation with the anchor moved to the grip; pins on
  lips and hair; hand pinch via a pre-comp. Ben warns raster Puppet and mesh warps are limiting, so rebuild as shapes when
  precision matters. Still in AE 2025 under the Pin tool.
- Duik: free and open source (Duik Angela). Paid ideas only: Limber (39.99 USD, simple limb rig with a quick walk cycle),
  Joysticks 'n Sliders (39.95 USD), Rubber Hose (45 USD, bendy limbs). Duik-free routes: nulls as controllers with parenting
  (items 36, 37), Blender Rigify or Grease Pencil armatures, Spine or Rive for web (untested).
- Check: heard (names and prices); Puppet visible in the walk-cycle project frame

## Sources and licences

Krita, Pencil2D, Rough Animator (paid iPad app), Duik, EaseCopy (name-your-price). Paid and ideas only: AE itself, Flow, Motion,
Limber, Joysticks 'n Sliders, Rubber Hose, AnimDessin 2 (unsupported). His paid course "Master Motion Design" and the
Perfect Shape Morphs free preview are links for the user to open, not downloads. Project files behind an email form are
likewise links to open.

