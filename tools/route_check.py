"""Post-route checker: what DRC can't see on a routed board (routing_guide.md, docs/studies/layer_study.md). Run with KiCad's Python
after a routing session (it fills the zones on its own copy, the board file is not changed):
  $KPY tools/route_check.py board.kicad_pcb [...]
Net classes come from the project (tools/netrules.py); the board's layer count picks the reference layers.
Checks, each line ERR (breaks a rule of the guide) or WARN (worth a look):
  1 return vias   every via on a signal net needs a GNDA via close by, so the return follows the signal to the other
                  layer (4-layer: In1 <-> In2): aim for 1 mm. On HighZ / Entry / Bus nets ERR past 2 mm, WARN at 1-2 mm
                  (beside a SOIC pin there is often no room within 1 mm); on the others WARN past 2 mm.
  2 reference     F.Cu / B.Cu tracks of HighZ / Entry / Bus nets sampled every 0.5 mm: filled GNDA copper on the
                  reference layer under each point (4-layer: In1 under F.Cu, In2 under B.Cu; 2-layer: the other outer
                  layer). ERR for each stretch over a gap, with its length and position. Needs the ground zones drawn.
  3 high-Z nets   routed length and vias per HighZ net against its pad-to-pad minimum (Manhattan MST): WARN past
                  1.5x + 5 mm or more than 2 vias.
  4 decouplers    two-pad caps between a supply rail and ground: copper path from the IC's supply pin to the cap
                  (WARN > 5 mm) and from the cap's ground pad to the nearest GNDA via or same-layer GNDA fill (WARN > 1 mm).
  5 stability     C0G caps on an op-amp input net: copper path to the pin (WARN > 7 mm, ERR more than one via).
  6 GNDD          a GNDD zone on an outer layer (ERR: GNDD runs as a spine, no fill), GNDD copper touching GNDA (DRC
                  reports shorts too).
Unrouted connections are skipped (the path checks say 'not routed yet' once, per board)."""
import heapq, json, math, os, sys
import pcbnew

mm, M = pcbnew.ToMM, pcbnew.FromMM
SENS = ('HighZ', 'Entry', 'Bus')
QUIET = ('Ground', 'Power', 'LogicSupply', 'Chassis')

def classes(path):
    pro = json.load(open(os.path.splitext(path)[0] + '.kicad_pro'))
    return {p['pattern'].lstrip('/'): p['netclass'] for p in pro.get('net_settings', {}).get('netclass_patterns', [])}

def isvia(t): return t.GetClass() == 'PCB_VIA'
def xy(v): return (mm(v.x), mm(v.y))

class Copper:
    """Per net: a graph of pads, vias, track ends and filled-zone regions, for shortest copper paths."""
    def __init__(self, b):
        self.b = b; self.adj = {}; self.nodes = {}
        self.cu = [l for l in (pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu) if b.IsLayerEnabled(l)]
        for f in b.GetFootprints():
            for p in f.Pads():
                n = p.GetNetname().lstrip('/')
                if n: self.add(n, ('pad', f.GetReference(), p.GetNumber()), xy(p.GetPosition()), [l for l in self.cu if p.IsOnLayer(l)], pad=p)
        self.tracks = []
        for t in b.GetTracks():
            n = t.GetNetname().lstrip('/')
            if not n: continue
            if isvia(t): self.add(n, ('via', id(t)), xy(t.GetPosition()), self.cu, via=t)
            else: self.tracks.append(t)
        for t in self.tracks:
            n = t.GetNetname().lstrip('/'); L = t.GetLayer()
            a, z = ('pt', L, round(mm(t.GetStart().x), 3), round(mm(t.GetStart().y), 3)), ('pt', L, round(mm(t.GetEnd().x), 3), round(mm(t.GetEnd().y), 3))
            self.add(n, a, a[2:], [L]); self.add(n, z, z[2:], [L])
            self.link(n, a, z, mm(t.GetLength()), 0)
        for n, nodes in self.nodes.items():                     # track ends onto pads / vias / other track ends
            ends = [(k, v) for k, v in nodes.items() if k[0] == 'pt']
            hard = [(k, v) for k, v in nodes.items() if k[0] in ('pad', 'via')]
            for k, (p, lay, extra) in ends:
                for k2, (p2, lay2, ex2) in hard:
                    if lay[0] not in lay2: continue
                    if k2[0] == 'pad' and ex2['pad'].HitTest(pcbnew.VECTOR2I(M(p[0]), M(p[1]))): self.link(n, k, k2, 0, 0)
                    if k2[0] == 'via' and math.dist(p, p2) <= mm(ex2['via'].GetWidth(lay[0])) / 2 + 1e-3: self.link(n, k, k2, 0, 0)
        self.zones = {}
        for z in b.Zones():
            if z.GetIsRuleArea(): continue
            n = z.GetNetname().lstrip('/')
            for L in self.cu:
                if z.IsOnLayer(L):
                    poly = z.GetFilledPolysList(L)
                    if poly.OutlineCount(): self.zones.setdefault((n, L), []).append(poly)
        for (n, L), polys in self.zones.items():                 # items inside a fill join through it, straight-line
            inside = [k for k, (p, lay, ex) in self.nodes.get(n, {}).items() if L in lay and any(q.Contains(pcbnew.VECTOR2I(M(p[0]), M(p[1]))) for q in polys)]
            for i, k in enumerate(inside):
                for k2 in inside[i + 1:]:
                    self.link(n, k, k2, math.dist(self.nodes[n][k][0], self.nodes[n][k2][0]), 0)
    def add(self, n, key, p, layers, **extra):
        self.nodes.setdefault(n, {})[key] = (p, layers, extra)
    def link(self, n, a, b, d, via):
        self.adj.setdefault((n, a), []).append((b, d, via)); self.adj.setdefault((n, b), []).append((a, d, via))
    def path(self, n, a, b):
        """(length mm, vias) of the shortest copper path between two nodes of net n, or None"""
        best = {a: (0, 0)}; q = [(0, 0, a)]
        while q:
            d, v, k = heapq.heappop(q)
            if k == b: return d, v
            if best.get(k, (1e18,))[0] < d: continue
            for k2, dd, vv in self.adj.get((n, k), ()):
                vv = v + (1 if k2[0] == 'via' else 0)            # a via counts once, when the path enters it
                if k2 in self.nodes[n] and (k2 not in best or d + dd < best[k2][0]):
                    best[k2] = (d + dd, vv); heapq.heappush(q, (d + dd, vv, k2))
        return None
    def covered(self, net, layer, p):
        return any(q.Contains(pcbnew.VECTOR2I(M(p[0]), M(p[1]))) for q in self.zones.get((net, layer), ()))

def mst_manhattan(pts):
    if len(pts) < 2: return 0.0
    best = {i: abs(pts[0][0] - pts[i][0]) + abs(pts[0][1] - pts[i][1]) for i in range(1, len(pts))}; tot = 0
    while best:
        i = min(best, key=best.get); tot += best.pop(i)
        for k in best: best[k] = min(best[k], abs(pts[i][0] - pts[k][0]) + abs(pts[i][1] - pts[k][1]))
    return tot

def check(path, out=print):
    b = pcbnew.LoadBoard(path)
    if any(not z.GetIsRuleArea() for z in b.Zones()):
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())               # a copy in memory; the file is not saved
    cls = classes(path); four = b.GetCopperLayerCount() == 4
    C = Copper(b); res = {'ERR': 0, 'WARN': 0}; unrouted = set()
    def say(kind, what):
        res[kind] += 1; out(f'  {kind:4s} {what}')
    name = os.path.basename(path)
    vias = [t for t in b.GetTracks() if isvia(t)]
    tracks = [t for t in b.GetTracks() if not isvia(t)]
    out(f'== {name}: {b.GetCopperLayerCount()} layers, {len(tracks)} tracks, {len(vias)} vias, '
        f'{sum(1 for z in b.Zones() if not z.GetIsRuleArea())} zones')
    gvias = [xy(v.GetPosition()) for v in vias if v.GetNetname().lstrip('/') == 'GNDA']
    # 1 return vias
    for v in vias:
        n = v.GetNetname().lstrip('/'); c = cls.get(n, 'Default')
        if c in QUIET: continue
        p = xy(v.GetPosition()); d = min((math.dist(p, g) for g in gvias), default=1e9)
        kind = ('ERR' if d > 2.0 else 'WARN' if d > 1.0 else None) if c in SENS else ('WARN' if d > 2.0 else None)
        if kind:
            say(kind, f'1 return via: {n} ({c}) via at ({p[0]:.1f}, {p[1]:.1f}): nearest GNDA via '
                + (f'{d:.1f} mm' if d < 1e8 else 'none'))
    # 2 reference under sensitive tracks
    ref = {pcbnew.F_Cu: pcbnew.In1_Cu if four else pcbnew.B_Cu, pcbnew.B_Cu: pcbnew.In2_Cu if four else pcbnew.F_Cu}
    noref = [L for L in set(ref.values()) if not C.zones.get(('GNDA', L))]
    for L in noref: out(f'  note 2 reference: no filled GNDA zone on {b.GetLayerName(L)} yet, so its tracks are not checked')
    for t in tracks:
        n = t.GetNetname().lstrip('/'); L = t.GetLayer()
        if cls.get(n) not in SENS or L not in ref or ref[L] in noref: continue
        a, z = xy(t.GetStart()), xy(t.GetEnd()); Lt = math.dist(a, z); k = max(1, int(Lt / 0.5)); step = Lt / k
        own = [p for kk, (p, lay, ex) in C.nodes.get(n, {}).items() if kk[0] in ('via', 'pad')]
        runs, cur = [], None                               # contiguous uncovered stretches, skipping the plane's
        for i in range(k + 1):                            # clearance holes around the net's own vias and pads (1 mm)
            q = (a[0] + (z[0] - a[0]) * i / k, a[1] + (z[1] - a[1]) * i / k)
            if any(math.dist(q, o) < 1.0 for o in own) or C.covered('GNDA', ref[L], q):
                cur = None; continue
            if cur is None: cur = [q, 0.0]; runs.append(cur)
            else: cur[1] += step
        runs = [r for r in runs if r[1] >= 0.5]
        if runs:
            r0 = max(runs, key=lambda r: r[1])
            say('ERR', f'2 reference: {n} on {b.GetLayerName(L)} runs {r0[1]:.1f} mm over a gap in the GNDA fill on '
                f'{b.GetLayerName(ref[L])}, from ({r0[0][0]:.1f}, {r0[0][1]:.1f})' + (f' ({len(runs)} gaps)' if len(runs) > 1 else ''))
    # 3 high-Z nets
    for n in sorted({t.GetNetname().lstrip('/') for t in tracks}):
        if cls.get(n) != 'HighZ': continue
        L = sum(mm(t.GetLength()) for t in tracks if t.GetNetname().lstrip('/') == n)
        nv = sum(1 for v in vias if v.GetNetname().lstrip('/') == n)
        m = mst_manhattan([p for k, (p, lay, ex) in C.nodes.get(n, {}).items() if k[0] == 'pad'])
        if L > 1.5 * m + 5 or nv > 2: say('WARN', f'3 high-Z: {n} routed {L:.0f} mm with {nv} vias (pads {m:.0f} mm apart)')
    # 4 decouplers, 5 stability caps
    pads = {(f.GetReference(), p.GetNumber()): p for f in b.GetFootprints() for p in f.Pads()}
    fps = {f.GetReference(): f for f in b.GetFootprints()}
    for r, f in fps.items():
        ps = list(f.Pads())
        if not r.startswith('C') or r.startswith('CN') or len(ps) != 2: continue
        nets = [p.GetNetname().lstrip('/') for p in ps]; kinds = [cls.get(x, 'Default') for x in nets]
        if sorted(kinds) in (['Ground', 'Power'], ['Ground', 'LogicSupply']):
            ri = kinds.index('Power') if 'Power' in kinds else kinds.index('LogicSupply'); gi = 1 - ri
            rail, gnd = nets[ri], nets[gi]
            pins = [(rr, num) for (rr, num), p in pads.items() if rr.startswith('U') and p.GetNetname().lstrip('/') == rail]
            if not pins: continue
            cp = xy(ps[ri].GetPosition())
            pin = min(pins, key=lambda k: math.dist(xy(pads[k].GetPosition()), cp))
            if math.dist(xy(pads[pin].GetPosition()), cp) > 12: continue          # a bulk cap, not a decoupler
            pt = C.path(rail, ('pad', *pin), ('pad', r, ps[ri].GetNumber()))
            if pt is None: unrouted.add(r); continue                   # its ground side is checked once it is routed
            if pt[0] > 5: say('WARN', f'4 decoupler: {r} is {pt[0]:.1f} mm of copper from {pin[0]} pin {pin[1]} ({rail})')
            gp = xy(ps[gi].GetPosition()); gl = [l for l in C.cu if ps[gi].IsOnLayer(l)]
            if gnd == 'GNDA' and not any(C.covered('GNDA', l, gp) for l in gl):
                d = min((math.dist(gp, g) for g in gvias), default=1e9)
                if d > 1.0: say('WARN', f'4 decoupler: {r} ground pad has no GNDA via within 1 mm' + (f' ({d:.1f} mm)' if d < 1e8 else ''))
        elif 'C0G' in f.GetValue():
            for p in ps:
                n = p.GetNetname().lstrip('/')
                if cls.get(n, 'Default') in ('Ground', 'Power', 'LogicSupply'): continue   # the cap's quiet side: a grounded + input is no stability node
                pins = [(rr, num) for (rr, num), q in pads.items() if rr.startswith('U') and num in ('2', '3', '5', '6')
                        and q.GetNetname().lstrip('/') == n and fps[rr].GetValue().startswith(('OPA', 'TL072'))]
                if not pins: continue
                pin = min(pins, key=lambda k: math.dist(xy(pads[k].GetPosition()), xy(p.GetPosition())))
                pt = C.path(n, ('pad', *pin), ('pad', r, p.GetNumber()))
                if pt is None: unrouted.add(r); continue
                if pt[1] > 1: say('ERR', f'5 stability: {r} reaches {pin[0]} pin {pin[1]} through {pt[1]} vias (one at most)')
                elif pt[0] > 7: say('WARN', f'5 stability: {r} is {pt[0]:.1f} mm of copper from {pin[0]} pin {pin[1]}')
    # 6 GNDD
    for z in b.Zones():
        if not z.GetIsRuleArea() and z.GetNetname().lstrip('/') == 'GNDD' and (z.IsOnLayer(pcbnew.F_Cu) or z.IsOnLayer(pcbnew.B_Cu)):
            say('ERR', '6 GNDD: a GNDD zone on an outer layer (GNDD runs as a spine, no fill)')
    if unrouted: out(f'  note 4/5: {len(unrouted)} decouplers / stability caps not routed to their pin yet')
    out(f'  {res["ERR"]} ERR, {res["WARN"]} WARN')
    return res

if __name__ == '__main__':
    for p in sys.argv[1:]: check(p)
