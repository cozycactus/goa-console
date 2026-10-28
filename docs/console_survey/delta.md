# delta: Soundcraft 200 Delta / Delta DLX, compared with goa-console

## 1. Header
**Documents read**
- `ref/Sndcft_DeltaDLX_Schems.pdf` (vector, legible at 300 dpi):
  - PDF p.6: ED2778A, group output.
  - PDF p.8: ED2779A, LH (aux) master.
  - PDF p.10: ED2780 sheet 1 (RH master): monitor select, PFL switcher / sum amp / detector, C/R and phones amps, talkback and oscillator, motherloom connector, power entry.
  - PDF p.11: ED2780 sheet 2: mix summing amps, insert, post-amps, balanced outputs, mono.
  - PDF p.12: ED2780 sheet 3: meter.
  - PDF p.17: ED3344C, Theatre strip pan, routing and direct out.
- 200 Delta Technical Manual ZZ2593, scanned:
  - Specs on printed p.12-14, 22, 24-25 and 31-32 (Part1).
  - Circuit descriptions on p.55-56 and 61-65 (Part2 PDF p.5-6, 11-15).
  - System overview / power supply on p.28-29 (Part3 PDF p.23).

**Missing**
- There is no PSU (CPS150) schematic, so rails, regulation and protection are not shown.
- ED2779B (LH meter) and the Delta 8 manual were not read. The Delta 8 manual is a ManualsLib scan of the user manual and duplicates the specs.

**Already covered, not repeated:** the strip stages in `delta_clone_comparison.md`.

## 2. Published specs (16-channel console)
| Spec | Value | Page |
|---|---|---|
| Operating levels | Internal −2 dBu; outputs +4 dBu or −10 dBV, 75 Ω; insert sends −2 dBu; mix / group insert −8 dBu | p.13 |
| Max levels | Mix out +27 dBu balanced into 600 Ω; group / aux +21 dBu unbalanced; insert / direct +21 dBu into 5K; phones +20 dBu | p.13 |
| Rails | ±17 V and +48 V from an external CPS150 (CPS450 for 32 channels) | ED2780 sht 1, p.29 |
| Line input CMRR | >40 dB at 1 kHz, unity gain | p.12, p.14 |
| Mix output CMRR | >40 dB | p.24 |
| Line EIN | −93 dBu (40 Ω source, unity gain) | p.12 |
| Mix noise, 16 channels routed, faders down | −80 dBu | p.12 |
| Typical mix noise, faders at 0 | −75 dBu | p.12 |
| Group bus residual | −93 dBu | p.22 |
| Aux bus noise | −78 dBu | p.12 |
| Crosstalk | mute >90 dB, fader >80 dB, pan >85 dB, routing >90 dB, L/R <−80 dB | p.12, p.24 |
| Frequency response | 20 Hz-20 kHz +0/−0.5 dB | p.12 |
| THD at +20 dBu | 0.003 % (mix), 0.008 % input to mix at 1 kHz | p.12 |

- Measurement conditions (p.25): noise is measured 22 Hz-22 kHz with an average-reading meter. 0 dBu in at gain "0" gives +4 dBu at any output.
- Against ours: −75 dBu re +4 dBu is about 79 dB S/N at 16 channels. Ours is −79 dBu re −0.8 dBu at 24 channels (RMS), about 78 dB, roughly 80 dB scaled to 16 channels. They are on a par, with different detectors.
- Our mains run about 5 dB below the Delta's +4 dBu reference: −0.8 dBu for 0 dBu in, pan centre. That is harmless given the +27 dBu ceiling.

## 3. Per topic
**T1 Line receiver.** **Read:** 10 kΩ electronically balanced diff amp (TL072), CMRR >40 dB (p.14).
- vs ours: different. Our buffered receiver (1 MΩ legs, 54 dB against a 1K source) is clearly better. The departure is justified.

**T2-T5:** see `delta_clone_comparison.md`.

**T6 Insert.** **Read:** the master mix insert sits at −10 dBV (−7.8 dBu), unbalanced, 75R send, normalled (ED2780 sht 2).
- vs ours: our master insert runs at the mix level, about 0 dBu. That suits a +4 dBu external bus compressor better. Justified.

**T7 Mute.** **Read** (corrected 2026-10-28, `delta_crosscheck.md` D3; this line said "same J112 pair as ours"):
series J112 (TR4) into IC6-A's virtual earth plus a shunt J112 (TR3) with its source on C30 47 µF (no DC across the
FET), gates on complementary MUTE / MUTE-bar from a TR6 / TR7 inverter pair (220K / 100n, 1N4148, 680K bleeds); the
Venue the same.
- vs ours: two shunt J112s in a 4K7 ladder into a follower, one RC ramp from the key: not the same circuit. Ours adds
  muting of the pre sends. Depth (86 dB simulated against the Delta's 100-110 dB) is CS8, measured at the jig.

**T8 Fader / post-amp.**
- **Strip:** same as ours. **Read:** the post-fader non-panned feed IC6-B is +1.4 dB (1K8 / 10K).
- **Master:** **read:** fader into IC3-A, non-inverting +6 dB (1K / 1K, 100p), 2.2 µF + 100K in, then a 1K2 / 430R pad switched by S1 for −10 dBV (ED2780 sht 2).
- vs ours: ours is +10 dB. Same idea.

**T9 Pan.** **Read** (ED3344C):
- VR10 is a 10K B dual. Each wiper drives a TL072 non-inverting buffer with a gain of 1.22 (R122 2K2 / R124 10K).
- A 3K3 "law resistor" (R120 / R121) runs from each buffer output back to its wiper. Manual p.56: law resistors fed from the buffer outputs, about 85 dB cut-off.
- **Inferred (my nodal calculation):** at the centre the wiper rises to 0.6 Vin, so the output is −2.7 dB, against +1.7 dB fully to one side. That is a **−4.4 dB pan law**.
- Outputs go through 220 µF + 47K.
- vs ours: **different.** Ours is −6 dB with unity followers, so a centre-panned mono synth sits 1.6 dB lower relative to hard-panned sources than on a Delta. This is not covered in `delta_clone_comparison.md`. See §4.

**T10 Aux sends.** Same values: 10K A pots, 22K to the bus, PRE per pair, J4-J7 pre-fader / pre-EQ links (ED3344C).

**T11 Routing.** 10K 0.5 W resistors; off grounds the resistor (Delta, ED3151). Ours uses 4K7 and the DG413. This is a known, recorded departure.

**T12 Bus summing.** **Read** (ED2780 sht 2, ED2778A, ED2779A; manual p.61):
- **Topology:** a discrete differential summing amp, not an op-amp virtual earth. Two 2SB737 PNPs in common base, bases joined, emitters fed from +17 V through 10K / 10K (mix), collectors on 4K7 / 4K7 + 820R to −17 V, into a 5532 differential stage (C3 100p across the collectors).
- **Bus input:** the bus enters TR1's emitter through a ferrite bead and **1000 µF / 6.3 V** (group: 1000 µF / 63 V).
- **Feedback:** from the output (after 75R) through a 4K7 / 4K7 unity inverter (IC1-A) and **3K9** back into the emitter. The inverter sits inside the loop, so the stage is **non-inverting overall** and needs no re-inverter.
- **Compensation:** C4 220p from the output to TR2's emitter.
- **Gain:** with 10K routing, 3K9 / 10K = −8.2 dB ("−5.8 dB ref chan fader top"). The mix runs at −7.8 dBu, then +6 dB post-amp and +6 dB output amp.
- **Aux:** the same stage with 33K emitter feeds and 10K feedback against 22K sends (−6.8 dB). The aux master pot sits inside the loop: R10 / R11 feed the post-pot buffer into the inverter's + input, so the summer's gain falls as the master is turned down (p.63).
- vs ours: **different.** Ours is an OPA1612 inverting summer, 4K7 / 4K7, plus a 4 × 2K2 re-inverter.
  - The Delta avoids the second stage but needs a 1000 µF coupler, a discrete pair and a bias network.
  - OPA1612 noise (1.1 nV/√Hz) is close to a 2SB737 pair's at these currents.
  - Ours is justified.
  - The pot inside the aux loop buys little: signal and summer noise fall together. Not worth copying.

**T13 Ground cancel.** **Read:**
- **Where it is used:** GCANCEL (pin 26) is used **only by the aux summing amps** (ED2779A, manual p.63). TR1's base sits on GROUND CANCEL and TR2's base on the master's local ground, so a single stage both sums and moves the reference to master ground.
- **Mix and group summers:** both bases are on local ground (ED2780 sht 2, ED2778A). They get no ground cancel.
- **Manual p.63:** "On every module, with the exception of the Left Hand Master, this bus is connected to the module ground by a 10 Ω resistor."
- **Strip:** R141 10R "GND CANCEL RES" (ED3344C).
- **RH master:** R220 10R "ground cancelling resistor" from master ground to pin 26 (ED2780 sht 1). The master is simply one more averaged ground.
- **LH master:** R125 10R is drawn (ED2779A), but per the text it is not fitted.
- **Group:** R66 is printed 75R, and the note says it is not fitted on the Delta 8. That disagrees with the "10 Ω" in the text, so treat it as unresolved.
- vs ours: different, and ours is more thorough. We cancel on every summer: MIX, SUB, aux and PFL.
- **Spec correction:** `master_section_spec.md` §3 says "The Delta does the same job with differential receivers on MIX L+/L−". That is a misreading. Those 43K / 22K receivers (IC7, ED2780 sht 1) are the **monitor-select** inputs fed from the balanced mix outputs, not ground cancel.
- **Our no-tie decision** (100K keeper) stays justified. In the Delta the RH master's 10R tie only dilutes the aux reference by 1 / (N + 1), and its mix summers don't use GCANCEL at all.

**T14 Bus AC coupling.**
- **Read:** the strip feeds go through 220 µF / 25 V polar + 47K (C54-C56, ED3344C). The summer inputs are DC-blocked with 1000 µF, and the PFL sum has 100 µF in series (C26) with 47K to ground.
- vs ours: similar. Ours is 100 µF NP + 47K with no summer-input block.

**T15 PFL.** **Read** (ED2780 sht 1, p.64-65):
- **Sum amp:** PFL+ → 100 µF → IC9-A inverter (22K / 22K, 100p), then a second inverter, IC9-B (22K / 22K).
- **Pin 28 (PFL−):** wired to IC9-B's virtual earth. The manual says this "anti-phase virtual earth … running next to the PFL bus" reduces PFL-to-bus crosstalk.
- **Switcher:** four J112 series switches (TR5-TR8) with 47K gate-source and 47 µF across, driven via 1N4148s from the detector.
- **Detector:** IC10-B (TL072) with 150K to −VL; each pressed key connects +VL through 100K (strip R48 100K). Output +10 V normal, −0.6 V active, and TR13 / TR14 (2SC2240) drive the J112 gates and the PFL LED.
- vs ours: DG413 instead of J112s (justified by our own switching sim). Same 100K detect line.
- **Difference:** we leave pin 28 spare.

**T16 Direct out.** **Read:**
- **Circuit:** a ground-compensated output. IC12-A non-inverting, gain 2 (4K7 / 4K7). Its + input is fed by 22K from the signal and 22K from the jack ring. The ring is the far-ground sense, 75R to local ground. The tip has a 75R build-out and 100 µF (ED3344C).
- vs ours: our impedance-balanced 75R / 75R does the same job. Equivalent.

**T17 Master outputs.** **Read:**
- **Mix:** cross-coupled electronically balanced pair per side (5532 IC4 / IC5):
  - 4K7 in, 10K feedback, 10K cross-coupling taken after the output caps, 22p;
  - 75R + 47 µF / 25 per leg;
  - a 1K / 1K / 1K balance preset (PR1) to ground;
  - +27 dBu into 600 Ω.
- **Group / aux / mono:** unbalanced ground-compensated outputs. The ring is a sense input through 4K3 (group) or 10K (aux); the mono uses 39R / 10R.
- **Mono:** L + R through 22K / 22K into a 15K inverter (−3 dB uncorrelated), **pre master fader**, with a mono-fader option.
- **No output mute relays and no power-on delay.**
- vs ours: DRV135 everywhere, relay mutes with a 2.8 s delay, mono post master. Ours is better on every point.

**Monitoring (part of T17).** **Read:**
- **C/R source:** taken from the **balanced mix outputs** through diff receivers (43K / 43K in, 22K feedback, 33p; the − leg's lower arm is a switched T, 6K8 + 20K with 2K2 to ground through S1: −4.1 dB open, +6.3 dB closed, so the bridge is 26.8K against 22K, not ratio-matched; D17, 2026-10-28). The 2TRK return goes through the same receivers, switched for −10 / +4 by that T. The control room therefore hears what leaves the XLRs.
- **C/R and phones amp:** TL072 + 2SC2240 / 2SA970 class-AB followers (10R emitters, 1N4148 bias), 220 µF out.
  - Phones through 47R; C/R through a 470R / 470R pad, 250 Ω output.
  - Ground-compensated: 22K / 47R sense.
  - Own ±VP supply (33R + 1000 µF) and PHONES GND.
- **Dim:** −20 dB and cut on talkback (R90 / R190, S3 / S4).
- vs ours:
  - We tap POST_L / R before the DRV135. That is fine, but it misses faults in the output stage.
  - LME49600 phones with a separate PHONESGND: same idea.
  - Dim: ours since CS7 (2026-10-28, SW4, −20 dB on C/Room only); this line read "we have no dim" before.

**T18 Meters.** **Read** (ED2780 sht 3; manual p.62, 65):
- **Rectifier:** TL071 precision half-wave (1N4148s), 10K / 4K7, 22K cal preset.
- **Ballistics:** average 33K + 2.2 µF; peak 75R + 10 µF with 33K / 22K discharge; J2 link selects. Spec: rise 150 / 4 ms, decay 250 ms / 1.2 s.
- **LEDs:** 20 LEDs, LM339 / LM2901 comparators that shunt the current away from each LED. Ladder 15K + 1K5…20R + 91R to **meter ground**. Two A970GR PNP current sources (75R, 2 × 1N4148).
- **Meter ground:** separate, on its own 20-way ribbon conductor.
- **Strip peak LED** (standard input, p.56): discrete TR3 / TR4 at about +9 dBu internal, which is 11 dB over the −2 dBu nominal and about 12 dB below clip.
- vs ours: meters identical in architecture (we even copied the ladder values).
- **Strip LED differs:** our red is at +18 dBu, about 3 dB below the ~+21 dBu clip. That is closer to an overload than a peak indicator, and the green −20 dBu LED fills the gap below it. See §4.

**T19 Power.**
- **Read:** CPS150 external supply, ±17 V and +48 V, 5-way SRC connector into the RH master, which is the power distribution point (p.28-29, ED2780 sht 1).
- **Master filtering:** op-amps 10R + 47 µF, logic ±VL 10R + 47 µF, phones 33R + 1000 µF. LH master: 10R + 220 µF per aux pair.
- **Strip:** 10R + 220 µF per rail; ground through a 1/4" spade (CN4).
- vs ours: same rails and per-module filtering. Our power enters at the master and adds the LDO, crowbar and wing PTCs; the PSU itself can't be compared (no schematic).

**T20 Op-amps.** TL072 / TL071 / NE5532 and discrete 2SB737 front ends. Ours are OPA1612 / OPA1656, a known departure.

**T21 Levels.** Internal −2 dBu; mix bus −7.8 dBu, +12 dB of make-up at the outputs (p.64: chosen for headroom). Ours is 0 dBu internal; MIX_L sits around −7 dBu per channel at the fader "0", so headroom is comparable.

**T22 Construction.** One PCB pair per channel on a ribbon motherloom with a spade ground; group / master outputs on a separate 20-way loom (p.28, p.62). Same as ours.

**Not covered / not checked:** the PSU circuit (T19 internals) and Delta-specific stability parts (T20 beyond IC types).

## 4. Worth considering for goa-console
1. **Pan law: −4.5 dB instead of −6 dB.**
   - Why: the Delta's 3K3 bootstrap from the buffer output to the wiper, with 1.22× buffers, gives about −4.4 dB. Ours drops centred mono synths 1.6 dB more against panned stereo sources.
   - Cost: 2 resistors + 2 gain resistors per strip. The pan buffers' gain changes, so stability (C0G caps, PM sims) and the level chain must be re-run.
   - Fit: a matter of taste for a stereo synth mix. It is not a fault, but it is the one strip departure nobody recorded.
2. **Correct `master_section_spec.md` §3.**
   - The Delta's MIX L+/L− receivers are monitor select, not ground cancel. The Delta applies GCANCEL only to its aux summers, and its RH master ties to GCANCEL with 10R.
   - Cost: documentation only. Our no-tie choice still stands on our own sim.
3. **Pin 28 as a guard.**
   - The Delta drives pin 28 with the PFL sum's anti-phase virtual earth to cut PFL-bus crosstalk.
   - The cheap equivalent for us: tie pin 28 to master GNDA so it shields PFL (27) from PFLDET's edges (29). Zero parts.
   - Fit: marginal, because our PFL bus is switched and PFLDET is debounced.
4. **Dim key on C/Room.**
   - The Delta has a −20 dB dim (and cut on talkback); ours has neither.
   - Cost: one PVA2 + a resistor across the C/Room feed, or one DG413 channel.
   - Fit: useful in a synth studio. Talkback, oscillator and slate are mic / tape features, so skip those.
5. **Strip red-LED threshold.**
   - The Delta warns 12 dB before clip; ours at +18 dBu, about 3 dB before.
   - With fast attack and 150 ms hold, ours catches real overloads. But any stage ahead of the detect point can clip first: receiver or gain stage with an EQ cut, or a boosted band near +21 dBu.
   - Consider +15 dBu, or a second detect point at the gain-stage output. The cost is a resistor change, or an LM393 half on the spare comparator.

**Not worth copying:**
- the discrete 2SB737 summers (1000 µF couplers, bias trims; OPA1612 is as quiet);
- the aux master pot inside the loop;
- monitoring from the balanced outputs: a receiver per side for little gain; our POST tap is fine;
- the unbalanced ground-compensated group / aux outputs (our DRV135s are better);
- J112 PFL switches (our sim already rejected them).

Work files (crops and renders) are in a scratch folder outside the repo (not kept). Key crops: c11a.png (mix summer), c08aux.png (aux summer on GCANCEL), c10bot.png (R220 tie), c17pan.png (pan law).
