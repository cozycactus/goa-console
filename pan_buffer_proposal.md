# Pan buffer L beside the pan pot (proposal PAN1, 2026-10-26)

**Signed off by Ruslan on 2026-10-26 and applied the same day (strip spec v4.8); see "Applied" at the end.** The change
is `pan_buffer_proposal.patch` (tools only: `gen.py`, `strip_draw.py`, `place_strip.py`). It changes the strip's unit
assignment (which op-amp half does what), not its parts.

## Why

`routing_guide.md` lists the pan buffer L input as the strip's longest high-impedance line:

- **The net:** RV8's L wiper → C79 (10p C0G) → U2B's + input. 165 mm (Manhattan MST of the pads).
- **The cause:** U2 sits at the fader end (y 403), because its A half is the fader post-amp. The pan pot RV8 is at y 252.
- **Its impedance:** the pan wiper, up to 2.5 kΩ (10K lin, fed from POST's low impedance) at mid rotation.
- **What's close to it:** the nearest aggressor pad is +5VL at C61 (U11's DG413 decoupler), 2.9 mm from U2 pin 5.
- **The R side:** pan buffer R (U3A) is already beside the pot: U3 at y 240.

## Options tried

All three were measured with `tools/emc_check.py` and the placer report, against the committed board.

| | What | Result |
|---|---|---|
| (a) | Both pan buffers in U3; the mute buffer (U3B) moves to U2B | Rejected. MUTEOUT 89 → 153 mm, PRE 181 → 369 mm, HOUT 210 → 407 mm; the mute buffer drives the pre aux pots (U3B had the strip's lowest margin, 59.8°), so it should not move away from them |
| (b) | Move U2 to the pan pot | Rejected without a run. U2A is the fader post-amp: the fader wiper FPIN (72 mm, up to 2.5 kΩ) would become the long line instead |
| **(c)** | **Pan buffer L into U8B, which was the tied-off spare; U2B becomes the spare** | **Proposed.** U8 already sits beside U3 and RV8 (y 240); no other line gets longer than a few mm |

## PAN1 (proposed)

**Schematic** (netlist change, no part change):
- **U8B:** pan buffer L, + input PANWL, output PBL. Was the spare (+ to GNDA, output on its − input).
- **U2B:** the spare now, tied off the same way.
- **Unchanged:** C79 (10p C0G at the + input), C16, R36. The BOM and the part count (290) don't change.
- **Drawn:**
  - page 12 shows U8B as pan buffer L;
  - page 10 shows the U2B spare, with a note;
  - page 11 no longer shows the U8 spare.

**Placement** (`place_strip.py`):
- U2, U3 and U8 are pinned where they were. So are U2's post-amp parts (R18, R38, JP1, R44), which would otherwise
  re-pack into the slot C79 leaves; R38 had ended up beside C61.
- C79 goes in the slot between U8 and U3, 3.1 mm from U8 pin 5. R70 (DIRSRC's 100K, DC only) moves below U8.
- C16 (PBL coupling cap, 100 µF THT, bottom side) moves to the nearest free bottom spot, (16.0, 202.3). The bottom
  near U8 / U3 holds C17 and C96; every spot nearer is under RV8's or a key's leads, or by H3.
- C17 is pinned at its old spot.

## Measured (trial board vs committed)

| | Committed | PAN1 |
|---|---|---|
| Pan L + input (wiper → C79 → pin 5), mm | **165** | **24** |
| Nearest aggressor to it | +5VL (C61) at 2.9 mm | D7 anode (R77) at 11.6 mm |
| C79 to its + input pin | 3 mm | 3.1 mm |
| Pan L output → C16 (op-amp output, low impedance), mm | 28 | 47 |
| PANL (after C16: 100 µF from the op-amp, 47K), mm | 188 | 137 |
| DIRSRC (U8A + input), mm | 50 | 40 |
| PRE / DO_T / DO_R, mm | 181 / 86 / 76 | 188 / 89 / 80 |
| MUTEOUT, FPIN, POST, HOUT, ±VA, +5VL | | unchanged |
| Parts moved | | 8: C16, C79, R70 and five resistors of the y 196 row (R13, R72, R73, R95, R96) shifted 3.5 mm along the row, clear of C16's leads |
| DRC / parity | 0 / 0 | 0 / 0; footprint links 290 / 290 |

`emc_check.py` before → after: the U2B + input row (2.9 mm from +5VL) is gone, and nothing new enters the twelve closest
couplings. The entry runs change by under 1 mm (DO_T / DO_R filters 66.1 / 64.6 → 66.5 / 65.4 mm). The placer report is
unchanged except for C79: decouplers 3.1 / 10.0 / 14, high-Z inputs 10.4 / 258.6 / 28 (SIG_B, MET1).

## Checks on the trial

- **Schematic:** 851 pins, 0 mismatches; check_fp 290 parts, 0 problems; ERC 0.
- **Sims:** `sim_netlist.py` 39/39, `sim_console.py` 35/35 (pan law, PAN switch, routing and noise unchanged).

- **Stability:** TI OPA161x model, `sim/review/strip/run_all.py none`, all 21 states, run on the trial netlist.
  - **Pan buffer L in U8B:** 80.2° in most states, 82.2° hard left, 87.5° hard right; ≤ 0.73 dB closed-loop peaking.
    These are exactly the values U2B had.
  - **The spare, now U2B:** 86.8°, as U8B was.
  - **Every other unit:** the same as on the committed netlist. Checked by re-running c01, c13 and c14 on the committed
    netlist, where only U2B and U8B swap.
  - **What the deck doesn't model:** trace capacitance. PAN1 helps there: about 1.6 pF of trace on the + input instead
    of about 10.7 pF (0.065 pF/mm × 24 vs 165 mm), beside C79's intended 10p.
  - **A side finding:** the local `sim/review/strip/results_none.json` (gitignored, like every results file there) dated from strip v4.1 (2026-10-23). Today's
    netlist gives U3B 59.8° in the direct-out-at-top states, as the design review recorded, plus U16 86.2° and U7B
    86.4° in c13. The file isn't PAN1's to change; refresh it when PAN1 is applied.

## What it does not change

- **Electrical:** pan, levels, noise, current draw. The spare half moves from U8 to U2, and an OPA1612's tied-off
  half draws the same quiescent current as before.
- **The BOM, the panel, the jack board.**

## Sign-off

- [x] **PAN1:** pan buffer L in U8B, U2B the spare; the placement as above.

## Applied (2026-10-26)

- **Change:** the patch as tried; the schematic revision goes to 4.8 with the spec.
- **Netlist:** identical to the trial's: 851 pins, 0 mismatches; check_fp 290 / 0; ERC 0. The BOM is unchanged.
- **Sims:** `sim_netlist.py` 39/39, `sim_console.py` 35/35.
- **Stability:** the trial's 21-state TI run applies as-is and is now the local `sim/review/strip/results_none.json` (gitignored; re-run `run_all.py none` to reproduce it). Every unit
  is ≥ 59.8°, ≤ 1.61 dB peaking.
- **Board:** re-placed identically to the trial (8 parts moved); 0 DRC violations, 0 parity issues, 290 / 290 links;
  the jack board is unchanged. `emc_check.py` gives the same output as the trial.
- **Exports and docs:** `render/strip.json` re-exported. Updated: the spec (§12, §14, §16 routing rule, §17),
  `routing_guide.md` and CLAUDE.md.
