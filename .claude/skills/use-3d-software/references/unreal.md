# Unreal Engine

Getting a Blender asset or scene into Unreal Engine 5 and making it playable: editor basics, assets, Blueprints, input, character, animation blueprint, UI, interaction, materials. The Blender import, Nanite, lighting and cinematic parts are not in the video and are marked "not from the video".

Version names
- The video uses a UE 5.x third person template. It does not name the exact 5.x version, so menu names below are the video's. Check them in your editor.
- Mannequins in the UE5 templates are Manny (SKM_Manny) and Quinn (SKM_Quinn). UE4 projects use the old single mannequin.
- The template's "Camera Boom" is a Spring Arm component. The video says so at 1:45:57.
- Input in the shown template uses Enhanced Input (Input Mapping Context plus Input Action assets). UE4 style Action and Axis Mappings are the older system.
- Ctrl+Space opens the content drawer, as the video says it started in 5.0.
- Live Coding, Interchange import and the Packaging menu paths changed across 5.x. Nothing in the video settles them, so check in the editor.
- The video's speech-to-text calls the project "social mix". Names such as "peakable" are the speaker's own class names (Pickable).

<!-- skill-navigation:start -->
## Reading Map

- [Unreal Engine](#unreal-engine)
- [Setup and editor basics](#setup-and-editor-basics)
- [Assets and Blueprints](#assets-and-blueprints)
- [Gameplay framework and character](#gameplay-framework-and-character)
- [Input](#input)
- [Animation blueprint](#animation-blueprint)
- [UI and interaction](#ui-and-interaction)
- [Materials and events](#materials-and-events)
- [Coming from Unity or Godot](#coming-from-unity-or-godot)
- [From Blender to Unreal](#from-blender-to-unreal)
- [Cinematics for video](#cinematics-for-video)
<!-- skill-navigation:end -->

## Setup and editor basics

- **New project from a template**: Start with the Third Person template and the C++ option if you will code, Blueprint only if you will not. Under Target Platform and Quality Preset choose Scalable so the machine is not burdened while learning. Name the project and create. The first open compiles shaders and is slow.
  1. Launch the engine and open Games.
  2. Pick Third Person, then the C++ project type.
  3. Set Quality Preset to Scalable.
  4. Name it and press Create.
  - Use when / pitfalls: put the project and the engine on an SSD, ideally NVMe, since compile time is the slow part. A Blueprint-only project needs no Visual Studio.
- **Code editor**: C++ projects open a Visual Studio solution with the game module and the engine source. Use Visual Studio 2022 or newer, or Rider, ideally with an Unreal-aware extension.
  - Use when / pitfalls: the engine source is open, so Ctrl+Click on any engine class shows its code and comments. This is the fastest way to learn what a node or property does.
- **Content Browser and engine content**: Ctrl+Space opens a quick content drawer that you can dock in the layout. Engine classes and assets stay hidden until you show them.
  1. Press Ctrl+Space, then dock the drawer if you want it permanent.
  2. Open the Settings dropdown of the Content Browser.
  3. Tick Show Engine Content to see engine assets.
  4. Tick Show C++ Classes if you code.
  - Use when / pitfalls: right click a folder and choose Set Color to find folders fast. Right click an asset and choose Show in Explorer to see the same folder tree on disk.
- **Asset editors in the main window**: By default each asset opens in a floating window. You can dock them.
  1. Edit > Editor Preferences.
  2. General > Appearance > Asset Editor Open Location.
  3. Set it to Main Window.
  - Use when / pitfalls: middle click a tab to close it.
- **Viewport navigation**: Right mouse drag orbits and looks, and while holding it WASD flies, E goes up and Q goes down. Scroll while flying changes speed, or use the camera speed control at the top right.
  1. Hold right mouse and use WASD, E and Q to move.
  2. Press F to focus the selected object.
  3. Alt + left mouse orbits around the focused object, right mouse alone orbits around yourself.
  4. Middle mouse pans.
  - Use when / pitfalls: for a non-QWERTY keyboard, open Editor Preferences, search "viewport navigation" and rebind forward, back, left, right, up and down. The video also inverts middle mouse pan in preferences so it feels like Blender.
- **Gizmos, snapping and placing**: W moves, E rotates, R scales, Q returns to selection. Space cycles gizmos.
  1. Select an object and press W, E or R.
  2. Use the World / Local button, or bind a key to Cycle Transform Coordinate System in Keyboard Shortcuts.
  3. Toggle the grid, rotation and scale snap buttons at the top right of the viewport.
  4. Press End to drop the object onto the nearest surface.
  5. Hold Alt and drag an arrow to duplicate, or use Ctrl+D.
  - Use when / pitfalls: holding Shift while moving an object brings the camera along. In the Details panel the Transform section has reset arrows for each value. The video also binds Screen Rotation in preferences for quick rotations.
- **Viewport views and Outliner**: Ctrl + middle mouse click gives a gesture menu to jump to top, front and other views. The viewport view menu has Lit, Unlit and Wireframe. The Outliner lists every object in the open level.
  - Use when / pitfalls: reopen a closed panel from the Window menu. In the Details panel the magnifier next to a mesh reference selects that asset in the Content Browser.

## Assets and Blueprints

- **Asset types and prefixes**: Each asset type has an icon colour and a name prefix. Skeletal meshes (pink, `SKM_`) are deformed by a skeleton (`SK_`), which is only a bone hierarchy. Static meshes (`SM_`) have no bones. Materials are `M_`, material instances `MI_`, textures `T_`. Animation assets and animation blueprints (`ABP_`) reference a skeleton.
  - Use when / pitfalls: one skeleton can be shared by many meshes and animations, which is why animations transfer between meshes that use the same skeleton. Blueprints use `BP_`, widget blueprints `WBP_` (suggested at 3:14:37).
- **Static mesh editor and collision**: Double click a static mesh to open it. You can show simple collision in green, add sphere, box or capsule shapes, and swap materials.
  1. Open the static mesh.
  2. Choose Show > Simple Collision.
  3. Use the Collision menu to add a shape.
  4. Ctrl+Z undoes it like anywhere else.
  - Use when / pitfalls: for imported Blender meshes see the `UCX_` section below.
- **Skeleton, mesh and animation links**: Open a skeletal mesh to see its skeleton asset in the Details panel. In the Skeleton Tree choose Character Bones > Whole Hierarchy to show every bone. Rotating a bone shows the deformation.
  - Use when / pitfalls: a skeletal mesh must reference a skeleton, and animation assets are tied to that skeleton.
- **Files and source control**: Assets are `.uasset` files on disk, readable only by the editor. Use Git or Perforce, connected inside the editor. Perforce is the usual choice on large projects because it handles binary assets better.
  - Use when / pitfalls: move and rename assets inside the editor so references update. Git needs LFS for large binaries.
- **Create a Blueprint class**: A Blueprint is a class made with visual scripting. Create one by right click in the Content Browser > Blueprint Class, then pick a parent such as Actor. Actor is anything placed in the world, like a GameObject.
  1. Content Browser > right click > Blueprint Class.
  2. Choose Actor, name it `BP_Test`.
  3. Open it and look at the Viewport, Construction Script and Event Graph tabs.
  4. Drag the Blueprint into the level.
  - Use when / pitfalls: an actor that is not in the level never runs. Big projects keep Blueprints thin, as shells with exposed settings, and put heavy logic in C++.
- **Event Graph, Begin Play and Print String**: Events are the red nodes. Begin Play runs once when the actor starts, like Start in Unity.
  1. In the Event Graph drag from the Begin Play exec pin and type Print String.
  2. Type text and set Duration, then click Compile.
  3. Press Play. The text shows at the top left.
  4. Add a Delay node and a second Print String to see the order.
  - Use when / pitfalls: Alt+click a node's pin to break its connections. Shift+F1 releases the mouse during play. Compile after every change.
- **Variables, Format Text and functions**: Add a variable in the My Blueprint panel, pick its type, and drag it into the graph as Get or Set.
  1. Click + on Variables, name it `DoorOpen`, type Boolean.
  2. Add a Format Text node and write `Door open is {DoorOpen}`. A pin appears for each name in braces.
  3. Plug the variable in and send the text to Print String. Convert Text to String if needed.
  4. Select repeated nodes, right click, Collapse to Function.
  - Use when / pitfalls: Text is the localisable type, String is plain. Functions can take several inputs and return several outputs. Double click a function to open its definition.
- **Tick and rotate a component**: Event Tick runs every frame.
  1. Add a Static Mesh component (a cube) in the Components panel.
  2. In Event Tick add a Float variable `Angle`. Set Angle = Angle + Delta Seconds times a speed.
  3. Drag the mesh into the graph and call Set World Rotation.
  4. Right click the Rotator pin, Split Struct Pin, and feed Angle into Z (Yaw).
 - Use when / pitfalls: the video first used Delta Seconds alone and the cube barely turned, then multiplied it by 20. Actors tick by default. Untick Start with Tick Enabled in the Details panel to save cost, and call Set Actor Tick Enabled later if needed.
- **Components and per-instance override**: An actor is built from components, so you add a mesh, a light, a collision box or a custom component to the Blueprint. Change one Blueprint and every placed copy updates, but you can override a value on a single placed copy.
  1. In the Blueprint add a Point Light, set colour and radius, compile.
  2. Place several copies in the level.
  3. Select one copy, pick the component in its Details panel and change a value. The reset arrow reverts it.
  - Use when / pitfalls: select an actor in the level and press Ctrl+E to open its Blueprint.
- **Construction Script**: It runs in the editor when you place or edit the actor and again at game start. Use it for tools that must show the result before Play, such as setting a material.
  - Use when / pitfalls: the video promotes a Create Dynamic Material Instance result to a variable and wraps it in a Validated Get so it is made once.

## Gameplay framework and character

- **Game Mode, Pawn and Controller**: The Game Mode sets the rules and which classes spawn. It names a Default Pawn Class, a Player Controller class, a HUD class and others. A Pawn is an actor that can be possessed, like a body with no brain. A Controller is the invisible brain that possesses it. A Player Start actor is where the player spawns.
  1. Open World Settings and find GameMode Override.
  2. Pick a Game Mode and set Default Pawn Class in its class defaults.
  3. Place a Player Start where the player appears.
  4. Right click the floor and choose Play From Here to override it for a test.
  - Use when / pitfalls: with no pawn set, the engine spawns a floating sphere. Press F8 while playing to eject from the pawn and fly around. The older Game State and Spectator classes are mostly legacy from shooter games.
- **Blueprint on top of a code class**: To tune a C++ class, create a Blueprint that derives from it. Right click in the Content Browser > Blueprint Class > All Classes > pick your class, name it `BP_...`, then assign it in World Settings. You get the code plus a designer-friendly asset.
  - Use when / pitfalls: do not hard-code asset paths in a C++ Constructor. The video removes the template's path to the character Blueprint and sets the class in the editor instead.
- **Character anatomy**: A Character is a Pawn with a Capsule (root and collision), an Arrow for facing, a Skeletal Mesh, and a Character Movement component. The template adds a Spring Arm with a Camera at its end. The Spring Arm shortens when it hits a wall, so the camera never goes through geometry.
 - Use when / pitfalls: parts inherited from C++ cannot be removed in the Blueprint. If you need fewer parts, start from Pawn. Scene components have a transform and can be seen. Actor components hold logic only.
- **Camera follow settings**: The Spring Arm uses the pawn's control rotation so the camera turns with the mouse. The camera attaches to the arm's socket at its end and does not rotate by itself.
  1. Select the Spring Arm in the character Blueprint.
  2. Change Target Arm Length and Socket Offset to reframe.
  3. Move the camera a little to one side for an over-the-shoulder view.
  4. Enable Camera Lag only with small values, since large values feel sick.
  - Use when / pitfalls: Target Arm Length 400 is the template default. Lag speed 5 made the video's camera feel heavy.
- **Move and look from input**: Look: the pawn feeds mouse X into the controller's yaw, mouse Y into pitch. Move: the pawn builds forward and right vectors from the controller's yaw only, then calls Add Movement Input. Pitch is dropped so looking down does not push the character into the ground.
 - Use when / pitfalls: in Blueprint the same nodes are Add Controller Yaw Input, Add Controller Pitch Input and Add Movement Input. Unreal axes are X forward, Y right, Z up.
- **Tune the Character Movement component**: Many gameplay values are plain properties.
  1. Select Character Movement in the character Blueprint.
  2. Change Gravity Scale (0.5 gives a moon jump).
  3. Change Air Control (0 means no steering in the air, 1 or more means full control).
  4. Change Jump Z Velocity (doubling it doubles jump height roughly).
 - Use when / pitfalls: use the engine's classes and look at their settings first. Jump is already built in. Bind the input to the Character's Jump and Stop Jumping functions.
- **Expose C++ to Blueprints**: `UPROPERTY` and `UFUNCTION` macros decide what the editor and Blueprints see.
  1. Mark a property `UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Grabber")`.
  2. For a private member add `meta = (AllowPrivateAccess = "true")`.
  3. Mark a function `UFUNCTION()` if it must bind to a delegate.
  4. Create sub objects with `CreateDefaultSubobject` in the Constructor, not `new`.
 - Use when / pitfalls: a property marked as an object pointer is garbage collected for you. Header changes need a rebuild (Ctrl+B in Visual Studio with the editor closed or Live Coding off). The video turns Live Coding off.
- **Debug output**: Print String (Blueprint) shows on screen. In C++ `UE_LOG(LogTemp, Warning, TEXT("..."))` writes to the Output Log, and `GEngine->AddOnScreenDebugMessage` shows on screen.
  - Use when / pitfalls: dereference an `FString` with `*` when passing it to `UE_LOG` or `AddOnScreenDebugMessage`. Check that `GEngine` is not null.
- **When the editor misbehaves**: After a header or component change the editor can show stale properties or crash.
  1. Close the editor and Visual Studio.
  2. Delete the project's Intermediate, DerivedDataCache, Saved and Binaries folders and the solution file.
  3. Right click the `.uproject` file > Generate Visual Studio project files.
  4. Rebuild and start the editor again.
  - Use when / pitfalls: in the video a rename of the property fixed a stubborn case, so try renaming it with the IDE's rename tool first. Restarting the editor from Visual Studio (Ctrl+F5) fixes many odd states.

## Input

- **Enhanced Input assets**: Input Action assets (jump, look, move) carry a value type, such as Axis2D for move. An Input Mapping Context (IMC) maps keys to actions, with modifiers. The pawn adds the context at Begin Play through the Enhanced Input Local Player subsystem.
  1. Open the template's Input folder and the IMC asset.
  2. Under each action see the keys, for example Space for jump, WASD for move, mouse XY for look.
  3. Create a new Input Action, add it to the IMC with a key, then bind it in the character.
  - Use when / pitfalls: a Blueprint-only version uses the Enhanced Input Action event nodes and an Add Mapping Context node on Begin Play. Without the mapping context nothing responds.
- **Rebind keys and modifiers**: To make WASD work on another layout, change the keys in the IMC. Modifiers shape the value. Negate flips a key for the opposite direction. Swizzle Input Axis Values swaps axes so a key drives X or Y of the 2D action.
 - Use when / pitfalls: forward needs a swizzle that puts the key on Y, and backward adds Negate. The video had to switch the swizzle order from YXZ back to the default to make it work.

## Animation blueprint

- **Parts of an animation blueprint**: An ABP has an Event Graph that gathers data each frame and an Anim Graph that outputs the final pose. Assign it in the character's Mesh component under Animation Mode: Use Animation Blueprint. A single animation asset can be assigned instead.
  - Use when / pitfalls: the mesh and the ABP must share the same skeleton. Mixing a female mesh with a male ABP in the video worked because both used the mannequin skeleton.
- **State machine**: A state machine holds states, each playing an animation or a blend space, joined by transitions with a condition and a blend duration. The template has Idle, Locomotion, Jump, Fall and Land states.
  1. In the Anim Graph add a State Machine node and open it.
  2. Right click > Add State, then double click it to put an animation inside and connect it to Output Pose.
  3. Drag from one state's edge to another to make a transition.
  4. Double click the transition and set a Boolean condition such as `ShouldMove`.
  5. Set the blend duration in the transition's Details.
 - Use when / pitfalls: tick Automatic Rule Based on Sequence Player when a state should leave as soon as its animation ends (jump start to fall).
- **Ground speed and blend space**: A blend space places animations along an axis, here Speed from 0 to 500, and blends between them.
  1. In the ABP Event Graph get the pawn's movement component velocity.
  2. Take Vector Length XY (ignore Z) and Set `GroundSpeed`.
  3. In the state, drop the blend space and plug `GroundSpeed` into its Speed input.
  4. Set `ShouldMove` true when ground speed is above about 3 and acceleration is not zero.
 - Use when / pitfalls: hold Ctrl in the blend space preview to scrub. The same ground speed can drive transitions.
- **Cached pose and foot placement**: Save a result with New Save Cached Pose (the video names it `Locomotion`) and reuse it elsewhere in the graph with Use Cached Pose. The template also runs a Control Rig at the end to plant the feet on the ground.
 - Use when / pitfalls: the cached pose name must match or the graph reports an error. Eject with F8 and look at the character's feet near a slope to see the IK work.

## UI and interaction

- **Crosshair with a widget**: A User Widget Blueprint holds the HUD.
  1. Content Browser > right click > User Interface > Widget Blueprint, User Widget, name it `WBP_HUD`.
  2. Add a Canvas Panel as the root, then an Image.
  3. Set the Image's anchor to the center preset, Position 0,0, Size 50 by 5, Alignment 0.5,0.5.
  4. Duplicate it and make it 5 by 15 for a plus sign.
 - Use when / pitfalls: anchors keep the layout when the screen size changes. UE5 does not add the Canvas Panel for you.
- **Show the widget**: Call Create Widget with the class, set the owning player to Get Player Controller (index 0), then Add to Viewport.
  - Use when / pitfalls: the player controller is the usual owner because UI is local to a player. The video does it in the Game Mode only for brevity. Offset the Spring Arm and camera so the crosshair lines up with the aim point.
- **Line trace from the camera**: A line trace is an invisible ray that returns what it hits.
  1. Get the camera location and rotation (Player Camera Manager > Get Camera View Point in C++, or Get Player Camera Manager in Blueprint).
  2. End = location + forward vector times distance (Get Forward Vector of the rotation).
  3. Call Line Trace By Channel with start, end and a trace channel.
  4. Read the hit result: actor, component, location and distance.
  - Use when / pitfalls: fill the camera data before using it, or the ray points the wrong way, as the video's first try did. Use Draw Debug Line while testing.
- **Custom trace channel**: Make a channel so only pickable objects are hit.
  1. Edit > Project Settings > Collision > Trace Channels > New Trace Channel.
  2. Name it `Pickable`, default response Ignore.
  3. On the pickable mesh set Collision Presets to Custom and set Pickable to Block. Enable Simulate Physics and gravity on it.
  4. Trace with that channel.
 - Use when / pitfalls: in C++ it appears as `ECC_GameTraceChannel1`, so define a readable alias. It is saved in the project's config files.
- **Grab and carry with a Physics Handle**: Add a Physics Handle component to the character. On click, trace, then call Grab Component at Location with the hit component. Every tick set the handle's target location.
  1. Store the hit distance when the grab starts.
  2. Each tick compute camera location + camera forward times that stored distance.
  3. Set Target Location to it, and call Release Component when the button is released.
  4. Use Grab Component at Location with Rotation and pass the actor's own rotation if you do not want it to swing.
 - Use when / pitfalls: guard against repeated Start events while the key is held with a boolean. Expose Max Grab Distance as an editable property. With rotation locked, boxes stack well.
- **Interface between systems**: An interface lists functions that many classes can implement, so the grabber does not need to know a box's type.
  1. Add Blueprint Interface or a C++ Unreal Interface class (it creates a `U` class you do not edit and an `I` class you do).
  2. Declare `StartGrab` and `StopGrab` as Blueprint Native Events.
  3. Have the pickable actor implement the interface.
  4. In the grabber, check the hit actor implements it, then call `Execute_StartGrab` or the Blueprint message node.
 - Use when / pitfalls: a native event's C++ body is named `..._Implementation`. In a Blueprint override, right click the event and Add Call to Parent Function or the C++ part never runs.

## Materials and events

- **Glow material with a parameter**: Build one material, expose a number, then drive it from Blueprint.
  1. Create `M_Pickable`. Add a Constant3Vector, pick a base colour.
  2. For Emissive Color add two Constant3Vectors, black and a bright colour. Values above 1 are allowed and glow harder.
  3. Add a Lerp (press L and click). A = black, B = bright colour, plug it into Emissive Color.
  4. Drive Alpha from a Scalar Parameter named `GlowPercent`, default 0.
  - Use when / pitfalls: Lerp at 0 gives A and at 1 gives B.
- **Change the parameter at run time**: Make a Dynamic Material Instance and set a scalar on it.
  1. In the Construction Script call Create Dynamic Material Instance on the mesh with `M_Pickable`.
  2. Promote the return value to a variable.
  3. On Start Grab call Set Scalar Parameter Value `GlowPercent` = 1, on Stop Grab set it to 0.
  - Use when / pitfalls: parameter names are exact. Use a Validated Get so you do not make a new instance each time.
- **Overlap events on a trigger box**: A Box Collision component reports begin and end overlap.
  1. Add a Box Collision in the Blueprint and set its extent to cover the area.
  2. Set its collision preset to Overlap All Dynamic if nothing triggers.
  3. Use the On Component Begin Overlap and End Overlap events, and check the other actor implements the interface so the player does not count.
  4. Keep a count: add on begin, subtract on end, update a Text Render.
 - Use when / pitfalls: in C++ bind with `AddDynamic` and mark the handler `UFUNCTION`. Copy the delegate's parameters, and drop the commas the macro puts between type and name.
- **Custom event dispatchers (delegates)**: An event dispatcher announces something to anyone listening, such as "bucket full".
  1. In the bucket Blueprint add an Event Dispatcher with a String parameter, or in C++ a Dynamic Multicast Delegate.
  2. When count reaches the maximum, Call the dispatcher with a message.
  3. In another actor, Bind Event to it.
  4. Mark the dispatcher Blueprint Assignable in C++.
 - Use when / pitfalls: the video first binds in the Level Blueprint and calls it bad practice. It then binds in the Game Mode, which collects all buckets with Get All Actors Of Class at Begin Play.

## Coming from Unity or Godot

- **Name map and axes**: Actor is the GameObject, Begin Play is Start, Tick is Update, and components compose the object. Unreal is Z up, X forward, Y right, and the unit is centimetres (a 100 cm lift is "100"). Unity's forward is Z.
 - Use when / pitfalls: rotators order is Pitch (Y), Yaw (Z), Roll (X), so the constructor looks like `(Y, Z, X)`.
- **Units and axes in code**: A 100 unit lift moves an actor one metre up.
  - Use when / pitfalls: forward vector of a rotation is its X axis.

## From Blender to Unreal

Not from the video. Each point below is common UE5 practice. Test with one object first and compare it to the mannequin, which is about 180 cm tall.

- **Scale**: Unreal uses 1 unit = 1 cm, Blender uses 1 unit = 1 m by default.
  1. Make a 1 m cube in Blender and export it with your settings.
  2. Import it and check it is 100 cm wide.
  3. If not, set Blender Scene > Units > Unit Scale to 0.01 with Length in centimetres, and in the FBX exporter set Apply Scalings to FBX Units Scale.
  4. Apply scale and rotation (Ctrl+A) on meshes first. Armatures should have scale 1.
  - Use when / pitfalls: pick one setup and keep it for the whole project, so assets from different files match.
- **Axes**: Blender is Z up, Unreal is Z up, but Blender's front axis is -Y and Unreal's forward is +X. Export with FBX defaults, import, and look at the object in the viewport. If a character faces the wrong way, fix the Forward and Up options in the exporter, not by rotating the object.
- **FBX versus glTF**: FBX is the reliable path for static meshes, skeletal meshes and animations. glTF or GLB carries PBR materials and works well for props and scans. Use the glTF Importer or Interchange plugin and check it is enabled under Edit > Plugins for your version. Rigged and animated glTF is less dependable, so use FBX for characters.
- **FBX export settings**: In the Blender exporter turn on Selected Objects, tick Mesh and Armature, and for a rig set Add Leaf Bones off and Armature FBXNode Type to Null. Apply Modifiers on. Check Smoothing: if Unreal warns about missing smoothing groups, export with Smoothing set to Face (or Edge) instead of Normals Only.
- **Armature and root bone**: Unreal prefers a bone at the top of the skeleton named `root` at the origin, with pelvis as its child. Keep the Blender Armature object at scale 1 and unrotated, so no extra node gets in the hierarchy. Name bones plainly. One skeleton can serve many meshes, so import the first mesh with Create New Skeleton and import later meshes and animations with that skeleton selected.
- **Animations**: Import an animation FBX with the same skeleton selected. Bake each Blender action you need and export one FBX per animation, or use NLA tracks and export all actions. Check the clip length after import. For other characters, use the IK Retargeter to copy animation between skeletons.
- **Nanite on import**: In the static mesh import options tick Build Nanite, or open the mesh and tick Enable Nanite Support in Nanite Settings, then Apply Changes. Use it on dense opaque and masked meshes. It is not for translucent materials. For skinned meshes check your version's notes.
- **Collision**: Name extra meshes in the same FBX `UCX_<MeshName>_01` for convex shapes, `UBX_` for boxes, `USP_` for spheres and `UCP_` for capsules. Unreal uses them as simple collision. Keep each hull convex.
- **Lightmap UVs**: Static baked lighting needs a second UV set (UV1) with no overlap. You can make it in Blender, or tick Generate Lightmap UVs on import. Lumen does not need lightmap UVs. Set the correct Lightmap Coordinate Index in the mesh editor if you have baked lighting.
- **Textures and materials**: Blender normal maps are OpenGL, Unreal expects DirectX, so turn on Flip Green Channel on the texture. Turn sRGB off for normal and data maps. Imported materials are basic. Build one master material with parameters and make instances, as in the glow entry above.

## Cinematics for video

Not from the video. The video covers no Sequencer, rendering or lighting, so this is the short version.
- Lighting: new levels use Lumen by default. A basic outdoor scene needs a Directional Light, Sky Atmosphere, Sky Light, Exponential Height Fog and optionally Volumetric Clouds.
- Sequencer: Cinematics > Add Level Sequence, add a Cine Camera Actor, key its transform and focus, and add a Camera Cut track.
- Output: enable the Movie Render Queue plugin, open Window > Cinematics > Movie Render Queue, add the sequence and choose an image sequence or video output. Turn on anti-aliasing passes for clean frames.
- Packaging a playable build: Platforms > Windows > Package Project, check the exact menu for your version.
