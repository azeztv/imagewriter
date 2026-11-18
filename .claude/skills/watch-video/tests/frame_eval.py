"""Known-answer eval for reading video frames: how small can text be, can counts, motion, UI state, brief shots and
cut times be read from perceive.py sheets and from full-size frames.

Usage:
  uv run --no-project --with pillow python frame_eval.py make <folder> [--seed 7]
      writes <folder>/eval.mp4, questions.md (give to the reader) and answers.json (keep from the reader)
  uv run --no-project python frame_eval.py score <folder> <responses.json>
      responses.json maps each question id to the reader's answer; prints a score per question kind

Every run with a new seed draws new codes and counts, so a reader cannot remember answers.
"""

import argparse
import json
import random
import subprocess
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # only `make` draws; `score` runs without Pillow
    Image = ImageDraw = ImageFont = None

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WIDTH = 1920
HEIGHT = 1080
FRAME_RATE = 30
SHOT_SECONDS = 3.0
TEXT_SIZES = [14, 20, 28, 40, 56, 80]
# No look-alike characters (0/O, 1/I/L, 5/S, 8/B, 2/Z), so a wrong read is a reading failure, not a font quirk.
CODE_ALPHABET = "ACDEFGHJKMNPQRTUVWXY34679"
BACKGROUND = (24, 26, 30)
FOREGROUND = (235, 235, 235)


def font(size):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        raise SystemExit("Pillow 10.1 or newer is needed for sized default fonts")


def blank(color=BACKGROUND):
    return Image.new("RGB", (WIDTH, HEIGHT), color)


def text_shot(random_source):
    image = blank()
    draw = ImageDraw.Draw(image)
    codes = {}
    top = 80
    for size in TEXT_SIZES:
        code = "".join(random_source.choice(CODE_ALPHABET) for _ in range(5))
        draw.text((120, top), code, font=font(size), fill=FOREGROUND)
        left, upper, right, lower = draw.textbbox((120, top), code, font=font(size))
        codes[size] = {"code": code, "cap_height": lower - upper}
        top += size + 70
    return image, codes


def count_shot(random_source):
    image = blank()
    draw = ImageDraw.Draw(image)
    count = random_source.randint(9, 17)
    placed = []
    while len(placed) < count:
        radius = random_source.randint(28, 60)
        x = random_source.randint(radius + 40, WIDTH - radius - 40)
        y = random_source.randint(radius + 40, HEIGHT - radius - 40)
        if all((x - other_x) ** 2 + (y - other_y) ** 2 > (radius + other_radius + 30) ** 2 for other_x, other_y, other_radius in placed):
            placed.append((x, y, radius))
            colour = random_source.choice([(220, 80, 70), (80, 160, 230), (240, 200, 70), (110, 200, 120)])
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=colour)
    return image, count


def ui_shot(random_source):
    image = blank((245, 246, 248))
    draw = ImageDraw.Draw(image)
    labels = ["Autosave", "Dark mode", "Sync photos", "Beta updates", "Location"]
    checked = [label for label in labels if random_source.random() < 0.5] or [labels[0]]
    for index, label in enumerate(labels):
        top = 160 + index * 110
        draw.rounded_rectangle((200, top, 248, top + 48), radius=8, outline=(60, 60, 70), width=4,
                               fill=(40, 110, 230) if label in checked else (255, 255, 255))
        if label in checked:
            draw.line((210, top + 26, 222, top + 38, 240, top + 12), fill=(255, 255, 255), width=6)
        draw.text((280, top + 4), label, font=font(36), fill=(30, 30, 35))
    percent = random_source.randint(12, 88)
    draw.rounded_rectangle((900, 300, 1700, 350), radius=25, fill=(220, 222, 228))
    draw.rounded_rectangle((900, 300, 900 + 8 * percent, 350), radius=25, fill=(40, 110, 230))
    return image, {"checked": sorted(checked), "progress_percent": percent}


def write_video(frames, path):
    command = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{WIDTH}x{HEIGHT}",
               "-r", str(FRAME_RATE), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", str(path)]
    encoder = subprocess.Popen(command, stdin=subprocess.PIPE)
    for image in frames:
        encoder.stdin.write(image.tobytes())
    encoder.stdin.close()
    encoder.wait()


def make(folder, seed):
    random_source = random.Random(seed)
    folder.mkdir(parents=True, exist_ok=True)
    shot_frames = int(SHOT_SECONDS * FRAME_RATE)
    frames = []
    cuts = []

    def hold(image, count):
        if frames:
            cuts.append(round(len(frames) / FRAME_RATE, 2))
        frames.extend([image] * count)

    text_image, codes = text_shot(random_source)
    hold(text_image, shot_frames)
    count_image, count = count_shot(random_source)
    hold(count_image, shot_frames)

    direction = random_source.choice(["left", "right", "up", "down"])
    cuts.append(round(len(frames) / FRAME_RATE, 2))
    for index in range(shot_frames):
        progress = index / (shot_frames - 1)
        image = blank()
        draw = ImageDraw.Draw(image)
        along = {"right": progress, "left": 1 - progress, "down": progress, "up": 1 - progress}[direction]
        if direction in ("left", "right"):
            x, y = 200 + along * (WIDTH - 400), HEIGHT / 2
        else:
            x, y = WIDTH / 2, 150 + along * (HEIGHT - 300)
        draw.rectangle((x - 70, y - 70, x + 70, y + 70), fill=(240, 200, 70))
        frames.append(image)

    flash_word = random_source.choice(["ORBIT", "MAPLE", "CRANE", "VELVET", "HARBOR"])
    flash = blank((200, 40, 40))
    ImageDraw.Draw(flash).text((WIDTH / 2, HEIGHT / 2), flash_word, font=font(140), fill=(255, 255, 255), anchor="mm")
    flash_start = round(len(frames) / FRAME_RATE, 2)
    hold(flash, int(0.3 * FRAME_RATE))

    ui_image, ui_state = ui_shot(random_source)
    hold(ui_image, shot_frames)

    counter_start = round(len(frames) / FRAME_RATE, 2)
    cuts.append(counter_start)
    first_number = random_source.randint(10, 60)
    for index in range(shot_frames):
        image = blank()
        number = first_number + index * 2 // FRAME_RATE  # changes every half second
        ImageDraw.Draw(image).text((WIDTH / 2, HEIGHT / 2), str(number), font=font(300), fill=FOREGROUND, anchor="mm")
        frames.append(image)
    ask_at = round(counter_start + random_source.choice([0.75, 1.25, 1.75, 2.25]), 2)
    number_at = first_number + int((ask_at - counter_start) * 2)

    # Time claims, where video readers fail most: order of brief events, a count faster than 2 frames per second,
    # and which event lasted longest. Sheets at 2 per second alias these; an 8 fps zoom resolves them.
    colours = {"red": (220, 60, 60), "blue": (60, 120, 230), "green": (70, 190, 90), "yellow": (240, 200, 60),
               "purple": (150, 80, 200), "orange": (240, 140, 40)}
    order = random_source.sample(sorted(colours), 5)
    durations = random_source.sample([0.2, 0.3, 0.4, 0.5, 0.8], 5)
    blocks_start = round(len(frames) / FRAME_RATE, 2)
    for colour_name, seconds in zip(order, durations):
        block = blank()
        ImageDraw.Draw(block).rectangle((WIDTH / 2 - 220, HEIGHT / 2 - 220, WIDTH / 2 + 220, HEIGHT / 2 + 220), fill=colours[colour_name])
        frames.extend([block] * int(seconds * FRAME_RATE))
        frames.extend([blank()] * int(0.2 * FRAME_RATE))
    longest = order[durations.index(max(durations))]
    blink_count = random_source.randint(7, 13)
    dot_on = blank()
    ImageDraw.Draw(dot_on).ellipse((WIDTH / 2 - 60, HEIGHT / 2 - 60, WIDTH / 2 + 60, HEIGHT / 2 + 60), fill=FOREGROUND)
    blink_frames = int(0.15 * FRAME_RATE)
    frames.extend([blank()] * int(0.5 * FRAME_RATE))
    for _ in range(blink_count):
        frames.extend([dot_on] * blink_frames)
        frames.extend([blank()] * blink_frames)
    frames.extend([blank()] * int(0.5 * FRAME_RATE))

    write_video(frames, folder / "eval.mp4")
    answers = {
        **{f"text_{size}": codes[size]["code"] for size in TEXT_SIZES},
        "circle_count": count,
        "motion_direction": direction,
        "flash_word": flash_word,
        "flash_start": flash_start,
        "checked_boxes": ui_state["checked"],
        "progress_percent": ui_state["progress_percent"],
        "number_at_time": number_at,
        "cut_times": cuts,
        "block_order": order,
        "longest_block": longest,
        "blink_count": blink_count,
    }
    meta = {"cap_heights": {size: codes[size]["cap_height"] for size in TEXT_SIZES}, "ask_at": ask_at, "seed": seed}
    (folder / "answers.json").write_text(json.dumps({"answers": answers, "meta": meta}, indent=1), encoding="utf-8")
    questions = [
        "Answer from what you see only; write `unreadable` instead of guessing. Return JSON with these keys:",
        f"- text_14, text_20, text_28, text_40, text_56, text_80: the first shot shows six 5-letter codes, smallest at the top; give each code (top to bottom = 14 .. 80)",
        "- circle_count: how many circles the second shot shows",
        "- motion_direction: which way the yellow square moves (left, right, up, down)",
        "- flash_word: the word on a very brief red shot, if there is one; flash_start: its start time in seconds",
        "- checked_boxes: the labels of the ticked checkboxes; progress_percent: how full the blue bar is, in percent",
        f"- number_at_time: the big number on screen at {ask_at} s",
        f"- cut_times: every cut before {blocks_start} s, in seconds",
        "- block_order: the colours of the big square blocks in the order they appear (red, blue, green, yellow, purple, orange)",
        "- longest_block: the colour of the block that stays on screen longest",
        "- blink_count: how many times the white dot after the blocks lights up",
    ]
    (folder / "questions.md").write_text("\n".join(questions) + "\n", encoding="utf-8")
    print(f"{len(frames) / FRAME_RATE:.1f} s video, {len(answers)} answers -> {folder}")


def score(folder, responses_path):
    key = json.loads((folder / "answers.json").read_text(encoding="utf-8"))
    answers = key["answers"]
    responses = json.loads(Path(responses_path).read_text(encoding="utf-8"))
    results = {}
    for name, truth in answers.items():
        given = responses.get(name)
        if name == "cut_times":
            given_times = [float(value) for value in (given or [])]
            matched = sum(1 for cut in truth if any(abs(cut - value) <= 0.25 for value in given_times))
            extra = sum(1 for value in given_times if all(abs(cut - value) > 0.25 for cut in truth))
            results[name] = (matched == len(truth) and extra == 0, f"{matched}/{len(truth)} found, {extra} extra")
        elif name == "progress_percent":
            results[name] = (given is not None and abs(float(given) - truth) <= 5, f"{given} vs {truth} (±5)")
        elif name == "flash_start":
            results[name] = (given is not None and abs(float(given) - truth) <= 0.25, f"{given} vs {truth} (±0.25 s)")
        elif name == "block_order":
            given_order = [str(colour).strip().lower() for colour in (given or [])]
            results[name] = (given_order == truth, f"{given_order} vs {truth}")
        elif name == "checked_boxes":
            results[name] = (sorted(given or []) == truth, f"{given} vs {truth}")
        else:
            results[name] = (str(given).strip().upper() == str(truth).upper(), f"{given} vs {truth}")
    for name, (correct, detail) in results.items():
        cap = key["meta"]["cap_heights"].get(name.removeprefix("text_")) if name.startswith("text_") else None
        cap_note = f" (cap height {cap} px at 1080p)" if cap else ""
        print(f"{'ok  ' if correct else 'MISS'} {name}{cap_note}: {detail}")
    print(f"{sum(correct for correct, _ in results.values())}/{len(results)} correct")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    maker = commands.add_parser("make")
    maker.add_argument("folder", type=Path)
    maker.add_argument("--seed", type=int, default=7)
    scorer = commands.add_parser("score")
    scorer.add_argument("folder", type=Path)
    scorer.add_argument("responses", type=Path)
    arguments = parser.parse_args()
    if arguments.command == "make":
        make(arguments.folder, arguments.seed)
    else:
        score(arguments.folder, arguments.responses)


if __name__ == "__main__":
    main()
