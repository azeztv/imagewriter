# Weather and nature across engines

Where to learn rain, wind, storms, sun and sky, snow and fog in Blender, Unity, Godot 4, Unreal Engine 5 and
three.js, and which ready assets to start from. Checked 2026-11-07 (three.js r187, UE 5.8 docs, Blender 5.2). Views
and stars are at check time. Before you rely on a pick, check its date and version again: tutorials age fast, and a
newer official sample beats an old video.

<!-- skill-navigation:start -->
## Reading Map

- [Weather and nature across engines](#weather-and-nature-across-engines)
- [Rain](#rain)
- [Wind](#wind)
- [Storms](#storms)
- [Sun and sky](#sun-and-sky)
- [Snow and fog](#snow-and-fog)
- [Weather systems and learning](#weather-systems-and-learning)
- [Not found](#not-found)
<!-- skill-navigation:end -->

Step-by-step Blender builds for these effects (rain kit, ground fog, god rays, grass, wind) are in
`environments.md`. This file is the cross-engine map.

## Rain

**Blender**
- Jepe, Blender Rain Generator (free, 36,900 sales, commercial use allowed): https://jepe.gumroad.com/l/raingenerator. Geometry-nodes rain with splashes, wind tilt and weight-painted splash areas. Blender 3.6+, Cycles.

**Unity (URP/HDRP)**
- VFX Graph manual: https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@17.0/manual/index.html
- VisualEffectGraph-Samples: https://github.com/Unity-Technologies/VisualEffectGraph-Samples (2.1k stars, last push 2024-11). Official sample set; no rain scene confirmed; licence text must be read before reuse.

**Godot 4**
- Particles docs: https://docs.godotengine.org/en/stable/tutorials/3d/particles/index.html
- Lexpartizan/Godot_rain_shader: https://github.com/Lexpartizan/Godot_rain_shader (102 stars, MIT, 2023-06). Check the Godot version.

**Unreal Engine 5**

**three.js**
- Official `webgpu_compute_particles_rain`: https://threejs.org/examples/webgpu_compute_particles_rain.html. GPU compute rain in TSL, needs WebGPU.

## Wind

**Blender**

**Unity**
- elringus/grass-bending: https://github.com/elringus/grass-bending (560 stars, 2025-10). Waving and bending grass; no licence on GitHub.
- ColinLeung-NiloCat/UnityURP-MobileDrawMeshInstancedIndirectExample: https://github.com/ColinLeung-NiloCat/UnityURP-MobileDrawMeshInstancedIndirectExample (1.7k stars, MIT, 2020-11). Instanced grass; needs porting.

**Godot 4**
- 2Retr0/GodotGrass: https://github.com/2Retr0/GodotGrass (700 stars, MIT, 2024-08). Ghost of Tsushima style MultiMesh grass with shader wind.
- IcterusGames/SimpleGrassTextured: https://github.com/IcterusGames/SimpleGrassTextured (585 stars, MIT, updated 2026-10). Grass painting plugin, also in AssetLib.

**Unreal Engine 5**
- Pivot Painter docs: https://dev.epicgames.com/documentation/en-us/unreal-engine/using-pivot-painter-tool-in-unreal-engine

**three.js**

## Storms

**Blender**

**Unity**

**Godot 4**: no storm tutorial found. Combine the rain particles with a sky shader and a flashing DirectionalLight3D.

**Unreal Engine 5**

**three.js**
- Official `webgpu_tsl_vfx_tornado`: https://threejs.org/examples/webgpu_tsl_vfx_tornado.html. Wind-driven swirl and debris.
- Lightning: no example. Use a short flash on a light plus emissive bolt geometry.

## Sun and sky

**Blender**
- Sky Texture docs: https://docs.blender.org/manual/en/latest/render/shader_nodes/textures/sky.html. In 5.x the types are Single Scattering and Multiple Scattering; the Dust input is gone.
- EEVEE volumes docs: https://docs.blender.org/manual/en/latest/render/eevee/render_settings/volumes.html
- CC0 skies and materials: https://polyhaven.com/hdris, https://ambientcg.com/

**Unity**
- HDRP volumetric clouds: https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.0/manual/create-realistic-clouds-volumetric-clouds.html
- jiaozi158/UnityVolumetricCloudsURP: https://github.com/jiaozi158/UnityVolumetricCloudsURP (527 stars, MIT, 2025-05). HDRP clouds in URP 14+.

**Godot 4**
- Sky shaders: https://docs.godotengine.org/en/stable/tutorials/shaders/shader_reference/sky_shader.html
- Volumetric fog: https://docs.godotengine.org/en/stable/tutorials/3d/volumetric_fog.html
- clayjohn/godot-volumetric-cloud-demo-v2: https://github.com/clayjohn/godot-volumetric-cloud-demo-v2 (250 stars, 2026-01, Godot 4.2+). Compute-shader clouds by a Godot rendering developer; licence "other", read it first.
- Bonkahe/SunshineClouds2: https://github.com/Bonkahe/SunshineClouds2 (635 stars, MIT, 2026-09). Volumetric cloud plugin.

**Unreal Engine 5**
- Sky Atmosphere: https://dev.epicgames.com/documentation/en-us/unreal-engine/sky-atmosphere-component-in-unreal-engine
- Volumetric Cloud: https://dev.epicgames.com/documentation/en-us/unreal-engine/volumetric-cloud-component-in-unreal-engine

**three.js**
- Official Sky addon `webgl_shaders_sky`: https://threejs.org/examples/webgl_shaders_sky.html, and `webgpu_sky`.
- Official `webgpu_volume_cloud` (raymarched clouds; `webgl_volume_cloud` for WebGL) and `webgpu_volume_lighting` (light shafts).

## Snow and fog

- Blender: snow storm and fog above; ground fog build in `environments.md`.
- Godot: the volumetric fog docs above.
- Unreal: Faucher's Sky Atmosphere and Fog video above.
- three.js: official `webgpu_compute_particles_snow`, `webgpu_custom_fog`, `webgpu_fog_height`, `webgpu_postprocessing_fog`.

## Weather systems and learning

- delebash/UE_GlobalEnvironmentalSystem: https://github.com/delebash/UE_GlobalEnvironmentalSystem (164 stars, MIT, UE 5.6). Ties weather, foliage, water and wind together; needs the paid Ultra Dynamic Sky.
- kS222138/TCA_Weather_System (Godot): https://github.com/kS222138/TCA_Weather_System (39 stars, MIT). Small, untested.
- three.js examples index: https://threejs.org/examples/ and the migration guide https://github.com/mrdoob/three.js/wiki/Migration-Guide to date any older tutorial.

## Not found

- Unity: no official weather sample project and no verified rain, snow or fog system.
- Godot: no storm or lightning tutorial; godot-demo-projects has no weather demo.
- three.js: no official grass, lightning or rain-on-glass example.
- Blender: no free weather add-on besides Jepe's rain kit; droplets on glass has only older tutorials.
