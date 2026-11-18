"""Mix stems into a final WAV, then check each stem on its own with the listen.py ears.

Run: uv run --no-project --python 3.12 --with numpy --with scipy --with librosa --with soundfile --with pyloudnorm
     --with psutil --with torch --with transformers python mix.py mix.json --out final.wav
mix.json: {"stems": [{"name", "file", "role": "cue|voice|duck|bed", "gain_db", "offset_s", "duck_db", "highpass",
"lowpass"}], "target_lufs": -14, "true_peak_db": -1, "expect": [{"stem", "label", "t"}], "expect_from_events":
"events.json" (checks every foley event on the "foley" stem; an event's optional "label" names it)}.
Roles: cue and voice trigger the side-chain and are never ducked; duck (music) and bed are ducked under them; a bed is
also band-limited (default 200 Hz - 5 kHz) so it stays out of the cues' band. A duck stem also gets a dynamic cut of
`carve_db` (default -3) at 1-4 kHz while the voice (else the cues) plays, and a stem with "phone_bass": true gets
2nd/3rd harmonics of its content under 150 Hz so impacts survive phone speakers. The master sums below 100 Hz to mono.
Voice stems are high-passed at 80 Hz and de-essed when their sibilance passes what the owner approved before; when the voice
sits under 10 LU over the music, the music and beds are lowered and the mix is made again; the master is encoded to
AAC 128k and Opus 64k and its ceiling lowered until the decoded true peak stays under -0.3 dBTP.
Checks from the 2026-11-04 research (references/mix.md, Evidence): short-term max over integrated + 5 LU, voice over
music under 10 LU while speaking, mono fold-down loss, cues with most energy under 200 Hz. Details: references/mix.md.
"""
import argparse
import json
import sys
from pathlib import Path

import librosa
import numpy
from scipy.ndimage import maximum_filter1d, minimum_filter1d
from scipy.signal import butter, resample_poly, sosfiltfilt

sys.path.insert(0, str(Path(__file__).parent))
import audio_tools as tools
import listen
import sound_library as library

DEFAULT_DUCK_DB = {"duck": -8.0, "bed": -6.0}
BED_BAND_HZ = (200, 5000)
SIDECHAIN_FLOOR_DB, SIDECHAIN_RANGE_DB = -50.0, 20.0  # no ducking below the floor, full ducking 20 dB above it
# Values only the owner's ears can set live in house-defaults.json, chosen with ab_test.py; an agent never tunes them alone.
HOUSE_DEFAULTS = json.loads((Path(__file__).parent.parent / "house-defaults.json").read_text(encoding="utf-8"))
# Release 300 ms is the low end of the 300-600 ms range for speech (Resolve ducker guidance, creator guides 250-700);
# the hold bridges the gaps between words so the music does not pump (no source gives a number: the owner's pick).
RELEASE_MS, LOOKAHEAD_MS = 300, 30
HOLD_MS = int(HOUSE_DEFAULTS["hold_ms"])
# A cue must stand this far over the ducked music, A-weighted (loudness as heard, so a sub thump counts for little),
# loudest frame of the cue against the music's median over the same 0.4 s. First set from two cues the owner did not hear in
# an intro film (a CRT power-on at -2.7 dB and a switch-off at +3.5 dB); later changes are the owner's A/B picks.
QUIET_UNDER_MUSIC_DB = float(HOUSE_DEFAULTS["cue_margin_dba"])
# Spectral unmasking (the TrackSpacer / Neutron Unmask idea): while a cue plays, the voice yields only in the
# frequency bins where the cue sits within 6 dB of it or above, by at most UNMASK_DB, so the cue reads without
# being turned up. How deep is an ear call (the owner's A/B pick, ab_test.py --param unmask).
UNMASK_DB = float(HOUSE_DEFAULTS.get("unmask_db", -3.0))
UNMASK_N_FFT, UNMASK_HOP = 1024, 240   # 21 ms window, 5 ms hop at 48 kHz
UNMASK_RELEASE_MS = 120
UNMASK_FLOOR_BELOW_PEAK_DB = 50.0     # cue bins this far under the cue stem's loudest bin count as silence
CUE_WINDOW_SECONDS = 0.4
# Research numbers, sources in references/mix.md "Evidence".
DEFAULT_TRUE_PEAK_DB = -1.5        # Spotify asks -1, or -2 above -14 LUFS, for lossy transcodes; -1.5 splits it
SHORT_TERM_OVER_INTEGRATED_LU = 5  # EBU R128 s1 short-form: max short-term loudness = target + 5 LU
VOICE_OVER_MUSIC_LU = 10           # Torcoli et al. 2019: commentary at least 10 LU over music (non-experts want ~4 more)
CARVE_BAND_HZ = (1000, 4000)
DEFAULT_CARVE_DB = -3.0
PHONE_BASS_HZ = 150
PHONE_CUTOFF_HZ = 200              # phone speakers roll off between about 100 and 250 Hz
PHONE_WEAK_SHARE = 0.3             # a cue with under 30% of its energy above 200 Hz is barely there on a phone
MONO_BASS_HZ = 100
MONO_LOSS_FLAG_DB = 3.0
VOICE_HIGHPASS_HZ = 80             # tutorial consensus 80-100 Hz; above 120 Hz thins the voice
AUTO_LEVEL_MARGIN_LU = 1.0         # when lowering the music to meet the voice rule, land this far past it
# De-essing threshold from the owner's approved narrations (four documentary Shorts;
# measured 2026-11-04): energy at 5-10 kHz over 125-4000 Hz per voiced frame never passed +25.4 dB. Frames above
# +25 dB get the 5-10 kHz band lowered by the excess, at most 4 dB (tutorials: 2-4 dB is usually enough).
SIBILANCE_BAND_HZ = (5000, 10000)
VOICE_BODY_HZ = (125, 4000)
SIBILANCE_THRESHOLD_DB = 25.0
DEESS_MAX_DB = 4.0
# Lossy encodes put the true peak 0.5 to 3.2 dB above the master's (measured 2026-11-04 on four clips, ffmpeg AAC
# 128k and 96k, Opus 128k and 64k, MP3 128k): no fixed ceiling is safe, so the encode is measured.
CODEC_CHECKS = {"aac 128k": ["-c:a", "aac", "-b:a", "128k", "-f", "adts"],
                "opus 64k": ["-c:a", "libopus", "-b:a", "64k", "-f", "ogg"]}
DECODED_PEAK_LIMIT_DB = -0.3


def zero_phase(samples, cutoff, btype, order=4):
    """Zero-phase filter, so a band taken out and put back (or subtracted) leaves the rest of the signal untouched."""
    sos = butter(order, cutoff, btype=btype, fs=tools.RATE, output="sos")
    return sosfiltfilt(sos, samples, axis=0).astype(numpy.float32)


def carve(audio, trigger_mono, carve_db):
    """Dynamic EQ: dip the 1-4 kHz band of a music stem by `carve_db` while the trigger plays, rest untouched."""
    band = zero_phase(audio, CARVE_BAND_HZ, "bandpass", order=2)
    gain = sidechain_gain(trigger_mono, carve_db)
    gain = numpy.pad(gain, (0, max(0, len(audio) - len(gain))), mode="edge")[: len(audio)]
    return audio - band * (1 - gain)[:, None]


def unmask_voice(voice_audio, cue_mono, unmask_db):
    """Lowers the voice by up to `unmask_db` only in the bins and moments a cue would be masked by it.
    Returns the voice and the milliseconds where it yielded more than 1 dB somewhere."""
    if not unmask_db:
        return voice_audio, 0
    cue_spectrum = numpy.abs(librosa.stft(cue_mono, n_fft=UNMASK_N_FFT, hop_length=UNMASK_HOP))
    voice_spectrum = numpy.abs(librosa.stft(voice_audio.mean(axis=1), n_fft=UNMASK_N_FFT, hop_length=UNMASK_HOP))
    frames = min(cue_spectrum.shape[1], voice_spectrum.shape[1])
    cue_spectrum = cue_spectrum[:, :frames]
    voice_spectrum = voice_spectrum[:, :frames]
    smoothing = numpy.ones(5) / 5  # about 235 Hz wide, so the cut follows bands and not single bins
    cue_db = 20 * numpy.log10(numpy.apply_along_axis(numpy.convolve, 0, cue_spectrum, smoothing, "same") + 1e-9)
    voice_db = 20 * numpy.log10(numpy.apply_along_axis(numpy.convolve, 0, voice_spectrum, smoothing, "same") + 1e-9)
    cue_present = cue_db > cue_db.max() - UNMASK_FLOOR_BELOW_PEAK_DB
    amount = numpy.clip((cue_db - voice_db + 6.0) / 12.0, 0, 1) * cue_present
    # 10 ms look-ahead so the voice is already out of the way on the cue's first frame, then a smooth release.
    ahead = 2
    amount = numpy.maximum(amount, numpy.concatenate([amount[:, ahead:], numpy.zeros((amount.shape[0], ahead))], axis=1))
    release = numpy.exp(-UNMASK_HOP / tools.RATE * 1000 / UNMASK_RELEASE_MS)
    held = numpy.zeros_like(amount)
    for frame in range(frames):
        previous = held[:, frame - 1] * release if frame else 0
        held[:, frame] = numpy.maximum(amount[:, frame], previous)
    gain = tools.db_to_gain(unmask_db * held)
    output = numpy.zeros_like(voice_audio)
    for channel in range(voice_audio.shape[1]):
        spectrum = librosa.stft(voice_audio[:, channel], n_fft=UNMASK_N_FFT, hop_length=UNMASK_HOP)[:, :frames]
        output[:, channel] = librosa.istft(spectrum * gain, hop_length=UNMASK_HOP, length=len(voice_audio))
    yielded_frames = int((unmask_db * held < -1.0).any(axis=0).sum())
    return output, round(yielded_frames * UNMASK_HOP / tools.RATE * 1000)


def add_phone_bass(audio):
    """Harmonics of the content under 150 Hz (soft clipping makes the 2nd and 3rd), band-passed to 150-600 Hz and mixed
    at -6 dB, so the ear infers a thump the phone speaker cannot play (missing fundamental)."""
    low = zero_phase(audio, PHONE_BASS_HZ, "lowpass")
    peak = float(numpy.abs(low).max()) or 1.0
    driven = low / peak * 4.0
    harmonics = (numpy.tanh(driven) + 0.5 * driven ** 2 / (1 + driven ** 2)) * peak / 4.0
    harmonics = zero_phase(harmonics, (PHONE_BASS_HZ, 600), "bandpass", order=2)
    return audio + harmonics * tools.db_to_gain(-6.0)


def deess(audio):
    """Split-band de-esser. Detection uses the same STFT frames as the threshold was measured with (2048 points, 10 ms
    hop): the 5-10 kHz energy over the 125-4000 Hz energy per voiced frame. Where it passes the threshold, the 5-10 kHz
    band alone is lowered by the excess (at most DEESS_MAX_DB), 60 ms release. Returns audio, frames cut, deepest cut."""
    mono = audio.mean(axis=1)
    hop = tools.RATE // 100
    power = numpy.abs(librosa.stft(mono, n_fft=2048, hop_length=hop)) ** 2
    frequencies = librosa.fft_frequencies(sr=tools.RATE, n_fft=2048)
    in_band = (frequencies >= SIBILANCE_BAND_HZ[0]) & (frequencies < SIBILANCE_BAND_HZ[1])
    in_body = (frequencies >= VOICE_BODY_HZ[0]) & (frequencies < VOICE_BODY_HZ[1])
    ratio_db = 10 * numpy.log10(power[in_band].sum(axis=0) + 1e-12) - 10 * numpy.log10(power[in_body].sum(axis=0) + 1e-12)
    level = 10 * numpy.log10(power.sum(axis=0) + 1e-12)
    voiced = level > level.max() - 40
    cut_db = numpy.where(voiced, numpy.clip(ratio_db - SIBILANCE_THRESHOLD_DB, 0, DEESS_MAX_DB), 0.0)
    if not cut_db.any():
        return audio, 0, 0.0
    smoothed = numpy.zeros_like(cut_db)
    release = numpy.exp(-10 / 60)
    for index in range(len(cut_db)):
        previous = smoothed[index - 1] if index else 0.0
        smoothed[index] = max(cut_db[index], previous * release)
    per_sample = numpy.interp(numpy.arange(len(audio)), numpy.arange(len(smoothed)) * hop, smoothed)
    band = zero_phase(audio, SIBILANCE_BAND_HZ, "bandpass", order=4)
    gain = tools.db_to_gain(-per_sample)
    return audio - band * (1 - gain)[:, None], int((cut_db > 0).sum()), float(cut_db.max())


def decoded_true_peaks(stereo):
    """True peak after each lossy encode in CODEC_CHECKS, decoded back to float with ffmpeg."""
    import subprocess
    import tempfile
    import soundfile
    peaks = {}
    folder = Path(tempfile.mkdtemp())
    source = folder / "master.wav"
    soundfile.write(source, stereo, tools.RATE, subtype="FLOAT")
    for name, options in CODEC_CHECKS.items():
        encoded = folder / f"encoded-{name.replace(' ', '-')}"
        decoded = folder / f"decoded-{name.replace(' ', '-')}.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(source), *options, str(encoded)], check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(encoded), "-ar", str(tools.RATE), "-ac", "2",
                        "-c:a", "pcm_f32le", str(decoded)], check=True)
        audio, _ = soundfile.read(decoded, dtype="float32")
        peaks[name] = true_peak_stereo_db(audio)
    return peaks


def master_for_codecs(total, target_lufs, ceiling_db, check_codecs):
    """Masters, then lowers the ceiling by the codec overshoot until every decoded true peak is under the limit
    (at most three tries; the gain loss is made up by the limiter, so loudness stays on target)."""
    final = master(total, target_lufs, ceiling_db)
    if not check_codecs:
        return final, ceiling_db, {}
    peaks = decoded_true_peaks(final)
    for _ in range(3):
        excess = max(peaks.values()) - DECODED_PEAK_LIMIT_DB
        if excess <= 0:
            break
        ceiling_db -= excess + 0.1
        final = master(total, target_lufs, ceiling_db)
        peaks = decoded_true_peaks(final)
    return final, ceiling_db, peaks


def mono_bass(stereo):
    """Everything under 100 Hz to the centre: small speakers play one channel of it, and wide sub cancels."""
    low = zero_phase(stereo, MONO_BASS_HZ, "lowpass")
    return stereo - low + low.mean(axis=1, keepdims=True)


def short_term_max_lufs(stereo):
    """Highest 3 s loudness, in 1 s steps (EBU short-term)."""
    import pyloudnorm
    meter = pyloudnorm.Meter(tools.RATE)
    window, step = 3 * tools.RATE, tools.RATE
    if len(stereo) < window:
        return stereo_loudness(stereo)
    values = [meter.integrated_loudness(stereo[start:start + window].astype(numpy.float64))
              for start in range(0, len(stereo) - window + 1, step)]
    finite = [value for value in values if numpy.isfinite(value)]
    return max(finite) if finite else float("-inf")


def voice_over_music_lu(voice, music):
    """Loudness of the voice against the ducked, carved music over the half seconds where the voice speaks."""
    import pyloudnorm
    meter = pyloudnorm.Meter(tools.RATE)
    voice_mono = voice.mean(axis=1)
    second = tools.RATE
    active = [start for start in range(0, len(voice_mono) - second, second // 2)
              if library.to_db(numpy.sqrt(numpy.mean(voice_mono[start:start + second] ** 2)) + 1e-12) > -45]
    if not active:
        return None
    voice_part = numpy.concatenate([voice[start:start + second] for start in active])
    music_part = numpy.concatenate([music[start:start + second] for start in active])
    music_loudness = meter.integrated_loudness(music_part.astype(numpy.float64))
    if not numpy.isfinite(music_loudness):
        return float("inf")
    return float(meter.integrated_loudness(voice_part.astype(numpy.float64)) - music_loudness)


def mono_loss_db(stereo):
    """How much quieter the mono fold-down is than the stereo mix; over 3 dB means wide or out-of-phase content."""
    return stereo_loudness(stereo) - stereo_loudness(numpy.repeat(stereo.mean(axis=1, keepdims=True), 2, axis=1))


def phone_share(cue_mono, cue_time):
    """Share of a cue's energy above 200 Hz in its first 0.4 s."""
    start, end = int(cue_time * tools.RATE), int((cue_time + CUE_WINDOW_SECONDS) * tools.RATE)
    window = cue_mono[start:end]
    if len(window) < 64:
        return None
    total = float(numpy.sum(window ** 2))
    if total < 1e-10:
        return None
    return float(numpy.sum(zero_phase(window, PHONE_CUTOFF_HZ, "highpass") ** 2)) / total


def a_weighted_levels_db(mono):
    """Per-frame A-weighted power in dB, on listen.py's STFT frames."""
    power = numpy.abs(librosa.stft(mono, n_fft=listen.N_FFT, hop_length=listen.HOP)) ** 2
    weights = 10 ** (librosa.A_weighting(librosa.fft_frequencies(sr=tools.RATE, n_fft=listen.N_FFT)) / 10)
    return 10 * numpy.log10((power * weights[:, None]).sum(axis=0) + 1e-12)


def margin_over_music(cue_levels, music_levels, cue_time):
    """Loudest A-weighted frame of the cue minus the music's median in the same window."""
    frame_seconds = listen.HOP / tools.RATE
    first, last = int(cue_time / frame_seconds), int((cue_time + CUE_WINDOW_SECONDS) / frame_seconds) + 1
    if not len(cue_levels[first:last]):
        return None
    return float(cue_levels[first:last].max() - numpy.median(music_levels[first:last]))


def sidechain_gain(trigger_mono, duck_db):
    """Per-sample gain that dips by `duck_db` while the trigger is loud: starts 30 ms early, releases over 250 ms."""
    level_db = 20 * numpy.log10(tools.envelope(trigger_mono, window_ms=10) + 1e-9)
    amount = numpy.clip((level_db - SIDECHAIN_FLOOR_DB) / SIDECHAIN_RANGE_DB, 0, 1)
    # Hold: each millisecond keeps the loudest value of the last HOLD_MS before the release starts.
    amount = maximum_filter1d(amount, size=HOLD_MS + 1, origin=HOLD_MS // 2, mode="nearest")
    held = numpy.zeros_like(amount)
    for index in range(len(amount)):
        held[index] = max(amount[index], held[index - 1] * numpy.exp(-1 / RELEASE_MS) if index else amount[index])
    early = numpy.concatenate([held[LOOKAHEAD_MS:], numpy.zeros(LOOKAHEAD_MS)])
    early = numpy.maximum(early, held)
    smooth = numpy.convolve(early, numpy.ones(20) / 20, mode="same")
    milliseconds = numpy.arange(len(smooth)) * (tools.RATE // 1000)
    per_sample = numpy.interp(numpy.arange(int(milliseconds[-1]) + tools.RATE // 1000), milliseconds, smooth)
    return tools.db_to_gain(duck_db * per_sample)


def limit_true_peak(stereo, ceiling_db):
    """Look-ahead limiter working on the 4x oversampled peak, so inter-sample peaks stay under the ceiling."""
    ceiling = tools.db_to_gain(ceiling_db) * 0.985
    oversampled = numpy.abs(resample_poly(stereo, 4, 1, axis=0)).max(axis=1)
    peak = oversampled[: len(stereo) * 4].reshape(-1, 4).max(axis=1)
    needed = numpy.minimum(1.0, ceiling / (peak + 1e-12))
    window = int(0.005 * tools.RATE)
    held = minimum_filter1d(needed, 2 * window + 1)
    kernel = numpy.hanning(window) / numpy.hanning(window).sum()
    return stereo * numpy.convolve(held, kernel, mode="same")[:, None]


def load_stem(spec, base):
    audio = tools.read_stereo(Path(base) / spec["file"])
    audio = audio * tools.db_to_gain(spec.get("gain_db", 0.0))
    role = spec["role"]
    high, low = spec.get("highpass"), spec.get("lowpass")
    if role == "bed":
        high, low = high if high is not None else BED_BAND_HZ[0], low if low is not None else BED_BAND_HZ[1]
    if role == "voice" and high is None:
        high = VOICE_HIGHPASS_HZ
    if high:
        audio = tools.highpass(audio, high)
    if low:
        audio = tools.lowpass(audio, low)
    if spec.get("phone_bass"):
        audio = add_phone_bass(audio)
    if role == "voice" and spec.get("deess", True):
        audio, reduced_frames, deepest = deess(audio)
        if reduced_frames:
            print(f"de-ess {spec["name"]}: {reduced_frames * 10} ms above +{SIBILANCE_THRESHOLD_DB:.0f} dB sibilance, "
                  f"deepest cut {deepest:.1f} dB")
    offset = int(spec.get("offset_s", 0.0) * tools.RATE)
    return numpy.concatenate([numpy.zeros((offset, 2), dtype=numpy.float32), audio]) if offset else audio


def master(stereo, target_lufs, ceiling_db):
    """Gain to the target integrated loudness, limited to the true-peak ceiling; the limiter's loss is made up again."""
    stereo = mono_bass(stereo)
    gain_db = target_lufs - stereo_loudness(stereo)
    for _ in range(4):
        limited = limit_true_peak(stereo * tools.db_to_gain(gain_db), ceiling_db)
        error = target_lufs - stereo_loudness(limited)
        if abs(error) < 0.2:
            break
        gain_db += error
    return limited


def true_peak_stereo_db(stereo):
    return library.to_db(numpy.abs(resample_poly(stereo, 4, 1, axis=0)).max())


def stereo_loudness(stereo):
    import pyloudnorm
    return float(pyloudnorm.Meter(tools.RATE).integrated_loudness(stereo.astype(numpy.float64)))


def expectations_for(mix, base):
    entries = [(item["stem"], item["label"], item["t"]) for item in mix.get("expect", [])]
    if mix.get("expect_from_events"):
        data = json.loads((Path(base) / mix["expect_from_events"]).read_text(encoding="utf-8"))
        for event in (data["events"] if isinstance(data, dict) else data):
            other = f" on {event['other_material']}" if event.get("other_material") else ""
            label = event.get("label") or f"{event.get('material', '')} {event['what']}{other}".strip()
            entries.append(("foley", label, event["t"]))
    return entries


def write_sheet(path, final, cues):
    """Waveform and mel spectrogram of the final mix with a dashed line and label at each expected cue time."""
    import librosa
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as pyplot

    mono = final.mean(axis=1)
    seconds = len(mono) / tools.RATE
    figure, (wave_axis, spectrogram_axis) = pyplot.subplots(2, 1, figsize=(14, 6), sharex=True,
                                                            gridspec_kw={"height_ratios": [1, 2.4]})
    wave_axis.plot(numpy.arange(len(mono)) / tools.RATE, mono, linewidth=0.4, color="#2b6cb0")
    wave_axis.set_ylim(-1, 1)
    mel = librosa.power_to_db(librosa.feature.melspectrogram(y=mono, sr=tools.RATE, n_mels=96, fmax=16000, hop_length=512), ref=numpy.max)
    spectrogram_axis.imshow(mel, origin="lower", aspect="auto", cmap="magma", vmin=-80, vmax=0, extent=[0, seconds, 0, 16000])
    for label, cue_time in cues:
        for axis in (wave_axis, spectrogram_axis):
            axis.axvline(cue_time, color="#7fff7f", linestyle="--", linewidth=0.6)
        spectrogram_axis.text(cue_time + 0.04, 15600, label[:28], color="white", fontsize=6, rotation=90, va="top")
    spectrogram_axis.set_xlabel("seconds")
    spectrogram_axis.set_ylabel("Hz")
    figure.tight_layout()
    figure.savefig(path, dpi=110)
    pyplot.close(figure)


def sum_stems(stems, padded, length, trigger_mono, carve_trigger, music_offset_db, verbose=False, unmask_db=None):
    """Ducks and carves the music and beds under the voice and cues, lets the voice yield to the cues where it would
    mask them, offsets the music by `music_offset_db`, and sums."""
    total = numpy.zeros((length, 2), dtype=numpy.float32)
    processed = {}
    cues = [padded[name] for name, (spec, _) in stems.items() if spec["role"] == "cue"]
    cue_mono = numpy.sum(cues, axis=0).mean(axis=1) if cues else None
    for name, (spec, _) in stems.items():
        audio = padded[name]
        if spec["role"] == "voice" and cue_mono is not None:
            depth = spec.get("unmask_db", UNMASK_DB if unmask_db is None else unmask_db)
            audio, yielded_ms = unmask_voice(audio, cue_mono, depth)
            if verbose and depth:
                print(f"unmask voice {name}: yields up to {depth:.1f} dB under the cues, {yielded_ms} ms touched")
        if spec["role"] in DEFAULT_DUCK_DB:
            audio = audio * tools.db_to_gain(music_offset_db)
            if trigger_mono is not None:
                gain = sidechain_gain(trigger_mono, spec.get("duck_db", DEFAULT_DUCK_DB[spec["role"]]))
                gain = numpy.pad(gain, (0, max(0, length - len(gain))), mode="edge")[:length]
                audio = audio * gain[:, None]
        carve_db = spec.get("carve_db", DEFAULT_CARVE_DB)
        if spec["role"] == "duck" and carve_trigger is not None and carve_db:
            audio = carve(audio, carve_trigger, carve_db)
        processed[name] = audio
        total += audio
        if verbose:
            print(f"stem {name:8s} role {spec['role']:5s} {stereo_loudness(padded[name]):6.1f} LUFS before ducking")
    return total, processed


def print_master_checks(final, processed, roles):
    """The whole-mix checks from the research; each prints a FLAG when it fails. Returns the number of flags."""
    flags = 0
    integrated = stereo_loudness(final)
    short_term = short_term_max_lufs(final)
    over = short_term - integrated
    too_loud_moment = over > SHORT_TERM_OVER_INTEGRATED_LU
    flags += int(too_loud_moment)
    print(f"short-term max {short_term:.1f} LUFS, {over:+.1f} LU over integrated"
          + (f"  FLAG over +{SHORT_TERM_OVER_INTEGRATED_LU} LU: a loud moment will jump out" if too_loud_moment else ""))
    loss = mono_loss_db(final)
    flags += int(loss > MONO_LOSS_FLAG_DB)
    print(f"mono fold-down {loss:+.1f} dB" + ("  FLAG wide or out-of-phase content" if loss > MONO_LOSS_FLAG_DB else ""))
    voices = [audio for name, audio in processed.items() if roles[name] == "voice"]
    music = [audio for name, audio in processed.items() if roles[name] in ("duck", "bed")]
    if voices and music:
        ratio = voice_over_music_lu(numpy.sum(voices, axis=0), numpy.sum(music, axis=0))
        if ratio is not None:
            flags += int(ratio < VOICE_OVER_MUSIC_LU)
            print(f"voice over music and beds while speaking {ratio:+.1f} LU"
                  + (f"  FLAG under {VOICE_OVER_MUSIC_LU} LU: lower the music or duck deeper"
                     if ratio < VOICE_OVER_MUSIC_LU else ""))
    return flags


def main():
    library.lower_priority()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("mix")
    parser.add_argument("--out", required=True)
    parser.add_argument("--no-listen", action="store_true", help="skip the per-stem listen checks")
    parser.add_argument("--quick", action="store_true", help="skip only the CLAP listening of stems alone; keep the "
                        "sync, masking and margin checks on the final")
    parser.add_argument("--sheet", help="write a PNG: waveform and spectrogram of the final mix with the expected cues marked")
    arguments = parser.parse_args()
    base = Path(arguments.mix).parent
    mix = json.loads(Path(arguments.mix).read_text(encoding="utf-8"))
    global HOLD_MS
    HOLD_MS = int(mix.get("hold_ms", HOLD_MS))  # ab_test.py renders variants this way
    unmask_db = mix.get("unmask_db")  # global override, also from ab_test.py

    stems = {spec["name"]: (spec, load_stem(spec, base)) for spec in mix["stems"]}
    length = max(len(audio) for _, audio in stems.values())
    padded = {name: numpy.pad(audio, ((0, length - len(audio)), (0, 0))) for name, (_, audio) in stems.items()}
    triggers = [padded[name] for name, (spec, _) in stems.items() if spec["role"] in ("cue", "voice")]
    trigger_mono = numpy.sum(triggers, axis=0).mean(axis=1) if triggers else None
    voices = [padded[name] for name, (spec, _) in stems.items() if spec["role"] == "voice"]
    carve_trigger = numpy.sum(voices, axis=0).mean(axis=1) if voices else trigger_mono

    total, processed = sum_stems(stems, padded, length, trigger_mono, carve_trigger, 0.0, verbose=True,
                                 unmask_db=unmask_db)
    roles = {name: spec["role"] for name, (spec, _) in stems.items()}
    if mix.get("auto_level", True):
        voices_processed = [processed[name] for name, role in roles.items() if role == "voice"]
        under = [processed[name] for name, role in roles.items() if role in ("duck", "bed")]
        if voices_processed and under:
            ratio = voice_over_music_lu(numpy.sum(voices_processed, axis=0), numpy.sum(under, axis=0))
            if ratio is not None and ratio < VOICE_OVER_MUSIC_LU:
                lowered = VOICE_OVER_MUSIC_LU + AUTO_LEVEL_MARGIN_LU - ratio
                print(f"auto level: voice was {ratio:+.1f} LU over the music, music and beds lowered {lowered:.1f} dB")
                total, processed = sum_stems(stems, padded, length, trigger_mono, carve_trigger, -lowered,
                                             unmask_db=unmask_db)

    final, ceiling, codec_peaks = master_for_codecs(total, mix.get("target_lufs", -14.0),
                                                    mix.get("true_peak_db", DEFAULT_TRUE_PEAK_DB),
                                                    mix.get("codec_check", True))
    tools.write_wav(arguments.out, final)
    mono = final.mean(axis=1)
    print(f"\nFINAL {arguments.out}  {length / tools.RATE:.2f}s  integrated {stereo_loudness(final):.2f} LUFS "
          f"(target {mix.get('target_lufs', -14.0)}), true peak {true_peak_stereo_db(final):.2f} dBTP "
          f"(ceiling {ceiling:.2f}), sample peak {library.to_db(numpy.abs(final).max()):.2f} dBFS")
    if codec_peaks:
        over = max(codec_peaks.values()) > DECODED_PEAK_LIMIT_DB
        print("after encoding: " + ", ".join(f"{name} {peak:+.2f} dBTP" for name, peak in codec_peaks.items())
              + (f"  FLAG still over {DECODED_PEAK_LIMIT_DB} dBTP" if over else ""))
    master_flags = print_master_checks(final, processed, roles)
    master_flags += int(bool(codec_peaks) and max(codec_peaks.values()) > DECODED_PEAK_LIMIT_DB)
    loudness_miss = stereo_loudness(final) - mix.get("target_lufs", -14.0)
    if abs(loudness_miss) > 0.5:
        master_flags += 1
        print(f"FLAG loudness {loudness_miss:+.1f} LU off target: the codec check forced the ceiling to {ceiling:.2f} "
              "dBTP; aim lower or tame the peaks (transient-heavy music) before mastering")
    expectations = expectations_for(mix, base)
    if arguments.sheet:
        write_sheet(arguments.sheet, final, [(label, t) for _, label, t in expectations])
        print(f"sheet written to {arguments.sheet}")
    if arguments.no_listen:
        print(f"\n{master_flags} whole-mix flag(s); per-cue listening skipped")
        return

    total_problems = master_flags
    if not arguments.quick:
        clap = library.ClapBundle()
        for name, (spec, _) in stems.items():
            cues = [(label, t) for stem, label, t in expectations if stem == name]
            if not cues:
                continue
            print(f"\n===== listen: stem '{name}' alone ({len(cues)} cues) =====")
            stem_mono = padded[name].mean(axis=1)
            total_problems += listen.report_cues(stem_mono, tools.RATE, cues, 1.0, clap, check_masking=False)
        clap.release()

    print("\n===== listen: final mix, sync and masking by the other stems =====")
    levels = listen.band_levels_db(mono, tools.RATE)
    roles = {name: spec["role"] for name, (spec, _) in stems.items()}
    cue_stems = [name for name, role in roles.items() if role == "cue"]
    music = [audio for name, audio in processed.items() if roles[name] == "duck"]
    music_levels = a_weighted_levels_db(numpy.sum(music, axis=0).mean(axis=1)) if music else None
    voice_stems = [audio for name, audio in processed.items() if roles[name] == "voice"]
    voice_levels = a_weighted_levels_db(numpy.sum(voice_stems, axis=0).mean(axis=1)) if voice_stems else None
    margins_over_voice = []
    cue_level_cache = {}
    margins_over_music = []
    for stem, label, t in expectations:
        error_ms = listen.find_onset_error_ms(mono, tools.RATE, t)
        margins, dominant = listen.masking_margins(levels, tools.RATE, t, 1.0)
        error_text = "no onset" if error_ms is None else f"{error_ms:+.0f} ms"
        # Event cues are listed under "foley"; measure them on the mix's cue stem when no stem has that name.
        cue_stem = stem if stem in processed else (cue_stems[0] if cue_stems else None)
        over_music = None
        if music_levels is not None and cue_stem is not None:
            if cue_stem not in cue_level_cache:
                cue_level_cache[cue_stem] = a_weighted_levels_db(processed[cue_stem].mean(axis=1))
            over_music = margin_over_music(cue_level_cache[cue_stem], music_levels, t)
        music_text = "" if over_music is None else f", {over_music:+5.1f} dB(A) over the music"
        if voice_levels is not None and cue_stem is not None:
            if cue_stem not in cue_level_cache:
                cue_level_cache[cue_stem] = a_weighted_levels_db(processed[cue_stem].mean(axis=1))
            over_voice = margin_over_music(cue_level_cache[cue_stem], voice_levels, t)
            if over_voice is not None:
                margins_over_voice.append(over_voice)
                music_text += f", {over_voice:+5.1f} over the voice"
        if over_music is not None:
            margins_over_music.append(over_music)
        share = phone_share(processed[cue_stem].mean(axis=1), t) if cue_stem is not None else None
        weak_on_phone = share is not None and share < PHONE_WEAK_SHARE
        total_problems += int(weak_on_phone)
        under_music = over_music is not None and over_music < QUIET_UNDER_MUSIC_DB
        total_problems += int(under_music)
        print(f"  {t:6.2f}s {label[:34]:34s} onset {error_text:>8s}  strongest band {dominant:4s} "
              f"{margins[dominant]:+5.1f} dB over the surrounding bed{music_text}"
              + ("  MASKED" if max(margins.values()) < listen.MASKING_MARGIN_DB else "")
              + ("  QUIET UNDER MUSIC" if under_music else "")
              + (f"  WEAK ON PHONE ({share:.0%} above 200 Hz; try phone_bass)" if weak_on_phone else ""))
    if margins_over_music:
        print(f"lowest cue margin over the music: {min(margins_over_music):+.1f} dB(A)")
    if margins_over_voice:
        print(f"cue margin over the voice: lowest {min(margins_over_voice):+.1f}, median "
              f"{float(numpy.median(margins_over_voice)):+.1f} dB(A)")
    print(f"\n{total_problems} thing(s) to check across the stems")


if __name__ == "__main__":
    main()
