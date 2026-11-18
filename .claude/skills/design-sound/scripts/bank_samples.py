"""The one-shot bank: loading, picking each recording at most once, and repitching recorded notes and taps."""
import json
from fractions import Fraction
from pathlib import Path

import numpy as np
import soundfile
from scipy.signal import resample_poly

RATE = 48000
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def note_to_midi(name):
    """'C#5' in scientific pitch -> 73."""
    pitch = name.rstrip("-0123456789")
    octave = int(name[len(pitch):])
    return NOTE_NAMES.index(pitch) + 12 * (octave + 1)


def midi_to_hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


class Sample:
    """Recorded audio with the position of its transient (`onset`, seconds from the start)."""

    def __init__(self, audio, onset, label):
        self.audio = audio
        self.onset = onset
        self.label = label

    @property
    def duration(self):
        return len(self.audio) / RATE


def repitch(sample, semitones):
    """Plays the recording faster or slower, as a sampler does; the transient position scales with it."""
    if abs(semitones) < 0.01:
        return sample
    ratio = Fraction(2 ** (semitones / 12)).limit_denominator(600)
    audio = resample_poly(sample.audio, ratio.denominator, ratio.numerator, axis=0).astype(np.float32)
    actual = ratio.numerator / ratio.denominator
    return Sample(audio, sample.onset / actual, f"{sample.label} {semitones:+.2f}st")


def main_attack(mono):
    """Sample index where the loudest attack of a sound begins: what the ear hears as the hit. For a single
    transient it is the onset; for a jingle or a page turn it is the big contact rather than a faint first touch."""
    mono = np.abs(mono)
    hop = max(1, RATE // 1000)
    window = 3 * hop
    level = np.sqrt(np.convolve(mono ** 2, np.ones(window) / window, mode="same")[::hop] + 1e-14)
    peak = int(np.argmax(level))
    quiet = level[peak] * 10 ** (-20 / 20)
    start = peak
    while start > 0 and level[start - 1] > quiet and level[start - 1] <= level[start] * 1.05:
        start -= 1
    region = mono[start * hop: peak * hop + hop]
    if len(region) == 0:
        return peak * hop
    return start * hop + int(np.argmax(region >= 0.1 * region.max()))


def on_main_attack(sample, lead_in=0.06, fade=0.01):
    """The same recording aligned on its main hit (its loudest attack, anywhere in it). Anything earlier than
    `lead_in` before that hit is cut away, so a faint first touch or a stray bounce never plays ahead of the cue."""
    attack = main_attack(sample.audio.mean(axis=1))
    start = max(0, attack - int(lead_in * RATE))
    audio = sample.audio[start:].copy()
    if start > 0:
        samples = min(len(audio), int(fade * RATE))
        audio[:samples] *= np.linspace(0, 1, samples)[:, None]
    # Measured again on exactly what will play: a press and release close together count as one hit, starting
    # at the press.
    return Sample(audio, main_attack(audio.mean(axis=1)) / RATE, sample.label)


def reverse(sample):
    return Sample(sample.audio[::-1].copy(), sample.duration - sample.onset, f"{sample.label} reversed")


def dominant_hz(audio, start=0.004, length=0.25, low=300.0, high=9000.0, within_db=15.0):
    """The pitch a struck glass is heard at: its lowest partial within `within_db` of the strongest one."""
    mono = audio.mean(axis=1)[int(start * RATE): int((start + length) * RATE)]
    size = 1 << 17
    spectrum = np.abs(np.fft.rfft(mono * np.hanning(len(mono)), n=size))
    frequencies = np.fft.rfftfreq(size, 1 / RATE)
    band = np.nonzero((frequencies > low) & (frequencies < high))[0]
    strongest = spectrum[band].max()
    is_peak = (spectrum[band] > spectrum[band - 1]) & (spectrum[band] >= spectrum[band + 1])
    strong = band[is_peak & (spectrum[band] >= strongest * 10 ** (-within_db / 20))]
    index = int(strong[0])
    left, centre, right = np.log(spectrum[index - 1: index + 2] + 1e-12)
    offset = 0.5 * (left - right) / (left - 2 * centre + right)
    return float(frequencies[index] + offset * (frequencies[1] - frequencies[0]))


class Bank:
    def __init__(self, root):
        self.root = Path(root)
        self.entries = json.loads((self.root / "prepared" / "bank.json").read_text(encoding="utf-8"))
        self.tuning = json.loads((self.root / "prepared" / "tuning.json").read_text(encoding="utf-8"))
        self.by_id = {entry["id"]: entry for entry in self.entries}
        self.cache = {}
        self.used = set()
        self.pitch_cache = {}

    def load(self, identifier):
        if identifier not in self.cache:
            entry = self.by_id[identifier]
            audio, rate = soundfile.read(self.root / entry["path"], dtype="float32", always_2d=True)
            assert rate == RATE
            self.cache[identifier] = Sample(audio, entry["pre_roll"], identifier)
        return self.cache[identifier]

    def role(self, role, source=None):
        return [entry for entry in self.entries if entry["role"] == role and (source is None or source in entry["id"])]

    def clean_hits(self, role, source=None, within_db=10.0, min_duration=0.03):
        """Slices that are real hits: within `within_db` of the loudest slice cut from the same recording."""
        entries = self.role(role, source)
        loudest = {}
        for entry in entries:
            key = entry.get("slice_of", entry["id"])
            loudest[key] = max(loudest.get(key, -200.0), entry["peak_db"])
        return [entry for entry in entries
                if entry["duration"] >= min_duration and entry["peak_db"] >= loudest[entry.get("slice_of", entry["id"])] - within_db]

    def take(self, candidates, key=None, label=""):
        """The first candidate nobody has used yet (in `key` order), marked as used."""
        ordered = sorted(candidates, key=key) if key else list(candidates)
        for entry in ordered:
            if entry["id"] not in self.used:
                self.used.add(entry["id"])
                return self.load(entry["id"])
        raise RuntimeError(f"no unused recording left for {label or candidates[:1]}")

    def normalised(self, sample, peak_db=-6.0):
        peak = float(np.abs(sample.audio).max())
        gain = 10 ** (peak_db / 20) / peak if peak > 0 else 1.0
        return Sample(sample.audio * gain, sample.onset, sample.label)

    def role_gain(self, role):
        """Brings an instrument's recordings to a common level (-6 dBFS at the role's median peak), keeping the
        differences between its notes and dynamics as they were played."""
        peaks = [entry["peak_db"] for entry in self.role(role)]
        return 10 ** ((-6.0 - float(np.median(peaks))) / 20)

    def note(self, role, midi, prefer=None, avoid_repeat=None):
        """The recorded note nearest to `midi` in an instrument role, tuned exactly onto it."""
        entries = [entry for entry in self.role(role) if "midi" in entry and (prefer is None or prefer in entry["id"])]
        entries.sort(key=lambda entry: (abs(entry["midi"] - midi), entry["id"] == avoid_repeat))
        entry = entries[0]
        correction = self.tuning.get(entry["id"], {}).get("cents", 0.0) / 100
        sample = self.load(entry["id"])
        levelled = Sample(sample.audio * self.role_gain(role), sample.onset, sample.label)
        return repitch(levelled, (midi - entry["midi"]) - correction), entry["id"]

    def tuned_hit(self, candidates, target_midi, max_shift=7.0, label=""):
        """An unused struck-glass (or similar) hit, shifted so its strongest partial lands on `target_midi`."""
        target_hz = midi_to_hz(target_midi)
        scored = []
        for entry in candidates:
            if entry["id"] in self.used:
                continue
            if entry["id"] not in self.pitch_cache:
                self.pitch_cache[entry["id"]] = dominant_hz(self.load(entry["id"]).audio)
            shift = 12 * np.log2(target_hz / self.pitch_cache[entry["id"]])
            if abs(shift) <= max_shift:
                scored.append((abs(shift), shift, entry))
        if not scored:
            raise RuntimeError(f"no glass hit within {max_shift} semitones of midi {target_midi} for {label}")
        scored.sort(key=lambda item: item[0])
        _, shift, entry = scored[0]
        self.used.add(entry["id"])
        return repitch(self.load(entry["id"]), shift)
