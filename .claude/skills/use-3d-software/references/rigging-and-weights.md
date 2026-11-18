# Rigging and weights

Armatures, IK, bone setup, skinning and weight paint.

Reading map
- 5.x names: read first
- Building armatures: Rigify, custom, skin-based
- Bone setup: roll, naming, collections, display
- IK, FK and constraints
- Weights and binding
- Face and mouth rigs
- Rigid and secondary motion

## 5.x names

- Bone layers (M to move) -> Bone Collections (4.0, nested in 4.1). Object Data > Bone Collections, Assign and Remove, eye hides, star solos. Rigify shows only the "ORG" collection for deform bones.
- Armature Bone Settings now carries Deform checkbox, Bendy Bones segments, Roll in N > Item. Alt+click applies to all selected bones.
- Bone Constraints tab is separate from Object Constraints, IK and Copy Rotation for bones go on the Bone Constraints tab.
- Pose Library is asset-based (3.0+): select bones, Asset > Create Pose Asset, F3 "Create Pose Asset".
- Rigify and Simple Renaming Panel: Rigify ships bundled, install others via Get Extensions (4.2+).
- Transfer weights, Armature modifier above Subdivision still holds. Eye or head parts under a Shrinkwrap modifier must have it applied before binding.
- Auto Smooth removal does not touch rigs.

## Building armatures

- **Rigify human in 5 steps**: Enable Rigify. Shift+A > Armature > Human (Meta-Rig). Viewport Display > In Front. Numpad 1, scale the meta-rig in Object Mode (S, X) to fit, Ctrl+A apply scale. Overlays > Wireframe. Edit Mode, pivot Active Element (period) to scale torso bones about the hips, Median for the rest. X-axis symmetry, fix one side. Check from top (7) and side (3). Keep a slight bend in arms and legs in the bend direction because IK needs it. Foot-roll bone to the foot edge. Object Data > Rigify > Generate Rig. Hide the meta-rig. Select mesh then rig, Ctrl+P > With Automatic Weights.
- **Custom armature from a single bone**: Shift+A > Armature > Single Bone. In Front, Names, Axes. E extrude (Z spine, X arms), Right-click > Subdivide for joints, F2 rename, Ctrl+F2 bulk rename. Control bones: uncheck Deform (Alt applies to all selected). Fingers: Shift+D, Ctrl+P Keep Offset to the hand. Snap with Snap to Volume and Ctrl+G. Fingers: Alt+P Disconnect, Subdivide (2 cuts = 3 bones, thumb 2). Parent leg to spine with Keep Offset. Always a tiny bend in limbs. Pivot Active Element rotates from the head, N > Item Length.
- **Root and torso control bones**: Shift+A bone, rotate flat, name `root` (~0.5 long), parent hips (Ctrl+P). Duplicate hips as `control.torso`, parent IK arms to it so hands follow, or to root to stay put. Parent every unparented bone to root with Keep Offset. Shift+Alt+click selects nested bones.
- **Skin-modifier armature**: Apply Mirror, Create Armature in the Skin panel, apply Skin. Ctrl+X dissolve extra bones. Free the root: Alt+P Clear Parent, reselect with root last, Ctrl+P Keep Offset. Delete half the bones, Auto-Name Left/Right, Symmetrize. Mark Root on the chest first. Armature modifier before Subdivision. Pivot Individual Origins curls chains. After adding bones: select bones in Pose Mode, mesh in Weight Paint, Weights > Assign Automatic from Bones.
- **Voxel character armature (3.0)**: In Front, Names, Axes. Snap with Ctrl (Ctrl+Shift finer), limbs parented Keep Offset, roll for jumping jacks, Symmetrize. Parenting: Automatic Weights (may fail on overlapping geometry) or With Empty Groups then Assign Automatic from Bones, or manually L, weight 1, Assign. Rigid parts: Ctrl+P > Bone. Turn Lock Object Modes back on afterwards.
- **Skeleton rig with IK, drivers, switches (2.93)**: Hip > spine > neck > head, legs duplicated, arm Alt+P, Subdivide fingers, eye bone placed with Shift+S Cursor to Selected. Roll in N > Item (Alt for many), X axis as main rotation, test R X X. Centre bones: cursor to world origin, 3D Cursor pivot, S X 0, then Auto-Name Left/Right.

## Bone setup

- **Consistent bone roll**: Pose Mode R X X on one bone to check bend. Edit Mode set Roll with Alt held (type 0, Alt+Enter) to apply to all selected. Pick X or Z and stay consistent. Test with all fingers, pivot Individual Origins, R X X curls a fist. Transform orientation Local skips the double X. Do this before IK and symmetry.
- **Left and right naming, symmetrize, pose mirror**: Select all non-centre bones, Names > Auto-Name Left/Right (.L), Symmetrize (.R). Names must end in .L or .R. Delete the right side before re-symmetrizing. Pose Mode X mirror, or Ctrl+C then Ctrl+Shift+V paste flipped. Alt+G/R/S reset. Simple Renaming Panel adds a suffix to many bones, Ctrl+F2 type Bones > Set Name. Drivers must be re-copied to .R after symmetrize and pole angles checked.
- **Bone collections (4.0+)**: Object Data > Bone Collections > +, select bones in Edit Mode, Assign, double-click to rename, drag to nest (4.1). Put IK targets and helpers in a hidden "mechanism" collection.
- **Bone display**: Object Data > Viewport Display > Display As: B-Bone. F3 "Scale B-Bone" (Quick Favorites Q, Ctrl+Alt+S) to make IK controls larger.
- **Bendy bones**: Select arm bones, Bone > Bendy Bones > Segments ~6 to 10 (Alt for all). Display as B-Bone.
- **Posing tips**: Individual Origins + R X X curls fingers or tails. Ctrl+C, Ctrl+V, Ctrl+Shift+V flipped. Three keyed poses (0, 20 flipped, 40) make a dance.

## IK, FK and constraints

- **Two-bone IK with pole target**: Edit Mode duplicate the foot bone as `ik.leg.L`, uncheck Deform, Alt+P so it is no child of any leg bone (else a dependency loop spins the leg). Pose Mode select the IK bone then Shift-select the calf, Shift+I > To Active Bone (or Bone Constraints > Inverse Kinematics). Chain Length 2 (0 = whole body). Parent the IK bone to the heel (Keep Offset). Copy Rotation (Ctrl+Shift+C) from the IK bone onto the foot bone. Pole: extrude from the knee along Y, Alt+P, name `target.leg.L`, parent to heel Keep Offset, Pole Target Armature + bone, Pole Angle ~90 (-90 for arms). If the hand ends backwards add a slight elbow bend in Edit Mode. Parent target.leg to the foot and untick Inherit Rotation on the foot so the knee follows the toe (common advice is not to). Alt+click selects a bone hidden inside another. Build one side, delete the other, Symmetrize.
- **Foot rig with roll and limits (2.92)**: IK leg controller (duplicate shin, Alt+P, chain 2, pole). Foot Copy Rotation of the controller. Pivot bones via Switch Direction: IK pivot foot parented (Keep Offset), toe pivot with IK chain length 1, heel pivot, roll in and roll out bones where the foot bends, parent heel > roll out > roll in > toe pivot. Main control at the heel: Copy Location to heel bone. Heel Copy Rotation + Limit Rotation X (0 to 45). Toe pivot limited X (-45 to 0). Roll bones Copy Rotation Y with Limit Y (0 to 45, -45 to 0). Lock location on children. Local space, bone roll aligned, F3 Copy Constraints to Selected Bones. Chain length 1 makes a bone point at its controller.
- **IK/FK switch**: Three chains (def, ik, fk) on separate collections and colours. Deform bones get two Copy Transforms constraints (Ctrl+Shift+C). A `switch` bone with Limit Location (Local, Y 0 to 1, Effect Transform) drives the second constraint's influence via a driver (bone Y location, Local). Copy and paste the driver to every deform bone. Deform only the middle chain. Snapping IK to FK with mutual constraints makes dependency loops. Variant: expression `var*10+1`, Limit Y -0.1 to 0.1.
- **Spine IK, eye aim, constraints**: Spine IK controller Chain Length 3 plus Copy Rotation on head. Eye aim bone with Damped Track. Stretchy bones: Alt+P, control bone at the tip, Ctrl+Shift+C > Stretch To.
- **Auto IK**: Pose Options Auto IK with chain length by scroll. IK bone with Deform off, Alt+P, Shift+I, chain 2 or 3, pole target and angle.

## Weights and binding

- **Binding**: Mesh then armature last, Ctrl+P > With Automatic Weights. "Bone heat weighting failed" means overlapping parts, so remesh, retopo or split objects. With Empty Groups then Edit Mode L, weight 1, Assign per vertex group (Remove from All Groups first). Redo chosen bones: Pose Mode select bones, Weight Paint, Weights > Assign Automatic from Bones. Rebinding with Automatic Weights resets weights. Head parts (head, eyes, hat): armature in Pose Mode with only the head bone, Ctrl+P > Bone. Rigid trick: scale the mesh to 0.1 with Individual Origins, auto-weight, scale back x10.
- **Weight paint settings**: Select armature, Shift-select mesh, Ctrl+Tab. Alt+click a bone to view weights. Tool > Options: Auto Normalize, Mirror. Front Faces Only off paints through, Falloff Sphere avoids painting through thick parts, Projected paints through. F radius. Weight 1 with a bone takes weight from others, 0 removes. Strength 0.1 to 0.25 builds gradually (0.25 for heels). Alt+drag gradient. Edit > Lock Object Modes off, Ctrl+click armature bones to pick them. Masks: 1 face, 2 vertex, 3 pose, or hide (H) the back half. Quantize 1 for hard weights. Wireframe overlay. Check by moving bones away.
- **Modifier order**: Armature modifier above Subdivision and Solidify (only Mirror before it). Apply modifiers before the Armature one only. Applying Subdivision after it breaks the mesh.
- **Cloth pin to a bone**: Skirt Ctrl+P With Empty Groups, assign the top ring to Hips, set cloth Pin Group to Hips.
- **Face and hair bones with Shrinkwrap constraint**: Duplicate a bone, snap ends with Ctrl+G, parent to the head with Keep Offset. Mouth control bone parented to head. Bone Constraints > Shrinkwrap, Target = hidden helper mesh, Align to Normal axis Y. F3 "Apply Selected as Rest Pose". Helper: duplicate eye and mouth parts, Solidify, Ctrl+J, delete back faces, hide in viewport and render. Distance offsets from the surface.

## Face and mouth rigs

- **Quick face rig with bones**: Snap bone ends to face vertices, head bone via Shift+A, Ctrl+F2 batch rename with .L, Symmetrize, Alt+P, Ctrl+P Automatic Weights, Armature above Subdivision. Weight paint the large head bone with Auto Normalize.
- **Easy mouth rig**: Head with mouth pocket and separate teeth. Armature bones: root, head, jaw (Active Element pivot), lip top, lip bottom. Parent Keep Offset, Deform off on root. Ctrl+P With Empty Groups for head and teeth. Lock Object Modes off, Weight Paint with Auto Normalize and symmetry, jaw 1, lips 1, shared centre 0.5. Lip bottom Copy Location + Copy Rotation of the jaw (Local, After Original). Limit Rotation on jaw (Local, X 0 to 30, Effect Transform). Shape keys: Basis, purse, smile (Range Min -1 gives frown). Control bones with drivers: Add Driver, Single Property Transform Channel Local, expression x5 or x10. A "shut" bone drives top lip influence.
- **Audio-driven puppet mouth (2.83)**: Shape Key Basis and "mouth open". Empty with a Z key, Graph Editor > Channel > Sound to Samples (Key > Bake Sound to F-Curves before 4.1). Add sound in the Video Sequencer at frame 1, Audio Scrubbing, Sync Frame Dropping. Shape key Value driver on empty Z (World Space) x ~3. Render with AAC or MP3. Isolate the voice.
- **Mii-style creator**: Parts as GLB in a grid with an index display, a part-switcher GN picks the object by a picker, one bone per part, each switcher parented to its bone so only the body is weighted, shrink-wrapped makeup via a vertex group "shrink". No exact values.

## Rigid and secondary motion

- **Wiggle Bones 2 (free)**: Pose Mode, N > Animation, Head affects location and Tail rotation, stiffness, collisions. Bake with F3 Bake Action (Visual Keying, Overwrite) on a duplicated action.
- **Rigid-body ragdoll**: Object > Rigid Body > Add Active, Connect Rigid Bodies (F3) Point, Chain By Distance.
- **Ready rigs**: Mixamo (Auto IK, Mixamo-control add-on), Blender Studio free rigs with face controls and pose libraries, Rokoko for video mocap. See `animation-and-nla.md`.
