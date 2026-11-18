# Web game audio (`web-game-audio.md`)

Step 7 for a browser game: the `design-sound` skill picks and checks the sounds; this file is how they live in the
page. Every number is a default to tune by ear and by the analyser.

## Graph

One `AudioContext`, built on the first user input (browsers block audio before it):

```
cue gains ──┐
music gain ─┴─> master (mute) ─> limiter ─> analyser ─> destination
```

- Limiter: a `DynamicsCompressor` at threshold -6 dB, knee 0, ratio 20, attack 3 ms, release 120 ms. Peak after it
  stays under 1.0.
- Mute: master gain 0 or 1; `M` toggles it, `?mute=1` starts muted, and the HUD says "Sound off". The game plays the
  same muted and with no audio files at all.
- Tests: `?silent=1` leaves `destination` out of the graph so a test reads only the analyser and nothing reaches the
  speakers.
- `file://` builds cannot fetch audio files: encode the clips as base64 in a generated `audio-data.js` (a build script
  that reads the credited source files), decode them once with `decodeAudioData`.

## Cues

- One cue per verb and outcome: start, the main action (and its charge, if it charges), success, failure, pause and
  resume, win, lose, restart. A cue for movement is quiet or a written "silent on purpose" line in `brief.md`.
- A charging action raises pitch with progress (`playbackRate` from about 0.8 to 1.9) so the ear hears the fill.
- Rotate two or three takes or detune by a few percent so repeated cues do not machine-gun.
- Music bed: a loop under the cues, ducked on pause and end screens. Measure it: between cues it sits about 12 to 18 dB
  under the cues; a bed 25 dB or more under is inaudible on a laptop.
- Real CC0 sounds first. Game and UI one-shots are usually faster from the web fetch in `design-sound` (Openverse) than
  from the indexed library, which holds mostly banks and music; batch library queries in one process, since each
  `search.py` call loads its model.

## Checks

- A muted analyser test plays the game through real input (a closed-loop bot), counts which cues fired per event, and
  reads the peak after the limiter. A test that edits the state to trigger cues proves the wiring only; say which.
- The capture carries the game's own sound: `scripts/record.mjs` taps the page's audio graph, never the speakers.
  Check the track with `ffmpeg -af volumedetect` and its loudness before sending.
