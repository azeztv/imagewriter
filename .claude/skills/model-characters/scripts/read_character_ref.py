#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pillow>=10.3.0",
#   "numpy>=1.26.0",
# ]
# ///
"""Calibrate a 2D character reference or turnaround image for low-poly 3D modeling.

Detects foreground character silhouette(s) (single view or side-by-side front/side turnaround),
normalizes height to world units (feet at Y=0, crown at target height), estimates anatomical
landmark heights and widths/depths, extracts a quantized color palette, and writes:
  - calibration.json
  - guide.png (annotated proportion & joint ruler)
  - atlas_template.png (POT 512x512 starter texture atlas with 3-step ramps and shadow swatch)
"""

from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any

import numpy as np
from PIL import Image, ImageDraw


LANDMARK_RATIOS = {
    "crown": 1.000,
    "eye_line": 0.885,
    "chin": 0.820,
    "shoulder": 0.785,
    "elbow": 0.610,
    "waist": 0.575,
    "wrist": 0.475,
    "crotch": 0.470,
    "knee": 0.265,
    "ankle": 0.065,
    "sole": 0.000,
}


def compute_foreground_mask(img: Image.Image, bg_tolerance: int = 24) -> np.ndarray:
    rgba = np.asarray(img.convert("RGBA"), dtype=np.uint8)
    alpha = rgba[:, :, 3]
    if int(alpha.min()) < 200 and np.any(alpha > 32):
        return alpha > 32

    rgb = rgba[:, :, :3].astype(np.int16)
    corners = np.vstack([rgb[0, 0], rgb[0, -1], rgb[-1, 0], rgb[-1, -1]])
    bg = np.median(corners, axis=0)
    dist = np.max(np.abs(rgb - bg), axis=2)
    mask = dist > bg_tolerance
    if not np.any(mask):
        mask = np.ones(rgb.shape[:2], dtype=bool)
    return mask


def split_turnaround_panels(mask: np.ndarray) -> list[tuple[int, int, int, int]]:
    h, w = mask.shape
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return [(0, 0, w, h)]
    y0, y1 = int(ys.min()), int(ys.max()) + 1
    x0, x1 = int(xs.min()), int(xs.max()) + 1

    col_counts = mask[y0:y1, x0:x1].sum(axis=0)
    span_w = x1 - x0
    mid_start = int(span_w * 0.30)
    mid_end = int(span_w * 0.70)
    if mid_end > mid_start + 4:
        mid_slice = col_counts[mid_start:mid_end]
        gap_cols = np.where(mid_slice == 0)[0]
        if len(gap_cols) >= max(2, int(span_w * 0.015)):
            split_x = x0 + mid_start + int(np.median(gap_cols))
            left_xs = np.where(mask[:, :split_x])[1]
            right_xs = np.where(mask[:, split_x:])[1]
            if len(left_xs) > 0 and len(right_xs) > 0:
                lx0, lx1 = int(left_xs.min()), int(left_xs.max()) + 1
                rx0, rx1 = split_x + int(right_xs.min()), split_x + int(right_xs.max()) + 1
                return [(lx0, y0, lx1, y1), (rx0, y0, rx1, y1)]

    return [(x0, y0, x1, y1)]


def measure_profile(mask: np.ndarray, box: tuple[int, int, int, int], world_height: float) -> dict[str, float]:
    x0, y0, x1, y1 = box
    sub = mask[y0:y1, x0:x1]
    ph, pw = sub.shape
    if ph <= 1 or pw <= 1:
        return {k: 0.1 for k in LANDMARK_RATIOS}

    meters_per_px = world_height / float(ph)
    widths: dict[str, float] = {}
    for name, ratio in LANDMARK_RATIOS.items():
        row_idx = int(np.clip(round((1.0 - ratio) * (ph - 1)), 0, ph - 1))
        r0 = max(0, row_idx - 2)
        r1 = min(ph, row_idx + 3)
        band = np.any(sub[r0:r1, :], axis=0)
        cols = np.where(band)[0]
        if len(cols) >= 2:
            span_px = float(cols[-1] - cols[0] + 1)
        else:
            span_px = float(pw * 0.25)
        widths[name] = round(span_px * meters_per_px, 4)
    return widths


def extract_palette(img: Image.Image, mask: np.ndarray, count: int = 8) -> list[dict[str, Any]]:
    rgba = np.asarray(img.convert("RGBA"), dtype=np.uint8)
    fg_pixels = rgba[mask][:, :3]
    if len(fg_pixels) == 0:
        fg_pixels = rgba.reshape(-1, 4)[:, :3]

    sample = Image.fromarray(fg_pixels.reshape(1, -1, 3), mode="RGB")
    quant = sample.quantize(colors=count, method=Image.Quantize.MEDIANCUT)
    palette_raw = quant.getpalette()[: count * 3]
    indices = np.asarray(quant).reshape(-1)

    swatches: list[dict[str, Any]] = []
    total = max(1, len(indices))
    for idx in range(count):
        cnt = int(np.sum(indices == idx))
        if cnt == 0:
            continue
        r, g, b = palette_raw[idx * 3 : idx * 3 + 3]
        hex_code = f"#{r:02x}{g:02x}{b:02x}"
        hi = (min(255, int(r * 1.15 + 12)), min(255, int(g * 1.15 + 12)), min(255, int(b * 1.15 + 12)))
        sh = (max(0, int(r * 0.72)), max(0, int(g * 0.72)), max(0, int(b * 0.72)))
        swatches.append(
            {
                "hex": hex_code,
                "rgb": [r, g, b],
                "share": round(cnt / total, 4),
                "ramp": {
                    "highlight": f"#{hi[0]:02x}{hi[1]:02x}{hi[2]:02x}",
                    "mid": hex_code,
                    "shadow": f"#{sh[0]:02x}{sh[1]:02x}{sh[2]:02x}",
                },
            }
        )
    swatches.sort(key=lambda s: s["share"], reverse=True)
    return swatches


def save_atlas_template(swatches: list[dict[str, Any]], out_path: pathlib.Path, size: int = 512) -> None:
    atlas = Image.new("RGBA", (size, size), (36, 36, 42, 255))
    draw = ImageDraw.Draw(atlas)

    half = size // 2
    # Quadrant borders
    draw.rectangle([0, 0, half - 1, half - 1], outline=(90, 90, 105, 255))
    draw.rectangle([half, 0, size - 1, half - 1], outline=(90, 90, 105, 255))
    draw.rectangle([0, half, half - 1, size - 1], outline=(90, 90, 105, 255))
    draw.rectangle([half, half, size - 1, size - 1], outline=(90, 90, 105, 255))

    # Top-Right: Hair vertical gradient strip + shadow cavity block
    base_hair = swatches[0]["rgb"] if swatches else [90, 110, 180]
    for y in range(half):
        t = y / max(1, half - 1)
        r = int(np.clip(base_hair[0] * (1.2 - 0.45 * t), 0, 255))
        g = int(np.clip(base_hair[1] * (1.2 - 0.45 * t), 0, 255))
        b = int(np.clip(base_hair[2] * (1.2 - 0.45 * t), 0, 255))
        draw.line([(half + 8, y), (size - 72, y)], fill=(r, g, b, 255))

    # Dedicated dark cavity/underside shadow swatch at top-right corner
    draw.rectangle([size - 64, 8, size - 8, 64], fill=(22, 18, 28, 255))

    # Bottom-Right: 3-step color ramp swatches (Highlight | Mid | Shadow)
    row_h = max(16, (half - 16) // max(1, len(swatches)))
    for i, sw in enumerate(swatches[:8]):
        y0 = half + 8 + i * row_h
        y1 = min(size - 8, y0 + row_h - 2)
        band_w = (half - 16) // 3
        for j, key in enumerate(["highlight", "mid", "shadow"]):
            hx = sw["ramp"][key].lstrip("#")
            rgb = tuple(int(hx[k : k + 2], 16) for k in (0, 2, 4))
            bx0 = half + 8 + j * band_w
            bx1 = bx0 + band_w
            draw.rectangle([bx0, y0, bx1, y1], fill=(*rgb, 255))

    # Top-Left: Face base & 6-cell expression strip guide
    skin_rgb = swatches[1]["rgb"] if len(swatches) > 1 else [242, 206, 182]
    draw.rectangle([8, 8, half - 8, half - 8], fill=(*skin_rgb, 255))
    cell_w = (half - 16) // 6
    for c in range(6):
        cx0 = 8 + c * cell_w
        draw.rectangle([cx0, half - 56, cx0 + cell_w - 1, half - 12], outline=(60, 45, 45, 255))

    atlas.save(out_path)


def save_guide_image(
    img: Image.Image,
    panels: list[tuple[int, int, int, int]],
    world_height: float,
    out_path: pathlib.Path,
) -> None:
    guide = img.convert("RGBA")
    draw = ImageDraw.Draw(guide)
    w, _ = guide.size
    x0, y0, x1, y1 = panels[0]
    ph = max(1, y1 - y0)

    for idx, (px0, py0, px1, py1) in enumerate(panels):
        label = "FRONT" if idx == 0 else "SIDE"
        draw.rectangle([px0, py0, px1, py1], outline=(0, 255, 180, 255), width=2)
        draw.text((px0 + 4, max(0, py0 - 14)), label, fill=(0, 255, 180, 255))

    for name, ratio in LANDMARK_RATIOS.items():
        y_px = int(round(y0 + (1.0 - ratio) * ph))
        z_m = round(ratio * world_height, 3)
        draw.line([(0, y_px), (w, y_px)], fill=(255, 215, 0, 170), width=1)
        draw.text((6, max(0, y_px - 11)), f"{name}: {z_m:.2f}m", fill=(255, 230, 80, 255))

    guide.save(out_path)


def calibrate_reference(
    image_path: pathlib.Path,
    out_dir: pathlib.Path,
    world_height: float = 1.70,
    bg_tolerance: int = 24,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    with Image.open(image_path) as raw_img:
        img = raw_img.copy()
    mask = compute_foreground_mask(img, bg_tolerance=bg_tolerance)
    panels = split_turnaround_panels(mask)

    front_box = panels[0]
    front_widths = measure_profile(mask, front_box, world_height)
    if len(panels) >= 2:
        side_depths = measure_profile(mask, panels[1], world_height)
        view_mode = "front_and_side_turnaround"
    else:
        side_depths = {
            k: round(v * (1.05 if k in ("crown", "eye_line", "chin", "knee", "ankle") else 0.65), 4)
            for k, v in front_widths.items()
        }
        view_mode = "single_view_inferred_depth"

    landmarks_world = {k: round(r * world_height, 4) for k, r in LANDMARK_RATIOS.items()}
    head_height = round(landmarks_world["crown"] - landmarks_world["chin"], 4)
    head_count = round(world_height / max(0.05, head_height), 2)
    swatches = extract_palette(img, mask, count=8)

    report: dict[str, Any] = {
        "source": str(image_path.name),
        "image_size": [img.width, img.height],
        "view_mode": view_mode,
        "panels_px": [list(b) for b in panels],
        "world_height_m": world_height,
        "estimated_head_count": head_count,
        "landmarks_y_m": landmarks_world,
        "front_widths_m": front_widths,
        "side_depths_m": side_depths,
        "recommended_part_budgets": {
            "foot": {"primitive": "cube_2_loopcuts", "verts_per_side": 16},
            "leg": {"primitive": "cylinder_5_verts_open", "verts_per_side": 25, "knee_prebend_m": 0.02},
            "waist": {"primitive": "mirrored_cube_bridged_cuffs", "verts_total": 36},
            "torso": {"primitive": "mirrored_cube_extruded_collar", "verts_total": 60},
            "arm": {"primitive": "rotated_4gon_tube_open", "verts_per_side": 20, "elbow_prebend_m": -0.02},
            "hand": {"primitive": "mitten_cube_merged_tips", "verts_per_side": 18},
            "neck": {"primitive": "cylinder_3_verts_open", "verts_total": 6},
            "face": {"primitive": "mirrored_plane_knife_cuts", "verts_total": 38},
            "hair": {"primitive": "cap_plus_extruded_triangle_spikes", "verts_total": 96},
        },
        "palette": swatches,
    }

    (out_dir / "calibration.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    save_guide_image(img, panels, world_height, out_dir / "guide.png")
    save_atlas_template(swatches, out_dir / "atlas_template.png")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=pathlib.Path, help="Path to 2D character reference or turnaround PNG/JPG")
    parser.add_argument("--height", type=float, default=1.70, help="Target character height in meters (default: 1.70)")
    parser.add_argument("--bg-tolerance", type=int, default=24, help="Background color tolerance (default: 24)")
    parser.add_argument("--out", type=pathlib.Path, default=pathlib.Path("cal"), help="Output directory")
    args = parser.parse_args()

    report = calibrate_reference(args.image, args.out, world_height=args.height, bg_tolerance=args.bg_tolerance)
    print(
        f"Calibrated {report['source']} ({report['view_mode']}): "
        f"height={report['world_height_m']}m, ~{report['estimated_head_count']} heads, "
        f"{len(report['palette'])} palette swatches -> {args.out}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
