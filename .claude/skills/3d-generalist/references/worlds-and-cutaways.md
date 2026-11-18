# Worlds, Cutaways and Environment Effects (`worlds-and-cutaways.md`)

A 3D scene must read at a glance and never look empty. Every layer of the frame (sky, background, midground, foreground
and underground section) needs real depth and subtle motion.

## 1. Perspective cutaway staging

- **Perspective side camera, never flat orthographic 2D:** place the camera slightly off-axis and above so cylinders,
  domes, timber and terrain read round and solid.
- **World on top, cross-section below:** carve the build into a ground, rock, snow or water cross-section slab. Make
  all cutaway section meshes **double-sided** so no camera angle ever shows sky through the back of a cut wall.
- **No coplanar flicker:** where a floor meets a cutaway wall, rest the floor on a ledge or beam inside the wall and cut
  both on the exact same plane so wood never pokes or z-fights through stone.
- **Part inside a building stays inside:** if a pipe, flue or trap sits inside a wall or room, give that wall its own
  local lengthwise cutaway rather than pulling the interior part outside the building onto the main cut plane.
- **Object-driven shader cutaway in Blender:** to see inside an enclosed cabin, room or vehicle without destructive
  boolean meshes, mix `Principled BSDF` and `Transparent BSDF` with a `Mix Shader` whose factor comes from
  `Texture Coordinate (Object: Empty Sphere) -> Separate XYZ (Y)`. Move, rotate (`180 deg`) or scale the Empty Sphere
  to control the transparent cut plane interactively from any camera angle.

## 2. Dressing the world (real place, real period, moving life)

- **Pick a specific place and century first:** before placing a single tree or fence, decide where and when the build
  happens (for example 14th-century English mill valley, Polynesian coral shore, Roman river crossing). Dress the world
  with period-accurate carts, tracks, hedges, far cottages, rocks and tools.
- **Dress where the camera actually looks:** measure which `(x, z)` cells appear in frame across the timeline. Do not
  waste 50 props behind the camera while leaving the visible horizon bare; if a sailing or road shot sees 150 m back,
  dress the shore or road 150 m deep.
- **Ambient motion in every layer:** nothing in the background stays dead still.
  - *Sky:* drifting clouds, birds flying across the horizon.
  - *Land / Road:* tree leaves swaying gently, a truck or cart moving linearly between two keyframes in the far background,
    animals with real breathing/grazing idle clips (never a frozen statue).
  - *Water:* swimming fish, bounded sine-field caustics on the bed (0.1 to 0.2 emissive, ~40 cm cells, never raw division
    that produces `NaN` black blobs), foam at the waterline, and water clamped below rising beach sand.

## 3. Physics-true water, fire, weather and digging

- **Water obeys gravity on every frame:** still water in a U-bend, trap or well sits flat and level at the weir height
  in both legs, never clinging to a falling outlet slope. Underground water pockets look carved in rough PBR rock with a
  dark wet band along the wall, never a smooth blue sphere.
- **Standing in water:** place the character's feet on the stream or sea bed (or a flat bed shelf under both feet), with
  water at ankle or shin height and ripples around the legs—never walking on top of the water surface.
- **Realistic fire:** use a sourced CC0 fire flipbook or clip on camera-facing planes with additive blending, rising
  embers, soft smoke and a warm flickering point light. Never use an orange cone or falling orange spheres.
- **Weather and air lines:** wind, mist, rain and sun rays are a faint atmospheric hint (soft-edged, low opacity,
  stopped by solid walls). Flow arrows use a single clean style (either thin solid or thin dashed lines, never thick
  striped tubes), and pull their tail into the arrowhead when exiting.
- **Piece-by-piece building and digging:**
  - Digging happens one scoop at a time where the character stands: each scoop removes one chunk and throws it onto a
    growing spoil mound (`mound` surface) with its own dig sound. Holes never sink or fade smoothly on their own.
  - Masonry and timber assemblies seat piece by piece from the character's hands with a small settle and contact SFX,
    with zero gap (within 1 cm) between courses.
