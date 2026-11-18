# Bones and weights

Method across tools. Blender recipes for a custom armature from one bone, root and torso bones, a skin-modifier armature,
weight paint settings, modifier order and cloth pins are in `use-3d-software/references/rigging-and-weights.md`.
This file adds the meta-rig route, the checks and the deltas from other tutorials.

<!-- skill-navigation:start -->
## Reading Map

- [Bones and weights](#bones-and-weights)
- [Prepare the mesh](#prepare-the-mesh)
- [Fit a Rigify meta-rig](#fit-a-rigify-meta-rig)
- [Bone roll](#bone-roll)
- [Generate and skin](#generate-and-skin)
- [Hard weights and rigid parts](#hard-weights-and-rigid-parts)
- [Weight fixes](#weight-fixes)
- [Naming and mirroring](#naming-and-mirroring)
- [Blender 5.x names](#blender-5x-names)
<!-- skill-navigation:end -->

## Prepare the mesh

- Apply the Mirror modifier first (hover it, Ctrl+A). Both sides need real geometry or weights come out one-sided.
- Apply scale (Ctrl+A > Scale). Put the feet on the ground at Z=0 and centred: select all, G Z to drop, Shift+C to centre the cursor.
 Rigify works from the world origin.
- Armature display: Object Data > Viewport Display, tick In Front, set Display As B-Bone, tick Axes to see roll.
- A bone rotates at its head. The joint sits where the previous bone ends.
- Model joint loops into the mesh (extra loops at elbow, knee and finger). Low-poly meshes need them most.

## Fit a Rigify meta-rig

1. Enable Rigify (Blender 5.x: Edit > Preferences > Get Extensions or Add-ons, search "Rigify"). Shift+A > Armature > Human (Meta-Rig).
2. Never change the meta-rig object scale. In N, keep Scale at 1,1,1.
3. Edit Mode. Set Pivot Point to 3D Cursor and S-scale the whole rig from the feet until the clavicle touches the top of the chest.
   Scale in Edit Mode, never in Object Mode. Switch back to Median Point for local moves.
4. Turn on X-Ray (Alt+Z) and Tool tab (T) > Armature Options > X-Axis Mirror. Edit one side.
5. Place in this order: ankle, toe, heel (heel on the floor, rotate on Z), knee, spine chain, clavicles, upper arm (root at the
   shoulder rotation point, slightly up), elbow, hand, neck base (B box select), jaw, head tip.
6. Fingers: Alt+B box view isolates the hand. Scale the hand bones up. Hide the others with H or Shift+H. Finger joints sit higher in
   the hand than the default. Keep every bone inside the mesh.
7. Snap to volume: set Snap (magnet) to Volume. G a bone head or tail and it lands at the centre of the geometry between the front
   and back faces. Nudge it if it snaps to the back. This needs a watertight mesh. Turn snapping off after.
8. A stylized character can add tail or ear chains: Armature properties > Rigify > Samples in Edit Mode adds spines, tails and
 chains.

Checklist before Generate: Auto Run Python Scripts on (old Blender, Edit > Preferences > Save & Load in 5.x), feet on Z=0,
meta-rig scale 1, roll checked on every limb, bones inside the mesh.

## Bone roll

- Test: Pose Mode, R X X on a finger. It must bend into the palm. Fix roll before IK, symmetry or Generate.
- Recalculate: Edit Mode, select bones, Armature > Bone Roll > Recalculate Roll (Shift+N in 2.8+ and 5.x) with the bending axis.
  One tutorial needed Local +X, another needed Y. Always test the result.
- Thumb: the bones sit about 45 degrees off, so Recalculate gives a wrong bend. Set roll by hand in N > Item > Roll, then test.
- Many bones at once: hold Alt while typing the Roll value. Hover a Roll field and press Ctrl+C, Ctrl+V to copy it across.
- A reversed elbow or a finger that curls the wrong way means wrong roll in the meta-rig. Fix it and regenerate.

## Generate and skin

1. Select the meta-rig. Armature data > Rigify > Generate Rig. Hide the meta-rig (Blender 4+: bone collections replace layers).
2. Delete old vertex groups (Object Data > Vertex Groups > Delete All Groups) and any leftover Armature modifier.
3. Object Mode: select every mesh to deform (skin, clothes, head) first and the generated rig last. Ctrl+P > With Automatic Weights.
4. Keep the Armature modifier above Subdivision Surface. Only Mirror goes before it.
5. Pose Mode: rotate the controllers to test.
6. Loose objects (hair, teeth, brows, shoes): show the DEF collection, select the accessory, shift-select the rig in Pose Mode,
   make the right DEF bone active (DEF-head, DEF-foot, DEF-toe), Ctrl+P > Bone. A controller parent stops the object following the
   deformation. A rigid sandal goes to the toe bone so Foot Roll lifts it.

## Hard weights and rigid parts

- Hard weights suit robots, armour, cut-outs and low-poly shoes. Each vertex gets weight 1 on one bone.
- Blender: Ctrl+P > With Empty Groups, Edit Mode, select the part (L), weight 1, Assign. Or Ctrl+P > Bone for a whole object.
  Quantize 1 in the weight brush options hardens painted weights.
- three.js and Crucible skinned meshes also take one bone per rigid part: weight 1 on one joint, or parent the mesh node to a bone node.
  See `export-to-engines.md`.
- A low-poly or retro style wants hard or two-bone weights. A cartoon-soft or realistic style wants smooth weights and extra joint loops.
- "Bone heat weighting failed" means overlapping or non-manifold parts. Remesh, split into objects or use hard weights.

## Weight fixes

- Select the armature, shift-select the mesh, press Ctrl+Tab for Weight Paint. Click a bone to see its weights: red is full, blue is none.
- Blend Add raises and Subtract lowers. Turn Symmetry X on. F sets radius, Shift+F sets strength. Low strength builds slowly.
- Typical fix: a chin follows the head bone, so remove head weight from the shoulders. Paint across the problem area.
- Rebinding with Automatic Weights resets all painting. To redo chosen bones only, use Weights > Assign Automatic from Bones.
- With the mirror toggle off, the other side stays unchanged. Check by rotating the bone.

## Naming and mirroring

- Left names end in `.L` (Blender also reads `_L` and ` L`). Symmetrize renames to `.R`. Duplicates get `.001`, so rename them.
- Names that search well: head, neck, chest, spine, hip, shoulder, upper arm, lower arm, wrist, palm, fingers, thumb, upper leg,
  lower leg, ankle, foot, `arm IK`, `leg IK`, `elbow IK`, `knee IK`, main controller.
- Finish IK and constraints on the left side first. Symmetrize copies constraints. Then check the pole angles on the right.
- Symmetrize mirrors about the world origin. Keep the spine at X=0.
- Parent with Keep Offset, not Connected. The last selected bone becomes the parent. Hip parents the leg tops. Main controller
  parents the hip and all IK and pole bones.

## Blender 5.x names

- Armature layers are Bone Collections (4.0+). Mapped from the 2.7x "M to a layer" step.
- Rigify is an extension from 4.2. Bone constraints live in the Bone Constraints tab.
- The Auto Smooth checkbox is gone (4.1). Rigs are not affected.
