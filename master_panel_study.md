# Master section — panel and module study, v0.1 (October 2026)

The strips are 8 HP × 12U Eurorack-style modules on a daisy-chained ribbon (`strip_panel_study.md`).
The master schematic (`master.kicad_sch`, 1062 parts) is one board with no panel layout yet. This study
asks how the master's controls and I/O fit the same frame, and proposes how to split the master into
modules. It needs Ruslan's choice before a master PCB.

## 1. What the master's panel carries (from `master.net`)

| Function | Faders | Pots | PVA2 | LEDs | ¼" jacks | XLR |
|----------|--------|------|------|------|----------|-----|
| Sub 1–4 (fader, pan, to MIX, AFL; out, insert) | 4 | 4 dual | 8 | 4 | 8 | |
| Stereo returns 1–4 (level, 1-2 / 3-4, MIX, PFL; L/R in) | | 4 dual | 16 | 4 | 8 | |
| Aux masters 1–6 (level, AFL; out) | | 6 | 6 | 6 | 6 | |
| Mix (master fader, inserts, main L/R/M out) | 1 dual | | | | 2 | 3 |
| Monitoring (EXT select and in, C/R level and outs, phones, solo level) | | 2 dual + 1 | 1 | 1 | 5 | |
| Meters 2 × 20, power LED | | | | 41 | | |
| **Total** | **5** | **17** | **31** | **56** | **29** | **3** |

Panel space per item, measured on the strip: two pot columns at 22 mm per row; three PVA2 per row at
18 mm; two NJ6FD-V jacks per row at 20 mm (on a jack board, about 24 mm deep); one XLR per 8 HP row,
26 mm; fader zone 130 mm; about 466 mm usable in 12U.

## 2. Options

| | M1. Delta-style modules (recommended) | M2. One wide master board | M3. Control panels + rear I/O box |
|---|---|---|---|
| Layout | 4 × group modules (8 HP) + 1 master module (16 HP) = 48 HP, about 245 mm | One 48 HP panel (245 × 514 mm), one board of about 240 × 460 mm | Controls on 12U panels; all XLR / jack I/O on a separate rear box joined by ribbons |
| Group module n | sub n (summing amp, re-inverter, insert, fader, pan, to MIX, AFL), stereo return n, aux n master; 5 jacks, 3 pots, 7 PVA2, 3 LEDs, fader: **308 mm** of 466 | — | — |
| Master module | MIX L/R summing amps, inserts, master fader with the 2 × 20 meters beside it, mono, main DRV134s and mute relays, power-on mute, monitoring, PFL / solo, aux 5–6 masters, power entry and both wing headers: **324 mm** in 16 HP (412 mm in 8 HP: possible but tight) | — | — |
| Bus connection | Every module sits on the ribbon like a strip (the Delta way): group n's summing amp takes SUB n and AUX n through solder-jumper bus selects, so all four group PCBs are identical. Sub → MIX and return routing go back onto the ribbon through 4K7 | All buses into one board from the two wing headers (as now) | as M2 |
| Builds / repairs | 5 PCBs of 2 kinds (group ×4, master), each strip-sized or double | One large, expensive board | Two boards plus internal cabling |
| Schematic change | Split gen_master.py into gen_group.py and gen_master.py. Each group buffers GCANCEL locally for its re-inverters (one op-amp half), so no extra ribbon pin is needed | none | moderate |

## 3. Recommendation

**M1.** It is the Delta's own architecture: group modules on the motherloom, a master module in the
centre. It keeps every board strip-sized, so it uses the same frame, panel stack, jack-board idea,
placement engine and assembly flow. The four group boards are identical. A group module has about
150 mm spare, which is room for an optional 20-LED sub meter, as on Delta group modules. The console
becomes 24 strips + 4 groups + a 16 HP master ≈ 1.2 m.

Details to settle with M1:
- Which modules sit on which wing (two groups per wing keeps the wings symmetrical).
- Whether the main XLRs stay on the master panel (3 rows of 26 mm, fits) or go to a small rear
  bracket.
- The power entry stays on the master, feeding both wings. The group modules draw from the ribbon
  like strips: about 60 mA each, already inside the §27 budget, since the circuits only move.

## 4. Decision and status

**M1, chosen 2026-10-22.** `tools/gen_group.py` → `group.kicad_sch`: 155 parts, 452 pins, 0
mismatches, every pin on a pad, ERC 0. `tools/gen_master.py` → `master.kicad_sch` (now the master
module): 528 parts, 1525 pins, 0 mismatches, ERC 0. The circuits are unchanged from the one-board
master, moved through `master_lib.py`.

Before placement:
- ~~Jack and XLR depth~~ done 2026-10-22: jack boards for both. `group_jack_board.kicad_sch` (5 ×
  NJ6FD-V, 2 × 8 link) and `master_jack_board.kicad_sch` (9 × NJ6FD-V + 3 × NC3MAV, 2 × 20 link). All
  four schematics: 0 mismatches, every pin on a pad, ERC 0; the link pinouts match pin for pin
  (master spec header).
- **Wings.** Which groups sit on which wing (two per wing).
