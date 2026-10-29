# goa-console — DIY 24+ channel line-level mixing console

Owner: Ruslan. Answer in English. Expert electronics hobbyist (KiCad, analog audio) — be technical, no hand-holding.
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
- `docs/decisions.md` — every decision in full, with reasons, rejected alternatives and dates.
- `docs/verification_log.md` — every check run after every change.
- `console_architecture.md` (v3.2), `channel_strip_schematic_spec.md` (v5.6), `master_section_spec.md` (v0.13),
  `test_jig_spec.md` (v0.10), `psu_spec.md` (v0.2) — authoritative specs. `routing_guide.md` for Ruslan's routing.

## Current state (2026-10-28)

| Board | Rev | Parts | Pins | Outline (mm) | Layers | Placement |
|---|---|---|---|---|---|---|
| `channel_strip` (×24) | strip v5.6 | 327 + 6 holes | 941 | 38 × 400 (y 44–444) | 4 | done |
| `jack_board` (×24) | " | 8 | 32 | 38 × 43 (y 0–43) | 2 | done |
| `group` (×4) | rev 0.12 + CS2b / CS4b / CS4c / CS6 / CS10 / RV7 | 292 + 6 | 807 | 38 × 349.5 (y 94.5–444) | 4 | done |
| `group_jack_board` (×4) | " | 11 | 60 | 38 × 93.5 | 2 | done |
| `master` | master v0.13 | 631 + 7 | 1818 | 78.6 × 331.5 (y 112.5–444) | 4 | done |
| `master_jack_board` | " | 16 | 92 | 78.6 × 111.5 | 2 | done |
| `jig_master_stub` | jig v0.10 | 144 + 4 | 365 | 160 × 125 | 2 | done |
| `jig_load_board` | " | 50 + 4 | 153 | 120 × 85 | 2 | done |
| `psu` | PSU v0.2 + RV1 | 52 + 4 | 119 | 120 × 60 | 2 | done |

Every board is its schematic's project board, so parity DRC runs in place; all nine: 0 DRC violations (jack boards
only the NJ6FD-V footprint's own items), 0 parity issues, every footprint linked to its symbol (1531 / 1531).
Last `check_all.py --full`: 70 / 71 on Linux 2026-10-28 (71 checks since RV11.2; the one failure is panel_fab, which
needs the macOS Arial Narrow; the last macOS run, before RV11.2, was 61 / 61). sim_netlist 45/45, sim_console 45/45, check_bus clean.

Power: console ~3.31 / 2.79 A typical, worst corner ~4.54 A on +V against the PSU's 4 A per rail, wing PTC ~2.07 A
(accepted, master spec §27). Routing: not started (Ruslan). Panels: quotes and a prototype strip panel pending.

## How to work

Regenerate + verify loop (KiCad 10.0.7; `KC=kicad-cli KPY=python3` on Linux, the app paths on macOS; `.venv` = kiutils
1.4.8; details and every other tool in `docs/tooling.md`):
```
.venv/bin/python tools/gen.py channel_strip.kicad_sch        # strip + jack board; gen_master.py master.kicad_sch,
                                                             # gen_group.py group.kicad_sch, gen_psu.py, gen_jig.py
$KC sch export netlist -o channel_strip.net channel_strip.kicad_sch
.venv/bin/python tools/verify.py channel_strip.net channel_strip_intended.json
python3 tools/check_fp.py channel_strip.net
$KC sch erc --severity-all channel_strip.kicad_sch
$KC sch export pdf -o channel_strip.pdf channel_strip.kicad_sch      # + the BOM export line in docs/tooling.md
$KPY tools/place_strip.py channel_strip.net channel_strip.kicad_pcb  # place_group.py, place_master.py (~3 min),
                                                                     # place_jig.py, place_psu.py; refuses a routed board
$KPY tools/netrules.py channel_strip                                 # after any re-placement or netlist change
python3 tools/check_all.py --full                                    # every check, tracked files untouched; exit 1 on FAIL
python3 tools/order_bom.py && python3 tools/order_bom.py phase1      # after any BOM export
```
Fab: `python3 tools/fab_out.py BOARD` (Gerbers, drills, CPL, BOM; refuses on DRC / route_check). Drawings: `tools/panel_fab.py`
(`panels/`, macOS fonts), `frame_fab.py`, `tub_fab.py`, `psu_case_fab.py`. 3D: `tools/export_3d.py` → `render/*.json`,
`tools/console_3d.py` (Blender 5.2). Escape plan: `tools/escape_plan.py` → `docs/escape/`.

## Rules
- Generated files are never hand-edited: schematics (`gen*.py`, netlist in the `P(...)` calls, drawings in
  `strip_draw.py` / `frags.py`), boards (`place_*.py`), footprints (`footprints.py`), panels, drawings, `order_*.csv`.
- A change goes proposal (with the reason and the simulation) → Ruslan's sign-off → apply → record (spec "Changes"
  block, the decision line below, `docs/decisions.md`, `docs/verification_log.md`, the state table above).
- New parts are created LAST in the generator (so no existing reference moves) and placed by the placer's `moves_only`
  at probed spots (so no existing part moves); check with a placement diff that only the new parts changed.
- After any generator, placement or rule change: regenerate, `check_all.py --full`, `netrules.py`, `order_bom.py`.
- Power the console down before plugging or unplugging a module (the fusible R1-R4 can open on a live plug).
- No phantom power on any balanced output, insert send or direct out (BAV199 clamps limit the damage, the rule stays).
- Decisions below are one line each; the full text with the reasons is `docs/decisions.md`. Do not silently change one.

## Decisions made (do not silently change)
**Architecture and bus**
- Delta Theatre input without the mic stage (2026-10-22, `delta_clone_comparison.md` §3): receiver + separate inverting gain stage −15…+15 dB, Ø, HPF, Delta EQ, EQ IN, post-EQ insert (jumper pre-EQ), ON, PAN switch, routing LEDs, PRE per aux pair, DIR; internal level 0 dBu; 4K7 summing.
- Master section = modules M1 (2026-10-22): 4 × 8 HP group modules (sub n, aux n master, returns n) + 16 HP master; `master_panel_study.md`.
- One 34-pin header per strip on a daisy-chained ribbon with crimped IDC sockets (2026-10-19); CN2 dropped.
- Bus pinout = the Delta motherloom ED3344C (SUB1-4 on 15/13/11/9, MIX R 17, MIX L 18 — ED3344C order kept over the manual's, 2026-10-23 —, AUX6..1 on 20-25, GCANCEL 26, PFL 27, PFL DET 29, −V 30-31, +V 32-34 since W1, even 2-16 GND). Pins 1/3/5/7 reserved for SUB 5-8 and 19 spare: unconnected on every module, grounded at the master through bridged jumpers JP3-JP7 (D13, 2026-10-28; open them for 8 groups). Pin 28 open everywhere (D22 / D24).
- Ground cancel: 10R from module AGND to pin 26, master summers reference it, each followed by a unity differential re-inverter; no master-end tie, a 100K keeper only (2026-10-19 / 23). SSL-style impedance-balanced bus dropped.
- Summing resistors 4K7 MIX / SUB (master feedback 4K7), 22K AUX / PFL; master sums invert and re-invert once; channel path non-inverting (tip = hot).
- Routing (2026-10-22): PVA2 keys carry logic only, DG413 U9-U11 at the bus header move each 4K7's bus end between bus and AGND; off = clean ground; yellow LED per key; +5VL from +VA via 4K7 + BZX84C5V1 (+ BAT54W D10).
- 4 subs with inserts, 6 aux (AFL), 8 stereo returns (two per group, RET1 2026-10-26), PFL only (no SIP), relay mute on the mains; C/Room DIM −20 dB (CS7, 2026-10-28, reverses the architecture's exclusion).
- Insert jacks tip = send, ring = return console-wide (D1, 2026-10-28; the Delta is ring = send).
- SSL bus compressor (Gyraf clone) external on the master insert; VCAs SSI2162 (THAT 2180 EOL), also the strip's plug-in VCA option (2026-10-19).

**Strip circuit (spec `channel_strip_schematic_spec.md`, "Changes" blocks)**
- Mid bands: KHN state-variable band-pass tuned by Alpha A10K duals as dividers, not the Delta's 100K C-law Wien; since EQM1 (2026-10-28) HI-MID 392R / 13K / 4K99 (598 Hz-9.93 kHz), LO-MID 430R / 13K / 4K22 (165 Hz-2.54 kHz); OPA1612; A10K not A100K (noise).
- Sweepable HPF H1-H4 (2026-10-24): KHN high-pass 21-403 Hz, unity, Q 0.707, RV16 A10K dual into U15, U5A summer, SW11 HP / HIN, C91; wing −V PTC MF-RX185/72 (H4).
- Fader post-amp +10 dB (R38 2K2); AC coupling 100 µF NP + 47K on every bus-feeding node; J112 soft mute (two shunts, not the Delta's series + shunt, D3); logic rails ±VL / GNDD joined to GNDA at NT1.
- Film couplers and bipolars F1-F4 (2026-10-24): WIMA MKS2 2.2 µF (wipers, meter averaging; THT, bottom side), MUSE ES 33 / 100 µF, 10 µF Panasonic ECE-A1EN100U (S1); no X7R in the signal path, no DC coupling, no polypropylene.
- Op-amps: OPA1612 in noise-critical stages and on the MIX / SUB / aux sums; OPA1656 on the PFL sum, the CRS followers and the input followers (G3, U16); N1 (OPA1656 in U1, U5-U7, U12-U15) open, decided by the jig A/B.
- Pan law CS2 Option A (2026-10-27): the Delta's −4.4 dB (U8B / U3A 1.22× with 3K3 back to the wipers, C105 / C106 22p); PAN off stays POST; the group's sub pan the same (CS2b, 2026-10-28). The old −6 dB was a transfer error.
- v4.1 T1-T11 stability caps and ratings (2026-10-23); v4.5 K1 / K3 (PFL DC block C96, ~150 ms OL hold); v4.7 MET1 red / green bicolour signal / OL LED D2 WP3VEGW; v4.8 PAN1 pan buffer L in U8B; v4.9 P1 / P2 / E6; v5.0 CS1 five-tap OL detector, both polarities, thresholds ratios of +VL (+18.4 dBu); v5.1 CS10 PMEG4010CEH across each audio rail (strip D16 / D17, group D5 / D6); v5.2 CS4 BAV199 on every jack-link signal at CN3 (TVS rejected); v5.3 CS6 fusible R1-R4 Vishay M25SI (strip and group); v5.4 CS2; v5.5 EQM1; v5.6 RV3 / RV4 (R142 1M gain-stage keeper, C107 33 µF in the direct out's cold leg).
- Design review (2026-10-25): ON also mutes the pre-fade sends and the direct out, PFL stays at PRE (Q1); group sub pan RV2 = RK09L; jig R45 ERJ-P06J332V; silk "2" at every PVA2's pads 1 / 4.
- Ground and hum G1-G3, G2b / G3b (2026-10-25): one 14 AWG wire per module to the master's copper bar under the M4 star (G1); balanced-input and DRV135 TRS sleeves on CHASSIS through plated standoffs, inserts / phones on GNDA (G2); receivers buffered by OPA1656 followers, 1M / 220R / 100 pF / 100R (G3); XLR shells on CHASSIS (2026-10-28).

**Master and group (spec `master_section_spec.md`)**
- Balanced outputs TI DRV135UA (DRV134 family, SO-8; THAT1646 EOL 2026-09-01), 10 µF NP per leg inside the Sense loop, 22R in-loop (CS4c), coupler pairs sorted within 2 % (CS11b), mute relay after; no phantom on any balanced output.
- Master parts S1-S8 (2026-10-23): six G6K-2F-Y mute relays (COM = connector, NO = driver, NC = ground), LM393B, one DG413 PFL switcher, OPA1656 CRS followers, PFLDET clamp (2 × 1N4148, 330K reference, 1 µF debounce), LM2901B meters with BCP53-16 / 120R current sources and Kingbright GaP / GaAsP LEDs, sub AFL kept, GCANCEL buffer kept.
- MG1-MG20 (2026-10-24): EXT_BL / BR + 100R; build-outs at the op-amp pins (solo 100R, post-amps 47R, CRS 100R, insert return 75R, meter DET 470R); C0G at the + inputs; insert returns 1K + 100p; TL072HIDR meter detector reading the diode cathode; 50 V X7R / C0G, anti-surge where rated; one SUB and one AUX bus jumper per group board.
- Master v0.13 RV7-RV9 (2026-10-28): 2.2 µF films ahead of the AFL 22Ks (master C194 / C195, group C98), phones gain-set 33 µF NP C196 / C197 (DC gain 1), U10B's + input on +1.0 V (R238 / R239) with R53 64K9.
- Jack-link clamps CS4b (group 14, master 24 BAV199) and loop resistors CS4c (group R119-R122, master R222-R235), made last (2026-10-27).
- Pan pot RV8 and group RV2: ALPS RK09L1240015 (M9 bushing, 6 mm D shaft, Ø9.5 hole, centre detent), 2026-10-25.

**Power**
- PSU option B (2026-10-22, `psu_spec.md` v0.2): two LRS-150-24 at 21.6 V → 10 µH / 2200 µF → LM1084-ADJ 17.0 V floating rails, TL431 + PNP + 2N6505G crowbar at 19.1 V, 4 A per rail; ADJ divider R2 / R11 ERJ-P06F1501V 1206 0.5 W (RV1, 2026-10-28). Case PC1-PC3: Hammond 1402KV, Fischer SK 47 75 SA on the front panel, Schurter DD11, NC7FD-LX (2026-10-26).
- Budget: ~3.31 / 2.79 A typical, worst corner ~4.54 A on +V accepted (the chain 4.0 → 4.24 → 4.33 → 4.38 → 4.54 A, master spec §27); inlet NC7MD-LX, two 5 A contacts per rail; wing PTCs +V MF-RX250/72 (W2) on three conductors, −V MF-RX185/72 (jig stub still MF-RX160/72).

**Mechanics and panels**
- Strip panel 8 HP × 12U, two pot columns at x 8.84 / 29.16 (20.32 pitch, 2026-10-23), jacks on the panel (NJ6FD-V) on a 38 × 43 mm jack board 24.0 mm under it, 2×5 IDC link; knobs Ø14.5; custom frame with rails only at the panel ends (2026-10-22).
- Faders Bourns PTB0143 (strips, groups) / PTB0144 (master) A10K, BP blade; caps Sifam LK111 01 black with a line (KC2); the AP / ALPS / TT / P+G alternatives rejected (2026-10-23 / 25).
- Knobs KN1-KN3 (2026-10-25): Elma 021-3525 (1/4") / 021-3425 (6 mm) matt black with a line, Elma 040-30x5 caps colour-coded per function; key caps C&K PV (KC1).
- Panel parts: Alpha RD901F / RD902F pots (centre-detent 10K B have 1/4" shafts), C&K PVA2 EE H1 keys fitted with the moulded "2" in the pad 1 / 4 column, Keystone 1287-ST spade, 3 mm LEDs on 7.6 mm spacers.
- Frame rails FR1-FR3 (2026-10-25): two 6060-T6 / 6082 bars 50 × 10 × 1227.2 mm, 30 M3 tapped holes each, bonded by bare holes + star washers, one 2.5 mm² bond per rail to the M4 star (`frame/`).
- Tub TB1-TB4 (2026-10-26): walnut cheeks carrying the 9° tilt, 12 mm birch-ply floor with 30 inlet slots + mesh, walnut arm-rest, back plenum with the NC7MD-LX, open underside, console raised 25 mm (`tub/`); supply cable through back-rail vent slot 14.
- Thermal TH1-TH3 (2026-10-26): 98 W; vented tub ~16 K rise, back rail's 30 vent slots 30 × 25, no fan unless the built console exceeds 20 K; MUSE ES kept.
- P4 (2026-10-27): welded blind M3 studs on the panel backs if the maker offers them, else the main-board standoffs are spacers; countersunk M3 + star washers at the jack boards.
- Board layers (2026-10-27, `layer_study.md`): strip, group and master mains 4-layer (In1 solid GNDA plane, In2 GNDA fill with the rails / GNDD only in the left-edge RAILS corridor), every other board 2-layer; JLCPCB +$93 for the console.

**Placement (placement only; Ruslan routes)**
- E1-E5 / E8 (2026-10-26) and E6: LED switches beside D2, the J112 mute and U16's network under their op-amps, supply filters at the bus header, jack-board C8 / C9 between J1's pins, master flasher diode and PFL detect by their ICs; E9 / E9b stability caps ≤ 6.4 mm from their pins; E10 input nets shortened; E11 decouplers ≤ 5.5 mm (THT 10 µF excepted); untangle turns (crossings −4..−7 %); upper strip op-amps fixed in `place_strip.py`.
- Routing rules by `tools/netrules.py` into every project (net classes, HighZ / Entry / Bus clearances, 4-layer rules, WingFeed, PSU HighCurrent); `routing_guide.md`; `route_check.py` after routing.
- Sourcing (2026-10-25): plain 0805 Yageo RC0805FR-07xxxL; stock risks PTB0143, NJ6FD-V, OPA1612, WIMA 2.2 µF; C0G order codes by footprint; DRV135 coupler pairs sorted (10 spares).

## Not done / open
- Sample checks before ordering boards (`sample_order.md`, spec 16.1): PVA2 orientation by continuity, fader pad pattern on a 1:1 print, the Sifam cap on the BP blade, knob fit on the 6.35 mm centre-notch pots, RV8's M9 nut / pin 1 / detent, panel stack height, the fader's law (before the panels are printed: the "0" marks and the printed scale depend on it) and its bottom-stop residual (CS9).
- Front panels: Ruslan is getting quotes and a prototype strip panel (`panel_makers.md`); if the maker's minimum printed line is above ~0.11 mm, switch the small text to Arial Narrow Bold in `panel_layout.py` and regenerate `panels/`. At that regeneration add the "INSERT tip = send" legend (D1) to the strip, group and master panels (`panel_layout.py`, `panel_print.md`).
- Bench, with the jig (`test_jig_spec.md`): mute depth (CS8), N1 OPA1656 A/B (one-strip swap), re-inverter stability (test 10), aux noise at N = 24, relay release and mains-off fall rate with the real PSU, PFL tick with programme, meter current-source temperature and LED brightness, hum with a real synth on TS / TRS, an earthed processor on the insert (D21), panel-to-frame bonding, output balance / CMR / fader breakthrough / GCANCEL current (CS11, tests 13-17), E7 ferrites.
- Accepted as they are: RV5 (MUTEOUT's DC on the fader top; the Delta's cap-isolated shunt source is the fallback), RV6 (U16 clips at +21.9 dBu input), the 4.54 A worst corner, the earthed-TS-synth hum (pseudo-balanced cables, one mains distribution point).
- PSU: routing (Ruslan) and the case build. Routing of every board is Ruslan's; `routing_guide.md`, `netrules.py` rules, `route_check.py` afterwards, then `fab_out.py`.
- `project_review.md`: everything applied but RV11.2's PFL switcher from the PFLDET net (needs a DC analysis of the detect line; `check_bus.py` covers pin 29) and RV12's optional second step (the ~40 proposal / study `.md` files into `docs/`, a scripted rewrite of ~280 references).

## Next steps
1. Order the samples (`sample_order.md`) and the prototype panel; do the sample checks; measure the fader law.
2. Ruslan routes the strip main board and jack board first (`routing_guide.md`, `escape_plan.md`); `route_check.py`;
   `fab_out.py channel_strip`; stage A of `test_jig_spec.md` §1.1 (one strip on a bench supply, `order_phase1.csv`).
3. Then the jig stub and load board (stage B), the group, the master and the PSU; the bench list above.
4. Panels in a batch after the fader law is measured; frame, tub and PSU case from their drawings.

## Reference material
In `ref/`: Delta DLX/Theatre schematics (`Sndcft_DeltaDLX_Schems.pdf`, the ED drawings), Soundcraft 200 Delta
Technical Manual ZZ2593 (`Soundcraft_200Delta_TechManual_ZZ2593_Part1-3.pdf`) and User Guide
(`Soundcraft_200Delta_UserGuide.pdf`, front-panel drawings of every module, cropped at 300 dpi into `ref/delta200_panels/`:
the legend style for our panels), both scanned, no text layer. Manual: specs,
circuit descriptions, jumper settings, connector and loom pinouts p. 129-135, spare-parts lists p. 151-162 (the Delta's
fader is an ALPS 10K 100 mm mono with a "SIF low profile" knob; 14 mm push-on knobs, M7 nuts, 16 mm pots),
dimensions p. 114), Mackie 1604-VLZ block diagram, API 500 spec. Ask Ruslan for other PDFs if needed.
`delta_crosscheck.md` (2026-10-28) is the sheet-by-sheet comparison of every ED drawing with our schematics; the
service-manual library of ten other consoles is in `console_survey.md` / `docs/console_survey/`.
