# Channel Strip — Component-Level Specification v4.8
## Soundcraft Delta Theatre input without the mic stage. One PCB per channel, ×24.

Bus pinout, grounding and power: `console_architecture.md`. Stage-by-stage comparison with the
Delta, the signed-off decisions and the simulations behind this version: `delta_clone_comparison.md`.
Reference designators are those of `tools/gen.py`; Delta drawing numbers are given where a
circuit comes from a Delta sheet (ED3344A/B/C = Theatre input RH board, ED3151 = LH board).

---

## Changes in v4.8 (2026-10-26, signed off; `pan_buffer_proposal.md` PAN1)

- **Pan buffer L** (§12, §14): moves from U2B to U8B, which was the spare beside U3 and the pan pot; U2B at the fader end
  is the spare now (+ to AGND, output on its − input). Parts and BOM unchanged.
  - The pan pot's L wiper line (C79 10 pF at the + input, unchanged) shrinks from 165 to 24 mm.
  - Its nearest switching pad is now 11.6 mm away (+5VL at C61 was 2.9 mm from U2 pin 5).
  - Stability (TI OPA161x, 21 states) unchanged: U8B 80.2–87.5° as U2B was.
- **Placement** (§16): 8 parts moved (C16, C79, R70, five resistors of the y 196 row). U2, U3, U8, C17 and U2's post-amp
  parts are now fixed in `place_strip.py`.

## Changes in v4.7 (2026-10-26, signed off; `feature_gaps.md` MET1)

- **Signal / overload LED** (§8.1): D2 becomes a red / green bicolour (Kingbright WP3VEGW, 3 mm, common cathode) in the
  OL LED's hole at (20.6, 50). Red is the overload as before; green lights from about −20 dBu with the same ~150 ms hold.
  - A second LM393 (U17) copies U4 one level lower. U17A sees PRESRC through R118 47K with a BAT54W clamp (D11), against
    VTH = VREF × 10K / 760K = 0.111 V (R119 750K / R120 10K, so VREF moves 0.7 %). It discharges SIG_HOLD (R121 1M,
    C99 220 nF), and U17B lights green while SIG_HOLD is below VREF.
  - Each colour has a PNP high-side switch (Q3 red, Q4 green, MMBT3906, 47K base resistors and pull-ups, R15 / R124
    4K7), so it draws current only while lit.
  - In overload, Q5 (a PNP from U4B's output through R125) holds Q4's base at +VL, so the red shows alone and the green
    draws nothing.
  - `sim/review/gaps/ol.py`:
    - red from +18.1 / +18.4 / +18.4 dBu at 50 Hz / 1 kHz / 10 kHz; green from −19.5 dBu;
    - holds 152–190 ms (red) and 170 ms (green);
    - 3.2 mA in either colour; the green is off in overload.
- **Supply:** ≈ +4 mA on +V per strip while green is lit (green 3.2 mA, base 0.3 mA, U17 ≈ 0.5 mA): ≈ 104 / 87 mA per
  strip (master spec §27). Nothing on −V.
- **Placement** (§16): the detector and switches (17 parts) sit in the free column left of the fader (x 1–10,
  y 298–324). They carry only DC and the low-impedance PRESRC, so the signal path keeps its places.

## Changes in v4.6 (2026-10-25, signed off; `design_review.md` Q1, R4, R5)

- **ON also mutes the pre-fade sends and the direct out** (§1, §11, Q1).
  - The pre-fader taps (JP2–JP4, 1-2) now come from MUTEOUT (U3B, after the J112 mute, before the fader), not PRE.
  - `tools/sim_netlist.py` checks both: aux 1 pre and the direct out are −86 dB with ON released.
  - The pre-EQ jumper setting (2-3, HOUT) stays ahead of the mute.
  - PFL stays at PRE, so a muted channel can still be soloed.
  - U3B now also drives the pre aux pots: worst phase margin 59.8° on TI's model (direct out at the top, a cable on
    J5), 72–74° elsewhere.
- **PVA2 orientation mark** (§16.1, R4): the placer prints a silk "2" beside pads 1/4 of every key, inside its outline.
- **BOM** (R5): MPNs for the C0G caps (KEMET), the rail electrolytics (Nichicon), R6–R9 (ERA-6AEB103V), C48 (WIMA
  MKS2C031501A00KSSD, check stock) and D9 (Nexperia). C49 on the W7.2 film footprint like C13 / C96. A value's voltage
  is its minimum rating; the MPN may be higher.

## Changes in v4.5 (2026-10-25, signed off; `gaps_proposal.md` K1, K3)

- **PFL send DC block** (§8.2, K1): C96 2.2 µF film (WIMA MKS2, bottom side) in series with R32.
  - Why: U3B's bias current leaves PRE 3–14 mV off ground, and the PFL key put that on the PFL bus as a tick, up to
    11.5 mV.
  - Now: no step (`sim/review/gaps/keys.py`); the PFL send's low corner is 3.3 Hz.
- **Overload detector, fast attack and hold** (§8.1, K3):
  - C12 1 µF → 100 nF, a 0.1 ms attack. With 1 µF short peaks never lit the LED.
  - U4B, the spare half, is a hold stage (R115 1M, C97 220 nF): the LED stays lit about 150 ms after the last
    overload.
  - Simulated (`sim/review/gaps/ol.py`): threshold +18.2 to +18.5 dBu as before; lit 154–192 ms for 2 cycles at
    +19 dBu or a single cycle at +20 dBu.
- The other gaps closed in the same pass pass as built: soft mute, key clicks, tolerances, headroom
  (`gaps_proposal.md`).

## Changes in v4.4 (2026-10-25, signed off; `ground_study.md` G2, G3)

- **Buffered receiver** (§3, G3): U16 OPA1656, both units as followers in front of SW15, each leg biased by 1M to
  AGND (R10 on IN_T, new R112 on IN_R) and fed through 220R (R110 / R111: fault current into the input diodes, with
  C8 / C9 an RF filter). 100R build-outs R113 / R114 at the follower outputs. The common-mode input impedance rises
  from 20 kΩ to 1 MΩ per leg: against a synth's 1 kΩ output on the tip leg, CMRR 26 → 54 dB (0.1 % parts, worst 5 %).
- **Jack sleeves on CHASSIS** (§16.4, G2): J1 (line in) and J5 (direct out) sleeves, and C8 / C9, go to a CHASSIS net
  on the jack board, bonded through the two standoff holes (now plated, H1 / H2 in the schematic) to the panel. Cable
  shield currents stay out of AGND. J2 (insert, single-ended) keeps its sleeve on AGND. J1's normals (TN / RN) now
  short tip and ring to AGND with nothing plugged in, so the 1M bias doesn't hiss on an empty input.
- **Supply:** +1 OPA1656, +7.8 mA per rail typical (10 mA maximum): ~100 / 87 mA per strip (master spec §27).
- Noise: unchanged at main L (−79.2 dBu, 24 strips; the followers add ~0.1 dB to the receiver's 10K network).

## Changes in v4.3 (2026-10-24, signed off; `hpf_proposal.md` H1–H3)

- **Sweepable HPF** (§5): a state-variable (KHN) high-pass, 21–403 Hz, unity gain, non-inverting, Q 0.707, tuned by
  RV16, the mid bands' stocked Alpha A10K dual. U5A is the summer, a new U15 holds the integrators. SW11 now selects the
  source of HOUT: HP (latched, HPF in) or HIN (released, a wire). It replaces the fixed 87 Hz Sallen-Key
  (C39, C40, R48, R49 removed); mid rotation is 85 Hz.
- **C91** 33 µF MUSE ES in parallel with C38: with the HPF out, HIN feeds the EQ input directly (~2.5 kΩ). PRE's LF
  corner stays at 1.0–1.1 Hz (C38 alone: 1.9–2.1 Hz).
- **Panel** (§16.3): the right column reads Ø key (y 50), HPF IN key (y 61), HPF FREQ knob (y 76). The OL LED moves
  to (20.6, 50) between the GAIN knob and the Ø key. **CN3** moves to y ≈ 131.5 (§16.4).
- **Supply:** +1 OPA1612, ~92 / 79 mA per strip. The master's wing PTCs become MF-RX185/72 (H4, master spec v0.9).
- Cost in noise with the HPF in: +0.2 dB with EQ in, +1.4–1.9 dB with EQ bypassed; none with it out.

## Changes in v4.2 (2026-10-24, signed off; `film_np_proposal.md` F1–F4)

- **Film coupler:** C13 (fader wiper → FPIN) is a WIMA MKS2C042201K00KSSD 2.2 µF PET film (63 V), THT on the bottom
  side; it was an X7R 1206. C49 (2.2 µF film, LF band) gets the same part and moves to the bottom side: the MKS2 is
  13 mm tall, and on the top side it sat under the 11.5 mm panel gap.
- **Bipolar electrolytics:** Nichicon MUSE ES 25 V in the existing footprints:
  - C10, C38, C51, C52: 47 µF → 33 µF (UES1E330MPM, 8 × 11.5);
  - C11, C15, C16, C17: 220 µF → 100 µF (UES1E101MPM, 10 × 16).
- **LF response:** end to end (strip input to the main XLR) −3 dB at 2.3 Hz (was 1.5 Hz), −0.04 dB and +14° at 20 Hz.
  The direct out into 600 Ω is −0.53 dB at 20 Hz, flat into 10 kΩ.

## Changes in v4.1 (2026-10-23, signed off; `strip_parts_review.md`)

Op-amp stability, checked with TI's OPA161x model in the real network (`sim/review/strip/`), and part ratings:
- **EQ stages:** 10 pF C0G across both 22Ks of U6A (C69/C70) and U6B (C71/C72), 22 pF across R67 (C73, U7A). They had
  ≈ 0° phase margin (U7A −20° with an insert lead). The equal pairs leave the Delta EQ unchanged.
- **KHN summers:** 10 pF across R83 / R92 (C74 / C76) and 22 pF from each summer's + input to AGND (C75 / C77):
  2–3° → 82°. Audio cost ≤ 0.084 dB at about 12 kHz (HI-MID full cut, frequency CW).
- **Receiver:** C78 33 pF across R9, matching C7 across R7: CMRR 86 dB flat (was 60 / 40 / 34 dB at
  1 / 10 / 20 kHz), 45° → 85°.
- **Followers on 1–5 kΩ sources:** 10 pF from the + input to AGND on PANWL (C79), PANWR (C80), M2 (C81) and FPIN
  (C82); 22 pF on DIRSRC (C83). Was 18–51°.
- **OL LED:** R15 1K → 4K7 (was 14 mA through an 0805 at 160 %).
- **Insert return:** R99 1K between RET and U7B's + input (RET_IN), with C84 100 pF from RET_IN to AGND. Without
  C84 the 1K left U7B at 40° (27° with DIR on and aux 6 at the top); with it, ≥ 70°, and it is an RF filter too.
- **+5VL:** D10 BAT54W from +5VL to +VA: VL stays within 0.3 V of V+ at power-down too.
- **BOM:**
  - MPNs: OPA1612AIDR, LM393BIDR, MMBFJ112 (value), Kingbright LEDs, the bus header.
  - Ceramics X7R 50 V (100n, 1u, 2.2u by MPN; C0G parts 50 V).
  - Anti-surge R1/R2 and R11/R71.
  - BOM export with a DNP column.
- **Spec notes:** routing rule for long op-amp output nets (16.3), J112 headroom (§9), no phantom on the insert
  send or direct out (§7, §11).

All stages ≥ 72° phase margin in the nominal state with the TI model (§17).

## 0. Changes from v3.1

Decided 2026-10-22 (reverses the earlier "no EQ, no trim"):
- **Ø switch** (SW15) and a **gain stage**, −15 … +15 dB, 0 dB at the centre detent (U1B, RV9).
- **HPF**, 2-pole, switched (U5A, SW11). Unity gain; the Delta's version has +3 dB.
- **4-band EQ** with Delta values (U5B, U6A/B, U7A; RV10–RV15) and **EQ IN** switch with green
  LED (SW12, D5).
- **Insert post-EQ** (Delta position), with three solder jumpers for pre-EQ (JP5–JP7). Insert
  return buffer moves from U1B to U7B.
- **ON** switch with green LED replaces MUTE/amber (SW4, D4); same J112 soft mute.
- **PRE switch per aux pair** on the panel (SW8–SW10); the solder jumpers JP2–JP4 now choose
  the pre source: pre-fader (default) or pre-EQ.
- **Direct out** (J5 on the jack board, U8A); the **DIR** switch (SW13) turns the aux 6 pot into its level.
- **PAN switch** (SW14): off sends the unpanned post-fader signal to the subgroups.
- Four more OPA1612 (U5–U8): seven in all.

Not changed: receiver, motherloom pinout, ground cancel, logic supply, soft mute circuit, fader
and +10 dB post-amp, VCA option, pan buffers, 4K7 routing with grounded off-position,
0 dBu internal level.

---

## 1. Signal flow

```
J1 line in ─ SW15 Ø ─ U1A receiver (unity, inverting) ─ U1B gain (−15…+15 dB, inverting) ─ C38 ─ HIN
 ─ HPF U5A + U15, RV16 21–403 Hz (SW11: HP or HIN) ─ HOUT ─── pre-EQ tap (aux jumpers, JP5/JP6)
 ─ JP6 ─ EQIN ─ U5B HF ─ U6A HI-MID ─ U6B LO-MID ─ U7A LF ─┐
                         └──────────── SW12 EQ IN: EQ out or EQIN ┘─ C51 ─ EQOUT
 ─ JP5 ─ R11 75R ─ J2 insert send / return (normalled) ─ U7B buffer ─ BUF1
 ─ JP7 ─ PRESRC ─ C11 ─ PRE ─┬─ OL detector (U4A, from PRESRC)
                             ├─ PFL (SW3, 22K) ── bus 27, PFL DET bus 29
                             └─ soft mute (Q1/Q2, SW4 ON) ─ U3B ─ MUTEOUT ─┬─ aux pre-fader tap (JP2–JP4; v4.6)
                                                                           └─ fader RV1 ─ [VCA option] ─ U2A +10 dB
                                 ─ C15 ─ POST ─┬─ aux post tap (SW8–SW10 unlatched)
                                               ├─ pan RV8 ─ U8B / U3A buffers ─ C16/C17 ─ PANL / PANR
                                               │    ├─ SW5 L-R ─ R26/R27 4K7 ─ MIX L/R
                                               │    └─ SW14 PAN ─ SUBSRC_L/R ─ SW6/SW7 ─ R28–R31 ─ SUB 1–4
                                               └─ (SW14 unlatched: SUBSRC_L/R = POST)
 aux 1-6: RV2–RV7 (10K A) ─ 22K ─ AUX buses; SW13 DIR: RV7 wiper ─ U8A ─ J5 direct out
```

Polarity: receiver and gain stage both invert; the HPF, the EQ (four inverting stages, or the
bypass), the insert buffer and the rest are non-inverting. Tip is hot, PRE is in phase with the
tip (simulated −0.6° at 1 kHz). The master's summing amps invert once more; the master
re-inverts.

Switch convention throughout: PVA2 pin 2 (and 5) is common; **latched = 2–1 (5–4)**,
unlatched = 2–3 (5–6). The latched throw still needs confirming on a real PVA2 (§16.1).

---

## 2. Power, grounding, bus connection

### 2.1 Audio rails (bus pins 30–34)
```
+V (pins 32–34) ── R1 10 Ω ── +VA ── C1 220 µF/25 V ── C2 100 nF ── AGND
−V (pins 30, 31) ── R2 10 Ω ── −VA ── C3 220 µF/25 V ── C4 100 nF ── AGND
```
100 nF at every op-amp: C20/C21 (U1), C22/C23 (U2), C24/C25 (U3), C29/C30 (U5), C31/C32 (U6),
C33/C34 (U7), C35/C36 (U8), C63–C68 (U12–U14), C89/C90 (U15), C92/C93 (U16). +V arrives on bus pins 32–34 (pin 34, the
Delta's +48 V, is a third +V conductor since 2026-10-25, `wing_power_proposal.md` W1).

### 2.2 Logic rails (ED3344B)
```
+V ── R3 10 Ω ── +VL ── C5 47 µF ── LGND        −V ── R4 10 Ω ── −VL ── C6 47 µF ── LGND
```
Feeds the LEDs (including the routing LEDs, §13), the mute gate drive, PFL DET and the OL comparator
(U4, C26). The DG413s' 5 V logic supply (+5VL) is taken from +VA instead, so VL never exceeds V+ at power-up;
D10 BAT54W keeps it within 0.3 V of V+ at power-down (§13).

### 2.3 Grounds
- AGND pour and a separate LGND pour, joined at one point: NT1, beside the spade.
- CN4: ¼" (6.3 mm) spade, one 14 AWG wire tied under the motherloom to its wing's bar at the master's star
  (`ground_study.md` G1, master spec §26).
- CHASSIS exists only on the jack board (jack sleeves J1 / J5, C8 / C9, plated standoff holes to the panel); it meets
  AGND only at the master's star (§16.4).
- Ground cancel: R5 10 Ω from AGND to bus pin 26 (ED3344C R141).
- Bus even pins 2–16: AGND.

### 2.4 Bus header
CN1: one 34-pin shrouded keyed header per strip, crimped IDC socket on a daisy-chained ribbon
(Delta ED3344C CN2). Spare pins 1, 3, 5, 7, 19 and 28 (PFL−) not connected; pin 34 (+48 V on the Delta) is +V (W1).

| Pin | Signal | Driven on this strip by |
|-----|--------|-------------------------|
| 9, 11 | SUB 4, SUB 3 | R31, R30 4K7 via SW7 (from SUBSRC_R / _L) |
| 13, 15 | SUB 2, SUB 1 | R29, R28 4K7 via SW6 (from SUBSRC_R / _L) |
| 17, 18 | MIX R, MIX L | R27, R26 4K7 via SW5 (from PANR / PANL) |
| 24, 25, 23, 22, 21 | AUX 1, 2, 3, 4, 5 | R20–R24 22K from the wipers of RV2–RV6 |
| 20 | AUX 6 | R25 22K from RV7 via SW13 (grounded when DIR is latched) |
| 26 | GND CANCEL | R5 10 Ω to AGND |
| 27 | PFL | R32 22K via SW3 |
| 29 | PFL DET | R33 100K via SW3 |
| 30–31, 32–34 | −V, +V | power entry |

---

## 3. Line input and Ø (U1A, SW15)

```
J1 tip  ─┬─ C8 100 pF to CHASSIS (jack board) ── ribbon pin 1 ── IN_T: R10 1M to AGND ── R110 220R ─┬─ U16A (+)
J1 ring ─┴─ C9 100 pF to CHASSIS (jack board) ── ribbon pin 2 ── IN_R: R112 1M to AGND ── R111 220R ─┼─ U16B (+)
                                                                       C94 / C95 100 pF C0G to AGND at the + inputs ┘
U16A, U16B (OPA1656) followers ── R113 / R114 100R ── BUF_T / BUF_R
SW15 pole A: INV_IN  = BUF_T (unlatched) or BUF_R (latched, Ø)   ── R6 10K ── U1A (−) ── R7 10K ── RECV
SW15 pole B: NINV_IN = BUF_R (unlatched) or BUF_T (latched, Ø)   ── R8 10K ── U1A (+) ── R9 10K ── AGND
C7 33 pF across R7; C78 33 pF across R9 (v4.1: balances the bridge, CMRR 86 dB flat, 85° phase margin)
```
- Buffered ground-compensated receiver, unity gain, **inverting** (tip to the inverting leg) so the
  inverting gain stage after it restores polarity. R6–R9 0.1 % (or a matched network).
- v4.4 (`ground_study.md` G3): the followers give each leg 1 MΩ to AGND in common mode (20 kΩ before), so a
  synth's output impedance no longer unbalances the bridge: CMRR 54 dB against a 1 kΩ source (worst 5 % of 0.1 %
  parts), 59 dB from the resistors alone.
- Follower stability, on the fitted OPA1656 model (which reads 11–14° below the datasheet):
  - ≥ 48.5° for any load capacitance thanks to the 100R build-outs (`sim/review/ground/follower_stab.py`);
  - 54.1° over the strip deck's states.
- C94 / C95 matter. Without them the 220R and the OPA1656's 9.1 pF input capacitance cost about 13°: 41° and 3.3 dB
  closed-loop peaking, found with the group's returns (2026-10-25). `tools/sim_netlist.py` checks −60 dBu at
  PRE for 0 dBu common mode through 1 kΩ on the tip leg.
- For ground compensation with unbalanced synths, use a pseudo-balanced cable (TRS at the
  console, ring joined to the synth's ground at the synth end, shield at both ends). A plain TS cable works as a normal
  unbalanced input, but from an earthed synth it carries the full ground-loop hum (`ground_study.md` §5).
- With nothing plugged in, J1's normals short both legs to AGND.
- Ø swaps the two legs between the followers and the 10K resistors.

---

## 4. Gain (U1B, RV9)

```
RECV ── R45 2K2 ── RV9 pin 3 (CW end)    RV9 wiper ── U1B (−);  U1B (+) ── AGND
GOUT ── R46 2K2 ── RV9 pin 1 (CCW end)   C37 22 pF from GOUT to U1B (−)
GOUT ── C38 33 µF NP ── HIN ── R47 47K to AGND
```
- Gain = (2K2 + R_wiper–pin1) / (2K2 + R_wiper–pin3): −15.0 dB fully CCW, 0 dB at the centre
  detent, +14.8 dB fully CW, symmetric in dB (≈ 2.5 dB per 10 % of rotation).
- RV9: Alpha RD901F-40-15R1-B10K-0CD (10K linear, centre detent).
- Noise at the gain-stage output, 50 Ω source: −105.2 dBu at 0 dB, −91.4 dBu at +15 dB. The
  Delta line-stage topology recalculated for the same range is 4.7 dB noisier (rejected).
- Noise at PRE with the OPA1612's input current noise (1.7 pA/√Hz) included (`tools/sim_console.py`, 2026-10-24):
  - −102.6 dBu with EQ bypassed, −92.9 dBu with EQ in, against −105.2 / −96.7 dBu from the resistors alone (the
    earlier figures).
  - Most of the current noise acts in the EQ's 22K networks and the KHN integrators.
  - A FET-input op-amp in those stages would trade it for higher voltage noise; not evaluated yet.

---

## 5. HPF (U5A, U15, RV16, SW11) — sweepable, v4.3

```
HIN ─ R100 4K99 ─┬─ U5A (+)   (H_SP: C85 22p to AGND)
H_BP ─ R101 2K49 ┘
H_LP ─ R102 2K49 ─┬─ U5A (−)  U5A out = HP;  R103 4K99 ∥ C86 10p from HP to (−)
HP ─ RV16A pin 3 (pin 1 ─ R104 330R ─ AGND; R105 13K pin 3 → wiper) ─ wiper ─ R106 5K6 ─ U15A (−); C87 100n to H_BP
H_BP ─ RV16B pin 6 (pin 4 ─ R107 330R ─ AGND; R108 13K pin 6 → wiper) ─ wiper ─ R109 5K6 ─ U15B (−); C88 100n to H_LP
U15A / U15B (+) = AGND
SW11 pole A: common HOUT; latched = HP (HPF in), released = HIN (HPF out)
```
- State-variable (KHN) high-pass: RF = 2 RLP and RIN = 2 RBP give unity gain, non-inverting, Q = 1/√2 (Butterworth,
  12 dB/oct, no peaking). Tuned as the mid bands (§6.2): each gang is a divider (330R here, for a 19:1 range) into an
  integrator's virtual earth. CW = higher.
- −3 dB at the 11 dial positions: 21, 37, 51, 64, 75, 85, 132, 171, 216, 280, 403 Hz (`sim/review/hpf/khn_hpf.py
  law`; the netlist gives 21.2 / 85.9 / 406 Hz). Gang mismatch ±20 %: ≤ 0.09 dB peaking, corner unchanged.
- No internal node exceeds the input (BP / LP −6 dB, summer inputs −9.6 dB): no headroom cost.
- C85 / C86 are stability parts: without them the summer has 6.6° (TI OPA161x), with them 84°.
- With the HPF out SW11 connects HIN straight to HOUT: no added noise. HIN then drives the EQ input; C91 doubles C38
  for that (§1, v4.3). The DC step at switching is ≤ 0.9 mV (CCW, typical Vos / Ib), as HIN follows HP's DC through
  the summer's input network.
- Was a unity-gain Sallen-Key at 87 Hz (C39/C40 47n, R48 27K, R49 56K, U5A follower). The Delta's (ED3344A IC3A) has
  +3 dB of passband gain, which our 0 dBu structure doesn't want.
- C85–C88: C0G 1206. HOUT is also the pre-EQ tap.

---

## 6. EQ (ED3344A, ED3151) and EQ IN

Four cascaded unity-gain inverting stages; each band's 10K B centre-detent gain pot spans its
stage's input and output; **clockwise boosts** on every band (as the ED3151 CW arrows).

| Band | Stage | Circuit (values as the Delta) | Pots |
|------|-------|-------------------------------|------|
| HF shelf | U5B | R50 33K in, R51 33K ∥ C41 33 pF feedback; wiper ─ C42 4n7 ─ T1 (R52 5K6 to AGND) ─ C43 4n7 ─ R53 6K8 ─ virtual earth | RV10 gain: pin 3 = EQIN, pin 1 = U5B out |
| HI-MID | U6A | R54 22K in, R55 22K feedback, C69/C70 10 pF across both (v4.1, stability); (+) input = band-pass of the gain-pot wiper. Delta: Wien network with a 100K C-law dual. **Here: KHN state-variable band-pass, same response (§6.2), U12A/U12B/U13A** | RV11 gain: pin 3 = U6A out; RV12 frequency: **10K A-law dual** |
| LO-MID | U6B | R58/R59 22K, C71/C72 10 pF across both (v4.1); (+) input as HI-MID, KHN on U13B/U14A/U14B | RV13 gain: pin 3 = U6B out; RV14 frequency: 10K A-law dual |
| LF bell | U7A | R66/R67 22K, C73 22 pF across R67 (v4.1); (+) input: wiper ─ R64 1K5 ─ C49 2µ2 ─ (C50 100 nF ∥ R65 5K1 to AGND) | RV15 gain between R62 3K3 (from U6B) and R63 3K3 (to U7A out), C48 150 nF across it |

- The Delta's R32/R36 meet the stage-input line on ED3344A without a junction dot. They cross
  rather than connect, and run from the rheostat to ground. Simulation confirms the reading.
- Simulated with the Delta's Wien mid bands (`sim/delta_eq.cir`); the KHN mid bands give the same
  response (§6.2), and the whole schematic is checked by `tools/sim_netlist.py`:
  HF ±11.5 dB at 12 kHz; HI-MID ±14.6 dB, 670 Hz–10.5 kHz, Q 1.44; LO-MID ±14.7 dB,
  148 Hz–2.3 kHz, Q 1.44; LF ±14.3 dB at 54 Hz, Q 0.88; flat within 0.16 dB and in phase with
  all pots centred.
- Capacitors: C0G 1206 up to 100 nF; C48 150 nF and C49 2.2 µF polyester film (MKS2).
- Op-amps OPA1612. EQ noise is resistor thermal noise (op-amp choice changes it by 0.2 dB);
  the Delta impedances are kept (halving them would buy 2.4 dB).

### 6.2 Mid-band tuning: KHN band-pass with an A-law dual (2026-10-22)

**Why.** The Delta tunes each mid band with a 100K C-law (reverse-log) dual used as two rheostats in
a Wien band-pass. That pot isn't stocked as a dual anywhere mainstream (Tayda: single only; Bourns
PTD90: linear and audio only). An A-law dual can't simply replace it. Each gang is a rheostat with
f ∝ 1/R, so an A pot either sweeps backwards (CW = lower) or, using its other segment, crams the whole
range into the last part of the rotation. A passive T-network can invert the series arm, but not the
grounded shunt arm.

**What.** Each mid band's Wien network is replaced by a KHN state-variable band-pass. It is tuned by
pot dividers feeding its two integrators, so f ∝ the divider's transfer conductance, which an A-law
segment makes rise roughly exponentially clockwise. The KHN is set to the Wien's own transfer
function: peak gain 0.407, Q 0.275, in phase. So U6A/U6B and the gain pots work exactly as before.

```
gain-pot wiper ── R81 10K ──┐
LP ── R82 10K ──────────────┼── U12A (−)   U12A (+) ── R84 2K2 ── BP ;  (+) ── R85 10K ── AGND
HP (U12A out) ── R83 10K ───┘                       summer: HP = −in − LP + 2.46·BP
HP ── RV12A pin 3 ; pin 1 ── R86 430R ── AGND ; R88 13K pin 3 → wiper ; wiper ── R56 4K7 ── U12B (−), C44 2n2 to BP
BP ── RV12B pin 6 ; pin 4 ── R87 430R ── AGND ; R89 13K pin 6 → wiper ; wiper ── R57 4K7 ── U13A (−), C45 4n7 to LP
BP (U12B out) ── U6A (+)                                                  LO-MID: R90–R98, C46 10n / C47 22n, U13B/U14A/U14B
```
- Summer gains 1 (input), 1 (LP) and 0.82 × 3 = 2.46 (BP). Q of the band-pass comes from the
  integrator capacitor ratio (C1/C2 ≈ 0.46). No internal node exceeds the input; at full boost every
  KHN node stays at least 7.8 dB below the stage output, which clips first.
- Divider: 430R / 13K / 4K7 around a 10K pot, fitted to Alpha's catalogue A taper (two slopes, 15 % at
  mid-rotation). The sweep stays within 0.28 octave of a straight log line; the Delta's C-law network
  is 0.31. The top of the range is exact whatever the pot's tolerance, because the wiper sits on the
  driven end; ±20 % on the pot moves the bottom by about ±12 % (the Delta's rheostat: ±18 %).
- A10K rather than A100K: the same divider at 100K impedance was 8.6 dB (HI-MID) and 5.7 dB (LO-MID)
  noisier than the Delta network; at 10K the difference is 1.3 and 0.6 dB. Alpha RD902F-40-15R1-A10K,
  same footprint as before.
- Cost: three more OPA1612 (U12–U14), 18 resistors, C63–C68 decoupling. The Wien parts' references
  C44–C47 and R56/R57/R60/R61 are reused for the integrator capacitors and 4K7 inputs.

Stability (v4.1): C74 / C76 10 pF across R83 / R92 and C75 / C77 22 pF from the summers' + inputs (EQ_MSP /
EQ_LSP) to AGND. Without them the summers had 2–3° of phase margin; a feedback cap alone tops out near 55°
because the 1.8 kΩ + node lags through the input capacitance.

`sim/mid_tuning.py` (both versions in the same U6A stage, Alpha 15 % tapers, OPA1612 with noise):

| | Delta Wien, C100K | KHN, A10K | Ideal log |
|---|---|---|---|
| HI-MID f0 at 0 / ¼ / ½ / ¾ / full rotation | 676 / 1122 / 3273 / 5012 / 10471 Hz | 684 / 1567 / 2213 / 4786 / 10471 Hz | 670 / 1333 / 2652 / 5277 / 10500 |
| HI-MID boost / cut, Q | ±14.4 … 14.7 dB, 1.40 … 1.44 | ±14.6 … 14.7 dB, 1.45 … 1.46 | |
| LO-MID f0 at 0 / ½ / full | 150 / 724 / 2317 Hz | 148 / 479 / 2291 Hz | 148 / 586 / 2320 |
| LO-MID boost / cut, Q | ±14.5 … 14.7 dB, 1.41 … 1.45 | ±14.6 dB, 1.42 … 1.44 | |
| Flat (gain pots centred) | 0.00 dB | 0.00 dB | |
| Stage output noise, flat, 20 Hz–20 kHz (HI / LO) | −101.8 / −104.5 dBu | −100.5 / −103.9 dBu | |

### 6.1 EQ IN (SW12, D5)
```
SW12 pole A: EQSEL = U7A out (latched, EQ in) or EQIN (unlatched, bypass)
EQSEL ── C51 33 µF NP ── EQOUT ── R68 47K to AGND
SW12 pole B: +VL to EQ_ON when latched ── R69 4K7 ── D5 green ── LGND
```
The bypass takes the EQ's own input, so it works in both insert positions.

---

## 7. Insert and its position (U7B, JP5–JP7)

```
JP5: INS_SRC = EQOUT (1-2, default) or HOUT (2-3)      ── R11 75R ── J2 tip (send)
J2 ring (return) normalled to tip with no plug ── C10 33 µF NP ── RET (R12 47K to AGND) ── R99 1K ── RET_IN (C84 100 pF) ── U7B follower ── BUF1
JP6: EQIN   = HOUT (1-2, default) or BUF1 (2-3)
JP7: PRESRC = BUF1 (1-2, default) or EQOUT (2-3)       ── C11 100 µF NP ── PRE ── R13 47K
```
- All three on 1-2 (as supplied, bridged): insert **post-EQ**, the Delta default.
- All three on 2-3: insert **pre-EQ** (HPF → insert → EQ → PRE).
- Never mix positions: cut and bridge all three together.

---

## 8. Pre-fade section

### 8.1 OL detector and signal LED (U4, U17, logic rails)
From PRESRC (always the signal entering PRE: post-EQ, post-insert): R39 1K, D1 1N4148,
C12 100 nF (v4.5, was 1 µF), R14 470K; U4A compares against R40/R41 for ≈ +18 dBu.
- **v4.5 hold:** U4A's output discharges OL_HOLD (R115 1M to +VL, C97 220 nF to LGND). U4B (+ = OL_HOLD,
  − = VREF) drives the red OL LED D2 via R15 4K7, so the LED stays lit ≈ 150 ms after the last overload (K3).
- **LED current:** ≈ 3 mA, as the other LEDs (v4.1; R15 was 1K, 14 mA in an 0805).
- **Common-mode range:** OL_HOLD rests at +VL, above the LM393's common-mode range, while U4B's − input (VREF) stays
  inside it; the datasheet allows that for a correct output.
- **v4.7 signal LED and drive (MET1):** D2 is a red / green bicolour (WP3VEGW, pin 1 red anode, pin 2 common cathode
  to GNDD, pin 3 green anode).
  - **Red drive:** U4B now pulls Q3's base (R116 47K, R117 47K pull-up; MMBT3906), and Q3 feeds the red anode through
    R15.
  - **Signal detector:** U17A compares SIG_IN (PRESRC through R118 47K, clamped at −0.2 V by D11 BAT54W) against
    VTH 0.111 V, the −20 dBu peak (R119 750K / R120 10K from VREF). It discharges SIG_HOLD (R121 1M, C99 220 nF).
  - **Green drive:** U17B (+ = SIG_HOLD, − = VREF) pulls Q4's base (R122 / R123 47K), and Q4 feeds the green anode
    through R124 4K7.
  - **Gate:** Q5 (PNP, base from U4B's output OL_K through R125 47K) holds Q4's base at +VL while the red is lit.
  - **Sim** (`sim/review/gaps/ol.py`): green from −19.5 dBu, 170 ms hold; 3.2 mA per colour; nothing lit in silence.

### 8.2 PFL (SW3, D3)
```
PRE ── C96 2.2 µF film ── R32 22K ── SW3 pole A ── bus 27 (latched) or AGND (unlatched)   (C96: v4.5, K1)
+VL ── SW3 pole B ── PFL_ON ── R33 100K ── bus 29 (PFL DET);  R34 4K7 ── D3 red ── LGND
```

---

## 9. ON and soft mute (ED3344B/C)

```
PRE ── R16 4K7 ── M1 ── Q1 J112 to AGND ── R17 4K7 ── M2 (C81 10 pF) ── Q2 J112 to AGND ── U3B follower ── MUTEOUT
SW4 pole A: MSW = −VL (latched, ON) or LGND (unlatched, muted) ── R42 220K ── MGATE ── C28 100 nF
SW4 pole B: +VL to ON_SW when latched ── R43 4K7 ── D4 green ── LGND
```
- Latched = channel on: gates at −VL, JFETs off. Unlatched = muted: gates at 0 V, ≈ 86 dB of
  attenuation, ≈ 20 ms ramp (R42/C28).
- Headroom (v4.1 note): while ON the gates sit at −VL, about 1 V below PRE's most negative excursion. A J112 at the
  worst-case VGS(off) of −5 V starts conducting on negative peaks above about +20.7 dBu (+22.9 dBu with typical
  parts); VDG reaches 32.5 V of 35 V. Selecting J112s with |VGS(off)| ≤ 3 V raises the onset to about +22 dBu.
- Q1/Q2 are the SOT-23 MMBFJ112 (J112 is the TO-92 part).

---

## 10. Fader, post-amp, VCA option

```
MUTEOUT ── RV1 fader top (pin 3), pin 1 AGND ── wiper ── C13 2.2 µF film ── JP1 (VCA bypass) ── FPIN ── R18 100K, C82 10 pF
U2A: (+) FPIN, R19 4K7 ∥ C14 100 pF feedback, R38 2K2 to AGND: +10 dB ── C15 100 µF NP ── POST ── R35 47K
```
- The fader's "0" mark sits 10 dB below the top. Omit R38 for unity at the top.
- C82 (v4.1): the fader wiper (up to 2.5 kΩ) against the op-amp's input capacitance left U2A at 40°; 10 pF to AGND
  gives 73°. Not above 22 pF: with the fader at the top it loads U3B's output.
- VCA option (DNP): J3 1×6 socket for an SSI2162 plug-in module across C13 → FPIN (in, out,
  control, +VA, AGND, −VA), J4 control input, R44 100K pull-down; JP1 bridged when no module.

---

## 11. Aux sends, PRE switches, DIR and direct out

```
JP2/JP3/JP4 (pairs 1-2, 3-4, 5-6): PSRCn = MUTEOUT (1-2, default, pre-fader after ON; v4.6) or HOUT (2-3, pre-EQ, not muted by ON)
SW8/SW9/SW10 pole A: SRCn = PSRCn (latched, PRE) or POST (unlatched)
RV2…RV7 10K A: pin 3 = SRCn, pin 1 = AGND, wiper ── R20…R24 22K ── AUX 1…5
RV7 wiper ── SW13 pole A ── A6R (unlatched) ── R25 22K ── AUX 6
                         └─ DIRSRC (latched, DIR) ── R70 100K to AGND, C83 22 pF ── U8A follower ── DOUT
SW13 pole B: A6R to AGND when latched (no floating resistor on the aux 6 bus)
DOUT ── R71 75R ── C52 33 µF NP ── J5 tip ── R72 47K to AGND;   J5 ring ── R73 75R ── AGND
```
- Direct out: impedance-balanced TRS, level = aux 6 pot, source = the aux 5/6 PRE selection.
  0 dBu at the jack with the pot fully up. U8B is pan buffer L since v4.8 (§12).
- C83 22 pF (v4.1): with DIR on and a short lead, U8A was down to 19–21°; with it, 70°. Not more: it loads U7B (PRE)
  when aux 6 is at the top.
- No phantom: neither the direct out nor the insert send may feed a phantom-powered input (a TRS-to-XLR lead into a
  mic preamp). C52 and C51 (33 µF NP 25 V) would see about 42 V.
- SW8–SW10 pole B unused.

---

## 12. Pan, pan buffers, PAN switch

```
POST ── RV8 (10K B dual, centre detent: ALPS RK09L1240015) ── wipers (C79 / C80 10 pF) ── U8B / U3A followers ── C16 / C17 100 µF NP ── PANL / PANR (R36/R37 47K)
SW14 pole A: SUBSRC_L = PANL (latched, PAN) or POST (unlatched)
SW14 pole B: SUBSRC_R = PANR (latched)       or POST (unlatched)
```
- MIX is always panned (−6 dB at centre with the linear pot). With PAN off the subgroups get the
  unpanned post-fader signal at full level: the Delta's behaviour (ED3151 "post pan switch"),
  for using a subgroup pair as two mono groups.
- Why the buffers: unbuffered, the routing load moves the pan law by up to 5 dB (v3 analysis,
  unchanged).

---

## 13. Routing matrix

Each assign moves the far end of its 4K7 resistor between the bus (assigned) and AGND (off), so the
load on the source never changes (ED3151, ED3344C). The moving is done by a **DG413** CMOS switch
right at the bus header. The PVA2 on the panel only carries logic: pole A drives the DG413 inputs,
pole B the routing LED (decided 2026-10-22, option b in `strip_panel_study.md`).

```
PANL ── R26 4K7 ── RT_R26 ═╤═ U9 SW1 (NO) ── MIX L (pin 18)      IN1 = IN2 = RTE_LR
                           ╘═ U9 SW2 (NC) ── AGND
PANR ── R27 4K7 ── RT_R27 ═╤═ U9 SW4 (NO) ── MIX R (pin 17)      IN3 = IN4 = RTE_LR
                           ╘═ U9 SW3 (NC) ── AGND
SW5 pole A: RTE_LR = +5VL (latched) or LGND (unlatched); R74 100K to LGND holds it low in the break
SW5 pole B: +VL (latched) ── R75 4K7 ── D6 yellow LED ── LGND
```

| Switch | DG413 | Left (SW1 NO / SW2 NC) | Right (SW4 NO / SW3 NC) | IN pull-down | LED |
|--------|-------|------------------------|-------------------------|--------------|-----|
| SW5 L-R | U9 | PANL ─ R26 ─ MIX L (18) | PANR ─ R27 ─ MIX R (17) | R74 | R75, D6 |
| SW6 1-2 | U10 | SUBSRC_L ─ R28 ─ SUB 1 (15) | SUBSRC_R ─ R29 ─ SUB 2 (13) | R76 | R77, D7 |
| SW7 3-4 | U11 | SUBSRC_L ─ R30 ─ SUB 3 (11) | SUBSRC_R ─ R31 ─ SUB 4 (9) | R78 | R79, D8 |

- **Pin use.** In each SPDT the S pins are the common (the 4K7 end), D goes to the bus or AGND. Charge
  injection into D at 0 V is about 0–5 pC, into S about 30 pC (Vishay curves), so the bus gets the
  small one.
- **Supplies.** V+ = +VA, V− = −VA (C53/C54, C56/C57, C59/C60, 100 nF to AGND), GND = LGND.
  VL = +5VL: R80 4K7 from +VA, D9 BZX84C5V1, C62 1 µF, plus 100 nF per IC (C55, C58, C61).
  +5VL comes from +VA, not +VL, so VL can never exceed V+ (abs max V+ + 0.3 V) during power-up. At power-down
  +5VL would lag a falling +VA by 1.3–1.5 V; D10 BAT54W (anode +5VL, cathode +VA) holds it within 0.3 V (v4.1).
  About 2.4 mA from +VA, DC only.
- **Why the bus end.** Both switch terminals sit at the virtual earth (assigned) or ground (off), so
  the switch never sees more than I × Ron ≈ 60 mV even at +20 dBu, and its Ron-versus-voltage curve
  can't add distortion.
- **DG413, not DG403.** Same Siliconix family and function: two NO plus two NC, so the two SPDTs
  come from pairing them, with IN pins tied in pairs. Its advantages: a KiCad library symbol and
  SOIC-16 footprint; Vishay, ADI/Maxim and Renesas make it; Ron 25 Ω typical.

**Simulation (`sim/routing_switch.cir`, Vishay DG413 data, OPA1612 two-pole model, Rf 4K7 ∥ 100 pF).**
The 4K7 resistor tolerance (1 %, ±0.09 dB) is larger than the switch's level effect.

| Check | Result |
|-------|--------|
| Level vs. ideal switch, Ron 17 / 25 / 35 / 45 Ω | −0.03 / −0.05 / −0.06 / −0.08 dB (same on every channel) |
| THD at +20 dBu, 1 and 10 kHz, Ron(V) curvature 2 × the datasheet curve | −124 dB (6 × 10⁻⁵ %); the same switch at the source end of the 4K7: −67 dB |
| Summing-amp stability, bus capacitance 130 pF / 1.1 nF / 2.2 nF (24 strips × 44 pF + ribbon ≈ 1.1 nF) | no peaking; −3 dB at 283 / 300 / 321 kHz |
| Click on switching, 20 kHz band | −55 dBu peak (5 pC, bus on D); −39.5 dBu if the bus were on S (30 pC) |
| Crosstalk from one unassigned strip into the bus | −137 dB at 1 kHz, −111 dB at 20 kHz (24 strips, same signal: −84 dB at 20 kHz) |

Leakage: 24 × 0.25 nA (25 °C max) × 4K7 = 28 µV DC at the summing amp; 0.6 mV at 85 °C. The
PVA2's contact bounce now toggles the DG413 for a few ms, just as it used to chatter the audio
directly; no debounce RC, because the DG413 inputs have no hysteresis.

---

## 14. IC summary

| Ref | Part | A | B |
|-----|------|---|---|
| U1 | OPA1612 | receiver | gain stage |
| U16 | OPA1656 | input follower, tip | input follower, ring |
| U2 | OPA1612 | fader post-amp | spare, tied off (v4.8) |
| U3 | OPA1612 | pan buffer R | mute output buffer |
| U4 | LM393 | OL comparator | OL hold (v4.5) |
| U17 | LM393 | signal comparator (v4.7) | signal hold |
| U5 | OPA1612 | HPF summer | EQ HF |
| U6 | OPA1612 | EQ HI-MID | EQ LO-MID |
| U7 | OPA1612 | EQ LF | insert return buffer |
| U8 | OPA1612 | direct out | pan buffer L (v4.8) |
| U9–U11 | DG413 | routing switches L-R, 1-2, 3-4 (two SPDT each) | |
| U12 | OPA1612 | HI-MID KHN summer | HI-MID integrator 1 (BP) |
| U13 | OPA1612 | HI-MID integrator 2 (LP) | LO-MID KHN summer |
| U14 | OPA1612 | LO-MID integrator 1 (BP) | LO-MID integrator 2 (LP) |
| U15 | OPA1612 | HPF integrator 1 (BP) | HPF integrator 2 (LP) |
| Q1, Q2 | MMBFJ112 (J112 in SOT-23) | soft mute | |
| Q3–Q5 | MMBT3906 | red / green LED switches, green gate (v4.7) | |

---

## 15. Bill of materials

`channel_strip_BOM.csv` (main board, exported from the schematic, with a DNP column): 265 parts per channel, of which
three are the DNP VCA-option parts (J3, J4, R44), so 262 fitted (the netlist's 273 also counts the solder jumpers
JP1–JP7 and the net tie NT1, which aren't bought); `jack_board_BOM.csv`: 6. Panel parts per channel:
16 pots (fader, 6 aux, pan, gain, 4 EQ gain, 2 dual EQ frequency, dual HPF frequency), 13 switches, 7 LEDs (OL / signal bicolour, PFL,
ON, EQ, 3 routing), 3 jacks, 1 bus header.

BOM rules (v4.1):
- every ceramic ≥ 25 V, 50 V preferred: 100n Samsung CL21B104KBCNNNC (X7R 50 V 0805), C62 1 µF Murata
  GRM21BR71H105KA12, C0G parts 50 V; no X7R in the signal path (v4.2);
- film: C13 and C49 WIMA MKS2C042201K00KSSD (2.2 µF PET 63 V, 7.2 × 13 × 7.2, bottom side), C48 150 nF MKS2;
- bipolar electrolytics: Nichicon MUSE ES 25 V, UES1E330MPM (33 µF; C38 + C91 in parallel) and UES1E101MPM (100 µF);
- OPA1612AIDR, OPA1656IDR (U16), LM393BIDR (the same comparator as the master), onsemi MMBFJ112;
- Kingbright WP710A10ID red, WP710A10GD green, WP710A10YD yellow; D2 WP3VEGW red / green (v4.7, own footprint
  `goa-console:LED_D3.0mm-3_P2.00mm`, leads at 2.0 mm); Q3–Q5 onsemi MMBT3906LT1G;
- Panasonic ERJ-P06J100V (R1/R2, 10R at up to 0.126 W) and ERJ-P06J750V (R11/R71, ~0.25 W into a shorted lead);
- Würth 61203421621 bus header.

Still open: the pots' full order codes (shaft and bushing). RV8 (pan) is the ALPS RK09L1240015 (decided 2026-10-25).

---

## 16. PCB layout notes

AI scope: component placement only. Ruslan routes copper and pours grounds in KiCad.

- 2-layer board, AGND pour on the bottom, separate LGND pour; join at NT1 beside the spade.
- Keep the bus resistors (R20–R31) next to CN1: their bus ends are virtual-earth nodes.
- Keep the receiver resistors symmetrical and close to U1; keep the EQ's 22K/33K and Wien
  networks compact around U5/U6/U7 (high impedance: up to ≈ 107K in the mid networks).
- LED and logic traces on LGND, away from the audio path.

### 16.1 Panel parts

| Ref | Part | Footprint | Notes |
|-----|------|-----------|-------|
| J1, J2, J5 | Neutrik NJ6FD-V | `Connector_Audio:Jack_6.35mm_Neutrik_NJ6FD-V_Vertical` | On the panel, **on the jack board** (§16.4): a 1/4" plug goes ~30 mm deep, too deep for the main board's 11.5 mm gap. All plastic, isolated; panel hole 12 mm, panel 1.2–1.5 mm. |
| RV1 | Bourns PTB0143-2010BPA103 | `goa-console:Potentiometer_Bourns_PTB0143_Slide_100mm` | 100 mm, A10K; pin 1 (ground end) to the operator. BP lever: 8.0 × 1.3 mm flat blade, 10 mm above the cover (5.0 mm above the panel). Cap: Sifam LK110 with tang 01 (8.0 × 1.2, socket 4.0 deep, so it sits 1.0 mm above the panel; 26 along the travel × 11.6 × 10), the Delta's own "SIF low profile" fader knob: RS 281-7197 (black), coloured from pot4audio / D&R; try two on a real blade first (the BP thickness is not dimensioned, the socket is 1.2). The AP 4 mm-fork audio codes are not sold (factory order, MOQ ~800), and no stocked 100 mm A10K fader with a 4 mm lever exists (2026-10-23, `panel_parts_drawings.md`). |
| RV2–RV7 | Alpha RD901F-40, A10K | `Potentiometer_THT:Potentiometer_Alpha_RD901F-40-00D_Single_Vertical` | Pin 1 = AGND (A-law runs from pin 1). |
| RV9–RV11, RV13, RV15 | Alpha RD901F-40-15R1-B10K-0CD | same | 10K linear, centre detent (Alpha spec SP26020021). In stock 2026-10-22 as Alpha 9 mm vertical linear "centre notch" 10K (Cedist / Amplified Parts R-VAV-B10K-CN), but with a 1/4" (6.35 mm) shaft: knobs must match. |
| RV8 | ALPS RK09L1240015 (10K 1B dual, centre detent) | `Potentiometer_THT:Potentiometer_Alps_RK09L_Double_Vertical` | The vertical dual centre-detent 10K B that is stocked (Mouser, Verical; no Alpha one exists). ALPS catalogue RV01 Drawing No.7: **M9 × 0.75** bushing 5 long, **Ø6 shaft with a flat** (4.5 across, 7 long) 15 from the face, face 10 above the board like the Alpha, snap-in legs. Panel hole **Ø9.5**; the knob is the **6 mm D** version of the strip's knob; M9 nut (not dimensioned: assumed 12 AF × 2.0) and a 9.5 / 11 × 1.5 spacer washer. The footprint's pin rows sit 7.5 / 10 mm from the shaft like the Alpha's, gangs swapped (pins 4-6 nearer the shaft); shaft at (10, 2.5) from pin 1. Check on a sample: nut thickness, pin 1 at the CCW end, the detent at the electrical centre. |
| RV12, RV14 | Alpha RD902F-40-15R1-A10K dual (log) | same | Stocked (Tayda). Replaces the Delta's 100K C-law dual, which isn't stocked; works with the KHN mid-band tuning (§6.2). |
| SW3–SW15 | C&K PVA2 EE H1 1.7N V2 | `Button_Switch_THT:SW_Push_2P2T_Toggle_CK_PVA2xxH1xxxxxxV2` | DPDT push-push, 32 V / 100 mA; PV caps. Datasheet (rev. 02/2025, p. 3): common 0 is the middle pin; released 0–1, pressed/latched 0–2; terminals moulded "2 0 1" on the body. **Fit each switch with its moulded "2" pins in the square-pad column (pads 1 and 4)**, so latched = 2–1 / 5–4 as drawn. Since v4.6 a silk "2" beside pads 1/4 marks that column on every board. The footprint is symmetric under 180°, so a switch fitted the other way round works inverted. Check one sample with a meter. |
| D2–D8 | 3 mm LEDs | `LED_THT:LED_D3.0mm` | 7.6 mm spacers. D6–D8 (routing, yellow) at y 283, centred under SW5–SW7. |
| CN4 | Keystone 1287-ST | `goa-console:Keystone_1287-ST_FastOn_Tab_6.35mm` | |

**Check on samples before ordering boards:** PVA2 orientation by continuity (moulded "2" in the
pad 1/4 column gives 2–1 / 5–4 when latched); the fader pad pattern against a 1:1 print; knob fit
on the 6.35 mm centre-notch pots.

### 16.2 Panel stack (unchanged from v3.1)

Panel underside 11.5 mm above the PCB (1.5 mm aluminium). PVA2 H1 + PV cap, panel hole ø8.0.
Pots: 1.5 mm M7 spacer washer, panel hole ø7.2. Fader: 3.5 mm spacer, lever 5 mm above the
panel. 3 mm LEDs on 7.6 mm spacers. Six M3 standoffs, unplated holes. Radial electrolytics,
the bus header, the spade and the VCA socket on the bottom side.

### 16.3 Panel and placement (v4.0; routing rule v4.1)

Study: `strip_panel_study.md`. Chosen: **8 HP × 12U** Eurorack-style panel (40.3 × 514 mm) in a
custom frame with rails only at the two ends, **two pot columns** (x = 8.84 / 29.16, 2026-10-23: an even
20.32 mm pitch within a module and across the module boundary; it was x = 10 / 28, 18 mm apart, which left 3 mm
between Ø15 knobs), jacks on the panel in the same columns. Every pot turns its pins towards the module's centre
line (left column 180°, right column 0°), so no pad comes within 1.3 mm of the board edge. Knobs about Ø13 (the
Delta used 14 mm, 12.5 mm on the MID frequency pot): 7.3 mm between knobs across, 9 mm down the 22 mm rows.
One column would need ≈ 545 mm (15U).

Two boards per channel, placed by `tools/place_strip.py` in one coordinate frame (y = 0 is 11 mm below
the panel's top edge), placement only:

| Board | File | Size | Depth under the panel | Parts |
|-------|------|------|-----------------------|-------|
| Main | `channel_strip.kicad_pcb` | 38 × 400 mm, y 44–444 | 11.5 mm | 273 + 6 M3 holes (11.5 mm standoffs) |
| Jack | `jack_board.kicad_pcb` | 38 × 43 mm, y 0–43 | 24.0 mm (the NJ6FD-V body) | 6 + 2 M3 holes |

DRC with `--schematic-parity`, both boards: 0 parity issues. The main board has no violations at all;
the jack board has only 6 hole-clearance + 6 solder-mask items inside KiCad's NJ6FD-V footprint (the
SN pad sits close to the footprint's own locating peg). Plus unrouted connections. Silkscreen
references are 0.8 mm text, each placed by the script at the nearest spot clear of pads, silk, other
references, other parts' courtyards and the edge. The bus header CN1 is turned 180° (pin 1 at
y 345.6, same pin field x 31.46/34, y 305–345.6), so its pin-1 arrow stays on the board. The Ø switch moved from the jack row to the main board, right
of the gain pot. v4.3: the right column's top reads Ø key (y 50), HPF IN key SW11 (y 61, the PRE keys' 11 mm pitch),
HPF FREQ dual RV16 (y 76, beside HF); the OL LED D2 sits between the GAIN knob and the Ø key at (20.6, 50), 3.8 mm from
the knob and 3.2 mm from the key cap; since v4.7 it is the three-lead bicolour, centred on its middle lead, and its
detector and switches (U17, Q3–Q5, 17 parts) sit left of the fader at y 298–324. The HPF knob's numerals (20 50 85 170 400Hz) need a panel-print check: there
are 4.6 mm between the HPF key cap and the knob, so the key's legend names it (`panel_print.md`). U5 and U15 sit
between the HF / HI-MID and HI-MID / LO-MID rows; every HPF input network is within 13 mm of its pin. Decoupling caps sit beside their IC's supply pins (place_strip.py
`DECOUPLE`); the DG413s (U9–U11) are beside the fader just below CN1, the routing 4K7s between the fader
and CN1's pins. The old v3.1 placement is `archive/channel_strip_v3.1.kicad_pcb`, kept unchanged.

**Layers (2026-10-27, `layer_study.md`).** The main board is 4-layer: In1.Cu a solid GNDA plane, In2.Cu the supply rails and
the GNDD spine to NT1, signals on F.Cu / B.Cu; the jack board stays 2-layer. `routing_guide.md` has the layer plan.

**Stability caps at their pins (E9, 2026-10-27, `stab_caps_proposal.md`).** Every C0G cap on an op-amp input (the v4.1
stability caps) is within 6.3 mm of its pin. Nine of them sit on the bottom under their op-amp: C37, C41, C70, C71,
C75, C78, C80, C83 and C85. C84 is 5.8 mm from U7 pin 5, the nearest free spot. They move after packing (`placer.py` `moves`), because the greedy
packer otherwise re-shuffles about 90 parts into the spots they leave.

**Routing rule (v4.1, `strip_parts_review.md` §5).** Four op-amp outputs drive long nets directly; at MHz the series
220 µF caps are shorts:
- POST (U2A, 200–270 mm to the pan pot, the PRE/POST switches and the aux pots);
- MUTEOUT (U3B, about 200 mm to the fader);
- PANL / PANR (U8B / U3A; 137 / 107 mm since v4.8, the L one was 188);
- PRE (U7B, to the switches and the aux pots).

Keep each at ≤ about 22 pF: short, thin, not run over a pour for long. With the v4.1 caps the stages keep ≥ 55° up
to 47 pF, but at 100 pF they fall to about 40°. Alternatives:
- put the long run on the high-impedance side (e.g. the post-amp near the pot block, so the long net is FPIN, where
  shunt C helps a follower);
- isolate U3B from the fader with a series resistor (100R costs −0.09 dB into 10K).

The v4.1 stability caps sit beside their op-amps: feedback caps within 6.2 mm, + input caps within 9.2 mm.

### 16.4 Jack board and link

The three jacks, plus the input RF caps C8/C9 at J1, are on a separate 38 × 43 mm board
(`jack_board.kicad_sch`, written by `tools/gen.py` with the main schematic). It sits 24.0 mm
under the panel, set by the jack body (Neutrik NJ*FD-V drawing: flange front 24.00 above the PCB; see
`panel_parts_drawings.md`). The jack caps hold it on the panel, plus two M3 female-female standoffs of exactly
24.0 mm (the jacks are rigid spacers). CN5 (jack board) and
CN3 (main board) are both on the bottom side, so the ribbon runs behind both boards. Since the pots turned their pins
to the centre line (16.3), CN3 lies across the strip. Since v4.3 it sits at y ≈ 131.5, between the LO-MID and LF rows:
the HPF FREQ dual's mounting tabs closed the gap at y ≈ 85.5 it had used (every gap between two pot rows is 9.2 mm,
the boxed header needs ~10; the LF row has the EQ key on the right, 11.7 mm). CN5 on the jack board stays along y,
so the 10-way ribbon makes one 90° fold (about 136 mm long, was 90).

| Pin | Net | | Pin | Net |
|-----|-----|-|-----|-----|
| 1 | IN_T (J1 tip) | | 2 | IN_R (J1 ring) |
| 3 | GNDA | | 4 | SEND (J2 tip, and RN normal) |
| 5 | GNDA | | 6 | RET_RAW (J2 ring) |
| 7 | GNDA | | 8 | DO_T (J5 tip) |
| 9 | DO_R (J5 ring) | | 10 | GNDA |

Each pair is adjacent, and ground conductors sit between input, send, return and direct out. Since v4.4
(`ground_study.md` G2) the balanced jacks' sleeves (J1, J5) and C8 / C9 are on CHASSIS, which leaves the jack board
only through the two plated standoff holes H1 / H2 (M3 female-female standoffs, metal, to the panel; the panel bonds
to the frame and the frame to the master's CHASSIS at J1 pin 1 / the star). The insert J2's sleeve stays on AGND
through the ribbon (send and return are single-ended). Mechanical rule: bare metal (no anodising, or a star washer) at
each standoff's panel end and wherever a panel meets the frame rails. CN3/CN5: Würth 61201021621 2 × 5 box header. Cable:
10-way 1.27 mm flat ribbon with two IDC sockets (not on the BOMs).

---

## 17. Status (v4.8, 2026-10-26)

v4.8 (`pan_buffer_proposal.md` PAN1):
- **Netlist:** 851 pin entries / 0 mismatches, check_fp 290 / 0, ERC 0.
- **Simulation:** `tools/sim_netlist.py` 39/39, `tools/sim_console.py` 35/35. TI stability, 21 states
  (`sim/review/strip/results_none.json`, refreshed): every unit ≥ 59.8° (U3B with the direct out at the top, as since
  v4.6), ≤ 1.61 dB peaking.
- **Placement:** 0 DRC violations, 0 parity issues, 290 / 290 footprints linked; 8 parts moved. Report: decouplers
  3.1 / 10.0 / 14, high-Z inputs 10.4 / 258.6 / 28 (SIG_B, MET1's green-switch base line).

v4.7 (`feature_gaps.md` MET1):
- **Netlist:** 851 pin entries / 0 mismatches, check_fp 290 / 0, ERC 0.
- **Simulation:** `tools/sim_netlist.py` 39/39, `tools/sim_console.py` 32/32, `sim/review/gaps/ol.py` as in the change
  notes.
- **Placement:** 290 footprints + 6 holes, 0 DRC violations, 0 parity issues. Only the input followers' row moved,
  1 mm left, for the wider three-lead LED. Report unchanged: decouplers 3.1 / 10.0 / 12, high-Z inputs
  10.5 / 22.1 / 30.


v4.5 (`gaps_proposal.md` K1 / K3):
- **Netlist:** 806 pin entries / 0 mismatches, check_fp 273 / 0, ERC 0.
- **Simulation:** `tools/sim_netlist.py` 37/37, `tools/sim_console.py` 32/32; overload and key clicks as in the change
  notes.
- **Placement:** 273 footprints + 6 holes, 0 DRC violations, 0 parity issues. Report: decouplers 3.1 / 10.0 / 11,
  high-Z inputs 10.5 / 22.1 / 29. C96 is on the bottom at the PFL area.

v4.4 (`ground_study.md` G2 / G3):
- **Netlist:** 796 pin entries / 0 mismatches, check_fp 268 / 0, ERC 0; jack board 32 pins / 8 parts, 0 / 0 / ERC 0.
  `tools/sim_netlist.py` 37/37 (new: common mode at 50 Hz / 1 kHz through 1 kΩ on the tip leg, −60.1 / −58.7 dBu (−56.0 at 1 kHz since C94 / C95) at
  PRE); `tools/sim_console.py` 32/32 (main L noise −79.2 dBu, unchanged).
- **Placement:** 268 footprints + 6 holes, 0 DRC violations, 0 parity issues; the jack board's H1 / H2 are plated
  CHASSIS pads in the old hole positions. U16 sits by SW15 in a zone of its own placed first (77 parts moved). Report:
  decouplers 3.1 / 10.0 / 12 (C92 / C93 8.0 / 8.5 mm: no closer spot between the gain pot's and SW11's pins), high-Z
  inputs 10.9 / 22.1 / 29 (32 inputs).

v4.3 (sweepable HPF, `hpf_proposal.md` H1–H3):
- **Netlist:** 774 pin entries / 0 mismatches, check_fp 260 / 0, ERC 0; jack board unchanged. `tools/sim_netlist.py`
  35/35 (the HPF check is now −3 dB at CCW / mid / CW, 21.2 / 85.9 / 406 Hz, and no peaking at each);
  `tools/sim_console.py` 32/32.
- **Stability (TI OPA161x, full strip, HPF in at CCW / mid / CW with EQ in, mid with EQ bypassed):** U5A 84.3°,
  U15A/B ≥ 87.4°, U5B 82.6°, U1B 86.0°; peaking ≤ 0.31 dB.
- **Noise (PRE, 20 Hz–20 kHz):** HPF out −92.9 / −102.6 dBu (EQ in / bypassed, unchanged); HPF in −92.6 to −92.7 /
  −100.7 to −101.2 dBu.
- **Placement:** 260 footprints + 6 holes, 0 DRC violations, 0 parity issues. Report: decouplers 3.1 / 10.0 / 10,
  high-Z inputs 11.0 / 23.1 / 29 (30 inputs; the worst is U5B's HF network, 23.1 mm, which moved with U5A).

v4.2 (film couplers, MUSE ES bipolars):
- **Netlist:** 734 pin entries / 0 mismatches, check_fp 245 / 0, ERC 0; `tools/sim_netlist.py` 30/30;
  `tools/sim_console.py` 32/32.
- **Placement:** re-placed with C13 and C49 on the bottom side: 0 DRC violations, 0 parity issues; report unchanged
  (decouplers 3.1 / 10.0 / 11, high-Z inputs 10.4 / 19.7 / 25; C49 now 17 mm from U7 pin 3, was 21.5 mm).

v4.1:
- **Netlist:** `tools/verify.py` main 734 pin entries / 0 mismatches, `tools/check_fp.py` 245 parts / 0, ERC 0;
  jack board unchanged.
- **Netlist sims:** `tools/sim_netlist.py` 30/30, same values as v4.0 within 0.06 dB.
- **Stability:** TI OPA161x model in the full network (`sim/review/strip/`, `python3 run_all.py none`). Every op-amp
  unit, over 21 pot / switch / cable states, has ≥ 69.9° phase margin (U7B with DIR on, aux 6 at the top and a lead on
  the jacks) and ≤ 1.61 dB closed-loop peaking (U8A with a 470 pF direct-out lead). As v4.0: U6A/U6B/U7A −3 to −5°,
  U12A/U13B 2.6–2.7°, followers 18–51°.
- **Placement:** `channel_strip.kicad_pcb` re-placed: 245 footprints + 6 holes, 0 DRC violations, 0 parity
  issues. Report: decouplers 3.1 / 10.0 / 11, high-Z inputs 10.0 / 19.7 / 25.

v4.0 (2026-10-22):

- Schematic generated by `tools/gen.py` (User-size sheet, label-connected).
- `tools/verify.py`: main 697 pin entries, jack board 30; 0 mismatches, 0 stray pins, no single-pin nets.
- `tools/check_fp.py`: 227 + 6 parts, every symbol pin on a footprint pad.
- KiCad 10.0.7 ERC, `--severity-all`: 0 violations on both schematics.
- `tools/sim_netlist.py` simulates the two exported netlists joined through the ribbon (CN3↔CN5), so
  the source drives J1 and the direct out is read at J5 (30 checks, all pass): levels
  (PRE 0 dBu, POST +9.9 dBu, MIX +3.8 dBu), gain range, Ø, HPF corner, every EQ band at both
  ends, EQ bypass, mute depth, direct out, DIR muting aux 6, PRE/post aux, PAN on/off, PFL,
  routing through the DG413s (state taken from the PVA2 logic; Ron 25 Ω): SUB 4, MIX L/R off;
  the KHN mid bands at both ends and at mid-rotation (A law: Alpha two-slope 15 %).
  It found one real error during development: the new HI-MID nets had the same names as the mute
  nets (M1/M2), so the generator merged them. Fixed by prefixing the EQ nets with `EQ_`.
- Hand-written decks: `sim/gain_stage.cir`, `sim/delta_eq.cir`, `sim/strip_v4.cir`
  (results in `delta_clone_comparison.md` §6), `sim/routing_switch.cir` (§13), `sim/mid_tuning.py` (§6.2). `sim/strip.cir` is the v3.1 path.

**Pan RV8** (2026-10-25): ALPS RK09L1240015, the stocked vertical dual 10K B with a centre detent (§16.1; no Alpha one
exists; RK097121TD57 is a right-angle part). Supply current ~104 / 87 mA per strip since v4.7 (master spec §27);
PVA2 sense: settled from the datasheet, with an assembly rule (§16.1). Jack-board depth: 24.0 mm from Neutrik's
drawings (2026-10-23). The panel parts checked against their drawings, with what still needs a sample (PTB lever
style and pin side, PV cap clearance in the Ø8.0 hole, Alpha bushing thread and tab slots, 1/4" knobs on every pot):
`panel_parts_drawings.md`.

*Document version 4.6 — October 2026*
*Sources: Soundcraft Delta ED3344A/B/C, ED3151, ED2911A/B, ED2915A, ED2780*
