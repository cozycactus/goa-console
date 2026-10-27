# CS1: the overload LED from five points, both polarities (proposal, 2026-10-27)

**Signed off by Ruslan on 2026-10-27 (as proposed: five taps, both polarities) and applied the same day as strip v5.0;
see "Applied" at the end.** The change is `cs1_proposal.patch`. It touches tools only: `gen.py`, `strip_draw.py`,
`place_strip.py` and `netrules.py`. The simulation is `sim/review/cs1/ol_multi.py`; its output is in `sim/review/cs1/ol_multi.out`.

## 1. Why

`console_survey.md` found the strip's overload LED the weakest circuit against the library:

| | Points watched | Polarity |
|---|---|---|
| SSL 4000G | 3 stages | both |
| Sapphyre | 4 | both (diode window) |
| Ghost | 4 | positive |
| Series Five | 3 | both ("bipolar") |
| Venue Theatre (ED3151, our lineage) | 4: post-input, post-EQ, pre-mute, post-fade | positive |
| Series Two | 2 | both (window) |
| PM-5000 | 3 | both |
| **goa-console (spec 8.1)** | **1: PRESRC** | **positive only** |

`sim/review/gaps/headroom.py` shows where the strip clips first (every op-amp swings ±15.5 V, +23.0 dBu):

| Setting | Clips first at | Seen by PRESRC? |
|---|---|---|
| Unity | the input followers / receiver | yes, at the same level |
| Gain up to +15 dB | the gain stage (U1B, GOUT); EQ_O3 equal | only while no EQ cut follows |
| Fader above "0" | the post-amp (U2A, FPOST), 9.8 dB over PRE | **no**: PRE is pre-fader |
| EQ boosted | EQ_O5 / EQ_O6, up to 1.4 dB over the EQ out | yes, within the 4.6 dB margin |
| Gain turned down | the receiver (U1A, RECV) | **no**: PRESRC sits up to 15 dB lower |

**What the as-built detector misses** (simulated, §5):
- the post-amp clipping with the fader up (CLAUDE.md already notes hot synths clip it);
- the gain stage or receiver clipping when the gain or an EQ cut brings PRESRC back down;
- **any negative-going peak.** A synth pulse wave's large excursion can be on either side, and our stages invert.

## 2. The circuit

**Taps.** Five taps, each through 1K into the middle of a BAV99 (pin 3; Nexperia pinout pin 1 anode, pin 2 cathode):

| Tap | Net | Op-amp | Parts |
|---|---|---|---|
| Receiver | RECV | U1A | R128, D12 |
| Gain stage | GOUT | U1B | R129, D13 |
| EQ out (the selected path, so the EQ in / out key is respected) | EQOUT | after SW12 / C51 | R130, D14 |
| PRESRC (today's tap) | PRESRC | U7B | R39, D1: was a DO-35 1N4148, now a BAV99 |
| Post-amp | FPOST | U2A | R131, D15 |

**Positive side, unchanged.** Each BAV99's top diode charges PK, which is C12 100n ∥ R14 470K. U4A trips at
PK > VREF = +VL / 2, as built: +18.4 dBu, 4.6 dB below clip.

**Negative side, PK's mirror.**
- **Node:** each BAV99's bottom diode pulls OL_NN down. OL_NN is C103 100n ∥ R134 470K to GNDA, so attack
  (1K × 100n) and decay (47 ms) match PK.
- **Level shift:** a single-supply LM393 can't see −8 V. R132 4M99 from +VL and R133 10M to OL_NN make
  OL_NC = 2/3 +VL + 1/3 OL_NN.
- **Comparator:** U18A (LM393B, +VL / GNDD, as U4 / U17) compares OL_NC with VREF. It trips at OL_NN < −VL / 2,
  mirroring +VL / 2, and discharges OL_HOLD through R135 1K, wired-OR with U4A / R126.
- **Spare half:** U18B is tied off (+ on VREF, − on GNDD, output off). C104 decouples U18.

Hold (R115 / C97), the LED drive (U4B, Q3, Q5) and the green signal detector are untouched.

**The first try, rejected.** It biased OL_NN to −5.6 V from −VL, so its diodes stayed off below +12 dBu. NN then rests
on the balance of +VL and −VL, and the threshold drifts whenever the rails don't fall together. It lit the red at
1.7-1.9 mA on every power-down tested (§5, test 7). The mirror depends on +VL alone: every threshold is a ratio of it,
and any lag errs safe.

## 3. Drawn schematic

The overload block is now two pieces:
- **Page 8:** as before, with D1 drawn as a BAV99 and PK / OL_NN / OL_HOLD labelled.
- **Page 9** (with PFL): the four taps in a row, then the negative side (divider, C103 / R134, U18A, R135, the tied-off
  U18B).

U18 / C104 join the comparator supply drawing. The strip goes from 16 to 17 pages; no page overflows.

## 4. Placement (trial board)

The new parts are placed by `moves` alone (`moves_only`, like v4.9's), at probed free spots, so nothing else re-packs.
- **Existing parts:** D1 moves from its DO-35 spot to the bottom beside R39. Taking D1 out of the OL zone shifted five
  neighbours one slot along, so `place_strip.py` moves them back (R39, R15, R104, R107, R116, in chain order).
- **Result:** against the committed board, 1 part moved (D1) and 15 are new.

| Part | Where | Distance |
|---|---|---|
| R128 / D12 | bottom, under U1 | R128 0.6 mm from U1.1 (RECV) |
| R129 / D13 | bottom, beside U1 | 3.9 mm from U1.7 (GOUT) |
| R130 / D14 | bottom, beside C51 | 5.6 mm from C51's EQOUT pad |
| R131 / D15 | bottom, beside U2 | 4.3 mm from U2.1 (FPOST) |
| U18 | bottom, beside U4 | C104 3.9 / 3.5 mm from pins 8 / 4; R132 / R133 2.5 / 4.8 mm from pin 3; R135 4.1 mm from pin 1 |
| C103 / R134 | bottom, beside R133 | 2.3 mm |

**The long lines.**
- **PK and OL_NN:** each about 390 mm (minimum spanning tree), because the FPOST tap is at U2 (y 403) and the detector
  at the top (y 85).
  - They are held DC nodes (100n at the detector end) that carry diode current only at overload.
  - The patch puts them in the Switching class (`netrules.py`, DETECTOR), so routing keeps them 1 mm from every HighZ
    / Entry / Bus net.
  - The placer report lists PK as a 326 mm "high-Z input". It counts U4's comparator input; netrules does not (no
    length rule applies).
- **OL_HOLD:** gains R135, 10.7 mm from C97.
- **EMC:** `tools/emc_check.py` is identical to the committed board except one more aggressor net (U18's output, 4 mm
  to R135). No victim has a new nearest aggressor, and no new long switching line.

## 5. Simulation (`sim/review/cs1/ol_multi.py`)

Taps are ideal op-amp outputs; the models and switch comparators are the ones `ol.py` uses.

| Test | As built | Proposed |
|---|---|---|
| 1. Sine threshold, 1 kHz, each tap alone | PRESRC +18.4 dBu | +18.4 dBu on all five taps; PRESRC +18.1 at 50 Hz, +18.5 at 10 kHz |
| 2. 10 % pulse wave on PRESRC, narrow peak that lights | +9.01 V; negative never (> 30 V) | +9.01 V / −9.29 V |
| One half-cycle at 1 kHz that lights | +10.46 V | +10.46 V / −10.76 V |
| 3a. Gain stage clips, EQ cuts 10 dB after it | off | **RED** |
| 3b. Post-amp clips (PRE +14 dBu, fader at the top) | off | **RED** |
| 3c. Negative-going pulse, −14 V | off | **RED** |
| 3d. Receiver clips (+26 dBu in), gain −15 dB | off | **RED** |
| 4. No false red: +16 dBu on all five (1 kHz and 10 kHz); ±8 V pulses of mixed polarity; silence | | off in all |
| 5. 1 kHz bursts at +20 / +22 dBu, 1-5 cycles: red lit for | 153-175 ms | identical |
| 6. Detector current from a tap at 0 / +10 / +16 / +18 dBu | | 27 / 106 / 229 / 293 µA peak; through 20 mΩ (a generous OPA1612 output impedance at 20 kHz) that is −123 to −126 dB re the signal |
| 7. Rails switching, silence: red current while +VL > 2.5 V | 0 at power-down; 3.18 mA at power-up | identical. The first try lit 1.67-1.89 mA at every power-down |
| 8. LM393B input bias at its 25 nA max | | negative trip +0.24 dB |
| R132 / R133 at ±1 % | | negative trip ±0.35 dB |

**Notes on the results:**
- **Power-up:** the 3.18 mA there is the existing ~150 ms lamp test. C97 starts discharged, so OL_HOLD starts below
  VREF.
- **Tap loading:** the detector current flows only near the peaks, as D1's does today. It goes through 1K, so the BAV99's
  1-1.5 pF never sits directly on an op-amp output and no stability check is needed.

## 6. Checks on the trial tree (`tools/check_all.py`, 59 / 59)

**Strip:**
- **Netlist and schematic:** 902 pins / 310 parts, 0 mismatches; check_fp 0; ERC 0.
- **Board:** parity DRC 0 violations, 0 parity issues; footprint links 310 / 310; route_check 0.
- **Sims:** sim_netlist 39/39, sim_console 35/35.

**Every other board:** unchanged and passing; `netrules_test` all rules fire.

**BOM change per strip:**
- **Out:** the 1N4148 (DO-35).
- **In:** 5 × BAV99 (Nexperia BAV99,215), 1 × LM393B (U18), 5 × 1K, 4M99 1 %, 10M 1 %, 470K, 2 × 100n X7R.
- **Totals:** 15 parts more, about $0.40 per strip.

U18 draws well under 1 mA from +VL, so the console's +V worst corner rises by at most ~24 mA.

KiCad's BAV99 symbol (Diode library) names its pins K / A / K (hidden). Its graphic and the netlist match the Nexperia
pinout (1 anode, 2 cathode, 3 common); only the names are wrong.

## 7. Not proposed

- **EQ internal stages** (EQ_O3-O5). Within the 4.6 dB margin the EQ out sees them, unless a later band cuts more than
  that at the same frequency. Tapping them would also light the red while the EQ is bypassed but still running with
  boosts set.
- **Separate thresholds per tap.** Every tap is an OPA1612 / OPA1656 on the same rails, so one threshold fits all.

## 8. On sign-off (apply steps)

1. Apply `cs1_proposal.patch`, regenerate (`gen.py`) and re-export the strip netlist, BOM and PDF. Re-place the strip
   and re-run netrules.
2. Make `ol_multi.py` the strip's OL deck, with part values read from the netlist as `ol.py` does. `ol.py` keeps the
   green / LED-drive tests.
3. Bump the strip spec to v5.0 (§8.1).
4. Update `routing_guide.md`: PK / OL_NN as detector lines, on B.Cu, away from the HPF / EQ high-Z nodes.
5. Add jig checks to `test_jig_spec.md`: a negative pulse at the input, and the fader at the top with PRE at +14 dBu.
6. Record it in CLAUDE.md and run `tools/check_all.py --full`.

## Sign-off

- [x] **CS1** as proposed: five taps, both polarities (U18 added). Ruslan, 2026-10-27.
- [ ] **CS1-lite** instead: the four extra taps on the positive side only (R128-R131 and four single diodes into PK, no
  U18, no negative side). It catches 3a, 3b and 3d but not 3c (negative peaks).
- [ ] Neither.

## Applied (2026-10-27, strip v5.0)

- **Applied:** the patch, plus revision 5.0 in `gen.py`.
- **Regenerated and re-exported:** the netlist, BOM (302 parts, 3 DNP), PDF and `order_bom.csv`.
- **Re-placed:** against the committed board only D1 moved; the 15 new parts are at the trial's spots. Netrules
  re-written.
- **Simulation:** `sim/review/cs1/ol_multi.py` now reads its part values from the netlist (output refreshed). Its
  `--quick` mode runs in `tools/check_all.py --full`.
- **Documents:** spec v5.0 (changes, §8.1, §14, §15, §17); `routing_guide.md` (PK / OL_NN / OL_HOLD); `test_jig_spec.md`
  v0.8 (four overload checks); CLAUDE.md.

