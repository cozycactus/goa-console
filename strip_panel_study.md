# Strip panel study — v4.0 channel at 8 HP, 12U vs 15U (October 2026)

Question: does the v4.0 channel (15 pots, 13 switches, 4 LEDs, 3 jacks, 100 mm fader) fit an 8 HP
Eurorack-style panel at 12U or 15U, with one or two pot columns? Result and the placement built from
it: `tools/place_strip.py` → `channel_strip_v4.kicad_pcb`.

## Fixed dimensions

| Item | Value | Source |
|------|-------|--------|
| 8 HP panel width | 40.3 mm (strip pitch 40.64) | Eurorack (Doepfer) |
| 12U / 15U panel height | 514.0 / 642.5 mm (4 × / 5 × 128.5) | Doepfer 3U = 128.5 mm |
| End-rail zone | ≈ 11 mm per end (holes 3 mm from the edge; 108–110 mm usable per 3U row) | Doepfer, sdiy wiki |
| Board width | 38 mm (1 mm clearance per side) | strip spec |
| Pot, RD901F | courtyard 13.8 × 12.8 mm, shaft 7.5 / 2.5 mm from pin 1; dual RD902F 16.3 mm wide | KiCad footprint, Alpha SLH-211-414 |
| Knob | ≤ 14 mm diameter with two columns 18 mm apart; ≤ 16 mm with one column | choice |
| PVA2 + PV cap | courtyard 10.3 × 9.7 mm, cap ø7.4; three per 38 mm row at 11 mm pitch | C&K PVA |
| Fader PTB0143 | body 128 mm, travel 100 mm; zone ≈ 130 mm | Bourns PTB |
| Jack, panel-mount | Neutrik NJ6FD-V, vertical, all plastic (PA shell, POM cap: isolated), panel hole 12 mm, panel 1.2–1.5 mm, courtyard 15.5 × 16 mm | Neutrik datasheet (neutrik.us) |

**Rear jacks are no longer possible.** Three right-angle NRJ6HF need about 47 mm of rear edge
(15.75 mm bodies) and the board is 38 mm wide. With the panel in a Eurorack-style frame there is no
rear apron anyway, so all three jacks go on the panel: two rows (line in | insert, direct out | Ø).

## Column height needed (panel top edge to bottom edge)

Pitches: pot rows 20 mm (one column) or 22 mm (two columns), switch rows 14–18 mm, jacks 40 mm
for two rows, fader 130 mm, 11 mm end rails.

| Layout | Needed | 12U (514) | 15U (642.5) | Board length |
|--------|--------|-----------|-------------|--------------|
| **One pot column** | ≈ 545 mm (15 pots × 20 = 300 in the column alone) | **does not fit** (31 mm over) | fits, ≈ 97 mm spare | ≈ 620 mm |
| **Two pot columns** | ≈ 466 mm (as placed: board 444 + rails 22) | **fits, ≈ 48 mm spare** | fits, ≈ 176 mm spare (wasted) | 444 mm |

Two-column rows (as placed, board y from the board's top end = panel y − 11):

| Board y | Left (x 10) | Right (x 28) |
|---------|-------------|--------------|
| 12 | LINE IN jack | INSERT jack |
| 32 | DIRECT OUT jack | Ø switch |
| 54 | GAIN | OL LED |
| 76 | HF | HPF switch |
| 98 | HI-MID gain | HI-MID freq (dual) |
| 120 | LO-MID gain | LO-MID freq (dual) |
| 142 | LF | EQ switch + LED |
| 166 / 188 / 210 | AUX 1 / 3 / 5 | AUX 2 / 4 / 6 |
| 230 | PRE 1-2, PRE 3-4, PRE 5-6 (x 6 / 17 / 28) | |
| 252 | PAN pot (dual) | PAN switch (246), DIR switch (258) |
| 274 | L-R, 1-2, 3-4 (x 6 / 17 / 28) | |
| 292 | PFL + LED | ON + LED |
| 308–436 | fader, slot centre 372 | bus header (bottom side, 305–346), post-amp |

## Frame: end rails only

A standard 4-row Eurorack case has rails at every 3U boundary. Under a single 12U panel that means
three more rail bands (≈ 20 mm each, rail depth close to the 11.5 mm PCB-to-panel gap), which the
board would have to clear: 444 + 60 = 504 mm against ≈ 492 mm between the end rails. It doesn't fit.
**Use a custom frame with rails (or cross-members) only at the two panel ends**, and the six M3
standoffs to hang the board from the panel.

## Recommendation

**12U, two pot columns, jacks on the panel (NJ6FD-V).** That is what `channel_strip_v4.kicad_pcb`
implements. 15U only makes sense for a single pot column, and it costs a 620 mm board and 128 mm
more panel per channel.

## Placement result (KiCad 10.0.7)

- 180 footprints + 6 M3 holes on 38 × 444 mm; zero tracks, vias and zones.
- DRC with `--schematic-parity`: 0 parity issues; no courtyard, clearance or placement errors.
  Remaining: 6 hole-clearance and 6 solder-mask items **inside KiCad's NJ6FD-V footprint** (its SN
  pad sits close to its own locating peg; library footprint, not placement), silkscreen warnings,
  376 unconnected items (placement only).
- Bottom side: 12 radial electrolytics, the bus header CN1, the spade CN4, the VCA socket J3/J4.

## Open checks

1. **NJ6FD-V height above the PCB** against the 11.5 mm panel gap. The Neutrik drawing wasn't
   available (neutrik.com down on 2026-10-22). If the jack's panel shoulder is higher, the jack rows
   need local spacers or a short jack board.
2. Knob diameter ≤ 14 mm in the two-column rows.
3. Routing LEDs still need a 4PDT switch (spec v4.0 §13).
4. C-law dual 100K and B10K centre-detent pot availability; PVA2 latched-throw sense.

Sources: [Neutrik NJ6FD-V datasheet](https://www.neutrik.us/en-us/product/nj6fd-v.pdf),
[Mouser NJ6FD-V](https://www.mouser.com/ProductDetail/Neutrik/NJ6FD-V),
[Eurorack (Wikipedia)](https://en.wikipedia.org/wiki/Eurorack), [SDIY wiki: Eurorack](https://sdiy.info/wiki/Eurorack).
