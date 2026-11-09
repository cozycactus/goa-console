# Yamaha PM-4000 / PM-5000 survey (label: yamaha)

## 1. Header
**Documents read** (all page numbers are PDF pages):
- **PM-5000 service manual** (693 pp., vector schematics):
  - specs p.3-5;
  - the circuit-diagram contents p.545;
  - CO power entry p.558;
  - INHA head amp, HPF, insert and direct out p.579; VCA, ON relay and pre/post buffers p.580;
  - INSEND pan / LCR p.583, routing multiplexers p.584, per-channel power and the 50-way analog bus p.586;
  - INSUB panel switches p.590; INBUS backplane p.560;
  - MAS1 summing amp p.607; MT meters p.647; REAR master line amps p.658.
- **PM-5000 block / level diagram** (separate PDF, p.1).
- **PM-4000 service manual:** specs p.3-4.
- **PM-4000 Circuit Board PDF** (400-dpi scans):
  - mono input p.6;
  - master (group) module p.13;
  - PW4000 block p.38 and DC1 regulator p.40.

**Not read:**
- GAM5000 option module, owner's manuals, part lists.
- The PM-4000 stereo master and rear panels; the PM-5000 MONI pages.

**Missing:**
- The PM-5000's PSU (PW5000) is not in these documents.
- The PM-4000 input uses Yamaha hybrids (HA, INS, PEQ, EBO, VCA, BA, SUM). Their internals aren't shown, so PM-4000 values are sparse.

**Big caveat:** both are mic consoles. The PM-5000 "MONO IN" has no separate line input. A line source goes through the mic head amp with a 26 dB pad (PM-4000: 30 dB pad). Both consoles are VCA-based; the PM-5000 is motor-fader, scene-recalled analogue.

## 2. Published specs
**PM-5000** (p.3-5):
- **Distortion and response:** THD < 0.1 % at +14 dBu / 600 Ω. Response 0 / +1 / −3 dB, 20 Hz-20 kHz.
- **Noise,** with a 12.7 kHz 6 dB/oct filter (Yamaha calls it the 20 kHz brickwall equivalent):
  - EIN −128 dBu; residual −100 dBu;
  - with every assign off: stereo / stereo aux −92 dBu, group/aux −87 dBu, matrix −89 dBu;
  - one input at max gain, fader nominal: −64 dBu.
- **Crosstalk:** −80 dB at 1 kHz, −70 dB at 10 kHz.
- **Levels:** internal level 0 dBu (aux buses −6 dBu, level diagram). I/O +4 dBu nominal, +24 dBu max, 150 Ω out. Line sub/insert inputs 10 kΩ. Clip line on the level diagram about +20 dBu.
- **Input:** pad 26 dB, gain 50 dB variable. HPF 12 dB/oct, 20-400 Hz.
- **DC in:** ±16 V, +12 V, +48 V.

**PM-4000** (p.3-4):
- THD, response, EIN and residual as the PM-5000.
- Group out −85 dBu with switches off (48 ch); stereo −84 dBu; matrix −94 dBu.
- Crosstalk −80 / −70 dB.
- PW4000 PSU: ±19 V 13 A, +12 V 8 A, +48 V 0.7 A; 1100 W for 48 ch.

## 3. Topics

**T1 Line input receiver**
- **PM-5000 (read, p.579):**
  - Discrete front end: an IMT1A dual PNP pair (Q103) with 2SA1312 transistors, 270 R / 2.2 K emitter and collector networks, gain pot T2K.
  - Then a diff stage, IC102A NE5532P, with 10 K "B-grade" resistors.
  - It has a **CMRR trim:** VR111 B200 preset with 22 K / 18 K ("CMG-ADJ").
  - Input impedance 3 kΩ. HAG is a separate head-amp ground.
- **PM-4000 (read, p.6):** a hybrid IC101 "HA" behind the 30 dB pad.
- **vs ours:** different. Theirs is a mic-amp front end; ours is a dedicated buffered line receiver with a higher input impedance. Our input is better suited to synths.

**T2 Line gain**
- **PM-5000 (read, p.579):** HA2 gain pot VR101 T5K with 1.1 K into IC102B (NE5532), coupled by 100 µ/16 caps. Range −60 to −10 dBu sensitivity, plus the 26 dB pad.
- **vs ours:** theirs is +50 dB of mic gain; ours is ±15 dB. Not comparable.

**T3 Polarity (Ø)**
- **PM-5000 (read, p.579):** an inverting NJM4580 stage (IC103, 10 K / 10 K, 68 p) after the gain stage, selected in or bypassed by a mechanical push switch on INSUB.
- **vs ours:** ours swaps the receiver legs and costs no op-amp. Ours is better.

**T4 HPF**
- **PM-5000 (read, p.579):** unity Sallen-Key, 12 dB/oct, Q fixed.
  - Two 0.12 µF caps; NJM4580.
  - Tuned by a dual C-law pot: C50K with 2.4 K in series (feedback leg), C100K with 4.7 K (ground leg). 20-400 Hz.
  - Mechanical HPF switch; output 100 µ/16 + 22 K.
- **PM-4000 (read, p.6):** the same topology, VR111 C100K / C50K and 0.12 µF caps.
- **vs ours:** same range. Ours is a KHN tuned by an A10K dual used as dividers. Theirs again uses a C-law dual (consistent with docs/studies/eq_survey.md).

**T5 EQ (not mid tuning)**
- 4 bands, all fully parametric (Q 0.5-3). HI and LOW switch peaking / shelving. EQ ON switch. NJM4580 / NE5532.
- **vs ours:** they have Q controls on every band; ours has fixed Q.

**T6 Insert**
- **PM-5000 (read, p.579):**
  - Selectable pre/post-EQ (INSERT PRE key), insert in/out key.
  - **Balanced send,** two op-amps (IC111 NJM4580): one inverting, 10 K in / 16 K feedback; one non-inverting, 11 K / 16 K with a 10 K / 18 K input divider. 33 p across each feedback, 75 R build-outs, 100 µ/25 out + 100 K, DAN217 diode clamps to ±15 V. Level +4 dBu.
  - **Balanced return:** diff receiver IC110 with 16 K in and 10 K feedback (−4 dB, so +4 dBu becomes 0 dBu), 68 p, 10 µ/25 input caps, 100 K bleeds, DAN217 clamps. Normalled by the jack.
- **vs ours:** theirs is balanced both ways at +4 dBu; ours is an unbalanced send and a follower return at 0 dBu.

**T7 Mute (ON)**
- **PM-5000 (read, p.580):**
  - A DPDT signal relay, RY101 NA-12W-K, with a 12 V coil and 1SS355 flyback diode, driven by the CPU (scene / mute groups).
  - Each pole is a changeover: the common feeds the buffer, one throw takes the signal, the other ground. So it mutes series and shunt at once, on both the pre-fader send feed and the post-VCA feed.
  - After it: 10 µ/25, 100 K, 220 R + 220 p, 47 K, then NJM4580 followers, then 220 µ/16 + 22 K.
- **PM-4000 (read, p.6):** two RY12W relays, transistor-driven. Mute groups 1-8 come in through diodes; R180 / C176 sit on the driver.
- **vs ours:** relay versus our J112 ramp. A relay gives over 100 dB with no ramp, but it clicks. Ours (about 86 dB, 20 ms ramp) suits live use.

**T8 Fader / VCA**
- **PM-5000 (read, p.580):**
  - The motor fader is a DC control only.
  - CV: fader and VCA groups 1-12 summed in NJM2068 (10 K / 10 K / 10 K), scaled 1.6 K / 13 K, then 470 R + 2200 p into EC−.
  - VCA: THAT2181LC with 20 K in, an OP275 current-to-voltage stage (20 K // 22 p), a THD trim (B10K + 270 K into SYM) and its own 100 µ supply bypasses.
- **PM-4000 (read, p.6):** a DC fader buffered by NJM2041, VCA CVs 1-8 through an RA101 100 K × 10 network, into a VCA hybrid with offset and THD trims.
- **Group masters (both):** audio faders; PM-4000 A10K plus a BA buffer (read, p.13).
- **vs ours:** different. Ours is an audio fader with a +10 dB post-amp. They use VCAs everywhere, for automation and recall.

**T9 Pan**
- **PM-5000 (read, p.583):** LCR pan with RK097 multi-gang pots: A20K / C20K pairs for L/R, and T40K plus a B50K "CSR" pot (6.8 K / 24 K) for centre.
  - Every wiper: 220 R + 100 p into an NJM4580 follower, 47 µ/16 or 22 µ/25 out, 22 K or 47 K bleed.
  - The pan law isn't stated.
- **PM-4000:** A20K / C20K pan into a BA hybrid.
- **vs ours:** same idea (followers on the wipers before the bus resistors). Their law comes from an A/C taper pair. Our −6 dB centre from a linear dual is a deliberate Delta choice.

**T10 Aux sends**
- **PM-5000 (read, p.584 + block diagram):**
  - 12 stereo aux (level + pan) and 8 group/aux.
  - 12 K bus resistors.
  - Aux ON switched by a TC74HC4053 at the resistor's bus end.
  - A PRE key per aux; an internal switch picks the pre point (pre / post EQ). Aux bus −6 dBu.
- **PM-4000 (read, p.6):** 8 aux + 2 stereo aux, A20K pots, 18 K into the bus, a PRE/OFF/POST key per aux.
- **vs ours:** similar. Ours is 22 K with a PRE key per pair.

**T11 Routing**
- **PM-5000 (read, p.584):** exactly our topology.
  - The 12 K summing resistor's bus end goes to a TC74HC4053AF common.
  - X0/Y0 go to the bus; X1/Y1 go to SUMG.
  - VEE, INH and GND of the 4053 sit on SUMG, and there are 100 p caps.
  - It works on a 5 V CMOS part because both throws sit at about 0 V (virtual earth or ground).
- **PM-4000 (read, p.6):** mechanical 2-pole keys with LEDs feeding 18 K resistors (R185-R196). I couldn't trace with confidence where the off-throw connects.
- **vs ours:** same principle. Theirs is cheaper (HC4053 on 5 V, not a DG413); ours has more margin. No change needed.

**T12 Mix bus summing**
- **PM-5000 (read, p.607):** a composite summing amp.
  - Bus → 220 µ/25 (AC coupling at the summing node, 100 K bleed) → base of a discrete PNP diff pair (2SA1312 ×2, 470 R degeneration, 2SA1312 tail source, 5.1 V zener) → NJM4580.
  - Feedback: 2.4 K, plus 27 K and a B47K trimmer that the SUM GAIN control taps (block diagram: "SUM GAIN 0 to −20 dB"); 220 p / 33 p.
  - Then a 10 K / 10 K NJM4580 inverter (68 p) and 10 R + 47 µ/25 out.
  - 12 K in against 2.4 K feedback doesn't give the stated range without tracing the switch; treat the gain as **not verified**.
  - Sub-in joins through 24 K.
- **PM-4000 (read, p.13):** SUM hybrid, 18 K in, 27 K + 22 p feedback, 220 µ BP coupling, 47 µ out + 100 K.
- **vs ours:**
  - Theirs uses a discrete low-noise front end where ours uses an OPA1612, which already matches it.
  - Their re-inverter is a plain inverter (no subtraction of a ground line).
  - Their bus resistors are 12-18 K against our 4K7.

**T13 Bus ground (inferred from the PM-5000 nets)**
- SUMG is each channel's analog ground: its cap-multiplier reservoirs and the 4053s' ground throw.
- It runs on 10 of the 50 pins of the analog bus connector (HIF2E 50-way, pins 20-29) to the INBUS backplane.
- At the master, the summing pair's other base and the inverter's + input sit on SUMG.
- So the summing amps are referenced to the channels' own ground return. That is the same goal as our GND CANCEL, but with no 10 Ω and no differential subtraction.
- Separate grounds: HAG (head amp), ISTG (input stage), DOG (direct out), DGND (logic), +12G (relays / LEDs).
- PM-4000 (read, p.6): SUM GND on about 25 odd pins of CN101, interleaved with the bus lines (like our even GND pins), and +12 GND separate.
- **vs ours:** similar intent; our ground cancel is more explicit and measurable.

**T14 AC coupling**
- Electrolytics at every follower output (220 µ/16, 47 µ/16, 22 µ/25) with 22-47 K bleeds.
- 10 µ/25 at stage inputs.
- 220 µ/25 at the summing node.
- No film caps.
- **vs ours:** similar; ours uses film at the pot wipers.

**T15 PFL / cue**
- **PM-5000:** CUE L/R/C buses, fed by input cue through 12 K via a 4053. PFL/AFL is selected per master, with CPU cue priority.
- **PM-4000 (read, p.6):** INPUT CUE L/R through 18 K, plus DC "SOLO LOGIC" and "INPUT CUE PRIORITY" lines.
- **vs ours:** the same DC-detect idea as our PFL DET.

**T16 Direct out**
- **PM-5000 (read, p.579-580):** the same balanced 2-op-amp driver as the insert send (IC112 NJM4580DD, 75 R, 100 µ/25, DAN217 clamps), +4 dBu.
  - Internal switches choose pre/post EQ and pre-fader / post-fader-post-ON.
- **PM-4000:** an EBO hybrid.
- **vs ours:** theirs is actively balanced; ours is impedance-balanced from aux 6.

**T17 Master outputs**
- **PM-5000 (read, p.658):** cross-coupled balanced line amp, two NJM4580 halves per output.
  - 10 K / 11 K in, 18 K feedback, 20 K cross-feedback, 33 p, 75 R build-out.
  - 220 µ/25 out + 100 K, DAN217 clamps, 10 µ/50 in.
  - Each op-amp rail 10 R + 10 µ/50; ICP-N10 fuses on the board.
- Master ON is a relay (block diagram).
- **vs ours:** functionally the same as our DRV135 with its 10 µ sense caps. No power-on mute relay is shown on the output.

**T18 Meters**
- **PM-5000 output meters (read, p.647):** 20-point LED bar.
  - Non-inverting ×3 (1.8 K / 3.6 K), precision full-wave rectifier (4.7 K, DAN217).
  - 100 K / 0.22 µ smoothing (22 ms, not a peak hold), buffer.
  - **The LEDs are a series string fed by 2SB1132 current sources (220 R / 100 R), with one comparator per LED and a ladder of small resistors (24 R, 10 R, 13 R, …).** That is our architecture.
- **PM-5000 input meter:** 9-point.
  - The PEAK LED is a discrete window detector (IMT1A pairs) that lights 3 dB below clip at **three points: pre-EQ, post-EQ and pre-fader**.
- **vs ours:** the bar meter is the same; the strip peak detect is wider.

**T19 Power**
- **PM-5000 (read, p.558, p.586):**
  - ±16 V comes in on 4 pins each, 4700 µ/25 per rail on CO.
  - **Per input channel:**
    - LS-MT-Y223NB EMI chokes;
    - ICP-N10 IC-protector fuses;
    - Darlington capacitance multipliers (2SB1132 + 2SC2412K; 2SD1664 + 2SA1037AK; 1 K + 10 µ/25 base RC);
    - D1F60 reverse diodes and 100 µ/25, giving ±15 V;
    - +12 V → +11 V for relays / LEDs, and 78L05 / 78L12 for logic.
- **PM-4000:**
  - PW4000 (read, p.40): ±28 V raw → ±19 V 13 A linear regulator with six parallel pass transistors per rail, each with 0.1 R / 5 W emitter resistors and ICP-F50 fuses. Current limit, NJM2041 error amp, HZT7A3 reference, remote sense, tracking negative rail. Relay inrush/protection board and fans.
  - Modules (read, p.6): F10 IC protectors on ±20 V, then transistor regulators (inferred).
- **vs ours:** ours is 10 Ω + 220 µF per strip with wing PTCs. Theirs: a fuse and a cap-multiplier per channel.

**T20 Op-amps / stability**
- NJM4580 nearly everywhere; NE5532 in the head amp; NJM2068 and OP275 around the VCA; NJM2041 in the PM-4000.
- 220 R + 100-220 p at every follower's + input. 33-68 p across feedback, 75 R build-outs.
- DAN217 rail clamps at every jack-facing I/O.
- 0.01 µ ceramic per rail per op-amp.
- **vs ours:** the same practices, except the I/O clamps.

**T21 Levels:** internal 0 dBu as ours; I/O at +4 dBu. Rails ±15 V (ours ±17 V, so we have about 1.5 dB more headroom).

**T22 Construction**
- **PM-5000:** each channel is several boards (INHA, INSEND, INSUB, INJK, INDMB, INFAD). The bus runs on a 50-way IDC to INBUS backplane PCBs (8 / 12 / 16 channels).
- **PM-4000:** modules plug into a bus PCB through CN101.
- **vs ours:** ours is one board per strip on a ribbon.

**Topics the documents don't show:** PW5000 (the PM-5000 PSU); PM-4000 hybrid internals; PM-5000 PFL-detect hardware (CPU).

## 4. Worth considering for goa-console
1. **Diode clamps to the rails at every op-amp I/O that faces a jack** (DAN217, i.e. a BAV99 / BAT54S equivalent):
   - Where: insert send / return, direct out, master and aux outputs, after the build-out or coupling cap.
   - Why: hot-plugging, ESD, a synth's DC or phantom from a patchbay.
   - Cost: one SOT-23 per leg, pennies.
   - Fits a synth console, where patching happens live. Check whether ours has them; if not, this is the one place ours looks weaker than common practice.
2. **Overload detection at more than one point:**
   - What: OR the OL detector across post-receiver/gain, post-EQ (up to +15 dB boost) and pre-fader.
   - Why: our OL may sample one node, and EQ boost or a hot insert return can clip unseen.
   - Cost: a few diodes and resistors into the existing LM393 stage. Fits.
3. **Per-strip fuse (and optionally a cap multiplier):**
   - Why a fuse: an ICP-N10-style fuse per strip on ±V isolates a shorted strip from the 34-way ribbon. Our wing PTCs protect groups of strips, and the PTC trips the whole wing in our accepted 4.5 A worst corner.
   - Why a cap multiplier: it gives tens of dB more ripple / noise rejection than 10 Ω + 220 µF.
   - Cost: about 1 V of headroom (17 → 16 V) and four transistors per strip.
   - Fuse: worth it. Cap multiplier: only if the bench shows supply-borne hum.
4. **A balanced insert return (diff receiver, 16 K / 10 K):**
   - Why: outboard gear is often balanced, and an unbalanced return on a console tied to synth grounds invites loops.
   - Cost: one op-amp half and four resistors.
   - Fit: moderate. A pseudo-balanced cable already covers most of it.
5. **Skip:**
   - CMRR trim presets: no help against unbalanced-source mismatch, which dominates our 54 dB.
   - VCAs and motor faders: automation only.
   - Switchable SUM GAIN: for 48-channel frames.
   - HC4053 routing: cheaper, but our DG413 works with margin.

None of their circuits suggests our bus summing, routing or ground scheme is weaker. The PM-5000 confirms bus-end switching to ground and a summing reference tied to the channels' ground return.

Working files (renders and crops) are in a scratch folder outside the repo (not kept).
