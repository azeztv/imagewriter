# Creature and stylized rigs

Rigs for stylized animals, dragons, tails, hair and trees: a spine with controller bones, IK limbs, Damped Track chains,
wind on bones and baking for export. Notes cover Blender 4.x and 5.x. Check tags: `heard` means
the voice-over only, `verified` means a frame confirmed it. Base Rigify steps are in
[bones-and-weights.md](bones-and-weights.md). Face shape keys are in [face-rigs.md](face-rigs.md).
Old Blender names are mapped: armature layers and bone groups are bone collections (4.0+), and Rigify is an extension
from 4.2.

<!-- skill-navigation:start -->
## Reading Map

- [Creature and stylized rigs](#creature-and-stylized-rigs)
- [Quick Rigify biped](#quick-rigify-biped)
- [Rigify on a frog or an animal](#rigify-on-a-frog-or-an-animal)
- [Rigify body with a custom face, hair and eyes](#rigify-body-with-a-custom-face-hair-and-eyes)
- [Creature spine with controller bones](#creature-spine-with-controller-bones)
- [IK limbs on a creature](#ik-limbs-on-a-creature)
- [Damped Track chains](#damped-track-chains)
- [Wind on bones without the paid add-on](#wind-on-bones-without-the-paid-add-on)
- [Fix deformation and rigid parts](#fix-deformation-and-rigid-parts)
- [Bake Action before export](#bake-action-before-export)
<!-- skill-navigation:end -->

## Quick Rigify biped

1. Edit > Preferences > Add-ons (Blender 4.2+: Get Extensions), search "rig", tick Rigify.
2. `Shift+A` > Armature > Rigify Meta-Rigs > Human. Scale it to the character, then `Ctrl+A` > Scale.
3. Edit Mode: select the face bones and delete them (Delete > Bones). Turn on X-axis Mirror in the header. Move the bones
   onto the mesh.
4. Armature data of the meta-rig > Rigify panel > Generate Rig. Hide the meta-rig.
5. Select the mesh (`A`), `Shift+click` the new rig, `Ctrl+P` > With Automatic Weights.

- Apply scale before you generate, and edit with symmetry on. Check: heard+seen (Blender 4.x).

## Rigify on a frog or an animal

1. Add the Human meta-rig (or the Wolf preset for a dog). Scale and place it for the animal. Delete the face bones and
   the face bone inside the head. Move the thumb away for four fingers.
2. Put every bone along the body. Roll the forearm and finger bones (`Ctrl+R`) and check the axes so each chain points
   the same way. Fix hands that cross the body.
3. `Ctrl+A` > All Transforms. Make sure `spine.003` and `spine.004` are connected. Generate Rig.
4. Skin: select the meshes, then the rig, `Ctrl+P` > With Automatic Weights.
5. Stop the arm and leg bones from deforming the body: open the DEF bone collection, select the arm and leg DEF bones,
   `Shift+W` > Deform to disable them, parent the body with Automatic Weights, then turn Deform on again for those bones.
6. Weight paint with the Vertex Groups tab and the Item tab to see which bones touch a vertex. Remove the index finger
   from the mouth, reduce the arm, shoulder and thigh spread, clear the arm from a scarf.
7. A hat gets its own bone. Parent it with `Ctrl+P` > Bone (Keep Offset) to a head bone.
8. Eyes: a bone named `DEF-eye.L` with its head at the eye origin, then Symmetrize (`F3`). Apply Mirror on the eye,
   Separate by Loose Parts, parent each eye and its highlight with `Ctrl+P` > Bone. Parent the eye bones to the head bone
   with only the DEF collection visible.
9. Copying a Rigify rig into another file brings extra duplicates. Move the rig and delete the extras.

- Check: heard (Blender 5.0 and 3.x/4.x).

## Rigify body with a custom face, hair and eyes

Use the Rigify body and skip the Rigify face rig. Place your own face bones for more acting control.

1. Generate the body from the Human or Wolf meta-rig with the face bones deleted.
2. Place bones across the face: nose, mouth and a jaw bone. Parent the bottom-of-mouth bones to the jaw bone.
3. Eye aim: a Damped Track on the eye bone, targeting a bone placed in front of the face.
4. Eyes with shape keys: left, right, up and down keys bound to a bone location through drivers. Blink and wide keys
   bound to a central eye bone. Do the same for the eyelashes. Draw a separate layer of blacks for closed eyes.
5. Two ways to close an eye: the lid goes down, or the lid goes up (the anime expression). Add an eye-shrink shape key for control.
6. Hair: place bones roughly along the strands. Convert hair curves to mesh and parent with automatic weights (heavy).
   Add controllers for hair jiggle and extra bones for feathers and ears.
7. Parent rigid parts (horns, teeth, tongue) directly to a bone. Weight the mouth bone only to the lower jaw.

- Check: heard (Blender 4.x). The long-hair mechanism sits in his paid course and is not described.

## Creature spine with controller bones

Use for a dragon, snake or any tail. Auto weights alone do not bend smoothly.

1. `Shift+S` cursor to the centre of the body. Side view (`Numpad 3`). `Shift+A` > Armature > Single Bone, `R 90`.
2. Edit Mode: extrude (`E Y`) along the body, five or six bones at an even distance. Add four more for a curved tail,
   and a head chain.
3. Right-click > Subdivide with Number of Cuts 2 to split each bone into three.
4. Controllers: duplicate one bone for every three-bone chain (`Shift+D`, `S`), pivot Individual Origins. Select the
   controller bones and `Shift+W` > Deform > Disable so they do not skin.
5. Pose Mode: `Shift+Ctrl+C` > Copy Rotation from the controller to the first deform bone. Set Target and Owner space to
   Local Space and Mix to Offset. Select the bones and use `F3` > Copy Constraints to Selected Bones. Repeat per segment.
   Each bone is parented to the previous one, so the rotations add up into a natural bend.
6. Bone tab > Bendy Bones > Segments 3 on all bones (right-click > Copy to Selected). Armature viewport display "As" =
   B-Bone to preview.
7. Select all meshes, the armature last, `Ctrl+P` > With Automatic Weights.

- Check: heard (Blender 4.x). (unverified: the frame at 74:00 shows only the bare armature. "Mix to offset" is read as
  Copy Rotation Mix = Offset.)

## IK limbs on a creature

1. `Shift+A` bone at the limb. Front view: extrude the thigh, shin and foot with clear names (front thigh, front shin,
   front foot).
2. Extrude an IK target bone backward from the foot. `Shift+W` > Deform off on it.
3. Pose Mode: select the target, then the shin, `Shift+Ctrl+C` > Inverse Kinematics. Chain Length 2. If it fails, clear the
   target's parent (`Alt+P`).
4. Select the left-side bones, `F3` > Symmetrize. Do the hind legs the same way (`Shift+D Y` duplicates backward).
5. `Ctrl+P` > With Automatic Weights.
- Weight paint the upper-arm bone so the body is not dragged (`Alt+click` a bone to select it). Parent thighs to the
  nearest body bone. A Corrective Smooth modifier was tried and removed as buggy.

## Damped Track chains

Moving the first bone makes the whole tail follow with a lag. No add-on needed.

1. Pose Mode: select the second bone, then the first. `Shift+Ctrl+C` > Damped Track (the target is the bone ahead of it
   in the chain).
2. Repeat up the chain, one constraint per bone.
3. Set the influence of each to about 0.05, less or more as you like. Rotate or move the first bone and the rest follow.

- Check: heard. (unverified: the influence "five" is read as 0.05, not checked on a frame.)

## Wind on bones without the paid add-on

Windy Armature is a paid add-on sold with the creator's Stylized Asset Suite. Do not buy it. Plain route (inferred by the
note writer, not shown):

1. Build one bone chain per stem or branch. Stems drawn as curves: Object > Convert > Mesh, add the armature, parent the
   stems with Automatic Weights, and parent each leaf to its nearest bone (`Shift+click` the armature, `Ctrl+P` > Bone).
2. Add a Noise F-curve modifier to the bone rotation curves, or use a Damped Track chain, with a different Phase per
   chain. Offset the keys of child bones by 1 or 2 frames.
3. Animate the root freely. The wind sits on top. Animate the Noise Strength for stronger wind.
4. Use the Armature animation checkbox of the Sapling Tree Gen add-on for auto motion on a generated tree, if you use it.

- Check: heard.
- The motion side is in `animate-characters` `references/overlap-acting-and-shot-planning.md`.

## Fix deformation and rigid parts

- Hat, horns, teeth and tongue: parent to a bone (`Ctrl+P` > Bone), never to a control.
- Bones for feather and ear jiggle can sit on extra bones off the head bone.

## Bake Action before export

1. Select all bones (Pose Mode). `F3` > Bake Action (also Pose > Animation > Bake Action).
2. Dialog values seen at 19:26 (Blender 4.1.1, verified): Start 1, End 250, Step 1, Only Selected Bones on, Visual Keying
   off, Clear Constraints off, Clear Parents off, Overwrite Current Action off, Clean Curves off, Bake Data Pose,
   Channels Location, Rotation, Scale, B-Bone and Custom Properties all on.
3. The creator names three options to enable. (unverified: which three. The dialog opened with Visual Keying, Clear
   Constraints and Clear Parents all off. For a game engine, enable them, as in [export-to-engines.md](export-to-engines.md).)
4. A Sapling tree: convert the trunk curve to a mesh and re-parent it to the rig first.
5. For Unreal: export only deform bones with FBX (Armature and Mesh, Smoothing = Face, Only Deform Bones on, Animations
   off), disable Bendy Bones, and unparent the deform bones after baking so nothing stretches.

