# Sweepable HPF — proposal

Proposal for sign-off, 2026-10-24. **Signed off by Ruslan the same day (H1–H4 as proposed, MF-RX185/72 for H4) and
applied:** strip v4.3, master spec v0.9. Strip 260 parts / 774 pins and master 1642 pins, 0 mismatches, check_fp 0,
ERC 0; `sim_netlist.py` 35/35, `sim_console.py` 32/32; strip and master re-placed with 0 DRC violations and 0 parity
issues. The master's F1–F4 are fixed in place so the wider body goes outward and the rest of the board keeps its
layout (only D8 / D9 moved, 7.5 mm down their column). (When written, nothing in the design had changed.) The
generator and layout edits are in `archive/patches/hpf_proposal.patch`. They were trial-applied in a throwaway worktree, then
regenerated, verified, simulated and re-placed (results below). The design study is `sim/review/hpf/khn_hpf.py`.

It replaces the signed decision "HPF unity-gain Butterworth 87 Hz" (Delta clone, 2026-10-22) with a swept one.

## Why

- **Synth bass vs low-end mud.** Hardware synths put a lot of energy below 80 Hz: sub-oscillators, pads, kick-like
  patches, DC-ish envelopes on old gear. A fixed 87 Hz cut is right for a pad and wrong for the bass line.
- **Kick and bass at the same time.** On a goa mix the kick and the bass own the bottom, and every other channel
  should be cut well above them: 150–400 Hz on pads, leads and FX.
- **One knob, at the source.** A sweep from ~20 to ~400 Hz covers both cases: barely there on the bass, high on a pad.

## Circuit

A state-variable (KHN) high-pass. It is the same topology and the same stocked dual pot as the strip's mid bands
(spec 6.2).

```
HIN ─ R100 4K99 ─┬─ U5A (+)      H_SP: C85 22p to AGND
H_BP ─ R101 2K49 ┘
H_LP ─ R102 2K49 ─┬─ U5A (−)     U5A out = HP;  R103 4K99 ∥ C86 10p from HP to (−)
                  │
HP ── RV16A (pin 3; pin 1 ─ R104 330R ─ AGND; R105 13K pin 3 → wiper) ─ wiper ─ R106 5K6 ─ U15A (−), C87 100n to H_BP
H_BP ─ RV16B (pin 6; pin 4 ─ R107 330R ─ AGND; R108 13K pin 6 → wiper) ─ wiper ─ R109 5K6 ─ U15B (−), C88 100n to H_LP
U15A/U15B (+) = AGND.   SW11 pole A: common HOUT; latched = HP (HPF in), released = HIN (HPF out)
C91 33 µF NP in parallel with C38 (GOUT → HIN)
```

- **Response.** RF = 2·RLP and RIN = 2·RBP give unity gain, non-inverting (tip = hot is kept), Q = 1/√2: Butterworth,
  12 dB/oct.
- **Tuning.** Each gang is a divider into its integrator's virtual earth, as on the mid bands. R0 is 330R here, not
  430R, for a 19:1 range. CW = higher frequency.
- **Bypass.** SW11 selects the source of HOUT, so the HPF out is a wire, with no added noise. U5A no longer acts as the
  HIN buffer, so C91 is added (below).
- **Parts.** It needs a third op-amp unit and a second package:
  - U5A becomes the summer;
  - U15 (new OPA1612) holds the integrators;
  - U5B is still the HF stage.
- **Stability caps.** C85 (22p) and C86 (10p) are part of the design. Without them the summer has 6.6° of phase margin
  and peaks +12.6 dB (TI OPA161x), the same Cdiff-lag case as the mid-band summers (strip v4.1).
- **Removed:** C39, C40, R48, R49 (the Sallen-Key).

### Values

| Ref | Value | Footprint |
|---|---|---|
| U15 | OPA1612 (TI OPA1612AIDR) | SOIC-8 |
| RV16 | Alpha RD902F-40-15R1-A10K, dual A10K: the HI/LO-MID frequency part | RD902F dual |
| R100, R103 | 4K99 1 % | 0805 |
| R101, R102 | 2K49 1 % | 0805 |
| R104, R107 | 330R 1 % | 0805 |
| R105, R108 | 13K 1 % | 0805 |
| R106, R109 | 5K6 1 % | 0805 |
| C85 / C86 | 22p / 10p C0G | 1206 |
| C87, C88 | 100n C0G (as C50) | 1206 |
| C89, C90 | U15 decoupling (as every OPA1612) | as the others |
| C91 | 33 µF NP 25 V, Nichicon UES1E330MPM (MUSE ES, as C38) | `CP_Radial_D8.0mm_P3.50mm` |

The strip goes from 245 to 260 parts.

## Performance

### Law

−3 dB frequency at the 11 dial positions (`khn_hpf.py law`; the strip netlist gives 21.2 / 85.9 / 406 Hz at
CCW / mid / CW):

| Position | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Hz | 21 | 37 | 51 | 64 | 75 | 85 | 132 | 171 | 216 | 280 | 403 |

- **Shape.** The step between 5 and 6 is the A taper's knee, as on the mid bands. The law is within about 0.4 oct of a
  log sweep.
- **Mid rotation is today's corner.** 85 Hz at the centre is the current fixed HPF.
- **Suggested scale numerals:** 20, 50, 85, 170, 400.

### Response and tracking

- **Response:** Butterworth at every rotation:
  - no peaking (0.00 dB);
  - unity passband: −0.11 dB at 1 kHz with the corner at 403 Hz, 0.00 dB at 20 kHz;
  - phase lead at 1 kHz: +7° at mid and +34° at CW. That is inherent in any 12 dB/oct high-pass (today's: about +7°).
- **Gang mismatch ±20 %:** peaking ≤ 0.09 dB, and the −3 dB point doesn't move. The corner follows the product of the
  two gangs, so a tracking error mostly moves Q.

### Headroom

No internal node rises above the input at any frequency or rotation:
- BP and LP peak at −6 dB;
- the summer's inputs peak at −9.6 dB.

So the HPF costs no headroom.

### Noise

PRE noise (dBu, 20 Hz–20 kHz, 50 Ω source, gain at the detent; `sim/review/strip_noise/noise.py` on the trial
netlist):

| | EQ in | EQ bypassed |
|---|---|---|
| HPF out (as now) | −92.9 | −102.6 |
| HPF in, CCW (21 Hz) | −92.6 | −100.7 |
| HPF in, mid (85 Hz) | −92.7 | −101.0 |
| HPF in, CW (403 Hz) | −92.7 | −101.2 |
| Today's Sallen-Key in (87 Hz) | −92.8 | −102.3 |

- **HPF out:** no change.
- **HPF in, EQ in:** +0.2 dB.
- **HPF in, EQ bypassed:** +1.4 to +1.9 dB.
- **Where it comes from:** the summer's 1.66 kΩ input network at a noise gain of 3, plus the integrators' current noise
  in 5–18 kΩ.
- **OPA1656 (strip noise proposal N1) wouldn't change this:** −105.3 against −105.1 dBu at the HPF output.

### Stability

TI OPA161x model in the full strip deck (`sim/review/strip`; HPF in at CCW / mid / CW with EQ in, and mid with EQ
bypassed):

| Unit | Phase margin | Closed-loop peaking |
|---|---|---|
| U5A summer | 84.3–84.8° | ≤ 0.08 dB |
| U15A, U15B integrators | 87.4–87.8° | ≤ 0.31 dB |
| U5B HF stage | 82.6° | 0.30 dB |
| U1B gain stage (drives HIN) | 86.0° | 0.22 dB |

These are the worst values over the four states. Every unit is above the strip's existing floor of 69.9° (U7B).

### LF corner and C91

With the HPF out, SW11 connects HIN straight to the EQ input and the other HOUT loads, about 2.5 kΩ in all. Before,
U5A buffered HIN.

| PRE, HPF out | −3 dB | At 20 Hz | Phase at 20 Hz |
|---|---|---|---|
| Today | 0.38 Hz | 0.0 dB | +2–3° |
| C38 alone (33 µF) | 1.9–2.1 Hz | −0.05 / −0.09 dB | +8° |
| C38 + C91 (66 µF) | 1.0–1.1 Hz | ±0.04 dB | +5° |

- **Why two 33 µF.** A 100 µF MUSE ES is a 10 mm can. It doesn't fit the bottom side in the top 100 mm, where every
  gap between pot rows is 9.2 mm, so two 8 mm cans instead.
- **Why it matters.** With C38 alone, about 10 % of the 20 Hz signal sits across one electrolytic. That's the
  distortion mechanism the film/NP change avoided elsewhere; C91 halves it.

### Switching

SW11 is a break-before-make selector, so HOUT is open for the few ms of travel; the EQ's input network holds the node.
The DC step between the two sources is ≤ 0.9 mV at CCW and 0.17 mV at CW (TI model, typical Vos and Ib), so a tick
of about −59 dBu at most. HIN sits on the summer's input network and follows HP's DC. In the worst case (max Vos / Ib)
it is a few mV. Today's switch shorts the Sallen-Key caps, which steps by the same order (not simulated).

## Panel and board

### Panel, right column

| y (mm) | Today | Proposed |
|---|---|---|
| 50 | Ø key | Ø key |
| 61 | OL LED | HPF IN key (SW11), 11 mm under Ø: the PRE key pitch |
| 76 | HPF IN key | HPF FREQ knob (RV16, dual, pins to the centre line) |

- **OL LED:** moves to (20.6, 50), between the GAIN knob (3.8 mm from the knob's edge) and the Ø key (3.2 mm).
- **The FREQ name** sits between the HPF IN key and the knob, 4.6 mm. The mid rows have 9 mm there, so the panel
  print needs a look.
- **Left column:** unchanged (GAIN 54, HF 76).

### Board (trial placement)

- **CN3 moves:**
  - The dual pot's mounting tabs at y 71.2 / 80.8 close the gap CN3 used. The boxed 2×5 header needs ~10 mm; every
    gap between two pot rows is 9.2 mm.
  - CN3 goes to y ≈ 131.5, between the LO-MID and LF rows. The right column has the EQ key there, not a pot, so the
    gap is 11.7 mm.
  - The jack-board ribbon gets about 46 mm longer: about 136 mm, still one 90° fold. Spec 16.4 changes.
- **HPF parts:** U5 sits at y ≈ 88 and U15 at y ≈ 109, between the HF/HI-MID and HI-MID/LO-MID rows.
  - Every HPF input network is within 13 mm of its pin (U5.2 13.0, U15.6 11.0, U15.2 10.7, U5.3 9.9).
  - The pot to U5 / U15 is 10–35 mm.
- **Zones:** HPF to y 44–135, EQ and KHN down to 200 and 215, insert jumpers to 200, C38 / C91 bottom 44–100.

Placement report, current board → trial (median / max / count over the limit):

| Check | Current | Trial |
|---|---|---|
| Decouplers, pad to supply pin | 3.1 / 10.0 / 11 | 3.1 / 10.0 / 10 |
| High-Z inputs, farthest pad (27 → 30 inputs) | 10.4 / 19.7 / 25 | 11.0 / 23.1 / 29 |

- **Worst new row:** U5B's HF network, 23.1 mm. U5B moved with U5A.
- **Not tuned yet:** this layout is a fit check. It would get the usual pass after sign-off.

### Trial results

| Check | Result |
|---|---|
| Strip schematic | 260 parts / 774 pins, 0 mismatches, check_fp 0, ERC 0 |
| `sim_netlist.py` | 35/35. The HPF check becomes six: −3 dB at mid / CCW / CW within 80–95 / 19–24 / 380–430 Hz, and no peaking at each |
| `sim_console.py` | 32/32 |
| Strip board | 0 DRC violations, 0 parity issues, 499 unconnected (expected) |
| Jack board | unchanged |

## Costs

- **Supply:** +1 OPA1612 per strip, about +7 mA per rail (3.6 mA per unit typical).
  - Strip: ~85 / 72 → ~92 / 79 mA.
  - Console: +0.17 A, 2.65 → 2.82 A on +V; the PSU has 4 A.
- **Wing PTCs.** The typical wing load on +V goes 1.16 → 1.25 A. On the MF-RX160/72 kept in MG14 that is 96 % of hold
  at 40 °C and 109 % at 50 °C (was 89 / 101 %). On the MF-RX185/72 alternative: 83 / 94 %. The HPF makes a warm-room
  nuisance trip more likely. This is the strongest argument yet for the outline-only MF-RX185/72 change.
- **Signed decisions:** it changes "HPF unity-gain Butterworth 87 Hz". It touches the Delta-clone panel layout
  (16.3: a knob where a key was) and the CN3 position (16.4).
- **Distortion (OPA1656 question, strip noise proposal):** the summer's + input sees 1.66 kΩ, against the Sallen-Key's
  27K / 56K. U5A stops being the "textbook bad case" for a CMOS input.
- **Parts and cost:** 15 parts per strip (360 for 24), one OPA1612 and one RD902F dual among them.

## Not chosen

- **No switch (CCW ≈ 21 Hz as "off"):** saves SW11 and the C91 question. But an HPF is never fully out, and the
  +1.4–1.9 dB noise with EQ bypassed is then always there.
- **Bypass by shorting the integrator caps** (as today's switch shorts the Sallen-Key caps): U5A would stay a buffer, so
  no C91. But the summer's noise is in the path even with the HPF out (+1.5–2 dB with EQ bypassed).
- **Sallen-Key with a dual pot as two rheostats:**
  - A unity-gain Butterworth Sallen-Key high-pass needs R2 = 2·R1. Two identical gangs can't hold that ratio over the
    sweep; equal resistors give Q ≤ 0.5.
  - Gang tracking and the pot's end resistance go straight into Q and the corner.
  - The KHN uses the stocked part the same way the mid bands do.

## After sign-off

- Apply `archive/patches/hpf_proposal.patch`, regenerate, verify, export BOM / PDF; `sim_netlist.py`, `sim_console.py`; re-place the
  strip and run parity DRC.
- Spec:
  - §5 (circuit), §1 / §2 summary, §11 package table (U15), §16.3 / §16.4 (panel, CN3, ribbon length), §17;
  - the noise figures with the HPF in (§4, strip noise proposal);
  - test jig per-strip checklist: HPF sweep at CCW / mid / CW.
- Panel: `panel_print.md` and `tools/console_3d.py` (FREQ scale 20 / 50 / 85 / 170 / 400 at the HPF knob, HPF IN key
  legend, OL LED position).
- CLAUDE.md decisions.

## What to sign

- [x] **H1** Sweepable HPF as above: KHN on U5A + U15, RV16 A10K dual, 21–403 Hz, SW11 selects HIN or HP. Replaces
  the signed 87 Hz Sallen-Key.
- [x] **H2** Panel and board:
  - SW11 to y 61 and RV16 at the right column y 76;
  - OL LED D2 to (20.6, 50);
  - CN3 to y ≈ 131.5 (ribbon about 136 mm).
- [x] **H3** C91 33 µF MUSE ES in parallel with C38 (or keep C38 alone and accept the 1.9 Hz corner).
- [x] **H4** Wing PTCs: revisit MG14, MF-RX185/72 (recommended with H1), or keep MF-RX160/72. **Your call:**
  MF-RX185/72.
