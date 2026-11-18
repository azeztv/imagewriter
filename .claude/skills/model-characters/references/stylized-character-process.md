# Stylized Character Process: anime-semireal, painted and manga

Build order for a character that is finished by painting, not by geometry. The look is 2D-looking anime, semi-real painted or
manga hatching, rendered in EEVEE. Shading, outlines and the painted layers are in
`npr-shading-and-painted-look.md`. Rigs and animation belong to `rig-characters` and `animate-characters`. Blender 4.2+ and 5.x
names are used. Free extensions F2 and LoopTools come from extensions.blender.org since 4.2 (Preferences > Get Extensions).

<!-- skill-navigation:start -->
## Reading Map

- [Stylized Character Process: anime-semireal, painted and manga](#stylized-character-process-anime-semireal-painted-and-manga)
- [1. Presets](#1-presets)
- [2. Build order](#2-build-order)
- [3. Head](#3-head)
- [4. Body, hands and feet](#4-body-hands-and-feet)
- [5. Clothing](#5-clothing)
- [6. Face painting order](#6-face-painting-order)
- [7. Hair](#7-hair)
- [8. Creature and animal notes](#8-creature-and-animal-notes)
- [9. Design lessons](#9-design-lessons)
<!-- skill-navigation:end -->

## 1. Presets

Rows to add to the dials in `style-presets.md`. The values are his working habits, not hard limits.

| Preset | Geometry | Shading | Face and hair |
|---|---|---|---|
| Anime-semireal (painted portrait) | Ordinary quad mesh, topology "relatively decent". Sculpt need not be great: 85% of the work is texturing | Toon ramp, `Standard` view, key plus rim | Face between cute anime and semi-realistic. Flattened-front eyes, painted brows, hair as bevelled curves |
| Painted (semi-real, soft) | Same, with clothing folds modelled by bevel and puff | Toon ramp, painted darks and brights, per-scene colour | Painted layers on one skin material, sharp jaw, harsh red and dark shapes |
| Manga (hatching) | Same, hair as curves that crisscross | Bright grey base, scribbled darks, black outline, Fresnel rim x crayon | Black hair with white reflection shapes, hatched face |
| Low poly "AAA" | Simple shapes, no detail geometry | Painted edge lights and darks, lighting last | Face as a painted atlas region |

## 2. Build order

1. Collect inspiration boards, one per part: hair (front, side and back), face, upper clothing, lower clothing. Take one standout
 detail from each image. Do not copy one whole sheet.
2. Sculpt the body from a cube or a Skin modifier vertex skeleton: head, hands, feet, chest. Model or retopo over it. Source:
.
3. Base colour, then outline, then eyes, mouth and teeth, then eyelashes. Paint the face (section 6).
4. Hair as curves (section 7), then paint it.
5. Clothing blocked as ugly but readable shapes, then folds (section 5), then accessories.
6. Lights after colours. Texture first, lighting last. Expect the model to look worse right after the lights go in. Adjust the
 hair to react to the light. Do not stop.
7. Rig last (Rigify body plus hand-placed face, hair and eye bones). Pose the rig during detailing and fix what deforms badly.
8. Reuse the finished base mesh for the next character.

Alternate order for a full painted piece: cube, sculpt head, hands, feet, torso, model over it, paint blacks, reds and darks,
hair, robe, dress, flowers, branches, switch colours, draw shading, add patterns. Source:
.

Judge the render, not the solid view. Silhouette, colour and light matter more than topology. Check the silhouette with Viewport
Shading > Lighting: Flat.

## 3. Head

**Head from a subdivided cube** (anime base).
1. A, X to clear. Shift+A > Cube. Ctrl+3 subdivision, Ctrl+A on the modifier to apply. Sculpt mode, Grab (G), Symmetry X on.
2. Pull the bottom down. Flatten the sides of the head. Front view: contour goes down, in, flat at the chin. Make a forehead cliff
   and push the nose forward. Top view: narrower at the front, wider at the back.
3. Edit Mode, Alt+Z X-ray, delete the left half, Mirror modifier with Clipping, Ctrl+1 Subdivision (not applied).
4. Eye cavity: select six faces around the eye, right-click > Loop Tools > Circle, S to shrink, I inset, X > Faces, Alt+click the
   hole loop, E Y extrude back, E S scale in, F3 > Grid Fill. Anime eyes sit close to the nose and low.
5. Mouth: select four faces near the nose, I, S Z, delete the faces, Alt+click the loop, E Y back twice, Loop Tools > Circle,
   E Y, F to fill (an n-gon is fine), loop cut around the mouth for rigging.
6. Nose: select faces, I (B for boundary if it goes wrong). The top of the nose is narrower than the bottom.
7. Ear last: inset the side-head faces, E X out, R Z, two loops, shape in sculpt. The top of the ear lines up with the eyebrow.
8. Jaw: Draw Sharp brush (strength 0.6) to cut a depression between jaw and back of head, Smooth brush (S, 0.25), a little
   Crease (Shift+C) under the jaw, Draw at low strength to inflate. Outlines then read correctly.
9. Proportion fix: Shift+S > Cursor to Selected on the chest top, Pivot = 3D Cursor, scale the head with S. Ctrl+I inverts the
   selection to scale the body for a chibi. Camera focal length near 95 for character work. Low-poly copy: duplicate, remove
   Subdivision, add Smooth modifier (about 0.6, repeat 2), apply.

**Head from a sphere** (portrait): flatten the sides, extrude a jaw, cylinder neck, squashed UV sphere ear mirrored on X, then
sculpt eye cavity, nose, mouth corners, Cupid's bow and chin. Accuracy is not crucial. Female proportions: bigger eyes, smaller
nose, shorter face, smaller lips, thinner neck.

Eyes (cheap and stylized): UV sphere in the socket with Mirror, white material. Flatten the front with Alt+S in Edit Mode (important
for anime). Select the front circle for a second slot (cornea). Highlight is a small white plane or circle over the eye. Eyelash:
select a chain of vertices on the lid, Shift+D, right-click to cancel, P > Selection, Object > Convert > Curve, Bevel Depth, Alt+S on
points to taper. Do not forget to mirror it. Add small lower lashes. For a lid that overlaps the eye, bevel a vertex in the socket
(Ctrl+B, V) and inset.

Mouth: shape key between the closed rest and a slightly open pose with teeth. Model the tooth, tongue and lower teeth before
rigging the jaw. A mouth bag (extrude the lip edge inward until the sides snap, fill) gives an interior. Source:
. When the mouth
deforms, adjust the lip vertices so the painted lip line still fits. Source:
.

Expressions: shape keys. Close the eyes two ways (lid down, and lid up for the anime look) plus an eye-shrink key. Source:
.

## 4. Body, hands and feet

Source for all of section 4 unless noted:.

- **Setup**: install F2 and LoopTools (Get Extensions). Sculpt hotkeys: G Grab, V Draw, I Inflate, Shift+C Crease, S Smooth, F size,
  Shift+F strength. With Subdivision on, the Vertex "on cage" button edits the smoothed shape. Source:
.
- **Neck**: select a 4 by 3 patch of faces at the head bottom, Loop Tools > Circle, E Z Z down, G Y back.
- **Arms**: add a circle of 8 vertices with the 3D cursor off the origin, G X out, R Y 90, move to the shoulder, extrude into an
  A-pose, loop cut for the bicep, extrude the shoulder edge three times to meet chest and back, F to close. Bevel the elbow loop
  (Ctrl+B, scroll once for an extra loop) so rigging deforms well. More loops in the armpit.
- **Torso**: Alt+click the chest loop, S Z flatten, E Z down, G Y forward, extrude again for hips. F3 > Smooth Vertices with Mirror
  clipping on cleans up. Side view: chest in, back slightly out.
- **Legs**: two edges, F fill, loop cut, Loop Tools > Circle, E Z down, a bevelled loop at the knee, a calf bulge. Turn off
  Mirror clipping and merge when working near the centre.
- **Body from the Skin modifier**: plane, M > At Center, add Skin, Mirror (first in the stack), Subdivision. X-ray, extrude vertices
  for spine, legs, arms, fingers. Apply Skin, sculpt over the reference, fuse head and body with Boolean Union (Ctrl+A, delete
  the excess), retopologize starting at the lips and spiral out, denser at the eyes. Face island biggest in the UV, seams in
 armpits and back.
- **Hand from a cube**: Ctrl+R three loop cuts each way, select four faces, I twice, Pivot Individual Origins, S Y to even them,
  extrude fingers to palm length. Thumb: Alt+S to puff, R Y 45 so it hangs off. Arch the back of the hand with proportional
  editing. Join to the arm with Ctrl+J and F3 > Bridge Edge Loops. Source:
.
- **Foot**: cube, triangle side profile, four loop cuts, inset faces for the toes, big toe larger, pinky pushed back. Arch the foot.
 Join to the leg with Bridge.
- **Skin modifier fingers and toes**: select the hand-start vertex, Mark Loose, extrude four times for the palm, E up four times,
  Ctrl+A to scale the skin radius (hotkey unverified), spread the fingers. Apply Skin then Subdivision, re-add Mirror.

## 5. Clothing

Clothing comes from the body, not from a cloth simulation (he avoids simulation because it removes art control).

- Duplicate body faces: select faces, Shift+D, right-click to cancel the move, P > By Selection, Alt+S to thicken, new material,
  Solidify and Subdivision. Extrude down and loop cut for dresses. Sources:
.
- Folds by bevel and puff: bevel chosen edges, select the middle one, Alt+S to push along the normals. Inner folds on a jacket point
  up and turn horizontal going down. Knife then bevel also works. Model the big folds, paint the small ones. Sources:
,
.
- Draw shoes, trouser seams, wraps and accessories in the texture instead of modelling them. It avoids rig and export problems.
 Model only what must move, such as laces.
- Cargo pants: duplicate from the legs, extrude pockets. Pleated skirt: bevel many edge loops. Plaid: add two Wave textures.
  Sneaker: duplicate part of the foot, model sole, flap and laces over it. Sources:
.
- Asymmetry (one striped sock) and a silhouette change (blocky sweater, cut-off sleeves) add interest.
- Towel or soft cloth: cube with loop cuts, Subdivision with support loops, Displace with Clouds, curve it to the head. Source:
.

## 6. Face painting order

Faces are painted on a base mesh, not built from geometry. Layers and tools are in section 6 of the shading reference.

1. Base colour, then outline.
2. Eyeballs, white base. Paint the cornea and pupil first. It gives context for the other features. Pupil dark in the centre.
3. Eyelashes thicker on the outer side, crease above the eye in black.
4. Block the reds: under the eye, nose, lips (small upper lip, larger lower, follow the geometry). Reds shape the face.
5. Darkness over the reds, like top-down AO. Under the jaw, under the eye, jaw line, around the nose.
6. Eye makeup (black around the eye is the biggest single detail), eyebrows, jaw shadow, freckles, nostrils, eye fat blob.
7. Highlights: cheekbones, nose, lip centre, inner eye. Lower the overall face brightness so they pop.
8. Smile instead of neutral for interest. Take screenshots as you go.

Painted-skin phases (alternate order): blank colour, black outlines, main darks, freckles, highlights for shine, AO at the sides,
shadow areas more red, lighting kept very sharp. Painted style defines the jaw more than anime. Model the eyebrow instead of
drawing it so it is 3D.

Eyebrows as a transparent mesh: model the shape, make its material transparent, paint alpha less transparent in the middle and
more at the edges, then draw strokes.

## 7. Hair

- **Curves**: Add > Curve > Path. Add a Bezier Circle (or Curve Circle, resolution 4, shaped to a diamond or oval) and set it as
  Curve > Geometry > Bevel > Object. Mirror for symmetry, rotate around the model often, parent all curves to the head bone.
- **Scalp**: select head vertices, Shift+D, P > By Selection, give a dark hair-colour material, so no bald gap shows. Paint extra
 hair at low strength on it.
- **Texture-ready curves**: reduce the curve resolution, delete Mirror, Object > Convert > Mesh, re-add Mirror, turn off Fill Caps,
  unwrap in groups with seams along each side of every strand. Alt+Q in Texture Paint switches objects. Source:
.
- **Six-step anime-game hair checklist**: (1) silhouette: big curves with smaller ones around, one flat colour, check all angles;
  (2) shadow design: light from above, adjust until the shadow shapes look deliberate, bake them to a mask (plain route: bake AO
  and multiply it in, inferred); (3) gradient top to bottom; (4) draw speculars by hand: long at the sides, narrow in the centre;
  (5) colour variation root to tip at low strength, excluded from shadow areas; (6) accessories. Source:
.
- **Shape design**: clumps overlap and cast shadow shapes that look deliberate. Threshold the design to black and white. Use big
  strands for the form and small strands to complement. Many tiny strands look bad under light. Flip between front and side while
 building.
- **Colour**: base colour, AO dark where hair meets skin, highlights. Black hair gets thin white highlights in the centre, long at
 the sides. Bottom gradient (orange, or pale white).
- **Curly hair**: diamond-profile bevel, strongly tilted curve points, extra loops at the ends, bright-dark-bright-dark streaks
 along the strand.
- **Manga hair**: curves that crisscross and vary, because real hair is chaotic. Source:
.
- **Overlapping action**: give strands a curve in the direction of travel. When the head stops, the tail drags, then drag the end
  behind instead of rotating the whole hair. Shape keys also work (one pulls back, one follows through). Sources:
. Details belong
  to `animate-characters`.

## 8. Creature and animal notes

- **Frog**: bean body from a cube (extrude, tilt), limbs from Skin modifier planes, eye cavity by Alt+S, lumps pulled up, Crease
 around bumps, mouth slot ripped with V so it reads as a slight smile.
- **Dragon**: subdivision cage from a cube. Snout: back face G Y, front face S Z smaller. Mouth: loop cut, Alt+S to push in, V
  rip. Crease the nose edges with Shift+E so Subdivision keeps them sharp. Body from a bevelled Path curve, Alt+S with proportional
  editing for thick-thin-thick, flat belly. Flat planes (feathers) need Solidify limited to a vertex group so outlines work.
  Feathers and fur flaps are extruded from head edges. Head joins the body by extruding back faces over it like feathers. Source:
,
.
- Reference real animals and sculptures from several angles, and make many small proportion changes. Source:
.
- A plain white creature lifts with detail passes: black pattern marks, spots, belly scales, dark lines in shadow areas, redness near
 the eyes, outline everything.

## 9. Design lessons

- Observation over button pressing. Keep references open and compare value, colour and design all the time. Do not use image planes
 when you train design.
- Plan lighting and silhouette first. About 90% of the quality comes from them and they are hard to change later. There is no magic
 shader.
- Accessories help up to a point, then give overload. Test each one and remove it if it overloads. Source:
.
- Alternate two colours for a coherent theme. Use complementary colours (red and blue, red and green). Vary hue or saturation
 across clothing parts and keep values harmonious.
- Drawn-in detail beats modelled detail: fold lines, icons, shadows, outlines and whole accessories painted on, which also
 prevents rig intersections.
- Ugly phase check: clear focal point, good lighting, enough detail, too much detail anywhere that steals focus, side by side with
  inspiration. A piece looks good around 70% done. Rest a few days before the final look. Sources:
.
- Seven tips: crisp face forms, more than two light levels, relentless bright and dark contrast, know the style, reference
  board of fashion (flip it, zoom out), let it cook, compare only with images at your stage. Source:
.
- Five ingredients of stylized art: merge several references, light and colour contrast, gradients (stepped for anime), enough detail
 but not photoreal, variety in size and rotation.
- Raise the bar one element per project (animals, then characters). Source:
.
- Make a prototype for an hour of the piece you actually want to make rather than "simple first" projects. Source:
.
