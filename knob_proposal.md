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
- **Measured on the generated panels** (before the edge rule below):
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

Signed off by Ruslan on 2026-10-25: KN1–KN3 as proposed, C/ROOM the same knob.

- [x] **KN1** Elma 021-3525 (1/4") and 021-3425 (6 mm) collet knobs, Ø14.5, matt black with a line; no nut covers.
- [x] **KN2** Panel print and 3D model at Ø14.5 (C/ROOM the same knob); panels regenerated.
- [x] **KN3** Elma 040-30x5 matt caps, colours as in the table (or your own mapping in these six colours).

## Applied (2026-10-25)

- **Model:** `tools/models3d/knob.py` is the Elma Ø14.5 (body 15 high, Ø11 cap, line on the rim and side; it sits 0.4 above
  the M7 nut). The "big" C/ROOM knob is gone everywhere: `alpha_pot` / `alps_rk09l` `panel()`, `console_3d.py`,
  `panel_layout.py`.
- **Colours:** set in `panel_layout.py` as in the KN3 table. The model shows one group design, so its AUX cap is yellow;
  groups 3–4 take green.
- **Print:** the larger ring put the 3 / 9 o'clock numerals of the edge-column pots off the plate, and numerals of
  neighbouring knobs met between the columns ("9 50"). Two rules in `panel_layout.panel_print()` now drop:
  - an optional numeral within 0.5 mm of the plate edge;
  - an optional numeral within 1.2 mm of another knob's text (0.3 mm within one knob's ring).
  
  Strip ring numerals and units: 158 at Ø13 → 137; master 79 → 75; group 42 → 39. Every name, end-of-scale numeral and
  centre mark still prints; the drops are inner numerals (9s, 8s, 2s) on the crowded side.
- **Panels:** `panels/` regenerated; strip, group and master pass every check. Closest knob gaps: 2.77 mm to the OL LED
  (strip), 5.82 mm knob to knob (master), 6.21 mm (group). Cut-outs unchanged.
- **3D model:** rebuilt with the new knob (Blender 5.2).

# Key caps and fader caps: proposal (2026-10-25)

The last panel parts with no order code: the PV caps on the 343 PVA2 keys and the 29 fader caps.

## Key caps (C&K PV, round Ø7.4 × 7, snap-fit)

C&K makes four colours for the PVA series: PVRD red, PVGY grey, PVWH white, PVBK black (DigiKey / Mouser). There is
**no green cap**, but the model's ON key (SW4) is green.

**KC1. PV caps by function; ON becomes black.**

| Colour | Cap | Keys | Qty |
|---|---|---|---|
| Grey | PVGY | Ø, HPF, EQ, PRE 1-2 / 3-4 / 5-6, PAN, DIR (strip); EXT (master) | 193 |
| White | PVWH | routing L-R / 1-2 / 3-4 (strip); MIX ×2, 1-2, 3-4 (group) | 88 |
| Red | PVRD | PFL (strip); PFL, AFL ×2 (group); AFL ×2 (master) | 38 |
| Black | PVBK | ON (strip) | 24 |

- **ON:** the one black key on a strip. Its green LED shows the state, as now.
- **DIR:** goes from black to grey. The model had ON green and DIR black; DIR is a set-and-forget key, and two black
  keys on a strip would read alike.

## Fader caps (Sifam LK110 tang 01, the signed fader decision)

- **Sifam standard:** a black body with a white line (Sifam catalogue colour chart, "single colour slider knobs").
  Coloured bodies are made to order, 1,000 pcs minimum.
- **Distributors:** RS stocks the black 4/02 LK110 01 (pack of 5).
- **Other sources:** pot4audio's coloured Sifam caps are for a different lever. Generic 24 × 11 mm caps for an
  8 × 1.2 mm lever come in white / red / yellow, but nobody has measured one on the PTB's BP blade.

**KC2. Black Sifam caps, with a coloured-cap trial alongside.**
- **Order now:** 29 + spares of the Sifam LK111 01, black with a white line: the tang-01 socket the decision names.
  Use 02 LK110 01 (RS 281-7197) if the plain cap is the only one stocked.
- **Trial:** with the fader sample check that is already open (`panel_parts_drawings.md`), try a few generic white /
  red / yellow 8 × 1.2 caps.
- **If a trial cap fits** (no wobble on the 1.3 blade, sitting about 1 mm above the panel), use white on strips, red on
  groups and yellow on the master, the model's colours. Otherwise every fader stays black with a white line.

## Sign-off

Signed off by Ruslan on 2026-10-25: KC1 and KC2 as proposed.

- [x] **KC1** PV caps PVGY / PVWH / PVRD / PVBK by function as in the table; ON black, DIR grey.
- [x] **KC2** Sifam black LK111 01 fader caps now, plus a coloured-cap trial at the fader sample check.

## Applied (2026-10-25)

- `panel_layout.py`: ON black and DIR grey, and every fader cap black in the model (the coloured caps only if the trial
  passes).
- `offboard_bom.md`: PV cap codes with counts; fader cap code and the trial.
- The panel drawings are unchanged: cap colours aren't on them. The 3D model was rebuilt.
