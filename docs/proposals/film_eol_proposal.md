# FE1 / FE2: the obsolete 2.2 µF film coupler (proposal, 2026-10-29)

**FE1 signed off by Ruslan on 2026-10-29 and applied the same day; see "Applied" at the end.** FE1's change is `archive/patches/film_eol_proposal.patch`. It touches tools only: the order code in `gen.py`,
`gen_master.py` and `master_lib.py`.

## 1. Why

The phase-1 pricing (2026-10-28) found **WIMA MKS2C042201K00KSSD** obsolete: DigiKey lists it obsolete, Farnell "no
longer manufactured", Mouser "restricted availability". It is the 2.2 µF PET film part signed off in `docs/proposals/film_np_proposal.md`
F1.

**Where it is:** 21 parts per board set, 108 in the console.

| Board | Parts | Use |
|---|---|---|
| strip ×24 | C13, C49, C96 | fader wiper coupler, LF EQ film, PFL send DC block (K1) |
| group ×4 | C15, C37, C56, C62, C82, C88 | wiper couplers |
| master | C29, C35, C66, C81, C106, C124, C128, C138, C147, C157, C175, C57 | wiper couplers, meter averaging, the power-on mute timing cap (C57) |

**The cause.** Yageo / KEMET notice PTN-093025-VK (30 Sep 2025) phases out thin-PET parts because Mylar Specialty Films
closed its Luxembourg film line, so the small 2.2 µF boxes are going end of life. WIMA's 2.2 µF / 63 V now ships only
in its larger "M" box.

## 2. What's on the market (read 2026-10-29)

| Part | Body W × H × L (mm) | Fits today's footprint | Status | Mouser stock / price |
|---|---|---|---|---|
| **KEMET MMK5225K63J06L4BULK**, PET 63 V ±10 % | 7.2 × 13 × 7.2 | **yes, exact** | **obsolete** (KEMET: "recommended replacement R60", which is 7.5 mm pitch and up) | **1,841** (+7,000 on order); $0.971 @10, $0.753 @100; Farnell UK 204 |
| KEMET RSBCC4220Z310K, PET **50 V** | 6.0 × 11 × 7.2 nominal (L up to 7.5) | yes | obsolete: last ship 30 Jun 2026 | 3,147; $0.698 @10 |
| **WIMA MKS2C042201M00KN00 / M00KSSD**, PET 63 V ±10 % | **8.5** × 14 × 7.2 | no: 1.3 mm wider | **active** | KN00 947; $1.18 @10, $0.879 @100 |
| TDK B32529D0225K000, PET 63 V ±10 % | 7.8 × 13 × 7.8 | no: 0.5 mm over on both sides | active, AEC-Q200 | 3 (16,000 due mid-2027); Farnell UK 3,608 |
| WIMA SMDTD04220XA00MT00, PET 100 V ±20 %, SMD | 12.7 × 10.2 × 6.0 | no: a new footprint | active | 2,028; $1.89 @10 |

Ruled out: Panasonic ECQ-V1H225JL (obsolete, 7.5 mm pitch), Vishay MKT1820 (10 mm pitch at 2.2 µF / 63 V), Würth
(no 2.2 µF at 5 mm), KEMET R82 2.2 µF (50 V, MOQ 1,150), WIMA MKS2D 100 V (11 × 16 × 7.2).

## 3. The options

**FE1 (proposed): keep the footprint, change the order code to KEMET MMK5225K63J06L4BULK, and buy the console's lifetime
quantity now.**
- **The part:** the same dielectric, voltage, tolerance, pitch and box as the WIMA, so nothing on any board changes.
- **The catch:** it is obsolete too. Mouser's 1,841 cover the console's 108 + spares many times over, so buy them all
  in one order: `bom/order_bom.csv` asks for 114. The phase-1 order takes 5 of them (stage A 5, a second strip 5).
- **Later:** if a board is ever re-spun after the stock is gone, FE2 is the way out.

**FE2 (alternative): widen the footprint to `C_Rect_L7.2mm_W8.5mm_P5.00mm` and use the active WIMA M-box.**
- **Compatibility:** the 8.5 mm footprint also takes the KEMET MMK, so the boards would accept both parts.
- **What the trial found:** it doesn't drop in. On each board one part then collides, and the placement guard refuses
  the board:
  - **strip:** R5's turn meets the wider C13;
  - **group:** C76's E9b spot meets C21, which the packer moved;
  - **master:** C82's spot meets the wider C66.
- **To work it up:** a few local moves per board, then the usual checks.
- **The panel side:** unchanged. The parts are on the bottom; 14 mm against 13 mm tall needs no other change.

**Neither:** build with the WIMA while any stock turns up (none found).

## 4. Checks on the trial tree (FE1)

- **Regenerated:** strip, group and master, 0 mismatches; only the MPN field changed. BOMs re-exported.
- **Re-placed:** for the MPN field; no footprint moved on any board.
- **`bom/order_bom.csv`:** 114 KEMET MMK5225K63J06L4BULK (108 + 6 spares). **`bom/order_phase1.csv`:** 5 / 0 / 5.
- **`check_all --full`:** 61 / 61.

## 5. On sign-off

- Apply the patch, then regenerate, re-export and re-place the three boards for the MPN field.
- Re-run `order_bom.py` (both modes) and the phase-1 pricing.
- **Update:** `docs/proposals/film_np_proposal.md` (an F1 note), `docs/build/sourcing.md`, CLAUDE.md (the film decision's order code), the strip
  spec's parts note and master spec §27 if it names the part.
- **Order the lifetime quantity** (about 120) with the stage-A order.

## Sign-off

- [x] **FE1** as proposed (Ruslan, 2026-10-29): KEMET MMK5225K63J06L4BULK in the same footprint; buy the console's quantity now.
- [ ] **FE2** instead: widen the footprint to 8.5 mm for the active WIMA M-box (work up the local moves first).
- [ ] Both: FE1's order code now, and FE2's footprint at the next board revision.

## Applied (2026-10-29)

- **Applied:** the patch.
- **Regenerated and re-exported:** strip, group and master (netlists unchanged but for the MPN field, 0 mismatches),
  their BOMs and PDFs; `bom/order_bom.csv` (114 KEMET MMK5225K63J06L4BULK), `bom/order_phase1.csv` and `bom/order_phase1_prices.csv` (stage A about $420 in
  parts + $70.50 PCBs, stage B $311, a second strip $290).
- **Re-placed:** for the MPN field; no footprint moved on any board.
- **Documents:** strip spec (§9 note, parts list), master spec, `docs/proposals/film_np_proposal.md` F1, `docs/build/sourcing.md`, CLAUDE.md.
- **To do when ordering:** buy the console's quantity (about 120) in one Mouser order; FE2 stays the way out if a board
  is re-spun after the stock is gone.
- **Since the merge with RV7 (2026-11-03):** six more of these caps, the AFL DC blocks C98 on each group and C194 / C195 on
  the master: the console needs 114 and `bom/order_bom.csv` buys 120.
