# PSU case: proposal (2026-10-26)

`psu_spec.md` §8 sets the case's job, but not the parts:
- **Inside:** two Mean Well LRS-150-24 (159 × 97 × 30 mm each) and the 120 × 60 mm regulator board, whose four
  TO-220s stand in a row along one long edge.
- **Heatsink:** one heatsink of about 1 °C/W, outside the case, fins vertical.
- **Panels:** an IEC inlet with a fuse, a 2-pole mains switch, the NC7FD-LX output, an earth stud and a power LED.
- **Case:** earthed and ventilated.

## Thermal sizing, rechecked at the accepted worst corner

- **LDO dissipation:** each LDO drops 21.6 − 17.0 = 4.6 V. At the accepted worst corner of 4.33 A on +V (master spec
  §27) and the 4 A rating on −V, that is 19.9 + 18.4 = 38.3 W into one heatsink.
- **Per-tab path:** junction to case 1.5 °C/W, silicone pad 0.8 °C/W.

| Heatsink | Rθ (natural convection) | Sink at 30 °C room | +V LDO junction (30 / 35 °C room) |
|---|---|---|---|
| Fischer SK 47 100 SA (200 × 40 × 100) | 0.7 °C/W | 56.8 °C | 102.6 / 107.6 °C |
| **Fischer SK 47 75 SA (200 × 40 × 75)** | ~0.85 °C/W | 62.6 °C | **108.4 / 113.4 °C** |
| Typical load (3.09 / 2.67 A, 26.5 W), SK 47 75 | ~0.85 °C/W | 52.5 °C | 85 °C |

- **SK 47 75 numbers:** distributors quote 0.85 °C/W, and the series 0.45–1.05 °C/W. Read its datasheet curve
  for natural convection before ordering.
- **Margin:** both heatsinks keep the junction under the LM1084's 125 °C at the worst corner. The 75 mm one leaves
  about 12 K in a 35 °C room. Mount the TO-220s directly on the heatsink (below), not through a panel.

## Proposal

**PC1. Case: Hammond 1402KV.**
- **What it is:** aluminium, 254 W × 244 D × 99 H mm, vented, with removable end panels; 1402K is the solid version
  (RS 269-5005, Farnell 1876479).
- **Fit:**
  - the two LRS-150s lie flat side by side across the width (194 mm plus a gap);
  - the regulator board sits behind them along the right side;
  - 99 mm of height leaves the LRS-150s about 60 mm above for convection.
- **Earthing:** the case is earthed at the earth stud, which is wired to the IEC earth pin, both LRS FG terminals,
  the PCB's EARTH terminal (NC7 pin 1) and every panel (star washers).

**PC2. Heatsink: Fischer SK 47 75 SA on the right side panel, fins vertical.**
- **Fit:** the 200 mm profile runs along the 244 mm side; at 75 mm it fits the 99 mm height, where the 100 mm version
  wouldn't.
- **Mounting:** the board's TO-220 edge faces the side. The four tabs go through a window in the side panel straight
  onto the heatsink base, each on a silicone pad with a shoulder washer: the tabs sit at +17 V, 0 V and the rails.
  The heatsink bolts to the panel round the window.
- **Optional:** an 85 °C normally-closed thermal switch on the heatsink, in series with the mains switch (as the spec
  allows).

**PC3. Panels.**
- **Rear:** Schurter DD11 (IEC C14 inlet with a 2-pole switch and fuse drawer, 5 × 20 mm fuse: T2.5 A at 230 V,
  T5 A at 115 V), the NC7FD-LX output and the M4 earth stud. All the mains wiring stays at the rear.
- **Front:** the power LED only.
- **Change from the spec:** `psu_spec.md` §8 puts the mains switch on the front. Moving it into the rear inlet means no
  mains wiring crosses the case, and the console's own power-on mute handles switch-on.
- **Then:** after sign-off, panel drilling drawings for the case (side window and heatsink holes, rear cut-outs from
  the Schurter and Neutrik datasheets, front LED) and the board's standoff positions, generated as `frame/` is.

## Sign-off

- [ ] **PC1** Hammond 1402KV (vented, 254 × 244 × 99 aluminium), earthed at one stud.
- [ ] **PC2** Fischer SK 47 75 SA on the right side, TO-220s through a window directly on the heatsink.
- [ ] **PC3** Rear: Schurter DD11 inlet with switch and fuse, NC7FD-LX, earth stud; front: power LED only.
