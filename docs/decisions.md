# goa-console — decisions made, in full

Moved out of `CLAUDE.md` on 2026-10-28 (`project_review.md` RV13), text unchanged. `CLAUDE.md` keeps one line per decision;
this is the record with the reasons, the rejected alternatives and the dates. Do not silently change any of them.

- Strip panel (2026-10-22): 8 HP × 12U Eurorack-style, two pot columns, jacks on the panel (Neutrik
  NJ6FD-V); custom frame with rails only at the panel ends. Columns at x 8.84 / 29.16 (2026-10-23, Ruslan): an even
  20.32 mm pitch within and across modules (`placer.py` XL / XR), every pot's pins turned to the centre line, knobs
  Ø14.5 since KN1 (planned at Ø13 then; Delta: 14 mm, 12.5 mm on MID frequency); was x 10 / 28 with 3 mm between Ø15 knobs.
- Master section as modules (2026-10-22, M1): four identical 8 HP group modules on the ribbon (sub n, aux n
  master, return n; solder-jumper SUB/AUX bus select; local GCANCEL buffer; strip-style power/grounds) and a
  16 HP master module (everything else, aux 5-6). master_section_spec.md header.
- PSU (2026-10-22): option B, two isolated LRS-150-24 at 21.6 V → 10 µH / 2200 µF → LM1084-ADJ (17.0 V,
  47 µF ADJ soft start) as identical floating rails; TL431 + PNP + 2N6505G SCR crowbar at 19.1 V per rail.
- Power (2026-10-22): strip v4.0 draws ~85 / 72 mA, console ~2.65 / 2.23 A typical (≤ 3.8 A on +V). Strip v4.3 (HPF):
  ~92 / 79 mA, console ~2.82 / 2.40 A, worst corner (max IQ, every LED) ~4.0 A on +V = the PSU rating; since MET1 / RET1
  (2026-10-26, current) console ~3.31 / 2.79 A typical, worst corner ~4.54 A on +V, wing ~2.07 A (accepted).
  PSU 4 A per rail; inlet 7-pin XLR NC7MD-LX (the plenum's rear wall since TB3, two 5 A contacts per rail, wired to a 7-way terminal);
  wing PTCs: +V Bourns MF-RX250/72 since 2026-10-25 (`wing_power_proposal.md` W2: 2.5 A hold on three conductors,
  0.83 A per contact at hold; own 10.16 mm footprint; F1 in its row, F3 vertical by the right edge), −V MF-RX185/72
  since 2026-10-24 (`hpf_proposal.md` H4; was MF-RX160/72, still on the jig stub; 72 V: a pin 31/32 short puts 34 V
  across one PTC). Master spec 24–27.
- Mid-band tuning (2026-10-22): the Delta's Wien band-pass with a 100K C-law dual (not stocked) is
  replaced by a KHN state-variable band-pass with the same response (peak 0.407, Q 0.275), tuned by a
  stocked Alpha A10K dual as dividers (430R / 13K wiper-to-top / 4K7; since strip v5.5 (EQM1) HI-MID 392R / 13K / 4K99,
  LO-MID 430R / 13K / 4K22) into the two integrators. CW = higher frequency, within 0.33 oct of a log sweep. U12–U14 OPA1612. A10K, not A100K: 100K was
  5.7–8.6 dB noisier. Spec 6.2.
- Routing (2026-10-22): the PVA2 routing switches carry logic only. Pole A drives a DG413 (U9–U11, at the
  bus header) that moves each 4K7's bus end between the bus (D side) and AGND; pole B drives a yellow
  routing LED. VL = +5VL from +VA via 4K7 + BZX84C5V1. Replaces the 4PDT idea (no vertical part exists).
- Jack board (2026-10-22): a 1/4" plug goes ~30 mm deep, so J1/J2/J5 sit on a separate 38 × 43 mm board
  24.0 mm under the panel (Neutrik's drawing), linked to the main board by a 2x5 IDC ribbon (CN5 ↔ CN3, both bottom side).
- Delta clone without mic stage (2026-10-22), replacing "no EQ, no trim". Input = our receiver +
  separate inverting gain stage (Delta line topology rejected, 4.7 dB noisier); HPF unity-gain
  Butterworth 87 Hz (Delta's has +3 dB; replaced by the sweepable HPF, strip v4.3, below); EQ with Delta values. Then: line gain −15 to +15 dB
  (centre detent 0 dB), Ø switch, switched HPF and 4-band EQ as the Delta (OPA1612), EQ IN, insert
  post-EQ (jumper for pre-EQ), ON switch with green LED (replaces MUTE), PAN switch, routing LEDs,
  PRE switch per aux pair (jumper: pre-fader / pre-EQ), direct out (aux 6 doubles as its level via
  DIR). Internal level stays 0 dBu; 4K7 summing stays.
- One 34-pin header per strip on a daisy-chained ribbon with crimped sockets (decided 2026-10-19;
  CN2 dropped).
- Bus = real Delta motherloom pinout (read from Delta ED3344C): GRP1-4 = SUB1-4 on pins 15/13/11/9,
  MIX R 17, MIX L 18, AUX6..1 on 20-25 (AUX1=24, AUX2=25), GND CANCEL 26, PFL 27, PFL DET 29,
  -V 30-31, +V 32-34 (pin 34 is the Delta's +48 V; a third +V conductor since 2026-10-25, `wing_power_proposal.md` W1,
  Ruslan: the IDC sockets are 1 A per contact). Spares: 19 (and 28 on the strips). **Pins 1, 3, 5, 7 are reserved for
  SUB 5-8** (Ruslan, 2026-10-27; the Venue pinout: groups 5 / 6 on 7 / 5, 7 / 8 on 3 / 1, `eight_groups_study.md`). Keep
  them unconnected on every board; the master joins its two wing headers on them (SPARE1-7) and, since D13 (`delta_crosscheck.md`,
  signed off 2026-10-28), grounds each spare (1 / 3 / 5 / 7, 19) through a bridged solder jumper JP3-JP7 beside CN2 on the
  bottom, as the Delta's LH master J2-J9 do: open them for an 8-group build. Pin 28 stays open everywhere (a Venue stereo
  input uses it as a PFL input when its inverting mute is fitted, D22: a borrowed Venue module won't PFL on our bus; a Venue
  mono input would PFL 6 dB hot through its two 22Ks, D24). Even pins 2-16 = GND.
  The 200 Delta Technical Manual (p. 134, `ref/`) lists 17 = Mix left / 18 = Mix right, the opposite of ED3344C;
  kept the ED3344C order (Ruslan, 2026-10-23; console_architecture.md 2). It confirms pin 28 = PFL Audio −VE.
- Ground cancel: 10 Ω from strip AGND to pin 26; master summing amps reference that line.
  Each master summing amp is followed by a unity differential re-inverter (sum − GCANCEL).
  No tie from GCANCEL to master ground at the master end (2026-10-19; sim: a 22 Ω tie costs ~45 dB). A 100K keeper to
  master GNDA (Ruslan, 2026-10-23) only defines the line when the master runs alone (−79 dB at N = 32); not a tie.
  Replaces SSL-style impedance-balanced bus (dropped unless the test jig says otherwise).
- Power on the ribbon (2 conductors on −V, 3 on +V since W1: pins 30-31 / 32-34); heavy ground via a 6.3 mm spade per strip.
- MIX/SUB summing resistors 4K7 (master feedback must also be 4K7). AUX/PFL 22K.
  (10K would keep real Delta modules compatible; 4K7 is ~3 dB quieter.)
- Fader post-amp +10 dB (R38 2K2; omit for unity). Hot synths >~+12 dBu clip with fader at top.
- Channel path is non-inverting (tip = hot). Master summing inverts → master must re-invert once.
- Routing switch off = resistor's bus end to clean ground (Delta practice).
- AC coupling 100 µF NP + 47K on every node feeding the bus (was 220 µF; MUSE ES, 2026-10-24); JFET (J112) soft mute;
  separate logic rails +VL/−VL and logic ground GNDD joined to GNDA at one point (NT1).
- OPA1612 in noise-critical stages and on the MIX/SUB/aux sums: an aux bus always carries every strip's 22K (noise gain
  25), where it beats NE5534 / OPA1656 by ~2 dB. OPA1656 on the PFL sum (switched bus, 1-4 sources) and the CRS
  followers (Ruslan, 2026-10-23, master parts review; replaces "NE5534 good for sub/aux summing").
- 4 subs (with inserts), 6 aux (AFL on masters), 8 stereo returns (two per group, RET1 2026-10-26), PFL only (no SIP),
  mute relay on mains.
- SSL bus compressor (Gyraf clone) as an external unit on the master insert.
- Strip v4.1 (signed off by Ruslan 2026-10-23, `strip_parts_review.md` T1-T11):
  - stability caps: 10p across both 22Ks of U6A/U6B and 22p across R67; 10p across the KHN summers' feedback and 22p
    on their + inputs; 33p across R9; 10p on PANWL/PANWR/M2/FPIN, 22p on DIRSRC;
  - parts: R15 4K7 (OL LED ~3 mA), R99 1K in series with the insert return plus C84 100p at U7B's + input (the 1K
    alone cost U7B 30-45° of margin), D10 BAT54W on +5VL (also on the master);
  - BOM: X7R 50 V ceramics, anti-surge R1/R2/R11/R71, MPNs;
  - kept: R71/R11 at 75R; no phantom on the insert send or direct out (spec note, not 50 V caps);
  - the same balanced 33p on every master/group receiver.
- Master parts (signed off by Ruslan 2026-10-23, `master_parts_review.md` S1-S8, applied in master spec v0.7):
  - GCANCEL buffer kept; 22 pF C0G on both legs of every re-inverter, 100 pF across every level buffer's 4K7.
  - Six G6K-2F-Y mute relays (main L/R/mono, C/Room L/R, phones), COM = connector, NO = driver, NC = ground;
    LM393B; reset / fast-release 4K7.
  - PFL switcher = one DG413 (the series J112s did not switch), OPA1656 CRS followers, 1 µF PFLDET debounce; PFLDET
    clamp 2 x 1N4148 + 330K reference (stops back-feed into released keys' LEDs).
  - Meters: LM2901B, BCP53-16 SOT-223 current sources with 120R, Kingbright GaP / GaAsP LEDs (no InGaN).
  - Sub AFL kept.
- Master / group stability and ratings (signed off by Ruslan 2026-10-24, `master_group_review.md` MG1-MG20, applied in
  master spec v0.8, group rev 0.2):
  - EXT receiver outputs EXT_BL/BR (they were on the R jack's ring net) + 100R build-out.
  - Phones: the 100p from the OPA1612's output, not PHO; 22p at the + input; LME49600 beside it.
  - Build-outs at the op-amp pins: solo 100R, post-amps 47R (`post_amp()`), CRS 100R, insert return 75R, meter DET
    470R (with the U3 feedback 10K on its pin side).
  - + input C0G: 10p post-amps, level buffers, group pan buffers; 22p solo, C/Room, phones. 10p not 22p in
    `level_buffer()`.
  - Insert returns 1K + 100p at the + input (`insert()`).
  - Meter peak detector reads the diode cathode, 220R, 22p; 22p across the summers; TL072HIDR.
  - Ratings: phones / ±VP 2R2 in 2512 1.5 W; anti-surge 0805 for R52/R48, the rude-solo 3K3, ±VA feeds, insert-send
    75R; 50 V X7R / C0G ceramics and MPNs (`master_lib.CAP_MPN`).
  - Kept: wing PTCs MF-RX160/72 (changed to MF-RX185/72 with the sweepable HPF, below). No mute relays on the aux outputs,
    a spec note instead (§13). No phantom on any balanced output (spec note).
  - Group bus select: one SUB and one AUX jumper per board, unique across the four (both summers rail otherwise);
    "GRP __" on the silk.
- Sweepable HPF (signed off by Ruslan 2026-10-24, `hpf_proposal.md` H1-H4; strip v4.3, master spec v0.9): a KHN
  high-pass, 21-403 Hz (85 Hz at mid rotation), unity, non-inverting, Q 0.707, tuned by RV16 (stocked Alpha A10K dual,
  dividers 330R / 13K / 5K6 into U15's integrators; U5A summer, 10p / 22p stability caps). SW11 selects HP or HIN (HPF
  out = a wire, no added noise). C91 33 µF MUSE ES doubles C38 (HIN feeds the EQ directly with the HPF out). Panel:
  Ø key y 50, HPF IN key y 61, HPF FREQ knob y 76 (right column), OL LED at (20.6, 50); CN3 to y ≈ 131.5 (ribbon
  ~136 mm). Wing PTCs MF-RX185/72 (H4), fixed in place.
- Film couplers and audio bipolars (signed off by Ruslan 2026-10-24, `film_np_proposal.md` F1-F4; strip v4.2, master
  spec v0.8 note): no X7R in the signal path. Every 2.2 µF wiper coupler and the meter averaging caps are WIMA
  MKS2C042201K00KSSD PET film (order code KEMET MMK5225K63J06L4BULK since FE1, 2026-10-29: the WIMA is obsolete, the KEMET a last-time
  buy in the same box), THT on the bottom side (13 mm: too tall for the 11.5 mm top gap). Bipolars are Nichicon
  MUSE ES 25 V in the existing footprints: 47 → 33 µF (UES1E330MPM), 220 → 100 µF (UES1E101MPM), 10 µF UES1E100MDM (discontinued: Panasonic ECE-A1EN100U since
  2026-10-25, `sourcing.md` S1, Ruslan; DRV135 sense legs and LME49600 ±VP bypasses, inside the loop / off the path).
  End-to-end LF −3 dB 2.3 Hz. Not DC coupling (rejected: faders, switches, synth DC); no polypropylene (too large at
  2.2 µF).
- All balanced outputs use the TI DRV134 family (2026-10-19): the SO-8 part, TI DRV135UA (design review R1, 2026-10-25:
  the DRV134 itself is DIP-8 / SOL-16 only), Sense pins after a 10 µF NP per leg, mute
  relay after that. Replaced THAT1646, which went EOL (THAT memo 2026-09-01). The same memo
  kills THAT 2180/2181 (bus-compressor VCA, strip VCA option) and THAT 124x.
- Design review (signed off by Ruslan 2026-10-25, `design_review.md`): group sub pan RV2 = ALPS RK09L1240015 (as RV8);
  jig R45 ERJ-P06J332V; silk "2" beside pads 1/4 of every PVA2 (placer); ON also mutes the pre-fade sends and the direct
  out (pre taps JP2-JP4 from MUTEOUT; the pre-EQ jumper setting stays ahead of the mute; PFL stays at PRE).
- Pan pot RV8 (2026-10-25, Ruslan): ALPS RK09L1240015, vertical dual 10K 1B with a centre detent (no Alpha B10K dual
  with a detent exists; the Alpha without one was the alternative). Stocked at Mouser (177) / Verical (565) on
  2026-10-25. M9 x 0.75 bushing (panel hole Ø9.5, M9 nut), Ø6 flatted shaft (the 6 mm D version of the strip's knob),
  mounting face 10 above the board like the Alpha; footprint Potentiometer_Alps_RK09L_Double_Vertical, shaft at (10, 2.5)
  from pin 1 (`placer.pot(..., sx=10)`); model `tools/models3d/alps_rk09l.py` (catalogue RV01 Drawing No.7). Netlist
  unchanged. RK097121TD57, named before, is a right-angle part.
- Ground and hum (signed off by Ruslan 2026-10-25, `ground_study.md` G1-G3; strip spec v4.4, master spec v0.10):
  - G1 harness: one 14 AWG wire per strip / group, tied under its wing's motherloom, down the master's free edge strip
    to its wing's copper bar (14 tabs) under the M4 star stud; cut list in master spec §26; never along the tub floor.
    `sim_console.py` models it by default (`SPADE_WIRE`); `console_3d.py` draws it.
  - G2 balanced-input sleeves on CHASSIS: strip J1 / J5 (+ C8 / C9), group returns, master EXT; plated CHASSIS standoff
    holes in the schematic (`MHPAD`, jack boards H1-H2 / H1-H2 / H1-H3) bond them to the panel; inserts, phones and the
    DRV134 TRS outputs keep GNDA. Group: CHASSIS off the link (`link_pins(skip=)`).
  - G3 strip receiver buffered: U16 OPA1656 followers, 1M per leg (R10, R112), 220R in (R110, R111), 100 pF C0G at
    each + input (C94, C95: without them the 220R and the OPA1656's input capacitance cost ~13°), 100R build-outs
    (R113, R114; ≥ 48.5° for any load, 54° in the strip deck, fitted model; 61.7° on TI's own OPA1656 model, 2026-10-28); J1's normals short both legs to GNDA when empty. CMRR vs a 1K synth output
    26 -> 54 dB (worst 5 %). U16 stays OPA1656: the PSU worst corner of ~4.24 A on +V is accepted (Ruslan, 2026-10-25).
- Ground and hum, part 2 (signed off by Ruslan 2026-10-25, `ground_study.md` §10 G2b / G3b): every DRV134 TRS output's
  sleeve on CHASSIS (group sub / aux, master aux 5 / 6, C/Room); the group return and master EXT receivers buffered as
  the strip's U16 (`master_lib.receiver()`; followers created last via `master_lib.DEFER`, so no existing ref moves);
  L jack normals short an empty return / EXT. +78 mA per rail; worst corner ~4.33 A on +V.
- Strip v4.5 (signed off by Ruslan 2026-10-25, `gaps_proposal.md` K1 / K3): C96 2.2 µF film in series with R32 (PFL
  send DC block); overload detector C12 100n and U4B as a ~150 ms hold stage (R115 1M, C97 220n).
- Strip v4.7 (signed off by Ruslan 2026-10-26, `feature_gaps.md` MET1): D2 = Kingbright WP3VEGW red / green bicolour
  (common cathode; own footprint LED_D3.0mm-3_P2.00mm) in the OL hole; green = signal from ~-20 dBu with U17 (LM393B,
  as U4 one level lower, ~150 ms hold), red = overload as before; PNP high-side switches Q3 / Q4 (lit only), Q5 holds
  Q4 off during overload (red alone). Detector left of the fader (y 298-324). +~4 mA per strip on +V; worst corner
  ~4.38 A. `sim/review/gaps/ol.py` covers both colours. `panel_layout.layout()` takes parts in reference order (the
  artwork had depended on the board's footprint order).
- Strip v4.8 (signed off by Ruslan 2026-10-26, `pan_buffer_proposal.md` PAN1): pan buffer L is U8B (beside U3 and the
  pan pot), U2B the tied-off spare; netlist unit swap only, parts and BOM unchanged. `place_strip.py` fixes U2, U3, U8,
  C16 / C17 / C79 and U2's post-amp parts (R18, R38, JP1, R44) so the packer keeps them.
- Group v0.12 (signed off by Ruslan 2026-10-26, `feature_gaps.md` RET1): a second stereo return on every group
  (`stereo_return()` in gen_group.py; U12-U15, RV5, SW8-SW11, D4; every old ref kept). Jack board 7 jacks (4th row
  RET 2 L / R at y 78), 38 x 93.5 mm, standoffs below the last row, return 2 on its own 2x5 link (CN2 <-> CN4) beside
  the unchanged 2x8. Main board from y 94.5; RET 1 / RET 2 knobs + PFL at y 106 / 128, return 2's MIX / 1-2 / 3-4 at
  y 150, AUX at 172; links on the bottom at y ~190. Console ~3.31 / 2.79 A typical, worst corner ~4.54 A on +V (wing
  ~2.07 A, above the MF-RX250/72's hold): accepted (Ruslan, 2026-10-26), as the 4.33 A corner before.
- Knobs (signed off by Ruslan 2026-10-25, `knob_proposal.md` KN1-KN3): Elma classic collet knob Ø14.5, matt black with
  a line, 021-3525 (1/4", 349) and 021-3425 (6 mm, RK09L pans, 28); no nut covers. Caps Elma 040-30x5 matt without a
  line: GAIN / SOLO red, EQ gains / C/ROOM / PHONES grey, FREQs / HPF / RETURN blue, AUX 1-2 yellow, AUX 3-4 green, AUX
  5-6 / PAN / SUB PAN black. C/ROOM takes the same knob. Print and model at Ø14.5 (`models3d/knob.py`, `panel_layout.py`).
  Key caps (KC1): C&K PV round, PVGY / PVWH (routing, group MIX) / PVRD (PFL, AFL) / PVBK (ON only; no green PV cap
  exists, DIR grey). Fader caps (KC2): Sifam LK111 01 black with a white line; coloured 8 x 1.2 caps (white strips, red
  groups, yellow master) only if a trial at the fader sample check fits the BP blade.
- Frame rails (signed off by Ruslan 2026-10-25, `frame_proposal.md` FR1-FR3): two 6060-T6 / 6082 flat bars 50 x 10
  on edge, 1227.2 mm (2 mm into each walnut cheek's rebate, 2 x M4 per end), on the panel screw lines y -8 / 500,
  30 M3 tapped holes each from the panel screw pattern (`panel_layout.rail_holes()`); 0.21 mm sag under the console,
  0.53 mm under 100 N at mid-span, no centre post. Panels bond through bare tapped holes + star washers; one 2.5 mm2
  bond per rail to the M4 star. Drawing `frame/` (`python3 tools/frame_fab.py`).
- PSU case (signed off by Ruslan 2026-10-26, `psu_case_proposal.md` PC1-PC3): Hammond 1402KV (254 x 244 x 99 vented
  aluminium); Fischer SK 47 75 SA on the FRONT end panel (the 1402K's sides are split by an extrusion), the TO-220s
  through a window onto it (tab backs 1.68 mm proud of the board edge, `place_psu.py` OVERHANG); LRS-150s stacked
  behind the board; rear Schurter DD11 (inlet + 2-pole switch + fuse), NC7FD-LX, M4 earth stud; front LED only.
  +V LDO junction 108 / 113 C at 30 / 35 C room at the 4.33 A worst corner (~111 / 116 C at today's 4.54 A, `psu_spec.md`). Drilling `psu_case/`.
- PSU ADJ divider (2026-10-28, `project_review.md` RV1): R2 / R11 (1K5, 15.7 V across them = 164 mW) are Panasonic
  ERJ-P06F1501V, 1206 0.5 W (the 0805 code was at 131 % of its rating); PSU re-placed (23 parts re-packed, DRC clean).
- Console thermal (signed off by Ruslan 2026-10-26, `thermal_study.md` TH1-TH3): 98 W inside the tub; closed it would
  run ~41 K above the room (31-60 K; MUSE ES ~1.8 years at 4 h/day). Vented tub: floor inlet slots inside the front rail
  (>= 1.2 m x 20 mm, mesh; the underside open, `tub_proposal.md`), the back rail's 30 vent slots 30 x 25 mm on its neutral axis
  (`panel_layout.vent_slots()`), a back-trim plenum with a top slot (>= 1.2 m x 20 mm): ~16 K. No fan (a 120 mm fan is the
  fallback if the built console's rise exceeds 20 K); MUSE ES kept. Model `sim/review/thermal/tub_thermal.py`.
- Tub (signed off by Ruslan 2026-10-26, `tub_proposal.md` TB1-TB4): walnut cheeks (601 x 212, carrying the 9 deg tilt,
  on the desk), 12 mm birch-ply floor in dados with 30 inlet slots 100 x 10 + mesh, walnut arm-rest, plenum (12 mm rear
  wall with the NC7MD-LX, 14 mm cap strip; the 21 mm channel's open top is the outlet, 0.026 m2), open underside; console
  raised 25 mm (panel front edge 99 mm above the desk). Supply cable through back-rail vent slot 14. Geometry in
  `panel_layout.py`; drawings `tub/` (`python3 tools/tub_fab.py`).
- Strip v4.9 (signed off by Ruslan 2026-10-27; `met1_ret1_review.md` P1 / P2, `emc_placement_study.md` E6):
  - **P1 / P2:** R126 / R127 1K between U4A / U17A and their hold caps (discharge peak 15.9 mA, inside the LM393B's
    25 mA); C100 100n on VREF.
  - **E6:** C101 / C102 10n base to emitter on Q3 / Q4 (SIG_B's 0.75 V edges 17.6 us / 1.04 ms; the LED current still
    switches in us).
  - **Declined / decided:** P3 declined. P4: welded blind M3 studs on the panel backs if the maker offers them
    (pressed-in PEM studs need a 1.6 mm sheet; the panels are 1.5), else the main-board standoffs are spacers. The
    jack-board standoffs (CHASSIS bond, G2) then get countersunk M3 screws (Ø3.4, 90° to Ø6.5) with star washers.
    Positions are in `panels/` (DXF layers STUDS / CSK_NO_STUDS, hole tables), clear of cut-outs and print.
  - **Placement:** placed by `placer.py` `moves_only` (never packed), so no other part moved.
- Strip v5.0 (signed off by Ruslan 2026-10-27, `cs1_proposal.md` CS1, from `console_survey.md`): the overload LED reads
  RECV, GOUT, EQOUT, PRESRC and FPOST, each through 1K into a BAV99 (D1, D12-D15). Positive peaks charge PK (U4A, as
  before); negative peaks pull OL_NN (C103 // R134 470K, PK's mirror), read by U18A (new LM393B, U18B spare) through
  R132 4M99 / R133 10M from +VL, wired-OR onto OL_HOLD through R135 1K. Thresholds are ratios of +VL only (+18.4 dBu;
  pulses +9.01 / -9.30 V). Placement by `moves_only`: only D1 moved (DO-35 -> SOT-23 on the bottom). PK / OL_NN are
  Switching class (`netrules.py` DETECTOR), ~390 mm. 902 pins, 310 parts; +~0.5 mA per strip on +VL.
- DRV135 coupler pairs (signed off by Ruslan 2026-10-27, `cs11b_proposal.md` CS11b): each console DRV135's two 10 uF
  couplers (groups and master; not the jig stub or the LME49600 bypasses) are a pair sorted within 2 % at 100 Hz; BOM MPN
  note, 10 sorting spares in `order_bom.py`, the sorting rule in `offboard_bom.md`. Output balance worst 5 % at 1 kHz /
  100 Hz -32 / -20 -> -60 / -47 dB.
- DRV135 loop resistors (signed off by Ruslan 2026-10-27, `cs4c_proposal.md` CS4c): 22R ERJ-P06J220V between each
  DRV135 output pin and its 10 uF, inside the Sense loop (group R119-R122, master R222-R235; jig stub without, `rx=False`),
  made last by `master_lib.drv_loop_rs()`. 8 kV into the output pin 5.9 -> 0.84 A; differential output impedance
  52.6 -> 73.8 ohm, -0.16 dB into 600R. Group 789 pins / 283 parts, master 1786 / 617.
- Group / master jack-link clamps (signed off by Ruslan 2026-10-27, `cs4b_proposal.md` CS4b): a BAV199 on every
  jack-link signal at the header, as the strip's (group D7-D20 at CN3 / CN4, 14 per board; master D79-D102 at CN5, 24),
  made last by `master_lib.link_clamps()` so no ref moved. Phantom on a DRV135 output now leaves its 10 uF 25 V coupler
  and Sense pin at 17.7 V (47.7 before); the no-phantom note stays. Group 781 pins / 279 parts, master 1758 / 603.
- Strip v5.6 / master v0.13 / group (signed off by Ruslan 2026-10-28, `clicks_proposal.md` RV3 / RV4 / RV7 / RV8 / RV9 from
  `project_review.md`): strip R142 1M from GOUT to U1B's − input (the gain pot's wiper was its only DC feedback) and
  C107 33 µF NP in the direct out's cold leg (R73, the same ERJ-P06J750V as R71; both legs 75R + 33 µF, CMRR limit at
  50 Hz ~46 → ~60 dB); master C194 / C195 2.2 µF films ahead of the aux 5 / 6 AFL 22Ks and group C98 the same (the
  level buffers' 6-25 mV DC no longer ticks onto PFL), master C196 / C197 33 µF NP in the phones gain-set legs (DC gain
  1: 19 / 79 mV → 6 / 25 mV on the cans under the relay; 2.2 Hz, a D10 100 µF found no spot), the −V-loss comparator U10B's + input on +1.0 V (R238 51K /
  R239 10K from VREF6) with R53 51K → 64K9 (trip −14.3 V, was −14.4; with −V lost the inputs stay inside the LM393B's
  range: SENSE_N +0.34 V normal, +4.7 V fault). Made last (the proposal's DEFER would have shifted 17 / 18 refs: the
  parts are created at the end of gen_master.py / gen_group.py instead), placed by moves_only at probed spots,
  nothing else moved. Strip 941 pins / 327 parts, master 1818 / 631, group 807 / 292.
- Strip v5.5 (signed off by Ruslan 2026-10-28, `eqmid_proposal.md` EQM1): the mid ranges are the Delta's measured ones
  (Audio Precision plots, 200 Delta Tech Manual p.17): HI-MID R86 / R87 392R and R56 / R57 4K99 (598 Hz-9.93 kHz), LO-MID
  R60 / R61 4K22 (165 Hz-2.54 kHz); the mid-band tuning entry's 430R / 13K / 4K7 is now per band. Boost / Q / noise /
  stability unchanged; FREQ numerals and four sim_netlist peak checks follow.
- Strip v5.4 (signed off by Ruslan 2026-10-27, `cs2_proposal.md` CS2 Option A): the Delta's -4.4 dB pan law. U8B / U3A at
  1.22x (R137 / R140 2K2, R138 / R141 10K, C105 / C106 22p C0G across the 2K2s for stability) with R136 / R139 3K3 from
  each output back to its wiper: -2.7 dB centre, +1.7 dB hard. Mix +3.3 dB at centre (S/N unchanged, summer headroom
  29.5 -> 26.2 dB per source); PAN off stays POST (1.7 dB under a hard pan). The old -6 dB was never a decision.
  937 pins, 325 parts.
- C/Room DIM (signed off by Ruslan 2026-10-28, `cs7_proposal.md` CS7; reverses console_architecture's "monitor dim"
  exclusion): SW4 (PVA2, latching, grey cap) beside POWER at (29.16, 178); R236 / R237 91K between CRSB and each C/ROOM pot
  top (CRP_L / R), shorted by the released key: -20.0..-20.75 dB on C/Room only. Main R's DRV135 U8 and C47-C50 / R224 /
  R225 on the bottom beside the key. Master 1796 pins / 620 parts.
- Group sub pan law (signed off by Ruslan 2026-10-28, `cs2b_proposal.md` CS2b): the strip's (CS2) on every group, so the
  sub pan copies the strip again (master spec §12). U3B / U5A at 1.22x (R124 / R127 2K2 with C96 / C97 22p C0G across
  them, R125 / R128 10K), R123 / R126 3K3 from each output back to its wiper: -2.7 dB centre, +1.7 dB hard (ED2778A, the
  Delta's group module, pans passively at -4.6 dB). Sub to MIX +3.3 dB at centre. Made last, placed by moves_only under
  U3 / U5 (<= 5.9 mm from the - inputs); nothing else moved. Group 805 pins / 291 parts.
- Strip v5.3 / group (signed off by Ruslan 2026-10-27, `cs6_proposal.md` CS6): R1-R4 (10R to +VA / -VA / +VL / -VL) on
  every strip and group are Vishay M25SI fusibles (M251206BB1009JP500, 1206, 0.25 W): a short behind one opens it in
  < 0.07 s and only that module goes quiet (the wing PTC never reached its trip current). **Power the console down
  before plugging or unplugging a module** (a live plug can open them; `offboard_bom.md`). Strip R1-R4 placed by
  moves_only (C2 / C4 fixed, old spots kept out); the group's packed as before.
- Strip v5.2 (signed off by Ruslan 2026-10-27, `cs4_proposal.md` CS4): a BAV199 at CN3 on each jack-link signal (D18
  IN_T, D19 IN_R, D20 RET_RAW, D21 SEND, D22 DO_T; pin 3 the signal, pin 2 +VA, pin 1 -VA), ahead of every series
  part: ESD into the op-amps 50-100x lower, phantom on SEND / DO_T clamped (C51 / C52 17.7 V, not 41.9; the no-phantom
  rule stays). TVS at the jacks rejected for its distortion. 921 pins, 317 parts; a "JACK LINK CLAMPS" block, 18 pages.
- Strip v5.1 / group (signed off by Ruslan 2026-10-27, `cs10_proposal.md` CS10, from `console_survey.md` §7): a reverse
  Schottky across each audio rail of every ribbon board, Nexperia PMEG4010CEH (40 V 1 A, SOD-123F): strip D16 (K +VA,
  A GNDA) / D17 (K GNDA, A -VA) beside C1 / C3; group D5 / D6 beside its C1 / C2, created last so no group ref moved.
  A lost supply rail (wing PTC, open ribbon conductor) no longer reverses the polar 220 uF reservoirs (simulated
  2.5-12.7 V without, 0.36 V with). Logic rails (+-VL) need none. 906 strip pins, 312 parts; group 739 pins, 265 parts.
- Board layers (Ruslan, 2026-10-27, `layer_study.md`): the strip, group and master main boards are 4-layer (In1.Cu "GND" a
  solid GNDA plane, the return for F.Cu; In2.Cu "GND2" GNDA fill, the return for B.Cu, with the rails and the GNDD spine
  only in a left-edge rail corridor, rule area RAILS, `placer.py` `rails=`; branches to the ICs on F.Cu / B.Cu; signals
  on F.Cu / B.Cu; the fab's 1.6 mm stackup; `placer.py` `layers=4`), every jack board, both jig boards and the PSU 2-layer. JLCPCB quotes
  2026-10-27: +$27 for phase 1, +$93 for the whole console. 4-layer DRC rules in `tools/netrules.py`.
- Faders (2026-10-23): Bourns PTB0143-2010BPA103 (strips, groups) / PTB0144-2010BPA103 (master), stocked, BP lever
  (8.0 x 1.3 mm flat blade, 5.0 mm above the panel), caps Sifam LK110 tang 01 (8.0 x 1.2, socket 4.0 deep: 1.0 mm
  above the panel; the Delta's "SIF low profile" knob; black LK111 01 with a white line (KC2, 2026-10-25;
  coloured bodies are Sifam made-to-order, MOQ 1000); sample-check the 1.2 socket on a real blade). Rejected after
  research: the AP 4 mm-fork audio codes (not sold, factory MOQ ~800), ALPS RSA0N (T-bar lever, sits too low), TT PS100,
  Song Huei, Penny+Giles; no stocked 100 mm A10K fader with a 4 mm lever exists. Panel slot >= 108 x 1.3 (model 110 x 2.4).
- VCA (decided 2026-10-19): Sound Semiconductor SSI2162 for the bus compressor (sidechain
  rescaled 6.1 → 33 mV/dB; THAT2181 backorder route rejected) and as a plug-in module for the
  strip VCA option.

## Added 2026-10-28 (after the move; the one-liners are in CLAUDE.md)
- Insert jacks tip = send, ring = return, console-wide (D1, `delta_crosscheck.md`, decided by Ruslan 2026-10-28; strip
  spec §7 / 16.4, master spec §4, `delta_clone_comparison.md` §2). The Delta is wired the other way round everywhere
  (ring = send: ED3344A JSK2, ED2780 sht 2 JSK1, manual p.124 / 128); no document had recorded ours and it was never
  decided (gen.py's `{'T': 'SEND', 'R': 'RET_RAW'}` followed the common convention). Kept because electrically the
  two are identical (75R build-out, 47K bleed, the normalling works both ways), so only which cables fit is at stake:
  tip = send is what the commercial insert lead (TS marked SEND on the tip), Mackie, A&H, Yamaha, Behringer and the
  later Soundcraft (Spirit, Ghost) use; ring = send serves Delta-era looms only. Switch (a T / R swap in four
  generators) only if Delta-wired looms or a ring = send patchbay are to be reused. Panel legend "INSERT tip = send" at
  the next panel regeneration.
- Soft mute topology (D3 / D11, 2026-10-28, documentation only): ours is two shunt J112s in a 4K7 ladder into a
  follower with one 220K / 100n ramp from the key, not the Delta's series J112 into a virtual earth plus a shunt J112
  with a cap-isolated source and a MUTE / MUTE-bar inverter pair. Kept: no series FET and no remote-mute input to
  drive; depth (86 dB simulated vs 100-110 dB) is measured at the jig (CS8); the Delta's cap-isolated shunt source is
  the fallback for RV5's DC on the fader top. `delta_clone_comparison.md` §2 and `console_survey/delta.md` T7 had
  called it "the same circuit"; corrected.
- XLR shells on CHASSIS (2026-10-28, `project_review.md` §2 minor items): the NC3MAV / NC3MAH footprints' shell pad G
  had no symbol pin, so the master jack board's J3-J5 and the jig stub's XLR shells were unconnected although master
  spec §7 said "shell to chassis"; with anodised panels they would have floated. Project symbol `XLR3_Shell` (KiCad's
  XLR3 plus pin G) with G on CHASSIS in `master_lib` / gen_master.py / gen_jig.py; nothing moved on either board.
- Resistor film TF1 (signed off by Ruslan 2026-10-29, `thin_film_proposal.md`): every plain 0805 resistor up to 1M is
  Yageo RT0805FRE07 thin film (1 %, 50 ppm/°C, 0.125 W, 150 V) by the sourcing rule in `order_bom.py`; RC0805FR thick
  film stays above 1M (DC positions, no thin-film part) and as the fallback for a value out of stock; the anti-surge
  ERJ-P06 positions (build-outs, DRV loop 22R, feeds, rude-solo 3K3, PSU ADJ), the 2512 2R2 and the fusibles keep
  their parts. Why: thick film's voltage coefficient is a measurable third-harmonic distortion near full swing in
  every feedback / EQ / summing resistor of 24 channels, its drift and tempco are 2-4× worse, and the Delta's own
  resistors are metal film 2 %; the noise argument does not apply (no DC across the audio resistors). ~€80-150 over
  the console. Rejected: thin film only in the ~20 full-swing values (a list to maintain for ~€30), deciding on the
  jig's THD (the fear is about the part class, not a number); MELF (Ruslan, 2026-10-29, "so no MELFs"): the same
  metal-film physics as the thin-film chips, better only in pulse energy, power and voltage, none of which this design
  needs (the pulse positions are the 188 anti-surge parts, where the film type cannot show: < 1 % of the signal across
  a build-out, the 22R inside the DRV135 loop, the rest DC); it would cost a footprint change on every plain resistor
  (MicroMELF +12 % courtyard, MiniMELF +77 %), so a full re-placement of every board, round bodies in assembly and
  3-10× the price (~€400-600).
- Strip v5.7 / master v0.14 (signed off by Ruslan 2026-10-29, `clicks_followup_proposal.md` RV3b / RV9b, from the
  independent review of the clicks batch): strip R143 47K from DO_R to AGND and D23 BAV199 on DO_R at CN3, so the
  direct out's ring has the DC bleed and the clamp the tip has (RV3's C107 had left it with neither: phantom would have
  charged the 25 V cap to ~48 V; with the clamp 17.7 V as C52); master R240 4K7 from the relay driver Q1's base to
  GNDD: with −V lost, −VL sits at ~+0.5 V and the comparators' low output is referenced to it, so the base saw
  0.65-1.0 V and a closed relay could stay held at 11-21 % of its coil current at the LM393B's V_OL corner; divided 2:1
  the coil current is 0.2 µA, the 2.80 s close unchanged (`sim/review/clicks/mute_rbe.cir`, `sim/mute.cir` v5). Both
  made last and placed by moves_only (D23 beside D22, R143 beside C107, R240 under Q1), nothing else moved. Strip 946
  pins / 329 parts, master 1820 / 632. Bench item: open the −V wire with the relays closed.
