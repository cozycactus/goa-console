"""Ground pours for the channel-strip PCB (run after place_strip.py, with KiCad's bundled Python):
  .../Python.framework/Versions/3.9/bin/python3 tools/pour_strip.py channel_strip.kicad_pcb
Strip spec section 13: AGND pour on the bottom, separate LGND (GNDD) pour, joined at the spade.
- B.Cu: GNDA over the whole board.
- F.Cu: GNDD islands over the logic parts (priority 1): one over the reservoir caps, power entry and
  overload detector (it holds NT1, the AGND-LGND tie next to the spade); one over the PFL/MUTE rows.
- F.Cu: GNDA everywhere else (priority 0), tied to the bottom pour by stitching vias on a grid,
  placed only where no footprint courtyard, pad or hole is near.
Run it after place_strip.py and route_strip.py; it refuses a board that already has its pour vias."""
import sys
import pcbnew

PCB = sys.argv[1]
board = pcbnew.LoadBoard(PCB)
W, L = 38.0, 480.0
EDGE = 0.5                                    # pour inset from the board edge
MM = pcbnew.FromMM

GNDD_ISLANDS = [
    # reservoir caps C5/C6 (bottom, leads soldered on top), power entry, OL detector, NT1
    [(EDGE, 61.5), (W - EDGE, 61.5), (W - EDGE, 132), (24.3, 132), (24.3, 72.9), (EDGE, 72.9)],
    # PFL and MUTE rows: LED cathodes, MUTE switch logic pole
    [(EDGE, 305), (W - EDGE, 305), (W - EDGE, 338), (EDGE, 338)],
]
VIA_PITCH, VIA_DRILL, VIA_DIA = 4.0, 0.4, 0.8
KEEP = 0.6                                    # via keep-away from courtyards and pads

for z in list(board.Zones()): board.Remove(z)
try: existing = list(board.GetTracks())            # routed tracks (route_strip.py) stay; stitching vias avoid them
except TypeError: existing = []                      # (an empty board's track list cannot be iterated in KiCad 10)
if any(t.GetNetname() in ('GNDA', 'GNDD') and t.IsLocked() for t in existing):
    raise SystemExit('board already has pour vias: re-run place_strip.py and route_strip.py first')

def zone(net, layer, pts, prio):
    z = pcbnew.ZONE(board); z.SetLayer(layer); z.SetNet(board.FindNet(net))
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

# ---- stitching vias: grid points clear of every courtyard (both sides), pad and GNDD island
def inside(poly, x, y):
    c = False; n = len(poly)
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1: c = not c
    return c
def TOMM_W(t):
    try: return pcbnew.ToMM(t.GetWidth())
    except TypeError: return pcbnew.ToMM(t.GetWidth(pcbnew.F_Cu))
boxes = []
for fp in board.GetFootprints():
    fp.BuildCourtyardCaches()
    for lay in (pcbnew.F_CrtYd, pcbnew.B_CrtYd):
        p = fp.GetCourtyard(lay)
        if p.OutlineCount():
            bb = p.BBox(); boxes.append((pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetTop()), pcbnew.ToMM(bb.GetRight()), pcbnew.ToMM(bb.GetBottom())))
    for pad in fp.Pads():
        bb = pad.GetBoundingBox()
        boxes.append((pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetTop()), pcbnew.ToMM(bb.GetRight()), pcbnew.ToMM(bb.GetBottom())))
for t in existing:                                   # routed tracks and vias as keep-outs for the stitching vias
    hw = (TOMM_W(t) / 2) if True else 0
    a, b = t.GetStart(), t.GetEnd()
    boxes.append((min(pcbnew.ToMM(a.x), pcbnew.ToMM(b.x)) - hw, min(pcbnew.ToMM(a.y), pcbnew.ToMM(b.y)) - hw,
                  max(pcbnew.ToMM(a.x), pcbnew.ToMM(b.x)) + hw, max(pcbnew.ToMM(a.y), pcbnew.ToMM(b.y)) + hw))
def clear(x, y):
    r = VIA_DIA / 2 + KEEP
    if x < 2 or x > W - 2 or y < 2 or y > L - 2: return False
    if any(inside(isl, x, y) for isl in GNDD_ISLANDS): return False
    return not any(l - r < x < rr + r and t - r < y < b + r for l, t, rr, b in boxes)
gnda = board.FindNet('GNDA'); nvia = 0
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
        x += VIA_PITCH
    y += VIA_PITCH

def via(net, x, y):
    v = pcbnew.PCB_VIA(board); v.SetPosition(pcbnew.VECTOR2I_MM(x, y)); v.SetDrill(MM(VIA_DRILL))
    try: v.SetWidth(MM(VIA_DIA))
    except TypeError: v.SetWidth(pcbnew.F_Cu, MM(VIA_DIA))
    v.SetNet(board.FindNet(net)); v.SetLocked(True); board.Add(v)
def track(net, layer, pts, w=0.5):
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        t = pcbnew.PCB_TRACK(board); t.SetStart(pcbnew.VECTOR2I_MM(x1, y1)); t.SetEnd(pcbnew.VECTOR2I_MM(x2, y2))
        t.SetWidth(MM(w)); t.SetLayer(layer); t.SetNet(board.FindNet(net)); t.SetLocked(True); board.Add(t)

# ---- LGND islands linked by one bottom track along the right edge (outside the bottom caps and CN2)
LINK = [(37.0, 129.0), (37.0, 307.0)]
via('GNDD', *LINK[0]); via('GNDD', *LINK[1]); track('GNDD', pcbnew.B_Cu, LINK)

# ---- top-side SMD GNDA pads inside an LGND island: short track to their own via into the bottom AGND pour
pads = [(pad, fp) for fp in board.GetFootprints() for pad in fp.Pads()]
def pad_free(x, y, own):
    r = VIA_DIA / 2 + 0.35
    for pad, fp in pads:
        if pad is own: continue
        bb = pad.GetBoundingBox()
        if pcbnew.ToMM(bb.GetLeft()) - r < x < pcbnew.ToMM(bb.GetRight()) + r and pcbnew.ToMM(bb.GetTop()) - r < y < pcbnew.ToMM(bb.GetBottom()) + r:
            return False
    return 1.2 < x < W - 1.2
nfix = 0; failed = []
for pad, fp in pads:
    if pad.GetNetname() != 'GNDA' or pad.GetAttribute() != pcbnew.PAD_ATTRIB_SMD or fp.IsFlipped(): continue
    px, py = pcbnew.ToMM(pad.GetPosition().x), pcbnew.ToMM(pad.GetPosition().y)
    if not any(inside(isl, px, py) for isl in GNDD_ISLANDS): continue
    for dx, dy in ((0, -1.4), (0, 1.4), (-1.6, 0), (1.6, 0), (-1.4, -1.4), (1.4, -1.4), (-1.4, 1.4), (1.4, 1.4), (0, -2.2), (0, 2.2)):
        if pad_free(px + dx, py + dy, pad):
            via('GNDA', px + dx, py + dy); track('GNDA', pcbnew.F_Cu, [(px, py), (px + dx, py + dy)], 0.4); nfix += 1; break
    else: failed.append(f'{fp.GetReference()}.{pad.GetNumber()}')

pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(PCB, board)
print(f'zones: {len(list(board.Zones()))}, stitching vias: {nvia}, GNDA pads in LGND islands given a via: {nfix}')
if failed: print('  no room for a via next to:', ', '.join(failed))
