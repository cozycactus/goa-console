# Clicks, DC and the −V detector: RV3, RV4, RV7, RV8, RV9 (proposal, 2026-10-28)

**Not signed off.** From `project_review.md` (2026-10-28), the circuit WARNs that cost parts: five small additions on
the strip, the group and the master, every one a cap or resistor in an existing node, no topology change. The change is
`clicks_proposal.patch` (tools only: `gen.py`, `strip_draw.py`, `gen_master.py`, `gen_group.py`), checked on a trial
tree (§5). RV5 (MUTEOUT DC on the fader / pre-aux pot tops) and RV6 (U16 input headroom) are not in it: see §6.

## 1. What and why

| ID | Board | Change | Why |
|---|---|---|---|
| **RV3** | strip | **C107** 33 µF NP (MUSE ES, as C52) between R73 and GNDA; R73 the same anti-surge ERJ-P06J750V as R71 | The direct out is impedance-balanced: hot leg DOUT – R71 75R – C52 – DO_T, cold leg DO_R – R73 75R – GNDA. The hot leg's source impedance is 75 − j96 Ω at 50 Hz against the cold leg's 75 Ω, so a 20K-per-leg receiver sees a CMRR limit of ~46 dB at 50 Hz, ~52 dB at 100 Hz, ~72 dB at 1 kHz: weakest at hum. With C107 both legs are 75R + 33 µF (the match then rests on the two caps' ±20 %: ~1 − 20 % of j96 Ω at 50 Hz, ~56 dB; sorted pairs as CS11b would give more). R73 was a plain 1 % Yageo (5 % R71 against it: up to 3.75 Ω). |
| **RV4** | strip | **R142** 1M from GOUT to U1B's − input (GV) | `Net-(U1B--)` is U1.6, RV9.2 and C37 only: the gain pot's wiper is U1B's only DC feedback path (the Delta's ED3344A topology: 2K2 – pot – 2K2, wiper to the summing node). A lifted or bouncing wiper on the most-turned pot leaves 22 pF of feedback and 60-250 nA of bias: the output ramps at 3-11 V/ms to a rail, a bang on PRE and every bus. 1M in parallel with the 2K2-12K2 feedback costs < 0.1 dB at +15 dB, nothing at the detent, and keeps U1B closed. |
| **RV7** | master, group | a **2.2 µF MKS2 film** between each aux level buffer's output and its AFL 22K (master aux 5 / 6, R69 / R80; group aux n) | The level buffers (`master_lib.level_buffer()`) are biased by 100K: their outputs sit 6 mV typical, 25 mV worst (OPA1612, 60-250 nA) off ground. Pressing AFL moves the 22K from GNDA onto the PFL virtual earth: a unity-gain DC step onto PFL_SUM, 96 % intact when the DG413 switches to PFL 5.8 ms later (the couplers' 0.2-0.3 s constants), a tick of about −42 dBu typical / −30 worst at CRS, +6 dB at the C/Room TRS; the reverse step on release. Every other PFL / AFL source is AC-coupled already (the strip since K1 with C96, the group's sub AFL after its coupler, the returns from PRE). Same part and placement rule as K1. |
| **RV8** | master | a **100 µF NP** (MUSE ES UES1E101MPM) in series with each phones gain-set 2K2 (R132 / R136, net PH_GL / PH_GR), so the composite's DC gain is 1 | The OPA1612 + LME49600 composite is DC-coupled to the jack with a gain of 1 + 4K7 / 2K2 = 3.14 and 100K (R129 / R133) on its + input: 19 mV typical, 79 mV worst on the cans continuously, and K6 closes onto it 2.8 s after power-up (a click in sensitive IEMs, which is what the relay is for). With the cap the DC gain is 1: ~6 / 25 mV, the AC corner 1 / (2π 2K2 100 µF) = 0.72 Hz (−0.1 dB at 20 Hz). Spec §21 and MG2 / MG11 didn't cover it. The 100K stays (22K would need a 10 µF film at the input). |
| **RV9** | master | the −V-loss comparator U10B's + input on **+1.0 V** (new 51K from VREF6 and 10K to GNDD, net SENSE_REF) instead of GNDD; its −V sense divider's lower leg **R53 51K → 64.9K** so the trip stays at −14.4 V | If the PSU's −V regulator drops out (LDO thermal shutdown, an LRS-150 hiccup) or a −V wire opens with +V up, the console's quiescent current drives −VBUS positive until D2 (and the PSU's D7) clamp it at ~+0.45 V, so −VL, U10B's own V−, ends at ~+0.5 V: its + input (GNDD, 0 V) is then 0.5 V below V−, past the LM393B's −0.3 V absolute maximum (TI: the parasitic input current "may cause output to be incorrect"). If it misreads, RAIL_OK floats high, the 2M2 / 2.2 µF timer re-arms and all six relays close 2.8 s later with −V gone, which puts the phones' DC fault on the cans. With the + input at +1.0 V and the divider re-scaled: SENSE_N = +0.34 V with −17 V (ok), +4.7 V with −V lost (fault), both inside the input range; trip at −VBUS = −14.4 V as before. `sim/mute.cir` (an ideal LM393, the trip only) doesn't model the fault; the fix is two resistors and a value. |

Not changed: the +V-loss case (the coil supply +VBUS and the base drive +VL both collapse), the AVG meter mode's
open-loop peak stage (reading unaffected), the group's unused −VL (R4 / C4; symmetry with the strip).

## 2. The circuits

```
RV3  DOUT ─ R71 75R ─ C52 33u NP ─ DO_T ─ J5 tip          DO_R ─ R73 75R ─ C107 33u NP ─ GNDA      (was R73 ─ GNDA)
RV4  RECV ─ R45 2K2 ─ RV9 (10K lin) ─ R46 2K2 ─ GOUT;  RV9 wiper ─ U1B−;  R142 1M + C37 22p from GOUT to U1B−
RV7  A5_OUT ─ C(new) 2.2u film ─ A5_AFLC ─ R69 22K ─ AFL key ─ PFL / GNDA          (master aux 5 / 6, group aux n)
RV8  PH_N ─ R132 2K2 ─ PH_GL ─ C(new) 100u NP ─ GNDA     (the 4K7 / 100p feedback unchanged)
RV9  VREF6 (6.2 V) ─ 51K ─ SENSE_REF ─ 10K ─ GNDD → U10B +;   VREF6 ─ R52 22K ─ SENSE_N ─ R53 64.9K ─ −VBUS → U10B −
```

Refs: the strip's new parts are named (R142, C107); on the master and the group every new part is created last
(`master_lib.DEFER`), so no existing ref moves. The strip drawings (`strip_draw.gain`, `direct_out`) place R142 under
U1B and C107 under R73; the master / group caps and the RV9 divider are drawn by `schgen.flow()` as labelled parts.

## 3. Numbers

- **RV3 CMRR limit** (source-impedance imbalance into 20 kΩ per leg, 20 log(2 R_cm / ΔZ)): as built ΔZ = 96 Ω at 50 Hz
  → 46 dB, 48 Ω at 100 Hz → 52 dB, 4.8 Ω at 1 kHz → 72 dB; with C107 and the caps 20 % apart ΔZ ≈ 19 Ω at 50 Hz → 60 dB
  (10 % apart: 66 dB); the resistors' 3.75 Ω → 75 dB.
- **RV4 gain error**: feedback 2K2 + (10K − x) against 1M: at +15 dB (x = 0) 12.2K ‖ 1M = −0.1 dB; at the detent the
  divider is symmetric and the 1M shifts nothing measurable. Noise: 1M's current noise at the summing node (0.13 pA/√Hz)
  is under the OPA1612's 1.7 pA/√Hz. Stability: 1M in parallel with the feedback network changes the loop by < 1 %
  (`run_all.py` state c01 to be re-run on TI's model when the lib is available: `OPA161X_LIB`, not in the repo).
- **RV7 step**: 22K from a 6-25 mV source into the PFL summer's 22K feedback (unity): 6-25 mV at PFL_SUM; CRS follows at
  unity; the C/Room DRV135 adds 6 dB. With the film cap: the step is the cap's charge imbalance only (the AFLC node sits
  at 0 V through the 22K when released and at the virtual earth when latched: no DC moves).
- **RV8**: output DC 3.14 × (Vos + Ib × 98.5K) → 1 × (…): 19 → 6 mV typical, 79 → 25 mV worst. The 100 µF NP sees < 30
  mV: a MUSE ES at 25 V is fine. Frequency response −3 dB at 0.72 Hz; the 2.2 µF / 100K input coupler already sets 0.72 Hz,
  so the LF corner moves from 0.72 to ~1.0 Hz (two equal poles), −0.1 dB at 10 Hz.
- **RV9**: SENSE_REF = 6.2 × 10 / 61 = 1.016 V. SENSE_N with 22K / 64.9K: −17 V → +0.33 V; −16 V → +0.59 V; trip
  (SENSE_N = 1.016 V) at −VBUS = −14.4 V; −V lost (+0.45 V) → +4.74 V. The comparator's inputs then sit 0.5 and 4.2 V
  above its V− (LM393B common mode from V− to V+ − 1.5 V). +V-loss: unchanged (SENSE_P against VREF6).

## 4. Parts and placement

| Board | New | Count per board | Placement |
|---|---|---|---|
| strip | R142 1M 0805, C107 33 µF NP (UES1E330MPM, 6.3 mm can) | 2 | `moves_only` (as CS1 / CS4 / CS6): R142 at U1's − pin on the bottom, C107 beside C52 at the jack-link header; nothing else moves |
| group | C 2.2 µF MKS2 (bottom, as the strip's films) | 1 | `moves_only` beside the aux AFL key |
| master | 2 × 2.2 µF MKS2, 2 × 100 µF NP, R 51K, R 10K | 6 | `moves_only`: films at SW (aux AFL keys), the NP cans at U26 / U27, the divider at U10 |

Console: +48 strips' 33 µF, +48 1M, +4 group films, the master's six. BOM / order list regenerate.

## 5. Checks on the trial tree (a copy of the tree with the RV1 / RV11 commit, `clicks_proposal.patch` applied)

KiCad 10.0.7 (Linux), ngspice 42:
- **Strip:** 941 pins / 327 parts (was 937 / 325), 0 mismatches, check_fp 0, ERC 0; jack board unchanged. `sim_netlist`
  45/45 (the direct out at J5's tip and the gain-stage checks unchanged). Drawings: R142 under U1B between the − input
  and the output (page 03), C107 under R73 (page 13); both pages exported and looked at.
- **Master:** 1808 pins / 626 parts (was 1796 / 620: 2 films, 2 NP cans, 2 resistors, all created last), 0 mismatches,
  check_fp 0, ERC 0; the new parts in labelled rows (SENSE_REF, A5_AFLC / A6_AFLC, PH_GL / PH_GR).
- **Group:** 807 pins / 292 parts (was 805 / 291), 0 mismatches, check_fp 0, ERC 0.
- `check_bus.py`: every header as the Delta map. `sim_console.py`: 45/45 (levels, pan, mutes, SUB 1-4, aux 1-6, PFL,
  returns, EXT, DIM, crosstalk, ground, noise all as before: the new parts are outside the AC paths at 1 kHz).
- Not run (no TI models in the repo): the strip deck's U1B margin with the 1M (`sim/review/strip/run_all.py none`,
  expected unchanged within 1°), the master deck's U26 with the 100 µF in the gain-set leg (`run_each.py`: the leg's
  impedance at HF is 2K2 as before). Placement not done (moves_only spots to be chosen on sign-off); the BOM lines are
  existing MPNs (UES1E330MPM, UES1E101MPM, MKS2C042201K00KSSD, Yageo 0805) plus a 64.9K 1 % (RC0805FR-0764K9L).

## 6. Left out, for the record

- **RV5** (MUTEOUT's 3.4 / 14.6 mV DC on the fader top and the pre-fade aux pot tops; scratchy worn tracks): U3B's
  bias current returns through R17 + R16 + R13 = 56.4K, R13 being PRE's 47K bleed. R13 10K gives ~4.9 mV worst (C11
  100 µF still 0.16 Hz; PRE's source sees 10K instead of 47K, which the post-EQ follower drives without trouble). A
  100 µF NP in MUTEOUT would AC-couple the fader and the pre taps instead, but adds a coupler into the fader's 10K and a
  can at the fader; the Delta drives its fader DC-coupled from the mute FET too. Ruslan's call: accept (new pots are
  quiet) or R13 10K.
- **RV6** (OPA1656 common mode (V+) − 2.25 V: the tip leg clips at ~+21.9 dBu, not +23): a documentation correction to
  `gaps_proposal.md` and the spec's headroom line, or accept.

## Sign-off

(open)
