"""Transcribe speech in 30 languages with Qwen3-ASR-0.6B, for what Parakeet does not know (Vietnamese, Chinese, Japanese,
Korean, Thai, Indonesian, Hindi, Arabic...). transcribe.py calls this on its own; run it directly only to force a language.

Usage:
    uv run --no-project --python 3.12 --with qwen-asr --with psutil python -I {{SKILL_DIR}}/scripts/transcribe_qwen.py \
        <video or audio> [--out <folder>] [--from <s>] [--to <s>] [--language Vietnamese] [--device cpu|cuda:0]

Writes the same files as transcribe.py: <out>/words.json ([{start, end, text}]) and <out>/transcript.txt ("[mm:ss] line").
The audio is cut at pauses into segments of at most SEGMENT_SECONDS, so every line keeps its own time. Word times come
from Qwen3-ForcedAligner for its 11 languages (zh, en, yue, fr, de, it, ja, ko, pt, ru, es); in every other language
the words are spread evenly over their segment, as rough as YouTube captions. Models live in QWEN_ASR_MODELS
(default ~/.cache/asr-models) and download there on first use (about 3.7 GB).
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy

SAMPLE_RATE = 16_000
SEGMENT_SECONDS = 20
PAUSE_SEARCH_SECONDS = 6
ENERGY_FRAME_SECONDS = 0.05
CPU_THREADS = int(os.environ.get("QWEN_ASR_THREADS", "6"))
ASR_MODEL = "Qwen3-ASR-0.6B"
ALIGNER_MODEL = "Qwen3-ForcedAligner-0.6B"
ALIGNER_LANGUAGES = {"Chinese", "English", "Cantonese", "French", "German", "Italian", "Japanese", "Korean", "Portuguese", "Russian", "Spanish"}
# Scripts written without spaces between words: a "word" there is one character.
UNSPACED_LANGUAGES = {"Chinese", "Cantonese", "Japanese", "Thai"}


def models_folder():
    configured = os.environ.get("QWEN_ASR_MODELS")
    if configured:
        return Path(configured)
    return Path.home() / ".cache" / "asr-models"


def ensure_model(folder, name):
    target = folder / name
    if not (target / "config.json").exists():
        from huggingface_hub import snapshot_download
        print(f"downloading Qwen/{name} to {target}")
        snapshot_download(f"Qwen/{name}", local_dir=str(target))
    return target


def decode_audio(media_path, start_seconds, end_seconds):
    command = ["ffmpeg", "-loglevel", "error", "-nostdin"]
    if start_seconds is not None:
        command += ["-ss", str(start_seconds)]
    command += ["-i", str(media_path)]
    if end_seconds is not None:
        command += ["-t", str(end_seconds - (start_seconds or 0))]
    command += ["-vn", "-ac", "1", "-ar", str(SAMPLE_RATE), "-f", "f32le", "-"]
    raw_audio = subprocess.run(command, check=True, capture_output=True).stdout
    return numpy.frombuffer(raw_audio, dtype=numpy.float32)


def segment_boundaries(waveform):
    """Cut at the quietest frame within PAUSE_SEARCH_SECONDS before each SEGMENT_SECONDS mark, so no word is split."""
    frame_length = int(ENERGY_FRAME_SECONDS * SAMPLE_RATE)
    boundaries = [0]
    while len(waveform) - boundaries[-1] > SEGMENT_SECONDS * SAMPLE_RATE:
        search_end = boundaries[-1] + SEGMENT_SECONDS * SAMPLE_RATE
        search_start = max(boundaries[-1] + frame_length, search_end - PAUSE_SEARCH_SECONDS * SAMPLE_RATE)
        frame_starts = range(search_start, search_end - frame_length, frame_length)
        quietest = min(frame_starts, key=lambda frame_start: float(numpy.square(waveform[frame_start:frame_start + frame_length]).mean()))
        boundaries.append(quietest + frame_length // 2)
    boundaries.append(len(waveform))
    return boundaries


def spread_words(text, language, start_seconds, end_seconds):
    pieces = list(text.replace(" ", "")) if language in UNSPACED_LANGUAGES else text.split()
    if not pieces:
        return []
    step = (end_seconds - start_seconds) / len(pieces)
    return [
        {"start": round(start_seconds + index * step, 2), "end": round(start_seconds + (index + 1) * step, 2), "text": piece}
        for index, piece in enumerate(pieces)
    ]


def load_model(device, with_aligner):
    import torch
    from qwen_asr import Qwen3ASRModel

    torch.set_num_threads(CPU_THREADS)
    dtype = torch.float32 if device == "cpu" else torch.bfloat16
    folder = models_folder()
    extra = {}
    if with_aligner:
        extra = dict(forced_aligner=str(ensure_model(folder, ALIGNER_MODEL)), forced_aligner_kwargs=dict(dtype=dtype, device_map=device))
    return Qwen3ASRModel.from_pretrained(str(ensure_model(folder, ASR_MODEL)), dtype=dtype, device_map=device,
                                         max_inference_batch_size=1, max_new_tokens=512, **extra)


def transcribe(media_path, start_seconds, end_seconds, language, device, context=""):
    waveform = decode_audio(media_path, start_seconds, end_seconds)
    offset = start_seconds or 0
    boundaries = segment_boundaries(waveform)
    segments = [(waveform[begin:end], offset + begin / SAMPLE_RATE, offset + end / SAMPLE_RATE) for begin, end in zip(boundaries, boundaries[1:])]
    voiced = [segment for segment in segments if float(numpy.abs(segment[0]).max(initial=0.0)) >= 1e-3]
    # The detected language only picks the aligner; the model is told a language only when the user named one.
    # Forced or not, Qwen often spells numbers out ("three hundred ninety-eight" written as words) and drops punctuation on news audio
    # (VTV clip, 2026-11-07): read numbers from the picture or captions before quoting them.
    forced_language = language
    if language is None and voiced:
        # One language per file: detect it on the first voiced segment, then fix it so the aligner can be chosen.
        detector = load_model(device, with_aligner=False)
        language = detector.transcribe(audio=(voiced[0][0], SAMPLE_RATE), language=None)[0].language or None
        if language in ALIGNER_LANGUAGES:
            del detector
            model = load_model(device, with_aligner=True)
        else:
            model = detector
    else:
        model = load_model(device, with_aligner=language in ALIGNER_LANGUAGES)
    lines = []
    words = []
    detected = {}
    for audio, segment_start, segment_end in voiced:
        wants_times = language in ALIGNER_LANGUAGES
        result = model.transcribe(audio=(audio, SAMPLE_RATE), context=context, language=forced_language, return_time_stamps=wants_times)[0]
        text = result.text.strip()
        if not text:
            continue
        detected[result.language] = detected.get(result.language, 0) + 1
        if wants_times and result.time_stamps:
            segment_words = [
                {"start": round(segment_start + item.start_time, 2), "end": round(segment_start + item.end_time, 2), "text": item.text}
                for item in result.time_stamps
            ]
        else:
            segment_words = spread_words(text, result.language, segment_start, segment_end)
        words += segment_words
        lines.append((segment_start, text))
    return words, lines, detected, language


def format_timestamp(seconds):
    minutes, remainder = divmod(int(seconds), 60)
    return f"{minutes:02d}:{remainder:02d}"


def window_suffix(start_seconds, end_seconds):
    if start_seconds is None and end_seconds is None:
        return ""
    return f"_{start_seconds or 0:g}-{'end' if end_seconds is None else format(end_seconds, 'g')}"


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    import psutil

    if sys.platform == "win32":
        psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("media")
    parser.add_argument("--out", default=None)
    parser.add_argument("--from", dest="start_seconds", type=float, default=None)
    parser.add_argument("--to", dest="end_seconds", type=float, default=None)
    parser.add_argument("--language", default=None, help="English name, e.g. Vietnamese; default detects it per segment")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--context", default="", help="title, description and names the video uses; helps proper nouns")
    arguments = parser.parse_args()

    media_path = Path(arguments.media)
    output_folder = Path(arguments.out) if arguments.out else media_path.parent
    output_folder.mkdir(parents=True, exist_ok=True)
    words, lines, detected, language = transcribe(media_path, arguments.start_seconds, arguments.end_seconds, arguments.language, arguments.device, arguments.context)
    suffix = window_suffix(arguments.start_seconds, arguments.end_seconds)
    (output_folder / f"words{suffix}.json").write_text(json.dumps(words, ensure_ascii=False, indent=1), encoding="utf-8")
    transcript = "\n".join(f"[{format_timestamp(start)}] {text}" for start, text in lines)
    (output_folder / f"transcript{suffix}.txt").write_text(transcript + "\n", encoding="utf-8")
    timing = "word times from the aligner" if language in ALIGNER_LANGUAGES else "word times spread over each segment"
    print(f"Qwen3-ASR: {len(lines)} segments, languages {detected}, {timing} -> {output_folder / f'transcript{suffix}.txt'}")


if __name__ == "__main__":
    main()
