# goa-console — file map and change narrative

Moved out of `CLAUDE.md` on 2026-10-28 (`docs/reviews/project_review.md` RV13), text unchanged: every file of the project, what generates it, what it decided and when, in the order the "Files" section of CLAUDE.md grew.
The live rules and the current state are in `CLAUDE.md`, the one-line decisions in `docs/decisions_summary.md` (since 2026-11-11); this file is the detail behind them.
Since 2026-11-09 the proposals, reviews, studies and build notes are in `docs/{proposals,reviews,studies,build}/`, the BOM exports and order lists in `bom/`, the schematic PDFs in `pdf/`; the narrative below is otherwise as it was written.
The same day each KiCad project moved into `boards/<name>/`: where this file names `channel_strip.kicad_pcb`, `master.net`, `group_intended.json` and the like, read `boards/<name>/` in front.

## Proposals and reviews (ID, document, sign-off, where it landed)

| IDs | Document | Signed off | Applied in | Patch (archive/patches/) |
|---|---|---|---|---|
| T1-T11 | `docs/reviews/strip_parts_review.md` | 2026-10-23 | strip v4.1 | — |
| S1-S8 | `docs/reviews/master_parts_review.md` | 2026-10-23 | master v0.7 | — |
| MG1-MG20 | `docs/reviews/master_group_review.md` | 2026-10-24 | master v0.8, group rev 0.2 | — |
| F1-F4 | `docs/proposals/film_np_proposal.md` | 2026-10-24 | strip v4.2 | film_np_proposal.patch |
| H1-H4 | `docs/proposals/hpf_proposal.md` | 2026-10-24 | strip v4.3, master v0.9 | hpf_proposal.patch |
| G1-G3, G2b / G3b | `docs/studies/ground_study.md` | 2026-10-25 | strip v4.4, master v0.10 | — |
| K1, K3 | `docs/proposals/gaps_proposal.md` | 2026-10-25 | strip v4.5 | — |
| R1-R5, Q1 | `docs/reviews/design_review.md` | 2026-10-25 | strip v4.6, master v0.11 | — |
| W1 / W2 | `docs/proposals/wing_power_proposal.md` | 2026-10-25 | every bus header, master F1 / F3 | — |
| S1 (sourcing) | `docs/build/sourcing.md` | 2026-10-25 | BOMs | — |
| KN1-KN3, KC1 / KC2 | `docs/proposals/knob_proposal.md` | 2026-10-25 | panels, 3D | — |
| FR1-FR3 | `docs/proposals/frame_proposal.md` | 2026-10-25 | `frame/` | — |
| MET1, RET1 | `docs/reviews/feature_gaps.md` | 2026-10-26 | strip v4.7, group v0.12 | — |
| PAN1 | `docs/proposals/pan_buffer_proposal.md` | 2026-10-26 | strip v4.8 | pan_buffer_proposal.patch |
| E1-E5, E8 | `docs/studies/emc_placement_study.md` | 2026-10-26 | placement | — |
| E6 | `docs/studies/emc_placement_study.md` | 2026-10-27 | strip v4.9 | — |
| P1 / P2, P4 | `docs/reviews/met1_ret1_review.md` | 2026-10-27 | strip v4.9 | — |
| PC1-PC3 | `docs/proposals/psu_case_proposal.md` | 2026-10-26 | `psu_case/` | — |
| TH1-TH3 | `docs/studies/thermal_study.md` | 2026-10-26 | tub | — |
| TB1-TB4 | `docs/proposals/tub_proposal.md` | 2026-10-26 | `tub/` | — |
| E9 / E9b | `docs/proposals/stab_caps_proposal.md` | 2026-10-27 | placement | stab_caps_proposal.patch (re-implemented as MOVES), stab_caps_e9b.patch |
| E10 | `docs/proposals/input_nets_proposal.md` | 2026-10-27 | placement | input_nets_proposal.patch |
| E11 | `docs/proposals/decouplers_proposal.md` | 2026-10-27 | placement | decouplers_proposal.patch |
| 2L / 4L | `docs/studies/layer_study.md` | 2026-10-27 | 4-layer mains | — |
| turns | `docs/proposals/untangle_proposal.md` | 2026-10-27 | placement | — |
| CS1 | `docs/proposals/cs1_proposal.md` | 2026-10-27 | strip v5.0 | cs1_proposal.patch |
| CS10 | `docs/proposals/cs10_proposal.md` | 2026-10-27 | strip v5.1, group | cs10_proposal.patch |
| CS4 / CS4b / CS4c | `docs/proposals/cs4_proposal.md`, `docs/proposals/cs4b_proposal.md`, `docs/proposals/cs4c_proposal.md` | 2026-10-27 | strip v5.2, group, master | cs4*, cs4b*, cs4c* |
| CS6 | `docs/proposals/cs6_proposal.md` | 2026-10-27 | strip v5.3, group | cs6_proposal.patch |
| CS11 / CS11b | `docs/proposals/cs11_proposal.md`, `docs/proposals/cs11b_proposal.md` | 2026-10-27 | jig spec v0.9, BOM notes | cs11*, cs11b* |
| CS2 / CS2b | `docs/proposals/cs2_proposal.md`, `docs/proposals/cs2b_proposal.md` | 2026-10-27 / 28 | strip v5.4, group | cs2*, cs2b* |
| CS7 | `docs/proposals/cs7_proposal.md` | 2026-10-28 | master v0.12 | cs7_proposal.patch |
| EQM1 | `docs/proposals/eqmid_proposal.md` | 2026-10-28 | strip v5.5 | eqmid_proposal.patch |
| RV1-RV14 | `docs/reviews/project_review.md` | 2026-10-28 | tools, docs, PSU, jig spec v0.10, cleanup | — |
| RV3 / RV4 / RV7-RV9 | `docs/proposals/clicks_proposal.md` | 2026-10-28 | strip v5.6, master v0.13, group | clicks_proposal.patch |
| D1-D24 | `docs/reviews/delta_crosscheck.md` | 2026-10-28 | master (D13 JP3-JP7), documentation | — |
| CS3 / CS5 / CS8 / CS9 | `docs/studies/console_survey.md` | CS3 / CS5 checked, CS8 / CS9 open (jig) | — | — |
| N1 | `docs/proposals/strip_noise_proposal.md` | open (the jig A/B decides) | — | — |
| TF1 | `docs/proposals/thin_film_proposal.md` | 2026-10-29 | order lists (sourcing rule) | thin_film_proposal.patch |
| RV3b / RV9b | `docs/proposals/clicks_followup_proposal.md` | 2026-10-29 | strip v5.7, master v0.14 | — |
| FE1 | `docs/proposals/film_eol_proposal.md` | 2026-10-29 | order code only (same footprint); FE2 not taken | film_eol_proposal.patch |
| SS1-SS3 | `docs/proposals/second_source_proposal.md` | 2026-11-03 | order codes for stage A's backordered parts; value label MBR140SFT1G; H3 keys on phase 1's strips | second_source_proposal.patch |
| SR1-SR7 | `docs/reviews/schematic_readability_review.md` | SR1's PSU sheet 2026-11-12; the rest open | `psu.kicad_sch` (drawing only, `docs/verification_log.md`) | — |

## Files

- `docs/clipping/` (2026-10-29) — clipping waveforms of the Delta's op-amps (TL072 classic with its input-stage phase
  reversal, TI's 1989 macro, the TL07xH die) against ours (OPA1612, OPA1656): follower and inverter on ±17 V at
  14 / 16 / 18 V peak, `sim/review/clipping/clip.py` + `tl072_classic.lib`; TI models via `$TI_MODELS`, not in the repo.
  Result: same hard clip within 1 dB at every stage output; the classic TL072 reverses to the positive rail in
  followers 1.5 V before its output would clip; the OPA1656 follower (U16) flat-tops at +14.75 V, its input range.
- `channel_strip.kicad_sch` / `.kicad_pro` — channel strip schematic v5.6 (KiCad 7 file format, opens in KiCad 10).
  HIERARCHICAL on A4 since 2026-10-25, like the master: a root sheet plus 17 pages in `strip_sheets/` (the group: 12
  pages in `group_sheets/`); strip_draw blocks too big for a page are lists of pieces (KHN per band, routing per
  assign key, power in rows), packed apart on pages and drawn in turn on a flat sheet (PILOT).
  GENERATED by `tools/gen.py` — edit the generator (netlist is in the `P(...)` calls), then regenerate.
  DRAWN since 2026-10-24: every block is a real schematic (stages laid out as on the Delta sheets, wires, junctions,
  labels only where a net leaves its drawing), one ~1001 x 759 mm sheet in signal-order columns. The drawings are
  `tools/strip_draw.py` (one function per block, keyed by title; helpers `inv_stage`, `svf_core`, `follower`,
  `led_chain`), the drawing layer `tools/schdraw.py` (placement with rotation / mirror on the 2.54 grid, polylines,
  auto junctions; it refuses a wire that joins two nets before anything is written). Nets inside a drawing are
  unlabelled, so KiCad names them `Net-(...)`: `tools/netnames.py` gives them their intended names back by exact pin
  set (verify.py, sim_netlist.py, sim_console.py, sim/review/strip/stripdeck.py, place_group.py, place_master.py, the
  placer's report). The group and master are drawn too (2026-10-24): every master_lib circuit function registers a
  drawing fragment of its own parts (`tools/frags.py`: inverting / difference / non-inverting stages, followers, insert,
  DRV134, relay, routing, AFL, power units, chains, pots; two-pin parts turned by their nets), `schgen.flow()` lays a
  block's fragments out in rows and puts any part no fragment drew in labelled rows under them (`build(flowed=True)`),
  so a new circuit can't be lost, only undrawn. Nothing on the group or master is left in rows (2026-10-24): the master's
  comparator logic, PFL switcher, meter detectors and LED strings (each comparator on its LED's anode, the BCP53 source on
  top), spares, +5VL, DG413 supply, power entry and PWR_FLAGs are drawn; headers (`frags.header`) put every pin on a stub
  to a horizontal label and join runs of one net (the even GNDA pins) to one symbol. The jig's load board and the jack
  boards keep the row layout; the jig's master stub (2026-11-10, `tools/gen_jig.py`) and the PSU (2026-11-12,
  `draw_sheet` in `tools/gen_psu.py`: two identical rail rows, each crowbar on a bus under its rail, reference / value
  places set with `Drawing.fld`) are one wired drawing each. GNDM and PHONESGND are power symbols in
  `goa-console.kicad_sym` (GNDA's triangle with the name shown); `+V`, `0V` and `-V` there are the PSU's rails as power
  symbols local to the sheet (`(power local)`: the net keeps its `/`, as a label's does, so the board's net names
  stand; KiCad marks such a symbol with a small sign; -V carries the drawing's own PWR_FLAG, `Drawing.flag`).
  `schgen.flow()` measures each fragment (label texts included) so neighbours' labels don't collide; field layouts per
  symbol key (`field_layout`, text side per unit via `text=`), unwired pins labelled in the direction the pin points.
  Legibility was proof-read tile by tile on all three sheets (2026-10-24, three passes); crops with
  `rsvg-convert` of the `kicad-cli sch export svg` output (viewBox in mm) are the quickest check after a drawing change. Live view while editing a drawing: `tools/live.sh [strip|group|master] "note"` regenerates, checks (verify, ERC) and exports SVG for the page served by
  `.claude/launch.json` ("schematic-live", http://localhost:8765).
- `master.kicad_sch` / `.kicad_pro` — master MODULE (16 HP; 631 parts since D13 + RV7-RV9, 620 since CS7; + its jack board) since the M1 split (2026-10-22).
  HIERARCHICAL on A4 since 2026-10-25 (prints on A4): `master.kicad_sch` is the root sheet (one sheet symbol per page),
  `master_sheets/NN_*.kicad_sch` the 30 pages (29 before v0.13), all GENERATED (`build(pages=dict(paper='A4', folder=...))` in schgen.py:
  the blocks' fragments packed in rows onto each page, a block running on to the next page with "(cont.)", a later
  smaller fragment pulled forward to fill a page; global labels between pages; the meter LED strings in two columns of
  five). The generator deletes and rewrites the folder. Netlist identical to the flat sheet (563 parts, 361 nets then;
  620 / 390 since CS7; four LED-string mid nodes now carry their intended names). PWR_FLAGs sit beside pins of their own
  net (ERC wants one on the page). `tools/live.sh master` shows the root sheet only; export SVG for the pages.
- `group.kicad_sch` / `.kicad_pro` — group module ×4 (sub n + returns 1 and 2 + aux n master, 292 parts since RV7), GENERATED by
  `.venv/bin/python tools/gen_group.py group.kicad_sch`; exports group.net/.pdf/_BOM.csv.
- `group_jack_board.kicad_sch` (7 × NJ6FD-V, 2×8 link + 2×5 link for return 2) and `master_jack_board.kicad_sch` (9 × NJ6FD-V + 3 × NC3MAV,
  2×20 link) — written by gen_group.py / gen_master.py with their main boards (master_lib.jack_board).
  Both generators also write `group_parts.json` / `master_parts.json` (blocks + decoupling pairs, for placement).
- Group / master PCBs (placement only, 2026-10-22): `$KPY tools/place_group.py` → `group.kicad_pcb` (38 × 349.5 mm,
  y 94.5–444 since RET1) + `group_jack_board.kicad_pcb` (38 × 93.5 mm, y 0–93.5); `$KPY tools/place_master.py` (~3 min) →
  `master.kicad_pcb` (78.6 × 331.5 mm, y 112.5–444) + `master_jack_board.kicad_pcb` (78.6 × 111.5 mm). Strip frame:
  same y origin, fader slot line (y 372), bus header height and spade; parity DRC in place.
- (history) the master section was one sheet of 1059 parts before the split.
  GENERATED by `tools/gen_master.py` from master_section_spec.md (helper functions per circuit;
  refs auto-assigned, dual op-amps/comparators allocated unit by unit with their decoupling).
  Both generators use the shared builder `tools/schgen.py`. Same loop with `master` in place of
  `channel_strip` (`tools/gen_master.py master.kicad_sch`). Exports: master.net/.pdf/_BOM.csv.
  The master's parts, reference allocation and circuit functions live in `tools/master_lib.py`
  (shared with gen_jig.py); gen_master.py is just the master's netlist.
- `jig_master_stub.kicad_sch` / `jig_load_board.kicad_sch` (+ .kicad_pro) — test-jig boards (test_jig_spec.md
  v0.11), GENERATED by `.venv/bin/python tools/gen_jig.py` (writes both, plus `jig_*_parts.json`: blocks and
  decoupling pairs for placement). Same verify/check_fp/ERC loop. PCBs (placement only):
  `$KPY tools/place_jig.py` → `jig_master_stub.kicad_pcb`, `jig_load_board.kicad_pcb`; parity DRC in place.
  Bus headers with pin 1 at the front end since 2026-11-11 (one flat ribbon: load board, strips, stub). `tools/jig_3d.py`
  (Blender, `docs/tooling.md`) draws the jig on a bench into `render/jig.blend` / `render/jig*.png` and writes
  `render/jig_master_stub.json` / `render/jig_load_board.json` (`tools/export_3d.py`).
- `goa-console.kicad_sym` + `sym-lib-table` — project symbols (DRV134, the GNDM and PHONESGND power symbols, the PSU's
  `+V` / `0V` / `-V` power symbols local to its sheet (2026-11-12), XLR3_Shell:
  KiCad's XLR3 plus the NC3MAV / NC3MAH shell pad G, on CHASSIS on the master jack board and the jig stub since 2026-10-28).
- `jack_board.kicad_sch` / `.kicad_pro` — strip jack board (J1, J2, J5 NJ6FD-V, C8/C9, CN5 2x5 link),
  GENERATED by `tools/gen.py` together with channel_strip.kicad_sch (link pinout = `LINK` in gen.py, spec 16.4).
  Exports: jack_board.net/.pdf/_BOM.csv. Same verify/check_fp/ERC loop with `jack_board` in place of `channel_strip`.
- `channel_strip.kicad_pcb` — strip main board (the strip project's own board since 2026-10-26; was
  `channel_strip_v4.kicad_pcb`), 4-layer since 2026-10-27, 38 × 400 mm (y 44–444) at 11.5 mm under an 8 HP × 12U
  panel (two pot columns), 327 parts + 6 M3 holes (v5.6); `jack_board.kicad_pcb` — 38 × 43 mm (y 0–43) at 24.0 mm
  under the panel. Same y frame, so they overlay. Component placement only: no tracks, vias or copper zones.
  Rebuild both with `tools/build_strip_pcb.sh [main.kicad_pcb [jack.kicad_pcb]]` or, per board,
  `/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 tools/place_strip.py channel_strip.net channel_strip.kicad_pcb`
  (`jack_board.net jack_board.kicad_pcb` for the jack board; the layout is picked from the parts).
  Re-running the generator overwrites unrouted placement edits. It refuses to overwrite
  an existing board containing tracks, vias or zones; use a separate output for later placement work.
  Every board is its schematic's project board (`X.kicad_pro` / `X.kicad_sch` / `X.kicad_pcb`), so parity DRC runs in
  place: `$KC pcb drc --schematic-parity --severity-all channel_strip.kicad_pcb` (and so for every board).
  Footprint-symbol links: the placer writes each footprint's full symbol path (`/<sheet uuid>/<symbol uuid>` on the
  hierarchical strip / group / master, with Sheetname / Sheetfile), as KiCad's Update PCB does (fixed 2026-10-26: flat
  `/uuid` paths had left every footprint on those three boards unlinked; parity DRC didn't show it, because it falls
  back to matching by reference). Check: `$KPY tools/check_links.py <name> ...` (every footprint's path equals its
  symbol's in the exported netlist; 1316 / 1316 on the nine boards on 2026-10-26, 1517 / 1517 on 2026-10-28);
  the placer also writes what KiCad's Update PCB copies from each symbol (the sheet's path names, the symbol's fields
  only, `ki_fp_filters`, the position-file flag, and the units with their pins, which the Python API can't set, so
  `placer.write_units()` adds them to the saved file). Checked in KiCad 10.0.7 (2026-10-26): Update PCB from Schematic with
  re-link by reference off lists 0 changes, 0 errors on the strip, group and master; the only warnings are the ALPS RK09L's
  mechanical MP pads (strip RV8, group RV2), which have no symbol pin.
  unconnected items are expected at the placement stage and are not an instruction to route.
  Schematic UUIDs are deterministic (schgen.py), so the footprint-symbol link survives regeneration.
  `docs/studies/strip_panel_study.md` — 12U vs 15U, one vs two pot columns.
- `archive/channel_strip_v3.1.kicad_pcb` — old v3.1 placement (38 × 480 mm, 103 parts), kept for reference; don't
  rebuild it from the v4.0 netlist.
- `docs/build/panel_print.md` — the Delta's panel legend system (from ref/delta200_panels and verified photos of real modules,
  with links) and our adaptation to the two-column panels; the reference for the panel artwork.
- `sim/strip.cir` — ngspice model of the signal path (ideal op-amps).
- `master_section_spec.md` — master section spec, v0.13 draft: stereo mix path, mono, outputs,
  power-on mute, subgroups, aux masters, stereo returns, monitoring/PFL/meters, power entry.
  `sim/master_mix.cir` — mix path model (single-pole OPA1612); `sim/aux_master.cir` — aux
  summing-amp stability; `sim/routing_switch.cir` — strip DG413 routing switch (level, THD, bus C, click);
  `sim/mid_tuning.py` — Delta Wien vs KHN mid-band tuning (law, boost, Q, noise; `python3 sim/mid_tuning.py 10e3`);
  `sim/mute.cir` — power-on mute control; `sim/meter.cir` — meter rectifier/ballistics (precision peak
  detector; the Delta-style one read −20 dB as −11.7 dB); `sim/pfldet.py` — PFL detect line with 42 keys, clamp,
  debounce and contact bounce. `tools/placer.py`: `PLACER_REPORT=1` prints every report row over its limit.
- `docs/studies/master_panel_study.md` — master panel/module study: M1 chosen (4 × 8 HP group modules + 16 HP master module).
- `docs/reviews/master_parts_review.md` — review of the six parts proposed in master spec v0.6 (2026-10-23), per-item verdicts and
  the sign-off list; review sims in `sim/review/` (one folder per item).
- `docs/reviews/strip_parts_review.md` — strip v4.0 op-amp stability (TI OPA161x model in the real network) and part ratings
  (2026-10-23); signed off T1-T11 and applied as strip v4.1. Scripts in `sim/review/strip/` (TI model via
  OPA161X_LIB, not in the repo; `python3 run_all.py none` gives every unit's phase margin over 21 states).
- `docs/reviews/master_group_review.md` — master + group op-amp stability (TI OPA161x / OPA1656 / TL072 / DRV134 models, fitted
  LME49600 macro, whole-module decks) and ratings / BOM (2026-10-24), analysts + three skeptics; MG1-MG20 signed off
  2026-10-24 and applied (master spec v0.8). Scripts in `sim/review/master/` (`TI_MODELS=... python3 run_all.py none
  all`) and `sim/review/group/` (`python3 sweep.py pots none 0.08`); TI models via TI_MODELS, not in the repo.
- `docs/reviews/design_review.md` — independent review (2026-10-25: pinouts vs datasheets, logic / polarity, spec and decision
  conformance; three reviewers, every finding verified): R1 DRV135UA, R2 group pan RK09L, R3 jig R45, R4 PVA2 silk
  marks, R5 documentation / BOM drift, Q1 ON mutes the pre sends; all signed off and applied 2026-10-25.
- `docs/proposals/gaps_proposal.md` — the strip's unsimulated circuits closed (2026-10-25): overload detector, soft mute, key clicks
  with real op-amp offsets, 200-strip tolerance Monte Carlo, headroom at every op-amp output (`sim/review/gaps/`:
  ol.py, mute.py, keys.py, mc.py, headroom.py). K1 (PFL send DC block, C96) and K3 (overload LED: C12 100n, U4B hold
  stage R115 / C97, ~150 ms) signed off and applied 2026-10-25 (strip spec v4.5). Everything else passes.
- `docs/reviews/met1_ret1_review.md` — independent review of MET1 / RET1 (2026-10-26): no faults; applied: group jack board CN1 moved
  1 mm off J5's tip joint, return keys labelled R1 / R2 on the group panel, D2's footprint outline / no model line,
  3-lead spacer for D2, `sim/pfldet.py` at 42 keys. Proposals P1-P4 (1K in series with U4A / U17A discharge,
  100 nF on VREF, optional 10M hysteresis, panel-end fastening of standoffs): P1 / P2 applied (strip v4.9), P3 declined,
  P4 decided (studs or spacers, countersunk screws at the jack boards; Decisions, strip v4.9). Group stability with return 2 (TI OPA161x +
  fitted OPA1656, `sweep.py ret none 0.08`): receivers >= 66.4 deg, level buffers >= 70.9, followers >= 52.1. Group review
  decks: fix set `none` since rev 0.2 (`mg` re-pins U2B onto a floating node; `fixes.apply()` now refuses it) and
  `OPA1656_FIT` for the followers (TI's OPA1656 model doesn't converge in the deck on ngspice 46; it does with `.options itl1=500`, found 2026-11-04). On TI's own OPA1656
  model with the OPA1612s single-pole (`OPA1612_SIMPLE=1`, `STAGES=`; 2026-10-28) the return followers read 59.2-61.0 deg
  over ret / pots / loads (fitted: 52.1-52.9).
- `docs/studies/console_survey.md` (2026-10-27) — the whole design against the ten analogue consoles in Ruslan's service-manual library
  (Delta / DLX, Venue II / Theatre, Series Two, 6000, 200B, Sapphyre, Ghost, Series Five, SSL 4000G, PM-4000 / 5000,
  Sony MXP-3000); per-console reports with page refs in `docs/console_survey/`. Ours leads on the line receiver, output
  relays / power-on mute, ground cancel and couplers. Proposals CS1-CS8 as written (since applied: CS1, CS2, CS2b, CS4,
  CS4b, CS4c, CS6, CS7, CS10, CS11, CS11b; CS3 / CS5 checked, no change; open: CS8, CS9): multi-point full-wave
  OL detect (7 of 9 consoles; ours one point, positive only), pan law -4.4 dB as the Delta's ED3344C (ours -6 dB, an
  unrecorded departure), summer headroom check / sum below unity, jack I/O clamp diodes, PFL crosstalk (SW3 / SW4
  supply-pole caps per the Series Two field mod, pin 28 dummy track, virtual-earth PFL DET), fusible per-strip feeds,
  C/Room dim, deeper mute (jig). Corrected master spec §3's misreading of the Delta's monitor-select receivers.
  Added 2026-11-12 (§8, `docs/console_survey/dda_amr24.md`): the DDA AMR 24 from the iCloud `Service Manuals/DDA amr24/`
  manual and schematics. Balanced mix / group buses with an op-amp-only differential summer, a 10K-per-module aux
  ground-sense line, source-end routing, an unbuffered 1 % line receiver, pre sends before or after the cut by a link.
  No change and no proposal.
  Second batch (§7, 2026-10-27, from ~/Downloads): A&H GL2 / GL2200 and GL3300, AMEK big (no circuits), Yamaha MC
  series (Phonic OEM), Spirit E8, Mackie 1604 / 1402-VLZ and 8•Bus; nothing weaker in ours. New proposals CS9 (fader
  shut-off compensation as A&H, only if the PTB0143 sample's residual is worse than -80 dB), CS10 (reverse diodes per
  rail on every strip / group board), CS11 (jig tests: output balance, measured CMR, fader breakthrough, GCANCEL current).
- `docs/proposals/cs11_proposal.md` (+ `archive/patches/cs11_proposal.patch`, `test_jig_spec.md` only) — CS11, signed off by Ruslan and applied 2026-10-27: jig
  tests 13-17 with targets from `sim/review/cs11/jig_targets.py`: DRV134 output balance (-90 dB with matched 10 uF, but
  -25 / -35 dB at 100 Hz / 1 kHz with them 20 % apart: the DRV floats its outputs; larger or matched couplers a possible
  follow-up), line CMR (1 kohm tip: 60 / 56 / 38 / 32 dB at 50 / 1k / 10k / 20k, the 100 pF caps), fader / pan
  residuals vs end resistance (-80 dB needs <= 0.3 ohm: decides CS9), faders-down MIX noise N 4..24 (-106.7..-100.1
  dBu), GCANCEL current.
- `docs/studies/goa_production_90s.md` (2026-11-11, a study, no design changes) — how goa trance was produced in 1993-1999,
  centred on the work at the console, from interviews, studio features and reviews read that day (every statement marked
  documented / inferred / not found, 53 sources listed; a second pass through Chrome and archive.org added sleeve
  credits, Posford's studio video and a search of Muzik 1995-99). Mackie 32•8: documented for Simon Posford
  (Hallucinogen), Eat Static and Banco de Gaia, found for no continental or Israeli act; Juno Reactor on a Raindirk Symphony, Butterfly on a
  DDA AMR24. Method: sequencer live through the desk to DAT, hands-on mix, no automation, no recall. Last section sets
  the findings against the decisions on inputs and returns, aux count, PFL only, direct outs and mutes.
- `docs/studies/eight_groups_study.md` (2026-10-27, a study, no design changes) — 8 subgroups, from the Venue / Delta 8 sheets
  (ED2911A/B, ED2915B, ED2778A/B, ED2780): the Venue input is the 8-group build of the DLX channel (groups 5-8 on
  motherloom pins 7/5/3/1), the Delta 8 is eight ED2778 group modules each jumpered to its bus, mute groups on a
  separate 10-way CN6. Costed for ours: strip keys / DG413s / panel row, 8 group modules (+163 mm), PSU / wing load.
- `docs/proposals/cs2_proposal.md` (+ `archive/patches/cs2_proposal.patch`, tools only) — CS2, signed off by Ruslan (Option A) and applied 2026-10-27 (strip v5.4): the Delta's pan law
  (ED3344C) on the strip: U8B / U3A at 1.22x (2K2 / 10K) with 3K3 back to the wipers (R136-R141), -2.7 dB centre, +1.7 dB
  hard (4.4 dB law); 22p C0G across each 2K2 (C105 / C106) needed: without it TI's model gives 32 / 14 deg, with it
  81.6-85.3. Mix +3.3 dB at centre (summer headroom 29.5 -> 26.2 dB per source), S/N unchanged; PAN off stays POST
  (1.7 dB under a hard pan; matching it needs a bus coupler no D10 spot allows). sim_netlist 41/41, sim_console 35/35
  with shifted targets. `sim/review/cs2/pan_law.py`. The -6 dB was a transfer error (v3 copied the buffers as followers),
  confirmed against ED3344C and the 200 Delta manual (p.34: 4.5 dB centre drop).
- `docs/proposals/cs2b_proposal.md` (+ `archive/patches/cs2b_proposal.patch`, tools only) — CS2b, signed off by Ruslan and applied 2026-10-28: the strip's law on
  the group's sub pan (U3B / U5A at 1.22x, R123-R128, C96 / C97, made last; placed by moves_only under U3 / U5, <= 5.9 mm).
  Master spec §12 says the sub pan copies the strip; the parent's ED2778A MONITOR PAN is passive (3K9 / 8K2), -4.6 dB.
  Sub to MIX +3.3 dB at centre (sim_console GPANC). TI models: U3B / U5A 74.5 / 75.3 deg, 55.3 / 55.9 with 47 pF, no unit
  worse. `sim/review/cs2/group_pan.py`. (Corrected 2026-10-28: the follower figures of that run came from a stand-in
  `OPA1656.LIB`, TI's OPA161x under the OPA1656 name; TI's real model gives the followers 59.2-61.0 deg, docs/reviews/met1_ret1_review.md.)
- `docs/proposals/eqmid_proposal.md` (+ `archive/patches/eqmid_proposal.patch`, tools only) — EQM1, signed off by Ruslan and applied 2026-10-28 (strip v5.5): the KHN mid ranges
  retuned to the Delta's measured ones (Audio Precision plots, 200 Delta Tech Manual p.17; overlay from `sim/eq_curves.py`):
  HI-MID R86 / R87 430R -> 392R and R56 / R57 4K7 -> 4K99 (686 Hz-10.5 kHz -> 598 Hz-9.93 kHz), LO-MID R60 / R61 4K7 -> 4K22
  (148 Hz-2.29 kHz -> 165 Hz-2.54 kHz). Boost / cut / Q, noise and TI stability unchanged. Closed-form fit
  `sim/review/eqmid/retune.py`, netlist measurement `measure.py`; four new sim_netlist peak-frequency checks (45); panel
  FREQ numerals. Cause: the tuning copied a model of the "100KC" pot; ED2911A reads "DUAL 100K REVLOG".
- `docs/proposals/cs7_proposal.md` (+ `archive/patches/cs7_proposal.patch`, tools + `sim/review/master/configs.py`) — CS7, signed off by Ruslan and applied
  2026-10-28: DIM on C/Room (SW4, a PVA2 at (29.16, 178) beside POWER; R236 / R237 91K between CRSB and each C/ROOM pot top, shorted
  by the released key; -20.0..-20.75 dB, phones / meters +0.08 dB; made last). Main R's DRV135 U8 + C47-C50 / R224 / R225
  move to the bottom beside the key (22R legs 9.0 / 9.8 mm, were 10.2 / 10.5). `placer.py`: moved parts leave their packed
  spots first (U8 and C48 trade spots); strip / group / jig re-place identically. `sim/review/cs7/dim.py`; sim_console dim
  test; TI models (the real OPA1656 is in the master review's model folder, `ti/OPA1656.LIB` is a stand-in): U23 84.8 deg
  dimmed, U21 49.7. Switching step -59 dBu at the TRS (0.50 mV CRS offset). Reverses console_architecture's "monitor dim".
- `docs/proposals/cs11b_proposal.md` (+ `archive/patches/cs11b_proposal.patch`, tools only) — CS11b, signed off by Ruslan and applied 2026-10-27: each DRV135's
  two 10 uF couplers as a pair sorted within 2 % (MPN note; LME49600 bypasses and the jig stub as bought; 10 sorting
  spares in `order_bom.py`). `sim/review/cs11/drv_couplers.py` (TI model): output balance worst 5 % at 1 kHz / 100 Hz
  -32 / -20 dB as bought -> -60 / -47 dB; 47 / 100 uF cans as bought only -45 / -26 and -52 / -32, and no D6.3 / D8 fits
  at any of the 30 coupler spots; the coupler value doesn't change the loop (|1+T| min 0.188). Nothing moved.
- `docs/proposals/cs6_proposal.md` (+ `archive/patches/cs6_proposal.patch`, tools only) — CS6, signed off by Ruslan and applied 2026-10-27 (strip v5.3): R1-R4 (10R to
  +VA / -VA / +VL / -VL) on every strip and group as Vishay M25SI fusibles (M251206BB1009JP500, 1206 0.25 W, fuses >= 3 W;
  DigiKey stock; TT FCR0805 / 1206 too small at 0.1 / 0.125 W, FCR1210 not stocked). `sim/review/cs6/fusible.py`: a
  short behind one draws 1.66 A, 27.5 W, opens it in < 0.07 s while the wing PTC stays under its trip current; duty
  32-73 % of rating (film <= 79 C in the 40 C tub); a module plugged into a live wing (1.59 A, 30 mJ, 1.6 ms over 6.5 W)
  may open them: power down first. Strip R1-R4 leave the packer (moves_only, C2 / C4 fixed, old spots kept out), nothing
  else moved.
- `sim/review/cs5/pfl_xtalk.py` (2026-10-27, CS5 check, no change): one wing's conductors 25-31 with the PFL summer and
  PFL DET; everything into the PFL sum sits at or below its ~-93..-97 dBu floor. AUX2 -105 dB at 20 kHz; -V ripple
  -122 dBu; a key press -94 dBu peak, at the DG413's own click; key decouplers (CS5a) can't help (+VL is already
  10R / 47 uF). Pin 28 on GNDA at the master (-105 dBu click, -202 dBu ripple) is a free option, not needed.
- `sim/review/cs3/bus_headroom.py` (2026-10-27, CS3 check, no change): per source the summer, re-inverter, master fader
  top and post-amp all carry -6.4 dBu (29.5 dB to clip), the XLR -0.9 dBu against the DRV135's +27 dBu (27.9 dB); 24
  strips at nominal leave 15.7 dB at the summer. The summer clips first only with the master fader > 1.6 dB below "0".
- `docs/proposals/cs4b_proposal.md` (+ `archive/patches/cs4b_proposal.patch`, tools only) — CS4b, signed off by Ruslan and applied 2026-10-27: the strip's
  BAV199 jack-link clamps on the group (14 per board, D7-D20 at CN3 / CN4) and master (24, D79-D102 at CN5), created
  last by `master_lib.link_clamps()` so no ref moves. `sim/review/cs4/jack_protect_mg.py`: phantom on a DRV135 output
  leg puts 47.7 V on its 10 uF 25 V coupler and Sense pin as built, 17.7 V clamped; 8 kV ESD into the output pin
  22.8 -> 5.9 A. CS4c: `docs/proposals/cs4c_proposal.md`.
- `docs/proposals/cs4c_proposal.md` (+ `archive/patches/cs4c_proposal.patch`, tools only) — CS4c, signed off by Ruslan and applied 2026-10-27: 22R ERJ-P06J220V
  between each DRV135 output pin and its 10 uF, inside the Sense loop (group R119-R122, master R222-R235, created last by
  `master_lib.drv_loop_rs()`; jig stub unchanged). `sim/review/cs4/cs4c_drv.py` (TI DRV134 model via TI_MODELS): 8 kV
  into the output pin 5.9 -> 0.84 A; no resonance in the cross-coupled loop up to 300 MHz for any load or 30-240 nH of
  in-loop track; the loop does NOT null the resistor: differential output impedance 52.6 -> 73.8 ohm, -0.16 dB into
  600R, clip into 600R +27.5 -> +27.2 dBu. `placer.py` `wire=`: attach targets see through the listed parts (else the
  DRV caps re-pack). Nothing else moved. Group U7's 10 uF sit ~115 mm from it (no nearer spot).
- `docs/proposals/cs4_proposal.md` (+ `archive/patches/cs4_proposal.patch`, tools only) — CS4, signed off by Ruslan and applied 2026-10-27 (strip v5.2): a BAV199 (pin 3 to
  the signal, pins 2 / 1 to +VA / -VA) on each jack-link signal at CN3 (D18 IN_T, D19 IN_R, D20 RET_RAW, D21 SEND,
  D22 DO_T), ahead of every series part. `sim/review/cs4/jack_protect.py`: an 8 kV contact discharge leaves the input
  op-amp 0.09 A (9.6 A as built), an output 0.38 A (18.9 A); phantom leaves C51 / C52 at 17.7 V (41.9). A TVS at the
  jacks was rejected (-93 / -99 dB THD at 20 kHz from 1 kohm); the clamps cost -106 dB at +20 dBu 20 kHz, nothing at
  0 dBu. Placement by moves_only, nothing moved. CS4b (group / master, shared master_lib functions) applied the same day.
- `docs/proposals/cs10_proposal.md` (+ `archive/patches/cs10_proposal.patch`, tools only) — CS10, signed off by Ruslan and applied 2026-10-27 (strip v5.1): a PMEG4010CEH
  reverse Schottky across each audio rail of every strip (D16 / D17) and group board (D5 / D6, created last so no ref
  moves). `sim/review/cs10/rail_loss.py`: a lost rail (wing PTC trip, open ribbon conductor) is driven past ground by
  the op-amps' 87 mA, C1 / C3 reversed by 2.5-12.7 V and 60-87 mA through the ICs' protection diodes; with the diodes
  +-0.36 V and 0 mA. Placement by moves_only (nothing else moved); `place_group.py` has `moves_only` now.
- `docs/proposals/cs1_proposal.md` (+ `archive/patches/cs1_proposal.patch`, tools only) — CS1, signed off by Ruslan and applied 2026-10-27 (strip v5.0): the OL LED from
  RECV / GOUT / EQOUT / PRESRC / FPOST through 1K + BAV99 each; positive peaks into PK as built, negative peaks into
  OL_NN (C103 // R134, PK's mirror) read by a new U18A through a 4M99 / 10M divider from +VL (thresholds ratios of +VL
  only: a first try biased from -VL lit the red at every power-down). `sim/review/cs1/ol_multi.py`: +18.4 dBu on every
  tap, -9.29 / +9.01 V pulse thresholds, catches four cases the as-built misses, no false red, holds unchanged. Trial
  tree 59 / 59 (strip 902 pins / 310 parts, 0 DRC / parity, 1 existing part moved: D1); PK / OL_NN ~390 mm (FPOST tap
  at U2), Switching class. Applied as proposed (five taps, both polarities); `ol_multi.py --quick` in check_all --full.
- `docs/studies/eq_survey.md` — how other consoles build the swept mid EQ, read from Ruslan's iCloud service manuals (SSL 4000G,
  Yamaha PM-4000/5000, Soundcraft 6000 / 200B / Sapphyre / Ghost / Series Five, Sony MXP-3000) and the Mackie BOM: all
  tune with reverse-log (C-law) pots as rheostats, Ghost / Series Five are KHN like ours but with 200KC / 100KC rheostats;
  none tunes by dividers (our A10K dual). Q pots on the big consoles are the one feature we lack (noted, not proposed).
- Stability re-run 2026-10-26 on today's netlists and placement (`docs/reviews/met1_ret1_review.md`): group (all sweeps, both
  returns) and master (31 configurations + phones, `sim/review/master/run_each.py`) match 2026-10-24; worst master
  unit U21A/B 47.7 deg at the pot top as then. `configs.py` now finds build-out far sides and spare units from the
  netlist (the drawn master's unnamed nets had moved the +47 pF stress to the pin side). Master re-run 2026-10-29 (master
  v0.12) with the trace table re-measured after CS4b-CS7 (34 configurations): worst still U21A 47.7 deg, no unit lower
  (`docs/reviews/met1_ret1_review.md`). Corrected 2026-11-04: 14 of those 34 timed out and read older raw files, the `_placed` runs among them
  (fixed in `mstab.py`). Full re-run on master v0.14, 2026-11-03 / 04: 34 configurations, 1360 unit results all simulated; worst
  U21A/B 47.7 deg, every unit's minimum unchanged; `_placed` U13A -5 deg with A5_OUT at 98 mm, still >= 69.1. Group 2026-11-04: 222 states on
  TI's real OPA161x + OPA1656 together, `mst_all.json` re-measured (it had reached only 22 of 78 op-amp nets): followers 59.1-60.9 deg, unstressed
  worst U1B 56.8, 46.1 with +47 pF (U6B).
- `docs/studies/emc_placement_study.md` — placement-level EMC check (2026-10-26) against Self / Whitlock / Muncy / AES48 / Ott /
  TI / ADI rules, measured with `tools/emc_check.py` (KiCad Python: entry runs, aggressor-victim pad distances, long
  switching nets, supply entry). Strip: MET1's LED lines span ~260 mm and end 4.3 mm from U16's inputs; U16's
  220R / 100p 11-16 mm from its pins; the J112 mute ~20 mm from U3B; bus power runs 42-46 mm unfiltered; jack board
  C8 / C9 and the sleeve 24 mm from the chassis standoffs. E1-E5 and E8 signed off and applied 2026-10-26
  (placement only): strip LED switches beside D2 on the bottom (anode lines 257/274 -> 19/8 mm), U16's 220R/100p and the
  J112 mute on the bottom under their op-amps (2.7-3.5 / 1.3 mm), supply filters at the bus header (strip 5.5-8 mm,
  group 15-16), jack board C8/C9 between J1's pins, master flasher diode at U22 and PFL detect by the PFL switcher.
  The strip's upper op-amps (U1, U4-U7, U12-U16) are now fixed in place_strip.py (the packer re-shuffled every IC);
  placer.py lets a fixed part stay in its zone as an anchor. E6 (10 nF base caps) applied in strip v4.9 (it slows SIG_B's edges, not the LED current's); E7 (ferrites) open
  until the jig.
- `routing_guide.md` — routing notes for the strip, group, master, the jack boards, the jig stub / load board and the PSU (2026-10-26; group / master / PSU 2026-10-27): ground and
  supply strategy, the sensitive nets with lengths (IN_T/IN_R, pan buffer L's wiper line (165 -> 24 mm with PAN1), FPIN, KHN nodes, aux
  sends, PRESRC, VREF; jig GCREF / GCREF_BUF ~175 mm), the switching nets to keep away, CHASSIS on the jack boards,
  the net classes and rules (written into the projects by `tools/netrules.py`, below), the 4-layer stackup and return vias.
- `docs/proposals/pan_buffer_proposal.md` (+ `archive/patches/pan_buffer_proposal.patch`) — PAN1, signed off and applied 2026-10-26 (strip v4.8): pan
  buffer L moved from U2B (fader end, 165 mm wiper line) into the spare U8B beside the pan pot (24 mm); U2B is the spare.
  Options (a) both buffers in U3 and (b) U2 at the pot rejected. the local (gitignored) `sim/review/strip/results_none.json`
  refreshed (it was from strip v4.1).
- `docs/proposals/stab_caps_proposal.md` (+ `archive/patches/stab_caps_proposal.patch`) — E9, signed off and applied 2026-10-27 (placement only): the
  strip's twelve C0G stability caps that sat 6-22 mm from their op-amp pins (C84 at U7B 22.1 mm, C83 at U8A 10.5) moved
  to them, nine on the bottom under their op-amp; every C0G cap on an op-amp input <= 6.3 mm. The caps move after packing (`placer.py` `moves`, 2026-10-27),
  so the greedy packer doesn't re-shuffle ~90 parts into the slots they leave. E9b (group 11 / master 13 caps, up to
  13 mm -> <= 6.4 mm, `archive/patches/stab_caps_e9b.patch`) signed off and applied 2026-10-27; the jig stub was already <= 6.3 mm.
- `docs/proposals/input_nets_proposal.md` (+ `archive/patches/input_nets_proposal.patch`) — E10, signed off and applied 2026-10-27 (placement only): 18 resistor
  moves (strip 9, group 7, master 2) shorten the long high-impedance op-amp input nets (MST over 20 mm: strip 17 -> 9,
  group 10 -> 3; e.g. group return receiver U9B- 39 -> 13 mm, master post-amp U5A- 27 -> 13), no net longer, C0G caps
  untouched; 0 DRC / parity.
- `docs/proposals/decouplers_proposal.md` (+ `archive/patches/decouplers_proposal.patch`) — E11, signed off and applied 2026-10-27 (placement only): 21 SMD
  decouplers over 5.5 mm from their supply pin moved to it (strip 13, incl. the DG413s' 6-10 mm -> <= 0.55; group 1; master
  7); decouplers over 5 mm strip 14 -> 1, group 2 -> 1, master 27 -> 20 (C144 / C145, the LME49600's THT 10 uF, have no
  nearer spot). 0 DRC / parity.
- `docs/studies/layer_study.md` — 2 vs 4 layers (2026-10-27, for Ruslan's decision): the main boards need about one full signal layer
  of routing (ratsnest 63-72 mm/cm2, 118-161 crossings per 10 cm2; jig / PSU / jack boards 8-17 and 2-14). Quotes on
  2026-10-27 (no shipping): JLCPCB phase 1 $43.50 all 2L vs $70.50 with the three main boards on 4L, full build $106 vs
  $199 ($1.25 per strip); PCBWay +$50 / +$184; Aisler +EUR 58 / +EUR 472 (4L ENIG only). Recommendation: 4L for the strip,
  group and master mains, 2L for every other board. Decided by Ruslan 2026-10-27 and applied (see Decisions).
- `docs/proposals/untangle_proposal.md` — ratsnest untangling (2026-10-27): `tools/ratsnest.py` (KiCad Python) measures each board's
  signal-net ratsnest and crossings (grounds / rails left out; incremental `Rats.trial()` checked against full and
  brute-force counts). Applied, placement only: two-pad parts turned in place (`placer.py` `turns`, `TURNS` in the three
  main-board layouts): crossings strip 1292 -> 1211, group 1674 -> 1600, master 2419 -> 2261, no part moved, DRC / rules
  clean. Unit / channel swaps measured: at most -12 crossings, none recommended. `placer.py` now ignores rule areas
  when refusing to overwrite a routed board.
- `docs/build/build_records.md` — values measured during assembly that later checks depend on: §1 the DRV135 coupler pairs (CS11b:
  sorting, 15-row record, per-output balance bench check against 20 log10(m) - 13 / - 26 dB at 100 Hz / 1 kHz).
- `docs/build/sample_order.md` — the parts to order with the prototype panel and the nine physical checks they settle (9: the fader's residual at the bottom stop, for CS9).
- `docs/proposals/wing_power_proposal.md` — pin 34 as a third +V conductor (W1) and MF-RX250/72 +V wing PTCs (W2), signed off and
  applied 2026-10-25.
- `docs/proposals/film_np_proposal.md` (+ `archive/patches/film_np_proposal.patch`) — film couplers and MUSE ES bipolars, F1-F4 signed off and applied
  2026-10-24.
- `docs/proposals/film_eol_proposal.md` (+ `archive/patches/film_eol_proposal.patch`, tools only) — FE1 signed off by Ruslan and applied 2026-10-29 (FE2 not taken): the 2.2 uF
  film coupler WIMA MKS2C042201K00KSSD is obsolete (Yageo PCN PTN-093025-VK, thin PET). FE1: same footprint, KEMET
  MMK5225K63J06L4BULK (7.2 x 13 x 7.2, also obsolete; Mouser 1,841), buy the console's quantity at once; trial 61/61, nothing moved.
  FE2: W8.5 footprint for the active WIMA M-box (8.5 x 14 x 7.2); the trial hits one collision per board (strip R5 / C13,
  group C76 / C21, master C82 / C66).
- `docs/proposals/hpf_proposal.md` (+ `archive/patches/hpf_proposal.patch`) — sweepable HPF 21-403 Hz (KHN on U5A + new U15, RV16 A10K dual, C91),
  H1-H4 signed off 2026-10-24 and applied (strip v4.3, master v0.9). Design study `sim/review/hpf/khn_hpf.py`
  (`law | mismatch | noise | stab`); trial checks `sim/review/hpf/trial_*.py` run on a tree with the patch applied.
- `docs/studies/ground_study.md` — ground-and-hum study (2026-10-25): harness lengths and loop areas from the 3D build, gauge,
  magnetic loop pickup, LED returns, synth ground loops with a receiver Monte Carlo; G1-G3 signed off and applied
  2026-10-25 (§9 there). `sim/review/ground/ground_study.py [geom|gauge|mag|led|synth|stereo|all]`;
  `sim/review/ground/follower_stab.py` (U16 phase margin, fitted OPA1656 macro via OPA1656_MACRO, not in the repo);
  `sim_console.console()` takes per-module spade R/L (`spade=`, default the G1 harness `SPADE_WIRE`) and EMFs
  (`spade_emf=`).
- `docs/build/sourcing.md` — BOM sourcing check of every MPN (2026-10-25): order-code fixes applied, stock risks (PTB0143, NJ6FD-V,
  OPA1612, WIMA 2.2 µF), S1 signed off and applied (the discontinued 10 µF NP UES1E100MDM -> Panasonic ECE-A1EN100U). Plain 0805 resistors: Yageo RC0805FR-07xxxL.
  `python3 tools/order_bom.py` -> `bom/order_bom.csv`: the console-wide order list (every board's BOM x boards built,
  one line per order code, spares, the jig A/B OPA1656s); re-run it after any BOM export.
  `python3 tools/order_bom.py phase1` -> `bom/order_phase1.csv` (2026-10-28): the staged hardware test (`test_jig_spec.md`
  1.1): stage A one strip + jack board merged with `docs/build/sample_order.md`, the N1 swap OPA1656s, bench-power lead, panel
  blank; stage B jig stub + load board + ribbons + test fixtures; an optional second strip. The same check found six
  strip C0G on 0805 pads with 1206 order codes (C7, C14, C37, C41, C94, C95); `gen.py` now picks the code by footprint.
- `panels/` — front-panel fabrication drawings (2026-10-25) from `.venv/bin/python tools/panel_fab.py`: per panel a DXF
  (OUTLINE / CUT / LEGEND, text outlined), 1:1 SVG / PDF artwork, PNG preview, hole table; numbered strip / group PDFs;
  checks (web, edge, rails, print clear of cut-outs). The layout is `tools/panel_layout.py`, shared with console_3d.py
  (cut-outs, screws, the Delta-style print). Open: measure the fader law before printing (`panels/README.md`).
- `frame/` — frame rail drawing (DXF, hole table, A3 PDF) from `python3 tools/frame_fab.py`; front and back rail, the
  back one with the vent slots.
- `tub/` — tub woodwork drawings (cheek, floor, arm-rest, plenum parts; cut list; A3 PDF) from `python3 tools/tub_fab.py`;
  `docs/proposals/tub_proposal.md`, `docs/tub_elevation.png`.
- `docs/studies/thermal_study.md` — console tub thermal study and the vented-tub decision (TH1-TH3).
- `psu_case/` — PSU case drilling (front / rear panels, heatsink, base; DXF, hole table, A3 PDF) from
  `python3 tools/psu_case_fab.py`.
- `docs/build/offboard_bom.md` — everything not on a board BOM (knobs, caps, washers, spacers, standoffs, panels, frame, IDC
  sockets and ribbon, the G1 harness, PSU chassis parts), counts per module and console; open decision: the panel maker
  (knobs / caps KN1-KC2, frame FR1-FR3, PSU case PC1-PC3 are decided).
- `psu_spec.md` — external PSU v0.2 (±17 V, 4 A per rail): study + the chosen option B design. `sim/psu.cir`
  (start-up, load step, crowbar, ripple). `psu.kicad_sch` (+ .kicad_pro) regulator board, GENERATED by
  `.venv/bin/python tools/gen_psu.py`; exports psu.net/.pdf/_BOM.csv. Same verify/check_fp/ERC loop.
  `psu.kicad_pcb` (120 × 60 mm, placement only) from `$KPY tools/place_psu.py`; parity DRC in place.
- `docs/proposals/strip_noise_proposal.md` — the strip's EQ current noise and N1 (OPA1656 in U1, U5-U7, U12-U15), not signed off.
  Re-evaluated on strip v4.4 (2026-10-25): PRE EQ in −92.8 -> −96.1 dBu, 24 strips at main L −79.2 -> −81.9 dBu;
  stability with datasheet-fitted macros (`sim/review/strip/stripdeck.py` OPA_MODEL=fit, `n1_stab.py`, `n1_compare.py`;
  the fit reads 3-24° below TI on the as-built strip): every N1 unit ≥ 50.1° over 21 states (on TI's real OPA1656 since 2026-11-04: ≥ 58.2°, as built U3B 59.8°, U16 61.7°); +115 mA typ console-wide.
  Open: distortion (CMOS input capacitance), only the jig A/B can settle it. `sim/review/strip_noise/noise.py n1`.
- `test_jig_spec.md` — test jig v0.11 (the jig boards' bus headers turned for a straight ribbon; v0.10 RV2 / RV10; v0.9 CS11: tests 13-17, output balance, line CMR, fader / pan residuals, faders-down noise,
  GCANCEL current; v0.8 strip v5.0: the CS1 overload checks, negative pulse / post-amp / gain stage / power-off; v0.7 strip v4.7: signal / OL LED checks; v0.6 strip v4.4; 4.2: the OPA1656 A/B for `docs/proposals/strip_noise_proposal.md` N1): 4 real strips with jack boards + master stub (A/D/22R-tie
  jumpers) + load board (dummy channels for 24-channel noise gain, 1 nF bus-capacitance jumpers); 11 bus
  tests and a per-strip function checklist with targets.
- `docs/studies/delta_clone_comparison.md` — the strip as a Delta Theatre input without the mic stage, stage by
  stage against the old strip; 7 decisions signed off 2026-10-22 (§3), now in spec v4.0 and the schematic.
- `console_architecture.md` — whole-console architecture, v3.2. Authoritative.
- `docs/reviews/project_review.md` (2026-10-28) — five-reviewer pass over the circuits, tooling, documentation and the repo, RV1-RV14.
  Applied 2026-10-28 (Ruslan, "continue" on the proposed split): RV1 (PSU R2 / R11 1206 0.5 W), RV2 option (a) and RV10
  (jig spec v0.10), RV11.1-7 (tool fixes, `check_bus.py`, +7 sim_console bus checks, check_all 71 checks), the §3 stale
  facts, the title-block revisions, `render/*.json` and the escape plan regenerated. RV3 / RV4 / RV7 / RV8 / RV9
  (`docs/proposals/clicks_proposal.md` + `.patch`, tools only) signed off and applied 2026-10-28 (strip v5.6, master v0.13; see
  Decisions). Open: RV5 / RV6 (accepted as is), RV12-RV14 (cleanup), RV11.8, the N1 order_bom EXTRA — all closed
  2026-10-28 but RV11.2's PFL-switcher check (applied 2026-11-11, `docs/verification_log.md`) and RV12's optional second step.
- `docs/reviews/delta_crosscheck.md` (2026-10-28) — every ED sheet of the Delta DLX service manual (17 pages at 300 dpi) against our
  schematics stage by stage: ~200 table rows (Delta as read / ours / SAME, RECORDED, UNRECORDED, N/A, UNREAD) in Parts
  A-D (strip, group + aux master, master, Venue / stereo / dual line); no fault in ours; 24 unrecorded items D1-D24, each
  with its reason, signed off by Ruslan 2026-10-28 as recommended: D1 insert jacks stay tip = send (the Delta: ring =
  send; documented), D13 applied (the spares grounded at the master, JP3-JP7, made last, placed by moves_only: master
  1806 pins / 625 parts, DRC 0, nothing else moved), D2-D12 / D14-D24 documentation (specs, `docs/studies/delta_clone_comparison.md`,
  `console_survey/delta.md`, `docs/proposals/clicks_proposal.md` RV5).
- `docs/reviews/schematic_readability_review.md` (2026-11-12) — all nine schematics (68 pages) read by eye on KiCad's own
  plot against the `readable-schematic` rules, with ERC (0 violations on all nine) and the skill's lint (689 errors,
  576 advisories, as leads). Seven findings SR1-SR7, all drawing only: five sheets with no wire (psu, jig load board,
  the three jack boards), the master's mute / PFL detect / flasher / meter current sources as chains of labels,
  fragments joined by labels in group and master, roots without pins and inter-sheet references off, strip spots,
  rail labels / sideways grounds / text on wires, two stale headings (master sheet 29 "1.85 A hold"). Applied so far:
  the PSU sheet of SR1, redrawn and signed off 2026-11-12 (`docs/verification_log.md`).
- `channel_strip_schematic_spec.md` — strip component-level spec, v5.6. Authoritative.
- `bom/channel_strip_BOM.csv`, `channel_strip.net`, `pdf/channel_strip.pdf` — exports.
