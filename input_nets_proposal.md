# Shorter high-impedance op-amp input nets (proposal E10, 2026-10-27)

**Status: proposal, not signed off.**
- **What changes:** placement only, after E9 / E9b. No netlist, part or BOM change.
- **The trial:** `input_nets_proposal.patch`, a `MOVES.update` in `place_strip.py`, `place_group.py` and
  `place_master.py`. The committed boards are unchanged.

## Why

E9 / E9b put the stability caps at their pins. The input nets themselves are the next sensitive copper: an op-amp's
− input with its resistors (a summing node or virtual earth), or a + input fed through a resistor. These are what
picks up RF and adds stray capacitance. After E9b:
- **Strip:** 17 of these nets are over 20 mm (Manhattan MST of their pads), the longest 39 mm.
- **Group:** 10 over 20 mm, also up to 39 mm.
- **Master:** 23 over 20 mm, but most of those are DC: the flasher, VREF6, the meter ladder taps and the comparator
  inputs.
- **Jig master stub:** 1 net over 20 mm, at 22 mm: already fine.

The placer report can't show these. It gives the farthest part per input, but a net of four parts can be long even
when no single part is far.

## Method

A scratch script (not in the repo) did the search:
- **Scope:** for each audio input net over about 20 mm, try moving each SMD passive on the net to a free spot within
  10 mm of the pin, top or bottom. "Free" means clear of courtyards on that side, through-hole pads, 3 mm around the
  holes and the board edge.
- **Objective:** MST(input net) + 0.5 × growth of the part's other net.
- **Acceptance:** a move is kept only if the input net shrinks by ≥ 5 mm and the other net grows by less than that.
- **Exclusions:** C0G caps, so a stability cap never leaves its pin. A first run moved the group's C9 from 5.3 to
  10 mm from U2's + input, so that rule was added.
- **Order:** nets are taken greedily in order; each move is placed before the next probe. The moves go through the
  placer's `moves`, so no other part re-packs.

## E10 (proposed)

| Board | Input net (pin) | Before, mm | After | Part moved |
|---|---|---|---|---|
| Strip | U5B − (HF EQ summing node) | 39 | 28 | R50 |
| Strip | U13B − | 35 | 20 | R92 |
| Strip | U5A − (HPF summer) | 31 | 19 | R103 |
| Strip | U6A − | 29 | 16 | R55 |
| Strip | U12A + (KHN summer) | 29 | 15 | R85 |
| Strip | U13B + | 28 | 19 | R94 |
| Strip | U7A − | 24 | 11 | R67 |
| Strip | U1A + (receiver) | 24 | 12 | R9 |
| Strip | U13A − | 24 | 14 | R57 |
| Group | U9B − (return receiver) | 39 | 13 | R57 |
| Group | U9B + | 36 | 19 | R55 |
| Group | U9A − | 26 | 13 | R53 |
| Group | U6B + | 25 | 18 | R32 |
| Group | U8A + | 24 | 17 | R43 |
| Group | U2A + | 22 | 15 | R10 |
| Group | U8B − | 22 | 16 | R46 |
| Master | U5A − (fader post-amp L) | 27 | 13 | R33 |
| Master | U5B − (fader post-amp R) | 27 | 20 | R38 |

**No move found** (none saves 5 mm):
- strip U12A − (25 mm);
- group U13B + (30 mm);
- master U5A + / U5B + (25 / 28 mm, the fader wipers' coupling network).

## Measured (trial vs the committed E9 / E9b boards)

| | Strip | Group | Master |
|---|---|---|---|
| Parts moved | the 9 resistors | the 7 resistors | the 2 resistors |
| DRC / parity | 0 / 0 | 0 / 0 | 0 / 0 |
| Footprints linked | 290 / 290 | 263 / 263 | 579 / 579 |
| Input nets over 20 mm | 17 → 9 | 10 → 3 | 23 → 21 |
| Nets longer | none | none | none |
| Signal MST total, mm | 9470 → 9342 | 9824 → 9724 | 16624 → 16594 |
| Worst C0G cap to pin | 6.3 mm (unchanged) | 6.1 mm (unchanged) | 6.4 mm (unchanged) |
| Placer report, high-Z inputs | median 8.5 → 8.2 mm, rest unchanged | unchanged | unchanged |

**`emc_check.py`:**
- strip U5B − moves from 7.6 to 13.6 mm from U4's comparator output;
- group U9A − moves from 7.0 to 15.1 mm from D3's anode;
- nothing comes closer, and the master is unchanged.

The other nets the moved parts touch got shorter too: strip SW11 / C70 nets, group RT_R 41 → 24 mm, master C37's
net 26 → 16, and GNDA on the strip and group.

## Sign-off

- [ ] **E10:** the 18 resistor moves above (strip 9, group 7, master 2), by `moves`.

If signed off, applying it means:
- apply the patch and re-place the three boards (identical to the trial);
- parity DRC, links and `emc_check.py`;
- re-export `render/*.json`;
- update `routing_guide.md` and CLAUDE.md.
