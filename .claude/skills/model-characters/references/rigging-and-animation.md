# Low-Poly Character Rigging, Weight Painting, Face/Eye Rigs & Animation

This reference distills Parts 9 to 11 of a low-poly character series plus its eyes video and animation video—covering skeletal rigging, hard/flat weight painting, secondary hair/skirt bones, 2D UV-offset facial rigs, 3D inset low-poly eyes, and cyclic animation—and maps every technique across **Blender**, **Three.js**, and **Crucible**.

<!-- skill-navigation:start -->
## Reading Map

- [Low-Poly Character Rigging, Weight Painting, Face/Eye Rigs & Animation](#low-poly-character-rigging-weight-painting-faceeye-rigs--animation)
- [1. Skeletal Rigging & Joint Placement (Part 9)](#1-skeletal-rigging--joint-placement-part-9)
- [2. Low-Poly Weight Painting & Secondary Bones (Part 10)](#2-low-poly-weight-painting--secondary-bones-part-10)
- [3. 2D UV-Stepped Face Animation Rig (Part 11)](#3-2d-uv-stepped-face-animation-rig-part-11)
- [4. 3D Recessed Low-Poly Eye Rig (eyes video)](#4-3d-recessed-low-poly-eye-rig-eyes-video)
- [5. Cyclic Low-Poly Animation Workflow (animation video)](#5-cyclic-low-poly-animation-workflow-animation-video)
<!-- skill-navigation:end -->

---

## 1. Skeletal Rigging & Joint Placement (Part 9)

### 1.1 Choosing the Right Skeleton
- **Blender (`Rigify Basic Human`):**
  - Enable the built-in `Rigify` addon (`Edit -> Preferences -> Add-ons -> Rigging: Rigify`).
  - Spawn **`Add -> Armature -> Rigify Meta-Rigs -> Basic Human`** (NOT the full `Human` meta-rig, which includes dozens of facial and finger bones that a low-poly character with mitten hands does not need).
  - Under `Object Data Properties -> Viewport Display`, enable **`In Front`** so bones stay visible inside the mesh.
- **Crucible (`preset: "humanoid"`):**
  - In a `Crucible` scene recipe, add an armature entry:
    ```json
    "armatures": [{
      "id": "rig",
      "preset": "humanoid",
      "fit": {
        "bounds": { "min": [-0.35, 0.0, -0.15], "max": [0.35, 1.70, 0.15] },
        "landmarks": {
          "hips": [0, 0.88, 0],
          "leftUpperLeg": [0.10, 0.84, 0],
          "leftLowerLeg": [0.10, 0.46, 0.02],
          "leftFoot": [0.10, 0.08, -0.01]
        }
      }
    }]
    ```
  - Bind each character mesh node with `"skin": { "armature": "rig", "maxInfluences": 4 }`.

### 1.2 Mandatory Joint Alignment Rules
1. **Enable X-Axis Mirror** in Edit Mode (top-right toolbar in Blender) before moving any limb bone so left and right bones stay 100% symmetric.
2. **Delete Unneeded Bones:** In the `Basic Human` meta-rig, delete `breast.L` and `breast.R` so they don't steal chest/jacket weights. Keep `pelvis.L`/`pelvis.R` directly on top of the upper thigh heads.
3. **Snap Joints to Topology Edge Loops:**
   - Place the **knee joint** (`shin.L` head) and **elbow joint** (`forearm.L` head) directly inside the middle loop of the 3-loop joint cluster you modeled on the leg and arm.
   - Place the **head bone** (`spine.006` head) at the base of the skull where the 3-vertex neck meets the jaw, and its tail at the crown of the head.
4. **Never Leave Knees or Elbows Dead-Straight ($180^\circ$):**
   - In Side View (`Numpad 3`), ensure the **knee joint sits slightly forward** of the hip-to-ankle line, and the **elbow joint sits slightly backward** of the shoulder-to-wrist line.
   - *Why:* Both Blender's `Generate Rig` IK solver and `Crucible` `motion.ik` (`jointAxisProblems: ["straight-chain", "knee-bends-backward"]`) use the rest-pose bend angle to determine which way the limb folds.
5. **Apply Transforms Before Binding:**
   - The series keeps the Mirror modifiers on the limbs and binds with `Ctrl+P -> With Automatic Weights` (Part 9). Applying them first is skill guidance for engine export (glTF needs real geometry). Run `Ctrl+A -> All Transforms` before binding and apply mirrors before exporting.
   - If you tweak meta-rig bone positions later in Blender, click **`Re-Generate Rig`**—your existing mesh bindings and weight paints are preserved.

---

## 2. Low-Poly Weight Painting & Secondary Bones (Part 10)

Automatic weights (`Bone Heat`) always bleed across separated low-poly chunks: raising the arm pulls the side of the hair and jacket collar, and rotating the head squashes the hair spikes.

### 2.1 The Golden Rules of Low-Poly Weight Painting
1. **Turn ON `Auto Normalize` (`Options -> Auto Normalize`):**
   - Mandatory in Blender Weight Paint mode (and required by `glTF` / Three.js / `Crucible`). When you paint weight onto one bone, Blender automatically subtracts weight from competing bones so the vertex sum stays `1.0`.
2. **Use `Flat` Brush Falloff (Flat curve preset, Falloff Shape stays `Sphere` with `Front Faces Only` on; `Projected` is only for painting through the model, Part 10):**
   - Low-poly meshes have very few vertices. Smooth Gaussian falloff leaves stray `0.12` weights on neighboring vertices. A **Flat** falloff curve paints crisp `1.0` (`100%` red) or `0.0` (`0%` blue) weights in a single click.
3. **Isolate the `DEF` (Deformation) Bone Collection:**
   - In Rigify, turn off visibility for `ORG` and `MCH` bone collections and turn **ON `DEF`** (deformation bones, prefixed `DEF-`).
   - In Weight Paint mode, **`Alt + Left Click`** (or `Ctrl + Left Click`) any `DEF-` bone to inspect and paint its weights directly.
4. **Fix Head & Hair Weights (`100%` to `DEF-spine.006` / `head`):**
   - Select the `face` and `hair` meshes, enter Weight Paint mode, select `DEF-spine.006` (head bone), choose the **Gradient Tool** (or Paint with Weight = `1.0`, Falloff = `Flat`, Front Faces Only = `Off`), and flood the entire head and upper hair cap to solid red (`1.0`). With `Auto Normalize` on, this immediately strips all accidental shoulder/arm weights from the hair!
5. **Fix Jacket Collar & Waist Weights:**
   - Flood the collar and upper chest to `DEF-spine.002` / `DEF-spine.003` so swinging the arms (`DEF-upper_arm.L`) does not rip the collar open.

### 2.2 Adding Custom Secondary Bones (Hair Bangs, Ponytails, Skirts, Tails)
To animate bouncy hair locks, skirts, or tails on top of a generated rig:
1. Select the Armature, enter **Edit Mode**, click `+` under **Bone Collections** to create a `Hair` (or `Secondary`) collection, and turn on `DEF` to see `DEF-spine.006`.
2. `Shift+A` to add a new bone at the root of the hair lock (`hair_front.L`), align its tail to the tip of the hair lock, and **Parent it (`Ctrl+P -> Keep Offset`) to `DEF-spine.006`**.
3. If the mesh is already bound, create a matching Vertex Group named `hair_front.L` on the hair mesh (or re-parent `Ctrl+P -> With Empty Groups`).
4. In Weight Paint mode (with **`Auto Normalize` ON**), select `hair_front.L` and drag the **Weight Gradient** tool from the tip of the bang (`1.0` red) toward the root (`0.0` blue, where `DEF-spine.006` retains `1.0`).

---

## 3. 2D UV-Stepped Face Animation Rig (Part 11)

Many retro/anime low-poly characters use a **2D texture sprite-sheet swap** for eyes and mouths instead of complex facial geometry.

### 3.1 Sprite Sheet Layout
- Arrange $N$ expressions (e.g., $N = 6$: `Neutral`, `Blink`, `Happy`, `Angry`, `Shocked`, `Sad`) in a **horizontal row of equal-width cells** across the texture atlas.
- Separate the eye polygons (`eyes` material) and mouth polygons (`mouth` material) into two distinct material slots sharing the same image texture so eyes and mouths can switch independently!

### 3.2 Implementation Across Engines

#### A. Blender Shader Editor (Cascade of `Greater Than` + `Mix Vector` Nodes)
0. The face is a separate texture and material duplicated from the body material, assigned only to the face faces, then Project from View again and lined up with the nose (Part 11). Eyes and mouth get their own duplicated materials.
1. With Node Wrangler, `Ctrl+T` on the image gives `Texture Coordinate` and a `Mapping` node. Only `X Location` moves, because the faces sit in one horizontal row.
2. Determine the UV horizontal step size $d$ between adjacent expression cells (e.g., if each cell is $0.085$ UV units wide, offsets are $0, d, 2d, 3d, 4d, 5d$).
3. Create **6 `Combine XYZ` nodes** with `X` set to $0, d, 2d, 3d, 4d, 5d$ (`Y = 0, Z = 0`).
4. Chain **5 `Mix` (`Vector`) nodes** in series:
   - `Mix 1` blends `Combine 0` ($A$) and `Combine 1` ($B$), driven by `Math (Greater Than, Threshold = 1.0)`.
   - `Mix 2` blends `Mix 1` ($A$) and `Combine 2` ($B$), driven by `Math (Greater Than, Threshold = 2.0)`.
   - Continue up to `Threshold = 5.0`, and plug the final `Mix` output into **`Mapping (Location)`**.
5. Connect a single **`Value` node** to the top input of all 5 `Greater Than` nodes. Now setting `Value` to `0..5` snaps the UVs cleanly across the 6 faces without ever stopping mid-sprite!
6. **Bone Driver:**
   - Add two small non-deforming bones in front of the head: `eye_control` and `mouth_control` (parented to `DEF-spine.006`, with **`Bone Roll = 0 deg`**).
   - Add a **`Limit Location` constraint** (`Owner: Local Space`, `Min/Max X = 0`, `Min/Max Y = 0`, `Min Z = 0`, `Max Z` = the bone's Z when the last face shows, 0.35 is only an example; the series copies that value from the move panel).
   - Add a **Driver** on the Shader `Value` node: `Type = Scripted Expression`, Variable `var` = `Armature / eye_control / Z Location / Local Space`, Expression = `var * 15` (so sliding the bone up $0\text{–}0.35\text{ m}$ steps through faces `0..5`).

#### B. Three.js (`texture.offset.x` Stepped Controller)
In Three.js, clone the texture descriptor for the `eyes` and `mouth` materials (they share the underlying GPU image) and step `offset.x` using `Math.floor`:
```js
export function setFaceExpression(eyeMaterial, mouthMaterial, eyeIndex, mouthIndex, stepU = 1 / 6) {
  // Math.floor guarantees discrete sprite snapping even if animated by a continuous curve:
  eyeMaterial.map.offset.x = Math.floor(eyeIndex) * stepU;
  mouthMaterial.map.offset.x = Math.floor(mouthIndex) * stepU;
}
```

#### C. Crucible (`STEP` Keyframe Tracks or Material/Morph Drivers)
In `Crucible`, author discrete expression swaps using **`interpolation: "STEP"`** on morph weight tracks (`kind: "morph"`, where each expression is a relative UV/plane morph target) or stepped node tracks that swap recessed/decal face cards (`decal: true`, `depthLayer: 1`).

---

## 4. 3D Recessed Low-Poly Eye Rig (eyes video)

When a character needs smooth 360-degree eye-tracking (pupils looking left/right/up/down and independent blinking) without UV sprite sheets, use the **3-Layer Recessed Low-Poly Eye Rig**:

```
[Front (+Z / -Y)]                                  [Inside Head (-Z / +Y)]
   Face Shell (Alpha Cutout Socket)  -->  Floating Iris Plane  -->  Recessed Eye-White Box
```

1. **Layer 1 — Face Shell with Alpha Cutout Eye Socket:**
   - Erase the sclera (eye white) and iris pixels inside the eye shape on the face texture so the eye opening has **transparent alpha (`A = 0`)**, while keeping the eyelashes/eyelid border opaque (`A = 1`).
   - Paint the isolated left and right irises onto a free corner of the same texture atlas (also with transparent background).
   - Set material Alpha Mode to `Alpha Clip` / `Mask` (`alphaCutoff: 0.5`).
2. **Layer 2 — Recessed Sclera (`eye_white` Box):**
   - In Edit Mode on the face mesh, select the polygons covering the eyes, **Duplicate (`Shift+D`)**, and **Separate (`P -> Selection`)** into a new object `eye_white`.
   - Push `eye_white` backward into the head, extrude it, delete the front faces and `F` fill the edge gap, and map its UVs to pure white pixels on the atlas. Then slide it forward until it clips and back a hair, so it sits almost flush behind the cutout (eyes video). The series gives no millimetre value.
3. **Layer 3 — Floating Iris Planes (`iris.L` & `iris.R`):**
   - Duplicate the eye socket polygons again (`Shift+D`, `P -> Selection`), position them **halfway between the outer Face Shell and the back `eye_white` wall**, and unwrap them to the isolated iris sprites on the atlas.
   - **Critical Edge-Slide Step (`GG`):** Turn **OFF** X-Axis Mirror, and use **Edge Slide (`G -> G`)** to shrink the outer border of each iris plane inward so the quad tightly hugs the painted iris circle. *Why:* If the iris quad stays large, sliding the iris toward the nose or temple will clip the quad corners right through the side of the face!
   - Separate `iris.L` and `iris.R` and bind them `100%` (with `Auto Normalize` ON) to `i.L` and `i.R` bones: bone in front of the eye pointing straight out, `Roll = 0`, parented to the head bone (`DEF-spine.006` on Rigify, `head` otherwise), made once and `Symmetrize`d. Bind with `Ctrl+P -> Armature Deform with Empty Groups`, then the Gradient tool. Pose with `Local` orientation and `Individual Origins`, otherwise the alignment work is lost.
   - Do not place the irises close to the head edge, they clip when moved. If one clips sideways, move the bone tail on X or push the iris deeper. Irises may stay asymmetric.

---

## 5. Cyclic Low-Poly Animation Workflow (animation video)

### 5.1 Viewport Performance Setup
- Before animating in Blender `EEVEE`, disable `Shadows` and `Raytracing` in Render Properties so the viewport runs at locked 30/60 FPS.
- Set Frame Rate to **`30 FPS`** (or `12–15 FPS` stepped for a choppy PS1/stop-motion feel).

### 5.2 Seamless Looping Recipe (`Frame N+1` Rule)
For an $N$-frame loop (e.g., $25$ frames, Timeline `Start = 1, End = 25`):
1. Pose the character at **Frame `1`**, select **ALL** rig controls (`A`), and insert keyframes (`I`).
2. Copy Frame `1` keyframes (`Ctrl+C`) and paste them at **Frame `N + 1` (`Frame 26`)**—one frame past the timeline end—so Frame `25` and Frame `1` never duplicate the same pose on loop wrap!
3. Pose the opposite extreme (e.g., breathing exhale / lowest hip bob) at the midpoint **Frame `13–14`**.
4. Open the **Graph Editor**, select all channels (`A`), press **`Shift+E -> Make Cyclic (F-Modifier)`**, and set handle types to **`V -> Automatic`** so curves flow seamlessly across the loop boundary.

### 5.3 Overlapping Action & Amplitude Scaling
- **Never let every body part hit its peak on Frame 14:**
  - Select the keyframes for the **hands/arms**, **head**, and **secondary hair/skirt bones** and slide them **`G -> X -> +2` to `+4` frames** later in the Dope Sheet / Graph Editor. Because `Make Cyclic` is active, keys pushed past Frame `26` wrap cleanly!
- **Scale Curve Amplitude (`S -> Y`):**
  - If a breathing or bounce motion feels too stiff or too exaggerated, select its F-curve in the Graph Editor (with pivot set to `2D Cursor` or `Individual Centers`) and press **`S -> Y`** to scale the vertical amplitude without re-keying poses.

### 5.4 Mandatory `Constant` / `STEP` Interpolation for 2D Face Rigs
- When keying `eye_control` or `mouth_control` (2D UV sprite swap), select all keyframes on those bones in the Timeline / Dope Sheet and press **`T -> Constant`** (`interpolation: "STEP"` in `Crucible` / Three.js `InterpolateDiscrete`).
- *Why:* Bezier/Linear interpolation sweeps the bone smoothly from $Z = 0$ to $Z = 0.3$, which rapidly scrolls through every intermediate facial expression on the sprite sheet like a slot machine!

### 5.5 Two-Handed Props (`Child Of` / `Dynamic Parent`)
- When a character holds a prop (sword, umbrella, rifle) with both hands:
  - Always initialize the `Child Of` constraint (`influence: 1.0`) or `Dynamic Parent` at **Frame `1`** in the base pose before animating the parent hand (`hand_ik.R`).
  - In `Crucible`, use `motion.constraints`:
    ```json
    "constraints": [
      { "node": "prop-umbrella", "type": "child_of", "target": "rightHand", "inverse": "rest" }
    ]
    ```
    and drive the left hand to a grip locator on the prop using `motion.ik` (`{ "root": "leftUpperArm", "middle": "leftLowerArm", "end": "leftHand", "target": "umbrella-grip-left" }`).
