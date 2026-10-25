# BOM sourcing check (2026-10-25)

I checked every MPN on the nine BOMs: 86 unique part numbers, at console quantities (24 strips, 4 groups, the master,
the PSU and the jig). Each was checked for an exact orderable code, its lifecycle and its stock. One agent searched the
distributors and I re-checked its doubtful claims by hand (Tayda, findchips, RS, Farnell, DigiKey). Stock figures are
snapshots from aggregators; check the live page before ordering.

## Applied (MPN fields only, no netlist or footprint change)

| Part | Was | Now | Why |
|---|---|---|---|
| Wing / jig PTCs | Bourns MF-RX160/72, 185/72, 250/72 | the same with `-0` | `-0` is the straight-lead order code |
| 1 µF 0805 X7R (strip) | Murata GRM21BR71H105KA12 | GRM21BR71H105KA12**L** | packaging suffix needed to order |
| BAT54W | Nexperia BAT54W | BAT54W,115 | order code |
| LM1084 (PSU) | TI LM1084IT-ADJ | LM1084IT-ADJ/NOPB | the orderable RoHS code |
| LME49600 (master) | TI LME49600TS | LME49600TS/NOPB | same |
| SS54 clamps | "SS54" / onsemi SS54 | Diodes B540C-13-F | SMC 40 V 5 A from a named maker; value text kept "SS54" |
| S1G (PSU) | "S1G" | Diodes S1G-13-F | named maker |
| Strip C0G caps | KEMET C0805… | KEMET C1206C…J5GACTU | every strip C0G sits on the 1206 footprint |
| Strip C0G 2n2 / 4n7 / 10n / 22n / 100n | none | KEMET C1206C222 / 472 / 103 / 223 J5GACTU, Murata GRM31C5C1H104JA01L | were missing |
| Strip C1 / C3 220 µF | Nichicon UPW1V221MPD (10 × 12.5) | Rubycon 35ZLH220MEFC8X11.5 | fits the strip's D8 / P3.5 footprint |
| Strip C5 / C6 47 µF | Nichicon UPW1J470MPD (8 mm) | Panasonic EEU-FR1H470 | fits the strip's D6.3 / P2.5 footprint |
| Group C1 / C2 220 µF | Nichicon UPW1V221MPD (not for new designs, no stock) | Nichicon UHE1V221MPD6 | 10 × 12.5, P5, the group's footprint; Farnell ~1900 |
| Jack board C8 / C9 100p C0G | none | KEMET C0805C101J5GACTU | was missing |
| Strip D1 | none | Vishay 1N4148-TAP | as the master |
| PSU caps | none | Rubycon 35ZLH2200MEFC16X25, 35ZLH220MEFC8X11.5, Panasonic EEU-FR1H470, Samsung CL21B104KBCNNNC, KEMET C0805C222J5GACTU (C0G) | were missing; each in its footprint |
| PSU LEDs | none | Kingbright WP710A10GD | as the strips |
| Phoenix terminals | series names | 1755897 (7-way), 1715721 (2-way), 1715734 (3-way) | order numbers (1755897 confirmed at RS as MKDS 1,5/7-5,08) |
| Master R57 22M | none | Yageo RC0805JR-0722ML | was missing |
| Master CN4 | none | Sullins PRPC005SAAN-RC | was missing |

Left without an MPN, by design: the DNP VCA socket / header on the strip (J3, J4) and the master's M4 star point (CN1,
a hole).

**Resistors.** Plain 0805 values carry no MPN. Rule: buy them as Yageo RC0805FR-07xxxL (1 %, 0.125 W) or any
equivalent 1 % thick-film 0805. Every part that needs more (anti-surge, 0.1 %, 2512) already has its own MPN.

## Checked and kept

- **Alpha pots.** The agent called RD902F-40-15R1-A10K "not stocked anywhere". Wrong: Tayda stocks it (SKU A-6980,
  700). It also stocks RD901F-40-15R1-A10K (A-1856, 1775), -B10K-0CD (A-8401, 741) and -A10K-0CD (A-7815, 220).
- **DG413DY-E3** is the tube code, stocked (Mouser ~4700, RS). It is not a mistake for -T1-E3, the reel.

**Follow-up (2026-10-25).**
- **C48 (strip, 150 nF film):** now WIMA MKS2D031501C00KSSD, the 100 V version of the same part. It is
  3.5 × 8.5 × 7.2 mm on a 5 mm pitch, so it fits the W4.5 footprint. No 63 V KSSD stock was found anywhere.
- **OPA1656:** one order code everywhere, OPA1656IDR. The master, group and jig used to say OPA1656ID (tube).

## Order list

`python3 tools/order_bom.py` writes `order_bom.csv`.
- **What it does:** takes each board's BOM times the boards built (24 strips and strip jack boards, 4 groups and group
  jack boards, one each of master, master jack board, PSU, jig stub and jig load board), one line per order code.
- **Additions:** the 16 OPA1656s for the jig's A/B strips. The jig's four strips are four of the 24.
- **Spares:** SMD R / C +10 % (at least 10), semis and LEDs +5 % (at least 2), electrolytics and film +5 % (at least 2),
  panel parts and connectors +3 % (at least 1).
- **Resistors:** plain 0805 values get `Yageo RC0805FR-07<value>L`.
- **Left out:** DNP parts and the M4 star point.
- **Not on any board, so not in the list** (they are in `offboard_bom.md`): knobs, fader caps, LED spacers, standoffs, ribbon and IDC sockets, the
  harness, the PSU modules and its case parts. See the specs (§16 of the strip spec, master spec §26, `psu_spec.md`).

## Stock risks: act before ordering

| Part | Needed | Situation | Action |
|---|---|---|---|
| Bourns PTB0143-2010BPA103 | 28 (24 strips + 4 groups) | DigiKey showed exactly 28 | buy 28 + spares now, or check Mouser / Bourns lead time |
| Neutrik NJ6FD-V | 101 (72 strip, 20 group, 9 master) | ~14-week lead time quoted | order first |
| TI OPA1612AIDR | 311 (264 strip, 28 group, 13 master, 6 jig) | LCSC the only volume stock seen | buy at LCSC, or split across distributors |
| TI LM1084IT-ADJ/NOPB | 2 | little stock | buy with the first order |
| WIMA MKS2C042201K00KSSD (2.2 µF film) | 100 (72 strip, 16 group, 12 master) | DigiKey out of stock; Farnell ~1080 | buy at Farnell now; no design change |
| WIMA MKS2D031501C00KSSD (150 nF film, C48) | 24 | the 63 V code (MKS2C031501A00KSSD) has no stock anywhere; RS ~1135 of this 100 V one | swapped (below) |

If the 2.2 µF WIMA does disappear, TDK B32520C0225J000 is the nearest film part. It is on a 7.5 mm pitch
(10.3 × 6 × 12 mm), so it needs a new footprint and re-placement. That would be a proposal of its own; it isn't needed
now.

## For sign-off

**S1. The 10 µF NP (Nichicon UES1E100MDM) is discontinued.** DigiKey lists the taped code as obsolete; Audiophonics says
the product line is stopped. It is used in 36 places:
- every DRV135 sense-leg cap: master 14, group 4 per board (16), jig 2;
- the master's four ±VP supply bypasses at the LME49600s.
- **Position:** each sense-leg cap sits inside the DRV135's loop, after the output and before the Sense pin. The
  driver's loop gain corrects its distortion, so an audio-grade part buys nothing there. The bypasses aren't in the
  signal path at all.
- **Proposal:** a general-purpose 25 V 10 µF bipolar in the same 5 mm / P2.0 footprint, Panasonic ECE-A1EN100U (SU).
  No footprint, netlist or placement change. This touches the signed F1–F4 note "bipolars are MUSE ES", so it needs
  your sign-off.
- **Alternative:** stay MUSE ES with UES1H100MPM (50 V). It is 8 mm, so the 36 footprints go to D8 / P3.5 and the
  group and master are re-placed.

Signed off by Ruslan on 2026-10-25.

- [x] **S1** 10 µF NP → Panasonic ECE-A1EN100U, drop-in (DRV135 sense legs and jig).

**Applied (2026-10-25).**
- `master_lib.CAP_MPN['10u NP 25V']` = Panasonic ECE-A1EN100U: 5 × 11 mm, 2.0 mm pitch (RS, Future); stocked at RS
  and Master Electronics.
- Changed parts: master 18, group 4, jig stub 2. Netlists unchanged but for the MPN field.
- Checks: 0 mismatches, check_fp 0, ERC 0. Re-placed with 0 parts moved; parity DRC clean on the group, master and
  jig stub.
