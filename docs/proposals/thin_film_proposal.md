# TF1 — thin-film resistors for the plain 0805 positions

**Signed off by Ruslan 2026-10-29 ("continue") and applied the same day; see Sign-off.** Raised by Ruslan 2026-10-29 ("I'm afraid to use thick film"). The change is one rule in
`tools/order_bom.py` (`archive/patches/thin_film_proposal.patch`): no netlist, footprint, placement or value changes;
the schematics carry no MPN for these parts, so nothing is regenerated.

## What is proposed

Every plain 0805 resistor up to 1 MΩ is ordered as **Yageo RT0805FRE07<value>L** (thin film, ±1 %, ±50 ppm/°C,
0.125 W, 150 V) instead of **Yageo RC0805FR-07<value>L** (thick film, ±1 %, ±100 ppm/°C, 0.125 W, 150 V). Same
footprint, same values, same tolerance class.

| | Lines | Parts (console + spares) | Per board |
|---|---|---|---|
| Thin film RT0805FRE07, ≤ 1M | 62 | 4411 | strip 126, group 90, master 181, PSU 16, jig stub 18, jig load 21 |
| Stay thick film RC0805FR, > 1M | 4 | 91 | 2M2 (11), 4M99 (34), 10M (35), 22M (11) |

Values: 10R … 1M, 62 of them, E24 plus the E96 ones the design uses (392R, 1K18, 1K58, 1K82, 2K49, 4K22, 4K99, 5K49,
7K32, 64K9, 66K5); the RT series carries E96 for the 1 % grade (distributor listings show 5K36, 8K66, 12K7, 49K9;
confirm each code at order time as `docs/build/sourcing.md` does for every MPN).

## What stays as it is, and why

- **Anti-surge Panasonic ERJ-P06 (thick film, 7 values):** the 75R insert / direct-out build-outs, the DRV135's 22R
  loop resistors, the 1R and 4K7 rail feeds, the rude-solo 3K3, the PSU's ADJ 1206s. They were chosen (T9 / T10,
  MG11, CS4c, RV1) for the pulse and short-circuit cases: an ESD hit or a shorted output lead. A surge is what thin
  film survives worst (the film is tens of nm thick and evaporates), so those positions keep the part picked for them.
- **Above 1M:** no RT part; all four values are DC positions (OL detector dividers, the mute timer and Schmitt
  hysteresis), where film type cannot matter.
- **Already thin film:** Panasonic ERA-6AEB 0.1 % (receiver 10Ks, re-inverter 2K2s), Vishay M25SI fusibles.
- **Vishay CRCW2512 2R2 1.5 W:** a power part in the phones supply; thick film is the right construction there.

## Why thin film, honestly

- **Distortion.** Thick film has a voltage coefficient of resistance; the resistance changes with the instantaneous
  voltage across it, which is third-harmonic distortion. Published measurements (Self, *Small Signal Audio Design*,
  resistor chapter) put a thick-film 0805 with ~10 Vrms across it at about −95 to −105 dB THD, falling 20 dB per
  decade of voltage; thin and metal film sit below the analyser floor. At the console's 0 dBu it is about 20 dB
  under those numbers and masked by the op-amps' own −110 dB and the bus noise; it shows only near full swing, in
  the gain stage's 2K2 / 10K, the EQ's 22Ks and the KHN networks, the post-amp's 4K7 / 2K2, the pan and the 4K7 / 22K
  summers. So: a real, measurable effect, small at normal level, gone with thin film.
- **Noise.** Thick film's excess (1/f) noise index is 10-20 dB worse than thin film's, but it scales with the DC
  voltage across the part. The audio resistors sit at 0 V DC (AC-coupled stages; bias drops of tens of mV), so there
  is nothing to gain here. The PSU and reference dividers do carry DC and do get quieter; they are not in the path.
- **Drift and tempco.** 50 ppm/°C against 100-200 ppm/°C, and thin film's load-life drift is a few times smaller.
  It is what keeps the KHN mid and HPF tunings, the pan law and the CMRR of the 1 % networks where the sims put them
  after years in a 40 °C tub (`docs/studies/thermal_study.md`).
- **What it does not buy:** nothing audible at 0 dBu on a mix of synths; the Delta's own metal-film 2 % resistors
  (spare-parts list p.151-162) are the same class as these thin films, so this is parity with the parent, not an
  upgrade over it.

## Cost and sourcing

Cut-tape prices for RT0805FRE07 run about $0.03-0.10 at 1-100 pieces and $0.008-0.015 at 1000-5000 (Mouser, LCSC,
RS listings, 2026-10-29), against $0.003-0.01 for RC0805FR. The four big values (4K7 614, 47K 437, 10K 379, 22K 369
parts) are bought at reel breaks; the other 58 lines are cut tape. Expected delta: **about €80-150 for the whole
console**, €10-15 for phase 1 (one strip + jack board + jig). Stock: a mainstream Yageo family, but single values do
show 20-28 week factory lead times at some distributors; if a value is out, the RC0805FR code still fits the
footprint and is the recorded fallback for that value only.

## Checks after sign-off

`order_bom.py` and `order_bom.py phase1` (done on the trial: 62 RT lines / 4411 parts, 4 RC lines / 91 parts),
`check_all.py` (nothing else changes), `docs/build/sourcing.md` decision line, CLAUDE.md "Sourcing" one-liner, BOM note in
`channel_strip_schematic_spec.md` §15.

## Sign-off
Signed off 2026-10-29 and applied: `order_bom.py` rule, order lists regenerated (62 RT lines / 4411 parts, 4 RC lines /
91 parts), `docs/build/sourcing.md`, `docs/decisions.md`, CLAUDE.md. Alternatives considered (and MELF, declined by Ruslan 2026-10-29: same film class, only pulse / power / voltage
better, none needed here; a footprint change on every plain resistor and a full re-placement, 3-10× the price): (b) thin film only in the ~20 full-swing signal values (saves ~€30, needs a per-value list to
maintain; not recommended); (c) keep thick film and decide on the jig's THD at +18 dBu (the earlier note in
`docs/build/sourcing.md`).
