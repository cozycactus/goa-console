# Schematic readability review: all nine schematics by eye (2026-11-12)

How the schematics look and read in KiCad, asked for by Ruslan as a check "by eye". A review only: nothing was
changed, every finding is about the drawing, none changes a netlist. Findings SR1-SR7 are open until signed off.

**Method.** KiCad 10.0.7's own plot of every project (`$KC sch export pdf --exclude-drawing-sheet`, one PDF per root,
68 pages), rasterised with `pdftoppm` at 140 dpi and cropped to the drawing; every page read at that size, the three
large sheets in tiles, dense spots again at 250-280 dpi, the whole set first as overview tiles for page fill and flow.
The meter pages 22, 23, 25 and 26 were read at half scale (they repeat 19 and 20), the stub's AUX and PFL lanes in
overview only. Use the PDF route: `rsvg-convert` on KiCad's SVG draws some field text falsely bold. Checks run beside
the reading: `$KC sch erc --severity-all` on each root, and the `readable-schematic` skill's `lint_kicad_sch.py`
(`--recursive --grid 1.27`; the skill is not in this repository). The yardstick is that skill's rules, which Ruslan
approved on 2026-11-12: wires over labels, the main path in one row passing from block to block by wire, parallel legs
as identical rows, supplies as symbols pointing the right way, a name on every important wire. The strip, group and
master drawings are older than those rules (the strip's title block says "labels join the blocks"), so the systematic
departures below are an earlier convention, not carelessness.

## 1. Result

Electrically clean, unevenly readable. ERC: 0 violations of any severity on all nine (the projects switch off four of
KiCad's checks: `four_way_junction`, `single_global_label`, `simulation_model_issue`, `footprint_filter`). The lint
counts are leads that were confirmed by pattern on the renders, not one by one.

| Schematic | Pages | Drawn by | Wires | Lint errors / advisories | Reads as |
|---|---|---|---|---|---|
| `channel_strip` | 18 | `tools/strip_draw.py` | yes | 115 / 57 | wired blocks, labels between blocks |
| `jack_board` | 1 | `schgen.build()` grid | 0 | 21 / 12 | a grid of labelled parts |
| `group` | 13 | `tools/frags.py` fragments | yes | 54 / 76 | fragments joined by labels |
| `group_jack_board` | 1 | `schgen.build()` grid | 0 | 45 / 21 | a grid of labelled parts |
| `master` | 31 | `tools/frags.py` fragments | yes | 212 / 198 | fragments joined by labels |
| `master_jack_board` | 1 | `schgen.build()` grid | 0 | 105 / 47 | a grid of labelled parts, CN1 on top of J1 |
| `jig_master_stub` | 1 | `tools/gen_jig.py`, drawn 2026-11-10 | 337 | 11 / 30 | the model sheet |
| `jig_load_board` | 1 | `schgen.build()` grid | 0 | 103 / 51 | a grid of labelled parts |
| `psu` | 1 | `schgen.build()` grid | 0 | 23 / 84 | a grid of labelled parts |
| total | 68 | | | 689 / 576 | |

## 2. What works (keep)

- **Strip, inside a block.** Sheet 02's receiver is two identical rows with the phase switch's cross-over drawn by
  wire; sheet 05's four EQ stages are one row joined by wire; the state-variable filters (04, 06, 07) carry SUMMER /
  INTEGRATOR sub-headings; the overload and signal detectors are two parallel rows (09); decoupling is one rail pair
  with the supply units and capacitors strung between (17, 18).
- **Jig master stub.** Power entry along one line, six bus lanes from ribbon to BNC as identical wired rows, names as
  plain labels on the wires, test points on the nodes. It shows what the other sheets can look like.
- **Master.** The power entry with its star of net ties (29), the comparator and LED columns of the meters (20, 22,
  25, 26), the DIM switch across R236 / R237 (16), the MONO summing node (05).
- **Everywhere.** Every sheet has its title, revision, date and sheet number; block headings state the key figures;
  the DNP parts seen carry a note (the VCA option, the +10 dB resistors); every part has a value; spare halves are
  tied off; no diagonal wire, no T without a junction, nothing off the 1.27 mm grid.

## 3. Findings, most important first

### SR1. Five sheets have no wire at all

`psu` (52 parts, 119 labels), `jig_load_board` (50 parts, 83 labels), `master_jack_board` (16 parts, 68 labels),
`group_jack_board` (11 parts), `jack_board` (8 parts): every part stands alone in a grid cell with a label on each pin.
Why it matters: nothing can be traced. On the PSU the LM1084-ADJ regulators, their dividers, the soft start and the
two crowbars (TL431 -> PNP -> SCR) have to be assembled from 119 names, and that sheet is what the PSU board will be
routed from. These sheets also hold the worst collisions:

- `master_jack_board`: the 2x20 link CN1 is drawn on top of jack J1; its left pin labels pile on each other and on J1's
  (text over text 44, text over symbol 36, symbol over symbol 6). On the XLRs J3-J5 the pin-3 label runs through the value.
- `jig_load_board`: the ground spade CN1 is drawn over the ribbon header CN2 (its reference inside CN2's body, its
  value across pins 17 / 18, CN2's own value across pins 25 / 26); 52 ground symbols point up or sideways.
- `psu`: the ADJ pin's label lies over the value of U1 / U3; the pin labels of U2 / U4 (TL431) pile onto the symbol;
  the references Q1 / Q3 sit under the POS_SC / NEG_SC labels; the value of L1 / L2 under POS_LC / NEG_LC; J3's value
  over its pin 7.
- `group_jack_board`: CN1's reference is inside its body and its value across pins 15 / 16; on J1 and J4-J7 the value
  is printed across the body, under a ground symbol (J4, J6) or crossed by a vertical label (J5, J7).
- `jack_board`: the value of J1 / J2 / J5 across the body; the CHASSIS label of H1 / H2 through the value; three ground
  symbols stacked sideways at CN5.

Code: `tools/schgen.py` `build()`, lines 479-490 (a block with no draw function is laid out `perrow` per row and
`attach()` labels every pin). Callers: `tools/gen_psu.py`, the load-board half of `tools/gen_jig.py` (from line 249),
`tools/gen.py` line 408, `jack_board()` in `tools/master_lib.py`. The stub was the same grid until 2026-11-10.

### SR2. Master: control and timing circuits are chains of labels

In these blocks the topology is the content (a pull-up, hysteresis, a time constant, a current source), and it cannot
be seen:

- **POWER-ON MUTE**, sheets 07-08, 15 fragments of one to three parts: R49 / D7 (VREF6), R50 / R51 (SENSE_P),
  R52 / R53 (SENSE_N), U10A / U10B (RAIL_OK), R54, R55 / C57 / D9 (MUTE_T), D8 / R56, R57 (22M), U11A (MUTE_GO), R58,
  R59 / D11 (RLY_B), D10 / R60, Q1 (RLY_DRV), R238 / R239 (SENSE_REF), R240.
- **PFL DETECT**, sheets 14-15, 7 fragments: R114 / R115, R113 / C120 / D16 / D17, R116, R117 (10M), U22A, U22B, R118.
- **RUDE SOLO**, sheet 15, 6 fragments: U11B, R119 / R120, R121, R122 / C123 / D18, R123, R124 / D19.
- **Meter LED-string current sources**, each over three sheets: MLA = R171 (18) + D27 / D28 / R172 (19) + Q2 (20);
  MLB = R173 (20) + D39 / D40 / R174 (21) + Q3 (22); MRA = R208 (23) + D55 / D56 / R209 (24) + Q4 (25);
  MRB = R210 (23) + D67 / D68 / R211 (24) + Q5 (26).
- **Peak detector**: the loop from U30B's output back to U30A's inverting input is closed by the label ML_DETO
  (sheet 19); MR_DETO on sheet 23.
- **Headphone amplifier**: the gain leg R132 -> PH_GL -> C196 (and R136 -> PH_GR -> C197) is cut by a label between
  sheets 17 and 18, so the series capacitor in the feedback shunt is not visible at the amplifier.
- **Group**: the PFL sum of a return is two separate rows that end in the same label, R65 / R66 -> RT_PFLJ (sheet 07)
  and R105 / R106 -> RT2_PFLJ (sheet 09); the summing node is not drawn.

Several of these are on the bench list (relay release, PFL tick, meter current-source temperature). The same PFL
detect is one wired figure on `jig_master_stub` (divider, comparator, clamp, LED string): the proof that it fits.
Code: the block definitions in `tools/gen_master.py` and their fragments in `tools/frags.py`.

### SR3. Group and master in general: fragments joined by labels

- Neighbouring stages of one row are joined by a pair of equal labels instead of a wire: S_SUM (group 03), A_SUM (05),
  SUM_L / SUM_R (master 02 / 03), MONO_INV (05), PFL_SUM (13). The balanced receivers reach their difference amplifier
  through RT_L_TB / RT_L_RB and the like, in swapped order (group 06, 07, 09; master 11, 12); the strip draws the same
  receiver by wire (sheet 02).
- A single part continues a stage as its own fragment: CRSB_LO -> R110 -> CRSB_L and CRS_R -> R111 (master 14), the
  keeper R10 on GCANCEL (master 02). Parts made last stand apart as a vertical capacitor between two rotated labels:
  C98 (group 05), C194 (master 09), C195 (master 10).
- The order is not the signal's: on group sheets 03-04 the DRV135, the pan pot and the sub-to-mix switches come before
  the post-amp U3A that feeds them.
- A function starts part-way down a page and continues on the next: group 02, 04, 06, 08, 12; master 02, 03, 04, 07,
  08, 11, 12, 13, 14, 17, 18, 29. In the worst cases only one row of small fragments stands under the new heading
  before the break: group 02 (5 parts), 04 (2), 08 (7); master 08 (7), 14 (8), 12 (10), 18 (12).
- L and R are on different pages instead of identical rows: MIX L 02-03 / MIX R 03-04, the fader post-amps 04 / 05,
  EXT L 11 / R 12, meter L 18-22 / R 23-26.
- Decoupling is one stamp per IC (the supply unit, two capacitors, four rotated rail labels), with the -VA label above
  its capacitor like the +VA one. Master sheet 21 is six stamps and one bias fragment (18 of its 21 parts); on sheet
  24 the stamps are 21 of 39 parts. The strip's rail pair (sheets 17-18) is the better figure.

Code: `tools/frags.py` and the packer `flow()` in `tools/schgen.py` (line 94), with `flowed=True` in
`tools/gen_group.py` and `tools/gen_master.py`.

### SR4. The root sheets show no signal path, and labels do not say where they continue

The three roots are grids of 17 / 12 / 30 sheet boxes without pins or wires. Inter-sheet references are off in every
project (`intersheets_ref_show` false in the group and master `.kicad_pro`, absent in the strip's), so none of the
global labels shows the pages it appears on, with 132 jumps counted inside single sheets alone.

### SR5. Strip: single spots

- Sheet 14: the references R137 and R140 are overprinted by C105 / C106 and cannot be read.
- Labels lie along their wire and are struck through by it: VCAIN, FPIN, FPOST (12; FPIN and FPOST also sit on a
  junction dot), VREF and SIG_IN (09), A6R (13).
- A label where the block already has the wire: HIN to SW11A pin 3 for the HPF bypass (04), EQ_FP from the LF network
  to U7A pin 3 (05), A6R between SW13A and SW13B (13).
- Sheet 13: the cold leg of DIRECT OUT (R73, C107, R143) is drawn vertically, not as a row identical to the hot leg
  (R71, C52, R72).
- Sheet 09: the LED D2 is apart from its resistors R15 / R124 (labels OL_A, SIG_A); Q5 is a fragment on OL_K / SIG_B;
  C101 and C102 hang from a +VL label drawn below them; nothing says that PK and OL_NN have four more sources
  (D12-D15) and the comparator U18A on sheet 10.
- Sheet 15: the +5VL supply (R80, D9, D10, C62) has no heading of its own inside ROUTING MATRIX.
- Sheet 17: "C26 100n" runs into "U17C" and "C98 100n" into "U18C"; the pin numbers of D16 / D17 lie over the diodes.
- Sheets 03, 08 and 11 hold 9, 8 and 11 parts on 9-11 % of an A4 page; ten strip sheets fill under a third.
- Connected four-way junctions: 05 (5), 14 (2), 09 (1); also group 04 (2) and master 05, 19, 23, 29 (1 each).

Code: `tools/strip_draw.py`.

### SR6. Conventions on every sheet

- Rails are boxed, mostly rotated labels instead of power symbols (130 places, counted once per name and sheet), so
  a rail looks like a signal.
- 144 ground symbols point sideways or up: the connector pin lists (strip 02, 18; group 11; master 28, 30, 31; the
  jack boards), the relay contacts (GNDA upward on master 06, 16; PHONESGND on 18), strip 15-16 (C54, C57, C60 between
  GNDA above and -VA below), the load board (52). At the end of a long wire a sideways ground reads as an arrow.
- The value "BAV199" is printed across the pin-3 wire on all 44 clamps (strip 02: D18-D23; group 12: D7-D20; master
  27-28: D79-D102).
- The meter ladders' tap labels (ML_T1...T20, MR_T1...T20) are squeezed between the resistors and struck through by
  the wire (master 18, 19, 23, 24: about 38), as is FL_N on master 15. A ladder is a divider; drawn vertically with
  the taps leaving sideways it would need no label on the wire.

### SR7. Two notes that are not true

- Master sheet 29's heading says "PTC per wing per rail, 1.85 A hold, 72 V". Since W2 (2026-10-25) F1 / F3 on +V are
  MF-RX250/72 with 2.5 A hold; only F2 / F4 hold 1.85 A. `tools/gen_master.py` line 29.
- The SUBGROUP, AUX MASTER, MAIN OUTPUTS and CONTROL ROOM headings say DRV134; the symbols say DRV135 (the same
  amplifier in SO-8).

## 4. Lint totals (leads, not a score)

| Rule | Count | Kind |
|---|---|---|
| `near_labels` | 300 | advisory |
| `power_symbol_direction` | 144 | error |
| `sheet_jump` | 132 | advisory |
| `rail_label` | 130 | error |
| `text_wire` | 101 | error |
| `plain_label_jump` | 100 | advisory |
| `text_text` | 83 | error |
| `text_body` | 80 | error |
| `label_fragment` | 72 | error |
| `symbol_pin_text` | 24 | advisory |
| `symbol_overlap` | 23 | error |
| `wire_body` | 20 | error |
| `label_loop` | 20 | error |
| `sheet_fill` | 15 | advisory |
| `four_way_junction` | 14 | error |
| `flat_hierarchy` | 3 | advisory |
| `collinear_overlap` | 2 | error |
| `intersheet_refs_off` | 2 | advisory |

All 20 `wire_body` findings are a PWR_FLAG standing on its wire (master 13, 29, 30; strip 15, 17): harmless.

## 5. Not checked

- KiCad's editor window: the plot was read, not the GUI (theme colours, behaviour on opening a project).
- Anything electrical; the netlists were not compared with anything.
- The lint's 1265 findings one by one; only each pattern on the renders.
- Legibility on paper.

## 6. Proposed order (nothing applied)

Each step is a drawing-only change to a generator, proven by a netlist comparison before and after
(`compare_netlists.py` of the skill, both sources), ERC, `check_all.py --full` and a placement diff, as the stub was.

1. **SR1, the PSU sheet first.** It is the one board whose routing needs the current paths on the drawing, it is a
   single sheet, and the change cannot reach the board. Ruslan started this redraw on 2026-11-12; its record goes to
   `docs/verification_log.md` when it lands.
2. **The small generator edits**: inter-sheet references on (SR4), the BAV199 value off its wire and the ladder taps
   (SR6), the labels on wires and R137 / R140 (SR5), the PTC heading (SR7). Little work, visible on every sheet.
3. **SR2**, the master's mute, PFL detect, flasher and current sources as drawn blocks, the way the stub draws its
   PFL detect.
4. **SR1's other four sheets** (load board, three jack boards).
5. **SR3**, the re-flow of group and master: the largest job, and the one that most needs a sample sheet agreed first.
6. **SR4's roots**: a block diagram or sheet pins with wires.
