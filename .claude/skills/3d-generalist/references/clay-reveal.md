# Clay reveal (render, clay model, render)

<!-- skill-navigation:start -->
## Reading Map

- [Clay reveal (render, clay model, render)](#clay-reveal-render-clay-model-render)
- [When](#when)
- [Grammar](#grammar)
- [Pacing](#pacing)
- [Build it (any software)](#build-it-any-software)
- [Cutaways under ground](#cutaways-under-ground)
- [Moving vehicles](#moving-vehicles)
- [Sound](#sound)
- [Checks](#checks)
- [Traps](#traps)
<!-- skill-navigation:end -->

A short film that shows a finished, lit world, wipes the same moving shot into a flat grey clay model, pulls back to
show how the whole thing is built, then wipes back to the render. The clay pass is the explanation, so it needs no
titles. It works for any built world: a city block, a station, a factory floor, a house, a diorama.

## When

- The making is part of the wow: a procedural or kitbashed world, a pack showcase, "all of this is 3D".
- Familiar everyday places land best (a metro platform, a street corner, a kitchen): viewers know the real thing,
  so the clay shot reads instantly as "this was built".

## Grammar

1. Open on the finished render from a human vantage (eye level on a platform, a pavement, a rooftop), lit with intent:
   low sun in front of the camera outdoors, practical lights indoors. One mover crossing close (a train, a car, a
   person) sells scale and gives the cut a clock.
2. A hard diagonal wipe of about 1 s, revealed from one corner, turns the same frame into clay. The camera keeps
   moving through it, and so does the mover. Every wipe in the film is the same wipe; never a dissolve.
3. In clay the camera leaves the human eye line: it backs out, cranes up or passes through a wall until the whole
   build reads as one object.
4. Wipe back to the render on the wide view, then drift or return to the opening spot for closure.
5. Sound only while the picture is rendered: fade the bed just before the first wipe, keep the clay section silent,
   cut sound back in hard on the wipe back. No music.

## Pacing

- The opening render runs long (about 7 to 10 s in a 20 s film): it has to sell the place as real before the clay
  takes it away. Let the mover's whole action play in it (a train enters, brakes, is still rolling at the wipe).
- After that, time follows detail: the clay pull-back is slow where there is structure to read (a section, a stair,
  a roof truss) and quick through empty space; the wide render after the wipe back holds 3 to 5 s.
- Reference times from a 36 s cut: render 0-10.5, wipe 10.5-11.5, clay crane 11.5-22, wipe 22-23.25, render
  aerial, back to the opening spot. A 21 s cut: render 0-7.5, wipe to 8.5, clay 8.5-16, wipe to 17, render to 21.

## Build it (any software)

The flow does not depend on a tool. Pick whatever the project already uses; the only rules are: one scene, one
camera that is a function of time (or one baked camera track), two passes rendered with identical frames and size,
wipes joined afterwards. Nothing in the scene knows about the wipe.

**Clay pass, the look:** every material replaced by flat colour with no maps: one warm grey for built things (about
0.6 linear), darker for roads and ground, darker again for soil or cut faces, flat green for plants (keep the leaf
alpha, or leaves become solid cards). Neutral white key, high ambient, blurred overcast sky, no bloom, grain,
vignette or emissive. **Render pass:** filmic or AgX view transform, light haze for depth, bloom on practical lights.

| Software | Clay pass | Render both passes |
|---|---|---|
| Blender | View Layer > Material Override (keep alpha leaves on their own layer), or Workbench Solid/Matcap | Two view layers or two scenes sharing objects, same frame range |
| Cinema 4D, Maya, Houdini, 3ds Max | Takes / render layers / material override (Redshift, Arnold, Karma all have one) | Two takes or layers in one batch |
| Unreal | A second Level Sequence shot with a clay material swapped in (Material Parameter Collection or Variant Manager), or Detail Lighting view mode for drafts | Movie Render Queue, two jobs, same sequence |
| Unity | Override material in a Render Objects feature (URP) or a custom pass (HDRP) | Recorder, two takes |
| Godot | A world-wide override material on the viewport (debug draw or `material_override` per mesh) | Movie Maker mode, two runs |
| three.js | `scene.overrideMaterial` plus alpha-tested exceptions | Headless frame-by-frame capture of each pass |
| Crucible | Replace `part.material` before building the renderer | Frame-by-frame capture of each pass |

**The wipe, in any editor:** a hard linear wipe at 45 degrees from one corner, about 1 s, no feather.

| Editor | How |
|---|---|
| DaVinci Resolve | Clay above render, Edge Wipe transition at 45 degrees, softness 0 (or a Fusion rectangle mask animated across) |
| Premiere / After Effects | Linear Wipe effect on the top clip, angle 135, feather 0, keyframe completion 0 to 100% |
| CapCut / Kdenlive | Wipe transition set to diagonal, hard edge |
| FFmpeg | render A, clay B, A0 and B0 the wipe starts: `blend=all_expr='if(lt(T,B0),if(lt((X/W+Y/H)/2,clip((T-A0)/1,0,1)*1.02),B,A),if(lt((X/W+Y/H)/2,clip((T-B0)/1,0,1)*1.02),A,B))'`; bed envelope with `volume='...':eval=frame` |

- Build the world wherever it is quickest: a DCC by script (boxes with world-space box UVs, booleans for soil and
  shafts, one object per material, one GLB or FBX out), kitbashed library assets, or open city data. Iterate on the
  whole film in whichever renderer gives a full pass in minutes; save the slow path-traced render for the final.
- Order of work: light and colour first on grey shapes, then materials, then forms, then clutter, then finish. Check
  collisions (props through walls, the camera through geometry) before the first full render.

## Cutaways under ground

- Build the world with one side missing on purpose: everything past a section plane is not modelled, so the soil,
  slab and street show their cut faces. Make the soil block deep (tens of metres below the lowest floor), or the sky
  shows under it in the wide shot.
- The wall the camera backs out through is its own object; hide it (move it far away) once the camera is past it
  and it is behind the lens, never while it is in frame.
- Wide section view: camera at about mid-height of the soil, oblique (30 to 40 degrees off the cut face), so the lit
  rooms read as rooms. Straight-on elevations and high views make a thin strip.
- Light: rooms by their own fixtures (area lights under the ceiling), the outside by a low sun behind the buildings,
  so the cut face sits in shade and the lit rooms glow. Raise the ambient only while the camera is outside.

## Moving vehicles

- Use the renderer's object motion blur where it has one (Cycles, Redshift, Unreal MRQ with spatial and temporal
  samples). A renderer that only blurs camera motion: render N subframes per output frame (4 worked) and blend them
  into a shutter, for example FFmpeg `tmix=frames=3,fps=30` on a 120 fps render.
- Drive the vehicle from a physical rule (constant braking to a stop point), so it is still moving at the wipe and
  stops in the clay section.
- Measure a sourced model before placing it: fit it to the real height (a metro car is about 3.7 m), compute its
  length from the scale, and set its bottom on the rail top.

## Sound

Rendered parts only. Video-to-foley from the render pass makes a believable bed (a train arriving: rumble, wheels,
brakes; a street: traffic, wind). Generate each rendered section separately and lay them at their film times.

## Checks

- Both passes: same frame count and size (ffprobe) before joining; a one frame offset jumps at the wipe.
- One still per pass at the opening, mid pull-back and wide view before any film render.
- Scene-cut detectors rarely see a slow diagonal wipe between similar frames; read wipes from 8 fps frame sheets.

## Traps

- Downloaded buildings often stand on their own diorama base (plinth, scanned ground) inside the same mesh: white
  islands in clay. Measure first; pick another source if the base cannot be cut.
- Many CC models load untextured or flat: check each in a neutral probe render with fog off before choosing it.
- A tall dark mass right beside the opening camera (a stair enclosure, a column) eats a third of the frame: move the
  camera between columns or turn the element so its lit face (a stair foot) meets the lens.
- A camera looking almost straight down yaws hard for small moves; end crane moves on a high oblique and keep moving.
- Map edges: load the ring of tiles or ground around the subject so a backlit view never looks into empty ground.
