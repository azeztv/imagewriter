"""Find crossfades and dissolves in a finished video: frames that look like a mix of the shot before and the shot after.

A frame counts as blended when the frames a few steps before and after it are very different (a change of shot) and
the frame itself is close to a weighted mix of the two, with a weight well away from 0 and 1. Hard cuts, in-place
swaps and motion inside a shot do not trigger it. Prints each blended stretch and exits 1 when any is found.

usage: uv run --no-project --with numpy python check_blended_cuts.py <video> [--allow 0] [--step 3]
"""
import argparse
import subprocess
import sys

import numpy

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WIDTH = 96
HEIGHT = 96
SHOT_CHANGE = 0.08       # mean absolute difference (0..1) between the frames on either side
MIX_FIT = 0.12           # residual of the best mix, relative to the shot change
WEIGHT_LOW = 0.15
WEIGHT_HIGH = 0.85
FLAT = 0.05              # standard deviation below which a frame counts as a flat dip or flash
MIN_FRAMES = 2           # a blend shorter than this is motion inside a shot, not a dissolve


def read_frames(video):
    command = ["ffmpeg", "-loglevel", "error", "-i", video, "-vf", f"scale={WIDTH}:{HEIGHT},format=gray",
               "-f", "rawvideo", "-"]
    raw = subprocess.run(command, capture_output=True, check=True).stdout
    frames = numpy.frombuffer(raw, dtype=numpy.uint8).reshape(-1, HEIGHT, WIDTH).astype(numpy.float32) / 255
    return frames


def frame_rate(video):
    command = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate",
               "-of", "csv=p=0", video]
    output = subprocess.run(command, capture_output=True, text=True, check=True).stdout
    numerator, denominator = output.split()[0].strip(",").split("/")
    return float(numerator) / float(denominator)


def blended_frames(frames, step):
    found = []
    for index in range(step, len(frames) - step):
        before = frames[index - step]
        after = frames[index + step]
        change = float(numpy.mean(numpy.abs(after - before)))
        if change < SHOT_CHANGE:
            continue
        # A dip to black or a flash to white fades through a flat frame on purpose; that is not a crossfade.
        if float(numpy.std(before)) < FLAT or float(numpy.std(after)) < FLAT:
            continue
        direction = (after - before).ravel()
        offset = (frames[index] - before).ravel()
        weight = float(numpy.dot(offset, direction) / max(1e-6, numpy.dot(direction, direction)))
        if not WEIGHT_LOW < weight < WEIGHT_HIGH:
            continue
        residual = float(numpy.mean(numpy.abs(offset - weight * direction)))
        if residual < MIX_FIT * change:
            found.append((index, weight))
    return found


def group(found):
    stretches = []
    for index, weight in found:
        if stretches and index - stretches[-1][1] <= 2:
            stretches[-1][1] = index
        else:
            stretches.append([index, index])
    return [stretch for stretch in stretches if stretch[1] - stretch[0] + 1 >= MIN_FRAMES]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("video")
    parser.add_argument("--allow", type=int, default=0, help="number of blended stretches that are allowed")
    parser.add_argument("--step", type=int, default=3, help="frames either side to compare")
    options = parser.parse_args()
    frames = read_frames(options.video)
    rate = frame_rate(options.video)
    stretches = group(blended_frames(frames, options.step))
    for first, last in stretches:
        print(f"blended {first / rate:7.2f}s - {last / rate:7.2f}s ({last - first + 1} frames): crossfade or dissolve")
    print(f"{len(stretches)} blended stretch(es) in {len(frames)} frames")
    sys.exit(1 if len(stretches) > options.allow else 0)


if __name__ == "__main__":
    main()
