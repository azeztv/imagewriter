# The 12 principles in 2D and 3D

Each entry says how the principle works when you draw it (2D) and when you key a rig or object (3D).
Rules hold for any style. The note on style says how the rule changes. Source of the principle set: Thomas and
Johnston, "The Illusion of Life". Worked demos use Rough Animator and Blender.

<!-- skill-navigation:start -->
## Reading Map

- [The 12 principles in 2D and 3D](#the-12-principles-in-2d-and-3d)
- [Squash and stretch](#squash-and-stretch)
- [Anticipation](#anticipation)
- [Staging](#staging)
- [Straight ahead and pose to pose](#straight-ahead-and-pose-to-pose)
- [Follow through and overlapping action](#follow-through-and-overlapping-action)
- [Slow in and slow out](#slow-in-and-slow-out)
- [Arcs](#arcs)
- [Secondary action](#secondary-action)
- [Timing](#timing)
- [Exaggeration](#exaggeration)
- [Solid drawing and solid posing](#solid-drawing-and-solid-posing)
- [Appeal](#appeal)
- [Silhouette and pose reading](#silhouette-and-pose-reading)
- [Worked example: a cube that jumps](#worked-example-a-cube-that-jumps)
<!-- skill-navigation:end -->

## Squash and stretch

- 2D: draw a ground and a ball, and keep the ball's area equal to a reference square in every frame. Falling frames
  stretch along the force (gravity), more near the ground. On contact draw a wide, short squash, and squash more on
  the contact frame. The rebound stretches again, then the ball settles. Eyes and mouth follow the shape. A diagonal
  throw stretches diagonally. Copy frame 1 to the last frame to close a loop.
- 3D: scale the control up along the motion and down across it so the volume stays the same. Use a stretchy rig
  (stretch-to bones) or a lattice or shape key deformer. For a whole jump, stretch the legs and let the head and arms
  trail.
- Style: realistic styles use a few percent. Cartoon styles push it hard. A rigid prop (robot arm) does not squash,
  so show the force with overlap and timing instead.
- Check: hold the contact squash for 2 frames. A first pass looks stiff until timing is added, which is normal.

## Anticipation

- 2D: before a punch, draw the fist moving back and the body folding. Before a jump, crouch. Before a head turn, turn
  slightly the other way. Looking from the screen to a hand: lift the head a little first.
- 3D: add an opposing key 3 to 6 frames before the main move on the same controls. Duplicate the next pose 3 frames
  earlier and set the earlier key to Automatic handles (V). Or use Pose > In-Betweens > Push (Ctrl+E) on the in-between.
- Style: subtle for realism, big for cartoon (Looney Tunes style).
- Motion graphics: anticipation can sit on Rotation, Path or Scale, and the object that anticipates draws the eye when
  several move. Three hold poses were enough to read as tension. Recipes: [motion-design-2d.md](motion-design-2d.md) (entries 5 and 2).

## Staging

- Frame the subject and the target together. Place the point of interest on a third line (rule of thirds).
- Screen direction in Western cinema: left to right reads as forward and powerful. Right to left reads as retreat or
  failure. Reverse it for audiences that read right to left.
- 3D: the same framing through the camera safe frame. Set Camera > Viewport Display > Passepartout to 1.0 so the frame is
  never a guess. Use hard cuts with one camera per shot (see the camera entries in the Blender reference).

## Straight ahead and pose to pose

- Straight ahead: draw frame after frame in order. It is spontaneous and slower, and you can lose the end point. Use it
  for fire, smoke, fluids and loose masses.
- Pose to pose: draw the key poses first (punch: wind-up pose and impact pose), then breakdowns and in-betweens with the
  timing and spacing rules. Hold the final stretched pose, then return to a relaxed pose.
- 3D: key the poses in Constant (stepped) first, then the breakdowns, then switch to Bezier. Simulations are the
  straight-ahead case.

## Follow through and overlapping action

- 2D: draw the body on its own layer first. On a second layer draw the attached part.
  It starts upright and trails as the body moves. When the body stops, it overshoots the rest position and returns.
- 3D: offset the keys of child controls by 1 to 3 frames. Select the head or hand keys and press `G` then `1`
  to push them one frame later. For an overshoot, duplicate the last key 3 frames later and set the original to
  Automatic (`V`). Repeat with `Shift+R`. Add Wiggle Bones for hair and cloth (see [acting-and-faces.md](acting-and-faces.md)).
- Rule: the main mass drives. The attached part is delayed, never independent.

## Slow in and slow out

- 2D: mark 10 ticks on the path. Space the drawings close together at the start (3 frames barely moving), widest in
  the middle, and close again at the stop. The position over time is an S curve.
- 3D: Bezier keys with flat handles at the ends (Auto Clamped, or `Shift+S` > Flatten Handles). Pulled-in handles make
  the move snappy. For an impact, put the steepest slope right before the contact key.

## Arcs

- 2D: plot the path of each joint-driven part (arm, fist, head) as dots on an overlay layer. Put every in-between on
  the arc and keep the limb length constant. A pendulum must not shorten its string. The head returns to rest along an
  arc, not a straight line.
- 3D: Pose Mode, select the wrist, then Pose > Motion Paths > Calculate (Blender 4.2+: Object > Animation > Motion
  Paths). FK arms give smooth arcs. IK paths come out as straight lines, so add a middle breakdown key (for example at
  frame 15) to bend the path.

## Secondary action

- Animate the main action first. Add the supporting action on its own layer or pass.
  Examples: an alien's antenna, a dog's ears when it turns its head, hair when someone jumps, blinks.
  Hands that fiddle while a character talks also count.
- 3D: a separate pass after the body animation (hair, props, fingers, blinks), often as its own action.

## Timing

- Hold more frames near the apex and fewer at the fast bottom. A timing chart is a small tick diagram next to a drawing.
  Evenly spaced ticks mean linear motion. Ticks bunched at one end mean acceleration or deceleration.
- 3D: spacing equals the curve in the Graph Editor. Bunched keys and flat handles are slow. Hold a pose by duplicating a
  key with `Shift+D` (an orange bar between two identical keys marks a hold).
- Frame rate: 24 fps with motion blur, or 24 fps on twos for hand-drawn work. 30 fps without blur or for games. Never
  render 24 fps without motion blur. Beat sync: frames per beat = fps x 60 / BPM (24 x 60 / 160 = 9).

## Exaggeration

- Push the pose so the idea reads. A sleeper that startles needs two exaggerated key poses and few in-betweens.
- 3D: push the pose and the timing on the controls. Pull back when it breaks the rig or the silhouette.
- Style: realistic work pushes the timing and the weight more than the shape.

## Solid drawing and solid posing

- 2D: build the body from forms. The head is a sphere with a direction line and the neck a cylinder.
  The torso is a slightly rounded box and the pelvis a half sphere. Limbs are cylinders and hands are mitten boxes.
  Draw through hidden edges. Without a sense of volume the
  in-betweens of a turning form fail. Shape language: circle reads cute, square reads solid, triangle reads aggressive.
- 3D: clean topology with loops at the joints and a decent rig. Keep the ribcage and pelvis tilted against each other
  (contrapposto). Use a straight line opposite a curve in the pose.

## Appeal

- Appeal comes from solid drawing, a clear silhouette, a strong emotion and readable shapes. The notes give no further
  procedure. Check it with the silhouette test below.

## Silhouette and pose reading

- Hide the interior (fill black, or hide the mesh) and check that the pose still reads. Check the negative space between
  the limbs and the torso.
- Avoid tangents. Do not let one outline just touch another. Overlap or separate them.
- For overlapping shapes in 2D, draw the front outline thicker and the rear line thinner where they meet.
- Check each pose from the side and front in orthographic view (`Numpad 1`, `3`, `5`). Perspective hides drift.

## Worked example: a cube that jumps

An object with no limbs shows every principle.

1. Turn on Auto Keying. Key the start pose and a `Shift+D` hold.
2. View from the side in orthographic. About 5 frames later key a crouch and lean (anticipation).
3. Key the air pose and the landing a few frames later. Make the fall one frame faster than the rise.
4. After the landing, add a few frames and slide the cube a little on X to show momentum. Then duplicate a hold.
5. Look around: at about frames 55 and 60 rotate on Z, hold, and rotate again at about 85.
6. For a big jump onto a platform, set the mid-air pose rotated closer to the final rotation. This removes a flip wobble
   on landing.
7. Set the end frame to the last key (215 in the demo). Turn Auto Keying off.
