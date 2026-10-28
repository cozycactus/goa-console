# Film couplers and audio bipolar electrolytics — proposal

Proposal for sign-off, 2026-10-24. **Signed off by Ruslan the same day (F1–F4 as proposed) and applied:** strip v4.2,
master spec v0.8 note, every board regenerated (0 mismatches, check_fp 0, ERC 0), `sim_netlist.py` 30/30,
`sim_console.py` 32/32, strip / group / master / jig re-placed with 0 DRC violations and 0 parity issues. (When written,
nothing in the design had changed.) The generator and layout edits are in
`archive/patches/film_np_proposal.patch`. They were trial-applied in a throwaway worktree: regenerated, verified, simulated and
re-placed (results below).

Scope, as decided in the discussion:
- **No DC coupling:** every coupling cap stays where it is.
- **X7R in the signal path → film:** every X7R ceramic in the audio path becomes polyester film.
- **Bipolar electrolytics → an audio series:** Nichicon MUSE ES.

## Why

- **X7R couplers.** The 2.2 µF wiper couplers into 100K carry about 3.6 % of the signal at 20 Hz. X7R's capacitance
  changes with voltage, so they are the one coupling cap with a measurable distortion mechanism.
- **Polyester rather than polypropylene.** Polypropylene stops at about 0.33 µF on a 5 mm pitch; 2.2 µF in PP would
  need a 27.5 mm pitch.
- **Bipolar electrolytics.** They carry far less signal (a 220 µF into 4K7 sees 0.8 % at 20 Hz, 0.02 % at 1 kHz), so
  an audio series won't measure differently. The practical reason to change them is the parts themselves:
  - the BOM's Panasonic SU parts are listed as discontinued (RS), and Nichicon's standard UEP bipolars as not
    recommended for new designs;
  - MUSE ES is Nichicon's current bipolar audio series (16–50 V, 10–1000 µF).

## Parts

| Value | Part | Size | Footprint |
|---|---|---|---|
| 2.2 µF film (was X7R 1206) | **WIMA MKS2C042201K00KSSD**: PET, 63 VDC, ±10 %, bulk, 6 mm leads | 7.2 × 13 × 7.2 mm, 5 mm pitch | `Capacitor_THT:C_Rect_L7.2mm_W7.2mm_P5.00mm_FKS2_FKP2_MKS2_MKP2`, **bottom side** (13 mm tall; the top side has 11.5 mm to the panel) |
| 10 µF NP 25 V | **Nichicon UES1E100MDM** (MUSE ES) | 5 × 11 mm, 2.0 mm pitch | unchanged (`CP_Radial_D5.0mm_P2.00mm`) |
| 47 µF NP 25 V → **33 µF** | **Nichicon UES1E330MPM** (MUSE ES) | 8 × 11.5 mm, 3.5 mm pitch | unchanged (`CP_Radial_D8.0mm_P3.50mm`) |
| 220 µF NP 25 V → **100 µF** | **Nichicon UES1E101MPM** (MUSE ES) | 10 × 16 mm, 5.0 mm pitch | unchanged (`CP_Radial_D10.0mm_P5.00mm`) |

Sources: WIMA MKS 2 datasheet; Nichicon CAT.8100D (ES series: 25 V sizes, 85 °C 1000 h endurance with the polarity
inverted every 250 h).

**Why 33 µF and 100 µF.** At 25 V, MUSE ES 47 µF is a 10 × 12.5 can and 220 µF a 12.5 × 25 can. That trial placed on
the master and groups, but not on the strip: its bottom side between y 45 and 175 is full of pot pins and the
jack-board link, with no free 10 mm circle. 33 µF and 100 µF are exactly the current cans, so nothing moves.

Low-frequency cost (`tools/sim_console.py`, strip input to main XLR):

| | As built (47 / 220 µF) | Proposed (33 / 100 µF) |
|---|---|---|
| End to end, −3 dB | 1.5 Hz | 2.3 Hz |
| Level at 20 Hz (re 1 kHz) | −0.02 dB | −0.04 dB |
| Phase lead at 20 Hz | +9° | +14° |
| Direct out into 600 Ω, at 20 Hz | −0.26 dB | −0.53 dB |
| Direct out into 10 kΩ | flat | flat |

**Rating.** All stay 25 V, the console's electrolytic rule (≥ 25 V on ±17 V rails). The 16 V MUSE ES parts would
fit 47 / 220 µF in the current cans, but they leave no margin against an op-amp latched at a rail.

**Endurance.** 85 °C, 1000 h (standard bipolars are often 105 °C). Inside the tub (~40–45 °C) that extrapolates to
roughly 16 000 h or more. These caps carry no DC and almost no ripple, which is the gentlest duty an electrolytic gets.

## Where

**Film couplers** (X7R → film; all are wiper couplers into 100K, plus the master meter's averaging caps):

| Board | Refs | Per board | In the console |
|---|---|---|---|
| Strip | C13 (fader wiper → post-amp) | 1 | 24 |
| Group | C15 (sub fader), C37 (aux master), C56 / C62 (return level L/R) | 4 | 16 |
| Master | C29 / C35 (master fader L/R), C66 / C81 (aux 5/6), C106 (solo), C124 / C128 (C/Room), C138 / C147 (phones) | 9 | 9 |
| Master meter | C157 / C175 (average-mode ballistics, 2.2 µF): not audio, but X7R's bias loss shifted the 73 ms | 2 | 2 |

The strip's existing film C49 (2.2 µF, LF band) gets the same MPN. The meter's 1 µF peak caps (C160/C178) stay
X7R (spec 22 accepts them).

**Bipolar electrolytics** (MUSE ES):

| Board | 33 µF (was 47) | 100 µF (was 220) | 10 µF |
|---|---|---|---|
| Strip | 4: C10 insert return, C38 gain out, C51 insert send, C52 direct out | 4: C11 PRE, C15 POST, C16/C17 pan | — |
| Group | 4 | 6 | 4 (DRV134 Sense loops) |
| Master | 11 | 4 | 18 (14 in DRV134 Sense loops, 4 phones-rail bulk) |
| Console | 123 | 124 | 34 |

The jig stub's two 10 µF NP parts follow `master_lib` and become MUSE ES too.

## Placement impact (trial)

- **Film is THT now:** it replaces 1206 SMD parts on the top side.
  - The master's layout already sends every `C_Rect` part to the bottom.
  - The strip and group layouts need small edits:
    - **strip:** C13 and C49 get bottom-side zones;
    - **group:** its tall-part rule includes `C_Rect`, not only `CP_Radial`.
- **An existing fault, fixed on the way:** on the committed strip board, C49 (2.2 µF MKS2, 13 mm tall per WIMA) sits
  on the top side, under the 11.5 mm panel gap. It would hit the panel. DRC doesn't check heights, so nothing caught
  it. This proposal moves it to the bottom.

Trial results (KiCad 10.0.7, placement only):

| Board | DRC / parity | Decouplers (median / max / over 5 mm) | High-Z inputs (median / max / over 6 mm) |
|---|---|---|---|
| Strip | 0 / 0 | 3.1 / 10.0 / 11 (as committed) | 10.4 / 19.7 / 25 |
| Group | 0 / 0 | 3.1 / 4.5 / 0 | 9.1 / 20.1 / 17 |
| Master | 0 / 0 | 3.1 / 10.5 / 25 | 7.5 / 108 / 72 (as committed: U11 VREF6) |
| Jack boards | only the NJ6FD-V's own items | — | — |

- **Film distance to the op-amp + input:**
  - group 3.5–13.4 mm;
  - master 2.5–18.4 mm (the master fader couplers C29/C35 are the farthest, 17–18 mm, on the bottom under the
    post-amp);
  - strip C49 17.0 mm (was 21.5 mm, a known hot spot).

  These are high-impedance nodes. Route them short on the bottom, or move the cap under the op-amp by hand.
- **Depth:** the tallest new bottom-side part is the 16 mm 100 µF, the same can as today's 220 µF. The 13 mm film
  stays within that. The 3D model's tub floor is at −45 mm against −27 mm for the deepest parts.

Schematic checks in the trial:
- every board 0 mismatches, check_fp 0, ERC 0;
- `tools/sim_netlist.py` 30/30;
- `tools/sim_console.py` 32/32 (levels unchanged; the LF figures above).

## What to sign

- [x] **F1** X7R 2.2 µF couplers → WIMA MKS2C042201K00KSSD film, THT on the bottom side. That's strip C13; group C15,
  C37, C56, C62; master C29, C35, C66, C81, C106, C124, C128, C138, C147, and the meter averaging caps C157, C175.
  Strip C49 gets the MPN.
- [x] **F2** Bipolar electrolytics → Nichicon MUSE ES 25 V in the current footprints: 47 µF → 33 µF (UES1E330MPM),
  220 µF → 100 µF (UES1E101MPM), 10 µF → UES1E100MDM. This changes the signed "AC coupling 220 µF NP + 47K" value
  to 100 µF, for the LF costs above.
- [x] **F3** Layout rules: strip C13 / C49 on the bottom, the group's tall-part rule including film. Re-place strip,
  group and master (placement only), with parity DRC.
- [x] **F4** Docs:
  - strip spec §15 (BOM) and §17 (LF response);
  - master spec §15 / §23 parts summaries;
  - CLAUDE.md (the AC-coupling decision's values);
  - the BOMs.

Not proposed: keeping 47 / 220 µF in MUSE ES. The strip has no room for the 10 × 12.5 / 12.5 × 25 cans without moving
its coupling caps far from their op-amps. Nor polypropylene film, which is too large at 2.2 µF.
