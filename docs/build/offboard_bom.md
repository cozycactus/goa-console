# Off-board parts (2026-10-25; RET1 counts 2026-10-26)

Everything a build needs that isn't on a board's BOM, so `bom/order_bom.csv` doesn't have it. Counts are for the console:
24 strips, 4 groups and the master, plus the PSU and the jig where marked. Per-module counts come from the placed
boards. Dimensions and rules come from `docs/build/panel_parts_drawings.md`, strip spec §16, master spec §24–26 and
`psu_spec.md` §7–8.

**Status:**
- **code:** the part is decided and named in the specs.
- **rule:** the specs fix its dimensions; any part meeting them will do, so pick an order code.
- **decide:** your choice. The 3D model uses placeholders for these.

## Panel side

| Item | Per strip / group / master | Console | Status | Part or rule |
|---|---|---|---|---|
| Knob, 1/4" (6.35) round shaft | 14 / 3 / 5 | 353 | code | **Elma 021-3525**: classic collet knob Ø14.5, matt black with a line (`docs/proposals/knob_proposal.md` KN1, signed off 2026-10-25); no nut cover |
| Knob cap | 15 / 4 / 5 | 381 | code | **Elma 040-30x5**, matt, without a line (KN3): red 040-3035 ×25, grey 040-3015 ×98, blue 040-3045 ×80, yellow 040-3055 ×50, green 040-3065 ×50, black 040-3025 ×78 (colour per function in `docs/proposals/knob_proposal.md`) |
| Knob, 6 mm D shaft (pan, RK09L) | 1 / 1 / 0 | 28 | code | **Elma 021-3425**: the same knob with a 6 mm collet |
| PV cap for PVA2 | 13 / 11 / 4 | 360 | code | C&K PV, round Ø7.4 × 7 (`docs/proposals/knob_proposal.md` KC1): PVGY ×194 (CS7: + master DIM), PVWH ×100, PVRD ×42, PVBK ×24 (ON). Panel hole Ø8.0. |
| Fader cap | 1 / 1 / 1 | 29 | code | Sifam LK111 01, black with a white line (KC2; 02 LK110 01, RS 281-7197, if only the plain one is stocked). Trial a few generic white / red / yellow 8 × 1.2 caps at the fader sample check; if one fits, strips white, groups red, master yellow. |
| Fader screws | 2 / 2 / 2 | 58 | rule | M3 into the PTB cover's tapped holes, 120.0 apart, through the 1.5 panel and the 3.5 spacer. M3 × 8 countersunk if the panel is countersunk. |
| Fader spacer | 2 / 2 / 2 | 58 | rule | 3.5 mm thick, M3 clearance, under the panel at each fixing (the stack puts the lever 5.0 above the panel). |
| Pot spacer washer, M7 | 14 / 3 / 5 | 353 | rule | 1.5 thick, ID 7.2, OD < 11.2 to clear the anti-rotation lug (model 10). Leave the pot's own 0.4 washer off: the bushing has no spare thread. |
| Pot spacer washer, M9 (RK09L) | 1 / 1 / 0 | 28 | rule | 9.5 / 11 × 1.5. Its M9 nut: check the thickness on a sample (spec open item). |
| LED spacer, 3 mm LED | 6 / 4 / 43 | 203 | rule | 7.6 mm long (the LED's lens then sits at the panel). |
| LED spacer, 3-lead 3 mm LED (strip D2, WP3VEGW) | 1 / 0 / 0 | 24 | rule | 7.2 mm long (the WP3VEGW is 5.0 mm tall against the WP710A10's 4.6) with three holes at 2.0 mm, or a 2-hole spacer opened up: settle on a sample (`docs/build/sample_order.md` check 8). The outer leads jog outward just under the flange. |
| LED spacer, 5 mm LED | 0 / 0 / 1 | 1 | rule | The master's PFL ACTIVE LED, sized to the same panel height. |
| Main-board standoff, M3 F-F | 6 / 6 / 7 | 175 | rule | 11.5 mm (panel underside to PCB), unplated holes. One M3 screw each at the board (175). Panel end (`docs/reviews/met1_ret1_review.md` P4, 2026-10-27): a blind M3 stud welded to the panel's back if the maker offers it (positions in `panels/<key>_holes.csv` and the DXFs' STUDS layer), else nothing: the standoff is a spacer and the board hangs on the pot and jack nuts, as on the Delta. |
| Jack-board standoff, M3 F-F | 2 / 2 / 3 | 59 | rule | **Exactly 24.0 mm, metal.** The jacks are rigid spacers, so a longer one hangs the board on its solder joints. One M3 screw each at the board (59). These standoffs carry CHASSIS to the panel (G2), so the panel end needs metal contact through the anodising, and an
internal-tooth M3 star washer between standoff and panel back does that (59). With welded studs (P4 b), the standoff
threads onto the stud. Without them (Ruslan, 2026-10-27): an M3 x 6 countersunk flat-head screw through the panel (59, black),
in the countersunk Ø3.4 / 90° to Ø6.5 holes on the DXFs' CSK_NO_STUDS layer and in the hole tables. |
| Front panels | 8 HP / 8 HP / 16 HP | 24 + 4 + 1 | **decide** maker (`docs/build/panel_makers.md`) | 1.5 mm aluminium, anodised (not powder-coated: 1.5 is the NJ6FD-V's upper limit). 40.30 × 514 mm (8 HP × 12U), the master 80.94 × 514. Fabrication drawings (DXF, 1:1 PDF artwork, hole tables) are in `panels/` (`tools/panel_fab.py`). |
| Frame rails | | 1 + 1 | code (make) | 6060-T6 / 6082 flat bar 50 × 10 × 1227.2 mm, 30 M3 + 5 M4 tapped holes each; the BACK rail also has 30 vent slots 30 × 25 (`docs/studies/thermal_study.md` TH1) (`frame/rail.dxf`, `rail_holes.csv`; `docs/proposals/frame_proposal.md` FR1–FR3). Star washers under the panel screws; one 2.5 mm² green-yellow bond per rail to the M4 star. |
| Tub | | 1 | code (make) | `docs/proposals/tub_proposal.md` TB1-TB4, drawings in `tub/` (`python3 tools/tub_fab.py`): walnut cheeks ×2 (601 × 212, rail rebates, floor dado), 12 mm birch-ply floor 1235.2 × 517 with 30 inlet slots + mesh, walnut arm-rest 1223.2 × 44 × 76, plenum rear wall 1223.2 × 80 × 12 (NC7MD-LX) and cap strip 1223.2 × 14 × 10; open underside; felt pads; console raised 25 mm |

## Ribbons and links

| Item | Console | Jig | Status | Part or rule |
|---|---|---|---|---|
| 34-way IDC socket (motherloom) | 30 (24 strips, 4 groups, 2 master wing headers) | 6 (4 strips, stub, load board) | code | Würth 61203423021 (WR-BHD, strain relief), the mate of the boards' 61203421621 headers |
| 34-way flat cable | 2 wing runs of about 14 × 40.6 mm + slack, ≈ 0.75 m each | ≈ 0.5 m | rule | 1.27 mm pitch grey flat cable, 28 AWG. The IDC contacts are rated 1 A (+V uses three conductors, W1). Order 3 m. |
| 10-way IDC socket (strip jack link; group return-2 link) | 56 (2 × 24 + 2 × 4) | | code | Würth 61201023021 |
| 10-way flat cable | 24 × ~125 mm (straight, no fold since 2026-11-11, strip spec §16.4) + 4 × ~200 mm (group return 2: straight, no fold, 179.3 mm between the socket centres plus the 12.5 mm step and about 10 mm of slack; it passes under the 16-way's two sockets; computed, not yet cut, `docs/decisions.md` 2026-11-11) | | rule | 1.27 mm flat cable; order 5 m |
| 16-way IDC socket (group jack link) | 8 (2 × 4) | | code | Würth 61201623021 |
| 40-way IDC socket (master jack link) | 2 | | code | Würth 61204023021 |
| 16- and 40-way flat cable | 4 × ~160 mm (group: straight, no fold, 140.1 mm between the socket centres plus the 12.5 mm step and about 10 mm of slack; computed, not yet cut, `docs/decisions.md` 2026-11-11), 1 short link (master) | | rule | 1.27 mm; the master's cut to fit the 24.0 mm board spacing with one fold |

## Ground harness (G1, master spec §26)

| Item | Qty | Status | Part or rule |
|---|---|---|---|
| 14 AWG (2.08 mm²) stranded wire | 28 wires, 16.1 m in all | rule | Cut list: left wing 264 + 40.6·k + 60 mm, right wing 237 + 40.6·k + 60 mm, k = 0…13 from the module next to the master. Longest 852 / 825 mm. Order 20 m. |
| 6.3 mm insulated receptacle, blue (14–16 AWG) | 56 | rule | Both ends of every wire (spade CN4 / CN1 to bar tab) |
| Copper ground bar | 2 | rule (make) | ~15 × 2 mm, fourteen 6.3 mm tabs in two rows, one per wing, on a threaded spacer under the master's M4 stud |
| M4 stud hardware | 1 set | rule | Screw, threaded spacer, nuts and star washers for CN1 and the two bars; the PSU 0 V and earth lead also land here |
| Cable ties | ~200 | rule | The wires are tied under the motherloom every ~80 mm, never along the tub floor |

## Power

| Item | Qty | Status | Part or rule |
|---|---|---|---|
| Mean Well LRS-150-24 | 2 | code | Set to 21.6 V (PSU decision, option B) |
| Console power inlet | 1 | code | Neutrik NC7MD-LX in the plenum's rear wall (TB3, `docs/proposals/tub_proposal.md`), wired to J1 |
| PSU output socket | 1 | code | Neutrik NC7FD-LX on the PSU panel, wired from the 7-way terminal |
| Link cable connectors | 1 + 1 | code | Neutrik NC7FX (to the console's NC7MD-LX) and NC7MX (to the PSU's NC7FD-LX) |
| Link cable | ≤ 2 m | rule | 7 × 1.0 mm² (≈ 70 mV drop at 4 A) |
| IEC inlet | 1 | code | Schurter DD11 (IEC C14 inlet, 2-pole switch, fuse drawer; T2.5 A at 230 V, T5 A at 115 V; PC1-PC3, `psu_spec.md` §8); spare fuses |
| Heatsink | 1 | code | Fischer SK 47 75 SA (~0.85 °C/W, PC2) on the case's front end panel; the four TO-220s in a row at the PCB's top edge pass through a window onto it (only the LDOs dissipate, 19 W each at 4 A); ≤ 1.2 °C/W needed |
| TO-220 insulators | 4 + 4 | rule | Silicone pad and shoulder washer per tab (the tabs sit at +17 V and 0 V); M3 screws |
| PSU case | 1 | code | Hammond 1402KV; Fischer SK 47 75 SA on the front; Schurter DD11 (+ 2 × T2.5 A 5 × 20 fuses), NC7FD-LX, M4 earth stud on the rear; 4 TO-220 silicone pads + shoulder washers; 2 mm aluminium shelf on 4 × M3 × 45 posts; 4 × M3 × 8 board standoffs; panel-clip LED. Drilling in `psu_case/` (`docs/proposals/psu_case_proposal.md`). 0 V stays isolated from earth in the PSU. |
| PSU PCB standoffs | 4 | rule | M3, to the case floor |
| DRV135 coupler pairs | 15 pairs | rule | Measure the 40 Panasonic ECE-A1EN100U at 100 Hz, sort, pair neighbours within 2 %, one pair per DRV135 (groups C21 / C22, C40 / C41; master C43 / C44, C47 / C48, C51 / C52, C71 / C72, C84 / C85, C130 / C131, C134 / C135); record the values and the bench check in `docs/build/build_records.md` §1 (CS11b, `docs/proposals/cs11b_proposal.md`) |
| Module plugging | — | rule | Power the console down before plugging or unplugging a strip or group: their R1-R4 are fusible (CS6, `docs/proposals/cs6_proposal.md`) and a module plugged into a live wing may open them |

## Decisions this list needs from you

1. ~~Knobs~~: decided, Elma 021-3525 / 021-3425 with 040-30x5 caps (`docs/proposals/knob_proposal.md`, 2026-10-25).
2. ~~PV cap colours~~ and 3. ~~fader caps~~: decided (`docs/proposals/knob_proposal.md` KC1 / KC2, 2026-10-25).
4. **Panel maker.** The fabrication drawings are in `panels/`. Measure the fader law before printing
   (`panels/README.md`).
5. ~~Frame and PSU case~~: decided (`docs/proposals/frame_proposal.md` FR1-FR3 and `docs/proposals/psu_case_proposal.md` PC1-PC3, 2026-10-25 / 26); drawings in `frame/` and `psu_case/`.
