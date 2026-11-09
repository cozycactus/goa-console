# SS1-SS3: second sources for the parts holding up stage A (proposal, 2026-11-03)

**Signed off by Ruslan 2026-11-03 (SS1, SS2, SS3 with H3 for stage A) and applied 2026-11-04**, after the master stability run
that read `master.net`. The change for SS1 and SS2 is `archive/patches/second_source_proposal.patch`. It touches tools only:
`gen.py`, `gen_group.py`, `gen_psu.py`, `master_lib.py`, `place_group.py`, `order_bom.py` and `sim/review/cs10/rail_loss.py`.
It changes order codes and one value label; no netlist connection, footprint or part position changes.

## 1. Why

The 2026-10-28 pricing flagged several stage-A parts as backordered, two of them to autumn 2027. I re-read them on
2026-11-03: Nexperia's small-signal diodes have gone to zero stock across the board, with 53-week lead times, and
**BAV99,215 has joined them since 28 Oct**. Stage A can't be ordered as the list stands.

All stock and prices below are from Mouser's site on 2026-11-03, as "stock; price @1 / @10". Mouser then blocked further
lookups from the browser, so §6 lists what wasn't re-read.

## 2. SS1: the same part in other packing (order lists only)

The schematics keep their codes. A new `ORDER_AS` table in `order_bom.py` swaps the code on the order lists, so it's undone
by deleting a line when stock returns.

| Code today | Mouser | Buy instead | Mouser | Console order |
|---|---|---|---|---|
| TI OPA1612AIDR (reel) | 0; 42,249 on order, 26 wk | **TI OPA1612AID** (tube) | 516; $9.52 / $7.41 | 335 |
| Nexperia BAV199,215 (7" reel) | 0; 783,741 on order, 53 wk | **Nexperia BAV199,235** (13" reel) | 1,631; $0.26 / $0.151 | 236 |
| Vishay DG413DY-E3 (tube) | 0; 7,457 on order, 19 wk | **Vishay DG413DY-T1-E3** (tape) | 57, 5,000 due 2026-12-25; $1.70 / $1.25 | 77 |

- **Why:** identical silicon and package, so nothing else needs checking.
- **Cost:** the OPA1612 tube is about $1.70 more than the reel at 10 pieces ($7.41 against $5.71). The phase-1 prices already
  assume the tube. For the whole console that could be about $570 at the 10-piece price, so re-check the reel before the
  console order.
- **Trap:** Mouser also shows **OPA1612AIDRGR with 2,179 in stock. That's the SON-8 package, not our SOIC-8.** Don't buy it.
- **DG413:** stage A's 5 are covered by the 57 in stock; the console's 77 need the December delivery.

## 3. SS2: another maker, same footprint

| Today | Mouser | Proposed | Mouser | Console order |
|---|---|---|---|---|
| Nexperia BZX84-C5V1,215 | 0; 53 wk | **Diodes BZX84C5V1-7-F** | 5,897, 186,000 on order; $0.22 / $0.105 | 27 |
| Nexperia BAV99,215 | 0; 53 wk | **Diodes BAV99-7-F** | 683,125; $0.18 / $0.08 | 126 |
| Nexperia PMEG4010CEH,115 | 0; 29,435 due 2027-09-24 | **onsemi MBR140SFT1G** | 24,002, 108,000 on order; $0.60 / $0.269 | 59 |
| Panasonic EEU-FR1H470 | 0; 37 wk | **Rubycon 63ZLH47MEFC6.3X11** | 1,549; $0.43 / $0.285 | 53 |
| Rubycon 35ZLH220MEFC8X11.5 | no stock read; 18 wk | **Panasonic EEU-FR1E221** | 8,028, 5,800 due 2027-01-07; $0.73 / $0.451 | 53 |

**Same maker first:** Nexperia's nearest SOD-123F parts are out too (PMEG4010EH,115 0 stock; PMEG6010CEH,115 due 2027-11-05),
so the Schottky has to change maker.

**BZX84C5V1-7-F** (Diodes DS18001, read): Vz 4.8-5.4 V at 5 mA, 300-350 mW. SOT-23 with pin 3 cathode, pin 1 anode, pin 2 not
connected, which is how D9 is wired (`{3: '+5VL', 1: 'GNDD', 2: 'NC'}`).

**BAV99-7-F** (Diodes DS12007, read): pin 3 is the common node and pins 1 / 2 the outer ends, as the symbol. 75 V, 300 mA, at
most 25 nA at 20 V. In the overload detector (CS1) five of them into R134 470K make at most 59 mV at 25 °C, against
thresholds near 9 V. Strip only (5 per strip).

**MBR140SFT1G** (onsemi MBR140SFT1/D, read): 40 V, 1 A, 30 A surge.
- **Fit on the existing `D_SOD-123F` pads** (1.1 × 1.1 at ±1.4 mm): the leads reach ±1.70-1.90 mm, each foot is 0.55-0.95 long
  and 0.70-1.10 wide, so the feet land on the pads across the tolerances; at worst a foot runs 0.1 mm past a pad's inner edge. Cathode band
  at pin 1, as the footprint.
- **CS10 still holds:** `rail_loss.py mbr` uses the datasheet's maximum Vf (0.36 V at 0.1 A, 0.55 V at 1 A) and gives the same
  result as the PMEG: a dead rail held to ±0.36 V, 0 mA through the ICs' protection diodes.
- **The cost:** more reverse leakage. At most 0.15 mA at 20 V and 25 °C (typically about 10 µA at 17 V), rising to 18 mA maximum
  at 85 °C. The tub runs about 16 K above the room (`docs/studies/thermal_study.md`), where I estimate about 10 mA across the console's 56
  diodes from the datasheet's typical curves, against a 4 A rail. The datasheet's derating curve for 17 V reverse stays well
  above that temperature.
- **Value label:** the schematic value becomes MBR140SFT1G on strip D16 / D17 and group D5 / D6.

**63ZLH47MEFC6.3X11:** 47 µF, 63 V, Ø6.3, 2.5 mm pitch on the existing footprint (rating 50 V before). One listing gives 12.5 mm
as its maximum height. Strip C5 / C6 are on the bottom side, clear of the 11.5 mm panel gap, and the PSU board has no panel.

**EEU-FR1E221:** 220 µF, Ø8 × 11.5, 3.5 mm pitch on the existing footprint. It's rated 25 V against 35 V today. The schematic
value already says 25 V, the rails are 17 V and the crowbar fires at 19.1 V. I passed over Rubycon's 35ZLQ220MEFC8X11.5
(6,007 in stock, Mouser's own suggestion) because I couldn't confirm its pitch.

**Further options, not checked:** BAV199: onsemi BAV199LT1G (90,864), Diodes BAV199-7-F (13,626). DG413: Renesas DG413DYZ
(1,712, $2.63 at 10), Analog Devices DG413DY+T (1,085, $6.55). I didn't check these against the circuit.

## 4. SS3: the PVA2 keys (a decision for stage A)

This is what really sets stage A's date, and there's no other maker with this footprint.

**C&K PVA2 EE H1 1.7N V2:** Mouser 0, 1,441 due **2027-03-01**, enough for the console's 371. DigiKey lists it (13 wk), but I
couldn't read a stock count.

**The alternative for stage A: PVA2 EE H3 1.7N V2.** Mouser 1,694 in stock, $2.79 / $2.49, the same price.

From C&K's PVA datasheet (rev. 02/20/25):
- **EE is push-push, so it latches. OA is momentary**, so the in-stock PVA2 OA parts are no use here.
- **Total height:** H1 17.5, H3 20.5, H2 23, H4 15, H5 13 mm.
- **PV caps fit only H1 and H3.** So H3 is the only in-stock height that takes our caps; H2 is out.
- **Same pads and contacts:** only the plunger is longer, read from the height drawings at low resolution. Check on a sample.

**What it costs:** the cap stands 3 mm higher above the panel. That doesn't matter on a bench strip, but H3 can't settle the
H1-specific sample checks (cap clearance in the 8.0 mm hole, panel stack height). Those need H1 keys when they arrive.

**Recommendation:** H3 for stage A's 14 keys and any second strip, H1 for the console. Stage A can then start now rather than in
March. It isn't in the patch: on sign-off it's one more line on the phase-1 list. If you'd rather not mix heights, the
alternative is to order H1 and start stage A in March.

## 5. Checks on the trial tree (SS1 + SS2)

**Regenerated and re-placed** every board in a clone, KiCad 10.0.7:
- **Parts:** no footprint moved. Changed fields only: strip 12 parts, group 2, master 1, PSU 4; the jack boards and the jig
  are unchanged.
- **`check_all --full`:** 72 / 72 (strip 946 pins, group 807, master 1820, 0 mismatches; 0 DRC / parity).
- **`bom/order_bom.csv`:** every proposed code appears at the quantities above, and no old code remains.
- **`rail_loss.py mbr`:** ±0.36 V and 0 mA in every lost-rail case, as the PMEG.

**Not touched:** the master stability run in progress reads the repo, so nothing here is applied yet.

**On applying (2026-11-04), two additions to what was tried:**
- **The phase-1 list:** the trial's `ORDER_AS` reached `bom/order_bom.csv` only, so `bom/order_phase1.csv`, the list ordered first, would
  have kept the out-of-stock codes. `board_lines()` now uses it too, and the patch here is the final change.
- **SS3:** `BENCH_KEY` puts H3 on stage A and the second strip (14 each: 13 keys + 1 spare). Check 3's 4 samples stay H1 on stage A,
  because the cap clearance is the console key's question; they arrive in March, and may be better on an order of their own.
- **Price:** stage A $452.04 -> $463.65: $11.16 for those samples, $0.45 for the rest. A second strip $322.25 -> $322.70.

## 6. Not re-read on 2026-11-03

**Most of these were read on 2026-11-04 (`bom/mouser_readings.csv`); what's left is 7 thin-film values, the ceramics and 3 RC0805s, all shown live by the BOM upload `bom/order_stage_a_mouser.csv`.** Two more out-of-stock lines turned up: thin-film 1K5 (R64, TF1's RC0805 fallback on the bench strips) and WP710A10GD as below.

Mouser blocked lookups before these. They showed no problem on 2026-10-28, except where noted, and should be re-read at order
time: MMBFJ112, MMBT3906LT1G, UES1E330MPM, UES1E101MPM, MKS2D031501C00KSSD, MMK5225K63J06L4BULK (1,841 on 2026-10-29),
NJ6FD-V, WP710A10ID / YD, WP3VEGW, RK09L1240015, M251206BB1009JP500, PTB0143 / 0144, Würth headers and sockets, ERJ-P06 and ERA-6A resistors,
the thin-film RT0805 resistors, the C0G and X7R ceramics, and everything only on stage B.

**Read and fine:** LM393BIDR 11,122; OPA1656IDR 12,494; BAT54W,115 184 (the console needs 52; buy them early).

**No action, short wait:** Kingbright WP710A10GD (stage A 4): 19,878 due 2026-12-07.

## 7. On sign-off

- Apply the patch once the master run has finished, regenerate and re-export (netlists, BOMs, PDFs), re-place, re-run netrules
  and `order_bom.py` (both modes).
- Re-price the changed lines in `bom/order_phase1_prices.csv`: stage A's total barely moves (about +$0.30 at the same price breaks).
- **Update:** `docs/build/sourcing.md` (order codes, stock table), `docs/decisions.md` (CS10's and CS4's part names), the strip spec's parts
  list, CLAUDE.md.

## Sign-off

- [x] **SS1** as proposed: OPA1612AID, BAV199,235 and DG413DY-T1-E3 on the order lists. Signed off 2026-11-03.
- [x] **SS2** as proposed: BZX84C5V1-7-F, BAV99-7-F, MBR140SFT1G, 63ZLH47MEFC6.3X11 and EEU-FR1E221. Signed off 2026-11-03.
- [x] **SS3** PVA2 EE H3 for stage A and any second strip, H1 for the console. Signed off 2026-11-03.
- [ ] SS3 instead: H1 only; stage A's keys arrive in March 2027.
