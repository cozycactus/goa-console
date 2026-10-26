# Strip stability caps at their pins (proposal E9, 2026-10-26)

**Signed off by Ruslan on 2026-10-27 and applied the same day; see "Applied" at the end.**
- **What changes:** placement only, like E1–E5. No netlist, part or BOM change.
- **The change:** `stab_caps_proposal.patch` (`tools/place_strip.py`).

## Why

The v4.1 review (`strip_parts_review.md` T1–T8) added small C0G caps to the strip's op-amps:
- at + inputs, against the source impedance and the op-amp's input capacitance;
- across feedback resistors.

Its margins assume each cap sits at its pin. The packer placed them by their net's other parts instead, so several are
far from the pin they serve:

- **C84** (100p, the T8 fix that brought U7B from 27–40° back to ~70°): 22 mm from U7's pin 5.
- **C83** (22p, the cap that took U8A from 19° to 70° with a short direct-out lead): 10.5 mm.

Between such a cap and its pin, the trace adds inductance and picks up whatever runs alongside. The cap stops working
at RF, and its loop with the pin becomes an antenna.

`tools/placer.py`'s report didn't show most of these. It gives one row per input (the farthest part), so a resistor
further out hides the cap. This check lists every C0G cap on an op-amp input, pad to pin.

## E9 (proposed)

Twelve caps move to their pins. Nine go on the bottom side under their op-amp, as E2 / E3 did for U16's input network
and the soft-mute JFETs.

| Cap | Value | Pin | Pad to pin, mm, before (side) | After (side) |
|---|---|---|---|---|
| C84 | 100p | U7B + (insert return) | 22.1 (F) | 5.8 (F) |
| C41 | 33p | U5B − (HF EQ feedback) | 17.3 (F) | 1.9 (B) |
| C37 | 22p | U1B − (gain stage feedback) | 15.8 (F) | 2.8 (B) |
| C71 | 10p | U6B − (across R58 22K) | 14.9 (F) | 1.6 (B) |
| C80 | 10p | U3A + (pan R) | 10.6 (F) | 1.4 (B) |
| C83 | 22p | U8A + (direct out) | 10.5 (F) | 0.0 (B) |
| C78 | 33p | U1A + (receiver) | 9.0 (F) | 0.0 (B) |
| C75 | 22p | U12A + (KHN summer) | 9.0 (F) | 0.0 (B) |
| C86 | 10p | U5A − (HPF summer) | 8.1 (F) | 3.6 (F) |
| C70 | 10p | U6A − | 7.9 (F) | 2.6 (B) |
| C85 | 22p | U5A + (HPF summer) | 7.1 (F) | 1.3 (B) |
| C81 | 10p | U3B + (mute buffer) | 6.3 (F) | 2.0 (F) |

- **Feedback caps** (C37, C41, C70, C71, C86): placed for the worse of their two pads, the − input and the output
  (or the far end of the resistor they bridge).
- **0.0 mm:** the cap's pad sits under the pin's pad on the other side, so one via joins them.
- **How the spots were found:** a probe placed each cap in turn at the nearest free spot. It checks courtyards on
  that side, every through-hole pad, 3 mm around the M3 holes and the board edge. Each cap was placed before the next
  probe, so the twelve don't collide.
- **C84:** U7 has no free top or bottom spot nearer than 5.8 mm. R99 holds the slot beside pin 5, and C84's C0G
  footprint doesn't fit there.

**The packer cascade:** freeing those twelve spots made the greedy packer re-shuffle about 90 other parts:
- R104 by 66 mm;
- C48 off the board;
- C49, U7A's film coupler, 20 mm from its pin;
- the input's 1M legs to the other edge.

So `place_strip.py` holds 86 parts where PAN1 placed them (`HOLD`, explicit coordinates). Only the twelve caps move.

## Measured (trial board vs the committed PAN1 board)

- **Parts moved:** 12, only the caps above.
- **DRC / parity / links:** 0 violations, 0 parity issues, 290 / 290.
- **Placer report:** decouplers unchanged (3.1 / 10.0 / 14). High-Z inputs 10.4 / 258.6 / 28 → 8.5 / 258.6 / 25; the
  max is MET1's SIG_B line, by design (E1).
- **Every C0G cap on an op-amp input** is now ≤ 6.3 mm from its pin (C73 / C74, as before). The worst was 22.1.
- **Nets:** every net the caps touch is shorter (U6B− 40 → 21 mm, U7B+ 31 → 14, U1B− 38 → 22, U5B− 49 → 39, U12A+
  38 → 29, U3A+ 23 → 15, U6A− 34 → 29), except U5A− (27 → 31). GNDA is 1060 → 1066 (the caps' ground pads). Total
  signal MST 9572 → 9470 mm.
- **`emc_check.py`:** unchanged: no new coupling, entry runs and supply entry as before.

## What it does not change

- **Netlist, BOM and stability numbers.** The TI deck has no trace model, so it reads the same. The change makes the
  board closer to what the deck assumes.
- **The other 278 parts.**

## Sign-off

- [x] **E9:** the twelve stability caps at their pins, the rest held in place.

## Applied (2026-10-27)

- **Board:** the patch applied; the strip re-placed identically to the trial (12 parts moved against PAN1, none
  against the trial board).
- **Checks:** 0 DRC violations, 0 parity issues, 290 / 290 and 8 / 8 footprints linked. `emc_check.py` output unchanged.
  Every C0G cap on an op-amp input ≤ 6.3 mm from its pin.
- **Exports and docs:** `render/strip.json` re-exported; the spec §16, `routing_guide.md` (stability caps) and CLAUDE.md
  updated.
