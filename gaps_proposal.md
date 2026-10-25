# Simulation gaps closed, and two fixes (2026-10-25)

This pass simulated the strip circuits that no earlier simulation covered, then the strip as a population of real
parts. Scripts are in `sim/review/gaps/`. Two findings needed design changes, K1 and K3 below. **Both were signed off by
Ruslan on 2026-10-25 and applied the same day (strip spec v4.5).** Everything else passed.

The overload figures in Results are the circuit before K3; `ol.py` now simulates the circuit as built.

## Results

**Overload detector** (`ol.py`; values read from `channel_strip.net`).
- **Steady sine:** the LED lights from +18.4 dBu at 50 Hz, 1 kHz and 10 kHz. That is right: 4.6 dB under the +23 dBu
  swing limit.
- **Programme peaks:** it misses them. The 1 kΩ / 1 µF charge path needs about 20 cycles to reach the threshold:

  | Burst at 1 kHz | +19 dBu | +20 dBu | +22 dBu |
  |---|---|---|---|
  | 1–2 cycles | off | off | off |
  | 5 cycles | off | off | 22 ms |
  | 20 cycles | 1 ms | 70 ms | 189 ms |

  A clipping drum hit doesn't show, and a near-threshold flash of about 1 ms is invisible. → **K3**.

**Soft mute** (`mute.py`; J112 at VGS(off) −1 / −2.5 / −5 V, rds(on) 50 Ω max, Cgs = Cgd 5 or 14 pF).
- **Mute:** −3 dB 28–64 ms after the key, then −60 dB about 7 ms later. The floor is −79 dB at the datasheet's
  worst-case on-resistance, about −86 dB with typical parts.
- **Unmute:** −3 dB to full in 1–8 ms, nearly a hard switch-on. This is inherited from the Delta, whose gate swings to
  −VL for headroom (spec 9). Not changed.
- **Click with no programme:** −97 to −81 dBu peak (gate charge into the 4K7 nodes). Fine.

**Key clicks** (`keys.py`). The DC step each key puts on the buses, with the op-amps' real DC errors: OPA1612 offset
±500 µV and bias current 60–250 nA; OPA1656 offset ±1.5 mV. 12 draws per key, one strip on ideal summers.

| Key | Worst | Median | |
|---|---|---|---|
| **PFL** | **11.5 mV (−39.6 dBu) on PFL** | 7.7 mV | → **K1** |
| HPF IN | 2.6 mV (−52.5 dBu) on MIX | 0.9 mV | the HPF study's 0.9 mV is the typical case |
| Ø | 1.3 mV (−58.5 dBu) | 0.7 mV | |
| PRE 1-2 / 3-4 / 5-6 | 0.52 mV (−66.5 dBu) | 0.35 mV | |
| DIR, EQ IN, PAN, ON | ≤ 0.01 mV | | |

- **Reference:** the routing switches' click (−55 dBu peak, `sim/routing_switch.cir`) was accepted.
- **Why PFL:** U3B's bias current (OPA1612, up to 250 nA) flows through R17 / R16 / R13. That leaves PRE 3–14 mV off
  ground, and the PFL key puts it on the PFL bus through R32, so every press ticks in the monitors at C/Room level.
- **HPF IN:** at worst-case offsets it is 2.5 dB over that reference, typical is 6 dB under. Keep it, and measure it on
  the jig.

**Part tolerances** (`mc.py`). 200 strips. Resistors 1 % (0.1 % where specified); C0G 5 %, X7R and film 10 %,
bipolars 20 %. Pots ±20 % track, the gangs of a dual within ±10 %.

| | Nominal | Spread (min … max) |
|---|---|---|
| PRE at the gain detent | −0.11 dB | −0.57 … +0.48 dB |
| Gain CW / CCW | +14.8 / −15.0 dB | ±1.7 dB |
| HF / HI-MID / LO-MID / LF at full boost | 11.3 / 14.4 / 14.5 / 14.2 dB | ±0.5 / ±0.8 / ±0.9 / ±1.9 dB |
| HPF −3 dB at mid rotation | 86 Hz | 80 … 96 Hz |
| EQ flat, worst ripple 20 Hz–20 kHz | 0.30 dB | 0.13 … 0.62 dB |
| Pan centre, L − R | 0 | ±0.17 dB |
| POST, fader at "0" | −0.37 dB | −0.85 … +0.27 dB |

Strips match within about ±0.5 dB at unity. The EQ is within normal console tolerances.

**Headroom** (`headroom.py`). Every op-amp output, 20 Hz–20 kHz, swing limit ±15.5 V = +23.0 dBu.
- Every setting clips first at the stage where the gain is; no internal node (KHN integrator, EQ stage) clips early.
- Clip points at the input:
  - unity: +23.0 dBu;
  - fader at the top: +13.2 dBu, at the post-amp (the known +10 dB trade-off);
  - gain +15 dB: +8.2 dBu;
  - every EQ band +15 dB: +6.7 dBu (mids centred), −4.4 dBu (mids CW, the bands overlap).
- The overload LED watches PRESRC, so it can't warn of the post-amp clipping with the fader high. That is spec 8.1 as
  designed, Delta practice.

## Proposals

**K1. DC block in the PFL send.**
- **Change:** a 2.2 µF film cap (WIMA MKS2C042201K00KSSD, the strip's coupler) in series with R32, between PRE and the
  PFL key.
- **Effect:** in simulation the PFL step goes from 7.7 mV median / 11.5 mV worst to nothing measurable. The PFL send's
  low corner is 3.3 Hz (22K, 2.2 µF).
- **Cost:** one part per strip, THT on the bottom like the other film couplers.

**K3. Overload detector: fast attack and a fixed hold.**
- **Attack:** C12 1 µF → 100 nF, a 0.1 ms charge.
- **Hold:** U4B, the package's spare comparator, becomes a hold stage. U4A's output no longer drives the LED; it
  discharges a hold cap (HOLD: 1M to +VL, 220 nF to GNDD). U4B compares HOLD with VREF and lights the LED while HOLD is
  below it, about 150 ms after the last overload. VREF is shared.
- **Common-mode range:** HOLD rests at +VL, above the LM393's input range (V+ − 1.5 V), but U4B's other input (VREF)
  stays inside it, which the datasheet allows for a correct output.
- **Simulated** (`ol_fix.py`):
  - same steady threshold (+18.2 to +18.5 dBu);
  - lights for 155–190 ms on 2 cycles at +19 dBu, and on a single cycle at +20 dBu or more.
- **Cost:** two parts (1M, 220n), a value change on C12, and U4B rewired; no new IC. The master's and group's own
  overload / peak circuits are not affected.

- [x] **K1** PFL send DC block (2.2 µF film in series with R32).
- [x] **K3** Overload detector: C12 100 nF, U4B hold stage (1M / 220 nF).

## Applied (2026-10-25)

- **Parts:** C96 (2.2 µF MKS2 film, bottom side, at the PFL area), C12 100 nF, and R115 1M with C97 220 nF (Samsung
  CL21B224KBFNNNE) for the hold. U4B is now the hold comparator.
- **Drawings:** overload and PFL redrawn.
- **Checks:**
  - strip 806 pins / 0 mismatches, check_fp 273 / 0, ERC 0;
  - `sim_netlist.py` 37/37, `sim_console.py` 32/32;
  - `ol.py` on the regenerated netlist: lit 154–192 ms from 2 cycles at +19 dBu, threshold +18.2 to +18.5 dBu;
  - `keys.py`: PFL step 0.
- **Placement:** re-placed with parity DRC clean. Report: decouplers 3.1 / 10.0 / 11, high-Z inputs 10.5 / 22.1 / 29.
