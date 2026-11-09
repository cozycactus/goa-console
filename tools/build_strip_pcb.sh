#!/bin/bash
# Build component placement only. No routing, vias or copper pours.
# usage: tools/build_strip_pcb.sh [main.kicad_pcb [jack.kicad_pcb]]
# Defaults: boards/channel_strip/channel_strip.kicad_pcb (main board, the strip project's own board, so KiCad links it to the schematic) and
# boards/jack_board/jack_board.kicad_pcb (jack board). The old v3.1 board is archive/channel_strip_v3.1.kicad_pcb.
# Overwrites existing unrouted placement; refuses to overwrite a board containing routing/zones.
set -euo pipefail
cd "$(dirname "$0")/.."
KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3
if [ "$#" -gt 2 ]; then
  echo "usage: $0 [main.kicad_pcb [jack.kicad_pcb]]" >&2
  exit 2
fi
MAIN=${1:-boards/channel_strip/channel_strip.kicad_pcb}
JACK=${2:-boards/jack_board/jack_board.kicad_pcb}
for PCB in "$MAIN" "$JACK"; do
  case "$PCB" in
    *.kicad_pcb) ;;
    *) echo "Output must end in .kicad_pcb; routing blocks are no longer supported." >&2; exit 2 ;;
  esac
done
"$KPY" tools/place_strip.py boards/channel_strip/channel_strip.net "$MAIN"
"$KPY" tools/place_strip.py boards/jack_board/jack_board.net "$JACK"
