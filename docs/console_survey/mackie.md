## Mackie CR1604-VLZ, MS1402-VLZ and 8•Bus: survey report (label: mackie)

### 1. Header
- **CR1604-VLZ** (`~/Downloads/402198774-Mackie-1604-VLZ-16-channel-mixer-pdf.pdf`, service manual 820-172-00, 05/99,
  18 pp). The text layer covers only the titles and the connector tables. The schematics are vector drawings, which I
  read at 600 dpi.
  - PDF p3: block diagram.
  - p4: channel. p10 repeats it.
  - p7: pod sheet 3 (output jacks).
  - p12: aux masters.
  - p13: subs and main mix.
  - p14: C-R / solo.
  - p15: meters.
  - p17: connector pinouts.
  - p18: PSU.
- **MS1402-VLZ** (`~/Downloads/291841104-ServiceManual-Mackie-1402-Vlz.pdf`, 820-169-00, 12 pp):
  - p2: block diagram.
  - p4: mono channels.
  - p6: aux send / return.
  - p7: master.
  - The PSU / meter page (p7 of the manual) was not read.
- **8•Bus** (990-0xx boards, © 1993/1999; the extracted `8 Buss Mixer/` folder):
  - 09U p1: channel board 990-009.
  - 09U p4: connector pinouts.
  - 08S p1: mic/line preamp.
  - 10U-1 p1: subs 1-4.
  - 10U-3 p1: L/R mix and Mix-B.
  - 10U-1 p3: monitoring / solo.
  - 11J: LED meter.
  - 15S: PSU.
  - `8bus-SM.pdf`: block diagram and quick parts.
  - The channel OL / −20 detector was read earlier and is not repeated here.
- **Missing from all three:** specifications (no noise, CMRR, crosstalk or headroom page), so section 2 is empty. On
  the 8•Bus, the sub output's jack wiring is on the jack-field board, which I did not read.

### 2. Published specs
None of these documents has a specification page. The only level marks:
- **Operating level:** "0dBu = 0VU" on the 1402 meter block, so the internal level is 0 dBu, as ours.
- **Clip LED:** the 1604 meter's clip LED is marked "+20".
- **Rails:** VLZ ±16 V (LM317 / LM337 set to 1.25 × (1 + 1485/130) = **15.5 V**). 8•Bus **±18 V**.

### 3. Topics

**T1 Line input** (read; 1604 p4, 1402 p4, 8•Bus 08S)
- **VLZ:** there is no separate line receiver. The TRS line jack feeds the mic preamp:
  - each leg: 47 µF → **10K0 1 %** into the preamp's base node, which carries **1K30 1 %** to ground;
  - pad: about −19 dB, −20 dB with the 6K81 bias legs (**inferred**);
  - preamp: discrete 2SA1084 / IMBTA06 pair plus an NJM4560, gain set by a 5KZY trim between the emitters;
  - the line and mic inputs are not switched, so both feed the preamp at once.
- **CMRR (inferred):** set only by 1 % resistor matching. I estimate about 40 dB, which is not published.
- **8•Bus:** a MIC/LINE switch, SW101. The line feeds the same discrete preamp through **7K32** per leg with **3K92**
  to ground (−9.2 dB).
- **vs ours:** different. Our line input is a dedicated buffered receiver (54 dB against a 1K source) with a separate
  gain stage. Mackie's route through a 60 dB mic preamp is a mic-console economy. Ours is better for line.

**T2 Line gain** (read)
- **VLZ / 8•Bus:** the preamp trim, about 60 dB of range minus the line pad (**inferred** from the values).
- **vs ours:** ours is ±15 dB around a detent, which suits synths better.

**T3 Ø** (read)
- **VLZ:** none.
- **8•Bus:** has a FLIP switch, but it swaps the tape return with the channel path; it is not a polarity switch.
- **vs ours:** we have Ø; they don't.

**T4 HPF** (read; 1604 p4)
- **Topology:** fixed **75 Hz, 18 dB/oct**. Three 0.22 µF caps feed an NJM4560 follower (U104A), with 20K / 5K1
  shunts, 62K at the + input and 1K3 feedback.
- **Switching:** a 47 µF / 20K bypass path; SW101 selects LO CUT.
- **8•Bus:** the same idea, with a HI-PASS IN / OUT switch.
- **vs ours:** ours is 12 dB/oct, sweepable 21-403 Hz. Theirs is steeper but fixed.

**T5 EQ** (read, values only)
- **1604:** HI / LO shelves at 12 kHz / 80 Hz, using 50KB pots around one NJM4560 (U105A, 1M + 10 pF). The swept mid
  uses a 500KC dual (100 Hz-8 kHz) in a stage of its own (U101A / B, 10K / 10K, 20 pF).
- **1402:** 80 Hz / 2.5 kHz / 12 kHz, fixed.
- **8•Bus:** 4-band EQ with a semi-parametric (Q-pot) hi-mid on module 990-016, plus EQ split to Mix-B.
- **vs ours:** ours has two swept mids with a fixed Q and the Delta shelves (see `eq_survey.md`).

**T6 Insert** (read)
- **1604 (pod, TRS):** the insert sits after the mic preamp, before low-cut and EQ.
  - Send: 47 µF, 10K to ground, then **120 Ω**.
  - Return: straight to the main board (C121 47 µF and the low-cut network, about 20K), normalled by the jack.
  - The return is not buffered.
- **1402:** the same, with 120 Ω. Wire links W43 / W45 / E102 place it post-HPF, and the jack sleeve has its own
  **G-INS** ground line.
- **8•Bus:** a "PATCH" jack with 120 Ω, pre-EQ.
- **vs ours:** different. Ours is post-EQ (pre-EQ by jumper), with a 75R send and a buffered return (1K + 100 pF into
  a follower).

**T7 Mute** (read)
- **1604:** SW103A is a mechanical series switch at the fader top. Muted, the fader input goes to ground, after the
  post-EQ / PFL tap. SW103B pulls the red OL LED's cathode to −16V-LED through 5K1, so mute shows as a "glow".
- **1402:** no mute in the path. MUTE/ALT (SW105) moves the main L / R assign to an ALT 3-4 bus, and its 510 Ω
  ground-sense resistor moves with it (G-MAIN → G-ALT). SW105D also re-sources aux 2.
- **8•Bus:** SW104B sits after the post-fader amp, before pan. Muted, the pan input goes to ground. The yellow mute
  LED runs from +5 V through 510 Ω. The direct out is post-mute.
- **vs ours:** different. Ours is a J112 soft mute with a 20 ms ramp that also mutes the pre sends. Theirs are hard
  contacts on AC-coupled nodes (47 µF everywhere), and the VLZ pre sends ignore mute.

**T8 Fader** (read)
- **All three:** a 10K "D"-taper fader (1604 R107 10KD, 8•Bus R126 10KD), then 47 µF into a non-inverting NJM4560:
  - feedback 1K1 / 510 gives **+10.0 dB**;
  - 220 pF across the 1K1;
  - a 100K load after the output cap;
  - the 8•Bus adds 15K to bias the + input.
- **vs ours:** the same scheme (fader then +10 dB post-amp, 100K). Mackie's fader is a custom D law. Our "0" mark is
  still approximate until the Bourns law is measured.

**T9 Pan** (read)
- **VLZ:** a 10KC / 10KA dual. Each section is a divider from the post-fader signal to ground. The wipers drive the
  bus resistors directly, unbuffered:
  - main 5K1;
  - subs 20K;
  - SIP 30K.
  - Pan law and source impedance therefore depend on what is assigned (**inferred**).
- **8•Bus:** a 50KA / 50KC dual, fed at the junction with the outer ends grounded, plus 36K law-shaping loads. The
  wipers go into **NJM4560 followers** (U103A / B), then 47 µF.
- **vs ours:** the 8•Bus matches ours (buffered pan). The VLZ saves the buffers.

**T10 Aux** (read)
- **Wiper-fed pot (all three):** source → **5K1 → wiper** of a 50KG pot. The pot's top goes to the aux bus (virtual
  earth) and its bottom to channel ground, so the upper part of the track is the summing resistor.
- **Gain:** with the 36K feedback, full CW gives +17 dB (**inferred**).
- **1604:**
  - aux 1-2 have a PRE switch;
  - by default (solder jumper Z103 "C" to pad F, "PRE EQ") the pre tap is post-low-cut, pre-EQ and pre-mute;
  - aux 3-4 are post-fader and SHIFT onto 5/6.
- **1402:** aux 1 is a dual 50KG feeding a B-PRE-1 and a B-POST-1 bus at once; a global master switch picks pre or
  post.
- **8•Bus:** aux 1-2 PRE / POST; aux 3-6 select channel or Mix-B as source.
- **vs ours:** ours uses 10K A pots, 22K into the bus and a per-pair PRE. Mackie's wiper feed gives send gain above
  unity with no extra stage. The cost is that the bus noise gain and the source's load (down to 5K1) change with the
  settings.

**T11 Routing** (read)
- **Resistors:** 5K1 per main bus (1604 main L / R, every 8•Bus bus).
- **Switching:** the switch moves the resistor's bus end between the bus and ground (the 8•Bus J3 AGND pins). This is
  the same practice as ours and the Delta's.
- **Contacts:** the switches carry audio directly; there is no logic switch.
- **vs ours:** the same principle. Ours puts a DG413 at the bus, and the key carries only logic and an LED.

**T12 Mix bus summing** (read)
- **1604 main:**
  - U1713A **NJM2068**: 5K1 in, **2K7 // 220 pF** feedback (−5.5 dB);
  - then U1733A, an inverting stage (2K7 / 5K1 // 47 pF, +5.5 dB), drives the insert send;
  - then a 50KD main fader and a +11 dB post-amp (1K3 / 510).
- **1402 main:** 5K1 / 5K1 // 47 pF (NJM2068), then a 10KD fader and the +10 dB post-amp.
- **1604 aux:** NJM4560, 36K // 20 pF.
- **8•Bus sub and L / R:** NJM2068, 2K7 // 220 pF. The sub post-amp is +16 dB (2K7 / 510).
  - The L mix summing node also carries **20 Ω + 220 pF to ground** (R607 / C341).
- **Noise gain (inferred):** with 16 channels on the 1604 main bus, the noise gain is 1 + 2K7/(5K1/16) = 9.5. That is
  25 dB above the signal gain, the same ratio as ours at 16 sources.
- **vs ours:** the same virtual-earth topology. They put a low-noise op-amp only on the summer; we use OPA1612
  throughout.

**T13 Bus ground** (read)
- **VLZ:** every bus has its own ground-sense line (G-MAIN, G-AUX-n, G-SUB-n, G-SOLO, G-ALT). Each channel ties its
  ground to every G line through **510 Ω**, permanently (1402: switched with the assign). The summer's + input sits on
  the G line.
  - **Aux:** the whole aux master section uses G-AUX-n as its ground (both stages, the AFL contacts). The output
    jack's cold leg is driven from it through 120 Ω on its own wire (pod p7: ring through 120 Ω to AUX-n-GND), so the
    ground difference leaves as common mode.
  - **Main:** G-MAIN is tied to the main section's local ground by one more 510 Ω (R1927), so the master counts as
    one more "channel" in the average. The following stages reference the local ground (**inferred** from the
    drawing).
- **8•Bus:** no 510 Ω network. The 20-way bus ribbon interleaves AGND with every bus line. The summer's + input goes
  to BUS-n-GND, which is grounded on the output board.
- **vs ours:** the VLZ is the same idea as our GCANCEL, implemented differently:
  - one line per bus, not one line shared;
  - 510 Ω per channel, against our 10 Ω;
  - no re-inverter: the section rides on the line, or the line is tied to the master through 510 Ω.
  - The 8•Bus relies on ribbon ground conductors only, like a ground-referenced bus without cancel.

**T14 Coupling** (read)
- **All three:** polarized **47 µF / 25 V** electrolytics at every stage boundary, with 10K-100K returns.
- **vs ours:** ours uses film and MUSE NP. Mackie's 47 µF polarized caps sit at near-zero DC, the usual budget
  practice.

**T15 Solo** (read)
- **1604:** each channel feeds SIP L / R (30K, post-pan) and PFL (30K, from post-EQ, pre-mute). Off, the resistor end
  goes to ground.
- **Detect:** SW107A pulls the shared **B-LOGIC** line to channel ground:
  - the line idles at 0.31 V (100K to +16 V, 2K to ground);
  - U1709B compares it with 0.158 V (200K / 2K) and drives 1N4148 + 2K7 into 2.2 µF // 20K;
  - this drives the RUDE LED and **J112** series switches (Q1705 / 06) that cut the C-R source bus, plus J112s that
    move the meters to solo.
  - Released, the channel's green LED is held off (U102B's + input grounded through SW107A). Soloed, that input
    floats up through 100K and the LED glows.
  - Z1701 links solo between two mixers through 20 Ω.
- **8•Bus:**
  - the same wired-OR SOLO-CTL line;
  - per-channel jumpers choose SIP or PFL (5K1);
  - the channel's red solo LED is switched onto a console-wide **FLASH-BUS** (one MPSA06 / 5.6 V-zener flasher on the
    output board);
  - 2SC3792 transistor switches.
- **vs ours:** the same concept. Ours uses a 100K-per-strip DC current sum, a DG413 switcher, a rude flasher and PFL
  only. Theirs offer SIP as well, which is destructive and which we deliberately skip.

**T16 Direct out** (read)
- **1604:** channels 1-8 only. Impedance-balanced TRS, **120 Ω tip / 120 Ω ring to GND**. Fed post-fader by default
  through jumper Z102 "A" (**inferred**).
- **8•Bus:** post-mute, 120 Ω, unbalanced (J103 on the preamp board).
- **vs ours:** the same style (ours 75R / 75R, level from aux 6).

**T17 Master outputs** (read)
- **1604 main TRS (pod):** tip = main L through 120 Ω; ring = an NJM4560 inverter (5K1 / 5K1) plus a follower,
  47 µF and 120 Ω. Aux and sub outputs are impedance-balanced (120 Ω / 120 Ω to the section's own ground wire).
- **1402 XLR:** a non-inverting post-amp and an inverter (U2018A 5K1 / 5K1), 120 Ω each. A PAD switch (5K1 series,
  120 shunt) gives a mic-level output.
- **8•Bus L / R:** U33A NJM2068 post-amp (+10.3 dB, 2K4 / 1K1) and U35A, a 5K1 / 5K1 inverter, each through 47 µF
  and 120 Ω (**read**; the pin naming is partly cut).
- **8•Bus sub cold leg:** U3A buffers a 20K / 20 Ω tap (about −60 dB) through 120 Ω. That makes a driven-ground cold
  leg (purpose **inferred**).
- **Mute relays:** none on any output.
- **vs ours:** ours is DRV135 with relay mute and power-on delay, which is better. Mackie has no output muting at all.

**T18 Meters and channel LEDs** (read)
- **1604 master (p15):**
  - detector: an NJM4560 half-wave precision rectifier into **47 µF // 7K5** (τ about 0.35 s; attack limited by the
    op-amp's current, **inferred**);
  - 12-LED series string (−30 … +10, "CLIP (+20)") fed by an **IMBT4403 PNP current source** (2 × 1N4148, 220 Ω,
    about 3 mA **inferred**);
  - each LED is shorted by an **LM339** output; the ladder is 10K / 3K9 / 2K / 1K3 / 620 / 510 …
- **1604 channel −20 LED:**
  - U102B is an inverting amplifier with gain **−27.8** (1M / 36K // 20 pF), not a comparator;
  - it reads the pre-EQ signal and drives the green LED through 1K1 to the LED ground;
  - it lights from about **−23 dBu** on negative half-cycles, with brightness proportional to level and no hold
    (**inferred** from Vf ≈ 2 V).
- **1604 channel OL LED:**
  - U102A comparator; post-EQ through a 10K / 5K1 divider against 4.03 V (27K / 10K // 100K from +16 V);
  - trips at **+20.7 dBu**, positive peaks only, about 1.7 dB under the clip of a 4560 on 15.5 V;
  - drives the red LED through 220 Ω + 1N4148; no hold.
- **1402:** no channel LEDs on the schematic.
- **8•Bus meters:** ROHM **BA6822F** log bar drivers with 2N4403 drivers, 12 LEDs (−40 … +10) and a peak-hold jumper.
- **vs ours:** the 1604's master meter is the same architecture as ours (LED string shorted by comparators, PNP
  current source). Our strip OL (5 taps, both polarities, 150 ms hold) is clearly stronger than the 1604's single
  post-EQ tap.

**T19 Power** (read)
- **1604:** an internal transformer and LM317T / LM337T giving ±15.5 V:
  - 1N5401 bridge, 6800 µF / 35 V reservoirs, 10 µF on ADJ, 1N4002 protection;
  - phantom from TIP29C pass transistors with a 47 V zener;
  - **LED rails** ±16V-LED from the regulated rails through 1N4002, **5.6 Ω 2 W** and 470 µF;
  - their **G-LED** ground runs as its own wire, joined to CHANNEL GND only at the PSU;
  - an E3 "sweet spot" chassis tie point.
- **8•Bus (external PSU):** discrete ±18 V regulators:
  - error amp: a 2N4403 differential pair with a 6.2 V zener reference;
  - TIP31C driver; 2 × MJE3055 / MJE2955 pass transistors with 0.51 Ω 5 W ballast;
  - MPSA06 current limit;
  - 22,000 µF reservoirs plus a separate 2,200 µF supply for the driver.
  - Other rails: +5 V (7805), +12 V, +48 V.
  - The cable keeps **AGND and DGND separate**, and the channel board's J1 carries DGND / +5 V for LEDs and logic.
- **vs ours:** the same principle as our ±VL / GNDD joined at one point; Mackie does it by wire to the PSU star. The
  8•Bus's ±18 V is close to our ±17 V. Ours has the crowbar; theirs has current limit only.

**T20 Op-amps** (read)
- **Op-amps:** NJM4560 everywhere; **NJM2068** only on the mix / sub summers.
- **Stability parts:** 20 pF / 220 pF across feedback resistors.
- **Build-outs:** 120 Ω on outputs.
- **vs ours:** ours uses OPA1612 / OPA1656, C0G stability caps and 75-100 Ω build-outs.

**T21 Levels** (inferred)
- **Internal level:** 0 dBu.
- **Clip:** on ±15.5 V, a 4560 clips at about +22 dBu, 1 dB below ours.
- **Bus attenuation:** the 1604 main bus runs 5.5 dB down (2K7 / 5K1) and is made up afterwards.

**T22 Construction** (read)
- **1604:** all 16 channels on one main board, plus a "pod" board with jacks and preamps, joined by 40-way ribbons.
- **1402:** a single main board.
- **8•Bus:** 8-channel boards (990-009), separate 4-channel preamp boards (990-008) and an output board, joined by
  ribbons. Each channel board's bus header pairs every bus with an AGND. The PSU is external.
- **vs ours:** ours is per-channel modules on a Delta loom.

**Not shown in these documents:** published specifications, noise and CMRR figures, the 8•Bus sub output's jack wiring,
the 1402 PSU / meter page (not read).

### 4. Worth considering for goa-console
1. **Separate LED supply with its own ground wire (VLZ: 5.6 Ω 2 W + 470 µF per LED rail, G-LED to the PSU star).**
   - **Why:** our ±VL / GNDD already do this.
   - **Verdict:** confirms our choice; nothing to add.
2. **RC from the summing node to ground (8•Bus L mix: 20 Ω + 220 pF).**
   - **Why:** it damps RF and long-bus effects on the virtual earth.
   - **Cost:** two parts per summer.
   - **Verdict:** our `sim/routing_switch.cir` shows no peaking up to 2.2 nF of bus capacitance. Only consider it if
     the jig (bus test, 1 nF jumpers) shows RF or ringing. The 220 pF + 20 Ω raises the HF noise gain, so check
     stability before adding it.
3. **Per-bus ground-sense resistor of moderate value (VLZ: 510 Ω per channel per bus).**
   - **Why:** this is the alternative to our 10 Ω GCANCEL. A 510 Ω tie doesn't carry inter-strip ground current along
     the sense line the way 10 Ω can.
   - **Cost:** for us, more ribbon conductors (one per bus), so it doesn't fit the Delta loom.
   - **Verdict:** not proposed. Our sim gives 20-24 dB of cancel, and a 34-way loom has no spare lines. Worth one jig
     measurement: GCANCEL conductor current with 4 strips.
4. **Wiper-fed aux pots (source → 5K1 → wiper, pot top to the bus).**
   - **Why:** +17 dB maximum send with no extra stage.
   - **Cost:** the bus noise gain and the source load vary with the settings.
   - **Verdict:** not worth it for a 0 dBu synth console with 22K sends. Ours is quieter and its law predictable.
5. **Global pre / post for an aux pair through a dual pot onto two buses (1402).**
   - **Why:** it frees a strip switch.
   - **Verdict:** we already have per-pair PRE keys and a full ribbon, so not proposed.

**Where ours looks weaker than every reasonable practice:** nothing found. Mackie's line input through the mic preamp,
the unbuffered insert return, the mechanical mutes, polarized couplers and the single-tap positive-only OL are all
budget choices that ours exceeds. The only Mackie feature we lack is solo-in-place, which is destructive in a mix and
which we decided against.
