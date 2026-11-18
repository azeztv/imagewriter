# Music (real tracks first, score.py for sketches)

<!-- skill-navigation:start -->
## Reading map

- [Music (real tracks first, score.py for sketches)](#music-real-tracks-first-scorepy-for-sketches)
- [Real tracks](#real-tracks)
- [The library](#the-library)
- [Search](#search)
- [fit_music.py](#fit_musicpy)
- [Credits](#credits)
- [score.py (sketch only)](#scorepy-sketch-only)
- [Score format](#score-format)
- [Writing a score from a film's beats](#writing-a-score-from-a-films-beats)
- [Owner verdicts that apply here](#owner-verdicts-that-apply-here)
- [Limits](#limits)
<!-- skill-navigation:end -->

Not for finished music (2026-10-29, on the pass 2 demo: the effects were fine, the music was weak). A score built
from repitched one-shots sounds like a MIDI sketch. Use it only as a timing sketch or a placeholder. Finished music
comes from a produced recording, either a track the owner names or one picked from the library by mood, then edited to the cut.

## Real tracks

1. `search.py "<mood in plain words>" --kind music [--min-seconds 60] [--bpm 90-130] --sheet sheet.png`, look at the
   sheet (energy curve, ticks = bars, dashed = sections), read the rows (tempo, time signature, licence, page).
2. `fit_music.py <track> --duration <film seconds> [--cues cues.json] --out music.wav` edits it to the cut (below).
3. Mix `music.wav` as a `duck` stem (`references/mix.md`), then write the credit line (Credits below).

## The library

`sound-library/music/` holds one folder per source, each with a `manifest.json`; `sources.json`
key `music` lists every track with its URL, licence and exact credit line. Any licence may be added; anything other
than CC0, CC BY or ElevenLabs is warned (`sources.md`, Licence policy). New music also comes from ElevenLabs
(`generate_elevenlabs.py music`, or `plan` then `music --plan` to land sections on the cuts) or a named track via
`fetch_web.py --source youtube`.

- `incompetech/` Kevin MacLeod, CC BY 4.0 (credit required). `scripts/fetch_music.py` picks a mood-balanced set from
  the site's `pieces.json` (feel and genre tags, BPM) and downloads it.
- `opengameart/` CC0 music from OpenGameArt (no credit needed). `scripts/fetch_oga.py`; it keeps a track only when its
  own page lists CC0.
- More: add a folder with a `manifest.json` (`file`, `title`, `author`, `license`, `source`, `page`, `bpm`, `music_tags`),
  then `index.py --add <folder>`. Folders under `music/` are indexed as `kind=music`.

Index fields added for music: `bpm`, `beats_per_bar`, `bar_seconds`, `beats`, `downbeats`, `constant_tempo`,
`sections` (novelty segmentation snapped to downbeats), `energy` (0 to 1 every 0.5 s), `lufs`, and CLAP vectors over
up to 8 ten-second windows (`embeddings.npz` keys `window_*`) beside the whole-track vector. Downbeats are the best of
3 or 4 beats per bar by onset strength and harmonic change; they are an estimate, not ground truth.

## Search

Score = CLAP (half whole track, half the best window) + BM25 over the source's tags. Mood words in the brief are
expanded to the sources' words (`MOOD_SYNONYMS` in `sound_library.py`: tense to suspenseful/intense/unnerving, calm to
calming/relaxed, playful to humorous/bouncy ...). Add a synonym there when a brief word finds nothing.

## fit_music.py

Cues: `[{"t": 10.0, "want": "downbeat|drop|silence|end"}]`; `silence` may carry `"until"`. Method: split the film at
silences into parts (each part is its own edit, entering on a downbeat); choose the source bars (a section start for a
`downbeat` cue, the biggest loudness rise for `drop`, otherwise a steady window that ends on a phrase end); repeat or
drop whole bars, jumping only to the bar that best follows the end of the previous one (chroma and MFCC) and joining
with a 40 ms equal-power crossfade centred on the downbeat; stretch the part by at most 4% with ffmpeg atempo so the
cue lands on a bar line; end on a cosine fade over the last bar (or the track's own ending). Tracks whose tempo is
not constant get each downbeat snapped to the nearest onset within 25 ms.

The report (`<out>.report.json`) lists per part the source bars, anchor, stretch, joins, and the self-check measured
on the output: drift in ms of the beat grid across each join (onset-strength grid fit of the two bars before and after),
the click ratio (largest step within 3 ms of the join against the 99th percentile step around it; over 2.5 flags), the
tracked tempo against the expected one, and the onset error at each downbeat/drop cue. `drift` over 20 ms or a flagged
click means look and listen. These are measurements; nobody has heard the result until someone listens.

## Credits

CC BY needs the credit wherever the video is published: put the credit line from `sources.json` (field `credit`) in the
post or the video description, and write it in `CREDITS.txt` next to the mix. CC0 needs none; credit anyway when asked.
Example line: `"Unity" Kevin MacLeod (incompetech.com)`, then `Licensed under Creative Commons: By Attribution 4.0
License`, then `http://creativecommons.org/licenses/by/4.0/`.

## score.py (sketch only)

`PY score.py score.json --out music.wav [--bank-root <bank folder>] [--seed 11]` writes the WAV and the same score as
`music.mid` next to it (format 1, one track per instrument), so it can be opened, edited or replaced. `PY` needs numpy,
scipy, soundfile, psutil only. Instruments are the CC0 Versilian recordings through the Bank in `scripts/bank_samples.py`
(repitch to the note, measured tuning corrections): `piano` (soft layer below energy ~0.6, loud layer above),
`marimba` (med/loud), `pizz` (contrabass, two round robins alternated), `kick`, `clap`, `shaker`. Timing is humanised
+-8 ms and level +-0.8 dB, seeded. Worked example: `examples/score-example.json` (14.5 s, rendered in
`sound-library/demos/pass2/`).

## Score format

- `tempo` bpm, `beats_per_bar`, `duration` seconds (the render ends there with a 0.4 s fade), `key` (a note for you).
- `sections`: `{start, end, energy 0..1, energy_to?, instruments[]}` in seconds, on the edit's cuts. `energy_to` ramps
  linearly. Energy 0 or an empty list is silence. Energy sets loudness (-24 dB at 0 to 0 dB at 1 per note) and the
  velocity layer.
- `chords`: `{beat, name, bass, notes[]}` in beats from 0, scientific pitch (`"A3"`). A chord lasts until the next
  one; `notes: []` is a rest.
- `motifs`: name -> list of `[midi, beat_offset, length_beats, velocity?]`.
- `phrases`: `{motif, beat, instrument, transpose?}` places a motif; this is where the melody is written.

## Writing a score from a film's beats

1. List the cuts and the big moment. Pick the tempo so that the cuts you care about land on beats:
   `beats = cut_seconds x tempo / 60` should be (nearly) whole; 120 bpm puts every half second on a beat, 96 puts
   0.625 s. Convert the big moment to a beat and put a chord change or a phrase start there.
2. Sections follow the story: set energy per shot group, ramp (`energy_to`) through a build, drop to 0 for the silence
   before the big moment (1 to 2 s reads as held breath; end the previous chord's length so nothing rings into it), and
   resume lower afterwards. Leave the moment itself to the foley.
3. Write a 2 to 4 bar motif (3 to 6 notes, one long note, a rhythm that is not all eighths). Develop it, never loop it:
   second statement a third higher, then a fragment (first two notes, augmented), or an inversion; change the
   instrument or octave when the energy changes. The example uses `a`, `a_up`, `a_frag`.
4. Chords: four chords of one bar each cycle fine; keep voicings 3 to 4 notes between A3 and G4, bass an octave or two
   below. The script adds a chord per `chords` entry on the piano and, from the energy, a bass on `pizz` (beat 1 at
   energy 0.2, beat 3 at 0.5, off-beat 0.8), a kick (0.6, beats 1 and 3 at 0.8), claps (0.8) and shaker (0.7).
5. End on the last cut: last chord at the final bar, a short motif fragment over it, `duration` = the last cut.
6. Render, open `music.mid` if the melody needs checking, then mix.

## Owner verdicts that apply here

No synthesised drones; no reverb; note answers on events sound scary (the music may be music, the events get object
sounds); a launch or trailer with a licensed track skips this script entirely.

## Limits

Sample coverage is sparse (marimba 20 files, piano one round robin) so notes far from a recording are repitched and sound
thinner. Chord voicings are block chords, not arpeggios; write arpeggios as a motif and a phrase. There is no
orchestration beyond the six instruments.
