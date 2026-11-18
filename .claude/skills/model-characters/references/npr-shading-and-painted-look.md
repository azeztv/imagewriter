# NPR Shading, Outlines and Painted Textures

Shared reference. Character, background and animation skills link here. It holds the toon shader, the lighting rigs, the outline
modifiers and the painted-texture layers behind the "2D looking" Blender look. All
steps are for Blender 4.2+ and 5.x in EEVEE. Old names are mapped: the Color node was called RGB before 5.0, the Filmic view
transform is replaced by AgX (default since 4.0) and Standard, and the Laplace "node" is the Filter node set to Laplace.
Shader to RGB works in EEVEE only, never in Cycles. Paid add-ons (Stylized Asset Suite, Windy Armature, Anime Ocean) are named
only to map them to the plain-node route. Do not buy them.

<!-- skill-navigation:start -->
## Reading Map

- [NPR Shading, Outlines and Painted Textures](#npr-shading-outlines-and-painted-textures)
- [1. Toon shader and view transform](#1-toon-shader-and-view-transform)
- [2. Lighting rigs for characters](#2-lighting-rigs-for-characters)
- [3. Rim, edge and gloss masks](#3-rim-edge-and-gloss-masks)
- [4. Banded gradients and colour variation](#4-banded-gradients-and-colour-variation)
- [5. Outlines](#5-outlines)
- [6. Painted mask layers (darks, brights, blacks)](#6-painted-mask-layers-darks-brights-blacks)
- [7. Sketchy, manga and pastel looks](#7-sketchy-manga-and-pastel-looks)
- [8. Value rules for painted characters](#8-value-rules-for-painted-characters)
- [9. Bake and export](#9-bake-and-export)
- [10. Compositor finish](#10-compositor-finish)
- [11. Paid add-on to plain-node map](#11-paid-add-on-to-plain-node-map)
<!-- skill-navigation:end -->

## 1. Toon shader and view transform

- **Base toon shader** (every material in his scenes):
  1. Shader editor > New. Delete Principled BSDF.
  2. Add Diffuse BSDF > Shader to RGB > Color Ramp, interpolation Constant. Two stops: dark = shadow colour, light = lit colour.
     Ctrl+click on the ramp adds a flag for a middle tone.
  3. Multiply (Mix node, Multiply) the ramp with a Color node (base colour). Use a Sun strength near 14 for harsher light.
  4. Node Wrangler (still bundled, enable in Preferences > Add-ons): Shift+Ctrl+click previews any node, Ctrl+T adds Texture
     Coordinate and Mapping to a texture node.
  - Use one Sun for this style. Share one material across objects with Ctrl+L > Link Materials. Every object must catch light
    on at least part of its surface or it reads flat.
- **Tinted two-tone**: push the white stop fully right, set highlight orange and shadow blue, then Multiply with the base
 colour.
- **One-step light, blue shadow**: two ramp stops only, Mix(Multiply) a blue onto the dark side. Source:
.
- **Light order**: lighting goes after the painted layers in the node chain, so paint sits under the light. Source:
.
- **Reusable lighting group**: select the Diffuse, Shader to RGB, Color Ramp nodes, Ctrl+G, rename ("main light"), paste the
  group into every material of the character. One edit then changes all. Hair gets the same group multiplied into the painted
 hair texture.
- **View transform**: Render properties > Color Management > View Transform = Standard (not AgX or Filmic) so painted colour does
  not wash out. Work in Standard from the start, most of all when you export. Sources:
,
.
- **Preview settings**: Compositor on Always, then two Filter nodes (Soften, then Box Sharpen). Turn on EEVEE ray tracing only as a
  visual aid: Shift+Ctrl+click on Diffuse BSDF then shows where bounce light would fall. Source:
.
- **Hand-drawn face light**: for a cinematic, paint the face light and shadow shapes by hand and switch them on or off per shot,
  because toon light on faces is often wrong. Warm the highlights toward orange and darken the shadows to match the scene.
- **Two-shade rule**: every object must read two shades. Make big shapes first, tune small props last. Source:
.

## 2. Lighting rigs for characters

Use one to four lights per scene. Main plus rim for the character, main plus rim for the environment, sometimes one light only.

- **Two-sun key and rim** (plain nodes, colour-coded lights). Sources:
,
.
  1. Add a Sun, colour pure red (R 1, G 0, B 0). A red sun loses strength, so raise it: about 4 in the node version of
     the lighting video, 10.5 to 11 in the painted-character video. Keep both values with their sources.
  2. Shift+D the Sun, colour pure blue (R 0, G 0, B 1), strength 1, aim from the side or back. This is the rim light.
  3. Main light nodes: Diffuse BSDF > Shader to RGB > Color Ramp (HSV mode is easier). Highlight value near 2.5 warm orange, shadow
     bluish. Mix(Multiply) with the base colour, and use the Fac as a strength slider.
  4. Rim nodes: copy Diffuse BSDF + Shader to RGB, add Separate Color after Shader to RGB, take Blue into a Color Ramp (the red
     channel is the first light, so each coloured light is isolated). Mix with Fac = that mask, Multiply or Screen onto the
     previous result, B = bright rim colour. Adjust only the highlight colour of the rim ramp.
  5. Put each light in its own group ("main light", "rim light"), paste into every material.
  - The lights must stay pure single-channel colours so Separate Color can split them. Red and blue are identification channels,
    not final colours.
  - Ramp thresholds (rebuilt and rendered in Blender 5.2, EEVEE, Standard): Color Ramp reads a colour as its luminance (red only
    gives 0.21 x R), and a Diffuse lit by a sun of strength S at angle a reads about 0.8 x S x cos(a) / pi per channel. With red
    strength 4 the lit side is only about 0.17, so a ramp stop at 0.3 or 0.5 leaves everything in shadow (flat shadow colour). Put
    the light stop of the main ramp near 0.08 and the rim ramp stop near 0.12, or raise the sun until the lit value passes the stop.
    Blue strength 3 aimed low from behind and to one side (rotation X -80, Z -60) gives a visible rim band; strength 1 from above
    gives only a sliver.
  - Scripted build (bpy): create suns with `bpy.ops.object.light_add(type="SUN", rotation=...)`, and set `light.data.color` and
    `light.data.energy`. Mix node sockets share names across data types: with `data_type="RGBA"` use `inputs[6]` (A), `inputs[7]`
    (B) and `outputs[2]` (Result); `inputs["A"]` hits the float socket and silently breaks the chain. A flat gradient in the
    viewport or a black frame from Shader to RGB usually means the outline hull is shadowing the character (see Outlines).
- **Light linking** (Blender 4.0+): select the character parts, M > New Collection "character". Select a Sun, Object properties >
  Shading > Light Linking, set Receiving Collection or Blocker to that collection. Repeat with duplicate suns for an
  "environment" collection. New objects get no light until they join the linked collection. Panel name: unverified on a frame.
- **Sky fill from a blue sun** (static scenes): Separate Color on the blue sun into a Constant ramp, Subtract the red-sun ramp
  from it so blue shows only where the red sun misses, Mix factor with B = HSV with raised Value. Source:
.
- **Rim only on the top**: Layer Weight (Facing) times a bottom-to-top Gradient Texture with Math Multiply, so edge glow does not
 appear on faces that point down.
- **Warm near the subject, blue far**: Gradient Texture (Texture Coordinate Object, pointing at an Empty, type Quadratic Sphere) as
  Fac, Mix set to Multiply: white multiplies orange, black multiplies blue. Move the Empty to move the pool of light. The same
  Empty-driven sphere gradient works as a movable light on a character. Sources:
.
- **Light blocker**: scale a Cube so it casts shadow on part of the character or scene. Source:
.
- **Top-down preview**: light from straight above while you paint, so highlights land on top edges and shadows below. Source:
.
- **Skin care**: lighting can kill the handmade look of painted skin. Give the face its own light mask and a different light
 strength from the body, and rework per scene.
- **More than two light levels**: add an environment top light with extra shadow areas, drawn in or from AO. Source:
.

## 3. Rim, edge and gloss masks

- **Layer Weight edge** (Facing or Fresnel) into a Color Ramp (tighten it) into a Mix Fac. B = HSV with raised Value for a bright
  rim, Value 0 for dark crisp edges. Map Range tunes the width. Sources:
,
.
- **Paintable exclusion for the edge**: new image "lw mask", default white, Mix(Multiply) with the Layer Weight output, paint
 black where the edge should vanish (sides of the nose).
- **Glowing game edge**: Fresnel times a crayon texture, saved as a node group and pasted on every clothing piece. Source:
.
- **Toon gloss mask**: Glossy BSDF > Shader to RGB > Color Ramp (Constant, black and white) into the Fac of a Mix. A = toon colour,
  B = bright highlight colour. Roughness sets the size of the shine. For a streaky shine add Noise > Bump (strength about 0.1) into
 the Glossy normal, or threshold the glossy result.
- **Painted metal** (five parts: reflection, distortion, drawn highlights, drawn darks, scratches). Source:
.
  1. Color node into Material Output. Layer Weight (Facing) > Color Ramp, flipped so the centre is bright, black flag crunched
     right, Ctrl+click to alternate white, black, white, black.
  2. Mix: Fac = ramp, A = the Color node, B = HSV with raised Value.
  3. Distortion: Geometry > Normal into the Layer Weight Normal input, with a Mix (Color, Overlay) and Noise Texture between them.
  4. Dark ring: duplicate the ramp with Shift+Ctrl+D, make the lower one larger, Subtract, feed a second Mix with lowered Value.
  5. Bright edge: a second Layer Weight, Fresnel output. Optional top-bright gradient.
  6. Highlights, darks and scratches are image masks in the chain. Highlight zigzag on the front, darks on the sides, scratch = dark
     then bright under it. Bevel the edges and use Shade Auto Smooth.
- **Toon glass**: Glossy BSDF mixed with Transparent BSDF, Fresnel into Fac. Turn off Shadow in the glass object's Ray
  Visibility if milk behind it looks wrong. Glass cannot take a Solidify outline well: use a Layer Weight Facing fake outline, or
 an inflated duplicate (Alt+S) with Transparent BSDF and Solidify.

## 4. Banded gradients and colour variation

- **Binarise or band any value**: Map Range with Interpolation = Steps (Stepped Linear). The step count is the tone count. Sources:
. A stepped gradient
  gives a contrasty anime look. A linear gradient can look plasticky. Source:
.
- **Painterly distortion**: Noise Texture, Ctrl+T, then a Mix between Mapping and the Noise vector with a second Noise in B (Divide
  in the low poly video). Use the result as the Fac of a Mix between a darker and a lighter HSV copy of the toon colour. Sources:
.
- **Hard-edged mottling**: Noise, Color Ramp Constant, Fac of a Mix with an HSV into B. Stretch the noise in Mapping for wood
  grain. UV unwrap by sharp edges (F3 > Select Sharp Edges, Ctrl+E > Mark Seam, U) so the grain reads evenly. Source:
.
- **Random value per duplicate**: Object Info > Random into a Color Ramp (low stop near 0.7) into an HSV Value. Source:
.
- **Master pattern**: every effect is a Mix whose B holds a brighter or darker HSV copy of the colour, driven by a mask. B is the
 white part of the mask and A is the black part.

## 5. Outlines

Solidify inverted hull needs a closed volume. A flat plane (leaf, feather flap, water) first gets a normal Solidify for thickness,
then the outline Solidify. Limit it with a vertex group (Object Data > Vertex Groups > new, Assign, then the modifier's Vertex
Group field; invert if needed). Material: add a second slot, black Color node, move it to the top with the arrow, Material
Settings > Backface Culling on (the cookie video ticks Shadow, maybe Camera too).

| Variant | Offset | Rim Fill | Normals Flip | Material Offset | Verified in frame |
|---|---|---|---|---|---|
| A: outward shell | 1.0 | off | on | 0, 100 or -100 (the videos differ) | Thickness 0.01 m: (Material Offset 0), (-100, Blender 4.0.2) |
| B: inward shell | -1.0 | on | on (unverified in frame) | not visible | Thickness 0.01 m:, (second Solidify after Subdivision, Blender 4.2) |

- Required for either variant: on the black outline material turn on Backface Culling Camera AND Shadow
  (`material.use_backface_culling = True`, `material.use_backface_culling_shadow = True`). Without the Shadow tick the hull
  blocks every sun and the character renders black or flat (measured in Blender 5.2). Material slot order: black outline in
  slot 1 (moved to the top), toon in slot 2 with the faces assigned to it; the Solidify Material Offset of -100 (or 100 when the
  black slot is last) clamps the hull to the end slot, which is why the videos show values like that. A black outline needs a
  grey backdrop to be seen: on a black background it vanishes.
- The cookie and bath videos say variant A in speech but show Offset -1 or Fill ticked on screen. Both work. Try A first. If the
  line is thin or broken, switch to B.
- Uneven outline: Ctrl+A > All Transforms, then Object > Set Origin > Origin to Geometry, then Shift+N on the faces. If every
  object turns black after Link Materials, in Edit Mode select all and Assign the object's own slot.
- Share to many objects: select targets, active last, Ctrl+L > Link Materials, then Ctrl+L > Copy Modifiers. Shade Auto Smooth on
  cylinders and smooth shapes.
- Blurry outlines: material settings, turn off Transparency Overlap (EEVEE), for every object. Source:
.
- Outlines grow when you zoom in. Reduce Thickness per shot.
- Keep eyes out of the outline: vertex group "outline" around the eyes in the modifier. Source:
. Mouth teeth: vertex group "mouth outline" thins it.
.
- Other outlines:
  - Sharp-edge curve: F3 > Select Sharp Edges, Shift+D, P > By Selection, Object > Convert > Curve, Bevel Depth, black material.
  - Accent line: a Path curve with bevel and a black material, placed on clothing where a line is wanted. Source:
.
  - Frame check: Bevel Round curve, Depth 0.036 m, Resolution 4, Fill Caps off (Blender 4.5). Source:
.
  - Crayon outline: copy the hair material nodes into the outline material so a crayon texture breaks the line. Source:
.
  - Line boil: the free Sketchify add-on (install the zip in Preferences > Add-ons, N panel > Sketchify, timing default threes,
 Apply Timing after changes). Retune per shot distance.
  - Whole-render lines: Compositor Filter node, type Laplace, into the Fac of a Mix with black as B. Unverified on a frame. Source:
.

## 6. Painted mask layers (darks, brights, blacks)

The painted skin, face, hair and clothing are all one pattern. Image Texture (new image, black default, 1024 to 4096) into the Fac of
a Mix. A = previous colour, B = layer colour. White paint shows B. Stack layers in series. Sources:
,
.

- Layer types: "blacks" (B = black: eye fold, brows, nostrils), "darks" (B = HSV with Value near 0.6 of the previous colour), "brights"
  (B = HSV with Value near 1.6), "reds" (B = red: lips, blush), "highlights" (B = white). Re-tint a layer by changing B. Value
  numbers from the ninja video.
- Texture Paint: white first colour, black second. Ctrl-click paints black. F sets size, Shift+F sets strength. Full strength with
  grey acts like a dry-erase marker. Low strength builds slowly. The Fingertip (Smudge) brush moves dark areas to wrap the eye. Wireframe
  on while painting. If painting does nothing, select the right image in the shader editor and press Shift+N on the faces.
- A Math Greater Than after the mask hardens a soft painted edge.
- A Mix set to Add that combines the image with itself doubles stroke strength. Source:
.
- Order matters. A black layer under a green layer does not show. Put black after green. Source:
.
- Fake 3D with paint: dark where a crack goes and bright right beside it, bright on edges that catch light, dark on the edge next to
  it, dark lines inside bright areas, AO under objects, keep separate layers for darks, brights, softer darks, subtler brights.
- Low poly to AAA with paint, five passes: (1) bright along every jutting edge, (2) a parallel dark line beside each bright one,
  (3) fake detail as dark with bright beside it, (4) micro detail: scratches (dark then bright under), gradients, pastel washes,
  (5) lighting last. The model must look good with no lighting. Compare in grayscale beside a reference. Sources:
.
- Paint plus bake: bake top-down light or AO to an image and use it as a mask, then draw folds on top (see section 9). Sources:
.
- Per-frame fix: for a face that shades badly in a few frames, keyframe a corrective texture layer on only those frames. Hair
 that cuts the body gets a shape key keyed on the bad frames.
- Fix tiny finger UV islands before painting: seams as rings round each finger, re-unwrap, scale islands up. Source:
.

## 7. Sketchy, manga and pastel looks

- **Cross-hatch skin**: bright grey base, high-resolution Image Texture into a Mix. Paint a soft blob of darkness, then scribble
  hatch lines over it. Always shade under the jaw (severely dark), behind the ear (Y shape), around the eyes, under the clavicle,
 the scalp and the hair shadow on the face.
- **Manga hair as reflection shapes**: black base, white blobs where the hair bulges (threshold a reference photo to black and
  white to see the shapes). One reflection thin in the middle and long at the sides, lines between two reflections at strand
 edges, vary streak length. Do not spray.
- **Clothing scribbles**: black base, white scribbles where the form turns or separates, stitch lines at seams, a streak of
 reflection on a chain.
- **Eye shadow globe**: a slightly larger transparent sphere over the eye (Mix Shader of Transparent BSDF and a dark colour, painted
 Fac). The shadow stays when the eye rotates.
- **Pastel overlay in screen space**: Image Texture of a crayon texture, Mapping with Texture Coordinate Window, Mix Multiply (Soft
  Light on light surfaces, Screen on dark hair). Break the tiling by adding Voronoi Color through Vector Math Add into the mapping
 location.
- **Pastel transparency**: crayon texture into the Fac of a Mix Shader (A colour, B Transparent BSDF), Color Ramp, Math Add for
  overall opacity, Alpha Blend. A copy opaque in the middle and translucent outside gives a feathered edge. Source:
.
- **Watercolour or charcoal breakup** (his add-on is paid): multiply or overlay a watercolour paper image over the colour, mapped in
  Window space or UV, masked by noise. Plain route inferred from his baked result. Source:
.
- **Painterly warp of any image**: warp its UVs with noise so a photo looks hand-painted. Source:
.
- **Painted transparency**: draw alpha only at hair tips, eyebrow edges and leaf edges so they feel light. Source:
.

## 8. Value rules for painted characters

- Value placement beats the shader. Two characters share one shader and differ only in where the darks sit (eyes, nose, lips,
 under the jaw) and one stroke-strength value.
- Bake the shadows into the design: paint top-down fake shadows under hair clumps, chin, accessories and fringe. Test: lights off,
 grayscale, posterize or threshold. The form must still show.
- Keep face value shapes crisp. Newcomers paint smooth muddy values. Zoom out while painting. Source:
.
- Anime stays sharp and bold. Painterly shifts hue and saturation near cloth edges and uses grunge. Source:
.
- Judge in grayscale against a reference. If yours looks flat, brighten the dark zone. Source:
.
- Sharpen the forms after painting: sharpen the nose, inflate the lip sides in sculpt mode, lower the overall face value so
 highlights pop.
- Flip a screenshot horizontally to find drawing faults.
- Check on a phone at low and full brightness.

## 9. Bake and export

Blender cannot export a shader. Bake it, then rebuild a simple material in the target engine. Sources:
,
.

1. Remove the lighting from the colour chain (keep colours). Bloom and light values above 1 do not export (bake as white), so set
   them to 1 before baking.
2. Plain route: Cycles, Bake panel, Diffuse (Color only) or Emit, and Ambient Occlusion, into a new image per object with the
   target Image Texture node active. Add-on route is paid. Name each bake, or it overwrites.
3. Join objects (Ctrl+J) before texturing if one bake is wanted. Combine bakes in an image editor or UV pack.
4. Engine: image to Emissive Color (Unreal), or an unlit material (see `uv-and-texturing.md`). Alpha through a Mix Shader with
   Transparent BSDF in slot A and the baked image in slot B, blend mode Alpha Blend. Rebuild the Fresnel edge in the engine.
5. FBX export for a rigged toon character: Armature and Mesh, Smoothing = Face, Only Deform Bones on, Animations off, bendy bones
   off. Match the engine focal length to Blender's.

## 10. Compositor finish

- Blender 5.0 has no Use Nodes button: Compositor tab > New, and Render tab > Compositor = Always. Source:
.
- Stack: Glare (Bloom), Soften filter, then Box (or Diamond) Sharpen. Glare adds little and is optional. Sources:
.
- Unify colour: Mix (Color) with one tint. Split tone: Map Range > Color Ramp > Mix for orange highlights and blue shadows.
- Contrast gradient: two-colour Multiply in the compositor.
- Depth of field: Add Empty named "focus" on the subject, camera DoF on, low F-stop. Source:
.

## 11. Paid add-on to plain-node map

Stylized Asset Suite (his add-on, paid Pro with a free base) maps to nodes:

| Add-on effect | Plain route |
|---|---|
| Stylized Light Dynamic, Steps 1 | Diffuse > Shader to RGB > Color Ramp Constant (section 1) |
| Extra light B or G | Colour-coded sun with Separate Color (section 2) |
| Per-object light, circular light | Layer Weight rim, or Empty-driven spherical gradient (sections 2 and 3) |
| Draw and paint single colour | Image Texture mask into a Mix (section 6) |
| Create light mask, bake light | Cycles bake of AO or diffuse as a Mix mask (section 6, 9) |
| Add Object Outline | Solidify shell (section 5) |
| Metallic and Glossy | Painted metal recipe (section 3) |
| Gradient Map | Color Ramp fed from Shader to RGB luminance (standard technique, not shown) |
| Bounce light | Gradient Texture or painted image into a Mix with HSV Value near 3.
