"""Turn a video file into things a model can read: timestamped frame sheets, scene cuts, spectrograms and a
timeline of what the sound does (hits, notes, silences, dips, tempo). Speech goes through {{SKILL_DIR}}/scripts/transcribe.py (Parakeet).

Usage: uv run --no-project --with numpy python perceive.py <video> [--out DIR] [--from SECONDS] [--to SECONDS]
       [--fps FRAMES_PER_SECOND] [--tile-width PIXELS]
"""
import argparse
import json
import math
import re
import subprocess
import sys
from pathlib import Path

import numpy

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SAMPLE_RATE = 16000
WINDOW_SAMPLES = 1024
HOP_SAMPLES = 320
HOP_SECONDS = HOP_SAMPLES / SAMPLE_RATE
SHEET_COLUMNS = 5
SHEET_ROWS = 4
STAMP_STRIP_PIXELS = 24
MAXIMUM_FRAMES = 80
MAXIMUM_CUT_FRAMES = 80
MAXIMUM_CUTS_LISTED = 60
SPECTRAL_BATCH_FRAMES = 20000
SPECTROGRAM_SECONDS = 30
SILENCE_BELOW_TYPICAL_DECIBELS = 40
SILENCE_BELOW_PEAK_DECIBELS = 70
TYPICAL_LEVEL_PERCENTILE = 95
DIP_BELOW_NEIGHBOURS_DECIBELS = 9
DIP_FRAME_HOPS = 5
DIP_NEIGHBOURHOOD_FRAMES = 50
MINIMUM_SILENCE_SECONDS = 0.3
MINIMUM_EVENT_GAP_SECONDS = 0.08
MERGE_GAP_SECONDS = 0.2
CUT_SCORE = 0.2
CUT_ABOVE_NEIGHBOURS = 2.0
# Two dark or similar shots cut together score far below CUT_SCORE (0.04 in the frame eval) but stand out from
# near-zero neighbours; 90 s of real news footage gave no extra cut with this rule (2026-11-07).
LOW_CONTRAST_CUT_SCORE = 0.03
LOW_CONTRAST_ABOVE_NEIGHBOURS = 10.0
MOVE_SCORE = 0.015
MOVE_BRIDGE_FRAMES = 3
MINIMUM_MOVE_SECONDS = 0.2
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
GENERATED_FILES = ("sheet_*.jpg", "cuts_*.jpg", "spectrogram_*.png", "audio_timeline.txt")


def run(command, binary_output=False):
    # Every path is passed in full: a working directory longer than about 250 characters stops Windows from
    # starting the process at all ("The directory name is invalid").
    completed = subprocess.run(command, capture_output=True)
    if completed.returncode != 0:
        raise SystemExit(f"command failed: {' '.join(map(str, command[:6]))} ...\n{completed.stderr.decode('utf-8', 'replace')[-800:]}")
    return completed.stdout if binary_output else completed.stdout.decode("utf-8", "replace")


def clock(seconds):
    minutes, rest = divmod(max(0.0, seconds), 60)
    return f"{int(minutes):02d}:{rest:05.2f}"


def probe(video):
    report = json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(video)]))
    streams = report.get("streams", [])
    picture = next((stream for stream in streams if stream.get("codec_type") == "video"), None)
    sound = next((stream for stream in streams if stream.get("codec_type") == "audio"), None)
    return {"duration": float(report["format"].get("duration", 0.0)), "picture": picture, "sound": sound}


def window_arguments(start, length):
    return ["-ss", f"{start:.3f}", "-t", f"{length:.3f}"]


def clear_generated_files(output):
    """A second run into the same folder must not leave sheets of an earlier window that look like this one's."""
    for pattern in GENERATED_FILES:
        for path in output.glob(pattern):
            path.unlink()


def time_stamp(start):
    # The stamp sits in its own strip under the picture: drawn over the corner it hid logos, captions and small text
    # (a frame eval code near the top-left vanished under it, 2026-11-07).
    return (f"pad=iw:ih+{STAMP_STRIP_PIXELS}:0:0:color=black,"
            f"drawtext=text='%{{pts\\:hms\\:{start:.3f}}}':x=6:y=h-{STAMP_STRIP_PIXELS - 3}:fontsize=20:fontcolor=white")


def write_frame_sheets(video, output, start, length, frames_per_second, tile_width):
    """Grids of evenly spaced frames, each stamped with its time in the source video."""
    # round=up: the default keeps the last frame of the half interval after each stamp, which at 0.1 frames per second
    # shows a picture 5 s later than its stamp says.
    chain = f"fps={frames_per_second:.4f}:round=up,scale={tile_width}:-2,{time_stamp(start)},tile={SHEET_COLUMNS}x{SHEET_ROWS}"
    run(["ffmpeg", "-v", "error", "-y", *window_arguments(start, length), "-i", str(video), "-vf", chain,
         "-q:v", "4", str(output / "sheet_%02d.jpg")])
    return sorted(path.name for path in output.glob("sheet_*.jpg"))


def frame_seconds(picture):
    numerator, _, denominator = picture.get("avg_frame_rate", "0/0").partition("/")
    rate = float(numerator) / float(denominator) if float(denominator or 0) else 0.0
    return 1.0 / rate if rate > 0 else 1.0 / 30.0


def write_cut_sheets(video, output, start, length, cuts, seconds_per_frame, tile_width):
    """The first frame of each new shot: a shot shorter than the sheet spacing would otherwise never be seen."""
    if not cuts:
        return []
    step = max(1, math.ceil(len(cuts) / MAXIMUM_CUT_FRAMES))
    picks = "+".join(f"between(t,{cut - start - 0.001:.3f},{cut - start + seconds_per_frame - 0.002:.3f})" for cut in cuts[::step])
    chain = f"select='{picks}',scale={tile_width}:-2,{time_stamp(start)},tile={SHEET_COLUMNS}x{SHEET_ROWS}"
    run(["ffmpeg", "-v", "error", "-y", *window_arguments(start, length), "-i", str(video), "-vf", chain,
         "-fps_mode", "vfr", "-q:v", "4", str(output / "cuts_%02d.jpg")])
    return sorted(path.name for path in output.glob("cuts_*.jpg"))


def measure_picture_changes(video, start, length):
    """Hard cuts and the stretches where the picture keeps changing, from ffmpeg's frame-to-frame scene score.

    A cut is one frame that differs strongly from the one before. A move is a run of smaller changes: a fade, a
    wipe, a camera push or an animation. Its start and end are the measured length of that transition."""
    raw = run(["ffmpeg", "-v", "error", *window_arguments(start, length), "-i", str(video), "-vf",
               "scale=320:-2,select='gte(scene,0)',metadata=print:file=-", "-an", "-f", "null", "-"])
    times = [float(value) for value in re.findall(r"pts_time:([0-9.]+)", raw)]
    scores = [float(value) for value in re.findall(r"scene_score=([0-9.]+)", raw)]
    count = min(len(times), len(scores))
    cut_indices = set()
    for index in range(count):
        neighbours = scores[max(0, index - 2):index] + scores[index + 1:index + 3]
        stands_alone = not neighbours or scores[index] >= CUT_ABOVE_NEIGHBOURS * max(neighbours)
        quiet_around = max(neighbours, default=0.0)
        low_contrast_cut = scores[index] > LOW_CONTRAST_CUT_SCORE and scores[index] >= LOW_CONTRAST_ABOVE_NEIGHBOURS * max(quiet_around, 1e-4)
        if (scores[index] > CUT_SCORE and stands_alone) or low_contrast_cut:
            cut_indices.add(index)
    moves = []
    run_start = None
    for index in range(count + 1):
        moving = index < count and scores[index] > MOVE_SCORE and index not in cut_indices
        if moving and run_start is None:
            run_start = index
        if moving:
            run_end = index
        still_for = index - run_end if run_start is not None else 0
        if run_start is not None and (index == count or still_for > MOVE_BRIDGE_FRAMES):
            if times[run_end] - times[run_start] >= MINIMUM_MOVE_SECONDS:
                moves.append({"start": start + times[run_start], "end": start + times[run_end],
                              "peak": max(scores[run_start:run_end + 1])})
            run_start = None
    return [start + times[index] for index in sorted(cut_indices)], moves


def write_spectrograms(video, output, start, length):
    """One picture per 30 seconds, so a pixel stays near 20 ms. The time axis of each restarts at zero."""
    names = []
    offset = 0.0
    while offset < length - 0.05:
        piece = min(SPECTROGRAM_SECONDS, length - offset)
        name = f"spectrogram_{int(start + offset):05d}s-{int(math.ceil(start + offset + piece)):05d}s.png"
        run(["ffmpeg", "-v", "error", "-y", *window_arguments(start + offset, piece), "-i", str(video), "-lavfi",
             "showspectrumpic=s=1600x480:legend=1:scale=log:fscale=log:stop=12000", str(output / name)])
        names.append(name)
        offset += SPECTROGRAM_SECONDS
    return names


def read_samples(video, start, length):
    raw = run(["ffmpeg", "-v", "error", *window_arguments(start, length), "-i", str(video), "-vn", "-ac", "1",
               "-ar", str(SAMPLE_RATE), "-f", "s16le", "-"], binary_output=True)
    return numpy.frombuffer(raw, dtype=numpy.int16).astype(numpy.float32) / 32768.0


def spectral_frames(samples):
    frame_count = 1 + max(0, (len(samples) - WINDOW_SAMPLES) // HOP_SAMPLES)
    window = numpy.hanning(WINDOW_SAMPLES).astype(numpy.float32)
    batches = []
    # In batches: one index table for an hour of audio alone takes 1.4 GB.
    for first_frame in range(0, frame_count, SPECTRAL_BATCH_FRAMES):
        batch_size = min(SPECTRAL_BATCH_FRAMES, frame_count - first_frame)
        indices = numpy.arange(WINDOW_SAMPLES)[None, :] + HOP_SAMPLES * (first_frame + numpy.arange(batch_size))[:, None]
        batches.append(numpy.abs(numpy.fft.rfft(samples[indices] * window, axis=1)).astype(numpy.float32))
    return numpy.concatenate(batches)


def decibels(values):
    return 20.0 * numpy.log10(numpy.maximum(values, 1e-9))


def note_name(frequency):
    midi = int(round(69 + 12 * math.log2(frequency / 440.0)))
    return f"{NOTE_NAMES[midi % 12]}{midi // 12 - 1}"


def find_silences(level, floor):
    silences = []
    quiet_since = None
    for index, value in enumerate(list(level) + [0.0]):
        quiet = index < len(level) and value < floor
        if quiet and quiet_since is None:
            quiet_since = index
        if not quiet and quiet_since is not None:
            if (index - quiet_since) * HOP_SECONDS >= MINIMUM_SILENCE_SECONDS:
                silences.append((quiet_since * HOP_SECONDS, index * HOP_SECONDS))
            quiet_since = None
    return silences


def silence_floor(level):
    """Measured from the typical level, not the peak: one loud hit must not turn quiet speech into silence."""
    typical = float(numpy.percentile(level, TYPICAL_LEVEL_PERCENTILE))
    return max(typical - SILENCE_BELOW_TYPICAL_DECIBELS, float(level.max()) - SILENCE_BELOW_PEAK_DECIBELS)


def find_dips(level, floor):
    """Stretches well below what surrounds them but above silence: the pauses in speech over music or room noise."""
    frame_count = len(level) // DIP_FRAME_HOPS
    if frame_count < DIP_NEIGHBOURHOOD_FRAMES:
        return []
    frames = level[:frame_count * DIP_FRAME_HOPS].reshape(frame_count, DIP_FRAME_HOPS).mean(axis=1)
    half = DIP_NEIGHBOURHOOD_FRAMES // 2
    padded = numpy.pad(frames, half, mode="edge")
    windows = numpy.lib.stride_tricks.sliding_window_view(padded, DIP_NEIGHBOURHOOD_FRAMES)
    neighbours = numpy.percentile(windows, 90, axis=1)[:frame_count]
    frame_hop_seconds = DIP_FRAME_HOPS * HOP_SECONDS
    dips = []
    dip_since = None
    for index in range(frame_count + 1):
        dipping = index < frame_count and floor <= frames[index] < neighbours[index] - DIP_BELOW_NEIGHBOURS_DECIBELS
        if dipping and dip_since is None:
            dip_since = index
        if not dipping and dip_since is not None:
            if (index - dip_since) * frame_hop_seconds >= MINIMUM_SILENCE_SECONDS:
                dips.append((dip_since * frame_hop_seconds, index * frame_hop_seconds))
            dip_since = None
    return dips


def find_events(magnitudes, level, floor):
    """Onsets by rising spectral energy, each described by loudness, register, length and pitch when it has one."""
    frequencies = numpy.fft.rfftfreq(WINDOW_SAMPLES, 1.0 / SAMPLE_RATE)
    rise = numpy.maximum(0.0, numpy.diff(numpy.log1p(magnitudes), axis=0)).sum(axis=1)
    rise = numpy.concatenate([[0.0], rise])
    threshold = numpy.median(rise) + 3.0 * (numpy.median(numpy.abs(rise - numpy.median(rise))) + 1e-6)
    minimum_gap = int(MINIMUM_EVENT_GAP_SECONDS / HOP_SECONDS)
    events = []
    last_index = -minimum_gap
    for index in range(1, len(rise) - 1):
        is_peak = rise[index] > threshold and rise[index] >= rise[index - 1] and rise[index] >= rise[index + 1]
        if not is_peak or index - last_index < minimum_gap or level[min(index + 1, len(level) - 1)] < floor:
            continue
        last_index = index
        span = magnitudes[index:index + 3].mean(axis=0) + 1e-9
        power = span ** 2
        peak_index = min(len(level) - 1, index + int(numpy.argmax(level[index:index + 6])))
        end_index = peak_index
        while end_index < len(level) - 1 and level[end_index] > level[peak_index] - 12.0:
            end_index += 1
        shares = [power[(frequencies >= low) & (frequencies < high)].sum() / power.sum()
                  for low, high in ((0, 250), (250, 2000), (2000, SAMPLE_RATE))]
        register = ("low (bass)", "mid", "high")[int(numpy.argmax(shares))]
        flatness = float(numpy.exp(numpy.log(span).mean()) / span.mean())
        dominant = float(frequencies[int(numpy.argmax(span[2:])) + 2])
        pitched = flatness < 0.12 and 60.0 < dominant < 5000.0
        events.append({"time": index * HOP_SECONDS, "level": float(level[peak_index]), "register": register,
                       "seconds": (end_index - index) * HOP_SECONDS,
                       "pitch": f"tonal ~{dominant:.0f} Hz ({note_name(dominant)})" if pitched else "noisy"})
    return events, rise


def merge_into_sounds(events):
    """One swell or rumble fires many onsets; onsets closer than MERGE_GAP_SECONDS become one sound."""
    sounds = []
    for event in events:
        end = event["time"] + event["seconds"]
        previous = sounds[-1] if sounds else None
        if previous and event["time"] - previous["end"] < MERGE_GAP_SECONDS:
            previous["end"] = max(previous["end"], end)
            previous["onsets"].append(event["time"])
            if event["level"] > previous["level"]:
                previous.update(level=event["level"], register=event["register"], pitch=event["pitch"])
        else:
            sounds.append({"time": event["time"], "end": end, "level": event["level"], "onsets": [event["time"]],
                           "register": event["register"], "pitch": event["pitch"]})
    return sounds


def describe_onsets(onsets):
    """How the onsets inside one sound are spaced: a steady pulse reads very differently from a swell."""
    if len(onsets) < 2:
        return ""
    if len(onsets) < 4:
        return f"  ({len(onsets)} onsets inside)"
    gaps = numpy.diff(onsets)
    if gaps.std() < 0.25 * gaps.mean():
        return f"  ({len(onsets)} onsets, evenly every {gaps.mean():.2f} s)"
    return f"  ({len(onsets)} onsets, uneven)"


def estimate_tempo(rise):
    """Beats per minute from the rhythm of the onsets, or None when no pulse stands out."""
    if len(rise) < int(8 / HOP_SECONDS):
        return None
    centered = rise - rise.mean()
    # Through the FFT: direct correlation grows with the square of the length.
    correlation = numpy.fft.irfft(numpy.abs(numpy.fft.rfft(centered, n=2 * len(centered))) ** 2)[:len(centered)]
    shortest, longest = int(60 / 200 / HOP_SECONDS), int(60 / 60 / HOP_SECONDS)
    if correlation[0] <= 0 or longest >= len(correlation):
        return None
    lag = shortest + int(numpy.argmax(correlation[shortest:longest]))
    return 60.0 / (lag * HOP_SECONDS) if correlation[lag] / correlation[0] > 0.3 else None


def write_audio_timeline(video, output, start, length):
    samples = read_samples(video, start, length)
    if len(samples) < WINDOW_SAMPLES:
        return ["audio: too short to analyse"], {"sounds": [], "silences": [], "dips": []}
    magnitudes = spectral_frames(samples)
    level = decibels(numpy.sqrt((magnitudes ** 2).mean(axis=1)) / (WINDOW_SAMPLES / 4))
    floor = silence_floor(level)
    silences = find_silences(level, floor)
    dips = find_dips(level, floor)
    events, rise = find_events(magnitudes, level, floor)
    tempo = estimate_tempo(rise)
    sounds = merge_into_sounds(events)
    entries = [(sound["time"], f"[{clock(start + sound['time'])}-{clock(start + sound['end'])}] sound  "
                f"peak {sound['level'] - level.max():6.1f} dB  {sound['register']:<10}  {sound['pitch']}"
                + describe_onsets(sound["onsets"])) for sound in sounds]
    entries += [(begin, f"[{clock(start + begin)}-{clock(start + end)}] silence  {end - begin:.2f} s") for begin, end in silences]
    entries += [(begin, f"[{clock(start + begin)}-{clock(start + end)}] dip  {end - begin:.2f} s") for begin, end in dips]
    lines = ["# Levels are relative to the loudest moment. 'tonal' means one pitch dominates (a note, a beep, a voice);",
             "# 'noisy' means a broadband sound (a hit, a whoosh, a click). This says what the sound does, not what it is:",
             "# name the source by reading the spectrogram and the frame at the same second.",
             "# 'dip' is a drop well below its surroundings but not silent: usually a pause in speech over music or noise.", ""]
    lines += [text for _, text in sorted(entries)]
    (output / "audio_timeline.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    quiet_seconds = sum(end - begin for begin, end in silences)
    pitched = sum(1 for event in events if event["pitch"] != "noisy")
    summary = [f"audio: {len(sounds)} sounds from {len(events)} onsets ({pitched} tonal), "
               f"{quiet_seconds:.1f} s of silence in {len(silences)} gaps, {len(dips)} dips",
               f"audio: steady pulse near {tempo:.0f} BPM" if tempo else "audio: no steady pulse found"]
    measured = {
        "sounds": [{"start": round(start + sound["time"], 3), "end": round(start + sound["end"], 3),
                    "level": round(sound["level"] - float(level.max()), 1), "register": sound["register"],
                    "pitch": sound["pitch"], "onsets": [round(start + onset, 3) for onset in sound["onsets"]]}
                   for sound in sounds],
        "silences": [{"start": round(start + begin, 3), "end": round(start + end, 3)} for begin, end in silences],
        "dips": [{"start": round(start + begin, 3), "end": round(start + end, 3)} for begin, end in dips],
        "tempo": round(tempo, 1) if tempo else None,
    }
    return summary, measured


def describe_cuts(cuts):
    if not cuts:
        return "picture: hard cuts at none found"
    if len(cuts) > MAXIMUM_CUTS_LISTED:
        return f"picture: {len(cuts)} hard cuts, every time is in perception.json"
    return "picture: hard cuts at " + ", ".join(clock(cut) for cut in cuts)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("video", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--from", dest="start", type=float, default=0.0)
    parser.add_argument("--to", dest="end", type=float)
    parser.add_argument("--fps", type=float)
    parser.add_argument("--tile-width", type=int, default=400)
    arguments = parser.parse_args()

    video = arguments.video.resolve()
    if not video.is_file():
        raise SystemExit(f"no such file: {video}")
    facts = probe(video)
    if facts["picture"] is None and facts["sound"] is None:
        raise SystemExit("the file has no video and no audio stream")
    end = min(arguments.end or facts["duration"], facts["duration"])
    length = end - arguments.start
    if length <= 0:
        raise SystemExit(f"empty window: {arguments.start} to {end} of {facts['duration']:.1f} s")
    output = (arguments.out or video.with_name(video.stem + "-perceived")).resolve()
    output.mkdir(parents=True, exist_ok=True)
    clear_generated_files(output)

    lines = [f"source: {video.name}", f"window: {clock(arguments.start)} to {clock(end)} of {clock(facts['duration'])}"]
    perception = {"source": video.name, "start": arguments.start, "end": end, "duration": facts["duration"],
                  "cuts": [], "moves": [], "sounds": [], "silences": [], "dips": [], "tempo": None}
    if facts["picture"]:
        frames_per_second = arguments.fps or min(2.0, max(0.1, MAXIMUM_FRAMES / length))
        sheets = write_frame_sheets(video, output, arguments.start, length, frames_per_second, arguments.tile_width)
        cuts, moves = measure_picture_changes(video, arguments.start, length)
        cut_sheets = write_cut_sheets(video, output, arguments.start, length, cuts, frame_seconds(facts["picture"]), arguments.tile_width)
        perception["cuts"] = [round(cut, 3) for cut in cuts]
        perception["moves"] = [{key: round(value, 3) for key, value in move.items()} for move in moves]
        perception["width"] = facts["picture"].get("width")
        perception["height"] = facts["picture"].get("height")
        lines += [f"picture: {facts['picture'].get('width')}x{facts['picture'].get('height')}, sheets at "
                  f"{frames_per_second:.2f} frames per second: {', '.join(sheets)}",
                  describe_cuts(cuts),
                  "picture: first frame of each new shot: " + (", ".join(cut_sheets) if cut_sheets else "no cuts"),
                  "picture: moving (fade, wipe, animation) during "
                  + (", ".join(f"{clock(move['start'])}-{clock(move['end'])}" for move in moves) if moves else "nothing")]
    else:
        lines.append("picture: none (audio only)")
    if facts["sound"]:
        summary, measured = write_audio_timeline(video, output, arguments.start, length)
        perception.update(measured)
        lines += summary
        lines.append("audio: spectrograms " + ", ".join(write_spectrograms(video, output, arguments.start, length)))
        lines.append("audio: every sound and silence is in audio_timeline.txt")
    else:
        lines.append("audio: none (silent video)")
    lines.append("measurements for recipe.py: perception.json")
    (output / "perception.json").write_text(json.dumps(perception, indent=1), encoding="utf-8")
    (output / "MANIFEST.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"output: {output}")


main()
