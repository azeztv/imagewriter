# Godot
Getting a Blender asset or scene running in Godot 4: nodes and scenes, import, materials, environment, lights, scripting in C#, input, character body, camera look-at, triggers, UI, shaders and builds.
<!-- skill-navigation:start -->
## Reading Map

- [Godot](#godot)
- [Version names](#version-names): read first
- [Orientation and Unity/Unreal map](#orientation-and-unityunreal-map)
- [Scenes and nodes](#scenes-and-nodes)
- [From Blender to Godot](#from-blender-to-godot)
- [Materials, environment and lights](#materials-environment-and-lights)
- [Scripting in C](#scripting-in-c)
- [Input and character movement](#input-and-character-movement)
- [Look-at, triggers and spawning](#look-at-triggers-and-spawning)
- [UI](#ui)
- [Shaders](#shaders)
- [Build and export](#build-and-export)
- [Rotations and quaternions](#rotations-and-quaternions)
<!-- skill-navigation:end -->
## Version names
The 3.5 hour video was recorded on Godot 3.x (Mono build). It says Godot 4.0 is "coming". Everything below is rewritten with Godot 4 names. The video only covers the editor, scripting, UI and shaders. It does not cover mesh import, animation or export, so those entries say "not in the video" and follow the Godot 4 manual. Check the editor when a name differs.
- Spatial is now Node3D. MeshInstance is MeshInstance3D. Camera is Camera3D. Area is Area3D. RayCast is RayCast3D.
- DirectionalLight is DirectionalLight3D. CollisionShape is CollisionShape3D.
- KinematicBody is CharacterBody3D. RigidBody is RigidBody3D. StaticBody is StaticBody3D.
- SpatialMaterial is StandardMaterial3D. Transform is Transform3D. Quat is Quaternion.
- `translation` is now `Position`. `GlobalTransform` and `GlobalPosition` exist in 4.
- `Instance()` on a PackedScene is now `Instantiate()`.
- `OS.GetTicksMsec()` is now `Time.GetTicksMsec()`.
- C# `_Process(float delta)` is now `_Process(double delta)`. The same goes for `_PhysicsProcess`.
- `MoveAndSlide(velocity, up)` is now `MoveAndSlide()`. It reads and writes the `Velocity` property and uses `UpDirection`.
- In C# 4.x signals are events, for example `button.Pressed += OnPressed`. The string `Connect` form still works through `Callable`.
- ProceduralSky is now a Sky resource with a ProceduralSkyMaterial. Set Background mode to Sky.
- Shader `hint_color` is now `source_color`. Built-ins are upper case: `TIME`, `UV`, `VERTEX`, `NORMAL`, `ALBEDO`, `ROUGHNESS`.
- NoiseTexture is NoiseTexture2D. OpenSimplexNoise is replaced by FastNoiseLite.
- The GLES3 and GLES2 renderers are replaced by Forward+, Mobile and Compatibility. Pick one at project creation. Check in the editor which fits the target.
- The .NET build is its own download in Godot 4 and exports need the .NET SDK. Check in the editor for the current requirement.
## Orientation and Unity/Unreal map
- **Viewport keys match Blender**
  1. Middle mouse orbits, Shift + middle mouse pans, wheel zooms.
  2. Numpad 1 is front, 3 is right, 7 is top, 5 toggles perspective.
  3. Change any key in Editor > Editor Settings > Shortcuts. Search "front view" to find the binding.
  4. Gizmo keys are Q select, W move, E rotate, R scale. T switches local and global.
  - Use when / pitfalls: a Blender user feels at home. Godot has separate 2D and 3D workspaces, so a UI never floats in the 3D view.
- **Godot is node based, not component based**
  1. A scene is a tree of nodes. Behavior is added as a child node or as a script on a node.
  2. Add a node with Ctrl+A or the plus button. It becomes a child of the selected node.
  3. Drag a node in the Scene dock to reparent it.
  4. Every scene has one root. Right click > Make Scene Root to change it. Right click > Change Type swaps the node class.
  - Use when / pitfalls: no AddComponent exists. Two siblings cannot share a name, Godot appends a number.
- **Unity and Unreal words in Godot**
  1. Prefab or Blueprint is a saved scene, instanced into other scenes.
  2. Start is `_Ready`. Update is `_Process`. FixedUpdate is `_PhysicsProcess`.
  3. SerializeField is `[Export]`. Input Manager is the Input Map in Project Settings.
  4. CharacterController is CharacterBody3D with `MoveAndSlide`.
  5. Camera looks down -Z and up is +Y.
  - Use when / pitfalls: the video states the camera forward is minus Z. Unity forward is plus Z, so ported look-at code flips.
- **Play runs the real game, not the editor**
  1. Press Play. Godot asks for a main scene on first run.
  2. Set it later in Project Settings > Application > Run > Main Scene.
  3. The game is a separate process. Procedural meshes do not preview in the editor.
  - Use when / pitfalls: unlike Unity, Play mode does not edit the live scene. Use the Remote tab in the Scene dock to inspect the running tree.
## Scenes and nodes
- **Primitive meshes and resource properties**
  1. Add a MeshInstance3D.
  2. In the Mesh property choose New BoxMesh (also Sphere, Cylinder, Plane).
  3. Click the resource to edit its size and subdivisions. Change the view mode to Display Wireframe from the viewport menu.
  - Use when / pitfalls: scale the mesh resource, not the node. Keep node scale at 1 so collision shapes and children stay correct. The video calls scaling a parent node a mistake it often makes.
- **Save a branch as a scene (prefab)**
  1. Right click a node in the Scene dock > Save Branch as Scene.
  2. Drag the saved .tscn into another scene to instance it.
  3. Edit the source scene and every instance updates.
  4. To override a child on one instance: right click it > Editable Children.
  - Use when / pitfalls: attach scripts to the root of the saved scene, not to one instance. Overridden values show in red.
## From Blender to Godot
These entries are not in the video. They follow the Godot 4 import manual and are limited to what is stable in Godot 4. Their source is the Godot manual, not the video.
- **Export a GLB from Blender**
  1. File > Export > glTF 2.0. Format: glTF Binary (.glb).
  2. Include: Selected Objects if you only want part of the scene. Keep Transform > +Y Up on.
  3. Mesh: Apply Modifiers on. Keep Normals on. Add Tangents only if the material has a normal map.
  4. Animation: keep Animation on, Group by NLA Track if you have several actions. Skinning on for a rig.
  5. Save the .glb inside the Godot project folder. Godot imports it on focus.
  - Use when / pitfalls: apply object scale and rotation first (Ctrl+A) so the root is 1, 1, 1. Godot reads scenes as meters, the same as Blender.
  - Source: [Godot manual, importing 3D scenes](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/index.html)
- **Facing direction, -Y forward and the Z flip**
  1. Blender characters usually face -Y. The glTF exporter converts that to glTF forward, which is +Z.
  2. Godot treats -Z as forward for cameras, `LookAt` and movement. A model exported from -Y faces +Z, so it looks backward.
  3. Fix once: wrap the imported model in a Node3D and rotate the child 180 degrees on Y. Run gameplay code on the wrapper.
  4. Alternative: rotate the model in Blender before export. Check the result in the editor.
  - Use when / pitfalls: do not flip the basis in code every frame. The video fights this exact flip during look-at and recommends fixing the character's axis.
  - Source: [Godot manual, importing 3D scenes](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/index.html)
- **Name suffixes read on import**
  1. Name objects in Blender before export. Godot reads the suffix in Godot 4.
  2. `-col` adds a trimesh static collider and keeps the mesh. `-convcol` adds a convex collider.
  3. `-colonly` and `-convcolonly` keep only the collider, the mesh is removed.
  4. `-rigid` makes a RigidBody3D. `-noimp` skips the object. `-navmesh` makes a NavigationRegion3D.
  5. Animation clips ending in `-loop` or `-cycle` import with loop on.
  - Use when / pitfalls: the video builds colliders by hand with StaticBody3D plus CollisionShape3D. Suffixes do the same on import. Verify with Visible Collision Shapes in the Debug menu.
  - Source: [Godot manual, importing 3D scenes](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/index.html)
- **Import settings and re-import**
  1. Select the .glb in the FileSystem dock. The Import dock opens beside the Scene dock.
  2. Change options and press Reimport. Use Advanced for per-mesh, per-material and per-animation settings.
  3. Right click the .glb > New Inherited Scene to add scripts, collision and child nodes.
  4. Re-export from Blender over the same file. Godot reimports and the inherited scene keeps your additions.
  - Use when / pitfalls: never edit inside the imported scene. A reimport wipes those edits. Add everything in the inherited scene or in a wrapper scene.
  - Source: [Godot manual, importing 3D scenes](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/index.html)
- **Animation import and loop flags**
  1. Actions in the .glb become clips in an AnimationPlayer inside the imported scene.
  2. Open Advanced Import Settings > select an animation to see Loop Mode and trimming. Or use the `-loop` suffix.
  3. Set the loop for walk and idle clips. Leave jumps and attacks as one-shot.
  4. To edit a clip, use Save to File in the animation import options, then change it outside the .glb.
  - Use when / pitfalls: an unlooped walk freezes at its last frame. Match the first and last pose in Blender before export. The video says animation is not covered.
  - Source: [Godot manual, importing 3D scenes](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/index.html)
- **AnimationPlayer and AnimationTree**
  1. Play a clip from code with `GetNode<AnimationPlayer>("AnimationPlayer").Play("walk")`.
  2. For blending add an AnimationTree. Set Tree Root to an AnimationNodeStateMachine or BlendTree and set Anim Player.
  3. Enable Active. Blend Space 1D or 2D mixes walk and run from a speed value.
  4. Drive it with parameters, for example `animationTree.Set("parameters/blend_position", speed)`.
  - Use when / pitfalls: not covered in the video. Parameter paths show in the Inspector under Parameters. Copy them from there.
  - Source: [Godot manual, importing 3D scenes](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/index.html)
## Materials, environment and lights
- **StandardMaterial3D basics**
  1. On a MeshInstance3D set Material Override or Surface Material to New StandardMaterial3D.
  2. Change Albedo color, Roughness and Metallic. A preview sits at the top of the resource.
  3. Under Transparency enable it for alpha. The video turns on Transparency to fade a box.
  - Use when / pitfalls: it is an all in one material, like Blender's Principled BSDF.
- **WorldEnvironment, sky and post effects**
  1. Add a WorldEnvironment node. It warns until you add an Environment resource, so create one.
  2. Background mode: Sky. Add a Sky with a ProceduralSkyMaterial, or load an HDR panorama.
  3. Ambient Light source: Sky, or set a color and energy.
  4. Enable SSAO, SSR, Glow and Adjustments (brightness, contrast, saturation). Color correction takes a gradient texture.
  5. Save the Environment as a file to reuse it in other scenes.
  - Use when / pitfalls: with no sky and no GI the scene is black. In Godot 4 also check Tonemap and SDFGI in the same resource.
- **Directional light and shadows**
  1. Ctrl+A > DirectionalLight3D. Rotate it to aim.
  2. Tint the color slightly. A pure white light looks flat.
  3. Light > Shadow > Enabled. The shadow color is editable in Godot 3. In 4 check the shadow settings in the editor.
  4. Lower ambient energy when the sky already lights the scene.
  - Use when / pitfalls: contact shadows gave more artifacts than gain in the video. Lights and sky stack, so avoid doubling them.
## Scripting in C#
- **Create and attach a C# script**
  1. Select the node. In Inspector > Script choose New Script. Language: C#. Or right click in FileSystem > New Script.
  2. The class name must match the file name.
  3. Open the generated solution (.sln) in Visual Studio or VS Code.
  4. Extend `Node3D` when you need Transform. `Node` alone has none.
  - Use when / pitfalls: the class must be `partial` in Godot 4. Attach to the root of a saved scene. After deleting a .cs file, clean the solution and reopen the editor if the build errors.
- **_Ready and _Process**
  1. Override `_Ready()` for setup. Use `GD.Print($"Hello {Name}")` to log.
  2. Override `_Process(double delta)` for per frame work. Delta is passed in. There is no static Time.deltaTime.
  3. For elapsed time add delta to a field, or use `Time.GetTicksMsec() * 0.001`.
  - Use when / pitfalls: engine start time is not zero because of the splash screen. A field that counts from zero is more predictable.
- **Change a transform**
  1. Read it: `Transform3D transform = GlobalTransform;`
  2. Change `transform.Origin` or call `transform.Rotated(Vector3.Up, angle)`.
  3. Write it back: `GlobalTransform = transform;`
  4. Shortcut: `Position = newPosition` for local position.
  - Use when / pitfalls: Transform3D is a struct. Editing the copy does nothing until you assign it back, which the video calls a beginner trap. `Rotated` returns a new transform, so assign the result.
```csharp
public partial class Bobber : Node3D
{
    private double time;
    public override void _Process(double delta)
    {
        time += delta;
        Vector3 position = Position;
        position.Y = 2.0f + Mathf.Sin((float)time);
        Position = position;
    }
}
```
- **Export fields and reference nodes**
  1. Add `[Export]` to a public field. Build the solution to see it in the Inspector.
  2. In Godot 3 only NodePath and basic types export. Use `[Export] NodePath TargetPath;` and `GetNode<Target>(TargetPath)`.
  3. Godot 4 can export node types directly, for example `[Export] Node3D Target;`. Check in the editor.
  4. Get a child by name with `GetNode<RayCast3D>("GroundRayCast")`. A wrong name errors.
  - Use when / pitfalls: a scene saved as a prefab cannot point at nodes outside itself. Spawn the target or find it by name.
## Input and character movement
- **Input Map actions**
  1. Project > Project Settings > Input Map. Type an action name and press Add.
  2. Press the plus on the action and press the key to bind.
  3. In code: `Input.GetActionStrength("move_up")` gives 0 to 1.
  4. `Input.IsActionJustPressed("jump")` fires once per press.
  - Use when / pitfalls: this beats testing key events in `_Input`, which the video tries first and calls clunky. It supports gamepads with no code change.
- **Direction vector and normalizing**
  1. `float vertical = Input.GetActionStrength("move_down") - Input.GetActionStrength("move_up");`
  2. Do the same for horizontal with left and right.
  3. `Vector3 direction = new Vector3(horizontal, 0, vertical).Normalized();`
  - Use when / pitfalls: forward is -Z, so the up key is a negative Z value. Without Normalized, diagonals move faster.
- **Character body with MoveAndSlide**
  1. Use a CharacterBody3D with a CollisionShape3D child. Floors are StaticBody3D with a collision shape.
  2. Work in `_PhysicsProcess(double delta)`.
  3. Set `Velocity` from direction times speed. Call `MoveAndSlide()`.
  4. The body slides along walls and slopes instead of stopping.
  - Use when / pitfalls: do not multiply the velocity by delta before MoveAndSlide, it applies delta itself. Do multiply gravity by delta, because it is an acceleration. The video finds this confusing.
- **Gravity, friction and jump**
  1. Each physics frame `velocity.Y -= gravity * (float)delta;` with gravity about 9.8.
  2. Friction: `velocity -= velocity * friction * (float)delta` applied before MoveAndSlide.
  3. Jump: if `IsActionJustPressed("jump")` set `velocity.Y = jumpSpeed`. Add the ground check.
  4. Mark gravity, friction, speed and jump speed as `[Export]` to tune in the Inspector.
  - Use when / pitfalls: in Godot 4 use `IsOnFloor()` for the ground check. The video uses a downward RayCast only as a demo.
## Look-at, triggers and spawning
- **LookAt and the minus Z flip**
  1. `LookAt(target.GlobalPosition, Vector3.Up);` points the node's -Z at the target.
  2. `Transform3D.LookingAt(target, up)` returns a transform instead.
  3. A model built facing +Z points backward. Rotate the model child by 180 degrees on Y.
  4. The up vector must not be parallel to the look direction or the basis breaks.
  - Use when / pitfalls: the video flips the Z axis of the basis by hand and loses time on it. Fix the model orientation first.
- **Smooth look-at with Slerp**
  1. Compute the look-at basis, then `Quaternion to = look.Basis.GetRotationQuaternion();`.
  2. `Quaternion from = transform.Basis.GetRotationQuaternion();`
  3. `transform.Basis = new Basis(from.Slerp(to, (float)delta * turnSpeed));`
  4. Assign the transform back.
  - Use when / pitfalls: the third value is a fraction from 0 to 1 per frame, not a speed. Both quaternions must use the same forward convention, or the turn spins the wrong way. Quaternions must be normalized.
- **Trigger volume with Area3D and signals**
  1. Add Area3D. Add a CollisionShape3D child with a shape such as BoxShape3D. A mesh child shows the volume.
  2. Give the target a physics type. The video uses a kinematic body, which is CharacterBody3D in Godot 4.
  3. In C# connect the signals: `BodyEntered += OnBodyEntered;` and `BodyExited += OnBodyExited;`.
  4. The signal gives the other body. Log it or react.
  - Use when / pitfalls: the script must be attached to the Area, or no signal fires. The area only senses bodies that have a collision shape. The Node dock lists every signal of the selected node.
- **Change a material from code**
  1. Export a path to the MeshInstance3D and get it in `_Ready`.
  2. Read its material (Material Override, or surface material 0 from the mesh).
  3. Set the albedo color on a StandardMaterial3D, or use `SetShaderParameter` on a ShaderMaterial.
  4. Use white with alpha 1 and white with alpha 0 for solid and clear.
  - Use when / pitfalls: the video hit a null reference by reading the wrong slot. Check Material Override versus surface material. Transparency must be enabled on the material.
- **Spawn a physics prefab**
  1. Make a scene with a RigidBody3D root, a MeshInstance3D and a CollisionShape3D. Save it.
  2. `[Export] PackedScene Prefab;` and drag the file in the Inspector.
  3. `var body = Prefab.Instantiate<RigidBody3D>();`
  4. Set its position, then `GetTree().CurrentScene.AddChild(body);`
  5. Optional: `body.ApplyCentralForce(force)` or `ApplyTorque`.
  - Use when / pitfalls: an instance that is never added to the tree never appears. Box half extents are half the visible size. Use the Remote tab to confirm spawns.
## UI
- **Control nodes and layout**
  1. Switch to the 2D workspace. Add a Control and set Layout > Full Rect.
  2. Add a VBoxContainer as a child. Add Button children. They stack and stretch.
  3. Set Custom Minimum Size on buttons, Separation on the container and margins on a MarginContainer.
  4. Set anchors with the Layout menu so the UI scales with the window.
  - Use when / pitfalls: containers decide child position, so do not drag children inside one. Check at several window sizes.
- **Themes**
  1. On the root Control choose Theme > New Theme. Save it as a file.
  2. Edit Theme, Add Class Items, choose Button.
  3. Under Styles set normal to StyleBoxFlat. Edit bg color, border width, corner radius, shadow and expand margin.
  4. Every child Control inherits the theme.
  - Use when / pitfalls: the video sets Normal first. Hover and pressed states need their own style, so add them or the button looks dead.
## Shaders
- **Vertex wobble shader**
  1. On the mesh create a ShaderMaterial, then a new Shader.
  2. Write `shader_type spatial;` and `void vertex() { VERTEX += NORMAL * sin(TIME) * 0.1; }`.
  3. Add `void fragment()` for color.
  - Use when / pitfalls: the language is strict and needs floats, so write `0.1` not `1`. Changing vertices does not change normals, so lighting looks off.
- **Uniforms and noise textures**
  1. `uniform float time_factor = 1.0;` and `uniform float scale_factor = 0.1;`. They show under Shader Parameters.
  2. Change them from C# with `material.SetShaderParameter("scale_factor", 0.3f);`.
  3. `uniform sampler2D noise;`. Assign a NoiseTexture2D with a FastNoiseLite resource.
  4. Sample with `texture(noise, UV).r` and multiply it into the offset. Use `clamp(value, 0.0, 1.0)` to limit it.
  - Use when / pitfalls: use the red channel for a grey value. A seamless noise texture avoids a visible seam.
## Build and export
- **Export a build**
  1. Project > Export. Add a preset for the platform, for example Windows Desktop.
  2. Install the export templates when the editor asks (Editor > Manage Export Templates).
  3. Set the output path and press Export Project. Turn Export With Debug off for a release.
  4. For C# projects the .NET SDK must be installed. Check in the editor for the current requirement.
  - Use when / pitfalls: not covered in the video. The video shows that Play already runs a real standalone process, so test there first. Set the main scene or the exported game opens nothing.
## Rotations and quaternions
These notes come from the 10 minute quaternion video and hold in Blender, Unity, Unreal and Godot.
- **Orientation versus rotation, and Euler order**
  1. An orientation is where the object points. A rotation is the act of changing it.
  2. Euler angles split an orientation into X, Y and Z turns.
  3. The order matters. Y then X can differ from X then Y with the same numbers.
  4. Check which Euler order the engine or Blender uses before copying values across.
  - Use when / pitfalls: a Blender rotation value pasted into an engine can give a different pose if the order differs. Blender sets the mode per object, default XYZ.
- **What the four numbers are**
  1. A quaternion is x, y, z, w.
  2. The xyz part is not an axis. All four values count the same.
  3. A negated component gives the opposite orientation for that part, in the video's picture.
  4. Normalize it so its length is 1. This is a unit quaternion. Engines usually do it for you.
  - Use when / pitfalls: build one from a non unit basis and Godot raises a "not normalized" error. Normalize the basis or the quaternion first.
- **Slerp, look rotation, from-to rotation**
  1. Slerp(a, b, t) mixes two orientations. t = 0 gives a, t = 1 gives b, 0.5 is halfway.
  2. Call it every frame with a small t for smooth turning.
  3. Look rotation makes a quaternion whose forward matches a vector. In Godot use LookingAt.
  4. From-to rotation turns one vector into another. Example: raycast down and align the object's up with the hit normal.
  - Use when / pitfalls: Slerp t is not a speed, so scale it by delta time. In Godot the from-to idea is `new Quaternion(from, to)`. Check the constructor in the editor.
- **Multiply quaternions and vectors**
  1. Quaternion times quaternion adds the rotations.
  2. Quaternion times vector rotates the vector.
  3. Chained products work as expected.
  4. The inverse gives the opposite rotation.
  - Use when / pitfalls: order matters. The same two rotations in a different order give a different result.
