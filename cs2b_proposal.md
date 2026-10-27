# CS2b: the Delta's pan law on the group's sub pan (proposal, 2026-10-28)

**Signed off by Ruslan on 2026-10-28 (as proposed) and applied the same day; see "Applied" at the end.** The change is
`cs2b_proposal.patch`. It touches tools only: `frags.py`, `gen_group.py`, `place_group.py` and `sim_console.py`.

**Calculation and simulation:**
- `sim/review/cs2/group_pan.py`, with its output in `group_pan.out` (it reuses `pan_law.py`'s network);
- the group deck with TI's OPA161x and OPA1656 models: `sim/review/group/sweep.py pots none 0.08` (18 configurations)
  and `loads none 0.08` (12, with 22 / 47 pF more on every long output net);
- the netlist checks and `check_all --full` on a trial tree.

## 1. Why

**CS2 left the groups behind.** Strip v5.4 gave every strip the Delta's −4.4 dB law (`cs2_proposal.md`); its §3 left
"the groups' sub pan to MIX (−6 dB)" unchanged and named this follow-up.

**Our own spec asks for it.** Master spec §12: "the pan, pan buffers, AC coupling and routing switch copy the strip".
Since CS2 they no longer do. RV2 (ALPS RK09L, linear 10K dual) feeds unity followers U3B / U5A, a plain −6 dB.

**The parent's group module pans at −4.6 dB.** ED2778A (`ref/Sndcft_DeltaDLX_Schems.pdf` p.6, read at 300 dpi):
- **MONITOR PAN:** VR10, a 10K LIN dual with a centre detent. R38 / R39 3K9 run from the source to each wiper, and each
  wiper goes through R40 / R41 8K2 into MIX L / R. It is passive, with no buffer.
- **RETURN PAN:** the same network (R17 / R18 3K9, R19 / R20 8K2).
- **The law:** at centre the wiper sits at 0.586 of the source, −4.64 dB against hard over.

| Sub pan | centre | hard over | law | power sum at centre |
|---|---|---|---|---|
| ours (as built) | −6.02 dB | 0 dB | 6.02 dB | −3.01 dB |
| **CS2b (the strip's network)** | **−2.71 dB** | **+1.73 dB** | **4.44 dB** | **−1.43 dB** |
| ED2778A (passive), for reference | −4.64 dB | 0 dB | 4.64 dB | −1.63 dB |

**What it does in use.** Take a strip panned centre into SUB 1, with the sub panned centre into MIX. Against the same
strip routed to MIX directly:

| | via the group | direct | the group path below direct |
|---|---|---|---|
| before CS2 | −12.0 dB | −6.0 dB | 6.0 dB |
| today (strip v5.4) | −8.7 dB | −2.7 dB | 6.0 dB |
| **CS2b** | **−5.4 dB** | **−2.7 dB** | **2.7 dB** |

A centred source through a group sits 6 dB under its direct level today, where the parent's group pan costs 4.6 dB.

## 2. The circuit: the strip's (CS2), not ED2778A's

```
S_POST ── RV2 (10K B dual) ── wiper ──┬── U3B + (×1.22: R124 2K2 out → −, R125 10K − → GNDA, C96 22p C0G across R124)
                                      └── R123 3K3 ── U3B out ── C29 100µ ── S_PANL     (R side: U5A, R126-R128, C97)
```

**Why the strip's network:**
- **One law across the console:** 4.44 dB on the strips and the groups. ED2778A's is 4.64 dB, a 0.2 dB difference.
- **The buffers stay:** U3B / U5A drive the 100 µF + 47K coupler and the routing 4K7s, as now. A passive network would
  need its levels worked out again into our 4K7 virtual earth.
- **It's proven:** the values and the op-amp are the strip's. The 22 pF is what CS2 found necessary. Without it, TI's
  model gave 32° at centre and 14° hard over on the strip, against 81.6-85.3° with it.

**Parts:** 6 resistors and 2 C0G per group:
- R123 / R126 3K3, R124 / R127 2K2, R125 / R128 10K, C96 / C97 22p C0G;
- made last (after `drv_loop_rs()`), so no other ref moves;
- the 10p on each + input (C25 / C26, MG5) stays.

## 3. What changes

**Levels** (0 dBu in, faders at "0"):
- sub to MIX: **+3.31 dB** at centre, **+1.73 dB** hard over;
- `sim_console`'s SUB 1 → MIX check moves by GPANC = 3.32 dB. It reads −0.75 dBu at main L, within the new
  −1.11 / −0.41 dBu window.

**Headroom:**
- **The pan buffers:** hard over they carry S_POST +1.7 dB, so they clip 1.7 dB before the sub post-amp, as the strip's
  pan buffers do since CS2.
- **The MIX bus:** a centred group adds 3.3 dB more into it, as a strip has done since CS2 (CS3: 26.2 dB to clip per
  centred source).

**Noise:** it rises with the signal, so S/N is unchanged.

**Not changed:**
- the sub output (DRV135) and AFL: they tap S_POST, ahead of the pan (the insert is earlier still);
- the returns: they have no pan;
- the aux master;
- the panel: the sub pan is unmarked but for its centre detent.

## 4. Schematic and placement (trial)

**Schematic:**
- 805 pin entries, 291 parts (+8);
- 0 mismatches, check_fp 0, ERC 0;
- 13 pages (12 before): each buffer is drawn as on the strip (2K2 ∥ 22p, the 10K, the 3K3 back to the wiper), so the
  sub block grows and the later blocks move one page on.

**Placement** (by `moves_only`; nothing else moved):

| Part | Spot | Farthest pad from its pin |
|---|---|---|
| C96, R124, R123 | bottom, under U3 | U3.6 (−): C96 4.5, R124 5.8 mm |
| R125 | top, beside U3 | U3.6: 5.6 mm |
| C97, R127, R126 | bottom, under U5 | U5.2 (−): C97 3.7, R127 5.9 mm |
| R128 | top, beside U5 | U5.2: 5.8 mm |

- **The 3K3s:** 5.3 / 4.9 mm from the + input pins.
- **The placer report:** decouplers unchanged (2.9 / 5.1 / 1). The two − inputs are new high-Z inputs (37 → 39), and
  inputs over 6 mm stay at 26. R124 was moved 0.35 mm from its first probed spot to get from 6.1 to 5.8 mm.
- **Netrules:** the two new − input nodes are HighZ.

## 5. Checks

**Stability** (group deck, TI's models, board 0.08 pF/mm):

| Unit | pots: PM min / peaking max | loads (+22 / 47 pF): PM min / peaking max |
|---|---|---|
| U3B pan buffer L | 74.5 → 74.5° / 0.77 → 0.52 dB | 54.1 → 55.3° / 2.02 → 1.84 dB |
| U5A pan buffer R | 75.2 → 75.3° / 0.76 → 0.50 dB | 54.6 → 55.9° / 1.97 → 1.78 dB |
| U3A sub post-amp (drives the pan pot) | 67.7 → 68.0° / 0.89 → 0.94 dB | 65.3 → 65.3° / 1.55 → 1.60 dB |

- **Every other OPA1612 unit is unchanged** in both sets.
- **The return followers** (OPA1656) ran on TI's model this time. It reached an operating point in this deck today; the
  2026-10-26 baseline used the fitted macro, which reads lower (about 53° against 85°). On the committed netlist the
  same TI model reads 84.9 / 84.1 / 82.9° (U10A / U10B / U14B), the same as the trial, so CS2b doesn't touch them.

**`sim_console`:** 35/35.

**`check_all --full`:** 61 / 61.
- **Group:** 805 pins, 0 mismatches; 291 / 291 footprints linked; 0 DRC / parity; route_check 0.
- **Every other board:** unchanged.

## 6. On sign-off

- Apply the patch and regenerate the group. Re-export it (netlist, BOM, PDF), re-place it, re-run netrules and
  `order_bom.py` (+4 × 3K3, 2K2, 10K and 22p C0G over the four groups).
- **Update:**
  - master spec §12 (the pan law; "RD902F pan" in its parts line is the RK09L since R2);
  - `console_survey.md`'s CS2 note;
  - CLAUDE.md.

## Sign-off

- [x] **CS2b** as proposed: the strip's −4.4 dB law on every group's sub pan (R123-R128, C96 / C97). Ruslan, 2026-10-28.
- [ ] Neither: keep −6 dB on the groups, and record it as a decision (the sub pan then no longer copies the strip,
  against master spec §12).

## Applied (2026-10-28)

- **Applied:** the patch.
- **Regenerated and re-exported:** the group schematic (805 pins, 291 parts, 0 mismatches, check_fp 0, ERC 0, 13
  pages), its netlist, BOM (+2 × 3K3, 2K2, 10K and 22p C0G per group), PDF and `order_bom.csv`.
- **Re-placed:** only C96 / C97 and R123-R128 are new; no other footprint moved. Decouplers 2.9 / 5.1 / 1, high-Z
  inputs over 6 mm 26, as before. Netrules re-run: the two new − input nodes are HighZ.
- **Documents:** master spec §12 (the diagram, a pan-law note, the RK09L in the parts line), `console_survey.md`,
  `cs2_proposal.md`'s follow-up line, CLAUDE.md.
- **`check_all --full`:** 61 / 61. Group 805 pins, 291 / 291 footprints linked, 0 DRC / parity, route_check 0;
  `sim_console` 35/35; every other board unchanged (1514 / 1514 links in all).
