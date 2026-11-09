"""Ratsnest measure of a placed board: per signal net the Euclidean minimum spanning tree of its pads, and the number of
crossings between different nets' MST edges. Grounds (planes) and supply rails (the rail corridor on the 4-layer
boards) are left out: their ratsnest lines don't show how they are routed. Run with KiCad's Python:
  $KPY tools/ratsnest.py board.kicad_pcb [...]
Used by the untangling study (docs/proposals/untangle_proposal.md) to score 180-degree turns and unit / channel swaps."""
import math, sys
import pcbnew

SKIP = {'GNDA', 'GNDD', 'GNDM', 'PHONESGND', 'CHASSIS', '+VA', '-VA', '+VL', '-VL', '+5VL', '+VBUS', '-VBUS',
        '+VBUS_L', '+VBUS_R', '-VBUS_L', '-VBUS_R', '+VP', '-VP', '+VM', '-VM', '+V', '-V'}
CELL = 5.0

def signal(n):
    n = n.lstrip('/')
    return n and not n.startswith('unconnected') and n not in SKIP

def mst(pts):
    """Prim's MST over points; returns the edges as point pairs."""
    if len(pts) < 2: return []
    best = {i: (math.dist(pts[0], pts[i]), 0) for i in range(1, len(pts))}; edges = []
    while best:
        i = min(best, key=lambda k: best[k][0]); edges.append((pts[best[i][1]], pts[i])); del best[i]
        for k in best:
            d = math.dist(pts[i], pts[k])
            if d < best[k][0]: best[k] = (d, i)
    return edges

def cross(a, b, c, d):
    o = lambda p, q, r: (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    return o(a, b, c) * o(a, b, d) < 0 and o(c, d, a) * o(c, d, b) < 0

class Rats:
    """Net -> pad points; MST edges per net in a 5 mm grid for fast crossing counts. pts[net] maps (ref, pad) -> (x, y)."""
    def __init__(self, board):
        self.pts = {}
        for f in board.GetFootprints():
            for p in f.Pads():
                n = p.GetNetname().lstrip('/')
                if signal(n):
                    q = p.GetPosition(); self.pts.setdefault(n, {})[(f.GetReference(), p.GetNumber())] = (pcbnew.ToMM(q.x), pcbnew.ToMM(q.y))
        self.edges = {}; self.grid = {}
        for n in self.pts: self._index(n)
    def _cells(self, e):
        (x0, y0), (x1, y1) = e
        for cx in range(int(min(x0, x1) // CELL), int(max(x0, x1) // CELL) + 1):
            for cy in range(int(min(y0, y1) // CELL), int(max(y0, y1) // CELL) + 1): yield cx, cy
    def _index(self, n):
        for e in self.edges.get(n, ()):
            for c in self._cells(e): self.grid[c].discard((n, e))
        self.edges[n] = mst(list(self.pts[n].values()))
        for e in self.edges[n]:
            for c in self._cells(e): self.grid.setdefault(c, set()).add((n, e))
    def crossings_of(self, n, edges=None):
        """Crossings of net n's edges (or the given edges) with every other net's edges."""
        k = 0
        for e in (self.edges[n] if edges is None else edges):
            seen = set()                                      # per edge: it spans several cells
            for c in self._cells(e):
                for (m, f) in self.grid.get(c, ()):
                    if m == n or (m, f) in seen: continue
                    seen.add((m, f))
                    if cross(*e, *f): k += 1
        return k
    def length(self, n, edges=None): return sum(math.dist(*e) for e in (self.edges[n] if edges is None else edges))
    def total(self):
        L = sum(self.length(n) for n in self.edges)
        X = sum(self.crossings_of(n) for n in self.edges) // 2
        return L, X
    def trial(self, changes):
        """changes: {net: {(ref, pad): (x, y) or None}}. Score (crossings, length) of the touched nets before and after,
        crossings counted against the untouched nets plus among the touched ones."""
        nets = list(changes)
        def score(edges_of):
            X = 0; L = 0
            for n in nets:
                L += self.length(n, edges_of[n])
                for e in edges_of[n]:
                    seen = set()                              # an edge spans several cells: count each pair once
                    for c in self._cells(e):
                        for (m, f) in self.grid.get(c, ()):
                            if m in changes or (m, f) in seen: continue
                            seen.add((m, f))
                            if cross(*e, *f): X += 1
            for i, a in enumerate(nets):                          # touched nets against each other, once per pair
                for b in nets[i + 1:]:
                    X += sum(1 for e in edges_of[a] for f in edges_of[b] if cross(*e, *f))
            return X, L
        before = score({n: self.edges[n] for n in nets})
        new = {}
        for n in nets:
            p = dict(self.pts[n])
            for k, v in changes[n].items():
                if v is None: p.pop(k, None)
                else: p[k] = v
            new[n] = mst(list(p.values()))
        return before, score(new), new
    def commit(self, changes):
        for n, ch in changes.items():
            for k, v in ch.items():
                if v is None: self.pts[n].pop(k, None)
                else: self.pts.setdefault(n, {})[k] = v
            self._index(n)

if __name__ == '__main__':
    for path in sys.argv[1:]:
        r = Rats(pcbnew.LoadBoard(path)); L, X = r.total()
        print(f'{path.split("/")[-1]:26s} signal nets {len(r.edges):4d}  ratsnest {L:7.0f} mm  crossings {X:5d}')
