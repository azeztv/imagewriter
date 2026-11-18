"""Turn a VTT caption file into the same transcript.txt and words.json that transcribe.py writes, rolling repeats removed.

YouTube auto captions carry each word's start time inline, and those are kept. Captions without them (most uploaded
ones) get word times spread evenly across each caption, rougher than a speech model's.

Usage: uv run --no-project python captions.py <captions.vtt> [--out DIR]
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TIMING_LINE = re.compile(r"(\d+):(\d\d):(\d\d)\.(\d+)\s*-->\s*(\d+):(\d\d):(\d\d)\.(\d+)")
SHORT_TIMING_LINE = re.compile(r"(\d+):(\d\d)\.(\d+)\s*-->\s*(\d+):(\d\d)\.(\d+)")
TAG = re.compile(r"<[^>]+>")
INLINE_TIME = re.compile(r"<(\d+:\d\d:\d\d\.\d+)>")
INLINE_TIME_PARTS = re.compile(r"(\d+):(\d\d):(\d\d)\.(\d+)")
SOUND_TAG = re.compile(r"\[[^\]]*\]")
RECENT_LINES_CHECKED = 3
LONGEST_WORD_SECONDS = 1.0


def seconds_from(hours, minutes, seconds, fraction):
    return int(hours) * 3600 + int(minutes) * 60 + int(seconds) + float(f"0.{fraction}")


def parse_timing(line):
    full = TIMING_LINE.search(line)
    if full:
        parts = full.groups()
        return seconds_from(*parts[:4]), seconds_from(*parts[4:])
    short = SHORT_TIMING_LINE.search(line)
    if short:
        parts = short.groups()
        return seconds_from(0, *parts[:3]), seconds_from(0, *parts[3:])
    return None


def read_cues(text):
    """Each cue as (start, end, [(clean line, raw line)]); the raw line keeps YouTube's inline word times."""
    cues = []
    # Only a truly empty line ends a cue: YouTube auto captions put a line holding one space inside each cue, between
    # the timing and the words with inline times.
    for block in re.split(r"\r?\n\r?\n", text):
        lines = block.splitlines()
        timing_index = next((index for index, line in enumerate(lines) if parse_timing(line)), None)
        if timing_index is None:
            continue
        start, end = parse_timing(lines[timing_index])
        pairs = [(" ".join(TAG.sub("", line).split()), line) for line in lines[timing_index + 1:]]
        cues.append((start, end, [(clean, raw) for clean, raw in pairs if clean]))
    return cues


def unique_lines(cues):
    """Rolling captions repeat each line in the next cues; a line seen just before is not said again."""
    spoken = []
    recent = []
    for start, end, lines in cues:
        for clean, raw in lines:
            if clean in recent:
                continue
            spoken.append((start, end, clean, raw))
            recent = (recent + [clean])[-RECENT_LINES_CHECKED:]
    return spoken


def timed_tokens(raw_line, line_start):
    """YouTube auto captions mark each word's start inline (`word<00:00:04.040><c> next</c>`): keep those times."""
    pieces = INLINE_TIME.split(raw_line)
    tokens = []
    piece_start = line_start
    for index, piece in enumerate(pieces):
        if index % 2 == 1:
            piece_start = seconds_from(*INLINE_TIME_PARTS.match(piece).groups())
            continue
        spoken_text = SOUND_TAG.sub(" ", TAG.sub("", piece))
        tokens += [(piece_start, token) for token in spoken_text.split()]
    return tokens


def evenly_spread_tokens(clean_line, start, end):
    tokens = SOUND_TAG.sub(" ", clean_line).split()
    step = (end - start) / max(len(tokens), 1)
    return [(start + index * step, token) for index, token in enumerate(tokens)]


def words_and_lines(caption_text):
    """Words with times (YouTube's own per word when present, else spread over the caption) and `[mm:ss] line` lines.

    Sound tags such as [Music] or [Applause], in any language, stay in the transcript lines and are left out of the words.
    """
    spoken = unique_lines(read_cues(caption_text))
    timed = []
    transcript_lines = []
    for start, end, clean, raw in spoken:
        if INLINE_TIME.search(raw):
            timed += timed_tokens(raw, start)
        else:
            timed += evenly_spread_tokens(clean, start, end)
        minutes, seconds = divmod(int(start), 60)
        transcript_lines.append(f"[{minutes:02d}:{seconds:02d}] {clean}")
    caption_end = spoken[-1][1] if spoken else 0.0
    words = []
    for index, (word_start, token) in enumerate(timed):
        next_start = timed[index + 1][0] if index + 1 < len(timed) else caption_end
        word_end = min(next_start, word_start + LONGEST_WORD_SECONDS) if next_start > word_start else word_start + 0.2
        words.append({"start": round(word_start, 2), "end": round(word_end, 2), "text": token})
    return words, transcript_lines


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("captions", type=Path)
    parser.add_argument("--out", type=Path)
    arguments = parser.parse_args()

    words, transcript_lines = words_and_lines(arguments.captions.read_text(encoding="utf-8"))
    output = (arguments.out or arguments.captions.parent).resolve()
    output.mkdir(parents=True, exist_ok=True)
    (output / "words.json").write_text(json.dumps(words, ensure_ascii=False, indent=1), encoding="utf-8")
    (output / "transcript.txt").write_text("\n".join(transcript_lines) + "\n", encoding="utf-8")
    print(f"{len(words)} words, {len(transcript_lines)} lines -> {output}")


if __name__ == "__main__":
    main()
