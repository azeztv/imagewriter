# Editing Craft for Any Editor

How to cut a piece so people keep watching, in any editor. The steps name the idea, and each tool reference gives
the buttons. Platform numbers change often, so check the platform's help page before relying on a limit.

<!-- skill-navigation:start -->
## Reading map

- [Editing Craft for Any Editor](#editing-craft-for-any-editor)
- [Plan the cut](#plan-the-cut)
- [Hook and pacing](#hook-and-pacing)
- [Cuts that feel smooth](#cuts-that-feel-smooth)
- [Beat sync](#beat-sync)
- [Captions and text](#captions-and-text)
- [Framing for vertical](#framing-for-vertical)
- [Sound in the edit](#sound-in-the-edit)
- [Platform export](#platform-export)
<!-- skill-navigation:end -->

## Plan the cut

**Cut to a script or a beat sheet**
1. Write the beats first: hook, setup, turns, payoff, end. Give each beat a target length.
2. Lay the voice or the music down first. Cut picture to it, not the other way round.
3. Make a rough cut with every beat in order before any effect.
- Use when / pitfalls: effects on a cut that still moves get redone. Finish timing before transitions and grade.

## Hook and pacing

**First seconds**
1. Open on the most interesting moment or the question the video answers. Never a logo or a slow fade in.
2. Put motion in frame 0. A still first frame reads as a frozen video in a feed.
3. Show the payoff or a teaser of it within the first 3 seconds when the piece is a Short.
- Use when / pitfalls: viewers decide in the first seconds. A long title card is the most common drop point.

**Pacing**
1. Change something on screen every 1 to 3 seconds in a Short: a cut, a zoom, a new caption, a new angle.
2. Vary shot length. Speed up in the build, hold a beat on the reveal.
3. Cut dead air from speech: breaths and pauses over about 0.3 s, unless the pause is the joke or the tension.
- Use when / pitfalls: equal shot lengths feel mechanical even when each shot is good.

## Cuts that feel smooth

**J cut and L cut**
1. J cut: the next shot's audio starts before its picture.
2. L cut: the current shot's audio carries on over the next picture.
- Use when / pitfalls: hard cuts on both picture and sound at the same frame feel abrupt in dialogue.

**Match cuts and cutting on action**
1. Cut in the middle of a movement so the motion carries across the cut.
2. Match shape, colour or screen position between the outgoing and incoming shot.
3. Keep the subject in the same screen area across a cut so the eye does not hunt.

**Transitions**
1. Use a hard cut by default. Use a styled transition only when it carries meaning or energy (a whip pan on a beat).
2. Keep one transition family per piece.

**Joins in explainer Shorts (measured)**
Three popular explainer Shorts were measured frame by frame (a 3D render explainer with 17 cuts, a game-dev tutorial with 38, a stock-footage science Short with 11). None had a crossfade at any cut. What they did instead:
1. Hard cut on an event: a sentence start, a key noun, a click, an impact. In a tutorial every UI step gets its own cut, at the click.
2. Cut while something is already moving (objects falling, a cursor travelling, facets turning). Never cut from a still to a still.
3. Change scale or angle at the cut and keep one anchor fixed on screen: the subject's position, a HUD counter, the cursor. A wide shot cut to a macro of the same pile reads as a punch-in, not a jump.
4. Swap in place: same framing, and the state changes (a menu opens, a render setting flips, a card swaps for the 3D view behind it). This was about as common as a crop change.
5. At most one special join per beat, used for a reason: one whip with motion blur on a change of subject, a dip to dark or an exposure flash to mark a new scene, a foreground object that wipes the frame. Everything else stays hard.
6. Overlays (outlines, labels, "?" marks, cards) pop in a few frames after the cut lands, never on the cut frame. The old caption leaves on the old shot; the new one arrives on the new shot.
7. A reference card enters blurred or pixelated and sharpens over about 0.7 s while the background defocuses. It holds 2 to 3 s once sharp, then shrinks or slides out over 0.3 to 0.5 s.
8. Keep something moving inside every shot: a slow drift or push, a live counter ticking every 0.25 to 0.5 s, a gizmo that rotates. A visible change every 1 to 3 s.
9. Alternate background type and brightness between neighbouring shots so a hard cut reads as intended.
- Use when / pitfalls: crossfades, slides, zooms and spins between shots are the slideshow look viewers call cheap ("PowerPoint"). The stock-footage Short with text fading on gradient cards looked weakest of the three. Two joins that are really one camera move (the same camera continuing, the same object from the same angle) play as one seamless shot, with no transition.
- Check: `uv run --no-project --with numpy python <skill>/scripts/check_blended_cuts.py <video>` lists every crossfade or dissolve (frames that mix the shot before and after; dips to black and flashes are allowed) and exits 1 if any is found. Run it on each preview before it goes out.

## Beat sync

**Cut on the beat**
1. Add markers on the beats (tap the marker key while the music plays, then nudge to the waveform peaks).
2. Snap cuts and effect peaks to the markers. Land big hits on the downbeat.
3. A speed ramp eases in before the beat and peaks on it.
- Use when / pitfalls: picture that lands one or two frames late feels off. Check at full frame rate, not a preview.

## Captions and text

**Captions for Shorts**
1. Generate captions with the editor's auto captions or the `watch-video` skill (`references/speech.md`), then fix names and numbers by hand.
2. Keep 1 to 4 words on screen at a time, synced to the spoken word within about 0.1 s.
3. Use a bold sans font with an outline or a shadow, large enough to read on a phone.
4. Place captions inside the safe zone (below).
- Use when / pitfalls: most people watch muted at first. Auto captions mishear names and numbers.

**Titles**
1. One idea per title. Hold it long enough to read twice.
2. Animate in with a short ease out, and out faster than in.

## Framing for vertical

**Safe zones**
1. Keep faces, text and key action in the middle band of a 1080x1920 frame.
2. Leave roughly the top 10 to 15 percent and the bottom 20 to 25 percent clear: the app puts the account name,
   caption, buttons and progress bar there. The right edge carries the like and share buttons.
3. Export a frame with a safe-zone overlay to check, or use the editor's guides.
- Use when / pitfalls: the exact bands differ by app and change with app updates. Check one real upload.

**Reframe landscape footage**
1. Keyframe the crop to follow the subject, or use the editor's auto reframe and fix its misses.
2. For wide shots that lose too much, place the shot over a blurred copy of itself.

## Sound in the edit

**Levels**
1. Voice sits on top. Music drops 8 to 15 dB under voice (duck it or keyframe it).
2. Every visible impact gets a sound. A loud moment lands harder after a short silence.
3. Measure the final loudness and aim near -14 LUFS integrated with peaks under -1 dBTP for streaming.

## Platform export

**Settings that work everywhere**
1. H.264 in MP4, yuv420p, AAC 48 kHz, the source frame rate, high bitrate (or CRF 18).
2. 1080x1920 for vertical Shorts, Reels and TikTok. 1920x1080 or 3840x2160 for landscape YouTube.
3. Check the current maximum length and file size of each platform before upload. They change often.
- Use when / pitfalls: 10-bit or HDR exports can upload with washed-out colour. Export SDR Rec.709 unless the
  platform and the viewer both support HDR.
