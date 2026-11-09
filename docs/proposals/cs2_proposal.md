# CS2: the Delta's −4.4 dB pan law (proposal, 2026-10-27)

**Signed off by Ruslan on 2026-10-27 (Option A: the Delta's law; PAN off stays at POST) and applied the same day as strip
v5.4; see "Applied" at the end.** The change is `archive/patches/cs2_proposal.patch`. It touches tools only: `gen.py`,
`strip_draw.py`, `place_strip.py`, `sim_netlist.py` and `sim_console.py`.

**Calculation and simulation:**
- `sim/review/cs2/pan_law.py`, with its output in `pan_law.out`;
- TI's OPA161x model over the strip's 21 configurations (`sim/review/strip/run_all.py none`);
- the netlist checks.

## 1. Why

`docs/studies/console_survey.md` §5 CS2: the Delta (ED3344C) and Venue Theatre (ED3151) pan at −4.4 / −4.5 dB. Ours is a linear dual
into unity followers, a plain −6 dB. `docs/studies/delta_clone_comparison.md` never recorded that as a decision; it looks like a
transcription loss.

| | centre | hard over | law | power sum at centre |
|---|---|---|---|---|
| ours (as built) | −6.02 dB | 0 dB | 6.0 dB | −3.0 dB |
| **Delta's network** | **−2.71 dB** | **+1.73 dB** | **4.4 dB** | **−1.4 dB** |
| constant power, for reference | −3.01 dB | 0 dB | 3.0 dB | 0 dB |

The "power sum" column is L² + R² against hard over. A centred mono synth sits 1.6 dB higher against panned stereo
sources than it does today, as on the parent console.

### The parent's circuit, re-read from the drawings (2026-10-27)

**ED3344C** (`ref/Sndcft_DeltaDLX_Schems.pdf` p.17, rendered at 300 dpi):

| Part | What the drawing shows |
|---|---|
| VR10 | "10KB CD" dual. Both gangs' tops on the post-fader line, marked −2 dBu; bottoms to ground |
| IC11-A / IC11-B (TL072) | Non-inverting buffers. R122 / R123 2K2 from the output to −in, R124 / R125 10K from −in to ground: 1.22× |
| R120 / R121 3K3 | From each buffer's output to its + input, which is the wiper (VR10-B pin 5 / VR10-A pin 2) |
| C54 / C55 220 µF + R67 / R68 47K | The bus coupling: POST PAN R / L |
| IC6-B (TL072) | The post-fader feed. R145 1K8 / R146 10K, +1.4 dB, its output marked "−0.5 dB": POST FADER through C56 220 µF / R69 47K |
| SW5-A / SW5-B (PAN) | Pick POST PAN L / R (latched) or POST FADER (unlatched) for the groups only: SW5-B → R126 / R127 10K 0.5 W → SW6-B "2" / SW7-A "4". MIX takes POST PAN L / R directly, always panned, as our SW14 |

**The 200 Delta Technical Manual** (ZZ2593, printed p.56, Part 2 PDF p.6) describes the pan buffers as an active design
for better rejection (about 85 dB cut-off). It calls the law resistors the parts that set the centre gain drop, fed
from the buffer outputs rather than the pot tops.

So the CS2 network is the parent's, value for value:
- the buffers in OPA1612 (TL072 on the Delta);
- C105 / C106 added for the OPA1612's faster loop;
- AC coupling at the strip's 100 µF.

The law follows from the drawing: centre −2.71 dB, hard +1.73 dB. The PAN-off stage (Option B) is the parent's IC6-B at
+1.4 dB; our U2B would use 1.22× to match the buffers exactly.

### The 200 Delta (Technical Manual ZZ2593, checked 2026-10-27)

The 200 Delta's own input drawing, ED2774 (manual p.69), is listed in the manual but not in the scanned PDF (`ref/`,
the iCloud copy). The rest of the manual agrees with the Theatre:

- **Printed p.34** (Standard Input Module D202, "Routing"): at centre both sides get equal levels with a 4.5 dB drop
  against fully clockwise or anticlockwise. This is the law stated outright, the same as the Theatre's network
  (4.44 dB).
- **Printed p.56:** the law resistors set the centre drop and are fed from the buffer outputs.
- **The spare parts, printed pp.151-152** (Standard Input Module):
  - VR10 "ALPS 16MM C/D 10KB LIN X 2";
  - TL072s;
  - R39 2K2 / R40 4K7, the +10 dB post-amp named on p.56;
  - then R42 3K3, R43 2K2, R44 10K, R45 3K3, (R46 not listed), R47 10K: two law resistors and the 2K2 / 10K gain pairs;
  - R48-R53 10K 1/2 W, the routing resistors.
- **Printed p.14** (specification): panpot rejection > 85 dB at 1 kHz (> 80 dB at 10 kHz), fader rejection > 80 dB at
  1 kHz. These are jig test 15's targets.
- **No PAN switch on the 200 Delta:** the D202's switches are +48V, LINE, 5-6, PFL, ON, MIX, 1-2 and 3-4, and its
  parts list has no 1K8. Every bus is panned. The PAN switch and its +1.4 dB IC6-B feed came with the Theatre
  (ED3344C), our decision 6.

### How the −6 dB got in (git history, checked 2026-10-27)

The −6 dB was never a decision. It is half of the Delta's pan stage, copied without the other half.

1. **v3, the initial commit (`4e2640c`, 2026-10-19), before the Delta clone.**
   - **The changelog:** "Added pan buffers L/R. (ED3344C, IC11)".
   - **The drawing:** IC2B / IC3A as plain followers.
   - **The stated reason:** "the buffers isolate the pan law from the routing load", which a follower does.
   - **The law was left open:** "VR7: 10K dual-gang pan pot (constant-power / MN taper, or linear 'B' with the Delta's
     buffer arrangement)". So linear B was only right together with the Delta's arrangement, and that arrangement was
     never drawn: R122 / R124 for 1.22× and the R120 / R121 3K3 law resistors.
2. **v4.0, the Delta clone (`a38b542`, 2026-10-22).**
   - **Strip spec §12:**
     - RV8 becomes a "10K B dual" and the condition is dropped;
     - the followers stay;
     - a new sentence, "MIX is always panned (−6 dB at centre with the linear pot)", states the result as a fact.
   - **`docs/studies/delta_clone_comparison.md`:**
     - Its stage table reads the Delta as "pan buffers with gain" and ours as "unity followers", and proposes "Keep our
       buffers; add PAN switch (decision 6)". The gain was seen, but not what it is for. The 3K3 law resistors aren't
       listed.
     - Decision 6 covered only the PAN switch, so the law never reached sign-off.
   - **The PAN-off feed:** the Delta takes it from IC6-B at +1.4 dB (1K8 / 10K) to match its +1.7 dB buffers. It was
     copied as plain POST.
   - **The checks:** the same commit's verification targets fixed "mix bus out +3.8 dBu (pan centre)", the −6 dB
     value, in `sim_netlist.py`. Every later check confirmed the law instead of questioning it.
3. **The ALPS RK09L (`17d7614`, 2026-10-25).** The pan pot stayed linear B (it was picked for its centre detent),
   still into followers.

So the fix restores the omitted half: the 1.22× gain and the 3K3s. The same omission covers the PAN-off gain (Option
B). The Delta's own IC6-B is +1.4 dB against its buffers' +1.7 dB, so even the parent leaves PAN off 0.3 dB under a
hard pan.

## 2. The circuit (the Delta's, ED3344C)

U8B / U3A go from followers to 1.22× stages, and a 3K3 from each output back to its wiper lifts the middle of the
travel:

```
POST ── RV8 (10K B dual) ── wiper ──┬── U8B + (×1.22: R137 2K2 out → −, R138 10K − → GNDA, C105 22p C0G across R137)
                                    └── R136 3K3 ── U8B out ── C16 100µ ── PANL      (R side: U3A, R139-R141, C106)
```

- **The law:** W = x·Vin / (1 − 0.22·x(1 − x)·10K / 3K3). At centre W = 0.6, so the output is 0.732 (−2.7 dB); hard
  over it is 1.22 (+1.7 dB).
- **The 22 pF (C105 / C106)** is needed:
  - **Without it:** the OPA1612's input capacitance against 2K2 ∥ 10K puts a pole at the 15-20 MHz crossover. The TI
    model then gave 32° at centre and 14° hard over, with 12 dB of peaking.
  - **With it:** 81.6-85.3°.
- **Parts:** 6 resistors and 2 C0G per strip: R136-R141, C105 / C106. Nothing else moves.

**PAN off is not matched (Option A, in the patch).** SW14 unlatched still sends POST, unpanned, to the subgroups.
That is now 1.7 dB under a hard pan (it used to equal one) and 2.7 dB over a centred one.
- **Option B:** the Delta matches it with a 1.22× stage (IC6-B). Ours would be U2B, the spare since PAN1: 2K2 / 10K
  plus a bus coupler.
- **What blocks it:** the signed rule asks for 100 µF NP + 47K on every node feeding the bus, and no D10 can fits
  anywhere on the strip with both sides free (probed). A D8 33 µF fits 26 mm from U2, with its LF pole at 2.2 Hz
  into the two sub buses' 4K7s.
- **If you want B:** say so and I'll add it. It departs from the 100 µF rule for that one node.

## 3. What changes

**Levels** (0 dBu in, faders at "0"):

| | centre | hard over |
|---|---|---|
| mix and subs per source | +3.3 dB | +1.7 dB |
| main L, one centred source | −0.8 → +2.5 dBu | |
| main L, hard left | +5.2 → +6.9 dBu | |

**Headroom** (`sim/review/cs3/bus_headroom.py`'s figures):
- summer per centred source: 29.5 → 26.2 dB to clip;
- 24 strips at nominal: 15.7 → 12.4 dB.

The master chain stays balanced: every stage rises by the same 3.3 dB, so the XLR still clips last. Pull the master
fader down by about 3 dB for the same output.

**Noise:** it rises with the signal, so S/N is unchanged. `sim_console`: main L, 24 strips: −79.2 → −75.8 dBu against
a 3.3 dB higher programme.

**The overload LED:** hard over, the pan buffers clip 1.7 dB before POST. The LED taps FPOST, not the buffers, so a
hard-panned signal in that 1.7 dB window clips without lighting it.

**Not changed:**
- the groups' sub pan to MIX (−6 dB, `master_lib`);
- aux sends and PFL;
- the direct out.

A follow-up could give the groups the same law (done: CS2b, `docs/proposals/cs2b_proposal.md`, applied 2026-10-28).

## 4. Schematic and placement (trial)

**Schematic:**
- 937 pin entries, 325 parts (+8). The pan drawing shows each buffer's 2K2 / 10K, the 22 pF and the 3K3 to the wiper.
- 0 mismatches, check_fp 0, ERC 0.

**Placement:**
- By `moves_only`, on the bottom under U8 / U3, 0.3-6.6 mm from their pins.
- C106 took R140's probed spot (4.0 mm from U3) and R140 went 6.6 mm out, so the C0G is the nearer of the two.
- Nothing else moved; the decoupler report is unchanged.

## 5. Checks on the trial tree

- **Stability (TI OPA161x, 21 configurations):**
  - U8B 81.6-85.3° and U3A 82.8-84.9° (80.2-87.5° before), at most 0.42 dB of peaking;
  - every other unit unchanged: the minimum is still U3B 59.8° (direct out at the top), the most peaking still U8A's
    1.61 dB.
- **`sim_netlist` 41/41:**
  - MIX at centre +7.1 dBu;
  - hard left +11.5 dBu, the far side −108.5 dB;
  - PAN off +9.8 dBu.
  - There are two new checks; the level targets moved with the law.
- **`sim_console` 35/35:** the level targets are shifted by PANC = +3.27 dB at centre and PANH = +1.68 dB hard over,
  both from the measured law.
- **`check_all --full`:** 61 / 61. The strip has 325 / 325 linked and 0 DRC / parity, and every other board is unchanged.

## 6. On sign-off

- Apply the patch, bump the strip to v5.4, then regenerate, re-export and re-place, and re-run netrules.
- Update:
  - strip spec §12 and the IC table;
  - master spec §27 (the bus level) and the CS3 note in `docs/studies/console_survey.md`;
  - the jig spec's routing level (+3.8 → +7.1 dBu on the bus);
  - `docs/studies/delta_clone_comparison.md`;
  - CLAUDE.md.
- `panel_print` needs nothing: the pan is unmarked but for its centre detent.

## Sign-off

- [x] **CS2** Option A as proposed: the Delta's law on every strip (R136-R141, C105 / C106); PAN off stays at POST. Ruslan, 2026-10-27.
- [ ] Option B as well: the PAN-off feed matched through U2B with a 33 µF D8 coupler (departs from the 100 µF rule).
- [ ] Neither: keep the −6 dB law, and record it as a decision.

## Applied (2026-10-27, strip v5.4)

- **Applied:** the patch, plus revision 5.4 in `gen.py`.
- **Regenerated and re-exported:**
  - strip netlist (937 pins, 0 mismatches) and its BOM: +2 × 3K3, 2K2, 10K and 22p per strip;
  - the PDF;
  - `bom/order_bom.csv`.
- **Re-placed:** only R136-R141 and C105 / C106 are new. Netrules re-run.
- **Documents:**
  - strip spec v5.4 (changes, §12, IC table, §17);
  - master spec §6 (mono levels);
  - jig spec 4.1 (routing levels);
  - the erratum in `docs/studies/delta_clone_comparison.md`;
  - CLAUDE.md and `docs/studies/console_survey.md`.

