"""Generate sound effects and music with ElevenLabs into the sound library, with the credit cost printed for every call.

Run: uv run --no-project --python 3.12 --with psutil --with requests python generate_elevenlabs.py <command> ...

Commands:
  credits                                         credits used, limit and left on the plan
  sfx "<prompt>" --folder NAME [--seconds 2.5] [--variants 3] [--loop] [--influence 0.5] [--model v2|v3]
  music "<prompt>" --folder NAME --seconds 30 [--instrumental] [--model music_v2_5] [--seed 7]
  music --plan plan.json --folder NAME            compose from a composition plan (sections with durations)
  plan "<prompt>" --seconds 30 --out plan.json    ask for a composition plan to edit before composing (free)
  stems <audio file> --folder NAME [--six]        split a track into stems (two: vocals + rest; six: more)
  video-music <video> --folder NAME [--description "..."] [--tags a,b] [--sfx] [--separate]

Files land in sound-library/generated/<NAME>/ with a manifest.json entry (prompt, model, seconds, licence), so
`index.py --add` picks them up with the licence class `elevenlabs`. The key is read from the key file and never
printed. Every paid call reads the subscription before and after and prints what it actually cost.
"""
import argparse
import json
import os
import sys
import time
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import requests

import sound_library as library

API_ROOT = "https://api.elevenlabs.io/v1"
# The key comes from ELEVENLABS_API_KEY, else from this file (never printed).
KEY_FILE = Path(os.environ.get("ELEVENLABS_KEY_FILE", str(Path.home() / ".config" / "elevenlabs" / "api_key.txt")))
GENERATED_DIRECTORY = library.LIBRARY_DIRECTORY / "generated"
LICENCE_TEXT = "ElevenLabs (generated on the owner's paid plan, commercial use)"
SFX_MODELS = {"v2": "eleven_text_to_sound_v2", "v3": "eleven_text_to_sound_v3"}
# Estimates for the pre-call check; the real cost is read back from the subscription after the call.
# Measured 2026-11-04: a 1.5 s v2 sound effect cost 17 credits, 15 s of music_v2_5 cost 206, a plan cost nothing.
ESTIMATED_SFX_CREDITS_PER_SECOND = 12
ESTIMATED_SFX_CREDITS_AUTO_LENGTH = 100
ESTIMATED_MUSIC_CREDITS_PER_SECOND = 14
# The subscription counter lags the call by a few seconds.
COST_READ_ATTEMPTS = 8
COST_READ_PAUSE_SECONDS = 3
REQUEST_TIMEOUT_SECONDS = 900


def read_key():
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if key:
        return key
    if not KEY_FILE.exists():
        sys.exit(f"No ElevenLabs key: set ELEVENLABS_API_KEY or put the key in {KEY_FILE}.")
    key = KEY_FILE.read_text(encoding="ascii").strip()
    if len(key) < 20:
        sys.exit(f"The ElevenLabs key file {KEY_FILE} looks empty (length {len(key)}).")
    return key


def headers(json_body=True):
    result = {"xi-api-key": read_key()}
    if json_body:
        result["Content-Type"] = "application/json"
    return result


def read_credits():
    response = requests.get(f"{API_ROOT}/user/subscription", headers=headers(False), timeout=30)
    response.raise_for_status()
    data = response.json()
    used = data.get("character_count", 0)
    limit = data.get("character_limit", 0)
    return {"tier": data.get("tier"), "used": used, "limit": limit, "left": limit - used,
            "resets": data.get("next_character_count_reset_unix")}


def require_credits(estimate, label):
    credits = read_credits()
    print(f"{label}: about {estimate} credits; {credits['left']} left on the {credits['tier']} plan")
    if credits["left"] < estimate:
        reset = time.strftime("%Y-%m-%d", time.localtime(credits["resets"])) if credits["resets"] else "unknown"
        sys.exit(f"Not enough credits for {label} (needs about {estimate}, {credits['left']} left, resets {reset}). "
                 "Use a library or web sound instead, or ask the owner before buying more.")
    return credits


def report_cost(before, label):
    after = read_credits()
    for _ in range(COST_READ_ATTEMPTS):
        if after["used"] != before["used"]:
            break
        time.sleep(COST_READ_PAUSE_SECONDS)
        after = read_credits()
    print(f"{label}: cost {after['used'] - before['used']} credits, {after['left']} left")


def raise_with_body(response):
    if response.status_code >= 400:
        sys.exit(f"ElevenLabs answered {response.status_code}: {response.text[:400]}")


def slug(text, limit=48):
    words = "".join(character.lower() if character.isalnum() else "-" for character in text).split("-")
    return "-".join(word for word in words if word)[:limit].strip("-") or "sound"


def output_folder(name):
    folder = GENERATED_DIRECTORY / f"elevenlabs-{slug(name)}"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def next_free_path(folder, stem, suffix):
    path = folder / f"{stem}{suffix}"
    number = 2
    while path.exists():
        path = folder / f"{stem}-{number}{suffix}"
        number += 1
    return path


def add_manifest_entry(folder, path, entry):
    """Name-keyed manifest.json that index.py reads; title holds the prompt so search finds it by its words."""
    manifest_path = folder / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    if isinstance(manifest, list):
        manifest = {Path(item["file"]).name: item for item in manifest if isinstance(item, dict) and item.get("file")}
    manifest[path.name] = {"file": path.name, "license": LICENCE_TEXT, "author": "ElevenLabs",
                           "source": "ElevenLabs API", "created": time.strftime("%Y-%m-%d %H:%M"), **entry}
    manifest_path.write_text(json.dumps(manifest, indent=1, ensure_ascii=False), encoding="utf-8")


def generate_sfx(arguments):
    folder = output_folder(arguments.folder)
    per_variant = (round(arguments.seconds * ESTIMATED_SFX_CREDITS_PER_SECOND) if arguments.seconds
                   else ESTIMATED_SFX_CREDITS_AUTO_LENGTH)
    before = require_credits(per_variant * arguments.variants, f"{arguments.variants} sound effect(s)")
    body = {"text": arguments.prompt, "prompt_influence": arguments.influence, "loop": arguments.loop,
            "model_id": SFX_MODELS[arguments.model]}
    if arguments.seconds:
        body["duration_seconds"] = arguments.seconds
    for variant in range(arguments.variants):
        response = requests.post(f"{API_ROOT}/sound-generation", params={"output_format": "mp3_44100_192"},
                                 headers=headers(), json=body, timeout=REQUEST_TIMEOUT_SECONDS)
        raise_with_body(response)
        path = next_free_path(folder, slug(arguments.name or arguments.prompt), ".mp3")
        path.write_bytes(response.content)
        add_manifest_entry(folder, path, {"title": arguments.prompt, "role": arguments.role or "sfx",
                                          "model": body["model_id"], "seconds": arguments.seconds,
                                          "loop": arguments.loop, "prompt_influence": arguments.influence,
                                          "variant": variant + 1})
        print("wrote", path)
    report_cost(before, "sound effects")
    print_index_hint(folder)


def generate_music(arguments):
    folder = output_folder(arguments.folder)
    if arguments.plan:
        plan = json.loads(Path(arguments.plan).read_text(encoding="utf-8"))
        # music_v1 plans hold "sections" under global styles; music_v2 and later answer with "chunks".
        parts = plan.get("sections") or plan.get("chunks") or []
        seconds = sum(part["duration_ms"] for part in parts) / 1000
        body = {"composition_plan": plan, "model_id": arguments.model}
        styles = plan.get("positive_global_styles") or (parts[0].get("positive_styles", []) if parts else [])
        title = arguments.name or "; ".join(styles)[:200]
    else:
        if not arguments.prompt:
            sys.exit("music needs a prompt or --plan")
        seconds = arguments.seconds
        body = {"prompt": arguments.prompt, "model_id": arguments.model, "force_instrumental": arguments.instrumental}
        if seconds:
            body["music_length_ms"] = round(seconds * 1000)
        title = arguments.prompt
    if arguments.seed is not None:
        body["seed"] = arguments.seed
    estimate = round((seconds or 60) * ESTIMATED_MUSIC_CREDITS_PER_SECOND)
    before = require_credits(estimate, f"{seconds or 'auto'} s of music")
    response = requests.post(f"{API_ROOT}/music", params={"output_format": "mp3_44100_192"}, headers=headers(),
                             json=body, timeout=REQUEST_TIMEOUT_SECONDS)
    raise_with_body(response)
    path = next_free_path(folder, slug(arguments.name or title), ".mp3")
    path.write_bytes(response.content)
    add_manifest_entry(folder, path, {"title": title, "role": "music", "model": arguments.model, "seconds": seconds,
                                      "music_tags": title, "plan": arguments.plan})
    print("wrote", path)
    report_cost(before, "music")
    print_index_hint(folder, music=True)


def generate_plan(arguments):
    body = {"prompt": arguments.prompt, "model_id": arguments.model}
    if arguments.seconds:
        body["music_length_ms"] = round(arguments.seconds * 1000)
    response = requests.post(f"{API_ROOT}/music/plan", headers=headers(), json=body, timeout=120)
    raise_with_body(response)
    Path(arguments.out).write_text(json.dumps(response.json(), indent=1, ensure_ascii=False), encoding="utf-8")
    print("plan written to", arguments.out, "- edit section styles and durations, then: music --plan", arguments.out)


def separate_stems(arguments):
    source = Path(arguments.file)
    folder = output_folder(arguments.folder)
    variation = "six_stems_v1" if arguments.six else "two_stems_v1"
    before = require_credits(0, f"stem separation ({variation})")
    with source.open("rb") as handle:
        response = requests.post(f"{API_ROOT}/music/stem-separation", params={"output_format": "mp3_44100_192"},
                                 headers=headers(False), files={"file": (source.name, handle)},
                                 data={"stem_variation_id": variation}, timeout=REQUEST_TIMEOUT_SECONDS)
    raise_with_body(response)
    unpack_answer(response, folder, slug(source.stem), {"title": f"stems of {source.name}", "role": "stem",
                                                        "stem_source": str(source)})
    report_cost(before, "stem separation")


def generate_video_music(arguments):
    video = Path(arguments.video)
    folder = output_folder(arguments.folder)
    before = require_credits(0, "video to music")
    data = {"model_id": arguments.model, "add_sfx": str(arguments.sfx).lower(),
            "separate_tracks": str(arguments.separate).lower()}
    if arguments.description:
        data["description"] = arguments.description
    tags = [tag.strip() for tag in (arguments.tags or "").split(",") if tag.strip()]
    with video.open("rb") as handle:
        response = requests.post(f"{API_ROOT}/music/video-to-music", params={"output_format": "mp3_44100_192"},
                                 headers=headers(False), files=[("videos", (video.name, handle, "video/mp4"))],
                                 data=list(data.items()) + [("tags", tag) for tag in tags],
                                 timeout=REQUEST_TIMEOUT_SECONDS)
    raise_with_body(response)
    unpack_answer(response, folder, slug(arguments.name or video.stem),
                  {"title": arguments.description or f"music for {video.name}", "role": "music",
                   "music_tags": " ".join(tags), "video": str(video)})
    report_cost(before, "video to music")
    print_index_hint(folder, music=True)


def unpack_answer(response, folder, stem, entry):
    """A ZIP answer (stems, separate tracks) is unpacked file by file; anything else is one audio file."""
    if response.content[:2] == b"PK":
        archive_path = next_free_path(folder, stem, ".zip")
        archive_path.write_bytes(response.content)
        with zipfile.ZipFile(archive_path) as archive:
            for member in archive.namelist():
                if Path(member).suffix.lower() not in library.AUDIO_EXTENSIONS:
                    continue
                path = next_free_path(folder, f"{stem}-{slug(Path(member).stem)}", Path(member).suffix.lower())
                path.write_bytes(archive.read(member))
                add_manifest_entry(folder, path, {**entry, "title": f"{entry['title']} - {Path(member).stem}"})
                print("wrote", path)
        archive_path.unlink()
        return
    path = next_free_path(folder, stem, ".mp3")
    path.write_bytes(response.content)
    add_manifest_entry(folder, path, entry)
    print("wrote", path)


def print_index_hint(folder, music=False):
    note = " (music: move the folder under sound-library/music/ first if it should index as kind=music)" if music else ""
    print(f"index it: PY index.py --add \"{library.normalize_path(folder)}\"{note}")


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("credits")

    sfx = commands.add_parser("sfx")
    sfx.add_argument("prompt")
    sfx.add_argument("--folder", required=True, help="project or scene name; files go to generated/elevenlabs-<name>")
    sfx.add_argument("--name", help="file name stem (default: from the prompt)")
    sfx.add_argument("--seconds", type=float, help="0.5 to 30; leave out to let the model choose")
    sfx.add_argument("--variants", type=int, default=2, help="takes to choose from (each costs credits)")
    sfx.add_argument("--loop", action="store_true", help="seamless loop, for beds and ambiences")
    sfx.add_argument("--influence", type=float, default=0.5, help="prompt influence 0..1 (API default 0.3)")
    sfx.add_argument("--model", choices=sorted(SFX_MODELS), default="v2")
    sfx.add_argument("--role", help="manifest role word (sfx, bed, ui, impact...)")

    music = commands.add_parser("music")
    music.add_argument("prompt", nargs="?")
    music.add_argument("--plan", help="composition plan JSON (from the plan command, edited)")
    music.add_argument("--folder", required=True)
    music.add_argument("--name")
    music.add_argument("--seconds", type=float, help="3 to 600 (prompt mode)")
    music.add_argument("--instrumental", action="store_true", help="guarantee no vocals (prompt mode)")
    music.add_argument("--model", choices=["music_v1", "music_v2", "music_v2_5"], default="music_v2_5")
    music.add_argument("--seed", type=int)

    plan = commands.add_parser("plan")
    plan.add_argument("prompt")
    plan.add_argument("--seconds", type=float)
    plan.add_argument("--out", required=True)
    plan.add_argument("--model", choices=["music_v1", "music_v2", "music_v2_5"], default="music_v2_5")

    stems = commands.add_parser("stems")
    stems.add_argument("file")
    stems.add_argument("--folder", required=True)
    stems.add_argument("--six", action="store_true", help="six stems instead of two (vocals + accompaniment)")

    video_music = commands.add_parser("video-music")
    video_music.add_argument("video")
    video_music.add_argument("--folder", required=True)
    video_music.add_argument("--name")
    video_music.add_argument("--description")
    video_music.add_argument("--tags", help="comma separated, at most 10")
    video_music.add_argument("--sfx", action="store_true", help="also add SFX cues the model hears in the picture")
    video_music.add_argument("--separate", action="store_true", help="return music and SFX as separate files")
    video_music.add_argument("--model", choices=["music_v1", "music_v2", "music_v2_5"], default="music_v2_5")
    return parser


def main():
    library.lower_priority()
    arguments = build_parser().parse_args()
    if arguments.command == "credits":
        credits = read_credits()
        reset = time.strftime("%Y-%m-%d", time.localtime(credits["resets"])) if credits["resets"] else "unknown"
        print(f"{credits['tier']}: used {credits['used']} of {credits['limit']}, {credits['left']} left, resets {reset}")
        return
    handlers = {"sfx": generate_sfx, "music": generate_music, "plan": generate_plan, "stems": separate_stems,
                "video-music": generate_video_music}
    handlers[arguments.command](arguments)


if __name__ == "__main__":
    main()
