"""Who speaks when: speaker turns for a video or audio file, offline, any language, with sherpa-onnx.

Usage:
  uv run --no-project --with sherpa-onnx --with numpy python diarize.py <video or audio> [--out DIR]
      [--threshold 0.6] [--sweep] [--speakers N] [--words words.json]

Writes <out>/speakers.json ([{start, end, speaker}]) and, with --words, <out>/transcript_speakers.txt: the transcript
cut into "[mm:ss] S1: ..." lines at each change of speaker. --threshold decides how alike two voices may be and stay
one speaker: lower splits one voice into several, higher merges similar voices. --sweep also prints the speaker count
at SWEEP_THRESHOLDS; a count that changes between them is not settled, so check it against the picture. --speakers
fixes the count but merged two of three similar voices in testing, so it is not a fix for that. Speaker labels are
arbitrary (S1 is whoever speaks first), never names: name a speaker only from the picture or what is said.

Models (about 30 MB, no sign-in) download on first use from the sherpa-onnx GitHub releases into
SPEAKER_MODELS (default ~/.cache/asr-models/diarization): pyannote segmentation 3.0 and the 3D-Speaker CAM++ embedding.
"""

import argparse
import json
import os
import subprocess
import sys
import tarfile
import urllib.request
from pathlib import Path

import numpy

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SAMPLE_RATE = 16_000
RELEASES = "https://github.com/k2-fsa/sherpa-onnx/releases/download"
SEGMENTATION_ARCHIVE = f"{RELEASES}/speaker-segmentation-models/sherpa-onnx-pyannote-segmentation-3-0.tar.bz2"
EMBEDDING_MODEL = "3dspeaker_speech_campplus_sv_zh_en_16k-common_advanced.onnx"
EMBEDDING_URL = f"{RELEASES}/speaker-recongition-models/{EMBEDDING_MODEL}"
SHORTEST_TURN_SECONDS = 0.3
SHORTEST_GAP_SECONDS = 0.5
# Two three-voice tests (2026-11-07), share of speech labelled right:
#   two men and a woman, two languages: 0.5 found 6 speakers (66%), 0.6 found 4 (86%), 0.7 found 3 (96%)
#   three men reading the same Vietnamese sentence: 0.5 and 0.6 found 3 (100%), 0.7 and --speakers 3 found 2 (64%)
# 0.6 is the best single value across both; no value is right for every recording.
DEFAULT_THRESHOLD = 0.6
SWEEP_THRESHOLDS = (0.5, 0.6, 0.7)


def models_folder():
    configured = os.environ.get("SPEAKER_MODELS")
    return Path(configured) if configured else Path.home() / ".cache" / "asr-models" / "diarization"


def ensure_models(folder):
    folder.mkdir(parents=True, exist_ok=True)
    segmentation = folder / "sherpa-onnx-pyannote-segmentation-3-0" / "model.onnx"
    if not segmentation.exists():
        archive = folder / "segmentation.tar.bz2"
        print(f"downloading speaker segmentation model to {folder}")
        urllib.request.urlretrieve(SEGMENTATION_ARCHIVE, archive)
        with tarfile.open(archive) as bundle:
            bundle.extractall(folder, filter="data")
        archive.unlink()
    embedding = folder / EMBEDDING_MODEL
    if not embedding.exists():
        print(f"downloading speaker embedding model to {folder}")
        urllib.request.urlretrieve(EMBEDDING_URL, embedding)
    return segmentation, embedding


def decode_audio(media_path):
    command = ["ffmpeg", "-loglevel", "error", "-nostdin", "-i", str(media_path), "-vn", "-ac", "1", "-ar", str(SAMPLE_RATE), "-f", "f32le", "-"]
    return numpy.frombuffer(subprocess.run(command, check=True, capture_output=True).stdout, dtype=numpy.float32)


def speaker_turns(waveform, speakers, threshold):
    import sherpa_onnx

    segmentation, embedding = ensure_models(models_folder())
    config = sherpa_onnx.OfflineSpeakerDiarizationConfig(
        segmentation=sherpa_onnx.OfflineSpeakerSegmentationModelConfig(
            pyannote=sherpa_onnx.OfflineSpeakerSegmentationPyannoteModelConfig(model=str(segmentation))),
        embedding=sherpa_onnx.SpeakerEmbeddingExtractorConfig(model=str(embedding)),
        clustering=sherpa_onnx.FastClusteringConfig(num_clusters=speakers or -1, threshold=threshold),
        min_duration_on=SHORTEST_TURN_SECONDS,
        min_duration_off=SHORTEST_GAP_SECONDS,
    )
    diarizer = sherpa_onnx.OfflineSpeakerDiarization(config)
    result = diarizer.process(numpy.ascontiguousarray(waveform)).sort_by_start_time()
    first_seen = {}
    turns = []
    for segment in result:
        label = first_seen.setdefault(segment.speaker, f"S{len(first_seen) + 1}")
        turns.append({"start": round(segment.start, 2), "end": round(segment.end, 2), "speaker": label})
    return turns


def speaker_at(turns, seconds):
    best = None
    best_distance = float("inf")
    for turn in turns:
        if turn["start"] <= seconds <= turn["end"]:
            return turn["speaker"]
        distance = min(abs(seconds - turn["start"]), abs(seconds - turn["end"]))
        if distance < best_distance:
            best, best_distance = turn["speaker"], distance
    return best


def transcript_by_speaker(turns, words):
    lines = []
    current_speaker = None
    for word in words:
        speaker = speaker_at(turns, (word["start"] + word["end"]) / 2)
        if speaker != current_speaker:
            minutes, seconds = divmod(int(word["start"]), 60)
            lines.append(f"[{minutes:02d}:{seconds:02d}] {speaker}:")
            current_speaker = speaker
        lines[-1] += " " + word["text"]
    return lines


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("media", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--speakers", type=int, default=0, help="number of speakers when known")
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    parser.add_argument("--words", type=Path, help="words.json to split by speaker")
    parser.add_argument("--sweep", action="store_true", help="also print the speaker count at each of SWEEP_THRESHOLDS")
    arguments = parser.parse_args()

    output = arguments.out or arguments.media.parent
    output.mkdir(parents=True, exist_ok=True)
    waveform = decode_audio(arguments.media)
    if arguments.sweep:
        counts = {threshold: len({turn["speaker"] for turn in speaker_turns(waveform, 0, threshold)}) for threshold in SWEEP_THRESHOLDS}
        settled = "settled" if len(set(counts.values())) == 1 else "NOT settled: check speaker changes against the picture"
        print("speaker count by threshold: " + ", ".join(f"{threshold}: {count}" for threshold, count in counts.items()) + f" ({settled})")
    turns = speaker_turns(waveform, arguments.speakers, arguments.threshold)
    (output / "speakers.json").write_text(json.dumps(turns, indent=1), encoding="utf-8")
    talk = {}
    for turn in turns:
        talk[turn["speaker"]] = talk.get(turn["speaker"], 0) + turn["end"] - turn["start"]
    summary = ", ".join(f"{speaker} {seconds:.0f} s" for speaker, seconds in talk.items())
    print(f"{len(talk)} speakers, {len(turns)} turns ({summary}) -> {output / 'speakers.json'}")
    if arguments.words:
        words = json.loads(arguments.words.read_text(encoding="utf-8"))
        lines = transcript_by_speaker(turns, words)
        (output / "transcript_speakers.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"{len(lines)} speaker lines -> {output / 'transcript_speakers.txt'}")


if __name__ == "__main__":
    main()
