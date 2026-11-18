"""Plan the pieces a video-to-audio foley model generates, one text prompt per shot (stdlib only).

HunyuanVideo-Foley hears the frames and reads a text prompt together, but one call takes one prompt and at most
15 s. A shot list gives each stretch of the film its own prompt:

    [
      {"start": 0.0, "prompt": "wet mud squelching under rubber boots", "neg": "music, speech"},
      {"start": 6.4, "prompt": "gravel poured from a wheelbarrow onto mud, stones rattling"},
      {"start": 14.0, "end": 20.0, "prompt": "shovel scraping gravel, steady rain on a road"}
    ]

`end` defaults to the next shot's start (the last shot runs to the end of the film). `neg` defaults to the
command's --neg. Stretches between shots get no foley. Inside a shot, pieces overlap by --overlap and crossfade;
at a cut between shots the pieces overlap by only --cut-fade, so one shot's sound does not smear into the next.
"""
import json


def load_shots(path, duration, default_prompt, default_neg):
    with open(path, encoding="utf-8") as handle:
        raw_shots = json.load(handle)
    if isinstance(raw_shots, dict):
        raw_shots = raw_shots.get("shots", [])
    if not raw_shots:
        raise SystemExit(f"{path}: no shots")
    raw_shots = sorted(raw_shots, key=lambda shot: float(shot["start"]))
    shots = []
    for index, raw in enumerate(raw_shots):
        start = max(0.0, float(raw["start"]))
        if "end" in raw:
            end = float(raw["end"])
        elif index + 1 < len(raw_shots):
            end = float(raw_shots[index + 1]["start"])
        else:
            end = duration
        end = min(end, duration)
        prompt = raw.get("prompt") or default_prompt
        if not prompt:
            raise SystemExit(f"{path}: shot at {start:.2f} s has no prompt and no --prompt was given")
        if end - start < 0.5:
            raise SystemExit(f"{path}: shot at {start:.2f} s is shorter than 0.5 s")
        shots.append({"start": start, "end": end, "prompt": prompt, "neg": raw.get("neg", default_neg)})
    for previous, current in zip(shots, shots[1:]):
        if current["start"] < previous["end"] - 1e-6:
            raise SystemExit(f"{path}: shots at {previous['start']:.2f} s and {current['start']:.2f} s overlap")
    return shots


def split_span(start, end, chunk_seconds, overlap_seconds):
    if end - start <= chunk_seconds:
        return [(start, end)]
    spans = []
    piece_start = start
    while piece_start < end:
        piece_end = min(piece_start + chunk_seconds, end)
        spans.append((piece_start, piece_end))
        if piece_end >= end:
            break
        piece_start = piece_end - overlap_seconds
    return spans


def plan_pieces(shots, duration, chunk_seconds, overlap_seconds, cut_fade_seconds):
    """Returns pieces as dicts with start, end, prompt, neg and shot index, in time order."""
    pieces = []
    half_fade = cut_fade_seconds / 2
    for index, shot in enumerate(shots):
        start = shot["start"]
        end = shot["end"]
        touches_previous = index > 0 and abs(shots[index - 1]["end"] - start) < 1e-6
        touches_next = index + 1 < len(shots) and abs(shots[index + 1]["start"] - end) < 1e-6
        if touches_previous:
            start = max(0.0, start - half_fade)
        if touches_next:
            end = min(duration, end + half_fade)
        for piece_start, piece_end in split_span(start, end, chunk_seconds, overlap_seconds):
            pieces.append({
                "start": piece_start,
                "end": piece_end,
                "prompt": shot["prompt"],
                "neg": shot["neg"],
                "shot": index,
            })
    return pieces


def single_prompt_pieces(duration, prompt, neg, chunk_seconds, overlap_seconds):
    shots = [{"start": 0.0, "end": duration, "prompt": prompt, "neg": neg}]
    return plan_pieces(shots, duration, chunk_seconds, overlap_seconds, 0.0)


def fade_lengths(pieces):
    """Seconds of fade-in and fade-out for each piece: the real overlap with its neighbour, 0 at a gap."""
    fades = []
    for index, piece in enumerate(pieces):
        fade_in = 0.0
        fade_out = 0.0
        if index > 0:
            fade_in = max(0.0, pieces[index - 1]["end"] - piece["start"])
        if index + 1 < len(pieces):
            fade_out = max(0.0, piece["end"] - pieces[index + 1]["start"])
        fades.append((fade_in, fade_out))
    return fades
