# Strip panel study — v4.0 channel at 8 HP, 12U vs 15U (October 2026)

Question: does the v4.0 channel (15 pots, 13 switches, 4 LEDs, 3 jacks, 100 mm fader) fit an 8 HP
Eurorack-style panel at 12U or 15U, with one or two pot columns? Result and the placement built from
it: `tools/place_strip.py` → `channel_strip_v4.kicad_pcb` (main board) + `jack_board.kicad_pcb`.

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

Two-column rows (as placed; y = panel y − 11; jack board y 0–43, main board y 44–444):

| Board y | Left (x 10) | Right (x 28) |
|---------|-------------|--------------|
| 12 | LINE IN jack (jack board) | INSERT jack (jack board) |
| 32 | DIRECT OUT jack (jack board) | (link header CN5, bottom of the jack board) |
| 50 / 54 / 61 | GAIN (54) | Ø switch (50), OL LED (61) |
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

- Main board: 176 footprints + 6 M3 holes on 38 × 400 mm (y 44–444). Jack board: J1, J2, J5, C8, C9,
  CN5 + 2 M3 holes on 38 × 43 mm (y 0–43). Zero tracks, vias and zones on both.
- DRC with `--schematic-parity`, both boards: 0 parity issues; no courtyard, clearance or placement errors.
  Remaining: 6 hole-clearance and 6 solder-mask items **inside KiCad's NJ6FD-V footprint** (its SN
  pad sits close to its own locating peg; library footprint, not placement), silkscreen warnings,
  unrouted connections (372 main, 17 jack board).
- Bottom side of the main board: 12 radial electrolytics, the bus header CN1, the link header CN3,
  the spade CN4, the VCA socket J3/J4. Bottom of the jack board: CN5, C8, C9.

## Jack depth: the jacks can't sit on the main board (found 2026-10-22, after placement)

A 1/4" plug goes about 30 mm into the jack (Switchcraft stereo plug: mating depth 30.2 mm), and
the jack's axis is perpendicular to the panel. Any 1/4" panel jack therefore needs about 25 mm
behind the panel. The NJ6FD-V body is reported as 12.8 × 15.0 × 24 mm behind the panel, with a
3.5 mm snout. That figure is second-hand, from Neutrik drawing nj6fd-v-3.dxf as quoted in a
public issue tracker; Neutrik's page returned 503, and its datasheet PDF has no drawing. Our
PCB is 11.5 mm under the panel, so **J1, J2 and J5 as placed in `channel_strip_v4.kicad_pcb`
cannot be built**. The pots, switches, LEDs and fader are unaffected.

Options:

| | Jacks | What changes | Cost |
|---|---|---|---|
| A | NJ6FD-V on a separate **jack board** (38 × ~44 mm) about 24 mm under the panel, held by the jack caps and 2 standoffs | Main board starts below the jacks (≈ 400 mm long); the Ø switch moves onto it; a 2 × 5 header on each board with a short IDC jumper (J1 T/R, J2 T/TN/R/RN, J5 T/R, GND) | A second small PCB per strip and a jumper; 1/4" jacks kept, isolated, no hand wiring |
| B | Panel-mount 1/4" jacks with solder lugs, wired to a header | Main board as A | About 72 jacks × 3–5 wires to hand-wire; slim isolated panel jacks with switching contacts are scarce |
| C | 3.5 mm TRS jacks (Thonkiconn class) directly on the main board | Jack footprints only | Eurorack-native and buildable at the 11.5 mm gap (height to confirm), but 1/4" synth outputs then need adapters |

Recommendation: **A**. Ruslan chose A on 2026-10-22, and it's implemented: `jack_board.kicad_sch` and
`jack_board.kicad_pcb`, link pinout in strip spec §16.4. Confirm the 24 mm figure with Neutrik's
DXF/STEP, or with a sample, before ordering: it sets the jack-board standoffs.

## Open checks

1. NJ6FD-V body height from Neutrik's drawing or a sample (sets the jack-board depth and standoffs).
2. Knob diameter ≤ 14 mm in the two-column rows.
3. Routing LEDs still need a 4PDT switch (spec v4.0 §13). Candidates found, datasheets not yet
   checked: C&K PHB4UEETS1A (PHB series, push-push, 1 A / 15 V; the 2-pole PHB is 7.4 × 26 × 10 mm,
   so the 4-pole is long), and generic Schadow-style 4PDT (34.9 × 7.6 × 12.3 mm, 3.2 mm pitch). A
   35 mm body along y doesn't fit the 18 mm between the routing row and the PFL row. The routing row
   would have to be re-laid.
4. C-law dual 100K and B10K centre-detent pot availability; PVA2 latched-throw sense.

Sources: [Neutrik NJ6FD-V datasheet](https://www.neutrik.us/en-us/product/nj6fd-v.pdf),
[Mouser NJ6FD-V](https://www.mouser.com/ProductDetail/Neutrik/NJ6FD-V),
[Eurorack (Wikipedia)](https://en.wikipedia.org/wiki/Eurorack), [SDIY wiki: Eurorack](https://sdiy.info/wiki/Eurorack).
