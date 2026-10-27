# 2 vs 4 layers for the console boards (study, 2026-10-27)

**Decided by Ruslan on 2026-10-27:** 4 layers for the strip, group and master main boards, 2 layers for every jack board,
both jig boards and the PSU. Applied the same day; see "Applied" at the end.

## The boards

| Board | Size, mm | Parts (bottom) | Built | Ratsnest density | Crossings per 10 cm² |
|---|---|---|---|---|---|
| Strip main | 38.1 × 400.1 | 296 (66) | 24 + spares | 63 mm/cm² | 118 |
| Group main | 38.1 × 349.6 | 269 (49) | 4 + spare | 72 mm/cm² | 161 |
| Master main | 78.7 × 331.6 | 586 (83) | 1 + spare | 66 mm/cm² | 151 |
| Jig master stub | 160.1 × 125.1 | 148 (0) | 1 | 15 mm/cm² | 14 |
| Jig load board | 120.1 × 85.1 | 54 (0) | 1 | 8 mm/cm² | 2 |
| PSU | 120.1 × 60.1 | 56 (0) | 1 | 17 mm/cm² | 9 |
| Jack boards (strip / group / master) | 38 × 43 / 38 × 94 / 79 × 112 | 8–16 | 24 / 4 / 1 | ≈ 10 mm/cm² | ≈ 4 |

**How the two density columns are measured:**
- **Ratsnest density:** the Euclidean MST of every signal and supply net, grounds excluded, per board area.
- **Crossings:** pairs of ratsnest edges of different nets that cross, grounds excluded. Routing resolves many of
  them by detours, so the counts overstate what a router needs. The ratio between boards holds.

**Only the three main boards are in question.** The jig, the PSU and the jack boards are 4–15 × sparser and stay
2-layer whatever is chosen.

## What the main boards need

**Routing capacity.**
- **Demand:** routed length is typically about 1.3 × the ratsnest, so the strip needs about 80 mm of track per cm²,
  the group about 95.
- **Capacity:** one layer at a 0.45 mm track pitch (0.25 track + 0.2 clearance) holds 220 mm/cm² fully packed. Between
  pads and courtyards a practical 30–40 % of that is usable: about 65–90 mm/cm² per layer. That fraction is a planning
  figure, not a measurement.
- **Result:** each main board needs roughly one full signal layer of routing.

**Cuts across the board.**
- **Why they matter:** a long, thin board has to pass every net that spans it through each horizontal cut.
- **Measured:** the busiest cut needs 35 tracks on the strip (y 151, the EQ area), 57 on the group (y 183) and 63 on
  the master (y 189), signal plus supply.
- **Capacity:** one layer has room for about 70, 75 and 151 tracks there, counting only the pads on the cut. So it fits
  on paper. In practice the cut sits among pads and SOIC rows, which is where the detours and layer changes pile up.

**Supply trees.**
- **Lengths:** ±VA reach 34–36 pads along the strip, about 560 mm each, plus +VL (360 mm) and +5VL (170 mm).
- **Crossings:** on 2 layers they compete with the signals for the top. About 500 of the strip's raw crossings (470 on
  the group, 1500 on the master) involve a supply net.

**Ground.**
- **Pad count:** about 120 ground pads on the strip, 150 on the group and 270 on the master, GNDA, GNDD and GNDM
  together. Each takes a via in either stackup, to the bottom pour or to the plane.
- **The GNDD region:** logic, LEDs, the DG413 logic side and the comparators. It must meet GNDA only at the net tie NT1.

**Bottom-side parts.** E2, E3, E9, E10 and E11 put many small parts on the bottom (courtyards cover 16 % of the strip's
bottom, 25 % of the group's, 23 % of the master's). On 2 layers every one of them is an island in the bottom ground
pour.

## 2 layers

**What it means:**
- **Bottom:** must be the ground: a GNDA pour that stays continuous along the whole board, with a GNDD region under the
  logic, joined at NT1.
- **Top:** carries nearly all signals and the three supply trees, roughly the full capacity of one layer at the
  busiest places.
- **Crossings:** every crossing that can't be detoured becomes a short bottom jumper through the pour.
- **The bottom parts:** cut more holes in the pour.

**Rules it needs (beyond `netrules.py`):**
- **Bottom jumpers:** short (≤ 10 mm), at right angles to the board's long axis. Never under or alongside a HighZ net
  or the bus, never across the NT1 joint.
- **Stitching:** the bottom pour stitched to top ground fill on both sides of every jumper and along the edges.
- **Long nets:** no top signal longer than about 50 mm without an unbroken pour under it. The bus lines, PRESRC
  (254 mm) and the long switching lines (SIG_B 285 mm, the RTE lines 120–130 mm) need a continuous return path under
  them along their whole length.
- **Supply trees:** run as two parallel, wide traces down one edge of the top. The decouplers branch off them, so the
  supplies don't weave through the audio.

**What it costs in quality:**
- **Ground impedance:** the bottom pour is a ground plane with holes. Its impedance and the loop areas depend on
  routing discipline at every jumper.
- **Ground cancel:** the ground-cancel scheme (GCANCEL, ground_study.md) and the 10 mA ground-current figures assumed
  a low-impedance strip ground.
- **It is workable:** consoles of the Delta's era were double-sided through-hole boards. But at today's density
  (SOIC, 0805, parts on both sides), routing it is slow, and the result varies with how it is routed.

## 4 layers

**Proposed stackup** (the fab's standard 1.6 mm build, 1 oz outer copper):

| Layer | Use |
|---|---|
| L1 (top) | parts, signals |
| L2 | solid GNDA plane, unbroken |
| L3 | GND2: GNDA fill (the return for L4), with ±VA, +VL / −VL, +5VL and the GNDD spine only in a rail corridor along the left edge (see Applied, In2 as ground) |
| L4 (bottom) | the bottom parts, signals, GNDA fill stitched to L2 |

**What it means:**
- **Routing:** two signal layers (L1, L4) for about one layer of demand: about 50 % use, and short layer changes are
  free.
- **Ground:** every GNDA pad takes one via straight to L2 (GNDD pads to their spine; see Applied). The ground is the same solid plane everywhere, under every
  HighZ net, bus line and decoupler loop.
- **Supplies:** the trees run in the rail corridor on L3, and their ~500 / 470 / 1500 crossings mostly leave the signal layers.
  The branches cross to each IC on L1 / L4.
- **Bottom parts:** the bottom-side caps (E9 / E11) via straight through to their pins with L2 / L3 right there, which
  is what those moves were for.

**Rules it needs** (`netrules.py` would add them as layer-specific rules):
- **HighZ:** on L1 / L4 only, never on L3 (the supply layer).
- **L2:** no tracks, and no zone but ground.
- **Power class:** pours on L3; the track-width rule only applies where a rail runs on L1 / L4.

**What it costs:** see Pricing below: at JLCPCB, $27 more for phase 1 and $93 more for the whole console.

## Pricing

Read from the fabs' instant-quote calculators on 2026-10-27, without an account and without uploading anything. A
research agent did the reading, so treat the figures as quotes on that date.

**Settings and quantities:**
- **Build:** 1.6 mm FR-4, 1 oz outer copper, green mask, white silk, lead-free HASL, single pieces (not panels),
  without shipping or VAT.
- **Phase 1** (the jig build) = 5 strip mains + 5 strip jacks + jig stub + load board, 5 of each (the minimum).
- **Full build** = 30 strip mains + 30 strip jacks + 5 groups + 5 group jacks + 5 masters + 5 master jacks.

| Fab | Phase 1, all 2L | Phase 1, mains 4L | Full build, all 2L | Full build, mains 4L | 4L premium per strip at 30 |
|---|---|---|---|---|---|
| JLCPCB (USD) | 43.50 | 70.50 (+27) | 106.40 | 199.00 (+93) | 1.25 |
| PCBWay (USD) | 132.99 | 182.70 (+50) | 265.05 | 449.37 (+184) | 2.64 |
| Aisler (EUR, 4L is ENIG only) | 184.22 | 242.29 (+58) | 478.26 | 950.46 (+472) | — |

"Mains 4L" means the strip, group and master main boards on 4 layers, and every jack board and both jig boards on 2.

**Notes:**
- **Where JLCPCB's premium comes from:** mostly its $25 engineering fee per 4-layer design (against $4 on 2 layers).
  Per board at 30 pieces the difference is small: $88.70 against $51.30 for 30 strip mains.
- **Board size:** none of the four fabs charges extra for the 38 × 400 mm board.
  - **JLCPCB:** the oversize fee starts at 60 cm length or 650 cm² area (strip main 152 cm², master main 261 cm²), and
    the live quote showed it at $0. Its large-aspect-ratio boards get a manual manufacturability check.
  - **Panels:** V-cut panels stop at 475 mm, so order single pieces.
- **Aisler:**
  - **Finish:** no 4-layer HASL (ENIG only).
  - **Quantities:** sold in multiples of 3.
  - **Rules:** 2-layer HASL is 200 µm track / 150 µm space, which the project's 0.2 / 0.2 mm rules meet.
  - **Size:** it publishes no maximum board size, so ask before ordering 400 mm boards.
- **Multi-CB:** 2–3× JLCPCB's price, and it sells only to businesses.
- **Lead times** (JLCPCB): 2-layer HASL 2 days, 4-layer 3–4 days; DHL to the EU or US about $35–40 for 30 strip mains
  (1.7 kg).
- **ENIG:** roughly doubles the 2-layer price at JLCPCB ($110 / $214 for phase 1 / full build all-2L, $183 / $343
  all-4L). Not needed: HASL is fine for SOIC-8 / 0805 / THT. ENIG only matters for fine-pitch or very flat pads.

## Recommendation

**4 layers for the strip, group and master main boards; 2 layers for every jack board, both jig boards and the PSU.**

**Why:**
- **Cost:** at JLCPCB the difference is $27 for phase 1 and $93 for the whole console, about $1.25 per strip. That
  is less than the 34-way IDC socket on each strip.
- **Routing:** the main boards need about one full signal layer of routing. On 4 layers that spreads over two signal
  layers at about half use, with layer changes free. On 2 layers it fills the top and pushes every unresolved crossing
  through the ground pour.
- **Ground:** a solid GNDA plane under everything is what ground_study.md, the ground-cancel scheme and the EMC work
  (E1–E11) assumed in effect. On 2 layers it depends on routing every jumper well. The bottom-side caps of E9 / E11 via
  straight to the plane.
- **Supplies:** they leave the signal layers (L3), removing about 500 of the strip's raw ratsnest crossings.

**Decide before phase 1:** the jig tests real strips, so the first strips should be the stackup the console will use.

**If you choose 4 layers, the follow-up work (settings only, no copper):**
- **Boards:** set the three main boards to 4 copper layers with the fab's 1.6 mm stackup in their files (`placer.py`
  writes the layer count; placement unchanged).
- **Rules:** add the layer rules to `tools/netrules.py` (HighZ off L3, no tracks on L2) and extend
  `netrules_test.py`.
- **Guide:** update `routing_guide.md` with the layer plan, including where GNDD runs and NT1.

**If you keep 2 layers:** the 2-layer rules above go into `routing_guide.md` and `netrules.py` instead. The routing is
slower, and its ground quality depends on how each jumper is routed.

## Applied (2026-10-27)

**Boards:**
- **Layer count:** `placer.py` takes `layers=4`. The strip, group and master layouts use it.
- **Inner layers:** In1.Cu is named GND (plane type), In2.Cu PWR (mixed; renamed GND2 and made a ground layer the same day, see In2 as ground). The board thickness is 1.6 mm, the fab's
  standard 4-layer stackup.
- **Re-placed:** 0 parts moved, 0 DRC violations, 0 parity issues, every footprint linked. The jack boards, jig and PSU
  stay 2-layer.

**GNDD on 4 layers:** GNDD's pads are spread in clusters along each board.
- **Strip:** D2 at y 50, U4 at 68–88, D5 at 142, the keys / LEDs / U17 at 265–323, the DG413s at 345–392; NT1 at 351.
- **Group:** 7 pads.
- **Master:** four groups around its net ties.

A partition in the GND plane would be a long, fragmented finger. So L2 stays a solid GNDA plane, and GNDD runs as a wide
spine on L3 (PWR at first; in the rail corridor on GND2 since, see In2 as ground), beside the +VL / +5VL that feed the logic and LEDs, to the net tie. Their currents go out and back
side by side over the GNDA plane and never through it. The GNDD 0.5 mm rule keeps the spine clear of the GNDA vias
passing through L3.

**Rules** (`tools/netrules.py`, 4-layer boards only), each shown to fire by `tools/netrules_test.py`:
- no tracks on In1.Cu;
- no zone on In1.Cu but a ground one;
- no HighZ / Entry / Bus tracks on In2.Cu.

## In2 as ground (2026-10-27, Ruslan)

**The flaw in the first 4-layer plan: it ignored where B.Cu's return current flows.**
- **The stackup:** the fab's standard 1.6 mm build has thin prepreg (about 0.2 mm) on each outer pair and a thick core
  (about 1.1 mm) in the middle. So F.Cu's return flows in In1, and B.Cu's in In2.
- **The plan:** In2 was to be supply strips plus the GNDD spine. A bottom trace crossing a gap between strips loses its
  return there (above roughly 10 kHz the return hugs the trace), and the current detours through a decoupler.
- **Worse:** the GNDD spine would have sat 0.2 mm under bottom audio traces.

**Applied the same day:**
- **In2 "GND2":** GNDA fill, the return for B.Cu.
- **The rail corridor:** the supply rails and the GNDD spine run only in a corridor along the left edge (x 0.5–5.5 mm on
  the strip and group, 0.5–6.5 mm on the master: the fewest through-hole pins). `placer.py` draws it as the rule area
  RAILS (`rails=(x0, x1)`; no keepout of its own).
- **Branches** from the corridor to each IC's decoupler cross on F.Cu / B.Cu, each over its own ground layer.
- **Rules** in `tools/netrules.py` (all fire in `netrules_test.py`, 13 on the 4-layer boards):
  - no HighZ / Entry / Bus tracks on In2;
  - rails and GNDD on In2 only inside RAILS (`!A.insideArea('RAILS')`: KiCad negates a single function call but
    drops `!( … )` and `insideArea(...) == 0` silently);
  - no HighZ / Entry / Bus track on B.Cu over RAILS.
- **Guide** (`routing_guide.md`): a GNDA via within about 1 mm of every signal via that changes between F.Cu and B.Cu
  (the return moves from In1 to In2); stitching every 10–15 mm and along the corridor; sensitive nets preferably on
  F.Cu.
- **Re-placed:** 0 parts moved, 0 DRC violations, 0 parity issues, every footprint linked.
