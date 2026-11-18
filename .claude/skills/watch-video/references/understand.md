# Understand a video

Use this for any video once it has been watched and heard (SKILL.md steps 1 to 4), whenever the user wants more than
a description: what it is for, what it means, whether it is right, what is out of date, what is worth learning.
Seeing every frame is not understanding. A summary that only retells the video in order is not this.

Reading map: 1 Kind · 2 Purpose · 3 Thesis and structure · 4 Claims · 5 Craft · 6 Lessons · 7 Output · Per kind ·
Worked example.

## 1. Kind

Name the kind from the title, channel, length, description and first 30 seconds: tutorial, explainer or essay, talk
or podcast, news or report, review or comparison, ad or launch, short-form or meme, film, animation or music video,
vlog or documentary, livestream or gameplay. A video can be two kinds (a sponsored tutorial). The kind decides what
"right" and "good" mean below; the table at the end lists what to check for each.

## 2. Purpose

- Who made it, for whom, and what they want the viewer to do, believe or feel: learn, buy, subscribe, vote, laugh.
- Follow the money: sponsor reads, affiliate links, the creator's own product, Patreon, a client brief. Say whether
  the stated purpose and the real one differ.
- Take the creator's own words about the work seriously: what they say they skipped, rushed or faked is part of
  the meaning. The creator said the forest was a quick client mock-up and the fog "covers up the lack of good design".

## 3. Thesis and structure

- The whole video in one sentence: what it claims, shows or argues.
- The beats with times: hook, setup, each turn, payoff, call to action. Use chapters, cuts, the transcript, the most
  replayed heatmap (it marks what viewers came for) and the tone table.
- What is left out: the obvious objection never raised, the step skipped, the cost never mentioned.

## 4. Claims: right, wrong, out of date

1. List every load-bearing claim with its time: spoken (transcript), on screen (`scripts/read_screen.py` reads
   labels, numbers and names) and in the description. Skip filler.
2. Give each one status: **true**, **false**, **out of date** (true at upload, not today), **unverifiable**, or
   **opinion**. Check the claims that matter at their owning source with `research-and-verify`; mark the rest as
   not checked. The upload date against today decides out of date: versions, renamed menus and nodes
   (`scripts/check_blender_names.py` for Blender), prices, "latest", "best", records, laws, people's roles.
3. Read the top comments and replies for corrections, "does not work" reports and timestamps others flagged. A
 repeated complaint is a pitfall the video hides. fog: "the other half is fully opaque" was the box
   placement trap that also broke the rebuild.
4. A method can be right and dated at once: say what still works today, what moved, and the current way.
5. Claims about time are where video readers fail most, models and people alike: order ("first X, then Y"), counts
   ("three hits", "every 2 s"), how long something lasts, and before/after. Video LLM benchmarks in 2026 put most
   errors there, while single-frame content scores high (VidOmni-Bench, TimeBlind, the VideoHallucer and ELV-Halluc
   scores in the 2026 hallucination survey). State each one with the two timestamps that prove it, and count from
   the 8 fps zoom, not from tiles at 2 per second.

## 5. Craft

- What works, with the measurable reason: hook in the first 3 s, cut rate, a silence before the hit, music that
  turns with the story, an on-screen label the moment a term is said. Cite the second.
- What fails: technical mistakes, misleading framing or thumbnails, padding, unclear audio, steps that cannot be
  followed, claims shown as facts. Separate an error (provably wrong) from taste (a choice you would make differently).
- For a tutorial, also: can a viewer follow it to the result? The steps it hides are where rebuilds fail.

## 6. Lessons

Rank the lessons, most useful first. Each is one actionable line, tagged: technique, craft, fact, pitfall, business.
Say which apply to the user's own work and how, and list what not to copy (a dated method, a misleading trick, a
licence problem). A lesson with no action ("the video is well made") is dropped.

## 7. Output

Lead with the one-sentence thesis and the purpose. Then, short sections in this order: kind and audience; structure
with times; claims table (claim, time, status, source); what works; what fails; lessons ranked; out of date with the
current way. Mark each statement seen, heard, measured, checked or guessed. Save it as `UNDERSTANDING.md` next to the
watch output when the user will come back to it.

## Per kind

| Kind | Purpose to name | Check first | Usually out of date |
| --- | --- | --- | --- |
| Tutorial, how-to | what the viewer can build after | each step reproduces; values and which handle they belong to; hidden steps; comments' failure reports | software version, menu and node names, removed features, add-on availability |
| Explainer, essay | the argument and who it persuades | key facts and numbers at the source; missing counter-arguments; charts' axes | statistics, "current" state of a field |
| Talk, podcast | the speaker's thesis and stake | claims vs the speaker's interest; quotes checked against audio | predictions, roles, company facts |
| News, report | what happened, according to whom | sources named; what is confirmed vs reported; later corrections | everything: check what happened since |
| Review, comparison | the verdict and its criteria | test method; sponsor or gifted product; measured vs felt | prices, versions, newer rivals |
| Ad, launch, promo | the action wanted and the promise | claims vs product page and fine print; demo real or rendered | specs, prices, availability |
| Short, meme | the joke or hook and why it spreads | the format's origin; the sound's source | the trend itself |
| Film, animation, music video | the feeling and story | craft only: shots, cuts, sound, colour, motion; credits | tools only |
| Vlog, documentary | the story and the point of view | what is staged; facts in narration | facts in narration |

## Worked example

A ground-fog tutorial for Blender 2.90 (uploaded 2020-09-10), checked 2026-11-07:

- **Thesis and purpose.** A volume box with an emission ramp makes cheap ground fog in Eevee. It was made to rescue
  a rushed client scene.
- **Craft that holds.** Fog driven by Emission Strength with density 0 never darkens the scene. A noise and
  gradient mix shapes it. A photo on a plane stands in for a far forest.
- **Pitfall the video hides.** The gradient lights only the half of the box under its centre, so the box must sit
  well above the ground. A comment reports the "other half fully opaque".
- **Out of date.** Blender 2.90 has given way to 5.x. MixRGB is now the Mix node in Color mode. Eevee bloom moved to
  the compositor. Volumes changed with Eevee Next in 4.2. Check the numbers on today's Eevee before trusting them.
- **Lessons.**
  - Trace a tutorial's assets before modelling anything.
  - Read which ramp stop a value belongs to.
  - Values are per Blender unit, so match the creator's scene scale.
