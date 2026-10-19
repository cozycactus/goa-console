"""Ground pours for the channel-strip PCB (run after place_strip.py, with KiCad's bundled Python):
  .../Python.framework/Versions/3.9/bin/python3 tools/pour_strip.py channel_strip.kicad_pcb
Strip spec section 13: AGND pour on the bottom, separate LGND (GNDD) pour, joined at the spade.
- B.Cu: GNDA over the whole board.
- F.Cu: GNDD islands over the logic parts (priority 1): one over the reservoir caps, power entry and
  overload detector (it holds NT1, the AGND-LGND tie next to the spade); one over the PFL/MUTE rows.
- F.Cu: GNDA everywhere else (priority 0), tied to the bottom pour by stitching vias on a grid,
  placed only where no footprint courtyard, pad or hole is near.
Run it after place_strip.py and route_strip.py. Each run first strips the previous pours (zones, and the
locked GNDA/GNDD vias and tracks) from the file; --strip does only that."""
import sys, math
import pcbnew

PCB = sys.argv[1]
STRIP = '--strip' in sys.argv[2:]                    # remove this script's zones, vias and tracks, then stop

def strip_file(path):
    """Text-level strip: drop every top-level (zone ...) block and the locked GNDA/GNDD vias and tracks this
    script made (the router never routes grounds). Done on the file because removing zones through the
    KiCad 10 Python API leaves later SWIG objects unusable."""
    txt = open(path).read(); out, i, n_z, n_t = [], 0, 0, 0
    while True:
        j = txt.find('\n\t(', i)
        if j < 0: out.append(txt[i:]); break
        out.append(txt[i:j + 1]); k = j + 1; depth = 0; q = k
        while True:                                   # find the matching paren of this top-level item
            ch = txt[q]
            if ch == '"':                             # skip the string, honouring \" escapes
                q += 1
                while txt[q] != '"': q += 2 if txt[q] == '\\' else 1
            elif ch == '(': depth += 1
            elif ch == ')':
                depth -= 1
                if depth == 0: break
            q += 1
        item = txt[k:q + 1]
        kind = item.lstrip('\t')[1:].split(None, 1)[0].rstrip(')') if item.strip() else ''
        if kind == 'zone': n_z += 1
        elif kind in ('via', 'segment') and '(locked yes)' in item and ('(net "GNDA")' in item or '(net "GNDD")' in item): n_t += 1
        else: out.append(item)
        i = q + 1
    open(path, 'w').write(''.join(out))
    return n_z, n_t

nz, nt = strip_file(PCB)
if STRIP:
    print(f'stripped {nz} zones and {nt} pour vias/tracks'); sys.exit(0)
board = pcbnew.LoadBoard(PCB)
W, L = 38.0, 480.0
EDGE = 0.5                                    # pour inset from the board edge
MM = pcbnew.FromMM

GNDD_ISLANDS = [
    # reservoir caps C5/C6 (bottom, leads soldered on top), power entry, NT1 (the OL detector stays on AGND)
    [(EDGE, 61.5), (W - EDGE, 61.5), (W - EDGE, 88.6), (EDGE, 88.6)],
    # PFL and MUTE rows: LED cathodes, MUTE switch logic pole
    [(EDGE, 305), (W - EDGE, 305), (W - EDGE, 338), (EDGE, 338)],
]
VIA_PITCH, VIA_DRILL, VIA_DIA = 4.0, 0.4, 0.8
KEEP = 0.6                                    # via keep-away from courtyards and pads

try: existing = list(board.GetTracks())            # routed tracks (route_strip.py) stay; stitching vias avoid them
except TypeError: existing = []                      # (an empty board's track list cannot be iterated in KiCad 10)
# ground net codes from the pads: KiCad 10's FindNet() sometimes hands back an unusable SWIG object
NETINFO = {n: board.FindNet(n) for n in ('GNDA', 'GNDD')}     # safe on a cleanly loaded board

def zone(net, layer, pts, prio):
    z = pcbnew.ZONE(board); z.SetLayer(layer); z.SetNet(NETINFO[net])
    o = z.Outline(); o.NewOutline()
    for x, y in pts: o.Append(MM(x), MM(y))
    z.SetAssignedPriority(prio); z.SetMinThickness(MM(0.25))
    z.SetLocalClearance(MM(0.3)); z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetThermalReliefGap(MM(0.4)); z.SetThermalReliefSpokeWidth(MM(0.5))
    z.SetIsFilled(False); board.Add(z); return z

full = [(EDGE, EDGE), (W - EDGE, EDGE), (W - EDGE, L - EDGE), (EDGE, L - EDGE)]
zone('GNDA', pcbnew.B_Cu, full, 0)
zone('GNDA', pcbnew.F_Cu, full, 0)
for isl in GNDD_ISLANDS: zone('GNDD', pcbnew.F_Cu, isl, 1)

# ---- copper already on the board (pads, routed tracks and vias): every added via or track keeps CLR from it
CLR = 0.25
def tomm(v): return pcbnew.ToMM(v)
def width_of(t):
    try: return tomm(t.GetWidth())
    except TypeError: return tomm(t.GetWidth(pcbnew.F_Cu))
segs = []                    # (layers, net, x1, y1, x2, y2, half-width)
for t in existing:
    a, b = t.GetStart(), t.GetEnd(); lay = (0, 1) if isinstance(t, pcbnew.PCB_VIA) else ((0,) if t.GetLayer() == pcbnew.F_Cu else (1,))
    segs.append((lay, t.GetNetname(), tomm(a.x), tomm(a.y), tomm(b.x), tomm(b.y), width_of(t) / 2))
rects = []                   # (layers, net, pad, x0, y0, x1, y1)
courtyards = []
for fp in board.GetFootprints():
    fp.BuildCourtyardCaches()
    for lay in (pcbnew.F_CrtYd, pcbnew.B_CrtYd):
        p = fp.GetCourtyard(lay)
        if p.OutlineCount():
            bb = p.BBox(); courtyards.append((tomm(bb.GetLeft()), tomm(bb.GetTop()), tomm(bb.GetRight()), tomm(bb.GetBottom())))
    for pad in fp.Pads():
        bb = pad.GetBoundingBox()
        lay = tuple(i for i, l in enumerate((pcbnew.F_Cu, pcbnew.B_Cu)) if pad.IsOnLayer(l)) or (0, 1)
        rects.append((lay, pad.GetNetname(), pad, tomm(bb.GetLeft()), tomm(bb.GetTop()), tomm(bb.GetRight()), tomm(bb.GetBottom())))

def d_pt_seg(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1; ll = dx * dx + dy * dy
    t = 0 if ll == 0 else max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / ll))
    return math.hypot(px - x1 - t * dx, py - y1 - t * dy)
def d_pt_rect(px, py, x0, y0, x1, y1):
    return math.hypot(max(x0 - px, 0, px - x1), max(y0 - py, 0, py - y1))
def point_clear(px, py, r, layers, net, own=None):
    for lay, n, x1, y1, x2, y2, hw in segs:
        d = d_pt_seg(px, py, x1, y1, x2, y2)
        if n != net and set(lay) & set(layers) and d < r + hw + CLR: return False
        if lay == (0, 1) and x1 == x2 and y1 == y2 and layers == (0, 1) and d < r + hw + CLR: return False   # via to via, any net
    for lay, n, pad, x0, y0, x1, y1 in rects:
        if pad is own or (n == net and n): continue
        if set(lay) & set(layers) and d_pt_rect(px, py, x0, y0, x1, y1) < r + CLR: return False
    return EDGE + r < px < W - EDGE - r and EDGE + r < py < L - EDGE - r
def line_clear(x1, y1, x2, y2, hw, layers, net, own=None):
    n = max(1, int(math.hypot(x2 - x1, y2 - y1) / 0.1))
    return all(point_clear(x1 + (x2 - x1) * k / n, y1 + (y2 - y1) * k / n, hw, layers, net, own) for k in range(n + 1))

# ---- stitching vias: grid points clear of copper, courtyards (both sides) and the LGND islands
def inside(poly, x, y):
    c = False; n = len(poly)
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1: c = not c
    return c
def clear(x, y):
    r = VIA_DIA / 2
    if x < 2 or x > W - 2 or y < 2 or y > L - 2: return False
    if any(inside(isl, x, y) for isl in GNDD_ISLANDS): return False
    if any(l - r - KEEP < x < rr + r + KEEP and t - r - KEEP < y < b + r + KEEP for l, t, rr, b in courtyards): return False
    return point_clear(x, y, r, (0, 1), 'GNDA')
def via(net, x, y):
    v = pcbnew.PCB_VIA(board); v.SetPosition(pcbnew.VECTOR2I_MM(x, y)); v.SetDrill(MM(VIA_DRILL))
    try: v.SetWidth(MM(VIA_DIA))
    except TypeError: v.SetWidth(pcbnew.F_Cu, MM(VIA_DIA))
    v.SetNet(NETINFO[net]); v.SetLocked(True); board.Add(v)
    segs.append(((0, 1), net, x, y, x, y, VIA_DIA / 2))
def track(net, layer, pts, w=0.5):
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        t = pcbnew.PCB_TRACK(board); t.SetStart(pcbnew.VECTOR2I_MM(x1, y1)); t.SetEnd(pcbnew.VECTOR2I_MM(x2, y2))
        t.SetWidth(MM(w)); t.SetLayer(layer); t.SetNet(NETINFO[net]); t.SetLocked(True); board.Add(t)
        segs.append(((0,) if layer == pcbnew.F_Cu else (1,), net, x1, y1, x2, y2, w / 2))

# ---- the LGND islands and the logic parts are joined by GNDD tracks from route_strip.py (rails block)

# ---- top-side SMD GNDA pads inside an LGND island: short track to their own via into the bottom AGND pour
pads = [(pad, fp) for fp in board.GetFootprints() for pad in fp.Pads()]
nfix = 0; failed = []
for pad, fp in pads:
    if pad.GetNetname() != 'GNDA' or pad.GetAttribute() != pcbnew.PAD_ATTRIB_SMD or fp.IsFlipped(): continue
    px, py = pcbnew.ToMM(pad.GetPosition().x), pcbnew.ToMM(pad.GetPosition().y)
    # every top-side GNDA SMD pad gets its own via to the bottom AGND pour: routed tracks can cut the top pour
    # into fragments, and inside an LGND island there is no top AGND at all
    for rr in (1.4, 1.9, 2.4, 3.0, 3.6, 4.5):
      for a in range(0, 360, 30):
        dx, dy = rr * math.cos(math.radians(a)), rr * math.sin(math.radians(a))
        vx, vy = px + dx, py + dy
        if point_clear(vx, vy, VIA_DIA / 2, (0, 1), 'GNDA', pad) and line_clear(px, py, vx, vy, 0.2, (0,), 'GNDA', pad):
            via('GNDA', vx, vy); track('GNDA', pcbnew.F_Cu, [(px, py), (vx, vy)], 0.4); nfix += 1; break
      else: continue
      break
    else: failed.append(f'{fp.GetReference()}.{pad.GetNumber()}')

# ---- stitching vias last, so the escape vias and the LGND link get first pick
gnda = NETINFO['GNDA']; nvia = 0
y = 2.0
while y < L - 1:
    x = 2.0
    while x < W - 1:
        if clear(x, y):
            v = pcbnew.PCB_VIA(board); v.SetPosition(pcbnew.VECTOR2I_MM(x, y))
            v.SetDrill(MM(VIA_DRILL))
            try: v.SetWidth(MM(VIA_DIA))
            except TypeError: v.SetWidth(pcbnew.F_Cu, MM(VIA_DIA))
            v.SetNet(gnda); v.SetLocked(True); board.Add(v); nvia += 1
            segs.append(((0, 1), 'GNDA', x, y, x, y, VIA_DIA / 2))
        x += VIA_PITCH
    y += VIA_PITCH

pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(PCB, board)
print(f'zones: {len(list(board.Zones()))}, stitching vias: {nvia}, top-side GNDA pads given their own via: {nfix}, '
      '')
if failed: print('  no room for a via next to:', ', '.join(failed))
