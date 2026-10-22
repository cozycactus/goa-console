# Master Section — Schematic Specification, v0.6 (draft)
## Part 1: stereo mix path, mono, main outputs, power-on mute
## Part 2: subgroups, aux masters
## Part 3: stereo returns · Part 4: monitoring · Part 5: power entry

Written to the same rules as `channel_strip_schematic_spec.md`; whole-console context is in
`console_architecture.md` section 4. Part 2 starts at section 12, Part 3 at 16, Part 4 at 17,
Part 5 at 24. Open items are in section 29.

Delta references: ED2780 sheet 2 (MIX SUM AMPS, MIX INSERT, FADER POST AMPS, BALANCED
OUTPUT AMPS, mono "GC O/P AMP") and sheet 1 (monitor-select differential receivers on MIX
L+/L−, master ground-cancel resistor).

---

## 1. Signal flow (one side; R identical)

```
MIX L bus (pin 18) ─ ferrite ─┬─ U1A summing amp, OPA1612, inverting, Rf 4K7 ∥ 100 pF
                              │    + input = GCANCEL (pin 26), direct
                              └─ output SUM_L  (= −Σ channels, referenced to GCANCEL)
SUM_L, GCANCEL_BUF ─ U1B differential re-inverter, unity, 4 × 2K2 0.1 %
                 output MIX_L (= +Σ channels, referenced to master AGND)
MIX_L ─ 75R ─ master insert send (tip) ─ [bus compressor] ─ return (ring, normalled to send)
      ─ 47µ NP + 47K ─ U2A buffer ─ 220µ NP + 47K ─ PRE_L
PRE_L ─ master fader (dual 100 mm, A10K) ─ 2.2µ + 100K ─ U2B post-amp +10 dB ─ 220µ NP + 47K ─ POST_L
POST_L ─┬─ U4 DRV134 balanced driver (+6 dB) ─ mute relay (series NO contacts) ─ XLR male MIX L OUT
        ├─ mono sum (with POST_R)
        └─ to monitoring and meters (later parts)
```

Polarity: the strip is non-inverting, U1A inverts and U1B inverts again, so MIX_L is in phase
with the channel inputs. The re-inversion the architecture asks for is U1B.

## 2. Mix summing amp (U1A)

- OPA1612, inverting. Inverting input on the MIX L bus through a ferrite bead (0805, ~220 Ω
  at 100 MHz; the Delta uses FB1/FB2 in the same place). No series resistor: it would add
  noise multiplied by the bus noise gain.
- Feedback 4K7 1 %, the same value as the strip summing resistors (decision: 4K7 bus).
  100 pF C0G across it.
- Non-inverting input connected **directly** to GCANCEL (pin 26). A bias-matching resistor
  would add noise at the full noise gain; OPA1612 bias current × 4K7 is under 1 mV of offset.
- No DC-blocking capacitor at the bus input. Every strip feed is AC-coupled, so the DC gain
  of this stage is 1. (The Delta's 1000 µF there protects a discrete input pair.)

## 3. Ground cancel at the master

- U1A's output is −Σ(channels) + V(GCANCEL): it is clean when read **relative to GCANCEL**,
  not relative to master ground. U1B reads it differentially and hands a clean signal to
  master ground. The Delta does the same job with differential receivers on MIX L+/L−.
- U1B: unity-gain difference amp, inverting input from SUM_L, non-inverting input from
  GCANCEL_BUF. Four 2K2 0.1 % resistors (or a matched quad network).
- **GCANCEL buffer (U9A, OPA1612 follower).** Thirteen re-inverters (MIX L/R, 4 subs, 6 aux,
  PFL) each load the line with 2K2 + 2K2, about 340 Ω in total. Driving that straight from
  the 0.42 Ω line (24 × 10 Ω) pulls it 0.12 % towards master ground, and the noise gain turns
  that into −31 dB of ground-difference leakage at 10 Hz. So one follower drives all the
  re-inverters' non-inverting legs (GCANCEL_BUF), while every summing amp's non-inverting
  input stays on the raw line, which then carries no current.
- **The master does not tie GCANCEL to its own ground.** Any tie pulls the line away from the
  strip grounds, and the bus noise gain (25 with 24 channels routed) multiplies that error.
  Simulated with a 22 Ω tie: a 1 V strip-to-master ground difference left −7 dB at the
  output. Without the tie and with the GCANCEL buffer: −71 dB at 10 Hz, −31 dB at 1 kHz.
  **Decided (October 2026): no tie.**
- The master's own audio ground still reaches the strips through the spade/ground bar, as the
  architecture specifies. Only the GCANCEL line stays free of a master-end tie.
- One GCANCEL wire serves MIX L, MIX R, the four subs, the six auxes and PFL. Each of those
  summing amps references it directly, and each has its own U1B-style re-inverter fed from
  GCANCEL_BUF.

## 4. Master insert

- Neutrik NRJ6HF, wired as the strip insert: send on tip through 75R, return on ring,
  ring normalled to send.
- Return: 47 µF NP + 47K bleed, OPA1612 follower (U2A), 220 µF NP + 47K to PRE_L.
- Nominal level at the insert is the mix level (about 0 dBu with channels at their "0" marks).
  The Delta runs its insert at −10 dBV. Ours stays at console level, because the bus
  compressor is our own design and can be built for it.

## 5. Master fader and post-amp

- Fader: Bourns PTB0144-2010BPA103 (100 mm, dual gang, A10K, metal lever). The dual-gang
  footprint is the PTB0143 one plus pins 1′ 2′ 3′ mirrored about the body centreline (same
  datasheet drawing). Wired with pin 1 = GNDA, as on the strips (A taper).
- Post-amp U2B: 2.2 µF + 100K input, gain 1 + 4K7/2K2 = +9.9 dB, 100 pF across 4K7. Same as
  the strip, so the "0" mark (−10 dB travel) is unity through the master.
- 220 µF NP + 47K to POST_L.

## 6. Mono

- U3A: inverting sum of POST_L and POST_R, 10K inputs, 10K feedback with 100 pF.
  A centre-panned mono source arrives at −6 dB in each side, so mono gives 0 dB for it.
  A hard-panned source also gives 0 dB.
- U3B: unity inverter (10K/10K) to restore polarity, then DRV134, relay, XLR.
- Optional mono fader is left out; mono follows the master fader.

## 7. Main outputs

- Driver: **TI DRV134** (SO-8) on every balanced output. **Decided October 2026**, replacing the
  THAT1646 chosen earlier, which THAT Corporation put on end-of-life on 1 September 2026
  (last-time buy closed 30 September). Both replace the Delta's cross-coupled NE5532 EBOS
  (ED2780 sheet 2, about 12 parts and a balance trim per output) with one IC.
- DRV134 (datasheet SBOS094B; TI lists it ACTIVE): +6 dB differential gain, and +6 dB
  single-ended with either leg grounded, so an unbalanced lead loses no level. ±4.5 to ±18 V,
  5.2 mA quiescent, output swing to within 2.5–3 V of the rails (about +27 dBu differential on
  ±17 V), 10K input impedance, OCMR 68 dB typical / 46 dB minimum, stable into up to 1 µF per
  output, ±85 mA short-circuit current. Output noise floor −98 dBu in 20 kHz, which adds
  about 1 dB to the mix output's −93 dBu differential.
- Pinout: 1 −VO, 2 −Sense, 3 Gnd, 4 VIN, 5 V−, 6 V+, 7 +Sense, 8 +VO.
- Connection, per output (TI Figure 29):
  - VIN from the stage before (POST_L, AUXn_OUT, …). It is a 10K load; every driving point is
    an op-amp output or a coupling-cap node that tolerates it.
  - Gnd (pin 3) to GNDA. 1 µF + 100 nF on each rail at the pins.
  - Each output leg: VO → 10 µF non-polar electrolytic → output node; the Sense pin connects to
    the output node, after the capacitor. The loop then removes the cap's effect and blocks the
    up to ±250 mV common-mode output offset, so there is no DC on the relay contacts or the
    connector.
  - The mute relay (where fitted) sits after the Sense connection. When it opens, the driver's
    loop stays closed and nothing swings to the rail.
  - Single-ended use: a TS plug in a TRS output, or pin 3 grounded on an XLR, grounds that leg.
    The datasheet asks for VO and Sense of the unused side both grounded. With Sense at the
    output node, a ground at the plug grounds both through the jack contact and a few cm of
    track.
- Output connectors: XLR male, Neutrik NC3MAH (horizontal PCB) or panel-mount with flying
  leads, pin 2 hot. Shell to chassis.

## 8. Power-on / power-off mute

- Contacts: Omron G6K-2F-Y (DPDT signal relay; Ag contacts with Au-alloy, bifurcated crossbar,
  2 A carry, 3 ms release), normally open, in series
  with both legs of each balanced output. L and R need four poles (two relays), mono needs two
  (one relay), so three relays here; the control-room outputs add two more (section 20). Coil: 12 V version (datasheet: 9.1 mA, 1315 Ω,
  ~100 mW; must operate at 80 % of rated, maximum 150 %). Each coil gets 560 Ω in series from
  +V (+17 V): the coil sees 11.9 V. A 24 V coil would get only 71 % on +17 V, below must-operate.
  NPN low-side switch, 1N4148 across each coil. Five coils draw about 46 mA.
- Control (simulated in `sim/mute.cir`; values as generated in `tools/gen_master.py`), LM393s on ±VL:
  - Reference: BZX84C6V2 fed from +V through 4K7 (VREF6 = 6.2 V).
  - Comparator A: +V through 56K / 47K against VREF6, trips below +13.6 V.
    Comparator B: divider 22K (to VREF6) / 51K (to −V) against GNDD, trips when −V rises above −14.4 V.
    Open-collector outputs wired-AND on RAIL_OK, 10K pull-up to +VL.
  - Timer: 2.2M from RAIL_OK into a 2.2 µF film capacitor (WIMA MKS2; an electrolytic's leakage
    would be comparable to the charging current near the threshold). A 1N4148 clamps it at
    −0.7 V, and a 1N4148 + 2.2K discharges it into RAIL_OK on a fault (about 5 ms), so every
    restart starts from about 0 V.
  - Schmitt: third comparator, timer against VREF6, 22M hysteresis, 4K7 pull-up; then 4K7 to the
    MMBT3904 base. Fast release: 1N4148 + 2.2K from the base to RAIL_OK, with a 1N4148 clamp
    holding the base above −0.7 V.
  - The relay transistor sinks all five coils (5 × 9.1 mA).
- Simulated (LM393 as an open-collector model that only works above 2 V of supply; coil
  inductance assumed 1 H):

  | Case | Result |
  |------|--------|
  | Power-up, rails in 50 ms | relays close at 2.80 s; worst coil current before that 7 µA (no glitch) |
  | Both rails collapse (17 → 0 V in 200 ms) | coils released 2 ms after −V passes −14.4 V; rails still ±14.2 V |
  | +V lost only | released at +13.4 V (−V still −17 V) |
  | −V lost only | released at −14.2 V (+V still 17 V) |
  | 20 ms dip to ±12 V | released in 1.4 ms; full re-arm, closes again 2.76 s after the dip |
  | Slow PSU ramp (2 s) | closes 2.82 s after +V reaches 14 V |

  Add the G6K's own release time (3 ms max) to the release figures.
- First draft (220K / 22 µF timer, 1M hysteresis, no series resistors on the reset diodes)
  failed in simulation: the 1M from the Schmitt output held the timer near 10.4 V, so the delay
  was over 3.6 s and very tolerance-sensitive; a brownout would also have left the timer at
  −16 V, giving a 5 s delay after short faults.

## 9. Simulation (`sim/master_mix.cir`, single-pole OPA1612 model, 40 MHz GBW)

24 channels routed, 4K7 bus, 0 dBu on one channel, hard-panned:

| Point | Result |
|------|--------|
| SUM_L (U1A out) | 0.0 dB, inverted (179.8°) |
| MIX_L (U1B out) | 0.0 dB, in phase (−0.2°) |
| POST_L, fader at top | +9.9 dBu |
| POST_L, fader at "0" mark | −0.3 dBu |
| Balanced output, fader at "0" mark | +5.7 dBu differential (driver modelled as an ideal +6 dB stage) |
| 1 V strip-to-master ground difference at MIX_L, ground cancel on, GCANCEL buffered, 13 re-inverters loading it | −71 dB at 10 Hz, −31 dB at 1 kHz |
| Same, the 13 re-inverters on the raw line (no buffer) | −31 dB at 10 Hz |
| Same, ground cancel defeated | +27.6 dB (bus noise gain 25 × the difference) |
| Bus capacitance 1 nF: SUM_L response | no peaking, −3 dB at 298 kHz |
| Bus capacitance 10 nF: SUM_L response | +0.09 dB peak at 141 kHz, −3 dB at 392 kHz |

The remaining ground-difference leakage at 1 kHz comes from the bus capacitance to master
ground (modelled as 1 nF). In the real ribbon much of that capacitance is to the strip-ground
conductors, which helps. The resistor match in U1B was ideal in the sim; with 0.1 % parts
expect a common-mode rejection of roughly 55–60 dB on top.

Noise, 20 Hz–20 kHz unweighted, OPA1612 (en 1.1 nV/√Hz, in 1.7 pA/√Hz):

| Channels routed | U1A alone | U1A + U1B (2K2) |
|----------------|-----------|-----------------|
| 1 | −111.3 dBu | −108.7 dBu (−106.5 with 4K7) |
| 24 | −100.4 dBu | −100.1 dBu (−99.7 with 4K7) |

At POST_L with the master fader at the "0" mark and 24 channels routed: −99.1 dBu
(mix-bus noise plus post-amp self-noise of −106 dBu). Channel noise from 24 open strips is on
top of this, as in the architecture's section 2.4.

## 10. Op-amps and parts (stereo mix part)

| Ref (proposed) | Part | Function |
|-----|------|----------|
| U1, U11 | OPA1612 | A: sum L/R, B: ground-cancel re-inverter L/R |
| U2, U12 | OPA1612 | A: insert return buffer, B: fader post-amp |
| U3 | OPA1612 or NE5532 | mono sum and re-inverter |
| U4, U14, U5 | DRV134 | L, R, mono line drivers |
| U6 | LM393 (+ second LM393 or latch) | mute relay control |
| U9A | OPA1612 (half) | GCANCEL buffer for all re-inverters |
| K1–K3 | Omron G6K-2F-Y | output mute |
| J (×3) | Neutrik NRJ6HF | master insert L/R (2) — the third is spare / mono insert if wanted |
| RV | Bourns PTB0144-2010BPA103 | master fader |

---

# Part 2 — Subgroups and aux masters

Delta references: ED2778A (group output: group sum amp, group insert, group fader, post amp,
"GND-CANCEL OUTPUT AMP", SUB switch into the monitor pan and on to MIX L/R, PFL) and ED2779A
(aux masters: GROUNDCANCEL on the summing amp's reference input, master level, buffer,
ground-cancelling output amp, TRS output, AFL switch to PFL+/PFLDET with LED).

## 12. Subgroups ×4

Bus pins: SUB1 = 15, SUB2 = 13, SUB3 = 11, SUB4 = 9. Each sub is a full copy of the stereo
mix path's first half, plus a pan into the mix.

```
SUBn bus ─ ferrite ─ summing amp (OPA1612 A), Rf 4K7 ∥ 100 pF, + input = GCANCEL
         ─ re-inverter (OPA1612 B), 4 × 2K2 0.1 %, + leg from GCANCEL_BUF   → SUBn_MIX
SUBn_MIX ─ 75R ─ insert send (tip) ─ return (ring, normalled) ─ 47µ NP + 47K
         ─ return buffer (OPA1612 A) ─ 220µ NP + 47K ─ PRE_SUBn
PRE_SUBn ─ fader PTB0143 A10K (pin 1 = GNDA) ─ 2.2µ + 100K ─ post-amp +9.9 dB (OPA1612 B,
           4K7 / 2K2, 100 pF) ─ 220µ NP + 47K ─ POST_SUBn
POST_SUBn ─┬─ DRV134 ─ NRJ6HF TRS output (tip hot, ring cold, sleeve GNDA)
           ├─ pan pot RD902F B10K centre detent ─ pan buffers (OPA1612 A/B)
           │    ─ 220µ NP + 47K each ─ MIX switch (PVA2, A-B = on)
           │    ─ 4K7 1 % to MIX L / MIX R (switch off grounds the resistor's bus end)
           └─ AFL switch (PVA2): pole A 22K to PFL bus (off: resistor end grounded),
                                  pole B +VL → 100K → PFLDET, 4K7 → AFL LED (red)
```

- Gain: unity from bus to POST_SUBn with the sub fader at its "0" mark, the same as the
  strips and the mix.
- Into the mix: the pan, pan buffers, AC coupling and routing switch copy the strip
  (channel_strip_schematic_spec sections 9 and 10), so a sub is just one more 4K7 feed on the
  MIX bus. Stereo-pair use (1-2, 3-4): pan the odd sub hard left and the even sub hard right.
  The two sub faders are not linked.
- Each assigned sub adds 1 to the MIX bus noise gain, like a routed channel.
- AFL on subs is not in the architecture's list but the Delta group output has it (PFL
  switch) and it costs one switch, one resistor and one LED. Included.
- **Ground note.** The sub's feed into the MIX bus is referenced to master ground, while the
  MIX summing amp references GCANCEL (the strip grounds). Any master-to-strip ground
  difference therefore enters the mix once per assigned sub, at unity rather than at the bus
  noise gain. Measure on the test jig. If it matters, take the pan-buffer ground reference
  from GCANCEL_BUF instead of GNDA.
- No mute relay on the sub outputs (they feed recorders and processors, not speakers). Add
  a fourth G6K-2F later if wanted.

Per sub: 3 × OPA1612 (sum/re-invert, return buffer/post-amp, pan buffers L/R), 1 × DRV134,
2 × NRJ6HF (insert, output), PTB0143 fader, RD902F pan, 2 × PVA2 (MIX, AFL), 1 LED.

## 13. Aux masters ×6

Bus pins: AUX1 = 24, AUX2 = 25, AUX3 = 23, AUX4 = 22, AUX5 = 21, AUX6 = 20. The strips feed
these buses through 22K.

```
AUXn bus ─ ferrite ─ summing amp (OPA1656 A), Rf 22K 1 % ∥ 100 pF, + input = GCANCEL
         ─ re-inverter (OPA1656 B), 4 × 2K2 0.1 %, + leg from GCANCEL_BUF   → AUXn_SUM
AUXn_SUM ─ 47µ NP ─ master level RD901F A10K (pin 1 = GNDA, pin 3 = signal)
         ─ wiper ─ 2.2µ + 100K ─ output buffer (OPA1612, non-inverting:
           Rf 4K7, Rg not fitted = unity; fit 4K7 for +6 dB, 2K2 for +10 dB)  → AUXn_OUT
AUXn_OUT ─┬─ DRV134 ─ NRJ6HF TRS output (tip hot, ring cold, sleeve GNDA)
          └─ AFL switch (PVA2): pole A 22K to PFL bus (off: resistor end grounded),
                                 pole B +VL → 100K → PFLDET, 4K7 → AFL LED (red)
```

- Gain: a strip with its aux pot fully up and the aux master fully up gives unity at
  AUXn_OUT, then +6 dB differential from the DRV134. The Rg position lets you raise it
  for effects units that want a hotter send.
- 100 pF across 22K (corner 72 kHz). Checked in `sim/aux_master.cir` with a single-pole
  op-amp at 10 MHz and 50 MHz GBW (the OPA1656 figure still to be confirmed) and 1 nF or
  10 nF of bus capacitance:

  | Cf | Worst case (10 MHz, 10 nF) | 20 kHz response |
  |----|----------------------------|-----------------|
  | 47 pF | +3.0 dB peak at 72 kHz | — |
  | 68 pF | +1.2 dB peak at 61 kHz | −0.2 to +0.2 dB |
  | **100 pF** | no peaking; −3 dB at 65–86 kHz across all four cases | −0.4 dB worst |

  The −0.4 dB at 20 kHz on an effects send is acceptable; 100 pF is the value.
- **Op-amp: OPA1656** (CMOS). Datasheet: ±2.25 to ±18 V (40 V absolute), so ±17 V is inside the
  recommended range; GBW 53 MHz; 3.9 mA per channel; input voltage noise 11.8 / 4.3 / 2.9
  nV/√Hz at 100 Hz / 1 kHz / 10 kHz (CMOS 1/f), about 3.3 nV/√Hz averaged over 20 Hz–20 kHz;
  current noise 6 fA/√Hz. At 22K the OPA1612's 1.7 pA/√Hz current noise costs it 3.8 dB with
  one channel on the aux. Aux sends usually carry a few channels, so the CMOS part is the
  better fit.
- Aux 5/6 as a stereo pair needs nothing special: two masters, two outputs.
- AFL is taken after the master level (post-master), as the architecture specifies.

Per aux: 1 × OPA1656 (sum, re-invert), ½ × OPA1612 (output buffer; two auxes share one),
1 × DRV134, 1 × NRJ6HF, RD901F level, 1 × PVA2 (AFL), 1 LED.

## 14. Noise, subs and auxes (20 Hz–20 kHz unweighted, summing amp + re-inverter)

OPA1656 figures include its 1/f noise (fitted to the datasheet's 4.3 nV at 1 kHz and 2.9 nV
at 10 kHz).

| Channels on the bus | SUB, 4K7, OPA1612 | AUX, 22K, OPA1612 | AUX, 22K, OPA1656 | AUX, 22K, NE5534 |
|---|---|---|---|---|
| 1 | −108.7 dBu | −101.1 dBu | **−104.9 dBu** | −104.6 dBu |
| 4 | −106.6 | −99.4 | **−101.2** | −101.0 |
| 12 | −103.1 | −96.6 | **−96.4** | −96.3 |
| 24 | −100.1 | −94.2 | −92.7 | −92.5 |

The aux buses are 6 dB noisier than MIX/SUB at full load because of the 22K resistors,
which stay at 22K so the strip aux pot wipers aren't loaded (architecture section 2.4).

## 15. Parts summary, Parts 1 and 2

| Part | Qty | Where |
|------|-----|-------|
| OPA1612 | 2 (mix L/R sum + re-invert) + 2 (mix insert/post-amp) + 1 (mono) + 1 (GCANCEL buffer, other half spare) + 12 (subs) + 3 (aux output buffers) = **21** | |
| OPA1656 | **6** | aux sum + re-invert |
| DRV134 | 3 (L, R, mono) + 4 (subs) + 6 (aux) = **13** | |
| 10 µF NP electrolytic | 2 per DRV134 = **26** | output DC blocking inside the Sense loop |
| LM393 | 1–2 | mute relay control |
| Omron G6K-2F-Y | 3 | main output mute |
| Bourns PTB0144 (dual) | 1 | master fader |
| Bourns PTB0143 | 4 | sub faders |
| Alpha RD902F B10K detent | 4 | sub pans |
| Alpha RD901F A10K | 6 | aux master levels |
| C&K PVA2 EE | 4 (sub MIX) + 4 (sub AFL) + 6 (aux AFL) = **14** | |
| Neutrik NRJ6HF | 2 (mix inserts) + 4 (sub inserts) + 4 (sub outs) + 6 (aux outs) = **16** | |
| XLR male | 3 | MIX L, MIX R, MONO |
| LED red | 10 | sub and aux AFL |
| 2K2 0.1 % | 4 × 13 = 52 (or 13 quad networks) | re-inverters |

---

# Part 3 — Stereo returns

## 16. Stereo returns ×4

Purpose: effects returns (reverbs, delays) into the mix and subs. Built on the master PCB, with
the same receiver, routing and PFL circuits as the strip.

```
RET n L in (NRJ6HF) ─ differential receiver (OPA1612 A, 4 × 10K 0.1 %, 33 pF, 100 pF + 1M on inputs) → RETn_L
RET n R in (NRJ6HF, tip and ring normals wired to the L jack's tip and ring:
           with no plug in R, the R receiver sees the L signal)        ─ receiver (OPA1612 B) → RETn_R
RETn_L/R ─ 47µ NP + 47K ─ PREn_L/R ─┬─ level, dual A10K (RD902F), pin 1 = GNDA
                                    │    ─ wipers ─ 2.2µ + 100K ─ buffers (OPA1612 A/B;
                                    │      Rf 4K7, Rg not fitted = unity, fit 2K2 for +10 dB)
                                    │    ─ 220µ NP + 47K ─ RTNn_L/R
                                    │       ─ routing: MIX, 1-2, 3-4 (3 × PVA2, A-B = on)
                                    │         L via 4K7 1 % to MIX L / SUB1 / SUB3,
                                    │         R via 4K7 1 % to MIX R / SUB2 / SUB4,
                                    │         off grounds the resistor's bus end (as the strip)
                                    └─ PFL (pre-level): L and R each through 43K to a junction,
                                       PVA2 pole A puts the junction on the PFL bus (off: grounded);
                                       pole B: +VL → 100K → PFLDET, 4K7 → PFL LED (red)
```

- Gain: unity from input to RTNn with the level fully up and Rg not fitted. 43K + 43K into
  the 22K PFL bus gives (L + R) × 0.51, so a centred mono source arrives on PFL at +0.2 dB.
- Each RTN output drives three 4K7 summing resistors (1.57K), the same load as a strip's pan
  buffer.
- Ground note as for the subs: the return feeds are referenced to master ground, so any
  master-to-strip ground difference enters once per assigned return, at unity.
- No balance or mute. Add a balance pot later if wanted (dual B10K after the level pot, as
  the strip pan).

Per return: 2 × OPA1612, 2 × NRJ6HF, 1 × RD902F A10K, 4 × PVA2 (PFL, MIX, 1-2, 3-4), 1 LED.
Totals for four: 8 × OPA1612, 8 jacks, 4 dual pots, 16 switches, 4 LEDs.

---

# Part 4 — Monitoring

Delta reference: ED2780 sheet 1 (monitor select receivers, PFL SWITCHER with series J112s,
PFL SUM AMP, PFL DETECTOR, C/ROOM dual pot, ground-cancel CRM output amps, headphone feed,
remote meter connector) and sheet 3 (meters).

## 17. Signal flow

```
EXT in L/R (2 × NRJ6HF, R normalled to L) ─ receivers (OPA1612) ─ 47µ NP + 47K → EXT_L/R
POST_L/R (mix, after the master fader) ──────────────────────────────────────────→ MIX_MON_L/R
EXT switch (PVA2: latched = EXT) selects MIX_MON or EXT                           → MON_L/R

PFL bus (pin 27) ─ PFL summing amp (OPA1656 A, Rf 22K ∥ 100 pF, + input = GCANCEL)
                 ─ re-inverter (OPA1656 B, 4 × 2K2 0.1 %, + leg from GCANCEL_BUF)
                 ─ 47µ NP ─ SOLO LEVEL (RD901F A10K) ─ 2.2µ + 100K ─ follower         → PFL_SIG

PFL switcher (series J112s, Delta ED2780 sh.1):
   MON_L   ─ 47µ + 47K ─ J112 ─┐
   PFL_SIG ─ 47µ + 47K ─ J112 ─┴─ CRS_L ─ follower (OPA1612) ─┬─ C/ROOM level ─ CR out
   MON_R   ─ 47µ + 47K ─ J112 ─┐                              ├─ PHONES level ─ phones amp
   PFL_SIG ─ 47µ + 47K ─ J112 ─┴─ CRS_R ─ follower           └─ meters
```

PFL is mono and goes to both sides. The meters follow what is being monitored: mix, EXT or PFL.

## 18. PFL summing amp and solo level

- Same circuit as an aux master (section 13): OPA1656 sum, 22K ∥ 100 pF feedback, + input on
  GCANCEL, re-inverter on GCANCEL_BUF. Strip PFL, sub AFL, aux AFL and return PFL all feed it
  through 22K (or 43K + 43K for the stereo returns).
- Pin 28 ("PFL−" in our reading of the Delta) is not used by the master. The strips only pass
  it through, so it stays a spare.
- SOLO LEVEL: RD901F A10K, pin 1 = GNDA, then 2.2 µF + 100K and an OPA1612 follower.
  Fully up = unity: strip PRE at 0 dBu gives 0 dBu in the control room, the same as a channel
  at its "0" mark through the mix.

## 19. PFL detect, auto-switch, rude solo

- PFLDET (pin 29): every pressed PFL/AFL switch connects +VL through 100K. The master pulls
  the line to GNDD with 10K. One press gives 1.5 V, twenty-four give 11.8 V. LM393 (A)
  compares it with 0.74 V (220K / 10K from +VL) on the logic supply ±VL.
- Two complementary control lines: comparator A drives PFL_ON, comparator B (inputs swapped)
  drives MON_ON. Each LM393 output has a 10K pull-up to +VL, so it swings from −VL to +VL,
  then 100K / 100 nF (about 10 ms) for a click-free transition.
- Series JFET switch, as the Delta: J112 drain and source in the signal path, 47K from gate to
  source, gate to the control line through a 1N4148 (cathode to the control line).
  Control line at +VL: the diode is reverse-biased, gate follows source through 47K, J112 on
  (about 30–50 Ω). Control line at −VL: gate pulled to about −16 V, J112 off for any signal up
  to the ±10 V the op-amps can swing (J112 pinch-off 1–5 V).
- Signal sources at the switches are op-amp outputs, AC-coupled (47 µF + 47K, Delta C22/R40),
  so there is no DC across the JFETs when they switch.
- Rude solo: LM393 (second package, A) as a ~2 Hz astable, enabled by PFL_ON, flashing a 5 mm
  red "PFL ACTIVE" LED on the master panel. Its spare half can drive a steady "EXT" LED from
  the EXT switch's second pole.

## 20. Control room outputs

- C/ROOM level: dual A10K (RD902F), pin 1 = GNDA, fed from the CRS followers.
  Wipers ─ 2.2 µF + 100K ─ OPA1612 followers ─ DRV134 ×2 ─ mute relay ─ NRJ6HF TRS outputs
  (tip hot, ring cold, sleeve GNDA).
- **Mute relay on the CR outputs too.** They drive the monitor speakers, which matters more
  than the main outputs. Two more G6K-2F-Y (L and R, both legs), driven by the same control
  as section 8. That makes five relays in total.
- Gain: unity at full C/ROOM, then +6 dB differential from the DRV134.

## 21. Headphones

- PHONES level: dual A10K (RD902F), fed from the CRS followers (independent of C/ROOM).
- Amplifier per side: OPA1612 driving an LME49600 buffer inside its feedback loop (TI's
  composite arrangement). LME49600 datasheet: ±2.25 to ±18 V operating (±20 V absolute),
  ±250 mA output, internal current limit and thermal shutdown, 7.3 mA quiescent with the BW
  pin open (110 MHz mode; use that). TO-263, so give it copper for heat. Non-inverting gain 1 + 4K7/2K2 = +9.9 dB. Feedback taken from the
  jack side of a 2.2 Ω output resistor; 100 pF across 4K7.
  0 dBu at CRS gives 2.4 V rms at full PHONES, 180 mW into 32 Ω, well inside the LME49600's
  250 mA.
- Supply: separate branch from ±V through 2.2 Ω + 1000 µF per rail (the Delta has its own
  phones supply). Phones ground (PHONESGND) is a separate wire to the star point, as the Delta.
- Jack: NRJ6HF, tip L, ring R, sleeve PHONESGND.

## 22. Meters (main L/R; follow the monitored signal)

Thresholds and LED drive are copied from the Delta (ED2780 sh.3). The detector is new: the
simulation (`sim/meter.cir`) showed the Delta-style peak detector reads the bottom of the
scale badly (below).

- Source: CRS_L/R (so the meters show mix, EXT or PFL, whichever is monitored), through
  100R (Delta R41/R141) to a remote-meter header (for a meter bridge later) and to the
  rectifier.
- Detector per side, four op-amps (2 × TL072; JFET inputs, as the Delta's TL071/072):
  - U1, U2: precision full-wave rectifier (inverting half-wave with two 1N4148, then a summer:
    v and 2 × half-wave). Gain trim in U2's feedback: 10K + 10K trimmer (gain 0.5–1.0).
  - Average (Delta R303/C302): |v| → 33K → 2.2 µF, about 73 ms.
  - Peak: U3 precision peak detector. 1N4148 inside the loop, 1K into 1 µF (≈1 ms attack),
    release 330K + 220K (0.55 s, Delta-like). U3's feedback comes from the U4 follower through
    10K, with a 1N4148 clamp from U3's output to its inverting input. The feedback must not
    come from the capacitor itself: then the clamp current discharges it (simulated: 50 Hz
    read 0.95 dB low and the hold collapsed).
  - PEAK/AVG solder jumper per side (Delta J2), then U4 follower. The 20 LM2901 inputs (about
    0.5 µA typical, 5 µA max in total) load U4, not the detector capacitor. Directly on the
    Delta's 55K they would be a 27 mV error against a 67 mV bottom threshold.
  - Calibrate after setting the jumper: 0 dBu sine → 0.649 V at U4. Peak mode needs a gain of
    0.594 (11.9K), average mode 0.931 (18.6K); the trim covers both.
- Simulated (single-pole op-amps at 3 MHz GBW, 1N4148 model):

  | Test | Peak mode | Average mode |
  |------|-----------|--------------|
  | −20 / −10 / +10 / +18 dBu at 1 kHz, relative to the 0 dBu reading | −20.08 / −10.03 / +10.01 / +18.02 dB | exact to 0.01 dB |
  | 50 Hz / 10 kHz / 20 kHz, relative to 1 kHz | −0.04 / −0.15 / −0.28 dB | +0.01 / −0.11 / −0.13 dB |
  | 5 ms / 10 ms / 100 ms tone burst | full reading (+0.1 dB overshoot) | −23.5 / −17.8 / −2.5 dB |
  | Release after a 0.5 s burst | −15.8 dB at 1 s, −32 dB at 2 s | τ 73 ms |
  | 10 % pulse wave, same p-p as a 0 dBu sine | reads the larger (+1.97 V) excursion | — |
  | v1 (Delta diode-compensated peak, 75R / 10 µF) at −20 dBu | read −11.7 dB | — |

  The peak mode is a fast "sample peak" (about 1 ms attack), faster than an IEC type II PPM
  (where a 10 ms burst reads −4 dB). A full-wave rectifier matters for synth pulse waves,
  which a half-wave detector can under-read by the waveform's asymmetry.
- Thresholds: resistor ladder from +V through 16K, then 1K5, 1K1, 910, 680, 620, 470, 330, 300,
  220, 180, 150, 110, 91, 68, 62, 47, 33, 27, 20, and 91R to meter ground (Delta R309–R329).
  That gives 2 dB steps from −20 to +18 dB about the 0.649 V tap (calculated from the values).
- 20 LEDs per side: −20 … 0 green (11), +2 … +10 amber (5), +12 … +18 red (4). With 0 dBu
  nominal and clip at about +22 dBu, red means less than 10 dB of headroom left.
- Comparators: 5 × LM2901 per side. LEDs in two series strings of 10 per side, each fed by a
  constant-current source (PNP, 75R emitter, two-diode reference, Delta TR15/TR16). Each
  comparator shorts out its LED, so supply current is constant whatever the reading, and
  the meters don't modulate the rails.
- Supply: meter branch from ±V through 10R + 47 µF per rail (Delta R307/R308, C305/C306),
  meter ground run separately to the star point.

## 23. Monitoring parts summary

| Part | Qty | Where |
|------|-----|-------|
| OPA1612 | 1 (EXT receivers) + 1 (solo follower, spare half) + 1 (CRS followers) + 1 (CR buffers) + 1 (phones) = **5** | |
| TL072 | 4 | meter detectors (2 per side) |
| OPA1656 | 1 | PFL sum + re-invert |
| LME49600 | 2 | phones |
| DRV134 | 2 | CR outs (+ 4 × 10 µF NP) |
| LM393 | 2 | PFL detect, rude-solo flasher |
| LM2901 | 10 | meters |
| J112 | 4 | PFL switcher |
| G6K-2F-Y | 2 | CR mute |
| RD902F A10K | 2 | C/ROOM, PHONES |
| RD901F A10K | 1 | SOLO LEVEL |
| PVA2 | 1 | EXT select |
| NRJ6HF | 2 (EXT in) + 2 (CR out) + 1 (phones) = **5** | |
| LEDs | 40 meter + 1 PFL ACTIVE + 1 EXT | |

---

# Part 5 — Master power entry

## 24. Rails and connector

- Rails: ±17 V from the external linear PSU (architecture 3.3). The master sits in the centre
  of the console and feeds both ribbon wings, so all power enters at the master.
- Connector: 5-pin XLR male on the master (Neutrik NC5MAH, horizontal PCB): +V, −V, 0 V on two
  pins, chassis/mains earth. Neutrik: 3 A per contact, rated voltage < 50 V, hard-gold contacts.
  Peak rail current was about 1.4 A with the v3.1 strips. With strip v4.0 it is about 2.65 A typical and
  3.2–3.8 A worst case on +V, which is over the 3 A contact rating: see §27 (7-pin XLR proposed).
- Reverse-polarity protection: a Schottky (SB540, 5 A) from each rail to 0 V, reverse-biased in
  normal use. A wrongly wired lead then puts the PSU into current limit instead of reversing
  every op-amp.

## 25. Distribution

- Two 34-pin headers on the master, one per wing (12 strips each), carrying the buses and
  power on pins 30–33.
- Each wing gets its own PTC fuse per rail (Bourns MF-R075, 0.75 A hold), to protect the 28 AWG
  ribbon conductors from a shorted strip. **Too small for strip v4.0**: a wing draws about 1.0 A
  typical on +V, and up to 1.5 A in the worst case (§27). Proposed: MF-R160 (1.6 A hold, 3.2 A trip),
  not yet in the schematic.
- Master local branches, each with its own series element and reservoir:

  | Branch | Feeds | Series | Reservoir |
  |--------|-------|--------|-----------|
  | ±VA audio | op-amps, DRV134 | 1 Ω per rail | 470 µF + 100 nF per IC |
  | ±VP phones | OPA1612 + LME49600 | 2.2 Ω | 1000 µF |
  | ±VM meters | LM2901s, LED strings | 10 Ω | 47 µF (Delta values) |
  | ±VL logic | LM393s, relay control, LEDs | 10 Ω | 47 µF |
  | relay coils | G6K-2F-Y ×5 via NPN switches | from +V directly | — |

  The audio branch uses 1 Ω instead of the strips' 10 Ω because it carries about 0.5 A.

## 26. Grounding (the star point)

- The star point is a copper ground bar on the master. On it, each with its own wire or link:
  PSU 0 V; the 24 strip spade wires (strip CN4); master AGND; master GNDD (one link); meter
  ground; PHONESGND; chassis, via the PSU lead's earth pin.
- GCANCEL (pin 26) does **not** go to the bar (decision, section 3).
- The ribbon's GND conductors (even pins 2–16) carry only the strips' local audio ground for
  the group-bus shielding; heavy return current goes through the spades.

## 27. Current budget (typical supply currents from the datasheets)

| Item | +V | −V |
|------|----|----|
| 34 × OPA1612 (3.6 mA/ch typ, 4.5 max) | 245 mA | 245 mA |
| 7 × OPA1656 (3.9 mA/ch) | 55 | 55 |
| 4 × TL072 (meters) | 11 | 11 |
| 15 × DRV134 (5.2 mA) | 78 | 78 |
| 10 × LM2901, 4 × LM393 | 14 | 14 |
| 2 × LME49600 (7.3 mA) + phones load | 65 | 65 |
| Meter LED strings, 4 × ~8 mA | 32 | 32 |
| 5 relay coils (9.1 mA each) | 46 | — |
| Panel LEDs (AFL, PFL, power, rude solo) | 60 | — |
| **Master** | **≈ 0.61 A** | **≈ 0.50 A** |
| 24 strips v4.0 at ≈ 85 / 72 mA | ≈ 2.04 A | ≈ 1.73 A |
| **Console** | **≈ 2.65 A** | **≈ 2.23 A** |

Strip v4.0 (2026-10-22): 10 × OPA1612 (with the KHN mid bands), DG413 logic supply 2.4 mA, LEDs on
+VL (ON, EQ and routing lit: about 9 mA). The strips were 33 / 23 mA in v3.1, when this budget was
first written. With the OPA1612 at its 4.5 mA maximum the console reaches about 3.2 A on +V. With
every LED on every strip lit as well, it reaches 3.8 A.

**Consequences (proposed, not yet in the schematic or `gen_master.py`):**

| Item | Now | Needed | Proposal |
|------|-----|--------|----------|
| Wing PTC per rail | MF-R075, 0.75 A hold | ≥ 1.5 A hold | Bourns MF-R160 (1.6 A hold, 3.2 A trip); new footprint in `tools/footprints.py` |
| Power inlet | 5-pin XLR, one 3 A contact per rail | ≥ 3.8 A per rail | 7-pin XLR (Neutrik NC7MAH): two contacts per rail, two for 0 V, one earth (6 A per rail) |
| PSU regulators | ≥ 3 A | ≥ 4 A per rail | LM338-class (5 A) or a pass transistor; heatsink for about 20 W per rail at 24 V in |
| PSU transformer | 2.5 A DC per rail | 3.5–4 A DC per rail | size for 4 A DC per rail |
| Strip R1/R2 (10 Ω, 0805) | 0.8 V drop, 55–80 mW | — | fine at 0805 (125 mW); 1206 for margin, or 4R7 for less drop |

Reducing the strip current instead: OPA1678 (about 2 mA/ch) in the six KHN positions would save about
10 mA per strip (0.25 A per rail). The EQ is resistor-noise dominated, but simulate the noise before
choosing.

## 28. Power-on sequencing

- Power-on mute (section 8) covers the main and CR outputs: five relays, closed about 2 s after
  both rails are above 14 V, opened at once if either drops.
- Power LED on +VL.

## 29. Still open

- Balanced outputs: THAT1646 went end-of-life (THAT memo, 1 September 2026); replaced by
  TI DRV134 on all 15 outputs (decided October 2026, section 7).
- The same THAT memo also ends the THAT 2180/2181 VCAs (planned for the external SSL bus compressor,
  architecture 4.2) and the THAT 124x receivers (listed as an option in architecture
  section 5). The bus compressor needs another VCA.
- Datasheet checks done October 2026: OPA1656, OPA1612, LME49600, DRV134, G6K-2F-Y, Neutrik
  NC5MAH (figures in sections 7, 8, 13, 21, 24, 27). TI lists OPA1612, OPA1656, LME49600,
  DRV134 and DRV135 as ACTIVE.
- Meter detector simulated and redesigned (section 22).
- Schematic: `master.kicad_sch`, generated by `tools/gen_master.py` from this spec (October 2026):
  1059 parts, netlist 2985 pins / 0 mismatches, every pin on a pad, ERC 0 violations.
  Mute control values are simulated (section 8, `sim/mute.cir`).
- The EXT LED in section 19 is not possible as written (both EXT switch poles carry audio); left out.
- PVA2 switching sense (affects every switch here too; see strip spec 13.1).
- Schematic generator for the master (like `tools/gen.py`).

*Document version 0.6 — October 2026 (mute control simulated and fixed; master schematic generated)*
