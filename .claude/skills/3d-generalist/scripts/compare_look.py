"""Compare rendered frames with the picked style frame: the look match gate in references/qa-and-gates.md.

Measures, for the style frame and for every checked frame: mean luma (Rec. 709, 0-255), mean saturation (0-1) and the
saturation-weighted mean hue (degrees on the colour wheel). A frame fails when its luma or saturation leaves the band
around the style frame, or when its mean hue turns too far. This catches the usual drift: shots rendered darker, greyer or in another colour
cast than the look the user picked. It does not judge composition or taste.

Run:
  uv run --no-project --with numpy python scripts/compare_look.py --style styleframes/B.png <frames or videos...>
      [--fps 1] [--luma-band 20] [--saturation-band 0.08] [--hue-shift 20] [--json report.json]

Inputs can be images or videos (videos are sampled at --fps). Exit code 0 when every frame is inside the band,
1 when one is outside, 2 when a file cannot be read.
"""

import argparse
import json
import pathlib
import subprocess
import sys

import numpy

ANALYSIS_WIDTH = 160
ANALYSIS_HEIGHT = 90
MIN_SATURATION_FOR_HUE = 0.08
VIDEO_SUFFIXES = {".mp4", ".mov", ".webm", ".mkv", ".avi", ".m4v"}


def decode_frames(path, frames_per_second):
    filters = f"scale={ANALYSIS_WIDTH}:{ANALYSIS_HEIGHT}"
    if path.suffix.lower() in VIDEO_SUFFIXES:
        filters = f"fps={frames_per_second}," + filters
    command = ["ffmpeg", "-v", "error", "-i", str(path), "-vf", filters, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    result = subprocess.run(command, capture_output=True)
    if result.returncode != 0 or not result.stdout:
        raise ValueError(f"cannot read {path}: {result.stderr.decode(errors='replace').strip()}")
    frame_size = ANALYSIS_WIDTH * ANALYSIS_HEIGHT * 3
    frame_count = len(result.stdout) // frame_size
    pixels = numpy.frombuffer(result.stdout[: frame_count * frame_size], dtype=numpy.uint8)
    return pixels.reshape(frame_count, ANALYSIS_HEIGHT, ANALYSIS_WIDTH, 3).astype(numpy.float64) / 255.0


def measure(frame):
    red = frame[..., 0]
    green = frame[..., 1]
    blue = frame[..., 2]
    luma = (0.2126 * red + 0.7152 * green + 0.0722 * blue) * 255.0
    highest = frame.max(axis=-1)
    lowest = frame.min(axis=-1)
    spread = highest - lowest
    saturation = numpy.where(highest > 0, spread / numpy.maximum(highest, 1e-9), 0.0)
    safe_spread = numpy.maximum(spread, 1e-9)
    hue = numpy.where(
        highest == red,
        ((green - blue) / safe_spread) % 6,
        numpy.where(highest == green, (blue - red) / safe_spread + 2, (red - green) / safe_spread + 4),
    )
    angle = hue / 6.0 * 2.0 * numpy.pi
    weighted_x = float((saturation * numpy.cos(angle)).sum())
    weighted_y = float((saturation * numpy.sin(angle)).sum())
    return {
        "luma": float(luma.mean()),
        "saturation": float(saturation.mean()),
        "hue_degrees": float(numpy.degrees(numpy.arctan2(weighted_y, weighted_x)) % 360.0),
    }


def hue_shift(first_degrees, second_degrees):
    difference = abs(first_degrees - second_degrees) % 360.0
    return min(difference, 360.0 - difference)


def compare(style, frame, luma_band, saturation_band, hue_shift_limit):
    luma_difference = frame["luma"] - style["luma"]
    saturation_difference = frame["saturation"] - style["saturation"]
    both_coloured = min(style["saturation"], frame["saturation"]) >= MIN_SATURATION_FOR_HUE
    shift = hue_shift(style["hue_degrees"], frame["hue_degrees"]) if both_coloured else 0.0
    problems = []
    if abs(luma_difference) > luma_band:
        problems.append("darker" if luma_difference < 0 else "brighter")
    if abs(saturation_difference) > saturation_band:
        problems.append("greyer" if saturation_difference < 0 else "more saturated")
    if shift > hue_shift_limit:
        problems.append("colour cast differs")
    return {
        "luma": round(frame["luma"], 1),
        "luma_difference": round(luma_difference, 1),
        "saturation": round(frame["saturation"], 3),
        "saturation_difference": round(saturation_difference, 3),
        "hue_shift_degrees": round(shift, 1),
        "problems": problems,
    }


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--style", required=True, type=pathlib.Path, help="the picked style frame")
    parser.add_argument("inputs", nargs="+", type=pathlib.Path, help="rendered frames or videos")
    parser.add_argument("--fps", type=float, default=1.0)
    parser.add_argument("--luma-band", type=float, default=20.0, help="allowed mean luma difference, 0-255")
    parser.add_argument("--saturation-band", type=float, default=0.08, help="allowed mean saturation difference")
    parser.add_argument("--hue-shift", type=float, default=20.0, help="allowed mean hue turn, degrees")
    parser.add_argument("--json", type=pathlib.Path, help="write the full report here")
    arguments = parser.parse_args()

    try:
        style = measure(decode_frames(arguments.style, arguments.fps)[0])
        rows = []
        for input_path in arguments.inputs:
            for index, frame in enumerate(decode_frames(input_path, arguments.fps)):
                result = compare(
                    style, measure(frame), arguments.luma_band, arguments.saturation_band, arguments.hue_shift
                )
                result["file"] = str(input_path)
                result["second"] = round(index / arguments.fps, 2) if input_path.suffix.lower() in VIDEO_SUFFIXES else None
                rows.append(result)
    except ValueError as error:
        print(error)
        return 2

    print(f"style {arguments.style}: luma {style['luma']:.1f}, saturation {style['saturation']:.3f}")
    failures = [row for row in rows if row["problems"]]
    for row in rows:
        where = row["file"] if row["second"] is None else f"{row['file']} @ {row['second']} s"
        verdict = "FAIL " + ", ".join(row["problems"]) if row["problems"] else "ok"
        print(
            f"{verdict:<40} {where}: luma {row['luma']} ({row['luma_difference']:+}), "
            f"saturation {row['saturation']} ({row['saturation_difference']:+}), hue shift {row['hue_shift_degrees']} deg"
        )
    print(f"{len(rows) - len(failures)} of {len(rows)} frames inside the look band")
    if arguments.json:
        report = {"style": str(arguments.style), "frames": rows}
        arguments.json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
