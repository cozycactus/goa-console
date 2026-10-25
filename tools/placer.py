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
  attach  True: every part is placed beside the IC pin it belongs to, found from the netlist's pin types:
         decouplers at their IC's supply pin (NEAR, or the IC before them in the zone), parts on an input, feedback or
         summing net at that input pin, output networks at the output pin, and parts joined only to such a part next
         to it. Each IC is placed with room around it and followed at once by its parts.
  limits  (decoupling, input reach) in mm for the placement report (default 5, 6).
  keepout  [(x0, y0, x1, y1)] areas kept free of parts on both sides, or [(x0, y0, x1, y1, side)] on one side.
After placing, the report gives each decoupler's distance to its supply pin and, per local high-impedance input net
(an IC input not driven by an output directly or through a coupling cap, not a connector line or a reference shared
by three or more inputs), the farthest R/C/L/D/FB/JP pad from the pin.
Fixed parts go first. Every other part is packed into its zone at the first position where its courtyard
clears every courtyard on its side and every through-hole pad on either side (THT pads go through the board),
so top and bottom parts can share an area. Then the silkscreen references are placed. Each footprint is linked
to its schematic symbol, so "Update PCB from Schematic" works later. Refuses to overwrite a routed board."""
import collections, re, math, os, sys
import pcbnew
sys.path.insert(0, os.path.dirname(__file__))
from verify import sexp, field
import netnames

PROJ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
KLIB = '/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/'
if not os.path.isdir(KLIB): KLIB = '/usr/share/kicad/footprints/'
GAP, STEP = 0.3, 0.5          # packer clearance between courtyards / pads, search step

# ---------------------------------------------------------------- 8 HP module frame, shared by strip, group and master
# y = 0 is 11 mm below the panel's top edge; panel x = board x + 1.15. Every module puts its fader, bus header and
# ground spade at the same coordinates, so the daisy-chained ribbon and the faders line up across the console.
W8 = 38.0                     # board width of an 8 HP module (40.64 mm pitch)
XL, XR, XC = 8.84, 29.16, 19.0  # pot columns and centre line: 20.32 mm pitch within and across modules (40.64 / 2)
FADER = (XC - 1.9, 372 + 63.75, 270, 'F')   # PTB0143/4: slot centre (19, 372), 100 mm travel
BUS = (31.46, 345.64, 180, 'B')             # 2x17 bus header, bottom side, pins x 31.46 / 34, y 305-346
SPADE, NETTIE = (5.0, 358.0, 0, 'B'), (5.0, 351.0, 0, 'F')
FADER_HOLES = [(5, 330), (5, 425), (34, 425)]

def pot(x, y, dual=False, right=None, sx=7.5):
    """RD901F/RD902F with the shaft at (x, y): shaft at (sx, 2.5) from pin 1 (7.5; the ALPS RK09L dual: 10). Every pot turns its pins towards the
    module's centre line (at x 8.84 / 29.16 outward pins would sit 1.3 mm from the board edge): left column 180 deg,
    right column 0 deg, so a dual's second row of pins also lies inboard. right: column, by default from x."""
    if right is None: right = x % 40.64 > XC
    return (x - sx, y - 2.5, 0, 'F') if right else (x + sx, y + 2.5, 180, 'F')
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
    GROUNDS = {v for g in L.get('grounds', ('GNDA', 'GNDD')) for v in (g.lstrip('/'), '/' + g.lstrip('/'))}  # with or without '/'
    SILK_OFF = set(L.get('silk_text_off', ()))
    ATTACH = L.get('attach', False)
    W = BOARD[2]
    # ---------------------------------------------------------------- netlist
    tree = sexp(open(NET).read())
    comps = next(c for c in tree[1:] if isinstance(c, list) and c[0] == 'components')
    nets = next(c for c in tree[1:] if isinstance(c, list) and c[0] == 'nets')
    parts = {}
    for c in comps[1:]:
        ts = next((x for x in c[1:] if isinstance(x, list) and x[0] == 'tstamps'), None)
        sp = next((x for x in c[1:] if isinstance(x, list) and x[0] == 'sheetpath'), None)
        props = {field(x, 'name'): field(x, 'value') for x in c[1:] if isinstance(x, list) and x[0] == 'property'}
        # the symbol's full path: its sheet's tstamps ('/' on a flat sheet, '/<sheet uuid>/' on a hierarchical page) and
        # its own uuid; KiCad links a footprint to its symbol by this path, so a flat '/uuid' breaks the link
        sheet = field(sp, 'tstamps') if sp else '/'
        parts[field(c, 'ref')] = dict(value=field(c, 'value'), fp=field(c, 'footprint'), uuid=ts[1] if ts else None,
                                      path=(sheet + ts[1]) if ts else None, sheetname=props.get('Sheetname', ''),
                                      sheetfile=props.get('Sheetfile', ''),
                                      mpn=props.get('MPN'), dnp='dnp' in props, nobom='exclude_from_bom' in props)
    SHOW = netnames.renames(NET)          # report names for a drawn schematic's unlabelled nets (the pads keep KiCad's)
    padnet, pintype = {}, {}
    for n in nets[1:]:
        name = field(n, 'name')
        for nd in n[1:]:
            if isinstance(nd, list) and nd[0] == 'node':
                padnet[(field(nd, 'ref'), field(nd, 'pin'))] = name; pintype[(field(nd, 'ref'), field(nd, 'pin'))] = field(nd, 'pintype')

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
        if os.path.exists(os.path.join(PROJ, 'goa-console.3dshapes', name + '.wrl')):     # our model (tools/models3d)
            fp.Models().clear(); m = pcbnew.FP_3DMODEL()                                     # for a part KiCad has none for
            m.m_Filename = '${KIPRJMOD}/goa-console.3dshapes/' + name + '.wrl'; fp.Models().push_back(m)
        fp.SetReference(ref); fp.SetValue(p['value'])
        if p['path']: fp.SetPath(pcbnew.KIID_PATH(p['path']))
        if p['sheetfile']: fp.SetSheetname(p['sheetname']); fp.SetSheetfile(p['sheetfile'])
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

    # occupancy per side on a 5 mm grid: courtyards, plus the THT pads of parts on the other side
    OCELL = 5.0
    occ = {'F': {}, 'B': {}}
    def occupy(side, r):
        for cx in range(int(r[0] // OCELL), int(r[2] // OCELL) + 1):
            for cy in range(int(r[1] // OCELL), int(r[3] // OCELL) + 1):
                occ[side].setdefault((cx, cy), []).append(r)
    def hits(side, r, g):
        x0, y0, x1, y1 = r[0] - g, r[1] - g, r[2] + g, r[3] + g
        for cx in range(int(x0 // OCELL), int(x1 // OCELL) + 1):
            for cy in range(int(y0 // OCELL), int(y1 // OCELL) + 1):
                for q in occ[side].get((cx, cy), ()):
                    if x0 < q[2] and q[0] < x1 and y0 < q[3] and q[1] < y1: return True
        return False
    def overlaps(r, rects, g=GAP):
        return any(r[0] < q[2] + g and q[0] < r[2] + g and r[1] < q[3] + g and q[1] < r[3] + g for q in rects)
    def register(fp, side):
        other = 'B' if side == 'F' else 'F'
        occupy(side, courtyard(fp))
        for pr in tht_pads(fp): occupy(other, pr)

    # silkscreen labels first: the packer treats them as occupied, so parts don't land on them
    label_items = []
    for x, y, txt, size in LABELS:
        t = pcbnew.PCB_TEXT(board); t.SetText(txt); t.SetPosition(pcbnew.VECTOR2I_MM(x, y)); t.SetLayer(pcbnew.F_SilkS)
        t.SetTextSize(pcbnew.VECTOR2I_MM(size, size)); t.SetTextThickness(pcbnew.FromMM(max(0.12, size * 0.15)))
        board.Add(t); label_items.append(t); occupy('F', bbox(t.GetBoundingBox()))
    for ref, (x, y, rot, side) in FIX.items():
        fp = load(ref)
        fp.SetOrientationDegrees(rot); fp.SetPosition(pcbnew.VECTOR2I_MM(x, y))
        if side == 'B': flip(fp)
        register(fp, side)
        if 'PVA2' in fp.GetFPIDAsString():              # orientation mark (design_review.md R4): the moulded "2" goes
            pads = {p.GetNumber(): p.GetPosition() for p in fp.Pads()}       # in the pad 1/4 column (spec 16.1)
            p1, p3, p4 = pads['1'], pads['3'], pads['4']
            ux, uy = p1.x - p3.x, p1.y - p3.y; n = math.hypot(ux, uy)
            mx, my = (p1.x + p4.x) / 2 + ux / n * pcbnew.FromMM(1.6), (p1.y + p4.y) / 2 + uy / n * pcbnew.FromMM(1.6)   # inside the switch outline: no new area
            t = pcbnew.PCB_TEXT(board); t.SetText('2'); t.SetPosition(pcbnew.VECTOR2I(int(mx), int(my)))
            t.SetLayer(pcbnew.F_SilkS if side == 'F' else pcbnew.B_SilkS); t.SetMirrored(side == 'B')
            t.SetTextSize(pcbnew.VECTOR2I_MM(1.0, 1.0)); t.SetTextThickness(pcbnew.FromMM(0.15))
            board.Add(t); label_items.append(t); occupy(side, bbox(t.GetBoundingBox()))
    for k in L.get('keepout', ()):                      # areas no part may use (supply channels, wire entries)
        for sd in (k[4:] or ('F', 'B')): occupy(sd, k[:4])
        edge_rect(*k[:4], pcbnew.Cmts_User, 0.05)
    for i, (x, y) in enumerate(HOLES, 1):
        h = pcbnew.FootprintLoad(os.path.join(KLIB, 'MountingHole.pretty'), 'MountingHole_3.2mm_M3')
        h.SetFPID(pcbnew.LIB_ID('MountingHole', 'MountingHole_3.2mm_M3')); h.SetReference(f'H{i}'); h.SetValue(HOLE_VALUE)
        h.SetBoardOnly(True); h.SetExcludedFromBOM(True); h.SetExcludedFromPosFiles(True)
        board.Add(h); h.SetPosition(pcbnew.VECTOR2I_MM(x, y))
        c = courtyard(h); occupy('F', c); occupy('B', c)

    # ---------------------------------------------------------------- what belongs where (netlist pin types)
    pins_of = collections.defaultdict(list)            # ref -> [(pin, net, pin type)]
    for (r, pn), n in padnet.items(): pins_of[r].append((pn, n, pintype.get((r, pn), '')))
    rails = {n for (r, pn), n in padnet.items() if pintype.get((r, pn)) == 'power_in'} - GROUNDS
    quiet = lambda n: n is None or n in GROUNDS or n in rails or n.startswith('unconnected')
    active = {r for r, ps in pins_of.items() if any(t in ('input', 'output', 'open_collector') for _, _, t in ps)}
    out_pins = {r: [(pn, n) for pn, n, t in pins_of[r] if t in ('output', 'open_collector') and not quiet(n)] for r in active}
    driven = {n for r in active for _, n in out_pins[r]}       # an input on an output's net is not a high-Z node,
    def ohms(v):                                       # '47R' / '2R2' / '1K' -> ohms (None if not a plain value)
        m = re.fullmatch(r'(\d+)([RK])(\d*)', v.split()[0]) if v else None
        return m and float(m.group(1) + '.' + (m.group(3) or '0')) * (1e3 if m.group(2) == 'K' else 1)
    for (r, pn), n in list(padnet.items()):            # nor one behind an output's build-out resistor (<= 100 ohm)
        if r.startswith('R') and not r.startswith('RV') and n in driven and (ohms(parts[r]['value']) or 1e9) <= 100:
            other = padnet.get((r, '2' if pn == '1' else '1'))
            if other and not quiet(other): driven.add(other)
    def coupled(net):                                  # nor one fed through a coupling cap from an output
        for (r, pn), n in padnet.items():
            if n == net and r.startswith('C') and 'u' in parts[r]['value'].split()[0]:
                if any(padnet.get((r, q)) in driven for q in ('1', '2') if q != pn): return True
        return False
    in_pins = {r: [(pn, n) for pn, n, t in pins_of[r] if t == 'input' and not quiet(n) and n not in driven and not coupled(n)]
               for r in active}
    sup_pins = {r: [(pn, n) for pn, n, t in pins_of[r] if t == 'power_in' and n in rails] for r in active}
    nets_of = lambda r: {n for _, n, _ in pins_of[r] if not quiet(n)}
    attach = {}                                        # ref -> (kind, target ref, target pin or None)
    positional = lambda r: r.startswith(('CN', 'J', 'SW', 'RV', 'K', 'NT', 'H')) and not r.startswith('JP')   # stay put
    for z in ZONES:
        refs = z[2]; here = [r for r in refs if r in active]
        for r in refs:
            if r in active and r not in NEAR: continue
            alln = {n for _, n, _ in pins_of[r]}; rl = [n for n in alln if n in rails]
            decoupler = r.startswith('C') and len(rl) == 1 and not (alln - set(rl) - GROUNDS)
            if r in NEAR:
                a = NEAR[r]
                sp = [pn for pn, n in sup_pins.get(a, ()) if decoupler and n == rl[0]]
                attach[r] = ('decouple', a, sp[0]) if (ATTACH and sp) else ('near', a, None); continue
            if not ATTACH or positional(r): continue
            if decoupler:
                cand = [a for a in here if any(n == rl[0] for _, n in sup_pins[a])]
                before = [a for a in cand if refs.index(a) < refs.index(r)]
                if cand:
                    a = (before or cand)[-1 if before else 0]
                    attach[r] = ('decouple', a, next(pn for pn, n in sup_pins[a] if n == rl[0]))
                continue
            ns = nets_of(r)
            for kind, table in (('input', in_pins), ('output', out_pins)):
                for pool in (here, sorted(active)):
                    hit = [(a, pn) for a in pool for pn, n in table[a] if n in ns]
                    if hit: attach[r] = (kind, *hit[0]); break
                if r in attach: break
        if ATTACH:                                     # parts joined only to an attached part go next to it
            grew = True
            while grew:
                grew = False
                for r in refs:
                    if r in active or r in attach or positional(r): continue
                    q = next((q for q in refs if q != r and q in attach and nets_of(r) & nets_of(q)), None)
                    if q: attach[r] = ('chain', q, None); grew = True
    PRIORITY = {'decouple': 0, 'near': 1, 'input': 1, 'output': 2, 'chain': 3}
    def ordered(refs):
        out, seen = [], set()
        def emit(r):
            if r in seen: return
            seen.add(r); out.append(r)
            for q in sorted((q for q in refs if q not in seen and attach.get(q, ('', None))[1] == r),
                            key=lambda q: PRIORITY[attach[q][0]]):
                emit(q)
        for r in refs:
            if r in active or (r in attach and attach[r][1] not in refs): emit(r)
        for r in refs: emit(r)
        return out
    kids = collections.Counter(t for kind, t, _ in attach.values() if kind != 'chain')
    zone_side = {r: z[3] for z in ZONES for r in z[2]}
    AREA = {}
    def fp_area(ref):                                  # courtyard area of a footprint, plus the packing gap
        key = parts[ref]['fp']
        if key not in AREA:
            lib, name = key.split(':', 1)
            f = pcbnew.FootprintLoad(os.path.join(PROJ, lib + '.pretty') if lib == 'goa-console' else os.path.join(KLIB, lib + '.pretty'), name)
            l, t, r, b = courtyard(f); AREA[key] = (r - l + GAP) * (b - t + GAP)
        return AREA[key]
    def ring(ref, w, h):
        """Free margin an IC keeps around its courtyard: enough for its own same-side parts at 70 % packing."""
        need = sum(fp_area(q) for q, (kind, t, _) in attach.items() if t == ref and zone_side.get(q) == zone_side.get(ref)) / 0.7
        return 0.0 if not need else (-(w + h) + math.sqrt((w + h) ** 2 + 4 * need)) / 4

    def target_xy(ref, fp):
        """Where a part wants to be: its IC pin (attach), or NEAR's first pad on a shared non-ground net."""
        a = attach.get(ref)
        if not a: return None
        kind, tref, tpin = a
        t = board.FindFootprintByReference(tref)
        if t is None: return None
        if tpin is not None:
            pad = next((p for p in t.Pads() if p.GetNumber() == tpin), None)
            return (mm(pad.GetPosition().x), mm(pad.GetPosition().y)) if pad else None
        nets = {padnet.get((ref, p.GetNumber())) for p in fp.Pads()} - GROUNDS - {None}
        for p in t.Pads():
            if padnet.get((tref, p.GetNumber())) in nets:
                return mm(p.GetPosition().x), mm(p.GetPosition().y)

    def shape(fp, side, rot):                          # courtyard and THT pads at the origin, translated per candidate.
        fp.SetOrientationDegrees(rot if side == 'F' else 180 - rot)     # KiCad rebuilds a courtyard ~1 nm larger away
        fp.SetPosition(pcbnew.VECTOR2I_MM(0, 0))                        # from the origin, so a part flush with a zone
        return courtyard(fp), tht_pads(fp)                              # edge may now fit one 0.5 mm step earlier
    def fits_at(sh, px, py, side, zr, g):
        (l, t, r, b), pads = sh
        c = (l + px, t + py, r + px, b + py)
        if (c[0] < max(zr[0], BOARD[0] + 0.3) or c[1] < max(zr[1], BOARD[1] + 0.3) or c[2] > min(zr[2], BOARD[2] - 0.3)
                or c[3] > min(zr[3], BOARD[3] - 0.3)): return False
        if hits(side, c, g): return False
        other = 'B' if side == 'F' else 'F'
        return not any(hits(other, (pl + px, pt + py, pr + px, pb + py), g) for pl, pt, pr, pb in pads)

    # Parts with a target go as close to it as the courtyards allow, searched within NEAR_R; anything else, or a part
    # with no room there, takes the zone's first free spot from the top left. An IC with parts of its own keeps a
    # margin free around it until they are placed.
    NEAR_R = 12.0
    report = []
    placed_refs, tried = set(FIX), set(FIX)
    zone_rect = {r: z[1] for z in ZONES for r in z[2]}
    def place_one(ref, z):
        tried.add(ref)
        zname, zr, _, side = z[:4]
        zgap = z[4] if len(z) > 4 else GAP
        fp = load(ref)
        if side == 'B': flip(fp)
        shapes = {rot: shape(fp, side, rot) for rot in (0, 90)}
        (l0, t0, r0, b0), _ = shapes[0]
        margin = min(8.0, ring(ref, r0 - l0, b0 - t0)) if (ATTACH and kids[ref]) else 0.0
        gaps = tuple(sorted({max(zgap, margin), max(zgap, margin / 2), zgap}, reverse=True))   # the ring shrinks when the zone is full
        best = None
        tgt = target_xy(ref, fp)
        zn = zr                                        # an attached part searches around its target wherever that
        if ATTACH and tgt:                             # landed; with no room there it falls back to its own zone
            zn = (min(zr[0], tgt[0] - 30), min(zr[1], tgt[1] - 30), max(zr[2], tgt[0] + 30), max(zr[3], tgt[1] + 30))
        for g in gaps if tgt else ():
            for reach_r in (NEAR_R, 20.0, 30.0) if ATTACH else (NEAR_R,):     # widen when crowded
                n = int(reach_r / STEP); cands = []
                for rot, ((l, t, r, b), _) in shapes.items():
                    for i in range(-n, n + 1):
                        for j in range(-n, n + 1):
                            cx, cy = tgt[0] + i * STEP, tgt[1] + j * STEP           # courtyard centre
                            cands.append((math.hypot(i, j) * STEP, rot, cx - (r - l) / 2 - l, cy - (b - t) / 2 - t))
                best = next(((rot, px, py) for d, rot, px, py in sorted(cands) if fits_at(shapes[rot], px, py, side, zn, g)), None)
                if best: break
            if best: break
        for g in gaps if best is None else ():
            for rot, sh in shapes.items():
                (l, t, r, b), _ = sh
                y = zr[1]
                while y + (b - t) <= zr[3] and best is None:
                    x = zr[0]
                    while x + (r - l) <= zr[2]:
                        if fits_at(sh, x - l, y - t, side, zr, g): best = (rot, x - l, y - t); break
                        x += STEP
                    y += STEP
                if best: break
            if best: break
        if best:
            rot, px, py = best
            fp.SetOrientationDegrees(rot if side == 'F' else 180 - rot); fp.SetPosition(pcbnew.VECTOR2I_MM(px, py))
            register(fp, side); placed_refs.add(ref)
        else:
            report.append(f'{zname}: no room for {ref}')
            fp.SetPosition(pcbnew.VECTOR2I_MM(BOARD[2] + 10, zr[1]))   # parked off-board so DRC flags it

    # A part whose target is placed later waits for it, then goes right after it, so it can still sit beside it.
    in_zones = {r for z in ZONES for r in z[2]}
    waiting = collections.defaultdict(list)
    def settle(ref):
        for r2, z2 in waiting.pop(ref, ()):
            if r2 not in tried: place_one(r2, z2); settle(r2)
    def tht(r):
        lib = parts[r]['fp'].split(':')[0]
        return lib.endswith('_THT') or lib.startswith(('Connector', 'TerminalBlock')) or lib == 'goa-console'
    def stage(r):                                      # attach: connectors and free through-hole parts (they need room
        if not ATTACH: return 0                        # on both sides), then ICs with their decouplers, input networks
        if r not in attach and (positional(r) or tht(r)): return 0     # and through-hole parts, then the other output
        if r in active or attach.get(r, ('',))[0] in ('decouple', 'input', 'near') or tht(r): return 1   # networks and
        return 2 if r in attach else 3                 # chains, then the rest
    for z in ZONES: edge_rect(*z[1], pcbnew.Dwgs_User if z[3] == 'F' else pcbnew.Cmts_User, 0.05)
    for st in (0, 1, 2, 3) if ATTACH else (0,):
        for z in ZONES:
            for ref in (ordered(z[2]) if ATTACH else z[2]):
                if stage(ref) != st or ref in tried: continue
                t = attach.get(ref, (None, None))[1]
                if ATTACH and t in in_zones and t not in placed_refs:
                    if (ref, z) not in waiting[t]: waiting[t].append((ref, z))
                    continue
                place_one(ref, z); settle(ref)
    for t in list(waiting):                            # targets that could not be placed: place the rest anyway
        for r2, z2 in waiting.pop(t, ()):
            if r2 not in tried: place_one(r2, z2); settle(r2)

    # ---------------------------------------------------------------- placement report
    LIM_DEC, LIM_IN = L.get('limits', (5.0, 6.0))
    def pad_of(ref, net):
        f = board.FindFootprintByReference(ref)
        return [(mm(p.GetPosition().x), mm(p.GetPosition().y)) for p in f.Pads() if padnet.get((ref, p.GetNumber())) == net]
    dec = []
    for r, (kind, a, _) in attach.items():
        if a not in active or not r.startswith('C'): continue
        alln = {n for _, n, _ in pins_of[r]}; rl = [n for n in alln if n in rails]
        if len(rl) != 1 or (alln - set(rl) - GROUNDS) or kind not in ('decouple', 'near'): continue
        ic = board.FindFootprintByReference(a)
        pins_xy = [(mm(p.GetPosition().x), mm(p.GetPosition().y)) for p in ic.Pads() if padnet.get((a, p.GetNumber())) == rl[0]]
        cap_xy = pad_of(r, rl[0])
        if pins_xy and cap_xy: dec.append((min(math.dist(u, v) for u in pins_xy for v in cap_xy), f'{r}->{a}'))
    outnets = driven
    passive = lambda r: r not in active and (r.startswith(('FB', 'JP')) or (r[0] in 'RCLD' and not r.startswith(('RV', 'CN'))))
    inputs_on = collections.Counter(n for a in active for _, n in in_pins[a])
    members = collections.defaultdict(set)
    for (r, pn), n in padnet.items(): members[n].add(r)
    reach = []
    for a in sorted(active):
        ic = board.FindFootprintByReference(a)
        for pn, n in in_pins[a]:
            if n in outnets or coupled(n) or inputs_on[n] >= 3: continue      # low-Z, or a shared reference line
            if any(r.startswith(('CN', 'J')) and not r.startswith('JP') for r in members[n]): continue   # off-board
            pin_xy = next(((mm(p.GetPosition().x), mm(p.GetPosition().y)) for p in ic.Pads() if p.GetNumber() == pn), None)
            far = [(min(math.dist(pin_xy, v) for v in pad_of(r, n)), r) for r in members[n] if passive(r)]
            if far: reach.append((max(far)[0], f'{a}.{pn} {SHOW.get(n.lstrip("/"), n.lstrip("/"))} {max(far)[1]}'))
    def summary(rows, lim, what):
        if not rows: return f'{what}: none'
        ds = sorted(x[0] for x in rows); bad = sorted((x for x in rows if x[0] > lim), reverse=True)
        return (f'{what}: {len(rows)}, median {ds[len(ds) // 2]:.1f} mm, max {ds[-1]:.1f} mm, over {lim:g} mm: {len(bad)}'
                + ('' if not bad else '  (worst: ' + '; '.join(f'{x[1]} {x[0]:.1f}' for x in bad[:6]) + ')'))
    stats = dict(decoupling=sorted(dec, reverse=True), input_reach=sorted(reach, reverse=True))

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
    print('  ' + summary(stats['decoupling'], LIM_DEC, 'decouplers, cap pad to supply pin'))
    print('  ' + summary(stats['input_reach'], LIM_IN, 'high-Z inputs, farthest R/C/L/D/FB/JP pad from the pin'))
    if os.environ.get('PLACER_REPORT'):                 # every row over its limit, for layout work
        for key, lim in (('decoupling', LIM_DEC), ('input_reach', LIM_IN)):
            print(f'  {key} over {lim:g} mm: ' + '; '.join(f'{x[1]} {x[0]:.1f}' for x in stats[key] if x[0] > lim))
    return report, hidden, stats
