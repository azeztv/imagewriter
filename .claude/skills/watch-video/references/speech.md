# Speech and tone of voice

Get a transcript with word times, then measure the voice. Both write into `$S`.

<!-- skill-navigation:start -->
## Reading map

- [Speech and tone of voice](#speech-and-tone-of-voice)
- [Transcript](#transcript)
- [Check the words: two transcripts](#check-the-words-two-transcripts)
- [Who speaks when](#who-speaks-when)
- [Subtitles and translation](#subtitles-and-translation)
- [Tone of voice](#tone-of-voice)
<!-- skill-navigation:end -->

## Transcript

A link with captions:

```
yt-dlp --js-runtimes node --encoding utf-8 --skip-download --write-auto-subs --write-subs --sub-langs "en.*" --sub-format vtt -o "$S/%(id)s.%(ext)s" "<url>"
uv run --no-project python {{SKILL_DIR}}/scripts/captions.py "$S/<id>.en.vtt" --out "$S"
```

Use the video's language in `--sub-langs` (`"vi.*"` for Vietnamese). HTTP 429 or "page needs to be reloaded" after a few
calls: do not keep retrying, transcribe locally. YouTube auto captions carry real per-word start times and `[Music]`-style
sound tags, and `captions.py` keeps both (tags stay out of `words.json`); uploaded captions only time each line, so
there the word times are spread evenly and rate and pause are rougher.
Captions come first whenever they exist, auto ones included: on a VTV news clip (2026-11-07) YouTube's Vietnamese
auto captions matched Qwen3-ASR word for word, with punctuation and digits, in one second instead of four minutes.

Local transcription is for files with no captions: NVIDIA Parakeet TDT on CPU, never Whisper. It reads
the video directly:

```
uv run --no-project --python 3.12 --with "onnx-asr[cpu,hub]" --with psutil python -I {{SKILL_DIR}}/scripts/transcribe.py "<video or audio>" --out "$S" [--from <s> --to <s>]
```

- It writes `transcript.txt` as `[mm:ss] sentence` and `words.json` with word times, at below-normal priority on 6
  threads, no GPU. A 318 s clip took about 70 s with the model load. A window gets its own names (`transcript_30-60.txt`).
- The default model is English-only; `--language German` (any of 25 European languages) switches to Parakeet v3.
- Other languages go to Qwen3-ASR-0.6B (`transcribe_qwen.py`, 30 languages: Vietnamese, Chinese, Cantonese, Japanese,
  Korean, Thai, Indonesian, Malay, Filipino, Hindi, Arabic, Persian, Turkish and more): pass `--language Vietnamese`,
  or let it happen on its own when most Parakeet lines come out unreliable. Measured 2026-11-07 on CPU, 6 threads, on
  FLEURS dev: Vietnamese WER 5.9% (20 clips, 0.76x real time), Japanese CER 10.4% (20 clips, 1.34x real time);
  language detected right 40 of 40. An hour of speech takes about an hour, so run it in the background.
- Qwen word times: real ones from its aligner for zh, en, yue, fr, de, it, ja, ko, pt, ru, es; elsewhere spread over
  each segment of at most 20 s, as rough as captions. It often spells numbers out and drops punctuation, and misses
  foreign names: read numbers and names from the picture before quoting. Models: `~/.cache/asr-models` (junctions to `D:/models/asr` here; `QWEN_ASR_MODELS` overrides).
  GPU: add `--device cuda:0` and swap in CUDA torch with `--with "torch==2.15.0+cu132" --index https://download.pytorch.org/whl/cu132
  --index-strategy unsafe-best-match` (plain `--with torch` resolves to the CPU build); run it through the machine's GPU
  queue if it has one. 120 s of news took 102 s on an RTX 3060 busy with a render and 110 s on an idle one, so startup and
  model load dominate a short clip; 285 s on CPU, same words (2026-11-07). Use the GPU for long files. A language outside both models
  (Khmer, Swahili...) has no local transcript: say so, use captions, and ask the user before installing another model.
- An `UNRELIABLE` line or `[unreliable]` mark means low model confidence, usually a language the model does not know.
  The words on that line can be fluent nonsense. It was measured only on synthetic voices, so a clean run is not proof.
- `--context "<title. description>"` (Qwen only) feeds the video's own words to the model. Get them with
  `yt-dlp --skip-download --print-to-file "%(title)s. %(description)s" "$S/context.txt" "<url>"`; plain `--print`
  breaks diacritics on Windows. On a Vietnamese news clip it fixed words the title holds ("express delivery", a
  tone-mark slip) and got a name closer, but agreement with the captions stayed 88-89% and it spelled more numbers out.
  Use it when names matter; it does not replace the check below.

## Check the words: two transcripts

Where a quote, name or number matters, make a second transcript of the same span (captions and Qwen, or Qwen with and
without context) and list where they disagree:

```
uv run --no-project python {{SKILL_DIR}}/scripts/compare_transcripts.py "$S/a/words.json" "$S/b/words.json" --names captions qwen --out "$S/disagreements.txt"
```

Each disagreement prints with its time; `number` spans are usually one source writing digits and the other words. On
a Vietnamese news clip (2 min, 423 words, 89% agreed) the 19 word disagreements held every real mishearing: sometimes
the captions were right, sometimes Qwen, sometimes both wrong (one common word misheard two different ways; a walker's
name heard as "Carski" and "Carl vutsky", really Karl Bushby). Settle each one from the audio at that second, the picture or a primary
source. Agreement lowers the risk; it does not prove the words.

## Who speaks when

```
uv run --no-project --with sherpa-onnx --with numpy python {{SKILL_DIR}}/scripts/diarize.py "<video or audio>" --out "$S" --sweep [--words "$S/words.json"]
```

Offline, any language, about 7 s for a minute of audio on CPU (three times that with `--sweep`); models (30 MB, no
sign-in) download on first use. `--words` writes `transcript_speakers.txt` with `S1:`, `S2:` lines. Two FLEURS tests
(2026-11-07, share of speech labelled right):

| threshold | 2 men + 1 woman, 2 languages | 3 men, same Vietnamese sentence |
| --- | --- | --- |
| 0.5 | 6 speakers, 66% | 3, 100% |
| 0.6 (default) | 4, 86% | 3, 100% |
| 0.7 | 3, 96% | 2, 64% |

No single threshold is right for both, and `--speakers 3` also merged the similar voices into 2. So use `--sweep`: it
prints the count at 0.5, 0.6 and 0.7 and says "NOT settled" when they differ, as both tests did. When it is not settled,
or a speaker change matters, check it against the picture (who is on screen, lips, name captions) before you rely on it.
Labels are not names. Phone audio, crosstalk and music beds were not tested.

## Subtitles and translation

Claude does not hear audio: translation works on the transcript, so its quality is the transcript's. Build numbered
cues from `words.json`, translate only the text lines of a copy, then check nothing else moved:

```
uv run --no-project python {{SKILL_DIR}}/scripts/make_srt.py build "$S/words.json" --out "$S/subs.vi.srt"
uv run --no-project python {{SKILL_DIR}}/scripts/make_srt.py check "$S/subs.vi.srt" "$S/subs.en.srt"
```

Cues end at a sentence end, a 0.6 s pause, 42 characters or 6 seconds. Translate sentence by sentence across cue
breaks so each cue stays readable, keep names the transcript check settled, and fix known mishearings while translating.
`check` fails on a changed cue count, number or time, or an empty cue, and lists cues left identical to the original.

## Tone of voice

```
uv run --no-project --with numpy python {{SKILL_DIR}}/scripts/voice.py "<video or audio>" --words "$S/words.json" --out "$S"
```

`voice.txt` gives each sentence's pitch, pitch range, loudness and rate against the speaker's own median, the pause
before it and whether it ends rising, falling or level. `*` marks a sentence far outside this file's own spread and names
what is far. Rate is blank under 4 words. Read it beside the transcript and the frame at that second.

It is evidence, not an emotion label. A high, fast, loud sentence can be joy, anger or fear; the words and the picture
decide, and the result stays marked as a reading. A flat pitch range or long pauses are worth noticing only against
how this speaker usually talks.

Where it misleads:

- Several speakers share one baseline, so a pitch jump can be a change of speaker. Use the picture and the words.
- Music under the voice makes pitch unreliable. A sentence with `pitch unknown` has no usable voiced frames.
- In a tonal language such as Vietnamese, each word's tone moves the pitch. Compare level and range across sentences;
  do not read a rising ending as a question.
