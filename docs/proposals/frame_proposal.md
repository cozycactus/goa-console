# Frame rails: proposal (2026-10-25)

The strip-panel decision (2026-10-22) is a custom 12U frame with rails at the panel ends only. The panels' screw pattern
is fixed: `panels/`, one Ø3.2 per end of each 8 HP panel and two on the master, 3 mm from the panel ends. This
proposal says what they screw into. The tub (floor, cheeks, arm-rest, 9° tilt) stays as the 3D model has it, and is
woodwork.

## What the rails carry

- **Span:** 30 × 8 HP = 1219.2 mm (12 strips | groups 1-2 | master | groups 3-4 | 12 strips), supported only by the
  two cheeks.
- **Load:** about 0.43 kg per 8 HP module (panel 84 g, boards, 15 pots, fader, jacks, keys, knobs); about 13 kg in
  all, so about 63 N per rail, spread along it. Add a hand leaning on the desk: 100 N at mid-span.
- **Clearance** (from the placed boards):
  - nothing below the panel at y < 0 or y > 444 (jack boards start at y 0, main boards end at 444);
  - the motherloom and the harness run at y 300–351;
  - the tub floor is 58 mm under the panel top.

  A rail 10 mm wide on each screw line (y −13…−3 and 495…505) can be as deep as 56 mm.

**Sag**, 6060-T6 aluminium (E = 69 GPa), simply supported over 1223 mm:

| Section (w × h) | Self-load | 100 N at mid-span | Mass per rail |
|---|---|---|---|
| 10 × 10 (the 3D model's placeholder) | 26.2 mm | 66 mm | 0.33 kg |
| 10 × 20 | 3.3 mm | 8.3 mm | 0.66 kg |
| 10 × 40 | 0.41 mm | 1.04 mm | 1.32 kg |
| **10 × 50** | **0.21 mm** | **0.53 mm** | **1.65 kg** |

**Eurorack rails** (Doepfer / Tiptop type, threaded strip) were considered and rejected:
- they come in 84–126 HP lengths, so 240 HP needs joints;
- they are light profiles made for 3U spans, so over 1.2 m they'd need posts down to the tub floor (their exact section
  wasn't checked).

Their real advantage, sliding nuts, matters little here: the panels and their holes are made to one drawing.

## Proposal

**FR1. Rails: 10 × 50 aluminium flat bar, 6060-T6 or 6082, mill finish, standing on edge.**
- **Size:** two rails, 1223.2 mm long (2 mm into each cheek), on the screw lines y −8 and y 500 (the panel's own frame).
- **Holes:** 30 M3 tapped holes in each rail's top face (60 in all): one per 8 HP module at module x + 6.35 mm, two on
  the master (+6.35 and +72.29). The first is 6.35 and the last 1184.91 from the console's left edge.
- **Tolerance:** ±0.15 mm on position. Each panel's own cut-outs fix its board, so a rail hole only moves the 0.34 mm
  gap between neighbouring panels.
- **Alternative to drilling from the table:** lay the panels on the rails with 0.34 mm shims, transfer-punch through
  their screw holes, then drill 2.5 and tap M3.
- **Result:** no centre post. Under 0.25 mm of sag from the console's weight and about 0.5 mm under a 100 N lean.

**FR2. End fixing and bonding.**
- **Ends:** each rail end sits in a 10 × 50 rebate in its walnut cheek, held by two M4 screws through the cheek into
  M4 holes tapped in the rail end (3.3 tap drill, 3.35 mm wall left).
- **Bonding:** the rails are the CHASSIS path for every panel. The jack boards' plated standoffs bond to the panels
  (G2); the panels bond to the rails through the M3 screws in bare tapped holes, and a star washer under each head.
  Each rail gets one 2.5 mm² green-yellow wire to the master's M4 star stud (chassis, earthed through the PSU lead's
  pin 1), via a ring lug on an M4 tapped hole near its middle. Mill finish (or clear anodise with the holes tapped
  afterwards) keeps the contact bare.

**FR3. Drawings and model.**
- **Generator:** a script writes the rail drawing (DXF, hole table) from the module order and `panel_layout`'s screw
  positions, as the panels are.
- **3D model:** the rails become 10 × 50.

## Sign-off

Signed off by Ruslan on 2026-10-25: FR1–FR3 as proposed.

- [x] **FR1** Two 10 × 50 6060-T6 / 6082 flat-bar rails, 1223.2 mm, 30 M3 tapped holes each from the panel screw pattern.
- [x] **FR2** Ends in cheek rebates with 2 × M4; panels bonded through bare tapped holes and star washers; one
  2.5 mm² bond per rail to the M4 star.
- [x] **FR3** Rail drawing generated (DXF + hole table) and the 3D model's rails at 10 × 50.

## Applied (2026-10-26)

- **Later the same day (`docs/studies/thermal_study.md` TH1):** the back rail carries 30 vent slots 30 × 25 mm on its neutral axis
  (sag 0.21 → 0.23 mm). The bonding hole moved to the bottom face (M4 × 8) on both rails.

- **Correction to FR1's length:** the 3D model's cheek inner faces sit 2 mm outside the console (x −2 and 1221.2), so a
  rail 2 mm into each cheek runs from −4 to 1223.2: **1227.2 mm**, not 1223.2. The holes move by the same 2 mm:
  10.35 … 1188.91 from the left end.
- `panel_layout.py`: the module order (`ORDER`, `modules()`), the rail section and lines, `rail_holes()` and
  `rail_span()`, shared by the panels, the rails and the 3D model. `console_3d.py` builds its rails and cheeks from them.
- `tools/frame_fab.py` → `frame/`:
  - `rail.dxf`: top, side and end views;
  - `rail_holes.csv`;
  - `rail.pdf` / `.svg`: an A3 drawing with the hole list.
- **Holes** (one part, two off):
  - 30 × M3 (tap drill 2.5 × 8, thread 6) on the top face's centre line;
  - 2 × M4 × 10 in each end at 12.5 / 37.5 below the top;
  - one M4 tapped through the side at mid-length for the bond.
  The script checks that every panel screw of every module lands on a rail, clear of the cheek rebates.
- **Checks:** `panel_fab.py` checks the cut-outs against the new rail band (y −13…−3 / 495…505), and all three panels
  pass. The 3D model was rebuilt with 10 × 50 rails.
