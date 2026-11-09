# Wing power: a third +V conductor and a larger +V PTC (proposal, 2026-10-25)

**Signed off by Ruslan on 2026-10-25 (W1 and W2 as proposed) and applied the same day; see "Applied" at the end.**
W1 changes the earlier decision that the bus pinout leaves pin 34 (+48 V on the Delta) unconnected.

## Why

The motherloom feeds each wing from the master: 12 strips and 2 groups through two ribbon conductors per rail. Only
the master end of a conductor carries the wing's whole current through a contact (its IDC socket blade and the
header pin). Along the wing the copper wire passes straight through each socket. The relevant ratings:

- **Würth WR-BHD female IDC socket** (the 34-way 61203423021): **1 A per contact**. The 61203421621 box header is
  in a 3 A family. The socket is the limit.
- **Bourns MF-RX185/72 wing PTC** (datasheet rev. W, thermal derating table): hold 1.85 / 1.50 / 1.33 A at
  23 / 40 / 50 °C.

The wing's +V current, from master spec §27:

| Case | +V per wing | Per contact (2 per rail) | MF-RX185/72 hold used, 40 / 50 °C |
|---|---|---|---|
| Typical, strip v4.4 | 1.34 A | 0.67 A | 89 / **101 %** |
| Worst corner (max IQ, every LED), accepted 2026-10-25 | 1.92 A | **0.96 A** | **128 / 144 %** |

- **Typical load.** At 50 °C a wing's typical load already sits at the PTC's hold. Inside a closed tub in a warm
  room, a nuisance trip of a whole wing is possible in normal use.
- **Worst corner.** Each contact is at its 1 A rating, and the PTC is past hold even at room temperature.
- **Why the bigger PTC was rejected before.** On two contacts the MF-RX250/72 would let 1.25 A per contact through
  at hold (§25).

−V is less pressed. A wing draws about 1.05 A typical: 0.52 A per contact, and 70 / 79 % of hold at 40 / 50 °C. At
maximum IQ it draws about 1.3 A, 98 % of hold at 50 °C. It has no LED load, because the LEDs run from +VL, which is
taken from +V. It keeps two conductors and the MF-RX185/72.

## Proposal

**W1. Pin 34 becomes a third +V conductor.** Pin 34 sits next to +V (pins 32 and 33). On the Delta it carries
+48 V phantom; here it is unconnected on every module.
- **Change:** pin 34 on +VBUS on every strip and group header, and on the master's CN2 / CN3 (the wing's +V after
  its PTC).
- **Effect:**
  - typical 0.45 A per contact, worst corner 0.64 A;
  - one third less ribbon drop on +V.
- **Cost:**
  - a real Delta module plugged into the loom would see +17 V where it expects +48 V. That is harmless, and Delta
    modules are already incompatible (4K7 summing);
  - the jig's master stub and load board follow the same pinout.

**W2. +V wing PTCs become MF-RX250/72; −V keeps the MF-RX185/72.** Data from the Bourns MF-RX/72 datasheet:

| Part | Hold / trip, 23 °C | Hold at 40 / 50 °C | R1max | Body A × B max | Lead spacing |
|---|---|---|---|---|---|
| MF-RX185/72 | 1.85 / 3.7 A | 1.50 / 1.33 A | 0.19 Ω | 15.18 × 21.18 mm | 5.1 mm |
| MF-RX250/72 | 2.50 / 5.0 A | 2.03 / 1.80 A | 0.13 Ω | 17.84 × 23.84 mm | 10.2 mm |

With W1 and W2 together:
- **Hold used:** typical 66 / 74 % at 40 / 50 °C; worst corner 95 / 107 %.
- **Per contact at the 23 °C hold:** 0.83 A, within the socket's 1 A, so the reason for rejecting the MF-RX250/72
  no longer applies.
- **Fault case unchanged:** a pin 31/32 short still puts 34 V across the PTC, which is why both PTCs stay 72 V parts.
- **Footprint:** the MF-RX250/72 needs a new one (10.2 mm lead pitch, 2.7 mm wider body). F1 / F3 (+V) have to be
  re-fitted on the master's power entry. The left pair currently ends 0.3 mm from the 4 mm edge channel, so this needs
  a placement trial before it can be confirmed.

**Alternative (W2 only, no pinout change).** Keep two contacts with an MF-RX250/72 on +V. This fixes the nuisance
trip, but the contacts can then carry up to 1.25 A each before the PTC is even at hold. Not recommended.

## What applying it would touch

- **Generators:**
  - the `hdr` pin 34 in gen.py, gen_group.py, the master's motherloom headers and the jig;
  - the F1 / F3 symbol, MPN and footprint;
  - the `tools/footprints.py` footprint and the `tools/models3d/bourns_mfrx.py` model for the 250.
- **Placement:** `place_master.py`, with F1 / F3 re-fixed; strip and group headers keep their place.
- **Specs:**
  - console_architecture.md §2, the bus pinout;
  - master spec §25 / §27;
  - strip spec §2.4;
  - CLAUDE.md, the decision.
- **Checks:**
  - `sim_console.py`: ribbon conductor 34 is already modelled, so it carries its share once connected;
  - verify, ERC, parity DRC and the placement reports.

## Sign-off

- [x] **W1** Pin 34 = third +V conductor on the motherloom.
- [x] **W2** +V wing PTCs MF-RX250/72 (new 10.2 mm footprint), −V stays MF-RX185/72.

## Applied (2026-10-25)

- **Headers:** pin 34 on +VBUS on the strip and group, and on the master's CN2 / CN3. Both jig boards carry their
  `plus` net on it. The master's single-pin P48V_NC nets are gone.
- **Parts:** F1 / F3 are MF-RX250/72 with a new footprint, Fuse_Bourns_MF-RX250-72_Radial_P10.16mm (`tools/footprints.py`),
  and a 3D model (`tools/models3d/bourns_mfrx.py`, the lead pitch now a parameter). F2 / F4 stay MF-RX185/72.
- **Placement:** the 250's wider body and 10.16 mm pads disturbed the U11 area wherever the old row put them (54 parts
  moved). So both spots were searched against every other part's courtyard and pads, with the packer's 0.3 mm gap and
  the keep-outs:
  - F1 stays in its row, 1.2 mm higher;
  - F3 stands vertical by the right edge at y 230–249.
  Result: only F1, F3 and 14 parts that took the old F3 spot moved, and the master's report is unchanged
  (3.1 / 10.5 / 26 and 8.2 / 38.5 / 75). Strip, group, jig and every jack board moved 0 parts.
- **Checks:**
  - every schematic 0 mismatches, check_fp 0, ERC 0;
  - `sim_netlist.py` 37/37, `sim_console.py` 32/32;
  - parity DRC 0 violations on every main and jig board, 0 parity issues on all eight; the jack boards show only the
    NJ6FD-V's own items.
- **Not done:** the jig's master stub keeps its MF-RX160/72s (four strips).
