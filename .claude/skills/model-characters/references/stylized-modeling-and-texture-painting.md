# Stylized Modeling and Texture Painting

Box-modeling, sculpting, topology and texture-painting recipes for cute, toy, clay and pixel characters and props. Routes are
checked against Blender 5.2: where a video menu moved, the 5.2 route comes first and the old name is given. Values marked
verified were read on a frame; an entry marked (heard) has no value seen on a frame.

Renames that apply to every entry below:
- Auto Smooth (checkbox) was removed in 4.1: use Object > Shade Auto Smooth or the Smooth by Angle modifier.
- Extra Objects (Round Cube, Rock Generator, Wall Factory, extra curves), LoopTools and Carver are Extensions since 4.2: Preferences > Get Extensions.
- Principled BSDF v2 (4.0+): Specular became Specular IOR Level, Transmission became Transmission Weight; Mix RGB is now Mix.
- Sculpt brushes are brush assets since 4.3 (search the brush by name in the asset shelf).

<!-- skill-navigation:start -->
## Reading Map

- [Stylized Modeling and Texture Painting](#stylized-modeling-and-texture-painting)
1. [1. Blockout and starting shapes](#1-blockout-and-starting-shapes): Reference images; Subdivided cube start; Round Cube and Quadsphere; Half model and Mirror; Blockout big, medium, small
2. [2. Shaping tricks](#2-shaping-tricks): Crease; Bevel then harden normals; Inset detail; Panel lines; Clothes as a body shell; Boolean mouth; Cylinder not cone; Curve-bevel tubes; Array and Curve; Metaball hair; Face disc and visor; Eyes on a sphere; Bevel node for seams; Checker deselect tendrils
3. [3. Splitting for rigs](#3-splitting-for-rigs): Pivot-ready parts
4. [4. Hand-worn and sculpt](#4-hand-worn-and-sculpt): Lattice and Clay Strips; Scrape wear; Carver rock; VDM brushes; Human Base Meshes
5. [5. Pixel and blocky](#5-pixel-and-blocky): Cuboid grid mob; Pixel-perfect UVs and noise
6. [6. Topology](#6-topology): Topology rules; Trace-over wireframe; Reduce to low poly
7. [7. Texture painting](#7-texture-painting): Paint setup; Brush defaults; Face mask and fill; Stencil; Alpha layers; Painted layer on tileable material; Alpha brushes; 4-colour painting; Tint without repainting; Photo to PBR; Slime
8. [8. UV notes](#8-uv-notes)
9. [9. Round chibi characters and carved faces](#9-round-chibi-characters-and-carved-faces): Cube to sphere; Chibi body; Face as loose edges; Mascot pole fix; Carved Boolean face
10. [Add-ons](#add-ons)
<!-- skill-navigation:end -->

## 1. Blockout and starting shapes

- **Reference images locked in the viewport**: drawings to model against in front, side and top.
  - Steps: drag the PNG into the viewport (it becomes an Empty, Display As Image). Object Data tab: Size 5 m, Depth Front, Show in Orthographic and Perspective, Opacity 0.15 (one video frame showed 0.089, another 25 percent for a sketch). For several views: numpad 1 and 3, select both, Shift S > Selection to Cursor. Put them in a "reference" collection and switch off its selectability with the Outliner filter arrow, so they cannot be grabbed but still edit from the properties. Use 3 or 4 viewports so every shape is checked from the side too. If the picture is crooked, rotate the Empty a little.
  - Principle: low opacity plus Depth Front shows the model through the drawing without the drawing hiding it.
  - Other tools: three.js textured plane, transparent, depthTest off; Krita reference layer beside the viewport.
  - Pitfall: hand drawings are not symmetric; model one half (one video used the right) and mirror. Front and side hands often disagree; pick one view. Extends the ortho-reference entry in `base-mesh-and-box-modeling.md`.

- **Every part starts as a subdivided cube**: head, body, ear, arm, mushroom, ghost, bunny, bean. Rounded, even quads, no sphere pole pinch.
  - Steps: Shift A > Mesh > Cube, Ctrl 1/2/3 adds a Subdivision Surface at that level (Ctrl 3 for head, body, scarf; Ctrl 2 for limbs; 1 for tiny parts). Bake with F3 "Convert to Mesh" (Object > Convert > Mesh) or Apply, then Shade Smooth. Edit mode with X-ray: scale top or bottom vertex rows, Ctrl R loop (scroll for count), proportional editing (O) with the wheel for falloff, S Z 0 to flatten a row. Sculpt Grab brush (F resizes; one frame: radius 415 px, strength 0.4) for last wobble. Bean head: face forward, back of head pushed in. To pinch an onion or mushroom cap: apply level 1 or 2, select the top vertices, Ctrl numpad plus to grow, extrude, scale; Ctrl numpad minus for a thin tip. Origin of each part goes where it will rotate (3D cursor, Object > Set Origin > Origin to 3D Cursor).
  - Principle: a subdivided cube is a rounded blob with even quads you can push, and it keeps a rig-friendly loop structure.
  - Pitfall: apply or convert before sculpting; keep parts separate until the shape is right, then join.

- **Round Cube (Quadsphere) for round bodies and heads**: a sphere made of a cube grid, no pole pinch.
  - Steps: enable Extra Objects (and LoopTools). Shift A > Mesh > Round Cube, then Operator Presets > Quadsphere (the default is Rounded Cube); Arc Divisions 4 for a frog, 8 for a flame. Subdivision modifier with edit-mode display off while shaping. Box select the top and E Z to extrude; box select the bottom, proportional on, S Z to round it; Alt click the lowest loop, proportional off, S Z to flatten the base. S Y for an oval body. Eyes: a second Round Cube, delete the back half (wireframe), S Y 0 to flatten, duplicate for pupil and highlight, shifted forward so they intersect the eye.
  - Principle: stay with quad-clean cube topology and push the shape with proportional edits rather than adding geometry.
  - Other tools: three.js has no cube-sphere; subdivide a BoxGeometry and normalise.
  - Pitfall: leave proportional editing off for the loop-flatten step.

- **Half model with Mirror, join after, mirror around another object**: build one side only.
  - Steps: delete one half in edit mode (wireframe), add Mirror (axis X). Ctrl A, Location then Rotation and Scale first or Mirror, Bevel and Array misbehave. Verified stack: Subdivision then Mirror (Merge 0.001, Clipping off) in one video; another puts Mirror above Subdivision to stop a centre crease (manatee). Parts joined with Ctrl J into a mirrored mesh inherit the mirror, so anything that must stay one-sided stays separate. Mirror Object = the body (not the origin) lets a part mirror around another object; for the crow's eye turn off X and on Y. Alternative for blocky meshes: F3 "Mesh > Symmetrize" (set +X to -X in the redo panel) instead of a modifier, then Shift S > Selection to Grid on single parts.
  - Principle: real applied symmetry avoids modifier overlap on cubes that cross the centre line.

- **Blockout big, medium, small**: scene and props from primitives first (heard).
  - Steps: floor plane, subdivided cube and cylinder cutters, a character from the Asset Browser as a human-height dummy, scale the whole scene to it. Boolean (Difference) cylinder for a window. Variation: reshape one mushroom or jar by edit-mode scale to fake many assets.
  - Pitfall: no scale dummy and shelves look huge.

## 2. Shaping tricks

- **Edge crease keeps points and grooves sharp under Subdivision**: pointed teeth, CRT screen corners, rocket bands, flat bunny base.
  - Steps: Subdivision with Use Creases on (Viewport 2, Render 2, Quality 3 shown). Select edges, Shift E, drag until the edges turn purple; or N panel > Item > Edge Crease. Rocket: Alt click a loop, Shift Alt click another, Ctrl B (wheel up once for two segments), Alt S on the centre to cut the groove, crease the outer loops, then S Z 0 on a lumpy loop to flatten it. CRT: split the screen (Shift D, P), crease the four corner edges fully, subdivide, pull the middle vertex out. Solidify shells take Edge Data > Crease Inner and Outer 0.5 to 0.75 (verified 0.5 and 0.75).
  - Principle: crease weight pins edges against Catmull-Clark smoothing.
  - Pitfall: creases do not export to engines; bake topology. The teeth crease value is not stated (heard).

- **Bevel big, apply, then bevel small with an angle limit; Solidify and Bevel for card walls**:
  - Steps: Robot body: Bevel modifier Width 0.1, a few segments, shade smooth, Apply; do small details after (C circle select, I inset twice, extrude back in for a screen), then a second Bevel: Segments 2, Harden Normals on, Limit Method Angle 40 degrees. Cardboard: Solidify Mode Simple, Thickness 0.025 m, Even Thickness on, Rim Fill on, Offset +1 on the Jaw and -1 on the Body (so shells never intersect), then Bevel Amount 0.005 m, Segments 2 to 3, Limit Angle 30, Geometry > Outer Miter Arc, Shading > Harden Normals. Today Harden Normals no longer needs Auto Smooth.
  - Principle: opposite offsets keep a gap clean; harden normals keeps flat faces flat under a bevel.
  - Other tools: harden normals equals custom split normals; keep the baked normals in three.js.
  - Pitfall: close vertices overlap bevels, move them apart first; apply scale before Bevel.

- **Inset and bevel detail on selected loops**: coat hem, cuffs, gear hubs, panel lines, belt grooves.
  - Steps: Alt click a loop (click again for the right side), C and middle mouse to deselect parts, I and drag in, select the new loops and Ctrl B for a small bevel that holds the crease under subdivision. Gear: Alt click the inner loop, F fill, repeat I and Ctrl I with small scale, Bevel with Harden Normals. Groove: Ctrl B on two loops, Alt S on the centre. Use / to isolate.

- **Clothes as a thickened shell of the body**: belt, suit, sleeves, pants that always fit, no cloth sim and no boolean.
  - Steps: duplicate the body (Shift D), rename Clothes, hide the original; L over teeth, eyes and shoes, X to delete. Alt click the cut loop, delete the rest. For a belt: Alt click two or three loops, Shift D then P, Selection. Raise a hem loop with S Z, G Z. Stack order Mirror, Solidify, Subdivision (Solidify above Subdivision; the wrong order was shown at frame 02:51). Solidify: Simple, Thickness 0.1 m, Offset -1 (shell goes inside; use +1 to push outside, 0 floats), Rim Fill on, Edge Data Crease Inner and Outer 0.5. Belt verified: Thickness 0.13 m, Offset -1, Rim Fill. Buckle: switch modifiers off, duplicate front faces, Proportional Editing off, inset, push forward on Y. Wrinkles: Sculpt Cloth brush at low strength. Button: low-side cylinder, Bevel the top. Tie: low Round Cube knot plus plane with Solidify.
  - Principle: clothes are the body surface thickened; creases stop subdivision from ballooning a thin shell.
  - Pitfall: delete loops hidden inside the head before Solidify or it artifacts.

- **Shrinkwrap for wings, brows and eye discs on a body**: parts that keep to the surface while you reshape them.
  - Steps: Shift D the body, delete to a patch, add Shrinkwrap (target body, show in edit mode on), reposition vertices to the sketch, then Solidify (offset toward 0, thickness to scale, nudge outward), then Subdivision 2 (apply Shrinkwrap before unwrapping). Wings need the body at the same subdivision level or they clip. Eye disc: Shrinkwrap to the head with Wrap Method Target Normal Project (video says Tangent Normal Project), Solidify offset about 0 so it lifts off, Subdivision 2, dissolve leftover outer loops; pupil is a duplicate whose Shrinkwrap target is the eye. Eyebrows follow the same stack: Shrinkwrap, Subdivision, Solidify (see `sculpt-stylized.md`).
  - Principle: the wrapped patch keeps the flat disc outline and stays on a curved head, like a decal in geometry.
  - Other tools: Unity and Unreal decals; three.js DecalGeometry.

- **Boolean mouth, then clean one loop**: toothy open mouth.
  - Steps: high-resolution cylinder rotated 90, scaled to the mouth. On the body add Boolean above Mirror: Difference, Object, Solver Exact (switch to Fast to apply). Apply Mirror and Boolean. Delete the inside, dissolve stray vertices, merge close ones at centre, extrude the edge loop and scale in a few times for the lip, close the open loop with Grid Fill (F3). Pull tight vertices out; Subdivision plus Smooth brush over dents.
  - Principle: the mess is only at one edge loop; fix it by hand and rebuild the inside by extrudes.

- **Cylinder, not cone, for subdivision; delete caps on joined tubes**: hats, beaks, legs.
  - Steps: Cylinder with 12 to 16 vertices, cap Fill Type N-gon on top only, scale the top ring in. Legs and beaks that join other meshes lose their cap faces first so subdivision does not collapse. S Z Z scales on local Z.
  - Principle: avoid single high-valence poles; keep quads.

- **Curve-bevel tubes for necks, ears, limbs, handles, shelves**: tapered tubes that stay editable.
  - Steps: Add > Curve > Bezier, edit points, Object Data > Geometry > Bevel Depth (about 0.05 for limbs, start 0.25 for a mug handle), Fill Caps on, Alt S on a control point tapers it, Convert to Mesh, Alt click the end loop, F, Ctrl B to round tips. Drawn limbs: delete the points, Draw tool with Surface set to Cursor, Shift D and R 180 Z for the mirror copy. Wing from a Bezier circle: Fill Mode Both, Extrude 0.1 m (very sensitive; verified), Bevel Depth 0.05, Resolution 32; Shift D with R 120 twice around the 3D cursor for three fins. Shelves: rectangle Bevel Object along Z.

- **Array plus Curve modifiers for rings and treads**: spiky collar, tank tread.
  - Steps: Bezier Circle plus one cube or triangle (scale it, never move it, apply scale). Modifiers on it: Array (Fit Type Fixed Count, Relative Offset X 1.0, start Count 2) then Curve (object = circle, Deformation Axis X). Raise Count until the loop closes (11 or 12 teeth). Collar: Ctrl T on the circle's control points to Tilt so teeth hang down, Solidify, parent the triangle to the circle, then Convert to Mesh, Alt P Clear and Keep Transformation. Tread: moving the cube along its axis scrolls the loop. Geometry Nodes Instance on Points on a Curve circle is the modern equivalent.
  - Other tools: three.js InstancedMesh along `CatmullRomCurve3.getPointAt`; Godot `PathFollow3D`.

- **Metaballs for clay hair and beard**: instant blobby hair that merges into one surface.
  - Steps: Shift A > Metaball > Ball; Metaball properties Resolution Viewport 0.1 and Render 0.1; duplicate and spread around the head, put them in a Hair collection, Ctrl P Keep Transform to the head; Object > Convert > Mesh to bake. Beard: hair particle system, Render As Object with a metaball, raise Stiffness and Resolution (heard).
  - Pitfall: a low resolution value is tighter but laggy; render to judge. Particle-metaball rendering is fragile in 5.2: use Geometry Nodes instancing. No engine equivalent, bake meshes.

- **Face disc and visor**: a flat circular face plate, or a glass visor with a rim.
  - Steps: Face disc: LoopTools Circle on a square of head vertices, select the inner faces, Ctrl numpad plus, S Y 0, E Y Y, Ctrl B on the inner edge and the outer rim. Visor: second Round Cube, side view, move forward, squash Z; wireframe, Alt click one loop, G Y to pull it in; inset with amount maxed, hold Ctrl for a thin loop, Ctrl B both edges; shade by angle 60 degrees; Ctrl J to the body.
  - Principle: a rim loop gives a visible edge so the visor reads in 3D. LoopTools Circle can twist vertices: save first and flatten overlaps with S Y 0.

- **Bevel node to soften seams where pieces join**: nubby legs that meet the body with no hard line.
  - Steps: Shader Editor, Shift A > Input > Bevel, Normal output into the BSDF Normal, raise Radius for softer. Legs: cylinder with N-gon, Alt click edge loop and Ctrl B to round the foot, delete the top face, raise the top loop so it does not poke out when rotated. Copy a swatch colour with Ctrl C over it, Ctrl V over another, then darken.
  - Other tools: Unreal and Unity have no per-pixel bevel; bake a normal map. Cycles only (the video says it failed with OptiX then; unchecked now).

- **Checker deselect for tendrils and skirts**: ghost body, ragged hem.
  - Steps: subdivided cube, extrude bottom half down, flatten with S Z, loops of similar size. Face select the bottom ring (Alt click), Select > Checker Deselect, deselect one or two more for irregularity, E extrude down, randomly scale and G move a few. Then bottom vertices with Proportional Editing and S plus wheel for a billowy skirt.

## 3. Splitting for rigs

- **Pivot-ready parts**: cut the model into pieces that rotate where they should.
  - Steps: Ctrl A apply Rotation and Scale, mirrored cubes joined with Ctrl J, F2 rename. P > By Selection splits Body, Shift D duplicates Jaw; on Jaw circle-select the tooth faces in wireframe and invert so it is a separate shell; do the inverse on Body one face row lower so no gap shows after bevel. Origin on the jaw hinge. Bend arms and legs slightly on purpose so the rig bends the right way. Finish: F3 Convert > Mesh (applies modifiers), Ctrl J, dissolve the centre mirror loop (Alt click, X > Dissolve Edges), lumpy loops by hand.
  - Pitfall: the Knife fix for shading artifacts adds a lot of geometry and was judged not worth it.

## 4. Hand-worn and sculpt

- **Lattice and Clay Strips to break CG-clean symmetry**: stylized wooden furniture and props.
  - Steps: bevelled low-poly shape, join, Convert to Mesh, one more Subdivision, Sculpt Clay Strips with a small radius in short vertical strokes for bark. Add a Lattice (Fit Lattice add-on is paid; otherwise scale a Lattice object to the model), Resolution U V W = 4 (BSpline, verified), move points in Edit mode for an aged warp, Apply the Lattice modifier and delete the lattice. Knife with Cut Through for cracks (delete, F fill, tidy). V rips vertices for leaf notches without new topology; Grid Fill (even boundary edge count) for stump tops.
  - Principle: clean shape, density, then sculpt plus lattice so it reads handmade.
  - Pitfall: apply the lattice before joining. Apply a second Subdivision if strokes look blocky.

- **Scrape wear for carved wood and soft rock**: hand-worn silhouettes from boxes.
  - Steps: model, Bevel (small width, many segments) then Subdivision, Convert to Mesh. Sculpt: Scrape (Flat Scrape) on edges, Remesh voxel about 0.1 to unify (the Carver rock verified 0.1 m, Preserve Volume), stylized stroke alpha for grain. Heavy meshes: Quad Remesher (paid) or Decimate (free, messier, fine if not animated). Dirt wall: Clay brush with big radius for muddy strips under a PBR.
  - Carver rock: enable Carver, Edit mode, Ctrl Shift X, cut type Rectangle, Space switches to Line; cut big planes into a cube, then Remesh and Scrape.

- **Vector displacement (VDM) brushes with overhangs**: stamps for hooks, rocks with caves, ornaments.
  - Steps (add-on route, verified): Preferences, enable "VDM Brush Baker"; in Sculpt Mode sidebar Misc > Create Sculpting Plane (a Grid with Multires). Sculpt the shape with overhangs. Name it, Map Resolution 512 px, Compression ZIP, Color Depth 16, Render Samples 64, Render and Create VDM Brush; a red name and "Overwrite" after creation is normal. Find it by search in the brush list.
  - Manual bake (3.5 route): Grid with Multires (Level 4); material nodes Texture Coordinate Object > Add > Multiply (2.0) > Subtract, Separate XYZ into Combine XYZ (values only partly read); image 1024 px (512 works) with 32-bit Float on; Bake Type Emit, View From Above Surface; save as OpenEXR, RGB, Half. In the brush Texture: open the EXR, Clamp OFF, Linear.
  - Principle: a heightmap cannot overhang; a vector map stores XYZ offsets in RGB.
  - Pitfall: Float, Linear and Clamp off are all required or overhangs flatten; Voxel Remesh breaks the baked UV. Check current docs: brush assets since 4.3 replaced the old append and Brush Manager steps.

- **Human Base Meshes pack and a Pixar-style eye**: stylized head in minutes.
  - Steps: download "Human Base Meshes" from the Blender demo files, Preferences > File Paths > Asset Libraries > Add, Import Method Append (not Append Reuse Data). Drag a collection into the scene, untick Instance in the redo panel for real objects. Colours are Face Sets (H hide under cursor, Shift H hide selection, Alt H unhide). Use Head Stylized with Eye Realistic for a catch light, delete Eye Stylized, parent eyes to the head. Slots Eye-White, Eye-Pupil, Eye-Clear, Eye-Iris (verified): iris faces by L, pupil ring Alt Shift click then F; front dome Ctrl numpad plus then Eye-Clear. Eye-Clear: Transmission 1.0, Roughness 0, plus Light Path > Ray Depth into a Math Less Than 2 into Alpha (Cycles only; keeps the iris bright and keeps highlights). Iris: Texture Coordinate Object > Mapping (Type Normal, Scale X 1, Y 0, Z 1) > Voronoi (3D, F1, Scale 3, Randomness 1) mixed (Clamp, Factor 0.25) with Noise 3D Scale about 5, then a blue Color Ramp.
  - Sculpt brushes named: Draw, Inflate, Pose (small for ears), Multiplane Scrape, Grab; split view numpad 1 and 3.
  - Other tools: in three.js a transparent MeshPhysicalMaterial dome with clearcoat over an iris texture (guess).

## 5. Pixel and blocky

- **Cuboid grid mob (Minecraft style)**: every part a cube, one grid square equals one pixel.
  - Steps: Render > Film > Pixel Filter Width 0.01 px. Snap > Increment, Absolute Grid Snap, Move and Scale ticked; front view, wireframe. Crab: body about 14 by 8 px, eyes 2 px cubes one pixel higher, arms 2 px thick and 5 px long, claws 3 by 5 px, 1 px overlap at every joint, legs duplicated along Y. L selects linked, Ctrl numpad plus grows to the whole body. Inset (I with Ctrl) does not snap; fix with Selection to Grid. Symmetrize instead of Mirror (see Mirror entry).
  - Principle: one limb thickness and 1 px overlaps make the model read as a single pixel grid.
  - Other tools: BoxGeometry with NearestFilter; Blockbench.

- **Pixel-perfect UVs, 32 by 32 paint, noise speckle**:
  - Steps: material with Diffuse BSDF (Roughness 0) not Principled; Image Texture on UV, New image 32 by 32 (16, 32, 64 only). Edit mode, A, U > Smart UV Project, UV > Snap Selected to Pixels; set image interpolation Linear to Closest. Texture Paint: Falloff Constant, Radius about 1 px, Image Editor Sidebar > Tool > Advanced, Anti-aliasing off; paint in 2D and 3D alternately (brush sizes are separate). Speckle: White Noise 3D into Multiply (A painted image, B noise, Factor about 0.35) into Diffuse. Pixel alpha layer for faces: Mix node A base, B "Pixel Face" 128 or 256 px with alpha 0, alpha into Factor, Closest, Radius 5 px, Strength 1, Constant falloff.
  - Principle: island edges on pixel edges plus no filtering means every dab is a whole pixel.
  - Other tools: Godot Filter Nearest; Unity Point filter. Pitfall: islands touching edge to edge bleed; nudge one pixel.

## 6. Topology

- **Topology rules and the tools that fix a mesh**:
  - Steps: quads are standard; triangles are fine on flat or game-bound parts; n-gons only on flat non-deforming faces. A pole has 3 or 5 plus edges: keep poles on the back of a hand, never in elbow, knee or mouth. Tools: Loop Cut Ctrl R, Edge Slide (G G), Merge M, Dissolve X (drops extra loops, shape unchanged), Alt click loops, Knife (snap to vertices to redirect loops), Grid Fill, Bridge Edge Loops, F2 add-on (F fills from one vertex). Subdivision with edit-mode display on shows how support loops will round the shape. Transition patterns 1 to 1, 3 to 1, 4 to 2, 5 to 3 by dissolve plus knife. Do not build topology from creases (box-modeling with sub-d creases gives bad flow; use subdivision only for smoothing).
  - Principle: even quads with loops following eyes, mouth and joints subdivide and bend cleanly. When a region is bad, delete it and rebuild inward.
  - Pitfall: too many support loops make uneven flow. First models will be bad; model anyway.

- **Trace-over a see-through wireframe**: practise edge flow over a ghost cage of a finished model.
  - Steps: delete the reference's materials, make slots White and Black. Viewport Display: White alpha 0.05 to 0.1, Black alpha 0.15 (colour black). Wireframe modifier (remove Subdivision first) Thickness 0.0025, Material Offset 1. Object Properties > Viewport Display: In Front on, Shadow off. Switch the reference off in the Outliner selectability filter. Model a new Cube with Subdivision over it.
  - Pitfall: practice only; do not re-upload other people's work.

- **Reduce a high-poly model to retro low poly (heard)**: 
  - Steps: Decimate > Un-Subdivide (quad-modeled meshes only; split into parts if it fails). Manual: Alt click a loop, Shift Alt click others, every other loop, X > Dissolve Edges, G G to slide. Plain Collapse leaves triangles; Quad Remesher and RetopoFlow are paid.
  - Pitfall: collapsing too fast can freeze the machine.

## 7. Texture painting

- **Texture paint setup**: the minimum chain to paint on a mesh.
  - Steps: apply Shrinkwrap, Solidify and Mirror first and join (Ctrl J) so one UV set works. Edit mode, A, U > Smart UV Project (raise Island Margin one or two clicks; one frame: Margin 0.01, Area Weight 1.0, Angle Limit 66). Pack Islands is in the UV menu (A in the UV editor, F3 Pack Islands). New image 4096 (2048 fine for small props), Image Texture on Base Color. Viewport Shading Solid with Lighting Flat and Color Texture, so light does not mislead colour. Save As and Save All Images (Texture Slots panel) before closing, or the paint is lost; unique names per image. Palette image open in an Image Editor to eyedrop from.
  - Principle: you paint the image, not the mesh.
  - Other tools: Krita or Substance on the exported UV layout.

- **Brush defaults and work order**:
  - Steps: TexDraw radius 137 px, Strength 0.7, Blend Mix (verified); Multiply or Screen for shadows, X swaps colours, S opens the picker, Palette (+) stores swatches. Falloff Constant for a hard flat edge; pressure on Strength, off on Radius. Eraser: Blend > Erase Alpha, Strength 1.0. Order: giant low-strength strokes for the base, small full-strength details, a dark line then a highlight for depth. Sample colours from the drawing with the eyedropper in the Image Editor. Symmetry toggle at the bottom of the viewport (Y for nostrils; off for one-sided details). Image Editor mode Paint shows a flat canvas while the 3D view updates (leaf cards; scale UVs with S X so a rectangle is not stretched, keep UVs inside the canvas).
  - Principle: low strength builds blended colour, full strength gives hard details.

- **Face mask and Fill bucket by region**: fast flat colour per part, gradients between palette colours.
  - Steps: turn on the face-selection mask next to the Texture Paint mode dropdown; in Edit mode L over parts or select faces, return to Texture Paint and only they paint. Fill tool, Color > Gradient (Linear or Radial), set RGB to HSV for a smoother falloff, Strength 1.0, Blend Mix; drag between two palette colours (beak darker at the base, eyes pale yellow not pure white). Use the same mask to paint dirt only where objects touch, with a big radius and low strength.

- **Stencil paint for a face (no UV work)**:
  - Steps: Texture Paint, Base Color image 2048 (white), brush black. Brush Settings > Texture > New, open the face PNG, Mapping Stencil. Right drag moves, Shift right drag scales (hint reads "Stencil Brush Control"). Paint over it once. Image node feeds Base Color.
  - Pitfall: not for animated faces. Krita does the same with a reference layer.

- **Second alpha layer for stickers, line work and prints**: details on top of the base colour that stay editable.
  - Steps: second Image Texture (name it, 4096, Alpha 0, black). Mix (Color), Factor 1: base in A, layer Color in B, layer Alpha into Factor, result into Base Color; pick the layer in Texture Slots to paint on it. Print with a raised ridge (LEGO): sticker Principled with Sticker Color to Base Color and Alpha to Alpha, Bump node with Sticker Alpha as Height, Strength 1, Mix Shader with Alpha as Fac (verified wiring).
  - Principle: alpha as mask and as height gives a printed-ink bump from one channel.
  - Other tools: decal layer in Unity or Unreal materials. Pitfall: set Alpha to 0 before the first stroke, or the whole mix shows the layer colour.

- **Painted colour layered on a tileable material**: paint colours only; a material supplies roughness, bump and fibre.
  - Steps: Fabric-Cotton node group (Crafty Asset sample): painted image Color into Color1 and Color2, group inputs Scale 5, AO 0.5, Bump 1, Displace 1; group into Material Output, remove Principled. Mapping (Generated, Object or Camera) so a circular pattern avoids the face. Wood: the painted image into the wood material's Color. Cardboard: Mix Shader with the material in one slot and a Paint-Brush group in the other, a new Base Color image 1024 into Fac for lettering; fibre direction fix: select one face per wrong island, L, R 90. Raise material Scale larger than life (5.0) so it reads on a phone. Dirt: Mix (Color) Multiply, Fac 1.0, grunge image in the bottom socket, a 4096 "dirt" image in Fac. Metallic only on the hilt and balls.
  - Principle: the painted layer stays simple; procedural detail does the rest.
  - Pitfall: do not use a PBR pack flat; add variation, dirt, wear.

- **Alpha stamps and textured brushes**: stitches, bristle strokes.
  - Steps: brush Texture panel > New or browse, Image Texture, Mapping Tiled (Size 1). Stitches: a free ZBrush alpha, paint with a dark colour in the base colour. Painterly brush: duplicate Paint Hard, name Painterly, Falloff the last flat preset, Texture Mask a black and white grunge with a radial edge, Strength 1.0, Radius about 23 px, Mix. The same brush painted into a normal map adds relief (Ucupaint layer add-on, not bundled: check Extensions).

- **Four-colour painted texture (heard)**: stylized wood and clay.
  - Steps: palette of four colours dark to light, 1024, fill the middle colour, smear large strokes, darkest colour for board edges and cracks, highlights beside the dark cracks, random specks last. Smear hides strokes, Blur softens small ones.
  - Other tools: Krita smudge and blur.

- **Tint without repainting**: Hue/Saturation/Value after the image (stripes: Hue 1.0, Saturation 1.5, Fac 1.0). Clay with wear: assign slots per colour, import Substance maps with all but Base Color Non-Color; unplug and re-plug a glitching normal map. Wear without Substance: cavity maps and free PBR.

- **Photo to PBR and background planes (heard)**: paint or generate a texture, make depth, normal and roughness maps (Substance Sampler Image to Material, free alternative Materialize). Photo background: depth map (a free web depth tool) into Displacement with a dense or adaptive-subdivision plane for parallax.
  - Pitfall: adaptive subdivision is Cycles only and experimental.

- **Jelly slime material (Principled v1 values)**:
  - Steps: Base Color bright green, Roughness 0, Transmission 1, IOR 1.45; Noise (3D, Scale 174.2, Detail 3.5, Roughness 1) into Bump (Strength 0.025, Distance 1) into Normal; Cycles. Today set Transmission Weight 1 and treat the rest as a start.

## 8. UV notes

- Texture paint works with Smart UV Project at default for clean cubes; raise Island Margin to avoid overlaps. Pixel and palette workflows use Snap Selected to Pixels (see section 5). Quick view: `uv-and-texturing.md` for palette atlases.
- Free alternative to UVPackmaster: built-in Pack Islands (Shape method). Packed area was 79 percent with UVPackmaster at Precision 500, Margin 0.003, Rotation Step 90 (verified).

## 9. Round chibi characters and carved faces

Checked: the cube-to-sphere blobs with Subdivision were built headless in 5.2.2 and rendered; the rest is frame-checked against the result
frames or heard (marked). Shading for these looks: `use-3d-software` `stylized-shading-recipes.md`, "Comic toon shader".

- **Cube to a perfect sphere**: Shift A cube, Ctrl 1 (Subdivision 1), apply (Modifier Tools extension adds Apply buttons), Edit Mode, A,
  Alt Shift S (To Sphere) 1.0, shade smooth, then a second Subdivision (Level 2). A cube-sphere has no UV-sphere poles to cause shading faults.
  Python: `bpy.ops.transform.tosphere(value=1.0)` in Edit Mode.
- **Chibi body in one mesh**: squash the sphere in Z (head); extrude the lower four faces with E (body); Ctrl R a loop at the waist, S to cancel
  the slide, scale Z 0 to flatten it, then LoopTools > Circle; same for the bottom ring and neck. S then Shift C scales X and Y only (works for
  G and R too). Neck loop and N panel > Item > Edge Data > Crease 1.0 keep the head-body break sharp under Subdivision. Arms and legs: cube,
  Ctrl 2, thin with S Shift C, Ctrl R loops, scale the end face; Mirror first in the stack; L then P > Selection splits parts; M new collection;
  Ctrl F2 batch rename (Set Name, prefix; Strip Characters from the end for digits and punctuation removes ".001"). Ears: subdivided cube, crease
  on the bottom face, Mirror Merge off if rotated. Result frame: head wider than body, small separate arms and feet.
- **Face as loose edges, drawn by Line Art**: plane, M > At Center (one vertex), extrude with E to draw brows, blush lines and mouth; Mirror with
  Clipping on; apply the mirror for an asymmetric blush; Shrinkwrap on the body (Wrap Method Target Normal Project, keep the mesh close to the
  body so it does not deform); no faces. Eyes and blush are subdivided planes with the same Shrinkwrap; eye shine is a duplicate, moved forward,
  white Color material, two highlights; Offset on the Shrinkwrap fixes clipping. Put face parts in their own collection (one Line Art pass reads it).
- **Round mascot from a UV sphere with a mouth pole**: halve Segments and Rings (math works in fields), rotate 90 on X so the pole is the mouth,
  add a loop around it (Ctrl R, G G slides vertices along edges), delete the back-pole vertex and Ctrl F > Grid Fill the hole (tune density and
  rotation), To Sphere again, rotate about 20 degrees on X. Feet: cubes with Mirror above Subdivision, bottom faces scaled Z 0 and positioned
  Z 0, crease 0.3, taller at the back, pointy toes; to scale up without lifting the soles set the pivot to 3D Cursor. Open mouth: extrude the
  mouth loop twice, scale, Grid Fill the last loop, crease the inner loop (frame: Mean Crease 1.00) and scale down if too open.
- **Carved face with a Boolean (hollow pumpkin pattern)**: UV sphere Segments 33 (odd, so one edge faces front), rotate 180 on Z, Alt-click every
  second loop and S Shift C to make ribs, proportional editing on the poles, face-select the ribs, Pivot Individual Origins and Orientation
  Normal to scale each. Stem: cube, E, Ctrl 2, crease 0.6 on top and bottom. Face: plane rotated 90 on X, Mirror (Clipping), Subdivision 1, Solidify
  (offset toward the body, thick). On the body: Subdivision, Solidify (hollow; above the Boolean), Boolean (Solver Manifold, the face object).
  Face object Display As Wire (the Exact solver is the slower alternative). Shade Auto Smooth 40 degrees (a Smooth by Angle modifier since 4.1) on
  the body and shade smooth the face object. Materials: Solidify Material Offset 1 for the inside; Boolean > Solver Options > Materials: Transfer
  for the carved wall. Eyes: duplicate a face of the mouth, scale Y 0. Frame check: the carved opening with wire face and mixed materials. The
  values 33, 0.6 and 40 degrees are heard.
  - Fixes: saw-tooth edges: duplicate the Subdivision, put it under the Solidify, method Simple; a flipped solidify: add an edge loop and move it
    forward. Text face: Shift A Text (centre), Convert to Mesh, rotate in Edit Mode 90 on X, Simple Deform Bend on Z, Solidify toward the target.
  - Teeth: planes, each face one tooth; Edge Split with a tiny angle, Solidify offset 0, Bevel (more segments is squarer), Subdivision. Hands the
    same: plane, Mirror, Solidify, Bevel.
  - Variants: Hue/Saturation/Value node at the end of the material, duplicate the material (number button) and nudge Hue.
  - Helpers: untick the camera icon in the Outliner for the face meshes so they do not render; parent all parts to an Empty with Ctrl P Keep Transform.
## Add-ons

- Crafty Asset pack (sample pack free on Gumroad, full paid): tileable fabric, wood, cardboard, plastic materials and googly eyes.
- Fit Lattice (paid): builds a lattice around an object; free alternative: scale a Lattice object to the model.
- Quad Remesher, RetopoFlow (paid): retopology; free alternative: Decimate or manual dissolve.
- UVPackmaster 3 (paid): denser UV packing; free: Pack Islands.
- Substance Painter / Sampler (paid): smart materials, image to material; free: Materialize, Krita.
- Free extensions: Extra Objects, LoopTools, Carver, F2, VDM Brush Baker, Ucupaint.

