"""Build a test sculpt fixture saved to the given .blend.

Default: Suzanne with a subdivision level and a little noise (passes the measured checks).
With --broken: the same head with unapplied scale and a loose vertex (fails two checks).
"""
import sys

import bmesh
import bpy

arguments = sys.argv[sys.argv.index("--") + 1:]
target = arguments[0]
broken = "--broken" in arguments
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.mesh.primitive_monkey_add()
monkey = bpy.context.active_object
monkey.modifiers.new("subdivision", "SUBSURF").levels = 2
displace = monkey.modifiers.new("noise", "DISPLACE")
displace.texture = bpy.data.textures.new("noise", "CLOUDS")
displace.strength = 0.02
if broken:
    monkey.scale = (1.3, 1.0, 1.0)
    surface = bmesh.new()
    surface.from_mesh(monkey.data)
    surface.verts.new((3.0, 0.0, 0.0))
    surface.to_mesh(monkey.data)
    surface.free()
bpy.ops.wm.save_as_mainfile(filepath=target)
