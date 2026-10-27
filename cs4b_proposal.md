# CS4b: the jack-link clamps on the group and master boards (proposal, 2026-10-27)

**Signed off by Ruslan on 2026-10-27 (as proposed: D7-D20 on every group, D79-D102 on the master) and applied the same
day; see "Applied" at the end.** The change is `cs4b_proposal.patch`. It touches tools only: `master_lib.py`,
`gen_group.py`, `gen_master.py`, `place_group.py` and `place_master.py`.

**Simulations:**
- `sim/review/cs4/jack_protect.py`: the receivers and inserts, as for the strip.
- `sim/review/cs4/jack_protect_mg.py` (new): the DRV135 balanced outputs.

## 1. What

Strip v5.2 (`cs4_proposal.md`) clamps the strip's five jack-link signals to ±VA at CN3. CS4b does the same on the
other ribbon boards: one Nexperia BAV199 per signal on the jack-board link, at the main board's header, ahead of every
series part. Pin 3 goes to the signal, pin 2 to +VA, pin 1 to −VA.

| Board | Link | Clamped signals | Clamps |
|---|---|---|---|
| Group (×4) | CN3 (2×8), CN4 (2×5) | return 1 and 2 legs (8); sub insert send and return; sub out and aux out legs (DRV135, 4) | 14: D7-D20 |
| Master | CN5 (2×20) | EXT legs (4); both mix inserts' sends and returns (4); main L / R / mono legs (relay side, 6); aux 5 / 6 and C/Room legs (DRV135, 8); phones L / R | 24: D79-D102 |

Grounds, CHASSIS and PHONESGND on the links are left alone. Console total: 4 × 14 + 24 = 80 BAV199.

## 2. Why each kind

**Receivers and inserts.** `master_lib.receiver()` and `insert()` are the strip's circuits, so the strip's results hold.
At 8 kV contact the receiver op-amp takes 0.09 A instead of 9.6 A, and the insert return about 0 instead of 5.9 A
(`jack_protect.py`).

**DRV135 balanced outputs** (group sub / aux out; master aux 5 / 6, C/Room, and main L / R / mono through their relays).
Each leg's jack-side node is the 10 µF NP 25 V coupler and the DRV135's Sense pin, inside its feedback network.

| `jack_protect_mg.py` | As built | BAV199 at the link |
|---|---|---|
| 48 V phantom / 6K8 on a leg: the coupler / the Sense pin's internal node | **47.7 V / 47.2 V** | 17.7 V / 17.5 V |
| 8 kV contact on a leg: current into the DRV135's output pin | 22.8 A | 5.9 A (clamp 20.7 A, I²t 7.1e-6 A²s) |
| 4 kV contact | 11.4 A | 3.3 A (clamp 10.0 A, 1.7e-6 A²s) |

**Phantom.** An XLR main output into a mic input with phantom on is a common mistake. As built it puts 48 V across a
25 V coupler and onto the DRV135's Sense pins. With the clamp it can't.

**ESD on an output.** The clamp helps 4×, but the DRV135's output pin still takes several amps: nothing but the 10 µF
and ~20 nH of track separates it from the clamp.

**Phones.** LME49600 → 2R2 → mute relay → jack. The clamp catches ESD on the most-plugged jack. A phones signal
(±15 V at most) never reaches the clamp's ±17.5 V threshold.

## 3. Not in this patch: CS4c, a resistor inside each DRV135 loop

**What:** 10-22 Ω between each DRV135 output pin and its 10 µF, inside the Sense loop. The driver's feedback removes it
from the output impedance.

**What it would buy** (`jack_protect_mg.py` variant, with the clamp):
- 22 Ω: 0.84 A at 8 kV, 0.63 A at 4 kV into the output pin, against 5.9 / 3.3 A.
- 10 Ω: 1.5 / 0.87 A.

**Why not here:** it changes the DRV135's loop, so it needs the TI-model stability run first (`sim/review/master`,
`master_group_review.md`). A proposal of its own if you want it.

## 4. Schematic and placement (trial)

**Generators:**
- `master_lib.link_clamps()` makes the clamps after every other part, so they take the next free D references and no
  existing reference moves. Checked pin by pin against the committed netlists: only the new parts differ.
- Each clamp is its own fragment. Group: page 11 ("JACK LINK CLAMPS, POWER AND GROUNDS"), 12 pages. Master: pages 26-27,
  30 pages.

**Placement:**
- By `moves_only` (place_master.py gains it), at probed free spots. A script blocked spots the placer's guard refused
  and re-probed them; one group clamp needed it.
- Distance to the header pin: group 8.2 / 13.0 / 20.2 mm (min / median / max), master 5.9 / 9.7 / 11.8 mm. That is
  a few to ~20 nH, against the link's ~100 nH.
- Nothing else moved on either board.

## 5. Checks on the trial tree (`tools/check_all.py`, 59 / 59)

- **Group:** 781 pins / 279 parts; **master:** 1758 pins / 603 parts.
- **Both:** 0 mismatches, check_fp 0, ERC 0, parity DRC 0 / 0, every footprint linked, route_check 0.
- **Jack boards:** unchanged.
- **Sims:** `sim_netlist` 39/39, `sim_console` 35/35.
- **BOM:** +14 BAV199 per group, +24 on the master: 80 for the console, ~$0.05 each.

## Sign-off

- [x] **CS4b** as proposed: D7-D20 on every group, D79-D102 on the master. Ruslan, 2026-10-27.
- [ ] Also work up **CS4c** (a resistor inside each DRV135 loop, with the TI stability run).
- [ ] Neither.

## Applied (2026-10-27)

- **Applied:** the patch.
- **Regenerated and re-exported:** group and master netlists, BOMs, PDFs and `order_bom.csv` (BAV199: 200 + 10
  spares, strip, group and master together).
- **Re-placed:** both boards; against the committed boards only the clamps are new.
- **Project files:** netrules re-written; the four `.kicad_pro` files kept their committed form. The master jack
  board's netlist now carries its net classes.
- **Documents:** master spec (Part 1 note, §7), CLAUDE.md. CS4c is not started.

