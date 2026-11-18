# Style Presets: one method, any look

The construction in this skill (chunked low-poly body, hair shell plus face patch, painted atlas, hard-weighted rig)
does not change between looks. The look comes from five dials: proportion, triangle budget, texture size and filter,
shading, and the face. Pick the preset that matches the user's reference or theme, then copy the reference over the
preset wherever they disagree. Anime is one preset, not the default.

The values are skill guidance from common practice in each look, not from one creator. Check them against the
reference before building.

## The five dials

| Preset | Heads tall | Triangles | Texture and filter | Shading | Face |
|---|---|---|---|---|---|
| Anime | 5 to 7 | 600 to 1,200 | 1024 body + separate face sheet, Linear | Unlit, painted 3-step ramps | Painted lashes and brows, iris quads (see `head-and-face.md`) |
| Chibi | 2 to 3 | 300 to 800 | 512 to 1024, Linear | Unlit, 2-step ramps | Eyes 0.35 to 0.45 of face width, mouth tiny or absent |
| PS1 retro | 5 to 7 | 300 to 900 | 64 to 256 per part, Closest (nearest), no mipmaps | Vertex-lit or unlit, dithered colour | Painted at texture resolution, 1-pixel lines |
| N64 retro | 4 to 6 | 300 to 800 | 32 to 64, bilinear blur, vertex colours carry most of the colour | Vertex colours + one light | Simple painted eyes, big and round |
| Cartoon | 3 to 5 | 500 to 1,500 | Flat colour swatches, 256 to 512 | Flat or toon ramp, inverted-hull outline | Big shapes: dot or oval eyes, thick brows |
| Mascot | 2 to 4 | 400 to 1,200 | Swatches, 256 to 512 | Toon ramp + rim, outline | Wide eyes set apart, the brand mark on the chest or head |
| Painterly | any | 800 to 2,000 | 1024 to 2048 hand-painted, Linear | Unlit with light and shadow painted in, brush strokes visible | Painted, matched to the reference's line weight |
| Anime-semireal | 6 to 7 | Not budgeted: render-first quad mesh | 1024 to 4096 image layers per colour, Standard view | Diffuse > Shader to RGB > Color Ramp, key plus rim sun, Solidify outline | Flattened-front eyes, painted brows, hair as bevelled curves |
| Painted semi-real | 6 to 7 | Not budgeted | Same layers, harsh red and dark shapes | Toon ramp, painted darks and brights | Face value structure matters more than the shader |
| Manga hatching | 6 to 7 | Not budgeted | Hi-res hatch image on a grey base | Black outline, Fresnel rim times crayon texture | Black hair with white reflection shapes, hatched face |

The three NPR rows are built by `stylized-character-process.md` and shaded by `npr-shading-and-painted-look.md`.

## Notes per preset

- PS1 retro: snap vertices to a coarse grid in a vertex shader or a Blender geometry nodes `Snap` for the wobble, and
  keep texture warping (no perspective correction) only when the user wants that artefact. Set the texture filter to
  Closest in Blender and `NearestFilter` in three.js.
- N64 retro: smooth bilinear blur is the look. Paint most colour as vertex colours and keep textures tiny.
- Cartoon and mascot outline: duplicate the mesh or add Solidify (negative thickness, Flip normals, a black material
  with Backface Culling on). In three.js use a second mesh with `side: BackSide` scaled out along normals.
- Painterly: paint light direction, ambient occlusion and colour shifts straight into the atlas, because the material is
  unlit. Warm light, cool shadow. Keep brush texture visible at the render size.
- Any preset: the colour palette comes from the reference (`read_character_ref.py` swatches), never from the preset.

## Choose

1. Read the reference: count heads tall, look at line weight, texture detail and whether pixels show.
2. Pick the nearest row. If two fit, render both as quick front stills and let the user pick.
3. Write the chosen dials into the build notes, so the atlas, rig and render use the same values.
