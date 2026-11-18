# 2D: frame by frame, Grease Pencil, Krita and cut-out

Hand-drawn and cut-out animation. Free tools first: Krita 5.x and Blender Grease Pencil (v3 in Blender 4.3+ and 5.x).
Rough Animator, Toon Boom, Spine and TVPaint are paid alternatives. Build the cut-out rig with the `rig-characters` skill.

Version mapping: the Grease Pencil notes come from Blender 2.82 (legacy, "GPv2"). Blender 4.3 and later use Grease
Pencil v3. The names marked "v3" below are mapped from general knowledge, not shown in the videos, so check the UI.

<!-- skill-navigation:start -->
## Reading Map

- [2D: frame by frame, Grease Pencil, Krita and cut-out](#2d-frame-by-frame-grease-pencil-krita-and-cut-out)
- [Choose a tool](#choose-a-tool)
- [Krita frame by frame](#krita-frame-by-frame)
- [Krita FX, shadows and export](#krita-fx-shadows-and-export)
- [Grease Pencil setup (v3)](#grease-pencil-setup-v3)
- [Grease Pencil walk cycle](#grease-pencil-walk-cycle)
- [Grease Pencil layers, materials and fill](#grease-pencil-layers-materials-and-fill)
- [Grease Pencil modifiers and looping](#grease-pencil-modifiers-and-looping)
- [Moving a drawing in 3D](#moving-a-drawing-in-3d)
- [Animatic with scenes and the Sequencer](#animatic-with-scenes-and-the-sequencer)
- [Cut-out animation with sprites](#cut-out-animation-with-sprites)
- [Preview playblast and checks](#preview-playblast-and-checks)
<!-- skill-navigation:end -->

## Choose a tool

| Need | Use | Why |
| --- | --- | --- |
| A hand-drawn shot, bouncing ball, FX | Krita 5.x | Native timeline, onion skin, no camera |
| Drawings that live in a 3D scene or need a camera | Blender Grease Pencil v3 | Drawings are objects in 3D space, so parallax is free |
| A character cut into parts, rig and tween | Cut-out in Blender (COA Tools) or Spine | Keys on bones, reusable parts |
| Pose animation of a 3D model with a drawn look | Blender with a toon shader | See `use-3d-software` and `3d-generalist` |

- Krita has no camera, no transitions and no vector or cut-out rig. It is closer to TVPaint than to Toon Boom. Transform
  tweening was not available in the version shown. Export to another tool for the composite.

## Krita frame by frame

1. Workspace: File > New (2880x1620 for 16:9). Settings > Dockers: enable Animation, Timeline and Onion Skin. Save the
   layout with the Workspace button > Save Workspace (Krita 5.x also ships an Animation workspace). Use a pen tablet.
2. Navigation: `Space`+drag pans, `Ctrl+Space`+drag zooms and `Shift+Space`+drag rotates. Numpad `5` resets.
   `Shift`+drag changes brush size, `E` toggles the eraser and `Tab` hides the UI.
3. Layers match timeline rows. Click the layer's "add to timeline" button for each layer. On the track, right-click a cell
   > Create Blank Frame before you draw. Without a blank frame the stroke lands in the previous frame and overwrites it.
4. Draw the extremes first. Ball on the ground at frame 0, apex at frame 9, next contact at 18, smaller apex at 27.
   Then add the in-betweens (right-click between keys > New Blank Frame). Squash at contact, stretch in the air.
5. Onion skin: the lightbulb on the layer track. In the Onion Skin docker, 0 is the current frame.
   Negative values are before and positive are after, up to 10 each way, with an opacity per offset.
   Lower the opacity to see your own drawing.
6. Retime: drag a key to move it. `Alt`+drag moves all keys after it. `Ctrl`+drag duplicates. `Shift` or drag-select several.
   Right-click > Copy Frame, Paste Frame, Remove Frame.
7. Spacing: keys far apart at the apex and close near the ground. If the ball hangs too long, move the keys closer.
8. Frame rate: 8 fps for rough tests, 12 fps for the character test, 24 fps on twos for a final. Set the end frame in the
   Animation docker (the last frame is the one before the first for a loop).
9. Audio: the Open Audio button in the timeline. Animation Curves docker keys opacity only.
- Pose to pose for a character action: plan the beats in words. Draw the key poses as rough frames spaced far apart,
  with onion skin on. Play, then add breakdowns. Check the arc of the arm and the weight shift.
  Draw the hand first (the hardest part) and fit the arm around it.
  Add in-betweens only where the jump is too violent. Slow in and out: more frames near the poses, fewer in the middle.
- Pitfalls: pick the correct layer row before you draw. The lightbulb sometimes disappears (click the canvas). Switching
  onion skin on and off can bug the display. Keep a guide layer for perspective and hide it before export.

## Krita FX, shadows and export

- Overlap layers: a `face` layer, drawn per frame, and an `fx` layer with frames only at the moment of contact. End the
  effect with a blank frame so no drawing stays.
- Fluid fire and smoke: change the blob shape every one or two frames. Make the mass trail behind the hand (drag), then
  move ahead as it is thrown. Smoke shrinks in volume on every frame and rises with gravity. Draw the orb on twos and bounce
  its position a little.
- Shadows: a layer set to Multiply, an airbrush or soft brush. Shade only the frames that need it (static shadows can be one
  long frame). Do it after the motion works.
- Export: save the .kra, then File > Render Animation. Set the last frame first, or the whole timeline renders.
  Choose GIF or MP4 (needs FFmpeg). You can delete the numbered PNG sequence afterward.

## Grease Pencil setup (v3)

1. Edit > Preferences > Input > Emulate 3 Button Mouse (Alt+stylus rotates, `Ctrl+Alt`+drag zooms, `Shift+Alt`+drag pans).
   Turn it off for cut-out rigging, where Alt assigns bones.
2. Delete the default cube. `Shift+Right-click` moves the 3D cursor. Add > Grease Pencil > Blank (v3: Add > Grease Pencil
   > Blank or Stroke). Switch Object, Edit, Sculpt and Draw modes from the header or the `Ctrl+Tab` pie.
3. For a 2D scene: File > New > 2D Animation gives a white background, a camera view (`Numpad 0`) and Ink brushes.
4. Drawing Plane (legacy name Stroke Placement): View, Front X-Z, Side Y-Z, Top X-Y, 3D Cursor, Surface. View projects onto
   the camera. Overlay > Canvas shows the grid on that plane. To flatten strokes at different depths: Edit Mode, select all,
   Clean Up > Reproject Strokes, choose Front (v3: Stroke menu, check the name). Fills project from the view too, so fill
   while looking straight at the right plane.

## Grease Pencil walk cycle

1. Open the Dope Sheet in Grease Pencil mode (not the object Dope Sheet). Make a layer `sketch` with a blue material.
2. Frame 1: contact pose as a stick figure. Right-click > Insert Blank Keyframe (Active Layer) to start each new drawing.
   Frame 10: opposite contact. Then passing, then the down poses. Copy the first drawing to the end frame (`Ctrl+C`,
   `Ctrl+V` in Edit Mode) and flip it with `G`, `X`.
3. Onion skin: Object Data > Onion Skinning (opacity, frames before and after, tint colours). Toggle it in Overlay and
   per layer.
4. Fix a bad frame in Edit Mode (`2` selects connected strokes, then scale and rotate). Drag a key onto another to
   overwrite it.
5. Set the end frame to the loop length. Select all keys (`A`) and press `S` with the playhead at frame 1 to speed up. `B`
   box-selects a part.
6. Ink on a new layer above with the sketch layer locked. Fill on a layer below. Clean geometry: Draw-mode Shapes (Circle,
   Line, Curve, Bezier, `Enter` or `Space` to confirm) and the Smooth option.
- 3D too: the contact, down, passing, up order also drives a keyed 3D walk.

## Grease Pencil layers, materials and fill

- Layers live in Object Data: add, rename, lock, hide, opacity, blend mode and a per-layer onion icon. Each material has a
  Stroke part and a Fill part. Change the material colour after drawing to recolour every stroke that uses it.
- Workflow: a sketch layer in blue, an ink layer above in black (Ink Pen, Stroke-only material), a colour layer below
  (Fill-only material). Lock the sketch layer before inking so `Ctrl`-erase does not erase it.
- Fill tool (paint bucket): click inside a closed shape. Hold `Ctrl` and draw a line to close a gap. A leak means a gap
  in the line.
- Edit and Sculpt: `Tab` Edit Mode, `A` select all, `B` box, `1`, `2`, `3` point, stroke and segment select. `G`, `R`, `S`
  with `X`, `Y`, `Z`. Sculpt brushes: Push, Grab, Smooth, Randomize, Thickness (`F` size, `Shift+F` strength, hold `Shift`
  to smooth, hold `Ctrl` for the opposite effect). Edit Mode > Clean Up > Delete Loose Points removes stray dots.

## Grease Pencil modifiers and looping

- Time Offset: Modifiers > Add Modifier > Time Offset, Mode Custom Range, frames 1 to 20, Keep Loop on. Extend the timeline
  to see it loop.
- Noise for the "boiling line" look: low Factor, and use Step to set it on twos. Thickness, Smooth and Tint modifiers also
  exist. Tint can target one material. The v3 modifier names are the same.
- Wind loop on drawn bushes: add a lattice per layer with a Lattice modifier. Key a lattice shape key side to side.
  Make the first and last values equal.
- Camera loop with parallax: parent the camera to a Plain Axes empty and key small rotations, first and last equal. Too
  much rotation shows flat drawings as cards.

## Moving a drawing in 3D

- A walk drawn in place gets its travel from an object key. Key the object with `I` > Location, frame 1 off-screen, frame
  100 on the other side. Use the regular Dope Sheet for object keys (the Grease Pencil Dope Sheet shows drawings).
- Default easing gives slow in and out, so select the keys and press `T` > Linear for constant walk speed. In the Graph
  Editor X is red, Y is green and Z is blue. The camera is keyed the same way.
- Several characters at different depths give parallax when the camera moves.

## Animatic with scenes and the Sequencer

- Scene menu: rename to `shot_a`. New Scene > Full Copy (not Linked Copy) for `shot_b`. Make an `edit` scene with the
  Video Editing workspace. Add > Scene (`Shift+A`) for each shot and drag handles to retime. Output: FFmpeg video, MPEG-4,
  then Render > Render Animation. Shot changes show live in the edit scene.

## Cut-out animation with sprites

Parts on layers, then keys on bones or transforms. Source set:.

1. Draw the whole character on one sketch layer, with the feet and arms pointing the same way. Add a layer per part (arm_r,
   hand_r, torso, arm_l, hips, leg_r, leg_l, head). Overlap the neighbouring part so joints hide gaps. Add a flat colour
   layer below each line layer. Group each part (`Ctrl+G`). Stack: hips above both legs, torso above hips, near arm above
   all, head above torso.
2. A hand drawn too far from the shoulder breaks the rig. Plan the pivots.
3. Export each part: hide the background, show one group, Crop tool, File > Save As PNG (`arm_l.png`), undo the crop,
   repeat. Krita 5 also has Layer > Export Layer and Batch export (check your version).
4. Blender: COA Tools (Cutout Animation Tools by ndee85, free, targets Blender 2.8x, so check 4.x or 5.x support before
   you rely on it). Free alternatives: Spine (paid), or Grease Pencil with bones. Import sprites with Create New Sprite
   Object, then Import Sprite. Set draw order with the Z value (back leg and far arm negative, front arm positive, torso 0).
5. Rig: root at the hip, then bones along the spine and limbs. Give each chain a slight bend toward the front so IK
   knows the direction. Then add IK bones.
   For a bendy limb, convert the sprite to a mesh (triangulate the border). Subdivide twice where it bends and bind it to
   the bones. IK hands do not arc, so use FK for a nice arc.
   Build the pelvis as a part that the legs attach to, so the torso can bend.
6. Sprite swap (hand poses): put the variants in equal-sized boxes in one PNG strip. Set Tiles in the COA panel and key the
   Tile Offset with `I`. Re-importing a replaced sprite errored in the video, so make a new sprite object instead.
7. Animate: Auto Keying on, select the whole character, key. `Shift+Right` jumps 10 frames. Key every bone at each pose.
   Squash by scaling in Z. Set the end frame in the Timeline range so the loop closes.
8. Render with an Orthographic camera (for example 960 x 960). Fake a shadow with a flat grey circle scaled in X under the
   character.

## Preview playblast and checks

- 2D: play at the final frame rate with the background and sound. Check the loop seam, the arc paths and the held frames.
  Turn the sketch layer off and check that the inked pose still reads.
- 3D with a drawn look: View > Viewport Render Animation over the preview range, with overlays, before any final render.
- Render a PNG sequence for finals, then assemble in the Video Sequencer (Add > Image/Sequence, FFmpeg, MPEG-4, H.264).
