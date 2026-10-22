# External PSU — Specification, v0.2 (October 2026)

The console's power supply sits outside the chassis (architecture 3.3). Sections 1–3 are the study
(requirements, four options). **Ruslan chose option B on 2026-10-22**; sections 5–7 are its design,
simulation and schematic.

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

## 4. Decision

Option B (2026-10-22): two isolated Mean Well LRS-150-24 at 21.6 V, LC filter, LDO post-regulators as
two identical floating positive regulators, crowbar and soft start per rail.

## 5. Design (one rail; the other is an identical floating copy)

```
LRS-150-24 (+, set 21.6 V) ── J (2-way) ── L 10 µH ── X_LC ─┬─ 2200 µF 35 V + 100 n ── RTN
                                                             └─ U LM1084-ADJ VI   VO ── X_OUT ── 7-way terminal
                       ADJ ── 120 Ω to VO;  1K5 ∥ 47 µF to RTN (soft start, ripple rejection)
                       diodes: ADJ → VO, VO → VI (S1G);  SS54 RTN → OUT (reverse)
X_OUT ── 220 µF + 100 n;  green LED + 4K7
crowbar: 66K5 / 10K (1 %) ∥ 2n2 → TL431 ref; TL431 cathode ── 1K ── PNP base (4K7 to OUT);
         PNP (MMBT3906) collector ── 100 Ω ── SCR gate (1K to RTN);  SCR 2N6505G anode OUT, cathode RTN
```

- **Stacking.** +V rail: OUT = +V, RTN = 0 V. −V rail: OUT = 0 V, RTN = −V. The two SMPS outputs
  are isolated, so both rails use the same positive regulator and the same crowbar.
- **Output.** 1.25 V × (1 + 1K5/120) + 55 µA × 1K5 = 17.0 V. 120 Ω also gives the LM1084's 10 mA
  minimum load.
- **LDO.** TI LM1084IT-ADJ (TO-220, 5 A, 1.3 V dropout typ.). 19 W at 4 A, 12 W typical. Tab = VO,
  so both tabs go on the heatsink through insulating pads (the two tabs sit at +17 V and 0 V).
  Heatsink ≤ 3.6 °C/W each at 40 °C ambient.
- **Crowbar threshold.** 2.495 V × (1 + 66K5/10K) = 19.1 V (±1.5 %): 2.1 V above the output, 0.9 V
  below the OPA1612's 20 V absolute maximum. A TL431 rather than a zener, because a 25 A SCR's gate
  current (up to 30 mA) would move a zener's trip point by more than a volt. The PNP gives the gate a
  hard pulse.
- **After a crowbar.** The SCR holds the rail near 1 V. The LRS-150 goes into hiccup current limiting;
  on each restart a shorted pass element puts 21.6 V back and the crowbar fires again, so the rail LED
  flashes. Switch off and repair.
- **Parts.** Bourns 2100LL-100-H-RC (10 µH, 11.4 A, 5 mΩ); 2200 µF 35 V low-ESR (Panasonic FR, 16 mm);
  onsemi 2N6505G SCR (25 A, ITSM 250 A, TO-220); TL431 (SOT-23); MMBT3906; SS54; S1G.
- **Mains side (chassis wiring, not on the PCB).** IEC inlet with fuse (T2.5A at 230 V, T5A at 115 V)
  and a 2-pole switch → both LRS-150 AC inputs (set their 115/230 V switch). FG terminals, the case
  and the NC7 pin 1 all go to the earth stud. 0 V stays isolated from earth in the PSU; it meets earth
  only at the console's star point.
- **Output connector.** Neutrik NC7FD-LX (female) on the PSU panel, wired from the PCB's 7-way terminal:
  1 earth, 2–3 +V, 4–5 0 V, 6–7 −V. Cable NC7MX ↔ NC7FX, 7 × 1.0 mm², ≤ 2 m.

## 6. Simulation (`sim/psu.cir`, one rail)

The model has a behavioural LM1084, a two-transistor SCR, a TL431 as a switched current sink, and the
LRS-150 as a 21.6 V source with an 8 A current limit. The load is the console at the end of a 2 m cable:
1 A + 3 A switched; 24 strips as 0.42 Ω + 6.4 mF (each strip's 10 Ω + 267 µF); master 1 Ω + 1.5 mF.

| Check | Result |
|-------|--------|
| Soft start, console bus 10 % → 90 % | 5 ms → 165 ms, no overshoot |
| SMPS current at start-up | 5.1 A peak (LRS-150-24 limit ≥ 6.8 A) |
| Crowbar margin in normal running | sense 2.21 V against 2.495 V; the gate never moves |
| 1 A → 4 A load step at the PSU output | no dip beyond load regulation |
| Cable drop at 4 A | 0.13 V |
| LDO dissipation at 4 A | 19.0 W |
| Pass element shorted (fault) | crowbar fires after 17 µs. Peak 20.7 V at the PSU terminals, 19.7 V on the console bus; the strips' and the master's own rails (behind 10 Ω / 1 Ω and their reservoirs) stay at 16.9 V. Rail then held at 0.9 V, SMPS in current limit |
| SMPS ripple 65 kHz through the LC filter | −47 dB: 150 mV pk-pk → 0.7 mV at the LDO input. Limited by the 2200 µF's 18 mΩ ESR, not the 71 dB of an ideal LC; a low-ESR polymer capacitor in parallel would recover more. The LDO's rejection (≥ 20 dB at 65 kHz) and the strips' RC filters (59 dB) follow |

## 7. Schematic

`psu.kicad_sch`, generated by `tools/gen_psu.py` (both rails, the output terminal, status LEDs).
The SMPS modules, the mains wiring and the NC7 socket are chassis parts wired to the PCB's terminals.
