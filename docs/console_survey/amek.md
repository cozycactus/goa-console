# AMEK "big" (big by Langley): survey against goa-console

## 1. Header

- **Console:** AMEK **big** ("big by Langley"), an in-line 24-buss recording console. It has VCA faders, Supertrue V3
  automation (IBM PC) and the optional Virtual Dynamics. Frames: 28 or 44 **big 1** mono inputs.
  - **Modules:** big 1 mono in-line input (PCB 1111E/F), big 2 effects / stereo-group return (1112C), big 3 master
    (1113C + 1114B), big 8 stereo input (1435), 12-buss group module (1115C).
  - **Power:** an external 850 / 305 PSU (28 inputs) or 401 PSU (44 inputs).
- **Document:** `~/Downloads/961585248-Technical-Manual-AMEK.pdf`, AMEK technical manual MAN/BIG. It was issued in
  January 1994 and has pages revised to July 1997. 163 scanned pages with no text layer, read by OCR and by eye.
  - **Page key:** manual page = PDF page, as follows. 1-0 = 1, 1-4/1-7 = 5-8, 2-2/2-5 = 15-18, 2-8 = 22, 2-10 = 24,
    3-2/3-5 = 27-30, 3-9/3-11 = 34-36, 3-15/3-17 = 40-42, 4-12/4-14 = 54-56, 5-5/5-20 = 64-79, 6-1/6-18 = 80-97,
    7-1/7-4 = 98-101, 8-1/8-52 = 102-159, 9-2 = 161.
- **What's in it:** installation and earthing, the connection summary, the three PSUs (text and block diagrams),
  automation and VD (skipped), module access and internal switches, level / meter / VCA-symmetry alignment, a full
  measurement protocol, the specification, and PCB component-location overlays.
- **What's missing (important):** none of the circuit diagrams.
  Section 9 is only the list on 9-2 (big 1 = BIG/3/011, 3 × A3, and so on), and the PDF ends with the revision
  record. So **no component value, op-amp type, VCA type, summing network or mute circuit can be read here**. The
  overlays show only designators and a few labels: "MULTITK BUFFERS", "CHAN AND AUX MUTE", "DIRECT DRIVER", "VCA
  CTRL", "MON I/P" and the "+4 dBu / −10 dBV" switch on big 1 (8-3/8-5); "AUX SENDS", "L+R BUSS" and "FADER" on
  big 3. Everything below is architecture and specification from the text pages.

## 2. Published specs (7-2 to 7-4; conditions 6-1 to 6-18)

All figures are typical, measured on a Neutrik TP402. The console is aligned to +4 dBu, 28 or 44 inputs, loads
≥ 10 kΩ, RMS, 22 Hz-22 kHz, inputs terminated in 200 Ω.

| Item | Value |
|---|---|
| Operating level | +4 dBu. The insert points sit at +4 dBu in a +4 system (2-8), so the **internal level is +4 dBu** |
| Max output | +21 dBu (outputs, ≥ 10 kΩ) |
| Max line input | > +22 dBu (with the line gain at −20 dB) |
| Max mic input | +10 dBu |
| Headroom over the operating level | ≈ 17 dB (+21 − 4) |
| Rails | ±17.5 V analogue, +5 V logic (floating, remote-sensed), +48 V phantom (3-2) |
| Mic EIN | −127 dBu (60 dB gain, 200 Ω) |
| Line in/out noise, one channel | −85 dBu (unity tape path to the stereo output, faders at "0") |
| Mix noise, 28 channels routed | −80 dBu |
| Mix noise, 44 channels routed | −76 dBu |
| THD | line 0.02 % (20 Hz-10 kHz); mic 0.07 % (20 Hz / 1 kHz / 10 kHz) |
| Frequency response | tape and line −0.3 dB, 20 Hz-20 kHz; mic ±0.5 dB |
| Crosstalk, input to multitrack outputs | −70 dB (20 Hz-15 kHz) |
| Fader breakthrough (VCA off) | −70 dB (20 Hz-15 kHz) |
| Pan isolation | −60 dB (20 Hz-20 kHz) |
| CMRR | mic < −80 dB (20 Hz-15 kHz). **Line-input CMRR has a method (6-16) but no published figure.** "Line output" > −30 dB is really output balance (6-17/6-18) |
| Impedances | line in > 15 kΩ (10 kΩ in the 2-8 table), mic > 3 kΩ, tape 20 kΩ; outputs 200 Ω at 20 Hz, 100 Ω at 1-20 kHz |

The output impedance rising at 20 Hz suggests a series output coupling capacitor (**inferred**).

## 3. Topics

**T1 Line input receiver.** The mic/line XLR is balanced, 10 kΩ on line, with line gain −20 to +30 dB (2-8). The
tape input is balanced, 20 kΩ, −20 to +20 dB. The circuit is not shown. Per channel, a terminal card on the rear panel
carries the mic/line in, tape in, insert and direct out. It reaches the motherboard by a 10-way ribbon (5-5, **read**).
- vs ours: both are balanced, and their 10 k load is like our 10K/10K diff amp's. Our 1M per leg buffered receiver is
  far higher impedance. They publish no line CMRR, so there is no comparison with our 54 dB.

**T2 Line gain.** One gain control covers both ranges: mic +10 to +60 dB, line −20 to +30 dB (2-8). A separate
TAPE/BUSS GAIN trim sits on the monitor path, ±20 dB, 0 dB at the centre (5-8, **read**). Circuit not shown.
- vs ours: theirs has a wider range (50 dB on line) because it is a mic/line stage. Our ±15 dB with a 0 dB detent
  suits synths. The idea is the same as their centre-zero tape trim.

**T3 Ø.** A PHASE switch in the in-line MIX section (5-8, **read**). Its position in the path isn't shown.
- vs ours: the same function.

**T4 HPF.** Fixed 120 Hz, 12 dB/oct, switched (7-3, **read**).
- vs ours: ours sweeps 21-403 Hz. Theirs is a mic-console rumble filter.

**T5 EQ (non-mid detail).** Four bands (7-3, **read**):
- HF shelf ±18 dB at 6 or 12 kHz (switched);
- HMF peak ±14 dB, 400 Hz-18 kHz, Q 0.7;
- LMF peak ±14 dB, 100 Hz-4 kHz, Q 0.7 or 1.5 switched;
- LF shelf ±18 dB at 40 / 80 / 120 / 240 Hz.

There is an EQUALISER in/out switch.
- vs ours: theirs has wider shelf ranges, switched shelf frequencies, a much wider-range mid (Q 0.7) and a Q switch on
  LMF. Ours: fixed 12 kHz / 54 Hz shelves, ±11.5 / ±14.3 dB, mids Q ~1.44.

**T6 Insert.** Unbalanced on one TRS jack: send on the tip at 30 Ω, return 10 kΩ, at +4 dBu (2-8, **read**). It is
taken at the channel prefade insert point (6-12). The input max-level test reads it there.
- vs ours: the same unbalanced TRS. Ours is post-EQ with a 75R send and a ~47K return. Their insert level is +4 dBu,
  ours 0 dBu.

**T7 Mute.** MIX MUTE and channel mute exist, and the mutes are automated by Supertrue. One board area is labelled
"CHAN AND AUX MUTE" (8-3, **read**). The mechanism (FET, VCA or relay) is not shown.
- vs ours: can't compare. The label suggests the mute also covers the aux sends (**inferred**), as our ON does
  (design review Q1).

**T8 Fader.** VCA faders on every big 1, big 2 and big 8 path and on the main stereo output (5-12, **read**).
- The fader or the automation sets the VCA's control voltage. The FADER ISOLATE switch on big 3 chooses the source
  for all faders.
- The mix fader scale goes to +10 dB: alignment is at "MIX FADER on +10", and 0 dBu in gives +10 dBu out (5-8).
- FADER FLIP swaps the VCA fader between the channel and monitor paths. The other path then has a "CHANNEL LEVEL"
  pot or "LINEAR FADER" (5-13/5-14, **read**).
- Each VCA has a SYM trim, set for < 0.03 % THD at +10 dBu out, 2 kHz (5-13).
- Fader-off breakthrough is −70 dB.
- The VCA type isn't named. A symmetry trim is typical of dbx 2150-series / THAT 2180-type VCAs (**inferred**). The
  VD side chain uses an SSM2110 (4-12).
- vs ours: different. Ours is a passive 10K A fader with a +10 dB post-amp. Both have +10 dB above "0". Our muted
  strip measures −87 dB in sim, better than their −70 dB VCA breakthrough.

**T9 Pan.** MIX PAN feeds the L/R mix buss. On the multitrack buses the pan pot picks odd (left) or even (right)
buses. Alignment does the odd buses with the pan fully left and the even buses fully right (5-10, **read**). Pan
isolation is −60 dB. Circuit not shown.
- vs ours: the same odd/even pan into the routing. Our simulated pan rejection is −116 dB.

**T10 Aux sends.** Aux outputs are balanced, 60 Ω, at +4 dBu (2-8).
- big 8 has internal switches S31-S33: aux 1-4, 5-6 and 7-8 each send a mono L+R sum or odd = L / even = R
  (5-20, **read**). So there are at least 8 aux sends (**inferred**).
- PRE/POST and the tap points aren't shown.
- vs ours: we have 6 aux with a PRE switch per pair; their stereo-pair mode on big 8 is the same idea for stereo
  inputs.

**T11 Routing.** Each channel has a "MIX TO TRACKS" switch and six multitrack routing switches, three pairs per
switch with odd/even taken from the pan (5-9, 6-8, **read**). There is a "MULTITK BUFFERS" block on big 1 (8-3), and
the 12-buss group modules have 1115C. Input to multitrack crosstalk is −70 dB. Switch type and the bus-end
arrangement aren't shown.
- vs ours: the buffers before the routing look like our pan-buffer followers (**inferred**). Our simulated unassigned
  leakage is −102 dB.

**T12 Mix bus summing.** The circuit is not shown. The only level adjustments in the audio path are the **buss output
trims**: one per multitrack buss and L/R mix trims on big 3. They are set so that 0 dBu in gives +10 dBu out with
the fader at +10 (5-8 to 5-10, **read**). That suggests a summing / buss-amp gain trimmed per buss to absorb
tolerances (**inferred**). Mix noise is −80 dBu with 28 inputs and −76 dBu with 44.
- vs ours: fixed 4K7 / 4K7 with no trims. Their 28 → 44 step costs 4 dB, against the ~2 dB that noise gain alone
  would give, so the source isn't clear.
- Our sim gives −79 dBu with 24 strips (20 Hz-20 kHz). Theirs is measured with EQ and filter out, at unity tape
  gain. Our figure is quoted with the strip path, so like for like ours is probably comparable or better. Check
  before quoting.

**T13 Bus ground.** Not shown.
- vs ours: no comparison possible.

**T14 Bus AC coupling.** Not shown.

**T15 PFL / solo.** big 1 has AFL in the MIX section. big 8 has internal switch S34: IN = stereo AFL, OUT = PFL
(5-20). The stereo LED meter card (1127C) has SOLO and CHECK LEDs (8-41, **read**). The 1147 "PFL system" is a
recall/501-console feature and is left out on big (4-14). Auto-switching and the bus arrangement aren't shown.
- vs ours: theirs is AFL-centred (in-place, stereo). Ours is PFL with auto-switching monitors.

**T16 Direct out.** Unbalanced, 30 Ω, 3-pole jack, at +4 dBu (2-8). There is a "DIRECT DRIVER" stage (8-4, **read**).
- vs ours: ours is impedance-balanced at 75R / 75R, which is better against ground hum at the same cost.

**T17 Master outputs.**
- Stereo buss and buss outputs are balanced, 60 Ω. The main stereo has an L/R VCA on the main fader (big 3 VR
  symmetry trims, 5-19).
- Speaker outputs are unbalanced, 60 Ω. Headphones need ≥ 200 Ω phones (2-8).
- Monitor inputs: stereo playback 1 has +12 dB gain for −10 dBV machines; playback 2/3 are at 0 dB.
- Internal switch S33 on big 1 raises the monitor / tape and buss-output sensitivity by 12 dB for −10 dBV
  (5-17, 1-4).
- Output balance is only > 30 dB.
- No mute relay or power-on delay is documented.
- vs ours: ours uses DRV135 outputs (better balance), relay mute and power-on delay. They suggest a 470R / 330R / 470R
  balanced pad for sensitive monitor amps (1-5). That is worth a note in our manual (C/Room).

**T18 Meters.**
- 24 multitrack LED bargraphs on 8-way cards (1126B) and a stereo LED meter card (1127C: two ~15-LED columns, a
  40-pin DIP of unknown type, CHECK and SOLO LEDs; 8-40/8-41, **read**).
- "0" = +4 dBu, set so the first red segment just lights; the segments have hysteresis and are aligned to the
  turn-on point (5-11, **read**). Feeds come after the +4/−10 compensation. Detector and ballistics not shown; no
  channel peak / signal LED documented.
- vs ours: master LED ladders in the same style; the same "set to the turn-on threshold" practice.

**T19 Power / rails.** All values **read**. Pages: 3-2 to 3-17 and 2-10, plus the 401 block diagram on 3-11.
- **850 PSU (28 inputs):**
  - four separate linear series regulators with separate transformer windings;
  - +17.5 V 10 A, −17.5 V 5 A, +5 V 5 A, 48 V 0.5 A;
  - fuses 10 A T per bipolar rail, 5 A T logic, 1 A T phantom; mains 0.6 kVA.
- **305 PSU:** an SMPS, ±17.5 V 6.5 A, +5 V 5 A, 48 V 0.35 A; 0.4 kVA. A fault on either 17.5 V rail shuts the other
  down.
- **401 PSU (44 inputs):** a 5-output SMPS module, each output through an 1160 filter card; ±17.5 V 16 A, +5 V 30 A;
  48 V from a DC-DC converter; 0.9 kVA.
- **Grounding:** ±17.5 V and 48 V share "AGND". AGND goes to chassis/mains earth **through 10 Ω** (850:
  R10, on pins, "to allow easy removal" with a technical earth; 305: 10R + 0.1 µF; 401: an "AGND link"). The 5 V
  logic is **floating**, with its own DGND.
- **Console earth terminal:** a rear-panel technical-earth terminal on the console is the preferred earth. The 850
  has four 4 mm terminals (A GND, DIG GND, two chassis) with links fitted if there is no technical earth (2-2).
- **Cable:** one 8-pin EP8 / Litton cable, 8 m: DGND, DGND sense, +5 V, +5 V sense, −17.5 V, AGND, +48 V, +17.5 V,
  so **one pin each** for ±17.5 V and AGND.
- **Remote sense:** only the 5 V is remote-sensed. On the 401, 1 Ω 2.5 W resistors run from sense to output, so
  regulation falls back to local if a sense wire opens (3-11).
- **In the console:** a power distribution card (1128C) has four large toroidal chokes (L1-L4), electrolytics, and
  diodes CR1 / CR2 between the "IN" terminals (±17V5, +5 V, DGND, +48 V, AGND) and the outputs to the
  motherboards (8-42). LC filtering at the entry is **inferred** from the layout.
- vs ours:
  - rails almost identical (±17.5 vs ±17 V), and ours is also an external linear PSU;
  - our analogue 0 V floats in the PSU and is hard-bonded to chassis at the console star; theirs is 10 Ω to earth in
    the PSU, removable, plus a console technical-earth terminal;
  - we have separate logic rails and a logic ground as they do;
  - our power filtering is per strip (10 Ω + 220 µF), theirs is central.

**T20 Op-amps / stability.** Not documented: the overlays show U1-U21 on big 1 without types. The only named analogue
IC is the SSM2110 in VD.

**T21 Levels / headroom / noise.** Internal level +4 dBu, max out +21 dBu: ≈ 17 dB of headroom (above). Line max
> +22 dBu. Noise is under T12 and section 2.
- vs ours: internal 0 dBu with +23 dBu swing, so ≈ 23 dB of headroom: 6 dB more than theirs, and a noise floor
  relative to it that is about as good.

**T22 Construction.**
- Each module plugs into a **64-way connector** on a 16-channel motherboard (1118B). The fader stays attached by its
  own Molex lead (5-5).
- Each input's jacks are on a **rear terminal card linked by a 10-way ribbon** (5-5).
- big 3 has three extra 26-way ribbons (monitor I/O, aux). The multitrack buss output cards (busses 1-8, 9-16,
  17-24) each use a 26-way ribbon (5-6).
- Modules come out with a screw used as a handle; there are extender cards for trims.
- vs ours: the same split as ours: a module PCB plus a separate jack board on a 10-way ribbon. Their bus is a
  backplane per 16 channels; ours is a daisy-chained IDC ribbon.

## 4. Worth considering for goa-console

1. **Adopt their measurement protocol in `test_jig_spec.md` (6-2 to 6-18).** It gives exact, repeatable methods:
   - mix noise with N inputs terminated in 200 Ω;
   - fader breakthrough as B = 20 − F at +20 dBu;
   - pan isolation T = 20 − P;
   - line-input CMR with a 0.01 %-matched 100 Ω pair driven common-mode;
   - **output balance** with matched 1 kΩ legs;
   - max input and max output by "rapid rise in THD", with the scope checking that the residue is harmonics.

   Cost: none, it's documentation. Fit: good. Our jig spec lacks an output-balance test for the DRV135 outputs and a
   line-input CMR figure measured this way. Our 54 dB figure is from simulation with a 1 kΩ source imbalance.
2. **A removable 10 Ω (+ 100 nF) between the console star and chassis, instead of a hard bond.**
   - Why: an earthed synth on a TS cable plus our hard 0 V-to-chassis bond is the loop `ground_study.md` can't fix.
     A 10 Ω / 100 nF "limited earth" keeps RF bonding and a safe DC reference, and cuts the LF loop current by the
     ratio of 10 Ω to the loop impedance.
   - Cost: a 2 W resistor, a cap and a link on the star bar.
   - Fit: good for a bench full of earthed synths, as a hum-hunting option. It isn't a safety earth: chassis stays on
     mains earth through NC7 pin 1. Check against G1-G3 before adopting.
3. **Fallback resistors on any remote-sense line (401: 1 Ω 2.5 W, sense to output).** We don't sense the ±17 V (a 70 mV
   drop over 2 m is harmless), so this applies only if we ever add remote sense to the PSU. Low priority.
4. **A balanced 470R / 330R / 470R pad for sensitive monitor amps (1-5).** It is a manual note, not hardware: it puts
   the C/Room pot back in its useful range with hot active monitors. Cost: none. Fit: good, since synth studios
   often have small active monitors.
5. **Q switch on the LMF (0.7 / 1.5) and switched shelf frequencies.** `eq_survey.md` already notes that Q controls are
   the one feature we lack.
   - Cost: a PVA2 key and resistor switching in the KHN damping, plus panel space we don't have on 8 HP.
   - Fit: marginal for line-level synth mixing. Only if the panel has room.

**Where ours looks weaker:** nothing clear-cut from this document. On fader-off breakthrough, routing isolation,
headroom, direct-out balancing and output balance ours is better on paper. Two caveats:
- Their measured, published line-input/output noise (−85 dBu, one channel at unity) is a bench figure. Our −91 dBu
  is simulated, so the jig should confirm it.
- Their big 1 takes > +22 dBu on line. Check that our receiver followers and diff amp also clip above +22 dBu at the
  jack (our op-amp outputs swing +23 dBu, so it is likely but not shown for the input pair).

**Not covered by this document** (no schematics): the circuit and values of T1-T3, T6-T16, T18 detectors, T13 bus
grounding / ground cancel, T14 coupling, T20 op-amp types and stability. Automation and VD were skipped as asked.
