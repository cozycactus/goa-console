# Master Section — Schematic Specification, v0.12 (draft)
## Part 1: stereo mix path, mono, main outputs, power-on mute
## Part 2: subgroups, aux masters
## Part 3: stereo returns · Part 4: monitoring · Part 5: power entry

**Jack-link clamps (2026-10-27, `cs4b_proposal.md` CS4b, signed off).** As the strip's D18-D22 (strip spec v5.2): a
Nexperia BAV199 on every signal of the jack-board link, at the main board's header, ahead of every series part. Pin 3
goes to the signal, pin 2 to +VA, pin 1 to −VA.
- **Master:** D79-D102 at CN5. EXT legs, the mix inserts' sends and returns, main L / R / mono (relay side), aux 5 / 6
  and C/Room legs, phones.
- **Group:** D7-D20 at CN3 / CN4. Return 1 and 2 legs, sub insert, sub and aux out legs.
- **Made by:** `master_lib.link_clamps()`, last, so no other ref moved.
- **Phantom on a DRV135 output:** the clamps hold a leg at 17.7 V instead of 47.7 V on its 10 µF 25 V coupler and Sense
  pin. The no-phantom rule (§7) still holds.
- **ESD:** an 8 kV contact discharge into a DRV135 output pin drops from 22.8 A to 5.9 A; a receiver or insert return
  drops to ~0.1 A or less (`sim/review/cs4/jack_protect.py`, `jack_protect_mg.py`).
- **Open (CS4c, `cs4c_proposal.md`, not signed off):** 22 Ω inside each DRV135 loop takes the output pin to 0.84 A
  (TI model: no loss of stability; +21 Ω differential output impedance, 0.16 dB into 600R).

Written to the same rules as `channel_strip_schematic_spec.md`; whole-console context is in
`console_architecture.md` section 4. Part 2 starts at section 12, Part 3 at 16, Part 4 at 17,
Part 5 at 24. Open items are in section 29.

**Modules (2026-10-22, `master_panel_study.md` M1).** The master section is built as five boards on the
ribbon. Four identical 8 HP **group modules** (`group.kicad_sch`, `tools/gen_group.py`) each carry one
subgroup (§12), one aux master (aux 1–4, §13) and two stereo returns (§16; the second since v0.12). Solder jumpers pick which
SUB and AUX bus a group sums, and each group buffers GCANCEL locally for its re-inverters. Groups have
strip-style power and grounds (10 Ω + 220 µF, spade, 10 Ω to GCANCEL; since 2026-10-27 a PMEG4010CEH reverse clamp
across each audio rail, D5 / D6, as the strip's D16 / D17, `cs10_proposal.md`). The 16 HP **master module**
(`master.kicad_sch`, `tools/gen_master.py`) carries everything else: power entry and both wing
headers, MIX L/R, master fader, mono, main outputs, power-on mute, aux masters 5–6, monitoring, PFL and
meters.

**Jack boards (2026-10-22).** As on the strip, ¼" jacks and XLRs need about 25 mm behind a panel that is
parallel to the board. So each module's panel connectors sit on a jack board under the panel, joined
by an IDC ribbon (`master_lib.jack` / `link_pins` / `jack_board`). Each jack's pair is adjacent, with a
ground after it; insert send and return are split by a ground; phones carry PHONESGND beside L/R.
Ribbon conductor = pin number; never 2 × 17, so a link can't be mistaken for the bus ribbon.
- Group: `group_jack_board.kicad_sch`, 7 × NJ6FD-V (sub out, sub insert, aux out, return 1 L / R, return 2 L / R),
  2 × 8 link (CN3 on the group board) and, since v0.12, a 2 × 5 link for return 2 (CN4). A single 2 × 13 is 43 mm
  long; the jack board's one free slot, right of AUX OUT between the jacks' pads, takes ~29 mm.
- Master: `master_jack_board.kicad_sch`, 9 × NJ6FD-V (MIX L/R inserts, EXT L/R, C/Room L/R, phones,
  aux 5/6 out) + 3 × Neutrik NC3MAV (vertical) main XLRs, 2 × 20 link (CN5 on the master board).
- The returns' and EXT's 100 pF RF caps and 1M stay on the main boards at the receivers. The strip
  moved its RF caps to its jack board; move these too if the jig shows RF pickup on the ribbon.

**Second return per group (signed off 2026-10-26, applied in v0.12; `feature_gaps.md` RET1).**
- **Circuit:** every group module carries a second stereo return, the same circuit as the first (§16). The console has
  eight returns.
- **Jack board:** two jacks more (a fourth row, RET 2 L / R at y 78) on a 38 × 93.5 mm board, with a 2 × 5 link of its
  own beside the 2 × 8. The main board starts at y 94.5.
- **Panel:** RET 1 / RET 2 knobs with their PFL keys at y 106 / 128; return 2's MIX / 1-2 / 3-4 keys at y 150; AUX at
  y 172. Return 1's routing keys stay in the routing row (y 274).
- **Cost:** per group +2 OPA1612 and +2 OPA1656, ≈ +30 mA per rail typical; ≈ +0.12 A per rail console-wide (§27).
- **Unchanged:** every existing part keeps its reference and connections.

**Design review (signed off 2026-10-25, applied in v0.11; `design_review.md` R1, R2, R4, R5).**
- **R1:** every balanced driver is a **TI DRV135UA**. The DRV134 comes only as DIP-8 or the 16-pin wide SOL-16; the
  SO-8 part, with exactly the pinout the symbol and footprint use, is the DRV135. Same datasheet (SBOS094B) and
  electrical table. "DRV134" below means the family.
- **R2:** the group's sub pan RV2 is the ALPS RK09L1240015, as the strip's RV8. The Alpha B10K dual with a detent named
  here before doesn't exist.
- **R4:** a silk "2" marks the pad 1/4 column of every PVA2 key.
- **R5:** documentation and BOM fixes (this file, CLAUDE.md, console_architecture.md); master C57 on the W7.2 film
  footprint with an orderable WIMA MPN.

**Ground and hum, part 2 (signed off 2026-10-25, applied in v0.10; `ground_study.md` §10, G2b / G3b).**
- **G2b:** every DRV134 TRS output's sleeve is on CHASSIS: group sub / aux out, master aux 5 / 6 and C/Room L / R.
- **G3b:** the group return and master EXT receivers are buffered like the strip's U16: OPA1656 followers, 1M per leg,
  220R in, the receiver's 100 pF at each + input (moved there from the jack line), 100R build-outs. That is two duals
  per stereo input.
- **Stability:** followers 53.1° on the fitted model (group deck, every returns state); the receivers and level
  buffers ≥ 69.8° (TI).
- **Normals:** the L jack's normals short an empty input.
- **Cost:** +78 mA per rail console-wide, 31 mA of it on each wing (§27).

**Wing power (signed off 2026-10-25, applied in v0.10; `wing_power_proposal.md` W1–W2).** Pin 34 (the Delta's +48 V)
is a third +V conductor on every header, and the +V wing PTCs are MF-RX250/72 (−V keeps the MF-RX185/72). The female
IDC sockets are rated 1 A per contact and the master end carries a whole wing: +V is now 0.45 A per contact typical,
0.83 A at the PTC's hold (§25, §27).

**Ground and hum (signed off 2026-10-25, applied in v0.10; `ground_study.md` G1–G3).**
- Harness (G1, §26): one 14 AWG wire per strip and group, tied under its wing's motherloom, down the master's edge
  strip to its wing's copper bar under the M4 star stud (two bars, fourteen 6.3 mm tabs each). The wires' loops with
  the ribbon's ground conductors drop from up to 800 cm² (wires on the tub floor) to at most 33 cm².
- Balanced-input sleeves on CHASSIS (G2): the groups' return L/R jacks and the master's EXT L/R jacks; each jack
  board's standoff holes are plated CHASSIS pads (group H1–H2, master H1–H3) that bond it to the panel. On the group
  jack board CHASSIS stays off the link (`link_pins(skip=)`); on the master it already reaches the star through the
  link for the XLRs' pin 1. Inserts and the phones keep GNDA; since G2b the balanced TRS outputs are on CHASSIS too.
- The strip's receiver gains input followers (G3, strip spec v4.4): +7.8 mA per strip and rail (§27). Since G3b the
  returns' and EXT receivers have them as well (§16).

**Parts review (signed off 2026-10-23, applied in v0.7).** The six parts proposed in v0.6 were reviewed in
`master_parts_review.md` (review sims in `sim/review/`):
- GCANCEL buffer kept, plus a 100K keeper (§3).
- Aux sums on OPA1612; PFL keeps the OPA1656 (§13, §18).
- 22 pF on every re-inverter, 100 pF across every level buffer's 4K7 (§3, §13).
- Six mute relays, phones included, with the line grounded through the NC contacts; LM393B (§8, §21).
- The J112 PFL switcher replaced by a DG413 (§17, §19).
- Meter current sources on SOT-223, LM2901B, GaP LEDs (§22).
- Sub AFL kept; a PFLDET clamp stops the back-feed into released keys' LEDs (§12, §19).

From the strip review (`strip_parts_review.md`, signed off 2026-10-23): every differential receiver (EXT, returns)
has 33 pF on both legs, and the master's +5VL has the BAT54W.

**Stability and ratings review (signed off 2026-10-24, applied in v0.8).** `master_group_review.md` (MG1–MG20)
simulated every op-amp stage with the manufacturers' models (TI OPA161x, OPA1656, TL072, DRV134; a fitted LME49600
macro) in whole-module decks; scripts in `sim/review/master/`, `sim/review/group/`. Applied:
- **EXT (§17):** the receiver outputs are EXT_BL/BR. They had been named EXT_RR, the R jack's ring net, so R read
  −12 dB and U17B oscillated with a source plugged in. 100R build-out from each receiver to its 47 µF.
- **Phones (§21):** the 100 pF goes from the OPA1612's output, not from PHO; 22 pF at the + input; the LME49600
  beside its op-amp. The composite was unstable at the pot ends.
- **Solo follower (§18):** 22 pF at the + input, 100R build-out (it oscillated with a key pressed).
- **Post-amps (§5, §12):** 10 pF at the + input, 47R build-out to the 220 µF.
- **Followers on pot wipers:** 10 pF in every level buffer (§13, §16) and on the group's pan buffers (§12); 22 pF on
  the C/Room followers (§20).
- **CRS followers (§19):** 100R build-out.
- **Inserts (§4, §12):** 1K + 100 pF at the return buffer's + input (as strip R99/C84), 75R build-out to the 220 µF,
  the PRE 47K beside the 220 µF.
- **Meters (§22):** the follower reads the peak diode's cathode, 1K → 220R, 22 pF across U3; 22 pF across the summer;
  a 470R build-out on the DET follower with the U3 feedback 10K on its pin side; TI TL072HIDR.
- **Placement:** every build-out resistor sits at its op-amp pin (`near()`).
- **Ratings:**
  - phones 2R2 (output and ±VP feed) in 2512, 1.5 W (§21, §25);
  - anti-surge 0805 for the mute pull-ups (R52/R48 then; now R58 4K7 MUTE_GO and R54 10K RAIL_OK, §8), the rude-solo
    3K3 (now R124, §19), the ±VA feeds (§25) and the insert-send 75R;
  - capacitor and semiconductor MPNs (50 V X7R / C0G ceramics).
- **Spec notes:** no phantom on any balanced output (§7); the gain changes (§5, §12); the group bus-select rule (§12);
  aux outputs unmuted (§13).
- **Kept by decision:** the wing PTCs stay MF-RX160/72 (§25; changed to MF-RX185/72 in v0.9); no mute relays on the
  aux outputs (§13).

**Wing PTCs MF-RX185/72 (v0.9, signed off 2026-10-24, `hpf_proposal.md` H4).** The strip's sweepable HPF (strip
v4.3) adds an OPA1612 per strip: a wing's typical +V load goes 1.16 → 1.25 A, which on the MF-RX160/72 would be 96 / 109 %
of hold at 40 / 50 °C. F1–F4 are now MF-RX185/72 (§25), same pads, fixed in place (`place_master.py`). The jig's master
stub keeps the MF-RX160/72 (4 strips).

**Film couplers and audio bipolars (signed off 2026-10-24, `film_np_proposal.md` F1–F4).**
- **Film:** every 2.2 µF wiper coupler (fader, aux 5/6, solo, C/Room, phones) and the meter's averaging caps are WIMA
  MKS2C042201K00KSSD PET film (THT, bottom side), not X7R.
- **Bipolar electrolytics:** Nichicon MUSE ES 25 V in the existing footprints: 47 µF → 33 µF (UES1E330MPM), 220 µF →
  100 µF (UES1E101MPM), 10 µF UES1E100MDM (now Panasonic ECE-A1EN100U, `sourcing.md` S1). The values in the diagrams below are the new ones.
- **LF response:** end to end, a strip's input to the main XLR is −3 dB at 2.3 Hz and −0.04 dB at 20 Hz.

Delta references: ED2780 sheet 2 (MIX SUM AMPS, MIX INSERT, FADER POST AMPS, BALANCED
OUTPUT AMPS, mono "GC O/P AMP") and sheet 1 (monitor-select differential receivers on MIX
L+/L−, master ground-cancel resistor).

---

## 1. Signal flow (one side; R identical)

```
MIX L bus (pin 18) ─ ferrite ─┬─ U1A summing amp, OPA1612, inverting, Rf 4K7 ∥ 100 pF
                              │    + input = GCANCEL (pin 26), direct
                              └─ output SUM_L  (= −Σ channels, referenced to GCANCEL)
SUM_L, GCANCEL_BUF ─ U1B differential re-inverter, unity, 4 × 2K2 0.1 %
                 output MIX_L (= +Σ channels, referenced to master AGND)
MIX_L ─ 75R ─ master insert send (tip) ─ [bus compressor] ─ return (ring, normalled to send)
      ─ 33µ NP + 47K ─ U2A buffer ─ 100µ NP + 47K ─ PRE_L
PRE_L ─ master fader (dual 100 mm, A10K) ─ 2.2µ film + 100K ─ U2B post-amp +10 dB ─ 100µ NP + 47K ─ POST_L
POST_L ─┬─ U4 DRV134 balanced driver (+6 dB) ─ mute relay (NO in series, NC grounds the line) ─ XLR male MIX L OUT
        ├─ mono sum (with POST_R)
        └─ to monitoring and meters (later parts)
```

Polarity: the strip is non-inverting, U1A inverts and U1B inverts again, so MIX_L is in phase
with the channel inputs. The re-inversion the architecture asks for is U1B.

## 2. Mix summing amp (U1A)

- OPA1612, inverting. Inverting input on the MIX L bus through a ferrite bead (0805, ~220 Ω
  at 100 MHz; the Delta uses FB1/FB2 in the same place). No series resistor: it would add
  noise multiplied by the bus noise gain.
- Feedback 4K7 1 %, the same value as the strip summing resistors (decision: 4K7 bus).
  100 pF C0G across it.
- Non-inverting input connected **directly** to GCANCEL (pin 26). A bias-matching resistor
  would add noise at the full noise gain; OPA1612 bias current × 4K7 is under 1 mV of offset.
- No DC-blocking capacitor at the bus input. Every strip feed is AC-coupled, so the DC gain
  of this stage is 1. (The Delta's 1000 µF there protects a discrete input pair.)

## 3. Ground cancel at the master

- U1A's output is −Σ(channels) + V(GCANCEL): it is clean when read **relative to GCANCEL**,
  not relative to master ground. U1B reads it differentially and hands a clean signal to
  master ground. The Delta has no equivalent on its mix: its mix summers reference local ground, and only its aux
  summers take GND CANCEL (one transistor base on the line, ED2779A). Its MIX L+/L− receivers (ED2780 sheet 1, IC7)
  are the monitor-select inputs fed from the balanced outputs, not ground cancel (`console_survey.md`, 2026-10-27;
  this line said otherwise before).
- U1B: unity-gain difference amp, inverting input from SUM_L, non-inverting input from
  GCANCEL_BUF. Four 2K2 0.1 % resistors (or a matched quad network).
- **GCANCEL buffer (an OPA1612 half as a follower; in the generated schematic it shares a package with the
  MIX L summer).**
  The master's five re-inverters (MIX L/R, aux 5/6, PFL) each load the line with 2K2 + 2K2:
  880 Ω in all. The line's source is 10 Ω / 28 = 0.357 Ω (24 strips and the 4 group modules,
  each with its own 10 Ω). Driven straight, the 880 Ω would be a tie to master ground: −37.7 dB
  of the master-to-strip ground difference at MIX with N = 32 bus sources (24 strips, 4 sub
  pans, 4 returns), −40.3 dB at N = 24. So one follower drives all the re-inverters'
  non-inverting legs (GCANCEL_BUF), while every summing amp's non-inverting input stays on the
  raw line, which then carries no current. Each group module has its own buffer for its two
  re-inverters (net GC_BUF, 2.2 kΩ). It costs no package but makes no measurable difference: the
  group's own 10 Ω already makes it one of the 28 contributors, and the load only shifts its
  weight by 0.45 %.
- Error budget with the buffer:
  - the buffer's own error is −118 dB at 50 Hz (TI OPA161x model);
  - the floor is the re-inverter's resistor match: four 2K2 0.1 % give −54 dB worst case and
    about −65 dB RMS, flat with frequency (ratio-matched 0.05 % / 0.01 % quads are the fix if
    the jig shows hum);
  - bus capacitance to master ground adds 2πf·C·4K7: 1 nF gives −31 dB at 1 kHz, a realistic
    50 pF gives −57 dB;
  - the summing amp's loop gain at noise gain 33 limits rejection to about −42 to −51 dB at
    10 kHz.
- **Layout rule.** The buffer's output goes straight to GCANCEL_BUF: no resistor outside the loop
  (10 Ω into 880 Ω would leak −39 dB, worse than no buffer), no capacitor, net ≤ about 50 pF
  (datasheet Fig. 19: about 20 % overshoot at 50 pF). If more capacitance is ever unavoidable,
  use in-loop isolation (47R output → load, 1K load → −IN, 220 pF output → −IN).
- **Re-inverter compensation.** Every re-inverter has 22 pF C0G 5 % across its feedback 2K2 and
  across the + leg's lower 2K2, the same value and tolerance on both legs so the balance holds.
  The op-amp's input capacitance against 2K2 leaves about 11° of phase margin without them
  (+15 dB peak at 15 MHz, TI model); with them there is no peaking, −3 dB at 3.3 MHz, and a CMR term
  of −102 dB at 1 kHz.
- **The master does not tie GCANCEL to its own ground.** Any tie pulls the line away from the
  strip grounds, and the bus noise gain (25 with 24 channels routed) multiplies that error.
  Simulated with a 22 Ω tie: a 1 V strip-to-master ground difference left −7 dB at the
  output. **Decided (October 2026): no tie.**
- **Keeper (decided 2026-10-23).** With no strip or group on either wing (master bring-up on
  the bench), nothing would hold the line, and the summers' bias currents would walk it out of
  range. A 100K from GCANCEL to master GNDA defines it: ≤ 125 mV with nothing connected, and a
  leak of −79 dB at N = 32, 25 dB under the 0.1 % match floor. It is a tie in name only.
- The master's own audio ground still reaches the strips through the spade/ground bar, as the
  architecture specifies. Only the GCANCEL line stays free of a master-end tie.
- One GCANCEL wire serves MIX L, MIX R, the four subs, the six auxes and PFL. Each of those
  summing amps references it directly, and each has its own U1B-style re-inverter fed from
  GCANCEL_BUF.

## 4. Master insert

- Neutrik NJ6FD-V, wired as the strip insert: send on tip through 75R, return on ring,
  ring normalled to send.
- Return: 33 µF NP + 47K bleed, then 1K + 100 pF C0G at the + input of an OPA1612 follower (U2A), then a 75R
  build-out, 100 µF NP + 47K to PRE_L (v0.8, `master_group_review.md` MG7).
  - The 1K bounds the input current from outboard gear driving an unpowered console: ≈ 9.5 mA at a +20 dBu peak.
  - The 100 pF keeps the follower stable with it (the 1K alone costs 25–45°).
  - The 75R isolates the follower from PRE and the fader-top wiper run: 75.6° with 47 pF, against 48° without.
  - Cost: −0.08 dB flat into the fader; +4 nV/√Hz at the return.
- Nominal level at the insert is the mix level (about 0 dBu with channels at their "0" marks).
  The Delta runs its insert at −10 dBV. Ours stays at console level, because the bus
  compressor is our own design and can be built for it.

## 5. Master fader and post-amp

- Fader: Bourns PTB0144-2010BPA103 (100 mm, dual gang, A10K, BP metal lever: 8 x 1.3 mm flat blade, as the strips
  and groups; the AP 4 mm-fork audio parts are factory-only, 2026-10-23). The dual-gang
  footprint is the PTB0143 one plus pins 1′ 2′ 3′ mirrored about the body centreline (same
  datasheet drawing). Wired with pin 1 = GNDA, as on the strips (A taper).
- Post-amp U2B: 2.2 µF film + 100K input, gain 1 + 4K7/2K2 = +9.9 dB, 100 pF across 4K7. Same as
  the strip, so the "0" mark (−10 dB travel) is unity through the master.
- v0.8 (MG4): 10 pF C0G from the + input to GNDA, and a 47R build-out at the op-amp pin before the 100 µF coupler (MUSE ES since v0.8).
  - With 100 pF across the 4K7 the stage is a follower above 339 kHz. The wiper's 1.3–2.5 kΩ against the input
    capacitance, plus POST's 337 mm run and the DG413's on-capacitance when MIX is monitored, left 2–21° of margin.
    With the fix it is ≥ 51°.
  - Cost: −0.094 dB flat. With the insert's 75R, the main path is about −0.18 dB below the v0.7 figures.
- 100 µF NP + 47K to POST_L.

## 6. Mono

- U3A: inverting sum of POST_L and POST_R, 10K inputs, 10K feedback with 100 pF.
  A centre-panned mono source arrives at −6 dB in each side, so mono gives 0 dB for it.
  A hard-panned source also gives 0 dB.
- U3B: unity inverter (10K/10K, 22 pF C0G across the feedback 10K for stability, review 2026-10-23) to restore
  polarity, then DRV134, relay, XLR.
- Optional mono fader is left out; mono follows the master fader.

## 7. Main outputs

- Driver: **TI DRV135UA** (the DRV134 family's SO-8 part; v0.11, R1) on every balanced output. **Decided October 2026**, replacing the
  THAT1646 chosen earlier, which THAT Corporation put on end-of-life on 1 September 2026
  (last-time buy closed 30 September). Both replace the Delta's cross-coupled NE5532 EBOS
  (ED2780 sheet 2, about 12 parts and a balance trim per output) with one IC.
- DRV134 (datasheet SBOS094B; TI lists it ACTIVE): +6 dB differential gain, and +6 dB
  single-ended with either leg grounded, so an unbalanced lead loses no level. ±4.5 to ±18 V,
  5.2 mA quiescent, output swing to within 2.5–3 V of the rails (about +27 dBu differential on
  ±17 V), 10K input impedance, OCMR 68 dB typical / 46 dB minimum, stable into up to 1 µF per
  output, ±85 mA short-circuit current. Output noise floor −98 dBu in 20 kHz, which adds
  about 1 dB to the mix output's −93 dBu differential.
- Pinout: 1 −VO, 2 −Sense, 3 Gnd, 4 VIN, 5 V−, 6 V+, 7 +Sense, 8 +VO.
- Connection, per output (TI Figure 29):
  - VIN from the stage before (POST_L, AUXn_OUT, …). It is a 10K load; every driving point is
    an op-amp output or a coupling-cap node that tolerates it.
  - Gnd (pin 3) to GNDA. 1 µF + 100 nF on each rail at the pins.
  - Each output leg: VO → 10 µF non-polar electrolytic → output node; the Sense pin connects to
    the output node, after the capacitor. The loop then removes the cap's effect and blocks the
    up to ±250 mV common-mode output offset, so there is no DC on the relay contacts or the
    connector.
  - The mute relay (where fitted) sits after the Sense connection. When it opens, the driver's
    loop stays closed and nothing swings to the rail.
  - Single-ended use: a TS plug in a TRS output, or pin 3 grounded on an XLR, grounds that leg.
    The datasheet asks for VO and Sense of the unused side both grounded. With Sense at the
    output node, a ground at the plug grounds both through the jack contact and a few cm of
    track.
- Output connectors: XLR male, Neutrik NC3MAV (vertical, on the master jack board) or panel-mount with flying
  leads, pin 2 hot. Shell to chassis.
- **No phantom on any balanced output** (main, aux 5/6, C/Room, and the groups' sub and aux outs; v0.8, MG15; since CS4b
  the BAV199 at the link holds a leg at 17.7 V if it happens). P48
  through 6.81K per leg forces the DRV134's Sense pins above V+ (its input protection conducting, beyond the abs-max
  input range) and silences the output. Phantom tolerance would need 50 V DC-blocking caps at the connector, outside
  the Sense loop.
- **Placement and routing (v0.8, MG10):**
  - Every build-out resistor sits at its op-amp pin, keeping the pin-side net pad-length: 22 pF between the pin and
    the resistor costs 4–10°.
  - With the build-outs, no master output net needs a length limit. GCANCEL_BUF takes no series R (66° with 47 pF).

## 8. Power-on / power-off mute

- Why a relay (review 2026-10-23): a DRV134 with its Sense loop is quiet when both rails rise
  together (≤ 5 mV), but with rail skew its amps run against the dead rail and step the output
  by 1.2–3.0 V common-mode and 0.2–0.75 V differential for 10–100 ms of skew. The two LRS-150-24s
  start independently, so skew is likely, and only a contact after the driver removes it. The
  Delta has no output relays (AC coupling and a C/R MUTE switch only).
- Contacts: Omron G6K-2F-Y DC12 (DPDT signal relay; Ag contacts with Au-alloy, bifurcated
  crossbar, 2 A carry; dry-circuit rated, failure level 10 µA / 10 mV). Now sold as Aratas
  (formerly Omron Components); Digi-Key Z129-ND, active (26-week factory lead time: buy early).
  Contact map: COM to the connector, NO to the driver's Sense node, NC to ground, on both legs of
  each output. A de-energised relay therefore shorts the line to ground instead of leaving it
  floating: idle balanced inputs see a defined line, and phantom or ESD has a path.
- Six relays: L and R mains need four poles (two relays), mono two (one relay); the control-room
  outputs add two (section 20), the phones one (section 21, NC to PHONESGND). Coil: 12 V version
  (datasheet: 9.1 mA, 1315 Ω ±10 %, ~100 mW; must operate at 80 % of rated, maximum 150 %). Each coil
  gets 560 Ω in series from +V (+17 V): the coil sees 11.9 V, +2 % to +26 % over must-operate across
  coil tolerance and a 70 °C coil, and 118 % of rated at the 19.7 V PSU fault peak. A 24 V coil would
  get only 71 % on +17 V, below must-operate. NPN low-side switch (forced beta 34), 1N4148 across
  each coil. Six coils draw about 55 mA.
- Control (simulated in `sim/mute.cir`; values as generated in `tools/gen_master.py`), LM393B on ±VL
  (34 V across the package, over the non-B part's 30 V recommended maximum):
  - Reference: BZT52C6V2 (SOD-123) fed from +V through 4K7 (VREF6 = 6.2 V).
  - Comparator A: +V through 56K / 47K against VREF6, trips below +13.6 V.
    Comparator B: divider 22K (to VREF6) / 51K (to −V) against GNDD, trips when −V rises above −14.4 V.
    Open-collector outputs wired-AND on RAIL_OK, 10K pull-up to +VL.
  - Timer: 2.2M from RAIL_OK into a 2.2 µF film capacitor (WIMA MKS2; an electrolytic's leakage
    would be comparable to the charging current near the threshold). A 1N4148 clamps it at
    −0.7 V, and a 1N4148 + 4.7K discharges it into RAIL_OK on a fault, so every restart starts
    from about 0 V.
  - Schmitt: third comparator, timer against VREF6, 22M hysteresis, 4K7 pull-up; then 4K7 to the
    MMBT3904 base. Fast release: 1N4148 + 4.7K from the base to RAIL_OK, with a 1N4148 clamp
    holding the base above −0.7 V.
  - The reset and fast-release resistors were 2.2K until 2026-10-23. Then, at a one-rail loss,
    one LM393 output had to sink 21.8–23.7 mA (pull-up + timer reset + fast release), over the
    non-B part's 20 mA absolute maximum. With 4.7K it is 12–13 mA, and the timing is unchanged
    (below).
  - The relay transistor sinks all six coils (6 × 9.1 mA).
- Simulated (`sim/mute.cir` v3, 2026-10-23: 4.7K resets, six coils; LM393 as an open-collector
  model that only works above 2 V of supply; coil inductance assumed 1 H):

  | Case | Result |
  |------|--------|
  | Power-up, rails in 50 ms | relays close at 2.80 s; worst coil current before that 7 µA (no glitch) |
  | Both rails collapse (17 → 0 V in 200 ms) | coils released 2 ms after −V passes −14.4 V; rails still ±14.2 V |
  | +V lost only | released at +13.4 V (−V still −17 V) |
  | −V lost only | released at −14.2 V (+V still 17 V) |
  | 20 ms dip to ±12 V | released in 1.4 ms; full re-arm, closes again 2.76 s after the dip |
  | Slow PSU ramp (2 s) | closes 2.82 s after +V reaches 14 V |

  The coil current then decays through the 1N4148. With the comparator at its minimum sink and
  the coil inductance up to 3 H, the contacts open within about 8.5 ms of a threshold crossing,
  the G6K's own release included. On mains-off the outputs first move 28–45 ms after a
  threshold, at the modelled 0.25 V/ms fall, so no zener is needed in the flyback path. Measure
  the fall rate with the real PSU and full load: a fall 4× faster leaves about 7 ms of margin.
  No relay beats a crowbar collapse, where the outputs move within 1.5 ms. Faults longer than
  about 8 ms re-arm the full delay. Not muted: the aux 1–6 and sub 1–4 outputs (sends and
  recorders) see the same skew steps; the root fix would be start-up tracking in the PSU.
- First draft (220K / 22 µF timer, 1M hysteresis, no series resistors on the reset diodes)
  failed in simulation: the 1M from the Schmitt output held the timer near 10.4 V, so the delay
  was over 3.6 s and very tolerance-sensitive; a brownout would also have left the timer at
  −16 V, giving a 5 s delay after short faults.

## 9. Simulation (`sim/master_mix.cir`, single-pole OPA1612 model, 40 MHz GBW)

24 channels routed, 4K7 bus, 0 dBu on one channel, hard-panned:

| Point | Result |
|------|--------|
| SUM_L (U1A out) | 0.0 dB, inverted (179.8°) |
| MIX_L (U1B out) | 0.0 dB, in phase (−0.2°) |
| POST_L, fader at top | +9.9 dBu |
| POST_L, fader at "0" mark | −0.3 dBu |
| Balanced output, fader at "0" mark | +5.7 dBu differential (driver modelled as an ideal +6 dB stage) |
| 1 V strip-to-master ground difference at MIX_L, ground cancel on, GCANCEL buffered, 13 re-inverters loading it (pre-M1), 1 nF bus capacitance | −71 dB at 10 Hz, −31 dB at 1 kHz: both the 1 nF × 4K7 term, not the buffer (review 2026-10-23, §3) |
| Same, the 13 re-inverters on the raw line (no buffer) | −31 dB at 10 Hz (post-M1, 5 re-inverters on the master: −37.7 dB) |
| Same, ground cancel defeated | +27.6 dB (bus noise gain 25 × the difference) |
| Bus capacitance 1 nF: SUM_L response | no peaking, −3 dB at 298 kHz |
| Bus capacitance 10 nF: SUM_L response | +0.09 dB peak at 141 kHz, −3 dB at 392 kHz |

The remaining ground-difference leakage at 1 kHz comes from the bus capacitance to master
ground (modelled as 1 nF; realistic is 20–65 pF, mostly the master trace and the ribbon's GND
neighbour). The resistor match in U1B was ideal in the sim; with 0.1 % parts the match sets the
floor at −54 dB worst case, about −65 dB RMS (§3; `sim/review/gcancel/gc_m1.cir`).

Noise, 20 Hz–20 kHz unweighted, OPA1612 (en 1.1 nV/√Hz, in 1.7 pA/√Hz):

| Channels routed | U1A alone | U1A + U1B (2K2) |
|----------------|-----------|-----------------|
| 1 | −111.3 dBu | −108.7 dBu (−106.5 with 4K7) |
| 24 | −100.4 dBu | −100.1 dBu (−99.7 with 4K7) |

At POST_L with the master fader at the "0" mark and 24 channels routed: −99.1 dBu
(mix-bus noise plus post-amp self-noise of −106 dBu). Channel noise from 24 open strips is on
top of this, as in the architecture's section 2.4.

## 10. Op-amps and parts (stereo mix part)

The U-labels in §1–§9 name functions (U1A summer, U1B re-inverter, U2A insert buffer, ...). The schematic's
references are assigned by the generator (`tools/gen_master.py`), differ from them and change when it is
regenerated. By function:

| Part | Function |
|------|----------|
| OPA1612 | GCANCEL buffer (shares a package with the MIX L summer), MIX L/R summers and re-inverters, insert return buffers, both fader post-amps (one package), mono sum and re-inverter |
| DRV134 | L, R, mono line drivers |
| LM393B ×1½ | rail sense (both halves of one package, wired-AND), timer Schmitt (half of a second, whose other half is the rude-solo flasher, §19) |
| MMBT3904 | relay driver, all six coils |
| Omron (Aratas) G6K-2F-Y DC12 ×3 | main output mute (L, R, mono); C/Room and phones add three (§20, §21) |
| Neutrik NJ6FD-V ×2 | master insert L/R, on the master jack board |
| Neutrik NC3MAV ×3 | main XLRs, on the master jack board |
| Bourns PTB0144-2010BPA103 | master fader |

---

# Part 2 — Subgroups and aux masters

(On the group modules, except aux masters 5–6, which are on the master module.)

Delta references: ED2778A (group output: group sum amp, group insert, group fader, post amp,
"GND-CANCEL OUTPUT AMP", SUB switch into the monitor pan and on to MIX L/R, PFL) and ED2779A
(aux masters: GROUNDCANCEL on the summing amp's reference input, master level, buffer,
ground-cancelling output amp, TRS output, AFL switch to PFL+/PFLDET with LED).

## 12. Subgroups ×4

Bus pins: SUB1 = 15, SUB2 = 13, SUB3 = 11, SUB4 = 9. Each sub is a full copy of the stereo
mix path's first half, plus a pan into the mix.

```
SUBn bus ─ ferrite ─ summing amp (OPA1612 A), Rf 4K7 ∥ 100 pF, + input = GCANCEL
         ─ re-inverter (OPA1612 B), 4 × 2K2 0.1 %, + leg from GCANCEL_BUF   → SUBn_MIX
SUBn_MIX ─ 75R ─ insert send (tip) ─ return (ring, normalled) ─ 33µ NP + 47K
         ─ return buffer (OPA1612 A) ─ 100µ NP + 47K ─ PRE_SUBn
PRE_SUBn ─ fader PTB0143 A10K (pin 1 = GNDA) ─ 2.2µ film + 100K ─ post-amp +9.9 dB (OPA1612 B,
           4K7 / 2K2, 100 pF) ─ 100µ NP + 47K ─ POST_SUBn
POST_SUBn ─┬─ DRV134 ─ NJ6FD-V TRS output (tip hot, ring cold, sleeve CHASSIS since G2b)
           ├─ pan pot ALPS RK09L1240015 B10K dual, centre detent (v0.11, R2) ─ pan buffers (OPA1612 A/B)
           │    ─ 100µ NP + 47K each ─ MIX switch (PVA2, A-B = on)
           │    ─ 4K7 1 % to MIX L / MIX R (switch off grounds the resistor's bus end)
           └─ AFL switch (PVA2): pole A 22K to PFL bus (off: resistor end grounded),
                                  pole B +VL → 100K → PFLDET, 4K7 → AFL LED (red)
```

- Gain: unity from bus to POST_SUBn with the sub fader at its "0" mark, the same as the
  strips and the mix.
- Into the mix: the pan, pan buffers, AC coupling and routing switch copy the strip
  (channel_strip_schematic_spec sections 9 and 10), so a sub is just one more 4K7 feed on the
  MIX bus. Stereo-pair use (1-2, 3-4): pan the odd sub hard left and the even sub hard right.
  The two sub faders are not linked.
- Each assigned sub adds 1 to the MIX bus noise gain, like a routed channel.
- AFL on subs is not in the architecture's list, but the Delta group module effectively has it,
  and it costs one PVA2, three resistors (22K, 100K, 4K7) and one LED. Kept (review 2026-10-23).
  - The Delta D203's "PFL" key belongs to the lower return, which is fed from the group's
    post-fader node unless RET is pressed (ED2778A; Tech Manual pp. 61–62). So in normal use it
    is an AFL of the group, but it goes dead in SUB mode.
  - Ours taps the same point, POST_SUBn: post-insert, post-fader, mono, pre-pan and pre-MIX
    switch. It works in every routing state and hears what both the sub output and the mix get.
  - Solo level at the fader's "0" mark is about −0.43 dB against a strip PFL (v0.8: −0.2 dB before the post-amp's
    47R and the insert's 75R, which cost −0.23 dB flat on the sub out, the MIX feed and the AFL). Pressing it moves the 22K's
    end between GNDA and a virtual earth, so the sub output does not change.
- **Ground note.** Since M1 the sub sits on a group module whose GNDA joins GCANCEL through its
  own 10 Ω, like a strip, so its feed into the MIX bus is referenced to one of the averaged
  grounds, not to master ground. The remaining master-referenced feeds into a bus are the
  master's own aux 5/6 AFL 22Ks: while pressed, they pass the master-to-strip ground difference
  into PFL at 0 dB. Measure on the test jig.
- No mute relay on the sub outputs (they feed recorders and processors, not speakers). Add
  one later if wanted.
- **v0.8 (MG4, MG5, MG7, MG10):**
  - The sub's post-amp and insert return are `post_amp()` / `insert()` with the master's fixes.
  - 10 pF C0G on the pan buffers' + inputs.
  - Routing: the 47R and 75R at the op-amp pins, so S_FPOST and SUB_RBUF stay pad-length. Keep A_MIX/A_PT,
    RT_BL/BR + RT_RTNL/R, RT_PREL/R, S_MIX and GC_BUF within ~40 pF of the placement estimate (thin traces, not
    over long double-sided pour). S_POST and S_PRE are behind the build-outs.
- **Bus select (v0.8, MG19):**
  - Close exactly one SUB jumper and one AUX jumper per board, unique across the four groups.
  - Two boards on one bus share a summing node with separate feedbacks. The difference mode has no feedback, so both
    summers rail in opposite directions (±16.5 V), and the insert send then carries ~16 V DC.
  - Write the group number in the silk's "GRP __" box beside the jumpers.
  - Check it on the jig.

Per sub: 3 × OPA1612 (sum/re-invert, return buffer/post-amp, pan buffers L/R), 1 × DRV134,
2 × NJ6FD-V (insert, output), PTB0143 fader, RD902F pan, 2 × PVA2 (MIX, AFL), 1 LED.

## 13. Aux masters ×6

Bus pins: AUX1 = 24, AUX2 = 25, AUX3 = 23, AUX4 = 22, AUX5 = 21, AUX6 = 20. The strips feed
these buses through 22K.

```
AUXn bus ─ ferrite ─ summing amp (OPA1612 A), Rf 22K 1 % ∥ 100 pF, + input = GCANCEL
         ─ re-inverter (OPA1612 B), 4 × 2K2 0.1 % + 2 × 22 pF, + leg from GCANCEL_BUF   → AUXn_SUM
AUXn_SUM ─ 33µ NP ─ master level RD901F A10K (pin 1 = GNDA, pin 3 = signal)
         ─ wiper ─ 2.2µ film + 100K ─ output buffer (OPA1612, non-inverting:
           Rf 4K7 ∥ 100 pF, Rg not fitted = unity; fit 4K7 for +6 dB, 2K2 for +10 dB)  → AUXn_OUT
AUXn_OUT ─┬─ DRV134 ─ NJ6FD-V TRS output (tip hot, ring cold, sleeve CHASSIS since G2b)
          └─ AFL switch (PVA2): pole A 22K to PFL bus (off: resistor end grounded),
                                 pole B +VL → 100K → PFLDET, 4K7 → AFL LED (red)
```

- Gain: a strip with its aux pot fully up and the aux master fully up gives unity at
  AUXn_OUT, then +6 dB differential from the DRV134. The Rg position lets you raise it
  for effects units that want a hotter send.
- 100 pF across 22K (corner 72 kHz). Checked in `sim/aux_master.cir` with a single-pole
  op-amp at 10 MHz and 50 MHz GBW and 1 nF or 10 nF of bus capacitance:

  | Cf | Worst case (10 MHz, 10 nF) | 20 kHz response |
  |----|----------------------------|-----------------|
  | 47 pF | +3.0 dB peak at 72 kHz | — |
  | 68 pF | +1.2 dB peak at 61 kHz | −0.2 to +0.2 dB |
  | **100 pF** | no peaking; −3 dB at 65–86 kHz across all four cases | −0.4 dB worst |

  The −0.4 dB at 20 kHz on an effects send is acceptable; 100 pF is the value. Re-checked in the
  review (2026-10-23) with open-loop models fitted to the datasheets and TI's OPA161x model:
  ≥ 55° phase margin for N = 1 or 24, Cbus 100 pF–10 nF, with or without the ferrite; 20 kHz
  −0.22 to −0.34 dB, −3 dB at 70–85 kHz.
- **Op-amp: OPA1612** (was OPA1656 until v0.6; review 2026-10-23). The strips' aux 22Ks hang
  permanently from the aux pot wipers (there is no per-strip aux on/off), and AUX1–6 run
  straight through the master between the wings. So every aux summer always sees all 24 strips
  and runs at a noise gain of 25, where voltage noise dominates. The OPA1612 (1.1 nV/√Hz) gives
  −94.3 dBu against −92.3 dBu for the OPA1656, whose 1/f-rich noise (0.53 µVrms over the band,
  ≈ 3.75 nV/√Hz average) is multiplied by 25. The difference holds A-weighted (−96.2 vs −94.3).
  That is within 0.9 dB of noiseless op-amps (resistor floor −95.2 dBu). The OPA1656 would only
  win on a console with ≤ 9 strips. The summer and its re-inverter share one dual (`new_package`).
  The PFL bus is the opposite case and keeps the OPA1656 (§18). `sim/review/opa1656/noise.py`.
- Aux 5/6 as a stereo pair needs nothing special: two masters, two outputs.
- Level buffer (`level_buffer()`, v0.8 MG5): 10 pF C0G from the + input to GNDA, against the wiper's lag
  (38–41° → 75–87°; ≥ 52° with 47 pF on the output). 22 pF would cost the re-inverter that drives the pot top more.
- **Aux outputs are unmuted** (decided 2026-10-24, MG20). Unlike the main, C/Room and phones outputs they have no
  mute relay, so at power-up they carry the §8 rail-skew step: 0.2–0.75 V differential and 1.2–3.0 V
  common-mode for 10–100 ms. Power monitor and headphone amps fed from an aux after the console, or mute them.
- AFL is taken after the master level (post-master), as the architecture specifies.

Per aux: 1 × OPA1612 (sum, re-invert), ½ × OPA1612 (output buffer; two auxes share one),
1 × DRV134, 1 × NJ6FD-V, RD901F level, 1 × PVA2 (AFL), 1 LED.

## 14. Noise, subs and auxes (20 Hz–20 kHz unweighted, summing amp + re-inverter)

OPA1656 figures include its 1/f noise, scaled to the datasheet's 0.53 µVrms over 20 Hz–20 kHz
(review 2026-10-23). The operating points:
- an aux bus always carries all 24 strips (N = 24, bold in the OPA1612 column);
- the PFL bus carries the pressed sources only (N = 1–4, bold in the OPA1656 column, §18).

| Channels on the bus | SUB, 4K7, OPA1612 | 22K, OPA1612 | 22K, OPA1656 | 22K, NE5534 |
|---|---|---|---|---|
| 1 | −108.7 dBu | −101.2 dBu | **−104.8 dBu** | −104.5 dBu |
| 4 | −106.6 | −99.5 | **−101.1** | −101.0 |
| 12 | −103.1 | −96.7 | −96.2 | −96.3 |
| 24 | −100.1 | **−94.3** | −92.3 | −92.5 |

The NE5534 is also recommended for at most ±15 V; the rails are ±17 V.

The aux buses are 6 dB noisier than MIX/SUB at full load because of the 22K resistors,
which stay at 22K so the strip aux pot wipers aren't loaded (architecture section 2.4).

## 15. Parts summary, Parts 1 and 2

| Part | Qty | Where |
|------|-----|-------|
| OPA1612 | 2 (mix L/R sum + re-invert) + 2 (mix insert/post-amp) + 1 (mono) + 1 (GCANCEL buffer) + 12 (subs) + 3 (aux output buffers) + 6 (aux sum + re-invert) = **27** | |
| OPA1656 | **0** | (PFL only, §23) |
| DRV134 | 3 (L, R, mono) + 4 (subs) + 6 (aux) = **13** | |
| 10 µF NP electrolytic | 2 per DRV134 = **26** | output DC blocking inside the Sense loop |
| LM393B | 1½ | mute relay control (rail sense, timer Schmitt) |
| Omron (Aratas) G6K-2F-Y DC12 | 3 | main output mute (C/Room and phones: §23) |
| Bourns PTB0144 (dual) | 1 | master fader |
| Bourns PTB0143 | 4 | sub faders |
| ALPS RK09L1240015 (B10K dual, detent) | 4 | sub pans (v0.11) |
| Alpha RD901F A10K | 6 | aux master levels |
| C&K PVA2 EE | 4 (sub MIX) + 4 (sub AFL) + 6 (aux AFL) = **14** | |
| Neutrik NJ6FD-V | 2 (mix inserts) + 4 (sub inserts) + 4 (sub outs) + 6 (aux outs) = **16** | |
| XLR male | 3 | MIX L, MIX R, MONO |
| LED red | 10 | sub and aux AFL |
| 2K2 0.1 % | 4 × 13 = 52 (or 13 quad networks) | re-inverters |
| 22 pF C0G 5 % | 2 × 13 = 26 | re-inverter compensation (§3) |

As generated (M1 modules, 2026-10-23): master 13 × OPA1612 + 2 × OPA1656 (two halves tied off as spares, so
no package straddles two placement areas), each group 7 × OPA1612; console 41 × OPA1612 + 2 × OPA1656. Since G3b
(2026-10-25): master 4 × OPA1656 (U18, U21, U43, U44), each group 7 × OPA1612 + 2 × OPA1656; the DRV134s are DRV135UA.

---

# Part 3 — Stereo returns

(On the group modules: returns 1 and 2 on every group, eight in the console since v0.12.)

## 16. Stereo returns ×8

Purpose: effects returns (reverbs, delays) into the mix and subs. Built on the group modules, two per group (the
second since v0.12, `feature_gaps.md` RET1; `stereo_return()` in `tools/gen_group.py` builds both), with the same
receiver, routing and PFL circuits as the strip.

```
RET n L in (NJ6FD-V) ─ 1M per leg, 220R, 100 pF at each follower + input, OPA1656 followers, 100R (G3b) ─ differential receiver (OPA1612 A, 4 × 10K 0.1 %, 33 pF on both legs) → RETn_L
RET n R in (NJ6FD-V, tip and ring normals wired to the L jack's tip and ring:
           with no plug in R, the R receiver sees the L signal)        ─ receiver (OPA1612 B) → RETn_R
RETn_L/R ─ 33µ NP + 47K ─ PREn_L/R ─┬─ level, dual A10K (RD902F), pin 1 = GNDA
                                    │    ─ wipers ─ 2.2µ film + 100K ─ buffers (OPA1612 A/B;
                                    │      Rf 4K7 ∥ 100 pF, Rg not fitted = unity, fit 2K2 for +10 dB)
                                    │    ─ 100µ NP + 47K ─ RTNn_L/R
                                    │       ─ routing: MIX, 1-2, 3-4 (3 × PVA2, A-B = on)
                                    │         L via 4K7 1 % to MIX L / SUB1 / SUB3,
                                    │         R via 4K7 1 % to MIX R / SUB2 / SUB4,
                                    │         off grounds the resistor's bus end (as the strip)
                                    └─ PFL (pre-level): L and R each through 43K to a junction,
                                       PVA2 pole A puts the junction on the PFL bus (off: grounded);
                                       pole B: +VL → 100K → PFLDET, 4K7 → PFL LED (red)
```

- Gain: unity from input to RTNn with the level fully up and Rg not fitted. 43K + 43K into
  the 22K PFL bus gives (L + R) × 0.51, so a centred mono source arrives on PFL at +0.2 dB.
- Each RTN output drives three 4K7 summing resistors (1.57K), the same load as a strip's pan
  buffer.
- Ground note as for the subs (§12): the return feeds are referenced to the group module's GNDA, which joins
  GCANCEL through its own 10 Ω like a strip, so they are one of the averaged grounds, not master ground.
- No balance or mute. Add a balance pot later if wanted (dual B10K after the level pot, as
  the strip pan).

Per return: 2 × OPA1612, 2 × OPA1656 (followers), 2 × NJ6FD-V, 1 × RD902F A10K, 4 × PVA2 (PFL, MIX, 1-2, 3-4), 1 LED.
Totals for four: 8 × OPA1612, 8 jacks, 4 dual pots, 16 switches, 4 LEDs.

---

# Part 4 — Monitoring

Delta reference: ED2780 sheet 1 (monitor select receivers, PFL SWITCHER with series J112s,
PFL SUM AMP, PFL DETECTOR, C/ROOM dual pot, ground-cancel CRM output amps, headphone feed,
remote meter connector) and sheet 3 (meters).

## 17. Signal flow

```
EXT in L/R (2 × NJ6FD-V, R normalled to L) ─ receivers (OPA1612, 33 pF on both legs) → EXT_BL/BR ─ 100R ─ 33µ NP + 47K → EXT_L/R
POST_L/R (mix, after the master fader) ──────────────────────────────────────────→ MIX_MON_L/R
EXT switch (PVA2: latched = EXT) selects MIX_MON or EXT                           → MON_L/R

PFL bus (pin 27) ─ PFL summing amp (OPA1656 A, Rf 22K ∥ 100 pF, + input = GCANCEL)
                 ─ re-inverter (OPA1656 B, 4 × 2K2 0.1 %, + leg from GCANCEL_BUF)
                 ─ 33µ NP ─ SOLO LEVEL (RD901F A10K) ─ 2.2µ film + 100K ─ follower ─ 100R  → PFL_SIG

PFL switcher (one DG413, break-before-make; CRS on the D side, 100K to GNDA):
   MON_L   ─ 33µ + 1M ─ SW2 (NC) ─┐
   PFL_SIG ─ 33µ + 1M ─ SW1 (NO) ─┴─ CRS_L ─ follower (OPA1656) ─┬─ C/ROOM level ─ CR out
   MON_R   ─ 33µ + 1M ─ SW3 (NC) ─┐                              ├─ PHONES level ─ phones amp
   PFL_SIG ─ 33µ + 1M ─ SW4 (NO) ─┴─ CRS_R ─ follower           └─ meters
```

PFL is mono and goes to both sides. The meters follow what is being monitored: mix, EXT or PFL.

## 18. PFL summing amp and solo level

- Same circuit as an aux master (section 13), but on an OPA1656: 22K ∥ 100 pF feedback, + input
  on GCANCEL, re-inverter on GCANCEL_BUF. Strip PFL, sub AFL, aux AFL and return PFL all feed it
  through 22K (or 43K + 43K for the stereo returns). The PFL bus is switched: only the pressed
  sources connect (N = 1–4 in use). There the OPA1612's current noise dominates (1.7 pA/√Hz ×
  22K), and the CMOS OPA1656 is quieter: −104.8 / −103.2 / −101.1 dBu at N = 1 / 2 / 4 against
  −101.2 / −100.6 / −99.5 (review 2026-10-23).
- Pin 28 ("PFL Audio −VE" in the 200 Delta Technical Manual, p. 134) is not used by the master. The strips only
  pass it through, so it stays a spare.
- SOLO LEVEL: RD901F A10K, pin 1 = GNDA, then 2.2 µF film + 100K and an OPA1612 follower with 22 pF C0G at its + input
  and a 100R build-out to PFL_SIG (v0.8, MG3).
  - With a key pressed, two DG413 on-switches and both CRS inputs hang on PFL_SIG, and the bare follower oscillated
    (−0.8°). With the fix it is ≥ 73.5°.
  - Cost: −0.019 dB with a key pressed.
  Fully up = unity: strip PRE at 0 dBu gives 0 dBu in the control room, the same as a channel
  at its "0" mark through the mix.

## 19. PFL detect, auto-switch, rude solo

- PFLDET (pin 29) carries 38 keys: 24 strips, 12 on the group modules (sub AFL, aux AFL,
  return PFL), aux 5/6 AFL on the master. Every pressed key connects +VL through 100K.
- **Clamp (2026-10-23).** A released key's pole B leaves its ON node floating. Without the clamp,
  PFLDET back-fed every released key's 100K + 4K7 + LED: with two or more solos pressed, every
  other PFL/AFL LED glowed faintly, and 24 presses read 9.0 V, not 11.8 V. So the master:
  - pulls the line to GNDD with 10K and clamps it with two 1N4148 in series to GNDD;
  - compares it with 0.50 V (330K / 10K from +VL), LM393B on ±VL.
  One press gives 0.92 V (1.86×; about −4 mV/°C), 24 presses 1.29 V, and released LEDs carry
  ≤ 20 nA (`sim/pfldet.py`).
- 1 µF from PFLDET to GNDD filters the PVA2's contact bounce (≤ 3 ms). 10M from the comparator
  output back to PFLDET gives about 20 mV of hysteresis. Simulated with 3 ms of bounce: one switch
  each way, 5.8 ms after a press and 8.2 ms after a release.
- PFL_ON_RAW (comparator A) has a 100K pull-up to +5VL, so it is a DG413 logic level. It reaches
  the four IN pins as PFL_ON through 10K, which bounds the clamp current while the rails settle.
  Its low level, −VL + 0.15 V, is inside the DG413's input range. Never drive the DG413 inputs
  from an RC: they are TTL-level, not Schmitt. The PFL detect parts and their LM393B (comparator A
  and the flasher hold B, same inputs) sit beside the DG413, so PFL_ON_RAW stays short.
- **Switch: one DG413** (replaces the series-J112 switcher, review 2026-10-23), the strip's
  routing part, on the same ±VA rails and a +5VL logic supply made as on the strip (4K7 from +VA,
  BZX84C5V1, 1 µF, and a BAT54W from +5VL to +VA so VL stays within 0.3 V of V+ at power-down too;
  `strip_parts_review.md` T7).
  - PFL pressed (logic 1): SW1 / SW4 connect PFL_SIG to CRS_L / CRS_R; otherwise SW2 / SW3
    connect MON_L / MON_R. Break-before-make, 25 ns.
  - Sources are AC-coupled (47 µF + 1M) and CRS is on the D side (about 5 pC of charge
    injection, against about 25 pC on S), with 100K to GNDA.
  - The CRS followers are OPA1656: an OPA1612's bias current across 100K ∥ 1M would step CRS by
    5.5 mV typical, 23 mV maximum, at every switch.
  - Each has a 100R build-out to CRSB (v0.8, MG6), because CRSB runs ~214 mm to C/ROOM, PHONES and the meters.
    That gives 48–52° with 47 pF, against 25–31° without. Cost: −0.30 dB flat on C/Room, phones and the meter feed;
    the meter trim takes out its share.
  - Rude-solo LED: its cathode returns to an LM393B output that sinks to −VL. The 3K3 therefore has ~31 V across it
    (9.5 mA, 297 mW peak), so it is an anti-surge ERJ-P06J332V (v0.8, MG13).
  - Simulated (`sim/review/pflswitch`, `python3 t2_ac.py dgF J112F` etc.): crosstalk −137 dB at
    1 kHz and −111 dB at 20 kHz, independent of level; THD −100 dB at +20 dBu.
  - The zero-signal click depends on the switch leakage into the 1M source bias. Peak in the
    audio band (`t4_click.py dgF_L10p,dgF_L100p,dgF_L250p`): −88.6 dBu at 10 pA, −78.3 dBu at
    0.1 nA (datasheet typical at ±15.5 V), −70.3 dBu at 0.25 nA (room-temperature maximum). The
    switch sits near 0 V bias, so expect the low end. Check it with the PFL tick on the bench.
  - It is a hard cut: switching with programme playing gives a tick, as on most consoles.
- Why not the J112s: as generated, the 100K ramp resistor and the two 47K gate–source resistors,
  which sat on the floating side of the 47 µF, formed a divider. The off gate reached only
  −9.3 V and the off JFET sat at pinch-off. The result was −27 dB of crosstalk, −2.4 V DC on CRS
  (the meters read +7 dB at silence), a +5 dBu thump per press, and 6 % THD at +20 dBu. The Delta
  returns its 47K to the op-amp side of the coupling cap and drives the gates from saturated
  transistors. A faithful copy needs MON buffers, Miller drivers and selected J112s
  (`master_parts_review.md` item 4).
- Rude solo: LM393B as a ~2 Hz astable (100K / 100K / 100K hysteresis divider, 1M / 330 nF), flashing
  a 5 mm red "PFL ACTIVE" LED on the master panel. While no key is pressed, the hold comparator (same
  inputs as A, no pull-up) sinks and pulls the timing node FL_N to about −VL through a 1N4148, so
  the flasher's output stays high and the LED off. On a press it lets go: the first flash comes
  0.6 s later, then 0.17 s on every 0.54 s (`sim/flasher.cir`).
  - Until 2026-10-23 the hold pulled the other input, FL_P, up through a diode from a pulled-up
    comparator output. FL_P could only reach that output less a diode drop, FL_N charged past it,
    and the LED flickered with nothing soloed (found in the applied-review check).

## 20. Control room outputs

- C/ROOM level: dual A10K (RD902F), pin 1 = GNDA, fed from the CRS followers.
  Wipers ─ 2.2 µF film + 100K ─ OPA1612 followers (22 pF C0G at the + inputs, v0.8 MG5) ─ DRV134 ×2 ─ mute relay ─
  NJ6FD-V TRS outputs (tip hot, ring cold, sleeve CHASSIS since G2b).
- **Mute relay on the CR outputs too** (signed off 2026-10-23). They drive the monitor
  speakers, which matters more than the main outputs. Two more G6K-2F-Y DC12 (L and R, both
  legs, NC to GNDA), driven by the same control as section 8.
- Gain: unity at full C/ROOM, then +6 dB differential from the DRV134.

## 21. Headphones

- PHONES level: dual A10K (RD902F), fed from the CRS followers (independent of C/ROOM).
- Amplifier per side: OPA1612 driving an LME49600 buffer inside its feedback loop (TI's
  composite arrangement). LME49600 datasheet: ±2.25 to ±18 V operating (±20 V absolute),
  ±250 mA output, internal current limit and thermal shutdown, 7.3 mA quiescent with the BW
  pin open (110 MHz mode; use that). TO-263, so give it copper for heat. Non-inverting gain 1 + 4K7/2K2 = +9.9 dB. Feedback taken from the
  jack side of a 2.2 Ω output resistor. The 100 pF goes from the OPA1612's output to its − input (v0.8, MG2), not
  across the 4K7 from PHO.
  - From PHO it put the composite's crossover at the OPA1612's unity-gain frequency, inside the LME49600's lag and
    80–90 MHz resonance. It was unstable at the pot ends.
  - From the op-amp's output, the op-amp is a local follower at HF and the LME49600 is out of the HF loop (hand-over
    at 339 kHz): 78–87° with three LME49600 macros and every load.
  - 22 pF C0G at the + input; each LME49600 beside its op-amp.
- Output and ±VP feed resistors 2.2 Ω are 2512, 1.5 W (Vishay CRCW25122R20FKEGHP, MG11).
  - A mono (TS) plug grounds PHO_R. With the feedback tap grounded the composite amplifies the OPA1612's own input
    offset by ~140, so the LME49600 can sit at its ±490 mA current limit even in silence: 0.53–0.67 W in the output
    2R2, up to 0.56 W in one rail 2R2.
  - With both channels shorted, R4 can see 2.2 W until the LME49600s' thermal shutdown cycles them.
  - The LME49600 is protected. A mono plug in the phones jack is still a fault: say so in the user notes.
  0 dBu at CRS gives 2.4 V rms at full PHONES, 180 mW into 32 Ω, well inside the LME49600's
  250 mA.
- Supply: separate branch from ±V through 2.2 Ω + 1000 µF per rail (the Delta has its own
  phones supply). Phones ground (PHONESGND) is a separate wire to the star point, as the Delta.
- **Mute relay (2026-10-23).** The composite is DC-coupled. After a crowbar, the SCR holds one
  rail near 0.9 V while the other stays up, and the output would sit at about 0.6–1.5 V DC,
  20–45 mA into 32 Ω, for the whole fault (rail skew at power-up: 0.4–1.5 V). So the phones get a
  sixth G6K-2F-Y DC12 on the same control as section 8: COM to the jack, NO to the amplifier
  output (after the 4K7 feedback tap, so ≤ 0.1 Ω sits outside the loop), NC to PHONESGND.
- Jack: NJ6FD-V, tip L and ring R through the relay (NC to PHONESGND), sleeve straight to PHONESGND.

## 22. Meters (main L/R; follow the monitored signal)

Thresholds and LED drive are copied from the Delta (ED2780 sh.3). The detector is new: the
simulation (`sim/meter.cir`) showed the Delta-style peak detector reads the bottom of the
scale badly (below).

- Source: CRS_L/R (so the meters show mix, EXT or PFL, whichever is monitored), through
  100R (Delta R41/R141) to a remote-meter header (for a meter bridge later) and to the
  rectifier.
- Detector per side, four op-amps (2 × TL072; JFET inputs, as the Delta's TL071/072):
  - U1, U2: precision full-wave rectifier (inverting half-wave with two 1N4148, then a summer:
    v and 2 × half-wave). Gain trim in U2's feedback: 10K + 10K trimmer (gain 0.5–1.0).
  - Average (Delta R303/C302): |v| → 33K → 2.2 µF, about 73 ms.
  - Peak: U3 precision peak detector. 1N4148 inside the loop, 220R into 1 µF (0.22 ms first-order attack),
    release 330K + 220K (0.55 s, Delta-like). U3's feedback comes from the U4 follower through
    10K, with a 1N4148 clamp from U3's output to its inverting input. The feedback must not
    come from the capacitor itself: then the clamp current discharges it (simulated: 50 Hz
    read 0.95 dB low and the hold collapsed).
  - v0.8 (MG8): the jumper's PEAK side takes the diode's cathode (PK1), not the capacitor end of the series resistor.
    - With the follower on the capacitor, the loop held two integrators (U3 and 1K / 1 µF): 0–1.5° while the diode
      conducts, and 10 kHz at −20 dBu read +5 dB high.
    - Now the loop holds U3 alone, plus 22 pF across U3 (output to − input): 64–79° (classic TL072), 43–52° with
      TI's pessimistic TL07xH model.
    - Held readings against the true peak: 1 kHz 0 dBu bursts −0.1 to −0.2 dB, 1 kHz −20 dBu −0.3 to −0.5 dB,
      10 kHz 0 dBu (2 ms) −0.8 dB, 10 kHz −20 dBu −1.5 to −2.5 dB.
    - Between peaks DET carries µs conduction spikes up to the true peak, so on HF bursts the next LED up can glow
      faintly.
    - A steady 1 kHz reading moves −0.08 dB at 0 dBu (the trim takes it) and −0.18 dB at −20 dBu.
  - Summer U2: 22 pF C0G across its feedback; the trimmer beside U2, so the summing junction stays short (MG9).
  - PEAK/AVG solder jumper per side (Delta J2), then U4 follower.
    - v0.8 (MG9): a 470R build-out from U4 to the DET distribution (20 comparator inputs + ~165 mm): 58–60°
      classic, ≈ 57–59° datasheet-corrected for the TL07xH die.
    - The 10K back to U3's − input is taken from U4's pin side. From the far side, the clamp current through the 470R
      read 0.4 dB low and rippled 0.5 dB.
    - TL072s: TI TL072HIDR. The H suffix fixes the new die (SLOS080W Table 9-1), which these margins assume; 42 V
      abs max. The 20 LM2901 inputs (about
    0.5 µA typical, 5 µA max in total) load U4, not the detector capacitor. Directly on the
    Delta's 55K they would be a 27 mV error against a 67 mV bottom threshold.
  - Calibrate after setting the jumper: apply 0 dBu and set the trim so that the 0 dB LED just
    lights, i.e. U4 at the 0 dB tap. That tap is about 0.63 V, not 0.649 V: the meter branch's
    10R drops VM to about 16.45 V, and calibrating to 0.649 V would read 0.27–0.29 dB high. Peak
    mode needs a gain of about 0.58, average mode about 0.90; the trim covers both.
  - The ballistics capacitors: the 2.2 µF average caps are MKS2 film (v0.8, F1); the 1 µF peak caps are 1206 MLCCs: use film, C0G or
    50 V X7R. A small X7R loses 10–25 % to DC bias and shifts the 73 ms / 0.55 s times.
- Simulated (single-pole op-amps at 3 MHz GBW, 1N4148 model):

  | Test | Peak mode | Average mode |
  |------|-----------|--------------|
  | −20 / −10 / +10 / +18 dBu at 1 kHz, relative to the 0 dBu reading | −20.08 / −10.03 / +10.01 / +18.02 dB | exact to 0.01 dB |
  | 50 Hz / 10 kHz / 20 kHz, relative to 1 kHz | −0.04 / −0.15 / −0.28 dB | +0.01 / −0.11 / −0.13 dB |
  | 5 ms / 10 ms / 100 ms tone burst | full reading (+0.1 dB overshoot) | −23.5 / −17.8 / −2.5 dB |
  | Release after a 0.5 s burst | −15.8 dB at 1 s, −32 dB at 2 s | τ 73 ms |
  | 10 % pulse wave, same p-p as a 0 dBu sine | reads the larger (+1.97 V) excursion | — |
  | v1 (Delta diode-compensated peak, 75R / 10 µF) at −20 dBu | read −11.7 dB | — |

  The peak mode is a fast "sample peak" (about 1 ms attack), faster than an IEC type II PPM
  (where a 10 ms burst reads −4 dB). A full-wave rectifier matters for synth pulse waves,
  which a half-wave detector can under-read by the waveform's asymmetry.
- Thresholds: resistor ladder from +V through 16K, then 1K5, 1K1, 910, 680, 620, 470, 330, 300,
  220, 180, 150, 110, 91, 68, 62, 47, 33, 27, 20, and 91R to meter ground (Delta R309–R329).
  That gives 2 dB steps from −20 to +18 dB about the 0.649 V tap (calculated from the values).
- 20 LEDs per side: −20 … 0 green (11), +2 … +10 amber (5), +12 … +18 red (4). With 0 dBu
  nominal and clip at about +22 dBu, red means less than 10 dB of headroom left.
- Comparators: 5 × LM2901B per side (TI LM2901BIDR), supplied from ±VM. That is about 33 V,
  over the non-B part's 30 V recommended maximum; the B part is rated 36 V, with 3.5 mV maximum
  offset (±0.45 dB at the −20 dB LED). Each package sits beside the first LED it drives.
- LED strings: two series strings of 10 per side, each fed by a PNP constant-current source
  (two-diode reference, Delta TR15/TR16). Comparator k pulls the anode of LED k to −VM (its GND
  pin), bypassing the rest of its string. The lowest comparator still on sets the top of the
  bar, and the source current flows either through the lit LEDs or into that comparator, so the
  supply current is constant whatever the reading and the meters don't modulate the rails.
  Simulated as generated: a correct 20-step bar, no ghost LEDs (`sim/review/meters`).
- **Current source (2026-10-23):** onsemi BCP53-16, SOT-223 (KiCad footprint SOT-223, pads 1–4,
  tab = collector), 120R emitter resistor: 4.2–5.7 mA (4.9 typical) over junction tolerances.
  That stays under the LM2901B's guaranteed 6 mA sink, so the LED above the bar cannot glow.
  When its string is dark (string B below 0 dBu, so nearly always) the source holds about 32 V:
  about 160 mW. Give each tab ≥ 1 cm² of collector copper: Tj 55–70 °C at 40 °C ambient. The first
  draft's SOT-23 MMBT3906 with 75R ran at 6–7 mA and 195–280 mW, past 150 °C, and its current rose
  as it heated. The Delta ran 2SA970s at about 230 mW of their 300 mW. Each source sits at the
  top of its string (beside the string's first LED).
- LEDs: 3 mm diffused GaP / GaAsP, Vf ≤ 2.6 V maximum at the datasheet current, no InGaN: ten in
  series must fit in about 31 V of the string's span. InGaN green (3.3 V typical, 4.1 V maximum)
  collapses string A at low rails and blanks LEDs 1–10. Kingbright WP710A10GD green (568 nm),
  WP710A10ND amber (602 nm), WP710A10ID red (617 nm), all stocked; worst case leaves ≥ 7.7 V of
  current-source headroom.
- Supply: meter branch from ±V through 10R + 47 µF per rail (Delta R307/R308, C305/C306),
  meter ground run separately to the star point.

## 23. Monitoring parts summary

| Part | Qty | Where |
|------|-----|-------|
| OPA1612 | 1 (EXT receivers) + 1 (solo follower, spare half) + 1 (CR buffers) + 1 (phones) = **4** | |
| TL072 | 4 | meter detectors (2 per side) |
| OPA1656 | 2 | PFL sum + re-invert; CRS followers |
| LME49600 | 2 | phones |
| DRV134 | 2 | CR outs (+ 4 × 10 µF NP) |
| LM393B | 1½ | PFL detect and flasher hold (one package, beside the DG413), rude-solo flasher (half) |
| LM2901B | 10 | meters |
| BCP53-16 | 4 | meter LED current sources (SOT-223) |
| DG413 | 1 | PFL switcher (+ BZX84C5V1 for +5VL) |
| G6K-2F-Y DC12 | 3 | CR mute (2), phones mute (1) |
| RD902F A10K | 2 | C/ROOM, PHONES |
| RD901F A10K | 1 | SOLO LEVEL |
| PVA2 | 1 | EXT select |
| NJ6FD-V | 2 (EXT in) + 2 (CR out) + 1 (phones) = **5** | |
| LEDs | 40 meter (Kingbright WP710A10GD / ND / ID) + 1 PFL ACTIVE | |

---

# Part 5 — Master power entry

## 24. Rails and connector

- Rails: ±17 V from the external linear PSU (architecture 3.3). The master sits in the centre
  of the console and feeds both ribbon wings, so all power enters at the master.
- Connector (2026-10-22): 7-pin XLR male, **Neutrik NC7MD-LX** on the rear panel (solder cups, 5 A
  per contact, < 50 V, wire up to 1.0 mm²). Wired with 18 AWG, one wire per pin, to J (Phoenix
  MKDS 1,5/7-5,08, 17.5 A) on the master PCB. Pin 1 = chassis/mains earth (mates first), 2–3 = +V,
  4–5 = 0 V, 6–7 = −V: two contacts per rail, so 10 A per rail against ≈ 3.09 A typical and
  ≈ 4.33 A in the accepted worst corner on +V (§27; was 2.65 / 3.8 A with strip v4.0). Neutrik makes no 7-pole horizontal-PCB receptacle (only 3–5 poles),
  hence the panel part and wires. The 5-pin NC5MAH (3 A per contact) is too small with strip v4.0.
- Reverse-polarity protection: a Schottky (SS54, SMC, 40 V 5 A) from each rail to 0 V, reverse-biased in
  normal use. A wrongly wired lead then puts the PSU into current limit instead of reversing
  every op-amp.

## 25. Distribution

- Two 34-pin headers on the master, one per wing (12 strips each), carrying the buses and
  power: −V on pins 30–31, +V on pins 32–34 (pin 34, the Delta's +48 V, since v0.10, `wing_power_proposal.md` W1).
- Each wing gets its own PTC fuse per rail: **Bourns MF-RX250/72** on +V (2.5 A hold, 5.0 A trip, 72 V, 40 A max,
  R1max 0.13 Ω; W2, v0.10) and **MF-RX185/72** on −V (1.85 A hold, 3.7 A trip; v0.9, `hpf_proposal.md` H4). They
  protect the 28 AWG ribbon conductors and the IDC contacts (Würth WR-BHD sockets, 1 A per contact; three on +V, two
  on −V) from a shorted strip; at hold that is 0.83 A (+V) and 0.93 A (−V) per contact.
  - +V wing PTC hold at 40 / 50 °C: 2.03 / 1.80 A. A wing's +V is 1.34 A typical (66 / 74 %) and 1.92 A in the
    accepted worst corner (95 / 107 %). −V: 1.05 A typical and about 1.3 A at maximum IQ against 1.50 / 1.33 A.
  - Placement (fixed, `place_master.py`, spots searched clear of every other part): F1 in its row, pads 8.17 / 18.33
    at y 186.75; F3 vertical by the right edge, pads (69.5, 234.17) / (69.5, 244.33), on the wing supply's way down to
    CN3. F2 / F4 (−V) unchanged (MF-RX185/72: F2 courtyard x 4.05–19.73, F4 58.36–74.04, clear of J1). The MF-RX250/72
    footprint has its own 10.16 mm lead pitch (`tools/footprints.py`).
  - 72 V rather than the 30 V MF-R parts: −V (pins 30–31) sits next to +V (32–34), so a bent pin or crimp fault shorts
    34 V across the pair, and the first PTC to trip takes almost all of it.
  - Initial resistance 0.05–0.13 Ω (MF-RX250/72) and 0.08–0.19 Ω (MF-RX185/72): about 0.1–0.2 V drop per wing.
  - History: MF-R075 (0.75 A hold) for the v3.1 strips, MF-RX160/72 (kept in MG14), MF-RX185/72 with strip v4.3 (H4),
    MF-RX250/72 on +V with three conductors (W2). Two conductors could not take the 250 (1.25 A per contact at hold).
  - Keep F1–F4 away from the ±VP 2R2s and the LME49600s (placement).
- Master local branches, each with its own series element and reservoir:

  | Branch | Feeds | Series | Reservoir |
  |--------|-------|--------|-----------|
  | ±VA audio | op-amps, DRV134 | 1 Ω per rail | 470 µF + 100 nF per IC |
  | ±VP phones | OPA1612 + LME49600 | 2.2 Ω | 1000 µF |
  | ±VM meters | LM2901s, LED strings | 10 Ω | 47 µF (Delta values) |
  | ±VL logic | LM393s, relay control, LEDs | 10 Ω | 47 µF |
  | relay coils | G6K-2F-Y ×6 via one NPN switch | from +V directly (560 Ω each) | — |

  The audio branch uses 1 Ω instead of the strips' 10 Ω because it carries more current: ~0.14 A typical, up to
  ~0.25–0.3 A with every DRV134 at +20 dBu into 600 Ω. It is an anti-surge 0805 (ERJ-P06J1R0V) for the PSU-lead
  hot-plug pulse. The ±VP 2.2 Ω are 2512, 1.5 W (§21).

## 26. Grounding (the star point)

- The star point is the master's M4 stud (CN1) with its four net ties. Under it, on a threaded spacer, two copper bars
  (one per wing, ~15 × 2 mm, ≈ 0.1 mΩ), each with fourteen 6.3 mm tabs in two rows. Each strip and group spade
  (CN4 / CN1) has its own 14 AWG (2.08 mm²) stranded wire to a tab of its wing's bar, blue 6.3 mm insulated
  receptacles at both ends (`ground_study.md` G1, 2026-10-25).
- Route: each wire drops from its tab to just under the motherloom and runs tied under it (every ~80 mm) to the
  master, then down the master's free edge strip (x 0.3–4.3 / 74.3–78.3) to the bars. Never along the tub floor: the
  loop each wire makes with the ribbon's ground conductors is what picks up hum (up to 800 cm² that way, at most
  33 cm² under the ribbon). Cut lengths from the module next to the master outwards: left wing 264 mm + 40.6 mm per
  module (to 792), right wing 237 mm + 40.6 mm (to 765), each with 60 mm for the receptacle and dressing.
- Also on the star: PSU 0 V; master AGND; master GNDD (one link); meter ground; PHONESGND; chassis, via the PSU lead's
  earth pin. Every jack board's CHASSIS (balanced-input sleeves, plated standoffs) reaches it through the panels and
  the frame: bare-metal contact or star washers at each standoff's panel end and where the panels meet the rails.
- GCANCEL (pin 26) does **not** go to the bar (decision, section 3).
- The ribbon's GND conductors (even pins 2–16) carry only the strips' local audio ground for
  the group-bus shielding; heavy return current goes through the spades.

## 27. Current budget (typical supply currents from the datasheets)

| Item | +V | −V |
|------|----|----|
| 49 × OPA1612 (3.6 mA/ch typ, 4.5 max) | 353 mA | 353 mA |
| 2 × OPA1656 (3.9 mA/ch): PFL sum, CRS followers | 16 | 16 |
| 18 × OPA1656, return / EXT followers (G3b, 2026-10-25; RET1): 16 on the groups, 2 on the master | 140 | 140 |
| 4 × TL072 (meters) | 11 | 11 |
| 15 × DRV134 (5.2 mA) | 78 | 78 |
| 10 × LM2901B, 3 × LM393B, DG413 (+5VL zener 2.5 mA) | 17 | 14 |
| 2 × LME49600 (7.3 mA) + phones load | 65 | 65 |
| Meter LED strings, 4 × ~5 mA | 20 | 20 |
| 6 relay coils (9.1 mA each) | 55 | — |
| Panel LEDs (AFL, PFL, power, rude solo) | 60 | — |
| **Master** | **≈ 0.81 A** | **≈ 0.70 A** |
| 24 strips v4.7 at ≈ 104 / 87 mA (v4.4: 100 / 87; v4.3: 92 / 79; v4.0: 85 / 72) | ≈ 2.50 A | ≈ 2.09 A |
| **Console** | **≈ 3.31 A** | **≈ 2.79 A** |

v0.12 (2026-10-26, `feature_gaps.md` RET1): each group's second return adds 2 OPA1612 and 2 OPA1656 (the followers),
≈ 30 mA per rail typical and ≈ 38 mA at maximum IQ, plus its PFL LED when pressed. Console ≈ 3.31 / 2.79 A typical
(+0.12 A per rail). With MET1 the worst corner on +V goes from ≈ 4.38 to ≈ 4.54 A. A wing's +V (two groups) is
≈ 1.48 A typical (74 / 82 % of the MF-RX250/72's hold at 40 / 50 °C) and ≈ 2.07 A in the corner (103 / 115 %):
in that corner a wing PTC can trip, as noted for v4.4 below. **Accepted (Ruslan, 2026-10-26)**, on the same grounds as
the 4.24 / 4.33 A corners: a console in use never has every op-amp at maximum IQ and every key and LED on at once, and a
tripped wing PTC only silences that wing until it cools. The "Master" row above holds the group modules' parts
too (the table predates the M1 split).

Strip v4.7 (2026-10-26, `feature_gaps.md` MET1): the signal LED adds ≈ 4 mA per strip on +V while green is lit
(green 3.2 mA, its switch's base 0.3 mA, U17 ≈ 0.5 mA), ≈ +0.1 A console-wide (counted as lit, the usual state with
programme), nothing on −V. In overload the red's drive replaces the old direct one, plus about 1 mA of switch bases, so
the worst corner (every LED lit, every op-amp at maximum IQ) goes from ≈ 4.33 to ≈ 4.38 A on +V. A wing's +V is ≈ 1.42 A
typical (71 / 79 % of the MF-RX250/72's hold at 40 / 50 °C) and ≈ 1.99 A in the corner.

G3b (2026-10-25, `ground_study.md` §10): the return / EXT followers add 78 mA per rail typical, 31 mA on each wing
(two groups), and about 92 mA at maximum IQ. The worst corner goes from ≈ 4.24 to ≈ 4.33 A on +V. A wing's +V is
≈ 1.37 A typical (68 / 76 % of the MF-RX250/72's hold at 40 / 50 °C) and ≈ 1.96 A in the corner.

Strip v4.4 (2026-10-25, `ground_study.md` G3): + U16 OPA1656 input followers, 7.8 mA per rail typical (10 mA at
the 5 mA-per-channel maximum). Console +V ≈ 3.01 A typical, ≈ 3.64 A with every OPA1612 / OPA1656 at maximum, and
≈ 4.24 A with every LED lit as well: **over the PSU's 4 A rating in that corner** (it was exactly 4.0 A with v4.3).
Per wing ≈ 1.34 A typical (MF-RX185/72 hold 1.85 A), ≈ 1.92 A in the same corner. **Accepted (Ruslan, 2026-10-25):**
U16 stays OPA1656. The corner needs every op-amp at maximum IQ and every key and LED on at once, which a console in use
never reaches; typical 3.01 A leaves 1 A of the PSU's 4 A. In that corner a wing's 1.92 A on +V is above the
MF-RX185/72's 1.85 A hold, so a wing PTC can trip (the wing goes silent until it cools); nothing is damaged (OPA1642
followers, ≈ 4.11 A, were the alternative). At 50 °C even a wing's typical 1.34 A meets the PTC's derated hold
(1.33 A); since v0.10 (`wing_power_proposal.md` W1 / W2) the +V PTC is an MF-RX250/72 on three conductors, so the
corner reaches 95 / 107 % of its hold at 40 / 50 °C instead, and the typical load 66 / 74 %.

With the M1 split, the subgroups, aux masters 1–4 and returns move to the four group modules. Each
draws about 61 mA per rail from the ribbon (7 OPA1612, 2 DRV134) plus up to 3 LEDs. The
master module's op-amps and drivers drop to about 174 mA per rail. The console total is unchanged
(same circuits). Two groups per wing: about 1.37 A per wing on +V typical since G3b (1.25 A with strip v4.3, 1.16 A with
v4.0), on the MF-RX250/72 (2.5 A hold, 2.03 / 1.80 A at 40 / 50 °C) and three ribbon conductors since W1 / W2. The
accepted worst corner (every LED lit, op-amps at maximum current) reaches about 1.96 A.

Strip v4.0 (2026-10-22): 10 × OPA1612 (with the KHN mid bands), DG413 logic supply 2.4 mA, LEDs on
+VL (ON, EQ and routing lit: about 9 mA). The strips were 33 / 23 mA in v3.1, when this budget was
first written. With the OPA1612 at its 4.5 mA maximum the console reaches about 3.2 A on +V. With
every LED on every strip lit as well, it reaches 3.8 A.

Strip v4.3 (2026-10-24, sweepable HPF): 11 × OPA1612, +7.2 mA per rail typical. The console's +V is about 2.82 A
typical, 3.4 A with every OPA1612 at maximum, and about 4.0 A with every LED lit as well: the PSU's 4 A rating, with
no margin left in that corner (a real console never has every key and every LED on at once at maximum IQ, but the
PSU's current limit and the LDOs' heatsink, sized for 4 A, are now exactly at it).

**Consequences (applied 2026-10-22):**

| Item | Was | Now |
|------|-----|-----|
| Wing PTC per rail | MF-R075, 0.75 A hold, 60 V | Bourns MF-RX160/72: 1.6 A hold, 3.2 A trip, 72 V (§25) |
| Power inlet | 5-pin XLR NC5MAH on the PCB, one 3 A contact per rail | 7-pin XLR NC7MD-LX on the panel, two 5 A contacts per rail, wired to a 7-way terminal (§24) |
| PSU regulators | ≥ 3 A | ≥ 4 A per rail (architecture 3.3) |
| PSU transformer | 2.5 A DC per rail | 4 A DC per rail (architecture 3.3) |
| Strip R1/R2 (10 Ω, 0805) | — | unchanged: 0.8 V drop, 55–80 mW (0805 is 125 mW); 1206 if margin is wanted |

Reducing the strip current instead: OPA1678 (about 2 mA/ch) in the six KHN positions would save about
10 mA per strip (0.25 A per rail). The EQ is resistor-noise dominated, but simulate the noise before
choosing.

## 28. Power-on sequencing

- Power-on mute (section 8) covers the main, C/Room and phones outputs: six relays, closed about 2.8 s after
  both rails are above 14 V, opened at once if either drops.
- Power LED on +VL.

## 29. Still open

- Ground and hum (2026-10-25, `ground_study.md`): the PSU's worst corner with the strip's input followers (≈ 4.24 A on
  +V) is accepted (§27, Ruslan 2026-10-25); G3b's return / EXT followers add ≈ 0.09 A to it (≈ 4.33 A). The returns,
  EXT and every balanced TRS output now follow G2 / G3 (G2b / G3b).
- Balanced outputs: THAT1646 went end-of-life (THAT memo, 1 September 2026); replaced by
  TI DRV134 on all 15 outputs (decided October 2026, section 7).
- The same THAT memo also ends the THAT 2180/2181 VCAs (planned for the external SSL bus compressor,
  architecture 4.2) and the THAT 124x receivers (listed as an option in architecture
  section 5). The bus compressor needs another VCA.
- Datasheet checks done October 2026: OPA1656, OPA1612, LME49600, DRV134, G6K-2F-Y, Neutrik
  NC5MAH (figures in sections 7, 8, 13, 21, 24, 27). TI lists OPA1612, OPA1656, LME49600,
  DRV134 and DRV135 as ACTIVE. Power entry re-checked for strip v4.0 (2026-10-22): Bourns MF-R and
  MF-RX/72 tables (MF-RX160/72), Neutrik NC7MD-LX via distributors (5 A per contact); §24, 25, 27.
- Meter detector simulated and redesigned (section 22).
- Schematics (M1 modules), generated by `tools/gen_master.py` / `tools/gen_group.py` from this spec, as of
  2026-10-25 (v0.11): master 579 parts, 1686 pins / 0 mismatches, check_fp 0, ERC 0; master jack board 89 pins;
  group 186 parts, 529 pins; group jack board 40 pins; all 0 mismatches, ERC 0 (v0.7: master 532 / 1579, group
  158 / 461). Mute control values are
  simulated (section 8, `sim/mute.cir` v3), PFL detect in `sim/pfldet.py`, the rude-solo flasher in `sim/flasher.cir`.
- Parts review (`master_parts_review.md`, signed off 2026-10-23) applied in v0.7. Its bench checks
  stay open: re-inverter stability on the scope (jig test 10), aux noise at N = 24, relay release time and
  mains-off fall rate with the real PSU, PFL tick with programme, meter current-source temperature and LED
  brightness at ~5 mA.
- An EXT LED (proposed in v0.6 §19) is not possible: both EXT switch poles carry audio; dropped.
- PVA2 switching sense: settled from the C&K datasheet with a fitting rule (strip spec 16.1); applies here too.

*Document version 0.11 — 25 October 2026 (design review R1/R2/R4/R5; earlier: ground and hum G1–G3, G2b/G3b, wing
power W1/W2, sweepable HPF, master/group review MG1–MG20, parts review S1–S8)*
