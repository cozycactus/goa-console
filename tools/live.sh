#!/bin/bash
# Regenerate the pilot sheet, check it, export SVG for the live viewer (render/live, served by .claude/launch.json)
set -eo pipefail
cd "$(dirname "$0")/.."
KC=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
L=render/live; mkdir -p $L
PILOT=$L/pilot.kicad_sch .venv/bin/python tools/gen.py /tmp/strip_rows.kicad_sch > $L/gen.log 2>&1 || { tail -3 $L/gen.log; echo "pilot.svg|$(date +%H:%M:%S)|GENERATOR ERROR: $(tail -1 $L/gen.log)" > $L/stamp.txt; exit 1; }
$KC sch export netlist -o $L/pilot.net $L/pilot.kicad_sch >/dev/null 2>&1
V=$(.venv/bin/python tools/verify.py $L/pilot.net $L/pilot_intended.json | head -1)
$KC sch erc --severity-error -o $L/erc.rpt $L/pilot.kicad_sch >/dev/null 2>&1 || true
# the pilot sheet has no power block: its op-amp power units and PWR_FLAGs are on the full schematic
E="$(grep -c "^\[" $L/erc.rpt) items, $(grep "^\[" $L/erc.rpt | grep -vc "missing_power_pin\|power_pin_not_driven" || true) beyond the pilot's missing power block"
$KC sch export svg -o $L $L/pilot.kicad_sch >/dev/null 2>&1
echo "pilot.svg|$(date +%H:%M:%S)|${1:-} · $V · ERC: $E" > $L/stamp.txt
echo "$V | ERC $E"
