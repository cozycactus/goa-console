# CS11: five jig tests from the console survey (proposal, 2026-10-27)

**Signed off by Ruslan on 2026-10-27 (as proposed: tests 13-17 in `test_jig_spec.md` v0.9) and applied the same day.**
The change is `archive/patches/cs11_proposal.patch`. It touches `test_jig_spec.md` only, as tests 13-17 in §4 and v0.9 (strip v5.3), so
no board or schematic changes.

**Targets:** `sim/review/cs11/jig_targets.py`; its output is in `jig_targets.out`. Section 1 needs TI's DRV134 model
via `TI_MODELS`.

## 1. Why

`docs/studies/console_survey.md` §7 CS11 lists what the AMEK big's test protocol and Mackie's per-bus ground tests measure that our
jig spec doesn't. Each test now has a target from our own netlists and models, so a jig result reads as pass or fail
and not as a bare number.

## 2. The tests

| # | Test | Target | From |
|---|---|---|---|
| 13 | DRV134 output balance (stub, MIX L): common mode against differential, 1 kΩ 0.1 % per leg | −90 dB below 1 kHz with equal 10 µF couplers; 20 % apart: −25 dB at 100 Hz, −35 dB at 1 kHz; −62 dB at 20 kHz. Pass within 3 dB of the measured couplers' prediction | TI model |
| 14 | Line-input CMR per strip: (a) matched 100 Ω pair, (b) 1 kΩ on the tip | (a) ≥ 58.7 dB at 50 Hz / 1 kHz. (b) ≥ 54 dB at 50 Hz; about 56 / 38 / 32 dB at 1 / 10 / 20 kHz | netlists + `docs/studies/ground_study.md` §5.2 |
| 15 | Fader breakthrough and pan isolation per strip, with each pot's end resistance r measured | Fader ≤ −80 dB below "0" (r ≤ 0.3 Ω); pan ≥ 60 dB (r ≤ 10 Ω); both within 3 dB of the r prediction | pot law |
| 16 | MIX L noise, faders down, N = 4…24 | N 4 −106.7 … N 24 −100.1 dBu, ±2 dB | noise model (summer + stub re-inverter) |
| 17 | GCANCEL current (each strip's R5 voltage) | A record: idle ≤ ~0.1 mV; test 2: 80 mV on the injected strip, 20 mV on the others | the line's arithmetic |

## 3. What the numbers say

- **Output balance (13) is the coupler match.**
  - **Mechanism:** the DRV135's cross-coupled loop floats its outputs, like a transformer. A mismatch between the two
    10 µF couplers inside the Sense loops comes out as common mode, whatever the load (1 kΩ or 10 kΩ give the same
    figures).
  - **Matched:** −90 dB.
  - **With the Panasonic ECE-A1EN100U's ±20 %:** as poor as −25 dB at 100 Hz and −35 dB at 1 kHz.
  - **Effect:** a balanced receiver rejects it, so the console's signal doesn't suffer. It shows on any test of output
    balance against ground, and as common mode on the cable.

  **Possible follow-up (not in this proposal):** larger couplers or matched pairs.

  | Couplers | 100 Hz | 1 kHz |
  |---|---|---|
  | 10 µF, 20 % apart (as fitted) | −25 dB | −35 dB |
  | 10 µF, 5 % apart (pairs sorted at assembly) | −38 dB | −49 dB |
  | 47 µF, 20 % apart | −30 dB | −49 dB |
  | 100 µF, 20 % apart | −35 dB | −55 dB |

  The jig can tell whether it matters on the bench.
- **CMR (14) at high frequency is the capacitors, not the resistors.** Against a synth's 1 kΩ on one leg, C8 / C9 (100 pF
  to CHASSIS at the jack) and C94 / C95 (100 pF at the followers) leave 38 dB at 10 kHz and 32 dB at 20 kHz. With the
  ideal-resistor netlist and a matched source, CMR is over 130 dB, so on the bench the bridge's 0.1 % sets it.
- **Fader breakthrough (15) is the fader's end resistance:** −80 dB below the "0" mark needs ≤ 0.3 Ω. This test and
  `docs/build/sample_order.md` check 9 decide CS9.
- **Faders-down noise (16)** is the bus alone: −100.1 dBu at 24, our like-for-like figure against the published ones in
  `docs/studies/console_survey.md` §2. Those include each maker's master stages.

## 4. Checks

- Doc-only; the patch applies cleanly on the committed tree.
- The CMR figures use the exported netlists through `sim_netlist.py`'s own deck builder.
- At 50 Hz the 1 kΩ figure (60.1 dB with ideal resistors) agrees with `docs/studies/ground_study.md`'s 60.0 dB median.

## Sign-off

- [x] **CS11** as proposed: tests 13-17 into `test_jig_spec.md` (v0.9). Ruslan, 2026-10-27; applied the same day.
- [ ] Also work up the DRV135 coupler follow-up (larger or matched couplers).
- [ ] Neither.
