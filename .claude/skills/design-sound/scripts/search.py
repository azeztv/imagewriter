"""Find sounds by meaning: CLAP text-to-audio similarity blended with tag/filename keywords.

Run: uv run --no-project --python 3.12 --with numpy --with scipy --with librosa --with soundfile --with pyloudnorm
     --with psutil --with torch --with transformers --with matplotlib python search.py "<description>" [options]
"""
import argparse
import sys
from pathlib import Path

import numpy

sys.path.insert(0, str(Path(__file__).parent))
import sound_library as library

# Chosen from the eval.py table: hybrid kw 2.0 + impact prior 0.5 (25/30 top-1, 26/30 top-5 on 30 queries).
DEFAULT_KEYWORD_WEIGHT = 2.0
DEFAULT_IMPACT_STRENGTH = 0.5


def draw_music_row(wave_axis, spectrogram_axis, record):
    """Energy curve with bars marked (every bar a tick, every fourth numbered), sections shaded, and the mel spectrogram."""
    import librosa
    step = record["energy_step"]
    energy_times = numpy.arange(len(record["energy"])) * step
    wave_axis.fill_between(energy_times, record["energy"], color="#2b6cb0", alpha=0.35, linewidth=0)
    wave_axis.plot(energy_times, record["energy"], linewidth=0.8, color="#2b6cb0")
    wave_axis.set_ylim(0, 1.15)
    wave_axis.set_xlim(0, record["duration"])
    wave_axis.set_yticks([])
    for index, bar_time in enumerate(record["downbeats"]):
        wave_axis.axvline(bar_time, ymax=0.12 if index % 4 else 0.22, color="#444", linewidth=0.5)
        if index % 8 == 0:
            wave_axis.text(bar_time, 1.0, str(index + 1), fontsize=5, color="#444", va="bottom")
    for section_start in record["sections"][1:]:
        wave_axis.axvline(section_start, color="#d97706", linewidth=1.0, linestyle="--")
    samples = library.load_mono(record["path"], seconds=record["duration"], sample_rate=11025)
    mel = librosa.power_to_db(librosa.feature.melspectrogram(y=samples, sr=11025, n_mels=48), ref=numpy.max)
    spectrogram_axis.imshow(mel, origin="lower", aspect="auto", cmap="magma", vmin=-70, vmax=0)
    spectrogram_axis.set_yticks([])
    spectrogram_axis.set_xticks([])


def write_sheet(rows, output_path):
    """One labelled waveform and mel spectrogram per result, so the candidates can be looked at before choosing."""
    import librosa
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as pyplot

    figure, axes = pyplot.subplots(len(rows), 2, figsize=(11, 1.55 * len(rows)), squeeze=False,
                                   gridspec_kw={"width_ratios": [1, 1.4]})
    for row_index, (rank, record, score) in enumerate(rows):
        wave_axis, spectrogram_axis = axes[row_index]
        warning = library.licence_warning(record["licence"])
        if warning:
            print(f"    LICENCE WARNING: {warning}" + (f" (page: {record['origin']})" if record["origin"] else ""))
        if record.get("downbeats"):
            draw_music_row(wave_axis, spectrogram_axis, record)
            wave_axis.set_title(f"#{rank} {record['name']}  [{record['licence']}]  {record['duration']:.0f}s  "
                                f"{record['bpm']:.0f} bpm  {record['lufs']} LUFS  score {score:.2f}  "
                                f"(ticks = bars, dashed = sections)", fontsize=7, loc="left", pad=2)
            continue
        samples = library.load_mono(record["path"], seconds=8, sample_rate=22050)
        times = numpy.arange(len(samples)) / 22050
        wave_axis.plot(times, samples, linewidth=0.5, color="#2b6cb0")
        wave_axis.set_ylim(-1, 1)
        wave_axis.set_yticks([])
        wave_axis.set_title(f"#{rank} {record['name']}  [{record['licence']}]  {record['duration']:.1f}s  "
                            f"attack {record['attack_ms']:.0f}ms  {record['centroid_hz']}Hz  score {score:.2f}",
                            fontsize=7, loc="left", pad=2)
        mel = librosa.power_to_db(librosa.feature.melspectrogram(y=samples, sr=22050, n_mels=64), ref=numpy.max)
        spectrogram_axis.imshow(mel, origin="lower", aspect="auto", cmap="magma", vmin=-70, vmax=0,
                                extent=[0, max(times[-1], 0.01) if len(times) else 1, 0, 64])
        spectrogram_axis.set_yticks([])
        for axis in (wave_axis, spectrogram_axis):
            axis.tick_params(labelsize=6)
    figure.tight_layout(pad=0.4)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=110)
    pyplot.close(figure)


def main():
    library.lower_priority()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("query")
    parser.add_argument("--n", type=int, default=8)
    parser.add_argument("--kind", choices=["oneshot", "bed", "music"])
    parser.add_argument("--licence", choices=["cc0", "public", "any"], default="any",
                        help="any (default) shows everything and warns; public = cc0, cc-by or ElevenLabs only")
    parser.add_argument("--max-seconds", type=float)
    parser.add_argument("--min-seconds", type=float, help="shortest track to show (music)")
    parser.add_argument("--bpm", help="tempo range such as 90-120 (music only; tracks without a tempo are hidden)")
    parser.add_argument("--sheet", help="write a PNG with a waveform and spectrogram per result")
    parser.add_argument("--keyword-weight", type=float, default=DEFAULT_KEYWORD_WEIGHT)
    parser.add_argument("--impact-strength", type=float, default=DEFAULT_IMPACT_STRENGTH)
    arguments = parser.parse_args()

    records, vectors = library.load_index()
    if not records:
        sys.exit("The index is empty. Run index.py first.")
    clap = library.ClapBundle()
    query_vector = clap.query_vector(arguments.query, library.QUERY_TEMPLATES_ENSEMBLE)
    clap.release()

    bpm_range = tuple(float(part) for part in arguments.bpm.split("-")) if arguments.bpm else None
    windows = library.load_windows() if arguments.kind == "music" else None
    ranked, aliases, scores, similarity, keyword = library.rank_sounds(
        records, vectors, query_vector, arguments.query, arguments.kind, arguments.licence, arguments.max_seconds,
        arguments.n, arguments.keyword_weight, arguments.impact_strength, arguments.min_seconds, bpm_range, windows)

    sheet_rows = []
    for rank, row in enumerate(ranked, start=1):
        record = records[row]
        shares = record["band_share"]
        print(f"#{rank} score {scores[row]:.2f} (clap {similarity[row]:.3f}, kw {keyword[row]:.1f})  {record['path']}")
        print(f"    {record['kind']} {record['duration']:.2f}s  licence {record['licence']} ({record['licence_text']})  "
              f"attack {record['attack_ms']:.0f}ms  centroid {record['centroid_hz']}Hz  lufs {record['lufs']}  "
              f"bands sub {shares['sub']:.0%} low {shares['low']:.0%} mid {shares['mid']:.0%} high {shares['high']:.0%}")
        if record.get("downbeats"):
            print(f"    {record['bpm']:.0f} bpm, {record['beats_per_bar']}/4, bar {record['bar_seconds']:.2f}s, "
                  f"{len(record['sections'])} sections; page: {record['origin']}")
        if row in aliases:
            print("    same audio under another name: " + ", ".join(records[other]["path"] for other in aliases[row]))
        sheet_rows.append((rank, record, scores[row]))
    if arguments.sheet and sheet_rows:
        write_sheet(sheet_rows, arguments.sheet)
        print(f"sheet written to {arguments.sheet}")


if __name__ == "__main__":
    main()
