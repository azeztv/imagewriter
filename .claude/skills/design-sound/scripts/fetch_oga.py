"""Download CC0 music from OpenGameArt.org into the music library (no login).

Walks the public advanced search (type Music, licence CC0, most downloaded first), opens each content page, and keeps
a track only when that page lists CC0 as a licence. Tracks under MIN_SECONDS are dropped after download.

Run: uv run --no-project --python 3.12 --with psutil --with soundfile python fetch_oga.py [--count 45]
"""
import argparse
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import psutil
import soundfile

sys.path.insert(0, str(Path(__file__).parent))
from sound_library import LIBRARY_DIRECTORY  # noqa: E402
TARGET_FOLDER = LIBRARY_DIRECTORY / "music" / "opengameart"
SEARCH_URL = ("https://opengameart.org/art-search-advanced?keys=&field_art_type_tid%5B%5D=12"
              "&field_art_licenses_tid%5B%5D=4&sort_by=count&sort_order=DESC&page={}")
SKIP_SLUGS = {"faq", "free-music-pack"}
MIN_SECONDS = 60
MAX_FILES_PER_PAGE = 2
HEADERS = {"User-Agent": "Mozilla/5.0"}


def fetch_bytes(url):
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def fetch_text(url):
    return fetch_bytes(url).decode("utf-8", errors="replace")


def strip_tags(fragment):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]*>", " ", fragment))).strip()


def find_slugs(search_html):
    slugs = re.findall(r'href="/content/([a-z0-9-]+)"', search_html)
    return [slug for slug in dict.fromkeys(slugs) if slug not in SKIP_SLUGS and "challenge" not in slug]


def field_text(page_html, field_class):
    match = re.search(field_class + r'.{0,600}?</div>\s*</div>', page_html, re.S)
    return strip_tags(match.group(0)) if match else ""


def parse_page(slug, page_html):
    licence_text = field_text(page_html, "field-name-field-art-licenses")
    if "CC0" not in licence_text:
        return None
    title_match = re.search(r"<title>([^<]*?)\s*\|", page_html)
    author_match = re.search(r'property="foaf:name" datatype="">([^<]+)<', page_html)
    tag_words = field_text(page_html, "field-name-field-art-tags").replace("Tags:", "").split()
    tag_text = " ".join(word for word in tag_words if "field" not in word and "=" not in word and "<" not in word)
    file_urls = re.findall(r'data-ogg-url=\'(https://opengameart.org/sites/default/files/[^\']+)\'', page_html)
    file_urls += re.findall(r'href="(https://opengameart.org/sites/default/files/[^"]+\.(?:mp3|ogg|flac))"', page_html)
    originals = [url for url in dict.fromkeys(file_urls) if "/styles/" not in url and "audio_preview" not in url]
    return {
        "slug": slug,
        "title": html.unescape(title_match.group(1)).strip() if title_match else slug,
        "author": html.unescape(author_match.group(1)).strip() if author_match else "unknown",
        "tags": tag_text,
        "urls": originals[:MAX_FILES_PER_PAGE],
        "page": f"https://opengameart.org/content/{slug}",
    }


def download_track(page_info, url):
    file_name = Path(urllib.parse.unquote(url)).name
    target = TARGET_FOLDER / file_name
    target.write_bytes(fetch_bytes(url))
    try:
        seconds = soundfile.info(str(target)).duration
    except RuntimeError:
        seconds = 0.0
    if seconds < MIN_SECONDS:
        target.unlink()
        return None
    return {
        "file": file_name,
        "title": page_info["title"],
        "author": page_info["author"],
        "license": "CC0",
        "source": url,
        "page": page_info["page"],
        "music_tags": page_info["tags"].lower(),
        "description": "",
        "credit": f'"{page_info["title"]}" by {page_info["author"]} (opengameart.org), CC0, no credit required.',
    }


def duplicate_key(entry):
    """The same track is often attached as .mp3 and .ogg, or twice as name and name_0: one key for all of them."""
    stem = re.sub(r"_\d+$", "", Path(entry["file"]).stem.lower())
    stem = re.sub(r"\.(ogg|mp3)$", "", stem)
    return re.sub(r"[^a-z0-9]", "", stem)


def drop_duplicates(entries):
    kept, seen = [], set()
    for entry in sorted(entries, key=lambda item: item["file"].lower().endswith(".mp3")):
        key = duplicate_key(entry)
        if key in seen:
            (TARGET_FOLDER / entry["file"]).unlink(missing_ok=True)
            continue
        seen.add(key)
        kept.append(entry)
    return kept


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
    parser.add_argument("--count", type=int, default=45)
    parser.add_argument("--pages", type=int, default=8)
    parser.add_argument("--dedupe-only", action="store_true", help="only drop duplicate files from the manifest")
    arguments = parser.parse_args()
    TARGET_FOLDER.mkdir(parents=True, exist_ok=True)
    entries = json.loads((TARGET_FOLDER / "manifest.json").read_text(encoding="utf-8")) if arguments.dedupe_only else []
    if arguments.dedupe_only:
        write_records(drop_duplicates(entries))
        return
    for page_number in range(0 if arguments.dedupe_only else arguments.pages):
        for slug in find_slugs(fetch_text(SEARCH_URL.format(page_number))):
            if len(entries) >= arguments.count:
                break
            time.sleep(0.5)
            page_info = parse_page(slug, fetch_text(f"https://opengameart.org/content/{slug}"))
            if not page_info:
                print(f"skip (not CC0 on its page): {slug}", flush=True)
                continue
            for url in page_info["urls"]:
                entry = download_track(page_info, url)
                if entry:
                    entries.append(entry)
                    print(f"{len(entries)} {entry['file']}", flush=True)
    entries = drop_duplicates(entries)
    write_records(entries)
    print(f"downloaded {len(entries)} CC0 tracks")


if __name__ == "__main__":
    main()
