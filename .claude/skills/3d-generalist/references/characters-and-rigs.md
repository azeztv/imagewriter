# Characters, Rigs and Expressions (`characters-and-rigs.md`)

A 3D video holds attention when the character reads as a living person with clear silhouette, grounded feet, natural
elbows and readable facial or head expressions.

## 1. Choosing the right character style

- **Realistic Cutaway Worker:** a realistic human at 1.8 m scale wearing a high-contrast
  yellow hard hat, bright orange hi-vis jacket with grey reflective bands, dark trousers, work boots and gloves. The
  loud orange/yellow colour pops immediately against calm snow, brown soil, grey stone or blue water.
- **Realistic Storytelling Cast:** generated in Blender with **Human Generator
  (HumGen3D)**, slightly muscular build (very skinny limbs look goofy when bent), 1-click **Rigify** rig, and built-in
  facial expression shape keys.
  - **Viewport performance rule:** turn **Hair Visibility OFF** in the viewport while rigging and animating; enable it
    only when picking hair colour and for the final render. Particle hair drops viewport playback from 30 fps to 8 fps.
- **Retro / Stylized Low-Poly:** 300 to 1,500 triangles, unlit power-of-two texture
  atlas (`512x512` / `1024x512` with `Standard` / `neutral` view transform), hard `100%/0%` auto-normalized weights,
  and 2D UV-stepped (`Constant`/`STEP`) or 3D recessed eye/face rigs. When building a custom low-poly character from a
  2D reference image or turnaround, load the companion skill `model-characters`
  (`../model-characters/SKILL.md`) and run `scripts/read_character_ref.py` + `scripts/check_character.py`.

## 2. Rigging and the 5-control workflow

Whether animating in Blender (`Rigify`) or through a declarative shot builder (`shared/anim` in headless Blender ->
Three.js `shotClip.js`), focus on five primary controls:

1. **Torso / Hips root box:** carries the centre of mass. Never leave the hips frozen while the arms flail.
2. **Left & Right Foot IK controls:** lock the soles to the ground, steps, ramps or platforms. Never animate knees
   directly; let leg IK solve knee bend from the foot target and pole vector.
3. **Left & Right Hand IK controls + Elbow poles:** place palms directly on the tool, rope, block or snowball. Keep
   elbow pole targets **low and close to the ribs**; winged-out sideways elbows look robotic immediately.
4. **Head / Neck control (`looks`):** leads every turn, reaction and inspection.
5. **Facial expression sliders (Shape Keys):** keyframe emotion blends across beats:
   - *Calm / Happy* (`0.3 -> 0.7`) during setup or normal routine.
   - *Surprise + Unpleasant Surprise* (`0.0 -> 1.0` over 4 to 6 frames) when a failure, wind gust, collapse or flood hits.
   - *Slightly Disgusted / Confused* (`0.6`) during recovery as the character looks left and right.

Free locomotion clips already retargeted to one rig: [codepawl/100style-glb](https://huggingface.co/datasets/codepawl/100style-glb) (810 clips, 100 styles, CC BY 4.0). Robots with working joints: [codepawl/menagerie-glb](https://huggingface.co/datasets/codepawl/menagerie-glb) (79 MuJoCo Menagerie robots, licence per robot on the card).

## 3. Retargeting and clip hygiene

- **Sources:** combine native rig clips (`Idle_Breathe`, `Walk`, `Kneel_Work`, `Sit_Enter`, `Sit_Idle`, `Sit_Exit`),
  Quaternius Universal Animation Library (`ual:Walk_Loop`, `ual:Walk_Carry_Loop`), and Mixamo FBX clips (`dig_shovel`,
  `push_heavy`, `Gangnam`).
- **World rotation deltas:** retarget onto the character skeleton by world rotation deltas per bone and verify with a
  round-trip pose check (under 0.3 degrees drift).
- **Inspect every retargeted clip in a still first:** some clips twist the shoulders or raise both arms unnaturally
  after retargeting. Render a still of any new clip before putting it in a film.
- **Clear cached mixer state on handoff:** when switching between two `AnimationMixer` instances on the same skeleton
  (for example a scene mixer and a shot mixer), clear the cached bone results on the outgoing mixer so out-of-order
  frame renders never keep a stale pose.
