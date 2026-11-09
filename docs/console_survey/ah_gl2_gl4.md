# ah_gl2_gl4: Allen & Heath GL2 (and GL2200), compared with goa-console

## 1. Header
**Document:** `~/Downloads/326862669-ALLEN-HEATH-GL2-GL4-Service-manual-127-pdf.pdf` (127 pages, scanned, no text layer). It is a
compilation, and the pages are not in manual order. PDF page numbers below.

**What it contains**
- **GL2 / GL2-S service manual** AP0179 issue 2 (1995), schematics dated 1993. All read at 220-450 dpi:
  - p.3: GL2 block diagram.
  - p.5: input (mono) D222.
  - p.7: stereo input D223.
  - p.9: group sheet 1, D224.
  - p.10 top: group sheet 2 (monitor meter, main L/R output driver, rails).
  - p.12-13: master D225 sheets 1 and 2.
  - p.14: contents. p.15: technical description. p.16: specification and connections.
  - Also in the PDF, not read in detail: GL2-S return and LR sections (p.115-127), Sys-Link expander (p.27-40).
- **GL2200 service manual** AP3389 (1999) and user guide AP3388. GL2200 is the GL2's successor.
  - Read: specs (p.53), input C3395 issue 5 (p.62), left master C3426 (p.70), user-guide channel page (p.98).
  - Used only to show what A&H changed six years later.

**Missing**
- **GL4:** no GL4 document is in the PDF. It appears only in the title of the fader-fitting note (p.1). Nothing below is about the GL4.
- **Power unit:** the GL2 power unit circuit D226 and wiring D247 are listed in the contents (manual p.66-68) but are not in the PDF. The GL2200 PSU C3504 is not there either.
- **Meter PCB:** the GL2 meter driver is on the group board (p.10). The master meter LED board is not shown.
- **Reference:** "vs ours" lines refer to the reference card `our_design.md`.

## 2. Published specs
**GL2 / GL2-S (p.16):**
- Levels and headroom:
  - Internal level −2 dBu; internal headroom +23 dB.
  - Max out: balanced +27 dBu into 600 Ω; unbalanced +21 dBu into 2 kΩ.
- Indicators: peak LEDs on 5 dB before clipping; SIG LEDs (GL2 only) "dynamic", on from −20 dBu.
- Rails: ±16 V 0.5 A, +48 V 0.05 A, internal linear PSU, 40 W max (p.15-16).
- Noise, 22 Hz-22 kHz:
  - Mic EIN −127.5 dB (150 Ω).
  - Line pre-amp at 0 dB: −88 dBu.
  - Mix noise −85 dB re 0VU (+4 dBu); the number of channels routed is not stated.
- Other:
  - THD 0.01 %, line in to mix out, 1 kHz.
  - Frequency response 20 Hz-20 kHz +0/−1 dB.
  - Crosstalk / isolation at 1 kHz: output mute >98 dB, channel mute >88 dB, fader shut-off >88 dB.
  - No CMRR figure.
- Line in 10 kΩ balanced (XLR or TRS), −40 to +10 dBu. Stereo in 20 kΩ, −20 to +22 dBu. Insert −2 dBu. Outputs 50-75 Ω.

**GL2200 (p.53):**
- Headroom +21 dB. Line in to L-R THD+N 0.008 % at +14 dBu. CMRR >88 dB (mic, 40 dB gain).
- Line pre-amp noise −90 dBu at 0 dB gain. Measured RMS in a 22 kHz bandwidth.
- L-R output:
  - Residual −94 dBu.
  - Faders at "0", nothing routed: −90 dBu.
  - **16 channels routed: −84 dBu (88 dB S/N).**
- Group mix, 16 channels routed: −84 dBu.
- Crosstalk: fader off −90 dB, mute −90 dB, pan −80 dB.

**Against ours:** ours is −79 dBu at main L with 24 strips routed, faders at "0", against −0.8 dBu nominal (about 78 dB).
- Scaled to 16 channels that is about −81 dBu, about 80 dB.
- GL2200 quotes 88 dB re +4 dBu, but A&H don't say where the faders sit, so the two aren't strictly comparable.

## 3. Per topic

**T1 Line receiver.** **Read** (D222 p.5):
- **No separate line amplifier.** The line jack (and the XLR when PAD/LINE is pressed) reaches the mic pre-amp through an 8K2 / 4K7 / 8K2 pad (1 %), about −13 dB. 47 µF electrolytic couplers sit in each leg ahead of it.
- The pre-amp is a discrete 2N4403 PNP differential pair:
  - 8K2 / 4K7 collector and emitter resistors, gain set between the emitters by 68R + 10K-C gang + 220 µF.
  - The collectors are AC-coupled (47 µF) into a TL072 differential stage (8K2 / 8K2, 22p).
  - A second TL072 stage follows; the other gang of the gain pot (10K-C, 4K7, 1K5) is in its feedback.
- Stereo inputs (D223 p.7) are unbalanced in the schematic: ring and sleeve both go to 0 V. This contradicts the "balanced" line on p.16. The input goes to a 20 kΩ attenuator pot (180R foot) and a TL072 non-inverting +19.3 dB stage (15K / 1K8).
- vs ours: different. CMRR rests on 1 % pad resistors and electrolytics in the legs, with no buffering. Our follower-buffered receiver is clearly better for synths. Their unbalanced stereo input is weaker still.

**T2 Line gain.** **Read:** dual-gang gain through the mic pre (line −40 to +10 dBu nominal). Stereo uses an attenuator pot ahead of a fixed +19 dB stage.
- vs ours: different. Ours is a ±15 dB stage with a detent, which suits line sources better.

**T3 Ø.** GL2: none (D222).
- GL2200 **read** (C3395 p.62): a PHASE switch swaps the legs ahead of the 2N4403 pair. Same as ours.

**T4 HPF.** GL2: none on D222.
- GL2200: fixed "100 Hz 18 dB/octave" lo-cut after the pre-amp (p.98). **Read:** 330 nF + 47 nF + 47 nF around a TL072 follower, switched (C3395).
- vs ours: ours is a sweepable 12 dB/oct HPF. Ours is more flexible; theirs has a steeper slope.

**T5 EQ.** GL2 (**read**, p.5):
- HF / LF shelves around TL072 sections: 20K-B pots, LF 0.33 µF / 2K2 / 100K.
- Two swept mids with 200K-C dual rheostats: 35 Hz-1 kHz and 500 Hz-15 kHz.
- EQ IN switch.
- Not compared further (docs/studies/eq_survey.md).

**T6 Insert.** **Read:** channel insert **pre-EQ** (post pre-amp).
- Send: TL072 output via 47 µF + 47R.
- Return: on the ring, normalled by the jack contact. It goes through 47 µF straight into the EQ's 47K input network, with no buffer. −2 dBu.
- Master L/R insert: the send is buffered by a unity TL072 inverter (15K / 15K, 47R); the return goes 47 µF to the fader top (D225 p.12).
- vs ours: ours is post-EQ, with a buffered return and RF/stability network. Different, and ours is the better choice for synths.

**T7 Mute.** GL2 **read:** a mechanical push switch (S8):
- one pole in series after the post-fader amp's 47 µF coupler, grounding the pan input when muted;
- a second pole switches the red mute LED;
- a third pole grounds the pre-fade aux feed (link J8 "POST-MUTE", default) and the post-mute direct out (J27).
- GL2200 moves the mute to the fader top (S7 series, grounding when muted), so pre (post-mute) and post sends die together.
- vs ours: same intent; ours also mutes the pre sends. Our J112 soft mute avoids their switch click.

**T8 Fader / post-amp.** **Read** (p.5):
- Fader RV15 10K-A feeds TL072 non-inverting +9.9 dB: 10K / 4K7, 22p, 47R wiper stop, 15K wiper load. "0" is 10 dB down, as ours.
- **Fader-off cancellation:** R80 68K runs from the fader top into R34 10R, which sits in the gain stage's ground leg.
  - That injects −3.1e-4 × V_top in anti-phase, cancelling a fader residual of about −80 dB (**inferred** from the values).
  - Group and master use the same idea (**read**, p.9, p.12): R31 / R86 150K from the fader top into a 10R at the + input of an inverting 5532 post-amp (15K in, 47K feedback).
  - Spec: fader shut-off >88 dB (GL2), −90 dB (GL2200, which uses a special "10KD" fader).
- vs ours: same gain structure. We have no residual cancellation (see §4).

**T9 Pan.** **Read:** passive 10K-AC dual, centre to 0 V. The wipers drive the 22K routing resistors directly, with no buffer, so the load changes with routing.
- Stereo channel: the same pot as balance, with 18K routing resistors.
- Group to mix: 20K level pot → 10K-AC pan → 8K2 into L/R mix.
- vs ours: we buffer the wipers. Theirs has a routing-dependent pan law; ours is better.

**T10 Aux.** **Read:**
- 6 × 20K pots (marked "20KK"), wiper → 22K → bus, no wiper coupler.
- Per-send links P / S / A (pre, switched, post); one PRE switch for 1-4 and one for 5-6.
- Pre-fade source by link: pre-EQ / post-EQ (J5 / J6) and pre-mute / post-mute (J7 / J8).
- Aux masters (p.9 / p.12): 5532 virtual earth 22K / 22p → 20K level pot → TL072 inverting +9.9 dB (15K / 47K) → unbalanced jack, 47R. SSM2142 balanced option by links.
- GL2200 uses 8K2 send resistors.
- vs ours: similar. We have a PRE per pair and a film coupler at the wiper.

**T11 Routing.** **Read** (p.5, zoomed on p.7):
- Mechanical latching switches at the **source end**: the off position grounds the summing resistor (22K mono, 18K stereo).
- So the bus noise gain is constant, as ours, but the switch is at the source end. Our sim gives THD −67 dB at the source end against −124 dB at the bus end.
- GL2200: L/R resistors 10K, groups 22K.
- vs ours: our DG413 at the bus end is better for crosstalk and THD.

**T12 Mix bus summing.** **Read:**
- Group, L/R, AFL and PFL: NE5532 virtual earth, + input on local 0 V, 22K / 22p feedback (PFL / AFL 12K).
- **220 µF/10 V in series between the bus and the summing node** on group, L/R, PFL and AFL (not on aux). The amp's DC noise gain is then 1.
- GL2200 adds a ferrite bead (FB1-FB4) in each bus line before the 220 µF, with feedback 8K2 / 100p or 12K / 22p (C3426 p.70).
- vs ours: same topology. We already have the ferrite; we have no series DC block and use OPA1612.

**T13 Bus ground.** **Read:** no ground cancel; the summing + inputs go to master 0 V.
- Ribbon pins 3 and 4 carry 0 V; pins 2 and 26 carry chassis.
- A soldered copper-wire busbar across all boards carries the "connector earth" (jack sleeves, E1 / E2).
- Each board links it to its audio 0 V (J4 / J1 / J30). A ground-lift switch on the PSU separates 0 V from mains earth (p.15).
- vs ours: we use ground cancel plus a star wire per strip. Ours is better on a 24-strip frame.

**T14 AC coupling.** **Read:** 47 µF/25 V polar electrolytics with 100K bleeders after every stage feeding a pot or the bus. 220 µF at the summing inputs.
- vs ours: theirs is cheaper. Ours (NP MUSE + film at the wipers) is better.

**T15 PFL / AFL.** **Read:**
- The PFL switch connects a 22K from the fader top to PFL_MIX; this is pre-fade and pre-mute.
- A second pole pulls PFL_DC low through 15K + 1N4148. The same line lights the channel's PEAK LED as a PFL indicator (D7 / R55).
- Master (p.13):
  - BC214C PNP detectors with 4K7, 560R + 1 µF filter on the PFL_DC / AFL_DC lines; PFL has priority over AFL.
  - 4053 CMOS switches on a local ±7.5 V supply select the monitor source.
  - PFL / AFL mix amps are 5532s with 220 µF series caps.
- vs ours: same scheme; we use DG413 and a debounced PFLDET. Their shared PEAK / PFL LED saves an LED.

**T16 Direct out.** **Read:** optional jack, unbalanced, 47R (GL2200 33R) from link-selected pre-fade / post-fade pre-mute / post-mute.
- vs ours: ours is impedance-balanced. Ours is better.

**T17 Master outputs.** **Read:**
- L/R: 5532 sum → insert → fader → 5532 +9.9 dB → mechanical mute → SSM2142 (+6 dB, 47 µF in, 47 µF/25 V in each output leg with 100K bleeders), 0 dBu internal to +4 dBu (p.10).
- No output relay, no power-on mute.
- Mono: L+R sum (27K / 27K into 6K8, −12 dB) → level → +13 dB → SSM2142.
- GL2200 **read** (p.70): the SSM2142 is replaced by a cross-coupled 5532 pair (10K / 4K7 1 %, 47R).
- Phones: TL072 inverting (3K3 / 47K) into a BC549 / BC214C class-AB follower, 10R emitter resistors, 1N4148 bias, 100R per output.
- vs ours: ours (DRV135 + relay with power-on delay) is better.

**T18 Meters / LEDs.**
- **Channel peak (read, p.5):**
  - Three taps (pre-amp out, post-EQ, post-fader amp), each 22K + 1N4148, positive half only.
  - 1.5 nF to −V, 10M bleed: about 33 µs attack, 15 ms decay.
  - TL072 used as a comparator: threshold 22K / 15K from +V (≈6.5 V, i.e. ≈7.1 V peak ≈ +16 dBu), 100K hysteresis, red LED via 12K. Block diagram: "on 5 dB below clip, 3 point detect".
  - Stereo: two taps.
- **Group / master (read, p.9 / p.12):**
  - LM339 PEAK (red) and 0 dB (green) from a 22K + 1N4148 + 2.7 nF / 10M detector.
  - SIG: a TL072 at a gain of 45 (1M / 22K) drives a green LED against a mid-rail 4K7 / 4K7 divider, so brightness follows the signal.
- **Bargraph (read, p.10, p.13):**
  - TL072 half-wave precision rectifier (47K / 330K, ×7), 1K8 + 1 µF.
  - Eight-LED −20...+6 series string fed by one BC214C current source; each LM339 shorts the LEDs above the level. Same principle as our master meters.
- **GL2200 channel (read, p.62):**
  - Four-segment series string (SIG / 0 / +6 / PEAK) from one 12K resistor.
  - Two detectors: 39K + 150 nF slow, 33K + 2.7 nF fast.
- vs ours: our strip OL already does five taps, both polarities, 150 ms hold. Their 15 ms hold is too short to see. Theirs is weaker.

**T19 Power.** **Read:**
- Internal linear ±16 V / +48 V supply. On the ribbon: −16 V pin 7, +16 V pin 9, 0 V pins 3 / 4. The input sheet also marks 8 −V / 10 +V, so the rails are probably paired (**inferred**).
- Each channel: 10R + 47 µF/25 V per rail.
- Group / master split ±VA (audio), ±VB (LEDs / comparators) and ±VC (output drivers / meter), each 10R + 47 µF.
- **1N4002 from each rail to 0 V, reverse-biased**, on the group and master boards.
- vs ours: same 10R RC split; we add a separate logic ground and the star wire. We have SS54 clamps only at the master entry, not per strip.

**T20 Op-amps.** **Read:** TL072 everywhere in channels; NE5532 on summing and group / master post-amps; LM339 meters; SSM2142 outputs; 4053 switching; 22 pF compensation; 47R build-outs.
- vs ours: ours is quieter and better specified.

**T21 Levels.** −2 dBu internal, +23 dB headroom (TL072 on ±16 V). Ours: 0 dBu and +23 dB.
- vs ours: equivalent.

**T22 Construction.** **Read** (p.15):
- 19" 11U steel front panel with individual channel PCBs hanging from it.
- Connectors on the boards, rear-mounted.
- 26-way plug-on IDC harness for buses and power; soldered copper busbar for earth.
- Removable PSU module.
- vs ours: the same idea (per-channel board, IDC ribbon, heavy separate earth).

**Not covered by the documents:** PSU internals, the GL4, and CMRR / crosstalk circuit measurements. For the GL2200 only the four pages above were read.

## 4. Worth considering for goa-console
1. **Fader-residual cancellation (T8).**
   - What: one resistor from the fader top (MUTEOUT) into a small resistor (~10 Ω) under R38 in our post-amp's ground leg. Value set so the anti-phase injection cancels the PTB0143's end-of-track residual.
   - Why: A&H got 88-90 dB fader shut-off from a plain 10K fader with this. It only matters with the channel ON and the fader down, but that is the usual way to park a synth.
   - Cost: two 0805s per strip.
   - Check: the cancellation is only as good as the end-resistance spread. Measure the PTB residual on the fader samples first, then sim (`sim_netlist.py`) and check U2A's stability with the 10R in the leg. Fits a line console.
2. **Reverse-biased rail diodes per module (T19).** A 1N4002 / SS14 per rail on every strip / group board, after the 10 Ω.
   - Why: if one rail fails or a ribbon is misplugged, the other rail can pull the dead one through the op-amps' substrate, and the 220 µF caps see reverse voltage.
   - Cost: two SMA diodes per board.
   - Fit: cheap insurance at 29 modules on one ribbon. The SS54 at the master entry doesn't protect a strip whose own fused feed opens.
3. **Op-amp cross-coupled balanced driver as a DRV135 fallback (T17).** The GL2200 dropped the SSM2142 for two 5532 halves (10K / 4K7 1 %).
   - Why: our outputs depend on one TI part family. THAT and SSM drivers have already gone EOL.
   - Cost: none unless needed. Keep the topology on file, sim-checked, as a footprint-compatible plan B.
4. **Series DC block at the summing node (T12).** Not recommended. It conflicts with ground cancel: GCANCEL references the + input, and a series cap only fixes DC that our per-node NP couplers already remove. Noted so it isn't re-proposed.
5. **Shared PEAK / PFL LED (T15).** Their channel PEAK LED also shows PFL. We have separate LEDs; nothing to gain. Listed only because it is the one panel-economy idea here.

**Where ours looks weaker:** nowhere obvious. The GL2 is a 1993 budget design (TL072, electrolytics, source-end routing, passive pan, no output relay). Its only ideas we lack are items 1 and 2.
