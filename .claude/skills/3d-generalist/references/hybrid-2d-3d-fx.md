# Hybrid 2D and 3D effects (`hybrid-2d-3d-fx.md`)

Blend drawn 2D effects with a 3D shot so the final frame reads as one style: drawn explosions, smoke, impacts, speed
lines and smears on top of, or inside, a 3D render. Treat the 2D effect as its own layer with its own timing, light and
colour, then unify both layers with one shared finish. Use it for stylized shots, impacts, magic, fire and smoke, and
any piece that wants a hand-made feel on 3D motion.

Marks: **[S]** from a studio breakdown or the Blender manual (Sources at the end), **[U]** a route we have not run yet:
test it on one shot before a full piece.

## 1. Pick the approach

| Approach | Use when | How |
| --- | --- | --- |
| Drawn FX cards | Explosions, smoke, dust puffs, splashes | Key drawings on camera-facing cards in the 3D scene (section 2) [S] |
| Draw-over in comp | A few hero frames need a graphic accent | Render 3D, draw 2D layers over it in Krita or OpenToonz, composite [S] |
| Sim plus sprite merge | A big effect needs volume and a drawn look | Render the sim in two flat tones, mix drawn sprites into it so the seam is hidden [S] |
| Toon FX meshes | Stylized fire, smoke and impact shapes in 3D | EEVEE Shader to RGB plus a Constant colour ramp, animated on twos (section 3) [S] |
| Grease Pencil in 3D | Lines, speed lines, smears that live in depth | Line Art plus Noise boil, hand-drawn strokes on keys (section 4) [S] |
| Flipbook sprites (web) | three.js or Crucible scenes | Sprite sheet on a billboard, stepped frame (section 5) [U] |

## 2. Drawn FX cards (the most reliable route)

1. Draw 4 to 12 key drawings with alpha in Krita (Animation workspace) or OpenToonz. Split the effect into 2 or 3 tonal
   layers: soft tone, main shape, hot core [S]. Free CC0 flipbooks can be the base to trace or posterize (Resources).
2. Export a PNG sequence or one packed sheet.
3. Blender: plane with an Image Sequence texture (cyclic or once, frame offset per copy), facing the camera with a
   Track To constraint or a Geometry Nodes instance rotated toward the camera [U].
4. Material: Emission or Shader to RGB, so scene shadows do not muddy the drawing; the card keeps its own light [S].
5. Step the drawing on twos: one drawn frame per two scene frames [S]. Offset each copy's start so no two cards match.

## 3. Toon FX meshes (EEVEE)

- Diffuse BSDF into Shader to RGB into a Color Ramp set to Constant with 2 or 3 stops [S]. EEVEE only; it drops soft
  shadows, AO and screen-space refraction, and is correct only in the Combined pass [S].
- Animate scale, displacement or the noise W input in steps (twos or threes), with a hard rim colour [U].
- Dissipate by breaking the shape into smaller pieces over time, never by fading opacity [S].

## 4. Grease Pencil lines in 3D (Blender 5.2)

- Line Art modifier: source Scene, Collection or Object; edge types Contour, Crease, Material, Edge Marks,
  Intersections, Loose; Occlusion Level 0 for visible lines only; Depth Offset pulls strokes toward the camera so they
  do not clip; needs an active or custom camera [S].
- Line boil: Noise modifier, Randomize mode Steps, step 2 for boil on twos [S].
- Hand-drawn strokes on key poses plus procedural lines read best together: drawn lines carry intent, procedural lines
  carry detail [S]. Edge detection in comp alone looks mechanical [S].

## 5. Flipbook sprites on the web (three.js, Crucible) [U]

- Plane or `Sprite` with the sheet texture, `uvScale = (1/columns, 1/rows)`, frame `floor(time * 12) % frameCount`,
  offset per frame (V runs bottom-up).
- `NearestFilter` for hard drawn edges, `transparent: true`, `depthWrite: false`, sort by view depth, and a soft depth
  fade where the card meets geometry.
- Billboard with `mesh.quaternion.copy(camera.quaternion)`.

## 6. Rules that make the blend look intentional

1. **Own timing:** the drawn layer runs on twos (or ones and twos by moment) while the 3D can stay smooth [S].
2. **No visible seam:** never a purely drawn effect beside a purely simulated one; merge them or alternate 2D and 3D
   passes until the source cannot be told [S].
3. **Light:** the drawn hot core and light side face the scene's key light; the shadow side takes the scene's shadow
   tint [U]. Self-lit cards are fine when the effect is a light source [S].
4. **Depth:** cards depth-test against the 3D, sort, and fade softly where they intersect; a flat card never slices a
   character [U]. Push and pull elements in depth to balance the layers [S].
5. **Motion blur:** off on the 2D layer; on the 3D keep it at 180 degrees or off. Check on a test frame [U].
6. **Line:** one line weight and one dark tinted line colour (not pure black) shared by the 3D outlines and the drawn
   effects [U].
7. **One finish over both:** halftone, misregistration, paper or brush texture goes on in comp over the whole frame,
   not per layer [S].

## 7. Free resources

| Resource | Licence | Note |
| --- | --- | --- |
| Unity free VFX image sequences and flipbooks (unity.com blog) | CC0 | 22 realistic smoke, fire and explosion sets; trace or posterize them |
| a_klingon Explosions VFX (itch.io) | CC0, check the page | 14 pixel-art explosion sheets |
| Tornado Games magic sparks and attacks (itch.io) | CC0 per author, check the page | Pixel and non-pixel versions |
| Krita, OpenToonz, Blender | GPL, BSD, GPL | Drawing, timing and 3D |

Sources: VFX Voice "The return of hand-drawn and stylized effects animation"; Toon Boom on Across the Spider-Verse;
Befores & Afters on Spider-Verse line work (2024-01-10); 80.lv on Fortiche's K/DA fire; Blendernation on the Guilty Gear
Xrd GDC talk; Blender 5.2 manual pages for Line Art, Noise, Shader to RGB and EEVEE node support. Research pass
2026-11-09; nothing in this file has been rendered by us yet.
