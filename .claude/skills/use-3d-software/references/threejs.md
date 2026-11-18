# three.js

Steps for putting a Blender asset or scene on a web page with three.js: export, load, compress, animate, light,
colour and performance. Written from the official three.js docs and examples (threejs.org/docs,
threejs.org/examples), names checked against r187 (2026-11). Crucible scenes follow the same export rules.

Version names
- `outputEncoding` and `sRGBEncoding` are gone. Use `renderer.outputColorSpace = THREE.SRGBColorSpace` (the default)
  and `texture.colorSpace = THREE.SRGBColorSpace` on colour maps only.
- `physicallyCorrectLights` is gone. Physical light units are the default, so old intensity values look dark.
  Multiply point and spot intensities by about 4 pi as a start, then tune by eye.
- `THREE.Clock` is deprecated since r183: use `THREE.Timer` (`timer.update()` once per frame, then `timer.getDelta()`).
- `RGBELoader` is deprecated since r180: use `HDRLoader` from `three/addons/loaders/HDRLoader.js`.
- `PCFSoftShadowMap` is deprecated since r186 and falls back to `PCFShadowMap`, which now filters soft.
- Import addons from `three/addons/...` (an import map or a bundler), not from `examples/js`.
- Check any other name in the current docs when it does not resolve.

<!-- skill-navigation:start -->
## Reading Map

- [three.js](#threejs)
- [From Blender to three.js](#from-blender-to-threejs)
- [Loading and compression](#loading-and-compression)
- [Materials and colour](#materials-and-colour)
- [Animation](#animation)
- [Lights, shadows and environment](#lights-shadows-and-environment)
- [Camera and controls](#camera-and-controls)
- [Performance](#performance)
- [Video and stills from a page](#video-and-stills-from-a-page)
<!-- skill-navigation:end -->

Ready assets: CodePawl's free GLB packs on Hugging Face (https://huggingface.co/codepawl) ship web, KTX2, LOD and mobile tiers made for three.js, each with a viewer Space. An agent-driven engine on top of WebGL2: [Crucible](https://github.com/codepawl/crucible).

## From Blender to three.js

**Export a GLB**
1. Apply scale and rotation (Ctrl+A, All Transforms). Keep 1 Blender unit = 1 metre.
2. File > Export > glTF 2.0. Format glTF Binary (.glb). Include: Selected Objects when exporting one asset.
3. Transform: +Y Up on. Geometry: Apply Modifiers on, UVs, Normals, Vertex Colors only if used.
4. Animation: export each action as its own clip (NLA tracks or Actions mode). Sampling on for constraints and IK.
5. Materials: Principled BSDF maps to `MeshStandardMaterial` or `MeshPhysicalMaterial`. Procedural nodes do not
   export, so bake them to image textures first.
- Use when / pitfalls: an object that looks huge or rotated had unapplied transforms. Shape keys export as morph
  targets only when the mesh has no modifiers that change vertex count.
- Source: [GLTFLoader docs](https://threejs.org/docs/#examples/en/loaders/GLTFLoader)

**Check the file before code**
1. Drop the GLB into the official viewer at gltf-viewer.donmccurdy.com or threejs.org/editor.
2. Look at scale, materials, clips and the triangle count in the info panel.
- Use when / pitfalls: if it is wrong in the viewer, fix it in Blender, not in code.
- Source: [three.js editor](https://threejs.org/editor/)

## Loading and compression

**Load a GLB**
1. `const loader = new GLTFLoader();`
2. `const gltf = await loader.loadAsync('model.glb'); scene.add(gltf.scene);`
3. Read clips from `gltf.animations`.
- Source: [GLTFLoader docs](https://threejs.org/docs/#examples/en/loaders/GLTFLoader)

**Compress meshes and textures**
1. Run `npx @gltf-transform/cli optimize in.glb out.glb --compress meshopt --texture-compress ktx2`.
2. In code: `loader.setMeshoptDecoder(MeshoptDecoder)` and a `KTX2Loader` with `detectSupport(renderer)` set by
   `loader.setKTX2Loader(ktx2)`. For Draco files, set a `DRACOLoader` instead.
- Use when / pitfalls: KTX2 cuts GPU memory as well as download size. Keep normal maps in UASTC, colour in ETC1S
  when size matters more than detail.
- Source: [KTX2Loader docs](https://threejs.org/docs/#examples/en/loaders/KTX2Loader)

## Materials and colour

**Colour that matches Blender**
1. Colour textures: `colorSpace = SRGBColorSpace`. Normal, roughness, metalness and AO maps stay linear.
2. Tone mapping: `renderer.toneMapping = THREE.AgXToneMapping` to match Blender's AgX view, or
   `ACESFilmicToneMapping`. Use `NoToneMapping` for unlit, painted styles.
3. Flat painted characters: `MeshBasicMaterial` with the texture, and `toneMapped: false` on the material.
- Use when / pitfalls: washed-out colour means a colour map left linear. Grey painted swatches mean tone mapping on
  an unlit style.
- Source: [Color management](https://threejs.org/docs/#manual/en/introduction/Color-management)

**Toon look**
1. `MeshToonMaterial` with a small `gradientMap` texture (3 to 5 pixels wide, `NearestFilter`).
2. Outlines: the `OutlinePass` in post, or an inverted hull copy of the mesh with `side: BackSide` and a scaled normal.
- Source: [MeshToonMaterial docs](https://threejs.org/docs/#api/en/materials/MeshToonMaterial)

**Pixel or PS1 texture look**
1. `texture.magFilter = THREE.NearestFilter`, `texture.minFilter = THREE.NearestFilter`, `generateMipmaps = false`.
2. Render to a small render target and scale it up for chunky pixels.
- Source: [Texture docs](https://threejs.org/docs/#api/en/textures/Texture)

## Animation

**Play and blend clips**
1. `const mixer = new THREE.AnimationMixer(gltf.scene);`
2. `const walk = mixer.clipAction(THREE.AnimationClip.findByName(gltf.animations, 'Walk'));` then `walk.play()`.
3. Each frame: `timer.update()`, then `mixer.update(timer.getDelta())` with `const timer = new THREE.Timer()`.
4. Blend: `idle.crossFadeTo(walk, 0.3, true)`.
- Use when / pitfalls: a character that slides needs root motion handled in code or removed in Blender. A clip that
  pops at the loop needs first and last keys equal.
- Source: [Animation system](https://threejs.org/docs/#manual/en/introduction/Animation-system)

**Morph targets for faces**
1. Find the mesh, then `mesh.morphTargetDictionary['Smile']` gives the index.
2. Set `mesh.morphTargetInfluences[index] = 0.8`, or key them in a clip from Blender shape keys.
- Source: [Mesh docs](https://threejs.org/docs/#api/en/objects/Mesh)

## Lights, shadows and environment

**Image-based light**
1. Load an HDR from Poly Haven with `HDRLoader` (`RGBELoader` before r180).
2. `scene.environment = pmrem.fromEquirectangular(hdr).texture` with a `PMREMGenerator`.
- Use when / pitfalls: one HDR gives most of a realistic look. Add a directional light only for crisp shadows.
- Source: [PMREMGenerator docs](https://threejs.org/docs/#api/en/extras/PMREMGenerator)

**Shadows**
1. `renderer.shadowMap.enabled = true`, `renderer.shadowMap.type = THREE.PCFShadowMap` (the default).
2. On the light: `castShadow = true`, set `shadow.camera` left, right, top and bottom tight around the scene,
   `shadow.mapSize` 2048, `shadow.bias` about -0.0005, `shadow.normalBias` about 0.02.
3. `castShadow` and `receiveShadow` on meshes.
- Use when / pitfalls: stripes on surfaces are shadow acne, raise normalBias. Blurry shadows mean the shadow camera
  covers too much area.
- Source: [DirectionalLightShadow docs](https://threejs.org/docs/#api/en/lights/shadows/DirectionalLightShadow)

## Camera and controls

**Orbit or a fixed shot**
1. `new OrbitControls(camera, renderer.domElement)` with `enableDamping = true` and `controls.update()` each frame.
2. For a film shot, animate `camera.position` and a look-at target on a curve (`CatmullRomCurve3`) instead.
3. Match a Blender lens: three.js `fov` is vertical. Convert from focal length with
   `camera.setFocalLength(mm)` after setting `filmGauge` to 36.
- Source: [PerspectiveCamera docs](https://threejs.org/docs/#api/en/cameras/PerspectiveCamera)

## Performance

**Keep 60 fps on a phone**
1. `renderer.setPixelRatio(Math.min(devicePixelRatio, 2))`.
2. Many copies of one mesh: `InstancedMesh`. Many static meshes with one material: merge them.
3. Watch `renderer.info.render.calls` (draw calls) and triangles. Aim under about 200 calls on mobile.
4. Dispose geometry, materials and textures you remove.
- Use when / pitfalls: frame time in a headless browser lies unless you force a GPU sync each frame.
- Source: [How to dispose of objects](https://threejs.org/docs/#manual/en/introduction/How-to-dispose-of-objects)

## Video and stills from a page

**Render frames for a video**
1. Drive time from a frame counter, not the clock: `t = frame / fps`.
2. Render each frame, read it with `canvas.toBlob` or a headless browser screenshot, then join with ffmpeg.
3. Use `preserveDrawingBuffer: true` on the renderer when reading the canvas.
- Use when / pitfalls: real-time capture drops frames. A fixed time step gives a smooth video at any speed.
- Source: [WebGLRenderer docs](https://threejs.org/docs/#api/en/renderers/WebGLRenderer)
