# Workflow, hotkeys, add-ons and scripting

Reading map
- 5.x names: read first
- Headless and bpy recipes (measured on 5.2.2)
- Node editor habits
- Viewport and preference habits
- Add-ons, free vs paid
- Assets and sources
- Hotkey and workflow tricks
- Add-ons named in the later notes

## 5.x names

- Add-ons moved to Extensions in 4.2. Node Wrangler, Loop Tools, Rigify, Modifier Tools, Extra Objects, Images as Planes, A.N.T. Landscape are bundled or one click in Preferences > Get Extensions. Third-party zips install with the Install from Disk menu.
- Material and World `use_nodes` is deprecated and removed in 6.0. Nodes are always on, a new material already has a Principled node tree.
- Render engine id is `BLENDER_EEVEE` in 5.2 (Eevee Next). Old `BLENDER_EEVEE_NEXT` and `BLENDER_EEVEE_LEGACY` ids are gone.
- Node idnames use the pattern `GeometryNode...`, `ShaderNode...`, `FunctionNode...`. Renamed nodes keep working only under the new idname, for example `FunctionNodeAlignRotationToVector`.
- Group interface uses `tree.interface.new_socket(...)` since 4.0.
- Video output by script (5.0+): set `scene.render.image_settings.media_type = "VIDEO"` before `file_format = "FFMPEG"`. Without it the assignment raises `enum "FFMPEG" not found` (seen on 5.3).

## Headless and bpy recipes

- **Run headless safely**: Use `blender -b <file.blend> -t 6 -P script.py -- args` (machine paths in `../local.md` when present). Args after `--` reach `sys.argv`. Start it at below-normal priority, bakes use `-t 6`, never two heavy jobs at once, and GPU jobs follow the project's queue rules.
- **Render one still**: `blender.exe -b scene.blend -o //out/frame_#### -F PNG -f 1`. Animation: `-s 1 -e 48 -a`. Engine override: `-E BLENDER_EEVEE` or `-E CYCLES`. Set resolution in the script (`scene.render.resolution_x`) and low samples for previews.
- **Geometry nodes tree by script** (ran on 5.2.2): create `tree = bpy.data.node_groups.new("Name", "GeometryNodeTree")`, add `tree.interface.new_socket(name="Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")` and the same with `OUTPUT`. Add nodes with `tree.nodes.new("GeometryNodeDistributePointsOnFaces")`, link with `tree.links.new(a.outputs["Points"], b.inputs["Points"])` using socket names, not indexes, where possible. Attach with `modifier = obj.modifiers.new("Name", "NODES")` then `modifier.node_group = tree`. Find an idname by adding the node in the UI, then reading `bl_idname` in the Python console (unverified shortcut: the Python tooltips setting shows it on hover).
- **Modifiers by script**: `obj.modifiers.new("Sub", "SUBSURF")`, `"MIRROR"`, `"SOLIDIFY"`, `"ARRAY"`, `"SKIN"`, `"BEVEL"`, `"DISPLACE"`, `"SHRINKWRAP"`. Apply with `bpy.ops.object.modifier_apply(modifier="Sub")` with the object active, top to bottom.
- **Shader nodes by script**: `mat = bpy.data.materials.new("M")`, then `mat.node_tree.nodes` and `.links`. Nodes: `ShaderNodeBsdfPrincipled`, `ShaderNodeEmission`, `ShaderNodeMixShader`, `ShaderNodeTexNoise`, `ShaderNodeMapRange`, `ShaderNodeValToRGB` (Color Ramp), `ShaderNodeMix` (new Mix, set `data_type`).
- **Check before handing off**: render one still, open the PNG and read it. Check node-tree errors by `tree.nodes` having no node with `bl_idname == "NodeUndefined"`, and read the console for "Warning" lines.
- **Python deprecations**: DeprecationWarning lines for `use_nodes` are noise. Remove them by not setting it.

## Node editor habits

- **Node Wrangler**: Shift+right-drag adds reroutes, Alt+right-drag lazy connect, Ctrl+T texture setup (Texture Coordinate + Mapping), Ctrl+Shift+click preview a shader node, Alt+Shift+click preview a geometry node, F connects selected sockets by name. M mute, Ctrl+J frame, F2 rename, drag from a socket and release to search.
- **Groups**: Ctrl+G, Tab, N > Group tab to add and rename inputs (drag the empty socket), Item tab for label and name. Number button = users, press for single user. Shield = fake user. Append the node tree to other files and Save Startup File. Math Divide by 1000 gives fine control of a value.
- **`#frame` instant driver**: type `#frame` in any value field, divide for slower motion. Copy as New Driver and Paste Driver link two fields.

## Viewport and preference habits

- **Setup**: Save the startup file after deleting the default cube (File > Defaults > Save Startup File). Preferences > Navigation: Auto Depth, Zoom to Mouse Position, Orbit Around Selection. Raise undo steps. Matcap + Cavity (Both) viewport. Save Fake User for groups.
- **Selection**: L selects an island, the operator panel after Select Linked delimits by Material, Seam, Sharpness or UVs. Shift+G Select Similar. Ctrl+I inverts, H hides.
- **Edit many at once**: Hold Alt while changing a value to edit all selected objects (modifiers, lights, nodes, bone Deform).
- **Misc hotkeys**: Ctrl+F2 batch rename (find and replace, bones, materials, nodes). Type units into fields (7' 6"). Object > Link/Transfer Data > Copy Modifiers (Ctrl+L). Convert to Mesh applies modifiers. Alt-click Apply on a modifier applies many. Ctrl+1/2/3 Subdivision level. Shift+backtick fly mode. Duplicate Collection as backup.
- **Multiple versions**: Blender Launcher (free) runs alpha builds and several versions.
- **Cycles GPU**: Preferences > System > OptiX. Light Paths raise Transparent, Transmission and Total bounces when planes or glass show black blobs. Open Image Denoise in Render settings instead of compositor nodes.

## Add-ons, free vs paid

Check the licence and price before use, notes are from the videos and may have changed.

- **Free, bundled or one click**: Node Wrangler, Loop Tools (Circle), Modifier Tools (Apply All), Extra Mesh and Curve Objects, Bool Tool, Auto Mirror, Images as Planes, Rigify, Global Transform, A.N.T. Landscape.
- **Free third-party**: Wiggle Bones 2 (secondary motion), Simple Renaming Panel (bone suffixes), Text Effects (character sprites for ASCII), Commotion (offset animation, GitHub), Visualizer (audio bars, GitHub), BakeLab (baking), Sketchfab importer (model licences vary, check each), Mixamo and Mixamo-control, Rokoko Vision and add-on, Blender Studio rigs, BlockBlender free version, Poly Haven HDRIs and textures (CC0), Inkscape, MagicaVoxel, Google Fonts, Blender Launcher, Womp and Spline (browser).
- **Paid**: Scribble Gen (Gumroad, presets, see `geometry-nodes.md`), BlockBlender full, Eyek ($15 Gumroad or $20 Blender Market), Final Topology, Quad Remesher, Copy World Space (~4 EUR), Syncretic 3D Material Builder Suite, Draw Model / Clay Gun ($7), Lightning Pack, ASCII Art Generator, Glitch packs, Fire Shader pack, Affinity Designer. Joey's own Gumroad also has free node groups, a palette and a simple rig. Do not assume availability, the references reproduce the node setups.
- **BlockBlender (Minecraft blocks)**: Install: Preferences > File Paths > Asset Libraries > +, put the .blend in that folder, drag the "BlockBlender Importer" from the Asset Browser (or File > Append > Object), delete the importer. Model: scale, Ctrl+A apply all, Ctrl+J join, Geometry Nodes modifier > BlockBlender, Image = base-colour texture, Resolution 1 (in-game scale) to 0.1 to 0.2. Make Instances Real speeds the viewport. Image: Images as Planes, Subdivisions ~7, Resolution ~0.03, Exterior Thickness or extrude by one resolution, Delete Alpha 1. Text: Shift+A > Text, R X 90, Geometry > Extrude, convert to mesh. Palettes by UV (select all, scale 0, move the point to a swatch). Vertex colours: Use Color Attribute 1. Block counter: realize off, Instances ID in the spreadsheet or a Viewer node. glTF export: Convert to Mesh, UV attribute back to a UV map, plain Principled BSDF, Opaque, glTF with Selected, +Y Up, vertex colours off. Walk preview: F3 Walk Navigation.
- **MagicaVoxel pipeline**: Export PLY (clean topology, OBJ has overlaps), import Stanford PLY, M > By Distance, Color Attribute into Base Color, bake to UV for game use.

## Assets and sources

- Poly Haven and ambientCG: CC0 HDRIs and textures. Sketchfab importer: check each model licence, Sketchfab itself may need sign-in. Pexels free photos. Blender Studio free rigs. Polycam for photo scans.
- Nintendo Mii assets, converter tools and DeviantArt model rips were used only as references in the source videos, check licences before reuse.
- Off topic content in the source notes (CSS shapes, em and rem graphics, VCV Rack) was dropped from this skill.

## Hotkey and workflow tricks

- **Grow, shrink, invert selection**: Edit mode, Ctrl+Numpad+ grows, Ctrl+Numpad- shrinks, Ctrl+I inverts. Select More follows connected geometry.
- **Clear transforms and redo panel**: Alt+G clears location, Alt+R rotation, Alt+S scale. F9 reopens the Adjust Last Operation panel after you closed it.
- **View Selected and View All**: Numpad period frames the selection. A then Shift+C frames the whole scene and resets the 3D cursor.
- **Randomize Transform**: select the objects, Object > Transform > Randomize Transform (or F3). Set origins first. Example: Rotation Z up to 32 degrees, other fields 0.
- **Vertex parenting**: select the child, Shift+click the parent, Tab, select three vertices, Ctrl+P > Vertex (Triangle). The child rides the surface (droplets on leaves, bubbles on an egg edge).
- **Sculpt and view keys**: G Grab, V Draw, I Inflate, Shift+C Crease, S Smooth in the sculpt brush list. F resizes the brush and Shift+F sets strength. Shift+N recalculates normals when shading looks wrong. F3 finds Grid Fill, Smooth Vertices, Symmetrize and Bridge Edge Loops. With a Subdivision modifier, the Vertex view (on cage) button edits the smoothed shape. Camera focal length about 95 for character work.
- **Overlay toggle on Tilde**: Preferences > Keymap, search "context toggle", assign it to Tilde in the 3D View. F2 rename is the free "F2" extension.
- **Startup file without the cube**: delete the cube, File > Defaults > Save Startup File. Load Factory Settings undoes it.
- **Clean file for animation**: paste the rig into a new .blend, animate there, then File > Append the action into the main file and type its name in the Action Editor. Avoids viewport lag.

## Add-ons named in the later notes

- Free: Edit Mesh Tools (v0.3.6), Extra Curve Objects (v0.2.0), Extra Objects (Gears, Pipe Joints, Rock Generator), LoopTools, Node Wrangler (bundled, off by default), Rigify, F2. All from extensions.blender.org in 4.2+.
- Paid, never buy: Stylized Asset Suite and Stylized Suite, Windy Armature, Anime Ocean. The reference entries give the plain-node route.
