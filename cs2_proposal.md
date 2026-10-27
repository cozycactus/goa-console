# CS2: the Delta's −4.4 dB pan law (proposal, 2026-10-27)

**Not signed off.** The change is `cs2_proposal.patch`. It touches tools only: `gen.py`, `strip_draw.py`,
`place_strip.py`, `sim_netlist.py` and `sim_console.py`. It was applied to a trial tree, checked (§5) and reverted, so
nothing in the design has changed. A taste decision: yours.

**Calculation and simulation:**
- `sim/review/cs2/pan_law.py`, with its output in `pan_law.out`;
- TI's OPA161x model over the strip's 21 configurations (`sim/review/strip/run_all.py none`);
- the netlist checks.

## 1. Why

`console_survey.md` §5 CS2: the Delta (ED3344C) and Venue Theatre (ED3151) pan at −4.4 / −4.5 dB. Ours is a linear dual
into unity followers, a plain −6 dB. `delta_clone_comparison.md` never recorded that as a decision; it looks like a
transcription loss.

| | centre | hard over | law | power sum at centre |
|---|---|---|---|---|
| ours (as built) | −6.02 dB | 0 dB | 6.0 dB | −3.0 dB |
| **Delta's network** | **−2.71 dB** | **+1.73 dB** | **4.4 dB** | **−1.4 dB** |
| constant power, for reference | −3.01 dB | 0 dB | 3.0 dB | 0 dB |

The "power sum" column is L² + R² against hard over. A centred mono synth sits 1.6 dB higher against panned stereo
sources than it does today, as on the parent console.

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

A follow-up could give the groups the same law.

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
  - master spec §27 (the bus level) and the CS3 note in `console_survey.md`;
  - the jig spec's routing level (+3.8 → +7.1 dBu on the bus);
  - `delta_clone_comparison.md`;
  - CLAUDE.md.
- `panel_print` needs nothing: the pan is unmarked but for its centre detent.

## Sign-off

- [ ] **CS2** Option A as proposed: the Delta's law on every strip (R136-R141, C105 / C106); PAN off stays at POST.
- [ ] Option B as well: the PAN-off feed matched through U2B with a 33 µF D8 coupler (departs from the 100 µF rule).
- [ ] Neither: keep the −6 dB law, and record it as a decision.
