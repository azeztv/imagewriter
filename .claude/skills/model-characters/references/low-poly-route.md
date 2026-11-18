# Low-Poly Route

Route for a stylized low-poly character (about 300 to 1,200 triangles) with an unlit power-of-two atlas, hard-weighted rig and stepped 2D or inset 3D face, in Blender, three.js or Crucible. Pick the look first in `style-presets.md`. `{{SKILL_DIR}}` is the skill folder.

## Steps

`{{SKILL_DIR}}` is this skill's directory. Run Python helpers with `uv run --no-project`.

1. **Calibrate the 2D Reference (`read_character_ref.py`).**
   Measure the 2D image before touching 3D:
   ```bash
   uv run --no-project {{SKILL_DIR}}/scripts/read_character_ref.py ref.png --height 1.70 --out cal
   ```
   This detects front/side panels (or single view), normalizes feet to $Y=0$ and crown to target height, extracts head-count proportions, joint elevations (ankle, knee, crotch, waist, shoulder, chin, eye), width/depth profiles, and a quantized color swatch palette (`cal/calibration.json`, `cal/guide.png`, `cal/atlas_template.png`).

2. **Block Out Separate Low-Poly Body Chunks.**
   Follow [modeling-and-topology.md](modeling-and-topology.md). Never sculpt or use high-density subdivisions. Build distinct anatomical chunks so clothing cuffs and hair layers create natural silhouette steps:
   - **Foot:** Cube (`bevel: 0`) + 2 vertical loop cuts; pull toe forward and sole flat on $Z=0$ (Blender) / $Y=0$ (Three.js/Crucible).
   - **Leg:** 5-vertex open cylinder (caps deleted), 3–4 horizontal loops around the knee for clean deformation and knee-pad UV isolation, slight forward knee bend.
   - **Waist / Shorts:** Mirrored cube on centerline + `Bridge Edge Loops` (`bridge` op) to leg cuffs.
   - **Torso / Jacket:** Extruded mirrored cube with collar inset/extrude; **delete all internal cap faces** between mirrored halves and inside sleeve/neck openings.
   - **Arm & Mitten Hand:** 4-sided rotated arm tube with slight backward elbow bend; mitten hand from cube + 2 loop cuts + extruded thumb + `Merge at Center` (`collapse`) for crisp wedge fingertips.
   - **Neck:** 3-vertex open cylinder.
   - **Head (read [head-and-face.md](head-and-face.md) first):** there is no box head. The head is a hair shell (cube, bottom deleted) plus a knifed face patch pulled into a nose, brow and jaw profile in the side view, plus under-jaw faces. Eyes and mouth are painted on the patch. Check a three-quarter view and the eye size against the reference before texturing.
   - **Hair:** **Upper Cap**, **Front/Side Bangs**, **Back Spikes**, as thin tapered triangles that frame the face. Apply mirror before cutting asymmetric bangs.
   - **Hood, hat, ears:** their own chunk from the turnaround, checked from the back and side.

3. **Unwrap UVs & Paint the Unlit Texture Atlas.**
   Follow [uv-and-texturing.md](uv-and-texturing.md):
   - Use **Unlit / Emission (`strength = 1.0`) + `Standard` View Transform** in Blender (`MeshBasicMaterial` + `SRGBColorSpace` in Three.js; `tag: "unlit"` + `viewTransform: "neutral"` in Crucible) so painted hex colors render 1:1 without grey tone-mapping.
   - Unwrap planar groups with **Project from View** (`uv_project` in Crucible) with Mirror modifier `On Cage` preview disabled so left/right islands don't double-overlap.
   - Paint flat base swatches first, then 3-step ramp bands (highlight / mid / shadow). Rotate triangle UVs across a dark/light boundary on the atlas to get diagonal hair/clothing shadows without adding geometry.

4. **Rig, Weight-Paint, and Add Face/Eye Controls.**
   Follow [rigging-and-animation.md](rigging-and-animation.md):
   - Align armature joints to wireframe loops in Front and Side views. Delete unused bones (e.g. breast bones on stylized characters). Keep a slight **forward knee bend** and **backward elbow bend** so IK never flips.
   - In Weight Paint mode, use **Flat brush falloff** (hard 100% / 0% weights) and **enable `Auto Normalize`** so vertex weight sums never exceed `1.0`. Assign head/hair 100% to the head bone (`DEF-spine.006` / `head`) plus custom secondary bones (`hair_front`, `skirt`, `tail`) for overlapping motion.
   - Choose **2D UV-Stepped Face Rig** (horizontal sprite strip of 6 expressions driven by bone Local Z with `Constant` stepped keyframes) or **3D Inset Eyes** (alpha cutout eye socket + recessed `eye_white` box + floating `iris.L`/`iris.R` planes between shell and sclera).

5. **Animate & Validate (`check_character.py`).**
   - For looping idle/walk cycles of length $N$ frames, copy Frame `1` to Frame `N+1`, render frames `1..N`, apply `Make Cyclic` F-modifiers, and offset secondary bones by 2–5 frames.
   - Run the validator on your exported `.glb` or `.recipe.json`:
     ```bash
     uv run --no-project {{SKILL_DIR}}/scripts/check_character.py character.glb --max-tris 1500
     ```

For any step done in Blender (geometry nodes, shaders, rigging, weight paint, NLA, bpy), load the `use-3d-software` skill for the exact nodes and current 5.x names.

## Hard Rules

- **No box head, no flat face plate:** the face patch has a pointed nose, brow and cheek steps in the side view, and hair covers every bare box edge. Fault 13.
- **UV before texture:** make the UV layout, then paint to it. Project from View for planar parts, Unwrap for curved ones (hair base). Never project at a harsh camera angle.
- **Zero internal or coplanar faces:** Delete caps inside open cylinders (neck, legs, sleeves) and along mirror seams.
- **Auto-normalized weights:** Every skinned vertex must have positive, normalized weights ($\sum w_i = 1.0$, max 4 influences).
- **Pre-bent IK limbs:** Never rig dead-straight $180^\circ$ knees or elbows when using IK (`motion.ik` or Rigify).
- **Stepped 2D face keys:** Always use `Constant` / `STEP` interpolation on UV-offset face controllers so expressions never slide across intermediate sprites.
- Run `uv run --no-project {{SKILL_DIR}}/scripts/test_character_skill.py` after modifying any script in `scripts/`.

## Garments and soft props (shirts, jackets, bags)

From a low-poly polo that looked odd until rebuilt this way (2026-11-17).

- **Loft through measured sections.** Take widths, depths and lengths from a real size chart checked against photos, as cross-sections from hem to neck. Shoulder and neckline sections are not planar: the shoulder slopes down from the neck and the front neckline sits lower than the back. Write the numbers in a plain math file the build script imports, so they can be checked without Blender.
- **v along height.** Set the body's v to height over garment length, so a painted row is a line of constant height: seams, hems and logos land where you expect.
- **Weld the strips.** A loft built strip by strip shows a shading seam at each join under smooth shading. Merge by distance (`bmesh.ops.remove_doubles`) per smooth part. Keep double-sided flaps (collars, lapels) as separate flat-shaded vertices.
- **Measure flap clearance.** A collar or lapel lying on the body must sit in front of the body surface along its whole edge (1 to 2 cm at this scale). Check the numbers or a close crop. An edge 5 mm behind the chest vanished in the render.
- **Fine detail only on near-rectangular faces.** PS1-style affine mapping smears texture on large trapezoid faces, such as neck-to-chest triangles. Put plackets, buttons and logos below the trapezoid, on faces close to rectangles.
- **No 1-texel stripes.** Ribs or stripes alternating every texel shimmer (moire) on a turntable. Use bands at least 2 texels wide, for example 2 dark columns in every 4.
- **Dark side shading only where the side faces away.** Painting side darkening or seam lines up over the shoulder shows as a streak from the top.
