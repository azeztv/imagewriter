# Stylized rig recipes (rigging, weights, face rigs)

Rig recipes for stylized, toy, cartoon and robot characters: bendy-bone limbs and tails, hard-weight rigs, Rigify built from
samples, weight fixes, corrective and face shape keys, image-sequence faces driven by a bone, squash and stretch, ragdoll proxies.
Routes are checked against Blender 5.2 (from notes made in Blender 2.8 to 4.4). Where a video route moved, the 5.2 route is given
and the old name is mentioned. `(heard)` means no value in the entry was seen on a frame. `untested` marks a route the note
infers. Base Rigify, bone roll and shape key basics are in `bones-and-weights.md` and `face-rigs.md`.

<!-- skill-navigation:start -->
## Reading Map

- [Stylized rig recipes (rigging, weights, face rigs)](#stylized-rig-recipes-rigging-weights-face-rigs)
- [Corrective shape key driven by a bone](#corrective-shape-key-driven-by-a-bone)
- [Slider handle that drives a shape key](#slider-handle-that-drives-a-shape-key)
- [Image-sequence face driven by a bone](#image-sequence-face-driven-by-a-bone)
- [Slider ticks and custom bone shape](#slider-ticks-and-custom-bone-shape)
- [Attach a face plane to a head](#attach-a-face-plane-to-a-head)
- [LCD pixel face on a screen](#lcd-pixel-face-on-a-screen)
- [Ten-shape lip sync with no mouth bones](#ten-shape-lip-sync-with-no-mouth-bones)
- [Eye rig: blink key, aim bone, master control](#eye-rig-blink-key-aim-bone-master-control)
- [One shape key for a whole-body pose](#one-shape-key-for-a-whole-body-pose)
- [Stretch To with absolute handles (bendy chains)](#stretch-to-with-absolute-handles-bendy-chains)
- [Rubber-hose rig](#rubber-hose-rig)
- [Hard-weight rigid rigs (empty groups)](#hard-weight-rigid-rigs-empty-groups)
- [Control circle and parent order](#control-circle-and-parent-order)
- [Single-axis toy rig (LEGO minifig)](#single-axis-toy-rig-lego-minifig)
- [Rigify built from samples](#rigify-built-from-samples)
- [Fix automatic weights](#fix-automatic-weights)
- [Cloth cage with Surface Deform](#cloth-cage-with-surface-deform)
- [Squash and stretch lattice](#squash-and-stretch-lattice)
- [Ragdoll proxy bones](#ragdoll-proxy-bones)
- [Voxel Remesh rig for blobby characters](#voxel-remesh-rig-for-blobby-characters)
- [Transformation constraint instead of drivers](#transformation-constraint-instead-of-drivers)
- [Add-ons](#add-ons)
- [Already covered elsewhere](#already-covered-elsewhere)
<!-- skill-navigation:end -->

## Corrective shape key driven by a bone

- **Corrective key**: a sculpted fix (a bicep that collapses on bend) that fades in only when the joint bends.
- Steps: select the mesh. Object Data > Shape Keys > `+` twice: `Basis`, then `Bicep-Fix`. Set its Value to 1. In the Armature
  modifier tick Edit Mode display so the bones stay visible. Pose the arm bent, Sculpt Mode, Inflate brush (strength 1.0, radius
  about 172 px in the frame) and push the bicep out. Object Mode, right-click the key Value > Add Driver. Drivers editor (N >
  Drivers): type Scripted Expression, variable Single Property or Transform Channel: Object = the armature, Bone = the bone
  (`Bone.001` in the video), Type = Z Rotation, Space = Local Space. The bone reads about -1.261 rad (-72.3 degrees) when bent,
  so the expression is `var * (-1)`. The key is 0 straight and 1 bent. Repeat per joint (arm, forearm, leg, body).
- Principle: drive a sculpted correction by the joint angle, so the straight pose is never touched.
- Other tools: glTF morph targets (three.js `morphTargetInfluences`), Unity and Godot blend shapes, Unreal morph targets can be
  driven by the bone angle in a script or graph. Blender keeps the drivers inside Blender (Blender drivers do not export).
- Pitfall: adding or deleting vertices after the keys exist breaks them. Sculpt edits show only when Value is above 0. The driver
  needs Local Space or the value is wrong.

## Slider handle that drives a shape key

- **Slider control**: an animator-friendly Happy/Sad slider next to the character.
- Steps: Add a Plane, R X 90, scale into a tall rectangle, Display As Wire or Bounds, Object properties > Visibility: Render off.
  Duplicate to a small square at the bottom, parent the square to the rectangle (Keep Transform). Add text above. Lock every
  transform channel of the square except Z. Object Constraints > Limit Location: tick Minimum Z and Maximum Z, Owner Space Local,
  type the lowest and highest Z (hover a field and Ctrl+C to copy). Right-click the key Value > Add Driver: Scripted Expression
  `var` (the default `var + 0.0`), variable = the square's Z Location, Space Local. Tune the min and max until the key reads 0 at
  the bottom and 1 at the top.
- Principle: a constrained object is a handle; the driver maps its position to the key value.
- Pitfall: World Space gives wrong values once the control moves with the rig. Use Local.

## Image-sequence face driven by a bone

- **Bone-driven face**: a flat plane carries a numbered face sheet; one bone slides to pick the face. No shape keys.
- Steps (Blender 5.2): Add > Image > Mesh Plane and pick the numbered images (in 4.1 and earlier: File > Import > Images as
  Planes, an add-on that was off by default before 4.2). Leave Detect Image Sequence off for the frames you want to drive by hand,
  or tick Animate Image Sequences. R X 90, Ctrl+A rotation and scale. Material: Image Texture node > Source = Image Sequence,
  open all frames, Frames = 1 (the default 25 cycles through them), Start Frame 1, Auto Refresh on, Cyclic off. For a sheet of
  26 frames the video types Frames 26 and runs Offset 0 to 25.
- Driver, bone slides on Y: add one bone named `Face-Rig`, Pose Mode, Transform Orientation Local. Right-click the bone's Y
  Location > Copy as New Driver; right-click the Image Texture Offset > Paste Driver. Expression `abs(int(eye*10))`
  (`*10` = one frame per 0.1 m, `int` removes in-between values, `abs` makes dragging down count up). Variable type Single
  Property, path `pose.bones["Eye-Ctrl"].location[1]`. Rename the bone before the driver, or the driver turns red.
- Driver, bone slides on X (variant): Scripted Expression `int(xloc / 0.1)`, variable `xloc`, type Transform Channel, Object =
  armature, Bone = `eyes`, X Location, Local Space. The default variable name `var` glitched in the video, so rename it.
- Limits: lock every location channel except the slider axis (Bone tab > Transform). Bone Constraints > Limit Location, tick the
  min and max of the slider axis (about -0.7 to 0 on Y in one video; Max X = 2.5 for 26 frames x 0.1), tick Affect Transform, Owner
  Space Local. Without Affect Transform the bone slides past frame 0 and shows the purple missing-texture frame. Alt+G resets the bone.
- Several features on one plane: eyes and mouth as two planes (offset the mouth 0.0001 on Y to stop z-fighting, Shadow off in
  Object properties > Shading), Ctrl+J into one object `facial rig`, Subdivide 2 or 3 times so it can wrap. Duplicate the bone
  (Shift+D), name it `mouth`, copy the driver expression to the mouth Offset and change the bone. Rotate the mouth bone 180 degrees
  so its slider sits below the eyes.
- No-bone variant: hover Offset, press I at frame 0, type (face number minus 1) on later frames (face 10 = Offset 9). Dope Sheet:
  select the keys, T > Constant, so faces swap instantly. A new key interpolates again, so repeat T > Constant.
- Principle: a driver turns bone position into an integer frame index, so the sheet is a sprite selector that animators key in the
  normal pose workflow.
- Other tools: three.js, Godot, Unity and Unreal use an atlas or array texture with a stepped frame index (`floor(abs(control*10))`
  in a shader uniform, `texture.offset`, `uv1_offset`, material offset). Untested for the shader route.
- Pitfall: Principled v2 (4.0+) renamed Specular to Specular IOR Level, so the video value 0.25 is not the same look; use about
  0.2 to 0.3 (inferred). Python-style driver expressions can be blocked when Auto Run Python Scripts is off (guessed, not tested).
  frames 5:45, 7:10 and 3:20; Blender 3.6, 4.4.1 and 2.82). See also `face-rigs.md`, "2D face texture atlas driven by a bone".

## Slider ticks and custom bone shape

- **Slider bone with frame ticks**: an arrow bone and a row of tick marks so the animator sees each frame.
- Steps: enable the Extra Objects extension (Extra Curve and Extra Mesh). Shift+A > Curve > Profile Arrow, Curve data Fill Mode =
  None, set the origin at the tip, rotate 90 around the cursor so it points up. Bone Properties > Viewport Display > Custom Object
  = the arrow, Wireframe on. Ticks (heard): Shift+A > Curve > Rectangle height 3 m, width 1 m, R 90, Fill None, convert to Mesh,
  apply rotation and scale, Array modifier with Relative Offset off, Constant Offset on, Distance X 0.1, Count 26. Parent the ticks to
  the armature (Ctrl+P > Object, Keep Transform).
- Quick custom shape (2D rig video): Add > Mesh > Plane in top view, merge the two top vertices to a triangle, scale, apply, delete
  the face (X > Only Faces), then Bone > Viewport Display > Custom Object.
- Principle: each tick is 0.1 m, one frame per tick. The shape is for the animator only.

## Attach a face plane to a head

- **Face plane on a curved head**: the flat face follows the head and does not shade the body.
- Steps, Shrinkwrap route: modifier Shrinkwrap, Target = head, Wrap Method Nearest Surface Point, Snap Mode On Surface (Above
  Surface did not work reliably), Offset: Shift-drag to a tiny positive value so the plane floats just above. Subdivide the plane
  first, optionally a Simple Subdivision above the Shrinkwrap. Object properties > Visibility: turn off shadow casting. Parent the
  plane to the character rig.
- Steps, bent plane route (when a clay shader makes Shrinkwrap bubble): F2 name `Face`, Ctrl+P Keep Transform onto the head.
  Edit Mode, A, Subdivide, move the corner rows back with proportional editing so it bends around the head. Object > Visibility >
  Ray Visibility (Cycles): untick Diffuse, Glossy, Transmission, Volume Scatter and Shadow, keep Camera. Shader: delete Principled,
  Emission (face colour) into the lower slot and Transparent BSDF in the top slot of a Mix Shader, Image Alpha to Fac.
- Principle: only the camera sees the face, so it casts no shadow or reflection, and alpha cuts the face out.
- Other tools: an unlit transparent material in three.js, Godot (Unshaded, Alpha) or Unity (Unlit, Cutout); a decal in Unity or Unreal.
  Untested.
- Pitfall: small Offset only, else a visible gap. In EEVEE (5.2) the old Blend Mode and Show Backface became Render Method:
  Transparent, with shadows set in the Object settings (inferred).
  frames 9:50, 12:51 and 9:14)

## LCD pixel face on a screen

- **Pixel-grid robot face**: a numbered 25-face sheet shown through a dot-matrix shader and swapped by the Offset value.
- Steps: append a Matrix Display material (a free forum shader by CgCody; the file comes with the video). Add a UV map `face` for
  the screen (seam the border loop, unwrap), set the shader's UV to `face`, rotate -90 in the UV editor to fit. Values at the
  frame: Pixel Size 0.003, Pixel Gap 0.200, Roundness 0.500, Smoothness 1.000, Texture/Mono 1.000, Mono Color green, Strength 2.000.
  Image Texture: Image Sequence, Frames 1 (down from 25), Auto Refresh and Cyclic on, key Offset with I, Graph Editor T > Constant.
- Principle: the image sequence is a sprite sheet and the offset is the face index.
- Other tools: atlas with a UV offset uniform, quantized index.
- Pitfall: EEVEE shows nothing in Solid view; use Rendered. Today's route would be a procedural grid mask in the same slot
  (untested in 5.2).

## Ten-shape lip sync with no mouth bones

- **Phoneme shape keys**: lip sync keyed by hand against the audio, no mouth rig.
- Steps: apply the Mirror modifier. Shape Keys: Basis is the closed mouth, then one key per phoneme from a 10-shape chart (the
  frames show EE, I, Oh, V.W, FU, MM, LU, SS plus Eye L and Eye R). Tab into each key and push vertices to the chart. Keep a
  `Mouth` vertex group on the head. Video Editing workspace: add the sound strip at frame 1 and scrub to hear it. Key the previous
  shape to 0 and the next to 1 (I over the value). Cross-fade tightly, since overlapping shapes make vertices fight. Timeline
  markers name each change (F_01, F_03, F_05).
- Principle: a few mouth shapes with keyed weights beat a bone rig for short clips.
- Other tools: glTF morph targets, Godot and Unity blend shapes.
- Pitfall: exact per-phoneme values are not shown on screen.

## Eye rig: blink key, aim bone, master control

- **Cartoon eye rig**: a blink shape key, an eye that aims at a controller, one master control.
- Steps: UV Sphere, Shade Smooth. Edit Mode: duplicate and scale slightly for the lids. Ctrl+I, H to hide the eyeball. Select the
  equator, V (rip) to split, hide the upper half, Alt+click the open loop, F to fill, Ctrl+B bevel 1 or 2 segments for a lip (repeat
  for the other lid). Shape Keys: `Basis`, `closed`, `open`. On `open`, Pivot to 3D Cursor, select the upper lid with L, R 90 then
  back, R -90 around the cursor, scale in slightly to avoid z-fighting. Value 1 = open.
- Blink: key the value, Dope Sheet T > Constant so it snaps. A turtle variant renames Basis to `Open` and adds `Closed` (pupils
  duplicated inside, eyelids scaled over); blink = animate Closed 0 to 1. Extra emotions are more keys.
- Aim: Armature, Edit Mode, bone along Y from the eye centre (R -90), Shift+D a second bone pushed forward on Y, names `Eye` and
  `Eye.Ctrl`. Parent the sphere with Ctrl+P > With Empty Groups and assign all vertices to the `Eye` group. Alt+P on the control
  bone. Pose Mode, `Eye` > Bone Constraints > Track To: Target = armature, Bone = `Eye.Ctrl`, Up = Z, Track Axis = Y. Duplicate
  eye and armature for the second eye. A Mesh Circle (R X 90, flattened to an oval) between the eyes is the master. Each eye bone
  gets Child Of to the circle, then Set Inverse (all location, rotation, scale ticked). To attach to a character: select both
  armatures, the circle and the eyes, then the character, Ctrl+P > Object (Keep Transform). Leave the eyes half inside the head so
  the lids fit.
- Principle: a shape key for lid rotation replaces a full eyelid rig; Track To plus a target is one-control gaze.
- Other tools: a look-at or aim IK node in Unity, Unreal, Godot; blink as a stepped morph target.
- Pitfall: the lid otherwise travels the shortest path; use Constant or add in-between keys.

## One shape key for a whole-body pose

- **Croak key**: one relative key bloats the body, flares the feet and lifts the eyes, as a squash and stretch.
- Steps: Shape Keys `+` for `Basis`, `+` for `Croak`. Edit Mode (hidden parts stay hidden): select the body top, scale up with
  proportional editing, move up on Z. Alt+H, L over the feet, move out and rotate, L over the eyes, lift on Z. Object Mode: Value 0
  to 1, I to key, step forward, I again, add a small wave on the way down so it reads as breathing, then back to 0. Scale the keys in
  time to slow it (the video uses 30).
- Principle: one relative key moves several parts as one pose.
- Pitfall: the key must sit on the same mesh as Basis. Use the right selection filter for hidden parts.

## Stretch To with absolute handles (bendy chains)

- **Bendy-bone chain**: moving two control bones bends a long body (banana, tail, tentacle, hair, smeary arm) like a Pen-tool curve.
- Steps, one segment (banana): Shift+A > Armature > Single Bone, wireframe, drag it to the base, E up to the height, E for a head
  bone, Alt+P Clear Parent on the last, name `Start`, `Body`, `End`. Armature data > Viewport Display > Display As B-Bone. Bone tab >
  Bendy Bones > Segments 12. Pose Mode, `Body` > Bone Constraints > Stretch To: Target armature, Bone `End` (Original Length 1.0175,
  Volume Variation 1.0, Maintain Volume XZ, Rotation Swing, Influence 1.0). On `Body`, Bendy Bones: Start Handle = Absolute, Custom
  = `Start`; End Handle = Absolute, Custom = `End`. Ctrl+A > Apply Pose as Rest Pose (spoken as "search apply rest pose"), Tab out,
  mesh then armature, Ctrl+P > With Automatic Weights (heard).
- Steps, longer chain: bones `start.000`, `mid.000`, `end.000` (the `.000` lets Blender number copies). Clear parent on the first
  and last. Middle bone Segments about 10. `start` > Stretch To the next control (`mid`). Middle bone Start Handle Absolute with
  Custom = the bone beneath it, End Handle Absolute with Custom = the bone above. For longer chains extrude five times in total,
  clear parent on every control bone, 10 segments on the middle ones, handles pointing to neighbours (`n.000`, `n.002`). G and R on
  the controls curve the chain. Bind with Ctrl+P > With Automatic Weights. Select the end and mid bone together when moving.
- Principle: each control owns a curve segment through the handles, Stretch To makes length follow.
- Other tools: Godot has no bendy bones (use a Skeleton3D IK chain or a Path3D skin); Unity and Unreal spline IK; three.js a
  `CatmullRomCurve3` sampled for a skinned tube, or three bones with two moved. Untested.
- Pitfall: keep the rest pose applied before parenting. Offset each bone's keys by a frame or two for a whip-like follow-through.
  4:30; Blender 3.4 and 3.2; in 5.2 bones sit in bone collections, panel names unchanged, inferred)

## Rubber-hose rig

- **Noodle limbs** for Cuphead-style animation: limbs stretch between two end bones and bend at a free knee or elbow.
- Steps: Front view, Single Bone named `Rubber-Rig`. Names used: Head, Neck, Body.End, Body, Body.Start, Hip.Control, Root;
  Leg.Start.L, Leg.L, Leg.End.L, Foot.Control, F.Start.L, F.End.L; A.Start.L, Arm.L, Elbow.L, A.End.L, Hand.L, H.End.L. The `.L`
  suffix is needed for Symmetrize. Knee: Shift+D the leg, right-click Subdivide, E Y on the middle point, delete the helpers, name
  `Knee.L`. Elbow the same.
- Parenting (Ctrl+P > Keep Offset): Body.End Alt+P (stays connected to the neck); A.Start.L, A.End.L, H.End.L to Body.End; Elbow.L and
  Knee.L Alt+P (done by constraint); Leg.End.L to Hip.Control; Leg.Start.L, F.Start.L, F.End.L to Foot.Control; Foot.Control and
  Hip.Control to Root; Body.End to Body.Start. Bone > Relations: Inherit Rotation off for Body.End and Neck.
- Deform off (Alt applies to all selected) for Hip.Control, Root, Knee, Foot.Control, Elbow. Display As B-Bone. Bendy Bones Segments 12
  for arm and leg, 6 for foot, hand and body.
- Constraints (Bone Constraints): `Leg.L` Stretch To `Leg.End.L`; its Bendy Bones Start and End Handle Absolute with `Leg.Start.L`
  and `Leg.End.L`. `Knee.L`: Child Of, bone `Body.Start`, Location XYZ and Scale XYZ on, Rotation off, then Set Inverse after
  switching rotation off. Damped Track from `Leg.L` to `Knee.L` with Track Axis -Y; `Leg.Start.L` to `Knee.L` (default axis). Arm
  and foot repeat it (Elbow.L is Child Of to `Body.End`; hand Start Handle Automatic, End Handle Absolute to the hand end; body Stretch
  To `Body.End`). Select all, Armature > Symmetrize, mesh with Ctrl+P > With Automatic Weights.
- Principle: the hose comes from Stretch To, the bend from a free knee or elbow that Damped Track and the handles follow.
- Other tools: Unreal Control Rig, Godot SkeletonModifier3D or Unity Animation Rigging do two-bone IK with a bend control
  (inferred, untested).
- Pitfall: after resizing bones, click the X next to Original Length on every Stretch To and Set Inverse on every Child Of; the
  author says that fixes most breaks. Select a bone in the Outliner and press Numpad Period to find it.

## Hard-weight rigid rigs (empty groups)

- **No weight painting**: a robot, mech or blocky character where each part follows one bone at weight 1.
- Mech with IK legs: Single Bone `Mech-Arm`, Viewport Display > In Front. Rename `Root`, Shift+D up, E Z for `Body` and `Head`. Build
  everything on the left with `.L` so Symmetrize copies parenting. Hip bone parented to `Body`; leg chain `Leg.000.L` onward; a
  short `Chain.L` IK bone in front, Deform off; `Foot.L` parented to `Root` with Keep Offset so the foot stays planted. Pose Mode:
  select `Foot.L` then `Chain.L`, Shift+I > To Active Bone. Inverse Kinematics values at the frame: Target the armature, Bone
  `Foot.L`, Iterations 500, Use Tail on, Stretch on, Weight Position 1, Influence 1; Chain Length 4. Lower limb bones: Rotation Mode
  XYZ Euler, then lock axes under Bone Constraints so only the useful axis turns. If the foot got parented to Root by mistake,
  re-parent the hip to `Body` in Pose Mode.
- Bind: Ctrl+P > With Empty Groups (not Automatic Weights). Edit Mode, L over a part, pick its vertex group, Weight 1, Assign, H to
  hide it. Repeat per part.
- Three-bone character (Among Us): keep the origin at the world origin with the feet on it. Bones `root`, `body`, `leg.R`, `leg.L`
  (leg bone from the top of a leg to the foot, Shift+D X for the other, select both legs then `body`, Ctrl+P > Keep Offset). With
  Empty Groups, move the Armature modifier above Subdivision. L over a leg, group `leg.L`, Weight 1, Assign; same for `leg.R`; select
  all, deselect each leg through the group's Deselect button, assign the rest to `body`. For leg mobility, scale the inner loops
  slightly.
- Principle: fully separate mesh islands with weight 1 give clean rigid motion.
- Other tools: rigid skinning in Godot, Unity and three.js (`SkinnedMesh`, one bone index per vertex). Unity Animation Rigging has
  Two Bone IK, three.js has `CCDIKSolver`; the note did not show them.
- Pitfall: a stray body vertex in a leg group makes the leg rotate with the body; use Remove.
  parenting steps heard)

## Control circle and parent order

- **One circle moves everything**: parent order separates what follows the whole robot from what follows only the body.
- Steps (robot with treads): armature with a tiny `root` and a `body` bone. Mesh Circle around the robot as the control. Pose Mode
  select `root`, Object Mode, circle, Ctrl+P > Object (Keep Transform) so the circle parents the armature. Monitor then armature,
  Ctrl+P > With Empty Groups, assign all vertices to `body`. Armature In Front. Parent each tread curve and its cube (Keep Transform)
  and the gears to the circle. Second tread: duplicate, snap to the other side, then Object Constraints > Copy Location, target the
  first tread, tick only Z, World Space, Influence 1, so both scroll together.
- Ghost variant: Add > Curve > Circle named `Ghost-Control`; ghost then control (active), Ctrl+P > Object (Keep Transform). Arms
  are UV spheres with the origin at the shoulder, parented to the control too (pinning arms to a cloth body can break the cloth).
  Mirror an arm: pivot to 3D Cursor, Shift+D, R Z 180, back to Median Point. A prop goes to the hand with Ctrl+P Keep Transform.
- Principle: a body bone bobs the monitor without moving the treads; the circle carries the rest.
- Pitfall: other engines use a root transform and a driven child, not the same node setup.

## Single-axis toy rig (LEGO minifig)

- **Each bone rotates one way**, like a real minifig piece.
- Steps: two 3D views (front, side). Armature `Lego-Mini-Arm`, In Front. Scale the character to real size if physical lighting or
  depth of field matters, apply scale. Bones: `root` at the feet, `leg.L` at the hip pivot, `arm.L` at the shoulder pivot (straight,
  limbs rotate rather than bend), `body` upright with a `head` bone extruded from its tip, `hand.L` angled on the wrist. Pose Mode:
  Rotation Mode XYZ Euler for every bone. Edit Mode, Keep Offset parenting: hand to arm, leg to body, arms to body, body to root.
  Transform orientation Local; lock channels by click-dragging the lock column: arm Z only, hand Y only, body X only plus location,
  head Y only, legs Z only (heard; the frame matches the locks at 15:05). Symmetrize (F3). Bind with Ctrl+P > With Empty Groups,
  L over each piece, assign at weight 1. Controls: a hidden Mesh Circle as Custom Shape (Custom Object, Scale to Bone Length on,
  scale about 0.35 for the arm).
- Principle: one local axis per bone means R works from any view and cannot go wrong; rigid weights give toy-plastic motion.
- Other tools: a parent hierarchy of pivots in three.js, Godot or Unity, no skinning needed.
- Pitfall: do not hit the key buttons beside the lock icons. Locks are per bone, so check after Symmetrize.

## Rigify built from samples

- **Samples kit**: Rigify generates controls from sample bones, so editing that list rigs a non-human (cat, cardboard robot, prop,
  building).
- Steps: enable Rigify. Armature > Human (Meta-Rig) or an empty Armature with its default bone deleted. Armature data > Rigify panel
  > Samples: pick one, Add Sample. Frames show: basic.copy_chain, basic.pivot, basic.raw_copy, basic.super_copy,
  experimental.super_chain, face.basic_tongue, face.skin_eye, face.skin_jaw, faces.super_face, limbs.arm, limbs.front_paw, limbs.leg,
  limbs.paw, limbs.rear_paw, limbs.simple_tentacle, limbs.super_finger, limbs.super_limb, limbs.super_palm, skin.anchor,
  skin.basic_chain, skin.glue, skin.stretchy_chain, skin.transform.basic, spines.basic_spine, spines.basic_tail, spines.super_head,
  spines.super_spine. Delete a sample only as a complete set of bones, or Generate errors (delete the three arm bones for a
  one-armed rig; add a second arm sample for four arms). Samples placed together land in sensible spots but are not parented: parent
  by hand (Keep Offset), then Generate. Bone > Rigify Type switches the sample type of a bone. Adding faces.super_face prompts
  "Upgrade Face Rig".
- Cat rig steps: select the metarig, In Front. Delete the left half, scale with Pivot = 3D Cursor, move leg, hips, arms, spine and
  head over the mesh, then select all and Armature > Symmetrize. Custom bones: Shift+click the 3D cursor (the sword tip), add the
  `basic.pivot` sample, Shift+S Selection to Cursor on head and tail, set Roll in N > Item, name it `sword`. F3 "Switch Direction"
  puts the control at the tip. Ears the same, then Symmetrize the one bone. Add a bone collection `Special`, assign the sword and
  ears and remove them from Torso, Color Set Extra, and click the small arrow in UI Layout so the button shows in the rig's side
  menu. Name the object `cat.rig`, Generate Rig. After: Bone > Custom Object swaps a control shape; Y translate and scale 0.5 for ear
  controls. Hide unused heel and toe bones by moving them from the leg IK to the leg tweak collection.
- Cardboard robot steps (Blender 3.1 route): Human meta-rig, delete all bones (the layer names stay). Armature > Rigify Layer Names:
  add a `Face` row. Add samples `limbs.leg` (appears as `.L`) and `limbs.arm`; `spines.super_head` for a stiff head; `basic.super_copy`
  for eyebrows, flaps and jaw (R X 90; Eyebrow.L, Flap.L; Jaw without a suffix so it is not mirrored; Shift+S Cursor to Selected to
  snap the jaw to its pivot). Select all, Symmetrize. Eyebrow, flap and jaw bones parent to the head bone (Keep Offset), both arms
  connect to the head bone, upper legs parent to the base so the face does not flip the legs. super_copy bones get Widget = cube in
  Bone > Rigify Type. Save an incremental file, Generate Rig, fix shapes in Bone > Viewport Display > Custom Shape.
- 5.2 route: "Rigify Layer Names" and "M to a layer" were removed in 4.0. Assign bones to Bone Collections and set the Rigify
  collection UI (row, Color Set) in the Armature tab instead. Bone Groups became Color Sets. The sample list in 5.2 is unverified.
- Bind: either Automatic Weights, or With Empty Groups, then L over a part, pick its `DEF-` group (use the first, not the `.001`
  tweak group, with tweak layers off), Weight 1, Assign, H. Assign leftovers to the head bone, Alt+H.
- Principle: Rigify's presets are assemblies of these samples; building from samples gives IK/FK and layers without hand rigging.
- Other tools: no generator; Unreal Control Rig and Godot skeleton modifiers are modular but not one-to-one.
- Pitfall: Rigify roots at the world centre, so move the feet to Z=0 first. A custom bone must be set as Deform (Bone tab) or no
  vertex group is made, and the vertex group names must match the bone names exactly. Name the jaw without `.L` or `.R`.
  0:50, 8:00, 12:20, 0:48, 4:15, 5:20, 3:10, 4:30, 8:15, 15:40, 17:20, 21:30; Blender 4.1, 3.6, 3.1)

## Fix automatic weights

- **Automatic weights are a start only.** Correct the parts Blender gets wrong.
- Steps: mesh then rig, Ctrl+P > With Automatic Weights. Weight Paint with Object Data > Vertex Groups to inspect each bone (red 1,
  blue 0). Fix a limb: Tab, L to select linked, back to Weight Paint, Weight 1, Strength 1. Weights > Normalize All stops two bones
  fighting. Tools: Draw, Subtract, Blur, Ramp (gradient), and Weights > Smooth for harsh edges.
- Prop bone (sword, ears): add vertex groups named exactly as the bones, select the piece with L, Assign weight 1, then Remove it
  from the nearby spine groups (`spine.004` to `spine.006` near the ears) so only the new bone controls it. Disconnected collar
  spikes go to the neck bone (`spine.005` was the neck in that deform rig; click through groups to find it).
- Belt trick: select belt and buckle in Edit Mode, P > Selection to split. Body then belt, Weight Paint, Weights > Transfer Weights
  (Data Type Vertex Groups, Vertex Mapping Nearest Vertex, Source Layers By Name, Destination All Layers, Replace), then Ctrl+J to
  join. The belt takes the torso's motion.
- Principle: automatic weights fail on odd proportions or separated geometry; transferring weights from the nearest body vertices
  fixes it.
- Other tools: Unity, Unreal and Godot import weights as they are, so fix them in Blender before export.
- Pitfall: removing from the few nearest bones fixes most fights; doing it for every bone is tedious. Blur and Ramp use is (heard).
  line heard; Blender 4.1 and 3.3, Transfer Weights unchanged in 5.2)

## Cloth cage with Surface Deform

- **One cage carries the weights**: outfits follow a low-poly surface, so there is no per-piece weight painting and swaps share a stack.
- Steps: build a bendable surface mesh around the character (low poly is fine). On the clothes and on the character add Surface
  Deform, Target = the surface mesh, Bind. Then select the surface mesh and the armature, Ctrl+P > With Automatic Weights.
- Principle: only the cage is skinned; every other piece is bound to it, so nothing clips.
- Other tools: no native version in Unity or Unreal; it equals a Wrap Deformer in Maya.
- Pitfall: the author offers a longer tutorial that this note does not cover.

## Squash and stretch lattice

- **Lattice squash** that adds to any rig: two hooks driven by two bones squash the whole character while the other controls work.
- Steps: Add > Lattice under the character, scale it in Object Mode (X, Y, Z) to enclose the mesh. Do not apply the scale and do not
  edit points before attaching. Lattice data: Resolution U, V, W all 2 (4 top and 4 bottom points); Interpolation U, V, W all Linear
  (the default B-Spline lets the mesh break out). Lattice modifier on the character (Strength 1.00). Lattice Edit Mode: select the 4
  top points, F3 > Hook to New Object, name `Squash`; select only the 4 bottom points, Hook to New Object, name `Squash-Anchor`. In
  the armature add two bones `Squash` and `Anchor`, select both, Ctrl+P > Keep Offset to the root bone, Deform off on both. Parent each
  hook empty to its bone: select the hook, then the armature, Pose Mode, only that bone, Ctrl+P > Bone. Parent the lattice object to
  the root (frame 3:00 shows it parented to a bone named `Start`, Parent Type Bone), or the mesh smears when the root moves. Put
  lattice and hooks in one collection `Squash Control` and hide it (hidden items still work). Modifier stack in the owl: Subdivision,
  Armature, Lattice. Lattice above Armature keeps the squash vertical only; below also affects other parts.
- Principle: a low-resolution lattice is a two-handle volume deformer, and bones drive the hooks so animators get normal pose bones.
  Scale the bottom anchor out when the top squashes down to keep volume.
- Other tools: Lattice or FFD in Maya, Cinema 4D and 3ds Max. In three.js or Godot, scale a bone chain or a vertex shader on Y with
  an inverse X and Z scale (a guess, untested).
- Checked in 5.2.2 by script (UV sphere radius 1, lattice 2x2x2 Linear, two Hook modifiers on the lattice, hook empties parented to
  bones `Squash` and `Anchor`): bounding box 2.00 x 2.00 x 2.00 (8.00) at rest; Squash bone moved down 0.5 gives 2.00 x 2.00 x 1.58
  (6.33); the same plus X and Z scale 1.124 on both bones gives 2.25 x 2.25 x 1.58 (8.00). So the volume is kept only when the bones
  also scale X and Z by 1/sqrt(Z ratio). Bones pointing up move along their local Y, so key `location.y` (not Z) on the Squash bone.
- Pitfall: applying the lattice scale or editing points before binding breaks the fit.

## Ragdoll proxy bones

- **Cheap box ragdoll drives the real character**: only proxy boxes are simulated.
- Steps: one Single Bone per rigid body, head and tail covering the proxy, Shift+D to duplicate, bones not connected. Character then
  armature, Ctrl+P > With Automatic Weights. Pose Mode, per bone: Bone Constraints > Child Of, Target = the matching rigid body object
  (Location, Rotation, Scale on, Influence 1.0). Hide the rigid body and constraint collections, play.
- Joint twist: select the thigh bone, Local orientation. Bone Constraints > Limit Rotation, Owner Space Local, tick Limit Z (not Y,
  because the bone is a child of the rigid body and the rigid body's own local Z is the twist axis), Min -15, Max 15 for a knee.
  Repeat per joint; the axis differs.
- Principle: the constraint axis is in the parent's space (the rigid body), so check the rigid body's Z, not the bone's Y.
- Other tools: Unity and Unreal ragdolls use a proxy collider per bone with joints between them.
- Pitfall: connected bones glitch. Auto weights smear a little because the bones are disconnected, which the video accepts. More
  bodies give better joints but cost more.

## Voxel Remesh rig for blobby characters

- **Blob character with plain bones**: no weight painting and no shape keys; the Remesh modifier re-merges overlapping solids.
- Steps: enable Extra Objects (Round Cube, Quad Sphere, Arc 8). A turtle: shell = a round cube with the bottom scaled S Z 0.1; legs,
  tail and head from a capsule (a round cube split along the middle, V to separate, Bridge Edge Loops, Ctrl+R extra loops); eyes
  round cubes; mouth a Torus with the top cut and Grid Fill; Ctrl+B bevel. Join as `Turtle`. Modifiers: Subdivision (viewport level
  2) first, then Generate > Remesh, Mode Voxel, Voxel Size 0.1 then 0.025 for detail (Adaptivity 0, about 4,248 vertices at 0.1),
  Smooth Shading on. Armature: bones along X, Shift+D duplicates, Alt+P and Ctrl+P Keep Offset for controllers, In Front, Display As
  Octahedral. Parent with Ctrl+P > Armature Deform With Empty Groups and rename bones to match the vertex groups.
- Principle: the Remesh modifier re-topologizes after deformation.
- Other tools: nothing direct; a metaball or SDF union in three.js, Unity or Unreal, or simple bones skinning separate meshes.
- Pitfall: no UVs or image textures, since the topology changes every frame. Use gradients, Generated or Object coordinates or
  procedural textures. Expect artifacts; it is heavy, so turn Remesh off in the viewport. Adaptivity above 0 disables Fix Poles.
  The Remesh modifier still has Voxel, Quad and Sharp modes in 5.2.

## Transformation constraint instead of drivers

- **Value remap constraint**: one object's rotation or location drives another with a ratio, no Python or driver editor.
- Gear train steps: Extra Objects > Gears (Shift+A > Mesh). Master gear radius 1 m, 12 teeth. Second gear radius 0.75 with the tooth
  size scaled by the same 0.75 (heard, the transcript garbles it); third radius 0.5, tooth count unverified. Object Constraints >
  Transformation: Target = `Master-Gear`; Map From = Rotation, Mode Auto Euler, Z Min -360, Max 360. Map To = Rotation, Z Source Axis
  Z; swap Min and Max (360, -360) to reverse direction. Ratio: for the 0.75 gear, 1/0.75 = 1.333, so Map From Z Min is typed
  `-360/1.33` (about -271) with Max 360.
- Location to rotation or scale: Map From Location, Z range 0 to 1 m; Map To Rotation, X Source Axis = Z (by default X source drives
  X); Max 360 so 1 m = one turn. Tick Extrapolate to keep turning beyond 1 m. For scale: Map To Scale with min and max (for example
  0.5, or different ranges per axis such as 0.25 and 2).
- Principle: most drivers are a linear remap, which the constraint does with optional extrapolation.
- Other tools: Unity and Godot need a script (`angle_b = -angle_a * (teethA / teethB)`); Unreal a Blueprint multiply.
- Pitfall: Map From is the target object, Map To is the owner; they are easy to swap. Use it for gears, wheels turning as a car
  moves, and sliders.
  current in 5.2 as far as heard)

## Add-ons

- Fit Lattice: automates the lattice fit for squash and stretch (paid). Free route: the lattice entry above.
- Extra Objects (Add Mesh and Curve): Round Cube, Gears, Profile Arrow (free, Blender extension).
- Matrix Display shader by CgCody: dot-matrix LCD material (free forum file).
- Stop-Mo: a free add-on that steps animation for a stop-motion look. How it works is not shown and the link was not found.
- A free worm rig from a mograph course is shown only as a tour of controls (star for eye look, head control, a circle for the
  butt, an antenna control); the download sits behind a paid workshop, so it is not covered.

## Already covered elsewhere

- Shape key basics (Basis, one key, slider, keyframe), shape key rules and the shape key panel: `face-rigs.md`.
- Hard weights with With Empty Groups, Armature modifier above Subdivision, Bone Collections, Bendy Bones segments, bone roll and
  Symmetrize: `bones-and-weights.md` and `use-3d-software/references/rigging-and-weights.md`.
- The general idea of a bone-driven 2D face atlas: `face-rigs.md`; this file adds the image-sequence Offset drivers.

