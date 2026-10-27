# Eight groups: a study (2026-10-27)

**A study, not a proposal.** No design file changes. It asks: what would 8 subgroups cost us, and what does the parent
family do? The request came from Ruslan via another session.

**Sources:**
- `ref/Sndcft_DeltaDLX_Schems.pdf`, every sheet rendered at 300 dpi.
- PDF page → drawing:

  | PDF page | Drawing |
  |---|---|
  | 1-2 | ED2911A / B, Venue input |
  | 3-4 | ED2915A / B, Venue stereo input |
  | 5 | ED2776 |
  | 6-7 | ED2778A / B, "Delta & Delta 8 group output" |
  | 8-9 | ED2779A / B, LH master |
  | 10-13 | ED2780, RH master |
  | 14-17 | ED3151, ED3344A-C, Theatre input |

## 1. What the parent family does (verified on the drawings)

**1.1 The Venue input (ED2911A / B) is the 8-group build of the DLX channel.**
- **The keys** (ED2911A routing matrix, "1/8W resistors"):
  - S9 MIX (R58 / R59), S10 1-2 (R60 / R61), S11 3-4 (R62 / R63);
  - S12 5-6 (R80 / R81), S13 7-8 (R82 / R83).
  - Each pair is 10K. An unassigned key grounds the resistor's far end.
- **Panning:** there is no PAN switch; every bus takes the pan buffers.
- **ED2911B's notes:** "FOR DELTA DLX: DO NOT FIT SW12, SW13, R80, R81, R82, R83, C35. IC5 PART CHANGES TO TL072". So the
  DLX is the 4-group build of the same board.

**1.2 The motherloom pinout (ED2911A CN2, each trace followed).**

| Pins | Signal |
|---|---|
| 15 / 13 | groups 1 / 2 (S10-A / B) |
| 11 / 9 | groups 3 / 4 (S11) |
| 7 / 5 | groups 5 / 6 (S12) |
| 3 / 1 | groups 7 / 8 (S13) |
| 18 / 17 | MIX L / R (S9-A / B) |
| 20-25 | AUX 6…1 |
| 26 | GND CANCEL through R75 10R |
| 27 / 28 / 29 | PFL+ / PFL− / PFL DET |
| 30-34 | rails |
| 2-16 even | ground, with the CN4 ¼" spade |
| 19 | empty |

- **Ours:**
  - groups 1-4 on 15 / 13 / 11 / 9 and MIX on 17 / 18, from ED3344C;
  - pins 1, 3, 5, 7 and 19 spare.
- **So:** groups 5-8 use exactly our spare pins 1, 3, 5, 7. Our bus is already Venue-compatible for 8 groups, provided
  those four pins stay free.
- **Crosstalk:** each of them sits between ground pins (2 / 4 / 6 / 8), as groups 1-4 do.

**1.3 The routing resistors and the pan.**
- **Routing:** the Venue's routing resistors are 10K; ours are 4K7.
- **Pan buffers:** ED3344C's again. IC6-A / B TL072 at 1.22× (R54 / R57 2K2, R53 / R56 10K), with R52 / R55 3K3 back to
  the wipers: the −4.4 dB law we adopted in strip v5.4 (CS2).

**1.4 Mute groups are on a separate loom, not the motherloom.**
- **The connector:** ED2911B CN6 is a 10-way IDC:
  - pins 1-4: MUTE 4, 3, 2, 1;
  - pins 5 / 6: LOGIC GND;
  - pins 7 / 8: +17 V (+VL);
  - pins 9 / 10: −17 V (−VL).
- **The keys:** S14-S17 (M1-M4) diode-OR the channel's mute (D9-D12) onto those lines.
- **The stereo input:** ED2915B's legend reads S8-S11 for groups 1-2 to 7-8 and S12-S15 for MUTE BUS 1-4.
- **The rule:** "all components omitted if mute system not used" (ED2911B).

**1.5 The master side: one group per module, a link picks the bus.**
- **ED2778A, "Delta & Delta 8 group output"**, is one group module:
  - **The bus:** its GROUP ASSIGN links J1-J8 pick GRP 1-8, with J5-J8 boxed as the 8-group option.
  - **CN1:** carries GRP 1-8 on 15 / 13 / 11 / 9 / 7 / 5 / 3 / 1.
  - **The summer:** a discrete 2SB737 pair and an NE5532, at −7.8 dBu.
  - **Its notes:** "FOR DELTA 8 OUTPUT": R50 8K2, C16 100 pF, CN6 not fitted.
  - **The Delta 8:** eight of these, each jumpered to its own bus.
- **ED2780 (RH master):** the talkback feeds "GROUPS 1 - 8, 10 × 30K" (GRP 1-8 + MIX L / R) on the same pins. The master
  was 8-group-ready even in the 4-group consoles.
- **ED2778B:** the group's LED meter.
- **Not read in detail here** (not group-specific): ED2779A / B (the aux masters, in `docs/console_survey/delta.md`) and
  ED2776.

## 2. An 8-group option for our console (costed, not proposed)

**Our structure:** our group module is one sub, one aux master and two stereo returns, with SUB / AUX select jumpers.
That is already the ED2778 pattern (one group per module, a link per bus). So 8 groups means 8 group modules. The
master needs no SUB 5-8 summers: each group module sums its own bus, re-inverts against its local GCANCEL buffer, and
pans to MIX.

**2.1 The strip, per strip:**

| Item | Parts | Notes |
|---|---|---|
| Routing keys 5-6, 7-8 | 2 × C&K PVA2 + PV caps | a second key row |
| Routing LEDs | 2 yellow + 2 resistors | pole B, as D6-D8 |
| DG413 | 2 × DG413 + 6 decouplers | one DG413 per assign pair, as U9-U11: no spare section to reuse |
| Summing resistors | 4 × 4K7 1 % | SUBSRC_L / R → pins 7 / 5 / 3 / 1 |
| CN1 pins 1 / 3 / 5 / 7 | nets instead of NC | no new connector |

- **Panel** (8 HP × 12U, `panel_layout.py`):
  - **Room:** five keys don't fit one row across 40.3 mm at the PVA2's 8 mm hole and ~11 mm pitch.
  - **Where:** the free band is between PFL / ON (y 292) and the fader slot's top (y 317; the slot is 110 mm long,
    centred at 372). A second row at about y 301 with LEDs at about y 310 leaves ~5 mm to the slot.
  - **To check:** the "+10" scale numeral and the fader cap at the top of travel.
  - **Fallback:** move the key block up into the pan / DIR area.
- **Board:** about 18 more parts (two SOIC-16 among them) on a board at 325 parts. That needs a placement trial; the
  DG413s belong in the header zone beside U9-U11.
- **Signal:** each strip's routing loads POST more; 5 × 2 × 4K7 per side is still a light load for the OPA1612 pan
  buffers. Bus noise per group is unchanged (24 × 4K7 per bus, as SUB 1-4).

**2.2 Group modules: 8 instead of 4.**
- **Width:**
  - today 24 strips + 4 groups + the 16 HP master = 240 HP = 1219 mm;
  - with 8 groups 272 HP = 1382 mm, +163 mm.
  - The frame rails (FR1-FR3, 1227.2 mm), the tub (TB1-TB4) and the panel screw lines grow with it.
  - Or keep the width: 20 strips + 8 groups.
- **Ribbon:** each wing goes from 14 to 16 modules (12 strips + 4 groups), +82 mm and two more sockets. Ribbon C / R
  per bus grow by the same 14 %.
- **The group board:**
  - **Jumpers:** 4 more SUB-select solder jumpers to pins 7 / 5 / 3 / 1, still one SUB and one AUX per board, unique
    across the eight (master spec §12).
  - **Groups 5-8 would have no aux bus** (we have 6 aux: 1-4 on groups 1-4, 5 / 6 on the master). Either leave their
    aux master unfitted, or move aux 5 / 6 to groups 5 / 6 to free the master.
  - **Returns:** 8 groups give 16 stereo returns. Return 2 could stay unfitted on groups 5-8.
- **Alternative, two subs per group module:** it would need a second fader and a second sub chain in 8 HP. No room on
  a panel that already carries two returns and the aux master.

**2.3 The master.**
- **Summers:** no SUB 5-8 summers or re-inverters, since the groups carry them. The master's headers pass pins
  1 / 3 / 5 / 7 through.
- **AFL / PFL:** the group AFL keys sit on the PFL bus already (42 keys in `sim/pfldet.py` → 50).
- **Re-check:** `sim/pfldet.py`'s 24-press margin, now 0.92 / 1.29 V against the 0.50 V threshold.

**2.4 Power** (master spec §27).
- **Per group module:** about 107 mA per rail typical and 135 mA at maximum IQ. That is the 61 mA base, 16 mA return-1
  followers and 30 mA return 2. Without return 2 it is about 77 mA.

| | today | 8 groups (full modules) |
|---|---|---|
| Console +V, typical | 3.31 A | ≈ 3.74 A (+ routing LEDs, lit: up to 0.14 A) |
| PSU rating per rail | 4.0 A | 94-97 % typical |
| Worst corner (+V) | ≈ 4.54 A (accepted) | ≈ 5.2 A |
| Wing +V (MF-RX250/72, hold 2.03 A at 40 °C) | 1.48 typ / 2.07 corner | 1.69 typ (83 %) / 2.34 corner (115 %) |
| Wing −V (MF-RX185/72, hold ≈ 1.50 A at 40 °C) | 1.05 / 1.30 | 1.26 (84 %) / 1.57 (105 %) |
| IDC contacts (1 A each) | +V 0.49, −V 0.53 A typ | +V 0.56, −V 0.63 A typ |

- **Typical use:** within the PSU, but with no margin left.
- **The corner:** past both the PSU's 4 A design point and the wing PTCs' hold.
- **To fix:** a PSU revision (the LM1084 is a 5 A part, so an LT1083-class LDO or two in parallel, a larger heatsink),
  or fewer strips.
- **Returns:** leaving return 2 off groups 5-8 saves about 0.12 A.

**2.5 Mute groups, optional (a CN6-style loom, the Venue's way).**
- **The loom:** a separate 10-way IDC on every strip (MUTE 1-4, ±VL, logic ground), daisy-chained like the motherloom.
  The 34-way has no free conductors for it, so this is the Venue's choice as well.
- **Per strip:**
  - 4 PVA2 keys (M1-M4);
  - 4 diodes ORing into the J112 mute drive, beside SW4;
  - the 2×5 header.
- **Master:** 4 mute-group master keys with LEDs and line drivers, and two headers (one per wing).
- **The cost:** the strip panel. Four more keys need another full key row, which only fits by moving the pot columns
  or growing the panel past 12U. `console_survey.md` §7 already set mute groups aside for that reason (GL3300).

## 3. What it touches among the signed decisions

- **4 subgroups:** "4 subs (with inserts)".
- **The bus pinout:** spares 1, 3, 5, 7, 19. Under this study, 1 / 3 / 5 / 7 would be SUB 5-8, as the Venue.
- **The structure:** the M1 module split (4 group modules) and the group bus-select jumpers.
- **Width:** the frame rails and the tub.
- **Power:** the PSU's 4 A rating and the accepted wing-PTC corner.

## 4. A no-cost step either way

Keep CN1 pins 1, 3, 5 and 7 unconnected on every board (they are today) and record them as reserved for SUB 5-8
(the Venue pinout). That keeps an 8-group console, or a genuine Venue / Delta 8 module, possible without touching the
loom. This study does not change CLAUDE.md or any spec. Recording the reservation is Ruslan's call.
