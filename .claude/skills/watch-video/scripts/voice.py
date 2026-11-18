"""Measure how each sentence is spoken: pitch, loudness, rate, pause and ending, each against the speaker's own baseline.

The numbers are evidence for reading tone, not an emotion label. Needs word times from transcribe.py or captions.py.

Usage: uv run --no-project --with numpy python voice.py <video or audio> --words <words.json> [--out DIR]
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SAMPLE_RATE = 16000
FRAME_SAMPLES = 640
HOP_SAMPLES = 160
HOP_SECONDS = HOP_SAMPLES / SAMPLE_RATE
LOWEST_PITCH_HZ = 70
HIGHEST_PITCH_HZ = 400
VOICED_CORRELATION = 0.5
OCTAVE_GUARD = 0.85
SENTENCE_ENDINGS = (".", "?", "!")
SENTENCE_GAP_SECONDS = 0.7
LONGEST_SENTENCE_SECONDS = 12.0
ENDING_SECONDS = 0.8
ENDING_CHANGE_SEMITONES = 2.0
MINIMUM_VOICED_SHARE = 0.25
MINIMUM_WORDS_FOR_RATE = 4
OCTAVE_FOLD_SHARE = 1.68  # about 9 semitones: a frame further than this from the sentence is usually an octave error
MAD_TO_DEVIATION = 1.4826
STANDS_OUT_DEVIATIONS = 2.5
# A sentence stands out by leaving this file's own spread, and never for less than these.
STANDS_OUT_MINIMUMS = {"pitch": 3.0, "loudness": 5.0, "rate": 0.35}
STANDS_OUT_PAUSE_SECONDS = 1.0
TABLE_NOTES = """# Evidence for reading tone, not an emotion label: say what the voice does, then what it may mean, marked as a guess.
# Each number is against this speaker's own median in this file. * marks a sentence far outside this file's own spread, and names what.
# One baseline assumes one speaker: with several, a jump in pitch can be a change of speaker. Music under the voice
# makes pitch unreliable. In a tonal language such as Vietnamese, compare sentence level and range; the ending is
# partly the last word's tone. Word times from captions are spread evenly, so rate and pause are rougher there.
"""


def read_samples(media):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-nostdin", "-i", str(media), "-vn", "-ac", "1", "-ar", str(SAMPLE_RATE),
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return numpy.frombuffer(raw, dtype=numpy.float32)


def split_into_sentences(words):
    sentences = []
    current = []
    for word in words:
        gap_before = word["start"] - current[-1]["end"] if current else 0.0
        too_long = current and word["end"] - current[0]["start"] > LONGEST_SENTENCE_SECONDS
        if gap_before >= SENTENCE_GAP_SECONDS or too_long:
            sentences.append(current)
            current = []
        current.append(word)
        if word["text"].endswith(SENTENCE_ENDINGS):
            sentences.append(current)
            current = []
    if current:
        sentences.append(current)
    return sentences


def pitch_track(samples):
    """Pitch in Hz per hop, NaN where unvoiced, by normalised autocorrelation."""
    if len(samples) < FRAME_SAMPLES:
        return numpy.full(1, numpy.nan)
    frame_count = 1 + (len(samples) - FRAME_SAMPLES) // HOP_SAMPLES
    indices = numpy.arange(FRAME_SAMPLES)[None, :] + HOP_SAMPLES * numpy.arange(frame_count)[:, None]
    frames = samples[indices] * numpy.hanning(FRAME_SAMPLES)
    frames = frames - frames.mean(axis=1, keepdims=True)
    spectrum = numpy.fft.rfft(frames, n=2 * FRAME_SAMPLES, axis=1)
    correlation = numpy.fft.irfft(numpy.abs(spectrum) ** 2, axis=1)[:, :FRAME_SAMPLES]
    window_correlation = numpy.fft.irfft(numpy.abs(numpy.fft.rfft(numpy.hanning(FRAME_SAMPLES), n=2 * FRAME_SAMPLES)) ** 2)[:FRAME_SAMPLES]
    energy = correlation[:, 0] + 1e-9
    normalised = correlation / energy[:, None] * (window_correlation[0] / numpy.maximum(window_correlation, 1e-6))
    shortest_lag = SAMPLE_RATE // HIGHEST_PITCH_HZ
    longest_lag = SAMPLE_RATE // LOWEST_PITCH_HZ
    candidates = normalised[:, shortest_lag:longest_lag]
    strongest = candidates.max(axis=1)
    # The first lag near the strongest peak: a voice also correlates at twice its period, which would read an octave low.
    first_strong = numpy.argmax(candidates >= (OCTAVE_GUARD * strongest)[:, None], axis=1)
    pitch = SAMPLE_RATE / (shortest_lag + first_strong).astype(numpy.float64)
    pitch[strongest < VOICED_CORRELATION] = numpy.nan
    return pitch


def semitones(frequency, reference):
    return 12.0 * numpy.log2(frequency / reference)


def fold_octave_errors(voiced):
    """Move frames an octave away back beside the sentence's median, so one tracking slip does not read as a wide range."""
    folded = voiced.copy()
    median = numpy.median(voiced)
    while (too_high := folded > median * OCTAVE_FOLD_SHARE).any():
        folded[too_high] /= 2.0
    while (too_low := folded < median / OCTAVE_FOLD_SHARE).any():
        folded[too_low] *= 2.0
    return folded


def describe_ending(pitch):
    """Rising or falling across the last voiced stretch of the sentence."""
    voiced = pitch[~numpy.isnan(pitch)]
    tail = voiced[-int(ENDING_SECONDS / HOP_SECONDS):]
    if len(tail) < 10:
        return "unknown"
    third = len(tail) // 3
    change = float(semitones(numpy.median(tail[-third:]), numpy.median(tail[:third])))
    if change >= ENDING_CHANGE_SEMITONES:
        return "rising"
    if change <= -ENDING_CHANGE_SEMITONES:
        return "falling"
    return "level"


def measure_sentence(samples, words, previous_end):
    start = words[0]["start"]
    end = words[-1]["end"]
    piece = samples[int(start * SAMPLE_RATE):int(end * SAMPLE_RATE)]
    if len(piece) < SAMPLE_RATE // 10:
        return None  # caption times past the end of the audio, or a zero-length line: nothing to measure
    pitch = pitch_track(piece)
    voiced = pitch[~numpy.isnan(pitch)]
    has_pitch = len(voiced) / len(pitch) >= MINIMUM_VOICED_SHARE
    folded = fold_octave_errors(voiced) if has_pitch else voiced
    loud_part = numpy.abs(piece) > 0.1 * (numpy.abs(piece).max() + 1e-9)
    return {
        "start": round(start, 2),
        "end": round(end, 2),
        "text": " ".join(word["text"] for word in words),
        "pause_seconds": round(max(0.0, start - previous_end), 2),
        "words_per_second": round(len(words) / max(end - start, 0.1), 2) if len(words) >= MINIMUM_WORDS_FOR_RATE else None,
        "pitch_hz": round(float(numpy.median(voiced)), 1) if has_pitch else None,
        "pitch_range_semitones": round(float(semitones(numpy.percentile(folded, 90), numpy.percentile(folded, 10))), 1) if has_pitch else None,
        "rms": float(numpy.sqrt(numpy.mean(piece[loud_part] ** 2))) if loud_part.any() else 0.0,
        "ending": describe_ending(pitch) if has_pitch else "unknown",
    }


def far_from_the_rest(values, minimum):
    """Which values lie outside the file's own spread. The median deviation resists the outliers being looked for."""
    known = [value for value in values if value is not None]
    if not known:
        return [False for _ in values]
    centre = float(numpy.median(known))
    spread = MAD_TO_DEVIATION * float(numpy.median(numpy.abs(numpy.array(known) - centre)))
    limit = max(STANDS_OUT_DEVIATIONS * spread, minimum)
    return [value is not None and abs(value - centre) >= limit for value in values]


def add_baseline_comparison(sentences):
    pitches = [sentence["pitch_hz"] for sentence in sentences if sentence["pitch_hz"]]
    baseline_pitch = float(numpy.median(pitches)) if pitches else None
    baseline_rms = float(numpy.median([sentence["rms"] for sentence in sentences])) + 1e-9
    rates = [sentence["words_per_second"] for sentence in sentences if sentence["words_per_second"]]
    baseline_rate = float(numpy.median(rates)) if rates else None
    for sentence in sentences:
        pitch = sentence["pitch_hz"]
        sentence["pitch_semitones"] = round(float(semitones(pitch, baseline_pitch)), 1) if pitch else None
        sentence["loudness_decibels"] = round(20.0 * float(numpy.log10((sentence.pop("rms") + 1e-9) / baseline_rms)), 1)
        rate = sentence["words_per_second"]
        sentence["rate_change"] = round(rate / baseline_rate - 1.0, 2) if rate else None
    far_pitch = far_from_the_rest([sentence["pitch_semitones"] for sentence in sentences], STANDS_OUT_MINIMUMS["pitch"])
    far_loudness = far_from_the_rest([sentence["loudness_decibels"] for sentence in sentences], STANDS_OUT_MINIMUMS["loudness"])
    far_rate = far_from_the_rest([sentence["rate_change"] for sentence in sentences], STANDS_OUT_MINIMUMS["rate"])
    for index, sentence in enumerate(sentences):
        reasons = [("pitch", far_pitch[index]), ("loudness", far_loudness[index]), ("rate", far_rate[index]),
                   ("pause", sentence["pause_seconds"] >= STANDS_OUT_PAUSE_SECONDS)]
        sentence["stands_out"] = [name for name, is_far in reasons if is_far]
    return baseline_pitch


def table_line(sentence):
    minutes, seconds = divmod(int(sentence["start"]), 60)
    mark = f"* {'+'.join(sentence['stands_out'])} " if sentence["stands_out"] else "  "
    if sentence["pitch_semitones"] is None:
        pitch = "pitch unknown"
    else:
        pitch = f"pitch {sentence['pitch_semitones']:+.1f} st, range {sentence['pitch_range_semitones']:.1f} st"
    rate = "rate n/a" if sentence["rate_change"] is None else f"rate {sentence['rate_change']:+.0%}"
    return (f"{mark}[{minutes:02d}:{seconds:02d}] {pitch}, loud {sentence['loudness_decibels']:+.1f} dB, "
            f"{rate}, pause {sentence['pause_seconds']:.1f} s, end {sentence['ending']} | {sentence['text']}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("media", type=Path)
    parser.add_argument("--words", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    arguments = parser.parse_args()

    words = json.loads(arguments.words.read_text(encoding="utf-8"))
    if not words:
        raise SystemExit(f"no words in {arguments.words}: nothing was said, or the transcript failed")
    samples = read_samples(arguments.media)
    sentences = []
    previous_end = 0.0
    for sentence_words in split_into_sentences(words):
        measured = measure_sentence(samples, sentence_words, previous_end)
        if measured is not None:
            sentences.append(measured)
        previous_end = sentence_words[-1]["end"]
    baseline_pitch = add_baseline_comparison(sentences)

    output = (arguments.out or arguments.words.parent).resolve()
    output.mkdir(parents=True, exist_ok=True)
    (output / "voice.json").write_text(json.dumps(sentences, ensure_ascii=False, indent=1), encoding="utf-8")
    baseline = f"# Baseline pitch {baseline_pitch:.0f} Hz.\n" if baseline_pitch else "# No voiced pitch found: music or noise may cover the voice.\n"
    table = TABLE_NOTES + baseline + "\n".join(table_line(sentence) for sentence in sentences) + "\n"
    (output / "voice.txt").write_text(table, encoding="utf-8")
    standing_out = sum(1 for sentence in sentences if sentence["stands_out"])
    print(f"{len(sentences)} sentences, {standing_out} stand out -> {output / 'voice.txt'}")


main()
