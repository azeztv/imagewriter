# Mix (mix.py)

<!-- skill-navigation:start -->
## Reading map

- [Mix (mix.py)](#mix-mixpy)
- [mix.json](#mixjson)
- [What it does](#what-it-does)
- [Whole-mix checks](#whole-mix-checks)
- [Listening per stem](#listening-per-stem)
- [Mixing practice](#mixing-practice)
- [Evidence](#evidence)
- [Limits](#limits)
<!-- skill-navigation:end -->

`PY mix.py mix.json --out final.wav [--sheet final-sheet.png] [--no-listen]` with the pass-1 run line (plus matplotlib for
the sheet). File paths in `mix.json` are relative to its folder.

## mix.json

```json
{"stems": [{"name": "foley", "file": "foley.wav", "role": "cue"},
           {"name": "music", "file": "music.wav", "role": "duck", "gain_db": -9, "duck_db": -8}],
 "target_lufs": -14, "true_peak_db": -1.5, "expect_from_events": "events.json"}
```

Stem fields: `role` (`cue`, `voice`, `duck`, `bed`), `gain_db`, `offset_s`, `duck_db`, `highpass`, `lowpass`,
`carve_db` (duck stems, default -3; 0 turns it off), `phone_bass` (true on a stem whose impacts live under 150 Hz),
`deess` (voice stems, default on), `unmask_db` (voice stems; default from `house-defaults.json`, 0 turns it off).
Top-level `auto_level` and `codec_check` (both default true), `hold_ms` and `unmask_db` (one mix only).
`expect` lists extra checks `{stem, label, t}`; `expect_from_events` adds every foley event (label = its `label`, else
"material what on other").

## What it does

1. Applies each stem's filters and gain. A `bed` (rain, wind, room tone) is band-limited to 200 Hz - 5 kHz unless set,
   so it stays out of the cues' band.
2. Side-chain: `cue` and `voice` stems drive a detector (10 ms level, no ducking under -50 dB, full ducking 20 dB
   higher, release 250 ms, dip starts 30 ms before the sound). `duck` stems (music) dip by `duck_db` (default -8) and
   `bed` stems by -6 under them. Cue and voice are never ducked.
3. Carve: each `duck` stem's 1-4 kHz band dips a further `carve_db` (default -3 dB) while the voice plays (the cues
   when there is no voice), with the same detector; zero-phase filters, so the rest of the music is untouched.
4. Unmask: each `voice` stem yields to the summed cue stems only in the frequency bins and moments where a cue sits
   within 6 dB of the voice or above it (21 ms STFT, 5 ms hop, ~235 Hz smoothing, 10 ms look-ahead, 120 ms release),
   by at most `unmask_db`. The effect reads clearer without being turned up and the voice keeps its level (the
   TrackSpacer / Neutron Unmask idea). Test mix 2026-11-07: cues over the voice +5.3 dB(A) off, +6.6 at -3, +7.9
   at -6; cue over music and voice over music unchanged. The report prints each cue's margin over the voice.
5. `phone_bass`: harmonics of the stem's content under 150 Hz (soft clipping, band-passed 150-600 Hz, -6 dB) are added,
   so a thump still reads on a phone speaker that plays nothing under about 200 Hz.
6. Sums, puts everything under 100 Hz in the centre (mono bass), brings the integrated loudness to `target_lufs`
   (default -14) and limits the true peak to `true_peak_db` (default -1.5 dBTP) with a 5 ms look-ahead limiter on
   the 4x oversampled signal; the loss is made up again.
7. Prints per-stem loudness, final integrated LUFS, true peak and sample peak, then the whole-mix checks. `--sheet`
   draws the final's waveform and mel spectrogram with every expected cue marked: each event should show a vertical
   front at its line.

## Whole-mix checks

Each prints `FLAG` and counts toward the "things to check" total:

- Short-term (3 s) maximum more than 5 LU over integrated: one moment will jump out (EBU R128 s1 short-form limit).
- Voice under 10 LU over music plus beds during the half seconds the voice speaks: lower the music or duck deeper.
  Measured, never assumed: the -8 dB dip only meets it when the music already sits a few LU under the voice.
- Mono fold-down more than 3 dB quieter than stereo: wide or out-of-phase content that a phone or a mono speaker loses.
- Per cue, `WEAK ON PHONE` when under 30% of its energy in the first 0.4 s sits above 200 Hz: add `phone_bass` or a
  layer with a mid-band click.

## Listening per stem

pass-1 found that CLAP cannot hear a single cue inside a dense music mix. So the label and level checks run on each STEM
alone (the foley stem for the events, with `listen.py`'s vocabulary rank), and only sync and masking are read from the
final mix: onset offset against the expected time and the margin over the surrounding bed. Masking is not checked on a
stem alone (no bed in it). In the final, the "bed" is the 20th percentile around the cue, so next to a silent gap the
margin reads absurdly high; trust it only for cues inside continuous music. It is never a margin over the music
itself: a cue can show +59 dB over the bed while sitting 15 dB under the score (an intro film, 2026-10-29). Measure
the cue's RMS in the effects stem against the music stem after its gain and ducking at the same second: `mix.py`
does it per cue, A-weighted (loudest cue frame against the music's median over 0.4 s), and flags `QUIET UNDER MUSIC`
under +6 dB(A). Band-by-band margins were tried and failed: both unheard cues read +14 to +54 dB in the band that
carried them, because a dark score leaves single bands nearly empty while the whole still covers the cue.

## Mixing practice

The order a re-recording mixer works in, with the numbers this script uses:

1. Voice first. Set it, then everything else is placed against it. Dialogue EQ is subtractive (high-pass about 80 Hz,
   cut mud, no boost); noise reduction no more than 3 to 5 dB.
2. Music under voice: about 10 LU or more below the voice while it speaks (12 LU for a general audience); carve 1-4 kHz
   a few dB when the voice is on rather than ducking the whole track further.
3. Effects per cue: each event its own sound (foley.md), 2 to 3 layers at most, bused. A long loud effect (engine,
   crowd, rain) fades up to make its point and is ducked back under speech.
4. Beds and ambience: 15 LU under the voice, sparse and peaky rather than a flat wall of noise.
5. Master: -14 LUFS integrated, -1.5 dBTP, short-term within +5 LU, bass under 100 Hz mono. Do not compress the master
   harder for loudness: micro-dynamics correlated with listener preference, and YouTube's Stable volume evens playback.
6. Check on a phone speaker's terms: anything that only lives under 200 Hz is gone there.

## Evidence

Read 2026-11-04 (V = at the owning source, R = reported by a secondary source or an abstract):

- [V] EBU R128 s1 (2020), short-form up to about 2 min: -23 LUFS broadcast, short-term max target + 5 LU, -1 dBTP,
  no LRA limit. https://tech.ebu.ch/docs/r/r128s1.pdf. EBU R128 s2 (2023): smartphones may get -20 to -16 LUFS.
- [V] Spotify: -14 LUFS, true peak under -1 dBTP, or -2 dBTP for masters louder than -14, for lossy transcodes.
  https://support.spotify.com/us/artists/article/loudness-normalization/
- [V] YouTube Stable volume narrows loud and quiet parts on playback (off for official music).
  https://support.google.com/youtube/answer/16619284. [R] YouTube's reference level is -14 LUFS; TikTok, Reels and X
  publish none (vendors say about -14 and -1 dBTP).
- [R] Torcoli et al., JAES 67(12) 2019, background ducking: at least 10 LU commentary over music, 15 LU over ambience;
  non-experts prefer about 4 LU more. Geary, Torcoli et al., JAES 68(11) 2020: voice over voice at least 20 LU.
- [V] De Man et al., AES 138 (2015), 98 mixes: preference rose with micro-dynamics (+0.26) and fell with 4 kHz octave
  energy (-0.21) and side-to-mid ratio (-0.32). https://joshreiss.github.io/documents/2015/DeMan%20Reiss%20-%20AES138.pdf
- [R] Re-recording mixer and editor tutorials (YouTube `Sh6kPfNDy5o`, `sbCd91VG22w`): dialogue first, subtractive EQ,
  music 10 to 20 dB under dialogue, effects set per cue, fade long effects up then duck them.
- [R] Phone speakers roll off between about 100 and 250 Hz; harmonics let the ear infer the missing fundamental.
Settled 2026-11-04 (second pass):

- Ducking: 10 ms detector, 30 ms early, 150 ms hold, 300 ms release, -8 dB start. [R] Resolve ducker guidance:
  recovery 300-600 ms (150-300 for fast short-form), rise 50-300 ms; Fairlight compressor default release 93 ms,
  hold 0-4000; [R] Premiere Auto Ducking defaults -8 dB, 500 ms fades; creator guides 6-12 dB, release 250-700 ms.
  The hold is a choice (no source has a number). Depth is not fixed: `auto_level` lowers music and beds until the
  voice is 11 LU over them, because the 10 LU rule is the goal and the dip only a means.
- Lossy headroom, measured: four clips mastered at -14 LUFS, ceilings -1, -1.5 and -2 dBTP, through ffmpeg AAC 128k
  and 96k, Opus 128k and 64k, MP3 128k. Decoded true peak rose 0.5 to 3.2 dB over the master's (worst: Kevin MacLeod
  "Latin Industries" through AAC 128k, -3.19 to -0.02 dBTP), so no fixed ceiling is safe for every clip. `mix.py`
  encodes the master to AAC 128k and Opus 64k, decodes, and lowers the ceiling until both stay under -0.3 dBTP
  (`codec_check`, default on), flagging a loudness miss over 0.5 LU if that costs loudness.
- Platform files, measured on downloads 2026-11-04: TikTok (MrBeast, 6) median -15.6 LUFS, range -23.4 to -11.7;
  YouTube Shorts (MrBeast, 6) median -13.3, range -16.5 to -9.1, true peak up to +1.0 dBTP; X (4 viral videos) median
  -17.8, range -22.2 to -15.1. No platform levels files on upload, so -14 stays: on target for YouTube, in the louder
  half of TikTok and X feeds. Instagram was not measured (needs a sign-in).
- De-essing, measured: per voiced STFT frame, energy at 5-10 kHz over 125-4000 Hz. Four approved
  narrations (four documentary Shorts): p99.9 +23.1 to +24.6 dB, max +24.2 to +25.4 dB. A cloned
  horror voice reached max +30.8. Rule: no harsher than anything the owner approved; frames over +25 dB get the 5-10 kHz band
  lowered by the excess, at most 4 dB ([R] tutorials 2-4 dB usual, 3-6 upper; [V] FabFilter: split band for mixes,
  s-sounds about 8-10 kHz; [V] Apple: sibilance 5-8 kHz female, 3-6 kHz male). On the cloned voice it cut 280 ms of
  60 s, max 30.8 to 27.5 dB. `deess: false` on a voice stem turns it off.
- Voice chain: high-pass 80 Hz on voice stems ([R] tutorial consensus 80-100 Hz, above 120 Hz thins). No compressor
  and no presence boost by default: ElevenLabs voices arrive level, and the owner prefers a soft top.
- SFX against music: no source has numbers for trailers, explainers or games ([R] NHK: preferred dialogue over
  background 0-13 LU, mean 7). The house rule stays ours, calibrated on cues the owner did not hear: every cue +6 dB(A) over
  the ducked music. [R] Trailers get impact from contrast (a dip or silence before the hit), not raw level.
- Panning: voice centre; effects follow the picture up to 75% (`foley.py` clamps `x`), an impact's body and tail at
  half its pan so the weight stays central, bass under 100 Hz mono. [R] sound designers: off-screen effects 50-75%,
  extremes only for dramatic moments, impacts and low end centred, mono check on every export.
- Ears only, the owner's call: the duck hold, the cue margin over the music and the voice unmask depth live in `house-defaults.json` (with their
  history) and change only through `ab_test.py`: two blind renders, the house value and one step away (hold +400 ms,
  cue +6 dB(A) with the cue gain set from a first render, unmask -4 dB), the step doubled until the two differ by at
  least 20 dB under the mix. Three-way sets 2026-11-07 that differed by 25-40 dB under the mix sounded the same to
  the owner; the unmask set at 18 dB did not. A mix that cannot show the value (hold on a voice with no gaps stayed 40 dB
  under at any hold) sends nothing. The owner picks A, B or `same` (value kept, noted),
  `pick` records the value and the owner's words. `mix.json` may set `hold_ms` for one mix; that is how the variants render.

## Limits

No dialogue-gated loudness and no LRA target (EBU calls LRA not useful under 2 minutes). The listen ranks come from a ~150-label
vocabulary: add labels in `scripts/vocabulary.txt` for new kinds of sound.
