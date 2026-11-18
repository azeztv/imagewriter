#!/usr/bin/env bash
# Behaviour test for scripts/check_sculpt.py: a clean fixture passes (exit 0), a broken one fails (exit 1)
# with the scale and loose-vertex checks named, and both write the report and the two sheets.
set -u
BLENDER="${BLENDER:-C:/Program Files/Blender Foundation/Blender 5.3/blender.exe}"
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$(mktemp -d)"
status=0
"$BLENDER" -b --python "$HERE/make_fixture.py" -- "$WORK/clean.blend" > /dev/null 2>&1
"$BLENDER" -b --python "$HERE/make_fixture.py" -- "$WORK/broken.blend" --broken > /dev/null 2>&1
"$BLENDER" -b "$WORK/clean.blend" --python "$HERE/../scripts/check_sculpt.py" -- --out "$WORK/clean" > "$WORK/clean.log" 2>&1
clean_code=$?
"$BLENDER" -b "$WORK/broken.blend" --python "$HERE/../scripts/check_sculpt.py" -- --out "$WORK/broken" > "$WORK/broken.log" 2>&1
broken_code=$?
[ "$clean_code" = 0 ] || { echo "FAIL clean fixture exit $clean_code"; status=1; }
[ "$broken_code" = 1 ] || { echo "FAIL broken fixture exit $broken_code"; status=1; }
grep -q "FAIL  scale applied" "$WORK/broken.log" || { echo "FAIL scale check not reported"; status=1; }
grep -q "FAIL  no loose vertices" "$WORK/broken.log" || { echo "FAIL loose check not reported"; status=1; }
for file in clean/sculpt_report.json clean/silhouette.png clean/matcap.png; do
  [ -s "$WORK/$file" ] || { echo "FAIL missing $file"; status=1; }
done
[ "$status" = 0 ] && echo "ok: check_sculpt behaves"
rm -rf "$WORK"
exit $status
