# goa-console — verification log

Moved out of `CLAUDE.md` on 2026-10-28 (`project_review.md` RV13), text unchanged: every check run after a change, newest
first. The current counts are in `CLAUDE.md`'s state table.

- Strip TI stability on the real OPA1656 (2026-11-04, ngspice 46, strip v5.7, 21 states, `n1_stab.py`): as built 504 / 504 results, worst U3B 59.8 deg, U16 61.7, <= 1.61 dB;
  c01 with U16 as OPA161x matches `results_none.json` to the digit on the units sampled. N1: 17 states full, 4 (`c07`, `c09`, `c10`, `c14`) with U2 / U3 / U8 single-pole, checked on c01:
  18 OPA1656 units identical to the full run. Every N1 unit >= 58.2 deg, <= 1.84 dB. U2 / U3 / U8 aren't measured under N1 in those four states (`strip_noise_proposal.md`).
- Group TI stability, whole deck (2026-11-04, ngspice 46): `pots` / `ret` / `loads` / `ins` / `bus`, 222 states, 1835 unit results, none
  without data, TI's OPA161x + OPA1656 together for the first time (`.options itl1=500`), `mst_all.json` re-measured from the placed
  board, 0.08 pF/mm. Worst 59.7 / 59.1 / 46.1 / 65.3 / 56.8 deg; followers 59.1-60.9; peaking <= 2.76 dB (`met1_ret1_review.md`). Deck test: planted
  old raw files give no result; no dangling node but the unused rails and the DRV135 outputs.
- SS1-SS3 applied (2026-11-04, `second_source_proposal.md`): every board regenerated and re-placed, `placediff.py` 0 changed on all
  nine. Fields only: strip 12 parts, group 2, master 1, PSU 4; values only on strip D16 / D17 and group D5 / D6 (MBR140SFT1G); the jack
  boards and jig differ only by dates and UUIDs (restored). `order_bom.csv` and `order_phase1.csv` carry no old code; phase 1 has
  14 + 14 PVA2 EE H3 and 4 H1 samples, the console 371 H1. `rail_loss.py mbr` ±0.36 V, 0 mA. `check_all.py --full` 72 / 72.
- Master TI stability, whole deck on v0.14 (2026-11-03 / 04, ngspice 46, TI's OPA161x / OPA1656 / DRV134 / TL072 models, 34
  configurations): the first pass read old raw files on 17 configurations when ngspice timed out, found because all 34 result files
  came out byte-identical to the previous run's. `mstab.py` fixed (e112981; test: a planted old result now gives no result, `p075`
  reaches the fallback options), those 17 re-run. All 1360 unit results come from raw files written during the run, none without
  data. Worst U21A/B 47.7 deg, every unit's minimum unchanged, <= 2.89 dB peaking; 29 configurations identical to the earlier
  figures, the five `_placed` move up to -5.1 deg (U13A, A5_OUT 98 mm, >= 69.1). The 2026-10-29 re-run had 14 of 34 configurations
  timed out (`met1_ret1_review.md`).
- SW4's silk mark and the project files' top-level sheets (2026-11-03): every board regenerated and re-placed. Only the master
  board changed: a silk "2" at (25.06, 178), the fourth on that board; the other eight identical but for UUIDs and file order.
  Seven project files changed only in `top_level_sheets`; fresh netlists on the flat boards now read their own sheet name, not
  "Root". `check_all.py --full` 72 / 72 with the new project-file check.
- Merge of the review branch (strip v5.7, master v0.14, TF1) with main's FE1 (2026-11-03, macOS, KiCad 10.0.7, ngspice 46):
  every board regenerated and re-placed; against the branch's boards no footprint moved and only the film caps' order code
  changed. `check_all.py --full` 71 / 71: strip 946 pins, group 807, master 1820, jack boards 32 / 60 / 92, jig 365 / 153,
  PSU 119, 0 mismatches; 1534 / 1534 footprints linked; sim_netlist 45/45, sim_console 45/45, ol.py red 18.4 / green -19.5
  dBu, ol_multi.py pulses +9.01 / -9.30 V. Phase-1 list re-priced.
  TI's models on the merged netlists: strip 21 states, worst U3B 59.8 deg, <= 1.61 dB, U1B >= 84.6 deg, every unit's minimum
  within 1 deg of v5.5. Master phones loop (U26A / B, OPA161x + OPA1656; DRV135s stubbed, meter TL072s left out, neither in the
  loop): 32R 1 nF pot top 76.6 deg, 32R 220 pF pot 0.75 83.0 deg, open pot top 75.9 deg, against 76.7 / 83.0 / 76.0 before.
- Full check of main before that merge (2026-11-03, strip v5.5, master v0.12): `check_all.py --full` 61 / 61; a clean copy of
  HEAD regenerated identically (schematics, BOMs, order lists, DRC rules, panel DXF / SVG byte for byte; boards but for UUIDs
  and file order); TI OPA161x, strip, 21 states: worst U3B 59.8 deg, peaking <= 1.61 dB.

- Strip v4.0 with jack board, DG413 routing and KHN mid bands (2026-10-22): netlists main 697 / jack 30
  pin entries, 0 mismatches; check_fp 227 + 6 parts, 0 problems; ERC 0 on both; tools/sim_netlist.py 30/30
  through the ribbon (levels, gain, Ø, HPF, every EQ band incl. mid-rotation, bypass, mute, direct out at J5,
  aux pre/post, PAN, PFL, routing via the DG413s incl. off = silent);
  with ribbon conductor 6 removed, 23 checks fail, so the link is really exercised.
- Mid tuning sim (`sim/mid_tuning.py`): KHN + A10K vs Delta Wien + C100K, both in the U6A stage: same range
  (684 Hz–10.47 kHz / 148 Hz–2.29 kHz), ±14.6 dB, Q 1.42–1.46 (Delta 1.40–1.45); noise 1.3 / 0.6 dB higher.
- Routing switch sim (`sim/routing_switch.cir`, Vishay DG413): level −0.05 dB (Ron 25 Ω), THD −124 dB at
  +20 dBu (−67 dB if the switch were at the source end), no summing-amp peaking up to 2.2 nF of bus
  capacitance, switching click −55 dBu peak in the 20 kHz band, crosstalk from an unassigned strip −111 dB at 20 kHz.
- Strip v4.0 placement (KiCad 10.0.7, 2026-10-22): main 227 footprints + 6 holes, jack board 6 + 2 holes;
  0 tracks/vias/zones, 0 schematic-parity issues. Main board: 0 violations, including silkscreen (refs
  0.8 mm, placed by place_strip.py). Jack board: only 6 hole-clearance + 6 solder-mask items inside
  KiCad's NJ6FD-V footprint. Unconnected items 499 main, 17 jack (expected). Decoupling caps and the
  KHN integrator parts beside their ICs' pins (place_strip.py NEAR).
- Strip placement check (v3.1 board, KiCad 10.0.7, 2026-10-20): 109 footprints including six mounting
  holes, 0 tracks/vias/zones, 0 schematic-parity issues; no clearance, courtyard, hole or
  outline errors. DRC reports 219 expected unconnected items and 157 silkscreen warnings.
- KiCad 10.0.7 ERC, --severity-all: 0 errors, 0 warnings (2026-10-19).
- Master module (M1 split + jack board, 2026-10-22; post-amps regrouped into U5 the same day): 1521 pins /
  0 mismatches, check_fp 517 / 0, ERC 0; master jack
  board 85 pins / 13 parts, 0 / 0 / ERC 0. Group: 447 pins / 151 parts; group jack board 38 pins / 6 parts; all 0 / 0 /
  ERC 0. Link pinouts match pin for pin between main and jack boards (checked from the netlists).
- Group / master placement (KiCad 10.0.7, 2026-10-22): group 151 footprints + 6 holes, master 517 + 7, jack boards
  6 + 2 and 13 + 3; 0 tracks/vias/zones, 0 schematic-parity issues, 0 DRC violations on both main boards (one silk
  reference hidden on the master, R81); jack boards only the NJ6FD-V's own hole-clearance / mask items (2 per jack).
  Unconnected items 326 group, 499 master (expected). Strip, jig and PSU boards re-place identically after the
  engine changes.
- Attach re-placement (2026-10-23), report before (committed placement) -> after, decouplers median / max / over 5 mm and
  high-Z inputs median / max / over 6 mm: strip 3.6 / 9.1 / 10 -> 3.4 / 10.0 / 11 and 23.2 / 38.1 / 24 -> 9.1 / 19.5 / 19;
  group 3.3 / 7.9 / 4 -> 2.9 / 5.1 / 1 and 25.3 / 229 / 18 -> 7.6 / 17.1 / 15; master 8.6 / 50.5 / 69 -> 3.1 / 7.6 / 20
  and 35.8 / 130 / 105 -> 6.1 / 77 / 55; jig stub 3.6 / 8.7 / 2 -> 2.7 / 3.3 / 0 and 44.0 / 121 / 19 -> 4.7 / 7.0 / 1.
  All boards 0 DRC violations, 0 parity issues; PSU and the three jack boards place identically. Report numbers
  reproduced independently (verification workflow; it also found 7 engine/layout faults, all fixed).
- Part models (2026-10-23, `tools/models3d`, `panel_parts_drawings.md`): 9 footprints built from the manufacturers'
  drawings, each family checked again by a second agent. `check.py`: every PTH pad has a lead, bodies inside the
  courtyards. KiCad 10.0.7 reads the VRML (3D viewer, `kicad-cli pcb render`) and the STEP twins (GLB export).
  All boards re-placed with the model paths: 0 parts moved, 0 net changes; parity DRC unchanged (0 violations on the main
  boards, jack boards only the NJ6FD-V's own 4 items per jack). Master regenerated for the CN1 MPN fix: 1521 pins /
  0 mismatches, check_fp 517 / 0, ERC 0; jack board 85 / 0 / ERC 0. Master then re-placed with J1's wire entry kept free
  (C1/C2 had sat 0.35 mm in front of it): 0 DRC violations, 0 parity issues; report decouplers 3.1 / 7.6 / 22, high-Z
  inputs 6.0 / 78.6 / 54. `check.py --kicad`: KiCad loads all 9 STEP models.
  Pot columns re-centred to x 8.84 / 29.16 (2026-10-23): strip / group / master re-placed, 0 DRC violations and 0 parity
  issues on all main boards (jack boards: only the NJ6FD-V's own items); reports decouplers 3.6 / 10.0 / 11,
  2.9 / 5.1 / 1, 3.1 / 7.6 / 22; high-Z inputs 8.9 / 22.7 / 18, 7.6 / 17.2 / 15, 5.9 / 78.6 / 52. Strip CN3 now lies
  across the strip (y 85.5), so the jack-board ribbon makes one 90° fold (spec 16.4). Independent review: 0 copper or
  courtyard conflicts; key rows re-aligned to the right column (XR - 22 / XR - 11 / XR). A review workflow (3 lenses + skeptics) found
  18 integration faults (flip axis, empty STEPs, ribbon routes, legends under screws, ...), all fixed.
- Master parts review applied (2026-10-23). Schematics:
  - master 532 parts / 1579 pins / 0 mismatches, check_fp 0, ERC 0 (master jack board 85 pins);
  - group 158 parts / 461 pins; jig master stub 144 parts / 364 pins; all 0 mismatches, check_fp 0, ERC 0;
  - the group jack board and jig load board are unchanged.
  Re-placed (placement only): 0 DRC violations and 0 parity issues on the master, group and both jig boards (jack boards:
  only the NJ6FD-V's own items). Reports, decouplers median / max / over 5 mm and high-Z inputs median / max / over 6 mm:
  - master 3.1 / 7.1 / 21 and 7.0 / 51.7 / 72 (worst: U11 VREF6, the meter ladder taps);
  - group 3.1 / 5.1 / 1 and 8.9 / 17.2 / 15;
  - jig stub 2.7 / 3.6 / 0 and 6.0 / 8.4 / 11.
  The new caps add parts to every re-inverter's input nets, which raises the medians (master 5.9 -> 7.0). Re-inverter
  networks are within 7 mm of their op-amp pins on the master; the 22 pF caps' nearest pad within 6.1 mm (master),
  5.6 mm (group) and 5.1 mm (jig). DG413 S nets 7-10 mm, PFL_ON_RAW + PFL_ON 43 mm. The layouts now take their groups
  from the netlist and the generator's near-records (`master_lib.near()`), not hard-coded refs. The master packs its
  summers zone before the overlapping monitoring zone.
  Sims:
  - `sim/mute.cir` v3: coils released 1.4-2.1 ms after a threshold (1 H), contacts open <= ~8.5 ms with 3 H, minimum
    sink and the G6K release (`sim/review/relays`); closes 2.80 s; a 20 ms dip re-arms.
  - `sim/pfldet.py`: one press 0.92 V against 0.50 V, 24 presses 1.29 V, released LEDs <= 20 nA; 3 ms of bounce gives one
    switch each way.
  - `sim/flasher.cir`: LED off while released, first flash 0.6 s after a press, 0.17 s on every 0.54 s.
  - DG413 switcher (`sim/review/pflswitch`, dgF): crosstalk −137 / −111 dB at 1 / 20 kHz, THD −99.8 dB at +20 dBu;
    zero-signal click −88.6 / −78.3 / −70.3 dBu at 10 / 100 / 250 pA leakage.
  - Meter (`sim/review/meters/mkdeck.py`, BCP53 model, 120R): 4.6 mA per string, correct 20-step bar, steps within
    +0.38 / −0.21 dB, no ghost at any of 46 levels.
  An independent check of the applied change found a v0.6 fault, now fixed: the rude-solo flasher's hold did not hold
  (the LED flickered with nothing soloed). It also found the DG413 network and C/Room followers spread out, and stale
  BOM / PDF exports; all fixed.
- Strip v4.1 (2026-10-23, `strip_parts_review.md` applied):
  - Schematics: strip 245 parts / 734 pins, 0 mismatches, check_fp 0, ERC 0, sim_netlist 30/30. Master 535 parts and group
    160 (balanced receiver caps, the master's BAT54W), both 0 mismatches / ERC 0. Jack boards and jig unchanged.
  - Stability (TI OPA161x model, `sim/review/strip/run_all.py none`, 21 states): every strip unit ≥ 69.9°, ≤ 1.61 dB
    peaking. Applying T8 alone (R99 1K into U7B) had dropped U7B to 27-40°; C84 100p at RET_IN restored it.
  - Re-placed with parity DRC: strip / master / group 0 violations, 0 parity issues; jack boards only the NJ6FD-V's own
    items. Reports: strip decouplers 3.1 / 10.0 / 11, high-Z 10.0 / 19.7 / 25; master 3.1 / 7.1 / 22, 7.0 / 51.7 / 71;
    group 3.1 / 4.5 / 0, 10.4 / 23.7 / 17 (the return receivers' area is the group's worst).
  - The stability caps sit within 6.2 mm (feedback) and 9.2 mm (+ inputs) of their pins.
  - BOMs re-exported with a DNP column and quoted fields.
- Master / group review applied (2026-10-24, `master_group_review.md` MG1-MG20, master spec v0.8):
  - Schematics: master 563 parts / 1642 pins, group 170 / 485, jack boards 85 / 38 pins, jig stub and load board
    unchanged but for MPNs; all 0 mismatches, check_fp 0, ERC 0. No IC output shares a net with a connector pin.
  - Stability of the built netlists (TI models): master every unit ≥ 47.7° (CRS followers at the pot top; EXT
    receivers 73°, phones 76-86°); group ≥ 64.2° on the board estimate, ≥ 45.8° with +47 pF on every output.
  - Re-placed: 0 DRC violations, 0 parity issues on the master, group and jig boards. Reports: master decouplers
    3.1 / 10.5 / 25, high-Z 7.2 / 108 / 71 (U11 VREF6); group 3.1 / 6.7 / 2, 9.5 / 20.1 / 18. Build-outs ≤ 10.3 mm
    from their pins. R1-R4 ≥ 13 mm from the PTCs. Strip, PSU, jig and jack boards place identically.
- Whole console (`tools/sim_console.py`, 2026-10-24): 24 strips + 4 groups + master from the generated netlists, each
  module on its own ground through the ribbon's ground conductors and its spade, ribbon R/L/C per 41 mm segment,
  single-pole op-amps with datasheet noise. 32/32 checks:
  - Level: 0 dBu in, pan centre, every fader at "0" gives −0.8 dBu at the main XLRs, not 0. Each "0" mark is
    −10.19 dB (the wiper loaded by the post-amp's 100K), each post-amp +9.93 dB, and the master's build-outs cost
    0.18 dB. The panel's "0" marks could sit a little higher once the fader's real law is measured.
  - Mutes and routing: muted strip −87 dB, unassigned −102 dB, pan rejection −116 dB.
  - Crosstalk at 20 kHz: MIX L → main R −94 dB, → sub −158 dB, → aux −124 dB.
  - Ground: 10 mA into one strip's ground gives −92 dBu at main L. With 1 mA into every module, main L is −93 dBu with
    ground cancel against −69 dBu with the summers on master ground (24 dB). The residue is the strips' unequal
    grounds along the ribbon.
  - Noise, 20 Hz–20 kHz at main L: 24 strips routed −79 dBu, one strip −91 dBu (strip noise dominates).
  - Mutation tests: the v0.7 master netlist fails EXT (−12 dB), and a cut GCANCEL conductor fails the ground checks.
- Film couplers and MUSE ES bipolars applied (2026-10-24):
  - Schematics: every board 0 mismatches, check_fp 0, ERC 0; `sim_netlist.py` 30/30; `sim_console.py` 32/32.
  - Re-placed: strip, group, master and jig 0 DRC violations, 0 parity issues; no tall cap on any top side.
  - Reports unchanged: strip 3.1 / 10.0 / 11 and 10.4 / 19.7 / 25; group 3.1 / 4.5 / 0 and 9.1 / 20.1 / 17; master
    3.1 / 10.5 / 25 and 7.5 / 108 / 72.
  - The committed strip had C49 (2.2 µF MKS2, 13 mm) on the top side under the 11.5 mm panel gap; now on the bottom.
- Drawn group and master schematics (2026-10-24): group 485 pins, master 1642, jack boards 38 / 85: 0 mismatches,
  check_fp 0, ERC 0 at --severity-all; references and nets identical to before; sim_console 32/32. Re-placed: 0 parts
  moved on either board, 0 DRC violations, 0 parity issues, reports unchanged.
- Legibility pass (2026-10-24): every sheet regenerated, 0 mismatches, check_fp 0, ERC 0; sim_netlist 35/35,
  sim_console 32/32; strip, master and master jack board re-placed for the renamed nets (routing control lines labelled,
  PHONESGND a power net): 0 parts moved, 0 DRC violations, 0 parity issues; other boards pass parity as committed.
- Drawn strip schematic (2026-10-24): 260 parts / 774 pins, 0 mismatches, check_fp 0, ERC 0 at --severity-all (no
  off-grid ends, no dangling wires); jack board unchanged; sim_netlist 35/35, sim_console 32/32; TI-model stability
  c01 identical to before (U6A 75.4, U1A 84.8). Re-placed: 0 parts moved, 0 DRC violations, 0 parity issues. Every
  other board regenerated with the builder's field / pin-name fixes: all 0 mismatches, ERC 0, netlists unchanged.
- Sweepable HPF applied (2026-10-24, strip v4.3 / master v0.9):
  - Schematics: strip 260 parts / 774 pins, master 1642 pins, 0 mismatches, check_fp 0, ERC 0; jack boards and jig
    unchanged (the jig stub keeps MF-RX160/72). `sim_netlist.py` 35/35 (HPF −3 dB 21.2 / 85.9 / 406 Hz at CCW / mid /
    CW, no peaking); `sim_console.py` 32/32.
  - Stability (TI OPA161x, full strip, HPF in at three rotations, EQ in / out): U5A 84.3°, U15 ≥ 87.4°, U5B 82.6°.
    Noise: HPF out unchanged; HPF in +0.2 dB (EQ in), +1.4-1.9 dB (EQ bypassed). DC step at switching ≤ 0.9 mV.
  - Re-placed: strip 0 DRC violations, 0 parity issues, report 3.1 / 10.0 / 10 and 11.0 / 23.1 / 29 (U5B's HF network
    23.1 mm). Master 0 / 0, 3.1 / 10.5 / 26 and 8.2 / 38.5 / 75; F1-F4 fixed so only D8 / D9 moved (the packer had
    reshuffled the power entry: a wider PTC body pushes top-side through-hole leads). KiCad loads 10 / 10 STEP models.
- Ground and hum applied (2026-10-25, G1-G3): strip 268 parts / 796 pins, jack boards 32 / 40 / 89 pins, group and
  master main netlists unchanged; all 0 mismatches, check_fp 0, ERC 0. `sim_netlist.py` 37/37 (new common-mode check:
  0 dBu through 1 kΩ on the tip leg gives −60.1 dBu at PRE), `sim_console.py` 32/32 with the G1 harness (noise
  −79.2 / −91.2 dBu unchanged; ground at 1 kHz: 10 mA into strip 24 −89.8 dBu, 1 mA per module −89.2 dBu, ground
  cancel 20 dB). U16 follower margin 52° unloaded, ≥ 48.5° with the 100R build-out for any load. Re-placed with parity
  DRC: 0 violations on the main boards, 0 parity issues on all six; group / master moved 0 parts; strip moved 77 to fit
  U16 (own zone by SW15), report 3.1 / 10.0 / 12 (C92 / C93 8.0 / 8.5 mm) and 10.9 / 22.1 / 29.
- Wing power applied (2026-10-25, W1 / W2): pin 34 = +V on every header; F1 / F3 MF-RX250/72. Every schematic 0
  mismatches, check_fp 0, ERC 0; sim_netlist 37/37, sim_console 32/32; parity DRC clean on all eight boards; the master
  moved F1, F3 and 14 parts around U11 (report unchanged, 3.1 / 10.5 / 26 and 8.2 / 38.5 / 75), every other board 0.
- MET1 / RET1 applied (2026-10-26): strip 290 parts / 851 pins, group 263 / 735, group jack board 11 / 60; master
  unchanged; all 0 mismatches, check_fp 0, ERC 0. sim_netlist 39/39, sim_console 35/35 (new: return 2 to MIX, and
  routed 1-2 equal to return 1), `sim/review/gaps/ol.py` (red 18.1-18.4 dBu, green -19.5 dBu, 170 ms hold, green off in
  overload). Parity DRC 0 violations on every main board; jack boards only the NJ6FD-V's own items (4 per jack); the
  PSU board's 8 silk-edge items are the TO-220s at its edge (since 8b38deb). Strip report unchanged; group 3.0 / 6.2 / 2,
  8.5 / 20.2 / 31. Group and master panels pixel-identical but for the group's new rows; strip panel one numeral (HF "9"
  in place of HPF "50") since `panel_layout.layout()` takes parts in reference order.
- TF1, RV3b, RV9b applied (2026-10-29, signed off "continue"): order lists regenerated with the thin-film rule (62 RT
  lines / 4411 parts, 4 RC lines / 91). Strip v5.7: 946 pins / 329 parts, 0 mismatches, check_fp 0, ERC 0, sim_netlist
  45/45; only D23 (13.0, 120.75) and R143 (34.03, 199.0, 90) added on the bottom, DRC 0 / parity 0, 329 / 329 linked,
  route_check 0, rules re-run. Master v0.14: 1820 / 632, 0 mismatches, ERC 0; only R240 (9.47, 237.25, 90, B) added,
  2.1 mm from Q1's base / emitter pads, DRC 0 / parity 0, 632 / 632 linked, route_check 0, rules re-run; `sim/mute.cir`
  v5 cases 1-6 as before (closes 2.80 s, −V-lost release at −14.14 V). `check_all.py --full` 70 / 71 (panel_fab).
- Cleanup RV12 / RV14 and the XLR shells (2026-10-28, `project_review.md`): the 20 proposal patches moved to
  `archive/patches/` (every reference updated); `.gitattributes` (linguist-generated); three unreferenced sim/review
  scripts deleted, the four old decks labelled HISTORICAL; `render/*.json` and `docs/escape/` regenerated on the v5.6 /
  v0.13 boards. The NC3MAV / NC3MAH shell pad G is on CHASSIS (master jack board J3-J5, jig stub): master jack board 92
  pins / 16 parts, jig stub 365 / 144, 0 mismatches, ERC 0, no part moved, parity 0, links 16 / 16 and 144 / 144;
  check_all --full 70 / 71 (panel_fab). N1: the A/B is the one-strip swap of `test_jig_spec.md` §1.1 everywhere
  (order_bom EXTRA 16 -> 8). `ol.py` is labelled a values check (RV11.8).
- Clicks batch applied (2026-10-28, strip v5.6, master v0.13, group; `clicks_proposal.md` RV3 / RV4 / RV7 / RV8 / RV9):
  strip 941 pins / 327 parts, master 1818 / 631, group 807 / 292; every schematic 0 mismatches, check_fp 0, ERC 0;
  sim_netlist 45/45, sim_console 45/45, check_bus clean. Placement by moves_only: only the new parts changed (strip R142 /
  C107, group C98, master C194-C197 / R238 / R239; films 64 / 24 mm and 33 uF cans 13 / 21 mm from their resistors on the
  master, the SENSE_REF divider 3.4 / 5.0 mm from U10); every board DRC 0 / parity 0, 1531 / 1531 footprint links,
  route_check 0, net rules re-run. `check_all.py --full` 70 / 71 on Linux (panel_fab needs the macOS fonts). Order
  lists regenerated (64K9 RC0805FR-0764K9L; R73 now ERJ-P06J750V).
- Whole project (2026-10-28, strip v5.5, group with CS2b, master with CS7, `tools/check_all.py --full`): 61 / 61 checks pass on the committed tree: every board's
  netlist vs intended (strip 937 pins, group 805, master 1796, jack boards 32 / 60 / 89, jig 364 / 153, PSU 119), pins vs
  footprints, ERC 0, parity DRC (only the known footprint items), 1517 / 1517 footprint links, route_check 0 ERR;
  sim_netlist 45/45, sim_console 38/38, every DRC rule fires (15), route_check_test 8 / 8, panel checks 0, ol.py red
  18.4 / green -19.5 dBu, ol_multi.py pulses +9.01 / -9.30 V.
- E11 applied (2026-10-27, placement only): strip 13 / group 1 / master 7 decouplers moved, nothing else; 0 DRC, 0 parity,
  every footprint linked; decouplers median / max / over 5 mm: strip 2.5 / 5.4 / 1, group 2.9 / 5.1 / 1, master
  3.1 / 11.5 / 20 (C144 / C145 THT stay). Routing rules re-generated, all 8 fire.
- E10 applied (2026-10-27, placement only): strip 9 / group 7 / master 2 resistors moved, nothing else; 0 DRC, 0 parity,
  every footprint linked on all six boards; input nets over 20 mm strip 17 -> 9, group 10 -> 3, master 23 -> 21, none
  longer; emc_check: strip U5B- 7.6 -> 13.6 mm from U4's output, group U9A- 7.0 -> 15.1 mm from D3.
- E9b applied (2026-10-27, placement only): group 11 / master 13 caps moved, nothing else; 0 DRC, 0 parity, every
  footprint linked; reports: group high-Z 8.5 / 20.2 / 30 -> 7.8 / 20.2 / 26, master 8.1 / 97.0 / 77 -> 76, decouplers
  unchanged; every C0G cap on an op-amp input <= 6.1 mm (group) / 6.4 mm (master), was 13.0.
- E9 applied (2026-10-27, placement only): 12 caps moved, 0 DRC, 0 parity, 290 / 290 links, `emc_check.py` unchanged;
  placer report high-Z inputs 10.4 / 258.6 / 28 -> 8.5 / 258.6 / 25, decouplers unchanged; every C0G cap on an op-amp
  input <= 6.3 mm from its pin (was up to 22.1).
- PAN1 applied (2026-10-26, strip v4.8): 851 pins / 0 mismatches, check_fp 290 / 0, ERC 0; BOM unchanged; sim_netlist
  39/39, sim_console 35/35. TI stability 21 states (`results_none.json`): pan L U8B 80.2-87.5 deg as U2B was, every other
  unit as on the v4.7 netlist, minimum U3B 59.8 deg (direct out at top), <= 1.61 dB peaking. Placement: 8 parts moved,
  0 DRC, 0 parity, 290 / 290 links; pan L + input 165 -> 24 mm, nearest aggressor 2.9 -> 11.6 mm (`emc_check.py`).
- G2b / G3b applied (2026-10-25): group 186 parts / 529 pins, master 579 / 1686, jack boards 40 / 89; 0 mismatches,
  check_fp 0, ERC 0; sim_console 32/32. Placement: group report no worse (3.1 / 4.5 / 0, 7.8 / 20.1 / 18), master
  unchanged (EXT followers in a last zone); parity DRC clean. Global labels on every hierarchical page now centred in
  their boxes (they sat on the outline; schgen `add_label`).
- Design review applied (2026-10-25): every schematic 0 mismatches, check_fp 0, ERC 0; sim_netlist 39/39 (new: ON mutes
  aux pre and the direct out, -86 dB), sim_console 32/32; TI strip stability: U3B 59.8° in the direct-out-at-top states
  (now drives the pre aux pots), 72-74° elsewhere, every other unit unchanged. Re-placed: parity DRC clean on all nine
  boards; group moved only RV2, master only C57, the strip re-packed (report 3.1 / 10.0 / 12, 10.5 / 22.1 / 30).
- PSU sim (`sim/psu.cir`, 2026-10-22): soft start 165 ms to 90 %, no overshoot; 5.1 A peak SMPS current;
  crowbar idle margin 2.21 / 2.495 V; fault (pass element shorted) → fires in 17 µs, console bus peak 19.7 V,
  strip/master rails stay 16.9 V; LDO 19 W at 4 A; LC −47 dB at 65 kHz (ESR-limited).
  Schematic: 52 parts, 119 pins / 0 mismatches, check_fp 0, ERC 0.
- Test jig (2026-10-22): master stub 334 pins / load board 153 pins, 0 mismatches; check_fp 129 / 50 parts, 0 problems;
  ERC 0 on both.
- Power-on mute (`sim/mute.cir`): closes 2.8 s after power-up, opens ~2 ms after either rail drops
  below ~14 V, full re-arm after any fault longer than ~10 ms.
- ngspice (2026-10-19, `sim/strip.cir`, the v3 strip): 0 dBu in → PRE 0 dBu, POST +9.9 dBu, pan centre −6 dB, mute ≈ 86 dB,
  LF −3 dB 1.1 Hz (today: pan centre −2.7 dB since CS2, LF −3 dB 2.3 Hz since F1-F4).
- Delta-clone sims (2026-10-22, `sim/gain_stage.cir`, `sim/delta_eq.cir`, `sim/strip_v4.cir`): gain −15…+14.8 dB,
  0 dB at the detent; HPF (unity Butterworth) −3 dB 87 Hz; EQ HF ±11.5 dB @12k, HI-MID ±14.6 dB 670 Hz–10.5 kHz,
  LO-MID ±14.7 dB 148 Hz–2.3 kHz (Q 1.44), LF ±14.3 dB @54 Hz; flat ±0.16 dB, in phase; 0 dBu in → PRE 0 dBu.
  PRE noise −105.2 dBu EQ bypassed, −97.2 dBu EQ in (resistor noise only). With the OPA1612's 1.7 pA/√Hz current
  noise (tools/sim_console.py, 2026-10-24): −102.6 / −92.9 dBu; the 22K EQ and KHN networks turn it into voltage.
- Bus noise (OPA1612, 24 ch routed): −97.6 dBu with 10K, −100.4 dBu with 4K7 (20 Hz–20 kHz).
