# Ground-and-hum study (2026-10-25)

What it covers: the heavy-ground harness, magnetic pickup in the ground loops, LED and logic return currents, and
synth ground loops. Each source is referred to main L and compared with the console's noise floor.

- Script: `sim/review/ground/ground_study.py [geom|gauge|mag|led|synth|stereo|all]`. Results are written to
  `sim/review/ground/results.json`.
- Console model: the whole-console deck of `tools/sim_console.py`. Each module's spade wire is now an R + L taken from
  its real length (`console(spade=, spade_emf=)`).
- Noise floor at main L, 20 Hz–20 kHz: −79 dBu with 24 strips routed, −91 dBu with one strip routed.
- Target: every source at most −89 dBu (10 dB under the 24-strip floor).

Three findings:

1. **The harness as drawn in the 3D model fails.** Its spade wires run down to the tub floor and along it, so each
   module's ground loop encloses up to 800 cm². A 1 µT field reaches main L at up to −81 dBu.
2. **Routing the wires under the motherloom fixes the harness.** The loop shrinks to at most 33 cm² (−28 dB). With
   14 AWG wire, every harness-related source passes.
3. **Earthed synths are the biggest hum risk, and wire gauge cannot fix them.**
   - The jack sleeves sit on GNDA, so the cable shield's ground-loop current flows through the strip's audio ground.
   - The receiver's common-mode impedance is 20 kΩ per leg, so a synth with a 1 kΩ output gets only 26 dB of
     rejection.
   - Pseudo-balanced cables still fail as built: −73 dBu at main L with a 10 mV earth difference.
   - Two changes together pass: sleeves to chassis plus a buffered receiver (−105 dBu). Either change alone leaves
     about −80 dBu.
   - TS cables from earthed synths fail whatever the console does (−53 dBu at 10 mV).

## 1. Harness geometry (from the 3D build)

The module layout comes from `tools/console_3d.py` and `render/*.json`:

- Modules at a 40.64 mm pitch, left to right: 12 strips, G1, G2, the master (two pitches), G3, G4, 12 strips.
- Each strip and group has its spade tab (Keystone 1287) at (5.0, 358.0), with the tip 10.2 mm under the board, and
  its bus header at (31.46, 345.64). The ribbon runs about 9 mm under the boards.
- The master's M4 star stud is at (39.3, 214.0); its bus headers are at x 5.5 and 72.0.

A module's ground loop is its spade wire out to the star, then back through the master board, the motherloom's ground
conductors (pins 2–16) and its own board. The script takes the loop's vector area from the polygon.

| route | wire length | loop area, worst (s12 / s24) | loop area, nearest group |
|---|---|---|---|
| `tub`: as drawn (down to the tub floor, along it, up to the star) | 0.31–0.87 m, 16.5 m in all | 798 / 757 cm² | 70–100 cm² |
| `ribbon`: tied under the motherloom, then along the master's underside to the star | 0.24–0.79 m, 14.4 m in all | 33 / 30 cm² | 6.5–7.7 cm² |

The lengths include 60 mm for the receptacle, the ring lug and dressing. Ribbon-route cut list, from the module next to
the master outwards, in mm:

- left wing: 264, 305, 345, … +40.6 per module … 792;
- right wing: 237, 278, 318, … 765.

The left wing is longer by the offset between the master's two headers.

## 2. Ground-current paths (wire gauge)

Main L per ampere injected into a module's ground, in mΩ at 50 Hz / 10 kHz. The "all" column is 1 mA into every
module (the common shift that GCANCEL is meant to cancel), in dBu.

| case | s12 (far L) | s06 | s01 | g1 | s24 (far R) | all, 1 mA each |
|---|---|---|---|---|---|---|
| old sim assumption (0.3 m, 18 AWG) | 1.88 / 5.6 | 1.50 / 4.0 | 0.05 / 0.6 | 4.01 / 6.0 | 1.88 / 5.6 | −93.9 |
| tub, 18 AWG | 4.43 / 14.1 | 2.98 / 9.9 | 0.15 / 2.0 | 4.15 / 5.9 | 4.30 / 13.7 | **−83.7** |
| tub, 16 AWG | 3.02 / 14.0 | 2.02 / 9.8 | 0.12 / 2.1 | 3.47 / 6.0 | 2.93 / 13.6 | −87.8 |
| tub, 14 AWG | 2.01 / 13.9 | 1.34 / 9.7 | 0.13 / 2.1 | 2.74 / 6.1 | 1.94 / 13.5 | −92.0 |
| ribbon, 18 AWG | 4.08 / 13.1 | 2.71 / 9.1 | 0.17 / 1.7 | 3.78 / 5.8 | 3.96 / 12.7 | −84.5 |
| ribbon, 16 AWG | 2.77 / 13.0 | 1.82 / 9.0 | 0.15 / 1.7 | 3.07 / 6.0 | 2.68 / 12.6 | −88.5 |
| **ribbon, 14 AWG** | 1.83 / 12.8 | 1.20 / 8.9 | 0.16 / 1.7 | 2.35 / 6.1 | 1.77 / 12.4 | **−92.6** |
| ribbon, 12 AWG | 1.20 / 12.6 | 0.78 / 8.7 | 0.15 / 1.7 | 1.72 / 6.1 | 1.16 / 12.3 | −96.8 |

- The real lengths are up to 3× the old 0.3 m assumption. They cost about 10 dB on the common case. `t_ground` in
  `sim_console.py` still uses 0.3 m, so its −93 dBu was optimistic.
- 14 AWG (2.08 mm²) is the thinnest gauge that meets the target on the common case, with 3.6 dB to spare. 12 AWG adds
  4 dB, but needs 4–6 mm² receptacles.
- At 10 kHz the transfer is set by inductance, about 12–14 mΩ, and gauge barely changes it.
- The group's figure includes its stereo return at full level.

## 3. Magnetic loop pickup

The model drives a 50 Hz field through every module's loop and feeds the induced EMF in series with that module's
spade wire. Results are main L in dBu for 1 µT; add 20 dB for 10 µT.

- A transformer's 150 Hz component is roughly B/3, which gives the same level as the 50 Hz figure.
- "uniform x / y / z" is a distant source. The two wings' loops partly cancel, because they circulate in opposite
  senses.
- "aligned" puts every loop at its own normal, all in phase. It is the upper bound, for a strong local source near
  the desk.

| case | uniform x | uniform y | uniform z | aligned (bound) |
|---|---|---|---|---|
| tub, 18 AWG | −105.0 | −124.3 | −115.4 | **−80.6** |
| tub, 14 AWG | −108.5 | −127.4 | −118.5 | −79.9 |
| ribbon, 18 AWG | −125.7 | −132.0 | −139.6 | −108.9 |
| **ribbon, 14 AWG** | −129.7 | −135.9 | −143.8 | **−108.6** |

- Gauge hardly matters here: a thicker wire carries more induced current but has a lower ground impedance.
- Loop area is what matters. The tub route fails the target at 1 µT in the bound case and is −60 dBu at 10 µT.
- The ribbon route passes up to about 10 µT even in the bound case.
- For scale: a studio away from transformers measures 0.1–0.5 µT, and a rack of linear supplies 1–5 µT.
- The console's own supply is switch-mode (LRS-150) in an external box, so it adds no 50 Hz field.

## 4. LED and logic return currents

- **Key LEDs.** The strip's key LEDs (ON, PFL, EQ, routing) and the group's AFL LED run from +VL through 4K7 (3.2 mA)
  into GNDD. GNDD joins GNDA at NT1, so every key press is a 3.2 mA step into the module's ground.
- **Supply side.** R3 / C5 (10R, 47 µF; 470 µs) feed +VL. The external ground current therefore rises in 0.5 ms, and
  the step is set by the 50 Hz–1 kHz transfer, not the 10 kHz one.
- **OL LED.** It returns through U4B to GNDD too, so its current follows the programme peaks.

Main L in dBu, as a peak step, at the worst module:

| case | one key LED | two keys at once | OL LED with programme |
|---|---|---|---|
| tub, 18 AWG | −94.2 | **−88.1** | −94.1 |
| **ribbon, 14 AWG** | −98.3 | −92.3 | −98.3 |

All pass on the ribbon route. A step is far less audible than continuous noise at the same level, so this
comparison is conservative. The OL LED's current only flows when the programme is near clipping, where it is masked.

These return at the star and touch no strip ground, so they were not simulated:

- the master's LEDs and relays;
- the meter strings, which run as constant currents to −VM;
- the PSU's Y-capacitor leakage (LRS-150, < 0.75 mA). It flows in the PSU cable's 0 V and chassis wires, which both
  land on the star.

## 5. Synth ground loops

### 5.1 How the loop forms

An earthed synth, or one tied to an earthed computer by USB, sits at an earth potential Vgl relative to the console's
star. The model uses R_earth 0.2 Ω, a 3 m cable with a 0.05 Ω shield, the jack board's link (10 mΩ) and the strip
ground from §2. The NJ6FD-V's sleeve is on GNDA, so the shield current flows through the jack board, the link and the
strip's ground to the star.

That current causes three problems:

- **Ground injection.** It raises the strip's ground: 38 mA at 10 mV gives −81 dBu at main L at s12.
- **TS cable.** The ring is shorted to the sleeve at the plug, so the receiver sees the full drop along the shield as
  differential signal. No receiver can remove it.
- **Pseudo-balanced cable** (tip hot, ring to the synth's ground at the far end). The shield drop is common-mode,
  rejected by the receiver's CMRR with the synth's output impedance unbalancing the legs.

### 5.2 Receiver CMRR (Monte Carlo)

R6–R9 are drawn uniformly within the tolerance, 4000 draws, at 50 Hz. Figures are median / worst 5 %, in dB.

| source impedance (tip leg) | as built, 0.1 % | as built, 1 % | buffered (1M bias), 0.1 % | buffered, 1 % |
|---|---|---|---|---|
| 0 Ω | 67.6 / 58.9 | 47.6 / 38.9 | 67.9 / 58.9 | 47.9 / 38.9 |
| 100 Ω | 45.9 / 44.3 | 45.0 / 36.5 | 68.0 / 58.7 | 47.9 / 38.8 |
| 1 kΩ (typical synth) | **25.9 / 25.7** | 25.9 / 24.3 | **60.0 / 54.1** | 48.0 / 38.7 |

- The 10K difference amplifier presents 20 kΩ common-mode per leg. With a 1 kΩ source the imbalance sets the CMRR at
  26 dB, and the 0.1 % resistors are wasted.
- Followers with 1M bias in front raise it to 54 dB (worst 5 %).
- 0.1 % parts are worth 20 dB over 1 % once the source imbalance is out of the way.

### 5.3 Main L, earthed synth on s12

Ribbon route, 14 AWG. Synth output 1 kΩ, 0.1 % resistors, worst 5 %. Figures are main L in dBu at Vgl = 10 mV /
100 mV / 1 V.

| cable | jack sleeve | receiver as built | buffered receiver |
|---|---|---|---|
| TS | GNDA (as built) | −52.6 / −32.6 / −12.6 | −52.7 / −32.7 / −12.7 |
| TS | chassis | −52.8 / −32.8 / −12.8 | −52.9 / −32.9 / −12.9 |
| TS | GNDA via 10 Ω | −63.7 / −43.7 / −23.7 | −81.7 / −61.7 / −41.7 |
| pseudo-balanced TRS | GNDA (as built) | **−72.8** / −52.8 / −32.8 | −80.4 / −60.4 / −40.4 |
| pseudo-balanced TRS | chassis | −77.0 / −57.0 / −37.0 | **−105.4 / −85.4** / −65.4 |
| pseudo-balanced TRS | GNDA via 10 Ω | −64.4 / −44.4 / −24.4 | −92.0 / −72.0 / −52.0 |

- With a 100 Ω synth output, the buffered receiver with chassis sleeves gives −110 / −90 / −70.
- Vgl is about 10 mV when every piece of gear, and the console's supply, is fed from one mains distribution point. It
  is 0.1–1 V across outlets on different circuits.

**Two synth cables, one synth** (stereo pair, no earth): the loop is driven only by the field through the area the
two cables enclose. Main L per strip in dBu:

| cables | 1 µT | 10 µT |
|---|---|---|
| TS, 10 cm apart | −87 | −67 |
| TS, 50 cm apart | −73 | −53 |
| pseudo-balanced, 10 cm apart | −113 | −93 |

## 6. Margins against the target (−89 dBu)

| source | as built / as drawn | with the recommendations (G1–G3) |
|---|---|---|
| ground currents, 1 mA per module | −83.7 (fails) | −92.6 (3.6 dB margin) |
| magnetic, 1 µT, bound | −80.6 (fails) | −108.6 (19.6 dB) |
| magnetic, 10 µT, bound | −60.6 (fails) | −88.6 (at the target; the uniform cases ≤ −110) |
| key LED, one / two keys | −94.2 / −88.1 | −98.3 / −92.3 |
| earthed synth, TRS, Vgl 10 mV | −72.8 (fails) | −105.4 (16.4 dB) |
| earthed synth, TRS, Vgl 100 mV | −52.8 (fails) | −85.4 (3.6 dB short: needs single-point mains) |
| earthed synth, TS | −53 at 10 mV (fails) | fails at any Vgl > 0.15 mV: don't use TS cables from earthed synths |
| stereo pair, cables together | −∞ | −∞ |

## 7. Recommendations

G1–G3 were signed off by Ruslan on 2026-10-25 and applied (strip spec v4.4, master spec v0.10); see §9. G4 is practice
at the desk.

**G1. Harness: route and gauge.**
- One 14 AWG (2.08 mm²) stranded wire per module, radial as decided (master spec §26). Use blue 6.3 mm insulated
  receptacles, taking 1.5–2.5 mm².
- Run each wire straight down from its tab (12 mm) to just under the motherloom, then along the ribbon's underside,
  tied to it every ~80 mm.
- At the master, follow the master board's underside to the star. The wires of one wing stay together as a flat
  bundle under their ribbon.
- Do not let the wires drop to the tub floor: the loop area is what matters, not the length.
- Cut lengths are in §1.
- Twenty-eight ring lugs don't stack on one M4 stud. Instead, bolt two short copper bars (one per wing, e.g.
  15 × 2 mm, ≈ 0.1 mΩ) under the star stud, each with fourteen 6.3 mm tabs. The bars add a negligible shared
  impedance.
- 12 AWG is the upgrade, if 4–6 mm² receptacles fit the tabs (a further 4 dB on the common case).

**G2. Balanced-input jack sleeves to chassis at the point of entry** (AES48, as the master's XLR pin 1 already is).
- Which jacks:
  - the strip's line input J1 and direct out J5;
  - the group's return inputs;
  - the master's EXT and return inputs.
- How:
  - the jack board's sleeve pads go to a CHASSIS net;
  - plated mounting holes and metal standoffs bond that net to the panel;
  - each panel bonds to the frame, and the frame to the master's CHASSIS (J1 pin 1, at the star);
  - C8 / C9 move to the sleeve side.
- The insert jack J2 stays on GNDA. Its send and return are single-ended, so a chassis sleeve would put the
  chassis–GNDA difference in series with the return.
- This keeps cable-shield currents out of every audio ground.

**G3. Buffered strip receiver.**
- An OPA1656 dual as followers in front of R6 / R8. 1M bias on each leg, from IN_T and IN_R to GNDA, replaces R10.
- Raises the common-mode impedance from 20 kΩ to 1 MΩ: 26 → 54 dB CMRR against a 1 kΩ synth output (worst 5 %).
- Noise: the followers add about 0.1 dB to the receiver's 10K network.
- An unplugged input would hiss through the 1M resistors. Wire J1's TN / RN normals to the sleeve, so an empty jack
  shorts both legs.
- The same applies to the group and master return receivers, for effects units with 100–600 Ω outputs.

**G4. At the desk.**
- Pseudo-balanced TRS cables for every synth: tip hot, ring to the synth's ground, shield at both ends.
- Feed every piece of gear and the console's supply from one mains distribution point.
- Keep a stereo pair's cables together.
- TS cables only from synths with no earth connection: no IEC earth, and not tied to an earthed computer by USB.

## 8. Not covered

- RF.
- The jack-board link's own inductance.
- Mutual inductance between the ribbon's ground conductors and the spade wires: the 10 kHz figures are conservative.
- Ground currents from the master's own loads.
- Measurements. Bench checks are the jig's ground tests (test_jig_spec.md) and a hum measurement with a real synth on
  TS and on TRS, before and after G2 / G3.

## 9. Applied (2026-10-25)

- **G1.** `tools/console_3d.py` draws the harness as specified: 14 AWG wires (2.9 mm insulated) tied under each
  motherloom, down the master's free edge strip, onto two copper bars with fourteen tabs each on a spacer under the
  star stud. `tools/sim_console.py` now models every spade wire from this harness by default (`SPADE_WIRE`: 14 AWG,
  the cut-list length). Its ground check at 1 kHz: 10 mA into strip 24 −89.8 dBu, 1 mA into every module −89.2 dBu
  (at the target; −92.6 at 50 Hz, §2), ground cancel still 20 dB. The 3D route adds a short drop at the master (edge
  strip to the bars below the bottom-side parts) that §1's loop areas don't include.
- **G2.** Strip J1 / J5 sleeves and C8 / C9 on CHASSIS; group return and master EXT sleeves on CHASSIS; plated CHASSIS
  standoff holes on all three jack boards (H1–H2, H1–H2, H1–H3), placed where the plain holes were. The group keeps
  CHASSIS off its link; every main board's netlist is unchanged but the strip's.
- **G3.** U16 OPA1656 followers, 1M bias per leg (R10, R112), 220R in (R110, R111) and, added in the implementation,
  100R build-outs (R113, R114): the follower is the OPA1656's least stable configuration, 52° unloaded and 25° with
  220 pF on the fitted model; with 100R it keeps ≥ 48.5° for any load (`sim/review/ground/follower_stab.py`).
  On TI's own OPA1656 model (2026-10-28; the OPA1612s single-pole so the deck converges, `OPA1612_SIMPLE=1
  OPA1656_UNITS=U16`): 61.7° over all 21 strip-deck states, peaking ≤ 0.83 dB; the group's return followers 59.2-61.0°.
  J1's normals go to AGND rather than to the sleeve (now CHASSIS), so an empty input sits exactly at the receiver's
  reference. `tools/sim_netlist.py` checks the common-mode rejection: −60.1 dBu at PRE for 0 dBu through 1 kΩ on the
  tip leg (it would be −26 with the unbuffered receiver).
- **Checks:** strip 796 pins, jack boards 32 / 40 / 89 pins, group and master unchanged: 0 mismatches, check_fp 0,
  ERC 0. `sim_netlist.py` 37/37, `sim_console.py` 32/32 (noise −79.2 / −91.2 dBu, unchanged). Parity DRC: 0
  violations on every main board, 0 parity issues on all six boards; the jack boards show only the NJ6FD-V
  footprint's own items. The strip moved 77 parts to fit U16 (a zone of its own by SW15, placed first); its report
  is decouplers 3.1 / 10.0 / 12 (C92 / C93 at 8.0 / 8.5 mm), high-Z inputs 10.9 / 22.1 / 29.
- **Cost:** +7.8 mA per strip and rail typical. The PSU's worst corner (every op-amp at maximum IQ, every LED lit)
  goes from 4.0 A to about 4.24 A on +V, over the 4 A rating (master spec §27, §29). OPA1642 followers (1.8 mA per
  channel, JFET, 5.1 nV/√Hz) would bring it to about 4.11 A. Accepted with the OPA1656 (Ruslan, 2026-10-25).
- **Not done:** the group return and master EXT receivers are still unbuffered (20 kΩ common mode); the balanced
  TRS outputs (sub, aux, C/Room) keep their sleeves on GNDA.

## 10. Extending G2 / G3 to the group and master (G2b / G3b, signed off by Ruslan and applied 2026-10-25)

G2 and G3 as signed cover the strip's line input and direct out, the group returns' and master EXT's sleeves, and the
strip receiver. Two gaps remain.

**G2b. Balanced TRS output sleeves on CHASSIS.** These are the DRV134 outputs:

| Jack | Board | Typical load |
|---|---|---|
| Sub out | each group's jack board | recorder, interface |
| Aux out | each group's jack board | outboard effects |
| Aux 5 / 6 out | master jack board | outboard effects |
| C/Room L / R out | master jack board | active monitors: earthed, the classic hum loop |

- **The problem.** These sleeves are on GNDA, so a shield current from earthed gear on the far end flows through the
  module's audio ground, exactly as on the strip inputs before G2.
- **How big.** A group's ground reaches main L at 2.35 mΩ (§2, ribbon route, 14 AWG). A 10 mV earth difference drives
  ~38 mA through the shield, which gives about −79 dBu at main L, 10 dB over the target.
- **Why it is safe.** The DRV134 is a floating-style driver, so its output doesn't need the sleeve as a reference.
  Into an unbalanced destination (ring shorted to sleeve at the far end) it still works, with the return current
  taking the shield and chassis.
- **Cost:** no parts, only the sleeve net on the jack boards. The group keeps CHASSIS off its link; on the master it
  is already on the link.
- **Recommended.**

**G3b. Buffered receivers on the group returns and the master EXT input.** The same circuit as the strip's U16: an
OPA1656 dual as followers, 1M per leg, 220R in, 100R build-outs.
- **Count:** each stereo input needs two followers per side, so two duals. That is four groups × 2 + the master × 2 =
  10 OPA1656 duals in the console.
- **CMRR (0.1 % bridge, worst 5 %), as built → buffered:** 44 → 59 dB against a 100 Ω source; 26 → 54 dB against a
  1 kΩ synth output.
- **When it matters.** With proper balanced effects returns (low-Z on both legs) the gain is small. With synths on the
  returns (a stereo synth on a stereo return) it is the same 28 dB as on the strip.
- **Power:**
  - +3.9 mA × 20 channels = +78 mA typical per rail. The groups put 31 mA on each wing; the 16 mA for EXT is the
    master's own.
  - The accepted worst corner goes from 4.24 to about 4.33 A on +V, or 4.37 A if N1 is adopted later.
- **Placement:** needs a trial. The group board is the narrow 38 mm strip and its return receivers' area is already
  its worst report entry (20 mm).
- **Normals:** an empty R jack takes the L signal through its normals (mono into L), and the followers keep that.
  The L jack's own normals are unused today. Wired to GNDA they short an empty L input, so the 1M bias doesn't hiss,
  and through R's normals they short an empty R input too.
- **Recommended** if returns will carry synths, otherwise optional.

- [x] **G2b** Sleeves of every DRV134 TRS output (group sub / aux out, master aux 5 / 6 and C/Room L / R) on CHASSIS.
- [x] **G3b** Buffered receivers on the group returns and master EXT (10 OPA1656 duals, +78 mA per rail typical).

### Applied (2026-10-25)

- **G2b:** the four TRS outputs' sleeves on CHASSIS. The group keeps CHASSIS off its link; the master's link already
  carries it.
- **G3b, the receiver:** `master_lib.receiver()` now builds the strip's U16 circuit in front of the bridge. The
  followers are created in a deferred pass just before `spares()` (`master_lib.DEFER`), so every existing reference on
  both boards is unchanged: group +16 parts (U10, U11, …), master +16 (U43, U44, …).
- **G3b, the jacks:** the return / EXT L jack's normals now short an empty input to GNDA.
- **G3b, the drawing:** a fragment of its own, `frags.rx_buffers`, ahead of the bridge.
- **Checks:**
  - group 186 parts / 529 pins, master 579 / 1686, jack boards 40 / 89 pins: 0 mismatches, check_fp 0, ERC 0;
  - `sim_console.py` 32/32 (returns and EXT levels unchanged).
- **Placement:**
  - group: the new parts fit and the report is no worse (decouplers 3.1 / 4.5 / 0, high-Z inputs 7.8 / 20.1 / 18);
  - master: placed first in the monitoring zone, they pushed U11's mute network and aux 6's input out to 73 mm. Now
    they get a zone of their own placed last, and the report is back to its old values (3.1 / 10.5 / 26 and
    8.1 / 38.5 / 75). The cost: U43 / U44 sit 40–50 mm from the EXT bridge, which is acceptable on their buffered,
    100R-fed lines;
  - parity DRC: 0 violations on both main boards, 0 parity issues on all four boards.
- **Found on the way:**
  - every global label on the hierarchical pages had its text justified to the bottom of its box, so underscores
    merged with the outline. `schgen` now centres it; no netlist changed;
  - the followers' stability. The group deck (`sim/review/group`, TI OPA161x for the OPA1612s, fitted OPA1656M for
    the followers; TI's OPA1656 model crawls there as in the strip deck) read only 40° and 3.4 dB peaking on the
    followers. Cause: the 220R in front of each + input against the OPA1656's 9.1 pF differential input capacitance.
    A 100 pF C0G from each + input to ground, after the 220R, fixes it:
    - receivers: their existing 100 pF moved from the jack line to the + input;
    - strip: new C94 / C95 at U16.
    Followers now 53.1° (group) and 54.1° (strip) on the fitted model, peaking ≤ 1.24 dB. The return receivers and
    level buffers are unchanged at ≥ 69.8° (TI).
  - Re-placed with the caps: strip (C38 / C91's bottom zone widened to y 120), group and master; parity DRC clean;
    reports: strip 3.1 / 10.0 / 11 and 10.9 / 22.1 / 29, group 2.9 / 4.5 / 0 and 7.8 / 20.1 / 18, master unchanged.
