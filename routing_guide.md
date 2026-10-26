# Routing guide: strip, strip jack board, jig master stub, jig load board (2026-10-26)

Notes for routing the first boards to build: the jig and four strips. They are drawn from the placed boards (net lengths
are Manhattan minimum-spanning-tree estimates from the pads, as `tools/emc_check.py` measures them) and from
`emc_placement_study.md`, whose rules and sources apply throughout. Copper is Ruslan's, so this is advice, not a spec.
The net classes at the end are suggestions only; nothing is written into the project files.

## Channel strip (main board)

### Ground and supply
- **GNDA:** one continuous reference under the audio circuit. The ribbon's even pins (2–16) and the spade (CN4) are
  where it leaves the board. Every op-amp decoupler's GNDA end takes its via at the cap.
- **GNDD:** the logic ground, for the LM393s (U4, U17), the LED switches (Q3–Q5), every LED cathode, the DG413 logic
  side, +5VL (D9 / C62) and the PVA2 pole-B returns.
  - It joins GNDA only at NT1, beside the spade.
  - No GNDA current through GNDD, and no LED current through GNDA. Don't cross a GNDD region with an audio trace, or
    the reverse.
- **±VBUS:** header pins 30–34 to the 10R filters R1–R4 (5–8 mm since E4). After them the rails are ±VA (op-amps),
  +VL / −VL (logic, LEDs) and +5VL from D9.
  - Strip current: about 104 mA on +V and 87 mA on −V.
  - ±VA reach 34–36 pads over about 560 mm, so give them a tree or a wide trace along the board, not a daisy chain
    through decoupler pads.
- **GCANCEL:** header pin 26 to R5 (10R) at the spade. It carries no current; route it as a quiet signal next to
  ground.

### Keep these short and guarded (high-impedance or sensitive)

| Net | Length | Why | Rule |
|---|---|---|---|
| IN_T, IN_R (CN3 → R110 / R111, then U16 + via 220R) | 74–76 mm | balanced input, RF from the ribbon | a pair, with ground on both sides, away from everything below; on the ribbon conductors 1–2 with ground at 3 |
| U2B + input (pan buffer L, from the pan pot) | 165 mm | the longest high-impedance line on the strip (pan pot at y 252, U2 at the fader end) | a guard trace or ground on both sides; nothing switching alongside; proposal PAN1 (`pan_buffer_proposal.md`) brings it to 24 mm; route it as here until that is signed off |
| FPIN (fader wiper → U2A) | 72 mm | fader wiper, up to 2.5 kΩ | ground beside; away from SIG_B and the routing lines |
| EQ_LP, EQ_MP, U12–U14 integrator nodes | 35–105 mm | KHN nodes, 10K-ish | short as placed; no logic crossing |
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

## Suggested net classes (for you to set, if wanted)

| Class | Nets | Width | Clearance | Notes |
|---|---|---|---|---|
| Power | ±VBUS, ±VA, ±VP / ±VM (master) | 0.6–0.8 mm (±VBUS 1.0 on the jig stub) | 0.25 mm | ±17 V: no special clearance needed |
| Logic supply | +VL, −VL, +5VL | 0.4 mm | 0.2 mm | |
| Ground (where not a pour) | GNDA, GNDD | 0.8 mm + pour | 0.2 mm | GNDD separate, joined at NT1 only |
| Chassis | CHASSIS | ≥ 1.5 mm / pour | 0.3 mm | jack boards and the jig XLR only |
| Bus | MIX L / R, SUB 1–4, AUX 1–6, PFL, PFLDET, GCANCEL, GCREF* | 0.3 mm | 0.3 mm | guarded where possible |
| Audio (default) | everything else | 0.25 mm | 0.2 mm | |

## Before routing

- Re-check placement with `$KPY tools/emc_check.py <board>.kicad_pcb` after any manual move.
- After routing, use parity DRC as usual. `emc_check.py` also reads routed boards, but it measures pads, not tracks.
