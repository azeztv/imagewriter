# Blender 5.x sculpt toolset (`blender-sculpt-tools.md`)

Exact names for Blender 5.2: brushes, topology modes, masks, face sets, symmetry, alphas, bake, retopology, and what
runs headless through `bpy`. Marks: **[V]** verified in the Blender manual or release notes, **[O]** observed by
running Blender 5.2.2 headless (2026-11-09), **[U]** unverified. Manual base: `docs.blender.org/manual/en/latest/`.

<!-- skill-navigation:start -->
## Reading Map

- [Blender 5.x sculpt toolset (`blender-sculpt-tools.md`)](#blender-5x-sculpt-toolset-blender-sculpt-toolsmd)
- [1. Brushes are assets (4.3 and later)](#1-brushes-are-assets-43-and-later)
- [2. Topology modes: which one when](#2-topology-modes-which-one-when)
- [3. Masks, face sets, expand](#3-masks-face-sets-expand)
- [4. Symmetry, strokes, alphas](#4-symmetry-strokes-alphas)
- [5. Bake sculpt detail to a low poly](#5-bake-sculpt-detail-to-a-low-poly)
- [6. Retopology](#6-retopology)
- [7. Performance](#7-performance)
- [8. Headless bpy: what an agent can and cannot do](#8-headless-bpy-what-an-agent-can-and-cannot-do)
<!-- skill-navigation:end -->

## 1. Brushes are assets (4.3 and later)

- Brushes live in asset libraries; the Essentials library ships about 130 [V]. Pick from the asset shelf at the bottom
  of the viewport or `Shift+Space` [V]. Essentials brushes are read-only: Duplicate Asset to customise [V].
- Activate by script (`paint.brush_select` and `paint.brush_set` are gone) [O]:

```python
bpy.ops.brush.asset_activate(asset_library_type='ESSENTIALS',
    relative_asset_identifier="brushes/essentials_brushes-mesh_sculpt.blend/Brush/Clay Strips")
```

- Mesh sculpt brush names [O]: Draw, Draw Sharp, Clay, Clay Strips, Clay Thumb, Layer, Inflate/Deflate, Blob, Crease
  Polish, Crease Sharp; Smooth, Flatten/Contrast, Plateau, Fill/Deepen, Scrape/Fill, Trim, Scrape Multiplane,
  Pinch/Magnify; Grab, Grab 2D, Grab Silhouette, Elastic Grab, Elastic Snake Hook, Snake Hook, Pull, Thumb, Pose,
  Nudge, Twist, Relax Slide, Relax Pinch, Boundary; Density, Mask, Face Set Paint, Scene Project; 13 Cloth brushes.
- Renames [V]: Crease became Crease Polish (4.3); Flatten, Fill, Scrape, Plateau and Trim are one Plane type with
  Height and Depth (4.4); Blur brush (5.1); Scene Project, a shrinkwrap brush, and Add Primitive in Sculpt Mode (5.2).
- Python [V]: the brush type is `brush.sculpt_brush_type` (was `sculpt_tool`), `brush.size` is now the diameter,
  falloff is `curve_distance_falloff`, unified settings are `tool_settings.sculpt.unified_paint_settings` (5.0).
- Keys [V]: V Draw, C Clay Strips, Shift+C Crease, S Smooth, Shift+T Scrape/Fill, I Inflate, P Pinch, G Grab, M Mask;
  Ctrl inverts, Shift smooths, F size, Shift+F strength.

## 2. Topology modes: which one when

| Mode | Use for | Do not | Script |
| --- | --- | --- | --- |
| Voxel Remesh | Block-out, unifying volumes, cleaning scans | Animated meshes; objects with Multires; open meshes (fill holes first) | `mesh.remesh_voxel_size = 0.02`, `bpy.ops.object.voxel_remesh()` in Object Mode [O] |
| Dyntopo | Local concept detail without planning resolution | Final topology; meshes with UVs, colours or face sets (it loses them) [V] | `bpy.ops.sculpt.dynamic_topology_toggle()`; `tool_settings.sculpt.detail_type_method` RELATIVE, CONSTANT, BRUSH, MANUAL [O] |
| QuadriFlow | A quad base for Multires or Subdivision | Self-intersecting meshes (it does not fix them) [V]; it cancels with "needs to be manifold" when normals are inconsistent, even on a fresh voxel remesh: run edit-mode `normals_make_consistent` first [O] | `bpy.ops.object.quadriflow_remesh(mode='FACES', target_faces=4000)` [O] |
| Multires | Detail on a clean quad base, the source for baking | More than 5 levels (slow) [V]; a geometry-changing modifier above it | `modifiers.new("Multires","MULTIRES")`, `bpy.ops.object.multires_subdivide(modifier="Multires", mode='CATMULL_CLARK')` [O] |
| Decimate | Static assets for real-time | Animated meshes | `ratio` counts triangles [V] |

- Voxel size picks resolution: a 1 m head at 0.01 is a fine block-out, 0.003 is detailed [U]. `R` sets it in Sculpt
  Mode, `Ctrl+R` runs it [V]. Adaptivity above 0 turns off Fix Poles [V].
- Multires levels [O]: `levels` (viewport), `sculpt_levels`, `render_levels`; `multires_rebuild_subdiv` recovers levels
  from a subdivided mesh, `multires_base_apply` pushes detail into the base, `multires_unsubdivide` makes a lower base.

## 3. Masks, face sets, expand

- Auto-masking (Alt+A pie) moved in 5.2 to `paint.mesh_automasking_settings` with `use_automasking_topology`,
  `use_automasking_face_sets`, `use_automasking_boundary_edges`, `use_automasking_cavity` and more [O].
- Mask operators [O]: `paint.mask_flood_fill`, `sculpt.mask_filter` (SMOOTH, SHARPEN, GROW, SHRINK, CONTRAST_*),
  `sculpt.mask_from_cavity`, `sculpt.paint_mask_extract` (new object from a mask, with solidify),
  `sculpt.paint_mask_slice` (cut by mask, optional fill holes). There is no `mask_expand`; Expand is `sculpt.expand`
  (modal: Shift+A mask by topology, Shift+Alt+A by normals, Shift+W face set) [V].
- Face sets [O]: `sculpt.face_sets_init(mode=...)` from LOOSE_PARTS, MATERIALS, NORMALS, UV_SEAMS, SHARP_EDGES and
  more; `face_sets_create`, `face_set_extract`, `face_set_edit`; Alt+W pie, Ctrl+W grow [V].
- **Scriptable masks:** write `.sculpt_mask` (FLOAT on points) and `.sculpt_face_set` (INT on faces) with
  `mesh.attributes.new(...)` in Object Mode; Voxel Remesh keeps them with `use_remesh_preserve_attributes` [O].

## 4. Symmetry, strokes, alphas

- Mirror: `tool_settings.sculpt.use_symmetry_x/y/z`; radial symmetry is `mesh.radial_symmetry` since 5.0; tiling with
  `tile_x/y/z` and `tile_offset` [O][V]. Symmetrize headless: edit-mode `bpy.ops.mesh.symmetrize(direction='POSITIVE_X')`;
  `sculpt.symmetrize` crashed headless [O].
- Stroke methods [O]: `brush.stroke_method` DOTS, DRAG_DOT, SPACE, AIRBRUSH, ANCHORED, LINE, CURVE (one enum since 5.1).
  Stabilize Stroke (Shift+S) is the "lazy mouse": `use_smooth_stroke`, `smooth_stroke_radius`, `smooth_stroke_factor` [V].
- Alphas [O][V]: an image texture (`bpy.data.textures.new(name, 'IMAGE')`) in `brush.texture_slot.texture`;
  `map_mode` VIEW_PLANE or AREA_PLANE for stamps (3D only for procedural textures); rotate and randomise
  (`random_angle`, `use_random`) so stamps never repeat.

## 5. Bake sculpt detail to a low poly

Settings live in `scene.render.bake` (the old flat names are gone) [O]. Both routes need UVs on the low poly and an
active Image Texture node in its material; displacement images are 16 or 32-bit float, Non-Color [V].

**From Multires** (detail between viewport and render levels) [V][O]:

```python
multires.levels = 0; multires.sculpt_levels = 4; multires.render_levels = 4
bake = scene.render.bake
bake.use_multires = True
bake.type = 'NORMALS'          # or 'DISPLACEMENT', 'VECTOR_DISPLACEMENT'
bpy.ops.object.bake_image()
```

**Selected to Active** (high poly selected, low poly active, Cycles) [O]:

```python
scene.render.engine = 'CYCLES'
bake = scene.render.bake
bake.use_selected_to_active = True
bake.use_cage = False; bake.max_ray_distance = 0.3   # or use_cage = True, cage_extrusion = 0.02 to 0.2
bake.normal_space = 'TANGENT'; bake.margin_type = 'EXTEND'; bake.margin = 8
scene.cycles.bake_type = 'NORMAL'
bpy.ops.object.bake(type='NORMAL')
```

Ray distance and extrusion scale with the mesh: start at about 1 to 2% of the object's size and raise until no
holes show [U]. Bake normals for detail that stays inside the silhouette and displacement where it changes it.

## 6. Retopology

- Animated meshes need hand retopology: no automatic tool gives good deformation loops [V]. Loops go round the eyes,
  mouth, shoulders, elbows and knees (`~/.claude/skills/model-characters/references/base-mesh-and-box-modeling.md`).
- Tools [V][O]: the Retopology overlay (`overlay.show_retopology`), Poly Build, snapping to Face Project or Face
  Nearest, a Shrinkwrap modifier (`wrap_method`, `wrap_mode`) on the new mesh.
- Automatic for static or base meshes: QuadriFlow (built in); Instant Meshes (free, external, dormant since 2022, check
  its licence) [V]; Quad Remesher (paid, trial) [V].
- Budgets depend on the target engine; check its own guidance. Rough starting points [U]: background prop 500 to 5k
  triangles, hero prop 5k to 20k, real-time hero character 20k to 60k.

## 7. Performance

- 4.3 made entering Sculpt Mode on 16M faces take 1.9 s instead of 11 s; brushes on 6M faces got about 8 times
  faster [V]. There is no official interactive limit; split big sculpts into objects and hide what is not in use [V].
- Fast Navigate (`tool_settings.sculpt.show_low_resolution`, Multires only), Delay Viewport Updates
  (`use_sculpt_delay_updates`), Use Deform Only [V]. Topology Rake and cavity blur above 6 steps are slow [V].

## 8. Headless bpy: what an agent can and cannot do

Works in `blender -b` on 5.2.2 [O]: `object.voxel_remesh`, `object.quadriflow_remesh`, all Multires operators,
applying Remesh, Displace (procedural textures), Subdivision, Decimate and Corrective Smooth modifiers, edit-mode
`mesh.symmetrize`, both bakes, `brush.asset_activate`, writing mask and face set attributes, entering and leaving
Sculpt Mode.

Does not work [O]: `sculpt.brush_stroke` and the trim gestures (poll fails without a viewport); `sculpt.expand`
(modal). These **crashed** Blender headless after entering Sculpt Mode: `sculpt.symmetrize`, `paint.mask_flood_fill`,
`sculpt.mask_filter`, `sculpt.face_sets_init`, `sculpt.mesh_filter`, `sculpt.paint_mask_extract`,
`sculpt.mask_from_cavity`, and `voxel_remesh` while in Sculpt Mode. Run structural work in Object Mode.

**Procedural sculpt pipeline that runs headless** [O]:

1. Build primary masses as volumes (primitives, Skin modifier, metaballs), join, `voxel_remesh`.
2. Shape with lattices, proportional edit and vertex-group-masked Displace (`modifier.vertex_group`), then apply.
3. Detail in scale layers: one Displace per frequency, each masked to where it belongs, applied in order.
4. Smooth with Corrective Smooth or a Subdivision round trip, `voxel_remesh` again to clean.
5. Clean (merge by distance, delete loose, `normals_make_consistent`), QuadriFlow to the target count (Decimate if it cancels, or for static), UV unwrap, bake from the high copy (section 5). Worked example: `scripts/procedural_rock.py` (188k-face rock, 1.8k-face QuadriFlow copy, 8 s headless).
6. `scripts/check_sculpt.py` on both the high and the low copy.

Sources: Blender manual (sculpting brushes, adaptive, remesh, Dyntopo, Multires, face sets, expand, symmetry, stroke,
texture, Cycles baking, retopology, snapping, overlays, Decimate); release notes 4.3 to 5.2 (sculpt and Python API);
the Blender 5.2.2 RNA probed headless on 2026-11-09.
