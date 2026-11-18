# Camera, Lighting and Cinematic Finish (`camera-and-lighting.md`)

Even simple kitbashed scenes look like a high-budget studio animation when the camera, character lighting, Depth of
Field and shutter motion blur work together.

## 1. Camera rules for 3D Shorts and explainers

- **One set, one continuous camera on cutaway builds:** keep under **1 hard cut per 10 seconds** (0 to 0.4 cuts/10 s).
  Frequent location cuts (1.9 to 2.6 cuts/10 s) confuse viewers and cause Shorts swipe-aways.
  - *Exception:* when the closing payoff names real distant places (*"from Madagascar to Hawaii"*), use a fast **sideways
    whip pan** (sliding laterally so the back of the cutaway slab never shows) to land on an instant landmark icon.
  - *Hard cut rule:* when the character must go somewhere the set cannot show (around a hill to a cliff top), walk him
    past the frame edge, place both cut keys inside a **single frame interval** (so no intermediate frame renders
    halfway), and walk him in.
- **Inside one set, change the angle with a move, not a cut:** a smooth dolly or arc of 0.6 to 1.2 s keeps the viewer
  oriented. Never cut to a reverse angle (more than 90 degrees around the subject). Check every frame of the camera
  path: a jump over **0.3 m or 15 degrees** in one frame that is not a planned cut in the shot list fails.
- **Eye-tracked camera for character storytelling:** in Blender or Three.js, add a `Track To` constraint (or damped
  look-at target) aimed at the character's **eye (`eyeball.R`) or upper chest**, with keyframed **Influence**:
  - Keep influence around `0.4 to 0.7` during close emotional reactions or dialogue.
  - Ramp influence down to `0.0` over 8 to 15 frames when a wide physical event (a cabin tipping over, a bridge
    collapsing) needs the whole set in frame.
- **Smooth camera spacing:** never place camera keyframes 2 or 3 frames apart. Space camera keys at least **5 to 8
  frames apart** (or use critically damped springs / smoothstep curves) so the frame never stutters.
- **Frame named parts straight on:** when the voice names a technical part and pops up its 3D leader-line label, point
  the camera at it and yaw slightly so the part reads as a 3D solid and the label panel covers nothing. Hold the framing
  until the label fades out (1.5 to 2 s after the word); never start panning to the next beat while a label is still up.
- **Viewport Passepartout (`1.0`):** in Blender (`1080x1920` at `30 FPS`), set Camera `Passepartout` to `1.0` so everything
  outside the vertical 9:16 frame is blacked out while staging. Use `0.99` instead when you still need to select things
 outside the frame.
- **Why a move works (camera on a path, rebuilt and checked in Blender 5.2):**
  - **Orbit with a locked target = parallax.** Camera on a curve, aim at a separate target empty: the subject stays
    centred while ears, backpack and background slide across it, which is what reads as depth
 (, measured in our rebuild).
  - **Speed is a choice.** Default Bezier starts slow and stops slow; use it when the stop is the point. For shots cut to
    music, Linear on camera and target gives constant speed, so the flow is not broken at each cut
. Ease only the last key if the camera must settle
. Linear on the camera but Bezier on its target looks wrong: match them
.
  - **A bend needs a curve, not a third key.** Three linear keys give a harsh turn at the middle key; put the camera on a
    path with preview resolution 64 and keep the distance to the subject steady (no far, close, far)
.
  - **Motivated handheld.** A walking operator gives the motion its reasons: eye height about 1.7 m (gravity on), a slow
 steady push in, a pause, a fast pass, a settle. Record it by hand, then
    bake and smooth (about 30 smooths removed the jitter, 10x less in our test) instead of keying every pose
.
 - **Lens choice.** 20 mm for walk-through depth and a wide opening reveal,
 30 mm to get close to a single subject without leaving it; re-check the
    framing after any lens change, 85 mm cropped our subject hard. Clip Start 0.01 for close passes.
  - **Reveal by cut or by move.** Change shot with one camera and a second path whose influence swaps in one frame, instead
 of piling up cameras.
 - **Format.** 21:9 and 60 fps made the dolly feel cinematic and smooth (,
 ). Depth of field: focus on an object that is inside the frame, then lower
 the F-Stop.
  - Same move in three.js, Godot, Unity, Unreal: `use-3d-software/references/animation-and-nla.md`, Camera.

## 2. Bright daylight + Spine-tracked character fill light

- **Bright, clear daylight first:** use a real scanned daytime HDRI sky (`Poly Haven` / `BlenderKit` afternoon sky) with
  soft directional sun shadows. Never use murky dark film lighting.
- **Visible bases in every shot:** every structure (especially distant towers or night stress tests) must show a lit rock,
  island or ground base with waterline detail so it never looks afloat in the dark.
- **Spine-tracked Area Light (Character Fill):** when a character sits inside a cabin, climbs down a well, crawls
  through an igloo tunnel or stands under a roof cutaway, global sun light leaves his face and torso in shadow.
  - Place a dedicated soft **Area Light** (or Three.js `PointLight` / `SpotLight` with soft falloff) near the character
    and bind a **`Track To` constraint to his `spine` / `Hips`**.
  - Keyframe the light's height to follow him when he falls, kneels or climbs so his face, yellow helmet and orange
    jacket stay bright and readable on every frame.

### Sunlight as the subject (shafts, stripes, golden hour)

Lessons from a 10 s elevated-metro shot that took three preview rounds before it looked lit (the user, 2026-11-08):

- **Face the sun.** "Sunlight shining in" means contre-jour: the camera looks toward a low sun behind the structure,
  so shafts and shadows come toward the lens. A sun behind the camera gave a flat, front-lit frame with no visible light.
- **Check the shadow geometry before promising it.** Stripes through ties, blinds or leaves depend on the sun angle
  and on what else blocks it. At 8 degrees the 1.5 m deck girders and tie thickness blocked every ray, and stripes
  only appeared near 20 degrees or more. Render one still at the planned sun angle before building the move.
- **Preview volumetric light in Cycles.** EEVEE gave flat grey shade and no beams. Cycles at 960x540, 28 samples,
  OpenImageDenoise, 4 bounces and 1 volume bounce took 5.5 s a frame on an RTX 3060 and showed the real look.
- **Haze has no visible edge.** See `use-3d-software/references/environments.md`, global fog box, edge check.
- **No untextured boxes in frame.** Plain grey fill buildings read as unfinished at any distance. Give distant ones a
  texture and window rows.
- **Leave room for the exit.** A passing vehicle must clear the frame before the shot ends if the beat is "it
  recedes". Count it: length / speed in seconds. A 64 m train at 22 m/s fills 70 frames, so cut it to three cars.
- **Read the sheet from the final mp4**, not from separate test stills. The encode, grade and motion blur change what
  the frame shows.

## 3. Depth of Field (DoF) and the Finish Pass

- **Keyframed Depth of Field:** turn on Camera Depth of Field and keyframe `Focus Distance` per beat (or bind focus to
  the active part / character eye). A softly blurred background separates the character and cutaway from dense trees and
  passing vehicles, instantly removing the flat "raw OpenGL viewport" look.
- **180-degree shutter Finish Pass (`ShutterPass`):** render final outputs with:
  1. **Motion blur:** accumulate **6 sub-frames** across a 180-degree shutter (`ONE / ONE` linear accumulation on RGB
     only—never `THREE.AdditiveBlending` with alpha weight, which squares the weight and darkens the frame by half).
  2. **Bloom:** thresholded strictly above linear `1.6` so only sun glints, fire and glowing air pockets bloom.
  3. **Vignette & Film Grain:** a light vignette and fine frame-seeded noise to prevent 8-bit MP4 banding.
