#!/bin/bash
# Live view of a drawn schematic: regenerate, check (verify, ERC) and export SVG for the page served by
# .claude/launch.json ("schematic-live", render/live). usage: tools/live.sh [strip|group|master] ["note"]
set -eo pipefail
cd "$(dirname "$0")/.."
KC=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
L=render/live; mkdir -p $L
B=${1:-strip}; NOTE=${2:-}
case $B in
  strip)  SCH=$L/pilot.kicad_sch; CMD=(env PILOT=$SCH .venv/bin/python tools/gen.py /tmp/strip_rows.kicad_sch) ;;
  group)  SCH=boards/group/group.kicad_sch;    CMD=(.venv/bin/python tools/gen_group.py boards/group/group.kicad_sch) ;;
  master) SCH=boards/master/master.kicad_sch;   CMD=(.venv/bin/python tools/gen_master.py boards/master/master.kicad_sch) ;;
  *) echo "usage: $0 [strip|group|master] [note]"; exit 2 ;;
esac
NAME=$(basename $SCH .kicad_sch); DIR=$(dirname $SCH)
"${CMD[@]}" > $L/gen.log 2>&1 || { tail -3 $L/gen.log; echo "pilot.svg|$(date +%H:%M:%S)|$B GENERATOR ERROR: $(tail -1 $L/gen.log)" > $L/stamp.txt; exit 1; }
$KC sch export netlist -o $L/live.net $SCH >/dev/null 2>&1
V=$(.venv/bin/python tools/verify.py $L/live.net $DIR/${NAME}_intended.json | head -1 || true)
$KC sch erc --severity-all -o $L/erc.rpt $SCH >/dev/null 2>&1 || true
E="$(grep -c "^\[" $L/erc.rpt || true) items"
[ $B = strip ] && E="$E (pilot sheet: no power block)"
$KC sch export svg -o $L $SCH >/dev/null 2>&1
[ $NAME != pilot ] && mv -f $L/$NAME.svg $L/pilot.svg
echo "pilot.svg|$(date +%H:%M:%S)|$B: $NOTE · $V · ERC: $E" > $L/stamp.txt
echo "$V | ERC $E"
