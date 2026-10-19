# Test Jig — Specification, v0.1 (draft)
## Bus and grounding tests before ordering 24 strips

Implements `console_architecture.md` section 9 with the designs as they now stand
(strip spec v3.1, master spec v0.6). Goal: confirm the Delta-style unbalanced bus with ground
cancel (config **D**) against the same bus without it (config **A**), and measure noise, hum,
crosstalk, PSRR, distortion and switching clicks on real hardware.

---

## 1. What gets built

| Item | Qty | What it is |
|------|-----|------------|
| Channel strip | 4 | Real strip PCBs from `channel_strip.kicad_sch`, fully populated. The jig tests the boards that will be built, not stand-ins. |
| Master stub | 1 | Bus side of the master only (section 2). |
| Load board | 1 | Dummy channels that raise the bus noise gain to the full 24-channel value (section 3). |
| Ribbon | 2 | 34-way, 28 AWG flat cable with 6 crimped IDC sockets (4 strips, master stub, load board): one 0.6 m (a 12-strip wing, ~0.5 m, plus slack), one 3 m (worst case and the hum-pickup tests). |
| Ground bar | 1 | M4 copper bar with a lug per board, as the console's star point. |
| Supply | 1 | ±17 V bench or the console PSU, ≥ 1 A per rail. |

The four strips also settle the strip-level open items: PVA2 switching sense, fader pad pattern
and panel stack height (strip spec 13.1), soft-mute depth and click, OL and PFL detect.

## 2. Master stub

A cut-down master built from the same circuits (master spec sections 2, 3, 12, 13, 18):

- One 34-pin header, like every board on the jig: a single ribbon with crimped sockets for
  the four strips, the master stub and the load board.
- MIX L and MIX R: summing amp (OPA1612, 4K7 ∥ 100 pF, ferrite) + re-inverter (2K2 0.1 %).
- SUB 1: same as MIX (for routing and SUB-to-MIX crosstalk).
- AUX 1: OPA1656 summing amp (22K ∥ 100 pF) + re-inverter (for the 22K bus and its crosstalk).
- PFL: OPA1656 summing amp + re-inverter, PFL-detect comparator and LED.
- GCANCEL buffer (OPA1612 follower) for the re-inverters.
- **Config jumper JP_GC (3-pole, one per bus amp group):**
  - D (ground cancel): summing-amp + inputs on GCANCEL, re-inverter + legs on GCANCEL_BUF.
  - A (plain): both on the master's AGND.
  - Third position for the 22 Ω master-end tie test (GCANCEL to AGND through 22 Ω), the case
    the simulation says to avoid; measuring it confirms or refutes the simulation.
- Outputs: each re-inverter output to a BNC through 100 Ω, plus one DRV134 on MIX L for the
  balanced-output checks. No faders, inserts or monitoring.
- Power entry as the master (5-pin XLR or bench leads), PTC per rail, reverse Schottkys.
- Test points: GCANCEL, GCANCEL_BUF, each SUM and re-inverter output, ±V.

## 3. Load board

Brings the bus noise gain up to what 24 routed channels give (1 + N), without 24 strips:

- On the ribbon like a strip, with its own spade to the ground bar and a 10 Ω ground-cancel
  resistor to pin 26, so its resistors return to a strip-like ground.
- Per MIX / SUB 1 bus: 20 × 4K7 1 % from the bus pin to local ground, in switchable groups of
  1, 3, 4, 12 (DIP switch or jumpers): any N from 0 to 20 extra channels.
- Per AUX 1 / PFL: 20 × 22K 1 % in the same groups.
- Switch at the bus end of each group, off grounds the group (as the routing switches do).

With the four strips routed, N runs from 4 to 24, so the measured noise can be compared
directly with the table in architecture section 2.4 (−100.4 dBu expected at N = 24, OPA1612,
4K7).

## 4. Measurements

Test gear: an audio analyser (QuantAsylum QA403 or similar, or a good interface with REW),
a scope, a 1:1 isolation transformer for ground injection, a 0.1 Ω 3 W resistor.
Levels in dBu, 20 Hz–20 kHz unweighted unless stated. Record every result in config A and D.

| # | Test | Method | Target |
|---|------|--------|-----------|
| 1 | Noise floor vs N | Strip inputs shorted, faders at the "0" mark, routed to MIX; load board N = 0, 8, 20. RMS and FFT at MIX L. | Within 2 dB of architecture 2.4 (−100.4 dBu at N = 24) plus strip noise. No discrete hum lines above −110 dBu. |
| 2 | Ground-difference rejection | Put 0.1 Ω in one strip's spade lead; drive 50 Hz through it from the isolation transformer (1 A = 100 mV of ground offset). Measure at MIX L. Repeat at 1 kHz. | D at least 40 dB better than A at 50 Hz (simulation: −71 vs +28 dB for a 1 V difference with 24 routed). |
| 3 | 22 Ω master-end tie | As test 2 with JP_GC in the tie position. | Confirms the simulated loss (simulation, 1 V difference at 10 Hz: −7 dB with the tie, −71 dB without); if not, revisit master spec section 3. |
| 4 | Hum pickup | 3 m ribbon laid along a loaded mains cable; then a deliberate ground loop through a synth connected to two strips. | No 50/100/150 Hz lines above −100 dBu at MIX L in D. |
| 5 | Crosstalk | One strip, 0 dBu, routed only to AUX 1 (pin 24); measure on MIX L, MIX R, SUB 1, AUX 2 (the ungrounded neighbours 17–25). 1 kHz, 10 kHz, 20 kHz. | ≤ −80 dB at 10 kHz between adjacent buses. |
| 6 | PSRR, power on the ribbon | 100 mV ripple at 100 Hz, 1 kHz, 10 kHz injected on +V, then −V (series transformer or a modulated supply). Measure at MIX L. | Ripple at output ≤ −100 dBu at 100 Hz. If not, try separate 18–20 AWG power wiring (architecture 3.2). |
| 7 | THD+N, all channels | All four strips driven at 0 dBu, routed L-R, faders at "0", N = 20 on the load board. | ≤ 0.005 % at 1 kHz at MIX L; no rise with N. |
| 8 | Switching clicks | 1 kHz at 0 dBu and silence: toggle every routing, MUTE and PFL switch; record MIX L and PFL. Also DC at each switch's bus side. | No audible click; transient < −60 dBu at MIX L; DC < 1 mV. |
| 9 | Soft mute | MUTE with 1 kHz at +10 dBu. | Depth ≥ 80 dB (simulation 86 dB), no click. |
| 10 | Stability | Square wave 1 kHz and 10 kHz at MIX L with the 3 m ribbon, N = 20. | No ringing or oscillation; overshoot < 10 %. |
| 11 | Balanced output | DRV134 on MIX L: level, both legs, then one leg grounded. | +6 dB differential and single-ended; no change in THD. |

## 5. Decisions the jig settles

- **Ground cancel (D) vs plain (A).** If D passes tests 2 and 4, it stays as decided and the
  balanced-bus options B/C (architecture section 9) are dropped for good. If D fails, B/C need
  different strips and come back as a separate design study.
- **Master-end tie.** Test 3 confirms the "no tie" decision against hardware.
- **Power on the ribbon.** Test 6 decides between ribbon power and separate wiring.
- **PVA2 switching sense, fader footprint, panel height** — from the strips themselves.

## 6. Not in the jig

- Faders, inserts, monitoring, meters and the power-on mute: tested on the real master later.
- Configs B and C (balanced bus): only if D fails.

## 7. Still to do

- Schematics for the master stub and the load board. Both can come from the existing
  generators: the master stub reuses `gen_master.py`'s circuit functions (they would need
  moving into a shared module), the load board is a few dozen resistors and switches.
- PCB layout of the strip (CLAUDE.md step 4) comes first, since the jig needs real strips.

*Document version 0.1 — October 2026*
