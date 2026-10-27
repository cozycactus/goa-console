# s2_venue: Soundcraft Series Two, Venue Theatre and Venue II

## 1. Header
Paths are relative to `Service Manuals/`. Page numbers are PDF pages.

- **Series Two (2000).**
  - `Tech Data/SERIES2D.PDF`: p6 architect's spec, p7 specs.
  - `Schematics/Series_2_Schematic_only.PDF` (vector, legible at 400 dpi):
    - p1-5 ED4019 "Mic Amp": 8 channels per PCB, holding the whole channel except the fader. p2 is mic amp + HPF; p4/5 are EQ, mute, aux, pan, routing.
    - p6-15 ED4020 Master: p6 power and GCOMP tie, p7 monitoring/PFL, p8 aux masters, p9 group summers, p10 mix summers + DRV135, p14/15 stereo inputs.
    - Other boards: p16 ED4021 input faders, p17 ED4022 meter board, p22 ED4026 output faders, p33 ED4041 PSU distribution.
  - `Documents/Series Two Crosstalk Mod.pdf`: all 4 pages read.
  - Tech manual (142 p): contents only. It repeats the schematics; the DCP200 PSU (ED3657) was not read.
- **Venue.** The `Soundcraft Venue` folder has user guides only, no technical data on an older "Venue":
  - `VenueTheatrezz2829.pdf`: Venue Theatre user guide. p16 block diagrams, p54 performance figures.
  - `Venue2zz2773.pdf`: Venue II user guide. Contents only.
- **Venue II / Theatre technical manual** `Venue2TheatreTMzz2774.pdf`:
  - p10 performance figures.
  - Circuit descriptions: p61 mono input, p65-67 Theatre input, p68-69 dual group, p74-78 master LH/RH.
  - Schematics: p90-93 Theatre input (ED3151, ED3152A/B/C), p94 dual group (ED2913A), p102 master RH (ED2919A).
- **Venue II vs Venue Theatre:** same frame, master and group modules, and identical spec pages. Venue II uses the Mono Input module; Venue Theatre adds the Theatre Input module (4 mute groups + SAFE, ON key, insert pre/post-EQ links, 8-segment meter). Both input modules have active pan, a +10 dB post-fader amp and a ground-compensated direct out (p61 / p66).

## 2. Published specs
**Series Two** (SERIES2D p7):
- **Levels and outputs:** internal 0 dBu (inserts 0 dBu nominal, +22 max). Outputs +4 nominal, +22 jacks / +26 XLR, 75 Ω.
- **Noise:** mix residual −88 dBu. Bus noise with 40 channels routed (faders down): −79 dBu mix, −80 dBu group.
- **Distortion and response:** THD <0.0065 % at +4 dBu. +0/−0.5 dB 20 Hz-20 kHz.
- **Crosstalk:** 90 dB for both mute and fader cut (1 kHz). No line CMRR figure.
- **Rails:** ±17 V and +48 V (read: ED4021, ED4041).

**Venue II / Theatre** (TM p10 = Theatre guide p54, measured on a 32-channel console):
- **Levels:** internal −2 dBu. Max out +26 dBu.
- **Noise:** line EIN −90 dBu (40 Ω). Mix bus −80 dBu (32 channels routed, faders down); typical mix out −73 dBu.
- **CMRR:** line >40 dB at unity, mic >80 dB.
- **Crosstalk (1 kHz):** mute >100 dB, fader >80, active pan >85, routing >95, aux >85.
- **THD at +20 dBu:** 0.003-0.02 %.

## 3. Topics

**T1 Line input**
- Series Two (read, p2): no separate line receiver. The jack and the XLR feed the same discrete mic amp:
  - 2SB737/BCW72 pair + OP275 difference stage, 2.2 µF couplers, 100K bias.
  - Low range +5…−40 dBu; Zin >10K.
- Venue (read, p91): jack → R1/R2 15K → TL072 difference amp IC2-A (4K7 in, 3K3 feedback/ground).
- vs ours: we are better. Their CMRR depends on 15K/4K7 resistor matching (>40 dB); ours has followers + a 0.1 % stage, 54 dB against a 1K source.

**T2 Gain**
- Series Two: the mic-amp gain pot (10K across the emitters) plus a range switch.
- Venue (read): VR1-B 5K RD in the feedback path through buffer IC2-B; −12…+18 dB line.
- vs ours: different, single-stage. Ours is a separate inverting stage, ±15 dB with a detent.

**T3 Ø**
- Series Two (read, p2): SA1 swaps the legs ahead of the mic amp. Venue (read): swaps the inputs of IC2-A.
- vs ours: same.

**T4 HPF**
- Series Two (read, p2):
  - Sallen-Key high-pass on OP275: 2 × 33 nF, dual 100KE rheostats + 12K, gain 1 + 12K/18K (+4.4 dB), cancelled by a 2K2/3K6 input divider.
  - 40-400 Hz. SA3 picks filtered or unfiltered.
- Venue (read): fixed 2nd-order on TL072, +3 dB gain; switched in by un-shorting the caps.
- vs ours: KHN 21-403 Hz; theirs is cheaper but has no Q control.

**T5 EQ (skip mids)**
- Series Two: TL072, HF 12k / LF 60 Hz, ±15 dB; mids use 200KC dual rheostats, Q 1.3. Venue: TL072, mids 100KC.
- vs ours: same family.

**T6 Insert**
- Series Two (read): post-HPF, pre-EQ. Send 75R (RA28); return feeds the EQ; spec 10K return.
- Venue (read, p91/93): post-EQ, LK1-6 moves it pre-EQ. Send R143 75R; return through 47 µF + 4K7 into a TL072 inverter (4K7/4K7, 33 pF).
- vs ours: Venue is like ours (post-EQ, jumpers).

**T7 Mute**
- Series Two (read, p4):
  - Series J111 switches: a pair after the fader return (QA8/QA9) and one on the pre-fade bus after a TL072 follower (QA7), so pre-fade sends are muted too.
  - Gate from AMUTE through a BAV99, 68K to the source, 4M7 to +17 V, 1 µF / 22K ramp.
  - The latching key goes to the CPU (MIDI scenes, 4099 latches). Spec 90 dB.
- Venue (read p93, p66):
  - J112 shunt (TR3) + J112 series (TR4) into a TL072 virtual earth (4K7/4K7).
  - About 10 ms ramp (100 nF / 220K); 4 mute groups + SAFE. Spec >100 dB.
- vs ours: different. Ours is two shunt J112s (86 dB). Venue's series + shunt reaches >100 dB.

**T8 Fader**
- Series Two (read, p16): 10K log fader, TL072 non-inverting 4K7/2K2 (+9.9 dB) with 100 pF. Masters 4K7/3K (+8.2 dB); stereo inputs 5K1/2K2.
- Venue (read): NE5532 4K7/2K2 + 100 pF, 2.2 µF in, 100K load, 220 µF out.
- vs ours: same.

**T9 Pan**
- Series Two (read): passive dual pot straight into the 22K routing resistors, 47K load; mono is taken pre-pan via 22K. Mono-channel pan value not printed.
- Venue (read, p93): active pan. VR10 10KB dual, TL072 buffers 3K3/2K2 (+1.5 dB), law −4.5 dB at centre. With PAN off, the groups come from IC6-B at matched gain.
- vs ours: Venue is the same idea (ours −6 dB centre).

**T10 Aux**
- Series Two (read, p4):
  - 8 auxes. Source → 12K → pot wiper; the 20K track runs from clean ground to the aux bus, so the pot doubles as the summing resistor.
  - PRE per pair, plus a pre-EQ/post-EQ key.
- Venue (read): 6 auxes, 10KA pots, 22K into the bus, PRE per pair, jumpers for the pre source; aux 6 = direct level (DIR).
- vs ours: Venue is identical. Series Two's trick changes the source load and the bus noise gain with the pot; not recommended.

**T11 Routing**
- Series Two (read): 22K resistors; the latching key moves the bus end between bus and the local clean-ground line.
- Venue (read p90, p68): 10K 0.5 W resistors; bus end to bus or "CLEAN GROUND".
- vs ours: same principle. Ours switches with a DG413 instead of a mechanical key on audio.

**T12 Summing**
- Series Two (read, p9/p10):
  - NE5532 virtual earth with 330 µF in series at the summing junction (DC gain 1), Rf 12K // 100 pF, + input at GCOMP.
  - 22K sources (−5.3 dB), then a 12K/22K (+5.3 dB) inverter to unity.
  - Group bus has 100K to GCOMP. Aux masters: NE5532 with 6K8 / 100 pF, then the master pot, then a TL072 at 6K8/56K.
- Venue (read p94, p68): discrete common-base 2SB737 pair ahead of an NE5532 ("differential", better PSRR). Bus via 1000 µF; 8K2 feedback through an NE5532 unity inverter; −1.5 dB from a 10K source.
- vs ours: OPA1612 at 4K7/4K7.

**T13 Ground cancel**
- Series Two (read):
  - 10R (RA70) from each channel ground to the GCOMP line; GCOMP sits on bus header pin 14.
  - At the master, R207 10R ties GCOMP to AGND (p6).
  - Summers reference GCOMP; the next stage is referenced to master AGND, so there is no difference re-inverter.
- Venue (read p93, p102): R141 10R "GND CANCEL RES" per module and R220 10R "ground cancelling resistor" at the master. The manual says it references the aux summers.
- vs ours: different. Both tie the master in at 10 Ω and stop at single-ended referencing. Ours has no master tie (sim: a 22 Ω tie costs ~45 dB) and adds the re-inverter, which is stronger.

**T14 AC coupling**
- Series Two: 33 µF / 100 µF polarised electrolytics at the channel nodes, 330 µF at the summers. Venue: 47-220 µF, 1000 µF at the summer.
- vs ours: ours is better (NP + 47K, film at wipers).

**T15 PFL**
- Series Two (read):
  - Channel: 22K from PREA via latching key to the SOLO bus (off = clean ground); a second pole feeds the SIP/solo-detect logic (470K/680K).
  - Stereo inputs: 36K + 36K mono sum on pole A; pole B carries +VC to an amber LED and 100K to the detect line (see §4.1).
  - Master: 74HC4053 source switching, SIP mode.
- Venue (read p93, p102, p77):
  - 22K to the PFL bus; 100K from +VM to PFL DET.
  - Master: TL072 detector (150K to −VL); J112 series/shunt pairs switch the monitor source; PFL sum amp, then a second inverter.
- vs ours: same scheme (ours uses a DG413).

**T16 Direct out**
- Series Two: 75 Ω impedance-balanced, pre/post switch (spec; rear board not read).
- Venue (read p93): ground-compensated NE5532. The ring samples the remote ground; 4K7/4K7, 22K ×3, 75R; 100 µF.
- vs ours: different; ours is impedance-balanced 75R/75R.

**T17 Master outputs**
- Series Two (read, p10, p22): fader + TL072 post-amp (+8.2 dB), 33 µF, DRV135 with 33 µF on the sense legs. Mix insert send 75R / 22K. No relay on the pages read (inferred: none).
- Venue (read p76): unity buffer after the fader, −10 dBV pad (11.8 dB), cross-coupled NE5532 "EBOS" outputs with a trim, no relay. Ground-cancelling control-room/phones stage with discrete output transistors.
- vs ours: Series Two is the same DRV135 approach; ours adds the relays and the power-on delay.

**T18 Meters**
- Series Two (read, p17):
  - The overbridge 12-segment meters are multiplexed: one LM2901 ladder strobed across 8 channels.
  - Peak LED: LM2901 window comparator fed by a BAV99 diode-OR of two sense points, 2.2 µF hold.
- Venue (read p92, p67):
  - Per channel: TL071 half-wave rectifier and an LM2901 8-segment ladder.
  - Peak LED: 4-point peak detector (post-input, post-EQ, pre-mute, post-fade) diode-ORed into one TL071.
  - Master: 20-segment meters, A970 current sources at 8 mA, two LED chains, peak/average jumper.
- vs ours: ours senses at one point (PRESRC).

**T19 Power**
- Series Two (read):
  - Each board takes ±17 V through 10R + 100 nF.
  - The master splits into ±VA/VB/VC via 4R7 fusible resistors.
  - +5 V CPU from a 7805 (+17 V via 33R). AGND-DGND 0R link (R158).
- Venue (read):
  - 10R + 220 µF per module; logic ±VM via 10R + 47 µF from a separate 10-way mute loom.
  - Phones on their own ±VP (1000 µF) with a separate PHONES GND.
  - ¼" spade ground per module.
- vs ours: same scheme.

**T20 Op-amps / stability**
- Both use TL072 throughout, OP275 / NE5532 at key points; 100 pF across post-amps, 22-33 pF elsewhere.
- vs ours: ours (OPA1612/1656) is quieter.

**T21 Levels / noise**
- Series Two is 0 dBu internal; Venue is −2 dBu.
- Their bus noise, −79/−80 dBu at 32-40 channels, matches our sim (24 strips routed −79 dBu).

**T22 Construction**
- Series Two:
  - 8 channels per PCB plus a separate 8-fader PCB, on point-to-point harnesses.
  - 14-way bus header: G1-4, AGND, G5-8, AGND, MIX L, MIX R, MONO, GCOMP; plus an 8-way aux header and an 8-way power header.
  - Monocoque chassis.
- Venue: one module per channel, IDC motherloom + mute loom, LH/RH PCBs joined by flexi-strips.
- vs ours: Venue is closest to ours.

## 4. Worth considering for goa-console
1. **The crosstalk mod applies to our PFL key SW3.**
   - Their fault: on a stereo input, PFL key SS22 had the audio pole (36K sum → PFL bus, off = AGND, pin 3) beside a supply pole (+VC, a 4R7-fed rail, pin 5, feeding an LED and the 100K PFL-detect pull-up). Above a certain level they got distorted crosstalk onto unrouted outputs, which they called "some sort of instability".
   - Their fix (concession 05/06/2002, SC4020 issue 7): 1 nF from pin 3 to pin 5 at the switch, on shipped and WIP units.
   - Ours (spec §8.2): SW3 is the same topology. Pole A is 22K to bus 27 / AGND; pole B is +VL to the LED and to 100K on PFL DET.
   - Cheap insurance: a 1-10 nF 0805 from +VL to LGND at SW3's pins, and the same at SW4 (ON, which carries ±VL). Two parts per strip; it is a netlist change. Soundcraft never named the root cause.
2. **Multi-point overload sensing.**
   - Venue diode-ORs four points into one peak comparator; Series Two uses two. Ours watches PRESRC only.
   - So we miss a gain stage clipping ahead of an EQ cut (PRESRC is post-EQ by default), and the +10 dB post-fader amp clipping (our own note: synths above ~+12 dBu clip with the fader at the top).
   - Fix: a diode/resistor pair per extra point into U4A. Clearly fits a hot-synth line console.
3. **Bus pin 28 as an anti-phase PFL virtual earth.**
   - Venue's master runs the second PFL inverter's virtual earth on the loom beside the PFL bus to cut crosstalk into the other virtual-earth buses (p77). The Delta's pin 28 "PFL Audio −VE" is the same idea.
   - Ours leaves pin 28 spare and floating between PFL (27) and PFL DET (29).
   - Cost: master-only (one inverter stage), or at least tie it to GNDA at the master as a guard. Modest benefit; needs a sim of the loom capacitance before claiming anything.
4. **Series + shunt JFET mute.** Venue claims >100 dB against our 86 dB. Only worth it if the bench shows audible bleed; a series JFET in the path adds distortion risk. Low priority.
5. **Ground-compensated direct out.** Venue's cold leg samples the far-end ground. It only helps unbalanced recorder inputs on TRS-to-TS-with-ground cables; ours already works with balanced receivers. Skeptical, optional.

**Where ours is weaker than every reasonable practice:** only the single-point OL (item 2). Our receiver, ground cancel (no master tie + re-inverter), output relays and op-amps all match or beat both Soundcraft designs.

**Not covered by the documents read:** the Series Two direct-out and insert jack circuits (rear board ED4024 not read), the DCP200 / Venue PSU internals, Venue's line CMRR circuit detail beyond the values above, and anything on an older Venue I.

Working files (renders and crops): `/private/tmp/claude-501/-Users-ruslanmigirov-projects-goa-console/20d2ad3b-cdbe-4f15-9de0-d1ce86379e7b/scratchpad/survey/s2_venue/`
