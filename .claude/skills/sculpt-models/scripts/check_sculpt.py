"""Check a sculpt in Blender: numbers that catch mushy or broken sculpts, plus silhouette and matcap sheets to look at.

Run (Blender 4.2 or later, headless):
  blender -b [file.blend] --python scripts/check_sculpt.py -- [--import model.glb|.obj|.fbx|.stl] [--object Name]
      [--out folder] [--views 8] [--size 384]

Measures (printed and written to <out>/sculpt_report.json):
- faces and vertices (evaluated, with modifiers), multires levels, whether scale is applied;
- non-manifold edges and loose vertices (holes and stray geometry break bakes, prints and remeshes);
- symmetry: mean and max distance from each vertex's X mirror to the surface, as a share of the object's size.
  Near 0.0% means a perfect mirror: break it on purpose for anything alive (0.3 to 2% is typical of a finished head);
- surface busyness: the share of faces whose normal turns more than 20 degrees from their neighbours' average
  (very high reads as noise or lumps, near zero on an organic sculpt reads as mush).

Writes <out>/silhouette.png (solid black shape from evenly spaced angles around Z, plus top and bottom) and
<out>/matcap.png (front, three-quarter, side, back under a studio matcap and under a flat light from above).
Exit code 0 when the measured checks pass, 1 when one fails, 2 when no mesh is found.
"""

import json
import math
import pathlib
import sys

import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

FAIL_NON_MANIFOLD = 0
FAIL_LOOSE = 0
SHARP_ANGLE_DEGREES = 20.0


def parse_arguments():
    arguments = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    options = {"import": None, "object": None, "out": "sculpt_check", "views": 8, "size": 384}
    index = 0
    while index < len(arguments):
        key = arguments[index].lstrip("-")
        options[key] = arguments[index + 1]
        index += 2
    options["views"] = int(options["views"])
    options["size"] = int(options["size"])
    return options


def import_model(path):
    suffix = pathlib.Path(path).suffix.lower()
    if suffix in (".glb", ".gltf"):
        bpy.ops.import_scene.gltf(filepath=path)
    elif suffix == ".obj":
        bpy.ops.wm.obj_import(filepath=path)
    elif suffix == ".fbx":
        bpy.ops.import_scene.fbx(filepath=path)
    elif suffix == ".stl":
        bpy.ops.wm.stl_import(filepath=path)
    else:
        raise SystemExit(f"cannot import {suffix}")


def pick_object(name):
    if name:
        return bpy.data.objects.get(name)
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH" and obj.visible_get()]
    if not meshes:
        return None
    return max(meshes, key=lambda obj: len(obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.polygons))


def evaluated_bmesh(obj):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    surface = bmesh.new()
    surface.from_mesh(mesh)
    surface.transform(obj.matrix_world)
    evaluated.to_mesh_clear()
    surface.normal_update()
    return surface


def symmetry_error(surface, size):
    tree = BVHTree.FromBMesh(surface)
    vertices = list(surface.verts)[:: max(1, len(surface.verts) // 20000)]
    distances = []
    centre_x = sum(vertex.co.x for vertex in surface.verts) / max(1, len(surface.verts))
    for vertex in vertices:
        mirrored = Vector((2 * centre_x - vertex.co.x, vertex.co.y, vertex.co.z))
        hit = tree.find_nearest(mirrored)
        if hit[0] is not None:
            distances.append(hit[3])
    if not distances:
        return 0.0, 0.0
    return sum(distances) / len(distances) / size, max(distances) / size


def busyness(surface):
    threshold = math.radians(SHARP_ANGLE_DEGREES)
    sharp = 0
    for face in surface.faces:
        neighbours = {other for edge in face.edges for other in edge.link_faces if other is not face}
        if not neighbours:
            continue
        average = Vector()
        for other in neighbours:
            average += other.normal
        if average.length and face.normal.angle(average.normalized(), 0.0) > threshold:
            sharp += 1
    return sharp / max(1, len(surface.faces))


def setup_render(size):
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x = size
    scene.render.resolution_y = size
    scene.render.film_transparent = False
    scene.display.shading.background_type = "VIEWPORT" if hasattr(scene.display.shading, "background_type") else None
    scene.world = scene.world or bpy.data.worlds.new("check_world")
    scene.display.shading.color_type = "SINGLE"
    return scene


def frame_camera(obj, scene):
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    centre = sum(corners, Vector()) / 8
    radius = max((corner - centre).length for corner in corners)
    camera_data = bpy.data.cameras.new("check_camera")
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = radius * 2.3
    camera = bpy.data.objects.new("check_camera", camera_data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    return camera, centre, radius


def aim(camera, centre, radius, azimuth_degrees, elevation_degrees):
    azimuth = math.radians(azimuth_degrees)
    elevation = math.radians(elevation_degrees)
    direction = Vector((math.sin(azimuth) * math.cos(elevation), -math.cos(azimuth) * math.cos(elevation), math.sin(elevation)))
    camera.location = centre + direction * radius * 4
    camera.rotation_euler = (centre - camera.location).to_track_quat("-Z", "Y").to_euler()


def render_views(scene, camera, centre, radius, views, out_folder, prefix):
    paths = []
    for index, (azimuth, elevation) in enumerate(views):
        aim(camera, centre, radius, azimuth, elevation)
        path = out_folder / f"{prefix}_{index:02d}.png"
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        paths.append(path)
    return paths


def tile(paths, target, columns):
    images = [bpy.data.images.load(str(path)) for path in paths]
    width, height = images[0].size
    rows = (len(images) + columns - 1) // columns
    sheet = bpy.data.images.new("sheet", width * columns, height * rows, alpha=False)
    pixels = [0.0] * (width * columns * height * rows * 4)
    for index, image in enumerate(images):
        source = list(image.pixels)
        column = index % columns
        row = rows - 1 - index // columns
        for line in range(height):
            start = ((row * height + line) * width * columns + column * width) * 4
            pixels[start:start + width * 4] = source[line * width * 4:(line + 1) * width * 4]
    sheet.pixels = pixels
    sheet.filepath_raw = str(target)
    sheet.file_format = "PNG"
    sheet.save()
    for path in paths:
        path.unlink(missing_ok=True)


def main():
    options = parse_arguments()
    if options["import"]:
        import_model(options["import"])
    obj = pick_object(options["object"])
    if obj is None:
        print("no mesh object found")
        return 2
    out_folder = pathlib.Path(options["out"]).resolve()
    out_folder.mkdir(parents=True, exist_ok=True)

    surface = evaluated_bmesh(obj)
    dimensions = obj.dimensions
    size = max(dimensions) or 1.0
    non_manifold = sum(1 for edge in surface.edges if not edge.is_manifold and not edge.is_boundary)
    boundary = sum(1 for edge in surface.edges if edge.is_boundary)
    loose = sum(1 for vertex in surface.verts if not vertex.link_edges)
    mean_mirror, max_mirror = symmetry_error(surface, size)
    busy = busyness(surface)
    multires = next((modifier for modifier in obj.modifiers if modifier.type == "MULTIRES"), None)
    scale_applied = all(abs(value - 1.0) < 1e-4 for value in obj.scale)
    report = {
        "object": obj.name,
        "faces": len(surface.faces),
        "vertices": len(surface.verts),
        "dimensions_m": [round(value, 4) for value in dimensions],
        "multires_levels": multires.total_levels if multires else 0,
        "scale_applied": scale_applied,
        "non_manifold_edges": non_manifold,
        "open_boundary_edges": boundary,
        "loose_vertices": loose,
        "mirror_error_mean_pct": round(mean_mirror * 100, 3),
        "mirror_error_max_pct": round(max_mirror * 100, 3),
        "busy_face_share_pct": round(busy * 100, 2),
    }
    surface.free()

    scene = setup_render(options["size"])
    camera, centre, radius = frame_camera(obj, scene)
    others = [item for item in scene.objects if item.type == "MESH" and item is not obj]
    for item in others:
        item.hide_render = True
    shading = scene.display.shading
    step = 360 / options["views"]
    silhouette_views = [(index * step, 0) for index in range(options["views"])] + [(0, 89), (0, -89)]
    shading.light = "FLAT"
    shading.single_color = (0.0, 0.0, 0.0)
    scene.display.shading.background_type = "WORLD" if hasattr(shading, "background_type") else None
    scene.world.color = (1.0, 1.0, 1.0)
    paths = render_views(scene, camera, centre, radius, silhouette_views, out_folder, "silhouette")
    tile(paths, out_folder / "silhouette.png", 5)

    matcap_views = [(0, 5), (35, 10), (90, 5), (180, 5)]
    shading.light = "MATCAP"
    shading.single_color = (0.8, 0.8, 0.8)
    scene.world.color = (0.18, 0.18, 0.18)
    paths = render_views(scene, camera, centre, radius, matcap_views, out_folder, "matcap")
    shading.light = "STUDIO"
    paths += render_views(scene, camera, centre, radius, [(35, 10), (0, 60)], out_folder, "studio")
    tile(paths, out_folder / "matcap.png", 3)

    checks = {
        "scale applied": scale_applied,
        "no non-manifold edges": non_manifold <= FAIL_NON_MANIFOLD,
        "no loose vertices": loose <= FAIL_LOOSE,
    }
    report["checks"] = checks
    (out_folder / "sculpt_report.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    for name, value in report.items():
        if name != "checks":
            print(f"{name}: {value}")
    for name, passed in checks.items():
        print(f"{'PASS' if passed else 'FAIL'}  {name}")
    if report["mirror_error_max_pct"] < 0.05:
        print("NOTE  perfect mirror: break symmetry for anything alive")
    print(f"sheets: {out_folder / 'silhouette.png'}  {out_folder / 'matcap.png'} (look at them)")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    code = main()
    sys.stdout.flush()
    import os
    os._exit(code)
