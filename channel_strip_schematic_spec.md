# Channel Strip — Component-Level Specification v3.0
## One PCB per channel, ×24. For KiCad implementation.

Bus pinout, grounding and power are defined in `console_architecture.md`.
Where a value comes from a Delta drawing, the drawing number is given.

---

## 0. Changes from v2.0

- Added a ground-compensated differential input receiver (was: input jack straight to insert).
- Added AC coupling (220 µF + 47K) on every node that feeds the bus. (ED3344C)
- Added pan buffers L/R. (ED3344C, IC11)
- Routing switches now ground the 10K resistor when off. (ED3151, ED3344C)
- Mute is now a click-free JFET block. (ED3344B/C, J112)
- Separate logic supply and logic ground. (ED3344B)
- Ground-cancel resistor to bus pin 26 and spade ground terminal. (ED3344C R141, CN4)
- Six dedicated aux pots, 10K log (ED3344C); Shift 5/6 removed.
- Aux pre/post selected per pair by links. (ED3344C J4–J7)
- Insert send has a 75 Ω build-out. (ED3344A R143)
- Fader post-amp gain +10 dB, as the Delta. (ED3344C R130/R132)
- Dropped the 15K balanced-bus footprints (replaced by ground cancel).
- Bus connections follow the real Delta motherloom pinout.

---

## 1. Signal Flow

```
J1 line in (TRS)
  └─ IC1A differential receiver (unity)
       └─ R_bo 75 Ω ─ J2 insert send (tip)
                       [external gear, or jack normalling]
                      J2 insert return (ring)
                         └─ C coupling ─ IC1B buffer ── PRE node (AC-coupled)
                                                         ├─ Aux 1/2 (link: pre)
                                                         ├─ PFL → bus 27, PFL DET → bus 29
                                                         ├─ OL peak detector
                                                         └─ soft mute (2× J112)
                                                              └─ fader ─ [VCA option] ─ IC2A post-amp +10 dB
                                                                   └─ POST node (AC-coupled)
                                                                        ├─ Aux 3/4, Aux 5/6 (link: post)
                                                                        └─ pan pot (dual)
                                                                             ├─ IC2B pan buffer L ─ PAN L (AC-coupled)
                                                                             └─ IC3A pan buffer R ─ PAN R (AC-coupled)
                                                                                  └─ routing switches → 10K → MIX L/R, SUB 1–4
```

---

## 2. Power, Grounding, Bus Connection

### 2.1 Audio rails (from bus pins 30–33)
```
+V (pins 32, 33) ── R1 10 Ω ── +VA ── C1 220 µF/25 V ── C2 100 nF ── AGND
−V (pins 30, 31) ── R2 10 Ω ── −VA ── C3 220 µF/25 V ── C4 100 nF ── AGND
```
- 100 nF ceramic at every op-amp supply pin.
- Bus pin 34 (+48 V): no connection on this PCB.

### 2.2 Logic rails (separate, ED3344B)
```
+V ── R3 10 Ω ── +VL ── C5 47 µF ── LGND
−V ── R4 10 Ω ── −VL ── C6 47 µF ── LGND
```
- Feeds LEDs, mute gate drive, PFL DET, OL comparator.

### 2.3 Grounds
- **AGND**: audio ground pour.
- **LGND**: separate logic pour.
- AGND and LGND join at **one point**, at the spade terminal.
- **CN4 spade terminal** (¼" / 6.3 mm faston): heavy wire to the main ground bar.
- **Ground cancel**: R5 10 Ω from AGND to bus **pin 26**. (ED3344C R141)
- Bus even pins 2–16: AGND.

### 2.4 Bus headers
- CN1, CN2: 34-pin shrouded keyed box headers, wired in parallel (daisy-chain in/out).

| Pin | Signal | Driven on this strip by |
|-----|--------|-------------------------|
| 9 | SUB 4 | R31 4K7 via SW_34 |
| 11 | SUB 3 | R30 4K7 via SW_34 |
| 13 | SUB 2 | R29 4K7 via SW_12 |
| 15 | SUB 1 | R28 4K7 via SW_12 |
| 17 | MIX R | R27 4K7 via SW_LR |
| 18 | MIX L | R26 4K7 via SW_LR |
| 20 | AUX 6 | R25 22K from VR6 |
| 21 | AUX 5 | R24 22K from VR5 |
| 22 | AUX 4 | R23 22K from VR4 |
| 23 | AUX 3 | R22 22K from VR3 |
| 24 | AUX 1 | R20 22K from VR1 |
| 25 | AUX 2 | R21 22K from VR2 |
| 26 | GND CANCEL | R5 10 Ω to AGND |
| 27 | PFL | R32 22K via SW_PFL |
| 29 | PFL DET | R33 100K via SW_PFL |
| 30–33 | −V, +V | power entry |
| 1, 3, 5, 7, 19 | spare | no connection |
| 34 | +48 V | no connection |

---

## 3. Input Receiver (IC1A, ½ OPA1612)

Unity-gain differential amplifier (ground-compensated input).

```
J1 ring ── R6 10K ──┬── IC1A (−)      R7 10K from IC1A out to (−)
J1 tip  ── R8 10K ──┬── IC1A (+)      R9 10K from (+) to AGND
(tip = hot, non-inverting; the whole channel path is non-inverting)
J1 sleeve ── AGND
C7 33 pF across R7 (HF stability)
C8, C9 100 pF from tip and ring to AGND at the jack (RF filter)
```
- R6–R9: 0.1% matched (or a 4-resistor network) for good common-mode rejection.
  (THAT1246 was the alternative here; it went end-of-life in September 2026.)
- **To get ground compensation from an unbalanced synth**, use a "pseudo-balanced" cable:
  TRS at the console, TS at the synth, with the ring conductor joined to the sleeve **at
  the synth end**. With a plain TS cable the input still works, as an ordinary
  unbalanced input.
- Optional R10 1M from tip to AGND so the input doesn't float when unplugged.

---

## 4. Insert

```
IC1A out ── R11 75 Ω ── J2 tip (send)                       (ED3344A R143)
J2 ring (return) ── normalled to tip by the jack when no plug is inserted
J2 ring ── C10 47 µF ── node RET ── R12 47K to AGND
J2 sleeve ── AGND
```
- J2: switched TRS jack with tip and ring normalling contacts.

### IC1B — post-insert buffer (½ OPA1612)
```
RET ── IC1B (+);  IC1B out ── (−)  (voltage follower)
IC1B out ── C11 220 µF ── PRE node ── R13 47K to AGND
```

---

## 5. Pre-fade Section

### 5.1 OL detector (½ LM393, on logic rails)
- Peak detector from IC1B output: D1 1N4148 → C12 1 µF, R14 470K discharge.
- Comparator against a divider set for ~+18 dBu; open-collector output drives the red
  OL LED via R15 1K from +VL.

### 5.2 PFL
```
PRE ── SW_PFL pole A ── R32 22K ── bus 27 (PFL)
+VL ── SW_PFL pole B ── R33 100K ── bus 29 (PFL DET)          (ED3344C R47/R48)
       SW_PFL pole C ── PFL LED (red) via R34 from +VL
```

---

## 6. Soft Mute (ED3344B / ED3344C mute block)

Two cascaded shunt-JFET attenuators, click-free.

```
PRE ── R16 4K7 ── node M1 ── Q1 J112 drain-source to AGND ── buffer
               ── R17 4K7 ── node M2 ── Q2 J112 drain-source to AGND ── IC3B follower ── MUTE OUT
```
- Unmuted: gates held at −VL (JFETs off, open circuit).
- Muted: gates pulled to 0 V (JFETs on, tens of ohms): roughly 40 dB per stage.
- Gate drive through an RC ramp (e.g. 220K / 100 nF, with 1N4148 steering, as ED3344B)
  so the gain changes over ~20 ms instead of switching instantly.
- SW_MUTE: latching switch on the logic side only; it never carries audio.
- Mute LED (amber) from the same logic signal.
- IC3B (½ OPA1612 or NE5532): buffer so the fader is driven from a low impedance.

---

## 7. Fader and Post-amp

```
MUTE OUT ── fader top (100 mm, 10K log/audio taper)
fader bottom ── AGND
fader wiper ── C13 2.2 µF ── [VCA option / JP1] ── R18 100K to AGND ── IC2A (+)
IC2A out ── R19 4K7 ── IC2A (−) ── R38 2K2 to AGND;  C14 100 pF across R19
IC2A out ── C15 220 µF ── POST node ── R35 47K to AGND
```
- Gain 1 + 4K7/2K2 ≈ +10 dB (ED3344C R130/R132): the fader's "0" mark sits about 10 dB
  below the top, giving 10 dB of gain at full travel.
- For unity at the top instead, omit R38 (follower).

### 7.1 VCA option (unpopulated)
- The THAT 2180/2181 planned here went end-of-life (September 2026). **Replaced by a plug-in VCA
  module built around a Sound Semiconductor SSI2162** (in production).
- The SSI2162 is current-in/current-out (output compliance only ±100 mV), so it needs an I/V
  converter, which inverts. To keep the strip's polarity and its PCB simple, the VCA lives on a
  small module: 10K input resistor → SSI2162 (both channels in parallel: 3 dB lower noise) →
  inverting I/V op-amp (10K ∥ 47–100 pF) → unity inverter. Voltage in, voltage out, in phase,
  unity gain at 0 V control.
- Datasheet figures for one channel, class AB, 10K: −99 dBu output noise (20 Hz–20 kHz),
  0.05 % THD at 0 dB; paralleling both channels lowers the noise by about 3 dB.
- Control: ground-referenced, −33 mV/dB, from a module pin (for VCA groups or automation later).
- On the strip: a footprint for the module (header: in, out, control, ±V, GNDA) across C13 →
  R18, with JP1 bridged when no module is fitted. Not yet in `tools/gen.py`.

---

## 8. Aux Sends

- VR1–VR6: 10K log (Delta ED3344C uses 10KA; ED2911A uses 20K log).
- Pot: top = source node, bottom = AGND, wiper → 22K → bus.
- Source links per pair (set at build time, like Delta J4–J7):

| Pair | Link PRE | Link POST | Default |
|------|----------|-----------|---------|
| Aux 1/2 | PRE node | POST node | PRE |
| Aux 3/4 | PRE node | POST node | POST |
| Aux 5/6 | PRE node | POST node | POST |

- Optional **stereo Aux 5/6**: link Aux 5 source to PAN L and Aux 6 to PAN R, and fit a
  dual-gang pot at VR5 (VR6 not fitted). Footprint should allow both.

---

## 9. Pan and Pan Buffers

```
POST ── VR7 gang A (CW) ... wiper ── IC2B (+) ── follower ── C16 220 µF ── PAN L ── R36 47K
POST ── VR7 gang B (CCW)... wiper ── IC3A (+) ── follower ── C17 220 µF ── PAN R ── R37 47K
```
- VR7: 10K dual-gang pan pot (constant-power / MN taper, or linear "B" with the Delta's
  buffer arrangement).
- IC2B: ½ OPA1612. IC3A: ½ OPA1612 or NE5532.
- The buffers isolate the pan law from the routing load.

---

## 10. Routing Matrix

Each assign switch is DPDT. Each resistor is always connected to the pan buffer; the
switch sends its far end either to the bus (on) or to clean AGND (off). (ED3151, ED3344C)

```
PAN L ── R26 4K7 ──┬─ SW_LR pole A ── on: bus 18 (MIX L)   off: AGND
PAN R ── R27 4K7 ──┴─ SW_LR pole B ── on: bus 17 (MIX R)   off: AGND
PAN L ── R28 4K7 ── SW_12 pole A ── on: bus 15 (SUB 1)     off: AGND
PAN R ── R29 4K7 ── SW_12 pole B ── on: bus 13 (SUB 2)     off: AGND
PAN L ── R30 4K7 ── SW_34 pole A ── on: bus 11 (SUB 3)     off: AGND
PAN R ── R31 4K7 ── SW_34 pole B ── on: bus 9  (SUB 4)     off: AGND
```
- R26–R31: 4K7 1% metal film (chosen for the quieter bus; 10K for Delta compatibility), 0.5 W body for low excess noise (the Delta uses 0.5 W).
- Constant load on each pan buffer: 3 × 10K = 3.3K (or 1.57K with 4K7), whatever is routed.
- Option: 4K7 routing resistors for a quieter bus (see architecture doc 2.4). The master
  summing feedback resistors must then also be 4K7.

### 10.1 Why the pan buffers are needed (calculated)
Linear 10K pan pot, level of one side:

| Pot position | Buffered (unloaded) | Unbuffered, 1 route (10K) | Unbuffered, 3 routes (3.3K) |
|--------------|---------------------|---------------------------|-----------------------------|
| full | 0 dB | 0 dB | 0 dB |
| ¾ | −2.5 dB | −4.0 dB | −6.4 dB |
| centre | −6.0 dB | −8.0 dB | −10.9 dB |
| ¼ | −12.0 dB | −13.5 dB | −15.9 dB |

- Unbuffered, the centre level falls by about 5 dB and the pan law changes shape.
- With the buffers, the pan law is set by the pot alone: linear gives −6 dB at centre.
  For a −3 dB (constant-power) centre, use an MN/constant-power taper pot, or give the pan
  buffers about +3 dB of gain with a linear pot (hard-panned then reads +3 dB).
- Assign LEDs optional, on logic rails.

---

## 11. IC Summary

| Ref | Part | Halves |
|-----|------|--------|
| IC1 | OPA1612 | A: input receiver; B: post-insert buffer |
| IC2 | OPA1612 | A: fader post-amp; B: pan buffer L |
| IC3 | OPA1612 or NE5532 | A: pan buffer R; B: mute output buffer |
| IC4 | LM393 | A: OL comparator; B: spare (inputs tied off) |
| Q1, Q2 | J112 | Soft mute |

---

## 12. Bill of Materials (per channel, approximate)

| Qty | Part | Notes |
|-----|------|-------|
| 3 | OPA1612 (or 2× OPA1612 + 1× NE5532) | SOIC-8 |
| 1 | LM393 | SOIC-8 or DIP-8 |
| 2 | J112 | TO-92 |
| 2 | TRS jack, switched, isolated | J1 input, J2 insert |
| 2 | 34-pin shrouded box header | CN1, CN2 |
| 1 | 6.3 mm spade/faston tab | CN4 ground |
| 1 | 100 mm fader, 10K audio taper | |
| 6 | 10K log pot | Aux 1–6 (VR5 footprint also fits dual-gang) |
| 1 | 10K dual-gang pan pot | VR7 |
| 3 | DPDT latching switch | L/R, 1-2, 3-4 |
| 1 | 3PDT (or DPDT + LED) latching switch | PFL |
| 1 | Latching switch | Mute (logic only) |
| 3 | LED | OL red, mute amber, PFL red |
| 4 | 10K 0.1% (or resistor network) | Input receiver |
| 6 | 10K 1% 0.5 W | Routing |
| 7 | 22K 1% | Aux ×6, PFL |
| ~25 | Assorted 1% resistors | 10 Ω ×5, 75 Ω, 4K7, 2K2, 47K ×6, 100K ×2, 470K, 1K ×3, 1M |
| 6 | 220 µF 25 V | Rails ×2, PRE, POST, PAN L, PAN R |
| 2 | 47 µF 25 V | Logic rails, insert return |
| 1 | 2.2 µF film or electrolytic | Fader wiper coupling |
| 1 | 1 µF | OL detector |
| ~10 | 100 nF ceramic | Decoupling, mute RC |
| 4 | 33–100 pF C0G | Stability and RF |
| 4 | 1N4148 | OL, mute steering |

Roughly 90–100 parts per channel (up from ~50 in v2.0, mostly from the input receiver,
pan buffers, AC coupling and soft mute).

---

## 13. PCB Layout Notes

- 2-layer board, AGND pour on the bottom, separate LGND pour; join at the spade terminal.
- Keep the routing resistors (R26–R31) and aux summing resistors (R20–R25) next to the
  bus headers; the bus side of each resistor is a virtual-earth node, so keep those traces short.
- Keep the input receiver resistors symmetrical and close to IC1.
- Coupling capacitors: watch polarity; DC on the PRE/POST/PAN nodes is near 0 V, so use
  bipolar (non-polarised) electrolytics, or orient for the op-amp's offset sign.
- LED and mute-drive traces on LGND only, away from the audio path.
- Footprints: SOIC-8 op-amps, 0805 or through-hole passives, through-hole jacks and headers.

### 13.1 Panel parts (chosen October 2026)

Assumed construction: one long PCB per strip, ~40 mm wide, lying flat under the top panel.
Pots, switches, fader and LEDs mount on the PCB and come through the top panel. The two
jacks are right-angle parts on the rear edge of the PCB and come through a vertical rear
apron. Top to bottom: OL LED, Aux 1–6, pan, assign L-R / 1-2 / 3-4, PFL, mute, fader.

| Ref | Part | Footprint | Notes |
|-----|------|-----------|-------|
| J1, J2 | Neutrik NRJ6HF | `Connector_Audio:Jack_6.35mm_Neutrik_NRJ6HF_Horizontal` | Plastic nose, so the sleeve is isolated from the panel. Not the `-1` variant, which bonds the sleeve to the panel. J1 uses the switched symbol with TN/RN unused; SN is unused on both. |
| RV1 | Bourns PTB0143-2010BPA103 | `goa-console:Potentiometer_Bourns_PTB0143_Slide_100mm` | 100 mm, A10K, metal housing, 10 mm metal lever, M3 panel screws. Body tabs are unconnected pads: the housing reaches chassis through the panel screws, not through AGND. Pin 1 (ground end) faces the operator. |
| RV2–RV7 | Alpha RD901F-40, A10K | `Potentiometer_THT:Potentiometer_Alpha_RD901F-40-00D_Single_Vertical` | 9 mm vertical. Shaft length is set by the panel height. |
| RV8 | Alpha RD902F-40, B10K, centre detent | `Potentiometer_THT:Potentiometer_Alpha_RD902F-40-00D_Dual_Vertical` | Confirm a detent version is stocked. |
| SW3–SW7 | C&K PVA2 EE H1 1.7N V2 | `Button_Switch_THT:SW_Push_2P2T_Toggle_CK_PVA2xxH1xxxxxxV2` | DPDT push-push. Rated 32 V DC / 100 mA, enough for audio and logic. H1 is 17.5 mm tall; H2 (23 mm), H3 (20.5 mm) and H4 (15 mm) use the same footprint, so the height can be picked later to suit the panel stack. Caps are ordered separately (PE/PV). |
| CN4 | Keystone 1287-ST | `goa-console:Keystone_1287-ST_FastOn_Tab_6.35mm` | 0.250 in tab, two legs, both pads are GNDA. |

**Audio-taper pin order.** On A-taper pots the law runs from pin 1, so pin 1 is the ground
end. The fader and the aux pots are wired 1 = GNDA, 3 = signal. Before v3.1a they were wired
the other way round, which would have given a reverse-log law.

**Check before ordering boards:**
- Fader pad pattern against a real PTB100, using a 1:1 print. The datasheet layout view may be
  mirrored relative to the component side.
- PVA2 switching sense. Pin 2/5 (datasheet "0") is common. Which throw (1 or 3) closes when
  the switch is latched in must be confirmed with a meter. The schematic assumes 1–2 / 4–5
  closed when latched (PFL on, mute on, routed). If it is the other way, mirror the
  footprint or swap pins 1↔3 and 4↔6 in `tools/gen.py`.
- Panel stack height: fixed in section 13.3.

### 13.3 Panel stack (October 2026)

Heights above the PCB top surface, from the datasheets (Bourns PTB100 drawing, Alpha
RD901F-40 drawing SLH-211-414, C&K PVA datasheet A-170/A-171):

| Part | Datasheet heights | Arrangement |
|------|-------------------|-------------|
| Panel | — | **underside 11.5 mm above the PCB**, 1.5 mm aluminium (top at 13.0) |
| PVA2 switch | body 11.0; H1 actuator 17.54 overall, cap snaps on the top 3.9 mm | **H1** (as in the MPN) + **PV cap** (ø7.4 × 9.7, ordered separately). Cap bottom 13.6 at rest (0.6 above the panel, top 10.3 mm proud), 12.1 latched, 11.2 fully pressed: panel hole **ø8.0** so the cap can sink through. H3 would leave the cap floating 3.6 mm above the panel. |
| Pots RD901F-40, L = 15 | body face 10.0; M7×0.75 bushing to 15.0; shaft to 25.0 | **1.5 mm M7 spacer washer** between body and panel; M7 nut (2.0 mm, no washer) flush with the bushing end; 12 mm of shaft for the knob. Panel hole ø7.2. |
| Fader PTB0143 | body top 8.0; lever 10.0 above body (top at 18.0) | **3.5 mm spacer** between body and panel, M3 × 8 screws into the body. Lever stands **5.0 mm above the panel**: choose a knob that grips a flat metal lever with 5 mm engagement, or get a longer lever from Bourns (not found as a standard part). |
| 3 mm LEDs (OL, PFL, MUTE) | T-1 LED ≈ 5.3 mm tall | **7.6 mm LED spacer**, dome flush with the panel top; panel hole ø3.1. |
| NRJ6HF jacks | nose ø11.2, body top ≈ 12 (estimated) | Taller than the gap: the top panel starts in front of them (y ≈ 27 mm); the rear apron covers the jack zone. |
| Standoffs | — | 6 × M3, 11.5 mm (or 11 mm + 0.5 mm washer), unplated holes H1–H6 so audio ground never meets the chassis. |

Parts too tall for the gap moved to the bottom side: the nine radial electrolytics, the
ground spade CN4 (faston + wire), and the VCA module socket J3 with its control header J4
(a module on a socket would stand 12–13 mm). Remaining top-side parts are SMD, the 1N4148
(DO-35, lying), the pots, switches, LEDs, fader and jacks.

### 13.2 PCB first placement (October 2026)

`channel_strip.kicad_pcb`, made by `tools/place_strip.py` (KiCad 10 pcbnew, run with KiCad's
bundled Python) from the netlist. Footprints are linked to their schematic symbols, so
"Update PCB from Schematic" works; schematic UUIDs are now deterministic, so regenerating the
schematic keeps the link. Placement only: no tracks or pours yet.

Board 38 × 480 mm (40 mm strip pitch, 1 mm clearance per side), two layers. y = 0 is the rear
edge. Control column at x = 19 mm.

| y (mm) | Panel feature | Notes |
|--------|---------------|-------|
| 0 | Rear edge: J1 line in, J2 insert | NRJ6HF noses through the rear apron, centres at x = 10 and 28 |
| 27–47 | — | input receiver + insert electronics |
| 48–61 | — | insert coupling caps C10, C11 (**bottom**) |
| 62–72 | — | rail reservoir caps C1, C3, C5, C6 (**bottom**) |
| 73–81 | — | power entry resistors, decoupling, net tie, spade tab |
| 84 | OL LED | |
| 84–90 | — | ground spade CN4 (bottom, x = 19) and net tie NT1 (top, x = 26.5): the strip's AGND-LGND star point |
| 100–200 | Aux 1–6 | 20 mm pitch; aux source jumpers in the left band, OL detector in the right |
| 222 | Pan | pan buffers in the right band (132–180); post and pan coupling caps C15–C17 below them on the **bottom** (181–233) |
| 236–288 | Bus headers CN1/CN2 | **bottom side**, so the ribbon runs under the boards; between them on top: the aux 22K (R20–R25) and routing 4K7 (R26–R31) bus resistors (spec 13: virtual-earth ends short) |
| 297 | L-R, 1-2, 3-4 | 12 mm pitch, right next to the headers: short virtual-earth traces |
| 314 | PFL + LED | |
| 331 | MUTE + LED | PFL and soft-mute electronics in the left band below |
| 346–478 | Fader, slot centre 412 | ground end (pin 1) to the front; post-amp and VCA socket in the right band |

Ground pours (`tools/pour_strip.py`, run after the placement script):
- B.Cu: AGND (GNDA) over the whole board.
- F.Cu: two LGND (GNDD) islands — one over the reservoir caps, power entry and OL detector
  (holding NT1 beside the spade), one over the PFL/MUTE rows — linked by one GNDD track on the
  bottom along the right edge (x = 37 mm). AGND fills the rest of the top layer.
- 369 GNDA stitching vias on a 4 mm grid, only where no courtyard, pad or LGND island is near;
  top-side GNDA SMD pads inside an LGND island get a short track to their own via.

DRC (`kicad-cli pcb drc --schematic-parity`): no clearance or courtyard violations, 0 schematic
parity issues, GNDA and GNDD fully connected. 178 unconnected signal items remain, plus
silkscreen overlaps from the packed reference designators.

Still to decide or do in KiCad:
- Mounting: six M3 standoff holes H1–H6 (section 13.3) at (34, 84.5), (5.5, 160), (19, 232.4),
  (34, 305.5), (5.5, 474.5), (32.5, 474.5); plus the pot nuts and the fader's M3 screws.
- All nine radial electrolytics (C1, C3, C5, C6, C10, C11, C15, C16, C17; D6.3–D10, 11–16 mm tall),
  the spade tab CN4 and the VCA socket J3/J4 are on the **bottom side** (section 13.3).
- Routing, AGND and LGND pours joined at the spade (section 13), silk clean-up.

---

## 14. Schematic and Simulation Status (v3.1)

**KiCad schematic** (`channel_strip/channel_strip.kicad_sch`, KiCad 7 file format, opens in KiCad 10, A1):
- Generated from this spec by `tools/gen.py`; nets joined by labels, grounds as GNDA/GNDD.
- KiCad's exported netlist was checked pin by pin against the design (`tools/verify.py`):
  337 pins, 0 mismatches, 0 stray pins, no single-pin nets.
- Every part has a footprint (panel parts in section 13.1). `tools/check_fp.py` confirms that
  every symbol pin lands on a pad of its footprint (101 parts, 0 problems).
- KiCad 10.0.7 ERC (`kicad-cli sch erc --severity-all`, default rule set): 0 errors,
  0 warnings. Library symbols are embedded from the KiCad 10 libraries.

**ngspice signal-path simulation** (`sim/strip.cir`; ideal op-amps, generic J112 model),
0 dBu into the tip:

| Node | Level at 1 kHz |
|------|----------------|
| Receiver out (RECV) | 0.0 dBu, in phase with tip |
| PRE | 0.0 dBu |
| POST, fader at top | +9.9 dBu |
| PAN L, pan centre (linear pot) | +3.9 dBu (−6 dB pan law) |
| Mix bus out, fader at top | +3.9 dBu, inverted (master must re-invert) |
| Mix bus out, fader at "0" mark (−10 dB travel) | −6.3 dBu |
| Mute engaged (MUTEOUT) | −86 dBu (≈ 86 dB of mute depth) |
| Low-frequency −3 dB point, whole chain | 1.1 Hz |
| 100 kHz | −0.5 dB |

**Headroom note.** With the +10 dB post-amp and ±16–17 V rails (about +22 dBu swing), a
channel with the fader at the top clips at about +12 dBu input. Hot synths therefore need
the fader below the top, or the external input module's trim/pad. If that proves
limiting, fit R38 as a higher value (e.g. 4K7 for +6 dB) or omit it for unity.

*Document version 3.1 — October 2026*
*Sources: Soundcraft Delta ED3344A/B/C, ED3151, ED2911A/B, ED2915A, ED2780*
