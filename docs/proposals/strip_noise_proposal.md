# Strip noise proposal — the EQ's current noise (strip v4.1)

Proposal, 2026-10-24. Nothing in the design has changed. The figures hold for strip v4.2: the film / MUSE ES change
doesn't move them. **Re-evaluated on strip v4.4 on 2026-10-25 (next section): noise, stability and power are now
settled in simulation. Distortion is the one open question, and only a bench A/B can answer it.**
**Decision (Ruslan, 2026-10-25): N1 stays gated on the jig A/B (`test_jig_spec.md` 4.2). Since 2026-10-28 (§1.1 of the
jig spec) the A/B is one strip measured as built, then with the N1 set hot-air swapped in (8 packages: U1, U5-U7,
U12-U15; U15 is the HPF's since v4.3), measured again; the earlier plan built two strips of each.**

## Re-evaluation on strip v4.4 (2026-10-25)

Strip v4.4 adds the sweepable HPF (U5A summer + U15 integrators) and the U16 input followers. The N1 set is now
U1, U5, U6, U7, U12, U13, U14 and **U15** on OPA1656 (U16 is OPA1656 already); U2, U3 and U8 stay OPA1612.

**Noise, PRE** (`sim/review/strip_noise/noise.py n1`, dBu, 20 Hz–20 kHz):

| Setting | As built | N1 | N1 with OPA1642 |
|---|---|---|---|
| Gain 0 dB, EQ in | −92.8 | **−96.1** | −95.7 |
| Gain 0 dB, EQ in, HPF in (mid) | −92.7 | −95.7 | −95.2 |
| Gain 0 dB, EQ bypassed | −102.5 | −104.5 | −104.1 |
| Gain +15 dB, EQ in | −87.5 | −89.9 | −89.6 |
| Gain +15 dB, EQ bypassed | −88.6 | −90.8 | −90.5 |
| EQ in, every band +15 dB | −84.2 | −87.1 | −86.8 |
| EQ in, every band −15 dB | −95.6 | −99.2 | −98.8 |

The attribution is unchanged. With EQ in, the largest terms are U6A −101.8, U6B −102.9, U7A −103.0 and U5B −103.1 dBu,
all of them current noise; the resistors alone give −96.7 dBu.

**Noise at the console** (`tools/sim_console.py` deck, main L, faders at "0"):

| | As built | N1 |
|---|---|---|
| 24 strips routed | −79.2 dBu | **−81.9 dBu** |
| One strip routed | −91.2 dBu | −92.7 dBu |

**Stability.**
- **Method.** TI's OPA1656 model still won't solve in the strip deck, so `sim/review/strip/stripdeck.py` gained a
  second model set, `OPA_MODEL=fit`: the datasheet-fitted linear macros of the master review (`OPA1612M` / `OPA1656M`:
  open-loop gain and phase, input capacitances, output resistance). The deck also now models OPA1656 parts (U16).
- **Sweeps.** `sim/review/strip/n1_stab.py` runs all 21 states of `configs.py` three ways: TI OPA161x as built (the
  reference), fitted as built, and fitted N1. `n1_compare.py` tabulates the worst margin per unit. 0 errors.
- **The fitted models read low.** On the as-built strip the fitted OPA1612M is 3–24° below TI's model (median 18.5°).
  In the master review the fitted OPA1656M read 11–14° below its datasheet's follower curve at 10–50 pF. So the fitted
  numbers below are a pessimistic comparison, not absolute margins.
- **Results, worst phase margin over the 21 states (fitted models):**

| Unit | Stage | As built | N1 |
|---|---|---|---|
| U7B | insert return buffer (c13: input open, cables) | 54.4° | **50.1°** (worst N1 unit) |
| U12B, U14A | KHN first integrators | 60.9° | 51.6 / 51.5° |
| U13A, U14B, U15A/B | KHN / HPF integrators | 63.5° | 53.0–53.2° |
| U1B | gain stage (c02, gain CCW) | 63.4° | 57.6° |
| U5B | HF (c05, EQ cut) | 62.5° | 57.5° |
| U7A | LF (cable load) | 62.8° | 58.4° |
| U6A / U6B, U12A / U13B, U1A | EQ, KHN summers, receiver | 62.9–65.8° | 61.6–65.3° |
| U5A | HPF summer | 68.6° | 70.2° |

  The units that stay OPA1612 don't change: U3B 53.6° is the as-built worst in this model (TI: 72.1°). Closed-loop
  peaking is at most 1.47 dB.

  N1 costs the integrators about 10° and the other stages 0–6°, because the OPA1656's crossover is lower (~20 MHz
  against the OPA1612's ~40). Every N1 unit stays at 50° or more even in this pessimistic model. With the fit's own
  calibration, that is 60° or more in practice, about what U7B has today on TI's OPA161x (69.9°).

**Power.** The OPA1656 draws 3.9 mA per channel typical, 4.6 maximum; the OPA1612 draws 3.6 / 4.5. That is 16 channels
per strip:
- per strip and rail: +4.8 mA typical; +1.6 mA when both parts sit at their maxima;
- console: +115 mA typical, +38 mA at maximum. +V goes from 3.01 to 3.13 A typical, and the accepted worst corner from
  4.24 to about 4.28 A;
- per wing: +V 1.40 A typical (78 % of the MF-RX250/72's hold at 50 °C), 1.94 A worst (108 % at 50 °C, as accepted);
  −V 1.11 A typical (83 % of the MF-RX185/72's hold at 50 °C), 1.32 A at maximum IQ (99 % at 50 °C).

**Distortion: still open.**
- Since v4.3 there is no Sallen-Key: the HPF is a KHN whose summer U5A only carries signal with the HPF in.
- The exposed + inputs (signal common-mode through a source impedance) are U1A (5K bridge), U6A/B and U7A (band
  networks), U12A / U13B (KHN summers) and U5A.
- SPICE macromodels can't settle CMOS input-capacitance distortion at −120 dB levels. The jig A/B (test_jig_spec.md
  4.2, A1–A4) remains the test.

The whole-console simulation (`tools/sim_console.py`) put the strip's PRE noise with EQ in at −92.9 dBu, against
−96.7 dBu in the earlier figures. Those figures counted resistor noise only. The difference is the OPA1612's input
current noise (1.7 pA/√Hz) flowing in the EQ's high-impedance networks. This document finds which stages it comes
from and what would remove it.

Method (`sim/review/strip_noise/noise.py`):
- **Deck:** one strip from `channel_strip.net` + `jack_board.net`, using the console simulator's module builder.
- **Noise:** 20 Hz–20 kHz unweighted at PRE, with a 50 Ω source, gain at the detent, fader at "0".
- **Op-amp models:** single-pole, with noise-only sources for the datasheet input voltage noise (en) and current noise
  (in), band-averaged over 20 Hz–20 kHz. A 1/f corner near 100 Hz adds about 0.2 dB unweighted. OPA1656's 3.75 nV/√Hz
  is its datasheet 0.53 µVrms over the band, so its 1/f noise is included.
- **Attribution:** every unit noiseless but one; voltage and current noise separately; contributions above the
  resistor floor.
- **Stability:** TI's OPA161x and OPA1656 models in `sim/review/strip/` (21 states), as in `docs/reviews/strip_parts_review.md`.

## Where it comes from

| | EQ in | EQ bypassed |
|---|---|---|
| Resistors only | −96.7 dBu | −105.2 dBu |
| As built (OPA1612 everywhere) | **−92.9 dBu** | **−102.6 dBu** |

Largest op-amp contributions with EQ in, all of them current noise. Voltage noise adds less than −110 dBu from any
unit.

| Unit | Stage | Node impedance | Adds |
|---|---|---|---|
| U6A | HI-MID (22K / 22K inverting, KHN band-pass at its + input) | ~11 kΩ | −101.8 dBu |
| U6B | LO-MID (22K / 22K) | ~11 kΩ | −102.9 dBu |
| U7A | LF (22K / 22K, the LF network at its + input) | ~11 kΩ | −103.1 dBu |
| U5B | HF (33K / 33K, the shelf network on its − input) | ~16 kΩ | −103.2 dBu |
| U12B | HI-MID KHN first integrator (4K7 + pot + 13K) | 5–18 kΩ | −105.6 dBu |
| U1A | receiver (10K bridge) | ~5 kΩ | −107.3 dBu |
| U13A | HI-MID KHN second integrator | 5–18 kΩ | −108.2 dBu |

The op-amps add −95.2 dBu in all, against −96.7 dBu from the resistors. The four Delta EQ stages are the whole story:
1.7 pA/√Hz into ~11 kΩ is ~19 nV/√Hz, against the 1.1 nV/√Hz the OPA1612 was chosen for. With EQ bypassed, the
receiver's current noise is the largest op-amp term.

## Options

**1. FET-input op-amps where the impedances are high.** The current noise vanishes, and the voltage noise the OPA1612
was chosen for hardly matters in these stages. PRE noise:

| In the EQ stages + KHN + receiver | EQ in | EQ bypassed |
|---|---|---|
| OPA1612 (as built) | −92.9 dBu | −102.6 dBu |
| OPA1656 (CMOS, 3.75 nV/√Hz band-averaged, ~6 fA/√Hz) | −96.1 dBu | −104.2 dBu |
| OPA1642 (JFET, 5.1 nV/√Hz) | −95.7 dBu | −104.1 dBu |
| NE5534A (bipolar, 3.5 nV/√Hz, 0.4 pA/√Hz; single, so twice the packages) | −95.9 dBu | −104.2 dBu |
| LM4562 (2.7 nV/√Hz, 1.6 pA/√Hz) | −93.1 dBu | −102.7 dBu |

The candidates differ by less than 0.4 dB, because what matters is current noise. LM4562 doesn't help.

**2. Lower impedances.** Scaling the whole EQ network to 0.47× (every R and pot × 0.47, every C × 2.13) leaves the
response identical; checked at every frequency with all bands at full boost.

| | EQ in, flat | EQ in, all bands +15 dB |
|---|---|---|
| As built | −92.9 dBu | −84.2 dBu |
| Scaled 0.47×, OPA1612 | −95.4 dBu | −85.9 dBu |
| Option 1 (OPA1656) | −96.1 dBu | −87.2 dBu |
| Both | −97.4 dBu | −88.0 dBu |

Costs of scaling:
- It needs 4K7/5K centre-detent gain pots (stock not checked).
- It doubles every EQ stage's load (still within the OPA1612's ability to drive).
- It changes the signed "EQ with Delta values" decision, all for 1.2 dB over option 1.

**Recommendation: option 1 as packages.** The op-amps are duals, so the change is by package. Every package whose
units sit at high impedance goes to OPA1656:

| Package | Units | Notes |
|---|---|---|
| U1 | receiver, gain stage | |
| U5 | HPF, HF | |
| U6 | HI-MID, LO-MID | |
| U7 | LF, insert-return buffer | |
| U12, U13, U14 | KHN | |

U2, U3 and U8 stay OPA1612. They are the post-amp, pan buffers, post-mute follower and direct out, all at low
impedance where the OPA1612's 1.1 nV/√Hz wins. The OPA1656 is already in the BOM (master PFL sum, CRS followers).
PRE noise (dBu), as built vs the recommended set (U1, U5–U7, U12–U14 on OPA1656):

| Setting | As built | Recommended |
|---|---|---|
| Gain 0 dB, EQ in | −92.9 | **−96.1** |
| Gain 0 dB, EQ in, HPF in | −92.8 | −96.1 |
| Gain 0 dB, EQ bypassed | −102.6 | **−104.6** |
| Gain +15 dB, EQ in | −87.6 | −90.1 |
| Gain +15 dB, EQ bypassed | −88.8 | −91.0 |
| EQ in, every band +15 dB | −84.2 | −87.2 |
| EQ in, every band −15 dB | −95.6 | −99.2 |

At the console (`tools/sim_console.py`, main L, faders at "0"):

| | As built | Recommended |
|---|---|---|
| 24 strips routed | −79.2 dBu | −81.9 dBu |
| One strip routed | −91.2 dBu | −92.7 dBu |

Even at +15 dB gain, U1's swap helps. The receiver's current noise in its 5–10 kΩ bridge outweighs the OPA1656's
higher voltage noise in the gain stage.

## Stability on TI's own models (2026-11-04)

**What changed:** with `.options itl1=500` in place of the deck's `srcsteps=50 gminsteps=50`, TI's OPA1656 runs beside TI's OPA161x in the full strip
deck (ngspice 46; `sim/review/strip/n1_stab.py ti u16` and `ti n1`, 21 states of strip v5.7). So the fitted macros aren't needed for this, and the
"doesn't solve" in the next section was the options.

**As built, U16 on TI's OPA1656 (504 of 504 results):** worst U3B 59.8°, U16A/B 61.7°, next U2A 72.5°; peaking <= 1.61 dB. No other unit moves more than
0.2° from the run with U16 as an OPA161x.

**N1 (U1, U5-U7, U12-U15 on TI's OPA1656):**

| Unit | Stage | As built | N1 |
|---|---|---|---|
| U14A, U12B | KHN first integrators | 82.7 / 82.5° | **58.2 / 58.3°** |
| U7A | LF (cable load) | 77.7° | **58.2°** |
| U13A, U14B, U15A/B | KHN / HPF integrators | 87.1-87.6° | 60.7-60.8° |
| U7B | insert return buffer | 86.4° | 62.0° |
| U1B | gain stage | 84.6° | 63.8° |
| U5B | HF | 82.2° | 63.8° |
| U6A / U6B | EQ | 75.4 / 79.0° | 63.9 / 64.7° |
| U1A | receiver | 84.8° | 67.4° |
| U12A, U13B | KHN summers | 82.3° | 68.6° |
| U5A | HPF summer | 84.3° | 72.1° |
| U16A/B | followers, OPA1656 either way | 61.7° | 61.7° |

Peaking <= 1.84 dB (U7A).

- **How to read it:** N1's lowest unit (58.2°) is about level with the as-built strip's lowest (U3B 59.8°), so on TI's models stability is no obstacle to N1.
  It costs more than the fitted pair said (11-27° against 0-10°), because TI's OPA161x starts higher, but it ends higher too: the fit's 50.1° was up to
  12° low (median 6°) on these units. Distortion stays the open question, and the bench A/B and the scope check still decide.
- **Four states needed a stand-in:** `c07`, `c09`, `c10`, `c14` have no operating point with TI's models on all 24 units, on the four option sets of `stab.py`;
  of eight more tried, only relaxed tolerances got `c14` through. They ran with U2, U3, U8 on the deck's single-pole op-amp (`OPA1612_SIMPLE=1`, `results_n1_ti_n1_simple.json`).
  Checked on `c01`: all 18 OPA1656 units match the full run to the last digit in margin and peaking.
- **Not measured:** U2, U3, U8 under N1 in those four states. As built they read 72.5° or more there; in the other 17 states N1 moves them at most
  -1.5° (U3B) / +0.7° (U2A), and only those two.

`python3 n1_compare.py` prints this table.

## Stability with TI's OPA1656 model (2026-10-24; settled with fitted models on 2026-10-25, above)

**Corrected 2026-11-04: it does solve, with `.options itl1=500` (section above). The "not gmin or source stepping" below tried changing those settings, not dropping them.**

- **The model doesn't solve.** TI's OPA1656 model (SBOMAW6C) will not reach an operating point inside the full strip
  deck in ngspice 46. Any single OPA1656 instance makes it fail, even a KHN integrator with its + input grounded.
  The singular matrix sits inside the TI models.
  - The library alone is harmless; its models are subcircuit-local, so there is no name clash with OPA161x.
  - It is not the include order, the rail voltage (±12 to ±17 V), gmin or source stepping, or `rshunt`.
  - The master deck does run OPA1656 instances (PFL sum, CRS followers), so this is specific to this deck.
- **A harness fault found on the way, now fixed.** `sim/review/strip/stab.py` read the previous run's raw files when
  ngspice failed. A first "OPA1656" run therefore returned the as-built margins exactly, without having simulated
  anything. `run_config()` now deletes a tag's raw files before running and reports "operating point failed".
  The v4.1 and as-built figures were genuine runs: the as-built c01 state reproduces at U6A 75.4°, U1A 84.8°.
- **What it would take:**
  - check each changed stage on its own with the OPA1656 model (a stage deck, not the whole strip);
  - or another simulator (TI's PSpice-for-TI, LTspice);
  - or scope it on the jig (below).

## Distortion: the open question

The OPA1656 has CMOS inputs, and their capacitance changes with common-mode voltage. Distortion follows wherever an
input sees signal common-mode through a source impedance. A bipolar OPA1612 doesn't do this in the same way. In the
recommended set, every package has one unit exposed:

| Unit | Stage | What its input sees |
|---|---|---|
| U5A | HPF Sallen-Key | 27K / 56K (the textbook bad case for FET inputs) |
| U1A | receiver | 5K bridge, balanced, which partly cancels |
| U6A/B, U7A | EQ stages | their + inputs carry the band networks |
| U12A, U13B | KHN summers | |

The integrators and inverting stages with a grounded + input are not exposed. Macromodels don't predict distortion at
these levels (the parts' datasheet THD+N is in the −130s dB), so this can't be settled in SPICE. The DRV134
(≈ −106 dB) bounds what the console can show at its outputs.

## Other consequences

- **Distortion and headroom:** both parts are far below the console's other limits. The master already runs OPA1656s
  at these levels.
- **Supply current:** similar per unit; check the strip's ~85 / 72 mA budget against the datasheet before ordering.
- **DC:** the OPA1656's fA bias current also removes the small bias-current DC across the 47K and 1M bias resistors.
- **What isn't covered:** 1/f is band-averaged (A-weighting would favour the OPA1612 slightly at LF). The OPA1656's
  CMOS input capacitance and EMI behaviour are in TI's model only as far as the model goes.

## What to sign

- [ ] **N1** (recommended, but only after a bench A/B) One jig strip, measured as built and again after the swap
  (`test_jig_spec.md` §1.1 / 4.2, 2026-10-28; was "two strips, one of each"):
  - OPA1656 in U1, U5, U6, U7, U12, U13, U14 and U15 (U15 = the HPF integrators since v4.3);
  - measure noise, THD+N and SMPTE / CCIF IMD at +4 and +20 dBu with the HPF in;
  - scope every op-amp output for oscillation.

  If the OPA1656 strip wins on noise and holds distortion and stability, adopt it as a strip revision:
  - `gen.py` part and MPN;
  - regenerate, verify, re-run `sim_netlist.py` and `sim_console.py`;
  - spec §17 noise figures.
- [x] **N1a** (done 2026-10-24) The A/B is `test_jig_spec.md` 4.2 (tests A1–A4); the strip noise with current noise
  is in spec §4.
- [ ] **N2** (not recommended) Scale the EQ network 0.47×, for a further 1.2 dB.
