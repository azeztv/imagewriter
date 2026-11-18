# Unity

Getting a Blender asset or scene into Unity 6: import, terrain, lighting, a character controller, animation, a follow camera, simple AI, a menu and a build. The series predates URP and HDRP (Unity 4/5 era, UnityScript code), so every name and path below is mapped to Unity 6 where I am sure.

<!-- skill-navigation:start -->
## Reading Map

- [Unity](#unity)
- [Version names](#version-names): read first
- [From Blender to Unity](#from-blender-to-unity)
- [Project setup and terrain](#project-setup-and-terrain)
- [Lighting and sky](#lighting-and-sky)
- [Character and camera](#character-and-camera)
- [Animation](#animation)
- [Enemy AI](#enemy-ai)
- [Menu and build](#menu-and-build)
- [Video output](#video-output)
<!-- skill-navigation:end -->

## Version names

- UnityScript (the `.js` scripts in the series) is gone. Write C#. Every code line below is the C# equivalent, not the video's text.
- Legacy Animation component (`animation.CrossFade("walk", 0.2)`) is replaced by Animator with an Animator Controller (Mecanim). The legacy component still exists but is deprecated. Check in the editor before using it.
- Built-in render pipeline with the Standard shader is now one of three pipelines. New Unity 6 3D projects usually start on URP (Lit shader). Convert old materials with Window > Rendering > Render Pipeline Converter (check in the editor).
- Terrain "Edit Textures" (Add Texture) became Terrain Layers. Add them in Paint Texture > Edit Terrain Layers > Create Layer.
- Terrain brush tools still exist: Raise or Lower Terrain, Paint Texture, Paint Trees, Smooth Height. Hotkeys changed between versions, check the tool help.
- Standard Assets (default skyboxes, first and third person controllers) were removed from Unity. The series' `Assets > Import Package > Skybox` no longer exists. Get a skybox from the Asset Store, a CC0 HDRI, or use the Skybox/Procedural material.
- Render Settings skybox slot (old Edit > Render Settings) is now the Lighting window: Window > Rendering > Lighting > Environment > Skybox Material.
- `OnGUI` and `GUI.Button` (IMGUI) are still in the engine but meant for debug. Menus use uGUI (Canvas, Button, TextMeshPro) or UI Toolkit.
- Old `Input.GetAxis` and `Input.GetKey` belong to the Input Manager. Unity 6 projects often default to the Input System package. Project Settings > Player > Active Input Handling can be set to Both. Check in the editor.
- `Application.LoadLevel` became `SceneManager.LoadScene`. Build Settings is now File > Build Profiles in Unity 6 (the scene list lives there). Check the menu in your version.
- Cinemachine is now a package, version 3 in Unity 6: Cinemachine Camera replaces Virtual Camera. Not from the video.
- Unity 6 names to look for: Timeline is Window > Sequencing > Timeline. AI Navigation (NavMeshSurface) is a package. Both not from the video.

## From Blender to Unity

This section is not from the video unless a Source line says so. It is the standard route and I am confident of each setting. Check labels in your Blender and Unity versions.

- **Export FBX from Blender**
  1. Select the mesh and armature. File > Export > FBX (.fbx).
  2. In the right panel tick Selected Objects.
  3. Transform: Scale 1.0, Apply Scalings = FBX Units Scale, Forward = -Z Forward, Up = Y Up. These are the defaults and give scale 1 in Unity when the Blender scene unit is metres.
  4. Tick Apply Transform if you see 100x scale or rotated objects. It bakes the fix into the mesh, but it can break animation on rigs, so try it only on static props.
  5. Geometry: Apply Modifiers on. Smoothing Face or Normals Only.
  6. Armature: untick Add Leaf Bones. Leaf bones add useless end bones that Unity shows and Humanoid mapping can trip on. Tick Only Deform Bones if you use control bones such as IK targets.
  7. Bake Animation on. Untick NLA Strips for a single clip. Tick All Actions to export every action as a clip.
- Use when / pitfalls: a model that arrives 100 times too big or lying on its side is a scale or axis setting. Fix it at export, not with scale 100 on the Unity object. Do not rely on the Unity scale field to cure it, since colliders and physics follow the real size.
- Source: not from the video.

- **Scale check in Unity**
  1. Drop the FBX into the Project window.
  2. Select it. Model tab > Scale Factor 1 and Convert Units on.
  3. Drag it into the scene next to a default Cube (1 m). A person should be about 1.7 m, a door about 2 m.
  4. In the video the author scales whole prefabs instead (houses, golem 0.15) after comparing the character to a door.
- Use when / pitfalls: compare against a known object. Scale the prefab root, never single bones.

- **Rig type: Humanoid or Generic**
  1. Select the FBX. Rig tab > Animation Type.
  2. Humanoid: retargets animation between different characters. Click Configure and check every bone turns green. The rig needs a T-pose or A-pose in the Blender file.
  3. Generic: for creatures, props and anything non-human. Set Root node to the armature root bone.
  4. Click Apply.
- Use when / pitfalls: Humanoid wants one hips bone, two legs, two arms, a head. Mixamo-style bone names map without work. A quadruped or a prop must be Generic. The series' characters play their own clips, so Generic fits that setup. Not from the video.
- Source: not from the video.

- **Extract materials and textures**
  1. Select the FBX. Materials tab.
  2. Click Extract Textures and pick a folder, then Extract Materials and pick a folder.
  3. Unity now uses the extracted material assets, so you can edit colours, shaders and tiling.
  4. If the surface is pink, the shader does not match the pipeline. Use the Render Pipeline Converter or set the shader to Universal Render Pipeline/Lit.
- Use when / pitfalls: Blender node trees do not export. Only Base Color, normal and a few values survive in a Principled BSDF. Bake or rebuild metallic and roughness maps by hand. In the series a prefab's textures also went missing after moving folders (houses lost their texture at ), so keep textures beside the model.

- **Split animation clips and loop time**
  1. Select the FBX. Animation tab.
  2. If Blender exported every action, each shows in the Clips list with a name such as `Armature|Walk`. Rename clips here.
  3. If you exported one long timeline, press + under Clips and set Start and End frame per clip (idle, walk, run).
  4. Tick Loop Time for idle, walk and run. Tick Loop Pose if the first and last frame match.
  5. Root Transform Rotation, Y and XZ: tick Bake Into Pose for in-place clips.
  6. Click Apply.
- Use when / pitfalls: a clip that pops at the loop point has mismatched first and last keys. Fix it in Blender, see `animation-and-nla.md`. Frame ranges follow Blender's frame numbers at the scene fps.

- **Keep animations in place for the controller**
  1. In Blender, animate walk, run and jump without moving the hips forward or up in world space.
  2. Keep the mesh inside the capsule. A hand or foot sticking out is fine, the root must not leave.
  3. In Unity, Bake Into Pose on Root Transform Y and XZ, and Apply Root Motion off on the Animator.
- Use when / pitfalls: the author's jump clip lifted the mesh itself, so the capsule and the mesh separated and the character poked through trees. He tells the animator to flatten the Y curve in the graph editor and let code lift the character. Stick-a-sticker test: a sticker on the belly must not rise.

## Project setup and terrain

- **Terrain from scratch**
  1. GameObject > 3D Object > Terrain.
  2. Terrain Settings (gear icon) > Mesh Resolution: set Terrain Width and Length smaller than the default so the map is not huge.
  3. Switch to the Sculpt tools. Draw a ring of hills around the edge so the player cannot walk out.
  4. Raise with a plain click, lower with Shift (in the video Shift digs, check your version).
  5. Use Smooth Height to soften peaks.
  6. Press Play and look from the game camera.
- Use when / pitfalls: keep the terrain basic. The author says the look comes from objects and textures added later. Terrain shortcuts resemble Blender sculpt: Alt rotates, Ctrl+Alt zooms in his tablet setup.

- **Tiling ground textures**
  1. Download tileable (seamless) textures, for example from CG Textures style sites. In Blender-world terms use Poly Haven or ambientCG.
  2. Terrain > Paint Texture > Edit Terrain Layers > Create Layer, pick the texture.
  3. The first layer fills the whole terrain. Open the layer and set Tiling Size. In the video 1 was too fine, 5 too big, 2 worked for grass and 4 for the rock layer.
  4. Add a second layer for hills and paint it. Lower Brush Size and Opacity for edges.
- Use when / pitfalls: if the texture looks huge, the tile size is too big. Seams show when the texture is not tileable.

- **Painting trees**
  1. Terrain > Paint Trees > Edit Trees > Add Tree Prefab, choose the tree prefab.
  2. Wind: the video sets bend factor to zero because wind is costly.
  3. If trees refuse to paint, the prefab is too large. Lower the scale (the video used 0.05 in the tree settings) and apply.
  4. Paint with a small brush, then rotate and scale some by hand.
- Use when / pitfalls: one tree model repeats. Rotate and scale copies so the repetition is less visible. Check that trunks touch the ground.

- **Dressing the level with props**
  1. Drag prefabs (barrels, carts, tents, rocks, plants, houses) from the Project window into the scene.
  2. Select one and press F to frame it. Duplicate with Ctrl+D (Cmd+D on Mac).
  3. Rotate each copy a different amount on Y. Scale some.
  4. Switch between Global and Local gizmos to seat a barrel on a cart. Zoom in to check nothing floats.
  5. Houses come in big on purpose so enemies can hide behind them. Scale them to game size, not to zero.
  6. Save the scene often (File > Save As, name it Level1).
- Use when / pitfalls: rocks and barrels carry most of a game's set dressing. Plants without colliders are walk-through, which the author keeps on purpose.

- **Hierarchy and folders**
  1. Create empty GameObjects named Props, Lighting and keep Main Camera and Terrain at the top level.
  2. Drag all props into Props, all lights into Lighting.
  3. In Project, make folders Visual (models and textures), Scripts and Levels.
- Use when / pitfalls: selecting the empty selects its children, so you can move a whole group. Empty objects act as folders.

- **Invisible walls**
  1. Create a Cube, stretch it to a wall, and put it at the map edge.
  2. Untick the Mesh Renderer so it is invisible but keep the collider.
  3. Place several around the terrain.
- Use when / pitfalls: stops characters leaving the terrain even if something glitches.

## Lighting and sky

- **Night skybox and mood**
  1. Get a skybox material. The series used the old Standard Assets package (Moonshine). Today use an Asset Store skybox, an HDRI, or Skybox/Procedural.
  2. Window > Rendering > Lighting > Environment > Skybox Material, drag the material in.
  3. Lights: change the scene's default Directional Light, or set it to Spot and place several lamps with an orange tint.
  4. Add one more Directional Light with a dark blue colour and low intensity. Rotate it until the shadows read well.
  5. Group all lights under Lighting.
- Use when / pitfalls: the author picks a night scene to hide a plain level. In URP intensity values are different from the 5.x ones in the video. Start low and raise it. Check the Lighting window for Auto Generate or baked lighting.

- **Darken a prefab's material**
  1. Select the tree or tent prefab and open its material.
  2. Change the colour tint to something darker. The texture's alpha stays.
  3. If you cannot find the material, search the Project window for the texture name.
- Use when / pitfalls: a bright leaf texture looks wrong at night. Tinting is faster than editing the image.

- **Light that follows a character**
  1. GameObject > Light > Point Light. Make it a child of the character's top object.
  2. Place it a little above and behind the character.
  3. Lower intensity, shorten Range, choose a blue colour so the floor around the player glows.
  4. For enemies, add a smaller orange point light as a child.
- Use when / pitfalls: do not edit objects while Play mode is on, changes are lost when you stop. Test lighting in the Game view, because Preview quality in the editor differs from a build.

## Character and camera

- **Pivot and parent for the player**
  1. Create an empty GameObject at the character's head height. Name it Golem.
  2. Drag the character model inside it as a child.
  3. Use the Pivot toggle (not Center) when you move it, so the gizmo sits on the empty.
  4. Add a child Sphere named Target behind the character. It marks where the camera should sit.
- Use when / pitfalls: the author uses a sphere only to see the point, then removes its Mesh Renderer and Collider. An empty named Target works the same.

- **Follow camera by script**
  1. Create `CameraMovement` and attach it to the camera.
  2. Find the target: `targetCamera = GameObject.Find("Target").transform` (the video fixes a type error by passing `.transform`).
  3. Each frame, move with `transform.position = Vector3.Lerp(transform.position, targetCamera.position, speed * Time.deltaTime)`.
  4. Look at the character: `transform.rotation = Quaternion.Slerp(transform.rotation, Quaternion.LookRotation(characterHead.position - transform.position), speed * Time.deltaTime)`.
  5. Aim at the character's head object, not the pivot of the model, so the camera does not look at the feet.
  6. Distance from the target sphere to the player sets the camera distance. Raise Target higher and farther to hide a low-poly model.
- Use when / pitfalls: low speeds make the camera lag smoothly. The video's camera can pass through trees, which third-person games often do. In Unity 6 use a Cinemachine Camera with Tracking Target and Third Person Follow or Orbital Follow instead (not from the video).

- **Character Controller component**
  1. Select the character's top object. Add Component > Physics > Character Controller.
  2. Set Center Y so the capsule sits on the feet (the video used -0.65 for its model).
  3. Set Height and Radius to wrap the body. Leave a small gap under the feet.
  4. Slope Limit sets the steepest slope it can climb.
  5. The script that calls Move must sit on the same object as the controller.
- Use when / pitfalls: it handles collisions and height, but you write the motion. Animations that move the mesh outside the capsule look wrong near trees, see the in-place entry above.

- **Walk, turn, gravity and run**
  1. In `Awake` or `Start`: `controller = GetComponent<CharacterController>()`.
  2. Each frame: `moveDirection = new Vector3(0, 0, Input.GetAxis("Vertical"))`. The axis goes from 0 to 1 gradually and to -1 backwards.
  3. Convert to local space: `moveDirection = transform.TransformDirection(moveDirection)`. Without it the character moves along world Z whatever way it faces.
  4. Multiply by speed. `controller.Move(moveDirection * Time.deltaTime)`. Do not multiply by deltaTime twice.
  5. Turn with `transform.Rotate(0, Input.GetAxis("Horizontal") * rotateSpeed * Time.deltaTime, 0)`. Move does not rotate.
  6. Gravity: `moveDirection.y -= gravity * Time.deltaTime` before Move. The video first sets Y to minus gravity, then multiplies by deltaTime.
  7. Run: if `Input.GetKey(KeyCode.LeftShift) || Input.GetKey(KeyCode.RightShift)` multiply the forward part by `runSpeed` (the video uses 4 against speed 2).
  8. Expose `speed`, `rotateSpeed`, `runSpeed`, `gravity` as public fields and tune in the Inspector. A value of zero means no movement.
- Use when / pitfalls: the Input Manager axes are in Project Settings > Input Manager (Vertical has positive Up and negative Down). With the new Input System package use an Input Action asset instead. Not from the video.

- **Jump**
  1. Test `controller.isGrounded`. Only allow movement and jumping when true.
  2. On `Input.GetKeyDown(KeyCode.Space)` set `moveDirection.y = jumpSpeed`.
  3. Gravity pulls it back down. In the video gravity 20 and jump speed 5 gave a decent jump.
- Use when / pitfalls: the author cuts the jump from the final game because his clip moved the mesh up. A jump clip must stay in place.

- **Shared values in one script**
  1. Create `Global` with `public static float deltaTime`, `fixedTime` and `gravity`.
  2. In `Update` assign `deltaTime = Time.deltaTime`.
  3. Attach `Global` to the camera so it exists in the scene.
  4. Other scripts read `Global.deltaTime`.
- Use when / pitfalls: the video's reason is fewer calls to Time. In C# calling `Time.deltaTime` is cheap, so this is only for tidiness. A static field set in `Update` is only valid while the object lives. Set a constant like gravity in the declaration.

## Animation

- **Switch clips by input (legacy Animation)**
  1. Put idle, walk, run in the model's Animation component list.
  2. Find the model child: `characterContent = transform.Find("Perso")`.
  3. No key held: `characterContent.animation.CrossFade("idle", 0.2f)`.
  4. Up or Down held: CrossFade "walk". With Shift also held: CrossFade "run".
  5. Use CrossFade, never plain Play, so clips blend.
- Use when / pitfalls: in Unity 6 do the same with an Animator Controller. Make states Idle, Walk, Run, add a float Speed parameter, and drive transitions with `animator.SetFloat("Speed", value)` or a Blend Tree. The video first used two booleans, then found testing the keys directly simpler. Not from the video for the Animator form.

## Enemy AI

- **Enemy setup**
  1. Create an empty named Enemy. Drag the skeleton model inside. Reset its local position to 0, 0, 0.
  2. Remove particle effects that come with the sample model if they look wrong.
  3. Scale the empty (the video uses 1.5) rather than the model.
  4. Add a Character Controller. Reduce Height and Radius and raise Center to fit the body.
  5. Attach the AI script to the Enemy empty, not to the model child. Dropping a script from Project onto the scene may attach it to a child.
- Use when / pitfalls: the enemy's run clip is played the same way as the player's.

- **Wander in random directions**
  1. Each frame: `moveDirection = transform.TransformDirection(Vector3.forward) * speed`, then subtract gravity on Y, then `controller.Move(moveDirection * Time.deltaTime)`.
  2. Keep two floats: `changeRotation` (a timer) and `delayRotation` (a wait).
  3. If `changeRotation + delayRotation < Time.time` pick `randomAngle = Random.Range(0, 361)`, set `transform.rotation = Quaternion.Slerp(transform.rotation, Quaternion.Euler(0, randomAngle, 0), 0.5f)`, then `changeRotation = Time.time` and `delayRotation = Random.Range(1, 6)`.
  4. The video rotates by a random Y angle every 1 to 5 seconds.
- Use when / pitfalls: random values are drawn once, so put them inside the timed condition. Gravity must be applied to the Y component only, subtracting from a whole Vector3 is a compile error.

- **Obstacle avoidance with a ray**
  1. Add a child empty named Origin at the enemy's eyes. Zero its rotation.
  2. `if (Physics.Raycast(origin.position, origin.forward, out hit, 5))` then turn around: `transform.rotation = transform.rotation * Quaternion.Euler(0, 180, 0)`. Multiplying quaternions adds rotations.
  3. Only pick a new random angle in the else branch.
  4. Draw it with `Debug.DrawRay(origin.position, origin.forward * 5, Color.red, 1)` and watch the Scene view.
  5. Add `OnControllerColliderHit(ControllerColliderHit hit)` and turn 180 degrees on any touch. It catches tree leaves that the ray slips between.
- Use when / pitfalls: AI is random, so write down every odd behaviour you see while testing. For real pathfinding use the AI Navigation package and NavMeshAgent (not from the video).

## Menu and build

- **Main menu scene**
  1. File > New Scene. Select the camera and set Clear Flags to Solid Color with a dark grey.
  2. Add a title text. In old Unity it was a GUIText, now use GameObject > UI > Text - TextMeshPro. Anchor to the centre and raise it a bit.
  3. Add a Start button below.
  4. Save the scene as Menu in the Levels folder.
- Use when / pitfalls: place the menu first in the scene list. The video puts it at index 0.

- **Button with OnGUI (old) and its replacement**
  1. The video draws in `OnGUI`: `if (GUI.Button(new Rect(Screen.width / 2 - 100, Screen.height / 2, 200, 50), "Start game")) { ... }`. A Rect is x, y, width and height from the top left.
  2. Subtract half the button width from the centre position or the button starts at the centre.
  3. In the braces load the game scene. Today: `SceneManager.LoadScene("Level1")`.
  4. In Unity 6 create a Canvas, a Button and hook On Click to a public method. Not from the video.
- Use when / pitfalls: forgot to add scenes to the build and the button appears to do nothing. See the next entry.

- **Build list and music**
  1. File > Build Profiles (older: Build Settings). Add the open scenes, Menu first, then Level1.
  2. On the menu camera add Audio Source. Drag in a music clip, tick Loop. Keep volume low.
  3. Pick the platform and press Build. For a quick test the Play button is enough.
  4. Quality in the editor can be lower than in the build.
- Use when / pitfalls: if the first scene is wrong the game opens in the level. Reorder the list.

## Video output

Not from the video. For a rendered video rather than a game:
1. Install Cinemachine and Timeline from Package Manager.
2. Add a Cinemachine Camera, set Tracking Target and Look At, add a Timeline asset on an empty object.
3. Add Cinemachine Track with a Cinemachine Brain on the main camera, then cut between cameras with clips.
4. Record with the Recorder package (Window > General > Recorder), movie output, fixed frame rate.
- Use when / pitfalls: set the same fps as the Blender scene. Check package names in the Package Manager of your editor version.
- Source: not from the video.
