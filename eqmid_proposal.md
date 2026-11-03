# EQM1: the mid EQ ranges retuned to the Delta's measured ones (proposal, 2026-10-28)

**Signed off by Ruslan on 2026-10-28 (as proposed) and applied the same day as strip v5.5; see "Applied" at the end.** The change is `archive/patches/eqmid_proposal.patch`. It touches tools only: `gen.py` (six resistor values),
`sim_netlist.py` (the mid checks) and `panel_layout.py` (the FREQ scale numerals).

**Asked for by Ruslan on 2026-10-28**, from the EQ overlay of a side session (`sim/eq_curves.py`). Divider resistor values
only; the mids should sweep 600 Hz - 10 kHz and about 165 Hz - 2.5 kHz, as the Delta measures.

**Calculation and simulation:**
- `sim/review/eqmid/retune.py`: the KHN tuning in closed form, fitted per band;
- `sim/review/eqmid/measure.py` on the strip netlist (sim_netlist's deck): f0, boost, cut, Q at five rotations. Its
  output is in `measure_new.out`, and for the as-built netlist in `measure_built.out`;
- TI's OPA161x model, `sim/review/strip/run_all.py none`, the seven EQ states;
- `sim_netlist`, `sim_console` and `check_all --full` on a trial tree.

## 1. Why

**The overlay** (side session, 2026-10-28) put our EQ on the Delta's Audio Precision plots: 200 Delta Tech Manual
p.17 (Deluxe Input), and the DLX user guide p.15 (D225 Mono Input), which looks like the same measurement. Our EQ
values match ED2911A / ED3344A part for part. LF and the mid peak heights are within part tolerance. The mid **ranges**
are not:

| Band | ours (as built) | Delta, measured | ED2911A label |
|---|---|---|---|
| HI-MID | 686 Hz - 10.5 kHz | ~600 Hz - 10 kHz | 600 - 10k |
| LO-MID | 148 Hz - 2.29 kHz | ~166 Hz - 2.55 kHz | 150 - 2.4k |

**The cause.** The KHN tuning (strip spec 6.2, `sim/mid_tuning.py`) was fitted to a model of the Delta's frequency pot
as a "100K C-law" dual. ED2911A calls it "DUAL 100K REVLOG", and the measured ranges differ from what that model gave.
No single tolerance explains both bands, so the model was off, not the parts.

## 2. The change

Each gang of the A10K dual is a divider from the driving op-amp: the upper section in parallel with RTOP (13K), the
lower section plus R0 to ground, and the wiper feeding the integrator through RB. With both gangs alike:

f0 = k / (2π (Rth + RB) √(C1 C2)), with k the divider ratio and Rth its Thevenin resistance.

At full CW k = 1, so RB alone sets the top of the range. At full CCW, R0 sets the bottom. The closed form gives the
as-built 686 Hz - 10.53 kHz and 149 Hz - 2.28 kHz, as the simulation does.

| Band | Parts | as built | EQM1 |
|---|---|---|---|
| HI-MID | R86 / R87 (R0) | 430R | **392R 1 %** |
| HI-MID | R56 / R57 (RB) | 4K7 | **4K99 1 %** |
| HI-MID | R88 / R89 (RTOP) | 13K | 13K |
| LO-MID | R95 / R96 (R0) | 430R | 430R (the fit asks 431R) |
| LO-MID | R60 / R61 (RB) | 4K7 | **4K22 1 %** |
| LO-MID | R97 / R98 (RTOP) | 13K | 13K |

Six parts per strip, new values only; the A10K dual and the integrator caps stay.
- **An alternative:** changing RTOP per band too (15K HI, 12K LO) keeps the law within 0.30 octave of a log sweep
  (EQM1: 0.33 / 0.31; as built 0.28), at the cost of four more value changes. It's not in the patch.

## 3. What it does (`measure.py`, on the netlist)

| Rotation | HI-MID f0, built → EQM1 | LO-MID f0, built → EQM1 |
|---|---|---|
| 0 (CCW) | 686 → **598 Hz** | 148 → **165 Hz** |
| ¼ | 1564 → 1451 | 340 → 371 |
| ½ | 2209 → 2086 | 480 → 521 |
| ¾ | 4779 → 4590 | 1039 → 1113 |
| 1 (CW) | 10519 → **9930 Hz** | 2287 → **2537 Hz** |

- **Boost, cut and Q are unchanged:** +14.4 to +14.5 dB / −14.7 to −14.9 dB, Q 1.42-1.46 at every rotation. The band-pass gain and Q
  are set by the summer, which is untouched.
- **Noise:** `sim_console` gives main L −75.82 dBu with 24 strips (−75.83 as built), and −88.68 with one (−88.69).
- **Stability** (TI's OPA161x, the seven EQ states c01, c04-c08, c15): every unit within 0.3° of the committed results.
  The KHN op-amps U12-U14 stay at 82.3-87.2°, with at most 0.33 dB of peaking.

## 4. Panel

The FREQ scales' numerals move with the law (`panel_layout.KHN`), at the same positions:
- **HI-MID:** 0.6 / 1.5 / 2.1 / 4.6 / 10KHz (was 0.7 / 1.6 / 2.2 / 4.8 / 10KHz);
- **LO-MID:** 0.17 / 0.37 / 0.52 / 1.1 / 2.5KHz (was 0.15 / 0.34 / 0.48 / 1.0 / 2.3KHz).

The ¾ numeral is dropped where it would collide, as before. `panel_fab`'s checks: strip 0 problems.

## 5. Checks on the trial tree

`check_all --full`: **61 / 61.**
- **Strip:** 937 pins / 325 parts, 0 mismatches, check_fp 0, ERC 0, 0 DRC / parity, 325 / 325 linked.
- **Re-placed:** only the six values changed; nothing moved.
- **`sim_netlist`:** 45 / 45. Four new checks give each band's peak frequency at both ends of its pot: HI 598 Hz /
  9.93 kHz, LO 165 Hz / 2.54 kHz. All four fail on the as-built netlist (686 / 10519, 148 / 2287 Hz). The boost checks'
  frequencies follow the new ranges.
- **`sim_console`:** 38 / 38. Every other board is unchanged.

## 6. On sign-off

- Apply the patch, regenerate the strip and re-export it (netlist, BOM, PDF), re-place it (values only), and run
  `order_bom.py` and `panel_fab.py` (`panels/strip.*`).
- **Update:**
  - strip spec 6.2 and the mid table, and §17's EQ figures;
  - `delta_clone_comparison.md`;
  - `eq_survey.md` (the overlay);
  - CLAUDE.md (the Decisions entry on mid-band tuning, the Verified line).

## Sign-off

- [x] **EQM1** as proposed (Ruslan, 2026-10-28): HI-MID R86 / R87 392R and R56 / R57 4K99, LO-MID R60 / R61 4K22.
- [ ] With RTOP per band as well (closer log law; four more value changes).
- [ ] Neither: keep the ranges, and record the difference in `eq_survey.md`.

## Applied (2026-10-28, strip v5.5)

- **Applied:** the patch, plus revision 5.5 in `gen.py`.
- **Regenerated and re-exported:** the strip schematic (937 pins, 0 mismatches, ERC 0), its netlist, BOM, PDF and
  `order_bom.csv` (4K7 −96, 430R −48, 392R +48, 4K99 +48, 4K22 +48).
- **Re-placed:** the six values; nothing moved.
- **Panel:** `panels/strip.*` regenerated with the new FREQ numerals (0 problems).
- **Documents:** strip spec v5.5 (changes, §6, §6.2, §17), `delta_clone_comparison.md`, `eq_survey.md`, CLAUDE.md.
- **`check_all --full`:** 61 / 61 (strip 325 / 325 linked, 0 DRC / parity; `sim_netlist` 45 / 45, `sim_console` 38 / 38).
