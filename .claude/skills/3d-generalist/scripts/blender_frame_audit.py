"""
Frame audit for a dressed Blender set, run before anyone sees a still.

It answers three questions with numbers instead of by eye:
1. What fills the frame? A letter map of what the camera sees in each cell, and the share of the frame each object
   covers, so large plain areas (bare wall, bare counter) show up before the viewer points at them.
2. Does each prop read? Its share inside the frame, whether the frame edge cuts it, and its height on screen.
3. Does anything float? The gap from each object to the nearest other surface. A hung, leaning or resting thing
   touches something; a gap above the limit means it hovers.

Run headless:
  blender -b scene.blend -P blender_frame_audit.py -- [--frame 1] [--columns 18] [--float-mm 4] [--only name,name] [--skip steam,air]

Exit code 1 when an object floats, so a build script can stop on it.
"""

import argparse
import re
import string
import sys

import bpy
import mathutils
from bpy_extras.object_utils import world_to_camera_view
from mathutils.bvhtree import BVHTree

SAMPLE_LIMIT = 600
LETTERS = string.ascii_uppercase + string.ascii_lowercase + string.digits


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--frame", type=int, default=None)
    parser.add_argument("--columns", type=int, default=18)
    parser.add_argument("--float-mm", type=float, default=4.0)
    parser.add_argument("--only", default="", help="comma separated name parts; limits the float check")
    parser.add_argument("--skip", default="", help="comma separated name parts left out of the float check (smoke, air volumes)")
    arguments = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return parser.parse_args(arguments)


def visible_geometry_objects(scene):
    kinds = {"MESH", "CURVE", "SURFACE", "FONT", "META"}
    return [obj for obj in scene.objects
            if obj.type in kinds and not obj.hide_render and obj.visible_get() and obj.visible_camera]


def family_of(name):
    """Numbered copies (bubble_012, slice.003) are reported as one family."""
    return re.sub(r"[._]\d+$", "", name)


def world_mesh_data(obj, depsgraph):
    """World-space vertices and polygons of the object as rendered (modifiers and curve bevels applied)."""
    evaluated = obj.evaluated_get(depsgraph)
    try:
        mesh = evaluated.to_mesh()
    except RuntimeError:
        return [], []
    if mesh is None:
        return [], []
    matrix = evaluated.matrix_world
    vertices = [matrix @ vertex.co for vertex in mesh.vertices]
    polygons = [tuple(polygon.vertices) for polygon in mesh.polygons]
    evaluated.to_mesh_clear()
    return vertices, polygons


def bounds_of(vertices):
    low = mathutils.Vector([min(vertex[axis] for vertex in vertices) for axis in range(3)])
    high = mathutils.Vector([max(vertex[axis] for vertex in vertices) for axis in range(3)])
    return low, high


def box_gap(low_a, high_a, low_b, high_b):
    """Distance between two axis-aligned boxes, 0 when they overlap."""
    total = 0.0
    for axis in range(3):
        gap = max(low_a[axis] - high_b[axis], low_b[axis] - high_a[axis], 0.0)
        total += gap * gap
    return total ** 0.5


def sample(vertices):
    step = max(1, len(vertices) // SAMPLE_LIMIT)
    return vertices[::step]


def first_camera_visible_hit(scene, depsgraph, origin, direction):
    """Name of the first object the camera really sees along the ray; light blockers hidden from it are skipped."""
    start = origin
    for _ in range(12):
        hit, location, _, _, hit_object, _ = scene.ray_cast(depsgraph, start, direction)
        if not hit:
            return None
        if hit_object.visible_camera and not hit_object.hide_render:
            return family_of(hit_object.name)
        start = location + direction * 0.0005
    return None


def frame_map(scene, camera, depsgraph, columns):
    """Cast one ray per cell from the camera and return rows of the object names hit."""
    aspect = scene.render.resolution_y / scene.render.resolution_x
    rows = max(1, round(columns * aspect * 0.5))  # terminal characters are about twice as tall as wide
    corners = [camera.matrix_world @ corner for corner in camera.data.view_frame(scene=scene)]
    top_right, bottom_right, bottom_left, top_left = corners
    origin = camera.matrix_world.translation
    grid = []
    for row in range(rows):
        vertical = (row + 0.5) / rows
        line = []
        for column in range(columns):
            horizontal = (column + 0.5) / columns
            top = top_left.lerp(top_right, horizontal)
            bottom = bottom_left.lerp(bottom_right, horizontal)
            target = top.lerp(bottom, vertical)
            direction = (target - origin).normalized()
            line.append(first_camera_visible_hit(scene, depsgraph, origin, direction))
        grid.append(line)
    return grid


def print_frame_map(grid):
    counts = {}
    for line in grid:
        for name in line:
            counts[name] = counts.get(name, 0) + 1
    ordered = sorted(counts, key=lambda name: -counts[name])
    letter_of = {name: (LETTERS[index] if index < len(LETTERS) else "#") for index, name in enumerate(ordered)}
    letter_of[None] = "."
    total = sum(counts.values())
    print("FRAME MAP (one letter per cell, '.' is empty sky or void)")
    for line in grid:
        print("  " + "".join(letter_of[name] for name in line))
    print("FRAME SHARE")
    for name in ordered:
        share = counts[name] / total
        note = "  <- large plain area? dress it or reframe" if share >= 0.15 else ""
        print(f"  {letter_of[name]} {share:5.1%}  {name}{note}")


def print_readability(scene, camera, meshes):
    print("PROPS IN FRAME (share of the object inside the frame, size on screen; copies as one family)")
    families = {}
    for name, vertices in meshes.items():
        points = [world_to_camera_view(scene, camera, vertex) for vertex in sample(vertices)]
        inside = [point for point in points if point.z > 0 and 0 <= point.x <= 1 and 0 <= point.y <= 1]
        if not inside:
            continue
        share = len(inside) / len(points)
        height = max(point.y for point in inside) - min(point.y for point in inside)
        width = max(point.x for point in inside) - min(point.x for point in inside)
        families.setdefault(family_of(name), []).append((share, height, width))
    for family, members in sorted(families.items()):
        share = min(member[0] for member in members)
        height = max(member[1] for member in members)
        width = max(member[2] for member in members)
        notes = []
        if share < 0.9:
            notes.append("cut by the frame edge")
        if max(height, width) < 0.03:
            notes.append("under 3% of the frame: will not read")
        count = f" x{len(members)}" if len(members) > 1 else ""
        print(f"  {share:5.0%} inside  {height:5.1%} tall  {width:5.1%} wide  {family}{count}"
              + ("  <- " + ", ".join(notes) if notes else ""))


def print_floating(meshes, trees, limit_millimetres, only, skip):
    print(f"CONTACT (gap to the nearest other surface, limit {limit_millimetres} mm)")
    boxes = {name: bounds_of(vertices) for name, vertices in meshes.items()}
    floating = []
    for name, vertices in sorted(meshes.items()):
        if (only and not any(part in name for part in only)) or any(part in name for part in skip):
            continue
        low, high = boxes[name]
        if (high - low).length < 0.0005:
            continue  # scaled to nothing at this frame
        best_gap = float("inf")
        best_other = None
        candidates = sorted((box_gap(low, high, *boxes[other]), other) for other in meshes if other != name)
        for nearest_possible, other in candidates:
            if nearest_possible >= best_gap:
                break
            tree = trees.get(other)
            if tree is None:
                continue
            for vertex in sample(vertices):
                found = tree.find_nearest(vertex)
                if found[0] is not None and found[3] < best_gap:
                    best_gap = found[3]
                    best_other = other
        millimetres = best_gap * 1000
        if millimetres > limit_millimetres:
            floating.append(name)
            print(f"  FLOATS {millimetres:7.1f} mm from {best_other}: {name}")
    if not floating:
        print("  every object touches something")
    return floating


def main():
    arguments = parse_arguments()
    scene = bpy.context.scene
    if arguments.frame is not None:
        scene.frame_set(arguments.frame)
    camera = scene.camera
    if camera is None:
        print("frame audit: the scene has no active camera")
        sys.exit(2)
    depsgraph = bpy.context.evaluated_depsgraph_get()
    meshes = {}
    trees = {}
    for obj in visible_geometry_objects(scene):
        vertices, polygons = world_mesh_data(obj, depsgraph)
        if not vertices:
            continue
        meshes[obj.name] = vertices
        if polygons:
            trees[obj.name] = BVHTree.FromPolygons(vertices, polygons)
    print(f"frame audit: camera {camera.name}, lens {camera.data.lens:.0f} mm, frame {scene.frame_current}, "
          f"{len(meshes)} objects")
    print_frame_map(frame_map(scene, camera, depsgraph, arguments.columns))
    print_readability(scene, camera, meshes)
    only = [part for part in arguments.only.split(",") if part]
    skip = [part for part in arguments.skip.split(",") if part]
    floating = print_floating(meshes, trees, arguments.float_mm, only, skip)
    sys.exit(1 if floating else 0)


main()
