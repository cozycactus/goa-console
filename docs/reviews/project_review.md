# Project review (2026-10-28): circuits, tooling, documentation, repo cleanup

Independent review of the whole tree at a45a1be (strip v5.5, group with CS2b, master with CS7), five reviewers (strip,
master, group / jig / PSU, tools, documentation), every finding re-traced in the netlists or the source before it was
kept. Proposals carry IDs RV1-RV14 for sign-off.

**Status (2026-10-28, Ruslan: "continue" on the proposed split):** APPLIED: RV1 (PSU R2 / R11 ERJ-P06F1501V 1206 0.5 W,
PSU regenerated and re-placed), RV2 option (a) and RV10 (`test_jig_spec.md` v0.10: tests 2-4 at N = K with the 1 − N/K
law written in, δ measured during the injection, the wing-current test's PTC / supply), RV11.1-7 (`check_all.py`
compares the committed `.net` with the fresh export and copies the intended JSONs beside the exports; new
`tools/check_bus.py`; sim_console +7 positive bus checks (every SUB and aux bus, 45 checks); `fab_out.is_known` one
footprint per item and the PSU rule `^(U1|U3|Q2|Q4)$`, route_check no-result refused, any layer numbering; `check_fp.py`
both directions with KiCad 7 / 8+ pad syntax (a wrong package fails; named contacts without a pin, the jacks' SN and the
XLRs' G, are notes); route_check check 5 skips ground / rail nets and the op-amp list is OPA / TL072 in netrules and
route_check (the DRV135's pins are not inputs: 5 master nets leave HighZ, 8 TL072 input nets join it); the DIM phones
check fails on a missing node; `write_intended` refuses a ref / unit placed twice; the placer's routed-board guard sees
drawn copper), the §3 stale facts (every file but the ones below), the three title-block revisions, `render/*.json`
and the escape plan regenerated. RV3 / RV4 / RV7 / RV8 / RV9 (the circuit batch, `docs/proposals/clicks_proposal.md`) signed off and
applied 2026-10-28 (strip v5.6, master v0.13; RV5 / RV6 accepted as they are). NOT APPLIED: RV11.2's PFL switcher from the PFLDET net (needs a DC analysis of the detect line; the bus check covers pin
29), RV11.8 (ol.py from the netlist), RV12-RV14 (cleanup: patches to `archive/`, the CLAUDE.md split, tracked outputs),
the N1 A/B contradiction (`order_bom.py` EXTRA 16 OPA1656 vs the one-board swap of `test_jig_spec.md` §1.1).

Baseline re-run on this tree (Linux, ngspice 42, KiCad 7's `kicad-cli` for the exports, kiutils 1.4.8):
`verify.py` 0 mismatches on all nine boards (strip 937, group 805, master 1796, jack boards 32 / 60 / 89, jig 364 / 153,
PSU 119 pins); `check_fp.py` 0 problems on all nine (with the pad-regex fix of RV11, below: KiCad 7's library files
write `(pad 1 ...)` unquoted and the committed regex reads every library footprint as "pads []"); `sim_netlist.py`
45/45; `sim_console.py` 38/38; `order_bom.py` regenerates both CSVs byte-identical. The committed boards carry no
tracks, vias or copper zones (the one `(zone` on each 4-layer board is the RAILS rule area). Fresh netlist exports
from the committed schematics have the same pin-to-net partition as the committed `.net` files (KiCad 7 only names
the single-pin nets differently).

## 1. Circuit findings

Severity: ERROR = wrong behaviour, a rating exceeded or a test that can't give its verdict; WARN = degraded or a
risk; DOC = documentation / BOM drift. No ERROR was found on the strip, group or master.

### ERROR

**RV1 PSU: R2 / R11 (1K5, 0805) run at 164 mW, 131 % of their rating.** `gen_psu.py:43`: the LM1084 ADJ divider is
120R from OUT to ADJ and 1K5 from ADJ to the rail's return, so the 1K5 carries Vout - 1.25 = 15.7 V = 164 mW.
`bom/order_bom.csv` buys them as Yageo RC0805FR-071K5L (0.125 W at 70 C), beside the LDOs in the 1402KV case.
Fix: ERJ-P06F1501V (1206, 0.5 W) or ERJ-8ENF1501V (1206, 0.25 W); or 2 x 3K0 0805 in parallel. Values unchanged
(16.96 V).

**RV2 Jig: the load board's single 10R ground-cancel tap breaks the ground-cancel weighting, so tests 2-4 can't
meet their target.** `gen_jig.py:101-104`: the load board puts one 10R from its GNDA to pin 26 "like a strip", but
SW1-SW20 switch in up to 20 channels' worth of bus resistance. GCANCEL is the mean of the K boards with a tap
(4 strips + load board: K = 5; stage B: K = 2), the bus weights a ground offset by N = routed strips + n dummy
channels. For an offset d in one strip the stub's re-inverter gives d (1 - N/K): exact only at n = 1, and at n = 20
option D reads 11.6 dB WORSE than option A (stage B: 19.6 dB), while test 2 asks for ">= 40 dB better". Test 17's
figures already assume K = 5; test 2's target silently assumes N = K. A wrong "D fails" verdict would bring back the
balanced-bus options of §5. Fix, either: (a) specify tests 2-4 with every strip routed and the load board at exactly
one channel (N = K), and write d (1 - N/K) into the spec; or (b) make the load board's tap follow its switches
(10R / 3R3 / 2R5 / 0R82 per group on a second pole; a jumper on R1 for n = 0).

### WARN

**RV3 Strip: the direct out is impedance-balanced only above ~300 Hz.** `DO_T` = CN3.8 / D22.3 / R72.1 / C52.2
(C52 33 uF NP in the hot leg after R71 75R); `DO_R` = CN3.9 / R73.1 and R73.2 goes straight to GNDA, no capacitor.
The hot leg's source impedance is 75 - j96 ohm at 50 Hz against 75 ohm on the cold leg: into a 20K-per-leg receiver
the CMRR limit is ~46 dB at 50 Hz, ~52 dB at 100 Hz, ~72 dB at 1 kHz, weakest at hum frequencies. R71 is 5 % (ERJ-P06J750V),
R73 the plain 1 % Yageo: 3.75 ohm of mismatch caps the balance at ~75 dB anyway. Fix: a matching 33 uF NP in series
with R73 (DO_R - R73 - C - GNDA) and the same part for R73 as R71. The insert send is a TS pair, unaffected.

**RV4 Strip: the gain stage goes open-loop if RV9's wiper lifts.** `Net-(U1B--)` = U1.6, RV9.2, C37.2 only: the gain
pot's wiper is U1B's only DC feedback path (R45 RECV - RV9.3, RV9.1 - R46 - GOUT, as the Delta's ED3344A). A dirty or
bouncing wiper on the most-turned pot leaves 22 pF of feedback; the 60-250 nA bias ramps GOUT at 3-11 V/ms to a rail:
a bang on PRE and every bus. Every other pot here keeps a path if its wiper opens. Fix: ~1M from GOUT to U1.6 (0.1 dB at
+15 dB, nothing at the detent). Stability unchanged in kind (parallel 1M on 10K-50K); re-run c01 on the TI model.

**RV5 Strip: DC on the fader track and the pre-fade aux pot tops.** MUTEOUT (U3B out, U3.6 / U3.7) drives RV1.3 and,
through JP2-JP4 and SW8-SW10, the aux pot tops. U3B's bias flows through R17 + R16 + R13 = 56.4K: MUTEOUT sits at
~3.4 mV typical, ~14.6 mV worst (250 nA + Vos), the mechanism K1 fixed for PFL. A fader move steps FPIN through C13 and
gets +10 dB (up to ~46 mV at POST); turning an aux pot with PRE latched pushes a changing DC into the 22K bus. `keys.py`
only tested key presses with the pots at mid. Fix: R13 10K (worst ~4.9 mV; C11 100 uF still gives 0.16 Hz), or
AC-couple the MUTEOUT feeds. Low severity: scratchy pots on worn tracks, not a fault when new.

**RV6 Strip: the U16 receiver followers set the input headroom at ~+21.9 dBu, not the +23 dBu stated.** The OPA1656's
common-mode range ends at (V+) - 2.25 V (datasheet; no phase reversal). +VA is ~15.9 V after R1's drop at the strip's
current, so the tip leg clips at ~13.7 V peak = +21.9 dBu on positive peaks (unbalanced synths, the main case).
`docs/proposals/gaps_proposal.md:63-66` states +23.0 dBu at unity. The OL LED still lights first (RECV tap at +18.4 dBu). Fix:
document +21.9 dBu, or accept.

**RV7 Master + group: the aux AFL keys put DC onto the PFL bus (the click K1 fixed on the strip).** `gen_master.py:125`
(R69 / R80 22K from A5_OUT / A6_OUT) and `gen_group.py:85` run straight from the level-buffer followers' outputs to the
AFL key. Those outputs are biased by the buffers' 100K (`master_lib.level_buffer()`, R66 / R77): 6 mV typical, 25 mV
worst at 60-250 nA. A press moves the 22K from GNDA onto the PFL virtual earth: a unity-gain DC step, still 96 %
intact when the DG413 switches 5.8 ms later (the couplers' 0.2-0.3 s constants), a tick of ~-42 dBu typical / -30 worst
at CRS, +6 dB at the C/Room TRS; the reverse step on release. Every other PFL / AFL source is AC-coupled (strip K1,
group sub AFL after the coupler, return PFL from PRE). Fix: a 2.2 uF MKS2 film in series with each aux-AFL 22K
(master 2, group 1 per board), as K1 (C96).

**RV8 Master: the phones output carries DC and the mute relay closes onto it.** The OPA1612 U26 + LME49600 composite
is DC-coupled to the jack; its + inputs sit on R129 / R133 100K and its DC gain is 1 + 4K7 / 2K2 = 3.14 (R131 / R132,
R135 / R136): ~19 mV typical, ~79 mV worst on the cans continuously, and K6 closes onto it 2.8 s after power-up (a click
in sensitive IEMs: the relay's purpose). Every other 100K-biased gain stage is AC-coupled after it. Fix: a large NP cap
(220-470 uF MUSE ES) in series with R132 / R136 (DC gain 1), and / or R129 / R133 10-22K. Spec §21, MG2 / MG11 don't
cover it.

**RV9 Master: the -V-loss comparator works outside its input range in exactly the fault it must catch.** U10B
(+ = GNDD, - = SENSE_N, V- = -VL via R8 from -VBUS). If the PSU's -V regulator drops out or a -V wire opens with +V
up, the console's quiescent current drives -VBUS positive until D2 / the PSU's D7 clamp it at ~+0.45 V, so -VL ends
at ~+0.5 V and U10B's + input (0 V) is 0.5 V below its own V-: past the LM393B's -0.3 V absolute maximum (TI's note:
the parasitic current "may cause output to be incorrect"). If it misreads, RAIL_OK floats high, the 2M2 / 2.2 uF timer
re-arms and all six relays close 2.8 s later with -V gone, putting the phones' DC fault (RV8) on the cans. `sim/mute.cir`
uses an ideal LM393 and models the trip, not the sustained state. The +V-loss case is safe (coil supply and base drive
both collapse). Fix (resistors only): feed pin 5 from a ~1.0 V tap (VREF6 - 51K / 10K - GNDD) and R53 51K -> 64.9K so
SENSE_N still crosses at -14.4 V (normal +0.34 V; -V lost 4.75 V against 1.0 V, every input in range). Moderate
confidence on the misread; the fix costs nothing either way.

**RV10 Jig: the wing-current test (load board J1, 17R per rail) exceeds the stub's PTC and the specified supply.** ~1 A
through F1 / F2 (MF-RX160/72, hold 1.6 A at 23 C, ~1.3 A at 40 C) plus the four strips' 0.42 A = 1.42 A; a real
12-strip wing adds up to 1.67 A. §1 specifies a supply of ">= 1 A per rail". Fix: run that test with the strips
unplugged, or fit MF-RX250/72 on the stub; specify >= 2 A per rail.

**Minor, no change proposed:** group R4 / C4 feed a -VL net nothing uses (one M25SI + 47 uF 63 V per board, kept for
symmetry with the strip; note it or drop them). Master jack board NC3MAV "G" pad (J3-J5) is unconnected; the panels
are anodised, so tie G to CHASSIS (three pads; open since the 2026-10-25 review) — DONE 2026-10-28 (project symbol
`XLR3_Shell` with pin G, master jack board and jig stub, nothing moved). Master AVG meter mode (JP1 / JP2
2-3) leaves the peak stage U30A / U37A open-loop (slews rail to rail at 2f; the reading is unaffected). KiCad's
`Diode:BAV99` symbol names its pins K/A/K; numbers and graphics are right, so D1 / D12-D22 and the group / master
BAV199s are correct as drawn: don't "fix" them from the pin names.

### Circuits checked and found correct
Every op-amp / comparator / DG413 / J112 / MMBT3906 / BCP53 / BZX84 / BAT54W / PMEG4010CEH / BAV99 / BAV199 / WP3VEGW /
DRV135UA (1 -VO, 2 -Sense, 3 Gnd, 4 VIN, 5 V-, 6 V+, 7 +Sense, 8 +VO) / G6K / LM2901 / LM1084 / 2N6505G / TL431AIDBZR
(SOT-23 1 K, 2 REF, 3 A: don't substitute a TL432-pinout part) pinout; DG413 truth table (switches 1 / 4 NO to the
bus, 2 / 3 NC to GNDA; PFL_ON high = SW1 / SW4 on); every unit powered and decoupled, spares tied off, no floating
input, no output on a connector or another output; polar caps oriented for their DC; the bus pinout identical on strip,
group, master, jig (1 / 3 / 5 / 7 / 19 / 28 NC, 17 MIX R, 18 MIX L, AUX1 = 24, AUX2 = 25); the jack links pin for pin;
PVA2 latched = 2-1 / 5-4 everywhere; pot tapers and CW sense; summing 4K7 / 22K, 100 uF NP + 47K; EQM1, CS1, CS2 / CS2b,
CS4 / CS4b / CS4c, CS6, CS7, CS10 values and wiring; re-inverter polarity (GCANCEL_BUF - SUM); the 100K keeper the
only GCANCEL tie; mute thresholds 13.6 / -14.4 V; meter ladder 2 dB +-0.2; PSU 16.96 V, crowbar 19.09 V nominal (19.2
typical with the TL431's reference current, 18.6-19.9 V worst: still safe), soft start 165 ms, every reservoir >= 35 V,
the -V rail's output / return sense; J3 matches the master's J1 pin for pin; every BOM MPN coherent with value /
footprint / voltage / dielectric on all nine boards (package size vs footprint checked by script: 0 mismatches).

## 2. Tooling findings (the checks relied on as proof)

Severity: FALSE-PASS = a check that passes when it should fail (demonstrated by mutating a copy of its input unless
marked traced); BUG = wrong result or silent loss; CLEANUP.

**RV11 (bundle of tool fixes, all small):**
1. FALSE-PASS `check_all.py`: it exports fresh netlists to a temp folder (`:34`) but `sim_console` (`sim_console.py:69-71`
   hard-codes `ROOT/*.net`), `check_links` (`:13`, cwd = ROOT), `ol.py:22` and `ol_multi.py` read the committed `.net`
   files; nothing compares the two. A regenerated schematic with a stale `.net` passes those checks for the old
   circuit. `netnames.renames()` also looks for `<board>_intended.json` beside the `.net` and silently returns `{}` for
   the temp exports (124 renames -> 0; sim_netlist happens not to need them today). Fix: a netlist-directory argument
   for sim_console / check_links / ol.py, the intended JSONs copied beside the temp exports, or one check that
   `ROOT/<b>.net` has the same pin-to-net partition as the fresh export (the script used for this review does that).
2. FALSE-PASS, demonstrated: swapping CN1 pins 22 / 23 (AUX3 / AUX4) in a copy of the strip netlist and its intended
   JSON (as a slip in `gen.py:84`'s `hdr` would produce) still gives verify 0 mismatches, sim_netlist 45/45,
   sim_console 38/38; opening the strip's AUX2 / AUX3 / AUX4 / AUX6 / SUB2 / SUB3 bus feeds also passes everything;
   MIX R open passes sim_netlist (MIX R only appears in "silent" checks). sim_netlist joins buses by name, never pin
   number, and models AUX2-5 not at all; sim_console tests only SUB1, AUX1, AUX5 and MIX positively; PFLDET (pin 29)
   is never simulated (`sim_console.py:174` sets the switcher from Python). The three hand-written `hdr` dicts
   (`gen.py:84`, `gen_group.py:31`, `gen_master.py:47`) agree today but nothing checks them. Fix: a header check (pin
   -> net name across strip / group / master / jig, NC and spares allowed); positive console checks on every bus
   (AUX2-4 at groups 2-4, AUX6 at the master, SUB2-4); the PFL switcher driven from the PFLDET net.
3. FALSE-PASS, demonstrated: `fab_out.is_known()` (`:37-45`) only requires every ref in a violation to match the
   board's regex, not that the items belong to ONE footprint: a hole clearance between J1 and J2, a mask bridge between
   J1 and J5, and on the PSU a silk-edge item on any D / U / Q (SOT-23s, SMA / SMC diodes, LEDs) all count as "known".
   Fix: require the same footprint on both items; PSU rule `^(U1|U3|Q2|Q4)$`.
4. BUG `check_fp.py:31`: one direction only (a pad with no pin is never flagged: U1 on SOIC-14 passes) and the pad
   regex needs quoted names (KiCad <= 7 library files are unquoted: 36 false problems on the strip here). Fix:
   `\(pad\s+"?([^"\s)]+)` and report pads without pins except `""` / MP / NPTH.
5. BUG `route_check.py:175-183`, demonstrated on a synthetic pcbnew-7 board: check 5 walks BOTH pads of every C0G cap
   to the nearest op-amp / DRV pin 2 / 3 / 5 / 6 on the same net. For the GNDA pad such pins exist (grounded + inputs
   U1.5, U2.5, U5.5, U12.5, U13.3 ...; DRV135 pin 3 is its ground), so once routed every C0G shunt to ground (C94 / C95,
   the KHN summers' 22p ...) raises "ERR 5 stability ... through 2 vias" and `fab_out.py` refuses to write. Fix: skip
   ground / quiet-class nets in check 5; also the op-amp lists have drifted (emc_check: OPA1612 / OPA1656 / TL072;
   netrules and route_check: `OPA`, `DRV13`, so the master's TL072 inputs never get HighZ, and DRV135 pins 2 / 3 / 5 /
   6 are Sense- / GND / V- / V+, not inputs).
6. FALSE-PASS (minor) `sim_console.py:421`: the DIM phones check is `.get('ph', 0) - .get('ph', 0)`; with the node
   missing it reports 0 dB and passes. Fix: fail on a missing value.
7. BUG, latent (traced): `placer.py:87`'s routed-board guard looks for segment / arc / via / zone only (copper
   `gr_poly` / `gr_rect` would be overwritten); `fab_out.py:79` detects 4 layers by the literal `(4 "In1.Cu"` (KiCad
   9+ numbering); `fab_out.py:74` lets a board through when route_check prints no summary. `schgen.write_intended`
   (`:503`) accepts a duplicate REF.PIN on the same net and no generator asserts unique refs (ERC / parity would
   probably catch it; a cheap assert in `P()` closes it).
8. `ol.py` (the `--full` check) builds its circuit by hand and takes only values from the netlist: still one PRESRC
   tap with a 1N4148, not the five CS1 taps; a wiring fault in the detector passes. Its docstring says "the deck
   follows the schematic". Mark it a values check or build the detector from the netlist as sim_netlist does.

Cleanup inside tools: `sim_console.py` `SPADE` (`:73`) unused, `n != 'NC'` (`:234`) dead; `master_lib.MPN` sets `'FB'`
twice (`:35`, `:44`) and overwrites `'DS'`; stale NRJ6HF / NC3MAH entries (`schgen.FP/MPN['JACKSW']`, `master_lib
MPN['JACK']`, `'XLR3'`), overridden so no output changes; `value()` / `law()` / the op-amp model copied in sim_netlist,
sim_console and ol.py (agree today); three CAP_MPN tables (gen.py, master_lib.py, gen_psu.py) and gen.py's 1206->0805
rewrite handles only `KEMET C1206C`; `placer.KLIB` ignores `KICAD_FOOTPRINT_DIR` (check_fp honours it); macOS
defaults in check_all, fab_out, netrules_test, live.sh; check_all skips verify silently when an intended JSON is
missing and ignores check_fp's exit code; pyflakes: unused imports (sim_netlist `math`, gen_group `json`, master_lib
`FADER_FP`, escape_plan / tub_fab `math`), unused locals (frags.py:47 / :490, schgen.py:189, placer.py:392,
schdraw.py:74); no broken import anywhere in tools/ or sim/.

Found sound (mutation-tested): verify.py (swapped pins, a dropped intended pin, a deleted node, a wired NC: all
caught; Net-( renames by exact pin set can't collide); sim decks have no `nc_` fallback nodes today and fail on a missing
ngspice result everywhere but t_dim; order_bom totals reconcile (9718 = 9718), every line has an MPN; schdraw's
wire check; the placer's placement-table and moves / turns guards; netrules_test and route_check_test fail through
their exit codes; a missing binary fails check_all.

## 3. Documentation: wrong facts (fix first)

- `test_jig_spec.md:135-136` mid-EQ acceptance targets are pre-EQM1 (684 / 2213 / 10471 and 148 / 479 / 2291 Hz; now
  598 / 2086 / 9930 and 165 / 521 / 2537, `docs/proposals/eqmid_proposal.md:57-62`): 684 vs 598 Hz sits at the +-15 % edge, a correct
  strip could fail test 4.1. `:125` "39 checks" (45); `:5` "strip v5.3"; §2 "5-pin XLR"; footer "0.3". `sim/mid_tuning.py:16-24`
  still models 430R / 13K / 4K7 and 670 Hz-10.5 kHz; CLAUDE.md:124 and `docs/build/panel_print.md:69-71` say the FREQ scales come
  from it (they come from `sim/review/eqmid/measure.py`; panel_print's numerals 0.7 / 1.6 / 2.2 / 4.8 / 10 and 0.15 /
  0.34 / 0.48 / 1.0 / 2.3 are the old ones, `panel_layout.py:146-147` prints 0.6 / 1.5 / 2.1 / 4.6 / 10 and 0.17 / 0.37 /
  0.52 / 1.1 / 2.5).
- `console_architecture.md` (authoritative): `:135` "10K for MIX and SUB" and the diagram at `:350` "-> 10K -> bus"
  (4K7, R26-R31); `:141` "220 uF + 47K" (100 uF NP); `:52` / `:178` "+-16 or +-17 V (decide)"; `:118` pins 1 / 3 / 5 / 7
  "free for mute groups / SIP" (reserved for SUB 5-8); `:234` / `:298` op-amp choices left open; `:296` omits U16; `:334`
  "strip spec 7.1" (the VCA option is §10); `:189-195` wing 1.96 A (2.07 A since RET1).
- `channel_strip_schematic_spec.md`: `:781` "2-layer board, AGND pour on the bottom" (4-layer; contradicts its own
  §16.3 at `:845`); `:783-784` "Wien networks around U5 / U6 / U7"; `:770` R1 / R2 still ERJ-P06J100V (M25SI since
  v5.3); `:756` "309 parts (v5.2)" (325; BOM 317 / 314 fitted); `:827` main board "273 + 6 holes"; `:798` D2 on
  `LED_THT:LED_D3.0mm` (own 3-lead footprint); `:311` signal-flow "OL detector (U4A, from PRESRC)" (five taps, U4 / U18);
  §2.2 lists U4 / C26 only (U17 / C98, U18 / C104 missing); `:529-533` KHN table pre-EQM1; `:521` "4K7 inputs"; footer
  `:1032` "Document version 4.6".
- `master_section_spec.md`: header v0.12, footer `:1088` 0.11; `:918` 3.09 / 4.33 A (3.31 / 4.54); §27 `:1045` / `:1049`
  MF-RX160/72 and "R1 / R2 0805 unchanged" (1206 M25SI); `:1062-1064` 4.24 / 4.33 A; `:1067` DRV134 (DRV135UA, 29 vs
  10 mentions); `:1076-1079` 579 / 1686 and 186 / 529; §7 "1 uF + 100 nF per DRV135 rail" (1 uF only, fine); §19 "47 uF
  + 1M" (33 uF); §23 "2 OPA1656" (4); §15 / §16 group counts pre-RET1 (9 OPA1612 + 4 OPA1656 per group; 16 jacks, 8 dual
  pots, 32 PVA2, 8 LEDs for four). `gen_master.py:27` block title "1.85 A hold" (2.5 A); title blocks `gen_master.py:326-327`
  rev 0.9 / "spec v0.9", `gen_group.py:146` 0.2, `gen.py:405` jack board 4.0.
- `docs/build/offboard_bom.md:65` NC7MD-LX "on the master panel" (plenum rear wall, TB3; CLAUDE.md:457 too); `:83` frame / PSU case
  "decision needed"; `:69-70` inlet / heatsink as "rule" (PC1-PC3 chose parts).
- `docs/build/sourcing.md:20` "every strip C0G on 1206" (six on 0805, its own `:13`); `:78-81` quantities 101 / 311 / 100 (109 / 319 /
  108 since RET1). `gen.py:19` has the same stale comment above the code that handles it.
- `psu_spec.md` §5 "2200 uF Panasonic FR" (BOM: Rubycon 35ZLH2200MEFC16X25); crowbar "+-1.5 %" (18.6-19.9 V worst, see
  above).
- N1 A/B plan contradicts itself: `test_jig_spec.md:18` and §4.2 build two OPA1656 strips, §1.1 (`:36`) swaps parts on one
  board; `order_bom.py` `EXTRA` still adds 16 "jig A/B" OPA1656 on top of phase 1's 8.
- `docs/proposals/gaps_proposal.md:89` cites `ol_fix.py` (doesn't exist); `docs/console_survey/*.md` link to `/private/tmp` scratch
  folders (5 places); `docs/studies/console_survey.md:5` and `docs/studies/emc_placement_study.md:6` headers say nothing is applied.
- CLAUDE.md: `:886` "pan centre -6 dB, LF -3 dB 1.1 Hz" undated under Verified (-2.7 dB, 2.3 Hz); `:456` worst corner
  4.0 A, `:614` 4.33 A / 108 / 113 C (4.54 A, ~111 / 116 C, `psu_spec.md:141-143`); `:448-449` O13 knobs (O14.5, KN1);
  `:21` group 7 pages (12), `:48` master 27 (29), `:51` "563 parts, 361 nets" (620 / 390), `:70-71` / `:948` jig spec
  v0.3 (0.9), `:103` 1316 links (1517), `:132` / `:157` only MF-RX160/72 listed, `:160` master spec v0.10 (0.12), `:198`
  "CS1-CS8 open" (CS8 / CS9 are), `:279` "CS4b not started", `:367` `--full` also runs ol_multi, `:424` open decisions
  (only the panel maker is), `:441` architecture v3.0 (3.2), `:895` / `:929` "spec 13.1" (no such section), `:900` /
  `:906` / `:914` resolved items under open, `:927` "Open: custom 12U frame" (FR1-FR3), `:941` / `:952-953` spec v0.5 /
  "3 mA OL LED" / "v4.1 placement".
- Stale generated outputs: `render/strip.json` / `render/group.json` are from v4.9 (30 / 28 parts missing: the 3D build is
  stale, `panels/` is not since no panel part moved); `docs/escape/*` and `docs/build/escape_plan.md` from v4.9 (no PK / OL_NN /
  OL_HOLD / GOUT / FPOST). README.md: spec v4.6 / v4.1, DRV134, "return n", PSU "0 DRC" (20 known silk items), 32
  checks (38), the v4.0 deck as example, a "copy step" that no longer exists, no mention of check_all / fab_out /
  order_bom / netrules / 4 layers.

The main source of drift: the worst-corner current chain (4.0 -> 4.24 -> 4.33 -> 4.38 -> 4.54 A) is restated in six
places in CLAUDE.md, master spec §24 / §27 / §29, psu_spec and the architecture; part / pin counts are copied into every
decision, changelog and proposal; DRV134 / DRV135UA naming.

## 4. Cleanup proposal

**RV12 Patches -> archive.** DONE 2026-10-28 (`archive/patches/`, 20 files with the clicks patch, every reference
updated). All 19 `*_proposal.patch` files are applied: cs7, cs11, cs11b, eqmid still reverse-apply
cleanly; cs1, cs2, cs2b, cs4, cs4b, cs4c, cs6, cs10, decouplers, film_np, hpf, input_nets, pan_buffer, stab_caps_e9b are
applied and superseded by later edits (84-100 % of their added lines present, no removed line left);
`archive/patches/stab_caps_proposal.patch` was re-implemented as `MOVES` (`place_strip.py:56`). `git mv *.patch archive/patches/`
(160 KB off the root); update the 19 CLAUDE.md pointers, each proposal's "The change" line and the docstrings of
`sim/review/hpf/trial_stab.py:2` / `trial_noise.py:2`. Risk: none (history keeps them). Optional second step: the ~40
proposal / review / study `.md` files into `docs/{proposals,reviews,studies}/` with the live specs left at the root;
that is a scripted rewrite of ~280 references in ~60 files (tools comments included) and `docs/build/escape_plan.md`'s relative
links to `docs/escape/`, so only worth doing in one commit with a link check. **Second step DONE 2026-11-09**: 57 files moved
(`docs/{proposals,reviews,studies,build}/`), the live specs and `routing_guide.md` left at the root; BOMs and order lists to `bom/`, schematic PDFs to `pdf/`.

**RV13 CLAUDE.md restructure.** DONE 2026-10-28: CLAUDE.md 106 KB -> ~21 KB (rules, state table, how to work, one line
per decision, open items); the Files section split verbatim into `docs/INDEX.md` (file map + proposals table) and
`docs/tooling.md`, the decisions in full into `docs/decisions.md`, "Verified so far" into `docs/verification_log.md`;
no separate history.md (the dated narratives live in INDEX.md's entries). As proposed: 100.9 KB / 965 lines today (Files 46.6 KB, Decisions 26.4, Verified 19.8, Open 2.4, Next
3.5): ~25k tokens loaded into every session, most of it superseded history. Proposed ~16 KB:
- Owner / scope / PCB rules (unchanged).
- Current state: ONE table of board / rev / parts / pins / outline / layers, the spec versions, power (typical and
  worst corner) and the last `check_all` result: the only place counts live (`check_all` could print the table).
- How to work: generate -> `check_all`; placement; `netrules`; `fab_out`; `order_bom`; fab drawings; 3D.
- Rules: generated files never hand-edited; proposal -> sign-off -> apply -> record; power down before plugging a
  module; no phantom.
- Decisions made: one line each, current value, date, doc; no superseded values or counts.
- Not done / open, Next steps: current items only.
Moved out, verbatim where possible: `docs/INDEX.md` (~12 KB: the file map plus a proposals table with ID, sign-off
date, version applied, patch state), `docs/tooling.md` (~15 KB: drawing system, placer, footprint links, 3D models,
netrules / route_check / fab_out), `docs/history.md` (~25 KB: the dated change narratives), `docs/verification_log.md`
(~20 KB: "Verified so far" and the per-change counts). Keep the headings "Decisions made", "Not done / open" and "Next
steps": `README.md:84,192` and `docs/build/sample_order.md:5,79` link to them.

**RV14 Tracked outputs and leftovers.** DONE 2026-10-28 as follows: `.gitattributes` marks the generated files
linguist-generated (not `-diff`: `git diff` on the boards is how placement changes are reviewed); the three unreferenced
sim/review scripts deleted; `tools/fly_render.py` kept and listed in CLAUDE.md; the four old decks labelled HISTORICAL;
`render/*.json` and the escape plan regenerated after the clicks batch; the PDFs stay tracked; `archive/channel_strip_v3.1.kicad_pcb`
stays (referenced).
- Keep tracked: `*.net`, `*_BOM.csv`, `*_intended.json`, `*_parts.json`, `*_sheets/` (tool inputs; the sims ran from
  them on a box without KiCad 10), `render/*.json` (`panel_layout.py:278` reads them), `goa-console.3dshapes/`, the
  deliverables `panels/`, `frame/`, `tub/`, `psu_case/`, `docs/escape/`, `order_*.csv`.
- Optional: gitignore `/*.pdf` (3.8 MB, rewritten in 5-8 of the last 50 commits) and `panels/*_numbers.pdf` (3.9 MB), at
  the cost of a schematic readable without KiCad; or a `.gitattributes` with `*.kicad_pcb *.kicad_sch *.net *.pdf *.step
  *.dxf -diff linguist-generated` (cheaper, keeps the files).
- Regenerate: `render/strip.json` / `render/group.json` (`export_3d.py`), the escape plan, the three title-block
  revisions then the PDFs; `sim/mid_tuning.py` to the EQM1 values or marked historical.
- Delete or list (done: the three deleted, fly_render listed, the archive board kept): `sim/review/group/table.py`, `sim/review/master/modeltest.py`, `sim/review/hpf/trial_lf.py` (the
  only unreferenced files under sim/review); `tools/fly_render.py` (undocumented); `archive/channel_strip_v3.1.kicad_pcb`
  (0.7 MB, in history; referenced from README.md:97, strip spec :843, `build_strip_pcb.sh:5`, CLAUDE.md:112). Old decks
  `sim/strip.cir`, `strip_v4.cir`, `delta_eq.cir`, `gain_stage.cir`: keep, label historical (cited by sim_netlist's
  docstring, strip spec §17, `docs/studies/delta_clone_comparison.md:97`). `ref/` (10.3 MB, Soundcraft copyright): fine while private.
- No other tracked file is unreferenced.

## 5. Suggested order

1. RV1 (PSU resistor rating) and RV2 (jig GCANCEL tap) before anything is ordered or built: both are cheap now.
2. RV7, RV8, RV9 (master / group clicks and the -V-loss detector) and RV3 / RV4 (strip direct out, gain-stage keeper)
   as one strip + group + master change: ~8 parts per master, 1-2 per group, 2 per strip; re-run the TI stability decks
   for U1B and U26, sim_netlist / sim_console targets, then re-place by `moves_only`.
3. RV11 tool fixes (1-6 first; they are what makes every later "61 / 61" believable), then re-run `check_all --full`.
4. The §3 wrong facts (test_jig_spec's EQ targets first), then RV12-RV14 as separate commits.
