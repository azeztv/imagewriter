# Base Mesh and Box Modeling

Box-modeling route for a clean quad base mesh at any style. A low-poly game character, a subdivided cartoon body and a sculpt base all start this way. The free "Character Modeling Reference Images" (front, side, top) on Gumroad match these steps.

- **[modeling] Orthographic reference images set up**: front, side, top images that only show in ortho views.
  - Steps: delete everything, `Numpad 1` (front), `Shift A` > Image > Background, choose the front image with Align to View on in the file browser sidebar (`N`), repeat for side (`Numpad 3`) and top (`Numpad 7`). Backgrounds only appear in orthographic (`Numpad 5`), so looking around freely hides them. Save early with File > Save As, then `Ctrl S` often. Blender 4.x: Add > Image > Background is the same.
  - Use when / pitfalls: use background rather than reference-empty-plane so they vanish in user perspective.

- **[modeling] Half-model with Mirror modifier and Clipping**: model one side and save half the work.
  - Steps: `Shift A` > Mesh > UV Sphere; in the Adjust Last Operation panel set Segments 16, Rings 12; `Tab`, `R` `90` `Enter` to put the poles where wanted. Hold `Z` to the wireframe, `A` deselect, `B` box select one half, `X` > Vertices. Modifier Properties > Add Modifier > Generate > Mirror (axis X). Turn on Clipping so centre vertices stay merged when moved. Use `Numpad 1` front view to check.
  - Use when / pitfalls: apply the Mirror modifier (`Ctrl A`) before rigging. Wireframe is needed to select through the mesh (or Alt Z X-ray).

- **[modeling] Proportional editing and edge slide**: soft pulls and even spacing while shaping.
  - Steps: `O` toggles Proportional Editing; `G` then mouse wheel changes the falloff circle; turn it off again when done. Double tap `G` (edge slide) on a vertex to slide along its edges, used to even spacing of faces. `Alt` click selects an edge loop/ring. `B` box select and `G`/`R`/`S` with axis keys for the rest of shaping (jaw, shoulders, hips).
  - Use when / pitfalls: for large uneven faces, select pairs of vertices and edge slide so quads are similar sizes.

- **[modeling] LoopTools Circle to make round limb openings**: turn a square face group into a round ring for a neck, arm or leg.
  - Steps: enable Edit > Preferences > Add-ons > "Mesh: LoopTools" (Blender 4.2+: install from Extensions, "LoopTools"). In edit mode face select (`3`), pick the faces (for example the 4 bottom faces for a neck; works across the mirror), `N` sidebar > Edit tab > LoopTools > Circle. Then `R` `S` `G` to position, `S` `Z` `0` to flatten faces on one axis. `E` extrude, `S` scale, `R` rotate, `G` move to build the neck, shoulder, arm.
  - Use when / pitfalls: the add-on is shipped with Blender but off by default. In 5.x it is an Extension.

- **[modeling] Extrude-and-shape body workflow, low-poly base mesh**: neck, shoulders, torso, hips, legs, feet, arms, thumb.
  - Steps: from the head, extrude neck (`E`, `R`, `G`, `Ctrl S` saves), extrude shoulder (`E`, `S`, `R`, `G`), flatten faces (face select, select two faces, `S` `X` `0`), add a loop cut (`Ctrl R`, left click then right click to keep it centred), make the arm opening round with LoopTools Circle, `E` for arm and `E` down for torso. Hips: extrude, widen on X, delete the two bottom faces (`X` > Faces) where the legs come out, add two loop cuts (`Ctrl R`, wheel to add count), proportional edit to lower the crotch. Legs: select a ring (`Alt` click), `E` down, scale per joint (thigh, knee out in front, calf, ankle thinner), flatten the lowest ring with `S` `Z` `0`. Foot: `E` down, select vertices and press `F` to fill the sole faces, loop cuts for toe and ankle, widen on X, shape from top (`Numpad 7`). Arm: extrude with slight bulges at muscle and thinner at joints, then wrist, palm, fingers as a mitten; thumb from two side faces extruded (flatten with `S` `Y` `0`, `E`, `R`, `G`).
  - Use when / pitfalls: keep each ring scaled to match reference views from front and side and in wireframe (`Z`). Keep topology quads and avoid huge faces.

- **[modeling] Subdivision Surface and polish pass**: smooth the blocky mesh then tweak shapes.
  - Steps: Modifier Properties > Add Modifier > Generate > Subdivision Surface, Levels Viewport 2, Render 2. Object > Shade Smooth (Blender 4.1+: Shade Auto Smooth/Smooth by Angle replaces the old Auto Smooth option; 4.1 removed the Auto Smooth checkbox). In edit mode refine: `Alt` select a ring and scale up for muscle, pull shoulder and chest vertices out, knee and calf, add a loop cut near the foot sole (`Ctrl R`, click then slide) to sharpen the bottom edge.
  - Use when / pitfalls: low-poly look means skip or lower the subdivision level and keep Shade Flat. Add support loops before sharpening.

