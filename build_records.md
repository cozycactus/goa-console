# Build records

Values measured during assembly that later checks depend on. Fill in as the boards are built.

## 1. DRV135 coupler pairs (CS11b, `cs11b_proposal.md`)

Each console DRV135's two 10 µF NP couplers (Panasonic ECE-A1EN100U) are a pair sorted within 2 %. Their match sets the
output's balance: the DRV floats its outputs, so a coupler mismatch comes out as common mode.

**Sorting:**
- Measure all 40 parts (30 fitted + 10 sorting stock) at 100 Hz, LCR meter or the analyser's impedance mode, at the same
  temperature.
- Sort by value and pair neighbours. 40 parts give the 15 pairs within 2 % in every simulated draw
  (`sim/review/cs11/drv_couplers.py` §5).
- Fit each pair at one DRV135: the + leg's and the − leg's coupler, in either order.

**Prediction** (TI's model, 1 kΩ 0.1 % per leg; m = |C+ − C−| / C, valid for m from 1 % to 20 %, within about 2 dB;
floor about −90 dB):
- common mode / differential ≈ 20 log10(m) − 13 dB at 100 Hz;
- ≈ 20 log10(m) − 26 dB at 1 kHz.
- Examples: m = 2 % → −47 / −60 dB; m = 1 % → −53 / −66 dB.

**Bench check, per output, once the board is built:**
- Each leg into 1 kΩ 0.1 % to the board's GNDA, +4 dBu differential at 100 Hz and 1 kHz (the method of jig test 13).
- Read (V+ + V−) / 2 against V+ − V−.
- Pass within 3 dB of the prediction from this table's values. A clearly worse result is a wrong pair, a damaged
  part, or a layout path.

| Board | DRV135 | Output | Couplers (+ / −) | C+ (µF) | C− (µF) | m (%) | Predicted 100 Hz / 1 kHz (dB) | Measured 100 Hz / 1 kHz (dB) |
|---|---|---|---|---|---|---|---|---|
| group 1 | U4 | sub out | C21 / C22 | | | | | |
| group 1 | U7 | aux out | C40 / C41 | | | | | |
| group 2 | U4 | sub out | C21 / C22 | | | | | |
| group 2 | U7 | aux out | C40 / C41 | | | | | |
| group 3 | U4 | sub out | C21 / C22 | | | | | |
| group 3 | U7 | aux out | C40 / C41 | | | | | |
| group 4 | U4 | sub out | C21 / C22 | | | | | |
| group 4 | U7 | aux out | C40 / C41 | | | | | |
| master | U7 | main L | C43 / C44 | | | | | |
| master | U8 | main R | C47 / C48 | | | | | |
| master | U9 | mono | C51 / C52 | | | | | |
| master | U14 | aux 5 | C71 / C72 | | | | | |
| master | U16 | aux 6 | C84 / C85 | | | | | |
| master | U24 | C/Room L | C130 / C131 | | | | | |
| master | U25 | C/Room R | C134 / C135 | | | | | |

The master's main and C/Room outputs sit behind their mute relays (main K1-K3): measure them with the relays energised,
after the power-on delay.

The jig stub's DRV134 (MIX L) keeps an unsorted pair on purpose; jig test 13 checks the as-bought prediction against
its measured values.
