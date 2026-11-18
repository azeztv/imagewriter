"""The review ear: check a finished mix or one cue against what it should contain.

Run: uv run --no-project --python 3.12 --with numpy --with scipy --with librosa --with soundfile --with pyloudnorm
     --with psutil --with torch --with transformers python listen.py <audio> --expect "door slam@3.2" [--expect ...]
For each expected cue it reports: does CLAP hear that label (rank among ~150 vocabulary labels), how far the onset
sits from the expected time, the window loudness, and whether the cue stands at least 6 dB above the bed in its band.
"""
import argparse
import sys
from pathlib import Path

import librosa
import numpy

sys.path.insert(0, str(Path(__file__).parent))
import sound_library as library

MASKING_MARGIN_DB = 6.0
CLEAR_RANK = 5  # expected label within the top 5 of ~150 vocabulary labels
PLAUSIBLE_RANK = 15
SILENCE_FLOOR_DB = -60.0
MINIMUM_SILENCE_SECONDS = 0.5
N_FFT = 4096
HOP = 512


def parse_expectation(text):
    label, _, seconds = text.rpartition("@")
    if not label:
        raise SystemExit(f'--expect needs "label@seconds", got: {text}')
    return label.strip(), float(seconds)


def find_silence_gaps(samples, sample_rate):
    window = sample_rate // 20
    count = len(samples) // window
    levels = numpy.array([library.to_db(numpy.sqrt(numpy.mean(samples[i * window:(i + 1) * window] ** 2) + 1e-12))
                          for i in range(count)])
    gaps, start = [], None
    for index, silent in enumerate(levels < SILENCE_FLOOR_DB):
        if silent and start is None:
            start = index
        if (not silent or index == count - 1) and start is not None:
            length = (index - start) * 0.05
            if length >= MINIMUM_SILENCE_SECONDS:
                gaps.append((start * 0.05, start * 0.05 + length))
            start = None
    return gaps


def band_levels_db(samples, sample_rate):
    """Per-frame power in dB for each band, from one STFT of the whole file."""
    power = numpy.abs(librosa.stft(samples, n_fft=N_FFT, hop_length=HOP)) ** 2
    frequencies = librosa.fft_frequencies(sr=sample_rate, n_fft=N_FFT)
    return {name: 10 * numpy.log10(power[(frequencies >= low) & (frequencies < high)].sum(axis=0) + 1e-12)
            for name, (low, high) in library.BANDS.items()}


def masking_margins(levels, sample_rate, cue_time, window_seconds):
    frame_seconds = HOP / sample_rate
    cue_start, cue_end = int(cue_time / frame_seconds), int((cue_time + window_seconds) / frame_seconds)
    near_start, near_end = max(0, int((cue_time - 3) / frame_seconds)), int((cue_time + window_seconds + 3) / frame_seconds)
    margins, cue_peaks = {}, {}
    for name, band in levels.items():
        around = numpy.concatenate([band[near_start:max(near_start, cue_start - 8)], band[cue_end + 8:near_end]])
        bed = numpy.percentile(around, 20) if len(around) else band.min()
        cue_peaks[name] = float(band[cue_start:cue_end + 1].max())
        margins[name] = cue_peaks[name] - float(bed)
    dominant = max(cue_peaks, key=cue_peaks.get)
    return margins, dominant


def find_onset_error_ms(samples, sample_rate, cue_time):
    window_start = max(0.0, cue_time - 0.5)
    clip = samples[int(window_start * sample_rate): int((cue_time + 0.5) * sample_rate)]
    if len(clip) < 2048:
        return None
    onsets = librosa.onset.onset_detect(y=clip, sr=sample_rate, hop_length=128, units="time", backtrack=True) + window_start
    if not len(onsets):
        return None
    nearest = onsets[numpy.argmin(numpy.abs(onsets - cue_time))]
    return float((nearest - cue_time) * 1000)


def main():
    library.lower_priority()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("audio")
    parser.add_argument("--expect", action="append", default=[], help='"label@seconds", repeatable')
    parser.add_argument("--window", type=float, default=1.0, help="seconds of sound after each expected time")
    arguments = parser.parse_args()
    expectations = [parse_expectation(text) for text in arguments.expect]

    sample_rate = library.CLAP_SAMPLE_RATE
    samples = library.load_mono(arguments.audio, sample_rate=sample_rate)
    duration = len(samples) / sample_rate
    print(f"file {arguments.audio}  {duration:.2f}s")
    print(f"whole file: integrated {library.integrated_loudness(samples, sample_rate):.1f} LUFS, "
          f"sample peak {library.to_db(numpy.abs(samples).max()):.1f} dBFS, true peak {library.true_peak_db(samples):.1f} dBTP")
    gaps = find_silence_gaps(samples, sample_rate)
    print("silence gaps (below -60 dBFS, 0.5 s+): " + (", ".join(f"{a:.2f}-{b:.2f}s" for a, b in gaps[:10]) or "none"))
    if not expectations:
        return

    clap = library.ClapBundle()
    problems = report_cues(samples, sample_rate, expectations, arguments.window, clap)
    clap.release()
    print(f"\n{problems} thing(s) to check across {len(expectations)} cue(s)")


def load_vocabulary():
    return [line.strip() for line in library.VOCABULARY_FILE.read_text(encoding="utf-8").splitlines() if line.strip()]


def report_cues(samples, sample_rate, expectations, window, clap, check_masking=True):
    """Prints the label, sync, level and masking check of each (label, seconds) cue; returns the number of problems.
    `check_masking=False` for a stem rendered alone: there is no bed in it to measure against."""
    vocabulary = load_vocabulary()
    levels = band_levels_db(samples, sample_rate)
    problems = 0
    for label, cue_time in expectations:
        start = max(0.0, cue_time - 0.1)
        clip = samples[int(start * sample_rate): int((cue_time + window) * sample_rate)]
        labels = [label] + vocabulary
        label_vectors = clap.embed_texts([f"the sound of {text}" for text in labels])
        similarity = label_vectors @ clap.embed_clips([clip])[0]
        vocabulary_order = numpy.argsort(-similarity[1:])[:3]
        expected_rank = int((similarity[1:] > similarity[0]).sum()) + 1
        top_three = ", ".join(f"{vocabulary[i]} ({similarity[1 + i]:.2f})" for i in vocabulary_order)
        heard = expected_rank <= PLAUSIBLE_RANK
        verdict = "OK" if expected_rank <= CLEAR_RANK else ("PLAUSIBLE" if heard else "CHECK")
        error_ms = find_onset_error_ms(samples, sample_rate, cue_time)
        margins, dominant = masking_margins(levels, sample_rate, cue_time, window)
        masked = check_masking and max(margins.values()) < MASKING_MARGIN_DB
        window_lufs = library.integrated_loudness(clip, sample_rate)
        window_rms = library.to_db(numpy.sqrt(numpy.mean(clip ** 2) + 1e-12))
        problems += (not heard) + masked + (error_ms is None or abs(error_ms) > 42)
        print(f'\ncue "{label}" at {cue_time:.2f}s')
        print(f"  hears: {verdict}  similarity {similarity[0]:.2f}, would rank {expected_rank} of "
              f"{len(vocabulary) + 1}; top 3 in vocabulary: {top_three}")
        print("  sync: " + ("no onset found within 0.5 s" if error_ms is None else f"onset {error_ms:+.0f} ms from expected"
              + ("" if abs(error_ms) <= 42 else "  CHECK (over one frame at 24 fps)")))
        print(f"  level: {window_rms:.1f} dBFS rms, {window_lufs:.1f} LUFS in the window")
        if not check_masking:
            continue
        print("  over the bed per band: " + ", ".join(f"{name} {value:+.1f} dB" for name, value in margins.items()))
        weak_note = "" if margins[dominant] >= MASKING_MARGIN_DB else f"; WEAK in its strongest band {dominant}"
        print(f"  masking: {'MASKED (under 6 dB in every band)' if masked else 'clear'}{weak_note} "
              f"(strongest band {dominant}, {margins[dominant]:+.1f} dB over the bed)")
    return problems


if __name__ == "__main__":
    main()
