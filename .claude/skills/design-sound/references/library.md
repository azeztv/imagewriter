# Sound library

Reading map: Where it lives, Index fields, Adding a folder, Licences, Search scoring, listen.py checks, Limits.

## Where it lives

`SOUND_LIBRARY_DIR`, default `Documents/sound-library` in the home folder:

- `sources.json` registered folders (default: the library's own `bank/sources`).
- `index.json` one record per file. `embeddings.npz` the CLAP vectors (`paths`, `vectors`, 512 floats each).
- `previews/` free space for contact sheets. Nothing is written inside a source folder.

## Index fields (per file)

`path` absolute, `name`, `source_folder`, `size`, `mtime` (change detection), `duration` s, `peak_db`, `rms_db`,
`lufs` (integrated, first 30 s), `attack_ms` (rise time from 10% to 90% of the peak level; a snap is under 40, a swell
is hundreds), `lead_ms` (silence before the sound starts), `centroid_hz` (brightness), `band_share` (share of energy
in sub <80 Hz, low 80-250, mid 250-4k, high >4k), `tail_drop_db` (peak window minus the last fifth; a big drop means
it decays), `kind`, `tags`, `licence` class, `licence_text`, `author`, `origin` (page or URL).

`kind` is a guess: `music` when a tag names an instrument or music; `oneshot` when 3 s or shorter, or when it
decays by more than 15 dB and is under 12 s; otherwise `bed`. The embedding covers the first 10 s of the file.

`tags` come from the filename and folder words (camelCase split, plural trimmed), and the manifest `role`, `library`
and `title` (ElevenLabs titles are full descriptions, so those files are easy to find by words).

## Adding a folder

`PY index.py --add <folder>`. It registers the folder, then embeds only new or changed files; files that
disappeared are dropped. Put a `manifest.json` in the folder (a list or a name-keyed dict of entries with `file`,
`license`, `author`, `source` or `page`, `title`, `role`) so the licence is known; without one every file is
`unknown`. Do not copy audio into the library; keep it where the project keeps it.

## Licences

`cc0` (also public domain), `cc-by` (credit `author`), `elevenlabs` (generated in the owner's paid account,
commercial use), `restricted` (NC or ND), `other`, `unknown`. Since 2026-11-04 search and foley default to `--licence
any` and print a `LICENCE WARNING` for the last three (policy in `sources.md`); `public` (cc0, cc-by, elevenlabs) and
`cc0` remain for a piece that must be clean. `index.py` re-derives every class from `licence_text` on each run.

## Search scoring

Score = z-score of the CLAP similarity (query phrasings averaged: plain, "the sound of", "a sound effect of",
"a recording of") + keyword weight x BM25 over tags (scaled 0 to 1) + impact prior. The impact prior applies only when
the query contains an impact stem (hit, slam, burst, crack, thud...): it lifts short sharp one-shots and lowers beds.
`eval.py` prints the measured effect of each piece; the defaults in `search.py` follow its table.

Duplicates: two results whose embeddings are closer than 0.999 and whose lengths differ by under 20 ms are the same audio
under two names (e.g. one pack's `glass-break-big.ogg` and `glass-shatter.ogg`). `rank_sounds` in
`sound_library.py` keeps the better-ranked one and lists the other as an alias; `search.py` prints it, `foley.py` never
sees it, so the two names cannot become two "different" layers. The embedding covers the first 10 s only, so two files that
share their first 10 s and differ later would also collapse (the length check makes this unlikely).

## listen.py checks

Per expected cue: CLAP similarity of the window to the label against a ~150-label vocabulary
(`scripts/vocabulary.txt`; add labels there), the onset offset in ms (over 42 ms is flagged, one frame at 24 fps),
window loudness, and the margin over the bed per band (bed = 20th percentile of that band within 3 s around the
cue); a cue under 6 dB above the bed in every band is MASKED, and one weak only in its strongest band is noted.
The label verdict is OK (rank 1-5 of ~150), PLAUSIBLE (6-15) or CHECK. Inside a dense mix CLAP often ranks a true
cue 10 to 50 (it hears the music); check such a cue by cutting the stem alone. Whole file: integrated LUFS, sample and true peak,
silences over 0.5 s below -60 dBFS.

## Limits

- CLAP confuses short impacts and near sounds (a door slam can rank far down); judge hits from the sheet.
- A vocabulary rank is a hint, not a verdict; "CHECK" means look and listen, not that the cue is wrong.
- Onset detection inside dense music can lock onto the beat instead of the cue.
- `kind` and tags are heuristics; fix a wrong record by renaming or adding a manifest entry and re-indexing.

## Music records

Folders under `music/` are indexed as `kind=music` with the extra fields listed in `references/music.md` (tempo, bars,
sections, energy curve, CLAP windows). `search.py --kind music` ranks on half whole-track and half best-window similarity
plus the source's mood tags; `--min-seconds` and `--bpm a-b` filter, `--sheet` draws energy with bars marked.
`sources.json` also keeps a `music` list: path, title, author, URL, licence and the exact credit line per track.
