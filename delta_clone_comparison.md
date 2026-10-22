# Delta channel clone (without the mic stage) — comparison for sign-off, v0.1

Goal agreed on 2026-10-22: the channel strip becomes a Soundcraft Delta input channel without the
mic stage. This document lists every stage of the Delta Theatre input next to the current strip,
with a proposal for each. Nothing in the spec or schematic changes until Ruslan signs it off.

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
| Input | XLR mic stage (2SB737 pair, IC1A) **or** line: TRS through 15K + 4K7 per leg into a diff amp (IC2A), 3K3 feedback via the gain pot divider and buffer IC2B | Ground-compensated diff receiver, fixed unity, 10K 0.1 % | **Delta line stage without the mic stage:** diff amp with gain pot in the loop, OPA1612, 0.1 % resistors. Input impedance ≈ 20K per leg. |
| Gain (trim) | VR1 5K reverse-log, in the line stage's feedback. Line range ≈ −15.5 dB to +6.7 dB (or to +15.6 dB with R24 shorted by SW1-B; mic/line switch wiring not fully traced) | none | **Add.** Range to set by us (decision 2); confirm in simulation. |
| Phase | SW2 Ø: swaps the diff amp's inputs | none | **Add** (one PVA2, no extra electronics). |
| Meter-bridge out | CN7 via 100R, after the gain stage | none | Leave out (no meter bridge planned). |
| HPF | Sallen-Key 2-pole: C12/C13 47n, R27 33K, R26 39K, IC3A gain 1 + 4K3/10K. Simulated: **−3 dB at 92 Hz, 12 dB/oct, no peaking, +3.1 dB passband**. HPF switch on the LH board bypasses the capacitors; the stage stays in the path. | none | **Add as drawn.** |
| EQ | 4 bands, TL072 (IC3B, IC4A, IC4B, IC5A): HF shelf 12 kHz (C51/C15 4n7, R87 5K6, R30 6K8); HI-MID 600 Hz–10 kHz (VR2 100K C-law dual, C17 3n3, C18 1n5, R32/R34 6K8, R33/R35 22K); LO-MID 150 Hz–2.4 kHz (VR3 100K C dual, C19 15n, C20 6n8, R36/R38 6K8, R37/R39 22K); LF shelf 60 Hz (C50 2µ2, C21 100n, R41 5K1, R42 1K5, R40/R43 22K). Gain pots on the LH board: 4 × 10K B centre-detent in a chain with R7/R8 3K3 and C1 150n. | none | **Add as drawn**, OPA1612 or NE5532 (decision 4). Boost/cut range and curves to confirm in ngspice before the schematic. |
| EQ in/out | SW3: EQ output or bypass; green EQ LED | — | **Add** (switch + LED). |
| Insert | TRS, 75R send, ring normalled; **post-EQ** by default (links LK1–LK6 for pre-EQ) | TRS, 75R, normalled; right after the receiver (pre-everything) | **Delta position: post-EQ**, solder jumper for pre-EQ. |
| Overload / peak | Discrete peak detector (TR12), red PEAK LED, taken post-insert | LM393 comparator, +18 dBu, red OL LED, post-insert | Keep ours (simulated, threshold known); same tap point. |
| PFL | SW10, 22K, pre-fade post-insert; red PFL LED; PFL DET | same | No change. |
| Channel on / mute | **ON** switch (SW11), green ON LED; latched = channel on | MUTE switch, amber LED; latched = muted | **Delta: ON switch, green LED** (decision 5). Same J112 soft-mute circuit. |
| Fader + post-amp | 10K log fader, IC12B +10 dB (4K7/2K2), VCA not fitted | same; VCA plug-in socket (SSI2162) | No change. |
| Pan | VR10 10K B centre detent; pan buffers with gain; **PAN switch**: off sends unpanned post-fader to the buses | dual pot, unity followers; always panned | Keep our buffers; **add PAN switch** (decision 6). |
| Routing | MIX, 1-2, 3-4 (5-6, 7-8 not fitted on Delta); off grounds the resistor; **amber LED per button** | MIX, 1-2, 3-4, off grounds the resistor; no LEDs | Keep 4K7 summing (recorded decision); **add the three LEDs**. |
| Aux 1-6 | 10K A pots, 22K; **PRE switch per pair on the panel**; links pick pre = pre-fader or pre-EQ | 10K A pots, 22K; pre/post per pair by solder jumper only | **Add the 3 PRE switches**; solder jumper per pair for pre-fader / pre-EQ (as the Delta links). |
| Direct out | TRS, IC12A, 75R; **DIR switch** turns aux 6 into the direct-out level | none (architecture excludes direct outs) | **Add** (decision 7). |
| Bus | 10K MIX/group, 22K aux, GND CANCEL 10R, spade | 4K7 MIX/sub, 22K aux, same GCANCEL and spade | Keep ours (4K7 is a recorded decision; 10K only for real-Delta compatibility). |
| Op-amps | TL072 throughout | OPA1612 | OPA1612 in the signal path (decision 4 for the EQ). |
| Internal level | −2 dBu nominal after the HPF | 0 dBu | Decision 3. |
| Power | 10R + 220 µF per rail, logic 10R + 47 µF | same | No change. |

## 3. Decisions to sign off

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

## 5. Next, after sign-off

1. ngspice: line gain stage with the chosen range; the EQ at full boost and cut per band
   (confirm ranges and curves against the Delta values); whole chain level and noise.
2. Strip spec v4.0 and `tools/gen.py`; ERC, netlist check.
3. Panel-height study and new placement (placement only).
