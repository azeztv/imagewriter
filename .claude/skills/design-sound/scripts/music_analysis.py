"""Music structure for the library: tempo, beat grid, downbeats, sections, energy curve, CLAP windows.

Used by index.py (to store it) and fit_music.py (to edit a track to a cut). Needs numpy, scipy, librosa, soundfile.
"""
import numpy

ANALYSIS_RATE = 22050
HOP = 512
ENERGY_STEP_SECONDS = 0.5
MAX_ANALYSIS_SECONDS = 480
SECTION_TARGET_SECONDS = 28
GRID_RESIDUAL_LIMIT_MS = 25
WINDOW_SECONDS = 10
MAX_WINDOWS = 8
MIN_WINDOWS = 3


def window_starts_for(duration):
    """Start seconds of the CLAP windows: evenly spread 10 s clips, about one per 20 s of music."""
    count = int(min(MAX_WINDOWS, max(MIN_WINDOWS, round(duration / 20))))
    last_start = max(0.0, duration - WINDOW_SECONDS)
    return [round(float(start), 2) for start in numpy.linspace(0, last_start, count)]


def pick_tempo(samples, hint_bpm):
    import librosa
    onset_envelope = librosa.onset.onset_strength(y=samples, sr=ANALYSIS_RATE, hop_length=HOP)
    start_bpm = hint_bpm if hint_bpm else 120.0
    tempo, beat_frames = librosa.beat.beat_track(onset_envelope=onset_envelope, sr=ANALYSIS_RATE, hop_length=HOP,
                                                 start_bpm=start_bpm, tightness=200)
    tempo = float(numpy.atleast_1d(tempo)[0])
    beat_times = librosa.frames_to_time(beat_frames, sr=ANALYSIS_RATE, hop_length=HOP)
    return tempo, beat_times, onset_envelope


def fit_constant_grid(beat_times):
    """Least-squares line through the beats. Returns (offset, period, worst residual in ms)."""
    indices = numpy.arange(len(beat_times))
    period, offset = numpy.polyfit(indices, beat_times, 1)
    for _ in range(2):  # refit without the beats the tracker placed badly
        close = numpy.abs(beat_times - (offset + period * indices)) < 0.04
        if close.sum() >= 8:
            period, offset = numpy.polyfit(indices[close], beat_times[close], 1)
    residual_ms = float(numpy.percentile(numpy.abs(beat_times - (offset + period * indices)), 95) * 1000)
    return float(offset), float(period), residual_ms


def beat_synchronous_features(samples, beat_times):
    import librosa
    chroma = librosa.feature.chroma_cqt(y=samples, sr=ANALYSIS_RATE, hop_length=HOP)
    frames = librosa.time_to_frames(beat_times, sr=ANALYSIS_RATE, hop_length=HOP)
    frames = numpy.clip(frames, 0, chroma.shape[1] - 1)
    return librosa.util.sync(chroma, frames, aggregate=numpy.median), chroma


def beats_per_bar_and_phase(beat_times, onset_envelope, chroma_sync):
    """Pick 3 or 4 beats per bar and which beat is the downbeat, from onset strength and harmonic change at each beat."""
    import librosa
    frames = numpy.clip(librosa.time_to_frames(beat_times, sr=ANALYSIS_RATE, hop_length=HOP), 0, len(onset_envelope) - 1)
    onset_at_beat = onset_envelope[frames]
    chroma_change = numpy.linalg.norm(numpy.diff(chroma_sync, axis=1, prepend=chroma_sync[:, :1]), axis=0)
    chroma_change = chroma_change[: len(beat_times)] if len(chroma_change) >= len(beat_times) else \
        numpy.pad(chroma_change, (0, len(beat_times) - len(chroma_change)))

    def standardise(values):
        return (values - values.mean()) / (values.std() + 1e-9)

    novelty = standardise(onset_at_beat) + standardise(chroma_change)
    best = {}
    for beats_per_bar in (3, 4):
        scores = [novelty[phase::beats_per_bar].mean() for phase in range(beats_per_bar)]
        best[beats_per_bar] = (int(numpy.argmax(scores)), float(max(scores)) - float(numpy.mean(scores)))
    beats_per_bar = 3 if best[3][1] > best[4][1] * 1.3 else 4
    return beats_per_bar, best[beats_per_bar][0]


def find_sections(samples, beat_times, downbeat_times, duration):
    """Section starts from agglomerative clustering of beat-synchronous chroma and MFCC, snapped to downbeats."""
    import librosa
    if len(beat_times) < 16 or len(downbeat_times) < 4:
        return [0.0]
    mfcc = librosa.feature.mfcc(y=samples, sr=ANALYSIS_RATE, hop_length=HOP, n_mfcc=13)
    frames = numpy.clip(librosa.time_to_frames(beat_times, sr=ANALYSIS_RATE, hop_length=HOP), 0, mfcc.shape[1] - 1)
    features = librosa.util.sync(librosa.util.normalize(mfcc, axis=1), frames, aggregate=numpy.mean)
    segment_count = int(max(2, min(len(beat_times) // 8, round(duration / SECTION_TARGET_SECONDS))))
    boundary_beats = librosa.segment.agglomerative(features, segment_count)
    boundary_times = [float(beat_times[min(index, len(beat_times) - 1)]) for index in boundary_beats]
    snapped = {float(downbeat_times[int(numpy.argmin(numpy.abs(downbeat_times - time)))]) for time in boundary_times}
    return sorted(snapped | {float(downbeat_times[0])})


def energy_curve(samples):
    """Loudness per ENERGY_STEP_SECONDS, scaled so the loudest step is 1.0 and -40 dB below it is 0.0."""
    import librosa
    step = int(ANALYSIS_RATE * ENERGY_STEP_SECONDS)
    rms = librosa.feature.rms(y=samples, frame_length=step * 2, hop_length=step, center=True)[0]
    decibels = 20 * numpy.log10(rms + 1e-9)
    return numpy.clip((decibels - (decibels.max() - 40)) / 40, 0, 1)


def analyse_music(path, hint_bpm=None):
    """Everything the index stores about a track except its CLAP vectors. Times are in seconds."""
    import librosa
    samples, _ = librosa.load(path, sr=ANALYSIS_RATE, mono=True, duration=MAX_ANALYSIS_SECONDS)
    duration = float(librosa.get_duration(path=str(path)))
    tempo, beat_times, onset_envelope = pick_tempo(samples, hint_bpm)
    chroma_sync, _ = beat_synchronous_features(samples, beat_times)
    beats_per_bar, phase = beats_per_bar_and_phase(beat_times, onset_envelope, chroma_sync)
    offset, period, residual_ms = fit_constant_grid(beat_times)
    constant = residual_ms <= GRID_RESIDUAL_LIMIT_MS
    if constant:
        beat_count = int((duration - offset) / period)
        beat_times = offset + period * numpy.arange(beat_count)
    downbeat_times = beat_times[phase::beats_per_bar]
    sections = find_sections(samples, beat_times, downbeat_times, duration)
    energy = energy_curve(samples)
    return {
        "bpm": round(60.0 / period if constant else tempo, 2),
        "beats_per_bar": beats_per_bar,
        "bar_seconds": round(float(numpy.median(numpy.diff(downbeat_times))) if len(downbeat_times) > 1 else 0.0, 4),
        "constant_tempo": bool(constant),
        "grid_residual_ms": round(residual_ms, 1),
        "beats": [round(float(time), 3) for time in beat_times],
        "downbeats": [round(float(time), 3) for time in downbeat_times],
        "sections": [round(float(time), 2) for time in sections],
        "energy_step": ENERGY_STEP_SECONDS,
        "energy": [round(float(value), 3) for value in energy],
    }
