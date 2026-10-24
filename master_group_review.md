# Master and group review — op-amp stability and part ratings (master v0.7, group module)

Reviewed 2026-10-24 for sign-off. Nothing in the design has changed yet: the changes wait for sign-off. This is the
pass the strip review asked for (`strip_parts_review.md`, "Found along the way"). Every op-amp stage on the master and
group boards is simulated with the manufacturers' models in the real network, and the BOM is brought up to the strip's
signed rules (`channel_strip_schematic_spec.md` §15).

Method:
- **Stability, master:** all 38 op-amp units plus both phones composites. One deck holds the whole module:
  `master.net` + `master_jack_board.net`, joined pin for pin through the CN5 ↔ CN1 link. It includes:
  - pots, PVA2 switches, the six relays, the DG413 in its logic state, the ferrites and the seven DRV134s;
  - jacks with their normals and external sources and loads;
  - the MIX / AUX / PFL buses (N sources + bus capacitance) and GCANCEL.
- **Stability, group:** all 14 OPA1612 units, from `group.net`. The deck adds a ribbon / bus model, the jack-board
  normals and the DRV134 input.
- **Models (not in the repo; their licences keep them out):**
  - TI OPA161x (SBOM396G) and OPA1656 (SBOMAW6C).
  - TL072: both the classic die (SLOJ067) and TL07xH (SLOM513A).
  - DRV134 (SBOM004A).
  - LME49600: TI publishes no SPICE model. We fitted a macro to SNAS422E Figs 12–17 (gain / phase against RL and
    CL) and bounded it with an optimistic variant and a pessimistic one.
- **Loop gain:** a Tian probe at each output, swept over:
  - pots 0–1 and switch states, PFL / AFL, EXT (open, L only, both, 50 Ω–600 Ω sources);
  - insert states (no plug, unit, dead plug, 2.5 kΩ source) and relays off;
  - MIX N 1–32 with 220 pF–2.2 nF of bus;
  - 22 pF and 47 pF on every op-amp output net, plus a trace estimate from the placed boards (pad-to-pad
    minimum spanning tree × 0.065–0.08 pF/mm).
- **Overshoot:** 10 mV step response.
- **Ratings and BOM:**
  - Dissipation from the datasheet IQ / ISC.
  - The mute and flasher transients (`sim/mute.cir`, `sim/flasher.cir`) re-run with power probes.
  - Abs max of every IC at ±16.8 V and at the crowbar threshold.
  - Footprint ↔ package ↔ KiCad pin numbering for every semiconductor; MPNs from distributor listings.
- **Merged set:** each analyst simulated one board, but three fixes go into functions both boards share
  (`post_amp()`, `level_buffer()`, `insert()`). Both harnesses were re-run with the union of the fixes (§18).
- **Skeptics:** three second reviewers re-derived every verdict. The master and group stability skeptics each wrote an
  independent deck (their own netlist converter, ladder bus, ferrite, DG413 and LME49600 macros). They used sign-aware
  phase and gain margins with a Nyquist count, time-domain kick tests, and both TL072 models with the diodes
  linearised at a converged operating point. The master skeptic ran the recommended set 712 times over 51
  configurations; the group skeptic covered 5500 unit-configurations. The BOM skeptic checked the ratings and MPNs
  against the datasheets.
  - Every finding survived.
  - They added the EXT build-out (§1), the meter's R137 tap (§9), the phones' DC fault (§11), the group's
    bus-select jumpers (§19) and the aux outputs' mute (§20).
  - They corrected several figures and two mechanisms (phantom §15, the TL072 die §9). This document uses the
    corrected numbers.

Scripts: `sim/review/master/`, `sim/review/group/` (last section).

## Summary

| # | Finding | Severity | Fix |
|---|---------|----------|-----|
| 1 | EXT input: the R receiver's output and the R jack's ring are one net (`EXT_RR`). R reads −12 dB, and U17B oscillates whenever a source is plugged in. Once split, the receivers drive the EXT/MON run unisolated | blocking | rename the receiver outputs; 100R build-out |
| 2 | Phones composite (U26 + LME49600): the 100p from PHO puts the crossover inside the LME49600's lag and resonance. Unstable at the pot ends with every LME49600 macro | blocking | 100p from the op-amp output (PH_DRV) instead; 22p at the + input; LME49600 beside U26 |
| 3 | Solo follower U19A oscillates whenever a PFL / AFL key is pressed | blocking | 22p at the + input; 100R build-out |
| 4 | Fader post-amps: master U5A/B 2–21° (7–9° as placed); group U3A 38° on the schematic, 67° as placed | blocking (master) / important (group) | 10p at the + input; 47R build-out (`post_amp()`) |
| 5 | Followers on pot wipers: master aux 5/6 level buffers and C/Room followers (16–41°), group pan buffers and aux / return level buffers (37–39° on the schematic) | important | C0G from the + input to GNDA |
| 6 | CRS followers U21 (OPA1656) drive the 214 mm CRSB net: 25–31° with 47 pF | important | 100R build-out (−0.30 dB on C/Room, phones, meters) |
| 7 | Insert returns (`insert()`): group U2B 56° on the board, 42° with +47 pF; no input protection (strip T8) | important | 1K + 100p at the + input, 75R build-out, 47K beside the 220u |
| 8 | Meter peak detectors: two integrators in the loop, 0–1.5° while the diode conducts; 10 kHz at −20 dBu reads +5 dB high | important | follower reads the diode cathode; 1K → 220R; 22p |
| 9 | Meter summers and DET followers on the placed board; TL072 part not specified | minor | 22p, trimmers beside their op-amps, 470R DET isolator with R137 on its pin side, TI TL072HIDR |
| 10 | Build-outs only work at their op-amp pins; long op-amp output nets | placement / routing rule | `near()` for every build-out; spec notes |
| 11 | Phones 2R2 (R119/R123) and the ±VP 2R2 (R3/R4): a mono plug pins the LME49600 at its current limit even in silence. 0.5–0.7 W in an 0805, up to 2.2 W in R4 | important | 2512 1.5 W; R1–R4 away from the PTCs |
| 12 | Mute: R52 takes 230 mW for 2.6 s at every power-up, and 178–190 mW indefinitely in a brown-out | important | anti-surge 0805 (R52, R48) |
| 13 | Rude-solo LED: R113 297 mW peak / 93 mW average, LED at 9.5 mA | important | anti-surge 0805; D19 MPN |
| 14 | Wing PTCs MF-RX160/72: typical wing load is 72 % of hold at 23 °C, 89 % at 40 °C, 101 % at 50 °C | your call (signed decision) | MF-RX185/72 (outline-only footprint change) or keep |
| 15 | Phantom on any DRV134 output drives its Sense pins above V+ and silences it; no spec note on the master / group | important | spec note, as strip T11 |
| 16 | BOM: no voltage, dielectric or MPN on 132 master / 40 group ceramics and on every electrolytic; other MPN gaps | minor | `CAP_MPN` map and MPNs |
| 17 | Rail filter resistors and the insert-send 75Rs, as strip T10 | minor | anti-surge 0805 |
| 18 | (Stages that pass, and the merged set's worst units) | — | — |
| 19 | Group bus-select jumpers: two groups on one SUB or AUX bus rail both summers in opposite directions | important | assembly rule, silk, jig check |
| 20 | Aux outputs (group aux 1–4, master aux 5/6) have no mute relay and get the power-up rail-skew step | your call | a decision note, or relays |

## What to sign

- [ ] **MG1** EXT:
  - rename the receiver outputs (`stereo_in(b, 'EXT', 'EXT_BL', 'EXT_BR')`);
  - add a 100R from each receiver output (feedback stays at the pin) to its 47 µF (C92/C93);
  - regenerate `master_intended.json`.
- [ ] **MG2** Phones:
  - C136/C142 100p from PH_DRVx (U26 output) to PH_Nx instead of from PHO_x;
  - 22p C0G PH_INx → GNDA at U26 pins 3/5;
  - each LME49600 placed beside U26.
- [ ] **MG3** Solo: 22p C0G PFL_FIN → GNDA at U19 pin 3; 100R from U19A's output / − input (new net PFL_SIGO) to
  PFL_SIG.
- [ ] **MG4** `post_amp()` (master U5A/B, group U3A): 10p C0G from the + input to GNDA; 47R between the output (the
  feedback tap) and the 220u.
- [ ] **MG5** + input caps:
  - 10p C0G in `level_buffer()` (master U13A/B, group U5B, U9A/B);
  - 22p C0G on the C/Room followers' inputs CR_FINL/R;
  - 10p C0G on the group pan buffers' inputs S_PWL/S_PWR.
- [ ] **MG6** CRS: 100R from U21's output / − input (new nets CRSB_LO/RO) to CRSB_L/R.
- [ ] **MG7** `insert()` (master U2B/U4A, group U2B):
  - 1K + 100p C0G at the + input (as strip R99/C84);
  - 75R build-out between the buffer and its 220u;
  - the 47K placed beside the 220u.
- [ ] **MG8** Meter peak detectors:
  - JP1/JP2 pin 1 on M_PK1 (the diode cathode);
  - R134/R170 1K → 220R;
  - 22p C0G from M_U3O to M_N4;
  - spec 22's attack, reading and calibration text.
- [ ] **MG9** Meter:
  - 22p C0G across the summers' feedback (M_X2 → M_N2), and RV7/RV8 placed beside U29/U36;
  - 470R between U30B/U37B (new net M_DETO, feedback at the pin) and the DET distribution, with R137/R173 (10K to
    M_N4) taken from M_DETO, not DET;
  - TL072 → TI TL072HIDR.
- [ ] **MG10** Placement and routing:
  - every build-out resistor (MG1, MG3, MG4, MG6, MG7, MG9) recorded with `near()` at its op-amp pin;
  - the routing notes in master spec §7 / group §12 (§10 below).
- [ ] **MG11** Phones resistors:
  - R119, R123, R3, R4 → Vishay CRCW25122R20FKEGHP (2.2 Ω 2512, 1.5 W);
  - re-place the master with R1–R4 away from F1–F4.
- [ ] **MG12** R52 → Panasonic ERJ-P06J472V, R48 → ERJ-P06J103V.
- [ ] **MG13** R113 → ERJ-P06J332V (or 6K8 ERJ-P06J682V for 4.6 mA); D19 Kingbright WP7113ID.
- [ ] **MG14** Wing PTCs: keep MF-RX160/72, or MF-RX185/72 (§14). **Your decision.**
- [ ] **MG15** "No phantom on any balanced output" in master spec §7, §12, §13, §20 and in `panel_print.md`.
- [ ] **MG16** BOM: a `CAP_MPN` map applied to every C / CP in `master_lib` (as `gen.py`), including the jig load
  board's 1n C0G; the MPNs in §16.
- [ ] **MG17** Anti-surge resistors:
  - group R1/R2 → ERJ-P06J100V;
  - master R1/R2 → ERJ-P06J1R0V, and fix spec §25's stale 0.5 A;
  - master R16/R24 and group R11 → ERJ-P06J750V.
- [ ] **MG18** Spec text for the new gain figures: master about −0.18 dB on the main path (−0.081 dB from MG7's 75R
  into the fader, −0.094 dB from MG4's 47R); group −0.23 dB on the sub out, MIX feed and sub AFL (§4, §7).
- [ ] **MG19** Group bus-select rule (§19):
  - one SUB jumper and one AUX jumper per board, unique across the four;
  - the group number on the silk;
  - a jig check.
- [ ] **MG20** Aux outputs (§20): a decision note, or mute relays. **Your decision.**

Applying MG1–MG9 changes the master and group netlists. That means:
- `master_lib.py`, `gen_master.py` and `gen_group.py` edits. The jig stub shares `master_lib` but only its summer,
  re-inverter and DRV134 (which pass here), so it changes in its BOM only (MG16);
- regenerating every affected board and its intended JSON;
- verify / check_fp / ERC;
- re-placing `master.kicad_pcb`, `group.kicad_pcb` and the jig stub (placement only), then parity DRC;
- master spec v0.8.

---

## 1. EXT input: net collision (blocking)

`gen_master.py` calls `stereo_in(b, 'EXT', 'EXT_RL', 'EXT_RR')`. `stereo_in()` already names the R jack's ring
`name + '_RR'`, i.e. `EXT_RR`. So the R receiver's output (U17 pin 7, R84, C90, C93) is the same net as the R jack ring
(R83, C89, CN5 pin 29 → J9 ring, which is normalled to EXT_LR):
- **Level:** with an L plug only, both EXT outputs read 0.249 V instead of 0.990 V (−12 dB). With both plugs, R reads
  0.125 V instead of 0.497 V.
- **Drive:** U17B drives the source's cold leg.
- **Stability:** 21.5–22.4° with nothing plugged (14.8° with 47 pF). With a source plugged in it oscillates: −21° from
  a 50 Ω L plug, −31° with 600 Ω on both (Nyquist count 2). A kick grows ×27 in 1.3 µs at 11.7 MHz, so a plugged EXT
  input also injects HF into the monitor path.

Why the checks missed it:
- `verify.py` passes because `master_intended.json` comes from the same code.
- ERC passes because a jack ring is a passive pin.

Fix:
- **Rename:** name the outputs `EXT_BL` / `EXT_BR` (and the 47 µF from `EXT_B{sd}`). With the net split, U17A/B are
  at 84.8° with MIX monitored and 57.4° with EXT selected and no trace C.
- **Build-out:** with EXT selected, the receivers drive the EXT_L → SW3 → MON → C104 → DG413 run directly. That gives
  42.6° with 47 pF on it, and 46–50° with the placed estimate. A 100R between each receiver output (feedback at the
  pin) and its 47 µF gives 73–74° in every case, for −0.03 dB.

The group's returns use `RT_L` / `RT_R` and have no collision.

## 2. Phones composite (blocking)

U26A/B (OPA1612 on ±VP) drive U27/U28 (LME49600, BW open) inside the loop; the output is a 2R2; the feedback is 4K7 ∥
100p from PHO (the jack side of the 2R2) with 2K2 to ground. With the 100p taken from PHO, the feedback factor goes to 1
above ~1 MHz, so the outer loop, LME49600 included, crosses over at the OPA1612's unity-gain frequency (~45 MHz). There
the LME49600 adds 25–35° of lag, and its 80–90 MHz resonance (SNAS422E Figs 12–17) lifts the loop gain above 0 dB a
second time.

As designed:
- **Pot at either end:** unstable with nearly every load (9 of 10 in the skeptic's deck) and every LME49600 macro: −46 to −90° in the analyst's deck, −0.3
  to −161° (Nyquist count 2) in the skeptic's. The loop re-crosses 0 dB at 83–125 MHz with +8 to +22 dB of
  closed-loop peaking.
- **Mid travel:** 1–31° depending on the load and macro (−14° with 32 Ω + 1 nF).
- **As placed:** −115 to −130° on the R side, where U28 sits 113 mm from U26.

Fix: take the 100p from PH_DRV (U26's output) to PH_N. At HF the op-amp is then a local follower and the LME49600 is out
of the HF loop. This is the usual composite compensation, with the hand-over at 1/(2π · 4K7 · 100p) = 339 kHz. Add 22p
C0G from PH_IN to GNDA at U26's + inputs, and place each LME49600 beside U26.

Result:
- **Margin:** 78.5–87.4°, ≤ 0.39 dB peaking, with all three macros (nominal, pessimistic, optimistic) in both decks.
  Swept over RV6 at 0 / 0.75 / 1 × {32 Ω + 220 pF, 32 Ω + 470 pF, 32 Ω + 1 nF, 300 Ω + 220 pF, open, K6
  de-energised}.
- **As placed:** ≥ 74° with the 113 mm traces modelled as LC lines.
- **Cost:** about 0 dB, −0.9° at 20 kHz; LF gain unchanged at +9.9 dB. The 2R2 stays inside the loop in the audio
  band.

## 3. Solo follower U19A (blocking)

U19A is a bare OPA1612 follower on the solo pot's wiper (via 2.2 µF and 100K). Its output, PFL_SIG, goes through
C105/C107 47 µF to the DG413's SW1/SW4. With a key pressed, both on-switches (25 Ω, ~35 pF each with their D and S
capacitance) and both OPA1656 CRS inputs hang on it.

As designed:
- **Key pressed, solo pot at 0.75:** −0.6 to −0.8° (Nyquist count 2), +28 dB at 20 MHz; a kick grows ×2.1 (×4.7 with
  47 pF). It oscillates.
- **Released:** 30°.

Fix: 22p C0G at PFL_FIN (U19 pin 3), and 100R from U19A's output / − input (new net PFL_SIGO) to PFL_SIG.
- **Result:** ≥ 73.5° in every state, 75–83° with a key pressed.
- **Placement:** the 100R at U19; with 22 pF between the pin and the 100R it is 65°.
- **Cost:** −0.019 dB with a key pressed, where each 47 µF drives 1M ∥ 100K; −0.002 dB released; −0.39° at 20 kHz.

## 4. Fader post-amps (blocking on the master, important on the group)

`post_amp()` builds +10 dB (4K7 ∥ 100p over 2K2) from the fader wiper via 2.2 µF + 100K. The 100p makes the stage a
follower above 339 kHz, so the Cdiff lag against the 1.3–2.5 kΩ wiper and the load on POST take the margin. On the
master, POST_L runs 337 mm, and with MIX monitored the DG413's on-capacitance hangs on it through SW3 / MON.

| Master U5A/B, fader 0.5–0.9 | As designed | MG4 |
|---|---|---|
| no trace C | 17–21°, +9.5 dB at 23 MHz | 57–76° |
| 22 pF on POST | 12.8° | |
| 47 pF on POST | 2–5°, +18 to +23 dB (kick: ζ = 0.03) | ≥ 51.2° |
| placed estimate (POST_L 337 mm + MON_L 123 mm) | 7–9° | 51–54° |

Fader at 0: 61–62°; at the top: 59–60°.

Fix (`post_amp()`): 10p C0G from the + input (MST_x_FIN) to GNDA, and 47R between the output (U5 out, which stays the
feedback tap with R28/R32 and C30/C33) and the 220u. The 47R must sit at U5: 22 pF on its pin side gives 47.3°.
- **Result:** ≥ 51.2° over every configuration (fader 0–1, PFL / EXT states, 47 pF on POST, placed estimate).
- **Cost:** −0.094 dB flat (47R into DRV134 10K ∥ mono 10K ∥ 47K); mono follows; −0.18° at 20 kHz.
- **L/R matching:** 0.01–0.03 dB, set by the DRV134's internal 10K (absolute tolerance not specified) rather than the
  1 % parts.

The group's sub post-amp U3A is the same function:
- **As designed:** 37.9° on the schematic. On the placed board it is 67° as designed, because the 286 mm S_W trace
  (~22 pF) sits on its + input. So on the group MG4 buys independence from the layout rather than curing a fault.
- **With the merged set** (10p + 47R): 65.6–66.0° in every pot and insert state, on the schematic and the board (74°
  at pan centre). With +47 pF beyond the 47R (S_POST): 62°. On the pin side (S_FPOST) the build-out does nothing
  (47.8°), so the 47R has to sit at U3 pin 1.
- **Cost on the group:** the 47R drives ~2.7 kΩ (DRV134 10K ∥ RV2's two 10K tracks ∥ R17 47K ∥ R22 22K), so −0.15 dB,
  and −0.82 to −1.0° at 20 kHz. With MG7's 75R that is −0.23 dB flat on the sub out, the MIX feed and the sub AFL. Spec
  §12's "solo level at the fader's 0 mark −0.2 dB" becomes about −0.43 dB (MG18).

## 5. Followers on pot wipers (important)

The same class as strip finding 4. Cdiff (8 pF in TI's model) between the + input and the output, against a 1–2.5 kΩ
wiper, puts a lag near crossover; trace C on the output makes it worse. The 100p across the level buffers' 4K7 (master
review S3) does not touch this. Every op-amp macro with an 8 pF Cdiff shows it: 33–48° as designed, against TI's
38°. The fix gains 25–35° in each.

| Stage | Board | As designed | Fix | With the fix |
|---|---|---|---|---|
| Aux 5/6 level buffers U13A/B (`level_buffer()`) | master | 38–41°; 18–20° with 47 pF | 10p | 75–87°; ≥ 51.6° with 47 pF |
| C/Room followers U23A/B | master | 37–40°; 16–18° with 47 pF | 22p | 81–85°; ≥ 58.1° with 47 pF |
| Sub pan buffers U3B, U5A | group | 37.5° schematic; 68–72° on the board (long wiper traces) | 10p | 75.3–75.6° (77.9° with the 10p alone); 54.4° with +47 pF |
| Aux level buffer U5B (`level_buffer()`) | group | 37.6° schematic; 36–49° board; 29° with +47 pF | 10p | 70.5–72.0° board; 47.9–49.5° with +47 pF |
| Return level buffers U9A/B (`level_buffer()`) | group | 38.7° schematic; 43–49° board; 29–30° with +47 pF | 10p | ≥ 64.9° board; ≥ 45.3–46.4° with +47 pF |

Notes:
- **Worst pot positions:** about 0.95 without extra C, and about 0.3 with 47 pF on the output (wiper ~0.8 kΩ). Neither
  is the maximum-impedance 0.706.
- **Board column:** for U5B / U9 the as-designed board margins rest on 1–3 pF of + input stray, each pF worth 5–9°
  (38 / 47 / 53 / 58° at 0 / 1 / 2 / 3 pF). The 10p removes that dependence: 75–83° for 0–5 pF of stray.
- **Cost:** ≤ 0.0004 dB and ≤ 0.38° at 20 kHz.

The caps cut both ways: at a pot's top end each one sits on the upstream op-amp's output. That decides 10p over 22p in
`level_buffer()`, which both boards share. Worst case with 47 pF on every output, merged set:

| `level_buffer()` cap | Master U13A/B | Master U12B/U15B (upstream) | Group U5B / U9A/B | Group U6B, U8A/B (upstream) | Worst group unit |
|---|---|---|---|---|---|
| 10p | 51.6–52.8° | 55.8–55.9° | 49.5° / 46.4–47.3° | 48.3°, 51.6° | 46.4° (U9B) |
| 22p | 59.2° | 51.9° | 55.7° / 51.8–52.7° | 44.8°, 48.0° | 44.8° (U6B) |

With no extra C the group's worst unit is 65.2° with 10p against 60.3° with 22p. 22p lifts the buffers but costs their
sources more. On the master the two are about equal (51.6–52.8° against 51.9°, within 1° either way, depending on
the deck); on the group 10p gives the higher worst case. The margin is small (1.6° on the group under the 47 pF
stress); the lever beyond that is routing (A_MIX / A_PT, RT_BL/BR), not the cap value.

## 6. CRS followers U21A/B (important)

The OPA1656 unity followers after the DG413 drive CRSB_L/R: 214 mm to RV5, RV6 (10K each) and the meter feed (100R).
At a pot's top end, the downstream followers' + inputs and their new caps also sit on CRSB.
- **As designed:** 49.5–57.7° with no trace C, 41° with 22 pF. With 47 pF: 25–31° (+7.8 dB); at the pot top 41°, but
  with a gain margin of only 2.9 dB at 34 MHz. 40.8° with the placed estimate.
- **Fix:** 100R from U21's output / − input (new nets CRSB_LO/RO) to CRSB_L/R, placed at U21: 22 pF on the pin side
  gives 44.8°.
- **Result:** ≥ 47.8° (pots at the top), 48.5–52.1° with 47 pF or placed, ≤ 1.9 dB peaking. The lowest units of the
  master's merged set.
- **Cost:** −0.30 dB flat on C/Room, phones and the meter feed (100R into 2.875 kΩ = RV5 ∥ RV6 ∥ 6.77 kΩ of meter
  input). The L/R match is set by the pots' end-to-end resistance, ~0.03 dB per 10 % gang mismatch. The meter trim
  takes out the meter's share.

Alternatives: 220R gives 52–55° at −0.64 dB; 47R leaves 42° at 47 pF.

## 7. Insert returns (important)

`insert()` builds the return path: ring → 47 µF NP → OPA1612 follower (47K shunt to GNDA at its + input: master R17/R25,
group R12) → 220u → fader top (PRE, with its own 47K to GNDA: master R18 / R26, group R13).

- **Stability, group U2B:** the follower drives two of the board's longest nets.
  - S_PRE is 292 mm, because R13, its 47K, was placed 265 mm from C13; beside C13 it would be 111–121 mm.
  - At the fader top it also drives S_W (286 mm).
  - Margin: 56–57° over 46 insert states as designed. With +22 / +47 / +100 pF on S_PRE: 49 / 42 / 30°.
- **Stability, master U2B/U4A:** 74° with no extra C; 47.7–48.0° with 47 pF on PRE (146 mm) at the fader top.
- **Protection:** the return reaches the OPA1612's + input with no series resistance, as the strip's RET did before
  T8. The input-current limit is ±10 mA (SBOS450C). Outboard gear driving a return while the console is off sends its
  current through the input diodes into unpowered rails: about 100 mA from a 10 V, 100 Ω source.

Fix (`insert()`):
- **Input:** 1K from the return to a new net at the + input, plus 100p C0G to GNDA (strip R99 / C84), at U2 pin 5.
  Never the 1K alone: on the group it drops U2B to 26–33° (as R99 alone did to the strip's U7B).
- **Output:** 75R between the buffer and its 220u (new net; the feedback stays at the pin), at the op-amp pin. With
  +47 / +100 pF on the pin side it gives only 55.5 / 41°.
- **Placement:** the 47K placed beside the 220u.

Results with the merged set:
- **Group U2B:** ≥ 74.2° in every pot and insert state; 75–79° with +22 to +100 pF on S_PRE.
- **Master U2B/U4A:** 75.5–86.8° over every insert state, 75.6° with 47 pF on PRE.
- **Isolation:** the 1K also isolates U2B's input capacitance from the send / normal path, lifting the group's U2A
  from 65.6° to 68.1°.

Cost:
- −0.085 dB flat into the fader (75R into 10K ∥ 47K).
- The 1K adds 4.07 nV/√Hz: +0.18–0.21 dB on the sub floor at N = 1, +0.03 dB at N = 24.
- From a 10 kΩ return source, −0.06 to −0.09 dB and −5.9° at 20 kHz. With 300 pF of cable on the return, −0.30 dB
  (the 100p adds to the cable's C). From a ≤ 600 Ω source, < 0.01 dB.
- **Protection limit:** into an unpowered console the 1K holds a return to about the ±10 mA input limit up to a
  ~11 V peak: a +20 dBu outboard peak (11.0 V) drives ≈ 9.5 mA. +24 dBu (17.4 V peak) still drives ≈ 15 mA. That is
  far better than the ~100 mA without it, but not a guarantee against a hot unit driving a dead console.

## 8. Meter peak detectors (important)

Refs: U30A / U37A are the peak detectors (L / R), U30B / U37B their DET followers; `M_` below stands for the nets
`ML_` / `MR_` (e.g. M_PK1 = ML_PK1 / MR_PK1). U30A → 1N4148 (D25) → 1K (R134) → 1 µF (C148, M_PK) → JP1 → U30B
follower → M_DET → 10K (R137) → U30A's − input (M_N4). While the diode conducts, the loop holds two integrators, the
TL072 and 1K / 1 µF:
- **Margin:** 0.3–1.5° tracking and on attack (Nyquist count 2 at a 1 mA attack), with either TL072 model; 65° in
  hold.
- **Reading:** the diode catches the overshoot, so the meter over-reads. 10 kHz at −20 dBu reads +4.4 to +5.3 dB
  high (2 ms bursts and steady 20 ms, both models); 1 kHz at −20 dBu reads +0.25–0.5 dB high.
- **Not the op-amp:** the same with an ideal 3 MHz op-amp, Schottky diodes or an OPA1656 in U30A (+4.1 to +4.7 dB).
  It is the topology.

Fix:
- **Topology:** the follower reads the diode cathode (JP1/JP2 pin 1 on M_PK1), so the loop holds only the op-amp.
- **Values:** R134/R170 1K → 220R; 22p C0G from U30A's output to its − input (M_U3O → M_N4).
- **Clamp current:** it still comes from the follower through the 10K, not from the capacitor (spec 22's rule holds).

Result:
- **Margin:** 64–79° with the classic TL072, 43–52° with the TL07xH model (42.9° in hold).
  - The TL07xH model runs 17–18° low against its datasheet (§9).
  - Its DC operating point does not converge in this loop. ngspice's gmin and source stepping both fail, and leave the
    1 µF still charging at 1.6 mA. AC runs of this loop need the diodes linearised at a converged point; that is how
    these numbers were taken.
- **Attack:** first-order, 0.22 ms, no overshoot.
- **Held readings against the true peak** (classic / TL07xH model):

  | Signal | Reading |
  |---|---|
  | 1 kHz 0 dBu, 5 ms / 10 ms bursts | −0.18 / −0.11 dB; −0.21 / −0.13 dB |
  | 1 kHz −20 dBu, 5 / 50 ms | −0.33 / −0.30 dB; −0.54 / −0.44 dB |
  | 10 kHz 0 dBu, 2 ms | −0.79 to −0.85 dB |
  | 10 kHz −20 dBu, 2 / 20 ms | −1.8 to −2.2 / −1.5 to −1.8 dB; −2.0 to −2.5 / −1.6 to −2.1 dB (−0.75 to −1.3 dB with BAT54W diodes) |

- **Conduction spikes:** DET follows the diode cathode, so during conduction it carries µs spikes up to the true
  peak. On a 10 kHz −20 dBu burst it sits > 0.26 dB above the held level 10–13 % of the time, so the next LED up can
  glow faintly on HF bursts; steady tones don't show it.
- **Calibration:** a steady 1 kHz reading (150 ms) moves −0.08 dB at 0 dBu and −0.18 dB at −20 dBu. As designed it
  is −0.03 / −0.12 dB; with MG8 −0.11 / −0.30 dB (classic model). The trim takes out the 0 dBu part; the −20 dBu law
  error grows by 0.1 dB.
- **Spec 22:** the "1K into 1 µF (≈1 ms attack)" text, the readings and these notes change.

Two runs of this fix disagreed during the review: one gave +0.00 dB for every burst, the other −0.2 to −2.2 dB. They
had simulated the same circuit and measured different things. One took max(DET) over the run, which catches the first
conduction spike; the other took the held DET after the burst. The table gives the held value.

## 9. Meter summers, DET followers and the TL072 part (minor)

- **Summers U29B/U36B (R side, as placed):** the summing junction MR_N2 runs 102 mm because RV8 sat far from U36.
  - As designed: 45–68° with the classic TL072 and 22–44° with the TL07xH model, depending on the trim position and
    the length estimate.
  - Fix: 22p C0G across the feedback (M_X2 → M_N2), and RV7/RV8 placed beside U29/U36.
  - Result: 78–90° classic, 55–67° TL07xH. The pole sits at 0.4–0.6 MHz, < 0.05 dB on a rectified 20 kHz tone.
  - The rectifiers U29A/U36A are fine: ≥ 69° classic, 43–48° TL07xH on the negative half.
- **DET followers U30B/U37B:** each drives 20 LM2901B inputs plus 165 mm of trace.
  - As designed: 51–58° classic; 24–33° with the TL07xH model.
  - That model runs 17–18° low against its datasheet. As a plain follower it gives 38° at 20 pF (SLOS080W: 56°),
    31° at 50 pF (Fig 5-25: ~48°) and 22° at 100 pF (~39°), and 34 % overshoot at 20 pF against ~9 %.
  - Fix: 470R between the follower (new net M_DETO, feedback at the pin) and the DET distribution. R137/R173, the 10K
    back to U30A/U37A's − input, must be taken from M_DETO, not DET. On DET, the clamp current flows through the 470R: DET
    reads 0.40 dB low in hold and ripples 0.5 dB at 2f while tracking. That partly lights an LED over ~25 % of each
    2 dB step, undoing the "no ghost" result. On M_DETO the ripple is 0.07–0.10 dB and the readings match §8.
  - Result: 58–60° classic, 40–41° with the TL07xH model, ≈ 57–59° once corrected to the datasheet. 1K instead of
    470R gives +3°.
  - Cost: ≤ 0.03 dB at the bottom LED (20 × 25 nA maximum bias).
- **Part:** the four TL072s have no MPN.
  - SLOS080W Table 9-1: TI's plain TL072 may ship with either the legacy die (3 MHz) or the new die (5.25 MHz,
    Zo 125 Ω). Only the H suffix fixes the die, and the margins above depend on knowing which one it is.
  - TL072H is rated 42 V abs max.
  - The crowbar acts per rail, so at its threshold ±VM is about +18.6…+18.9 / −16.5 V: 35.1–35.4 V across. A
    classic-die second source (±18 V abs, i.e. 36 V) survives that. It is already over its ±15 V recommended supply
    at nominal (33 V), and over its ±15 V input abs max when CRS clips (~15.5 V on pin 3; the OPA1656 swings rail to
    rail).
  - Choose TI TL072HIDR.

## 10. Placement and routing rules (MG10)

- **Build-outs at the pin:** every build-out resistor isolates only the capacitance beyond it. With 22 pF between the
  pin and the resistor:
  - U21: 44.8°;
  - U5: 47.3°;
  - U2B: 66°;
  - U19: 65°.

  Each build-out (MG1, MG3, MG4, MG6, MG7, MG9) gets a `near()` record, and the pin-side nets stay pad-length.
- **Master:** with the build-outs, POST, CRSB, PFL_SIG, PRE and the EXT/MON run are isolated, so no other master output
  net needs a special limit. GCANCEL_BUF takes no series R (66° with 47 pF).
- **Group:** keep A_PT / A_MIX, RT_BL/BR + RT_RTNL/R, RT_PREL/R, S_MIX and GC_BUF within ~40 pF of the placement
  estimate (≤ ~55–60 pF in all): thin traces, not run over long double-sided pour. S_POST and S_PRE are behind the
  47R / 75R and relaxed. With the merged set and +47 pF on every output pin net:

  | Unit | Margin |
  |---|---|
  | U9B | 46.4° |
  | U9A | 47.3° |
  | U3A (on S_FPOST; 62.4° beyond the 47R) | 47.8° |
  | U6B | 48.3° |
  | U5B | 49.5° |
  | U8B | 51.6° |
  | U2A | 52.7° |
  | U2B (on SUB_RBUF; 75.8° beyond the 75R) | 55.0° |
  | U1A | 62.5° |

## 11. Phones resistors (important)

The relay contacts sit after the feedback tap, so a mono (TS) plug grounds PHO_R through a ~50 mΩ residual:
- **It is a DC fault.** With PHO grounded, the composite becomes a ×~140 amplifier of U26's own DC input (Ib × 100K
  = 6–25 mV). A TS plug alone, in silence, can hold U28 at its current limit.
- **Current limit:** SNAS422E gives ±490 mA typical with BW open (its text says ~±450 mA). The ±550 mA maximum is
  specified only with BW tied to VEE.
- **Rails:** Ib has the same sign in both halves of U26, so both outputs pull −VP. With both channels shorted, R4
  carries both.
- **The LME49600:** it dissipates ~7.2 W in the limit. Only its thermal-shutdown cycling bounds the average; the
  resistors have no such protection.

| Part | Case | Dissipation | Of 0.125 W |
|---|---|---|---|
| R119/R123 (2R2 output) | short or TS plug, programme or silent | 0.53–0.67 W | 423–536 % |
| R119/R123 | full swing into 32 Ω | 184 mW | 147 % |
| R3/R4 (2R2 ±VP feed) | one channel shorted, programme | 0.16 W | 128 % |
| R3/R4 | one channel shorted, silent (DC) | up to 0.56 W | 448 % |
| R4 | both channels shorted, silent (DC) | up to 2.2 W, until the LME49600s thermal-cycle (~0.7 W at ~30 % duty) | 1760 % |

Fix: Vishay CRCW25122R20FKEGHP (2.2 Ω 1 % 2512, 1.5 W) for all four: 35–44 % for an output in a short, 37 % for one
rail resistor. The both-channel case still relies on the LME49600s' thermal cycling. The cheaper ERJ-P08 option is
dropped (85 % with one channel, 330 % with both).

Re-place the master:
- R1–R4 now sit 1–3 mm from the F1–F4 lead rows on the other side of the board. R1 is at (69.7, 187.0) and R3 at
  (69.7, 189.5), beside F3 at (66.5, 187.9); R4 at (59.2, 190.5) is within F4's span; R2 at (6.2, 189.5) sits between
  F1 and F2.
- A phones fault heating R3/R4 would derate the PTCs (1.30 A hold at 40 °C) and could trip a wing.
- R1–R4 go away from F1–F4 (R3/R4 now 2512, R1/R2 0805 per MG17). R119/R123 sit elsewhere (y 306 / 170) and only grow
  to 2512.

A DC servo, or a feedback tap that survives a grounded PHO, would remove the silent fault. It is not proposed: it
changes the composite, and the 2512s cover the single-channel case.

## 12. Mute network (important)

MUTE_GO (the Schmitt output, U11A) sinks to −VL, which is the LM393B's GND pin, for the whole power-on delay. So R52
(4K7, +VL → MUTE_GO) has about 33 V across it, and dissipates 230 mW (184 %) from 0.2 s until the relays close at
2.80 s, at every power-up (`sim/mute.cir` with power probes). That pulse alone is inside a standard 0805's 5 s
short-time overload rating. A brown-out is the case that needs the change: with one rail between its trip point and
nominal, it lasts indefinitely:

| Case | R52 | R48 |
|---|---|---|
| +V held at 13 V | 178 mW | 84 mW |
| −V held at −14 V | 190 mW | 90 mW |
| +V held at 13.9 V (just above the trip) | 190 mW until the relays close at 3.85 s | |

Fix: R52 → Panasonic ERJ-P06J472V (0.5 W 0805, 46 %), R48 → ERJ-P06J103V (18 %). Same value and footprint, so the
timing is unchanged.

U11A sinks 10.3 mA: under the B part's 25 mA abs max, over its guaranteed 6 mA at 1.5 V, which is harmless here.

## 13. Rude-solo LED (important)

D19's cathode returns to an LM393B output that sinks to −VL, not GNDD. So R113 (3K3) has about 31.3 V across it while
the LED is lit:
- **LED current:** 9.5 mA, three times the other panel LEDs.
- **R113:** 297–299 mW peak (239 %), 92–93 mW average (74 %), with 0.17 s on in every 0.54 s, for as long as a solo is
  held.
- **R112:** 110 mW peak, 35 mW average: fine.

Fix:
- **R113:** ERJ-P06J332V (0.5 W: 59 % peak, 19 % average), same brightness. Or 6K8 for 4.6 mA, which still needs
  ERJ-P06J682V for its 147 mW peak.
- **D19:** MPN Kingbright WP7113ID (5 mm red, diffused, ~2.0 V; fits LED_D5.0mm).

## 14. Wing PTCs (your call: a signed decision)

A wing is 12 strips × 85 mA + 2 groups × ~70 mA = 1.16 A on +V. Bourns MF-RX/72 derating (Ihold 1.60 / 1.30 / 1.15 /
1.01 A at 23 / 40 / 50 / 60 °C) puts that at 72 / 89 / 101 / 115 % of hold. The spec's worst case of 1.7 A (OPA1612 at
maximum IQ, every LED lit) is 106 % at 23 °C. The PTCs sit at the master's power entry, inside a tub that dissipates
about 90 W. In a warm room a wing can nuisance-trip at typical load.

| Option | Hold at 40 / 50 °C | Typical load as % of hold | Trip | Body (max) | Board change |
|---|---|---|---|---|---|
| Keep MF-RX160/72 | 1.30 / 1.15 A | 89 / 101 % | 3.2 A | 13.94 × 19.94 mm, 5.1 mm pitch | none |
| MF-RX185/72 | 1.50 / 1.33 A | 77 / 87 % | 3.7 A | 15.18 × 21.18 mm, 5.1 mm pitch | outline / courtyard only (+1.24 mm); same pads |
| MF-RX250/72 | 2.03 A at 40 °C | 57 % | 5.0 A | 17.84 × 23.84 mm, 10.2 mm pitch | new footprint; rejected (below) |

The ribbon's limit is the crimped IDC socket, not the 3 A header: about 1 A per contact (Würth WR-BHD female
61203423021; console_architecture.md §2). Each rail has two conductors:

| Condition | Per contact |
|---|---|
| Typical load | 0.58 A |
| Worst-case load | 0.85 A |
| At hold, MF-RX160 | 0.80 A |
| At hold, MF-RX185 | 0.93 A |
| At hold, MF-RX250 | 1.25 A, indefinitely below hold |

So MF-RX250 is out while power stays on the ribbon. If you change the part, MF-RX185/72 is the choice: same pads, and
it likely fits as placed (the F1/F2 rows are 4.5 mm apart). Either way, keep F1–F4 away from the LME49600s and the rail
resistors (§11).

## 15. Phantom on the balanced outputs (important, spec only)

On every DRV134 output the Sense pins sit on the connector node, after the 10 µF NP caps. This covers the master's main
XLRs, aux 5/6 and C/Room, and the group's sub and aux outs.
- **What phantom does (TI's DRV134 model):**
  - P48 (6.81K per leg) drives the Sense pins into their clamps to the rails: ~17.4 V (V+ + 0.5 V), outside the
    DRV134's input range (V− to V+, SBOS094B).
  - About 2.4 mA per leg flows through them into +VA.
  - Both outputs saturate at +14.6 V, and the output goes silent.
  - The 10 µF caps see ≤ 3 V (2.2 V unpowered).
- **The earlier ~27 V figure** (master parts review §3) holds only for Sense pins without clamps.
- **Where it will meet phantom:** the main XLRs (recorder and interface inputs), and the group sub outs through
  TRS-to-XLR leads.
- **What the specs say:** nothing for the master or the groups; only the strip has the note.

Fix: the strip's T11 rule. "No phantom on any balanced output: P48 forces the DRV134's Sense pins above V+ (its input
protection conducting) and silences the output" goes in master spec §7 (and §12 / §13 / §20) and in the panel legend rules.
If phantom tolerance is ever wanted, it needs 50 V DC-blocking caps at the connector, outside the Sense loop.

## 16. BOM (minor)

**Ceramics.** Value only, no voltage, dielectric or MPN:
- Master: 71 × 100n, 18 × 1u, 11 × 2.2u, C116 330n, 16 × 100p, 11 × 22p, 4 × 33p (132).
- Group: 14 × 100n, 4 × 1u, 4 × 2.2u, 10 × 100p, 4 × 22p, 4 × 33p (40).
- The jack boards carry no capacitors.

Most sit on ±16.45–16.9 V, and C116 holds −16.2 V. The strip's rule applies: ≥ 25 V, 50 V X7R preferred, C0G at 50 V.
Add a `CAP_MPN` map to `master_lib.py` and fill empty C / CP MPNs in one pass before `build()`, so the
`unit_of()` decouplers are covered too:

| Value | MPN |
|---|---|
| 100n | Samsung CL21B104KBCNNNC (X7R 50 V 0805) |
| 1u | Samsung CL31B105KBHNNNE (X7R 50 V 1206) |
| 2.2u | Murata GRM31CR71H225KA88L (X7R 50 V 1206) |
| 330n | Samsung CL21B334KBFNNNE (X7R 50 V 0805) |
| 22p / 33p / 100p C0G | KEMET C0805C220J5GACTU / C0805C330J5GACTU / C0805C101J5GACTU (50 V 5 %) |
| 1n C0G (jig load board) | KEMET C0805C102J5GACTU |

The X7R 330n (C116, flasher timing) loses capacitance at 5–11 V of bias, so the flasher runs ~20–35 % faster. Use a
WIMA MKS2 0.33 µF film if the 0.6 s / 0.54 s timing matters. The meter ballistics caps are fine as 50 V X7R 1206
(≤ 6 V of bias, about −10 %).

**Electrolytics.** No MPNs. `CP()` reuses the bipolar footprint map, and three value classes don't fit the usual
25 V parts. These MPNs fit the current footprints, with no board change. All the electrolytics sit on the bottom side,
below the 11.5 mm panel gap.

| Value | MPN | Size |
|---|---|---|
| 470u 25V | Nichicon UPW1E471MPD | 10 × 16, P5.0 |
| 1000u 25V | Nichicon UPW1E102MHD | 12.5 × 20, P5.0 |
| 47u 25V (polar) | Nichicon UPW1J470MPD (63 V) | 8 × 11.5, P3.5 |
| 220u 25V (polar, group) | Nichicon UPW1V221MPD (35 V) | 10 × 12.5, P5.0 |
| 10u NP 25V | Panasonic ECE-A1EN100U, or any 5 × 11 P2.0 bipolar ≥ 25 V | 5 × 11, P2.0 |
| 47u NP 25V | Panasonic ECE-A1VN470U (35 V) | 8 × 11.5, P3.5 |
| 220u NP 25V | Panasonic ECE-A1EN221U | 10 × 16, P5.0 |

- **Ratings:** the value strings keep the minimum rating. Every voltage is fine: ≤ 68 % on the rails, 78 % at the top
  of the crowbar threshold. Polarity is correct on all 12 polar caps.
- **Lifecycle, check before ordering:**
  - Digi-Key lists UPW1V221MPD as Not For New Designs, and Cytech lists UPW1E471MPD the same, so check the UPW
    family's status.
  - RS marks the ECE-A1EN100U and the hyphenated ECE-A1EN221U listings as discontinued.

**Other MPNs:**

| Part | MPN |
|---|---|
| OPA1612 (13 master, 7 group; only `gen.py` sets it today) | TI OPA1612AIDR |
| TL072 | TI TL072HIDR (§9) |
| NPN | onsemi MMBT3904LT1G |
| 1N4148 (DO-35) | Vishay 1N4148-TAP |
| BZX84C5V1 | Nexperia BZX84-C5V1,215 |
| BZT52C6V2 | Diodes BZT52C6V2-7-F |
| SS54 | onsemi SS54 |
| D3 power LED | `LED_MPN['green']` |
| Cal trimmers | Bourns 3296W-1-103LF |
| Pots | Alpha RD901F-40-15R1-A10K; dual RD902F-40-15R1-A10K, as the strip (the '-00D…' suffix the footprints carry is still open, as on the strip) |
| Bus header 2×17 | Würth 61203421621 |
| Link headers 2×20 / 2×8 | Würth 61204021621 / 61201621621 |
| Ferrites | Murata BLM21PG221SN1D (220 Ω at 100 MHz, 2 A, 45 mΩ) |
| 0.1 % 2K2 / 10K | Panasonic ERA-6AEB222V / ERA-6AEB103V |

- **The ferrite is a stability part.** The aux summer's margin depends on its inductance: 66 / 73 / 82° at 0.25 /
  0.5 / 1.5 µH, and 57° shorted. A lower-inductance 220 Ω signal bead is not a free substitute.
- **Group RV2 (sub pan):** it inherits a B10K-with-detent MPN that isn't stocked. This is the same open item as strip
  RV8.
- **Spec §24:** it says SB540 (axial) where the schematic has SS54 (SMC).
- **Footprints and pinouts:** every semiconductor footprint matches its package and KiCad pin numbering. That covers
  SS54, BAT54W, BZX84, BZT52, MMBT3904, BCP53 and LME49600.
- **DNP:** exported for master R62/R73 and group R32/R50/R54.

## 17. Resistor power (minor, as strip T10)

- **Group R1/R2 (10R, ±VA):**
  - Load: 7 × OPA1612 + 2 × DRV134, 61 mA typical: 37 mW (30 %).
  - At the OPA1612's over-temperature maximum IQ: 77 mW (62 %).
  - With both DRV134s at +20 dBu into 600 Ω: 137 mW (110 %).
  - Fix: ERJ-P06J100V.
- **Master R1/R2 (1R, ±VA):**
  - 20 mW typical; 36 mW at maximum IQ; 59–90 mW with every DRV134 at +20 dBu into 600 Ω (depending on the stage-load
    assumption).
  - A PSU-lead hot plug puts at most ~68 mJ into it. That is an upper bound for a stiff source: the PSU's 220 µF
    output behind a current-limited LDO, shared with the wings, makes it much smaller.
  - Panasonic gives an overload rating for ERJ-P06 but no single-pulse curve, so the pulse rating is unverified.
  - Fix: ERJ-P06J1R0V.
  - Spec §25's "carries about 0.5 A" predates the M1 split; it is ~0.14 A typical, ~0.25–0.3 A worst.
- **Insert-send 75R** (master R16/R24, group R11): 258 mW into a shorted lead (OPA1612 ISC +55 / −62 mA). Fix:
  ERJ-P06J750V.
- **Fine as they are:**
  - ±VM 10R (19–30 mW), ±VL 10R (≤ 7 mW), meter 120R / 27K;
  - relay 560R (37–57 %; coil 12.0 V, 113 % at the crowbar threshold, under its 150 %);
  - Q1 (~56 mA), the BCP53s (~157 mW dark), BZX84 / BZT52 (≤ 13 mW);
  - BAT54W (11.8 V reverse), LM393B (10.3–12.9 mA of its 25 mA).

**Remote meter header CN4** (note, no change while unused): it takes C/Room and ±VM off the board unprotected.
- **Shorted MTR lead, as designed:** up to 1 W in R127/R163 and ~0.7 W in U21; the 100R takes 10 V of the swing.
- **Both MTR leads shorted:** ~1.4 W in the one OPA1656 package (a rise of ~167 °C at 121 °C/W).
- **With MG6's 100R build-out in series:** a short sees 200 Ω, so ~0.3 W rms (0.64 W peak) in each 0805 100R and
  ~0.1 W in U21.
- **±VM short on a bridge cable:** burns R5/R6.
- **Calibration:** a bridge drawing > ~60 mA moves the meter's 0.63 V calibration tap.

If a bridge is fitted: feed MTR through 1K (−1.2 dB, inside the trim range), and power the bridge from its own fused
branch.

## 18. Stages that pass, and the merged set

Worst case over every configuration. The fixes column is the merged set; "unchanged" means no fix touches the stage.

| Stage | Board | As designed | With the fixes |
|---|---|---|---|
| GCANCEL buffer U1A | master | 88.8° nominal; 66.0° with 47 pF | unchanged |
| GC buffer U1A | group | 83–85°; 61.5–62.8° with +47 pF | unchanged |
| MIX summers U1B/U3A (4K7 ∥ 100p, ferrite) | master | 70.1–74.1° at N = 1; 92–96° at N = 24–32; 58.5° with the ferrite shorted | unchanged |
| Sub summer U1B / aux summer U6A (ferrite) | group | ≥ 62.9° / ≥ 66.4° (N 0–28, 0–10 nF; U6A 76–78° at the real N = 24); 57.6° / 56.8° with the ferrite shorted | unchanged |
| MIX re-inverters U2A/U3B | master | 57.0° with 47 pF | 60.7° with 47 pF; 58.7° with a dead insert plug at the fader top + 47 pF |
| Sub / aux re-inverters U2A, U6B | group | 65.6° / 69.6° board | 68.1° / 65.2° board; 52.7° / 48.3° with +47 pF |
| Aux 5/6 summers U12A/U15A, re-inverters U12B/U15B | master | 68.2° with 47 pF (68.6° at N = 1); 59.4° | unchanged; 55.8° (the level buffers' 10p at the pot top) |
| Mono U4B / U6A | master | 63.7° / 61.0° with 47 pF | unchanged |
| PFL summer U18A, re-inverter U18B (OPA1656) | master | 56.2–61.0° / 57.2–68.0° | unchanged / 57.2° (MG3's 22p on its output at the solo-pot top) |
| Return receivers U8A/B | group | 74.2–75.8° board | 69.3–70.7° (the 10p at RTx_LIN on their output at the pot top); 51.6° with +47 pF |
| Spares U6B, U19B | master | 86.8° | unchanged |
| Meter rectifiers U29A/U36A | master | ≥ 69° classic; 43–48° TL07xH model (its own follower figure is 38–44°) | unchanged |
| DRV134 ×7 / ×2 | both | no output peaking with 10 µF Sense caps and 0–100 nF; step overshoot ≤ 5.9 %; Zout rises monotonically | unchanged |

The ferrites stay: each resonates with the bus capacitance (series LC, 3.6–18 MHz) and notches the loop gain, but every
crossing keeps its margin (the notch's up-crossings sit +25° from −180°). They add ~7° (sub) and 10–16° (aux),
depending on the bead's inductance (§16).

**The merged set's worst units:**
- **Master:** every unit ≥ 47.8° except the EXT receivers U17A/B, which are 42.9° with EXT selected and 47 pF until
  MG1's 100R is fitted (73–74°; the harness's `MG` set does not include it).
  - CRS followers U21: 47.8–48.5° (pots at the top, placed estimate).
  - Post-amps U5: 51°.
  - Aux level buffers U13: 51.6–52.8° with 47 pF.
- **Group, without extra C:** every fixed stage ≥ 64.9°; the untouched summer U1B is at 62.9° with a 1.5 µH bead.
- **Group, stress:** ≥ 56° with +22 pF on every output and ≥ 46.4° with +47 pF (U9B, §10).
- **Below 45°:** on the master, U17A/B without MG1's 100R (above), and the meter loops with the pessimistic TL07xH
  model (~40–43°; §8, §9). On the group, only two cases outside the stress spec: +100 pF directly on SUB_RBUF (41°), and FB2 shorted with
  +47 pF on A_SUM (42.6°).

## 19. Group bus-select jumpers (important)

Each group board picks its SUB and AUX bus with solder jumpers (JP1–JP8). Nothing stops two boards being jumpered to the
same bus. Then two virtual-earth summers share one summing node, each with its own 4K7 feedback:
- **The fault:** their difference mode has no feedback, so the two outputs run to opposite rails: −16.55 / +16.46 V
  from a 0.1 mV offset difference.
- **Insert send:** S_MIX is DC-coupled to the insert send through R11 75R, so the send tip then carries ~16 V DC to
  outboard.

Fix (MG19):
- **Assembly rule:** one SUB jumper and one AUX jumper per board, unique across the four.
- **Marking:** the group number on the silk, and in the spec.
- **Jig check:** test_jig_spec could add one.

## 20. Aux outputs without a mute relay (your call)

The six main / C/Room / phones outputs have mute relays. The group's sub outs don't, and spec §12 justifies that: they
feed recorders and processors, not speakers. The aux outs (group aux 1–4, master aux 5/6) have no relay and no such
note:
- Aux sends commonly drive monitor and headphone amps.
- At power-up they get the master spec §8 rail-skew step: 0.2–0.75 V differential and 1.2–3.0 V common-mode for 10–100 ms.

Either a decision note in spec §13 ("aux outs unmuted: mute monitor amps at power-up"), or a G6K per aux out on the
same control as master spec §8 (six relays, a board change on both modules). **Your decision (MG20).**

## Found along the way

- **Net-name lint:** `verify.py` can't catch a collision like §1, because the intended JSON comes from the same code.
  A netlist lint could flag any net that joins an IC output pin and a connector pin directly. Every legitimate path on
  these boards has a part in between (a build-out, a coupling cap, a relay contact).
- **Return L jack J4 (group, optional):** its TN/RN switch contacts are unconnected. An unplugged return routed to MIX
  or SUB leaves both receivers' inputs floating: 1M on the tip, and the ring open into 10K. Tying J4's TN/RN to GNDA
  would silence an unplugged return; with J5 normalled to J4, both go quiet. Also, a mono plug into L loads its
  source with both receivers: the ring leg sees 5 kΩ.
- **Model limits:**
  - TI's OPA161x model gives unusable noise in ngspice: a follower comes out at 56 nV/√Hz at 1 kHz, from its diode
    1/f sources. The noise figures here use a datasheet-noise model.
  - TI's DRV134 model gives +6.75 dB of differential gain (datasheet 6 dB). It is fine for stability, but don't take
    level or headroom figures from it.
  - A Tian probe at the DRV134's own output pins can't be interpreted: the cross-coupled common-mode loop makes the
    broken loop non-minimum-phase. Use the closed-loop response, Zout and a kick test.
- **Strip electrolytics:** the strip's 47u NP and 220u NP use the same footprints, so the §16 MPNs apply. Its 220u 25V
  polar on D8 P3.5 takes UPW1E221MPD.
- **Gain-margin test:** `sim/review/strip/stab.py` treated a phase wrap at 0° (mod 360) as a −180° crossing. It reported
  e.g. "gm 1.4 dB" inside a ferrite notch where T is positive real. Fixed in this commit (test the wrapped value).
  Phase-margin verdicts were unaffected.

## Review sims (`sim/review/master/`, `sim/review/group/`)

TI's models stay out of the repo. Put them in one folder and set `TI_MODELS=/path/to/that/folder`:
- **master:** `OPA161x.LIB`, `OPA1656.LIB`, `DRV134.LIB`, `TL072_boyle.lib` (SLOJ067), `tl07xh_tl08xh.lib` (SLOM513A);
- **group:** `OPA161x.LIB`.

The LME49600 macro is our own fit and lives in `masterdeck.py`. Each folder's `.spiceinit` sets `ngbehavior=psa`, which
TI's models need. The decks read `master.net` / `master_jack_board.net` / `group.net` from the repo root, so regenerate
those first.

| Script | What |
|---|---|
| `master/masterdeck.py` | The whole master module as one deck: both netlists joined through the link; a Tian probe at each unit's output and a source at each + input |
| `master/run_all.py <fixset> [configs\|all] [units]` | Loop gain over the configurations in `configs.py`, in parallel (`NJ`); e.g. `python3 run_all.py none all`, `python3 run_all.py MG p100_out47` |
| `master/fixes.py` | Fix sets; `MG` = the recommended set (MG2–MG7; MG1's 100R and MG9 are not in it), `MG22` = 22p in `level_buffer()` |
| `master/run_phv.py`, `lmefit.py` | Phones composite variants with the LME49600 macro and its bracket; the macro's fit to SNAS422E |
| `master/meterstab.py`, `metertran.py`, `meterburst2.py` | Meter TL072 loops (both models) and the peak-mode tone-burst readings. With the TL07xH model, check the operating point (§8) |
| `master/extbug.py`, `drvtest.py`, `audio.py`, `steps.py` | The EXT net collision; DRV134 with its Sense loop; audio-band cost; step overshoot |
| `master/pcblen.py` (KiCad Python) → `master_len.json` | Pad-to-pad MST length per net on the placed board, for the trace estimate |
| `group/groupdeck.py`, `stabg.py` | The group deck (bus, ribbon, jack-board and DRV134 models) and the loop-gain analysis |
| `group/sweep.py <pots\|bus\|ins\|ret\|loads> <fixset> [pF/mm]` | Sweeps; e.g. `python3 sweep.py loads mg 0.08`; `fixes.py`: `mg` = recommended, `mg22`, `rec` (the analyst's set). The `loads` set has no pot at 0.3, where U5B / U9 are worst with extra C (§5) |
| `group/u2b.py`, `u2b_prot.py`, `tranrun.py`, `audio.py` | Insert-return build-out and protection variants; steps; audio-band cost |
| `group/padpos.py` (KiCad Python) + `mst.py` → `mst_all.json` | The group's MST lengths |

Reproduced from the repo folders with the recommended sets:
- group `ret`: U8A/B 69.6 / 69.3°, U9A/B 71.3 / 69.0°;
- master `p100`: U2B 77.2°, U19A 74.5°.

The skeptics' independent decks stayed in the review scratch; their figures are quoted above.
