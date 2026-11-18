# Modeling

Edit-mode craft, modifiers, characters, props, sculpt tips. Hotkeys are default Blender.

Reading map
- 5.x names: read first
- Setup and habits: origin, scale, reference, edit-mode hotkeys
- Skin modifier characters
- Box-modelled characters and parts
- Props and objects
- Procedural and modifier forms: cloud shapes, grids, landscapes, pumpkins
- Sculpt notes
- Tools: Clay Gun, particles and rigid body

## 5.x names

- Auto Smooth (Object Data > Normals) was removed in 4.1. Use the Smooth by Angle modifier (Add Modifier > Normals) or Shade Auto Smooth on the Shade menu. Alt+click Auto Smooth on all selected becomes adding the modifier to all.
- Mean Crease is N > Item > Mean Crease, Shift+E scales edge crease.
- Loop Tools, Modifier Tools, Extra Objects, Bool Tool, Auto Mirror: from 4.2 enable them via Preferences > Get Extensions (bundled add-ons). Modifier Tools adds Apply All.
- Apply Modifier on a curve fails, use Convert to Mesh.
- Subdivision Surface keyboard Ctrl+1/2/3 unchanged. Optimal Display is a checkbox on the modifier.
- Mirror: tick Clipping, Mirror Object, Bisect, Flip as before.
- Remesh modifier, Voxel Remesh Shift+R in sculpt unchanged.
- Particle hair and Particle System > Convert still work. New Curves hair exists beside it (see `geometry-nodes.md` fuzz and fur).

## Setup and habits

- **Origin-at-the-bottom primitive**: Shift+A cube, Tab, G Z 1 Enter so origin sits at the base, Tab. Snap with Face Project and Snap With Center, hold Ctrl on G. Isolate with `/`.
- **Apply scale**: Ctrl+A > Scale before modifiers read it. Unapplied non-uniform scale stretches Bevel, Solidify, Generated and Object coordinates and breaks armature binding. Scale in Edit Mode to avoid it. Do not apply for squash and stretch animation. Check N > Item scale = 1 when modifiers look wrong.
- **Reference image in the viewport**: Drag the image in (Object Mode), Alt+G, Alt+R, rotate X 90, Object Data > Opacity low, scale. Lock it via Outliner filter > selectable toggle. Alt held toggles opacity on all.
- **Beginner edit-mode toolkit**: Setup: Cavity on, MatCap, raise undo steps, enable Loop Tools. 1/2/3 modes, E extrude (E then S), Alt+E menu (along normals, individual, spin), Ctrl+click extrude to cursor, Ctrl+B bevel (scroll segments, C clamp, V vertices, Ctrl+Shift+B vertex bevel), I inset (twice = individual, B boundary), Ctrl+R loop cut, G G slide (Alt extends, E copies neighbour loop shape, F flips side), Alt+click loop, Ctrl+click shortest path, L linked, K knife, Bisect, Poly Build, Spin, Alt+Shift+S To Sphere, Alt+S Shrink/Fatten, Ctrl+Alt+Shift+S shear, X delete, Ctrl+X dissolve, F fill, Ctrl+F Grid Fill, J join vertices, M merge (At Center, By Distance), P separate (Selection, Loose Parts), Ctrl+J join objects (active keeps origin), right-click Poke, Triangulate, Tris to Quads, Bridge Edge Loops or Faces, Edge Split, O proportional (Connected Only, Sphere, Sharp), period pivot (Individual Origins, 3D Cursor), Shift+S cursor, Alt+N normals, Face Orientation overlay (red = inside out), F3 Flip Normals, Shift+G Select Similar, Ctrl+Numpad+/- grow and shrink, Select > Checker Deselect. Modifier order matters, apply top to bottom, Mirror with an Empty as object, Simple Deform Bend. Quads loop-cut cleanly, n-gons do not.
- **Navigation and transforms**: Numpad 1/3/7, 5 persp/ortho, Numpad. focus, 0 camera. G/R/S then X/Y/Z, Shift+axis excludes, XX local, type numbers, Ctrl snap, Shift precise, Alt+G/R/S reset, Shift+R repeat, Shift+D duplicate, Alt+D linked, Alt edits a value on all selected. Affect Only Origins or Set Origin. Ctrl+P parent (Keep Transform), Alt+P clear, [ and ] parent and children. Randomize Transform in F3.
- **Snap to ground**: Snapping > Increment > Absolute Grid Snap, hold Ctrl while moving. S Z 0 flattens first.

## Skin modifier characters

- **Skin base (merged recipe)**: Plane, Tab, M > At Center to one vertex. Modifiers: Mirror (Merge Distance 0.1, Clipping optional) > Skin > Subdivision Surface (viewport 2). Alt+Z X-ray. E extrude the skeleton, Ctrl+A scales radius (Ctrl+A then X or Y one axis, or N > Item Mean Radius). Mark Root on every disconnected piece (hip or chest). Loop cut then Ctrl+Shift+B vertex bevel (3 cuts) adds volume. Hands: from the wrist extrude a fork, three fingers and thumb on X, scale the hub up, subdivide for knuckles. Shade smooth is the checkbox inside the Skin modifier. Skin cannot rotate points. Subdivision placed before Skin causes scale errors. Duplicate and hide an unapplied copy. Apply Skin before UV or texture work. Create Armature button: apply Mirror first, clean bones. Delete the edge between two verts for two separate pieces.
- **Stylised ghost**: Skin from one vertex, Mirror, Subdivision (3), X-ray, Normals MatCap. Ctrl+R extra points, flatten fingers S X 0, Mark Root on the chest. Apply Mirror, Create Armature, apply Skin, Ctrl+2. Delete half, Mirror above Subdivision, inset eyes (I, B), mouth, extrude along Y with Clipping on.
- **Separate limbs and tail**: Select the vertex carrying the root, Shift+D, P > Selection. If Mirror misbehaves set Mirror Object to the head. Origin at a joint: Shift+S Cursor to Selected, Set Origin > Origin to 3D Cursor. Tail: Loop Cuts, Proportional Sharp, origin at the tip, Simple Deform Bend with Active Element pivot.
- **Skin body into clothing**: Apply Skin, Ctrl+R and scale for sleeves and cuffs, Mean Crease 1. Pants: lower Subdivision levels, apply, add new Ctrl+2. Ruffled sock: scale loops out with Shift+Z, drag random loops down, Connected Only.
- **Skin worm**: Plane, merge top and bottom vertices to a line, Ctrl+R ~19 loops, Skin, Ctrl+A radii, Smooth Shading in the Skin modifier.
- **Skin skeleton and skull**: Cube Subdivision, To Sphere, Mirror above Subdivision with Clipping. Teeth: S Z flatten, Alt+E Individual Faces, Mean Crease 1. Sockets: inset (B), Loop Tools Circle (Clipping off), Normal orientation, extrude inward.
- **Hair, cane, accessories from skin**: Extra Objects "Add Single Vert", extrude, Subdivision, Skin, second Subdivision after. Skin needs manual shade smooth and must be applied before UVs.

## Box-modelled characters and parts

- **Face box modelling with loops**: Cube, Ctrl+R loops (brow, middle, cheek), Ctrl+B for a centre loop, inset eyes, vertical loops, inset mouth and nose, Loop Tools Circle for eye loops, Subdivision, delete half and Mirror (Clipping on). Edits: O Connected Only, Alt+S, G G, To Sphere. Eyes: UV sphere rotated 90, Mirror Object = head, Face Project snapping. Alternatives: Multires + sculpt, Shrinkwrap a cube onto a reference head.
- **Chibi from a cube**: References Alt+G, Alt+R, X 90, ~1 m, lock in Outliner. Cube, Ctrl+3, X-ray, Ctrl+R and scale (Shift+Z excludes Z). Shift+D then apply for a smooth shape. Mirror above Subdivision, Clipping on. Face: inset (B), E Y. Mean Crease 1 sharp, 0.4 soft, Alt+click loops.
- **Scarf with Shrinkwrap Outside + Solidify**: Cube without top and bottom, Subdivision 2, Shrinkwrap (Target body, Outside), Solidify (Offset 1, 0.03), Subdivision 1. Duplicate for layers. Tails: plane, Face snap with Align Rotation to Target and Ctrl.
- **Eyes, eyelids, nose, brows**: UV sphere with Mirror (Mirror Object = body), Origin to Center of Mass. Eyelids: select half, Shift+D, P, Solidify offset 1 + Subdivision. Brows: plane, Solidify offset 0, Bevel before Subdivision. Nose: cube in the mirror with Clipping, inset nostrils. Mirror first in the stack.
- **Gardener from a base mesh**: Append the base collection (Alt+G). Reshape with Mirror object = head. Shoes: duplicate leg, delete geometry in Edit Mode (keeps modifiers), Solidify 0.005. Pants: duplicate body, apply Subdivision, delete upper faces, Solidify, Shift+D for belt, Alt+E along normals. Buttons snapped (Face, Median, Ctrl). Shirt: Solidify offset 0, Edge Split plus Sharp proportional for a collar. Eyes with a Lattice modifier, parent to the lattice, Mirror before Lattice. Bucket and rake via Skin (scale Y 0 for flat). Apply Skin only after the Subdivision above it.
- **Old guy parts**: Shoe from a cube moved up 1 m: toe loops, delete top face, S Y 0 flatten, Edge Split heel, F, inset sole, Solidify before Subdivision. Glasses: plane X 90, Solidify, tiny Bevel, Mirror (Mirror Object = head). Mustache: origin at top, Solidify before Subdivision, Mirror. Hat: inset, extrude, Loop Tools Circle. Hair strip: Subdivision + Shrinkwrap (offset 0) + Solidify (0), apply, pull spikes. Collar: delete faces, Circle, extrude Z. Cane: Skin. Apply scale first.
- **Five base meshes from a sketch**: Drag the PNG in, Alt+G/R, X 90, 3D Cursor pivot, ~2 m tall, feet on 0, apply, lock. Head: Cube, Subdivision 4. Arms: plane, At Center, Mirror (merge off), Skin, Mark Root at the shoulder. Hand flat for easier rigging. Duplicate Collection for the next character.
- **Cat from cubes**: Apply Subdivision on a cube first, then loops. Ears: inset, Loop Tools Circle, extrude, Alt+S. Nose and mouth: plane X 90, Solidify (offset 0, above Subdivision). Eyes: plane + Mirror (Mirror Object = head) + Shrinkwrap on top. Whiskers: inset, Alt+E along normals, crease. Coat: duplicate body, lower subdivision one level, apply, Solidify top. Convert to Mesh with all selected applies modifiers.
- **Cartoon shoe, vest, hat, eyelid**: Eyelid and hat: Ctrl+Numpad+ to grow, Shift+D, P > Selection, Solidify above Subdivision. Vest: cube Ctrl+4, delete top and bottom, loop cut and bevel, inset B for arm holes. Shoes: cube, Mirror (merge off), extrude toe, delete top, cuff scaled and dropped for a lip, S Z 0 flat sole, Alt+E + crease for sole edge.
- **Mouth pocket and lips**: Apply the first Subdivision, add another, Mirror on top. Inset (B), move down, Mirror off, E Y in, S Y 0, loop cut, delete inner faces, extrude lips along Y, Mean Crease up to 1.
- **Werewolf**: Cube + Subdivision + Mirror, snout via loops and E Y. Duplicate, hide, apply both, delete half, re-add. Ears: extrude Z, scale. Fur spikes: Alt+E Individual, Individual Origins. Eyebrows: Solidify 0 + Bevel (Arc). Hands: plane + Mirror, Loop Cut, Edge Split, knuckles Ctrl+R with 5. Shorts: Mirror, delete top, Solidify, Edge Split hem.
- **Boba girl**: Append base collection. Hair: duplicate head, apply Subdivision, delete half, Mirror, Solidify out, Subdivision, Shrinkwrap, apply top to bottom. Bun: Cube + To Sphere + Loop Tools Circle. Earring ring: inset and delete, Ctrl+P to the ear. Cup: Mean Crease, rings, Solidify, straw from an inner edge ring. Liquid: duplicate cup, delete outside, Ctrl+F, Face Orientation, scale slightly to avoid z-fighting.
- **Witch**: Cube Ctrl+2 + Mirror for hips, legs from a plane (Clipping off), fix inside-out faces (Face Orientation, Flip Normals). 3D Cursor pivot with S Z 0 flattens to the floor. Mean Crease for boots and hat tip. Hat Simple Deform Bend with an empty parented to the hat. Cloth skirt in `effects-fx.md`.
- **Low-poly human, mitten hands**: Cube torso, extrude neck, arm and mitten hand with thumb, loop and bevel at elbow, knee, foot, Absolute Grid Snap. Delete half in X-ray, Mirror, Ctrl+A location. Select the centre loop and scale to round.
- **Car character from memory**: Cube, subdivide x3, loop cuts for a pillowy hood, Ctrl+click shortest path mouth, Fill + Circle, Alt+E headlights, wheel from a cylinder (apply scale and rotation), Alt+D linked, mirror across cursor with S X -1.
- **Topology for deformation**: Edge mode Alt+click a loop, Ctrl+X dissolve. Inset the 3 outer elbow or knee faces, X-ray, G G halfway. More verts outside, fewer inside. 3 loop cuts on clothes and limbs, matching loop counts between clothes and limb. Round with Alt+S. Duplicate Collection as a backup. Final Topology (paid) adds loops without shape change.
- **Cleanup for rigging**: Render Properties > Simplify > Max Subdivision 0 shows base mesh. Straighten bent arms, Bevel at elbows and knees. Match density by lowering Subdivision levels, apply, Ctrl+2. Feet following the head: clear Mirror Object, cursor to world origin, Origin to 3D Cursor, apply rotation.
- **Floating parts joined by custom normals**: Vertex group weight 1, Vertex Weight Proximity, Displace, Shrinkwrap and Data Transfer (Face Corner Data > Custom Normals) all targeting the other object with the inverted group, Target Geometry, Falloff Smooth. Same material and density help.

## Props and objects

- **Cafe props (box recipes)**: Crate: inset individual, poke faces, inset, Alt+E along normals. Building: loop cuts + bevel, Alt+E trim with offset even. Lamp, table, vase: 16-vertex cylinder, E and S, bevel top loop. Mug: bevel bottom, inset thick, bevel rim loops with C, handle by extruding side faces, shear (Ctrl+Alt+Shift+S, 1), bridge, Mean Crease. Flower: petal plane, five copies, 3D Cursor pivot R Z 72 then Shift+R. Apple: cube + Subsurf over reference, Sharp proportional, random nudges. Espresso machine: subdivide x3, Loop Tools Circle, extrude spouts. Bike: thin box with Normal orientation, Bridge for bars, Mirror Y with Bisect and Flip, wheel by circle + Wireframe modifier for spokes, gear by Checker Deselect + X.
- **Pumpkin by poly modelling**: Circle 36 verts, Ctrl+3 level 3. Extrude, top and bottom loops, X-ray, E then S, centre loop scaled out. Crease every third loop: select one loop, skip two, Shift+click, Ctrl+Shift+Numpad+, Select Loops > Edge Loops, Mean Crease 0.5. Close with S Z 0 + Ctrl+F Grid Fill (span ~10, offset 4). Stem with creases, Ctrl+Plus then P > By Selection, parent, scale ~0.3, apply.
- **Pumpkin by Displace ridges**: Plane + Subdivision, extrude profile. Displace strength 0.1, Mid Level 0, Blend Radial texture, Color Ramp Constant with alternating stops (one white per ridge), switch to Ease. Mask the stem with a vertex group in the Displace field. Second low Displace for irregularity.
- **Screw lathe**: Plane > Merge at Center on the axis (Absolute Grid Snap + Ctrl), extrude the profile, Screw (resolution 64), Subdivision above Screw.
- **One-segment Array around an Empty**: Circle 12 verts rotated 360 / (2 x ridges), extrude and scale, keep one face. Empty rotated 360 / ridges. Array Relative off, Object Offset = Empty, Count 12, Merge, First Last. 3D Cursor pivot at origin.
- **Array with individual rotation**: Array Object Offset with an Empty that has Copy Rotation of the arrayed object (Mix After Original).
- **Curve taper and bevel object**: Path curve with Taper Object = Bezier profile and Bevel Object = Circle. Ridges: subdivide circle by 5, Checker Deselect, scale. Hook to New Object for deformers. Taper cannot overhang.
- **Carving (Boolean, SVG, photo)**: Solidify (offset 1, 0.02). Destructive: apply Subdivision, circle select, vertex group, X, Smooth restricted to that group. Knife: K shapes, Edge Split, L, X. SVG: File > Import > SVG, Origin to Center of Mass, R X 90, Convert to Mesh, Solidify, Boolean (Fast, switch to Exact if broken), cutter shown as Wire. Photo: plane in front, Subdivision 6 then apply, Displace with Image texture driven by an Empty, Extension Clip, Shrinkwrap Project Y offset 0.005 then apply, Displace direction Y strength 0.02 to 0.1, Solidify before Displace, Boolean. Booleans crash so save first.
- **Pickle jar**: See `effects-fx.md` for glass and liquid. Pickle: cube with loops, Subdivision, Simple Deform bend, Displace Clouds, Displace Voronoi (inverted, Ease).
- **Hex and triangle tunnel**: See `animation-and-nla.md`.

## Procedural and modifier forms

- **Cylinder grid (2.90)**: Plane, subdivide 3x, Edge Split, Select Random, subdivide, repeat. Bevel (vertices, 50%, segments 10), Solidify, Weld after Bevel, second Bevel optional. P > By Loose Parts, Randomize Transform Z ~0.026. Camera focal ~100. Second Solidify for hollow glass (Cycles).
- **Abstract cloud shapes (2.90)**: Plane, origin in corner, subdivide 19. Decimate (Planar), Bevel (Vertices 0.05, segments 8), Weld (0.05), Solidify 0.1. Select faces with C, Shift+D, P > Selection. Edge Split fixes diagonal artifacts.
- **Greeble with modifiers (2.9)**: Plane > Subdivision (Simple, 6) > Displace Voronoi (Chebychev, size 0.5, strength 0.1) > Decimate Planar > optional Wireframe. Pieces: apply all, Edge Split, Extrude Z, P > Loose Parts, Origin to Center of Mass Volume, Randomize Transform, Ctrl+J.
- **Landscapes with Displace**: Plane x10, subdivide ~50, Subdivision above Displace. Displace Clouds, Object coords with an Empty, Mid Level 0. Weight-paint mask. Plateau: Color Ramp Ease or B-Spline. Canyon: negative strength. Dunes: Wood Band Noise. A.N.T. Landscape add-on is another route.
- **Displaced bands loop**: See `animation-and-nla.md` loops.
- **Voxel import cleanup**: Export PLY from MagicaVoxel (OBJ has overlaps), import Stanford PLY, M > By Distance first, Origin to 3D Cursor, Alt+G. Separate limbs in MagicaVoxel if joints must not bend.

## Sculpt notes

Full sculpting craft, the 5.x toolset, retopo, bake and the check script: the `sculpt-models` skill.

- **Sculpt workflow**: Poly model the base with Skin and subdivided boxes, then Dynamic Topology and Grab or Snake Hook for big shapes, Draw and Inflate for bulbs, Clay Strips flat (Ctrl subtracts), Crease between, Smooth with Shift (Mode Surface cleans topology). Voxel Remesh Shift+R. Mask, invert, draw to pop details, smooth afterwards. Make toppings and eyes separate objects. Remesh dense meshes before Dirty Vertex Colors. Sculpt in perspective. Alpha brushes for surface texture. Multires + Radial Symmetry 12 for ridges. Alt+D linked instances save memory.
- **Speed modelling practice**: Time-boxed household objects, big shapes first, details later, textures last.

## Tools

- **Pile of objects with particles and rigid body**: Cube emitter, Particle Source = Volume, hide emitter, Frame End 1, Distribution Grid, Render As Object or Collection. Ground Rigid Body Passive, friction 1. Convert on the Modifier tab, M to a collection. Active Rigid Body on one object (friction 1, damping 0.5), Copy from Active, play, then Object > Rigid Body > Apply Transformation and Remove. Apply before removing or objects snap back.
- **Clay Gun / Draw Model (paid, $7)**: Put the .blend in an asset library, drag in with Append. Draw with Surface or cursor depth, vertex colours, negative brush cuts, Grease Pencil to Mesh then rig, Quad Remesh for topology.
- **Womp (browser SDF modeler, not Blender)**: Positive and negative shapes, Goop Strength, Union and Subtract groups, Ctrl+Shift+M mirror, transparent render.
- **Spline 3D (browser, not Blender)**: Low-poly scenes with states, events, Bloom, public URL.
