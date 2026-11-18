#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=1.26.0",
#   "pillow>=10.3.0",
# ]
# ///
"""Self-contained unit test suite for model-characters scripts and skill files."""

from __future__ import annotations

import json
import pathlib
import struct
import tempfile
import unittest

import numpy as np
from PIL import Image, ImageDraw

from check_character import validate_character
from read_character_ref import calibrate_reference


def build_minimal_glb(
    positions: np.ndarray,
    indices: np.ndarray,
    weights: np.ndarray | None = None,
) -> bytes:
    pos_bytes = positions.astype(np.float32).tobytes()
    idx_bytes = indices.astype(np.uint16).tobytes()
    while len(idx_bytes) % 4 != 0:
        idx_bytes += b"\x00"

    buffer_views = [
        {"buffer": 0, "byteOffset": 0, "byteLength": len(pos_bytes), "target": 34962},
        {"buffer": 0, "byteOffset": len(pos_bytes), "byteLength": len(idx_bytes), "target": 34963},
    ]
    accessors = [
        {
            "bufferView": 0,
            "componentType": 5126,
            "count": len(positions),
            "type": "VEC3",
            "min": positions.min(axis=0).tolist(),
            "max": positions.max(axis=0).tolist(),
        },
        {
            "bufferView": 1,
            "componentType": 5123,
            "count": len(indices),
            "type": "SCALAR",
        },
    ]
    attrs = {"POSITION": 0}
    blob = pos_bytes + idx_bytes

    if weights is not None:
        w_bytes = weights.astype(np.float32).tobytes()
        buffer_views.append(
            {"buffer": 0, "byteOffset": len(blob), "byteLength": len(w_bytes), "target": 34962}
        )
        accessors.append(
            {
                "bufferView": 2,
                "componentType": 5126,
                "count": len(weights),
                "type": "VEC4",
            }
        )
        attrs["WEIGHTS_0"] = 2
        blob += w_bytes

    gltf = {
        "asset": {"version": "2.0"},
        "buffers": [{"byteLength": len(blob)}],
        "bufferViews": buffer_views,
        "accessors": accessors,
        "meshes": [{"primitives": [{"attributes": attrs, "indices": 1}]}],
    }
    json_bytes = json.dumps(gltf).encode("utf-8")
    while len(json_bytes) % 4 != 0:
        json_bytes += b" "

    total_len = 12 + 8 + len(json_bytes) + 8 + len(blob)
    header = struct.pack("<4sII", b"glTF", 2, total_len)
    json_chunk = struct.pack("<II", len(json_bytes), 0x4E4F534A) + json_bytes
    bin_chunk = struct.pack("<II", len(blob), 0x004E4942) + blob
    return header + json_chunk + bin_chunk


class LowPolyCharacterSkillTests(unittest.TestCase):
    def test_turnaround_calibration_and_atlas(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tdir = pathlib.Path(tmp)
            img = Image.new("RGBA", (240, 200), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            # Front character silhouette (left panel)
            draw.rectangle([35, 20, 85, 65], fill=(245, 205, 180, 255))
            draw.rectangle([30, 65, 90, 125], fill=(65, 110, 210, 255))
            draw.rectangle([35, 125, 85, 185], fill=(45, 50, 75, 255))
            # Side character silhouette (right panel)
            draw.rectangle([155, 20, 195, 65], fill=(245, 205, 180, 255))
            draw.rectangle([160, 65, 195, 125], fill=(65, 110, 210, 255))
            draw.rectangle([162, 125, 192, 185], fill=(45, 50, 75, 255))

            ref_path = tdir / "turnaround.png"
            img.save(ref_path)

            out_dir = tdir / "cal"
            report = calibrate_reference(ref_path, out_dir, world_height=1.70)
            self.assertEqual(report["view_mode"], "front_and_side_turnaround")
            self.assertEqual(len(report["panels_px"]), 2)
            self.assertAlmostEqual(report["landmarks_y_m"]["crown"], 1.70, places=3)
            self.assertAlmostEqual(report["landmarks_y_m"]["sole"], 0.0, places=3)
            self.assertTrue((out_dir / "guide.png").exists())
            self.assertTrue((out_dir / "atlas_template.png").exists())

            with Image.open(out_dir / "atlas_template.png") as atlas:
                self.assertEqual(atlas.size, (512, 512))

    def test_glb_validation_passes_clean_and_catches_faults(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tdir = pathlib.Path(tmp)
            # Build a grounded 24-triangle low-poly prism stack with normalized weights
            angles = np.linspace(0, 2 * np.pi, 7)[:-1]
            ring0 = np.stack([0.15 * np.cos(angles), np.zeros(6), 0.15 * np.sin(angles)], axis=1)
            ring1 = np.stack([0.18 * np.cos(angles), np.full(6, 0.85), 0.18 * np.sin(angles)], axis=1)
            ring2 = np.stack([0.14 * np.cos(angles), np.full(6, 1.70), 0.14 * np.sin(angles)], axis=1)
            positions = np.vstack([ring0, ring1, ring2]).astype(np.float32)

            tris = []
            for r in range(2):
                base = r * 6
                for i in range(6):
                    nxt = (i + 1) % 6
                    tris.extend([base + i, base + nxt, base + 6 + nxt])
                    tris.extend([base + i, base + 6 + nxt, base + 6 + i])
            indices = np.array(tris, dtype=np.uint16)
            weights = np.tile(np.array([[1.0, 0.0, 0.0, 0.0]], dtype=np.float32), (len(positions), 1))

            clean_glb = tdir / "clean.glb"
            clean_glb.write_bytes(build_minimal_glb(positions, indices, weights))
            res = validate_character(clean_glb, max_tris=500, min_tris=12)
            self.assertTrue(res["ok"], msg=res["errors"])
            self.assertEqual(res["triangles"], 24)

            # Corrupt weights (sum = 1.6 > 1.0 -> Auto Normalize off fault)
            bad_weights = np.tile(np.array([[1.0, 0.6, 0.0, 0.0]], dtype=np.float32), (len(positions), 1))
            bad_glb = tdir / "bad_weights.glb"
            bad_glb.write_bytes(build_minimal_glb(positions, indices, bad_weights))
            res_bad = validate_character(bad_glb, max_tris=500, min_tris=12)
            self.assertFalse(res_bad["ok"])
            self.assertTrue(any("unnormalized skin weights" in e for e in res_bad["errors"]))

    def test_67js_recipe_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tdir = pathlib.Path(tmp)
            good_recipe = {
                "format": "crucible.scene",
                "schemaVersion": 1,
                "geometries": [{"id": "leg", "type": "mesh", "base": {"type": "cylinder", "radialSegments": 5}}],
                "materials": [{"id": "mat", "tag": "unlit", "color": [0.9, 0.8, 0.7]}],
                "armatures": [
                    {
                        "id": "rig",
                        "preset": "humanoid",
                        "fit": {
                            "bounds": {"min": [-0.3, 0, -0.15], "max": [0.3, 1.7, 0.15]},
                            "landmarks": {
                                "leftUpperLeg": [0.1, 0.84, 0.0],
                                "leftLowerLeg": [0.1, 0.45, 0.02],
                                "leftFoot": [0.1, 0.06, 0.0],
                            },
                        },
                    }
                ],
                "nodes": [{"id": "leg-node", "geometry": "leg", "material": "mat", "skin": {"armature": "rig"}}],
                "motion": {
                    "duration": 1.0,
                    "loop": True,
                    "tracks": [
                        {
                            "kind": "node",
                            "id": "eye_control",
                            "property": "translation",
                            "interpolation": "STEP",
                            "keyframes": [{"time": 0, "value": [0, 0, 0]}, {"time": 0.5, "value": [0, 0, 0.1]}],
                        }
                    ],
                },
            }
            good_path = tdir / "good.recipe.json"
            good_path.write_text(json.dumps(good_recipe), encoding="utf-8")
            res = validate_character(good_path)
            self.assertTrue(res["ok"], msg=res["errors"])

            # Fault: non-stepped 2D face controller + straight/backward knee
            bad_recipe = json.loads(json.dumps(good_recipe))
            bad_recipe["motion"]["tracks"][0]["interpolation"] = "SMOOTH"
            bad_recipe["armatures"][0]["fit"]["landmarks"]["leftLowerLeg"] = [0.1, 0.45, -0.02]
            bad_path = tdir / "bad.recipe.json"
            bad_path.write_text(json.dumps(bad_recipe), encoding="utf-8")
            res_bad = validate_character(bad_path)
            self.assertFalse(res_bad["ok"])
            self.assertEqual(len(res_bad["errors"]), 2)


if __name__ == "__main__":
    unittest.main()
