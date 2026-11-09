# Delta DLX service manual vs goa-console: sheet-by-sheet cross-check (2026-10-28)

Every ED sheet in `ref/Sndcft_DeltaDLX_Schems.pdf` (17 pages, vector; rendered at 300 dpi, read in 300-dpi tiles and
2-4x crops) against our schematics as generated today (strip v5.5 `tools/gen.py`, group `tools/gen_group.py`, master
`tools/gen_master.py` with `tools/master_lib.py`; the exported netlists), stage by stage. Four readers (one per sheet
group), each cross-checking against the 200 Delta Technical Manual ZZ2593 circuit descriptions (Part 2 p.55-56, 61-65)
and connector tables (Part 3 p.114, 124, 128). The per-sheet tables are in Parts A-D below (Delta as read, refs and
values / ours by ref and value / status / note). Status: SAME, RECORDED (a departure already written down, with the
pointer), UNRECORDED (nobody wrote it down: listed for sign-off in §2), N/A (Delta-only context), UNREAD.

| PDF p. | Sheet | What | Part |
|---|---|---|---|
| 15 | ED3344A | Theatre input RH PCB: line input, gain, HPF, 4-band EQ, insert | A |
| 16 | ED3344B | Theatre input RH PCB: ON logic, mute control, LED current source, peak detector | A |
| 17 | ED3344C | Theatre input RH PCB: mute block, fader + post-amp, aux, pan, routing, direct out, CN2 | A |
| 14 | ED3151 | Venue II / Delta Theatre input LH PCB: switches, pots, LEDs, routing keys, aux source | A |
| 6 | ED2778A | Delta / Delta 8 group output (summer, insert, fader, post-amp, pan, output, returns, AFL, assign links) | B |
| 7 | ED2778B | group output sht 2: the group's 20-LED meter | B |
| 8 | ED2779A | LH master: six aux summers with ground cancel, masters, AFL, outputs, loom, power | B |
| 9 | ED2779B | LH master sht 2: Mix L meter | B |
| 10 | ED2780 sht 1 | RH master: monitor select, PFL switcher / sum / detect, C/R and phones amps, talkback, oscillator, loom, power | C |
| 11 | ED2780 sht 2 | RH master: mix summers, insert, post-amps, balanced outputs, mono | C |
| 12 | ED2780 sht 3 | RH master: meter (right) | C |
| 13 | ED2780 sht 4 | RH master: BVE option programme links | C |
| 1-2 | ED2911A / B | Venue input (the 8-group build of the Theatre strip; mute groups) | D |
| 3-4 | ED2915A / B | Venue stereo input | D |
| 5 | ED2776 | Delta dual line input | D |

## 1. Result

- **Strip (Part A, ~45 rows):** stage for stage the Delta Theatre input. Every substantive departure is recorded
  (receiver + separate gain stage, sweepable HPF, KHN mids, 4K7 / DG413 routing, the CS2 pan law, film / MUSE ES
  couplers, MET1 / CS1 detector, fusibles and clamps, op-amp types, levels); the Delta's gain range read literally is
  −15.5…+15.2 dB against our −15.0…+14.8.
- **Group / aux (Part B, 69 rows):** same or recorded (M1, 4K7, ground cancel on every summer + re-inverter, DRV135 /
  G2b / CS4b / CS4c / CS6 / CS10 / CS11b, CS2b at −4.4 dB against the Delta group's passive −4.6 dB, G3b, levels, no
  −10 dBV, no group meters). ED2778B and ED2779B are meters (N/A for the groups; the master's ladder top 16K follows
  ED2779B's R309).
- **Master (Part C, ~45 rows):** same (motherloom pins 1-33, XLR pin 2 hot, ladder / comparator / LED-string / current
  source architecture, average ballistics, meter tap after the switcher, EXT select) or recorded (parts, 4K7 + ground
  cancel + re-inverters, keeper, insert level / buffer, post-amps, mono, DRV135 + relays + power-on mute, DG413, PFLDET
  clamp, DIM CS7, full-wave detector, pin 34, PTCs / star). N/A and explicitly excluded: talkback, oscillator, +48 V,
  the BVE option.
- **Venue / stereo / dual line (Part D):** nothing contradicts a signed decision or the bus map; ED2915A's CN1 confirms
  the ED3344C order and the SUB 5-8 reservation on pins 1 / 3 / 5 / 7.
- **Nothing read as a fault in ours.** The unrecorded items below are conventions, omitted features and record
  corrections; two of them need a decision (D1, D13).

## 2. Unrecorded discrepancies for sign-off

Merged from the four readers (their own numbered lists, with the evidence, are at the end of each Part). Each item:
what the Delta does, what ours does, the recommendation and **why** — the reason is the part to disagree with.

**Decisions needed**

- **D1 Insert jack tip / ring sense (strip J2, master J1 / J2, the groups' sub inserts, the jig).** Delta: tip = return,
  ring = send, console-wide (ED3344A JSK2, ED2780 sht 2 JSK1, manual p.124 / p.128). Ours: tip = send, ring = return,
  ring normalled to the send. Readers A and C found it independently; no document records it, and it was never
  decided (gen.py's `{'T': 'SEND', 'R': 'RET_RAW'}` simply followed the common convention).
  Recommendation: **keep tip = send, document it** (strip spec §7 / 16.4, master spec §4, `docs/studies/delta_clone_comparison.md`
  §2; panel legend "INSERT tip = send" when the panels are next regenerated).
  Why: electrically the two are identical (75R send build-out, 47K return bleed, the normalling works both ways), so
  the only thing at stake is which cables fit. Tip = send is what Mackie, Allen & Heath, Yamaha, Behringer, later
  Soundcraft (Spirit, Ghost) and the commercial "insert cable" (the TS marked SEND on the tip) use; ring = send is the
  1980s Soundcraft convention and serves only Delta-era looms. Adopting the Delta's would make every insert lead bought
  or made "backwards" relative to its label for the console's life. The one reason to switch: existing Delta-wired
  looms or a patchbay wired ring = send that are to be reused (then it is a T / R swap in four generators).
- **D13 Unused / spare bus conductors.** Delta LH master grounds every group bus no module sums (ED2779A links J2-J9);
  ours left pins 1 / 3 / 5 / 7 (SUB 5-8) and 19 floating, joined only wing to wing (SPARE1-7). Recommendation:
  **adopt**: one bridged solder jumper per spare conductor to GNDA on the master only (JP3-JP7, applied below), the
  modules keep them unconnected as decided 2026-10-27; open the jumpers for an 8-group build.
  Why: a floating conductor between grounded ones couples capacitively to its neighbours and re-radiates them (19 lies
  between MIX L on 18 and AUX6 on 20; 1 / 3 / 5 / 7 lie between ground conductors 2-8, so they matter less), and a
  floating line on a header is also an ESD / hot-plug antenna. Grounding at the master costs five jumpers and no board
  area, adds a shield between MIX L and AUX6, and changes nothing a module sees (they are NC there). The Delta does
  exactly this for the same reason. Against: none found; the only cost is remembering to open them for SUB 5-8, which
  the silk and the spec note cover.

**Keep, document (the record is wrong or silent)**

- **D2 PAN LED.** Delta Theatre LD2 red, shorted by SW5-D when PAN is off; ours none (SW14's two poles both carry audio).
  Recommendation: keep, note it in the strip spec's LED list. Why: adding it needs a third pole (a 4-pole key, which
  the PVA2 range lacks) or a spare comparator / DG413 section, for an indication the key's latched height already gives
  (as on the PRE and DIR keys, which the Delta itself leaves without LEDs); not worth a part and a panel hole.
- **D3 Soft mute: topology and record.** Delta: series J112 (TR4) into IC6-A's virtual earth + shunt J112 (TR3) with
  its source on C30 47 µF, gates on MUTE / MUTE-bar from a TR6 / TR7 inverter pair (220K / 100n, 1N4148, 680K bleeds);
  the Venue the same with the shunt source on a 47 µF (no DC across the FET). Ours: two shunt J112s in a 4K7 ladder
  into a follower, one 220K / 100n ramp from the key (~86 dB). Recommendation: reword `docs/studies/delta_clone_comparison.md` §2
  and `console_survey/delta.md` T7 (they say "same J112 circuit", which is false); keep the circuit; add the
  cap-isolated shunt source to `docs/proposals/clicks_proposal.md` RV5 as an alternative. Why: the depth question is already
  `docs/studies/console_survey.md` CS8, deferred to the jig (86 dB simulated against the Delta's 100-110 dB), and a second pass of
  simulation would not settle what a bench measurement will; but the record must not claim a sameness that isn't
  there, and the Delta's cap-isolated source is the cheapest fix for RV5's DC-on-the-fader if the bench shows a click.
- **D4 Insert-return input impedance.** Delta C24 47 µF → R45 4K7 into IC5-B's virtual earth (≈ 4K7; spec sheet says
  10K); ours 47K + 1K into a follower. Recommendation: keep, document. Why: 47K loads an outboard output ten times
  less than 4K7 (an outboard with a 600R-class output doesn't care; a passive or valve unit does), the follower is
  already signed off for stability (T8 / C84), and the LF corner of our return (C10 33 µF / 47K: 0.1 Hz) is better.
- **D5 Routing resistors.** Delta 10K 0.5 W (R126 / R127, ED3151 R1-R4); ours 4K7 1 % 0805 (0.125 W). Recommendation:
  keep, document. Why: the dissipation case is a bus shorted to a 17 V rail: 17² / 4K7 = 61 mW, half the 0805's rating;
  normal signal is < 15 mW. The Delta's part is "MINI-RES MF 1/2W 5% 10K" (spare-parts list p.154 / 158: a 5 %
  miniature 0.5 W metal film, where every other resistor on its boards is "MF 0.25W RES 2%"), a margin choice for the
  one resistor a shorted bus can load, not a precision part (corrected 2026-10-29; the text had guessed 1 % metal
  film), and 4K7 against 10K is a recorded decision (3 dB quieter bus).
- **D6 LED colours and drive.** Delta: one ≈ 6 mA series chain from a 2SA970 current source, routing LEDs amber, EQ
  green, PFL / PEAK / PAN red, ON green; ours 4K7 per LED from +VL (≈ 3 mA), routing yellow WP710A10YD. Recommendation:
  keep, document (amber = Kingbright WP710A10SEC/J if the colour is wanted). Why: a series chain needs every LED in
  the loop and shorting poles on every key (the Delta spends a switch pole per LED on it), while per-LED resistors
  let a lit LED draw only its own 3 mA from the logic rail and leave the keys' poles for logic (the DG413 drive);
  3 mA in a modern GaP / GaAsP LED is as bright as 6 mA was in 1990's parts. Yellow vs amber is taste.
- **D7 Aux 5 / 6 pre-EQ option.** Delta links J4-J7 cover aux 1-4 only (aux 5 / 6 PRE = pre-fader); ours JP2-JP4 give
  all three pairs the choice. Recommendation: keep, document. Why: a strict superset (default 1-2 = pre-fader, as the
  Delta), one solder jumper per pair; removing it would save nothing.
- **D8 EQ bypass.** Delta SW3-A (Venue S5-A / S3-A) grounds the idle EQ's input; ours SW12 only selects the source
  (pole B drives the EQ LED), the bypassed EQ keeps running. Recommendation: keep, document. Why: the only path from
  the idle EQ to the signal is the PVA2's open contact, and the idle EQ carries the same programme (HOUT), so its
  crosstalk is the programme itself — no level or noise effect is possible; the pole the Delta spends on grounding
  gives us the EQ-in LED instead, which the Delta has too but pays a chain pole for.
- **D9 Peak-detect tap.** Delta Theatre: SW3-B output, post-EQ-switch, pre-insert (the Venue the same); not
  "post-insert" as `docs/studies/delta_clone_comparison.md` §2 says. Ours (CS1) taps EQOUT and PRESRC among five. Recommendation:
  fix the row. Why: a record error; ours already covers both points, so no circuit change follows.
- **D10 Peak threshold.** Delta Theatre ≈ +14 dBu by calculation (R92 470K / R88 56K, positive only; the manual's
  +9 dBu is the Standard input), decay ≈ 1.5 s; ours +18.4 dBu both polarities, 150 ms hold (CS1,
  `console_survey/delta.md` §4.5). Recommendation: keep, record the Delta's number. Why: the margin question was
  already argued in CS1 (+18.4 dBu = 4 dB under the strip's +22-23 dBu clip, which the Delta's +14 does not match
  because its headroom is lower); a lower threshold would light red on EQ boosts that aren't clipping. If the bench
  disagrees, +15 dBu is a one-resistor change (R40 / R41) — so nothing to decide before the jig.
- **D11 ON logic levels.** Delta derives ±VM ON / ON-bar (TR6 / TR7, also the ON-LED switch); ours drives the gate RC
  from the key. Recommendation: keep, document. Why: the complementary lines exist on the Delta to drive its
  series + shunt FET pair and a remote-mute input; ours has one shunt pair and no remote mute (the Theatre has none
  either), so the inverter would drive nothing.
- **D12 Coupler between HPF and EQ.** Delta C14 47 µF (and C11 before the HPF); ours C38 / C91 before the HPF, HPF →
  EQ DC-coupled. Recommendation: keep, document. Why: the KHN HPF's output offset is the summer's Vos plus the
  integrators' (a few mV); every EQ stage is a unity inverter and the insert send is AC-coupled by C51, so the offset
  reaches nothing a user can hear or measure, while a 47 µF NP in that spot would add a part, a corner and ~0.5 dB of
  LF phase in the HPF's own passband.
- **D14 No +4 dBu / −10 dBV operating-level switch.** Delta S1 (6 poles) pads the post-amps 11.6 dB (1K2 / 430R) and
  raises the four monitor receivers 10.4 dB (6K8 / 20K / 2K2 T); ours fixed gains, EXT unity. Recommendation: keep,
  document in master spec §17 / §7 with the option (EXT receivers' 10K legs → 24K3 0.1 %, R85 / R90 and R87 / R92, for
  a gain of 2.43, +7.7 dB; the exact −10 dBV → +4 dBu ratio is 2.45). Why: the console's destinations are +4 dBu (DAW interfaces, the bus compressor), so the main
  outputs need no −10 pad, and a −10 dBV source on EXT is 7.8 dB low on the C/Room only, which the C/ROOM pot covers;
  a 6-pole switch in the output and monitor paths is contacts in the signal path for a case that is not planned.
- **D15 Peak-meter release.** Spec §22 calls our 0.55 s (C160 / C178 1 µF, R146 + R147 550K) "Delta-like"; the
  Delta's R306 22K / C301 10 µF is ≈ 0.22 s. Recommendation: keep 0.55 s, correct the wording. Why: the slower fall
  is easier to read on a 20-LED bar and is within the usual peak-meter range (DIN 1.5 s, "fast" PPMs ~0.5 s); only
  the claim of likeness is wrong.
- **D16 Remote meter header.** Delta CN8: 1 METER L, 2 ground, 3 +17 V, 4 METER R, 5 −17 V (logic rails); ours CN4:
  1 MTR_L, 2 MTR_R, 3 +VM, 4 GNDM, 5 −VM. Recommendation: keep, document in spec §22. Why: a Delta meter bridge is
  not going to be plugged in, and ours feeds the bridge from the meter rails and meter ground (GNDM) so a bridge's
  LED current stays off the audio ground — the better arrangement.
- **D17 Monitor-select receiver reading.** `docs/console_survey/delta.md` Monitoring omits the switched T on the −
  leg (6K8 + 20K, 2K2 to ground through S1: −4.1 dB open, +6.3 dB closed; the bridge is 26.8K vs 22K, not
  ratio-matched). Recommendation: survey correction only. Why: it describes the Delta, not ours.
- **D18 Returns: what the Delta / Venue returns have and ours don't.** Delta group tape returns: 2-band shelving EQ
  (IC2-B, VR1 / VR2 10K lin, 4K7 + 6n8, 7K5 + 5K1 + 100n) and an aux-1 send (VR3 / VR8 20K log + 22K); the Venue
  stereo input: A / B select, Ø, ±15 dB trim, width / mono, 3-band EQ, balance, mono sums, six aux sends, a stereo
  peak LED. Ours (spec §16): receiver, level, buffers, routing, PFL. Recommendation: keep, one sentence in §16 that
  these were seen and left out. Why: a return here is an effects return (reverb / delay back into the mix), eight of
  them on four 8 HP panels that are already full (RET 1 / RET 2 knobs + PFL + routing keys per group); anything that
  needs EQ, trim or an aux send is a line source and takes a strip, which is what the 24 strips are for. A stereo
  peak LED per return would be 8 × ~12 parts and a panel hole each for a condition PFL shows.
- **D19 Group insert send build-out.** Delta group R112 220R (its mix insert 75R); ours 75R everywhere. Recommendation:
  keep, document. Why: 75R vs 220R into a ≥ 10K outboard input is 0.06 dB vs 0.19 dB of loss and no difference in
  drive; the short-circuit case (a send into ground) is already covered by the anti-surge ERJ-P06J750V; one value
  for every insert keeps the BOM and the jig's test 13-14 fixtures the same.
- **D20 PFLDET resistor grading.** Delta LH master R201-R206 100K / 100K / 100K / 82K / 68K / 47K for aux 1-6 (to
  overcome its TL072 detector's 150K bias); ours 100K on every key (LM393B, 1 µF, `sim/pfldet.py` 42 keys).
  Recommendation: keep, document. Why: the grading compensates the Delta's detector threshold against the number of
  keys ahead of it on the line; our detector is a comparator against a fixed 0.50 V reference with a clamp, simulated
  for one press (0.92 V) through 42 presses with released LEDs at ≤ 20 nA — there is nothing to compensate.
- **D21 Jack-sleeve ground.** Delta: every jack sleeve and the gain pot's bracket on a socket ground tied to module
  ground by 10R (ED3344A R144, ED2911A R76, ED2915A R74, ED2776 R45); ours: balanced inputs / direct out on CHASSIS
  (G2), the insert sleeve on GNDA directly (`docs/studies/ground_study.md` §5.3 evaluated the 10R only for the line input).
  Recommendation: keep, document; the insert with a real earthed processor is on the jig list. Why: G2's CHASSIS for
  the balanced jacks is the AES48 arrangement and better than a 10R tie; for the unbalanced insert the sleeve is the
  signal reference, and 10R in it would put the loop current's drop into the send / return reference (the Delta
  accepts that; we'd rather see on the bench whether a loop exists at all before adding a resistor in the reference).
- **D22 Pin 28.** The Venue stereo input uses pin 28 (PFL−) as a polarity-correcting PFL input when its inverting
  mute block is fitted (ED2915B note); ours leaves 28 open on every board (CS5: GNDA at the master is a free option).
  Recommendation: one line in the bus decision. Why: it only matters if a real Venue stereo module is ever put on
  our bus, and then its PFL would be silent — the note prevents a puzzling bench hour, nothing more.
- **D23 Delta line gain ranges, read literally.** ED3344A / ED2911A −15.5…+15.2 dB (S2-D shorts R24 in line mode),
  ED2915A −13.4…+17.3, ED2776 −13.4…+16.5; ours −15.0…+14.8. Recommendation: close `docs/studies/delta_clone_comparison.md` §2's
  "not fully traced". Why: the numbers match within 0.8 dB; the open note was the only loose end.
- **D24 Venue oddity, no action.** ED2911A feeds its PFL key through two 22Ks (R46 post-C23, R108 pre-C23); a Venue
  module on our bus would PFL 6 dB hot. Note only. Why: not our module; the note is for the same borrowed-module case
  as D22.

**Unread (at 300 dpi):** ED3344A CN5 (two pins on SKT1's normals) and the link positions Z1 / Z2 / Z20 in the ground run
to the spade (ED3344C); the "−0.5 dB" legend on IC6-B (computed +1.4 dB); VR1 "MASTER LEVEL" value and Z3 / Z4 "L29998"
on ED2779A; the group PFL LEDs' return path (ED2778A). None touches ours.

## 3. Status

Signed off by Ruslan 2026-10-28 ("proceed with your recommendations") and applied:
- D1 decided: tip = send stays; recorded in strip spec §7 / 16.4, master spec §4, `docs/studies/delta_clone_comparison.md` §2.
- D13 applied (master JP3-JP7 beside CN2, made last, placed by moves_only; master 1806 pins / 625 parts then, DRC 0).
- D2-D24 documentation: strip spec §4 (D23), §5 (D12), §6.1 (D8), §7 (D1 / D4 / D21), §8.1 (D9 / D10), §9 (D3 / D11),
  §11 (D7), §12 (D2), §13 (D5 / D6); master spec §4 (D1 / D19), §7 (D14), §16 (D18), §17 (D14), §19 (D20), §22
  (D15 / D16); `docs/studies/delta_clone_comparison.md` §2 (D1, D3, D9 / D10, D23); `console_survey/delta.md` T7 (D3), Monitoring
  (D17, and its stale "no dim" line); `docs/proposals/clicks_proposal.md` §6 RV5 (D3); CLAUDE.md bus decision (D22 / D24).


---

## Part A: Theatre input ED3344A / B / C + ED3151 vs the channel strip v5.5

Date 2026-10-28. Sources: `ref/Sndcft_DeltaDLX_Schems.pdf` rendered at 300 dpi (PDF p.15 = ED3344A, p.16 = ED3344B,
p.17 = ED3344C, p.14 = ED3151; crops kept by the reader, not in the repo), 200 Delta Technical Manual ZZ2593 Part 2 printed
p.55-56 (Standard input circuit description; p.61-65 are the group / aux / master modules and say nothing about the input
strip) and Part 3 printed p.124 (Deluxe input rear-panel pin table). Ours: `tools/gen.py` (the `P(...)` netlist),
`channel_strip.net` / `jack_board.net`, `channel_strip_schematic_spec.md` v5.5.

Reading conventions used below: Delta switch poles have the middle pin (2 / 5 / 8 / 11) as common; the Delta drawing marks
junctions with small squares and crossings without (confirmed at R32 / R36 on ED3344A, `docs/studies/delta_clone_comparison.md` §5).
Values are quoted as printed on the drawing. Where I computed a number it is marked "calc".

Status key: SAME / RECORDED (pointer given) / UNRECORDED / N/A / UNREAD.

---

### ED3344A — Theatre input, RH PCB: line input, gain, HPF, 4-band EQ, insert

| Delta (sheet, refs, value / topology as read) | Ours (refs, value / topology) | Status | Note |
|---|---|---|---|
| Line input jack SKT1 (TRS, 6 contacts); tip / ring through R1 / R2 15K to the line input stage; sleeve on INPUT GROUND. Normal contacts 4 / 5 wired to a 2-pin CN5 (CN5 1 / 2) | J1 NJ6FD-V on the jack board; tip / ring to IN_T / IN_R through the 2x5 link; sleeve on CHASSIS (C8 / C9 100p to CHASSIS); normals short tip and ring to GNDA when empty | RECORDED | Receiver: `docs/studies/delta_clone_comparison.md` §2 Input, §3 d.1; sleeves on CHASSIS: `docs/studies/ground_study.md` G2 (CLAUDE.md "Ground and hum"). CN5's purpose is not labelled on the sheet (UNREAD: probably a line-input link / meter-bridge feed). |
| INPUT GROUND: XLR pin 1, SKT1 sleeve, JSK2 / SKT3 sleeves and BKT1 (panel bracket) on one node, joined to the channel audio ground through R144 10R (plus solder links SWT1 1 / 2 "transformer grounding") | Balanced jacks' sleeves (J1, J5) on CHASSIS via the plated standoffs H1 / H2 to the panel; insert J2 sleeve on GNDA; no 10R between CHASSIS and GNDA on the strip | RECORDED | `docs/studies/ground_study.md` G2 / G2b; CLAUDE.md "Ground and hum". The Delta's 10R tie between input ground and audio ground has no counterpart in ours (CHASSIS and GNDA meet only at the master's star). |
| Line input stage IC2-A TL072: diff amp, R1 / R2 15K + R19 / R20 4K7 per leg, R22 3K3 (+ input to ground), feedback R21 3K3 from IC2-B's output; C45 12pF 100V across the feedback. IC2-B TL072 buffers the wiper of VR1-B 5K RD (reverse log, the line gang of the dual mic / line gain pot) which divides IC2-A's output across R23 150R + R24 330R; R89 3K3 wiper to ground; SW1-B shorts R24 in LINE mode (manual p.55: "S2 shorting the junction of R23 and R24"). Gain calc = (3K3 / 19K7) / k: −15.5 dB (k = 1) to +15.6 dB (R24 shorted; +6.7 dB with R24 in). Output "−5 dBu", C11 47µF 25V coupler, R142 100R to CN7 (optional meter bridge) | Receiver U1A OPA1612, R6-R9 10K 0.1 % (unity, inverting), C7 / C78 33p; U16 OPA1656 followers ahead of it (R10 / R112 1M, R110 / R111 220R, C94 / C95 100p, R113 / R114 100R); separate gain stage U1B (R45 / R46 2K2, RV9 10K B centre-detent, C37 22p): −15.0 … +14.8 dB, 0 dB at the detent; C38 + C91 33µF NP to HIN, R47 47K | RECORDED | `docs/studies/delta_clone_comparison.md` §2 Input / Gain, §3 decisions 1-2; buffered receiver `docs/studies/ground_study.md` G3; `console_survey/delta.md` T1. Ranges match within 0.8 dB. Delta line input impedance ≈ 2 × 19.7K differential (manual spec ">10 kΩ"); ours 1M per leg. |
| Ø switch SW2-A / SW2-B: swaps the two legs between R1 / R2 and R19 / R20 (ahead of the diff amp) | SW15 PVA2: swaps BUF_T / BUF_R between the followers and R6 / R8 | SAME | Same position in the chain (ahead of the differential stage). |
| Mic / line select SW1-A / C / D, mic stage (2SB737 TR1 / TR2, IC1-A / B, VR1-A 5K RD, C1 / C2 47µF 63V, transformer option, D1-D6, C10 47µF + R18 47K into SW1), +48 V switched | none | N/A | No mic stage by decision (CLAUDE.md "Delta clone without mic stage"). |
| Meter-bridge feed CN7 via R142 100R | none | RECORDED | `docs/studies/delta_clone_comparison.md` §2 "Leave out". |
| HPF IC3-A TL072 Sallen-Key: C12 / C13 47n 100V, R27 33K (to output), R26 39K (to ground), R25 47K input bias; gain 1 + R85 4K3 / R84 10K = 1.43 (+3.1 dB); −3 dB ≈ 91 Hz (sim in `docs/studies/delta_clone_comparison.md`; calc 1/(2π·47n·√(33K·39K)) = 94 Hz undamped). Output "−2 dBu", C14 47µF 25V, R28 47K | KHN state-variable HPF U5A + U15 (OPA1612), RV16 A10K dual, R100-R109, C85-C88: 21-403 Hz sweepable, unity, Q 0.707; no coupler after it (HOUT DC-coupled into the EQ) | RECORDED | `docs/proposals/hpf_proposal.md` H1-H4; CLAUDE.md "Sweepable HPF"; decision 3 of `docs/studies/delta_clone_comparison.md` (unity, no +3 dB). Our only coupler ahead of the EQ is C38 / C91 before the HPF; the Delta has C11 before and C14 after it — consequence none (unity inverting EQ stages, mV offsets). |
| HPF switch (ED3151 SW2-A / SW2-B, two poles in parallel): shorts the C12 input node to the C13 output node, i.e. bypasses both capacitors; the IC3-A stage stays in the path with its +3.1 dB. Flexi CN8 pins 13 / 14 | SW11 pole A: HOUT = HP (latched) or HIN (released): true bypass, HPF out of the path | RECORDED | `docs/proposals/hpf_proposal.md` (SW11 selects HP or HIN); `docs/studies/delta_clone_comparison.md` §2 HPF row records the Delta's cap-short bypass. |
| EQ input / EQ switch SW3-A: common (pin 2) = EQ input node (R29); pin 1 = HPF out (via LK1); pin 3 = ground. SW3-B: common (pin 5) = insert source / peak-detect node; pin 4 = EQ out (C22); pin 6 = HPF out. EQ in = 2-1 / 5-4; EQ out = 2-3 / 5-6: the insert gets the HPF out and the **EQ's input is grounded** | SW12 pole A: EQSEL = EQ_O6 (latched) or EQIN (released); pole B drives the LED. The EQ's input stays connected in bypass, its output (EQ_O6) floats | UNRECORDED | Function identical (bypass source = the EQ's own input, works in both insert positions). Detail: the Delta silences the EQ in bypass (its input grounded); ours leaves it running into nothing. No consequence (the bypassed U7A output sits on a PVA2 contact ~mm from EQIN; crosstalk through the switch's open contact only). Document only. |
| EQ LED LD1 green (ED3344A), in the series LED chain (LED CHAIN 1A → LD1 → 1B), shorted by SW3-D (pins 10-11-12) when the EQ is out; the chain is fed by the ~6 mA current source TR8 (ED3344B) | D5 green WP710A10GD, R69 4K7 from +VL through SW12 pole B (≈ 3 mA), own return to GNDD | UNRECORDED | Function same (green, lit with EQ in). Drive scheme differs for every LED (see ED3344B "LED current source"): one 6 mA series chain through all 8 Delta LEDs vs one 4K7 per LED in ours. Consequence: brightness (6 vs 3 mA), none functionally. Document only. |
| HF shelf IC3-B TL072: R29 33K in, R31 33K feedback, C16 33pF 100V across; VR1 (ED3151) 10KB CD gain pot, wiper → C51 4n7 100V → node (R87 5K6 to ground) → C15 4n7 100V → R30 6K8 → virtual earth. Legend "12 kHz" | U5B OPA1612: R50 / R51 33K, C41 33p C0G; RV10 10K B CD; C42 / C43 4n7 C0G, R52 5K6, R53 6K8 | SAME | Op-amp type: RECORDED (OPA1612, decision 4). ±11.5 dB at 12 kHz (sim). |
| HI-MID IC4-A TL072: R33 22K in, R35 22K fb (no cap); + input = Wien band-pass: wiper → C17 3n3 100V → R34 6K8 → VR2-A 100KC (rheostat) → node; VR2-B 100KC + R32 6K8 to ground, C18 1n5 100V node to ground. Legend "600 Hz-10 kHz". VR2 (ED3151) 10KB CD gain | U6A OPA1612: R54 / R55 22K, C69 / C70 10p; + input from the KHN band-pass U12A / U12B / U13A (R81-R89, C44 2n2 / C45 4n7, RV12 A10K dual, 392R / 13K / 4K99): 598 Hz-9.93 kHz | RECORDED | CLAUDE.md "Mid-band tuning" + "Strip v5.5" (EQM1); `docs/proposals/eqmid_proposal.md`; C69 / C70 `docs/reviews/strip_parts_review.md` T1. Boost / cut ±14.6 dB, Q 1.44 as the Delta's Wien (sim). |
| LO-MID IC4-B TL072: R37 22K / R39 22K; Wien: C19 15n 100V, R38 6K8, VR3-A / B 100KC, R36 6K8, C20 6n8 100V. Legend "150 Hz-2.4 kHz". VR3 10KB CD gain | U6B OPA1612: R58 / R59 22K, C71 / C72 10p; KHN U13B / U14A / U14B (R90-R98, C46 10n / C47 22n, RV14 A10K dual, 430R / 13K / 4K22): 165 Hz-2.54 kHz | RECORDED | As HI-MID. |
| LF IC5-A TL072: R40 22K in, R43 22K fb (no cap); + input: wiper → R42 1K5 → C50 2.2µF 50V → node (C21 100n 63V ∥ R41 5K1 to ground). Gain pot (ED3151): R7 3K3 – VR4 10KB CD – R8 3K3 between IC4-B out and IC5-A out, C1 150n 63V across VR4. Legend "60 Hz" | U7A OPA1612: R66 / R67 22K, C73 22p across R67; R64 1K5, C49 2.2µF MKS2 film, C50 100n C0G, R65 5K1; R62 / R63 3K3, RV15 10K B CD, C48 150n MKS2 | SAME | C73: RECORDED (`docs/reviews/strip_parts_review.md` T1). C49 / C48 film: RECORDED (`docs/proposals/film_np_proposal.md` F1). Bell, Q 0.88 at 54 Hz (sim), not a shelf (`docs/studies/delta_clone_comparison.md` §5). |
| EQ output coupler C22 47µF 25V, R44 47K, "−2 dBu" | C51 33µF NP (MUSE ES), R68 47K, 0 dBu | RECORDED | Bipolar value: `docs/proposals/film_np_proposal.md` F2 (CLAUDE.md "Film couplers and audio bipolars"); internal level: decision 3. |
| Pre-EQ aux tap "PRE EQ to aux 1-4 (SHT3)" = the HPF-out node (LK1 side), ahead of SW3 | HOUT (JP2-JP4 position 2-3) | SAME | Same node (HPF out / EQ in). Aux 5-6: see ED3344C. |
| Insert JSK2 TRS: **ring (pin 2) = send** via R143 75R; **tip (pin 1) = return**; the tip's normal contact (4) joins it to the send when empty; sleeve (pin 3) on INPUT GROUND. Manual Part 3 p.124 table: "Insert: Tip = Insert Return, Ring = Insert Send". Links: LK1 / LK4 / LK6 fitted = post-EQ (send from SW3-B's output, return to POST INS); LK2 / LK3 / LK5 = pre-EQ. | J2 NJ6FD-V: **tip = SEND** (R11 75R), **ring = RET_RAW**, ring normal (RN) to SEND; sleeve GNDA. JP5 / JP6 / JP7 solder jumpers: 1-2 post-EQ (default), 2-3 pre-EQ | UNRECORDED | Position and 75R: RECORDED (`docs/studies/delta_clone_comparison.md` §2 Insert). **Tip / ring assignment is reversed** relative to the Delta (ours is the Mackie / Allen & Heath / "modern" convention, the Delta the Soundcraft one). Nothing in the repo records the departure (spec §7 states tip = send without reference). See sign-off item 1. |
| Insert return impedance: C24 47µF 25V → R45 4K7 into IC5-B's virtual earth (ED3344C): ≈ 4.7 kΩ (manual spec for Standard / Deluxe says 10 kΩ) | C10 33µF NP → R12 47K to AGND → R99 1K → U7B follower (C84 100p): ≈ 47 kΩ | UNRECORDED | Ours is 10x higher (easier on insert devices with high output impedance). Topology: the Delta's return buffer IC5-B is a unity **inverter** (R45 / R46 4K7, C25 33pF 100V), ours a follower (R99 / C84 from `docs/reviews/strip_parts_review.md` T8). The Delta re-inverts in IC6-A (mute block), so end-to-end polarity is the same. Document only. |
| Peak detect tap: from the SW3-B common node (post-EQ-switch, **pre-insert-send**, before LK4 / R143) | PRESRC (post insert return) plus RECV, GOUT, EQOUT, FPOST (CS1) | RECORDED | CS1 (`docs/proposals/cs1_proposal.md`); but `docs/studies/delta_clone_comparison.md` §2 "Overload / peak" says the Delta takes it "post-insert": per ED3344A it is pre-insert (the return LK6 → POST INS is a different node). Record correction only; our five taps bracket both points. |
| IC power: IC1-C … IC5-C TL072 pins 8 / 4 on +VA / −VA, no per-IC decoupling drawn on this sheet | 100n X7R 50V per IC on each rail (C20-C36, C63-C68, C89-C93) | SAME | Ours adds local decoupling; the Delta relies on the board reservoirs (C47 / C48, ED3344C) and one "local decouple" C52 at IC12. |
| Flexi CN8 14-way to the LH PCB: 1 LF wiper, 2 IC5A out, 3 IC4B out, 4 LMF wiper, 5 IC4A out, 6 HMF wiper, 7 IC3B out, 8 HF wiper, 9 ground, 10 EQ in, 11 / 12 +48 V, 13 / 14 HPF switch | one PCB: pots and switches on the main board | N/A | Two-board construction detail; recorded in `docs/studies/delta_clone_comparison.md` §5. |

### ED3344B — Theatre input, RH PCB: ON logic, mute control, LED current source, peak detector, logic supply

| Delta | Ours | Status | Note |
|---|---|---|---|
| Logic supply: R71 10R from +17 V → +VM, C35 47µF 25V; R74 10R from −17 V → −VM, C36 47µF 25V; LOGIC GROUND | R3 / R4 10R (fusible M25SI) → +VL / −VL, C5 / C6 47µF 25V, GNDD, NT1 star to GNDA | SAME | Fusible parts: RECORDED (CS6). Values identical. |
| ON switch SW11-A: pin 3 = +VM, pin 2 common → R59 470K → TR6 2SC2240 base (R62 47K to −VM); TR6 collector R63 47K to +VM = ON-bar; TR7 (R64 220K base, R65 100K collector) re-inverts = ON. R66 680K from ON to LED chain / TR11 | SW4 pole A: MSW = −VL (latched, ON) or GNDD (released) directly; pole B lights D4 | UNRECORDED | The Delta derives ±VM logic levels (ON, ON-bar) with two transistor inverters; ours switches the gate RC straight from the key. Consequence none for a single strip (the logic levels would matter for mute groups / remote mute, which the Theatre's RH PCB only provides as "pads for 0.1 in connectors", manual p.56). Document only. |
| Mute control: ON-bar → R51 220K → C28 100n 63V to ground → D7 1N4148 → MUTE (R55 680K to ground) → TR3 gate; ON → R52 220K → C29 100n 63V → D8 1N4148 (R53 + R54 10M + 10M across it) → MUTE-bar (R56 680K) → TR4 gate | R42 220K / C28 100n: one ramp (τ 22 ms) driving both J112 gates (MGATE) | UNRECORDED | Same RC constant (220K / 100n = 22 ms). The Delta has two gate lines with diode shaping and 680K bleeds (asymmetric make / break for its series-shunt pair, below); ours one line for two shunt FETs. Simulated clicks for ours in `docs/proposals/gaps_proposal.md` (keys.py). No audible consequence expected. Document only (see sign-off item 3 with the mute block). |
| LED current source: TR8 2SA970 PNP, R102 100R emitter to +VM, base on 2 × 1N4148 (D26 / D27) biased by R103 27K to −VM, C53 100n 63V; feeds LED CHAIN 1A: LD1 EQ → (LH PCB CN9) LD5 MIX, LD4 "1", LD3 "3" (LD2 / LD1 "5" / "7" not fitted, linked) → LD2 PAN, LD3 "2", LD4 "4", LD7 PFL (ED3344C) → LD9 PEAK, LD8 ON → R148 2K2 to −VM. Calc ≈ (2 × 0.6 − 0.6) / 100R ≈ 6 mA. Unlit LEDs are shorted by a switch pole or a transistor | Each LED: 4K7 from +VL through its key's pole B (or a PNP switch for D2): ≈ 3 mA, returns to GNDD | UNRECORDED | Function same. One constant current through a chain (switch poles short the dark LEDs) vs independent resistors. Consequence: LED brightness 6 vs 3 mA (ours chosen in `docs/reviews/strip_parts_review.md` T2, "~3 mA as the other LEDs"); ours draws current only for lit LEDs. Document only. |
| Peak detector: PEAK DETECT → R92 470K → C30 2.2µF 50V → TR12 2SC2240 base, R88 56K base to −VM, emitter −VM; collector R91 680K to +VM; C32 2.2µF 50V collector to the LED-chain node (hold); TR12 collector drives TR9 2SC2240 which shorts LD9 PEAK red when idle. Threshold calc: Vbe 0.6 V / (56 / 526) ≈ 5.6 V peak ≈ **+14 dBu**, positive half-cycles only, one tap (pre-insert). Manual p.55-56 (Standard input, TR3 / TR4, other values): "approximately +9 dBu internal level", "fast-response, slow-decay" | U4A LM393B comparator against VREF = +VL / 2: +18.4 dBu (9.0 V peak), both polarities (U18A on OL_NN, CS1), five taps, C12 100n attack, U4B hold ≈ 150 ms (R115 1M / C97 220n), Q3 PNP drives the red of D2 (R15 4K7) | RECORDED | `docs/studies/delta_clone_comparison.md` §2 "Keep ours"; `console_survey/delta.md` T18 + §4 item 5 (threshold margin discussed, not changed); CS1 `docs/proposals/cs1_proposal.md`; K3 `docs/proposals/gaps_proposal.md`; MET1. Numbers: Delta ≈ 16 dB above its −2 dBu nominal / ≈ 6 dB below TL072 clip (calc, value ambiguous: the manual's +9 dBu is for the Standard input's different divider); ours 18.4 dB above 0 dBu / 4.6 dB below the OPA1612 swing. Delta decay R91 × C32 ≈ 1.5 s order; ours 150 ms. |
| Signal-present LED | U17 LM393B at −20 dBu, green of D2 (MET1) | RECORDED | `docs/reviews/feature_gaps.md` MET1; the Delta has none. |
| PEAK LED LD9 red, ON LED LD8 green (TR11 2SC2240 shorts it when off, R104 220K from the ON logic) | D2 WP3VEGW red / green bicolour (red = OL, green = signal), D4 green ON | RECORDED | MET1; ON green: decision 5 `docs/studies/delta_clone_comparison.md`. |
| +48 V | none | N/A | Phantom: no mic stage. The sheet title says "+48 V"; the switch itself is on ED3151 (SW1-A / B) and the feed on ED3344A / CN8 11-12. |

### ED3344C — Theatre input, RH PCB: mute block, fader + post-amp, aux, pan, routing, direct out, motherloom

| Delta | Ours | Status | Note |
|---|---|---|---|
| Insert-return buffer IC5-B TL072: POST INS → C24 47µF 25V → R45 4K7 → (−); R46 4K7 feedback, C25 33pF 100V; (+) ground. Unity inverter | U7B OPA1612 follower (R99 1K, C84 100p) after C10 33µF NP / R12 47K | UNRECORDED | Listed under ED3344A "Insert return impedance" (4K7 vs 47K; inverter vs follower). |
| PFL: POST INS (= IC5-B's input node, pre-mute) → C23 47µF 25V → R47 22K → SW10-A pin 2; pin 1 = PFL+ (CN2 pin 27); pin 3 = ground. SW10-C: pin 8 = +VM, pin 7 → R48 100K → PFL DET (CN2 pin 29). SW10-D shorts LD7 PFL red in the LED chain | PRE → C96 2.2µF film → R32 22K → SW3 pole A (PFL bus 27 latched / AGND released); pole B: +VL → R33 100K → PFLDET (29), R34 4K7 → D3 red | SAME | Same tap (pre-mute, post insert), 22K, 100K detect, grounded off position. Coupler: the Delta's C23 is 47µF (0.15 Hz into 22K); ours C96 2.2µF film (3.3 Hz), added as K1 (`docs/proposals/gaps_proposal.md`, RECORDED). PFL on a 4-pole key there, 2-pole here. |
| Mute block: IC5-B out → C26 47µF 25V → R49 4K7 → node A; TR4 J112 **series** from node A into IC6-A's virtual earth (gate = MUTE-bar); TR3 J112 **shunt** from node A to a node held by C30 47µF 25V to ground and R57 22K from IC6-A's output (gate = MUTE); IC6-A TL072 inverter R50 4K7 feedback, C27 33pF 100V, (+) ground; output C31 47µF 25V, R58 47K → fader send / PRE-FADE line | PRE → R16 4K7 → M1 (Q1 MMBFJ112 shunt to AGND) → R17 4K7 → M2 (Q2 shunt, C81 10p) → U3B follower → MUTEOUT; both gates on MGATE (−VL = on, 0 V = muted). ≈ 86 dB (sim) | RECORDED | The topology difference (series + shunt into a virtual earth, 100-110 dB, vs our double shunt, ≈ 86 dB) is recorded in `docs/studies/console_survey.md` §3 Mute row and §5 **CS8** (open, "deeper mute, defer to the jig"; there credited to the Venue Theatre, but ED3344C shows the Delta Theatre is the same). Three other records are wrong and need a one-line fix: `docs/studies/delta_clone_comparison.md` §2 ("Same J112 soft-mute circuit"), `console_survey/delta.md` T7 ("Same J112 pair as ours"), CLAUDE.md ("JFET (J112) soft mute", neutral). Gate drive: see ED3344B. See sign-off item 3. |
| Fader: 3-pin header SEND / GND / RET to a 10K log 100 mm ALPS carbon fader (manual p.56); "pads for 0.1 in connectors for a remote mute or VCA" | RV1 Bourns PTB0143 10K A on the board; J3 / J4 / JP1 VCA module option (SSI2162) | SAME | Fader part: RECORDED (CLAUDE.md "Faders"). VCA option is ours (spec §10). |
| Post-amp IC12-B TL072: wiper → C46 2.2µF 50V → R131 100K to ground → (+); R130 4K7 ∥ C43 100pF 100V feedback, R132 2K2 to ground: +9.9 dB (calc 1 + 4K7 / 2K2); output C44 220µF 6.3V, "−2 dBu"; C52 100n 63V local decoupling | U2A OPA1612: C13 2.2µF MKS2, R18 100K, C82 10p, R19 4K7 ∥ C14 100p, R38 2K2: +9.93 dB; C15 100µF NP, R35 47K | SAME | Couplers: RECORDED (F1 film wiper cap, F2 MUSE ES 100µF; the Delta's C44 is a polar 6.3 V part). C82: `docs/reviews/strip_parts_review.md` T4. |
| Post-fader (unpanned) feed IC6-B TL072 non-inverting: R145 1K8 feedback / R146 10K = 1.18 (+1.4 dB calc; drawing legend "−0.5 dB"), output C56 220µF 25V, R69 47K → POST FADER (PAN switch's off-source) | SW14 released: SUBSRC_L / R = POST directly (0 dB, no buffer) | RECORDED | `docs/proposals/cs2_proposal.md` (PAN off stays POST, 1.7 dB under a hard pan); `console_survey/delta.md` T8; `docs/studies/delta_clone_comparison.md` erratum. The "−0.5 dB" legend is ambiguous (the computed gain is +1.4 dB). |
| Pan VR10-A / B 10KB CD dual: pin 3 / 4 = post-fader, 1 / 6 ground, wipers 2 / 5 → IC11-A / IC11-B TL072 non-inverting ×1.22 (R122 / R123 2K2 feedback, R124 / R125 10K to ground), law resistors R120 / R121 3K3 from each output back to its wiper; outputs C54 / C55 220µF 25V, R67 / R68 47K → POST PAN L / R | RV8 ALPS RK09L 10K B dual CD; U8B / U3A OPA1612 ×1.22 (R137 / R140 2K2 ∥ C105 / C106 22p, R138 / R141 10K), R136 / R139 3K3 back to the wipers; C79 / C80 10p; C16 / C17 100µF NP, R36 / R37 47K | SAME | −2.7 dB centre / +1.7 dB hard (4.4 dB law) since v5.4: RECORDED `docs/proposals/cs2_proposal.md` CS2; pan buffer unit choice PAN1; C105 / C106 stability caps (CS2); pot part (CLAUDE.md "Pan pot RV8"). |
| PAN switch SW5-A (pin 2 → group-L feed: pin 1 POST PAN L, pin 3 POST FADER), SW5-B (pin 5 → group-R feed: pin 4 POST PAN R, pin 6 POST FADER); SW5-D shorts **LD2 PAN red** in the LED chain. MIX L / R are always panned | SW14 pole A / B: SUBSRC_L / R = PANL / PANR (latched) or POST; MIX always panned; **no PAN LED** | UNRECORDED | Switch function: RECORDED (decision 6, `docs/studies/delta_clone_comparison.md`; spec §12). The Delta's PAN LED is not in the record (`docs/studies/delta_clone_comparison.md` §4 counts 7 LEDs; the Delta Theatre has 8). Consequence: PAN state is shown only by the key's latch position. Our PVA2 has no spare pole. See sign-off item 2. |
| Routing: R126 / R127 10K 0.5W (groups 2 / 4, RH PCB) and ED3151 R1 / R2 (MIX L / R from POST PAN L / R), R3 / R4 (groups 1 / 3) 10K 0.5W; R5 / R6 (5 / 7) not fitted. Each key pole moves the resistor's bus end between the bus (CN2 / CN1 flexi) and CLEAN GROUND (SW6-A / C, SW7-A, SW8-A, SW6-B / SW7-B on the RH board); LEDs LD5 / LD4 / LD3 amber shorted by the keys' B poles | R26-R31 4K7 1 % 0805 (0.125 W); DG413 U9-U11 at the bus header move the bus end between the bus and AGND; PVA2 pole A = logic (+5VL / GNDD, R74 / R76 / R78 100K), pole B = D6 / D7 / D8 **yellow** WP710A10YD via 4K7 | RECORDED | 4K7 and DG413: CLAUDE.md "Routing" and "MIX / SUB summing resistors 4K7"; `console_survey/delta.md` T11; `sim/routing_switch.cir`. Two unrecorded details, cosmetic / rating only: the Delta's routing resistors are 0.5 W (ours 0805; worst case 17 V across 4K7 = 61 mW, within rating; see sign-off item 5) and its routing LEDs are amber, ours yellow (sign-off item 6). |
| Aux sends VR4-VR9 10KA (pin 1 = source, 3 = ground, wiper 2) → R133-R138 22K → AUX 1-6 (CN2); aux 1 / 2 source = SW3-B (ED3151), 3 / 4 = SW4-B, 5 / 6 = SW5-B: pin 4 POST FADE, pin 6 PRE; the PRE line for 1 / 2 and 3 / 4 is chosen by push-on links J4 / J5 and J6 / J7 (PRE FADER = IC6-A out after C31, i.e. post-mute / pre-fader; PRE EQ = HPF out); **aux 5 / 6 PRE is pre-fader only** (no link) | RV2-RV7 10K A, R20-R25 22K; SW8 / SW9 / SW10 pole A: PSRCn (latched) or POST; JP2 / JP3 / JP4 solder jumpers for **all three pairs**: MUTEOUT (pre-fader, after the mute) or HOUT (pre-EQ) | UNRECORDED | Pots, 22K, PRE keys, link idea: RECORDED (`docs/studies/delta_clone_comparison.md` §2 Aux; `console_survey/delta.md` T10; design_review Q1 for the post-mute tap, which matches the Delta's PRE FADER = post-mute node). Difference: we give aux 5 / 6 the pre-EQ option too (a superset). No consequence. Document only. |
| DIR: VR9 (aux 6) wiper → SW4-B pin 4 (pin 5 → DIRECT OUTPUT, pin 6 open) and SW4-A pin 3 (pin 2 → R138 22K → AUX 6, pin 1 → ground): latched = wiper to the direct-out amp and R138 grounded | SW13 pole A: A6W → DIRSRC (latched) or A6R → R25 22K → AUX6; pole B grounds A6R when latched | SAME | Decision 7 (`docs/studies/delta_clone_comparison.md`). |
| Direct out IC12-A TL072, ground-compensated: (+) from DIRECT OUTPUT via R115 22K and from the jack **ring** via R116 22K; R113 4K7 feedback / R114 4K7 to ground (gain 2, C42 33pF 100V); output R119 75R → C41 100µF 10V → SKT3 **tip** (R117 22K bleed); ring R118 75R to ground (sense); sleeve INPUT GROUND. Net signal gain 1 (0 dB), "−2 dBu". Manual p.124 table: direct out ring + sleeve = ground / screen (Deluxe) | U8A OPA1612 follower (R70 100K, C83 22p) → R71 75R → C52 33µF NP → J5 tip (R72 47K); ring R73 75R to GNDA (impedance-balanced); sleeve CHASSIS | RECORDED | `console_survey/delta.md` T16 ("equivalent"); couplers F2; sleeve G2. Level 0 dBu with the pot at top (spec §11). |
| Motherloom CN2 34-way: 34 = +48 V, 32 / 33 = +17 V, 30 / 31 = −17 V, 29 PFL DET, 27 PFL+, 26 GND CANCEL (R141 10R to ground), 25 / 24 AUX 2 / 1, 20-23 AUX 6-3, 18 / 17 L / R, 15 / 13 / 11 / 9 GROUP 1-4, odd 1-7 groups 5-8 (not fitted), even 2-16 ground, 19 / 28 spare; ground row to CN4 1/4" spade through link positions Z1 / Z2 / Z20 | CN1 identical pinout; pin 34 = +V (third conductor), pins 1 / 3 / 5 / 7 reserved for SUB 5-8, 19 / 28 NC; R5 10R GCANCEL; CN4 6.3 mm spade | RECORDED | CLAUDE.md "Bus = real Delta motherloom pinout" (incl. the 17 / 18 L-R order note), W1 (pin 34), `docs/studies/eight_groups_study.md`. Z1 / Z2 / Z20: three link positions in the strip's ground run to the spade (read as wire / zero-ohm links; purpose not stated) — nothing equivalent in ours. |
| Board power: +17 V → R139 10R → +VA, C47 220µF 25V; −17 V → R140 10R → −VA, C48 220µF 25V; IC6-C / IC11-C / IC12-C supply pins | R1 / R2 10R fusible, C1 / C3 220µF 25V, C2 / C4 100n, D16 / D17 PMEG4010CEH reverse clamps | SAME | Fusibles CS6 and clamps CS10: RECORDED (ours adds them). |
| Jack-line protection | D18-D22 BAV199 clamps at CN3 (CS4) | RECORDED | `docs/proposals/cs4_proposal.md`; the Delta has none on the line / insert / direct jacks (its mic stage has D3-D6). |
| Brackets BKT4-BKT10 | M3 standoffs H1-H6 | N/A | Mechanical. |

### ED3151 — LH PCB (Venue II & Delta Theatre input): pots, switches, LEDs

| Delta | Ours | Status | Note |
|---|---|---|---|
| +48 V switch SW1-A / B, +48 V to mic input via CN3 | none | N/A | No mic stage. |
| HPF switch SW2-A / SW2-B (both poles short CN3 pins 13-14: the capacitor bypass) | SW11 (HP / HIN select) | RECORDED | See ED3344A HPF switch row. |
| EQ gain pots VR1-VR4 10KB CD (centre detent), CW = boost on all four (VR1 drawn with pins 1-3 reversed and the CW arrow pointing left); LF: R7 3K3 – VR4 – R8 3K3, C1 150n 63V across VR4; brackets BKT1-BKT4 | RV10 / RV11 / RV13 / RV15 Alpha RD901F B10K centre detent, R62 / R63 3K3, C48 150n film; CW = boost | SAME | Pot part choice is ours (spec §16.1). |
| Aux source keys SW3-B / SW4-B / SW5-B (PRE 1-2, 3-4, 5-6): pin 5 → the pair's pots, 4 = POST FADE, 6 = pre line (1 / 2 and 3 / 4 via links J4-J7 on the RH PCB; 5 / 6 fixed PRE FADE) | SW8 / SW9 / SW10 pole A; JP2-JP4 for every pair | UNRECORDED | See ED3344C aux row (aux 5 / 6 pre-EQ option is ours only). |
| Routing keys SW6 (MIX: poles A + C audio, B LED), SW7 ("1" / "2": A on LH, B LED, the other pole on the RH), SW8 ("3" / "4"), SW9 / SW10 ("5" / "7", not fitted, LK2 fitted); off position = CLEAN GROUND; CN1 8-way flexi carries MIX L / R and groups to the RH PCB | SW5 / SW6 / SW7 PVA2 logic + DG413 | RECORDED | CLAUDE.md "Routing" (the PVA2 carries logic only; the 4PDT idea replaced). |
| Routing LEDs LD5 MIX, LD4 "1", LD3 "3" amber, in the LED chain, shorted by SW6-B / SW7-B / SW8-B; chain from the EQ LED (RH) and on to the PAN LED (RH) | D6 / D7 / D8 yellow, 4K7 each from +VL via pole B | UNRECORDED | Colour (amber vs yellow) and drive (chain vs resistors). Cosmetic. Sign-off item 6. |
| Notes box: "Components in dotted area not fitted for Delta. LD1 & LD2 linked on Delta. N.B. LK2 is fitted in dotted area" | pins 1 / 3 / 5 / 7 reserved for SUB 5-8, no parts | RECORDED | `docs/studies/eight_groups_study.md`; CLAUDE.md Bus decision (pins reserved). |

### Cross-sheet items

| Delta | Ours | Status | Note |
|---|---|---|---|
| Op-amps TL072 throughout (IC2-IC6, IC11, IC12); discrete 2SC2240 / 2SA970 logic and LED drive | OPA1612 (U1-U3, U5-U8, U12-U15), OPA1656 (U16), LM393B (U4, U17, U18), MMBT3906 (Q3-Q5), DG413 | RECORDED | Decision 4 `docs/studies/delta_clone_comparison.md`; CLAUDE.md "OPA1612 in noise-critical stages"; G3 (OPA1656). |
| Coupling capacitors: polar electrolytics 47µF 25V (C11, C14, C22, C23, C24, C26, C31), 220µF 25V (C54-C56), 220µF 6.3V (C44), 100µF 10V (C41), 2.2µF 50V (C46, C50) | MUSE ES bipolar 33µF / 100µF, WIMA MKS2 2.2µF / 150n film, all 25 V or more | RECORDED | `docs/proposals/film_np_proposal.md` F1-F4; CLAUDE.md "Film couplers and audio bipolars". |
| Stability caps: C45 12pF (line stage), C16 33pF (HF), C25 / C27 33pF (IC5-B / IC6-A), C43 100pF (post-amp), C42 33pF (direct out); none on the mid / LF stages or the pan buffers | 33p (C7 / C78, C41), 10p / 22p across the 22K EQ feedbacks and KHN summers, 100p (C14, C84), 22p (C37, C83, C105 / C106, C85, C73), 10p on followers' + inputs | RECORDED | `docs/reviews/strip_parts_review.md` T1-T8, `docs/proposals/hpf_proposal.md`, `docs/proposals/cs2_proposal.md` (TI OPA161x needs them; the TL072's lower GBW did not). |
| Internal level −2 dBu (−5 dBu after the line stage, +3.1 dB HPF) | 0 dBu throughout, HPF unity | RECORDED | Decision 3 `docs/studies/delta_clone_comparison.md`. |
| Switch hardware: multi-pole keys (SW3 4-pole EQ, SW5 4-pole PAN, SW10 4-pole PFL, SW6 / SW7 3-pole routing) | C&K PVA2 DPDT everywhere, DG413 and PNP switches take the extra poles | RECORDED | CLAUDE.md "Routing" (no vertical 4PDT exists); MET1 (LED switches). The PAN LED is the one function that fell out of this (sign-off item 2). |

---

### UNRECORDED discrepancies for sign-off

1. **Insert jack tip / ring convention.** Delta (ED3344A JSK2; manual Part 3 p.124 table): **tip = return, ring = send**,
   tip normalled to the send. Ours (gen.py J2, spec §7, 16.4): **tip = send, ring = return**, ring normalled to the send.
   Consequence: an insert cable (or a patchbay) wired for a Soundcraft console works the wrong way round on ours and vice
   versa; a plain TRS-to-dual-TS "Y" lead with the common tip = send convention (Mackie, A&H, Behringer, most patchbays)
   works on ours as labelled. No electrical risk either way (both ends are 75R / 47K-terminated line level).
   Recommendation: **keep ours, document** the convention on the panel legend / spec §7 (and in `docs/studies/delta_clone_comparison.md`
   §2 Insert row) as a deliberate departure from the Delta.
2. **PAN LED.** Delta: LD2 red "PAN" on ED3344C, shorted by SW5-D when PAN is off (the 8th LED of the strip). Ours: none
   (SW14's two poles both carry audio). Consequence: PAN on / off is visible only from the key's latched height; a
   sub-group fed unpanned by mistake is not flagged. Recommendation: **keep ours, document** (adding it needs a 4-pole key
   or a spare DG413 / comparator; the key's mechanical latch is the Delta's own ON-state cue for the PRE and DIR keys too).
3. **Soft-mute: record correction + gate drive.** Delta: TR4 J112 **series** into IC6-A's virtual earth plus TR3 J112
   **shunt** (source held by C30 47µF / R57 22K), gates on two lines (MUTE / MUTE-bar) from a TR6 / TR7 inverter pair
   through 220K / 100n, 1N4148 and 680K bleeds; the insert-return buffer IC5-B and IC6-A are both inverters. Ours: two
   **shunt** J112s in a 4K7 / 4K7 ladder into a follower, one 220K / 100n ramp straight from the key. The topology gap is
   already recorded as `docs/studies/console_survey.md` CS8 (open, deferred to the jig: ≈ 86 dB vs 100-110 dB), so the only
   unrecorded parts are (a) the gate-drive scheme and (b) the wrong "same J112 soft-mute circuit" wording in
   `docs/studies/delta_clone_comparison.md` §2 and `console_survey/delta.md` T7. Consequence: none beyond CS8's. Recommendation:
   **document only** (reword the two statements; CS8 stays the decision point).
4. **Insert-return input impedance / buffer.** Delta: C24 47µF → R45 4K7 into IC5-B's virtual earth (≈ 4.7 kΩ; the
   manual's spec sheet says 10 kΩ). Ours: 47K (R12) + 1K into a follower (≈ 47 kΩ). Consequence: ours loads an insert
   device 10x less; LF corner of our return 0.1 Hz. Recommendation: **keep ours, document**.
5. **Routing resistor rating.** Delta: 10K **0.5 W** (R126 / R127, ED3151 R1-R4). Ours: 4K7 1 % 0805 (0.125 W). Worst case
   a bus shorted to a 17 V rail puts 61 mW in a 4K7; normal signal < 15 mW. The Delta's 0.5 W is most likely a low-noise
   metal-film choice rather than a dissipation need. Recommendation: **keep ours** (if wanted, Yageo RC0805 → a 0.25 W
   1206 costs nothing in placement terms); document only.
6. **LED colours and drive.** Delta: routing LEDs **amber** (LD3-LD5 / LD2-LD4), PAN red, EQ green, PFL red, PEAK red, ON
   green, all in one ≈ 6 mA series chain from a 2SA970 current source (TR8), unlit ones shorted by switch poles /
   transistors. Ours: routing **yellow** WP710A10YD, 4K7 from +VL per LED (≈ 3 mA), lit LEDs only draw current.
   Consequence: cosmetic (yellow vs amber, half the current / brightness). Recommendation: **keep ours**; if amber is
   wanted, swap to Kingbright WP710A10SEC/J (amber) in `gen.py` LED_MPN; document.
7. **Aux 5 / 6 pre-EQ option.** Delta: push-on links J4 / J5 (aux 1-2) and J6 / J7 (aux 3-4) choose pre-fader or pre-EQ;
   aux 5 / 6 PRE is pre-fader only (ED3151 SW5-B pin 6 = PRE FADE). Ours: JP2 / JP3 / JP4 give all three pairs the choice.
   Consequence: none (a superset). Recommendation: **keep ours, document**.
8. **EQ bypass grounds the EQ input (Delta) vs leaves the EQ running (ours).** Delta SW3-A 2-3 grounds the R29 node when the
   EQ is out; ours (SW12) only selects the source. Consequence: none measurable (the only path from the idle EQ to the
   signal is the PVA2's open contact). Recommendation: **keep ours, document**.
9. **Peak-detect tap point record.** Delta's PEAK DETECT is taken at the SW3-B output (post-EQ-switch, pre-insert send),
   not "post-insert" as `docs/studies/delta_clone_comparison.md` §2 says. Ours (CS1) taps PRESRC (post return) and four other points,
   so both positions are covered. Recommendation: **document only** (fix the row in `docs/studies/delta_clone_comparison.md`).
10. **Peak threshold and hold (numbers, already discussed, recorded as "keep ours").** Delta Theatre ≈ +14 dBu by my
    calculation (R92 470K / R88 56K, Vbe 0.6 V; positive peaks only; the manual's "+9 dBu" is the Standard input), decay
    R91 680K × C32 2.2µF ≈ 1.5 s order; ours +18.4 dBu both polarities, 150 ms hold. `console_survey/delta.md` §4 item 5
    already raised the margin; CS1 added taps but kept the threshold. Recommendation: **keep ours** (no new facts); if the
    bench shows red too late on EQ boosts, +15 dBu is a one-resistor change (R40 / R41).
11. **Delta ON logic levels.** TR6 / TR7 give ±VM "ON / ON-bar" lines (also used for the ON LED switch TR11 via R66 680K /
    R104 220K); ours drives the gate RC from the key directly. Consequence: none on the strip as built; only relevant if a
    remote / group mute were ever added (the Theatre's own provision is pads only). Recommendation: **keep ours, document**.
12. **Second coupler after the HPF.** Delta: C14 47µF between the HPF and the EQ (and C11 before the HPF). Ours: C38 / C91
    before the HPF, DC-coupled HPF → EQ. Consequence: the KHN summer's few mV of offset reach the EQ's unity inverting
    stages and the insert send through C51 / R11 — nothing audible or measurable. Recommendation: **keep ours, document**.

Items not read / not resolvable at 300 dpi: the purpose of CN5 (two pins on SKT1's normal contacts, ED3344A) and of the
link positions Z1 / Z2 / Z20 in the ground run to the spade (ED3344C); the "−0.5 dB" legend on IC6-B (computed +1.4 dB).
Everything else on the four sheets was read, including the notes boxes (ED3151's is the only one with text).


---

## Part B: Group output ED2778A / B + LH (aux) master ED2779A / B vs the group module and the master aux 5 / 6

Cross-check 2026-10-28. Sources read: `ref/Sndcft_DeltaDLX_Schems.pdf` PDF p.6-9 rendered at 300 dpi (crops not in the repo), 200 Delta Technical Manual Part 2 printed p.61-65 (Group Output Module, LH (Auxiliary) Master Module,
RH (Mix) Master Module), `docs/console_survey/delta.md`, `master_section_spec.md` §2-§5, §12-§16, §22, CLAUDE.md
Decisions. Ours: `tools/gen_group.py` + `tools/master_lib.py` (netlist `group.net` 291 parts, `group_jack_board.net`),
`tools/gen_master.py` aux 5/6 block (`master.net`). All Delta refs and values are as read from the sheets; where a
value has an asterisk the sheet's note box gives the Delta 8 alternative.

**Sheet identities (differs from the brief).** ED2778A sht 1 of 2 "DELTA & DELTA 8 GROUP OUTPUT" carries the whole
group audio path including the GROUP ASSIGN links J1-J8 (J5-J8 "DELTA 8 ONLY" boxed) and the motherloom CN1.
**ED2778B sht 2 of 2 is the group's 20-LED meter** (rectifier IC2-A, LM2901 ladder, current sources), not a bus-select
ladder. ED2779A is the LH master (six aux masters, AFL, loom, power); **ED2779B is the LH master's Mix L meter**.
Levels: Delta sheets write the Delta level first and the Delta 8 level in brackets (group summer −7.8 dBu, (−2 dBu)).

Status key: SAME / RECORDED (where) / UNRECORDED / N/A / UNREAD.

---

### 1. ED2778A — group output, group audio path

| Delta (sheet, refs, value / topology as read) | Ours (refs, value / topology) | Status | Note |
|---|---|---|---|
| **Bus input, group assign:** GRP 1-4 from loom pins 15/13/11/9 through wire links J1-J4 to one summing node; J5-J8 (GRP 5-8, pins 7/5/3/1) "DELTA 8 ONLY". One link closed per module. | JP1-JP4 solder jumpers (`SolderJumper-2_P1.3mm_Open`) SUB1-4 → SUB_SEL; JP5-JP8 AUX1-4 → AUX_SEL; "close ONE SUB jumper and ONE AUX jumper". | RECORDED (spec §12 Bus select, MG19; CLAUDE.md M1 modules) | Same scheme (link per bus). Our board also selects its aux bus, the Delta's LH master sums all six auxes. J5-J8: N/A (pins 1/3/5/7 reserved, CLAUDE.md bus decision). |
| **Summer DC block:** C13 1000 µF 63 V in series with the bus into TR1's emitter; C28 220 µF 25 V (Delta 8 only) on the bias node. | None: FB1 ferrite straight into U1B's − input. | RECORDED (spec §2 "No DC-blocking capacitor at the bus input") | Our feeds are AC-coupled at the strips (100 µF NP + 47K). |
| **Group summing amp:** discrete differential: TR1/TR2 2SB737 common base, bases to local ground (both), emitter feeds R46/R48 22K from +17 V via R44 220R + C15 220 µF 25 V, collector loads R47/R49 10K, R45 820R to −17 V, C14 100 pF across the collectors, IC5-B NE5532 differential stage; feedback IC5-A NE5532 unity inverter (R51/R52 4K7) and R50 3K9* back into TR1's emitter (* Delta 8: 8K2); C16 220 pF* output → TR2 emitter (* Delta 8: 100 pF). Non-inverting overall. | U1B OPA1612 inverting summer, FB1 220R@100MHz bead, R6 4K7 1 % ∥ C7 100p C0G, + input on GCANCEL (raw line); U2A OPA1612 re-inverter R7-R10 2K2 0.1 % (ERA-6AEB222V) with C8/C9 22p C0G 5 %, + leg from GC_BUF (U1A follower on GCANCEL). | RECORDED (delta.md T12, T13; spec §2, §3, §12; CLAUDE.md "ground cancel") | Gain: Delta 3K9/10K = −8.2 dB (Delta 8: 8K2/10K = −1.7 dB); ours 4K7/4K7 = unity (4K7 bus decision). The Delta's group summer takes **no** ground cancel (both bases on module ground); ours does. |
| **Op-amp types in the group path:** NE5532 (IC5, IC6, IC4), TL072 (IC1, IC2, IC3). | OPA1612 everywhere in the sub / aux / return paths (U1-U3, U5, U6, U8, U9, U12, U13), OPA1656 followers (U10, U11, U14, U15), DRV135 (U4, U7). | RECORDED (delta.md T20; CLAUDE.md OPA1612 decision; G3b) | — |
| **Insert send:** IC5-B output → C35 47 µF 25 V → R112 220R → JSK1 pin 5 (SEND); return pin 4 normalled to send (pin 1 / 2 / 3 ring normalling as drawn), socket ground. Level −7.8 dBu. | R11 75R (ERJ-P06J750V) from S_MIX → SUB_SEND → J1 tip (RN = send), ring = SUB_RETRAW; level ≈ 0 dBu. | RECORDED for the level (delta.md T6, spec §4 "Ours stays at console level"); **UNRECORDED** for the build-out value (Delta group 220R, ours 75R) | Our 75R is "as the strip insert"; the Delta's mix insert is 75R (ED2780), its group insert 220R. Consequence: none (75R + the outboard's input). Document only. |
| **Insert return → fader:** JSK1 return → C17 47 µF 25 V → fader top directly (no buffer). | SUB_RETRAW → C12 33 µF NP (MUSE ES) + R12 47K → R13 1K + C13 100p → U2B OPA1612 follower → R14 75R → C14 100 µF NP + R15 47K → S_PRE → RV1 top. | RECORDED (spec §4, `docs/reviews/master_group_review.md` MG7; spec §12 "return buffer") | Ours adds a buffer so the fader / insert never load the re-inverter; 1K bounds the current from outboard into an unpowered console. |
| **Group fader:** "GP FADER, 0 dB AT TOP (+10 dB AT TOP)" (Delta 8); R53 100K + C18 2.2 µF 50 V from the wiper. | RV1 Bourns PTB0143-2010BPA103 A10K, pin 1 GNDA; C15 2.2 µF film (WIMA MKS2) + R16 100K; C18 10p C0G at U3A's + input. | RECORDED (spec §5 / §12 "unity ... at its '0' mark"; CLAUDE.md faders) | Delta: unity at the fader top; ours: unity at the "0" mark, +9.9 dB in hand (the Delta 8 configuration). |
| **Post-fader amp:** IC6-B NE5532 non-inverting, R56 2K4* / R54 2K → +6.8 dB (* Delta 8: 4K7 / 2K2 → +9.9 dB); C19 220 µF 6.3 V out. | U3A OPA1612, R18 4K7 / R19 2K2 → +9.9 dB, C19 100p across R18, R17 47R build-out at the pin, C20 100 µF NP + R20 47K → S_POST. | RECORDED (spec §5 / §12; MG4) | Our values are exactly the Delta 8's. |
| **Output level switch:** S1-B selects +4 dBu or −10 dBV (pad R82 2K4 / R91 910R, −11.2 dB); other poles (S1-A, S1-C, S1-D) change the tape-return input gains. Manual p.61. | None. All outputs one level (0 dBu internal, DRV135 +6 dB). | RECORDED (console_survey/delta.md T21 levels; `docs/studies/delta_clone_comparison.md` "−10 dBV source reaches 0 dBu" via gain) | No −10 dBV option anywhere in ours; the strip gain pot covers consumer sources. |
| **Group output amp:** IC6-A NE5532 "GND-CANCEL OUTPUT AMP": + input via R57 2K2 (signal) and R61 4K3 (ring = far ground), − input R58 2K2 to ground, R60 4K3 ∥ C20 100 pF feedback → signal gain (4.3/6.5)(1 + 4.3/2.2) = 1.954 = +5.8 dB, ring gain 1.000; R62 75R + C21 220 µF 25 V to CN2 pin 1 (tip, "GRP OUT" also to the 20-way loom); ring = CN3 pin 2 through R63 75R to socket ground. Unbalanced, +4 dBu, +21 dBu max. | U4 DRV135UA: in S_POST, R119/R120 22R (CS4c) → C21/C22 10 µF NP (matched pair, CS11b) → S_OP / S_ON → J2 tip / ring, sleeve CHASSIS (G2b); D9/D10 BAV199 clamps (CS4b); C23/C24 1 µF decoupling. Balanced, +6 dB differential, no mute relay on subs. | RECORDED (CLAUDE.md DRV134 family / DRV135UA, G2b, CS4b, CS4c, CS11b; spec §12 "No mute relay on the sub outputs"; delta.md T17) | — |
| **Monitor pan (sub into MIX):** passive: VR10-A/B 10K LIN CD (dual), tops on the switched signal (S5-B SUB), R38 / R39 3K9 from the signal to each wiper, wipers through R40 / R41 8K2 to MIX R / MIX L. | RV2 ALPS RK09L1240015 B10K dual detent; C25/C26 10p; U3B / U5A OPA1612 at 1.22× (R124/R127 2K2 ∥ C96/C97 22p, R125/R128 10K) with R123/R126 3K3 from each output back to its wiper; C29/C30 100 µF NP + R21/R22 47K; SW1 "Sub to MIX" (PVA2), R23/R24 4K7 1 % to MIXL / MIXR, released = resistor end to GNDA. | RECORDED (`docs/proposals/cs2b_proposal.md` CS2b, spec §12 "Pan law", CLAUDE.md "Group sub pan law") | Computed from the sheet: wiper at centre 0.586 V into 8K2 → −2.9 dB relative to a 10K strip feed, hard over +1.7 dB (10K / 8K2): a 4.6 dB law. Ours −2.7 / +1.7 dB (4.4 dB). The Delta has no MIX on/off for the group pan (the pan is always on the mix when SUB is up); ours has SW1. |
| **SUB / RET switching and the lower tape return as the group's monitor path:** S5-A/B "SUB", S4-A/B "RET"; with SUB and RET up the group signal goes through return B's 2-band EQ, VOLUME, ON and the pan to the mix; SUB down: group post-amp straight to the pan; RET down: the tape return takes that path; SUB + RET down: the tape return is summed onto the group bus through R43 8K2 (manual p.61-62). LK20 / LK10B / R42 75R / C27 47 µF "EFFECT RETURN TO GROUP", CN7 "MTR". | No SUB / RET modes: POST_SUB always feeds the pan buffers and the AFL; the returns have their own MIX / 1-2 / 3-4 keys (4K7 onto SUB1-4 / MIX). | RECORDED (spec §12 AFL bullet "Delta D203's PFL key belongs to the lower return ... goes dead in SUB mode"; spec §16) | N/A as a mode set; the return-to-sub routing exists in ours (any return to subs 1-2 / 3-4). |
| **Group AFL / PFL:** none of its own; return B's PFL key (S6-B, R32 22K from the post-EQ node → PFL+) acts as the group AFL only in SUB-up / RET-up. | SW2 "Sub AFL" PVA2: pole A R25 22K from S_POST → PFL (pin 27), released → GNDA; pole B +VL → R26 100K → PFLDET, R27 4K7 → D1 red → GNDD. | RECORDED (spec §12 AFL bullets; `docs/reviews/master_parts_review.md`) | Level: Delta AFL at −2 dBu internal through 22K; ours 0 dBu through 22K (−0.43 dB vs a strip PFL, spec §12). |
| **Op-amp power:** R64 / R65 10R, C25 / C26 220 µF 25 V, C36 / C37 100n 63 V; IC1-C, IC3-C TL072 and IC4-C, IC5-C, IC6-C NE5532 on the same rails. +48 V unused (pin 34 "+"). | R1 / R2 10R Vishay M251206BB1009JP500 fusible 1206 + C1 / C2 220 µF 25 V (±VA); R3 / R4 10R + C3 / C4 47 µF (±VL, GNDD via NT1); 100n at every package (C5/C6, C10/C11, ...); D5 / D6 PMEG4010CEH reverse clamps on ±VA; pin 34 = third +V (W1). | RECORDED (CLAUDE.md CS6, CS10, W1; spec header "Groups have strip-style power") | — |
| **Ground spade / module ground:** "MAIN GROUND" at the tape return A jack: R100 10R between PANEL (socket ground) and MAIN GROUND; module ground returns through the loom's even pins. | CN1 Keystone 1287-ST 6.3 mm spade on GNDA (G1 harness); NT1 GNDA-GNDD star; jack sleeves on CHASSIS bonded by H1 / H2 on the jack board (G2b). | RECORDED (CLAUDE.md G1, G2b; `docs/studies/ground_study.md`) | The Delta's panel-to-audio-ground 10R (R100) has no equivalent in ours: our panel is bonded to CHASSIS, GNDA meets it only at the master's star. |
| **Ground-cancel resistor:** R66 75R* "GROUND CANCELLING RESISTOR" from pin 26 to ground, "* CN6 / R66 not fitted" on the Delta 8; manual p.63: 10 Ω on every module but the LH master. | R5 10R GND cancel GNDA → GCANCEL (pin 26); the group also reads GCANCEL raw at U1B / U6A (+ inputs) and buffered (U1A → GC_BUF) for its two re-inverters. | RECORDED (delta.md T13 "unresolved" 75R vs 10R; spec §3; CLAUDE.md ground cancel) | — |
| **Motherloom CN1 (as read):** 18 MIX L, 17 MIX R, 15/13/11/9 GRP 1-4, 7/5/3/1 GRP 5-8, 24 AUX 1 (return sends), 26 GND CANCEL, 27 PFL+, 29 PFLDET, 16 and even 2-14 ground, 33+32 +17 V, 31+30 −17 V, 34 +48 V ("+" only), 28 / 19 / 20-23 / 25 unconnected on this module. | CN2 2×17: 18 MIXL, 17 MIXR, 15/13/11/9 SUB1-4, 22-25 AUX4/3/1/2 (jumpered), 26 GCANCEL, 27 PFL, 29 PFLDET, even 2-16 GNDA, 30/31 −VBUS, 32/33/34 +VBUS; 1/3/5/7/19/20/21/28 NC. | SAME (bus pinout decision, CLAUDE.md) / RECORDED (W1 for 34) | Group pin 28 is open on the Delta group too (read at 5×). |
| **Meter / overbridge:** CN10 "TO METER OVERBRIDGE, DELTA 8 ONLY" through R118 100R; MTR feed to ED2778B; "GRP OUT" on the 20-way output loom. | No meter on the group; no 20-way loom (outputs on the jack board link CN3 / CN4). | RECORDED (`docs/studies/master_panel_study.md` M1: "room for an optional 20-LED sub meter, as on Delta group modules"; spec §22 meters on the master only) | N/A for the circuit. |
| **Group output / tape jacks on a separate rear PCB** ("GROUP OUTPUT METHODE" CN2 / CN3, "TAPE RETURN 1 METHODE" CN4 / CN5, "FROM M/T TAPE 1 / 9" CN8 / CN9). | Jack board `group_jack_board`: J1 insert, J2 sub out, J3 aux out, J4-J7 returns, CN1 2×8 + CN2 2×5 IDC links, H1 / H2 CHASSIS. | RECORDED (spec header "Jack boards", RET1) | Same idea (connectors off the main PCB). |

#### 1b. ED2778A — the two tape returns vs our two stereo returns (spec §16)

| Delta (sheet, refs, value / topology as read) | Ours (refs, value / topology) | Status | Note |
|---|---|---|---|
| **Inputs:** two mono TRS jacks JSK3 / JSK2 per group ("TAPE RETURN A / B"), also fed from the rear tape connectors CN8 / CN9. | Two stereo returns per group: J4 / J5 (return 1 L / R), J6 / J7 (return 2 L / R); R normalled to L (J5.TN / RN to J4's tip / ring); L's normals short an empty input to GNDA. | RECORDED (spec §16; `docs/reviews/feature_gaps.md` RET1; CLAUDE.md "8 stereo returns") | — |
| **Receiver:** IC1-A TL072 balanced: R1 / R2 43K, R3 22K, R4 20K feedback, C1 / C2 33 pF 100 V; S1-C adds R6 2K2 / R5 6K8 for −10 dBV; output "−2 dBu". | Per leg R39 / R44 1M, R70 / R71 220R, C44 / C45 100p, U10A / U10B OPA1656 followers, R72 / R73 100R; U8A OPA1612 bridge R40-R43 10K 0.1 % with C46 / C47 33p (return 1 L; U8B / R45-R48 / C52-C53 R; U12 + U14 / U15 for return 2); unity. | RECORDED (delta.md T1; CLAUDE.md G3b; spec §16) | — |
| **2-band EQ:** IC2-B TL072, R7 / R10 22K, HF shelf VR1 10K LIN CD + C4 6n8 100 V + R9 4K7, LF shelf VR2 10K LIN CD + R8 7K5, R93 5K1, C3 100n 63 V, C5 33 pF. | None. | **UNRECORDED** | Spec §16 lists receiver, level, buffers, routing, PFL; nothing says the Delta's return EQ was dropped. Consequence: a reverb return can't be shelved on the console (use the strip EQ on a strip, or the effect's own). Recommendation: document only (keep; a panel row is not free). |
| **AUX 1 send from each return:** VR3 20K LOG → R13 22K → AUX 1 (pin 24) (return A; R32 22K / VR8 20K for return B). | None: the group's CN2 pins 22-25 carry only the jumpered aux bus. | **UNRECORDED** | Consequence: a return can't be sent to an aux (e.g. a reverb return into a delay send). Recommendation: document only (keep; our returns are stereo and would need two pots or a mono sum). |
| **Return level:** VR4 10K LOG "VOLUME" after the EQ. | RV4 / RV5 Alpha RD902F A10K dual, pin 1 GNDA, after C54 / C55 33 µF NP + R49 / R50 47K. | RECORDED (spec §16) | — |
| **Post-level amp:** IC4-A NE5532 non-inverting R16 4K7 / R15 2K2 (+9.9 dB), R14 47K, C6 2.2 µF 50 V; C38 47 µF 25 V out. | U9A / U9B OPA1612 `level_buffer()`: C56 / C62 2.2 µF film + R51 / R55 100K, C60 / C64 10p, R52 / R56 4K7 ∥ C59 / C63 100p, R53 / R57 DNF ("2K2 = +10 dB"); C61 / C65 100 µF NP + R54 / R58 47K. | RECORDED (spec §16 "Rg not fitted = unity, fit 2K2 for +10 dB") | The Delta runs the return +10 dB hot after its volume pot (its internal −2 dBu); ours unity at console level, the 2K2 option gives the Delta's gain. |
| **ON switch and green LED:** S3-B mutes after the post-amp; LD14 / LD16 green from +17 V through S3-C / S7-C, shared R67 4K7 to −17 V (≈6.8 mA for one lit). | None (no mute on the returns). | RECORDED (spec §16 "No balance or mute") | — |
| **Return pan to MIX:** R17 / R18 3K9, VR5 10K LIN CD dual, R19 / R20 8K2 → MIX R / MIX L (same passive law as the monitor pan, 4.6 dB). | No pan: L → MIX L / SUB1 / SUB3, R → MIX R / SUB2 / SUB4 through R59-R64 4K7 1 % (return 1), R99-R104 (return 2); SW4-SW6 / SW8-SW10 PVA2, released → GNDA. | RECORDED (spec §16 "No balance ... Add a balance pot later if wanted") | — |
| **Return PFL:** S2-B / S6-B: R11 / R32 22K from the post-EQ, pre-volume node → PFL+; released → ground. LD13 / LD15 red from +17 V through S2-C / S6-C, with R12 / R33 100K to PFLDET. | SW7 / SW11: R65 / R66 (R105 / R106) 43K from RT_PREL / PRER (pre-level) to RT_PFLJ → PFL; released → GNDA; pole B +VL → R67 / R107 100K → PFLDET, R68 / R108 4K7 → D3 / D4 red. | RECORDED (spec §16 PFL, +0.2 dB for a centred mono source) | Delta PFL LED return path not resolved at 300 dpi (UNREAD detail); ours ≈3.2 mA from +VL (17 V) via 4K7, "~3 mA, as the other LEDs" (gen.py, `docs/reviews/strip_parts_review.md` T: R15 4K7). |
| **Return summed onto its own group bus** (SUB + RET down) through R43 8K2. | Returns route to SUB1-4 through 4K7 like a strip (any group's return to any sub pair). | RECORDED (spec §16 routing) | — |

---

### 2. ED2778B — group meter (sht 2 of 2)

Our groups carry no meter, so every row is N/A for the group. Values are given because the Delta meter is the model for
our master's main meters (`master_section_spec.md` §22, delta.md T18); our master refs in brackets for reference only.

| Delta (sheet, refs, value / topology as read) | Ours (group) | Status | Note |
|---|---|---|---|
| Source: "MTR" (group signal, or the tape return when RET is pressed, manual p.62) → PR1 22K cal preset → R70 4K7 → IC2-A TL072 precision half-wave rectifier (D1 / D2 / D5 1N4148, R71 22K feedback). | No group meter. (Master: TL072HIDR detector, 10K / 4K7, 22K trim, §22.) | N/A (RECORDED that the architecture is copied: delta.md T18) | — |
| Ballistics: average R111 33K + C33 2.2 µF 50 V; peak R72 75R + C30 10 µF 25 V with R73 33K / R110 22K discharge and C34 1n 100 V; J13 AVERAGE / PEAK link; all to METER GROUND. | — (Master: precision peak detector, 220R into 1 µF, §22: "the Delta-style one read −20 dB as −11.7 dB".) | N/A | — |
| Ladder from +17 V: R74 15K, R101 1K5, R102 1K1, R103 910R, R104 680R, R105 620R, R106 470R, R107 330R, R108 300R, R75 220R, R76 180R, R77 150R, R78 110R, R79 91R, R80 68R, R81 62R, R82 47R, R83 33R, R84 27R, R85 20R, R86 91R to METER GROUND; 20 × LM2901 (IC7-IC11), each comparator shunting its LED. | — (Master: R150 16K then R151-R170 1K5 ... 20R, 91R: identical but for the top 16K vs 15K; LM2901B.) | N/A | The master's top resistor is 16K where the Delta's is 15K (outside this check's scope; noted for the master reviewer). |
| LEDs: LD1-LD10 green, LD11 green, LD12 / LD13-LD19 amber ... LD20-LD24 red (two strings of ten); current sources TR3 / TR4 2SA970GR with R87 / R109 75R, R88 27K to −17 V, D3 / D4 1N4148 bias. | — (Master: BCP53-16 with 120R, Kingbright GaP / GaAsP, `docs/reviews/master_parts_review.md`.) | N/A | — |
| Comparator / rectifier supply: R89 / R90 10R + C31 / C32 47 µF 25 V, METER GROUND separate (its own conductor on the 20-way loom; R113 10R meter ground to ground "used on Delta 8 only", ED2778A). | — (Master: GNDM power net.) | N/A | — |

---

### 3. ED2779A — LH master: aux summing amps, aux masters, AFL, outputs, loom, power

Aux 1 read in full (IC1, IC2, TR1, TR2, R1-R20, C1-C9, VR1, S1, LD21); aux 2-6 are identical copies with their own
refs (aux 3: TR21 / TR22, IC5 / IC6, R41-R52; aux 4: TR31 / TR32, IC7 / IC8, R61-R80, S4, LD24; checked that the
values repeat). Ours: group aux master (U6, U5B, U7, RV3, SW3, D2) and the master's aux 5 / 6 (U12 / U13A / U14 / RV2 /
SW1 / D12 and U15 / U13B / U16 / RV3 / SW2 / D13).

| Delta (sheet, refs, value / topology as read) | Ours (refs, value / topology) | Status | Note |
|---|---|---|---|
| **Bus input:** AUX 1 (pin 24) → C1 100 µF 10 V → TR1 emitter. Bias: R3 1K + C3 47 µF 25 V from +VA, R1 / R2 33K emitter feeds, R5 / R6 10K collector loads, R7 6K8 to −VA, C2 47 µF 25 V on the tail node. | Group: AUX_SEL (jumpered) → FB2 bead → U6A − input, no DC block. Master: AUX5 / AUX6 → FB3 / FB4 → U12A / U15A. | RECORDED (spec §2, §13; delta.md T12) | — |
| **Summing amp with ground cancel:** TR1 / TR2 2SB737 common base; **TR1 base on GROUND CANCEL, TR2 base on local ground**; IC1-B TL072 differential stage (collectors to pins 5 / 6), C5 33 pF output → TR2 emitter; feedback IC1-A TL072 inverter (R9 22K in, R8 22K ∥ C6 15 pF) and **R4 10K ∥ C8 33 pF** back into TR1's emitter. Non-inverting overall. | Group: U6A OPA1612 inverting summer R28 22K 1 % ∥ C33 100p C0G, + input on GCANCEL; U6B re-inverter R29-R32 2K2 0.1 %, C34 / C35 22p, + leg GC_BUF (U1A). Master: U12A / R61 22K ∥ C62 100p; U12B / R62-R65 / C63-C64; U15A / R72 / C77; U15B / R73-R76 / C78-C79; + legs from GCANCEL_BUF (U1A). | RECORDED (delta.md T12, T13: GCANCEL "used only by the aux summing amps"; spec §3, §13) | Gain: Delta 10K / 22K = −6.8 dB at master minimum; ours unity (22K / 22K). Compensation: Delta 33 pF across 10K (corner 480 kHz), ours 100 pF across 22K (72 kHz, `sim/aux_master.cir`, spec §13). Same ground-cancel sense: one input on the line, the other on module ground. |
| **Master level inside the loop:** IC1-A's + input from the post-level buffer IC2-B through R10 6K8 / R11 27K (fraction 0.201); with the pot at minimum the inverter is unity (+ pin at ground), at maximum the inverter's gain falls to 0.598 and the summer's rises by 4.5 dB (manual p.63: lower noise at low master settings). | Pot after the re-inverter, outside every loop: C36 33 µF NP → RV3 Alpha RD901F A10K → C37 2.2 µF film + R33 100K → U5B unity buffer. Master: C65 / C80, RV2 / RV3, C66 / C81, R66 / R77, U13A / U13B. | RECORDED (delta.md T12 "The pot inside the aux loop buys little ... Not worth copying") | Computed: Delta summer −6.8 dB (min) to −2.4 dB (max) relative to a 22K send; ours 0 dB. |
| **Master level pot:** VR1 "MASTER LEVEL", CW arrow, value not printed on the sheet (UNREAD: no value at 300 dpi; the strip's aux pots are 10K A). C4 47 µF 25 V in. | RD901F A10K log, pin 1 GNDA, pin 3 signal; C36 33 µF NP (MUSE ES). | RECORDED (spec §13) | — |
| **Post-level buffer:** IC2-B 5532/2 follower; nominal "−12 dBu / −29.8 dBu" written at its output. | U5B OPA1612 non-inverting: R34 4K7 ∥ C38 100p, R35 DNF (2K2 = +10 dB), C39 10p at the + input. Master: U13A / R67 / C69 / R68 / C70, U13B / R78 / C82 / R79 / C83. | RECORDED (spec §13 `level_buffer()`, MG5) | — |
| **Ground-cancelling output amp:** IC2-A 5532/2: + input R13 1K5 (signal) and R19 10K (ring sense), − input R15 1K5 to ground, R16 10K ∥ C7 100 pF feedback → signal gain (10/11.5)(1 + 10/1.5) = 6.67 = **+16.5 dB**, ring gain 1.00; R18 75R + C9 220 µF 25 V → CN2 pin 1 (tip), ring CN2 pin 2 through R20 75R to ground; "+4 dBu / −7.8 dBu" at the output. Unbalanced, +21 dBu max. | U7 DRV135UA from A_OUT: R121 / R122 22R (CS4c), C40 / C41 10 µF NP matched pair (CS11b), A_OP / A_ON → J3 tip / ring, sleeve CHASSIS (G2b), D11 / D12 BAV199 (CS4b), C42 / C43 1 µF. Master: U14 / R228-R229 / C71-C72 / D89-D90 → CN5 19 / 20; U16 / R230-R231 / C84-C85 / D91-D92 → CN5 22 / 23. Balanced, +6 dB differential, +27 dBu max, no mute relay (MG20). | RECORDED (CLAUDE.md DRV134 family, G2b, CS4b, CS4c, CS11b; spec §13 "Aux outputs are unmuted"; delta.md T17) | Level chain: Delta −6.8 … −2.4 dB summer, 0 dB buffer, +16.5 dB output; ours 0 / 0 / +6 dB differential (0 dBu in → +6 dBu balanced, = +4 dBu + 2 dB). |
| **Aux output jack:** JSK1 TRS on the rear socket board via CN2, "Z4 / Z3 L29998" parts on the jack board (unread: look like ferrite or clamp parts on the output jack board, not legible). | J3 NJ6FD-V on the group jack board through CN3 pins 8 / 9; master: NJ6FD-V on the master jack board through CN5. | RECORDED (jack boards; CS4b clamps at the link) | UNREAD: Z3 / Z4 identity. |
| **AFL:** S1-B: pole common = R12 6K8 from the buffer output (post master level); pressed → PFL+ (pin 27), released → ground. S1-A / S1-C: LD21 red from +17 V, cathode through S1-C to a common line with **R200 3K3 to −17 V shared by all six AFL LEDs** (≈9.8 mA with one lit, split when several are pressed); R201 100K (aux 1; R202-R206 = 100K / 100K / 82K / 68K / 47K for aux 2-6) from the key's pole A to PFLDET. PFL− (pin 28) only brought to pads beside each AFL key. | Group: R36 22K from A_OUT → SW3 pole A → PFL, released → GNDA; pole B +VL → R37 100K → PFLDET, R38 4K7 → D2 red → GNDD (≈3.2 mA). Master: R69 / R80 22K, SW1 / SW2, R70 / R81 100K, R71 / R82 4K7, D12 / D13. | RECORDED (spec §13 AFL, §18 solo level; `docs/reviews/master_parts_review.md` PFLDET clamp) | Level-matched design: the Delta's 6K8 lifts its −12 dBu aux by 22K/6K8 = +10.2 dB onto the PFL sum (≈ −2 dBu, its strip PFL level); ours 22K at 0 dBu = unity, the same intent. The per-aux PFLDET resistors on the Delta (graded 100K, 100K, 100K, 82K, 68K, 47K for aux 1-6) have no equivalent: ours are all 100K as the strips. The Delta LED current ≈3× ours (recorded as "~3 mA, as the other LEDs"). |
| **Ground-cancel bus at the LH master:** R125 10R from GROUND CANCEL BUS (pin 26) to ground drawn; manual p.63: every module except the LH master has the 10R (so R125 not fitted). | Master: R10 100K keeper GCANCEL → GNDA only; U1A follower → GCANCEL_BUF for the five re-inverters. Group: R5 10R as a strip. | RECORDED (CLAUDE.md ground cancel "No tie ... 100K keeper"; spec §3; delta.md T13) | — |
| **Loom CN1 (as read):** 24 / 25 / 23 / 21 / 20 AUX 1-5 (22 = AUX 4 by the Delta pinout; the arrows read 24 AUX1, 25 AUX2, 23 AUX3, 22 AUX4, 21 AUX5, 20 AUX6), 26 GROUND CANCEL BUS, 27 PFL+, 28 PFL−, 29 PFLDET, 18 / 17 MIX L / R pass-through, 15 … 1 GROUP BUSES 1-8 each with a link J2-J9 to ground, even 2-16 ground, 33+32 +17 V, 31+30 −17 V, 34 +48 V. | Master CN2 / CN3 (two wing headers): 20 AUX6, 21 AUX5, 22 AUX4, 23 AUX3, 24 AUX1, 25 AUX2, 26 GCANCEL, 27 PFL, 29 PFLDET, 30-34 rails; 1 / 3 / 5 / 7 and 19 joined wing to wing as SPARE1-7 only; 28 spare. | SAME pinout / RECORDED (CLAUDE.md bus decision; "Pins 1, 3, 5, 7 are reserved for SUB 5-8"); **UNRECORDED**: the Delta grounds every unused group bus with a link (J2-J9) | Consequence: our SPARE1-7 conductors (pins 1/3/5/7, 19) float between ground conductors; a floating conductor couples capacitively into its neighbours (pin 1 is at the ribbon edge, 19 lies between 18 MIX L and 20 AUX6). Recommendation: a solder jumper per spare conductor to GNDA on the master (keeps the "unconnected on every board" rule for the modules); or document only. |
| **Pin 28 (PFL−):** the LH master passes it through and brings it to pads; the RH master drives it from the PFL re-inverter's virtual earth (ED2780, delta.md T15). | NC on every board. | RECORDED (docs/studies/console_survey.md CS5: "Pin 28 on GNDA at the master ... a free option, not needed"; `sim/review/cs5/pfl_xtalk.py`) | — |
| **Power:** separate decoupling per aux pair: +VA / −VA R210 / R220 10R + C70 / C71 220 µF 25 V (IC1-IC4), +VB / −VB R230 / R240 + C72 / C73 (IC5-IC8), +VC / −VC R250 / R260 + C74 / C75 (IC9-IC12); "SEPARATE DECOUPLING FOR AUXES IN PAIRS". | Group: one 10R fusible + 220 µF pair for the whole module (sub, aux, two returns), 100n per package. Master: its own power entry (spec §24-§25), 100n per package. | RECORDED (delta.md T19 "LH master: 10R + 220 µF per aux pair"; spec §25) | — |
| **Meter connector CN8 (20-way), METER GROUND via R270 10R, socket ground R280 10R, pot brackets BKT1-3.** | No 20-way loom; GNDM on the master only. | N/A | — |

---

### 4. ED2779B — LH master Mix L meter

Identical in topology to ED2778B (IC13-A TL071 rectifier, PR1 22K, R301 4K7, R302 22K, D1-D3 1N4148; average R303 33K +
C302 2.2 µF 50 V; peak R304 75R + C301 10 µF 25 V, R305 33K, R306 22K, C303 1n 100 V, J1 AVERAGE / PEAK; ladder R309 16K,
R310 1K5, R311 1K1, R312 910R, R313 680R, R314 620R, R315 470R, … R323 68R, R324 62R, R325 47R, R326 33R, R327 27R, R328 20R,
R329 91R to METER GROUND; IC14-IC18 LM2901 (LM139 on the supply box); LD1-LD10 green (−22 … −4), LD11 green −2, LD12 amber
0 dBu, LD13-LD16 amber +2 … +8, LD17-LD20 red +10 … +16; TR13 / TR14 A970GR with R330 / R331 75R, R332 27K, D4 / D5;
R307 / R308 10R + C305 / C306 47 µF 25 V).

| Delta | Ours | Status | Note |
|---|---|---|---|
| Mix L meter on the LH master; scale −22 … +16 dB about 0 dBu = +4 dBu out (manual p.62 "0 = +4 dBu and peak response", "to be checked"). | Master main L / R meters (spec §22): 20 LEDs −20 … +18, GNDM, precision peak detector, LM2901B, BCP53-16 / 120R. | N/A for the group / aux scope; architecture RECORDED (delta.md T18, spec §22) | The LH master's ladder top is **R309 16K** (the group's ED2778B reads R74 15K); our master uses 16K, so it follows the LH master sheet, not the group sheet. |

---

### 5. Numbers that decide rows (computed from the readings)

| Quantity | Delta | Ours |
|---|---|---|
| Group / sub summer gain vs the strip feed | 3K9 / 10K = −8.2 dB (Delta 8: 8K2 / 10K = −1.7 dB) | 4K7 / 4K7 = 0 dB |
| Sub post-fader amp | 1 + 2K4 / 2K0 = +6.8 dB (Delta 8: 1 + 4K7 / 2K2 = +9.9 dB) | 1 + 4K7 / 2K2 = +9.9 dB |
| Sub output stage | IC6-A: (4K3 / 6K5)(1 + 4K3 / 2K2) = +5.8 dB, ring gain 1.00, unbalanced | DRV135: +6.0 dB differential |
| Sub pan law (relative to a strip feed) | centre 0.586 V into 8K2 vs 1 V into 10K = −2.9 dB; hard 10K / 8K2 = +1.7 dB (4.6 dB law) | −2.7 dB centre, +1.7 dB hard (4.4 dB law, CS2b) |
| Aux summer gain vs a 22K send | 10K / 22K = −6.8 dB at master min; ×1 / 0.598 at max = −2.4 dB | 22K / 22K = 0 dB |
| Aux output stage | IC2-A: (10K / 11K5)(1 + 10K / 1K5) = +16.5 dB, ring gain 1.00, unbalanced | DRV135 +6.0 dB differential |
| AFL onto the PFL bus (22K feedback) | 22K / 6K8 = +10.2 dB from a −12 dBu point ≈ −2 dBu | 22K / 22K = 0 dB from a 0 dBu point |
| Aux summer compensation corner | 1 / (2π · 10K · 33 pF) = 480 kHz | 1 / (2π · 22K · 100 pF) = 72 kHz |
| AFL / PFL LED current | LH master (34 − 1.8) V / 3K3 ≈ 9.8 mA (one lit); group ON LEDs ≈ 6.8 mA | (17 − 1.9) V / 4K7 ≈ 3.2 mA |

---

### UNRECORDED discrepancies for sign-off

1. **Return EQ.** Delta (ED2778A): each tape return has a 2-band shelving EQ (IC2-B TL072, VR1 / VR2 10K LIN CD, 22K /
   22K, 4K7 + 6n8, 7K5 + 5K1 + 100n). Ours: no EQ on the eight stereo returns (spec §16 lists receiver, level, buffers,
   routing, PFL). Consequence: an effects return cannot be tilted on the console. Recommendation: **document only**
   (keep; add "no EQ, use a strip for a return that needs it" to spec §16).
2. **Return aux send.** Delta: VR3 / VR8 20K LOG + R13 / R32 22K from each return to AUX 1 (pin 24). Ours: none; the
   group's aux pins carry only its jumpered bus. Consequence: a return can't feed an aux (reverb into a delay send).
   Recommendation: **document only** (keep; a stereo return would need a mono sum or two pots).
3. **Unused group buses grounded.** Delta LH master (ED2779A): links J2-J9 ground GROUP BUSES 1-8 that no module
   sums; ours leaves the reserved conductors 1 / 3 / 5 / 7 (SUB 5-8) and 19 floating, joined only wing to wing at the
   master (SPARE1-7). Consequence: a floating conductor between grounds picks up and re-radiates its neighbours (19 lies
   between MIX L and AUX6); grounding it costs nothing in parts. Recommendation: **adopt as an option**: one solder
   jumper per spare conductor to GNDA on the master only (the modules keep them unconnected, as decided), or document
   only.
4. **Insert send build-out.** Delta group R112 220R (its mix insert uses 75R); ours R11 75R on the sub insert (and on
   every master insert). Consequence: none audible (75R vs 220R into a ≥10K outboard input; short-circuit dissipation
   already covered by the anti-surge ERJ-P06J750V). Recommendation: **document only**.
5. **PFLDET resistor grading on the LH master.** Delta: 100K / 100K / 100K / 82K / 68K / 47K for aux 1-6 (ED2779A R201-R206);
   ours: 100K on every key (strips, groups, master). Consequence: the Delta weights later keys to overcome its TL072
   detector's 150K bias; ours (LM393B, 1 µF debounce, `sim/pfldet.py` 42 keys) needs no grading. Recommendation:
   **keep, document only**.

Everything else on these four sheets is either the same (bus pinout, 22K aux sends into a 22K-referenced summer, 2.2 µF
+ 100K wiper couplers, 100K PFLDET keys, 22K AFL feeds, link-per-bus select, A10K pots, pin 28 open on the group) or a
difference already written down (M1 modules, OPA1612 / OPA1656 / DRV135, ground cancel on every summer with the
re-inverter, no master-end tie, 4K7 summing, no DC block at the summer, buffered receivers, CS2b pan law, CS4b / CS4c /
CS6 / CS10 / CS11b, unmuted aux outputs, insert at 0 dBu, AFL from POST_SUB, no −10 dBV switch, no group meters).

UNREAD: the value of VR1 "MASTER LEVEL" (not printed on ED2779A), the identity of Z3 / Z4 "L29998" on the Delta aux
output jack board, and the exact return path of the group's red PFL LEDs LD13 / LD15 through S2-A / S6-A (300 dpi crop
ambiguous; it does not affect ours).


---

## Part C: RH master ED2780 sheets 1-4 vs the master module

Date: 2026-10-28. Read: `ref/Sndcft_DeltaDLX_Schems.pdf` PDF p.10-13 (ED2780 sheets 1-4, issue 2, 21/8/92) at 300 dpi
(tiles and crops not in the repo), the 200 Delta Technical Manual Part2 printed p.61-65 (circuit descriptions) and Part3
printed p.29 (system / power), p.114 (SRC power connector), p.124 / p.128 (input and master rear-connector pinout tables).
Ours: `tools/gen_master.py` + `tools/master_lib.py`, `master.net` / `master_jack_board.net` (parsed to
`work_master/master_comps.txt`: every ref with its pin nets), `master_section_spec.md` v0.12, `console_architecture.md`,
`docs/console_survey/delta.md`, CLAUDE.md Decisions. Nothing tracked was modified.

Reading notes on the Delta sheets (where my reading differs from or adds to `docs/console_survey/delta.md`):
- Monitor-select receivers (IC7-A/B mix, IC19-A/B 2-track): 43K / 43K in, + leg 22K + 33p; the − leg feedback is a T:
  output → 6K8 (R38 / R91 …) → node → 20K (R36 / R32 …) → − input, with 2K2 (R39 / R92 …) from the node to ground
  through S1 ("MIX −10" / "TAPE −10"). S1 open: Rf = 26.8K, gain 26.8 / 43 = 0.62 (−4.1 dB); S1 closed: Rf,eff =
  6.8 + 20 + 6.8·20 / 2.2 = 88.6K, gain 2.06 (+6.3 dB). delta.md ("20K / 22K") omits the switched T.
- Mix insert jack JSK1 (sheet 2) and the manual's connector tables (p.124 input, p.128 master): **tip = insert return,
  ring = insert send**, console-wide.
- S1 is one 6-pole operating-level switch: poles D / E pad the post-amps (1K2 / 430R, −11.6 dB), poles A / B / C / F
  raise the four monitor receivers' gain so the control room and meters stay at −2 dBu.
- The phones socket JSK4 is fed from the C/ROOM amplifiers' outputs (after R51 / R151 47R): the Delta has no PHONES
  level and no separate phones amplifier. The C/R outputs leave through a 470R / 470R pad (R54 / R53, R154 / R153).
- Sheet 3 carries only the RIGHT meter (its title block reads "SHT. 3 OF 3"); the left meter is on the LH master
  (ED2779B, not in the PDF set). Sheet 4 is the BVE option ("SHT. 4 OF 4", drawn by JH).

Status key: SAME / RECORDED (where) / UNRECORDED (a difference nobody wrote down) / N/A (Delta-only or ours-only) /
UNREAD. Our refs are the generated ones in `master.net` (they move when the generator changes; the function names are
in the spec).

---

### Sheet 1 — ED2780 sht 1: monitor select, PFL switcher / sum / detector, C/R and phones amps, talkback, oscillator, motherloom, power

| Delta (sheet, refs, value / topology as read) | Ours (refs, value / topology) | Status | Note |
|---|---|---|---|
| **Monitor source, mix.** IC7-A / IC7-B TL072 differential receivers on MIX L+/L− and R+/R− (the balanced XLR outputs, read back after S1's output pad): R34 / R35 43K, R37 22K + C21 33p on the + leg, feedback R36 20K + R38 6K8 T with R39 2K2 to ground via S1-A ("MIX −10"), C20 33p; gain −4.1 dB (S1 open) / +6.3 dB (S1 closed) → "BVE MIX L" at −2 dBu | POST_L / POST_R (after the master fader post-amps U5A / U5B, before the DRV135s) straight into SW3 and the DG413; no receiver | RECORDED (delta.md Monitoring: "We tap POST_L / R before the DRV135"; spec §17) | The Delta hears the XLRs (pad included); ours cannot show an output-stage fault. Accepted. |
| **Monitor source, 2-track.** IC19-A / IC19-B TL072 receivers on 2 TRK L± / R±: R30 / R31 43K, R33 22K + C51 33p, R32 20K + R91 6K8 T, R92 2K2 via S1-C ("TAPE −10"), C50 33p; LK1 / LK2 "break for BVE" | EXT: J8 / J9 (R jack normalled to L: J9 TN = EXT_LT, RN = EXT_LR), sleeves CHASSIS; per leg 1M (R83 / R212, R88 / R217), 220R (R213 / R214, R218 / R219), 100p C0G at the follower + input (C88 / C89, C94 / C95), OPA1656 followers U43 / U44, 100R (R215 / R216, R220 / R221), then OPA1612 U17A / U17B with 4 × 10K 0.1 % (R84-R87, R89-R92) and 33p on both legs (C90 / C91, C96 / C97): unity. Then R93 / R95 100R, C98 / C99 33 µF NP, R94 / R96 47K → EXT_L / R | RECORDED (spec §17, MG1; G3b `docs/studies/ground_study.md`; delta.md T1) | Delta input Z 43K, ours 1M / leg. No −10 dBV gain option on EXT: see sign-off item 2. |
| **MIX / 2TK monitor select.** S5-A / S5-B (2TK): MON L = BVE 2TRK L (contact 8) or BVE MIX L (contact 5); same for R | SW3 "EXT select" PVA2: 2 = MON_L, 1 = EXT_L, 3 = POST_L; 5 / 4 / 6 for R; latched = EXT | SAME | Both poles carry audio, so no EXT LED (spec §29). |
| **PFL switcher.** MON L → C22 47/25 → TR5 J112 (series) → −2 dBu node; R40 47K from the op-amp side of C22 to the gate, D1 1N4148 gate → TR14 collector line; PFL sum → C28 47/25 + R64 47K → TR6 J112 (gate D4 → TR13 collector line); R side TR7 (C122, R140, D101) / TR8. Hard switch, mono PFL to both sides | One DG413 U20: SW1 (pins 1/3/2) PFL_SIG → CRS_L, SW2 (16/14/15) MON_L → CRS_L, SW4 (8/6/7) PFL_SIG → CRS_R, SW3 (9/11/10) MON_R → CRS_R; all IN pins on PFL_ON; sources AC-coupled C111-C114 33 µF NP + R105-R108 1M, CRS on the D side with R109 / R111 100K; +5VL logic from +VA via R104 4K7 + D14 BZX84C5V1 + C110 1 µF, D15 BAT54W | RECORDED (CLAUDE.md Decision "PFL switcher = one DG413"; spec §19; `docs/reviews/master_parts_review.md` item 4) | Our sim of the J112 copy gave −27 dB crosstalk and −2.4 V on CRS. |
| **Monitor level node.** −2 dBu node → VR3-A / VR3-B C/ROOM 10K LOG (dual), wiper → C23 / C123 2µ2/50 → R42 / R142 4K7 → IC8 + input | CRS_L / R → OPA1656 followers U21A / U21B → R110 / R112 100R → CRSB_L / R → (R236 / R237 91K, DIM) → RV5 C/Room dual A10K (pin 1 GNDA) → C124 / C128 2.2 µF film + R125 / R126 100K → OPA1612 followers U23A / U23B (C127 / C129 22p) | RECORDED (spec §19-20, MG5 / MG6) | Pot and coupler the same idea; the Delta's pot is driven by the J112s' source node, ours by buffered CRSB. Coupler corner: Delta 2.2 µ into ≈ 24.7K ≈ 2.9 Hz, ours 2.2 µ × 100K = 0.72 Hz. |
| **C/R amplifier.** IC8-A / IC8-B TL072 "ground-cancel CRM O/P amps": + input R42 4K7 from the pot, R45 20K from the output-jack ground-sense node; − input R43 4K7 to PHONES GND, R44 20K feedback; C25 15p; discrete class-AB output TR9 2SC2240BL / TR10 2SA970GR with R47 / R48 10R emitters, D2 / D3 1N4148 bias, R46 4K7; C24 220/25 out, R49 22K bleed to the sense node, R50 47R sense node to PHONES GND; R51 47R build-out. Gain 20 / 4.7 = 4.26 (+12.6 dB), output follows the far ground ×1.0 | OPA1612 followers U23A / U23B (unity) → DRV135 U24 / U25 (+6 dB differential) with R232-R235 22R, C130 / C131 / C134 / C135 10 µF NP (sorted pairs) inside the Sense loop → K4 / K5 G6K-2F-Y → J10 / J11 TRS (tip hot, ring cold, sleeve CHASSIS) | RECORDED (spec §20; G2b; delta.md Monitoring) | Delta max C/R out: −2 dBu + 12.6 − 6 (pad) ≈ +4.6 dBu unbalanced, 250 Ω; ours 0 dBu at CRS → +6 dBu balanced. |
| **C/R output pad / connector.** R54 / R154 470R series, R53 / R153 470R shunt to PHONES GND; jack pin 1 hot, pin 2 "ground sense", pin 3 ground/screen (manual p.128) | No pad; balanced TRS from the DRV135 | RECORDED (G2b, spec §20) | — |
| **Dim / cut.** R90 / R190 470R from the IC8 + input node to ground through S3-C / S3-D (talkback 1-2): 470 / (4700 + 470) = −20.8 dB; R52 / R152 0R through S4-A / S4-B (talkback ALL): cut. Only while talkback is pressed; no front-panel DIM key | SW4 "C/Room DIM" (latching PVA2): R236 / R237 91K between CRSB_L / R and the C/ROOM pot tops CRP_L / R, shorted while released: −20.0…−20.75 dB; phones and meters unaffected | RECORDED (CS7 `docs/proposals/cs7_proposal.md`, 2026-10-28; console_architecture §6 "C/Room DIM … was excluded") | Same depth. No cut / C/R mute key in ours (the Delta's only comes with the BVE option, sheet 4). |
| **Phones.** JSK4 tip = LEFT, ring = RIGHT, sleeve PHONES GND, fed from the C/R amps after R51 / R151 47R; no phones level pot, no separate amp (the C/R amp is rated for 8 Ω) | RV6 PHONES dual A10K on CRSB_L / R (independent of C/ROOM) → C138 / C147 2.2 µF film + R129 / R133 100K → OPA1612 U26A / U26B (on ±VP) driving LME49600 U27 / U28 inside the loop: R131 / R135 4K7, R132 / R136 2K2 (+9.9 dB), C146 / C153 100p from the op-amp output to its − input, C141 / C148 22p; R130 / R134 2R2 2512 out; K6 relay (NC to PHONESGND) → J12 tip L, ring R, sleeve PHONESGND | RECORDED (spec §21; console_architecture §5 / §6) | Delta phones level = C/ROOM level; ours separate (a design choice written in §21, not a Delta comparison). Jack tip / ring assignment the same. |
| **Phones / C/R supply.** ±VP: R251 / R252 33R + C36 / C37 1000 µ/25; PHONES GND separate, R94 0R to main audio ground at the power connector | ±VP: R3 / R4 2R2 2512 + C3 / C4 1000 µ/25; PHONESGND net tie NT3 at the star stud; LME49600 bypasses C144 / C145 / C151 / C152 10 µF NP + 100n | RECORDED (spec §21, §25; MG11 / MG17) | 33R → 2R2 because the LME49600 can sit at its current limit. |
| **PFL sum amp.** PFL+ (pin 27) → C26 100/10 → IC9-A TL072 inverting, R61 22K feedback + C27 100p (72 kHz), R60 47K bus bleed; IC9-B second inverter R62 / R63 22K; **PFL− (pin 28) wired to IC9-B's virtual earth** (manual p.65: anti-phase virtual earth beside the PFL bus cuts crosstalk) | FB5 ferrite → U18A OPA1656 inverting, R97 22K 1 % ∥ C102 100p, + input on GCANCEL; U18B re-inverter 4 × 2K2 0.1 % (R98-R101) + C103 / C104 22p, + leg from GCANCEL_BUF; no input cap; pin 28 = net PFLN on CN2.28 / CN3.28 only (passed between the wings, unused) | RECORDED (spec §18; CLAUDE.md CS5 check 2026-10-27: pin 28 on GNDA "a free option, not needed"; Decisions: OPA1656 on the PFL sum) | Both unity from a 22K source, same 72 kHz corner. |
| **PFL level.** None: the sum goes at fixed gain to TR6 / TR8 | RV4 SOLO LEVEL A10K after C105 33 µF NP; C106 2.2 µF film + R102 100K → OPA1612 follower U19A, C109 22p, R103 100R → PFL_SIG; fully up = unity | RECORDED (spec §18, MG3) | Ours-only control; at full it equals the Delta. |
| **PFL detector.** IC10-B TL072 inverting summer: PFL DET (pin 29) into the − input, R65 150K to −VL (113 µA), each pressed key +VL through 100K (170 µA); feedback R66 100K + D5 1N4148 clamp + C42 1n: +10 V idle, −0.6 V active; threshold = 0.67 key. R67 33K → TR13 2SC2240BL (R68 820R, C43 1n, R69 100K load) → TR14 (R70 680K, C44 1n); collectors drive the J112 gates through D1 / D4 / D101 | R113 10K to GNDD, clamp D16 + D17 (2 × 1N4148 in series to GNDD), C120 1 µF debounce; LM393B U22A compares PFLDET with PFL_REF = +VL × 10K / 340K (R114 330K / R115 10K) = 0.50 V; one press 0.92 V (1.84×), 24 presses 1.29 V; R116 100K pull-up to +5VL, R117 10M hysteresis (~20 mV), R118 10K → PFL_ON (DG413 IN pins); U22B (same inputs) → FL_HOLD | RECORDED (spec §19; `docs/reviews/master_parts_review.md` S-items: clamp; `sim/pfldet.py`) | Delta's ratio one key / threshold 1.5×, ours 1.84×; the Delta has no clamp (its released keys' LEDs back-feed is what our clamp fixes) and no debounce beyond C42 1n. |
| **PFL LED.** LD21 red "PFL ON", R71 3K3 from +VL, sunk by TR14 to −VL: (34 − 2) / 3.3K ≈ 9.7 mA, steady | D19 "PFL ACTIVE" red 5 mm, R124 3K3 anti-surge from +VL, cathode on U11B's output (sinks to −VL): ~9.5 mA; flashes ~2 Hz (R119-R121 100K, R122 1M, C123 330n, D18 hold from FL_HOLD, R123 10K) | RECORDED (spec §19 rude solo; console_architecture §6 "rude solo LED") | Same current; ours flashes. |
| **Remote meter connector.** CN8 5-way: 1 METER L (via R41 100R from the −2 dBu node), 2 ground, 3 +17 V (+VL), 4 METER R (R141 100R), 5 −17 V (−VL) | CN4 5-way: 1 MTR_L, 2 MTR_R, 3 +VM, 4 GNDM, 5 −VM; MTR_L / R from CRSB_L / R via R138 / R175 100R | RECORDED function (spec §22 "Delta R41 / R141"); pin order UNRECORDED (trivial) | Sign-off item 4 (document only). |
| **Talkback.** CN3 electret mic, IC10-A preamp (R87 47K bias, C32 2µ2/50, R88 100K, C34 100p, VR2 10K log level, C35 100/10, R89 15R), S3 (1-2) / S4 (ALL): 62K × 8 (R200-R207) into AUX 1-6, 30K × 10 (R208-R217) into GRP 1-8 and MIX L / R; notes: "talkback overrides osc", "preamp set to min gain when not in use", "slate resistors grounded when not in use" | None | N/A — excluded explicitly (console_architecture §6 Excluded: "Talkback, oscillator, tape I/O") | — |
| **Oscillator.** IC11-A / IC11-B TL072 1 kHz Wien bridge (R80 150R, C29 / C30 100n, R81 18K, R82 9K1, R83 8K2, R84 10K, R85 820R, R86 8K2, D6 / D7 1N4148 limiter), S2 ON, R86 75R + C31 47/25, VR1 10K log OSC LEVEL, into the same bus resistors | None | N/A — excluded explicitly (console_architecture §6) | — |
| **Motherloom CN1 (34-way).** Top row 33 31 29 28 26 25 23 21 20 19 18 17 15 13 11 9 7 5 3 1, bottom 34 32 30 16 27 24 14 22 12 10 8 6 4 2. +17 V on 32 / 33 / 34?: +17 V to 33, 32 (and 34 is +48 V), −17 V to 30 / 31; 29 PFL DET; 28 PFL−; 27 PFL+; 26 GND CANCEL via R220 10R from master ground (Z200 → Z60); AUX 6/5/4/3 on 20/21/22/23, AUX 1 / 2 on 24 / 25; 19 unconnected; 18 MIX BUS L, 17 MIX BUS R; GRP 1-8 on 15 / 13 / 11 / 9 / 7 / 5 / 3 / 1; even 2-16 ground | CN2 (left wing) / CN3 (right wing), identical pinout: 1 / 3 / 5 / 7 SPARE1-7 (joined wing to wing, reserved for SUB 5-8), 9 SUB4, 11 SUB3, 13 SUB2, 15 SUB1, 17 MIXR, 18 MIXL, 19 SPARE19, 20 AUX6, 21 AUX5, 22 AUX4, 23 AUX3, 24 AUX1, 25 AUX2, 26 GCANCEL, 27 PFL, 28 PFLN, 29 PFLDET, 30-31 −VBUS_w, 32-34 +VBUS_w, even 2-16 GNDA | SAME (pins 1-33); pin 34 RECORDED (`docs/proposals/wing_power_proposal.md` W1: third +V); 17 / 18 order RECORDED (CLAUDE.md Decisions: ED3344C order kept; the manual p.134 says the opposite) | The Delta's master is one board across the whole loom; ours splits it into two wing headers with the buses bridged on the master. |
| **Ground cancel at the master.** R220 10R "ground cancelling resistor" from master ground to pin 26 | No tie; R10 100K keeper GCANCEL → GNDA; U1A OPA1612 follower GCANCEL → GCANCEL_BUF feeding every re-inverter's + leg; every summer's + input on the raw line | RECORDED (CLAUDE.md Decisions "no tie … 100K keeper"; spec §3; delta.md T13) | Delta's mix summers don't use the line at all (T13). |
| **Power connections.** 0.156" Molex CN5 8-way to the SRC socket (5-way on the rear panel, p.114): CN5-8 +17 V, CN5-5 −17 V, CN5-4 +48 V, CN5-2 METER GROUND, CN5-7 / 6 / 3 / 1 main audio ground; CN9 spade terminal + BKT1 / BKT2 brackets on main audio ground; R94 0R PHONES GND → main audio ground. No fuses, no reverse protection on the master | J1 7-way terminal wired to a panel NC7MD-LX: 1 CHASSIS, 2-3 +VBUS, 4-5 GNDA, 6-7 −VBUS; D1 / D2 SS54 reverse clamps; CN1 M4 star stud (GNDA) with net ties NT1 GNDD, NT2 GNDM, NT3 PHONESGND, NT4 CHASSIS; wing PTCs F1 / F3 MF-RX250/72 (+V), F2 / F4 MF-RX185/72 (−V) | RECORDED (spec §24-26; CLAUDE.md Decisions PSU / Power / G1) | +48 V: N/A (no phantom; pin 34 is +V). |
| **Local rail filtering.** Op-amps ±VA: R255 / R256 10R + C40 / C41 47/25; logic ±VL: R253 / R254 10R + C38 / C39 47/25; phones ±VP: 33R + 1000 µ (above); meters (sheet 3): R307 / R308 10R + C305 / C306 47/25 | ±VA: R1 / R2 1R anti-surge + C1 / C2 470 µ/25 (+ 100n per package); ±VL: R7 / R8 10R + C7 / C8 47 µ; ±VP: 2R2 + 1000 µ; ±VM: R5 / R6 10R + C5 / C6 47 µ; power LED D3 green + R9 4K7 on +VL | RECORDED (spec §25 table; delta.md T19) | VA 1R instead of 10R: the master's audio branch carries ~0.14-0.3 A. |
| **Op-amp types, sheet 1.** TL072 everywhere (IC7, IC8, IC9, IC10, IC11, IC19); J112 switches; 2SC2240BL / 2SA970GR output pairs | OPA1612 (U17, U19, U23, U26), OPA1656 (U18 PFL sum, U21 CRS followers, U43 / U44 EXT followers), LM393B (U22, U11B), DG413, LME49600 | RECORDED (CLAUDE.md Decisions "OPA1612 … OPA1656 on the PFL sum and CRS followers"; delta.md T20) | — |

### Sheet 2 — ED2780 sht 2: mix summing amps, insert, fader post-amps, balanced outputs, mono

| Delta (sheet, refs, value / topology as read) | Ours (refs, value / topology) | Status | Note |
|---|---|---|---|
| **Mix summing amp (L; R = R10x / C10x / TR3-TR4 / IC2).** MIX BUS L → FB1 ferrite → C1 1000 µ/6.3 → TR1 2SB737 emitter; TR1 / TR2 common-base pair, bases to local ground (not GND CANCEL), emitters fed by R1 / R2 10K from +17 V through R3 220R (C2 220/25), collectors R6 / R7 4K7 + R5 820R to −17 V (C56 220/25), C3 100p across the collectors; IC1-B 5532 differential stage; IC1-A 5532 unity inverter R8 / R10 4K7 in the loop; R4 3K9 feedback into the emitter; C4 220p compensation; R9 75R build-out, C5 47/25, R11 47K: "−10 dBV / −7.8 dBu", "gain −5.8 dB ref chan fader top" (3K9 / 10K routing = −8.2 dB per source). Power box lists IC1 / IC2 as "072" though the symbols say 5532/2 | MIXL → FB1 ferrite → U1B OPA1612 inverting, R11 4K7 1 % ∥ C11 100p C0G (339 kHz), + input on GCANCEL, no input cap → SUM_L; U2A re-inverter 4 × 2K2 0.1 % (R12-R15) + C12 / C13 22p 5 %, + leg from GCANCEL_BUF → MIX_L (unity per 4K7 source). R: FB2, U3A, R21, C21; U3B, R22-R25, C22 / C23 → MIX_R | RECORDED (CLAUDE.md Decisions "4K7 summing … 4K7 feedback", "ground cancel on every summer + re-inverter"; spec §2-3; delta.md T12-T14) | Mix level: Delta −7.8 dBu at the insert, ours ≈ 0 dBu (T21). |
| **Mix insert.** Send = summer output after R9 75R / C5 47 µ / R11 47K; JSK1: **ring = send, tip = return** (manual p.128, p.124), sleeve ground; return normalled to send; return → C55 47 µ/25 → the fader top (ZZ1 "FADER SEND") and the mono summer, with no buffer | R16 / R26 75R anti-surge → **J1 / J2 tip = MIX_L_SEND (RN normal), ring = MIX_L_RETRAW**, sleeve GNDA; return → C16 / C24 33 µF NP + R17 / R27 47K → R18 / R28 1K + C17 / C25 100p → OPA1612 followers U2B / U4A → R19 / R29 75R → C18 / C28 100 µF NP + R20 / R30 47K → PRE_L / R; BAV199 clamps D79-D82 at the link | Level / buffer RECORDED (spec §4, MG7; delta.md T6). **Tip / ring assignment UNRECORDED** | Sign-off item 1. |
| **Master fader and post-amp.** Fader off-board (ZZ1 top, ZZ3 wiper, ZZ2 ground; ALPS 10K log 100 mm per the spares list) → C6 2µ2/50 + R12 100K → IC3-A 5532 non-inverting, R13 1K / R14 1K + C7 100p (+6 dB, 1.6 MHz) → R15 1K2 / R16 430R pad through S1-D ("−10" = 430 / 1630 = −11.6 dB; "+4" direct): "−2 / −13.8 dBu" → C8 47/25 → EBOS | RV1 Bourns PTB0144 dual A10K (pin 1 GNDA) → C29 / C35 2.2 µF film + R31 / R36 100K → U5A / U5B OPA1612 (one package), R33 / R38 4K7 + C33 / C37 100p (339 kHz), R34 / R39 2K2 (+9.9 dB), C32 / C36 10p at the + input, R32 / R37 47R build-out → C34 / C38 100 µF NP + R35 / R40 47K → POST_L / R | RECORDED (spec §5, MG4; delta.md T8; CLAUDE.md "Fader post-amp +10 dB") | No operating-level switch in ours: sign-off item 2. |
| **Balanced output amps (L; R = IC5 / RIC3 / RIC4 / C109 / C111 / R117-R120 / PR2).** "EBOS", gain +6 dB: IC4-A / IC4-B 5532 cross-coupled, RIC1-A…D 4K7 (input and cross legs), RIC2-A…D 10K (feedback and cross-coupling taken after the output caps), C9 / C11 22p (10K ∥ 22p = 723 kHz), R17 / R18 75R, C13 / C14 47/25, R19 / R20 1K + PR1 1K BALANCE preset to ground; MIX L −/+ to Z205-Z207 (loom to the XLRs), "+27 dBu into 600 Ω". No mute relay, no power-on delay | DRV135UA U7 / U8 (U9 mono): VIN from POST_L / R, pin 3 GNDA, C45 / C46 … 1 µF rail bypasses; each leg VO → R222-R227 22R anti-surge → C43 / C44 / C47 / C48 / C51 / C52 10 µF NP (pairs sorted ≤ 2 %) → Sense pin on the output node; K1 / K2 / K3 G6K-2F-Y (COM = connector, NO = Sense node, NC = GNDA), R46-R48 560R coils from +VBUS, D4-D6 flyback; D83-D88 BAV199 at the link | RECORDED (CLAUDE.md Decisions "All balanced outputs use the TI DRV134 family … DRV135UA"; spec §7-8; CS4b / CS4c / CS11b; delta.md T17) | DRV135: +27 dBu differential on ±17 V, OCMR 46 dB min; the Delta's balance is set per output by PR1 / PR2. |
| **Output XLR pinout.** Pin 1 ground/screen, pin 2 hot (+), pin 3 cold (−) (manual p.128) | J3 / J4 / J5 NC3MAV: 1 CHASSIS, 2 MAIN_x_XP (hot), 3 MAIN_x_XN | SAME | Pin 1 on CHASSIS, not audio ground (G2 / G2b). |
| **Mono.** "SUMMER" IC6-B 5532 inverting: R21 / R121 22K from the L / R insert-return nodes (**pre master fader**), R22 15K feedback (−3.3 dB each, "−7.8 dBu uncorr."), C15 47/25 → ZZ7 → J1 link / ZZ8-ZZ9 "mono fader option" → R23 2K7 → IC6-A "GC O/P AMP, +11.3 dB" (R25 11K + R26 feedback, C16 100p) → R27 75R + C17 47/25 → tip; ground-sense ring through R28 39R to the + input with R24 10R to ground; JSK3 "mono output" TRS, ground compensated (tip hot, ring ground sense, p.128) | R41 / R42 10K from POST_L / POST_R (**post master fader**) into U4B OPA1612, R43 10K + C39 100p (unity per side) → MONO_INV; U6A inverter R44 / R45 10K + C40 22p → MONO; DRV135 U9 → K3 → J5 XLR; no mono fader | RECORDED (spec §6 "mono follows the master fader; optional mono fader left out"; delta.md T17) | Centre-panned source: ours +3.3 dB in mono vs one side (CS2 law). |
| **Decoupling.** C18 / C19 100n "local decouple" at IC3 / IC6 and IC4 / IC5 only; IC1 / IC2 none shown | 100n pair per package (C9 / C10 … C192 / C193), 1 µF per DRV135 | SAME in intent | — |
| **Op-amp types, sheet 2.** 5532 (IC1-IC6), 2SB737 input pairs | OPA1612 (U1-U6), DRV135 | RECORDED (Decisions; delta.md T20) | — |

### Sheet 3 — ED2780 sht 3: meter (right; the left meter is on the LH master)

| Delta (sheet, refs, value / topology as read) | Ours (refs, value / topology) | Status | Note |
|---|---|---|---|
| **Meter source.** METER R from the −2 dBu node via R141 100R (sheet 1) / the 20-way loom; shows whatever is monitored | MTR_L / MTR_R from CRSB_L / R via R138 / R175 100R (mix, EXT or PFL, as monitored) | SAME (spec §22) | — |
| **Calibration.** PR3 22K preset as an input divider → R301 4K7 | RV7 / RV8 10K trimmers in the summer's feedback (R143 / R180 10K + trimmer: gain 0.5-1.0 of U29B / U36B), beside the op-amp | RECORDED (spec §22, MG9) | Both a single trim; ours is in a low-impedance loop, the Delta's is a 22K source into the rectifier. |
| **Rectifier.** IC12-A TL071 precision **half-wave**: R301 4K7 in, R302 10K feedback, D10 / D11 1N4148 (gain 2.13 for one polarity, 0 for the other) | **Full-wave**: U29A TL072H half-wave (R139 / R140 10K, D23 / D24), U29B summer R141 20K (v) + R142 10K (2 × half-wave), feedback R143 10K + RV7, C156 22p; R side U36A / U36B, R176-R180, D51 / D52, C174 | RECORDED (spec §22 "The detector is new"; `sim/meter.cir`) | Half-wave under-reads asymmetric synth waves. |
| **Average ballistics.** R303 33K + C302 2.2 µF/50 V → J2 "AVERAGE" (73 ms) | R144 / R181 33K + C157 / C175 2.2 µF film → JP1 / JP2 pin 3 (73 ms) | SAME (spec §22 "Delta R303 / C302") | — |
| **Peak ballistics.** D14 1N4148 → R304 75R → C301 10 µ/35 V, R305 33K → J2 "PEAK", R306 22K discharge (10 µ × 22K ≈ 0.22 s), C303 1n at J2 | U30A / U37A precision peak detector: D25 / D53 inside the loop, R145 / R182 220R → C160 / C178 1 µF (0.22 ms attack), release R146 / R183 330K + R147 / R184 220K (1 µ × 550K ≈ 0.55 s), feedback R148 / R185 10K from the follower, clamp D26 / D54, C161 / C179 22p; JP1 / JP2 PEAK side on the diode cathode | RECORDED (spec §22, MG8: the Delta-style detector read −20 dB as −11.7 dB); release time wording UNRECORDED (spec says "0.55 s, Delta-like"; the Delta's R306 / C301 gives ≈ 0.22 s) | Sign-off item 3 (document only). |
| **Detector output.** J2 → directly to all 20 comparator + inputs (no follower) | JP1 / JP2 → TL072H follower U30B / U37B → R149 / R186 470R build-out → ML_DET / MR_DET | RECORDED (spec §22, MG9: LM2901 input current 27 mV error against a 67 mV bottom tap otherwise) | — |
| **Threshold ladder.** +17 V → R309 16K → taps through R310 1K5, R311 1K1, R312 910R, R313 680R, R314 620R, R315 470R, R316 330R, R317 300R, R318 220R, R319 180R, R320 150R, R321 110R, R322 91R, R323 68R, R324 62R, R325 47R, R326 33R, R327 27R, R328 20R → R329 91R → METER GROUND. Computed: 23 009 Ω total, 0.739 mA; tap 1 (−20 dB) 67 mV, tap 11 (0 dB) 0.649 V, tap 20 (+18 dB) 5.18 V; steps 2.0 dB | +VM → R150 / R187 16K → R151-R169 / R188-R206 identical values → R170 / R207 91R → GNDM; ML_T1…T20 | SAME (spec §22 "Delta R309-R329") | Spec's 0.649 V tap confirmed by calculation; VM is +VBUS less the 10R drop (spec: calibrate at ≈ 0.63 V). |
| **Comparators.** IC14-IC18 LM139 / LCM2901 (5 quads), + input = DET, − input = tap, open-collector output on the LED anode node, V− = −17 V | U31-U35 / U38-U42 LM2901B on ±VM, `cmp(DET, T_k, node)`: + = DET, − = tap, output = LED k's anode | SAME (spec §22: LM2901B for the 34 V rail span) | — |
| **LED strings.** LD1-LD10 green (−20…−2 dB) from current source TR15 to −17 V; LD11 green (0 dB), LD12-LD16 amber (+2…+10), LD17-LD20 red (+12…+18) from TR16 to −17 V; comparator k shorts LED k's anode to −17 V, so the source current is constant (manual p.62 / p.65) | String A D29-D38 (green −20…−2, source Q2 at D29's anode, D38 cathode on −VM), string B D41-D50 (green 0, amber +2…+10, red +12…+18, source Q3); R side D57-D66 / D69-D78 with Q4 / Q5 | SAME (spec §22) | Colour split identical: 11 green / 5 amber / 4 red. |
| **Current sources.** TR15 / TR16 A970GR (2SA970), R330 / R331 75R emitter, D12 / D13 1N4148 from +17 V, R332 27K to −17 V: ≈ 0.6 / 75 ≈ 8 mA | Q2-Q5 BCP53-16 SOT-223, R171 / R173 / R208 / R210 120R, D27 / D28 / D39 / D40 / D55 / D56 / D67 / D68 1N4148 pairs, R172 / R174 / R209 / R211 27K: 4.2-5.7 mA (4.9 typ) | RECORDED (spec §22 "Current source (2026-10-23)"; `docs/reviews/master_parts_review.md`) | Under the LM2901B's 6 mA guaranteed sink. |
| **Meter supply and ground.** R307 / R308 10R + C305 / C306 47 µ/25; METER GROUND separate (own loom conductor, R340 link to ground on the sheet; CN5-2 at the power connector) | R5 / R6 10R + C5 / C6 47 µ/25 → ±VM; GNDM joined to GNDA only at the star (NT2); 100n per comparator / TL072 (C154-C189) | SAME (spec §22 "Delta R307 / R308, C305 / C306"; §26) | — |
| **Op-amp types, sheet 3.** TL071 (IC12), LM139 / LM2901 | TL072HIDR (U29 / U30 / U36 / U37), LM2901BIDR | RECORDED (spec §22, MG9 / MG16) | — |

### Sheet 4 — ED2780 sht 4: BVE option (programme links, control-room mute, pre/post phones)

| Delta (sheet, refs, value / topology as read) | Ours (refs, value / topology) | Status | Note |
|---|---|---|---|
| **BVE option switches.** S6-S9 illuminated latching keys "BVE", "MON 1/L", "MON 2/R", "MUTE" (poles A / C, lamp pins 7 / 8), wired to CN6 (20-way to the BVE board) | None | N/A — not named in console_architecture §6; the base Delta has none either (sheet 4 is an option, LK1 / LK2 "break for BVE" on sheet 1) | — |
| **CN4 (14-way).** BVE MIX L / MON L / BVE 2TRK L / BVE 2TRK R / MON R / BVE MIX R on even pins 4-12, odd pins ground, 13 / 14 ground | The monitor select is on-board (SW3) | N/A | — |
| **CN6 (20-way).** Switch poles on 1-12, 15 / 16 ground, 17 / 18 CRM L and 19 / 20 CRM R with "programming links: control room mute, pre/post h/phone socket" | No C/R cut; phones always from CRSB (ahead of the C/ROOM pot and the DIM resistors) | N/A (option). A C/R cut key is nowhere in our spec; CS7 added DIM only | The Delta's phones can be linked pre or post the C/R mute; ours are pre everything. Document only. |

### Tech Manual circuit descriptions (p.61-65) and system pages — points checked against the sheets and ours

| Manual statement | Sheet reading | Ours | Status |
|---|---|---|---|
| p.64: insert send level −10 dBV ≈ −7.8 dBu, chosen for headroom; mix fader 0 dB at the top | Sheet 2 "−10 dBV / −7.8 dBu", IC3-A +6 dB | ≈ 0 dBu at the insert, fader "0" mark −10 dB with a +9.9 dB post-amp | RECORDED (spec §4-5; delta.md T6 / T8 / T21) |
| p.64: insert return goes directly to the mix fader and the mono summing amp (R21 / R121, −3 dB) | Sheet 2 | Return buffered (U2B / U4A); mono from POST_L / R | RECORDED (spec §4, §6) |
| p.64: S1 poles D / E switch a 12 dB attenuator; the monitor buffers IC7 / IC19 have their gain switched by S1 | Sheet 1 / 2: 1K2 / 430R (−11.6 dB); receiver T network (−4.1 / +6.3 dB) | No operating-level switch | UNRECORDED (item 2) |
| p.64: PFL switching with J111 FETs (sheet says J112), detector IC10-B / TR13 / TR14; D4 holds TR6 / TR8 off, R40 / R140 bias TR5 / TR7 on | Sheet 1 | DG413 + LM393B | RECORDED |
| p.65: second PFL inverter's anti-phase virtual earth on the motherloom beside the PFL bus | Sheet 1: pin 28 on IC9-B's − input | Pin 28 unused (PFLN) | RECORDED (spec §18; CS5) |
| p.65: C/R buffers IC8 with discrete outputs drive 8 Ω phones and a power amp; separate supply decoupling C36 / C37; ground separate | Sheet 1 | LME49600 phones amp, DRV135 C/R outputs, ±VP, PHONESGND | RECORDED (spec §20-21) |
| p.65: R42 / R142 with R90 / R190, S3C / S3D, S4A / S4B dim (−20 dB) or cut the monitors on talkback | Sheet 1 | DIM key (CS7); no cut | RECORDED (CS7) |
| p.62 / p.65: meter = precision half-wave rectifier, average R / C and peak C selected by a jumper, comparators that sink the source current, calibration preset "0 = +4 dBu, peak response", separate meter ground on the 20-way loom | Sheet 3 | Full-wave + precision peak, same ladder / drive, GNDM | RECORDED (spec §22) |
| p.63: GND CANCEL joined to every module's ground by 10 Ω except the LH master; used by the aux summers | Sheet 1 R220 10R (RH master) | No master tie, 100K keeper, every summer referenced | RECORDED (Decisions; spec §3) |
| p.29: CPS150 external PSU; motherloom and output looms are IDC ribbon | — | External PSU (psu_spec.md), 34-way IDC motherloom | SAME in kind |
| p.114 / p.128: SRC 5-way (10-way for 32 ch) power connector; master rear connectors: XLR pin 2 hot; mono / aux / C/R outputs ground-compensated TRS (ring = ground sense); inserts tip = return, ring = send; 2-track returns balanced TRS | — | NC7MD-LX 7-pin; XLR pin 2 hot; balanced TRS (ring = cold) on aux 5 / 6 and C/R, mono on XLR; inserts tip = send | XLR SAME; outputs RECORDED (G2b); inserts UNRECORDED (item 1) |

---

### UNRECORDED discrepancies for sign-off

1. **Insert jack tip / ring assignment.** Delta: tip = insert return, ring = insert send, on the channel inserts (manual
   p.124, Deluxe input table) and the mix inserts (p.128; ED2780 sheet 2 JSK1: the long contact to C55 / the fader, the
   middle one to the summer output). Ours: tip = send (J1 / J2 T = MIX_L_SEND through R16 / R26 75R, RN normal), ring =
   return (MIX_L_RETRAW), the same convention on the strip (strip spec §7: "R11 75R ── J2 tip (send)"), the groups' sub inserts and
   the jig. Consequence: an insert lead or patchbay wired to Soundcraft's Delta-era convention arrives reversed (send into
   the outboard's output); the normalling still works. Most current desks (Mackie, A&H, Soundcraft Ghost and later) use
   tip = send, so ours is the common one. Recommendation: **keep, document only** — one line in master spec §4 and the
   strip spec's insert section: "tip = send, ring = return (the Delta is the other way round: ring = send, p.124 / p.128)".

2. **No +4 dBu / −10 dBV operating-level switch.** Delta: S1 (6 poles) pads both mix post-amps by 11.6 dB (R15 / R16
   1K2 / 430R, R115 / R116) and raises the four monitor receivers' gain by 10.4 dB (6K8 / 20K / 2K2 T networks) so the
   control room and meters stay at −2 dBu; the 2-track return gets +12 dB for −10 dBV tape. Ours: fixed gains
   everywhere: main XLRs at −0.8 dBu for 0 dBu in (fader "0", pan centre; delta.md §2), EXT receivers unity (U17A / U17B
   4 × 10K) with no gain option. Consequence: a −10 dBV (−7.8 dBu) DAW or tape return on EXT monitors 7.8 dB below the
   mix, and the main outputs cannot be set to a −10 dBV destination without the destination's own trim. Not a fault
   (DAW interfaces take +4 dBu; the C/ROOM pot covers the EXT difference). Recommendation: **keep, document only** in
   spec §17 / §7 ("no operating-level switch; EXT expects +4 dBu; fit Rg on the EXT receivers' 10K legs if a −10 dBV
   source is ever the norm" — the 4 × 10K bridge can take a gain of 2.45 by changing R85 / R90 and R87 / R92 to 24K3
   0.1 %, 2 resistors per side, if wanted later).

3. **Peak-meter release time described as "Delta-like".** Delta: C301 10 µF / 35 V discharged by R306 22K: τ ≈ 0.22 s
   (the manual's spec sheet quotes the peak decay separately; delta.md T18 "decay 250 ms / 1.2 s"). Ours: C160 / C178
   1 µF with R146 + R147 = 550K: τ ≈ 0.55 s; spec §22 calls that "(0.55 s, Delta-like)". Consequence: documentation
   only — ours holds a peak about 2.5× longer than the Delta's, which is a reasonable choice (slower fall is easier to
   read) but not the Delta's number. Recommendation: **keep the 0.55 s, correct the wording** in spec §22 to "0.55 s
   (Delta: ≈ 0.22 s, R306 / C301)".

4. **Remote meter header pin order and supply.** Delta CN8: 1 METER L, 2 ground, 3 +17 V (+VL), 4 METER R, 5 −17 V.
   Ours CN4: 1 MTR_L, 2 MTR_R, 3 +VM, 4 GNDM, 5 −VM (meter rails and meter ground, not the logic rails). Consequence:
   none in use (a future meter bridge is ours to wire); a Delta meter bridge would not plug in, which no one intends.
   Recommendation: **keep, document only** (spec §22: "pinout our own, not the Delta's CN8").

5. **delta.md's reading of the monitor-select receivers.** `docs/console_survey/delta.md` "Monitoring" describes IC7 /
   IC19 as "43K / 43K in, 20K / 22K, 33p" and the 2TRK return as "switched for −10 / +4" without the mechanism. As
   read: the − leg is a 6K8 + 20K T with 2K2 to ground through S1 (−4.1 dB open, +6.3 dB closed), the + leg 22K; the
   bridge is therefore not ratio-matched (26.8K vs 22K), which the Delta tolerates because the sources are its own
   balanced outputs. Consequence: documentation only (it does not touch our circuit). Recommendation: **document only** —
   add the T-network reading to delta.md T17 / Monitoring.

Everything else on the four sheets is either the same as ours (motherloom pins 1-33, XLR pin 2 hot, meter ladder /
comparator / LED-string / current-source architecture, average ballistics, meter tap, EXT select, PFL to both sides,
meters following the monitored signal, 0.1 µF local decoupling) or a departure already written down (M1 modules,
OPA1612 / OPA1656 / TL072H / LM393B / LM2901B / DRV135 / LME49600 / DG413 parts, 4K7 summing with ground cancel and
re-inverters, no master-end GCANCEL tie with the 100K keeper, insert level and return buffer, +9.9 dB post-amps,
post-fader mono without a mono fader, DRV135 outputs with 22R / sorted 10 µF / Sense loop / mute relays and the
power-on mute, buffered 1M EXT receivers, separate SOLO LEVEL and PHONES level, flashing rude-solo LED, PFLDET clamp /
debounce / hysteresis, DIM (CS7), full-wave meter detector with follower and 470R, BCP53 at 4.9 mA, pin 34 as +V, wing
PTCs / SS54 / star stud / net ties, 1R audio-rail feed, 2R2 phones feed), or Delta-only and explicitly excluded
(talkback, oscillator, +48 V, the BVE option and its C/R mute / pre-post phones links; the operating-level switch is
item 2 above).

Work files: `work_master/s1_*.png`, `s2_*.png`, `s3_*.png`, `s4_links.png` (300 dpi crops), `manual/p2-11..15.png`,
`manual/p3-23.png`, `manual/m28_src.png`, `manual/m30_table.png`, `manual/m34_table*.png`, `work_master/master_comps.txt`
(every master ref with its pin nets, from `master.net` via `work_master/netparse.py`).


---

## Part D: Venue input ED2911A / B, Venue stereo input ED2915A / B, Delta dual line input ED2776 (feature level)

**Sheets read** (every stage and notes box, from `ref/Sndcft_DeltaDLX_Schems.pdf` rendered at 300 dpi; crops in
the reader's scratch crops, not in the repo):

| Sheet | PDF p. | Title block | What it is |
|---|---|---|---|
| ED2911A | 1 | VENUE INPUT sht 1 of 2, DCB, issue 3.01, 24/01/00 | mic / line input, HPF, 4-band EQ, insert, peak, PFL, ON, fader, aux 1-6, pan, routing to 8 groups |
| ED2911B | 2 | VENUE INPUT sht 2 of 2 | mute block (2 × J112 + 2 × TL072), mute-group keys M1-M4, CN6 10-way mute loom, ±VL |
| ED2915A | 3 | VENUE STEREO INPUT sht 1 of 2, JH, issue 2, 20-3-92 | two selectable stereo line inputs, gain, Ø (L), width control, 3-band EQ, EQ switch, power, CN1 |
| ED2915B | 4 | VENUE STEREO INPUT sht 2 of 2 | stereo peak detector, PFL, mute, fader post-amps, pan (balance), mono sums, aux 1-6, routing, mute-bus keys |
| ED2776 | 5 | DELTA DUAL LINE INPUT, JH, P5 2/8/89 | two independent mono line channels: gain, 3-band EQ, PFL, ON, rotary fader, pan to MIX, aux 1-6 |

These modules are not the parent of our strip (the Theatre input ED3344A-C / ED3151 is), so the comparison is at
feature / topology level. "Ours" = strip v5.5 (`tools/gen.py`, `channel_strip_schematic_spec.md`), group (returns:
`stereo_return()` in `tools/gen_group.py`, `master_lib.receiver()` / `stereo_in()` / `level_buffer()` / `routing()` /
`afl()`), master (`tools/gen_master.py`, `master_section_spec.md`).

**Status key:** SAME = same circuit or value; RECORDED = a deliberate, documented departure (citation given);
UNRECORDED = a Delta technique or value that differs from ours with no decision on record (collected at the end);
N/A = a feature we don't have and never specified (mic stage, +48 V, SUB 5-8, mute groups, stereo-input-only
features) — pointer given; UNREAD = could not be read, with what was tried.

Pin numbers of Delta PVA2-style keys are as printed; the Delta draws the common as the middle pin (2 / 5), the same
convention as our SW parts (pin 2 / 5 common).

---

### 1. ED2911A — Venue input, sheet 1

| Delta / Venue (sheet, refs, value / topology as read) | Ours (refs, value / topology) | Status | Note |
|---|---|---|---|
| **Mic stage:** XLR CN1 / XLR-1..3, 2SB737 pair TR1 / TR2 with D1-D4 1N4148, R8 / R9 4K7, R12 / R13 10K, C29 47n, VR1-A 5K RD-law gain, R10 2K7, R11 10R, R14 2K7, C6 / C7 220/6.3, IC1-A / IC1-B TL072 (R15 2K7 / C8 12p, R16 22K / C9 15p, R17 22K), C10 47/25, R18 47K; S1-A/B +48 V; transformer pads Z60 / Z61; C3 / C4 / C5 680p RF, R4 / R5 6K8, R3 2K2, C1 / C2 47/63, R6 / R7 22K | none (line only) | N/A | `docs/studies/delta_clone_comparison.md` §1: Theatre input without the mic stage. |
| **Line input jack and legs:** JSK1 TRS; tip → R1 15K, ring → R2 15K; S2-A / S2-B / S2-C (box "LI", the LINE key) select the line legs or the mic stage output into IC2-A; the jack's tip / ring normals go to CN5 1 / 2 (2-pin link) | J1 NJ6FD-V on the jack board, normals short tip and ring to GNDA when empty; tip / ring → CN3 link → D18 / D19 BAV199 clamps → R10 / R112 1M to GNDA, R110 / R111 220R, C94 / C95 100p, U16A / U16B OPA1656 followers, R113 / R114 100R build-outs | RECORDED | Receiver: `docs/studies/ground_study.md` G3 (buffered, 1M per leg, CMRR 54 dB vs a 1K source); clamps CS4; CN5 (a line-input normalling link, use not shown on this sheet) is a Venue frame feature we don't have. |
| **Line input stage:** IC2-A TL072 differential amp, R19 4K7 (−) / R20 4K7 (+) after the 15Ks, R22 3K3 from + to ground; feedback R21 3K3 from IC2-B (buffer) whose input is the wiper of VR1-B 5K RD-law from IC2-A's output through R23 150R + R24 330R to ground, R89 3K3 wiper to ground; S2-D (LINE key, 4th pole) shorts R24. Input impedance per leg ≈ 15K + 4K7 (+ 3K3 on the + leg) ≈ 20-23K. Gain = (3K3 / 19.7K) / k: −15.5 dB at the top, +15.2 dB at the bottom with R24 shorted (line), +5.6 dB with R24 in (mic). Output marked −5 dBu. | U1A OPA1612 unity inverting bridge R6-R9 10K 0.1 % with C7 / C78 33p (balanced), fed from the followers; then a separate inverting gain stage U1B, R45 / R46 2K2 + RV9 B10K CD: −15.0 … +14.8 dB, 0 dB at the detent | RECORDED | `docs/studies/delta_clone_comparison.md` §2 row "Input" / "Gain" and §6: the Delta line topology was simulated for the same range and rejected (4.7 dB noisier). New literal fact: the Venue sheet shows S2-D shorting R24 in LINE mode, which gives the Delta line range −15.5 … +15.2 dB — the same ±15 dB as our decision 2 (delta_clone §3 wrote "mic/line switch wiring not fully traced"). Document only. |
| **Ø:** S3-A / S3-B swap the two legs between the 15Ks and R19 / R20 | SW15 swaps BUF_T / BUF_R between the followers and the 10K bridge | SAME | |
| **RF / input ground:** no RF caps on the line input (680p only on the mic). Jack sleeves (JSK1 line, JSK2 insert, JSK3 direct out "INPUT GROUND") and XLR pin 1 sit on an INPUT GROUND net joined to the module ground by **R76 10R** | C8 / C9 100p to CHASSIS at J1; J1 / J5 sleeves on CHASSIS (plated standoffs to the panel), J2 insert sleeve on GNDA directly | RECORDED / UNRECORDED | Sleeves on chassis: `docs/studies/ground_study.md` G2 (and §5.3 simulated the "GNDA via 10 Ω" variant: better than chassis for a TS cable, worse for pseudo-balanced TRS; chassis chosen). The **insert / direct-out sleeve through 10R** was not evaluated (G2 says inserts keep GNDA): see U1 at the end. RF caps: ours better (G3, C94 / C95). |
| **HPF:** IC3-A TL072 Sallen-Key, C12 / C13 47n, R27 33K (output to the mid node), R26 39K to ground, gain 1 + R85 4K3 / R84 10K = 1.43 (+3.1 dB); S4-A / S4-B short both caps when out; C11 47/25 + R25 47K in, C14 47/25 + R28 47K out, level −2 dBu. fc = 1 / (2π √(33K·39K) · 47n) = 94 Hz | sweepable KHN high-pass U5A + U15, RV16 A10K dual, 21-403 Hz, unity, Q 0.707 (R100-R109, C85-C88), SW11 | RECORDED | `docs/proposals/hpf_proposal.md` H1-H4 (strip v4.3); the +3 dB gain rejected in `docs/studies/delta_clone_comparison.md` §2 (decision 3). Same stage as ED3344A. |
| **EQ, 4 bands:** HF IC3-B: VR2 10K lin CD, C32 / C15 4n7, R87 5K6, R30 6K8, C16 33p across R31 33K, R29 33K. HI MID IC4-A "600 Hz-10 kHz": VR4 10K lin CD, VR3-A/B dual 100K revlog, C17 3n3, C18 1n5, R34 / R32 6K8, R33 / R35 22K. LO MID IC4-B "150 Hz-2.4 kHz": VR6, VR5 dual 100K revlog, C19 15n, C20 6n8, R38 / R36 6K8, R37 / R39 22K. LF IC5-A 5532: VR7 10K lin CD with C33 150n across, R88 / R86 3K3, R42 1K5, C34 2u2/50, R40 / R43 22K, C21 100n, R41 5K1; C22 47/25 + R44 47K out | U5B HF (R50 / R51 33K, C41 33p, C42 / C43 4n7, R52 5K6, R53 6K8, RV10); U6A / U6B mids as KHN band-pass (U12-U14, RV12 / RV14 A10K dual; 392R / 13K / 4K99 and 430R / 13K / 4K22; C44-C47) with R54 / R55, R58 / R59 22K and C69-C72 10p; U7A LF (R66 / R67 22K, C73 22p, R62 / R63 3K3, RV15, C48 150n, R64 1K5, C49 2.2u film, C50 100n, R65 5K1) | SAME / RECORDED | Values identical to ED3344A (ours); the mid bands' Wien + 100K C-law replaced by KHN + A10K (Decision "Mid-band tuning"), ranges retuned to the Delta's measured ones (EQM1, strip v5.5). Our 10p / 22p stability caps are `docs/reviews/strip_parts_review.md` T1-T11 (the Venue has only C16 33p). |
| **EQ switch:** S5 two poles. S5-B: insert-send source = EQ out (C22) or the EQ-input node (bypass). S5-A: the EQ's input (HF pot end / R29) = that node (EQ in) or **ground** (EQ out). No EQ LED | SW12 pole A: EQSEL = EQ_O6 (latched) or EQIN (bypass), pole B: +VL → R69 4K7 → D5 green EQ LED. The EQ input (JP6 → EQIN) stays driven when bypassed; the idle EQ output EQ_O6 floats at the switch | UNRECORDED | The Delta grounds the idle EQ input so the bypassed EQ carries no signal (no crosstalk from the idle chain, no load change). Ours keeps the EQ running on HOUT while bypassed. Consequence small: the idle EQ output is the same programme, EQ'd, 1 pin away at SW12. See U2. The LED pole was the Theatre's choice (`docs/studies/delta_clone_comparison.md`: SW3 + green EQ LED). |
| **Insert and position links:** JSK2 TRS, R45 75R send, return normalled to send; LK66 / LK68 / LK70 = post-EQ (standard), LK65 / LK67 / LK69 = pre-EQ (note 1); CN7 "I/P CHANNEL METERING" taps the post-insert node; C23 47/25 DC block after the return | JP5 / JP6 / JP7 solder jumpers (1-2 post-EQ, 2-3 pre-EQ), R11 75R, J2 normalled, C10 33 µF NP + R12 47K, R99 1K + C84 100p, U7B follower, then C11 100 µF NP + R13 47K to PRE | SAME / RECORDED | Same 3-link matrix. Our return buffer U7B / R99 / C84: T8 (`docs/reviews/strip_parts_review.md`); no meter-bridge tap (`docs/studies/delta_clone_comparison.md` §2 "Meter-bridge out: leave out"). |
| **Peak detector:** tapped at the EQ-switch output (pre-insert): R70 470K → C27 2u2/50 → TR3 2SC2240BL (R71 56K to −17 V), R72 680K from +17 V, C28 2u2/50 hold, TR4 2240BL → LED1 PEAK red via R73 4K7 from +17 V, R74 1K; runs on the raw ±17 V rails | five taps RECV / GOUT / EQOUT / PRESRC / FPOST through 1K (R39, R128-R131) into BAV99 D1 / D12-D15, both polarities; LM393B U4 / U18, +18.4 dBu, ~150 ms hold; red / green bicolour D2 with Q3-Q5 (MET1); on +VL / −VL | RECORDED | CS1 (`docs/proposals/cs1_proposal.md`), K3, MET1; threshold discussion in `docs/studies/console_survey.md` T18 / §4.5. The Venue reads one point (post-EQ, pre-insert; the Theatre read post-insert): our EQOUT and PRESRC taps cover both. |
| **PFL:** S8-B pole: common → PFL+ (pin 27, latched) or ground; R46 22K from the post-C23 node **and R108 22K from the pre-C23 node** both into the key's common; S8-A: +17 V → R47 100K → PFL DET, LED2 red; PFL− (pin 28) ends on a pad "Z2" only | C96 2.2 µF film → R32 22K → SW3 → PFL (27) or GNDA; SW3 pole B: +VL → R33 100K → PFLDET, R34 4K7 → D3 red | SAME / UNRECORDED | Same 22K / 100K / LED. The second 22K (R108, across C23 to the same key) is read but unexplained (two 22Ks in parallel at audio = 11K, +6 dB on PFL, and a DC path around C23); not on the Theatre, not for us. See U3 (document only). Pin 28 unused here as on ours (spec §2.4; CS5 note). |
| **ON key:** S7-A is **in the audio path**: common → fader / pre-fade node; latched (2-1) = passes MUTE OUT, released (2-3) = grounds the fader feed. LK47 bridges MUTE IN → MUTE OUT when the mute system is not fitted (note 2: "fit LK46 when mute system not used; omit LK46, fit TR5, R90 when used"); S7-B / S7-C switch LED3 green ON, driven by TR5 C2240BL (R90 100K, C42 10n/100V) from the mute logic's ON LED CONTROL | SW4 pole A drives the J112 gates (MSW = −VL latched / GNDD released → R42 220K / C28 100n → Q1 / Q2 MMBFJ112 shunts, R16 / R17 4K7, U3B follower); pole B: +VL → R43 4K7 → D4 green | RECORDED | Decision "ON switch, green LED … same J112 soft-mute circuit" (`docs/studies/delta_clone_comparison.md` §3 decision 5, from ED3344B / C). The Venue's local ON is a hard switch (clicky, −∞), its soft mute serves only the mute groups (ED2911B). Document only. |
| **Fader + post-amp:** fader via CN (SEND / GND / RET), C24 2u2/50, R48 100K, IC6-B 5532 non-inverting R50 4K7 / R49 2K2 = +9.9 dB, C25 100p, R51 75R build-out; C35 100n "local decouple"; C26 220/6.3 to the DIRECT OUT jack JSK3 (−2 dBu, fixed post-fade, sleeve on INPUT GROUND) and to the POSTFADE line | RV1 PTB0143 A10K, C13 2.2 µF film, JP1 / J3 VCA option, R18 100K, C82 10p, U2A OPA1612 R19 4K7 / R38 2K2 (+9.9 dB), C14 100p, C15 100 µF NP + R35 47K → POST; direct out separate: aux 6 pot via SW13 DIR → U8A, R71 75R, C52 33 µF NP, J5 impedance-balanced (R72 47K, R73 75R) | SAME / RECORDED | Post-amp identical. Direct out: Theatre style with DIR (decision 7, `docs/studies/delta_clone_comparison.md`); Venue's is fixed post-fade, unbalanced, 6.3 V polar cap. No build-out on U2A: strip stability review T1-T11 (≥ 69.9°) with C82. Couplers: F1-F4. |
| **Aux 1-6:** six 20K LOG pots VR8-VR11, VR13, VR14 with R64-R69 22K; push-on links J1-J3 (aux 1), J4-J6 (aux 2): POST / PRE-FADER / PRE-EQ; J7-J8, J9-J10 (aux 3, 4): POST / PRE-FADER; aux 5-6 fixed POSTFADE; note 3: J2 / J5 (aux 1, 2 pre-fade) and J7 / J9 (aux 3, 4 post) fitted as standard. No panel PRE keys | RV2-RV7 10K A with R20-R25 22K; SW8-SW10 PRE keys per pair (POST / PSRCn), JP2-JP4 PSRCn = MUTEOUT (pre-fade, after ON) or HOUT (pre-EQ); SW13 DIR on aux 6 | RECORDED | Theatre values and PRE keys (`docs/studies/delta_clone_comparison.md` §2 "Aux 1-6"); ON muting the pre sends: `docs/reviews/design_review.md` Q1. The 20K pots are a Venue / DLX value (lighter load on the post-amp: 6 × 20K = 3.3K vs our 6 × 10K = 1.67K); ours copies ED3344C's 10K A. Document only (within U9). |
| **Pan:** VR12-A / B 2 × 10K lin; IC6-A / IC6-B TL072 at 1.22× (R54 / R57 2K2, R53 / R56 10K) with R52 / R55 3K3 from each output back to its wiper (−4.4 dB law); no PAN key | RV8 RK09L B10K dual CD, U8B / U3A at 1.22× (R137 / R140 2K2 ∥ C105 / C106 22p, R138 / R141 10K), R136 / R139 3K3 law resistors; C79 / C80 10p; C16 / C17 100 µF NP; SW14 PAN (off: subs get POST) | SAME / RECORDED | CS2 (strip v5.4), `docs/studies/eight_groups_study.md` §1.3; PAN key = Theatre feature (decision 6). |
| **Routing matrix:** S9 MIX (R58 / R59), S10 1-2 (R60 / R61), S11 3-4 (R62 / R63), S12 5-6 (R80 / R81), S13 7-8 (R82 / R83), all 10K 1/8 W; released = resistor end to ground; no routing LEDs; CN2 pins 15/13/11/9/7/5/3/1 = GRP 1-8, 18/17 = MIX L/R | R26-R31 4K7 1 %, U9-U11 DG413 at the header (bus / GNDA), SW5-SW7 PVA2 logic + yellow LEDs D6-D8; pins 1/3/5/7 NC, reserved for SUB 5-8 | RECORDED | 4K7 (Decision "MIX/SUB summing resistors 4K7"), DG413 (Decision "Routing"), LEDs (Theatre), SUB 5-8 pins: `docs/studies/eight_groups_study.md` and the bus-pinout decision. |
| **Power / bus:** R77 / R78 10R, C30 / C31 220 µF/25 V, "MAIN GND"; +17 / −17 raw rails feed the peak detector and (via ED2911B CN6) the logic; R75 10R GND CANCEL to pin 26; CN2 34-way (34 = +48 V, 30-31 −17, 32-33 +17, even 2-16 ground, 19 empty, 27 / 28 / 29 PFL+ / PFL− / PFL DET, 20-25 AUX 6…1, 26 GCANCEL); CN4 ¼" spade | R1-R4 10R M25SI fusible, C1 / C3 220 µF, C2 / C4 100n, D16 / D17 PMEG4010CEH, C5 / C6 47 µF logic rails, NT1, R5 10R GCANCEL, CN1 (same map; 34 = third +V), CN4 spade | SAME / RECORDED | Fusibles CS6, rail diodes CS10, pin 34 as +V W1, logic rails from the bus through 10R + 47 µF (spec §2.2, ED3344B). |
| IC supply list IC1-C … IC6-C, C35 local 100n | 100n at every op-amp (C20-C36, C63-C68, C89 / C90, C92 / C93) | SAME | |

---

### 2. ED2911B — Venue input, sheet 2 (mute system)

| Delta / Venue (sheet, refs, value / topology as read) | Ours (refs, value / topology) | Status | Note |
|---|---|---|---|
| **Mute block (fitted only with the mute system, note 2):** MUTE IN → R91 4K7 → node X; **TR6 J112 shunt** from X to ground through **C41 47/25** (source on a cap: the FET carries no DC); **TR7 J112 series** from X into IC7-A TL072's virtual earth, R93 4K7 ∥ C40 33p (unity inverter); R92 22K from IC7-A's output to the TR6 source / C41 node; R100 680K TR7 gate to ground; second unity inverter IC7-B R94 / R95 4K7 ∥ C36 33p; C37 47/25 + R107 47K → MUTE OUT. Non-inverting overall. | PRE → R16 4K7 → M1 (Q1 shunt to GNDA) → R17 4K7 → M2 (Q2 shunt to GNDA, C81 10p) → U3B follower → MUTEOUT: two shunt J112s with their sources on GNDA directly, ≈ 86 dB (sim) | RECORDED / UNRECORDED | Our circuit is ED3344B/C's (Decision "JFET (J112) soft mute"; `docs/studies/delta_clone_comparison.md` "Same J112 soft-mute circuit"; keys / clicks `docs/proposals/gaps_proposal.md`). The Venue variant (series + shunt into a virtual earth, cap-isolated shunt source) is a different, deeper mute with no DC across the shunt FET: see U4 (document only; the DC-at-the-FET click is covered by `docs/proposals/gaps_proposal.md` keys.py and RV5). |
| **Gate drives:** R96 220K + C38 100n (τ 22 ms) → D7 1N4148 → TR6 gate, R99 680K gate bleed; R97 220K + C39 100n → D8 1N4148 (R98 22M across it) → TR7 gate, R100 680K. D7 / D8 isolate the gates: a −VL control pulls a gate to −16.4 V (FET off); +VL leaves the gate at 0 V through its 680K (FET on) | SW4 → R42 220K / C28 100n (22 ms) → MGATE for both Q1 / Q2, no diodes (one control, both gates the same way) | SAME / RECORDED | Same 22 ms ramp. The diodes exist because the two Venue FETs need opposite drives (shunt on / series off) and the mute logic (not the key) sources the drive. N/A for a shunt-only pair. |
| **Logic:** +VL → R104 100K and R103 47K pull-ups; TR8 BL (base: R101 4K7 from the diode-OR of the mute lines, R102 47K to −VL; collector = ON node), TR9 BL (base R105 220K from the ON node; collector = R104 node → R106 100K "ON LED CONTROL" → ED2911A TR5); the ON node and its inverse drive R96 / R97 | SW4 pole A: MSW = −VL (latched, on) or GNDD (released): the key is the whole logic; LED from pole B | N/A | Mute-group logic; `docs/studies/eight_groups_study.md` §2.5 (mute groups set aside, no loom conductors; console_survey §7). |
| **Mute groups:** keys S14-B / S15-B / S16-B / S17-A (M1-M4) → D9-D12 1N4148 → CN6 pins 4 / 3 / 2 / 1 = MUTE 1-4; CN6 10-way IDC: 5 / 6 LOGIC GND, 7 / 8 +17 V (+VL), 9 / 10 −17 V (−VL). Note 1: D7-D12 1N4148 or equivalent; note 2: all components omitted if the mute system is not used | none; +VL / −VL made on the strip from the bus (R3 / R4 10R, C5 / C6 47 µF) | N/A / RECORDED | `docs/studies/eight_groups_study.md` §1.4 (CN6 pinout) and §2.5 (cost: a second 10-way loom and a key row that doesn't fit 12U). Logic rails: spec §2.2. |
| Notes: "FOR DELTA DLX: do not fit SW12, SW13, R80, R81, R82, R83, C35. IC5 part changes to TL072" | our IC5-equivalent (LF) is OPA1612 | N/A | DLX = 4-group build (`docs/studies/eight_groups_study.md` §1.1). The DLX's LF stage drops the 5532 for a TL072 (cost); ours OPA1612 (decision 4). |

---

### 3. ED2915A — Venue stereo input, sheet 1

| Delta / Venue (sheet, refs, value / topology as read) | Ours (refs, value / topology) | Status | Note |
|---|---|---|---|
| **Inputs:** two stereo sources per module: LINE I/P A (JSK1 L, JSK2 R) and LINE I/P B (JSK3 L, JSK4 R, also via CN2 / CN9 and CN4 / CN10 with links J13 / J14, J11 / J12 for a rear feed); S1 "INPUT SELECT A / B" (S1-B / S1-D left, S1-A / S1-C right); every TRS normal grounds the empty jack's legs; all sleeves on SOCKET GROUND; S2-A / S2-B "LEFT PHASE" Ø on L only | per return one stereo pair: J4 / J5 (return 1), J6 / J7 (return 2) NJ6FD-V, R jack's tip / ring normals to the L jack (mono source feeds both), L normals to GNDA; sleeves on CHASSIS; no Ø | RECORDED | Returns: master spec §16 (feature list; "No balance or mute"); two returns per group instead of an A / B selector (RET1, `docs/reviews/feature_gaps.md`); sleeves G2 / G2b. |
| **Socket ground:** SOCKET GROUND (all jack sleeves + BKT1 "VR1 bracket" + BKT2 / BKT3) joined to main audio ground by **R74 10R** | balanced-input sleeves on CHASSIS bonded to the panel (standoffs), no resistor to GNDA on the module; the panel / pot brackets are chassis | RECORDED | `docs/studies/ground_study.md` G2 (and §5.3's "GNDA via 10 Ω" rows). Same 10R scheme as ED2911A R76; see U1 only for the unbalanced insert. |
| **Line I/P stage (per side):** IC1-A (L) / IC2-A (R) 072 diff amp, 4 × 22K input resistors fitted in one of two patterns (note: "if mute not used fit R1, R2, R101, R102 else fit R200-R203"): the alternative positions swap the diff amp's input polarity to undo the mute block's single inversion; R3 / R103 4K7 feedback from the IC1-B / IC2-B buffer, R4 / R104 4K7 + to ground, C28 / C128 12p across the feedback; VR1-A / B 5K rev log, R5 / R105 150R, R86 / R186 3K3 on the wiper. Gain (4K7 / 22K) / k: −13.4 dB (top) … +17.3 dB (bottom). Output "−2 dB" | `master_lib.receiver()`: R39 / R44 … 1M, R70 / R71 … 220R, 100p, U10 / U11 (return 1), U14 / U15 (return 2) OPA1656 followers, 100R, R40-R43 / R45-R48 (return 1) 10K 0.1 % bridges with 33p both legs, OPA1612; **no gain stage**: unity, then the level pot and unity buffers (R35 / R53 / R57 / R93 / R97 DNF = fit 2K2 for +10 dB) | RECORDED | Receiver G3b (`docs/studies/ground_study.md` §10); return gain range: master spec §16 ("unity … fit 2K2 for +10 dB"). The ±15 dB trim is a Venue / DLX stereo-input feature; ours has none on the returns (a hot or quiet return is set on the device). Document only (U9). |
| **Width control:** R190 / R193 / R194 / R195 5K1 cross-feeds, VR13 10K lin dual WIDE / MONO (R191 / R196 4K7), IC9-A / IC9-B TL072 with R192 / R197 2K4 feedback: continuous stereo-width / mono blend | none (the R jack's normals give mono from one plug; the PFL mono sum is 43K + 43K, R65 / R66 and R105 / R106) | RECORDED | Master spec §16 lists the return's controls (level, routing, PFL) and says "No balance or mute. Add a balance pot later if wanted". Width / mono blend not specified: a stereo-input feature of a line-input module, not of an effects return. Listed under U9 for the record. |
| **EQ IN:** C1 / C11 47/25 + R221 / R222 47K; S3-A: EQ input = signal (in) or **ground** (out); S3-B: L POST EQ = EQ out via C26 (in) or the signal (out); 3-band EQ per side: HF IC3-A / IC3-B (VR2 10K lin CD, C2 / C12 4n7, R8 / R108 4K7, R6 / R106, R9 / R109 22K, C4 / C14 33p), LF (VR5, R7 / R107 7K5, R85 / R185 5K1, C3 / C13 100n), MID IC4-A/B, IC5-A/B (VR4 10K lin CD, R10 15K, R11 / R12 22K, C5 10n, C6 15n, R14 1K, VR3 dual 100K revlog, R13 10K: a 2-op-amp swept mid); C26 / C27 47/25 + R84 / R184 47K out | no EQ on the returns | N/A | Master spec §16 (returns: level + routing + PFL). The same idle-input grounding technique as ED2911A S5-A (see U2, strip). |
| **Power:** R40 / R41 10R, C24 / C25 220U/25, CN11 3-pin (+17 / 0 / −17 sub-board feed); op-amp list IC1-C … IC10-C (IC8-E = TL074 pins 4 / 11); R75 10R ground cancelling resistor to pin 26; CN1: 32 / 33 = +17 V, 30 / 31 = −17 V, **34 open**, 29 PFL DET, 28 PFL−, 27 PFL+, 26 GCANCEL, 25 / 24 / 23 / 22 / 21 / 20 = AUX 2 / 1 / 3 / 4 / 5 / 6, 19 empty, 18 / 17 MIX L / R, 15 … 1 = GRP 1-8, even 2-16 ground; CN8 spade "MAIN AUDIO GROUND" | group: R1 / R2 10R fusible + 220 µF, 10R + 47 µF logic, D5 / D6 rail diodes, R 10R GCANCEL, CN1 same map with 34 = +V, spade | SAME / RECORDED | Confirms the ED3344C map (Decision "Bus = real Delta motherloom pinout"); the 1992 stereo input leaves pin 34 (+48 V) open, as a non-mic module should; ours ties it to +V (W1). |
| Notes: "FOR DELTA DLX: do not fit SW10, SW11, R80-R83" | — | N/A | 4-group build (`docs/studies/eight_groups_study.md`). |

---

### 4. ED2915B — Venue stereo input, sheet 2

| Delta / Venue (sheet, refs, value / topology as read) | Ours (refs, value / topology) | Status | Note |
|---|---|---|---|
| **Stereo peak detector:** R66 / R67 470K → C21 / C22 2u2/50 → TR1 / TR2 BL (R68 / R69 56K to −17 V), OR'd into TR3 BL (R70 680K from +17 V, C23 2u2/50 hold, R71 1K) → PEAK LED (LED1 red, switched through S5-C / S6-D-E with the PFL / ON LEDs, R72 4K7, TR10 BL, C32 3n3/100V, R47 680K) | returns have no peak / signal LED (the PFL key puts them on the master's meters) | UNRECORDED | Master spec §16 lists no indicator; a return at the receiver's ~+21 dBu clip is unindicated except via PFL. Document only (U9). |
| **PFL:** S5-B common → PFL bus or ground; with the mute system: R15 / R115 33K from L / R POST EQ (pre-mute) and link J7 → **PFL− (pin 28)**; without: R45 / R46 33K from the post-ON-switch nodes and J9 → PFL+ (note: "if mute used fit J7, R15, R115 else fit J21, J8, J9, J22, J10, R45 and R46"); S5-A: +17 V → R73 100K → PFL DET, LED via R72 4K7 | `afl()`: R65 / R66 (return 1), R105 / R106 (return 2) 43K + 43K → SW7 / SW11 → PFL (27) or GNDA; +VL → 100K → PFLDET, 4K7 → D3 / D4 red | SAME / UNRECORDED | Same mono-sum PFL (33K + 33K vs our 43K + 43K: §16 "(L + R) × 0.51"). The Venue uses **pin 28 (PFL−, the master's anti-phase virtual earth) as a polarity-correcting PFL input** when its inverting mute block sits between the PFL tap and the output. Ours is non-inverting everywhere (strip: PRE in phase with the tip; returns: unity), pin 28 NC (spec §2.4; `docs/studies/console_survey.md` §4.3 / CS5 note). Document only (U5). |
| **Mute (per side):** C7 / C17 47/25 → R204 / R207 4K7 → TR5 / TR7 J112 **series** into IC10-A / IC10-B TL072 virtual earth (R205 / R208 4K7 ∥ C201 / C203 33p: **one** inverter), TR4 / TR6 J112 **shunt** to ground through C202 / C204 47/25, R206 / R209 22K from the output to the shunt's source node; C207 / C208 47/25 out. Without the mute: J21 / J22 bypass to S6-A / S6-B (CHANNEL ON, a hard switch in each path), J8 / J10 to the fader | strip: see §2 (shunt pair); returns: no mute | RECORDED | Returns: master spec §16 "No balance or mute". Strip: Decision "JFET (J112) soft mute" (see U4 for the Venue variant). |
| **Mute-bus logic:** S12-A … S15-A (MUTE BUS 1-4) → D1-D4 1N4148 → R210 4K7 → TR8 BL (R211 47K), R212 47K, R213 220K → TR9 BL, R214 100K; S6-C (CHANNEL ON, logic pole); R216 / R217 2 × 220K + C205 / C206 2 × 100n (22 ms), D5 / D6 2 × 1N4148 with R218 22M, R215 220K, R219 / R220 680K gate bleeds; CN6 (the same 10-way mute loom) | none | N/A | As ED2911B; `docs/studies/eight_groups_study.md` §2.5. Legend box: S5 PFL, S6 CHANNEL ON, S7 MIX, S8-S11 GROUPS 1-2 … 7-8, S12-S15 MUTE BUS 1-4. |
| **Fader + post-amp (per side):** fader connector SND / RET / GND, C8 / C18 2u2/50, R16 / R116 100K, IC6-A / IC6-B 5532 non-inverting **R19 / R119 7K5 / R17 / R117 1K8 = +14.3 dB**, C9 / C19 100p, C10 / C20 100/10 (10 V polar) out, C31 100n local decouple; "−2 dB" | `level_buffer()`: C 2.2 µF film, R 100K, OPA1612, Rf 4K7 ∥ 100p, 10p at +, Rg DNF (unity; 2K2 = +10 dB); 220 µF NP + 47K out; RV4 / RV5 dual A10K level pots (not faders) | RECORDED | Master spec §16 (rotary level, unity buffers); the stereo input's +14.3 dB make-up (vs the mono input's +9.9) belongs to its fader law / −2 dB structure. Couplers F1-F4 (no 10 V polar caps). |
| **Pan / balance:** VR10-A / VR10-B dual 10K lin CD wired as a **balance** (gang A: pin 3 = L signal, pin 1 ground; gang B: pin 4 = R signal, pin 6 ground, wipers move oppositely); IC7-A / IC7-B 072 at 1.22× (R21 / R121 3K3 law to the wiper, R22 / R122 2K2, R20 / R120 10K): −2.7 dB each at centre, +1.7 dB / −85 dB at the ends | none on the returns; strip / sub pans use the same 1.22× + 3K3 network (CS2 / CS2b) | RECORDED | Master spec §16: "No balance … Add a balance pot later if wanted (dual B10K after the level pot, as the strip pan)". The Venue's balance is exactly that: the pan network with the gangs reversed. Document only (U9). |
| **Pre-fade mono sum:** R50 / R51 22K → IC8-A 074 (R52 15K: each −3.3 dB) → R53 22K → IC8-B (R54 22K ∥ C29 33p, unity) → MONO PRE; R223 100R → CN12 "TO METER OVERBRIDGE". **Post-fade mono sum:** R55 / R56 22K → IC8-C (R57 9K1: each −7.7 dB) → R58 22K → IC8-D (R59 22K ∥ C30 33p) → MONO POST | PFL junction only (43K + 43K passive) | N/A / RECORDED | A stereo input's aux-send source; our returns have no aux sends (master spec §16). Pointer U9. |
| **Aux 1-6:** VR6 / VR7 (aux 1 / 2) 20K LOG with R60 / R61 22K, links J1-J4 / J5, J6, J15, J16 select MONO POST / MONO PRE / LEFT (RIGHT) PRE / LEFT (RIGHT) POST; VR8 / VR9 / VR11 / VR12 (aux 3-6) 20K LOG with R62-R65 22K from MONO POST (J17 / J19) or MONO PRE (J18 / J20) | none on the returns | N/A / RECORDED | Master spec §16. |
| **Routing:** IC7-A (L) → R23 / R24 / R25 / R80 / R82 10K → S7-A MIX LEFT, S8-A GRP 1, S9-A GRP 3, S10-A GRP 5, S11-A GRP 7; IC7-B (R) → R123 / R124 / R125 / R81 / R83 10K → S7-B MIX RIGHT, S8-B GRP 2, S9-B GRP 4, S10-B GRP 6, S11-B GRP 8; released = resistor to ground | `routing()`: 4K7 1 % pairs, PVA2 SW4 / SW5 / SW6 (return 1: MIX, 1-2, 3-4), SW8 / SW9 / SW10 (return 2); released = GNDA; no DG413 on the group | RECORDED | 4K7 decision; 5-6 / 7-8: `docs/studies/eight_groups_study.md`. The group's return routing switches the resistor end directly with the PVA2 (strip style before the DG413 decision; `master_lib.routing` "strip-style routing switch, off grounds the resistor") — a recorded structure (master spec §16). |
| Notes box: "IF MUTE USED FIT J7, R15, R115 ELSE FIT J21, J8, J9, J22, J10, R45 AND R46" | — | N/A | Read; explained in the PFL row. |

---

### 5. ED2776 — Delta dual line input (two identical mono channels; channel 1 refs, channel 2 = R1xx / IC3-IC6)

| Delta (sheet, refs, value / topology as read) | Ours (refs, value / topology) | Status | Note |
|---|---|---|---|
| **Line I/P stage:** JSK1 TRS (normals ground the legs, sleeve SOCKET GROUND via BKT1 / R45 10R); R1 / R2 22K; IC1-A 072 diff amp, R3 4K7 feedback from IC1-B buffer, R4 4K7 + to ground; VR1 10K REV LOG, R5 330R, R47 6K8 on the wiper; "−2 dB". Gain (4K7 / 22K) / k: −13.4 dB … +16.5 dB. No Ø, no RF caps | strip: U16 followers + U1A bridge + U1B gain stage (−15 … +14.8 dB); returns: unity receivers | RECORDED | `docs/studies/delta_clone_comparison.md` §2 / §6 (Delta line topology rejected for noise); the gain range matches decision 2 within 1.5 dB. Same family as ED2915A's stage (22K / 4K7). |
| **3-band EQ:** HF IC2-A: VR2 10K lin CD, C5 3n3, R8 4K7, R6 / R9 22K, C6 33p; LF: VR5 10K lin CD, R7 7K5, R46 5K1, C4 100n; MID IC2-B: VR4 10K lin CD, C8 6n8, C7 3n3, R12 / R10 6K8, VR3-A / B dual 100K revlog, R11 / R13 22K (Wien band-pass as the Theatre's HI-MID with doubled caps, ≈ 300 Hz-5 kHz); C9 47/25 out | strip: 4-band (ED3344A values, KHN mids) | N/A | A simpler module's EQ; our strip EQ is the Theatre's (`docs/studies/delta_clone_comparison.md`). |
| **PFL / ON:** S1-B: R14 22K → PFL+ or ground; S1-A: V+ → R15 100K → PFL DET; LD1 red (S1-C). **ON: S2-B is a hard switch in the signal path** ("ON SWITCH"), LD2 green (S2-C), S2-A; "MIDI / DVE" CN2 with links J3 / J4 (a bypassable mute-module point) | strip: SW3 PFL (22K + C96, 100K, D3); SW4 ON → J112 soft mute, D4 green | SAME / RECORDED | PFL same values; ON: Decision (soft mute, Theatre); the ED2776 ON key (1989) is a hard switch like the Venue's. |
| **Rotary fader + post-amp:** VR11 10K LOG rotary, C10 2u2/50, R16 47K, IC5 NE5534 R19 4K7 / R17 2K2 (+9.9 dB), C11 100p, C13 15p comp; C12 220/25 out; J1 PRE / J2 POST aux-source links | strip: as §1 (U2A); returns: rotary dual A10K level + unity buffers | SAME / RECORDED | Post-amp identical to ours. |
| **Pan to MIX (passive):** VR10-A / B dual 10K lin CD, pin 3 / 4 = signal, pin 1 / 6 ground, **R20 / R21 3K0 from the signal to each wiper** (law resistors), wipers → R22 / R23 **8K2** → MIX L / R. Centre (my calculation, 8K2 into a virtual earth): 5K ∥ 8K2 / (3K0 ∥ 5K + 5K ∥ 8K2) = 0.62 → ≈ −4.1 dB; ends 0 dB. No group routing: GRP 1-8 header pins unconnected | strip / sub: active 1.22× buffers with 3K3 law resistors (−2.7 dB centre / +1.7 dB ends, CS2 / CS2b); 4K7 to the buses | RECORDED | CS2 chose ED3344C's active network; `docs/proposals/cs2b_proposal.md` records the parent's passive pan as ED2778A's 3K9 / 8K2 (−4.6 dB). ED2776 is another passive one at 3K0 / 8K2 (≈ −4.1 dB) with 8K2 (not 10K) MIX resistors (+1.7 dB into a 3K9 … summer). Document only (U9). |
| **Aux 1-6:** VR6-VR9 20K LOG + R24-R29 22K (aux 1-2 from J1 PRE / J2 POST; aux 3-6 via "INTERNAL SELECT FOR AUX 5-6" S5-A … S5-D), aux 5-6 grounded when not selected | strip: 10K A pots, 22K, PRE keys | RECORDED | Theatre values (`docs/studies/delta_clone_comparison.md`). 20K pots: U9. |
| **Power:** R40 / R41 10R, C20 / C21 220U/25V, C22 / C23 47n; R31 10R ground cancel; CN1 (same map, GRP 1-8 labelled on 15 … 1, 34 "+", PFL DET / PFL− / PFL+ on 29 / 28 / 27); CN4 spade; op-amps TL072 / TL071 / NE5534 | as §1 | SAME / RECORDED | |
| Notes box: empty | — | N/A | |

---

### UNRECORDED discrepancies for sign-off

1. **Insert / direct-out sleeves through 10 Ω (ED2911A R76 "INPUT GROUND", ED2915A R74, ED2776 R45).**
   Delta: every jack sleeve and the gain pot's bracket sit on a socket-ground net tied to the module's audio ground
   by 10R. Ours: balanced inputs / direct out on CHASSIS (G2), the insert jack J2's sleeve on GNDA directly; groups and
   master the same (`master_lib.insert()` S = GNDA). `docs/studies/ground_study.md` §5.3 evaluated the 10R variant for the line
   input only. Consequence: an earthed insert processor on an unbalanced TRS insert forms its loop straight through
   the module's GNDA; with 10R the loop current is limited but the drop appears in the send / return reference
   (the Delta accepts that). Recommendation: **keep** (G2 already assigns the insert to GNDA; our insert is
   normalled and a bench check with a real insert device is on the jig list); document only.
2. **EQ bypass grounds the idle EQ input (ED2911A S5-A, ED2915A S3-A).** Delta: pole A grounds the EQ chain's input when
   the EQ is out, pole B routes around it. Ours: SW12 pole A routes, pole B drives the green EQ LED (Theatre);
   the bypassed EQ keeps running on HOUT. Consequence: the idle EQ's output (same programme, EQ'd) sits one PVA2
   contact from the bypass path and the EQ's pots stay live on the signal; no noise or level effect (bypass and EQ
   paths are both driven by HOUT). Recommendation: **keep** (the LED is worth more than the ground; crosstalk at the
   switch is the same signal); document only.
3. **ED2911A PFL feed has two 22Ks (R46 post-C23 and R108 pre-C23) into the PFL key.** Read twice (crops a_pflsw,
   a_postins_r); no note explains it; the Theatre and ours use one 22K (R32, with C96 since K1). Consequence for us:
   none. Recommendation: **document only** (a Venue oddity; if it matters for a Venue module on our bus its PFL
   would arrive 6 dB hot).
4. **Venue mute block topology (ED2911B TR6 / TR7, ED2915B TR4-TR7):** series J112 into a virtual-earth inverter plus a
   shunt J112 whose source is on a 47 µF (no DC across the shunt FET), 22K from the output to that node, 680K
   gate bleeds, diode-isolated opposite-sense gate drives; vs ours (ED3344B): two shunt J112s on GNDA with 4K7s
   and a follower, ~86 dB. Consequence: deeper mute and no DC step from the FET's own node when it switches (our
   M1 / M2 sit a few mV off ground from U3B's bias, RV5 in `docs/reviews/project_review.md`; the click is within `docs/proposals/gaps_proposal.md`
   keys.py's result). Recommendation: **keep** (ours is the parent's, simulated and signed off; the Venue's exists to
   serve remote mute groups with a hard local ON key), but add the cap-isolated-source option to the open
   `docs/proposals/clicks_proposal.md` (RV5) as a zero-cost alternative to AC-coupling MUTEOUT should the bench show a click.
5. **Pin 28 (PFL−) as a polarity-correcting PFL input (ED2915B note, J7 / R15 / R115 when the inverting mute block is
   fitted; the 4 × 22K input resistors re-fitted in the swapped pattern to keep the output polarity).** Ours: every
   path non-inverting, pin 28 NC on all boards (spec §2.4; CS5: tying it to GNDA at the master is a free option).
   Consequence: none for our modules; a real Venue stereo input with the mute fitted would need pin 28 to be a
   PFL summer input on our master, which it is not (our master leaves 28 open). Recommendation: **keep / document**:
   add one line to the bus-pinout decision that pin 28 is a PFL input on Venue stereo-input modules, so a borrowed
   module isn't expected to PFL.
6. **Delta line-input gain range read literally:** ED2911A S2-D (LINE key pole) shorts R24 330R: line −15.5 … +15.2 dB,
   mic trim −15.5 … +5.6 dB; ED2915A −13.4 … +17.3 dB; ED2776 −13.4 … +16.5 dB. Ours −15.0 … +14.8 dB (decision 2).
   `docs/studies/delta_clone_comparison.md` §2 left the mic / line switch "not fully traced". Consequence: none (same range).
   Recommendation: **document only** (close the open note in docs/studies/delta_clone_comparison.md).
7. **Venue peak detector tap = post-EQ switch, pre-insert** (ED2911A "TO PEAK DETECT" from S5-B's common), where the
   Theatre's is post-insert. Ours (CS1) reads both EQOUT and PRESRC plus RECV / GOUT / FPOST. Consequence: none.
   Recommendation: **keep**; document only.
8. **Return-module indicators:** the Venue stereo input has a stereo peak LED (ED2915B TR1-TR3); our returns have no
   indicator; a return at the receiver's ~+21 dBu clip shows only on PFL. Consequence: a hot reverb return clips
   unseen if nobody PFLs it (the master meters read the mix). Recommendation: **keep** for now (eight returns ×
   LED + detector = 8 × ~12 parts and a panel hole each; PFL covers it); document in master spec §16.
9. **Stereo-input features not on our returns, for the record** (all read, none decided against by name): input A / B
   select with a rear feed (ED2915A S1, CN2 / CN9), Ø on L (S2), ±15 dB gain trim (VR1), width / mono blend (VR13,
   IC9), 3-band EQ (IC3-IC5), balance built from the pan network (VR10, IC7), pre / post mono sums (IC8), six aux
   sends from the mono sum (VR6-VR12), 20K log aux pots (also ED2911A / ED2776), passive 3K0 / 8K2 pan with 8K2 MIX
   resistors (ED2776). Master spec §16 defines the return as level + routing + PFL and names balance as a possible
   later add. Recommendation: **document only**: one sentence in §16 that trim, Ø, width / mono, EQ and aux sends
   were seen on the Venue stereo input and left out (an effects return, not a line input; the strips take line
   sources), so the omission is a decision rather than an oversight.

**Not found:** nothing in these five sheets contradicts a signed decision or the bus map; the Venue input's EQ,
HPF, post-amp, pan law, aux values, PFL, ground-cancel and power are the Theatre's (ours), and the ED2915A CN1 map
(32 / 33 +17 V, 30 / 31 −17 V, 34 open, 1 / 3 / 5 / 7 GRP 8 / 7 / 6 / 5) confirms the ED3344C order and the SUB 5-8
reservation.

**UNREAD:** none. Every value above was read on a 2-4× crop of the 300 dpi page; the three items that needed a
second look (ED2911A S5 wiring and R108, ED2911B R92's node, ED2915A CN1 rail pins) were resolved on 4× crops
(a_s5, a_links, a_pflsw, b_fets, c_rails3). The ED2915A alternative-resistor positions (R1 / R2 / R101 / R102 vs
R200-R203) were read from the note and the mute's single inversion; the four resistor outlines are drawn stacked and
their leg assignment is inferred, not traced pin by pin.
