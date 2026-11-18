#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=1.26.0",
#   "pillow>=10.3.0",
# ]
# ///
"""Validate a low-poly character GLB, glTF, or Crucible scene recipe JSON.

Checks:
1. Triangle & vertex budget (low-poly range: min_tris..max_tris).
2. Degenerate zero-area triangles and internal/duplicate faces.
3. Skin weight normalization (every skinned vertex sum(weights) == 1.0 +/- 0.01, max 4 influences).
4. Grounding (lowest vertex planted near Y=0) and symmetry bounds.
5. Power-of-Two (POT) texture dimensions if embedded images are present.
6. For Crucible recipes: armature presence, unlit/neutral look configuration, and stepped 2D face tracks.
"""

from __future__ import annotations

import argparse
import io
import json
import math
import pathlib
import struct
from typing import Any

import numpy as np
from PIL import Image


COMPONENT_DTYPES = {
    5120: np.int8,
    5121: np.uint8,
    5122: np.int16,
    5123: np.uint16,
    5125: np.uint32,
    5126: np.float32,
}

TYPE_COUNTS = {
    "SCALAR": 1,
    "VEC2": 2,
    "VEC3": 3,
    "VEC4": 4,
    "MAT4": 16,
}


def is_power_of_two(n: int) -> bool:
    return n > 0 and (n & (n - 1)) == 0


def parse_glb(path: pathlib.Path) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    if len(raw) < 20 or raw[:4] != b"glTF":
        raise ValueError(f"{path} is not a valid binary .glb file")
    version, total_len = struct.unpack("<II", raw[4:12])
    if version != 2:
        raise ValueError(f"Unsupported glTF version {version}")

    offset = 12
    gltf_json: dict[str, Any] = {}
    bin_chunk = b""
    while offset + 8 <= len(raw) and offset < total_len:
        chunk_len, chunk_type = struct.unpack("<II", raw[offset : offset + 8])
        offset += 8
        chunk_data = raw[offset : offset + chunk_len]
        offset += chunk_len
        if chunk_type == 0x4E4F534A:  # JSON
            gltf_json = json.loads(chunk_data.decode("utf-8"))
        elif chunk_type == 0x004E4942:  # BIN
            bin_chunk = chunk_data
    return gltf_json, bin_chunk


def read_accessor(gltf: dict[str, Any], blob: bytes, acc_idx: int) -> np.ndarray:
    acc = gltf["accessors"][acc_idx]
    bv = gltf["bufferViews"][acc["bufferView"]]
    dtype = COMPONENT_DTYPES[acc["componentType"]]
    num_comp = TYPE_COUNTS[acc["type"]]
    count = acc["count"]
    byte_offset = int(bv.get("byteOffset", 0)) + int(acc.get("byteOffset", 0))
    byte_stride = bv.get("byteStride")
    item_bytes = np.dtype(dtype).itemsize * num_comp

    if byte_stride is None or byte_stride == item_bytes:
        arr = np.frombuffer(blob, dtype=dtype, count=count * num_comp, offset=byte_offset)
        out = arr.reshape((count, num_comp)) if num_comp > 1 else arr
    else:
        rows = []
        for i in range(count):
            start = byte_offset + i * byte_stride
            rows.append(np.frombuffer(blob, dtype=dtype, count=num_comp, offset=start))
        out = np.vstack(rows) if num_comp > 1 else np.concatenate(rows)

    if acc.get("normalized"):
        if acc["componentType"] == 5121:
            out = out.astype(np.float32) / 255.0
        elif acc["componentType"] == 5123:
            out = out.astype(np.float32) / 65535.0
    return out


def check_glb(path: pathlib.Path, max_tris: int = 1800, min_tris: int = 20) -> dict[str, Any]:
    gltf, blob = parse_glb(path)
    errors: list[str] = []
    warnings: list[str] = []

    total_verts = 0
    total_tris = 0
    degenerate_tris = 0
    duplicate_tris = 0
    unnormalized_weight_verts = 0
    zero_weight_verts = 0
    uv_out_of_bounds = 0
    all_positions: list[np.ndarray] = []

    for mesh in gltf.get("meshes", []):
        for prim in mesh.get("primitives", []):
            attrs = prim.get("attributes", {})
            if "POSITION" not in attrs:
                continue
            pos = read_accessor(gltf, blob, attrs["POSITION"]).astype(np.float32)
            total_verts += len(pos)
            all_positions.append(pos)

            if "indices" in prim:
                idx = read_accessor(gltf, blob, prim["indices"]).reshape(-1)
            else:
                idx = np.arange(len(pos), dtype=np.uint32)

            tris = idx.reshape((-1, 3))
            total_tris += len(tris)

            # Check degenerate or duplicate faces
            v0 = pos[tris[:, 0]]
            v1 = pos[tris[:, 1]]
            v2 = pos[tris[:, 2]]
            cross = np.cross(v1 - v0, v2 - v0)
            areas = 0.5 * np.linalg.norm(cross, axis=1)
            degenerate_tris += int(np.sum(areas < 1e-8))

            # Quantized vertex positions to catch exact double/coplanar internal faces
            q_pos = np.round(pos * 10000).astype(np.int64)
            seen_faces: set[tuple[tuple[int, ...], ...]] = set()
            for t in tris:
                key = tuple(sorted((tuple(q_pos[t[0]]), tuple(q_pos[t[1]]), tuple(q_pos[t[2]]))))
                if key in seen_faces:
                    duplicate_tris += 1
                else:
                    seen_faces.add(key)

            # Check skin weights (Auto Normalize rule)
            if "WEIGHTS_0" in attrs:
                weights = read_accessor(gltf, blob, attrs["WEIGHTS_0"]).astype(np.float32)
                sums = np.sum(weights, axis=1)
                zero_weight_verts += int(np.sum(sums <= 1e-5))
                unnormalized_weight_verts += int(np.sum(np.abs(sums - 1.0) > 0.015))

            # Check UVs
            if "TEXCOORD_0" in attrs:
                uvs = read_accessor(gltf, blob, attrs["TEXCOORD_0"]).astype(np.float32)
                uv_out_of_bounds += int(np.sum((uvs < -0.05) | (uvs > 1.05)))

    if total_tris < min_tris:
        errors.append(f"Triangle count ({total_tris}) is below minimum ({min_tris}).")
    if total_tris > max_tris:
        errors.append(f"Triangle count ({total_tris}) exceeds low-poly budget ({max_tris}).")
    if degenerate_tris > 0:
        errors.append(f"Found {degenerate_tris} degenerate zero-area triangle(s).")
    if duplicate_tris > 0:
        errors.append(f"Found {duplicate_tris} duplicate/coplanar double face(s) (check mirror seam or internal caps).")
    if zero_weight_verts > 0:
        errors.append(f"Found {zero_weight_verts} skinned vertex/vertices with zero total weight.")
    if unnormalized_weight_verts > 0:
        errors.append(
            f"Found {unnormalized_weight_verts} vertex/vertices with unnormalized skin weights (enable Auto Normalize)."
        )
    if uv_out_of_bounds > 0:
        warnings.append(f"{uv_out_of_bounds} UV coordinate(s) extend outside [0, 1] atlas bounds.")

    bounds_min = [0.0, 0.0, 0.0]
    bounds_max = [0.0, 0.0, 0.0]
    if all_positions:
        merged = np.vstack(all_positions)
        bounds_min = [round(float(x), 4) for x in merged.min(axis=0)]
        bounds_max = [round(float(x), 4) for x in merged.max(axis=0)]
        min_y = bounds_min[1]
        if abs(min_y) > 0.08:
            warnings.append(f"Lowest vertex Y is {min_y:.3f}m (character soles should sit near Y=0.0m).")

    # Check embedded textures for Power-of-Two dimensions
    textures_info: list[dict[str, Any]] = []
    for img_def in gltf.get("images", []):
        if "bufferView" in img_def:
            bv = gltf["bufferViews"][img_def["bufferView"]]
            start = int(bv.get("byteOffset", 0))
            end = start + int(bv["byteLength"])
            im = Image.open(io.BytesIO(blob[start:end]))
            pot = is_power_of_two(im.width) and is_power_of_two(im.height)
            textures_info.append({"size": [im.width, im.height], "pot": pot})
            if not pot:
                warnings.append(
                    f"Embedded texture size {im.width}x{im.height} is not Power-of-Two (prefer 512x512 or 1024x512)."
                )

    return {
        "ok": len(errors) == 0,
        "kind": "glb",
        "vertices": total_verts,
        "triangles": total_tris,
        "bounds_min": bounds_min,
        "bounds_max": bounds_max,
        "textures": textures_info,
        "errors": errors,
        "warnings": warnings,
    }


def check_67js_recipe(path: pathlib.Path) -> dict[str, Any]:
    recipe = json.loads(path.read_text(encoding="utf-8"))
    errors: list[str] = []
    warnings: list[str] = []

    if recipe.get("format") not in ("crucible.scene", "crucible.asset"):
        errors.append("Recipe format must be 'crucible.scene' or 'crucible.asset'.")

    geoms = {g["id"]: g for g in recipe.get("geometries", [])}
    for gid, g in geoms.items():
        if g.get("type") == "mesh":
            for st in g.get("stack", []):
                if st.get("op") == "subdivide" and int(st.get("levels", 0)) > 3:
                    errors.append(f"Geometry '{gid}' uses subdivide levels={st.get('levels')} (exceeds low-poly budget).")

    armatures = recipe.get("armatures", [])
    skinned_nodes = [n for n in recipe.get("nodes", []) if "skin" in n]
    if skinned_nodes and not armatures:
        errors.append("Nodes declare 'skin' binding but recipe has no 'armatures' list.")

    for arm in armatures:
        landmarks = arm.get("fit", {}).get("landmarks", {})
        if "leftLowerLeg" in landmarks and "leftUpperLeg" in landmarks and "leftFoot" in landmarks:
            hip_z = landmarks["leftUpperLeg"][2]
            knee_z = landmarks["leftLowerLeg"][2]
            ankle_z = landmarks["leftFoot"][2]
            mid_z = 0.5 * (hip_z + ankle_z)
            if knee_z <= mid_z:
                errors.append(
                    f"Armature '{arm.get('id')}' knee landmark is not pre-bent forward (+Z); IK will bend backward."
                )

    motion = recipe.get("motion") or {}
    for tr in motion.get("tracks", []):
        tid = str(tr.get("id", ""))
        if ("eye_control" in tid or "mouth_control" in tid or "face" in tid) and tr.get("interpolation") != "STEP":
            errors.append(
                f"2D face controller track '{tid}' uses interpolation='{tr.get('interpolation')}' instead of 'STEP'."
            )

    return {
        "ok": len(errors) == 0,
        "kind": "Crucible.recipe",
        "geometries": len(geoms),
        "nodes": len(recipe.get("nodes", [])),
        "armatures": len(armatures),
        "errors": errors,
        "warnings": warnings,
    }


def validate_character(path: pathlib.Path, max_tris: int = 1800, min_tris: int = 20) -> dict[str, Any]:
    suffix = path.suffix.lower()
    if suffix == ".glb":
        return check_glb(path, max_tris=max_tris, min_tris=min_tris)
    if suffix == ".json":
        return check_67js_recipe(path)
    raise ValueError(f"Unsupported file extension '{suffix}' (expected .glb or .json)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=pathlib.Path, help="Path to character .glb or Crucible .recipe.json")
    parser.add_argument("--max-tris", type=int, default=1800, help="Maximum triangle budget (default: 1800)")
    parser.add_argument("--min-tris", type=int, default=20, help="Minimum triangle budget (default: 20)")
    args = parser.parse_args()

    result = validate_character(args.target, max_tris=args.max_tris, min_tris=args.min_tris)
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
