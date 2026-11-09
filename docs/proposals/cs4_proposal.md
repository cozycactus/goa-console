# CS4: clamp the strip's jack signals to the audio rails at the link (proposal, 2026-10-27)

**Signed off by Ruslan on 2026-10-27 (as proposed: D18-D22 BAV199 at CN3 on every strip) and applied the same day as
strip v5.2; see "Applied" at the end.** The change is `archive/patches/cs4_proposal.patch`. It touches tools only: `gen.py`,
`strip_draw.py` and `place_strip.py`. The
simulation is `sim/review/cs4/jack_protect.py`; its output is in `jack_protect.out`.

## 1. Why

`docs/studies/console_survey.md` §5 CS4: the PM-5000 clamps every jack-facing op-amp pin to the rails (DAN217); our strip has
nothing. A synth console is patched live, and three things reach the main board through the 10-way link (CN3):

- **ESD on a jack's tip or ring.** On the inputs, C8 / C9 (100 pF to CHASSIS on the jack board) charge to kilovolts;
  their charge then goes through the 220R into U16's protection diodes. The outputs (insert send, direct out) have only
  75R between the jack and the op-amp's output pin.
- **Phantom power on an output.** 48 V through 6K8 puts 42 V across C51 (behind the insert send) or C52 (the direct
  out's coupler), both 33 µF 25 V. Today the spec just forbids it (§11, "No phantom").
- **A fault or a hot source on an input:** limited only by the 220R / R99 1K into the IC.

## 2. The circuit

One Nexperia BAV199 per signal, at the main-board end of the link, ahead of every series part:
- **Connections:** pin 3 (the common node) to the signal, pin 2 to +VA, pin 1 to −VA.
- **Parts:** D18 IN_T, D19 IN_R, D20 RET_RAW, D21 SEND, D22 DO_T.
- **DO_R needs none:** it only goes to ground through R73 75R. **No longer true since strip v5.6 (RV3, 2026-10-28):** DO_R
  goes through R73 to C107 33 µF 25 V to GNDA, so the ring has neither a clamp nor a DC bleed; phantom on the direct out
  would charge C107 to ~48 V. Fixed by `docs/proposals/clicks_followup_proposal.md` RV3b (signed off and applied 2026-10-29, strip v5.7): R143 47K bleed and D23
  BAV199 on DO_R, as the tip's R72 / D22.

**Why the BAV199:**
- **Leakage:** 3 pA typical (5 nA max at 75 V). On the input legs' 1 MΩ that is 3 µV typical, 5 mV at the
  datasheet maximum, which is specified far above the ~17 V the clamps see.
- **Capacitance:** 2 pF at 0 V, and the rails keep both diodes reverse-biased.
- **Surge:** 4 A for 1 µs.
- **Pinout and footprint:** the BAV99's (SOT-23, already on the strip for CS1).

**Why at the link end, not after the 220R / 1K** (simulated, §3): there the series resistor stands between the clamp
and the IC, so the IC sees almost nothing. A clamp after the resistor leaves the receiver's op-amp 2.8 A at 8 kV.

**Why not a TVS at the jacks** (PESD24VL1BA, bidirectional 24 V, ~11 pF, to CHASSIS):
- **Inputs:** it protects the inputs well.
- **Distortion:** its capacitance is most nonlinear around 0 V. From a 1 kΩ source that gives −93 dB THD at +20 dBu,
  20 kHz, and −99 dB at 0 dBu, 20 kHz, where the rail clamps measure −106 dB and the solver's floor.
- **Outputs:** they need no TVS once clamped.

## 3. Simulation (`sim/review/cs4/jack_protect.py`)

**Test:** IEC 61000-4-2 contact discharge on the tip (150 pF / 330 Ω gun).
- **8 kV:** level 4.
- **4 kV:** the contact level EN 55103-2 asks of professional audio. It is applied to accessible metal; connector pins
  are often exempt.

**Model:** C8, the link (100 nH), the main-board parts and the rails are in it. "IC" is the current into the pin's own
protection diodes. An HBM 2 kV pin rating, which TI gives its OPA165x / OPA166x audio op-amps, is about 1.33 A /
0.2 µC.

| Tip | As built (IC) | Link clamps (proposed): IC; clamp | Clamp after the series R (IC) | TVS at the jacks (IC) |
|---|---|---|---|---|
| IN_T, 8 kV | 9.6 A, 1.17 µC | **0.09 A**, 0.004 µC; clamp 38 A, I²t 2.1e-5 A²s | 2.8 A | 0.8 A |
| IN_T, 4 kV | 4.8 A, 0.58 µC | **0.05 A**; clamp 19 A, I²t 5.3e-6 A²s | 1.4 A | 0.4 A |
| RET_RAW, 8 kV | 5.9 A | **0.001 A**; clamp 23 A, 1.4e-5 A²s | 1.7 A | 0.16 A |
| SEND / DO_T, 8 kV | 18.9 A, 1.2 µC | **0.38 A**, 0.084 µC; clamp 23 A, 1.4e-5 A²s | (the same place) | 2.2 A |
| SEND / DO_T, 4 kV | 9.4 A | **0.28 A**; clamp 11 A, 3.3e-6 A²s | | 1.2 A |

**The clamp's own stress:** the BAV199's 4 A / 1 µs surge rating is an I²t of about 1.6e-5 A²s. At 4 kV every clamp is
well inside it. At 8 kV on IN_T it is a little over (2.1e-5). That is a direct contact on a tip contact, not a
standard test point.

**Phantom (48 V / 6K8):** C51 and C52 see 17.7 V instead of 41.9 V. The clamp passes about 4.5 mA into +VA.

**Distortion at U16's input, 1 kΩ source:**

| | as built | link clamps |
|---|---|---|
| +20 dBu, 1 kHz | floor (−134 dB) | −131 dB |
| +20 dBu, 20 kHz | floor | **−106 dB** |
| 0 dBu, 1 kHz | floor | floor |
| 0 dBu, 20 kHz | floor | floor |

- The −106 dB comes from the diodes' ~0.5 pF, modulated near clip at high frequency.
- The output clamps sit behind 75R driven by an op-amp, so they add nothing there.

**Swing:** the clamps stay off until a pin is ~0.6 V beyond a rail. The op-amps swing ±15.5 V on ±16.9 V rails, so
they never conduct on signal.

## 4. Schematic and placement (trial)

**Schematic:**
- The clamps are a block of their own: "JACK LINK CLAMPS", drawn on page 2 above the line input. The gain stage moves
  to page 3, and the strip goes to 18 pages.
- 921 pins, 317 parts.

**Placement:**
- By `moves_only`, bottom side beside CN3. Pin 3 is 6.3-9.8 mm from its CN3 pin: a few nH against the link's ~100 nH.
- Nothing else moved.

## 5. Checks on the trial tree (`tools/check_all.py`, 59 / 59)

- **Strip:** 921 pins / 317 parts, 0 mismatches, check_fp 0, ERC 0, parity DRC 0 / 0, 317 / 317 linked, route_check 0.
- **Sims:** `sim_netlist` 39/39, `sim_console` 35/35.
- **Every other board:** unchanged.
- **BOM:** +5 BAV199 per strip, 120 for the console, about $0.05 each.

## 6. On sign-off

- Apply the patch, bump the strip to v5.2, regenerate and re-export, re-place, re-run netrules.
- Update spec §3 (input), §7 (insert), §11 (the phantom note becomes "clamped to 17.7 V; avoid anyway") and §2.4.
- The group and master have the same exposure (their receivers, inserts and outputs). The shared `master_lib`
  functions (`receiver()`, `insert()`, the DRV135 outputs) would take the same clamp in one change. That is a follow-up
  (CS4b) if this one is signed off.

## Sign-off

- [x] **CS4** as proposed: D18-D22 BAV199 at CN3 on every strip. Ruslan, 2026-10-27.
- [ ] Also work up **CS4b** for the group and master.
- [ ] Neither.

## Applied (2026-10-27, strip v5.2)

- **Applied:** the patch, plus revision 5.2 in `gen.py`.
- **Regenerated and re-exported:** the strip netlist, BOM (309 parts, 3 DNP), PDF and `bom/order_bom.csv` (120 + 6 spare
  BAV199).
- **Re-placed:** against the committed board only D18-D22 are new. Netrules re-written.
- **Documents:** strip spec v5.2 (changes, §3, §11, §14, §15, §17), CLAUDE.md. CS4b (group / master) is not started.

