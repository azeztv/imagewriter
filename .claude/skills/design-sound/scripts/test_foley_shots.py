"""Checks the foley shot planner: python test_foley_shots.py (stdlib only), prints ok or fails with the case."""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from foley_shots import fade_lengths, load_shots, plan_pieces, single_prompt_pieces


def write_shots(shots):
    handle = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
    json.dump(shots, handle)
    handle.close()
    return handle.name


def check(condition, message):
    if not condition:
        raise SystemExit(f"FAIL {message}")


def test_single_prompt_long_film():
    pieces = single_prompt_pieces(30.0, "mud", None, 12.0, 1.0)
    check([(piece["start"], piece["end"]) for piece in pieces] == [(0.0, 12.0), (11.0, 23.0), (22.0, 30.0)],
          f"single prompt split: {pieces}")
    check(fade_lengths(pieces) == [(0.0, 1.0), (1.0, 1.0), (1.0, 0.0)], "single prompt fades")


def test_shots_cut_fade_and_defaults():
    path = write_shots([
        {"start": 6.0, "prompt": "gravel"},
        {"start": 0.0, "prompt": "mud", "neg": "music"},
        {"start": 20.0, "end": 26.0},
    ])
    shots = load_shots(path, 30.0, "rain", "speech")
    check([shot["start"] for shot in shots] == [0.0, 6.0, 20.0], "shots sorted")
    check(shots[1]["end"] == 20.0 and shots[2]["end"] == 26.0, "end from next start and explicit end")
    check(shots[2]["prompt"] == "rain" and shots[1]["neg"] == "speech" and shots[0]["neg"] == "music",
          "default prompt and neg")
    pieces = plan_pieces(shots, 30.0, 12.0, 1.0, 0.08)
    spans = [(round(piece["start"], 2), round(piece["end"], 2), piece["shot"]) for piece in pieces]
    check(spans == [(0.0, 6.04, 0), (5.96, 17.96, 1), (16.96, 20.04, 1), (19.96, 26.0, 2)], f"plan: {spans}")
    fades = [(round(fade_in, 2), round(fade_out, 2)) for fade_in, fade_out in fade_lengths(pieces)]
    check(fades == [(0.0, 0.08), (0.08, 1.0), (1.0, 0.08), (0.08, 0.0)], f"fades: {fades}")


def test_gap_between_shots_has_no_fade():
    path = write_shots([{"start": 0.0, "end": 5.0, "prompt": "a"}, {"start": 8.0, "end": 12.0, "prompt": "b"}])
    pieces = plan_pieces(load_shots(path, 12.0, None, None), 12.0, 12.0, 1.0, 0.08)
    check([(piece["start"], piece["end"]) for piece in pieces] == [(0.0, 5.0), (8.0, 12.0)], "gap kept")
    check(fade_lengths(pieces) == [(0.0, 0.0), (0.0, 0.0)], "no fade across a gap")


def test_rejects_bad_lists():
    for shots, reason in [
        ([{"start": 0.0, "end": 6.0, "prompt": "a"}, {"start": 5.0, "prompt": "b"}], "overlap"),
        ([{"start": 0.0}], "no prompt"),
        ([{"start": 0.0, "end": 0.2, "prompt": "a"}], "too short"),
    ]:
        try:
            load_shots(write_shots(shots), 10.0, None, None)
        except SystemExit:
            continue
        raise SystemExit(f"FAIL accepted a list with {reason}")


if __name__ == "__main__":
    test_single_prompt_long_film()
    test_shots_cut_fade_and_defaults()
    test_gap_between_shots_has_no_fade()
    test_rejects_bad_lists()
    print("ok")
