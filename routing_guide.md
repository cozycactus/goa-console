# Routing guide: strip, strip jack board, jig master stub, jig load board (2026-10-26, layers 2026-10-27)

Notes for routing the first boards to build: the jig and four strips. They are drawn from the placed boards (net lengths
are Manhattan minimum-spanning-tree estimates from the pads, as `tools/emc_check.py` measures them) and from
`emc_placement_study.md`, whose rules and sources apply throughout. Copper is Ruslan's, so this is advice, not a spec.
The net classes and DRC rules at the end are written into the projects by `tools/netrules.py`.

## Layers (`layer_study.md`, decided 2026-10-27; In2 as ground 2026-10-27)

**The strip, group and master main boards are 4-layer:**

| Layer | Use | Its return |
|---|---|---|
| F.Cu | parts, signals | In1, about 0.2 mm below |
| In1.Cu "GND" | a solid GNDA plane, unbroken. No tracks; no zone but ground | — |
| In2.Cu "GND2" | GNDA fill everywhere, except the rail corridor along the left edge, where the supply rails and GNDD run. Outside the corridor: no tracks at all | — |
| B.Cu | the bottom parts, signals | In2, about 0.2 mm above |

**Why In2 is ground, not power.** In the fab's standard 1.6 mm build, B.Cu is about 0.2 mm from In2 and about 1.3 mm
from In1 (thin prepreg on each outer pair, a thick core in the middle). A bottom trace's return current flows in In2,
right under the trace; above roughly 10 kHz it hugs the trace, and at RF entirely so. If In2 were split into supply
strips, a bottom trace crossing a gap would lose its return there, and the current would detour through the nearest
decoupler: a bigger loop, more pickup.
- **Ordering:** when you order, check the stackup has the thin dielectric on both outer pairs; JLCPCB's default 1.6 mm
  4-layer build does.

**The rail corridor (rule area RAILS)**, drawn by `placer.py` along the left edge, all the board's length: x 0.5–5.5 mm
on the strip and group, 0.5–6.5 mm on the master.
- **What runs in it:** on In2, ±VA, +VL / −VL, +5VL (the master adds ±VP / ±VM) and the GNDD spine, side by side.
  GNDD sits beside +VL / +5VL, which feed the logic and LEDs, so their currents go out and back together. Fill GNDA
  between them where there's room.
- **On B.Cu over it:** no HighZ / Entry / Bus track (DRC rule), because B.Cu there sits over the rails, not over
  ground.
- **Why the left edge:** fewest through-hole pins (22 / 25 / 28 in the band on the three boards, against 37 / 38 / 31 on
  the right). The rails pass the switch pins and the M3 holes H4 / H5 on their inner side.
- **Branches to the ICs:** a via at the corridor's edge, then across on F.Cu or B.Cu, straight to the decoupler's
  supply pad, which feeds the pin (E11). Not on In2, which stays whole outside the corridor (DRC rule).
- **Feeds into the corridor:** cross the board on an outer layer, as wide tracks (Power class, ≥ 0.5 mm).
  - **Strip:** from the filters R1–R4 by the bus header (right side, y ≈ 296–300).
  - **Group:** from the filters by its header.
  - **Master:** from the power entry in the middle (y 186–236). The master's GNDD / GNDM / PHONESGND leave the
    corridor the same way to their net ties at the star (NT1–NT4, x 33–46, y 208–220).
- **GNDD to NT1:**
  - **Strip:** NT1 is at (5, 351), at the corridor's edge.
  - **GNDD pads:** each takes a via to its spine.
  - **Clearance:** the spine keeps 0.5 mm from GNDA (DRC rule), including the GNDA stitching vias.

**Returns and vias:**
- **Every GNDA pad:** one via, next to the pad, joining In1 and In2 (and any outer fill).
- **Ground via beside every signal via:** a signal changing between F.Cu and B.Cu moves its return from In1 to In2.
  Put a GNDA via within about 1 mm of each such signal via so the return can follow. For HighZ, Entry and Bus nets
  this is a must; for the rest, wherever there's room.
- **Stitching:** stitch In1 and In2 (and any outer GNDA fill) every 10–15 mm over the whole board, along both edges of
  the corridor and along the board edges.
- **Prefer F.Cu for the sensitive nets** (HighZ, Entry, Bus): they sit over the unbroken In1. Use B.Cu for short runs
  and the bottom parts' connections.
- **Fills:** a fill on F.Cu or B.Cu is GNDA only. No GNDD fill anywhere.

**The jack boards, both jig boards and the PSU are 2-layer:**
- **Layout:** a bottom GNDA pour (CHASSIS on the jack boards as below), signals on top.
- **Jumpers:** short bottom jumpers, at right angles, with a ground stitching via at each end. Each one cuts the top
  traces' return, so keep them off HighZ and bus lines.

## Channel strip (main board)

### Ground and supply
- **GNDA:** the In1 plane and the In2 fill. The ribbon's even pins (2–16) and the spade (CN4) are where it leaves the board. Every
  op-amp decoupler's GNDA end takes its via at the cap.
- **GNDD:** the logic ground, for the LM393s (U4, U17), the LED switches (Q3–Q5), every LED cathode, the DG413 logic
  side, +5VL (D9 / C62) and the PVA2 pole-B returns. It runs as the spine in the rail corridor on In2 (see Layers).
  - It joins GNDA only at NT1, beside the spade.
  - No GNDA current through GNDD, and no LED current through GNDA.
- **±VBUS:** header pins 30–34 to the 10R filters R1–R4 (5–8 mm since E4). After them the rails are ±VA (op-amps),
  +VL / −VL (logic, LEDs) and +5VL from D9.
  - Strip current: about 104 mA on +V and 87 mA on −V.
  - ±VA reach 34–36 pads over about 560 mm. Run them on In2 in the rail corridor, with a branch on F.Cu / B.Cu to
    each decoupler. Not a daisy chain through decoupler pads.
- **GCANCEL:** header pin 26 to R5 (10R) at the spade. It carries no current; route it as a quiet signal next to
  ground.

### Keep these short and guarded (high-impedance or sensitive)

| Net | Length | Why | Rule |
|---|---|---|---|
| IN_T, IN_R (CN3 → R110 / R111, then U16 + via 220R) | 74–76 mm | balanced input, RF from the ribbon | a pair, with ground on both sides, away from everything below; on the ribbon conductors 1–2 with ground at 3 |
| U8B + input (pan buffer L, from the pan pot; PAN1, strip v4.8) | 24 mm | the pan wiper, up to 2.5 kΩ; was 165 mm from U2B at the fader end until PAN1 | RV8 pin 2 → C79 → U8 pin 5 directly, ground beside it. C79's ground end at U8's ground |
| FPIN (fader wiper → U2A) | 72 mm | fader wiper, up to 2.5 kΩ | ground beside; away from SIG_B and the routing lines |
| EQ_LP, EQ_MP, U12–U14 integrator nodes | 35–105 mm | KHN nodes, 10K-ish | short as placed; no logic crossing |
| Op-amp summing nodes and resistor-fed + inputs (E10) | ≤ 28 mm, most 11–20 mm | high impedance at RF | route each from the pin outwards, parts in the order placed; nothing switching alongside. The longest left: U5B − 28 mm (HF EQ), U12A − 25 mm |
| MUTEOUT, BUF1 | 88–89 mm | op-amp outputs, low impedance | ordinary care |
| Aux send lines (pot wiper → 22K at the header, R20–R25) | about 125–145 mm | up to 2.5 kΩ wipers; their 22K at the header is right (bus side short) | run them together as a bundle with ground between pairs where possible; away from SIG_B and the RTE lines |
| PRESRC → R118 (to U17) | 254 mm | low impedance (U7B output), but it carries the full pre-fader signal past the fader area | away from the routing 4K7s, the DG413 bus side and MUTEOUT |
| VREF (R40 / R41 → U4, U17) | 271 mm | a DC reference, 5K source | quiet route; see `met1_ret1_review.md` P2 (100 nF at R40 / R41) |

### Keep these away from the sensitive nets above (switching)

| Net | Length | What switches |
|---|---|---|
| SIG_B (R122 at U17 → Q4 beside D2) | 285 mm | green LED switch base, through 47K; on signal / no signal (≈ 150 ms holds) |
| RTE_LR / RTE_12 / RTE_34 (PVA2 → DG413 logic inputs) | 119–132 mm | routing keys; edges only on a key press |
| +5VL | 182 mm | DC, zener-derived; quiet but a logic supply |
| LED anode lines (D3–D8, D2) | short since E1 | key-latched LEDs; D2 by MET1 |
| U17 output / SIG_HOLD area (beside U17) | local | U17A discharges its hold cap on every signal peak above −20 dBu: an audio-rate pulse; keep the C99 loop tight to GNDD |

**Crossing rules:**
- **Crossings:** cross a sensitive net at right angles; never run alongside it.
- **Separation:** where SIG_B or an RTE line must pass the audio area, keep ≥ 2 mm from it with GNDA between where
  possible.

### Bus side
- **Bus-side stubs:** the bus lines from the header to the DG413s (MIX L / R: 25–31 mm; SUB 1–4: 37–53 mm) and to the
  22K aux resistors (12–24 mm) are the high-impedance stubs of the summing buses. Keep them as placed: short, with
  ground beside them, nothing switching alongside.
- **DG413 logic lines:** they enter on the chip's other side; don't route them between the bus pins.

### Soft mute and input
- **Soft mute:** the J112s (Q1 / Q2) are under U3B since E3. Their source vias go straight to GNDA at U3's ground, and
  the drain to the M1 / M2 nodes is a short stub (Self, "offness").
- **Input:** C94 / C95's GNDA ends via down beside U16's decoupler ground.

### Decouplers (E11)
- **Where they are:** every SMD decoupler is within 5.5 mm of its supply pin, most on the bottom right under the pin.
  This includes the DG413s' three each and U16's.
- **Joining them:** one via from the pin to the cap's rail pad; the cap's ground end vias straight to its own ground,
  GNDA or GNDD per the netlist.
- **No daisy chain:** don't run the rail through the cap and on to the next part; the rail tree feeds the cap, and the
  cap feeds the pin.

### Stability caps (E9)
- **Where they are:** the C0G stability caps sit at their op-amp pins, nine of them on the bottom under the op-amp:
  C37, C41, C70, C71, C75, C78, C80, C83 and C85.
- **Joining them:**
  - each takes one via straight from its pad to the pin's pad;
  - at C75, C78 and C83 the pads sit under the pin, so the via goes in the pad or right beside it;
  - their GNDA end vias down to the ground plane next to the cap.
- **Group and master (E9b):** the same applies to the group's 11 and the master's 13 bottom-side stability caps,
  including the fader post-amps' C32 / C33 / C36 / C37 under U5 (`stab_caps_proposal.md`).
- **Don't lengthen them:** a trace between such a cap and its pin undoes the stabilising, so don't route the input
  net to the cap first and on to the pin.

## Strip jack board

- **CHASSIS copper:**
  - **What's on it:** J1's sleeve, J5's sleeve, C8 / C9's chassis pads and H1 / H2.
  - **How to route it:** as wide as possible on both layers, a short pour from J1's sleeve pad to H1 / H2. That copper
    is the input shield's only path to the panel, 24 mm (E5: no closer standoff fits).
  - **Isolation:** no GNDA on it, and none of it on the link.
- **C8 / C9:** their pads to J1's tip / ring as short as the pads allow; the chassis pad straight into the sleeve copper.
- **The link CN5:** IN_T / IN_R on pins 1–2 with GNDA at 3 (as wired), SEND / RET_RAW split by grounds, DO_T / DO_R
  last. GNDA on the jack board is only the link grounds and J2's sleeve (the insert), J1's normals and the insert.

## Jig master stub

- **GCREF / GCREF_BUF:**
  - **What they are:** GCREF is the ground-cancel reference, JP1-selected: D = GCANCEL, A = local. GCREF_BUF is its
    buffered copy to every re-inverter.
  - **Route:** these are this board's critical nets, about 175 mm each. Route each as one trace with GNDA on both sides,
    and keep it away from the BNC output lines and the PFL LED / comparator (PFL_LA, PFL_LK).
  - **What the jig measures:** ground-cancel tests 2–4 measure exactly the residue these nets carry. A noisy route here
    would show up as a ground-cancel failure that isn't the console's.
- **Summing nodes (MIXL_VE … PFL_VE) and re-inverter inputs:** 13–22 mm as placed. Keep them short, with ground around
  them.
- **The bus lines from the header to the summers (MIX_L / MIX_R / SUB_1 / AUX_1–2 / PFL_MIX):** 86–222 mm.
  - These are the virtual-earth buses: low impedance at audio frequencies, but their capacitance counts against the
    summers' stability (sim: fine to 2.2 nF).
  - Route them as straight runs with ground between them.
  - The 1 nF bus-capacitance jumpers on the load board are the test of this, so don't add a lot of copper capacitance
    here.
- **BNC outputs (J2–J7) and the balanced XLR (J8):**
  - **CHASSIS:** J8's shell is the only CHASSIS on the stub (NT2 to GNDA). Keep its copper local to J8.
  - **The BNCs:** their shells are GNDA here (bench instruments); route their returns back to the summers' ground,
    not across the board.
- **GC_TIE (JP2 + 22R to GCANCEL):** short, as placed. It is the "22 Ω tie" test.
- **Supply:** the bench supply J1 → ±VBUS (about 68 mm) feeds the four strips through the ribbon as well. Give ±VBUS
  wide traces (the strips draw about 0.42 A on +V in all, plus the stub and load board).

## Jig load board

- **What it is:** passive, a grid of slide switches each with its group resistor (dummy channels), plus 1 nF
  bus-capacitance jumpers.
- **Routing:** each bus line (MIXL / MIXR / SUB1 / AUX1 / PFL) runs as a straight spine with its switches beside it;
  GNDA as a pour or wide return.
- **The 1 nF jumpers' ground:** must be the bus's own reference, so the added capacitance is what the test intends.
- **±VBUS:** about 140 mm, only if the load board takes supply (it passes the ribbon's) — wide.

## Net classes and DRC rules (in the projects, 2026-10-27)

`tools/netrules.py` writes them into each board's project. Run it with KiCad's Python after any re-placement or netlist
change, because nets are assigned by exact name:
- **Where:** net classes go in `X.kicad_pro`, custom rules in `X.kicad_dru`, for the strip, group, master, both jig
  boards and the three jack boards.
- **Regeneration:** the generators that copy `master.kicad_pro` (jack boards, jig, PSU) keep each project's own net
  settings.
- **Tests:** `tools/netrules_test.py` draws one offending track group per rule on a scratch copy of the strip and its
  jack board, and checks that DRC reports every rule. KiCad drops a rule whose condition it can't evaluate without
  saying so; `!( … )` was one such condition.

**Net classes**, assigned from the placed board, first match wins:

| Class | Nets | Track | Via |
|---|---|---|---|
| Ground | GNDA, GNDD, GNDM, PHONESGND | 0.6 mm (min 0.4 by rule) | 0.6 / 0.3 |
| Chassis | CHASSIS | 1.5 mm | 0.8 / 0.4 |
| Power | ±VBUS*, ±VA, ±VP, ±VM | 0.8 mm (min 0.5 by rule) | 0.8 / 0.4 |
| LogicSupply | ±VL, +5VL | 0.4 mm | 0.6 / 0.3 |
| Bus | signal pins of the 34-way bus header | 0.3 mm | 0.6 / 0.3 |
| Entry | signal lines on jacks and board-to-board links | 0.3 mm | 0.6 / 0.3 |
| HighZ | op-amp input nets with no op-amp output on them | 0.2 mm | 0.6 / 0.3 |
| Switching | LED, comparator-output, DG413-logic, relay-coil, transistor nets | 0.25 mm | 0.6 / 0.3 |
| Default | everything else (op-amp outputs, low-impedance audio) | 0.25 mm | 0.6 / 0.3 |

- **Class clearances:** 0.2 mm everywhere. Footprints have pad gaps down to 0.25 mm (the load board's slide switches),
  so the wider spacings below are rules on tracks.
- **The jig stub's ±VBUS:** feeds four strips; widen it to 1.0 mm by hand.

**Custom rules** (`X.kicad_dru`). Where several set the same constraint, KiCad takes the later one in the file, so
they are written general first:
- **0.3 mm:** Bus, Entry and HighZ tracks keep 0.3 mm from other copper.
- **0.5 mm:** HighZ, Entry and Bus copper keeps 0.5 mm from the logic supplies.
- **1 mm:** HighZ, Entry and Bus copper keeps 1 mm from Switching nets. Pad-to-pad is placement, measured by
  `tools/emc_check.py`; a DG413's logic pin is 0.67 mm from a bus pin by its pinout.
- **GNDD vs GNDA:** 0.5 mm between them. They meet only at the net tie, so keep the two pours apart.
- **CHASSIS:** 0.5 mm from everything else.
- **Length:** a HighZ net routed longer than 60 mm is flagged (today's longest is 28 mm of pads).
- **Track widths:** Power at least 0.5 mm, Ground at least 0.4 mm.
- **On the 4-layer boards only:**
  - no tracks on In1 (GND), and no zone there but ground;
  - no HighZ / Entry / Bus tracks on In2 (GND2);
  - rails and GNDD on In2 only inside the rail corridor;
  - no HighZ / Entry / Bus track on B.Cu over the corridor.

  Thirteen rules in all on these boards, eight on the 2-layer ones.

On today's placement, DRC is unchanged with the rules: 0 violations on the main and jig boards, and only the NJ6FD-V
footprint's own items on the jack boards.

## Before routing

- Re-check placement with `$KPY tools/emc_check.py <board>.kicad_pcb` after any manual move.
- `$KPY tools/ratsnest.py <board>.kicad_pcb` gives the signal ratsnest length and crossings; a manual move or turn that
  lowers the crossings is worth keeping (`untangle_proposal.md`).
- After routing, use parity DRC as usual. `emc_check.py` also reads routed boards, but it measures pads, not tracks.
