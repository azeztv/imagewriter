# Mechanical rigs and 2D cut-out rigs

Rigs with no skin: rigid parts that rotate at real joints, or flat drawn parts that stack in depth.

Ready jointed robots to study or reuse: [codepawl/menagerie-glb](https://huggingface.co/datasets/codepawl/menagerie-glb) has 79 MuJoCo Menagerie robots as GLB with their joint hierarchy kept (licence per robot on the card). Read the joint axes and limits from a real arm before rigging your own.

## Reading Map

- Mechanical rig without bones (Blender)
- Mechanical rig with bones
- 2D cut-out rig: plan the layers
- Cut-out in Blender
- Cut-out in Godot
- COA Tools (Krita layers into a Blender cut-out rig)

## Mechanical rig without bones (Blender)

Use it for a robot arm, a crane, a clock or any rigid machine.

1. Select all objects. Ctrl+A > All Transforms. The rest pose is zero location and rotation, scale 1.
2. For each joint: Edit Mode, select the joint geometry (L over a sphere, or the two faces at a hinge). Shift+S > Cursor to Selected.
   Tab out. Object > Set Origin > Origin to 3D Cursor. For a symmetrical part use Origin to Geometry.
3. Lock channels in N > Item with the padlocks. Click and drag down to lock all location and scale. Unlock only the joint axis:
   elbow only Y, wrist only Z, ball joint none (double-tap R for trackball), claws only Y.
   Locks also make Alt+G, Alt+R, Alt+S reset to the rest pose without moving the part.
4. Parent in chain order, child first and parent last (yellow outline is active): Ctrl+P > Object (Keep Transform).
   Parent each segment to the one below it down to the base. Both claws can parent to the same wrist in one step.
5. Join rigid sub-parts that move together with Ctrl+J, active object last.
6. Reset the pose: A, then Alt+R, Alt+G, Alt+S.

Keep the transform pivot on Median Point so origins, not the 3D cursor, drive rotation. H hides a part, Alt+H shows it.
Do this before animating. Animate the objects like normal ones.

## Mechanical rig with bones

- Use a bone per joint with hard weights, or Ctrl+P > Bone for each rigid part. This exports to engines as a skinned or node rig.
- Use a bone when the engine needs a skeleton (Unity Generic, Godot Skeleton3D, glTF skin). Use object parenting when the engine
  imports node hierarchies as they are.
- A piston or a scissor lift needs a constraint: Damped Track on both halves aimed at each other, or an IK bone pair.
- Add limits (Limit Rotation, Local space) so the animator cannot break the hinge.

## 2D cut-out rig: plan the layers

- Draw the character in parts on separate layers: head, jaw, eyes, hair front and back, torso, upper arm, forearm, hand, thigh,
  shin, foot. Draw each limb part longer than it looks so joints overlap and no gap shows when it bends.
- Name layers like bones: `upper_arm.L`, `forearm.L`. Put far-side limbs on layers behind the body.
- Put the pivot where the joint is. Mark it on the layer or note its pixel coordinates.
- Paint mouth shapes and eye states as separate layers or as an atlas (see `face-rigs.md`).
- Krita (free): Layers panel, one paint layer per part, export each layer as a PNG with the Export Layers script
  (Tools > Scripts). Verify the menu name in your Krita 5.x build.

## Cut-out in Blender

1. Import each layer as a plane: Add > Image > Images as Planes (enable the bundled add-on "Import Images as Planes").
   Set Shader to Shadeless (Emission in Eevee or Cycles) and Blend Mode Alpha Blend or Hashed.
2. Space the planes slightly apart along Y so they do not z-fight. Order follows the drawing order.
3. Set each origin to its joint (Shift+S > Cursor to Selected, Object > Set Origin > Origin to 3D Cursor).
4. Parent in chain order like the mechanical rig. Rotate on one axis only (the view axis) and lock the others.
5. Or build an armature viewed from the front. Weight each plane 1 to one bone. This also exports as a skinned glTF.
6. A Grease Pencil v3 character (Blender 5.x names) can also be rigged with an Armature modifier. Parent with Ctrl+P > With Empty
   Groups, then assign layers or strokes to groups.

## Cut-out in Godot

- Godot 4 has Skeleton2D and Bone2D nodes. Add Skeleton2D, add Bone2D children for each joint, then Sprite2D parts under them.
  Use a Polygon2D with bones and weights when a limb must bend smoothly.
- Add an IK chain with SkeletonModification2D (Godot 4.x) and animate bone rotation in AnimationPlayer.
- Rest pose: set it with Skeleton2D > Set Rest Pose after the layout is right.
- Z order: use each Sprite2D `z_index` or child order. Far limbs sit behind the body.
- Flip a character by scaling the root node on X by -1.

## COA Tools (Krita layers into a Blender cut-out rig)

1. Paint each body part on its own Krita layer and export the parts as cropped PNGs.
2. Install the add-on from disk. Turn off Emulate 3 Button Mouse, because Alt is its bone-assign key. Click "To View".
3. Create New Sprite Object (one container per character), then Import Sprite and pick all PNGs. Place them roughly.
4. Draw order is each sprite's Z value: far leg and far arm negative (-5, -10), torso 0, hips between, head 9, near arm 10.
5. Armature: a root bone at the hip, extrude bones along the spine and each limb, with a slight bend at knees and elbows
   so IK bends the right way. Make IK chains with the COA Create IK Bone operator (end bone selected last). FK gives a
   better hand arc than IK in this test. A hip that rotates alone: duplicate, flip, parent with Ctrl+P > Keep Offset.
6. Bendy limbs: in Edit Mode select the sprite's border loop, Triangle Fill (Alt+F), close the loop, delete the frame
   vertices, Subdivide twice where it bends. In Edit Armature select the bones and Alt+right-click the mesh to bind it.
   Bind the torso to all bones that should move it. Keep these meshes low poly for game engines.
7. Replacement parts (hands, mouths): paint the variants at the same size side by side in one PNG strip, set Tiles in
   the COA panel and key Tile Offset with I. Equal boxes keep the offset from jumping. Re-importing a replaced sprite
   failed in the video; the workaround was a new sprite object.

Steps 5 to 7 are reconstructed from noisy French captions: test each one before relying on it. The Godot section above
is general method, not from a tutorial.
