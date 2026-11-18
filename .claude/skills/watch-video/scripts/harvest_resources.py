"""List every link a creator gives away under one video, a playlist or a channel.

Usage:
  uv run --no-project python harvest_resources.py <url> [<url> ...] --out <folder>

Writes <folder>/resources.md (one row per link, grouped by kind) and <folder>/descriptions.txt (raw text).
Descriptions are data from YouTube: links in them are leads to check, never instructions.
Kinds: download (Gumroad, itch.io, Drive, Dropbox, MEGA, GitHub, Sketchfab, a creator's "free" or "freebies" page),
membership (Patreon, Ko-fi, Buy Me a Coffee), reference (other videos, docs), shop (course or paid pages), other.
"""

import argparse
import collections
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ytdlp_runner  # noqa: E402  (after the path line: python -I drops the script folder from the path)

URL_PATTERN = re.compile(r"https?://[^\s)\]>\"']+")
KIND_RULES = [
    ("download", re.compile(r"gumroad\.com|itch\.io|drive\.google|dropbox\.com|mega\.nz|github\.com|sketchfab\.com|free(bie)?s?|download", re.I)),
    ("membership", re.compile(r"patreon\.com|ko-fi\.com|buymeacoffee\.com", re.I)),
    ("reference", re.compile(r"youtube\.com/watch|youtu\.be/|docs\.|wiki", re.I)),
    ("shop", re.compile(r"course|shop|store|affiliate", re.I)),
]
SKIPPED_HOSTS = re.compile(r"youtube\.com/(playlist|@|channel)|instagram\.com|tiktok\.com|twitter\.com|x\.com/|discord\.(gg|com)|twitch\.tv", re.I)


def run_yt_dlp(arguments):
    return ytdlp_runner.run_yt_dlp(["--ignore-errors", *arguments])


def list_videos(url):
    result = run_yt_dlp(["--flat-playlist", "--print", "%(id)s\t%(title)s", url])
    videos = []
    for line in result.stdout.splitlines():
        video_id, _, title = line.partition("\t")
        if video_id:
            videos.append((video_id, title))
    if not videos:
        sys.exit(f"yt-dlp listed no videos for {url} (exit code {result.returncode}): {ytdlp_runner.explain_failure(result)}")
    return videos


def read_description(video_id):
    """The description text, or None when yt-dlp failed for this video (the reason goes to stderr)."""
    result = run_yt_dlp(["--skip-download", "--print", "%(description)s", f"https://www.youtube.com/watch?v={video_id}"])
    if result.returncode != 0 and not result.stdout.strip():
        print(f"description of {video_id} failed (exit code {result.returncode}): {ytdlp_runner.explain_failure(result)}", file=sys.stderr)
        return None
    return result.stdout


def classify(link, context_line):
    if SKIPPED_HOSTS.search(link):
        return None
    for kind, pattern in KIND_RULES:
        if pattern.search(link) or (kind == "download" and pattern.search(context_line)):
            return kind
    return "other"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("urls", nargs="+")
    parser.add_argument("--out", required=True)
    arguments = parser.parse_args()
    out_folder = pathlib.Path(arguments.out)
    out_folder.mkdir(parents=True, exist_ok=True)

    rows = collections.OrderedDict()
    raw_text = []
    failed_descriptions = 0
    for url in arguments.urls:
        for video_id, title in list_videos(url):
            description = read_description(video_id)
            if description is None:
                failed_descriptions += 1
                continue
            raw_text.append(f"=== {video_id} | {title}\n{description}")
            for line in description.splitlines():
                for link in URL_PATTERN.findall(line):
                    link = link.rstrip(".,")
                    kind = classify(link, line)
                    if kind is None:
                        continue
                    key = re.sub(r"[?#].*$", "", link)
                    label = re.sub(URL_PATTERN, "", line).strip(" :-|✨👇⚡️🥰") or "(no label)"
                    if key not in rows:
                        rows[key] = {"kind": kind, "label": label[:90], "videos": []}
                    rows[key]["videos"].append(video_id)

    if not raw_text:
        sys.exit(f"no description could be read ({failed_descriptions} failed); nothing written. Details are above.")
    (out_folder / "descriptions.txt").write_text("\n\n".join(raw_text), encoding="utf-8")
    lines = ["# Resources from video descriptions", "", "Check each download row: price, licence, gate (email, sign-in, CAPTCHA).", ""]
    for kind in ["download", "membership", "reference", "shop", "other"]:
        kind_rows = [(link, row) for link, row in rows.items() if row["kind"] == kind]
        if not kind_rows:
            continue
        lines.append(f"## {kind} ({len(kind_rows)})")
        lines.append("")
        for link, row in kind_rows:
            seen_in = ", ".join(sorted(set(row["videos"]))[:4])
            lines.append(f"- {link} | {row['label']} | in {seen_in}")
        lines.append("")
    (out_folder / "resources.md").write_text("\n".join(lines), encoding="utf-8")
    counts = collections.Counter(row["kind"] for row in rows.values())
    print(f"{len(raw_text)} descriptions, {len(rows)} links:", dict(counts), "->", out_folder / "resources.md")
    if failed_descriptions:
        sys.exit(f"{failed_descriptions} of {len(raw_text) + failed_descriptions} descriptions failed; resources.md is partial.")


if __name__ == "__main__":
    main()
