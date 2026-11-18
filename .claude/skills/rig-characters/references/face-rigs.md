# Face rigs

Blender recipes for a quick face rig with bones, the easy mouth rig, the audio-driven puppet mouth and Shrinkwrap face bones are in
`use-3d-software/references/rigging-and-weights.md`. This file holds shape keys in full, the 2D face texture atlas and
the choice between the three methods.

<!-- skill-navigation:start -->
## Reading Map

- [Face rigs](#face-rigs)
- [Choose a method](#choose-a-method)
- [Shape keys](#shape-keys)
- [Shape key rules](#shape-key-rules)
- [Shape key panel](#shape-key-panel)
- [Mirror, copy and limit shape keys](#mirror-copy-and-limit-shape-keys)
- [2D face texture atlas driven by a bone](#2d-face-texture-atlas-driven-by-a-bone)
- [Blinking eyes on a floating eye mesh](#blinking-eyes-on-a-floating-eye-mesh)
- [Eyes and teeth as separate objects](#eyes-and-teeth-as-separate-objects)
- [Measured in the creator's shape key file](#measured-in-the-creators-shape-key-file)
<!-- skill-navigation:end -->

## Choose a method

| Style | Method |
| --- | --- |
| Anime, Animal Crossing, flat or low-poly with a painted face | 2D face texture atlas switched by a bone driver |
| Cartoon or realistic with smooth deformation | Shape keys, driven by bones for animators |
| Mouth that opens and shuts only | Jaw bone plus two lip bones, or one shape key |
| Mechanical or mascot head | Eye bones with Damped Track, separate eyelid meshes |

Shape keys survive glTF export. A texture atlas survives only if the engine can drive UV offset or material parameters.
Pick the method that the target engine can play. See `export-to-engines.md`.

## Shape keys

1. Select the mesh. Object Data > Shape Keys > `+` once. This creates `Basis`, the rest pose. Never edit Basis for a pose.
2. Press `+` again for `Key 1`. Double-click to rename it, for example `mouth closed`.
3. With that key selected, press Tab. Move, rotate and scale vertices. Press Tab again.
4. Drag the Value slider from 0 to 1 to blend. Type `0.5` for exact half.
5. Key the value: hover it and press I. Yellow means keyed at this frame, orange means animated but not on this frame.
6. Sculpt a key: set Value to 1, switch to Sculpt Mode, use Inflate or Grab. Nothing happens if the value is 0.

Face rigs tie shape keys to bones with drivers. Add Driver on the Value, Single Property or Transform Channel, Local Space,
expression `x5` or `x10`. A Range Min of -1 on a smile key gives a frown.

## Shape key rules

- Finish the Basis (modifiers, topology) before you add keys.
- Extruding inside a key leaves overlapping vertices in the Basis. A loop cut or a new object added while a key is active shows up
  in the Basis at its default position. Deleting faces deletes them from every key.
- To change topology, select Basis, press Tab, edit, then re-check each key.
- Modifier Apply fails on a mesh with shape keys. Apply Subdivision or Array first.
- Set the key Value to 1 before you edit or sculpt it. At 0 you see no change.

## Shape key panel

- X under the list resets all values to 0. The checkbox mutes one key. The lock icon stops edits ("active shape key is locked").
- Range Min and Max clamp the slider. The pin icon shows poses in Edit Mode. The star solos the active key.
- The down arrow menu: Delete All, Apply All (current pose becomes the mesh), Make Basis, Lock/Unlock All.
- Lock all keys when the rig is done. Use Solo to inspect one expression.
- Relative off gives one Evaluation Time slider that runs key 1 then key 2. New Shape from Mix copies the mix into a new key.
  Leave Relative on for face rigs.

## Mirror, copy and limit shape keys

- Mirror: make the key on one side with Proportional Editing (O). Duplicate it from the menu, set both values to 0, rename them
  `ear right` and `ear left`. Select the copy, then menu > Mirror Shape Key > Flip Topology. The mesh must be symmetrical.
- Copy to another object: select the source, shift-select the target last, menu > Copy Shape Key to Selected. The topology must
  match. Solo turns on after copying, so switch it off.
- Limit a key to an area: make a vertex group, Assign, then pick the group in the field under the key Value.

## 2D face texture atlas driven by a bone

Use it for anime, Animal Crossing and low-poly looks. The face is a texture. A bone slides the UV across a grid of expressions.

1. Apply the Mirror modifier on the head so the face can be asymmetric.
2. Duplicate the character material, name it `face`. In Edit Mode select the face area and Assign.
3. Make a new 1K image. Unwrap the face with Project from View (front orthographic). Fit the UV into the top-left cell of a grid.
   Split the texture in 4 rows and columns so each face is 0.25 apart. Use a UV Grid image while you set up, then a blank image.
4. UV > Export UV Layout. Paint the faces in Krita (free), GIMP or Clip Studio Paint with a 256 px grid (a quarter of 1K).
   Copy a face one cell down, snapped to the grid. Reload in Blender with Alt+R over the image. Hide the UV layout layer first.
5. Shader: add a Mapping node (Ctrl+T with Node Wrangler on the image texture). Use a Combine XYZ node per face offset
   (Y = 0, 0.25, 0.5, 0.75, and X = 0.5 for the right column). Chain Mix nodes (Vector): A is the previous face, B is the next.
   Drive them from one Value node through Math nodes set to Greater Than with thresholds 1, 2 and 3.
6. Make a bone in its own bone collection: Shift+A in Armature Edit Mode, Roll 0, Z up, name `face_select`.
   Right-click the Value > Add Driver: object = the armature, bone = `face_select`, Local Space Z Location, expression `var * 10`.
7. Add a Limit Location constraint (Local Space) on the bone so it slides only up and down. Cap Z if needed.
8. Split eyes and mouth: duplicate the material slots as `eyes` and `mouth`, assign each area, then make `eye_select` and
   `mouth_select` bones with their own drivers.

If you key the Value directly, set the key interpolation to Constant so faces do not blend. A bone lets you animate the face in the
normal pose workflow. In Godot or Unity the same idea is a UV offset or frame-index parameter on the face material.
Mapped from the Blender 5.x Mix node (Vector type): older tutorials call it MixRGB.
2D hand-drawn animation uses the same idea as a mouth chart for lip sync.

## Blinking eyes on a floating eye mesh

- Model the eyes as a separate plane slightly in front of the face with its own texture (open and closed drawn side by side).
- Offset the UV with a Mapping node Location. Key the Mapping location and set the interpolation to Constant.

## Eyes and teeth as separate objects

- Eyes: UV sphere, R X 90 so the pole faces out, Shade Smooth, push the iris loop out with Alt+click, Ctrl+R for the iris edge.
  Add a Mirror modifier with the head as the Mirror Object. Without a Mirror Object, Mirror uses each object's own origin.
- Two materials on one eye: `eyes white` and `eyes black`, Roughness 0 on both. Select the iris loops and Assign the black slot.
- Apply scale on every object in sculpt mode, or brush strokes stretch.
- Eyebrows: a flat plane with Shrinkwrap first in the stack (Target = head, raise Offset), then Mirror, Solidify and Subdivision.
- Parent loose eyes, teeth and brows to the head DEF bone, or weight them 1 to the head bone.

## Measured in the creator's shape key file

free "Monkey Expressions Shape Keys" file shows the two ways to split shape keys:

- Per part, combined at animation time: `Ears Size`, `Mouth Closed`, `Mouth Circle`, `Mouth Sad`, `Nose Size`,
  `Eyes Size`, `Eyes Move Left/Right/Up/Down`. Flexible, more keys to animate.
- Whole expressions: `Sad`, `Happy`, `Angry`, `Asleep`. Fast to animate, no mixing between parts.

Both sit on a Subdivision Surface mesh, with the shape keys on the base mesh under the modifier.
