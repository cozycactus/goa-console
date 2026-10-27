# CS10: a reverse Schottky across each audio rail of every strip and group board (proposal, 2026-10-27)

**Not signed off.** The change is `cs10_proposal.patch`. It touches tools only: `gen.py`, `strip_draw.py`,
`gen_group.py`, `master_lib.py`, `schgen.py`, `place_strip.py` and `place_group.py`. It was applied to a trial tree,
checked (§5) and reverted, so nothing in the design has changed. The simulation is `sim/review/cs10/rail_loss.py`; its
output is in `rail_loss.out`.

## 1. Why

**Where it comes from.** `console_survey.md` §7: the Allen & Heath GL2 puts a reverse diode (1N4002) on each rail of
every board. Our strip and group boards have none.

**Where our clamps are.** The master's SS54s (D8 / D9) clamp the bus at the master's supply entry, before the wing
PTCs. A tripped PTC therefore leaves its wing's rail floating with nothing on it.

**How a rail gets lost:**
- **A wing PTC trips.** The +V wing reaches ~2.07 A in the accepted 4.54 A worst corner, above the MF-RX250/72's hold
  (CLAUDE.md, RET1).
- **A ribbon conductor opens.** Each rail's two or three ribbon conductors run through IDC contacts.
- **The PSU loses one rail.** The two rails are separate floating LDOs.

**What happens then:**
- **The current keeps flowing.** Take −V lost with +V still up. The op-amps' quiescent current, about 87 mA per strip,
  still flows from +VA through the ICs into −VA.
- **−VA rises past ground.** With −VBUS open, nothing takes the current to ground but the ICs' own pin-protection
  diodes into the inputs and outputs, which sit near ground through the circuit's resistors.
- **The reservoir reverses.** −VA rises until the op-amps run out of supply span. C3, a polar 220 µF 25 V, ends up
  reversed, and the pin-protection paths carry tens of mA.
- **+V lost is the mirror:** C1 reverses.

## 2. The circuit

Per board, one PMEG4010CEH (Nexperia, SOD-123F) across each audio rail:

| Board | +VA | −VA |
|---|---|---|
| Strip | D16: cathode +VA, anode GNDA, beside C1 | D17: cathode GNDA, anode −VA, beside C3 |
| Group | D5: as D16, beside C1 | D6: as D17, beside C2 |

**Why this part:**
- **Ratings:** 40 V, 1 A. The rail is 17 V and the crowbar fires at 19.1 V.
- **Forward drop:** VF 340 mV typical, 390 mV max at 100 mA (datasheet). That is well below a silicon pin-protection
  diode's at the same current, so the Schottky takes the whole current.
- **Leakage:** IR 1.1 µA at 10 V (25 °C).
- **Fault dissipation:** about 30 mW at 87 mA.

**Not needed on the logic rails (±VL).** +VL's loads all return to GNDD. −VL feeds only the mute gates, through 220K.
Neither can be dragged past ground.

## 3. Simulation (`sim/review/cs10/rail_loss.py`)

**Model:**
- One board: R1 / R2 10R, C1 / C3 220 µF plus the decouplers.
- The op-amps' 87 mA rail to rail, constant down to a 4.5 V span (the OPA1612 / OPA1656 minimum supply).
- 13 mA from +VA to ground.
- The ICs' pin-protection paths lumped as one silicon diode with 20 Ω or 200 Ω in series, which brackets them.

| Event (100 ms after) | Paths | No diodes: dead rail / IC-path current | PMEG4010CEH |
|---|---|---|---|
| −V lost | 20 Ω | −VA **+2.5 V**, 87 mA through the ICs' protection diodes | −VA +0.36 V, 0 mA |
| −V lost | 200 Ω | −VA **+12.7 V** (C3 reversed by 12.7 V), 60 mA | +0.36 V, 0 mA |
| +V lost | 20 Ω / 200 Ω | +VA **−2.5 / −12.8 V** (C1 reversed), 87 / 60 mA | −0.36 V, 0 mA |
| Power-down, +V falling faster (280 / 240 V/s) | both | −0.11 V: harmless (the spans collapse together) | the same |

Without the diodes, −VA crosses +0.3 V 42 ms after −V is lost: 87 mA charging 220 µF.

## 4. Schematic and placement (trial)

**Strip:**
- **Schematic:** D16 / D17 beside C2 / C4 on page 16 (power entry), drawn as shunts from the rail to GNDA.
- **Placement:** by `moves_only`, top side: D16 4.0 mm from C1's +VA pad, D17 2.8 mm from C3's −VA pad.
- **Moved:** nothing else.

**Group:**
- **Schematic:** D5 / D6 are created after every other part, so no reference moves (263 → 265 parts; the netlist is
  otherwise identical, checked pin by pin). They are drawn on page 11 (power) in their own fragment.
- **Placement:** by `moves_only`: D5 3.0 mm from C1, D6 3.4 mm from C2. `place_group.py` now has `moves_only` and
  keeps the two out of the power zone.
- **Moved:** nothing else.

**Builder:** `schgen.py`'s field layout learns the D_Schottky key. A diode turned 90° is drawn mirrored, so its
reference and value read beside it like the others.

## 5. Checks on the trial tree (`tools/check_all.py`, 59 / 59)

- **Strip:** 906 pins / 312 parts, 0 mismatches, check_fp 0, ERC 0, parity DRC 0 / 0, 312 / 312 linked, route_check 0.
- **Group:** 739 pins / 265 parts, the same.
- **Sims:** `sim_netlist` 39/39, `sim_console` 35/35.
- **Every other board:** unchanged.

**On apply:** regenerating the group rewrites `group.kicad_pro` / `group_jack_board.kicad_pro` from master.kicad_pro.
They gain the KiCad sections master.kicad_pro carries (schematic, ERC and library settings); their net classes and
board rules don't change. The trial kept the committed files.

**BOM:** +2 × PMEG4010CEH per strip and group board, 56 for the console, about $0.10 each.

## 6. Alternative considered

- **Option B: clamps on the master, one SS54 per wing rail after each PTC (4 parts).**
- **What it leaves out:** it doesn't cover a single strip's open ribbon contact.
- **What it lets through:** the 10R in each strip's feed carries the strip's current. The strip's rail would sit about
  0.8 V + the diode drop past ground, enough for the ICs' own protection diodes to share the current.
- **Verdict:** the per-board diode is the robust choice, and it is what the GL2 does.

## Sign-off

- [ ] **CS10** as proposed: D16 / D17 on every strip, D5 / D6 on every group board.
- [ ] Option B instead: four SS54s on the master after the wing PTCs.
- [ ] Neither.
