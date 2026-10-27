"""Escape / layer plan for the densest spots of a placed board (routing help, no copper). Run with KiCad's Python:
  $KPY tools/escape_plan.py board.kicad_pcb [windows=3] [height=30]
  -> docs/escape/<board>_<n>.svg per window, docs/escape/<board>_layers.csv (the plan per net), a table on stdout
1. Windows: a window of the board's width and `height` mm slides along the board; the windows with the most ratsnest
   crossings (tools/ratsnest.py, signal nets) are taken, not overlapping.
2. Layer plan, made once for the whole board (so a long net keeps its layer through every window):
   - HighZ / Entry / Bus nets on F.Cu (they want the unbroken In1 under them; netrules.py keeps them off the corridor
     on B.Cu);
   - Switching nets (LEDs, comparator outputs, DG413 logic) on B.Cu: both ground planes then lie between them and the
     sensitive nets, better than any spacing on one layer;
   - every other net starts on the side most of its pads are on, then nets flip greedily while that lowers
     cost = same-layer crossings + 0.3 per layer change the choice needs (one per pad on the other side).
3. SVG: pads (top dark, bottom light), IC / control references; local edges red on F.Cu and blue on B.Cu, through
   traffic (edges entering and leaving the window) faint and dashed in its layer's colour; a crossing left on one layer
   is circled where at least one side is local (two through lines run parallel in practice).
The plan is a starting point: same-layer crossings left over mean a detour or a short jumper there."""
import json, math, os, sys
import pcbnew
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ratsnest import Rats, cross, signal

mm = pcbnew.ToMM
SENS = ('HighZ', 'Entry', 'Bus')

def clip(e, y0, y1):
    """the part of a segment inside y0..y1 (None if outside)"""
    (ax, ay), (bx, by) = e
    if max(ay, by) < y0 or min(ay, by) > y1: return None
    def at(y): return (ax + (bx - ax) * (y - ay) / (by - ay), y) if by != ay else (ax, y)
    p = (ax, ay) if y0 <= ay <= y1 else at(y0 if ay < y0 else y1)
    q = (bx, by) if y0 <= by <= y1 else at(y0 if by < y0 else y1)
    return (p, q)

def plan(path, windows=3, height=30.0):
    b = pcbnew.LoadBoard(path); r = Rats(b); name = os.path.splitext(os.path.basename(path))[0]
    pro = json.load(open(os.path.splitext(path)[0] + '.kicad_pro'))
    cls = {p['pattern'].lstrip('/'): p['netclass'] for p in pro['net_settings']['netclass_patterns']}
    side = {}; padsxy = []
    for f in b.GetFootprints():
        for p in f.Pads():
            n = p.GetNetname().lstrip('/'); bb = p.GetBoundingBox()
            padsxy.append((mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom()),
                           'TH' if p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH else ('B' if f.IsFlipped() else 'F')))
            if signal(n): side.setdefault(n, []).append('TH' if p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH else ('B' if f.IsFlipped() else 'F'))
    EB = b.GetBoardEdgesBoundingBox(); X0, X1, Y0, Y1 = mm(EB.GetLeft()), mm(EB.GetRight()), mm(EB.GetTop()), mm(EB.GetBottom())
    edges = [(n, e) for n, es in r.edges.items() for e in es]
    def crossings_in(y0, y1):
        es = [(n, c) for n, e in edges if (c := clip(e, y0, y1))]
        return sum(1 for i, (n, e) in enumerate(es) for m, f in es[i + 1:] if n != m and cross(*e, *f)), es
    scored = sorted(((crossings_in(y, y + height)[0], y) for y in range(int(Y0), int(Y1 - height) + 1, 2)), reverse=True)
    picks = []
    for c, y in scored:
        if all(abs(y - p) >= height for _, p in picks): picks.append((c, y))
        if len(picks) == windows: break
    # the layer plan, once for the whole board
    nets = sorted(r.edges)
    def pref(n):
        s = side.get(n, []); return 'B' if s.count('B') > s.count('F') else 'F'
    layer = {n: 'F' if cls.get(n) in SENS else 'B' if cls.get(n) == 'Switching' else pref(n) for n in nets}
    fixed = {n for n in nets if cls.get(n) in SENS or cls.get(n) == 'Switching'}
    by_net = {}
    for i, (n, e) in enumerate(edges):
        for m, f in edges[i + 1:]:
            if n != m and cross(*e, *f): by_net.setdefault(n, []).append(m); by_net.setdefault(m, []).append(n)
    def vias(n, L): return sum(1 for s in side.get(n, []) if s != 'TH' and s != L)
    def cost_of(n, L): return sum(1 for m in by_net.get(n, []) if layer[m] == L) + 0.3 * vias(n, L)
    for _ in range(30):
        moved = 0
        for n in nets:
            if n in fixed: continue
            other = 'B' if layer[n] == 'F' else 'F'
            if cost_of(n, other) < cost_of(n, layer[n]) - 1e-9: layer[n] = other; moved += 1
        if not moved: break
    total_x = sum(len(v) for v in by_net.values()) // 2
    total_left = sum(1 for n, ms in by_net.items() for m in ms if layer[n] == layer[m]) // 2
    print(f'{name}: whole board {total_x} crossings, {total_left} left on one layer after the plan, '
          f'{sum(vias(n, layer[n]) for n in nets)} layer changes; {sum(1 for n in nets if layer[n] == "F")} nets on F.Cu, '
          f'{sum(1 for n in nets if layer[n] == "B")} on B.Cu')
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(path)), 'docs', 'escape'), exist_ok=True)
    import csv                                        # the whole-board plan, one row per signal net
    with open(os.path.join(os.path.dirname(os.path.abspath(path)), 'docs', 'escape', f'{name}_layers.csv'), 'w', newline='') as fh:
        w = csv.writer(fh); w.writerow(['net', 'class', 'layer', 'pads top', 'pads bottom', 'through-hole pads', 'ratsnest crossings', 'left on its layer'])
        for n in nets:
            s_ = side.get(n, [])
            w.writerow([n, cls.get(n, 'Default'), 'F.Cu' if layer[n] == 'F' else 'B.Cu', s_.count('F'), s_.count('B'), s_.count('TH'),
                        len(by_net.get(n, [])), sum(1 for m in by_net.get(n, []) if layer[m] == layer[n])])
    out = []
    for k, (c0, y0) in enumerate(sorted(picks, key=lambda t: t[1])):
        y1 = y0 + height; _, es = crossings_in(y0, y1)
        wnets = sorted({n for n, e in es})
        through = [((abs(e[0][1] - y0) < 1e-6 or abs(e[0][1] - y1) < 1e-6) and (abs(e[1][1] - y0) < 1e-6 or abs(e[1][1] - y1) < 1e-6)) for n, e in es]
        pairs = [(i, j) for i in range(len(es)) for j in range(i + 1, len(es)) if es[i][0] != es[j][0] and cross(*es[i][1], *es[j][1])
                 and not (through[i] and through[j])]
        left = [(i, j) for i, j in pairs if layer[es[i][0]] == layer[es[j][0]]]
        nvias = sum(vias(n, layer[n]) for n in wnets)
        # SVG
        sx = 14.0; W = (X1 - X0) * sx; H = height * sx
        X = lambda x: (x - X0) * sx; Y = lambda y: (y - y0) * sx
        svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W + 260:.0f}" height="{H + 40:.0f}" font-family="Helvetica" font-size="11">',
               f'<rect x="0" y="0" width="{W + 260:.0f}" height="{H + 40:.0f}" fill="white"/>',
               f'<rect x="0" y="20" width="{W:.0f}" height="{H:.0f}" fill="#f4f1e8" stroke="#888"/>',
               f'<text x="2" y="14">{name}: y {y0:.0f}–{y1:.0f} mm; {len(wnets)} nets, {len(pairs)} crossings, {len(left)} left on one layer, {nvias} layer changes</text>']
        for (l, t, rr, bt, s) in padsxy:
            if bt < y0 or t > y1: continue
            col = {'F': '#444', 'B': '#bbb', 'TH': '#b8860b'}[s]
            svg.append(f'<rect x="{X(l):.1f}" y="{Y(t) + 20:.1f}" width="{(rr - l) * sx:.1f}" height="{(bt - t) * sx:.1f}" fill="{col}" opacity="0.8"/>')
        for i, (n, ((ax, ay), (bx, by))) in enumerate(es):
            col = '#d62728' if layer[n] == 'F' else '#1f77b4'
            if through[i]:
                svg.append(f'<line x1="{X(ax):.1f}" y1="{Y(ay) + 20:.1f}" x2="{X(bx):.1f}" y2="{Y(by) + 20:.1f}" stroke="{col}" stroke-width="1" opacity="0.35" stroke-dasharray="4 3"/>')
            else:
                svg.append(f'<line x1="{X(ax):.1f}" y1="{Y(ay) + 20:.1f}" x2="{X(bx):.1f}" y2="{Y(by) + 20:.1f}" stroke="{col}" stroke-width="{2.6 if cls.get(n) in SENS else 1.4}"/>')
        for f in b.GetFootprints():
            ref = f.GetReference(); q = f.GetPosition(); fx, fy = mm(q.x), mm(q.y)
            if ref.startswith(('U', 'J', 'RV', 'SW', 'CN')) and y0 <= fy <= y1:
                svg.append(f'<text x="{X(fx):.1f}" y="{Y(fy) + 20:.1f}" font-size="13" font-weight="bold" fill="#2a2a2a" '
                           f'text-anchor="middle" stroke="white" stroke-width="3" paint-order="stroke">{ref}</text>')
        for i, j in left:
            (a, bq), (c, d) = es[i][1], es[j][1]
            den = (a[0] - bq[0]) * (c[1] - d[1]) - (a[1] - bq[1]) * (c[0] - d[0])
            if den == 0: continue
            t_ = ((a[0] - c[0]) * (c[1] - d[1]) - (a[1] - c[1]) * (c[0] - d[0])) / den
            px, py = a[0] + t_ * (bq[0] - a[0]), a[1] + t_ * (bq[1] - a[1])
            svg.append(f'<circle cx="{X(px):.1f}" cy="{Y(py) + 20:.1f}" r="5" fill="none" stroke="black" stroke-width="1.5"/>')
        lx = W + 10
        for i, (txt, col) in enumerate((('F.Cu (over In1)', '#d62728'), ('B.Cu (over In2)', '#1f77b4'), ('thick: HighZ / Entry / Bus', '#000'),
                                        ('dashed: through traffic', '#666'),
                                        ('pad, top', '#444'), ('pad, bottom', '#bbb'), ('through-hole pad', '#b8860b'), ('O crossing left on one layer', '#000'))):
            svg.append(f'<text x="{lx}" y="{40 + 16 * i}" fill="{col}">{txt}</text>')
        svg.append('</svg>')
        fn = os.path.join(os.path.dirname(os.path.abspath(path)), 'docs', 'escape', f'{name}_{k + 1}.svg')
        open(fn, 'w').write('\n'.join(svg))
        out.append(dict(window=k + 1, y0=y0, y1=y1, nets=len(wnets), crossings=len(pairs), left=len(left), vias=nvias,
                        F=sorted(n for n in wnets if layer[n] == 'F'), B=sorted(n for n in wnets if layer[n] == 'B'), svg=fn))
    return out

if __name__ == '__main__':
    path = sys.argv[1]; w = int(sys.argv[2]) if len(sys.argv) > 2 else 3; h = float(sys.argv[3]) if len(sys.argv) > 3 else 30.0
    for o in plan(path, w, h):
        print(f"window {o['window']}: y {o['y0']:.0f}-{o['y1']:.0f} mm, {o['nets']} nets, {o['crossings']} crossings -> "
              f"{o['left']} left on one layer, {o['vias']} layer changes; {os.path.relpath(o['svg'])}")
        print('  F.Cu:', ' '.join(o['F'])); print('  B.Cu:', ' '.join(o['B']))
