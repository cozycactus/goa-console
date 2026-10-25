# Independent design review (2026-10-25)

Three reviewers worked in parallel, read-only, from the repo alone:
- **A:** every pin of every part against its manufacturer's datasheet;
- **B:** logic sense and polarity, by netlist analysis plus phase simulations at every output;
- **C:** every spec section and signed decision against the generated netlists and BOMs.

I verified each finding below against the source before listing it. Their scratch files are in /tmp/review_A, B and C;
they are not kept.

## Findings

| # | Severity | Finding | Verified | Proposed action |
|---|---|---|---|---|
| R1 | **BLOCKER** | **DRV134UA doesn't fit the SOIC-8 footprint.** The MPN is "TI DRV134UA" (`master_lib.py`), on master U7 U8 U9 U14 U16 U24 U25, group U4 U7 (×4) and jig U8. TI SBOS094B p. 1: "The DRV134 is available in 8-pin DIP and SOL-16 … The DRV135 comes in a space-saving SO-8". DRV134UA is the 16-pin wide SOIC with another pinout. The symbol, footprint and every connection match the SO-8 pinout exactly. Found by all three reviewers. | yes, TI datasheet | **MPN → TI DRV135UA**: same die family, one datasheet table, the same pinout. No netlist or layout change. The signed "all balanced outputs use TI DRV134" decision becomes "DRV134 family, SO-8 = DRV135UA". |
| R2 | MAJOR | **Group sub pan RV2 is a part that doesn't exist.** It is listed as "Alpha RD902F-40 B10K centre detent" on all four group boards (`schgen.MPN['POT2']`, master spec §12 / §15). The RV8 decision (2026-10-25) established that no Alpha B10K dual with a detent exists. | yes | **ALPS RK09L1240015** (footprint `Potentiometer_Alps_RK09L_Double_Vertical`, `placer.pot(..., sx=10)`), the same part and change as the strip's RV8. Group placement re-run. |
| R3 | MAJOR (jig only) | **Jig stub R45 (3K3, 0805) takes about 0.31 W** while any PFL key is pressed. The PFL ACTIVE LED sinks into an LM393 on ±VL. This is the fault MG13 fixed on the master's R124. | yes | **Panasonic ERJ-P06J332V** (anti-surge 0805, 0.5 W), as on the master. |
| R4 | MAJOR (assembly) | **No board marks which way a PVA2 key goes in.** The footprint is symmetric under 180°, and every key relies on the moulded "2" sitting in the pad 1/4 column (spec §16.1). A key fitted backwards inverts its function: ON mutes, routing inverts. Found by A and B. | yes, no silk on any board | **A silk "2" beside pads 1/4 of every PVA2** (placement-stage silkscreen; no copper). |
| Q1 | question | **ON (SW4) doesn't mute the pre-fade aux sends or the direct out.** JP2–JP4 tap PRE, before the J112 mute; simulated, aux 1 pre is unchanged with ON released. This matches the spec's drawing (§1, §11), so it isn't a wiring fault. Most consoles' channel mute kills pre-fade sends too. | yes (`gen.py` 238) | Your call: keep as drawn, or take the pre taps (and DIR) from MUTEOUT. |
| R5 | MINOR | **Documentation and BOM drift.** No circuit is affected; listed in full below. | yes | I fix these on sign-off; none of them changes a decision. |

**Notes that need no change now:**
- **Comparator supplies.** The master's LM393B and LM2901B run from ±VL / ±VM, 34 V. The PSU crowbar fires at 19.1 V a rail, 38.2 V across them, just over their 38 V absolute maximum for the instant before the SCR fires.
- **XLR ground contact.** The NC3MAV "G" pad is unconnected; pin 1 is CHASSIS. Tie it to CHASSIS if the housing variant has the contact.
- **Fader pin side.** The PTB0143/0144 pin side of the slot rests on a Bourns drawing that contradicts itself. It is already on the sample-check list; check a 1:1 print before ordering.
- **Sample checks still needed:** the PVA2 latched throw, RK09L pin 1 at CCW, and the fader taper end. A, B and the earlier reading of the datasheets agree on them, but nobody has checked a sample.

**Checked and correct.** Reviewers A and B verified every part type against its datasheet, on every instance:
- OPA1612, OPA1656, TL072H, LM393B, LM2901B;
- DG413 pinout and truth table, routing and PFL switcher sense;
- LME49600, LM1084, TL431, 2N6505, MMBFJ112, MMBT3904 / 3906, BCP53, BAT54W, BZX84, SS54 / S1G / 1N4148 and LED polarities;
- G6K-2F-Y coil, contacts and flyback;
- NJ6FD-V pads, including the TN / RN normals; NC3MAV pins 1 / 2 / 3;
- Alpha RD901F / RD902F and ALPS RK09L pin roles;
- MF-RX pitches, Keystone 1287-ST, the Phoenix terminal, every IDC link and the 34-way bus on all five headers.

Signal polarity is in phase (0 ± 2.3°) at every output, and the strip's Ø key gives 179°. Reviewer C found every
signed decision present as signed, apart from R1 and R2, and all nine netlists at 0 mismatches.

## R5: drift to fix

- **Strip spec:**
  - §14 still calls U4B a spare;
  - the §15 part counts and the C12 / C62 rule are stale;
  - §16.3 still says 260 + 6;
  - §17 supply figures are from before v4.4;
  - the footer says 4.3, and the strip sheets' title blocks say rev 4.3 (`gen.py`);
  - the common mode at 1 kHz is now −56.0 dBu (since C94 / C95), still within its −50 dBu limit.
- **Strip BOM:**
  - MPNs missing for the C0G caps, the rail electrolytics, R6–R9 0.1 % (the master already uses KEMET, Nichicon and
    ERA-6AEB parts), C48 and D9;
  - the aux pots lack the RD901F-40-15R1 order code;
  - C49 and master C57 use the W8.5 film footprint while the other MKS2C042201K00KSSD sit on W7.2;
  - C57's MPN isn't orderable.
- **Value texts** say "25V" where the MPN is a 35 or 63 V part (master C5–C8, group C1–C4, jig C3 / C4). Jig R1 / R2
  aren't anti-surge parts (the master's are).
- **Master spec:**
  - G2b / G3b contradictions: the header line, the §12 / §13 / §20 sleeve notes and the §16 receiver diagram;
  - §17's 47 µF is now 33 µF, §5's 220 µF is now 100 µF;
  - the OPA1656 counts in §15 / §23;
  - stale figures in §24 / §27 (the 2.65 A / 3.8 A note and the MF-RX185 wing paragraph);
  - the §29 counts and the footer version;
  - MG12 / MG13 refer to old refs (now R58, R54, R124).
- **CLAUDE.md:** "What this is" (v4.5), the Files entries (v4.3, the jig spec v0.6), and "2 conductors per rail"
  (3 on +V since W1).
- **console_architecture.md:**
  - §3.2 load and pins 30–34;
  - §3.3 LM338 / transformer bullets that contradict option B;
  - §3.4 "+VM/−VM" logic rail (it is ±VL) and the star "at the PSU" (it is the master's stud);
  - the title / footer versions.
- **Other docs:**
  - psu_spec.md §1 load figures;
  - test_jig_spec.md's MF-RX160 note;
  - README.md (strip v4.1, the old pan-pot note).

## Sign-off

- [ ] **R1** DRV135UA for every balanced driver.
- [ ] **R2** Group RV2 → ALPS RK09L1240015.
- [ ] **R3** Jig R45 → ERJ-P06J332V.
- [ ] **R4** Silk "2" at pads 1/4 of every PVA2.
- [ ] **R5** Documentation and BOM drift.
- [ ] **Q1** ON muting the pre-fade sends and direct out: keep as drawn, or tap them after the mute.
