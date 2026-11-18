"""
Blender helper for 3D Generalist:
1. Configures 1080x1920 vertical Shorts settings at 30 FPS in Eevee with Passepartout = 1.0 and Depth of Field.
2. Creates an Empty Sphere ('Cutaway_Guide') and wires an object-driven transparent cutaway shader onto a target mesh.
3. Adds a spine-tracked Area Fill Light so the character's face and torso never fall into dark shadow inside cutaways.

Run inside Blender or headless:
  blender -b scene.blend -P blender_cutaway_and_rig.py -- --target CabinWall --rig HumanRig
"""

import sys
import bpy


def configure_shorts_render(fps=30, width=1080, height=1920):
    scene = bpy.context.scene
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.fps = fps
    for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            scene.render.engine = eng
            break
        except TypeError:
            continue
    image_settings = scene.render.image_settings
    if hasattr(image_settings, "media_type"):
        # Blender 5.0+: video formats are only offered after the media type is VIDEO.
        image_settings.media_type = "VIDEO"
    image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.codec = "H264"
    if scene.camera and scene.camera.data:
        scene.camera.data.passepartout_alpha = 1.0
        scene.camera.data.dof.use_dof = True


def add_object_cutaway_shader(mesh_obj_name, empty_name="Cutaway_Guide"):
    obj = bpy.data.objects.get(mesh_obj_name)
    if not obj or not obj.data.materials:
        return None
    empty = bpy.data.objects.get(empty_name)
    if not empty:
        bpy.ops.object.empty_add(type="SPHERE", radius=0.5, location=obj.location)
        empty = bpy.context.active_object
        empty.name = empty_name

    mat = obj.data.materials[0]
    if mat.node_tree is None:
        # Before 5.0 a material may have no node tree yet; 5.0+ always has one and deprecates use_nodes.
        mat.use_nodes = True
    if hasattr(mat, "blend_method"):
        mat.blend_method = "HASHED"
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    out_node = next((n for n in nodes if n.type == "OUTPUT_MATERIAL"), None)
    bsdf_node = next((n for n in nodes if n.type == "BSDF_PRINCIPLED"), None)
    if not out_node or not bsdf_node:
        return empty

    tex_coord = nodes.new("ShaderNodeTexCoord")
    tex_coord.object = empty
    sep_xyz = nodes.new("ShaderNodeSeparateXYZ")
    transp = nodes.new("ShaderNodeBsdfTransparent")
    mix_shader = nodes.new("ShaderNodeMixShader")

    links.new(tex_coord.outputs["Object"], sep_xyz.inputs["Vector"])
    links.new(sep_xyz.outputs["Y"], mix_shader.inputs["Fac"])
    links.new(bsdf_node.outputs["BSDF"], mix_shader.inputs[1])
    links.new(transp.outputs["BSDF"], mix_shader.inputs[2])
    links.new(mix_shader.outputs["Shader"], out_node.inputs["Surface"])
    return empty


def add_spine_tracked_fill_light(rig_name, bone_name="spine", energy=150.0):
    rig = bpy.data.objects.get(rig_name)
    if not rig:
        return None
    bpy.ops.object.light_add(type="AREA", location=(rig.location.x + 1.5, rig.location.y - 1.5, rig.location.z + 2.2))
    light_obj = bpy.context.active_object
    light_obj.name = "Worker_Fill_Light"
    light_obj.data.energy = energy
    light_obj.data.size = 1.5

    con = light_obj.constraints.new(type="TRACK_TO")
    con.target = rig
    if rig.type == "ARMATURE" and bone_name in rig.data.bones:
        con.subtarget = bone_name
    con.track_axis = "TRACK_NEGATIVE_Z"
    con.up_axis = "UP_Y"
    return light_obj


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    configure_shorts_render()
    if "--target" in argv:
        idx = argv.index("--target")
        if idx + 1 < len(argv):
            add_object_cutaway_shader(argv[idx + 1])
    if "--rig" in argv:
        idx = argv.index("--rig")
        if idx + 1 < len(argv):
            add_spine_tracked_fill_light(argv[idx + 1])
