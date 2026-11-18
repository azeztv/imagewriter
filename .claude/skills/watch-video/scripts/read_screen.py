"""Read the text on screen through a video with OCR: values that change, new labels, and names that give away sources.

Usage:
  uv run --no-project --with rapidocr --with onnxruntime-directml --with numpy --with pillow python read_screen.py <video> --out <folder>
      [--every 2] [--from <s>] [--to <s>] [--crop x:y:w:h] [--upscale 1.0] [--tier medium] [--cpu]
  With --recheck-names add: --python 3.12 --with "transformers>=5.17" --with "torch==2.15.0+cu132" --with torchvision
      --with accelerate --index https://download.pytorch.org/whl/cu132 --index-strategy unsafe-best-match

Built for screen recordings (software tutorials): numbers under 2% of frame height that frame sheets cannot show.
A frame goes to OCR only when some block of it changed since the last read frame, so long static stretches cost
nothing, and when only a few blocks changed (a value, the cursor) only that patch is read again. A noisy viewport
(live volumetrics, video playback) changes every frame and defeats the patch reading.

Models (benchmarked 2026-11-07 on Blender and chart frames, RTX 3060): PP-OCRv6 medium (June 2026, Apache-2.0)
through RapidOCR on DirectML reads a full 720p frame in about 1 s with boxes; on the CPU it takes 37 s (small: 2 s),
and onnxruntime-gpu on CUDA took 32 s at the same accuracy (it re-tunes for every image size): keep DirectML.
Small on DirectML is as fast and less exact, so medium is the default.
It swaps letters inside IDs. 2026 OCR VLMs without boxes were slower on full frames and no more exact there
(Xiaomi-OCR-0 9-13 s, GLM-OCR 4-6 s; surya-ocr-2.5 6/14 at 7-30 s, Qianfan-OCR 4/14 in 9.4 GB and indra-ocr 5/14 at 0.9 s on CPU, which drops
underscores and garbles IDs, were worse), but on a crop Xiaomi-OCR-0 read an Unsplash ID exactly where PP-OCRv6 and
GLM-OCR both slipped a letter. So --recheck-names re-reads only the source-name crops with Xiaomi-OCR-0.

Writes:
  value_changes.txt  "00:12  Pos  = 0.000" when a label first shows a number, "02:08  Pos  0.000 -> 0.567" when it
                     changes (label = nearest text left on the same row, or the text before the number on one line)
  first_seen.txt     "03:05  Gradient Texture": every text line the first time it appears (new nodes, menus,
                     objects, chart titles and percentages; bare numbers are left to value_changes.txt)
  sources.md         names that point at where assets came from (CGTrader, Unsplash, Poly Haven, Sketchfab, .blend paths)
  screen.jsonl       every read frame: time, text lines with boxes and scores, frame/source size and crop
  crops/             the line crop each source name was read from
OCR misreads letters (Beech -> Beect, l -> i): check a value you rely on in one full-size frame or crop.
"""

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MINIMUM_SCORE = 0.6
CHANGE_GRID = (32, 18)  # blocks across and down for the change check
CHANGE_LEVEL = 6.0  # mean grey difference inside one block that counts as a change
FULL_READ_SHARE = 0.25  # above this share of changed blocks the whole frame is read again, below it only the patch
SAME_NAME = 0.75  # readings at least this similar are one on-screen name
CROPS_PER_NAME = 4  # moments per name whose crops go to the second reader
VLM_WEIGHT = 2  # one Xiaomi-OCR-0 reading counts as two PP-OCRv6 readings in the vote
NUMBER = re.compile(r"^[-+]?\d+(?:[.,]\d+)?\s*(?:m|cm|mm|°|px|%|x)?$")
LABEL_AND_NUMBER = re.compile(r"^(?P<label>[A-Za-z][A-Za-z0-9 _./:-]*?)\s*:?\s+(?P<value>[-+]?\d+(?:[.,]\d+)?)\s*(?:m|cm|mm|°|px|%)?$")
SOURCE_PATTERNS = [
    (re.compile(r"uploads_f\w*_\d+_[\w.-]+", re.IGNORECASE), "CGTrader download (uploads_files_<item id>_<name>)"),
    (re.compile(r"[\w-]+-[A-Za-z0-9_&-]{11}-unsplash", re.IGNORECASE), "Unsplash photo (<photographer>-<photo id>-unsplash)"),
    (re.compile(r"[\w-]+_\d+k(?:\s*\(\d+\))?\.(?:hdr|exr)", re.IGNORECASE), "HDRI, Poly Haven naming (<name>_<res>k.hdr)"),
    (re.compile(r"[\w-]+_(?:diff|nor_gl|rough|disp|arm|ao)_\d+k\.\w+", re.IGNORECASE), "Poly Haven texture map"),
    (re.compile(r"sketchfab|polyhaven|poly haven|ambientcg|quixel|megascans|blenderkit|botaniq|graswald|kitbash", re.IGNORECASE), "asset site or add-on name"),
    (re.compile(r"[A-Za-z]:\\[^\s]*\.blend|[\w -]+\.blend\b", re.IGNORECASE), ".blend file name"),
]


def timestamp(seconds):
    whole = int(seconds)
    return f"{whole // 60:02d}:{whole % 60:02d}"


def box_bounds(points):
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    return min(xs), min(ys), max(xs), max(ys)


def clean_number(text):
    match = re.match(r"[-+]?\d+(?:[.,]\d+)?", text.strip())
    return match.group(0).replace(",", ".") if match else None


def same_digits(old_value, new_value):
    """OCR drops decimal points ("1.320" read as "1320"): equal digits are not a change."""
    return old_value.replace(".", "").lstrip("0") == new_value.replace(".", "").lstrip("0")


def pair_fields(lines, frame_width):
    """Label -> value for one frame. A number takes the nearest label ending left of it on the same row."""
    fields = {}
    labels = [line for line in lines if not NUMBER.match(line["text"].strip())]
    for line in lines:
        text = line["text"].strip()
        joined = LABEL_AND_NUMBER.match(text)
        if joined:
            fields[joined.group("label").strip()] = joined.group("value").replace(",", ".")
            continue
        if not NUMBER.match(text):
            continue
        row_middle = (line["y0"] + line["y1"]) / 2
        height = max(line["y1"] - line["y0"], 1)
        best_label, best_gap = None, frame_width * 0.3
        for label in labels:
            label_middle = (label["y0"] + label["y1"]) / 2
            gap = line["x0"] - label["x1"]
            if abs(label_middle - row_middle) <= height * 0.6 and -height <= gap < best_gap:
                best_label, best_gap = label, gap
        if best_label is not None:
            fields[best_label["text"].strip().rstrip(":")] = clean_number(text)
    return fields


def changed_mask(previous, current):
    """Rows x columns booleans: which blocks of a small grey frame differ by more than CHANGE_LEVEL."""
    import numpy
    columns, rows = CHANGE_GRID
    if previous is None:
        return numpy.ones((rows, columns), dtype=bool)
    height, width = current.shape
    block_height, block_width = height // rows, width // columns
    difference = numpy.abs(current.astype(numpy.int16) - previous.astype(numpy.int16))
    trimmed = difference[: block_height * rows, : block_width * columns]
    means = trimmed.reshape(rows, block_height, columns, block_width).mean(axis=(1, 3))
    return means > CHANGE_LEVEL


def changed_blocks(previous, current):
    return int(changed_mask(previous, current).sum())


def changed_region(mask, image_width, image_height, padding=40):
    """Pixel box (x0, y0, x1, y1) around the changed blocks, padded so a whole label and value fit."""
    import numpy
    rows, columns = mask.shape
    changed_rows, changed_columns = numpy.nonzero(mask)
    block_width, block_height = image_width / columns, image_height / rows
    x0 = max(0, int(changed_columns.min() * block_width) - padding)
    y0 = max(0, int(changed_rows.min() * block_height) - padding)
    x1 = min(image_width, int((changed_columns.max() + 1) * block_width) + padding)
    y1 = min(image_height, int((changed_rows.max() + 1) * block_height) + padding)
    return x0, y0, x1, y1


def overlaps(line, region):
    x0, y0, x1, y1 = region
    return not (line["x1"] < x0 or line["x0"] > x1 or line["y1"] < y0 or line["y0"] > y1)


def find_sources(text):
    found = []
    for pattern, meaning in SOURCE_PATTERNS:
        for match in pattern.finditer(text):
            found.append((match.group(0).strip(), meaning))
    return found


def make_engine(tier, cpu_only):
    """PP-OCRv6 (June 2026) through RapidOCR, on the GPU through DirectML unless --cpu."""
    from rapidocr import RapidOCR
    from rapidocr.utils.typings import ModelType, OCRVersion
    model_type = {"tiny": ModelType.TINY, "small": ModelType.SMALL, "medium": ModelType.MEDIUM}[tier]
    return RapidOCR(params={
        "Global.use_cls": False,
        "Global.log_level": "error",
        "Det.ocr_version": OCRVersion.PPOCRV6,
        "Det.model_type": model_type,
        "Rec.ocr_version": OCRVersion.PPOCRV6,
        "Rec.model_type": model_type,
        "EngineConfig.onnxruntime.use_dml": not cpu_only,
    })


def similarity(first, second):
    from difflib import SequenceMatcher
    return SequenceMatcher(None, first.lower(), second.lower()).ratio()


def find_cluster(clusters, name, meaning):
    """The cluster holding other readings of the same on-screen name (OCR slips change a few letters)."""
    for cluster in clusters:
        if cluster["meaning"] == meaning and similarity(cluster["readings"][0][0], name) >= SAME_NAME:
            return cluster
    cluster = {"meaning": meaning, "first": None, "readings": [], "crops": []}
    clusters.append(cluster)
    return cluster


def vote_name(readings):
    """Per-letter majority over weighted readings, aligned on the reading closest to all others.

    One reading of a 720p UI line is right about half the time at best (hlc vs hk is a few pixels); letters that
    each reader gets right in most frames still win the vote. Replacements of unequal length are not voted on.
    """
    from difflib import SequenceMatcher
    texts = [text for text, weight in readings]
    base = max(texts, key=lambda text: sum(similarity(text, other) for other in texts))
    # Upper and lower case of one letter vote together (OCR flips I/i beside an icon), then the commoner case is kept.
    tallies = [{} for _ in base]
    cases = [{} for _ in base]
    for text, weight in readings:
        for tag, base_start, base_end, start, end in SequenceMatcher(None, base.lower(), text.lower(), autojunk=False).get_opcodes():
            if tag == "equal" or (tag == "replace" and base_end - base_start == end - start):
                for offset in range(base_end - base_start):
                    letter = text[start + offset]
                    position = base_start + offset
                    tallies[position][letter.lower()] = tallies[position].get(letter.lower(), 0) + weight
                    cases[position][letter] = cases[position].get(letter, 0) + weight
    voted_letters = []
    for tally, case_tally, letter in zip(tallies, cases, base):
        if not tally:
            voted_letters.append(letter)
            continue
        winner = max(tally, key=tally.get)
        spellings = {spelling: votes for spelling, votes in case_tally.items() if spelling.lower() == winner}
        voted_letters.append(max(spellings, key=spellings.get))
    voted = "".join(voted_letters)
    agreeing = sum(weight for text, weight in readings if text == voted)
    return voted, agreeing


def save_line_crops(image, line, folder, stem):
    """Two crops of one name line, both 2x: tight (one line height around it) and wide (neighbouring rows)."""
    height = line["y1"] - line["y0"]
    paths = []
    for kind, across, down in (("tight", 1, 1), ("wide", 4, 3)):
        box = (max(0, int(line["x0"] - across * height)), max(0, int(line["y0"] - down * height)),
               min(image.width, int(line["x1"] + across * height)), min(image.height, int(line["y1"] + down * height)))
        crop = image.convert("RGB").crop(box)
        path = folder / f"{stem}_{kind}.png"
        crop.resize((crop.width * 2, crop.height * 2)).save(path)
        paths.append(path)
    return paths


def recheck_names(clusters):
    """Add Xiaomi-OCR-0 readings of every saved crop to each cluster, weighted above PP-OCRv6 readings.

    On these crops PP-OCRv6 repeats the same slip in every frame (sdhlc -> sdhic) while Xiaomi-OCR-0's slips vary
    and it reads more letters right (measured 2026-11-07). Needs CUDA torch and transformers (module docstring).
    """
    import torch
    from PIL import Image
    from transformers import AutoModelForImageTextToText, AutoProcessor
    model_id = "xiaomi-research/Xiaomi-OCR-0"
    processor = AutoProcessor.from_pretrained(model_id)
    model = AutoModelForImageTextToText.from_pretrained(model_id, dtype=torch.float16).to("cuda").eval()
    for cluster in clusters:
        anchor = cluster["readings"][0][0]
        for path in cluster["crops"]:
            messages = [{"role": "user", "content": [{"type": "image", "image": Image.open(path).convert("RGB")},
                                                     {"type": "text", "text": "Extract the text in the image."}]}]
            inputs = processor.apply_chat_template(messages, tokenize=True, add_generation_prompt=True,
                                                   return_dict=True, return_tensors="pt").to("cuda")
            with torch.inference_mode():
                output = model.generate(**inputs, max_new_tokens=256, do_sample=False)
            text = processor.batch_decode(output[:, inputs["input_ids"].shape[1]:], skip_special_tokens=True)[0]
            matches = [found for found, meaning in find_sources(text) if meaning == cluster["meaning"]]
            if matches:
                best = max(matches, key=lambda found: similarity(found, anchor))
                if similarity(best, anchor) >= SAME_NAME:
                    cluster["readings"].append((best, VLM_WEIGHT))


def video_size(video):
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                            "-of", "csv=p=0", str(video)], capture_output=True, text=True, check=True)
    width, height = probe.stdout.strip().split(",")[:2]
    return [int(width), int(height)]


def extract_frames(video, folder, every, start, end, crop, upscale):
    filters = [f"fps=1/{every}"]
    if crop:
        x, y, width, height = crop.split(":")
        filters.append(f"crop={width}:{height}:{x}:{y}")
    if upscale != 1.0:
        filters.append(f"scale=iw*{upscale}:-2:flags=lanczos")
    command = ["ffmpeg", "-v", "error", "-y", "-ss", str(start)]
    if end is not None:
        command += ["-to", str(end)]
    command += ["-i", str(video), "-vf", ",".join(filters), str(folder / "frame_%05d.png")]
    subprocess.run(command, check=True)
    return sorted(folder.glob("frame_*.png"))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("video")
    parser.add_argument("--out", required=True)
    parser.add_argument("--every", type=float, default=2.0, help="seconds between sampled frames")
    parser.add_argument("--from", dest="start", type=float, default=0.0)
    parser.add_argument("--to", dest="end", type=float, default=None)
    parser.add_argument("--crop", help="x:y:w:h of the panel to read, in source pixels")
    parser.add_argument("--upscale", type=float, default=1.0, help="enlarge before OCR; on 720p Blender frames 1.5-3x doubled the time and fixed none of PP-OCRv6's slips")
    parser.add_argument("--tier", choices=["tiny", "small", "medium"], default="medium", help="PP-OCRv6 model size")
    parser.add_argument("--cpu", action="store_true", help="no GPU; medium then takes about 37 s a frame, so pass --tier small")
    parser.add_argument("--recheck-names", action="store_true", help="re-read source-name crops with Xiaomi-OCR-0 on CUDA")
    arguments = parser.parse_args()

    import numpy
    from PIL import Image

    out_folder = Path(arguments.out)
    out_folder.mkdir(parents=True, exist_ok=True)
    crop_folder = out_folder / "crops"
    crop_folder.mkdir(exist_ok=True)
    engine = make_engine(arguments.tier, arguments.cpu)
    # Saved with every frame so annotate.py can map the boxes onto any copy of the video.
    source_size = video_size(arguments.video)
    crop_box = [float(part) for part in arguments.crop.split(":")] if arguments.crop else None
    last_values = {}
    seen_text = set()
    changes, first_seen, clusters = [], [], []
    previous_small = None
    screen_lines = []
    read_count = 0
    with tempfile.TemporaryDirectory() as temporary, open(out_folder / "screen.jsonl", "w", encoding="utf-8") as screen_log:
        frames = extract_frames(arguments.video, Path(temporary), arguments.every, arguments.start, arguments.end,
                                arguments.crop, arguments.upscale)
        for index, frame_path in enumerate(frames):
            seconds = arguments.start + index * arguments.every
            image = Image.open(frame_path)
            small = numpy.asarray(image.convert("L").resize((640, 360)))
            mask = changed_mask(previous_small, small)
            if not mask.any():
                continue
            previous_small = small
            read_count += 1
            if mask.mean() > FULL_READ_SHARE:
                region = (0, 0, image.width, image.height)
                kept = []
            else:
                # Only a few blocks changed (a value, a cursor): read that patch and keep the rest of the screen.
                region = changed_region(mask, image.width, image.height)
                kept = [line for line in screen_lines if not overlaps(line, region)]
            patch = numpy.asarray(image.convert("RGB").crop(region))
            result = engine(patch)
            fresh = []
            for points, text, score in zip(result.boxes if result.boxes is not None else [], result.txts or [], result.scores or []):
                if float(score) < MINIMUM_SCORE:
                    continue
                x0, y0, x1, y1 = box_bounds(points)
                fresh.append({"text": text, "x0": float(x0) + region[0], "y0": float(y0) + region[1],
                              "x1": float(x1) + region[0], "y1": float(y1) + region[1], "score": round(float(score), 3)})
            screen_lines = kept + fresh
            lines = screen_lines
            record = {"seconds": seconds, "lines": lines, "frame": [image.width, image.height],
                      "source": source_size, "crop": crop_box}
            screen_log.write(json.dumps(record, ensure_ascii=False) + "\n")
            for label, value in pair_fields(lines, image.width).items():
                if value is None:
                    continue
                if label not in last_values:
                    changes.append(f"{timestamp(seconds)}  {label}  = {value}")
                elif not same_digits(last_values[label], value):
                    changes.append(f"{timestamp(seconds)}  {label}  {last_values[label]} -> {value}")
                last_values[label] = value
            for line in lines:
                text = line["text"].strip()
                # Bare numbers flood the list (every UI field), but a percentage is usually a chart or a result.
                worth_listing = not NUMBER.match(text) or "%" in text
                if len(text) >= 3 and worth_listing and text not in seen_text:
                    seen_text.add(text)
                    first_seen.append(f"{timestamp(seconds)}  {text}")
                if line not in fresh:
                    continue  # a line kept from an earlier frame is the same reading again, not a new vote
                for name, meaning in find_sources(text):
                    cluster = find_cluster(clusters, name, meaning)
                    cluster["readings"].append((name, 1))
                    if cluster["first"] is None:
                        cluster["first"] = seconds
                    if len(cluster["crops"]) < 2 * CROPS_PER_NAME:
                        stem = f"name{clusters.index(cluster):02d}_{int(seconds):05d}"
                        cluster["crops"] += save_line_crops(image, line, crop_folder, stem)
            print(f"\r{timestamp(seconds)} read {read_count} of {index + 1} sampled frames", end="", flush=True)
    print()

    (out_folder / "value_changes.txt").write_text("\n".join(changes) + "\n", encoding="utf-8")
    (out_folder / "first_seen.txt").write_text("\n".join(first_seen) + "\n", encoding="utf-8")
    if arguments.recheck_names and clusters:
        print(f"re-reading {sum(len(cluster['crops']) for cluster in clusters)} name crops with Xiaomi-OCR-0")
        recheck_names(clusters)
    source_lines = ["# Names on screen that point at sources", "",
                    "Voted per letter over every reading. Fewer than half agreeing: open the crops before searching for it.", ""]
    for index, cluster in enumerate(clusters):
        voted, agreeing = vote_name(cluster["readings"])
        total = sum(weight for text, weight in cluster["readings"])
        source_lines.append(f"- `{voted}` | {cluster['meaning']} | first at {timestamp(cluster['first'])} | "
                            f"{agreeing}/{total} readings agree | crops/name{index:02d}_*")
    (out_folder / "sources.md").write_text("\n".join(source_lines) + "\n", encoding="utf-8")
    print(f"{read_count} frames read, {len(changes)} value changes, {len(first_seen)} new lines, {len(clusters)} source names -> {out_folder}")


if __name__ == "__main__":
    main()
