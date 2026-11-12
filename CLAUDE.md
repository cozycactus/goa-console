# goa-console — DIY 24+ channel line-level mixing console

Owner: Ruslan. Answer in the language he asks in (everything written into the repository stays English). Expert electronics hobbyist (KiCad, analog audio) — be technical, no hand-holding.
When you find a difference or propose a change, say clearly **why** you recommend it (the reason is the part to disagree
with).

## PCB scope
Component placement only. Ruslan does all copper routing in KiCad. Deliver no tracks,
vias or copper zones; do not autoroute, pour grounds or add stitching/escape vias.
Keep footprint pads and the net-tie's internal copper. See `AGENTS.md`.

## What this is
A Soundcraft-Delta-style console for mixing hardware synths (goa trance). Line level only. One identical main PCB per
channel (plus a small jack board), joined by a 34-way IDC ribbon "motherloom"; four 8 HP group modules and a 16 HP
master module on the same ribbon (M1); an external ±17 V PSU. A channel = a Soundcraft Delta Theatre input without the
mic stage: line gain, Ø, sweepable HPF, 4-band EQ, post-EQ insert, ON, PFL, aux 1-6 with PRE switches, pan + PAN
switch, routing, direct out. Everything is GENERATED from Python (schematics, placement, panels, drawings, 3D) and
checked by `tools/check_all.py`.

Where the detail lives (all moved out of this file on 2026-10-28, text unchanged):
- `docs/INDEX.md` — every file, what generates it, the proposals / reviews table (ID, sign-off, where it landed).
- `docs/tooling.md` — the verify loop, placer, footprints / 3D models, routing rules, route_check, check_all, fab_out.
- `docs/decisions.md` — every decision in full, with reasons, rejected alternatives and dates; `docs/decisions_summary.md` — the same decisions, one line each (read it before any design change).
- `docs/verification_log.md` — every check run after every change.
- `console_architecture.md` (v3.2), `channel_strip_schematic_spec.md` (v5.7), `master_section_spec.md` (v0.14),
  `test_jig_spec.md` (v0.11), `psu_spec.md` (v0.2) — authoritative specs. `routing_guide.md` for Ruslan's routing.
- `boards/<name>/` — each of the nine KiCad projects in its own folder (schematic, board, `.kicad_pro`, `.kicad_dru`, `.net`, `_intended.json`, `_parts.json`, its `*_sheets/` and the two lib tables); the project libraries (`goa-console.pretty`, `.3dshapes`, `.kicad_sym`) stay in the root, reached as `${KIPRJMOD}/../../`. Tools are run from the repository root.
- `docs/proposals/`, `docs/reviews/`, `docs/studies/`, `docs/build/` — the design record (out of the root since 2026-11-09; the live specs above stay there with the KiCad projects). `bom/` — BOM exports and order lists. `pdf/` — schematic PDFs.

## Current state (2026-11-04)

| Board | Rev | Parts | Pins | Outline (mm) | Layers | Placement |
|---|---|---|---|---|---|---|
| `channel_strip` (×24) | strip v5.7 | 329 + 6 holes | 946 | 38 × 400 (y 44–444) | 4 | done |
| `jack_board` (×24) | " | 8 | 32 | 38 × 43 (y 0–43) | 2 | done |
| `group` (×4) | rev 0.12 + CS2b / CS4b / CS4c / CS6 / CS10 / RV7 | 292 + 6 | 807 | 38 × 349.5 (y 94.5–444) | 4 | done |
| `group_jack_board` (×4) | " | 11 | 60 | 38 × 93.5 | 2 | done |
| `master` | master v0.14 | 632 + 7 | 1820 | 78.6 × 331.5 (y 112.5–444) | 4 | done |
| `master_jack_board` | " | 16 | 92 | 78.6 × 111.5 | 2 | done |
| `jig_master_stub` | jig v0.11 | 144 + 4 | 365 | 160 × 125 | 2 | done |
| `jig_load_board` | " | 50 + 4 | 153 | 120 × 85 | 2 | done |
| `psu` | PSU v0.2 + RV1 | 52 + 4 | 119 | 120 × 60 | 2 | done |

Every board is its schematic's project board, so parity DRC runs in place; all nine: 0 DRC violations (jack boards
only the NJ6FD-V footprint's own items), 0 parity issues, every footprint linked to its symbol (1534 / 1534).
Last `check_all.py --full`: 72 / 72 on macOS 2026-11-11 (KiCad 10.0.7, ngspice 46; Linux runs stop one short, panel_fab
needs the macOS Arial Narrow). sim_netlist 45/45, sim_console 108/108, check_bus clean.

Power: console ~3.31 / 2.79 A typical, worst corner ~4.54 A on +V against the PSU's 4 A per rail, wing PTC ~2.07 A
(accepted, master spec §27). Routing: not started (Ruslan). Panels: quotes and a prototype strip panel pending.

## How to work

Regenerate + verify loop (KiCad 10.0.7; `KC=kicad-cli KPY=python3` on Linux, the app paths on macOS; `.venv` = kiutils
1.4.8; details and every other tool in `docs/tooling.md`):
```
.venv/bin/python tools/gen.py boards/channel_strip/channel_strip.kicad_sch        # strip + jack board; gen_master.py boards/master/master.kicad_sch,
                                                             # gen_group.py boards/group/group.kicad_sch, gen_psu.py, gen_jig.py
$KC sch export netlist -o boards/channel_strip/channel_strip.net boards/channel_strip/channel_strip.kicad_sch
.venv/bin/python tools/verify.py boards/channel_strip/channel_strip.net boards/channel_strip/channel_strip_intended.json
python3 tools/check_fp.py boards/channel_strip/channel_strip.net
$KC sch erc --severity-all boards/channel_strip/channel_strip.kicad_sch
$KC sch export pdf -o pdf/channel_strip.pdf boards/channel_strip/channel_strip.kicad_sch      # + the BOM export line in docs/tooling.md
$KPY tools/place_strip.py boards/channel_strip/channel_strip.net boards/channel_strip/channel_strip.kicad_pcb  # place_group.py, place_master.py (~3 min),
                                                                     # place_jig.py, place_psu.py; refuses a routed board
$KPY tools/netrules.py channel_strip                                 # after any re-placement or netlist change
python3 tools/check_all.py --full                                    # every check, tracked files untouched; exit 1 on FAIL
python3 tools/order_bom.py && python3 tools/order_bom.py phase1 && python3 tools/order_bom.py stagea   # after any BOM export
$KPY tools/freespot.py boards/master/master.kicad_pcb Resistor_SMD:R_0805_2012Metric B 90 X Y  # free spot for a part made last
python3 tools/placediff.py boards/master/master.kicad_pcb                          # vs HEAD: must list only the new parts
```
Fab: `python3 tools/fab_out.py BOARD` (Gerbers, drills, CPL, BOM; refuses on DRC / route_check). Drawings: `tools/panel_fab.py`
(`panels/`, macOS fonts), `frame_fab.py`, `tub_fab.py`, `psu_case_fab.py`. 3D: `tools/export_3d.py` → `render/*.json`,
`tools/console_3d.py` (Blender 5.2). Escape plan: `tools/escape_plan.py` → `docs/escape/`.

## Rules
- Generated files are never hand-edited: schematics (`gen*.py`, netlist in the `P(...)` calls, drawings in
  `strip_draw.py` / `frags.py`), boards (`place_*.py`), footprints (`footprints.py`), panels, drawings, `order_*.csv`.
- A change goes proposal (with the reason and the simulation) → Ruslan's sign-off → apply → record, **once** (since
  2026-11-11; before, each change was written up in five to seven places): one dated entry in `docs/decisions.md` with
  the decision, the reason, what was rejected and the check results (placement diff, DRC, `check_all` count). Elsewhere
  only what the change makes untrue: the spec's text at the fact that changed (a circuit change also gets its line in
  the spec's "Changes" block with the new revision), a line in `docs/decisions_summary.md` for a standing decision,
  the state table above when its numbers change. `docs/verification_log.md` is for check runs that belong to no
  decision (a re-run, a tool fix). No second account of the same change anywhere.
- New parts are created LAST in the generator (so no existing reference moves) and placed by the placer's `moves_only`
  at probed spots (so no existing part moves); check with a placement diff that only the new parts changed.
- After any generator, placement or rule change: regenerate, `check_all.py --full`, `netrules.py`, `order_bom.py`.
- Power the console down before plugging or unplugging a module (the fusible R1-R4 can open on a live plug).
- No phantom power on any balanced output, insert send or direct out (BAV199 clamps limit the damage, the rule stays).
- Repository: public (`cozycactus/goa-console`, CERN-OHL-S-2.0). `ref/` stays on disk, git-ignored: never commit it. Commit with the GitHub noreply address.
- Decisions are one line each in `docs/decisions_summary.md`; the full text with the reasons is `docs/decisions.md`. Do not silently change one.
- Keeping sessions cheap (2026-11-11, Ruslan): one topic per session (when a request starts a new topic, say so and
  offer a new session instead of growing this one); check with numbers before pictures (an assert or a measured value in
  the script; render and look only at what Ruslan will see or asked for, as small previews; he looks at the pictures
  himself and says what is wrong); send long tool output to a log and read only the result lines; one record per change
  (above).

## Decisions made (do not silently change)
One line per decision, by area (architecture and bus, strip circuit, master and group, power, mechanics and panels,
placement, repository): `docs/decisions_summary.md` (moved out of this file on 2026-11-11, text unchanged; this file is
loaded into every session, the list was 11.5 KB of it). Full text with reasons and rejected alternatives: `docs/decisions.md`.
**Read `docs/decisions_summary.md` before proposing or making any change to a circuit, a part, a placement, the
mechanics or a rule.** A question, a drawing or a check run doesn't need it. Do not silently change a decision.

## Not done / open
- Sample checks before ordering boards (`docs/build/sample_order.md`, spec 16.1): PVA2 orientation by continuity, fader pad pattern on a 1:1 print and its ground end by continuity, the Alpha pots' tab slots on a 1:1 print (KiCad's are turned 90° from Alpha's PCB detail), the NJ6FD-V's peg (3.18 vs 3.81 mm off the axis) and its TN / RN / SN pads on a 1:1 print and by continuity, the Sifam cap on the BP blade, knob fit on the 6.35 mm centre-notch pots, RV8's M9 nut / pin 1 / detent, panel stack height, the fader's law (before the panels are printed: the "0" marks and the printed scale depend on it) and its bottom-stop residual (CS9). What to keep clear or swappable while routing before these checks: `routing_guide.md`, "Provisional areas".
- Group jack-board links (10-way CN2 → CN4, 16-way CN1 → CN3): straight since 2026-11-11, all four headers across (`docs/decisions.md`). Still open: both cables have not been tried together on real boards (the 10-way under the 16-way's two sockets; cut about 160 / 200 mm with ~10 mm of slack, a taut 16-way bears on C14 / C20); `console_3d.py` draws the straight runs but not the dip under each socket (console renders and `goa_console.blend` rebuilt 2026-11-12 with the straight links).
- Front panels: Ruslan is getting quotes and a prototype strip panel (`docs/build/panel_makers.md`); if the maker's minimum printed line is above ~0.11 mm, switch the small text to Arial Narrow Bold in `panel_layout.py` and regenerate `panels/`. At that regeneration add the "INSERT tip = send" legend (D1) to the strip, group and master panels (`panel_layout.py`, `docs/build/panel_print.md`).
- Bench, with the jig (`test_jig_spec.md`): every relay releases when the −V wire is opened with the relays closed (RV9b), mute depth (CS8), N1 OPA1656 A/B (one-strip swap), re-inverter stability (test 10), aux noise at N = 24, relay release and mains-off fall rate with the real PSU, PFL tick with programme, meter current-source temperature and LED brightness, hum with a real synth on TS / TRS, an earthed processor on the insert (D21), panel-to-frame bonding, output balance / CMR / fader breakthrough / GCANCEL current (CS11, tests 13-17), E7 ferrites.
- Accepted as they are: RV5 (MUTEOUT's DC on the fader top; the Delta's cap-isolated shunt source is the fallback), RV6 (U16 clips at +21.9 dBu input), the 4.54 A worst corner, the earthed-TS-synth hum (pseudo-balanced cables, one mains distribution point).
- PSU: routing (Ruslan) and the case build. Routing of every board is Ruslan's; `routing_guide.md`, `netrules.py` rules, `route_check.py` afterwards, then `fab_out.py`.
- TI-model stability (TI's models are not in the repo: `sim/review/master/models/`, gitignored, or `$TI_MODELS` / `$OPA161X_LIB`),
  re-run 2026-11-03 / 04. Strip v5.7, 21 states, U16 on TI's real OPA1656 since 2026-11-04 (`.options itl1=500`): worst U3B 59.8 deg, U16 61.7, <= 1.61 dB peaking, U1B >= 84.6 deg, all as v5.5
  (R142 1M doesn't show); N1 on TI's real model: every N1 unit >= 58.2 deg, <= 1.84 dB (the fitted macro read 50.1), so only distortion is left for the A/B (`docs/proposals/strip_noise_proposal.md`). Master v0.14, all 34 configurations of `sim/review/master/run_each.py`: worst U21A/B 47.7 deg at the pot top, every
  unit's minimum as before, <= 2.89 dB peaking; the `_placed` runs saw the re-measured trace table for the first time (U13A -5 deg
  with A5_OUT at 98 mm, still >= 69.1). The phones loop, run separately: U26 75.9-83.0 deg, within 0.1 deg of before. The deck used
  to read old raw files when ngspice timed out (fixed 2026-11-03), so the 2026-10-29 master re-run was only part-simulated
  (`docs/reviews/met1_ret1_review.md`). Group, 222 states on TI's real OPA161x + OPA1656 (`.options itl1=500`), re-run 2026-11-11 on the board with the straight links, trace table
  re-measured: followers 59.5-60.3 deg, unstressed worst U1B 56.8 deg (ferrite shorted), 45.8 deg with +47 pF (U8B, its output runs 98 mm to C55; U6B 46.1), <= 2.99 dB; the DRV135 loops are not in the deck.
- Ordering stage A: `bom/order_stage_a.csv` (every line, by vendor) and `bom/order_stage_a_mouser.csv` (Mouser's BOM upload), from `python3 tools/order_bom.py stagea` and the readings in `bom/mouser_readings.csv` (2026-11-04); about $435 + $70.50 PCBs. Unread lines (7 thin-film values, the ceramics, 3 RC0805s) show live in the upload. Later list: 4 PVA2 H1 samples (2027-03-01), 4 WP710A10GD (2026-12-07).

## Next steps
1. Order the samples (`docs/build/sample_order.md`) and the prototype panel; do the sample checks; measure the fader law.
2. Ruslan routes the strip main board and jack board first (`routing_guide.md`, `docs/build/escape_plan.md`); `route_check.py`;
   `fab_out.py channel_strip`; stage A of `test_jig_spec.md` §1.1 (one strip on a bench supply, `bom/order_phase1.csv`).
3. Then the jig stub and load board (stage B), the group, the master and the PSU; the bench list above.
4. Panels in a batch after the fader law is measured; frame, tub and PSU case from their drawings.

## Reference material
In `ref/` (git-ignored, on disk only; third-party copyright): Delta DLX/Theatre schematics (`Sndcft_DeltaDLX_Schems.pdf`, the ED drawings), Soundcraft 200 Delta
Technical Manual ZZ2593 (`Soundcraft_200Delta_TechManual_ZZ2593_Part1-3.pdf`) and User Guide
(`Soundcraft_200Delta_UserGuide.pdf`, front-panel drawings of every module, cropped at 300 dpi into `ref/delta200_panels/`:
the legend style for our panels), both scanned, no text layer. Manual: specs,
circuit descriptions, jumper settings, connector and loom pinouts p. 129-135, spare-parts lists p. 151-162 (Part3 PDF pages 10-21; every resistor "MF 0.25W RES 2%", routing "MINI-RES MF 1/2W 5%"; the Delta's
fader is an ALPS 10K 100 mm mono with a "SIF low profile" knob; 14 mm push-on knobs, M7 nuts, 16 mm pots),
dimensions p. 114), Mackie 1604-VLZ block diagram, API 500 spec. Ask Ruslan for other PDFs if needed.
`docs/reviews/delta_crosscheck.md` (2026-10-28) is the sheet-by-sheet comparison of every ED drawing with our schematics; the
service-manual library of the other consoles (ten, the Downloads batch, and since 2026-11-12 the DDA AMR 24) is in
`docs/studies/console_survey.md` / `docs/console_survey/`.
