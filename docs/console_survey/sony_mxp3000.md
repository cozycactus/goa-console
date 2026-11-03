## Sony MXP-3000: survey report (label: sony)

### 1. Header
**Console:** Sony MXP-3000 (MXP-3020 / MXP-3036 frames, 1980s). It is an in-line multitrack console: each I/O module has a channel path and a monitor path, with mic pre, EQ and VCA as plug-in daughter boards. Every PDF is a scan with no text layer.

**Documents read** (page numbers are PDF pages, with the manual's own page number):
- `sony_mxp-3000_series_mixer.pdf`, Operation and Maintenance Manual vol. 1:
  - contents and section 1-4, 7 overviews;
  - specs p.21-22 (1-11, 1-12);
  - power installation p.25-26 (2-3, 2-4).
- `03 Modules.pdf`:
  - I/O module sheet 1 p.3 (3-3) and sheet 2 p.5 (3-5);
  - master module p.7 / p.9 (3-7, 3-9);
  - monitor module p.17 (3-17).
- `08 Fader Packages.pdf`: AFP p.3 (8-3), MAF p.5 (8-5).
- `06 Voltage Controlled Amplifiers.pdf`: dbx 202X VCA p.5 (6-3).
- `07 Mother Boards.pdf`: UMB p.3 (7-3).
- `14 Power Supply Boards.pdf`: console PSU p.6 (14-6), DCC p.7 (14-9).
- `09 Meter Housing Boards.pdf`: contents, mechanical PPM p.9 (9-9).
- `16 Listening Amplifier.pdf`: p.3 (16-3).
- `17 Electrical Parts List.pdf`: IOM p.3-4 (17-3, 17-4).
- Technical bulletin 89-070: meter mounting only, nothing electrical.

**Missing:**
- The console PSU ("Deltona") has a component layout only, no schematic.
- The Sony thick-film hybrids (DIS II differential input, DLO-F differential line out, ACN III summing amp, overload indicator) appear only as blocks with gains.
- Appendix C (system grounding) is not in the 83-page PDF.
- The EQ (05) was skipped per the brief.
- Where the schematic and the parts list disagree, both values are given below.

### 2. Published specs (p.21-22)
- **Mix bus:**
  - summing bus headroom +24 dB; output trim −14 to +5 dB;
  - noise better than −84 dBu with no channel or one channel assigned (unity, bandwidth not stated);
  - bus crosstalk better than −60 dB at 15 kHz;
  - transformerless active differential outputs: +4 dBu nominal, 120 Ω, +28 dBu max; THD < 0.01 %, SMPTE IMD < 0.02 % at max.
- **Internal level −2 dBu:** EQ nominal −2 dBu / max +22 dBu; pre-master-fader patch −2 dBu / +24 dBu. EQ noise better than −85 dBu (20 Hz-20 kHz, flat).
- **Monitor line input:** 10 k, ±10 dB gain, +4 dBu nominal, +28 dBu max.
- **Master fader:** turn-off better than −90 dBu; tracking ±2 dB. Master noise −80 dB at unity.
- **Control room:** inputs 5 k differential; left/right separation better than −55 dB at 15 kHz.
- **Power:**
  - PSU outputs +18, −18, +24, +48 V DC and 5 V AC; 100-260 VAC; 35 ft cable;
  - fuses 20 A on each of ±18 V and +24 V, 2 A on +48 V (p.26).
- **Not published:** CMRR and frequency response for the line inputs.

### 3. Topics

**T1 Line input** (03 p.3)
- **read:** optional 1:1 transformer (bypassed by jumpers JW1 / JW2), then 47 µF/16 V on each leg into a Sony DIS II hybrid, "AV = −6 dB".
  - The schematic marks those caps NP; the parts list (C1101) says polar electrolytic.
  - The insert return, mic-pre return and every master wild input use the same DIS hybrid.
- **inferred:** +4 dBu in becomes −2 dBu internal. The hybrid's topology and input impedance are not documented.
- **vs ours:** same idea (balanced receiver, then a gain stage). They have no per-leg buffers that we can see, an optional transformer, and run 6 dB lower internally.

**T2 Line gain** (03 p.3, parts list)
- **read:** NE5534 inverting stage. Input → R1501 3K3 → 10K lin pot (RV1500) → R1503 3K3 → output. The wiper goes to the inverting input through a coupler: 2.2 µF NP per the parts list, 47 µF NP on the schematic. 47K from the input and 47K + 22 pF from the output also reach the inverting input, so DC gain is −1. Spec ±10 dB.
- **vs ours:** the same topology. Theirs uses 3K3 end resistors (±12 dB before the 47K paths; ±10 dB published), ours 2K2 (±15 dB).

**T3 Polarity** (03 p.3)
- **read:** a unity inverter (5532, 10K/10K, 10 pF) after the filters; S27 picks the direct or the inverted signal.
- **vs ours:** different. They add a stage; we swap the legs ahead of the diff amp, which costs no stage. Ours is better.

**T4 HPF / LPF** (03 p.3, parts list)
- **read, HPF:** R402 6.19K / R405 10K 1 % attenuator (−4.2 dB), 5532 follower, then a Sallen-Key high-pass: C411 / C412 0.15 µF film, R410 / R412 3K3 plus a 50K dual rheostat (RV400). The amp gain is 1 + 11.3K / 18.2K = 1.62. The schematic looks like 10.2K; the parts list says 18.2K.
- **inferred, HPF:** Q ≈ 0.72, net gain ≈ 0 dB, sweep ≈ 20-320 Hz.
- **read, LPF:** fixed unity-gain Sallen-Key low-pass, C502 0.01 µF, C504 0.022 µF. R502 / R504 are chosen from a table for 5-20 kHz; 665 Ω gives 16 kHz.
- Both filters have IN switches and can be moved between the channel and monitor paths.
- **vs ours:** same 12 dB/oct Butterworth sweep over a similar range. Ours is KHN with a stocked A10K dual; theirs needs a 50K dual rheostat. They also have a fixed LPF.

**T5 EQ** (p.21 only)
- **read:** MXBK-EQ31, ±15 dB, Q 1.5 ± 10 %:
  - LF 40-250 Hz, shelf or peak;
  - MID1 150 Hz-2.5 kHz;
  - MID2 800 Hz-8 kHz;
  - HF 8-20 kHz, shelf or peak.
- An EQ-to-monitor switch moves the EQ between paths.
- **vs ours:** more switchable (shelf / peak on LF and HF, wider ranges); otherwise comparable.

**T6 Insert** (03 p.3)
- **read:** EQ OUT HIGH through a 22 Ω build-out (R48). EQ OUT LOW is wired to the module's AG, so the send is ground-referenced.
- The return (FADER IN HIGH / LOW) goes through 47 µF on each leg into a DIS II differential receiver. The patch bay normals the send to the return.
- **vs ours:** different. Their return is ground-sensing (pseudo-balanced); ours is single-ended (75R send; 1K + 100 pF into a follower) on one TRS jack.

**T7 Mute** (08 p.3, 03 p.3)
- **read, channel mute:** S2 on the fader package is a mechanical changeover. It switches the post-amp input from the fader wiper to the fader's ground end, so it is post-fader only. It has a 24 V lamp.
- **read, 2-mix mute:** S39 grounds the source end of the 7.5K bus resistors. The resistors stay on the bus.
- **read, send-master mutes:** S13-S16 switch the level-pot top to AG.
- **read, FET switching:** monitor, PFL, solo and meter switching use J111s with 4.7M + 22 pF gate networks (soft switching).
- **vs ours:** our J112 ramped shunt mute, which also mutes the pre sends, is better. Their source-end 2-mix mute keeps the bus loading constant, as ours does.

**T8 Fader** (08 p.3, 06 p.5, 03 p.5)
- **read, non-automated (AFP):**
  - 5K fader (RV1) fed through 100 µF NP;
  - wiper loaded by R1 12.7K 1 % (optional) and R2 10K 1 % after a 47 µF NP coupler;
  - NE5534 non-inverting, R3 10K over R4 3.92K 1 %, so +10.9 dB; 33 pF / 22 pF; output 100 µF NP + 47K.
- **read, automated:** the fader is a DC control (0-5 V) for a dbx 202X VCA (6.04K in, 7.32K + 56 pF I-V on a 5532; "0 V full atten, 5 V +12 dB"). Allison and Aphex VCAs are alternatives.
- **read, rotary (monitor) fader:** 10K, 15K wiper load, NE5534 at +12 dB (10K over 3K3).
- **inferred:** the ≈5.6K load on a 5K track bends the law heavily, so the post-amp needs about +11 dB.
- **vs ours:** same post-amp idea (+10 dB on ours). Ours loads the wiper with only 100K.

**T9 Pan** (03 p.5)
- **read:** bus pan RV1200, a 5K dual, with R50 / R51 750 Ω and R49 150 Ω (1/4 W) in a law network. Odd and even bus drivers follow: 5532 non-inverting, gain 2 (+6 dB), 47 µF NP in with a 20K bias, 220 µF NP + 22K out. The monitor pan is similar (2.5K dual, 750 Ω).
- **inferred:** the exact law network could not be traced.
- **vs ours:** similar (dual pot, then buffers). Theirs makes up gain after the pan; ours uses unity followers.

**T10 Aux sends** (03 p.3, parts list)
- **read:**
  - 6 sends. Sends 1-4 are mono 10K audio pots (RV5-RV8); sends 5/6 are a 10K dual audio pot (RV9) fed by 5532 ×2 buffers.
  - PRE / POST switch per pair; channel / monitor source switch per pair.
  - Wipers drive the 7.5K 1 % bus resistors (RN4) directly. Optional 20K resistors from wiper to ground (R52-R57).
- **read, master:** sends are summed with 15K feedback, so +6 dB. Each send master adds a balanced "wild input" through a DIS (−6 dB) and 15K into the sum. Then mute, a 10K level pot and a DLO line out.
- **vs ours:** similar unbuffered pot-into-bus approach. Their lower bus resistor gives a higher noise gain: ≈73 at 36 modules against our 22K / noise gain 25.

**T11 Routing** (03 p.5)
- **read:** 24 track buses through 15K 1 % networks (RN1-RN3), switched by mechanical 2-pole push keys at the source end. Odd buses come from the left pan driver, even from the right. A DIRECT switch (S45) sends the module's own ACN output to its line out.
- **inferred:** the off position grounds the resistor's source end.
- **vs ours:** ours (DG413 at the bus end, logic-only key) keeps the switch out of the audio and stays quiet. Theirs carries audio through the panel key.

**T12 Mix bus summing** (03 p.3 / 7 / 9 / 17)
- **read:** every bus has an ACN III hybrid (inverting virtual-earth amp). The bus reaches the inverting input through a 220 µH choke in series with a large NP cap:
  | Bus | Series cap | Summing R | Feedback |
  |---|---|---|---|
  | 2-mix | 1000 µF / 6.3 V NP | 7.5K | R1403 7.68K 1 % + 100 pF (≈ unity) |
  | Send masters | 1000 µF / 6.3 V NP | 7.5K | 15K + 56 pF (+6 dB) |
  | Track bus (on each I/O) | 220 µF NP | 15K | 3K + 25K trim + 47 pF (−14 to +5.4 dB, matches the spec) |
  | Solo | 220 µF NP | 7.5K | 7.5K + 18 pF (5532 summer, not the hybrid) |
- The choke on the 2-mix can be bypassed by a jumper.
- **vs ours:** same virtual-earth summing. Their series choke and cap at the summing node keep DC noise gain at unity and isolate the bus capacitance.

**T13 Ground cancel / bus ground** (07 p.3, 03 p.3 / 5 / 7 / 9 / 17)
- **read, COM lines:** each bus family has its own COM line on the mother board, run beside it: CHAN ACN COM, SENDS ACN COM, 2 MIX ACN COM, SOLO ACN COM, PFL ACN COM.
- **read, module ties:** every I/O ties its AG to each COM line through a resistor. Values disagree between sources:
  | Line | Schematic | Parts list |
  |---|---|---|
  | 2-mix, R77 | 1K | 1K |
  | Send, R84 | 1K | 4.7K |
  | Chan ACN, R1003 | 100 Ω | 1K |
  | Solo, R88 | 1K | — |
- **read, receiving end:** the summing amp's + input sits on the COM line. The master end ties the line to master AG with R1401 1K (2-mix), R512 1K (solo) and R2301 2K (sends). An unused ACN input is terminated with an optional 510 Ω to its COM line (UMB R1).
- **read, PFL:** the PFL COM tie is switched by a J111 (Q2), so only the modules being PFLed set the PFL reference.
- **vs ours:** the same averaged-ground-reference principle. Differences:
  - theirs uses one COM line per bus family (ours: one GCANCEL wire for everything);
  - module weights are about 1K (ours 10 Ω);
  - the master tie is of the same order as one module (1-2K), where ours has none (100K keeper);
  - they need no re-inverter because the hybrid is referenced directly.

**T14 Bus AC coupling** (03 p.3 / 5)
- **read:** sources are AC-coupled (220 µF NP + 22K on the bus drivers) and the summing inputs are too (above).
- **vs ours:** ours couples at the sources (100 µF NP + 47K) only; theirs couples at both ends.

**T15 PFL / solo** (03 p.5, 08 p.3, 16 p.3, 03 p.17)
- **read:**
  - PFL: J111 series switch (Q3, 4.7M / 22 pF gate) through 7.5K 1 % onto PFL ACN, driven by a DC PFL COMMAND line. The fader-mounted PFL key carries logic only (10K + 0.1 µF).
  - Solo: stereo solo-in-place on SOLO L / R ACN through 7.5K 1 %, plus a SOLO COMMAND line. The monitor module switches the control room to solo with J111s.
  - PFL speaker: J111 mute → TL071 → µPC1238 amplifier on +24 V.
- **vs ours:** same scheme (logic key, DC command line, soft-switched bus). Their switched PFL ground reference is a neat extra.

**T16 Direct / line out** (03 p.5)
- **read:** DLO-F hybrid (+6 dB) fed through 47 µF NP and 15K / 30K. 220 µF NP on each output leg + 22K to AG. RV10, a 500 Ω 1-turn trim, between hybrid pins 11 / 12. Optional 1:1 transformer.
- **inferred:** RV10 trims leg balance / CMRR.
- **vs ours:** an actively balanced output against our impedance-balanced 75R / 75R.

**T17 Master outputs** (03 p.9, 08 p.5)
- **read:**
  - The mix drives a 0 dB DIS (1700 / 1800) into the passive stereo master fader. The fader's bottom end returns on its own LOW / FADER GROUND wire; 51K bleeds sit across the caps.
  - The DLO input reads the wiper against FADER GROUND (22K to AG, 750K bias, 22 pF).
  - Output stage: DLO-F +6 dB; 220 µF NP per leg; 500 Ω trim (RV13 / RV14); optional transformer.
  - Mono: L and R through 47 µF + 30K each into a DLO.
- **read:** no output relay or power-on mute is visible on the mains.
- **vs ours:** ours has relay mute with power-on delay; theirs has a ground-sensed fader. Both are actively balanced (ours DRV135).

**T18 Meters** (03 p.3 / 5, 09 p.9)
- **read, per I/O:**
  - "OVERLOAD INDICATOR 1400" hybrid with separate red and green LEDs, fed through 2.2 µF + 100K, with two 18-turn threshold trims (RV2 2K, RV3 10K);
  - meter source selected by J111s into a TL072 virtual-earth stage (10K / 10K / 22 pF).
- **read, mechanical PPM per channel:** TL074 precision full-wave rectifier (10K 1 %). Charge resistor R6 3.65K. The hold cap C3 is barely legible ("0.47 / 1 %"?). Discharge R7 2.0M + R24 221K. Then a transistor-array log converter; the part number reads "CA3080 ARRAY", not reliable. Local LM340L-15 / LM320H-15 regulators.
- **inferred:** attack about 1.7 ms if C3 is 0.47 µF.
- VU, LED send meters and a phase meter exist but were not read.
- **vs ours:** an overload plus signal LED pair, as ours. Their channel meters are moving-coil, against our LED ladder.

**T19 Power** (p.25-26, 14 p.6 / 7, 03 p.5, 08 p.3)
- **read, supply:** external linear "Deltona" PSU; layout only. Six 14-pin regulator ICs in sockets, type not printed.
- **read, cable:** two 15-pin connectors, 35 ft, carrying **remote sense** (−18 V, +18 V and AUDIO GND sense; +24 V and +24 V GND sense), a Faraday shield conductor and FG chassis.
- **read, in-console decoupling board:**
  - 2 × 10,000 µF / 35 V on each ±18 V rail, plus 0.1 / 0.22 / 0.001 µF, 470 Ω bleeders;
  - 2 × 4700 µF / 63 V on +48 V; 10,000 µF on +24 V; 22,000 µF on +5 V.
- **read, grounds:** Analog, Peripheral (+24 V lamps / LEDs / relays), Digital and Frame grounds are separate.
- **read, per module:** ±18 V through 1.0 Ω + 22 µF + 0.1 µF; +24 V through 10 Ω + 22 µF; +48 V through 47 Ω.
- **read, per IC:** 47-100 Ω + 22 µF / 35 V on each rail (5534 100 Ω, 5532 / TL072 47 Ω, hybrids 22-47 Ω).
- **vs ours:**
  - Ours: ±17 V, 10 Ω + 220 µF per strip, one logic ground.
  - Theirs adds remote sense and per-IC RC filtering, and runs the LEDs and lamps on a separate +24 V with its own ground.

**T20 Op-amps / stability** (parts list p.3)
- **read:** NE5532AP / NE5534AN, TL072 / TL074 for metering, J111 FETs, 74C74 logic, Sony hybrids (DIS II, DLO-F, ACN III). Op-amps are socketed. 10-33 pF across almost every feedback resistor.
- **vs ours:** ours uses newer parts (OPA1612 / 1656) with C0G caps and build-outs throughout.

**T21 Levels / headroom / noise**
- **read:** internal −2 dBu, outputs +4 dBu, clip about +22 dBu single-ended (+28 dBu differential), so about 24 dB headroom. Mix noise better than −84 dBu with one channel; no figure for N routed.
- **vs ours:** ours (0 dBu internal, about +21 dBu clip; sim −91 dBu for one strip, −79 dBu for 24) is comparable or better. Their −60 dB crosstalk spec is weak.

**T22 Construction** (03, 07)
- **read:** long in-line modules with plug-in daughter boards (mic pre, EQ, VCA, overload hybrid). Upper and lower mother boards carry every bus and COM line as PCB traces into edge connectors. Separate fader packages on a fader mother board. Tuchel multipin connectors and a patch bay. Separate master, monitor and comms modules.
- **vs ours:** a backplane where ours uses a ribbon; theirs is a far bigger frame.

**Not covered by these documents:** none fully. T5 internals were skipped; the PSU regulator circuit and the hybrid internals are missing.

### 4. Worth considering for goa-console
1. **One reference line per bus family, with a modest master tie.** They give mix, sends, solo and PFL each their own COM line.
   - Why: a separate GCANCEL conductor for aux / PFL would keep aux return currents off the MIX reference. Their 1-2K master tie, with about 1K per module, shows a tie can be harmless *if it is weighted like one module*.
   - Cost: spare ribbon conductors (1, 3, 5, 7, 19 are free).
   - Our sim found a 22 Ω tie costs 45 dB, so check any tie in `sim_console`. Probably not worth it unless the jig shows aux hum.
2. **Switched PFL ground reference** (J111 on each module's PFL COM tie). The PFL sum then references only the soloed strips' grounds.
   - Cost: a FET or one DG413 section per strip plus a conductor.
   - Modest gain, because PFL is a monitoring path. Low priority.
3. **Remote sense on the PSU cable.**
   - Why: it removes cable IR drop and ground-return error at the console end (they sense ±18 V and audio ground).
   - Cost: 2-3 more contacts (our NC7MD-LX is full), plus LM1084 ADJ wiring.
   - Only useful if our cable is long or the 4 A drop matters. Ours is short; skip unless bench droop shows up.
4. **Ground-sensed insert return** (diff receiver, send's low = module ground).
   - Why: it kills hum loops through outboard.
   - Catch: it needs separate send / return jacks or a balanced return; our single TRS insert cannot carry a ground-sense conductor.
   - Fits only if the jack board changes. Our G2 / G3 work already covers the main inputs.
5. **Separate supply and ground for lamps / LEDs / relays (+24 V "peripheral"), and per-IC RC rail filtering.**
   - Ours already separates logic (±VL, GNDD).
   - Per-IC 47 Ω + 22 µF is 1980s 5532 practice; modern op-amp PSRR makes it marginal, and our boards are dense. Not recommended.

**Where Sony is not better:**
- Polarity through an extra inverter.
- A mechanical post-fader-only mute.
- Audio through the routing keys.
- No mute relay on the mains.
- −60 dB crosstalk.

**Nothing on the line-level path of ours looks weaker than this console's practice.** The series 220 µH + NP cap at each summing node could be noted as RF / bus-capacitance isolation. Our ribbon bus is already simulated stable to 2.2 nF, so it is optional.

Working files (crops and renders) are in a scratch folder outside the repo (not kept).
