# CS7: DIM on C/Room (proposal, 2026-10-28)

**Signed off by Ruslan on 2026-10-28 (as proposed) and applied the same day; see "Applied" at the end.** The change is `archive/patches/cs7_proposal.patch`. It touches tools only: `gen_master.py`, `frags.py`,
`place_master.py`, `placer.py`, `panel_layout.py`, `sim_console.py` and `sim/review/master/configs.py`.

**Asked for by Ruslan on 2026-10-28:** a DIM key at (29.16, 178) beside POWER, 91K per side bypassed by the key,
−20 dB on C/Room only; U8, R225 and C48 moved locally.

**Calculation and simulation:**
- `sim/review/cs7/dim.py`, with its output in `dim.out`: depth over the C/ROOM travel, tolerance, what it does to
  CRSB, the switching step, noise;
- `sim_console.py`: a new `dim` test on the whole console;
- TI's models (OPA161x, OPA1656, DRV134, TL07xH) on the master deck: `sim/review/master/run_each.py none` with three
  new configurations (`p100_dim`, `p075_dim`, `p100_dim_out47`);
- the netlist checks and `check_all --full` on a trial tree.

## 1. Why, and what it reverses

**The library.** The Delta has a −20 dB dim on the control room (ED2780: R90 / R190, S3 / S4; with cut on talkback).
Series Five dims with a J112 shunt (4K7 / 470R), Sapphyre with a J111 and 1K. Ours has none (`console_survey.md` CS7,
`docs/console_survey/delta.md` T17).

**What it reverses.** `console_architecture.md` lists "monitor dim" under **Excluded** (with SIP and per-channel
meters). Signing this off moves it to Included.

## 2. The circuit

```
CRS follower ─ 100R ─ CRSB_L ─┬─ PHONES pot, meter feed (unchanged)
                              └─ R236 91K ─ CRP_L ─ C/ROOM pot top (RV5)        (R side: R237, CRP_R)
                                 └─ SW4 pole A across R236: released = short (full level), latched = open (DIM)
```

- **The key:** SW4, a C&K PVA2 like EXT. Each pole's common goes to CRSB, its released throw to CRP; the latched
  throws are left unconnected. So the key carries audio, as the master's EXT key already does, and there is no LED
  (EXT has none either).
- **Parts:** SW4, R236 / R237 91K 1 % 0805, a grey PV cap. They are made last (after `drv_loop_rs()`), so no other
  ref moves. The C/ROOM pot's tops are now CRP_L / CRP_R.
- **Only C/Room:** PHONES and the meters stay on CRSB.
- **The schematic:** on page 16 (CONTROL ROOM), each pole drawn across its resistor.

## 3. What it does (`dim.py`, `sim_console.py`)

**Depth** at the C/ROOM wiper (into the follower's 100K):

| C/ROOM rotation | 1.0 | 0.9 | 0.8 | 0.7 | 0.6 | ≤ 0.5 |
|---|---|---|---|---|---|---|
| dim | −20.75 dB | −20.52 | −20.33 | −20.19 | −20.09 | −20.0 |

- **Tolerance:** ±0.08 dB for a 1 % RD, so L and R stay within 0.17 dB of each other. The dual pot's own tracking is
  larger.
- **The whole console** (`sim_console`, new test): −20.75 dB on C/Room L and R with C/ROOM at the top.
- **Phones and meters:** +0.08 dB while dimmed, because the C/ROOM pot no longer loads the CRS build-out.

**The switching step.** The CRS follower's output offset sits on CRSB. TI's OPA1656 model gives 0.50 mV. Pressing
or releasing DIM moves the pot-top DC, and the wiper's 2.2 µF passes that on as a step, which then decays with
2.2 µF × 100K (0.22 s).

| C/ROOM | step at the C/Room follower | at the TRS output (DRV135 +6 dB) |
|---|---|---|
| top | 0.44 mV, −65 dBu | −59 dBu |
| 0.7 | 0.21 mV, −71 dBu | −65 dBu |
| 0.5 | 0.06 mV, −81 dBu | −75 dBu |

It is mostly sub-audio (a step through a 0.72 Hz high-pass). The PFL switcher's tick, for comparison, is estimated
at −89 to −70 dBu (master spec §19). If the bench finds the dim's step audible, a DC block ahead of the pot top would
remove it: a 10 µF NP per side, which is not in this patch.

**Noise.** While dimmed, RD's Johnson noise at the follower is −113.4 dBu (8.3K at the wiper; −107.4 dBu at the TRS
output). That is more than 10 dB under the dimmed mix noise of 24 routed strips. Released, RD is shorted and nothing
changes.

**Not changed:** the main outputs, mono, phones, meters, PFL / EXT selection, the mute relays. No power is drawn.

## 4. Stability (TI's models, master deck)

TI's OPA161x, OPA1656 (TI's own model, not a stand-in), DRV134 and TL07xH models, `run_each.py none`:

| Configuration | U23A / B (C/Room followers) | U21A / B (CRS followers, the master's worst) |
|---|---|---|
| p100, DIM released (trial netlist) | 83.4°, 0.44 dB | 47.7° |
| **p100_dim** (every pot at the top, DIM latched) | **84.8°, 0.32 dB** | **49.7°** |
| **p075_dim** | **84.6°, 0.34 dB** | **54.9°** |
| p100_out47, released | 61.9°, 1.52 dB | 49.0° |
| **p100_dim_out47** (+47 pF on every output) | **61.1°, 1.33 dB** | **48.6°** |

- **The C/Room followers:** DIM raises the wiper's source impedance to 8.3K, and the 22 pF at their + inputs (MG5)
  holds it: the margin rises by 1.4°, and loses 0.8° with 47 pF on the outputs.
- **The CRS followers:** CRSB carries less load while dimmed (49.7° against 47.7°).
- **Released:** the trial netlist reads exactly as the committed one, unit for unit, in p100 and p100_out47.
- **Every other unit** is within 0.4° (the post-amps U5A / B 64.3 → 63.9°).

## 5. Placement (trial)

**The key:** SW4 at sw(29.16, 178), so its actuator sits in the EXT row, right of the POWER LED (x 19). The panel row
reads POWER | DIM || EXT | PFL ACTIVE.

**What had to move.** The spot held main R's DRV135 (U8). Its loop parts sat under the key: C48 had a pad where SW4's
pin 3 goes, and R225 sat between the key's pads. U8 can't stay on the top within reach of its parts: the nearest top
spot is 10 mm away, with its decouplers 10-14 mm from their pins. So U8 goes to the bottom beside the key, with its
loop and decoupling parts. A joint search (`U8` on either side and any rotation, then its couplers, 22Rs and
decouplers) picked the spot with the shortest loops:

| Part | was | now |
|---|---|---|
| U8 DRV135 | top, (34.74, 178.75) | **bottom**, (37.0, 174.0), 90° |
| C47 / C48 10 µF (couplers) | bottom | bottom, (43.25, 169.5) / (37.75, 182.0) |
| R224 / R225 22R (CS4c) | top / bottom | top, (39.75, 171.5) / (39.75, 176.5) |
| C49 1 µF +VA | top | top, (35.0, 171.5), over its pin |
| C50 1 µF −VA | top | bottom, (32.75, 170.0) |
| R236 / R237 91K | — | bottom, (30.5, 177.75) / (30.5, 183.75), 2.8 mm from each key pin |

| | committed | trial |
|---|---|---|
| + leg (pin 8 → 22R → 10 µF → +Sense) | 10.2 mm | 9.0 mm |
| − leg (pin 1 → 22R → 10 µF → −Sense) | 10.5 mm | 9.8 mm |
| C49 / C50 pad to supply pin | 4.3 / 4.0 mm | 0.1 / 2.4 mm |
| outputs to the mute relay K2 (MAIN_R_N / P) | 6.0 / 14.0 mm | 9.4 / 20.4 mm |

- **Vias:** each 22R is now on the other side from U8, so each leg crosses once. CS4c's check allows 30-240 nH of
  in-loop track; these legs are about 10 nH.
- **The couplers** stay on the bottom (11.5 mm panel gap).
- **Everything else** is where it was: 620 footprints, only these 7 moved and 3 new. The placer report is unchanged
  (decouplers 3.1 / 11.5 / 20; high-Z inputs 7.9 / 97.0 / 72).

**A placer change was needed.** U8's new spot overlaps C48's old one, and C48's new spot overlaps U8's old one. The
guard used to check each move against the parts not yet moved, so neither order passed. Now every moved part leaves
its packed spot first. Each is then placed and checked against everything already placed, so every pair is still
checked once.
- **Checked:** the strip, group, both jig boards and the group jack board re-place identically, part for part.

**Panel:** a Ø8 hole at (30.31, 325) on the panel drawing, with "DIM" above it. `panel_fab`'s checks: master 0
problems (77 holes).

## 6. Checks on the trial tree

`check_all --full`: **61 / 61.**
- **Master:** 1796 pins / 620 parts, 0 mismatches, check_fp 0, ERC 0; 0 DRC / parity; 620 / 620 footprints linked;
  route_check 0.
- **`sim_console`:** 38 / 38 (three new dim checks). The other boards are unchanged (1517 / 1517 links in all).
- **Panel checks:** strip, group and master 0.
- **Netrules:** re-run; the master's classes are unchanged (CRP_L / CRP_R are Default, like CRSB).

## 7. On sign-off

- Apply the patch, regenerate and re-export the master (netlist, BOM, PDF), re-place it, re-run netrules,
  `export_3d.py` for the master, `panel_fab.py` and `order_bom.py`.
- **Update:**
  - `console_architecture.md` (monitor dim from Excluded to Included);
  - master spec §20 (C/Room) and §23 (parts);
  - `offboard_bom.md` (one more grey PV cap on the master);
  - `console_survey.md`, CLAUDE.md.

## Sign-off

- [x] **CS7** as proposed (Ruslan, 2026-10-28): DIM on C/Room, −20 dB (R236 / R237 91K across SW4), key beside POWER; U8's group on the
  bottom beside it.
- [ ] As proposed, plus a 10 µF NP DC block ahead of each C/ROOM pot top (removes the switching step).
- [ ] Neither: keep monitor dim excluded.

## Applied (2026-10-28)

- **Applied:** the patch.
- **Regenerated and re-exported:** the master schematic (1796 pins, 620 parts, 0 mismatches, check_fp 0, ERC 0), its
  netlist, BOM (+ SW4 PVA2, 2 × 91K), PDF and `order_bom.csv` (PVA2 371, Yageo RC0805FR-0791KL 12).
- **Re-placed:** identical to the trial (SW4, R236, R237 new; U8's group of 7 moved; nothing else). The master jack
  board's file only reordered, so it is unchanged. Netrules re-run (classes unchanged).
- **Panel:** `render/master.json` re-exported, `panels/master.*` regenerated (77 holes, "DIM" beside POWER, 0 problems).
- **Documents:** `console_architecture.md` (DIM moved from Excluded to Included), master spec §20 / §23,
  `offboard_bom.md` (PVGY 194), `console_survey.md`, CLAUDE.md.
- **`check_all --full`:** 61 / 61 (master 1796 pins, 620 / 620 linked, 0 DRC / parity; `sim_console` 38 / 38; 1517 / 1517 links in all).
