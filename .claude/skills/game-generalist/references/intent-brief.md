# Intent brief: ask before you build a game

A game that misses what the user wanted is a failed game, even when it runs well. Run this brief before step 1 of the
production spine (`references/pipeline-spine.md`). It costs one short round of questions and saves a rebuild.

## When to run it

- Run it at the start of every new game and when the user changes the goal mid-way.
- Skip the questions, not the brief, when the request fills every slot. Write the brief and go.
- When another skill passed a brief, use it. Do not ask again.
- On "just do it", "surprise me" or "you choose", take the defaults, state them in one line, and go.

## The five slots

| Slot | What you need to know | Example options to offer |
|---|---|---|
| Purpose and audience | What the game is for and who plays it | jam entry, portfolio piece, post on X, client demo, learning project |
| Format | Platform, input device, session length, time box | browser on phone with touch, PC with keyboard, controller; 60 s per run; 48 h jam |
| Subject | The one-sentence promise: verb, goal, win, lose; genre | "Dodge falling rocks to reach the exit before the timer ends; hit a rock and you lose." |
| Look | Style, references, palette, mood | greybox now and a look picked at step 4; a link or image the user likes |
| Constraints | Engine, jam rules, must-haves, must-nots, tools, audio, deadline | "Unreal only", "no text on screen", "must run on a phone", "theme is X" |

## The promise sentence

- One sentence. It names the verb the player does, the goal, how they win and how they lose.
- No "and" joining two mechanics. If it needs "and", it is two games: pick one (a default from jam experience, change if the user insists).
- Test: a fresh agent restates the loop, the win and the lose from the sentence alone. If it cannot, rewrite.

## Not a copy

- "Like X", "a remake of X" or "X but with Y" becomes genre mechanics with an original theme, characters, art and levels.
- Never reuse an existing commercial game's name, characters, art, music or levels, even as a placeholder or in an example.
- Write one line in `brief.md`: "Mechanics taken: <list>. Original: theme, art, names, levels." Say the rule once to the user
  if the request was a remake, then follow it.
- Genre conventions (platformer jump, match-three, tower defense lanes, twin-stick aim) are free to use.

## Scope budget and cut list

- Put the time box in the brief: hours for a jam, days for a game, one sitting for a prototype.
- Budget by feature count, not by hope: 5 to 15 features in total (default), the core loop first.
- Write the cut list now: the 3 to 5 things you drop first when time runs short. Cut in that order, never the core loop.
- Stop and cut features when a phase fails twice.

## Engine pick

- The engine is a brief slot, not a mode.
- Browser target: three.js, Phaser or plain canvas. Pick the lightest that fits (plain canvas for 2D arcade, Phaser for
  2D with scenes and physics, three.js for 3D).
- Light 2D or 3D game with a native build: Godot or Unity. When the slot is open and no earlier answer is on record,
  ask once with Godot as the recommended option, and record the answer in `brief.md`. Do not ask again in later games.
- Photoreal, or a jam that requires it: Unreal.
- A jam's rules override the pick. Films and stills are not this skill.
- Engine steps live in the use-3d-software skill.

## How to ask

1. Read everything first: the prompt, attached files and links, the project folder, earlier messages. Fill each slot you
   can infer and mark it inferred.
2. Do not ask what you can check yourself (installed engines, jam rules on the jam page).
3. Ask only about empty or ambiguous slots that would change the result. A slot with a safe default needs no question.
4. One round, at most 4 questions. Each names the slot, gives 2 to 4 concrete options, recommended option first.
5. Where the agent has a question tool, use it. Elsewhere, send a numbered list and end with:
   "Reply with numbers, or 'ok' to take the first option of each."
6. Never ask "is this plan OK?". Ask the decision itself.

## Write the brief

Write `brief.md` in {{WORK_DIR}}, 8 to 12 lines:

- Goal in the user's own words, then one line on what done looks like ("a playable browser build and a 45 s capture").
- The five slots, each marked given, answered or default.
- Not-a-copy line, scope budget, cut list.
- Gate thresholds that differ from the defaults (frame-time p95 and its target machine, softlock seconds N). Mark any
  number you did not measure as a default.
- Out of scope: what you will not make. Always: publishing, deploying, spending, accounts.
- A `## Progress` section, one line per spine step, filled as each step finishes (format in the spine).

Show the brief in one short message and start work. Stop only if the user changes something.

## Checkpoints while building

- The checkpoints are the spine's:
  - Step 4: prep sheet, the playable greybox of the core loop (the user plays it), and style frames A/B/C. The user picks
    a look and gives a one-line reason; write `LOOK.md`. Whether the loop is fun is the user's call.
  - Step 6: send a playable link to the first finished slice without waiting for a reply.
  - Step 8: the preview is the playable build plus a 30 to 60 s capture of real play. Send a low-quality capture first.
- The link is a local file or a localhost address. Never deploy, publish or spend unless the user asks.
- After the preview, offer two or three next directions and "you decide". The answer picks a fix round, a round in the
  user's direction, or free creative mode (the spine's last section).
- When the user gives notes, update `brief.md` or `LOOK.md` first, then change the game. A note that changes the
  promise or the format restarts the brief.
- Prototype mode ends at step 4 with a go/kill note (format in `design-one-pager.md`). Polish mode starts at step 6 and
  adds no features.

## Drift check before delivery

Compare the build with `brief.md` slot by slot, then with the frozen `features.json`. Fix what you can. List each slot
or feature that still differs, with the reason, in the delivery message. Never hand over a game whose promise,
platform or controls differ from the brief without saying so first.
