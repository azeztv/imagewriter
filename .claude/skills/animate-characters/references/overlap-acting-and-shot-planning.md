# Overlap, acting and shot planning

Hair, tail and wind motion, reference-driven acting, and the order of work for a short animated shot. Notes come from
Blender tutorials. Rig set-up for tails, wind bones and Damped Track chains is in
`rig-characters` `references/creature-and-stylized-rigs.md`. The principle itself is in [principles.md](principles.md).

<!-- skill-navigation:start -->
## Reading Map

- [Overlap, acting and shot planning](#overlap-acting-and-shot-planning)
- [Overlap on hair and tails by hand](#overlap-on-hair-and-tails-by-hand)
- [Overlap with shape keys on hair](#overlap-with-shape-keys-on-hair)
- [Tail and wind on bones](#tail-and-wind-on-bones)
- [Wind without the paid add-on](#wind-without-the-paid-add-on)
- [Acting from reference](#acting-from-reference)
- [Plan a shot, then block and polish](#plan-a-shot-then-block-and-polish)
- [Cinematic shot lessons](#cinematic-shot-lessons)
- [Test small before a series](#test-small-before-a-series)
<!-- skill-navigation:end -->

## Overlap on hair and tails by hand

- Do not draw or pose hair strands straight. Give them a curve in the direction of travel.
- The tail drags. When it loses velocity and changes direction, switch it to the opposite pose.
- When the body comes back down, drag the end of the tail back behind. Do not just rotate the whole hair as one piece.
- Screenshot the frames and check frame by frame.

## Overlap with shape keys on hair

1. Make one shape key where the hair pulls back as the head moves.
2. Make a second key where it follows through in the opposite direction.
3. Repeat the two with a lower influence each cycle, so the hair settles to zero.

## Tail and wind on bones

- Animate only the head bone and let the tail bones follow. A Damped Track chain does this with no add-on. See the rig
  reference.
- Windy Armature is a paid add-on by the same creator (sold with his Stylized Asset Suite). It adds wind to a selected bone
  chain: pick the chain (`Ctrl+L` selects it), choose "template 1, 2 or 3" (each shares one global scale, speed and
  strength), and set influence per bone. Trunk first as its own chain, then each branch. Animate the first bones freely
  and the wind rides on top. Keyframe the strength for stronger wind. To flip the direction, rotate the bones 180 degrees
  in Edit Mode (`Ctrl+R`).
- Do not buy it for this. Use the plain route below.

## Wind without the paid add-on

Plain Blender, built from the same ideas. (inferred by the note writer, not shown in the videos)

1. Pose the chain (trunk, branch, hair, lamp cord) as bones. One chain per branch.
2. Offset the keys of each bone by 1 or 2 frames from its parent, so the motion travels up the chain.
3. Add a Noise F-curve modifier to the bone rotation curves. Use a different Phase or Offset per bone so the bones do not
   move together. Details are in [timing-and-graph-editor.md](timing-and-graph-editor.md).
4. For a loop, use Cycles on the keys or bake the result (see the rig reference, Bake Action).
5. Keep the tips straight with a small rotation or a shape key.
6. For a stepped look, add Stepped Interpolation with the same step as the rest of the shot.

## Acting from reference

- Film yourself doing the action with a phone on a tripod, animate from it, then push it past reality with squash and
  stretch (for example when excited). Without reference the body mechanics are weaker. (heard)
- Review the reference frame by frame in a review app (SyncSketch, or a draw-over site) and load it at the same frame
  rate as the shot (25 fps in one note). Find good reference, then extrapolate from it.
- Keep strong contrast between poses, especially in jumps. A running cat bobs up and down.
- When no reference exists (an arm and a guitar reacting to a cat), make it up carefully.
- Run cycle on a long route: animate the cycle in place, then move the character along the route. Break the monotony with
  a log jump. To slow down, reduce the stride step by step, slow the root, lean over and put the hands on the knees.

## Plan a shot, then block and polish

1. Pick the idea and a simple story beat (a dance, then the character stops, notices a dog and sits). No tight story at
   first. Improvise per scene.
2. Collect reference for every beat. Film yourself for beats with no clip.
3. Block the poses first for rhythm. Watch the hip and chest subtlety between frames.
4. For a character entering the frame, hide the feet and plan the path with cube markers on the trajectory.
5. Polish for flow. Fix hair that intersects clothes last. Hands on the face are tricky, so check contact.
6. For a mouth use shape keys for the smile, the closed mouth and the vowels A E I O U.
7. Reuse the set-up of scene one for other shots with the camera rotated or zoomed.

## Cinematic shot lessons

- Expect the first block to look awful. Refine it. When a scene does not work, test alternatives and remake it from
  scratch.
- Plan a set piece (the dragon dodges towers before the castle) instead of the plain version.
- Keep a scene under about 10 seconds, or switch the angle halfway. Vary the camera mid-scene (side to front) for retention.
- Orbit camera with shake: an Empty named "track", the camera parented to it, the Empty rotated over time. In the Graph
  Editor (`Ctrl+Tab`) select the Z location curve, `Shift+H` to hide the others, Modifiers tab > Noise on location Z and
  rotation X and Z.
- Depth of field with a focus Empty: Add Empty (`F2` rename "focus"), place it at the subject. Camera Depth of Field on,
  F-stop low (about 1.4, the only setting that matters), Focus Object = the Empty.
- Lighting and colour are decided in the blockout before the character comes in (see the NPR reference for the look).

## Test small before a series

- Make short pieces with feeling (a fight or an emotional moment), see which get traction, then double down. Animate on
  twos. Plan smears and sword trails. Write down why a failure failed.
