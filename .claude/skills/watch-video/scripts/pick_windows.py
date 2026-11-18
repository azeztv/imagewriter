"""Pick which windows of a long video to zoom into for a question, from what is already cheap to read.

Usage:
  uv run --no-project python pick_windows.py --question "<question>" [--terms word word ...] [--folder <watch folder>]
      [--transcript transcript.txt] [--info info.json] [--perception perception.json] [--screen first_seen.txt]
      [--seen 30-60 120-150] [--count 6] [--window 20]

No model: each window of --window seconds (sliding by half) scores from
  - question terms in the transcript and in on-screen text (first_seen.txt from read_screen.py), the strongest signal;
  - the chapter whose title holds a term;
  - YouTube's most-replayed curve (info.json heatmap);
  - how many hard cuts fall in it (perception.json), a weak sign that something happens there.
The opening and the ending are always offered: the hook and the payoff carry the purpose of most videos.
--seen drops windows already read, so a second pass after reading the first picks follows the open questions:
write the new terms with --terms (the cue-revision loop of agentic keyframe selection, without the model).
--folder reads the files watch.py writes (transcript.txt, info.json, perceived/perception.json, screen/first_seen.txt).
Question terms in another language than the video find nothing: pass --terms in the video's language.
Writes windows.md next to the inputs when --folder is given, else prints only.
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TERM_WEIGHT = 3.0
SCREEN_WEIGHT = 2.0
CHAPTER_WEIGHT = 2.0
REPLAY_WEIGHT = 2.0
CUT_WEIGHT = 0.5
MINIMUM_SHARE_OF_BEST = 0.2  # a window under this share of the best score is noise, not a lead
STOPWORDS = set("""a an the and or but if of to in on at by for with from into over under about as is are was were be been
being it its this that these those what which who whom whose when where why how do does did done can could should would
will shall may might must i you he she we they me him her us them my your his our their there here than then so not no
yes video clip show shows shown does doing make made like just only also very much many more most some any each
get got gets use used using say says said tell told know want need thing things way one two come comes came go goes""".split())
TIME_LINE = re.compile(r"^\[(?P<minutes>\d+):(?P<seconds>\d{2})(?:\.\d+)?\]\s*(?P<text>.*)$")


def clock(seconds):
    whole = int(seconds)
    return f"{whole // 60:02d}:{whole % 60:02d}"


def question_terms(question, extra_terms):
    words = re.findall(r"[\w'%-]+", (question or "").lower())
    terms = [word for word in words if len(word) > 2 and word not in STOPWORDS]
    terms += [term.lower() for term in extra_terms or []]
    return sorted(set(terms))


def read_timed_lines(path):
    """[(seconds, text)] from '[mm:ss] text' lines (transcript.txt) or 'mm:ss  text' lines (first_seen.txt)."""
    lines = []
    if not path or not Path(path).exists():
        return lines
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        match = TIME_LINE.match(raw.strip())
        if not match:
            plain = re.match(r"^(?P<minutes>\d+):(?P<seconds>\d{2})\s+(?P<text>.+)$", raw.strip())
            match = plain
        if match:
            lines.append((int(match["minutes"]) * 60 + int(match["seconds"]), match["text"]))
    return lines


def term_hits(text, terms):
    lowered = text.lower()
    return [term for term in terms if term in lowered]


def term_weights(terms, timed_lines, duration, window):
    """Rarer terms count more (inverse document frequency over windows): a word said all through the video points nowhere."""
    import math
    window_count = max(1, int(duration // window) + 1)
    weights = {}
    for term in terms:
        windows_with_term = {int(time // window) for time, text in timed_lines if term in text.lower()}
        weights[term] = math.log((window_count + 1) / (len(windows_with_term) + 1)) + 0.1
    return weights


def score_windows(duration, terms, transcript, screen, chapters, heatmap, cuts, window, seen):
    windows = []
    weights = term_weights(terms, transcript + screen, duration, window)
    step = window / 2
    start = 0.0
    while start < max(duration, window):
        end = min(start + window, duration) if duration else start + window
        if not any(start < seen_end and end > seen_start for seen_start, seen_end in seen):
            reasons = []
            score = 0.0
            spoken = [hit for time, text in transcript if start <= time < end for hit in term_hits(text, terms)]
            if spoken:
                score += TERM_WEIGHT * sum(weights[hit] for hit in spoken)
                reasons.append("said: " + ", ".join(sorted(set(spoken))))
            shown = [hit for time, text in screen if start <= time < end for hit in term_hits(text, terms)]
            if shown:
                score += SCREEN_WEIGHT * sum(weights[hit] for hit in shown)
                reasons.append("on screen: " + ", ".join(sorted(set(shown))))
            for chapter in chapters:
                if chapter.get("start_time", 0) < end and chapter.get("end_time", duration) > start:
                    hits = term_hits(chapter.get("title", ""), terms)
                    if hits:
                        score += CHAPTER_WEIGHT
                        reasons.append(f"chapter \"{chapter['title']}\"")
                        break
            replay = [point["value"] for point in heatmap if point["start_time"] < end and point["end_time"] > start]
            if replay and max(replay) >= 0.5:
                score += REPLAY_WEIGHT * max(replay)
                reasons.append(f"most replayed {max(replay):.2f}")
            cut_count = sum(1 for cut in cuts if start <= cut < end)
            if cut_count:
                score += CUT_WEIGHT * min(cut_count, 6)
                if cut_count >= 4:
                    reasons.append(f"{cut_count} cuts")
            windows.append({"start": start, "end": end, "score": score, "reasons": reasons})
        start += step
    return windows


def pick(windows, count, duration, window):
    """Best windows without overlap, plus the opening and the ending when they were not read yet."""
    chosen = []
    best = max((item["score"] for item in windows), default=0)
    floor = best * MINIMUM_SHARE_OF_BEST
    for candidate in sorted(windows, key=lambda item: -item["score"]):
        if candidate["score"] <= floor or len(chosen) >= count:
            break
        if all(candidate["end"] <= other["start"] or candidate["start"] >= other["end"] for other in chosen):
            chosen.append(candidate)
    for label, edge in (("opening: the hook and the promise", 0.0), ("ending: the payoff and the ask", max(duration - window, 0.0))):
        edge_window = next((item for item in windows if abs(item["start"] - edge) < window / 2), None)
        if edge_window and all(edge_window["end"] <= other["start"] or edge_window["start"] >= other["end"] for other in chosen):
            chosen.append({**edge_window, "reasons": edge_window["reasons"] + [label]})
    return sorted(chosen, key=lambda item: item["start"])


def parse_seen(values):
    seen = []
    for value in values or []:
        first, last = value.split("-")
        seen.append((float(first), float(last)))
    return seen


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--question", default="")
    parser.add_argument("--terms", nargs="*", default=[])
    parser.add_argument("--folder", type=Path)
    parser.add_argument("--transcript", type=Path)
    parser.add_argument("--info", type=Path)
    parser.add_argument("--perception", type=Path)
    parser.add_argument("--screen", type=Path)
    parser.add_argument("--seen", nargs="*", default=[], help="windows already read, as start-end seconds")
    parser.add_argument("--count", type=int, default=6)
    parser.add_argument("--window", type=float, default=20.0)
    arguments = parser.parse_args()

    folder = arguments.folder
    transcript_path = arguments.transcript or (folder / "transcript.txt" if folder else None)
    info_path = arguments.info or (folder / "info.json" if folder else None)
    perception_path = arguments.perception or (folder / "perceived" / "perception.json" if folder else None)
    screen_path = arguments.screen or (folder / "screen" / "first_seen.txt" if folder else None)

    info = json.loads(info_path.read_text(encoding="utf-8")) if info_path and info_path.exists() else {}
    perception = json.loads(perception_path.read_text(encoding="utf-8")) if perception_path and perception_path.exists() else {}
    transcript = read_timed_lines(transcript_path)
    screen = read_timed_lines(screen_path)
    duration = float(info.get("duration") or perception.get("duration") or 0)
    if not duration:
        times = [time for time, text in transcript + screen] + perception.get("cuts", [])
        duration = max(times, default=0) + arguments.window
    terms = question_terms(arguments.question, arguments.terms)
    windows = score_windows(duration, terms, transcript, screen, info.get("chapters") or [], info.get("heatmap") or [],
                            perception.get("cuts", []), arguments.window, parse_seen(arguments.seen))
    chosen = pick(windows, arguments.count, duration, arguments.window)

    lines = [f"# Windows to zoom into ({clock(duration)} video)", "",
             f"Terms: {', '.join(terms) if terms else 'none (pass --question or --terms)'}",
             f"Sources: transcript {len(transcript)} lines, screen {len(screen)} lines, chapters {len(info.get('chapters') or [])}, "
             f"replay curve {'yes' if info.get('heatmap') else 'no'}, cuts {len(perception.get('cuts', []))}", ""]
    for item in chosen:
        reasons = "; ".join(item["reasons"]) or "coverage"
        lines.append(f"- {clock(item['start'])}-{clock(item['end'])}  (score {item['score']:.1f})  {reasons}  "
                     f"zoom: --from {item['start']:.0f} --to {item['end']:.0f} --fps 8")
    lines += ["", "After reading these: list what is still unanswered, then run again with --seen "
              + " ".join(f"{item['start']:.0f}-{item['end']:.0f}" for item in chosen) + " and new --terms."]
    text = "\n".join(lines) + "\n"
    print(text)
    if folder:
        (folder / "windows.md").write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
