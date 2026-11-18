"""Work with a video recipe: the beats, sound cues and rules learned from a reference video.

    check    <recipe.json> <perception.json> [rebuild]   does the recipe match what perceive.py measured?
    graybox  <recipe.json> <out.mp4>           render the recipe alone as a grey-box animatic with synthetic cues
    compare  <a/perception.json> <b/perception.json>   timing of two videos side by side (reference and remake)
    retime   <recipe.json> <seconds> <out.json>        the same recipe stretched or squeezed to a new length

Usage: uv run --no-project --with numpy --with pillow python recipe.py <command> ...
"""
import json
import math
import subprocess
import sys
import wave
from pathlib import Path

import numpy
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# "hold" keeps the backdrop and changes what sits on it (new words, a new card), so no cut or fade is measured.
ENTERS = ("start", "cut", "fade", "wipe", "morph", "hold")
SOFT_ENTERS = ("fade", "wipe", "morph")
EVIDENCE = ("measured", "seen", "inferred")
# What a beat is made of, which decides the tool that can build it (references/recipe.md has the table).
TECHNIQUES = ("type", "ui", "graphic", "image", "3d", "footage")
CUT_TOLERANCE_SECONDS = 0.12
CUE_TOLERANCE_SECONDS = 0.12
# A riser, whoosh or held tone swells in, so where it "starts" depends on the mix.
SLOW_KINDS = ("riser", "whoosh", "tone", "sketch", "gather")
SLOW_CUE_TOLERANCE_SECONDS = 0.4
QUIET_CUE_DECIBELS = -20.0
MOVE_SEARCH_SECONDS = 0.5
LOUD_DECIBELS = -15.0
SILENCE_OVERLAP = 0.6
LONG_SILENCE_SECONDS = 1.0
FRAME_RATE = 25
FRAME_SIZE = (960, 540)
BAND_HEIGHT = 216
LONG_TRANSITION_SECONDS = 1.0
# The grey box's sounds only mark where cues fall; keep them quiet and soft-edged.
PLACEHOLDER_LEVEL = 0.35
TEXT_MARGIN = 48
TEXT_SIZES = (44, 36, 30, 24)
AUDIO_RATE = 48000
BACKDROPS = {"gradient": (201, 166, 224), "light": (230, 230, 230), "dark": (28, 28, 28),
             "footage": (125, 139, 111), "ui": (143, 211, 240)}
BAND_COLOURS = [(232, 93, 117), (66, 135, 245), (247, 181, 0), (46, 170, 120), (150, 90, 220), (240, 120, 40)]
FONT_FILES = ["C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/System/Library/Fonts/Helvetica.ttc"]


def fail(message):
    raise SystemExit(f"recipe: {message}")


def load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        fail(f"cannot read {path}: {error}")


def load_recipe(path):
    """Read a recipe and stop on anything a renderer or a later reader could not rely on."""
    recipe = load_json(path)
    duration = recipe.get("source", {}).get("duration")
    beats = recipe.get("beats")
    if not isinstance(duration, (int, float)) or duration <= 0:
        fail("source.duration must be the length of the reference in seconds")
    if not beats:
        fail("beats is empty")
    previous_end = 0.0
    seen = set()
    for beat in beats:
        for key in ("id", "role", "start", "end", "enter", "backdrop", "visual", "evidence"):
            if key not in beat:
                fail(f"beat {beat.get('id', '?')} lacks '{key}'")
        if beat["id"] in seen:
            fail(f"beat id '{beat['id']}' is used twice")
        seen.add(beat["id"])
        if beat["enter"] not in ENTERS:
            fail(f"beat {beat['id']}: enter must be one of {', '.join(ENTERS)}")
        if beat["evidence"] not in EVIDENCE:
            fail(f"beat {beat['id']}: evidence must be one of {', '.join(EVIDENCE)}")
        if beat.get("technique") not in (None, *TECHNIQUES):
            fail(f"beat {beat['id']}: technique must be one of {', '.join(TECHNIQUES)}")
        if abs(beat["start"] - previous_end) > 0.01 or beat["end"] <= beat["start"]:
            fail(f"beat {beat['id']} must start where the one before ends ({previous_end:.2f}) and last a while")
        previous_end = beat["end"]
    if abs(previous_end - duration) > 0.1:
        fail(f"the beats end at {previous_end:.2f} but the reference lasts {duration:.2f}")
    for cue in recipe.get("cues", []):
        for key in ("time", "kind", "length", "level"):
            if key not in cue:
                fail(f"a cue lacks '{key}': {cue}")
        if not 0 <= cue["time"] <= duration:
            fail(f"cue at {cue['time']} lies outside the video")
        if cue.get("on") and cue["on"] not in seen:
            fail(f"cue at {cue['time']} names beat '{cue['on']}', which does not exist")
    for silence in recipe.get("silences", []):
        if not 0 <= silence["start"] < silence["end"] <= duration + 0.1:
            fail(f"silence {silence} lies outside the video")
    return recipe


def cue_times(cue):
    """Every moment one cue sounds: itself, plus its repeats."""
    repeat = cue.get("repeat") or {}
    return [cue["time"] + index * repeat.get("every", 0.0) for index in range(int(repeat.get("count", 1)))]


def nearest(value, candidates):
    return min(candidates, key=lambda candidate: abs(candidate - value)) if candidates else None


def check(recipe_path, perception_path, mode="reference"):
    """mode "rebuild" is for a grey box or a remake measured by perceive.py: soft transitions are not checked,
    because steady movement barely registers in the scene score, and a slow sound may start late."""
    if mode not in ("reference", "rebuild"):
        fail("the third argument of check is 'rebuild' or nothing")
    recipe = load_recipe(recipe_path)
    measured = load_json(perception_path)
    cuts = measured.get("cuts", [])
    moves = measured.get("moves", [])
    onsets = sorted(onset for sound in measured.get("sounds", []) for onset in sound["onsets"])
    problems = []
    unverified = []
    errors = []

    print("picture")
    explained_cuts = set()
    for beat in recipe["beats"]:
        if beat["enter"] == "cut":
            match = nearest(beat["start"], cuts)
            if match is None or abs(match - beat["start"]) > CUT_TOLERANCE_SECONDS:
                problems.append(f"beat {beat['id']} claims a cut at {beat['start']:.2f}, nearest measured: {match}")
                continue
            explained_cuts.add(match)
            errors.append(abs(match - beat["start"]))
            print(f"  ok   cut into {beat['id']:<14} {beat['start']:6.2f}  measured {match:6.2f}")
        if beat["enter"] in SOFT_ENTERS and mode == "reference":
            near = [move for move in moves if move["start"] - MOVE_SEARCH_SECONDS <= beat["start"] <= move["end"] + MOVE_SEARCH_SECONDS]
            if not near:
                problems.append(f"beat {beat['id']} claims a {beat['enter']} at {beat['start']:.2f}, no movement measured there")
                continue
            move = min(near, key=lambda item: abs(item["start"] - beat["start"]))
            print(f"  ok   {beat['enter']:<5} into {beat['id']:<12} {beat['start']:6.2f}  measured moving "
                  f"{move['start']:.2f}-{move['end']:.2f} ({move['end'] - move['start']:.2f} s, recipe says "
                  f"{beat.get('enter_seconds', 0):.2f} s)")
    inner_cuts = [time for beat in recipe["beats"] for time in beat.get("inner_cuts", [])]
    for cut in cuts:
        inside_a_beat = any(abs(cut - time) <= CUT_TOLERANCE_SECONDS for time in inner_cuts)
        # A remake may land a soft transition as a cut; at a beat boundary that is a choice, not a mismatch.
        on_a_boundary = mode == "rebuild" and any(abs(cut - beat["start"]) <= CUT_TOLERANCE_SECONDS for beat in recipe["beats"])
        if cut not in explained_cuts and not inside_a_beat and not on_a_boundary:
            problems.append(f"measured cut at {cut:.2f} is not a beat boundary in the recipe")

    print("sound")
    explained_onsets = []
    for cue in recipe.get("cues", []):
        tolerance = SLOW_CUE_TOLERANCE_SECONDS if cue["kind"] in SLOW_KINDS else CUE_TOLERANCE_SECONDS
        too_quiet_to_measure = mode == "rebuild" and cue["level"] < QUIET_CUE_DECIBELS
        for time in cue_times(cue):
            match = nearest(time, onsets)
            if (match is None or abs(match - time) > tolerance) and too_quiet_to_measure:
                unverified.append(f"cue {cue['kind']} at {time:.2f} ({cue['level']} dB) is too quiet to measure in a mix")
                continue
            if match is None or abs(match - time) > tolerance:
                problems.append(f"cue {cue['kind']} at {time:.2f} has no measured onset within {tolerance} s (nearest {match})")
                continue
            explained_onsets.append(match)
            errors.append(abs(match - time))
        print(f"  cue  {cue['kind']:<7} {cue['time']:6.2f}" + (f" x{cue['repeat']['count']}" if cue.get("repeat") else ""))
    for sound in measured.get("sounds", []):
        covered = any(sound["start"] - CUE_TOLERANCE_SECONDS <= onset <= sound["end"] for onset in explained_onsets)
        if sound["level"] > LOUD_DECIBELS and not covered:
            problems.append(f"loud sound {sound['start']:.2f}-{sound['end']:.2f} ({sound['level']} dB, {sound['register']}) has no cue")
    for silence in recipe.get("silences", []):
        overlap = sum(max(0.0, min(silence["end"], gap["end"]) - max(silence["start"], gap["start"]))
                      for gap in measured.get("silences", []))
        if overlap < SILENCE_OVERLAP * (silence["end"] - silence["start"]):
            problems.append(f"silence {silence['start']:.2f}-{silence['end']:.2f} is mostly not silent in the reference")

    median = sorted(errors)[len(errors) // 2] * 1000 if errors else 0.0
    print(f"matched {len(errors)} timed claims, median error {median:.0f} ms, worst {max(errors, default=0) * 1000:.0f} ms")
    for note in unverified:
        print(f"  UNVERIFIED  {note}")
    for problem in problems:
        print(f"  FIX  {problem}")
    subject = "the recipe agrees with the reference" if mode == "reference" else "the video realises the recipe"
    print(f"PASS: {subject}" if not problems else f"FAIL: {len(problems)} claims to fix")
    return 0 if not problems else 1


def load_font(size):
    for candidate in FONT_FILES:
        if Path(candidate).is_file():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def draw_beat(beat, index, position):
    """One still per beat: backdrop, the text and the notes on a wide colour band.

    Neighbouring stills must differ enough for perceive.py to measure the cut between them, also when two beats
    share a backdrop, so the shade alternates and the band takes a new colour each time."""
    width, height = FRAME_SIZE
    band_top = height - BAND_HEIGHT
    shade = 1.0 if position % 2 == 0 else 0.72
    colour = tuple(int(channel * shade) for channel in BACKDROPS.get(beat["backdrop"], (187, 187, 187)))
    image = Image.new("RGB", FRAME_SIZE, colour)
    draw = ImageDraw.Draw(image)
    draw.rectangle([0, band_top, width, height], fill=BAND_COLOURS[position % len(BAND_COLOURS)])
    ink = (20, 20, 20) if sum(colour) > 380 else (240, 240, 240)
    draw.text((24, 18), f"{index + 1}. {beat['id']}  ·  {beat['role']}  ·  enters by {beat['enter']}", font=load_font(22), fill=ink)
    text = beat.get("text") or ""
    if text:
        font, lines = fit_text(draw, text, width - 2 * TEXT_MARGIN)
        line_height = int(font.size * 1.25)
        top = (band_top - line_height * len(lines)) / 2
        for line_number, line in enumerate(lines):
            line_width = draw.textlength(line, font=font)
            draw.text(((width - line_width) / 2, top + line_height * line_number), line, font=font, fill=ink)
    for line_number, line in enumerate(wrap_text(beat["visual"]) + wrap_text(beat.get("motion") or "")):
        draw.text((24, band_top + 14 + 28 * line_number), line, font=load_font(20), fill=(255, 255, 255))
    return image


def fit_text(draw, text, available_width):
    """The beat's words at the largest size that fits the frame in at most three lines."""
    for size in TEXT_SIZES:
        font = load_font(size)
        lines = []
        for word in text.split():
            candidate = f"{lines[-1]} {word}" if lines else word
            if lines and draw.textlength(candidate, font=font) <= available_width:
                lines[-1] = candidate
            else:
                lines.append(word)
        fits = all(draw.textlength(line, font=font) <= available_width for line in lines)
        if fits and len(lines) <= 3:
            return font, lines
    return font, lines[:3]


def wrap_text(text, width=96):
    words = text.split()
    lines = []
    for word in words:
        if lines and len(lines[-1]) + 1 + len(word) <= width:
            lines[-1] += " " + word
        else:
            lines.append(word)
    return lines[:3]


def still_positions(beats):
    """Which shade and band each beat gets. A "hold" keeps its neighbour's, so it does not read as a cut."""
    positions = []
    position = -1
    for beat in beats:
        if beat["enter"] != "hold":
            position += 1
        positions.append(position)
        position += len(beat.get("inner_cuts", []))
    return positions


def synthesize(cue, time):
    """A stand-in sound of the right kind, length and level, so timing can be heard and measured."""
    length = max(0.02, cue["length"])
    count = int(length * AUDIO_RATE)
    clock = numpy.arange(count) / AUDIO_RATE
    decay = numpy.exp(-5.0 * clock / length)
    noise = numpy.random.default_rng(int(time * 1000)).standard_normal(count)
    pitch = cue.get("pitch")
    kind = cue["kind"]
    if kind == "bass":
        wave_form = numpy.sin(2 * math.pi * (pitch or 70) * clock) * decay
    elif kind == "blip":
        wave_form = numpy.sin(2 * math.pi * (pitch or 880) * clock) * decay
    elif kind == "tone":
        wave_form = numpy.sin(2 * math.pi * (pitch or 440) * clock) * numpy.minimum(1.0, numpy.minimum(clock, length - clock) * 20)
    elif kind == "click":
        wave_form = numpy.convolve(noise, numpy.ones(12) / 12, mode="same") * numpy.exp(-clock * 90)
    elif kind in ("riser", "whoosh"):
        # Both start audibly, so the measured onset sits at the cue time and not somewhere up the swell.
        swell = clock / length if kind == "riser" else numpy.sin(math.pi * clock / length)
        shape = 0.25 + 0.75 * swell
        wave_form = numpy.convolve(noise, numpy.ones(160) / 160, mode="same") * 4 * shape
    else:
        thump = numpy.sin(2 * math.pi * 140 * clock) * decay
        wave_form = thump + numpy.convolve(noise, numpy.ones(200) / 200, mode="same") * 4 * decay
    # A few milliseconds of fade at both ends: a sound that starts or stops mid-wave clicks harshly.
    fade = min(count // 2, int(0.004 * AUDIO_RATE))
    if fade:
        wave_form[:fade] *= numpy.linspace(0.0, 1.0, fade)
        wave_form[-fade:] *= numpy.linspace(1.0, 0.0, fade)
    peak = numpy.abs(wave_form).max() or 1.0
    return wave_form / peak * PLACEHOLDER_LEVEL * 10 ** (min(0.0, cue["level"]) / 20.0)


def render_sound(recipe, path):
    total = numpy.zeros(int(recipe["source"]["duration"] * AUDIO_RATE) + AUDIO_RATE, dtype=numpy.float64)
    for cue in recipe.get("cues", []):
        for time in cue_times(cue):
            sound = synthesize(cue, time)
            begin = int(time * AUDIO_RATE)
            total[begin:begin + len(sound)] += sound[:len(total) - begin]
    total = total[:int(recipe["source"]["duration"] * AUDIO_RATE)]
    samples = (numpy.clip(total, -1.0, 1.0) * 32767).astype(numpy.int16)
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(AUDIO_RATE)
        output.writeframes(samples.tobytes())


def frame_at(number, beats, stills):
    time = number / FRAME_RATE
    index = next((position for position, beat in enumerate(beats) if beat["start"] <= time < beat["end"]), len(beats) - 1)
    beat = beats[index]
    passed_inner_cuts = sum(1 for cut in beat.get("inner_cuts", []) if time >= cut)
    still = stills[index][min(passed_inner_cuts, len(stills[index]) - 1)]
    progress = (time - beat["start"]) / beat["enter_seconds"] if beat.get("enter_seconds") else 1.0
    if index == 0 or beat["enter"] not in SOFT_ENTERS or progress >= 1.0:
        return still
    before = stills[index - 1][-1]
    if beat["enter_seconds"] > LONG_TRANSITION_SECONDS:
        # A long blend of two stills is unreadable; show the new one with a bar that fills while it arrives.
        frame = still.copy()
        bar_top = FRAME_SIZE[1] - BAND_HEIGHT - 12
        ImageDraw.Draw(frame).rectangle([0, bar_top, int(FRAME_SIZE[0] * progress), bar_top + 12], fill=(20, 20, 20))
        return frame
    if beat["enter"] == "wipe":
        frame = before.copy()
        edge = int(FRAME_SIZE[0] * progress)
        frame.paste(still.crop((0, 0, edge, FRAME_SIZE[1])), (0, 0))
    else:
        frame = Image.blend(before, still, progress)
    return frame


def graybox(recipe_path, output_path):
    recipe = load_recipe(recipe_path)
    output = Path(output_path).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    sound_path = output.with_suffix(".wav")
    render_sound(recipe, sound_path)
    beats = recipe["beats"]
    positions = still_positions(beats)
    stills = [[draw_beat(beat, index, positions[index] + variant) for variant in range(1 + len(beat.get("inner_cuts", [])))]
              for index, beat in enumerate(beats)]
    encoder = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{FRAME_SIZE[0]}x{FRAME_SIZE[1]}",
         "-r", str(FRAME_RATE), "-i", "-", "-i", str(sound_path), "-c:v", "libx264", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-shortest", str(output)], stdin=subprocess.PIPE)
    for number in range(int(recipe["source"]["duration"] * FRAME_RATE)):
        encoder.stdin.write(frame_at(number, beats, stills).tobytes())
    encoder.stdin.close()
    if encoder.wait() != 0:
        fail("ffmpeg could not encode the grey box")
    sound_path.unlink()
    print(f"grey box: {output} ({len(beats)} beats, {len(recipe.get('cues', []))} cues)")
    return 0


def match_times(label, first, second, tolerance):
    offsets = []
    missing = []
    for time in first:
        match = nearest(time, second)
        if match is None or abs(match - time) > tolerance:
            missing.append(time)
        else:
            offsets.append(match - time)
    extra = [time for time in second if nearest(time, first) is None or abs(nearest(time, first) - time) > tolerance]
    median = sorted(abs(offset) for offset in offsets)[len(offsets) // 2] * 1000 if offsets else 0.0
    print(f"{label}: {len(offsets)} of {len(first)} line up, median offset {median:.0f} ms, "
          f"worst {max((abs(offset) for offset in offsets), default=0) * 1000:.0f} ms")
    for time in missing:
        print(f"  only in the first:  {time:.2f}")
    for time in extra:
        print(f"  only in the second: {time:.2f}")
    return len(missing) + len(extra)


def match_spans(label, first, second, padding):
    """Spans line up when they overlap. Two mixes rarely split their sounds at the same places, so starts differ."""
    def overlaps(span, others):
        return any(span[0] - padding <= other[1] and other[0] - padding <= span[1] for other in others)

    missing = [span for span in first if not overlaps(span, second)]
    extra = [span for span in second if not overlaps(span, first)]
    print(f"{label}: {len(first) - len(missing)} of {len(first)} have a counterpart")
    for span in missing:
        print(f"  only in the first:  {span[0]:.2f}-{span[1]:.2f}")
    for span in extra:
        print(f"  only in the second: {span[0]:.2f}-{span[1]:.2f}")
    return len(missing) + len(extra)


def compare(first_path, second_path):
    """Line up cuts, loud sounds and long silences of two videos. A different length is compared in proportion."""
    first = load_json(first_path)
    second = load_json(second_path)
    scale = first["duration"] / second["duration"]
    if abs(scale - 1.0) > 0.02:
        print(f"lengths differ ({first['duration']:.1f} s and {second['duration']:.1f} s): the second is scaled by {scale:.3f}")

    def loud_spans(data, factor):
        return [(sound["start"] * factor, sound["end"] * factor) for sound in data.get("sounds", [])
                if sound["level"] > LOUD_DECIBELS]

    def long_silences(data, factor):
        return [(gap["start"] * factor, gap["end"] * factor) for gap in data.get("silences", [])
                if gap["end"] - gap["start"] >= LONG_SILENCE_SECONDS]

    differences = match_times("cuts", first.get("cuts", []), [cut * scale for cut in second.get("cuts", [])], 0.25)
    differences += match_spans("loud sounds", loud_spans(first, 1.0), loud_spans(second, scale), 0.25)
    differences += match_spans("long silences", long_silences(first, 1.0), long_silences(second, scale), 0.0)
    print("same timing" if differences == 0 else f"{differences} moments differ; read each one, some are a choice")
    return 0


def retime(recipe_path, seconds, output_path):
    recipe = load_recipe(recipe_path)
    factor = float(seconds) / recipe["source"]["duration"]
    recipe["source"] = dict(recipe["source"], duration=float(seconds), retimed_from=recipe["source"]["duration"])
    for beat in recipe["beats"]:
        beat["start"], beat["end"] = round(beat["start"] * factor, 3), round(beat["end"] * factor, 3)
        if "enter_seconds" in beat:
            beat["enter_seconds"] = round(beat["enter_seconds"] * factor, 3)
        if "inner_cuts" in beat:
            beat["inner_cuts"] = [round(cut * factor, 3) for cut in beat["inner_cuts"]]
    for cue in recipe.get("cues", []):
        cue["time"] = round(cue["time"] * factor, 3)
        cue["length"] = round(cue["length"] * factor, 3)
        if cue.get("repeat"):
            cue["repeat"]["every"] = round(cue["repeat"]["every"] * factor, 3)
    for silence in recipe.get("silences", []):
        silence["start"], silence["end"] = round(silence["start"] * factor, 3), round(silence["end"] * factor, 3)
    recipe["beats"][-1]["end"] = float(seconds)
    Path(output_path).write_text(json.dumps(recipe, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"retimed by {factor:.3f} to {float(seconds):.1f} s: {output_path}")
    return 0


COMMANDS = {"check": (check, 2), "graybox": (graybox, 2), "compare": (compare, 2), "retime": (retime, 3)}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        fail("usage: recipe.py check|graybox|compare|retime ... (see the top of this file)")
    function, count = COMMANDS[sys.argv[1]]
    optional = 1 if sys.argv[1] == "check" else 0
    if not 2 + count <= len(sys.argv) <= 2 + count + optional:
        fail(f"{sys.argv[1]} takes {count} arguments")
    raise SystemExit(function(*sys.argv[2:]))


main()
