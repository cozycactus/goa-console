# Master parts review — the six proposals in master_section_spec.md v0.6

Reviewed 2026-10-23 for sign-off. Each proposal was checked against the spec, the generated schematics
(`master.net`, `group.net`, `jig_master_stub.net`), the manufacturers' datasheets, the Delta drawings in `ref/`
and new ngspice runs. One analyst worked on each item; a second reviewer then re-derived the key numbers and tried to
refute every verdict. All six verdicts survived; where the second reviewer corrected a figure or a value, this document
uses the corrected one. Nothing has been changed in the design yet: the changes below wait for your sign-off.

Review sims are kept in `sim/review/` (last section).

## Summary

| # | Proposal | Verdict | In one line |
|---|----------|---------|-------------|
| 1 | GCANCEL buffer | **Sign off**; spec text corrected | Needed on the master (−37.7 dB unbuffered against a −54…−65 dB floor). Costs no package. The spec's −71 / −31 dB figures are its 1 nF bus capacitance, not the buffer. |
| 2 | OPA1656 on the aux / PFL sums | **Aux: OPA1612 instead. PFL: keep OPA1656.** Plus 22 pF on every re-inverter | Aux buses always carry all 24 strips' 22K, so noise gain is fixed at 25: OPA1612 −94.3 dBu vs OPA1656 −92.3. PFL is switched (N = 1–4): OPA1656 3.6 dB better. |
| 3 | Mute relays, main + C/Room | **Sign off with changes** | Relays are needed (the DRV134 steps 1–3 V CM on rail skew). Add K6 on phones, ground the lines through the free NC contacts, LM393B, R49/R53 4K7, D7 footprint. |
| 4 | Series-J112 PFL switcher | **Replace with one DG413** | The generated switcher does not switch: off gate at −9.3 V, −27 dB crosstalk, −2.4 V DC on CRS (meters read +7 dB at silence), a +5 dBu thump per press. |
| 5 | 20-LED meters | **Sign off with changes** | Bar logic is correct (simulated). The SOT-23 current-source PNPs run away thermally (Tj > 150 °C): SOT-223 + 120R. LM2901B, GaP LEDs (no InGaN), calibration target. |
| 6 | Sub AFL | **Sign off as generated** | Taps the same point as the Delta D203's group key, works in every routing state, solo level within 0.2 dB of a strip PFL. |

## What to sign

Tick or strike each line. The bracketed letter is the recommendation.

- [ ] **S1** GCANCEL buffer kept as generated; spec §3 / §9 / §10 / §15 text corrected (item 1).
- [ ] **S2** Aux sums (master aux 5/6, group aux, jig AUX1/2) → OPA1612; PFL sum stays OPA1656 (item 2).
- [ ] **S3** 22 pF C0G on every re-inverter, 100 pF across every level buffer's 4K7, 22 pF on the mono re-inverter
  (item 2). This touches MIX L/R, SUB, aux, PFL and the jig.
- [ ] **S4** Relays: NC-to-ground contact map, K6 on phones, LM393B, R49/R53 2K2 → 4K7, D7 footprint (item 3).
- [ ] **S5** PFL switcher → DG413 with the additions in item 4 [recommended]; *or* the Delta-faithful JFET
  switcher (soft transition, about 38 parts and selected J112s).
- [ ] **S6** Meters: BCP53-16 + 120R current sources, LM2901B, Kingbright GaP LEDs, new calibration rule (item 5).
- [ ] **S7** Sub AFL kept as generated (item 6).
- [ ] **S8** PFLDET back-feed fix: master-side clamp [recommended]; *or* a diode per key (touches the strip netlist).

Two of the changes touch recorded decisions. They are listed separately so neither changes silently:

- [ ] **D1** GCANCEL keeper (item 1): 100K from GCANCEL to master GNDA, which leaks −79 dB. Without it the line floats
  whenever the master runs with no strip or group on a wing. This is a (very weak) master-end tie, against the "no tie"
  decision. Options: 100K / 1M (−99 dB) / none, plus a "never power the master alone" rule in the spec.
- [ ] **D2** CLAUDE.md "NE5534 good for sub/aux summing" and console_architecture.md line 291: on this console's aux
  buses (N fixed at 24) the OPA1612 is quieter than the NE5534 (−94.3 vs −92.5 dBu), and ±17 V is above the
  NE5534's recommended ±15 V. Replace the line with "OPA1612 on MIX/SUB/aux sums, OPA1656 on PFL".

---

## 1. GCANCEL buffer

**Proposed (§3).** U9A, an OPA1612 follower, drives the + legs of all re-inverters (GCANCEL_BUF). The summing amps' +
inputs stay on the raw GCANCEL line. The stated reason: 13 re-inverters × 4K4 ≈ 340 Ω on a 0.42 Ω line pull it 0.12 %
towards master ground, giving −31 dB of leakage; buffered, "−71 dB at 10 Hz, −31 dB at 1 kHz".

**As generated.** The buffer is U1A (it shares a package with the MIX L summer U1B; the spec's "other half spare"
does not exist). Since the M1 split it drives five re-inverters on the master (MIX L/R, aux 5/6, PFL: 880 Ω). Each
group has its own buffer for its two re-inverters (net GC_BUF, 2.2 kΩ). The line is 10 Ω / 28 = 0.357 Ω (24 strips +
4 groups). No series resistor and no capacitor on the buffered net.

**Findings.**
- Needed on the master. Unbuffered, the 880 Ω is a tie to master ground: −37.7 dB of the master-to-strip ground offset
  reaches MIX at N = 32 (24 strips + 4 sub pans + 4 returns), −40.3 dB at N = 24. Buffered, the buffer's own error is
  −118 dB at 50 Hz (TI OPA161x model).
- The real floor is the re-inverter resistor match: four 2K2 0.1 % give −54 dB worst case and about −65 dB RMS, flat
  with frequency. The spec's "55–60 dB CMR on top" is in fact the floor.
- The spec's −71 dB / −31 dB come from the deck's 1 nF bus-to-master-ground capacitor acting through the 4K7
  feedback (2πfC·4K7). The buffer cannot change that term. A realistic bus capacitance is 20–65 pF: −58 dB at 1 kHz.
  At 10 kHz the summer's loop gain at noise gain 33 sets −42 to −51 dB whatever the buffer does.
- The group buffers make no measurable difference: each group's own 10 Ω (R5) already makes it one of the 28
  contributors, and loading the line there shifts its weight by 0.45 % (−35 dB of a group-to-strip offset). They cost
  no package, so keep them, but the spec should not claim they improve rejection.
- Stability as generated is fine for the buffer itself: 3–15 pF of placed trace, about 11–14 % overshoot (datasheet
  Fig. 19). **Never put a resistor outside the loop**: 10 Ω into 880 Ω leaks −39 dB, worse than no buffer. If more
  capacitance is ever unavoidable, use in-loop isolation (47R output → load, 1K load → −IN, 220 pF output → −IN).
- Bias, offset and noise of the buffer are irrelevant on 0.357 Ω (−134 dBu of noise, 34 dB under the bus floor).
- With no strip or group on either wing (master bring-up on the bench), nothing holds GCANCEL: the 5–6 + input bias
  currents walk it out of range and every master sum is undefined (decision D1).
- Hum in context: at a realistic 10 mV / 50 Hz offset, the 0.1 % worst case leaves about −92 dBu at MIX L, above the
  −100 dBu N = 24 noise floor; the RMS case is about −103 dBu. Order a few 0.05 % / 0.01 % ratio-matched quads with
  the jig parts; they are a likely fallback, not a remote one.

**Alternatives considered.** 10K re-inverters without a buffer (−50.8 dB, but 5.6 dB more MIX noise at low channel
counts); INA134 (−58.6 dB, 8.2 dB noisier); INA1650 (−80 dB load term, 4.9 dB noisier, TSSOP-14); INA1620 (better
match, but still needs the buffer, WQFN-24). None beats the follower.

**Changes (S1).** No circuit change. Spec: U9A → U1A (no spare half); load = 5 re-inverters, 880 Ω on the master,
2 re-inverters, 2.2 kΩ per group (GC_BUF); line 0.357 Ω; replace the −71 / −31 dB figures with the budget above; add
the layout rule (U1A output straight to the net, ≤ 50 pF, no series R). Test jig tests 2/3: expect −54 to −65 dB at
50 Hz with 0.1 % re-inverters, and read TP2 − TP1 (buffer error, expect < −90 dB). Optional: a 220R@100 MHz ferrite in
GCANCEL at each module's pin 26, matching FB1–FB5 (the six raw + inputs are the only unfiltered bus-connected pins);
decide after a scope check.

**Bench.** Jig test 2 config D at 50 Hz and 1 kHz, each bus output separately; TP2 − TP1; scope GCANCEL_BUF with a
10 kHz square coupled onto GCANCEL (≤ 20 % overshoot); LCR measurement of MIX bus pins to master GNDA; master DC
state with no strips (with or without the keeper).

## 2. OPA1656 on the aux and PFL sums

**Proposed (§13, §14, §18).** OPA1656 (CMOS) dual per aux bus and on PFL: summer (22K ∥ 100 pF) + re-inverter. The
reason given: "aux sends usually carry a few channels", where the OPA1612's 1.7 pA/√Hz × 22K costs it 3.8 dB.

**As generated.** OPA1656ID on master U12 (aux 5), U14 (aux 6), U18 (PFL); group U6; jig U5, U6, U7. Matches the spec.

**Findings.**
- The premise does not hold for the aux buses. The strip's R20–R25 22K hang permanently from the aux pot wipers (there
  is no per-strip aux on/off), and AUX1–6 run straight through the master between the wings. So every aux summer always
  sees N = 24 and runs at a noise gain of 25. There voltage noise dominates, and the OPA1656's 1/f-rich en (0.53 µVrms
  over the band, not the spec's "3.3 nV/√Hz average": 3.75) is multiplied by 25.
- Noise at the re-inverter output, 20 Hz–20 kHz unweighted, N = 24: **OPA1612 −94.3 dBu**, OPA1656 −92.3,
  NE5534A −92.5, LM4562 −93.0, OPA2210 −93.9; resistor-only floor −95.2. The 2 dB survives A-weighting (−96.2 vs
  −94.3). The two parts break even at N ≈ 10, so the OPA1656 only wins on a console with ≤ 9 strips.
- The PFL bus is switched (only pressed sources connect, N = 1–4). There the OPA1656 is right: −104.8 / −103.2 /
  −101.1 dBu at N = 1 / 2 / 4 against −101.2 / −100.6 / −99.5 for the OPA1612.
- Summer stability: ≥ 55° phase margin with either part, N = 1 or 24, Cbus 100 pF–10 nF, with or without the ferrite
  (fitted models and TI's OPA161x model). 20 kHz −0.22 to −0.34 dB, −3 dB at 70–85 kHz, as the spec says.
- **Re-inverters have no feedback capacitor, and they ring.** With TI's own OPA161x model, the 4 × 2K2 re-inverter
  peaks +14.7 dB at 14.8 MHz with 70 % step overshoot (phase margin about 11°): the op-amp's input capacitance against
  2K2. TI's own G = −1 test circuit uses 2 kΩ / 2 kΩ with 5.6 pF. 22 pF C0G across the feedback 2K2 and across the
  + leg's lower 2K2 (same value and tolerance on both legs, so the GCANCEL balance holds) gives no peaking, −3 dB at
  3.3 MHz, and a CMR term of −102 dB at 1 kHz / −76 dB at 20 kHz. The same `reinv()` builds every re-inverter, MIX
  and SUB included.
- Same failure class in the stages that follow: `level_buffer()` (master U6B, U15A; group U5B, U9A, U9B: follower with
  4K7 from output to −IN, no capacitor) oscillates at 10–17 MHz in TI's model with any wiper impedance; 100 pF across
  the 4K7, as `post_amp()` already has, fixes it. The mono re-inverter U6A (10K / 10K, no capacitor) peaks +33 dB at
  9.8 MHz; 22 pF across R38 fixes it.
- Abs max: OPA1612 and OPA1656 are both rated 40 V; the op-amps sit behind the 1R / 10R filters and see 33.9 V in the
  PSU fault case. The NE5534's recommended maximum is ±15 V.

**Changes (S2, S3).**
- `gen_master.py` aux 5/6 and `gen_group.py` aux: summer and re-inverter 'OPA1656' → 'OPA1612', inside one
  `new_package()` so each pair stays in one dual. `gen_jig.py` AUX1/AUX2 likewise; `test_jig_spec.md` line 34.
- PFL keeps the OPA1656 (master U18, jig U7).
- `master_lib.reinv()`: 22 pF C0G (≤ 5 %) across the feedback 2K2 and across the + leg's lower 2K2.
- `master_lib.level_buffer()`: 100 pF C0G across the 4K7 (keeps the Rg option for +6 / +10 dB).
- `gen_master.py` mono: 22 pF C0G across R38.
- Spec §13, §14 (OPA1656 column −104.8 / −101.1 / −96.2 / −92.3; N = 24 marked as the aux operating point, N = 1–4
  as PFL's), §15 / §23 to post-M1 per-module counts (master 13 OPA1612 + 1 OPA1656, group 7 + 0; console 41 + 1),
  §18 (PFL keeps OPA1656 because the bus is switched), §27 (about −4 mA per rail). "GBW 53 MHz" is the G = 100 figure;
  unity-gain bandwidth is 20 MHz.

**Bench.** Aux noise at N = 24 on the load board (expect −94.3 dBu), PFL noise at N = 1 (−104.8 dBu). Jig test 10
extended: 100 MHz scope with a short ground spring on every re-inverter output, the level buffers and the mono output,
idle and with a 10 kHz square, before and after the capacitors.

## 3. Mute relays (main, C/Room)

**Proposed (§8, §20).** Omron G6K-2F-Y DC12, normally-open contacts after the DRV134 Sense node: three on main L/R/mono
(already a decision), two more on C/Room (the proposal). Coils from +V through 560 Ω, one MMBT3904, 1N4148 per coil;
LM393 rail monitor, 2.8 s timer, fast release.

**As generated.** K1–K5 match the spec, coil polarity and contact map checked against Omron's terminal drawing
(COM 3/6, NC 2/7, NO 4/5). Gaps: NC pins unconnected, LM393s without an MPN (non-B allowed), D7 is BZX84C6V2 (SOT-23)
on a SOD-123 footprint, spec §10 still lists K1–K3 / U6.

**Findings.**
- The relays are needed, and after the Sense node is the right place. A behavioural DRV134 (datasheet block diagram)
  is quiet with symmetric rails (≤ 5 mV), but any rail skew drives its amps against the dead rail: 1.2–3.0 V
  common-mode and 0.2–0.75 V differential for 10–100 ms of skew. Skew is likely: the two LRS-150-24s start
  independently (Mean Well: setup 500 ms). Only a contact after the driver removes that. At closure the Sense nodes sit
  at about 1 mV, so the contacts make dry.
- G6K-2F-Y DC12 figures confirmed (9.1 mA, 1,315 Ω ±10 %, 80 % must-operate, 10 % must-release, 150 % max;
  10 µA / 10 mV failure-rate level, so dry-circuit capable). Coil drive: +2 % to +26 % over must-operate across
  tolerance and 70 °C coil; 118 % at the 19.7 V fault peak. Now sold as "Aratas (formerly Omron Components)";
  Digi-Key Z129-ND active, 11,828 in stock, $5.05, 26-week factory lead time. Buy the relays early.
- Release: the datasheet's 3 ms is without suppression. With the 1N4148 the contacts open ≤ 8.5 ms after a threshold
  (coil L up to 3 H, comparator at minimum sink). On mains-off the outputs first move ≥ 28–45 ms after a threshold at
  the modelled 0.25 V/ms fall, so a zener is not needed. No relay beats a crowbar collapse (outputs move in 1.5 ms).
- **Phones need a relay.** The OPA1612 + LME49600 composite is DC-coupled. After a crowbar the SCR holds one rail
  near 0.9 V until mains-off while the other stays up; RAIL_OK opens K1–K5, but the phones output sits at the dead
  rail plus the LME49600's swing limit: about 0.6–1.5 V DC, 20–45 mA into 32 Ω, for the whole fault. A sixth G6K after
  the feedback tap adds ≤ 0.1 Ω outside the loop.
- The LM393 runs at 34.0–34.6 V across the package, over the non-B part's 30 V recommended maximum: specify LM393B
  (36 V recommended, 38 V abs max).
- At a single-rail loss one LM393 output must sink 21.8–23.7 mA (10K pull-up + the 2K2 timer reset + the 2K2 fast
  release), above the non-B's 20 mA abs max and near the B's 25 mA. R49 and R53 at 4K7 halve that (12.0–12.9 mA);
  release, close and re-arm timing are unchanged in the sim. Faults longer than about 8 ms then re-arm the full delay
  (4 ms with 2K2).
- With NO contacts only, the output legs float whenever the console is off or muted. Grounding them through the
  unused NC contacts (COM = connector, NO = driver, NC = GNDA) costs nothing and gives idle balanced inputs a defined
  line and phantom/ESD a path. The Delta never floats an output leg.
- The Delta has no output relays and no power-on mute (ED2780 sh.1–3), only AC coupling and a C/R MUTE switch.
- Not covered, by design: the other ten DRV134 outputs (aux 1–6, sub 1–4) see the same skew steps. Acceptable for
  sends and recorders, not for powered foldback on an aux. The root fix is at the PSU (both LM1084 soft starts held
  until both LRS-150s are up), outside this review.

**Changes (S4).**
- `master_lib.relay()`: contact map COM 3/6 = connector, NO 4/5 = driver Sense node, NC 2/7 = GNDA. K1–K5.
- `gen_master.py` headphones: K6 G6K-2F-Y DC12 with its 560R and 1N4148 on RLY_DRV, NC to PHONESGND; the jack moves
  to the contact side, the 4K7 feedback stays on the amp side. Six coils, about 55 mA (Q1 forced beta 34).
- MPN TI LM393BIDR on U10, U11, U19.
- R49, R53 2K2 → 4K7.
- D7: MPN BZT52C6V2 (SOD-123), or keep BZX84C6V2 on SOT-23.
- Spec §7 (NC3MAV), §8 (six relays, contact map, release ≤ 8.5 ms, re-arm after ~8 ms faults, Aratas / Z129-ND),
  §10, §20 / §23 (NJ6FD-V, three G6K on monitoring), §21 (phones relay), §25 / §27 (six coils), §28, plus a note
  that aux and sub outputs are not muted.
- Optional: wing-rail sensing so a tripped MF-RX160/72 also mutes; a panel C/R MUTE on its own driver for K4–K6;
  50 V Sense-loop caps if phantom on an output must be survivable (they see about 27 V). Do not fall back to a
  latching relay: it would hold its state on mains-off.

**Bench.** Relay sample release time with the 1N4148 (expect ≤ 8.5 ms); pull-in at 16.5 V with a hot coil; rail skew
(one LRS-150 delayed 0.1–1 s) with 10K and 32 Ω loads; **mains-off with the real PSU and full load, scoping RLY_DRV
against the outputs** (mandatory: a fall 4× faster than modelled leaves about 7 ms of margin); one rail crowbarred
for 10 s with 32 Ω phones (expect 0 mA with K6); contact resistance after weeks energised.

## 4. Series-J112 PFL switcher

**Proposed (§17, §19).** Four J112 in series (MON_L, PFL → CRS_L; MON_R, PFL → CRS_R), gates through a 1N4148 to a
control line swinging ±VL, 47K gate–source, 100K / 100 nF ramp "for a click-free transition", OPA1612 followers.

**As generated.** Q2–Q5 MMBFJ112 (no MPN), 47 µF + **1M** at each source (the spec says 47K), 47K gate–source on the
JFET side of the cap, 100K at CRS (not in the spec), 100K / 100 nF ramps, OPA1612 followers (U20).

**Findings.**
- **It does not switch.** The 100K ramp resistor and the two 47K gate–source resistors form a divider, and with the
  47K on the floating side of the 47 µF the gate current can only return through the JFET's own channel. The off gate
  reaches only −9.3 V (spec: −16 V) and the off JFET sits at pinch-off, conducting 26–45 µA. Simulated with Fairchild's
  MMBFJ112 model and the datasheet corners (Vp −1 to −5 V), and reproduced independently:
  - crosstalk −27 dB (−9 dB at the Vp −5 V corner);
  - −2.4 V DC on CRS (−4.1 V at the corner), which the meters read as +6.9 dB (peak) / +10.8 dB (average) with no
    signal, and which sits on the C/ROOM and PHONES pot wipers;
  - a 2.9 V step at CRS on every press, +4.8 dBu in the audio band, still settling 0.3 s later;
  - 5.6–6.5 % THD at +20 dBu, because the "off" JFET clamps CRS below about −8 V.
- The spec's own 47K-to-ground version also fails at the Vp corners (−10.4 dB crosstalk at Vp −5).
- Both misread the Delta (ED2780 sh.1): there R40 / R64 47K return to the **op-amp side** of the 47 µF, the gates are
  pulled down by saturated 2SC2240 transistors with Miller capacitors, and there is no follower at CRS. A faithful copy
  works (−120 dB THD at +20 dBu, −91 dBu click, about 1 ms crossfade), but here it needs new MON buffers (MON_L/R are
  AC-coupled 47K nodes, and the master has no spare op-amp half), two Miller drivers, an FET-input follower and J112s
  selected for |VGS(off)| < 2.3 V (a −5 V part leaks and pumps DC above about +20 dBu).
- One DG413, the strip's routing part on the same rails and +5VL circuit, does the job: crosstalk −137 dB at 1 kHz,
  −111 dB at 20 kHz, independent of level; THD −100 dB at +20 dBu into 100K (−120 dB into 1M); break-before-make
  25 ns. Its cost is a hard cut: a tick when switching with programme playing, as on most consoles.
- The CRS follower must have FET inputs with any series switch: the OPA1612's bias current across 100K ∥ 1M is
  5.5 mV typ / 23 mV max at CRS, which steps at every switch (−43 dBu click). An OPA1656 there gives −88 dBu.
- With the RC ramps gone, the PVA2's ≤ 3 ms contact bounce reaches PFLDET directly: 5 or more threshold crossings per
  press, each a DG413 cut. 1 µF from PFLDET to GNDD at the master leaves exactly one crossing each way (5–8 ms).
- Other options simulated: a DG413 virtual-earth switch (strip-routing topology; best THD, but one more dual, an
  extra inversion and a −44 dBu click) and a relay (perfect isolation, but a dead gap, bounce and the worst splatter).

**Changes (S5, DG413).**
- New U: Vishay DG413DY-E3, the strip's pin map: SW1 (1 IN, 3 S = PFL→L, 2 D = CRS_L), SW4 (8, 6 = PFL→R, 7 = CRS_R),
  SW2 (16, 14 = MON_L, 15 = CRS_L), SW3 (9, 11 = MON_R, 10 = CRS_R); 13 +VA, 4 −VA, 12 +5VL, 5 GNDD; 3 × 100 nF.
  Logic 1 (PFL pressed) = SW1/SW4 on, logic 0 = SW2/SW3 (MON).
- +5VL on the master as on the strip: 4K7 from +VA, BZX84C5V1 to GNDD, 1 µF, PWR_FLAG.
- PFL_ON_RAW (U11 pin 7) pull-up: 100K to +5VL, replacing R97 10K to +VL (10K would take 2.2 mA of the zener's
  2.5 mA). Optional 10K in series with each IN pin (the LM393 low at −16.75 V is inside the DG413's abs max but new
  territory) and 10M from PFL_ON_RAW to U11 pin 5 for about 20 mV of hysteresis.
- 1 µF from PFLDET to GNDD at the comparator inputs (debounce). Never feed the DG413 IN pins from an RC: they are
  TTL-level, not Schmitt.
- U20 CRS followers OPA1612 → OPA1656. Keep C91/C92/C95/C96 47 µF + R107/R109/R112/R114 1M and R111/R116 100K
  (1M optional, for −120 dB THD). Keep U19A + R98 for the flasher hold (D14).
- Delete Q2–Q5, D16–D19, R108/R110/R113/R115, R99/C88, R100/C89.
- `master_lib.jfet_switch` and gen_master.py lines 113–131 replaced by the DG413 block (DG and ZEN symbols and MPNs as
  gen.py lines 9–10). Title block v0.5 → v0.6.
- Spec §17 diagram, §19 (DG413, BBM 25 ns, hard cut, PFLDET debounce; MON_L/R are AC-coupled nodes, not op-amp
  outputs), §23 (J112 ×4 → DG413 ×1, OPA1612 −1, OPA1656 +1, BZX84C5V1).

If you prefer the Delta's soft switch, sign the JFET version only with all of: 47K gate returns to the op-amp side of
each 47 µF, a new OPA1612 dual as MON followers, NPN Miller drivers (MMBT3904 to −VL, 100K pull-up, 2.2 nF C–B, R_be
≥ 220K), OPA1656 CRS followers, and selected J112s (|VGS(off)| < 2.3 V) or J113s.

**Bench.** CRS DC < 1 mV and meters dark at silence; press and release with 0 dBu programme on the phones (one tick, no
burst); isolation ≤ −105 dB at 20 kHz with a +20 dBu muted source; power cycling with programme (no DG413 latch-up).

## 5. 20-LED meters

**Proposed (§22).** Precision full-wave rectifier with peak / average detectors (already simulated), the Delta's
ladder (16K … 91R, R309–R329), 5 × LM2901 per side, two series strings of 10 LEDs per side, each fed by a PNP current
source (75R, two-diode reference).

**As generated.** Matches the Delta ED2780 sh.3 topology and the simulated detector. Q6–Q9 MMBT3906 (SOT-23), 75R;
LM2901 and LEDs without MPNs. The current-source PNPs sit 50–115 mm from the tops of their strings.

**Findings.**
- The bar graph works. The spec's "each comparator shorts out its LED" is wrong in mechanism (the comparator's emitter
  is the package's shared −VM pin) but right in effect: comparator k pulls the anode of LED k to −VM, bypassing the
  rest of its string; the lowest comparator still on sets the top of the bar, and the source current flows either
  through the lit LEDs or into that comparator. Simulated −25 to +20 dBu: LED 1 at −19, LEDs 1–11 at 0, all 20 at +18,
  no ghosts, string current constant. Ladder taps within −0.22…+0.12 dB of the 2 dB grid (−20 reads −19.7, as on the
  Delta).
- **The SOT-23 current sources overheat.** When a string is dark (string B is dark below 0 dBu, i.e. most of the
  time) the PNP holds about 32 V at 6–7 mA: 195–280 mW in a 225 mW / 556 K/W package. The 2-diode reference sits at
  ambient while the PNP heats, so current rises with temperature: Tj > 150 °C in every corner at Ta 40 °C. The Delta ran
  2SA970s (300 mW) at about 230 mW.
- String current is set by 2·Vd − Vbe and spreads ±17 % with junction tolerances; at 75R it is 6.9 mA typical,
  5.7–8.1 mA, above the LM2901's guaranteed 6 mA sink, which allows a ghost on the LED above the bar. BCP53-16
  (SOT-223, 80 V) with 120R gives 4.2–5.7 mA (4.9 typical), always below 6 mA; Tj 55–70 °C at Ta 40 °C with about
  1 cm² of collector copper.
- The comparators span about 33 V: over the non-B LM2901's 30 V recommended maximum. LM2901B: 36 V recommended,
  3.5 mV max offset (±0.45 dB at the −20 LED, against ±0.9 dB for the non-B).
- LED headroom: each string has about 31 V for 10 LEDs. InGaN green (3.3 V typical, 4.1 V max) collapses string A at
  low rails, blanking LEDs 1–10 while 11–20 light. GaP / GaAsP / AlInGaP with Vf ≤ 2.6 V max leave ≥ 7.7 V of
  current-source headroom.
- Calibration: the 10R meter-branch drop puts VM at about 16.45 V, so the 0 dB tap is about 0.63 V, not 0.649 V
  (a 0.27–0.29 dB error if calibrated to 0.649 V). Calibrate to the LED instead.
- Panel: the 40 LEDs fit (two 95 mm columns at 5 mm pitch beside the fader, ≥ 10.8 mm from its courtyard). The
  CLAUDE.md "meter ladders 26–30 mm" hot spot is harmless: the taps are DC nodes of 91 Ω–4.9 kΩ.

**Changes (S6).**
- Q6–Q9: onsemi / Nexperia BCP53-16 (KiCad Transistor_BJT:BCP53, SOT-223-3_TabPin2; pin map {1: B, 2: C, 3: E, 4: C});
  fallback 2N3906 TO-92 with 100R. R161, R163, R197, R199 75R → 120R. Spec: "PNP ≥ 60 V; dark-state dissipation
  ≈ 32 V × I; SOT-223 with ≥ 1 cm² collector copper".
- MPN TI LM2901BIDR on U29–U33, U36–U40.
- LEDs: Kingbright WP710A10GD green (D28–D37, D40, D56–D65, D68), WP710A10ND amber (D41–D45, D69–D73), WP710A10ID red
  (D46–D49, D74–D77); 3 mm diffused, about $0.25, all in stock. Spec rule: Vf ≤ 2.6 V max, no InGaN.
- Spec §22 calibration: "apply 0 dBu and set RV7 / RV8 so the 0 dB LED (D40 / D68) just lights" (U4 ≈ 0.63 V).
- Spec §22 mechanism wording as above; §27 meter strings 4 × ~5 mA = 20 mA.
- `place_master.py` NEAR: (D28, Q6), (D40, Q7), (D56, Q8), (D68, Q9), so each current source sits at the top of its
  string.
- Optional: R160 / R196 91R → 88R7 (−20 LED at −20.0 dB); one shared reference per side as on the Delta; C125 / C141
  (2.2 µF) and C128 / C144 (1 µF) as film or C0G, because X7R DC-bias loss shifts the 73 ms / 0.55 s ballistics by
  10–25 %.

**Bench.** PNP tab temperature after 30 min dark (< 70 °C at room temperature); string current from the Re drop
(4–6 mA); 1 dB-step sweep −25 to +20 dBu (each LED within ±0.5 dB of its point); dark-room ghost check; scope DET and
the master post-amp output with the level parked on a threshold (no hysteresis, as on the Delta: look for flicker and
for comparator-dither noise near the fader).

## 6. Sub AFL

**Proposed (§12).** AFL key (PVA2) on each sub: 22K from POST_SUBn to the PFL bus (bus end grounded when released),
+VL → 100K → PFLDET, 4K7 → red LED.

**As generated.** Group SW2, R22 22K from S_POST, R23 100K, R24 4K7, D1 red (no MPN). Placed at the strips' PFL key
position, labelled in the 3D panel. The group's +VL is +VBUS through 10R, the same as the strip's and master's (the
strip's 5.1 V rail is +5VL, which feeds only its DG413s), so a sub AFL press reads the same 1.5 V on PFLDET as a strip
PFL press.

**Findings.**
- The Delta D203 group module has no group solo of its own: its "PFL" key belongs to the lower return, which is fed
  from the group's post-fader node unless RET is pressed (ED2778A; Tech Manual pp. 61–62). In normal use it is a
  post-insert, post-fader AFL of the group, but it goes dead in SUB mode. Ours taps the same point (POST_SUBn:
  post-insert, post-fader, mono, pre-pan, pre-MIX switch) and works in every routing state.
- Solo level at the fader's "0" mark: −0.20 dB against 0.00 dB for a strip PFL and an aux AFL at 1 kHz (the 100K
  post-amp input loading the fader wiper, the same on the strips). No click and no change at the sub output when
  pressed (the resistor end moves between GNDA and a virtual earth, both at 0 V).
- Console-wide defect, copied by sub AFL but not caused by it: a released PFL/AFL switch leaves its pole-B node
  floating, so PFLDET back-feeds every released key's 100K + 4K7 + LED. With two or more solos pressed, all other
  PFL/AFL LEDs glow faintly (3 µA at 2 presses, 22 µA at 8), and PFLDET reads 9.0 V at 24 presses, not 11.8 V. The
  auto-switch threshold still holds in every case. The Delta avoids it: its LED is not on the detect node.
- Cost of keeping: about $3.5 per group, already placed. Dropping it leaves a gap in the PFL key row and no way to
  hear a sub's post-insert, post-fader signal.

**Changes (S7, S8).**
- No circuit change to sub AFL. LED MPN: one 3 mm red part for every PFL/AFL LED (the strip PFL LED's).
- Back-feed fix, preferred (master only, no strip or group regeneration): 2 × 1N4148 in series from PFLDET to GNDD and
  R95 220K → 330K (PFL_REF 0.497 V). One press 0.92 V (1.85× the threshold; −4 mV/°C), 24 presses 1.29 V, released
  LEDs ≤ 36 nA. Works with the 1 µF debounce of item 4. Nothing else reads PFLDET.
  Alternative: a 1N4148 in each key's 100K branch (`master_lib.afl()` and the strip's R33): one press 1.49 V,
  24 presses 11.6 V; 38 diodes, and it reopens the signed-off strip netlist.
- Spec §12: "one PVA2, three resistors and one LED"; the tap point and the Delta comparison above. §12 ground note:
  since M1 the group's GNDA joins GCANCEL through R5 10R like a strip, so the premise ("referenced to master ground")
  no longer holds; the remaining master-referenced feeds into a bus are the master's own aux 5/6 AFL 22Ks, which pass
  the master-to-strip ground offset into PFL at 0 dB while pressed. §19: 38 PFLDET positions (24 strips, 12 group keys,
  2 master) and the levels of the chosen fix.

**Bench.** Sub AFL against a strip PFL within ±0.3 dB at the fader's "0" mark on the jig; PFLDET with 1 / 2 / 4 / 8
keys pressed and the released LEDs viewed in a dim room, before and after the fix.

---

## Found along the way

Outside the six items, but found while checking them:

- **Strip op-amp stages without a feedback capacitor** (EQ U6A, U6B, U7A at 22K / 22K; KHN summers U12A, U13B at
  10K) are the same class as the re-inverters and level buffers. The strip is signed off; check them with TI's
  OPA161x model before routing. The EXT and return receivers already have 33 pF across 10K, so the convention exists.
- **PSU start-up skew**: `psu_spec.md`'s "both rails rise together" is not guaranteed with two independent LRS-150s.
  Start-up tracking (hold both LM1084 soft starts until both modules are up, opto-coupled across the floating rails)
  would remove the cause of the output steps on every unmuted output.
- **Wing PTC trip** is not detected: the mute sense is on ±VBUS, before the MF-RX160/72s.
- **Stale spec text** (fix with the changes): U9A → U1A; NRJ6HF → NJ6FD-V; NC3MAH → NC3MAV; §10 / §15 / §23 counts
  are pre-M1; the master schematic's title block says v0.5; Omron Components is now Aratas.

## After sign-off

The signed items become generator changes (`gen_master.py`, `gen_group.py`, `gen_jig.py`, `master_lib.py`,
`place_master.py`). Then: regenerate master, group and jig; netlist / verify / check_fp / ERC; re-place (placement
only); parity DRC; spec v0.7; CLAUDE.md decisions and verification record; the new circuits' sims (DG413 switcher,
meter current source, mute timing with 4K7) moved from `sim/review/` into `sim/`.

## Review sims (`sim/review/`)

Run from each item's folder. ngspice 46 and python3 (numpy for `noise.py`).

| Path | What it shows |
|------|---------------|
| `gcancel/gc_m1.cir` | Post-M1 ground cancel (24 strips + 4 groups, 5 master re-inverters, N = 32): buffer on / off, bus C, 0.1 % / 0.02 % match, keeper values. `ngspice -b gc_m1.cir` |
| `opa1656/noise.py` | Summer + re-inverter output noise for 9 op-amps at N = 1…32, 22K and 4K7 buses. `python3 noise.py` |
| `relays/drv134_pwr.cir` | Behavioural DRV134 with the Sense-loop caps and the DC-coupled phones amp: symmetric start, rail skew, mains-off, crowbar (writes `case2.dat`) |
| `relays/mute_review.cir` | `sim/mute.cir` with comparator sink limits, coil inductance, late-rail cases |
| `relays/coil_margin.py` | G6K pull-in margin over rail, tolerance and coil temperature; Q1 loading |
| `pflswitch/pfl.py`, `t1_op.py` … `t6_power.py`, `models.lib` | PFL switcher: generated circuit, spec variant, Delta-faithful fix, DG413, relay. e.g. `python3 t1_op.py gen J112F` (operating point), `t2_ac.py`, `t3_thd.py`, `t4_click.py`, `t6_power.py`; decks go to `decks/`. `models.lib`: Fairchild MMBFJ112, LTspice J112, datasheet corners, 1N4148 |
| `meters/mkdeck.py`, `analyse.py` | Both meter sides as generated; `python3 mkdeck.py nom.cir`, `ngspice -b nom.cir` (writes `nom.dat`), `python3 analyse.py nom.dat` (mkdeck options: LED type, sink limit, Re, rails) |
| `meters/ccs_thermal.py`, `ccs_calc.py` | Current-source self-heating (dark string) and current spread over junction tolerances; VM and calibration |
| `subafl/pfldet.py` | PFLDET with 38 keys, N pressed: back-feed current in released LEDs, with and without a per-key diode |
