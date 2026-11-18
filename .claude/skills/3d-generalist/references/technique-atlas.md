# Technique atlas: the advanced craft, one index (`technique-atlas.md`)

The named techniques professionals use for 3D, 2D motion, animation, VFX, editing and sound, each with when to reach for
it, the numbers that set it, and where the full recipe lives. Use it before building anything that could be faked,
cheated or borrowed instead of brute-forced, and whenever a frame looks flat, CG, stiff or cheap.

Marks: **[P]** physics or a published standard, **[R]** a rule of thumb professionals quote (start there, judge by
eye), **[H]** a house rule. Paths are relative to the 3d-generalist skill folder; `../<skill>/` points into a sibling skill.

<!-- skill-navigation:start -->
## Reading Map

- [Technique atlas: the advanced craft, one index (`technique-atlas.md`)](#technique-atlas-the-advanced-craft-one-index-technique-atlasmd)
- [0. Symptom to technique](#0-symptom-to-technique)
- [1. Composition](#1-composition)
- [2. Lighting](#2-lighting)
- [3. Colour and grade](#3-colour-and-grade)
- [4. Depth](#4-depth)
- [5. Camera](#5-camera)
- [6. Animation](#6-animation)
- [7. VFX and compositing](#7-vfx-and-compositing)
- [8. Materials and surfaces](#8-materials-and-surfaces)
- [9. Environment](#9-environment)
- [10. NPR and stylized looks](#10-npr-and-stylized-looks)
- [11. Editing](#11-editing)
- [12. Type on screen](#12-type-on-screen)
- [13. Sound](#13-sound)
<!-- skill-navigation:end -->

## 0. Symptom to technique

| The frame looks | Reach for | Section |
| --- | --- | --- |
| Brute-forced: every pebble, blade or brick modelled | Detail ladder: texture, displacement, scatter, cards, hero pieces only | 8, 9 |
| Boxy, too clean, repeated | Bevels, broken silhouettes, per-instance variation, anti-tiling, wear | 8, 9 |
| Flat, no depth | Value planes, atmospheric mix, parallax layers, rim light, foreground frame | 1, 2, 4 |
| "CG", pasted in | Contact shadows, light wrap, grain and lens match, roughness variation | 7, 8 |
| Muddy, no focal point | Squint test, value grouping, one contrast winner, saturation focus | 1, 3 |
| Stiff or floaty motion | Anticipation, arcs, overlap, spacing, moving holds, stepped by channel | 6 |
| Cut feels off | Cut on action, J and L cuts, Murch's rule of six, 30-degree rule | 11 |
| Text hard to read | Size and hold minimums, scrim, safe areas, no scale shimmer | 12 |
| Sound thin or fake | One sound per event, layers by size, ducking, room tone | 13 |
| A drawn effect on a 3D shot | Hybrid 2D and 3D FX | 7 |
| A real thing drawn badly from shapes (train, person, building, logo) | A real photo or scan found online, reworked into the look: `../2d-generalist/references/real-images.md`; in 3D a sourced model (`references/assets-and-kitbash.md`) | 8, 9 |

## 1. Composition

| Technique | Use when | How, with numbers | Recipe |
| --- | --- | --- | --- |
| Squint test and value grouping | Any frame before colour | Reduce to 3 or 4 greys; the focal area holds the strongest value contrast [R] | `../draw-and-paint-art/references/noticing-and-design-lessons.md` |
| Focal hierarchy | The eye wanders | One winner on contrast, size, sharpness or saturation, a clear second and third [R] | `../2d-generalist/references/vox-psychology-and-design.md` §1 |
| Silhouette read | Characters, props, poses | Fill solid black; still readable, gaps between limbs, no tangents [R] | `../animate-characters/references/principles.md` |
| Leading lines and frame in frame | Guide the eye, add depth | Lines converge on the subject; a darker, soft foreground frame brackets it [R] | this file |
| Thirds, odds, asymmetric balance | Static staging | Key feature on a third; groups of 3 or 5 with uneven spacing; centre only for symmetry on purpose [R] | this file |
| Negative space, lead room | Scale, loneliness, motion | Room in front of a moving or looking subject; small subject in 40 to 60% empty frame [R] | this file |
| Shape language | Characters and sets | Circle friendly, square stable, triangle danger; one outlier against a consistent group [R] | `../draw-and-paint-art/references/gesture-and-construction.md` |
| Vertical-first framing | Shorts | Action inside the centre, clear of platform UI (bottom 15 to 20%, right edge) [H] | `../2d-generalist/references/qa-and-gates.md` |

## 2. Lighting

| Technique | Use when | How, with numbers | Recipe |
| --- | --- | --- | --- |
| Motivated light | Always | Every light has a visible or implied source; match its direction, colour and softness [R] | `references/camera-and-lighting.md` |
| Key, fill, rim | A clean subject | Key 45 degrees side and up; key to fill 2:1 (soft) to 8:1 (drama); rim behind and above [R] | `../paint-stylized-backgrounds/references/light-colour-and-time-of-day.md` |
| Source size for softness | Shadow quality | Large and close is soft, small and far is hard [P] | this file |
| Inverse square falloff | Light looks flat | Intensity drops to a quarter at twice the distance; move lights closer for falloff [P] | this file |
| Bounce and negative fill | Black or flat shadows | Dim card or area light coloured like the nearest surface; black flag to deepen a side [R] | this file |
| Practicals | Lamps, screens, signs | Emissive mesh plus a real light at the same spot; signs stay dimmer than lit roofs [H] | `../use-3d-software/references/lighting-render-and-gn-recipes.md` |
| Gobo or cookie | Empty walls, mood | Spot through a mask texture or a cut-out plane: leaves, blinds, window bars [R] | `../use-3d-software/references/lighting-render-and-gn-recipes.md` |
| Light pools and shafts | Mood, eye guide | Soft-edged spots (20 to 40% blend) with dark between; volume shafts behind the subject [R] | `references/camera-and-lighting.md`, `references/depth-parallax-and-atmosphere.md` |
| Temperature contrast | Separate zones | Warm key about 3200 K against cool fill 5600 to 7000 K; a 2000 K gap reads as intent [R] | this file |
| Flat 2D shading | Vector or Remotion art | Four-step formula, feathered masks, form shadow clipped to the body [R] | `../2d-generalist/references/textures-retro-and-shading.md` |

## 3. Colour and grade

| Technique | Use when | How, with numbers | Recipe |
| --- | --- | --- | --- |
| Value before colour | Every design | Design in grey, colour on top, check the final in grey again [R] | this file |
| 60-30-10 and limited palette | Cohesion | 60% dominant (low saturation), 30% secondary, 10% accent; 3 to 5 hues per piece [R] | `../2d-generalist/references/vox-psychology-and-design.md` |
| Complementary accent and saturation focus | Make the subject pop | World analogous, subject the opposite hue in a small area; periphery 20 to 40% less saturated [R] | this file |
| Colour script | A film with an arc | One frame per beat; temperature and saturation follow the story [R] | this file |
| Scene-linear, tone-map once | 3D renders | Light in linear, AgX or Filmic once, then grade; flat-colour styles use Standard [P] | `../paint-stylized-backgrounds/SKILL.md` |
| Split tone, teal-orange | Separation | Warm highlights and skin, cool shadows; skin stays on the vectorscope skin line [R] | `../edit-video/references/color.md` |
| LUT as a look | Consistent finish | After correction, 50 to 100% strength, never to fix white balance [R] | `../edit-video/references/color.md` |
| Memory colours | Stylized grades | Skin, sky, grass stay believable [R] | this file |

## 4. Depth

All the depth maths (atmosphere formula, parallax speeds by distance, medium-by-medium routes and checks):
`references/depth-parallax-and-atmosphere.md`. In short:

| Technique | How, with numbers |
| --- | --- |
| Atmospheric perspective | `seen = object*T + haze*(1-T)`, `T = exp(-sigma*d)`, visibility `V = 3.912/sigma`; haze colour is the horizon sky [P] |
| Parallax | Speed proportional to `1/distance` under camera translation; a pan has none; 5 to 8 layers [P][R] |
| Overlap, scale cues | Overlap on purpose, no tangents; a person, door or tree for scale [R] |
| Depth of field | f/1.4 to 2.8 shallow, f/4 to 5.6 medium, f/8 to 11 deep, real sensor size; shallow DOF on a wide shot makes a miniature [P][R] |
| Z-depth in comp | Mist or depth pass drives haze, defocus and colour shift after the render [R] |

## 5. Camera

| Technique | Use when | How, with numbers | Recipe |
| --- | --- | --- | --- |
| Lens choice | Space and mood | 18 to 24 mm stretch, 35 natural, 50 neutral, 85 to 135 compressed, 200+ flat [R] | `references/camera-and-lighting.md` |
| Push-in | Emphasis | 5 to 15% scale over the hold, eased in and out [R] | `../animate-characters/references/motion-design-2d.md` |
| Rack focus | Shift attention | 0.5 to 1.5 s eased, subjects at clearly different depths [R] | `../paint-stylized-backgrounds/references/animate-backgrounds.md` |
| Dolly zoom | Unease, reveal | Distance proportional to `1/tan(FOV/2)` [P] | `../use-3d-software/references/lighting-render-and-gn-recipes.md` |
| Whip pan | Transition | Full blur; cut on the blur into a matching whip [R] | `references/camera-and-lighting.md` |
| Motivated shake | Impacts | Event-triggered, sharp start, exponential decay over 0.3 to 1 s, rotation more than position [R] | `../edit-video/references/shakes-and-camera.md` |
| Handheld noise | Liveliness | 2 or 3 noise octaves, 0.2 to 0.5 degrees, 0.5 to 2 Hz, ramped with action [R] | `../animate-characters/references/timing-and-graph-editor.md` |
| 180-degree shutter | Filmic blur | Exposure `1/(2*fps)`; Blender shutter 0.5 [P] | `references/camera-and-lighting.md` |
| 180 and 30-degree rules | Continuity | Do not cross the action line; change angle by 30 degrees or more between similar cuts [R] | `../edit-video/references/editing-craft.md` |
| Angle with a reason | Every film | No two shots in a row share an angle kind; static unless motivated [H] | `references/camera-and-lighting.md` |
| Ken Burns on stills | Archival photos | Slow push or drift, 5 to 10% over the hold; add parallax layers for more depth [R] | `../2d-generalist/references/archival-collage-and-camera.md` |

## 6. Animation

| Technique | Use when | How, with numbers | Recipe |
| --- | --- | --- | --- |
| The 12 principles | Base vocabulary | Squash and stretch with kept volume, anticipation, arcs, overlap, slow in and out, timing, exaggeration [P] | `../animate-characters/references/principles.md` |
| Anticipation | Actions from nowhere | 3 to 8 frame wind-up opposite the move, bigger for bigger moves [R] | `../animate-characters/references/motion-design-2d.md` §5 |
| Overlap and offset | Stiff, simultaneous parts | Children 1 to 3 frames behind the parent; nothing stops on the same frame [R][H] | `references/acting-and-motion.md` |
| Arcs and spacing | Mechanical paths | Trace the motion path; ticks close at ends, wide in the middle [R] | `../animate-characters/references/timing-and-graph-editor.md` |
| Moving holds | Dead pauses | 2 to 4 frames of drift or settle; never a full freeze [R] | `../animate-characters/references/motion-design-2d.md` §15 |
| Head leads | Robotic turns | Eyes 2 to 4 frames before the head, head before the body; blink on direction changes [R] | `references/acting-and-motion.md` |
| Smears and multiples | Fast moves | 1 or 2 frames of stretched or multiplied shape in place of in-betweens [R] | `../animate-characters/references/smears-and-vfx-planes.md` |
| On twos, stepped by channel | Hand-made feel | 12 drawings per second at 24 fps; ones for fast action; character stepped, camera smooth [R] | `../animate-characters/references/stepped-2d-look-in-3d.md` |
| Block stepped, then spline | Every keyed shot | Constant interpolation until timing works, then curves [R] | `../animate-characters/references/stylized-animation-recipes.md` |
| No stiff repeats | Groups and entrances | Neighbours never share size, angle and timing [H] | `../2d-generalist/SKILL.md` |
| Physics for weight | Props, cloth, falls | Bake rigid bodies, cloth, springs so each frame is `f(t)` [H] | `references/acting-and-motion.md` |

## 7. VFX and compositing

| Technique | Use when | How, with numbers | Recipe |
| --- | --- | --- | --- |
| Hybrid 2D and 3D FX | Drawn smoke, fire, impacts on 3D | Drawn cards on twos, own light, one shared finish over both [R] | `references/hybrid-2d-3d-fx.md` |
| Matte painting and camera projection | Rich backgrounds cheaply | Paint over a render, project from the shot camera onto simple geometry, move the camera only a little [R] | `../use-3d-software/references/lighting-render-and-gn-recipes.md` |
| Cards and impostors | Far trees, crowds, mountains | Camera-facing baked cards at distance, 3D up close [R] | `../paint-stylized-backgrounds/references/blender-card-backgrounds.md` |
| Light wrap | A layer pasted on a background | Blurred background added inside the foreground edge, about 5 to 20 px at 1080p [R] | this file |
| Edge blend and despill | Cut-out fringes | Choke the matte 0.5 to 1 px, blur 0.5 px, remove spill colour [R] | this file |
| Grain and lens match | CG in footage, or a unified finish | Same grain size and amount (subtle digital 1 to 3%), then distortion, vignette, defocus [R] | `../edit-video/references/paid-to-free.md` |
| Bloom and halation | Bright lights | Threshold near 1.0 linear, radius 0.5 to 2% of frame width, 2 or 3 sizes; Blender 4.2+ uses the Glare node [P][R] | `../2d-generalist/references/textures-retro-and-shading.md` |
| Chromatic aberration | Lens feel | 0.5 to 2 px R and B shift, growing to the edges, none at the centre [R] | this file |
| Contact shadows and AO | Floating objects | Dark soft shadow at every contact, tight AO under objects [H] | `references/qa-and-gates.md` |
| Passes and Cryptomatte | Fix without re-render | Render mist, AO, diffuse, glossy and object masks [P] | `../use-3d-software/references/shading-and-textures.md` |
| Mattes and wipes (2D) | Reveals, transitions | Track, luma and set mattes; shape-matte wipes that lead into the next shot [R] | `../2d-generalist/references/2d-fx-type-and-compositing.md` |

## 8. Materials and surfaces

| Technique | Use when | How, with numbers | Recipe |
| --- | --- | --- | --- |
| Detail ladder | Any surface detail | Texture, then displacement or parallax, then scattered instances, then cards, then modelled hero pieces [H] | `references/assets-and-kitbash.md` |
| Displacement or normal | Choose a detail method | Real displacement only when the silhouette changes; bump or normal under about 1 cm [R] | `../use-3d-software/references/shading-and-textures.md` |
| Anti-tiling | Repeats visible on ground and walls | Per-cell random UV offset and rotation (Voronoi cells) or two samples at different scales blended by noise (Inigo Quilez, "texture repetition"); always add a metre-scale colour and roughness noise [R] | this file |
| Macro, mid, micro variation | Uniform surfaces | Metre-scale colour and roughness noise, a mid pattern, micro normal tiled 4 to 10 times [R] | `references/assets-and-kitbash.md` |
| Edge wear by curvature | Believable wear | Convex edges chip and brighten, concave areas collect dirt (Pointiness, Bevel or AO node) [R] | `../use-3d-software/references/stylized-shading-recipes.md` |
| Bevel everything | Hard edges look CG | 1 to 2 mm bevel so edges catch a highlight [R] | `../use-3d-software/references/quick-modeling-recipes.md` |
| Trim sheets and decals | Detail across many assets | Shared strip texture for bevels and panels; dirt, stains, labels as decals [R] | `../use-3d-software/references/shading-and-textures.md` |
| Triplanar (Box) mapping | No UVs, stretching | Image Texture Projection Box, Blend about 0.2 [P] | this file |
| Texel density | Mixed sharpness | One target across assets (512 to 1024 px/m for real-time, more for hero close-ups) [R] | this file |
| PBR value ranges | Plastic look | Albedo never pure black or white (charcoal about 0.04, snow about 0.9 linear); metal 0 or 1; vary roughness more than colour [P] | `../use-3d-software/references/shading-and-textures.md` |
| Paper and real-material texture (2D) | Sterile vector art | Looping paper and grit, torn borders, real scanned sources [H] | `../2d-generalist/references/textures-retro-and-shading.md` |

## 9. Environment

| Technique | Use when | How, with numbers | Recipe |
| --- | --- | --- | --- |
| Build to camera | Every set | Grey block-out, lock the camera, spend detail where the frame looks [R] | `../paint-stylized-backgrounds/references/render-and-blockout.md` |
| Kitbash and source first | Any real-world object | Add-on, then online model, then a build from reference photos [H] | `references/assets-and-kitbash.md` |
| Scatter with density masks | Rocks, grass, debris | Distribute Points on Faces with noise or a weight map for density, clusters not even spread [R] | `../use-3d-software/references/geometry-nodes.md` |
| Per-instance variation | Repeated instances | Random rotation, scale 0.7 to 1.3, slight tilt, 3 or more variants [R] | `references/assets-and-kitbash.md` |
| Three scales | Ground and rock beds | Large, medium, small pieces (boulder, gravel, grit) [R] | `references/assets-and-kitbash.md` |
| Ground contact | Objects sit on top | Dirt, AO, grass or debris at every base [H] | `references/qa-and-gates.md` |
| Set dressing as story | Lived-in places | Wear, mess, personal items, signs of use; real place and period [H] | `references/worlds-and-cutaways.md` |
| Asymmetry and broken lines | Too neat | Leaning fences, uneven roofs, varied spacing [R] | `references/assets-and-kitbash.md` |
| LOD and impostors | Big worlds | Simpler meshes and baked cards at distance; collection instances to stay light [R] | `../use-3d-software/references/environments.md` |
| Ambient life | Dead worlds | Trees sway, birds, water, passing vehicles, procedural wind [H] | `references/worlds-and-cutaways.md` |

## 10. NPR and stylized looks

| Technique | Use when | How, with numbers | Recipe |
| --- | --- | --- | --- |
| Toon ramp | Cel look | Shader to RGB into a Constant ramp, 2 or 3 bands (EEVEE only) [P] | `../model-characters/references/npr-shading-and-painted-look.md` |
| Hand-tuned shadow shapes | Noisy toon shading | Edit normals and thresholds per character (Guilty Gear Xrd, GDC 2015) [R] | `../model-characters/references/npr-shading-and-painted-look.md` |
| Outlines | Line art | Inverted hull, depth and normal edge detect, or Line Art; thicker silhouette than interior [R] | `../use-3d-software/references/stylized-shading-recipes.md` |
| Halftone, dither, print | Comic, newsprint | Dots sized by value at about 45 degrees; misregistered plates; Bayer dither [R] | `../2d-generalist/references/textures-retro-and-shading.md` |
| Painterly overlay | Smooth CG | Screen-space paper or brush texture, Kuwahara node [R] | `../use-3d-software/references/stylized-shading-recipes.md` |
| Line boil | Hand-drawn life | Jitter on twos or threes, 8 to 12 changes a second, small amplitude [R] | `../animate-characters/references/stepped-2d-look-in-3d.md` |
| Paint-over | Stills and hero frames | Render a base, paint over in Krita [R] | `../draw-and-paint-art/references/light-form-and-colour.md` |
| Clay reveal | Show how a world is made | Render, then clay, then render [H] | `references/clay-reveal.md` |

## 11. Editing

| Technique | Use when | How, with numbers | Recipe |
| --- | --- | --- | --- |
| Rule of six (Murch) | Choosing a cut | Emotion 51%, story 23%, rhythm 10%, eye trace 7%, 2D plane 5%, 3D space 4%; sacrifice from the bottom [P] | `../edit-video/references/editing-craft.md` |
| Cut on action, match on action | Hide the cut | Cut mid-motion, keep position and direction across it [R] | `../edit-video/references/editing-craft.md` |
| J and L cuts | Smooth scene changes | Next sound leads the picture (J) or the last sound runs on (L) by 4 to 24 frames [R] | `../edit-video/references/editing-craft.md` |
| Hard cut by default | Transitions | Dissolve only for passing time; smash cut for shock; fade to black for an end [R] | `../edit-video/references/editing-craft.md` |
| Match cut | Link two ideas | Same position, scale and direction of the main shape across the cut [R] | `../animate-characters/references/motion-design-2d.md` §12 |
| Rhythm | Pacing | Vary shot length; a new wide shot holds 2 to 3 s to read [R] | `../edit-video/references/editing-craft.md` |
| Speed ramp | Impact | Ramp over 6 to 12 frames with optical flow [R] | `../edit-video/references/retime-and-speed.md` |
| Beat sync | Music-led cuts | The fast part of the move lands on the beat marker [R] | `../edit-video/references/edit-page-and-keyframes.md` |
| Picture before word | Explainers | The picture lands 4 to 8 frames before the word it shows [H] | `../2d-generalist/references/explainer-script.md` |

## 12. Type on screen

| Technique | Use when | How, with numbers | Recipe |
| --- | --- | --- | --- |
| Size minimum | Any read text | Cap height 5% of frame height or more (about 54 px at 1080p); contrast 4.5:1 or more [H][P] | `../2d-generalist/references/qa-and-gates.md` |
| Hold time | Kinetic text | At least 0.5 s plus 0.3 s per word; subtitles at most 20 characters a second, 42 per line, 5/6 s minimum (Netflix) [H][P] | `../2d-generalist/references/qa-and-gates.md` |
| Safe areas | Every frame | Action safe 93%, graphics safe 90% (EBU R95); clear of vertical platform UI [P][H] | `../2d-generalist/references/qa-and-gates.md` |
| Entrances | Motion type | Ease out in 200 to 400 ms, faster exit, 2 to 5 frame stagger per word [R] | `../edit-video/references/text-and-typography.md` |
| Text over busy footage | Legibility | Scrim, shadow, blur or a plate behind [R] | `../2d-generalist/references/2d-fx-type-and-compositing.md` |
| No scale shimmer | Animated text | Animate from the final size, avoid scaling glyphs [H] | the `motion-quality` skill |
| Shorts captions | Vertical video | One word at a time, centred, synced within 0.05 s [H] | `../edit-video/references/editing-craft.md` |

## 13. Sound

| Technique | Use when | How, with numbers | Recipe |
| --- | --- | --- | --- |
| One sound per event | Every visible action | Its own recording at its own frame, within one frame [H] | `../design-sound/references/foley.md` |
| Layers by size | Impacts, steps | Transient, body and tail layers scaled by size and distance [R] | `../design-sound/references/foley.md` |
| Ducking and carving | Voice over music | Voice 10 LU or more over music, music carved at 1 to 4 kHz [H] | `../design-sound/references/mix.md` |
| Room tone and beds | Silence gaps | A bed under everything, band-limited, 15 LU under the voice [H] | `../design-sound/references/mix.md` |
| Loudness | Delivery | -14 LUFS integrated, true peak -1 dB or lower [P][H] | `../design-sound/references/mix.md` |
| Silence before a hit | Emphasis | A short drop before the loud moment [R] | `../design-sound/references/mix.md` |
| Foley from the picture | Many contacts | Video-to-audio model, then fix by events [H] | `../design-sound/references/video-foley.md` |

Sources: Bruce Block, *The Visual Story*; Blain Brown, *Cinematography: Theory and Practice*; Walter Murch, *In the
Blink of an Eye*; Richard Williams, *The Animator's Survival Kit*; Thomas and Johnston, *The Illusion of Life*; Ron
Brinkmann, *The Art and Science of Digital Compositing*; Inigo Quilez articles on fog and texture repetition; Adobe,
*The PBR Guide*; Netflix Timed Text Style Guide; EBU R95; Blender 5.2 manual; Motomura, GDC 2015. The [R] numbers are
starting points, not standards. Research pass 2026-11-09.
