"""Sculpt a rock procedurally, headless, by the pipeline in references/blender-sculpt-tools.md section 8.

Block (convex hull of scattered points, cut by three joint sets) -> chips (flattened spheres subtracted at corners)
-> voxel remesh -> chamfer smooth -> displacement by scale, fine layers masked to edges and base -> remesh -> low copy by
QuadriFlow (Decimate when it cancels or leaves the mesh unreduced). Fracture planes follow a bedding set plus two steep cross sets, so the rock breaks like
real stone instead of a noise blob.

Run:
  blender -b --python scripts/procedural_rock.py -- --out rock.blend [--seed 4] [--size 1.0] [--low-faces 2000]
"""

import math
import random
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector


def parse_arguments():
    arguments = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    options = {"out": "rock.blend", "seed": 4, "size": 1.0, "low-faces": 2000}
    for index in range(0, len(arguments), 2):
        options[arguments[index].lstrip("-")] = arguments[index + 1]
    return options["out"], int(options["seed"]), float(options["size"]), int(options["low-faces"])


def cut_with_plane(surface, point, normal):
    """Bisect and drop everything on the outer side of the plane: one fracture face."""
    geometry = surface.verts[:] + surface.edges[:] + surface.faces[:]
    result = bmesh.ops.bisect_plane(surface, geom=geometry, plane_co=point, plane_no=normal, clear_outer=True)
    edges = [element for element in result["geom_cut"] if isinstance(element, bmesh.types.BMEdge)]
    if edges:
        bmesh.ops.holes_fill(surface, edges=edges)


def joint_normal(azimuth, dip):
    return Vector((math.cos(azimuth) * math.sin(dip), math.sin(azimuth) * math.sin(dip), math.cos(dip)))


def block_out(size, generator):
    """Convex hull of scattered points (many facets of varied angle), then joint-set cuts that remove real volume."""
    mesh = bpy.data.meshes.new("rock")
    surface = bmesh.new()
    radii = Vector((1.0, generator.uniform(0.65, 0.85), generator.uniform(0.45, 0.6))) * size
    for _ in range(36):
        direction = Vector((generator.gauss(0, 1), generator.gauss(0, 1), generator.gauss(0, 1))).normalized()
        reach = generator.uniform(0.8, 1.0)
        surface.verts.new(Vector((direction.x * radii.x, direction.y * radii.y, direction.z * radii.z)) * reach)
    bmesh.ops.convex_hull(surface, input=surface.verts[:])
    bedding = (generator.uniform(0, 2 * math.pi), math.radians(generator.uniform(8, 20)))
    cross_azimuth = generator.uniform(0, 2 * math.pi)
    joint_sets = [
        bedding,
        (cross_azimuth, math.radians(generator.uniform(72, 88))),
        (cross_azimuth + math.radians(generator.uniform(70, 100)), math.radians(generator.uniform(65, 85))),
    ]
    for index in range(11):
        azimuth, dip = joint_sets[index % 3]
        jitter = math.radians(generator.uniform(-8, 8))
        normal = joint_normal(azimuth + jitter, dip + jitter * 0.5)
        if generator.random() < 0.5:
            normal = -normal
        reach = abs(normal.x) * radii.x + abs(normal.y) * radii.y + abs(normal.z) * radii.z
        cut_with_plane(surface, normal * reach * generator.uniform(0.55, 0.85), normal)
    surface.to_mesh(mesh)
    surface.free()
    rock = bpy.data.objects.new("Rock", mesh)
    bpy.context.scene.collection.objects.link(rock)
    return rock


def add_chips(rock, size, generator, count=6):
    """Flattened spheres subtracted at corners: the concave, shell-shaped spalls where stone breaks off an edge."""
    corners = sorted(rock.data.vertices, key=lambda vertex: -vertex.co.length)[:40]
    for index in range(count):
        corner = generator.choice(corners).co
        radius = size * generator.uniform(0.12, 0.24)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, segments=24, ring_count=12,
                                             location=corner * generator.uniform(1.0, 1.08))
        cutter = bpy.context.active_object
        cutter.scale = (1.0, generator.uniform(0.7, 1.0), generator.uniform(0.35, 0.55))
        cutter.rotation_euler = (generator.uniform(0, 3.1), generator.uniform(0, 3.1), generator.uniform(0, 3.1))
        boolean = rock.modifiers.new(f"chip_{index}", "BOOLEAN")
        boolean.operation = "DIFFERENCE"
        boolean.object = cutter
        activate(rock)
        bpy.ops.object.modifier_apply(modifier=boolean.name)
        bpy.data.objects.remove(cutter)


def edge_and_base_weights(rock, size, iterations=6):
    """Vertex group "wear": high on convex edges and the lower part, low on big flat faces (the rest areas)."""
    surface = bmesh.new()
    surface.from_mesh(rock.data)
    surface.normal_update()
    weights = []
    lowest = min(vertex.co.z for vertex in surface.verts)
    highest = max(vertex.co.z for vertex in surface.verts)
    for vertex in surface.verts:
        neighbours = [edge.other_vert(vertex) for edge in vertex.link_edges]
        if not neighbours:
            weights.append(0.0)
            continue
        average = sum((other.normal for other in neighbours), Vector()) / len(neighbours)
        bend = vertex.normal.angle(average.normalized(), 0.0) if average.length else 0.0
        height = (vertex.co.z - lowest) / max(1e-6, highest - lowest)
        weights.append(min(1.0, bend * 6.0) * 0.8 + (1.0 - height) * 0.35)
    for _ in range(iterations):
        smoothed = []
        for vertex in surface.verts:
            neighbours = [edge.other_vert(vertex).index for edge in vertex.link_edges]
            total = weights[vertex.index] + sum(weights[index] for index in neighbours)
            smoothed.append(total / (1 + len(neighbours)))
        weights = smoothed
    surface.free()
    group = rock.vertex_groups.new(name="wear")
    for index, weight in enumerate(weights):
        group.add([index], min(1.0, weight * 1.6), "REPLACE")
    return group.name


def activate(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def remesh(obj, voxel_size):
    activate(obj)
    obj.data.remesh_voxel_size = voxel_size
    bpy.ops.object.voxel_remesh()


def add_displace(obj, name, texture_type, scale, strength, seed, mid_level=0.5, group=None):
    texture = bpy.data.textures.new(name, texture_type)
    if texture_type == "VORONOI":
        texture.distance_metric = "DISTANCE"
    texture.noise_scale = scale
    modifier = obj.modifiers.new(name, "DISPLACE")
    modifier.texture = texture
    modifier.texture_coords = "LOCAL"
    modifier.strength = strength
    modifier.mid_level = mid_level
    if group:
        modifier.vertex_group = group
    random.seed(seed)


def apply_all(obj):
    activate(obj)
    for modifier in list(obj.modifiers):
        bpy.ops.object.modifier_apply(modifier=modifier.name)


def main():
    out_path, seed, size, low_faces = parse_arguments()
    generator = random.Random(seed)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    rock = block_out(size, generator)
    add_chips(rock, size, generator)
    remesh(rock, size * 0.012)
    chamfer = rock.modifiers.new("chamfer_edges", "SMOOTH")
    chamfer.iterations = 4
    chamfer.factor = 0.5
    apply_all(rock)
    wear = edge_and_base_weights(rock, size)
    add_displace(rock, "medium_ledges", "DISTORTED_NOISE", size * 0.28, size * 0.018, seed + 1)
    add_displace(rock, "pits", "VORONOI", size * 0.06, size * 0.006, seed + 3, group=wear)
    add_displace(rock, "grain", "CLOUDS", size * 0.02, size * 0.008, seed + 2, group=wear)
    apply_all(rock)
    remesh(rock, size * 0.006)
    if hasattr(rock.data, "shade_smooth"):
        rock.data.shade_smooth()

    low = rock.copy()
    low.data = rock.data.copy()
    low.name = "Rock_low"
    bpy.context.scene.collection.objects.link(low)
    method = make_low_poly(low, low_faces)
    low.location.x = size * 2.6
    bpy.ops.wm.save_as_mainfile(filepath=out_path)
    print(f"high faces {len(rock.data.polygons)}, low faces {len(low.data.polygons)} by {method} -> {out_path}")


def triangle_count(mesh):
    return sum(len(polygon.vertices) - 2 for polygon in mesh.polygons)


def make_low_poly(obj, target_faces):
    """Low copy near target_faces. QuadriFlow needs a manifold mesh with consistent normals, so clean first.

    QuadriFlow can return FINISHED without remeshing (Blender 4.4 warns "The mesh needs to be manifold" and leaves the
    mesh as it was), so the face count after it decides, not its return value. When it did not reduce, Decimate runs.
    """
    activate(obj)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.remove_doubles(threshold=0.0001)
    bpy.ops.mesh.delete_loose()
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.mesh.select_all(action="DESELECT")
    bpy.ops.mesh.select_non_manifold()
    bpy.ops.object.mode_set(mode="OBJECT")
    non_manifold = sum(1 for vertex in obj.data.vertices if vertex.select)
    faces_before = len(obj.data.polygons)
    result = bpy.ops.object.quadriflow_remesh(mode="FACES", target_faces=target_faces)
    faces_after = len(obj.data.polygons)
    quadriflow_reduced = "FINISHED" in result and faces_after < faces_before // 2
    if quadriflow_reduced:
        return f"QuadriFlow ({non_manifold} non-manifold vertices before)"
    # Decimate collapse counts triangles, and a collapsed mesh is all triangles, so the ratio is taken over the
    # triangles of the current mesh; a ratio over quads landed the low copy about 4x over target.
    decimate = obj.modifiers.new("decimate", "DECIMATE")
    decimate.ratio = min(1.0, target_faces / max(1, triangle_count(obj.data)))
    bpy.ops.object.modifier_apply(modifier=decimate.name)
    reason = "QuadriFlow did not reduce the mesh" if "FINISHED" in result else "QuadriFlow cancelled"
    return f"Decimate ({reason}, {non_manifold} non-manifold vertices)"


if __name__ == "__main__":
    main()
