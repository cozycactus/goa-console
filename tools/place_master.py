"""Component placement for the master module (M1, 16 HP): main board + jack board, placement only.
  KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3
  $KPY tools/place_master.py      # -> master.kicad_pcb (78.6 x 331.5 mm), master_jack_board.kicad_pcb (78.6 x 111.5 mm)
16 HP x 12U panel (80.9 mm) in the strip's frame (placer.py): y = 0 is 11 mm below the panel's top edge, panel
x = board x + 1.15, pot columns at the strips' 10 / 28 and 50.64 / 68.64 (8 HP further). The dual master fader
sits on the strips' slot line (y 372, x 39.3) between the two 20-LED meters; both wing bus headers sit at the
strips' header height, pin 1 at the bottom end like every strip, so each wing's ribbon runs straight.
Jack board (~24 mm under the panel): MAIN L / R / MONO XLRs (NC3MAV) in a column, 9 NJ6FD-V in two columns,
2x20 link along its bottom edge; the main board's 2x20 sits along its top edge, pin 1 at the same end.
Zones follow gen_master.py's blocks (master_parts.json)."""
import json, os, re, sys
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
NEAR = dict(d['near'])
for u, cs in (('U7', 'C34 C35 C36 C37 K1'), ('U8', 'C38 C39 C40 C41 K2'), ('U9', 'C42 C43 C44 C45 K3'),
              ('U13', 'C56 C57 C58 C59'), ('U16', 'C67 C68 C69 C70'), ('U22', 'C100 C101 C102 C103 K4'),
              ('U23', 'C105 C106 C107 C108 K5'), ('K1', 'R39 D4'), ('K2', 'R40 D5'), ('K3', 'R41 D6'),
              ('K4', 'R118 D20'), ('K5', 'R120 D21'),
              ('U1', 'FB1 R10 C11'), ('U3', 'FB2 R18 C18'), ('U12', 'FB3 R54 C53'), ('U14', 'FB4 R65 C62'),
              ('U18', 'FB5 R88 C83'), ('U25', 'C112 C113 C114 C115 R122'), ('U26', 'C118 C119 C120 C121 R126'),
              # LM2901 ladders beside the first LED each package drives
              ('D28', 'U29'), ('D32', 'U30'), ('D36', 'U31'), ('D42', 'U32'), ('D46', 'U33'),
              ('D56', 'U36'), ('D60', 'U37'), ('D64', 'U38'), ('D70', 'U39'), ('D74', 'U40')):
    NEAR.update({c: u for c in cs.split()})

mL = [r for r in B['METER L'] if r.startswith('D') and r not in ('D22', 'D23', 'D24', 'D25', 'D26', 'D27', 'D38', 'D39')]
mR = [r for r in B['METER R'] if r.startswith('D') and r not in ('D50', 'D51', 'D52', 'D53', 'D54', 'D55', 'D66', 'D67')]
FIX = {
 'RV2': pot(XL, 134), 'RV3': pot(XR, 134, right=True), 'RV5': pot(59.3, 134, dual=True),           # AUX 5 | AUX 6 || C/ROOM
 'SW1': sw(6, 156), 'D12': led(14.2, 156), 'SW2': sw(24, 156), 'D13': led(32.2, 156),             # AFL 5 | AFL 6
 'RV6': pot(XL + H8, 156, dual=True), 'RV4': pot(XR + H8, 156, right=True),                        # || PHONES | SOLO
 'D3': led(19, 178), 'SW3': sw(XL + H8, 178), 'D15': led(XR + H8, 178),                           # POWER || EXT | PFL ACTIVE
 'RV1': (XF - 1.9, 372 + 63.75, 270, 'F'),                                                         # dual master fader
 'CN2': (5.5, BUS[1], 180, 'B'),              # left-wing bus header: as a strip's, 1.4 mm in so its pin-1 mark stays on
 'CN3': (72.0, BUS[1], 180, 'B'),             # right-wing bus header (pin-1 mark inboard)
 'CN5': (15.0, 118.0, 270, 'B'),              # 2x20 link to the jack board, pin 1 left, pin-1 mark towards the edge
}
for k, (l, r) in enumerate(zip(mL, mR)):      # D28..D49 / D56..D77 in ladder order: -20 dB at the bottom, +18 dB at the top
    FIX[l] = led(18.0, 422.0 - 5.0 * k); FIX[r] = led(60.6, 422.0 - 5.0 * k)
HOLES = [(44, 134), (5, 215), (73.6, 215), (26, 318), (52.6, 318), (24, 436), (54.4, 436)]

net = sexp(open(os.path.join(PROJ, 'master.net')).read())
comps = next(c for c in net[1:] if isinstance(c, list) and c[0] == 'components')
FPN = {field(c, 'ref'): field(c, 'footprint') for c in comps[1:]}
VAL = {field(c, 'ref'): field(c, 'value') for c in comps[1:]}
TALL = {r for r, f in FPN.items() if any(k in f for k in ('CP_Radial', 'C_Rect', 'Fuse_', 'TerminalBlock',
                                                         'Potentiometer_Bourns_3296', 'PinHeader'))}  # bottom: 11.5 mm gap
dia = lambda r: float(FPN[r].split('_D')[1].split('mm')[0]) if 'CP_Radial' in FPN[r] else 0.0
num = lambda r: int(re.sub(r'\D', '', r))
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
SUMMER5 = ['U12', 'C51', 'C52', 'FB3', 'R54', 'C53', 'R55', 'R56', 'R57', 'R58']
SUMMER6 = ['U14', 'C60', 'C61', 'FB4', 'R65', 'C62', 'R66', 'R67', 'R68', 'R69']
SUMMERP = ['U18', 'C81', 'C82', 'FB5', 'R88', 'C83', 'R89', 'R90', 'R91', 'R92']
OUTS = ['U7', 'C36', 'C37', 'K1', 'R39', 'D4', 'U8', 'C40', 'C41', 'K2', 'R40', 'D5', 'U9', 'C44', 'C45', 'K3', 'R41', 'D6',
        'U22', 'C102', 'C103', 'K4', 'R118', 'D20', 'U23', 'C107', 'C108', 'K5', 'R120', 'D21',
        'U13', 'C58', 'C59', 'U16', 'C69', 'C70']
ic_first = lambda refs: sorted(refs, key=lambda r: not r.startswith(('U', 'K')))    # ICs before their NEAR parts
ZONES = [
 # bottom side: electrolytics, PTCs, terminal, trimmers
 ('balanced-out, monitor and aux coupling caps (bottom)', (0.3, MAIN_Y0, W - 0.3, 236),
  tall('MAIN OUTPUTS', 'AUX MASTER 5', 'AUX MASTER 6', 'EXT INPUT', 'PFL / AFL', 'PFL SWITCHER', 'CONTROL ROOM',
       'HEADPHONES', 'POWER-ON MUTE'), 'B'),
 ('power entry: terminal, reservoirs, wing PTCs (bottom)', (11, 228, 68, 305),         # terminal, big caps, PTCs, rest
  sorted(tall('POWER ENTRY', 'DISTRIBUTION'), key=lambda r: (0 if r[0] == 'J' else 1 if dia(r) >= 10 else
                                                             2 if r[0] == 'F' else 3, -dia(r), num(r))), 'B'),
 ('mix coupling (bottom)', (11, 296, 68, 444), tall('MIX L', 'MIX R', 'MASTER FADER'), 'B'),
 ('meter trims + remote meter header (bottom)', (0.3, 300, W - 0.3, 444), tall('METER L', 'METER R', 'REMOTE METER HEADER'), 'B'),
 # top side
 ('balanced outputs + mute relays (towards the jack-board link)', (0.3, MAIN_Y0, W - 0.3, 236), ic_first(OUTS), 'F'),
 ('monitoring: EXT, PFL switcher, C/ROOM, phones', (36, MAIN_Y0, W - 0.3, 236),
  ic_first(take('EXT INPUT', 'PFL SWITCHER', 'CONTROL ROOM', 'HEADPHONES', drop=OUTS)), 'F'),
 ('aux 5-6 level buffers, AFL; solo level', (0.3, MAIN_Y0, 40, 236),
  ic_first(take('AUX MASTER 5', 'AUX MASTER 6', 'PFL / AFL', drop=OUTS + SUMMER5 + SUMMER6 + SUMMERP)), 'F'),
 ('PFL detect, power-on mute', (0.3, 160, W - 0.3, 240), ic_first(take('PFL DETECT', 'POWER-ON MUTE')), 'F'),
 ('GC buffer, summers, re-inverters, insert returns, mono (between the wing headers)', (11, 236, 68, 306),
  ic_first(take('GROUND CANCEL BUFFER', 'MIX L', 'MIX R', 'MONO') + SUMMER5 + SUMMER6 + SUMMERP), 'F'),
 ('power distribution, star ground', (11, 190, 68, 306), take('POWER ENTRY', 'DISTRIBUTION'), 'F'),
 ('post-amps L + R around U5 and wiper coupling (fader wiper end)', (19, 424.5, 60, 444), POST, 'F'),
 ('meter L', (0.3, 300, 31.2, 444), ic_first(take('METER L')), 'F', 0.8),
 ('meter R', (47.4, 300, W - 0.3, 444), ic_first(take('METER R')), 'F', 0.8),
]
NOTES = ((134, 'AUX 5 | AUX 6 || C/ROOM'), (156, 'AFL 5 | AFL 6 || PHONES | SOLO'), (178, 'POWER || EXT | PFL ACTIVE'),
         (305, 'BUS HEADERS: left wing CN2, right wing CN3 (bottom)'), (372, 'MASTER FADER 100 mm, meters L | R'),
         (118, 'LINK CN5 (bottom) to the jack board, pin 1 left'))
place(os.path.join(PROJ, 'master.net'), os.path.join(PROJ, 'master.kicad_pcb'),
      dict(board=(0, MAIN_Y0, W, MAIN_Y1), fix=FIX, holes=HOLES, zones=ZONES, near=NEAR, notes=NOTES,
           grounds=('GNDA', 'GNDD', 'GNDM', 'PHONESGND'), silk_text_off=('K',), hole_value='M3 standoff 11.5 mm'))
