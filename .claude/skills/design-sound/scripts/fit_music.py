"""Edit one produced music track to a film's cut: pick the segment, repeat or drop whole bars, join on downbeats,
stretch at most 4% to land a cue, end on a fade, then check the result's beat grid and joins.

Cues (JSON list): {"t": 10.0, "want": "downbeat|drop|silence|end"}. "silence" may carry "until": the music stops by t
(fading over its last bar) and a new edit enters on a downbeat at "until". "end" ends the music at t.

Run: uv run --no-project --python 3.12 --with numpy --with scipy --with librosa --with soundfile --with psutil
     python fit_music.py <track path> --duration 14.5 [--cues cues.json] --out music.wav [--report report.json]
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy
import soundfile

sys.path.insert(0, str(Path(__file__).parent))
import audio_tools as tools
import music_analysis
import sound_library as library

MAX_STRETCH = 0.04
JOIN_CROSSFADE_SECONDS = 0.04
ENTRY_FADE_SECONDS = 0.008
MAX_END_FADE_SECONDS = 2.5
MIN_DROP_RISE = 0.12
CLICK_RATIO_LIMIT = 2.5
KEY_WANTS = ("downbeat", "drop")


# ------------------------------------------------------------------ track facts

def load_track_record(track_path):
    """The indexed record of a track (tempo, downbeats, sections, energy), or a fresh analysis when it is not indexed."""
    normalized = library.normalize_path(track_path)
    records, _ = library.load_index()
    for record in records:
        if record["path"] == normalized and record.get("downbeats"):
            return record
    print("track is not in the index; analysing it now", flush=True)
    record = {"path": normalized, "name": Path(track_path).stem}
    record.update(music_analysis.analyse_music(track_path))
    record["duration"] = float(soundfile.info(track_path).duration)
    return record


def bar_table(record):
    """Bar start seconds (only bars that fit inside the file) and the mean energy of each bar."""
    bar_seconds = record["bar_seconds"]
    starts = numpy.array([start for start in record["downbeats"] if start + bar_seconds <= record["duration"] + 0.02])
    curve = numpy.array(record["energy"])
    times = numpy.arange(len(curve)) * record["energy_step"]
    energies = numpy.array([curve[(times >= start) & (times < start + bar_seconds)].mean()
                            if ((times >= start) & (times < start + bar_seconds)).any() else 0.0 for start in starts])
    return starts, energies


def section_bar_indices(record, starts):
    return sorted({int(numpy.argmin(numpy.abs(starts - section))) for section in record["sections"]} | {0})


def find_drop_bar(energies):
    """The bar where loudness jumps most against the two bars before it; None when nothing jumps."""
    best_bar, best_rise = None, 0.0
    for bar in range(1, len(energies)):
        before = energies[max(0, bar - 2):bar].mean()
        rise = energies[bar:bar + 2].mean() - before
        if rise > best_rise:
            best_bar, best_rise = bar, rise
    return (best_bar, best_rise) if best_rise >= MIN_DROP_RISE else (None, best_rise)


def refine_bar_starts(track_path, starts):
    """Move each downbeat to the strongest onset within 25 ms. A tracked grid is only that accurate; a cut that lands on
    the real attack keeps the beat where the listener hears it."""
    import librosa
    hop = 64
    samples, rate = librosa.load(track_path, sr=music_analysis.ANALYSIS_RATE, mono=True)
    envelope = librosa.onset.onset_strength(y=samples, sr=rate, hop_length=hop)
    span = int(0.025 * rate / hop)
    refined = []
    for start in starts:
        centre = int(round(start * rate / hop))
        first = max(0, centre - span)
        window = envelope[first:centre + span + 1]
        refined.append((first + int(numpy.argmax(window))) * hop / rate if len(window) else start)
    return numpy.array(refined)


def bar_features(track_path, starts, bar_seconds):
    """One normalised chroma + MFCC vector per bar, used to choose jumps that sound like the natural continuation."""
    import librosa
    samples, rate = librosa.load(track_path, sr=music_analysis.ANALYSIS_RATE, mono=True)
    chroma = librosa.feature.chroma_stft(y=samples, sr=rate, hop_length=music_analysis.HOP)
    mfcc = librosa.feature.mfcc(y=samples, sr=rate, hop_length=music_analysis.HOP, n_mfcc=13)
    frames = numpy.vstack([chroma, mfcc / 20.0])
    rows = []
    for start in starts:
        first = int(start * rate / music_analysis.HOP)
        last = max(first + 1, int((start + bar_seconds) * rate / music_analysis.HOP))
        rows.append(frames[:, first:last].mean(axis=1))
    rows = numpy.array(rows)
    return (rows - rows.mean(axis=0)) / (rows.std(axis=0) + 1e-9)


# ------------------------------------------------------------------ choosing bars

class BarPlanner:
    def __init__(self, track_path, record):
        self.track_path = track_path
        self.record = record
        self.starts, self.energies = bar_table(record)
        if not record.get("constant_tempo"):
            self.starts = refine_bar_starts(track_path, self.starts)
        self.bar_count = len(self.starts)
        self.sections = section_bar_indices(record, self.starts)
        self.features = None

    def feature_distance(self, first_bar, second_bar):
        if self.features is None:
            self.features = bar_features(self.track_path, self.starts, self.record["bar_seconds"])
        return float(numpy.linalg.norm(self.features[first_bar] - self.features[second_bar]))

    def best_jump_target(self, last_bar):
        """Where to go after `last_bar` when the track runs out: the earlier bar that best follows the end of it."""
        candidates = [bar for bar in range(1, last_bar - 2)]
        if not candidates:
            return 0
        def cost(bar):
            return self.feature_distance(bar - 1, last_bar) - (0.5 if bar in self.sections else 0.0)
        return min(candidates, key=cost)

    def continue_to(self, sequence, total):
        """Append bars after `sequence` until it holds `total`; at the end of the track jump back by best match."""
        sequence = list(sequence)
        while len(sequence) < total:
            following = sequence[-1] + 1
            sequence.append(following if following < self.bar_count else self.best_jump_target(sequence[-1]))
        return sequence

    def lead_in(self, anchor_bar, count):
        """`count` bars ending just before `anchor_bar`; repeats the last bars of the track's lead-in when it is short."""
        if count <= anchor_bar:
            return list(range(anchor_bar - count, anchor_bar))
        cycle_length = min(anchor_bar, 4) or 1
        cycle = list(range(anchor_bar - cycle_length, anchor_bar)) if anchor_bar else [0]
        repeated = cycle * (count // len(cycle) + 1)
        return repeated[len(repeated) - count:]

    def free_window(self, count):
        """Best start bar for `count` bars with no anchor: stationary, mid energy, ending on a phrase end."""
        best_start, best_score = 0, -1e9
        for start in self.sections:
            if start + count > self.bar_count:
                continue
            window = self.energies[start:start + count]
            ends_on_phrase = (start + count in self.sections) or (start + count == self.bar_count)
            score = (1.0 if ends_on_phrase else 0.0) - 2.0 * float(window.std()) - abs(float(window.mean()) - 0.55)
            if score > best_score:
                best_start, best_score = start, score
        return best_start

    def anchor_bar(self, want, lead_bars, after_bars):
        """Source bar that must land on the cue: the biggest drop, or the section start that suits best."""
        drop_bar, rise = find_drop_bar(self.energies)
        if want == "drop" and drop_bar is not None:
            return drop_bar, f"drop (+{rise:.2f} energy)"
        def fit(bar):
            rise_here = self.energies[bar:bar + 2].mean() - self.energies[max(0, bar - 2):bar].mean() if bar else 0.0
            lead_ok = bar >= lead_bars
            tail_ok = bar + after_bars <= self.bar_count
            return (lead_ok + tail_ok) + rise_here
        return max(self.sections, key=fit), "section start"

    def plan(self, bar_count, key_want, key_bar_index):
        """Source bar numbers for the part, in order, and a description of the anchor."""
        if key_want is None:
            start = self.free_window(bar_count)
            return self.continue_to(list(range(start, min(start + bar_count, self.bar_count))), bar_count), "free window"
        anchor, how = self.anchor_bar(key_want, key_bar_index, bar_count - key_bar_index)
        lead = self.lead_in(anchor, key_bar_index)
        return self.continue_to(lead + [anchor], bar_count), how


# ------------------------------------------------------------------ audio assembly

def slice_with_padding(audio, first, last):
    first_pad = max(0, -first)
    last_pad = max(0, last - len(audio))
    piece = audio[max(0, first):min(len(audio), last)]
    return numpy.pad(piece, ((first_pad, last_pad), (0, 0)))


def runs_of(sequence):
    runs = [[sequence[0]]]
    for bar in sequence[1:]:
        if bar == runs[-1][-1] + 1:
            runs[-1].append(bar)
        else:
            runs.append([bar])
    return runs


def assemble(source, starts, bar_seconds, sequence):
    """Join the runs of consecutive bars; only a real jump gets an equal-power crossfade centred on the join.

    Returns (audio, joins) where joins are {"at_bar", "from_bar", "to_bar"} entries (at_bar counts bars in the output).
    """
    rate = tools.RATE
    half = int(JOIN_CROSSFADE_SECONDS * rate / 2)
    def sample_of(bar):
        return int(round((starts[bar] if bar < len(starts) else starts[-1] + bar_seconds) * rate))
    output, joins, bars_so_far = None, [], 0
    for run in runs_of(sequence):
        first, last = sample_of(run[0]), sample_of(run[-1] + 1)
        if output is None:
            output = source[first:last]
        else:
            fade = numpy.linspace(0, numpy.pi / 2, 2 * half)[:, None]
            previous = slice_with_padding(source, sample_of(joins_end) - half, sample_of(joins_end) + half)
            following = slice_with_padding(source, first - half, first + half)
            blended = previous * numpy.cos(fade) + following * numpy.sin(fade)
            output = numpy.concatenate([output[:-half], blended, source[first + half:last]])
            joins.append({"at_bar": bars_so_far, "from_bar": int(joins_end - 1), "to_bar": int(run[0])})
        joins_end = run[-1] + 1
        bars_so_far += len(run)
    return output, joins


def time_stretch(audio, rate_factor):
    """Tempo change by `rate_factor` (above 1 is faster) through ffmpeg's atempo; a few percent is inaudible."""
    if abs(rate_factor - 1.0) < 0.0005:
        return audio
    with tempfile.TemporaryDirectory() as folder:
        source_path, target_path = Path(folder) / "in.wav", Path(folder) / "out.wav"
        soundfile.write(str(source_path), audio, tools.RATE, subtype="FLOAT")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(source_path), "-filter:a",
                        f"atempo={rate_factor:.6f}", str(target_path)], check=True)
        stretched, _ = soundfile.read(str(target_path), dtype="float32", always_2d=True)
    return stretched


def fit_length(audio, samples):
    return audio[:samples] if len(audio) >= samples else numpy.pad(audio, ((0, samples - len(audio)), (0, 0)))


def end_fade_seconds(bar_seconds_out, part_seconds):
    return min(bar_seconds_out, MAX_END_FADE_SECONDS, part_seconds)


# ------------------------------------------------------------------ one part (one edit)

def render_part(planner, source, part, track_seconds_per_bar):
    """Render one contiguous stretch of music of `part["length"]` seconds. Returns (audio, facts)."""
    length, key = part["length"], part.get("key")
    nominal = track_seconds_per_bar
    if key is not None and key["seconds_in"] > 0.5 * nominal:
        key_bar_index = max(1, int(round(key["seconds_in"] / nominal)))
        wanted_stretch = key["seconds_in"] / (key_bar_index * nominal)
    else:
        key_bar_index = 0
        wanted_stretch = length / (max(1, round(length / nominal)) * nominal)
    stretch = float(numpy.clip(wanted_stretch, 1 - MAX_STRETCH, 1 + MAX_STRETCH))
    bar_seconds_out = nominal * stretch
    bar_count = int(numpy.ceil(length / bar_seconds_out - 1e-6))
    key_want = key["want"] if key is not None else None
    sequence, anchor_note = planner.plan(bar_count, key_want, key_bar_index)
    audio, joins = assemble(source, planner.starts, nominal, sequence)
    audio = fit_length(time_stretch(audio, 1.0 / stretch), int(round(length * tools.RATE)))
    reaches_track_end = sequence[-1] >= planner.bar_count - 1 and planner.energies[-1] < 0.3
    fade = 0.0 if reaches_track_end else end_fade_seconds(bar_seconds_out, length)
    audio = tools.fade(audio, in_seconds=ENTRY_FADE_SECONDS, out_seconds=fade)
    facts = {"start": part["start"], "length": length, "source_bars": sequence, "anchor": anchor_note,
             "stretch_percent": round((stretch - 1) * 100, 2), "bar_seconds_out": round(bar_seconds_out, 4),
             "wanted_stretch_percent": round((wanted_stretch - 1) * 100, 2),
             "end": "natural ending of the track" if reaches_track_end else f"fade over {fade:.2f} s",
             "joins": [dict(join, at_seconds=round(part["start"] + join["at_bar"] * bar_seconds_out, 3))
                       for join in joins]}
    return audio, facts


# ------------------------------------------------------------------ cues to parts

def split_into_parts(cues, duration):
    """Silence cues cut the film into parts; each part keeps the first downbeat/drop cue that falls inside it."""
    parts, start = [], 0.0
    for cue in sorted((cue for cue in cues if cue["want"] == "silence"), key=lambda cue: cue["t"]):
        parts.append({"start": start, "end": cue["t"]})
        start = cue.get("until", cue["t"])
    end_cues = [cue["t"] for cue in cues if cue["want"] == "end"]
    parts.append({"start": start, "end": min([duration] + end_cues)})
    for part in parts:
        part["length"] = part["end"] - part["start"]
        inside = [cue for cue in cues if cue["want"] in KEY_WANTS and part["start"] <= cue["t"] < part["end"]]
        part["key"] = {"want": inside[0]["want"], "seconds_in": inside[0]["t"] - part["start"]} if inside else None
    return [part for part in parts if part["length"] > 0.5]


# ------------------------------------------------------------------ self check

def onset_envelope(mono, rate):
    import librosa
    hop = 128
    envelope = librosa.onset.onset_strength(y=mono, sr=rate, hop_length=hop)
    return envelope, hop


def grid_phase(envelope, hop, rate, period, first, last):
    """Phase (seconds into a beat) at which a regular grid of this period best hits the onsets in [first, last]."""
    frame_times = numpy.arange(len(envelope)) * hop / rate
    best_phase, best_score, scores = 0.0, -1.0, []
    for phase in numpy.arange(0, period, 0.002):
        grid = numpy.arange(first + phase, last, period)
        score = float(numpy.interp(grid, frame_times, envelope).sum()) if len(grid) else 0.0
        scores.append(score)
        if score > best_score:
            best_phase, best_score = float(phase), score
    confidence = best_score / (numpy.mean(scores) + 1e-9)
    return best_phase, confidence


def wrapped_ms(difference, period):
    return ((difference + period / 2) % period - period / 2) * 1000


def drift_at(envelope, hop, rate, period, centre, span):
    before, confidence_before = grid_phase(envelope, hop, rate, period, centre - span, centre)
    after, confidence_after = grid_phase(envelope, hop, rate, period, centre, centre + span)
    # Both grids are read at absolute times: phase is relative to each window's own start.
    offset_before = (centre - span + before) % period
    offset_after = (centre + after) % period
    return wrapped_ms(offset_after - offset_before, period), min(confidence_before, confidence_after)


def click_ratio(mono, rate, at_seconds):
    """Largest sample-to-sample step within 3 ms of a join against the 99th percentile step in the 400 ms around it."""
    centre = int(at_seconds * rate)
    wide = numpy.abs(numpy.diff(mono[max(0, centre - int(0.2 * rate)):centre + int(0.2 * rate)]))
    narrow = numpy.abs(numpy.diff(mono[max(0, centre - int(0.003 * rate)):centre + int(0.003 * rate)]))
    return float(narrow.max() / (numpy.percentile(wide, 99) + 1e-9)) if len(wide) and len(narrow) else 0.0


def cue_onset_error_ms(mono, rate, cue_seconds):
    """Offset of the strongest onset within 150 ms of the cue time (positive means late)."""
    import librosa
    hop = 64
    envelope = librosa.onset.onset_strength(y=mono, sr=rate, hop_length=hop)
    centre, span = int(cue_seconds * rate / hop), int(0.15 * rate / hop)
    window = envelope[max(0, centre - span):centre + span]
    peak = int(numpy.argmax(window)) + max(0, centre - span)
    return round((peak - centre) * hop / rate * 1000, 1)


def check_output(timeline, part_facts, cues):
    import librosa
    mono = timeline.mean(axis=1)
    analysis_rate = 22050
    mono_analysis = librosa.resample(mono, orig_sr=tools.RATE, target_sr=analysis_rate)
    envelope, hop = onset_envelope(mono_analysis, analysis_rate)
    checks = {"joins": [], "parts": [], "cues": []}
    for facts in part_facts:
        beat_period = facts["bar_seconds_out"] / facts["beats_per_bar"]
        span = min(2 * facts["bar_seconds_out"], facts["length"] / 2)
        points = [(join["at_seconds"], "join") for join in facts["joins"]]
        if not points:
            points = [(facts["start"] + facts["length"] / 2, "mid-part (no joins)")]
        for at_seconds, label in points:
            drift, confidence = drift_at(envelope, hop, analysis_rate, beat_period, at_seconds, span)
            entry = {"at_seconds": round(at_seconds, 3), "where": label, "drift_ms": round(drift, 1),
                     "grid_confidence": round(confidence, 2),
                     "click_ratio": round(click_ratio(mono, tools.RATE, at_seconds), 2)}
            entry["verdict"] = "ok" if abs(drift) <= 20 and entry["click_ratio"] <= CLICK_RATIO_LIMIT else "check"
            checks["joins"].append(entry)
        first, last = int(facts["start"] * tools.RATE), int((facts["start"] + facts["length"]) * tools.RATE)
        tempo, _ = librosa.beat.beat_track(y=mono[first:last], sr=tools.RATE, start_bpm=60 / beat_period)
        checks["parts"].append({"start": facts["start"], "expected_bpm": round(60 / beat_period, 1),
                                "tracked_bpm": round(float(numpy.atleast_1d(tempo)[0]), 1)})
    for cue in cues:
        if cue["want"] in KEY_WANTS:
            checks["cues"].append({"t": cue["t"], "want": cue["want"],
                                   "onset_error_ms": cue_onset_error_ms(mono, tools.RATE, cue["t"])})
    return checks


# ------------------------------------------------------------------ main

def fit_music(track_path, duration, cues):
    record = load_track_record(track_path)
    planner = BarPlanner(track_path, record)
    source = tools.read_stereo(track_path)
    timeline = numpy.zeros((int(round(duration * tools.RATE)), 2), dtype=numpy.float32)
    part_facts = []
    for part in split_into_parts(cues, duration):
        audio, facts = render_part(planner, source, part, record["bar_seconds"])
        facts["beats_per_bar"] = record["beats_per_bar"]
        timeline = tools.add_at(timeline, audio, int(round(part["start"] * tools.RATE)))[:len(timeline)]
        part_facts.append(facts)
    report = {"track": record["path"], "track_bpm": record["bpm"], "bar_seconds": record["bar_seconds"],
              "constant_tempo": record.get("constant_tempo"), "duration": duration, "parts": part_facts}
    report["checks"] = check_output(timeline, part_facts, cues)
    return timeline, report


def main():
    library.lower_priority()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("track")
    parser.add_argument("--duration", type=float, required=True)
    parser.add_argument("--cues", help="JSON file: [{\"t\": 10.0, \"want\": \"downbeat\"}, ...]")
    parser.add_argument("--out", required=True)
    parser.add_argument("--report")
    arguments = parser.parse_args()
    cues = json.loads(Path(arguments.cues).read_text(encoding="utf-8")) if arguments.cues else []
    timeline, report = fit_music(arguments.track, arguments.duration, cues)
    tools.write_wav(arguments.out, timeline)
    report_path = Path(arguments.report) if arguments.report else Path(arguments.out).with_suffix(".report.json")
    report_path.write_text(json.dumps(report, indent=1), encoding="utf-8")
    print(json.dumps(report["checks"], indent=1))
    print(f"wrote {arguments.out} and {report_path}")


if __name__ == "__main__":
    main()
