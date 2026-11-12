## DDA AMR 24: survey report (label: dda_amr24)

Read 2026-11-12 against strip v5.7, master v0.14 and `docs/decisions_summary.md`. Every claim is marked **read**
(from the drawing or the manual's text) or **inferred** (calculated or deduced). Nothing in our design was changed.

### 1. Header
- **Console:** DDA AMR 24, a split 24-bus recording console (inputs on the left, 24 group / monitor modules and four
  master modules on the right, a jack patchbay at the end). Designed 1988, manual issues 1988-92. Mic / line inputs;
  for us only the line path, the buses and the master section matter.
- **Documents** (iCloud `Service Manuals/DDA amr24/`, both scans with no text layer, 150 dpi picture + 300 dpi line
  masks; "UM pN" and "SCH pN" below are PDF pages):
  - `amr24-user-manual.pdf`, 83 pp, issue 8905 (some pages 8811 / 8912 / 9206, bargraph section 9002):
    - UM p7-9: specifications and options.
    - p12-16: earthing, PSU hook-up, audio connections.
    - p18-23: input module. p24-28: output (group / monitor) module. p29-37: the four master modules.
    - p43-47: internal links. p49-52: module removal, alignments.
    - p53-62: EDAC multiway pinouts. p63-70: motherboard pinouts.
    - p73-75: spare parts. p76-81: optional bargraph meter (text only, its schematic page is a title).
  - `amr24-schematics.pdf`, 18 pp (the manual's section 6, which is only a title page in the manual itself):
    - SCH p2: input module. p3: output module. p4: control room master. p5: studio master. p6: oscillator master.
      p7: talkback master. p8: EBO balanced-driver sub-board (PC1081) and the phase meter.
    - p9-10: block diagrams. p11: audio PSU CD1025. p12: logic PSU CD1028. p13-18: PCB layouts.
- **Read at 300 dpi:** SCH p2 (whole sheet), p3 (group summer, insert, group output, routing, solo, logic, power
  entry), p4 (whole top half: mix summer, mix insert, master fader post-amp, mix output, C/R, solo summers, solo
  logic), p7 (aux summers and masters), p8 (EBO), p11 (whole), p12 (output side).
- **Not read:** the output module's monitor path in detail, SCH p5 and p6 (the right and mono mix outputs, foldback,
  oscillator), the block diagrams, the PCB layouts, the phase meter, the EDAC tables.
- **Missing:** line-input CMRR, mute depth, per-stage noise, PSU current rating, any bus-wiring drawing beyond the
  pin tables.
- **Scan limits:** coupling capacitors are marked "68" with no unit or voltage (taken as 68 µF; the mic input's are
  "33/63", the supply's "22/25"). Values below 12 px high were zoomed 2-3× before being written down.

### 2. Published specs (UM p7-8)
- **Levels:** outputs nominal +4 dBv "ref 0.775 V" (so dBu), 0 VU = 1.228 V; every output electronically balanced,
  < 75 Ω, +26 dBu into a balanced load; insert sends ground-compensated, +21 dBu.
- **Line input:** > 10 kΩ; line to mix gain up to 30 dB; ± 0.25 dB 20 Hz-20 kHz at 0 dB gain.
- **Noise:** mix noise < −82 dBu, DIN audio, 36 channels routed at unity gain.
- **Crosstalk:** group to group < −88 dBu at 1 kHz, < −72 at 20 kHz; group to mix < −82 / < −70.
- **Distortion:** < 0.05 % line, +4 dBu in and out.
- **CMRR:** only the mic amp's, > 60 dB at 1 kHz after trimming (UM p50).
- **Rails:** ±18 V audio and ±22 V logic at the motherboard (UM p64); the EBO board is drawn on ±17 V (SCH p8).

### 3. Topics

**T1 Line input** (read; SCH p2, top left)
- **Receiver:** one TL074 section as a differential amplifier.
  - each leg: 100K to ground at the connector, "68" coupler, then **6K8 1 % + 6K8 1 %** with 100 pF from their
    junction to ground;
  - feedback 6K8 1 % ∥ 100 pF, and the same to ground on the + leg;
  - so 13.6 kΩ per leg and a gain of **−6 dB** (**inferred** from the values);
  - 75 Ω build-out, "68" coupler into the gain stage.
- **No trim on the line receiver.** The common-mode preset and its 0.1 %-matched 200 Ω test pair (UM p50) belong to
  the mic amplifier (2SB737 pair + TL074, optional transformer).
- **CMRR (inferred):** set by the 1 % resistors, about 32 dB at their worst case; against a 1 kΩ unbalanced source
  the 13.6 kΩ legs give about 26 dB whatever the matching.
- **Mic / line select:** two series J111s (FET1 / FET2) from the two amplifiers onto one node, gates driven through
  diodes and RCs (10K + 2.2 nF, 10K + 220 nF) by CMOS logic, so the channel flips electronically from the master or
  the local "input reverse" key.
- **vs ours:** different. Ours has OPA1656 followers with 1 MΩ legs ahead of a 0.1 % differential amplifier (54 dB
  against 1 kΩ, sim). The AMR 24 is one more console that does not buffer the legs; ours stays the only one in the
  library that keeps its CMRR against a synth's output impedance.

**T2 Line gain** (read; SCH p2, UM p20)
- A non-inverting TL074 section: 10K in series with its + input, 10K feedback, and a 10K pot with its wiper on
  ground between two 2K resistors, one from the + input and one from the − input.
- **Range (inferred):** ±10.3 dB with 0 dB at centre; the manual says −10…+10 dB, centre-detented.
- **vs ours:** the same idea (a separate gain stage with a centre detent), ours ±15 dB and inverting.

**T3 Ø** (read; SCH p2)
- A unity inverting TL074 stage (10K / 10K ∥ 100 pF) hangs on the mic / line node; the PHASE REVERSE key takes the
  signal either from that node directly or from the inverter's output. It reverses mic and line alike (UM p20).
- **vs ours:** different. Ours swaps the legs ahead of the receiver and costs no stage; theirs must invert after the
  point where mic and line join, so it adds a stage when pressed (as the SSL, Sony and PM-5000 do).

**T4 HPF** (read; SCH p2, UM p21)
- **Topology:** second-order Sallen-Key, 12 dB/oct, **45-500 Hz**, with a FILTER IN key and LED.
  - 47 nF and 22 nF in series, a 100K dual pot with a 10K end-stop on each gang;
  - the TL072 runs at a gain of 2 (10K / 10K) behind a 4K7 / 4K7 pad;
  - **inferred:** the unequal capacitors with a gain of 2 give Q ≈ 0.69, and 10K / 110K give 494 / 45 Hz.
- **vs ours:** the same job and range (ours 21-403 Hz, KHN, A10K dual as dividers). Theirs needs a 100K dual whose
  law the drawing does not give; ours tunes with a stocked 10K.

**T5 EQ** (read for values, topology partly inferred; SCH p2, UM p19, p21)
- Four bands, all swept, ±15 dB, EQ IN key:
  - HF 1-16 kHz, shelf or peak (Q 1.5);
  - HI-MID 550 Hz-8.8 kHz and LO-MID 125 Hz-2.5 kHz, peaking, Q switched 0.8 / 1.5;
  - LF 30-125 Hz, shelf or peak, the peak narrowing as the frequency falls.
- **Circuit:** each band has its own unity inverting stage (10K / 10K ∥ 100 pF) with a 10K boost / cut pot between
  its input and output; the wiper feeds a one-op-amp band-pass (100K dual sweep pot, 6K8 stops, 1-6.8 nF) whose
  output returns to the stage's + input (4K7 to ground). Four such stages in series.
- **vs ours:** different. Ours keeps the Delta's shelves around one stage and uses KHN band-passes for the mids
  (598 Hz-9.93 kHz, 165 Hz-2.54 kHz, fixed Q). The ranges of the two mids agree within a third of an octave; the
  AMR 24's swept shelves and Q keys are panel room we do not have. `docs/studies/eq_survey.md` covers the swept mids
  of the other consoles; the AMR 24 is not in it.

**T6 Insert** (read; SCH p2, UM p18, p23)
- **Position:** post-EQ, pre-fader, on patchbay jacks.
- **Send:** always live. A TL071 with 10K / 10K to each input, 75 Ω, "68"; the send's cold pin returns to ground
  through 75 Ω and is sensed back into the + input through 10K, so the output rides on the far end's ground
  ("ground compensating", +21 dBu).
- **Return:** balanced. An NE5534 differential receiver, 10K per leg ("68" couplers, 100K to ground), 10K ∥ 100 pF
  feedback. The INS key switches the receiver's two inputs between the return pins and the internal signal.
- **vs ours:** different. Ours is one normalled TRS (tip = send, D1), a 75 Ω unbalanced send and a buffered
  unbalanced return (1K + 100 pF). A balanced return needs separate jacks, declined in `console_survey.md` §5. The
  ground-compensated send is the Delta's direct-out practice; our send is plain.

**T7 Mute** (read; SCH p2, UM p23, p45)
- **Audio:** a series J111 (FET3) followed by a shunt J111 (FET4) to ground, ahead of the fader. The series FET
  works into the fader's 10K, not into a virtual earth.
- **Timing:** each gate has its own RC with a diode for the fast direction: FET3 through 1M ∥ (diode + 220K) into
  10 nF, FET4 through 1M ∥ (diode + 220 Ω) into 2.2 nF. **Inferred:** 2-10 ms, staggered so the two do not overlap.
- **Logic:** a momentary CUT key into a CMOS NAND latch (22 nF + 330K debounce, power-on reset from 10K + 2.2 µF);
  the same line is pulled by EXT MUTE, by the MUTE A / MUTE B buses through their select keys, and by SIP MUTE
  unless SAFE is pressed.
- **Pre-fade sends:** the two "pre" lines are tapped before and after the FET pair, and a link per board chooses
  which one the PRE positions use. As shipped the pre sends ignore CUT.
- **vs ours:** ours is two J112 shunts after 4K7 with a 20 ms ramp (≈ 86 dB), a latching key, and ON always mutes
  the pre sends and the direct out (Q1). The AMR 24 adds one more series + shunt design to CS8's list, though not
  the virtual-earth kind, and publishes no depth. Ours has the same choice per aux pair on JP2-JP4, but its unmuted
  position is the pre-EQ tap (HOUT); the AMR 24's stays post-EQ and post-insert.

**T8 Fader** (read; SCH p2)
- A mono ALPS fader on a connector (P&G optional), then 220 nF and 220K ∥ 220K into an NE5534 non-inverting stage,
  10K / 4K7 feedback: **+9.9 dB** (**inferred**), 75 Ω, "68".
- The motherboard carries Fader Send / Return / Ground pins for the optional VCA automation (UM p64).
- **vs ours:** the same scheme (10K fader, +10 dB post-amp).

**T9 Pan** (read; SCH p2)
- **Passive.** The post-amp feeds 3K3 into each gang of a 4K7 dual whose wipers are grounded, so each gang is a
  variable shunt. A PAN IN key bypasses it (the signal then goes straight to both drivers).
- **Law (inferred, unloaded):** −7.6 dB at centre, −4.6 dB hard over, so a −3.0 dB law with 4.6 dB of loss, made up
  by the +6 dB of the bus drivers. The drivers' 18K inputs load it a little.
- **vs ours:** different. Ours buffers each side (U8B / U3A, 1.22× with 3K3 back to the wipers) for the Delta's
  −4.4 dB law. Like ours, the AMR 24 has a switch that takes the pan out for routing to single groups.

**T10 Aux** (read; SCH p2, p7, UM p22)
- **Sends:** six, as two stereo (A, B: a level pot and a pan pot each) and four mono; PRE / POST per stereo send and
  per mono pair.
- **Network:** 10K pots, the wiper straight into **10K** to the bus, unbuffered. The stereo sends pan passively
  (3K3 into each end of a 10K pot with its wiper on ground, then 10K per side).
- **Summers (SCH p7):** NE5534 (22 pF compensation), bus through "68" into the − input, feedback 22K ∥ 100 pF on
  aux A / B and 6K8 on aux 1-4. Then a 10K master pot, 220 nF, and a TL072 at 1 + 10K / 2K7 (+13.4 dB, **inferred**)
  into an EBO.
- **vs ours:** the same send (pot wiper into the bus resistor, PRE per pair); ours 10K pots into 22K, six mono
  sends, OPA1612 summers.

**T11 Routing** (read; SCH p2, p3, UM p20)
- 24 group keys in pairs and L-R, each with an LED, direct or through the pan pot (odd / even).
- **Resistors:** a pair of **10K** per bus, one for each bus leg.
- **Switching:** mechanical keys at the **source end**. Released, both resistors' source ends go to ground; the
  resistors stay on the bus.
- **vs ours:** different. Ours moves the bus end of each 4K7 between the bus and AGND with a DG413, the key carrying
  logic only, so an unrouted strip is off the bus. The AMR 24 keeps every channel's 10K on every bus at all times:
  the bus impedance and the summer's noise gain do not change with routing (1 + 36 = 37 for 36 channels,
  **inferred**), which is why its noise figure is quoted "36 channels routed" and would read the same unrouted.
  Ours is quieter with few strips routed and the same when all are.

**T12 Mix bus summing** (read; SCH p3 top left, SCH p4 top left, SCH p8)
- **Every mix, group and monitor-mix bus is a balanced pair** (Mix L+ / L−, Group n+ / n−; UM p64-66).
- **Driver (EBO, PC1081):** per channel two cross-coupled TL072 pairs, one for L / odd and one for R / even, R1 = 36K
  and R2 = 18K "for mix bus balancing", +6 dB differential, 75 Ω + 220 µF / 16 V per leg, a 5K balance preset.
- **Summer:** two NE5532 halves, no discrete parts.
  - the − leg enters the first half's inverting input through "68", with 10K feedback (∥ 100 pF) from its output;
  - the second half is a unity inverter of that output (10K / 10K ∥ 100 pF);
  - the + leg enters the first half's non-inverting input through "68", and 10K from the **inverter's** output
    returns to that node;
  - 100K from each leg to ground on the bus side.
- **Result (inferred):** both legs sit at the same node voltage, the output is (I+ − I−) × R / 2, so a balanced
  source sums at Rf / Rbus and a voltage common to both legs (a ground difference between a channel and the master,
  or pickup on the pair) cancels to the matching of the resistors.
- **Gains (inferred):** group 10K / 10K, unity; stereo mix 6K8 1 % / 10K, **−3.3 dB**.
- **After the summer:** 10K into the mix insert (ground-compensated TL071 send, balanced TL072 return), the master
  fader, a TL072 post-amp (10K / 2K7 read, +13.4 dB), the output driver.
- **vs ours:** different in kind. Ours is a single-ended 4K7 bus into an OPA1612 referenced to GCANCEL, then a
  re-inverter. The AMR 24 is the second console in the library with balanced buses (after the Series Five) and does
  it with two op-amp halves where the Series Five uses a grounded-base 2SB737 pair. The price is two bus conductors
  and two 10K per assignment, and four op-amp sections per channel only to drive the buses. Our 34-way Delta pinout
  has no pairs to give; the balanced bus was dropped on 2026-10-19 / 23 for ground cancel.

**T13 Bus ground** (read; SCH p2, p3, p4, p7, UM p64)
- **Mix, groups, monitor mix:** no ground-cancel line; the pair does that work.
- **Aux:** single-ended, with one **AUX EARTH** line (lower motherboard row 27, both pins).
  - each input and output module ties it to its 0 V audio through **10K** (read; a parallel capacitor is marked
    optional);
  - each aux summer's + input rides on it through "68", with 100K to the master's ground.
  - **Inferred:** 36 modules make it a 278 Ω average of the module grounds that carries no current.
- **PFL, AFL L / R:** single-ended, summers referenced to local ground through 75 Ω, no cancel, no dummy track.
- **Chassis:** "Metalwork Ground" has its own motherboard pin (row 22b), apart from 0 V audio and 0 V logic.
- **vs ours:** our GCANCEL is their AUX EARTH applied to every summer, with 10 Ω ties, a 100K keeper and a
  re-inverter. Their tie is a thousand times higher: like Mackie's 510 Ω it averages without carrying ground
  current. The Delta too references only its aux summers.

**T14 Coupling** (read)
- "68" electrolytics at every stage boundary and at every bus leg into a summer, with 100K returns; 220 nF into the
  two fader post-amps (220K bias); 220 µF / 16 V in the EBO legs.
- **vs ours:** ours is MUSE NP 100 µF + 47K at every bus-feeding node and film at the wipers; no polar part on a
  bipolar node.

**T15 Solo** (read; SCH p2, p4, UM p23, p31)
- **Three modes from the master:** PFL, AFL (post-pan, stereo) and solo-in-place.
- **Audio:** each channel feeds PFL (from the pre-fade node, "68" + 100K + 10K) and AFL L / R (10K from the pan
  outputs) through **series J111s** (FET5-7) onto three single-ended buses. All three are switched together by the
  SOLO latch; the master chooses which bus it listens to.
- **Master (SCH p4):** three TL071 virtual-earth summers (10K ∥ 100 pF feedback), then series J111s into the
  control-room left / right feed.
- **Detect:** a logic line. Each module pulls SOLO ENABLE through a diode and 1K; the master reads it through 22K
  with 100K to the rail into CMOS. Its level does not depend on how many keys are pressed.
- **SIP:** the master drives a SIP MUTE line that cuts every module whose SAFE key is out; a FLASH bus from a TL072
  oscillator blinks the lamps.
- **vs ours:** ours is PFL only by decision: 22K onto one bus, a 100K-per-strip DC sum sensed as a voltage, a DG413
  switcher. The AMR 24 gates each feed with a JFET where ours uses the key and the DG413, and detects with a logic
  line like the 8•Bus, so it needs no clamp.

**T16 Direct out** (read; SCH p2)
- Post-fader, from the fader post-amp through 10K into a TL071 (NE5534 optional, 22 pF), ground-compensated like the
  insert send: 75 Ω + "68" on the hot pin, the cold pin through 75 Ω to ground and sensed through 10K.
- **vs ours:** the same class. Ours is impedance-balanced 75R / 75R with its level from aux 6; theirs cancels the
  far ground actively and has no level control.

**T17 Master outputs** (read; SCH p4, p8, UM p51, p53)
- **Group, aux and monitor outputs:** EBO sub-boards, cross-coupled TL072 pairs with R1 = 10K and R2 = 4K7 "for
  output balancing", 75 Ω + 220 µF / 16 V per leg, a 5K preset per output.
- **Stereo mix (SCH p4):** the same circuit on the module (TL072, 12K / 24K, 75 Ω + "68" per leg, 5K preset).
- **Balance alignment:** two 6K8 1 % across the legs, trim for minimum at their junction, typically −40 dBu.
- **Use:** either leg may be grounded; the manual wants an unbalanced load grounded at the console end (UM p13).
- **Mute relays / power-on delay:** none on the sheets read.
- **C/R:** balanced sources selected through 24K per leg into a TL071 differential stage; DIM is a J111 shunting
  470 Ω after 4K7 (−20.8 dB, **inferred**); MONO, L / R cut and an alternative-speaker key at line level.
- **vs ours:** ours is DRV135 (laser-trimmed, couplers sorted in pairs, CS11b) with relay mute and a power-on delay,
  and needs no preset. Their DIM depth is ours (CS7, −20 dB).

**T18 Meters and channel LEDs** (read; SCH p2, p3, p4, UM p23, p51)
- **Channel PEAK LED:** one point, the insert, both polarities, lit 4 dB below clipping (UM p23); three BC184s with
  2.2 µF couplers (the circuit was not traced further).
- **Meters:** moving-coil VU, one per group and for the mix, each behind a TL071 / TL072 buffer with a 5K preset
  (10K in, 22K feedback, 3K6 to the meter), reachable through a hole in the panel. PPM and an LED bargraph by Klark
  Teknik are options.
- **LED drive:** every module's LEDs are in series chains fed by BC212 current sources (two diodes and 100 Ω:
  about 6 mA, **inferred**), one for the main board and one for the sub board; a key pole shorts its LED when off.
- **vs ours:** ours has a five-tap OL detector, both polarities, 3 dB below clip with a 150 ms hold, and a −20 dBu
  signal LED; LED ladders on the master. The series chain is the Delta's scheme too (D6); ours runs each LED from
  +VL through its own 4K7 and keeps the key poles for logic.

**T19 Power** (read; SCH p2, p3, p11, p12, UM p15, p49, p64)
- **Per module:** 10 Ω + 22 µF / 25 V on each audio rail, twice (main board and sub board), a third 10 Ω pair for
  the EBO on the output module; 10 Ω + 22 µF on each logic rail and on VDD. 0 V audio and 0 V logic are separate
  motherboard pins.
- **Supplies:** two external 3U units, audio and logic, on 8 m cables to barrier strips on the console.
- **Audio PSU CD1025:** a dual-primary transformer, a bridge and **10,000 µF / 40 V** per rail, a T10A fuse after
  the bridge, then a discrete series regulator per rail: two 3055 pass transistors with 10 Ω base resistors, a
  BC441 / BC461 driver, a BC212 / BC182 error pair on a 12 V zener, a 5K preset, and four 0.22 Ω in parallel as the
  current-limit sense. +48 V from its own winding and a 783-type regulator. Outputs ±18 V, 0 V, +48 V.
- **Earth:** mains earth meets the supply's 0 V **inside the PSU through 100 Ω ∥ 100 nF**.
- **Logic PSU CD1028:** the same circuit at ±22 V, +48 V through a 250 mA fuse.
- **Protection:** current limit and fuses; no crowbar is drawn on either.
- **Service rule:** switch the console off before pulling a module (UM p49).
- **vs ours:** the same per-module RC (ours fusible 10 Ω + 220 µF, a reverse Schottky per rail, ±VL / GNDD joined at
  NT1). Our PSU has the SCR crowbar theirs lacks. Our 0 V floats in the PSU and meets chassis only at the master's
  M4 star; theirs is lifted from mains earth by 100 Ω ∥ 100 nF at the supply.

**T20 Op-amps** (read; SCH, UM p75)
- TL071 / 072 / 074 everywhere; NE5534 for the insert return, the fader post-amp and the aux summers; NE5532 for
  the bus summers; 2SB737 in the mic amp; J111 for every switch.
- 100 pF across nearly every feedback resistor; **75 Ω build-out on every op-amp output**.
- **vs ours:** OPA1612 / OPA1656 with C0G caps; our build-outs are 47-100 Ω, the same practice.

**T21 Levels** (inferred)
- The line receiver's −6 dB puts a +4 dBu input at **−2 dBu** inside, the Soundcraft level.
- On ±18 V a TL07x clips near +22 dBu, so about 24 dB of internal headroom; the insert send is rated +21 dBu.
- The stereo mix sums at −3.3 dB and is made up after the master fader.
- **vs ours:** 0 dBu internal, 23 dB to clip, unity summing (checked in CS3).

**T22 Construction** (read; UM p49-50, p63-70, p73)
- **Modules plug into two motherboards** through two 64-way two-row connectors (rows a / b, 32 positions), lifted
  out from the top after two screws; extender cards are supplied.
- **Lower motherboard, the same on every module:** Mix L / R pairs with a ground row between them, Aux Ground, aux
  A / B L / R and aux 1-4, monitor mix pairs, AFL L / R, PFL, oscillator, the logic lines (solo enable, SIP mode,
  SIP mute, flash, mute A / B, external mute, tape / group status, mic / line), 0 V audio on four pins, ±18 V audio
  on two pins each, ±22 V logic, 0 V logic, −10 V, +48 V, Metalwork Ground.
- **Upper motherboard, per module type:** the 24 group pairs on rows 7-30 (evens above, odds below, each pair on
  the two pins of one row, no ground between pairs), and the module's own balanced I/O on rows 1-5 and 32 (line in,
  insert send / return, direct out; group out, tape returns, meter).
- **External I/O:** XLR for mics; everything else through the motherboard to the patchbay cards by ribbon and to
  EDAC multiways. The parts list has a 40-way bus ribbon connector, so motherboard sections are joined by ribbon
  (**inferred**).
- **vs ours:** ours joins per-channel modules with one daisy-chained 34-way ribbon carrying buses, GCANCEL and
  power; theirs is a backplane with 128 contacts per module, half of them bus pairs.

### 4. Worth considering for goa-console
1. **A post-EQ position for pre sends that survive the mute (UM p45).**
   - **Why:** ours mutes the pre sends with ON by default (Q1, 2026-10-25) and JP2-JP4 can take a pair ahead of the
     mute, but only from HOUT, ahead of the EQ and the insert. The AMR 24's link keeps the EQ and insert on the
     unmuted send (a cue or effect feed that stays while the channel is out of the mix).
   - **Cost:** a third position (PRE) on JP2-JP4, so three jumper footprints change on every strip.
   - **Verdict:** not proposed. The need is already met pre-EQ; write it up only if a post-EQ feed that survives ON
     is wanted.
2. **Balanced buses with an op-amp-only differential summer (SCH p3, p4).**
   - **Why:** it removes ground differences and pickup without a cancel line, and needs no discrete pair.
   - **Cost:** twice the bus conductors and resistors, a driver pair per channel, a new pinout.
   - **Verdict:** not proposed; it reverses the 2026-10-19 / 23 decision. Keep the circuit on file as the form to
     use if the jig's bus tests (13-17) show residue that GCANCEL does not remove.
3. **A high-value tie to the ground-sense line (10K per module on AUX EARTH).**
   - **Why:** with Mackie's 510 Ω it is the second sense line that carries no current, against our 10 Ω.
   - **Verdict:** no new proposal. It is one more reason to make the GCANCEL-current measurement already in the jig
     list (CS11).
4. **Source-end routing with the released key grounding the resistors.**
   - **Why:** constant bus impedance and noise gain whatever is routed.
   - **Verdict:** not proposed; ours takes unrouted strips off the bus, which is quieter in a small mix.
5. **100 Ω ∥ 100 nF between mains earth and 0 V in the PSU.**
   - **Verdict:** not proposed; it conflicts with G1-G3 (one star at the master). On file as a hum-hunting option
     with AMEK's removable 10 Ω.
6. **Series LED chains from a current source.**
   - **Verdict:** not proposed; already weighed against the Delta's (D6).

**Where ours looks weaker than the AMR 24:** nothing in the line path. The AMR 24 has what a 24-track room needs and
we left out by decision (balanced buses and insert returns, stereo AFL and solo-in-place, mute groups, swept
shelves). Its line receiver, passive pan, single-point peak LED, polar couplers, unprotected outputs and a supply
without a crowbar are all behind ours.
