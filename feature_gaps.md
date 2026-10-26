# Feature gaps against a Mackie 32•8: study (2026-10-26)

Comparing the console with a Mackie 32•8 left two gaps worth closing for live hardware-synth mixing:
- you can't see each channel's level at a glance;
- there are only four stereo effects returns.

The 32•8's other extras are left out:
- **Mic preamps and phantom power:** the console is line-only by decision (2026-10-22).
- **In-line "Mix B" tape monitoring:** no multitrack in this setup.
- **Solo-in-place:** PFL-only, by decision.
- **MIDI mute automation:** the ON key is a mechanical PVA2.

## 1. Channel level at a glance

**Today.** Each strip has one red OL LED at (20.6, 50). It lights from +18.2 dBu with a ~150 ms hold (K3). The master
has L/R bars. A channel's level is only visible by pressing PFL.

**Where a second LED could go.** Nowhere, cleanly:
- around the OL LED, a second hole collides with the GAIN scale's "+10" or the OL legend;
- the free panel area higher up the right column (y 20–44) is over the jack board, 24 mm deeper, not the main board
  (which starts at y 44);
- the strip has no spare comparator: U4A is the OL detector and U4B, since K3, is its hold stage.

**The clean option: a red/green bicolour LED in the existing OL hole.**
- **Lights:** green from about −20 dBu (signal present), red at +18 dBu (overload). No panel or print change.
- **Detector:** a second LM393 (U17) copies K3's topology one level lower:
  - U17A sees PRESRC through a clamp, so it never goes below GNDD, against about +0.11 V (−20 dBu peak) and discharges
    a hold cap;
  - U17B lights green while the hold lasts (~150 ms).
  - About 8 parts per strip; a placement trial needed around U4.
- **The LED:** Kingbright WP3VEGW, 3 mm, red / green, diffused. It is **common-cathode**, and the LM393's outputs can only
  sink. So each colour's anode is fed from +VL through its own resistor, and the comparator shorts it to ground to turn
  that colour off. Both resistors then draw current all the time.

| Driving the bicolour | Parts per strip | Console current on +V | Notes |
|---|---|---|---|
| **a. Common-cathode (WP3VEGW), comparators shunt the anodes** | LED, 2 R, U17 + ~8 | **+~120 mA**, constant | The simplest. The accepted worst corner goes from 4.33 to ~4.45 A, on a 4 A PSU. |
| b. Common-cathode, a PNP high-side switch per colour | + 2 transistors, 2 R | +~50 mA (only while lit) | Clean current; more parts on a crowded board. |
| c. Common-anode part (another maker), comparators sink the cathodes as today | LED, 2 R, U17 + ~8 | +~50 mA while lit | Needs a stocked 3 mm common-anode red / green part (to find). |

**In overload both colours light**, which reads amber. Showing red alone needs the green gated off during the OL hold:
one diode-OR into U17B, under 1 part. Recommended.

**Power, either way.** The PSU's accepted worst corner is already over its rating (4.33 A on +V). Option a adds
~0.12 A all the time; b and c only while green is lit, about the typical case anyway. So b or c, not a.

**Recommendation:** option **c** if a stocked common-anode 3 mm red/green part exists, otherwise **b**.

## 2. More stereo effects returns

**Today.** One stereo return per group module, four in all, each with level, PFL and routing to MIX / 1-2 / 3-4. Six
aux sends feed the effects.

| Option | What it takes | Returns |
|---|---|---|
| **A. A second return on every group module** | Per group: 2 jacks on its jack board (5 → 7, one more row), a receiver, level and routing like the existing return (~40 parts, 2 op-amp packages + the OPA1656 followers), a knob and keys in the group panel's free area (y ~100–160). Schematic, placement, panel and 3D model regenerated. | 8 |
| B. A new 8 HP "return module" with two stereo returns | A new board design, mostly reusing `master_lib` circuits; one more 8 HP slot (+40.64 mm). The rails, tub and panels regenerate from the module order. | 6 |
| C. Use strips as returns | Nothing: a stereo return on two strips panned hard left / right (strips have full EQ and routing). | 4, plus as many as you give up |

**Recommendation:** A, if you want more returns in hardware. The group panels have the room, nothing else in the
console changes size, and the parts are already designed. C costs nothing and suits one or two extra effects.

## Sign-off

Signed off by Ruslan on 2026-10-26: both, MET1 per option c if a common-anode part exists, else b, with the green gated
off in overload; RET1 option A.

- [x] **MET1** Bicolour signal / OL LED on every strip, green / red with the green gated off in overload; drive per option
  **b** (no stocked 3 mm common-anode red / green part: Bivar's 3BC-3-CA-F is broker-only).
- [x] **RET1** A second stereo return on every group module (option A).

## Applied: MET1 (2026-10-26, strip spec v4.7)

- **Schematic** (`tools/gen.py`, page 08 OVERLOAD DETECTOR):
  - **LED:** D2 is a WP3VEGW on its own footprint, `goa-console:LED_D3.0mm-3_P2.00mm` (leads at 2.0 mm, centred on
    the middle lead).
  - **Red:** U4B drives the red through a PNP, Q3.
  - **Green:** U17 (LM393B) is the signal detector and hold, and drives the green through Q4.
  - **Gate:** Q5, a PNP, holds Q4's base at +VL while U4B lights the red. It replaces the diode-OR idea above: the
    green then draws nothing in overload, where shorting its anode would have wasted 3.6 mA.
  - **Threshold divider:** R119 / R120 are 750K / 10K, not 75K / 1K, which would have loaded VREF by 7 % and moved the
    red's threshold by 0.5 dB.
- **Sim** (`sim/review/gaps/ol.py`, rewritten for both colours):

  | | Lights from | Hold | Current |
  |---|---|---|---|
  | Red | +18.1 / +18.4 / +18.4 dBu at 50 Hz / 1 kHz / 10 kHz | 143–181 ms | 3.2 mA |
  | Green | −19.5 dBu | 159 ms | 3.2 mA |

  The green is off in overload, and neither colour lights in silence.
- **Checks:** 851 pins, 0 mismatches, check_fp 0, ERC 0; `sim_netlist.py` 39/39, `sim_console.py` 32/32.
- **Placement:** the detector and switches sit in the free column left of the fader (y 298–324). Only the input
  followers' row moved, 1 mm. Parity DRC: 0 violations, 0 parity issues, 290 / 290 symbols linked; report unchanged.
- **Panel:** same hole and legend.
  - **Fix found on the way:** the artwork depended on the boards' footprint order, which changes on every re-placement
    (where two scales' numerals collide, the first one placed stays). `panel_layout.layout()` now takes parts in
    reference order.
  - **Result:** group and master are pixel-identical. On the strip, one numeral changed: the HF ring's "9" now shows
    where the HPF ring's "50" did.
- **Power:** ≈ +4 mA per strip on +V while green is lit, ≈ +0.1 A console-wide typical. The worst corner goes from
  ≈ 4.33 to ≈ 4.38 A on +V (master spec §27).
- **BOM:** per strip +1 LM393B, 3 MMBT3906, 1 BAT54W, 1 WP3VEGW in place of the WP710A10ID, and 13 passives;
  `order_bom.csv` regenerated.
