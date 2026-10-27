# goa-console against the consoles in the service-manual library (2026-10-27)

This compares the whole design, strip, bus and master, stage by stage with the analogue consoles in Ruslan's iCloud
`Service Manuals/` folder. `eq_survey.md` already did the swept mid EQ, so that is left out here. Nothing in the
design has changed; the proposals in §5 wait for sign-off. One documentation error was found and fixed (§6).

## 1. Sources

Eight readers each took one console family. They rendered the scanned schematics, read values from crops and
compared them against a reference card of our design. Their full reports, with PDF page numbers, are in
`docs/console_survey/`. Each report marks every claim as **read** (from the drawing) or **inferred** (calculated or
deduced).

| Console | Era | Documents | Report |
|---|---|---|---|
| Soundcraft 200 Delta / Delta DLX (our parent) | 1990s | DLX schematics (ED2778-2780, ED3344C), 200 Delta tech manual ZZ2593 | `delta.md` |
| Soundcraft Venue II / Venue Theatre | 1990s | Venue II / Theatre tech manual ZZ2774 (ED3151, ED2913A, ED2919A), user guides | `series_two_venue.md` |
| Soundcraft Series Two | 2000 | schematics ED4019-4041, spec sheet, crosstalk mod | `series_two_venue.md` |
| Soundcraft 6000, 200B | 1988 / 1980s | 6000 schematics ED2721-2722 (+ P3 master), S500 boards, 200B schematics, user guides | `soundcraft_6000_200b.md` |
| Soundcraft Sapphyre, Ghost | 1990s | full schematic sets, Sapphyre user guide | `sapphyre_ghost.md` |
| Soundcraft Series Five | 1997 | technical manual ZM0204 (schematics, specs, CPS2000 PSU) | `series_five.md` |
| SSL 4000G | 1993 | console service manual (82E291 channel amps, 82E26 mix amp, PSU) | `ssl_4000g.md` |
| Yamaha PM-4000 / PM-5000 | 1990s / 2000s | PM-5000 service manual, PM-4000 circuit board scans | `yamaha_pm4000_pm5000.md` |
| Sony MXP-3000 | 1980s | operation / maintenance manual, module, mother-board and PSU schematics | `sony_mxp3000.md` |

**Not used:**
- Delta 8 and Soundcraft 500 / 600: user guides only.
- Yamaha 01V96: digital.
- Pioneer DJM-500 and Technics SH-DJ1200: DJ mixers.

**Gaps in the library:**
- No PSU schematic for the Delta, PM-5000 or Sony.
- No SSL send or insert-send circuit.
- The Sony and PM-4000 hybrids are drawn as blocks.

## 2. Published specifications

Conditions differ between makers, so read across a column with care. Soundcraft measures noise 22 Hz-22 kHz with
an average-reading meter; Yamaha uses a 12.7 kHz filter.

| Console | Internal level | Rails | Mix bus noise (channels routed, faders down) | Line CMRR | Mute |
|---|---|---|---|---|---|
| 200 Delta | −2 dBu (mix bus −7.8) | ±17 V | −80 dBu (16); −75 typical with faders at 0 | > 40 dB | > 90 dB |
| Venue II / Theatre | −2 dBu | ±17 V | −80 dBu (32); −73 typical | > 40 dB | > 100 dB |
| Series Two | 0 dBu | ±17 V | −79 dBu (40) | — | 90 dB |
| 6000 | −2 dBu (mix insert −7.8) | ±17 V | −87 dBu (16, conditions not stated) | "exceptionally high" | 110 dB |
| Sapphyre | −2 dBu | ±17 V | −90 dBu (16) | — | > 110 dB |
| Series Five | −2 dBu | ±17 V | < −78 dBu (32) | 60 dB (0 Ω source) | > 100 dB |
| SSL 4000G | +4 dBm | ±18.5 V | — | — | — |
| PM-5000 | 0 dBu (aux −6) | ±16 V in, ±15 V local | −92 dBu stereo, all assigns off | — | relay |
| Sony MXP-3000 | −2 dBu | ±18 V | < −84 dBu (0-1 channel) | — | — |
| **goa-console** | **0 dBu** | **±17 V** | **−100.4 dBu summer alone (24, sim); −79 dBu at main L with 24 strips at "0", EQ in (sim)** | **54 dB vs a 1 kΩ source (sim)** | **≈ 86 dB** |

**Reading the noise row:**
- Our −79 dBu is not like-for-like: it has every fader at "0" with EQ in, so it includes the strips' own noise,
  whereas the others list bus noise with faders down.
- The comparable figure for faders down is the summer alone, −100.4 dBu in the sim. It leaves out the master fader,
  post-amp and DRV135 that a measured output includes, so it reads optimistic.
- Delta "typical, faders at 0" (−75 dBu re a +4 dBu output, 16 channels) and our −79 dBu re −0.8 dBu (24 channels)
  are about the same S/N.
- Only the jig can give a measured figure.

## 3. Stage by stage

| Topic | What the library does | Ours | Verdict |
|---|---|---|---|
| Line receiver | **No console buffers the legs.** The leg impedance depends on the topology: 15K series into a diff amp (Venue, 6000, Series Five: 2 kΩ), 17K into a fully differential pair (SSL), the mic amp's input (Series Two, Ghost, PM), a hybrid (Sony). CMRR > 40-60 dB with a 0 Ω source. | OPA1656 followers, 1 MΩ per leg, then a 0.1 % diff amp: 54 dB against a 1 kΩ unbalanced source | **Ours ahead** for synths with single-ended outputs |
| Line gain | Most fold the gain into the receiver (Delta, Venue, 6000, Series Five, Sapphyre). Sony uses our topology; SSL a differential stage on a dual pot (±20 dB). | Separate inverting stage, ±15 dB, centre detent | Same as the best of them; folding was rejected (4.7 dB noisier) |
| Ø | Leg swap ahead of the amp (Soundcraft, all); an extra inverting stage (SSL, Sony, PM-5000) | Leg swap | Same; no extra stage |
| HPF | Sallen-Key: fixed ~100 Hz (6000, 200B, Venue), or swept by C-law rheostats (Series Two 40-400, Series Five 20-600, PM 20-400, Sony 20-320); SSL 18 dB/oct | KHN 12 dB/oct, 21-403 Hz, A10K dual as dividers | Same range; ours tunes with a stocked pot |
| Insert | Unbalanced send 75R on a TRS jack (Delta, Venue, 6000, Ghost). Balanced send and return on separate jacks or a patch bay (SSL, PM-5000, Series Five, Sapphyre, Sony ground-sensed) | Unbalanced, normalled TRS, post-EQ (jumpers pre-EQ) | Same as the Delta family; a balanced return needs separate jacks |
| Mute | Series JFET into a virtual earth + shunt JFET: 100-110 dB (6000, Sapphyre, Series Five, Venue Theatre). Two shunts like ours (Ghost). Relays (PM-5000). Mechanical (200B, Sony) | Two J112 shunts after 4K7, 20 ms ramp, ≈ 86 dB; also mutes pre sends and direct out | Shallower than the series-shunt designs (§5 CS8) |
| Fader | Passive 10K log + ≈ +10 dB post-amp (every Soundcraft, Sony +10.9) or a VCA (SSL, PM, Sony option) | 10K A + 10 dB post-amp | Same |
| **Pan law** | **−4.4 dB Delta** (ED3344C: 3K3 from each buffer output back to its wiper, 1.22× buffers; checked on the drawing). Also −4.5 dB Venue Theatre (ED3151) and Series Five, about −4 dB SSL (6K81 law resistors), about −3 dB Ghost (A / C dual) and Sapphyre (3K3 law resistors) | **−6 dB** (linear dual, unity followers) | **Ours is the only −6 dB, and departs from the parent without a record** (§5 CS2) |
| Aux sends | Pot wiper into the bus resistor, unbuffered. Resistor values: 22K (Delta, Venue, 6000), 15K (SSL), 12K (PM-5000, Ghost), 10K (Sapphyre, Series Five), 7.5K (Sony) | 10K A pots, 22K | Same; our 22K gives a lower noise gain |
| Routing | Mechanical key switches the resistor's bus end to clean ground (Soundcraft, all). Source end grounded (SSL, Sony). **PM-5000 uses exactly our scheme:** a CMOS 74HC4053 at the bus end | DG413 at the bus end; the key carries logic only | Same principle; the PM-5000 confirms it in silicon |
| Mix summer | Discrete common-base pair + op-amp (Delta, Venue, 6000 P3, Sapphyre, Series Five, PM-5000, SSL quad); plain op-amp virtual earth (Ghost, 200B, Series Two, Sony hybrid). Most block DC at the summing node with 220-2200 µF. **Most sum below unity:** Delta −8.2 dB, 6000 −6.8, Series Two −5.3 | OPA1612, 4K7 in / 4K7 feedback, unity; DC blocked at each source | The discrete pairs were a TL072-era answer; the OPA1612 matches them. **Unity summing needs a headroom check** (§5 CS3) |
| Ground cancel | 10 Ω per module to a cancel line, but referenced only on the **aux** summers (Delta, Venue, Ghost, Sapphyre; Ghost ties the line with 1K). Series Two references every summer, tied at the master with 10 Ω. 6000 and SSL use a sensed SUM GND (SSL trims it). Sony runs one COM line per bus family, ≈ 1K per module. Series Five makes mix and groups **balanced buses** | 10 Ω per module; every summer (MIX, SUB, aux, PFL) referenced; differential re-inverter to master ground; no master tie (100K keeper) | **Ours is the most thorough single-ended scheme** in the library; only Series Five's balanced bus goes further (it would need a new pinout) |
| Bus AC coupling | Polar electrolytics at sources and summing nodes | 100 µF NP + 47K at every source, film at wipers | Ours more careful |
| PFL | 22K onto a PFL bus + 100K DC detect line (every Soundcraft). The detector holds the line at a virtual earth (200B) or senses it through 150K to −VL (Delta, Venue). JFET source switchers. **Pin 28 driven** as an anti-phase PFL virtual earth (Delta, Venue) or an undriven dummy track subtracted at the master (Series Five) | 22K, 100K detect line sensed as a voltage (0.5 → 0.92 V), DG413 switcher; pin 28 spare | Ours leaves two crosstalk measures unused (§5 CS5) |
| Direct out | Ground-compensated (Delta, Venue), actively balanced (PM-5000, Series Five, Sony), unbalanced (Ghost, 6000) | Impedance-balanced 75R / 75R from aux 6 | Equivalent |
| Master outputs | Cross-coupled 5532 pairs (Delta, Sapphyre, 6000, PM-5000), SSM2142 (Series Five), DRV135 (Series Two), hybrids (Sony, SSL). **No console has an output mute relay or a power-on delay** | DRV135 + G6K relays, 2.8 s power-on delay, fast release on a rail drop | **Ours ahead** |
| C/Room | Taken from the balanced outputs through receivers (Delta); **dim** (Delta −20 dB, Series Five, Ghost) | From POST_L/R; no dim | Missing dim (§5 CS7) |
| Master meters | Precision rectifier + LM2901 ladder with a PNP current source, series or shunted LED strings (Delta, Ghost, Sapphyre, Series Five, PM-5000) | The same, values copied from the Delta | Same |
| **Strip overload LED** | **Several points, often full-wave:** SSL (3 stages, both polarities), Sapphyre (4 points, full-wave window), Ghost (4 points), Series Five (3, "bipolar"), Venue Theatre (4), Series Two (2, window), PM-5000 (3, window, 3 dB below clip). Delta: one point at +9 dBu, 12 dB below clip | **One point (PRESRC), positive half only**, +18 dBu (≈ 3 dB below clip); green from −20 dBu | **Ours is the weakest in the library** (§5 CS1) |
| Strip power | 10R + 47-220 µF per module (every Soundcraft, Sapphyre exactly ours). Logic rails via 10R with a single-point tie. Spade ground. **Fusible feeds:** Series Five fusible 10R per sub-rail, Series Two 4R7 fusible, SSL 2 A fuses per module, PM-5000 IC protectors per channel | 10R anti-surge (ERJ-P06J100V) + 220 µF, ±VL, GNDD tie NT1, spade; wing PTCs per 12 strips | Same scheme; ours has no per-strip fuse (§5 CS6) |
| PSU | Linear with SCR crowbar (SSL), linear with mutual shutdown but no crowbar (Series Five CPS2000), LM317 / LM337 without a crowbar (200B), linear with remote sense (Sony) | LM1084 + SCR crowbar per rail, LC pre-filter | Same class as SSL |
| Jack-facing I/O protection | **PM-5000:** DAN217 clamps to the rails at every insert, direct and line output and return. Others: none seen | None (the BAT54W on the signal-LED detector is the only clamp) | Missing (§5 CS4) |
| Op-amps | TL072 / NE5532 / 5534, discrete pairs, hybrids | OPA1612 / OPA1656, C0G stability caps, build-outs | Ours ahead; stability practice the same |

## 4. Where ours is ahead of everything in the library

- **Line receiver:** the only input that keeps its CMRR against a synth's unbalanced output impedance.
- **Mains:** output mute relays with a power-on delay. No console in the library has them.
- **Ground cancel:** applied to every summer, with a true difference re-inverter and no master tie.
- **Bipolar coupling:** non-polar and film everywhere; no polar electrolytic on a bipolar node.
- **Polarity, routing and the PFL switcher:**
  - Ø costs no stage.
  - Routing carries no audio through the panel keys; the PM-5000 does the same with a 4053.
  - The DG413 PFL switcher isn't affected by the J112 gate-bias problem we hit.

## 5. Proposals (not applied; for sign-off)

Each is a candidate for its own proposal document with simulation before anything changes. They are ordered by how
strongly the library supports them.

- [ ] **CS1 Multi-point, full-wave overload detection.** Worked up in `cs1_proposal.md` (patch, simulation, trial checks).
  - *Library:* seven of nine consoles watch two to four stages; four of them catch both polarities.
  - *The gap:* ours sees only PRESRC's positive peaks. That misses:
    - the gain stage clipping ahead of an EQ cut;
    - EQ boost clipping when the insert follows it (PRESRC is post-insert, so a post-EQ insert pad hides it);
    - the +10 dB post-amp U2A clipping with the fader up (hot synths above ~+12 dBu, already noted in CLAUDE.md);
    - asymmetric synth waveforms clipping on the negative half.
  - *Proposed:* diode-OR GOUT (U1B), PRESRC and U2A's output into the existing hold node; a full-wave window (Sapphyre /
    PM-5000 style) or a second diode set from an inverted tap; thresholds set per point against each stage's own
    clip level.
  - *Cost:* about 4-8 small parts per strip, likely no new IC. Re-run `sim/review/gaps/ol.py`; check loading on U1B /
    U2A (C0G and phase margin).
- [ ] **CS2 Pan law −4.4 dB, as the Delta (ED3344C) and Venue Theatre (ED3151).**
  - *The circuit:* 3K3 from each pan buffer's output back to its pot wiper; buffers at 1.22× (2K2 / 10K). Result:
    −2.7 dB at centre, +1.7 dB hard-panned.
  - *The gap:* ours is a plain −6 dB, so a centred mono synth sits 1.6 dB lower against panned stereo sources than on
    the parent. `delta_clone_comparison.md` doesn't record this as a decision; it looks like a transcription loss.
  - *Cost:* 4 resistors per strip, and U8B / U3A become gain stages (re-run stability).
  - *Knock-on effects:*
    - mix levels move +3.3 dB at centre, so the `sim_console` targets change;
    - the PAN-off feed to the subs needs the same +1.7 dB to match. The Delta does it with IC6-B, R145 1K8 / R146 10K
      in the crop; our U3A / U8B arrangement differs, so this needs working out;
    - mix-bus headroom drops by up to 3.3 dB (see CS3).
  - Taste decision, yours.
- [ ] **CS3 Mix and sub summer headroom: sum below unity.**
  - *The numbers:*
    - Each strip at nominal (POST 0 dBu, centred) puts −6 dBu on the summer; 24 uncorrelated strips sum to about
      +7.8 dBu at the summer output.
    - With synths 10 dB hot at the "0" gain setting, the sum is about +17.8 dBu, 3 dB from the OPA1612's ≈ +21 dBu
      clip.
    - The master fader comes after the summer, so it can't help. CS2 would take another 3.3 dB.
  - *Library:* the Delta sums at −8.2 dB (3K9 on 10K), the 6000 at −6.8 dB, Series Two at −5.3 dB; all make it up after
    the master fader or in the output stage.
  - *Proposed:* feedback 4K7 → about 2K4 (−6 dB) on the MIX / SUB summers, +6 dB more after the master fader.
  - *Noise:* the summer's noise relative to signal barely moves at N = 24 (the noise gain falls with the signal gain);
    the make-up stage adds a little.
  - *First step is only a check:* a `sim_console` run with hot correlated and uncorrelated sources, and the noise
    figure, before deciding.
- [ ] **CS4 Clamp diodes at jack-facing I/O** (PM-5000 practice).
  - *Why:* live patching (hot plugging, a phantom-powered lead, synth DC). 48 V through 6K8 into J1 gives about 7 mA
    through the 220R into U16's internal ESD diodes, near the OPA1656's rating.
  - *Proposed:* a low-leakage dual diode (BAV199-class; a BAV99's leakage into the 1M legs would shift DC) to the rails
    at J1's legs after the 220R, the insert return, and the direct-out and insert-send pins.
  - *Master:* DRV135 outputs to be checked against TI's protection notes.
  - *Cost:* about 4 SOT-23 per strip.
- [ ] **CS5 PFL-bus crosstalk measures.** Three independent items:
  - **(a) PFL / ON key supply poles:**
    - *Library:* Soundcraft's Series Two field mod (concession 05/06/2002) added 1 nF from the PFL key's audio-ground
      throw (pin 3) to its supply pole (pin 5, an LED / detect rail). That cured distorted crosstalk onto unrouted
      outputs.
    - *Ours:* SW3 has the same layout (pin 3 GNDA, pin 5 +VL), and SW4 carries ±VL.
    - *Proposed:* 1-10 nF from +VL to GNDD at SW3 and SW4. Two 0805 parts per strip.
  - **(b) Pin 28:**
    - *Library:* the Delta and Venue drive it as the PFL sum's anti-phase virtual earth; Series Five subtracts an
      undriven dummy track at the master.
    - *Ours:* the strips leave it unconnected, so it already is Series Five's dummy track; it only needs the
      subtraction at the master PFL summer (one op-amp half, two 22K), or at least a GNDA tie as a guard between PFL
      (27) and PFL DET (29).
    - *Change:* master only.
  - **(c) PFL DET at a virtual earth** (200B, 6000 detector):
    - the master holds pin 29 at 0 V and reads the current, so the line no longer swings 0.5 → 0.92 V beside the PFL
      bus;
    - re-run `sim/pfldet.py` (clamp, debounce, back-feed into the LEDs). Master only.
- [ ] **CS6 Per-strip fusible supply feed.**
  - *Library:* Series Five (fusible 10R per sub-rail), Series Two (4R7 fusible), SSL (2 A fuses per module), PM-5000
    (IC protector per channel).
  - *Ours:* a shorted strip trips its wing's PTC, which silences 12 strips; anti-surge resistors are built not to open.
  - *Proposed:* R1 / R2 (and R3 / R4) as fusible types sized for the strip's ~92 mA. This needs a part search: an 0805
    fusible 10R that opens fast enough to beat the MF-RX250/72's trip.
- [ ] **CS7 Dim on C/Room** (Delta −20 dB, Series Five, Ghost). One key and a resistor, or a spare DG413 section, on
  the master. A feature, your call. Talkback / slate / oscillator are left out on purpose: they serve mics and tape.
- [ ] **CS8 Deeper mute (defer to the jig).**
  - *Library:* series JFET into a virtual earth + shunt reaches 100-110 dB (6000, Sapphyre, Series Five, Venue).
    Their own fader kill is 80-90 dB, the same as our ≈ 86 dB mute.
  - *Proposed:* only if the jig hears bleed; it would turn U3B into an inverting virtual-earth stage.

**Considered and not proposed:**
- **Balanced insert return** (SSL, PM-5000, Series Five, Sapphyre): needs separate send / return jacks, and our
  single normalled TRS can't carry it.
- **Solo-in-place** (SSL, 6000, Sapphyre): conflicts with the signed decision "PFL only (no SIP)".
- **Balanced mix bus** (Series Five): needs a new bus pinout; our ground cancel already simulates −93 dBu residue.
- **Others, each with the reason in its console report:** discrete summing pairs; DC blocking at the summing node;
  ground-cancel ties or trims (our sim: a 22 Ω tie costs 45 dB); cap multipliers or remote sense on the supply; Sony's
  one reference line per bus family (worth revisiting only if the jig shows aux hum).

## 6. Correction made

`master_section_spec.md` §3 said "The Delta does the same job with differential receivers on MIX L+/L−". The Delta
DLX drawing (ED2780 sheet 1) shows those receivers (IC7, 43K / 20K / 22K) under MONITOR SELECT. They are fed from the
balanced mix outputs and have nothing to do with ground cancel. The Delta's mix summers reference local ground; only
its aux summers take GND CANCEL. The spec line is corrected. Our design and its no-tie decision are unaffected.
