"""Compare two transcripts of the same audio and list where they disagree: those spots are the likely mishearings.

Usage:
  uv run --no-project python compare_transcripts.py <words_a.json> <words_b.json> [--names A B] [--out disagreements.txt]

Inputs are words.json files from captions.py, transcribe.py or transcribe_qwen.py ([{start, end, text}]). Only the
time both cover is compared. Words are matched after lowercasing and dropping punctuation. Each disagreement prints
with its time and both versions; spans that involve a digit are marked `number`, because one source writing "30%" and
the other "thirty percent" is a difference in writing, not in hearing. Where both sources agree they can still both
be wrong: agreement lowers the risk, it does not prove the words.
"""

import argparse
import difflib
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PUNCTUATION = re.compile(r"[^\w]+")
EDGE_SLACK_SECONDS = 3.0


def load_words(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def normalized(text):
    return PUNCTUATION.sub("", unicodedata.normalize("NFC", text.lower()))


def overlap(words_a, words_b):
    start = max(words_a[0]["start"], words_b[0]["start"])
    end = min(words_a[-1]["end"], words_b[-1]["end"])
    # Spread word times (captions, Qwen without its aligner) can sit seconds off, so the window edges get some slack.
    slack = EDGE_SLACK_SECONDS
    inside = lambda words: [word for word in words if start - slack <= word["start"] <= end + slack and normalized(word["text"])]
    return inside(words_a), inside(words_b), start, end


def format_timestamp(seconds):
    minutes, remainder = divmod(int(seconds), 60)
    return f"{minutes:02d}:{remainder:02d}"


def disagreements(words_a, words_b):
    tokens_a = [normalized(word["text"]) for word in words_a]
    tokens_b = [normalized(word["text"]) for word in words_b]
    matcher = difflib.SequenceMatcher(a=tokens_a, b=tokens_b, autojunk=False)
    found = []
    for operation, a_start, a_end, b_start, b_end in matcher.get_opcodes():
        if operation == "equal":
            continue
        text_a = " ".join(word["text"] for word in words_a[a_start:a_end])
        text_b = " ".join(word["text"] for word in words_b[b_start:b_end])
        time_source = words_a[a_start] if a_start < len(words_a) else words_b[min(b_start, len(words_b) - 1)]
        kind = "number" if re.search(r"\d", text_a + text_b) else "words"
        found.append({"time": time_source["start"], "kind": kind, "a": text_a, "b": text_b})
    agreeing = sum(block.size for block in matcher.get_matching_blocks())
    return found, agreeing / max(len(tokens_a), 1)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("words_a")
    parser.add_argument("words_b")
    parser.add_argument("--names", nargs=2, default=["A", "B"])
    parser.add_argument("--out", type=Path)
    arguments = parser.parse_args()

    words_a, words_b, start, end = overlap(load_words(arguments.words_a), load_words(arguments.words_b))
    found, agreement = disagreements(words_a, words_b)
    name_a, name_b = arguments.names
    width = max(len(name_a), len(name_b))
    lines = [f"{format_timestamp(start)}-{format_timestamp(end)}: {len(words_a)} words in {name_a}, {agreement:.0%} matched by {name_b}; "
             f"{sum(1 for item in found if item['kind'] == 'words')} word disagreements, {sum(1 for item in found if item['kind'] == 'number')} number spans"]
    for item in found:
        lines.append(f"[{format_timestamp(item['time'])}] {item['kind']:<6} {name_a:<{width}}: {item['a'] or '-'}")
        lines.append(f"{'':16}{name_b:<{width}}: {item['b'] or '-'}")
    report = "\n".join(lines) + "\n"
    if arguments.out:
        arguments.out.write_text(report, encoding="utf-8")
    print(report if len(lines) < 80 else "\n".join(lines[:80]) + f"\n... {len(lines) - 80} more lines in {arguments.out}")


if __name__ == "__main__":
    main()
