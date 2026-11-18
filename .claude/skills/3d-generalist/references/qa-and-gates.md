# Automated Anti-Slop QA and Render Gates (`qa-and-gates.md`)

Never trust a single preview or code change by eye alone. Numbers miss what a frame shows, and a single still misses
what happens between frames. Every 3D video must pass **both** automated numerical checks at 30 fps and visual contact
sheet inspection before the user sees a preview. This is step 8 of `pipeline-spine.md`: it runs after the build and
the sound, never in place of the look gate at step 4.

## 1. The Preview Gate

Run these checks across the entire film at 30 fps (`window.placeTime(t)` for fast geometry checks without rendering, and
real page renders for visibility checks). **One failure blocks the preview.** `scripts/check_contact_and_slip.mjs`
measures gates 1 to 4 only (three.js pages; a Blender set uses gate 14's script); grip, clearance, exits, chips and caption sync need the project's own checks. Gates 8
and 9 apply to narrated pieces with label chips.

| Gate | Threshold / Rule | What it catches |
|---|---|---|
| **1. Contact & Support** | Lowest vertices of every stone, prop, structure and planted foot/knee/hip sit within **1 to 2 cm** of the real mesh below (at least 3 contact points for stones). Base is lit and visible. | Floating stones, hovering workers, crouching past a cliff edge, towers floating on dark unlit islands. |
| **2. Flight Check** | Both heels and both toes are never >3 cm above the surface under them at the same time outside `airborne` jump/climb/dance beats. | Walk cycles or kneel transitions that hop into the air for 5 to 7 frames. |
| **3. Foot Slip** | Any heel or toe within 3 cm of the ground moves at **<0.25 m/s** (no slide lasting 3+ frames). Turns pivot on the ball of the foot. | Moonwalking, skating during clip blends, pushing a cart faster than stride speed. |
| **4. Teleport & Speed** | Character hips move **<0.30 m per frame** and walk speed stays **<2.0 m/s** over any 0.3 s window. Camera cuts happen inside 1 frame interval. The camera never jumps >0.3 m or >15° in one frame except at a cut in the shot list, and never cuts to a reverse angle (>90°). | Word-anchored walk keys that jump 0.9 m after audio trimming, or slow pans across a teleport gap. |
| **5. Hand Grip & Cause** | Both palms sit within **3 cm** of the gripped surface or handle on every active frame. No prop, door, fire or mechanism moves without a hold, grip or explicit `free` physics flag. | Pulling a chain hanging in mid-air, buckets pouring sideways 0.6 m from the pan, cranks spinning on their own. |
| **6. Clearance** | Hard hat, head, chest, hips, thighs, knees and shins never penetrate a box surface, wall, door leaf or spoil mound (>5 cm brush). On a hand-to-face grip the forearm midpoint stays ≥3 cm off the chest. Standing hips stay above ~0.65 m (1.8 m character) outside kneel, sit and crouch beats. | Stopping mid-stride with a toe 27 cm inside a door or 44 cm inside a hearth; blocks passing through the head. |
| **7. Abrupt Exit & Vanish** | No mesh, trail, flow line, sprite or label goes from visible to hidden (or jumps >15 cm) between two adjacent frames without an ease-out motion. Old beat props leave when the beat ends. | Wind lines or labels snapping off in 1 frame; rain, dung or tools lingering into the next beat. |
| **8. Chip Hygiene** | Every on-screen label chip is a technical part name actually spoken in the narration, shown for at least 1 s and hidden 1.5–2 s after the word. | Number chips (`"62 BC"`), place chips (`"HAWAII"`), or a card naming the final object at the end. |
| **9. Caption & Voice Sync** | Every spoken word's caption appears within **±0.05 s** of the mean of 3 ASR transcriptions. Zero internal voice silences >0.4 s. Duration is 55 to 65 s for Shorts. | Drifting captions, ElevenLabs trailing 1.5 s full-stop stalls, padded waits (*"6 months later..."*). |
| **10. Contact Sheet Visual Review** | Inspect `scripts/contact-sheet.sh` grids at 1 fps (and per-shot stills) to verify silhouettes, elbow angles, pour alignment, water levels and lighting. | Backward carts, backwards arms, black `NaN` water patches, dark faces inside cutaways. |
| **11. Look Match** | `scripts/compare_look.py --style <picked style frame> <preview>`: mean luma within 20 of 255, mean saturation within 0.08, mean hue turned under 20 degrees, on every sampled second. Light direction and lens checked by eye on one still per shot against `LOOK.md`. | Shots rendered darker, greyer or in another colour cast than the look the user picked; parallel shots drifting apart in grade. |
| **12. Phone Check** | The contact sheet looked at 360 px wide: the subject reads in every shot, the hero is separated from the background by value, and readable text is at least 5% of frame height and clear of the platform UI (bottom 15%, right edge on vertical video). | Subjects lost in a busy set, labels too small on a phone, captions under the like button. |
| **14. Frame Audit (Blender sets)** | `scripts/blender_frame_audit.py` on the film's camera, before the first still goes to the user and after every prop move: no object reported `FLOATS` (hung, leaning and resting things touch their support; a hook passes through the hole, measured), no hero prop `cut by the frame edge` or under 3% of the frame unless meant, no bare surface over about 15% of the frame left undressed. Then one zoomed crop of each spot that changed, read before sending. | Ladles hovering beside their hooks, vegetables cropped at the edge, empty wall and counter the user has to point at, three rounds on one fix because only the full frame was looked at. |
| **13. Brief Drift** | `brief.md` compared slot by slot with the preview: purpose, format, length, subject beats, look, constraints. | A film that is well made but is not what was asked for. |

## 2. Keeping QA checks fast (<30 seconds)

- Expose `window.placeTime(seconds)` on the scene page so `scripts/check_contact_and_slip.mjs` updates transforms and
  skeletons without running the WebGL pixel shader or post-processing passes.
- Skip instanced grass blades, rain/snow particles and camera-sized sky domes when building raycast BVH caches, and
  reuse static mesh BVHs across frames.
- Render the fast **540p preview** (`scale = 0.5`, `blur = 1`) first, mux with the -14 LUFS audio mix, run the gate, and
  render the **1080p 6-subframe motion-blur final** only after user sign-off.
