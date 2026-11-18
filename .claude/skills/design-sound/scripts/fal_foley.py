"""Generate foley for a silent video with HunyuanVideo-Foley hosted on fal (fal-ai/hunyuan-video-foley).

Run: uv run --no-project --python 3.12 --with fal-client --with numpy --with soundfile python fal_foley.py film.mp4 \
         --prompt "furniture dropped on a wooden floor, soft thuds" --out foley.wav [--mux out.mp4]
     ... fal_foley.py film.mp4 --shots shots.json --out foley.wav     one prompt per shot (format: foley_shots.py)

Same model as video_foley.py, on fal's GPUs, so nothing runs on this machine. The key comes from FAL_KEY, else
~/.config/fal/api_key.txt, else a FAL_KEY= line in ~/.config/fal/.env; it is never printed. Films longer than --chunk
seconds go up as overlapping pieces (the model takes at most 15 s) and are joined with an equal-power crossfade.
Writes <out>.report.json with time, the price estimate and the share of near-silent windows (heard nothing).
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

import numpy
import soundfile

from foley_shots import fade_lengths, load_shots, plan_pieces, single_prompt_pieces

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ENDPOINT = "fal-ai/hunyuan-video-foley"
PRICE_PER_10_SECONDS = 0.10  # fal model page, read 2026-11-08
MODEL_MAX_SECONDS = 15.0
SAMPLE_RATE = 48000
SILENT_WINDOW_DB = -80.0
HEARD_NOTHING_SHARE = 0.8
CONFIG_FOLDER = Path.home() / ".config" / "fal"


def load_key():
    key = os.environ.get("FAL_KEY", "").strip()
    if not key and (CONFIG_FOLDER / "api_key.txt").exists():
        key = (CONFIG_FOLDER / "api_key.txt").read_text(encoding="ascii").strip()
    if not key and (CONFIG_FOLDER / ".env").exists():
        for line in (CONFIG_FOLDER / ".env").read_text(encoding="ascii").splitlines():
            if line.startswith("FAL_KEY="):
                key = line.partition("=")[2].strip().strip('"')
    if len(key) < 20:
        sys.exit("No fal key: create one at https://fal.ai/dashboard/keys and save it to ~/.config/fal/api_key.txt "
                 "(or set FAL_KEY).")
    os.environ["FAL_KEY"] = key


def probe_duration(video_path):
    output = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video_path],
        capture_output=True, text=True, check=True,
    ).stdout
    return float(output.strip())


def cut_clip(video_path, start, end, folder, index):
    clip_path = os.path.join(folder, f"chunk_{index:03d}.mp4")
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-ss", f"{start:.3f}", "-i", video_path, "-t", f"{end - start:.3f}",
         "-an", "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", clip_path],
        check=True,
    )
    return clip_path


def generate_piece(clip_path, piece, arguments, folder, index):
    import fal_client

    video_url = fal_client.upload_file(clip_path)
    request = {
        "video_url": video_url,
        "text_prompt": piece["prompt"],
        "negative_prompt": piece["neg"],
        "num_inference_steps": arguments.steps,
        "guidance_scale": arguments.guidance,
        "seed": arguments.seed,
    }
    result = fal_client.subscribe(ENDPOINT, arguments=request)
    videos = result["video"] if isinstance(result["video"], list) else [result["video"]]
    returned_video = os.path.join(folder, f"returned_{index:03d}.mp4")
    urllib.request.urlretrieve(videos[0]["url"], returned_video)
    returned_audio = os.path.join(folder, f"returned_{index:03d}.wav")
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", returned_video, "-vn", "-ac", "2", "-ar", str(SAMPLE_RATE),
         "-c:a", "pcm_s24le", returned_audio],
        check=True,
    )
    samples, _ = soundfile.read(returned_audio, always_2d=True)
    return samples


def join_with_crossfade(audio_pieces, pieces, total_seconds):
    """Lays each piece at its start time; equal-power fades over the real overlap with each neighbour."""
    total_samples = int(round(total_seconds * SAMPLE_RATE))
    output = numpy.zeros((total_samples, audio_pieces[0].shape[1]))
    for audio, piece, (fade_in, fade_out) in zip(audio_pieces, pieces, fade_lengths(pieces)):
        audio = audio.copy()
        fade_in_samples = min(int(round(fade_in * SAMPLE_RATE)), len(audio))
        fade_out_samples = min(int(round(fade_out * SAMPLE_RATE)), len(audio))
        if fade_in_samples > 0:
            audio[:fade_in_samples] *= numpy.sin(numpy.linspace(0, 1, fade_in_samples) * numpy.pi / 2)[:, None]
        if fade_out_samples > 0:
            audio[-fade_out_samples:] *= numpy.sin(numpy.linspace(1, 0, fade_out_samples) * numpy.pi / 2)[:, None]
        offset = int(round(piece["start"] * SAMPLE_RATE))
        length = min(len(audio), total_samples - offset)
        output[offset:offset + length] += audio[:length]
    return output


def heard_nothing_share(track):
    mono = track.mean(axis=1)
    window = SAMPLE_RATE // 2
    count = max(1, len(mono) // window)
    silent = 0
    for index in range(count):
        piece = mono[index * window:(index + 1) * window]
        if 20 * numpy.log10(numpy.sqrt(numpy.mean(piece ** 2)) + 1e-9) < SILENT_WINDOW_DB:
            silent += 1
    return silent / count


def mux(video_path, audio_path, out_path):
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", video_path, "-i", audio_path, "-map", "0:v:0", "-map", "1:a:0",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out_path],
        check=True,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("video")
    parser.add_argument("--prompt", default=None, help="what makes the sound, in plain words (whole film)")
    parser.add_argument("--shots", default=None, help="JSON shot list, one prompt per shot (see foley_shots.py)")
    parser.add_argument("--cut-fade", type=float, default=0.08, help="crossfade at a cut between shots, seconds")
    parser.add_argument("--neg", default="noisy, harsh", help="what to avoid")
    parser.add_argument("--out", required=True, help="output WAV (48 kHz)")
    parser.add_argument("--mux", default=None, help="also write the video with this audio as AAC")
    parser.add_argument("--steps", type=int, default=50)
    parser.add_argument("--guidance", type=float, default=4.5)
    parser.add_argument("--chunk", type=float, default=12.0, help="piece length for long films, at most 15")
    parser.add_argument("--overlap", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=1)
    arguments = parser.parse_args()
    if not arguments.prompt and not arguments.shots:
        parser.error("give --prompt, --shots, or both (--prompt then fills shots without one)")

    load_key()
    duration = probe_duration(arguments.video)
    chunk_seconds = min(arguments.chunk, MODEL_MAX_SECONDS)
    if arguments.shots:
        shots = load_shots(arguments.shots, duration, arguments.prompt, arguments.neg)
        pieces_plan = plan_pieces(shots, duration, chunk_seconds, arguments.overlap, arguments.cut_fade)
    else:
        shots = None
        pieces_plan = single_prompt_pieces(duration, arguments.prompt, arguments.neg, chunk_seconds, arguments.overlap)
    whole_film = len(pieces_plan) == 1 and pieces_plan[0]["start"] == 0.0 and pieces_plan[0]["end"] >= duration
    billed_seconds = sum(piece["end"] - piece["start"] for piece in pieces_plan)
    estimate = round(billed_seconds / 10 * PRICE_PER_10_SECONDS, 3)
    print(f"{duration:.1f} s in {len(pieces_plan)} piece(s), about ${estimate} at ${PRICE_PER_10_SECONDS} per 10 s")

    started = time.time()
    pieces = []
    with tempfile.TemporaryDirectory() as folder:
        for index, piece in enumerate(pieces_plan):
            if whole_film:
                clip_path = arguments.video
            else:
                clip_path = cut_clip(arguments.video, piece["start"], piece["end"], folder, index)
            pieces.append(generate_piece(clip_path, piece, arguments, folder, index))
            print(f"piece {index + 1}/{len(pieces_plan)} {piece['start']:.1f}-{piece['end']:.1f} s "
                  f"\"{piece['prompt'][:50]}\" done at {time.time() - started:.0f} s")

    track = pieces[0] if whole_film else join_with_crossfade(pieces, pieces_plan, duration)
    os.makedirs(os.path.dirname(os.path.abspath(arguments.out)), exist_ok=True)
    soundfile.write(arguments.out, track, SAMPLE_RATE, subtype="PCM_24")
    if arguments.mux:
        mux(arguments.video, arguments.out, arguments.mux)

    silent_share = heard_nothing_share(track)
    report = {
        "video": arguments.video,
        "prompt": arguments.prompt,
        "shots": shots,
        "endpoint": ENDPOINT,
        "video_seconds": round(duration, 2),
        "pieces": len(pieces_plan),
        "wall_seconds": round(time.time() - started, 1),
        "estimated_cost_usd": estimate,
        "silent_share": round(silent_share, 2),
        "heard_nothing": silent_share >= HEARD_NOTHING_SHARE,
    }
    with open(arguments.out + ".report.json", "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
    print(json.dumps(report, indent=2))
    if report["heard_nothing"]:
        print("WARNING heard nothing: place this film's foley from its event list instead (foley.py).")


if __name__ == "__main__":
    main()
