"""Index registered sound folders in place: CLAP embedding, loudness, attack, spectrum, kind guess, tags, licence.

Run: uv run --no-project --python 3.12 --with numpy --with scipy --with librosa --with soundfile --with pyloudnorm
     --with psutil --with torch --with transformers python index.py [--add <folder>]... [--rebuild]
Incremental: a file is measured again only when its size or modification time changed.
"""
import argparse
import sys
import time
from pathlib import Path

import numpy

sys.path.insert(0, str(Path(__file__).parent))
import music_analysis
import sound_library as library

BATCH_SIZE = 8


def list_audio_files(folder):
    return sorted(path for path in Path(folder).rglob("*") if path.suffix.lower() in library.AUDIO_EXTENSIONS)


def build_record(path, folder, manifest_entries):
    import soundfile
    entry = manifest_entries.get(path.name, {})
    try:
        info = soundfile.info(str(path))
        full_duration = info.duration
    except RuntimeError:
        import librosa
        full_duration = librosa.get_duration(path=str(path))
    samples = library.load_mono(path, seconds=library.ANALYSIS_SECONDS)
    measures = library.measure_audio(samples, library.CLAP_SAMPLE_RATE, full_duration)
    tags = library.build_tags(path.relative_to(folder), entry)
    raw_licence = entry.get("license") or entry.get("licence") or ""
    stats = path.stat()
    record = {
        "path": library.normalize_path(path),
        "name": path.stem,
        "source_folder": library.normalize_path(folder),
        "size": stats.st_size,
        "mtime": int(stats.st_mtime),
        "tags": tags,
        "licence": library.classify_licence(raw_licence),
        "licence_text": raw_licence or "unknown",
        "author": entry.get("author", ""),
        "origin": entry.get("page") or entry.get("source") or "",
    }
    record.update(measures)
    record["kind"] = library.guess_kind(measures, tags)
    clip = samples[: library.CLAP_SAMPLE_RATE * library.CLAP_CLIP_SECONDS]
    return record, clip


def is_music_entry(entry, folder):
    return "music_tags" in entry or (library.LIBRARY_DIRECTORY / "music").resolve() in Path(folder).resolve().parents


def build_music_record(path, folder, manifest_entries, clap):
    """A music track: the usual measures plus tempo, beats, downbeats, sections, energy curve, and CLAP windows.

    Returns (record, window starts, window vectors). The record's own vector is the mean of its windows.
    """
    entry = manifest_entries.get(path.name, {})
    record, _ = build_record(path, folder, manifest_entries)
    record["kind"] = "music"
    record["lufs"] = round(library.integrated_loudness(library.load_mono(path, sample_rate=44100), 44100), 1)
    record.update(music_analysis.analyse_music(path, entry.get("bpm")))
    record["source_bpm"] = entry.get("bpm")
    samples = library.load_mono(path, sample_rate=library.CLAP_SAMPLE_RATE)
    starts = music_analysis.window_starts_for(record["duration"])
    window_length = library.CLAP_SAMPLE_RATE * library.CLAP_CLIP_SECONDS
    clips = [samples[int(start * library.CLAP_SAMPLE_RATE):][:window_length] for start in starts]
    vectors = numpy.concatenate([clap.embed_clips(clips[first:first + BATCH_SIZE])
                                 for first in range(0, len(clips), BATCH_SIZE)])
    record["window_starts"] = starts
    return record, numpy.array(starts), vectors


def index_music(pending, clap, windows):
    records, vectors = [], []
    for number, (path, folder_path, manifest_entries) in enumerate(pending, start=1):
        try:
            record, starts, window_vectors = build_music_record(path, folder_path, manifest_entries, clap)
        except Exception as error:
            print(f"skipped {path.name}: {error}")
            continue
        mean_vector = window_vectors.mean(axis=0)
        vectors.append(mean_vector / numpy.linalg.norm(mean_vector))
        windows[record["path"]] = (starts, window_vectors)
        records.append(record)
        print(f"music {number}/{len(pending)} {path.name} {record['bpm']} bpm", flush=True)
    return records, vectors


def main():
    library.lower_priority()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--add", action="append", default=[], help="register another folder to index")
    parser.add_argument("--rebuild", action="store_true", help="measure every file again")
    arguments = parser.parse_args()

    folders = library.load_sources()
    for added in arguments.add:
        normalized = library.normalize_path(added)
        if normalized not in folders:
            folders.append(normalized)
    library.save_sources(folders)

    records, vectors = ([], numpy.zeros((0, 512), dtype=numpy.float32)) if arguments.rebuild else library.load_index()
    windows = {} if arguments.rebuild else library.load_windows()
    known = {record["path"]: row for row, record in enumerate(records)}

    pending = []
    seen_paths = set()
    entry_by_path = {}
    for folder in folders:
        folder_path = Path(folder)
        if not folder_path.exists():
            print(f"missing folder, skipped: {folder}")
            continue
        manifest_entries = library.read_manifest_entries(folder_path)
        for path in list_audio_files(folder_path):
            normalized = library.normalize_path(path)
            seen_paths.add(normalized)
            entry_by_path[normalized] = manifest_entries.get(path.name, {})
            row = known.get(normalized)
            stats = path.stat()
            unchanged = row is not None and records[row]["size"] == stats.st_size and records[row]["mtime"] == int(stats.st_mtime)
            if not unchanged:
                pending.append((path, folder_path, manifest_entries))

    kept_rows = [row for row, record in enumerate(records) if record["path"] in seen_paths
                 and record["path"] not in {library.normalize_path(item[0]) for item in pending}]
    records_kept = [records[row] for row in kept_rows]
    vectors_kept = vectors[kept_rows] if len(kept_rows) else numpy.zeros((0, 512), dtype=numpy.float32)
    print(f"{len(records_kept)} unchanged, {len(pending)} to index, {sum(1 for record in records if record['path'] not in seen_paths)} gone")

    new_records, new_vectors = [], []
    pending_music = [item for item in pending if is_music_entry(item[2].get(item[0].name, {}), item[1])]
    pending = [item for item in pending if item not in pending_music]
    if pending or pending_music:
        clap = library.ClapBundle()
        print(f"device {clap.device}", flush=True)
        started = time.time()
        music_records, music_vectors = index_music(pending_music, clap, windows)
        new_records += music_records
        new_vectors += [numpy.stack(music_vectors)] if music_vectors else []
        for first in range(0, len(pending), BATCH_SIZE):
            batch_records, batch_clips = [], []
            for path, folder_path, manifest_entries in pending[first:first + BATCH_SIZE]:
                try:
                    record, clip = build_record(path, folder_path, manifest_entries)
                except Exception as error:  # a corrupt file must not stop the whole run
                    print(f"skipped {path.name}: {error}")
                    continue
                batch_records.append(record)
                batch_clips.append(clip)
            if batch_clips:
                new_vectors.append(clap.embed_clips(batch_clips))
                new_records += batch_records
            print(f"{min(first + BATCH_SIZE, len(pending))}/{len(pending)} in {time.time() - started:.0f} s", flush=True)
        clap.release()

    all_records = records_kept + new_records
    # Licences follow the manifest and the current rules without re-measuring: a manifest added later, or a rule
    # change (CC BY-NC files were once classed cc-by), reaches every record on the next run.
    for record in all_records:
        entry = entry_by_path.get(record["path"], {})
        raw_licence = entry.get("license") or entry.get("licence")
        if raw_licence:
            record["licence_text"] = raw_licence
            record["author"] = entry.get("author", record.get("author", ""))
            record["origin"] = entry.get("page") or entry.get("source") or record.get("origin", "")
        record["licence"] = library.classify_licence(record["licence_text"])
    all_vectors = numpy.concatenate([vectors_kept] + new_vectors) if new_vectors else vectors_kept
    present = {record["path"] for record in all_records}
    library.save_index(all_records, all_vectors.astype(numpy.float32),
                       {path: value for path, value in windows.items() if path in present})

    by_kind, by_licence = {}, {}
    for record in all_records:
        by_kind[record["kind"]] = by_kind.get(record["kind"], 0) + 1
        by_licence[record["licence"]] = by_licence.get(record["licence"], 0) + 1
    print(f"indexed {len(all_records)} files; kinds {by_kind}; licences {by_licence}")
    print(f"index at {library.INDEX_FILE}")


if __name__ == "__main__":
    main()
