## sc6000: Soundcraft 6000 and Soundcraft 200B

### 1. What I read

**Soundcraft 6000** (1988)
- `Soundcraft 6000/soundcraft_6000_schematic.pdf` and `soundcraft 6000 schematic.pdf` are byte-identical (same MD5). Six 600-dpi scans.
  - p1: system diagram MI2911.
  - p2: input channel ED2721, issue 1, 24-3-88.
  - p3-p4: master R/H PCB ED2722, sheets 1-2.
  - p5: S500 "Standard O/P", the group module ED2176.
  - p6: S500/600 Aux Master L/H ED2174.
- The JPGs in `Soundcraft S-6000/` are the same drawings, split into halves at lower resolution. I used the PDF.
- `Soundcraft6000UG.pdf`:
  - p4: performance specifications.
  - p5: input module description.
  - pp71-81: schematics. p73 is a later master mix board, ED2771/A issue P3 (18-10-88), which has a different mix summing amp.
- Missing: the 6000 PSU, the meter bridge, and the return-module detail.

**Soundcraft 200B**
- `Soundcraft-S200B-mix-sch.pdf` and `soundcraft s-200b.pdf` hold the same 10 page images. Their contents:
  - p1: rear input connector PCB ED2301, which carries the line pad.
  - p2: stereo input ED2298.
  - p3: LH master. Not read.
  - p4: master RH ED2251.
  - p5: sweep-EQ input. Not read.
  - p6: standard input ED2183.
  - p7: standard output (group) ED2179.
  - p8: console wiring.
  - p9: small-console PSU ED2116.
  - p10: ground-compensated output wiring MI2426.
- `Soundcraft-200B-UG-ZM2310.pdf` and its `_original` copy are identical. I read:
  - PDF p26: interface levels.
  - PDF p37: PSU.
  - PDF pp40-42: technical description.
  - The spec page (PDF p3) is a blank factory test sheet. **The 200B documents publish no noise, CMRR or crosstalk figures.**
- `200.pdf` is the original Series 200 user manual (1983). It holds only 200-dpi schematics; I used it only for the PSU page.

### 2. Published specs

**6000** (UG p4):
- Frequency response: +0 / −0.5 dB, 20 Hz-20 kHz, any input to any output.
- THD at +20 dB over nominal: groups < 0.004 % at 1 kHz and < 0.01 % at 10 kHz; other outputs < 0.008 % and < 0.02 %.
- Noise:
  - mix, 16 channels routed: −87 dBu (S/N 91 dB);
  - group, 16 channels routed: −82 dBu;
  - aux, 32-channel console: −84 dBu.
  - The measurement conditions (fader positions, EQ) are not stated.
- Crosstalk:

| Path | 1 kHz | 10 kHz |
|---|---|---|
| Adjacent channel | −110 dB | −95 dB |
| Channel mute | −110 dB | — |
| Fader kill | −85 dB | −78 dB |
| Pan isolation | −90 dB | — |
| Aux send kill | −90 dB | — |
| Routing | −110 dB | −100 dB |

- Impedances: line input 20 kΩ balanced; insert return 10 kΩ; outputs < 75 Ω.
- Balanced outputs: ≥ +26 dBu into 600 Ω.
- CMRR: no number; the text only says "exceptionally high".
- Line gain covers nominal inputs from +10 to −20 dBu (UG p5).

**200B** (UG pp35-37, p21):
- Internal level −6 dBu nominal; interfaces +4 dBu or −10 dBV, set per board.
- Groups and aux outputs are ground-compensated; mix and control-room outputs are electronically balanced.
- Rails: ±17 V audio, +48 V phantom; unregulated 26 V on the reservoirs.

### 3. Topics

**T1 Line receiver**
- 6000 (**read**, ED2721): the line input has 15K in series per leg on the rear connector PCB. It then feeds a TL072 difference amp (IC2-A) with 4K7 inputs (R16 / R17), 4K7 feedback from a follower (IC2-B) and 4K7 (R19) to ground. That gives about 20 kΩ per leg, matching the spec. CMRR rests on the 15K resistors matching; no tolerance is marked.
- 200B stereo input (**read**, ED2298):
  - 47 µF on each leg with 33K bias.
  - Cold leg: 47K into an inverting stage (6K8 feedback), then 6K8 into the summing node of IC1 (TL074).
  - Hot leg: 47K straight into that summing node. The result is a two-op-amp virtual-earth receiver with 47K per leg.
- 200B mono input (**read**, ED2183/ED2301): a 4K7/470/4K7 pad on the rear PCB, then the transistor mic preamp (2N4403 pair + TL072), selected by the LI key.
- vs ours: different. Ours is buffered (1M per leg + OPA1656) with 54 dB CMRR against a 1K source. Neither Soundcraft input survives source-impedance imbalance as well. Ours is better.

**T2 Line gain**
- 6000 (**read**): no separate gain stage. A 5K RD gain pot is a divider on the diff amp's output, with 150R + 330R at its bottom. Its wiper is buffered by IC2-B and fed back through R18 4K7, so receiver and gain are one stage. S2-D re-references R19 between line and mic modes. Range per UG: +10 to −20 dBu nominal inputs. This is the Delta-style topology we rejected as 4.7 dB noisier.
- 200B stereo (**read**): the 10K lin pot sits in a T-network in the summer's feedback (27K, 2K2, 1K + 100 µF), plus jumper J5 (9K1).
- vs ours: different. We use a separate inverting stage. Keep ours.

**T3 Ø (polarity)**
- 6000: S3 swaps the legs ahead of the diff amp (**read**).
- 200B stereo: S1 swaps the legs ahead of the 47 µF caps (**read**).
- vs ours: same.

**T4 HPF**
- Both consoles (**read**): Sallen-Key, unity, 47n / 47n, 22K feedback, 47K to ground. **Inferred** from the values: fc ≈ 105 Hz, Q ≈ 0.73. Fixed frequency, labelled "100 Hz", switched in/out (6000 S4, 200B S4).
- vs ours: theirs is fixed; ours is a sweepable KHN at 21-403 Hz.

**T5 EQ (mid tuning skipped)**
- 6000 (**read**): four cascaded inverting TL072 stages, each 47K / 22K.
  - HF shelf: 10K lin, 3n3 + 7K5.
  - Mids: Wien band-pass tuned by a 100K dual ("100K-X2"), 10K lin boost/cut.
  - LF: 20K lin Baxandall with 3K3 / 3K3 and 100 nF, in its own stage.
  - System diagram: HF 10 kHz, HM 600 Hz-10 kHz, LM 150 Hz-2.4 kHz, LF 60 Hz. EQ switch S5.
- 200B mono (**read**): four bands in only two op-amp stages, with fixed-frequency mids on 20K lin pots.
- 200B stereo: HF / LF only.
- vs ours: the 6000 is the Delta EQ's ancestor and essentially the same. The 200B's 2-op-amp packing is cheaper but has fixed mids.

**T6 Insert**
- 6000 (**read**): post-EQ, before the mute; send through 75R (R119). Return impedance 10 kΩ per spec; the return circuit was not clearly legible.
- 200B master (**read**): insert after the first inverter, on the switching contacts of the TRS jack.
- vs ours: same position and same 75R send.

**T7 Mute**
- 6000 (**read**), "electronic mute":
  - IC5-B (22K/22K) → 47 µF → 4K7 → **series J111** into the virtual earth of IC6-A (4K7 // 220p).
  - A **shunt J111** sits at the 4K7 junction.
  - Gates are ramped by 220K / 100 nF (**inferred** τ ≈ 22 ms) from discrete FET drivers.
  - The ON key works through an op-amp flip-flop (IC6-B, 680K feedback). It also takes a mute bus (100K, group mutes), a computer port (automation), SIP-mute with a per-channel "SIP SAFE" jumper, and a reset from the PFL-detect line.
  - Spec: −110 dB channel muting.
- 200B: a mechanical ON key.
- vs ours: different. We use shunt J112s only (≈86 dB). The 6000 gets its 110 dB from series-into-virtual-earth plus a shunt.

**T8 Fader and post-amp**
- 6000 (**read**): wiper → 2.2 µF → 47K → NE5534, with 4K7 / 2K2 (+9.9 dB) // 100p. The 75R build-out is inside the loop, followed by 220 µF / 6.3 V. Pre-fade load is annotated "max 1K4", post-fade "max 600R".
- 200B mono: ALPS 10K log, TL072 +11 dB (12K / 4K7).
- vs ours: the 6000 is identical (our R38 2K2), except for its 47K load (ours 100K) and the electrolytic output cap.

**T9 Pan**
- 6000 (**read**): 2 × 10K lin dual, buffered by NE5532 followers with gain 1 + 2K2/10K (+1.7 dB). Each buffer also has a 3K3 (R75 / R76) whose function I could not resolve.
- 200B mono (**read**): **unbuffered**. The pan pot drives the 22K routing resistors through 3K9.
- vs ours: the 6000 matches ours; the 200B is cheaper.

**T10 Aux sends**
- 6000 (**read**):
  - six sends, 10K log pots, 22K into the bus;
  - PRE key on pairs 1-2 and 3-4; aux 5-6 post only;
  - jumpers J2 / J3 pick pre-EQ or pre-fade for 1-2.
- 200B (**read**): four sends with **7K5** into the bus; pre/post-EQ and pre/post-fader jumpers per pair.
- vs ours: the 6000 is the same.

**T11 Routing**
- 6000 (**read**):
  - group routing resistors 22K, 1/8 W; mix resistors 4K7 (R77 / R78);
  - mechanical switches move each resistor's bus end between the bus and MAIN GND;
  - 24-bus option on a second 10-way IDC (CN5).
- 200B (**read**, and UG p36): 22K for mix and groups; the released end is grounded "so that crosstalk cannot occur to the bus across the switch contact capacitance".
- vs ours: same principle. Our DG413 keeps audio off the keys, and our groups use 4K7 rather than 22K.

**T12 Mix-bus summing**
- 6000 master, issue 1 (**read**, ED2722):
  - a **common-base 2N4403** whose emitter is the summing node;
  - 6K8 bias from a filtered SUM V+;
  - collector 10K // 47p to SUM V−, then 2.2 µF into a TL072;
  - feedback 8K0 // 33p to the emitter; DC loop 1M // 33p;
  - bus enters through a ferrite bead and 100 µF / 10 V.
  - The group and aux masters (S500 boards) use the same circuit with 27K / 22K feedback.
- 6000 issue P3 (**read**, UG p73):
  - a **differential pair** of common-base 2N4403s (10K emitter loads from +17 V via 220R / 220 µF; 4K7 collectors + 820R to −17 V; 220p);
  - TL072 across the collectors;
  - feedback through an inverter and **2K0** to the emitter, "gain −6.8 dB ref channel fader top";
  - bus coupled with 220 µF / 6.3 V.
- 200B (**read**): plain NE5532 inverting summer, 15K // 100p, 100 µF in series with the bus.
- vs ours: different. The discrete front end beat a TL072's noise. With an OPA1612 (1.1 nV/√Hz) it buys nothing, so skip it. The 6000 does sum below unity (see Worth considering 2).

**T13 Ground cancel**
- 6000 channel (**read**): R74 **10 Ω "GND CANCEL RES"** from the module ground to a cancel bus line, the same as ours.
- Summing amps (**read**): transistor bases and op-amp + inputs sit on a separate "SUM GND" / "SUMMING AMP GND". On P3 the mix path through the insert send is referenced to SUM GND L.
- That SUM GND equals the cancel line is **inferred**: the master's "GND CANCEL BUS" pin is drawn without a wire.
- There is no difference re-inverter back to master ground.
- vs ours: same idea. Our explicit re-inverter is more thorough.

**T14 Bus AC coupling**
- 6000 / 200B (**read**): one electrolytic in series with each bus at the summing amp (100 µF / 10 V or 220 µF / 6.3 V). The channel output caps are 220 µF / 6.3 V and 47 µF / 25 V electrolytics.
- vs ours: different. We couple at every source (100 µF NP + 47K) with film at the wipers. Theirs costs fewer caps; ours keeps DC off the bus.

**T15 PFL / solo**
- 6000 (**read**):
  - channel: PFL 22K (R40) onto the PFL bus, and SIP DET 100K (R41) onto a DC detect line;
  - master: a TL072 PFL detector (100K / D6, 150K to V−), plus an "initial reset" that pulses the enable bus low to reset the inputs;
  - SIP (solo-in-place) logic;
  - switcher: series J112s (47K gate-source, diodes, 47 µF);
  - PFL sum: TL072, 22K // 100p, 100 µF in series with the bus, 47K bus terminator, then a 12K/12K inverter.
- 200B (**read**, and UG p37): each channel pulls the "Solo Enable" bus to V− through 100K. A TL071 (IC9) holds that bus at a **virtual earth**, "so that there are no transient signals on it that might crosstalk onto the audio buses".
- vs ours: the 100K detect is the same. Ours senses a line that swings (0.5 → 0.92 V); theirs keeps the line at 0 V.

**T16 Direct out**
- 6000 (**read**, system diagram): "LINE OUT" taken post-fader, after the post-amp; unbalanced. Electrical detail is **inferred** (post-amp output, 75R inside the loop).
- vs ours: ours is impedance-balanced. Ours is better.

**T17 Master outputs**
- 6000 / 200B (**read**):
  - sum → inverting insert-send driver (12K / 12K, 75R) → master fader → NE5532 post-amp with a +4 / −10 jumper;
  - cross-coupled balanced output: NE5532 pair, 4K7 / 10K SIL networks, 22p / 33p, 75R + 47 µF per leg, balance trim (1K pot between 1K / 1K).
  - Control-room amps (6000): TL072 with discrete complementary followers (10R emitters, diode bias), 100 µF out, 47R, "ground-cancel".
  - 200B groups / aux: **ground-compensated** outputs. The cold pin is sensed through 75R / 12K / 22K into the amp, and you wire cold to ground at the far end (MI2426).
  - No mute relay or power-on delay is shown.
- vs ours: different. Our DRV135 + relay with power-on mute is more robust; theirs is cheaper.

**T18 Meters**
- 6000 channel peak LED (**read**): two transistors; 47K + 2.2 µF into a base biased by 5K6; 680K / 2.2 µF stretch; 4K7 LED. Threshold not stated.
- 200B stereo overload: a similar two-transistor circuit. 200B VU drive cards are trimmed to 0 VU = +4 dBu.
- vs ours: ours is comparator-based and calibrated. Ours is better.

**T19 Power**
- 6000 channel (**read**):
  - ±17 V through 10R + 47 µF / 25 V per rail (R103 / R104), op-amps decoupled only by those caps;
  - LEDs and FET drivers on a separate ±VB;
  - master has separate "logic power" (V+ / V−) and ±VA audio rails;
  - summing-amp bias rails are RC-filtered (3K3 / 1K8 + 220 µF on the master, 4K7 / 1K + 47 µF on the aux board) and referenced to SUM GND.
- S500 modules: 6.3 mm **spade terminal** for ground, and C35 100 nF to the spade.
- 200B master: separate VA / VB rail sets (10R + 47 µF each) with separate grounds 0VA / 0VB.
- 200B PSU (**read**, ED2116): LM317K / LM337K (360R / 4K7, 22 µF adjust bypass); 4700 µF / 50 V reservoirs; discrete +48 V; no crowbar.
- vs ours: same scheme (10R filter, separate logic rails, spade ground). We add a crowbar and per-IC decoupling.

**T20 Op-amps**
- 6000 channel: TL072 throughout, NE5534 post-amp, NE5532 pan buffers. Master: NE5532 outputs, TL072 plus discrete summer front ends.
- 33p / 100p across feedback resistors; 75R build-outs inside the loop.
- Couplers are electrolytics everywhere.
- vs ours: modern parts, and we use C0G caps and film couplers.

**T21 Levels and headroom**
- 6000: mix insert at −10 dBV / −7.8 dBu; group fader at −2 / −13.8 dBu (annotated).
- 200B: internal level −6 dBu.
- vs ours: we run 0 dBu internal, 6-8 dB hotter. That means less headroom on ±17 V.

**T22 Construction**
- 6000 channel: one PCB with a 10-way rear-connector PCB (the line-input 15K resistors and the phantom feed sit there). Fader on a 3-way connector with a screened send; 40-way IDC motherloom; chassis grounded through the pot bracket.
- Group, aux and 200B modules: card-edge bus connectors, a chassis pin or spade, jumper-selected group buses ("odd / even group select links").
- vs ours: the 6000 is very close to ours (main PCB + small connector board + IDC loom). The group select links are the equivalent of our SUB / AUX jumpers.

**Not covered by the documents:**
- 6000 PSU and meter ladder.
- CMRR numbers for either console.
- 200B noise and crosstalk specs.
- I did not read the 200B sweep-EQ input, the LH aux master, or the 200.pdf (Series 200) schematics.

### 4. Worth considering for goa-console

1. **Virtual-earth sensing of the PFL-detect line** (200B IC9; 6000 PFL detector).
   - **Why:** the master holds the line at 0 V and reads the current, so pin 29 never swings. That removes the edge we currently debounce with 1 µF, and any coupling into the neighbouring ribbon pins 28 / 30.
   - **Cost:** one op-amp section and a resistor or two at the master; `sim/pfldet.py` needs re-running.
   - **Fit:** good.
   - The 6000's "initial reset" pulse is only needed if latching keys are used (ours latch mechanically), so skip that part.
2. **Sum below unity on the mix bus** (6000 P3: 2K0 feedback on 4K7 sources, −6.8 dB, made up after the master fader).
   - **Why:** 24 hot synths panned together can clip our unity summer before the master fader can help. Summing lower adds headroom, and it also lowers the summer's noise gain, roughly 25 → 11.
   - **Cost:** change the 4K7 feedback, add gain in the master post-amp, and redo the noise sim.
   - **Caveat:** the bus resistors' thermal noise is unchanged relative to signal, so the noise benefit is small. This is mainly a headroom question.
   - **Fit:** worth a sim at N = 24 with +12 dBu sources.
3. **Ferrite bead in series with each bus at the summing amp** (every 6000 / S500 summer).
   - **Cost:** cents per bus.
   - **Fit:** good; our ribbon buses are about 1 m long. Size it so it doesn't upset the summer's stability (check with the master stability decks).
4. **Mute depth** (6000: series JFET into a virtual earth plus a shunt, −110 dB).
   - **Caveat:** the 6000's own fader kill is only −85 dB, and our ≈86 dB is adequate for synths.
   - **Fit:** optional. Only consider it if bench tests show mute bleed.
5. **Spec gap to check, not a design change.** The 6000 publishes mix noise of −87 dBu with 16 channels routed. Our sim gives −79 dBu with 24 strips (about −81 scaled to 16).
   - The 6000's conditions are unstated (probably EQ out, faders at nominal or down). Ours is EQ in, faders at "0", +10 dB post-amp, and EQ current noise is still open (N1).
   - Re-run `sim_console.py` with EQ bypassed before reading this as a weakness.

**Not worth copying:**
- Discrete common-base summers (obsolete with OPA1612).
- Bus coupling at the summing node instead of at each source.
- Unbuffered pan (200B).
- 15K-series or 47K virtual-earth receivers; our buffered receiver is better.
- Electrolytic couplers.
- Ground-compensated outputs: our DRV135 and impedance-balanced outputs already cover that job.

Working files (renders and crops) are in `/private/tmp/claude-501/-Users-ruslanmigirov-projects-goa-console/20d2ad3b-cdbe-4f15-9de0-d1ce86379e7b/scratchpad/survey/sc6000/`.
