"""Route selected nets on the channel-strip PCB with a small two-layer grid router (KiCad has none).
Run after place_strip.py and before pour_strip.py, with KiCad's bundled Python:
  .../Python.framework/Versions/3.9/bin/python3 tools/route_strip.py channel_strip.kicad_pcb NET [NET ...]
  (no NET: the ribbon nets, i.e. everything on the bus header except ground)
A* on a 0.1 mm grid, 8-connected, both copper layers. Obstacles are every pad, hole and track of
other nets, inflated by clearance + half the track width, plus the board edge. Vias only where both
layers have room. B.Cu costs more, so the bottom AGND pour stays as whole as possible. Each net is
routed as a minimum spanning tree over its pads. Tracks are locked so later scripts can tell them apart."""
import sys, heapq, math
import pcbnew

PCB = sys.argv[1]
board = pcbnew.LoadBoard(PCB)
MM, TOMM = pcbnew.FromMM, pcbnew.ToMM
W, L, G = 38.0, 480.0, 0.1                 # board and grid (mm)
NX, NY = int(round(W / G)) + 1, int(round(L / G)) + 1
CLR, EDGE = 0.2, 0.5                       # copper clearance, copper-to-edge
VIA_D, VIA_DRILL = 0.8, 0.4
COST_B, COST_VIA = 1.6, 25.0
WIDTH = {'+VBUS': 0.6, '-VBUS': 0.6}
DEFAULT_W = 0.3
# order matters: the nets that must cross the header's pin columns go first
RIBBON = ['MIXR', 'MIXL', 'SUB1', 'SUB2', 'SUB3', 'SUB4', 'AUX1', 'AUX2', 'AUX3', 'AUX4', 'AUX5', 'AUX6',
          'PFL', 'PFLDET', 'GCANCEL', '+VBUS', '-VBUS']
nets = sys.argv[2:] or RIBBON
LAYERS = (pcbnew.F_Cu, pcbnew.B_Cu)

# ---------------------------------------------------------------- copper inventory: (net, layer, rect or circle)
shapes = []          # (netname or None, layer index or None for both, kind, params)
pads_of = {}
full_name = {}                                       # 'MIXL' -> '/MIXL' (label nets carry a leading slash)
for fp in board.GetFootprints():
    for pad in fp.Pads():
        bb = pad.GetBoundingBox()
        r = (TOMM(bb.GetLeft()), TOMM(bb.GetTop()), TOMM(bb.GetRight()), TOMM(bb.GetBottom()))
        net = pad.GetNetname() or None
        lays = [i for i, l in enumerate(LAYERS) if pad.IsOnLayer(l)]
        if pad.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH or not lays:
            lays = [0, 1]; net = '#hole'
        for li in lays: shapes.append((net, li, 'rect', r))
        if net and net != '#hole':
            pads_of.setdefault(net.lstrip('/'), []).append((pad, lays, r))
            full_name[net.lstrip('/')] = net
try: tracks = list(board.GetTracks())
except TypeError: tracks = []
for t in tracks:
    net = t.GetNetname()
    if isinstance(t, pcbnew.PCB_VIA):
        x, y = TOMM(t.GetPosition().x), TOMM(t.GetPosition().y); d = TOMM(t.GetWidth(pcbnew.F_Cu)) if hasattr(t, 'GetWidth') else VIA_D
        for li in (0, 1): shapes.append((net, li, 'seg', (x, y, x, y, d / 2)))
    else:
        li = 0 if t.GetLayer() == pcbnew.F_Cu else 1
        shapes.append((net, li, 'seg', (TOMM(t.GetStart().x), TOMM(t.GetStart().y), TOMM(t.GetEnd().x), TOMM(t.GetEnd().y), TOMM(t.GetWidth()) / 2)))

# ---------------------------------------------------------------- occupancy grids: per layer, cell -> owning net id
net_id = {}
def nid(n):
    if n not in net_id: net_id[n] = len(net_id) + 1
    return net_id[n]
FREE, MULTI = 0, 65535
def new_grid(): return [bytearray(NX * NY * 2), bytearray(NX * NY * 2)]   # uint16 little-endian per cell
def gget(g, i): return g[i * 2] | (g[i * 2 + 1] << 8)
def gset(g, i, v): g[i * 2] = v & 255; g[i * 2 + 1] = v >> 8
def mark(grid, li, net, kind, p, infl):
    v = MULTI if net in (None, '#hole') else nid(net)
    if kind == 'rect':
        x0, y0, x1, y1 = p[0] - infl, p[1] - infl, p[2] + infl, p[3] + infl
        test = None
    else:
        ax, ay, bx, by, hw = p; r = hw + infl
        x0, y0, x1, y1 = min(ax, bx) - r, min(ay, by) - r, max(ax, bx) + r, max(ay, by) + r
        dx, dy = bx - ax, by - ay; ll = dx * dx + dy * dy
        def test(x, y):
            t = 0 if ll == 0 else max(0, min(1, ((x - ax) * dx + (y - ay) * dy) / ll))
            return (x - ax - t * dx) ** 2 + (y - ay - t * dy) ** 2 <= r * r
    g = grid[li]
    for iy in range(max(0, int(y0 / G)), min(NY - 1, int(math.ceil(y1 / G))) + 1):
        for ix in range(max(0, int(x0 / G)), min(NX - 1, int(math.ceil(x1 / G))) + 1):
            if test and not test(ix * G, iy * G): continue
            i = iy * NX + ix; c = gget(g, i)
            if c == FREE: gset(g, i, v)
            elif c != v: gset(g, i, MULTI)

grids = {}           # inflation -> occupancy grid
def grid_for(infl):
    key = round(infl, 3)
    if key not in grids:
        g = new_grid()
        for net, li, kind, p in shapes: mark(g, li, net, kind, p, infl)
        e = EDGE + infl - CLR
        for li in (0, 1):
            for iy in range(NY):
                for ix in range(NX):
                    x, y = ix * G, iy * G
                    if x < e or y < e or x > W - e or y > L - e: gset(g[li], iy * NX + ix, MULTI)
        grids[key] = g
    return grids[key]

def add_shape(net, li, kind, p):
    shapes.append((net, li, kind, p))
    for infl, g in grids.items(): mark(g, li, net, kind, p, infl)

# ---------------------------------------------------------------- A*
DIRS = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0), (1, 1, 1.414), (1, -1, 1.414), (-1, 1, 1.414), (-1, -1, 1.414)]
def route(net, src_cells, dst_cells, w):
    g = grid_for(CLR + w / 2 + G / 2); gv = grid_for(CLR + VIA_D / 2 + G / 2)
    me = nid(net)
    def ok(gg, li, i): c = gget(gg[li], i); return c == FREE or c == me
    dst = set(dst_cells)
    tx = sum(c[1] % NX for c in dst_cells) / len(dst_cells); ty = sum(c[1] // NX for c in dst_cells) / len(dst_cells)
    h = lambda i: math.hypot(i % NX - tx, i // NX - ty) * 0.98
    openq, best, prev = [], {}, {}
    for s in src_cells:
        best[s] = 0.0; heapq.heappush(openq, (h(s[1]), 0.0, s))
    n = 0
    while openq:
        f, cost, s = heapq.heappop(openq)
        if cost > best.get(s, 1e18): continue
        if s in dst:
            path = [s]
            while path[-1] in prev: path.append(prev[path[-1]])
            return path[::-1]
        n += 1
        if n > 3_000_000: return None
        li, i = s; x, y = i % NX, i // NX
        for dx, dy, c in DIRS:
            nx_, ny_ = x + dx, y + dy
            if not (0 <= nx_ < NX and 0 <= ny_ < NY): continue
            j = ny_ * NX + nx_
            if not ok(g, li, j): continue
            if dx and dy and not (ok(g, li, y * NX + nx_) and ok(g, li, ny_ * NX + x)): continue
            t = (li, j); nc = cost + c * (COST_B if li else 1.0)
            if nc < best.get(t, 1e18): best[t] = nc; prev[t] = s; heapq.heappush(openq, (nc + h(j), nc, t))
        t = (1 - li, i)
        if ok(gv, 0, i) and ok(gv, 1, i):
            nc = cost + COST_VIA
            if nc < best.get(t, 1e18): best[t] = nc; prev[t] = s; heapq.heappush(openq, (nc + h(i), nc, t))
    return None

def pad_cells(pad, lays, r):
    cx, cy = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
    rad = 0.35 * min(r[2] - r[0], r[3] - r[1])
    cells = []
    for iy in range(int((cy - rad) / G), int((cy + rad) / G) + 2):
        for ix in range(int((cx - rad) / G), int((cx + rad) / G) + 2):
            if (ix * G - cx) ** 2 + (iy * G - cy) ** 2 <= rad * rad:
                for li in lays: cells.append((li, iy * NX + ix))
    return cells or [(li, int(round(cy / G)) * NX + int(round(cx / G))) for li in lays]

def clear_line(net, li, x0, y0, x1, y1, w):
    g = grid_for(CLR + w / 2 + G / 2); me = nid(net)
    n = max(1, int(math.hypot(x1 - x0, y1 - y0) / (G / 2)))
    for k in range(n + 1):
        x, y = x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n
        for ix, iy in ((math.floor(x / G), math.floor(y / G)), (math.ceil(x / G), math.floor(y / G)),
                       (math.floor(x / G), math.ceil(y / G)), (math.ceil(x / G), math.ceil(y / G))):
            if not (0 <= ix < NX and 0 <= iy < NY): return False
            c = gget(g[li], iy * NX + ix)
            if c != FREE and c != me: return False
    return True

def smooth(net, pts, w):
    """Greedy line-of-sight: on each same-layer run, jump to the farthest point still in clear view."""
    out = [pts[0]]; k = 0
    while k < len(pts) - 1:
        li = pts[k][0]
        if pts[k + 1][0] != li: out.append(pts[k + 1]); k += 1; continue
        j = k + 1
        while j + 1 < len(pts) and pts[j + 1][0] == li and clear_line(net, li, pts[k][1], pts[k][2], pts[j + 1][1], pts[j + 1][2], w):
            j += 1
        out.append(pts[j]); k = j
    return out

def emit(net, path, w):
    ni = board.FindNet(net); segs = 0
    pts = smooth(net, [(c[0], (c[1] % NX) * G, (c[1] // NX) * G) for c in path], w)
    k = 0
    while k < len(pts) - 1:
        li, x0, y0 = pts[k]
        if pts[k + 1][0] != li:                       # layer change: via
            v = pcbnew.PCB_VIA(board); v.SetPosition(pcbnew.VECTOR2I_MM(x0, y0)); v.SetDrill(MM(VIA_DRILL))
            try: v.SetWidth(MM(VIA_D))
            except TypeError: v.SetWidth(pcbnew.F_Cu, MM(VIA_D))
            v.SetNet(ni); v.SetLocked(True); board.Add(v)
            for l2 in (0, 1): add_shape(net, l2, 'seg', (x0, y0, x0, y0, VIA_D / 2))
            k += 1; continue
        j = k + 1
        x1, y1 = pts[j][1], pts[j][2]
        t = pcbnew.PCB_TRACK(board); t.SetStart(pcbnew.VECTOR2I_MM(x0, y0)); t.SetEnd(pcbnew.VECTOR2I_MM(x1, y1))
        t.SetWidth(MM(w)); t.SetLayer(LAYERS[li]); t.SetNet(ni); t.SetLocked(True); board.Add(t)
        add_shape(net, li, 'seg', (x0, y0, x1, y1, w / 2)); segs += 1
        k = j
    return segs

# ---------------------------------------------------------------- route each net as an MST over its pads
report = []
for short in nets:
    net = full_name.get(short, short)
    pads = pads_of.get(short, [])
    if len(pads) < 2: report.append(f'{short}: fewer than 2 pads'); continue
    w = WIDTH.get(short, DEFAULT_W)
    centre = lambda p: ((p[2][0] + p[2][2]) / 2, (p[2][1] + p[2][3]) / 2)
    done, todo, total = [pads[0]], pads[1:], 0
    while todo:                                          # Prim: nearest unconnected pad to the tree
        a, b = min(((a, b) for a in done for b in todo), key=lambda ab: math.dist(centre(ab[0]), centre(ab[1])))
        path = route(net, pad_cells(*a), pad_cells(*b), w); wu = w
        if path is None and w > DEFAULT_W:              # e.g. paired rail pins on the header: no room for 0.6 mm
            wu = DEFAULT_W; path = route(net, pad_cells(*a), pad_cells(*b), wu)
        if path is None: report.append(f'{net}: no path {a[0].GetParentFootprint().GetReference()}.{a[0].GetNumber()} -> {b[0].GetParentFootprint().GetReference()}.{b[0].GetNumber()}')
        else: total += emit(net, path, wu)
        done.append(b); todo.remove(b)
    print(f'{short:8s} {len(pads)} pads, {total} segments, width {w} mm')
pcbnew.SaveBoard(PCB, board)
for r in report: print('  FAILED', r)
