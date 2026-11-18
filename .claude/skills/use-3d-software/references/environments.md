# Blender environments

This reference covers how to build natural and urban environments in Blender 5.x: terrain, scattered plants, grass, fog, light, rain, buildings from photos and water. It comes from 14 tutorials, mostly shot in Blender 2.8 to 3.6. Each entry gives the current 5.x name first and the old name in brackets. Free tools and routes come first. Paid add-ons are marked paid and have a free route beside them.

Each entry ends with `Check: verified` (the value was read on screen in the source video) or `Check: unverified` (heard only, or not shown). Values read from the video are exact. Where a value changed between Blender versions, treat the number as a starting point and tune by eye.

<!-- skill-navigation:start -->
## Reading Map

- [Blender environments](#blender-environments)
- [Version map](#version-map)
- [Build a scene in layers](#build-a-scene-in-layers)
- [Terrain](#terrain)
- [Scattering](#scattering)
- [Grass and vegetation](#grass-and-vegetation)
- [Wind and animation](#wind-and-animation)
- [Fog and volumetrics](#fog-and-volumetrics): also the fake cone god rays, dust specks, metaball clouds, a pointer to the geometry nodes scenes
- [Lighting and world](#lighting-and-world)
- [Rain and weather](#rain-and-weather)
- [Buildings from photos](#buildings-from-photos)
- [Water](#water): also the Ocean modifier foam mask
- [Camera and rendering](#camera-and-rendering)
- [Tips and tricks](#tips-and-tricks)
- [Real terrain and cities as GLB](#real-terrain-and-cities-as-glb)
- [Add-ons and assets](#add-ons-and-assets)
- [Unverified](#unverified)
- [Remastering a game scene](#remastering-a-game-scene)
<!-- skill-navigation:end -->

## Version map

These renames affect the entries below.

| Video name | Blender 5.x name | Note |
| --- | --- | --- |
| Musgrave Texture | Noise Texture, 3D, Type fBM | Merged in 4.1. Dimension becomes Roughness, so the numbers are not one-to-one. |
| Mix RGB | Mix (Data Type Color) | Same Factor, A, B, Blend, Clamp Factor. |
| Hair Info | Curves Info | Outputs Is Strand, Intercept, Length, Thickness, Tangent Normal, Random. |
| Principled BSDF Transmission, Specular | Transmission Weight, Specular IOR Level | Default Specular IOR Level is 0.5. |
| EEVEE (legacy) | EEVEE | Since 4.2 volumes use the Volumes panel (Resolution, Steps, Distribution, Max Depth). No Bloom checkbox. |
| Intel denoiser | OpenImageDenoise | Default in Cycles. |
| Filmic | AgX | Default since 4.0. The Filmic looks became AgX looks. |
| Fluid (2.81) | Fluid with Mantaflow | Since 2.82. Quick Smoke and Quick Liquid are in Object > Quick Effects. |
| Particle hair | Hair Curves with Geometry Nodes | Legacy particle hair still ships in 5.x. Wind and Turbulence force fields affect only legacy particles. |
| Glass BSDF Beckmann | GGX or Multiscatter GGX | Beckmann was removed as a choice in 4.x. |
| Sky Texture type Nishita | Single Scattering (`SINGLE_SCATTERING`) or Multiple Scattering (`MULTIPLE_SCATTERING`) | Measured in 5.2.2: no Nishita enum, no Dust input. Left: Sun Disc, Size, Intensity, Elevation, Rotation, Altitude, Air, Ozone. |
| Principled Subsurface IOR | Only enabled with Subsurface Method Random Walk (Skin) | Measured 5.2.2: under Random Walk or Burley the socket is disabled and `inputs["Subsurface IOR"]` raises KeyError in a script. With Subsurface 0 it changes nothing, so skip it. |
| EEVEE engine id | `BLENDER_EEVEE` | The only EEVEE id in 5.2.2 (scripts). Cycles is `CYCLES`. |
| Film > Exposure | `scene.cycles.film_exposure`, a multiplier (1.0 default) | Not `view_settings.exposure` (Color Management, in stops): 0.10 there is almost no change, 0.10 here dims 10x. |
| Mesh to Volume `resolution_mode`, Distribute Points in Volume `mode` | Menu input sockets `Resolution Mode` (Amount, Size) and `Mode` (Random, Grid) | Measured 5.2.2: the node properties are gone, so `node.mode = ...` raises AttributeError. Set `node.inputs['Mode'].default_value = 'Random'`. Vector Math output is `Vector`, not `Value`. |
| Noise Texture | Adds Offset and Gain inputs beside Detail, Roughness, Lacunarity, Distortion | Measured 5.2.2. Old settings still map; the new inputs default to neutral. |
| Add-ons "that come with Blender" (A.N.T. Landscape, Real Snow) | Extensions, not bundled | Install from Preferences > Get Extensions. Node Wrangler is the one still bundled. |
| Compositor Mix RGB, old output node | Mix node (Color, Blend Type), Group Output | Compositor effect nodes (Glare, Pixelate, Posterize, Kuwahara, Lens Distortion, Blur) take their settings as input sockets. See `lighting-render-and-gn-recipes.md`. |

## Build a scene in layers

**Three-layer environment.** Make a believable landscape with layers, not with detail in one layer.

Steps:
1. Big shapes: terrain, hills, large rocks and trees.
2. Mid layer: scatter several species of plants, rocks and debris at different sizes. Mask them into clumps.
3. Detail layer: ground cover, grass, leaves, sticks, wind, fog.
4. Far background: an HDRI or a photo card behind the scene instead of modelled hills.
5. Compare with a real reference after layer 2. Use PureRef (free, pay what you want) as the reference board.

Use when: any landscape, forest or meadow. The three scatter layers named are scattering, shapes and sizes, and movement. Even a still image gains from the movement layer.
Pitfall: the common rookie mistake is one type of grass. Use many sizes and species.
Check: verified [title cards 1:26 to 1:30, frames 6:48 and 7:35]

**Far background as an HDRI, not geometry.** In tunnel render, the mountains and pink sky are the "Kiara 1 Dawn" HDRI seen by the camera. The file has no image plane, photo card or backdrop mesh. The only Image Texture node is in the World.

Steps: see [HDRI sunset light](#lighting-and-world). Rotate the HDRI so the sun side sits behind the subject.
Use when: you need depth without modelling. Depth of field hides the lack of detail.
Check: verified [frames 6:48, 7:35]

## Terrain

**Canyon terrain from one displaced plane (adaptive subdivision).** A huge plane becomes mountains at render time, with only 4 vertices in the mesh. Cycles only.

Steps:
1. Add > Mesh > Plane, scale about 50x, Ctrl+A > All Transforms.
2. Render Properties: Device GPU Compute, Feature Set Experimental.
3. Add a Subdivision Surface modifier, switch to Simple, tick Adaptive Subdivision. Dicing Scale 1.00 while testing, 0.50 for the final close shots (Final Scale Render 0.50 px, Viewport 4.00 px). Levels Viewport 1.
4. Material Properties > Settings > Surface > Displacement: Displacement and Bump.
5. Nodes: Texture Coordinate > Noise Texture (3D, Type fBM, Scale 4, Detail 15, Lacunarity 2.0, Roughness about 0.5) > Math Add (Value 0.25, Clamp off) > Math Multiply (Clamp on, the other input is the noise height) > Displacement node (Space Object, Height 20, Midlevel 0) > Material Output Displacement.
6. The Add lifts the values, so the Multiply keeps the shape only above the floor and flattens the valleys. A Color Ramp with two stops works "a little better" (Add value 0.24 in that variant).

Use when: wide landscapes seen from one camera. Height 20 with Midlevel 0 gave the canyon walls.
Pitfalls: extra nodes before the Displacement socket shift the whole geometry up. A larger Dicing Scale saves memory on far or top-down views. Test with Simple subdivision before adding adaptive detail. Check that adaptive subdivision is still under the Cycles Experimental feature set on your build.
Check: verified [1:45, 2:55, 3:36, 3:48, 4:16]. The videos' Musgrave values are mapped to Noise Texture by us. Dimension 1.0 has no direct Roughness equivalent, so tune by eye. A Dicing Scale of 10 for the final is heard only, unverified.

**Canyon strata colour.** Streaky orange and yellow rock from a stretched noise.

Steps: Texture Coordinate Object > Mapping (Type Point, Scale Z 25.0) > Noise Texture (Scale 1.0, Detail 2.0, Roughness 0.5) > Mix (Color, Mix, Clamp Factor on, Factor 0.5, A peach-orange, B pale cream) > Hue/Saturation/Value (Hue 0.500, Saturation 1.210, Value 1.000, Fac 1.000) > Principled BSDF Base Color.
Use when: you want colour that follows the displaced shape. Use Object coordinates because a plane has no UVs that fit. The stretched Z scale makes streaks run along the mountains.
Check: verified [4:16, 4:42, 5:01]. Noise Scale read 5.0 at 4:16 and 1.0 at 4:42 and 5:01, so use 1.0. The swatch hex is unverified.

**Hills with a Displace modifier and Clouds texture.** A subdivided plane turned into rolling ground. No add-on.

Steps:
1. Shift+A > Mesh > Plane, S 5, Ctrl+A > Scale. Tab, right-click > Subdivide, Number of Cuts 20.
2. Add Modifier > Deform > Displace, New texture, Type Clouds (Depth 2). Add Subdivision Surface (Catmull-Clark), Levels Viewport 2, Render 2. Displace Strength 2.000, Midlevel 0.5. Right-click > Shade Smooth.
3. Turn on Edit Mode and On Cage on the Displace modifier so you can edit the displaced shape. Select a middle vertex, Numpad 1, Proportional Editing (O) on, G to lift it, scroll to grow the circle.
4. Delete vertices outside the camera frame (Numpad 7, X > Vertices) so scatter counts cover only what is visible.

variant: Clouds Noise Basis Blender Original, Type Soft, Color Grayscale, Size 0.38, Depth 2, Nabla 0.03.
Pitfall: decide the final plane size first, then apply scale. Applying scale on a small plane and scaling up later gives a different displacement.
No-add-on alternative for 5.x: Geometry Nodes, Set Position with a Noise Texture value along Normal.
Check: verified [Strength 2.000, levels 2, cuts 20 at 1:10 and 2:50 on sheets, Clouds panel at 0:52]. Midlevel 0.5 and the modifier strength are unverified.

**Ground textures and the repetition fix.** CC0 textures from Poly Haven or ambientCG on the plane.

Steps: drag a material from the Asset Browser onto the plane. If the pattern is too big or small, raise the Scale on the Mapping node in the Shading workspace. To break repetition, use free "How to Tile a Texture Without Repetition" node group (link in his video description). Delete the old Mapping node, raise the group's Scale, then use the group's sliders.
Use when: you keep your own materials in a catalog so they drag into any scene.
Check: verified [4:20 asset names]. The node group values were not read, unverified.

**Plane ground with a procedural reflective material.** Patchy wet-looking floor, no image textures.

Steps: Shift+A > Mesh > Plane, S to scale up. Principled BSDF stays non-metallic. Noise Texture (Scale 11.6, Detail 16, raise Distortion) > Bump (Height). Color Ramp on the noise Fac (stops 0.461 and 1) into Roughness with the colours flipped. A second Color Ramp from the same noise into Base Color, white made light purple, black pulled in.
Use when: you want patchy reflection "like water but not really". Put heavy detail only near the camera. Depth of field hides it.
Check: verified [10:46]

**Trees by hand, ground raised under them.** Single trees (Botaniq, paid, or Poly Haven CC0 models) placed in the shot.

Steps: place several trees. Select the ground, turn on Proportional Editing, pull the ground up where each tree sits. Use Shift+` fly navigation (WASD, Q and E) to look through the camera.
Use when: you need a few hero trees. Geometry Nodes can snap trees to the ground with Raycast or Sample Nearest Surface and lift the ground with a Weight Paint mask. This was not tested.
Check: verified [2:34 sheet, tree name approximate]

## Scattering

**Hair particles with Render As Collection (no add-on).** Scatter grass, weeds, rocks, trees or debris by instancing a collection through hair children. One plane per area keeps it art directed.

Steps:
1. Add > Mesh > Plane. In Edit Mode bevel the corners (Ctrl+Shift+B, scroll to add segments) to make a flat circle.
2. Particles > New, Type Hair, Number 1000, Hair Length 4 m, Segments 5. In Render set Render As = Collection. Untick Show Emitter in Viewport Display and Render.
3. Children = Interpolated, Display Amount and Render Amount 3, Length 1.000, Threshold 0.
4. Import the assets (Poly Haven grass, weeds, rocks). Put them in their own collection and set Render > Instance Collection to it. Whole Collection off, Pick Random off, Object Scale ticked, Scale 0.610 for grass or 0.740 for weeds.
5. Shift+D the plane around the scene. Each copy has its own particle system, so change the Seed for variety.
6. For a second layer, duplicate the plane and its particle system and point it at another collection (Weeds, Rocks).
7. Trees: Render As Object, Instance Object `Tree_Pinus-ponderosa`, Scale 0.260. Garbage: Render As Collection, Number 50, Scale 0.260. Rocks plane: Number 5, Seed 0, Hair Length 4 m, Rotation ticked (Orientation Axis Global Y), Advanced ticked.

Use when: you want many assets with less setup than a single giant particle system. Keep the child display count low for viewport speed.
Check: verified [frames 0:13, 0:19, 0:29, 0:56, 1:12]

**Save the scatter plane as an Asset Browser asset.** Reuse a configured plane in any scene.

Steps: in the Asset Browser, mark the plane and its collection as an asset (shown as `Rock_Scatter`). Save the file. In a new scene, pick the saved library in the Asset Browser dropdown and drag the asset into the 3D view. The rocks, the plane and its particle system come in. Drag again for a second patch.
Check: Asset Browser and the saved file seen, verified. The actual drag into a new scene is spoken and not shown, unverified.

**Geometry Nodes route (current, free).** The modern replacement for particle scatter.

Steps: Distribute Points on Faces on the ground (set Density from a vertex group through a Named Attribute), then Instance on Points with a Collection Info of the plants. Add random rotation and scale.
Check: unverified

**GScatter (free) base layer with many species.** A Geometry Nodes scatter add-on by Graswald.

Steps: open the GScatter tab in the N-panel. Select the ground plane as Emitter. For bought assets, select the emitter, click the asset icon, then Install asset. For other assets, select the asset in the Outliner, import it, click Scatter selected. Set Density generous. Repeat for each species. meadow used seven species, each its own system: Golden Marguerite, Musk Mallow Big, Hoary Alison Big, Viper's Bugloss Big LOD2, Wild Chamomile, Common Poppy Big LOD2 and one name cut off. His forest demo used Sycamore Maple Big LOD4 with Large Rock 03.
Pitfall: re-check GScatter against the add-on release before using it in Blender 5.x.
Check: verified [2:56 to 3:36, 5:02, 5:56]

**GScatter masks for clumps and sizes (layer 2).** Plants grow in clumps and the scene gets lighter.

Steps: select a scatter system > Distribution tab > Add Effect Layer > Mask (Noise Texture or the add-on's Musgrave mask). Edit the Color Ramp. Seen in the Distribution tab: Musgrave, scale 1.000, seed 0, Multiply, Influence 100%, then Distribution effect Distance Min 0, Density 15.000, Seed 45. In the Scale tab use a different mask type: Noise Texture, scale 4.450, detail 2.0, roughness 0.5, distortion 1.0, ramp position 0.55. Set Visualise Effect Layers = All to preview a mask on the ground.
Use when: you want viewport relief. A Distribution mask removes instances (counts went to 523 and 426). Use a different mask type per tab. Inside GScatter the mask names follow the add-on, so check them on your version.
Check: verified [frames 5:02, 5:35, 5:08 caption, 5:58 caption]

**GScatter Proximity effect to keep plants out of rocks.**

Steps: on the plant system, Distribution tab (also usable in the Scale tab) > Add Effect Layer > Proximity. Set Object (or system) to the rock scatter system. Untick "Use pivots only (faster)" so real geometry counts. Edit the curve (point 0.697, 0.176) and Distance Multiplier 1.0. Tick "Clear inside objects".
Use when: leaves grow through rocks. Make exceptions where moss belongs on rock.
Check: verified [frame 5:56]. The Use pivots box is still ticked in the frame and is unticked a few seconds later (heard).

**Geo-Scatter (paid) with a vertex-group density mask.** BD3D's scatter add-on. Free route: the Geometry Nodes route above, plus the free Biome Reader and free Plant Library.

Steps: select the ground, open the N panel Geo-Scatter tab (Density Scatter, Preset Scatter, Manual Scatter, Quick Scatter, Biome Scatter, Scatter Object(s)). Pick a biome and scatter, then add wind. To save load, paint a vertex group in Weight Paint, then in the scatter system enable the Density > Vertex Group option, choose the group, enable the layers and flip it if inverted.
Use when: you need biomes fast. Pitfall: on a big plane with applied scale, Geo-Scatter tries to fill all of it and can freeze the machine. Scatter only what is in shot.
Check: verified [panel names at 3:18]. The exact button names inside the density options were not readable, unverified.

**Particle scatter of simple cylinders.** Small tubes across a floor.

Steps: Shift+A > Mesh > Cylinder, Fill Type Nothing, Vertices 30. Scale thin and tall. Select the plane > Particles > New > Hair, Render As Object, pick the cylinder, tick Object Rotation. Rotate the cylinder Y 90 degrees so it stands (loc -15.3 m, rot Y 90, scale 0.157, 0.157, 1.538). Use Scale Randomness in Render.
Pitfall: instanced objects lie down by default. The particle number (1000 in a tile) is unverified.
Check: verified [frame 4:00 transform]

## Grass and vegetation

**Hair particle grass (legacy route, full settings).** Hair strands as grass blades on a hill. Values.

Steps:
1. Select the plane > Particles > + (new system). Rename the settings "Grass". Type Hair. Tick Advanced.
2. Emission: Number 1000, Seed 2, Hair Length 0.1 m, Segments 5.
3. Physics > Forces: Brownian 0.020. Drag 0, Damp 0. Newtonian, Mass 1 kg. Add Brownian before children.
4. Children: Simple, Display Amount 10, Render Amount 40, Length 0.7, Threshold 0.5, Seed 2, Size 1.0, Randomize Size 0, Radius 0.15 m, Roundness 0. Set display to 40 to judge density, then back to 10 for speed. Use Wireframe and Numpad 7 while tuning Radius.
5. Clumping: Clump -0.7 (positive clumps the tips, negative clumps the roots), Shape 0.074, Twist 0. Clump Noise, Roughness and Kink stay off.
6. Hair Shape: Strand Shape 0.000, Diameter Root 0.5 m, Tip 0.1 m, Diameter Scale 0.01, Close Tip on. A root bigger than the tip tapers the blade.
7. Density by painting: Object Data > Vertex Groups > + and rename "Grass Density". Disable the particle system while you paint. In Weight Paint use Draw (red is most blades, blue is none). Re-enable the system and set Particles > Vertex Groups > Density to the group.

Pitfall: nothing renders until the particle Render panel Material slot is set to the grass material.
Rebuild (5.2.2, measured 2026-11-07): the video renders in Cycles (Sample counter /1024), World signal_hill_sunrise Strength 2.0, Z rotation 300, AgX. Scene: a 2 m subdivided plane with a 0.35 m bump, Ground048 2K (Color, Roughness, NormalGL) on slot 1, "grass" on slot 2, a vertex group falling off from the centre. In bpy: `settings.root_radius`, `tip_radius`, `radius_scale`, `use_close_tip`, `shape`, `child_percent` (Display Amount), `rendered_child_count`, `clump_factor`, `clump_shape`, `render_step`, `use_hair_bspline`, `material_slot`; the seeds are on the system, `psys.seed` and `psys.child_seed`, not on the settings. With these values the blades, clumps and gradient matched the video's final render.
Check: verified [3:18, 3:44, 4:34, 5:40, 6:12 to 6:44, 8:52]

**Grass blade material with Curves Info [Hair Info] gradient and translucency.**

Steps: add a second material slot named "grass" and set it in the particle Render panel. Nodes: Curves Info [Hair Info] Intercept > Color Ramp > Principled BSDF Base Color. Ramp: dark green at the root, lighter green stops, lightest green at the tip (four stops, one at 0.881). Add Shader the Principled BSDF with a Translucent BSDF whose Color uses the same ramp. Principled values: GGX, Random Walk, Subsurface 0, Subsurface IOR 1.400, Specular IOR Level [Specular] 0.500, Roughness lowered from 0.5 to 0.137 for a glossier blade.
Variant: Principled BSDF (dark green, Subsurface 0, Subsurface IOR 1.4, Metallic 0, Specular IOR Level [Specular] 0.049, Roughness 1.000) mixed with a sandy Translucent BSDF through Mix Shader Fac 0.213.
Check: verified [11:14 ramp stop 0.881, 13:48 roughness 0.137, 3:36]. The RGB values of the stops are unverified.

**Hair Curves route (current in 5.x).** Replaces legacy particle hair for grass and fur.

Steps: Add > Curves > Empty Hair and set the Surface object to the ground. Add the Geometry Nodes hair modifiers: Distribute Hair Curves (count and density, with a Density Factor or vertex group), Clump Hair Curves (replaces Clumping), Frizz Hair Curves (replaces Kink and Brownian), Hair Curves Noise (replaces Roughness). Curves Sculpt mode has combing, add, delete and Density brushes. Mapping from the legacy settings: Number and Children become total curves with Duplicate or Interpolate Hair Curves, Hair Length becomes the curve length, Diameter Root and Tip become Set Curve Radius or the profile, Seed becomes the node seed.
Pitfall: do not mix the two systems. The Curves object has its own material slot. In 5.2.2 Empty Hair adds only a Hair Dynamics simulation modifier (measured 2026-11-08), so build the grass generator yourself (next entries).
Check: modifier names verified in the 5.2 manual. The numeric mapping is inferred, unverified.

**Hair particle grass coloured by the ground image (fastest dense lawn).** Blender Tips, "Make a grass in 45 seconds" (Blender 4.0, Eevee, no speech). The blades take their colour from the picture on the ground plane, so no grass material is built.

Steps:
1. Add > Image > Images as Planes with a grass photo (the add-on prints "Added 1 Image Plane(s)"). Tab, select all, Subdivide with Number of Cuts 50, then G Z with Proportional Editing on (Smooth falloff, size about 0.35) to raise a few bumps.
2. Object mode > Particles > + > Type Hair, tick Advanced. Defaults are Number 1000, Hair Length 4 m: set Number 80000, Seed 0, Hair Length 0.04 m, Segments 5 (a 1 m plane).
3. Physics > Forces: Brownian 0.040, Drag 0, Damp 0 (Newtonian, Mass 1 kg). Children and Hair Shape stay at their defaults, and the hair keeps the emitter's material slot.
4. Add > Light > Sun, Strength 10, Angle 0.526 (default), rotate it about 47 degrees on Y. World stays the default grey.
Principle: a hair strand reads the emitter's UV at its root, so the plane's Image Texture colours every strand with no extra node.
Pitfalls: the photo decides everything (the video's is green; Poly Haven `aerial_grass_rock` is olive and rendered straw-coloured, `grass_path_2` is beige and rendered pale). The strands show a pale sheen; lower Specular or Roughness 1 on the plane material is the likely fix, not tested.
Rebuild (5.2.2, measured 2026-11-08): Python `settings.count`, `hair_length`, `hair_step` (Segments), `brownian_factor`, `use_advanced_hair`, `material_slot` set by name. Structure, density and soft silhouette matched the video; colour differed only by the stand-in photo.
Check: verified [0:17 menu, 0:19 cuts 50, 0:22 bumps, 0:28 Hair 1000 / 4 m, 0:38 80000 / 0.04 m, 0:41 Brownian 0.040, 0:44 Sun 1.000, 0:47 Strength 10]. Version: 4.0 video, 5.2.2 rebuilt.

**Geometry Nodes hair-curve grass with wind (offset-point accumulate).** For grass that bends more at the tip. Blender 4.1 video.

Steps:
1. A scaled-up Plane and a Cube. Add > Curves > Empty Hair, Surface = the plane, open Geometry Nodes. In 4.1 the Surface Deform group holds Deform Curves on Surface; add Generate Hair Curves (an asset node group), Surface = Plane, Density raised from 20 (Hair Length 1 m, Control Points 12, Poisson Disk on). Render properties > Curves > Shape Strip, then Set Curve Radius (hold Shift to drag).
2. Per-point neighbour: Offset Point in Curve (Offset 1) > Switch (Integer): Switch = Is Valid Offset, True = Point Index, False = Index. Evaluate at Index (Vector) of Position gives the neighbour. Vector Math Subtract = neighbour minus Position.
3. Wind rotation: Align Rotation to Vector [Align Euler to Vector] Axis Z, Pivot Auto, Vector (1, 0, 0). Mix, data type Rotation, Factor = Spline Parameter Factor times (Noise Fac through Multiply Add 0.5, 0.5), A = 0, B = the align rotation. Noise Texture 3D, fBM, Normalize off, Scale 0.5, Detail 0, Roughness 0.5; its Vector = Curve Root position plus Combine XYZ with X from Scene Time times a Multiply value (sway speed).
4. Second Mix (Rotation, Factor 1.0, controls the wobble): A = Euler to Rotation of the Noise Color. Rotate Rotation (Global) with Rotation = that Mix and Rotate By = the first Mix. Feed the result to Rotate Vector on the Subtract vectors.
5. Accumulate Field (Vector, Leading) with Group ID = Evaluate on Domain (Spline) of Index, into Set Position Position, Offset = Curve Root position. Without the Group ID every blade stacks on one.
6. Toon look: Diffuse BSDF (Roughness 0, white, Normal from a Normal node) > Shader to RGB > Mix Factor. Mix A dark green (about #435930), B a Color Ramp fed by Noise Texture (3D fBM, Normalize on, Scale 0.3, Detail 2, Roughness 0.5): stops light yellow-green, yellow (#ccd42e at Pos 0.384), dark green (#49664e). Shadow none (5.x: Object > Visibility > Cast Shadow off on the Curves object). Sun Strength 10, World Color black, Color Management View Transform Standard.
7. Wind colour: Store Named Attribute "wind" (Float, Point) from the Multiply Add value and "random" (Vector, Spline) from Random Value min -1. In the shader Attribute (Geometry) "wind" > Map Range > Mix, Attribute "random" > Separate XYZ > Hue/Saturation/Value Hue with a lowered Fac.
Principle: a blade is rebuilt from per-segment direction vectors; rotating each by a gradient (zero at the root, full at the tip) and summing them bends the blade without moving the root.
Pitfalls: Offset 1 reads the NEXT point, not the previous one the narration says: with "position minus neighbour" every blade grew downward (measured 2026-11-08). The last point has no neighbour, so the switch gives it a zero vector and it repeats the point before. Mix nodes repeat socket names per data type: in bpy pick sockets by identifier (`A_Rotation`, `B_Rotation`, `Result_Rotation`, `A_Color`, `Factor_Float`), not by name. 5.2.2 node ids: Evaluate at Index is `GeometryNodeFieldAtIndex`, Spline Parameter is `GeometryNodeSplineParameter`. A 1 m blade swamped the cube; the video's final grass is about 0.4 m with radius about 0.012 (my values, tuned to its frame).
Rebuild (5.2.2, measured 2026-11-08): own hair generator (Distribute Points on Faces Density 250, Curve Line to Z 0.4, Resample 12, Instance on Points, Realize) in place of the asset. Blades lean and move between frames (tips moved 0.043 m from frame 20 to 120), the cube shadow and toon bands match; patch colour contrast and the painted sky plate did not.
Same idea in other engines: three.js, instance a thin blade mesh and sway the tip in the vertex shader with a tip-weighted noise (inferred, not built).
Check: verified [2:15 Generate Hair Curves 20 / 12, 5:05 offset 1 and switch, 5:35 vector 1 0 0, 6:35 noise 0.5 / 0, 7:35 mix, 8:35 ramp stops and Normal node, 9:15 world and Standard, 9:58 Separate XYZ]. Set Curve Radius and Density values were not shown, unverified. Version: 4.1 video, 5.2.2 rebuilt.

**Painterly grass cards scattered by Scatter on Surface, with wind and inherited colour.** Cards with a brush texture, coloured from the ground under them. Blender 5.2 video, Eevee, 2026-09.

Steps:
1. Add > Image > Images as Planes with the Grass Card Textures PNG (white blades on alpha). Top view, K knife around each clump, Enter; face select, Ctrl+I, delete faces; P > Loose Parts. Move the pieces so their bases meet the 3D cursor, Object > Set Origin > Origin to 3D Cursor, rotate 90 on X and Ctrl+A Rotation. M > New Collection "Grass_Cards", then exclude it.
2. A Plane named Grass_Plane, subdivided a few times with proportional editing for hills. Add Modifier > search "Scatter on Surface": Density Method Density, Distribution Method Poisson Disk, Density 150, Minimum Distance 0.08, Keep Surface on. Instancing: Instance Type Collection, Collection Grass_Cards, tick Pick Instance. Randomize on: Rotation 45, 45, 45, Scale Axes Uniform, Scale 0.5, Flipping 1.
3. Unpack the modifier to edit it. Wind: Noise Texture (Scale 5, Detail 2) with Vector = Position plus Combine XYZ (X = Scene Time Frame divided by 125) minus 0.5, into Rotate Instances Rotation after Instance on Points. Group Input sockets "Animation Speed" (the divisor) and "Animation Toggle" through a Switch (Geometry): False unrotated, True rotated.
4. Store Named Attribute "is_grass" (Float, Instance, 1) and "hill_normal" (Vector, normal), then Set Material with a Group Input Material socket.
5. Shader (no lighting): Attribute (Instancer) "is_grass"; Attribute (Geometry) "UV Map" and Attribute (Instancer) "UV Map" into Mix (Vector) with Factor is_grass; then Mapping (Scale 0.16, 0.48, 1; Location X driven by `#frame/-15000` for drifting cloud shadows) into the Grass Texture; Emission is the texture colour.
6. Brush alpha: Grass Card texture Alpha > Math Multiply with is_grass; Math Subtract (1 minus is_grass); Math Add with Clamp; the sum is the Fac of a Mix Shader with Transparent BSDF on top and the colour below. The ground stays opaque, the blades take the card shape. Thin blades: lower Minimum Distance.
Principle: blades sample the texture at the UV of the ground point they stand on (Instancer attribute), so the field's colour reads continuous; the card alpha only carves the blades.
Pitfalls: the creator's two textures sit behind a free Patreon sign-in (not downloaded): a stand-in card (six procedural clumps) and a procedural green texture were used. The Instancer UV needs a UV on the points: the build took it with Sample Nearest Surface of the ground "UV Map". A bmesh grid has no UV layer until you create one named exactly "UV Map", else the whole field is one flat colour. In bpy 5.2.2 `modifier[identifier] = value` on a Nodes modifier raised "id properties not supported": put the Material into Set Material and keep the socket defaults.
Rebuild (5.2.2 logic, rendered on 5.2.4 RC, measured 2026-11-08): card collection, Poisson scatter 150 per m2, rotate-instances wind (frame 20 vs 120 changed 31% of pixels by over 20 levels), inherited colour and brush alpha all worked; the painted sky, tree and light rays of the hero frame are outside the tutorial.
Same idea in other engines: three.js InstancedMesh of the cards with alpha test and a vertex-shader sway from noise of position and time; Godot MultiMesh with a spatial shader and the same sway (both inferred, not built).
Check: verified [0:55 plane and collection, 5:30 settings 150 / 0.08 / 45 / 0.5, 9:45 speed 125, 13:50 mapping 0.160 / 0.480, 15:05 final nodes]. The is_grass wiring is from the transcript, partly unverified. Version: 5.2.0 video, 5.2 rebuilt.

**Botaniq (paid) trees and plants.** Free route: Poly Haven CC0 trees and plants, or Botaniq's free version.

Steps: add trees from the Botaniq asset browser (they land in a "botaniq" collection) and use the add-on's wind tool. Free wind route: Geometry Nodes with a Noise Texture driving a small Set Position on the leaves. Not tested.
Check: the "botaniq" collection verified [5:45]. The wind use is heard.

## Wind and animation

**Wind and Turbulence force fields on hair grass (legacy particles).** Grass swaying on a hill. Values (Blender 3.6).

Steps:
1. Add > Force Field > Wind. Physics tab: Shape Plane, Strength 0.500, Flow 1.000, Noise Amount 0, Seed 54, Wind Factor 1.000.
2. Add > Force Field > Turbulence. Shape Plane, Strength 1.100, Size 2.340, Flow 0, Affect Location and Rotation on, Wind Factor 0, Falloff Sphere, Z Direction Both Z. A larger field gives a larger turbulence size.
3. Animate the turbulence: select it, press I > Location at frame 1, move it along X, key again (frame 34 in the shot). In the Timeline select the keys and press V > Vector. In the Graph Editor right-click the X channel > Extrapolation Mode > Linear Extrapolation so it keeps moving. A later second key is slower, an earlier one is faster.
4. Children = Interpolated, Display Amount = Render Amount (100), Length 1.000, Threshold 0.
5. Path through the grass: Weight Paint on the plane with the particle system disabled (Draw, Strength 1.000, radius about 50 px). Re-enable, then set Particles > Vertex Groups > Density to the group and invert it (Weights > Invert). Assign the same group to Length to fade the grass at the path edge.
6. After painting the path, lower the turbulence to Strength 0.400 (Seed 1).
7. Hair settings: Number 1000, Seed 0, Hair Length 0.63 m, Segments 5. Render Properties > Curves > Viewport Display Shape: Strip. Final Hair Shape: Strand Shape 0.000, Diameter Root 1.2 m, Tip 0.33 m, Diameter Scale 0.01, Close Tip off. Render: Render As Path, B-Spline, Steps 3.
8. Ground: duplicate the plane, name it `ground`, remove its particle systems. On the grass plane turn off Show Emitter in Viewport Display and Render, so the two have separate materials.

Use when: legacy particle grass. These force fields do not affect Hair Curves. For Hair Curves use Geometry Nodes wind.
Check: verified [0:38, 0:50, 0:53, 1:22, 2:08, 2:49, 2:52, 3:17, 3:24, 3:36]. The final Wind strength after the reduction was not shown, unverified.

**GScatter Wind effect (no simulation).** Subtle sway of every scattered plant, with Geometry Nodes only.

Steps: select the system > Rotation tab > Add Effect Layer > Wind. Defaults seen: Speed 10, Strength 10, Detail 1, Scale 0.1. Subtle sway used Speed 1.000, Strength 28.400, Detail 2.000, Scale 0.100. To share it, select another asset, click the link icon in the Rotation tab and type "w". A linked effect shows "Win 2" for two users, and changes affect every linked system.
Use when: you want low speed and strength with high detail. Strength 61.4 was a tilt test and bends too far. Strong-wind scenes need other values.
Check: verified [frames 8:28, 8:54, 8:58]

**Animate fog by driving the 4D Noise W value.** See [Ground fog from emission only](#fog-and-volumetrics). Check: heard, unverified.

## Fog and volumetrics

**Global fog box with Principled Volume.** One cube around the scene gives mist, haze and shafts. Cycles.

Steps: Add > Mesh > Cube and scale it to cover the scene. Display As Wire or Bounds if it blocks the view. New material, delete the Principled BSDF, Shift+A > Shader > Principled Volume, connect Volume to Material Output Volume. Start values: Density 0.05, Anisotropy 0.585, Absorption Color black, Emission Strength 0, Blackbody 0, Temperature 1000. A denser look: Density 0.16, Anisotropy -0.633, Emission Strength 0.03 with a pale cyan Emission Color. tunnel render used Density 0.1 with Anisotropy and colour near default.
Use when: you want atmosphere. Anisotropy is forward scatter when positive (strong shafts toward the sun) and back scatter when negative.
Pitfalls: a bigger box means less effect per unit length. Applying scale does nothing to density. The camera inside or outside the box makes no difference. The World Volume socket does not light the same way with an HDRI and Sun (the creator says the world route ignores them), so the box is preferred. Volume renders are heavy.
Edge check (the user, 2026-11-08): a fog box that ends inside the frame shows as a hard band with clear sky above it. That happens when a camera rises above its top or looks past its side, and a metro shot cranes from 1.7 m to 11 m. Make the box larger than every camera view in the shot. Fade its density to zero toward the top and sides with the height gradient below. Check a still from the highest and widest camera position for a line at the fog edge.
Check: verified [5:10, 6:26, 11:36]. The world-versus-box claim is heard [6:39].

**Volume Scatter fog (minimal god rays).** The fastest fog setup.

Steps: Shift+D the cube and scale it up. Material > New, delete the Principled BSDF. Add a Volume Scatter shader, connect Volume to Material Output Volume. Density 0.1, Anisotropy 0.9.
Use when: you pair it with a low Sun and objects between the sun and the camera. See [God rays](#lighting-and-world).
Check: verified [0:51]

**Basic fog with Light Path, Is Camera Ray.** A volume that shows only to the camera. Build it from plain nodes.

Steps: cube scaled to enclose the scene. Inside a node group "fog_basic" with inputs Fog Color (white), Fog Thick 0.010 (first set to 0.1), Anisotrop 0.850. Light Path > Is Camera Ray and the thickness go into a Math Multiply node. Its output feeds a Volume Scatter Density. Anisotropy and Color come from the inputs. Volume output goes to Material Output Volume.
Use when: you want thick fog in the shot. Thick fog is very noisy in the viewport, so look through the camera and use the denoiser. Test in Cycles first. Whether the Is Camera Ray trick works in EEVEE is unknown.
Check: verified [5:45, 7:04 values]. The group's inside is from speech and sheets, unverified.

**Height fog with a gradient.** Fog denser near the ground. It also hides seams where volume boxes overlap.

Steps: Principled Volume (Density 0.15, Anisotropy 0.881). Drive Density with Gradient Texture (Linear) > Color Ramp (Ease interpolation, stop about 0.773). Feed a Texture Coordinate (Object or Generated) into the gradient so the ramp runs along the box's Z.
Use when: overlapping background boxes.
Check: verified [9:10]. The Texture Coordinate type is unverified.

**EEVEE ground fog from emission only.** A flat box of fog on a forest floor, broken up by noise, with no Volume Scatter and no density. The engine is inferred as EEVEE from the title "Real Time Ground Fog". Render Properties is never shown, so the engine is unverified. The video is Blender 2.90.

Steps:
1. Add a cube, squash it in Z to just cover the ground area, Ctrl+A > Scale.
2. Shading workspace, delete the default nodes. Shift+A > Shader > Principled Volume, link Volume to Material Output Volume.
3. Principled Volume: Density 0.000, Anisotropy 0.000, Absorption Color black, Emission Color white, Temperature 1000, Blackbody Intensity 0.000. Only Emission Strength is driven.
4. Shift+A > Converter > Color Ramp, link Color to Emission Strength. Linear, RGB, stop 0 black, stop 1 white.
5. Noise Texture: 4D, W 1.320, Scale 1.000, Detail 2.000, Roughness 0.500, Distortion 0.000. Link its Fac to the Color Ramp Fac. Node Wrangler Ctrl+T adds Texture Coordinate and Mapping. Use the Object output into Mapping Vector.
6. Gradient Texture (Linear), Vector from Mapping. Mapping Type Point, rotation Y -90 so the gradient rises along Z (bottom is fog, top is clear).
7. Mix (Color, Blend Mix, Clamp off) [Mix RGB]: A is Noise Color, B is Gradient Color, Factor 0.276. Output to Color Ramp Fac.
8. Final tweaks: Color Ramp black stop Position 0.484, Mapping Location X -0.35 m.

Rebuild notes (Blender 5.2.2 EEVEE `BLENDER_EEVEE`, measured 2026-11-07, a stand-in forest of 0.28 m trunks 14 m tall, HDRI `kiara_1_dawn_2k` Strength 2.0, Mapping Z rotation 0, AgX):
- Units are metres, scene scale 1. The Gradient reads raw Object coordinates (Mapping Point, Rotation Y -90 gives gradient = -Z, clamped 0 to 1), so a box about 2.4 m tall (Z 0 to 2.4, centre at 1.2) gives fog that fades by half height. At 0.1 or 0.05 scale the gradient spans only 0.1 and the fog vanished at the last step. Emission adds up along the whole ray (Density 0), so a long view through a 32 x 36 m box is bright.
- Mix (Color) sockets by index: A (Noise Color) is `inputs[6]`, B (Gradient Color) is `inputs[7]`, Result is `outputs[2]`. Emission Strength is the ramp output itself (0 to 1), no extra value.
- Steps 2 to 7 gave a bright white wash up to the box top, like the video at 4:15. Step 8 as written (black stop 0.484) left no fog in this scene. Black stop 0.38 gave ground wisps like the final frame at 4:40, 0.30 a thicker bank. The exact 0.484 depends on the noise and box of the original file (not shown), so tune the black stop until the wisps read.

Use when: you want to hide a weak ground or add mood. A lowered cube alone gives a flat top, and the gradient plus noise mix avoids it. Animate by changing the noise W.
Pitfalls: match the scene around the fog before judging it. The video lights it with the HDRI `kiara_1_dawn_4k` at
Strength 2.000 (Poly Haven, CC0). Under a near-black world or in Cycles the same box reads as a flat white slab, which
is how a one-pass rebuild failed. Build the tweaks last and compare each step with the video frame at that second.
In EEVEE (4.2+) volumes use Render Properties > Volumes (Resolution, Steps, Max Depth). This entry was not re-tested in 5.x. The Emission Strength value and the cube dimensions are never shown. The black-stop colour test (HSV 0, 0, 0.290) was an experiment and returned to black.
Check: verified [frames 1:50, 4:15, 4:16, 4:25, Mix Factor 0.276]. Emission Strength, cube size and engine: unverified.

**Noise-broken fog for a Cycles landscape.** Fog with patches, tinted yellow-orange.

Steps: cube over the scene, material "Volumetrics". Noise Texture (Scale 5, Detail 2, Roughness 0.5) and a second Noise Texture (3D, fBM, Scale 5, Detail 2) [Musgrave] into Mix (Factor 0.2) > Math Divide by 10 > Volume Scatter Density. Color yellow-orange, Anisotropy 0.9. A test frame had Density 0.010 with no Divide.
Pitfall: Light Paths Max Bounces was 32, which strongly raises render time.
Check: verified [9:00, 9:30]

**Localized fog boxes.** Small volume cubes for pockets of mist.

Steps: separate cubes, each with its own Principled Volume or Volume Scatter. Keep them in a Localized Fog collection and the big one in a Globalized Fog collection. For god rays through a window, match a box to the window opening.
Use when: you overlap boxes with a gradient density to hide edges.
Check: verified [1:22 to 1:32 collections]. The god-ray box is heard.

**Cloud shader and VDB clouds.** Puffy volumes for clouds and fog.

Steps (VDB): import a VDB object with Principled Volume Density 1.700, Density Attribute "density", Anisotropy 0.531, Emission Strength 0, Blackbody Intensity 0, Temperature 1000, Temperature Attribute "temperature". For fire, raise Blackbody Intensity above 0. Import via File > Import > OpenVDB or Add > Volume > Volume Open Sequence.
Steps (procedural): BlenderKit free "Simple Procedural Cloud" material on a cube (seen: Cloud Dimensions 1.5, 0.7, 1.0, Noise Scale 1.5, Noise Detail 16, Density 2.0, Visual Location X 0.12, Size 0.43). Lower Density a lot for fog.
Pitfall: the creator called Blender's own smoke sim "a waste of 4 days". Use JangaFX free VDBs instead.
Check: verified [12:04, 13:58]

**Fake god rays with a cone card (no volume).** A long cone lit by emission and faded alpha, aligned to the light. No volume render time and no light spill. Cycles or EEVEE.

Steps:
1. Add a Cylinder, stretch it long, scale the top face down and the bottom face up. Put the narrow end at the light and align the axis with the light so the real shadows still fall inside the shaft. Object Properties > Visibility > Ray Visibility: turn Shadow off so the cone does not shade the scene.
2. Material (Principled BSDF). Texture Coordinate Generated > Noise Texture (3D, fBM, Normalize on, Scale 5.0, Detail 2.0, Roughness 0.5, Distortion 0) Color into a Mix node (Color, Multiply, Clamp Factor on, Factor 1.0) A. Texture Coordinate > Separate XYZ Z > Color Ramp (Ease, three stops, last at Position 1.000, white to black) into the same Mix B.
3. That Result goes into a second Mix (Multiply) A. Layer Weight (Blend 0.9) Facing > Invert Color (Fac 1.0) into its B. The second Result goes into the Principled Alpha.
4. Principled: Base Color white, Roughness 0.5, IOR 1.5, Emission Color light blue, Emission Strength 3.0.
Use when: shafts at almost no render cost, in a viewport that cannot afford a Volume Scatter box.
Pitfalls: the Texture Coordinate output is hard to read in the frame (Generated Z is the likely height fade, unverified). The Color Ramp middle stop is about 0.5. With the narrow end up, white-to-black on Generated Z (Z 0 is the wide end) makes the wide end brightest, as in the video. Layer Weight Facing and the Invert fade the silhouette edges, which is what makes it read as light.
Rebuild (Blender 5.2.2 EEVEE `BLENDER_EEVEE`, 64 samples, AgX, measured 2026-11-08): Alpha needs Material Settings > Render Method Blended (`material.surface_render_method = 'BLENDED'`) or it dithers. Mix (Color) sockets by index: A `inputs[6]`, B `inputs[7]`, Result `outputs[2]`. Cone 64 vertices, top radius 4 percent of the bottom, the cone's Z length equal to the light to floor distance. The build gave a soft blue-white shaft with feathered edges like the video's cone (bright wide end, faded top). The noise streaks were faint (fBM Color sits near 0.5, low contrast): to get visible streaks, steepen a Color Ramp after the noise (not in the video). The shaft is solid where it meets the floor, so end the cone just above the floor or add a second ramp that fades the wide end.
Check: verified [frame 04:55 for the node values]; rebuilt in 5.2.2. The Generated versus Normal split of the Texture Coordinate link is unverified. See also the GN "Cone light ray" in `lighting-render-and-gn-recipes.md`, a volume-shader version.

**Dust specks with a particle system.** Almost still, depth-of-field-blurred dust through the whole frame. Legacy particles still ship in 5.2. For dust that stays in a light beam, use the geometry nodes version in `geometry-nodes.md` ("Dust motes in a sunbeam").

Steps: Add a cube and scale it over the scene. Particles tab > New (Emitter). Object Properties > Viewport Display > Display As Bounds. Frame Start 1, Lifetime very high, Emission Source Volume (default Face). Field Weights Gravity 0. Velocity Normal 0, then raise Randomize until they barely move (a little gravity if they should fall slowly). Make an Icosphere (Subdivisions 2) with a Translucent BSDF, hide it off-screen. Particles > Render > Render As Object, Instance Object = the icosphere, small Scale and Scale Randomness. Children Simple: Display Amount low, Render Amount high. Give the emitter cube a transparent or volume material. Camera > Depth of Field on.
Pitfalls: the scale, child count and brightness are not given in the video, so tune by eye. Velocity Normal defaults to 1 m/s, which scatters the dust unless it is zeroed.
Check: verified [frame 00:58: Velocity panel at defaults, Field Weights Gravity 0.000]. Properties `emit_from`, `render_type`, `child_type`, `normal_factor`, `factor_random` exist in 5.2.

**Volume clouds from metaballs.** A cloud shape you can move, with texture-driven edges.

Steps: Add > Metaball, duplicate several into a cloud shape. Convert one to a mesh (Object > Convert > Mesh in 5.2; the video said "visual geometry to mesh"). Add > Volume > Empty, select it, Modifier Mesh to Volume with Object = the metaball. Hide the metaball from viewport and render. Voxel Amount: higher is better (frame shows the default 32, Density 1.0, Fill Volume on, Exterior Band Width 0.1). Add a Volume Displace modifier, press New, in Texture properties set Type to Clouds, tune the texture and the modifier. Light it with an HDRI and a Spot light. To move the cloud, unhide the metaballs and move them.
Pitfall: the metaball conversion route is unverified in 5.2.
Check: verified [frame 00:22: Mesh to Volume panel]. `MESH_TO_VOLUME`, `VOLUME_DISPLACE` and Texture Type Clouds exist in 5.2.

**Geometry nodes environment scenes.** Dust motes in a sunbeam, a footpath carved by a curve, a forest that avoids cliffs and follows a painted mask, random lit windows, and a snow layer on every up-facing surface are full entries in `geometry-nodes.md` ("Environment scenes"), each with the values read from the frame.

**Fog cards (2D fog footage on planes).** Cheap pre-rendered smoke drifting through the scene.

Steps: Add > Image > Images as Planes with fog footage. Keep the planes facing the camera with a Track To constraint. Use Emission and Alpha, or a Screen blend. In the demo the planes sit in a "2d smoke" collection, dragged and rotated with G and D around the actor.
Use when: you need fast fog. It works only from the original camera angle.
Check: verified [12:44 menu, 12:56 collection]. The Emission and Alpha wiring was never shown, unverified.

**Shaped sunlight with a noise-alpha plane.** A plane between the sun and the fog breaks the light into shafts.

Steps: add a plane in front of the sun, new material, Principled BSDF with Alpha from Noise Texture > Color Ramp (first stop 0.200, then a stop at 1). Noise Scale 4.6 or 8.1, Detail 2, Roughness 0.5. The Sun shines through the clear parts. Thicker fog and a view toward the sun give clear god rays.
Pitfall: in EEVEE alpha is a stochastic mask, so test it there.
Check: verified [6:28 Ramp 0.200]. Noise Scale 4.6 versus 8.1 is unverified.

**God rays with a low Sun and Nishita sky.** Shafts through gaps between objects.

Steps: floor and cubes. World > Sky Texture, Nishita [Single or Multiple Scattering in 5.x], Sun Disc on, Sun Size 0.545, Sun Intensity 1.0, Sun Elevation 15 (animated to 5), Sun Rotation 0. Render Properties > Film > Exposure 0.10 (`scene.cycles.film_exposure`, a multiplier). Add the Volume Scatter box (60 x 60 x 20 m was enough). Move small cubes into the sun path to find the shaft angle. View in Cycles rendered mode.
Rebuild (5.2.2 Cycles, 64 samples, AgX, measured 2026-11-07): with Exposure 0.10 and Elevation 5 the haze turned golden brown with a dark backlit cube like the video at 0:51. At Elevation 15 with no volume the scene is blown white (video 0:33). Sun azimuth and camera are not in the source: keep the camera looking toward the sun side, or the cube front is lit and the haze reads blue-grey. Elevation 15 plus the volume gave a dim blue haze, not the white of 0:33, so the 0:33 frame had no volume yet.
Use when: the low exposure stops the sun from blowing out. Anisotropy near 0.9 makes the shafts.
Check: verified [0:33, 0:58]

**Mist pass compositing.** Add fog in post with control.

Steps: View Layer Properties > Passes > Data: Mist. Optionally add Volume Direct and Volume Indirect. World Properties > Mist Pass: Start 5 m, Depth 500 m, Falloff Quadratic. Compositor: Render Layers Mist > Color Ramp (stop at 0.887) > Mix Screen (or Multiply) over Image > Composite. Denoise the Noisy Image.
Use when: you want to change fog density without re-rendering. In 5.x the compositor setup changed (no Use Nodes checkbox), so check before scripting.
Check: verified [7:58]

**Render settings for volumes.**

Steps: Light Paths > Max Bounces > Volume: default 0, set 1 for hazier fog. Render Properties > Volumes: Step Rate Render 1.0, Viewport 0.10 to 0.70, Max Steps 1024. A lower step rate gives more detail and a slower render (tested at 0.10 on clouds). Noise: Max Samples 35 viewport and 100 render, OpenImageDenoise, Denoising Data prefilter Accurate, Start Sample 35. For video, the free Super Image Denoiser add-on (Pidgeon Tools) removes flicker between frames. To render volumes separately, render the scene without volumes and the volume collection on its own, then mix with Screen or Add in the compositor (heard only).
Pitfall: volume bounces and low step rates raise render time. The step rate matters mostly for clouds and small boxes.
Check: verified [16:00 to 16:40, 12:04, 16:50, 9:10]. Separate render node details: unverified.

## Lighting and world

**HDRI sunset light with rotation control.** One HDRI lights the scene and shows as the background.

Steps: World Properties > Surface > Surface = Background, Color = Environment Texture, open the .hdr (Linear, Equirectangular, Single Image). Z for rendered view. Shader Editor set to World. Add Texture Coordinate and Mapping (Node Wrangler Ctrl+T does both): Generated > Mapping Vector > Environment Texture Vector. Rotate in Z until the sun side sits right.
Strengths used: tunnel scene 0.3 (heard), fog forest scene 2.000 (`kiara_1_dawn_4k.hdr`), a third scene 0.3 with Z rotation -112 degrees (`kloppenheim_06_4k.hdr`), a fourth scene 2.0 with Z rotation 300 degrees (`signal_hill_sunrise`), a fifth scene 0.25 (`shanghai_bund_4k.hdr`). All are Poly Haven CC0.
Pitfalls: in the old EEVEE, turn Bloom off first. EEVEE (4.2+) has no Bloom checkbox, so use a Compositor Glare. In scene, hovering over the colour dot and pressing E picks Environment Texture.
Check: verified [7:35 node tree, fog forest 3:52 to 4:25, 5:45, 7:32 and 14:16]. Tunnel scene rotation values and the 0.3 strength are unverified.

**Strong sun with a dim HDRI.** look.

Steps: Sun Strength 25 (he says 25 to 35), Angle 0.526 degrees, Max Bounces 1024, Cast Shadow and Multiple Importance on. HDRI strength about 0.3. Sun Strength is in W/m² in 5.x, and 25 is still fine.
Check: verified [4:20, 5:45]

**Sun lamp plus HDRI without a paid add-on.** One build used a "Starlight Sun" from the paid Physical Starlight Atmosphere add-on with an HDRI. The free route is a Nishita Sky Texture plus a Sun lamp, or any Poly Haven HDRI.
Check: the "Starlight Sun" name verified [9:00, 7:57]. The HDRI is never shown, so its name is unverified.

**Emissive inner tubes and a back light.**

Steps: give the ring two materials, Metallic (Principled, Metallic 1) and Emission (Strength 50, purple). In Edit Mode, Face select, Alt+click the inside faces, pick the emissive slot, Assign. Add a Point light behind the character (Size 0.25 m, Max Bounces 1024, Emission strength 100).
Use when: you need to separate a subject from a dark background. Alt+click can select the wrong side.
Check: verified [12:58 light]. The emission 50 is heard.

**Tunnel of rings with an Array modifier.**

Steps: Cylinder, Fill Type None, 50 vertices. R X 90, scale, Ctrl+A all transforms. Solidify then Apply. Bevel (Width 0.01 spoken, Segments 5, Limit Method Angle, Width Method Width), Shade Smooth. Add an Empty at the first ring. Array modifier: untick Relative Offset, tick Object Offset, pick the Empty. Move the Empty back and scale it slightly so each copy is smaller. Fit Type Fixed Count, about a dozen. Camera: Ctrl+Alt+Numpad 0 snaps it to the view. Put the camera on the tunnel's centre axis.
Check: verified [1:20 bevel panel, Width 0.1 m still being dragged]. Other values are from speech, unverified.

## Rain and weather

**Rain with an emitter plane and object particles.** The drops fall onto the road. The chain is: drops, Dynamic Paint splash, wet map, waves, material, splash cards.

Steps:
1. Drop mesh: Add Ico Sphere, in Edit Mode pull the top vertex up (G Z, Proportional Editing on Sharp falloff), scale thin, Shade Smooth. Material: delete Principled BSDF, add Glass BSDF (GGX, IOR 1.330, Roughness 0.000).
2. Duplicate the road plane and move it up in Z. A higher plane gives a faster fall.
3. Particles > New, Type Emitter. Number 1000 while testing, later 100,000 then 200,000. Seed 0, Frame Start 1, End 250, Lifetime 50 (about 36 to 37 so drops vanish after landing), Lifetime Randomness 0. Velocity > Normal -1 m/s, other velocity 0. Render As Object, Instance Object the drop, Scale 0.050, Object Scale on, random scale on. Untick Show Emitter.
4. Save the file, then Cache tab > Bake.

Pitfalls: bake after any change or the drops will not match the Dynamic Paint bake. Save the .blend first or the cache has no folder.
Check: verified [3:44, 4:05, 4:12, 4:22, 17:08]. The 100,000 and random scale are heard, and the vertex pull is heard. Glass is shown as Beckmann in the video and mapped to GGX by us.

**Dynamic Paint splash canvas and brush (step 2).** The falling drops paint white dots on the road that shrink, giving a splash texture sequence.

Steps:
1. Road > Physics > Dynamic Paint > Type Canvas. Surface "Surface": Format Image Sequence, Resolution 1024, Anti-Aliasing on, Frame Start 1, End 250, Sub-Steps 0, Surface Type Paint. Effects: Shrink on, Speed 0.60. Initial Color black. Dry off. UV Map UVMap. Output Cache path //Splash, PNG. Click Bake Image Sequence.
2. Emitter plane > Physics > Dynamic Paint > Type Brush. Paint Color white, Alpha 1.00, Wetness 1.00, Absolute Alpha on, Erase Paint off. Source Paint: Particle System, pick the drops settings. Effect Solid Radius 0.01 or 0.02, Smooth Radius 0, Use Particle's Radius off.

Pitfalls: run the particle bake first. Solid Radius sets the dot size, which sets the splash size.
Check: verified [5:24, 5:30, 5:42, 6:58]. The 0.01 versus 0.02 Solid Radius is a speech and frame conflict, so the final is unverified. Dry off and the folder name are heard.

**Wet map and Waves surfaces (step 3).**

Steps (wet): on the canvas add a second surface. Untick Paint Maps, tick Wet Maps. Shrink off, Spread on with Speed 0.06, Dry on with Time 140 to 150 frames. Output folder "wet". Bake.
Steps (waves): third surface "displace", Image Sequence, Resolution 1024, Sub-Steps 2. Surface Type Waves: Open Borders on, Timescale 0.80, Speed 0.30, Damping 0.04, Spring 0.20, Smoothness 0.30, Sub-Steps 1, Scale Influence 1.00, Radius 1.00. Output File Format OpenEXR (not PNG), folder "waves". Bake.
Pitfall: the waves bake looks empty in an image viewer because it is float data. The wet map drives roughness and darkening later.
Check: waves verified [8:00 to 8:18, 8:38]. Wet values are heard, unverified. The 8.3 Speed in the transcript is a mishearing of 0.3.

**Road material that reads the three bakes (step 4).**

Steps: Image Texture nodes set to Image Sequence with Auto Refresh and Cycles on. Splash: add the splash image over the colour with a Mix Shader, and a Color Ramp controls how much white shows. Wet: Image Texture > Invert > Mix (Multiply, Data Type Color) [Mix RGB] into Roughness, and a duplicate Multiply on Base Color to darken. Waves: Image Texture (EXR sequence) into the Height of a Bump node after the Normal Map node, with the strength turned down. Match each sequence's frame count to the bake (250).
Check: heard, node layout seen on sheets, exact values unverified

**Fluid splash sprite, render once and reuse as a card.**

Steps: default Cube is the Fluid domain. An Ico Sphere inside is a Fluid Flow, Type Fluid, initial velocity Z about -10 m/s. A flattened cube at the bottom is a Fluid pool. Domain: Final Resolution 100, Preview 45, Time Start 0, End 4.000, Speed 0.500, Generate Speed Vectors on, Boundary Type Partial Slip, Amount 0.200, Surface Smoothing 1.000, Subdivisions 2, Remove Air Bubbles on, Particles 0.2. Bake a few minutes and stop when the splash has peaked. Shade Smooth the mesh. Camera at the side. Untick Show in Renders and Show in Viewport for the sphere and pool. Water material: Glass BSDF IOR 1.33, Roughness 0. World `shanghai_bund_4k.hdr`. Render Properties > Film > Transparent on. F12 and save PNGs at two different frames (Splash1.png, Splash2.png).
Check: verified [12:02, 12:09]. The HDRI Mapping Z rotation (about 40) is unverified. The video used the old 2.81 Fluid. Mantaflow Fluid is the current route.

**Splash cards scattered with hair particles.**

Steps:
1. Shift+A > Image > Images as Planes with the PNGs. In Edit Mode put the origin at the bottom of the splash and scale up in Z. Material: Principled BSDF IOR 1.33, Roughness 0.1, then a Mix Shader at the end with Transparent BSDF in the second socket (Fac about 0.2) and a Hue/Saturation/Value node to lift Value. Duplicate the plane, make its material single user, use Splash2.png at another scale.
2. Ctrl+G the two planes into a collection "raindrops". Delete lamps so only the HDR lights the scene.
3. Road > Particles > New, Hair, Advanced. Render As Collection, Instance Collection raindrops, smaller Scale, random scale, Count 200,000. Rotation on, Orientation Axis Normal, a different Phase and Random Phase.
4. Particle Textures tab: New texture, the white-dot splash image sequence, Auto Refresh on, Mapping Coordinates UV. Influence: untick Time, tick Density.

Use when: you fake a 3D splash with 2D cards that each have a different rotation phase and scale.
Pitfalls: the viewport does not refresh the sequence per frame, so click Refresh in the texture panel (renders are fine). For alpha artefacts, untick Film > Transparent and set Light Paths > Max Bounces > Transparency to 64.
Check: verified [17:34 Transparency 64, Total 12, Diffuse 4, Glossy 4, Transmission 12, Volume 0, 17:08 count]. Fac 0.2 versus 0.22 is unverified.

**Rain Kit (Jepe, free).** A Geometry Nodes rain and splash add-on. Notes come from frames only. It was not downloaded because it sits behind an email form.

Steps: File > Append > rain_generator.blend > Collection > Rain Kit. It holds Droplet, Rain Splash and Rain Zone. Select Rain Zone > Modifiers > Geometry Nodes "Rain Zone". Droplet: Amount 3247, Scale 0.170, Fall Speed 0.500, Instance Droplet. Zone: Size X 8.550, Y 11.940, Z 8.680, Tilt X 4.130, Tilt Y 0.000, Outline on. Play the animation.
Splashes by weight: Shift+A > Mesh > Plane, scale, Ctrl+A > Scale. Add Modifier > Geometry Nodes > Rain Splash (Density 1.000, Z Limit 0.000, Drops/Splash 4, Power 1.000, Speed 0.700, Droplet Radius 0.019). Edit Mode, right-click > Subdivide, Number of Cuts 60. Vertex Groups: add "Density", set the modifier's Vertex Group to it. Weight Paint with Draw, weight 1.000, strength 1.000.
Use when: you raise Amount about 10x for heavy rain, and tilt slants it. The plane needs dense geometry or the stroke is blocky.
Check: verified [0:46, 1:10, 1:19]. Blender version and brush size unverified. In 5.x the modifier panel may differ.

## Buildings from photos

**Block the street, then light it early.**

Steps: block buildings with extruded boxes and edge loops. Decide the camera view. Add a point light in a doorway or alley and a night HDR at the same time.
Use when: you fix composition before texturing. Ian says to be lazy about detail.
Check: heard, unverified

**Facade photo by Cube Projection.**

Steps: select a building > New material > Base Color > Image Texture, load a facade photo. UV Editing workspace, load the image. Select all faces, U > Cube Projection. Move UVs until the photo lines up with the model. Back in modelling, add edge loops and extrude pieces in or out.
Pitfall: re-project stretched faces with U > Project From View, then line them up. The facade photos came from textures.com (free tier, not CC0, terms unverified). Use CC0 photos from Poly Haven or ambientCG textures when you can.
Check: verified [0:12, 0:16]

**Pop out details with Knife and Inset.**

Steps: K Knife to trace the shape on the facade. I Inset (Boundary on, Offset Even on) for panes, then extrude in or out. Offset random edge loops and vertices so nothing is perfectly straight.
Check: verified [0:27 panel]. The thickness value is unreadable, unverified.

**Window material.**

Steps: select the pane faces > New material "windows" > Assign. Image Texture colour into a Translucent BSDF into Material Output Surface (Glossy is the other option). Add point lights in windows if you want.
Use when: you want glowing windows without modelling interiors.
Check: verified [0:42 node link]. The Alpha use at 0:39 is unverified.

**Straighten crooked UVs with UV Squares (free add-on).**

Steps: enable the add-on in Preferences. In the UV Editor select the islands and use "To Grid By Shape". Other buttons: Snap to Axis, Snap with Equal Distance, To Square Grid, Rip Vertex, Rip Faces, Snap to Closest Unselected, V Join Stitch, I Toggle Islands. Do the same for the street unwrap.
Pitfall: its packaging for the 4.2+ Extensions platform is unverified.
Check: verified [0:45 to 0:50]

## Water

**Water as a second plane.** Transparent turquoise water with a fine ripple bump. Cycles.

Steps: duplicate the terrain plane at the same scale and move it up to sit in the canyon. New material "Water". Principled BSDF: Transmission Weight [Transmission] 1.0, Roughness 0.05, Specular IOR Level [Specular] 0.1, Base Color azure or cyan, IOR 1.450. Bump node Strength 0.35, Height from Noise Texture (3D, fBM, Scale 200, Detail 15, Lacunarity 2.0) [Musgrave Dimension 1.0]. Volume socket: Emission shader of the same colour (lighter green) at Strength 0.100.
Use when: the fog cube and sun are there to sell it. Transmission is heavy to render.
Pitfall: the video's Specular 0.077 became 0.100 later, so use 0.1. Specular IOR Level has a different scale (default 0.5), so compare by eye.
Check: verified [5:42, 6:16, 7:07]

**Ocean modifier with a foam mask.** Animated waves with foam driven from the modifier's own data layer. No add-on.

Steps: Add a plane, scale up. Add Modifier > Physics > Ocean (in the Generate group in older builds). Resolution Viewport to what the machine handles (frame: Viewport 30, Render 7), any Random Seed. Waves: Scale 3. Foam: tick Foam, Data Layer name `Ocean`, Coverage 0.2. Material: Principled BSDF and an Emission into an Add Shader into Material Output Surface. Attribute node (Type Geometry, Name `Ocean`) into a Color Ramp Fac into the Emission Color. Principled Base Color dark blue, Transmission Weight [Transmission] 1.0. The Color Ramp sets how much foam shows. Animate: hover Time in the modifier and press I, move the timeline, change Time, press I again.
Use when: a cheap animated sea with white caps. Choppiness raises sharp crests, Scale raises the swell, Wind Velocity down gives ripples.
Pitfalls: the Attribute name must match the Data Layer name exactly. The foam value `Time` for natural motion was heard as both 5 and 6 over 120 frames, so tune by eye. The `effects-fx.md` entry has more modifier values.
Check: verified [frames 00:12, 00:30: Scale 3.000, Foam on, Data Layer Ocean, Coverage 0.200, Attribute and Color Ramp wired]. `OCEAN` modifier exists in 5.2.

## Camera and rendering

**Depth of field with a focus empty.**

Steps: Add > Empty, move it to the subject, rename "focus". Camera properties > Depth of Field > Focus Object = focus. Aperture Type Radius, Size 0.04 m, Blades 20. Switch to rendered view and adjust Size until the blur looks right.
Use when: you want blur to hide detail on the floor. One build used a "Focus Master" empty (f-stop values not readable).
Check: verified [12:38]

**Low rain camera with pentagon bokeh.**

Steps: second camera near the ground: Focal Length 80 mm, Depth of Field on, Focus Distance 1.8 m, Aperture Blades 5 for pentagon bokeh (with a small f-stop). HDR strength 0.25. Motion Blur on, shutter about 0.5 to 0.6 (Render > Motion Blur). Color Management: the video used Filmic with Look High Contrast, so use AgX with a contrast look in 5.x. Compositing: Render Layers > Filter > Denoise > Composite. Test with 128 render samples and 32 viewport samples. The final was said to be about 1000 samples.
Pitfall: Film > Transparent must be off for the final or the splash cards break.
Check: verified [18:30, 17:34, 18:48 Film Transparent off]. The Look High Contrast and the 1000 samples are heard, unverified.

**Second camera with markers.**

Steps: copy the camera. In the Timeline with the camera selected press Ctrl+B (Bind Camera to Markers) at the first position, jump to the second frame range, press Ctrl+B again. Delete the copy's keyframes and change its angle.
Check: heard, 7:36 to 7:46 sheets. The DoF values are unverified. The 5.x keymap is unverified.

**Final render settings used by the grass and tunnel videos.**

Steps: Cycles, Device GPU Compute, viewport Noise Threshold 0.1, Max Samples 1024 viewport, 128 final. Output 1920 x 1080 at 100%, 30 fps, PNG, RGBA, Depth 8, Compression 15%. F12.
Steps: 1920 x 1080, 24 fps, PNG RGBA, 128 samples on the GPU while working, 500 final (spoken), denoising on, "maybe 1000 if still noisy".
Check: verified [14:30, 13:08 and 11:50]. The 128 final samples and 500 are heard, unverified.

**Handheld camera.** The free Camera Shakify add-on (EatTheFuture, GitHub) adds handheld motion. One build used a top-down camera with a raised Dicing Scale to keep render time sane.
Check: unverified (listed in the description, "CameraShakify.v2" seen in the Outliner)

## Tips and tricks

- Fake detail with ground fog: it hides weak grass in a client scene (, heard).
- Cheat the camera angle and scatter far less geometry (, heard).
- Use premade assets instead of modelling or scanning everything (, heard).
- Trees raise the ground they grow on. Lift the terrain under them (, heard).
- While you work, keep children low and the Render Preview on, then return to 100% (, heard).
- Black-and-white grading suits fog scenes (, heard).
- In Photoshop or Resolve, Screen or Color Dodge for fog cards, then curves (, heard).
- A fake EEVEE volume with a light flare comes from a Gleb Alexandrov tutorial (, heard, the node tree never shown).
- Link materials between planes: select the new one, Shift+click the textured one, Ctrl+L > Link Materials (, verified at 5:00).
- Weight Paint a vertex group to place splashes or grass, and subdivide the plane first (, verified at 1:19).
- Hide fluid helper objects by unticking Show in Renders and Show in Viewport (, heard).
- Photos that do not look like photos: break up straight lines with small random edge and vertex offsets (, heard).
- Add a story prop (a swing, a figure) to a quick nature scene (, heard).
- Hotkeys: Ctrl+A apply, Ctrl+T Node Wrangler texture setup, Shift+A add, V keyframe handle type, Ctrl+Shift+B bevel vertices, Shift+D duplicate, Ctrl+Alt+Numpad 0 camera to view, Ctrl+B bind camera to markers, O proportional editing.

## Real terrain and cities as GLB

- **Real city blocks**: [codepawl/plateau-city-glb](https://huggingface.co/datasets/codepawl/plateau-city-glb) has 797 Japanese city tiles from PLATEAU (CC BY 4.0) with a [viewer](https://huggingface.co/spaces/codepawl/plateau-city-glb-viewer) to pick tiles. Import the `engine/` tier into Blender, then add fog, scatter and lighting from the sections above.
- **Real terrain**: [codepawl/mars-hirise-terrain](https://huggingface.co/datasets/codepawl/mars-hirise-terrain) has 320 Mars HiRISE tiles ([viewer](https://huggingface.co/spaces/codepawl/mars-hirise-terrain-viewer)). Credit NASA/JPL/University of Arizona as the card says. Recolour and scatter rocks on it for any desert or alien landscape.
- More free GLB packs (props, scans, robots, anatomy, mocap): the CodePawl table in the `3d-generalist` asset reference, or https://huggingface.co/codepawl.

## Add-ons and assets

| Name | Free or paid | Licence | What for | Link |
| --- | --- | --- | --- | --- |
| Node Wrangler | free, bundled | GPL | Ctrl+T texture setup, still bundled in 5.2 (measured 2026-11-08). Ctrl+Shift+T sets up a full PBR set from picked files | in Blender |
| Scatter Objects | free extension (id `scatter_objects`) | not stated | select the object, Shift-select the surface, F3 "Scatter Objects", drag over the surface, Enter. Not run in 5.2 | Edit > Preferences > Get Extensions |
| Sapling Tree Gen | free extension | not stated | Shift+A > Curve > Sapling Tree Gen: branches, leaves, wind options in one panel. Menu path not run in 5.2 | Get Extensions |
| A.N.T.Landscape | free extension (id `antlandscape`), not bundled in 5.2 | not stated | Shift+A > Mesh > Landscape, presets Canyon, Mountain, Cliff. Change values in Adjust Last Operation before clicking anything else. Alt+D linked copies at other scales fill a view with cliffs and distant mountains. Menu path not run | Get Extensions |
| Copy Attributes Menu | free extension | not stated | Ctrl+C on a selection copies rotation, location and more between objects | Get Extensions |
| Tri-lighting | free extension | not stated | three-point lights with Track To (see `lighting-render-and-gn-recipes.md`) | Get Extensions |
| Real Snow | not bundled in 5.x, unverified | not verified | snow on selected faces (N panel > Real Snow > Add Snow). The video called it pre-installed, which is out of date | Get Extensions or its own page |
| fSpy | free, separate app plus a Blender importer, not on extensions.blender.org | not verified | camera match from one photo (see Unverified) | fSpy project page |
| Import Images as Planes | free, bundled | GPL | fog and splash cards | in Blender |
| Poly Haven | free | CC0 | HDRIs, textures, models, plants, rocks | https://polyhaven.com |
| ambientCG | free | CC0 | textures (V2 used Ground048_2K) | https://ambientcg.com |
| GScatter (Graswald) | free add-on, free starter assets | not stated | Geometry Nodes scatter with effect layers | https://bit.ly/GScatter |
| Graswald asset library | paid (starter assets free) | Graswald plan | scanned scatter assets | in GScatter |
| Geo-Scatter (BD3D) | paid | commercial | scatter, biomes, wind. Free route: Geometry Nodes scatter | https://blendermarket.com/creators/bd3d-store |
| Biome Reader | free | not stated | opens Geo-Scatter biomes | Blender Market |
| Plant Library | free | listed free | 175+ plants for Geo-Scatter | https://blendermarket.com/products/the-plant-library |
| Botaniq (polygoniq) | paid, free version exists | commercial | trees and plants with wind. Free route: Poly Haven | https://blendermarket.com/creators/polygoniq |
| Rain Kit (Jepe) | free, email form | not stated | Geometry Nodes rain | https://jepe.gumroad.com/l/raingenerator |
| UV Squares | free | not verified | straighten UVs | built into the add-on list |
| Super Image Denoiser | free | not stated | temporal denoise for video | https://pidgeontools.gumroad.com/l/SuperImageDenoiser |
| Camera Shakify | free | GPL-compatible | handheld camera | https://github.com/EatTheFuture |
| BlenderKit Simple Procedural Cloud | free | BlenderKit | cloud volume | BlenderKit |
| JangaFX free VDBs | free | JangaFX | smoke and fire VDBs (EmberGen is paid) | https://jangafx.com |
| Tiling node group | free | not stated | break texture repetition | his video description |
| Steam pack | paid | not stated | fog and steam cards. Free route: free fog footage | https://blendermarket.com/products/steamkpack |
| Alt Tab Easy Fog | $0 demo, $4 personal, $8 commercial | per listing | fog presets. Free route: the fog entries above | https://blendermarket.com/products/alt-tab-easy-fog |
| Physical Starlight Atmosphere | paid | commercial | sun and sky. Free route: Nishita sky plus Sun | Blender Market |
| Mixamo | free with an Adobe account | Mixamo terms | rigged characters. Import FBX directly in 2.9+ | https://www.mixamo.com |
| PureRef | free (pay what you want) | n/a | reference board | https://pureref.com |
| textures.com | free tier | not CC0 | facade and road photos | https://textures.com |

Paid items in the sources that have no entry above (unneeded for the techniques): Geo-Scatter packs, Pure Sky Pro, materialiq, Character Creator 4, HumGen (paid status unverified), ActionVFX and Production Crate fog footage, material packs, KitBash3D.

## Unverified

- Dicing Scale 10 for the final canyon render: heard only.
- Swatch hex of the canyon colours: never read.
- HDRI name: never on screen.
- Ground fog scene: Emission Strength, cube dimensions and the render engine.
- Tunnel scene HDRI rotation and strength 0.3.
- Wind strength after the reduction on grass: not shown.
- Hair Info colour ramp RGB values on the grass blade.
- Fog card Emission and Alpha wiring.
- Wet map values and Dynamic Paint brush Solid Radius (0.01 versus 0.02).
- Splash card Mix Shader Fac (0.2 versus 0.22) and the fluid HDRI rotation (about 40).
- Tiling node group values, Geo-Scatter density option names, DoF values.
- Rain Kit Blender version, brush size and collapsed panels.
- The Geometry Nodes scatter and Hair Curves mappings in this file: inferred from release knowledge, not shown in any video. The notes did not re-check docs.blender.org line by line, except the Hair Curves modifier names and the Curves Info node (5.2 manual).
- Whether Is Camera Ray, noise-alpha planes and the old fog cube work in EEVEE 4.2+ unchanged: not tested.

Entries below were added 2026-11-08. They are all `unverified`: heard only, an add-on not run in 5.2, or values spoken and never shown.

- **Photo sky card that always faces the camera.** Enable the Copy Attributes Menu extension. Plane scaled up at the horizon line. Select the plane, Shift-select the camera, Ctrl+C > Copy Rotation, then Ctrl+P > Object (Keep Transform) so it follows the camera. Edit Mode on the plane, U > Project from View (a second video said Cube Projection), then in the UV Editor line the photo's horizon with the scene's. Shader: sky Image Texture into Emission (Strength 1.0) and Base Color. Light the scene with an HDRI of matching colour and direction. The add-on exists (seen in the add-on list at 00:04); the UV projection name is unsure. Related: camera projection mapping in `lighting-render-and-gn-recipes.md`.
- **One photo into a 3D set with fSpy and UV Project.** In fSpy (separate app) load the photo, drag the vanishing-point axes (Shift for precision), place the origin, save. Blender: enable the fSpy importer, File > Import > fSpy (a camera appears). Model simple geometry aligned to the image. Material: Image Texture into Surface. Add a Subdivision Surface modifier (Simple, raise levels) then a UV Project modifier: UV Map, Object = the fSpy camera, aspect set to the image. The node setup and Subdivision panel were seen at 00:40; the fSpy add-on is not on extensions.blender.org, so its version support in 5.2 is unknown. `UV_PROJECT` and `SUBSURF` exist in 5.2.
- **Real Snow add-on.** Enable Real Snow, select the object, N panel > Real Snow > Add Snow. For selected faces only: Edit Mode, select faces, back to Object Mode, tick "take selected faces", Add Snow. Not bundled in 5.x (check Extensions). The geometry nodes snow layer in `geometry-nodes.md` is the verified route.
- **Fire from black-background stock video.** Search "fire" videos with a black background on Pixabay or Pexels. Add > Image > Mesh Plane (Images as Planes) with the video. Shader: delete Principled, Emission (video Color into Color), Mix Shader before the output with Transparent in the top slot and Emission in the bottom, video Color also into the Mix Fac. Duplicate and rotate planes for depth. Optional wind: subdivide, bottom-edge vertex group as the Cloth pin group, Wind force field. A "tick circ" option was heard and not understood.
- **Ruined pillar by Boolean with a displaced Suzanne.** A Suzanne with a Displace modifier (Clouds texture) as the cutter, Boolean (Difference) on the pillar, hide the cutter, Alt+D copies along the path. No values given.
- **Terrain blockout from inside the camera view.** Scale and subdivide a plane, Sculpt Mode Inflate brush, camera set before sculpting, sculpt from the camera view (Numpad 0). Test render at 50 percent resolution and 10 samples to find artifacts, and enable the Mist pass for grading. The 50 percent and 10 samples are spoken, not shown.
- **Sand floor with footprints.** Subdivided plane, Displace modifier with a Voronoi texture plus a footprint displacement map, proportional editing (O) to raise the corners.
- **Fence from a plane.** Loop cuts, right-click > Poke Faces, select one edge, Shift+G > Length with the threshold decreased, delete Only Edges and Faces, convert to Curve, raise Depth. The Poke Faces step is unsure (it may be Inset).
- **Mist pass for a Photoshop haze.** View Layer > Passes > Mist before rendering; in Photoshop set the mist layer to Screen, add curves, invert the mask, paint. The in-Blender route is the Mist pass compositing entry above.

## Remastering a game scene

Rebuilding a known place as a realistic Blender scene (one build remastered Skyrim's Riverwood in Blender 4.0.2,
Cycles, Max Samples 64 with denoise). Licence: his scans, the houses rebuilt from them and his paid town kit come from
Bethesda game assets. That is a licence risk: name it and ask the user once whether to accept it. Yes: go ahead, the
responsibility is theirs. No: use the method on your own places, photos or licence-clear sources.

**Order of work.** Inspiration, references, blockout, modeling, then scan, modular kit, texturing, roofs, terrain,
scatter, trees, cliff, props, camera, render, grade. Writing the plan first stops the size of the job from stalling it.

**Photogrammetry from video.** A position guide and per-object modeling references from recorded footage.
Steps:
1. Record 4K 60 fps, HUD off, moving in orbits while always rotating the view, far first then close. One recording
   for the whole area (to place things) and one per building or object (for exact shapes).
2. DaVinci Resolve (free), Deliver page, Format TIFF: export the clip as an image sequence (his gate scan was 472 images).
3. RealityCapture (free): drag the folder in, Align Images (F6), Calculate Model at High quality, then Simplify
   (Type Absolute, Target triangle count 1 000 000), Texture, Export FBX. Blender: File > Import > FBX.
Use when: the place exists and you can film it, or as a scan of your own real objects.
Pitfalls: simplify to 1 to 5 million triangles before import or Blender chokes. The scan is a guide to model over,
not the final mesh.

**Modular kit with linked duplicates.** Build one building from reusable parts (rock wall, wood wall, pillar,
window, floorboard, railing, roof support) on planes fitted to the scan, then reuse them across all buildings with
Alt+D (linked duplicate), not Shift+D. Blender stores one mesh per part. Sculpt weathered edges with the Scrape brush.

**Layered texturing and export.** Base texture (Poly Haven wood or rock, CC0) with levels and saturation tweaks, a
darker copy masked by grunge for colour variation, dirt layers masked by grunge maps, moss from the ambient occlusion
mask, then painted decals. He uses Substance 3D Painter (paid); the free route is the same stack in Blender nodes
(Mix by a grunge or AO mask) or in ArmorPaint. Export only base colour (PNG 8 bit), roughness (PNG 8 bit) and height
(TIF 32 bit float), 2048 px (4K also used), one texture set per part.

**Height map as bump in Cycles.** Base colour (sRGB) and roughness (Non-Color) into Principled BSDF. Height (Non-Color)
into a Displacement node (Object Space, Midlevel 0.500, Scale 0.050) into Material Output Displacement. Then Material
Properties > Settings > Surface > Displacement: Bump Only. Displacement and Bump on unsubdivided parts blows the mesh up.

**Thatch roof from hair particles.** A roof shell with a thatch texture at real scale, then Particles > Hair:
Emission Number 1000, Hair Length 0.423 m, Segments 5; Children Interpolated, Display 155, Render 100, Length 1.000;
Roughness Endpoint 0.003; Hair Shape Diameter Root 1 m, Tip 0 m, Diameter Scale 0.01, Close Tip on; Render As Path
with the thatch material, Path Steps 3. Particle Edit > Comb (Deflect Emitter on, strength 0.500) to brush the strands
down the slope. Copy the system to the other roofs.
Pitfalls: he spent three to four days tuning these. In 5.x the same look can come from Hair Curves (see Grass and vegetation).

**Terrain cut from the scan.** Duplicate the whole-area scan, delete the buildings, clean and smooth what is left: a
1:1 ground. A plane with proportional editing did not match.
Ground material: Noise Texture (4D, Normalize on, W 9.040, Scale 1.460, Detail 5.000, Roughness 0.699, Lacunarity 2.000)
into a Color Ramp (Linear, black stop at 0.435) into the Factor of a Mix Shader between two material groups (dirt and
forest ground, each with BSDF and Displacement outputs). The same ramp drives a Mix (Color) of the two displacement
outputs into Material Output Displacement. Paint a cobblestone path in with a texture-paint mask.

**Snow on ledges by slope.** Geometry node Normal into Separate Color (RGB), Green into a Color Ramp (stops near 0.58
and 0.9), into the Factor of a Mix Shader between rock and snow groups and of a Mix (Color) for their displacements.
Green is the up axis, so snow lands on faces that point up. Move the ramp stops to set the cover. Render with
displacement to turn a flat scan into real cliff detail.

**Ecosystem list, then scatter.** Match the place's plants to real species (ferns, small plants, crawling plants,
grass, a leafy weed), get them from a scanned plant library, and scatter in that order (small plants, grass, ferns,
weeds) with Geometry Nodes, mixing boulders in. Trees: placed by hand at the real positions. He uses Blender Trees by
3D SHAKER (paid, Blender Market) and Quixel Megascans (Fab terms) for boulders and props; free routes are Poly Haven
models and the Scattering section above.

**Prop pass.** Walk the place, list every item people use there (buckets, barrels, carts, firewood, fences, anvil),
find each in an asset library, and place them by how people live and work there. Model by hand only what no library
has. Check: heard and seen [23:38 to 23:56].

Tried and dropped: Gaea for the cliff (could not match the shape). Final grade in DaVinci Resolve, values not shown.
