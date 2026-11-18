# Quick modeling recipes

Short edit-mode tricks and prop recipes: bevel, extrude, holes, bridges, lathe, array, curve, shrinkwrap and lattice jobs, then pipes, gears, stairs, fences, rails, bottles, bookshelves and food. Hotkeys are default Blender.

## Reading Map

- 5.x names
- Bevel, extrude and inset
- Holes and clean topology
- Bridges, fills and connecting vertices
- Lathe, skin and separate parts
- Modifier recipes: array, curve, displace, wireframe
- Shrinkwrap decals and lattice jobs
- Props: pipes, gears, stairs, dice, bottle, fence, rails, bookshelf
- Props: rocks, hills, cables, food and baskets

## 5.x names

- Edit Mesh Tools (Offset Edges), Extra Curve Objects (Curve > Spirals, Knots) and LoopTools are free extensions from extensions.blender.org since 4.2. Enable them in Preferences > Get Extensions. LoopTools was a bundled add-on before 4.2. The notes say "Extra Objects" for the curve pack: the Spirals entry is in Extra Curve Objects, v0.2.0.
- Shade Auto Smooth in the right-click menu (4.1+) adds the Smooth by Angle modifier. The notes use it as "Shade Auto Smooth".
- The Displace texture type Musgrave is the legacy texture type and still exists. The shader Musgrave node became a Noise Texture type in 4.1.
- Quick Effects (Object > Quick Effects > Quick Liquid) is bundled, not an add-on.

## Bevel, extrude and inset

- **Bevel keys (Ctrl+B)**: Edit mode, select edges, Ctrl+B, drag. Scroll wheel adds segments. V toggles Affect between Edges and Vertices (vertex affect on a corner gives a concave scoop). C toggles Clamp Overlap: off lets a big width explode into spikes, on keeps edges clean. Profile while dragging: one source presses P (Superellipse to Custom, the round bevel becomes a stepped L), another presses B for the shape `unverified (the two clips name different keys, check in the editor)`.
- **Bevel Miter Outer = Arc**: Ctrl+B, Width about 0.242 m, Segments 6. In the redo panel set Miter Outer from Sharp to Arc (Sharp, Patch, Arc). Fixes ugly topology where bevelled edges meet. Panel also showed Shape 0.5, Loop Slide on, Intersection Grid Fill.
- **Extrude Manifold**: Alt+E, Extrude Manifold. Plain E leaves a ring loop at the base of the extruded faces, manifold does not. Use it to pull a face out or push it into a block.
- **Offset Edges**: enable Edit Mesh Tools. Select edges, right click > Mesh Tools > Offset Edges. Operator panel: Geometry Mode Extrude, Width 0.033 to 0.164 seen, Angle 0. Plain edge extrude self-overlaps on sharp corners.
- **Extrude to the cursor and plane lock**: Ctrl+right-click extrudes toward the click point. On a face ring press E, S, then Shift+Z to scale in X and Y only, which builds a flange without adding height.
- **Edge crease**: select edges, Shift+E, drag 0 to 1, with Subdivision Surface on. Replaces support loops.
- **Loop cut that copies an outline**: Ctrl+R over an uneven object, right click to lock the position, then E copies the flat bottom shape and F copies the zigzag top (F toggles top and bottom, E returns). Fits a picket-fence top. The right-click lock is not confirmed.
- **Flatten**: select faces or edges, S, Z, 0, Enter. Use another axis letter for edges.
- **Correct Face Attributes**: tick it in the header Options > Transform (also N > Tool > Options) in Edit mode, then extrude or scale and UVs keep their proportions (brick, wood grain on a log). Off by default.
- **Smooth edge flow**: Object properties > Viewport Display > Show Wireframe. Sculpt mode, Smooth brush (radius 50 px, strength 0.7), Deformation Surface instead of Laplacian, Auto-Masking Topology and Mesh Boundary on. Boundary stops open edges from shrinking.
- **Dyntopo then QuadriFlow**: Sculpt mode, tick Dyntopo, accept the Attribute Data warning (UVs and colours are lost). Sculpt, then Data tab > Remesh Mode Quad > QuadriFlow Remesh. Dialog: Use Mesh Symmetry, Preserve Sharp, Preserve Mesh Boundary, Smooth Normals on, Number of Faces 4000. The dialog values are partly `unverified (no frame of the dialog)`.

## Holes and clean topology

- **Round hole with LoopTools Circle**: Face mode, select a 3x3 patch (one source insets first with I), right click > LoopTools > Circle, extrude inward (E), then a Bevel modifier with Profile Superellipse and Shape 0.46. No Boolean, so no n-gons. The voiceovers say "edges" but the frames show faces.
- **Perforated surface from vertex bevel**: select grid vertices in a checker pattern, Ctrl+B then V. Redo panel: Affect Vertices, Width Type Offset, Segments 5, Shape 0.1, Width 0.026 to 0.035 m (circle size). Select one circle, Shift+G > Select Similar > Face Regions, X > Faces. Needs an even quad grid.
- **Square to round with To Sphere**: select a roughly planar edge loop, Shift+Alt+S (Mesh > Transform > To Sphere), slide the factor with the mouse until round, then extrude.
- **LoopTools Curve to re-space a messy patch**: select the damaged vertices, Ctrl+I to select the good patch, right click > LoopTools > Curve. Repeat on stubborn spots.
- **Triangulate then Tris to Quads**: Ctrl+T then Alt+J (Face > Tris to Quads) evens a tube end ring. Alt+J alone returns a triangulated torus to quads.
- **Quad direction change**: select all, Face > Poke Faces, then Alt+J. A square grid becomes a diagonal grid. For a grille add a Wireframe modifier (Thickness 0.02 m, Offset 0, Replace Original, Even).
- **Poke diamond panel (can)**: X-ray (Alt+Z), box select the body faces, Poke Faces, Alt+J, I then I again (individual), Alt+S pushes faces along normals, Shade Smooth. Keep the neck and base unselected. Needs a regular grid.

## Bridges, fills and connecting vertices

- **Bridge Edge Loops for elbows**: Ctrl+J the two objects, Edit mode, select both open ends (delete cap faces first), Edge > Bridge Edge Loops. Redo panel: Connect Loops Open Loop, Interpolation Blend Path, Profile Shape Smooth, Merge Factor 0.5. Number of Cuts: 3 to 9 in one clip, 12 to 17 in others (more cuts are smoother). Smoothness: 1.0 in one clip, 0.57 to 0.76 in others, above 1 gives an L bend (1.31 seen). Profile Factor: -0.32 to 0.75 seen, it swells or pinches the middle. Rebuilt in Blender 5.2 by script: two open-top 1 x 1 x 3 boxes 3 m apart, both open ends facing up, `bpy.ops.mesh.bridge_edge_loops(type="SINGLE", interpolation="PATH", number_cuts=12, smoothness=1.0, profile_shape="SMOOTH", profile_shape_factor=0.0)` gave the smooth U arch of the video (the API name for Open Loop is `SINGLE`; `OPEN_LOOP` raises an enum error). Select only the boundary edges of the two open ends first.
- **Grid Fill**: select all boundary edges of a hole (even count), Face > Grid Fill. Bridge Edge Loops works only between two loops.
- **Connect with J, not F**: select two vertices on one face and press J. Each press splits the face cleanly, F makes a new face and wrecks neighbours.

## Lathe, skin and separate parts

- **Lathe (bottle, pawn)**: put a front-view reference on a plane. Add a Cube, Edit mode, A, M > At Center to one vertex. E up the outline, vertex by vertex, on the centre axis. Select all, Spin tool (drag the plus handle). Bottle values: Steps 12, Angle 360, Auto Merge on (closes the seam), then Ctrl+2 and Shade Smooth. Works for a vase, glass or lamp.
- **Handrail with posts**: select the top deck edges, E up, select the new faces, P > Selection. Add a Skin modifier to the new object, Edit mode, A, Ctrl+A and drag for thickness. Add vertical loop cuts for more posts.
- **Separate parts**: Edit mode, A, P > By Loose Parts, or hover and press L, then P > Selection.
- **Mirror a part with a wrong origin**: select the part, then the body (active), Ctrl+J, move the part, A, P > By Loose Parts, then add Mirror (Axis X, Merge 0.001 m) on the part. The part now shares the body origin.

## Modifier recipes: array, curve, displace, wireframe

- **Brick wall**: one brick cube. Array Fixed Count 4, Relative Offset X 1. Duplicate the modifier (dropdown > Duplicate), second Array Count 6, X 0, Z 1. Apply both (Ctrl+A in the dropdown). Edit mode, A, Mesh > Transform > Randomize, about 0.04 to 0.07 m. Bevel modifier (Offset, 0.01 to 0.02 m, Segments 1, Limit Angle 30 deg). Move alternate rows along the wall (G, X) for a running bond.
- **Array then Curve (road, rail, ties)**: the object needs enough loop cuts. Shift+A > Curve > Path. Array Fixed Count (2 raised to 14 in one clip, 11 for railway ties), Relative Offset X (-1 sets direction, 1.7 for ties), then Curve modifier with Curve Object = the path and Deform Axis X. Array goes before Curve in the stack. Railway: select one rail edge, Shift+D, move down, P > Selection, Object > Convert > Curve for the guide, the tie is a cube.
- **Bookshelf fill**: one book, Array Fixed Count 8, X 1.0. Duplicate it, Count 4, X 0, Z about -1.12 to -1.34. Apply both. A, P > By Loose Parts. Object > Set Origin > Origin to Geometry. F3 "Randomize Transform": Rotation Y 6.4 to 8.5 degrees, Location Y 0.033 m. Set origins first or the pivots are wrong.
- **Hills with Displace**: Plane scaled up, Edit mode, Subdivide 30 cuts. Displace modifier with a new Clouds texture (Noise Basis Blender Original, Soft, Grayscale, Size 1.30, Depth 1, Nabla 0.03), Strength 1.0, Midlevel 0.5, Direction Normal. Then Ctrl+2, Shade Auto Smooth.
- **Subdivision hotkeys**: Ctrl+1 to Ctrl+5 add Subdivision Surface at that level.

## Shrinkwrap decals and lattice jobs

- **Shrinkwrap decal**: select the image plane, Edit mode, Subdivide (6 cuts seen) or it stays flat. Add Shrinkwrap, Wrap Method Nearest Surface Point, Target the model. Two sources, two settings: Snap Mode On Surface with Offset 0.02 m, or 0.044 to 0.046 m on a beanie. Snap Mode Above Surface with Offset -0.05 m (the offset sign decides if the decal floats or sinks). Raise Offset if it z-fights.
- **Lattice dent (balloon, pipe bulge)**: Add > Lattice around the poking object. Resolution: U 4, V 4, W 5 (`unverified`, the voiceover says W 6) for the balloon, 16 on each axis for the pipe. Scale the inner lattice vertices up, or Alt+Shift+S To Sphere on all. Ctrl+P the lattice to the poking object (Object Without Inverse `unverified`, or plain Ctrl+P). Add a Lattice modifier on the deformed object with Object = lattice, hide the lattice (H).
- **Lattice net**: Lattice Resolution 7 on each axis on top of the ball, scale the centre vertex with proportional editing (O), parent ball and lattice. On the net assign the rim vertices to a vertex group, set it in the Lattice modifier so only the lower net deforms.
- **Lattice carrier that slides over a sphere**: Lattice U 35, V 35, W 1 just below the object, Lattice modifier on the object, Ctrl+P (Keep Transform) object to lattice. On the lattice add Shrinkwrap (Nearest Surface Point, On Surface, Target the sphere). Header Snap > Snap To Face, Align Rotation to Target on. Parent before adding Shrinkwrap.
- **Lattice drape on terrain**: Lattice U 30, V 30 (`unverified`, heard "UV to 30"), W 1 under the object. Object gets Subdivision Surface Simple (Viewport 5, Render 2). Select the object, then the lattice, Ctrl+P > Lattice Deform. Lattice gets Shrinkwrap (Nearest Surface Point, On Surface, Target the terrain, Offset 0).

## Props: pipes, gears, stairs, dice, bottle, fence, rails, bookshelf

- **Pipe from a vertex path**: Cube, A, M > At Center to one vertex, E along an axis-aligned path. Select the corner vertices, Ctrl+B then V. Object > Convert > Curve. Object Data > Geometry > Bevel Round, Depth 1.12 m, Resolution 12 (depth matches the fitting radius). Shade Smooth.
- **Gear teeth**: Alt+click a side face loop of a cylinder, Select > Checker Deselect (even loop count only), Alt+E > Extrude Faces Along Normals, Pivot Individual Origins, S to shrink the tips, extrude along normals again, S then Shift+Y.
- **Stairs from a bevel**: Cube, Edge mode, select the top front edge, Ctrl+B. Redo panel: Width Type Offset, Width 3.16 m, Segments 14, Shape 0.5, Profile Type Custom, Preset Steps (list: Default, Support Loops, Cornice Molding, Crown Molding, Steps). Step count equals Segments.
- **Dice**: Cube, Ctrl+R loops to a 5x5 grid per face. Face mode, select the pip faces, I twice (individual), Face > Poke Faces (Poke Offset 0, Center Weighted Median), lower the Poke Offset so pips sink. Ctrl+3, Shade Smooth.
- **Chain-link fence**: Cube, delete two opposite faces, lengthen with S Y, rotate 45, duplicate a little higher, Bridge Edge Loops (2 cuts), duplicate, bridge again for a zigzag, duplicate, rotate 180, interlock, delete the overlap. Array 1: Count 11, Relative X 0.96, Merge on, Distance 0.35 m (raise if gaps remain). Array 2: Count 8, Relative X 0, Y 0.85. Subdivision Surface (Viewport 1, Render 2), Shade Smooth.
- **Align a part to a surface**: Tab, select the part's contact face, Shift+S > Cursor to Selected, Set Origin > Origin to 3D Cursor. Header Snap popover: Face Project and Align Rotation to Target on. Drag near the target.
- **Centre an object in a hole**: Set Origin > Origin to Center of Mass (Volume), select the hole edge ring in Edit mode, Shift+S > Cursor to Selected, then Object mode Shift+S > Selection to Cursor.

## Props: rocks, hills, cables, food and baskets

- **Stylized rock**: UV Sphere, Shade Smooth, two Subdivision modifiers (Viewport 4 then 1, Render 2), Displace Strength 0.05 with a new Musgrave texture (Noise Basis Voronoi F2-F1, Size 0.5, Dimension 1.2, Nabla 0.03). Enable Colors > Color Ramp, move a stop left (0.13 to 0.15 seen). The ramp value is `unverified` (no frame).
- **Cable that follows connectors**: Shift+A > Curve > Path with about 5 points. Select an end point, F3 "Hook to New Object", then Ctrl+P (Keep Transform) the empty to the connector. Repeat for the other end. Geometry > Bevel Round, Depth 0.08 m, Resolution 4.
- **Whipped cream swirl**: enable Extra Curve Objects. Shift+A > Curve > Spirals > Archemedian (spelled so): Turns 5, Steps 24, Radius Growth 0.12, Radius 0.16, stretch the height into a cone. Star profile: Circle 10 vertices, Fill Nothing, scale alternate vertices, F3 Convert > Curve. On the spiral set Geometry > Bevel to Object with the star. Alt+S the top points to taper the tip.
- **Basket**: UV Sphere, delete the top half, flatten the bottom (S Z), bevel the ring, cap with Grid Fill. Handle from a Bridge Edge Loops strip. Weave from Curve > Knots > Celtic Links (Extra Curve Objects). The fit of the weave to the bowl is not narrated `unverified`.
- **Cupcake, hot dog, cake**: see `effects-fx.md` for sauce, glaze and cheese simulations.
