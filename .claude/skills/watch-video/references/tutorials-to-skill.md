# From a tutorial channel to a checked skill

Reading map: 1 Pick and fetch · 2 Distill · 3 Verify (required) · 4 Write the skill · 5 Prove it builds · 6 Checks.
Use for "watch this whole channel and make a skill", "turn this playlist into a skill", or adding a channel to an existing skill.
Steps 1 and 2 run in parallel workers; step 3 is never skipped.

Why step 3 exists: watching gets things wrong in three ways. Speech-to-text mishears names and
numbers. The note-writer misreads what a step is for. The video teaches an older version, so names, menus and defaults
have moved. A transcript alone cannot catch any of the three.

## 1. Pick and fetch

1. `harvest_resources.py` first (SKILL.md step 1) for the creator's free files.
2. List and pick:
   `uv run --no-project python {{SKILL_DIR}}/scripts/fetch_tutorial_transcripts.py "<channel or playlist>" --out {{WORK_DIR}}/transcripts/<creator> --list-only [--include "<topic regex>"] [--top 40]`.
   Read the list; short films, vlogs and updates are not tutorials, tighten `--include` / `--exclude` until it is clean.
3. Same command without `--list-only`. It stops asking YouTube on the first 429 and writes `pending.txt`; rerun later
   or add `--local` (Parakeet on CPU, below-normal priority). Batches land in `<out>/batches/`.

## 2. Distill

One `worker` per batch, 3 to 5 at once, brief = `references/briefs/distill-notes.md` with the batch path. Notes go to
`{{WORK_DIR}}/tutorial-notes/<batch>.md`. Each entry carries `Check` and `Version`.

## 3. Verify

Mark each entry `verified` (with how) or fix it. Order, cheapest first:

1. **Names.** Blender: `uv run --no-project python {{SKILL_DIR}}/scripts/check_blender_names.py <notes, skill folder or transcript.txt>` (a `.txt` transcript is also searched for old names in lower case, "mix rgb")
   checks every node, modifier, constraint, editor and bundled node-group name against the installed Blender
   (`data/blender-names.json`; regenerate with `blender_names_dump.py` when Blender updates). Each flag is a lead:
   a real node under another name, an add-on, a group the video builds itself, or a mishearing. Other software: check
   names against its current manual (DaVinci Resolve reference manual, Krita docs, Godot docs).
2. **Values on screen.** Every `[frame mm:ss]` and every number that decides the look (voxel size, strength, count,
   colour) is read from one full-size frame at that time:
   `yt-dlp --download-sections "*<s>-<s+2>" -f "bv*" -S "res:1080" -o "$S/clip.%(ext)s" <url>`, then
   `ffmpeg -i clip -frames:v 1 frame.png`. More than 5 frames: a subagent reads them. Fix the note to what
   the frame shows.
3. **Meaning.** For each technique, the frame at the end of its segment shows the result. If "what it makes" in the
   note does not match that frame, rewrite it from the frame.
4. **Currency.** A video older than the current major version: look the feature up in the current manual and the
   release notes (Blender: docs.blender.org/manual/en/latest and developer.blender.org release notes) for renames,
   removals and new defaults. Write the current name and keep the old one in brackets.
5. **Cross-source.** Two creators or two videos giving different values or orders: keep both with sources and say
   which one the current version or a test supports. Never average them.
6. `[unsure]` left after 1 to 5: drop the entry or keep it marked `unverified`. Never state it as fact.

## 4. Write the skill

One `worker` per skill, brief = `references/briefs/write-craft-skill.md`. Only verified entries go in as rules;
`unverified` entries stay in references with the mark.

## 5. Prove it builds

Pick the 3 techniques the skill leans on most. A fresh worker, given only the new skill, builds each one (Blender
headless with `--disable-autoexec`) and renders a still at the video's angle. Put the still beside
the video's result frame on one comparison sheet. A gap is a skill bug: fix the skill, not the render. When the look
matters or the gap is a judgement call, send the sheet to the user with SendUserFile and say what to look at.

## 6. Checks before saying "learned"

- `index.tsv`, transcripts and batches exist; `pending.txt` is empty or its videos are named as skipped.
- Every rule in the skill traces to a source link and a `verified` entry; the name check prints no unexplained flag.
- The three comparison sheets were read; any sent to the user are listed in the report.
- If the skill ships in a public pack, run its sync and release guard (global AGENTS.md).
- Creator names, channel handles and video links appear only in `Source:` or `Sources:` lines and in a `## Credit`
  section, never in headings, prose or tables. A public copy drops those lines, so the learning stays private and
  nobody can pick a fight over who it came from.
