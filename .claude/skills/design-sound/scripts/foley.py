"""Foley stem from an event list: each event becomes layered real recordings picked by the library search.

Run: uv run --no-project --python 3.12 --with numpy --with scipy --with librosa --with soundfile --with pyloudnorm
     --with psutil --with torch --with transformers python foley.py events.json --out stem.wav [--report report.csv]
Event fields: t, what, material, other_material, mass_kg, speed_mps, x (-1..1), distance_m, intensity (0..1), seed,
duration_s (rolls, scrapes), query (replaces the body query). Layers, size and distance rules: references/foley.md.
"""
import argparse
import csv
import json
import sys
from pathlib import Path

import numpy

sys.path.insert(0, str(Path(__file__).parent))
import audio_tools as tools
import sound_library as library

SUSTAINED = {"roll", "scrape", "slide", "drag"}  # one long layer, aligned on its first sound
SLICED = {"footstep", "step", "walk", "knock", "tap"}  # a recording of several hits is cut into single hits
BREAKS = {"break", "shatter", "smash"}
NO_TAIL = {"slam", "click", "close", "latch"}  # nothing scatters or settles after these
IMPACT_KINDS = BREAKS | {"slam", "impact", "drop", "hit", "explode", "explosion", "crash", "land"}
MAX_PAN = 0.75  # off-screen effects at 50-75% pan, extremes saved for dramatic moments (sound designer practice)
# Mass the recordings usually carry, so pitch only moves when the event is heavier or lighter than that.
TYPICAL_MASS_KG = {"footstep": 70, "step": 70, "walk": 70, "slam": 30, "drop": 5, "break": 0.5, "shatter": 0.5,
                   "smash": 0.5, "roll": 2}
DEFAULT_TYPICAL_MASS_KG = 2.0
LAYER_GAIN_DB = {"transient": 0.0, "body": -3.0, "tail": -8.0}
POOL_SIZE = 12
POOL_SCORE_RATIO = 0.6  # a fallback candidate must score at least this share of the best one
ONSET_FLAG_MS = 42  # one frame at 24 fps
SOFT_TOP_HZ = 8000  # house rule: gentle top, no shrill build-up
LEAD_IN_SECONDS = 0.015  # sound kept before the aligned attack; anything earlier is cut so nothing plays ahead of the cue


class Unit:
    """One usable recording: a whole file, or one hit cut out of a multi-hit file."""

    def __init__(self, path, segment, audio):
        self.path, self.segment, self.audio = path, segment, audio
        self.key = (path, segment)

    @property
    def name(self):
        return Path(self.path).name + ("" if self.segment is None else f"#{self.segment}")


class Pool:
    """Ranks candidates once per query, loads them lazily and hands each recording out once."""

    def __init__(self, records, vectors, clap, licence):
        self.records, self.vectors, self.clap, self.licence = records, vectors, clap, licence
        self.used = set()
        self.cache = {}

    def candidates(self, query, focus_word, kind, max_seconds, sliced):
        cache_key = (query, focus_word, kind, max_seconds, sliced)
        if cache_key not in self.cache:
            query_vector = self.clap.query_vector(query, library.QUERY_TEMPLATES_ENSEMBLE)
            rows, _, scores, _, _ = library.rank_sounds(self.records, self.vectors, query_vector, query, kind,
                                                        self.licence, max_seconds, POOL_SIZE)
            focus = library.split_words(focus_word or "")
            matching = [row for row in rows if focus and set(focus) & set(self.records[row]["tags"])]
            others = [row for row in rows if row not in matching and scores[row] >= POOL_SCORE_RATIO * scores[rows[0]]]
            units = []
            for row in matching + others:
                units += self.units_of(self.records[row]["path"], sliced)
            self.cache[cache_key] = units
        return self.cache[cache_key]

    def pinned(self, paths):
        """An event's own recordings (`files`), each one whole: for a sound set chosen by hand, such as a game's
        variants of one action, where search would wander off the set."""
        cache_key = ("files",) + tuple(paths)
        if cache_key not in self.cache:
            units = []
            for path in paths:
                units += self.units_of(path, False)
            self.cache[cache_key] = units
        return self.cache[cache_key]

    def units_of(self, path, sliced):
        audio = library.load_mono(path, sample_rate=tools.RATE)
        if not sliced:
            return [Unit(path, None, audio)]
        import librosa
        onsets = librosa.onset.onset_detect(y=audio, sr=tools.RATE, hop_length=128, units="samples", backtrack=True)
        if len(onsets) < 2:
            return [Unit(path, None, audio)]
        lead = int(0.01 * tools.RATE)
        edges = [max(0, int(onset) - lead) for onset in onsets] + [len(audio)]
        peak = float(numpy.abs(audio).max())
        units = []
        for index in range(len(onsets)):
            segment = audio[edges[index]: min(edges[index + 1], edges[index] + int(0.7 * tools.RATE))]
            if len(segment) >= int(0.06 * tools.RATE) and numpy.abs(segment).max() >= 0.2 * peak:
                units.append(Unit(path, index, segment))
        return units or [Unit(path, None, audio)]

    def take(self, units, rng, vary):
        """Rotates: the best unused recording (`vary`: one of the best three, for repeated hits such as steps);
        once all are used, any one, flagged as reused."""
        unused = [unit for unit in units if unit.key not in self.used]
        if unused:
            unit = unused[int(rng.integers(0, min(3, len(unused)))) if vary else 0]
            self.used.add(unit.key)
            return unit, False
        return units[int(rng.integers(0, len(units)))], True


# ---------------------------------------------------------------- event to layers

def layer_names(event):
    what, intensity = event["what"], event["intensity"]
    if what in SUSTAINED:
        return ["body"]
    if what in SLICED:
        return ["body"] + (["tail"] if intensity > 0.6 else [])
    count = 3 if what in BREAKS else (1 if intensity < 0.3 else 2 if intensity < 0.65 else 3)
    if what in NO_TAIL:
        count = min(count, 2)
    return ["body"] if count == 1 else ["transient", "body", "tail"][:count]


def layer_query(event, layer):
    what, material, other = event["what"], event["material"], event.get("other_material")
    if layer == "tail":
        return (f"{material} shards falling debris" if what in BREAKS else f"{other or material} debris rattle settling"), \
            (other or material), None, 6
    if event.get("query") and layer == "body":
        base = event["query"]
    elif what in SLICED:
        base = f"{what} on {material}" if what in {"footstep", "step", "walk"} else f"{material} {what}"
    elif what in {"drop", "dropped"}:
        base = f"{material} dropped on {other}" if other else f"{material} dropped"
    elif what in BREAKS:
        base = f"{material} breaking"
    elif what in SUSTAINED:
        base = f"{material} {what}ing" if what in {"roll", "scrape"} else f"{material} {what}"
    else:
        base = f"{material} on {other} {what}" if other else f"{material} {what}"
    if layer == "transient":
        return base + " sharp hit", material, "oneshot", 3
    return base, material, None, (14 if what in SUSTAINED else 6)


def event_gain_db(event):
    gain = -20 + 16 * event["intensity"]
    if event.get("speed_mps"):
        gain += 3 * float(numpy.clip(numpy.log2(event["speed_mps"] / 2.0), -2, 2))
    distance = event.get("distance_m", 0) or 0
    return gain - min(18.0, 3.5 * numpy.log2(max(distance, 2.0) / 2.0))


def mass_shift_and_cutoff(event):
    mass = event.get("mass_kg")
    if not mass:
        return 0.0, 16000.0
    ratio = mass / TYPICAL_MASS_KG.get(event["what"], DEFAULT_TYPICAL_MASS_KG)
    shift = float(numpy.clip(-1.0 * numpy.log2(ratio), -6, 6))
    cutoff = float(numpy.clip(14000 * ratio ** -0.15, 3000, 16000))
    return shift, cutoff


def distance_cutoff(event, cutoff):
    distance = event.get("distance_m", 0) or 0
    return float(max(1800.0, min(cutoff, SOFT_TOP_HZ, 16000 / (1 + distance / 6))))


def render_layer(event, layer, unit, reused, rng):
    """Returns (mono audio, attack sample index, delay seconds, notes) for one layer."""
    shift, cutoff = mass_shift_and_cutoff(event)
    cutoff = distance_cutoff(event, cutoff)
    shift += float(rng.uniform(-0.4, 0.4))
    notes = []
    if reused:
        shift += float(rng.choice([-1, 1]) * rng.uniform(1.0, 2.5))
        notes.append("reused, pitch varied")
    audio = tools.repitch(unit.audio, shift)
    sustained = event["what"] in SUSTAINED
    attack = tools.first_onset_index(audio) if sustained else tools.main_attack_index(audio)
    trim = max(0, attack - int(LEAD_IN_SECONDS * tools.RATE))
    audio, attack = tools.fade(audio[trim:], in_seconds=0.005 if trim else 0), attack - trim

    after_attack = int({"transient": 0.2, "body": event.get("duration_s") or (3.0 if sustained else 2.5), "tail": 3.0}[layer]
                       * tools.RATE)
    audio = audio[: attack + after_attack]
    fade_out = {"transient": 0.06, "body": 0.1 if sustained else 0.25, "tail": 0.5}[layer]
    audio = tools.fade(audio, out_seconds=fade_out)
    if layer == "transient":
        audio = tools.highpass(audio, 300)
    if layer == "tail":
        audio = tools.highpass(audio, 200)
    audio = tools.lowpass(audio, cutoff)

    delay = 0.0
    gain_db = event_gain_db(event) + LAYER_GAIN_DB[layer] + float(rng.uniform(-1, 1))
    if layer == "tail":
        distance = event.get("distance_m", 0) or 0
        delay = 0.025 + min(0.25, 0.006 * distance) + float(rng.uniform(0, 0.03))
        gain_db -= 3 * min(distance, 50) / 50
        audio = tools.fade(audio, in_seconds=0.02)
    peak = float(numpy.abs(audio).max()) or 1.0
    audio = audio / peak * tools.db_to_gain(gain_db)
    notes.append(f"{shift:+.1f}st lp{cutoff:.0f}Hz {gain_db:+.1f}dB")
    return audio.astype(numpy.float32), attack, delay, "; ".join(notes)


def layer_pan(event, layer):
    """Follow the picture, but never past 75% (extremes pull the eye off the action), and keep the weight of an
    impact near the centre: the transient carries the position, an impact's body and tail sit at half of it."""
    position = float(numpy.clip(event.get("x", 0.0), -MAX_PAN, MAX_PAN))
    if layer != "transient" and event["what"] in IMPACT_KINDS:
        return position * 0.5
    return position


def render_event(event, index, pool, stem, global_seed):
    rng = numpy.random.default_rng([global_seed, int(event.get("seed", index))])
    placed, chosen = [], []
    pinned_files = event.get("files")
    for layer in (["body"] if pinned_files else layer_names(event)):
        query, focus, kind, max_seconds = layer_query(event, layer)
        if pinned_files:
            query = "files: " + ", ".join(Path(path).name for path in pinned_files)
            units = pool.pinned(pinned_files)
        else:
            units = pool.candidates(query, focus, kind, max_seconds, event["what"] in SLICED and layer == "body")
        if not units:
            chosen.append(f"{layer}: NO CANDIDATE for '{query}'")
            continue
        unit, reused = pool.take(units, rng, vary=bool(pinned_files) or event["what"] in SLICED)
        audio, attack, delay, notes = render_layer(event, layer, unit, reused, rng)
        start = int(round((event["t"] + delay) * tools.RATE)) - attack
        placed.append((start, tools.pan_stereo(audio, layer_pan(event, layer))))
        chosen.append(f"{layer}: {unit.name} [{notes}]")
    if not placed:
        return stem, chosen, None
    begin = max(0, min(start for start, _ in placed))
    event_buffer = numpy.zeros((0, 2), dtype=numpy.float32)
    for start, audio in placed:
        event_buffer = tools.add_at(event_buffer, audio, start - begin)
        stem = tools.add_at(stem, audio, start)
    onset = begin / tools.RATE + tools.measured_onset_seconds(event_buffer.sum(axis=1))
    return stem, chosen, (onset - event["t"]) * 1000


def normalise_event(raw, index):
    event = {"intensity": 0.6, "x": 0.0, "material": "", **raw}
    for field in ("t", "what"):
        if field not in event:
            raise SystemExit(f"event {index} lacks '{field}'")
    event["intensity"] = float(numpy.clip(event["intensity"], 0, 1))
    return event


def main():
    library.lower_priority()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("events")
    parser.add_argument("--out", required=True)
    parser.add_argument("--report")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--licence", choices=["cc0", "public", "any"], default="any",
                        help="any (default) uses every recording and warns; public = cc0, cc-by, ElevenLabs only")
    parser.add_argument("--seconds", type=float, help="stem length (default: last event + 3 s)")
    arguments = parser.parse_args()

    data = json.loads(Path(arguments.events).read_text(encoding="utf-8"))
    events = [normalise_event(raw, index) for index, raw in enumerate(data["events"] if isinstance(data, dict) else data)]
    records, vectors = library.load_index()
    clap = library.ClapBundle()
    pool = Pool(records, vectors, clap, arguments.licence)

    length = int((arguments.seconds or max(event["t"] for event in events) + 3) * tools.RATE)
    stem = numpy.zeros((length, 2), dtype=numpy.float32)
    rows = []
    for index, event in sorted(enumerate(events), key=lambda pair: pair[1]["t"]):
        stem, chosen, error_ms = render_event(event, index, pool, stem, arguments.seed)
        rows.append({"index": index, "t": event["t"], "what": event["what"], "material": event["material"],
                     "layers": " | ".join(chosen), "onset_error_ms": "" if error_ms is None else f"{error_ms:+.1f}",
                     "flag": "" if error_ms is not None and abs(error_ms) <= ONSET_FLAG_MS else "CHECK"})
        print(f"[{event['t']:6.2f}s] {event['what']:9s} {event['material']:8s} onset "
              f"{'n/a' if error_ms is None else f'{error_ms:+.1f} ms'}  {rows[-1]['layers']}")
    clap.release()

    peak = float(numpy.abs(stem).max())
    if peak > 0.89:
        stem *= 0.89 / peak
        print(f"stem peak was {library.to_db(peak):.1f} dBFS, scaled to -1 dBFS")
    tools.write_wav(arguments.out, stem)
    print(f"wrote {arguments.out}  {len(stem) / tools.RATE:.2f}s  reused recordings: "
          f"{sum('reused' in row['layers'] for row in rows)} event(s)")
    print_licence_warnings(records, {unit_key[0] for unit_key in pool.used})
    if arguments.report:
        with open(arguments.report, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)


def print_licence_warnings(records, used_paths):
    by_path = {record["path"]: record for record in records}
    for path in sorted(used_paths):
        record = by_path.get(library.normalize_path(path))
        warning = library.licence_warning(record["licence"]) if record else "not in the index"
        if warning:
            print(f"LICENCE WARNING {Path(path).name} [{record['licence_text'] if record else '?'}]: {warning}")


if __name__ == "__main__":
    main()
