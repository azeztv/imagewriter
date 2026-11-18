# Stylized animation, physics and jiggle recipes

Blender recipes for stylized character animation: stop-motion looks, key and graph habits, loops, secondary motion, NLA and
slotted actions, mocap retarget, procedural motion, and cheap physics (jiggle, cloth, ragdoll, particles). Checked against
Blender 5.2 where a route moved; values marked `verified` were read from a frame, `heard` ones were only spoken. An entry
tagged `(heard)` has no value seen on a frame. Generic stepped modifier, Make Cyclic, Copy and Paste Flipped, and basic NLA
are not repeated: see the end of the file.

<!-- skill-navigation:start -->
## Reading Map

- [Stylized animation, physics and jiggle recipes](#stylized-animation-physics-and-jiggle-recipes)
- [Stop-motion and stepped looks](#stop-motion-and-stepped-looks)
  - Clay fingerprint and boil jitter
  - Block in Constant, then splines, then Bezier
  - [Stop-motion and stepped looks](#stop-motion-and-stepped-looks): one-click stepped animation
- [Keys and the Graph Editor](#keys-and-the-graph-editor)
  - Keying sets and Only Active Keying Set
  - Handle shaping: ease, overshoot, rest
  - Ball bounce with squash and stretch
- [Cycles and loops](#cycles-and-loops)
  - Walk cycle polish
  - 16-frame box-character walk
  - Pivot flipper animation without a rig
  - Mograph Array twirl loop
  - Looping balls on curves
- [Secondary motion and acting](#secondary-motion-and-acting)
  - Offset keys for follow-through
  - Constant shape-key blink
  - Coffee wobble without a sim
  - Anime tear on a path
- [Actions, NLA and mocap](#actions-nla-and-mocap)
  - Slotted actions
  - NLA mixing: Hold Forward, influence, Combine
  - Mocap retarget with Rokoko
- [Audio and procedural motion](#audio-and-procedural-motion)
  - Shape key driven by audio
  - Procedural wind on instances
- [Physics and particles](#physics-and-particles)
  - Rigid-body spring jiggle
  - Box-proxy ragdoll
  - Jelly soft body with Cloth pressure
  - Vertex groups and vertex parents on cloth
  - Cable with Hook, Cloth and Skin
  - Wobbly ghost with a weighted Pin group
  - Cloth settings guide
  - Geometry Nodes cloth and tearing (experimental)
  - Hair dynamics trick
  - Floating dust particles
  - Particle explosion with random colours
- [Add-ons](#add-ons)
- [Already covered elsewhere](#already-covered-elsewhere)
<!-- skill-navigation:end -->

## Stop-motion and stepped looks

### Clay fingerprint and boil jitter

- **Clay surface that looks re-sculpted every two frames**: a fingerprint texture that shifts and a displacement that wobbles, on a stop-motion character.
- Steps:
  1. Shader Editor: Mapping node (Type Point, Scale 1.5 on all axes, verified) feeding the Fingerprint image texture. Hover Rotation Z, press `I` every 2 frames for 4 keys (0, 90, 180, 270 degrees, verified at 270).
  2. Displace modifier with a Clouds texture (Noise Basis Blender Original, Type Soft, Grayscale, Size 0.25, Depth 2, Nabla 0.03, verified). Key the Displace Strength (0.05, 0.10, 0.01, 0.075 over frames 1 to 8, verified) or the texture Size up and down the same way. Keep Strength low and limit it with a vertex group so eyes, mouth, ground and background stay still.
  3. Graph Editor: select all those keys, `T` > Constant. Then Modifiers tab in the `N` sidebar > Add Modifier > Cycles so it loops forever (the Cycles step was heard, not framed). Select the Mapping node so its curves show.
  4. Scene at 12 fps (or 24 fps with 2-frame holds).
- Principle: clay stop motion has no tweening and no motion blur; holding values for 2 frames while the print texture rotates reads as hand-touched.
- Other tools: in a shader, drive UV rotation and a noise seed from `floor(time * 12)`; three.js and Godot use the same time quantize. Untested.
- Pitfall: high Displace strength tears dense meshes; the Clouds texture is a legacy texture and was not run in 5.2.

### Block in Constant, then splines, then Bezier

- **Stepped blocking order**: the order he starts every rig animation, so timing is judged before easing hides it.
- Steps:
  1. Learn the controls first: `G`/`R` in Pose Mode, `Alt+R`, `Alt+G`, `Alt+S` reset rotation, location, scale.
  2. Layout: camera view on top, Dope Sheet and Timeline below. Animate only what the camera sees.
  3. Timeline > Keying > Active Keying Set = LocRot, then Auto Keying on (see the keying set entry).
  4. Block key poses big to small: head first, then eyelids and brows, with ears or other secondary parts lagging the head turn.
  5. Dope Sheet: `A`, `T` > Constant. Play the stepped blocking and fix timing by moving keys.
  6. Add in-betweens on arcs. If the stepped look is too sparse, undo Constant, walk backwards through the shot adding keys at the important points, set Constant again. There is no right key count.
  7. Dope Sheet: `A`, `T` > Bezier for everything, then shape handles (next entries).
- Principle: easing cannot hide a timing mistake in stepped view; everything moves in arcs and poses are held, not constantly moving.
- Other tools: for a stop-motion look keep the Constant result and animate at 24 fps so a jittery and a smooth version are one switch apart (12 fps is the traditional rate).
- Use when: any rig; loop a reference GIF for the blocking pass.

### Stop-Mo: one-click stepped animation

- **Stepped (on twos or fours) character animation with a free panel** over the built-in Stepped Interpolation modifier, camera stays smooth.
- Steps:
  1. Install the zip (Edit > Preferences > Add-ons > Install from disk). Panel "Stop-Mo" in the 3D View `N` sidebar. Select the rig.
  2. Add/Remove Modifiers: Apply Steps, Remove Steps, Select Objects, Toggle Preview. Controls: Step Amount 2.00, Frame Offset 0, Influence 1.00, Start Frame 0, End Frame 250 (verified; the 5.1 build also shows Target Filters: Object Level Transforms, Only Selected Bones, Only Shape Keys).
  3. By hand, no add-on: Graph Editor > select F-curves > Add F-Curve Modifier > Stepped Interpolation, Step Size 2.
  4. Reapply after changing any setting.
- Principle: real stop motion moves the puppet every second frame; key on even frames because a key on frame 3 is skipped by a step of 2. When the shot starts at frame 1, set Frame Offset 1 so keys land on even numbers.
- Other tools: three.js `t = Math.floor(t * 12) / 12` for the character mixer only; Unity Constant tangent, Godot Nearest track, Unreal Constant curve. Untested.
- Pitfall: Only Shape Keys + Remove Steps keeps corrective shape keys smooth. Head on ones with body on twos gives a jiggly look. Add-on is open code, author gives no long-term support; confirm it installs on 5.2 (unverified).

## Keys and the Graph Editor

### Keying sets and Only Active Keying Set

- **Keys only on the channels you animate**, so the Graph Editor stays readable.
- Steps:
  1. Record dot (Auto Keying) on in the Timeline. Open the Keying popover > Active Keying Set. Seen list: Available, BBone Shape, Delta Location/Rotation/Scale, Location, Rotation, Scale, Location & Rotation, Location & Scale, Location Rotation & Scale, Rotation & Scale.
  2. Open the arrow beside the record button and tick Only Active Keying Set. Without the tick, rotating a bone still keys all 9 channels (verified).
  3. Choices: Rotation for a single-property pose, Location & Scale for a bounce, LocRot for characters (keeps scale out of the Dope Sheet).
  4. Rig-aware walk set-up: in Pose Mode, `N` > Item, right-click Location and Rotation > Insert Keyframes on the foot IK bones, Rotation on both heels, Location and Rotation on the torso, Rotation on the hips, all at frame 1. Active Keying Set = Available, Only Active Keying Set on: now only channels that already hold a key get new keys (the Available choice was heard).
  5. One-off key: right-click a single field (for example Rotation X) > Insert Single Keyframe; plain Insert Keyframes keys all three axes.
  6. Rotate in Local orientation so one Euler channel changes.
- Principle: the set decides which channels may be keyed; the checkbox forces auto-key to obey it.
- Other tools: no keying sets in Unity, Unreal or Godot; add tracks only for what moves.
- Pitfall: set it before posing; fix a stray key by box-selecting the frame in the Timeline and `G`. The Keying popover and the auto-key options were reorganised in 4.2 and later, so look by name (5.2 layout unchecked). Auto Keying menu moves are inferred.

### Handle shaping: ease, overshoot, rest

- **Soft, weighted motion from blocked poses**, in the Graph Editor.
- Steps:
  1. Header: Only Show Selected on (arrow-cursor icon), so one control's curves show. `Shift+H` isolates a channel, `Alt+H` brings the rest back, `Period` (or View > Frame Selected) frames the selection. Delete channels a control does not use (`X` on Location curves of a rotate-only bone). Flat curves mean no animation.
  2. Interpolation `T`: Bezier (default), Linear (robotic), Constant (hold). Handle type `V`: Automatic moves both handles together; Free lets each handle move alone. For a hard impact switch the landing key to Free (or Vector) and pull the handles down so the value stops dead instead of easing through the floor (verified on the chicken bounce).
  3. Click the centre of a key to select both handles; `G`, `R`, `S` move them together. `S` then `X` stretches handles horizontally for a longer ease and a built-in pause.
  4. Overshoot: drag the key and handle past the target, then put a key back at the value. Rest: `Shift+D` a key and move it on X, or scale its handles wide. Delete keys that do not change the curve.
  5. Pivot menu (Graph Editor header) = Individual Centers so scaling keys scales each one, not the group.
  6. Dope Sheet > Key > Clean Keyframes removes redundant keys.
- Principle: a body winds up slowly, snaps, then settles; linear is robotic, default Bezier is sluggish, so hand-shape the handles. Robot or mechanical parts use Linear on purpose (verified on a mech Body curve, frames 1 to 30).
- Pitfall: do the big mover (head turn) first and time-lapse the rest; beginners keep everything moving and forget rests. No overshoot numbers were given.
- Other tools: Unity and Godot have the same tangent modes; three.js `InterpolateLinear` versus smooth for mech parts. Untested.

### Ball bounce with squash and stretch

- **Looping 28-frame bounce, blocked then eased**: the first full animation exercise.
- Steps:
  1. Keying set Location & Scale, Auto Key on, Only Active Keying Set on. Keys at frames 1, 14, 28 (`I`); at 28 move the ball up on Z. Select all, `Shift+D`, drag the copy to cover frame 1 so it loops. Start 1, End 28.
  2. Frame 14 (contact): Scale tool, squash Z down, widen X and Y from the top view to keep volume (Resize panel X 1.442, Y 1, Z 1 seen). `Alt+S` clears scale at frames 8 and 20 so the squash does not carry over. Frame 8: stretch Z up; copy that key to frame 20 with `Shift+D`.
  3. Graph Editor: delete X and Y Location curves, keep Z. Pivot = Individual Centers. Select the top-of-arc keys, `S` `X` to widen them so the ball hangs; tighten the bottom key so it snaps into the ground by about frame 10: hit, hold, pop up fast, hang, fall slowly.
  4. Z scale curve: select both handles at the contact key, Key > Handle Type > Vector so the sides move independently, then pull. Rotate and scale X/Y handles with `R` and `S` until the three scale curves agree. Final check in Front view.
- Principle: block extremes first, pose squash and stretch second, spend time on speed in the Graph Editor; squash trades height for width.
- Other tools: the same is an AnimationCurve in Unity or Godot Bezier tracks plus a scale track. Untested.
- Pitfall: never squash only Z; check the top view.

## Cycles and loops

### Walk cycle polish

- **Hip roll, key cleanup, toe fix and torso hang on a four-pose walk**: small steps that make a cycle read as walking.
- Steps:
  1. Hips: Graph Editor, Only Show Selected, hips selected, Local orientation, rotate on the green circle (Y Euler Rotation); `Shift+H` all other channels (verified, frame 11:40). Keep hips at 0 on contact frames and rotate toward the weight-bearing leg on each Pass pose. Delete unused keys.
  2. Dope Sheet > Key > Clean Keyframes.
  3. Toes dipping through the floor: key the toe IK control, rotate it up at the dip, `Alt+R` it on the next frame.
  4. Torso: animate only Z Location; delete the X and Y curves and the middle key of each bounce. Select all torso keys, Pivot = Individual Centers, `S` to scale handles out for more hang time (cartoony bounce; Z seen at 0.17089 m).
  5. Loop close: paste frame 1 with plain Paste Pose on the closing frame and set scene End one frame earlier so there is no double frame.
- Principle: fewer keys with shaped handles are easier to edit and read as intent.
- Pitfall: big cartoon feet clip the floor; toe control keys fix it.

### 16-frame box-character walk

- **Looping walk with weight shift, head wobble, flap lag and squash on an IK rig**, keyed with Insert All.
- Steps:
  1. Put a walk reference (the Animator's Survival Kit walk) in an Image Editor, flip it horizontally, animate from the Right view (numpad 3). Frame Start 0, End 16, 24 fps.
  2. Pose Mode, `A`, `I` > Location, Rotation & Scale at frame 0: one foot forward and one back, arms opposite. Frame 8: swap feet and arms, key. Select the frame-0 keys, `Shift+D`, drag to frame 16, then set End to 15 so the repeated pose is not played twice.
  3. Hips up between contacts (frames 4 and 12), legs bend through. Front view: hip rotates onto the weight-bearing foot at 0, other side at 8. Head bone matches the hip. Flaps tuck in at 4, down at 12.
  4. Dope Sheet: offset flap, neck/hip and hand keys by 1 to 2 frames (hands 2) for follow-through. Root Z scale slightly below 1 on the down frames for squish; exaggerate by scaling those keys in the Graph Editor with Pivot = Individual Centers.
  5. Graph Editor with Only Show Selected off, `A`, `Shift+E` > Make Cyclic (adds a Cycles modifier to every curve), then set End back to 16 to remove the pause at the loop point.
- Principle: five poses (contact, down, passing, up, contact), channel offsets give overlap, the cyclic modifier makes the loop endless.
- Other tools: key the same five poses in an engine clip, set it to loop, offset secondary bones by 1 to 2 frames. Untested.
- Pitfall: with auto-key off the head bone gets only 3 keys; a duplicated end frame stutters unless End is 15.

### Pivot flipper animation without a rig

- **Swimming creature from nested rotations**: a manatee circles and flaps its fins with no armature.
- Steps:
  1. Fin origins at the joint (tip), fins parented to the body. Empty at scene centre, body parented to it (Keep Transform).
  2. Key Empty Y rotation 0 at frame 1 and 360 at last frame + 1 so the loop does not hold. Key the body's own Y rotation the same way, slightly out of sync.
  3. Right-click a single field > Insert Single Keyframe, then `Shift+E` > Make Cyclic. Fins: key X rotation in and out, Make Cyclic, shift timing per fin.
  4. Second creature: duplicate it with its Empty and shift the Empty's keys to sit opposite.
- Principle: nested rotations (orbit Empty plus own spin) replace a rig; origin placement is the joint.
- Other tools: Group > mesh with offset pivot in three.js and any engine; loop the clip. Untested.
- Pitfall: a Mirror modifier on a fin only works if the fin origin is not moved off the body origin; set the body as the mirror object. (heard)

### Mograph Array twirl loop

- **Five cards that twirl, hold and spin once, from two keyed curves.**
- Steps:
  1. Cube, add the Mograph Array modifier (free add-on). Mode Line, Count 5, Distance Type Relative, Y 1.25, X 0, Rotation Style Increment (not Constant).
  2. Timeline 1 to 170 at 24 fps. Rotation Y: 0 at frame 1, -16 at 48, the same at 96 (hold), 0 at the end; rotate the first and last handles slightly for overshoot and scale handles up with Individual Centers so it starts soft and snaps in.
  3. Object Y rotation: key near frame 60, -10 degrees at 96 for anticipation, 360 near 144, one more at the end, one key pulled up for overshoot.
  4. Card: cube thin in Y and tall in Z, `Ctrl+B` on 4 edges, Bevel modifier 0.5 with 2 segments, Subdivision Surface. Instance Object > Object for one card, Collection for a set (then switch Distance off Relative and use Offset X 1 m, or Length). Array Type Iterate walks the set, Random picks by Seed.
  5. Background plane: Mapping > Separate XYZ > Z into Gradient Vector, Color Ramp into Base Color (avoids Node Wrangler guessing).
- Principle: key one transform on the base and let the array offset each copy; the whole animation is two curves.
- Other tools: rotation = base * index with one tween in three.js, Unity or Godot. Untested.
- Pitfall: with Collection mode the animation breaks until Distance is no longer Relative.

### Looping balls on curves

- **Perfect loop of balls travelling on curves through tubes**, closing exactly at frame 240.
- Steps:
  1. Bezier curve, Control Points > Set Handle Type Automatic; snapping on, build a 10 m sine-like curve (extrude 1 m with `E`, rotate 180 and -180 alternately, 10 times, Y scale 0.5 applied). Quad sphere radius 0.25 with a `Ctrl+B` seam.
  2. MoGraph Array modifier: Array Mode Curve, Curve Instance Mode Count, Count 10 (ten balls on a ten metre curve), Primary axis Y, secondary X, rotate 90. Scale 0.95 stops sphere intersection. Curve resolution 64.
  3. Scene end 239 (keys at 0 and 240). Sphere X rotation 0 to -1080 and MoGraph Offset 0 to 3, select all keys, `T` Linear, and `Shift+E` > Linear Extrapolation.
  4. Second curve: duplicate, rotate -180, offset 1 m; slide one ball's graph so balls sit on opposite sides. Camera: X 2 m at frame 0 to 6 m at 240 linear, Orthographic Scale 3.5.
  5. Tubes: Circle curve radius 0.25, cyclic off, delete the left point, rotate top and bottom points 45 and -45 for a half circle, use as Bevel Object (Geometry > Bevel > Object). Tilt 45 on the lower control points so the tube cups the ball. Join tubes (`Ctrl+J`), Solidify 0.05 m, Offset -1, Even Thickness on, then Bevel modifier; a second Solidify material slot index offsets the edge colour. Lift one curve 0.5 m on Z at one end for over and under crossings.
- Principle: whole-metre sizes and a count equal to the curve length make the offset loop exactly; linear interpolation and extrapolation avoid slowdown.
- Other tools: loop logic `(offset + i / count) mod length` ports to Unity, Godot or three.js code; the tube is a swept profile. Untested.

## Secondary motion and acting

### Offset keys for follow-through

- **Parts that follow the main mass lag 1 frame**: head and antenna land together, then the antenna keys move 1 frame later.
- Steps:
  1. Pose Mode, Auto Keying on. Block the bounce: head down at frame 1, `Alt+G` at 12 so it lands in the default pose, squash the antenna and head a little on landing, stretch at 16, `Alt+G`; move frame 16 keys to 20 with the Summary key and stretch out.
  2. Antenna keys: down on 12, up on 16 and stretched more. Keep all keys aligned while animating, offset at the end.
  3. Dope Sheet: select the antenna keys, `G` -1 or 1 frame (2 frames was too much at 24 fps).
  4. Graph Editor: `A`, `Period`, Pivot = Individual Centers, `S` `X` to scale slightly outward for more snap and ease in the middle.
- Principle: parts attached to a mass lag by 1 or 2 frames (overlap).
- Other tools: the same offset works in Unity Timeline, Unreal Sequencer or After Effects keyframes.

### Constant shape-key blink

- **Snappy stylized blink from two keys.**
- Steps: select the Eye object, Object Data > Shape Keys, key "Open" at 0 on frame 0 then 1 a couple of frames later. Graph Editor: select the keys, `T` > Constant.
- Principle: Constant pops from open to closed like a drawn blink.
- Pitfall: not made for slow-motion blinks. The Constant step was heard, not framed.

### Coffee wobble without a sim

- **Liquid surface that moves with the mug**, no fluid simulation.
- Steps:
  1. Coffee is a Circle mesh with Grid Fill. Two or three rotation keys on the disc tilt it toward and away from the camera, Auto Keying on.
  2. Subdivision, then a Displace modifier with very low Strength, Texture Clouds (Noise Basis Blender Original, Type Soft, Size 1.00, Depth 15, Nabla 0.03, verified).
  3. Key the texture Size, then in the Graph Editor add a Noise modifier on the Size channel (Blend Replace, Scale 10, Strength 2, Offset 0, Phase 1, Depth 0, verified).
- Principle: a jittering displacement on a tilting disc reads as liquid.
- Other tools: animate UV noise offset on the surface in a shader. Untested.
- Pitfall: the Clouds legacy texture was not run in 5.2 (inferred to exist).

### Anime tear on a path

- **Droplet that stays on any surface and rolls down a drawn path**, no fluid sim.
- Steps:
  1. `Shift+right-click` puts the 3D cursor on the face; add a tiny Cube there. Shrinkwrap modifier: Wrap Method Nearest Surface Point, Target the character, Snap Mode Outside Surface (use Outside if it fails), then Subdivision Surface and Shade Smooth: the cube becomes a drop.
  2. Shrinkwrap alone jitters when moved. Add > Curve > Bezier, delete its points, use the Draw tool with Surface as target and trace the route off the chin; pull the last handles off the surface in front view.
  3. Tear: Object Constraints > Follow Path, Target the curve, Forward Y, Up Z, Fixed Position on, Curve Radius and Follow Curve off (verified). It jumps to the world origin offset: zero its Location (alt-drag on X, Y, Z).
  4. Animate Offset Factor 0 to 1: slow roll then faster drop; scale handles in the Graph Editor and rotate the last key for a linear fall so it does not ease out.
  5. Scale keys: 0 at start, 1 by about frame 12, 0.5/0.5/0.2 two frames after the fall starts for a stretch. Noise F-curve modifier on each scale curve (higher scale, lower strength), copy the modifier to the others for the wobble (values heard).
- Principle: Shrinkwrap puts the object on the surface; a path you control gives timing.
- Other tools: three.js `CatmullRomCurve3.getPointAt(t)` plus a raycast, Unity spline or DOTween, Godot PathFollow3D `progress_ratio`. Untested.

## Actions, NLA and mocap

### Slotted actions

- **One Action for a whole character** (Blender 4.4+; in 5.2 actions are always slotted, so there is nothing to enable).
- Steps:
  1. Action Editor: the slot selector sits next to the action name; the NLA shows the slot under the action. Slots also appear in Object, Material and Data properties > Animation.
  2. Create one action "character" with slot "body" (key with auto-key). Select the head, switch the Action Editor to "character", New Slot "head", keyframe. No new actions appear.
  3. Shader key (a face-plane image-sequence offset): Material properties > Animation, pick "character", New, slot "facial animation", right-click > Insert Keyframe.
  4. Camera: keying location creates "camera action" with slot camera; keying focal length 50 to 100 mm adds slot "lens" automatically. For a parent empty choose the same action in Object properties > Animation, New slot "cam control", `K` for location and rotation.
- Principle: slots separate the animated data-blocks inside one action, so objects share one clip and the NLA stays clean (old files show a pile like CubeAction, TextureAction, ShaderNodetreeAction with "Legacy Slot" on each).
- Other tools: Unity clips with several targets and Unreal Sequencer tracks.
- Pitfall: same-object properties slot automatically; shader keys and mixed object types need manual slots. NLA Active Strip panel shows Action and Slot fields.

### NLA mixing: Hold Forward, influence, Combine

- **Idle that fades into a wave over 15 frames, and layers on top.**
- Steps:
  1. Strip fields: strip Frame Start and End only place and trim; Action Clip Frame Start and End choose which source frames play (start 50 skips 50). Playback Scale is the recommended speed control (2 is twice as slow). Repeat repeats the clip; Sync Length on by default. `Tab` into a strip to edit it; avoid the Dope Sheet Action Editor, which makes a stray strip.
  2. Idle on its own track, `Shift+A` add Wave on a new track. The top clip hides the lower one, so Extrapolation = Hold Forward (Blending Replace, Blend In/Out 0, Auto Blend off).
  3. Do not use Blend In/Out or Auto Blend. Check Animated Influence: influence 0 keyed at frame 50, 1 at 65, so the wave fades in over 15 frames; change easing from linear in the Graph Editor.
  4. Replace only overrides channels that clip has keys for: a rotation clip with no location keys lets a bobbing location clip show through. Insert a Z location key in it (strip, `Tab`, `I`, `Tab`) to stop the bob, or use Combine.
  5. Layer on top: Action Editor with the armature selected, New action "look up", key the head bone, Push Down in the NLA, Blending = Combine, `Tab` and add head motion.
- Principle: a keyframed influence is an ordinary curve, so you control transition shape and length; a clip only overrides the channels it keys.
- Other tools: keyframed blend weight on a Unity Animator layer or Godot AnimationTree blend.
- Pitfall: extrapolation Nothing shows the lower track until the next clip and then jumps; Hold also holds before. A walk cycle with no head keys lets the head follow whatever is under it. Add, Subtract and Multiply are rarely useful. 4.4 panels; 5.2 layout unchecked.

### Mocap retarget with Rokoko

- **Video or webcam mocap onto a stylized rig**, free capture plus the free retarget add-on.
- Steps:
  1. Capture on a tripod, full body in frame, no dark clothes, no long occlusions. Processing is about 3:1 (30 s takes about 90 s). In Rokoko Studio check the foot-lock bars so foot sliding is removed at the source.
  2. Export tab: FBX, Skeleton target Newton, naming Mixamo, Reference pose T-Pose, FBX Binary, FBX201600, Framerate 100, Include reference pose on, Use constant key reducer on (verified).
  3. Import the FBX. Rokoko add-on panel: Source = the mocap armature, Target = your rig. Build Bone List (bone map such as LeftHandRing1 to mixamorig:LeftHandRing1; blank rows are fine), tick Auto Scale (untick if the character flies around), Use Pose: Current, Retarget Animation. Live streaming: Rokoko Studio Live, port 14043, scene scale 1.0, Start Receiver.
  4. Fix leftovers (knees through ground) with a Combine NLA layer that raises the hip bone.
  5. Auto-Rig Pro Remap (paid) does the same: Source mixamorig:Reference, Target rig, Build Bones List, Re-Target.
- Principle: map names once, bake the retargeted clip, clean up in layers.
- Other tools: Unity Humanoid retarget, Unreal 5 IK Retargeter, both import the same FBX.
- Pitfall: the Studio is beta and the add-on was not checked on 5.2 (Blender 3.4 and 4.3 frames). Sponsored video.

## Audio and procedural motion

### Shape key driven by audio

- **Beats open an egg**: music drives a shape key, no hand keying.
- Steps:
  1. Model the egg and chick, join with the egg second (active). Mesh data > Shape Keys: Basis plus "Open"; in edit mode lift the shell and chick parts so the chick shows. Shell: Solidify Thickness 0.01 m, Offset -1, Fill Rim on.
  2. Armature with one bone "Driver". Right-click the Open key's Value > Add Driver: Scripted Expression `var`, variable type Single Property or Transform Channel on the Armature, Bone Driver, Z Location (World Space).
  3. Pose mode `I` for location, delete the other channels so only the driven axis stays. Graph Editor: Channel > Sound to Samples (Key > Bake Sound to F-Curves before 4.1), Lowest 20, Highest 200, Attack 0.005, Release 0.200, Threshold 0 (verified), pick the music file.
  4. Pose Context > Bake Action (`F3` "bake action"): Only Selected Bones off, Bake Data Pose, Start 1 to the end of the song. Delete every channel except the driver location and scale the curve in Y until it peaks at 1 (the baked curve peaked near 0.5).
  5. Audio only plays if added in the Video Sequencer (Add > Sound, same file, start 1).
  6. Wave: each ring is a parented Empty (Row.000 to Row.004), keys offset 2 to 4 frames per row; duplicate the driver bone per row and offset its keys.
- Principle: the bone location is the single driver value; baked sound is an editable curve and the driver maps it to 0 to 1.
- Other tools: three.js `morphTargetInfluences` from an AnalyserNode band, Godot spectrum analyzer into a blend shape, Unity `GetSpectrumData` into a blend shape weight. Untested.
- Pitfall: the 2.80 frames use Auto Smooth, removed in 4.1 (use Shade Auto Smooth or Smooth by Angle). Bake Sound to F-Curves is now Channel > Sound to Samples in the Graph Editor (`graph.sound_to_samples`, seen in 5.3).

### Procedural wind on instances

- **Grass or feathers that sway forever**, in Geometry Nodes, no keys (Blender 5.2 frames).
- Steps:
  1. After Instance on Points add Rotate Instances.
  2. Scene Time Frame > Math Divide by 125 (feathers 350) > Combine XYZ X; add that vector to Position (Vector Math Add) > Noise Texture (3D, fBM, Normalize on, Scale 5, Detail 2, Roughness 0.5, Lacunarity 2, Distortion 0) Vector.
  3. Noise Color > Vector Math Subtract with a vector of 0.5 (Math Add 0.0 + 0.5) to centre on zero > Rotate Instances Rotation (Local Space on).
  4. Expose the Divide value as group input "Animation Speed" and wrap Rotate Instances in a Switch (Geometry) with a Boolean "Animation Toggle".
- Principle: noise sampled at position plus time on X drifts smoothly across the field; subtracting 0.5 makes instances lean both ways.
- Other tools: vertex shader rotating instances by simplex noise(position + time) in three.js or Crucible, Unity or Unreal shader graph with a Time node. Untested.
- Pitfall: a bigger divisor is calmer. Pin and rename the modifier so the node group matches the stack.

## Physics and particles

### Rigid-body spring jiggle

- **Bones that jiggle by following cheap rigid bodies**: banana, tail, hair chunk or backpack.
- Steps:
  1. Two cubes scaled to the Start and End bone, `Ctrl+A` Apply Rotation & Scale. Object > Rigid Body > Add Active on both. On the fixed end set Type Active, tick Animated, keyframe it so it stays put.
  2. Select both, Object > Rigid Body > Connect (Type Fixed, Location Center, Pattern Selected to Active), then set Type Generic Spring and name it Spring.
  3. Spring empty, Physics > Rigid Body Constraint: Type Generic Spring, untick Disable Collisions, Springs Type Blender 2.8, tick X Angle and Z Angle. Defaults Stiffness 10, Damping 0.5; he raises to Stiffness 100 and Damping 1 (heard).
  4. Connect again with Type Point so the two joint at a point. Move the fixed cube with keys (not too fast) and press play.
  5. Pose Mode: Child Of constraint on the Start and End bones, Target = the matching cube. Put cubes in a "Rigid Body" collection and constraints in "Constraints"; hide cubes from render.
- Principle: the cubes carry the physics (cheap convex hulls), the Child Of constraints pass motion to the bones; the animator moves only the main body.
- Other tools: spring joints or Verlet bones in Unity, Unreal, Godot; a Verlet or spring solver driving bones in three.js. Principle only.
- Pitfall: fast animator motion breaks the sim, raise substeps if it must be fast. Bone Dynamics Pro (paid) does it with bones directly.

### Box-proxy ragdoll

- **Crash-test dummy collapse that runs on a weak machine.**
- Steps:
  1. Build box proxies: arms and legs in three parts each, plus body and head; Mirror modifier needs `Ctrl+A` > Location applied. Join (`Ctrl+J`), Subdivision Simple apply, then Catmull-Clark level 1 (Viewport 1, Render 2). Leave gaps because the collision margin is 0.04 m.
  2. Tab, `A`, `P` > By Loose Parts, `M` > New Collection "rigid". Plane: Add Passive. All boxes: Add Active. `F3` "origin to geometry" for all boxes or they spray out.
  3. Select neighbour pairs, Object > Rigid Body > Connect: Type Point, Location Center, Pattern Selected to Active (verified). One Empty per link; `M` > New Collection "constraints".
  4. Select all Empties, tick Disable Collisions in Physics, hold `Alt` and press Enter to apply it to every selected one (verified, 15 constraints).
- Principle: connect neighbours only; disabling collisions between linked bodies stops them fighting.
- Other tools: Godot RigidBody3D + PinJoint3D, Unity Rigidbody + CharacterJoint, Unreal Physics Asset: same proxy plus joint model.
- Pitfall: every Connect makes an Empty, so a big rig is tedious. Raise collision margin only on strong machines. 3.4 frames; operators unchanged in 5.2 (inferred).

### Jelly soft body with Cloth pressure

- **Character that squashes and wobbles on landing**, fast in the viewport.
- Steps:
  1. Add Mesh > Round Cube (Extra Objects, Quad Sphere preset). Plane underneath with Physics > Collision. Blob: Physics > Cloth, Shade Smooth.
  2. Stack: Cloth first, then Subdivision Surface (low-res sim, subdivision only smooths).
  3. Cloth: Quality Steps 5, Speed 1, Vertex Mass 0.3 kg, Air Viscosity 1, Bending Model Angular. Stiffness Tension 1, Compression 1, Shear 5, Bending 2 (defaults he started from: 15, 15, 5, 0.5). Damping 5, 5, 5, 0.5.
  4. Pressure on: Pressure 1, Pressure Scale 2, Fluid Density 0.1, Target Volume 0 (Custom Volume off). All verified.
  5. Cache tab > Bake All Dynamics to replay fast.
- Principle: tension, compression and shear springs hold shape, lowering them collapses it like jelly; pressure acts like air in a balloon so sides do not cave in. Bending at 50 jitters.
- Pitfall: change one value at a time; numbers depend on mesh size and scene scale. Tab into Edit Mode snaps back to the frame-1 shape, reshape at frame 1. Quality Steps 3 to 4 is enough for blobs; raise only for capes. No direct engine match (Unity and Unreal cloth lacks internal pressure).

### Vertex groups and vertex parents on cloth

- **Only part of the mesh balloons or stays stiff, and an eye follows the wobble.**
- Steps:
  1. Object Data > Vertex Groups, add "Balloon", Edit Mode select, click Assign (assign after picking the group). Physics > Cloth > Pressure > Vertex Group = Balloon (verified).
  2. Cloth > Property Weights has Structural, Shear, Bending and Shrinking Group fields with Max Tension 15, Max Compression 15, Max Shearing 5, Max Bending 50. For antennas: select their verts, `Ctrl+Numpad Plus` to grow one or two rings, group "Antenna", put it in the Structural, Shear and Bending slots to stiffen them.
  3. Cloth > Collisions > Self Collisions on, or protrusions fold into the body.
  4. Vertex Parent: at frame 1 place the eyeball, select eyeball then soft mesh, Tab, pick one vertex, `Ctrl+P` > Make Vertex Parent (heard).
- Principle: per-vertex weights scale the spring values; a vertex parent follows the deformed mesh, not the object origin.

### Cable with Hook, Cloth and Skin

- **Hanging cable on a rigged mech back.**
- Steps:
  1. Plane, Edit Mode, select all, Merge > At Center. Extrude out and back up. Subdivide with 12 cuts. First and last vertex into vertex group "Pin".
  2. Select one end vertex, `F3` "Hook to New Object" (gives an Empty); the same for the other end; name them Start and End.
  3. Physics > Cloth; Shape > Pin Group = Pin (Pin Stiffness 1). Stack order: Hook, Hook, Cloth, Skin, Subdivision (Catmull-Clark, Viewport 1, Render 1). Skin gives thickness (Edit Mode, select all, `Ctrl+A` to set radius). Collision Quality 2, Object Collisions Distance 0.015 m (verified).
  4. Parent: Start empty, then armature, Pose Mode, head bone, `Ctrl+P` > Bone; the other Empty to the body bone.
- Principle: hooks drive the pinned ends, cloth swings the middle. Cloth only collides on faces, so a pure edge cable passes through the mech; giving it faces collides but lags badly.
- Other tools: a Verlet rope in three.js or Godot (not shown in the video).
- Pitfall: do not scrub live; key the body bone and play from frame 1.

### Wobbly ghost with a weighted Pin group

- **Top held, bottom swings and lags behind the controller.**
- Steps:
  1. Physics > Cloth with Cloth above Subdivision in the stack. Vertex group `Pin`: top half Weight 1, next rows 0.5, lower rows 0.25 (Assign each; optional Blur in the weight tools). Cloth > Shape > Pin Group = Pin.
  2. Stiffness Tension 25, Compression 25, Shear 10, Bending 10 (Tension and Compression verified; Shear and Bending heard). Start from Mass 0.3 kg, Quality Steps 5, Angular.
  3. Keyframe the control curve with spaced-out keys (a ghost never snaps side to side), re-cache after changing keys or frame range.
- Principle: a graded pin weight makes soft-body jiggle: 1 stays rigid, lower values move more.
- Other tools: Unity Cloth max-distance paint, Unreal Chaos Cloth max distance, Godot SoftBody3D pinned points, three.js Verlet cloth with pinned top. Untested.
- Pitfall: cloth under Subsurf is very slow.

### Cloth settings guide

- **Reference for the Cloth panel**: presets, springs, pressure, pin, sewing, collisions, cache.
- Steps:
  1. Physics > Cloth; colliders need Physics > Collision. Blender simulates from the first frame, so go back to frame 1 after any change. Presets: Cotton default, Rubber for stretchy and heavy.
  2. Springs: Tension resists stretch, Compression resists collapse, Shear is diagonal, Bending is folding. Low shear and compression is light cloth. Change values by 5 to 10. Damping (5, 5, 5, 0.5 seen) reduces jitter; raise tension damping if edges bounce. Quality Steps 5 default (max 64): raise only for glitches.
  3. Fast stack on a weak PC: Subdivision (Simple, Viewport 1, Render 2) above Cloth so the sim uses the extra vertices, then Cloth, then Solidify, then a second smooth Subdivision last, which Cloth does not compute.
  4. Solidify: Offset positive (0.4229, Thickness 0.01 m seen), Even Thickness off (spikes), Rim Fill on.
  5. Internal Springs: tick for jelly behaviour; Max Spring Creation Length 0 (auto), Max Creation Diversion 45 degrees, tension and compression 15, optional vertex group.
  6. Pressure: 0 with Custom Volume off is automatic; he often enters 50 (verified 50.000). Custom Volume with Target Volume 3 to 5 for a roughly 2 m object. Pressure Scale 300 with Fluid Density 1 looks water-filled. Negative pressure shrink-wraps a cube onto a banana (value heard, unverified). Field Weights Gravity 0 for balloons.
  7. Cache: Simulation Start can be negative (-60) so the sim starts settled, End 120; Disk Cache; Calculate to Frame; Bake (selected), Bake All Dynamics, Delete All Bakes. Re-bake after any change.
  8. Shape: Pin Group (flag, scarf); Sewing with Max Sewing Force and Shrinking Factor (-0.2 seen on a shirt): cut a pattern plane, extrude to the back, delete middle faces (leave edges).
  9. Collisions: Quality about 8 (max 20), Distance default 0.001 (change only if clipping), Impulse Clamping reduces jitter. Self Collisions friction 5, 0 for silk. On the collider: Damping 0.1, Thickness Outer 0.02, Inner 0.2, Friction 0, Single Sided on (off for containers).
- Principle: cloth is a spring mesh; density gives finer wrinkles but costs speed.
- Other tools: Unity Cloth component, Unreal Chaos Cloth; Godot has no cloth; for web bake from Blender into a vertex animation or shape-key cache.
- Pitfall: forgot frame 1, collision off, Distance too high. Blender 4.4.1 panels; 5.2 the same as far as heard.

### Geometry Nodes cloth and tearing (experimental)

- **Cloth as a node, plus a shell that peels off any object** (Blender 5.2 alpha, so values drift).
- Steps:
  1. Preferences > Experimental on. Geometry Nodes modifier, Cloth Dynamics (Experimental) node between Group Input and Output. Inputs: Pin Group (expose on the group input and assign a vertex group), Invert Pin Group, Stretchiness and Bendiness (0 to 1; 0.25 for realistic cloth; Stretchiness 1 falls as if nothing holds it), Solver Sub-steps and Constraint steps (20 and 5 recommended, 1 and 1 is visibly poor), Mass, Friction, Collision Radius, Linear Damping (50 gives gooey soft body), Gravity, Tearing (threshold 1.05 holds, 1 tears at once; Voronoi noise zones), Effectors (Custom Force and Geometry Collider; plug a collection of instances into the collider). Defaults 0 for Stretchiness and Bendiness verified.
  2. Peeling shell (object of about 50,000 faces): Set Position with Normal scaled by Vector Math Scale (0.027) to inflate a shell; Set Material (outer); Simulation zone with Transform Geometry Scale 0.9995; Boolean into Simulation Skip keyed off at frame 0 and on near 12 so it shrinks for a few frames only.
  3. Original object into a Geometry Collider (Deforming on, Object Space set to the object). Cloth Dynamics on the shell: no pin, Stretchiness and Bendiness 0.05 to 0.15, sub-steps 10, constraint 1 (raise to 20 and 5 if it fails), Mass 0.25, Friction 1.5, Gravity Z 0 and X 1 m/s for a sideways peel, Tearing on, Voronoi, threshold 1.05, scale 50.
  4. Wind: Custom Force (Field, World Space) from Scene Time (seconds) times 5 into a 4D Noise Texture (fBM, Normalize) into Map Range (To Min -1.5, Clamp) into Vector Rotate (Axis 0.5, 0.9, 1.0, Vector X animated 5 to 1.5). Inside material through a second Set Material, Join Geometry, Bake node at the end.
- Principle: the sim is a normal node, so selections, fields and collections drive it; shrink the shell until the collider blocks it, then pull with force so it tears.
- Other tools: the model is Houdini Vellum; the wind pattern ports to any particle force.
- Pitfall: alpha build, tearing threshold is fragile, tune friction, scale and threshold per object. Wind setup credited to another creator (gated files).

### Hair dynamics trick

- **Node hair that reads as dynamic** (heard).
- Steps: on the character add a legacy particle system (hair, a kink, interpolated children) and turn on Hair Dynamics. A few long moving strands make viewers read the whole Geometry Nodes coat as dynamic.
- Principle: node hair follows the surface with no dynamics, so a handful of simulated hairs sells the secondary motion.
- Pitfall: legacy particle hair assumed to still exist in 5.2 (not run).

### Floating dust particles

- **Slow drifting debris volume that adds depth**, rendered as tiny specks.
- Steps:
  1. Cube "Dust Box", S 4 to enlarge. Particles tab > New. Emission: Number 1000 then 500, Frame Start -100, End 0 (so it is full at frame 1), Lifetime 5000. Source > Emit From Volume.
  2. Physics (Newtonian): Brownian 25, Damp 0.05, Drag 0, Field Weights Gravity 0, normal and object velocity 0, Integration Time Step about 0.005 (all verified except the time step).
  3. Ico Sphere (Subdivisions 1) "Dust Particle", own collection hidden in viewport and render. Render As Object, pick it; untick Show Emitter in Render and Viewport Display; Scale about 0.01.
  4. Dust Box Object > Visibility > Ray Visibility: leave only Camera. Turn off the world for general lighting, camera with depth of field.
- Principle: Brownian gives wobble, damping and a tiny step make it slow float; a negative start frame pre-fills the volume; camera-only rays stop shadows and cut render time.
- Other tools: three.js Points or InstancedMesh with a small random walk and drag; Unity VFX Graph or Godot GPUParticles3D box emitter with zero gravity. Untested.

### Particle explosion with random colours

- **A sphere bursts into hundreds of random bricks**, each with its own colour (Blender 4.1).
- Steps:
  1. UV Sphere "Emitter"; brick objects in a collection "Particles". Particles tab > New: Number 1000, Frame Start 1, End 5, Lifetime equal to the scene length (72; a lifetime of 50 stopped the bake at frame 57).
  2. Velocity: Normal 20 m/s, Randomize 20 (verified). Physics > Brownian about 20 (150 twirls).
  3. Render As > Collection, pick "Particles", Pick Random on, Collection Scale 0.05 to 1. Rotation panel: tick Rotation and Randomize. Go back to frame 1, Physics > Cache > Bake (delete the bake before changing anything).
  4. Untick Show Emitter in Render and Viewport Display; hide the particle collection in viewport and render (instances still appear).
  5. Colour: plastic material on a brick, Color Ramp into Base Color, Fac from Object Info > Random, a few bright stops, Distribute Stops Evenly, Linear to Constant. Select the other bricks, the source brick last, `Ctrl+L` > Link Materials.
- Principle: a particle system instances a collection (swappable); outward normal velocity gives an even burst; Object Info Random is per instance.
- Other tools: Unity VFX Graph and Godot GPUParticles3D burst with random mesh pick; three.js `InstancedMesh.setColorAt`. Untested.
- Pitfall: lifetime shorter than the scene silently truncates the bake; Random varies per instance only, not across a merged mesh; for big counts use Geometry Nodes (the timeline bake is slow).

## Add-ons

- Stop-Mo: stepped animation panel (free on Superhive); free alternative is the Stepped Interpolation F-curve modifier.
- Mograph Array: array line, grid, ring, curve (free); Mograph Toolbox: fields and falloffs (paid).
- Bone Dynamics Pro: bone jiggle without rigid-body cubes (paid).
- Auto-Rig Pro: Remap panel for retargeting (paid); free alternative is the Rokoko add-on.
- Ultimate Animators Toolkit: graph editor cleanup (paid). Animation Layers: simpler layers than the NLA (price not stated).
- Rokoko Studio and Rokoko Blender add-on: free with an account; Rokoko Indie bundle is paid.
- Copy Global Transform: free, bundled (space switching, fixes foot jitter).

## Already covered elsewhere

- Generic Stepped Interpolation modifier, step sizes and Restrict Frame Range: [timing-and-graph-editor.md](timing-and-graph-editor.md).
- `I` and `K` keying menu in 4.1+: timing-and-graph-editor.md "Keyframe basics and Auto Keying".
- Make Cyclic, loop seam, Copy and Paste Flipped, four-pose walk (Contact, Down, Pass, Up): [cycles-and-locomotion.md](cycles-and-locomotion.md).
- Insert Single Keyframe with Linear Extrapolation loops: [stepped-2d-look-in-3d.md](stepped-2d-look-in-3d.md).
- Pose Library asset route and Bake Sound mouth puppet: use-3d-software `animation-and-nla.md` and `rigging-and-weights.md`.
- Texture face swap and blink basics: [acting-and-faces.md](acting-and-faces.md).

