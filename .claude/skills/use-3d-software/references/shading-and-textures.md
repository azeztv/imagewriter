# Shading and textures

Shader nodes, world shaders, palette colouring, baking, toon looks and lighting.

<!-- skill-navigation:start -->
## Reading Map

- [Shading and textures](#shading-and-textures)
- [5.x names](#5x-names): read first
- [Palette and UV colouring](#palette-and-uv-colouring)
- [Procedural textures and distortion](#procedural-textures-and-distortion)
- Character and prop materials
- [World and sky shaders](#world-and-sky-shaders)
- [Toon and stylised looks](#toon-and-stylised-looks)
- [Baking, painting, decals](#baking-painting-decals)
- [Lighting](#lighting)
- [Compositor and post](#compositor-and-post)
- [Quick material and viewport tricks (Blender 4.2+)](#quick-material-and-viewport-tricks-blender-42)
<!-- skill-navigation:end -->

## 5.x names

- Mix RGB -> Mix (Color), with Float and Vector variants. Separate and Combine RGB -> Separate and Combine Color.
- Musgrave Texture -> Noise Texture Type dropdown (4.1). Voronoi and Noise are 4D capable.
- Principled BSDF (4.0): Specular -> Specular IOR Level, Transmission -> Transmission Weight, Subsurface -> Weight, Scale, Radius. Old Subsurface 0.02 values need re-tuning.
- Color Management: Filmic is replaced by AgX (4.0), so "Very High Contrast" and "Look" names differ. Set View Transform Standard for toon and flat looks.
- Eevee Bloom, Blend Mode and Shadow Mode changed in Eevee Next (4.2+). See `effects-fx.md` 5.x names.
- Auto Smooth removed in 4.1, use the Smooth by Angle modifier.
- Pointiness stays Cycles only. Ambient Occlusion node works in both.
- `use_nodes` on materials and worlds is deprecated in 5.0 because nodes are always on, setting it is harmless.
- Texture Coordinate Window, Object, UV, Camera and Generated all still exist. Mapping node takes vectors for Location, Rotation (radians) and Scale.

## Palette and UV colouring

- **Palette material for a whole character**: Material with Image Texture (palette, 16 x 16 or 256 px, Interpolation Closest) into Base Color, UV into the vector. Ctrl+L > Link Materials to all parts (or M). Apply Subdivision then Skin (top to bottom) on skin parts. Select all, U > Smart UV Project (margin 0.01 to 0.5). UV editor: select a part's faces, S 0 to collapse to a point, G onto a swatch. L or Ctrl+Numpad+ select sub-parts. Material Preview, sync selection on. Fix shading with Smooth by Angle. Metal parts: duplicate the slot, raise Metallic, assign those faces. Skin hair must be applied and unwrapped first. One material means shared roughness. Free palette image comes from the author's Gumroad, any small swatch works.
- **Stripes and fabric on palette parts**: Second material slot assigned in Edit Mode, Wave Texture (Z axis) -> Greater Than -> Mix. Fabric: Magic Texture factor -> Bump (scale ~100, low distance, strength).
- **Texture-paint detail over the palette**: Second UV map (Smart UV Project, margin 0.01), new image 2048 with Alpha transparent. Mix with the image Alpha as Factor, palette in one slot and painted colour in the other. Texture Paint, soft falloff, Strength 0.2 and Falloff Sharp for dark rims. Save the image (asterisk = unsaved). Roughness 0.8 for fur.
- **Painted wrinkle mask on a second UV map**: Object Data > UV Maps > + ("face"), Edit Mode select faces, U > Project from View. New black image, paint white (Stroke > Stabilize Stroke). UV Map node set to "face" into the Image Texture, colour into Mix factor between skin and darker skin. Without the UV Map node it uses the first map.
- **Vertex colours**: MagicaVoxel PLY import shows through a Color Attribute node into Base Color. Vertex Paint, Shift+K fills, Color Attribute -> Base Color, a Less Than after it masks a second colour, roughness and bump. Dirty Vertex Colors (Paint > Dirty Vertex Colors) or AO or Pointiness for crevices. Resolution follows mesh density so UV unwrap if animating.
- **Eye pupils from UVs**: Texture Coordinate UV -> Vector Math Length -> Greater Than, offset with Vector Add (acts like Mapping location). Unwrap the cube eye, shift the island so the centre is at 0. Mapping scale gives taller pupils.
- **Bone material**: Noise (Generated coordinates if the model animates) -> Map Range (smoother step, From Max ~0.35) -> Bump (0.1, 0.5) into Normal.

## Procedural textures and distortion

- **Distortion node group**: Plane, Wave Texture, Ctrl+T (Node Wrangler), Object coords. Vector Add after the coordinate, Noise Color into the second input, Multiply (strength), Subtract 0.5. Group, expose Vector, W, Strength, Scale, Detail, Roughness. Per-axis: Combine XYZ from three Multiply, Mix switch "individual". Voronoi variant (4D, Randomness replaces Detail). Stack a few, each costs viewport speed. Displacement: Displacement node, Cycles Material Settings > Displacement and Bump, adaptive Subdivision. Free groups pack covers Euclidean, Chebychev, Manhattan, Minkowski variants, value compressor, input Color Ramp (up to 10 colours), Multiple Color Mixer, pixelator.
- **Material distortion via Mapping inputs**: Object coords -> Mapping -> Checker etc. Voronoi Color or Distance (Randomness 0) -> Multiply (Clamp) -> Combine XYZ into Mapping Location, Rotation Z or Scale (Multiply Add with 1 keeps default). Rotation is radians. Noise into Location warps uniformly. Voronoi normal trick: Normal into Voronoi, Position into the Normal socket for a faceted clay look.
- **Map Range vs Color Ramp**: Map Range From Min and Max are the flag positions, To Min and Max the outputs. Drive From Min with a Value and From Max with Add (width) to move a band. Unclamped Map Range passes negatives, Color Ramp always clamps. Interpolations: Linear, Stepped Linear, Smooth Step, Smoother Step, and for ramps Cardinal, Ease, B-Spline (overshoots), Constant. Three or more colours: chain Map Range + Mix, each Mix into the next Color 2.
- **Stripe pattern**: Wave Texture -> Greater Than (threshold = width) -> Mix between Emission and base. Ctrl+T, Object coordinate on Y, scale via Divide 1000.
- **Procedural spiral (2.82)**: Gradient Radial -> Multiply (bands) -> Fraction -> Color Ramp Constant. Spiral: Gradient Spherical -> Combine XYZ Z only -> first Mapping Rotation, Multiply for strength, animated Add to spin. Mapping scale Z 0 on non-planes.
- **Retro sun (2.83)**: Plane X 90. Emission + Transparent. Object coords -> Vector Length -> Less Than 1 for a disc. Wave (UV, Y) Greater Than 0.5, subtract from the disc, Clamp. Varying widths: Length of UV -> Mapping scale X 0 as gradient -> Multiply Add into Wave Mapping Y scale. Wobble with 4D Noise, W `#frame`/50 to 200. Colour via Noise -> Greater Than -> Mix (black, red) or a fire Color Ramp. Animate: Multiply 0 distortion, key the Add value -1, +1, -1, key Mapping Y with Constant interpolation. Triangles: Wave profile Triangle, Mapping Z rotation 45 or 90, Linear.
- **Vein material**: Voronoi Distance to Edge -> Map Range (From Min ~0.05 via a Value, Smoother Step), second Voronoi smaller scale (To Max ~0.5). Mix Linear Light or Lighten -> Bump (x0.01), Color Ramp Ease. Colour pink and red. Noise before Mapping for swirl. 4D W animates.
- **Pumpkin skin and glow-through**: Orange Base Color, Noise (scale 10) -> Bump (0.1, 0.2 to 0.3), Object coords. Second slot "inside" via Solidify Material Offset 1 and Rim 1. Subsurface ~0.02 radius 1,1,1 for glow in Cycles, or Eevee Mix with Translucent 0.05 to 0.1. Stem rougher.
- **Boba pearls, fabric**: Voronoi (Object) -> Map Range for circles, Generated Z gradient to bunch at the bottom. Glass IOR ~1.1. Fabric: Magic Texture.
- **Random per-object colour and metal**: Link one material (Ctrl+L). Object Info Random -> Color Ramp -> Base Color, Greater Than -> Metallic and Transmission, roughness 0.1 to 0.2.
- **Ambient Occlusion and Pointiness for creases**: AO into Base Color, Color Ramp pushes black up, tint it. Skin: green stylised tint, Voronoi Distance to Edge on Bump for cracked leather, high roughness + Voronoi bump + subsurface for blanket.
- **Grunge masks**: Bevel node (Samples 6) vs Normal compared with Vector Distance gives an edge mask, AO gives a cavity mask. Use as Mix factor.
- **Ghost glass with Layer Weight**: Diffuse + Transparent Mix. Layer Weight Facing -> Map Range (swapped, To Min 0.1) -> factor. Glow Add Shader Emission 0.05. Hide back faces via Light Path Transparent Depth. Eevee: alpha blend, back-face off.
- **Cartoon glass stripes**: Wave (Object) -> Mix factor, colours via eyedropper (hover, E), roughness 0. Cycles Transmission and Transmission Roughness.
- **Flat distance fog (Eevee)**: World strength 0, plane with Emission. Texture Coordinate Object with the camera as object, Separate XYZ X -> Mix factor (Clamp) or Color Ramp (HSL Far for rainbow), Divide for falloff. Clip End 1000. Emission above 1 blooms.
- **Endless low-poly scene loop**: Plane x50 with Displace Clouds, Array 50 on Y after the displace, Voronoi-displaced Ico Spheres decimated, hair particle system Render As Collection with scale randomness and density vertex group, Convert to Mesh, Ctrl+J. Floaties: grid with parented Ico Sphere, Instancing > Verts. Camera key Y by the tile distance, Linear.

## World and sky shaders

- **Galaxy HDRI (2.82)**: Stars first, Mix (Add). Mask top half via Mapping -> Separate XYZ Z. Gradient Spherical through Mapping Z scale 0 scaled by Combine XYZ. Multiply with Noise (detail max, scale 20). Spiral: gradient multiplied into a Mapping Z rotation (~6). Centre: Power then Multiply ~30, Add. Spin: key Z 0 to 360 over 250 frames Linear or `#frame`/200.
- **Star sky and nebula**: Voronoi Distance or Noise -> Greater Than -> Map Range (From Min and Max by one Value + Add). Layers at different scales, Add (Clamp). Brightness via Noise Map Range. Nebula: Noise Smoother Step distorted by second Noise, Mix colour on the mask. Do not multiply brightness before colour. Simple star field: very high scale Noise -> Color Ramp, black stop up.
- **Procedural sky**: Ctrl+T on Background, Separate XYZ Z -> Mix (ground, sky), second mix for horizon, Noise clouds, Multiply 5, no Clamp so values pass 1.
- **Window-light HDRI (2.82)**: Separate Z -> Mix -> Color Ramp (white at 0.5) -> Greater Than 0.5 band. Windows: Gradient Radial x count -> Fraction -> Map Range (width). Multiply with band. Count 3 acts as a three-point setup.
- **Aurora**: Mapping -> Separate Z mask. Wave with Mapping scales zeroed except one, scale ~2, distorted by Noise (detail 0, scale 3) x Multiply -> Combine XYZ -> Mapping location Y. Sharpen with Power or RGB Curves. Colour: Color Ramp blue to green. Shimmer: duplicate noise, detail high, x0.5 - 0.05. Loop: Mapping rotation X 0 to 360 over 250 frames Linear. Nothing downstream may clamp.
- **Infinite studio background plus separate world lighting**: Floor with Principled mixed with Transparent, factor Vector Length -> Map Range to 10 m. World: Light Path Is Camera Ray between two Backgrounds. Glass dark: mix Glass with a tiny Translucent (0.05). Pointiness via Map Range (Cycles). Lights tracked to an Empty (Track To).
- **Chrome reflections**: Environment Texture from Poly Haven, Hue Saturation, Mapping Z to tune reflections.

## Toon and stylised looks

- **Cell shading (Eevee)**: Global: Compositor Posterize with Brightness/Contrast first. Per material: Principled white -> Shader to RGB -> Color Ramp Constant, Map Range, or Greater Than. View Transform Standard. Lights: Shadow off, small. Colour groups: image in the middle colour, Mix Multiply for shadow, Add for highlight, Map Range Stepped Linear (Vector). Separate Color R as main and G and B as rim. Fake lighting: Normal from Texture Coordinate dot (0,0,1).
- **Outlines**: Fresnel or Layer Weight -> Less Than. Inverted hull: Solidify (flip normals, Material Offset 1) with black Emission second material, Backface Culling on, Shadow None. Grease Pencil Object Line Art (camera, Lock Camera to View, Silhouette). Freestyle in Render Properties. Alan Wyatt's Line Art Curve (GN) as an alternative.
- **Halftone**: Shader to RGB -> Greater Than from Voronoi Distance (Randomness 0, 2D, Camera coordinates). Constant size via View Vector from Camera Data. Wave for lines.
- **Painterly normals**: Smooth mesh, Voronoi (Position in) into Normal, add Noise - 0.5 scaled, Voronoi Smooth blends. Bake for animated characters.
- **Procedural landscape shaders**: see `modeling.md` Displace landscapes.

## Baking, painting, decals

- **Bake vertex colours or procedural textures**: Cycles, CPU. Smart UV Project margin 0.005. Bake > Diffuse with only Color (Direct and Indirect off), margin ~2 px, or Emit. New Image Texture node (256 test, 1024 final), selected, Bake. Emit trick: Ctrl+Shift+click a socket to preview and bake with Emit type. Roughness bake to its own image. Save, then File > External Data > Pack Resources. Non-colour maps use Non-Color. Subsurface corrupts bakes so bake via Emit. BakeLab add-on batch bakes.
- **Eyek projection decals (paid add-on, 2.93)**: UV unwrap, install add-on, drag PNGs to make image empties (Alt+G, Alt+R, R X 90) or camera Background Images. Select images, object last, Eyek panel, resolution, Paint. Shader: Image Texture (UV, Closest) -> Mix with Alpha. Snap with Face, Ctrl+G. UDIM: set tiles, drag one 1001 tile.
- **Hair particle fur density**: Particles Hair, length 0.1, count 100 to 250, Interpolated children, Clumping high, vertex group "hair" for Density and Length painted with Weight Paint (symmetry X, Front Faces Only off, Projected falloff). Eevee Render > Hair Strip.

## Lighting

- **Cartoon scene lighting**: Ground plane, N > View Lock Camera to View, focal length ~100 or Orthographic for miniature. Area lights (bigger = softer, ~2500 W, warm interior lights low). Material slots per object (Assign), link, Metallic. World colour and strength. GPU = OptiX under Preferences > System.
- **Rim-light portrait**: One big top Area fill, two Spot lights from behind on each side, one warm and one cool. Spots because areas lit the ground. Cycles GPU.
- **Three-point backdrop**: Soft white top, warm side, cool rim on a curved backdrop.
- **Eevee flicker fixes**: Raise viewport samples to 128, light Contact Shadows on if objects float. Light Power flicker: key Power, Noise F-curve modifier, range 0 to 250, blend 12.
- **Worm loop shading**: Mix Principled and Emission by Wave -> Greater Than, normal-based coordinates + Multiply -0.02 so waves follow the worm. Ground: Voronoi Chebychev Randomness 0, Smooth F1 for bump (0.001, invert).
- **Milky rings material**: White metallic roughness 0, Musgrave (now Noise type) scale 300 for roughness and Bump 0.03, look High Contrast, ground subsurface 1, point lights on camera (1000, green and blue saturation 0.5).

## Quick material and viewport tricks (Blender 4.2+)

- **Link materials**: select the objects that need the material, then Shift+click the one that has it (active, last). Ctrl+L > Link Materials.
- **Viewport colours for modeling**: Viewport Shading dropdown, Color > Random, tick Cavity (Type Both), World Space Ridge about 1.295, Valley 1.27 to 1.39 (Valley `unverified`). Viewport only, renders do not change.
- **Silhouette check**: Viewport Shading dropdown > Lighting > Flat during early modeling.
- **Node Wrangler PBR setup**: Node Wrangler is still bundled and off by default (Preferences > Add-ons, search "node"). In the Shader editor select the Principled BSDF, press Ctrl+Shift+T, pick all maps (base colour, roughness, metallic, normal, height), click Principled Texture Setup.
- **Lights that always aim at the subject**: select the light, Object Constraints > Add Object Constraint > Tracking > Track To, Target = the object (Track Axis -Z, Up Y, Influence 1.0). The light aims at the target origin, so aim at an Empty (Shift+A > Empty) for control. Many lights: select all, hover over the object, press Shift+T. Shift+T is not a default key, the add-on is not named on screen `unverified`.
- **World colour that does not change lighting**: World shader, Light Path (Is Camera Ray) into the Factor of a Mix Shader. One input is the normal world lighting, the other an RGB colour for the visible background. Same trick as the studio background above.

## Compositor and post

General render and compositor steps from the tutorial notes. The NPR looks that use them live in other skills.

- **Turn the compositor on**: Compositor tab > New (Blender 5.0 has no Use Nodes button, 4.x ticks Use Nodes). Render properties > Compositor = Always so the viewport shows it.
- **Soften then sharpen**: Filter > Soften (0.45, verified [frame 16:57] in Blender 5.2) then Filter > Box Sharpen (0.70, same frame). Diamond Sharpen also works.
- **Glare**: add a Glare node and tune Type (Bloom, Ghosts, Streaks) and Threshold so bright areas glow. In Eevee Next this replaces the old Bloom checkbox. Soft glare keeps flat lighting from looking dead.
- **One tint over mixed layers**: Mix node set to Color after the image, pick a colour. Fac about 0.08, never above 0.2, or colours wash out.
- **Two-colour contrast gradient**: Color Ramp from dark purple to bright orange with values 1.1 to 1.4 (Ctrl+Shift+click to preview), Fac from the sharpened image. Mix (Multiply) the scene by the ramp. Every pixel is multiplied by the same two colours. Only the Soften and Box Sharpen values and the first stop were verified.
- **Split tone**: Map Range, Color Ramp, Mix for orange highlights and blue shadows. Heard only, no values `unverified`.
- **Grain and lens fringe**: Image node (any noise image) > Map Range clamped bright > Mix Soft Light with the render. Lens Distortion adds chromatic aberration at the edges. If areas blow out, lower the material values.
- **Colour management**: the cat-scene video switches View Transform from Filmic to Standard. Filmic became AgX in 4.0, so pick Standard for flat looks and AgX for photoreal.
- **Eevee Next ray tracing as a preview aid**: Render properties > Ray Tracing on, then Ctrl+Shift+click a Diffuse node previews bounce light. Not used in the final. Blender 4.2.2 verified [frame 05:54].
- **Depth of field with a focus Empty**: Ctrl+Alt+Numpad 0 snaps a new camera to the current view. Camera data > Depth of Field on, Focus Object = an Empty named Focus, move the Empty to pull focus.
- **Bake without add-ons**: Cycles, Bake panel, Diffuse (Color only) and Ambient Occlusion into a new image per object, with its Image Texture node active. Ctrl+J objects before texturing if you export one atlas, joining late breaks the texturing. A shader-built animation exports as an image sequence or video: render it and import that.
