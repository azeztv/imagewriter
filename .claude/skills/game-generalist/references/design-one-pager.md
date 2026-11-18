# Design one-pager, features list and go/kill note

One page is enough: every worker reads all of it. Write `design.md` at step 3, `features.json` beside it, and freeze
both at step 4 when the greybox is playable.

<!-- skill-navigation:start -->
## Reading Map

- [Design one-pager, features list and go/kill note](#design-one-pager-features-list-and-gokill-note)
- [One-page template](#one-page-template)
- [Core loop checks](#core-loop-checks)
- [features.json](#featuresjson)
- [Freeze and change log](#freeze-and-change-log)
- [Go/kill note (prototype mode)](#gokill-note-prototype-mode)
- [Worked example: an original 60-second arcade toy](#worked-example-an-original-60-second-arcade-toy)
<!-- skill-navigation:end -->

## One-page template

Keep `design.md` to one screen of text. Leave out anything that does not change a decision.

```
# <Title>
Promise: <one sentence: verb, goal, win, lose>
Genre and mechanics taken: <list>   Original: <theme, art, names>

## Core loop
Input:    <what the player does, per device>
Rule:     <what the game does in response>
Feedback: <what the player sees, hears, feels>
Win:      <exact condition>
Lose:     <exact condition>
Restart:  <key or tap; target under 2 s>

## Controls
<every input, one line each; this list also goes on screen or in the README>

## Progression (3 lines)
Start: <what is easy>   Ramp: <what gets harder, how>   End: <last state>

## Fail state
<what the player sees on losing, what it costs, how fast they retry>

## Scope cut list
Cut first: 1 <...> 2 <...> 3 <...>
```

## Core loop checks

- Win and lose must each be reachable by scripted input. If the loop has no lose, add a timer or a threat.
- Restart returns to the same initial state as a fresh load with the same seed.
- First player input within 10 s of load and one full loop under 60 s are targets for the greybox (defaults).

## features.json

An array of 5 to 15 items. The core loop, win, lose and restart are always items.

```json
[
  {
    "id": "move",
    "description": "Player moves left and right with arrow keys or A/D",
    "verify": "replay replays/move.json; expect state().playerX > 100 after 1 s",
    "passes": false
  }
]
```

| Field | Rule |
|---|---|
| `id` | short, lowercase, unique |
| `description` | one sentence, player-visible behavior |
| `verify` | a concrete machine check that names its command: a replay file plus the expected state values, or a named unit check on the shared `sim.js` for a pure rule. Asserts game state, not pixels alone. End-to-end items (win, lose, restart) need a browser run. "Looks right" is not a verify step |
| `passes` | `false` at start. Flip it to `true` only after the verify step ran and matched. Never edit the other fields to make a check pass |

Replay files follow the input replay format: an array of `{t: ms, type: "key"|"pointer", key?, x?, y?, action: "down"|"up"|"move"}`.

UI features (title, pause, HUD, feedback toggles) verify through a Playwright check that reads the optional `screen()`
and `effects()` hooks and saves a screenshot (`playtest-gates.md`). A native dialog cannot be seen by browser
automation: add a scripted manual check as its verify step.

## Freeze and change log

- List freeze, end of step 4: add a `## Freeze` line to `plan.md` with the date and item count. After it, adding or
  removing a feature needs one line in `plan.md`: id, reason, what was cut to pay for it.
- Feature freeze (alpha), when all items pass, and content freeze (beta), after the preview round: fix only, every
  edit logged in `plan.md`.
- Check before delivery: every item has a verify step, and none passes without a run behind it.

## Go/kill note (prototype mode)

A prototype ends at step 4 with `go-kill.md`, 6 lines. Write it when the gate message goes out, with `Decision: not played yet` and the bot
result lines; fill the human note, decision and reason after the user plays. Kills are normal; write the reason so the
next game reuses it.

```
Decision: go | reshape | kill | not played yet
Promise tested: <the sentence>
Bot result: win reached yes/no, lose reached yes/no, restart ok yes/no
Human note: <what the user said after playing, in their words, or "not played yet">
Reason (one line): <why this decision>
If reshape: <the one change to try next>
```

Rules:

- Agents never write "fun". The decision rests on the user's play note. With no note, the decision is "not played yet".
- Kill when the loop reads as a chore after one run, when no change to rules or numbers was found in two rounds, or
  when the time box would pass without a playable.
- Reshape when the loop works but one rule is off (too slow, too hard, no stakes).
- Go means moving to step 5 with the same promise.

## Worked example: an original 60-second arcade toy

```
# Lantern Run
Promise: Steer a lantern through a dark maze of drifting moths to reach the exit before the oil runs out.
Mechanics taken: top-down steering, timer. Original: lantern, moths, oil, names and art.

## Core loop
Input:    arrow keys or drag on touch moves the lantern
Rule:     moths drift; a touch drains oil; oil also drains over time
Feedback: lantern light shrinks as oil drops; a soft chime on exit; a thud on a moth hit
Win:      lantern reaches the exit tile
Lose:     oil reaches 0
Restart:  R key or tap anywhere on the end screen

## Controls
Arrows or WASD move. R restarts. On touch: drag.

## Progression (3 lines)
Start: two slow moths.  Ramp: one more moth every 15 s.  End: exit opens at 60 s of oil.

## Fail state
Screen dims, "Out of oil", restart in one input, same seed.

## Scope cut list
Cut first: 1 second maze layout  2 oil refills  3 high-score table
```

Matching `features.json` ids: `move`, `moth-drift`, `oil-drain`, `win-exit`, `lose-oil`, `restart`, `controls-shown`.
Example verify for `win-exit`: `replay replays/win.json with seed 1; expect state().status == "won"`.
