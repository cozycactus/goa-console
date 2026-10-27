# CS11b: matched DRV135 couplers for output balance (proposal, 2026-10-27)

**Signed off by Ruslan on 2026-10-27 (as proposed: pairs within 2 %, 10 sorting spares) and applied the same day; see
"Applied" at the end.** The change is `cs11b_proposal.patch`. It touches tools only: `master_lib.py` and `order_bom.py`.

**Simulation:** `sim/review/cs11/drv_couplers.py` on TI's DRV134 model (via `TI_MODELS`), with CS4c's 22R in each loop.
Its output is in `drv_couplers.out`.

## 1. Why

`cs11_proposal.md` found, while setting jig test 13's target, that a DRV135 output's balance is set by how well its two
10 µF couplers match.
- **Mechanism:** the couplers sit inside the Sense loops. The DRV's cross-coupled loop floats the outputs (|T| ≈ 0.96 in
  the audio band), so a coupler mismatch comes out as common mode, much as a transformer's would. The load (1 kΩ or
  10 kΩ) hardly matters.
- **Our part:** Panasonic ECE-A1EN100U, ±20 %.

| 10 µF pair (Monte Carlo, 2000 pairs) | 1 kHz median / worst 5 % | 100 Hz median / worst 5 % |
|---|---|---|
| as bought (±20 % each) | −43 / −32 dB | −30 / −20 dB |
| sorted within 5 % | −58 / −52 dB | −45 / −39 dB |
| **sorted within 2 %** | **−66 / −60 dB** | **−53 / −47 dB** |

**What it costs today.** The common mode is the programme itself, not noise. A balanced input rejects it.
- **What it touches:** output-balance measurements against ground, and the common mode on the cable (radiation,
  coupling into neighbouring cables).
- **The bass:** a worst-case pair's −20 dB at 100 Hz is a lot of the bass on the cable as common mode.
- **Where:** the main L / R / mono, aux 5 / 6, C/Room and the groups' sub and aux outputs.

## 2. The options

| | Balance, 1 kHz / 100 Hz, worst 5 % | Layout | Cost |
|---|---|---|---|
| **Sort the 10 µF into pairs within 2 % (proposed)** | −60 / −47 dB | none | 10 extra parts ($3) and an hour with an LCR meter |
| 47 µF bipolar (D8) | −45 / −26 dB as bought | re-pack both boards: no D6.3 or D8 fits at any of the 30 coupler spots (4 / 4 group, 14 / 14 master) | large |
| 100 µF (D10) | −52 / −32 dB as bought | as above, worse | large |

Sorting beats even 100 µF bought loose, and changes nothing on the boards. The bigger values would only help the low
end into 1 kΩ: −0.73 dB at 20 Hz for 10 µF, against −0.16 / −0.04 dB for 22 / 47 µF. Into 10 kΩ it's negligible. The
cross-coupled loop is the same for every value: its deepest |1 + T| below 20 kHz is 0.188, whatever the coupler.

## 3. The change

- **`master_lib.drv134()`:** on the console's DRV135s (the ones with CS4c's loop resistor), the two 10 µF carry the MPN
  note "Panasonic ECE-A1EN100U (matched pair: the two at one DRV135 within 2 %, sorted at 100 Hz)". BOM: group
  C21 / C22 / C40 / C41; master C43 / C44, C47 / C48, C51 / C52, C71 / C72, C84 / C85, C130 / C131, C134 / C135.
- **Left as bought:**
  - the LME49600 bypasses (C144, C145, C151, C152);
  - the jig stub's pair, so jig test 13 still checks the as-bought prediction against the measured capacitances.
- **`order_bom.py`:** 10 extra ECE-A1EN100U as sorting stock. The order line goes from 38 to 49.
  - **Monte Carlo:** 36 parts give the 15 pairs within 2 % in 98.5 % of draws for a uniform ±20 % spread, and 40 give
    100 %. A normal spread (σ 5 %) needs 34 for 99.6 %.
- **Assembly:** measure every capacitor at 100 Hz (LCR meter or the analyser's impedance mode), sort, pair neighbours,
  and fit one pair per DRV135. Record the values on the build sheet; jig test 13 / the master's outputs can then be
  checked against the prediction.
- **Unchanged:** the netlist, footprints and placement.

## 4. Checks (`drv_couplers.py`)

- **Balance against mismatch (10 µF):** halving the mismatch gains about 6 dB.
  - At 1 kHz: 0 % −90.6 dB; 1 % −66.2 dB; 2 % −60.0 dB; 5 % −51.7 dB; 20 % −38.1 dB.
  - At 100 Hz: 2 % −46.7 dB; 20 % −25.8 dB.
  - At 50 Hz: about 0.6 dB worse than at 100 Hz.
- **Low end:** no peaking for any value.

## 5. Checks on the trial tree (`tools/check_all.py --full`)

All 61 checks pass:
- **Regenerated:** group and master, 789 / 1786 pins, 0 mismatches. The jig stub is unchanged.
- **BOMs:** the 30 couplers carry the matched-pair note, and the LME49600 bypasses keep the plain MPN.
- **`order_bom.csv`:** ECE-A1EN100U 38 → 49.
- **Placement:** both boards re-placed for the MPN field; 0 parts moved. Netrules re-run.

## Sign-off

- [x] **CS11b** as proposed: the console's DRV135 couplers sorted into pairs within 2 %, 10 sorting spares. Ruslan, 2026-10-27.
- [ ] Within 5 % instead (−52 / −39 dB worst 5 %; fewer spares needed).
- [ ] Neither (the balance stays as bought; jig test 13 measures it).

## Applied (2026-10-27)

- **Applied:** the patch.
- **Regenerated and re-exported:** group and master netlists (789 / 1786 pins, 0 mismatches), BOMs, PDFs and
  `order_bom.csv` (ECE-A1EN100U 49 with the note and the 10 sorting spares).
- **Re-placed:** both boards for the MPN field; 0 parts moved. Netrules re-run.
- **Documents:** master spec (Part 1 note), `offboard_bom.md` (the sorting rule), CLAUDE.md, `console_survey.md`.

