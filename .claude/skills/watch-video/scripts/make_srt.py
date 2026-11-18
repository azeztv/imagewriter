"""Build subtitles from words.json, and check a translated copy kept every cue and time.

Usage:
  uv run --no-project python make_srt.py build <words.json> --out <file.srt> [--max-characters 42] [--max-seconds 6]
  uv run --no-project python make_srt.py check <original.srt> <translated.srt>

build: groups words into cues that end at a sentence end, a pause of PAUSE_SECONDS, the character limit or the time
limit, and writes a numbered SRT. Scripts without spaces (Chinese, Japanese, Thai) count characters the same way.
check: after translating only the text lines of a copy, confirms the same cue count, numbers and times, and no empty
or untranslated cue (a cue identical to the original is listed so it can be looked at; names may rightly stay).
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PAUSE_SECONDS = 0.6
SENTENCE_ENDINGS = (".", "?", "!", "。", "？", "！")
TIME_LINE = re.compile(r"^\d\d:\d\d:\d\d,\d{3} --> \d\d:\d\d:\d\d,\d{3}$")


def srt_time(seconds):
    milliseconds = int(round(seconds * 1000))
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    whole_seconds, milliseconds = divmod(milliseconds, 1000)
    return f"{hours:02d}:{minutes:02d}:{whole_seconds:02d},{milliseconds:03d}"


def joined(words):
    text = ""
    for word in words:
        unspaced = len(word["text"]) == 1 and not word["text"].isascii()
        text += word["text"] if unspaced or not text else " " + word["text"]
    return text


def group_into_cues(words, max_characters, max_seconds):
    cues = []
    current = []
    for index, word in enumerate(words):
        current.append(word)
        next_word = words[index + 1] if index + 1 < len(words) else None
        text = joined(current)
        ends_here = (
            next_word is None
            or word["text"].endswith(SENTENCE_ENDINGS)
            or next_word["start"] - word["end"] >= PAUSE_SECONDS
            or len(text) + 1 + len(next_word["text"]) > max_characters
            or next_word["end"] - current[0]["start"] > max_seconds
        )
        if ends_here:
            cues.append((current[0]["start"], max(word["end"], current[0]["start"] + 0.3), text))
            current = []
    return cues


def write_srt(cues, path):
    blocks = [f"{number}\n{srt_time(start)} --> {srt_time(end)}\n{text}" for number, (start, end, text) in enumerate(cues, start=1)]
    path.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")


def read_srt(path):
    cues = []
    for block in re.split(r"\r?\n\s*\r?\n", path.read_text(encoding="utf-8-sig").strip()):
        lines = block.splitlines()
        if len(lines) >= 2:
            cues.append((lines[0].strip(), lines[1].strip(), " ".join(line.strip() for line in lines[2:])))
    return cues


def check(original_path, translated_path):
    original = read_srt(original_path)
    translated = read_srt(translated_path)
    problems = []
    if len(original) != len(translated):
        problems.append(f"cue count {len(translated)} instead of {len(original)}")
    for (number, times, text), (new_number, new_times, new_text) in zip(original, translated):
        if new_number != number or new_times != times or not TIME_LINE.match(new_times):
            problems.append(f"cue {number}: number or time changed ({new_number} {new_times})")
        if not new_text:
            problems.append(f"cue {number}: empty text")
    unchanged = [number for (number, _, text), (_, _, new_text) in zip(original, translated) if text == new_text]
    for problem in problems:
        print(problem)
    if unchanged:
        print(f"{len(unchanged)} cues identical to the original (names may rightly stay): {', '.join(unchanged[:20])}")
    print("ok" if not problems else f"{len(problems)} problems")
    return 0 if not problems else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build")
    build.add_argument("words", type=Path)
    build.add_argument("--out", type=Path, required=True)
    build.add_argument("--max-characters", type=int, default=42)
    build.add_argument("--max-seconds", type=float, default=6.0)
    checker = commands.add_parser("check")
    checker.add_argument("original", type=Path)
    checker.add_argument("translated", type=Path)
    arguments = parser.parse_args()

    if arguments.command == "check":
        sys.exit(check(arguments.original, arguments.translated))
    words = [word for word in json.loads(arguments.words.read_text(encoding="utf-8")) if word["text"].strip()]
    cues = group_into_cues(words, arguments.max_characters, arguments.max_seconds)
    write_srt(cues, arguments.out)
    print(f"{len(cues)} cues -> {arguments.out}")


if __name__ == "__main__":
    main()
