# Lighting, render speed, color, geometry nodes and workflow recipes

Tricks for lighting, Cycles and EEVEE render cost, color management, the compositor, geometry-nodes environments and effects, and workflow habits.
Checked against Blender 5.2: every route below is given in the 5.2 names, and where the video used an older name the old name is
written after "was". An entry marked `(heard)` has no value that was seen on a frame. `untested` marks a route the note only inferred.

<!-- skill-navigation:start -->
## Reading Map

- [Lighting, render speed, color, geometry nodes and workflow recipes](#lighting-render-speed-color-geometry-nodes-and-workflow-recipes)
- [Lighting](#lighting): Light roles and classic setups; Light types, power, Exposure and Normalize; Key to fill ratio, falloff and colour;
  HDRI as fill, not as the light; IES profiles and gobos; Cards and flags; Light Linking and Shadow Linking; Window glass shadow
  off; Aim lights with Track To and Tri-lighting; Negative light power (unverified); Light Groups and
  flicker in post; Night lighting recipe; Cozy interior stack; Soft focus and backlit sun for phone scans
- [Fog and volumes](#fog-and-volumes): Cheaper camera-only volume; Array-sphere fake fog; Camera-parented plane fog; Gradient fake fog in emission;
  Mist pass haze and underwater mix; Light-ray node group and ground fog; Cone light ray; Mesh-to-volume fog with falloff
- [Render speed](#render-speed): Cycles settings checklist; Light Tree; Denoise: passes, OIDN and OptiX; Temporal denoise of an animation;
  Render at 75 percent and upscale; Indirect Only layers and Alpha Over; EEVEE ray tracing and shadows; EEVEE depth of field (legacy)
- [Cheap backgrounds](#cheap-backgrounds): Baked 2D asset with normal map; Distance LOD swap; Camera culling; Mist depth map as displaced plane;
  Camera projection mapping; Decimate, photo cut-outs and flat photo displacement
- [Color and camera](#color-and-camera): AgX, ACES 2.0, Standard and curves; Grade EXRs in Resolve; Compositor glow, streaks and dispersion; Glass look
  from an abstract world texture; Compositor 5.x settings are input sockets; 5.0 presets and Glare Sun Beams; Kuwahara; Vignette
  and Split; Pixelate, Posterize and Lens Distortion; Dolly zoom, Lens Shift and orthographic; Camera shake with a Noise modifier;
  Cinematic camera; Ray Portal BSDF; Looking Glass quilt
- [Geometry nodes](#geometry-nodes): Scatter with masks, exposed controls and wind; Mesh from image alpha; New Array modifier and Curve to Tube;
  Free Normal blend; Mesh Bevel panel cuts; Camera speed lines; Simulation Zone and the sparkler; Automatic plant growth; Books and
  floor planks; Node Tools and tool-style groups; Circle array and stitch generator; Grease Pencil rope; Procedural castle; Gaussian splats
- [Workflow](#workflow): Asset Browser libraries and tools; Simplify and viewport speed; Video Sequencer basics; Hotkey sheet
- [Add-ons](#add-ons)
- [Dropped or covered elsewhere](#dropped-or-covered-elsewhere)
<!-- skill-navigation:end -->

## Lighting

**Light roles and classic setups**: key, fill, rim, background, motivated, and the named film setups.
- Steps: add lights one at a time with all others off. Key: the main light, 25 to 45 degrees off the subject, on the side of the frame that has
  the most space. Fill: opposite the key, always dimmer, a soft Area light. Rim: a Sun or Area behind and slightly high, aimed through the
  edge (this is also what makes fuzz or fur visible: fuzz is invisible without a back light). Background light separates subject from set.
  Motivated: justified by a visible source. Skull example (Blender 2.8 era): Sun rim Strength 10, large Angle; cool cyan Area 500 W behind in top view;
  warm Area 500 W in front scaled by 3 and flipped for soft fill; a Point 50 W below in red to catch the underside. Three-light clay: Sun
  Strength 5, Angle 10 degrees, orange; two crossed Area lights, Power 100 W and a larger warm 250 W, Size 1 m.
  Named setups: three-point, Rembrandt (key about 45 degrees plus a white reflector card opposite), butterfly (light above, card below),
  split (key from the side), under-lighting (spooky), two-point (fill moved back), silhouette (backlit).
- Principle: a light has one job: shape, soften, separate or justify. Cool back with warm front, plus one accent from a third direction.
- Pitfall or use when: all lights the same brightness and plain white gives a sterile render.

**Light types, power, Exposure and Normalize**: what each type is for and which numbers matter.
- Steps: Point: watts, Size (radius) sets shadow softness; small coloured splashes. Sun: only rotation matters; Strength about 10 for a
  bright sun in a Filmic-era scene, Angle 0.5 degrees default; raise Angle to 5 to 15 for soft shadows, 25 for very soft (a very high Angle
  can glitch shadows). Spot: Spot Size and Blend. Area: most used; Shape Square, Rectangle, Disc or Ellipse (shape shows in highlights and eyes); size softens;
  Spread 180 default. Area light Portal: tick it on an Area light placed in a window or wall opening to cut interior noise (needs a World light).
  Mesh emission works for exact shapes but is noisy. Light Properties also has Temperature (Kelvin: tick it beside the Color row, `Light.use_temperature`; it replaces the swatch. Real sources to type: candle about 1800 K, warm household lamp about 2700 K, midday daylight about 5500 K, heard; also use it to match a plate), Exposure and Normalize. Exposure only scales power: right click Exposure > Copy as New Driver, paste on each other light's Exposure,
  and one value dims the whole rig keeping ratios. Normalize off (default): a bigger light is brighter; on: brightness stays, softness still follows size.
  The manual has a power table for real sources and sun strength for clear, cloudy, overcast and moonlight.
- Principle: size sets shadow softness, then power sets brightness; sun strength is a different unit from watts.
- Other tools: three.js DirectionalLight, PointLight, SpotLight, RectAreaLight (no shadows, needs RectAreaLightUniformsLib); Unity and Godot have the same light types.
- Pitfall or use when: Filmic became AgX in 4.0 and the same Sun Strength looks different; judge by the picture.

**Key to fill ratio, falloff and colour**: reading contrast and choosing light colour.
- Steps: inverse square: a light 2 m away gives a quarter of the brightness at 1 m. Ratios: 1:1 flat, 1:2, 1:4 dramatic, 1:8 stylized (frame: key 75 W,
  fill 9.375 W). Colour: complementary colours across the wheel, one set in the background and one in the foreground (blue key against orange and
  red background); warm foreground with cool background. Fire as a yellow-to-orange-to-purple gradient, moon spill in blue, one neutral Area light to bring back original colours.
  Lights slightly behind the subject at a fraction of the fill brightness add depth. Save palette images and view them in the Image editor.
- Principle: shapes read through shadow wrapping the form, not through brightness.

**HDRI as fill, not as the light**: keep reflections and ambience, add your own lights for direction.
- Steps: World Properties > Surface > Color > Environment Texture (equirectangular HDRI, for example from Poly Haven) or Sky Texture; set World Strength to 0.15
  to 0.25 once lights carry the shot (frame: empty warehouse HDRI at 0.150). Sky Texture for a stylised scene: Sun Size 10, Sun Intensity 1.5, then tune
  Elevation and Rotation so the sun hits from the side. Model at real scale because DOF and Area size depend on it.
- Principle: HDRI-only lighting is flat; a low HDRI keeps reflections and fill, creative lights add shape.
- Other tools: three.js HDRLoader (RGBELoader before r180) plus PMREMGenerator into scene.environment.

**IES profiles and gobos (textured lights)**: real bulb falloff, and a pattern cast through a spot.
- Steps: IES: light properties, tick Use Nodes on the light, add an IES Texture node (External, load the .ies file),
  Factor into the Emission Strength (frame: Point 1 W). Gobo: Spot light, Use Nodes: Texture Coordinate UV > Mapping (Location X and Y 0.5, heard) > Image Texture > Emission
  Strength; an Invert Color adds more shadow. Spot plus an animated leaf-shadow texture is a cheap cookie. Physical cookie: an object with holes in front of the light.
- Principle: IES stores measured intensity by angle; a texture on the light's strength casts its pattern.
- Other tools: Unreal IES profiles and light functions; Unity HDRP IES and cookies; three.js SpotLight.map for a cookie, no IES built in; Godot light cookie.
- Pitfall or use when: Cycles only.

**Cards and flags**: subtractive lighting and bounce cards.
- Steps: a large plane with a Principled BSDF in black, Roughness 1, IOR 1, Alpha around 0.43 to set how much it blocks (frame: Alpha 0.428). Put it between
  light and subject to kill a hotspot. Hide it from the camera: Object Properties > Visibility > Ray Visibility, untick Camera. A white card is a reflector bounce.
  A dirt-textured flag in front of a window sun breaks up spill.
- Principle: film flags darken instead of adding lights, which focuses the eye.

**Light Linking and Shadow Linking**: a light affects only chosen objects; a light can be ignored by a caster.
- Steps: select the light, Object Properties > Shading > Light Linking > Collection > New (makes "Light Linking for <light>"), drag objects or collections in;
  the icon toggles Include or Exclude. Shadow Linking is its own sub-panel with its own collection. Shortcut (4.3): select lights, then the object, Ctrl+L > Link Light.
  Put characters in a "Characters" collection and link the back Area light to it so the rim does not hot-spot the set. Eye highlights: Point lights linked only to the eyes.
  Lights inside a glass bottle that do not change the room. Cyclorama trick: a cyc wall with Ray Visibility on Camera only so sun passes through while the camera sees it.
  Pre-4.0 glass trick: Light Path > Ray Depth > Math Less Than (threshold 2) into the Alpha of the glass Principled BSDF.
- Principle: tell the renderer which objects a light touches instead of moving lights.
- Other tools: Unreal Lighting Channels; Unity Light Layers (URP and HDRP); Godot light cull mask.
- Pitfall or use when: Cycles; EEVEE support untested. It was first an experimental Cycles branch in 3.6 and shipped in 4.0.

**Window glass stops blocking sunlight (Cycles)**: pane geometry casts a shadow, so less sun reaches the floor.
- Steps: select the window object, Object Properties > Visibility > Ray Visibility, turn Shadow off. Light passes while the pane stays in place and visible to the camera.
- Principle: shadow rays ignore the object, camera rays still see it.
- Pitfall or use when: interiors lit by a Sun through glass. `Object.visible_shadow` exists in 5.2. Heard, no frame read.

**Aim lights with Track To, and the Tri-lighting extension**: lights that follow a target.
- Steps: select the light, Constraints tab, Add Track To, Target the object (Track Axis -Z, Up Y); the light follows it. Extension "Tri-lighting": Edit > Preferences > Get Extensions, search it; select the object, Shift+A > Light > the entry builds three-point lights with Track To constraints.
- Pitfall or use when: the video also said Shift+T makes a light follow the cursor, unverified.
- Check: `TRACK_TO` and the extension exist (measured 2026-11-08); the add-on's menu path was not run.

**Negative light power (unverified)**: the video says a negative Power removes light from an area in Cycles. Not tested in 5.2 for Cycles or EEVEE.

**Light Groups and flicker in post (Cycles)**: render once, animate one light afterwards.
- Steps: View Layer Properties > Light Groups, add "fire1" and "fire2". For each light: Object Properties > Shading > Light Group (it is under Object, not Light). Render. In
  the Compositor the Render Layers node now has Combined_fire1 and Combined_fire2. Mix node: image, the fire pass second, Factor = the other pass; between them
  a Brightness/Contrast node (Bright 50, Convert Premultiplied on). Keyframe Bright, then Graph Editor > Modifiers > Noise, Strength about 250 for flicker.
- Principle: each light gets its own pass, so you brighten or flicker it without re-rendering the slow image.
- Other tools: Fusion or After Effects can do the same from separate light passes.
- Pitfall or use when: EEVEE also supports light groups in current versions (untested). Source value check: 3.2 introduced them.

**Night lighting recipe**: colour contrast and softness, with faked light where reality would be too dark.
- Steps: no world light at first; add a night HDRI at Strength 1. Add a very large Area light from the moon direction (frame: purple, Power 375000 W, Size 1 m scaled huge for soft shadows).
  A moon that does not glow gets a Point light in front of it. Palette: light blue, cyan, dark blue, purple, a little pink, with one opposite accent in orange. Sun for top fill: blue,
  very high Strength, Angle 25 to 50 degrees (heard). Cookie for clouds: a big plane, Image Texture (grunge) > Color Ramp (crushed) > Principled Alpha, placed in front of the sun.
  Characters get warmer spot lights because the huge soft lights are too weak; torches and lamps are a Point or Spot light parented to the object, power above realistic. Little orange Points scattered around add contrast.
- Principle: night is colour contrast plus soft light; cheat the power.
- Other tools: light cookie in Unreal and Unity; a soft sun is a large area light in any engine.

**Cozy interior stack**: HDRI, window sun, flag, hidden warm practicals, shafts, dust, DOF, grain. (heard, one volume frame)
- Steps: HDRI only for ambient and reflections. Sun behind the window, Angle 5 to 10 degrees. Flag plane with a dirt texture to block spill. Practicals: bright, very warm Point lights hidden and enlarged so there is no harsh
  specular. Shafts: a cylinder fitted to the light with Principled Volume (pale gold, Density 1.0) into Volume output; faster: Emission into Volume with a noise group to break it up. Dust: particles with a small sphere or a geometry-nodes dust.
  Camera: strong soft DOF for a miniature feel, not overdone. Compositor: tiny Glare (Bloom), tiny Lens Distortion dispersion, 35 mm film grain mix.
- Principle: ambient and key first, then warm fill, then atmosphere.
- Pitfall or use when: Principled Volume is slow; EEVEE Next has no Bloom checkbox, use the Glare node.

**Soft focus and backlit sun for phone scans**: hide low-resolution photo scans.
- Steps: camera at 1080x1080, low angle. Camera data > Depth of Field on, Focus Object the subject, F-Stop 1.5 (default 2.8). Sun from behind, Strength about 10, slightly yellow, Angle 5 to 15 (25 for very soft); Area Strength 25 from the side, warm.
- Principle: soft focus hides scan detail loss; warm lights tie the subject to the scan.

## Fog and volumes

**Cheaper camera-only volume**: a real volume without the cost of tracing its bounces.
- Steps: cube around the scene. Principled Volume (Density 0.003, teal) into the Volume input of a Mix Shader; Light Path > Is Camera Ray as the Factor; Transparent BSDF in the other slot.
  Object Properties > Visibility > Ray Visibility: leave only Shadow on. Render Properties > Light Paths: Transmission, Volume and Transparent bounces 2. He measured
  42 s normal, 27.5 s no volume, about 15 percent of the volume cost saved.
- Principle: stop the volume from tracing bounce rays.
- Pitfall or use when: the existing fog entry in environments.md covers the basic Is Camera Ray fog; this adds the bounce and ray-visibility settings.

**Array-sphere fake fog**: translucent shells instead of a volume (adds 2 to 3 s).
- Steps: 3D cursor at the focal point; UV Sphere big enough to contain the camera, Ctrl+1, Shade Smooth, name it. Array modifier: Relative Offset off, Object Offset with an Empty at the cursor; scale the Empty to grow the spheres outward; Count 2. Material: Principled, Specular 0, Roughness high, Alpha 0.05 to 0.1 and a colour.
- Principle: stacked translucent shells accumulate density with distance.
- Pitfall or use when: no light shafts.

**Camera-parented plane fog**: layered translucent planes, camera rays only.
- Steps: select the camera, Shift+S > Cursor to Selected, Shift+A > Plane, R 90 on X, Ctrl+A apply rotation, name it, move it forward, Ctrl+P > Object (Keep Transform) to the camera. Edit mode S 100. Array modifier: Relative Offset off,
  Constant Offset on, Y about 10 m, raise Count. Material Principled, Alpha near 0.05; Noise Texture > Color Ramp > Alpha to break it up. Object Properties > Visibility: untick everything except Camera.
- Principle: density accumulates with distance like fog at a fraction of volume cost.
- Other tools: layered alpha planes are the classic real-time fake fog; three.js FogExp2 or sprites.

**Gradient fake fog in emission**: colour-only atmospheric perspective.
- Steps: on the shared rock or wall material: Texture Coordinate > Mapping (Rotation Z -90) > Gradient Texture (Linear) > Color Ramp (four stops, dark teal to light cyan, Constant interpolation as shown) > Emission. Share the one material across the set.
- Principle: colour depends only on distance along the gradient axis; no volume cost.
- Other tools: a world-space gradient into an unlit colour is trivial in a three.js ShaderMaterial. Untested.
- Pitfall or use when: gradient is in object space; rotate the Mapping to the cave direction.

**Mist pass haze and underwater mix**: depth fog in the compositor, adds about 1 s.
- Steps: View Layer > Passes > Data > Mist (also Z for DOF). World Properties > Mist Pass: Start 5 m, Depth 800 m, Falloff Quadratic for a landscape. Compositor: Mist > Color Ramp (crush it, pull the white end down if too thick) >
  Mix Factor; image in the top slot, fog colour in the bottom slot (Alpha Over below to place a colour behind). Underwater: blue fog colour, optional box with Volume Scatter driven by stretched noise for light streaks, free dust footage in a Mix set to Multiply.
  The pass depends on camera distance, so animate Start and Depth if the camera moves a lot. Measured cost: about 1 s on a 27 s scene.
- Principle: fog is a depth-based composite, so it is cheap and exactly art-directable.
- Other tools: three.js FogExp2 or a depth post pass; Unreal Exponential Height Fog.
- Pitfall or use when: no light shafts. Also covered more briefly in environments.md "Mist pass compositing".

**Light-ray node group and ground fog**: low-density blue volume and streaks from stretched noise.
- Steps: general fog: cube from camera to far sky, Principled Volume, blue, Density 0.002. Ground fog: thin box above the ground, brighter, density from Noise Texture > Color Ramp (small noise for fog-free pockets). Rays group: Mapping (Point, Rotation Y -11.9) > Noise Texture (2D, Roughness 0.5) >
  Color Ramp (RGB, Linear, stop 0.594) > Multiply; second Color Ramp (Ease, stop 0.218) fed by Layer Weight Fresnel (Blend 0.600); Mix (Color, Multiply, Factor 1.0) into Emission Strength.
- Principle: a low-density volume gives depth falloff; stretched noise gives streaks.
- Pitfall or use when: Cycles volumes are noisy; keep density very low.

**Cone light ray**: god rays in one cone object, no scene-wide fog. Eevee and Cycles.
- Steps: new object with a Geometry Nodes group "Light Ray". Cone primitive, Vertices 16; expose Radius Top, Radius Bottom, Depth and rename them Source Radius, End Radius, Length in the group panel. Pivot at the top: Cone > Bounding Box (Use Radius) > Max > Separate XYZ Z > Multiply -1 >
  Combine XYZ Z > Transform Geometry Translation. A Linear Gizmo node each (three; Value into Source Radius, End Radius, Length; End Radius gizmo Position at Z = Length x -1), Joined with the result so they show. Set Material before the Transform.
  Shader: delete the Principled BSDF, Principled Volume into Material Output Volume (turn the world off while working). Texture Coordinate Generated > Separate XYZ; X-0.5 and Y-0.5; Z: 1 minus Z, then Maximum 0.025; X and Y divided by that Z > Combine XYZ >
  Vector Math Multiply (2.2, 2.2, 1) > Noise Texture (4D, W animates, Detail 2, Distortion 0.2) > Color Ramp (white stop at 0.52) > Multiply 0.075 into Density; the same ramp Color times 0.5 into Emission Strength. Ctrl+G the group with Animation, Scale, Color, Emission Strength inputs.
  Optional falloff: Gradient Texture Linear from Generated Z > Color Ramp > Mix (Multiply).
- Principle: dividing X and Y by Z squeezes the noise to a point at the top and stretches it down the cone, a perspective of one noise field.
- Other tools: cone mesh with a custom additive shader in three.js or Unreal. Untested.
- Related: a cheaper cone with no volume at all (stretched cylinder, emission and faded alpha, Layer Weight edge fade) is "Fake god rays with a cone card" in `environments.md`; it was rebuilt in EEVEE 5.2.2.
- Pitfall or use when: Emission colour overrides base colour unless both are linked.

**Mesh-to-volume fog with falloff**: ground fog Blender's world lacks.
- Steps: a Fog_GN object with a Geometry Nodes modifier. Chain: Object Info (Relative) of the objects in a Fog Object collection > Mesh to Volume (Resolution: Amount, Density 2, Voxel Amount 64, Exterior Band 0.1, Interior Band 0.2, Fill Volume on) > Set Material. Modifier inputs: Density 0.030, Noise Amount 1, Noise Contrast Min 0.25, Max 1,
  Linear Falloff, Spherical Falloff. Spherical: scale an Empty to the fade radius. Gradient: Spherical 0, raise Linear Falloff along a gradient Empty.
- Principle: mesh to volume gives a cheap fog box; Empties give falloff positions.
- Pitfall or use when: spherical radius at max hides the fog until the control Empty is scaled. Part of a paid pack (see Add-ons).

## Render speed

**Cycles settings checklist**: stop paying for rays and polygons that do not change the picture.
- Steps: Sampling: Noise Threshold 0.01, Max Samples 1000, Denoise on (render OpenImageDenoise, viewport OptiX or OpenImageDenoise), Albedo and Normal passes. Light Paths: Max Bounces 12 to 8, Transmission, Volume and Transparent to 0 or 2 where unused; Filter Glossy up and Clamping for fireflies; Fast GI approximation (about 20 percent).
  Subdivision: Dicing Rate Render 1.0 px, Viewport 8 px. Performance: Persistent Data on for animation. Textures: 4K only on near or large objects, 1K to 2K elsewhere. Emissive meshes are noisy, use real lights, or a Light Path mix factor to look emissive without emitting.
  Ray Visibility off on unseen paths. Convex Hull (Edit Mode, Mesh > Convex Hull) for collision. Decimate or Multires on backgrounds; bump instead of displacement (Material Settings: Bump Only). Save to OpenEXR or TIFF.
  Vector Blur instead of motion blur: View Layer Z and Vector passes; Compositor Render Layers Depth > Vector Blur Z and Vector > Speed. Defocus node with the depth pass for DOF. Simplify: max subdivision, texture limit 1024, camera and distance culling.
  Adaptive Subdivision with a displacement map (Feature Set Experimental in older builds) instead of sculpting millions of faces. Measure Experimental, tiles and Z pass again in 5.2: tile size has been automatic since 3.0, and the Z pass is now Depth.
- Principle: light paths and memory are the two cost centres; push blur, DOF and fog to the compositor.
- Pitfall or use when: Fast GI and Filter Glossy trade accuracy; Persistent Data uses more VRAM. Frame values beat transcript values: one video said Noise Threshold 0.1 while the panel showed 0.0100.

**Light Tree**: less noise at the same samples when a scene has many lights.
- Steps: Render Properties > Sampling > Render > Lights > Light Tree (Light Threshold 0.01). On by default since 3.5. Compare with Render Slots in the Image Editor. Big many-light scene: 1000 samples 20 s, Light Tree at 1000 samples 15 s, at 600 samples 10 s with the same noise.
- Principle: the tree picks the most important lights per shading point.
- Pitfall or use when: a single character gains little (10 to 15 percent more time per sample); forests with volumetrics, heavy HDRI and glossy sheen got more fireflies, so lower indirect, raise Filter Glossy or switch it off there.

**Denoise: passes, OIDN and OptiX**: render at low samples and keep edge detail.
- Steps: Render Properties > Sampling > Render > Denoise on; Denoiser OpenImageDenoise or OptiX (RTX only); Passes Albedo and Normal (old name: View Layer Denoising Data plus a compositor Denoise node with Image, Albedo, Normal wired; 10 samples took 14 s against 5 min 22 s at 500). Adaptive Sampling is on by default. Viewport denoise OptiX.
- Principle: the denoiser reads albedo and normals as guides so it does not smear edges.
- Pitfall or use when: soft on straight edges, bubbling when animated, not for blown-up stills.

**Temporal denoise of an animation**: removes per-frame noise boiling so lower samples work.
- Steps: Preferences > Interface > Developer Extras on. Cycles, Device GPU Compute, Denoise OptiX with Albedo and Normal. Output: OpenEXR MultiLayer, Color Depth Float (Full), Codec ZIP, Color Management Override sRGB. View Layer > Passes: Combined, Vector, Denoising Data. Render the EXRs, then F3 > "Denoise Animation"
  (cycles.denoise_animation). The screen freezes and the EXRs are overwritten. To PNG: Compositing, an Image node loading the EXR sequence, output PNG, Ctrl+F12.
- Principle: a window of frames is denoised together, so the pattern is consistent across frames.
- Other tools: Resolve Studio temporal noise reduction node; Neat Video on the same EXRs.
- Pitfall or use when: needs an NVIDIA card (OptiX); verify the operator still shows in F3 in 5.2 before relying on it.

**Render at 75 percent and upscale**: 20 s to 13.5 s at 1000 samples on an RTX 4090.
- Steps: scene named Scene_75%; New Scene > Linked Copy named Scene_100%. In Scene_75% set Format % 75 and render. In Scene_100%: Compositor with Render Layers pointing to Scene_75%; Scale node (Render Size, Stretch); Filter node Box Sharpen (or Diamond) Fac about 0.1 (frame 0.093). Export from Scene_100%.
- Principle: a 20 to 25 percent cut is hard to see after upscale and platform compression; a light sharpen restores detail.
- Pitfall or use when: heavy sharpening gives halos. The compositor node tree is made from the Compositor panel in 5.x (no Use Nodes checkbox); verify the click path.

**Indirect Only layers and Alpha Over**: cut memory by moving heavy far objects into a separate layer.
- Steps: put hills or a forest in its own collection; Outliner filter > enable the Indirect Only toggle on it (or View Layer > Filter > Indirect Only). It keeps its shadows and bounce on the rest but hides from camera. Render each layer, then Alpha Over in the Compositor.
  Baked-plane version: import each rendered layer as a plane (Images as Planes) and offset the planes in depth so DOF and parallax read.
- Principle: indirect-only keeps the object's light on the scene while the picture comes from a cheap plane.
- Pitfall or use when: foreground the camera passes must stay 3D; planes must differ in depth.

**EEVEE ray tracing and shadows (EEVEE Next)**: better GI and reflections, shadow control.
- Steps: Render properties > Raytracing on, Method Screen-Trace, Resolution 1:1 (1:16 is one sixteenth of the resolution), Precision 1; Denoising on; Fast GI Approximation: Resolution 1:1, Rays 12, Steps 16 (heard). Shadows: raise Rays (max 4) and Steps (max 16), resolution; Light > Shadow Jitter plus Overblur. Light > Influence sliders (Diffuse, Glossy, Transmission, Volume Scatter): Glossy 0.5, Diffuse 0.75 softens a backlight on a normal-mapped character.
- Principle: resolution fraction is a divisor; Influence sliders cheat energy per light for art control.
- Pitfall or use when: Fast GI cost grows with rays and steps. To use Cycles lighting in EEVEE, bake it to textures (Simple Bake, see Add-ons) and keep dynamic lights only on the animated character.

**EEVEE depth of field (legacy, 2.93)**: where the old bokeh sliders were. Not applicable as written to EEVEE Next.
- Steps: Camera data > Depth of Field (Focus on Object, F-Stop 2.4, Focal Length 85 mm). Render tab > Depth of Field: Max Size 67 px, Sprite Threshold (higher means more highlight sprites, slower), Neighbor Rejection (lower is better), Denoise Amount (0.75 to 1.0), High Quality Slight Defocus, Jitter Camera, Over-blur.
  In 4.2 and later DOF follows the camera aperture and these sliders are gone (untested in the app).

## Cheap backgrounds

**Baked 2D asset with a normal map**: a flat cut-out that still reacts to light.
- Steps: orthographic camera, flat grey world. Render with Film > Transparent, save as base colour. Switch the engine to Workbench, Lighting MatCap, pick the Normal matcap, F12, save as the normal map. File > Import > Images as Planes for both; set the normal image Color Space Non-Color; Image Color > Normal Map > Principled Normal; raise Roughness, add a light. (heard)
- Principle: a camera-space normals matcap render is a screen-space normal map.
- Other tools: three.js MeshStandardMaterial with map plus normalMap on a billboard plane.
- Pitfall or use when: only valid while the plane faces the camera; pair with the LOD face-camera rotation. Works for trees, clouds, hills, dust, stock-footage steam.

**Distance LOD swap (3D near, 2D far)**: geometry nodes pick the tree version by camera distance.
- Steps: Distribute Points on Faces (Poisson Disk, Distance Min 0, Density Max 1.0, Factor 0.25). Instance on Points twice ("3D Tree", "2D Tree" from Object Info, Original), both Joined with the ground. LOD: Active Camera > Object Info Location minus Position (Vector Math Subtract) > Length > Multiply -1 > Add 19.1 (the switch distance in metres, scene specific) into the 3D Selection; the same value times -1 into the 2D Selection.
  Face camera: camera location minus Position > Vector Math Multiply (1, 1, 0) > Align Rotation to Vector (was Align Euler to Vector; Axis Y, Factor 1.0) into the 2D instance Rotation.
- Principle: distance becomes a float used as a boolean selection; Multiply (1,1,0) keeps cards upright.
- Other tools: THREE.LOD, Unity LOD Group, Unreal LOD, Godot visibility ranges.
- Pitfall or use when: single-camera shots only.

**Camera culling**: skip what the camera cannot see.
- Steps: Cycles: Render properties > Simplify > Culling > Camera Culling on, Distance about 0.1 so edge shadows do not pop; per object Object properties > Visibility > Culling > Use Camera Cull (Alt-tick to set on all selected). Only shows in Rendered shading. (heard)
  For heavy geometry-node forests: a node group "CULLING" with a Boolean output feeds the Selection of every Instance on Points; inside it raycasts to a plane in front of the camera (setup from a Polycount tutorial; inner nodes not seen).
- Principle: instances that hit the camera frustum plane stay, the rest are deleted.
- Pitfall or use when: Camera Culling does not help dense geometry-node systems; unverified in 5.2.

**Mist depth map as a displaced plane**: a rendered background re-used with real parallax; no denoise shimmer.
- Steps: View Layer > Passes > Data: Combined, Z, Mist, Denoising Data; render a still. Compositor: Mist > Normalize > Viewer or File Output; save colour and depth. New scene: Plane subdivided about 120 times. Material: colour into Emission; depth image > Color Ramp > Invert > Displacement (Midlevel 0.5, Scale 1, Object Space) > Material Output Displacement.
  Material Settings > Displacement = Displacement and Bump. Subdivision Surface modifier: Simple, tick Adaptive Subdivision (Dicing Scale 1.0).
- Principle: camera depth drives displacement, so a flat render gets parallax for small camera moves.
- Other tools: three.js displacementMap on a dense plane. Untested.
- Pitfall or use when: breaks with large camera moves; adaptive subdivision may sit elsewhere in 5.2, check the manual.

**Camera projection mapping**: rough 3D set from one image, camera can move.
- Steps: Camera data > Background Images, add the image, match render resolution. Through the camera (Numpad 0), block in a ground plane, back wall and boxes over the buildings, rotated slightly on X. Ctrl+J into one object, Edit Mode, A, U > Project From View. Material: Image Texture (same image, Extension Clip) > Base Color, via Texture Coordinate UV > Mapping. Tweak UVs. DOF with a focus object.
- Principle: UVs projected from the camera re-project the photo exactly; a nearby camera sees the geometry's parallax.
- Other tools: projective texture or camera projection in Fusion, Nuke, Unreal decals. Untested.
- Pitfall or use when: stretching at grazing angles.

**Decimate, photo cut-outs and flat photo displacement**: smaller backgrounds.
- Steps: Decimate: Ctrl+J all tree pieces, Decimate Collapse Ratio 0.25, apply, repeat (fewer crashes); hide leaf planes first. Photo cut-out: Images as Planes, Edit Mode, Knife (K) around windows and doors, extrude the parts. Flat photo displacement: depth map (Photoshop Neural Filters, or a free web depth tool), Image Texture > Base Color, depth > Displacement,
  Subdivision with Adaptive Subdivision Simple. (heard for the last two)
- Principle: the photo carries detail, geometry only needs big depth steps.
- Pitfall or use when: background only.

## Color and camera

**AgX, ACES 2.0, Standard and curves**: choose a view transform and fix a washed-out look.
- Steps: Render Properties > Color Management > View Transform: Standard, AgX (replaced Filmic in 4.0), ACES 2.0 (new in 5.0). Working Space defaults to Linear Rec.709 (also Rec.2020, ACES); change it only at the start of a file. ACES is darker: Exposure about 0.75, tick Curves, drag the white point left, add a shadow point pulled down for contrast;
  on the Blue channel add a midtone point pushed up to put blue in green water. Looks (Punchy, High Contrast in AgX, 4.2+) replace the old Filmic "Medium High Contrast". Test with a spectrum-to-white ramp plus a very bright emissive tube.
- Principle: flat grey images are log-like data, not a bug; fix it with exposure and contrast at the grade.
- Other tools: three.js `renderer.toneMapping = THREE.AgXToneMapping`; Unreal and Godot ACES or AgX variants.
- Pitfall or use when: Standard blows highlights out to cyan; compare views on a test ramp.

**Grade EXRs in Resolve**: when Blender's compositor is too technical.
- Steps: render OpenEXR, import to Resolve's Color page, add LUTs (frame: eight nodes, Film Look Creator Contrast 1.25, Highlights 0.35, Fade 0.285, Subtractive Sat 1.2, RGB Mixer, a custom curve).
- Principle: grade on wide-gamut data, not baked 8-bit. Fusion is the free compositing alternative.

**Compositor glow, streaks and dispersion**: bloom, star streaks and fringe in post (EEVEE Next has no Bloom checkbox).
- Steps: Glare node Bloom (Quality High; older "Fog Glow": Mix 0, Threshold 5, Size 8) for a mug or glass; Streaks (4 streaks, Strength about 0.54, Iterations 3, Angle Offset 45, Fade 0.9, Threshold 5 so only highlights bloom). Lens Distortion with Projector on, Distortion 0, Dispersion 0.015 (subtle) to 0.15 (strong). Alpha Over with black on top for a logo on black.
  Tear or highlight element: its own collection and View Layer (other layer set to Holdout or Indirect Only), two Render Layers nodes, Mix Add Factor 1.0, Glare Streaks High Iterations 5 Color Modulation 0.25, add the result back, Lens Distortion, Composite.
  Compositor Glare was reworked in 5.0 and has no Use Nodes checkbox: adapt names, untested.
- Principle: render the highlight element alone and bloom it independently; dark gaps between highlights make glass look expensive.
- Other tools: three.js UnrealBloomPass plus a chromatic aberration shader; Fusion Glow and Lens Distort.

**Glass look from an abstract world texture**: colourful liquid-metal images light a glass logo.
- Steps: World > Environment Texture with the abstract image, Background Strength 3.0 ("two or three"); Film > Transparent on and hide the background; Shader editor World, Ctrl+T (Node Wrangler) adds Texture Coordinate and Mapping; rotate Mapping Z until there is a little darkness with highlights at the side. Pair with the glare entry above and a High Contrast look.
- Principle: glass shows what is around it, so the environment is the look.
- Pitfall or use when: the position is very particular; scroll the rotation.

**Compositor 5.x: settings are input sockets**: read before scripting any effect node below.
- Steps: in 5.x Glare, Pixelate, Posterize, Lens Distortion, Kuwahara, Blur, Ellipse Mask and Split have no node properties for their settings; set `node.inputs['Size'].default_value` and the like. Measured defaults (5.2.2): Glare Type Streaks, Quality Medium, Threshold 1.0, Smoothness 0.1, Strength 1.0, Saturation 1.0, Size 0.5, Streaks 4, Streaks Angle 0, Iterations 3. Pixelate Size 1. Posterize Steps 8. Lens Distortion Type Radial, Distortion 0, Dispersion 0, Jitter off, Fit off. Kuwahara Size 6, Type Anisotropic, Uniformity 4, Sharpness 1.0, Eccentricity 1.0, High Precision off. Blur Size is a 2D pixel socket, Type Gaussian. Ellipse Mask Operation Add, with Position, Size, Rotation sockets. Split Position, Rotation 45 degrees, two Image inputs. The old Mix RGB is the Mix node (Blend Type Multiply); the old output node is Group Output. Viewport preview: Shading popover > Compositor: Disabled, Camera or Always.
- Pitfall or use when: names heard from the video, values measured by probing 5.2; the visuals below were not all rebuilt.

**Blender 5.0 compositor presets and Glare Sun Beams**: node-group presets and shafts from bright areas.
- Steps: in the Compositor add the bundled preset node groups (Sensor Noise for a retro look, Vignette, Tune Image: contrast, colour boost, clarity, detail, sharpen), connect and adjust. Glare node Type Sun Beams (the enum name; "Sunbeams" is rejected in 5.2).
- Pitfall or use when: the names exist in the 5.2 bundled node-group list and Sun Beams was set in 5.2 bpy; not rendered.

**Painterly look with Kuwahara**: oil strokes from a render.
- Steps: Kuwahara, Type Anisotropic, Size about 10 (20 looser). Classic gives square dabs. Sharpness up crisps edges; Eccentricity sets stroke length (0 is blobby); raise Uniformity until it stops changing.
- Pitfall or use when: Anisotropic is slow in the viewport. Heard; defaults measured in 5.2 (above). For more painterly looks see `stylized-shading-recipes.md`.

**Vignette from three nodes, with a before and after split**: darker edges.
- Steps: Mix node (Blend Type Multiply, Factor about 0.8), Ellipse Mask (size nearly fills the frame, position on the subject) into the second input, Blur (Size 100 x 100) between mask and Mix. Before and after: Split node, Render Layers Image in the first input, the vignette in the second; remove it before the final render. M mutes a node (Mix passes the first image).
- Pitfall or use when: heard, names verified in 5.2.

**Pixel art with flat colour bands, and lens distortion looks**: two cheap post effects.
- Steps: Pixelate (Size about 12) then Posterize (Steps 4, or 2 for few colours); muting Pixelate leaves a cel-shaded look. Lens Distortion: Distortion 0.3 for barrel (tick Fit to remove black corners), negative pinches; Dispersion 0.1 for subtle fringes, 0.5 for a glitch; Type Horizontal for a VHS colour shift, Radial is the default.
- Pitfall or use when: heard. A subtler dispersion range (0.015 to 0.15) is in the glow entry above.

**Dolly zoom, Lens Shift and orthographic cameras**: three lens tricks, all keyframable.
- Steps: Dolly zoom: Focal Length 50 mm, subject framed. Frame 1: hover Location and press I, hover Focal Length and press I. Frame 120: G Z Z pulls the camera back along its axis until the subject is clearly smaller, raise Focal Length until the subject size matches frame 1 (compare its top and bottom edges), key both again, then adjust the last focal value and re-key if it drifts. Lens Shift: level the camera (X rotation 90, Y and Z 0) and raise Camera Data > Lens > Shift Y until building tops return to frame, with no converging verticals. Orthographic: Camera Data > Type Orthographic; Orthographic Scale sets the framing (lower is tighter) and moving the camera along its axis does not change the size, which suits diagrams.
- Pitfall or use when: heard; `Camera.lens`, `shift_y` and `ortho_scale` exist in 5.2. A different dolly zoom (pivot scale) is in `animation-and-nla.md`.

**Camera shake with a Noise modifier**: handheld feel without a plug-in.
- Steps: select the camera, Numpad 0, Graph Editor, click the X Euler Rotation curve (one key is enough), Ctrl+Shift+M > Noise. N > Modifiers: Strength 0.1 (the default 1.0 is wild: it is radians), Scale 5. Add a Noise to Z Euler Rotation too with Phase 2 (a different seed); later 0.05 for subtler. Settings are live. Each axis needs its own modifier; the panel shows only the active curve.
- Pitfall or use when: Noise defaults in 5.2 are Strength 1.0, Scale 1.0, Phase 1.0 (measured). Heard.

**Cinematic camera**: shot types, lens, DOF, handheld.
- Steps: Camera data > Lens Focal Length (35 to 50 mm eye-like; wide exaggerates, long flattens), Depth of Field with F-Stop (lower is blurrier; low f-stop on a small subject gives a toy look), Viewport Overlays > Guides > Composition Guides > Rule of Thirds. Handheld: a Noise modifier on the camera location and rotation F-curves. Shot names: cowboy mid-thigh up, medium from the waist, close-up chest up, extreme close-up neck up. Canted is wrong or surreal, low angle power, high angle weak, 180 degree rule.
  Keep real scale so DOF reads. Camera at f 0.3 and 125 mm on a flame shows how extreme DOF looks (light groups video).
- Principle: shot size and lens set space and feeling.
- Other tools: three.js PerspectiveCamera fov from focal length, BokehPass for DOF.

**Ray Portal BSDF (Cycles)**: a plane that shows a room elsewhere in the scene.
- Steps: plane, replace Principled with Ray Portal BSDF (Color, Position, Direction). Position: Texture Coordinate (Object) > Mapping (Point) > Position. Direction (from CG Matter): UV Map > Tangent; Geometry Normal and Incoming; Cross Product(Normal, Tangent); Incoming > Vector Math Scale -1; three Dot Products of the scaled vector with Tangent, Cross, Normal in X, Y, Z order > Combine XYZ > Direction.
  Room: a cube 1 m below, inset the top face and extrude inward. More portals: duplicate plane and cube 5 m on X, new material, offset its Mapping by 5 on X. Four planes at 90 degrees form a cube you can see into; keep plane scale 1.
- Principle: the shader rewrites ray origin and direction as if the plane were elsewhere.
- Other tools: render-to-texture portal camera or stencil buffer portal; parallax interior cubemap for single rooms.
- Pitfall or use when: Cycles only; rotation can glitch.

**Looking Glass quilt**: render for a hologram display.
- Steps: install and enable the Looking Glass add-on from their GitHub; sidebar Camera Setup: pick camera, clip start and end, focal plane on the subject; Quilt Setup: device and quilt (2k Quilt, 32 Views shown; 48, 88, 91, 180 also); Render Quilt or Render Animation Quilt; drag the quilt into the Looking Glass software.

## Geometry nodes

**Scatter with masks, exposed controls and wind**: one ground plane, several instance systems, controls in the modifier panel.
- Steps (5.2 route; the 2.92 video used Point Distribute and Point Instance on a Point Cloud object, replaced in 3.0): Geometry Nodes modifier on Ground. Group Input Geometry > Distribute Points on Faces (Random: Density 125 for grass; Poisson Disk with Distance Min for rocks, Density Max about 0.15) > Instance on Points; Instance from Collection Info (Separate Children and Reset Children on) with Pick Instance on, or Object Info for one asset.
  Rotation: Random Value Float Min 0.15 Max 0.75 into Rotate Instances (grass: only Z, tiny tilt 1). Scale: Random Value Min 0.3 Max 0.6 (rocks 0.1 to 1, flowers about 0.35, Density 0.25). Join Geometry with the ground. Grass density needs big numbers: a Math Multiply 50 after Density.
  Wind: Noise Texture 3D (Scale 1, Detail 0) added to Position (Vector Math Add), Subtract and Math Add 0.5 to lessen it; a Value node with `#frame` > Multiply (1 on, 0 off) > Divide (24 windy, 48 subtler) > into the noise Position. Today a Scene Time node can replace the `#frame` driver (inferred, untested).
  Make it a preset: drag each value onto Group Input and name it in the group Interface panel: Grass Collection, Selection, Scale Min and Max, Rotate Min and Max, Animation (0 to 1), Animation Speed (default 48, min 0, max 10000). Mask: a vertex group named Veg (case sensitive) on Ground, painted weights, into the Selection or Density Factor; clear zones get weight 0.
  Ctrl+A apply rotation and scale on every source object first or instances sit tilted.
- Principle: distribute points, give them random scale and rotation, instance an object on each point; every random range is a modifier input.
- Other tools: three.js InstancedMesh with a density mask texture; Unity and Unreal foliage tools, Unreal PCG; Godot MultiMeshInstance3D.
- Pitfall or use when: a higher Animation Speed number means slower wind. Poisson Disk stops overlapping rocks. Legacy alternative: a Hair particle system with Render As Object (Scale 0.05, Scale Randomness 0.5, Rotation on, Phase 1) is quick but legacy. Scatter on Surface painterly grass is in environments.md.

**Mesh from image alpha**: turn an alpha-cut leaf into low-poly geometry.
- Steps: Image > Mesh Plane with the leaf PNG. New Geometry Nodes modifier: Image Texture with the leaf, Vector from a Group Input Vector (pick the UV map in the modifier panel). Group Input Geometry > Subdivide Mesh (Level 9) > Delete Geometry (Point, All) with Selection from the image Alpha through Map Range (To Min and To Max flipped). Apply (about 183k verts), Decimate Ratio 0.01,
  Proportional Editing and G Z to curve it, Decimate again, Solidify for thickness.
- Principle: delete the transparent points of a dense grid, then decimate to a clean outline.

**New Array modifier and Curve to Tube**: gizmo-driven replacements for Array and curve bevel.
- Steps: Add Modifier > Generate > Array (the old one is Array (Legacy)): shape Line, Circle, Curve or Transform. Circle example: Count Method Distance, Angular Distance 34.7, Central Axis Z, Sweep Angle 90, Radius 3.12 m, Realize Instances on, Align Rotation. Randomize Transform is its own modifier that works on instances above it (flip doubles variety from 5 planks). Instance on Elements instances on points, edges, faces or corners.
  Generate > Curve to Tube: Scale 0.08 m, Profile Round, Resolution 8, Shade Smooth, Resample Evaluated, Caps on, UV Map on so a fabric material follows the tube; Custom profile uses another curve.
- Principle: the old logic is now a node group with exposed controls, so downstream modifiers can chain.

**Free Normal blend (Set Mesh Normal)**: weld a part onto a surface visually, no remesh.
- Steps: Geometry Nodes modifier on the part, group "Free Normal". Normal (this object) into Mix A (Vector, Uniform, Clamp Factor on). Object Info (Relative, the target) Geometry into Sample Nearest Surface (Vector) with a Normal node as Value, into Mix B. Set Mesh Normal on the geometry line: mode Free, domain Face Corner, Custom Normal from the Mix result.
  Limit to the seam: Geometry Proximity (target Faces) Distance into Map Range (Clamp) Result into Mix Factor; lower From Max (about 0.25) until only the seam blends. Optional: a Shrinkwrap modifier (Nearest Surface Point, On Surface, Offset 0) with a vertex group. Smooth by Angle (60 degrees) after it.
  Make a tool: drag the target object and From Max into Group Input (named Object, Distance), mark the group as an asset (Outliner > Blender File > Node Groups), catalog Utility, then Add Modifier > Utility > Free Normal.
- Principle: only shading normals blend across the seam, so the objects read as one shape.
- Other tools: bake a blended normal map in any DCC. Untested.
- Pitfall or use when: a mixed span breaks shading until Map Range limits the area. Blender 4.5 route, unchanged as far as known.

**Mesh Bevel panel cuts (5.2)**: a box with sharp edges becomes a panelled box from one modifier. The old way was Edge Split, Solidify and Bevel modifiers.
- Steps: box with sharp edges marked (right click > Mark Sharp); Matcap, Cavity and Outline on. Split to Instances (domain Face) with Group ID from Named Attribute sharp_edge through Edges to Face Groups. For Each Element zone (domain Instance): Extrude Mesh (Individual Faces off, Offset 0.009 times -1), Join with Flip Faces of the original, Flip Faces again after the zone; check the Face Orientation overlay.
  Merge by Distance (very small). Mesh Bevel: one Bevel Amount socket on all four offsets (0.01 m), Segments 3, Selection = Edge Angle Unsigned Angle Compare Greater Than a group input Bevel Angle (subtype Angle, 30 degrees). Finish with Shade Auto Smooth (Smooth by Angle 60, Ignore Sharpness). Modifier panel: Thickness 0.009, Bevel Amount 0.01, Segments 3, Bevel Angle 30.
  Mesh Bevel node settings: Selection, domain Edges, start and end offsets, Miter, Spread, Segments, Shape 0.5, Profile curve input, output Selections.
- Principle: splitting into shells and extruding gives seams a bevel can round.
- Pitfall or use when: without Merge by Distance the bevel pokes through. Export to GLB afterwards for other engines.

**Camera speed lines**: a ring of spikes that rotate and jitter, parented to the camera.
- Steps: plane with group "3D Speed Lines". Curve Circle (Resolution 32, Radius 1) > Transform Geometry (Scale 2) > Resample Curve Count 12. Spike: Curve Circle Resolution 3 > Set Position Offset X 0.5 (origin moves to a tip) > Transform Geometry. Instance on Points on the ring with the spike; Rotate Instances (Local Space) with Align Rotation to Vector (was Align Euler to Vector, axis X, Normal).
  Scale from two Random Value nodes into Combine XYZ (Y min 0.25, Z 1, never 0). Motion: Realize Instances > Transform Geometry, rotation Z from Scene Time Frame through Combine XYZ. Fill the mesh. Set Material (Emission strength 1) inside the group. Parent to the camera.
- Principle: instances on a ring, each stretched randomly, rotated by time.
- Other tools: a particle ring of stretched quads in three.js, Unity VFX Graph or Niagara. Untested.

**Simulation Zone and the sparkler**: per-point state across frames.
- Steps: Simulation Zone with Group Input Geometry into Simulation Input, out to Output. The cube vanishes at frame 1 until cached: Properties > Physics > Simulation Nodes > Bake. Sparkler: Plane, group "Spark Nodes". Emitter: an Empty, Object Info Location into Set Position Offset; Distribute Points on Faces (Density 10, Random) with Scene Time Frame into Seed so points change every frame.
  Inside the zone: Join Geometry; Store Named Attribute age (Integer, Point) = Named Attribute age plus 1. Velocity: Set Position with Offset = Named Attribute velocity + Random Value (Vector, symmetric) scaled about 0.37; store velocity; add a downward vector scaled about -0.098 for gravity. After the zone: Delete Geometry with Selection = age Greater Than 15.
  Shape: Instance on Points with Curve Line > Set Curve Radius (Spline Parameter Factor taper) > Curve to Mesh (Profile Curve Circle Resolution 8, Radius 0.002). Rotation aligned to velocity: Align Rotation to Vector (was Align Euler to Vector, axis Z) with the stored velocity. Material: Set Material, Emission strength 120; Attribute (Instancer, age) > Map Range (From Max 15) > Color Ramp white, yellow, orange, red.
- Principle: store per-point attributes (age, velocity) in the sim so shader and shape read them later.
- Other tools: GPU particles with age curves (Unity VFX Graph, Niagara, three.js).
- Pitfall or use when: delete old points or the count grows. EEVEE Next has no Bloom checkbox: use Glare in the compositor.

**Automatic plant growth**: a curve becomes a stem that grows, carries a collection along it, bounces and unfolds. Frame values from Blender 5.2.
- Steps: Bezier curve with a Geometry Nodes modifier "Automated_Plant". Timing: Scene Time Frame > Subtract Start Frame > Divide (Clamp) by Maximum(Duration, 1) > Map Range Smooth Step = progress 0 to 1. Travel and scale: progress times End Progress and Object Scale through two Switch nodes on one Auto Animate boolean (false = manual Progress and Object Scale); plug the second switch into the existing Auto Animate socket.
  Bounce: (travel duration minus elapsed) / Maximum(Bounce Duration, 1) x 3 bounces; Floor and Fraction in parallel; Fraction > Map Range Smooth Step; Floor + that > Add > Divide by 3 > Float Curve > Multiply Add (Multiplier Bounce Strength, Addend 1) > Multiply with progress.
  Stem: Separate Components > Curve > Trim Curve (Factor, End = progress) > Switch Grow Stem; Curve to Mesh (Profile Curve Circle Resolution 24, Radius Thickness; Scale from Spline Parameter Factor times Taper, one minus), Fill Caps, Shade Smooth. Place objects: Collection Info > Instance on Points; Sample Curve (Factor = progress) Position > Points (Count 1); Tangent > Align Rotation to Vector (Z). Unfold: Rotate Instances with Starting Fold Rotation scaled by one minus progress.
  Stacking: a Boolean attribute "stem created" read with Named Attribute, Sample Index, Switch, written with Store Named Attribute, Set Curve Radius 0.005 on the built stem, Join Geometry; a second Automated_Plant modifier then adds another object. Final values: Start Frame 0, Duration 24, End Progress 1, Object Scale 0.25, Bounce Duration 36, Bounce Strength 0.15, Taper 1, Thickness 0.07 m, Starting Fold Rotation X -90.
- Principle: all motion is a function of Scene Time; one 0 to 1 progress drives trim, position, scale and rotation; the bounce is a repeating ramp shaped by a curve. Auto Animate off lets you keyframe the same sockets.
- Other tools: three.js time uniform with smoothstep, floor and fract; TubeGeometry drawRange for growth. Untested.
- Pitfall or use when: default Stem Length 1 or the stem vanishes when Grow Stem is off; the narration said Maximum while the frame shows Minimum, so check the node on screen.

**Books and floor planks**: fill a line or a floor with instanced models.
- Steps: shelves (group "Bookcase.Generator"): curve > Curve Length and Curve to Points (Count). Object Info of one book > Bounding Box (Use Radius) > Subtract > Separate XYZ X = width; Count = Curve Length / width. Collection Info (Separate Children on, Reset Children off) into Instance on Points (Pick Instance); Align Rotation to Vector (Y) plus Random Value rotation Max (0.06, 0.04, 0.1); Scale Random Min (1,1,0.65) Max (1,1,1).
  Then Realize Instances > Convert to Mesh, delete some books, tilt others, leave gaps. Floor planks (group "Floor.Generator"): three Curve Line > Curve to Points rows with offsets (first row Set Position Offset X 0.125, Y 0.05); Instance on Points > Realize Instances > Instance on Points with a plank collection (Pick Instance) > Random Value rotation -0.025 to 0.025 > Translate Instances Max Z 0.002.
- Principle: same-width items fill a line by width divide; offset rows and slight tilt show real depth without displacement.
- Pitfall or use when: shelves need all books the same width; a plank floor reached 1.0 million verts.

**Node Tools and tool-style groups**: your own operators and modifiers without Python.
- Steps: Geometry Node Editor, change the editor type from Modifier to Tool, New, name it; in the group sidebar tick Tool. Add a node (Extrude Mesh); in Edit Mode a tool button appears and acts destructively. Expose parameters on Group Input. To put it in a menu: mark the group as an asset (Blender File > Node Groups), assign a catalog; save in a folder registered in Preferences > File Paths > Asset Libraries.
  A group can be both modifier and tool (tick Modifier too).
- Principle: Tool mode runs once on active data like an operator; Modifier mode runs live.
- Other tools: closest are Houdini digital assets or Unity editor scripts. Untested.
- Pitfall or use when: Edit Mode tools are destructive; Ctrl+Z. Frames from the 4.0 beta; tools have grown since.

**Circle array and stitch generator**: two small reusable groups.
- Steps: circle array: Mesh Circle (Vertices = Amount, Radius, Fill Type None) > Instance on Points (Points); Group Input Geometry into Instance; Normal > Align Rotation to Vector (was Align Euler to Vector, X axis, Auto pivot) into Rotation, its Factor exposed as Align Rotation; Math Multiply into Scale exposed as Scale; Amount integer, default 32, min 3. Tick Modifier to get it in Add Modifier.
  Stitch generator on a curve: stitch object = a Torus cut in half with filled caps (origin sets stitch height). Resample Curve (Count 7) > Instance on Points; Align Rotation to Vector (Z) on Position; Object Info (stitch, Original) as Instance; Join Geometry with the original curve.
- Principle: a mesh circle's vertices are the instance points; resampled curve points are stitch points.
- Pitfall or use when: the frame feeds Position into the align node; a Curve Tangent is the more usual input, so check stitch orientation.

**Grease Pencil rope**: a drawn animated path becomes a braided rope.
- Steps: Grease Pencil object, Draw mode (Pencil, Radius 0.01 m, Strength 0.6), Onion Skinning on (before and after frames), one stroke per frame. Modifier group on the object: Resample Curve (Length 0.01) > Set Curve Radius 0.015 > Set Curve Tilt (Index / Divide 2.13, so it twists) > Curve to Mesh with a braid Profile Curve > Set Material > Join Geometry.
  Profile: Curve Circle (Radius 1, Resolution 30) copied by three Transform Geometry at (1,0,0), (0.5,1,0), (0.5,-1,0), joined and moved -0.5 on X. End knots: Object Info (Knot) > Instance on Points with Selection from Endpoint Selection (start 1, end 1), rotation Align Rotation to Vector (Y, Normal). Based on a CG Matter rope tutorial.
- Principle: the GP stroke acts as the curve and each frame is its own pose, so no rope sim.
- Other tools: Unity or Unreal spline mesh on a hand-keyed path; three.js TubeGeometry along keyed CatmullRom points.
- Pitfall or use when: strokes are invisible while the modifier is on, so use onion skin. Grease Pencil 3 has layer groups, a brush asset library and geometry-nodes support.

**Procedural castle (Extra Objects Wall Factory)**: wall, tower and cone roof from an add-on plus curve modifiers.
- Steps: enable Add Mesh: Extra Objects (from Extensions in 4.2+; whether Wall Factory still ships there is unverified). Shift+A > Mesh > Extras > Wall Factory (Start 0, End 25.09, Top 15, Block width 1.5, Height minimum 0.5 for chunky bricks, Depth 2, Grout 0.10, window width 2.5 height 3.5, Top Arch). Base wall about 50 long; Repeat for windows.
  Bevel (0.1 m, 2 segments, Limit Angle 30, Harden Normals), Shade Smooth (3.x also needed Auto Smooth; removed in 4.1, use Smooth by Angle). Set Origin to Geometry (individual), F3 "Randomize" (Mesh Transform Randomize) and scale until bricks touch. Bend: Array above a Curve modifier with a Bezier curve; tower: Repeat off, radius about 25, height 30, Curve modifier with a Bezier Circle, parent it (Ctrl+P > Object Keep Transform).
  Roof: plane, scale the top in, Solidify 0.25 with crease 0.25, Subdivision, F3 "Convert to Mesh"; two Arrays (Relative X 0.8 count 8; Y 0.5 Z 0.5 count 6) for a shingle fan, Curve modifier on a Bezier Circle, Ctrl+T tilt (about -49 degrees) so it fans into a cone.
- Principle: everything stays procedural; edit the curve to reshape.

**Gaussian splats (Blender 5.3 beta, not in 5.2)**: a splat is a point cloud with attributes.
- Steps: File > Import (.ply or .spz). Data properties > Type: 3D Gaussian Splat or Points. Render settings > Performance > Viewport Pixel Size 1 for sharpness; EEVEE looks better than Cycles. Dispersion group: Set Position Offset = Scale(Random Value Vector -1 to 1, Seed 42, Value keyed from 5 to 0). Spheres: Instance on Points with a UV Sphere (Radius 0.1, Subdivisions 3), material Attribute (Instancer, `splat_color`) > Emission. A Random Boolean (0.05) thins millions of points for the viewport.
- Pitfall or use when: lighting in a splat is baked. Splat tools: Brush (free, open source), SuperSplat for viewing and editing.

## Workflow

**Asset Browser libraries and tools**: reuse materials, lights, worlds and node groups by drag and drop.
- Steps: Preferences > File Paths > Asset Libraries, add a folder; set Import Method to Append when a pack must give each drag its own copy (Append Reuse Data shares data). Mark an asset: Outliner (Blender File view) right click > Mark as Asset; make a catalog with the plus beside All; save in the library folder. Dragging a collection asset arrives as a collection instance, which locks controls: untick Instance in the Add Collection redo panel.
  Use Link in production so source edits propagate. Worlds can store HDRIs; store warm and cool Area lights, cookie lights and fog as assets. Node groups marked as assets appear under Add Modifier and in the Add menu.
- Principle: any object, material, world or node group can be a preset.
- Pitfall or use when: pack effects built on simulation nodes need 3.6 or later.

**Simplify and viewport speed**: a lighter viewport on a slow GPU. (heard)
- Steps: Render Properties > Simplify: turn off Subdivision, Volume resolution and particles in the viewport; Texture Limit (for example 64 px) for Material Preview and Rendered views. Use viewport renders with materials for the edit pass instead of final renders. Long projects: environments, props and characters as separate .blend files, Append or Link into scenes.

**Video Sequencer basics**: cut, fade, grade and export renders as a video.
- Steps: File > New > Video Editing. Output: FFmpeg Video, MPEG-4, AAC, 24 fps, resolution matching footage. Proxy: Strip Proxy & Timecode panel, 25 percent for weak machines. Keys: K split, G grab, H mute, Alt+H unmute, Ctrl+G meta strip, P preview range, Ctrl+Home and Ctrl+End set start and end. View > Range > Set Frame Range to Strips last.
  Strip sidebar: Compositing Blend, Transform, Crop; all keyframeable. Add > Color, Text, Adjustment Layer, Effect Strip (Gaussian Blur, Speed Control). Modifiers: Curves, Color Balance, Hue Correct, White Balance, Tone Mapping; histogram and waveform scopes. Fade: right click strip > Fade In/Out; audio needs its own fade. Render > Render Animation.
- Principle: treat renders as strips, scrub with proxies, set the range from strips at the end.
- Pitfall or use when: a meta strip loses separate audio control; Resolve or Kdenlive do the same.

**Hotkey sheet** (heard, unchanged in 5.2): Shift+A add; Ctrl+1/2/3 subdivision level; G then X, Y or Z; Ctrl+A apply transforms; Ctrl+R loop cut; Ctrl+B bevel; Alt+click edge loop; Alt+S shrink/fatten; V rip; L select linked; P > By Loose Parts; Shift+D duplicate; Ctrl+J join (also frames nodes); Ctrl+I invert selection;
K knife (C cut through, A angle snap); I inset; E extrude; M move to collection; `/` local view; H, Shift+H, Alt+H hide in Sculpt face sets; F3 search (Convert to Mesh, Grid Fill, Merge at Center, Pack Islands, Denoise Animation); Shift+S snap (Selection to Active, Cursor to Selected); Shift+C reset cursor and view; Alt+R and Alt+G clear rotation and location;
Ctrl+P > Keep Transform; Ctrl+G group nodes; Ctrl+H collapse a node to used sockets; F2 rename; I keyframe a hovered value; Node Wrangler: Ctrl+Shift+click preview, Ctrl+T texture setup, Ctrl+Shift+T load a PBR set, Shift+right-drag reroutes; Ctrl+C then Ctrl+V on a colour field copies it.

## Add-ons

- Turbo Tools Turbo Render: Cycles at 50 samples that beats 1000, with a "remove temporal flicker" publish step; denoises extra passes through the compositor. Paid. Free alternatives: the Denoise and Temporal denoise entries above.
- Simple Bake: bake Cycles lighting into textures for EEVEE. Paid in the video (heard). Free alternative: Blender's own Bake panel.
- Dynamic VFX Elemental Asset Pack: drag-and-drop geometry-nodes effects (explosion, shield, rain, snow, fire, lightning, fog, dust, fish school, tornado, speed lines). Paid on Blender Market. Free alternatives: the Simulation Zone, speed lines, cone light ray and fog entries above.
- Better Array: free circle array and effector (clone modes Grid, Line, Circle, Object, Curve; effectors with gizmos, writes a "Color" attribute); full version paid. Free alternative: New Array modifier and Circle array above.
- CinePack: asset-browser camera moves (push, pan, 360 track, crane, handheld). Paid affiliate. Free alternative: Noise modifier on camera F-curves.
- Fit Lattice: auto-sizes a lattice to an object. Paid. Free alternative: Lattice modifier by hand.
- Gobo Light Textures and Gobos Plus: light cookie packs, Superhive, paid. Free alternative: any grunge image through the gobo node setup above.
- Roots by curve: a free geometry-nodes tool from a Ko-fi page, creator not named (heard).

## Dropped or covered elsewhere

- Painterly grass with Scatter on Surface (grass cards, Poisson Disk, Pick Instance), `#frame` driver, Is Camera Ray world and fog, Images as Planes, and the basic mist composite already sit in environments.md, shading-and-textures.md and workflow-and-addons.md.
- Texture-paint mask, freckle brush, image-to-PBR and shape-key notes belong to the modeling and texturing references; career, sponsor and pipeline-tool talk (Milanote, PureRef, Omniverse) was dropped.

