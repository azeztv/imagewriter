# Seamless strip of painted frames

A strip of N frames that each stand alone on X yet flow into each other when swiped.

## Layout

- Frame size is the platform's frame (X carousel: 3:4). The strip is N frames wide.
- Around each cut, a transition band (about 300 px at 4096 px tall) where the two scenes meet along a wandering
  boundary. Outside the band each frame shows only its own picture.
- A thin ragged band of bare paper along the top and bottom of every frame ties the set together.

## Painting

1. Build each frame's target in strip coordinates: its own crop, widened by the band and some context (about 420 px)
   into both neighbours.
2. Paint each frame in its own window with the same flow field defined in strip coordinates (curl-noise eddies), so
   strokes near a cut follow the same swirl in both windows. Seed every random choice with a hash that is stable
   across processes (zlib.crc32), not Python's `hash()`.
3. Run windows as parallel processes at below-normal priority.

## Joining

1. For each cut, take the two paintings' columns inside the band.
2. Find the path, one column per row moving at most one column a row, where the two paintings differ least (dynamic
   programming over the absolute difference).
3. Take every pixel from one painting or the other along that path. Never blend pixels.
4. Cut the strip at exact frame-width boundaries, reload the saved frames and check they rejoin into the strip pixel
   for pixel.

## Measuring

- Colour step across each cut against a typical column step inside a frame: equal means no visible seam.
- Hue per frame (chroma-weighted Lab mean) to order frames and to check the colour journey moves one way.
- SSIM of painting against target on Lab L, a and b to catch frames that lost their structure.
