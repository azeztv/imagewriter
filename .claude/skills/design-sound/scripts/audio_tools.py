"""Small audio helpers shared by foley.py, score.py and mix.py: filters, repitching, panning, onsets, WAV output."""
from fractions import Fraction

import numpy
import soundfile
from scipy.signal import butter, resample_poly, sosfilt

RATE = 48000


def lowpass(samples, cutoff_hz, order=2):
    if cutoff_hz >= RATE / 2 * 0.95:
        return samples
    return sosfilt(butter(order, cutoff_hz, btype="low", fs=RATE, output="sos"), samples, axis=0).astype(numpy.float32)


def highpass(samples, cutoff_hz, order=2):
    if cutoff_hz <= 10:
        return samples
    return sosfilt(butter(order, cutoff_hz, btype="high", fs=RATE, output="sos"), samples, axis=0).astype(numpy.float32)


def repitch(samples, semitones):
    """Plays the recording faster or slower, as a sampler does (pitch and duration move together)."""
    if abs(semitones) < 0.01:
        return samples
    ratio = Fraction(2 ** (semitones / 12)).limit_denominator(600)
    return resample_poly(samples, ratio.denominator, ratio.numerator, axis=0).astype(numpy.float32)


def db_to_gain(db):
    return 10 ** (db / 20)


def envelope(mono, window_ms=3):
    """Smoothed RMS level, one value per millisecond."""
    hop = RATE // 1000
    window = window_ms * hop
    squared = numpy.convolve(mono.astype(numpy.float64) ** 2, numpy.ones(window) / window, mode="same")
    return numpy.sqrt(squared[::hop] + 1e-14)


def main_attack_index(mono):
    """Sample where the loudest attack begins: what the ear hears as the hit."""
    level = envelope(mono)
    peak = int(numpy.argmax(level))
    quiet = level[peak] * 10 ** (-20 / 20)
    start = peak
    while start > 0 and level[start - 1] > quiet and level[start - 1] <= level[start] * 1.05:
        start -= 1
    hop = RATE // 1000
    region = numpy.abs(mono[start * hop: peak * hop + hop])
    if len(region) == 0:
        return peak * hop
    return start * hop + int(numpy.argmax(region >= 0.1 * region.max()))


def first_onset_index(mono, fraction=0.1):
    """Sample where the sound first reaches `fraction` of its peak level (for rolls and scrapes)."""
    level = envelope(mono)
    return int(numpy.argmax(level >= fraction * level.max())) * (RATE // 1000)


def measured_onset_seconds(mono, fraction=0.1):
    """Independent check on a rendered buffer: first time it reaches -20 dB of its own peak."""
    return first_onset_index(mono, fraction) / RATE


def pan_stereo(mono, position):
    """Constant-power pan, position -1 (left) to 1 (right)."""
    angle = (float(numpy.clip(position, -1, 1)) + 1) * numpy.pi / 4
    return numpy.stack([mono * numpy.cos(angle), mono * numpy.sin(angle)], axis=1)


def fade(samples, in_seconds=0.0, out_seconds=0.0):
    samples = samples.copy()
    fade_in = min(len(samples), int(in_seconds * RATE))
    fade_out = min(len(samples), int(out_seconds * RATE))
    shape = (-1,) + (1,) * (samples.ndim - 1)
    if fade_in:
        samples[:fade_in] *= numpy.linspace(0, 1, fade_in).reshape(shape)
    if fade_out:
        samples[-fade_out:] *= numpy.linspace(1, 0, fade_out).reshape(shape)
    return samples


def add_at(buffer, samples, start_index):
    """Mixes `samples` into `buffer` at a sample index, growing the buffer when needed."""
    if start_index < 0:
        samples = samples[-start_index:]
        start_index = 0
    needed = start_index + len(samples)
    if needed > len(buffer):
        buffer = numpy.concatenate([buffer, numpy.zeros((needed - len(buffer),) + buffer.shape[1:], dtype=buffer.dtype)])
    buffer[start_index:needed] += samples
    return buffer


def read_stereo(path):
    audio, rate = soundfile.read(path, dtype="float32", always_2d=True)
    if rate != RATE:
        audio = resample_poly(audio, RATE, rate, axis=0).astype(numpy.float32)
    return audio if audio.shape[1] == 2 else numpy.repeat(audio[:, :1], 2, axis=1)


def write_wav(path, stereo):
    soundfile.write(str(path), numpy.clip(stereo, -1.0, 1.0), RATE, subtype="PCM_24")
