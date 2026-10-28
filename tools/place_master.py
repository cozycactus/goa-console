"""Component placement for the master module (M1, 16 HP): main board + jack board, placement only.
  KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3
  $KPY tools/place_master.py      # -> master.kicad_pcb (78.6 x 331.5 mm), master_jack_board.kicad_pcb (78.6 x 111.5 mm)
16 HP x 12U panel (80.9 mm) in the strip's frame (placer.py): y = 0 is 11 mm below the panel's top edge, panel
x = board x + 1.15, pot columns at the strips' 8.84 / 29.16 and 49.48 / 69.80 (8 HP further). The dual master fader
sits on the strips' slot line (y 372, x 39.3) between the two 20-LED meters; both wing bus headers sit at the
strips' header height, pin 1 at the bottom end like every strip, so each wing's ribbon runs straight.
Jack board (~24 mm under the panel): MAIN L / R / MONO XLRs (NC3MAV) in a column, 9 NJ6FD-V in two columns,
2x20 link along its bottom edge; the main board's 2x20 sits along its top edge, pin 1 at the same end.
Zones follow gen_master.py's blocks (master_parts.json)."""
import collections, json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from placer import place, PROJ, XL, XR, pot, sw, led, jack, BUS
from verify import sexp, field
import netnames

W = 78.6                                      # 16 HP board: 2 x 40.64 mm pitch
H8 = 40.64                                    # second 8 HP half: columns at XL + H8, XR + H8
JACK_Y1, MAIN_Y0, MAIN_Y1 = 111.5, 112.5, 444.0
XF = 39.3                                     # fader slot and module centre line

# ================================================================ jack board
xlr = lambda x, y: (x - 3.81, y, 0, 'F')      # NC3MAV: barrel centre at (3.81, 0) from pin 1
JC = (41.0, 60.0)                             # jack columns
JACK_FIX = {'J3': xlr(16, 15), 'J4': xlr(16, 47), 'J5': xlr(16, 79),                 # MAIN L / MAIN R / MONO
            'J1': jack(JC[0], 12), 'J2': jack(JC[1], 12),                            # MIX L / R insert
            'J10': jack(JC[0], 32), 'J11': jack(JC[1], 32),                          # C/ROOM L / R out
            'J8': jack(JC[0], 52), 'J9': jack(JC[1], 52),                            # EXT L / R in
            'J6': jack(JC[0], 72), 'J7': jack(JC[1], 72),                            # AUX 5 / 6 out
            'J12': jack(JC[0], 92),                                                  # PHONES
            'CN1': (15.0, 104.5, 270, 'B')}           # 2x20 link, bottom, pins x 15-63.3, y 104.5 / 107.0, pin 1 left
JACK_HOLES = []                               # plated M3 standoff holes on CHASSIS (ground_study.md G2): bond the panel
JACK_FIX.update({'H1': (73.3, 15, 0, 'F'), 'H2': (73.3, 90, 0, 'F'), 'H3': (8, 97, 0, 'F')})
JACK_NOTES = ((15, 'MAIN L (XLR) | MIX L INS | MIX R INS'), (32, 'C/ROOM L | R'), (47, 'MAIN R (XLR)'),
              (52, 'EXT L | R'), (72, 'AUX 5 | AUX 6 OUT'), (79, 'MONO (XLR)'), (92, 'PHONES'),
              (105, 'link CN1 (bottom), pin 1 left'))
place(os.path.join(PROJ, 'master_jack_board.net'), os.path.join(PROJ, 'master_jack_board.kicad_pcb'),
      dict(board=(0, 0, W, JACK_Y1), fix=JACK_FIX, holes=JACK_HOLES, zones=[], notes=JACK_NOTES,
           hole_value='M3 standoff = jack body height (~24 mm)'))

# ================================================================ main board
d = json.load(open(os.path.join(PROJ, 'master_parts.json')))
seen, B = set(), {}
for title, refs in d['blocks']:                 # a package shared by two blocks stays in the first
    B[re.split(r'\s*[(:]|  ', title)[0].strip()] = [r for r in refs if not (r in seen or seen.add(r))]
# Beside-parts come from the generator (master_parts.json 'near': decouplers, summing-junction parts, DRV134 caps,
# relay coil parts, LM2901s at the first LED they drive, ...), so a regeneration that renumbers parts needs no edits here
NEAR = dict(d['near'])
net = sexp(open(os.path.join(PROJ, 'master.net')).read())
comps = next(c for c in net[1:] if isinstance(c, list) and c[0] == 'components')
FPN = {field(c, 'ref'): field(c, 'footprint') for c in comps[1:]}
VAL = {field(c, 'ref'): field(c, 'value') for c in comps[1:]}
ON = {field(n, 'name').lstrip('/'): {field(x, 'ref') for x in n[1:] if isinstance(x, list) and x[0] == 'node'}
      for n in next(c for c in net[1:] if isinstance(c, list) and c[0] == 'nets')[1:]}
_rn = netnames.renames(os.path.join(PROJ, 'master.net'))    # a drawn schematic leaves nets inside a drawing unlabelled
ON = {_rn.get(k, k): v for k, v in ON.items()}
num = lambda r: int(re.sub(r'\D', '', r))
byval = lambda v: next(r for r, x in VAL.items() if x == v)

# meter LEDs in ladder order (-20 dB first): the LEDs of each meter block, by the dB in their value
meter_leds = lambda blk: sorted((r for r in B[blk] if 'LED_' in FPN[r]), key=lambda r: int(VAL[r].split()[1]))
mL, mR = meter_leds('METER L'), meter_leds('METER R')
FIX = {
 'RV2': pot(XL, 134), 'RV3': pot(XR, 134, right=True), 'RV5': pot(59.3, 134, dual=True),           # AUX 5 | AUX 6 || C/ROOM
 'SW1': sw(XR - 22, 156), byval('Aux 5 AFL red'): led(XR - 13.8, 156),                             # AFL 5 | 6
 'SW2': sw(XR - 4, 156), byval('Aux 6 AFL red'): led(XR + 4.2, 156),
 'RV6': pot(XL + H8, 156, dual=True), 'RV4': pot(XR + H8, 156, right=True),                        # || PHONES | SOLO
 byval('Power green'): led(19, 178), 'SW3': sw(XL + H8, 178),                                      # POWER || EXT
 byval('PFL ACTIVE red 5mm'): led(XR + H8, 178),                                                   # | PFL ACTIVE
 'RV1': (XF - 1.9, 372 + 63.75, 270, 'F'),                                                         # dual master fader
 'CN2': (5.5, BUS[1], 180, 'B'),              # left-wing bus header: as a strip's, 1.4 mm in so its pin-1 mark stays on
 'CN3': (72.0, BUS[1], 180, 'B'),             # right-wing bus header (pin-1 mark inboard)
 'CN5': (15.0, 118.0, 270, 'B'),              # 2x20 link to the jack board, pin 1 left, pin-1 mark towards the edge
 # power entry at y 186-236, between the panel controls and the summers: J1 (bottom, centred), the wing PTCs beside
 # it, and the star point (the M4 stud with the four net ties around it). Each wing's fused supply then runs along its
 # own board edge (keep-outs x < 4 and x > 74.6, y 186-299) to its header's power pins, never past the summers
 'J1': (XF + 15.24, 197.0, 0, 'B'),           # 7-way terminal, pins 54.5 .. 24.1
 'CN1': (XF, 214.0, 0, 'F'),                  # M4 star stud
 'NT1': (XF - 6.5, 214.0, 180, 'F'), 'NT2': (XF + 6.5, 214.0, 0, 'F'),        # GNDA-GNDD | GNDA-GNDM, GNDA pads
 'NT3': (XF, 214.0 - 6.5, 90, 'F'), 'NT4': (XF, 214.0 + 6.5, 270, 'F'),       # GNDA-PHONESGND | GNDA-CHASSIS  to the stud
 # wing PTCs (bottom), fixed. -V: MF-RX185/72 (hpf_proposal.md H4): F2 courtyard x 4.05-19.73, F4 0.7 mm right of the
 # 160's spot, clear of J1 (58.36-74.04). +V: MF-RX250/72 (wing_power_proposal.md W2, 10.16 mm leads, body 17.84):
 # spots searched clear of every other part with the packer's 0.3 mm gap and the keep-outs, so the rest of the board
 # places as before. F1 in its row, 1.2 mm higher (D5's lead at y 189.92): pads 18.33 / 8.17, courtyard x 4.1-22.4.
 # F3 found no spot in its row (R121 / R123 / R122 above, the edge channel) and stands vertical by the right edge,
 # pads (69.5, 234.17) / (69.5, 244.33), courtyard x 67.6-71.4, on the wing supply's way down to CN3
 'F1': (18.33, 186.75, 0, 'B'), 'F2': (14.435, 192.445, 0, 'B'),
 'F3': (69.5, 234.17, 270, 'B'), 'F4': (68.74, 192.445, 0, 'B'),
}
for k, (l, r) in enumerate(zip(mL, mR)):      # D28..D49 / D56..D77 in ladder order: -20 dB at the bottom, +18 dB at the top
    FIX[l] = led(18.0, 422.0 - 5.0 * k); FIX[r] = led(60.6, 422.0 - 5.0 * k)
HOLES = [(44, 134), (8.5, 228), (70.1, 228), (26, 318), (52.6, 318), (24, 436), (54.4, 436)]   # clear of the edge channels

TALL = {r for r, f in FPN.items() if any(k in f for k in ('CP_Radial', 'C_Rect', 'Fuse_', 'TerminalBlock',
                                                         'Potentiometer_Bourns_3296', 'PinHeader'))}  # bottom: 11.5 mm gap
dia = lambda r: float(FPN[r].split('_D')[1].split('mm')[0]) if 'CP_Radial' in FPN[r] else 0.0
def take(*names, only=None, drop=()):
    out = [r for n in names for r in B[n] if r not in FIX and r not in TALL and r not in drop]
    return [r for r in out if r in only] if only else out
def tall(*names): return sorted(TALL & {r for n in names for r in B[n]}, key=num)
# post-amps: both in one OPA1612 (gen_master.py new_package), across the 5.9 mm strip under the fader's wiper end:
# pins 1-3 (L) face the L wiper, 5-7 (R) the R wiper; the 2.2u wiper couplers at the fader pins
FADER_BLOCK = take('MASTER FADER')
COUPLE = [r for r in FADER_BLOCK if VAL[r] == '2.2u']
POST_U = [r for r in FADER_BLOCK if r.startswith('U')]
FIX[POST_U[0]] = (XF, 440.75, 0, 'F')
POST = COUPLE + [r for r in FADER_BLOCK if r not in COUPLE + POST_U]
NEAR.update({c: 'RV1' for c in COUPLE})
NEAR.update({r: POST_U[0] for r in POST if r not in COUPLE and r not in NEAR})
NETS_OF = collections.defaultdict(set)
for n, rs in ON.items():
    for r in rs: NETS_OF[r].add(n)
def caps_first(r):
    """Beside-part order (first = closest to the pins): decouplers, summing-junction parts, other caps, the rest."""
    if r.startswith('C') and VAL[r].split()[0] in ('100n', '1u', '10u'): rank = 0
    elif any(n.endswith('_VE') for n in NETS_OF[r]): rank = 1
    else: rank = 2 if r.startswith('C') else 3
    return rank, num(r)
beside = lambda a: sorted((r for r, x in NEAR.items() if x == a and r not in TALL), key=caps_first)
def summer_group(bus, out):
    """Summing amp package (sum + re-inverter), its decouplers and junction parts, the re-inverter's network."""
    u = next(r for r in ON[bus + '_VE'] if r.startswith('U'))
    rest = sorted((ON[out + '_DN'] | ON[out + '_DP']) - {u} - set(beside(u)), key=caps_first)
    return [u] + beside(u) + rest
SUMMER5, SUMMER6, SUMMERP = summer_group('AUX5', 'A5_MIX'), summer_group('AUX6', 'A6_MIX'), summer_group('PFL', 'PFL_MIX')
# balanced outputs: each DRV134 with its 1u caps, then its mute relay with the coil resistor and diode; then the phones
# relay (no driver of its own)
# the EXT receivers' followers (OPA1656 in the EXT block) and the parts recorded beside them
EXTF = [r for r in B['EXT INPUT'] if VAL.get(r) == 'OPA1656']
EXTF += [r for r, a in NEAR.items() if a in EXTF and r in B['EXT INPUT']]
OUTS = []
for u in sorted((r for r in VAL if VAL[r] in ('DRV134', 'DRV135')), key=num):
    OUTS += [u] + [r for r in beside(u) if not r.startswith('K')]
    for k in (r for r in beside(u) if r.startswith('K')): OUTS += [k] + beside(k)
for k in sorted((r for r in VAL if VAL[r].startswith('G6K') and r not in NEAR), key=num): OUTS += [k] + beside(k)
# E8 (emc_placement_study.md): the flasher's hold diode beside the comparator that drives it, so the long run to the
# flasher is behind the diode (its slow RC node), not the comparator's output
PFLD_U = next(r for r in B['PFL DETECT'] if r.startswith('U'))
FL_D = next(r for r in B['RUDE SOLO'] if r.startswith('D') and 'FL_HOLD' in NETS_OF[r])
NEAR[FL_D] = PFLD_U
EL, ER = 4.0, W - 4.0                          # edge channels for the wing supplies (y 186 to the headers)
PWR_TALL = tall('POWER ENTRY', 'DISTRIBUTION')
ZONES = [
 # power entry first, so it gets its area around J1 and the star stud
 ('rail reservoirs beside J1 (bottom)', (EL, 186, ER, 236), sorted((r for r in PWR_TALL if r[0] == 'C'), key=lambda r: (-dia(r), num(r))), 'B'),
 # between the PTC columns (x 4-22 / 56.6-74.6 on the bottom): a phones fault heats the VP 2R2s, and a warm PTC
 # holds less (master_group_review.md MG11)
 ('SS54 clamps, branch resistors (top, at J1, clear of the PTCs)', (24, 186, W - 24, 236), take('POWER ENTRY', 'DISTRIBUTION'), 'F'),
 # bottom side: electrolytics, trimmers
 ('balanced-out, monitor and aux coupling caps (bottom)', (0.3, MAIN_Y0, W - 0.3, 186),
  tall('MAIN OUTPUTS', 'AUX MASTER 5', 'AUX MASTER 6', 'EXT INPUT', 'PFL / AFL', 'PFL SWITCHER', 'CONTROL ROOM',
       'HEADPHONES', 'POWER-ON MUTE', 'PFL DETECT', 'RUDE SOLO'), 'B'),
 ('mix coupling (bottom)', (11, 296, 68, 444), tall('MIX L', 'MIX R', 'MASTER FADER'), 'B'),
 ('meter trims + remote meter header (bottom)', (0.3, 300, W - 0.3, 444), tall('METER L', 'METER R', 'REMOTE METER HEADER'), 'B'),
 # top side
 ('balanced outputs + mute relays (towards the jack-board link)', (EL, MAIN_Y0, ER, 236), OUTS, 'F'),
 # the summers first: the monitoring and aux zones overlap their area and would otherwise take it
 ('GC buffer, summers, re-inverters, insert returns, mono (between the wing headers)', (11, 236, 68, 306),
  take('GROUND CANCEL BUFFER', 'MIX L', 'MIX R', 'MONO') + SUMMER5 + SUMMER6 + SUMMERP, 'F'),
 # E8: PFL detect beside the PFL switcher it drives, at least 8 mm from the phones amplifier's inputs
 ('PFL detect, beside the PFL switcher (E8)', (44, 266, ER, 306), take('PFL DETECT'), 'F'),
 ('monitoring: EXT, PFL switcher, C/ROOM, phones', (EL, MAIN_Y0, ER, 306),
  take('EXT INPUT', 'PFL SWITCHER', 'CONTROL ROOM', 'HEADPHONES', drop=OUTS + EXTF), 'F'),
 ('aux 5-6 level buffers, AFL; solo level', (EL, MAIN_Y0, ER, 306),
  take('AUX MASTER 5', 'AUX MASTER 6', 'PFL / AFL', drop=OUTS + SUMMER5 + SUMMER6 + SUMMERP), 'F'),
 ('rude-solo flasher, power-on mute', (EL, 160, ER, 306), take('RUDE SOLO', 'POWER-ON MUTE'), 'F'),
 # EXT receivers' input followers (ground_study.md G3b), added 2026-10-25: placed last, into what the zones above
 # leave, so the mute and aux 5-6 networks keep their places; their parts still follow U43 / U44 (attach)
 ('EXT input followers', (EL, MAIN_Y0, ER, 306), take('EXT INPUT', only=EXTF), 'F'),
 ('post-amps L + R around U5 and wiper coupling (fader wiper end)', (19, 424.5, 60, 444), POST, 'F'),
 ('meter L', (0.3, 300, 31.2, 444), take('METER L'), 'F'),
 ('meter R', (47.4, 300, W - 0.3, 444), take('METER R'), 'F'),
]
NOTES = ((134, 'AUX 5 | AUX 6 || C/ROOM'), (156, 'AFL 5 | AFL 6 || PHONES | SOLO'), (178, 'POWER | DIM || EXT | PFL ACTIVE'),
         (197, 'POWER IN J1 (bottom), star stud CN1 + NT1-4 at y 214; wing supplies along the board edges'),
         (305, 'BUS HEADERS: left wing CN2, right wing CN3 (bottom)'), (372, 'MASTER FADER 100 mm, meters L | R'),
         (118, 'LINK CN5 (bottom) to the jack board, pin 1 left'))
# E9 (stab_caps_proposal.md): the C0G stability caps at the op-amp pins they stabilise (the packer had left them
# 6.6-13 mm away). Moved after packing (placer `moves`), so no other part re-packs into the slots they leave;
# bottom-side rotations are before the flip (board angle = 180 - rot)
MOVES = {'C37': (41.775, 440.635, 270, 'B'), 'C83': (9.22, 149.65, 180, 'F'), 'C69': (5.27, 144.36, 270, 'B'),
         'C33': (36.825, 439.365, 270, 'B'), 'C82': (7.72, 145.63, 270, 'B'), 'C70': (5.27, 147.88, 270, 'B'),
         'C36': (39.025, 442.655, 0, 'B'), 'C153': (12.72, 282.63, 270, 'B'), 'C32': (35.575, 442.135, 0, 'B'),
         'C94': (56.77, 144.38, 90, 'B'), 'C174': (74.12, 353.38, 270, 'B'), 'C146': (9.27, 282.61, 270, 'B'),
         'C91': (9.27, 269.88, 0, 'B')}
# E10 (input_nets_proposal.md): one SMD part per long high-impedance op-amp input net moved so the net shrinks by
# >= 5 mm without its other net growing more than that (placer `moves`)
MOVES.update({'R38': (47.525, 438.635, 0, 'F'), 'R33': (30.325, 441.615, 180, 'B')})
# E11 (decouplers_proposal.md): decouplers more than 5.5 mm from their supply pin moved to it, most on the bottom
# under the pin (placer `moves`); not C144 / C145, the LME49600's through-hole 10 uF: no spot nearer clears U27's pads
MOVES.update({'C193': (56.77, 147.9, 90, 'B'), 'C180': (68.56, 414.975, 270, 'B'),
              'C150': (57.595, 167.695, 270, 'B'), 'C116': (58.22, 280.61, 270, 'B'),
              'C58': (57.865, 180.135, 180, 'B'), 'C31': (38.825, 439.905, 270, 'B'),
              'C74': (12.72, 116.15, 270, 'F')})
# untangle_proposal.md: two-pad parts turned in place (degrees) so their ratsnest crosses less, measured with
# tools/ratsnest.py (placer `turns`, after packing and the moves)
TURNS = {'C160': 180, 'D7': 180, 'R9': 90, 'R27': 270, 'R29': 180, 'R44': 270, 'R47': 180, 'R50': 180, 'R59': 180,
         'R62': 180, 'R63': 180, 'R65': 180, 'R67': 180, 'R70': 180, 'R72': 270, 'R73': 180, 'R74': 180, 'R76': 180,
         'R80': 180, 'R81': 90, 'R82': 180, 'R90': 270, 'R95': 90, 'R98': 180, 'R99': 180, 'R100': 180, 'R101': 180,
         'R105': 180, 'R110': 90, 'R111': 270, 'R114': 180, 'R117': 180, 'R119': 180, 'R120': 180, 'R121': 180,
         'R122': 180, 'R133': 180, 'R134': 180, 'R135': 180, 'R138': 180, 'R139': 180, 'R141': 180, 'R143': 180,
         'R145': 270, 'R148': 180, 'R149': 270, 'R151': 180, 'R152': 180, 'R153': 90, 'R155': 180, 'R159': 180,
         'R160': 180, 'R167': 180, 'R168': 180, 'R169': 180, 'R175': 180, 'R176': 180, 'R178': 180, 'R187': 90,
         'R190': 180, 'R191': 180, 'R193': 180, 'R195': 90, 'R196': 180, 'R197': 180, 'R198': 90, 'R199': 180,
         'R202': 180, 'R203': 180, 'R204': 180, 'R205': 180, 'R206': 180, 'R212': 180, 'R213': 180, 'R214': 180,
         'R216': 180, 'R218': 180, 'R219': 180, 'R221': 180}
# CS4b (cs4b_proposal.md, signed off 2026-10-27): the jack-link clamps (BAV199) beside CN5, placed by MOVES alone (never packed)
CS4B = {'D79': (16.0, 123.75, 0, 'F'), 'D80': (20.25, 123.75, 0, 'F'), 'D81': (24.25, 123.75, 0, 'F'),
        'D82': (28.25, 123.75, 0, 'F'), 'D83': (24.75, 126.25, 0, 'B'), 'D84': (33.5, 126.25, 0, 'B'),
        'D85': (37.5, 126.25, 0, 'B'), 'D86': (33.5, 130.0, 0, 'B'), 'D87': (41.25, 126.5, 90, 'B'),
        'D88': (37.75, 130.0, 90, 'B'), 'D89': (45.25, 126.25, 0, 'B'), 'D90': (45.25, 130.0, 0, 'B'),
        'D91': (49.25, 126.25, 0, 'B'), 'D92': (51.0, 123.75, 0, 'F'), 'D93': (50.75, 127.5, 90, 'F'),
        'D94': (53.25, 126.25, 0, 'B'), 'D95': (54.75, 124.0, 90, 'F'), 'D96': (58.5, 123.75, 0, 'F'),
        'D97': (62.5, 123.75, 0, 'F'), 'D98': (54.75, 130.0, 0, 'B'), 'D99': (63.5, 126.25, 0, 'B'),
        'D100': (66.5, 117.25, 90, 'F'), 'D101': (67.75, 126.25, 0, 'B'), 'D102': (63.5, 130.0, 90, 'B')}
MOVES.update(CS4B)
# CS4c (cs4c_proposal.md): the 22R inside each DRV135 loop at its output pin, placed by MOVES alone (never packed)
CS4C = {'R222': (10.25, 163.5, 0, 'B'), 'R223': (6.0, 168.5, 0, 'B'), 'R224': (37.0, 174.5, 0, 'F'),
        'R225': (33.0, 179.0, 0, 'B'), 'R226': (25.75, 203.75, 0, 'B'), 'R227': (20.75, 203.75, 0, 'B'),
        'R228': (7.25, 114.75, 0, 'B'), 'R229': (3.25, 114.25, 0, 'B'), 'R230': (71.25, 114.5, 0, 'F'),
        'R231': (68.25, 126.25, 0, 'F'), 'R232': (56.5, 219.0, 0, 'B'), 'R233': (52.25, 220.25, 0, 'B'),
        'R234': (31.5, 231.5, 90, 'B'), 'R235': (28.25, 228.75, 0, 'F')}
MOVES.update(CS4C)
# CS7 (cs7_proposal.md): the DIM key beside POWER in the EXT row (actuator at (XR, 178)) and its two 91K across its poles,
# placed by MOVES alone. Main R's DRV135 (U8) leaves the key's spot with its loop and decoupling parts, to the bottom side
# beside it: the 22R legs (pin -> 22R -> 10u -> Sense) 9.0 / 9.8 mm (were 10.2 / 10.4), C49 / C50 0.1 / 2.4 mm from their
# supply pins (4.3 / 4.0); the 10u radials stay on the bottom (11.5 mm panel gap)
CS7_U8 = {'U8': (37.0, 174.0, 90, 'B'), 'C47': (43.25, 169.5, 270, 'B'), 'C48': (37.75, 182.0, 90, 'B'),
          'C49': (35.0, 171.5, 180, 'F'), 'C50': (32.75, 170.0, 270, 'B'), 'R224': (39.75, 171.5, 0, 'F'),
          'R225': (39.75, 176.5, 0, 'F')}
CS7 = {'SW4': sw(XR, 178), 'R236': (30.5, 177.75, 180, 'B'), 'R237': (30.5, 183.75, 180, 'B')}
MOVES.update(CS7_U8); MOVES.update(CS7)
# D13 (delta_crosscheck.md): the five spare-conductor ground jumpers on the bottom beside the left wing header, placed
# by MOVES alone (bridged: open them for an 8-group build)
D13 = {'JP3': (13.3, 321.5, 90, 'B'), 'JP4': (13.3, 325.5, 90, 'B'), 'JP5': (13.3, 329.5, 90, 'B'), 'JP6': (13.3, 333.5, 90, 'B'),
       'JP7': (13.3, 337.2, 90, 'B')}    # a column between CN2's courtyard (x <= 11.8) and the meter LEDs' leads (x 15.5)
MOVES.update(D13)
# clicks_proposal.md RV7 / RV8 / RV9 (signed off 2026-10-28), placed by MOVES alone at probed free spots on the bottom
# (the guard's rules: same-side courtyards, THT leads against both sides): the aux 5 / 6 AFL films (the bottom under the
# aux masters is full of leads from the top: 64 / 24 mm from their 22K, a low-Z buffer output feed), the phones
# gain-set 33u NP cans (D8; no D10 spot exists) 13 / 21 mm from their 2K2, the -V-loss reference divider beside U10
CLICKS = {'C194': (70.71, 143.91, 0, 'B'), 'C195': (42.58, 165.29, 90, 'B'), 'C196': (10.32, 276.39, 0, 'B'),
          'C197': (22.54, 311.35, 0, 'B'), 'R238': (48.74, 188.25, 0, 'B'), 'R239': (47.49, 186.08, 0, 'B')}
MOVES.update(CLICKS)
for z in ZONES: z[2][:] = [r for r in z[2] if r not in CS4C and r not in CS7 and r not in CLICKS]   # their drivers' blocks list them too
place(os.path.join(PROJ, 'master.net'), os.path.join(PROJ, 'master.kicad_pcb'),
      dict(board=(0, MAIN_Y0, W, MAIN_Y1), fix=FIX, moves=MOVES, moves_only=tuple(CS4B) + tuple(CS4C) + tuple(CS7) + tuple(D13) + tuple(CLICKS), wire=tuple(CS4C) + ('C194', 'C195'), attach_as={'R69': ('output', 'U13', '1'), 'R80': ('output', 'U13', '7')}, turns=TURNS, layers=4, rails=(0.5, 6.5), holes=HOLES, zones=ZONES, near=NEAR, notes=NOTES,
           grounds=('GNDA', 'GNDD', 'GNDM', 'PHONESGND', 'CHASSIS'), silk_text_off=('K',), hole_value='M3 standoff 11.5 mm',
           attach=True, keepout=[(0, 186, EL, 299), (ER, 186, W, 299),
                                 (21.0, 202.2, 58.0, 220.0, 'B')]))     # J1's wire entries (its +y face): room for the wires
