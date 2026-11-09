# Delta channel clone (without the mic stage) — comparison, v0.2 (signed off)

Goal agreed on 2026-10-22: the channel strip becomes a Soundcraft Delta input channel without the
mic stage. This document lists every stage of the Delta Theatre input next to the current strip,
with a proposal for each. **Ruslan signed off all seven decisions in §3 as proposed on 2026-10-22.**

**Sources** (`ref/Sndcft_DeltaDLX_Schems.pdf`): ED3344A (input, HPF, 4-band EQ, insert; PDF p.15),
ED3344B (ON/mute logic, peak detector; p.16), ED3344C (mute, fader, pan, aux, routing, direct out;
p.17), ED3151 (LH board: EQ gain pots, HPF switch, aux pre/post switches, routing; p.14).
Component references below (R27, VR2 …) are the Delta's.

## 1. Delta Theatre input, signal order

```
Line in (TRS) ─ line stage: diff amp IC2A + gain pot VR1 in its feedback, Ø switch ─ −5 dBu
 ─ HPF (switched, 2-pole) ─ −2 dBu
 ─ 4-band EQ (HF shelf, HI-MID swept, LO-MID swept, LF shelf) ─ EQ IN switch (bypass) ─ PRE-EQ tap
 ─ insert (post-EQ by default; links allow pre-EQ) ─ peak detector ─ PFL (22K)
 ─ ON/mute (2 × J112) ─ fader ─ post-amp +10 dB ─ −2 dBu
 ─ post-fader buffer ─ pan (dual 10K B, centre detent) ─ pan buffers
 ─ PAN switch (off: unpanned post-fader to the buses) ─ routing MIX / 1-2 / 3-4 (10K 0.5 W)
 aux 1-6: 10K A pots, 22K to the bus; PRE switch per pair; links pick pre-fader or pre-EQ
 aux 6 doubles as direct-out level (DIR switch) ─ direct out (TRS, 75R)
```

## 2. Stage by stage

| Stage | Delta (Theatre input) | Our strip now | Proposal |
|---|---|---|---|
| Input | XLR mic stage (2SB737 pair, IC1A) **or** line: TRS through 15K + 4K7 per leg into a diff amp (IC2A), 3K3 feedback via the gain pot divider and buffer IC2B | Ground-compensated diff receiver, fixed unity, 10K 0.1 % | **Keep our receiver** (unity, 4 × 10K 0.1 %, inputs swapped so it inverts) **plus a separate gain stage** (below). The Delta line topology, recalculated for −15…+15 dB, was simulated and rejected: noise gain 6.6 at 0 dB, 4.7 dB noisier (§6). |
| Gain (trim) | VR1 5K reverse-log, in the line stage's feedback. Line range −15.5…+15.2 dB (S2-D shorts R24 in line mode; traced 2026-10-28, `docs/reviews/delta_crosscheck.md` D23: ED2915A −13.4…+17.3, ED2776 −13.4…+16.5) | none | **Add:** inverting stage, 10K B centre-detent pot with 2K2 at each end, wiper to the virtual earth. −15.0 … +14.8 dB, 0 dB at the detent, dB-symmetric law (≈ 2.5 dB per 10 % of rotation). Two inversions: in phase. |
| Phase | SW2 Ø: swaps the diff amp's inputs | none | **Add** (one PVA2, no extra electronics). |
| Meter-bridge out | CN7 via 100R, after the gain stage | none | Leave out (no meter bridge planned). |
| HPF | Sallen-Key 2-pole: C12/C13 47n, R27 33K, R26 39K, IC3A gain 1 + 4K3/10K. Simulated: **−3 dB at 91 Hz, 12 dB/oct, no peaking, +3.1 dB passband**. HPF switch on the LH board bypasses the capacitors; the stage stays in the path. | none | **Add, unity gain** to keep 0 dBu (decision 3): same 47n caps, 27K (to output) / 56K (to ground), Butterworth. Simulated −3 dB at 87 Hz, −10 dB at 50 Hz, no peaking. Switch shorts the caps, as the Delta. |
| EQ | 4 bands, TL072 (IC3B, IC4A, IC4B, IC5A): HF shelf (C51/C15 4n7, R87 5K6, R30 6K8, R29/R31 33K); HI-MID 600 Hz–10 kHz (VR2 100K C-law dual, Wien band-pass C17 3n3 / C18 1n5, R32/R34 6K8, R33/R35 22K); LO-MID 150 Hz–2.4 kHz (VR3, C19 15n / C20 6n8, R36/R38 6K8, R37/R39 22K); LF bell (C50 2µ2, C21 100n, R41 5K1, R42 1K5, R40/R43 22K). Gain pots (LH board ED3151): 4 × 10K B centre-detent chained EQ_IN–IC3B–IC4A–IC4B–R7 3K3–VR4 (C1 150n across)–R8 3K3–IC5A. | none | **Add as drawn**, OPA1612. Simulated (§6): ±11.5 dB HF at 12 kHz; HI-MID ±14.6 dB 670 Hz–10.5 kHz Q 1.44; LO-MID ±14.7 dB 148 Hz–2.3 kHz Q 1.44; LF ±14.3 dB at 54 Hz Q 0.88; flat within 0.16 dB, in phase. Since strip v5.5 (EQM1, `docs/proposals/eqmid_proposal.md`) the mids sweep 598 Hz–9.93 kHz and 165 Hz–2.54 kHz, the Delta's measured ranges. |
| EQ in/out | SW3: EQ output or bypass; green EQ LED | — | **Add** (switch + LED). |
| Insert | TRS, **ring = send, tip = return** (console-wide, JSK2), 75R send, tip normalled to ring; **post-EQ** by default (links LK1–LK6 for pre-EQ) | TRS, tip = send, 75R, ring normalled; right after the receiver (pre-everything) | **Delta position: post-EQ**, solder jumper for pre-EQ. **Tip = send kept** (D1, decided 2026-10-28: electrically identical, and the sense of the commercial insert lead; strip spec §7). |
| Overload / peak | Discrete peak detector (TR12), red PEAK LED, taken at SW3-B's output: post-EQ-switch, **pre-insert** (corrected 2026-10-28, D9; "post-insert" before), ≈ +14 dBu positive peaks only, ≈ 1.5 s decay (D10) | LM393 comparator, +18.4 dBu both polarities, 150 ms hold; since CS1 five taps (RECV, GOUT, EQOUT, PRESRC, FPOST) | Keep ours (simulated, threshold known); the Delta's point is our EQOUT tap. |
| PFL | SW10, 22K, pre-fade post-insert; red PFL LED; PFL DET | same | No change. |
| Channel on / mute | **ON** switch (SW11), green ON LED; latched = channel on. Mute: series J112 (TR4) into IC6-A's virtual earth + shunt J112 (TR3) with its source on C30 47 µF, gates on MUTE / MUTE-bar from a TR6 / TR7 inverter pair | MUTE switch, amber LED; latched = muted. Two shunt J112s in a 4K7 ladder into a follower, one RC from the key | **Delta: ON switch, green LED** (decision 5). **Not** the same J112 circuit (corrected 2026-10-28, D3; this row said "same"): ours keeps its shunt pair (strip spec §9), depth measured at the jig (CS8). |
| Fader + post-amp | 10K log fader, IC12B +10 dB (4K7/2K2), VCA not fitted | same; VCA plug-in socket (SSI2162) | No change. |
| Pan | VR10 10K B centre detent; pan buffers with gain; **PAN switch**: off sends unpanned post-fader to the buses | dual pot, unity followers; always panned | Keep our buffers; **add PAN switch** (decision 6). **Erratum (2026-10-27):** the Delta's buffers are 1.22× (R122 / R124) with 3K3 law resistors (R120 / R121) back to the wipers, a −4.4 dB law, and its PAN-off feed is +1.4 dB (IC6-B). This row missed both, so our −6 dB law was never decided; see `docs/proposals/cs2_proposal.md` §1. Corrected in strip v5.4 (CS2 Option A: the law; PAN off stays POST). |
| Routing | MIX, 1-2, 3-4 (5-6, 7-8 not fitted on Delta); off grounds the resistor; **amber LED per button** | MIX, 1-2, 3-4, off grounds the resistor; no LEDs | Keep 4K7 summing (recorded decision); **add the three LEDs**. |
| Aux 1-6 | 10K A pots, 22K; **PRE switch per pair on the panel**; links pick pre = pre-fader or pre-EQ | 10K A pots, 22K; pre/post per pair by solder jumper only | **Add the 3 PRE switches**; solder jumper per pair for pre-fader / pre-EQ (as the Delta links). |
| Direct out | TRS, IC12A, 75R; **DIR switch** turns aux 6 into the direct-out level | none (architecture excludes direct outs) | **Add** (decision 7). |
| Bus | 10K MIX/group, 22K aux, GND CANCEL 10R, spade | 4K7 MIX/sub, 22K aux, same GCANCEL and spade | Keep ours (4K7 is a recorded decision; 10K only for real-Delta compatibility). |
| Op-amps | TL072 throughout | OPA1612 | OPA1612 in the signal path (decision 4 for the EQ). |
| Internal level | −2 dBu nominal after the HPF | 0 dBu | Decision 3. |
| Power | 10R + 220 µF per rail, logic 10R + 47 µF | same | No change. |

## 3. Decisions (all accepted as proposed, 2026-10-22)

1. **Reverse the recorded "no EQ, no trim" decision.** CLAUDE.md and `console_architecture.md` §6
   (Excluded: trim, HPF, EQ, direct outs) change accordingly.
2. **Gain range.** Proposal: −15 dB to +15 dB, centre detent at 0 dB, so a +12 dBu synth fits
   with the fader at "0" and a −10 dBV source reaches 0 dBu.
3. **Internal level.** Keep 0 dBu (our post-amp, summing and meters are set for it, 22 dB
   headroom on ±17 V), or adopt the Delta's −2 dBu (24 dB headroom, EQ values unchanged).
   Proposal: keep 0 dBu; the EQ is unity-gain, so its values don't depend on the level.
4. **EQ op-amps.** OPA1612 (lowest noise, same as the rest) or NE5532 (the classic choice for this
   EQ topology, cheaper; fine at 10K–22K impedances). Proposal: OPA1612 for consistency.
5. **ON or MUTE.** Delta ON (green, latched = on) or keep MUTE (amber, latched = muted).
6. **PAN switch.** Add (Delta) or keep always-panned.
7. **Direct out.** Add (Delta: aux 6 doubles as its level via DIR), or leave out.

**Later change (2026-10-22, after sign-off):** the HI-MID / LO-MID frequency pots (100K C-law duals) are
not stocked, so those two bands now use a KHN state-variable band-pass with the Wien's exact response,
tuned by a stocked A10K dual. Boost/cut, Q and ranges are as the Delta's. See strip spec §6.2.

## 4. Panel and board impact

| | Now | Delta clone |
|---|---|---|
| Pots | 7 + fader | 14 + fader (gain, HF, HMF gain + freq, LMF gain + freq, LF, aux 1-6, pan) |
| Switches | 5 | 13 (Ø, HPF, EQ, 3 × PRE, DIR, PAN, MIX, 1-2, 3-4, PFL, ON) |
| LEDs | 3 | 7 (PEAK, EQ, ON, PFL, MIX, 1-2, 3-4) |
| Jacks | 2 | 3 (line in, insert, direct out) |
| Op-amps | 3 × OPA1612 | about 7 (gain stage + buffer, HPF, 4 EQ stages, direct out) |

Rough column height with two pot columns at 8 HP (EQ and aux pots in pairs), 12 mm switch rows,
100 mm fader: about 480–520 mm. That is at the limit of an 8 HP × 12U panel (514 mm) and
comfortable in 15U (642 mm). A placement study decides it, after the decisions above.

## 5. Notes from transcribing the Delta EQ

- Flexi CN8 (ED3344A) = CN3 (ED3151): 1 LF wiper, 2 IC5A out, 3 IC4B out, 4 LMF wiper, 5 IC4A out,
  6 HMF wiper, 7 IC3B out, 8 HF wiper, 9 ground, 10 EQ in, 11/12 +48 V (not used), 13/14 HPF switch.
- R32 and R36 (6K8) run from the frequency rheostats to ground. On ED3344A their top ends meet the
  stage-input line without a junction dot: they cross, they don't connect. Read as connected, the
  mid bands give only +4 / −1 dB.
- All four gain pots boost clockwise, matching the CW arrows on ED3151.
- The LF band is a bell (Q 0.88 at 54 Hz), not a shelf, despite the "60 Hz" legend; it still gives
  +7.6 dB at 20 Hz at full boost.

## 6. Simulation results (October 2026)

Decks: `sim/gain_stage.cir` (input + gain, and the rejected Delta topology), `sim/delta_eq.cir`
(Delta HPF + EQ as drawn), `sim/strip_v4.cir` (whole v4 channel). Op-amps single-pole 40 MHz;
OPA1612 noise modelled as resistors (1.1 nV/√Hz, 1.7 pA/√Hz). Noise 20 Hz–20 kHz unweighted,
50 Ω source.

| Check | Result |
|---|---|
| Gain law | −15.0 / −11.0 / −7.8 / −5.0 / −2.5 / **−0.1** / +2.3 / +4.9 / +7.6 / +10.8 / +14.8 dB at 0 … 100 % rotation; in phase |
| Input + gain noise at the output, 0 dB / +15 dB | −105.2 / −91.4 dBu (Delta topology: −100.4 / −85.9; old unity receiver −106.5) |
| Levels, 0 dBu in, gain at detent, EQ flat | RECV, GAIN, HPF, EQ out, PRE all 0.0 dBu; POST +9.9 dBu with the fader at the top; mix bus out +3.8 dBu (pan centre) |
| Response, EQ flat, HPF out | −3 dB at 1.0 Hz; −0.07 dB at 20 Hz; −0.24 dB at 20 kHz |
| HPF in (unity Butterworth) | −3 dB at 87 Hz, −10.1 dB at 50 Hz, no peaking |
| EQ bands at full boost / cut | HF ±11.5 dB at 12 kHz (±13.5 at 20 kHz); HI-MID ±14.6 dB, 670 Hz–10.5 kHz, Q 1.44 at both ends; LO-MID ±14.7 dB, 148 Hz–2.3 kHz, Q 1.44; LF ±14.3 dB at 54 Hz, Q 0.88 |
| PRE noise, gain at detent | **EQ in, flat: −97.2 dBu**; EQ bypassed: −105.2 dBu |
| POST noise, fader at the "0" mark | EQ in: −96.9 dBu; EQ bypassed: −102.7 dBu |

**EQ noise.** The EQ in circuit adds about 8 dB. It is resistor thermal noise (33K/22K stages,
6K8–106K networks, 10K pots), not the op-amp: OPA1656 instead of OPA1612 changes it by 0.2 dB at
any frequency setting, so OPA1612 stays. Scaling all EQ impedances down (curves unchanged)
gives −99.5 dBu at ½ (5K gain pots, 50K frequency pots) and −100.8 dBu at ⅓ (3K3 / 33K pots).
**Recommendation: keep the Delta values.** The gain is 2–4 dB for harder-to-get pots, and EQ IN
bypass gives the full 8 dB back on channels that don't use the EQ. With all 24 channels routed and
EQ in, channel noise at the mix bus is about −83 dBu, below the output noise of most analogue synths.

**Headroom.** Internal nodes clip at about +21 dBu (OPA1612 on ±17 V). At the gain detent, with
an EQ band at +15 dB, a +6 dBu input clips at the boosted frequency; use the trim.

## 7. Next

1. Strip spec v4.0 and `tools/gen.py` (new stages, panel parts, footprints); ERC, netlist check.
2. Panel-height study and new placement (placement only).
