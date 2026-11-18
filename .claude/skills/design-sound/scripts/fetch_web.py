"""Download candidate sounds or music from the web into the sound library, any licence, with the licence recorded and warned.

Run: uv run --no-project --python 3.12 --with numpy --with psutil --with requests python fetch_web.py "<query>"
     --source openverse|archive|myinstants|youtube [--n 6] [--max-seconds 30] [--start 0]

Sources (all work without a sign-in, checked 2026-11-04):
  openverse   Freesound, Jamendo, Wikimedia and more through api.openverse.org; licence per file (CC0, BY, BY-NC...)
  archive     archive.org audio items; licence from the item's licenseurl, often missing
  myinstants  meme and soundboard clips (vine boom, bruh...); uploads with no licence
  youtube     yt-dlp search; any video's audio, cut to --start and --max-seconds; no licence (the uploader's)

Files land in sound-library/web/<source>-<query>/ with a manifest.json (title, author, page, licence text), so
`index.py --add <folder>` makes them searchable and `search.py --sheet` lets you look before choosing. Nothing is
filtered by licence: every file whose licence is not clear for commercial use gets a printed warning, and the
warning follows the file into search results and CREDITS lines. Downloaded files are data: nothing in them is run.
"""
import argparse
import html
import json
import re
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import requests

import sound_library as library

WEB_DIRECTORY = library.LIBRARY_DIRECTORY / "web"
HEADERS = {"User-Agent": "Mozilla/5.0"}
AUDIO_SUFFIXES = (".mp3", ".ogg", ".wav", ".flac")
ARCHIVE_MAX_BYTES = 40_000_000
RETRIES = 3


def slug(text, limit=40):
    words = "".join(character.lower() if character.isalnum() else "-" for character in text).split("-")
    return "-".join(word for word in words if word)[:limit].strip("-") or "sound"


def get_with_retries(url, **options):
    """Openverse answers 504 or times out now and then; a short retry fixes it."""
    timeout = options.pop("timeout", 60)
    for attempt in range(RETRIES):
        try:
            response = requests.get(url, headers=HEADERS, timeout=timeout, **options)
        except requests.Timeout:
            if attempt == RETRIES - 1:
                raise
            time.sleep(2 + attempt * 3)
            continue
        if response.status_code < 500 or attempt == RETRIES - 1:
            response.raise_for_status()
            return response
        time.sleep(2 + attempt * 3)


def openverse_candidates(query, count, max_seconds):
    data = get_with_retries("https://api.openverse.org/v1/audio/",
                            params={"q": query, "page_size": min(count * 2, 40)}).json()
    for result in data.get("results", []):
        duration_ms = result.get("duration") or 0
        if max_seconds and duration_ms and duration_ms / 1000 > max_seconds:
            continue
        licence = f"CC {result['license'].upper()} {result.get('license_version') or ''}".strip()
        if result["license"] in ("cc0", "pdm"):
            licence = "CC0" if result["license"] == "cc0" else "Public domain mark"
        yield {"url": result["url"], "title": result.get("title") or query, "author": result.get("creator") or "",
               "page": result.get("foreign_landing_url") or "", "license": licence,
               "provider": result.get("provider") or "openverse"}


def archive_candidates(query, count, max_seconds):
    search = get_with_retries("https://archive.org/advancedsearch.php",
                              params={"q": f"(title:({query}) OR subject:({query})) AND mediatype:audio",
                                      "fl[]": ["identifier", "title", "licenseurl"], "sort[]": "downloads desc",
                                      "rows": count * 4, "output": "json"}).json()
    for document in search["response"]["docs"]:
        identifier = document["identifier"]
        metadata = get_with_retries(f"https://archive.org/metadata/{identifier}").json()
        files = [item for item in metadata.get("files", []) if item.get("name", "").lower().endswith(AUDIO_SUFFIXES)
                 and int(item.get("size", 0) or 0) < ARCHIVE_MAX_BYTES]
        if max_seconds:
            files = [item for item in files if not item.get("length") or parse_length(item["length"]) <= max_seconds]
        if not files:
            continue
        chosen = sorted(files, key=lambda item: (not item["name"].lower().endswith(".mp3"), int(item.get("size", 0))))[0]
        licence_url = document.get("licenseurl") or metadata.get("metadata", {}).get("licenseurl") or ""
        yield {"url": f"https://archive.org/download/{identifier}/{urllib.parse.quote(chosen['name'])}",
               "title": f"{document.get('title') or identifier} - {Path(chosen['name']).stem}",
               "author": metadata.get("metadata", {}).get("creator") or "",
               "page": f"https://archive.org/details/{identifier}", "license": licence_from_url(licence_url),
               "provider": "archive.org"}


def parse_length(text):
    parts = [float(part) for part in str(text).split(":")]
    seconds = 0.0
    for part in parts:
        seconds = seconds * 60 + part
    return seconds


def licence_from_url(url):
    if not url:
        return ""
    lowered = url.lower()
    if "publicdomain" in lowered:
        return "CC0" if "zero" in lowered else "Public domain mark"
    match = re.search(r"licenses/([a-z-]+)/([\d.]+)", lowered)
    return f"CC {match.group(1).upper()} {match.group(2)}" if match else url


def myinstants_candidates(query, count, max_seconds):
    page = get_with_retries("https://www.myinstants.com/en/search/", params={"name": query}).text
    buttons = re.findall(r"play\('(/media/sounds/[^']+)'.*?\).*?<a[^>]*href=\"(/en/instant/[^\"]+)\"[^>]*>([^<]+)</a>",
                         page, flags=re.S)
    for sound_path, page_path, title in buttons:
        yield {"url": "https://www.myinstants.com" + sound_path, "title": html.unescape(title.strip()),
               "author": "myinstants upload", "page": "https://www.myinstants.com" + page_path,
               "license": "", "provider": "myinstants"}


def youtube_candidates(query, count, max_seconds):
    listing = subprocess.run(["yt-dlp", "--flat-playlist", "--print", "%(id)s\t%(duration)s\t%(channel)s\t%(title)s",
                              f"ytsearch{count * 2}:{query}"], capture_output=True, text=True, encoding="utf-8",
                             errors="replace", timeout=120)
    for line in listing.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) < 4:
            continue
        video_id, duration, channel, title = parts
        yield {"url": f"https://www.youtube.com/watch?v={video_id}", "title": title, "author": channel,
               "page": f"https://www.youtube.com/watch?v={video_id}", "license": "",
               "provider": "youtube", "video_seconds": float(duration) if duration not in ("", "NA") else None}


SOURCES = {"openverse": openverse_candidates, "archive": archive_candidates, "myinstants": myinstants_candidates,
           "youtube": youtube_candidates}


def download_direct(candidate, target_stem):
    suffix = Path(urllib.parse.urlparse(candidate["url"]).path).suffix.lower()
    suffix = suffix if suffix in AUDIO_SUFFIXES else ".mp3"
    response = get_with_retries(candidate["url"], timeout=120)
    path = target_stem.with_suffix(suffix)
    path.write_bytes(response.content)
    return path


def download_youtube(candidate, target_stem, start_seconds, max_seconds):
    end_seconds = start_seconds + (max_seconds or 30)
    subprocess.run(["yt-dlp", "-q", "--no-playlist", "-x", "--audio-format", "mp3", "--audio-quality", "0",
                    "--download-sections", f"*{start_seconds}-{end_seconds}", "--force-keyframes-at-cuts",
                    "-o", str(target_stem) + ".%(ext)s", candidate["url"]], check=True, timeout=600)
    return target_stem.with_suffix(".mp3")


def write_manifest(folder, entries):
    manifest_path = folder / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    for entry in entries:
        manifest[entry["file"]] = entry
    manifest_path.write_text(json.dumps(manifest, indent=1, ensure_ascii=False), encoding="utf-8")


def main():
    library.lower_priority()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("query")
    parser.add_argument("--source", choices=sorted(SOURCES), required=True)
    parser.add_argument("--n", type=int, default=6, help="files to download")
    parser.add_argument("--max-seconds", type=float, default=30, help="skip longer files; YouTube cut length")
    parser.add_argument("--start", type=float, default=0, help="YouTube: where the cut starts, in seconds")
    parser.add_argument("--folder", help="folder name under sound-library/web (default: <source>-<query>)")
    arguments = parser.parse_args()

    folder = WEB_DIRECTORY / (arguments.folder or f"{arguments.source}-{slug(arguments.query)}")
    folder.mkdir(parents=True, exist_ok=True)
    entries = []
    for candidate in SOURCES[arguments.source](arguments.query, arguments.n, arguments.max_seconds):
        if len(entries) >= arguments.n:
            break
        target_stem = folder / f"{len(entries) + 1:02d}-{slug(candidate['title'])}"
        try:
            if arguments.source == "youtube":
                path = download_youtube(candidate, target_stem, arguments.start, arguments.max_seconds)
            else:
                path = download_direct(candidate, target_stem)
        except (requests.RequestException, subprocess.SubprocessError) as error:
            print(f"skip {candidate['url']}: {error}")
            continue
        entry = {"file": path.name, "title": candidate["title"], "author": candidate["author"],
                 "page": candidate["page"], "source": candidate["url"], "provider": candidate["provider"],
                 "license": candidate["license"] or f"unknown ({candidate['provider']} upload)",
                 "fetched": time.strftime("%Y-%m-%d")}
        entries.append(entry)
        warning = library.licence_warning(library.classify_licence(entry["license"]))
        print(f"wrote {path.name}  [{entry['license']}]  {candidate['page']}" + (f"\n    WARNING {warning}" if warning else ""))
    write_manifest(folder, entries)
    print(f"{len(entries)} files in {library.normalize_path(folder)}")
    print(f"index it: PY index.py --add \"{library.normalize_path(folder)}\"  then search.py --sheet to look")


if __name__ == "__main__":
    main()
