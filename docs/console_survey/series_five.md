# series5: Soundcraft Series Five

## 1. Header
- **Document:** `Soundcraft Series Five/SeriesFIVETMzm0204.pdf`, Technical Manual ZM0204 (©1997, drawings dated 1997–99). It is a 208-page scan with no text layer. "pN" below means the PDF page.
- **Contents:**
  - p3–4: table of contents.
  - p20–25: block diagrams.
  - p27–33: mono and stereo input functional description.
  - p75–76: specifications (5.2 / 5.3).
  - p79: drawing list.
  - p80–169: schematics with PCB layouts.
  - p173 onward: spare parts.
- **Drawings I read:**
  - Mono input "RH PCB" ED3698A–C (p80–82): filters, EQ amps, routing, direct out.
  - Mono input "LH PCB" ED3699A–D (p84–87): input amps, insert, EQ cores, mute, VCA, fader post-amp, pan, aux, bus connector, peak detector, PFL.
  - Output (group) module ED3702A (p101).
  - Master 1 ED3704A–C (p107–109).
  - Master 2 ED3706A–D (p113–116).
  - Input fader card ED3711A/B (p132–133).
  - Power distribution / loom ED3718A (p150).
  - CPS2000 PSU ED3804A/B (p168–169).
  - Spare parts p184.
- **Not read:** stereo input sheets, master fader ED3713, meter drive cards ED3719 / ED3772, rear-connector boards.
- **Missing from the manual:** any noise or level figure per stage, and the mute ramp RC values on the fader card (not legible).

## 2. Published specs (p75–76)
- **Levels:** internal level −2 dBu (marked on every schematic). Outputs are +4 dBu nominal and +26 dBu max into 1 kΩ, balanced, <75 Ω. Insert send +4 dBu, max +26; insert return max +21 dBu, >15 kΩ.
- **Mono input:** sensitivity −70…−2 dBu (mic) or −20…+10 dBu (RNG line range). Max +30 dBu. Impedance is given as **2 kΩ** for both ranges.
- **Rails:** ±17 V. A 48-channel console draws 12.98 A per rail plus 0.8 A on +8 V.
- **Noise:**
  - Residual (mix out, nothing routed, mix fader at 0): −90 dBu.
  - Bus noise (32 channels routed, input faders at −∞, mix or group fader at 0): < −78 dBu.
  - Mic EIN < −127.5 dBu (200 Ω).
- **THD at +20 dBu, 1 kHz:** <0.004 % XLR to direct out, <0.005 % to mix out.
- **CMRR:** mono input 60 dB at 1 kHz.
- **Crosstalk at 1 kHz, +20 dBu:**
  - Mute >100 dB; fader cut >90 dB; pan isolation >85 dB.
  - Mix / group routing isolation >100 dB.
  - Group-to-group, group-to-mix and mix-to-group <−90 dB.
- **Frequency response:** +0/−0.5 dB, 20 Hz–20 kHz.

## 3. Topics

**T1 Line input receiver (read, p84).**
- **Line path (RNG range):** the XLR legs go through 47 µF (C92 / C39), then 15K per leg (R171 / R51), then the RNG switch, then the Ø switch. After that come 47 µF and 4K7 per leg into an NE5532 difference amp (IC2-A). The + leg has 4K7 to ground, and there is 100 pF on each input.
- **Gain:** the feedback 4K7 is driven by IC2-B, a follower on the wiper of VR1-B (5K "RD" gang across the output, with 120R + 220 µF to ground). This makes it a variable-gain difference amp.
- **Mic amp:** a discrete 2SB737 pair, bypassed on line.
- **Inferred:** the XLR still sees the mic amp's input network in line mode, which would explain the spec's 2 kΩ input impedance.
- **vs ours:** different. Theirs has no input buffers, low input impedance and 60 dB CMRR, measured with a 0 Ω source. Ours (OPA1656 followers, 1M per leg) is better against synth source impedances.

**T2 Line gain (read, p84).**
- The gain is inside the receiver: one dual pot VR1, with VR1-A setting mic gain and VR1-B line gain.
- Range is about 30 dB (+10 to −20 dBu into −2 dBu).
- **vs ours:** different. They combine receiver and gain in one stage; we use a separate inverting stage with a detent.

**T3 Ø (read, p84).**
- SW2 swaps the legs between the 15K resistors and the difference amp.
- **vs ours:** same.

**T4 HPF (read, p80).**
- A unity-gain Sallen-Key 12 dB/oct high-pass, swept 20–600 Hz on TL072:
  - input divider 2K7 / 2K7 (−6 dB);
  - C1 100n and C2 47n;
  - quad-gang pot sections as rheostats plus 4K7;
  - gain 2 from 6K8 / 6K8.
- It is followed by a Sallen-Key low-pass (1–20 kHz: 4K7 + pot, 2n2 / 1n, follower).
- The output goes through 47 µF with 47K to ground.
- **vs ours:** different topology, same purpose. Ours is a KHN; theirs is cheaper and has a wider range.

**T5 EQ (read, p85, skimmed).**
- Four inverting TL072 stages, each with a 10K lin centre-detent gain pot and 22K / 22K, 47 µF between stages.
- The band cores are TL072 KHN filters with 100KC rev-log dual rheostats and a Q pot (0.5–3).
- **vs ours:** already covered in eq_survey.md.

**T6 Insert (read, p84).**
- Pre-EQ by default, post-EQ by jumpers JMP1-6. The return is switched in by the INSERT IN key, not by a jack normal.
- **Send:** a cross-coupled TL072 balanced driver: 4K7 in, 10K feedback, 33 pF, 75R + 47 µF per leg. PR1 (4K7 balance trim) sits between two 2K2s, and there is 330 pF to chassis on each leg.
- **Return:** NE5532 receiver, 10K in / 4K7 feedback (−6.6 dB, +4 → −2 dBu), 33 pF, 330 pF per leg to chassis, then 47 µF + 47K.
- **vs ours:** different. Theirs is balanced on both ends at +4 dBu; ours is unbalanced and normalled.

**T7 Mute (read, p86 and p133).**
- An inverting stage (IC14-A TL072, 4K7 in, 4K7 feedback, 33 pF) with a J111 in series between the 4K7 and the virtual earth, plus a J111 shunt at the junction (to ground via 47 µF).
- The FET drivers are on the fader card (0 V on, −15 V cut); the ramp RC values are not legible.
- It sits before the VCA and fader. Pre-fade sends can be taken pre-mute or post-mute (jumpers J20 / J21).
- Spec: mute >100 dB.
- **vs ours:** similar idea (JFET shunt). They also put a series JFET inside the virtual earth, which gives a deeper mute than our two shunts (>100 vs ~86 dB).

**T8 Fader (read, p86 and p184).**
- ALPS 100 mm 10K (DD0369). It is driven from a TL072 inverter through 47R and loaded by 33K.
- The post-amp is a non-inverting NE5532, +8.3 dB (3K96 / 2K2, value hard to read), followed by a +1.7 dB stage (1K / 4K7).
- Annotations: −3.7 dBu after the post-amp and −2 dBu after the +1.7 dB stage, so fader "0" is about 10 dB down.
- A THAT 2181 VCA is switched out by J111s when no VCA group is assigned.
- **vs ours:** same principle (fader "0" ~10 dB down, then makeup gain).

**T9 Pan (read, p86).**
- A 20K linear quad-gang pot with taps (LCR mode, PR2 220K, 15K tap resistors) giving a 4.5 dB centre drop.
- Each side is buffered by a non-inverting NE5532 at +1.7 dB (2K2 / 10K), coupled out through **1000 µF / 6.3 V**.
- Unity inverters (4K7 / 4K7) make the "−" legs for the balanced bus.
- The PAN key chooses panned or unpanned odd/even feeds to the groups.
- **vs ours:** similar (buffered pan). Their law is −4.5 dB at centre, ours −6 dB, and they add inverters for the − legs.

**T10 Aux (read, p86 and p82).**
- 12 sends on 20K log pots. The wiper goes straight to the bus through **10K**; only the stereo-aux pan pairs are buffered (NE5532), and those go through 8K2.
- The pots are fed from buffered pre or post sources (e.g. IC15-B "prefade buffer").
- PRE and ON keys per send. Jumper blocks pick the pre source (pre-EQ or post-mute) in four groups.
- **vs ours:** similar. Our 22K buses run at a lower noise gain than their 10K ones.

**T11 Routing (read, p82 and p86).**
- 10K per leg (2 % MF, AR1673), feeding the + and − lines of each bus.
- ALPS SUJ 4-pole keys switch each resistor's bus end between the bus and ground. The keys carry audio.
- **vs ours:** same "off = bus end to ground" principle. We switch logic only, through the DG413s.

**T12 Mix-bus summing (read, p107 and p101).**
- **Every mix, mono and group bus is a differential pair:** L+/L−, R+/R−, M±, GP1–8±. The 64-way bus pinout (p87) confirms this.
- **Master front end:**
  - two 2SB737 PNPs in grounded-base form;
  - emitters biased by 22K from a filtered +17 V (1K + 47 µF);
  - the bus legs enter the emitters through **220 µF / 6.3 V**;
  - collectors into 10K loads to a filtered −17 V;
  - a TL072 takes the difference of the collector voltages;
  - feedback is 10K to the − leg's emitter, and 10K via a unity inverter (TL072, 4K7 / 4K7) to the + leg's emitter.
- So both legs are virtual earths, 10K in and 10K feedback; there is 68 pF between the collectors and 100 pF across the feedback.
- The group module uses the same amp (p101; 8K2 feedback on the odd half).
- **vs ours:** different. Ours is a single-ended 4K7 bus into an OPA1612 summer referenced to GCANCEL, then a re-inverter.

**T13 Ground cancel / bus ground (read, p86, p87, p101, p113).**
- **Mix and groups:** no ground-cancel line. The balanced bus pair rejects any ground difference as common mode.
- **Aux:** the aux pots' local ground goes through **10R** (R190, R203) to GND CANCEL 1 (aux 1–6) and GND CANCEL 2 (aux 7–12). At the aux master, the reference transistor's emitter takes the GC line (jumper J33; R55 0R or R56 47R + 100n).
- **PFL / AFL:** the "−" line is an undriven parallel "crosstalk cancellation track". The master puts it through its own virtual-earth amp (NE5532, 22K / 22K) and subtracts it from PFL+ (22K feedback).
- **Grounds:** each module has a ground spade to audio GND, chassis via 10R (R202), and DGND on separate bus pins.
- **vs ours:** our GC scheme is the same as their aux scheme. For mix and groups they use the stronger balanced bus.

**T14 AC coupling (read).**
- 1000 µF / 6.3 V after the pan buffers on the strip, 220 µF / 6.3 V at the master inputs, 47–100 µF electrolytics between stages.
- No film and no bipolar caps.
- **vs ours:** different. Ours (100 µF NP + 47K, film couplers) is more careful.

**T15 PFL / solo (read, p87, p113–115, p133).**
- **Strip:** 22K, then a series J111 and a shunt J111, onto PFL+ (AFL L/R likewise).
- **Detection:** solo detect is a DC line. There is an electronic latch on the fader card, and LM2901 / 4053 logic on Master 2 for SIP, auto-cancel and input priority.
- **Monitor switching:** J112 series / shunt pairs (10K) into TL072 virtual-earth stages.
- **Dim:** a J112 shunt with 4K7 / 470R.
- **Phones amp:** TL072 plus an MJE340/350 output stage, 33R out.
- **vs ours:** similar function. Their switching is JFET; ours is a DG413.

**T16 Direct out (read, p82).**
- Aux 12 doubles as the direct-out level (DIR key); otherwise the direct out is post-fader.
- The driver is a cross-coupled TL072 pair (4K7 / 10K, 33 pF) with 75R + 47 µF per leg; +4 dBu nominal, +26 max.
- **vs ours:** same idea (the aux pot doubles as level). Ours is impedance-balanced, theirs actively balanced.

**T17 Master outputs (read, p107, p101).**
- The signal path is the bus amp at −2 dB, then:
  - SSM2142 insert send and MC33078 receiver return (10K / 4K7);
  - the fader and post-amp;
  - a J112 series + shunt mute inside a 10K / 10K virtual-earth stage, the gates fed through 1M with 22 nF;
  - an NE5532 at +1.7 dB;
  - an **SSM2142** line driver with 220 µF / 6.3 V and 100K per leg, and a transformer option header.
- No output relay or power-on mute is shown.
- **vs ours:** different. Ours uses DRV135 drivers and G6K relays with a power-on delay, which is more protective.

**T18 Meters (read, p87, p132).**
- **Strip meter:** a TL072 precision half-wave peak rectifier with a 1 µF hold drives an LM2901 ladder. The LEDs are one series string fed from a PNP (2SA970) current source, and each comparator shorts its LED. Steps are −30…+14 dB plus a red peak at +18 dB, with 0 dB = −2 dBu.
- **Peak LED:** a "multi-point bipolar peak detector": diode-OR of the input amp, EQ out and post-fader, a TL072 comparator, and 2.2 µF / 560K hold (~1 s).
- **Master:** VU meters with peak LEDs 3 dB below clip (spec).
- **vs ours:** the LED string is the same as our master meters. Their peak LED watches three points; ours watches one.

**T19 Power (read, p168–169, p87, p116).**
- **CPS2000 PSU, linear, per rail:** LM723 with an LM385 reference, an MJL3281A driver and 4 × MJ15024 in parallel with 2 W emitter resistors. It runs from a ~26 V reservoir plus a +38 V "high rail" for the driver.
- **Protection and monitoring:** a 50 A Schottky in series with the output (inferred: OR-ing for a backup PSU), overcurrent limiting, mutual shutdown of both rails via an opto, LM35 over-temperature shutdown, a fan, a "headroom" (dropout) alarm and a current DPM.
- **Other supplies:** +48 V and +8 V lamp rails (LM317). The connector is a 19-way Socapex with 4 pins per rail. No SCR crowbar is shown.
- **Module side:** six sub-rails (±17 V audio, ±17 V EQ, ±17 VL logic), each through its own **10R fusible resistor** with 47 µF (10 µF on logic). Master phones get their own rails via 2 × 75R and 1000 µF.
- **vs ours:** similar. We have the crowbar they lack; they split the analogue rail into two filtered sub-rails per strip.

**T20 Op-amps / stability (read).**
- TL072 in most stages (filters, EQ, mute, fader drive), NE5532 for the receiver and post-amps.
- MC33078 receivers, SSM2142 balanced drivers, a discrete 2SB737 bus front end, LM2901 comparators.
- 33 pF across the feedback of nearly every stage.
- **vs ours:** our parts are better (OPA1612 / OPA1656); the stability practice is the same.

**T21 Levels / headroom / noise (spec).**
- −2 dBu internal and about 23 dB headroom on ±17 V; +4 dBu out, +26 max.
- Bus noise < −78 dBu at N = 32 with input faders at −∞.
- **vs ours:** comparable. Our sim gives mix-bus noise −100.4 dBu (24 channels) with the bus alone, and −79 dBu with 24 strips at the main output, which includes strip noise. Their −78 dBu sits 82 dB under +4 dBu.

**T22 Construction (read, p150, p184).**
- Each channel is two stacked PCBs (LH / RH) plus a fader card on a 16-way IDC, with 4-channel rear-connector boards.
- 64-way IDC ribbon looms run per channel block (CH1–14, 15–24, 25–40, 41–48) to a distribution board, which carries the console-link summing resistors (10K / 22K / 8K2).
- **vs ours:** same ribbon-motherloom concept.

**Topics not covered or not read:** none fully missing. Partial: the mute ramp RC (T7) is not legible, and the master VU meter circuit (T18 master side) was not read.

## 4. Worth considering for goa-console
1. **Dummy return track on PFL / AFL, subtracted at the master.**
   - The PFL bus is a switched, high-impedance line; a parallel undriven track picks up the same capacitive and ground interference and cancels it.
   - Cost: one op-amp half and two 22K resistors at the master PFL summer.
   - It fits: Delta pin 28 is "PFL Audio −VE", and we leave it unused.
   - This is the cheapest idea here and suits our ribbon.
2. **Multi-point peak detect for the OL LED.**
   - Diode-OR the receiver output, EQ out and post-fader into the overload comparator, so internal clipping from EQ boost or a hot post-amp shows even when the input is fine.
   - Cost: about 4–6 BAS16-type diodes per strip.
   - It suits synths, which often run hot with EQ boost.
3. **Split analogue sub-rails with fusible 10R per strip.**
   - EQ and the rest of the audio each get their own 10R + 47 µF, using flameproof / fusible resistors so a shorted strip opens its own feed instead of loading the console rail.
   - Cost: cents.
   - Worth checking whether our 10 Ω feeds are fusible types.
4. **Balanced (differential) mix / group bus.**
   - It is technically the strongest ground-rejection scheme, removes the GCANCEL dependence and gives about 3 dB better SNR in principle.
   - Cost: double the bus conductors, two inverters per strip output, and a differential summer at the master.
   - It does not fit our 34-way Delta pinout. Our GCANCEL plus re-inverter already simulates −93 dBu ground residue. **Not recommended** unless the bus is redesigned.
5. **Series JFET in the mute stage's virtual earth (series + shunt).**
   - About 100 dB of mute against our ~86 dB.
   - Cost: one J112 and a stage restructure.
   - Marginal for a synth console; optional.

**Where ours already does better:** the line input. Theirs is 2 kΩ with 60 dB CMRR measured with a 0 Ω source; ours has high-impedance followers. Our insert, bus caps and output muting (NP and film caps, relays, crowbar) are also more careful.

**Only relevant elsewhere:**
- The discrete 2SB737 bus front end is a 1990s answer to TL072 / 5532 noise; OPA1612 makes it unnecessary.
- The VCA bypass, MIDI mute scenes, LCR pan and the transformer options matter only for theatre or live work.

Renders and crops are in a scratch folder outside the repo (not kept).
