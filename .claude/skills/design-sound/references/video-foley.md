# Foley generated from the picture (HunyuanVideo-Foley)

<!-- skill-navigation:start -->
## Reading map

- [Foley generated from the picture (HunyuanVideo-Foley)](#foley-generated-from-the-picture-hunyuanvideo-foley)
- [When](#when)
- [Command (local, the default)](#command-local-the-default)
- [Prompts and shot lists](#prompts-and-shot-lists)
- [Hosted on fal](#hosted-on-fal)
- [Install](#install)
- [Resources](#resources)
- [Limits](#limits)
- [Licence](#licence)
- [Why this model (checked 2026-11-07)](#why-this-model-checked-2026-11-07)
- [ElevenLabs instead (checked 2026-11-07)](#elevenlabs-instead-checked-2026-11-07)
<!-- skill-navigation:end -->

## When

- The default for foley on a silent film whose sounds come from what is on screen (landings, rolling, cloth, water,
  machines), when there is no event list or the contacts are too many to place one by one. A first
  pass for a whole cut in minutes, before hand-placed cues.
- Not for voice, music, memes or a named real sound: use the library, the web or ElevenLabs.
- Not when every event has a timeline time and must land on its frame: `foley.py` from `events.json` is exact; the
  model is looser (Limits). Layer them: the model as the bed of contact sound, `foley.py` for the hero hits.

## Command (local, the default)

```bash
<model root>/repo/.venv/Scripts/python.exe <this skill>/scripts/video_foley.py film.mp4 \
  --prompt "furniture dropped on a wooden floor, soft thuds" --neg "music, speech, noisy, harsh" \
  --out foley.wav --mux film_foley.mp4
```

- `--prompt` names what makes the sound in plain words; `--neg` what to avoid (model default "noisy, harsh").
  `--steps 50` default; `--seed` for another take; `--chunk` piece length (at most 15 s, the model's limit).
- The script lowers its own priority, holds the encoders and the generator across pieces instead of reloading them,
  joins pieces with a 1 s equal-power crossfade, exits hard so nothing keeps VRAM, and writes `<out>.report.json`:
  load and generation time, seconds per video second, peak VRAM, peak RAM, CPU cores used, `silent_share` and
  `heard_nothing` (80% or more of the half-second windows under -80 dB). On `heard_nothing` it prints a warning: that
  film goes to `foley.py` with its event list.
- Then treat `foley.wav` like any stem: `listen.py` for onsets, `mix.py` for loudness and the phone check.

## Prompts and shot lists

The model takes the video and the text together in one pass: SigLIP2 reads the frames (what is in the shot),
Synchformer reads the motion (when contact happens) and CLAP reads the prompt (checked in the installed repo's
`feature_utils.py`, 2026-11-08). The picture already gives the timing; the prompt settles what the picture leaves
open. Always write one.

- Name the material, the object and the action: "wooden paddle stirring thick soap paste in a clay pot", not "stirring".
  CGI surfaces look alike (ash and sand, wet mud and dry earth, wood and plastic), and the prompt is how the model
  tells them apart.
- Add the texture of the sound in two or three words: "soft wet slosh", "dry gravel rattle", "dull wooden thud".
- Say what is off screen but heard, when it matters: "steady light rain on the road".
- Keep music, voice and named meme sounds out of the prompt; put "music, speech" in `--neg`, plus anything the model
  keeps adding (a whine, crowd noise, wind).
- English, one short sentence; a list of ten nouns blurs the result.

One call takes one prompt, so a film whose shots change material needs one prompt per shot. Give a shot list
(`--shots shots.json`, format in `scripts/foley_shots.py`): each shot has `start`, an optional `end` and `neg`, and its
`prompt`. Shots longer than `--chunk` still split into pieces with the `--overlap` crossfade; at a cut between shots the
pieces overlap by only `--cut-fade` (0.08 s), so one shot's sound does not bleed across the cut. A stretch with no
shot gets silence. Take shot times from the film's own timeline or cut list, not by eye.

```json
[
  {"start": 0.0, "prompt": "rubber boots squelching in deep wet mud, soft sucking steps"},
  {"start": 6.4, "prompt": "gravel tipped from a wheelbarrow onto mud, stones rattling"},
  {"start": 14.0, "prompt": "steel shovel scraping gravel, steady light rain on a dirt road", "neg": "music, speech, wind"}
]
```

- A/B a new prompt on one shot before running the whole film (`--seed` for a second take of the same prompt).

## Hosted on fal

The same model runs on fal as `fal-ai/hunyuan-video-foley` (commercial use allowed on fal's page, $0.10 per 10 s of
video, read 2026-11-08). Use it only when the card cannot free 9 GB for a long while: in the one timed run the
queue made it slower than a warm local run.

```bash
uv run --no-project --python 3.12 --with fal-client --with numpy --with soundfile python \
  <this skill>/scripts/fal_foley.py film.mp4 --prompt "..." --neg "music, speech, noisy, harsh" \
  --out foley.wav --mux film_foley.mp4
```

- Key: `FAL_KEY`, else `~/.config/fal/api_key.txt`, else a `FAL_KEY=` line in `~/.config/fal/.env`; never printed.
  With none it exits and says where to create one (fal.ai/dashboard/keys).
- Same flags as the local script, same 12 s pieces with a 1 s crossfade; it prints the price estimate before
  uploading and writes `<out>.report.json` (wall time, estimate, `silent_share`, `heard_nothing`).
- Same 12 s clip as Limits (2026-11-08): 282 s wall time including fal's queue (local warm: about 1 min), estimate $0.12; onset error median
  35 ms, 48% within one frame, 98% within 100 ms (local: 54 ms, 39%, 73%), but 40 onsets with no event (local: 7)
  and a soft tail at -48 dB after the motion stops where the local run was silent. Level and gate it in `mix.py`.

## Install

Model root: `~/models/hunyuanvideo-foley` (`HUNYUAN_FOLEY_ROOT` moves it; a junction to a big drive is fine).

1. `git clone --depth 1 https://github.com/Tencent-Hunyuan/HunyuanVideo-Foley.git <root>/repo`
2. `uv venv --python 3.11 <root>/repo/.venv`, then `uv pip install` torch, torchvision and torchaudio from the CUDA
   index (cu126 worked), then `numpy==1.26.4 scipy diffusers timm accelerate "transformers>=4.50,<4.57" sentencepiece
   descript-audiotools pillow av einops pyyaml omegaconf easydict loguru tqdm setuptools pandas pyarrow soundfile
   psutil` (mainline transformers instead of the pinned git tag; no gradio).
3. Weights from `tencent/HunyuanVideo-Foley` into `<root>/weights`: `hunyuanvideo_foley_xl.pth`,
   `synchformer_state_dict.pth`, `vae_128d_48k.pth`, `config_xl.yaml`, `LICENSE`, `NOTICE`. `google/siglip2-base-patch16-512`
   and `laion/larger_clap_general` go to the Hugging Face cache, which the script points at `<root>/../hf-hub`.
4. Check: the repo's example "A person walks on frozen ice" should land near Tencent's own result (here -28 dB mean
   against their -24.7 dB).

## Resources

Measured 2026-11-07 on an RTX 3060 12 GB, i7-14700KF, 64 GB RAM, model on an HDD, other jobs on the card and CPU:

| What | Measured |
| --- | --- |
| Disk | weights 7.8 GB, encoders 2.2 GB, venv 4.7 GB (about 15 GB in all) |
| VRAM | torch reserved 9.1 GB at peak (XL, offload on); give it 9 GB free and run nothing else heavy beside it |
| RAM | 7.8 GB peak for the process |
| CPU | about 1 core on average while generating, up to 17 cores while loading |
| Time, warm | 5.2-5.3 s per video second (12 s clip in about 1 min, 26 s film in 2.3 min) plus about 18 s of loading |
| Time, cold or busy | 7.5 min for 8 s (first run, HDD and CPU at 100%); 23 s per video second with 65% CPU load elsewhere |

## Limits

| Clip | Result |
| --- | --- |
| Items raining onto a pile, then a box tower toppling, 12 s | onset error against the 44 physics impacts: median 54 ms, 39% within one frame, 73% within 100 ms; silent once motion stops |
| Furniture showroom, 26 s, small fast drops in a wide clean CGI shot | near silence (-89 dB) through 18 drops; sound only at two later moments |
| Elevated metro train pass, 10 s, slow build then a close pass (2026-11-08) | heard it: rise from 4 s, peak at the close pass; stayed loud after the train left, and a steady whine at about 14.8 kHz from 7.5 s |

- It hears clear contact (things landing on a pile, a tower falling, footsteps), not small fast objects in a wide
  clean CGI shot. Dense events also flatter the median onset, so keep hero hits frame-placed with `foley.py`.
- It does not always fade when the subject leaves frame, and it can add a steady high whine. Check the final sheet: low-pass the stem at about 11 kHz and fade it from the exit frame (metro pass: `lowpass=f=11000` twice, then a volume ramp to -12 dB over 1.2 s).
- Raw output sits near -27 dB RMS: level it in `mix.py`. Pieces join with a 1 s crossfade, which can smear a hit on
  the seam. Output is 48 kHz stereo.

## Licence

Tencent Hunyuan Community Licence: commercial use is allowed inside the Territory (the world minus the EU, UK and South
Korea) for products under 100M monthly users. Outputs may not be used to improve other AI models, nor used or
displayed outside the Territory (clause 5(c)), so a public post seen in the EU is a grey zone: warn once, like any
licence warning, and raise it before delivering to an EU or UK client. Keep `LICENSE` and `NOTICE` with the weights.

## Why this model (checked 2026-11-07)

MMAudio (about 6 GB, fast), ControlFoley (Xiaomi), Woosh (Sony) and ThinkSound all ship weights under non-commercial
terms, so for paid work only HunyuanVideo-Foley is clean. XL with offload is stated at 8 GB; XXL needs 12 GB offloaded
and would fill a 12 GB card.

## ElevenLabs instead (checked 2026-11-07)

ElevenLabs has no foley endpoint (OpenAPI read 2026-11-07: `/v1/sound-generation` from text and
`/v1/music/video-to-music`). The video route is `generate_elevenlabs.py video-music <mp4> --sfx --separate`: a music
file and an SFX stem heard from the picture. On the same 12 s clip: onset median 49 ms, 34% within one frame, 77%
within 100 ms, but it went silent for 4.5 s while items kept landing, added 33 onsets with no event (local: 7) and kept
sounding after motion stopped. The credit counter showed 0 at once, then 1,619 fewer within the hour (about 135
credits per second of video). In an A/B on that clip the owner preferred the local model clearly, so
ElevenLabs video SFX is a fallback only when no GPU is free.
