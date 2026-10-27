# Routing guide: strip, group, master, their jack boards, the jig and the PSU (2026-10-26; layers, group, master, PSU 2026-10-27)

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
  Put a GNDA via close to each such signal via so the return can follow: about 1 mm where there's room, 2 mm at most
  on HighZ, Entry and Bus nets. Beside a SOIC pin, where E9 / E11 put caps under the pins, there is often no pad-free
  spot nearer than about 1.4 mm. For the other nets, wherever there's room.
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

## Group module (main board, 4-layer)

The same layer plan, rules and tools as the strip: GND / GND2 planes, rail corridor x 0.5–5.5, `route_check.py`,
`escape_plan.py` (`docs/escape/group_*.svg`). Measured on the placed board (Manhattan MST of the pads).

**Supply and ground**
- **Supply:** ±VBUS from the header CN2 to the filters R1–R4, 15–16 mm (E4), then ±VA (32 pads, about 500 mm) and +VL
  in the corridor.
- **GCANCEL:** header to R5 and the local buffer U1 / U6 input, 101 mm; quiet, ground beside it.
  - **GC_BUF:** to the re-inverters, 44 mm.
  - **The rule:** a cut or noisy GCANCEL costs the whole ground-cancel scheme.

**Bus lines** (Bus class: F.Cu, ground both sides where possible, nothing switching alongside). They run from CN2 to
the routing keys and jumpers far up the board:
- MIX L / R 243–252 mm (to SW1 / SW4 / SW8);
- SUB 1–4 221–227 mm (to SW5 / SW6 / SW9 / SW10 and JP1–JP4);
- AUX 1–4 42–51 mm;
- PFL 256 mm, PFLDET 239 mm.

They are summing-bus lines: low impedance at audio, but their copper adds to the master's bus capacitance (fine to
2.2 nF; roughly 0.1 pF per mm of track).

**Entry and outputs**
- **The links:** to the jack board, run as pairs with a ground between pairs:
  - CN3: the aux master's DRV135 outputs A_OP / A_ON (133–139 mm), the sub's S_OP / S_ON (50–53 mm), the insert
    SUB_SEND (267 mm, behind its 75R) and SUB_RETRAW (89 mm);
  - CN4: return 2.
- **The returns:** each run from its receiver through the level pot and PRE / PFL to the routing.
  - **Return 1:** RT_RTNL / RTNR 168–176 mm; the pot wipers RT_WL / WR 71–90 mm.
  - **Return 2:** RT2_ 45–111 mm.
  - **How:** low impedance after the followers; keep them on F.Cu, away from the LED lines.

**Switching**
- **LED anode lines:** D3 / D4 run 64–67 mm. On B.Cu.
- **Closest:** U11B+ (a return receiver input) is 3.8 mm from D4's anode pad, and U15B+ 5.2 mm. Cross at right angles,
  and keep the anode line on B.Cu past them.

**Summing nodes** (short as placed): A_SUM 11 mm at U6. The sub summer's node is at U1, with S_SUM its output (54 mm
to R7, low impedance).

## Master module (main board, 4-layer)

The same layer plan and tools; rail corridor x 0.5–6.5 (±VA, ±VP, ±VM, +VL, −VL, +5VL, GNDD).

**Power entry** (y 186–236, by J1 and the M4 star). +VBUS runs J1 → the wing PTCs F1 / F3, 257 mm in all with the
reservoirs and clamps.
- **Wing feeds:** ±VBUS_L / R run 68–129 mm to the wing headers CN2 / CN3. Each carries a whole wing, up to about
  2 A on +V.
  - **Width:** they are the WingFeed class (every net through a wing PTC): DRC asks for at least 1.5 mm, 2 mm
    preferred, and more if any part runs on In2 (0.5 oz there). The jig stub's PTC feeds are in the same class.
  - **Where:** keep them on their edge keep-outs.
- **Rails:** ±VA (52 / 50 pads, about 720 mm), ±VM (meters, 517–566 mm), ±VP (phones, 207–216 mm). In the corridor,
  with branches on F.Cu / B.Cu.
- **Grounds:** the star joins GNDA, GNDD, GNDM and PHONESGND through NT1–NT4 (x 33–46, y 208–220).
  - **Separate routes:** each ground keeps its own route to its net tie. GNDM (meters) and PHONESGND (120 mm) are not
    GNDA fill.

**Ground cancel**
- **GCANCEL:** 222 mm, from both wing headers to R10, the buffer U1 and the re-inverters U12 / U15.
- **GCANCEL_BUF:** 99 mm, to every re-inverter's reference resistor (R14, R24, R64, R75, R100).
- **How:** quiet, on F.Cu over the plane, ground both sides, no switching line within the 1 mm rule. This pair carries
  what the ground-cancel checks measure.

**Buses between the wings:** MIX L / R 167–176 mm, AUX 5 / 6 141–147 mm, PFL 290 mm, SUB 1–4 66 mm, header to header.
- **How:** Bus class, straight, with ground between.
- **Summing nodes:** short as placed (MIX_L 9 mm, MIX_R 19 mm, PFL_SUM 18 mm); keep them so.

**Outputs and inserts** (to the jack board on CN5, pairs with ground between):
- **The main outputs:** after the relays, MAIN_L / R / M _XP / XN, 54–111 mm, each pair together; before the relays,
  10–49 mm.
- **The insert:** MIX_L / R_SEND 145–158 mm behind their 75R; MIX_L / R_RETRAW 183–198 mm.
- **Phones:** PHO_L / R 159–165 mm from the LME49600s to K6. Route each beside PHONESGND, the phones' own return,
  as a pair.

**The C/Room path**
- **CRSB_L / R:** 233–277 mm, from the followers' 100R build-outs (pad-length, MG3) to the pots and the meters.
- **CRS_L / R:** the follower inputs, 22–29 mm. They sit 1.3 mm from the PFL switcher's logic line PFL_ON at U20's
  pins. That's the DG413 pinout (a logic pin next to a switch pin), as on the strip. Bring PFL_ON to U20 from the side
  away from CRS, on B.Cu.

**Switching** (B.Cu, away from all of the above)
- **RLY_DRV:** 204 mm, the six relay coils from Q1. It passes 3.0 mm from U2A's − input at D20; cross at right angles,
  never alongside.
- **MUTE_GO:** 99 mm.
- **The key LEDs' anode lines:** D12 / D13, 129–137 mm.
- **The meters:** the LM2901 outputs and LED strings sit 3.8–4.9 mm from the detector nodes (MR_DETO, ML_DETO, ML_X2,
  U36 / U37 inputs).
  - **How:** detector nodes on F.Cu, the strings and comparator outputs on B.Cu, both planes between them.
  - **Hot spot:** the meter area, y 320–350, is the master's third densest window (`docs/escape/master_3.svg`).
- **The flasher:** FL_N runs 97 mm behind D18 (E8, intended). It's a slow RC node; keep it off the audio anyway.

## PSU board (2-layer, `psu_spec.md` §7)

**The layout:** two identical floating regulators. The −V one is the same circuit stacked under the +V one: its
"output" is 0V and its return is −V, so 0V carries 4 A from both rails.
- **The 4 A paths:** the SMPS in (J1 / J2) → chokes L1 / L2 → reservoirs → LM1084 U1 / U3 → output caps → J3.
- **How to route them:** the HighCurrent class (POS_IN, NEG_IN, POS_LC, NEG_LC, +V, −V, 0V); DRC wants at least
  3 mm tracks, 4 preferred, or pours.
  - **Layers:** on both layers, stitched with via arrays: about 1 A per 0.5 mm via, so 5 or more per layer change.
  - **The fault path:** the crowbar SCRs Q2 / Q4 short a rail to its return in a fault, through +V / 0V / −V. The
    same copper takes that surge until the SMPS current limit acts.

**The regulators**
- **Adjust dividers (Kelvin):** the adjust divider sets each output, Vout = 1.25 × (1 + R2 / R1). R1 / R2 (and R10 /
  R11 on −V) sit about 30 mm from U1 / U3.
  - **R1:** take its OUT end from the regulator's OUT pin by its own track, not from the 4 A copper. Otherwise the
    drop along that copper raises the output by the same amount.
  - **R2:** its low end goes to the output side's return at J3, so the output is held at the console's connector.
  - **The ADJ line:** low impedance at audio (47 µF C3 / C9 on it), so its length is harmless. Keep it off the
    choke's field.
- **The chokes:** L1 / L2 are horizontal toroids. Don't run the ADJ, sense or LED lines through the toroid's
  middle or close past its ends.

**Crowbar sensing**
- **The divider:** the TL431 divider (R4 / R5, R13 / R14 on −V) should sense the rail where it leaves the board.
  Take R4's top from the +V copper at J3, not from U1's pin, so the trip point (19.1 V) is the console's voltage.
- **The reference node:** POS_REF / NEG_REF is the TL431's high-impedance input, with C6 / C12 on it. Keep it short
  and away from the SCR gate lines.

**Grounds and earth**
- **0V star:** at J3's 0V pins (4 / 5). The SMPS returns, the reservoirs, the output caps, the divider low ends and
  the crowbar return meet there, each by its own copper. The reservoir ripple then doesn't ride on the sense
  returns.
- **EARTH** (J3 pin 1 to the case stud J4) is the console's safety earth. It stays isolated from 0V on this board
  (psu_spec): Chassis class, 0.5 mm from everything (DRC rule). Run it as one wide track straight to J4.

**Heat:** the four TO-220s sit at the top edge, tabs over it onto the heatsink (PC1). Keep their legs' copper wide
right up to the pads; that is part of the 4 A path.

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
| HighCurrent | the PSU's 4 A paths (POS_IN, NEG_IN, POS_LC, NEG_LC, +V, −V, 0V) | 4.0 mm (min 3.0 by rule) or pours | 1.0 / 0.5 |
| WingFeed | nets through a wing PTC (master ±VBUS, ±VBUS_L / R; jig stub) | 2.0 mm (min 1.5 by rule) | 1.0 / 0.5 |
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

## Fab limits and outputs (2026-10-27)

**Board Setup > Constraints in every project, the PSU's too** (`tools/netrules.py` `FAB`), from JLCPCB's published
capabilities (read 2026-10-27):
- **Copper:** 0.15 mm pad to pad, tracks ≥ 0.1 mm (the classes use ≥ 0.2), holes ≥ 0.3 mm and vias ≥ 0.5 mm (our
  choice, at no extra cost), via annulus ≥ 0.1 mm.
- **Holes:** a plated hole 0.28 mm from a track, pad holes 0.45 mm apart.
- **Edge:** 0.5 mm from the board edge (ours; JLCPCB 0.2).
- **Silk:** 0.15 mm from pads; text ≥ 1.0 mm high with ≥ 0.15 mm lines.

**Silk:** the placer now writes every reference at 1.0 mm text with 0.15 mm lines (it was 0.8 / 0.12, below JLCPCB's
minimum).
- **Search:** a free spot within 7 mm of the part.
- **Hidden:** only four master references (R139, R142, R158, R212) find no room. They stay on the Fab layer.
- **Group labels:** the group's "GRP __" and jumper numbers are 1.0 mm too.

**When a board is routed:** `python3 tools/fab_out.py <board>` runs the checks, then writes `fab/<board>/` (gitignored).
- **The checks:**
  - DRC with zones refilled and schematic parity;
  - `route_check.py`;
  - it refuses on any DRC violation, parity issue, unrouted connection or route_check ERR. The footprint-internal
    items listed in its `KNOWN` are accepted: the NJ6FD-V jacks, the PSU's overhanging TO-220s.
- **The files:**
  - Gerbers with every copper layer;
  - Excellon drill, PTH and NPTH separate, with maps;
  - `<board>_gerbers.zip` to upload;
  - the position file and a JLCPCB CPL;
  - the BOM and the DRC report.

## Before routing

- **After each routing session:** run `$KPY tools/route_check.py <board>.kicad_pcb`. It checks what DRC can't:
  - **Return vias:** a GNDA via beside each signal via.
  - **Reference:** filled GNDA under every HighZ / Entry / Bus track on its reference layer, with the gaps' lengths and
    positions.
  - **High-Z nets:** routed length and via count.
  - **Decouplers:** copper path from pin to cap, and the cap's ground via.
  - **Stability caps:** at most one via to their pin.
  - **GNDD:** no GNDD fill.

  It fills the zones on its own copy, so draw the GNDA zones first. `tools/route_check_test.py` proves each check on
  synthetic routing.
- Re-check placement with `$KPY tools/emc_check.py <board>.kicad_pcb` after any manual move.
- `escape_plan.md`: which outer layer each net takes (`docs/escape/<board>_layers.csv`) and pictures of the densest
  spots; re-run `$KPY tools/escape_plan.py <board>.kicad_pcb` after placement changes.
- `$KPY tools/ratsnest.py <board>.kicad_pcb` gives the signal ratsnest length and crossings; a manual move or turn that
  lowers the crossings is worth keeping (`untangle_proposal.md`).
- After routing, use parity DRC as usual. `emc_check.py` also reads routed boards, but it measures pads, not tracks.
