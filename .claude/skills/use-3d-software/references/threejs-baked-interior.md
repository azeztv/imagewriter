# A photoreal room in three.js, all from code

How to make one quiet interior (a bedroom, a studio, a shop) look like a photograph in a browser, with no model files,
image textures or HDRIs.
Cook path tracer on 2026-11-13.

Reading map: Scene rules, Baked light, Textures, Picture and grade, Film, Porting to a path tracer.

## Scene rules

- Units are metres. Fix one frame for the room, for example X along the window wall and Z into the room.
  Write the window opening and furniture footprints in one `layout.js` that every part reads.
- One file per part (`bed.js`, `desk.js`, `plants.js`). Each exports a load `order` and `build(ctx)` that returns a
  `THREE.Group` in world metres. The context carries the shared material library, a list for walk colliders and a
  list for per-frame callbacks.
- All randomness goes through one seeded RNG. `Math.random()` breaks the bake and makes frames differ between runs.
- Every box gets a bevel of 1.5 mm or more. Sharp boxes are what make a code-built room look like code.
- Cloth is a designed height field (folds, piping, a printed pattern), not a flat plane. Vines hang on catenary curves
  with instanced leaves. Trees outside grow from a branching skeleton with leaf cards.

## Baked light (no real-time lights)

- Bake sky light through the window with a small CPU path tracer in web workers on `three-mesh-bvh`.
  Trace a first pass of full paths. Then do a final gather with next-event estimation through the window opening.
  Combine the two by multiple importance sampling.
- Store irradiance and its dominant direction per vertex (a binary file loaded at start). Normal maps then still shade,
  because the shader lights the per-pixel normal from the stored direction.
- Per-vertex light needs vertices: tessellate big flat faces. Where objects rest on a surface, use a maximum edge of 15 to 20 mm.
  On large furniture faces, use 40 to 60 mm.
- Posters and rugs must not occlude in the bake. Otherwise they carve a dark halo into the surface behind.
- Give cloth and leaves diffuse transmission in the bake: probability about 0.3, a transmission colour, two sided.
  Sheers and leaf cards with holes also get a fraction of rays that pass straight through.
- Many identical small things (leaves): one `InstancedMesh`, one light sample per instance.
- Each textured material gives the bake its linear average albedo, so bounce light carries the right colour.
- Specular comes from a box-projected PMREM capture of the room, not from lights.
- Anything that moves (wind) moves in the vertex shader from a shared time uniform. The rest pose is what gets baked.

## Textures from code

Synthesize at load time with noise and Canvas2D: woodchip wallpaper, oak laminate, linen weave, cable knit, leaf
atlases, postcards. Small wear (a water ring, dust on the sill, candle soot) sells the room more than resolution does.

## Picture and grade

- HDR pipeline with contact AO and a light bloom (about 0.08).
- Use a high exposure on a dim scene (19 for pre-dawn sky light) into an Uchimura curve.
  Apply the curve partly per luminance and partly per channel.
  Pull highlights towards their luminance so bright areas do not go neon.
- Tonal tints: cool shadows (about 0.9, 0.98, 1.12), near neutral mids, a cool white balance for dawn.
- Saturation 1.1 plus a vibrance boost only where green leads, so plants read alive without lifting the whole frame.
- Vignette 0.15 and fine grain (about 0.012) that fades in the highlights.
- The outside through the window is drawn in its own pass at about 0.2 of its brightness. That keeps the trees
  readable instead of a white blown window. This is a grade choice, not physics.

## Film

- Shots are Catmull-Rom camera keys with per-shot exposure, a focus target that can pull, and fades.
- Each output frame averages jittered sub-frames: anti-aliasing, thin-lens depth of field and a 180 degree shutter
  in one loop. That only works because every motion (wind, camera) is a pure function of time.
- Masters: HDR10 (PQ, BT.2020, 10-bit HEVC) plus SDR, through ffmpeg.

## Porting to a path tracer (Crucible Cook, measured 2026-11-13)

What changed and what it cost when the same room was traced live instead of baked:

- Window glass blocks next-event estimation, so the room fills with speckle. Let shadow rays pass the glass panes
  (clear their shadow visibility bit), keep camera and bounce rays refracting.
- Denoise with OIDN (CUDA, about 0.05 s a frame), not an a-trous filter, which leaves blotches on cloth.
- To recreate the "outside at 0.2" grade, trace a second pass where only glass stays and every opaque surface is black.
  Subtract 0.8 of that pass. A path tracer sees one world, so the window otherwise blows out.
- An environment panorama exported from cube passes needs supersampling and a slight blur, or tree leaves stipple.
- Decimate with error-bounded simplification (meshoptimizer, absolute error), not a fixed ratio, which punches dark
  dots into leaves and folds.
- An animated sun is a separate light pass. Render the sky pass and the sun pass apart.
  Add `sunAmount(t) * sun` in linear light before the denoise. Volume fog goes only in the sun pass with fewer bounces,
  or each frame costs several times more.
- Move the grade with the light, or the sun patch clips to white.
  As the sun rises, blend from the dawn look (exposure 19, cool white balance) to a sunrise look.
  The sunrise look has exposure about 9, a neutral white balance and a warm highlight tint.
- Reuse one native session per pass and send only the camera per frame.
  Measured: 0.55 s a frame at 480x270 and 32 spp, RTX 3060, 349k triangles.
- Cook has no thin diffuse transmission yet (Crucible issue 1058), so curtains and leaves that the bake lit from behind
  read darker. Lifting their albedo a little narrows the gap.

Source: Leon Lin, "room-at-dawn" (MIT), github.com/Leonxlnx/room-at-dawn.
