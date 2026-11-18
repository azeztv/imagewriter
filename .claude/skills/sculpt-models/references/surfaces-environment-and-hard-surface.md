# Surfaces, environments and hard surface (`surfaces-environment-and-hard-surface.md`)

Surface detail that does not read as noise, rocks and cliffs that look broken by nature, cloth that hangs from
something, and hard edges that catch light. Marks: **[S]** sourced, **[R]** rule of thumb, **[D]** our untested default.

Reading map: 1 layered surface detail, 2 cloth folds, 3 rocks, cliffs and terrain, 4 bark and wood, 5 hard surface,
6 stamps vs procedural.

## 1. Layered surface detail

Single-frequency noise is the mark of a mushy procedural surface [R]. Stack distinct scales, each with its own strength:

| Layer | Skin | Rock | Strength (share of the layer above) |
| --- | --- | --- | --- |
| Large | Folds, fat pads | Cuts, fractures | Sculpted, not noise |
| Medium | Wrinkles, creases | Chips, ledges | 30 to 50% [D] |
| Small | Pores (broad, then finer T-zone) [S] | Grain | 10 to 25% [D] |
| Micro | Fine breakup | Roughness map only | Texture, not geometry |

- Leave rest areas: detail at equal strength everywhere reads as a texture slapped on [R].
- Pores are denser and finer on the nose and cheeks, absent on lips and eyelids; lips carry lines [R].
- Detail invisible at the final camera distance is deleted, not kept "for quality"; bake or texture it instead.
- Which method per scale (texture, displacement, scatter, model): `~/.claude/skills/3d-generalist/references/assets-and-kitbash.md`, "Detail ladder".

## 2. Cloth folds

1. Find the support points first: shoulders, hips, belt, knees, elbows [R].
2. Pick the fold type per region. Classic seven: pipe (hangs from a point), zigzag (a bent pipe), spiral (wrapped round a
   limb), half-lock (where fabric changes direction at a bent joint), diaper (hangs between two supports), drop (hangs
   from one support), inert (rests on a surface). Proko's list swaps zigzag and drop for compression and flag [S].
3. Tension folds radiate from a support; compression folds bunch at the inside of a joint [R].
4. Blender: Cloth brush, or Pose and Boundary brushes with the Cloth deformation target, for bends without collisions
   [S]; or a cloth sim on the garment, then hand fixes.

## 3. Rocks, cliffs and terrain

- **Fracture logic:** one main set of parallel joint planes plus 1 or 2 cross sets at a consistent dip; rocks broken in
  random directions look fake [R].
- **Block, cut, then wear:** a blocky mass, big planar cuts (Flatten, Scrape, Trim-style planes), then erosion on edges.
  Stylised flat-plane rocks: 5 to 15 large planes, sharp edges with a slight chamfer, little noise [D].
- **Strata:** horizontal or one consistent tilt; hard layers stand proud, soft layers recess [R].
- **Erosion direction:** water grooves run downhill, wind-worn faces face the wind, talus piles at the base [R].
- **Terrain:** several displacement frequencies with ridged noise at the large scale, then hand-sculpted paths and
  focal features. Real terrain first when the place is real: `~/.claude/skills/use-3d-software/references/environments.md`.
- **Procedural route:** rock = cube, a few boolean or bisect cuts at the joint angles, Voxel Remesh, Displace with low
  strength Voronoi plus noise, then decimate for real-time [D].

## 4. Bark and wood

Vertical flow along the trunk, splits that follow the axis, fewer cross-cracks; growth flares at roots and branches [R].

## 5. Hard surface

- Planar brushes for flat faces and crisp edges: Flatten, Scrape, the plane and trim brushes, Clay Strips with a hard
  falloff; Face Set boundary auto-masking protects edges [S].
- Panel lines: mask or face set, shrink the mask edge, push in with a hard brush [R].
- Every hard edge gets a small bevel that catches light [R].
- **Use poly modelling instead** when the shape is mostly planes, cylinders and booleans, needs exact dimensions or
  symmetric parts, or must subdivide cleanly; sculpt adds only wear, damage and organic transitions [R]. Machined
  parts at real dimensions: the `model-parts-in-cad` skill.

## 6. Stamps vs procedural displacement

| Method | Good for | Watch |
| --- | --- | --- |
| Hand-cut big forms | Primary rock and terrain shapes, hero silhouettes | Slow, needs a reference |
| Procedural displacement | Medium and small detail over large areas, seamless | One frequency looks mushy; layer it |
| Alphas and stamps | Hero close-ups, focal points | Repetition shows: rotate, scale and vary every stamp |

Best default: hand-cut large, procedural medium, stamps only at focal points [R].

Sources: Proko "A review of the 7 folds"; Blender 2.91 sculpt notes and BlenderNation on Pablo Dobarro's cloth and
boundary tools; 80.lv "From model to ZBrush splash screen" (rock planes); novedge ZBrush tip on skin pore layers;
polycount discussion on planar cliffs. Research pass 2026-11-09.
