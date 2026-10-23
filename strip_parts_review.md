# Strip review — op-amp stability and part ratings (strip v4.0)

Reviewed 2026-10-23 for sign-off. This follows the master parts review (`master_parts_review.md`), which found
OPA1612 stages with resistive feedback and no capacitor ringing at 10–15 MHz in TI's model, and listed the strip's
EQ and KHN stages as the same class. The strip is signed off, so nothing here has been changed yet: the changes wait
for your sign-off.

Method:
- **Stability:** every OPA1612 unit on the strip (20) with TI's OPA161x macromodel (SBOM396G) in the real network. The
  decks are built from `channel_strip.net` / `jack_board.net` by the same code as `tools/sim_netlist.py`.
- **Loop gain:** measured with a Tian probe at each output, over 21 pot / switch / cable states.
- **Overshoot:** checked with a 10 mV step.
- **Ratings:** a separate audit of ratings and the BOM against the datasheets.
- **Skeptic:** a second reviewer re-derived every stability verdict with two other methods (its own MNA return
  ratio, an independent double-injection deck) and re-checked the ratings findings. All verdicts held; where it
  corrected a number, this document uses the corrected one.

Scripts: `sim/review/strip/` (last section).

## Summary

| # | Finding | Severity | Fix |
|---|---------|----------|-----|
| 1 | Delta EQ stages U6A, U6B, U7A (22K / 22K, no cap): −3 to −5° phase margin in every state; U7A −20 to −27° with an insert lead | blocking | 10p + 10p across both 22Ks of U6A and U6B; 22p across R67 (U7A) |
| 2 | KHN summers U12A, U13B: 2.4–3.2°; negative with 2 pF of board stray | blocking | 10p across the feedback 10K and 22p from the + input to AGND |
| 3 | Receiver U1A: C7 33p across R7 only. 45° margin, and the ground-compensation CMRR collapses with frequency (59.7 / 39.7 / 33.7 dB at 1 / 10 / 20 kHz) | important | 33p across R9 (+ input to AGND): 85°, CMRR 86 dB flat |
| 4 | Followers fed from pot wipers or 4K7 (U2A, U2B, U3A, U3B, U8A): 18–51°, worst U8A 18.6° with a short direct-out lead | important | 10p (22p on U8A) from the + input to AGND |
| 5 | Long op-amp output nets on the placed board (POST, MUTEOUT, PANL/R, PRE: 110–270 mm) | routing rule | keep each ≤ ~22 pF; ≥ 55° up to 47 pF with fixes 1–4 |
| 6 | R15 1K: OL LED at ~14 mA, 190–215 mW in an 0805 (152–172 %), LM393 output beyond its guaranteed sink | important | 4K7 (as the other LEDs) |
| 7 | +5VL rises above V+ at every power-down (DG413 VL abs max is V+ + 0.3 V). Master too | minor | BAT54 from +5VL to +VA, strip and master |
| 8 | RET (insert return) reaches U7 pin 5 with no series resistance | minor | 1K in series |
| 9 | BOM: no voltage or dielectric on ceramics (30 of 33 100n at 16–17 V); MPN gaps; DNP parts counted | minor | BOM rules and MPNs (§9) |
| 10 | R1/R2 10R reach 0.125 W at the OPA1612's maximum current; R11/R71 (75R) take ~0.25 W into a shorted lead | minor | anti-surge 0805 parts |
| 11 | Spec notes: J112 mute headroom, phantom on the insert send / direct out | note | text only |

The three receivers on the master and group boards (`master_lib.receiver()`: master EXT, group returns) have the
same one-sided 33p as U1A (finding 3), and the master's +5VL the same power-down issue (finding 7).

## What to sign

- [ ] **T1** EQ stages: C0G 10p across R55 and across R54 (U6A); 10p across R59 and R58 (U6B); 22p across R67 (U7A).
- [ ] **T2** KHN summers: 10p C0G across R83 (U12A) and R92 (U13B); 22p C0G from EQ_MSP (U12 pin 3) and from EQ_LSP
  (U13 pin 5) to AGND.
- [ ] **T3** Receiver: 33p C0G across R9 (U1A_P to AGND); the same in `master_lib.receiver()` (master EXT, group returns).
- [ ] **T4** Followers: 10p C0G from PANWL (U2 pin 5), PANWR (U3 pin 3), M2 (U3 pin 5) and FPIN (U2 pin 3) to AGND; 22p
  from DIRSRC (U8 pin 3) to AGND. Optional: R71 and R11 75R → 100R.
- [ ] **T5** Routing rule in spec 16.3 (below).
- [ ] **T6** R15 1K → 4K7.
- [ ] **T7** BAT54 from +5VL (anode) to +VA (cathode), next to the 4K7, on the strip and the master.
- [ ] **T8** 1K between RET and U7 pin 5 (new net RET_IN).
- [ ] **T9** BOM rules and MPNs (§9); BOM export with DNP.
- [ ] **T10** Anti-surge 0805: R1/R2 Panasonic ERJ-P06J100V; R11/R71 ERJ-P06J750V (or …101V with T4's 100R).
- [ ] **T11** Spec notes (J112 headroom, phantom).

Applying T1–T8 changes the signed-off strip netlist. It means: `gen.py` edits, regenerating the strip and
`channel_strip_intended.json`, verify / check_fp / ERC / `sim_netlist.py`, re-placing `channel_strip_v4.kicad_pcb`
(placement only), parity DRC, and strip spec v4.1.

---

## 1. Delta EQ stages (U6A HI-MID, U6B LO-MID, U7A LF)

Each is an inverting stage with 22K in and 22K feedback and no capacitor. The − node sees 11 kΩ against about 10 pF
of input capacitance (Cdiff 8 pF + Ccm 2 pF): a 1.45 MHz pole in the feedback path, inside the 40 MHz unity-gain
bandwidth.

- **Phase margin:** −3.3 to −4.5° in every pot and switch state. U7A drives the insert send through 75R and falls to
  −20 to −27° with a 47–470 pF insert lead.
- **Model caveat:** TI's model leaves out the datasheet's 20 kΩ differential input resistance. With it, U6A, U6B and
  U7A without a lead come out at +3 to +6° instead of oscillating, so call these "zero margin". U7A with a lead stays
  at −20° either way.
- **Fix, U6A / U6B:** 10p across both 22Ks of each stage (Z55 / Z54 = 1 at every frequency, so the Delta EQ is
  unchanged: ≤ 0.001 dB anywhere in 20 Hz–20 kHz). Result: 75.4° / 79.0° worst case.
- **Fix, U7A:** a single 22p across R67 beats a balanced pair with a lead (71.3° worst case with a 47 pF lead,
  1.4 dB peaking; a pair gives 60–65°). Cost: ≤ 0.03 dB and 3.5° at 20 kHz.

## 2. KHN summers (U12A HI-MID, U13B LO-MID)

Each is a 10K summer at noise gain 3 (− node 3.3 kΩ), with the + input fed from 2K2 ∥ 10K (1.8 kΩ).

- **Phase margin:** 2.4–3.2°, +26 dB at 8.7 MHz, ζ ≈ 0.02. With 2 pF of − node board stray it goes negative.
- **A feedback cap alone tops out near 55°:** the + node lag through Cdiff takes over (4.7p 55°, 22p 45°, 100p 40°).
- **Fix:** 10p across the feedback 10K plus 22p from the + input to AGND. Result: 82–83° worst case, 0.22 dB peaking.
- **Cost:** ≤ 0.084 dB at about 12 kHz with HI-MID at full cut and its frequency at CW; the 10.5 kHz HI-MID check moves
  by +0.058 dB.
- **Zero-shift variant, if wanted:** add 10p across the other two 10Ks too, and compensate the + divider (47p across
  the 2K2, 10p across the 10K): ≤ 0.0014 dB.

## 3. Line receiver U1A

C7 33p across R7 (feedback) has no partner across R9 (the + leg to ground). That unbalances the bridge:

- **CMRR:** the ground-compensation CMRR, the reason for the 0.1 % resistors, falls to 59.7 / 39.7 / 33.7 dB at
  1 / 10 / 20 kHz.
- **Stability:** the + node (5 kΩ) lags through Cdiff, giving 45° and +3.6 dB at 12 MHz.

33p across R9 matches R7·C7. Result: 85° phase margin, CMRR 86 dB flat. Cost: with Ø latched only, −0.002 dB and 1.2°
at 20 kHz. `master_lib.receiver()` has the same one-sided cap (master EXT L/R, group return L/R).

## 4. Followers on pot wipers

Cdiff from the + input to the output, against 1–5 kΩ of source, makes a lag near crossover (a bare follower bottoms
out at 38° near 2.4 kΩ). As designed:

| Stage | Worst case | With the fix |
|---|---|---|
| Pan buffers U2B / U3A | 38–40° | 77–80° |
| Fader post-amp U2A, + input FPIN (fader near "0") | 40–41° | 70–73° |
| Post-mute follower U3B | 51–54° | 72° |
| Direct-out follower U8A, with a 100 pF lead and aux 6 near 0.75 | 18.6–21°, 9–10 dB peaking | 70–71° |

The fix is 10p from the + input to AGND (22p on DIRSRC), costing ≤ 0.001 dB and ≤ 0.7° at 20 kHz. Don't go higher:
FPIN's cap sits on U3B's output when the fader is at the top, and DIRSRC's on U7B's when aux 6 is at the top (with 22p
U7B is at 59–62° in that state, the floor of the fixed set).

Board parasitics cut both ways, which is why the caps are worth fitting regardless:
- **Helps:** J112 Cdg / Cds lift U3B to 71–76° as designed.
- **Helps:** the 160 mm PANWL trace lifts U2B to 74–82°.
- **Hurts:** output trace capacitance (§5).

Optional: R71 / R11 75R → 100R, which lifts U8A to 74.5° with a short lead and costs 25 Ω more output impedance.

## 5. Routing rule: long op-amp output nets

On the placed board, several op-amp outputs drive long nets directly (the series 220 µF caps are shorts at MHz):

| Net | Driver | Length | 22 pF, as designed / fixed | 47 pF, as designed / fixed |
|---|---|---|---|---|
| POST | U2A | 200–270 mm (C15 to the pan pot, PRE/POST switches, aux pots) | 34° / 71° | 25° / 60° |
| MUTEOUT | U3B | ~200 mm to the fader | 49° / 64–72° | 42° / 55–61° |
| PANL / PANR | U2B / U3A | 110–170 mm | 32° / 70° | 23° / 58° |
| PRE | U7B | to the switches and aux pots | 63° | 53° |

Spec 16.3 should say:
- keep each of POST, MUTEOUT, PANL/R and PRE at ≤ about 22 pF (short, thin, not run over a pour for long);
- or put the long run on the high-impedance side (e.g. move the post-amp near the pot block, so the long net is
  FPIN, where shunt C helps a follower);
- or isolate U3B from the fader with a series resistor (100R costs −0.09 dB into 10K; pin 7 has to be split from
  MUTEOUT).

At 100 pF even the fixed stages are only about 40°.

## 6. OL LED current (R15)

+VL (16.75 V) → R15 1K → red LED → LM393 output (U4A). That gives 13.8–14.7 mA and 190–215 mW in an 0805 (152–172 % of
0.125 W). It is also above the LM393's 4 mA region for VOL ≤ 0.4 V and 4.6× brighter than the strip's other six LEDs
(4K7). It overheats only on a sustained overload, but it is out of rating. 4K7 gives 2.9–3.1 mA and the same
brightness as the others; 3K3 (4.3 mA) if OL should stand out. It saves about 11 mA per strip on +VL. U4 itself runs
from +VL to GNDD (17 V), inside the non-B LM393's rating.

## 7. +5VL above V+ at power-down (strip and master)

+5VL (4K7 from +VA, BZX84C5V1, about 1.3 µF) can only discharge back through the 4K7 (τ ≈ 6 ms). So at power-down,
and when the + rail is crowbarred, it lags a falling +VA by about 1.3–1.5 V. The DG413's VL absolute maximum is
(V+) + 0.3 V. A BAT54 from +5VL to +VA (anode on +5VL) holds it within 0.21–0.27 V; its reverse leakage is negligible
against the 2.4 mA zener current. The master's +5VL (for its DG413 PFL switcher) is the same circuit. Spec 2.2 / 13
say VL never exceeds V+; that holds at power-up only.

## 8. RET input protection

The insert return (J2 ring → C10 47 µF → RET) reaches U7 pin 5 with no series resistance; it is the only jack net
that reaches an IC pin directly. A fault or hot plug can push more than the OPA1612's ±10 mA input-current limit
through its input diodes. A 1K in series (R12 47K and C10 stay on RET; pin 5 on a new net RET_IN) bounds it. It adds
4 nV/√Hz: +0.013 dB on the EQ-in floor (−97.2 dBu), +0.08 dB on the bypass floor. Optional 100 pF C0G from RET_IN to
GNDA, matching the main input's C8/C9.

## 9. BOM

- **Capacitors:** every ceramic needs a voltage and a dielectric; 30 of the 33 100n parts sit at 16.2–16.9 V. Rule:
  ≥ 25 V, 50 V preferred.
  - 100n: X7R 50 V 0805 (Samsung CL21B104KBCNNNC).
  - C12 (OL hold): 1 µF X7R 50 V 0805 (Murata GRM21BR71H105KA12).
  - C13 (audio path): 2.2 µF X7R 50 V 1206 (Murata GRM31CR71H225KA88), or film.
  - C0G parts: 50 V.
- **MPNs:**
  - OPA1612: TI OPA1612AIDR.
  - U4: TI LM393BIDR, sharing one comparator part with the master.
  - Q1 / Q2: value and MPN onsemi MMBFJ112 (J112 is the TO-92 part).
  - LEDs: Kingbright WP710A10ID red (D2/D3), WP710A10GD green (D4/D5), WP710A10YD yellow (D6–D8).
  - The pots need their full shaft codes. RV8's MPN names a detent part that CLAUDE.md records as not found (open
    item: the pan pot).
- **Export:** the BOM counts the DNP VCA-option parts (J3, J4, R44) as fitted. Add `${DNP}` to the CLAUDE.md BOM
  command's fields and group-by, or `--exclude-dnp`.

## 10. Resistor power

- **R1 / R2 (10R rail filters):** 55 mW typical, 85 mW at the OPA1612's 25 °C maximum, 126 mW at its −40…85 °C
  maximum (0.125 W 0805). Fix: anti-surge 0.5 W 0805 (Panasonic ERJ-P06J100V), no layout change.
- **R11 / R71 (75R output build-outs):** with a clipping signal into a shorted lead, about 0.25 W. Fix: ERJ-P06J750V
  (or 101V).

## 11. Spec notes (no circuit change)

- **J112 soft mute headroom (spec 9):** while ON, the gates sit at −VL, about 1 V below the most negative PRE
  excursion. A J112 at the worst-case VGS(off) of −5 V starts conducting on negative peaks above about +20.7 dBu
  (+22.9 dBu with typical parts); VDG reaches 32.5 V of 35 V. Optionally select J112s with |VGS(off)| ≤ 3 V.
- **Phantom:** the insert send (C51) and direct out (C52) put about 42 V across their 47 µF 25 V NP caps if fed to a
  phantom-powered input. Note "no phantom on these outputs" (as decided for the master), or fit 50 V parts (10 mm can,
  footprint change).

## Found along the way (beyond the strip)

- **Single-pole sim:** `tools/sim_netlist.py` uses a single-pole op-amp with no input capacitance, so it can't see any
  of this; every stage passes there. A stability pass with TI's model (the scripts below, model path as an argument)
  should run on the master and group boards too. Their re-inverters, level buffers and mono were fixed in the master
  review; the receivers (finding 3), post-amps, C/Room and solo followers have not been checked this way.
- **Output trace capacitance:** the stability harness should also put 22–47 pF on long op-amp output nets. "+2 pF on
  every input" only exercises the direction that helps followers.

## Review sims (`sim/review/strip/`)

TI's OPA161x macromodel (SBOM396G, from ti.com) stays out of the repo: set `OPA161X_LIB=/path/to/OPA161x.LIB`. The
`.spiceinit` there sets `ngbehavior=psa`, which the model needs.

| Script | What |
|---|---|
| `stripdeck.py` | `tools/sim_netlist.py`'s deck builder with TI's model per unit, a Tian probe at each output and a source at each + input |
| `run_all.py <fixset> [states]` | Loop gain (phase margin, peaking) of all 20 units over the states in `configs.py`; e.g. `python3 run_all.py none c01_nominal`, `python3 run_all.py recF` |
| `fixes.py` | Candidate caps; `recF` = the recommended set (T1–T4) |
| `checks.py`, `audio.py`, `cmrr.py` | `sim_netlist.py`'s 30 checks with both op-amp models; audio-band cost per fix; receiver CMRR |

Reproduced from this folder, nominal state: as designed U6A −4.0°, U6B −3.4°, U7A −4.0°, U12A 2.6°, U13B 2.7°, U2B/U3A
38.3°, U1A 45.0°, U3B 50.8°; with `recF` every unit ≥ 72.5°.
