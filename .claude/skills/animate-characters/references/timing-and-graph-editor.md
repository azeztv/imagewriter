# Timing, Dope Sheet and Graph Editor

Keys, holds, retiming, curves and procedural modifiers for character work. Blender 4.x to 5.x names. Hotkeys are
Blender defaults.

<!-- skill-navigation:start -->
## Reading Map

- [Timing, Dope Sheet and Graph Editor](#timing-dope-sheet-and-graph-editor)
- [Keyframe basics and Auto Keying](#keyframe-basics-and-auto-keying)
- [Timeline, frame range and playback](#timeline-frame-range-and-playback)
- [Dope Sheet](#dope-sheet)
- [Graph Editor: value versus timing](#graph-editor-value-versus-timing)
- [Handle types and slow in, slow out](#handle-types-and-slow-in-slow-out)
- [Interpolation modes](#interpolation-modes)
- [Stepped modifier: on twos and threes](#stepped-modifier-on-twos-and-threes)
- [Noise modifier](#noise-modifier)
- [Cycles modifier](#cycles-modifier)
- [Motion paths and arc checks](#motion-paths-and-arc-checks)
- [Timing charts for 2D](#timing-charts-for-2d)
- [Frame rate and motion blur](#frame-rate-and-motion-blur)
<!-- skill-navigation:end -->

## Keyframe basics and Auto Keying

- Select the object (or bone), put the playhead on a frame, hover the viewport and press `I`. Blender 4.1+ keys the
  Default Key Channels from Preferences and `I` shows no menu. `K` opens the keying set menu (so "Location, Rotation &
  Scale" is a menu choice there). Older versions: `I` opens the menu.
- Field colours: grey is not animated, green is animated with no key here, yellow is a key on this frame.
  Hover a field and press `I` to key only that field.
  To replace a pose, put the playhead on the key, change the pose and press `I` again.
- The most common beginner bug is moving an object and forgetting to key it. The object hops back on scrub.
- Auto Keying: the record dot in the Timeline header. Each transform makes a key. Turn it off when done, or it keys
  later scene setup. In the Graph Editor, `I` offers "Only Selected Channels". You need a first key before Auto Keying
  records on a channel.
- Any value is animatable: material, node, colour, light strength, shape key value. Hover and press `I`.

## Timeline, frame range and playback

- Set the End frame to the last key so no dead frames render. The stopwatch icon is Use Preview Range. `P` over the
  Timeline, Dope Sheet or Graph Editor and drag a box to set it. Preview range suits polishing one passage (a landing,
  lip sync). `Ctrl+Home` and `Ctrl+End` set the start and end at the playhead.
- Move a key with `G` (closer together is faster). `Shift+D` duplicates. Box-select keys and `S` then a number
  (2 is half speed). `X` or Delete removes. Left and Right arrows step one frame. `Alt+MMB` drag scrubs.
- Markers: `M` adds a marker, `F2` renames, `G` moves. Use them for sound hits, cuts and cues.
- Playback: Timeline > Playback popover > Sync > Sync to Audio. The default Play Every Frame misreads speed. Turn on
  Audio > Scrubbing to hear sound while you drag the playhead.
- Keys vanish from view when the object is not selected or the view is scrolled. Select the object and press Home.

## Dope Sheet

- Expand the object arrow to see the channels. Home frames all keys. The Summary row moves all keys at once. `Alt+click`
  a key selects its whole frame column. `G` retimes. `Ctrl+C` and `Ctrl+V` copy keys to the playhead.
- Channel checkbox mutes, the lock icon protects. View > Show Sliders shows live values per channel. `Ctrl+G` groups
  channels. `Ctrl+Tab` toggles Dope Sheet and Graph Editor. Turn on Only Show Selected to cut noise.
- 2D: this is the exposure sheet. Use it to block and retime like a timing chart.

## Graph Editor: value versus timing

- `Ctrl+Tab` from the Dope Sheet. Numpad `.` frames the selected keys. Double-click a channel to select all its keys.
- `G` moves in both axes. Press `X` to move only timing and `Y` to move only value.
- To retime everything, set the header Pivot Point to 2D Cursor. Press `S` then `X` around the playhead, then set the
  pivot back. Plain `S` scales values and timing together and warps the pose.
- Limit selection: View > Only Selected Curve Keyframes. `Shift+H` hides all but the selected channel, `Alt+H` reveals all.
  Search "zquat" in the channel filter to find the Z rotation channels.
- Normalize (header toggle) shows rotation and location on one range. It is a view toggle only.

## Handle types and slow in, slow out

- Drag a handle, or `G`, `S`, `R` it. Flat handles are slow in and out. Pulled-in handles are snappy. `Shift+S` > Flatten
  Handles resets them.
- `V` menu: Aligned (default, mirrored handles), Free (independent, for bounces and sharp contacts), Automatic (smoothest,
  for hair and accessories, can overshoot), Auto Clamped (flat at extremes, no overshoot), Vector (straight handles).
  The key icon in the Dope Sheet shows the type.
- Impact: shape the incoming handle steep and flat so the thing accelerates and stops dead on the contact frame. A soft
  Bezier ease makes impacts float. `Ctrl+E` sets easing.
- Heel and weight: hips drop faster than they rise. A planted heel curve stays flat, with a slight overshoot on leaving.
- Motion-design curves: a bounce eases only at the apex and stays linear at impact; a snap puts most travel in a few
  frames with long flat handle tails; a loop lifts handles so speed never hits zero. The value graph shows direction, the
 speed graph shows pace. Recipes: [motion-design-2d.md](motion-design-2d.md) (entries 3, 4, 6, 8).

## Interpolation modes

- `T` on selected keys: Constant (hold, then pop to the next pose: use for blocking and for texture-offset face swaps),
  Linear (constant speed: camera dollies, mechanical motion, root travel), Bezier (default, ease in and out).
  Blender 4.x also lists Sine, Quad, Cubic, Back, Bounce and Elastic in the same menu. Back, Bounce and Elastic give
  instant overshoot, bounce and spring. Bounce is a math ball, not a replacement for hand-tuned timing.
- Order of work: block on Constant, then switch to Bezier and polish. To keep the timing, copy each pose to 3 frames
  before the next key first.

## Stepped modifier: on twos and threes

- Graph Editor, `N` sidebar > Modifiers tab (click a channel first) > Add Modifier > Stepped Interpolation. Step Size 2
  is on twos, 3 is on threes. Options: Start and End frame, Influence, Restrict Frame Range with Blend In and Out. End
  frame 0 means off. `Ctrl+Shift+M` opens the add menu.
- Untick the checkbox to compare with the smooth original. It is non-destructive.
- Use a different step size per channel (stepped body, smooth camera) for the Spider-Verse look. In 2D this is the normal
  frame hold.

## Noise modifier

- Modifiers > Add Modifier > Noise. Scale is the grain size (small is fine jitter, large is slow wobble). Strength is the
  amount. Influence is the opacity. Restrict Frame Range with Blend In and Out fades the effect in and out.
- On characters use it on loose parts (antenna, tail tip) with small strength, or on a camera for handheld shake (strength
  about 0.1). `Backspace` over a value resets it.

## Cycles modifier

- Key a loop where the last key equals the first (copy the first key with `Ctrl+C`, move the playhead, `Ctrl+V`). Select
  the channels and press `Shift+E` > Make Cyclic (F-Curve), or add the Cycles modifier. Copy modifiers to other channels
  with Copy F-Modifiers and Paste. It repeats forever and updates when you edit keys.
- Detail and the pop-at-the-seam fix: see [cycles-and-locomotion.md](cycles-and-locomotion.md).

## Motion paths and arc checks

- Pose Mode, select a bone, Pose > Motion Paths > Calculate (Blender 4.2+: Object > Animation > Motion Paths, or the
  Animation tab panel). Play and compare. FK gives a smooth half circle. IK gives a straight line.
- Fix an IK path by adjusting a middle key (frame 15 of 30) until the path bends. Clean arcs read as natural.

## Timing charts for 2D

- Next to each key drawing, draw a tick diagram for the in-betweens. Even ticks are linear. Bunched ticks at one end are
  an ease. Mark a loop by adding the repeated first drawing as the last frame.
- The Graph Editor curve is the same chart drawn as a line.
- Hold the squash contact frame for 2 frames. Raise the duplicated last frame slightly so a loop decelerates into the
  first frame.

## Frame rate and motion blur

- Output Properties > Format > Frame Rate. 24 fps with motion blur for film. 30 fps for games or when you skip blur. 60 fps
  plays smoother but costs renders. Viewport playback never shows motion blur.
- 2D: use 24 fps on twos. Add smear frames or blur on fast moves for the same reason.
- Preview with View > Viewport Render Animation (preview range, no blur). Final: Render > Render Animation (`Ctrl+F12`).
  Use a PNG sequence so a crash keeps finished frames.
