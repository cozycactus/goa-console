# Sample order for the prototype panel (2026-10-26)

One small order, timed with the prototype strip panel (`panel_makers.md`), that settles every open physical check
before the batch of 29 panels and the console's parts are bought. Order codes are the BOM's (`order_bom.csv`,
`offboard_bom.md`); the checks come from `panel_parts_drawings.md`, strip spec §16 and the decisions in `CLAUDE.md`.
Most checks need the prototype panel and a 1:1 print of the strip board's top side; none needs a routed board.

## What to order

| Part | Order code | Qty | For check |
|---|---|---|---|
| Fader, strip / group | Bourns PTB0143-2010BPA103 | 2 | 1 |
| Fader, master | Bourns PTB0144-2010BPA103 | 1 | 1 |
| Fader cap | Sifam LK111 01 (black, white line) | 3 | 2 |
| Fader cap, plain | Sifam LK110 tang 01 (RS 281-7197) | 2 | 2 |
| Fader cap, coloured trial | any 8 × 1.2 mm slot cap, white / red / yellow | 2 each | 2 |
| Key switch | C&K PVA2 EE H1 1.7N V2 | 4 | 3 |
| Key cap | C&K PV, PVGY / PVWH / PVRD / PVBK | 2 each | 3 |
| Pot, single A10K | Alpha RD901F-40-15R1-A10K | 2 | 4, 7 |
| Pot, single B10K centre detent | Alpha RD901F-40-15R1-B10K-0CD | 1 | 4, 7 |
| Pot, dual A10K | Alpha RD902F-40-15R1-A10K | 1 | 4, 7 |
| Pan pot | ALPS RK09L1240015 | 2 | 5, 7 |
| Knob, 1/4" | Elma 021-3525 | 3 | 7 |
| Knob, 6 mm | Elma 021-3425 | 1 | 7 |
| Knob caps | Elma 040-3035 red, -3015 grey, -3045 blue, -3055 yellow, -3065 green, -3025 black | 1 each | 7 |
| Jack | Neutrik NJ6FD-V | 2 | 6 |
| Signal / OL LED | Kingbright WP3VEGW | 5 | 8 |
| Panel LEDs | Kingbright WP710A10ID / -GD / -YD | 3 each | 8 |
| LED spacer | 3 mm LED, 7.6 mm long; a 3-lead one (2.0 mm pitch) for the WP3VEGW if one exists | 5; 3 | 8 |
| Standoffs | M3 F-F 24.0 mm metal; M3 11.5 mm | 2 each | 6 |
| Spacer washers | M7, 1.5 thick, ID 7.2, OD < 11.2; M9, 9.5 / 11 × 1.5; M3 3.5 mm fader spacers | 4; 2; 2 | 1, 4, 5 |

## The checks

1. **Fader footprint and height.** Lay a PTB0143 on a 1:1 print of its footprint (`goa-console:Potentiometer_Bourns_PTB0143_Slide_100mm`) and check:
   - the pads, and which side of the slot the pins are on;
   - with the 3.5 mm spacers and the prototype panel, that the blade top is 5.0 mm above the panel and its two M3
     fixings (120.0 apart) meet the panel holes;
   - the same for the PTB0144 on the master's print.
2. **Fader cap fit.** The LK111 / LK110 socket is 8.0 × 1.2 mm on an 8.0 × 1.3 mm blade:
   - the cap must push on firmly and sit about 1.0 mm above the panel;
   - also try the coloured trial caps (KC2); if one fits, the strips get white, the groups red, the master yellow.
3. **Key cap clearance.** A PV cap in the Ø8.0 panel hole has 0.30 mm radial clearance (`panel_parts_drawings.md`).
   Latch and release each colour 20 times through the prototype panel: no rubbing, no sticking. If it rubs, open the
   holes to Ø8.2 in `panel_layout.HOLE` and regenerate the panels.
4. **Alpha pot stack and footprint:**
   - the bushing leaves no spare thread with the 1.5 spacer, the 1.5 panel and the 2.0 nut: check the nut takes
     full thread with the supplied 0.4 washer left off;
   - KiCad's tab slots are drawn turned 90° from Alpha's PCB detail: check a tab against a 1:1 print;
   - the B10K-0CD detent sits at the electrical centre (measure the wiper there).
5. **RK09L pan pot:**
   - the M9 nut's thickness against the 2.0 mm of thread above the panel;
   - pin 1 at the CCW end;
   - the detent at the electrical centre.
6. **NJ6FD-V:**
   - the jack board depth: the flange front is 24.0 above the board, so 24.0 standoffs leave no load on the
     solder joints;
   - on a 1:1 print, the Ø2.0 peg (drawn 3.18 vs 3.81 off the axis) and the TN / RN / SN pads, which nobody has
     checked yet.
7. **Knobs:**
   - the Elma collet grips the 1/4" Alpha shafts and the 6 mm D RK09L shaft;
   - the Ø14.5 skirt clears the nuts and its neighbours on the 20.32 mm pitch;
   - the caps snap in.
8. **LEDs behind the panel.** Each LED on its 7.6 mm spacer under the prototype panel's 3.2 mm hole, at its design
   current (3 mm: 4K7 from 17 V, about 3 mA):
   - **WP3VEGW:** the square pad 1 is the red lead, and red and green are both readable in daylight; its three leads
     need a 3-lead spacer (or a 2-hole one opened up), about 7.2 mm long since its body is 5.0 mm tall against the
     WP710A10's 4.6; its Ø3.0 ± 0.25 dome must pass the panel's Ø3.2 hole (open D2's hole to Ø3.4 if not);
   - **brightness:** the panel LEDs look about as bright as each other;
   - **fix if not:** change R15 / R124 for the bicolour, or the 4K7s of the panel LEDs.
   The strip's D2 is the signal / overload LED since strip v4.7 (`feature_gaps.md` MET1).

## After the checks

Write each result into `panel_parts_drawings.md` and `CLAUDE.md`'s open items. Anything that changes a hole, a
footprint or a value goes through the generators (`panel_layout.py`, `footprints.py`, `gen.py`), never by hand, so
the panels, boards and 3D model stay in step.
9. **Fader residual at the bottom stop** (for `console_survey.md` CS9).
   - **Setup:** a PTB0143 wired as on the strip: 0 dBu at 1 kHz on the top, the bottom pin to ground through a short
     wire, the wiper into 100K.
   - **Measure:** the wiper level with the fader at its bottom stop, and the end resistance (bottom pin to wiper,
     with a 4-wire ohmmeter if you have one). Repeat at both ends of the travel and on the second sample.
   - **Decide:** below −80 dB, nothing to do. Worse than that, size CS9's injection resistor from the measured end
     resistance.
