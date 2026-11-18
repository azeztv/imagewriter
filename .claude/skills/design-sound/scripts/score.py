"""Render a composed score (score.json) with sampled instruments, and write the same score as a .mid file.

Run: uv run --no-project --python 3.12 --with numpy --with scipy --with soundfile --with psutil python score.py
     score.json --out music.wav [--bank-root <audio-real folder>] [--seed 11]
The score format and how to write one from a film's beats: references/music.md. Instruments come from the CC0 Versilian
recordings through the Bank in bank_samples.py (repitch + measured tuning): piano, piano-soft (two velocity layers),
marimba (med/loud), pizz (round robin), kick, clap, shaker.
"""
import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path

import numpy

sys.path.insert(0, str(Path(__file__).parent))
import audio_tools as tools

DEFAULT_BANK_ROOT = os.environ.get("SOUND_BANK_DIR", str(Path(os.environ.get("SOUND_LIBRARY_DIR", str(Path.home() / "Documents" / "sound-library"))) / "bank"))
SAMPLES_MODULE = str(Path(__file__).parent / "bank_samples.py")
BASE_GAIN_DB = {"piano": -14, "marimba": -10, "pizz": -10, "kick": -8, "clap": -14, "shaker": -20}
PAN = {"piano": 0.0, "marimba": 0.25, "pizz": -0.05, "kick": 0.0, "clap": 0.08, "shaker": 0.35}
MIDI_PROGRAM = {"piano": 0, "marimba": 12, "pizz": 45}
MIDI_DRUM_NOTE = {"kick": 36, "clap": 39, "shaker": 70}
TIMING_JITTER_SECONDS = 0.008
END_FADE_SECONDS = 0.4
TICKS_PER_BEAT = 480


def load_samples_module():
    spec = importlib.util.spec_from_file_location("bank_samples", SAMPLES_MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Score:
    def __init__(self, data):
        self.data = data
        self.beat = 60.0 / data["tempo"]
        self.beats_per_bar = data.get("beats_per_bar", 4)
        self.duration = data["duration"]
        self.sections = data["sections"]
        self.chords = sorted(data["chords"], key=lambda chord: chord["beat"])
        self.motifs = data["motifs"]

    def section_at(self, time):
        for section in self.sections:
            if section["start"] <= time < section["end"]:
                return section
        return None

    def energy_at(self, time):
        section = self.section_at(time)
        if section is None:
            return 0.0
        span = max(1e-9, section["end"] - section["start"])
        progress = (time - section["start"]) / span
        return section["energy"] + (section.get("energy_to", section["energy"]) - section["energy"]) * progress

    def chord_at(self, beat):
        current = self.chords[0]
        for chord in self.chords:
            if chord["beat"] <= beat + 1e-6:
                current = chord
        return current

    def chord_length_beats(self, chord):
        later = [other["beat"] for other in self.chords if other["beat"] > chord["beat"]]
        return (min(later) if later else self.duration / self.beat) - chord["beat"]

    def notes(self, note_to_midi):
        """Every note that will sound: dicts with instrument, midi, beat, length_beats, velocity."""
        planned = []
        total_beats = int(self.duration / self.beat) + 1
        for phrase in self.data["phrases"]:
            for midi, offset, length, *loudness in self.motifs[phrase["motif"]]:
                planned.append({"instrument": phrase["instrument"], "midi": midi + phrase.get("transpose", 0),
                                "beat": phrase["beat"] + offset, "length_beats": length,
                                "velocity": loudness[0] if loudness else 1.0, "source": "motif"})
        for chord in self.chords:
            length = self.chord_length_beats(chord)
            for index, name in enumerate(chord["notes"]):
                planned.append({"instrument": "piano", "midi": note_to_midi(name), "beat": chord["beat"] + index * 0.04,
                                "length_beats": length, "velocity": 1.0, "source": "chord"})
        for beat in range(total_beats):
            chord = self.chord_at(beat)
            energy = self.energy_at(beat * self.beat)
            in_bar = beat % self.beats_per_bar
            root = note_to_midi(chord["bass"])
            if energy >= 0.2 and in_bar == 0 or energy >= 0.5 and in_bar == 2:
                planned.append({"instrument": "pizz", "midi": root, "beat": beat, "length_beats": 1.4, "velocity": 1.0, "source": "bass"})
            if energy >= 0.8 and in_bar == 3:
                planned.append({"instrument": "pizz", "midi": root + 12, "beat": beat + 0.5, "length_beats": 0.5, "velocity": 0.7, "source": "bass"})
            if energy >= 0.6 and (in_bar == 0 or energy >= 0.8 and in_bar == 2):
                planned.append({"instrument": "kick", "midi": 36, "beat": beat, "length_beats": 1, "velocity": 1.0, "source": "drums"})
            if energy >= 0.8 and in_bar in (1, 3):
                planned.append({"instrument": "clap", "midi": 39, "beat": beat, "length_beats": 1, "velocity": 0.8, "source": "drums"})
            if energy >= 0.7:
                for half in (0, 0.5):
                    planned.append({"instrument": "shaker", "midi": 70, "beat": beat + half, "length_beats": 0.5,
                                    "velocity": 0.6 if half else 0.4, "source": "drums"})
        gated = []
        for note in planned:
            time = note["beat"] * self.beat
            section = self.section_at(time)
            energy = self.energy_at(time)
            if section is None or energy <= 0 or note["instrument"] not in section["instruments"] or time >= self.duration:
                continue
            note["time"] = time
            note["energy"] = energy
            gated.append(note)
        return sorted(gated, key=lambda note: note["time"])


class Renderer:
    def __init__(self, bank, samples_module, seed):
        self.bank = bank
        self.module = samples_module
        self.rng = numpy.random.default_rng(seed)
        self.round_robin = {}
        self.percussion = {
            "kick": [bank.normalised(bank.load(entry["id"]), -3) for entry in bank.role("bass-drum")],
            "clap": [bank.normalised(bank.load(entry["id"]), -3) for entry in bank.role("claps") if "/Clap_" in entry["id"]],
            "shaker": [bank.normalised(bank.load(entry["id"]), -3) for entry in bank.role("shaker") if "Roll" not in entry["id"]],
        }

    def sample_for(self, note):
        instrument, loudness = note["instrument"], 0.25 + 0.75 * note["energy"] * note["velocity"]
        if instrument == "piano":
            return self.bank.note("piano-soft" if loudness < 0.6 else "piano", note["midi"])[0]
        if instrument == "marimba":
            return self.bank.note("marimba", note["midi"], prefer="med" if loudness < 0.6 else "loud")[0]
        if instrument == "pizz":
            turn = self.round_robin[instrument] = 1 - self.round_robin.get(instrument, 1)
            return self.bank.note("pizz", note["midi"], prefer=f"rr{turn + 1}")[0]
        takes = self.percussion[instrument]
        turn = self.round_robin[instrument] = (self.round_robin.get(instrument, -1) + 1) % len(takes)
        return takes[turn]

    def render(self, score, notes):
        buffer = numpy.zeros((int((score.duration + 1) * tools.RATE), 2), dtype=numpy.float32)
        for note in notes:
            sample = self.sample_for(note)
            loudness = 0.25 + 0.75 * note["energy"] * note["velocity"]
            gain_db = BASE_GAIN_DB[note["instrument"]] - 24 * (1 - loudness) + float(self.rng.uniform(-0.8, 0.8))
            time = note["time"] + float(self.rng.uniform(-TIMING_JITTER_SECONDS, TIMING_JITTER_SECONDS))
            length = min(note["length_beats"] * score.beat, 6.5)
            audio = sample.audio[: int((sample.onset + length) * tools.RATE)]
            audio = tools.fade(audio, out_seconds=min(0.35, length / 3))
            pan = PAN[note["instrument"]] + (0.0 if note["instrument"] != "piano" else (note["midi"] % 12 / 11 - 0.5) * 0.4)
            angle = (pan + 1) * numpy.pi / 4
            audio = audio * tools.db_to_gain(gain_db) * numpy.array([numpy.cos(angle), numpy.sin(angle)]) * numpy.sqrt(2)
            start = int(round(time * tools.RATE)) - int(round(sample.onset * tools.RATE))
            buffer = tools.add_at(buffer, audio.astype(numpy.float32), start)
        buffer = buffer[: int(score.duration * tools.RATE)]
        buffer = tools.fade(buffer, out_seconds=END_FADE_SECONDS)
        peak = float(numpy.abs(buffer).max())
        return buffer * (0.7 / peak) if peak > 0.7 else buffer


# ---------------------------------------------------------------- MIDI

def variable_length(value):
    chunks = [value & 0x7F]
    value >>= 7
    while value:
        chunks.append((value & 0x7F) | 0x80)
        value >>= 7
    return bytes(reversed(chunks))


def write_midi(path, score, notes):
    """Format 1 file: a tempo track and one track per instrument (percussion on channel 10)."""
    microseconds = int(60_000_000 / score.data["tempo"])
    tracks = [variable_length(0) + b"\xff\x51\x03" + microseconds.to_bytes(3, "big")
              + variable_length(0) + b"\xff\x58\x04" + bytes([score.beats_per_bar, 2, 24, 8])]
    for instrument in dict.fromkeys(note["instrument"] for note in notes):
        drum = instrument in MIDI_DRUM_NOTE
        channel = 9 if drum else len(tracks) % 9
        events = []
        for note in notes:
            if note["instrument"] != instrument:
                continue
            start = int(round(note["beat"] * TICKS_PER_BEAT))
            end = start + max(1, int(round(note["length_beats"] * TICKS_PER_BEAT)))
            velocity = int(numpy.clip(30 + 97 * note["energy"] * note["velocity"], 1, 127))
            pitch = MIDI_DRUM_NOTE[instrument] if drum else note["midi"]
            events += [(start, 1, bytes([0x90 | channel, pitch, velocity])), (end, 0, bytes([0x80 | channel, pitch, 0]))]
        body = b""
        if not drum:
            body += variable_length(0) + bytes([0xC0 | channel, MIDI_PROGRAM[instrument]])
        body += variable_length(0) + b"\xff\x03" + bytes([len(instrument)]) + instrument.encode()
        previous = 0
        for tick, _, message in sorted(events, key=lambda event: (event[0], event[1])):
            body += variable_length(tick - previous) + message
            previous = tick
        tracks.append(body)
    data = b"MThd" + (6).to_bytes(4, "big") + (1).to_bytes(2, "big") + len(tracks).to_bytes(2, "big") \
        + TICKS_PER_BEAT.to_bytes(2, "big")
    for body in tracks:
        body += variable_length(0) + b"\xff\x2f\x00"
        data += b"MTrk" + len(body).to_bytes(4, "big") + body
    Path(path).write_bytes(data)


def main():
    import psutil
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("score")
    parser.add_argument("--out", required=True)
    parser.add_argument("--bank-root", default=DEFAULT_BANK_ROOT)
    parser.add_argument("--seed", type=int, default=11)
    arguments = parser.parse_args()

    module = load_samples_module()
    score = Score(json.loads(Path(arguments.score).read_text(encoding="utf-8")))
    notes = score.notes(module.note_to_midi)
    renderer = Renderer(module.Bank(arguments.bank_root), module, arguments.seed)
    music = renderer.render(score, notes)
    tools.write_wav(arguments.out, music)
    midi_path = Path(arguments.out).with_suffix(".mid")
    write_midi(midi_path, score, notes)
    per_instrument = {name: sum(note["instrument"] == name for note in notes) for name in dict.fromkeys(n["instrument"] for n in notes)}
    print(f"wrote {arguments.out} ({len(music) / tools.RATE:.2f}s, {score.data['tempo']} bpm) and {midi_path}")
    print("notes per instrument: " + json.dumps(per_instrument))
    for section in score.sections:
        count = sum(section["start"] <= note["time"] < section["end"] for note in notes)
        print(f"  section {section['start']:5.2f}-{section['end']:5.2f}s energy {section['energy']}"
              f"->{section.get('energy_to', section['energy'])}  {count} notes")


if __name__ == "__main__":
    main()
