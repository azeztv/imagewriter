# Acting, faces, shape keys and procedural motion

Face swaps, shape keys, blinks, mouth shapes, lip sync, and procedural wiggle or wind on loose parts.

<!-- skill-navigation:start -->
## Reading Map

- [Acting, faces, shape keys and procedural motion](#acting-faces-shape-keys-and-procedural-motion)
- [Shape keys for animation](#shape-keys-for-animation)
- [Shape key panel and mirroring](#shape-key-panel-and-mirroring)
- [Texture face swap with a bone driver](#texture-face-swap-with-a-bone-driver)
- [Blinks on a floating eye mesh](#blinks-on-a-floating-eye-mesh)
- [Eye and mouth swaps in 2D](#eye-and-mouth-swaps-in-2d)
- [Lip sync](#lip-sync)
- [Procedural wiggle and wind](#procedural-wiggle-and-wind)
- [Mechanical and prop animation](#mechanical-and-prop-animation)
- [Squash and stretch on props](#squash-and-stretch-on-props)
<!-- skill-navigation:end -->

## Shape keys for animation

- Select the mesh. Properties > Object Data > Shape Keys > `+` once makes `Basis` (the rest pose, never edit it for a
  pose). `+` again makes `Key 1`. Double-click to rename (for example `mouth closed`). Select the key, press `Tab`, move
  vertices, press `Tab` again, and drag the Value slider (0 to 1).
- Key it: hover the Value and press `I`. Yellow is keyed on this frame, orange is animated but not on this frame.
  Refine in the Graph Editor.
- Use for blinks, smiles, mouth shapes, wings and morphs.
- Topology rule: finish the Basis (modifiers and topology) before you add keys. Do not add or delete geometry after keys
  exist. A loop cut shows up in the Basis at its default position, and a deleted face disappears from every key. If you
  must change topology, edit the Basis first and re-check every key.
- A key's value must be 1 before you sculpt or edit it, or you see no effect. Sculpting a key works the same way: add the
  key, set Value 1, sculpt, return to Object Mode.
- Modifiers: Apply fails on a mesh with shape keys. Apply Subdivision or Array first.

## Shape key panel and mirroring

- The `X` button under the list resets all values to 0. The checkbox mutes one key. Lock icons stop edits. Range Min and
  Max clamp the slider (for example max 0.8). The pin shows poses in Edit Mode. The star (Solo) shows only the selected
  key. Lock all keys once the face is done.
- Dropdown menu: Delete All, Apply All, Make Basis, Duplicate Shape Key, Mirror Shape Key and Copy Shape Key to
  Selected. Mirror uses Flip Topology and needs a symmetrical mesh. Copy needs the same topology, so select the target last.
- Limit a key to a region with a vertex group: pick it in the field under the key's Value.
- Relative off gives one Evaluation Time slider that runs the keys in order (New Shape from Mix copies the mix). Face rigs
  keep Relative on.
- Face rigs tie shape keys to bones with drivers. Quick driver: `#frame` in a Value field.

## Texture face swap with a bone driver

For a cartoon or "Animal Crossing" style face drawn as flat texture cells. One bone slides to pick the cell. Source:
.

1. Give the face its own material slot named `face`. Duplicate the character material, select the face area, Assign.
   Apply the Mirror modifier on the head first so the face can be asymmetric.
2. Make a 1K image for the face. Unwrap with Project from View (front orthographic). Fit the face UV into the top-left
   cell of a 4 by 4 grid (island X 0.25). Use the UV Grid image while you set up, then switch back to blank.
3. UV > Export UV Layout. Paint the faces in Krita (free), GIMP or Photoshop on a 256 px grid (a quarter of 1K), one
   face per cell. Reload in Blender with `Alt+R` over the image.
4. Shader: a Mapping node after the texture coordinates (`Ctrl+T` with Node Wrangler). One Combine XYZ per face offset
   (Y offsets 0, 0.25, 0.5, 0.75, and X 0.5 for the right-side column). Chain Mix nodes (Vector) with A as the previous
   result and B as the next face. Drive them from one Value node through Math nodes set to Greater Than with thresholds
   1, 2 and 3.
5. Make a bone `face_select` in Armature Edit Mode (Roll 0, Z up, its own bone collection). Right-click the Value > Add
   Driver: object is the armature, bone is `face_select`, Local Space Z Location, expression `var * 10`. Add a Limit
   Location constraint (X and Y in Local Space) so the bone only slides up and down.
6. For separate eyes and mouth, duplicate the material slots (`eyes`, `mouth`) and assign each area.
   Duplicate the bone to `eye_select` and `mouth_select`, each with its own driver.
7. If you key the offset directly, set the keys to Constant interpolation, or the faces blend.
- With a bone, the face animates in the normal pose workflow, so the swap is one key per change.
- Free tools: Krita or GIMP for painting. Photoshop and Clip Studio Paint work the same.

## Blinks on a floating eye mesh

- Model the eyes as a separate mesh slightly in front of the face with its own texture (open and closed drawn side by
  side). A Mapping node offsets the UV between open and closed. Key the Mapping location and set the keys to Constant.
- Timing: hold the closed eye for 1 to 2 frames and open it fast. Blink on a head turn or at a beat, not at fixed
  intervals.

## Eye and mouth swaps in 2D

- Keep eyes on their own layer so facial parts animate independently (Krita: one layer per part). Swap mouth shapes from a
  mouth chart. Draw the face on each frame of a squash so it follows the shape. Rotate the face on two axes so it drifts
  to the visible edge and comes back for a turning head.
- Cut-out sprites: store the variants in one strip, then flip the Tile Offset and key it (see
  [2d-frame-by-frame-and-cutout.md](2d-frame-by-frame-and-cutout.md)).

## Lip sync

- Put the audio in the Sequencer. Turn on the waveform, Audio Scrubbing and Sync to Audio. Work in preview range.
- Mouth shapes as pose assets (Asset Browser in Pose Mode > Asset > Create Pose Asset), in their own action. Place keys 2
  to 3 frames apart and slightly early.
- Key the jaw and mouth first, then the cheeks and brows. Body acting goes in a separate action.

## Procedural wiggle and wind

- Noise modifier on a channel: small Scale for jitter, large Scale for slow wobble, small Strength. Restrict Frame Range
  and Blend In and Out to fade it. Details in [timing-and-graph-editor.md](timing-and-graph-editor.md).
- Wiggle Bones for floppy parts (bake them into a separate action so you can mute them).
- Wind on foliage or loose masses: add a Displace modifier with a Clouds texture (Size 6, Strength about 0.6, Direction X).
  Set Coordinates to Object with an animated Empty, and the noise slides as the Empty moves.
  Limit it with a vertex group so the trunk stays still. Key the Empty with Linear interpolation for constant drift.
- Lattice and shape keys for loops: use one lattice per layer. Key the shape key value side to side.
  Make the first and last values equal.

## Mechanical and prop animation

- A machine that rotates only at real joints: set the origin to each joint (`Shift+S` > Cursor to Selected, then Set Origin
  > Origin to 3D Cursor). Lock every channel except the joint axis (elbow only Y, wrist only Z).
  Parent in chain order, child first. Reset with `A`, `Alt+R`, `Alt+G`, `Alt+S`.
- Then animate like any object. Without limbs, show weight with timing, overshoot and the settle after the stop.
- Pick-ups: Child Of constraint with animated influence, and fix the jump with Copy Global Transform.

## Squash and stretch on props

- A bouncing prop: key the scale on the contact frame (wide and short) and the air frames (tall and thin). Keep the volume.
  Use a shape key or lattice for soft props. Use Free handles at the contact.
- A rigid prop only stretches in a cartoon style. Realistic styles show weight with overlap and the settle instead.
