# Channel Strip — Component-Level Specification v4.0
## Soundcraft Delta Theatre input without the mic stage. One PCB per channel, ×24.

Bus pinout, grounding and power: `console_architecture.md`. Stage-by-stage comparison with the
Delta, the signed-off decisions and the simulations behind this version: `delta_clone_comparison.md`.
Reference designators are those of `tools/gen.py`; Delta drawing numbers are given where a
circuit comes from a Delta sheet (ED3344A/B/C = Theatre input RH board, ED3151 = LH board).

---

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
 ─ U5A HPF (SW11 in/out) ─ HOUT ──────────────────────────── pre-EQ tap (aux jumpers, JP5/JP6)
 ─ JP6 ─ EQIN ─ U5B HF ─ U6A HI-MID ─ U6B LO-MID ─ U7A LF ─┐
                         └──────────── SW12 EQ IN: EQ out or EQIN ┘─ C51 ─ EQOUT
 ─ JP5 ─ R11 75R ─ J2 insert send / return (normalled) ─ U7B buffer ─ BUF1
 ─ JP7 ─ PRESRC ─ C11 ─ PRE ─┬─ OL detector (U4A, from PRESRC)
                             ├─ PFL (SW3, 22K) ── bus 27, PFL DET bus 29
                             ├─ aux pre-fader tap (JP2–JP4)
                             └─ soft mute (Q1/Q2, SW4 ON) ─ U3B ─ fader RV1 ─ [VCA option] ─ U2A +10 dB
                                 ─ C15 ─ POST ─┬─ aux post tap (SW8–SW10 unlatched)
                                               ├─ pan RV8 ─ U2B / U3A buffers ─ C16/C17 ─ PANL / PANR
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

### 2.1 Audio rails (bus pins 30–33)
```
+V (pins 32, 33) ── R1 10 Ω ── +VA ── C1 220 µF/25 V ── C2 100 nF ── AGND
−V (pins 30, 31) ── R2 10 Ω ── −VA ── C3 220 µF/25 V ── C4 100 nF ── AGND
```
100 nF at every op-amp: C20/C21 (U1), C22/C23 (U2), C24/C25 (U3), C29/C30 (U5), C31/C32 (U6),
C33/C34 (U7), C35/C36 (U8). Bus pin 34 (+48 V): not connected.

### 2.2 Logic rails (ED3344B)
```
+V ── R3 10 Ω ── +VL ── C5 47 µF ── LGND        −V ── R4 10 Ω ── −VL ── C6 47 µF ── LGND
```
Feeds the LEDs, the mute gate drive, PFL DET and the OL comparator (U4, C26).

### 2.3 Grounds
- AGND pour and a separate LGND pour, joined at one point: NT1, beside the spade.
- CN4: ¼" (6.3 mm) spade to the main ground bar.
- Ground cancel: R5 10 Ω from AGND to bus pin 26 (ED3344C R141).
- Bus even pins 2–16: AGND.

### 2.4 Bus header
CN1: one 34-pin shrouded keyed header per strip, crimped IDC socket on a daisy-chained ribbon
(Delta ED3344C CN2). Spare pins 1, 3, 5, 7, 19, 28 (PFL−) and 34 (+48 V) not connected.

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
| 30–33 | −V, +V | power entry |

---

## 3. Line input and Ø (U1A, SW15)

```
J1 tip  ─┬─ C8 100 pF to AGND (jack board) ── ribbon pin 1 ── IN_T: R10 1M to AGND
J1 ring ─┴─ C9 100 pF to AGND (jack board) ── ribbon pin 2 ── IN_R
SW15 pole A: INV_IN  = tip (unlatched) or ring (latched, Ø)   ── R6 10K ── U1A (−) ── R7 10K ── RECV
SW15 pole B: NINV_IN = ring (unlatched) or tip (latched, Ø)   ── R8 10K ── U1A (+) ── R9 10K ── AGND
C7 33 pF across R7
```
- Ground-compensated receiver, unity gain, now **inverting** (tip to the inverting leg) so the
  inverting gain stage after it restores polarity. R6–R9 0.1 % (or a matched network).
- For ground compensation with unbalanced synths, use a pseudo-balanced cable (TRS at the
  console, ring joined to sleeve at the synth end). A plain TS cable works as a normal
  unbalanced input.
- Ø swaps the two legs before the 10K resistors.

---

## 4. Gain (U1B, RV9)

```
RECV ── R45 2K2 ── RV9 pin 3 (CW end)    RV9 wiper ── U1B (−);  U1B (+) ── AGND
GOUT ── R46 2K2 ── RV9 pin 1 (CCW end)   C37 22 pF from GOUT to U1B (−)
GOUT ── C38 47 µF NP ── HIN ── R47 47K to AGND
```
- Gain = (2K2 + R_wiper–pin1) / (2K2 + R_wiper–pin3): −15.0 dB fully CCW, 0 dB at the centre
  detent, +14.8 dB fully CW, symmetric in dB (≈ 2.5 dB per 10 % of rotation).
- RV9: Alpha RD901F-40-15R1-B10K-0CD (10K linear, centre detent).
- Noise at the gain-stage output, 50 Ω source: −105.2 dBu at 0 dB, −91.4 dBu at +15 dB. The
  Delta line-stage topology recalculated for the same range is 4.7 dB noisier (rejected).

---

## 5. HPF (U5A, SW11)

```
HIN ── C39 47 nF ── H1 ── C40 47 nF ── HP ── U5A (+);  U5A out = HOUT, follower
H1 ── R48 27K ── HOUT;   HP ── R49 56K ── AGND
SW11 pole A: HIN ─ HP when unlatched (caps shorted, HPF out); open when latched (HPF in)
```
- Unity-gain Sallen-Key Butterworth: −3 dB at 87 Hz, −10 dB at 50 Hz, 12 dB/oct, no peaking.
  The Delta's (ED3344A IC3A, 33K/39K with +3 dB gain, −3 dB at 91 Hz) has +3 dB of passband gain,
  which our 0 dBu structure doesn't want.
- C39, C40: C0G 1206. HOUT is also the pre-EQ tap.

---

## 6. EQ (ED3344A, ED3151) and EQ IN

Four cascaded unity-gain inverting stages; each band's 10K B centre-detent gain pot spans its
stage's input and output; **clockwise boosts** on every band (as the ED3151 CW arrows).

| Band | Stage | Circuit (values as the Delta) | Pots |
|------|-------|-------------------------------|------|
| HF shelf | U5B | R50 33K in, R51 33K ∥ C41 33 pF feedback; wiper ─ C42 4n7 ─ T1 (R52 5K6 to AGND) ─ C43 4n7 ─ R53 6K8 ─ virtual earth | RV10 gain: pin 3 = EQIN, pin 1 = U5B out |
| HI-MID | U6A | R54 22K in, R55 22K feedback; (+) input from the wiper through a Wien band-pass: C44 3n3 + R56 6K8 + RV12A in series, C45 1n5 ∥ (RV12B + R57 6K8) to AGND | RV11 gain: pin 3 = U6A out; RV12 frequency: 100K C-law dual, each gang a rheostat |
| LO-MID | U6B | R58/R59 22K; C46 15n + R60 6K8 + RV14A; C47 6n8 ∥ (RV14B + R61 6K8) | RV13 gain: pin 3 = U6B out; RV14 frequency |
| LF bell | U7A | R66/R67 22K; (+) input: wiper ─ R64 1K5 ─ C49 2µ2 ─ (C50 100 nF ∥ R65 5K1 to AGND) | RV15 gain between R62 3K3 (from U6B) and R63 3K3 (to U7A out), C48 150 nF across it |

- Frequency pots RV12, RV14: wiper tied to pin 1 (and 4); rheostat between wiper and pin 3 (6),
  so resistance falls clockwise and, with the C (reverse-log) law, frequency rises
  logarithmically.
- The Delta's R32/R36 meet the stage-input line on ED3344A without a junction dot. They cross
  rather than connect, and run from the rheostat to ground. Simulation confirms the reading.
- Simulated (`sim/delta_eq.cir`; whole schematic in `tools/sim_netlist.py`):
  HF ±11.5 dB at 12 kHz; HI-MID ±14.6 dB, 670 Hz–10.5 kHz, Q 1.44; LO-MID ±14.7 dB,
  148 Hz–2.3 kHz, Q 1.44; LF ±14.3 dB at 54 Hz, Q 0.88; flat within 0.16 dB and in phase with
  all pots centred.
- Capacitors: C0G 1206 up to 100 nF; C48 150 nF and C49 2.2 µF polyester film (MKS2).
- Op-amps OPA1612. EQ noise is resistor thermal noise (op-amp choice changes it by 0.2 dB);
  the Delta impedances are kept (halving them would buy 2.4 dB).

### 6.1 EQ IN (SW12, D5)
```
SW12 pole A: EQSEL = U7A out (latched, EQ in) or EQIN (unlatched, bypass)
EQSEL ── C51 47 µF NP ── EQOUT ── R68 47K to AGND
SW12 pole B: +VL to EQ_ON when latched ── R69 4K7 ── D5 green ── LGND
```
The bypass takes the EQ's own input, so it works in both insert positions.

---

## 7. Insert and its position (U7B, JP5–JP7)

```
JP5: INS_SRC = EQOUT (1-2, default) or HOUT (2-3)      ── R11 75R ── J2 tip (send)
J2 ring (return) normalled to tip with no plug ── C10 47 µF NP ── RET ── R12 47K ── U7B follower ── BUF1
JP6: EQIN   = HOUT (1-2, default) or BUF1 (2-3)
JP7: PRESRC = BUF1 (1-2, default) or EQOUT (2-3)       ── C11 220 µF NP ── PRE ── R13 47K
```
- All three on 1-2 (as supplied, bridged): insert **post-EQ**, the Delta default.
- All three on 2-3: insert **pre-EQ** (HPF → insert → EQ → PRE).
- Never mix positions: cut and bridge all three together.

---

## 8. Pre-fade section

### 8.1 OL detector (U4A, logic rails)
From PRESRC (always the signal entering PRE: post-EQ, post-insert): R39 1K, D1 1N4148,
C12 1 µF, R14 470K; comparator against R40/R41 for ≈ +18 dBu; red OL LED D2 via R15 1K.
U4B tied off.

### 8.2 PFL (SW3, D3)
```
PRE ── R32 22K ── SW3 pole A ── bus 27 (latched) or AGND (unlatched)
+VL ── SW3 pole B ── PFL_ON ── R33 100K ── bus 29 (PFL DET);  R34 4K7 ── D3 red ── LGND
```

---

## 9. ON and soft mute (ED3344B/C)

```
PRE ── R16 4K7 ── M1 ── Q1 J112 to AGND ── R17 4K7 ── M2 ── Q2 J112 to AGND ── U3B follower ── MUTEOUT
SW4 pole A: MSW = −VL (latched, ON) or LGND (unlatched, muted) ── R42 220K ── MGATE ── C28 100 nF
SW4 pole B: +VL to ON_SW when latched ── R43 4K7 ── D4 green ── LGND
```
- Latched = channel on: gates at −VL, JFETs off. Unlatched = muted: gates at 0 V, ≈ 86 dB of
  attenuation, ≈ 20 ms ramp (R42/C28).

---

## 10. Fader, post-amp, VCA option (unchanged)

```
MUTEOUT ── RV1 fader top (pin 3), pin 1 AGND ── wiper ── C13 2.2 µF ── JP1 (VCA bypass) ── FPIN ── R18 100K
U2A: (+) FPIN, R19 4K7 ∥ C14 100 pF feedback, R38 2K2 to AGND: +10 dB ── C15 220 µF NP ── POST ── R35 47K
```
- The fader's "0" mark sits 10 dB below the top. Omit R38 for unity at the top.
- VCA option (DNP): J3 1×6 socket for an SSI2162 plug-in module across C13 → FPIN (in, out,
  control, +VA, AGND, −VA), J4 control input, R44 100K pull-down; JP1 bridged when no module.

---

## 11. Aux sends, PRE switches, DIR and direct out

```
JP2/JP3/JP4 (pairs 1-2, 3-4, 5-6): PSRCn = PRE (1-2, default, pre-fader) or HOUT (2-3, pre-EQ)
SW8/SW9/SW10 pole A: SRCn = PSRCn (latched, PRE) or POST (unlatched)
RV2…RV7 10K A: pin 3 = SRCn, pin 1 = AGND, wiper ── R20…R24 22K ── AUX 1…5
RV7 wiper ── SW13 pole A ── A6R (unlatched) ── R25 22K ── AUX 6
                         └─ DIRSRC (latched, DIR) ── R70 100K to AGND ── U8A follower ── DOUT
SW13 pole B: A6R to AGND when latched (no floating resistor on the aux 6 bus)
DOUT ── R71 75R ── C52 47 µF NP ── J5 tip ── R72 47K to AGND;   J5 ring ── R73 75R ── AGND
```
- Direct out: impedance-balanced TRS, level = aux 6 pot, source = the aux 5/6 PRE selection.
  0 dBu at the jack with the pot fully up. U8B spare, tied off as a grounded follower.
- SW8–SW10 pole B unused.

---

## 12. Pan, pan buffers, PAN switch

```
POST ── RV8 (10K B dual, centre detent) ── wipers ── U2B / U3A followers ── C16 / C17 220 µF NP ── PANL / PANR (R36/R37 47K)
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

Each DPDT assign switch sends the far end of its 4K7 resistor to the bus (latched) or to AGND
(unlatched), so the load on the source never changes (ED3151, ED3344C).

| Switch | Pole A | Pole B |
|--------|--------|--------|
| SW5 L-R | PANL ─ R26 ─ MIX L (18) | PANR ─ R27 ─ MIX R (17) |
| SW6 1-2 | SUBSRC_L ─ R28 ─ SUB 1 (15) | SUBSRC_R ─ R29 ─ SUB 2 (13) |
| SW7 3-4 | SUBSRC_L ─ R30 ─ SUB 3 (11) | SUBSRC_R ─ R31 ─ SUB 4 (9) |

R26–R31: 4K7 1 % metal film (recorded decision; the master's feedback resistors are 4K7 too).

**Routing LEDs (decided, not yet drawn).** Both PVA2 poles carry audio, so an LED needs a third
pole. No vertical-action 4PDT latching switch from a known maker has turned up. The C&K PHB 4-pole
(PHB4UEE1A, body 22.5 × 7.4 mm) is right-angle: its plunger moves parallel to the PCB, 5 mm above it.
Alps SPUN/SPUJ are listed as horizontal-mount. Options are in `strip_panel_study.md`, open check 3.

---

## 14. IC summary

| Ref | Part | A | B |
|-----|------|---|---|
| U1 | OPA1612 | receiver | gain stage |
| U2 | OPA1612 | fader post-amp | pan buffer L |
| U3 | OPA1612 | pan buffer R | mute output buffer |
| U4 | LM393 | OL comparator | spare, tied off |
| U5 | OPA1612 | HPF | EQ HF |
| U6 | OPA1612 | EQ HI-MID | EQ LO-MID |
| U7 | OPA1612 | EQ LF | insert return buffer |
| U8 | OPA1612 | direct out | spare, tied off |
| Q1, Q2 | J112 | soft mute | |

---

## 15. Bill of materials

`channel_strip_BOM.csv` (exported from the schematic): 172 parts per channel, of which three are
the DNP VCA-option parts (J3, J4, R44), so 169 fitted. Panel parts per channel: 15 pots (fader, 6 aux, pan, gain, 4 EQ
gain, 2 dual EQ frequency), 13 switches, 4 LEDs (OL, PFL, ON, EQ), 3 jacks, 1 bus header.

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
| RV1 | Bourns PTB0143-2010BPA103 | `goa-console:Potentiometer_Bourns_PTB0143_Slide_100mm` | 100 mm, A10K; pin 1 (ground end) to the operator. |
| RV2–RV7 | Alpha RD901F-40, A10K | `Potentiometer_THT:Potentiometer_Alpha_RD901F-40-00D_Single_Vertical` | Pin 1 = AGND (A-law runs from pin 1). |
| RV9–RV11, RV13, RV15 | Alpha RD901F-40-15R1-B10K-0CD | same | 10K linear, centre detent (Alpha spec SP26020021). |
| RV8 | Alpha RD902F-40, B10K, centre detent | `Potentiometer_THT:Potentiometer_Alpha_RD902F-40-00D_Dual_Vertical` | Confirm a detent version is stocked. |
| RV12, RV14 | Alpha RD902F-40 dual, **100K C (reverse log)** | same | **Availability to confirm**; the Delta used 100K C-law dual. |
| SW3–SW15 | C&K PVA2 EE H1 1.7N V2 | `Button_Switch_THT:SW_Push_2P2T_Toggle_CK_PVA2xxH1xxxxxxV2` | DPDT push-push, 32 V / 100 mA; PV caps. |
| D2–D5 | 3 mm LEDs | `LED_THT:LED_D3.0mm` | 7.6 mm spacers. |
| CN4 | Keystone 1287-ST | `goa-console:Keystone_1287-ST_FastOn_Tab_6.35mm` | |

**Check on samples before ordering boards:** which PVA2 throw closes when latched (the
schematic assumes 2–1 / 5–4; if not, swap pins 1↔3 and 4↔6 in `tools/gen.py`); the fader pad
pattern against a 1:1 print; detent and C-law pot availability.

### 16.2 Panel stack (unchanged from v3.1)

Panel underside 11.5 mm above the PCB (1.5 mm aluminium). PVA2 H1 + PV cap, panel hole ø8.0.
Pots: 1.5 mm M7 spacer washer, panel hole ø7.2. Fader: 3.5 mm spacer, lever 5 mm above the
panel. 3 mm LEDs on 7.6 mm spacers. Six M3 standoffs, unplated holes. Radial electrolytics,
the bus header, the spade and the VCA socket on the bottom side.

### 16.3 Panel and placement (v4.0)

Study: `strip_panel_study.md`. Chosen: **8 HP × 12U** Eurorack-style panel (40.3 × 514 mm) in a
custom frame with rails only at the two ends, **two pot columns** (x = 10 / 28), jacks on the
panel. One column would need ≈ 545 mm (15U).

Two boards per channel, placed by `tools/place_strip.py` in one coordinate frame (y = 0 is 11 mm below
the panel's top edge), placement only:

| Board | File | Size | Depth under the panel | Parts |
|-------|------|------|-----------------------|-------|
| Main | `channel_strip_v4.kicad_pcb` | 38 × 400 mm, y 44–444 | 11.5 mm | 176 + 6 M3 holes (11.5 mm standoffs) |
| Jack | `jack_board.kicad_pcb` | 38 × 43 mm, y 0–43 | ≈ 24 mm (the NJ6FD-V body) | 6 + 2 M3 holes |

DRC with `--schematic-parity`, both boards: 0 parity issues. The main board has no violations at all;
the jack board has only 6 hole-clearance + 6 solder-mask items inside KiCad's NJ6FD-V footprint (the
SN pad sits close to the footprint's own locating peg). Plus unrouted connections. Silkscreen
references are 0.8 mm text, each placed by the script at the nearest spot clear of pads, silk, other
references, other parts' courtyards and the edge. The bus header CN1 is turned 180° (pin 1 at
y 345.6, same pin field x 31.46/34, y 305–345.6), so its pin-1 arrow stays on the board. The Ø switch moved from the jack row to the main board, right
of the gain pot (above the OL LED). `channel_strip.kicad_pcb` is the old v3.1 placement, kept unchanged.

### 16.4 Jack board and link

The three jacks, plus the input RF caps C8/C9 at J1, are on a separate 38 × 43 mm board
(`jack_board.kicad_sch`, written by `tools/gen.py` with the main schematic). It sits about 24 mm
under the panel, set by the jack body: confirm against Neutrik's drawing or a sample before ordering.
The jack caps hold it on the panel, plus two M3 standoffs of the jack-body height. CN5 (jack board) and
CN3 (main board) are both on the bottom side, so the ribbon runs behind both boards. CN3 sits
between the pot columns at y ≈ 77; the ribbon is about 80 mm long.

| Pin | Net | | Pin | Net |
|-----|-----|-|-----|-----|
| 1 | IN_T (J1 tip) | | 2 | IN_R (J1 ring) |
| 3 | GNDA | | 4 | SEND (J2 tip, and RN normal) |
| 5 | GNDA | | 6 | RET_RAW (J2 ring) |
| 7 | GNDA | | 8 | DO_T (J5 tip) |
| 9 | DO_R (J5 ring) | | 10 | GNDA |

Each pair is adjacent, and ground conductors sit between input, send, return and direct out. The
sleeves go to AGND only through the ribbon. CN3/CN5: Würth 61201021621 2 × 5 box header. Cable:
10-way 1.27 mm flat ribbon with two IDC sockets (not on the BOMs).

---

## 17. Status (v4.0, 2026-10-22)

- Schematic generated by `tools/gen.py` (User-size sheet, label-connected).
- `tools/verify.py`: main 533 pin entries, jack board 30; 0 mismatches, 0 stray pins, no single-pin nets.
- `tools/check_fp.py`: 176 + 6 parts, every symbol pin on a footprint pad.
- KiCad 10.0.7 ERC, `--severity-all`: 0 violations on both schematics.
- `tools/sim_netlist.py` simulates the two exported netlists joined through the ribbon (CN3↔CN5), so
  the source drives J1 and the direct out is read at J5 (25 checks, all pass): levels
  (PRE 0 dBu, POST +9.9 dBu, MIX +3.8 dBu), gain range, Ø, HPF corner, every EQ band at both
  ends, EQ bypass, mute depth, direct out, DIR muting aux 6, PRE/post aux, PAN on/off, PFL.
  It found one real error during development: the new HI-MID nets had the same names as the mute
  nets (M1/M2), so the generator merged them. Fixed by prefixing the EQ nets with `EQ_`.
- Hand-written decks: `sim/gain_stage.cir`, `sim/delta_eq.cir`, `sim/strip_v4.cir`
  (results in `delta_clone_comparison.md` §6). `sim/strip.cir` is the v3.1 path.

**Open:** routing LEDs (a 4PDT switch); C-law dual and centre-detent pot availability;
PVA2 latched-throw sense; NJ6FD-V body height (sets the jack-board depth and standoffs).

*Document version 4.0 — October 2026*
*Sources: Soundcraft Delta ED3344A/B/C, ED3151, ED2911A/B, ED2915A, ED2780*
