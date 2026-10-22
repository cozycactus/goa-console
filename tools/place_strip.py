"""First placement of the channel-strip PCB (KiCad 10 pcbnew API).
Run with KiCad's bundled Python:
  /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 \
      tools/place_strip.py channel_strip.net channel_strip.kicad_pcb
Panel parts (jacks, pots, switches, LEDs, fader, bus headers) go to fixed coordinates on the control
column; everything else is packed into named zones next to the circuit it belongs to. Pads get their
nets from the KiCad netlist, and each footprint is linked to its schematic symbol (path = /<uuid>),
so "Update PCB from Schematic" works afterwards. No tracks: routing is done in KiCad.
Coordinates in mm; y = 0 is the rear edge (jacks), y grows towards the operator (fader)."""
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

W, L = 38.0, 480.0            # board: 40 mm strip pitch, 1 mm clearance each side
COL = 19.0                    # control column (knob / actuator centre line)

# ---------------------------------------------------------------- fixed parts: ref -> (x, y, rotation, side)
# x, y are the footprint origin; the comments give the feature that lands on the panel grid.
FIX = {
 # NRJ6HF, nose to the rear edge: body face (local x 16.95) on y = 0, nose centres at x = 10 and 28
 'J1': (10 - 7.23, 16.95, 90, 'F'), 'J2': (28 - 7.23, 16.95, 90, 'F'),
 'D2': (COL - 1.27, 84, 0, 'F'),                                   # OL LED, 3 mm
 'CN1': (COL + 1.27, 242, 0, 'B'),       # one bus header, centred, on the bottom: the daisy-chained ribbon runs under the boards
 'SW5': (7 - 2.5, 297 - 3.0, 0, 'F'), 'SW6': (COL - 2.5, 297 - 3.0, 0, 'F'), 'SW7': (31 - 2.5, 297 - 3.0, 0, 'F'),   # L-R, 1-2, 3-4
 'SW3': (12 - 2.5, 314 - 3.0, 0, 'F'), 'D3': (28 - 1.27, 314, 0, 'F'),   # PFL + LED
 'SW4': (12 - 2.5, 331 - 3.0, 0, 'F'), 'D4': (28 - 1.27, 331, 0, 'F'),   # MUTE + LED
 'RV1': (COL - 1.9, 475.75, 270, 'F'),                              # fader: slot centre at y = 412, pin 1 (ground) to the front
 'CN4': (COL, 89.9, 0, 'B'),
 'NT1': (26.5, 86.5, 0, 'F'),            # AGND-LGND net tie, next to the spade (star point of the strip)             # ground spade on the bottom (faston + wire too tall under the panel), between OL LED and aux 1
}
# M3 standoff holes for the panel (11.5 mm standoffs), unplated so audio ground never touches the chassis
HOLES = [(34, 84.5), (5.5, 160), (19, 232.4), (34, 305.5), (5.5, 474.5), (32.5, 474.5)]
for i, ref in enumerate(['RV2', 'RV3', 'RV4', 'RV5', 'RV6', 'RV7']):   # aux 1-6, shafts at 20 mm pitch from y = 100
    FIX[ref] = (COL - 7.5, 100 + 20 * i - 2.5, 0, 'F')
FIX['RV8'] = (COL - 7.5, 222 - 2.5, 0, 'F')                          # pan

# ---------------------------------------------------------------- zones: name -> ((x0, y0, x1, y1), refs in placement order, side)
# Radial electrolytics (D6.3/D8/D10, 11-16 mm tall) go on the bottom side, so the PCB-to-panel gap is set by
# the fader, not by capacitors. Their leads are soldered on top, so no top-side zone overlaps a bottom one.
ZONES = {
 'input receiver + insert':    ((1, 27, 37, 47), ['U1', 'C20', 'C21', 'R6', 'R7', 'C7', 'R8', 'R9', 'R10', 'C8', 'C9',
                                                  'R11', 'R12', 'R13'], 'F'),
 'insert coupling caps (bottom)': ((1, 48, 37, 61), ['C10', 'C11'], 'B'),
 'rail reservoir caps (bottom)':  ((1, 62, 37, 72.6), ['C1', 'C3', 'C5', 'C6'], 'B'),
 'power entry':                ((1, 72.8, 37, 81.6), ['R1', 'R2', 'R3', 'R4', 'R5', 'C2', 'C4'], 'F'),
 'overload detector':          ((24.5, 88, 37, 130), ['U4', 'C26', 'R39', 'D1', 'C12', 'R14', 'R40', 'R41', 'R15'], 'F'),
 'aux source jumpers':         ((1, 88, 10.2, 232), ['JP2', 'JP3', 'JP4'], 'F'),
 'pan buffers':                ((24.5, 132, 37, 180), ['U3', 'C24', 'C25', 'R36', 'R37', 'R35'], 'F'),
 'post + pan coupling caps (bottom)': ((24.5, 181, 37, 233), ['C15', 'C16', 'C17'], 'B'),
 # bus resistors beside the header, each on the side of its header pin (even pins left, odd right) or its switch;
 # bus ends are virtual earth: keep them short (spec 13)
 'bus resistors L':            ((1, 237, 13.8, 288), ['R20', 'R23', 'R25', 'R26', 'R27', 'R28'], 'F'),
 'bus resistors R':            ((24.2, 237, 37, 288), ['R21', 'R22', 'R24', 'R29', 'R30', 'R31'], 'F'),
 'PFL + soft mute':            ((1, 338, 10.6, 470), ['R32', 'R33', 'R34', 'R16', 'Q1', 'R17', 'Q2', 'R42', 'C28', 'R43'], 'F'),
 'fader post-amp':             ((27.4, 338, 37, 418), ['U2', 'C22', 'C23', 'R19', 'C14', 'R38', 'C13', 'JP1', 'R18', 'R44'], 'F'),   # U2A loop local; U2B pan-buffer input comes from the low-Z pan wiper
 'VCA module socket (bottom)': ((27.4, 420, 37, 468), ['J3', 'J4'], 'B'),   # module would stand 12-13 mm tall on top
}
GAP = 0.6

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

placed = set(FIX) | {r for _, (_, refs, _) in ZONES.items() for r in refs}
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

edge_rect(0, 0, W, L)

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

def courtyard_bbox(fp):
    side = pcbnew.B_CrtYd if fp.IsFlipped() else pcbnew.F_CrtYd
    fp.BuildCourtyardCaches()
    poly = fp.GetCourtyard(side)
    bb = poly.BBox() if poly.OutlineCount() else fp.GetBoundingBox(False)
    return (pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetTop()), pcbnew.ToMM(bb.GetRight()), pcbnew.ToMM(bb.GetBottom()))

def flip(fp):
    try: fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    except (AttributeError, TypeError): fp.Flip(fp.GetPosition(), False)

for ref, (x, y, rot, side) in FIX.items():
    fp = load(ref)
    fp.SetOrientationDegrees(rot); fp.SetPosition(pcbnew.VECTOR2I_MM(x, y))
    if side == 'B': flip(fp)

report = []
for zname, ((x0, y0, x1, y1), refs, side) in ZONES.items():
    edge_rect(x0, y0, x1, y1, pcbnew.Dwgs_User, 0.05); note(zname, x0 + 0.3, y0 + 1.2, size=1.0)
    cx, cy, rowh = x0, y0 + 2.0, 0.0                     # leave room for the zone label
    for ref in refs:
        fp = load(ref); fp.SetPosition(pcbnew.VECTOR2I_MM(0, 0))
        if side == 'B': flip(fp)
        l, t, r, b = courtyard_bbox(fp); w, h = r - l, b - t
        if cx + w > x1 and cx > x0: cx, cy, rowh = x0, cy + rowh + GAP, 0.0
        if cx + w > x1 + 0.01: report.append(f'{zname}: {ref} is {w:.1f} mm wide, zone only {x1 - x0:.1f}')
        fp.SetPosition(pcbnew.VECTOR2I_MM(cx - l, cy - t))
        cx += w + GAP; rowh = max(rowh, h)
    if cy + rowh > y1 + 0.01: report.append(f'{zname}: overflows by {cy + rowh - y1:.1f} mm')

for i, (x, y) in enumerate(HOLES, 1):
    h = pcbnew.FootprintLoad(os.path.join(KLIB, 'MountingHole.pretty'), 'MountingHole_3.2mm_M3')
    h.SetFPID(pcbnew.LIB_ID('MountingHole', 'MountingHole_3.2mm_M3')); h.SetReference(f'H{i}'); h.SetValue('M3 standoff 11.5 mm')
    h.SetBoardOnly(True); h.SetExcludedFromBOM(True); h.SetExcludedFromPosFiles(True)
    board.Add(h); h.SetPosition(pcbnew.VECTOR2I_MM(x, y))

# panel-grid notes
for y, txt in ((5, 'REAR APRON: jack noses'), (84, 'OL'), (222, 'PAN'), (262, 'BUS HEADER (bottom side)'),
               (297, 'L-R  1-2  3-4'), (314, 'PFL'), (331, 'MUTE'), (412, 'FADER 100 mm')):
    note(txt, W + 3, y, size=2.0)
pcbnew.SaveBoard(OUT, board)
print(f'placed {len(parts)} footprints on {W:.0f} x {L:.0f} mm; nets {len(netinfo)}')
for r in report: print('  WARNING', r)
