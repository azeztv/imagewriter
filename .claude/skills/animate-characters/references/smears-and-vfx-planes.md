# Smears and VFX planes in 3D

Effects that make a 3D shot read as drawn: stepped noise planes, shape-key smoke and puffs, a Grease Pencil splash, rain
on twos, layered flames and particle splashes. Notes come (Blender). Step size and the `floor` driver are in
[stepped-2d-look-in-3d.md](stepped-2d-look-in-3d.md). Check tags follow the same meaning: `heard` or `verified`.

<!-- skill-navigation:start -->
## Reading Map

- [Smears and VFX planes in 3D](#smears-and-vfx-planes-in-3d)
- [Stepped noise VFX plane](#stepped-noise-vfx-plane)
- [Rain streaks on twos](#rain-streaks-on-twos)
- [Grease Pencil rain splash](#grease-pencil-rain-splash)
- [Shape-key smoke and puffs](#shape-key-smoke-and-puffs)
- [Layered flame and sparks](#layered-flame-and-sparks)
- [Particle splash and bubbles](#particle-splash-and-bubbles)
- [Shape-key and noise jiggle](#shape-key-and-noise-jiggle)
<!-- skill-navigation:end -->

## Stepped noise VFX plane

Transparent streaks for wind, dust and speed lines.

1. Add a plane. New material, delete the Principled BSDF.
2. Add a Noise Texture. Switch it from 3D to 2D. Press `Ctrl+T` (Node Wrangler, still bundled) to add Texture Coordinate
   and Mapping.
3. Add a Map Range after the noise to clamp. Stretch the streaks sideways with the noise scale.
4. Extrude the plane edges (`E`) so it curves around the camera and covers a rotation. Put the camera on the view with
   `Ctrl+Alt+Numpad 0`. Optionally parent the plane to the camera.
5. Animate Mapping X Location with a driver expression. Start with `#frame`, then change it to a `floor(frame/4)/31`
   style form, with brackets: floor of the frame divided by the choppiness (4 changes every 4 frames), then divide by a
   larger number to slow it.
6. Mix Shader: Transparent BSDF in the first slot (the blacks), an RGB (Color) node in the second (the whites). Blender 5.0
   calls the node Color.

- Verified at 10:36 (Blender 5.0.1): the formula sits in Mapping Location X and starts `(floor((frame`. The rest of the
  text is unverified. Noise 2D fBM, Normalize on, Scale 10.85, Detail 2, Roughness 0.5, Lacunarity 2, Distortion 0.
  Map Range Float, Linear, Clamp on, From Min 0.73, From Max 1, To Min 0, To Max 1.15. Mapping Scale X 0.7.

## Rain streaks on twos

1. Plane, new material, Noise Texture, `Ctrl+T`. Scale X very high so the streaks are thin. Clamp heavily with Map Range.
2. Mix Shader with Transparent BSDF in the first slot, the mask as Factor, a white Color node in B.
3. Animate Mapping Y with `#frame` typed in the field. For twos wrap it in a floor and divide. A larger divisor is slower.
4. Set Blend Mode from Dithered to Blended (Blender 4.2+ EEVEE: Material > Render Method Blended). Turn off Cast Shadows on the plane.

- Verified at 50:08 (Blender 4.5.0): Mapping Y `(floor((frame) / -2))/-8`, Mapping Scale X 11.04, Y 0.42, Z 1.0,
  noise Scale 15.32, Detail 2.0, Roughness 0.251.
- Rebuilt in Blender 5.2 by script and checked: the Mix Shader first slot takes Transparent BSDF and the second an Emission
  (white), because a Color node cannot link to a shader socket by script; Mapping Vector from the UV output; the Mapping Y
  driver is `fcurve = mapping.inputs["Location"].driver_add("default_value", 1)`, type SCRIPTED, expression above. With
  `floor(frame / -2)` frames 1 and 2 render pixel-identical (PSNR inf) and frame 3 jumps, which is the held-on-twos look.
- A second creator note uses a Noise Texture with a Math Floor for the rain in the froggie scene (no values given).

## Grease Pencil rain splash

The one use of Grease Pencil he likes, for small hand-drawn effects. Grease Pencil is v3 in Blender 4.3+ and 5.x.

1. `Shift+A` > Grease Pencil > Stroke. In Draw mode erase the stroke (hold `Ctrl` and erase it all).
2. Turn on Auto Keying. Pick white. On frame 1 draw three short streaks.
3. Go forward about 3 frames. Erase and turn on Onion Skin (if it is not visible, press the down arrow then the right
   arrow to step between frames). Draw the streaks again, smaller and more spread out.
4. About 3 frames later erase everything. Turn Auto Keying off.
5. Duplicate the object (`Shift+D`) around the scene. In the Timeline select the keyframes and `Shift+D` to repeat the
   splash when you want it.

- Check: heard (Blender 5.0). He uses shader setups for everything else and keeps Grease Pencil for smears in fight shots.

## Shape-key smoke and puffs

Use shape keys on a subdivided plane instead of Grease Pencil. Sliders let you change the extent without redrawing.

1. Add a plane. Edit Mode, right-click > Subdivide.
2. Object Data > Shape Keys: `+` adds the Basis, `+` again adds Key 1. Set it to 1, then shape it in Edit Mode with
   proportional editing.
3. Add Key 2 and press the edit button on the shape key to shape a different puff. Add more keys the same way.
4. Key each value with `I`, in order: key 1 at frame 1, key 2 at frame 2, and so on. Select the keys and press
   `T` > Constant so the puff steps.
5. Add a Noise Texture shader on that plane with an animated Map Range so the smoke dissipates over time.

- Used for smoke from a character's mouth.

## Layered flame and sparks

- Flame: a sphere, extruded every other vertex on top for inverted-V tips. Add a Displace modifier driven by an Empty
  and drag the Empty to animate. Duplicate it: the first layer orange emission, the second layer more transparent, the
  bottom layer yellow and the top reddish. Sparks: duplicate the flame, a gradient from top to bottom, a mostly black
  Noise Texture animated upward.
- A downloadable fire asset in another video works the same: copies of one object in different colours (bright at the
  base, yellow in the centre, orange or red at the top), some partly transparent. Its speed is a "frame divided by
  number" node: 500 instead of 200 is slower, 50 is faster. (unverified: he did not build it live, no timestamp)

## Particle splash and bubbles

- Splash: an Ico Sphere with a flat white Color material. A plane with a Particle System (Emitter) renders the Ico Sphere
  as the object. Set Frame Start -50 and End 250 so the splash is already going at frame 0. Tune velocity. Set the plane
  material to Transparent BSDF to hide it. Duplicate emitters at the top, base, rocks and sides.
- Frying bubbles: duplicate small spheres and vertex-parent them to the egg edge (select three vertices, `Ctrl+P` > Vertex
  (Triangle)). A shader outputs black or white from object location, so they flicker as they move. Manual placement took
  about 30 minutes.

## Shape-key and noise jiggle

- Idle life on food and props: shape keys that move the object a little in several directions. Key each value or add a
  Noise F-curve modifier on the value.
- Pulsing egg: Key 1 moves the egg toward the centre and back, Key 2 is a spasm puff, Key 3 is an edge puff (`Alt+click`
  an edge loop, `S` slightly). Press `I` over each slider and oscillate 1 to 0 over the whole time. In the Graph Editor
  (`Ctrl+Tab`) hide the other keys to see one curve and use `Shift+D` to repeat the keys along the timeline. For Key 3 use
  a Noise modifier with some Strength instead of keys. Do it for every egg.
- Eye squash: one shape key slider squashes the eyes.
