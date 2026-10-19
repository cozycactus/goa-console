#!/bin/bash
# Rebuild channel_strip.kicad_pcb from the netlist: placement, then routing block by block, with the
# ground pours re-made and DRC run after each block. Overwrites any hand edits to the board.
# usage: tools/build_strip_pcb.sh [last-block]      (blocks: ribbon rails audio logic; default: all)
set -euo pipefail
cd "$(dirname "$0")/.."
KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3
KC=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
PCB=channel_strip.kicad_pcb
LAST=${1:-logic}
quiet() { grep -v "assert\|memory leak\|Debug: " || true; }

declare -a ORDER=(ribbon rails audio logic)
RIBBON="MIXR MIXL SUB1 SUB2 SUB3 SUB4 AUX1 AUX2 AUX3 AUX4 AUX5 AUX6 PFL PFLDET GCANCEL +VBUS -VBUS"
RAILS="GNDD +VA -VA +VL -VL"      # GNDD: LGND tracks joining the logic parts and the LGND islands to NT1
# audio path, shortest first so local connections take their natural paths before the long runs
AUDIO="RET BUF1 RET_RAW SEND IN_R IN_T U1A_P U1A_N RECV WIPER VCAIN FPIN U2A_N FPOST PANWL PANWR PBL PBR \
RT_R26 RT_R27 RT_R28 RT_R29 RT_R30 RT_R31 PFL_S M1 M2 MUTEOUT SRC12 SRC34 SRC56 PANL PANR \
A1W A2W A3W A4W A5W A6W POST PRE"
LOGIC="OL_A OL_K PKA PK VREF PFL_LA PFL_ON MSW MUTE_LA MUTE_ON MGATE VCA_CTRL"

"$KPY" tools/place_strip.py channel_strip.net "$PCB" 2>&1 | quiet
for blk in "${ORDER[@]}"; do
  case $blk in ribbon) NETS=$RIBBON;; rails) NETS=$RAILS;; audio) NETS=$AUDIO;; logic) NETS=$LOGIC;; esac
  echo "=== block: $blk"
  "$KPY" tools/pour_strip.py "$PCB" --strip 2>&1 | quiet
  "$KPY" tools/route_strip.py "$PCB" $NETS 2>&1 | quiet
  "$KPY" tools/pour_strip.py "$PCB" 2>&1 | quiet
  R=$(mktemp -t drc)
  "$KC" pcb drc --schematic-parity --severity-all -o "$R" "$PCB" 2>&1 | grep Found || true
  grep "^\[" "$R" | sed 's/\].*/]/' | sort | uniq -c | sort -rn | grep -v "silk_\|unconnected_items" || true
  for n in $NETS; do
    c=$(grep -A3 "unconnected_items" "$R" | grep -c -F -e "[$n]" -e "[/$n]" || true)
    [ "$c" != "0" ] && echo "   still unconnected: $n ($c)"
  done
  rm -f "$R"
  [ "$blk" = "$LAST" ] && break
done
