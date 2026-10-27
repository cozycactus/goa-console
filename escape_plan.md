# Escape and layer plan for the dense spots (2026-10-27)

Routing help for the three 4-layer main boards, from `tools/escape_plan.py`: where the board is densest, and which
outer layer each signal net should take there. It is a starting point for your routing, not a rule set. Nothing in the
projects changes.

## The policy

**Signal layers on the 4-layer boards:** F.Cu over In1 (GND) and B.Cu over In2 (GND2); see `layer_study.md`.

| Nets | Layer | Why |
|---|---|---|
| HighZ, Entry, Bus | F.Cu | over the unbroken In1; the rules already keep them off In2 and off B.Cu over the rail corridor |
| Switching (LED lines, comparator outputs, DG413 logic, transistors) | B.Cu | both ground planes then lie between them and the sensitive nets, better than any spacing on one layer |
| Everything else | where most of its pads are, then flipped net by net to clear crossings | |

**Scoring:** each net's layer is chosen once for the whole board, so a long net keeps one layer. A choice costs 1 per
crossing left with a net on the same layer, plus 0.3 per layer change it needs (a pad on the other side). Greedy
flips run until none lowers the cost.

**The per-net plan:** `docs/escape/<board>_layers.csv` gives net, class, suggested layer, pads per side, ratsnest
crossings, and how many are left on its layer.

## Results

Crossings are between straight ratsnest edges, so they are an upper bound: many get resolved by a detour, not a layer.
In the windows, through traffic (lines entering and leaving the window) is drawn faint, and its crossings with other
through lines are not counted, since a router runs those in parallel.

| Board | Crossings | Left on one layer after the plan | Layer changes needed | Nets on F.Cu / B.Cu |
|---|---|---|---|---|
| Strip | 1211 | 487 | 170 | 102 / 72 |
| Group | 1600 | 708 | 135 | 93 / 59 |
| Master | 2258 | 924 | 320 | 186 / 160 |

### The densest windows (30 mm of the board's length each)

| Board | Window | What's there | Crossings → left | Picture |
|---|---|---|---|---|
| Strip | y 91–121 | U15 (HPF integrators), RV11 / RV12 / RV14 | 173 → 70 | [channel_strip_1.svg](docs/escape/channel_strip_1.svg) |
| Strip | y 121–151 | U12, U13 (the mid KHNs), RV13 / RV15, SW12, CN3 (jack-board link) | 269 → 92 | [channel_strip_2.svg](docs/escape/channel_strip_2.svg) |
| Strip | y 155–185 | U14, JP5 / JP6 (insert jumpers), RV2 / RV3 | 170 → 69 | [channel_strip_3.svg](docs/escape/channel_strip_3.svg) |
| Group | y 136–166 | U8, U9, U11 (returns), SW8–SW10 | 325 → 146 | [group_1.svg](docs/escape/group_1.svg) |
| Group | y 180–210 | U4, U12, U13, U15, CN3 / CN4 (jack-board links) | 497 → 215 | [group_2.svg](docs/escape/group_2.svg) |
| Group | y 236–266 | U3, U5, RV2, SW1 | 226 → 98 | [group_3.svg](docs/escape/group_3.svg) |
| Master | y 166–196 | U7, U8, U10, U11, U19, U28, SW3 | 362 → 144 | [master_1.svg](docs/escape/master_1.svg) |
| Master | y 248–278 | U3, U4, U6, U12, U15, U17, U18 | 344 → 148 | [master_2.svg](docs/escape/master_2.svg) |
| Master | y 320–350 | CN2 / CN3 (wing headers), U35, U41, U42 (meters) | 337 → 110 | [master_3.svg](docs/escape/master_3.svg) |

**What the pictures show:**
- **Layers:** red is F.Cu, blue B.Cu; thick lines are HighZ / Entry / Bus.
- **Pads:** dark on top, light on the bottom, gold through-hole.
- **Circles:** a crossing still on one layer, where at least one side is local.

### Reading the strip
- **The worst spot (window 2):** the middle column between U12 and U13, where RV13, RV15, SW12 and the jack-board link
  CN3 sit. It is a vertical highway: through traffic runs up and down it, and the pots' local connections to the two
  op-amps cross it sideways.
  - **Order:** route the through traffic first as parallel tracks on its planned layers, then bring the pot
    connections across at right angles.
  - **Leftovers:** the remaining same-layer crossings there are mostly local blue (B.Cu) ones, each a short jog or
    one layer change.
- **Windows 1 and 3:** the same pattern around U15 (the HPF) and U14 / the insert jumpers, but lighter.

## Order of work it suggests (per board)

1. **HighZ / Entry / Bus nets on F.Cu first**, short and direct: input, summing nodes, bus lines to the header.
   Each stability cap on the bottom gets its one via (route_check check 5).
2. **The rail corridor:** ±VA, ±VL, +5VL and the GNDD spine on In2, and the branches to the decouplers on F.Cu / B.Cu
   (E11).
3. **Switching nets on B.Cu:** the LED lines, comparator outputs and DG413 logic.
4. **The rest by the plan,** densest window first. Use the circles as the places to expect a jog or a layer change.
5. **After each session:** run `tools/route_check.py` (return vias, reference, high-Z lengths, decouplers, stability
   caps) and `tools/ratsnest.py` if you move parts.

Re-run `$KPY tools/escape_plan.py <board>.kicad_pcb` after any placement change. It takes under a second.
