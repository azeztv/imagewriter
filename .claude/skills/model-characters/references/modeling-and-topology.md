# Low-Poly Character Modeling & Topology from 2D References

This guide distills a complete low-poly character modeling workflow (Parts 1–6) and translates every step into **Blender** (interactive & `bpy` headless script), **Three.js** (`BufferGeometry`), and **Crucible** (`mesh` recipe operations).

<!-- skill-navigation:start -->
## Reading Map

- [Low-Poly Character Modeling & Topology from 2D References](#low-poly-character-modeling--topology-from-2d-references)
- [1. Scene & 2D Reference Calibration](#1-scene--2d-reference-calibration)
- [2. Part-by-Part Topology Recipes](#2-part-by-part-topology-recipes)
- [3. Hair Chunking & Asymmetric Bangs](#3-hair-chunking--asymmetric-bangs)
- [4. Multi-Engine Implementation Patterns](#4-multi-engine-implementation-patterns)
<!-- skill-navigation:end -->

---

## 1. Scene & 2D Reference Calibration

### 1.1 Coordinate & Scale Conventions
- **World Height:** Scale the character to real human/stylized height ($1.60\text{ m}$ to $1.80\text{ m}$) with the **soles of the feet planted at ground level** ($Z = 0$ in Blender; $Y = 0$ in Three.js and Crucible) and the **centerline on $X = 0$**.
- **Rigify Scale Anchor (Blender):** Enable the built-in `Rigify` addon first and spawn `Add -> Armature -> Human (Meta-Rig)`. Scale your 2D reference images to match the meta-rig height ($~1.75\text{ m}$) before modeling so automatic weights and IK solvers never suffer from microscopic or giant unit scales.
- **Unlit Viewport Setup (Blender):**
  - Set Render Engine to `EEVEE`.
  - Under `Color Management`, change **View Transform** from `AgX` / `Filmic` to **`Standard`**, and set **Look** to `None`. (`AgX`/`Filmic` desaturates bright colors and turns pure white `#FFFFFF` into muddy grey).
  - Disable scene lights/world lighting in Material Preview when painting unlit/emission textures.

### 1.2 Aligning Front & Side Turnaround Planes
- **Front Reference Plane:** Placed behind the character (`Y > 0` in Blender, `Z < 0` in Three.js/Crucible), facing the front orthographic camera.
- **Side Reference Plane:** Rotated $90^\circ$ around the vertical axis, offset to the side (`X < 0`) so it does not slice through the mesh in perspective view.
- **Image Object Settings (Blender):**
  - Set `Depth` to **`Back`** and check **`Side: Front`** (one-sided) so the reference image never blocks the mesh when orbiting behind it.
  - Enable `Opacity` ($0.4\text{–}0.6$) and disable **Selectable** (funnel filter icon -> arrow toggle in Outliner) so you never accidentally drag the reference plane.
- **Single-Image Fallback:** When only a single 2D front concept or 3/4 illustration is available, run `scripts/read_character_ref.py` to extract vertical landmark ratios ($Y_{\text{ankle}}, Y_{\text{knee}}, Y_{\text{crotch}}, Y_{\text{waist}}, Y_{\text{shoulder}}, Y_{\text{chin}}, Y_{\text{crown}}$) and infer side depths using standard stylized low-poly thickness ratios:
  - Foot length $\approx 1.8 \times$ foot width; ankle depth $\approx 1.0 \times$ ankle width.
  - Thigh/calf depth $\approx 1.05 \times$ limb width, with the knee cap forward by $+2\text{ cm}$ and calf apex back by $-1.5\text{ cm}$.
  - Pelvis/waist depth $\approx 0.65 \times$ hip width; chest depth $\approx 0.60 \times$ chest width.
  - Head depth (nose tip to back of skull) $\approx 1.05 \times$ head width.

---

## 2. Part-by-Part Topology Recipes

Build the character as **separate low-poly chunks** (`foot`, `leg`, `waist`, `torso`, `arm`, `hand`, `neck`, `face`, `hair`). Keeping parts separate until UV unwrapping (or keeping natural clothing overlaps as separate sub-meshes) creates crisp silhouette steps at cuffs, collars, and shorts without wasting polygons on connector loops.

### Summary Budget Table

| Body Part | Base Primitive | Key Topology Edits | Target Budget (per side / total) |
|---|---|---|---|
| **Foot** | Cube (`8` verts) | 2 vertical loop cuts along length; pull toe forward, flatten sole, taper ankle | `16` verts / `14` quads (`~28` tris/side) |
| **Leg** | **5-vertex Cylinder** (`Fill: Nothing`) | Open ends; 1 knee loop + 2 boundary loops above/below knee; slight forward knee bend | `25` verts / `20` quads (`~40` tris/side) |
| **Waist / Shorts** | Cube + Mirror (`Clipping: On`) | Delete inner seam face; extrude hip-to-crotch; **Bridge Edge Loops** (`bridge`) to leg cuff | `~36` verts / `~64` tris total |
| **Torso / Jacket** | Cube + Mirror (`Clipping: On`) | Extrude waist -> chest -> shoulder; inset + extrude collar up & neck hole down; **delete all internal caps** | `~60` verts / `~110` tris total |
| **Arm** | Rotated Cube (`4`-sided) | Loop cuts for elbow and cuffs; slight backward elbow bend (series does not delete caps; the sleeve hides them) | `20` verts / `16` quads (`~32` tris/side) |
| **Hand (Mitten)** | Cube (`8` verts) | Rotate, extrude one face, `Merge at Center` (`collapse`) the front pair and the back pair so it tapers to a point. Thumb is skill guidance, the series has none | `~18` verts / `~30` tris/side |
| **Neck** | **3-vertex Cylinder** (`Fill: Nothing`) | Open triangular prism (`3` verts/ring); tuck top into jaw underside, bottom into collar | `6` verts / `3` quads (`6` tris total) |
| **Head** | Hair shell + face patch + under-jaw faces | No box head. See [head-and-face.md](head-and-face.md): relief patch knifed from a plane, side-view profile, hair frames it | `~38` face verts, hair `~90–160` tris |
| **Hair** | Open Cube Cap + Extruded Strips | Upper cap from 5-face cube; extrude triangular spikes (`Merge at Center`) + asymmetric front bangs | `~90–160` tris total |

---

### 2.1 Foot (`Cube + 2 Loop Cuts`)
1. Spawn a Cube positioned at the foot reference in Front (`X`) and Side (`Y`/`Z`) views.
2. Scale the cube to match the ankle width and full foot length (heel to toe).
3. Add **2 vertical loop cuts** (`Ctrl+R` -> scroll `2`) dividing the foot into 3 segments from heel to toe (heel/ankle column, midfoot arch slope, toe box).
4. Select the top-front edges and slide them down to form the sloped instep; select the ankle top quad and taper it inward so it tucks cleanly inside the lower leg or boot cuff.
5. Keep all bottom vertices coplanar at ground height ($0.0$).

### 2.2 Leg (`5-Vertex Open Cylinder`)
Why 5 vertices? A 4-sided leg looks overly boxy from 3/4 angles, while 6–8 sides waste polygons. A **5-vertex cylinder** places one ridge down the front shin (catching a crisp 2-tone highlight/shadow split) and a flat face across the back calf.
1. Add a Cylinder with **`Vertices = 5`** and **`Cap Fill Type = Nothing`** (no top or bottom cap faces).
2. Rotate the cylinder so one vertex points straight forward along the shin (or straight back, depending on whether the front shin or back calf needs a sharp crease).
3. Match the ankle ring and upper-thigh ring to the 2D reference in Front and Side views.
4. Add a horizontal loop cut at the **knee** and pull it slightly **forward** (creating the knee cap / back-of-knee divot).
5. Add **2 support loop cuts** (one just above the knee, one just below the knee). These serve two purposes:
   - They hold the knee volume during $90^\circ$ skeletal bending.
   - They bound the knee UV quad so painted knee-pad or skin shading does not stretch down the whole shin.

### 2.3 Waist / Shorts (`Mirrored Cube + Bridge Edge Loops`)
1. Spawn a Cube at the pelvis, delete half of it, and add a **Mirror Modifier** on $X$ with **`Clipping` enabled**.
2. **Delete the internal face** on the mirror plane ($X=0$) immediately so no hidden geometry is trapped inside the pelvis.
3. Shape the outer hip and crotch profile in Front and Side views.
4. Series method (Part 3): add loop cuts around where each leg opening goes, delete the faces over it, then select the front and back edges of the opening and run **`Edge -> Bridge Edge Loops`** (`bridge` in Crucible) to seal the crotch. Sealing the opening is the bridge's job, not connecting to a cuff.
5. Skill guidance for a cuff: duplicate (`Shift+D`) the top ring of the leg cylinder, scale it slightly outward, and extrude it into a cuff. Keep the shorts an open hollow shell.

### 2.4 Torso / Jacket (`Extruded Mirrored Cube`)
1. Start from a mirrored Cube at the waist (`Clipping: On`, inner seam face deleted).
2. Extrude upward in 3 sections: **Waist -> Ribcage/Chest -> Shoulder**.
3. In Side view, angle the chest forward and the upper back slightly curved; in Front view, flare the jacket hem or taper the waist to match the 2D silhouette.
4. **Shoulder Sleeve Opening:** Select the upper side quad of the torso, extrude or inset it slightly for the shoulder cap, and **delete the outer cap face** where the arm emerges.
5. **Collar & Neck Cavity:**
   - Select the top shoulder/neck face along the mirror line, inset (`I`) or loop-cut around the neck base, and extrude upward to form a popped jacket collar.
   - Select the inner neck floor face, **Inset (`I`) slightly and Extrude (`E`) downward** into the chest, then paint/map that recessed ring to dark shadow so no gaps ever show around the cylindrical neck.

### 2.5 Arm (`Rotated 4-Sided Tube`) & Mitten Hand (`Cube + Merged Tips`)
- **Arm:**
  1. Spawn a Cube, rotate it to match the A-pose or T-pose angle in the 2D reference, and drag the bottom face to the wrist (Part 3).
  2. Tuck the upper end inside the torso sleeve opening and match the wrist to the cuff.
  3. Add loop cuts at the elbow and cuffs and nudge the elbow **slightly backward** (pre-bend for IK). If the drawn side view is useless, eyeball the depth as the series does.
- **Hand (Low-Poly Mitten):**
  1. Spawn a Cube at the wrist, scale it into a flat palm block, and rotate it to match the arm angle.
  2. Extrude one face toward the fingertip (Part 3).
  3. **Taper to a point:** in opaque solid view select the two front vertices, `F3 -> Merge -> At Center`, then the two back vertices the same way (`collapse` in Crucible).
  4. Widen it on Y a little so it is not flat (Part 3).
  5. **Thumb (skill guidance, not in the series):** extrude a side quad outward and merge its tip into a wedge.

### 2.6 Neck (`3-Vertex Open Cylinder`) & Face (`Plane + Mirror + Knife Cuts`)
- **Neck:**
  - Spawn a Cylinder with **`Vertices = 3`** and **`Cap Fill Type = Nothing`**.
  - Rotate it so one flat face points forward (or one vertex points forward under the chin) and scale it to bridge the torso collar and the underside of the head. Only 6 vertices (6 triangles) are needed!
- **Face:** full steps, the head rule and the proportion check are in [head-and-face.md](head-and-face.md). Short form:
  1. Plane facing Front, cut at $X=0$, Mirror (`Clipping: On`).
  2. Knife only the edges the drawing shows (eye line, nose, cheek step, mouth, jaw). Do not cut a rectangular eye box, the eyes are painted.
  3. Side View is mandatory: pull the nose tip out first, then brow and chin, then temple, cheek and jaw corner back (`+Y` in Blender / `-Z` in Three.js & Crucible). Front view alone leaves a flat plate.
  4. Under-jaw faces: extrude the jaw edge back toward the neck and fill with `F`, map to the dark shadow swatch.

---

## 3. Hair Chunking & Asymmetric Bangs

Never model hair as one giant subdivided sphere. Break the hairstyle from the 2D reference into **3 logical layers**:
1. **Base Hair Cap (Upper Skull):**
   - Spawn a Cube around the head, **delete the bottom face**, add a Mirror Modifier (`Clipping: On`), and shape the 5 remaining faces into a dome that wraps the top, sides, and back of the skull.
   - Fit it in front, side, top and back views: the top view must not be a flat plane, and the hem rises to where the bangs start (Part 5).
   - Join (`Ctrl+J`) the hair cap to the face object (or share the mirror modifier) while blocking out spikes. This joined object is the head (see [head-and-face.md](head-and-face.md)).
2. **Extruded Hair Spikes & Side Locks (Edge-to-Triangle Method):**
   - In isolated view (`Numpad /`), select an edge along the hairline of the cap and **Extrude (`E`)** downward/outward along the 2D hair lock silhouette.
   - To taper a lock to a sharp anime/PS1 point: select the two bottom vertices of the extruded quad and press **`M -> Merge at Center`** (or `At Last`), turning the tip quad into a sharp triangle.
   - To give a flat hair strip 3D volume: extrude the central ridge edge outward slightly and fill (`F`) the side triangles between the ridge tip and the root corners.
3. **Asymmetric Front Bangs:**
   - Complete all symmetric back/side hair chunks first.
   - Separate the hair mesh (`P -> Selection`) if joined, **Apply the Mirror Modifier** (`Ctrl+A` over Mirror), and use the **Knife Tool (`K`)** + **Extrude (`E`)** + **Merge (`M`)** to cut and extrude the asymmetric parting and bangs across the forehead.

---

## 4. Multi-Engine Implementation Patterns

### 4.1 Headless Blender (`bpy` + `bmesh`)
When generating a character procedurally in Blender Python:
- Build each part in its own `bpy.data.meshes.new(name)` using `bmesh`.
- For open cylinders (`leg`, `neck`), use `bmesh.ops.create_cone(bm, cap_ends=False, segments=5, radius1=r_bot, radius2=r_top, depth=h)`.
- Always call `bmesh.ops.recalc_face_normals(bm, faces=bm.faces)` after extrusions, bridges, or mirror-plane welds.
- Set `poly.use_smooth = False` across all low-poly faces (or use `Shade Auto Smooth`, which replaced the Auto Smooth checkbox in 4.1, at $60^\circ$ only on cylindrical limbs if soft shading is desired; pure PS1 style uses **Flat Shading** + hand-painted ramp gradients).

### 4.2 Three.js (`BufferGeometry` / Procedural Kit)
When building low-poly character parts directly in Three.js without Blender:
- Construct open 5-sided leg tubes with `new THREE.CylinderGeometry(rTop, rBot, height, 5, 3, true)` (`openEnded = true`) and displace the middle ring vertices (`y == 0`) forward by `+0.02` for the knee bend.
- Construct the 3-sided neck with `new THREE.CylinderGeometry(rTop, rBot, height, 3, 1, true)`.
- Use `geometry.toNonIndexed()` + `geometry.computeVertexNormals()` when you want crisp faceted low-poly normals, or `THREE.MeshBasicMaterial({ map: atlasTexture })` for authentic unlit shading where normals are ignored and lighting is 100% painted into the texture atlas.

### 4.3 Crucible (`mesh` Recipe Operations)
In `Crucible` (`@codepawlhq/crucible`), build each character chunk as a declarative `mesh` geometry in the scene recipe:
- **5-Sided Leg:** Start with `base: { type: "cylinder", radialSegments: 5, heightSegments: 3, bevel: 0 }`, delete `top` and `bottom` caps (`{ op: "delete", faces: { tag: ["top", "bottom"] } }`), and translate the knee ring forward.
- **Mirrored Torso / Waist:** Model the right (`+X`) half from a `box` (`bevel: 0`), delete the `left` seam face (`{ op: "delete", faces: { tag: "left" } }`), use `extrude`, `inset`, and `translate` on tagged faces (`top`, `bottom`, `right`), and place `{ op: "mirror", axis: "x", mergeThreshold: 0.001 }` in the `stack`.
- **Wedge Mitten Hand:** Start with `base: { type: "box", bevel: 0 }`, use `loop_cut` across the palm, `extrude` the thumb from a side face, and `collapse` the distal fingertip edge into a wedge.
- Always inspect with `mesh_inspect` (`lintMesh`) to confirm zero non-manifold edges or degenerate faces before binding to an armature.
