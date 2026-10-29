"""Free spots for a new part on a placed board, by the placer's own guard rules (tools/placer.py check_spot): the
footprint's courtyard against same-side courtyards, every through-hole pad on either side, and its own leads against
everything; the footprint set up exactly as placer.py does it (rotate, position, then flip for the bottom). Use it to
pick the spot of a part that is made last and placed by `moves_only` (CLAUDE.md, Rules); then re-place and check with
tools/placediff.py that only the new parts changed.
usage (KiCad's Python):
  $KPY tools/freespot.py BOARD.kicad_pcb LIB:FOOTPRINT F|B ROT X Y [N]
  e.g. $KPY tools/freespot.py master.kicad_pcb Resistor_SMD:R_0805_2012Metric B 90 9.47 237.25 3
Prints up to N free spots spiralling out from (X, Y), nearest first. Env: OCC="x,y,w,h;..." keeps boxes out (spots
already given to other new parts in the same batch), GAP (mm, default 0.1), RMAX (spiral steps of 0.5 mm, default 100).
Library footprints come from the project (goa-console.pretty) or KiCad's library: $KICAD10_FOOTPRINT_DIR,
$KICAD_FOOTPRINT_DIR, the Linux or the macOS default path.
Caution, learned the hard way: KiCad's THT capacitors (C_Rect, CP_Radial) have pad 1 at the origin, not the body's
centre; this script loads the real footprint, so its answer is right where a centred box would not be."""
import sys, math, os, pcbnew
board = pcbnew.LoadBoard(sys.argv[1]); fpid = sys.argv[2]; side = sys.argv[3]; rot = float(sys.argv[4]); ax, ay = float(sys.argv[5]), float(sys.argv[6])
n = int(sys.argv[7]) if len(sys.argv) > 7 else 3
lib, name = fpid.split(':')
PROJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
CANDIDATES = [PROJ, os.environ.get('KICAD10_FOOTPRINT_DIR', ''), os.environ.get('KICAD_FOOTPRINT_DIR', ''),
              '/usr/share/kicad/footprints', '/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints']
root = next((c for c in CANDIDATES if c and os.path.isdir(os.path.join(c, lib + '.pretty'))), None)
if root is None: sys.exit(f'{lib}.pretty not found in {CANDIDATES}')
root = root.rstrip('/') + '/'
fp = pcbnew.FootprintLoad(root + lib + '.pretty', name)
if fp is None: sys.exit(f'{name} not in {root}{lib}.pretty')
def bbox(r): return (r.GetLeft()/1e6, r.GetTop()/1e6, r.GetRight()/1e6, r.GetBottom()/1e6)
def courtyard(f):
    f.BuildCourtyardCaches(); poly = f.GetCourtyard(pcbnew.B_CrtYd if f.IsFlipped() else pcbnew.F_CrtYd)
    return bbox(poly.BBox() if poly.OutlineCount() else f.GetBoundingBox(False))
def tht(f): return [bbox(p.GetBoundingBox()) for p in f.Pads() if p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH)]
def ov(r, qs, g=0.0): return any(r[0] < q[2] + g and q[0] < r[2] + g and r[1] < q[3] + g and q[1] < r[3] + g for q in qs)
others = []
for f in board.GetFootprints():
    f.BuildCourtyardCaches(); others.append((f.GetReference(), f.IsFlipped(), courtyard(f), tht(f), [bbox(p.GetBoundingBox()) for p in f.Pads()]))
occ = [tuple(map(float, o.split(','))) for o in filter(None, os.environ.get('OCC', '').split(';'))]
occ = [(x - w/2, y - h/2, x + w/2, y + h/2) for x, y, w, h in occ]
eb = bbox(board.GetBoardEdgesBoundingBox()); G = float(os.environ.get('GAP', '0.1'))
PROBE = pcbnew.FootprintLoad(root + lib + '.pretty', name); PROBE.SetReference('PROBE'); board.Add(PROBE)
PROBE.SetOrientationDegrees(rot); PROBE.SetPosition(pcbnew.VECTOR2I_MM(ax, ay))
if side == 'B':
    try: PROBE.Flip(PROBE.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    except (AttributeError, TypeError): PROBE.Flip(PROBE.GetPosition(), False)
def setup(x, y):
    PROBE.SetPosition(pcbnew.VECTOR2I_MM(x, y)); return PROBE
def free(x, y):
    f = setup(x, y); box = courtyard(f); mine = tht(f); flipped = f.IsFlipped()
    if box[0] < eb[0] + 0.5 or box[1] < eb[1] + 0.5 or box[2] > eb[2] - 0.5 or box[3] > eb[3] - 0.5: return 'edge'
    if ov(box, occ, G): return 'occ'
    for ref, ofl, oc, ot, op in others:
        if ofl == flipped and ov(box, [oc], G): return ref
        if ov(box, ot, G): return ref + ':tht'
        if mine and (ov(oc, mine, G) or any(ov(q, mine, G) for q in op)): return ref + ':lead'
    return ''
found = []
for rad in [i * 0.5 for i in range(0, int(os.environ.get('RMAX', '100')))]:
    for ang in range(0, 360, 10):
        x, y = round(ax + rad * math.cos(math.radians(ang)), 2), round(ay + rad * math.sin(math.radians(ang)), 2)
        if free(x, y) == '' and all(math.dist((x, y), q) > 1.0 for q in found):
            found.append((x, y)); print(f'free at ({x}, {y}) {math.dist((x, y), (ax, ay)):.1f} mm from the anchor; box {tuple(round(v, 1) for v in courtyard(setup(x, y)))}')
            if len(found) >= n: sys.exit(0)
print('none found' if not found else '')
