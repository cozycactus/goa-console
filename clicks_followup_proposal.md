# Clicks batch follow-up: RV3b (direct-out cold leg) and RV9b (relay driver with −V lost)

**Signed off by Ruslan 2026-10-29 ("continue") and applied the same day (strip v5.7, master v0.14); see Sign-off.**
Two findings of the independent review of the applied clicks batch (2026-10-29, `clicks_proposal.md`
"Review"). Both are small netlist changes on circuits the batch touched; neither moves an existing part. Placement by
`moves_only` as the batch's own parts.

## RV3b — the direct out's cold leg has no DC bleed and no clamp (strip)

**What RV3 did.** J5's ring went from "R73 75R to GNDA" to "R73 75R → C107 33 µF NP 25 V → GNDA", so the two legs
have the same source impedance at LF (CMRR at 50 Hz ~46 → ~60 dB into a 20 kΩ-per-leg receiver).

**What it broke** (CONFIRMED from `channel_strip.net`: DO_R = {CN3.9, R73.1}; R73.2 only meets C107.1):
1. The ring has no DC path at all now. The hot leg has R72 47K from DO_T to GNDA; the ring floats at whatever the
   receiver's bias and C107's leakage settle to.
2. `cs4_proposal.md` (strip v5.2) put a BAV199 on every jack-link signal and left DO_R out with the words "it only goes to
   ground through R73 75R". That premise is gone. The forbidden case CS4 exists to survive (a TRS-to-XLR lead into a
   phantom-powered mic input: +48 V through 6K8 per leg) now charges C107 to ~48 V through 6K8 + 75R with nothing
   limiting it, while the hot leg's C52 is held to 17.7 V by D22. C107 is a 25 V part.

**Proposal: mirror the hot leg completely.**
- **R143 47K** (RC0805FR-0747KL, as R72) from DO_R to GNDA: the ring's DC bleed. Noise / level: nothing (47K across a
  75R + 33 µF leg).
- **D23 BAV199** at DO_R (pin 3 DO_R, pin 2 +VA, pin 1 −VA), as D22 on DO_T: phantom leaves C107 at 17.7 V like C52,
  ESD into the ring is clamped before R73 instead of into C107.
- Spec §11 line becomes "both legs 75R + 33 µF + 47K, both clamped"; `cs4_proposal.md`'s DO_R line already points here.
- Why not drop C107 instead: the LF CMRR gain of RV3 is real (46 → 60 dB at 50 Hz with the caps 20 % apart), and two
  0805-class parts restore everything the single cap took away.
- Why 47K and not a lower value: the hot leg's R72 is 47K; equal bleeds keep the legs' impedances equal below the
  corner, which is RV3's whole point.

**Netlist (gen.py, created last so no reference moves):**
```
P(b,'R143','R','47K',{1:'DO_R',2:'GNDA'})
P(b,'D23','DD','BAV199',{1:'-VA',3:'DO_R',2:'+VA'})      # as D18-D22 in the JACK LINK CLAMPS block
```
Drawing: R143 under R73 in `strip_draw.direct_out`; D23 in the clamps block beside D22 (`link_clamps`-style fragment).
Placement: `moves_only`, bottom side, near CN3 pin 9 for D23 (the other clamps sit at CN3) and beside C107 for R143;
probe with the guard-consistent probe. Checks: sim_netlist (direct-out level and the common-mode check unchanged),
`sim/review/cs4/jack_protect.py` for the ring (expect the hot leg's 17.7 V), check_all.

## RV9b — the relay driver can stay on with −V lost (master)

**What RV9 did.** U10B's + input moved from GNDD to +1.0 V so that, with −V lost and −VL sitting at about +0.5 V
(the console's quiescent current drives −VBUS to the SS54 clamp), both comparator inputs stay inside the LM393B's
range and RAIL_OK is pulled low correctly.

**What it does not cover** (PLAUSIBLE: simulation at the datasheet corner, `sim/review/clicks/mute_rbe.cir`): the
relay driver Q (MMBT3904, emitter on GNDD, base from MUTE_GO through 4K7) is driven by comparators whose "low" is
referenced to −VL. With −VL at +0.5..0.65 V the Schmitt comparator's low output sits at −VL + V_OL = 0.65..1.0 V above
the emitter, and the 4K7 alone does not keep the transistor off:

| −V clamp | V_OL | base | coil current (one G6K-2F-Y, 9.1 mA rated, must-release 10 % = 0.91 mA) |
|---|---|---|---|
| 0 V (the deck's old case 4) | 0 | 0.21 V | 0.2 µA: releases |
| +0.45 V | 0 (typical) | 0.65 V | 0.11 mA (1.2 %): releases |
| +0.45 V | +0.2 V (datasheet corner, 0.4 V max at 4 mA) | 0.71 V | 1.0 mA (11 %) |
| +0.6 V | +0.2 V | 0.73 V | 1.9 mA (21 %) |

So with typical parts the relays release; at the LM393B's V_OL corner with a 0.6 V clamp a relay that was closed when
−V dropped can stay held at 11-21 % of its rated coil current, which is exactly the "phones DC on the cans" case RV9
was written for. Not a regression (the GNDD-referenced version had the same driver), but RV9's text "both inside the
input range" treats the fault as closed, and `sim/mute.cir`'s case 4 (−V to 0 V) cannot show it.

**Proposal: one base-emitter resistor.** R 4K7 from RLY_B to GNDD (RC0805FR-074K7L). It divides the comparator's
residual low level 2:1 before it reaches the base (4K7 series / 4K7 shunt), the standard pull-down on an NPN switch
fed from an open-collector output with a pull-up. Same deck, every case:

| R B-E | worst case above (0.6 V clamp, V_OL +0.2) | base | coil current | power-up close (unchanged 2.80 s?) |
|---|---|---|---|---|
| none | | 0.73 V | 1.87 mA | 2.795 s |
| 4K7 | | 0.51 V | 0.2 µA | 2.795 s |
| 2K2 | | 0.31 V | 0.1 µA | 2.795 s |
| 1K | | 0.18 V | < 0.1 µA | 2.796 s |

Drive margin with 4K7: MUTE_GO high is +VL through its 4K7 pull-up, base current (17 − 0.7) / 4K7 − 0.7 / 4K7 ≈
3.3 mA against six coils' 55 mA / h_FE ≥ 100 = 0.55 mA needed; the pull-up's 230 mW per power-up (MG12) is unchanged.
4K7 is enough and the smallest load on the pull-up; 2K2 if Ruslan prefers a 4:1 margin. Why not an emitter on −VL:
it changes the driver's normal-state levels and the fast-release path (RLY_B → D → 4K7 → RAIL_OK) and buys nothing
over the resistor.

**Netlist (gen_master.py, in the mute block after `qd`; the master's parts created after it are the LATE_* blocks, so
make it the last `R` in that block or append it to the LATE list so no reference moves):**
```
R(b, '4K7', 'RLY_B', 'GNDD')      # base-emitter pull-down: holds Q off with -V lost and -VL at +0.5 V (RV9b)
```
Placement: `moves_only` beside Q (bottom or top, probe). Checks: `sim/mute.cir` (v4) unchanged on cases 1-6,
`sim/review/clicks/mute_rbe.cir` for the fault, check_all. **Bench item** (either way): with the console on and the
relays closed, open the −V wire at the master's J1 and confirm every relay releases (test_jig_spec.md, master bench list).

## Also recorded by the review (fixed 2026-10-29, no sign-off needed)
- The −V trip is −14.3 V with 64K9 (65.3K would hold the old −14.4 V exactly; the zener's ±3 % moves it ±0.3 V):
  numbers corrected in the master spec, clicks_proposal.md, gen_master.py's comment and docs/decisions.md.
- `sim/mute.cir` is v4 (the RV9 values); cases 1-6 as before, −V-lost release at −14.14 V (was −14.24).
- R142's cost: 0.1 dB at +15 dB, 0.06 dB at the detent, 0.02 dB at −15 dB (it parallels the feedback half only);
  the proposal and spec §4 had said "nothing at the detent". R142's pads are 8.6 / 9.9 mm from U1's pins (not "at the
  pin"): the nearest free spot; comments corrected.
- gen.py's title-block comment said v5.5; regenerated (title blocks only, netlist identical).

## Sign-off
Signed off 2026-10-29 and applied: RV3b as proposed (R143 47K, D23 BAV199 at CN3; strip 946 pins / 329 parts, D23 beside
D22 and R143 beside C107 on the bottom, nothing else moved); RV9b with 4K7 (R240, made last, on the bottom under Q1,
pads 2.1 mm from Q1's base / emitter through the board; master 1820 pins / 632 parts). `sim/mute.cir` v5 carries the
resistor (cases 1-6 unchanged); the bench item is in master spec §8.
