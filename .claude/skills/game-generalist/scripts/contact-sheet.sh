#!/usr/bin/env bash
set -euo pipefail

# Build a labelled 1-fps contact sheet from a rendered 3D video for anti-slop QA review.
# Usage: bash contact-sheet.sh <input.mp4> <output.png> [fps=1] [cols=6]

USAGE="Usage: contact-sheet.sh <input.mp4> <output.png> [fps=1] [cols=6]"

if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
  echo "$USAGE"
  exit 0
fi

if [ "$#" -lt 2 ]; then
  echo "$USAGE" >&2
  exit 2
fi

VIDEO="$1"
OUT="$2"
FPS="${3:-1}"
COLS="${4:-6}"

DUR=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$VIDEO")
FRAMES=$(awk -v d="$DUR" -v f="$FPS" 'BEGIN { n = int(d * f + 0.999); print (n < 1 ? 1 : n) }')
ROWS=$(awk -v n="$FRAMES" -v c="$COLS" 'BEGIN { r = int((n + c - 1) / c); print (r < 1 ? 1 : r) }')

mkdir -p "$(dirname "$OUT")"

ffmpeg -y -hide_banner -loglevel error \
  -i "$VIDEO" \
  -vf "fps=${FPS},scale=360:-2,drawtext=text='%{pts\:hms}':x=8:y=8:fontsize=18:fontcolor=white:box=1:boxcolor=black@0.65,tile=${COLS}x${ROWS}:padding=4:margin=4:color=0x111111" \
  -frames:v 1 \
  "$OUT"

echo "Wrote contact sheet ($FRAMES frames, ${COLS}x${ROWS}) -> $OUT"
