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
JACK_HOLES = [(73.3, 15), (73.3, 90), (8, 97)]
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
OUTS = []
for u in sorted((r for r in VAL if VAL[r] == 'DRV134'), key=num):
    OUTS += [u] + [r for r in beside(u) if not r.startswith('K')]
    for k in (r for r in beside(u) if r.startswith('K')): OUTS += [k] + beside(k)
for k in sorted((r for r in VAL if VAL[r].startswith('G6K') and r not in NEAR), key=num): OUTS += [k] + beside(k)
EL, ER = 4.0, W - 4.0                          # edge channels for the wing supplies (y 186 to the headers)
PWR_TALL = tall('POWER ENTRY', 'DISTRIBUTION')
ZONES = [
 # power entry first, so it gets its area around J1 and the star stud
 ('left-wing PTCs at J1 (bottom)', (EL, 186, 22, 236), ['F1', 'F2'], 'B'),
 ('right-wing PTCs at J1 (bottom)', (W - 22, 186, ER, 236), ['F3', 'F4'], 'B'),
 ('rail reservoirs beside J1 (bottom)', (EL, 186, ER, 236), sorted((r for r in PWR_TALL if r[0] == 'C'), key=lambda r: (-dia(r), num(r))), 'B'),
 ('SS54 clamps, branch resistors (top, at J1)', (EL, 186, ER, 236), take('POWER ENTRY', 'DISTRIBUTION'), 'F'),
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
 ('monitoring: EXT, PFL switcher, C/ROOM, phones', (EL, MAIN_Y0, ER, 306),
  take('EXT INPUT', 'PFL SWITCHER', 'PFL DETECT', 'CONTROL ROOM', 'HEADPHONES', drop=OUTS), 'F'),
 ('aux 5-6 level buffers, AFL; solo level', (EL, MAIN_Y0, ER, 306),
  take('AUX MASTER 5', 'AUX MASTER 6', 'PFL / AFL', drop=OUTS + SUMMER5 + SUMMER6 + SUMMERP), 'F'),
 ('rude-solo flasher, power-on mute', (EL, 160, ER, 306), take('RUDE SOLO', 'POWER-ON MUTE'), 'F'),
 ('post-amps L + R around U5 and wiper coupling (fader wiper end)', (19, 424.5, 60, 444), POST, 'F'),
 ('meter L', (0.3, 300, 31.2, 444), take('METER L'), 'F'),
 ('meter R', (47.4, 300, W - 0.3, 444), take('METER R'), 'F'),
]
NOTES = ((134, 'AUX 5 | AUX 6 || C/ROOM'), (156, 'AFL 5 | AFL 6 || PHONES | SOLO'), (178, 'POWER || EXT | PFL ACTIVE'),
         (197, 'POWER IN J1 (bottom), star stud CN1 + NT1-4 at y 214; wing supplies along the board edges'),
         (305, 'BUS HEADERS: left wing CN2, right wing CN3 (bottom)'), (372, 'MASTER FADER 100 mm, meters L | R'),
         (118, 'LINK CN5 (bottom) to the jack board, pin 1 left'))
place(os.path.join(PROJ, 'master.net'), os.path.join(PROJ, 'master.kicad_pcb'),
      dict(board=(0, MAIN_Y0, W, MAIN_Y1), fix=FIX, holes=HOLES, zones=ZONES, near=NEAR, notes=NOTES,
           grounds=('GNDA', 'GNDD', 'GNDM', 'PHONESGND', 'CHASSIS'), silk_text_off=('K',), hole_value='M3 standoff 11.5 mm',
           attach=True, keepout=[(0, 186, EL, 299), (ER, 186, W, 299),
                                 (21.0, 202.2, 58.0, 220.0, 'B')]))     # J1's wire entries (its +y face): room for the wires
