# Panel print — the Soundcraft Delta's legend system and ours

Sources:
- the 200 Delta User Guide's module drawings, cropped in `ref/delta200_panels/`;
- photos of real 200 Delta, Delta DLX and Delta SR modules (list below), read on 2026-10-23 by three search agents and
  re-checked by three more.

The 3D model applies this in `tools/console_3d.py` (`panel_print`); see `render/panel_strip.png` and
`render/panel_master.png`. Panel finish and cap colours are still placeholders.

## The Delta's system (from the drawings and photos)

- **Ink:** one colour only, cream / pale ivory (warm off-white), on a matte dark slate blue-grey panel. There are no
  coloured bands or tinted section fills; colour comes only from the knob caps and fader caps.
- **Type:** a Helvetica/Univers-like grotesque.
  - Names are uppercase bold and slightly condensed.
  - Numerals are the regular weight of the same face, about 0.7× the name height.
  - Units are "dB" and "KHz" (capital K).
  - Two-word names are stacked and centred (AUX / 1, HI / MID, OSC / LEVEL, TB / GAIN).
- **Names:** at the upper right of each knob, just outside the numerals, at about 1–2 o'clock. Knobs sit left of
  centre, so the names form a right-hand column.
- **Rings:** 11 positions over 300° (7 to 5 o'clock, 30° apart).
  - Each position has a small square dot just outside the knob skirt, with its numeral further out on the same radius.
  - Proportions: dots at about 1.15–1.25× the skirt radius, numerals at about 1.45–1.6×; numerals about 1.6–1.8 mm high
    on 14–15 mm knobs.
- **Scales:**

  | Control | Numerals | Extra |
  |---|---|---|
  | EQ gain | 15 12 9 6 3 −0+ 3 6 9 12 15 | 0 has a line tick instead of a dot; "dB" at 6 o'clock between the two 15s |
  | AUX / VOL / levels | 0 1 2 … 10 | 5 at the top |
  | PAN (real panels) | L5 4 3 2 1 0 1 2 3 4 5R | The user-guide drawing shows L 4…0…4 R |
  | Frequency | Five numerals on the 11 dots | Unit on the last numeral |
  | GAIN (mono input) | Inner dot ring: MIC scale, 2…70. Outer ring of dashes: LINE scale, −10 0 5 12 15 17 +20 | "MIC" then "LINE" under the knob, with an L-shaped leader to the LINE key |

  Frequency labels: HI MID 0.6 1.2 2.5 5 10KHz; LO MID 0.15 0.3 0.6 1.2 2.4KHz.
- **Graphics:**
  - Thin full-width rules separate sections; a key can sit on a rule (EQ, RET).
  - A "]" bracket joins each frequency knob to its gain knob, with the band name (HI MID, LO MID) set into the bracket.
  - Leader lines join an aux pot to its key (AUX 3/4 → "5-6", aux masters → AFL).
  - "PEAK" is printed beside its LED; "100Hz" beside the HPF key.
  - Meter: thin rounded-rectangle outline around the LED column, with the dB scale (16 12 8 4 0 −4 … −20) on the
    left and "SET 0" at the bottom.
  - Faders: ticks on both sides of the slot, numerals on the right, a heavier bar at 0. The input scale reads
    10 5 0 5 10 15 20 25 30 40 50 60 ∞; groups read 0 … 70 ∞.
  - Key legends are printed on the key caps.
  - The channel numbers are on the frame, not the module.

## Our adaptation (two pot columns 20.32 mm apart, rows 22 mm, Ø13 knobs)

- **Names:** above the knob, centred, bold condensed (Arial Narrow Bold in the model). The Delta's upper-right
  column needs a single-column module about 40 mm wide.
- **Pairs:** HI MID and LO MID gain + FREQ are joined by a bracket over both knobs, with the band name in the middle,
  as the Delta's "]".
- **Rings:** 11 square dots (21 on GAIN). Numerals are placed in the Delta's priority order:
  1. ends;
  2. top;
  3. 9 / 3 o'clock;
  4. the rest.

  A numeral is dropped where it would land in a neighbouring knob's ring, a switch, LED, jack or a name. In
  practice, at the 20.32 mm column pitch, most rings print in full; only numerals that would touch a
  neighbouring ring or name are dropped.
- **Scales:**
  - EQ: 15 … −0+ … 15 with "dB".
  - Levels: 0–10.
  - PAN: L5 … 0 … 5R.
  - GAIN: −15 … +15 at the true positions of our gain-stage law (G = (2K2 + 10K θ) / (2K2 + 10K (1 − θ))), with "dB".
  - FREQ: the KHN centre frequencies at θ 0 / .25 / .5 / .75 / 1 from `sim/mid_tuning.py`:
    - HI: 0.7 1.6 2.2 4.8 10KHz;
    - LO: 0.15 0.34 0.48 1.0 2.3KHz.

    The law is two-slope, not log, so the numerals are uneven.
- **Faders:** the Delta input scale (10 5 0 5 … 60 ∞), placed with a two-slope A taper (15 % at mid travel) plus the
  +9.9 dB post-amp. This is approximate until the chosen fader's own law is known.
- **Rules and meters:**
  - Section rules: strip y 152.2 / 221.2 / 236.6 / 264.6, group 118 / 207 / 264.6, master 112 / 196.
  - The master meters get the Delta outline box.
- **Switch legends:** printed on the panel above each switch; the PRE keys read PRE 1-2 / 3-4 / 5-6. The C&K PV caps
  can't carry printing.

## Photos (pages verified reachable on 2026-10-23)

- 200 Delta D201 input, whole module: https://www.ebay.de/itm/335779458001
- 200 Delta 32ch: inputs, groups, master, faders — the sharpest legend reference:
  https://reverb.com/item/99123955-soundcraft-delta-200-deluxe-32-channel-analog-recording-console-made-in-england-cps275-psu-serviced
- 200 Delta 24ch group and master faders: https://reverb.com/item/14961008-soundcraft-delta-200-24-channel
- 200 Delta D203 group, neutral light (colour reference): https://www.ebay.de/itm/366724474090
- 200 Delta D204 master: https://reverb.com/item/7192782-soundcraft-delta-200-master-module-model-d204
- 200 Delta D203 group, head-on: https://reverb.com/item/87692230-soundcraft-delta-200-90-s-group-module-d203-nr-1
- D201 input, section by section, straight on: http://www.av-kompaniet.se/Beg_details/Soundcraft%20Delta_Input_D201.html
- 200 Delta and DLX photo sets (D202 whole faceplate, DLX D201, frames):
  https://fr.audiofanzine.com/console-analogique/soundcraft/Delta-200/medias/photos/ and
  https://fr.audiofanzine.com/console-analogique/soundcraft/delta-dlx/medias/photos/
- Delta DLX 16 overhead: https://reverb.com/item/5722815-soundcraft-delta-dlx-16-channel-analog-console
- Soundcraft's own DLX product page: https://www.soundcraft.com/en-US/products/Delta-DLX
- Sound On Sound review of the 200 Delta (Nov 1989): https://www.muzines.co.uk/articles/soundcraft-200-delta/5691
