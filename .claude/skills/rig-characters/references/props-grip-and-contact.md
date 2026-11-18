# Props, grip and contact (`props-grip-and-contact.md`)

How a character holds, picks up, carries, hands over and puts down a prop in any software. Entries marked `unverified`
were heard in a tutorial but not confirmed on screen or in docs: use them as hints, test before relying on them.
Names are current; the name the tutorial showed is in brackets.

<!-- skill-navigation:start -->
## Reading Map

- [Props, grip and contact (`props-grip-and-contact.md`)](#props-grip-and-contact-props-grip-and-contactmd)
1. [1. Core idea (any software)](#1-core-idea-any-software)
2. [2. Blender (5.x)](#2-blender-5x)
3. [3. Maya](#3-maya)
4. [4. Unreal Engine (5.x)](#4-unreal-engine-5x)
5. [5. Unity](#5-unity)
6. [6. Godot (4.x)](#6-godot-4x)
7. [7. Spine 2D (Pro 4.x: IK and transform constraints are not in Essential)](#7-spine-2d-pro-4x-ik-and-transform-constraints-are-not-in-essential)
8. [8. Cascadeur](#8-cascadeur)
9. [9. Craft](#9-craft): weight, the C-to-S lift, finger posing, grip tension
10. [10. Checklist for a grip shot](#10-checklist-for-a-grip-shot)
11. [11. Sources](#11-sources)
<!-- skill-navigation:end -->

## 1. Core idea (any software)

1. **The prop has its own control.** Give it a bone, an empty, a locator or a null. Never glue the mesh straight to the hand
   control: the prop control is what you key to change the grip inside the hand without breaking the wrist.
2. **Place the prop in the hand first, then link.** The relative offset is baked at the moment you link (Child Of inverse,
   Unreal attach then reset, Cascadeur Outliner drop). Move the hand afterwards to test.
3. **Dynamic parenting = a switch on the link, not a re-parent.** A normal parent cannot change mid-shot. Use a constraint
   whose weight you key (Blender Child Of Influence, Maya Blend Parent, Unity multi-parent weight, Spine constraint mix).
   Key the weight 0 on the frame before and 1 on the grab frame, with stepped (constant) interpolation on the weight.
4. **One hand drives, the other follows.** The dominant hand drives the prop, the prop drives the support hand, so every
   edit happens in one place. Constrain the support hand to a grip point on the prop, not to the other hand.
   Keep the support hand keyable (hide the driver, not the control).
5. **Light prop: hand is the parent. Heavy prop: prop is the parent and the hands follow.** For a heavy prop you animate the
   prop path with the effort, and the hands stay glued to it. Pose the hands on the prop for the whole lift first.
6. **No pop on the switch frame.** The prop's own channels must hold the same world pose that the hand gives on the grab
   frame (hold key under the constraint), and on release you bake the held world pose into the prop's own channels
   (visual transform) before the weight drops to 0. The hand should be nearly still on the switch frame: a hand that
   touches the prop pauses for a frame or two anyway.
7. **After release the prop needs its own keys**, or it snaps back to where it was before the constraint.
8. **Blend IK or weights in and out, never snap.** About 0.3 s from 0 to 1, with the first half held at 0 while the pose
   changes from idle to the hold pose.
9. **Test by moving the hand, then scrub the switch frames one at a time.** Judge the contact frame, not the scrub: a
   scrub through a constraint switch always looks glitchy.

## 2. Blender (5.x)

### Child Of switch for pick-up and put-down (verified)

Works on an object or a pose bone. Use a bone of the character rig (the hand IK control, for example `hand_ik`) as the target.

1. At the grab frame N, pose the hand on the prop. Key the prop's location, rotation and scale (`I` over the field).
   Keep identical keys on every frame the prop sits still before the grab.
2. Prop: Object Constraints tab > Add Object Constraint > Child Of (pose bone: Bone Constraints tab > Add Bone Constraint).
   Target = the armature, Bone = the hand control.
3. Click Set Inverse once, on the frame where the hand and the prop are in the final grip. The prop stays put.
   Clicking Set Inverse again on other frames stacks offsets and throws the prop away.
4. Key Influence = 1 at N, and Influence = 0 at N-1. Set the Influence curve to Constant interpolation
   (Graph Editor, select the curve, `T` > Constant) so there is no blend frame.
5. Hold: while the constraint is on, keep the prop's own keys equal to the grab-frame values (key them again at R-1).
6. Release at frame R. Key location, rotation, scale and Influence 1 at R-1. At R, with the influence still at 1, run
   Pose > Apply > Visual Transform (object: Object > Apply > Visual Transform), key location, rotation and scale, then set
   Influence 0 and key it. The prop now stays where the hand left it. Do the visual transform before lowering the
   influence, or the prop gets a double transform.
7. Headless / script equivalent of steps 3 and 6: `constraint.inverse_matrix = (armature.matrix_world @ pose_bone.matrix).inverted()`
   evaluated on the grab frame; for the release, force `influence = 1` on frame R, update the view layer, read the
   evaluated `matrix_world`, write it to `prop.matrix_basis`, key it, then key `influence = 0`.
   In Blender 5.x actions are slotted: `action.fcurves` no longer exists, so reach the curves (to set Constant) with
   `action.layers[0].strips[0].channelbag(obj.animation_data.action_slot).fcurves`. Proved headless on Blender 5.2: a cube
   picked up, carried and put down with a 0 mm jump on both switch frames and no slide in the hand.
- A ball that is thrown needs its own keyed flight after R, or it returns to its start position. A frame-keyed
  enable (eye icon) works the same as Influence.
- In production the Child Of can be replaced by Copy Transforms with a constraint-switching tool (`unverified`, one
  creator's habit).
- Child Of takes its inverse from the frame at which the constraint was added or the target was set: add the
  constraint while on the frame where it must be 1.

### Handing a prop between carriers (verified)

Add one Child Of per carrier. For a hand-off: constraint A has Influence 1 until frame F-1 and 0 from F; constraint B
has Influence 0 until F-1 and 1 from F (all constant). Add each constraint on the frame where it becomes active, and
snap the prop's own keys to the carrier on the frame before and after the switch. Add a jump arc by keying Z higher
between two distant carriers. One constraint is active at a time, so the rig is not heavier.

### Dynamic Parent add-on (verified for panel labels; support for the current Blender version unverified)

Free add-on, 3D viewport sidebar tab Dynamic Parent with Create, Disable and a Clear dropdown. Select the new parent
(hand), then Shift-select the prop (active, last), press Create at the grab frame; select only the prop and press Disable
at the release frame. For a holster select the holster bone, then the gun, Create. Do not move with both hand and gun
selected (double transform). The prop must not have a normal parent. If the second hand pops, remove the keyed
constraint and Create again on a clean frame.

### Two-handed prop with empties (verified)

1. Set the prop origin to the handle (Tool tab > Options > Transform > Affect Only: Origins, move, turn it off; or Edit mode,
   Shift+S Cursor to Selected, Object > Set Origin > Origin to 3D Cursor).
2. Pose the dominant hand control on the handle. Add Empty > Plain Axes at the hand (the prop control). Select the empty,
   Shift-select the armature, Pose mode, select the hand IK bone, `Ctrl+P` > Bone.
3. Select the prop, then the empty, `Ctrl+P` > Object (Keep Transform). Moving the hand now moves empty and prop.
4. Support hand: add a second empty at the grip point. On the support hand IK bone add Bone Constraints > Copy Location
   and Copy Rotation, both with Target = that empty. Parent the empty to the prop (empty first, then prop, Keep Transform).
5. Fingers: Pivot Point = Individual Origins, rotate the finger bones round the handle (`R`), pose the index separately,
   thumb behind. Rigs with finger bone collections (CloudRig) show them through the rig tab.
6. To let go with the support hand set both constraint influences to 0 (key them). Needs IK arms; use the elbow pole
   targets to place elbows. A small prop is easier to pose scaled up.

### Hide-swap fake grab (`unverified`)

Duplicate the prop, parent the duplicate to the hand bone (`Ctrl+P` > Bone), key viewport and render visibility so the
duplicate shows from the grab frame and the original hides. Only for a prop that stays in the hand to the end.

## 3. Maya

- **Parent constraint with Blend Parent keys (verified: the Constrain menu and Parent Constraint Options exist in current Maya).**
  Select the hand control, Shift-select the prop, Constrain > Parent. In the Channel Box key `blendParent1` on the prop (the
  attribute label is `unverified`): 0 on the frame before the grab, 1 on the grab frame; 1 on the last held frame, 0
  on the release frame. Key the 0 a frame before the 1 or the prop slides to the hand. Animate the flight after release.
- **Heavy prop leads (verified).** Pose the hands on the prop for the whole lift. Select the prop (driver), Shift-select the
  hand IK control, Constrain > Parent > options: Maintain Offset on, Translate All, Rotate All, Weight 1, Add. Key Blend Parent
  0 before the grab, 1 at the grab. Hidden hands can stay unanimated.
- **Two-handed weapon chain (names verified, Maintain Offset values `unverified`).** Base pose first. Create > Locator, group it
  (`Ctrl+G`). Snap the group to the prop pivot with a Maintain Offset OFF parent constraint, delete the constraint. Same for
  the locator and the off-hand control. Then: prop parent-constrained to the main hand control (Maintain Offset ON), prop
  drives the group, group drives the off-hand control. Put the locator in a hidden Display Layer so a stray key cannot
  break it. A referenced rig will not let you re-parent the hand under the prop (error: cannot change hierarchy): constrain.
- **Three-part prop setup (names verified, numbers `unverified`).** Locator A parent-constrained to the dominant hand control
  (FK preferred for arcs), locator B child of A, prop constrained to B: key B to change the grip. Locator C child of the prop
  at the off-hand contact point (slide it along a staff). Locator D at the pivot, locator E at the IK control as a child of D,
  IK control parent-constrained to E, D point-constrained to C. A pre-made rig that space-switches the prop makes a cycle
  error: break the connections or duplicate the geometry. A human wrist bends down only about 45 to 50 degrees (spoken, unverified).
- **Staff drives both hands, per-hand weight (`unverified` for animBot names).** Hand constraint locators parent-constrained
  to the staff (Maintain Offset ON); IK handle parent-constrained to a control under each locator; staff constrained
  to a hips locator. Turn off Enable Rest Position on every constraint, so nothing snaps when a weight changes. To let go
  with one hand, key that hand's weight (`<prop>W0`) 1 then 0 on the next frame. To re-grab, match the hand locator to the staff
  position on the grab frame (World Space paste in animBot, or `Constrain` to the new grip) and rotate the hand to the new grip.

## 4. Unreal Engine (5.x)

- **Attach a prop in Sequencer, then Control Rig (`unverified`).** Level Sequence with the character (Metahuman) and the prop. On the
  prop track: plus > Attach > Metahuman, component Body, bone `hand_r`; click reset to zero the transform; stretch the
  Attach track over the shot; eyeball the prop into the hand. Right-click Body > untick Filter asset by skeleton > Bake to Control Rig.
- **FK to IK switch on the Metahuman control rig (`unverified`).** On the top-level `global` control find the `arm left` / `arm right`
  switch. Delete all keys on the switch tracks first, then tick IK. The hand control becomes a square and the elbow follows.
- **Override finger poses from a pose library (`unverified`; the name "Pose Library" could not be checked in the manual).** Delete the finger control keys of that
  hand, reset them, paste a saved gun-trigger or barrel pose. Build and save your own pose assets.
- **Chain with an additive offset rig (`unverified`).** Right hand drives the prop. Left hand IK control: constraint plus > Parent > the prop;
  drag the green key to the start to hold the whole shot. To fix clipping add a control rig plus > Additive, key the right hand IK
  on that layer. Always move the driver hand, never the prop alone.
- **Mannequin weapon socket (`unverified`).** Skeleton asset `SKM_Manny`, arm bone (the video showed `weapon_r`, heard only), Add Socket,
  set the mesh's parent socket. Rotate the socket by -90 degrees if the gun lies sideways. Custom meshes must use or retarget to the mannequin skeleton.
- **Animation Blueprint hand IK with Two Bone IK and a virtual bone (verified on screen).** Stack: `Hand IK Retargeting` >
  `Copy Bone` > `Two Bone IK` per hand. Hand IK Retargeting: Hand FK Weight 1.0, IK bone `ik_hand_gun`, alpha from the animation
  curve `DisableHandIKRetargeting` with scale -1 and bias 1. Virtual bone under the weapon bone from `ik_hand_l` to `ik_hand_r`
  named `VB ik_hand_l_weaponSpace`. Copy Bone: source = that virtual bone, target `ik_hand_l`, copy translation and rotation,
  scale off, Component Space. Two Bone IK right: IK bone `hand_r`, effector `ik_hand_r` in Bone Space, joint target `lowerarm_r`
  in Bone Space, joint target location Y 50. Left: `hand_l`, effector `ik_hand_l`, joint target `lowerarm_l`, Y -50.
  Drive both alphas from float variables (0 when disabled, else 1, clamped) set in the thread-safe update, and gate on an
  `ItemEquipped` bool. A 45 degree aim offset can pull the hand back: delete those poses in the pistol aim offset.
- **Left-hand FABRIK to a weapon marker (verified on screen except tip and root bones).** Scene component `LeftHandIK` on the base
  weapon, moved per weapon. Anim graph: `Local To Component` > `FABRIK` > `Component To Local`; Effector Target = right hand
  bone, Effector Transform Space = Bone Space, Effector Rotation Source = No Change, Precision 1.0, Max Iterations 10,
  Tip = left hand, Root = left shoulder (heard). Compute the effector transform with `Transform to Bone Space` from the
  component's world transform. Eject with F8 in play and move the component live to tune it per weapon.
- **Ease the alpha (verified).** Timeline `TL_IKAlpha`, length 0.3, keys (0, 0), (0.15, 0), (0.3, 1); feed it to the FABRIK alpha.
  Move `Set Is Holding Weapon` to the end of the spawn event, after the weapon is attached.
- **Smooth the hand target (verified).** `VInterp To` and `RInterp To`, Delta Time from `Get World Delta Seconds`, Interp Speed 60,
  store the results in smoothed variables, feed them into `Make Transform`. If shaking remains, move the marker away from the body.

## 5. Unity

- **Two-handed weapon with Animation Rigging (verified against current docs).** Install the Animation Rigging package. On the root with the Animator add
  Rig Builder. Child GameObject with the Rig component, assigned in Rig Builder > Rig Layers. Under it one object per hand with
  Two Bone IK Constraint: Root = shoulder, Mid = elbow, Tip = hand, Target = a child of the gun (a grip node), Hint = an
  object behind the elbow to stop pigeon-wing elbows. Fit the grip in play mode, copy the Transform (component menu >
  Copy), exit and paste. Add Rig Transform to an object that is a constraint target and moves in the editor. If the gun is far
  the off hand will not reach: move the gun first. Parenting the gun under the clavicle to stop bounce while running is
  advice, `unverified`.
- **Reach and grab on top of idle (verified).** Component menu > Auto Setup from Tip Transform makes Target and Hint. Clip
  `grab item`: animate only the constraint weight 0 to 1 over about 1 s; Animator transition by a trigger, no exit time; set the
  target position from code, then SetTrigger. A second constraint placed below the first in the hierarchy (order is
  hierarchy order) and a second clip animate the pull-back; one target cannot be both set by code and keyed. Animation
  Events reparent the item to the hand bone at the start and destroy it at the end of the clip.

## 6. Godot (4.x)

- **BoneAttachment3D [BoneAttachment] (verified against class reference).** Right-click the imported model > Editable Children
  (menu item in Godot 4 `unverified`). Under the `Skeleton3D` [Skeleton] add `BoneAttachment3D`, set `bone_name` to the hand bone, add
  the prop (`MeshInstance3D` [MeshInstance]) as its child, place and scale the child (offsets live on the child). Tune the
  offset in side view against every animation that matters. One node holds one bone: add another for the off hand.
  To swap hands at runtime, change `bone_name` or reparent the prop (`unverified`).

## 7. Spine 2D (Pro 4.x: IK and transform constraints are not in Essential)

- **Two-handed item (verified against the user guide).** Item bone under the root so it does not move with the hands. Two child
  bones `hand on item front` and `hand on item back`. Per arm New > IK Constraint on the upper and lower arm bones with the hand
  bone as target. Add a Transform constraint on each hand bone with the item bone as target and a rotation offset (Match fills
  the offset). Hide the item and mix 0 in setup, make an animation `item setup` with mix 100, play it on a higher track over walk or idle.
  IK takes one or two bones per constraint; constraints apply top to bottom (drag, or Reset); reset the order after adding one.
- **Item follows the hand (verified).** Transform constraint on the item bone, target `hand front`, mix translate X, Y and rotate;
  off in setup, on in an animation `item in hand` on a higher track. Equip: duplicate it, shift the frames, key all mixes (shortcut
  `unverified`). Mix values can be keyed to blend in and out.
- **Aim rig with the rifle as master (verified structure, percentages `unverified`).** The four arm IK targets are children of the
  rifle bone; an aim IK on the rifle bone; a transform constraint (Match first, mix about 10 percent) lets the rifle drift toward
  the aim; torso, neck and head lean through transform constraints on a limit bone (about 20 to 30, 15 and 20 percent, tuned per character).

## 8. Cascadeur

- **Link a prop without rigging (verified against the guide).** Timeline: add a track for the prop. File > Import Fbx/Dae > Add model
  (rigid mesh; scale it down, it can arrive 100 times too big). Place it in the hand by eye, then drag the mesh onto the hand
  joint in the Outliner. Test with Auto Posing, close the fingers with finger auto posing, then run the AI inbetweener.
- **Two-handed hold (verified against the Constraints page).** Link to the dominant hand, place both hands. In Point controller mode select the
  dominant hand's point controller, select the off wrist, Commands > Constrain > Points; activate it on the selected timeline interval
  in Object Properties > Constraints (red circles show). The hold only works on the selected frames. For imported
  animation use inbetweening and set arm interpolation to linear.

## 9. Craft

- **Weight (`unverified`, opinion).** Two knobs: the delay before the prop starts to move shows its weight, the number of frames the
  character needs to overcome it shows strength. Light prop: lift with no delay. Heavy prop: a pause or struggle first, then
  accelerate from rest. A strong character lifting a boulder with no effort looks like polystyrene: show one beat of weight.
  For a throw, drag the prop behind the hand in the anticipation. Add sound, camera shake and dust where frames are missing.
- **The C-to-S lift (`unverified`).** Pose path S, then C (bent over, heavy prop), back to S, open S standing. Lead the lift with hips
  and core. Lean the prop on the body or rest it on the leg. At the hardest moment the heel stays planted, the toes lift and the foot slides
  back to catch the centre of gravity. On set-down the chest and core go down first, then the body settles. Move the prop backward toward the
  centre of gravity a little before it rises. Keep a slight arm bend, straight arms look robotic. Use IK hands while a hand rests on the prop.
- **Regrip.** Hands touch down, shift to a better anchor, then lift. Fingers close as the hand shifts, thumb and fingers lag then settle.
- **Finger posing (`unverified`).** Relaxed is not straight: curve the fingers slightly, close the gaps, thumb in a little, wrist line not perfectly straight.
  Group the last three fingers; spread fingers read as tension. Fist: tips converge on a line of action, do not in-between
  relaxed to fist, add a second pose near the end; knuckle controls move little until the fingers really close. Smallest finger closes first and
  opens last. Overlap by at most one frame (pinky early, index and thumb late). On a surface do not keep fingers straight: spread them,
  reverse the tip joint slightly to sell compression, add easing on the contact. Mocap with only thumb, index and pinky: paste your own finger poses.
- **Grip tension (`unverified`).** Avoid the death grip. Key finger flex, loosen on the carry, re-grip on a change of direction or weight, and keep
  small offset keys on the prop control. A constraint-only grip reads stiff.
- **Mocap with a prop (`unverified`).** Poses first on an additive layer, then jitter, then contacts. Bake FK to IK on the contact.

## 10. Checklist for a grip shot

Run these on the switch frames and on the held frames before showing anyone:

- [ ] At the grab frame the hand is within 3 cm of the prop surface (measure hand control to nearest surface point).
- [ ] No pop on the switch frame: the prop world position jumps less than 1 mm from the frame before to the switch frame and from
      the last held frame to the release frame, while the hand is still.
- [ ] The prop does not slide in the hand: its position in the hand's local space is constant on every held frame (under 1 mm).
- [ ] After release the prop stays put for 10 frames while the hand leaves.
- [ ] Switch frame keys: weight 0 on the frame before, 1 on the grab frame, constant interpolation on the weight.
- [ ] Fingers wrap the surface: no finger through the prop, thumb on the other side, no death grip.
- [ ] Weight reads: delay, effort, settle on set-down. Heavy prop: it drives, the hands follow.
- [ ] Support hand stays on its grip point and can still be keyed.
- [ ] Scrub the clip at real speed with the prop visible and hidden: the hand shape tells the story alone.
