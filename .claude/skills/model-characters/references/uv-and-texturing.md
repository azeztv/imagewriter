# Low-Poly UV Unwrapping & Hand-Painted / Pixel Texture Atlases

This reference covers a complete UV unwrapping and unlit texture-atlas workflow (Parts 7–8), plus how to configure identical color-accurate shaders in **Blender**, **Three.js**, and **Crucible**.

<!-- skill-navigation:start -->
## Reading Map

- [Low-Poly UV Unwrapping & Hand-Painted / Pixel Texture Atlases](#low-poly-uv-unwrapping--hand-painted--pixel-texture-atlases)
- [1. The Power-of-Two Texture Atlas Layout](#1-the-power-of-two-texture-atlas-layout)
- [2. Unlit / Emission Shader & Color Management Across Engines](#2-unlit--emission-shader--color-management-across-engines)
- [3. Planar "Project from View" UV Unwrapping Workflow](#3-planar-project-from-view-uv-unwrapping-workflow)
- [4. Low-Poly UV Tricks (Shadow Ramps, Rotated Triangles & Asymmetric Flips)](#4-low-poly-uv-tricks-shadow-ramps-rotated-triangles--asymmetric-flips)
<!-- skill-navigation:end -->

---

## 1. The Power-of-Two Texture Atlas Layout

Low-poly stylized characters use **one compact Power-of-Two (POT) texture sheet** (the series uses `1024x512`, Part 7) organized into human-readable rectangular zones. Make the UV layout first and paint to it: the series author painted first and got pixelation and misaligned faces (Part 8). Project from View is right for planar parts (about 90 percent of cases, Part 8). Unwrap or Smart UV Project are fine for curved parts, and the series itself uses Unwrap for the hair base colour. Overlapping UVs are fine inside Blender but break lightmap baking in game engines (Part 8 correction).

The zone table below is skill guidance, not the series' layout. The series' sheet was admitted to be imperfect, with the face a small part. Its later model gives the face 10 to 15 percent. When the face has an expression rig, it gets its own texture (see below).

| Atlas Zone | Recommended UV Footprint | Contents |
|---|---|---|
| **Top-Left (`[0.0, 0.5] x [0.5, 1.0]`)** | `~15-25%` | **Face:** Base skin, blush, nose shadow, painted eyes and mouth. With an expression rig, the face moves to a separate texture and material (a horizontal strip of equal cells, `rigging-and-animation.md` section 3), and this zone becomes extra hair or cloth space. |
| **Top-Right (`[0.5, 1.0] x [0.5, 1.0]`)** | `~25%` | **Hair Swatches & Bang Strips:** Vertical gradient ramp (crown highlight -> mid tone -> tip shadow) + dark root/shadow block for under-hair faces. |
| **Bottom-Left (`[0.0, 0.5] x [0.0, 0.5]`)** | `~25%` | **Torso, Jacket, Waist/Shorts:** Front/back jacket graphics, collar/cuff trim strips, zipper/pocket details, and 3-step cloth shading ramps. |
| **Bottom-Right (`[0.5, 1.0] x [0.0, 0.5]`)** | `~25%` | **Limbs, Hands, Feet & Solid Swatches:** Skin knee/calf patch, sock/shoe sole & toe box, and a row of 3-step solid color swatches (`Highlight | Mid | Shadow`) for fast flat-face mapping. |

### Two-Pass Painting Strategy
1. **Pass 1 — Flat Base Colors:** Block out solid rectangular color regions on the POT canvas for skin, hair, jacket, shorts, shoes, and a dedicated **dark shadow swatch** (for under-jaw, inside-collar, and under-skirt/shorts cavities).
2. **Pass 2 — Gradients, Highlights &Painted Creases:**
   - Paint soft vertical gradients on the hair, face, and limbs (brighter at the top/front, darker toward joints and cuffs).
   - Paint crisp graphic details (collar stripes, shoe laces, knee blush/shadow, pocket seams) directly onto the projected UV rectangles.

---

## 2. Unlit / Emission Shader & Color Management Across Engines

Stylized low-poly characters rely on **painted lighting** inside the texture atlas. Standard PBR shaders and filmic tone-mappers ruin the palette by darkening whites and shifting hues.

### 2.1 Blender (`Emission` + `Standard` View Transform)
1. **Shader Editor:** Route `Image Texture (Color)` -> **`Emission` shader (`Strength = 1.0`)** -> `Material Output (Surface)`.
   - If the texture uses alpha cutouts (e.g., the 3D eye sockets in the eyes video), use a `Principled BSDF` with `Base Color = Black`, `Roughness = 1.0`, `Specular = 0.0`, plug `Image Texture (Color)` into `Emission Color` (`Emission Strength = 1.0`), and plug `Image Texture (Alpha)` into `Alpha`.
2. **Texture Filtering:** Set the `Image Texture` interpolation to:
   - **`Closest`** for crisp PS1 / pixel-art textures (`256x256` or `512x512`).
   - **`Linear`** for smooth hand-painted anime gradients (`1024x512` or `1024x1024`).
3. **Color Management:** Under `Render Properties -> Color Management`, set **`View Transform = Standard`** and **`Look = None`**.

### 2.2 Three.js (`MeshBasicMaterial` + `SRGBColorSpace`)
```js
import * as THREE from 'three';

const loader = new THREE.TextureLoader();
const atlas = loader.load('textures/character_atlas.png');
atlas.colorSpace = THREE.SRGBColorSpace;
atlas.flipY = false; // Keep false when applying to GLTF/GLB meshes!
// Use NearestFilter for pixel-art look, or LinearFilter for hand-painted look:
atlas.magFilter = THREE.NearestFilter;
atlas.minFilter = THREE.NearestFilter;

const material = new THREE.MeshBasicMaterial({
  map: atlas,
  alphaTest: 0.5, // Only needed if using alpha-cutout eye sockets
});
```
- Also set `renderer.outputColorSpace = THREE.SRGBColorSpace` and `renderer.toneMapping = THREE.NoToneMapping` (or `THREE.NeutralToneMapping` if mixing with a lit stage) so character colors match the 2D reference 1:1.

### 2.3 Crucible (`tag: "unlit"` + `viewTransform: "neutral"`)
- For procedural/flat-colored low-poly parts in a `Crucible` recipe, set `tag: "unlit"` on the material and `environment.viewTransform: "neutral"`.
- For GLB characters exported from Blender with an unlit/emissive atlas:
  - Export the texture into `baseColorTexture` (and/or `emissiveTexture` with `emissiveFactor: [1, 1, 1]`).
  - In `Crucible`, set `environment.viewTransform: "neutral"` and balance `ambientIntensity` / `keyIntensity` so the character's painted gradients read cleanly without harsh specular blowout (`roughness: 1.0, metallic: 0.0`).

---

## 3. Planar "Project from View" UV Unwrapping Workflow

Never unwrap the whole character at once. Unwrap **one body chunk at a time**, projecting planar groups from Orthographic views (`Front`, `Side`, `Back`, `Top`):

1. **Disable Mirror Modifier "On Cage" / Edit-Mode Preview First:**
   - Before selecting faces to unwrap on a mirrored object (`face`, `torso`, `waist`), **turn off the Mirror Modifier's `Edit Mode` / `On Cage` visibility toggle** (the square-with-vertices icon).
   - *Why:* If Mirror preview is active while you run `Project from View`, Blender projects both the real side and the mirrored preview, creating weird center-seam distortions or misleading UV placement.
2. **Project Planar Face Groups (`U -> Project from View`):**
   - Switch to **Front View (`Numpad 1`)**, select the front-facing polygons of the part (e.g., front face mask, front torso, front shin), and run **`U -> Project from View`**.
   - Move (`G`) and scale (`S`) that projected UV island directly onto its painted region in the UV Editor.
   - Switch to **Right/Left Side View (`Numpad 3`)**, select the side-facing polygons (temple/cheek, outer arm, outer leg, shoe side), and run **`U -> Project from View`**.
3. **Matching Proportions & Flipping Mirrored UVs (`S X -1`):**
   - If a side projection faces the wrong direction compared to your painted detail on the atlas, flip it horizontally in the UV Editor with **`S -> X -> -1`** (or vertically with `S -> Y -> -1`).
   - Never project from a harsh camera angle. Projection is a snapshot of the camera, so an angled view distorts. Fix remaining distortion by moving UV vertices (Part 8).
   - The face patch: scale and move its island until the bottom of the 3D nose meets the nose shadow on the art. Check eye size against the reference and scale the island wider and bigger if the face looks derpy (Part 8 end).
4. **Cavity & Underside Shadow Mapping:**
   - Select hidden/downward-facing polygons (**under-jaw**, **neck cylinder**, **inside jacket collar**, **inside shorts cuffs**, **shoe soles**) and scale (`S -> 0.05`) their UVs into the **dark shadow swatch** on the atlas. This gives instant anime/retro occlusion under the chin and cuffs without any runtime ambient occlusion cost.

---

## 4. Low-Poly UV Tricks (Shadow Ramps, Rotated Triangles & Asymmetric Flips)

### 4.1 The 3-Step Color Swatch Ramp (Flat-Shaded Facets)
For faceted parts like the 5-sided leg, mitten hand, or shoes:
- Paint a small 3-band color swatch on the atlas: **`[ Highlight | Midtone | Shadow ]`**.
- Map the **front-facing quad** of the shin/shoe into the `Highlight` band.
- Map the **side-facing quads** into the `Midtone` band.
- Map the **back-facing quads** into the `Shadow` band.
- This creates crisp, stylized cel-shaded volume around every limb even under completely flat (`unlit`) lighting.

### 4.2 The Rotated UV Triangle Trick (Diagonal Hair & Cloth Shadows)
In Part 8, the series demonstrates how to get sharp diagonal shadows or two-tone hair tips **without adding extra geometry cuts**:
1. Paint a straight horizontal or vertical boundary between a **Midtone** swatch and a **Shadow** swatch on the texture atlas.
2. Select a single triangular or quad face on a hair spike or jacket lapel.
3. In the UV Editor, **Rotate (`R`) and position that UV face diagonally across the Midtone/Shadow boundary** on the atlas.
4. Because the texture boundary cuts diagonally across the UV triangle, a single 3-vertex triangle displays a crisp two-tone shadow slice in 3D!

### 4.3 Extra Joint Loop Cuts to Confine UV Details
- If you paint a knee detail (knee pad, blush, sock top) onto a long leg quad that stretches from ankle to hip, the detail will stretch and warp.
- Add **two horizontal loop cuts** closely framing the knee (above and below the kneecap). Map only that compact middle quad ring to the knee detail on the atlas, and map the long upper/lower shafts to solid skin/sock swatches.

### 4.4 Asymmetric Clothing / Hair Details Without Duplicating Texture Space
When a character has symmetric geometry (e.g., shorts or jacket) but an **asymmetric detail** on one side (e.g., a stripe or logo only on the left leg):
1. Unwrap the mirrored mesh first so both sides share identical UVs.
2. **Apply the Mirror Modifier** (`Ctrl+A` in Object Mode).
3. Enter Edit Mode, select only the polygons on the side that needs the unique detail, and **move (`G`) or flip (`S X -1`) their UV island** to a separate small patch on the atlas while leaving the rest of the body sharing symmetric UVs.
