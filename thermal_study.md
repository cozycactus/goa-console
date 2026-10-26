# Console thermal study (2026-10-26)

**The question.** The console dissipates about 98 W inside a shallow wooden tub closed by the aluminium panels. How warm
does it get inside, what does that do to the parts, and what should the tub do about it before the woodwork is drawn?

**The model.** `sim/review/thermal/tub_thermal.py`, a lumped steady-state model:
- **Geometry:** from the 3D model. The cavity is 1219 × 516 mm and 56.5 mm deep under the panels; tilt 9°.
- **Dissipation:** 17 V × (3.09 + 2.67 A) = 98 W typical, from the master spec §27 budget (≈ 104 W since MET1 / RET1,
  2026-10-26: `tub_thermal.py` at that figure gives the vented case 16.9 K, mid, against 16.1 K); 116 W with every op-amp at
  maximum current.
- **Heat paths:**
  - through the black anodised panels (inside film → panel → convection and radiation to the room);
  - through the wooden floor and walls;
  - through vents, as a buoyancy chimney from a low inlet to a high outlet. The tilt plus the cavity depth give 137 mm
    of stack.
- **Uncertainty:** an enclosed cavity full of boards isn't a textbook case, so the inside film coefficients are given as
  a range (low / mid / high: 2 / 3.5 / 5 W/m²K to the panel, 1 / 1.5 / 2.5 to the floor). Every result below is for all
  three.

## Results

Inside-air rise above the room at 98 W:

| Case | low | mid | high |
|---|---|---|---|
| **Closed tub** (as the 3D model is now) | 60 K | **41 K** | 31 K |
| Front and back slots, 1.2 m × 12 mm each | 21 K | 18 K | 17 K |
| Front and back slots, 1.2 m × 20 mm each | 16 K | 15 K | 13 K |
| **Floor slots 1.2 m × 20 mm inside the front rail + 30 slots 30 × 25 mm through the back rail + back-trim slot 1.2 m × 20 mm** | 18 K | **16 K** | 15 K |
| One slow 120 mm fan, about 30 m³/h | 8 K | 8 K | 7 K |

**What the closed tub means.** About 66 °C inside in a 25 °C room, with the parts a few kelvin above that.
- **Coupling caps:** every audio coupling cap is a Nichicon MUSE ES bipolar, rated 1000 h at 85 °C. Electrolytic life
  roughly doubles for every 10 K below the rating. At about 71 °C on the part that is about 2600 h: 1.8 years at
  4 hours a day.
  - They don't fail suddenly: capacitance falls and ESR rises, so the low-frequency corner creeps up.
  - They sit at almost no DC bias with no ripple, which helps, but not by an order of magnitude.
- **Wing PTCs:** the hold current falls with temperature. At 66 °C a wing's typical 1.37 A on +V is still held, but the
  accepted worst corner (1.96 A) would trip it sooner.
- **Unaffected:** op-amps, switches, pots and LEDs are comfortable even at 66 °C.

**With the vented path** (about 16 K, 41 °C inside, about 46 °C on the parts): MUSE ES life is about 15 000 h,
10 years at 4 hours a day. The panel top runs about 12 K above the room closed and 5 K vented.

**Why the vents go where they do.** The two 10 × 50 frame rails run the full width under both panel ends and reach to
6.5 mm off the floor, so they wall off the cavity front and back.
- **Inlet:** cold air can come in through floor slots just inside the front rail. The floor is free there: y 445–490,
  between the strips' fader end (444) and the rail.
- **Outlet:** the warm air pools under the panels at the high back end, so it has to leave through the back rail. The
  rail gets slots on its neutral axis into a plenum in the back trim, which has a slot on top.
- **The slots' cost to the rail:** 25 mm slots on the axis remove 12.5 % of the bar's stiffness where they are. Over 73 %
  of its length that moves the sag from 0.21 to 0.23 mm (0.53 to 0.59 mm under 100 N). 15 mm slots: 2.7 %, unmeasurable.

## Proposals

**TH1. A vented tub** (recommended). Built into the tub and the back rail, about 16 K inside rise:
- **Floor inlet:** slots in the floor just inside the front rail, at least 1.2 m × 20 mm free area in all (for example
  two rows of 10 mm), with a fine mesh against dust and a 10 mm air gap under the tub (feet).
- **Back rail:** 30 slots, 30 × 25 mm, centred on its neutral axis (25 mm below its top face), between the panel screw
  holes. A change to the signed FR1 drawing; `frame_fab.py` adds them.
- **Back trim:** a plenum behind the back rail, open to it, with a slot along its top of at least 1.2 m × 20 mm. The
  slot faces up and back, away from the engineer.
- **The tub drawings** (still to do) carry these.

**TH2. A slow fan** (optional, not recommended now). One 120 mm fan at about 5 V (about 30 m³/h, quiet but not silent)
exhausting through the back-trim plenum gives about 8 K. It needs a supply (a 5 V regulator from +V) and puts a moving
part and some noise in a studio console. Keep it as the fallback if the measured rise of the built console exceeds
20 K.

**TH3. 105 °C bipolars** (optional). Nichicon's UEP series (bipolar, −55 to +105 °C) in place of the MUSE ES, in the
same footprints where the sizes match.
- **Life:** about four times the MUSE ES's at any temperature, which covers the closed-tub case on its own.
- **Cost:** it reopens the signed F1–F4 choice of audio-grade bipolars (`film_np_proposal.md`).
- **Recommendation:** TH1 alone is enough, so TH3 only if the vents can't be built.

**Measure on the build:** two thermocouples (inside air under the back panels, and a MUSE ES on a mid-console strip)
after 2 hours at idle, with the room temperature noted.

## Sign-off

Signed off by Ruslan on 2026-10-26: TH1–TH3 as proposed.

- [x] **TH1** Vented tub: floor inlet slots inside the front rail, 30 × (30 × 25 mm) slots through the back rail,
  back-trim plenum with a top slot.
- [x] **TH2** No fan now; a 120 mm fan is the fallback if the built console's inside rise exceeds 20 K.
- [x] **TH3** Keep MUSE ES (no change), given TH1.

## Applied (2026-10-26)

- **Back rail:** `panel_layout.vent_slots()` holds the 30 slots, 30 × 25 mm, centred 25 mm below the top face and spread
  evenly from 40 mm in (39.56 mm pitch). `frame_fab.py` draws them on the back rail only; the front rail is unchanged.
  - **Bonding hole:** on both rails it moved from the side face to the bottom face (M4 × 8), into the gap between the two
    middle slots, so it can't land on a slot.
  - **Checks:** the script checks the slots against the end holes and the bonding hole.
  - **Outputs:** the drawing (`frame/rail.pdf`) and hole table now say front 1 off, back 1 off.
- **3D model:** the back rail is built slotted (top and bottom strips and 31 webs).
- **Tub requirements** for the woodwork drawings (`offboard_bom.md` Tub row):
  - floor inlet slots inside the front rail, at least 1.2 m × 20 mm free area, with mesh;
  - feet giving a 10 mm air gap under the tub (superseded by `tub_proposal.md` TB2: the underside is open between the
    cheeks, with 30 mm under the front of the floor);
  - a back-trim plenum open to the back rail's slots, with a top slot of at least 1.2 m × 20 mm facing up and back.
- **No fan** (TH2); MUSE ES kept (TH3).
