# Decouplers at their supply pins (proposal E11, 2026-10-27)

**Status: proposal, not signed off.**
- **What changes:** placement only, after E9 / E9b / E10. No netlist, part or BOM change.
- **The trial:** `decouplers_proposal.patch`, a `MOVES.update` in `place_strip.py`, `place_group.py` and
  `place_master.py`. The committed boards are unchanged.

## Why

The placer's limit for a decoupler is 5 mm from its cap pad to the supply pin. The boards still had caps over it:
- **Strip:** 14, up to 10 mm. Mostly the DG413s' three supplies each (V+, V−, VL) and the OPA1656 followers U16.
- **Group:** 2.
- **Master:** 27. Most sit at 5.0–5.4 mm (the meter comparators' caps); four are over 6 mm.

A decoupler's trace to its pin is inductance in the supply loop, about 1 nH per mm. It matters for an OPA1612 / OPA1656
(80 / 53 MHz) and for the DG413's switching edges.

## E11 (proposed)

The 21 SMD decouplers more than 5.5 mm from their pin move to it. They went through the same probe as E9 (both sides,
courtyards, through-hole pads, holes, board edge), placed in turn and moved after packing:

| Board | Cap | Supply pin | Before, mm | After | Side |
|---|---|---|---|---|---|
| Strip | C60 | U11 pin 4 (DG413) | 10.0 | 0.05 | B |
| Strip | C57 | U10 pin 4 (DG413) | 10.0 | 0.05 | B |
| Strip | C61 | U11 pin 12 | 9.1 | 0.05 | B |
| Strip | C58 | U10 pin 12 | 9.1 | 0.05 | B |
| Strip | C92 | U16 pin 8 (OPA1656) | 8.6 | 1.6 | B |
| Strip | C93 | U16 pin 4 | 8.5 | 1.5 | B |
| Strip | C25 | U3 pin 4 | 8.1 | 2.0 | F |
| Strip | C59 | U11 pin 13 | 7.6 | 0.55 | B |
| Strip | C56 | U10 pin 13 | 7.6 | 0.55 | B |
| Strip | C54 | U9 pin 4 (DG413) | 7.6 | 0.05 | B |
| Strip | C53 | U9 pin 13 | 6.2 | 0.05 | B |
| Strip | C98 | U17 pin 8 (LM393) | 6.1 | 0.05 | B |
| Strip | C55 | U9 pin 12 | 6.1 | 0.55 | B |
| Group | C43 | U7 pin 5 | 6.2 | 1.8 | F |
| Master | C193 | U44 pin 4 | 9.8 | 0.3 | B |
| Master | C180 | U38 pin 3 | 7.1 | 0.05 | B |
| Master | C150 | U28 pin 3 | 6.4 | 0.05 | B |
| Master | C116 | U20 pin 13 | 6.1 | 2.7 | B |
| Master | C58 | U11 pin 8 | 6.0 | 0.05 | B |
| Master | C31 | U5 pin 4 (fader post-amps) | 5.8 | 2.7 | B |
| Master | C74 | U14 pin 5 | 5.8 | 2.5 | F |

**Not moved:**
- **C144 / C145, the LME49600's 10 µF ±VP bypasses (11.5 / 6.4 mm):** they are through-hole. Within 8 mm no spot
  keeps their leads clear of U27's pads and courtyard. The first trial put C144 under U27, and its leads would have
  shorted U27's pads through the board.
  - That trial found a gap in the new `moves` guard, now closed: the guard refuses a through-hole part whose leads meet
    another part's pad or courtyard on either side.
  - The probe got the same lead check.
- **Caps at 5.0–5.5 mm:** the meter comparators' and the like, not worth a move.

## Measured (trial vs the committed E10 boards)

| | Strip | Group | Master |
|---|---|---|---|
| Parts moved | the 13 caps | C43 | the 7 caps |
| DRC / parity | 0 / 0 | 0 / 0 | 0 / 0 |
| Decouplers median / max / over 5 mm | 3.1 / 10.0 / 14 → 2.5 / 5.4 / 1 | 2.9 / 6.2 / 2 → 2.9 / 5.1 / 1 | 3.1 / 11.5 / 27 → 3.1 / 11.5 / 20 |
| Signal nets | unchanged | unchanged | unchanged |
| Supply nets, MST mm | +5VL 182 → 168, +VA 558 → 547, −VA 562 → 554, GNDA 1048 → 1033, GNDD 544 → 536, +VL 358 → 362 | unchanged | −VA 744 → 725, −VP 211 → 207 |
| `emc_check.py` | +5VL's pad (C61) no longer 5.9 mm from U2B− (now off the twelve closest) | unchanged | unchanged |

- **Unchanged on every board:** the input nets (E10) and the C0G caps (E9).
- **On the master:** the maximum stays 11.5 mm, C144 (see above).

## Sign-off

- [ ] **E11:** the 21 decouplers above at their supply pins, by `moves`.
