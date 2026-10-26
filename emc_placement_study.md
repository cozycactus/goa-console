# EMC placement study (2026-10-26)

Ruslan routes the copper. Placement still decides most of the EMC result before any copper exists: where RF from a
cable is shunted, how far unfiltered lines run, which noisy and sensitive nodes routing has to pass next to each other,
and how large the supply and LED current loops are. This study checks the placed boards against the established rules
for audio boards and proposes changes. Nothing has been moved; the proposals are for sign-off.

## Method

- **The rules:** a research pass over Self (*Small Signal Audio Design*: track crosstalk, line inputs, signal
  switching, mixer subsystems, metering), Whitlock (AES 2012 seminar, JAES 1995), Muncy (pin-1 problem, JAES 1995),
  AES48, RaneNotes 151 / 165, Ott (*EMC Engineering*: grounding, power distribution, RF immunity, mixed-signal layout),
  TI SBOA128 (op-amp EMI rejection) and ADI AN-671 / MT-101. The distilled checklist is at the end.
  - **Read in the original:** RaneNotes 165 / 151, Whitlock's slides and Self's table of contents.
  - **From summaries:** AES48's wording, Ott's chapter numbers and Self's input-filter values. Check them before
    quoting.
- **The measurements:** `tools/emc_check.py` (KiCad Python, any placed board) classifies nets from the board's own
  pads:
  - **victims:** nets on op-amp inputs;
  - **aggressors:** LED, comparator-output, DG413-logic, relay-coil and transistor nets, and +5VL;
  - **entries:** connector signal nets.

  It reports pad-to-pad distances: entry run to the first filter part, the closest aggressor to each victim, aggressor
  nets spanning more than 60 mm, and bus supply pin to its filter. These are placement facts, not field strengths: they
  show where routing has no choice.
- **The trials:** layout variants placed into scratch files and measured the same way. The board files are unchanged.

## Already right

- **Bus side:** the bus ends sit at the header. The 4K7 / 22K summing resistors are 18–22 mm from their pins, and the
  DG413s 25–62 mm, at the header as decided.
- **Grounds:** the ground star is the spade, with NT1 (GNDA–GNDD) beside it (5 mm). GNDD is a separate logic ground
  with a single tie. CHASSIS exists only on the jack boards and reaches the panel through the standoffs; GNDA and
  CHASSIS meet only at the master star (G1 / G2).
- **The first RF shunt of the balanced input sits on the jack board, to CHASSIS:** C8 / C9, 100 pF C0G, the textbook
  topology.
- **Decouplers:** median 3.1 mm from their supply pin. Twelve of 35 are over 5 mm, mostly the DG413s' (C59–C61) and
  U16's (C92 / C93, 8.5 mm).
- **Group and jig:** the jig's closest aggressor is 18 mm from any op-amp input. The group's are its PFL LEDs (3.8 mm
  from a return follower's input), which switch only on a key press.

## Findings, by board

### Channel strip (×24): the board that matters most

1. **The signal / overload LED's switching lines cross the whole board.**
   - **Where the parts are:** MET1's LED switches and detector sit left of the fader (y 298–324), while D2 is fixed in
     the panel at (20.6, 50) and U4 at y 86.
   - **Resulting runs:** the switched LED anodes OL_A / SIG_A span 257 / 274 mm, and U4's comparator output OL_K
     237 mm.
   - **Where they end:** the anode lines end 4.3–4.6 mm from U16's + inputs (the 1M-biased balanced-input followers)
     and U1B's − input. That is the board's most sensitive spot.
   - **The rules:** Self ch. 2 / 18 (crosstalk scales with the victim's impedance and the parallel run; an LED's switching
     current must not share the audio return); Ott (partition by placement).
   - **The second aggressor:** U17A switches on every signal peak above −20 dBu, so its hold node is an audio-rate
     aggressor wherever it sits.
2. **The balanced input's RC sits far from its op-amp.** The 220R + 100 pF (R110 / R111, C94 / C95) that form the
   second RF pole are 11–16 mm from U16's + pins.
   - **The rules:** TI SBOA128 / ADI AN-671 put the input shunt cap at the pin with a local return, to stop RF
     rectification.
   - **The stability side:** the same caps are G3's stability fix (the 220R plus the OPA1656's input capacitance cost
     about 13° without them), so they belong at the pin on both counts.
3. **The balanced input runs 70–86 mm unfiltered on the main board.** IN_T / IN_R come off the ribbon at CN3 (y 133)
   and first meet a part at y 46–64.
   - **Why the rules flag it:** they want the RF filter at the entry (Whitlock slide 95; Ott RF immunity). Here the
     ribbon, then a long board run, carry whatever C8 / C9 didn't remove (above ~30 MHz they give limited attenuation)
     past half the strip.
   - **Fixed in place:** CN3 sits at y ≈ 131.5 since the sweepable HPF.
4. **The soft-mute JFETs sit far from the stage they shunt.** Q1 / Q2 (J112) are about 20 mm from U3B's + input, and
   R17 is 19.4 mm (the second-worst high-Z distance in the placer's report).
   - **The rule:** Self ch. 16, "Physical layout and offness": the JFET's source at the following stage's ground, its
     drain at the node. The mute's −87 dB depends on it.
5. **Unfiltered bus power runs 42–46 mm.** The bus ±V enters at header pins 30–34 (x 33, y 305–310), the 10R filters
   R1–R4 sit at x 3–7, y 341, and the reservoirs C1 / C3 at y 364 (bottom).
   - **The rule:** the entry filter and bulk caps go at the board entry (Ott power distribution).
6. **The direct-out lines run 65 mm and the insert send 50 mm** from CN3 to their output resistors. These nets are
   driven at low impedance and the build-outs belong at the drivers (stability), so this is acceptable. Route them as
   pairs with ground.

### Strip jack board (×24)

7. **The RF caps' return to the panel is long.** C8 / C9 sit 6.7 / 11.8 mm from J1's tip / ring pins and 10.2 mm from
   its sleeve pad. The sleeve's only route to the panel is 24 mm of trace to the standoffs H1 / H2.
   - **Why it matters:** the NJ6FD-V housing is plastic, so nothing else bonds the sleeve. Brown measured about 2 Ω at
     60 MHz for 1 cm of path.
   - **The rules:** Muncy / AES48 / RaneNote 165 bond the shield to the enclosure at the point of entry, with the RF
     caps between the pins and that bond.

### Group (×4)

8. **The returns' inputs run long.** RET1 moved the links to y ≈ 190, so return 1's inputs now run 48–85 mm from the
   link to their first part (return 2 runs 8–42 mm). The insert send runs 252 mm, but it is driven at low impedance.
   - **What the spec already says:** master spec §0 holds that the group's and master's RF caps stay on the main boards
     "unless the jig shows RF pickup on the ribbon". That still applies; the strip's jack-board C8 / C9 pattern is
     ready if needed.

### Master (×1)

9. **The rude-solo flasher and its LEDs run long.** The flasher's hold line FL_HOLD (a 0.5 s toggle while soloed) runs
   112 mm, and the panel-LED anode lines of D12 / D13 run 143 mm. PFL_ON_RAW (a comparator output) passes 2.3 mm from
   the phones op-amp's input.
   - **Unavoidable or harmless:** CRS_L / R sit 1.3 mm from the DG413's own logic pin (the chip's pinout). The meter
     detectors sit next to their LED ladders, outside the audio path.

## Proposals

Each item below is placement only (no netlist change) unless it says **circuit**.

- **E1 (strip): LED switches beside D2; base resistors at the comparators.**
  - **Moves:** Q3 / Q4 / Q5 with R117, R123, R124 and R125 go to the bottom side by D2 (trial: they fit at x 30–37,
    y 44–76). R116 goes beside U4 and R122 beside U17.
  - **Effect:** the LED anode lines drop from about 260 mm to a few mm, and the remaining long lines (OL_K, SIG_K) are
    fed through 47K at their source, so their edges are slow. U17 stays where it is.
  - **Why not move U17 too:** trials that also moved it put it over U1 / U16 or the HPF integrator U15 (1.1 mm through
    the board), which is worse.
- **E2 (strip): the input followers' RC at the pins.** R110 / R111 and C94 / C95 go within 3 mm of U16's pins 3 / 5,
  and C94 / C95's ground beside U16's decoupler ground (11–16 mm today). Also, where it fits, keep the U16 group's
  + input pads at least 8 mm from D2's leads (4.3 mm today).
- **E3 (strip): the soft-mute JFETs at U3B.** Q1 / Q2 and R16 / R17 go within about 5 mm of U3B's + input, the JFET
  sources at U3's ground (about 20 mm today).
- **E4 (strip, and the group the same way): the supply filter at the header.** R1–R4 go beside the header's power pins,
  and C1 / C3 / C5 / C6 on the bottom side under them. Unfiltered bus power then runs a few mm, not 42–46 mm (the
  group's runs 26–30 mm).
- **E5 (jack board): the RF caps and a chassis bond at J1.**
  - **The caps:** C8 / C9 within 3 mm of J1's tip / ring pins and its sleeve pad.
  - **The bond:** a chassis standoff beside J1's sleeve, by moving H1 there (24 mm today). Check that the jack pads
    leave room.
- **E6 (strip, circuit): slow LED edges.** 10 nF from base to emitter on Q3 and Q4 (2 parts per strip), so with the 47K
  base resistors the LED current ramps over about 0.5 ms instead of switching in a microsecond. Together with
  `met1_ret1_review.md` P1 (1K in each hold stage's discharge), no comparator in MET1 has a fast edge on a long line.
- **E7 (strip / group / master, circuit, optional): ferrites at the jack.** A ferrite bead in series with tip and ring
  on the jack board, between the jack and the link, with C8 / C9 on the jack side. That makes the entry filter a real
  two-pole filter at the connector. Hold it until the jig shows RF pickup on the ribbon, as master spec §0 already says
  for the RF caps.
- **E8 (master): the flasher and PFL logic.**
  - **The flasher:** move the rude-solo flasher (U22's flasher half, FL_HOLD's parts) next to its LED, so the 0.5 s
    toggle doesn't cross the board.
  - **PFL_ON_RAW:** move it, or the phones input network, apart by at least 8 mm.

E1–E5 and E8 change only placement: the generators' zones and `near()` records. They need a re-placement and the usual
parity DRC; no schematic changes. E6 and E7 add parts.

## For the routing (Ruslan's)

Rules that only routing can keep, from the same sources:
- **IN_T / IN_R:** a pair from CN3 to U16, with ground on both sides; the same on the ribbon (conductors 1–2, ground at
  3).
- **LED and logic lines:** OL_K / SIG_K / LED anodes, DG413 IN lines (RTE_*), PVA2 pole-B lines and +5VL away from the
  op-amp input nets, the KHN integrator nodes and the pot-wiper nets. No parallel runs; cross at right angles.
- **LED currents:** each returns on GNDD to its own driver; no LED return through GNDA. NT1 is the only GNDA–GNDD
  connection.
- **CHASSIS:** jack board only, short and wide, sleeve to standoff. Never onto the main board.
- **Decoupling:** each decoupler's ground via goes straight down at the cap; the loop is what counts, not the
  capacitance.

## Checklist (from the research)

1. **RF shunt at the connector, to chassis,** within a few mm of the pin (RaneNote 165, Whitlock, AES48).
2. **Series element on the connector side, shunt cap after it,** both before the op-amp (Self, Line Inputs).
3. **Matched shunt caps on a balanced input:** C0G 1–2 %; a differential cap at least 10× the common-mode caps if one
   is used (ADI AN-671).
4. **Shield bonded at the point of entry,** never through a trace the circuit shares: the pin-1 problem (Muncy, AES48).
5. **One signal-ground-to-chassis tie per unit,** carrying no return current (RaneNote 151).
6. **Decoupling loop area** minimised at the supply pin (ADI MT-101, Ott).
7. **Entry filter and bulk caps at the board's supply entry** (Ott).
8. **Partition by placement with one reference;** a split ground only with no signal crossing and no return current
   through the tie (Ott; disputed in converter notes).
9. **LED and indicator currents in their own tight loop on the logic ground** (Self, Metering).
10. **Analog-switch control lines away from high-impedance nodes:** control feedthrough (Self, Signal Switching).
11. **A shunt JFET's offness** needs its source at the next stage's ground (Self, Signal Switching).
12. **Crosstalk scales with victim impedance and parallel length;** keep high-impedance nodes short and apart (Self,
    PCB crosstalk).
13. **Input shunt cap at the op-amp pin,** with the local return, against RF rectification (TI SBOA128, ADI AN-671).
14. **Summing buses:** the high-impedance stub short at the header; ground conductors between buses where the pinout
    allows (Self, Mixer Subsystems).

## Sign-off

Signed off by Ruslan on 2026-10-26: E1–E5 and E8 (placement only). E6 and E7 are left for later.

- [x] **E1** LED switches beside D2 (bottom side); base resistors at their comparators.
- [x] **E2** Input followers' 220R / 100 pF at U16's pins; U16's inputs at least 8 mm from D2 where possible.
- [x] **E3** Soft-mute JFETs at U3B's input.
- [x] **E4** Supply entry filters at the header (strip and group).
- [x] **E5** Jack board: C8 / C9 at J1; a chassis standoff beside J1's sleeve.
- [ ] **E6** 10 nF base caps on Q3 / Q4 (circuit). Later.
- [ ] **E7** Ferrites at the jack, only if the jig shows RF pickup (circuit, deferred).
- [x] **E8** Master: flasher next to its LED; PFL_ON_RAW away from the phones input.

## Applied (2026-10-26): E1–E5, E8

Placement only: zones, `near()` records and fixed positions in `tools/place_strip.py`, `place_group.py` and
`place_master.py`. No schematic changes. Measured with `tools/emc_check.py` before and after.

| Item | Measure | Before | After |
|---|---|---|---|
| E1 strip | LED anode lines OL_A / SIG_A, U4 output OL_K (pad span) | 257 / 274 / 237 mm | 19 / 8 / 8 mm |
| E2 strip | U16's 100 pF to its + pins (C94 / C95) | 10.9 / 15.5 mm | 2.7 / 3.5 mm |
| E3 strip | Soft-mute JFET drain (Q2) to U3B's + input | about 20 mm | 1.3 mm |
| E4 strip | Bus ±V pin to its 10R filter | 46 / 42 mm | 5.5 / 8.0 mm |
| E4 group | the same | 30 / 26 mm | 16 / 15 mm |
| E5 jack board | C8 / C9 signal pad to J1's tip / ring; chassis pad to J1's sleeve | 6.7 / 11.8; 10.2 / 10.2 mm | 3.2 / 4.2; 3.2 / 4.1 mm |
| E8 master | Flasher hold line FL_HOLD (comparator output) | 112 mm | short (D18 beside U22) |
| E8 master | PFL detect output to the phones amplifier's inputs | 2.3 mm | no longer among the closest pairs |

**E1**
- **Moves:** the LED switches (Q3–Q5, R117, R123–R125) went to the bottom side beside D2. R116 sits at U4, and R122 at
  U17.
- **The one long line left:** SIG_B (U17 → Q4, 259 mm), now fed through 47K at the comparator rather than straight from
  its pin.
- **U17 stays left of the fader:** trials that moved it put it over U1 / U16 or the HPF integrator U15.

**E2**
- **Moves:** R110 / R111 / C94 / C95 went to the bottom, under U16's pins.
- **Partly met:** U16 itself couldn't get 8 mm from D2's leads (the pot and key pins fill every spot nearby), so it stays
  4.3 mm away. The long switching lines that ended there are gone (E1).

**E3:** Q1 / Q2 / R16 / R17 / R42 / C28 went to the bottom, under U3B.

**E4**
- **Strip:** R1–R4 sit beside the header's power pins, and C1 / C3 / C5 / C6 on the bottom under them.
- **Group:** the same. The summers' column fills the space right beside its header, hence 15 mm.

**E5**
- **Moves:** C8 / C9 sit on the bottom between J1's tip / ring and sleeve pads.
- **Not possible:** a standoff closer to J1's sleeve. The jack courtyards leave no M3 spot nearer than H1 (24 mm), so
  the CHASSIS copper from the sleeve to H1 / H2 must be wide, on both layers (routing note).

**E8**
- **Flasher:** its hold diode D18 sits beside U22, so the long run to the flasher is behind the diode, on its slow RC
  node.
- **PFL detect:** it has its own zone beside the PFL switcher, away from the phones amplifier.
- **One new near pair:** FL_HOLD is now 5.4 mm from U18B's + input. Acceptable: the flasher only toggles while
  something is soloed.

**A placer change made on the way.** The strip's packer re-shuffled every IC after any change near the top: E2–E3 at
first moved 163 parts and starved the HPF. So the upper board's op-amps (U1, U4–U7, U12–U16) are now fixed where the
reviewed placement had them, and their parts pack around them. `placer.py` now lets a fixed part stay listed in its
zone, where it anchors its parts.

**Checks:**
- **Moved:** 109 parts on the strip, 28 on the group, 64 on the master.
- **DRC:** strip, group and master have 0 DRC violations and 0 parity issues; the jack boards show only the NJ6FD-V's
  own items.
- **Links:** every symbol is linked.
- **Panels:** pixel-identical.

**Placer reports:**

| Board | Decouplers (median / max / over 5 mm) | High-Z inputs over 6 mm |
|---|---|---|
| Strip | 3.1 / 10.0 / 14 (was 12) | 28 (was 30), apart from the intended SIG_B |
| Group | unchanged | unchanged |
| Master | 3.1 / 11.5 / 27 (was 26) | FL_N via D18 is the intended long one |

The two extra strip decouplers over 5 mm are DG413 decouplers next to the new supply-filter zone.

**Stability:** the master's sensitive cases were re-run on TI's models after E8, with `master_len.json` re-measured from
the new placement (`run_each.py` p100, p075 / p100 / p075_pfl placed, p075_out47; `run_phv.py` both channels). The
results are unchanged: worst 47.7° (U21A at the pot top, as before), placed traces 48.6–54.1°, +47 pF 49.1°, phones
76.0°. The strip's and group's changes move no op-amp's feedback network: E2 and E3 bring the strip's input RC and mute
closer to their pins, and E4 moves only supply filters.
