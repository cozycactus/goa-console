# Knobs and caps: proposal (2026-10-25)

The knob is the last undecided panel part (`offboard_bom.md`). The 3D model and the panel print use a Ø13 placeholder.

## What the knob has to meet

| Requirement | Source |
|---|---|
| 349 knobs for 1/4" (6.35) **round** shafts (Alpha RD901F / RD902F-40-15R1) and 28 for the **6 mm D** shaft of the ALPS RK09L pan pots; one family, so they look the same | `offboard_bom.md` |
| About Ø13–14.5 (Delta: 14 mm push-on): columns 20.32 mm apart, rows 22 mm; the print's dot ring sits just outside the knob | strip panel decision, `panel_print.md` |
| It clears the M7 nut (10 AF × 2.0) and grips the ~10 mm of shaft left above it | `panel_parts_drawings.md` |
| Coloured caps, with colours per function as the Delta | `panel_print.md` |

## Searched and rejected

- **Sifam** (the Delta's knob maker). Its 13 mm collet knobs (S130 / S131) take shafts up to 4 mm only. Its 1/4" knobs
  start at 15.5 mm (S151 250): the size the strip moved away from on 2026-10-23.
- **Mentor 331.6 / 4331.6000** (14.5 mm collet). Only a 6 mm bore was found, no 1/4".
- **Rogan RB-67 small** (13 mm, set-screw). A spun aluminium insert, no colour caps.
- **Generic set-screw knobs:** no coloured caps, and one size doesn't come in both shaft types.

## Proposal

**KN1. Elma classic collet knob, Ø14.5, matt black with a line.**
- **Codes:** 021-3525 for 1/4" (349) and 021-3425 for 6 mm (28). One moulding and one look, collet-fixed.
- **Fit:** the collet engages 7.0 mm of shaft (Elma datasheet, "classic collet knobs", Ø14.5 page), and about 10 mm
  is left above the nut. The RK09L's 6 mm D shaft is gripped by the same collet. The knob is about 16–17 mm high.
- **No nut covers:** the 044-3xxx skirts (Ø17–18.7) are too wide for the 20.32 mm column pitch and would cover the
  dot ring. From above, the 14.5 knob hides the M7 nut (11.5 across corners).
- **Stock (2026-10-25):** element14 had 302 of the glossy 021-3520 at S$11.16. Don Audio sells the 021-3525 at
  €2.59 (more than 10 in stock). Elma packs them in 100s.

**KN2. The print and the model at Ø14.5.**
- **Print:** `models3d/knob.py` D_KNOB 13 → 14.5; the dot ring and numerals scale with it (`panel_layout.py`).
- **Measured on the generated panels:**
  - the print keeps every name and all but one ring numeral (strip 157 of 158);
  - closest gaps: GAIN knob to the OL LED 2.77 mm (was 3.52), knob to knob 5.82 mm (was 7.32);
  - no cut-out changes.
- **C/ROOM:** the master's C/ROOM knob takes the same 14.5 knob (the model's Ø16 "big" knob is dropped). Elma's next
  size up, Ø21 (021-4525), would be the alternative.
- **Then:** re-run `panels/` and the 3D model.

**KN3. Caps: Elma 040-30x5, matt, without a line** (the knob carries the line).
- **Colours:** Elma has six: grey, black, red, blue, yellow and green. No white or orange, which the model's
  placeholders used.
- **Proposed by function:**

| Colour | Cap | Functions | Qty |
|---|---|---|---|
| Red | 040-3035 | GAIN; master SOLO | 25 |
| Grey | 040-3015 | HF, HI-MID, LO-MID and LF gain; master C/ROOM and PHONES | 98 |
| Blue | 040-3045 | HI / LO MID FREQ and HPF FREQ; group RETURN | 76 |
| Yellow | 040-3055 | AUX 1-2; the aux master on groups 1-2 | 50 |
| Green | 040-3065 | AUX 3-4; the aux master on groups 3-4 | 50 |
| Black | 040-3025 | AUX 5-6 (strip and master); PAN and SUB PAN | 78 |

- **Mapping notes:**
  - the aux pairs keep their colour from the strip to the group's aux master (each group masters aux n);
  - black on AUX 5-6 and the pans replaces the placeholders' orange and grey.
- **Cost:** about 377 knobs at roughly €1.5–2.6 plus 377 caps at about £1.2–1.3 (RS, 50+): roughly €1,100–1,500
  before spares. The cheapest route is Elma's 100-packs from one distributor.

## Sign-off

- [ ] **KN1** Elma 021-3525 (1/4") and 021-3425 (6 mm) collet knobs, Ø14.5, matt black with a line; no nut covers.
- [ ] **KN2** Panel print and 3D model at Ø14.5 (C/ROOM the same knob); panels regenerated.
- [ ] **KN3** Elma 040-30x5 matt caps, colours as in the table (or your own mapping in these six colours).
