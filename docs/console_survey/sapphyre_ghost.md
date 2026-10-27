## sapphyre_ghost: Soundcraft Sapphyre and Soundcraft Ghost

### 1. Header
- **Sapphyre** (an in-line recording console, with Dual Line and Dual Stereo modules and an LC/VCA option).
  - `soundcraft_sapphyre_sch.pdf`: 30 scanned pages at 300 dpi, legible. Pages read:
    - p1 (manual 7.2, I/O LH: EQ / gate / lo-cut)
    - p3-5 (7.4-7.6, I/O RH: mic and line input, mute, fader, pan, routing, power)
    - p6 and p10 (7.7 / 7.11, Group: summing amp, insert, power distribution)
    - p11 (7.12, Master LH: aux summers)
    - p14-15 (7.15 / 7.16, Master RH: mix summers, balanced outputs, control room / solo)
    - p20-21 (7.21 / 7.22, **Dual Line Module**: the closest analogue to our strip)
    - p23 (7.24, LED meter)
  - User guide 2/2: PDF p22 (manual p58, specifications) and p36 (manual p72, specification notes).
  - **Missing:** the PSU (external CPS450 / CPS550, not drawn), the VCA pages (not read), any noise/CMRR data for the line input.
- **Ghost** (an in-line console with MIDI mute automation).
  - `soundcraft_ghost_sch.pdf`: 30 pages, vector drawings rendered at 300 dpi. Pages read:
    - p2 (ED3620, input module)
    - p5 and p9 (ED3625 stereo inputs / group; ED3627 main aux / group)
    - p8 (ED3626, group + meter)
    - p11-12 (ED3628, master mix, control room, solo logic, bus loom)
    - p25 (ED3622, PSU distribution)
  - **Missing:** no specification page or user guide; the PSU itself (external, PSM300 mentioned) is not drawn.

### 2. Published specs (Sapphyre only: user guide 2/2 p58 and notes p72)
- **Levels:** nominal output +4 dBu. Line input sensitivity −20 to +10 dBu. Insert −2 dBu (the internal level is −2 dBu, see T12).
- **Max output:** balanced line outputs +27 dBu into 600 Ω; insert sends +21 dBu into 2 kΩ; phones +20 dBu into 600 Ω (150 mW into 8 Ω).
- **Impedances:** line input >15 kΩ, insert send 75 Ω, insert return >15 kΩ.
- **Frequency response:** 20 Hz-20 kHz +0 / −0.5 dB.
- **Crosstalk at 10 kHz** (16 channels routed, re +20 dBu): channel mute >110 dB, pan isolation >85 dB, routing isolation >85 dB.
- **Noise** (22 Hz-22 kHz, average reading, unweighted): group and mix outputs −90 dBu with 16 channels routed. Note H defines "mix bus noise" as 36 channels routed with faders down.
- **THD:** line in to tape send at +20 dBu, <0.005 % at 1 kHz, <0.025 % at 10 kHz.
- **Not published:** rails (±17 V from the schematics), CMRR, residual noise.
- **Comparison with ours:** our sim gives −100.4 dBu bus noise with 24 strips, at 0 dBu nominal. Sapphyre's −90 dBu at +4 nominal is about −94 dB relative to nominal. Ours is better on paper, but sim vs measured.

### 3. Topics

**T1 Line input**
- Sapphyre Dual Line, **read** (p20): a one-op-amp variable-gain differential stage on a TL072.
  - 15K per leg, 3K3 to ground on the + side.
  - Feedback is a 3K3 driven from a TL072 follower on the wiper of a 5K reverse-log pot. The pot sits from the op-amp output to 120R to ground.
  - The I/O line stage is the same circuit with 15K inputs (p3).
  - **Inferred:** gain roughly −13...+19 dB.
- Ghost, **read** (p2): there is no separate line amp.
  - The line legs pass 47 µF + 10K into an 8K2 shunt pad, then the discrete mic pre (2SD786 + TL072, gain pot 10K special).
  - Then a 10K/10K NE5532 diff amp with 47 pF on both legs.
  - Stereo inputs (p5): TL072 diff amps, 30K in / 15K feedback (−6 dB), 100 pF.
- **vs ours:** different. Neither console buffers the legs: Sapphyre's legs see 15K, Ghost's go through a pad into the mic pre. Ours, with 1M follower inputs and OPA1612 at 0.1 %, should give clearly better CMRR against unbalanced synth sources. Sapphyre's combined gain/receiver saves a stage, but every gain setting changes the leg impedances (**inferred**).

**T2 Line gain**
- Sapphyre: the gain sits inside the receiver (above).
- Ghost: the mic-pre gain pot.
- **vs ours:** we use a separate stage. Ours is quieter at unity (the decision recorded 2026-10-22).

**T3 Polarity**
- Both consoles swap the legs ahead of the amp (**read**: Ghost SW2, Sapphyre I/O S2). The Dual Line module has no Ø switch.
- **vs ours:** same.

**T4 HPF**
- Ghost (**read**): a 2-pole Sallen-Key on an NE5532, 47n / 47n, 24K feedback and 100K to ground, switched. **Inferred:** about 69 Hz, Q about 1.0. A 3K8 is switched by the same key; its role is unclear.
- Sapphyre I/O: a fixed lo-cut on a TL071 (2K7 / 47n / 22n). The Dual Line module has none.
- **vs ours:** ours (sweepable KHN) is more capable.

**T5 EQ (non-mid parts)**
- Sapphyre Dual Line (p20): a 2-band HF/MF EQ only (VR3 10K B shelf, VR2 2×100K C mids on NE5532s). The I/O EQ (p1) has 4 bands with a master EQ IN (S12).
- Ghost: a 4-band EQ with 220 µF couplers between stages.
- **vs ours:** comparable; nothing new.

**T6 Insert**
- Sapphyre (**read**: p20 Dual Line, p3 I/O):
  - On Dual Line: pre-EQ, send from the input amp via 47 µF + 75R; on I/O: unbalanced 75R send.
  - The return is **balanced** on both modules (I/O: TL071 diff amp, 15K/15K): on Dual Line, a TL071 with 15K/15K and 5K1/5K1 plus 100 pF; normalled on the jack.
  - The group, mix and master inserts are balanced both ways: hot 75R, cold 10R to ground, with a diff-amp return.
- Ghost (p2): send via 75R, unbalanced return with 220 µF. SWAP and SRCE keys move the insert and the EQ between paths.
- **vs ours:** ours is post-EQ with an unbalanced follower return. Sapphyre's balanced return is a small, cheap upgrade.

**T7 Mute**
- Sapphyre (**read**: p20 / p21 Dual Line, p4 I/O): a **series-shunt JFET into a virtual earth**.
  - Signal → 4K7 → series J111 (J112 on I/O) → TL072 inverting amp with 4K7 feedback.
  - A shunt J111 (J112 on I/O) on the source side, with 47 µF in series so the shunt causes no DC step.
  - The gates are driven through 220K / 100 nF with diodes and 10M + 10M, giving asymmetric on/off ramps (**inferred**: ~20 ms).
  - Logic: CUT switch, 4 mute-group buses (diode-OR), solo-in-place mute with a solo-safe jumper, opto-isolated automation status.
  - Spec: channel mute >110 dB at 10 kHz.
- Ghost (**read**, p2): two **P-channel J174 shunts** at the nodes of a 3K3-3K3-3K3 series chain, **post-fader**.
  - The gate is pulled to +17VL via 100K when not cut, ramped by 330K / 47 nF (τ ≈ 15 ms).
  - A CMOS 4069 latch, settable by the CPU (MIDI mutes), via a 2SC2240.
  - SOLO CUT (destructive SIP) comes in through a diode.
- **vs ours:** Ghost's mute is the same concept as ours (two shunts, about 86 dB class). Sapphyre's series-into-virtual-earth plus AC-coupled shunt claims >110 dB.
- **Note:** both consoles switch *series* J111/J112s successfully because the channel sits at a virtual earth, so Vgs is defined. Our PFL switcher's series J112s failed without that condition.

**T8 Fader**
- Sapphyre Dual Line (**read**): driven from 75R.
  - Return via 2.2 µF and 47K into an NE5532 at +10.1 dB (2K2 / 1K), with a 2M2 DC feedback path.
  - The I/O channel fader is "10K LOG", with an NE5532 post-amp (**inferred** +9.9 dB, 4K7 / 2K2).
  - The master mix fader is 0 dB at the top, followed by an NE5532 unity follower.
- Ghost (**read**): the wiper goes through 3×3K3 (the mute chain) and 2.2 µF into an NE5532 at +10.4 dB (5K1 / 2K2). A 24K / 10R network ties into the gain leg; its purpose is unclear.
- **vs ours:** same (+10 dB post-amp). Ours loads the wiper with 100K, theirs with 47K / 220K.

**T9 Pan**
- Ghost (**read**): a dual 10K pot with **A and C tapers** (10KAC), 3K3 law resistors, NE5532 followers. **Inferred:** about −3 dB centre.
- Sapphyre I/O: 4×10K B with 3K3 law resistors, NE5532 non-inverting buffers at +1.7 dB (2K2 / 10K).
- Sapphyre Dual Line: **passive and unbuffered**: 3K9 law resistors, pot wiper straight into 4K7 bus resistors ("530R max load" noted on the sheet).
- **vs ours:** ours is linear, −6 dB centre, buffered. Theirs give a −3 dB-ish law, which is better for stereo mixing.

**T10 Aux**
- Sapphyre: aux pots 20K B, wipers into **10K** bus resistors, unbuffered. Aux 1 is stereo, through the pan section (3K9 / 10K). PRE/POST switch.
- Ghost: 20K pots into **12K** (mono) and 22K (stereo aux 7/8), unbuffered.
- **vs ours:** same principle; we use 22K.

**T11 Routing**
- Both (**read**): mechanical switches carry the audio. The resistor's bus end goes to ground when off.
  - Sapphyre I/O: mix 4K7, groups 10K ("1/8 W resistors").
  - Ghost: 5K1 everywhere.
- **vs ours:** the same grounding principle. We switch with a DG413; they use switch contacts.

**T12 Summing**
- Sapphyre (**read**: p6, p11, p14): **every summer has a discrete front end**.
  - A 2SB737 PNP pair (common base, ~1-1.5 mA, rails RC-filtered with 220R / 820R + 47-220 µF).
  - The bus enters an emitter through **220 µF (group) or 1000 µF / 6.3 V (mix, aux)**.
  - An NE5532 (TL072 on aux) takes the collector difference. A second op-amp inverts the output and feeds it back to the summing emitter: 3K9 on the mix (4K7 bus resistors), 8K2 on the groups (10K bus resistors). So the internal level is −2 dBu.
  - On the groups the second emitter takes a "BALANCING TRACK" (**read**), i.e. a differential summing input. I could not find what drives that track in these pages.
  - An 8K2 / 3K9 from each bus to the insert-send cold leg (10R to ground) is also unresolved.
- Ghost (**read**): conventional NE5532 virtual earth.
  - Mix: 5K1 / 5K1 with 33 pF; group: 5K1 / 47 pF.
  - Aux 1-6 and 7/8: TL072, 12K feedback with **220 µF in series at the virtual-earth input**.
- **vs ours:** we use an OPA1612 with 4K7 / 4K7. Sapphyre's transistor front end was the low-noise answer for the NE5532 era. OPA1612's 1.1 nV/√Hz makes it unnecessary.

**T13 Ground cancel**
- Sapphyre (**read**):
  - Every module ties its ground through **10R to bus pin 27 "GND CANCEL"** (Dual Line R162, I/O R163, group R279).
  - On the aux summers, the input transistor's **base sits on the GND CANCEL line**.
  - On the mix summers, both bases are on local ground (**read**, p14). Where GND CANCEL is referenced for the mix is not visible.
- Ghost (**read**):
  - Each input module has 10R (R147) to pin 40 "GC".
  - Aux summers: + input via 75R to GC.
  - Group and main-mix summers: + input on local ground.
  - **GC is tied to master ground via 1K** (R125, p12; another 1K, R134, on p9).
- **vs ours:** same principle as Delta and ours. Ghost applies it only to the aux buses and ties GC with 1K (ours is a 100K keeper). Neither has our differential re-inverter.

**T14 Bus AC coupling**
- Both: 47-220 µF electrolytics on the source outputs (Sapphyre 220 µF after the fader amp; Ghost 220 µF before the pan).
- Plus series caps at the summing-amp inputs (Sapphyre 220-1000 µF, Ghost aux 220 µF). That keeps the summer's DC noise gain at 1.
- **vs ours:** ours couples at every source only. That is fine with OPA1612 offsets; nothing to change.

**T15 PFL / solo**
- Sapphyre: PFL and AFL buses at 22K. Solo-in-place with solo-safe. AFL and SIP detectors on TL072s. Monitor switching by **J112 series-shunt pairs into virtual earths** (p15).
- Ghost: a stereo PFL/AFL bus at 22K.
  - DC detect lines: PFL DET and SOLO DET, each 100K per module. At the master they meet 100K to −17VL + 100 nF and a transistor detector, then 47K / 220 nF ramps to the gates.
  - Control-room switching by J111 series + shunt pairs (10K series) into a TL072 virtual earth; DIM is a J111 + 1K shunt.
  - Meters follow the control-room source.
- **vs ours:** the same DC-detect scheme. Theirs adds AFL and SIP, which suit recording rather than our use.

**T16 Direct out**
- Ghost: post-fader, from the +10 dB amp via 75R, unbalanced.
- Sapphyre: not on the Dual Line module.
- **vs ours:** ours (from aux 6, impedance-balanced) is more flexible.

**T17 Master outputs**
- Sapphyre (**read**, p14): a **cross-coupled NE5532 pair** (4K7 / 10K, 22 pF), 75R + 47 µF per leg, a 1K BALANCE trimmer. +27 dBu into 600 Ω. No relay mute seen.
- Ghost: a ground-compensated single NE5532: hot via 75R, cold 75R to ground and sensed back via 10K. **Inferred:** about +3.4 dB gain.
- **vs ours:** ours (DRV135 + relay with power-on delay) is the modern equivalent and does more.

**T18 Meters**
- Ghost (**read**, p8 / p11):
  - TL072 half-wave precision rectifier (33K / 47K), 560R into 10 µF.
  - 12 LEDs in **one series string**, each shorted by an LM2901 output.
  - 2SA970 current source (**inferred** ~5 mA).
  - On separate meter rails ±17VSB / SBGND.
- Sapphyre (p23): the same series-string LM2901 ladder, 20 LEDs from −22 to +16.
  - A single **+24 V** meter supply with an 8 V virtual ground.
  - PEAK/VU jumper (75R / 10 µF / 22K for peak, 5K6 for VU); input ground "not joined to module".
- Channel peak LEDs (**read**), both consoles **multipoint**:
  - Sapphyre Dual Line: a diode window comparator, **full-wave**, from 4 points (input amp, insert return, EQ out, post-fader amp). 82K / 27K threshold ladder, 2.2 µF / 220K hold (~0.5 s).
  - Ghost: 4 points (pre-amp, HMF, LMF, post-fader), positive only, threshold ~+6 V peak (**inferred**), 2.2 µF / 330K hold. Signal LED at −20.
  - Sapphyre's channel LEDs (solo / peak / active / cut) are one series stack with shorting transistors, so the module draws constant LED current.
- **vs ours:** the master meter architecture is the same. Our strip OL detector reads **one point (PRESRC), positive peaks only**.

**T19 Power**
- Sapphyre (**read**):
  - Per module: 10R + 220 µF per rail (`rail fusing` 10R on the master).
  - Logic rails ±VL via 10R + 47 µF, logic ground DG.
  - A **spade connector per module** for heavy ground; chassis and pot brackets to audio ground via 10R.
  - Earth stud with 0R links joining meter 0V, bus GND and logic GND.
  - Separate rails from several PSUs (±17 V "B" and "C", +24 V meters, +48 V).
- Ghost (**read**):
  - Per module: 10R + 47 µF + 100 nF.
  - Logic rails ±17VL via 10R; +5 V for the CMOS from 4K7 + 5V1 zener.
  - Separate meter rails.
  - Logic ground joined to audio ground once at the master (R208, 0R); DGND to the chassis/EMC stud via 100R.
- **vs ours:** essentially identical to ours, down to 10R + 220 µF, logic rails with a single-point tie, the spade, and 4K7 + 5V1 for the logic supply. This validates our choices.

**T20 Op-amps**
- Both consoles: TL072 / TL071 everywhere non-critical (Ghost even in the mic pre and on the stereo inputs), NE5532 in the gain, fader and summing stages, and 2SB737 / 2SD786 discrete front ends.
- Stability caps 33-47 pF everywhere; 75R build-outs on every output.
- **vs ours:** ours is better in noise and THD; the stability practice is the same.

**T21 Levels**
- Sapphyre: −2 dBu internal (mix, group and insert marked "−2 dBu"), +4 dBu outputs, +27 dBu maximum.
- **vs ours:** ours is 0 dBu internal; headroom is similar on ±17 V.

**T22 Construction**
- Sapphyre: an in-line frame with a 40-way bus connector and per-module spades. Pots on sub-boards via IDC headers.
- Ghost: 40-way looms, an external PSU on Mini-Fit, and a CPU board.
- **vs ours:** comparable (our 34-way ribbon plus a spade).

**Not covered** (or only touched): T4 detail on the Sapphyre I/O; T16 on the Sapphyre; mute relays and power-on mute (none seen); the PSU circuits; any CMRR figure.

### 4. Worth considering for goa-console
1. **Multipoint OL detection, including the post-fader +10 dB amp (U2A out) and the gain-stage out (U1B).**
   - Why: both consoles do it. Our CLAUDE.md already notes that hot synths clip the post-amp with the fader at the top, which our PRESRC-only detector cannot see. An EQ cut after a clipped gain stage also hides the clip from PRESRC.
   - Cost: 2-3 diodes + resistors OR-ed into U4A's input network; a re-sim of `ol.py`. Fits well.
2. **Full-wave OL detection** (Sapphyre's diode window).
   - Why: our detector is half-wave positive only, so asymmetric synth waveforms (saws, pulses) can clip on the negative side unseen.
   - Cost: a few diodes or a second comparator input. Fits.
3. **Balanced insert return.**
   - Why: Sapphyre uses a 15K/15K diff amp; outboard gear is often balanced, and this would cancel ground loops from the outboard unit.
   - Cost: replaces the U7B follower with a diff amp (4 resistors, 0.1 %); the stability (C84) has to be re-checked. Moderate value for a synth console with outboard effects.
4. **Constant-current LED stacks** (Sapphyre's channel LEDs in one series string with shorting transistors).
   - Why: no LED switching transients on the supply.
   - Low value for us: we already have separate logic rails and GNDD. Mention only.
5. **Pan law −3 dB** (Ghost's A/C-taper dual, Sapphyre's law resistors).
   - Why: our linear −6 dB centre is a choice, not a fault. If we want −3 dB / −4.5 dB, law-bending resistors to ground on the buffered pan outputs cost almost nothing. It is a taste decision.

**Not recommended:**
- Sapphyre's discrete summing front ends: OPA1612 makes them pointless.
- Series-cap virtual-earth DC blocking: our offsets are small.
- AFL, SIP and mute groups: recording and automation features.
- Mechanical-contact routing: our DG413 is cleaner.

**Where ours looks weaker:** only the OL detector's coverage (items 1-2). The mute depth (~86 dB vs Sapphyre's >110 dB spec) is adequate for line level with the fader also down, but a series JFET into U3B's virtual earth would close the gap if the jig shows feed-through.
