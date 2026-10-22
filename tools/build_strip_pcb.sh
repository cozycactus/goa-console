#!/bin/bash
# Build component placement only. No routing, vias or copper pours.
# usage: tools/build_strip_pcb.sh [output.kicad_pcb]
# Overwrites existing unrouted placement; refuses to overwrite a board containing routing/zones.
set -euo pipefail
cd "$(dirname "$0")/.."
KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3
if [ "$#" -gt 1 ]; then
  echo "usage: $0 [output.kicad_pcb]" >&2
  exit 2
fi
PCB=${1:-channel_strip_v4.kicad_pcb}  # v4.0 placement; channel_strip.kicad_pcb is the old v3.1 board
case "$PCB" in
  *.kicad_pcb) ;;
  *) echo "Output must end in .kicad_pcb; routing blocks are no longer supported." >&2; exit 2 ;;
esac
"$KPY" tools/place_strip.py channel_strip.net "$PCB"
