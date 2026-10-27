# MET1 / RET1 review (2026-10-26)

An independent check of the two changes applied on 2026-10-26: the strip's red / green signal / overload LED (MET1,
strip v4.7) and the group's second stereo return (RET1, master spec v0.12). Two reviewers worked from the generators,
netlists, placed boards and the manufacturers' datasheets, not from the change notes. Every finding below was checked
again against the source before it was written here.

**Result: no faults.** Every pinout checks end to end, return 2 is the same circuit as return 1 part for part, and
nothing else on either board changed. Three small fixes are applied. Four changes are proposed for your sign-off (P1–P4),
because they touch a signed circuit, cost parts, or change the panels.

## Checked and correct

- **MET1 pinouts:**
  - **WP3VEGW** (Kingbright drawing, p. 1): pin 1 red anode, pin 2 common cathode, pin 3 green anode, leads 0.5 mm
    square at 2.0 mm, holes Ø0.9. This matches `Device:LED_Dual_AKA` and the `LED_D3.0mm-3_P2.00mm` pads 1 / 2 / 3.
  - **MMBT3906LT1G** (onsemi): pin 1 base, 2 emitter, 3 collector, as `Q_PNP_BEC` and the netlist.
  - **BAT54W:** pin 1 anode, 3 cathode, 2 NC. D11 clamps negative swings only.
  - **LM393B** (TI SLCS005, table 4-1): every U17 pin, supply and decoupler as intended.
- **MET1 logic and ratings:**
  - Q3 / Q4 saturate with forced beta about 10.
  - Q5 holds Q4's base at +VL in overload, so the green draws 0.0 µA.
  - Nothing lights in silence, no state lights both colours, and no LED or transistor is reverse-biased.
  - LED 6.5 mW against 62.5–75 mW; R15 / R124 about 47 mW in 0805.
  - VREF is loaded 0.7 %, so the red's threshold doesn't move.
- **RET1 circuit:**
  - **Return 2 = return 1:** the two blocks match part for part (76 each) under the net map RT_ → RT2_,
    Return_ → Return2_, SW4–7 → SW8–11, with 0 differences in value, footprint, MPN, DNP or connection.
  - **Routing:** SW8 / SW9 / SW10 go to MIX L/R, SUB 1/2 and SUB 3/4 through 4K7 1 %; off grounds the resistor end.
    SW11 puts the 43K pair on the PFL bus and lights D4.
  - **Jacks:** J6's normals go to GNDA; J7's normals go to J6's tip / ring, so R is normalled to L. Sleeves are on
    CHASSIS.
  - **NJ6FD-V pads:** KiCad's footprint is Neutrik's PCB layout (drawing 3102 St 07 11) turned 180°, not mirrored, so
    T / R / S / TN / RN / SN mean what the netlist says. This also settles the "TN / RN / SN unchecked" item in
    `panel_parts_drawings.md`.
- **RET1 links and history:**
  - **Links:** group CN3 = jack board CN1 (2 × 8, pinout unchanged) and CN4 = CN2 (2 × 5) pin for pin; no CHASSIS on
    either.
  - **Against the commit before RET1:** no old part changed value, footprint or connection; old nets only gained the
    new pins.
- **RET1 mechanics:**
  - **Jack board:** the fourth jack row and the standoffs end before the main board's edge at y 94.5.
  - **Panel:** every group panel hole is on its part's feature, and the legends name the right functions.
  - **Off-board counts:** they reconcile with the boards.

## Applied now

1. **Jack board CN1 moved 1 mm** (pin 1 to y 42.3). Its body had sat over J5's tip solder joint: courtyard to y 48.95,
   pad edge at 48.78. This predates RET1. It now clears J5 and J1 by about 0.8–0.9 mm. Parity DRC: 0 violations on
   the group; the jack board has only the NJ6FD-V's own items.
2. **Group panel: return routing keys named R1 / R2.** The panel had two identical MIX / 1-2 / 3-4 rows, and the lower
   one (return 1, in the routing row at y 274) sat in the sub section with nothing tying it to RET 1. The keys now read
   R1 MIX / R1 1-2 / R1 3-4 and R2 MIX / R2 1-2 / R2 3-4; panels regenerated.
3. **D2's footprint:**
   - the fab outline is the Ø4.0 flange (was the Ø3.0 dome);
   - no 3D model line: the file didn't exist, and the render draws D2's pins and lens;
   - the strip was re-placed with 0 parts moved and 0 DRC violations.

   Also from the review:
   - **3-lead LED spacer:** D2 needs one (or a 2-hole spacer opened up), about 7.2 mm long since it is 0.4 mm taller.
     Counted apart in `offboard_bom.md` (24) and added to `sample_order.md` check 8, with the Ø3.0 ± 0.25 dome in the
     Ø3.2 hole.
   - **`sim/pfldet.py`:** now counts the PFLDET line's 42 keys (16 on the groups): results unchanged, one press
     0.924 V against 0.497 V, 24 presses 1.289 V, released LEDs 20.4 nA.

## Proposals

**P1. A 1K in series with each hold stage's discharge.** U4A (since K3) and U17A (MET1) discharge their 220 nF hold
caps straight from +VL.
- **The stress:** for about 0.1 ms the output sinks at its own current limit (21 mA typ at 5 V, more at 17 V). That is at
  or above the LM393B's 25 mA absolute maximum for the output current, though TI rates a short to ground as unlimited
  (SLCS005 §5.1).
- **The fix:** a 1K from each comparator output to its hold node caps the peak at 17 mA. 470R, as the reviewer
  suggested, would still allow 36 mA.
- **Sim** (`sim/review/gaps/ol.py`'s deck with the 1K): thresholds unchanged (red +18.4, green −19.5 dBu at 1 and
  10 kHz), and a single +20 dBu cycle still lights the red.
- **Scope:** 2 parts per strip. It touches K3's signed circuit (U4A).

**P2. 100 nF on VREF at R40 / R41.** VREF (a 5K node, no cap) now runs from R40 / R41 at y 85–90 to U17 at y ~300,
about 215 mm.
- **The fix:** a 100 nF there keeps pickup and the LED's 15 mV supply step out of both thresholds.
- **Scope:** 1 part per strip. Touches K3's divider.

**P3. 10M hysteresis on U4B and U17B (optional).**
- **The issue:** at the end of each hold they compare a slow ramp (about 38 mV/ms) against VREF, with no hysteresis.
  The sim shows no chatter, but its switch model has 1 mV built in. Chatter would be invisible but puts edges on
  +VL / GNDD.
- **The fix:** 10M from output to + input.
- **Scope:** 2 parts per strip. Low priority.

**P4. Standoff screws in the panels (decide how the boards fasten).**
- **The gap:** `offboard_bom.md` counts two M3 screws per standoff, one at the panel end. But the panel drawings have
  no hole for any standoff, on strip, group or master, and the 3D model ends the standoffs at the panel's underside.
  The boards are held by the pot and jack nuts now; the standoffs only support them.
- **Options:**
  - a. M3 countersunk through-holes at every standoff, heads flush on the front (visible; check each against the
    legends: the group jack board's at board (8.84 / 29.16, 89.8) come within about 1.3 mm of the RET 1 title, so they
    may need to move);
  - b. blind self-clinching M3 studs pressed into the panel's back (invisible; the panel maker must offer them, as
    Schaeffer does);
  - c. no panel-end screw: the standoffs are spacers only, held by the board screw and the pot / jack nuts.
- **Recommendation:** b, if the maker quotes it, else c. The Delta's own modules hang their boards on the pot nuts.

## Notes (no change)

- **SIG_IN's negative clamp:** D11 holds SIG_IN at about −0.21 V on negative half-cycles (sim, +22 dBu). The
  LM393B's recommended input minimum is −0.1 V (absolute −0.3 V); below it the parasitic input diode can upset the
  output (SLCS005 note 5). A wrong state there can only light the green, which is right when there's signal.
  - Raising R118 to 220K, as the reviewer suggested, only reaches −0.17 V and moves the green's threshold by the input
    bias, so it isn't proposed.
  - A series-diode rectifier would keep SIG_IN at or above 0 V, at the cost of a temperature-dependent threshold.

- **Routing guidance for the strip's signal detector** (U17 block at x 1–11, y 298–324, left of the fader):
  - PRESRC to R118 is about 145 mm of pre-mute audio. Keep it away from MUTEOUT, the fader, the routing 4K7s and the
    DG413 nets, with ground beside it, or the ON mute (−87 dB) and unassigned (−102 dB) figures can erode.
  - The LED lines (OL_A, SIG_A, about 260 mm) and OL_K carry DC and switch edges only.
- **Power-up lamp test:** both hold caps start at 0 V, so the red lights for about 0.2 s at power-up (sim). With C97 /
  C99 at opposite tolerance ends, the green can blink for about 30 ms after it. Harmless.
- **Group link pinout:** CN4 / CN2 starts with a signal on conductor 1. Starting with a ground would give every pair a
  ground on both sides. It's the shared `link_pins()` rule (the strip's and master's links too), so it is left as it is.
- **Jack board standoff pads:** they reach y 93.0 against the 93.5 board edge (0.5 mm). Fine for most fabs.
- **Panel print:** on every 0–10 ring the "2" at 9 o'clock is a dot only (it would cross the panel edge). The group's
  AUX cap is printed yellow on every group, while the cap order counts groups 3–4 green (`panel_layout.GROUP` comment).

## Stability (TI models)

Return 1 and return 2 on the group deck (`sim/review/group/`, `sweep.py ret none 0.08`, 21 states: inputs open or
driven from 10 / 600 / 2K2 through 100 p / 2.2 n of cable, level at 0 / 0.706 / 1, every key on; board traces from the
new placement). TI's OPA161x for the OPA1612s, the datasheet-fitted macro for the OPA1656 followers.
Log: `sim/review/group/log_v03_ret.txt` (local: the folder ignores logs and results; the command above reproduces it in 91 s).

| Unit | Return 1 | Return 2 |
|---|---|---|
| Receivers L / R (OPA1612) | 69.6 / 66.6° | 68.5 / 66.4° |
| Level buffers L / R (OPA1612) | 71.0 / 70.9° | 76.9 / 76.8° |
| Input followers (OPA1656, fitted) | 52.5–52.9° | 52.1–52.8° |

Closed-loop peaking ≤ 1.32 dB everywhere. The 2026-10-25 figures were 69.3–71.3° and 53.1°.
- **Return 1's receiver R** went from 69.3 to 66.6°: its output trace is 40.7 mm on the new placement, against
  17.9 mm before.
- **Return 2's level buffers** have more margin than return 1's: their output traces are shorter.

**The rest of the group, re-run on the new placement** (same models, fix set `none`, 0.08 pF/mm):

| Sweep | States | Worst now | Worst 2026-10-24 | Largest drop for one unit |
|---|---|---|---|---|
| `pots` (positions, keys) | 18 | 52.8° (return 2 L ring follower) | 64.2° | −2.7° (return 1 receiver R) |
| `bus` (bus C, ribbon, jumpers) | 103 | 57.1° (sub summer, 100 pF bus with the ferrite shorted) | 57.2° | −0.1° |
| `ins` (insert plugged / open) | 68 | 66.4° (sub re-inverter) | 65.7° | −0.1° |
| `loads` (+22 / +47 pF on every output) | 12 | 46.8° (aux re-inverter, +47 pF) | 45.8° | −2.2° (pan buffer L) |

The `pots` worst is the input followers, which are new since that run (G3b) and sit at 52–54° on the fitted model.
Every other unit is within 2.7° of its October figure, and several gained (sub re-inverter 67.6 → 71.4°).

**The master module, re-run on today's netlist and placement** (`sim/review/master/`, TI's OPA161x / OPA1656 /
DRV134 / TL072 models, fix set `none`).
- **What was run:** all 31 configurations of `configs.py` (pots, PFL / AFL, EXT, inserts, relays, bus, ground
  cancel, +22 / +47 pF on every output, the placed trace estimate), 166 min, plus the phones composite (`run_phv.py
  asis`, both channels).
- **Runner:** `run_each.py` runs one configuration at a time in its own process group, printing time and worst unit
  per configuration (local log `log_v12_none.txt`).
- **Trace table:** `master_len.json` was re-measured from the placed board.

| | Today | 2026-10-24 |
|---|---|---|
| Worst unit | U21A/B (C/Room followers), 47.7° at every pot fully up | the same, 47.7° |
| Fader post-amps U5A/B | 51.6° (+47 pF) | 51.6° |
| EXT followers U43/U44 (new since, G3b) | 52.8° (+47 pF) | – |
| Solo U19A | 65.3° (+22 pF beyond its 100R) | 73.5° |
| Phones composite U26A/B | 76.0° | 76.0° |
| Every other unit | within 1.5° of October, or better | |

Two faults in the stress configurations' load map came from the master having been drawn on 2026-10-24, and both are
fixed in `configs.py`:
- **The +47 pF landed on the pin side of the build-outs.** The map put it beyond them by net names that are now
  unnamed, so it hit the post-amps, the solo stage and the insert-return buffers on the pin side (U5A read 44.1°).
  - MG10 keeps those nets pad-length, so that isn't the intended stress.
  - The far side is now found from the netlist: the other end of each build-out of 100R or less.
- **The two idle spare halves (U6B, U19B) were loaded too.** They used to be skipped by "SPARE" in their net names, so
  they read 63.6°, which means nothing. They are now found by structure and skipped.

The meter detectors (U29A, U36A) read 108° rather than 149°: their output is now the diode cathode (MG8), so the
stress load sits elsewhere. That is still far from any limit.

**Why the first attempts failed:**
1. **The `mg` fix set is obsolete.** It was written for group rev 0.1: MG4–MG8 have been in the schematic since rev 0.2,
   and the drawn schematic leaves those nets unnamed. Applied to today's netlist, its re-pin moved U2B's + input onto a
   node with nothing else on it, so the deck had no operating point.
   - The 2026-10-25 runs used `none`. `master_group_review.md`'s example still said `mg`; it's corrected.
   - `fixes.apply()` now refuses a set that refers to nets the netlist doesn't have.
2. **TI's OPA1656 model doesn't converge in this deck on ngspice 46** (as on the strip, `strip_noise_proposal.md`). The
   followers need `OPA1656_FIT=<models_cd.inc>`.

**Not the cause:** the ngspice version or the OPA161x file. A single OPA161x converges at once, and the 2026-10-24 /
25 runs used the same binary and the same model file (same MD5).

## Sign-off

- [x] **P1** 1K between the U4A / U17A outputs and their hold nodes. Signed off 2026-10-27, applied (strip v4.9: R126 / R127).
- [x] **P2** 100 nF on VREF at R40 / R41. Signed off 2026-10-27, applied (C100).
- [ ] **P3** 10M hysteresis on U4B / U17B (optional). Declined 2026-10-27: the sim shows no chatter at a 1-2 us step.
- [x] **P4** Standoff fastening at the panel: **b if the panel maker offers blind M3 studs, else c** (Ruslan, 2026-10-27).
  - **Stud type:** pressed-in (PEM concealed-head) M3 studs need a 1.60 mm sheet and the panels are 1.5 mm, so b means
    welded studs.
  - **Drawings:** their positions are in `panels/` (hole tables, DXF layer STUDS), all clear of the front cut-outs.
  - **Without studs (Ruslan, 2026-10-27):** the jack-board standoffs, which carry CHASSIS to the panel (G2), get
    countersunk M3 flat-head screws through the panel: Ø3.4, 90° to Ø6.5, with an internal-tooth star washer under
    each standoff. The main-board standoffs stay spacers.
  - **In the drawings:** the DXF layer CSK_NO_STUDS and the hole tables, rows marked "ONLY IF NO WELDED STUDS".
  - **Checked:** every countersink is clear of the cut-outs and the print, so no legend moved. The tightest is group
    H1, its head 0.78 mm from the RET 1 title.
