# IK, FK and controls

Blender recipes for two-bone IK with a pole, the foot rig with roll and limits, the IK/FK switch with drivers, spine IK and
Auto IK are in `use-3d-software/references/rigging-and-weights.md`. This file holds the method, the choice rules and the
Rigify and ready-rig controls.

<!-- skill-navigation:start -->
## Reading Map

- [IK, FK and controls](#ik-fk-and-controls)
- [IK limb recipe (short)](#ik-limb-recipe-short)
- [Control bones and the master bone](#control-bones-and-the-master-bone)
- [IK or FK per shot](#ik-or-fk-per-shot)
- [Rigify controls: switch, snap, foot roll](#rigify-controls-switch-snap-foot-roll)
- [Bone collections](#bone-collections)
- [Ready rigs](#ready-rigs)
- [Pose tools](#pose-tools)
- [Measured in the creator's rig files](#measured-in-the-creators-rig-files)
<!-- skill-navigation:end -->

## IK limb recipe (short)

1. Name the chain bones: `upper arm.L`, `lower arm.L`. The bones must be parent-child connected.
2. Duplicate the wrist (or ankle) bone as `arm IK.L`. Press Alt+P > Clear Parent. Enlarge its look with Ctrl+Alt+S.
3. Extrude a pole bone from the elbow joint with E and Y (behind for the elbow, in front for the knee). Alt+P > Clear Parent.
4. Pose Mode, select the lower bone. Bone Constraints > Inverse Kinematics. Target the armature and `arm IK.L`.
   Untick Use Tail. Set Chain Length 2 (0 moves the whole body). Set the Pole Target to the armature and the pole bone.
5. Set Pole Angle to 90 or -90 and adjust until the limb returns to its rest pose. The value changes with bone roll.
6. Add Copy Rotation from the IK bone to the same bone so the hand or foot rotates.
7. Reset with A, then Alt+R, Alt+G, Alt+S.

Fixes:
- The leg does not move as a chain: the bones are not connected. Rebuild the top bone from the hip, use Subdivide (W or right
  click) to split one bone into two, move the middle joint to the knee, and rename.
- A hand ends backwards: add a slight elbow bend in Edit Mode, then flip the pole angle.
- A bone without "IK" in its name was not found in the search box. Rename first.

## Control bones and the master bone

- Control bones (IK, pole, master) have Deform off. Do this before you skin.
- Master bone: Shift+C, Shift+A in Edit Mode, G to the floor in side view, R 90 Enter, enlarge with Ctrl+Alt+S.
- Parent the hip, the IK bones and the pole bones to the master with Ctrl+P > Keep Offset in Edit Mode.
  In Pose Mode the master must move, rotate and scale everything. The hip must move the legs.
- Give controls a larger display size than the skeleton. Animators click them.

## IK or FK per shot

- IK: pose by moving a hand or foot controller. The limb follows. Use the pole bone for the elbow direction.
  Use IK to hit exact positions: a drum hit, a hand on a sword, planted feet.
- FK: pose by rotating joint by joint. Use FK for loose swinging and dragging arms, such as a character falling onto a bed
  where the arms drag behind and overshoot.
- Mixed is allowed: a two-handed sword with one IK hand and one FK hand.
- In IK, moving the shoulder leaves the hand in place. In FK the whole arm follows.
- IK arcs look mechanical. Add breakdown keys or check motion paths. FK arcs come free but lose end-point accuracy.
- 2D drawn animation uses the same split. Planted contact poses behave like IK. Follow-through on a loose limb behaves like FK.

## Rigify controls: switch, snap, foot roll

- Select a limb controller, press N > Item. The Rig Main Properties panel shows the IK/FK slider (0 = IK, 1 = FK), Snap FK to IK,
  Snap IK to FK and Stretch.
- Switch mode mid-animation: key the pose at frame 10 in IK. Go to the next frame and click Snap FK to IK. Change the slider and key it.
  Key both the IK and the FK values.
- Foot Roll: rotate the foot roll control on local X (R X X) to lift the heel. Drag the knee or elbow ball (pole) to aim it.
- Fingers: scale the finger controllers to curl them, or rotate them.
- Auto Keying on, press I, and Shift+Up jumps 10 frames to lay keys while you move controllers.
- A hand with no IK influence follows the arm. With IK = 1 the hand stays put while you move the body.
- Snapping IK to FK with mutual constraints on a hand-built switch makes dependency loops. Use a script or Rigify.

## Bone collections

- Blender 4.0+ replaced bone layers with Bone Collections (Object Data > Bone Collections, nested from 4.1). Mapped from "layers".
- Keep helpers (IK targets, pole bones, mechanism bones) in a hidden collection. Keep deform bones in a hidden DEF collection.
- While animating, show only IK/FK plus fingers or hair when needed. Fingers and hair look unposed while their collection is hidden.
- CloudRig rigs show a `N` sidebar CloudRig tab with layer buttons (IK, IK secondary, FK, fingers, hair, clothes, face, stretch).
  Shift+click shows several.

## Ready rigs

- Blender Studio free rigs, for example "Rain" (CloudRig, with face controls). Download from the Blender Studio characters page,
  open the `.blend`, allow script execution for trusted sources so the CloudRig panel works.
- Pose Mode needs the armature selected, or nothing selected. A mesh selection greys it out. Switch with Ctrl+Tab.
- Practice flow: A to select all controllers, I to key, turn on Auto Keying, then G, R, S the controllers.
- Mixamo and Rokoko mocap clips retarget onto a humanoid. See `export-to-engines.md`.

## Pose tools

- Relaxed hands: curl the fingers a little with R. Default hands look stiff.
- Mirror a pose: box select the finger bones on one hand, select the Dope Sheet Summary row, Ctrl+C. Select the other hand's bones,
  key them once with I, then Ctrl+Shift+V pastes flipped. Plain Ctrl+V pastes unmirrored. This also works for feet.
- Alt+G, Alt+R, Alt+S clear position, rotation and scale to rest.

## Measured in the creator's rig files

free tutorial files (Arm and Leg IK Rigging, Robot Arm), opened read-only in Blender 5.2:

| Rig | IK on | Chain | Pole angle | Use Tail | Stretch | Extra |
|---|---|---|---|---|---|---|
| Arm | Hand, target `Wrist`, pole `Elbow` | 2 | -90 | off | on | Copy Rotation from `Wrist` to Hand, World space, Replace |
| Leg | Foot, target `Ankle`, pole `Knee` | 2 | +90 | off | on | Copy Rotation from `Ankle` to Foot |

- The IK target and pole bones have no parent and Deform off. Every other bone deforms.
- The mesh has Subdivision Surface above Armature in the stack and one vertex group per deforming bone.
- The robot arm has no armature at all: Base > Arm 1 > Arm 2 > Wrist > Claw 1 and Claw 2 are parented objects, each
  with a Bevel modifier. Rotate each part around its origin.
