# PCB work scope

Ruslan wants component placement only. Copper routing is done by Ruslan in KiCad.

- Preserve the schematic, net assignments, footprint pad geometry, board outline, panel
  coordinates and mounting-hole locations when changing placement.
- Deliver an unrouted PCB: no tracks, vias or copper zones. Footprint pads and the
  net-tie's internal copper remain part of their footprints.
- Do not run an autorouter or generate ground pours, escape tracks or stitching vias.
- Do not overwrite a board containing manual routing. Create a separate placement
  output when updating placement after routing has started.
- Check footprint/schematic parity and placement clearances. Unrouted connections
  are expected; do not route them to make a DRC report clean.

The channel-strip placement generator is `tools/place_strip.py`; the placement-only
build command is `tools/build_strip_pcb.sh`. See `CLAUDE.md` for project details.
