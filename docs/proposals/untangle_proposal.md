# Untangling the ratsnest (2026-10-27)

**Status:** the turns are placement only and applied, as Ruslan asked. The unit / channel swaps are a measured
sign-off list, and none is recommended.

## The measure

`tools/ratsnest.py` (KiCad Python) computes, per signal net, the Euclidean minimum spanning tree of its pads (the
ratsnest), and counts the crossings between different nets' edges.
- **What it leaves out:** grounds and supply rails, which go to the GND / GND2 layers and the rail corridor; their
  ratsnest lines say nothing about how they will be routed.
- **Incremental scoring:** a 5 mm grid makes it fast. `Rats.trial()` scores a change on the touched nets only.
- **Checked:** the incremental counts match a full recount on 40 random turns, and the total matches a brute-force
  count of every edge pair. A first version counted a crossing once per shared grid cell (inflating long edges), and
  its numbers were wrong, so this check is part of the record.

**Before**, signal nets only:

| Board | Signal nets | Ratsnest | Crossings |
|---|---|---|---|
| Strip | 174 | 8079 mm | 1292 |
| Group | 152 | 8463 mm | 1674 |
| Master | 346 | 13568 mm | 2419 |

## Turns (applied, placement only)

**The search:** every two-pad SMD part is turned in place, about its own origin, by 90°, 180° or 270°.
- **Excluded:** C0G caps and the parts E9 / E10 / E11 placed at a pin, so none leaves its pin. Through-hole parts are
  excluded too; they don't turn about their centre.
- **Collisions:** a 180° turn keeps the courtyard exactly. A 90° / 270° turn passes the same collision checks as the
  E9 probe.
- **Acceptance:** a turn is kept if it removes crossings, adds at most 1 mm of ratsnest, and lengthens no HighZ net.
  Greedy, until a pass finds nothing.

| Board | Parts turned (180° / 90°–270°) | Crossings | Ratsnest |
|---|---|---|---|
| Strip | 36 (30 / 6) | 1292 → 1211 (−6.3 %) | 8079 → 8031 mm |
| Group | 32 (27 / 5) | 1674 → 1600 (−4.4 %) | 8463 → 8426 mm |
| Master | 79 (64 / 15) | 2419 → 2261 (−6.5 %) | 13568 → 13473 mm |

**How it's built:**
- **The placer:** `placer.py` takes `turns` ({ref: degrees}), applied after packing and the moves, with the same
  refusal as `moves`. The lists are `TURNS` in `place_strip.py`, `place_group.py` and `place_master.py`.
- **Re-placed:** no part moved, only the listed ones turned.
  - **DRC / parity:** 0 violations, 0 parity issues.
  - **Links:** every footprint linked.
  - **Rules:** `tools/netrules.py` unchanged; all 13 rules still fire.
  - **Report:** decouplers unchanged. High-Z inputs: strip 8.2 → 8.1 median, 25 → 24 over 6 mm; group 7.8 → 7.5;
    master 8.1 → 7.9, 76 → 72.
- **Input nets over 20 mm:** strip 9 → 8, master 21 → 19, group 3.
- **The C0G caps:** unchanged.

**`emc_check.py`:** the closest couplings mostly move apart:
- strip U16A− 3.9 → 5.8 mm from U4's output, U3A− 4.1 → 4.7, U6B− 7.0 → 8.8;
- master CRSB_LO 3.4 → 4.8, ML_DETO 3.7 → 4.8, U18B+ 5.4 → 5.8;
- one comes closer: group U15A− 10.8 → 9.6 mm from D2's anode.

**A side fix:** `placer.py` refused to rebuild a board that "contains routing or zones", and the RAILS rule area
counts as a zone. It now ignores rule areas, which aren't copper; real zones and tracks still stop it.

## Unit / channel swaps (sign-off list, none recommended)

**The candidates** (they change the netlist):
- **Dual op-amps and comparators:** OPA1612 / OPA1656 / TL072 / LM393, A ↔ B (pins 1, 2, 3 ↔ 7, 6, 5).
- **DG413:** SW1 ↔ SW4 (the normally-open pair), SW2 ↔ SW3 (the normally-closed pair), or both. All four of a strip
  DG413's inputs share one control line, so either is electrically identical.

**How each was scored:** after the turns. A swap is blocked if any C0G cap or E9–E11 part on a touched net would end
more than 1 mm farther from its pin; that part would then need re-placing.

| Board | Swap | Crossings | Ratsnest | Blocked by |
|---|---|---|---|---|
| Master | U17 A ↔ B (EXT receiver followers) | −12 | +25 mm | C90, C91, C96, C97 |
| Master | U30 A ↔ B (meter detector, TL072) | −5 | +2 mm | C161 |
| Master | U18 A ↔ B | −5 | +14 mm | C102, C103, C104 |
| Master | U10 A ↔ B | −3 | −2 mm | — |
| Master | U22 A ↔ B (PFL comparators) | −1 | +3 mm | — |
| Strip, group | none improves | | | |

**Why none is recommended:**
- **The gains are small:** at most 12 crossings out of 2261.
- **The bigger ones cost:** they need their stability caps moved again, and some lengthen the ratsnest.
- **Placement already did this:** the placer's `attach` mode puts each part beside the pin of the unit it belongs to,
  so the unit assignment already suits the placement.
- **One free swap:** U10 is clean, but 3 crossings don't justify a netlist change.

The scripts that searched (turns, swaps, swap with re-placement) are scratch, built on `tools/ratsnest.py`. Its
`Rats.trial()` / `commit()` are the API to try a change and keep it.
