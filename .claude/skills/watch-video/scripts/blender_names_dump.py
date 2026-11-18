"""Run inside Blender to dump the names a tutorial can mention: node titles per editor, modifiers, constraints.

Usage:
  blender -b --factory-startup --python-exit-code 1 -P blender_names_dump.py -- <out.json>

check_blender_names.py reads the JSON. Regenerate it when Blender's version changes.
"""

import json
import sys

import bpy

TREE_TYPES = {
    "shader": "ShaderNodeTree",
    "geometry": "GeometryNodeTree",
    "compositor": "CompositorNodeTree",
    "texture": "TextureNodeTree",
}


def node_titles(tree_type):
    tree = bpy.data.node_groups.new("names_probe", tree_type)
    titles = set()
    for type_name in dir(bpy.types):
        node_class = getattr(bpy.types, type_name)
        if not isinstance(node_class, type) or not issubclass(node_class, bpy.types.Node):
            continue
        try:
            node = tree.nodes.new(type_name)
        except (RuntimeError, TypeError):
            continue
        titles.add(node.bl_label if hasattr(node, "bl_label") else node.name)
        titles.add(node.name.rstrip(".0123456789"))
        tree.nodes.remove(node)
    bpy.data.node_groups.remove(tree)
    return sorted(title for title in titles if title)


def enum_names(property_owner, property_name):
    return sorted(item.name for item in property_owner.bl_rna.properties[property_name].enum_items)


def bundled_node_groups():
    """Node groups shipped as assets (Cloth Dynamics, Smooth Geometry...) appear in Add menus like built-in nodes."""
    import pathlib

    asset_folder = pathlib.Path(bpy.utils.system_resource("DATAFILES")) / "assets" / "nodes"
    group_names = set()
    for blend_path in sorted(asset_folder.glob("*.blend")):
        with bpy.data.libraries.load(str(blend_path)) as (library_data, _):
            group_names.update(library_data.node_groups)
    return sorted(group_names)


def main():
    out_path = sys.argv[sys.argv.index("--") + 1]
    names = {"blender_version": bpy.app.version_string}
    for key, tree_type in TREE_TYPES.items():
        names[key] = node_titles(tree_type)
    names["modifiers"] = enum_names(bpy.types.Modifier, "type")
    names["constraints"] = enum_names(bpy.types.Constraint, "type")
    names["fcurve_modifiers"] = enum_names(bpy.types.FModifier, "type")
    # Area.ui_type lists no items in background mode, so the editor names are written out.
    names["editors"] = [
        "3D Viewport", "Image Editor", "UV Editor", "Shader Editor", "Compositor", "Texture Node Editor",
        "Geometry Node Editor", "Video Sequencer", "Movie Clip Editor", "Dope Sheet", "Timeline", "Graph Editor",
        "Drivers", "Nonlinear Animation", "Text Editor", "Python Console", "Info", "Outliner", "Properties",
        "File Browser", "Asset Browser", "Spreadsheet", "Preferences",
    ]
    names["math_operations"] = sorted(
        set(enum_names(bpy.types.ShaderNodeMath, "operation"))
        | set(enum_names(bpy.types.ShaderNodeVectorMath, "operation"))
        | set(enum_names(bpy.types.ShaderNodeMix, "blend_type"))
    )
    names["render_engines"] = ["Cycles", "Eevee", "Workbench"]
    names["bundled_node_groups"] = bundled_node_groups()
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump(names, handle, indent=1)
    print(f"names written to {out_path}: " + ", ".join(f"{key} {len(value)}" for key, value in names.items() if isinstance(value, list)))


main()
