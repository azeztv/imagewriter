# Paid tools to Blender

Mapping table, not tested. Written from general knowledge of each tool, not from the tutorial notes. Verify the node names in the installed 5.2 build before relying on a row. Related: `geometry-nodes.md`, `animation-and-nla.md`.

Reading map
- Cinema 4D
- Houdini
- Maya
- 3ds Max
- Cross-tool habits

## Cinema 4D

- MoGraph Cloner (grid, linear, radial) -> Instance on Points over a Grid, Mesh Line or Curve Circle primitive.
- Cloner on an object's surface or vertices -> Distribute Points on Faces or Mesh to Points, then Instance on Points.
- Cloner "Iterate" or "Random" mode -> Pick Instance with Random Value or Index modulo.
- Random Effector -> Random Value into Rotate, Scale or Translate Instances.
- Step Effector and Plain Effector with falloff -> Map Range or Float Curve on Index, or a Distance to an Empty via Object Info, into the transform.
- Shader Effector -> Noise or Image Texture node into the Scale Instances or Set Position field.
- Delay and Inheritance Effectors -> Commotion add-on offset keys, or a Simulation Zone with a blend toward the target.
- Fields (Spherical, Linear, Random, Falloff) -> a field built from Position, Vector Math Distance, Map Range and Noise Texture. Weight painting a vertex group works as a field through Named Attribute.
- Fracture and Voronoi Fracture -> Cell Fracture add-on, or Voronoi in a Repeat Zone, or Boolean per piece.
- Tracer -> Trim Curve over Curve to Points history inside a Simulation Zone, or Geometry Nodes Curve to Mesh on a stored path.
- XPresso -> Drivers and the Python expression field, or Geometry Nodes inputs keyed in the Dope Sheet.
- Redshift materials -> Principled BSDF in Cycles or Eevee, shader nodes as in `shading-and-textures.md`.
- Takes -> View Layers and Collections, or Scene copies.

## Houdini

- SOP network -> Geometry Nodes tree. The node-by-node flow maps closely.
- Scatter + Copy to Points -> Distribute Points on Faces + Instance on Points.
- Point attributes and `@P`, `@N`, `@Cd` -> Position, Normal node and Named Attribute or Store Named Attribute.
- VEX wrangle (point) -> Math, Vector Math and Set Position fields. Complex VEX has no direct node, use a Repeat Zone or a Python script.
- Attribute Randomize or `rand()` -> Random Value or White Noise Texture, seeded by Index or ID.
- Attribute Transfer -> Sample Index with Sample Nearest, or Geometry Proximity.
- Attribute Blur or Smooth -> Blur Attribute.
- For-Each loop -> Repeat Zone, or For Each Element zone (4.3+) for per-element work.
- POP network (particles) -> Simulation Zone with Distribute, Set Position, age attributes and Delete Geometry. No collision solver beyond Geometry Proximity snap.
- DOP rigid bodies -> Blender Rigid Body world or the physics Pile trick. Pyro and FLIP -> Cycles Principled Volume with Mantaflow Quick Smoke or Liquid, or the Spume solver on this machine for liquids.
- VDB from Polygons, Convert VDB -> Mesh to Volume, Volume to Mesh.
- Curve tools (Resample, Carve, Sweep) -> Resample Curve, Trim Curve, Curve to Mesh.
- Digital assets (HDA) -> Node groups with exposed inputs, saved as assets in an asset library.
- Copernicus and COPs -> Compositor or shader texture nodes.
- Solaris and USD -> Blender USD import and export.

## Maya

- Deformers (bend, twist, lattice) -> Simple Deform and Lattice modifiers.
- Blend shapes -> Shape Keys with drivers.
- Set Driven Key -> Drivers (right-click > Add Driver) with a bone Transform Channel or a custom property.
- Expressions and Mel -> Driver expressions or a Python script.
- Skin cluster, paint skin weights -> Armature modifier, Vertex Groups and Weight Paint.
- Joint orient -> Bone roll.
- HumanIK, Quick Rig -> Rigify or Auto-Rig Pro (paid). Maya Time Editor -> NLA editor. Graph Editor -> Graph Editor.
- nParticles and Bifrost -> Simulation Zone, Particle System or Mantaflow.
- nCloth -> Cloth modifier or the Cloth Dynamics node.
- MASH network -> Geometry Nodes with Instance on Points, Random Value and Distribute.
- Arnold materials -> Principled BSDF.

## 3ds Max

- Modifier stack -> Modifier stack. Turbosmooth -> Subdivision Surface. Shell -> Solidify. Symmetry -> Mirror. FFD -> Lattice. Edit Poly -> Edit Mode.
- Chamfer -> Bevel. Connect -> Loop Cut. Cap Holes -> Fill or Grid Fill.
- Scatter and ForestPack -> Instance on Points, or the Scatter and fuzz recipes in `geometry-nodes.md`.
- Array tool -> Array modifier or Shift+R repeat with a pivot.
- Spline IK Solver -> Spline IK constraint on a bone chain.
- Biped and CAT -> Rigify.
- Particle Flow -> Simulation Zone or Particle System.
- Tyflow -> Simulation Zone and Rigid Body.
- Corona and V-Ray materials -> Principled BSDF in Cycles.
- Graphite modelling ribbon -> Edit Mode tools and the Loop Tools add-on.

## Cross-tool habits

- Pivot and origin: Blender origin is per object, set with Set Origin or Affect Only Origins.
- Layers: Collections replace layers, View Layers replace render layers.
- Units: Scene > Units, apply scale before modifiers read it.
- Python: every UI action has a `bpy.ops` or data path equivalent, see `workflow-and-addons.md`.
- A row here is a starting point. If the Blender node does not exist or behaves differently, say so and look it up in the manual instead of guessing.
