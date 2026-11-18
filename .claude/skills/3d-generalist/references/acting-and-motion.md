# Character Acting, Motion and Physics (`acting-and-motion.md`)

Technical accuracy (no floating, no foot sliding) is only half of non-slop 3D animation. The other half is **acting,
anticipation and staggered timing** so the character never moves like a linear robot.

## 1. Anti-stiffness and comedic / reaction acting

From our study of 19M–20M view 3D Shorts:

- **Never freeze all joints on the same frame:** when blocking pose-to-pose or blending clips, offset the head, torso
  and arms by **3 to 6 frames**. If the character stops walking or finishes sitting down, let the head turn 4 frames
  early and let one hand settle a few frames after the hips.
- **Lead every notice or turn with the head (`looks`):** when a problem starts (water leaks in, wind hits, smoke fills
  the cave), whip the character's head toward the problem **4 to 6 frames before** the body turns or steps back.
- **Reaction and slapstick beats on `"But <failure>"` rounds:**
  - Never transition linearly from calm work to a failure state.
  - Insert a **0.2 to 0.5 s anticipation/reaction beat**: a sudden flinch, catching balance (`"Whoa"`), or a 4-frame
    upward head look right before falling or getting knocked over.
  - When a fall or gag happens (falling through a roof into a hearth, or tipping with a cabin), exaggerate the landing
    pose (spread feet, face-plant 3 frames after the structure hits, patting out a singed backside—funny and bloodless)
    followed by a slow recovery where the character props up on one hand and looks left, then right, in confusion.
- **React to danger like a real person:** when a flood, rockfall or collapse comes, the character gets out of the way
  first (runs or walks to the bank/ledge) and watches the failure from safety.

## 2. Grounded feet, walks, steps and turns

- **Walk speed matches stride:** time every walk by `distance / stride_speed` (keep normal walks under **1.8 m/s**, and
  loaded cart pushes near **1.4 m/s** with `Push` upper body layered on `Walk` legs). Faster walks slide the toes.
- **Stop with feet together (`arrive: "together"`):** a default walk cycle stops mid-stride with the front toe 0.5 m
  ahead of the hips—putting a foot straight through a closed door, hearth or stool. Start the walk at the phase that
  ends on the passing pose so both feet plant together within 15 cm of the hips.
- **Turns over 45 degrees get a pivot beat:** blending a sharp turn directly into the first stride surges the hips and
  skates the planted foot. Give any turn over 45 degrees a **0.35 s stand/pivot beat** on the balls of the feet before
  walking. Round path corners into smooth arcs.
- **Kneel-to-walk and sit-to-walk transitions:** never go straight from `Kneel_Work` into a walk (it drags the toe 7 cm).
  Insert a **0.3 s stand-up idle** (`blend: 0.3`) between kneeling and walking. For seats (`sit_on`), walk up side-on to
  25–29 cm ahead of the seat, turn, and sit; keep post-exit turns under 30 degrees so the shin clears the stool.
- **Both feet on their own surface:** on steps, blocks or slopes (ramps 30 degrees or less), place the root on the
  carrying foot's height and use leg IK to lift the other foot and knee onto its own surface so neither foot hangs in
  mid-air over an edge. Make standing blocks at least `0.8 m x 0.56 m`.
- **Walk starts keep the hips up:** blending from an idle into a walk can dip the hips for a few frames (one case dropped a
  1.8 m character's hips to 0.48 m). Outside kneel, sit and crouch beats, hips stay above about **0.65 m** for a 1.8 m
  character, and a check fails any frame below it.

## 3. Hands, tools, props and baked physics

- **Work at arm's length (under 15 cm):** kneel right at the fire ring with hands in the kindling; stand beside a crank
  with the shoulder level with its axle (never behind it where the far half of the turn is 0.8 m away).
- **Fit the worker to the machine, never the machine to his reach:** keep chains, levers and spouts where the real
  machine puts them, and walk the character to them.
- **Both hands have a job:** a one-handed pour or interact clip often leaves the free arm sticking straight out
  sideways. Put a second grip point on the load (for example palm up under the bucket base) so both arms read naturally.
- **Every piece travels from the hands:** stones, blocks, roof timbers, furs and lamps start in the character's hands
  and travel to their seat. When building many pieces, speed the sequence up as a **time-lapse** (`fit: "timelapse"`),
  but still carry and set each piece by hand.
- **Deterministic baked physics (`f(t)`):** loose planks, falling stones, carts and drifting timber move by real rigid-body
  physics (Rapier in JS or Rigid Body in Blender), baked to keyframes ahead of capture so any frame `t` renders
  identically in any order.
- **Grip mechanics live in one place:** for pick-up and put-down without a pop, dynamic parenting, two-handed props, heavy
  lifts and finger posing, read `rig-characters` `references/props-grip-and-contact.md`.
- **Hand to face needs its own elbow:** a default arm IK pole points the elbow down and back, which is right for
  handles and loads but lays the forearm across the chest when the hand goes to the nose, mouth or brow. For any
  grip at face height, aim the elbow pole **low and forward** (about 0.3 m down and 0.4 m ahead of the elbow) and
  keep the forearm midpoint at least **3 cm** off the chest.
- **Pick the finger shape for the action:** fist for handles and ropes, **pinch** to hold the nose (index curled,
  thumb folded in to meet it within about 2 cm, other fingers relaxed), **flat palm** with fingers together to cover
  mouth and nose. A fist on the face reads as a punch, an open relaxed hand reads as a wave.
- **Bend the knees to reach low:** to set something on the floor or a low course, the character squats or kneels
  with a straight back. Folding in half at the waist with straight legs looks wrong at once.
- **Tools face the worker:** an oven mouth, a hatch, a tap or a crank faces the side the character works from, not
  the camera. If the camera needs to see it, move the camera, never turn the tool.
- **Loose objects come to rest:** a dropped bag, plank or stone settles within about a second and then stays still.
  Damp spin and sliding (angular and linear damping, a sleep threshold) and check the last frames of each bake for
  leftover rotation. An object that keeps spinning on the floor reads as a bug.
