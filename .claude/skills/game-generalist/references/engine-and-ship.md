# Engine and ship (`engine-and-ship.md`)

The engine is a slot in `brief.md`. This file holds only what a game needs on top of the `use-3d-software` skill: how each engine exposes what the gates read, how to capture real play, where the build lands and how to hand it over. For every engine step (import, controllers, export settings, axes, scale) follow the use-3d-software skill and do not copy it here.

<!-- skill-navigation:start -->
## Reading Map

- [Engine and ship (`engine-and-ship.md`)](#engine-and-ship-engine-and-shipmd)
- [Pick the engine](#pick-the-engine)
- [Per engine](#per-engine)
- [Capture real play](#capture-real-play)
- [Jam checklist](#jam-checklist)
- [Ship](#ship)
<!-- skill-navigation:end -->

## Pick the engine

| Brief says | Engine |
|---|---|
| Others should play it in a browser, or share a link | web: three.js, Phaser or plain canvas |
| Light 2D or 3D game, native build | Godot or Unity: ask the user once, record the answer in `brief.md` |
| Photoreal look, or the jam requires it | Unreal |

- Web is the default when the brief gives no target.
- Films, stills and renders are not this skill.
- Ask the engine question once. When the answer is recorded, do not ask again.

## Per engine

| | Web | Godot | Unity | Unreal |
|---|---|---|---|---|
| State for the gates | `window.__game` hook (`references/playtest-gates.md`) | an autoload node prints `GATE state status=.. progress=.. hash=..` on change | a static class logs the same line with `Debug.Log` | a game-instance or subsystem logs the same line with `UE_LOG` |
| Seeded randomness | one seeded generator, `seed(n)` reseeds it | `seed()` with the number and one `RandomNumberGenerator` | one `System.Random` or `UnityEngine.Random.InitState` | one `FRandomStream`, seed from a launch argument |
| Fixed step | own loop with a fixed delta | physics tick plus `--fixed-fps 60` | `Time.fixedDeltaTime`, `Application.targetFrameRate` | fixed tick or `t.MaxFPS`, avoid frame-rate-bound logic |
| Scripted run | Playwright through `scripts/probe.mjs` | `--headless --quit-after N` with a bot script and a replay file path as a user argument after `--` | `-batchmode` with an `-executeMethod` entry that plays a replay | `-game -ExecCmds` with console commands, or a bot actor |
| Replay input | the replay JSON fed by the probe | the same JSON read by an input injector that calls `Input.parse_input_event` | the same JSON read by a test input source | the same JSON read by a bot controller that injects input |
| Build output | `{{WORK_DIR}}/build/` (static files) | `{{WORK_DIR}}/build/<platform>/` from the export preset | `{{WORK_DIR}}/build/<platform>/` | `{{WORK_DIR}}/build/` from packaging |

- The replay format stays the one in `references/playtest-gates.md` for every engine, so one set of replays serves all.
- Exact flags and editor steps vary by version. Check the version's help output and the use-3d-software skill before relying on a flag, and record what actually ran.
- A bot that plays by reading the state is deterministic. A bot that plays by screenshots is exploratory only.
- Keep gameplay rules in code or data files, not scattered over scenes, so the state line and the replay can reach them.

## Capture real play

- Record 30 to 60 s of real play of the build, with sound, as `capture.mp4`. Record real gameplay before writing any caption, post or devlog about the game.
- Web: `node {{SKILL_DIR}}/scripts/record.mjs <url> --seconds 45 --bot <bot.mjs> --size 960x540 --autostart --out capture.mp4`
  records the page with the game's own sound (tapped from its audio graph, never the speakers), aligns them on a
  flash-and-beep marker and prints the offset. A WIP clip uses the same script at 640x360. Check the track with
  `ffmpeg -af volumedetect` before sending.
- Godot: `--write-movie` with `--fixed-fps 60` gives a steady file; mux the audio afterward. Unity: the Recorder package or a screen capture. Unreal: a screen capture of the packaged build, or a Movie Render Queue pass for a cleaner clip.
- Show the loop, one win or loss and the restart. Do not cut together moments the game cannot produce.
- Send a small, low-quality capture first. Make the full-quality one only after the user signs off.
- More than 5 frames to check go to a subagent that returns text.

## Jam checklist

Run it at step 1 for a jam brief.

1. Read the jam rules in full: theme, dates, allowed assets and tools, AI-use rules, team size, submission format, what may be public and when.
2. Put the deadline with its time zone in `brief.md`. Work back from it: a feature freeze, a content freeze and a last-hour buffer for the build and the upload.
3. Scope to the time box: one mechanic, one screen or one short level set, a cut list written down.
4. Check the theme in the one-sentence promise.
5. Daily work-in-progress note: what runs, a clip, what is next. Keep it in `brief.md` under `## Progress`. Post it publicly only if the rules and the user allow.
6. Keep an unbroken build every day. The last working build is the submission if all else fails.
7. Submission files: the playable build (platform archive or web build), a cover image, three screenshots, a short description with controls, the capture, `CREDITS.md`.
8. Test the downloaded submission on a clean folder or machine before the deadline.
9. Credits: every asset, font, sound and tool listed with its licence. Follow the jam's rule on pre-made assets.

Submit only when the user says so.

## Ship

- The preview is a local file or a localhost link, plus `capture.mp4`. Never deploy, upload or publish unless the user asks.
- When the user asks for a static deploy of a web build, ship only the `build/` folder. Check that the live build matches the local one.
- `CREDITS.md` lists every asset with source, author and licence. A `credits.json` copy feeds an in-game credits screen: `[{ "asset": "", "author": "", "licence": "", "url": "" }]`.
- A licence that needs a trade-off is named in one line and asked once.
- The README holds: what the game is, the controls, how to run it, the credits link.
