"""Count and time on-off pulses in one region of a video, frame by frame: blinks, flashes, lights, on-screen hits.

Usage:
  uv run --no-project --with numpy python count_pulses.py <video> --crop x:y:w:h [--from <s>] [--to <s>] [--level 0.5]

Reads the mean brightness of the crop in every frame (no sampling), then counts the rises above a threshold halfway
between the darkest and brightest frame (--level moves it, 0 to 1). Prints each pulse with its start, end and length.
Built for counts faster than frame sheets can show: a dot blinking 3.3 times a second was read as 2 blinks from
2-per-second sheets and as 11, the true count, this way (frame eval, 2026-11-08). A pulse much longer or shorter than
the rest is usually something else crossing the crop (there: the tail of the shot before): narrow --from/--to.
"""

import argparse
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def frame_brightness(video, crop, start, end):
    import numpy
    x, y, width, height = (int(value) for value in crop.split(":"))
    rate_probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=avg_frame_rate",
                                 "-of", "csv=p=0", str(video)], capture_output=True, text=True).stdout.strip()
    numerator, denominator = (rate_probe.split("/") + ["1"])[:2]
    frame_rate = float(numerator) / float(denominator or 1)
    command = ["ffmpeg", "-v", "error", "-ss", str(start)]
    if end is not None:
        command += ["-to", str(end)]
    command += ["-i", str(video), "-vf", f"crop={width}:{height}:{x}:{y},format=gray", "-f", "rawvideo", "-"]
    raw = subprocess.run(command, capture_output=True, check=True).stdout
    frames = numpy.frombuffer(raw, dtype=numpy.uint8).reshape(-1, height * width)
    return frames.mean(axis=1), frame_rate


def find_pulses(values, frame_rate, start, level):
    low, high = float(min(values)), float(max(values))
    if high - low < 8:  # under 8 grey levels of swing there is nothing pulsing
        return [], low + (high - low) * level
    threshold = low + (high - low) * level
    pulses = []
    pulse_start = None
    for index, value in enumerate(values):
        if value > threshold and pulse_start is None:
            pulse_start = index
        elif value <= threshold and pulse_start is not None:
            pulses.append((start + pulse_start / frame_rate, start + index / frame_rate))
            pulse_start = None
    if pulse_start is not None:
        pulses.append((start + pulse_start / frame_rate, start + len(values) / frame_rate))
    return pulses, threshold


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("video")
    parser.add_argument("--crop", required=True, help="x:y:w:h around the thing that pulses, in source pixels")
    parser.add_argument("--from", dest="start", type=float, default=0.0)
    parser.add_argument("--to", dest="end", type=float)
    parser.add_argument("--level", type=float, default=0.5)
    arguments = parser.parse_args()
    values, frame_rate = frame_brightness(arguments.video, arguments.crop, arguments.start, arguments.end)
    pulses, threshold = find_pulses(values, frame_rate, arguments.start, arguments.level)
    print(f"{len(values)} frames at {frame_rate:.2f} fps, brightness {min(values):.0f}-{max(values):.0f}, threshold {threshold:.0f}")
    for number, (pulse_start, pulse_end) in enumerate(pulses, 1):
        print(f"pulse {number}: {pulse_start:.2f}-{pulse_end:.2f} s ({pulse_end - pulse_start:.2f} s)")
    print(f"{len(pulses)} pulses")


if __name__ == "__main__":
    main()
