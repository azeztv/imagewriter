"""Download a mood-balanced set of Kevin MacLeod tracks (CC BY 4.0) from incompetech.com into the music library.

Licence was read on the source's own page (incompetech.com/music/royalty-free/music.html: "Licensed under Creative
Commons: By Attribution 4.0 License"). Writes manifest.json (read by index.py) and registers each track in
sources.json with its URL, licence and exact credit line.

Run: uv run --no-project --python 3.12 --with psutil python fetch_music.py [--count 190] [--seed 7]
"""
import argparse
import concurrent.futures
import json
import random
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import psutil

sys.path.insert(0, str(Path(__file__).parent))
from sound_library import LIBRARY_DIRECTORY  # noqa: E402
TARGET_FOLDER = LIBRARY_DIRECTORY / "music" / "incompetech"
CATALOGUE_URL = "https://incompetech.com/music/royalty-free/pieces.json"
FILE_URL = "https://incompetech.com/music/royalty-free/mp3-royaltyfree/"
PAGE_URL = "https://incompetech.com/music/royalty-free/music.html"
LICENCE_TEXT = "CC BY 4.0"
LICENCE_URL = "http://creativecommons.org/licenses/by/4.0/"
GENRE_NAMES = {"2": "african", "4": "classical", "5": "contemporary", "7": "electronica", "8": "funk", "10": "horror",
               "11": "jazz", "19": "rock", "20": "silent film score", "22": "soundtrack", "24": "unclassifiable",
               "25": "world", "12": "latin", "16": "pop", "13": "modern", "9": "holiday", "18": "reggae"}
MIN_SECONDS = 60
MAX_SECONDS = 330
HEADERS = {"User-Agent": "Mozilla/5.0"}


def fetch_bytes(url):
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def length_seconds(piece):
    hours, minutes, seconds = (int(part) for part in piece["length"].split(":"))
    return hours * 3600 + minutes * 60 + seconds


def feels_of(piece):
    return [feel.strip().lower() for feel in (piece["feel"] or "").split(",") if feel.strip()]


def choose_pieces(pieces, count, seed):
    """Round robin over the feel tags so every mood is covered, shortest-first among equals is avoided by shuffling."""
    random_source = random.Random(seed)
    usable = [piece for piece in pieces if MIN_SECONDS <= length_seconds(piece) <= MAX_SECONDS and piece["isrc"]]
    random_source.shuffle(usable)
    by_feel = {}
    for piece in usable:
        for feel in feels_of(piece):
            by_feel.setdefault(feel, []).append(piece)
    chosen, chosen_titles = [], set()
    while len(chosen) < count and any(by_feel.values()):
        for feel in sorted(by_feel):
            while by_feel[feel] and by_feel[feel][-1]["title"] in chosen_titles:
                by_feel[feel].pop()
            if by_feel[feel] and len(chosen) < count:
                piece = by_feel[feel].pop()
                chosen.append(piece)
                chosen_titles.add(piece["title"])
    return chosen


def build_entry(piece):
    file_name = piece["filename"]
    tag_words = feels_of(piece) + [GENRE_NAMES.get(piece["genre"], "")] + [
        name.strip().lower() for name in (piece["instruments"] or "").split(",")]
    return {
        "file": file_name,
        "title": piece["title"],
        "author": "Kevin MacLeod",
        "license": LICENCE_TEXT,
        "licence_url": LICENCE_URL,
        "source": FILE_URL + urllib.parse.quote(file_name),
        "page": PAGE_URL,
        "bpm": int(piece["bpm"]) if (piece["bpm"] or "").isdigit() else None,
        "music_tags": " ".join(word for word in tag_words if word),
        "description": piece["description"] or "",
        "credit": f'"{piece["title"]}" Kevin MacLeod (incompetech.com)\nLicensed under Creative Commons: '
                  f'By Attribution 4.0 License\n{LICENCE_URL}',
    }


def download_one(entry):
    """Download one track unless it is already complete; retries twice. Returns True when the file is in place."""
    target = TARGET_FOLDER / entry["file"]
    if target.exists() and target.stat().st_size >= 100_000:
        return True
    for _ in range(3):
        try:
            target.write_bytes(fetch_bytes(entry["source"]))
            return True
        except Exception as error:
            print(f"retry {entry['file']}: {error}", flush=True)
    return False


def download_all(entries):
    """Four downloads at a time: the site serves each connection slowly."""
    TARGET_FOLDER.mkdir(parents=True, exist_ok=True)
    done = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for number, (entry, ok) in enumerate(zip(entries, pool.map(download_one, entries)), start=1):
            if ok:
                done.append(entry)
            print(f"{number}/{len(entries)} {entry['file']} {'ok' if ok else 'FAILED'}", flush=True)
    return done


def write_records(entries):
    (TARGET_FOLDER / "manifest.json").write_text(json.dumps(entries, indent=1), encoding="utf-8")
    sources_path = LIBRARY_DIRECTORY / "sources.json"
    sources = json.loads(sources_path.read_text(encoding="utf-8"))
    folder = str(TARGET_FOLDER).replace("\\", "/")
    if folder not in sources["folders"]:
        sources["folders"].append(folder)
    kept = [track for track in sources.get("music", []) if not track["path"].startswith(folder)]
    kept += [{"path": f"{folder}/{entry['file']}", "title": entry["title"], "author": entry["author"],
              "url": entry["source"], "page": entry["page"], "licence": entry["license"],
              "credit": entry["credit"]} for entry in entries]
    sources["music"] = kept
    sources_path.write_text(json.dumps(sources, indent=1), encoding="utf-8")


def main():
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--count", type=int, default=190)
    parser.add_argument("--seed", type=int, default=7)
    arguments = parser.parse_args()
    pieces = json.loads(fetch_bytes(CATALOGUE_URL).decode("utf-8"))
    chosen = choose_pieces(pieces, arguments.count, arguments.seed)
    print(f"{len(chosen)} tracks chosen from {len(pieces)}", flush=True)
    entries = download_all([build_entry(piece) for piece in chosen])
    write_records(entries)
    print(f"downloaded {len(entries)} tracks")


if __name__ == "__main__":
    main()
