"""Placement engine for the goa-console boards (KiCad 10 pcbnew API). Placement only: no copper.
place(net, out, layout) builds a board from a KiCad netlist and a layout:
  board  (x0, y0, x1, y1) outline;  fix {ref: (x, y, rot, 'F'|'B')} at fixed coordinates;
  holes  [(x, y)] M3 mounting holes, hole_value their value;  zones [(name, (x0, y0, x1, y1), [refs], side[, gap])],
         gap = courtyard spacing in that zone (default GAP; more leaves room for the silk references);
  near   {ref: IC} parts placed beside the IC's pin on a shared non-ground net;  notes [(y, text)] beside the board;
  labels [(x, y, text, size)] silkscreen text on the top side (the reference pass keeps clear of them);
  grounds  nets ignored when matching a near part to its IC's pin (default GNDA, GNDD).
  silk_text_off  footprint silk texts moved to the Fab layer, e.g. ('K',): DO-35's cathode letter sits outside
         the courtyard, over the next part's pads (KiCad 10 doesn't save a hidden footprint text).
Fixed parts go first. Every other part is packed into its zone at the first position where its courtyard
clears every courtyard on its side and every through-hole pad on either side (THT pads go through the board),
so top and bottom parts can share an area. Then the silkscreen references are placed. Each footprint is linked
to its schematic symbol, so "Update PCB from Schematic" works later. Refuses to overwrite a routed board."""
import math, os, sys
import pcbnew
sys.path.insert(0, os.path.dirname(__file__))
from verify import sexp, field

PROJ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
KLIB = '/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/'
if not os.path.isdir(KLIB): KLIB = '/usr/share/kicad/footprints/'
GAP, STEP = 0.3, 0.5          # packer clearance between courtyards / pads, search step

# ---------------------------------------------------------------- 8 HP module frame, shared by strip, group and master
# y = 0 is 11 mm below the panel's top edge; panel x = board x + 1.15. Every module puts its fader, bus header and
# ground spade at the same coordinates, so the daisy-chained ribbon and the faders line up across the console.
W8 = 38.0                     # board width of an 8 HP module (40.64 mm pitch)
XL, XR, XC = 10.0, 28.0, 19.0 # pot columns and centre line
FADER = (XC - 1.9, 372 + 63.75, 270, 'F')   # PTB0143/4: slot centre (19, 372), 100 mm travel
BUS = (31.46, 345.64, 180, 'B')             # 2x17 bus header, bottom side, pins x 31.46 / 34, y 305-346
SPADE, NETTIE = (5.0, 358.0, 0, 'B'), (5.0, 351.0, 0, 'F')
FADER_HOLES = [(5, 330), (5, 425), (34, 425)]

def pot(x, y, dual=False, right=False):
    """RD901F/RD902F with the shaft at (x, y): shaft at (7.5, 2.5) from pin 1. Single pots in the right column turn
    180 deg (body to the board edge); dual pots stay at 0 deg on the right (their second gang would hang off the
    edge) and turn 180 deg on the left."""
    rot = 180 if (right and not dual) or (dual and not right) else 0
    return (x + 7.5, y + 2.5, 180, 'F') if rot == 180 else (x - 7.5, y - 2.5, 0, 'F')
sw = lambda x, y: (x - 2.5, y - 3.0, 0, 'F')          # PVA2: actuator centre at (2.5, 3.0) from pin 1
led = lambda x, y: (x - 1.27, y, 0, 'F')               # 3 mm LED: centre at (1.27, 0)
jack = lambda x, y: (x, y - 5.72, 0, 'F')              # NJ6FD-V: nose centre at (0, 5.72) from the tip pin

def place(NET, OUT, L):
    # Preserve any later manual routing. Rebuild into a separate file once routing has started.
    if os.path.exists(OUT):
        old = sexp(open(OUT).read())
        copper = [item[0] for item in old[1:] if isinstance(item, list) and
                  item and item[0] in ('segment', 'arc', 'via', 'zone')]
        if copper:
            raise SystemExit(f'{OUT}: contains routing or zones; choose a separate placement output')
    BOARD, FIX, HOLES, ZONES = L['board'], L['fix'], L.get('holes', []), L['zones']
    HOLE_VALUE, NEAR, NOTES = L.get('hole_value', 'M3'), L.get('near', {}), L.get('notes', ())
    LABELS = L.get('labels', ())
    GROUNDS = set(L.get('grounds', ('GNDA', 'GNDD')))   # nets ignored when matching a NEAR part to its IC pin
    SILK_OFF = set(L.get('silk_text_off', ()))
    W = BOARD[2]
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

    every = list(FIX) + [r for z in ZONES for r in z[2]]
    placed = set(every); twice = sorted({r for r in every if every.count(r) > 1})
    missing = sorted(set(parts) - placed); extra = sorted(placed - set(parts))
    if missing or extra or twice:
        raise SystemExit(f'placement table out of date: unplaced {missing}, unknown {extra}, twice {twice}')

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
        for g in fp.GraphicalItems():               # loaded unflipped: silk texts are on F.SilkS
            t = g.Cast()
            if SILK_OFF and isinstance(t, pcbnew.PCB_TEXT) and t.GetLayer() == pcbnew.F_SilkS and t.GetText() in SILK_OFF:
                t.SetLayer(pcbnew.F_Fab)
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

    # silkscreen labels first: the packer treats them as occupied, so parts don't land on them
    label_items = []
    for x, y, txt, size in LABELS:
        t = pcbnew.PCB_TEXT(board); t.SetText(txt); t.SetPosition(pcbnew.VECTOR2I_MM(x, y)); t.SetLayer(pcbnew.F_SilkS)
        t.SetTextSize(pcbnew.VECTOR2I_MM(size, size)); t.SetTextThickness(pcbnew.FromMM(max(0.12, size * 0.15)))
        board.Add(t); label_items.append(t); occ['F'].append(bbox(t.GetBoundingBox()))
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

    def fits(fp, side, x0, y0, x1, y1, g=GAP):
        other = 'B' if side == 'F' else 'F'
        c = courtyard(fp)
        if (c[0] < max(x0, BOARD[0] + 0.3) or c[1] < max(y0, BOARD[1] + 0.3) or c[2] > min(x1, BOARD[2] - 0.3)
                or c[3] > min(y1, BOARD[3] - 0.3)): return False
        if overlaps(c, occ[side], g): return False
        pads = tht_pads(fp)
        return not (pads and any(overlaps(p, occ[other], g) for p in pads))

    # Parts in NEAR (decoupling caps, integrator parts) go as close as the courtyards allow to their IC's pin on a
    # shared non-ground net, searched within NEAR_R of it; anything else, or a part with no room there, takes the
    # zone's first free spot from the top left.
    NEAR_R = 12.0
    def supply_pin(ref, fp):
        ic = board.FindFootprintByReference(NEAR.get(ref, ''))
        if ic is None: return None
        nets = {padnet.get((ref, p.GetNumber())) for p in fp.Pads()} - GROUNDS - {None}
        for p in ic.Pads():
            if padnet.get((ic.GetReference(), p.GetNumber())) in nets:
                return mm(p.GetPosition().x), mm(p.GetPosition().y)

    report = []
    for z in ZONES:
        zname, (x0, y0, x1, y1), refs, side = z[:4]
        zgap = z[4] if len(z) > 4 else GAP
        edge_rect(x0, y0, x1, y1, pcbnew.Dwgs_User if side == 'F' else pcbnew.Cmts_User, 0.05)
        for ref in refs:
            fp = load(ref)
            if side == 'B': flip(fp)
            done = False
            tgt = supply_pin(ref, fp)
            if tgt:
                cands = []
                for rot in (0, 90):
                    fp.SetOrientationDegrees(rot if side == 'F' else 180 - rot)
                    fp.SetPosition(pcbnew.VECTOR2I_MM(0, 0))
                    l, t, r, b = courtyard(fp)
                    n = int(NEAR_R / STEP)
                    for i in range(-n, n + 1):
                        for j in range(-n, n + 1):
                            cx, cy = tgt[0] + i * STEP, tgt[1] + j * STEP     # courtyard centre
                            cands.append((math.hypot(i, j) * STEP, rot, cx - (r - l) / 2 - l, cy - (b - t) / 2 - t))
                for d, rot, px, py in sorted(cands):
                    fp.SetOrientationDegrees(rot if side == 'F' else 180 - rot)
                    fp.SetPosition(pcbnew.VECTOR2I_MM(px, py))
                    if fits(fp, side, x0, y0, x1, y1, zgap):
                        done = True; break
            for rot in (0, 90) if not done else ():
                fp.SetOrientationDegrees(rot if side == 'F' else 180 - rot)
                fp.SetPosition(pcbnew.VECTOR2I_MM(0, 0))
                l, t, r, b = courtyard(fp)
                y = y0
                while y + (b - t) <= y1 and not done:
                    x = x0
                    while x + (r - l) <= x1:
                        fp.SetPosition(pcbnew.VECTOR2I_MM(x - l, y - t))
                        if fits(fp, side, x0, y0, x1, y1, zgap):
                            done = True; break
                        x += STEP
                    if not done: y += STEP
                if done: break
            if done: register(fp, side)
            else:
                report.append(f'{zname}: no room for {ref}')
                fp.SetPosition(pcbnew.VECTOR2I_MM(BOARD[2] + 10, y0))   # parked off-board so DRC flags it

    # ---------------------------------------------------------------- silkscreen reference designators
    # 0.8 mm text (board minimum), at the nearest spot that clears pads (mask openings), other silk, other
    # references and the board edge. Pass 1 also keeps the text off other parts' courtyards, so it stays
    # readable after assembly; pass 2 drops that; if nothing fits, the silk reference is hidden (the Fab layer
    # keeps ${REFERENCE}). Big parts try their own body first.
    SILK_H, SILK_T, SILK_GAP, MASK_GAP, EDGE_GAP, REACH = 0.8, 0.12, 0.15, 0.1, 0.5, 5.0
    F = pcbnew.FromMM
    fps = list(board.GetFootprints())           # mounting holes too: their labels must clear the parts
    CELL = 5.0
    grid = {'F': {}, 'B': {}}      # side -> cell -> [(bbox, shape, clearance, owner)]
    def add_obstacle(side, item, shape, clearance, owner):
        l, t, r, b = bbox(item.GetBoundingBox())
        for cx in range(int(l // CELL), int(r // CELL) + 1):
            for cy in range(int(t // CELL), int(b // CELL) + 1):
                grid[side].setdefault((cx, cy), []).append(((l, t, r, b), shape, clearance, owner))
    for t in label_items:
        add_obstacle('F', t, t.GetEffectiveShape(pcbnew.F_SilkS), SILK_GAP, None)
    for f in board.GetFootprints():
        for side, silk, cu in (('F', pcbnew.F_SilkS, pcbnew.F_Cu), ('B', pcbnew.B_SilkS, pcbnew.B_Cu)):
            for g in f.GraphicalItems():
                if g.GetLayer() == silk: add_obstacle(side, g, g.GetEffectiveShape(silk), SILK_GAP, f)
            for p in f.Pads():
                if p.IsOnLayer(cu) or p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
                    add_obstacle(side, p, p.GetEffectiveShape(cu), MASK_GAP, f)
    crt = {'F': [(courtyard(f), f) for f in board.GetFootprints() if not f.IsFlipped()],
           'B': [(courtyard(f), f) for f in board.GetFootprints() if f.IsFlipped()]}
    crt['F'] += [(bbox(t.GetBoundingBox()), None) for t in label_items]   # refs keep off whole labels, not just strokes

    def ref_clear(f, side, strict):
        ref = f.Reference(); silk = ref.GetLayer()
        l, t, r, b = bbox(ref.GetBoundingBox())
        if l < BOARD[0] + EDGE_GAP or t < BOARD[1] + EDGE_GAP or r > BOARD[2] - EDGE_GAP or b > BOARD[3] - EDGE_GAP:
            return False
        if strict and overlaps((l, t, r, b), [c for c, o in crt[side] if o is not f], 0): return False
        shape = None
        seen = set()
        for cx in range(int((l - 1) // CELL), int((r + 1) // CELL) + 1):
            for cy in range(int((t - 1) // CELL), int((b + 1) // CELL) + 1):
                for ob in grid[side].get((cx, cy), ()):
                    if id(ob) in seen or not overlaps((l, t, r, b), [ob[0]], ob[2] + 0.05): continue
                    seen.add(id(ob))
                    shape = shape or ref.GetEffectiveShape(silk)
                    if shape.Collide(ob[1], F(ob[2])): return False
        return True

    hidden = []
    for f in sorted(fps, key=lambda f: -(lambda c: (c[2] - c[0]) * (c[3] - c[1]))(courtyard(f))):
        side = 'B' if f.IsFlipped() else 'F'
        ref = f.Reference(); ref.SetVisible(True)
        ref.SetTextSize(pcbnew.VECTOR2I_MM(SILK_H, SILK_H)); ref.SetTextThickness(F(SILK_T))
        ref.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER); ref.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
        l, t, r, b = courtyard(f); cx0, cy0 = (l + r) / 2, (t + b) / 2
        big = min(r - l, b - t) > 6
        cands = []
        n = int(((max(r - l, b - t) / 2) + REACH) / 0.25)
        for i in range(-n, n + 1):
            for j in range(-n, n + 1):
                x, y = cx0 + i * 0.25, cy0 + j * 0.25
                inside = l < x < r and t < y < b
                if not inside and (x < l - REACH or x > r + REACH or y < t - REACH or y > b + REACH): continue
                for ang in (0, 90):
                    d = math.hypot(x - cx0, y - cy0) + (1.0 if ang else 0) - (100 if big and inside else 0)
                    cands.append((d, x, y, ang))
        cands.sort()
        done = False
        for strict in (True, False):
            for d, x, y, ang in cands:
                ref.SetTextAngleDegrees(ang); ref.SetPosition(pcbnew.VECTOR2I_MM(x, y))
                if ref_clear(f, side, strict):
                    done = True; break
            if done: break
        if done:
            add_obstacle(side, ref, ref.GetEffectiveShape(ref.GetLayer()), SILK_GAP, f)
        else:
            ref.SetVisible(False); hidden.append(f.GetReference())

    # notes beside the board (board y)
    for y, txt in NOTES:
        note(txt, W + 3, y, size=2.0)

    pcbnew.SaveBoard(OUT, board)
    print(f'placed {len(parts)} footprints + {len(HOLES)} holes on {BOARD[2] - BOARD[0]:.0f} x {BOARD[3] - BOARD[1]:.0f} mm; nets {len(netinfo)}')
    for r in report: print('  WARNING', r)
    if hidden: print(f'  silk reference hidden (no room): {" ".join(sorted(hidden))}')
    return report, hidden
