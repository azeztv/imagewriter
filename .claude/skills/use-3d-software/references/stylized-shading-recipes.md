# Stylized shading, looks, hair and line art

Blender 5.2 names. Values marked in an entry were read from a video frame unless the entry says (heard). Where a video used an
older route, the entry gives the 5.2 route and the old name. Name changes that apply everywhere: Mix RGB is now Mix (Data Type
Color); Principled BSDF v2 (4.0+) renamed Specular to Specular IOR Level, Clearcoat to Coat, Transmission to Transmission Weight,
Subsurface to Subsurface Weight, and made Sheen and Specular Tint colours; Hair Info is now Curves Info; Musgrave is now Noise
Texture (4.1+); Eevee Bloom and Screen Space Reflections checkboxes are gone (Eevee Next, 4.2+: Raytracing panel, Glare node in
the Compositor); Eevee Blend Mode is now Material Settings > Render Method (Dithered or Blended); Grease Pencil is v3 since 4.3.
Complements `shading-and-textures.md`, `geometry-nodes.md` and `modeling.md`.

<!-- skill-navigation:start -->
## Reading Map

- [Stylized shading, looks, hair and line art](#stylized-shading-looks-hair-and-line-art)
- [Clay and plastic](#clay-and-plastic): clay fingerprint material, clay to plastic toy, Eevee clay preview, soft displacement, stop-motion boil
- [Painterly and brush looks](#painterly-and-brush-looks): faceted normals, brush normal map, outline shell, Compositor Paint Filter (5.2), stroke tracking and layers, Kuwahara in a shader, painterly grass
- [Outlines and line art](#outlines-and-line-art): Line Art modifier, blueprint look, light contour and priority
- [Comic toon shader: cell shade, screen tone, outline, rim light, glow (Eevee)](#comic-toon-shader-cell-shade-screen-tone-outline-rim-light-glow-eevee): scene rig, mask method, cell shade, screen tone, hatch, flat chibi shading, backface outline, rim light, glow, Grease Pencil ink outline
- [Pixel art](#pixel-art): render small, Pixel Blender Kit, pixel texture node
- [Wear, grime and mapping](#wear-grime-and-mapping): dirty vertex colours, edge and cavity masks, positional gradient, mixing two materials, box mapping, displacement setup, Node Wrangler PBR, Principled reference
- [Skin, wax and thickness](#skin-wax-and-thickness): thickness masks, fake SSS with Layer Weight, skin shader with painted blush
- [Glass and transparency](#glass-and-transparency): believable glass, Eevee glass, RGB split glass, Thin Wall, bubbles and tears
- [Fabric](#fabric): sheen and fuzz, cotton character
- [Procedural effects and materials](#procedural-effects-and-materials): Is Camera Ray, rim and falloff, energy trail, toon water, hologram, light rays, speed lines, caustics, flame, rock, wood, coffee, leaf, ground splat, dynamic palette, Raycast
- [Texture painting](#texture-painting): painterly brush, second UV sticker, painted details
- [Hair and fur](#hair-and-fur): Quick Fur stack, needle felt, fabric fuzz, stylized curve hair, feathers, per-strand colour, legacy particle hair, combing, dynamics
- [Add-ons](#add-ons)
<!-- skill-navigation:end -->

## Clay and plastic

- **Clay material, fingerprints in roughness and bump**: a handmade clay look whose fingerprints read in the highlights.
  - Steps: material "clay", burnt-orange Base Color, Specular IOR Level 0.5 (old Specular 0.5). Image Texture with a fingerprint
    PNG (cgbookcase Fingerprints 01), Color Space Non-Color. With Node Wrangler on, Ctrl+T adds Texture Coordinate (UV) and
    Mapping (Type Point, Scale 1.5 on X, Y and Z, all equal or it stretches). Image Color -> Color Ramp -> Roughness (white is
    rough, black is shiny; move the black stop right until it looks less wet). Same ramp -> Invert Color -> Bump
    (Strength 0.5) Height -> Bump Normal into Principled Normal.
  - Principle: one grey map drives gloss variation and height, which is how clay shows fingerprints.
  - Other tools: three.js or Godot use the same map as roughnessMap plus a baked normal map (untested).
  - Pitfall: forget Non-Color and the map is gamma shifted; forget Invert and the prints stick out.

- **Clay to plastic switch for toy sets**: the same shader turned shiny for props next to a clay character.
  - Steps: on the clay material set the Bump node Strength to 0 and adjust Roughness; keep colours vibrant. Optional Noise
    Texture (3D, Scale 5, Detail 2, Distortion 0) into Bump Height for tooth. The plastic rocket variant: Principled red,
    Specular IOR Level 1.0, Color Ramp -> Roughness, Noise Texture (3D, Scale 250, Detail 16, Distortion 0) -> Normal Map
    (Tangent Space, Strength 0.1) -> Normal.
  - Principle: roughness variation reads as plastic; tiny normal noise adds tooth without looking like clay.
  - Pitfall: raising the Normal Map strength above about 0.1 ruins the toy look.

- **Soft noise displacement for clay and painterly silhouettes**: a perfect sphere or model becomes lumpy and hand-made.
  - Steps: Subdivision Surface (Catmull-Clark, Viewport 2, Render 2, Quality 3, Smooth Keep Corners), then Displace modifier
    with a new texture: Clouds with Noise Basis Improved Perlin for clay (Strength 0.05, Midlevel 0.5, Coordinates Local), or
    Voronoi for painterly (strength starts at 1.0, lower to about 0.045 (heard)). Direction Normal.
  - Principle: low-strength noise breaks the perfect shape.
  - Pitfall: complex models need lower strength or they distort.

- **Eevee preview for clay animation**: playback while animating.
  - Steps: Eevee, Render samples 64, Viewport 16, ambient occlusion on. Video used Bloom (Threshold 0.8, Knee 0.5, Radius 6.5,
    Intensity 0.010) and SSR; today use Raytracing in Render properties and a Glare node (Bloom) in the Compositor.

- **Stop-motion boil and stepped timing**: clay texture shifts a little every step, like real puppets.
  - Steps: key the Mapping node Rotation Z or Location every few frames (keys at 14, 20, 26, 32, 38 in the video), Constant
    interpolation, Cycles modifier. A free add-on panel "Stop-Mo" does it with Animate Texture > Add Animation, Step/Loop,
    and Apply Steps (Step Amount 2) for the object animation. No add-on: type `#floor(frame/8)` into a Seed or offset field.
  - Principle: low, steady change rate reads as handmade.
  - Other tools: step `texture.offset` every 2 or 3 frames in three.js (untested).
  - Camera for the miniature feel: Depth of Field on, Focus Object set, F-Stop about 0.5, Focal Length 250 mm.

## Painterly and brush looks

- **Painterly material: Voronoi position as faceted normals**: normals break into flat brush planes with wobbly edges.
  - Steps: Texture Coordinate Normal -> Voronoi (3D, F1, Euclidean, Scale 4, Detail 1, Roughness 0.5, Lacunarity 2,
    Randomness 1) Vector; Voronoi Position -> Normal Map node (Tangent Space, Strength 1) or straight into Normal. Roughen the
    edges: Mix (Color, Clamp Factor, Factor 0.15) before the Voronoi Vector, A = Normal coordinate, B = Noise Texture on
    Object coordinates. Principled Roughness 0.15, warm orange Base Color. Ctrl+Shift+click previews a node.
  - Principle: Voronoi cell positions as normals give flat facets; a little noise in the input makes edges wobble like paint.
  - Other tools: three.js ShaderMaterial can perturb normals with a Voronoi cell direction (untested).
  - Pitfall: use Object coordinates for the noise so it sticks to an animated object.

- **Brush strokes from a paint-brush normal map**: directional strokes on the facets.
  - Steps: Image Texture (brush normal PNG), Non-Color, Projection Box, Blend 1.0; vector from Texture Coordinate Object ->
    Mapping with Scale driven by one Value node. Image Color -> Normal Map -> Mix (Linear Light, Factor 0.15) with the facet
    normal; second Mix (Factor 0.3) with the Voronoi position. Colour: brush diffuse (Box, Blend 1) in a Mix Multiply (Factor
    0.7) with a Color Ramp of the Voronoi; ramp -> Factor of a Mix between warm orange and dark purple -> Base Color; a second
    ramp -> Roughness.
  - Principle: a tangent-space normal from a hand-made tile gives strokes; Box avoids Object-coordinate swirl.
  - Pitfall: Flat projection swirls; Box can show seams unless Blend is up.

- **Outline shell cut with Is Shadow Ray and Backfacing**: a flipped-normals outline that is also broken like a painted edge.
  - Steps: second material slot "outline". Solidify (Mode Simple, Thickness 0.015 m, Offset -1, Flip Normals on, Rim Fill on,
    Material Offset 1). Outline nodes: Principled, Transparent BSDF, Light Path (Is Shadow Ray), Geometry (Backfacing), two Mix
    Shader. Mix 1: Fac = Is Shadow Ray, top = Principled, bottom = Transparent. Mix 2: Fac = Backfacing, top = Mix 1, bottom =
    Transparent. Messy line: Noise Texture (Scale 10) -> Color Ramp (stop near 0.233) -> Principled Alpha. Thickness is line width.
  - Principle: the shell shows only behind objects; ray tricks keep it out of shadows and the front.
  - Other tools: three.js and Godot use an inverted hull scaled along normals.
  - Pitfall: forget Material Offset and the shell uses the body material; in Eevee Next check the material's backface settings.

- **Compositor Paint Filter (new in 5.2)**: turns a render into a painting; strokes can stick to objects.
  - 5.2.2 check: Paint Filter is NOT a built-in node (no `CompositorNodePaintFilter`; it is a downloadable node-group asset, so
    it cannot be added by bpy headless or without the cloud download). Its socket names are therefore unverified here. The built-in
    `CompositorNodeKuwahara` has sockets Image, Size, Type, Uniformity, Sharpness, Eccentricity, High Precision (Type is a socket, no
    `variation` property) and works as a plain stand-in. The 5.2 compositor is a node group (`scene.compositing_node_group`): there
    is no Composite node, end in Group Output.
  - Steps: Compositing workspace, asset shelf (Compositor, Creative) > Paint Filter (cloud asset), Download Asset, drag onto the
    Render Layers Image link. Defaults: Texture Watercolor, Size 20, Simplification 4.0, Accidental Colors 0.2, Pooling 0.1,
    Sharpness 0.6, Seed 0, Edge Breakup 1, Scale 2, Overlay Texture 0.15. Texture presets: watercolor, oil, digital geometric
    (heard: works for nearly everything), custom. Smaller Size means finer strokes; Simplification is a Kuwahara pre-pass (4 is
    the sweet spot, 50 loses form); keep Accidental Colors and Pooling low; Sharpness 0.6 to 0.65 restores clarity.
  - Principle: small strokes near the focus, big strokes far away, paint stuck to the surface rather than a static overlay.
  - Other tools: a Kuwahara pass plus a stroke texture sampled in object space is a post shader in three.js or Unreal (untested).
  - Pitfall: flat colour swatches do not read as paint; give surfaces colour and texture variation.

- **Paint Filter stroke tracking, layers, halo and eye mask**: strokes that follow the character, big on the set, sharp on the eyes.
  - Steps: View Layer > Passes > Data: tick Depth and Position, re-render, plug Position into the filter and tick Use Tracking
    (Depth plugged in gave poor results). Layers: Foreground and Background collections, first view layer "Foreground", New Scene >
    Linked Copy for "BG"; Render Layers plus Paint Filter per scene, Alpha Over (Background = BG, Foreground = character, Factor 1).
    Foreground example: Size 10, Simplification 4, Accidental Colors 0.05, Pooling 0.25, Sharpness 0.6, Seed 12, Edge Breakup 2.
    Halo (heard): a coarse over-simplified copy behind the sharp one, no Position. Eye mask: a separate material with an AOV
    Output node (name ID_Eyes, Color white), View Layer > Shader AOV add ID_Eyes, re-render; Alpha Over with Factor = ID_Eyes
    through Blur (about 30 px), Foreground = raw image. Custom canvas (heard): Canvas Custom plus a brush-stroke Image Texture.
    Handmade jitter: Seed field `#floor(frame/8)` (4, 6 or 8) in every filter, with stepped character keys.
  - Principle: composite separately painted layers so stroke size follows depth; an AOV is a motion-proof mask.
  - Pitfall: passes and AOVs only appear after a fresh render.

- **Kuwahara filter inside a material (closures and repeat zones)**: stylises any texture per material, 5.x only.
  - Steps: delete Principled, plug the colour straight into Surface. Put the Image Texture in a Closure zone (input Vector,
    output Color and Alpha). "Filter Base" group: Repeat zone, Iterations 25 (5x5), Truncated Modulo (Iteration, 5) and floor of
    Iteration / 5 build the UV offset, Evaluate Closure samples it; sum colour, luminance and luminance squared. After the loop
    divide by 25 (scale 0.04), variance = mean of squares minus square of mean, clamp at 0. Four copies of the group with X and Y
    axis offsets (one pair with -1); per pair keep the colour of the lower variance with Less Than and Mix; compare the two
    winners. A 45 degree pass (offsets times 0.707) averaged 50 percent with the 0 degree pass removes blockiness. Inputs: Image
    closure, Intensity (about 20 px), image width and height typed by hand.
  - Principle: look at four neighbouring areas, pick the one with least colour variance, replace the pixel by its mean.
  - Other tools: the same filter is a 5x5 loop in a three.js ShaderMaterial or an Unreal Custom node (untested).
  - Pitfall: needs Blender 5.0 or later; sockets stay red until the closure is connected. Wiring from frames only partly seen.

- **Painterly grass with attributes read in the shader**: cartoon blades take the ground's colour and have brush-shaped edges.
  - Steps: in Geometry Nodes store "is_grass" (Float, Point, 1) and "hill_normal" (Vector, Point) with Store Named Attribute, and
    expose Set Material. Shader: Image Texture (grass) straight into Surface. Attribute nodes: Instancer "is_grass" as Fac,
    Geometry "UVMap" (ground) as A, Instancer "UVMap" (blade card) as B in a Mix feeding the texture Vector. Scroll a Mapping
    Location with `#frame/-15000` for slow cloud shadows. Blade alpha: card alpha -> Multiply -> Add (Clamp) with 1 minus
    is_grass -> Mix Shader Fac with Transparent BSDF. Lower Minimum Distance (0.08 to 0.007) to keep blades dense.
  - Other tools: instanced mesh with per-instance colour sampled from the terrain plus alphaTest (untested).

## Outlines and line art

- **Line Art modifier toon outlines, with light contour and priority**: real-time outlines drawn as Grease Pencil strokes.
  - Steps (5.2 is Grease Pencil v3; the 2.93 menus differ, so re-check names): Add > Grease Pencil with a Line Art preset (video:
    Shift+A > Grease Pencil > Stroke, then delete its points), modifier Line Art. Source Type Object (Collection or Scene also work),
    Target Layer Lines, Target Material black. Edge Types: Contour, Material Borders, Edge Marks, Intersections, Crease (140;
    30 draws few lines, 180 draws polygon edges). Thickness 25 is heavy, 10 is technical. Edge Marks: Edge > Mark Freestyle Edge.
    Object Viewport Display > In Front. Baking panel: Bake Line Art, then disable (not hide) the modifier in the viewport.
    Light Contour: Light Reference > Light Object, Illumination Filtering, Cast Shadow (needs a receiver plane), Create >
    Silhouette; per-material Intersection Priority makes the higher level win.
  - Principle: line extraction from the camera view onto a stroke layer, styled by the stroke material.
  - Other tools: three.js OutlineEffect or inverted hull; Unity and Unreal post-process edge detection.
  - Pitfall: lines smear in the viewport but are right in camera view; bake before previewing animation.

- **Blueprint look (white lines on blue)**: a white line drawing of any model on a blueprint grid.
  - Steps: Line Art as above with a white Target Material and Crease 140. Model: delete extra materials, one Emission "Blue"
    (HSV 0.630, 0.964, 1.0), copy the colour and paste it into the World colour so surfaces vanish. Stroke data > Layers: Use Lights
    off. Grid: plane subdivided (25 cuts), Wireframe modifier, white emission, a faded second blue (H 0.619, S 0.929, V 0.952).
    Turn the stroke modifier off in the viewport while editing.
  - Other tools: three.js EdgesGeometry plus LineBasicMaterial on a blue background and a GridHelper (untested).

## Comic toon shader: cell shade, screen tone, outline, rim light, glow (Eevee)

Checked in a headless 5.2.2 build (cell shade, screen tone, backface outline, rim, Bloom glow all rendered). Eevee only: Shader to RGB does
not work in Cycles. Rim and outline here ignore light colour.

- **Scene rig**: Sun light Strength 5, Angle 50 degrees (softens the terminator), Cast Shadow off (on, the lit side turns noisy).
  A camera is required (the dots follow it). World Strength 0 so shadows are true black; in the viewport Lighting popover untick Scene World
  and set 0 so the background stays readable. View Transform Standard, not AgX, or flat colours wash out. Principled base colour pure white.
- **Mask method** (every effect below): a grey mask drives the Factor of a Mix node (Data Type Color, Clamp Factor on); Factor 0 gives A, 1 gives
  B. A is the result so far, B is the effect colour. Chain: base, shadow, screen tone, outline, rim. Group each effect (Shift P frame, F2 name);
  keep Material Output outside groups. Node Wrangler: Ctrl+Shift+click a node previews it.
- **Cell shading**: Principled BSDF -> Shader to RGB -> Color Ramp (Constant; black stop 0, white stop about 0.45 to 0.56, frame showed 0.564) ->
  Factor of Mix (A shadow colour, B lit colour). B-Spline interpolation instead gives a soft ramp.
- **Screen tone (halftone dots)**: Camera Data View Vector -> Voronoi Texture (2D, F1, Euclidean; Detail, Roughness, Lacunarity, Randomness all 0)
  Distance -> Math Less Than, Value 1; Value 2 = Color Ramp output fed by Shader to RGB of a Glossy BSDF (Roughness 0.8 widens the highlight;
  ramp stops 0 and 0.9, Linear). Math result is the Factor of a Mix (B = dot colour). Dot size follows the ramp: lower is smaller.
  - Scale: the View Vector changes only about sensor/focal across the frame, so cells across the frame is about Scale x 0.42 at 85 mm. Use
    Scale 200 or more; the video's 5 is a first test value and gives a few blobs. Judge from the camera view.
  - Rotate or move the dots: Mapping node (Type Texture) after Camera Data, Z rotation and X/Y location.
- **Hatch shadow**: the same setup with a Wave Texture (all values 0 except Scale; Profile Sine changed to Triangle). Invert the ramp so the
  lines sit in the dark areas, and use it as the shadow mask.
- **Flat or one-small-shadow chibi shading**: flat = a Color node alone. Small shadow = Principled or Diffuse -> Shader to RGB -> Color Ramp
  -> Math Less Than (threshold 0.02, heard) -> Mix Factor (A main colour, B shadow). Rotate the light so only a thin crescent is dark. Make
  the shadow more saturated (pink on white), not just darker; with a texture in A use blend Multiply. Eyes are dark brown, not black, and the
  line colour must equal the eye colour.
- **Backface outline (geometry)**: object gets two material slots, outline last. Outline material: Settings > Surface > Backface Culling >
  Camera on, flat Color node. Solidify: Offset 1, Thickness 0.03 to 0.04 (outline width), Normals > Flip on, Materials > Material Offset 1.
  Link materials to other objects: select them, the source object last, Ctrl-L > Link Materials. Variable width: Solidify Thickness vertex
  group. Uniform and works on low poly, but doubles vertices and self-intersections show. Python names: `material.use_backface_culling`,
  `modifier.use_flip_normals`, `modifier.material_offset`.
  - Fresnel outline (cheap): Layer Weight Fresnel (Blend 0.5) or Facing (thicker) -> Color Ramp Constant -> Mix Factor. Fails on flat and low-poly surfaces.
- **Rim light**: outline mask = Layer Weight Fresnel (Blend 0.5) -> Math Greater Than (0.25; the threshold is the rim thickness). Light mask =
  Diffuse BSDF (white, Roughness 0; reuse the material's own BSDF for accuracy) -> Shader to RGB. Rim mask = Math Multiply (light x outline),
  optionally Greater Than 0.1 for a hard edge. Mix: Factor rim mask, A previous result, B rim colour. Works over any texture if the chain is
  turned into colour with Shader to RGB first.
  - Backface variant (unproved in the render): in the outline material multiply Normal by -1 (Vector Math Multiply, then BSDF Normal), because
    the flipped shell inverts the light; then Shader to RGB, Greater Than, Mix.
- **Glow**: Compositor Glare node between Render Layers and the output (5.x: a node group stored in `scene.compositing_node_group`; set
  `render.use_compositing`). Type Bloom, Size 0.9, Quality High, Strength 1, Threshold 1 (default Size gave no glow). Raise the rim colour
  Value above 1 (1.7 in the video, type it in the colour field). Sun Beams and Streaks are the other types.
  - Backdrop and night: Alpha Over for a solid background colour; Mix (Multiply) with a tint colour for a night variant.
- **Grease Pencil ink outline for a flat character**: Add > Grease Pencil > Blank, camera required. Modifier Line Art (Python id `LINEART`),
  Source Type Collection or Object, one modifier and one layer per part (Body, Face, Limbs; layer Use Lights off). Edge Types: Contour only (if
  artefacts, Silhouette); face detail drawn as loose edges: Loose on, Contour off. Thickness 0.03; Depth Offset 1 m stops clipping. Then Length
  (Absolute, negative Start and End so strokes stop short), Thickness with a custom curve (thin, thick, thin; ends not zero for limbs), and
  Simplify Iterations 2 for a hand-drawn wobble. Interior lines: a second layer with a white material and the Silhouette invert button. Manual
  lines: edge select, Ctrl-E > Mark Freestyle Edge, Edge Marks on. Reuse on a second character: duplicate the GP object, swap collections.
  Frame values: Line Radius 0.002 (interior pass), Crease Threshold 140, Uniform Thickness 0.030. Python ids: GREASE_PENCIL_LENGTH, _THICKNESS, _SIMPLIFY.

## Pixel art

- **Render small, then enlarge with nearest**: pixel art from a 3D model.
  - Steps: Eevee, Diffuse BSDF -> Shader to RGB -> Color Ramp (Constant, about 0.159) -> Brightness/Contrast (Bright -0.25,
    Contrast -0.5). Small hard area light (power about 500). Camera straight on. Output 64 x 64 (range 16 to 256), Film >
    Transparent on, Filter Size 0.01 px, PNG RGBA sequence. Enlarge: new file, import as Images as Planes, Image Color -> Emission,
    Interpolation Closest. Darken back limbs so the silhouette reads.
  - Principle: few flat colours, tiny resolution, no filter, nearest sampling.
  - Other tools: three.js render target with NearestFilter drawn as a quad; Godot SubViewport 64 x 64 with Nearest; Unity point filter.
  - Pitfall: Shader to RGB works in Eevee only; two-colour shading blobs together; big soft lights flicker.

- **Pixel Blender Kit (free add-on)**: pixel and isometric cameras, live pixel preview, outline, toon with dither.
  - Steps: Edit > Preferences > Add-ons > Install from disk; N-panel tab "Pixel Kit". Set up Render Settings (Eevee, Pixel Filter 0,
    sRGB), Pixel Camera or Isometric Camera (Orthographic, Create Camera), Set up Viewport Preview (Transform nodes with Nearest down
    and up), Outline (Line Thickness 2), materials Flat, Toon (Constant ramp, 3 stops near 0.333 and 0.66, dither from 128 px
    up), Image to Pixel, Flat UV palette.
  - Other tools: same downscale and upscale chain as above in any engine.

- **Pixel texture node: Voronoi quantised UVs and Snap posterise**: any texture becomes chunky pixels with a crushed palette.
  - Steps: Voronoi (3D, F1, Euclidean, Randomness 0, Scale 128) with the UV as Vector; its Position output is the image Vector.
    Posterise: Image Color -> Separate Color -> three Math Snap nodes -> Combine Color, one Math Add (0 + 0.05) feeds all
    three Increment inputs (below 0.1 looks best). Ctrl+G as "Pixelation" (Scale) and "Color Limiter".
  - Other tools: `floor(uv * res) / res` plus a colour quantise in a shader (untested).
  - Pitfall: needs clean UVs. Feed the Voronoi Vector from a UV Map node, and set the Image Texture to Interpolation Closest.
  - Checked in 5.2.2 by script (Snap increment 0.2 gave a clearly crushed palette, 0.05 as above is subtler): works as written.

## Wear, grime and mapping

- **Dirty Vertex Colours plus AO grime mask**: crevice and edge dirt on a clean shader.
  - Steps: Vertex Paint, delete existing Color Attributes, Paint > Dirty Vertex Colors (Blur Strength 1.0, Iterations 10,
    Highlight Angle 90, Dirt Angle 0, Dirt Only off, Normalize on), run twice for thicker dirt, rename the attribute "Grime".
    Shader: Ambient Occlusion (Samples 16, Distance 1) -> Color Ramp, Attribute (Geometry, "Grime") -> Color Ramp, Mix Multiply
    Factor 1 -> Mix Shader Fac between the clean Principled and a duplicate with duller colour, higher roughness and no bump.
    Cavity only: tick Dirt Only and mix a bright and a painted wood.
  - Principle: wear sits in cracks, edges and where hands touch; the vertex noise gives a warbly grunge AO alone cannot.
  - Other tools: Substance smart masks do it automatically; in three.js bake the grime to vertex colour (untested).
  - Pitfall: needs dense meshes (65k verts in the video); AO node does not run in Eevee Next the same way, so use Cycles or bake.

- **Edge wear and cavity masks (Bevel dot, Pointiness, AO)**: Substance-style smart masks in nodes.
  - Steps: Bevel node (Samples 4, Radius 0.05; stronger around 0.25 to 0.75 (heard)) Normal -> Vector Math Dot Product with Geometry
    Normal -> Color Ramp (stops near 0.324 and 0.658). Alternative: Geometry Pointiness -> Color Ramp (stops 0 and 0.505). Combine
    with AO (cavity) in Mix Screen, break up with a grunge Mix, then Color Ramp -> Mix Shader Fac between two materials
    (painted and rusted, rough wood and dirt). Painted masks: Image Texture "mask" screened in after the ramp.
  - Principle: bevelled normal differs from the real normal only at edges; AO catches crevices; grunge breaks the clean mask.
  - Other tools: bake curvature and AO and mix in a shader (untested).
  - Pitfall: Bevel and Pointiness are Cycles only; Pointiness needs enough geometry.

- **Positional gradient broken by grunge**: roughness or paint amount that varies top to bottom.
  - Steps: Gradient Texture on Generated coordinates, Mapping Y rotation 90, Color Ramp B-Spline -> Roughness. Mix Multiply with a
    grunge image, second ramp to limit; Screen for an extra scratch layer. Bump Strength 0.015 from the grunge for dents.

- **Two full materials mixed by a grunge map**: paint with metal showing through, fabric on wallpaper.
  - Steps: Mix Shader with material A (paint) in the first slot and B (worn metal) in the second; Image Texture grunge Color (Non-Color)
    into Fac, a Color Ramp for contrast. Colour mask for dirt: Mix with dirty and clean colours, grunge as factor, multiplied by
    the dirty-vertex mask. Box-project grunge on meshes with no UVs.
  - Principle: any greyscale map is a mask; Mix Shader Fac blends whole materials.
  - Other tools: `mix(materialA, materialB, mask)` in any shader.

- **Box mapping with Blend (free tri-planar)**: stops stretching without unwrapping.
  - Steps: Image Texture Projection Flat -> Box, Blend 0.25 to 0.5; vector from Texture Coordinate Generated or Object through
    Mapping (Scale 0.25 in the house video). With Smart UV Project first, then Node Wrangler Ctrl+Shift+T and Box on every image.
    Mosaic UV mapping (free add-on) or paid scatter tools hide repetition (Mosaic: Scale 50, Aspect 1, Rotate 14.2).
  - Other tools: Godot Triplanar checkbox, Unity Triplanar node, three.js custom shader.
  - Pitfall: poor for directional wood grain.

- **Displacement that actually displaces (Cycles)**: real geometry from a height map.
  - Steps: height map -> Displacement node (Midlevel 0.5, Scale 0.05 to 0.1; default 1 explodes the mesh) -> Material Output
    Displacement. Material Properties > Settings > Surface > Displacement: Displacement and Bump (default Bump Only is why nothing
    happens). Subdivision Surface with Adaptive Subdivision (Dicing Scale 2 for coarse stylized textures). Keep Subdivision above Bevel.
    Notes disagree on the Feature Set Experimental switch (needed up to 3.x, removed by 4.2 according to one note): look in Render
    properties first (unverified for 5.2). If tears appear, copy the displacement strength into the Bump strength.
  - Other tools: bake the height to a normal map for engines; Nanite or tessellation elsewhere.
  - Pitfall: viewport stays low-poly until Rendered view.

- **PBR set in one keystroke (Node Wrangler)**: Principled wired from a folder of maps.
  - Steps: Node Wrangler is a bundled extension (Preferences > Get Extensions). Select the Principled node, Ctrl+Shift+T, pick the
    maps (skip Opacity and the DirectX normal; use the OpenGL normal), Principled Texture Setup. Base Color sRGB, every other map
    Non-Color, normal through a Normal Map node, height through Displacement. AO is never imported: Mix Multiply it. One Value
    node into Mapping Scale resizes all maps. Prefix and suffix names are set in Node Wrangler preferences.
  - Principle: the preset only builds nodes; file suffixes decide the socket.
  - Other tools: same map convention in three.js MeshStandardMaterial, Godot and Unity.
  - Pitfall: metal-roughness maps only; lower Specular IOR Level to 0.25 on a washed-out part.

- **Principled BSDF v2 reference**: what each socket means and which value to try.
  - Steps: Distribution Multiscatter GGX (no energy loss at high roughness). Subsurface Random Walk; Fixed Radius for thin curved
    parts, weight by a mask rather than one global value. Metallic as a map. Roughness noise matters most. Base Color without baked
    lighting. Coat for pottery and car paint, Sheen Weight on every fabric, Anisotropic under Specular for brushed metal, IOR 1.45
    default. Normal Map strength near 1 (v2 no longer shows black artefacts at high values). Emission: coat now renders above it.
    Frosted glass uses Roughness (Transmission Roughness is gone). The IOR-to-Specular helper group is obsolete: set IOR directly.
  - Principle: realism comes from variation and honest base colour, not single sliders.
  - Other tools: maps to glTF KHR_materials_sheen, clearcoat, ior, anisotropy.

## Skin, wax and thickness

- **Thickness mask for subsurface**: light shows only through thin parts, so ears glow and cheeks do not.
  - Steps: Ambient Occlusion with Inside and Only Local on, Invert Color after it, lower Distance until thick areas are black; Invert -> Subsurface
    Weight. Or Raycast (5.1+): Geometry Incoming -> Vector Math Scale -1 -> Raycast Direction; Hit Distance -> Map Range (From 0 to 0.08,
    To 1 to 0, later Smoother Step 0 to 0.1) -> Subsurface Weight (Random Walk, Radius 1, 0.2, 0.1, Scale 0.05 m). Wax: dark yellow
    Base Color, Layer Weight -> Color Ramp -> Subsurface (heard). Tint Subsurface Radius orange-red for skin.
  - Principle: a ray fired inward measures wall thickness; invert so thin means bright.
  - Other tools: thickness baker in Substance; Unreal subsurface profile opacity map; Godot Transmittance map.
  - Pitfall: Raycast and AO are Cycles only; the effect breaks if the object is not at real scale.

- **Raycast depth and hit-normal glow in Eevee**: x-ray look, rounded cube shows what sits inside, glowing egg.
  - Steps: Raycast Hit Distance -> Map Range (From Max 2.35) -> Emission mixed with Transparent BSDF (Mix Shader 0.999); Render
    properties > Raytracing on, Screen Trace, Render Method Blended. Hit Normal -> Layer Weight Normal; Facing -> Subtract 1 ->
    Power 3.5 -> Map Range (From Max 0.2); second Layer Weight (Blend 0.5) -> HSV (Hue 0.570) -> Color Ramp -> Base Color.
  - Pitfall: needs some transparency or ray data is invalid (possibly a beta quirk); factor must stay below 1.

- **Fake SSS in Eevee with Layer Weight**: warm rim on ears and nose.
  - Steps: duplicate the head material as "SSS" for ears and nose; Base Color -> HSV (Hue 0.475, Value 1.25 to 2) into B of a Mix, A =
    original; Layer Weight (Blend about 0.7) as the factor.
  - Other tools: `mix(base, warm, pow(1 - dot(N, V), p))` in a three.js shader.

- **Skin shader with painted blush and per-area pores**: a reusable skin group with a painted layer.
  - Steps: skin group (Scale 5, Skin Color, Subsurface off, Subsurface Color). New Image 2048, copy the skin colour into it
    (Ctrl+C on the swatch, Ctrl+V on the image), image Color -> Skin Color; paint blush and freckles. Pores: scale a UV island down
    to about a quarter for bigger pores on the nose. Thin-skin mask: image -> Color Ramp (stops near 0.417 and 0.9) -> Invert ->
    Subsurface (set to 1 in the group).
  - Pitfall: overlapping UV islands show seams; without the mask the whole head glows.

## Glass and transparency

- **Believable glass**: not a perfect pane; thick, tinted, dirty, slightly warped.
  - Steps: model about 0.5 cm thickness (Solidify), Glass BSDF or Principled Transmission Weight 1, IOR 1.45 to 1.5, Multiscatter.
    Stains and a grunge image through a Color Ramp into Roughness, a scratch normal map into Normal Map (Strength 0.25) or Bump. Faint
    yellow tint, darker edges. Brighter: Mix Shader with Light Path Is Shadow Ray as Fac, Transparent BSDF on one input. Visor
    micro-bump: Noise (Scale 1000, Detail 2) -> Normal Map (Strength 0.15, never straight into Normal), Roughness 0.15 (heard).
    Robot screen: Glass (Roughness 0, IOR 1.45) mixed 0.5 with Transparent.
  - Pitfall: zero-thickness panes refract wrongly; Is Shadow Ray trick is Cycles only.
  - Other tools: three.js MeshPhysicalMaterial transmission, thickness, roughnessMap, normalMap.

- **Eevee glass bottle with Layer Weight alpha**: see-through but not ghostly.
  - Steps: Material Settings Render Method Dithered, Raytraced Transmission on; Layer Weight (Blend 0.1) Facing -> Color Ramp (white
    stop 0.462, left stop raised from black to grey) -> Principled Alpha.
  - Pitfall: needs Raytracing on to see transmission; raising the black stop stops the glass being knocked out.

- **RGB split iridescent glass group**: fake dispersion from three layers.
  - Steps: three Principled BSDFs, Base Color red, green, blue, Transmission Weight 1, Roughness 0, IOR 1.45 and +0.05, +0.1 through Math
    Add inside the group; two Add Shader nodes. Ctrl+G "RGB Glass Base", expose three colours, Roughness, IOR, Transmission Weight; grunge
    roughness; Bump Strength 0.015.
  - Other tools: three.js MeshPhysicalMaterial dispersion (r166+) and iridescence. Blender Thin Film is a built-in alternative.
  - Pitfall: Cycles only and noisy.

- **Thin Wall transparency (new in 5.2)**: one checkbox for single-sided planes, glass, foliage, paper.
  - Steps: Principled BSDF, tick Thin Wall below Alpha; remove any Solidify. The subsurface radius is ignored, so put the tint in Base
    Color. A direction slider (-1 to 1, default 0) picks the lit side. Foliage dropped from 26.3 s to just over 2 s render; windows stop
    eating light; a sphere reads as a bubble film. Frosted horror glass: Thin Wall on, Transmission Weight 1, stretched noise Mix
    Multiply 0.25, scratch grunge into Roughness and Bump (Strength 1, Distance 0.001), coloured area lights in front, Cycles 150 samples.
  - Other tools: three.js `thickness = 0`; Unity HDRP thin refraction; Unreal Substrate thin translucent.
  - Pitfall: not for thick glass; Eevee support untested.

- **Air bubbles in goo, and cartoon tears**: bubbles trapped inside glass or goo; clear drop with a cartoon highlight.
  - Steps: Principled Transmission 1, Noise (Scale 5000, Detail 2) -> Bump (Strength 0.05) -> Normal, Color Ramp -> Roughness. Bubble:
    UV Sphere with Flip Normals, same material, named "Particle"; hair particle system with Render As Object, Instance Object
    Particle, Source Volume, Scale 0.15, Scale Randomness 1, Number 150. Tear: Transmission 1, Roughness 0.1 (heard), HDRI in the world,
    a point light parented beside it with power keyed from 0.
  - Pitfall: legacy particles at 4 m default length explode the viewport until Render As is Object; refraction in Eevee needs Raytracing.

## Fabric

- **Fabric that reads as fabric**: Sheen, fuzz, mixed colour, shaped geometry, stitches.
  - Steps: import a fabric PBR set (Node Wrangler Ctrl+Shift+T), Sheen Weight 1 and Sheen Tint (colour in v2; 0.5 old value). Fuzz:
    a hair system on the clothes only (see Fabric fuzz below). Mix several close colours; sculpt seams; stitch with a stretched
    stroke or geometry nodes.
  - Principle: sheen is a roughness lobe for cloth that lights grazing edges; fuzz catches light lighter than the cloth.
  - Other tools: three.js sheen, sheenColor, sheenRoughness; Unreal Cloth model; Unity HDRP Fabric; Godot Rim.
  - Pitfall: Sheen is not physically exact; kept for a stylized look.

- **Cotton character: gradient, weave and painted face**: pink-to-cream body with a painted face over the weave.
  - Steps: Texture Coordinate -> Mapping -> Separate XYZ (Z) -> Gradient -> Color Ramp (HSV Near so the middle does not grey out) ->
    fabric group colours; cotton group Scale 10. Face: new image 4096 with alpha 0, two Mix (Color) nodes with image Alpha as Factor,
    Texture Paint with F for brush size; save the image.
  - Principle: painting into a transparent layer keeps the weave under the paint.

## Procedural effects and materials

- **Look versus light with Is Camera Ray**: glowing surface that lights the scene, or a shadeless unlit look that emits nothing.
  - Steps: Mix Shader, Fac = Light Path > Is Camera Ray; the camera side holds the visible look (Emission 1), the other side the strong
    light (Emission 50). Dust: Emission and Diffuse of one colour, second Mix with Transparent (0.5 to 0.75). Shadeless palette: Image
    Texture -> Emission on the camera side, nothing on the other. Toon water uses it too.
  - Other tools: add a point light and keep the material emissive modest.
  - Pitfall: Cycles; Eevee Next does not treat ray types the same way (unchecked).

- **Layer Weight rim and glow falloff**: fake rim light, fluorescent-tube fade.
  - Steps: Layer Weight Blend 0.5 Fresnel into Material Output (white rim), or Facing into Emission Strength so the glow fades at edges. Feather
    rim: Layer Weight -> Color Ramp (stop 0.14) -> HSV Factor with Value 5 on the colour.
  - Other tools: three.js `1 - dot(normal, viewDir)`; Godot VIEW and NORMAL; Unreal and Unity fresnel node.

- **Energy trail (Nintendo style)**: tapered, fading, animated glowing tube from a curve.
  - Steps: Bezier curve, Bevel Depth 0.16 m, Resolution 4. Noise (Scale 7.3, Detail 0) with Mapping X scale about 0.6 -> Color Ramp (0 and 0.51)
    -> Alpha. Wobble: Mix 0.25 with a second Noise (Scale 2.5). Move: Value `#frame` / 200 -> Combine XYZ -> Mapping Location. Tip fade:
    Gradient -> Ease ramp; Mix Multiply with the noise ramp -> Alpha. Colour: second ramp -> Mix of green and cyan -> Base Color and Emission.
    Taper with Alt+S in Edit Mode. Eevee Next: Render Method Blended and a Glare node instead of Bloom.
  - Other tools: ShaderMaterial with scrolling `uv.y`, additive blending (untested).
  - Pitfall: if noise stops following the curve use Texture Space > Match Texture Space.

- **Toon water**: flat cyan water with distorting foam lines.
  - Steps: Emission in a Mix Shader with Is Camera Ray. Two Voronoi (Distance To Edge, Scale 5), Noise (Scale 5, Detail 0.25, Distortion
    0.1) Fac into both Randomness. Each Voronoi -> Color Ramp Constant (water 30e3ca and 2ad3c9, foam black to white), Mix Screen. Two
    Mapping nodes (Point), bottom Y 90. One Value times three Math Multiply sets scales; key the last Multiply 0.75 to 1.25 to animate.
  - Pitfall: far foam gets busy: lower Voronoi scale, raise noise scale.

- **Animated hologram and light rays**: scan bands, see-through centre, sweeping beam; volume shafts.
  - Steps: Base Color and Emission blue, Strength about 25. Wave (Bands, X, Sine, Scale 15, Distortion 7.5, Detail 2) Phase Offset `#frame/2`
    -> Color Ramp Constant (0 and 0.225). Layer Weight Blend 0.05 Facing -> ramp Ease -> Alpha. Noise (Scale 150, Detail 15) -> Constant ramp (0.389).
    Beam: Gradient, Mapping rotation Y 90, Location X -1 to 1 over 60 frames, Graph Editor Shift+E Make Cyclic. Mix Multiply, Multiply, Add
    for the beam. Light rays: cylinder with Volume Emission, Noise 2D on Object coordinates -> ramp (0.525) x intensity -> Emission Strength.
  - Other tools: sin of world Y plus time, fresnel alpha, moving smoothstep in a three.js shader (untested).
  - Pitfall: Eevee needs Render Method Blended for alpha (inferred).

- **Anime speed lines shader**: streaks for motion backgrounds.
  - Steps: Noise (3D, fBM, Normalize, Scale 15, Detail 15) via Mapping Scale X 0.05, Y 5, Z 1 -> Color Ramp Constant (two blues). Key Mapping
    Location X 0 to 1 over 10 frames, Graph Editor T Linear, Shift+E Linear Extrapolation.
  - Principle: extrapolation gives endless uniform motion you can retime by dragging keys.

- **Fake caustics in Eevee**: moving light patterns driven by an empty.
  - Steps: Texture Coordinate Object (the empty) -> Mapping -> Noise (Detail 0) and Voronoi (2D, Distance to Edge) with Value-driven scales ->
    Color Ramp -> Mix Add over the colour. Move the empty to animate.

- **Clay cartoon flame**: low-poly flame whose top wobbles.
  - Steps: Round Cube (Extra Mesh Objects extension) Quad Sphere, 8 divisions, pull the top up with proportional editing. Displace with a Clouds
    texture (size about 0.75, depth 0), Coordinates Object with an empty, Strength 0.3, vertex group "Fire" smoothed (Weights > Smooth, 30
    iterations). Empty Z `#frame/5`, flame Z `#frame/100`; parent to a control empty; Subdivision on top.
  - Other tools: vertex shader with noise at position + time masked by vertex colour (untested).

- **Stylized rock from masks**: blue-grey rock with worn edges, divots and strata.
  - Steps: two AO nodes (Distance 0.1 and about 0.2) -> Color Ramps -> Mix Screen -> Mix factor between stone and lighter worn colour. Divots:
    Voronoi Smooth F1 Scale 13.9 -> ramp black stop 0.211, plus Scale 50 Multiply. Strata: Wave (Bands, Diagonal, Saw, Scale 2.5, Distortion 7.5).
    Detail x strata Mix Multiply 0.8 -> Roughness and Displacement (Scale 0.015); Base Color Multiply 0.4; final AO.
  - Pitfall: needs dense mesh; AO does not run the same in Eevee Next, so bake or use Cycles.

- **Stylized wood node group from one image**: colour, roughness, bump and displacement from one hand-painted tile.
  - Steps: image Color -> Base Color; three Color Ramps: roughness (inverted so raised boards are shiny, stops 0.25 and 0.35), bump (stop 0.691)
    -> Bump, displacement -> Displacement (Midlevel 0 to stay level, Scale 0.25). Ctrl+G "Wood" exposing Hue, Saturation, Value, Scale, Strength.
    Aged wood: wear mask into a Mix Shader of two Wood groups (heard).
  - Pitfall: fine adaptive dicing shows every stroke; stylized textures want a coarse Dicing Scale (2).

- **Coffee, leaf and ground from one image**: one image driving colour, roughness and relief.
  - Steps: coffee photo -> two Color Ramps (roughness; eased bump), Hue/Saturation 1.2. Leaf: image plane with alpha, Subdivide, proportional
    edit, Color -> Color Ramp -> Roughness and Bump. Ground splat: two Node Wrangler PBR sets, mask (Non-Color) -> Color Ramp -> Mix Shader Fac and
    displacement Mix.
  - Other tools: alpha-tested cards with normal maps; Unity and Unreal landscape layers; three.js two-set mask shader.

- **Dynamic colour palette**: one object's custom properties recolour every material.
  - Steps: plane with material "Dynamic Color Palette", delete Principled and Output. Object properties > Custom Properties > New > gear: Float Array,
    Length 3, Subtype Linear Color. One RGB node per colour, Ctrl+G "Dynamic Palette", outputs named in the group Interface panel (N panel > Group in
    3.x). Hover the property colour, right click R, Copy as New Driver, then Paste Driver on each RGB channel. Save the palette object as an asset.
  - Other tools: Godot global shader uniforms, Unity `Shader.SetGlobalColor`, Unreal Material Parameter Collection.
  - Pitfall: three drivers per colour; non-linear subtype looks washed out.

- **Per-brick colour with Random Per Island**: each brick its own colour without splitting objects.
  - Steps: select the bricks, UV > Unwrap > From Active Quads; Geometry > Random Per Island -> Color Ramp Constant -> AO colour mix. Noise (Scale 500) bump.

- **Gaussian splat material (5.3 beta, not 5.2)**: lights on a scanned splat.
  - Steps: New material, replace Emission (Attribute `radiance`) with Principled BSDF fed by the colour; add a point light. Baked lighting cannot be removed.

## Texture painting

- **Painterly paint brush**: strokes that read as bristles.
  - Steps: Texture Paint, duplicate Paint Hard, Falloff last preset, Texture Mask new texture from a black-and-white grunge, Strength 1, Radius about 23 px,
    Blend Mix. Paint a lighter colour for highlights. Brush into the Normal map with a layer add-on for relief.
  - Other tools: Krita and Procreate grunge-alpha tips.

- **Sticker on a second UV map and projected logo**: decals without touching the main UVs.
  - Steps: Object Data > UV Maps > + "sticker", U > Project From View, align in the UV editor; shader UV Map node (sticker) into the image Vector. Logo
    by stencil: Texture Paint, brush texture Mapping Projection (heard).

- **Painted details over a base, flat cartoon eyes**: stripes, pupils, soot sprite, set-in eyes.
  - Steps: image Color -> Hue/Saturation/Value (tint without repainting). Soot sprite: charcoal not pure black, off-yellow eyes, Roughness 0.75, Specular IOR
    Level 0.15, hard-edge brush. Eyes as floating filled pills: Circle, extrude to a pill, F to fill, nearly black material, just in front of the face.
  - Principle: a slightly lifted black and a hard brush give a clean cutout look; a pill casts a small real shadow.
  - Pitfall: a circle is invisible until filled; avoid z-fighting.

## Hair and fur

- **Hair assets stack (Quick Fur)**: editable geometry-nodes hair on a Curves object.
  - Steps: Object > Quick Effects > Quick Fur or drag from Essentials > Hair. Stack top to bottom: Set Hair Curve Profile (Radius 0.001, Shape 0.5), Interpolate Hair Curves
    (UV map needed, Guides 4, Poisson Disk, Follow Surface Normal, Density 100000 or lower), Trim, Noise (Distance 0.005), Curl (Guide Distance 0.02, Factor 0.5,
    Radius 0.02, Frequency 4), Clump (Guide Distance 0.005), Frizz (Distance 0.005, Shape -0.5), Surface Deform, Rotate. Density masks come from vertex groups.
  - Pitfall: armature or shape keys above Surface Deform; Surface Deform near the end; hair is not dynamic. Names of assets should be confirmed in 5.2.

- **Needle-felted fur**: fluffy puppet from curve hair plus tiny particle fuzz.
  - Steps: clean UV (seams, Unwrap, Pack Islands), F3 Quick Fur. Stack: Set Profile, Interpolate (Interpolation 4, Poisson, Follow Normal), Curl (Factor 1, Frequency 4, Radius 0.28,
    Random Offset 0.25, Guide Distance 0.1), Noise and Frizz (Preserve Length, Distance about 0.05), Surface Deform. Fuzz: particle Hair with tiny length, B-Spline, Render
    steps 6, Brownian 0.05 to 0.2.
  - Other tools: card fur or shell fur shader.
  - Pitfall: density is the real cost; keep viewport amount low.

- **Fabric fuzz with a hair particle system**: short hairs on the clothes only.
  - Steps: vertex group Cloth; Particle > + > Hair; Number 1000, Hair Length 0.1 (default 4 m), Segments 5, Emit From Faces, Density = Cloth. Children Simple 25, Length 0.15,
    Clump 0.05, Roughness Uniform 0.1, Kink Curl Amplitude 0.05, Frequency 2. Material: Principled Hair BSDF (Direct Coloring, lighter colour, Roughness 0.3, Radial 0.3, IOR 1.55).
  - Other tools: shell fur in shaders.
  - Pitfall: shorten before anything else; particle count times children explodes; Principled Hair is Cycles only.

- **Stylized curve hair**: chunky teardrop strands, sculpted.
  - Steps: Add > Curves > Empty Hair, Curves sculpt Add brush (Sphere falloff). Stack: Surface Deform, then a node tree: Set Curve Radius, Curve to Mesh (Fill Caps, Curve Circle
    resolution 5 for chunky), Set Shade Smooth off. Radius: Spline Parameter -> Color Ramp (third stop for teardrop, raise tip). F3 "Convert Curves to Particle System" for children.
  - Pitfall: low-resolution profile with flat shading gives the blocky anime look; turn the modifier off while grooming.

- **Feather and fur balls with custom normals**: instanced feather cards that shade as one smooth shape.
  - Steps: Quad Sphere (Extra Mesh Objects Round Cube), Scatter on Surface: Density 150, Scatter on Instances, Align Rotation to Y, Rotation X -25, Y 15, Z 15, Scale 0.15. Normals proxy:
    subdivided copy "Normals"; Object Info -> Sample Nearest Surface (Vector, Normal) -> Set Mesh Normal Mode Free. Shader: Gradient on UV Y -> B-Spline ramp, Noise (Scale 2, Distortion
    1.1, Mapping X 5), random colour "rancolor" attribute, rim by Layer Weight.
  - Pitfall: Eevee ray tracing with Fast GI off or 1 ray; use simple proxies for complex characters.

- **Per-strand hair colour**: broken colour like real hair and wool.
  - Steps: Principled Hair BSDF (Roughness 0.75, Radial 0.5, Random Roughness 1; Coat about 0.75 (heard)). Curves Info Random -> Color Ramp Constant (3 to 4 stops) -> Mix; Intercept
    -> ramp for darker roots (HSV Hue 0.475, Value 0.5). Baked hair colour: Bake Diffuse Color only (Direct and Indirect off) into the UV map and read it in the hair material.
  - Other tools: per-instance random colour in Unreal and three.js (untested).
  - Pitfall: Curves Info replaced Hair Info; bake only Color or lighting is baked in.

- **Legacy particle hair and combing**: thick curly hair that renders fast.
  - Steps: model the hair mass as icospheres, vertex group "Hair" for Density, Particle > Hair, Length 0.25, Number 1000, Segments 6, Children Simple (Display 10, Render 100),
    Diameter Root 0.25, Roughness 0.025, Kink Curl (Amplitude 0.1, Frequency 3), Principled Hair BSDF in Render > Material. Particle Edit: Comb, Smooth, Add, Length, Puff, Cut.
  - Pitfall: combing locks settings; armature above particles; legacy route, rebuild with Curves hair if possible.

- **Hair dynamics with a loopable cache**: simulate on mocap and bake.
  - Steps: Hair Dynamics, Quality Steps high, Stiffness 1. Paste the first dozen keys before the start, set Start -50 and End 394, Bake, Delete bakes before changes.
  - Pitfall: only approximates a loop.

## Add-ons

- Pixel Blender Kit: pixel art tools. Free (Superhive).
- Stop-Mo panel (stepped timing and Animate Texture): free.
- Crafty Asset Pack: materials, fabric, grunge maps; free sample, full pack paid.
- Scattershot (CG Cookie): image scattering and tri-planar; paid. Free alternatives: Box mapping with Blend, Mosaic UV mapping.
- Mowgli toolbox: free array, fields and falloffs paid.
- Substance 3D add-on: .sbsar materials; free add-on, assets from Substance Source and Share. Status in 5.2 unchecked.
- Ucupaint: paint layers; check Extensions.
- Node Wrangler: bundled extension.

