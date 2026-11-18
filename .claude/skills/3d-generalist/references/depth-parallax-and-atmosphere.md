# Depth: parallax and atmospheric perspective (`depth-parallax-and-atmosphere.md`)

One file for the two strongest depth cues after overlap. Use it for any shot that reads flat: a 3D world, a 2.5D photo,
a painted multiplane background, a Remotion or SVG scene, a map. Marks: **[P]** physics or a published standard,
**[R]** a rule of thumb professionals quote (start there, judge by eye), **[H]** a house rule.

Reading map: 1 the one formula, 2 atmosphere by medium, 3 parallax maths, 4 parallax by medium, 5 checks, 6 where the
recipes live.

## 1. Atmosphere is one formula

Air between the camera and an object removes the object's light and adds the sky's light [P]:

```
seen = object * T + haze * (1 - T),   T = exp(-sigma * distance)
visibility V (contrast down to 2%) = 3.912 / sigma        (Koschmieder)
```

That single mix explains every artist rule at once: contrast falls, darks lift more than lights, saturation drops and
the hue slides toward the haze colour. Do not grade each of those by hand; mix toward one haze colour by `1 - T`.

- **Pick V from the story, then derive sigma.** Clear day 20 to 50 km, light haze 5 to 10 km, mist 1 to 2 km, fog
  under 1 km [P]. A small set needs a V a few times its depth, or the haze never shows: a 60 m street with V = 300 m
  gives sigma = 0.013 per metre [R].
- **Haze colour = the sky at the horizon behind the object**, never grey by default [P]: blue-white at midday, warm
  orange at golden hour, flat grey when overcast, dark blue at night (lights then bloom through it).
- **Height fog:** density falls with altitude, so valleys and ground level are hazier than ridges; the side toward the
  sun scatters brighter (Inigo Quilez, "better fog") [P].
- **Painted or 2D planes:** apply the mix per plane. Five planes at T = 1.0, 0.8, 0.6, 0.4, 0.2 is a good start [R]; the
  last plane sits close to the sky colour. Check in greyscale: each plane steps lighter and flatter.
- **Warm near, cool far** comes out of the formula on a blue day; on a golden or night scene the far planes go warm or
  dark instead. Follow the haze colour, not the slogan [P].

## 2. Atmosphere by medium

| Medium | How | Numbers |
| --- | --- | --- |
| Blender Cycles/EEVEE | World or a box with Principled Volume or Volume Scatter | Density is about sigma per metre: `3.912 / V` [P]; anisotropy 0.3 to 0.8 for sun shafts [R] |
| Blender compositor | Mist pass (Start, Depth, Falloff) drives a Mix toward the haze colour | Falloff Quadratic or Inverse Quadratic, Depth near V [R] |
| three.js | `scene.fog = new THREE.FogExp2(hazeColor, density)` | `FogExp2` keeps `exp(-(density*d)^2)`, so 2% at V means `density = 1.978 / V` [P] |
| Crucible | `environment.fogColor` and `fogDensity` (fog colour is linear RGB); `volumeFog` for lit shafts and shadows | `volumeFog` needs `{ hdr: true, depth: true }`; read the checkout's `docs/volumetric.md` first [H] |
| Remotion, SVG, DOM | Each layer gets `mix(layerColor, haze, 1 - T)`: a haze-coloured rectangle over the layer at opacity `1 - T` | Same T table as painted planes |
| Painted (Krita) | One haze-colour layer per depth plane, Normal mode at `1 - T` opacity, then flatten lightly | Lift the darkest value of each plane first |

## 3. Parallax maths

Parallax comes from **camera translation**, never from a pan or tilt (a rotating camera shows no parallax) [P]. With
the camera trucking by `x`, a layer at distance `z` moves on screen by `x * f / z`, so speed falls as `1 / z` [P]:

| Layer | Distance (subject = 1) | Speed (subject = 1) |
| --- | --- | --- |
| Foreground frame (leaves, rail, pole) | 0.5 | 2.0 |
| Subject | 1 | 1.0 |
| Midground | 2 | 0.5 |
| Background | 4 | 0.25 |
| Far hills | 10 | 0.1 |
| Sky, sun, moon | infinite | 0 |

- **Five to eight layers** read as continuous depth; two or three read as cardboard [R].
- **A fast foreground element** (a pole, a branch passing at 2x) sells depth more than any background detail [R].
- **Scale with distance:** a card moved to `k` times its distance must grow by `k` to keep its framed size [P].
- **Dolly zoom** keeps the subject size with `distance proportional to 1 / tan(FOV / 2)` while the background swells [P].
- **Ease** every parallax move in and out; a linear start pops [R].

## 4. Parallax by medium

| Medium | Route | Pitfall |
| --- | --- | --- |
| Blender, three.js, Crucible | Put cards or models at their real depth and move a real camera; parallax is free and correct | A pan instead of a truck kills it |
| After Effects style 2D (Remotion, SVG, DOM) | `layerX = cameraX * (zSubject / zLayer)`, same for Y | Foreground layers must be wider than the frame by `cameraTravel * speed` |
| Still photo to 2.5D | Depth map, cut 3 to 5 layers, fill behind each cut (clone or inpaint), or displace a subdivided plane | Keep camera travel under about 5 to 10% of frame width or the stretch shows [R] |
| Painted multiplane | Paint each plane on its own layer with overpaint at its edges, then the AE style route | Paint the hidden part behind each plane before animating |
| Map or chart | Labels and clouds on planes above the terrain; slight orbit or truck | Text stays camera-facing and outside the fog |

## 5. Checks before showing anyone

1. Greyscale frame: each plane farther back is lighter and lower in contrast, in steps, with the subject the strongest
   contrast in the frame.
2. Haze colour matches the sky colour near the horizon in the same frame.
3. Scrub the move: speeds order with distance, the sky does not move, nothing near slides slower than something far.
4. No empty paper or missing fill appears at the edges or behind cut layers at the end of the move.
5. Text and UI are not fogged or parallaxed unless that is the design.

## 6. Where the recipes live

- Fog plane, aerial perspective cards, layered dark planes, image-card clouds: `../paint-stylized-backgrounds/references/blender-card-backgrounds.md`.
- Parallax with 2D and 3D layers, loops and camera moves: `../paint-stylized-backgrounds/references/animate-backgrounds.md`.
- Gradient fake fog, mist depth, camera projection: `../use-3d-software/references/lighting-render-and-gn-recipes.md`.
- Fog and volumetrics across engines: `../use-3d-software/references/environments.md`, `../use-3d-software/references/weather-across-engines.md`.
- 2.5D photo parallax with depth titles: `../2d-generalist/references/archival-collage-and-camera.md`; raised maps and parallax clouds: `../2d-generalist/references/maps-and-geodata-2d-3d.md`.
- Orbit parallax, depth of field and the finish pass: `references/camera-and-lighting.md`.

Sources: Wikipedia "Visibility" (Koschmieder relation); Inigo Quilez, "Better fog" (iquilezles.org/articles/fog);
three.js `FogExp2` docs; Blender 5.2 manual (Mist pass, Volume Scatter); Bruce Block, *The Visual Story* (depth cues);
Wikipedia "Multiplane camera" and "Dolly zoom". Research pass 2026-11-09.
