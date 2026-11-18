"""Bake an AI high-poly (Tripo Studio H3.1 or any scan) onto a low poly, headless.

high GLB -> low poly (--low GLB from Tripo Smart Mesh, or a Decimate stand-in) -> UV (kept, or Smart UV) ->
bake normal + base colour with a ray distance sized from the measured low-to-high gap ->
detail normal derived from the base colour, blended with the baked normal (RNM) in the node group
"Normal tuning RNM" with Baked Strength and Detail Strength sliders -> roughness derived from the base colour ->
renders of high, low colour-only, low + baked normal, low full flow from one camera, plus a .blend.

Run: blender -b --python bake_ai_mesh.py -- --glb high.glb --out folder [--low low.glb] [--faces 3000]
     [--res 2048] [--rough-min 0.15] [--rough-max 0.9]
Measured 2026-11-11 on a 14.5k-face Tripo postbox, 3k low: error vs the high render 0.049 colour only, 0.034 with
the baked normal, 0.037 with detail + roughness (adds texture the high lacks; grey concrete read wet, so set the
roughness range per material).
"""
import sys
import os
import argparse
import math
import bpy
import bmesh
import numpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


def parse_arguments():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--glb", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--faces", type=int, default=3000)
    parser.add_argument("--res", type=int, default=2048)
    parser.add_argument("--low", help="low-poly GLB (Tripo Smart Mesh export); default: decimate the high")
    parser.add_argument("--rough-min", type=float, default=0.15)
    parser.add_argument("--rough-max", type=float, default=0.9)
    return parser.parse_args(argv)


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def import_joined(glb_path, name):
    before = set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=glb_path)
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH" and obj not in before]
    bpy.ops.object.select_all(action="DESELECT")
    for mesh_object in meshes:
        mesh_object.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    if len(meshes) > 1:
        bpy.ops.object.join()
    joined = bpy.context.view_layer.objects.active
    joined.parent = None
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    joined.name = name
    return joined


def make_low(high, target_faces, low_path=None):
    if low_path:
        low = import_joined(low_path, "low")
        for polygon in low.data.polygons:
            polygon.use_smooth = True
        if low.data.uv_layers:
            return low
        bpy.ops.object.select_all(action="DESELECT")
        low.select_set(True)
        bpy.context.view_layer.objects.active = low
    else:
        low = high.copy()
        low.data = high.data.copy()
        low.name = "low"
        bpy.context.scene.collection.objects.link(low)
        ratio = min(1.0, target_faces / max(1, len(high.data.polygons)))
        decimate = low.modifiers.new("decimate", "DECIMATE")
        decimate.ratio = ratio
        bpy.ops.object.select_all(action="DESELECT")
        low.select_set(True)
        bpy.context.view_layer.objects.active = low
        bpy.ops.object.modifier_apply(modifier="decimate")
        for polygon in low.data.polygons:
            polygon.use_smooth = True
    # fresh UV when the low has none (Tripo Smart UV output keeps its own)
    while low.data.uv_layers:
        low.data.uv_layers.remove(low.data.uv_layers[0])
    low.data.uv_layers.new(name="bake_uv")
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.004)
    bpy.ops.object.mode_set(mode="OBJECT")
    return low


def measure_gap(low, high):
    """Distance from each low vertex to the high surface: sizes the bake rays."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    tree = BVHTree.FromObject(high, depsgraph)
    distances = []
    for vertex in low.data.vertices:
        hit = tree.find_nearest(low.matrix_world @ vertex.co)
        if hit[0] is not None:
            distances.append(hit[3])
    distances = numpy.array(distances)
    size = max(high.dimensions)
    return {
        "mean": float(distances.mean()),
        "p95": float(numpy.percentile(distances, 95)),
        "max": float(distances.max()),
        "object_size": float(size),
    }


def new_image(name, resolution, is_data):
    image = bpy.data.images.new(name, resolution, resolution, alpha=False, float_buffer=is_data)
    if is_data:
        image.colorspace_settings.name = "Non-Color"
    return image


def set_bake_target(low, image):
    material = low.data.materials[0] if low.data.materials else None
    if material is None or material.name.startswith("low_mat") is False:
        material = bpy.data.materials.new("low_mat")
        material.use_nodes = True
        low.data.materials.clear()
        low.data.materials.append(material)
    nodes = material.node_tree.nodes
    for node in nodes:
        node.select = False
    target = nodes.get("bake_target") or nodes.new("ShaderNodeTexImage")
    target.name = "bake_target"
    target.image = image
    target.select = True
    nodes.active = target
    return material


def bake(low, high, bake_type, image, ray_distance):
    scene = bpy.context.scene
    set_bake_target(low, image)
    bpy.ops.object.select_all(action="DESELECT")
    high.select_set(True)
    low.select_set(True)
    bpy.context.view_layer.objects.active = low
    bake_settings = scene.render.bake
    bake_settings.use_selected_to_active = True
    bake_settings.use_cage = False
    bake_settings.max_ray_distance = ray_distance
    bake_settings.cage_extrusion = ray_distance * 0.5
    bake_settings.margin = 8
    bake_settings.margin_type = "EXTEND"
    if bake_type == "NORMAL":
        bake_settings.normal_space = "TANGENT"
        bpy.ops.object.bake(type="NORMAL")
    else:
        bake_settings.use_pass_direct = False
        bake_settings.use_pass_indirect = False
        bake_settings.use_pass_color = True
        bpy.ops.object.bake(type="DIFFUSE")


def image_to_array(image):
    width, height = image.size
    pixels = numpy.empty(width * height * 4, dtype=numpy.float32)
    image.pixels.foreach_get(pixels)
    return pixels.reshape(height, width, 4)


def array_to_image(name, array, is_data):
    height, width = array.shape[:2]
    image = bpy.data.images.new(name, width, height, alpha=False, float_buffer=is_data)
    if is_data:
        image.colorspace_settings.name = "Non-Color"
    rgba = numpy.ones((height, width, 4), dtype=numpy.float32)
    rgba[..., :array.shape[2] if array.ndim == 3 else 1] = array if array.ndim == 3 else array[..., None]
    if array.ndim == 2:
        rgba[..., 1] = array
        rgba[..., 2] = array
    image.pixels.foreach_set(rgba.ravel())
    return image


def box_blur(values, radius):
    kernel = numpy.ones(2 * radius + 1) / (2 * radius + 1)
    blurred = numpy.apply_along_axis(lambda row: numpy.convolve(row, kernel, mode="same"), 1, values)
    return numpy.apply_along_axis(lambda column: numpy.convolve(column, kernel, mode="same"), 0, blurred)


def detail_maps_from_color(base_color, coverage_mask, rough_min=0.15, rough_max=0.9):
    """High-pass luminance -> detail height -> tangent normal; plus roughness variation."""
    luminance = base_color[..., 0] * 0.2126 + base_color[..., 1] * 0.7152 + base_color[..., 2] * 0.0722
    high_pass = luminance - box_blur(luminance, 6)
    height = numpy.clip(high_pass * 4.0, -1.0, 1.0)
    gradient_y, gradient_x = numpy.gradient(height)
    strength = 6.0
    normal = numpy.stack([-gradient_x * strength, -gradient_y * strength, numpy.ones_like(height)], axis=-1)
    normal /= numpy.linalg.norm(normal, axis=-1, keepdims=True)
    normal = normal * 0.5 + 0.5
    normal[~coverage_mask] = (0.5, 0.5, 1.0)
    rng = numpy.random.default_rng(7)
    noise = box_blur(rng.standard_normal(luminance.shape).astype(numpy.float32), 3)
    noise /= max(1e-6, numpy.abs(noise).max())
    # darker, dirtier paint is rougher; clean bright paint is glossier
    roughness = 0.42 - (luminance - luminance[coverage_mask].mean()) * 0.6 + numpy.abs(high_pass) * 1.5 + noise * 0.06
    roughness = numpy.clip(roughness, rough_min, rough_max)
    return normal.astype(numpy.float32), roughness.astype(numpy.float32)


def build_normal_group():
    """Node group: Baked Normal + Detail Normal colours -> RNM blend -> tangent normal colour."""
    group = bpy.data.node_groups.new("Normal tuning RNM", "ShaderNodeTree")
    group.interface.new_socket("Baked Normal", in_out="INPUT", socket_type="NodeSocketColor")
    group.interface.new_socket("Detail Normal", in_out="INPUT", socket_type="NodeSocketColor")
    baked_strength = group.interface.new_socket("Baked Strength", in_out="INPUT", socket_type="NodeSocketFloat")
    baked_strength.default_value = 1.0
    detail_strength = group.interface.new_socket("Detail Strength", in_out="INPUT", socket_type="NodeSocketFloat")
    detail_strength.default_value = 0.6
    group.interface.new_socket("Normal Color", in_out="OUTPUT", socket_type="NodeSocketColor")
    nodes = group.nodes
    links = group.links
    group_input = nodes.new("NodeGroupInput")
    group_output = nodes.new("NodeGroupOutput")
    flat = (0.5, 0.5, 1.0)

    def mix_toward_flat(color_socket, factor_socket):
        mix = nodes.new("ShaderNodeMix")
        mix.data_type = "VECTOR"
        mix.inputs[4].default_value = flat
        links.new(factor_socket, mix.inputs[0])
        links.new(color_socket, mix.inputs[5])
        return mix.outputs[1]

    def vector_math(operation, first, second=None, constant=None):
        node = nodes.new("ShaderNodeVectorMath")
        node.operation = operation
        links.new(first, node.inputs[0])
        if second is not None:
            links.new(second, node.inputs[1])
        if constant is not None:
            node.inputs[1].default_value = constant
        return node

    base = mix_toward_flat(group_input.outputs["Baked Normal"], group_input.outputs["Baked Strength"])
    detail = mix_toward_flat(group_input.outputs["Detail Normal"], group_input.outputs["Detail Strength"])
    # RNM: t = n1*(2,2,2)+(-1,-1,0); u = n2*(-2,-2,2)+(1,1,-1); r = t*dot(t,u) - u*t.z
    t_scaled = vector_math("MULTIPLY", base, constant=(2.0, 2.0, 2.0))
    t_vector = vector_math("ADD", t_scaled.outputs[0], constant=(-1.0, -1.0, 0.0))
    u_scaled = vector_math("MULTIPLY", detail, constant=(-2.0, -2.0, 2.0))
    u_vector = vector_math("ADD", u_scaled.outputs[0], constant=(1.0, 1.0, -1.0))
    dot = vector_math("DOT_PRODUCT", t_vector.outputs[0], u_vector.outputs[0])
    t_times_dot = vector_math("SCALE", t_vector.outputs[0])
    links.new(dot.outputs["Value"], t_times_dot.inputs["Scale"])
    separate = nodes.new("ShaderNodeSeparateXYZ")
    links.new(t_vector.outputs[0], separate.inputs[0])
    u_times_tz = vector_math("SCALE", u_vector.outputs[0])
    links.new(separate.outputs["Z"], u_times_tz.inputs["Scale"])
    blended = vector_math("SUBTRACT", t_times_dot.outputs[0], u_times_tz.outputs[0])
    normalized = vector_math("NORMALIZE", blended.outputs[0])
    to_color_half = vector_math("MULTIPLY", normalized.outputs[0], constant=(0.5, 0.5, 0.5))
    to_color = vector_math("ADD", to_color_half.outputs[0], constant=(0.5, 0.5, 0.5))
    links.new(to_color.outputs[0], group_output.inputs["Normal Color"])
    return group


def wire_material(low, base_image, normal_image, detail_image, roughness_image, full_flow, detail_strength=0.6):
    material = bpy.data.materials.new("low_full" if full_flow else "low_color_only")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    shader = nodes["Principled BSDF"]
    base_node = nodes.new("ShaderNodeTexImage")
    base_node.image = base_image
    links.new(base_node.outputs["Color"], shader.inputs["Base Color"])
    if full_flow:
        baked_node = nodes.new("ShaderNodeTexImage")
        baked_node.image = normal_image
        detail_node = nodes.new("ShaderNodeTexImage")
        detail_node.image = detail_image
        rough_node = nodes.new("ShaderNodeTexImage")
        rough_node.image = roughness_image
        group_node = nodes.new("ShaderNodeGroup")
        group_node.node_tree = bpy.data.node_groups["Normal tuning RNM"]
        links.new(baked_node.outputs["Color"], group_node.inputs["Baked Normal"])
        links.new(detail_node.outputs["Color"], group_node.inputs["Detail Normal"])
        group_node.inputs["Detail Strength"].default_value = detail_strength
        normal_map = nodes.new("ShaderNodeNormalMap")
        links.new(group_node.outputs["Normal Color"], normal_map.inputs["Color"])
        links.new(normal_map.outputs["Normal"], shader.inputs["Normal"])
        links.new(rough_node.outputs["Color"], shader.inputs["Roughness"])
    else:
        shader.inputs["Roughness"].default_value = 0.5
    low.data.materials.clear()
    low.data.materials.append(material)
    return material


def setup_render(target_object, output_folder):
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "GPU"
    scene.cycles.samples = 64
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 900
    scene.render.resolution_y = 900
    world = bpy.data.worlds.new("world")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.25
    scene.world = world
    corners = [target_object.matrix_world @ Vector(corner) for corner in target_object.bound_box]
    center = sum(corners, Vector()) / 8
    size = max(target_object.dimensions)
    # raking key light so surface relief reads
    sun = bpy.data.objects.new("key", bpy.data.lights.new("key", "SUN"))
    sun.data.energy = 4.0
    sun.data.angle = math.radians(3)
    sun.rotation_euler = (math.radians(70), 0, math.radians(-55))
    scene.collection.objects.link(sun)
    camera = bpy.data.objects.new("camera", bpy.data.cameras.new("camera"))
    camera.data.lens = 50
    scene.collection.objects.link(camera)
    scene.camera = camera
    direction = Vector((0.55, -1.0, 0.25)).normalized()
    camera.location = center + direction * size * 2.0
    camera.rotation_euler = (center - camera.location).to_track_quat("-Z", "Y").to_euler()
    return center, size


def render_only(visible_object, all_objects, path):
    for scene_object in all_objects:
        scene_object.hide_render = scene_object is not visible_object
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)


def enable_gpu():
    preferences = bpy.context.preferences.addons["cycles"].preferences
    for device_type in ("OPTIX", "CUDA"):
        try:
            preferences.compute_device_type = device_type
            preferences.get_devices()
            for device in preferences.devices:
                device.use = True
            return device_type
        except TypeError:
            continue
    return "CPU"


def main():
    arguments = parse_arguments()
    os.makedirs(arguments.out, exist_ok=True)
    clear_scene()
    device = enable_gpu()
    high = import_joined(arguments.glb, "high")
    low = make_low(high, arguments.faces, arguments.low)
    gap = measure_gap(low, high)
    ray_distance = max(gap["p95"] * 2.0, gap["object_size"] * 0.005)
    print(f"faces high={len(high.data.polygons)} low={len(low.data.polygons)} gap={gap} ray={ray_distance:.4f} device={device}")
    if gap["mean"] > gap["object_size"] * 0.01:
        print("WARN low and high do not overlap (mean gap over 1% of size): Tripo retopo resets each part's "
              "position and scale, so align the low to the high before baking")
    bpy.context.scene.render.engine = "CYCLES"
    bpy.context.scene.cycles.device = "GPU"
    bpy.context.scene.cycles.samples = 4

    resolution = arguments.res
    normal_image = new_image("baked_normal", resolution, True)
    bake(low, high, "NORMAL", normal_image, ray_distance)
    color_image = new_image("baked_color", resolution, False)
    bake(low, high, "DIFFUSE", color_image, ray_distance)

    color_array = image_to_array(color_image)[..., :3]
    normal_array = image_to_array(normal_image)[..., :3]
    coverage_mask = numpy.abs(normal_array - numpy.array([0.5, 0.5, 1.0])).sum(axis=-1) > 1e-4
    coverage_mask |= color_array.sum(axis=-1) > 1e-4
    detail_normal, roughness = detail_maps_from_color(color_array, coverage_mask, arguments.rough_min, arguments.rough_max)
    detail_image = array_to_image("detail_normal", detail_normal, True)
    roughness_image = array_to_image("roughness", roughness, True)
    steep = numpy.arccos(numpy.clip(normal_array[..., 2] * 2 - 1, -1, 1)) > math.radians(60)
    print(f"coverage={coverage_mask.mean():.3f} steep_normal_pixels={steep[coverage_mask].mean():.4f}")

    for image in (normal_image, color_image, detail_image, roughness_image):
        image.filepath_raw = os.path.join(arguments.out, image.name + ".png")
        image.file_format = "PNG"
        image.save()

    build_normal_group()
    setup_render(high, arguments.out)
    bpy.context.scene.cycles.samples = 64
    render_only(high, [high, low], os.path.join(arguments.out, "render_high.png"))
    wire_material(low, color_image, None, None, None, full_flow=False)
    render_only(low, [high, low], os.path.join(arguments.out, "render_low_color_only.png"))
    wire_material(low, color_image, normal_image, detail_image, roughness_image, full_flow=True)
    render_only(low, [high, low], os.path.join(arguments.out, "render_low_full.png"))
    wire_material(low, color_image, normal_image, detail_image, roughness_image, full_flow=True, detail_strength=0.0)
    render_only(low, [high, low], os.path.join(arguments.out, "render_low_baked_only.png"))
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(arguments.out, "bake_test.blend"))
    print("done")


main()
