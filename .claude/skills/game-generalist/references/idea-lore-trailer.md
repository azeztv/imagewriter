# Idea, lore and trailer (`idea-lore-trailer.md`)

Use at step 1 (brief) and step 2 (reference) for the idea and the lore, and at step 8 for the capture and trailer.
Every line here was paid for on a real jam prototype; none is theory.

<!-- skill-navigation:start -->
## Reading Map

- [Idea, lore and trailer (`idea-lore-trailer.md`)](#idea-lore-and-trailer-idea-lore-trailermd)
- [Idea: check before committing](#idea-check-before-committing)
- [Lore: one rule becomes the mechanic](#lore-one-rule-becomes-the-mechanic)
- [The core loop must work with the gimmick off](#the-core-loop-must-work-with-the-gimmick-off)
- [The player must see enough to play](#the-player-must-see-enough-to-play)
- [Trailer and capture](#trailer-and-capture)
<!-- skill-navigation:end -->

## Idea: check before committing

- Search prior art before the brief is frozen: the genre's known games, plus two or three searches with the mechanic's
  own words. Write one "take / leave" line per game in `refs/NOTES.md`. Twists that feel new are often already shipped:
  drop them or go one step further, and write the difference into the brief as one sentence.
- Ride something live when the game is meant to be posted: a news item, a new engine feature, a jam theme. The brief
  names it and links the source read at the owner's page.
- Pick a genre that hides the target's limits. A weak renderer (web, mobile) suits dark, abstract or stylized games;
  unlit points on black cost almost nothing and hide the lack of real-time lighting.
- Read the jam rules before building anything. If the jam forbids work before a start date, the early work is a
  throwaway prototype: keep a `DECLARE.md` listing every file, asset and sound made before the date, and rebuild fresh.

## Lore: one rule becomes the mechanic

- Build on a real myth, record or event, read from a reputable source. Mark each fact verified, reported or unknown,
  and never quote a translation in the game until the wording is checked by hand.
- Find the one rule in the source that can be played, and make it the core mechanic. Example shape: "the lords below
  are angered by noise" becomes a noise meter that every action feeds.
- Imply, do not explain. No lore dump: the rule is felt through play, names appear on the HUD and in short radio
  lines, and the twist is carried by who speaks, not by a text screen.
- A living culture's story is a setting, not a villain. No real community is named as the threat, and assets taken
  from real sites are credited.

## The core loop must work with the gimmick off

- A hardware gimmick (microphone, camera, motion) is an extra layer. The loop must be fun with it denied or silent:
  many players refuse the permission or never speak. Build the keyboard loop first, the gimmick last.
- Give the loop a cost and a tool, both from the same lore: seeing costs something (charge, noise), and one item
  lets the player spend risk elsewhere (a thrown decoy that must be picked up again).
- State the threat's rule in one line the player can learn in a minute, such as "it only moves while you are not
  looking". A rule that cannot be said in one line cannot be played around.

## The player must see enough to play

- A "you cannot see" horror game still needs a readable near field at all times. Give a weak, free, always-on view
  (short range, sparse, blind to the threat) and make the strong view the costly one.
- Scary is not loud. Keep the common action's sound soft and short; save volume for the rare event.
- Check readability on a small, compressed capture, not in the editor: dots that look fine at full size vanish at
  960x540. Turn off bloom, motion blur and temporal anti-aliasing for point-like visuals, and keep emissive values
  under 1 so colours do not wash out to white.
- The first preview goes to the user early and ugly. Expect "not scary, cannot see": that is the brief for round two.

## Trailer and capture

- Order: genre, then hook, then content. The hook is in the first shot or the first 10 to 15 seconds, and it is a
  thing seen, not a sentence.
- Gameplay first. A mechanic the viewer cannot feel (voice, haptics) gets one on-screen beat that shows cause and
  effect: the meter jumps when the player speaks. The visual hook still leads.
- End on a turn: the last shot changes what the viewer thought the game was.
- Jams usually require a 30 to 60 s gameplay video: record it from a scripted run with the game's own audio so
  picture and sound stay in step, and keep clean in-game clips (no editor) at every milestone for posts.
- Keep a devlog source log from day one: one line per step with what was tried, what broke, the fix and numbers.
