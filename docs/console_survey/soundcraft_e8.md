# soundcraft_e8: Soundcraft (Spirit) E series (E8), compared with goa-console

## 1. Header
**Document read:** `~/Downloads/672971245-Soundcraft-e8-Mixer-Sch.pdf`, 12 pages, "Spirit E Series Technical Manual"
p.1.14-1.25. Every page is drawing S-S2001AS-02A "E8 MIXER" (issue 2A, ECN 20/10/02). The drawings are vector, so the
values are legible at 400 dpi. The text layer holds only the page footers.
- p.1.14-1.21: mono input channels 1-8, one sheet each. At overview they are identical, and p.1.14 was read in detail.
- p.1.22-1.23: stereo inputs (p.1.22 read).
- p.1.24: master: aux 1/2 masters and outputs, PFL/monitor switching, mix L/R summing, master insert and faders,
  monitor and phones outputs, playback / record, mix XLR outputs.
- p.1.25: L/R LED meters, the SOLOVOLT / PEAKCOM references, power entry (CN9), phantom switch.

**Missing:**
- There is no specification page, block diagram, circuit description or PSU schematic (the PSU is external).
- There are no groups, direct outs, routing, polarity or HPF: the E8 doesn't have them.
- The E8 is a single-PCB console. Parts "enclosed by dotted line" sit on a "top break-off section" (the connector strip)
  that is joined to the main board by wire links (LKnnn).

## 2. Published specs
None in this document. The only levels are the drawing's annotations, given for "mic input at minimum gain, channel
fader at '0dB', pan and EQ at centre". The test input level isn't stated. The annotations are:

| Point | Level |
|---|---|
| Channel after the preamp, EQ out, post-fader | +4.7 dB |
| Pan wipers (MIXL / MIXR) | +1.7 dB |
| Aux buses | +4.7 dB |
| Aux outputs | +10.7 dBu |
| Monitor amp | 4.5 dB |
| Master out | +4.63 dB |
| Record out | −1.37 dB |

The meter is marked "0 = 0dBu" (p.1.25). The rails are ±15 V (p.1.24-1.25). **Inferred:** the internal working level
is about +4 dBu on ±15 V TL07x / NE5532. That is roughly 15 dB below clip, against our 0 dBu with 23 dB on ±17 V.

## 3. Topics

**T1 Line input receiver**
- **Mono channel** (p.1.14, **read**):
  - There is no separate line receiver. The LINE TRS (CN501) feeds the discrete mic preamp through 4K3 per leg
    (R511 ring, R512 tip), straight onto the bases of the input pair (2SB737 TR500/TR501, after the 47 µF/63 V mic
    couplers). Each base has 1K2 to ground (R509/R510).
  - The gain pot is P500-A, a 10K A-log rheostat with 10R in series and 3300 µF in the emitter leg. The second gang,
    P500-B, is unused.
  - The pair's two outputs (LK500 / LK501) go into IC500-A, a TL074 (6K8 / 6K8, 22 pF / 22 pF).
  - The preamp collector loads hang off +V2, which is CN9's +PH (phantom) rail (**inferred:** a high-voltage rail for
    headroom).
  - **Inferred:** the line pad is about −12 dB (4K3 into 1K2), with about 5.5 kΩ per leg. CMRR depends on 4K3
    matching, and the tolerance isn't given.
- **Stereo input** (p.1.22, **read**):
  - A TL072 differential amp per side. Each leg has 3K3, then 680 pF to ground, then 47K (≈71 kHz RF pole).
  - The + leg has 15K to ground. The feedback is 15K into a T-network: GAIN P1305 20K lin, 1K5, then 620R +
    100 µF to ground.
  - The R jack is normalled from L.
  - **Inferred:** the T-network varies only the inverting gain, so the legs are balanced at one gain setting only.
- **vs ours:** different. Ours is a dedicated buffered receiver (1M legs, OPA1656 followers, 0.1 % diff amp, CMRR 54 dB
  against 1K). Their mono line in is a pad into a mic pair, and their stereo receiver has CMRR that varies with gain.

**T2 Line gain** (**read**)
- Mono channel: the mic preamp's gain pot does the job, with no separate stage and no centre detent.
- Stereo input: the T-network pot inside the receiver.
- **vs ours:** different. Ours is a separate inverting stage with a 0 dB detent, and the receiver stays at unity.

**T5 EQ** (p.1.14, **read**; mid-tuning detail skipped)
- **Mono channel:** HF/LF Baxandall shelving in one TL074 (IC500-C):
  - 20K lin pots, 3K3 / 3K3 in and out;
  - LF 68 nF across the pot, 47K to the − input;
  - HF 2 × 2N2 with 20K / 47K.
- **Swept mid** in IC500-D:
  - 20K / 20K inverting stage;
  - MF boost/cut on a 20K lin pot, wiper into 10 nF and 8K2;
  - FREQ is a 200K A-log dual rheostat with 8K2 per gang, 3N3 on the + input.
- There is no EQ in/out switch and no HPF.
- The stereo input has HF/LF only.
- **vs ours:** ours has 4 bands with two KHN mids, a sweepable HPF and EQ IN.

**T6 Insert** (p.1.14, p.1.24, **read**)
- **Mono channel:** the insert is after the preamp and before the EQ.
  - Send: tip, from IC500-A's output through 75R (R536).
  - Return: ring, through 10 µF/16 V (C515, polarised) straight into the EQ's inputs (20K into IC500-D and 3K3 into the
    Baxandall), with no buffer.
  - Normalled by the jack's switch contacts (T/ST/SR tied).
- **Mix L/R inserts:** after the summing amp and before the master fader. The return goes through 10 µF/16 V into the
  fader top.
- **Inferred:** the channel return is loaded by about 3-4 kΩ.
- **vs ours:** ours is post-EQ (with a pre-EQ jumper). Our return goes through 33 µF + 47K + 1K + 100 pF into a
  follower, so its load is high and defined.

**T7 Mute** (p.1.14, **read**)
- The MUTE key, SW500 (DPDT), sits after the EQ's output cap (C512 33 µF/16 V).
- Unmuted, both poles join the EQ out to the node that feeds the fader and the pre-fade aux gangs (two contacts in
  parallel).
- Muted, pole A grounds that node and pole B parks C512 on 47K (R538) to ground.
- It is a hard mechanical mute. It mutes the pre sends. PFL is taken before it.
- **vs ours:** same scope (pre sends muted). Ours is a J112 soft mute (≈86 dB, 20 ms ramp) driven by a logic-only key.

**T8 Fader** (p.1.14, **read**)
- The fader is a 10K part (P505), with 20K from the wiper to ground (R523).
- After it comes a TL074 non-inverting post-amp, 1 + 10K/4K3 = +10.5 dB (R524 / R525). R525 goes straight to ground
  with no cap, so the DC gain is 3.3.
- The mix master is the same scheme: a 10K dual fader, 20K load, and an NE5532 at 1 + 3K3/8K2 = +2.9 dB.
- **vs ours:** same idea (+10 dB post-amp). Ours loads the wiper with 100K, so the fader law is distorted far less than
  by their 20K.

**T9 Pan** (p.1.14, **read**)
- The pan is a dual 10K pot of a special "PAN" taper, wired as two dividers off the post-amp output (one gang
  ground-to-output, the other output-to-ground).
- Each wiper goes straight into a 10K bus resistor (R530 / R531), unbuffered.
- The annotation shows −3 dB at centre (+4.7 → +1.7 dB).
- The stereo input uses one gang per side as BALANCE.
- **vs ours:** different. Ours is linear (−6 dB at centre) and buffered before the routing resistors. Theirs gives a
  source impedance of 10-12.5 kΩ that varies with pan position.

**T10 Aux sends** (p.1.14, p.1.24, **read**)
- There are 2 auxes, each a dual-gang 20K pot ("20KK", taper not stated).
  - Gang A is fed from the post-mute, pre-fade node into an AUXnPRE bus through 10K.
  - Gang B is fed from the post-fader amp into an AUXnPOST bus through 10K.
- Pre/post is chosen once per aux on the master (SW1 / SW2, both poles in parallel). The bus not chosen is left open.
- **vs ours:** ours has 6 auxes with 22K into one bus per aux and a per-strip PRE key per pair. They spend a pot gang
  and a bus to save the per-channel switch.

**T12 Mix bus summing** (p.1.24, **read**)
- MIXL / MIXR go straight (DC) into NE5532 virtual earths (IC1-B / IC3-B), 10K ‖ 22 pF feedback, + input to local
  ground.
- Each channel's 10K therefore sums at unity.
- Playback is switched onto the mix ("PB TO MIX", SW5) through 6K8 (R55 / R56).
- **Inferred:** the noise gain is about 12-13 (8 mono + 2 stereo sources plus 6K8).
- **vs ours:** same topology. Ours uses 4K7 / 4K7 on OPA1612, which is quieter.

**T13 Bus ground** (**read**)
- The summing amps' + inputs go to the board's ground. With a single PCB there's no motherloom and no ground cancel.
- **vs ours:** ours needs ground cancel because the modules sit on a ribbon. On a single board it has no counterpart.

**T14 Bus AC coupling** (**read**)
- **Channel:** one 33 µF/16 V polarised cap after the EQ (C512). Everything after it is DC coupled: the fader post-amp
  (DC gain 3.3), the pan pots, the 10K bus resistors and the mix summing amp.
- **Aux and solo summing amps:** a 33 µF/16 V cap in series between the bus and the virtual earth (C7 / C8 / C23 /
  C29). One cap per bus blocks every source's DC and keeps the DC noise gain at 1.
- **Elsewhere:** 10 µF on insert returns and playback.
- **vs ours:** different. Ours puts 100 µF NP + 47K at every node feeding the bus and film couplers at the wipers, with
  no polarised caps in the path.

**T15 PFL / solo** (p.1.14, p.1.24-1.25, **read**)
- **Audio:**
  - The SOLO key's pole B takes the signal before the mute (after C512) through 4K3 (R532) onto SOLOBUS. When off,
    it grounds the resistor's switch end.
  - On the master, SOLOBUS goes through 1K0 into a 74HC4053 switch (IC5).
  - The switch output goes through 33 µF into the virtual earth of a TL072 (20K ‖ 22 pF) that drives MONL / MONR.
  - The same mux selects the monitor source when solo is off. That source is a 10K / 20K-into-1K5 network from mix or
    playback.
  - Every mux pin therefore sits near 0 V: either a low-impedance divider node or an input to a virtual earth.
- **Detect:**
  - Pole A shorts SOLOVOLT (+15 V through 3K3, R80) to SOLOCOM. SOLOCOM has 4K3 to ground, 100 nF and the SOLO LED
    (620R).
  - SOLOCOM drives the mux select pins.
- **Mux supply:**
  - The 74HC4053 runs from a divider: +15 → 3K9 → VDD → 3K3 → VEE → 6K8 → −15. VSS goes to ground.
  - **Inferred:** VDD ≈ +6.6 V and VEE ≈ −0.4 V. SOLOCOM (≈8.5 V) is above VDD and is limited by the 3K3, so the
    select inputs are clamped.
- **vs ours:** same concept: pre-mute PFL bus, a DC detect line, and auto-switching at a near-virtual-earth node. Ours
  uses a DG413 on proper rails, a debounce, a clamp against back-feed and a rude-solo flasher. Theirs is a bare
  contact closure with no per-channel LED on the line.

**T17 Master outputs** (p.1.24, **read**)
- **Mix XLRs:** impedance balanced. Pin 2 is fed through 75R, pin 3 through 75R to ground, and pin 1 and the
  connector's CHAS tag go to the board's signal ground.
- **Other outputs:**
  - Record out: 1K2 / 1K2 (−6 dB) to RCA.
  - Monitor outs: NE5532 inverting 20K / 8K2 (+7.7 dB), 75R / 75R TRS.
  - Aux outs: NE5532, fixed +6 dB (20K / 10K, no aux master pot), 75R / 75R TRS.
  - Phones: per side an inverting NE5532 (20K / 8K2) and a follower, with both outputs paralleled through 75R each.
- There is no mute relay and no power-on mute.
- **vs ours:** ours has DRV135 active-balanced outputs, the shield on CHASSIS and G6K relays with a 2.8 s power-on delay.

**T18 Meters** (p.1.25, p.1.14, **read**)
- **Master L/R:**
  - The meters read MONL / MONR, so they follow PFL.
  - Detector: a TL072 precision rectifier (negative-going) with BAV70.
  - Bar: 330R / 100 nF attack (33 µs) and 1M decay (≈0.1 s).
  - A separate +16 LED holds on 10 µF / 220K (≈2.2 s).
  - Display: 10 LEDs (−24 … +10) in a series string from a BC856 current source (240R, base referenced to the power
    LED), with an LM2901 output at each string node.
  - Thresholds: a ladder from ground to −15 V (75, 75, 130, 330, 240, 330, 470, 620, 1K5, 3K9, then 9K1).
  - **Inferred:** the ladder gives taps at −24.3 / −18.3 / −12.8 / −6.1 / −3.2 / −0.3 / +2.6 / +5.4 / +9.8 / +15.9 dBu
    peak-of-sine, so the scale is peak-reading and calibrated in dBu.
- **Channel PEAK LED:**
  - Four taps through two BAV70s (anodes at the taps, so positive peaks only): preamp out / insert send, insert return,
    EQ out, and the post-fader amp.
  - The taps feed 4K3 → 4.7 µF/50 V → the base of a BC846, with the LED (620R) from +15 V in the collector.
  - The emitter goes to PEAKCOM, which is two BZX84C3V9 zeners to DGND, shared by every channel.
  - R537 (the base bleeder) is not fitted.
  - **Inferred:** the threshold is about 7.8 + 0.6 + 0.6 ≈ 9 V peak (≈+18 dBu sine), about 1.5 dB below TL074 clip on
    ±15 V. The 4K3 / 4.7 µF integrates (slow attack) and the hold is set by base current.
  - The stereo input taps EQ out L/R and post-fader L/R.
- **vs ours:** the master meter is the same architecture. Our v5.0 strip OL LED also takes several taps, but both
  polarities, with a comparator, 0.1 ms attack and a defined ~150 ms hold.

**T19 Power** (p.1.25, **read**)
- **Entry:** external PSU into a 5-pin CN9: −VA, GND, GND, +VA, +PH.
- **Rails:** ±15 V with 100 nF at entry and 100 nF per op-amp pair.
- **Phantom:** SW4 switches +PH onto SWPHANT; when off, the line is grounded and a 10 µF/63 V cap sits on it.
- **Logic ground:** DGND carries the meter, PEAKCOM and LED returns. It joins GND only through link LK22 (single point).
- **vs ours:** same separate-logic-ground idea (our NT1). Ours runs ±17 V with per-module filtering and a heavy ground
  harness.

**T20 Op-amps / stability** (**read**)
- Channels: TL074 / TL072 throughout.
- Summing, aux, monitor, phones and outputs: NE5532.
- Meters and logic: LM2901.
- 22 pF across every summing and aux feedback and across the preamp diff stage. 75R build-outs on outputs and insert
  sends only.
- **vs ours:** ours uses OPA1612 / OPA1656, C0G stability caps at the inputs and build-outs at every pin.

**T21 Levels / headroom** (**inferred** from the annotations)
- About +4.7 dBu at the channel and pan −3 dB, on ±15 V. That gives about 15 dB to TL07x clip and about 1.5 dB from
  the peak LED to clip.
- **vs ours:** ours runs 0 dBu with 23 dB of swing.

**T22 Construction** (**read**)
- One PCB carries all 8 mono channels, the 2 stereo inputs and the master.
- Pots and switches are PCB-mounted. The jacks and XLRs sit on a break-off strip of the same panel, linked by wire
  links.
- **vs ours:** our separate jack board on a ribbon is the same idea at module scale.

**Not shown in the document:** T3 polarity, T4 HPF, T11 routing, T16 direct out, the PSU circuit and every published
spec.

## 4. Worth considering for goa-console
1. **One coupling cap at each summing amp's input** (33 µF in series with the virtual earth on aux and solo).
   - It blocks every source's DC with one part and holds the DC noise gain at 1.
   - We already block DC at each source (needed so the DG413 routing and keys don't click) and use NP / film, so it
     adds nothing to the strip.
   - It could stand as cheap insurance on our master aux / PFL summers against one faulty strip putting DC on a bus.
     The cost is one NP cap per summer, but it adds an LF pole and a series element at the most sensitive node.
   - Low priority.
2. **Global aux pre/post on the master, using dual-gang pots and PRE + POST buses.**
   - It saves per-channel switches, but costs a gang per aux and a second bus conductor per aux.
   - Our Delta motherloom has no spare pins for six more buses, and our per-pair PRE key is more flexible.
   - Not for us.
3. **A shared zener reference for the channel peak LEDs (PEAKCOM): one transistor per channel, no comparator.**
   - It is cheap, but the threshold drifts with zener tolerance and Vbe, it sees positive peaks only, and the hold is
     undefined.
   - Our v5.0 LM393 detector is better on every count. This only confirms that multi-tap overload sensing is ordinary
     practice even on a budget desk.
4. **Mute with both key poles in parallel for the signal, and the coupling cap parked on 47K when muted.**
   - The 47K park is a cheap click reducer for a hard mute.
   - We use a JFET soft mute with logic-only keys, so it doesn't apply.

Where ours looks weaker than this console: nowhere found.
- Their only advantages are cost and simplicity (single board, no ribbon, so no ground cancel needed).
- Every stage we share with them we build at higher load impedances: fader wiper 100K vs 20K, a buffered insert return
  vs an unbuffered one into ~3 kΩ, and a buffered pan vs an unbuffered one.
- We also have more headroom (23 vs ~15 dB) and quieter parts.
