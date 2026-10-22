# External PSU — Study, v0.1 (draft, October 2026)

The console's power supply sits outside the chassis (architecture 3.3). This study sets the
requirements from the strip v4.0 current budget and compares four ways to meet them. It needs
Ruslan's choice before a schematic.

## 1. Requirements

| Item | Value | Source |
|------|-------|--------|
| Rails | ±17 V | strip and master design rails |
| Current | +V 2.65 A typical, 3.8 A worst; −V 2.23 A typical, 2.8 A worst; **design 4 A per rail** | master spec §27 |
| Abs max at the console | OPA1612 ±20 V; DRV134 ±18 V recommended | datasheets |
| Ripple and noise at the output | ≤ 1 mV pk-pk, 20 Hz–20 kHz; nothing large above 20 kHz either | the strips' 10 Ω + 220 µF filter only starts at 72 Hz |
| Link | 7-pin XLR (console: Neutrik NC7MD-LX). Pin 1 earth; 2–3 +V; 4–5 0 V; 6–7 −V. Cable 7 × 1.0 mm², ≤ 2 m (≈ 70 mV drop at 4 A) | master spec §24 |
| Grounding | 0 V floats inside the PSU; it meets mains earth only at the console's star point. Pin 1 carries mains earth to the console chassis | architecture 3.4 |
| Start-up | Both rails rise together; the console's power-on mute (master §8) keeps the outputs muted for 2.8 s | — |
| Faults | Short-circuit proof per rail; **overvoltage crowbar per rail**, because a shorted pass element would put 21.6–29 V on a rail rated ±20 V | — |

The console's load capacitance is about 6.5 mF per rail in the strips plus about 5 mF in the master.
At a 5 A current limit the rails charge in ≈ 40 ms; a soft start of ≈ 100 ms keeps the supply out of
current limit.

## 2. Options

| | A. Linear | B. SMPS + LC + LDO (recommended) | C. SMPS + LC only | D. Used Soundcraft CPS275 |
|---|---|---|---|---|
| How | Toroid 2 × 20 V (separate secondaries), bridge and 2 × 10 000 µF per rail, each rail its own floating positive regulator (output to 0 V for −V) | Two isolated Mean Well LRS-150-24 (24 V 6.5 A, set to 21.6 V), 10 µH + 2200 µF, LT1084-class LDO (5 A, 1.5 V dropout), floating like A | Two Mean Well LRS-150-15 (15 V 10 A, set to 17.0 V), π filter 2200 µF + 10 µH + 2200 µF, common-mode choke | Soundcraft's PSU for large Delta-era consoles: ±17.5 V at 5.25 A, +5 V 1 A, +48 V 0.3 A |
| Regulator heat per rail | 23 W typical, 33 W at 4 A, 44 W at 4 A and +10 % mains | 12 W typical, 18 W at 4 A | none | (inside the unit) |
| Heatsinking | about 1 °C/W per rail; pass transistors (two TO-247 per rail), since an LM338 in TO-220 (4 °C/W junction-case) cannot shed 23 W | 3.6 °C/W per rail | — | — |
| Size / weight | 300 VA toroid, 2 big heatsinks, about 5 kg | 2 × 150 W SMPS modules, small sinks, about 1.5 kg | smallest | 2U rack unit |
| Ripple at the output | 1.3–2 V pk-pk at the regulator input; 60–75 dB rejection → about 0.5–1 mV | SMPS 150 mV pk-pk at ≈ 65 kHz; LC: −71 dB → about 40 µV; then LDO | about 0.1–0.5 mV of switching residue plus spikes; the strips' RC filters take another 59 dB at 65 kHz | Soundcraft spec (manual not obtained) |
| Low mains | valley 21.5 V at −10 % and 4 A (needs ≥ 20 V) | SMPS regulates; no effect | none | — |
| Risks | heat; mains transformer build | SMPS EMI and earth-leakage current (Y caps) | switching residue reaching audio, regulation only ±1 % | age (recap), unknown connector pinout (needs an adapter cable to the NC7), availability |
| Cost (parts) | high (toroid, sinks, case) | medium | lowest | used-market price |

Common to A–C: IEC inlet with fuse and switch, an earth-bonded metal case, a 2-pole mains switch. Per
rail: an SCR crowbar triggered at ≈ 19.5 V (zener + gate resistor), which shuts the SMPS down
(hiccup) or blows the fuse; reverse diodes and a 100 nF / 10 µF output stack at the XLR; soft start
(A: on the regulator's ADJ pin; B: the LDO's ADJ; C: the SMPS's own).

## 3. Recommendation

**B: SMPS with an LC filter and a linear post-regulator.** It is as quiet as A at the output (the LC
filter removes the switching ripple before the LDO, and the LDO removes what's left). It runs a third
as hot and weighs a third as much. The isolated SMPS outputs make the floating-rail trick free (two
identical positive regulators). Keep the PSU external and in a steel or aluminium case, as decided, so
SMPS fields stay away from the console.

A is the purist's choice if heat and weight don't matter. C is fine for the test jig and is cheap to
try first; its residue can be measured on the jig (test 6). D is attractive if a CPS275 turns up: get
its pinout from the Soundcraft manual and make an adapter cable to the NC7.

## 4. Next

- Ruslan to choose A–D.
- Then: a schematic (generator like the others), the crowbar and soft-start sims in ngspice, and the
  heatsink and case layout.
