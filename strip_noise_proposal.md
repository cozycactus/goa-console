# Strip noise proposal — the EQ's current noise (strip v4.1)

Proposal, 2026-10-24. Nothing in the design has changed. The figures hold for strip v4.2: the film / MUSE ES change
doesn't move them. **Not ready for sign-off as a design change: the stability check is unresolved (below).**

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
- **Stability:** TI's OPA161x and OPA1656 models in `sim/review/strip/` (21 states), as in `strip_parts_review.md`.

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

## Stability with TI's OPA1656 model: unresolved

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

- [ ] **N1** (recommended, but only after a bench A/B) Build two jig strips:
  - one as built, one with OPA1656 in U1, U5, U6, U7, U12, U13 and U14;
  - measure noise, THD+N and SMPTE / CCIF IMD at +4 and +20 dBu with the HPF in;
  - scope every op-amp output for oscillation.

  If the OPA1656 strip wins on noise and holds distortion and stability, adopt it as a strip revision:
  - `gen.py` part and MPN;
  - regenerate, verify, re-run `sim_netlist.py` and `sim_console.py`;
  - spec §17 noise figures.
- [ ] **N1a** (now, no design change) Add the A/B to `test_jig_spec.md`, and the strip noise with current noise to
  spec §17 (already noted there).
- [ ] **N2** (not recommended) Scale the EQ network 0.47×, for a further 1.2 dB.
