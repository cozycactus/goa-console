# goa-console against the consoles in the service-manual library (2026-10-27)

This compares the whole design, strip, bus and master, stage by stage with the analogue consoles in Ruslan's iCloud
`Service Manuals/` folder. `eq_survey.md` already did the swept mid EQ, so that is left out here. Nothing in the
design has changed; the proposals in §5 wait for sign-off. One documentation error was found and fixed (§6).

## 1. Sources

Eight readers each took one console family, and a second batch of six read the consoles in Ruslan's Downloads (§7). They rendered the scanned schematics, read values from crops and
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
| *Second batch (§7, from `~/Downloads`):* | | | |
| Allen & Heath GL2 (+ GL2200) | 1993 / 1999 | GL2 service manual AP0179, GL2200 schematics (the GL4 isn't in the PDF) | `ah_gl2_gl4.md` |
| Allen & Heath GL3300 ("L3D") | 1997-2000 | 26 pages of schematics, no spec page | `ah_gl3300.md` |
| AMEK big (by Langley) | 1994-97 | technical manual MAN/BIG: specs, alignment, test methods, PSUs; no circuit diagrams | `amek.md` |
| Yamaha MC803 / 1203 / 1603 / 2403 (a Phonic OEM design) | 1993 | service manual with the full schematic | `yamaha_mc.md` |
| Soundcraft Spirit E series (E8) | 2000s | technical manual schematics S-S2001AS-02A | `soundcraft_e8.md` |
| Mackie CR1604-VLZ, MS1402-VLZ, 8•Bus | 1990s | VLZ service manuals; the 8•Bus board schematics (zip) | `mackie.md` |

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
| **Strip overload LED** | **Several points, often full-wave:** SSL (3 stages, both polarities), Sapphyre (4 points, full-wave window), Ghost (4 points), Series Five (3, "bipolar"), Venue Theatre (4), Series Two (2, window), PM-5000 (3, window, 3 dB below clip). Delta: one point at +9 dBu, 12 dB below clip | **One point (PRESRC), positive half only**, +18 dBu (≈ 3 dB below clip); green from −20 dBu | **Ours was the weakest in the library** (§5 CS1). Since strip v5.0: 5 points, both polarities |
| Strip power | 10R + 47-220 µF per module (every Soundcraft, Sapphyre exactly ours). Logic rails via 10R with a single-point tie. Spade ground. **Fusible feeds:** Series Five fusible 10R per sub-rail, Series Two 4R7 fusible, SSL 2 A fuses per module, PM-5000 IC protectors per channel | 10R anti-surge (ERJ-P06J100V) + 220 µF, ±VL, GNDD tie NT1, spade; wing PTCs per 12 strips | Same scheme; ours has no per-strip fuse (§5 CS6) |
| PSU | Linear with SCR crowbar (SSL), linear with mutual shutdown but no crowbar (Series Five CPS2000), LM317 / LM337 without a crowbar (200B), linear with remote sense (Sony) | LM1084 + SCR crowbar per rail, LC pre-filter | Same class as SSL |
| Jack-facing I/O protection | **PM-5000:** DAN217 clamps to the rails at every insert, direct and line output and return. Others: none seen | None (the BAT54W on the signal-LED detector is the only clamp) | Missing (§5 CS4) |
| Op-amps | TL072 / NE5532 / 5534, discrete pairs, hybrids | OPA1612 / OPA1656, C0G stability caps, build-outs | Ours ahead; stability practice the same |

### Addendum: Mackie 8•Bus (24•8 / 32•8), read 2026-10-27

From `~/Downloads/mackie_8-buss_mixer.zip`, channel board 990-009-00 rev U, sheet 09-1, top right; the owner's manual
gives the three points.
- **Taps:** three, each through 200K and a 1N4148 (D101-D103): the mic/line preamp out, after the EQ in/out switch, and
  after the fader amp. They charge C113 0.22 µF ∥ R119 100K.
- **Comparator:** U101A (a "2403" quad) against 2.78 V from R120 200K / R121 36K / R122 510 on +18 V.
- **Polarity:** positive peaks only.
- **Attack:** slow. 200K × 0.22 µF (with the 100K, a 3:1 divider) needs a sustained overload. The hold is set by
  0.22 µF ∥ 100K, about 22 ms.
- **−20 LED (U101B):** one point, the post-EQ node, through R171 200K with D110 clamping the negative half, against
  39 mV.

**Against strip v5.0:**
- Mackie has 3 taps to our 5, positive only against our both polarities.
- Its attack takes many cycles; ours is 0.1 ms, so a single peak lights.
- Holds: ~22 ms against our ~150 ms.
- The −20 / green LED reads one point in both designs.

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

- [x] **CS1 Multi-point, full-wave overload detection.** Signed off and applied 2026-10-27 as strip v5.0 (`cs1_proposal.md`).
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
- [x] **CS2 Pan law −4.4 dB, as the Delta (ED3344C) and Venue Theatre (ED3151).** Signed off and applied 2026-10-27 as
  strip v5.4 (`cs2_proposal.md` Option A: the Delta's network with 22 pF for our OPA1612s; PAN off stays at POST).
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
- [ ] **CS2b The same law on the group's sub pan** (proposed 2026-10-28, `cs2b_proposal.md`, not signed off): the
  strip's network on U3B / U5A (R123-R128, C96 / C97), so the sub pan copies the strip again (master spec §12). The
  parent's group module (ED2778A MONITOR PAN, passive 3K9 / 8K2) pans at −4.6 dB; ours is −6 dB. Sub to MIX +3.3 dB at
  centre; U3B / U5A 74.5 / 75.3° (55.3 / 55.9° with 47 pF); `check_all --full` 61 / 61 on the trial tree.
- [x] **CS3 Mix and sub summer headroom: checked 2026-10-27, no change** (`sim/review/cs3/bus_headroom.py`, from the
  whole-console model).
  - *Per source* (0 dBu in, pan centre, every fader at "0"): the summer carries −6.4 dBu, as do the re-inverter, the
    master fader's top and its post-amp; that's 29.5 dB to the ±15.5 V swing (+23.0 dBu). The XLR carries −0.9 dBu
    against the DRV135's +27 dBu: 27.9 dB.
  - *A full mix:* 24 strips at their nominal level, uncorrelated, put the summer at +7.4 dBu, a 15.7 dB margin. The XLR
    is at +12.9 dBu, a 14.1 dB margin.
  - *Why no change:*
    - **Balanced chain:** with the master fader at "0" the summer has 1.6 dB more margin than the output stage.
    - **Pan law:** our −6 dB already sums 6 dB below the strip level, doing what the Delta's −8.2 dB summer gain does.
      The first draft of this item used a +21 dBu clip and synths left 10 dB hot at the gain detent; both were wrong.
  - *The one case left:* the summer clips first only when a hot mix is pulled down by the master fader more than
    1.6 dB below "0". The meters, after the fader, then read low and don't show it.
  - *Fixes if wanted:*
    - Operating note: trim with the channel faders and keep the master near "0".
    - Hardware: a pre-master-fader peak LED on SUM_L / SUM_R. Summing below unity would need more post-amp gain and
      noise for the same effect.
  - *CS2 interaction:* the −4.4 dB pan law raises every stage of the master chain by the same 1.6 dB at centre (3.3 dB
    hard-panned), so the balance holds.
- [x] **CS4 Clamp diodes at jack-facing I/O** (PM-5000 practice). Signed off and applied 2026-10-27 as strip v5.2 (`cs4_proposal.md`): one BAV199 per link signal at CN3. CS4b (group / master) signed off and applied 2026-10-27 (`cs4b_proposal.md`); CS4c (22R inside each DRV135 loop) signed off and applied 2026-10-27 (`cs4c_proposal.md`).
  - *Why:* live patching (hot plugging, a phantom-powered lead, synth DC). 48 V through 6K8 into J1 gives about 7 mA
    through the 220R into U16's internal ESD diodes, near the OPA1656's rating.
  - *Proposed:* a low-leakage dual diode (BAV199-class; a BAV99's leakage into the 1M legs would shift DC) to the rails
    at J1's legs after the 220R, the insert return, and the direct-out and insert-send pins.
  - *Master:* DRV135 outputs to be checked against TI's protection notes.
  - *Cost:* about 4 SOT-23 per strip.
- [x] **CS5 PFL-bus crosstalk measures: checked 2026-10-27, no change** (`sim/review/cs5/pfl_xtalk.py`, output in
  `pfl_xtalk.out`).
  - *The model:* one wing of the motherloom (14 segments), conductors 25-31, 2.5 pF to the next conductor per segment as
    `sim_console.py` and an estimated 0.4 pF to the one after. The master's PFL summer and PFL DET network are as built;
    strip 1 is pressed.
  - *Why it is quiet:*
    - every bus on the ribbon (MIX, SUB, AUX, PFL) is a virtual earth at its summer, so its conductor carries almost no
      voltage;
    - the PFL bus (27) lies between GCANCEL (26) and pin 28, and PFL DET (29) is held by the master's 1 µF.
  - *Results:* against a PFL path floor of about −93 to −97 dBu (the strip's PRE noise, EQ in):

    | Into the PFL sum | as built | (b) pin 28 on GNDA | (c) PFL DET at a virtual earth |
    |---|---|---|---|
    | AUX2 at 0 dBu, 20 kHz | −105 dB | −105 dB | −105 dB |
    | −V, 10 mA AC per strip (a hard worst case) | −122 dBu | −202 dBu | −122 dBu |
    | A key press (PFL_ON 0 → 5 V in 1 µs), peak | −94 dBu | −105 dBu | −121 dBu |
    | (a) 1 mA AC on every strip's +VL, 1 pF per key | −104 dBu | | |

  - *Verdict:*
    - **(a)** can't help: +VL is already 10R / 47 µF at every key, so a local 10 nF changes nothing.
    - **The press click** coincides with the DG413's own switching click (−70 to −89 dBu, `sim/review/pflswitch`).
    - **(b)** is the one free option: a wire from CN2 / CN3 pin 28 to GNDA on the master, no part. It isn't needed.
  - *The three items as surveyed:*
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
- [x] **CS6 Per-strip fusible supply feed.** Signed off and applied 2026-10-27 as strip v5.3 (`cs6_proposal.md`): Vishay
  M25SI 10R 1206 for R1-R4 on every strip and group; power the console down before plugging a module.
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

## 7. Second batch: the consoles in Downloads (2026-10-27)

Same method and reference card (strip v5.0). These are smaller desks and one large one without circuits. None shows our
design weaker than common practice; the findings below either confirm it or add two cheap protections and a measurement.

### What they confirm

| Topic | Second batch | Ours |
|---|---|---|
| Line input | **No separate line receiver in any of them.** Line reaches the mic pre through a resistive pad (GL2 8K2 / 4K7, GL3300 10K per leg, Mackie VLZ 10K / 1K3, Yamaha MC 20 dB, E8 4K3 / 1K2) | Buffered receiver, 1 MΩ legs: still the only one that keeps CMRR against a synth's output impedance |
| Fader + post-amp | **"0" 10 dB down, then about +10 dB:** GL2, GL3300, Mackie (NJM4560, 1K1 / 510), Yamaha MC (10K / 4K7), E8 (+10.5 dB) | The same; the gain structure is industry standard |
| Fader shut-off | **GL2 and GL3300 inject an anti-phase copy of the fader top into the post-amp's ground leg** ("FADER SHUTOFF COMPENSATION", GL3300 C3100: 100K into 10R, J9 to disable) | Nothing; see CS9 |
| Mute | Mechanical in the path (GL2, Mackie, Yamaha MC, E8); GL3300 J111 shunts with a 10 ms ramp and four mute groups | J112 soft mute, also on pre sends: ahead of all of them |
| Pan | Passive, unbuffered (GL2, GL3300, VLZ, Yamaha MC, E8: −3 dB pan-taper duals); the 8•Bus buffers like ours | Buffered, −6 dB (CS2 is about the law, not the buffer) |
| Routing | Mechanical keys switching the resistor's bus end (GL3300) or source end (GL2) to ground | DG413 at the bus end; the key carries logic only |
| Summers | DC block in series with the summing node (GL2, GL3300, Yamaha MC, E8 on aux / solo) | Coupling at each source; a summing-node cap would fight ground cancel |
| Bus ground | **Mackie VLZ: one ground-sense line per bus** (G-MAIN, G-AUX-n, G-SUB-n), 510 Ω from each channel, summer + input on it; GL2, GL3300, Yamaha MC, E8: local ground only | One GCANCEL line for every summer, 10 Ω per strip, and re-inverters |
| Channel OL | Multi-point on GL2 (3 taps), E8 (4 taps: preamp, insert return, EQ, post-fader), 8•Bus (3 taps); single point on the 1604-VLZ, GL3300, Yamaha MC. **All positive half only**, holds 0-22 ms | 5 taps, both polarities, ~150 ms hold (v5.0) |
| Master meters | Precision rectifier into a series LED string with one current source and a comparator per LED (GL3300, 1604-VLZ, E8) | The same architecture |
| Outputs | Cross-coupled op-amp pairs (GL3300, GL2200, Yamaha MC), SSM2142 (GL2), impedance-balanced (E8); **no mute relay in any** (Yamaha MC has a transistor shunt at the master fader) | DRV135 + relay with power-on delay |
| Power | 10R + 47 µF per rail per board (GL2, GL3300, "PF" fusible on the GL3300), separate LED rail with its own ground (1604-VLZ), **reverse diodes on each rail of every board** (GL2 1N4002) | 10R anti-surge + 220 µF; no reverse diodes on the strips (see CS10); fusible feeds already CS6 |
| Levels | Internal −2 dBu (GL2, GL3300), +4 dBu (AMEK big, 17 dB headroom), about 0 dBu (Yamaha MC, Mackie) | 0 dBu, 23 dB to clip |

### Proposals (not applied; for sign-off)

- [ ] **CS9 Fader shut-off compensation, if the sample needs it** (GL2, GL3300).
  - *What:* a resistor from the fader top (MUTEOUT) into a few ohms under R38 in U2A's ground leg. The anti-phase
    copy cancels the residual that the fader's end resistance leaks at the bottom stop.
  - *Numbers:* the GL3300's 100K / 10R cancels about −83 dB, i.e. ~0.7 Ω of end resistance on 10K. The spread of end
    resistance limits the gain to perhaps 10-20 dB.
  - *First:* measure a PTB0143's residual at the bottom stop (`sample_order.md` check 9). Propose values only if it is
    worse than about −80 dB. Then sim U2A's stability with the added ground-leg resistor.
- [x] **CS10 Reverse-biased diodes on each rail of every strip / group board** (GL2: 1N4002 per rail per board). Signed off and applied 2026-10-27 (strip v5.1, `cs10_proposal.md`).
  - *Why:* if a wing loses one rail (a PTC trips, a ribbon conductor opens), the op-amps can drag that rail past
    ground. A strip's C3 is a polar 220 µF on −VA and C1 one on +VA.
  - *Today:* the master has SS54 clamps at its supply entry, but nothing on the strips or groups.
  - *Proposed:* two Schottky or 1N4002-class diodes per board, after R1 / R2, cathode to +VA / GNDA, anode to GNDA /
    −VA.
  - *Cost:* about 2 parts per board, placed by `moves_only`.
- [x] **CS11 Jig test additions** (AMEK big's test protocol, Mackie's per-bus ground) — `test_jig_spec.md` only. Signed
  off and applied 2026-10-27 as tests 13-17 in `test_jig_spec.md` v0.9 (`cs11_proposal.md`). Its follow-up, matched DRV135
  couplers for output balance, signed off and applied 2026-10-27 (`cs11b_proposal.md`):
  - output balance of the DRV135 outputs with matched 1 kΩ legs;
  - a measured line-input CMR with a 0.01 %-matched 100 Ω pair, plus the 1 kΩ-unbalanced case our 54 dB claim rests on;
  - fader breakthrough and pan isolation;
  - mix noise at N = 4…24 with faders down (comparable with the published figures in §2);
  - the current in the GCANCEL conductor with four strips (our 10 Ω against Mackie's 510 Ω per channel).

**Considered and not proposed (second batch):**
- **A removable 10 Ω between the console star and chassis** (AMEK): conflicts with the signed G1-G3 grounding. Worth a
  note only as a hum-hunting option, after the jig.
- **Mackie's per-bus ground-sense lines:** needs conductors the 34-way loom doesn't have; Sony's version was declined
  the same way (§5).
- **Mute groups on the spare ribbon pins** (GL3300): no panel room for group keys on an 8 HP strip.
- **The 8•Bus's 20 Ω + 220 pF on the summing node:** only if the jig shows RF or ringing; our sim is clean to 2.2 nF.
- **Wiper-fed aux pots, a global pre / post, A+C taper pan, a JFET-mute null resistor, the discrete cross-coupled
  output:** each either needs the unbuffered topology we don't have, or (the cross-coupled driver) is a fallback to keep
  on file in case the DRV135 goes.

## 6. Correction made

`master_section_spec.md` §3 said "The Delta does the same job with differential receivers on MIX L+/L−". The Delta
DLX drawing (ED2780 sheet 1) shows those receivers (IC7, 43K / 20K / 22K) under MONITOR SELECT. They are fed from the
balanced mix outputs and have nothing to do with ground cancel. The Delta's mix summers reference local ground; only
its aux summers take GND CANCEL. The spec line is corrected. Our design and its no-tie decision are unaffected.
