# CS4c: a resistor inside each DRV135 loop (proposal, 2026-10-27)

**Signed off by Ruslan on 2026-10-27 (as proposed: 22R in each DRV135 loop, group R119-R122, master R222-R235) and
applied the same day; see "Applied" at the end.** The change is `archive/patches/cs4c_proposal.patch`. It touches tools only:
`master_lib.py`, `frags.py`, `gen_group.py`, `gen_master.py`, `gen_jig.py`, `placer.py`, `place_group.py` and
`place_master.py`.

**Simulation:** `sim/review/cs4/cs4c_drv.py` on TI's DRV134 model (SBOM004A; the DRV135 is the same die in SO-8). Its
output is in `cs4c_drv.out`. TI's model stays out of the repo: run it with `TI_MODELS=<folder>`.

## 1. Why

CS4b put a BAV199 on every jack-link signal. On the DRV135 outputs that clamps phantom power (17.7 V, not 47.7 V on the
10 µF and the Sense pin). An 8 kV contact discharge into an output still drives **5.9 A** into the DRV135's output
pin: nothing but the 10 µF and a few nH of track lies between the clamp and the pin. An HBM 2 kV pin rating is about
1.33 A / 0.2 µC.

CS4c puts a 22 Ω between each output pin (VO) and its 10 µF. The Sense pin stays on the jack side of the 10 µF, so the
resistor is inside the loop.

## 2. The circuit

| Board | DRV135 | Resistors |
|---|---|---|
| Group (×4) | U4 sub out, U7 aux out | R119-R122 |
| Master | U7 / U8 / U9 main L / R / mono, U14 / U16 aux 5 / 6, U24 / U25 C/Room L / R | R222-R235 |

- **Count:** 4 × 4 + 14 = 30 for the console.
- **Part:** 22R 0805 anti-surge, Panasonic ERJ-P06J220V, as the 75R insert sends.
- **Drawing:** each resistor is drawn in its driver's fragment, ahead of the 10 µF.
- **Refs:** `master_lib.drv_loop_rs()` creates them after every other part (after the CS4b clamps), so no existing
  ref moves.
- **Jig:** the jig stub's DRV135 is unchanged (`drv134(..., rx=False)`); it has no link clamps either.

## 3. Simulation (`cs4c_drv.py`)

**Loads:** every load sits after the relay contact (50 mΩ, 10 nH) and the link (100 nH):
- 10K // 1 nF;
- 600R;
- 600R + 47 nF;
- 10K + 47 nF;
- a TS plug (one leg shorted at the jack).

| | 0 Ω (as built) | 10 Ω | **22 Ω** | 33 Ω |
|---|---|---|---|---|
| 8 kV contact: into the output pin | 5.91 A, 0.66 µC | 1.52 A, 0.27 µC | **0.84 A, 0.19 µC** | 0.67 A, 0.15 µC |
| Differential output impedance, 1 kHz | 52.6 Ω | 62.2 Ω | **73.8 Ω** | 84.5 Ω |
| Gain into 600R (10K: +6.69 dB) | +6.35 dB | +6.28 dB | **+6.19 dB** | +6.11 dB |
| 20 kHz into 600R + 47 nF | −0.06 dB | −0.10 dB | **−0.14 dB** | −0.19 dB |
| Clip (0.1 % THD) into 600R per leg | +27.5 dBu | +27.4 dBu | **+27.2 dBu** | +27.1 dBu |
| Clip into 10K per leg / TS into 10K | +28.4 / +22.4 dBu | the same | **the same** | +28.4 / +22.3 dBu |
| 1 V step overshoot, 10K // 1 nF | 0.3 % | 0.6 % | **1.2 %** | 1.7 % |

**22 Ω** brings the output pin under the HBM 2 kV level, 0.84 A against 1.33 A and 0.19 µC against 0.2 µC. The costs:
- 0.16 dB into 600R, 0.02 dB into 10K;
- 0.3 dB of headroom into 600R;
- 0.08 dB more at 20 kHz into 47 nF of cable.

33 Ω buys 20 % less current for 50 % more of each cost.

**Output impedance (a correction to CS4b).** CS4b §3 said the driver's feedback would remove a series resistor from the
output impedance. TI's model says otherwise. The cross-coupled loop floats the outputs; it does not null their
resistance. TI's own 50 Ω per leg already shows as 52.6 Ω differential, and 22 Ω adds 21 Ω to that.

**Stability.** The only loop through an output pin is the cross-coupled one: VO+ → 10 µF → Sense+ → the other side's
amplifier → VO− → 10 µF → Sense− → back. It is a positive-feedback loop just under unity in the audio band (|T| 0.95-0.96
into 10K, 0.74-0.83 into 600R); that is how the DRV floats its outputs. A Tian probe at VO+:
- **Dips:** for every load and resistor, |1 + T| has no dip above 20 kHz deeper than 0.97 up to 300 MHz.
- **Peaking:** no response peaks above 20 kHz.
- **Damping:** a series resistor reduces |T| slightly, so it moves the loop away from the critical point, not towards it.

**The 10 µF away from the driver.** On the group the aux-out DRV135's (U7) 10 µFs sit ~115 mm from it (C40 / C41 at
y 99, U7 at y 214), the sub out's (U4) at 15 / 31 mm, and the master's U9 at 17 / 26 mm. No free spot for a 5 mm
radial cap exists within 20 mm of these drivers, so they stay; that track is inside the loop.

With 30-240 nH in both the VO run and the Sense run, at 0 and 22 Ω: no change. The overshoot stays within 0.1 % of the
values above, and the dips stay at 0.966-1.0 (`cs4c_drv.py` §6). The DRV135's loop is only ~1.5 MHz wide. Route each VO run beside
its Sense run, so their loop area stays small.

## 4. Schematic and placement (trial)

**Schematic:**
- Group 789 pins / 283 parts (+8 / +4); master 1786 / 617 (+28 / +14). Pages unchanged: 12 and 30.
- Pin by pin against the committed netlists, only the new parts differ. Each DRV's VO pin and its 10 µF's pin 1 now
  sit on either side of the resistor.

**Placement:**
- **Spots:** by `moves_only`, at probed free spots nearest each output pin. Distance from the pin:
  - group 1.5 / 7.8 / 5.9 / 6.9 mm;
  - master 0.1-6.1 mm, median 2.2.
- **R120:** its first spot, 6.9 mm from U4 pin 1, hid R88's silk reference, so it moved to the bottom at 7.8 mm.
- **R225:** its first refused spot was a symptom of the next point. It is back at 2.3 mm.
- **Nothing else moved.** With the resistor in the loop, a 10 µF's pin 1 is no longer on the driver's output net, so
  the attach engine had aimed the minus-leg caps at the Sense pin instead and re-packed them. That moved C22 on the
  group, and on the master seven caps plus R50.
- **The fix:** `placer.py` takes `wire=` (refs its attach targets see through, here the loop resistors), so each 10 µF
  keeps the pin it had. Without `wire` the placer is unchanged.
- **Reports:** both boards' decoupler and high-Z reports are unchanged.

## 5. Checks on the trial tree (`tools/check_all.py --full`, 61 / 61)

- **Group and master:** 0 mismatches, check_fp 0, ERC 0, parity DRC 0 / 0, 283 / 283 and 617 / 617 linked,
  route_check 0.
- **Every other board:** unchanged (the jig stub's netlist too).
- **Sims:** `sim_netlist` 39/39, `sim_console` 35/35.
- **Net rules:** re-run; the new nets are Default class and every rule fires.
- **BOM:** +4 ERJ-P06J220V per group, +14 on the master: 30 for the console, about $0.10 each.

## 6. On sign-off

- Apply the patch, then regenerate, re-export, re-place and re-run netrules.
- Update the master spec's Part 1 note and §7, and CLAUDE.md.
- CS4b §3's output-impedance sentence is already corrected, with a pointer here.

## Sign-off

- [x] **CS4c** as proposed: 22R ERJ-P06J220V inside each DRV135 loop (group R119-R122, master R222-R235). Ruslan, 2026-10-27.
- [ ] CS4c with 33R instead (0.67 A; −0.24 dB into 600R).
- [ ] Neither (keep 5.9 A into the output pin at 8 kV; the clamp alone).

## Applied (2026-10-27)

- **Applied:** the patch.
- **Regenerated and re-exported:** group and master netlists (789 / 1786 pins), BOMs, PDFs and `bom/order_bom.csv`
  (ERJ-P06J220V: 30 + 10 spares).
- **Re-placed:** both boards; against the committed boards only R119-R122 and R222-R235 are new.
- **Project files:** netrules re-run. The `.kicad_pro` files and the jack boards keep their committed form; the jack
  boards' rewrites were UUID-only.
- **Documents:** master spec (Part 1 note), CLAUDE.md, `docs/studies/console_survey.md`.

