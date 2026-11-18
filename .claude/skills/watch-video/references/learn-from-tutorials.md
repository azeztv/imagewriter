# Learn from tutorials

Use this when a video, playlist or channel is the source for building something like it, or for writing or fixing a
skill. It exists because on 2026-11-07 a low-poly character was built from transcripts alone: the creator's free
.blend files and face textures sat linked in every description, nobody opened them, and the eyes came out wrong three
times. Words describe steps. Only the creator's files and full-size frames show what the result looks like.

## Order

1. **Resources first.** Run `scripts/harvest_resources.py` on the video, playlist or channel. Open each download row:
   price, licence, gate. Free: download into `<project>/ref/<creator>/<pack>/`, one folder each. A licence risk
   (non-commercial, unknown, game-ripped): name it and ask the user once; yes means use it at their responsibility.
   Patreon pages refuse to open in Claude in Chrome: say so and try the same file on the creator's site or Gumroad.
   A CAPTCHA, a bot or AI block, a sign-in or sign-up, an email form or any payment: never click through. One line to
   the user with the link and what it unlocks, they do it themselves; keep working on the rest.
2. **Open the creator's files read-only.** Blender: `blender -b --disable-autoexec file.blend -P inspect.py` that prints
   objects, triangle counts, modifiers, materials, image sizes, UV island sizes and bones. Render their character with
   their own materials from the front and three-quarter view: that render is the target. Look at every texture: how
   eyes, mouths and shading are painted, at what pixel size, in which layers (PSD layers say more than the PNG).
   Write what you measured to `ref/<creator>/NOTES.md`.
   No files linked: trace the sources from the video itself before building anything. Read, from full-size frames
   through a subagent, every Outliner name, the title bar's .blend path, image names in Image Texture and
   World nodes, add-on tabs and the asset browser. Names give the source away: `uploads_files_<id>_<name>` is a
   CGTrader download, `<photographer>-<id>-unsplash` is an Unsplash photo (search the id, fetch through the page's
   og:image when the download link refuses scripts), `<name>_<res>k.hdr` is Poly Haven. Then fetch the same or the
 nearest free asset. Also note what the creator says they skipped: fog forest (2026-11-07) was a quick
   client mock-up whose far forest was an Unsplash photo on a plane, not hundreds of modelled trunks.
3. **Transcripts for the steps.** Captions give menu paths and order. Captions do not give looks.
4. **Full-size frames for each visual feature.** For every part that decides the look (face, eyes, hair, silhouette,
   texture, lighting), pull 2 or 3 full-size frames of the finished result with ffmpeg and read them. Tiles in a frame
   sheet are too small for line weight and proportions.
5. **Build by their construction, traced to the reference.** Use the same build method as the creator. Draw by
   tracing the user's reference at the same scale, not from a verbal description.
6. **Build along, one step at a time.** List the video's steps with their seconds (read through a subagent: full-size frames at
   every cut and every action line of the transcript: each value, link and view change). Then loop: build only the next
   step, render the same view in the same engine, put it beside the video frame of that second, say what matches and
   what does not and why, fix it, then go on. A step that does not match is never built on. The last steps are where
   tutorials tweak values (a ramp stop, a mapping offset) and where a one-pass rebuild goes wrong. Match the scene
 around the effect too: lighting, world strength and object scale decide how an effect reads. ground fog
   rebuilt in one pass (2026-11-07) came out a white slab: world near black instead of an HDRI at strength 2, Cycles
   instead of Eevee, and the last two tweaks (ramp 0.484, mapping X -0.35) missed. A value alone is not enough: read
   which handle it belongs to (the selected ramp stop, the active socket) and the scene's unit scale. Moving the
   white stop instead of the black one to 0.567 gave an even white wash, not the video's clumps, and a forest built
   in real metres piled ten times the emission of his small scene until it was shrunk to his units.
   Keep the loop fast: each round renders only the steps in question at preview size (about 320 px, 16 samples), and
   before rendering, work out on paper what the values do with this scene's numbers (coordinate range across the box,
   where a ramp threshold falls, which half of the box a rotated gradient lights). A render then confirms; it does not
   search. When the build is a test of watching, the deliverable is the understanding and the lessons, not a pixel
   match: stop and report once the cause of each mismatch is known. A 90-minute fog loop on 2026-11-07 was stopped
   by the user as too slow; understanding the causes was what they wanted.
   **Watch and do** when the user wants it followed like a person (in the app's own window, with clicks and keys):
   get the video and captions once, then per chapter run `perceive.py --from <s> --to <e>`, read that window, do it,
   screenshot beside the frame at the chapter's end, fix, next. Never run `watch.py` on the whole video first: on
   2026-11-08 a full pass on a 31 min tutorial left Blender idle for minutes and looked frozen; chapter by
   chapter, all 11 donut chapters were done in Blender by mouse and keyboard in 34 minutes.
7. **Compare, never display.** A reference image is for checking, not for the final picture or banner. Every review
   round has one comparison sheet: the reference crop, your render at the same angle and size, and the creator's render
   from step 2, plus a 50% overlay of yours on the reference. A round goes to the user only after you have read it.
   Measure before judging by eye: `scripts/compare_profile.py <frame> <render> --frame-base ... --render-base ...`
   prints brightness per band and how high an effect reaches ("video 30% up, +51; render no visible effect, +8").
8. **Feed the skill.** Every gap between the skill and the creator's files becomes an edit in the skill the same day,
   with the source link and the measured numbers.

## Checks before saying "learned"

- `resources.md` exists and every download row is marked taken, left (why) or waiting on the user.
- The creator's own files were opened and `NOTES.md` has numbers from them.
- The comparison sheet was read for each visual feature that matters.
- Each built step was compared with the video frame of its second before the next step was built.
