# goa-console — decisions made, in full

Moved out of `CLAUDE.md` on 2026-10-28 (`docs/reviews/project_review.md` RV13), text unchanged. `CLAUDE.md` keeps one line per decision;
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
  wing PTCs: +V Bourns MF-RX250/72 since 2026-10-25 (`docs/proposals/wing_power_proposal.md` W2: 2.5 A hold on three conductors,
  0.83 A per contact at hold; own 10.16 mm footprint; F1 in its row, F3 vertical by the right edge), −V MF-RX185/72
  since 2026-10-24 (`docs/proposals/hpf_proposal.md` H4; was MF-RX160/72, still on the jig stub; 72 V: a pin 31/32 short puts 34 V
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
  -V 30-31, +V 32-34 (pin 34 is the Delta's +48 V; a third +V conductor since 2026-10-25, `docs/proposals/wing_power_proposal.md` W1,
  Ruslan: the IDC sockets are 1 A per contact). Spares: 19 (and 28 on the strips). **Pins 1, 3, 5, 7 are reserved for
  SUB 5-8** (Ruslan, 2026-10-27; the Venue pinout: groups 5 / 6 on 7 / 5, 7 / 8 on 3 / 1, `docs/studies/eight_groups_study.md`). Keep
  them unconnected on every board; the master joins its two wing headers on them (SPARE1-7) and, since D13 (`docs/reviews/delta_crosscheck.md`,
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
- Strip v4.1 (signed off by Ruslan 2026-10-23, `docs/reviews/strip_parts_review.md` T1-T11):
  - stability caps: 10p across both 22Ks of U6A/U6B and 22p across R67; 10p across the KHN summers' feedback and 22p
    on their + inputs; 33p across R9; 10p on PANWL/PANWR/M2/FPIN, 22p on DIRSRC;
  - parts: R15 4K7 (OL LED ~3 mA), R99 1K in series with the insert return plus C84 100p at U7B's + input (the 1K
    alone cost U7B 30-45° of margin), D10 BAT54W on +5VL (also on the master);
  - BOM: X7R 50 V ceramics, anti-surge R1/R2/R11/R71, MPNs;
  - kept: R71/R11 at 75R; no phantom on the insert send or direct out (spec note, not 50 V caps);
  - the same balanced 33p on every master/group receiver.
- Master parts (signed off by Ruslan 2026-10-23, `docs/reviews/master_parts_review.md` S1-S8, applied in master spec v0.7):
  - GCANCEL buffer kept; 22 pF C0G on both legs of every re-inverter, 100 pF across every level buffer's 4K7.
  - Six G6K-2F-Y mute relays (main L/R/mono, C/Room L/R, phones), COM = connector, NO = driver, NC = ground;
    LM393B; reset / fast-release 4K7.
  - PFL switcher = one DG413 (the series J112s did not switch), OPA1656 CRS followers, 1 µF PFLDET debounce; PFLDET
    clamp 2 x 1N4148 + 330K reference (stops back-feed into released keys' LEDs).
  - Meters: LM2901B, BCP53-16 SOT-223 current sources with 120R, Kingbright GaP / GaAsP LEDs (no InGaN).
  - Sub AFL kept.
- Master / group stability and ratings (signed off by Ruslan 2026-10-24, `docs/reviews/master_group_review.md` MG1-MG20, applied in
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
- Sweepable HPF (signed off by Ruslan 2026-10-24, `docs/proposals/hpf_proposal.md` H1-H4; strip v4.3, master spec v0.9): a KHN
  high-pass, 21-403 Hz (85 Hz at mid rotation), unity, non-inverting, Q 0.707, tuned by RV16 (stocked Alpha A10K dual,
  dividers 330R / 13K / 5K6 into U15's integrators; U5A summer, 10p / 22p stability caps). SW11 selects HP or HIN (HPF
  out = a wire, no added noise). C91 33 µF MUSE ES doubles C38 (HIN feeds the EQ directly with the HPF out). Panel:
  Ø key y 50, HPF IN key y 61, HPF FREQ knob y 76 (right column), OL LED at (20.6, 50); CN3 to y ≈ 131.5 (ribbon
  ~136 mm). Wing PTCs MF-RX185/72 (H4), fixed in place.
- Film couplers and audio bipolars (signed off by Ruslan 2026-10-24, `docs/proposals/film_np_proposal.md` F1-F4; strip v4.2, master
  spec v0.8 note): no X7R in the signal path. Every 2.2 µF wiper coupler and the meter averaging caps are WIMA
  MKS2C042201K00KSSD PET film (order code KEMET MMK5225K63J06L4BULK since FE1, 2026-10-29: the WIMA is obsolete, the KEMET a last-time
  buy in the same box), THT on the bottom side (13 mm: too tall for the 11.5 mm top gap). Bipolars are Nichicon
  MUSE ES 25 V in the existing footprints: 47 → 33 µF (UES1E330MPM), 220 → 100 µF (UES1E101MPM), 10 µF UES1E100MDM (discontinued: Panasonic ECE-A1EN100U since
  2026-10-25, `docs/build/sourcing.md` S1, Ruslan; DRV135 sense legs and LME49600 ±VP bypasses, inside the loop / off the path).
  End-to-end LF −3 dB 2.3 Hz. Not DC coupling (rejected: faders, switches, synth DC); no polypropylene (too large at
  2.2 µF).
- All balanced outputs use the TI DRV134 family (2026-10-19): the SO-8 part, TI DRV135UA (design review R1, 2026-10-25:
  the DRV134 itself is DIP-8 / SOL-16 only), Sense pins after a 10 µF NP per leg, mute
  relay after that. Replaced THAT1646, which went EOL (THAT memo 2026-09-01). The same memo
  kills THAT 2180/2181 (bus-compressor VCA, strip VCA option) and THAT 124x.
- Design review (signed off by Ruslan 2026-10-25, `docs/reviews/design_review.md`): group sub pan RV2 = ALPS RK09L1240015 (as RV8);
  jig R45 ERJ-P06J332V; silk "2" beside pads 1/4 of every PVA2 (placer); ON also mutes the pre-fade sends and the direct
  out (pre taps JP2-JP4 from MUTEOUT; the pre-EQ jumper setting stays ahead of the mute; PFL stays at PRE).
- Pan pot RV8 (2026-10-25, Ruslan): ALPS RK09L1240015, vertical dual 10K 1B with a centre detent (no Alpha B10K dual
  with a detent exists; the Alpha without one was the alternative). Stocked at Mouser (177) / Verical (565) on
  2026-10-25. M9 x 0.75 bushing (panel hole Ø9.5, M9 nut), Ø6 flatted shaft (the 6 mm D version of the strip's knob),
  mounting face 10 above the board like the Alpha; footprint Potentiometer_Alps_RK09L_Double_Vertical, shaft at (10, 2.5)
  from pin 1 (`placer.pot(..., sx=10)`); model `tools/models3d/alps_rk09l.py` (catalogue RV01 Drawing No.7). Netlist
  unchanged. RK097121TD57, named before, is a right-angle part.
- Ground and hum (signed off by Ruslan 2026-10-25, `docs/studies/ground_study.md` G1-G3; strip spec v4.4, master spec v0.10):
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
- Ground and hum, part 2 (signed off by Ruslan 2026-10-25, `docs/studies/ground_study.md` §10 G2b / G3b): every DRV134 TRS output's
  sleeve on CHASSIS (group sub / aux, master aux 5 / 6, C/Room); the group return and master EXT receivers buffered as
  the strip's U16 (`master_lib.receiver()`; followers created last via `master_lib.DEFER`, so no existing ref moves);
  L jack normals short an empty return / EXT. +78 mA per rail; worst corner ~4.33 A on +V.
- Strip v4.5 (signed off by Ruslan 2026-10-25, `docs/proposals/gaps_proposal.md` K1 / K3): C96 2.2 µF film in series with R32 (PFL
  send DC block); overload detector C12 100n and U4B as a ~150 ms hold stage (R115 1M, C97 220n).
- Strip v4.7 (signed off by Ruslan 2026-10-26, `docs/reviews/feature_gaps.md` MET1): D2 = Kingbright WP3VEGW red / green bicolour
  (common cathode; own footprint LED_D3.0mm-3_P2.00mm) in the OL hole; green = signal from ~-20 dBu with U17 (LM393B,
  as U4 one level lower, ~150 ms hold), red = overload as before; PNP high-side switches Q3 / Q4 (lit only), Q5 holds
  Q4 off during overload (red alone). Detector left of the fader (y 298-324). +~4 mA per strip on +V; worst corner
  ~4.38 A. `sim/review/gaps/ol.py` covers both colours. `panel_layout.layout()` takes parts in reference order (the
  artwork had depended on the board's footprint order).
- Strip v4.8 (signed off by Ruslan 2026-10-26, `docs/proposals/pan_buffer_proposal.md` PAN1): pan buffer L is U8B (beside U3 and the
  pan pot), U2B the tied-off spare; netlist unit swap only, parts and BOM unchanged. `place_strip.py` fixes U2, U3, U8,
  C16 / C17 / C79 and U2's post-amp parts (R18, R38, JP1, R44) so the packer keeps them.
- Group v0.12 (signed off by Ruslan 2026-10-26, `docs/reviews/feature_gaps.md` RET1): a second stereo return on every group
  (`stereo_return()` in gen_group.py; U12-U15, RV5, SW8-SW11, D4; every old ref kept). Jack board 7 jacks (4th row
  RET 2 L / R at y 78), 38 x 93.5 mm, standoffs below the last row, return 2 on its own 2x5 link (CN2 <-> CN4) beside
  the unchanged 2x8. Main board from y 94.5; RET 1 / RET 2 knobs + PFL at y 106 / 128, return 2's MIX / 1-2 / 3-4 at
  y 150, AUX at 172; links on the bottom at y ~190. Console ~3.31 / 2.79 A typical, worst corner ~4.54 A on +V (wing
  ~2.07 A, above the MF-RX250/72's hold): accepted (Ruslan, 2026-10-26), as the 4.33 A corner before.
- Knobs (signed off by Ruslan 2026-10-25, `docs/proposals/knob_proposal.md` KN1-KN3): Elma classic collet knob Ø14.5, matt black with
  a line, 021-3525 (1/4", 349) and 021-3425 (6 mm, RK09L pans, 28); no nut covers. Caps Elma 040-30x5 matt without a
  line: GAIN / SOLO red, EQ gains / C/ROOM / PHONES grey, FREQs / HPF / RETURN blue, AUX 1-2 yellow, AUX 3-4 green, AUX
  5-6 / PAN / SUB PAN black. C/ROOM takes the same knob. Print and model at Ø14.5 (`models3d/knob.py`, `panel_layout.py`).
  Key caps (KC1): C&K PV round, PVGY / PVWH (routing, group MIX) / PVRD (PFL, AFL) / PVBK (ON only; no green PV cap
  exists, DIR grey). Fader caps (KC2): Sifam LK111 01 black with a white line; coloured 8 x 1.2 caps (white strips, red
  groups, yellow master) only if a trial at the fader sample check fits the BP blade.
- Frame rails (signed off by Ruslan 2026-10-25, `docs/proposals/frame_proposal.md` FR1-FR3): two 6060-T6 / 6082 flat bars 50 x 10
  on edge, 1227.2 mm (2 mm into each walnut cheek's rebate, 2 x M4 per end), on the panel screw lines y -8 / 500,
  30 M3 tapped holes each from the panel screw pattern (`panel_layout.rail_holes()`); 0.21 mm sag under the console,
  0.53 mm under 100 N at mid-span, no centre post. Panels bond through bare tapped holes + star washers; one 2.5 mm2
  bond per rail to the M4 star. Drawing `frame/` (`python3 tools/frame_fab.py`).
- PSU case (signed off by Ruslan 2026-10-26, `docs/proposals/psu_case_proposal.md` PC1-PC3): Hammond 1402KV (254 x 244 x 99 vented
  aluminium); Fischer SK 47 75 SA on the FRONT end panel (the 1402K's sides are split by an extrusion), the TO-220s
  through a window onto it (tab backs 1.68 mm proud of the board edge, `place_psu.py` OVERHANG); LRS-150s stacked
  behind the board; rear Schurter DD11 (inlet + 2-pole switch + fuse), NC7FD-LX, M4 earth stud; front LED only.
  +V LDO junction 108 / 113 C at 30 / 35 C room at the 4.33 A worst corner (~111 / 116 C at today's 4.54 A, `psu_spec.md`). Drilling `psu_case/`.
- PSU ADJ divider (2026-10-28, `docs/reviews/project_review.md` RV1): R2 / R11 (1K5, 15.7 V across them = 164 mW) are Panasonic
  ERJ-P06F1501V, 1206 0.5 W (the 0805 code was at 131 % of its rating); PSU re-placed (23 parts re-packed, DRC clean).
- Console thermal (signed off by Ruslan 2026-10-26, `docs/studies/thermal_study.md` TH1-TH3): 98 W inside the tub; closed it would
  run ~41 K above the room (31-60 K; MUSE ES ~1.8 years at 4 h/day). Vented tub: floor inlet slots inside the front rail
  (>= 1.2 m x 20 mm, mesh; the underside open, `docs/proposals/tub_proposal.md`), the back rail's 30 vent slots 30 x 25 mm on its neutral axis
  (`panel_layout.vent_slots()`), a back-trim plenum with a top slot (>= 1.2 m x 20 mm): ~16 K. No fan (a 120 mm fan is the
  fallback if the built console's rise exceeds 20 K); MUSE ES kept. Model `sim/review/thermal/tub_thermal.py`.
- Tub (signed off by Ruslan 2026-10-26, `docs/proposals/tub_proposal.md` TB1-TB4): walnut cheeks (601 x 212, carrying the 9 deg tilt,
  on the desk), 12 mm birch-ply floor in dados with 30 inlet slots 100 x 10 + mesh, walnut arm-rest, plenum (12 mm rear
  wall with the NC7MD-LX, 14 mm cap strip; the 21 mm channel's open top is the outlet, 0.026 m2), open underside; console
  raised 25 mm (panel front edge 99 mm above the desk). Supply cable through back-rail vent slot 14. Geometry in
  `panel_layout.py`; drawings `tub/` (`python3 tools/tub_fab.py`).
- Strip v4.9 (signed off by Ruslan 2026-10-27; `docs/reviews/met1_ret1_review.md` P1 / P2, `docs/studies/emc_placement_study.md` E6):
  - **P1 / P2:** R126 / R127 1K between U4A / U17A and their hold caps (discharge peak 15.9 mA, inside the LM393B's
    25 mA); C100 100n on VREF.
  - **E6:** C101 / C102 10n base to emitter on Q3 / Q4 (SIG_B's 0.75 V edges 17.6 us / 1.04 ms; the LED current still
    switches in us).
  - **Declined / decided:** P3 declined. P4: welded blind M3 studs on the panel backs if the maker offers them
    (pressed-in PEM studs need a 1.6 mm sheet; the panels are 1.5), else the main-board standoffs are spacers. The
    jack-board standoffs (CHASSIS bond, G2) then get countersunk M3 screws (Ø3.4, 90° to Ø6.5) with star washers.
    Positions are in `panels/` (DXF layers STUDS / CSK_NO_STUDS, hole tables), clear of cut-outs and print.
  - **Placement:** placed by `placer.py` `moves_only` (never packed), so no other part moved.
- Strip v5.0 (signed off by Ruslan 2026-10-27, `docs/proposals/cs1_proposal.md` CS1, from `docs/studies/console_survey.md`): the overload LED reads
  RECV, GOUT, EQOUT, PRESRC and FPOST, each through 1K into a BAV99 (D1, D12-D15). Positive peaks charge PK (U4A, as
  before); negative peaks pull OL_NN (C103 // R134 470K, PK's mirror), read by U18A (new LM393B, U18B spare) through
  R132 4M99 / R133 10M from +VL, wired-OR onto OL_HOLD through R135 1K. Thresholds are ratios of +VL only (+18.4 dBu;
  pulses +9.01 / -9.30 V). Placement by `moves_only`: only D1 moved (DO-35 -> SOT-23 on the bottom). PK / OL_NN are
  Switching class (`netrules.py` DETECTOR), ~390 mm. 902 pins, 310 parts; +~0.5 mA per strip on +VL.
- DRV135 coupler pairs (signed off by Ruslan 2026-10-27, `docs/proposals/cs11b_proposal.md` CS11b): each console DRV135's two 10 uF
  couplers (groups and master; not the jig stub or the LME49600 bypasses) are a pair sorted within 2 % at 100 Hz; BOM MPN
  note, 10 sorting spares in `order_bom.py`, the sorting rule in `docs/build/offboard_bom.md`. Output balance worst 5 % at 1 kHz /
  100 Hz -32 / -20 -> -60 / -47 dB.
- DRV135 loop resistors (signed off by Ruslan 2026-10-27, `docs/proposals/cs4c_proposal.md` CS4c): 22R ERJ-P06J220V between each
  DRV135 output pin and its 10 uF, inside the Sense loop (group R119-R122, master R222-R235; jig stub without, `rx=False`),
  made last by `master_lib.drv_loop_rs()`. 8 kV into the output pin 5.9 -> 0.84 A; differential output impedance
  52.6 -> 73.8 ohm, -0.16 dB into 600R. Group 789 pins / 283 parts, master 1786 / 617.
- Group / master jack-link clamps (signed off by Ruslan 2026-10-27, `docs/proposals/cs4b_proposal.md` CS4b): a BAV199 on every
  jack-link signal at the header, as the strip's (group D7-D20 at CN3 / CN4, 14 per board; master D79-D102 at CN5, 24),
  made last by `master_lib.link_clamps()` so no ref moved. Phantom on a DRV135 output now leaves its 10 uF 25 V coupler
  and Sense pin at 17.7 V (47.7 before); the no-phantom note stays. Group 781 pins / 279 parts, master 1758 / 603.
- Strip v5.6 / master v0.13 / group (signed off by Ruslan 2026-10-28, `docs/proposals/clicks_proposal.md` RV3 / RV4 / RV7 / RV8 / RV9 from
  `docs/reviews/project_review.md`): strip R142 1M from GOUT to U1B's − input (the gain pot's wiper was its only DC feedback) and
  C107 33 µF NP in the direct out's cold leg (R73, the same ERJ-P06J750V as R71; both legs 75R + 33 µF, CMRR limit at
  50 Hz ~46 → ~60 dB); master C194 / C195 2.2 µF films ahead of the aux 5 / 6 AFL 22Ks and group C98 the same (the
  level buffers' 6-25 mV DC no longer ticks onto PFL), master C196 / C197 33 µF NP in the phones gain-set legs (DC gain
  1: 19 / 79 mV → 6 / 25 mV on the cans under the relay; 2.2 Hz, a D10 100 µF found no spot), the −V-loss comparator U10B's + input on +1.0 V (R238 51K /
  R239 10K from VREF6) with R53 51K → 64K9 (trip −14.3 V, was −14.4; with −V lost the inputs stay inside the LM393B's
  range: SENSE_N +0.34 V normal, +4.7 V fault). Made last (the proposal's DEFER would have shifted 17 / 18 refs: the
  parts are created at the end of gen_master.py / gen_group.py instead), placed by moves_only at probed spots,
  nothing else moved. Strip 941 pins / 327 parts, master 1818 / 631, group 807 / 292.
- Strip v5.5 (signed off by Ruslan 2026-10-28, `docs/proposals/eqmid_proposal.md` EQM1): the mid ranges are the Delta's measured ones
  (Audio Precision plots, 200 Delta Tech Manual p.17): HI-MID R86 / R87 392R and R56 / R57 4K99 (598 Hz-9.93 kHz), LO-MID
  R60 / R61 4K22 (165 Hz-2.54 kHz); the mid-band tuning entry's 430R / 13K / 4K7 is now per band. Boost / Q / noise /
  stability unchanged; FREQ numerals and four sim_netlist peak checks follow.
- Strip v5.4 (signed off by Ruslan 2026-10-27, `docs/proposals/cs2_proposal.md` CS2 Option A): the Delta's -4.4 dB pan law. U8B / U3A at
  1.22x (R137 / R140 2K2, R138 / R141 10K, C105 / C106 22p C0G across the 2K2s for stability) with R136 / R139 3K3 from
  each output back to its wiper: -2.7 dB centre, +1.7 dB hard. Mix +3.3 dB at centre (S/N unchanged, summer headroom
  29.5 -> 26.2 dB per source); PAN off stays POST (1.7 dB under a hard pan). The old -6 dB was never a decision.
  937 pins, 325 parts.
- C/Room DIM (signed off by Ruslan 2026-10-28, `docs/proposals/cs7_proposal.md` CS7; reverses console_architecture's "monitor dim"
  exclusion): SW4 (PVA2, latching, grey cap) beside POWER at (29.16, 178); R236 / R237 91K between CRSB and each C/ROOM pot
  top (CRP_L / R), shorted by the released key: -20.0..-20.75 dB on C/Room only. Main R's DRV135 U8 and C47 / C48 / C50 on
  the bottom beside the key, C49 / R224 / R225 on top above it. Master 1796 pins / 620 parts.
- Group sub pan law (signed off by Ruslan 2026-10-28, `docs/proposals/cs2b_proposal.md` CS2b): the strip's (CS2) on every group, so the
  sub pan copies the strip again (master spec §12). U3B / U5A at 1.22x (R124 / R127 2K2 with C96 / C97 22p C0G across
  them, R125 / R128 10K), R123 / R126 3K3 from each output back to its wiper: -2.7 dB centre, +1.7 dB hard (ED2778A, the
  Delta's group module, pans passively at -4.6 dB). Sub to MIX +3.3 dB at centre. Made last, placed by moves_only under
  U3 / U5 (<= 5.9 mm from the - inputs); nothing else moved. Group 805 pins / 291 parts.
- Strip v5.3 / group (signed off by Ruslan 2026-10-27, `docs/proposals/cs6_proposal.md` CS6): R1-R4 (10R to +VA / -VA / +VL / -VL) on
  every strip and group are Vishay M25SI fusibles (M251206BB1009JP500, 1206, 0.25 W): a short behind one opens it in
  < 0.07 s and only that module goes quiet (the wing PTC never reached its trip current). **Power the console down
  before plugging or unplugging a module** (a live plug can open them; `docs/build/offboard_bom.md`). Strip R1-R4 placed by
  moves_only (C2 / C4 fixed, old spots kept out); the group's packed as before.
- Strip v5.2 (signed off by Ruslan 2026-10-27, `docs/proposals/cs4_proposal.md` CS4): a BAV199 at CN3 on each jack-link signal (D18
  IN_T, D19 IN_R, D20 RET_RAW, D21 SEND, D22 DO_T; pin 3 the signal, pin 2 +VA, pin 1 -VA), ahead of every series
  part: ESD into the op-amps 50-100x lower, phantom on SEND / DO_T clamped (C51 / C52 17.7 V, not 41.9; the no-phantom
  rule stays). TVS at the jacks rejected for its distortion. 921 pins, 317 parts; a "JACK LINK CLAMPS" block, 18 pages.
- Strip v5.1 / group (signed off by Ruslan 2026-10-27, `docs/proposals/cs10_proposal.md` CS10, from `docs/studies/console_survey.md` §7): a reverse
  Schottky across each audio rail of every ribbon board, Nexperia PMEG4010CEH (40 V 1 A, SOD-123F; onsemi MBR140SFT1G since SS2, below): strip D16 (K +VA,
  A GNDA) / D17 (K GNDA, A -VA) beside C1 / C3; group D5 / D6 beside its C1 / C2, created last so no group ref moved.
  A lost supply rail (wing PTC, open ribbon conductor) no longer reverses the polar 220 uF reservoirs (simulated
  2.5-12.7 V without, 0.36 V with). Logic rails (+-VL) need none. 906 strip pins, 312 parts; group 739 pins, 265 parts.
- Board layers (Ruslan, 2026-10-27, `docs/studies/layer_study.md`): the strip, group and master main boards are 4-layer (In1.Cu "GND" a
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

## Added 2026-10-28 (after the move; the one-liners were in CLAUDE.md, since 2026-11-11 in `docs/decisions_summary.md`)
- Insert jacks tip = send, ring = return, console-wide (D1, `docs/reviews/delta_crosscheck.md`, decided by Ruslan 2026-10-28; strip
  spec §7 / 16.4, master spec §4, `docs/studies/delta_clone_comparison.md` §2). The Delta is wired the other way round everywhere
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
  the fallback for RV5's DC on the fader top. `docs/studies/delta_clone_comparison.md` §2 and `console_survey/delta.md` T7 had
  called it "the same circuit"; corrected.
- XLR shells on CHASSIS (2026-10-28, `docs/reviews/project_review.md` §2 minor items): the NC3MAV / NC3MAH footprints' shell pad G
  had no symbol pin, so the master jack board's J3-J5 and the jig stub's XLR shells were unconnected although master
  spec §7 said "shell to chassis"; with anodised panels they would have floated. Project symbol `XLR3_Shell` (KiCad's
  XLR3 plus pin G) with G on CHASSIS in `master_lib` / gen_master.py / gen_jig.py; nothing moved on either board.
- Resistor film TF1 (signed off by Ruslan 2026-10-29, `docs/proposals/thin_film_proposal.md`): every plain 0805 resistor up to 1M is
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
- Strip v5.7 / master v0.14 (signed off by Ruslan 2026-10-29, `docs/proposals/clicks_followup_proposal.md` RV3b / RV9b, from the
  independent review of the clicks batch): strip R143 47K from DO_R to AGND and D23 BAV199 on DO_R at CN3, so the
  direct out's ring has the DC bleed and the clamp the tip has (RV3's C107 had left it with neither: phantom would have
  charged the 25 V cap to ~48 V; with the clamp 17.7 V as C52); master R240 4K7 from the relay driver Q1's base to
  GNDD: with −V lost, −VL sits at ~+0.5 V and the comparators' low output is referenced to it, so the base saw
  0.65-1.0 V and a closed relay could stay held at 11-21 % of its coil current at the LM393B's V_OL corner; divided 2:1
  the coil current is 0.2 µA, the 2.80 s close unchanged (`sim/review/clicks/mute_rbe.cir`, `sim/mute.cir` v5). Both
  made last and placed by moves_only (D23 beside D22, R143 beside C107, R240 under Q1), nothing else moved. Strip 946
  pins / 329 parts, master 1820 / 632. Bench item: open the −V wire with the relays closed.

## Added 2026-11-04
- Second sources for what held up stage A (signed off by Ruslan 2026-11-03, `docs/proposals/second_source_proposal.md` SS1-SS3; read at Mouser
  2026-11-03). Nexperia's small-signal diodes went to zero stock with 53-week lead times, BAV99,215 among them since 28 Oct.
  - **SS1, same part in other packing, order lists only (`ORDER_AS` in `order_bom.py`; the schematics keep the first code, so a line
    goes when stock returns):** OPA1612AID tube for the AIDR reel (not OPA1612AIDRGR, which is SON-8), BAV199,235 for ,215,
    DG413DY-T1-E3 for -E3.
  - **SS2, other maker on the same footprint:** Diodes BZX84C5V1-7-F, Diodes BAV99-7-F, onsemi MBR140SFT1G for PMEG4010CEH (strip D16 /
    D17, group D5 / D6; the feet land on the D_SOD-123F pads; `rail_loss.py mbr` holds a dead rail to ±0.36 V, 0 mA, at its maximum
    Vf; more reverse leakage, about 10 mA across the console's 56 diodes in the tub by estimate), Rubycon 63ZLH47MEFC6.3X11, Panasonic
    EEU-FR1E221 (25 V against 17 V rails; the 35 V Rubycon 35ZLQ passed over because its pitch couldn't be confirmed).
  - **SS3, the keys:** PVA2 EE H1 is due 2027-03-01 and nobody else makes this footprint. H3 is in stock at the same price, with the
    same pads and latching read from low-resolution drawings (check on a sample) and PV caps fit only H1 and H3. Phase 1's bench strips
    take H3 (`BENCH_KEY`), the console stays H1, and check 3's samples stay H1 because H3 can't settle the cap clearance or panel stack.
  - **R64 on the bench strips (2026-11-04, TF1's stated fallback, no sign-off needed):** Yageo RT0805FRE071K5L is at zero stock, 9,942 due 2027-01-26, so phase 1 orders
    RC0805FR-071K5L. R64 is in the LF bell's signal path, so a measured distortion figure there is on thick film; the N1 A/B compares the same strip with itself and isn't affected.

## Added 2026-11-09

- **Published.** `cozycactus/goa-console` is public, from a filtered copy of the history: `ref/` and `docs/img/delta_d201_top.png` (Soundcraft, Mackie and API copyright) are out of all 227 commits and the commit email is GitHub's noreply address. The old private repo is `goa-console-archive`, kept as the backup with those documents. Rejected: rewriting the private repo and flipping it public, because GitHub can keep serving force-pushed-over commits by hash; a new repo never held them.
- **Licence.** CERN-OHL-S-2.0 over the whole repo. Rejected: MIT on `tools/`, because the generators there hold the design itself (the netlists in the `P(...)` calls, the drawings, the placement), so MIT would have let anyone take the design without the reciprocal terms.
- **Repository layout (RV12's second step).** 57 proposals, reviews, studies and build notes moved to `docs/{proposals,reviews,studies,build}/`, BOM exports and order lists to `bom/`, schematic PDFs to `pdf/`. Staying at the root: the five live specs and `routing_guide.md`, because the generated schematics and DRC rules name them; and each board's `.kicad_sch` / `.kicad_pcb` / `.kicad_pro` / `.kicad_dru` / `.net` / `_intended.json`, because KiCad resolves the library tables and sheets per project and every tool assumes the flat root, so a per-board tree would rewrite the whole toolchain just before routing. Code strings that end up in generated files (`layer_study.md`, `frame_proposal.md`, `thermal_study.md`, `tub_proposal.md`, `offboard_bom.md`, `met1_ret1_review.md`) keep the bare name, so no design file was regenerated.
- **One folder per board (2026-11-09, reverses the previous bullet's "stay at the root" for the KiCad files).** Ruslan asked for a shorter root after the docs moved, and the best moment is before routing starts: all nine projects now live in `boards/<name>/` (schematic, board, `.kicad_pro`, `.kicad_dru`, `.net`, `_intended.json`, `_parts.json`, the hierarchical `*_sheets/`), the root keeps 13 files. Why it works: each folder carries its own `fp-lib-table` / `sym-lib-table` pointing at the shared libraries in the root (`${KIPRJMOD}/../../goa-console.*`), the 3D model paths use the same prefix (`tools/footprints.py`, `tools/placer.py`), and the generators write the jack boards as sibling folders (`schgen.sibling_sch`). The five live specs and `routing_guide.md` stay at the root. Checked by exporting every netlist again: all nine are identical to the pre-move netlists except the library path line in four of them. Cost: ~45 scripts changed their paths; commands now name `boards/<name>/<file>`.

## Added 2026-11-11

- **Jig bus headers turned (Ruslan, 2026-11-11; `tools/place_jig.py`, test jig spec v0.11).** Drawing the jig on a bench (`tools/jig_3d.py`) showed that the master stub and the load board had their 34-way header with pin 1 at the far end, while the strip, the group and the master all have it at the fader end (bottom side, y 345.64). A flat ribbon keeps conductor 1 on one edge, so a jig board had to lie turned by 180° or the ribbon had to take a half twist; the console itself has no such twist. Changed, since neither jig board is routed: the stub's CN2 turned by 180° on its own pads (one part changed), the load board's CN1 moved to the right edge with pin 1 at the front (10 parts changed: the header, the spade CN2, R1, J1, the three 1 nF jumpers and their caps). The spade, the 10 Ω ground-cancel tap and the dummy-load terminal went with the header, as on a strip, so GCANCEL is 26 mm (a header on the far edge alone left it at 118 mm) and the dummy load's 1 A returns at the header instead of across the board's ground. Rejected: leaving the boards and twisting the ribbon (works, but the ribbon is the thing under test); turning the load board by 180° on the bench (its legends then read upside down). Order on the ribbon: load board, strips, stub.
- **Strip jack-board link: CN5 turned (Ruslan, 2026-11-11; `tools/place_strip.py`, strip spec 16.4).** The 3D model drew the 10-way link with quarter twists, which hid a pin-order fault: a 45° fold turns a flat cable over, and with CN5's pin 1 at the front end and CN3's at the right end the spec's "one 90° fold" lands the stripe on CN3's left end. As first placed the cable needed a fold away from CN3 plus a double-back, three layers under the jack board. CN5 is turned by 180° instead, so one fold fits. Turned on its own pads, the footprint's pin-1 arrow ran over the board edge (two new silkscreen warnings; the old comment in `place_strip.py` gave that as the reason for the first orientation), so the header also moved 0.5 mm in: pins at x 30.5 / 33.04, the arrow 0.27 mm inside the edge, 0.28 mm between its courtyard and the standoff holes'. Rejected: turning CN3 on the main board instead (the BAV199 clamps and the shortened input nets sit round its pins; the jack board has eight parts); leaving the cable to leave CN5 outwards (the fold would lie under the neighbouring module). `console_3d.py`'s `link_ribbon` now takes the fold count from pin 1 of the two headers, so the drawing can no longer hide this.
- **Strip jack-board link: CN5 across, no fold (Ruslan, 2026-11-11, replaces the bullet above the same day).** Ruslan asked why the header isn't simply turned so the cable runs straight, and corrected my objection: the panel drawings have not gone to any maker, so moving a standoff costs only a regenerated drawing. Two placements were tried in a copy outside the repository, each with DRC and the panel checks: A, the header at the bottom edge with only H2 moved (3.6 mm off CN3's line, J1's sleeve path unchanged at 24.4 mm), and B, the header in the middle band with both standoffs in the bottom band (1.7 mm off, the sleeve path 29.6 mm). B chosen: the point is a cable that lies without side strain, and 5 mm more of wide CHASSIS copper is small beside the 24 mm standoff it leads to. It does change E5's figure, so it is recorded here and in the routing guide. Neither variant reaches CN3's line exactly: J5's peg and tip pin are in the way; only moving CN3 on the main board would, and that was not tried. Why a straight cable at all: the fold worked on paper, but it is made by hand on 24 cables and can be folded the wrong way, while a straight cable between two headers with pin 1 on the same end can only be made one way. Applied: `place_strip.py` (CN5 `29.5 25.4 90`, H1 `21 36`, H2 `32 36`), `panels/strip.dxf` and `strip_holes.csv` regenerated (the two stud positions), `console_3d.py`'s `link_ribbon` draws the straight run and asserts pin 1 on the same end.
- **One record per change; the decision one-liners out of `CLAUDE.md` (Ruslan, 2026-11-11, to spend fewer tokens).** `CLAUDE.md` is loaded into every session; 11.5 KB of its 25 KB was the one-line decision list, now `docs/decisions_summary.md` (text unchanged), read before any design change. And a change is now recorded once, here, with its reason, the rejected options and the check results; the specs, the summary and the state table get only the fact that changed. Before, one change was written up in five to seven places (today's three took about a third of the session's output). `docs/verification_log.md` stays for check runs that belong to no decision. Also in `CLAUDE.md`'s rules: one topic per session, numbers before pictures, long tool output into a log.
- **Group jack-board links: CN1 turned, two folds and a strain-relief wrap per cable (Ruslan, 2026-11-11; `tools/place_group.py`, placement only, unrouted).** The group's two links were checked as the strip's was, from pin 1 of the four headers read with pcbnew. All four lie along the boards, bottom side, so a cable leaves sideways and needs two folds; a fold swaps travel and stripe directions, (t, w) -> (w, t) or (-w, -t), which fixes the side a cable must enter the main header from. Main board: CN3 (2 × 8) pins x 4.72 / 7.26, y 190.65-208.43, CN4 (2 × 5) x 28.23 / 30.77, y 190.65-200.81, pin 1 of both at the jack end. Jack board as first placed: CN1 (2 × 8) pins x 31.0 / 33.54, y 24.52-42.3, CN2 (2 × 5) x 19.9 / 22.44, y 28.84-39.0, pin 1 of both at the fader end.
  - **10-way, CN2 -> CN4: right as placed.** Out of CN2 to the left, down the board with the stripe on the left edge, into CN4 from the left; 185 mm between the socket centres. The run slants 3.5 mm (1.25°, the creases a little off 45°) so its second fold clears CN3's socket.
  - **16-way, CN1 -> CN3: wrong as placed.** Its two two-fold routes put the run 17.3 mm (at CN3) or 17.6 mm (at CN1) outside the board, under the next module; inside the module it took a fold away and a double-back. **CN1 is turned by 180°**, pin 1 at the jack end like CN3's, and sits 0.5 mm in (`'CN1': (33.04, 24.52, 0, 'B')`, pins x 30.5 / 33.04; on its own pads the pin-1 arrow ran over the board edge, three silk warnings, as on the strip). Now: out of CN1 to the left, down the board with the stripe on the right edge, into CN3 from the right; 192 mm between the socket centres. So the two jack-board headers have pin 1 at opposite ends, because CN3 can only be entered from the right and CN4 only from the left.
  - **The dress (computed, not yet tried on a cable).** Neither cable can lie in the sockets' ribbon plane (9.4-10.3 mm under a board; socket cover bottom 12.9): on the jack board CN2's socket is 4.6 mm from CN1's, in the 16-way's way out; on the main board the two sockets are 17.5 mm apart, CN4's overlaps the 16-way's fold by 2.82 mm, and C81 (33 µF, 11.5 mm tall) and C82 (2.2 µF film, 13 mm) stand in the gap, 3.9 mm from CN3's socket and 5.0 mm from CN4's. So the cables take the Würth sockets' strain-relief wrap and lie one cover lower: the 16-way leaves CN1 on the right and CN3 on the left and is doubled back under each cover, the 10-way the same at CN4 (leaves on the right); the 16-way lies under the 10-way all the way. 3.0-5.5 mm of board beside each socket for the wrap. C82 at 13.0 mm touches a cable at 12.9. Cut lengths about 230 mm (16-way) and 210 mm (10-way); cut the first one long.
  - **Rejected.** Turning CN3 on the main board instead (the same pin order, but the CS4b clamps sit round its pins; the jack board has 11 parts). A header across the jack board for one fold or none, as the strip's CN5: probed every 0.25 mm with the placer's rules, a 2 × 8 fits nowhere even without the standoffs, a 2 × 5 only at centre x 24.6-26.7 where one fold into CN4 needs x <= 20.15. Swapping CN1 and CN2 (the 16-way's run 2.15 mm outside the board). Turning CN2 as well (its cable would leave through CN1's socket and slant 10.4 mm). Moving CN3 / CN4 apart or across on the main board with C81 / C82 kept out of the gap, which would let the cables land without wraps: it re-places 292 parts and the measured trace table behind the group's stability runs, for four modules; not trialled.
  - **Checks.** Placer run on the jack board alone (the main board's file byte for byte the old one); placement diff against HEAD one part, CN1 `31 42.3` -> `33.04 24.52 180`. Read back: pin 1 SUB_SEND (33.04, 24.52), pin 16 GNDA (30.5, 42.3), courtyard 0.61 mm from CN2's. DRC 28 violations, the same 28 as before (the NJ6FD-V's own), 0 parity. Manhattan MST of the jack board's nets 912 -> 811 mm (SUB_SEND 43 -> 23, SUB_RETRAW 31 -> 16, Return_RR 35 -> 15, Return_RT 28 -> 12, S_ON 45 -> 34; A_ON 19 -> 20). `netrules.py group_jack_board`, `check_all.py --full` 72 / 72 (296 s), the three `order_bom.py` runs leave `bom/` unchanged, `render/group.json` re-exported (CN1 only). The master's 40-way link read at the same time: its CN1 and CN5 both lie across, pin 1 at x 15.0 on both, so no fold and no fault. The model draws this dress since the same day: `cable.folded_link` (new) works the route out from pin 1 of the two headers by mirroring the stripe in each crease, and `console_3d.py`'s `link_ribbon` uses it for two headers along the boards (`GROUP_DRESS`: which cable is wrapped where), so the build stops on a header with pin 1 at the wrong end; the quarter twists are gone. Checked without Blender from `render/group.json`: both cables inside the board (x 0.78-36.99), the stripe on the pin-1 side at all four sockets, the 10-way 2.0-3.5 mm above the 16-way along the run and 0.20 mm clear of it at the main board's fold, the placement before the turn refused, an unwrapped 16-way refused. Centre-line lengths in the model 217 mm (16-way) and 198 mm (10-way). The group module alone built in Blender 5.2.2 and one small view rendered (`render/group_links.png`); the console's blend and renders not rebuilt.
- **Group jack-board links: all four headers across, no fold (Ruslan, 2026-11-11, replaces the bullet above the same day; `tools/place_group.py`, `tools/placer.py`, placement only, unrouted).** Ruslan pointed out that two folds and a wrap per cable is not a straight connection, and that straight ribbons are always better: a straight cable between two headers with pin 1 on the same end can only be made one way, and eight of these are made by hand. A first trial in a copy showed that the jack board is easy and the main board is not; this is the main board worked out, in a copy outside the repository, and applied after sign-off.
  - **Jack board (three parts).** J3 (AUX OUT, alone in its row) 3 mm up, row y 31: a header across needs a pad-free band of 10.2 mm and the 22 mm rows leave 7.63. CN1 (16-way) centre (16.0, 43.4), CN2 (10-way) centre (26.6, 25.0) in the slot beside J3, both `90, 'B'`, pin 1 on the right end as the strip's CN5. The panel's AUX OUT hole moves 3 mm (`panels/group.*` regenerated, `panel_fab.py` 0 problems).
  - **Main board (46 of 298 footprints).** CN3 across at centre (16.0, 183.5), CN4 at (26.6, 204.25), pin 1 right, on CN1's / CN2's lines, so every pin pair has the same x (0.00 mm offset, pin n to pin n on all 26, read from the placed boards). The packing is kept as it was: the two headers are still packed along the board and `LINKS` (placer `moves`) then lays them across and re-seats only what they, their pin-1 arrows and the cables' keepouts displace. Moved: U12 3.0 mm down and U4 6.75 mm up (both stood on the new header pads), eight tall capacitors, the 14 CS4b clamps to the new pins, and 20 small parts of U12 / U13 / U15 / U4 / U9 (R119 / R120, C76, R55 / R57 and R21 among them). The small parts went to the free spot nearest to their own pins, found by a probe with the placer's rules; the tall capacitors to the few spots free on both sides, chosen by hand: C80 / C82 / C81 in the column CN3 left, C62 beside U9, C56 on C55's spot, C55 where C61 stood, C61 and C22 by the pan row. CN4 is at y 204.25 and not 205 because 0.75 mm more lets a 33 µF can stand between it and C88 / C21 (the run between the two sockets is then 14.75 mm).
  - **The cables.** The 16-way is the short upper one (140.1 mm between the socket centres, cut about 160 mm); the 10-way (179.25 mm, cut about 200 mm) passes under CN1's and CN3's socket covers and rises 3.7 mm in 14.75 mm into CN4. The jack board's ribbon plane is 12.5 mm lower than the main board's, so each cable comes up into its socket over its last centimetres. `placer.py` got a keepout with a height for that room (`keepout` with a sixth field, `heights` = seated maximum per footprint: 100 µF 10 × 16 can 17.5 mm, 33 µF 13.0, 10 µF 12.5, 2.2 µF film 13.0, the 100 µF and the film from distributor listings): under the 16-way no 100 µF can for 30 mm before CN3's socket and nothing over 9 mm for 17.5 mm; under the 10-way where it runs alone no 100 µF can for 30 mm and nothing over 9 mm for 7 mm (it lies 3.7 mm lower there); nothing over 9 mm between the two sockets. The packer keeps the parts it places out of such an area, a move or turn into one is refused, the finished board is checked once more, and a missing height table, an unknown side or a tall footprint without a height stops the run. The distances are a model of the cable's shape and have not been tried on a cable: both cables must be cut with about 10 mm of slack (a taut 16-way would bear on C14 / C20, unchanged, 38-49 mm before CN3), and both must be tried together on real boards before boards are ordered.
  - **What it costs.** The board has almost no spot left where a through-hole part is free on both sides (a scan found them only between the pan row and the routing rows), so three coupling capacitors stand far from where they were: C55 59.6 mm (RT_R 24 → 98 mm, RT_PRER 94 → 169), C61 54.7 mm (RT_BL 70 → 130, beside the routing resistors it feeds), C22 65.5 mm (S_ON 50 → 85; it is inside U4's sense loop, 46.9 mm from pin 2 against C21's 22.8, were 33.8 / 16.0). C56 is 16.3 mm from U9 pin 3 (was 3.8) and C62 2.9 mm from pin 5 (was 16.5): only one film fits beside U9. One new line in `emc_check.py`'s closest couplings: U9A+ 4.9 mm from D3's LED net at R68, on the other side of the board. The group's placed-trace table and TI-model stability runs were repeated the same day (below).
  - **Rejected.** Letting the packer re-place with the headers fixed across: 156 parts move (11 op-amps) and C0G caps stand up to 56.6 mm from their pins before any fix-up; with every op-amp held as well, 193 parts and 15.5 mm. The headers further down the board (CN3 at y 188-192, CN4 beyond the standoff H3 at 223.5 or more): seven tall capacitors displaced, two 100 µF and the high-impedance film C88 among them, less room for them and cables 16-19 mm longer. CN4 at y 205: C55 misses its spot by 0.5 mm and goes to y 281. A blanket 30 mm keepout for everything tall: it closes y 150-210 at nearly the full width. The jack board's mirrored variant (10-way as the near cable): its keepout between the sockets covers the column CN3 left, the only free through-hole room. C22 near U4 in C55's place: C55 then stands about 125 mm from its spot (still the swap to make if the DRV135 loop's symmetry turns out to matter). Turning the moved resistors by 180° (`ratsnest.py`): every one makes the crossings worse.
  - **Checks.** Placement diff against HEAD: main board 46, jack board 3 (J3, CN1, CN2). DRC main board 0 violations, jack board 28, the same 28 as before (the NJ6FD-V's own); 0 parity issues on both; every footprint linked (292 / 292, 11 / 11). Placer report, before → after: decouplers median 2.9 → 2.7 mm, max 5.1 → 4.4, over 5 mm 1 → 0; high-impedance inputs median 7.5 → 7.0, max 20.2 → 20.2, over 6 mm 26 → 22. C0G caps on op-amp inputs worst 6.1 → 6.1 mm (C76 0.0 → 3.3: CN3's body lies under U15's pin 3). Clamps, pad to header pin, 8.2-20.2 → 2.1-9.5 mm; R119 / R120 to U4's output pins 1.7 / 8.3 → 0.2 / 0.9. Manhattan MST of the 159 signal nets 9952 → 9995 mm, the 14 link nets 1719 → 1556, U12's nets 88 → 101, U4's 270 → 290; ratsnest crossings 1752 → 1822; jack board 509 → 615 mm (610 before the CN1 turn). `netrules.py group` / `group_jack_board`, `check_all.py --full` 72 / 72 (267 s), the three `order_bom.py` runs leave `bom/` unchanged, `render/group.json` and `docs/escape/group_*` regenerated (`escape_plan.py` wrote them under `boards/group/docs/escape/`, its path predates the boards' folders; moved by hand). `console_3d.py` takes the strip's straight branch for both links (pin 1 asserted, the 10-way 4 mm lower; the dip under each socket is not drawn); the blend and the renders not rebuilt. Reviewed by Codex Sol, DeepSeek and Grok before the apply (Gemini's quota was exhausted): the pin mapping confirmed on every pad; taken from them, the keepout's refusals and the 30 mm for the 100 µF cans under the 10-way; left open, the cable trial (the stability runs followed, next sub-bullet).
  - **Stability on the moved board (2026-11-11, ngspice 46, TI's OPA161x + OPA1656, `.options itl1=500`, 0.08 pF/mm).** `sim/review/group/mst_all.json` re-measured from the placed board (48 of its 179 nets changed; the method checked first: from the old board it gives the old table byte for byte), then the five sweeps as on 2026-11-04: 222 states, 1835 unit results, none without data, 2434 s. `ins` and `bus` unchanged (worst 65.3° U2A, 56.8° U1B with the ferrite shorted). `pots` worst 59.7 → 60.1° and `ret` 59.1 → 59.5° (U14B both); the followers 59.5-60.3° (were 59.1-60.9). The units whose output nets grew lose margin: U8B (RT_R 24 → 98 mm, C55) 66.1 → 61.9°, U9A (RT_BL 70 → 130 mm, C61) 68.6 → 65.9°, U12B (RT2_R, C81) 64.9 → 63.4°; U3B gains, 73.6 → 76.0° (S_PANL shorter). With +22 / +47 pF on every long output net (`loads`) the worst is now U8B at 45.8° where it was U6B at 46.1°, U9A 48.8 → 47.2°, U12B 47.9 → 46.9°, peaking at most 2.76 → 2.99 dB (U9A). Not covered: the DRV135s are not in this deck, so C22's place in U4's sense loop is not simulated.
