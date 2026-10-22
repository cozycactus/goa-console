"""Component placement for the channel-strip PCBs, v4.0 (KiCad 10 pcbnew API). Placement only: no copper.
Two boards, each from its own netlist; the layout is picked from the parts (CN5 = jack board):
  KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3
  $KPY tools/place_strip.py channel_strip.net channel_strip_v4.kicad_pcb     # main board, 38 x 400 mm
  $KPY tools/place_strip.py jack_board.net jack_board.kicad_pcb              # jack board, 38 x 43 mm
Panel: 8 HP x 12U Eurorack-style (40.3 x 514 mm), two pot columns, jacks on the panel (study:
strip_panel_study.md). y = 0 is 11 mm below the panel's top edge (end rail) and grows towards the fader;
both boards use these coordinates, so the two files overlay on the panel. The jack board (y 0-43) sits
~24 mm under the panel (a 1/4" plug goes ~30 mm deep); the main board (y 44-444) at 11.5 mm. A 10-way
IDC ribbon joins CN5 (jack board, bottom) to CN3 (main board, bottom).
Panel parts sit at fixed coordinates. Every other part is packed into a named zone at the first position
where its courtyard clears every courtyard on its side and every through-hole pad on either side (THT
pads go through the board), so top and bottom parts can share an area without colliding.
Each footprint is linked to its schematic symbol, so "Update PCB from Schematic" works later."""
import os, sys
import pcbnew
sys.path.insert(0, os.path.dirname(__file__))
from verify import sexp, field

NET, OUT = sys.argv[1], sys.argv[2]
# Preserve any later manual routing. Rebuild into a separate file once routing has started.
if os.path.exists(OUT):
    old = sexp(open(OUT).read())
    copper = [item[0] for item in old[1:] if isinstance(item, list) and
              item and item[0] in ('segment', 'arc', 'via', 'zone')]
    if copper:
        raise SystemExit(f'{OUT}: contains routing or zones; choose a separate placement output')
PROJ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
KLIB = '/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/'
if not os.path.isdir(KLIB): KLIB = '/usr/share/kicad/footprints/'

W = 38.0                      # board width: 40 mm strip pitch
JACK_Y1, MAIN_Y0, MAIN_Y1 = 43.0, 44.0, 444.0   # jack board y 0-43, main board y 44-444 (514 mm 12U panel)
XL, XR, XC = 10.0, 28.0, 19.0 # pot columns and centre line (panel x = board x + 1.15)
GAP, STEP = 0.3, 0.5          # packer clearance between courtyards / pads, search step

# ---------------------------------------------------------------- feature positions -> footprint origins
def pot(x, y, dual=False, right=False):
    # RD901F/RD902F: shaft at (7.5, 2.5) from pin 1. Single pots in the right column turn 180 deg (body to the
    # board edge); dual pots stay at 0 deg on the right (their second gang would hang off the edge) and turn
    # 180 deg on the left.
    rot = 180 if (right and not dual) or (dual and not right) else 0
    return (x + 7.5, y + 2.5, 180, 'F') if rot == 180 else (x - 7.5, y - 2.5, 0, 'F')
sw  = lambda x, y: (x - 2.5, y - 3.0, 0, 'F')          # PVA2: actuator centre at (2.5, 3.0) from pin 1
led = lambda x, y: (x - 1.27, y, 0, 'F')               # 3 mm LED: centre at (1.27, 0)
jack = lambda x, y: (x, y - 5.72, 0, 'F')              # NJ6FD-V: nose centre at (0, 5.72) from the tip pin

# ================================================================ jack board
JACK_FIX = {'J1': jack(XL, 12), 'J2': jack(XR, 12), 'J5': jack(XL, 32)}              # line in, insert / direct out
# M3 standoffs to the panel, length = jack body height (~24 mm); the jack caps hold the board too
JACK_HOLES = [(23, 27), (23, 37)]
JACK_ZONES = [
 ('link header (bottom)', (25, 21, 37, 43), ['CN5'], 'B'),
 ('input RF caps (bottom, at J1)', (1, 1, 19, 22), ['C8', 'C9'], 'B'),
]
JACK_NOTES = ((12, 'LINE IN | INSERT'), (32, 'DIRECT OUT | link CN5 (bottom)'))

# ================================================================ main board
FIX = {
 'SW15': sw(XR, 50), 'RV9': pot(XL, 54), 'D2': led(XR, 61),                               # Ø, gain, OL
 'RV10': pot(XL, 76), 'SW11': sw(XR, 76),                                                 # HF, HPF
 'RV11': pot(XL, 98), 'RV12': pot(XR, 98, dual=True, right=True),                         # HI-MID gain, freq
 'RV13': pot(XL, 120), 'RV14': pot(XR, 120, dual=True, right=True),                       # LO-MID gain, freq
 'RV15': pot(XL, 142), 'SW12': sw(26, 142), 'D5': led(34.5, 142),                         # LF, EQ + LED
 'RV2': pot(XL, 166), 'RV3': pot(XR, 166, right=True),                                    # aux 1, 2
 'RV4': pot(XL, 188), 'RV5': pot(XR, 188, right=True),                                    # aux 3, 4
 'RV6': pot(XL, 210), 'RV7': pot(XR, 210, right=True),                                    # aux 5, 6
 'SW8': sw(6, 230), 'SW9': sw(17, 230), 'SW10': sw(28, 230),                              # PRE 1-2, 3-4, 5-6
 'RV8': pot(XL, 252, dual=True), 'SW14': sw(XR, 246), 'SW13': sw(XR, 258),                # pan, PAN, DIR
 'SW5': sw(6, 274), 'SW6': sw(17, 274), 'SW7': sw(28, 274),                               # L-R, 1-2, 3-4
 'SW3': sw(6, 292), 'D3': led(14.2, 292), 'SW4': sw(24, 292), 'D4': led(32.2, 292),       # PFL, ON
 'RV1': (XC - 1.9, 372 + 63.75, 270, 'F'),                                                # fader, slot centre y = 372
 'CN1': (34.0, 305.0, 0, 'B'),           # bus header, bottom side, pins at x = 31.46 / 34, y = 305..346
 'CN4': (5.0, 358.0, 0, 'B'),            # ground spade, bottom side, left of the fader body
 'NT1': (5.0, 351.0, 0, 'F'),            # AGND-LGND net tie beside the spade (no courtyard: keep it clear by hand)
}
# M3 standoff holes (11.5 mm), unplated so audio ground never meets the chassis
HOLES = [(XC, 67), (XC, 154), (XC, 221), (5, 330), (5, 425), (34, 425)]

# ---------------------------------------------------------------- zones: (x0, y0, x1, y1), refs, side
# Bottom side: radial electrolytics (too tall for the 11.5 mm panel gap), VCA socket. Placed first.
ZONES = [
 ('jack-board link (bottom)', (12, 44, 37, 120), ['CN3'], 'B'),     # pins between the columns
 ('rail reservoir caps (bottom)', (1, 360, 37, 444), ['C1', 'C3', 'C5', 'C6'], 'B'),
 ('gain-out coupling (bottom)',  (1, 45, 37, 80), ['C38'], 'B'),
 ('insert / EQ coupling (bottom)', (1, 75, 37, 160), ['C51', 'C10', 'C11'], 'B'),
 ('post / pan / direct-out coupling (bottom)', (1, 160, 37, 300), ['C15', 'C16', 'C17', 'C52'], 'B'),
 ('VCA module socket (bottom)', (1, 380, 37, 444), ['J3', 'J4'], 'B'),
 # Top side, roughly in signal order
 ('input receiver + gain', (1, 45, 37, 100), ['U1', 'C20', 'C21', 'R6', 'R7', 'C7', 'R8', 'R9', 'R10',
                                              'R45', 'R46', 'C37', 'R47'], 'F'),
 ('OL detector', (1, 45, 37, 100), ['U4', 'C26', 'R39', 'D1', 'C12', 'R14', 'R40', 'R41', 'R15'], 'F'),
 ('HPF', (1, 60, 37, 100), ['U5', 'C29', 'C30', 'C39', 'C40', 'R48', 'R49'], 'F'),
 ('EQ', (1, 82, 37, 162), ['U6', 'C31', 'C32', 'U7', 'C33', 'C34', 'C48', 'C49', 'R50', 'R51', 'C41', 'C42', 'R52',
                           'C43', 'R53', 'R54', 'R55', 'C44', 'R56', 'R57', 'C45', 'R58', 'R59', 'C46', 'R60', 'R61',
                           'C47', 'R62', 'R63', 'R64', 'C50', 'R65', 'R66', 'R67', 'R68', 'R69'], 'F'),
 ('insert + position jumpers', (1, 120, 37, 175), ['R11', 'R12', 'R13', 'JP5', 'JP6', 'JP7'], 'F'),
 ('aux / PRE jumpers / direct out', (1, 150, 37, 270), ['JP2', 'JP3', 'JP4', 'U8', 'C35', 'C36', 'R70', 'R71',
                                                        'R72', 'R73'], 'F'),
 ('pan buffers + mute', (1, 236, 37, 306), ['U3', 'C24', 'C25', 'R35', 'R36', 'R37', 'R16', 'R17', 'Q1', 'Q2',
                                            'R42', 'C28', 'R43'], 'F'),
 ('PFL', (1, 280, 37, 330), ['R32', 'R33', 'R34'], 'F'),
 ('bus resistors (at the header)', (22, 296, 37, 362), ['R20', 'R21', 'R22', 'R23', 'R24', 'R25', 'R26', 'R27',
                                                        'R28', 'R29', 'R30', 'R31'], 'F'),
 ('power entry', (1, 340, 37, 380), ['R1', 'R2', 'R3', 'R4', 'R5', 'C2', 'C4'], 'F'),
 ('fader post-amp', (27, 340, 37, 444), ['U2', 'C22', 'C23', 'R19', 'C14', 'R38', 'C13', 'JP1', 'R18', 'R44'], 'F'),
]
NOTES = ((50, 'GAIN | PHASE, OL'), (76, 'HF | HPF'), (98, 'HI-MID gain | freq'), (120, 'LO-MID gain | freq'),
         (142, 'LF | EQ'), (166, 'AUX 1 | 2'), (188, 'AUX 3 | 4'), (210, 'AUX 5 | 6'), (230, 'PRE 1-2  3-4  5-6'),
         (252, 'PAN | PAN, DIR'), (274, 'L-R  1-2  3-4'), (292, 'PFL | ON'), (305, 'BUS HEADER (bottom, right)'),
         (372, 'FADER 100 mm'), (55, 'LINK CN3 (bottom) to the jack board'))

# ---------------------------------------------------------------- netlist
tree = sexp(open(NET).read())
comps = next(c for c in tree[1:] if isinstance(c, list) and c[0] == 'components')
nets = next(c for c in tree[1:] if isinstance(c, list) and c[0] == 'nets')
parts = {}
for c in comps[1:]:
    ts = next((x for x in c[1:] if isinstance(x, list) and x[0] == 'tstamps'), None)
    props = {field(x, 'name'): field(x, 'value') for x in c[1:] if isinstance(x, list) and x[0] == 'property'}
    parts[field(c, 'ref')] = dict(value=field(c, 'value'), fp=field(c, 'footprint'), uuid=ts[1] if ts else None,
                                  mpn=props.get('MPN'), dnp='dnp' in props, nobom='exclude_from_bom' in props)
padnet = {}
for n in nets[1:]:
    name = field(n, 'name')
    for nd in n[1:]:
        if isinstance(nd, list) and nd[0] == 'node': padnet[(field(nd, 'ref'), field(nd, 'pin'))] = name

if 'CN5' in parts:      # jack board
    BOARD, FIX, HOLES, ZONES, NOTES = (0, 0, W, JACK_Y1), JACK_FIX, JACK_HOLES, JACK_ZONES, JACK_NOTES
    HOLE_VALUE = 'M3 standoff = jack body height (~24 mm)'
else:
    BOARD, HOLE_VALUE = (0, MAIN_Y0, W, MAIN_Y1), 'M3 standoff 11.5 mm'
placed = set(FIX) | {r for _, _, refs, _ in ZONES for r in refs}
missing = sorted(set(parts) - placed); extra = sorted(placed - set(parts))
if missing or extra: raise SystemExit(f'placement table out of date: unplaced {missing}, unknown {extra}')

# ---------------------------------------------------------------- board
board = pcbnew.CreateEmptyBoard()
board.SetCopperLayerCount(2)
netinfo = {}
for name in sorted(set(padnet.values())):
    ni = pcbnew.NETINFO_ITEM(board, name); board.Add(ni); netinfo[name] = ni

def edge_rect(x0, y0, x1, y1, layer=pcbnew.Edge_Cuts, width=0.1):
    s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_RECT)
    s.SetStart(pcbnew.VECTOR2I_MM(x0, y0)); s.SetEnd(pcbnew.VECTOR2I_MM(x1, y1))
    s.SetLayer(layer); s.SetWidth(pcbnew.FromMM(width)); board.Add(s)

def note(text, x, y, layer=pcbnew.Cmts_User, size=1.5):
    t = pcbnew.PCB_TEXT(board); t.SetText(text); t.SetPosition(pcbnew.VECTOR2I_MM(x, y))
    t.SetLayer(layer); t.SetTextSize(pcbnew.VECTOR2I_MM(size, size)); t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
    board.Add(t)

edge_rect(*BOARD)

def load(ref):
    p = parts[ref]; lib, name = p['fp'].split(':', 1)
    path = os.path.join(PROJ, lib + '.pretty') if lib == 'goa-console' else os.path.join(KLIB, lib + '.pretty')
    fp = pcbnew.FootprintLoad(path, name)
    if fp is None: raise SystemExit(f'{ref}: footprint {p["fp"]} not found')
    fp.SetFPID(pcbnew.LIB_ID(lib, name))
    fp.SetReference(ref); fp.SetValue(p['value'])
    if p['uuid']: fp.SetPath(pcbnew.KIID_PATH('/' + p['uuid']))
    if p['mpn']:
        fp.SetField('MPN', p['mpn']); fp.GetField('MPN').SetVisible(False)
    fp.SetDNP(p['dnp']); fp.SetExcludedFromBOM(p['nobom'])
    board.Add(fp)
    for pad in fp.Pads():
        n = padnet.get((ref, pad.GetNumber()))
        if n: pad.SetNet(netinfo[n])
    return fp

mm = pcbnew.ToMM
def bbox(bb): return (mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom()))
def courtyard(fp):
    side = pcbnew.B_CrtYd if fp.IsFlipped() else pcbnew.F_CrtYd
    fp.BuildCourtyardCaches()
    poly = fp.GetCourtyard(side)
    return bbox(poly.BBox() if poly.OutlineCount() else fp.GetBoundingBox(False))
def tht_pads(fp):
    return [bbox(p.GetBoundingBox()) for p in fp.Pads()
            if p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH)]
def flip(fp):
    try: fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    except (AttributeError, TypeError): fp.Flip(fp.GetPosition(), False)

occ = {'F': [], 'B': []}       # courtyards per side, plus THT pads of parts on the other side
def overlaps(r, rects, g=GAP):
    return any(r[0] < q[2] + g and q[0] < r[2] + g and r[1] < q[3] + g and q[1] < r[3] + g for q in rects)
def register(fp, side):
    other = 'B' if side == 'F' else 'F'
    occ[side].append(courtyard(fp))
    occ[other].extend(tht_pads(fp))

for ref, (x, y, rot, side) in FIX.items():
    fp = load(ref)
    fp.SetOrientationDegrees(rot); fp.SetPosition(pcbnew.VECTOR2I_MM(x, y))
    if side == 'B': flip(fp)
    register(fp, side)
for i, (x, y) in enumerate(HOLES, 1):
    h = pcbnew.FootprintLoad(os.path.join(KLIB, 'MountingHole.pretty'), 'MountingHole_3.2mm_M3')
    h.SetFPID(pcbnew.LIB_ID('MountingHole', 'MountingHole_3.2mm_M3')); h.SetReference(f'H{i}'); h.SetValue(HOLE_VALUE)
    h.SetBoardOnly(True); h.SetExcludedFromBOM(True); h.SetExcludedFromPosFiles(True)
    board.Add(h); h.SetPosition(pcbnew.VECTOR2I_MM(x, y))
    c = courtyard(h); occ['F'].append(c); occ['B'].append(c)

def fits(fp, side, x0, y0, x1, y1):
    other = 'B' if side == 'F' else 'F'
    c = courtyard(fp)
    if (c[0] < max(x0, BOARD[0] + 0.3) or c[1] < max(y0, BOARD[1] + 0.3) or c[2] > min(x1, BOARD[2] - 0.3)
            or c[3] > min(y1, BOARD[3] - 0.3)): return False
    if overlaps(c, occ[side]): return False
    pads = tht_pads(fp)
    return not (pads and any(overlaps(p, occ[other]) for p in pads))

report = []
for zname, (x0, y0, x1, y1), refs, side in ZONES:
    edge_rect(x0, y0, x1, y1, pcbnew.Dwgs_User if side == 'F' else pcbnew.Cmts_User, 0.05)
    for ref in refs:
        fp = load(ref)
        if side == 'B': flip(fp)
        done = False
        for rot in (0, 90):
            fp.SetOrientationDegrees(rot if side == 'F' else 180 - rot)
            fp.SetPosition(pcbnew.VECTOR2I_MM(0, 0))
            l, t, r, b = courtyard(fp)
            y = y0
            while y + (b - t) <= y1 and not done:
                x = x0
                while x + (r - l) <= x1:
                    fp.SetPosition(pcbnew.VECTOR2I_MM(x - l, y - t))
                    if fits(fp, side, x0, y0, x1, y1):
                        done = True; break
                    x += STEP
                if not done: y += STEP
            if done: break
        if done: register(fp, side)
        else:
            report.append(f'{zname}: no room for {ref}')
            fp.SetPosition(pcbnew.VECTOR2I_MM(BOARD[2] + 10, y0))   # parked off-board so DRC flags it

# panel-feature notes (board y)
for y, txt in NOTES:
    note(txt, W + 3, y, size=2.0)
pcbnew.SaveBoard(OUT, board)
print(f'placed {len(parts)} footprints + {len(HOLES)} holes on {BOARD[2] - BOARD[0]:.0f} x {BOARD[3] - BOARD[1]:.0f} mm; nets {len(netinfo)}')
for r in report: print('  WARNING', r)
