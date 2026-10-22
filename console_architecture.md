# DIY Mixing Console — Architecture Document v3.0
## Goa Trance Production Console, 24+ Channels, Line Level

---

## 0. What changed in v3.0

v3.0 is based on a full read of all 17 pages of the Soundcraft Delta DLX / Theatre
schematic set (ED2911, ED2915, ED2776, ED2778, ED2779, ED2780, ED3151, ED3344).

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
| 17 | MIX R | MIX R |
| 18 | MIX L | MIX L |
| 19 | unused | spare |
| 20 | AUX 6 | AUX 6 |
| 21 | AUX 5 | AUX 5 |
| 22 | AUX 4 | AUX 4 |
| 23 | AUX 3 | AUX 3 |
| 24 | AUX 1 | AUX 1 |
| 25 | AUX 2 | AUX 2 |
| 26 | GND CANCEL | GND CANCEL (see 2.2) |
| 27 | PFL+ | PFL |
| 28 | PFL− | PFL− (stereo returns only; reading less certain) |
| 29 | PFL DET | PFL DET |
| 30 | −17 V | −V |
| 31 | −17 V | −V |
| 32 | +17 V | +V |
| 33 | +17 V | +V |
| 34 | +48 V | **not connected** — no phantom in this console |

Confidence: pins 1–27 and 29–34 read clearly. Pin 28 (PFL−) is inferred from the
stereo-input sheet. Note AUX 1/AUX 2 are on 24/25, not in numeric order.

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
  (Delta CN4) wired to the ground bus bar.
- Local decoupling on every strip: 10 Ω series + 220 µF/25 V + 100 nF per rail.
- Estimated load: ~30 mA per strip, ~0.75 A per rail for 24 strips. With two 28 AWG
  conductors per rail (about 0.1 Ω/m) and feeding from the middle, the DC drop is well
  under 0.1 V; the 10 Ω local resistors and 220 µF caps take care of transients.
- If the test jig shows supply noise coupling into the bus, fall back to separate
  18–20 AWG power wiring and leave pins 30–33 unused.

### 3.3 PSU
- External linear PSU, outside the console chassis.
- Target ±V at 2 A minimum per rail.
- Regulators rated at least 3 A: e.g. LM338 for +V, and an LM337 boosted with an external
  pass transistor for −V (a plain 7816/7916 at 1.5 A is not enough margin).
- Soft start; power-on mute handled in the master (section 4.1).

### 3.4 Grounding — three domains, one star point
- **Audio ground:** signal path, summing resistors, pot grounds, op-amp references.
- **Logic ground:** LEDs, mute logic, PFL detect, OL comparator. The Delta gives logic its
  own supply (+VM/−VM via 10 Ω and 47 µF) and its own "LOGIC GROUND" (ED3344B). Copy this.
- **Chassis ground:** enclosure and connector shells.
- All three meet only at the star point at the PSU / main ground bar.
- Use **isolated jacks** (e.g. Neutrik NRJ6HF or plastic-bodied types) so jack sleeves
  don't short audio ground to the metal panel at every jack.
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
- **Power-on/off mute relay** on the main outputs: closes 2–3 s after the rails are up,
  opens immediately when they drop.

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
| SUB / AUX summing amps | OPA1612 or NE5534 | NE5534 is quieter than OPA1612 with few channels routed (lower current noise) |
| Channel input receiver | OPA1612 (THAT1246 is end-of-life, Sept 2026) | Ground-loop rejection, low noise |
| Fader post-amp | OPA1612 | Critical path |
| Pan buffers | OPA1612 or NE5532 | Drive the routing resistors |
| Balanced outputs | DRV134 | Floating-style balanced driver, one part per output (replaces the Delta NE5532 EBOS; THAT1646 went end-of-life Sept 2026) |
| Headphone amp | NE5532 or TPA6120 | Output current |
| Monitor / PFL | NE5532 | Non-critical |

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

- Strip width ~40 mm; 24 strips ~960 mm plus master.
- Master in the centre (bus fed from the middle).
- 100 mm faders. All I/O on the rear. Isolated jacks.
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
