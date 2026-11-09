# goa-console — tooling

Moved out of `CLAUDE.md` on 2026-10-28 (`docs/reviews/project_review.md` RV13), text unchanged: the verify loop, the placer, the footprints and 3D models, the routing rules, the post-route checker, check_all, the fab outputs and the escape plan.
The live rules, the current state and the one-line decisions are in `CLAUDE.md`; this file is the detail behind them.

- Placement engine `tools/placer.py` (`place(net, out, layout)`: fixed parts, zone packer, near-placement,
  silk labels and references; optional per-zone gap, `silk_text_off`, `keepout`, `moves`: parts moved to fixed spots after packing, with a collision guard that also checks a THT part's leads; `turns`: parts turned in place, same guard; `layers` / `rails`: 4-layer boards and the rail corridor) plus the shared 8 HP frame (`pot`, `sw`,
  `led`, `jack`, `FADER`, `BUS`, `SPADE`); place_strip / place_group / place_master / place_jig / place_psu are layouts.
  `attach=True` (strip, group, master, jig; 2026-10-23): parts follow the IC pin they belong to, from the netlist's pin
  types: decouplers at their supply pin, input / feedback / summing parts at the input pin, output networks at the
  output pin, chains next to their partner; each IC keeps a ring sized from its parts' area, parts wait for an IC placed
  later, staged placement (connectors and free THT parts, ICs + decouplers + inputs + THT, outputs, rest). Every run
  prints a report: decoupler cap pad to supply pin (limit 5 mm) and, per high-Z input (not driven by an output directly
  or through a coupling cap, not a connector line, not a reference shared by 3+ inputs), the farthest R/C/L/D/FB/JP pad
  (limit 6 mm). Without attach (PSU, jack boards) placement is unchanged.
- 3D model: `tools/export_3d.py` (KiCad Python) exports each module's placed boards to `render/strip.json`,
  `group.json`, `master.json` (positions, panel features, which footprints have a KiCad 3D model, pins of the rest);
  `tools/console_3d.py` (Blender 5.2, headless:
  `Blender -b --factory-startup --python tools/console_3d.py -- render [norender]`) builds `render/goa_console.blend`:
  every board is KiCad's own GLB export (`kicad-cli pcb export glb`: KiCad's STEP models, pads, mask, silk; cached in
  render/glb/, re-exported when a .kicad_pcb is newer); the parts KiCad has no model for come from `tools/models3d`;
  standoffs, M4 stud, LED spacers/lenses are generic; IDC sockets crimped on the ribbons (34-way motherloom through
  every module's bus header, folded jack-board links), the supply cable to the master's J1; the panel plate has real
  cut-outs (holes, fader slots, D-size XLR) and Delta-style print (`panel_print`, rules in `docs/build/panel_print.md`: cream ink,
  bold name above each pot, HI/LO MID bracket, 11 square dots with numerals that dodge neighbours, "dB" between the end
  numerals, FREQ scales from sim/review/eqmid/measure.py (EQM1; sim/mid_tuning.py is the 2026-10-22 study), gain scale from the gain-stage law, fader dB scale from a two-slope A
  law + 9.9 dB post-amp (approximate until the fader's law is measured), section rules, meter outlines); views
  panel_strip.png / panel_strip_top.png (gain to LF) / panel_master.png; `export_3d.py` takes the board files as
  arguments (its docstring), one module per call; the panel layer is a separate collection per module (hide it to see the
  boards). 24 strips + 4 groups + master as instanced collections, 9° tub, ten PNG views incl. internals.png.
  `tools/fly_render.py` renders the fly-through camera of the .blend (`-- preview | final [a-b]`, its docstring).
  .blend, PNGs and GLBs are gitignored.
- `tools/models3d/` — part models from the manufacturers' drawings for the footprints KiCad has no model for (Alpha
  RD901F/RD902F + knob, ALPS RK09L1240015 (pan), C&K PVA2 + PV cap, Neutrik NJ6FD-V and NC3MAV, Bourns PTB0143/0144 + fader knob, Keystone
  1287-ST, Bourns MF-RX160/72 / 185/72 / 250/72, the 3-lead bicolour LED): one module per part (`build()` on the board up through the panel, `panel()` on the
  panel top, `pins()`), shared geometry (`geom.py`), Blender adapter (`blend.py`), cables (`cable.py`).
  `python3 tools/models3d/check.py --wrl`: leads vs footprint pads, body vs courtyard, and writes
  `goa-console.3dshapes/<footprint>.wrl` (KiCad's 3D viewer) + `.step` (KiCad's GLB/STEP export). The placer points
  a footprint at that model when it exists; tools/footprints.py writes the model line. Per-part review renders:
  `Blender -b --factory-startup --python tools/models3d/preview.py -- render/parts [module]`.
- `tools/verify.py` — checks KiCad's exported netlist against `boards/channel_strip/channel_strip_intended.json`.
  Regenerate + verify loop:
  ```
  KC=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli   # macOS, KiCad 10.0.7
  .venv/bin/python tools/gen.py boards/channel_strip/channel_strip.kicad_sch
  $KC sch export netlist -o boards/channel_strip/channel_strip.net boards/channel_strip/channel_strip.kicad_sch
  .venv/bin/python tools/verify.py boards/channel_strip/channel_strip.net boards/channel_strip/channel_strip_intended.json
  python3 tools/check_fp.py boards/channel_strip/channel_strip.net                # pins vs footprint pads
  $KC sch erc --severity-all boards/channel_strip/channel_strip.kicad_sch
  $KC sch export pdf -o pdf/channel_strip.pdf boards/channel_strip/channel_strip.kicad_sch
  ```
  python3 tools/sim_netlist.py boards/channel_strip/channel_strip.net boards/jack_board/jack_board.net   # both netlists joined by the ribbon: 45 checks
  python3 tools/sim_console.py     # the whole console from the netlists: 24 strips + 4 groups + master + ribbon, 45 checks
  python3 tools/check_bus.py boards/channel_strip/channel_strip.net boards/group/group.net boards/master/master.net boards/jig_master_stub/jig_master_stub.net   # the motherloom pin by pin
  BOM (every board; quoted fields, because some MPNs contain commas; DNP column): `$KC sch export bom -o bom/channel_strip_BOM.csv --fields '${QUANTITY},Value,Footprint,MPN,${DNP},Reference' --labels 'Qty,Value,Footprint,MPN,DNP,References' --group-by 'Value,Footprint,MPN,${DNP}' --ref-delimiter ' ' --ref-range-delimiter '' boards/channel_strip/channel_strip.kicad_sch`
  `.venv/` (gitignored) holds kiutils 1.4.8. gen.py finds the symbol libs at the Linux or macOS
  default path, or `$KICAD_SYMBOL_DIR`. verify.py parses both KiCad 7 and KiCad 8+ netlists
  and exits non-zero on any mismatch.
- `goa-console.pretty/` + `fp-lib-table` — project footprints (PTB0143/PTB0144 faders, Keystone 1287-ST tab, MF-RX160/72 / 185/72 / 250/72 PTCs, LED_D3.0mm-3_P2.00mm),
  GENERATED by `tools/footprints.py` from the datasheet dimensions in its comments.
- Routing rules (2026-10-27): `tools/netrules.py` (KiCad Python) writes net classes (Ground, Chassis, Power, LogicSupply,
  Bus, Entry, HighZ, Switching, Default; exact net names from the placed board) into each project and custom rules into
  `X.kicad_dru` (strip, group, master, jig boards, jack boards): HighZ / Entry / Bus copper 1 mm from Switching and 0.5
  from logic supplies, their tracks 0.3 from other copper, GNDD 0.5 from GNDA, CHASSIS 0.5, HighZ <= 60 mm, Power /
  Ground widths. `tools/netrules_test.py` proves every rule fires (KiCad silently drops a rule it can't evaluate, e.g.
  `!(...)`; the later rule in the file wins for the same constraint). The 4-layer boards add five: no tracks on In1.Cu, no
  zone there but ground, no HighZ / Entry / Bus tracks on In2.Cu, rails / GNDD on In2 only inside RAILS, no HighZ / Entry
  / Bus on B.Cu over RAILS (13 rules on the strip, all fire). WingFeed class (nets through a wing PTC: master ±VBUS / ±VBUS_L / _R, the jig
  stub's feeds): tracks >= 1.5 mm, 2.0 preferred. PSU (2026-10-27): HighCurrent class (POS_IN / NEG_IN / POS_LC / NEG_LC /
  +V / -V / 0V, the 4 A paths) >= 3 mm, 4 preferred (psu_spec.md §7), EARTH as Chassis; 15 rules in the test, all fire;
  routing notes in routing_guide.md (Kelvin ADJ dividers, crowbar sense at J3, 0V star). Re-run netrules.py after any
  re-placement or netlist change. Generators that copy boards/master/master.kicad_pro keep each project's net settings (`schgen.keep_net_settings`).
- `tools/route_check.py` (2026-10-27, KiCad Python) — post-route checker for what DRC can't see:
  - return vias: a GNDA via within 1 mm of each signal via, 2 mm at most on HighZ / Entry / Bus;
  - reference: filled GNDA under every sensitive track on its reference layer (In1 under F.Cu, In2 under B.Cu; on 2
    layers the other outer layer), gaps with length and position;
  - high-Z length and vias, decoupler copper path and ground via, stability caps' vias to their pin, no GNDD fill.

  It fills the zones in memory. `tools/route_check_test.py` routes a known fault and a known-good case for each check
  on a scratch strip (8 / 8 found, 0 false alarms). The test showed a via beside a SOIC pin can't get a GNDA via
  within 1 mm (about 1.4 mm), hence the 2 mm limit.
- `python3 tools/check_all.py [--full]` (2026-10-27) — every project check in one run, tracked files untouched (netlists,
  reports, panel outputs in a temp folder): per board the committed `.net` against the fresh export (same pins and
  nets: sim_console, check_links and the ol sims read the committed one; RV11.1), netlist vs intended, pins vs footprints
  (both directions since RV11.4), ERC, parity DRC (KNOWN items of fab_out.py aside, one footprint per item since RV11.3),
  footprint links, route_check; then each project file's top-level sheet (its own schematic, `schgen.own_sheet`), `check_bus.py` (the motherloom pin by pin on strip / group / master / jig, RV11.2),
  sim_netlist, sim_console, netrules_test, route_check_test, panel_fab's checks; `--full` adds `sim/review/gaps/ol.py`
  (a values check: its wiring is the pre-CS1 one-tap detector, RV11.8) and `sim/review/cs1/ol_multi.py --quick` (the five
  taps from the netlist). 71 checks (2026-10-28). Exit 1 on any FAIL. Run it after any generator,
  placement or rule change. Doesn't regenerate (run the generators first) or run the TI-model stability decks. On Linux
  (KiCad 10.0.7 from the KiCad PPA, `KC=kicad-cli KPY=python3`, a `.venv` with kiutils) everything but panel_fab runs
  (it loads Arial Narrow from the macOS font path).
- Fab limits and outputs (2026-10-27):
  - **Board rules:** `tools/netrules.py` writes JLCPCB-based limits (`FAB`) into every project, the PSU's too.
    JLCPCB's capabilities page was read 2026-10-27: text >= 1.0 mm / 0.15 mm lines, plated hole to track 0.28, pad
    holes 0.45 apart, silk 0.15 from pads, pad to pad 0.15.
  - **Silk:** `placer.py` writes references at 1.0 / 0.15 mm (was 0.8 / 0.12) within 7 mm. Hidden: master R139, R142,
    R158, R212; none elsewhere. The group's silk labels are 1.0 mm.
  - **Re-placed:** every board, no part moved; DRC unchanged except the PSU's TO-220 silk at the edge (20 items, by
    design).
  - **`python3 tools/fab_out.py BOARD`:**
    - **Checks:** DRC (zones refilled, parity) and `route_check.py`. It refuses on anything but the footprint-internal
      items in `KNOWN`, and a known item must name only footprints.
    - **Writes `fab/BOARD/` (gitignored):** Gerbers with all copper layers, Excellon PTH / NPTH, a zip, the position
      file + JLCPCB CPL, BOM, DRC JSON.
    - **Tried:** on the strip (4L: L1 / L2 GND / L3 GND2 / L4), jack board and PSU with `--allow-unrouted`. The jig
      load board is refused for its 106 unrouted connections.
- `docs/build/escape_plan.md` (2026-10-27) — layer plan for the 4-layer main boards from `tools/escape_plan.py` (KiCad Python):
  HighZ / Entry / Bus on F.Cu, Switching on B.Cu (both planes between them), the rest greedily to clear crossings, once
  per board. `docs/escape/<board>_layers.csv` per net; the three densest 30 mm windows per board as SVGs. Strip worst:
  y 121-151, the column between U12 / U13 (RV13, RV15, SW12, CN3).
- `tools/freespot.py` (KiCad Python, 2026-10-29) — free spots for a part made last, by the placer's guard rules
  (same-side courtyards, THT pads on both sides, the part's own leads against everything), the footprint loaded and
  set up as placer.py does it; finds KiCad's library on Linux and macOS. `tools/placediff.py` — footprints added,
  removed, moved, turned or flipped between two versions of a board (default: against git HEAD); exit 1 on any
  difference. Together they are the "made last, placed by moves_only, check that only the new parts changed" rule.

