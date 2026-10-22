# Test Jig — Specification, v0.2 (draft)
## Bus and grounding tests before ordering 24 strips

Implements `console_architecture.md` section 9 with the designs as they now stand
(strip spec v4.0 with its jack board, master spec v0.6). Goal: confirm the Delta-style unbalanced bus with ground
cancel (config **D**) against the same bus without it (config **A**), and measure noise, hum,
crosstalk, PSRR, distortion and switching clicks on real hardware.

---

## 1. What gets built

| Item | Qty | What it is |
|------|-----|------------|
| Channel strip | 4 | Real strip main boards (`channel_strip.kicad_sch`) with their jack boards (`jack_board.kicad_sch`) on the 10-way link, fully populated. The jig tests the boards that will be built, not stand-ins. Panels optional: the controls work without them. |
| Master stub | 1 | Bus side of the master only (section 2). |
| Load board | 1 | Dummy channels that raise the bus noise gain to the full 24-channel value (section 3). |
| Ribbon | 2 | 34-way, 28 AWG flat cable with 6 crimped IDC sockets (4 strips, master stub, load board): one 0.6 m (a 12-strip wing, ~0.5 m, plus slack), one 3 m (worst case and the hum-pickup tests). |
| Ground bar | 1 | M4 copper bar with a lug per board, as the console's star point. |
| Supply | 1 | ±17 V bench or the console PSU, ≥ 1 A per rail (4 strips draw about 0.35 A from +V, 0.3 A from −V; master stub and load board about 0.15 A). |

The four strips also settle the strip-level open items (strip spec 16.1, 17): PVA2 orientation
(moulded "2" in the pad 1/4 column, by continuity), fader pad pattern, panel stack height,
NJ6FD-V body height (sets the jack-board standoffs), knob fit, and the function checks in 4.1.

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

As generated: one config jumper (GC REF: 1-2 = D, 2-3 = A) sets every summing amp's + input and
the re-inverters' buffered reference together, and a separate 22 Ω tie jumper covers test 3. AUX 2
gets its own summing amp as well, for the crosstalk test. Unused buses (SUB 2–4, AUX 3–6) are tied
to AGND at the stub, standing in for their summing amps' virtual earths. Power comes from a bench
supply on a screw terminal, with the master's MF-RX160/72 PTCs and SS54 reverse diodes. The PFL
detect is one LM393 and an LED. The BNC outputs and the test points are as listed above.

## 3. Load board

Brings the bus noise gain up to what 24 routed channels give (1 + N), without 24 strips:

- On the ribbon like a strip, with its own spade to the ground bar and a 10 Ω ground-cancel
  resistor to pin 26, so its resistors return to a strip-like ground.
- Per MIX / SUB 1 bus: 20 × 4K7 1 % from the bus pin to local ground, in switchable groups of
  1, 3, 4, 12 (DIP switch or jumpers): any N from 0 to 20 extra channels.
- Per AUX 1 / PFL: 20 × 22K 1 % in the same groups.
- Switch at the bus end of each group, off grounds the group (as the routing switches do).
- As generated, each group is one equivalent resistor: 4K7 / 1K58 / 1K18 / 392R, and 22K / 7K32 /
  5K49 / 1K82. That gives the same thermal noise and noise gain as 1 / 3 / 4 / 12 separate
  channels. Each group has a C&K OS102011 slide switch, and there are five buses: MIX L, MIX R,
  SUB 1, AUX 1, PFL.
- Bus capacitance: the strips' DG413 routing switches put about 44 pF each on MIX / SUB buses
  (35 pF on, 9 pF off), about 1.1 nF with 24 strips and the ribbon. Per MIX / SUB 1 bus, a jumper
  adds 1 nF C0G to AGND, so tests 1, 8 and 10 can run with the full-console bus capacitance.

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
| 8 | Switching clicks | 1 kHz at 0 dBu and silence: toggle every routing (DG413), ON and PFL switch; record MIX L and PFL, raw and through a 20 kHz low-pass. Also DC at each DG413's bus pin. | No audible click. DG413 charge injection: sim −55 dBu peak in the 20 kHz band (`sim/routing_switch.cir`), target ≤ −50 dBu; DC < 1 mV. |
| 9 | Soft mute | ON switch off with 1 kHz at +10 dBu. | Depth ≥ 70 dB (netlist sim 76 dB at POST), no click. |
| 10 | Stability | Square wave 1 kHz and 10 kHz at MIX L with the 3 m ribbon, N = 20. | No ringing or oscillation; overshoot < 10 %. |
| 11 | Balanced output | DRV134 on MIX L: level, both legs, then one leg grounded. | +6 dB differential and single-ended; no change in THD. |

### 4.1 Strip function checks (each of the four strips)

Targets from `tools/sim_netlist.py` (the exported netlists, 30 checks) and `sim/mid_tuning.py`.
1 kHz, 0 dBu at the line input unless stated.

| Check | Target |
|-------|--------|
| PRE level, gain at the detent; POST with the fader at the top | 0 dBu ± 0.3; +9.9 dBu |
| Gain pot CCW / CW | −14.9 / +14.8 dB |
| Ø: phase at PRE | 180° |
| HPF in: −3 dB | 86 Hz |
| HF at 12 kHz, CW / CCW | +11.4 / −11.7 dB |
| HI-MID boost at 670 Hz (freq CCW), 2.2 kHz (mid), 10.5 kHz (CW) | ≈ +14.5 dB each; peak frequency within ±15 % of 684 / 2213 / 10471 Hz |
| LO-MID boost at 148 Hz, 480 Hz, 2.31 kHz | ≈ +14.5 dB each; peak within ±15 % of 148 / 479 / 2291 Hz |
| LF at 54 Hz, CW / CCW | +14.3 / −14.4 dB |
| EQ IN off, all bands at full boost | flat within 0.5 dB |
| Insert: nothing plugged (normal), send/return through a cable | 0 dB change |
| Direct out (DIR + PRE 5-6, aux 6 at the top) | 0 dBu at J5 tip; aux 6 bus silent |
| Routing: L-R, 1-2, 3-4 on and off (DG413) | +3.8 dBu on the bus with pan at centre; off: below −80 dB; LED follows the switch |
| PFL: bus level, PFL DET, LED | 0 dBu; master PFL logic switches |
| OL LED | lights at about +18 dBu at PRE |
| Supply current per strip (typical) | about 85 mA +V, 72 mA −V; more than 110 / 90 mA means a fault |

## 5. Decisions the jig settles

- **Ground cancel (D) vs plain (A).** If D passes tests 2 and 4, it stays as decided and the
  balanced-bus options B/C (architecture section 9) are dropped for good. If D fails, B/C need
  different strips and come back as a separate design study.
- **Master-end tie.** Test 3 confirms the "no tie" decision against hardware.
- **Power on the ribbon.** Test 6 decides between ribbon power and separate wiring.
- **PVA2 orientation, fader footprint, panel height, jack-board depth** — from the strips themselves.
- **Ribbon power at the v4.0 strip current** (about 85 mA per strip on +V): test 6 at N = 20, plus the
  measured drop along the 0.6 m ribbon with the load board drawing a 12-strip wing's current.

## 6. Not in the jig

- Faders, inserts, monitoring, meters and the power-on mute: tested on the real master later.
- Configs B and C (balanced bus): only if D fails.

## 7. Still to do

- ~~Schematics for the master stub and the load board~~ done 2026-10-22: `tools/gen_jig.py` writes
  `jig_master_stub.kicad_sch` (127 parts) and `jig_load_board.kicad_sch` (50 parts) from the master's
  own circuit functions, now in `tools/master_lib.py`. Both: netlist 0 mismatches, every pin on a
  pad, ERC 0.
- ~~PCB placement~~ done 2026-10-22: `tools/place_jig.py` → `jig_master_stub.kicad_pcb` (160 × 125 mm:
  six BNCs and the balanced XLR on the front edge, ribbon header on the left, bench terminal top right,
  labelled jumpers) and `jig_load_board.kicad_pcb` (120 × 85 mm: a labelled 5 × 4 grid of slide switches,
  each with its group resistor). Both: 0 schematic-parity issues, 0 DRC violations; placement only, no
  copper. Routing is Ruslan's.
- The strips need routed boards: placement is done (`channel_strip_v4.kicad_pcb`,
  `jack_board.kicad_pcb`); copper routing is Ruslan's.
- For the ribbon-current test, the load board could also carry a switchable dummy load
  (about 1 A per rail) to emulate a 12-strip wing.

*Document version 0.2 — October 2026 (strip v4.0: jack board, DG413 routing, KHN mid bands)*
