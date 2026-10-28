# CS6: fusible supply resistors on every ribbon module (proposal, 2026-10-27)

**Signed off by Ruslan on 2026-10-27 (as proposed: M25SI for R1-R4 on every strip and group, with the power-down rule)
and applied the same day as strip v5.3; see "Applied" at the end.** The change is `archive/patches/cs6_proposal.patch`. It touches tools
only: `gen.py`, `gen_group.py` and `place_strip.py`.

**Calculation:** `sim/review/cs6/fusible.py` (duty, faults, surges in ngspice). Its output is in `fusible.out`.

## 1. Why

`console_survey.md` §5 CS6:
- **Library:** Series Five (fusible 10R per sub-rail), Series Two (4R7 fusible), SSL (a fuse per module) and the
  PM-5000 (an IC protector per channel) all isolate a faulty module.
- **Ours:** every strip and group feeds its four rails through 10R: R1 +VA, R2 −VA, R3 +VL, R4 −VL. The audio pair are
  anti-surge 0805s, picked for their 0.5 W rating (T10), and the logic pair are plain 0805s.

**What a short does today.** A short behind one of those resistors draws ~1.66 A through it, about 27.5 W in an 0805.
- **The wing:** carries 3.1-3.7 A on +V or 2.7-3.0 A on −V, under its PTC's trip current (5.0 / 3.7 A). A PTC need not
  trip below that, so the wing stays up.
- **The resistor:** does whatever an overloaded 0805 does: chars, cracks or opens, at its own pace, possibly scorching
  the board.

## 2. The part

**Vishay Draloric M25SI, 10 Ω 5 %, 1206: M251206BB1009JP500.** Thin film on alumina, flame-retardant coat, built to fuse
at constant voltage.
- **Rating:** 0.25 W at 70 °C, ±100 ppm/K.
- **Fusing:** at 3 W or more. The datasheet's band gives 1.5-100 s at 3 W and 1 ms-0.07 s at 9 W.
- **After fusing:** it withstands ~22 V at 10 Ω.
- **Stock:** DigiKey 9,977 on 2026-10-27, $0.50 each, $0.26 per 5k reel.

| Considered | Why not |
|---|---|
| TT Electronics FCR0805 / FCR1206 (thick-film fusible) | rated 0.1 / 0.125 W, under a strip's +VA at maximum (0.125 W) |
| TT FCR1210 (0.25 W, 100 V standoff, more pulse margin) | not at DigiKey; Future: no stock, 42 weeks |
| A slow-blow chip fuse after the anti-surge 10R | two parts per rail, and the 10R still takes 27.5 W until the fuse opens |

All four resistors on both modules become the M25SI. Value, nets and filtering are unchanged; only the footprint (0805 →
1206) and the MPN change. The logic pair carry almost nothing, but a short on ±VL is the same 27.5 W fault.

## 3. Calculation (`fusible.py`)

**Normal duty:** film temperature in the 40 °C tub (`thermal_study.md`). The datasheet gives 216 K/W, and the film may
reach 125 °C.

| | typical / maximum | power | % of 0.25 W | film |
|---|---|---|---|---|
| strip R1 +VA | 89 / 112 mA | 79 / 125 mW | 32 / 50 % | 57 / 67 °C |
| strip R2 −VA | 87 / 108 mA | 76 / 117 mW | 30 / 47 % | 56 / 65 °C |
| group R1 / R2 ±VA | 107 / 135 mA | 115 / 182 mW | 46 / 73 % | 65 / 79 °C |
| R3 / R4 (±VL), both | ≤ 22 mA | ≤ 5 mW | ≤ 2 % | ~41 °C |

**Faults:** worst source impedance (the far end of a wing). RF is the fault's own resistance.

| RF | current | power in the 10R | fuses in | wing +V (typ / corner) |
|---|---|---|---|---|
| 0 Ω (hard short) | 1.66 A | 27.5 W | < 0.07 s (beyond the band) | 3.14 / 3.73 A, under trip |
| 5 Ω | 1.11 A | 12.4 W | < 0.07 s | 2.59 / 3.18 A |
| 10 Ω | 0.84 A | 7.0 W | 1 ms-0.45 s | 2.32 / 2.91 A |
| 20 Ω | 0.56 A | 3.1 W | 1-74 s | 2.04 / 2.63 A |
| 30 Ω | 0.42 A | 1.8 W | not specified (film ~420 °C) | 1.90 / 2.49 A |

−V is the same within 2 %.

- **Hard and low-resistance faults:** the fusible opens in well under a second, so only that module goes quiet. The
  wing PTC never reaches its trip current.
- **0.25-3 W:** a fault there (about 0.16-0.55 A) has no specified fusing time, as with any fuse's grey zone. Today's
  0805 has the same zone.
- **After fusing:**
  - the open part sees at most the rail, 16.9 V;
  - with a +VA-to-−VA short and the CS10 diodes, 17.3 V;
  - both under the M25SI's ~22 V.

**Surges through a module's 10R** (ngspice: the console as 28 modules on two wings, the master's branches, the 2 m
cable):

| Case | peak | energy | time above 6.5 W |
|---|---|---|---|
| Power-up through the PSU's soft start (`sim/psu.cir`: 5 → 165 ms) | 0.04 A | 0.9 mJ | 0 |
| PSU lead plugged into a running PSU (its 220 µF, then the LDO's limit) | 0.76 A | 5.1 mJ | 0 |
| **One module plugged into a live wing:** VA (10R + 220 µF) | 1.59 A | 30 mJ | 1.6 ms |
| the same, VL (10R + 47 µF) | 1.55 A | 6.1 mJ | 0.3 ms |

The fastest parts in the M25SI's band fuse in ~1 ms at 6.5 W. **A module plugged into a running console may open its
fusibles.**
- **The rule:** power the console down before plugging or unplugging a module. The 34-way IDC can't sequence ground
  before the rails anyway.
- **If it happens anyway:** it costs a 1206 on that module, nothing else.
- **Normal use:** power-up and plugging in the PSU lead stay under 3 W, where nothing fuses.

## 4. Schematic and placement (trial)

**Schematic:**
- Unchanged but for R1-R4's footprint and MPN, on the strip and the group: 921 / 789 pins, 0 mismatches.

**Placement:**
- **Group:** R1-R4 stay packed; the 1206s fit where the 0805s were. Nothing else moved.
- **Strip:** the E4 cluster by the header's power pins is too tight for four 1206s. Packed, they had pushed C2, C4 and
  the aux-send resistors R20-R31 down the board, R31 off it.
- **The strip's fix:** R1-R4 leave the packer and are placed by `moves_only`, as for CS10 / CS4:
  - R1 / R2 on top at their old spots, R3 / R4 on the bottom (probed free spots, ≤ 4.8 mm from the old ones);
  - C2 / C4 fixed where they were;
  - the old 0805 spots kept out of packing (`keepout`, marked on User.Comments).

  Nothing else moved.

## 5. Checks on the trial tree (`tools/check_all.py --full`, 61 / 61)

- **Strip and group:** 0 mismatches, check_fp 0, ERC 0, parity DRC 0 / 0, 317 / 317 and 283 / 283 linked, route_check
  0.
- **Every other board:** unchanged.
- **Sims:** `sim_netlist` 39/39, `sim_console` 35/35.
- **Placer reports:** unchanged.
- **BOM:** R1-R4 on 24 strips and 4 groups, 112 M25SI, ~$30 at the reel price, against ~$1 for the 0805s.

## 6. On sign-off

- Apply the patch, then regenerate, re-export and re-place, and re-run netrules and `order_bom.py`.
- Update strip spec §2 (power) and the master spec's group note, `offboard_bom.md`'s handling note (power down before
  plugging a module), CLAUDE.md and `console_survey.md`.

## Sign-off

- [x] **CS6** as proposed: Vishay M25SI 10R 1206 for R1-R4 on every strip and group, with the "power down before
  plugging a module" rule. Ruslan, 2026-10-27.
- [ ] Only R1 / R2 (the audio rails): the ±VL pair stay plain 0805s.
- [ ] Neither.

## Applied (2026-10-27, strip v5.3)

- **Applied:** the patch, plus revision 5.3 in `gen.py`.
- **Regenerated and re-exported:** strip and group netlists (921 / 789 pins, 0 mismatches), BOMs, PDFs and
  `order_bom.csv` (M251206BB1009JP500: 112 + 12 spares; the 0805 10Rs drop to the ground-cancel ones).
- **Re-placed:** against the committed boards only R1-R4 moved, on both. Netrules re-run.
- **Project files:** the `.kicad_pro` and jack-board files keep their committed form.
- **Documents:** strip spec v5.3 (changes, §2.1, §17), master spec (groups), `offboard_bom.md` (the plugging rule),
  CLAUDE.md, `console_survey.md`.

