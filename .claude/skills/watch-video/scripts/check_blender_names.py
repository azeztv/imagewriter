"""Flag Blender node, modifier and constraint names in notes or skill files that Blender 5.x does not have.

Tutorial notes come from transcripts of videos made for older Blender versions, and speech-to-text mishears names.
This checks every "X node", "X modifier", "X constraint" and every Title Case step of an `A -> B -> C` chain against
the names dumped from the installed Blender (data/blender-names.json, made by blender_names_dump.py).

Usage:
  uv run --no-project python check_blender_names.py <file.md, transcript.txt or folder> [...] [--spoken] [--names data/blender-names.json]

Prints one line per unknown name with file, line, a known rename or the closest real names. Exit code 1 when any
unknown name is found. Each flag is a lead to check (frame of the video, Blender manual), not proof of an error:
add-on nodes and node groups a tutorial builds itself are not in Blender.
"""

import argparse
import difflib
import json
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DEFAULT_NAMES = pathlib.Path(__file__).resolve().parent.parent / "data" / "blender-names.json"
TITLE_WORDS = r"[A-Z][A-Za-z0-9/]*(?:\s+(?:[A-Z][A-Za-z0-9/]*|to|on|in|of|from|by))*"
NAMED_THING = re.compile(rf"\b({TITLE_WORDS})\s+(node|modifier|constraint)s?\b")
CHAIN_STEP = re.compile(rf"^\s*({TITLE_WORDS})\s*(?:\(.*\))?\s*$")
# Old names a transcript from Blender 2.8 to 4.x still uses, mapped to the 5.x name.
RENAMED = {
    "mix rgb": "Mix (Color)",
    "separate rgb": "Separate Color",
    "combine rgb": "Combine Color",
    "separate hsv": "Separate Color (HSV mode)",
    "combine hsv": "Combine Color (HSV mode)",
    "musgrave texture": "Noise Texture (Type dropdown, 4.1+)",
    "attribute randomize": "Random Value (fields, 3.0+)",
    "point distribute": "Distribute Points on Faces",
    "point instance": "Instance on Points",
    "attribute proximity": "Geometry Proximity",
    "transfer attribute": "Sample Index / Sample Nearest / Sample Nearest Surface (3.4+)",
    "bloom": "Glare node in the compositor (Eevee Next, 4.2+)",
    "invert": "Invert Color",
}
# Spoken transcripts are lower case and say "mix rgb" without "node", so --spoken (on by default for .txt) looks for the
# old names anywhere in a line. Plain English words among them would flag every sentence, so they are left out there.
COMMON_WORDS_AMONG_OLD_NAMES = {"bloom", "invert"}
SKIPPED_WORDS = {"Ctrl", "Shift", "Alt", "Tab", "Edit Mode", "Object Mode", "Properties", "Add", "Shift A", "Node Wrangler"}


def load_known_names(names_path):
    data = json.loads(names_path.read_text(encoding="utf-8"))
    known = set()
    for value in data.values():
        if isinstance(value, list):
            known.update(name.lower() for name in value)
    return known, data.get("blender_version", "?")


LEADING_FILLER = {"a", "an", "the", "new", "compositor", "shader", "geometry", "add", "check", "renamed", "apply", "blender"}


def strip_filler(candidate):
    words = candidate.split()
    while words and words[0].lower() in LEADING_FILLER:
        words = words[1:]
    return " ".join(words)


def is_known(candidate, known):
    words = candidate.lower().split()
    if not words:
        return True
    for length in range(len(words), 0, -1):
        if " ".join(words[:length]) in known:
            return True
    # Shorthand for a longer real name: "Distribute" for Distribute Points on Faces, "Principled" for Principled BSDF.
    return len(words) == 1 and any(name.startswith(words[0] + " ") for name in known)


def candidates_in_line(line):
    for match in NAMED_THING.finditer(line):
        yield match.group(1)
    if "->" in line:
        for segment in line.split("->"):
            segment = segment.strip(" .,;:*`")
            step = CHAIN_STEP.match(segment)
            if step:
                yield step.group(1)


def check_file(path, known):
    findings = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        for raw_candidate in candidates_in_line(line):
            candidate = strip_filler(raw_candidate)
            renamed = RENAMED.get(candidate.lower())
            # An old name is checked first: its prefix ("Mix" in "Mix RGB") is often a real 5.x name.
            line_without_old_name = line.lower().replace(candidate.lower(), "")
            if renamed and renamed.split(" (")[0].lower() in line_without_old_name:
                continue
            if not renamed and (candidate in SKIPPED_WORDS or is_known(candidate, known)):
                continue
            if renamed:
                hint = f"old name, now {renamed}"
            else:
                close = difflib.get_close_matches(candidate.lower(), known, n=3, cutoff=0.75)
                hint = "closest: " + ", ".join(close) if close else "not in Blender: add-on, custom group, or misheard"
            findings.append((path, line_number, candidate, hint))
    return findings


def check_spoken_file(path):
    findings = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        lowered = line.lower()
        for old_name, new_name in RENAMED.items():
            if old_name in COMMON_WORDS_AMONG_OLD_NAMES:
                continue
            if re.search(rf"\b{re.escape(old_name)}\b", lowered):
                findings.append((path, line_number, old_name, f"old name, now {new_name}"))
    return findings


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", nargs="+", type=pathlib.Path)
    parser.add_argument("--names", type=pathlib.Path, default=DEFAULT_NAMES)
    parser.add_argument("--spoken", action="store_true", help="transcript text: find old names in any case, without 'node'")
    arguments = parser.parse_args()

    known, version = load_known_names(arguments.names)
    files = []
    for path in arguments.paths:
        files.extend(sorted(path.rglob("*.md")) if path.is_dir() else [path])
    findings = []
    for path in files:
        findings.extend(check_file(path, known))
        if arguments.spoken or path.suffix == ".txt":
            findings.extend(check_spoken_file(path))
    seen = set()
    for path, line_number, candidate, hint in findings:
        key = (path, candidate)
        if key in seen:
            continue
        seen.add(key)
        print(f"{path}:{line_number}: {candidate} -- {hint}")
    print(f"{len(seen)} unknown names in {len(files)} files (Blender {version})")
    sys.exit(1 if seen else 0)


if __name__ == "__main__":
    main()
