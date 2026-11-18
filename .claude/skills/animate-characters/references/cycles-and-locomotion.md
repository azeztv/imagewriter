# Cycles, locomotion, IK or FK and pose tools

Walk, run and idle cycles, foot planting, IK versus FK per shot, and the copy and mirror tools. Blender recipes for
the full walk cycle, NLA and Global Transform stay in
[use-3d-software animation-and-nla](../../use-3d-software/references/animation-and-nla.md), "Walk cycle and foot slide".
Build the rig with the `rig-characters` skill.

<!-- skill-navigation:start -->
## Reading Map

- [Cycles, locomotion, IK or FK and pose tools](#cycles-locomotion-ik-or-fk-and-pose-tools)
- [Cycle rules](#cycle-rules)
- [Walk cycle poses (2D and 3D)](#walk-cycle-poses-2d-and-3d)
- [Run and idle cycles](#run-and-idle-cycles)
- [Make Cyclic and the loop seam](#make-cyclic-and-the-loop-seam)
- [Foot slide and root travel](#foot-slide-and-root-travel)
- [IK or FK per shot](#ik-or-fk-per-shot)
- [Copy, paste and mirror poses](#copy-paste-and-mirror-poses)
- [Offsetting and crowds](#offsetting-and-crowds)
- [Acting rules for stops and turns](#acting-rules-for-stops-and-turns)
<!-- skill-navigation:end -->

Ready mocap to study or start from: [codepawl/100style-glb](https://huggingface.co/datasets/codepawl/100style-glb) has 810 clips of 100 walking and running styles (CC BY 4.0), retargeted onto one free character, with a [viewer](https://huggingface.co/spaces/codepawl/100style-viewer) to compare styles side by side. Pick a clip, then key a stylised version over it rather than shipping raw mocap.

## Cycle rules

- The last pose equals the first pose. The last frame of the cycle is the one before the first, so the pose is not shown
  twice (frame 32 instead of 33 in a 32-frame loop).
- Do not paste the same bounce in sync on every part. Offset the head and hands by 2 to 3 frames.
- Key only the channels you move. A key on every channel at every pose makes the loop stiff.
- A looping render keeps the first and last frames the same.

## Walk cycle poses (2D and 3D)

Order of the poses: contact, down, passing, up, then the opposite side.

- 2D (Grease Pencil, Krita, paper): frame 1 draws the contact pose as a stick figure. Frame 10 draws the opposite contact.
  Add the passing pose halfway (head higher, body stretched, leg lifted), then the down poses between contact and
  passing. Copy the first drawing to the last frame and mirror it as a reference for the reverse pose. Set the end
  frame to the loop length (about 39 in the demo). Select all keys, put the playhead at frame 1 and press `S` to speed up
  the walk. Ink on a new layer above with the sketch layer locked, and fill on a layer below.
- 3D (FK, 4 poses): 30 fps, one step is 20 frames, so the cycle is 40. Frame 0 is contact: torso lowered, front heel
  rotated on local X, key feet and torso. `Ctrl+C` the Summary row, then `Ctrl+Shift+V` at frame 20, and copy frame 0 to
  frame 40. Passing (frame 10): `Alt+R`, `Alt+G` on the feet, back foot up (right-click the channel > Insert Single
  Keyframe). Down (frame 5): hips lowest. Up (frame 15): hips highest. Hips rotate toward the lead foot and the shoulders
  counter-rotate. The head bobs. Arms come last, and the hands follow through.
- Graph Editor for the bob: isolate the Z rotation channel (`Shift+H`) and scale Y with the Bounding Box Center pivot.
- Style: a stylized or cartoon walk exaggerates the down and up poses and the hip tilt. A realistic walk keeps them small.

## Run and idle cycles

- The notes give no run poses. Reuse the walk order and make the cycle shorter.
  Add an air phase where both feet leave the ground, and a bigger squash on the down pose.
  This part is inferred, not sourced, so test it with motion paths.
- Idle and breathing: a short loop (for example 48 to 96 frames) on the chest, head and arms with a Cycles modifier.
  Desync the parts by 2 to 3 frames so the loop does not look like one pulse. Add a blink and an occasional shift of
  weight on a separate, longer action.
- Silly walks: delete the Z rotation channels (filter "zquat") or change the pose set, keep the same contact timing.

## Make Cyclic and the loop seam

- Select all curves (`Alt+H` to unhide), then `Shift+E` > Make Cyclic (F-Curve). Or N > Modifiers > Cycles and copy it to
  the other channels. Use Repeat Mirrored when the second half mirrors the first.
- Use `V` > Automatic on the keys so the curve is smooth. The curve looks odd while you edit, which is normal.
- If the loop pops, the last pose differs from the first. Copy the first key to the last frame.
- Looping travel: Cycles modifier with Repeat and Offset, or `Shift+E` > Linear Extrapolation.

## Foot slide and root travel

- The planted heel Y curve stays flat between contacts (Free handles with `V`, then `S` `0`). `Shift+S` > Cursor to
  Selected marks the heel.
- Eyeball the travel: key the root Y at frame 0 and 20 and press `T` > Linear. Exact: copy the heel Y at frame 20 (hover,
  `Ctrl+C`) into the root Y key and set Linear.
- Match speed: put the 3D cursor at the planted foot. Move the root end key until the foot stays on it
  (about 1.18 m per cycle in one demo). Mute the root F-curve to keep the camera still while you check the pose.
- Moving the Armature object instead of the root bone rotates around its origin, which gives better curves.
- Keep walks under about 1.8 m/s so the toes do not slide. Stop with both feet together by ending on the passing pose.
- Speed or slow the cycle with the NLA Playback Scale to keep the feet planted.

## IK or FK per shot

- IK: move a hand or foot controller and the limb follows. Use the pole bone for the elbow or knee direction. Use it for
  exact positions: a drum hit, a hand on a sword, planted feet.
- FK: rotate joint by joint. Use it for loose swinging and dragging arms (a character falling onto a bed: the arms drag
  behind, then overshoot). FK arcs are free. FK loses the end point. IK loses drag and overlap.
- Mix them: a two-handed sword with one IK hand and one FK hand. On a rig use the IK or FK switch property (select the arm
  control, IK FK Switch panel). In Rigify, the slider is 0 for IK and 1 for FK.
  To switch mid-shot, key the pose and step one frame. Click Snap FK to IK (or the reverse), change the slider and key both values.
- Check IK arcs with motion paths. Add breakdown keys to bend them. A raised arm in IK also needs the shoulder rotated up
  and the elbow pole moved forward.
- Rule of thumb: contact poses behave like IK, follow-through behaves like FK. In 2D you choose per drawing which end leads.
- Hide the controls you do not need: Blender 4.0+ Bone Collections (older versions: armature layers).

## Copy, paste and mirror poses

- Copy: box-select the controls, Dope Sheet Summary row (or Pose > Copy Pose), `Ctrl+C`. Paste Flipped: key the opposite
  controls once with `I` first (they need existing keys), then `Ctrl+Shift+V`. Plain `Ctrl+V` pastes unmirrored. Works for
  hands and feet.
- Relaxed hands: curl the fingers a little with `R`. Default hands look stiff.
- Mirror pose in 2D: copy the drawing, flip it and tweak it. Offset one side by a few frames so limbs do not look
  copy-pasted.
- Paste a pose a fixed number of frames later (for example 5) to get consistent easing.
- Reset the rig: `A`, then `Alt+R`, `Alt+G`, `Alt+S`.

## Offsetting and crowds

- 3D: duplicate an action as an NLA strip. Offset each instance by a frame or more, or change its Playback Scale.
- 2D (Grease Pencil): Time Offset modifier, Mode Custom Range, frames 1 to 20, Keep Loop on. Set the pivot to the feet
  first (select feet points, `Shift+S` > Cursor to Selected, then Set Origin > Origin to 3D Cursor). `Shift+D` copies the
  data. `Alt+D` makes a linked instance that shares stroke data. Offset each copy's Time Offset and tint each one.

## Acting rules for stops and turns

These match the `3d-generalist` acting rules. Keep them in one place.

- The head leads every turn and notice by 4 to 6 frames before the body turns.
- Stagger the stops. When a walk ends, the head arrives about 4 frames early.
  One hand settles a few frames after the hips. Offset the head, torso and arms by 3 to 6 frames. No two stops share a frame.
- Add a 0.2 to 0.5 s anticipation or reaction beat before a fall or a fail. Never go straight from calm to the failure.
- A turn over 45 degrees needs a pivot beat (about 0.35 s) before the first stride.
- Never go straight from a kneel or a sit into a walk. Insert a short stand-up idle (about 0.3 s).
- Body weight moves over the supporting foot, the shoulders tilt, and the hand drags slightly behind the body.
