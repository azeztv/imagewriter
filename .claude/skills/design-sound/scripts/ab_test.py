"""Blind listening test for the mix values only the owner's ears can set, and the record of the pick.

The agent never tunes these values itself: what needs listening is the owner's call. It renders the
same mix two ways (the house value and one step away, widened until the two are audibly different), shuffles the
labels, sends the files, and writes the value the owner picks into house-defaults.json.

  make <mix.json> --param hold|cue|unmask --out-dir DIR [--step S] [--seed N]
      hold: the duck's hold in ms (step +400); listen for the music pumping between words.
      cue:  the quietest cue's margin over the music in dB(A) (step +6): the cue
            stems' gain is set from a first render so each variant lands there; listen for buried or loud effects.
      unmask: how far the voice yields under the cues, in dB, only where it would mask them (step -4);
            listen for effects that read clearly while the voice still sounds whole.
      The step doubles (up to 3 times) until the renders differ by at least 20 dB under the mix; a mix that cannot
      show the parameter exits without files. Writes DIR/A.mp3, B.mp3 and DIR/key.json (the answer key; do not
      read it out before the owner picks).
  pick DIR <A|B|same> [--note "the owner's words"]
      same: the house value stays, the history notes that the owner heard no difference.
      hold: house hold_ms = the picked value. cue: house cue_margin_dba = the picked variant's measured lowest cue
      margin, rounded down to 0.5 dB, so a later cue quieter than where the owner wants effects gets flagged.
      unmask: house unmask_db = the picked depth.

Run: PY ab_test.py ... (the design-sound PY line; mix.py runs with --quick for each variant)
"""
import argparse
import json
import math
import random
import re
import subprocess
import sys
import time
from pathlib import Path

import numpy
import soundfile

SCRIPTS = Path(__file__).parent
HOUSE_DEFAULTS_FILE = SCRIPTS.parent / "house-defaults.json"
DEFAULT_STEPS = {"hold": 400.0, "cue": 6.0, "unmask": -4.0}
AUDIBLE_DIFFERENCE_DB = -20.0
WIDEN_ATTEMPTS = 3
HOUSE_KEYS = {"hold": "hold_ms", "cue": "cue_margin_dba", "unmask": "unmask_db"}


def absolute_mix(mix_path):
    """The mix with every file path made absolute, so a variant can live in another folder."""
    base = Path(mix_path).resolve().parent
    mix = json.loads(Path(mix_path).read_text(encoding="utf-8"))
    for stem in mix["stems"]:
        stem["file"] = str((base / stem["file"]).resolve())
    if mix.get("expect_from_events"):
        mix["expect_from_events"] = str((base / mix["expect_from_events"]).resolve())
    return mix


def variant_mix(mix, parameter, value, baseline_margin=None):
    """hold: the value is the hold in ms. cue: the value is the target lowest margin; the cue gain moves by the
    distance from the baseline render's margin (nearly linear: the cue stem itself is never ducked)."""
    variant = json.loads(json.dumps(mix))
    if parameter == "hold":
        variant["hold_ms"] = int(value)
        return variant
    if parameter == "unmask":
        variant["unmask_db"] = float(value)
        return variant
    cue_stems = [stem for stem in variant["stems"] if stem["role"] == "cue"]
    if not cue_stems:
        sys.exit("the mix has no cue stem to vary")
    for stem in cue_stems:
        stem["gain_db"] = stem.get("gain_db", 0.0) + float(value) - baseline_margin
    return variant


def render(variant, folder, name):
    mix_path = folder / f"{name}.mix.json"
    wav_path = folder / f"{name}.wav"
    mix_path.write_text(json.dumps(variant, indent=1), encoding="utf-8")
    result = subprocess.run([sys.executable, str(SCRIPTS / "mix.py"), str(mix_path), "--out", str(wav_path), "--quick"],
                            capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode:
        sys.exit(f"mix.py failed for {name}:\n{result.stderr[-2000:]}")
    margin = re.search(r"lowest cue margin over the music: ([+-][\d.]+)", result.stdout)
    return wav_path, float(margin.group(1)) if margin else None


def difference_db(first_path, second_path):
    """How far under the mix the sample-wise difference of two renders sits, in dB (less negative = easier to hear)."""
    first = soundfile.read(first_path)[0].mean(axis=1)
    second = soundfile.read(second_path)[0].mean(axis=1)
    length = min(len(first), len(second))
    difference = first[:length] - second[:length]
    return float(20 * numpy.log10(numpy.sqrt(numpy.mean(difference ** 2)) / numpy.sqrt(numpy.mean(first[:length] ** 2))))


def make(arguments):
    folder = Path(arguments.out_dir)
    folder.mkdir(parents=True, exist_ok=True)
    defaults = json.loads(HOUSE_DEFAULTS_FILE.read_text(encoding="utf-8"))
    current = float(defaults[HOUSE_KEYS[arguments.param]])
    step = float(arguments.step) if arguments.step else DEFAULT_STEPS[arguments.param]
    mix = absolute_mix(arguments.mix)
    baseline_margin = None
    if arguments.param == "cue":
        _, baseline_margin = render(mix, folder, "baseline")
        if baseline_margin is None:
            sys.exit("no cue margin in the baseline (the mix needs a cue stem, a music stem and expected cues)")
        print(f"baseline lowest cue margin {baseline_margin:+.1f} dB(A)")
    current_wav, current_margin = render(variant_mix(mix, arguments.param, current, baseline_margin), folder, "current")
    # Widen the other variant until the two differ audibly: the owner heard no difference at 25-40 dB under the mix
    # (hold and cue sets, 2026-11-07) and could choose at 18 dB (unmask set).
    for attempt in range(WIDEN_ATTEMPTS):
        other = current + step * (2 ** attempt)
        if arguments.param == "hold":
            other = max(0.0, other)
        other_wav, other_margin = render(variant_mix(mix, arguments.param, other, baseline_margin), folder, "other")
        apart = difference_db(current_wav, other_wav)
        print(f"{arguments.param} {current:g} vs {other:g}: difference {apart:.1f} dB under the mix")
        if apart >= AUDIBLE_DIFFERENCE_DB:
            break
    else:
        sys.exit(f"even {other:g} is under {AUDIBLE_DIFFERENCE_DB} dB apart from {current:g}: this mix cannot show "
                 f"'{arguments.param}', so do not send it; keep the house value")
    letters = ["A", "B"]
    random.Random(arguments.seed).shuffle(letters)
    key = {"param": arguments.param, "mix": str(Path(arguments.mix).resolve()), "made": time.strftime("%Y-%m-%d %H:%M"),
           "difference_db": round(apart, 1), "variants": {}}
    for letter, value, wav_path, margin in [(letters[0], current, current_wav, current_margin),
                                            (letters[1], other, other_wav, other_margin)]:
        mp3_path = folder / f"{letter}.mp3"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wav_path), "-b:a", "192k", str(mp3_path)], check=True)
        key["variants"][letter] = {"value": value, "lowest_cue_margin_dba": margin}
        print(f"wrote {mp3_path}")
    (folder / "key.json").write_text(json.dumps(key, indent=1), encoding="utf-8")
    question = {"hold": "which one has the music breathing least between words, without sounding stuck down?",
                "cue": "in which one do the effects sit right: heard, not sticking out?",
                "unmask": "in which one are the effects clearest while the voice still sounds natural?"}[arguments.param]
    print(f"send A and B to the owner and ask: {question} (or: they sound the same)")
    print(f"then: ab_test.py pick {folder} <A|B|same> --note \"<the owner's words>\"")


def pick(arguments):
    folder = Path(arguments.dir)
    key = json.loads((folder / "key.json").read_text(encoding="utf-8"))
    letter = arguments.letter.upper()
    house_key = HOUSE_KEYS[key["param"]]
    if letter == "SAME":
        record_same(key, house_key, arguments.note)
        return
    if letter not in key["variants"]:
        sys.exit(f"no variant {letter}; there are {', '.join(sorted(key['variants']))}")
    chosen = key["variants"][letter]
    if key["param"] == "hold":
        new_value = int(chosen["value"])
    elif key["param"] == "unmask":
        new_value = float(chosen["value"])
    else:
        if chosen["lowest_cue_margin_dba"] is None:
            sys.exit("this test has no cue margin (no music stem?); nothing to record")
        new_value = math.floor(chosen["lowest_cue_margin_dba"] * 2) / 2
    defaults = json.loads(HOUSE_DEFAULTS_FILE.read_text(encoding="utf-8"))
    old_value = defaults.get(house_key)
    defaults[house_key] = new_value
    defaults.setdefault("history", []).append({
        "date": time.strftime("%Y-%m-%d"), "key": house_key, "value": new_value, "was": old_value,
        "why": f"Picked {letter} of {len(key['variants'])} blind ({key['param']} {chosen['value']}) on "
               f"{Path(key['mix']).name}" + (f": {arguments.note}" if arguments.note else "")})
    HOUSE_DEFAULTS_FILE.write_text(json.dumps(defaults, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"{house_key}: {old_value} -> {new_value}  (answer key: " + ", ".join(
        f"{name}={variant['value']}" for name, variant in sorted(key["variants"].items())) + ")")


def record_same(key, house_key, note):
    """No audible difference: keep the house value and write that down, so the test is not sent again for it."""
    defaults = json.loads(HOUSE_DEFAULTS_FILE.read_text(encoding="utf-8"))
    values = ", ".join(f"{variant['value']:g}" for variant in key["variants"].values())
    defaults.setdefault("history", []).append({
        "date": time.strftime("%Y-%m-%d"), "key": house_key, "value": defaults.get(house_key),
        "why": f"No audible difference between {values} on {Path(key['mix']).name}; value kept"
               + (f": {note}" if note else "")})
    HOUSE_DEFAULTS_FILE.write_text(json.dumps(defaults, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"{house_key}: kept at {defaults.get(house_key)} (no audible difference)")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    make_parser = commands.add_parser("make")
    make_parser.add_argument("mix")
    make_parser.add_argument("--param", choices=sorted(DEFAULT_STEPS), required=True)
    make_parser.add_argument("--out-dir", required=True)
    make_parser.add_argument("--step", help="distance of the second variant from the house value")
    make_parser.add_argument("--seed", type=int, default=int(time.time()))
    pick_parser = commands.add_parser("pick")
    pick_parser.add_argument("dir")
    pick_parser.add_argument("letter")
    pick_parser.add_argument("--note")
    arguments = parser.parse_args()
    if arguments.command == "make":
        make(arguments)
    else:
        pick(arguments)


if __name__ == "__main__":
    main()
