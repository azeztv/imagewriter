# Unreal jam build, headless (`unreal-jam-build.md`)

What a C++ Unreal game built by an agent without opening the editor needs on top of the `use-3d-software` skill.
Measured on UE 5.9 (Launcher build) in November 2026; check the installed version before relying on a flag.

<!-- skill-navigation:start -->
## Reading Map

- [Unreal jam build, headless (`unreal-jam-build.md`)](#unreal-jam-build-headless-unreal-jam-buildmd)
- [Project shape](#project-shape)
- [Loop: build, set up, run](#loop-build-set-up-run)
- [Point-cloud and other instanced visuals](#point-cloud-and-other-instanced-visuals)
- [Scripted capture with game audio](#scripted-capture-with-game-audio)
- [Web target](#web-target)
- [What was slow or broke](#what-was-slow-or-broke)
<!-- skill-navigation:end -->

## Project shape

- A C++ project from the start: the web target needs one, and all rules live in two files an agent can read whole.
  No Blueprints, no input assets: read keys in `Tick` with `IsInputKeyDown`, draw the HUD with `AHUD::DrawHUD`.
- One tuning namespace at the top of the game file holds every number a playtest will change.
- Assets are made by a Python script the headless editor runs (`-run=PythonScript -nullrhi`): import GLBs, build
  materials node by node, import sounds, build the level. Safe to run twice.
- Keep the source outside the project folder when the project lives on another drive: a junction keeps one copy.

## Loop: build, set up, run

1. Compile: `Engine/Build/BatchFiles/Build.bat <Project>Editor Win64 Development -project=<uproject> -waitmutex`.
2. Set up assets: the editor in commandlet mode with the setup script.
3. Run: `UnrealEditor-Cmd.exe <uproject> <map> -game -RenderOffScreen -ResX= -ResY= -windowed` plus the game's own
   launch arguments for the scripted run.

Each step logs to a file; the wrapper prints only lines that matter (`Result:`, errors, the game's own log category).

## Point-cloud and other instanced visuals

- Instanced static meshes with per-instance custom data (colour, birth time) and an unlit material. The material
  does fades and flashes from the birth time, so nothing is updated per frame on the CPU.
- One instanced component per batch (one per scan), reused round-robin, so clearing old points is one call.
- Constant on-screen size: scale each instance around its own pivot in World Position Offset by its distance to the
  camera. Without it, far points vanish and near points become blobs.
- The collision world can stay invisible: line traces against complex collision supply the points.
- The dedicated point-cloud plugin is desktop only; this path uses plain mobile-renderer features.

## Scripted capture with game audio

- A text file drives the run: timed camera keys and timed actions. The pawn is carried along a traced path instead
  of walking with physics, so the run is the same every time. A person walking with physics is a separate test.
- Fixed time step (`FApp::SetUseFixedTimeStep`), one screenshot request per tick, and the non-realtime audio mixer
  stepped by hand each tick: start with `-deterministicaudio` and `-execcmds="au.nrt.RenderEveryTick 0"`, or the
  engine renders extra audio and the track comes out several times too long.
- Log every game event with its time to a CSV, and check sound onsets against it.
- Frames go to a text-returning reader agent; the main session opens only the frame a decision hangs on.

## Web target

- Read the engine's own platform docs on disk before believing any forum summary. On 5.9 the Launcher build
  already ships the web platform: no engine source build, a C++ project and one exact emscripten version.
- The web tiers use the mobile renderer: no Nanite, Lumen or virtual shadow maps. Design the look for that.
- No microphone backend on the web: a small JavaScript bridge (`getUserMedia` plus an analyser) must feed the level
  in. Sound starts only after a click or key.
- Editor-only tool plugins break the web cook: keep them out of the shipped project.
- Hosting a threaded Wasm build needs cross-origin isolation headers (COOP and COEP) on the static host.

## What was slow or broke

- Compiles take 2 to 10 minutes and stall when RAM is short: run them in the background and patch the next thing.
- Material recompiles fail without a renderer: save only, and the game compiles on first load (first seconds dark).
- A GLB with skin data imports as a skeletal mesh: strip vertex groups, modifiers and shape keys first.
- Scans of real places have holes and tight spots: measure headroom along the path and scale before building on it.
- A paid API's credit check can rate-limit a burst of calls: space generation calls a few seconds apart.
