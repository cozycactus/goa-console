# Yamaha MC803 / MC1203 / MC1603 / MC2403 survey (label: yamaha_mc)

## 1. Header
**Document:** `545496244-yamaha-mc803-mc1203-mc1603-mc2403-mixer-service-manual-1.pdf`. It has 40 pages, scanned at 300 dpi; the schematic pages are at 600 dpi. All page numbers below are PDF pages; the printed page numbers differ.

**Pages read:**
- specifications, p.3 (printed 2-3);
- panel and control descriptions with the channel block diagram, p.6 (printed 8-9);
- rear panel, p.7;
- circuit-board wiring, p.10 (printed 16-17);
- inspection and adjustment, p.23-26 (printed 34-37);
- the overall circuit diagram on four sheets, p.32-35, with the parts notes on p.33 and p.35.

**Not read:** the disassembly pages, the PCB artwork (p.17-20) and the separate parts list (p.36-40).

**What the console is:** a 1993 compact one-piece mic mixer with no subgroups. The title block on p.35 reads "PHONIC CO., LTD., MC03-SERIES, January 18, 1993", so it is an OEM design.

**Signal flow:** 8 / 12 / 16 / 24 mono mic/line channels feed a stereo bus, 3 aux buses and a cue bus. There are no subgroups and no routing switches. "MIX" is a mono output derived from L+R through a MIX BAL pot. There are two aux returns, ST / AUX sub-ins and talkback.

**Family differences:** one schematic covers all four models.
- Channel count, width (506 / 642 / 778 / 1050 mm), weight (12.5-24.5 kg) and power (40 / 45 / 50 / 60 W) differ (p.3).
- The reservoir caps are 2200 µF / 35 V × 4. A note gives 3300 µF / 35 V × 4 for the largest model; it prints as "MC2402II", which is probably a misprint.
- The T12 input-jack cable differs for CH17-24.
- Fuses differ by region.

**Missing:** the input-jack board (MC03-K) and fader board (MC03-H) are only partly drawn. There is no mix-noise figure with N channels routed and no CMRR figure. Some labels are duplicated or illegible (noted below).

## 2. Published specs (p.3, p.25-26)
**Levels:**
- 0 dB = 0.775 V. Nominal setting: all faders at −10 dB, all level controls at −6 dB.
- ST OUT / MIX OUT XLR: +4 dBu rated, +24 dBu max, 150 Ω.
- Parallel unbalanced "−6 dB" jacks: −6 dBu rated, +14 dBu max, 600 Ω.
- Aux sends: +4 dBu, +20 dBu max, 100 Ω.
- Channel insert: 0 dBu, +20 dBu max, 600 Ω out, 10 kΩ in.
- Sub-ins: +4 dBu, 10 kΩ.

**Channel input:**
- LO-Z 4 kΩ, HI-Z 10 kΩ (balanced TRS).
- Pad off: sensitivity −80 to −40 dBu. Pad on (20 dB): −20 dBu sensitivity at max gain, rated 0 dBu, max +24 dBu.

**Response and distortion:** 20 Hz-20 kHz +1/−3 dB; THD < 0.1 % at +4 dBu / 600 Ω.

**Noise** (20 Hz-20 kHz, Rs 150 Ω, −6 dB/oct LPF at 12.7 kHz; p.26 says DIN-audio average):
- EIN −128 dBu.
- Residual −96 dBu (ST / MIX), −91 dBu (aux).
- ST OUT −88 dBu with the master at nominal and every channel ON off.
- −64 dBu with one channel at nominal (mic gain).
- Aux −78 / −64 dBu.
- With ON off the channel's 27K stays on the bus with its source end open, so −88 dBu is essentially bus-amp plus master noise, not "N routed".

**Crosstalk:** −70 dB at 1 kHz, adjacent channels and pan.

**Rails:** ±15 V (7815 / 7915), +48 V phantom (6K8 per leg).

**Peak LED:** "post-EQ, 3 dB below clip". In the test procedure it starts blinking at −43 ± 2 dBu input at max gain, i.e. about +17 dBu at the tap (**inferred** from about 60 dB of gain). Meter peak LEDs light at +14 ± 3 dBu.

## 3. Topics

**T1 Line input receiver** (p.32, **read**):
- There is no separate line receiver. XLR and HI-Z TRS both enter the mic preamp. Each leg sees a 20 dB pad on SW101: a 4K7 / 1K1 / 4K7 ladder (R104-R106), with C102 22/50 and R107 100K, then 10 Ω + 470 pF RF filters.
- The preamp is a discrete 2SA970 PNP pair (Q101 / Q102) with 4K3 collector loads, plus IC101A NJM4558 (R119 / R120 16K).
- Gain is VR101 20K C-law plus R112 12 Ω between the emitters (R157 68K across), with C104 470 µF. The resistors in this stage are metal film (marked **).
- A line source uses the pad plus the preamp's minimum gain of about 20 dB.
- **vs ours:** different. They use a mic pre with a pad; we use followers plus a 0.1 % diff amp. Their CMRR is not specified. Ours is the cleaner line path.

**T2 Line gain:** VR101, 40 dB range, plus the 20 dB pad (**read**). **vs ours:** ±15 dB in a separate stage. Theirs has no centre detent.

**T4 HPF:** none (the panel on p.6 has no HPF).

**T5 EQ** (p.32, **read**): 3 bands, ±15 dB.
- LF / HF shelves are a Baxandall in the feedback of one 4558 half:
  - LF: 100 Hz, VR102 50KB, C114 / C115 33 nF, R125 33K, R123 / R126 10K, R124 4K7.
  - HF: 10 kHz, VR103 50KB, C116 1.2 nF, R127 5K6.
- That stage's label prints as "IC102B", the same as the post-fader amp. The parts list gives only IC101 / IC102 per channel, so it must be IC101B (**inferred**).
- The swept mid (350 Hz-5 kHz) is on IC102A with R130 / R131 10K, VR105 50KB gain and VR104 C100K dual tuning C121 2.7 nF / C122 6.8 nF with R128 / R129 6K8. Q is fixed. This is the C-law dual that `eq_survey.md` notes.
- There is no EQ IN switch.
- **vs ours:** fewer bands, no in/out switch.

**T6 Insert** (p.32, p.6, **read**):
- TRS jack, tip = send, ring = return, normalled. Send through a 560 Ω build-out (its label reads "R110", which duplicates the preamp's R110 10 Ω). Return 10 kΩ, nominal 0 dBu.
- Solder jumpers JP3 / JP6-JP9 / JP20 / JP21 put the insert pre-EQ or post-EQ. The block diagram shows both positions.
- **vs ours:** same idea (pre / post by jumper). We use 75 Ω and a buffered return.

**T7 Mute** (p.32, **read**): CH ON SW103 is a 4-pole mechanical push switch in the audio path. It breaks:
- the fader wiper into the post-amp;
- both pan outputs ahead of the 27K summing resistors;
- the pre-fader aux feed (C128 22 µF / R155 470K).

CUE is independent of ON. **vs ours:** same scope (ON also mutes the pre sends), but theirs uses raw contacts with no ramp. Our J112 soft mute is better.

**T8 Fader** (**read**):
- VR110 is a 10K A slide. Its wiper goes through R139 1K into IC102B, non-inverting, gain 1 + 10K/4K7 = +9.9 dB (R151 10K, R149 4K7, C132 56 pF, C131 56 pF at the input, R150 47K).
- Then C129 22 µF / 16 V and R156 100K.
- The nominal fader position is −10 dB (p.3 spec, p.24 test procedure).
- **vs ours:** identical gain structure (+10 dB post-amp, fader "nominal" 10 dB down). Their fader scale prints 0 at the top and calls −10 the nominal mark.

**T9 Pan** (**read**): VR106 is a 25K "A-C" dual (one A-law, one C-law gang). It is driven from the post-amp coupling cap and feeds the 27K summing resistors directly, unbuffered, through the ON contacts. **vs ours:** we use a linear dual with buffers. Theirs loads a 25K pot with 27K, so level depends on pot position; the dual-law is the cheap route to a near-constant-power law.

**T10 Aux sends** (**read**):
- Aux 1-3 are VR107-VR109 25K A pots, wiper through 27K to the bus, bottom end to the bus GND line.
- A jumper per aux selects post-fader or pre. The schematic labels the pre jumper "PRE EQ"; the block diagram takes it after the ON switch.
- As shipped, aux 1 is pre and aux 2 / 3 are post (p.23).
- CUE goes through 47K (R148), pre-EQ or post-EQ by jumper.
- **vs ours:** same scheme (unbuffered pot into the summing R), 3 aux vs our 6.

**T11 Routing:** none. Every channel goes to ST L/R through the ON contacts only. **vs ours:** our DG413 bus-end switching has no counterpart.

**T12 Bus summing** (p.34-35, **read**):
- ST L / R: NJM4558 / NJM2068 inverting summers. The ST L summer prints as 4558DY; the parts list gives IC203 as NJM2068D, an inconsistency. Feedback is R241 / R301 33K with 47 pF.
- Each summer has C242 / C302 47 µF / 16 V in series between the bus and the inverting input, i.e. the bus is DC-blocked at the summing node, once per bus.
- Aux: IC403A-IC405A NJM2068, R432 30K, 47 pF, again with 47 µF at the input.
- Cue: IC502A NJM2068, R520 22K, C528 47 pF, with C510 22 µF.
- Summing resistors are 27K (ST, aux) and 47K (cue).
- **vs ours:** we use 4K7 / 4K7 with no series cap, and our coupling sits at each source. Their 27K is about 7.6 dB noisier in Johnson terms than 4K7, which is acceptable at a +4 dBu output level.

**T13 Bus ground** (p.32 / p.34, partly **read**):
- The bus carries B+, B−, GND, L, R, AUX1-3, CUE, L CUE and R CUE.
- Each channel's pan-pot ground, aux-pot bottoms and R156 return to the GND line.
- That same line is the ST summer's + input and its decoupling reference: the pin-3 line has a junction dot on the GND column (**read**).
- G1 / G2 are joined on each channel board by C133 10 nF.
- **vs ours:** it is a shared reference line but with no 10 Ω isolation and no differential re-inverter. That is the plain version of what our GCANCEL does properly.

**T14 Bus AC coupling** (**read**):
- One 22 µF electrolytic after each channel's post-amp (C129, R156 100K bleed). Pan and aux pots hang off that DC-free node.
- Pre-fader feed: C128 22 µF / R155 470K. EQ out: C125 22 µF.
- Bus: 47 µF at each summer input.
- **vs ours:** we have 100 µF NP + 47K at every bus-feeding node. They need fewer caps because nothing active sits between the coupling cap and the summing R.

**T15 PFL / solo** (**read** in part):
- Mono CUE bus (47K, CUE switch per channel) plus L / R CUE lines for the stereo and return cue.
- IC502A / B (NJM2068) sum CUE and M/CUE, mixed through 75K / 47K into the phones pot VR502 10K A dual.
- No auto-switching logic is visible: phones = cue mix (**inferred**). Cue phase is negative (p.26).
- **vs ours:** no detect line, no monitor switching.

**T16 Direct out:** none.

**T17 Master outputs** (p.34-35, **read**):
- Stereo master and output stage:
  - ST ON switch (SW301) after the summer.
  - R242 100 → C245 22 µF → R263 100K → master fader VR203 10K A.
  - Q201 2SC2878 mute shunt at the wiper (base via R233 100K from the MU line) → C246 10 µF → RC (R243 100 / R244 47K / C248 100 pF) → IC203B NJM2068, gain 1 + 4K7/4K7 = +6 dB → C250 47 µF NP.
- Balanced output: a discrete cross-coupled stage (the DRV134 topology) on NJM4556:
  - R247 / R248 / R252 / R253 10K, R249 / R254 36K, cross-coupling R251 / R256 39K, R261 430 Ω (all metal film);
  - R250 / R255 75 Ω build-outs, C255 / C256 220 µF NP outside the loop, R257 / R258 100K bleeds, 33 pF compensation.
  - An unbalanced "−6 dB" jack hangs off IC203B through R262 560 Ω.
- MIX (mono):
  - VR401 10K B MIX BAL across L/R → IC401A follower (NJM2068) → MIX fader VR402 → Q401 mute → IC401B (+6.4 dB, R406 4K7 / R407 4K3);
  - then the same cross-coupled output on IC402.
- Mute: Q607 2SA970 with D605 / D606, R611 / R612 47K, C615 10 µF, C616 100 µF and R613 470K drives the MU line, which holds the 2SC2878 shunts on at power-up and power-down. Spec: meters stay below −3 VU (p.26). The RC timing was not traced.
- **vs ours:** the topology matches our DRV135 (theirs is discrete). We use relays rather than transistor shunts; our relay mute is the stronger one.

**T18 Meters** (p.34, **read**):
- Four VU meters (aux 1/2/3 switchable, ST L, ST R, cue/mix).
- Meter amp: NJM4558 with VR302 50KB calibration trim, R321 56K, R322 33K, R323 130K, C324 10 µF → R325 470 Ω, then a 1N60P germanium rectifier with R801 / R802 1K2 and C801 10 µF into the movement.
- Meter peak LED: the other 4558 half used as a comparator → 1N4148 → C325 3.3 µF hold → 103HD LED, R813 3K9 to V−. It trips at +14 dBu.
- Channel peak LED (p.32):
  - Single tap at EQ out / fader top through C126 1 µF and R133 100K into Q103 2SC1815 (R134 10K), driving Q104 2SA1015 with C127 1 µF / R135 4K7 stretching (about 5 ms, **inferred**).
  - LED D101 through R138 3K9 between +15 and −15 V (about 7 mA).
  - It responds to the positive half only (**inferred** from the NPN input).
- **vs ours:** our strip OL (5 taps, both polarities, 150 ms hold) and master peak ladder are more complete.

**T19 Power** (p.33, **read**):
- Internal transformer → PBL405 bridge → 4 × 2200 µF / 35 V → UA7815 / UA7915 with 0.1 µF / 10 µF.
- Phantom: separate PBM205 bridge, 1000 µF / 80 V, discrete 48 V regulator (2SC2240 / 2SC4381, 12 V and 56 V zeners).
- Primary fuse 1 A / T500 mA; secondary 2 A / T1.6 A.
- Power enters at the master end (board F → E) and reaches every channel through 14-pin, 65 mm board-to-board jumpers (T11) that daisy-chain the bus through each board's copper (p.10). There is no heavy ground wire.
- Channel decoupling is 10 nF per op-amp only. There are no per-channel rail filters and no separate logic rails. Board C takes B± through 10 Ω fuse resistors (R361 / R362).
- **vs ours:** our external supply, per-strip 10 Ω + 220 µF filters and 14 AWG spade are much stronger. Their daisy chain is the same idea as our ribbon, but with segment jumpers.

**T20 Op-amps:** NJM4558DY (channel, meters, some summers), NJM2068D (summers, aux / master amps), NJM4556D (balanced outputs, phones). Stability parts are 47 pF / 56 pF / 33 pF / 100 pF; the output build-outs are 75 Ω balanced, 24 Ω on aux (R437) and 200 Ω ∥ 200 Ω on phones (**read**). **vs ours:** same practice, older parts.

**T21 Levels:**
- Internal level is about 0 dBu: insert 0 dBu nominal, +20 dBu max.
- ST output +4 dBu: the internal 0 dBu gets +6 dB in IC203B and the balanced stage gives a further +6 dB differentially (**inferred**).
- That is about 20 dB of headroom against our 23 dB.
- Noise: see section 2.

**T22 Construction:**
- One long PCB per channel (MC03-A) carrying its pots and switches, plus an input-jack board (MC03-K) and a fader board (MC03-H) on short cables.
- The bus runs on 14-pin jumpers from board to board into master boards B / C / D / E.
- Single chassis.
- **vs ours:** same "one board per channel + daisy-chained bus" concept.

**Not covered by the documents (feature absent):** T3 polarity, T4 HPF, T11 routing, T16 direct out.

## 4. Worth considering for goa-console
1. **A cheap pan law from mixed-taper duals (A + C gangs).** It gives a near-constant-power centre without extra parts. It's the wrong fit for us: our pan is buffered, and the ALPS RK09L detent part is linear only. The decision on −6 dB vs −3 dB at centre stays a law choice, not a parts choice. Not recommended.
2. **One DC block at each summer input (47 µF in series with the virtual-earth leg) instead of a cap per source.** It only works because their pan and aux pots feed the summing resistors straight from an AC-coupled node. Our pan followers and DG413 bus-end switching need the per-node caps (click-free switching), so keep ours. A series cap would also add LF crosstalk and phase shift at the bus. Not recommended.
3. **A parallel unbalanced "−6 dB" (−6 dBu nominal) output tap per main, through 560 Ω.** It costs a resistor and a jack per output and would suit a semi-pro recorder. Our DRV135 TRS already drives unbalanced loads, so this is low value. Optional only.
4. **Confirmation, not a change:** their gain structure matches ours exactly: fader nominal −10 dB, a +9.9 dB post-amp (10K / 4K7), pre/post aux by jumper, insert pre/post-EQ by jumper, and ON killing the pre sends.
5. **Where ours is clearly stronger, and nothing to borrow:**
   - line input: a real receiver vs a mic pre with a pad;
   - mute: JFET ramp vs raw ON contacts;
   - bus ground: GCANCEL + re-inverter vs a shared GND line;
   - power: an external PSU with a heavy ground vs ±15 V through 14-pin jumpers with 10 nF decoupling;
   - OL detection: 5 taps, both polarities, vs one positive-only tap;
   - output mute: relays vs 2SC2878 shunts.

   No point where ours is weaker than common practice turned up in this console.
