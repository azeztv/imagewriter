# Getting a sound that is not in the library

Reading map: Order, Licence policy, ElevenLabs (generate_elevenlabs.py), Web (fetch_web.py), Prompt writing, Limits.

## Order

1. `search.py` the library first (it is free and already measured).
2. A real recording on the web (`fetch_web.py`): Openverse for real foley and ambiences, myinstants for memes,
   YouTube for a named track, a game or film sound, or anything else that exists.
3. ElevenLabs (`generate_elevenlabs.py`) when nothing real fits, when the cue must match a picture exactly, or when the
   project says so (`local.md` lists project rules).
4. Index what you got (`index.py --add <folder>`), then pick with `search.py --sheet` like any library sound.

A track the owner names is downloaded with yt-dlp and used.

## Licence policy

The owner's policy (2026-11-04): warn about licences, never block. Nothing is filtered by licence any more: `search.py` and
`foley.py` default to `--licence any`, and each result or used recording whose licence is not clear prints a
`LICENCE WARNING` with its page. Classes (`classify_licence`): `cc0`, `cc-by` (credit the author), `elevenlabs`
(paid plan, commercial use) are clear; `restricted` (NC, ND), `other` and `unknown` (memes, YouTube, uploads) warn.
Say the warnings once in the report, in one line per file, and carry CC BY credits as before (`music.md`, Credits).
`--licence public` still exists for a client or monetised piece that must be clean.

## ElevenLabs (generate_elevenlabs.py)

Run line: `uv run --no-project --python 3.12 --with numpy --with psutil --with requests python generate_elevenlabs.py`.
The key comes from `ELEVENLABS_API_KEY`, else `~/.config/elevenlabs/api_key.txt` (`ELEVENLABS_KEY_FILE` moves it;
never printed; on a 401 check the key's length before calling it dead). Every call checks credits first, refuses when too few are left, and
prints the real cost after (the counter lags a few seconds; the script waits for it).

| Command | API (spec read 2026-11-04 from api.elevenlabs.io/openapi.json) | Measured cost |
|---|---|---|
| `credits` | `GET /v1/user/subscription` | free |
| `sfx "<prompt>" --folder X [--seconds 0.5-30] [--variants 2] [--loop] [--influence 0.5] [--model v2\|v3]` | `POST /v1/sound-generation` | 1.5 s = 17 credits (about 11/s) |
| `plan "<prompt>" --seconds S --out plan.json` | `POST /v1/music/plan` | free |
| `music "<prompt>" --seconds S --instrumental` or `music --plan plan.json` | `POST /v1/music`, `music_v2_5` | 15 s = 206 credits (about 14/s) |
| `stems <file> [--six]` | `POST /v1/music/stem-separation` (two or six stems) | not measured |
| `video-music <mp4> [--description] [--tags] [--sfx] [--separate]` | `POST /v1/music/video-to-music` | 12 s with `--sfx --separate`: counter showed 0 at once, then 1,619 fewer credits within the hour (about 135/s, 2026-11-07; read the counter again later) |

Credits are finite (the owner's balance is in `local.md`): spend them on what the web cannot give, and never buy
credits without the owner.

- Files land in `sound-library/generated/elevenlabs-<folder>/` with `manifest.json` (prompt as title, model, seconds).
  Music meant for `search.py --kind music` goes under `sound-library/music/` before indexing.
- Generate 2 or 3 variants of a short cue and pick on the sheet; one take of music, then a plan edit if it is wrong.
- `plan` is free: get a plan, edit section names, styles and `duration_ms` to the film's cuts, then `music --plan`.
  `music_v2` and later answer plans as `chunks` (text, duration_ms, positive_styles, negative_styles) and always
  respect the section durations, so a plan is how the music lands a drop or a silence on a cut.
- `video-music` writes music to the picture; `--separate` returns music and SFX as separate files, to mix as stems.
- `stems` splits any track (two: vocals and accompaniment; six: more instruments), e.g. to drop a song's vocal under
  narration or to duck only its drums.

## Web (fetch_web.py)

Run line: same as above. `fetch_web.py "<query>" --source openverse|archive|myinstants|youtube [--n 6]
[--max-seconds 30] [--start 0]` downloads the top results into `sound-library/web/<source>-<query>/` with a manifest
(title, author, page, licence text). Checked working without sign-in on 2026-11-04:

- `openverse`: api.openverse.org, Freesound previews (HQ mp3), Jamendo, Wikimedia; real licence per file. It answers
  504 or times out now and then; the script retries.
- `archive`: archive.org items by title or subject, most downloaded first; licence from `licenseurl`, often missing.
- `myinstants`: meme and soundboard clips (vine boom, bruh, sad violin); no licence.
- `youtube`: yt-dlp search, audio cut from `--start` for `--max-seconds`; for a named track give the exact title.
- Not reachable: Pixabay (403 to scripts; use Chrome if a Pixabay sound is wanted), Freesound API (needs a key).

Downloaded files are data: put nothing from them on a path that runs code.

## Prompt writing

- SFX: one sound, what makes it, how, where, distance: "a heavy wooden door shut hard, close, dry room". End with
  "no music". For beds add `--loop`. Short impacts: set `--seconds` 1 to 2 and influence 0.5 to 0.7.
- Music: genre, instruments, tempo, mood arc and what to avoid ("instrumental only, no vocals, no risers, soft top
  end"). Name the length and where it builds; for cuts use a plan. Past prompts that worked (a 54 s
  documentary underscore, three candidates from one shared opening, ElevenLabs music, `music_length_ms` 54000, model `music_v1`):
  shared: "Instrumental only, no vocals. Underscore for a 54 second documentary film of one real day of ship traffic at the Port
  of Los Angeles, seen from above: dusk, night, dawn, day. Calm, modern and warm, slowly building, never comic, quirky or tense.
  Clean mix, soft top end, no drums until late, no risers, no big hits." Then one of: "Felt piano motif over warm low strings and
  a soft synth pad, around 80 BPM, gentle pulse that grows into a fuller string swell in the last third, resolving softly at the
  end." / "Warm analog synth arpeggio and airy pads, Jon Hopkins and Nils Frahm feel, around 90 BPM, a quiet pulse from the start,
  a soft kick enters halfway, glowing and hopeful, fades out at the end." / "Ambient electric guitar with long reverb, cello and
  pads, around 75 BPM, spacious and nocturnal at first, brighter and wider at dawn, ends on a long held chord.".

## Limits

Costs for stems and video-music are not measured yet; read them from the printed cost the first time. Openverse
ranking is by text, not sound: always index and look at the sheet before choosing.
