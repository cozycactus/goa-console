# DIY Mixing Console — Architecture Document v3.0
## Goa Trance Production Console, 24+ Channels, Line Level

---

## 0. What changed in v3.0

v3.0 is based on a full read of all 17 pages of the Soundcraft Delta DLX / Theatre
schematic set (ED2911, ED2915, ED2776, ED2778, ED2779, ED2780, ED3151, ED3344). Since 2026-10-23 also the
Soundcraft 200 Delta Technical Manual (ZZ2593, `ref/Soundcraft_200Delta_TechManual_ZZ2593_Part1-3.pdf`, scanned):
loom pinouts, connector pinouts, jumper settings, spare-parts lists, dimensions.

**Corrections to v2.0**
- The 2SB737 transistors in the Delta mix summing amp (ED2780 sh.2) are a **low-noise
  discrete input stage**, not bus protection. v2.0 called them "2SD737 bus protection".
- The 43K resistors in ED2780 belong to the **monitor-select differential receivers**,
  not the mix summing amp. v2.0 listed them as "mix sum input R".
- The v2.0 IDC pinout was my own invention. It is replaced by the **real Delta motherloom
  pinout** (section 2), read from ED3344C and checked against ED2915A.

**New, taken from the Delta drawings**
- Ground-cancel line on the bus (pin 26): one wire that rejects ground-potential
  differences between strips and master. Replaces the 50-pin SSL-style balanced bus option.
- Unassigned routing resistors are grounded, not left floating (constant pan-buffer load, no
  floating resistor picking up crosstalk). Note: this does **not** keep the bus noise gain
  constant; noise rises with each channel routed (section 2.4).
- All bus feeds AC-coupled (220 µF + 47K bleed), so routing switches never click.
- Pan buffers after the pan pot.
- Click-free JFET mute (J112 pair with RC ramp).
- Separate logic supply and logic ground on every strip.
- Per-module ¼" spade terminal for heavy audio ground.

**New from design review**
- Ground-compensated (differential) line input on every channel.
- 47–100 pF feedback capacitor on every bus summing amp.
- Bus fed from the middle of the console.
- Isolated jacks so chassis ground meets audio ground only at the star point.
- Six dedicated aux pots (no Shift 5/6), Aux 5/6 optionally a stereo pair.
- Insert jacks on the four subgroups.
- Stronger PSU regulators.

---

## 1. Design Philosophy

- Delta-style IDC ribbon motherloom, daisy-chained strip to strip. No backplane PCB.
- **Delta-compatible bus pinout**: a real Delta module could in principle sit on the same ribbon.
- One identical PCB per channel strip: a Delta Theatre input without the mic stage (line gain, HPF,
  4-band EQ, direct out); see `delta_clone_comparison.md`.
- Insert point on every channel for external processing (EQ, compressor, effects).
- All sources are synths at line level.
- Rails: ±16 V or ±17 V (decide with the PSU design; see section 3).
- OPA1612 in noise-critical stages (summing amps, input receiver, fader post-amp).
- SSL-style stereo bus compressor patched into the master insert.

---

## 2. Bus — 34-pin IDC Motherloom (real Delta pinout)

Read from ED3344C (Theatre input, CN2 "MOTHERLOOM") at 400 dpi, consistent with
ED2915A (stereo input). Ribbon conductor order = pin number.

| Pin | Delta signal | Use in this console |
|-----|--------------|---------------------|
| 1 | GRP 8 | spare (reserved) |
| 2 | GND | GND |
| 3 | GRP 7 | spare (reserved) |
| 4 | GND | GND |
| 5 | GRP 6 | spare (reserved) |
| 6 | GND | GND |
| 7 | GRP 5 | spare (reserved) |
| 8 | GND | GND |
| 9 | GRP 4 | SUB 4 |
| 10 | GND | GND |
| 11 | GRP 3 | SUB 3 |
| 12 | GND | GND |
| 13 | GRP 2 | SUB 2 |
| 14 | GND | GND |
| 15 | GRP 1 | SUB 1 |
| 16 | GND | GND |
| 17 | MIX R | MIX R (200 Delta manual: Mix left, see below) |
| 18 | MIX L | MIX L (200 Delta manual: Mix right) |
| 19 | unused | spare |
| 20 | AUX 6 | AUX 6 |
| 21 | AUX 5 | AUX 5 |
| 22 | AUX 4 | AUX 4 |
| 23 | AUX 3 | AUX 3 |
| 24 | AUX 1 | AUX 1 |
| 25 | AUX 2 | AUX 2 |
| 26 | GND CANCEL | GND CANCEL (see 2.2) |
| 27 | PFL+ | PFL |
| 28 | PFL− | PFL− (stereo returns only); 200 Delta manual: "PFL Audio −VE" |
| 29 | PFL DET | PFL DET |
| 30 | −17 V | −V |
| 31 | −17 V | −V |
| 32 | +17 V | +V |
| 33 | +17 V | +V |
| 34 | +48 V | **not connected** — no phantom in this console |

Confidence: pins 1–27 and 29–34 read clearly. Pin 28 (PFL−), first inferred from the
stereo-input sheet, is confirmed by the 200 Delta Technical Manual (p. 134, "Motherloom, 34 way IDC loom":
27 PFL Audio +VE, 28 PFL Audio −VE). Note AUX 1/AUX 2 are on 24/25, not in numeric order.

MIX L / R: the two Soundcraft sources disagree. ED3344C (Theatre input, CN2) labels the trace to pin 17 "R"
and the one to pin 18 "L" (re-read at 600 dpi on 2026-10-23: odd pins in the top row, pin 1 at the right, GROUP 1-4
on 15/13/11/9, "L" beside the trace to bottom-row pin 18, "R" beside the one to top-row pin 17). The 200 Delta
manual's loom table (p. 134) lists 17 = Mix left, 18 = Mix right. Every other pin agrees between the two (groups
1-8 on 15/13/11/9 and 7/5/3/1, AUX 6..1 on 20-25 with AUX 1/2 on 24/25, GND cancel 26, PFL 27/28, PFL detect 29,
±17 V on 30-33, +48 V on 34). Decision (Ruslan, 2026-10-23): keep the ED3344C order, MIX R = 17 and MIX L = 18.
Our strips, groups and master all use it, so the console is consistent either way; only a real Delta module
built to the 200 Delta order would have its L and R swapped on this bus.

### 2.1 Observations from the real pinout
- Only the group buses have ground wires between them (pins 2–16).
- MIX L/R and AUX 1–6 sit on adjacent conductors (17–25) with no ground between them.
  Soundcraft relied on all buses being at virtual earth (very low impedance), which keeps
  capacitive crosstalk low.
- The four spare group pins (1, 3, 5, 7) and pin 19 are free for future use
  (e.g. a mute-group line, SIP, or more subgroups).

### 2.2 Ground cancel (pin 26) — the Delta's anti-hum system
- On every module, local audio ground connects to pin 26 through a **10 Ω resistor**
  (R141 on ED3344C, R75 on ED2915A, labelled "GND CANCEL RES").
- In the master section, the summing amps reference the ground-cancel line instead of
  the master's own ground (see "GROUNDCANCEL" on ED2779A and ED2780).
- Any ground-voltage difference between a strip and the master appears on both the bus
  signal and the reference, and the summing amp rejects it.
- Cost: one 10 Ω resistor per module and one wire. It does the job that SSL's
  impedance-balanced bus does, without doubling the bus conductors.
- **Decision:** adopt ground cancel. The 50-pin balanced-bus option from v2.0 is dropped
  unless the test jig (section 9) shows ground cancel is not enough.

### 2.3 Bus topology
- Virtual-earth summing in the master; every bus wire sits at ~0 V.
- Summing resistors: 10K for MIX and SUB, 22K for AUX and PFL (Delta values).
- **Unassigned routing resistors are grounded** to a clean ground by the off position of
  the routing switch (ED3151, ED3344C). The switch sits at the bus end of the resistor,
  so an unassigned resistor is taken off the bus and its free end tied to ground. Result:
  the pan buffers see a constant load, and no floating resistor picks up crosstalk. The
  bus noise gain still rises with every channel routed (1 + N for unity-gain summing).
- Every feed into the bus is AC-coupled (220 µF + 47K bleed) so no DC reaches the
  routing switches.
- **Feed the bus from the middle**: put the master in the centre (12 strips each side), or
  bring both ribbon ends into the master. This halves worst-case cable length.
- Cable: 34-way flat ribbon, 28 AWG, one per wing, with a crimped IDC socket at each strip
  position (daisy chain). One shrouded, keyed 34-pin header per strip, as the Delta.

### 2.4 Bus noise budget (calculated, 20 Hz–20 kHz unweighted)
Unity gain per channel (Rf = R), output noise of the summing amp:

| Channels routed | Noise gain | OPA1612 | NE5534 | NE5532 | TL072 |
|-----------------|------------|---------|--------|--------|-------|
| 1  | 2 (6 dB)   | −106.8 dBu | −108.8 | −108.0 | −102.7 |
| 8  | 9 (19 dB)  | −102.1 | −100.8 | −99.3 | −90.3 |
| 16 | 17 (25 dB) | −99.4 | −96.7 | −94.7 | −84.9 |
| 24 | 25 (28 dB) | −97.6 | −94.1 | −91.8 | −81.6 |

- With 24 channels routed, the **summing resistors' own thermal noise dominates**: an ideal
  noiseless op-amp would still give −98.6 dBu. The OPA1612 adds only 1 dB on top of that.
- Lower summing resistance lowers the floor (OPA1612, 24 channels):
  22K −94.3 dBu, **10K −97.6 dBu**, **4K7 −100.4 dBu**, 2K2 −102.5 dBu.
- Because every strip now has pan buffers, MIX and SUB can use **4K7 summing resistors with
  4K7 feedback** (2.8 dB quieter). Each pan buffer then drives 3 × 4K7 = 1.57K, which an
  OPA1612 handles easily. Aux buses stay at 22K, because the aux pot wipers would otherwise
  be loaded and their taper bent.
- Trade-off: 4K7 departs from the Delta's 10K, so a genuine Delta module on the same ribbon
  would sum about 6.6 dB low. **Chosen: 4K7 (quieter).** The master MIX/SUB feedback resistors must also be 4K7. Revert both to 10K if Delta compatibility ever matters.
- These figures cover the bus amp only. Each routed channel also adds its own strip noise,
  which grows by 10·log(N) and will dominate in practice with all faders up.

---

## 3. Power and Grounding

### 3.1 Rails
| Rail | Voltage | Notes |
|------|---------|-------|
| +V | +16 V or +17 V | Delta uses ±17 V; ±16 V matches the 500-series spec |
| −V | −16 V or −17 V | |
| +48 V | none | Pin 34 left unconnected |

### 3.2 Distribution (Delta method)
- ±V on the ribbon: two conductors per rail (pins 30–33).
- Heavy audio ground does **not** use the ribbon: each strip has a ¼" spade terminal
  (Delta CN4) wired to the ground bus bar: one 14 AWG wire per module, tied under the motherloom to its wing's copper
  bar under the master's star stud (`ground_study.md` G1, master spec §26).
- Local decoupling on every strip: 10 Ω series + 220 µF/25 V + 100 nF per rail.
- Load (strip v4.0, 2026-10-22): about 85 mA (+V) and 72 mA (−V) per strip, typical: 10 × OPA1612
  at 3.6 mA per channel, the DG413 logic supply, and the panel LEDs (ON, EQ, routing; 3.1 mA each).
  The worst case is about 127 / 90 mA, with OPA1612 at 4.5 mA/ch and every LED lit including OL.
  That's about 2.0 / 1.7 A for 24 strips (v3.1 was 30 mA per strip). Per 12-strip wing, about 1.0 A
  on +V, so 0.5 A per ribbon conductor: within a 28 AWG conductor's and an IDC contact's ~1 A.
  The DC drop along a 0.5 m wing fed from the master end is about 0.03 V. The strips' 10 Ω
  series resistors drop about 0.8 V; the strip rails sit near 16.2 V. The 10 Ω and 220 µF
  take care of transients. Consequences for the master power entry: master spec §27.
- If the test jig shows supply noise coupling into the bus, fall back to separate
  18–20 AWG power wiring and leave pins 30–33 unused.

### 3.3 PSU
- External PSU, outside the console chassis: two isolated Mean Well LRS-150-24 at 21.6 V, LC filter,
  LM1084-ADJ post-regulators as identical floating rails, TL431/SCR crowbar at 19.1 V and soft start
  per rail (chosen 2026-10-22; `psu_spec.md`, `sim/psu.cir`, `psu.kicad_sch`).
- Target ±17 V at **4 A per rail** (2026-10-22, strip v4.0). The console draws about 2.65 / 2.23 A
  typical and up to 3.8 A on +V: master spec §27.
- Regulators rated at least 4 A per rail. +V: an LM338 (5 A). −V: the LM337 is a 1.5 A part, so
  boost it with an external PNP pass transistor, or use a discrete series regulator. Heatsinks for
  about 20 W per rail (24 V unregulated in, 17 V out, 3 A).
- Transformer and rectifier sized for 4 A DC per rail. A capacitor-input filter needs the
  secondary rated at about 1.6 × the DC current: about 6.5 A RMS per winding, so ≈ 2 × 18 V,
  roughly 230 VA.
- Link to the console: 7-pin XLR (Neutrik NC7MD-LX on the console, 5 A per contact): pin 1 earth,
  2–3 +V, 4–5 0 V, 6–7 −V. That's two contacts per rail; 1.0 mm² (18 AWG) per pin.
- Soft start; power-on mute handled in the master (section 4.1).

### 3.4 Grounding — three domains, one star point
- **Audio ground:** signal path, summing resistors, pot grounds, op-amp references.
- **Logic ground:** LEDs, mute logic, PFL detect, OL comparator. The Delta gives logic its
  own supply (+VM/−VM via 10 Ω and 47 µF) and its own "LOGIC GROUND" (ED3344B). Copy this.
- **Chassis ground:** enclosure and connector shells.
- All three meet only at the star point at the PSU / main ground bar.
- Use **isolated jacks** (e.g. Neutrik NJ6FD-V or other plastic-bodied types) so jack sleeves
  don't short audio ground to the metal panel at every jack.
- Balanced-input jacks (strip line in and direct out, group returns, master EXT) have their sleeves on **chassis**
  at the jack board, bonded through plated standoffs to the panel (AES48, as the XLRs' pin 1); inserts and phones keep
  audio ground (`ground_study.md` G2, 2026-10-25). Cable-shield currents from earthed synths then never flow through an
  audio ground. The strip's receiver has input followers (1 MΩ common mode, G3) so a synth's output impedance doesn't
  spoil its rejection; use pseudo-balanced TRS cables from synths.
- Ground-cancel line (pin 26) per section 2.2.

---

## 4. Master Section

### 4.1 Stereo mix
- Summing amps L and R: low-noise, inverting. The channel path is non-inverting, so the
  master must re-invert once (as the Delta does) to keep absolute polarity.
- Summing amps L and R: low-noise. Either OPA1612, or a discrete front end like the Delta
  (2SB737 pair + NE5532, ED2780 sh.2).
- Non-inverting input referenced to the **ground-cancel** line.
- 47–100 pF across the feedback resistor (ribbon capacitance at the virtual-earth node).
- Master insert (TRS, normalled) for the bus compressor.
- Stereo master fader, balanced outputs L/R (DRV134), mono sum output.
- **Power-on/off mute relay** on the main outputs (and the control-room and phones outputs, 2026-10-23): closes
  2–3 s after the rails are up, opens immediately when they drop; a released relay grounds the line.

### 4.2 SSL bus compressor (external, via master insert)
- Clone of the SSL 4000 bus compressor (Gyraf design). The Gyraf uses THAT 2181 VCAs, which went
  end-of-life (THAT memo, 1 Sept 2026; Mouser lists 2181AL08-U as EOL, 0 in stock, 569 on order
  from the last-time buy, backorderable, October 2026).
- **VCA (October 2026): Sound Semiconductor SSI2162** (dual, in production). Both channels in one
  package, matched to 0.07 dB at 0 dB and 0.24 dB at −40 dB, which suits a stereo-linked bus
  compressor. Datasheet figures (±15 V class): ±4 to ±18 V supply; gain +20 to −100 dB;
  ground-referenced control, −33 mV/dB (−3300 ppm/°C); control feedthrough −60 dB.
  Class AB output noise −99 dBu with 10K in/out, −105 dBu with 3.74K; THD 0.05 % at 0 dB,
  0.045 % at −20 dB (class A: 0.025 % at 0 dB, but −88 dBu noise at 10K). Headroom +22 dBu.
- Consequences for the Gyraf circuit:
  - Control scaling: THAT 2181 is 6.1 mV/dB, SSI2162 is 33 mV/dB, so the sidechain's control
    output must be 5.4 × larger (20 dB of gain reduction = 0.66 V). Opposite-polarity port
    conventions must be checked when the sidechain is drawn.
  - Current-in/current-out like the 2181: 10K input resistor, output into a virtual-earth I/V
    op-amp (output compliance only ±100 mV), as in the Gyraf.
  - No symmetry/THD trim (the SSI2162 has none); a mode resistor sets class A/AB — use AB.
  - Distortion is about 20 × the 2181A's 0.0025 %. That is the price of a part still made.
- Decided October 2026: SSI2162. (Considered and rejected: building the Gyraf unchanged with
  THAT 2181A bought on backorder from last-time-buy stock.)
- Controls: threshold, ratio 2/4/10:1, attack 0.1–30 ms, release 0.1–1.2 s + auto, makeup.
- Built as a separate 1U unit.

### 4.3 Subgroups (×4)
- Summing amps referenced to ground cancel, feedback cap as above.
- **Insert jack on each subgroup** (the Delta group output has one, ED2778A).
- Sub faders, assign to main L/R, balanced outputs (DRV134).

### 4.4 Aux masters (×6)
- Summing amps referenced to ground cancel.
- Master level, balanced outputs (DRV134).
- AFL on each aux master (switch + 22K to the PFL bus).

### 4.5 Aux returns (×4 stereo)
- Level, assign (main / subs), solo.

### 4.6 Monitoring
- PFL summing amp, PFL detect with auto-switch, solo level.
- Monitor source: main mix / external input (DAW A/B).
- Control-room output with level, headphone amp.
- Rude solo LED.
- Main L/R meters: comparator LED ladder with peak/average link, as the Delta
  (ED2779B / ED2780 sh.3, LM139 / LM2901).

---

## 5. Op-Amp Selection

| Position | Op-amp | Reason |
|----------|--------|--------|
| MIX L/R summing amps | OPA1612 | Many channels routed: low voltage noise matters (section 2.4) |
| SUB / AUX summing amps | OPA1612 | An aux bus always carries every strip's 22K (noise gain 25), where the OPA1612 is quietest: −94.3 dBu vs −92.5 (NE5534) and −92.3 (OPA1656); ±17 V is also above the NE5534's recommended ±15 V (master parts review, 2026-10-23) |
| PFL summing amp | OPA1656 | Switched bus, 1–4 sources: no current noise, 1.6–3.6 dB quieter than the OPA1612 |
| Channel input receiver | OPA1612 (THAT1246 is end-of-life, Sept 2026) | Ground-loop rejection, low noise |
| Fader post-amp | OPA1612 | Critical path |
| Pan buffers | OPA1612 or NE5532 | Drive the routing resistors |
| Balanced outputs | DRV134 | Floating-style balanced driver, one part per output (replaces the Delta NE5532 EBOS; THAT1646 went end-of-life Sept 2026) |
| Headphone amp | OPA1612 + LME49600 (composite) | 250 mA output inside the op-amp's loop (master spec section 21) |
| Monitor (CRS) followers | OPA1656 | FET input after the DG413 PFL switch: a bipolar part's bias current would step CRS at every switch |

PSRR at audio frequencies (not DC) is the deciding figure: about 45 dB at 10 kHz for
the NE5532 versus about 80 dB for the OPA1612.

---

## 6. Features

### Included
- 24+ identical channel strips (section 7)
- 4 subgroups with inserts, faders, assign to main
- 6 aux masters with AFL
- 4 stereo aux returns
- Stereo mix with master insert, master fader, mono out, mute relay
- Control room, headphones, PFL with auto-switch, rude solo LED, LED meters
- External monitor input

### Excluded
- Mic preamps, phantom (trim, HPF, EQ and direct outs added back on 2026-10-22, Delta clone)
- Talkback, oscillator, tape I/O
- SIP (PFL only), per-channel meters, monitor dim
- Per-channel dynamics (use inserts)
- Transformers, in-line monitoring, cue/foldback

### Borrowed from SSL / Neve
| Feature | Source | Status |
|---------|--------|--------|
| Bus compressor | SSL | External, via master insert |
| AFL on aux masters | SSL / Neve | Included |
| Star grounding, 3 domains | SSL / Neve (and Delta) | Included |
| Power-on/off mute relay | SSL / Neve | Included |
| VCA module option on the strip | SSL | Unpopulated; SSI2162 plug-in module (strip spec 7.1) |
| Impedance-balanced bus | SSL | **Replaced by Delta ground cancel** |

---

## 7. Channel Strip — Summary

Full component-level detail is in `channel_strip_schematic_spec.md`.

```
Line in (TRS) → differential receiver → insert send (75 Ω)
             → [external gear] → insert return (normalled)
             → buffer ─┬─ pre-fade: Aux 1-2, PFL
                       └─ soft mute (JFET) → fader → [VCA option] → fader post-amp
                            ─┬─ post-fade: Aux 3-6 (AC-coupled)
                             └─ pan → pan buffers L/R (AC-coupled)
                                  → routing switches (off = grounded) → 10K → bus
```

---

## 8. Mechanical

- Strip: 8 HP × 12U Eurorack-style panel (40.3 × 514 mm), custom frame with rails only at the panel
  ends; jacks on the panel, on a small jack board ~24 mm deep with a 10-way ribbon to the main board
  (`strip_panel_study.md`). 24 strips ≈ 975 mm plus master.
- Master in the centre (bus fed from the middle).
- 100 mm faders. Channel I/O on the panel (no rear apron). Isolated jacks.
- One spade ground terminal per strip.

---

## 9. Test Plan (before ordering 24 boards)

Detailed jig, tests and targets: `test_jig_spec.md`.

Build 4 channel stubs and 1 master stub. Compare:

| Config | Bus |
|--------|-----|
| A | Delta unbalanced, no ground cancel |
| **D** | **Delta unbalanced + ground cancel (pin 26)** — the expected winner |
| B | SSL-style copper bus, impedance-balanced (reference) |
| C | Ribbon, impedance-balanced (only if D disappoints) |

Measurements:
1. Noise floor (inputs shorted, RMS + FFT)
2. Hum (ribbon near mains; inject a deliberate ground loop through a synth)
3. Crosstalk between adjacent buses (17–25 are not ground-separated)
4. PSRR (AC injected on the rail; power on ribbon vs separate wiring)
5. THD+N with all channels driven
6. Click test: toggle every routing and mute switch with signal present

Also simulate in KiCad/ngspice first: summing-amp noise vs channels, and pan law under
bus load.

---

*Document version 3.1 — October 2026 (4K7 summing and +10 dB fader post-amp chosen; channel strip schematic generated and simulated)*
*Sources: Soundcraft Delta DLX/Theatre schematics (all 17 pages), SSL 4000, Mackie CR1604-VLZ*
