# Head, Face, Eyes and Hair Shell

Read this whole file before modelling a head. It exists because a box head with a flat face quad looks ugly, and the series never builds one.

<!-- skill-navigation:start -->
## Reading Map

- [Head, Face, Eyes and Hair Shell](#head-face-eyes-and-hair-shell)
- [1. What the head is](#1-what-the-head-is)
- [2. Face relief patch steps](#2-face-relief-patch-steps)
- [3. Hair shell that frames the face](#3-hair-shell-that-frames-the-face)
- [4. Painted face texture](#4-painted-face-texture)
- [5. Eye options](#5-eye-options)
- [6. Face proportion check](#6-face-proportion-check)
- [7. Hood and other head accessories](#7-hood-and-other-head-accessories)
<!-- skill-navigation:end -->

## 1. What the head is

In the series the head is one object made of three parts (Part 5 joins them with Ctrl+J):
- A hair shell: a cube with the bottom face deleted, covering top, sides and back of the skull.
- A face relief patch: one knifed plane, pulled into 3D in the side view. It has a pointed nose, a brow, steps at the cheek and a jaw edge.
- A few under-jaw faces mapped to the shadow colour.

There is no skull box and no bare box edge. Hair bangs and side triangles frame the patch ("the rest just gets filled in with hair"). Eyes and mouth are painted on the patch texture (Part 7) and only become geometry in the optional eyes rig.

## 2. Face relief patch steps

Source: Part 4. The series gives no vertex count, so count from the reference. A reference face usually needs about 30 to 45 vertices per half.
1. Plane, rotate X 90, front orthographic, X-ray, scale it onto the reference face.
2. One vertical loop cut at the centre, delete the half, add Mirror (Clipping on).
3. Knife (K, click edge, click edge, Enter) only where the drawing shows an edge: eye line, nose, cheek step, mouth line, jaw. Move the vertices to match the drawing. Dissolve edges that are not needed so faces are quads.
4. Front view alone is not done. The patch is flat until the side view is matched. In side view move rows with G Y: nose tip out first, then brow and chin, then pull the temple, cheek corner and jaw corner back so the profile is a rounded triangle with a nose point.
5. Merge doubled vertices (Merge At Last). Fix mirror holes by sliding the vertex on X until it welds.
6. Under-jaw: knife the jaw edges in solid view, extrude backward toward the 3-vertex neck, fill with F.
7. Compare both views against the reference with X-ray on, then orbit in solid view. Nose slightly bigger and pointier reads better.
8. If a source model exists (The Models Resource, Mega Man Legends), import it and copy its topology.

Fault to avoid: a rectangular quad with a cuboid behind it. Check a three-quarter view. If the patch looks like a mask on a block, push cheeks and jaw back and add the nose point.

## 3. Hair shell that frames the face

Sources: Parts 5 and 6, finale (hair is the hardest part).
1. Cube, delete bottom face, one loop cut, delete half, Mirror. Add loop cuts to give a raised centre ridge and sloped planes like the drawing. Fit it in front, side, top and back views. The top view must not be a flat plane, and corners step inward.
2. Raise the hem to where the bangs start.
3. Ctrl+J it with the face patch. Bangs and locks: extrude hairline edges, move forward, extrude an edge and M At Center to a tapered tip, F to fill triangles. Keep the whole hair to roughly 90 to 160 triangles. Few big triangles beat many blocks.
4. Back spikes: extrude edge, extrude face, M At Center. Centre vertices at X 0.
5. Apply the Mirror, then move bangs by hand so left and right differ.
6. Hair is chunks that follow the drawing: hairline, side locks beside the cheeks, nape. If the hair looks bulky, the chunks are too thick or too many. Thin each chunk to the drawn silhouette, taper to points, never leave rectangular ends.
7. A hairstyle is hard. Source a reference model or kit before inventing one.

## 4. Painted face texture

Source: Parts 7 and 11, eyes video.
- Face UV: select face patch faces, Project from View in front orthographic, scale the island in the UV editor until the bottom of the 3D nose lines up with the nose shadow on the art. Under-jaw faces go into the shadow colour.
- Never project from a harsh angle. Zero or small camera tilt, then fix distortion by moving UV vertices.
- Face texture size, measured in the creator's own files (Love-chan, Juliet, Astolfo, Teto): the face always has its own material and sheet, apart from the body sheet. Love-chan uses a 1024x209 strip, Juliet a 1024x1024 sheet of 3x3 expression cells (about 340 px each, face island about 290 px wide), Astolfo a 1024x1024 sheet of 5 cells of about 410x305 px plus brow, blush, iris and teeth strips, Teto 2048 plus a mouth sheet. Expressions swap cells, so the body sheet never changes.
- Paint on the flat colour pass first, then add the face. Make the UV before the texture, not after.
- Pixel clean-up matters: lock transparent pixels and clean edges before import (eyes video).
- Large eyes are the cute part. In Part 8 the presenter fixed a "derpy" face by making the eyes wider and bigger and moving them over.

## 5. Eye options

How the creator draws the eye, measured on the face islands of the source files (numbers for a face island about 290 px wide):
- The eye white is a flat shape with almost straight vertical inner and outer sides. Eye width is 0.30 to 0.38 of the face width, eye height about 0.30 of the face height. Eyes sit a little below the middle of the island.
- The upper lash line is the heaviest mark: about 8 px (2.7 percent of face width), tapering, with 2 to 4 small flicks at the outer end. The lower lid is a thin 2 to 3 px line.
- Brows are tapered strokes of 6 to 10 px at the thick end. Blush is 2 or 3 short red hatch strokes, the nose a tiny dash, the mouth a small thin curve.
- The iris is never painted into the face island. It is a tall oval on its own quad (about 0.7 of the eye white's width, almost its full height): thick dark outline, a 2 or 3 colour gradient, one light blob and one small highlight. The lash line overlaps the iris top. In Astolfo the lashes are a separate alpha-blended mesh in front of the iris; in Love-chan the iris quad is 2 triangles with an `Eye.L` / `Eye.R` bone.
- Trace these marks from the user's reference at its own proportions, then compare a front render to the reference side by side and as a 50 percent overlay. The reference is for that comparison, never shown in the deliverable.

- Painted (default, Parts 7 and 11): eyes and mouth are part of the face texture. Cheapest and cutest, and the sprite strip gives blinks.
- Geometry rig (eyes video), for looking around:
  1. Cut the eye shape out of the face texture so it is transparent, keep the eyelash opaque. Irises go on their own free area, asymmetric allowed.
  2. Material: Principled BSDF, texture Alpha into Alpha, Color into Emission Color, strength 1.
  3. `eye white`: duplicate the two eye faces, separate, push back into the head, UV on white pixels, extrude, delete the front faces, fill the gap. Slide forward until it clips, then back a hair.
  4. `iris.L` and `iris.R`: duplicate the eye faces again, push into the head between the face and the eye white, UV onto the iris art, then Edge Slide the borders in so each plane is only as big as the iris (Mirror X off).
  5. Bones `i.L` and `i.R` in front of the eyes, pointing out, roll 0, parent to the head bone, Symmetrize. Bind with Empty Groups, gradient weight 100 percent with Auto Normalize. Pose with Local orientation.
  6. If an iris clips at the side, move the bone tail on X or push the iris deeper.

## 6. Face proportion check

Do this before texturing and again after (Part 8 end). The numbers are skill guidance, not from the series, so copy the reference first.
1. Measure on the reference: eye width divided by head width, eye centre height as a fraction of crown to chin, gap between eyes, mouth height, chin to nose distance. `read_character_ref.py` gives the crown, eye line and chin landmarks.
2. Render front and side stills and overlay them on the reference at 50 percent. Eyes should match the drawing within about one eye height.
3. Anime chibi guide: eyes sit at or a little below the middle of crown to chin, each eye is roughly a quarter of the head width, bigger when unsure.
4. Orbit in a three-quarter view: nose point, cheek step and jaw edge must read. Hair must cover the head box.
5. A look that matters goes to the user as two or three options first, and the user picks.

## 7. Hood and other head accessories

The series has only a jacket collar. Skill guidance: a hood, hat or ears is its own chunk built from the turnaround in front, side and back views, behind and around the hair shell, with its own UV colour. Orbit to the back and side before calling it done. If it is not visible in a front render, move it, do not delete it. Hair must stay visible through the hood opening.
