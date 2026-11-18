"""Transcribe speech with NVIDIA Parakeet TDT (ONNX, CPU) and word timestamps. Replaces Whisper everywhere.

Usage:
    uv run --no-project --python 3.12 --with "onnx-asr[cpu,hub]" --with psutil python -I {{SKILL_DIR}}/scripts/transcribe.py \
        <video or audio> [--out <folder>] [--from <s>] [--to <s>] [--model nemo-parakeet-tdt-0.6b-v3]

Writes <out>/words.json ([{start, end, text, logprob}], seconds in the source file) and <out>/transcript.txt ("[mm:ss] sentence").
With --from or --to the names carry the window (words_30-60.json), so the whole file's transcript stays. A sentence the
model is unsure of is marked [unreliable], and a summary line says so. The default model is English-only Parakeet TDT 0.6B v2; v3 covers 25 European languages.
Other languages (Vietnamese, Chinese, Japanese, Korean, Thai, Indonesian, Hindi, Arabic...) go to transcribe_qwen.py
(Qwen3-ASR, 30 languages): with --language <English name>, or on its own when most Parakeet lines come out unreliable.
Measured 2026-10-29 on the Breaking Bad "Say my name" clip: 70 s of audio in 9 s on CPU, and it caught the quiet
closing lines under the score that faster-whisper small.en and medium.en both dropped. Names still come out misheard
("Gus Fringe", "Eisenberg"): fix them from context.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy
import onnx_asr
import onnxruntime
import psutil

SAMPLE_RATE = 16_000
WINDOW_SECONDS = 60
BOUNDARY_SEARCH_SECONDS = 5
ENERGY_FRAME_SECONDS = 0.1
CPU_THREADS = 6
MODELS_FOLDER = Path.home() / ".cache" / "asr-models"
SENTENCE_ENDINGS = (".", "?", "!")
# Measured 2026-10-31 on synthetic voices: clear English about -0.03, reversed speech the model cannot understand about -0.7.
UNRELIABLE_MEAN_LOGPROB = -0.35
QWEN_SCRIPT = Path(__file__).resolve().parent / "transcribe_qwen.py"
# Parakeet v2 is English; v3 adds these European languages. Anything else goes to Qwen3-ASR.
PARAKEET_LANGUAGES = {
    "english", "bulgarian", "croatian", "czech", "danish", "dutch", "estonian", "finnish", "french", "german", "greek",
    "hungarian", "italian", "latvian", "lithuanian", "maltese", "polish", "portuguese", "romanian", "slovak",
    "slovenian", "spanish", "swedish", "russian", "ukrainian",
}


def decode_audio(media_path, start_seconds, end_seconds):
    """Decode any media file to 16 kHz mono float32 with ffmpeg."""
    command = ["ffmpeg", "-loglevel", "error", "-nostdin"]
    if start_seconds is not None:
        command += ["-ss", str(start_seconds)]
    command += ["-i", str(media_path)]
    if end_seconds is not None:
        command += ["-t", str(end_seconds - (start_seconds or 0))]
    command += ["-vn", "-ac", "1", "-ar", str(SAMPLE_RATE), "-f", "f32le", "-"]
    raw_audio = subprocess.run(command, check=True, capture_output=True).stdout
    return numpy.frombuffer(raw_audio, dtype=numpy.float32)


def window_boundaries(waveform):
    """Cut points about every WINDOW_SECONDS, each moved to the quietest frame nearby so no word is split."""
    frame_length = int(ENERGY_FRAME_SECONDS * SAMPLE_RATE)
    boundaries = [0]
    target = WINDOW_SECONDS * SAMPLE_RATE
    while target < len(waveform) - frame_length:
        search_start = max(boundaries[-1] + frame_length, target - BOUNDARY_SEARCH_SECONDS * SAMPLE_RATE)
        search_end = min(len(waveform), target + BOUNDARY_SEARCH_SECONDS * SAMPLE_RATE)
        frame_starts = range(search_start, search_end - frame_length, frame_length)
        quietest = min(frame_starts, key=lambda frame_start: float(numpy.square(waveform[frame_start:frame_start + frame_length]).mean()))
        boundaries.append(quietest + frame_length // 2)
        target = boundaries[-1] + WINDOW_SECONDS * SAMPLE_RATE
    boundaries.append(len(waveform))
    return boundaries


def words_from_tokens(tokens, timestamps, logprobs, offset_seconds, window_end_seconds):
    """Join subword tokens into words; a token starting with a space starts a new word."""
    words = []
    word_logprobs = []
    for token, timestamp, logprob in zip(tokens, timestamps, logprobs):
        if token.startswith(" ") or not words:
            words.append({"start": offset_seconds + timestamp, "text": token.strip()})
            word_logprobs.append([])
        else:
            words[-1]["text"] += token
        word_logprobs[-1].append(float(logprob))
    for index, word in enumerate(words):
        next_start = words[index + 1]["start"] if index + 1 < len(words) else window_end_seconds
        word["end"] = min(next_start, word["start"] + 1.0)
        word["start"] = round(word["start"], 2)
        word["end"] = round(word["end"], 2)
        word["logprob"] = round(sum(word_logprobs[index]) / len(word_logprobs[index]), 3)
    return [word for word in words if word["text"]]


def load_model(model_name):
    session_options = onnxruntime.SessionOptions()
    session_options.intra_op_num_threads = CPU_THREADS
    # A plain folder, not the Hugging Face cache: onnxruntime refuses external weights reached through cache symlinks.
    model_folder = MODELS_FOLDER / model_name
    return onnx_asr.load_model(model_name, model_folder, sess_options=session_options).with_timestamps()


def transcribe(media_path, start_seconds, end_seconds, model_name):
    waveform = decode_audio(media_path, start_seconds, end_seconds)
    model = load_model(model_name)
    offset = start_seconds or 0
    boundaries = window_boundaries(waveform)
    words = []
    for window_start, window_end in zip(boundaries, boundaries[1:]):
        result = model.recognize(waveform[window_start:window_end], sample_rate=SAMPLE_RATE)
        window_offset = offset + window_start / SAMPLE_RATE
        window_end_seconds = offset + window_end / SAMPLE_RATE
        words += words_from_tokens(result.tokens or [], result.timestamps or [], result.logprobs or [], window_offset, window_end_seconds)
    return words


def sentences_from_words(words):
    sentences = []
    current = []
    for word in words:
        current.append(word)
        if word["text"].endswith(SENTENCE_ENDINGS):
            sentences.append(current)
            current = []
    if current:
        sentences.append(current)
    return sentences


def is_unreliable(words):
    return sum(word["logprob"] for word in words) / len(words) < UNRELIABLE_MEAN_LOGPROB


def format_timestamp(seconds):
    minutes, remainder = divmod(int(seconds), 60)
    return f"{minutes:02d}:{remainder:02d}"


def transcript_line(sentence):
    mark = "[unreliable] " if is_unreliable(sentence) else ""
    return f"[{format_timestamp(sentence[0]['start'])}] {mark}{' '.join(word['text'] for word in sentence)}"


def window_suffix(start_seconds, end_seconds):
    """A window gets its own file names, so it never replaces the transcript of the whole file."""
    if start_seconds is None and end_seconds is None:
        return ""
    return f"_{start_seconds or 0:g}-{'end' if end_seconds is None else format(end_seconds, 'g')}"


def run_qwen(arguments):
    """Hand the same file over to transcribe_qwen.py, which needs torch and qwen-asr instead of onnx-asr."""
    sys.stdout.flush()
    command = [
        "uv", "run", "--no-project", "--python", "3.12", "--with", "qwen-asr", "--with", "psutil",
        "python", "-I", str(QWEN_SCRIPT), arguments.media,
    ]
    for flag, value in (("--out", arguments.out), ("--from", arguments.start_seconds), ("--to", arguments.end_seconds), ("--language", arguments.language)):
        if value is not None:
            command += [flag, str(value)]
    completed = subprocess.run(command)
    if completed.returncode != 0:
        sys.exit(completed.returncode)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("media")
    parser.add_argument("--out", default=None, help="output folder (default: next to the media file)")
    parser.add_argument("--from", dest="start_seconds", type=float, default=None)
    parser.add_argument("--to", dest="end_seconds", type=float, default=None)
    parser.add_argument("--model", default="nemo-parakeet-tdt-0.6b-v2")
    parser.add_argument("--language", default=None,
                        help="English name of a language Parakeet lacks (Vietnamese, Japanese, Thai...): go straight to Qwen3-ASR")
    parser.add_argument("--no-fallback", action="store_true", help="never hand over to Qwen3-ASR")
    arguments = parser.parse_args()
    if arguments.language and arguments.language.lower() not in PARAKEET_LANGUAGES:
        run_qwen(arguments)
        return
    if arguments.language and arguments.language.lower() != "english" and arguments.model.endswith("-v2"):
        arguments.model = "nemo-parakeet-tdt-0.6b-v3"

    media_path = Path(arguments.media)
    output_folder = Path(arguments.out) if arguments.out else media_path.parent
    output_folder.mkdir(parents=True, exist_ok=True)
    words = transcribe(media_path, arguments.start_seconds, arguments.end_seconds, arguments.model)

    suffix = window_suffix(arguments.start_seconds, arguments.end_seconds)
    (output_folder / f"words{suffix}.json").write_text(json.dumps(words, ensure_ascii=False, indent=1), encoding="utf-8")
    sentences = sentences_from_words(words)
    lines = [transcript_line(sentence) for sentence in sentences]
    (output_folder / f"transcript{suffix}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(words)} words, {len(lines)} sentences -> {output_folder / f'transcript{suffix}.txt'}")
    unreliable_count = sum(1 for sentence in sentences if is_unreliable(sentence))
    mostly_unknown = not lines or unreliable_count * 2 > len(lines)
    if mostly_unknown and not arguments.no_fallback:
        print("Parakeet does not know this language: transcribing again with Qwen3-ASR (30 languages).")
        run_qwen(arguments)
        return
    if unreliable_count:
        cause = ("Most of the file: the language may be one this model does not know, use captions."
                 if unreliable_count * 2 > len(lines) else "Those lines are probably misheard: check before quoting.")
        print(f"UNRELIABLE: {unreliable_count} of {len(lines)} sentences have low model confidence. {cause}")


if __name__ == "__main__":
    main()
