# Blender: Headless Runs and Version Names

Read before any Blender step.

## Run Blender headless safely

- Find the binary: `blender` on PATH, else the default install folder of your OS. Read the skill's `local.md` first when it exists: it holds this machine's paths and job rules.
- Command: `blender -b scene.blend -t 6 -P script.py -- args`. Write the script to a file first, never pipe it.
- Start it at below-normal priority so the machine stays usable (PowerShell: `Start-Process ... -PassThru`, then `.PriorityClass = 'BelowNormal'`; Unix: `nice -n 10`).
- Bakes use `-t 6`. Never run two heavy jobs at once, and never a bake beside a render.
- Run renders and bakes in the background. Previews are low resolution and low samples first.
- Follow the project's own rules for GPU queues and output folders.

## Version rule

- The source notes cover Blender 2.8 to 4.3. Node names, hotkeys and panels from those versions drift in 5.x.
- Always map an old name to its 5.x name before building, and say that you mapped it. Each reference starts with a "5.x names" list.
- Common ones: Attribute Transfer -> Sample Index and Sample Nearest, Align Euler to Vector -> Align Rotation to Vector, Mix RGB -> Mix (Color), bone layers -> bone collections, Auto Smooth -> Smooth by Angle modifier, Musgrave -> Noise Texture type, Eevee Bloom -> Compositor Glare.
- When a name does not resolve in the installed build, check it in the UI or by script. Do not guess. A value copied from an old video (Principled Subsurface, Filmic looks) needs re-tuning.

