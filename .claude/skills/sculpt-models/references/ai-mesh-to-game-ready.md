# AI high-poly to a game-ready, realistic asset

Reading map: 1 Generate in parts · 2 Assemble · 3 Retopo and UV · 4 Bake (script) · 5 Detail, roughness, extras · 6 Skipped.
Marks: [M] measured here on 2026-11-11, [R] reported by the source video and not tested here, [O] checked against
the vendor's own page. Tripo steps use the Tripo Studio web app.

## 1. Generate in parts [M]

For a creature, vehicle or character that must hold up in close-up, do not generate the whole thing at once.
Measured 2026-11-11 on one shore crab photo, H3.1, same 2K export and credits per job: the claw inside a whole-crab
generation got about 43k faces and 0.39M texture pixels and read as smooth clay; the claw generated alone got 288k faces
and 2.8M texture pixels (about 7 times both) with the shell granules and joints carved in the geometry. The part image
drifted from the photo (chunkier claw, the pincer teeth lost), so step 2's check is required, not optional.

1. List the parts that differ in shape: for a crab, the top shell, the underside, one claw, one leg (segments), one eye.
   Only one of each mirrored or repeated part.
2. One reference image per part, on a plain background, matching colour and lighting across the set. Give the image
   model both a prompt and an input image (the whole-subject reference); Tripo Studio's own image tool works (GPT
   Image 2.5 cost 0 credits on the Max plan). Check every image against the reference for shape, proportion and
   small features (teeth, spines, joints) and regenerate before spending 3D credits.
3. Generate each part from its image in Tripo Studio with the high-fidelity model (the "H3.1 - Best Quality" option at
   the time of the video [O]; 65 credits a job with 8K texture on, about 3 minutes, measured). A small part needs no
   more than about 1M faces. Studio also has a members-only "Generate in Parts" switch that splits one generation
   into segments; it is a different thing and was not tested here.

Pick the route by shot: parts for a hero asset seen up close, where the detail pays for an assembly pass (section 2's
crab cost 250 credits for 2 more parts and 3 retopos); one whole generation for anything seen from a distance, since
its pose and proportions come out coherent with no assembly.

Why: each part gets the generator's full resolution, and image-following beats a whole-body generation on fine organic
detail. Other high-fidelity generators gave sharper meshes but followed the image worse on organic shapes [R].

## 2. Assemble [M]

Place the parts by script against the reference photo: one anchor per part (the joint end of a leg or claw, the
centre of the body), a turn that lays it in the body's frame, then location, angle and scale per instance; the left
side is the right side times a -1 X scale. Reuse one leg, scaled per position. Render a top view beside the photo and
adjust until the outline matches; the whole-subject generation is a good guide for pose and proportion. Assemble the
low parts with their baked maps (section 4), since each part's high and low share one space.

Measured 2026-11-11, crab from 3 parts (shell, one claw, one leg; 8 instances): 31k triangles against 298k for the
whole-crab generation, with the claw teeth, shell granules, eyes and leg spines that the whole generation smoothed
away. But the result read as kit-bashed: the shell image had empty leg sockets that stayed as visible rings, legs sat
beside them instead of in them, and the pose was stiffer than the whole generation's. Ask for the body image with
short leg stubs or closed sockets, and seat each leg in its socket in the side view too, not only from the top.

## 3. Retopology and UV [M]

- Run Studio's Retopo tool (left bar) on each high part: Quad, Smart Mesh on (P1.0 on 2026-11-11), polygon count from
  500 to 10000, 40 credits a part, about a minute. Targets of 1500 and 3000 gave 1.7k and 2.8k quads; 3k held a crab
  shell's shape and teeth, 1.5k a claw and a leg. The "Smart Mesh" tab of the Model panel is a different thing: it
  generates a new model from an image.
- The video reported that retopo resets each part's position and scale; on parts generated in Studio and retopologized
  in place it did not (mean gap 0.2% to 0.3% of the size on all three). `bake_ai_mesh.py` still warns when the mean
  gap is over 1% of the object size; then put the low back on the high before baking.
- The retopo comes back with a projected texture, but bake your own colour anyway (section 4).
- Spend five minutes on the wireframe at joints and tight areas; mush there spoils the bake.
- UV: Tripo Studio Smart UV costs 10 credits for 4 results. Generate all 4, keep the best, and add a seam in Blender
  where a close-up shot would show stretching.

## 4. Bake [M]

`blender -b --python scripts/bake_ai_mesh.py -- --glb high.glb --low low.glb --out <folder> [--res 4096]`
(without `--low` it decimates the high as a stand-in). It sizes the ray distance from the measured low-to-high gap
(twice the 95th percentile, at least 0.5% of the size), bakes tangent normal and base colour with 8 px padding, prints
coverage and the share of steep normal pixels, writes the maps, the node group and renders, and saves a .blend.

Measured on a 14.5k-face Tripo postbox with a 3k low: mean error against the high-poly render was 0.049 with colour
only and 0.034 with the baked normal; the faceting from the decimation is gone.

- Parts that are mirrored or repeated exist on one side of the high only: turn the Mirror modifiers off for the bake so
  the empty side cannot overwrite good pixels, then back on; the mirrored copy reuses the texture through a +1 UV
  offset [R].
- Bright green or orange patches along normal-map island edges at joints mean the low and high shapes differ there;
  check them at the shot's camera before calling the bake done [R].

## 5. Detail, roughness and small extras

- Detail normal from base colour, blended with the baked normal (Reoriented Normal Mapping) in the node group
  "Normal tuning RNM", with Baked Strength and Detail Strength sliders [M]. It adds paint and surface grain the
  high-poly does not have, so the error against the high rose slightly (0.034 to 0.037); judge it by eye at the shot.
- Roughness from base colour with noise, never uniform [M]. Bright does not mean glossy: with one range for the whole
  asset the grey concrete base read wet. Set `--rough-min` and `--rough-max` per material, or mask per material.
- A subsurface weight map for thin shell and skin edges (a `*_sss_weight` texture) was shown working in the render [R].
- Bristles, hairs and spines: one small triangle card coloured from a spot on the same UV, scattered over the part
  with geometry nodes (Distribute Points on Faces, then Instance on Points with random rotation and scale) [R].

## 6. Seen and not adopted

- A web texture inpainting tool (Modddif, free beta tier [O]) to add detail per view on a 4K texture: our
  photo-to-PBR route and real scans come first; try it only when a generated texture misses a spot.
- An AI video (Kling) as the animation reference and an agent-built rig: rigging stays with `rig-characters`, motion
  with `animate-characters`.

