# Clipping waveforms: the Delta DLX's op-amps against ours (2026-10-29)

`sim/review/clipping/clip.py` (ngspice 42, PSpice compatibility mode; TI's models from `$TI_MODELS`, default
`sim/review/clipping/models/`, kept out of the repo: SLOJ067 TL072 1989 macromodel, SLOM513 TL07xH, SBOM396 OPA161x,
SBOMAW6 OPA1656). ±17 V, 10 kΩ load, 1 kHz, 14 / 16 / 18 V peak in (+22.1 / +23.3 / +24.3 dBu).

- `clip_follower.png` — unity follower (the Delta's gain-pot buffer, Sallen-Key HPF, post-amp and direct-out buffer are
  non-inverting; ours: the U16 receiver followers, pan buffers, insert return, CRS followers).
- `clip_inverting.png` — unity inverter, 10K / 10K (EQ stages, summers, re-inverters, the mute inverter).
- `clip_zoom.png` — one negative half-cycle of the follower at 16 V peak, all models.

## What the pictures show

| Part | Follower peaks at 16 / 18 V in | Inverter peaks at 18 V in | Character |
|---|---|---|---|
| TL072 classic (1989 macro + reversal) | +15.5 / **flips to +15.5 below −13.4 V** | ±15.5 | the negative half-cycle's bottom is replaced by a flat top at the positive rail |
| TL072 1989 macro, as TI published it | ±15.5; at 18 V in it also flips (its JFET gate junction conducts below ≈ V− + 0.5 V) | ±15.5 | output clipping only until the input goes under V− |
| TL07xH (TI 2020, the redesigned die) | +16.9 / −16.0 (input clamp at V− + 1) | ±16.9 | clean, slightly asymmetric |
| OPA1612 (ours) | ±15.0 (input range V± ∓ 2 V), ±15.5 at 18 V | ±16.7 | clean; the wobble at 18 V in is the macromodel's input-range clamp driven from a 0 Ω source |
| OPA1656 (ours, U16 etc.) | **+14.75** (input range V+ − 2.25) / −16.0..−17.0 (rail-to-rail output) | ±16.9 | clean but asymmetric in a follower: the top is the input limit, the bottom the output |

- The reversal is the one qualitative difference. The classic TL072's input stage stops working about 3 V above V−
  (datasheet typical VICR −12 V on ±15 V); in a follower that is 1.5 V before its output would clip, and the output
  snaps to the positive rail for as long as the input stays below the limit, then recovers (the spike at 14 V in is
  the input just touching the limit). None of TI's models carries it, so `tl072_classic.lib` adds it to TI's 1989
  macromodel phenomenologically (an input under the limit is replaced by V+, blended over 0.2 V). TI's bare 1989
  macro shows the same flip once the input goes below V−, which is the mechanism (the JFET gate junction) at the
  wrong threshold; the TL07xH model is a different die, redesigned without it.
- Inverting stages never see it: their inputs sit at the virtual earth. Every part clips the same way there, hard,
  within 0.5 dB of each other.
- Ours clip cleanly everywhere. The OPA1656 follower's +14.75 V ceiling (+22.6 dBu on these rails; +21.9 dBu in the
  strip with its 10R-fed +VA, RV6) is the input common-mode range, not the output: a hot source clips the U16
  receiver followers before anything else in the strip, flat-topped on the positive half only. The Delta's line
  receiver attenuates before its op-amp, so it reaches +30 dBu at minimum gain; the price of our unity receiver.
- Headroom at the stage outputs is the same within 1 dB: +23.0 dBu (TL072) against +23.3..+23.6 dBu (OPA1612 /
  OPA1656), both on ±17 V; the Delta's −2 dBu internal level buys it 2 dB that its followers' reversal takes back.
