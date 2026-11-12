"""Drawn schematic blocks for schgen.py: parts placed on the grid with rotation / mirror, real wires between pins,
labels only where a net leaves the drawing, junctions where wires meet. A block gets a draw function
(schgen.block(title, draw=fn)); fn(d) places every part and draws the wires through the Drawing d. Coordinates are
in grid units (G = 2.54 mm) relative to the block's origin, screen orientation (y down).
Before anything is written, check() proves the drawing: every connected group of pins, wires, labels and power
symbols carries one net, so a wire can't join two nets; tools/verify.py then checks the exported netlist."""
G = 2.54

def xform(px, py, rot=0, mirror=None):
    """Symbol-library pin offset (y up) -> schematic offset (y down) for a symbol at angle rot (CCW on screen),
    mirrored about its x axis ('x', y flips) or y axis ('y', x flips) after the rotation, as KiCad does."""
    x, y = px, -py
    for _ in range((rot // 90) % 4):
        x, y = y, -x
    if mirror == 'x': y = -y
    if mirror == 'y': x = -x
    return x, y

def snap(v): return round(v, 3)


class Drawing:
    def __init__(self, parts, pins_of, origin):
        self.parts, self.pins_of, self.ox, self.oy = parts, pins_of, origin[0], origin[1]
        self.place = {}            # (ref, unit) -> (x, y, rot, mirror) in mm, absolute
        self.wires = []            # [((x0, y0), (x1, y1))] mm
        self.ports = []            # (net, (x, y), side) labels
        self.gnds = []             # (net, (x, y), direction of the symbol: 'D' down, 'U' up, 'L', 'R')
        self.flags = []            # ((x, y), 'U' / 'D'): PWR_FLAGs of the drawing (not parts), see flag()
        self.notes = []            # (text, (x, y), size)
        self.height = 20           # grid units the block takes, set by the draw function
        self.textside = {}         # ref -> 'L' / 'R': which side of a vertical part its reference and value go
        self.fields = {}           # (ref, unit) -> (reference, value) places set by fld(): each (dx, dy, justify) or None
        self.unit = {}
        for pt in parts:
            for pn in pt['pins']: self.unit[(pt['ref'], pn)] = pt['unit']

    def xy(self, x, y): return (snap(self.ox + x * G), snap(self.oy + y * G))

    def shift(self, dx, dy):
        """Move the origin for everything drawn after this (grid units)."""
        self.ox += dx * G; self.oy += dy * G

    def at(self, ref, x, y, rot=0, mirror=None, unit=None, text=None):
        """Place a part (unit) with its origin at grid (x, y); text='L' puts a vertical part's fields on its left."""
        units = sorted({pt['unit'] for pt in self.parts if pt['ref'] == ref})
        if unit is None:
            if len(units) != 1: raise SystemExit(f'{ref}: give the unit ({units})')
            unit = units[0]
        if text:                                   # per unit; the whole part only when it has one unit
            self.textside[(ref, unit)] = text
            if len(units) == 1: self.textside[ref] = text
        self.place[(ref, unit)] = (snap(self.ox + x * G), snap(self.oy + y * G), rot, mirror)

    def fld(self, ref, ref_at=None, val_at=None, unit=None):
        """Explicit places for a part's reference and value, where the layout's defaults would collide: each (dx, dy) or
        (dx, dy, justify), in grid units from the part's origin as seen on the sheet (x right, y down); justify 'left'
        (the text starts at the point), 'right' (ends there) or none (centred on it). None keeps the default."""
        units = sorted({pt['unit'] for pt in self.parts if pt['ref'] == ref})
        if unit is None:
            if len(units) != 1: raise SystemExit(f'{ref}: give the unit ({units})')
            unit = units[0]
        norm = lambda f: f and (f[0] * G, f[1] * G, f[2] if len(f) > 2 else None)
        self.fields[(ref, unit)] = (norm(ref_at), norm(val_at))

    def nets(self, ref):
        """{pin: net} of a part (all its units)."""
        return {pn: net for pt in self.parts if pt['ref'] == ref for pn, net in pt['pins'].items()}

    def h(self, ref, x, y, left=None, text=None):
        """A two-pin part placed horizontally, the pin on net 'left' (default pin 1) on the left. Returns the net
        on its right."""
        n = self.nets(ref); first = '1' if left is None or n.get('1') == left else '2'
        if self.lib_horizontal(ref): rot = 0 if first == '1' else 180
        else: rot = 90 if first == '1' else 270
        self.at(ref, x, y, rot=rot, text=text)
        return n['2' if first == '1' else '1']

    def lib_horizontal(self, ref):
        """True when the library symbol has its two pins left and right (diodes, LEDs), not top and bottom."""
        pt = next(pt for pt in self.parts if pt['ref'] == ref)
        px, py = self.pins_of(pt['key'], pt['unit'])['1']
        return abs(px) > abs(py)

    def v(self, ref, x, y, top=None, text=None):
        """A two-pin part placed vertically, the pin on net 'top' (default pin 1) at the top. Returns the bottom net."""
        n = self.nets(ref); key = next(pt['key'] for pt in self.parts if pt['ref'] == ref)
        first = '1' if top is None or n.get('1') == top else '2'
        if self.lib_horizontal(ref):                              # diodes: K (1) on the left at rot 0
            rot = 270 if first == '1' else 90
        else:
            rot = 0 if first == '1' else 180
        self.at(ref, x, y, rot=rot, text=text)
        return n['2' if first == '1' else '1']

    def pin(self, ref, pn):
        pn = str(pn); unit = self.unit[(ref, pn)]
        cx, cy, rot, mir = self.place[(ref, unit)]
        key = next(pt['key'] for pt in self.parts if pt['ref'] == ref and pt['unit'] == unit)
        px, py = self.pins_of(key, unit)[pn]
        dx, dy = xform(px, py, rot, mir)
        return (snap(cx + dx), snap(cy + dy))

    def pt(self, p):
        """A point: (ref, pin) or a grid (x, y) pair of numbers."""
        if isinstance(p[0], str): return self.pin(*p)
        return self.xy(*p)

    def w(self, *pts):
        """Polyline through points: (ref, pin), grid (x, y), or 'h' / 'v' meaning: go horizontally / vertically first
        to reach the next point (an L)."""
        out, mode = [], None
        for p in pts:
            if isinstance(p, str): mode = p; continue
            q = self.pt(p)
            if out and mode and out[-1][0] != q[0] and out[-1][1] != q[1]:
                a = out[-1]; out.append((q[0], a[1]) if mode == 'h' else (a[0], q[1]))
            out.append(q); mode = None
        for a, b in zip(out, out[1:]):
            if a != b:
                if a[0] != b[0] and a[1] != b[1]: raise SystemExit(f'diagonal wire {a} -> {b}')
                self.wires.append((a, b))
        return out[-1]

    def port(self, net, p, side='L'):
        """A net label at point p; side = where the text goes ('L' text to the left, 'R', 'U', 'D')."""
        self.ports.append((net, self.pt(p), side))

    def gnd(self, p, net='GNDA', d='D'):
        self.gnds.append((net, self.pt(p), d))

    def flag(self, p, d='U'):
        """A PWR_FLAG at point p (the end of a stub off the rail it marks), standing up ('U') or hanging ('D'): for a rail
        that only power symbols and passive pins are on, so that ERC sees it driven. It belongs to the drawing, as a
        power symbol does: no part, nothing in the netlist."""
        self.flags.append((self.pt(p), d))

    def note(self, text, p, size=1.5):
        self.notes.append((text, self.xy(*p), size))


def on_seg(p, a, b, interior=False):
    (x, y), (x0, y0), (x1, y1) = p, a, b
    if x0 == x1 == x and min(y0, y1) <= y <= max(y0, y1): pass
    elif y0 == y1 == y and min(x0, x1) <= x <= max(x0, x1): pass
    else: return False
    return not (interior and p in (a, b))


def check(d, pin_nets):
    """pin_nets: [(ref, pin, net, (x, y))] for every pin of the block. Returns (groups, junctions):
    groups = list of sets of item ids, with a net each; raises on a group carrying two nets."""
    items = []                                     # (kind, net or None, points / segment)
    for ref, pn, net, p in pin_nets: items.append(('pin', net, p, (ref, pn)))
    for a, b in d.wires: items.append(('wire', None, (a, b), None))
    for net, p, _ in d.ports: items.append(('port', net, p, None))
    for net, p, _ in d.gnds: items.append(('gnd', net, p, None))
    par = list(range(len(items)))
    def f(i):
        while par[i] != i: par[i] = par[par[i]]; i = par[i]
        return i
    def u(i, j): par[f(i)] = f(j)
    pts = lambda it: list(it[2]) if it[0] == 'wire' else [it[2]]
    segs = [(i, it[2]) for i, it in enumerate(items) if it[0] == 'wire']
    by_pt = {}
    for i, it in enumerate(items):
        for p in pts(it): by_pt.setdefault(p, []).append(i)
    for p, ids in by_pt.items():
        for j in ids[1:]: u(ids[0], j)
    junctions = set()
    for p, ids in by_pt.items():                   # a point inside another wire joins it (T): needs a junction
        for i, (a, b) in segs:
            if on_seg(p, a, b, interior=True):
                for j in ids: u(i, j)
                junctions.add(p)
        ends = sum(1 for j in ids if items[j][0] in ('wire', 'pin'))
        if ends >= 3: junctions.add(p)
    groups = {}
    for i in range(len(items)): groups.setdefault(f(i), []).append(i)
    out = []
    for g in groups.values():
        nets = {items[i][1] for i in g if items[i][1] is not None}
        if len(nets) > 1:
            who = [items[i][3] or items[i][0] for i in g]
            raise SystemExit(f'drawing joins nets {sorted(nets)}: {who}')
        out.append((nets.pop() if nets else None, [items[i] for i in g]))
    return out, junctions
