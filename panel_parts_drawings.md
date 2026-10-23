# Panel parts against the manufacturers' drawings

Read on 2026-10-23 to build the 3D models in `tools/models3d` (one module per part). For every family except
the last, a second reader went back to the drawings independently. All numbers are in mm. Board z = 0 is the
seating plane; the panel stack is spec 16.2.

## Sources

| Part | Drawing |
|------|---------|
| Alpha RD901F-40-15R1 | Alpha spec SP26020021 (2026-02-04) containing drawing SLH-211-414 "RD901F-40-(L)R1-XXX-0XD" (2022-06-24): taydaelectronics.com/datasheets/files/SP26020021_RD901F-40-15R1-B10K-0CD-1.pdf |
| Alpha RD902F-40 | Taiwan Alpha catalogue "9mm Single Metal Shaft, Multi-Ganged Series" (2024-11-11), p. 4-5: taiwanalpha.com.tw/downloads?target=products&id=113 (no RD902F-40-15R1 drawing exists; shaft, nut and terminals taken from the RD901F R1 drawing) |
| C&K PVA2 + PV cap | C&K/Littelfuse PVA series, rev. 02/20/25 (ckswitches.com/media/1343/pva.pdf), same views as the 2018 D-15..D-17 pages |
| Neutrik NJ6FD-V | NJ*FD-V family drawing (Neutrik product guide, Plugs & Jacks 2021-04 V22, p. 17) and the NJ3FD-V drawing / DXF. Neutrik's own NJ6FD-V drawing could not be fetched (neutrik.com was down, nothing archived). |
| Neutrik NC3MAV | ST-NC3MAV, index C (2010-01-12), cross-checked with ST-NC3MAV-1 (2003) |
| Bourns PTB0143/0144 | PTB series REV. 08/20 (bourns.com/docs/Product-Datasheets/ptb.pdf), PTB100 drawing p. 2, lever styles p. 1 |
| Keystone 1287-ST | Keystone catalogue M75 p. 65 (keyelco.com/userAssets/file/K75p65.pdf) |
| Bourns MF-RX160/72 | MF-RX/72 series REV. W (bourns.com/docs/product-datasheets/mf-rx72.pdf), p. 2 |

## Findings

| Part | What the drawing says | What it means here |
|------|-----------------------|--------------------|
| NJ6FD-V | Flange front is 24.00 above the PCB, the housing sits on 0.5 feet, and the panel range is 1.2–1.5. There is no thread, nut or washer: the snap-on / twist-off cap's front sits 9.0 above the panel underside. Panel hole ≥ 12.0. | The **24.0 mm jack-board depth is confirmed**. Use M3 female-female standoffs of exactly 24.0: the jacks are rigid spacers, so a longer standoff would hang the board on the solder joints. Our 1.5 mm panel is the jack's upper limit: anodise it, don't powder-coat it. Check on a sample: the side views draw the Ø2.0 peg 3.18 off the axis against 3.81 in the layout and footprint; TN/RN/SN positions are unchecked. |
| NC3MAV | This is an A-series rear-mount receptacle, not D-size. PCB to housing front is 24; the Ø21.8 nose stands 1.2 above a 1.5 panel. Mating pins are Ø2.38. | The **same 24.0 depth** as the NJ6FD-V, so one master jack board suits both. Panel cut-out: hole ≥ Ø22 plus two Ø3.2 at (−9.9, −9.9) / (+9.9, +9.9) from the axis in the footprint frame (upper left / lower right seen from the front). Only the nose and two screw heads show on the panel. |
| RD901F / RD902F-40-15R1 | Mounting face 10 ± 0.5 above the seating plane. Bushing M7 × 0.75 × 5.0. Shaft Ø6.35 (R1), 15 from the face, top at 25.0. Nut 10 AF × 2.0. Anti-rotation lug 2 × 0.8, 0.8 high at r 6 (top z 10.8). | The bushing equals spacer 1.5 + panel 1.5 + nut 2.0 exactly, leaving **no spare thread**. Leave the supplied 0.4 washer off, or find the 7 mm bushing (code B3; listed in the order code but not for the -40 bracket version). **All three pot types have 1/4" shafts**, so every knob is 1/4", with 9.6 mm of shaft above a nut-clearing knob. Spacer-washer OD must be < 11.2 to clear the lug (model: 10). Fit the panel and tighten the nuts before soldering the pots, to take up the ±0.5. KiCad's tab slots are turned 90° from Alpha's PCB detail (Alpha: 1.8 along the tab line): check a sample tab. |
| PVA2 EE H1 + PV cap | H1 = 17.54 ± 0.2 to the plunger top; collar top at 11.0. Latching travel 1.5, full stroke 2.4. The PV cap is round, Ø7.4 × 7, colours RD/GY/BK/WH (GR in the ordering code only). | The collar clears the panel underside by 0.5. The cap stands 0.64 above the panel released and goes 0.86 into the hole latched. The Ø8.0 hole leaves **0.30 radial clearance** to the cap on every press, before pin and hole tolerances: check on a panel prototype. No yellow or orange caps exist. KiCad's "h=17.5mm" is the H1 code. |
| PTB0143 / PTB0144-2010BPA103 | Body 8.0 to the cover top; lever 10.0 above that (top at z 18.0, 5.0 above the panel, as planned). BP lever = flat blade 8.0 wide × ~1.3. Panel fixing: two tapped M3 in the cover, 120.0 apart on the slot line. Base flange 16.0 wide. | The stack fits exactly. **The BP blade takes no standard 4 mm knob.** The AP lever (4.0 split fork) exists only as the linear PTB0143-2010APB103; the audio AP codes are not sold anywhere (factory order, MOQ ~800, 12-14 weeks), and no maker stocks a 100 mm A10K fader with a 4 mm lever (ALPS RSA0N has a T-bar that sits 3.2 mm above our panel; TT PS100 and Song Huei are blades / T-bars with large MOQs; Bourns PTF is obsolete). Kept the stocked BP parts (Mouser 620 single / 420 dual on 2026-10-23) with caps made for an 8 mm flat lever. Panel slot ≥ 108 × ≥ 1.3 (model 110 × 2.4), plus two Ø3.2 at ±60 from the slot centre. Use M3 × 6 screws (about one thread in ~0.6 sheet). The footprint's fab outline shows the 15.0 cover, so its courtyard has zero margin to the flange. REV. 08/20 doesn't say on which side of the slot the single-gang pins sit: confirm with the 1:1 print / a sample. A cheap hedge is the dual pad pattern on the PTB0143 footprint. |
| 1287-ST | Legs 1.14–1.27 × 0.81 (diagonal 1.40–1.50) for a Ø1.3 hole. 10.2 above the board; legs 3.8 below. | It is a press fit, as Keystone intends; a 1.4–1.5 hole would ease hand insertion. Bottom side only, which is where it is placed. |
| MF-RX160/72 | Style 2: square body on **straight** leads (kinked = suffix -14). 19.94 max high, 3.1 max thick. | With straight leads the seating height is not defined (modelled 1.5 standoff, 21.4 total); order -14 for a fixed one. Bottom side only. F1/F2 and F3/F4 face each other 4.5 apart, so a tripped PTC (~1.9 W) warms its partner and lowers its hold current. |

Also found: the master BOM gave the M4 star stud (CN1) the 1287-ST's MPN. Fixed in `tools/schgen.py`: an explicit
`mpn=''` now stays empty.
