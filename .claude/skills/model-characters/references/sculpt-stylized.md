# Sculpt Stylized Characters

Sculpting route for cartoon, chibi, mascot and stylized-realistic characters, sculpting tutorials. Sculpt first, then retopologize or decimate when the character must animate or ship to an engine (see `base-mesh-and-box-modeling.md` and the `rig-characters` skill). Blender 5.x names: Dyntopo and Voxel Remesh are still in the Sculpt header; recheck any panel that moved.

Free sample file: "Cute Character Sculpt" on Gumroad ($0) shows the finished result.

- **[sculpting] Sculpt base: icosphere, voxel remesh and brush size/strength**: start a sculpt with enough geometry and control the clay.
  - Steps: Delete default objects (A, X). Add > Mesh > Ico Sphere, Add Ico Sphere panel Subdivisions 6 (for a UV Sphere sculpt: Ctrl+2 then Ctrl+A on the modifier to apply). Open the Sculpting workspace. R in sculpt mode drags the Voxel Size grid, click to set; Ctrl+R remeshes. Remesh again whenever faces stretch. Use less detail early. F drags brush size, Shift+F drags strength. Turn off pen-pressure size button to keep strength pressure. Turn off the "unified size" brush button when each brush needs its own size.
  - Use when / pitfalls: very high detail early is laggy and hard to shape. Remesh loses nothing without UVs.

- **[sculpting] Core brush hotkeys and the Ctrl-inverts rule**: the brush set used for characters.
  - Steps: G Grab (big shapes), V Draw, C Clay Strips (most common), Clay, Blob, Inflate (I), Flatten/Contrast, Scrape (flatten planes), Crease (Crease Polish for soft, Crease Sharp for hard), Snake Hook (Elastic variant, pulls limbs; large size, big drags may lower topology so Ctrl+Z), S Smooth. Hold Shift with any brush to smooth temporarily. Hold Ctrl with a brush to invert it: Clay Strips carves, Draw/Blob push in, Crease pinches out and sharpens an edge. Plus/minus button swaps add/subtract. Use Clay Strips with Ctrl for sockets and nostrils.
  - Use when / pitfalls: smooth sparingly or detail disappears.

- **[sculpting] Mask a shape, invert, pull out limbs with Snake Hook**: stubby arms and legs from a blob.
  - Steps: M mask brush, paint circles where limbs start, Ctrl+I invert mask (or Mask menu > Invert), Elastic Snake Hook with a large F-size, drag out and rotate. Alt+M clears the mask. Ctrl+R remesh then smooth with Shift and finish with Clay and Inflate rounding. Turn on X symmetry first so both limbs are masked.
  - Use when / pitfalls: forgetting the invert pulls the whole body.

- **[sculpting] Symmetry on, then off for the last details**: symmetrical base, asymmetrical finish.
  - Steps: Header symmetry button (butterfly) > X on mirrors sculpting across the axis. At the very end click X off for freckles, hair parting and asymmetry. Dyntopo and mirrored objects: a tongue sculpted without symmetry can be fixed with Symmetry panel direction (-X to +X) > Symmetrize (try the other directions if nothing changes).
  - Use when / pitfalls: switching symmetry off early forces redoing the other side.

- **[sculpting] Dyntopo for local detail**: add triangles only where you sculpt (freckles, ears, eyelids).
  - Steps: Header Dyntopo checkbox, accept the warning (UVs and similar data are lost), expand and set Detail Size (video uses 4 to 6; lower number = more detail; for Constant detail 12 is default). Ctrl+D toggles it. It switches off after leaving sculpt mode. Zoom far out and use a size of about 2 to sculpt a bump at fine detail from a distance. Turn off when done. Blender 4.x: Dyntopo lives in the Sculpt tool settings panel; 5.0 same place.
  - Use when / pitfalls: smoothing too much destroys the form; snake hook near low topology warps.

- **[sculpting] Sculpt setup: matcap, focal length 70, save increments, viewport helpers**: comfortable view for sculpting.
  - Steps: N panel > View > Focal Length 70 (50 is default). Viewport Shading dropdown > MatCap (a red or bright clay one shows form). Turn off the navigation gizmo. Use the period key (numpad) to centre on the stroke, or Alt+middle click to orbit around any point. Ctrl+S often; File > Save As, then `+` next to the name to increment (`head1.blend`). Preferences > Interface > Resolution Scale 1.3 and thin Line Width are cosmetic. Click -Y on the gizmo for front view; numpad 1 front, 3 side, 7 top.
  - Use when / pitfalls: pen-tablet back button can accidentally pull geometry; Ctrl+Z.

- **[sculpting] Stylized face build order and proportions**: carve a cartoon head with a realistic structure.
  - Steps: Start from sphere with Ctrl+2 applied. Grab brush to narrow sides and pull the jaw down. Clay Strips with Ctrl to carve eye sockets, flatten cheeks; add forehead, cheekbones, chin and jaw with Clay Strips. Draw brush for nose, Scrape to flatten planes, Crease around nostrils and smile lines. Brush Auto Smooth 0.1 helps soft forms but turn it off when carving in deep. Front view check; keep the face and mouth round (front of mouth forward, sides back). Proportions: eyes at the centre of the head height, about one eye width between the eyes, ears between eye top and nose base, directly behind the jaw. Eyelids wrap around the round eyeball, are thin, top lid sharper, bottom lid flatter; add the groove between nose and lip. Neck: drag clay down with Clay Strips and Snake Hook, thicker than it first looks. Always orbit while sculpting; check from far away. Use separate objects for hair (UV sphere, Grab to shape, symmetry off for a parting, Crease for strands, Scrape to flatten) so the face is safe.
  - Use when / pitfalls: skip fine anatomy for stylized work; keep ear inner and outer surfaces apart or the sculpt self-intersects.

## Modeling

- **[modeling] Add eyes, teeth and tongue as separate objects**: simple eyeballs and mouth inside a sculpted head.
  - Steps: Shift+C to centre the cursor. Eyes: Shift+A > UV Sphere, in edit mode G/S to place, R X 90 so the pole faces out, Shade Smooth, Alt+click and Shift+Alt+click loops to push the iris/pupil ring out, Ctrl+R loop cut for the iris edge. Mirror modifier with the head as Mirror Object. Teeth: Cube, loop cut at the centre, delete one half (wireframe Z, X > Vertices), Mirror modifier with Clipping, extrude faces back, Ctrl+2 Subdivision, add edge loops (Ctrl+R) to sharpen. Tongue: cube, Ctrl+2, loop cuts, 4 levels, Ctrl+A on the modifier to apply, apply scale (Ctrl+A > Scale) or sculpt brushes stretch, sculpt with Dyntopo and symmetry.
  - Use when / pitfalls: a scaled object in sculpt mode stretches strokes; always apply scale.

- **[modeling] Stylized eyebrows with Shrinkwrap, Mirror, Solidify and Subdivision**: eyebrows that stay on the face surface.
  - Steps: Add a cube, make it a flat plane by deleting front vertices (X > Vertices). Add Modifier > Shrinkwrap, Target = head (the video wrapped the sphere), raise Offset so it sits above the skin. Extrude (E) in edit mode to draw the brow. Add Mirror, then Solidify (set Thickness, adjust offset), Ctrl+2 Subdivision, Shade Smooth, same material as the hair.
  - Use when / pitfalls: put Shrinkwrap first in the stack.

## Painted-character sculpt progression

- **[sculpting] Head, hair mass, skin-modifier body, hands, then paint-over**: build order seen in a sculpt timelapse. Check: seen.
  - Steps: sphere (0:04); bald head with ink-drawn brows and eyes (0:05-0:07); hair cap as a faceted block (0:07), pulled into a long slab, strands cut in later (0:09-0:12); body from a Skin modifier mesh, torso blob then arm tubes (0:13-0:19); hand as a blunt mitten (0:20), then four fingers pulled out (0:23-0:25); both hands raised beside the face (0:26-0:28); clothing at 0:29; paint the viewport in Clip Studio Paint and project it back (0:30-0:36, caption "I paint over so I can use image projection"); then background, bracelets and pendant (0:37).
  - Use when / pitfalls: accessories come last; hair stays a smooth separate mass until strands are needed.
- **[sculpting] Placeholder objects and eye aim in a WIP head**: a food can sits on the head as a stand-in hat while the hair is unfinished (caption "Still have to do the hair"); a circle gizmo around one eye shows the eyeball being rotated to aim the gaze (guessed: separate eyeball object). Check: seen.
- Stage order for the whole illustration (sculpt is stage 2 of 6): `draw-and-paint-art` `references/illustration-process-2d-3d.md`.

- Finished pieces: the sculpt-to-paint pieces use a warm key against a cool fill and round faces with large eyes; the sketch before the paint-over is loose boxes for props and a clean face.
