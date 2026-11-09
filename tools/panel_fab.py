"""Front-panel fabrication drawings from tools/panel_layout.py (the 3D model's own panels), one set per module:
  panels/<key>.dxf          R12 DXF, mm, origin at the panel's bottom-left corner seen from the front: layers OUTLINE
                            (plate), CUT (every hole and slot) and LEGEND (the print, text as glyph outlines, filled
                            closed polylines)
  panels/<key>.svg / .pdf   1:1 artwork: plate outline and cut-outs as hairlines, the print filled (one ink)
  panels/<key>.png          preview (anodised black, cream ink)
  panels/<key>_holes.csv    hole table: x, y from the bottom-left corner, diameter or slot size, what
  panels/strip_numbers.pdf / group_numbers.pdf: the same artwork per strip 1-24 / group 1-4 (number at the bottom)
Then checks: web between cut-outs, hole to edge, holes clear of the frame rails, print clear of the cut-outs and inside
the plate. Text: Arial Narrow / Arial Narrow Bold (the model's fonts), outlined, so no font is needed at the maker.
usage: .venv/bin/python tools/panel_fab.py [out_dir]   (needs fonttools; rsvg-convert for the PDF / PNG)"""
import csv, math, os, subprocess, sys
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import panel_layout as L

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
FONTS = {False: '/System/Library/Fonts/Supplemental/Arial Narrow.ttf', True: '/System/Library/Fonts/Supplemental/Arial Narrow Bold.ttf'}
RAILS = tuple((y - L.RAIL_W / 2, y + L.RAIL_W / 2) for y in L.RAIL_LINES)   # frame rails under the panel ends: no cut-out over them
STUD_D, STUD_BOSS = 3.2, 6.0       # blind M3 stud on the panel's back (docs/reviews/met1_ret1_review.md P4): shank and its weld / boss area.
# Welded, not pressed in: PEM's concealed-head M3 studs need a 1.60 mm sheet and the panels are 1.5 mm (the NJ6FD-V's limit)
WEB, EDGE, INK_GAP, INK_EDGE = 1.0, 1.0, 0.2, 0.3   # minimum web between cut-outs, cut-out to edge, print to cut-out, print to edge (the section rules run full width, 0.41 from the edges)
INK, PLATE = '#efe6cf', '#1b1b1d'              # cream print on black anodising (preview only; colours are placeholders)

# ---------------------------------------------------------------- text as outlines
class Flatten(BasePen):
    """Glyph contours as polylines (quadratic / cubic segments cut into 8 pieces)."""
    def __init__(self, gs):
        super().__init__(gs); self.contours, self.cur = [], []
    def _moveTo(self, p): self.cur = [p]
    def _lineTo(self, p): self.cur.append(p)
    def _curveToOne(self, p1, p2, p3):
        p0 = self.cur[-1]
        for k in range(1, 9):
            t = k / 8; u = 1 - t
            self.cur.append(tuple(u ** 3 * a + 3 * u * u * t * b + 3 * u * t * t * c + t ** 3 * d for a, b, c, d in zip(p0, p1, p2, p3)))
    def _qCurveToOne(self, p1, p2):
        p0 = self.cur[-1]
        for k in range(1, 9):
            t = k / 8; u = 1 - t
            self.cur.append(tuple(u * u * a + 2 * u * t * b + t * t * c for a, b, c in zip(p0, p1, p2)))
    def _closePath(self):
        if len(self.cur) > 2: self.contours.append(self.cur)
        self.cur = []
    _endPath = _closePath

class Font:
    def __init__(self, path):
        self.f = TTFont(path); self.gs = self.f.getGlyphSet(); self.cmap = self.f.getBestCmap()
        self.upm = self.f['head'].unitsPerEm; self.hmtx = self.f['hmtx']
        b = self.f['glyf']['H']; self.cap = b.yMax                    # the font's own cap height
        self.cache = {}
    def glyph(self, ch):
        name = self.cmap.get(ord(ch), '.notdef')
        if name not in self.cache:
            pen = Flatten(self.gs); self.gs[name].draw(pen); self.cache[name] = (pen.contours, self.hmtx[name][0])
        return self.cache[name]
    def outline(self, s, x, y, size):
        """Contours of s centred on (x, y) in board mm (y down), cap height centred vertically; and its box."""
        k = size / self.upm; adv = sum(self.glyph(c)[1] for c in s) * k
        ox, base = x - adv / 2, y + self.cap * k / 2
        out, pen_x = [], ox
        for c in s:
            cs, a = self.glyph(c)
            out += [[(pen_x + px * k, base - py * k) for px, py in ct] for ct in cs]
            pen_x += a * k
        pts = [p for ct in out for p in ct] or [(x, y)]
        return out, (min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts))

# ---------------------------------------------------------------- geometry
def ink(P, fonts):
    """Every inked shape as closed polylines [(points, box)] in board mm."""
    shapes = []
    for s, x, y, size, bold in P.texts:
        cs, box = fonts[bold].outline(s, x, y, size)
        shapes += [(ct, box) for ct in cs]
    for x0, y0, x1, y1 in P.rects:
        shapes.append(([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], (x0, y0, x1, y1)))
    return shapes

def slot_outline(x, y, ln, w, a, n=12):
    ca, sa = math.cos(math.radians(a)), -math.sin(math.radians(a)); r = w / 2; h = ln / 2 - r
    pts = [(h + r * math.cos(t), r * math.sin(t)) for t in (math.pi * (k / n - 0.5) for k in range(n + 1))]
    pts += [(-h - r * math.cos(t), -r * math.sin(t)) for t in (math.pi * (k / n - 0.5) for k in range(n + 1))]
    return [(x + u * ca - v * sa, y + u * sa + v * ca) for u, v in pts]

def seg_dist(p, a, b):
    ax, ay = b[0] - a[0], b[1] - a[1]; L2 = ax * ax + ay * ay
    t = 0 if L2 == 0 else max(0, min(1, ((p[0] - a[0]) * ax + (p[1] - a[1]) * ay) / L2))
    return math.hypot(p[0] - a[0] - t * ax, p[1] - a[1] - t * ay)

# ---------------------------------------------------------------- writers
def dxf(path, P, circles, slots, shapes):
    X = lambda x: x - P.x0; Y = lambda y: P.y1 - y           # front view, origin bottom-left, y up
    o = ['0', 'SECTION', '2', 'HEADER', '9', '$INSUNITS', '70', '4', '9', '$MEASUREMENT', '70', '1', '0', 'ENDSEC',
         '0', 'SECTION', '2', 'TABLES', '0', 'TABLE', '2', 'LAYER', '70', '3']
    for i, (n, col) in enumerate((('OUTLINE', 7), ('CUT', 1), ('LEGEND', 2), ('STUDS', 5), ('CSK_NO_STUDS', 6))):
        o += ['0', 'LAYER', '2', n, '70', '0', '62', str(col), '6', 'CONTINUOUS']
    o += ['0', 'ENDTAB', '0', 'ENDSEC', '0', 'SECTION', '2', 'ENTITIES']
    def poly(layer, pts):
        nonlocal o
        o += ['0', 'POLYLINE', '8', layer, '66', '1', '70', '1']
        for px, py in pts: o += ['0', 'VERTEX', '8', layer, '10', f'{X(px):.4f}', '20', f'{Y(py):.4f}']
        o += ['0', 'SEQEND', '8', layer]
    poly('OUTLINE', [(P.x0, P.y0), (P.x1, P.y0), (P.x1, P.y1), (P.x0, P.y1)])
    for x, y, d in circles: o += ['0', 'CIRCLE', '8', 'CUT', '10', f'{X(x):.4f}', '20', f'{Y(y):.4f}', '40', f'{d / 2:.4f}']
    for x, y, ln, w, a in slots: poly('CUT', slot_outline(x, y, ln, w, a, 24))
    for pts, _ in shapes: poly('LEGEND', pts)
    for x, y, ref, bd in P.studs:                         # back side, not through: a circle and a cross per stud
        o += ['0', 'CIRCLE', '8', 'STUDS', '10', f'{X(x):.4f}', '20', f'{Y(y):.4f}', '40', f'{STUD_D / 2:.4f}']
        for dx, dy in ((1, 0), (0, 1)):
            o += ['0', 'LINE', '8', 'STUDS', '10', f'{X(x - dx * STUD_D / 2):.4f}', '20', f'{Y(y - dy * STUD_D / 2):.4f}',
                  '11', f'{X(x + dx * STUD_D / 2):.4f}', '21', f'{Y(y + dy * STUD_D / 2):.4f}']
    for x, y, ref, bd in P.studs:                         # only if no welded studs: through-hole + countersink outline
        if bd != 'jack': continue
        for d_ in (L.CSK_HOLE, L.CSK_D):
            o += ['0', 'CIRCLE', '8', 'CSK_NO_STUDS', '10', f'{X(x):.4f}', '20', f'{Y(y):.4f}', '40', f'{d_ / 2:.4f}']
    o += ['0', 'ENDSEC', '0', 'EOF']
    open(path, 'w').write('\n'.join(o) + '\n')

def svg(path, P, circles, slots, shapes, preview=False):
    W, H = P.x1 - P.x0, P.y1 - P.y0
    X = lambda x: x - P.x0; Y = lambda y: y - P.y0
    d = lambda pts: 'M' + ' L'.join(f'{X(a):.3f},{Y(b):.3f}' for a, b in pts) + ' Z'
    line = '#ffffff' if preview else '#ff0000'
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.3f}mm" height="{H:.3f}mm" viewBox="0 0 {W:.3f} {H:.3f}">']
    if preview: o.append(f'<rect width="{W:.3f}" height="{H:.3f}" fill="{PLATE}"/>')
    o.append(f'<g id="outline" fill="none" stroke="{"#555" if preview else line}" stroke-width="0.05">'
             f'<rect width="{W:.3f}" height="{H:.3f}"/></g>')
    o.append(f'<g id="cut" fill="{"#d8d8d8" if preview else "none"}" stroke="{line}" stroke-width="0.05">')
    o += [f'<circle cx="{X(x):.3f}" cy="{Y(y):.3f}" r="{dd / 2:.3f}"/>' for x, y, dd in circles]
    o += [f'<path d="{d(slot_outline(*s, 24))}"/>' for s in slots]
    o.append('</g>')
    o.append(f'<g id="legend" fill="{INK if preview else "#000000"}" fill-rule="nonzero"><path d="'
             + ' '.join(d(pts) for pts, _ in shapes) + '"/></g></svg>')
    open(path, 'w').write('\n'.join(o) + '\n')

def holes_csv(path, P):
    with open(path, 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['x mm', 'y mm', 'diameter / slot', 'what'])
        rows = []
        for kind, x, y, a in P.holes:
            what = next((f'{r} {k}' for r, k, px, py, *_ in P.parts if abs(px - x) < 1e-6 and abs(py - y) < 1e-6), kind)
            if kind == 'round': rows.append((x, y, f'Ø{a:.1f}', what))
            elif kind == 'slot':
                rows.append((x, y, f'slot {L.FADER_SLOT[0]:.1f} x {L.FADER_SLOT[1]:.1f}, rot {a:g}', what))
                ca, sa = math.cos(math.radians(a)), -math.sin(math.radians(a))
                rows += [(x + u * ca, y + u * sa, f'Ø{L.FIX_D:.1f}', what + ' fixing') for u in (-L.FADER_SLOT[2], L.FADER_SLOT[2])]
            else:
                rows.append((x, y, f'Ø{L.XLR_CUT[0]:.1f}', what))
                ca, sa = math.cos(math.radians(a)), -math.sin(math.radians(a))
                rows += [(x + u * ca - v * sa, y + u * sa + v * ca, f'Ø{L.FIX_D:.1f}', what + ' fixing') for u, v in L.XLR_CUT[1]]
        rows += [(x, y, f'Ø{L.SCREW_D:.1f}', 'panel screw') for x, y in P.screws]
        rows += [(x, y, 'M3 blind stud, back side, not through',
                  f'{ref} {"jack-board standoff (bonds CHASSIS to the panel: metal contact)" if bd == "jack" else "main-board standoff"}')
                 for x, y, ref, bd in P.studs]
        rows += [(x, y, f'Ø{L.CSK_HOLE:.1f} through, countersunk 90° to Ø{L.CSK_D:.1f} (M3 flat head)',
                  f'{ref} jack-board standoff: ONLY IF NO WELDED STUDS (met1_ret1_review.md P4); a star washer under the standoff')
                 for x, y, ref, bd in P.studs if bd == 'jack']
        for x, y, s, what in sorted(rows, key=lambda r: (round(-r[1], 2), r[0])):
            w.writerow([f'{x - P.x0:.2f}', f'{P.y1 - y:.2f}', s, what])

# ---------------------------------------------------------------- checks
def check(P, circles, slots, shapes):
    """Problems as text lines; empty when the panel is buildable as drawn."""
    bad = []
    cuts = [('c', x, y, d / 2) for x, y, d in circles] + [('s', x, y, s) for (x, y, *_), s in
                                                          zip(slots, (slot_outline(*s_, 24) for s_ in slots))]
    def gap(a, b):
        if a[0] == 'c' and b[0] == 'c': return math.hypot(a[1] - b[1], a[2] - b[2]) - a[3] - b[3]
        c, s = (a, b) if a[0] == 'c' else (b, a)
        if c[0] == 's': return min(math.hypot(p[0] - q[0], p[1] - q[1]) for p in c[3] for q in s[3])
        pts = s[3]; return min(seg_dist((c[1], c[2]), pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts))) - c[3]
    for i in range(len(cuts)):
        for j in range(i + 1, len(cuts)):
            g = gap(cuts[i], cuts[j])
            if g < WEB: bad.append(f'web {g:.2f} mm between cut-outs at ({cuts[i][1]:.1f}, {cuts[i][2]:.1f}) and ({cuts[j][1]:.1f}, {cuts[j][2]:.1f})')
    def extent(c):
        if c[0] == 'c': return c[1] - c[3], c[2] - c[3], c[1] + c[3], c[2] + c[3]
        return (min(p[0] for p in c[3]), min(p[1] for p in c[3]), max(p[0] for p in c[3]), max(p[1] for p in c[3]))
    for c in cuts:
        x0, y0, x1, y1 = extent(c)
        e = min(x0 - P.x0, P.x1 - x1, y0 - P.y0, P.y1 - y1)
        if e < EDGE: bad.append(f'cut-out at ({c[1]:.1f}, {c[2]:.1f}) {e:.2f} mm from the plate edge')
        if (c[1], c[2]) not in P.screws and any(y1 > r0 and y0 < r1 for r0, r1 in RAILS):
            bad.append(f'cut-out at ({c[1]:.1f}, {c[2]:.1f}) over a frame rail')
    n_ink = 0
    for pts, (bx0, by0, bx1, by1) in shapes:
        if bx0 < P.x0 + INK_EDGE or bx1 > P.x1 - INK_EDGE or by0 < P.y0 + INK_EDGE or by1 > P.y1 - INK_EDGE:
            bad.append(f'print at ({bx0:.1f}, {by0:.1f}) within {INK_EDGE} mm of the plate edge'); continue
        for c in cuts:
            x0, y0, x1, y1 = extent(c)
            if bx1 < x0 - INK_GAP or bx0 > x1 + INK_GAP or by1 < y0 - INK_GAP or by0 > y1 + INK_GAP: continue
            if c[0] == 'c':
                dmin = min(math.hypot(p[0] - c[1], p[1] - c[2]) for p in pts)
                if dmin < c[3] + INK_GAP: n_ink += 1; bad.append(f'print {dmin - c[3]:+.2f} mm from the cut-out at ({c[1]:.1f}, {c[2]:.1f})'); break
            else:
                n_ink += 1; bad.append(f'print box touches the slot at ({c[1]:.1f}, {c[2]:.1f})'); break
    for x, y, ref, bd in P.studs:                    # without studs: the countersink, as a cut-out of its own
        if bd != 'jack': continue
        for c in cuts:
            g = gap(('c', x, y, L.CSK_D / 2), c)
            if g < WEB: bad.append(f'countersink {ref} at ({x:.1f}, {y:.1f}) {g:.2f} mm from the cut-out at ({c[1]:.1f}, {c[2]:.1f})')
        for pts, (bx0, by0, bx1, by1) in shapes:
            if bx1 < x - L.CSK_D / 2 - INK_GAP or bx0 > x + L.CSK_D / 2 + INK_GAP or by1 < y - L.CSK_D / 2 - INK_GAP or by0 > y + L.CSK_D / 2 + INK_GAP: continue
            dmin = min(math.hypot(p[0] - x, p[1] - y) for p in pts)
            if dmin < L.CSK_D / 2 + INK_GAP: bad.append(f'print {dmin - L.CSK_D / 2:+.2f} mm from the countersink {ref} at ({x:.1f}, {y:.1f})')
    for x, y, ref, bd in P.studs:                    # the stud's boss behind the plate stays clear of every front cut-out
        for c in cuts:
            g = gap(('c', x, y, STUD_BOSS / 2), c)
            if g < WEB: bad.append(f'stud {ref} ({bd}) at ({x:.1f}, {y:.1f}): its boss {g:.2f} mm from the cut-out at ({c[1]:.1f}, {c[2]:.1f})')
    return bad

# ---------------------------------------------------------------- main
def build(P, out, stem, fonts, numbered=None):
    circles, slots = P.cut(); shapes = ink(P, fonts)
    dxf(os.path.join(out, stem + '.dxf'), P, circles, slots, shapes)
    svg(os.path.join(out, stem + '.svg'), P, circles, slots, shapes)
    svg(os.path.join(out, stem + '_preview.svg'), P, circles, slots, shapes, preview=True)
    holes_csv(os.path.join(out, stem + '_holes.csv'), P)
    return circles, slots, shapes

def main():
    out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'panels')); os.makedirs(out, exist_ok=True)
    fonts = {b: Font(p) for b, p in FONTS.items()}
    rsvg = subprocess.run(['which', 'rsvg-convert'], capture_output=True, text=True).stdout.strip()
    ok = True
    for key in ('strip', 'group', 'master'):
        P = L.layout(key); circles, slots, shapes = build(P, out, key, fonts)
        bad = check(P, circles, slots, shapes)
        print(f'{key}: {P.x1 - P.x0:.2f} x {P.y1 - P.y0:.1f} mm, {len(circles)} holes, {len(slots)} slot, '
              f'{len(P.texts)} texts, {len(P.rects)} marks; {len(bad)} problems')
        for b in bad: print('   ', b)
        ok &= not bad
        if rsvg:
            subprocess.run([rsvg, '-f', 'pdf', '-o', os.path.join(out, key + '.pdf'), os.path.join(out, key + '.svg')], check=True)
            subprocess.run([rsvg, '-d', '150', '-p', '150', '-o', os.path.join(out, key + '.png'),
                            os.path.join(out, key + '_preview.svg')], check=True)
            os.remove(os.path.join(out, key + '_preview.svg'))
        if key in ('strip', 'group') and rsvg:            # numbered artwork, one page per module
            pages = []
            for n in range(1, 25 if key == 'strip' else 5):
                Pn = L.layout(key, number=n); c_, s_ = Pn.cut()
                pth = os.path.join(out, f'.{key}_{n:02d}.svg'); svg(pth, Pn, c_, s_, ink(Pn, fonts)); pages.append(pth)
            subprocess.run([rsvg, '-f', 'pdf', '-o', os.path.join(out, f'{key}_numbers.pdf')] + pages, check=True)
            for pth in pages: os.remove(pth)
    sys.exit(0 if ok else 1)

if __name__ == '__main__':
    main()
