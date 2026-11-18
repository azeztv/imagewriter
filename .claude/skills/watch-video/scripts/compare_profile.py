"""Measure a rebuild against the video by brightness per horizontal band, instead of judging two pictures by eye.

Usage:
  uv run --no-project --with numpy --with pillow python compare_profile.py <video frame> <render>
      [--frame-crop x:y:w:h] [--frame-base <frame without the effect>] [--render-base <render without it>] [--bands 10]

Prints, for each band from top to bottom, the mean brightness (0-255) of the video frame and the render, and their
difference. With the two base images (the same shot before the effect, such as fog hidden), it measures what the
effect adds instead: the lift per band, and how high it reaches (the highest band, counted from the bottom, whose
lift is over a quarter of the strongest band's). For ground fog this reads "video fog reaches 40% up, yours 10%".
Also prints overall mean and contrast (standard deviation): an even wash has low contrast, clumpy fog higher.
The render is resized to the frame crop's size; crop the video frame to its viewport (no UI) with --frame-crop.
"""

import argparse
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REACH_SHARE = 0.25
VISIBLE_LIFT = 12.0  # a band must gain this much brightness (0-255) before the effect counts as visible


def load_grey(path, crop=None, size=None):
    import numpy
    from PIL import Image
    image = Image.open(path).convert("L")
    if crop:
        x, y, width, height = (int(part) for part in crop.split(":"))
        image = image.crop((x, y, x + width, y + height))
    if size:
        image = image.resize(size)
    return numpy.asarray(image, dtype=numpy.float32)


def band_means(grey, bands):
    import numpy
    edges = numpy.linspace(0, grey.shape[0], bands + 1).astype(int)
    return [float(grey[top:bottom].mean()) for top, bottom in zip(edges, edges[1:])]


def reach_from_bottom(lifts):
    """Share of the frame height, from the bottom, that the effect reaches."""
    strongest = max(lifts)
    if strongest < VISIBLE_LIFT:
        return 0.0
    bands = len(lifts)
    highest = None
    for index, lift in enumerate(lifts):
        if lift >= strongest * REACH_SHARE:
            highest = index
            break
    return (bands - highest) / bands


def compare(frame, render, frame_base=None, render_base=None, bands=10):
    report = {"frame_bands": band_means(frame, bands), "render_bands": band_means(render, bands),
              "frame_mean": float(frame.mean()), "render_mean": float(render.mean()),
              "frame_contrast": float(frame.std()), "render_contrast": float(render.std())}
    if frame_base is not None and render_base is not None:
        frame_lift = [max(0.0, value - base) for value, base in zip(report["frame_bands"], band_means(frame_base, bands))]
        render_lift = [max(0.0, value - base) for value, base in zip(report["render_bands"], band_means(render_base, bands))]
        report.update(frame_lift=frame_lift, render_lift=render_lift,
                      frame_reach=reach_from_bottom(frame_lift), render_reach=reach_from_bottom(render_lift))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("frame")
    parser.add_argument("render")
    parser.add_argument("--frame-crop")
    parser.add_argument("--frame-base")
    parser.add_argument("--render-base")
    parser.add_argument("--bands", type=int, default=10)
    arguments = parser.parse_args()

    frame = load_grey(arguments.frame, arguments.frame_crop)
    size = (frame.shape[1], frame.shape[0])
    render = load_grey(arguments.render, size=size)
    frame_base = load_grey(arguments.frame_base, arguments.frame_crop) if arguments.frame_base else None
    render_base = load_grey(arguments.render_base, size=size) if arguments.render_base else None
    report = compare(frame, render, frame_base, render_base, arguments.bands)

    with_lift = "frame_lift" in report
    header = "band (top->bottom)   video  render  diff" + ("   video lift  render lift" if with_lift else "")
    print(header)
    for index in range(arguments.bands):
        row = f"{index + 1:>2}/{arguments.bands:<17} {report['frame_bands'][index]:6.1f}  {report['render_bands'][index]:6.1f}  {report['render_bands'][index] - report['frame_bands'][index]:+5.1f}"
        if with_lift:
            row += f"   {report['frame_lift'][index]:10.1f}  {report['render_lift'][index]:11.1f}"
        print(row)
    print(f"mean      video {report['frame_mean']:.1f}  render {report['render_mean']:.1f}")
    print(f"contrast  video {report['frame_contrast']:.1f}  render {report['render_contrast']:.1f}  (low = even wash)")
    if with_lift:
        def reach_words(reach, lifts):
            if reach == 0.0:
                return f"no visible effect (strongest band +{max(lifts):.0f})"
            return f"{reach:.0%} up, strongest band +{max(lifts):.0f}"
        print(f"effect  video: {reach_words(report['frame_reach'], report['frame_lift'])}")
        print(f"        render: {reach_words(report['render_reach'], report['render_lift'])}")


if __name__ == "__main__":
    main()
