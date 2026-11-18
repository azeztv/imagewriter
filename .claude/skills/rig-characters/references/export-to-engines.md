# Export to engines

Send a rig out of Blender to Unity, Godot, three.js, Crucible or any glTF viewer. The Unity Mecanim steps come from the tutorial notes.
The glTF, Godot and three.js parts are general method, not tested against a tutorial. Test them with one clip.

## Reading Map

- Before any export
- Unity Mecanim humanoid from Rigify
- FBX export preset for Unity
- Configure the Humanoid avatar
- Test the avatar
- Godot
- glTF, three.js and Crucible
- Gaps in the notes

## Before any export

- Export deform bones only when the engine does not need controls. Controls and IK bones are not skin joints.
- Bake the animation to the deform bones (F3 Bake Action, Visual Keying, Clear Constraints) when the engine has no IK or
  constraints. Engines play baked keys only.
- Apply scale and rotation (Ctrl+A) on mesh and armature. Rest pose is the T-pose or A-pose with all transforms cleared.
- Keep one root bone. Keep bone names without spaces and with plain ASCII.
- Make a test clip first: a walk, or a run from a stock library.

## Unity Mecanim humanoid from Rigify

Unity Mecanim does not accept the Rigify hierarchy as generated, because the DEF bones are not in a clean humanoid chain.
The fix is to parent the DEF bones to the ORG bones.

1. Pose or Edit Mode: select the DEF bone, then shift-select the matching ORG bone. The ORG bone must be active (lighter highlight).
2. Ctrl+P > Keep Offset.
3. Do DEF-chest to ORG-chest, DEF-neck to ORG-neck, DEF-head to ORG-head, the upper arms, forearms and thighs the same way.
4. Fingers: select the small inner DEF bones, then the large ORG bone last, and parent with Keep Offset. Repeat for the thumb.
5. Repeat for the other side. Symmetry is not applied.
6. Test every controller in Pose Mode, especially the fingers, because missed parenting shows up there first.
Unconnected parenting leaves some bones that do not deform.

## FBX export preset for Unity

1. Select the armature, then shift-select the character mesh. File > Export > FBX (.fbx).
2. Tick Selected Objects. Set Object Types to Armature and Mesh only.
3. Set Forward to Z Forward (Blender 5.x: under Transform). Set Scale by trial (the demo used 1.6).
4. Untick Bake Animation if the clips come from Unity assets.
5. Save the settings as a preset (the preset menu by the dialog title, "Unity Character").
If a preset does not take a new scale, delete it and create it again. Presets store the scale used when saved.

## Configure the Humanoid avatar

1. Drag the FBX into Assets. Model tab: set Scale Factor (0.2 in the demo, never 0).
2. Rig tab: Animation Type = Humanoid. Click Configure and save the scene.
3. In the Avatar mapping window (Body, Head, Left Hand, Right Hand), replace every DEF-named bone with its ORG-named bone.
   Example: DEF-toe.L becomes ORG-toe.L, DEF-head becomes ORG-head, and fingers map ORG-thumb.01.L to ORG-pinky.03.R.
4. Remove extra bones from the map (eyes, jaw). Check left and right are not swapped.
5. The status symbols turn green when the map is valid. Click Apply, then Done.
If the avatar shows errors, set Animation Type to Generic, press Clear, re-import, then set Humanoid again.
A broken hand is usually the source animation, not the mapping.

## Test the avatar

1. Assets > Create > Animator Controller. Assign it to the Animator component. Open the Animator window.
2. Import a stock humanoid clip (the demo used Standard Assets > Characters > ThirdPersonCharacter animations, HumanoidRun only).
3. Drag the clip into the Animator graph as the default state. Tick Loop Time on the clip.
4. Untick Apply Root Motion to hold the character in place. Tick it to see the character travel.
5. Press Play. Stock clips are mocap on a humanoid skeleton, so they confirm that the mapping is right.
The same Humanoid retargeting shares clips between characters.

## Godot

- Export glTF 2.0 (`.glb`) from Blender: File > Export > glTF 2.0. Tick Selected Objects, Include Armature, and Animation if needed.
- Godot imports the armature as a Skeleton3D under the scene. Use the Import dock > Advanced to split animations into
  an AnimationPlayer library.
- For humanoid retargeting use the Import dock's Skeleton retarget settings with a BoneMap (Godot 4.x). Map ORG or DEF bones to the
  Godot humanoid profile, the same idea as the Unity avatar.
- Use Rigify DEF bones for the skin, as for Unity. Controls and IK bones can stay out of the export.
- A 2D rig is a Skeleton2D (see `mechanical-and-cutout.md`).

## glTF, three.js and Crucible

- glTF stores a skin as joints and inverse bind matrices. Each vertex has up to 4 joints and weights. Keep influences at 4 or fewer
  per vertex in Blender (Weights > Limit Total, 4) or the exporter cuts them and the mesh shifts.
- Shape keys export as morph targets. Names are kept. Drive them with `morphTargetInfluences`. Set the same names in both tools.
- Export the deform bones with the skinned mesh. In Blender glTF export: Armature > Export Deformation Bones Only.
- three.js: load with `GLTFLoader`. The scene holds a `SkinnedMesh` and a `Skeleton`. Play clips with `AnimationMixer`.
  Rigid parts parented to a bone become child nodes of that bone, and they follow it.
- A mechanical rig without bones exports as nodes. The origins and the hierarchy carry over. Apply no scale on children.
- Check scale, axis (Blender Z up, glTF Y up, the exporter converts) and the rest pose in the viewer before you animate.
- Retarget a stock clip with a bone name map. Rigify DEF names are not the Mixamo names, so map or rename them.

## Gaps in the notes

No note covers Godot, glTF or three.js export. The steps above are general method. Verify them against the current engine docs
before a production run.
