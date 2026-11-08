# Channel Graphics Guide (apply to every motion graphics job)

## Canvas
- 1920 × 1080

## Safe area — reserved zones (measured from `safe-area-guide.webp`)
Keep all scene text, numbers and key visuals OUT of these zones.
Background imagery may run underneath them.

| Zone | x (px) | y (px) | Notes |
|---|---|---|---|
| Top-left box (channel logo) | 59 – 253 | 45 – 151 | |
| Top-right bar | 1571 – 1920 | 115 – 151 | split at x ≈ 1832 |
| Bottom-left box | 59 – 353 | 801 – 907 | darker inner block x 72 – 253 |
| Bottom band (full width) | 0 – 1920 | 913 – 1080 | ticker / lower third |

Practical content area: **y 160 – 790** across the full width
(right of x 360 it may extend down to y 905).

## Colour palette (from `palette-reference.png` — palette only, not the layout)
| Colour | HEX |
|---|---|
| Orange | `#FF6000` |
| Dark grey | `#3C3C3C` |
| White | `#FFFFFF` |

All graphic elements (caption bars, numbers, rules, arrows, icons) use these three.
Subject colours (e.g. green trees) stay only inside the imagery.

## Typography
- Font: **Neue Haas Bloomberg** (supports Arabic + Latin)
  - Black → main title
  - Bold → sub-title
  - Regular → body text

## Numbers
- Always Western digits 0–9 (never Eastern Arabic ٠١٢٣).
- Percent written as `50%`.
- Negative written as `-2.2`.

## Captions
- On-screen text (call-ups) must match the script word for word: no additions, no omissions.
- Full creative freedom in the visual execution.

---

## Production lessons (from the Green Initiative job) — apply to every new project

### Workflow
- Read the script fully; on-screen text (call-ups) word for word — no additions, no omissions. Creative freedom only in the visual execution.
- Get the VO first and transcribe it (Whisper) to time every scene and every number to the spoken word.
- Show a styleframe board before building; agree on ONE style reference and keep colour, light (direction + time of day) and materials identical across all shots.
- Discuss before executing when the client asks for it; confirm decisions in one list.
- Ask for `build_log.txt` + a screenshot (or the render) whenever something looks wrong — don't guess.

### After Effects scripting (AE 2026)
- Expressions run on the JavaScript engine: never `array + array` — write each axis (`[value[0]+x, value[1]]`) or use `add()/sub()`.
- Re-fetch properties after every `addProperty()` (old references become invalid).
- Use correct matchNames (`ADBE Rotate Z`, not `ADBE Rotation`); one bad call aborts the whole scene — wrap risky calls in try/catch and log to `build_log.txt`.
- Arabic text placement: anchor point via expression `sourceRectAtTime()` at render time (right edge for RTL captions); do NOT rely on build-time measuring or paragraph justification.
- Stamp every build (`BUILD yyyy-mm-dd-X`) in the alert and the log so the right file is confirmed.

### Look
- One caption system for all scenes: right-hand block inside the safe area; tag 50 Black on orange, headlines 80 Black, labels 58 Bold, primary number 180 Black orange, secondary 140 white, units 70 Bold left of the number.
- Effects only where the scene needs them (rain where it rains, smoke where there is smoke…); avoid decorative clutter (god rays, bokeh blobs, HUD rings were rejected).
- Smoke/heat displacement must be masked so solid objects never warp.
- Maps must use real borders (Natural Earth) — never AI-drawn borders; no flight-path arcs unless asked.
- Currency/landmarks must be accurate or neutral (no US dollars for riyal figures).
