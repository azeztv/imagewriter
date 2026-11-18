"""Draw a numbered build list on reference frames: boxes on the frame, one legend line per box below it.

Usage: uv run --no-project --with pillow python build_list.py <notes.json> <out_folder> [--frames <folder>]

notes.json:
{
  "frames": {
    "clip_3.14.png": [
      {"box": [0.10, 0.52, 0.45, 0.95], "category": "DEBRIS", "text": "Collapsed timber roof, planks in parallel"}
    ]
  }
}
A box is left, top, right, bottom as 0-1 fractions of the frame. Frame names resolve against --frames, else against
the folder of notes.json. Categories are free words; each gets its own colour, the same in every frame.
"""
import json
import os
import sys
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PALETTE = [
    (255, 190, 60), (255, 110, 90), (250, 240, 120), (190, 190, 200), (255, 255, 255), (80, 240, 255),
    (150, 255, 140), (255, 140, 230), (140, 170, 255), (255, 160, 60),
]
FONT_CANDIDATES_BOLD = ["C:/Windows/Fonts/arialbd.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
FONT_CANDIDATES_REGULAR = ["C:/Windows/Fonts/arial.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf",
                           "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
REFERENCE_WIDTH = 1280.0


def load_font(candidates, size):
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def wrap_text(draw, text, font, max_width):
    lines = []
    current = ""
    for word in text.split():
        trial = (current + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def annotate(frame_path, items, colors, output_path):
    frame = Image.open(frame_path).convert("RGB")
    width, height = frame.size
    scale = width / REFERENCE_WIDTH
    label_font = load_font(FONT_CANDIDATES_BOLD, max(12, int(22 * scale)))
    legend_font = load_font(FONT_CANDIDATES_REGULAR, max(12, int(21 * scale)))
    line_height = int(30 * scale)
    margin = int(14 * scale)
    swatch = int(20 * scale)
    text_left = margin + swatch + int(10 * scale)
    probe = ImageDraw.Draw(frame)
    legend_lines = []
    for index, item in enumerate(items, start=1):
        text = f"{index}. [{item['category']}] {item['text']}"
        wrapped = wrap_text(probe, text, legend_font, width - text_left - margin)
        legend_lines.append((item["category"], wrapped))
    legend_rows = sum(len(wrapped) for _, wrapped in legend_lines)
    sheet = Image.new("RGB", (width, height + line_height * legend_rows + 2 * margin), (18, 18, 20))
    sheet.paste(frame, (0, 0))
    draw = ImageDraw.Draw(sheet)
    outline = max(2, int(3 * scale))
    for index, item in enumerate(items, start=1):
        color = colors[item["category"]]
        left, top, right, bottom = item["box"]
        left, top, right, bottom = left * width, top * height, right * width, bottom * height
        draw.rectangle([left, top, right, bottom], outline=color, width=outline)
        tag = str(index)
        tag_width = int((16 + 13 * len(tag)) * scale)
        draw.rectangle([left, top, left + tag_width, top + int(28 * scale)], fill=color)
        draw.text((left + int(7 * scale), top + int(2 * scale)), tag, fill=(0, 0, 0), font=label_font)
    row_top = height + margin
    for category, wrapped in legend_lines:
        draw.rectangle([margin, row_top + int(4 * scale), margin + swatch, row_top + int(4 * scale) + swatch],
                       fill=colors[category])
        for line in wrapped:
            draw.text((text_left, row_top), line, fill=(235, 235, 235), font=legend_font)
            row_top += line_height
    sheet.save(output_path, quality=88)


def main():
    arguments = sys.argv[1:]
    frames_folder = None
    if "--frames" in arguments:
        position = arguments.index("--frames")
        frames_folder = arguments[position + 1]
        del arguments[position:position + 2]
    notes_path, output_folder = arguments[0], arguments[1]
    if frames_folder is None:
        frames_folder = os.path.dirname(os.path.abspath(notes_path))
    with open(notes_path, encoding="utf-8") as handle:
        notes = json.load(handle)
    os.makedirs(output_folder, exist_ok=True)
    colors = {}
    for items in notes["frames"].values():
        for item in items:
            if item["category"] not in colors:
                colors[item["category"]] = PALETTE[len(colors) % len(PALETTE)]
    for name, items in notes["frames"].items():
        stem = os.path.splitext(os.path.basename(name))[0]
        output_path = os.path.join(output_folder, stem + "_build_list.jpg")
        annotate(os.path.join(frames_folder, name), items, colors, output_path)
        print("BUILD_LIST", output_path, len(items), "items")


if __name__ == "__main__":
    main()
