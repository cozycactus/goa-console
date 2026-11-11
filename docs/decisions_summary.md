# goa-console — decisions, one line each

Moved out of `CLAUDE.md` on 2026-11-11, text unchanged, so that file stays short (it is loaded into every session).
The full text of each decision, with the reasons and the rejected alternatives, is `docs/decisions.md`.
**Read this file before proposing or making any change to a circuit, a part, a placement, the mechanics or a rule.
Do not silently change a decision.**

**Architecture and bus**
- Delta Theatre input without the mic stage (2026-10-22, `docs/studies/delta_clone_comparison.md` §3): receiver + separate inverting gain stage −15…+15 dB, Ø, HPF, Delta EQ, EQ IN, post-EQ insert (jumper pre-EQ), ON, PAN switch, routing LEDs, PRE per aux pair, DIR; internal level 0 dBu; 4K7 summing.
- Master section = modules M1 (2026-10-22): 4 × 8 HP group modules (sub n, aux n master, returns n) + 16 HP master; `docs/studies/master_panel_study.md`.
- One 34-pin header per strip on a daisy-chained ribbon with crimped IDC sockets (2026-10-19); CN2 dropped.
- Bus pinout = the Delta motherloom ED3344C (SUB1-4 on 15/13/11/9, MIX R 17, MIX L 18 — ED3344C order kept over the manual's, 2026-10-23 —, AUX6..1 on 20-25, GCANCEL 26, PFL 27, PFL DET 29, −V 30-31, +V 32-34 since W1, even 2-16 GND). Pins 1/3/5/7 reserved for SUB 5-8 and 19 spare: unconnected on every module, grounded at the master through bridged jumpers JP3-JP7 (D13, 2026-10-28; open them for 8 groups). Pin 28 open everywhere (D22 / D24).
- Ground cancel: 10R from module AGND to pin 26, master summers reference it, each followed by a unity differential re-inverter; no master-end tie, a 100K keeper only (2026-10-19 / 23). SSL-style impedance-balanced bus dropped.
- Summing resistors 4K7 MIX / SUB (master feedback 4K7), 22K AUX / PFL; master sums invert and re-invert once; channel path non-inverting (tip = hot).
- Routing (2026-10-22): PVA2 keys carry logic only, DG413 U9-U11 at the bus header move each 4K7's bus end between bus and AGND; off = clean ground; yellow LED per key; +5VL from +VA via 4K7 + BZX84C5V1 (+ BAT54W D10).
- 4 subs with inserts, 6 aux (AFL), 8 stereo returns (two per group, RET1 2026-10-26), PFL only (no SIP), relay mute on the mains; C/Room DIM −20 dB (CS7, 2026-10-28, reverses the architecture's exclusion).
- Insert jacks tip = send, ring = return console-wide (D1, 2026-10-28; the Delta is ring = send).
- SSL bus compressor (Gyraf clone) external on the master insert; VCAs SSI2162 (THAT 2180 EOL), also the strip's plug-in VCA option (2026-10-19).

**Strip circuit (spec `channel_strip_schematic_spec.md`, "Changes" blocks)**
- Mid bands: KHN state-variable band-pass tuned by Alpha A10K duals as dividers, not the Delta's 100K C-law Wien; since EQM1 (2026-10-28) HI-MID 392R / 13K / 4K99 (598 Hz-9.93 kHz), LO-MID 430R / 13K / 4K22 (165 Hz-2.54 kHz); OPA1612; A10K not A100K (noise).
- Sweepable HPF H1-H4 (2026-10-24): KHN high-pass 21-403 Hz, unity, Q 0.707, RV16 A10K dual into U15, U5A summer, SW11 HP / HIN, C91; wing −V PTC MF-RX185/72 (H4).
- Fader post-amp +10 dB (R38 2K2); AC coupling 100 µF NP + 47K on every bus-feeding node; J112 soft mute (two shunts, not the Delta's series + shunt, D3); logic rails ±VL / GNDD joined to GNDA at NT1.
- Film couplers and bipolars F1-F4 (2026-10-24): 2.2 µF PET film (wipers, meter averaging; THT, bottom side; order code KEMET MMK5225K63J06L4BULK since FE1, 2026-10-29: the WIMA MKS2 is obsolete, the KEMET a last-time buy in the same box), MUSE ES 33 / 100 µF, 10 µF Panasonic ECE-A1EN100U (S1); no X7R in the signal path, no DC coupling, no polypropylene.
- Op-amps: OPA1612 in noise-critical stages and on the MIX / SUB / aux sums; OPA1656 on the PFL sum, the CRS followers and the input followers (G3, U16); N1 (OPA1656 in U1, U5-U7, U12-U15) open, decided by the jig A/B.
- Pan law CS2 Option A (2026-10-27): the Delta's −4.4 dB (U8B / U3A 1.22× with 3K3 back to the wipers, C105 / C106 22p); PAN off stays POST; the group's sub pan the same (CS2b, 2026-10-28). The old −6 dB was a transfer error.
- v4.1 T1-T11 stability caps and ratings (2026-10-23); v4.5 K1 / K3 (PFL DC block C96, ~150 ms OL hold); v4.7 MET1 red / green bicolour signal / OL LED D2 WP3VEGW; v4.8 PAN1 pan buffer L in U8B; v4.9 P1 / P2 / E6; v5.0 CS1 five-tap OL detector, both polarities, thresholds ratios of +VL (+18.4 dBu); v5.1 CS10 a reverse Schottky across each audio rail (strip D16 / D17, group D5 / D6; MBR140SFT1G since SS2, the PMEG4010CEH out of stock); v5.2 CS4 BAV199 on every jack-link signal at CN3 (TVS rejected); v5.3 CS6 fusible R1-R4 Vishay M25SI (strip and group); v5.4 CS2; v5.5 EQM1; v5.6 RV3 / RV4 (R142 1M gain-stage keeper, C107 33 µF in the direct out's cold leg); v5.7 RV3b (2026-10-29: R143 47K bleed and D23 BAV199 on the direct out's ring, as the tip's R72 / D22).
- Design review (2026-10-25): ON also mutes the pre-fade sends and the direct out, PFL stays at PRE (Q1); group sub pan RV2 = RK09L; jig R45 ERJ-P06J332V; silk "2" at every PVA2's pads 1 / 4.
- Ground and hum G1-G3, G2b / G3b (2026-10-25): one 14 AWG wire per module to the master's copper bar under the M4 star (G1); balanced-input and DRV135 TRS sleeves on CHASSIS through plated standoffs, inserts / phones on GNDA (G2); receivers buffered by OPA1656 followers, 1M / 220R / 100 pF / 100R (G3); XLR shells on CHASSIS (2026-10-28).

**Master and group (spec `master_section_spec.md`)**
- Balanced outputs TI DRV135UA (DRV134 family, SO-8; THAT1646 EOL 2026-09-01), 10 µF NP per leg inside the Sense loop, 22R in-loop (CS4c), coupler pairs sorted within 2 % (CS11b), mute relay after; no phantom on any balanced output.
- Master parts S1-S8 (2026-10-23): six G6K-2F-Y mute relays (COM = connector, NO = driver, NC = ground), LM393B, one DG413 PFL switcher, OPA1656 CRS followers, PFLDET clamp (2 × 1N4148, 330K reference, 1 µF debounce), LM2901B meters with BCP53-16 / 120R current sources and Kingbright GaP / GaAsP LEDs, sub AFL kept, GCANCEL buffer kept.
- MG1-MG20 (2026-10-24): EXT_BL / BR + 100R; build-outs at the op-amp pins (solo 100R, post-amps 47R, CRS 100R, insert return 75R, meter DET 470R); C0G at the + inputs; insert returns 1K + 100p; TL072HIDR meter detector reading the diode cathode; 50 V X7R / C0G, anti-surge where rated; one SUB and one AUX bus jumper per group board.
- Master v0.13 RV7-RV9 (2026-10-28): 2.2 µF films ahead of the AFL 22Ks (master C194 / C195, group C98), phones gain-set 33 µF NP C196 / C197 (DC gain 1), U10B's + input on +1.0 V (R238 / R239) with R53 64K9 (trip −14.3 V); v0.14 RV9b (2026-10-29): R240 4K7 base-emitter on the relay driver Q1, so a closed relay releases with −V lost at the LM393B's V_OL corner.
- Jack-link clamps CS4b (group 14, master 24 BAV199) and loop resistors CS4c (group R119-R122, master R222-R235), made last (2026-10-27).
- Pan pot RV8 and group RV2: ALPS RK09L1240015 (M9 bushing, 6 mm D shaft, Ø9.5 hole, centre detent), 2026-10-25.

**Power**
- PSU option B (2026-10-22, `psu_spec.md` v0.2): two LRS-150-24 at 21.6 V → 10 µH / 2200 µF → LM1084-ADJ 17.0 V floating rails, TL431 + PNP + 2N6505G crowbar at 19.1 V, 4 A per rail; ADJ divider R2 / R11 ERJ-P06F1501V 1206 0.5 W (RV1, 2026-10-28). Case PC1-PC3: Hammond 1402KV, Fischer SK 47 75 SA on the front panel, Schurter DD11, NC7FD-LX (2026-10-26).
- Budget: ~3.31 / 2.79 A typical, worst corner ~4.54 A on +V accepted (the chain 4.0 → 4.24 → 4.33 → 4.38 → 4.54 A, master spec §27); inlet NC7MD-LX, two 5 A contacts per rail; wing PTCs +V MF-RX250/72 (W2) on three conductors, −V MF-RX185/72 (jig stub still MF-RX160/72).

**Mechanics and panels**
- Strip panel 8 HP × 12U, two pot columns at x 8.84 / 29.16 (20.32 pitch, 2026-10-23), jacks on the panel (NJ6FD-V) on a 38 × 43 mm jack board 24.0 mm under it, 2×5 IDC link; knobs Ø14.5; custom frame with rails only at the panel ends (2026-10-22).
- Faders Bourns PTB0143 (strips, groups) / PTB0144 (master) A10K, BP blade; caps Sifam LK111 01 black with a line (KC2); the AP / ALPS / TT / P+G alternatives rejected (2026-10-23 / 25).
- Knobs KN1-KN3 (2026-10-25): Elma 021-3525 (1/4") / 021-3425 (6 mm) matt black with a line, Elma 040-30x5 caps colour-coded per function; key caps C&K PV (KC1).
- Panel parts: Alpha RD901F / RD902F pots (centre-detent 10K B have 1/4" shafts), C&K PVA2 EE H1 keys fitted with the moulded "2" in the pad 1 / 4 column (H3 on phase 1's bench strips, SS3), Keystone 1287-ST spade, 3 mm LEDs on 7.6 mm spacers.
- Frame rails FR1-FR3 (2026-10-25): two 6060-T6 / 6082 bars 50 × 10 × 1227.2 mm, 30 M3 tapped holes each, bonded by bare holes + star washers, one 2.5 mm² bond per rail to the M4 star (`frame/`).
- Tub TB1-TB4 (2026-10-26): walnut cheeks carrying the 9° tilt, 12 mm birch-ply floor with 30 inlet slots + mesh, walnut arm-rest, back plenum with the NC7MD-LX, open underside, console raised 25 mm (`tub/`); supply cable through back-rail vent slot 14.
- Thermal TH1-TH3 (2026-10-26): 98 W; vented tub ~16 K rise, back rail's 30 vent slots 30 × 25, no fan unless the built console exceeds 20 K; MUSE ES kept.
- P4 (2026-10-27): welded blind M3 studs on the panel backs if the maker offers them, else the main-board standoffs are spacers; countersunk M3 + star washers at the jack boards.
- Board layers (2026-10-27, `docs/studies/layer_study.md`): strip, group and master mains 4-layer (In1 solid GNDA plane, In2 GNDA fill with the rails / GNDD only in the left-edge RAILS corridor), every other board 2-layer; JLCPCB +$93 for the console.

**Placement (placement only; Ruslan routes)**
- E1-E5 / E8 (2026-10-26) and E6: LED switches beside D2, the J112 mute and U16's network under their op-amps, supply filters at the bus header, jack-board C8 / C9 between J1's pins, master flasher diode and PFL detect by their ICs; E9 / E9b stability caps ≤ 6.4 mm from their pins; E10 input nets shortened; E11 decouplers ≤ 5.5 mm (THT 10 µF excepted); untangle turns (crossings −4..−7 %); upper strip op-amps fixed in `place_strip.py`.
- Strip jack-board link (2026-11-11): CN5 across the jack board like CN3, pin 1 on the right like CN3's, so the 10-way ribbon runs straight (no fold; 1.7 mm right of CN3's line); standoffs H1 / H2 at (21, 36) / (32, 36), the panel's two stud positions with them; J1's sleeve to a standoff 29.6 mm (was 24.4, E5). As first placed the spec's one fold put the stripe on CN3's wrong end (spec 16.4).
- Group jack-board links (2026-11-11, replaces the two-fold dress of the same day): all four headers across, pin 1 on the right, so both ribbons run straight. Jack board: J3 3 mm up (row y 31), CN1 (16-way) centre (16.0, 43.4), CN2 (10-way) centre (26.6, 25.0); main board: CN3 centre (16.0, 183.5), CN4 centre (26.6, 204.25). The 10-way passes under the 16-way's two sockets. The main board's packing is kept: `LINKS` in `place_group.py` moves the headers and the 44 parts they displace (U12 3.0 mm, U4 6.75 mm; C55, C61, C22 55-66 mm away); do not remove the packed links zone or the old silk keepout (the board re-packs). `KEEP_TALL` (placer keepout with a height) keeps tall parts out from under the cables.
- Jig bus headers (2026-11-11): pin 1 at the front end as on every console module (stub CN2 turned on its pads, load board CN1 on the right edge with the spade, R1 and J1 beside it): one flat ribbon, load board | strips | stub, no twist.
- Routing rules by `tools/netrules.py` into every project (net classes, HighZ / Entry / Bus clearances, 4-layer rules, WingFeed, PSU HighCurrent); `routing_guide.md`; `route_check.py` after routing.
- Sourcing (2026-10-25): plain 0805 resistors Yageo RT0805FRE07xxxL thin film up to 1M (TF1, 2026-10-29; RC0805FR thick film above 1M and as the out-of-stock fallback; anti-surge ERJ-P06 positions stay); stock risks PTB0143, NJ6FD-V, OPA1612, the 2.2 µF film (FE1: buy the console's 120 in one order; FE2's wider footprint is the way out); C0G order codes by footprint; DRV135 coupler pairs sorted (10 spares); second sources SS1-SS3 (2026-11-03, `docs/proposals/second_source_proposal.md`): OPA1612AID, BAV199,235, DG413DY-T1-E3 on the order lists only, Diodes BZX84C5V1-7-F / BAV99-7-F, onsemi MBR140SFT1G, Rubycon 63ZLH47MEFC6.3X11, Panasonic EEU-FR1E221 in the schematics, PVA2 EE H3 and thick-film R64 (the 1K5 thin film is out of stock) on phase 1's bench strips.

**Repository**
- Public since 2026-11-09 as `cozycactus/goa-console`, CERN-OHL-S-2.0 over the whole repo (`tools/` too: the generators hold the design). History filtered of `ref/` and the Delta drawing; the old private repo is `goa-console-archive`. `ref/` stays on disk, git-ignored: never commit it. Commit with the GitHub noreply address.
