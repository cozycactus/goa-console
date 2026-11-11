"""Cables between the boards: IDC sockets crimped on flat ribbon, folded ribbon, round cable. Geometry only, in board
millimetres (x right, y down, z up); tools/console_3d.py places them. A 2xN IDC socket (2.54 mm grid, 1.27 mm
ribbon) is 2.54 N + 5.08 long and 6.0 wide, 6.4 mm body + 2.6 mm cover; the ribbon (2N conductors, 2.54 N wide,
0.9 thick) runs between body and cover, square to the socket's long side."""
import math
from .geom import Mesh

THICK = 0.9
SOCKET_BODY, SOCKET_COVER = 6.4, 2.6


def _sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def _add(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def _mul(a, k): return (a[0] * k, a[1] * k, a[2] * k)
def _dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def _cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def _unit(a):
    L = math.sqrt(_dot(a, a)) or 1.0
    return (a[0] / L, a[1] / L, a[2] / L)


def idc_socket(n, cx, cy, z_face, along='y', down=True, key=-1):
    """2xN IDC socket centred on (cx, cy), long side along 'x' or 'y', mating face at z_face, body towards -z
    (down=True: a socket on a bottom-side header), polarising key on the long side towards -y / -x (key=-1, for 'x' /
    'y') or +y / +x (key=1). Returns (mesh, z of the ribbon centre)."""
    L, W = 2.54 * n + 5.08, 6.0; s = -1 if down else 1
    hx, hy = (L / 2, W / 2) if along == 'x' else (W / 2, L / 2)
    zb = z_face + s * SOCKET_BODY; zr = zb + s * THICK / 2; zc = zb + s * THICK
    m = Mesh().box(cx - hx, cy - hy, z_face, cx + hx, cy + hy, zb, 'plastic_dark', chamfer=0.2)
    m.box(cx - hx, cy - hy, zc, cx + hx, cy + hy, zc + s * SOCKET_COVER, 'plastic_dark', chamfer=0.2)
    if along == 'x': m.box(cx - 2.25, cy, z_face + s * 1.0, cx + 2.25, cy + key * (W / 2 + 0.9), z_face + s * 5.0, 'plastic_dark')
    else: m.box(cx, cy - 2.25, z_face + s * 1.0, cx + key * (W / 2 + 0.9), cy + 2.25, z_face + s * 5.0, 'plastic_dark')
    for k in (-1, 1):                                                         # cover latches on the short ends
        if along == 'x': m.box(cx + k * hx, cy - 1.2, zb - s * 1.5, cx + k * (hx + 0.6), cy + 1.2, zc + s * SOCKET_COVER, 'plastic_dark')
        else: m.box(cx - 1.2, cy + k * hy, zb - s * 1.5, cx + 1.2, cy + k * (hy + 0.6), zc + s * SOCKET_COVER, 'plastic_dark')
    return m, zr


def ribbon(path, wdirs, width, stripe=+1, thick=THICK):
    """Flat cable along a polyline of centre points [(x, y, z)], the width along wdirs (one per point, made square to
    the path); the pin-1 stripe on the +wdir edge (stripe=+1), the other one (-1) or none (0). Ends are square to the path."""
    m = Mesh(); n = len(path)
    if len(wdirs) == 1: wdirs = wdirs * n
    rings, rings_s = [], []
    for i, p in enumerate(path):
        t = _unit(_sub(path[min(i + 1, n - 1)], path[max(i - 1, 0)]))
        w = _unit(_sub(wdirs[i], _mul(t, _dot(wdirs[i], t)))); h = _unit(_cross(t, w))
        def ring(c, half, ht):
            return [_add(_add(c, _mul(w, half)), _mul(h, ht)), _add(_add(c, _mul(w, -half)), _mul(h, ht)),
                    _add(_add(c, _mul(w, -half)), _mul(h, -ht)), _add(_add(c, _mul(w, half)), _mul(h, -ht))]
        rings.append(ring(p, width / 2, thick / 2))
        rings_s.append(ring(_add(p, _mul(w, stripe * (width / 2 - 0.65))), 0.66, thick / 2 + 0.02))
    m.loft(rings, 'ribbon_grey')
    if stripe: m.loft(rings_s, 'ribbon_red')
    return m


def flat_leg(a0, a1, b0, b1, z, mat='ribbon_grey', thick=THICK):
    """A straight flat piece lying in the plane z, between end line a0-a1 and end line b0-b1 ((x, y) each; a0-b0 and
    a1-b1 are its two edges). A 45-degree fold is two legs sharing one end line, one thickness apart in z."""
    lo = [(a0[0], a0[1], z - thick / 2), (a1[0], a1[1], z - thick / 2), (b1[0], b1[1], z - thick / 2), (b0[0], b0[1], z - thick / 2)]
    hi = [(x, y, z + thick / 2) for x, y, _ in lo]
    return Mesh().loft([lo, hi], mat)


HALF = 3.0                                    # half an IDC socket's width: the cable leaves the socket here
RED = 1.32                                    # width of the stripe drawn on a flat piece

def _unit2(a):
    L = math.hypot(a[0], a[1]) or 1.0
    return (a[0] / L, a[1] / L)

def _mirror(v, c):
    """the plan vector v mirrored in a crease along the unit vector c: what a flat fold does to a cable's directions"""
    d = v[0] * c[0] + v[1] * c[1]
    return (2 * d * c[0] - v[0], 2 * d * c[1] - v[1])

def _hit(s, u, p, c):
    """where the line from s along u meets the crease through p along c"""
    t = ((p[0] - s[0]) * c[1] - (p[1] - s[1]) * c[0]) / (u[0] * c[1] - u[1] * c[0])
    return (s[0] + u[0] * t, s[1] + u[1] * t)


def link_route(j, m, bx, clear=()):
    """Two-fold route of a flat cable between two IDC sockets that both lie along y (the group's jack-board links):
    out of j along x, folded into a run towards m, folded again, into m along x. j, m: dicts with n (pins per row),
    x, y (socket centre) and pin1 (x, y); bx: the board's (x0, x1), the cable has to stay inside it; clear: x ranges
    (x0, x1) the second fold must stay out of (another socket at the same level).
    A fold mirrors the cable in its crease, so the stripe edge follows from pin 1 of j, and a route counts only when
    it brings the stripe to m's pin-1 end. Returns (dj, dm, xj, xm, rejected): the way out of j (-1 / +1 along x),
    the direction of travel into m, the run's x at the first and second fold (they differ when the run has to
    slant; the creases are then a little off 45 degrees), and why the other routes fail. Raises AssertionError when
    no route works: the headers' pin 1 is then wrong for a cable without a twist or a third turn-over."""
    h = 1.27 * j['n']
    sj = 1 if j['pin1'][1] > j['y'] else -1; sm = 1 if m['pin1'][1] > m['y'] else -1
    found, why = [], []
    for dj in (-1, 1):
        for dm in (-1, 1):
            tag = f"out of the jack board's socket to {'+x' if dj > 0 else '-x'}, into the main board's travelling {'+x' if dm > 0 else '-x'}"
            wj = (j['x'] + HALF + h, bx[1] - h) if dj > 0 else (bx[0] + h, j['x'] - HALF - h)
            lo, hi = (bx[0] + h, m['x'] - HALF - h) if dm > 0 else (m['x'] + HALF + h, bx[1] - h)
            for c0, c1 in clear:
                if dm > 0 and c1 <= m['x']: lo = max(lo, c1 + h)
                if dm < 0 and c0 >= m['x']: hi = min(hi, c0 - h)
            if wj[0] > wj[1] + 1e-6: why.append(f'{tag}: the run lies {wj[0] - wj[1]:.2f} mm outside the board at the jack board'); continue
            if lo > hi + 1e-6: why.append(f'{tag}: the run lies {lo - hi:.2f} mm outside the board at the main board'); continue
            if wj[1] < lo: xj, xm = wj[1], lo
            elif hi < wj[0]: xj, xm = wj[0], hi
            else: xj = xm = (max(wj[0], lo) + min(wj[1], hi)) / 2
            ur = _unit2((xm - xj, m['y'] - j['y']))
            s = _mirror(_mirror((0.0, sj), _unit2((dj + ur[0], ur[1]))), _unit2((ur[0] + dm, ur[1])))
            if s[1] * sm < 0.99: why.append(f'{tag}: the stripe arrives at the wrong end of the main board\'s header'); continue
            found.append((abs(xm - xj), dj, dm, xj, xm))
    assert found, 'jack-board link: no two-fold route brings pin 1 to pin 1 inside the board. ' + '; '.join(why)
    _, dj, dm, xj, xm = min(found)
    return dj, dm, xj, xm, why


def folded_link(j, m, bx, wrap=(False, False), drop=0.0, clear=(), block=(), zs=None):
    """The cable of link_route as a mesh. j, m as there plus z (the ribbon's centre in the socket; both sockets hang
    under their boards). wrap: (at j, at m), the socket's strain-relief wrap: the cable leaves the socket on the far
    side and is doubled back under the cover, so it lies one cover + one cable thickness lower and can pass under a
    neighbouring socket or a tall part. drop: how much lower still the second fold lies (a cable crossing under
    another one); it comes up again under m's own socket, so it needs the wrap at m. block: plan boxes (x0, y0, x1,
    y1) of the other sockets on j's board; an unwrapped cable may not leave through one. zs: (y0, y1) between which
    the run changes level, by default the last 45 to 8 mm before the second fold (the group's main board has 16 mm
    cans, C14 / C20, further up the run's way).
    Layers: at each fold the run is the lower layer. Returns (mesh, info); info has the route, the two fold
    positions, the run's stripe edge ('left' / 'right', seen from above looking from the jack board to the main
    board, x to the right), the centre-line length between the two socket centres and the levels."""
    h = 1.27 * j['n']; T = THICK; W = SOCKET_COVER + T; R = W / 2
    sj = 1 if j['pin1'][1] > j['y'] else -1; sm = 1 if m['pin1'][1] > m['y'] else -1
    dj, dm, xj, xm, why = link_route(j, m, bx, clear)
    assert wrap[1] or not drop, 'a dropped second fold needs the wrap at the main board\'s socket to come up again'
    if not wrap[0]:                                         # the way out of j at socket level: nothing in it
        a, b = sorted((j['x'] + dj * HALF, xj + dj * h))
        hit = [q for q in block if q[0] < b and a < q[2] and q[1] < j['y'] + h and j['y'] - h < q[3]]
        assert not hit, f'jack-board link: another socket stands in the way out of the socket at x {j["x"]:.2f}: wrap it'
    p1, p2 = (xj, j['y']), (xm, m['y']); run = math.hypot(xm - xj, m['y'] - j['y'])
    ur = _unit2((xm - xj, m['y'] - j['y'])); pr = (-ur[1], ur[0])
    c1 = _unit2((dj + ur[0], ur[1])); c2 = _unit2((ur[0] + dm, ur[1]))
    sr = _mirror((0.0, sj), c1); sig = 1 if sr[0] * pr[0] + sr[1] * pr[1] > 0 else -1     # the run's stripe edge, along pr
    z1 = j['z'] - (W if wrap[0] else 0.0); za = z1 - T      # first leg, run at the first fold
    ze = m['z'] - (W if wrap[1] else 0.0); z2 = ze - drop; zb = z2 - T    # into m, second leg at its fold, run there
    me = Mesh()
    def strip(s, u, p, p0, c, z):
        """flat piece from the end line through s (across p) along u to the crease through p0 along c, with its stripe"""
        for o0, o1, mat, th in ((-h, h, 'ribbon_grey', T), (p[2] * (h - RED), p[2] * h, 'ribbon_red', T + 0.04)):
            a0, a1 = (s[0] + p[0] * o0, s[1] + p[1] * o0), (s[0] + p[0] * o1, s[1] + p[1] * o1)
            me.merge(flat_leg(a0, a1, _hit(a0, u, p0, c), _hit(a1, u, p0, c), z, mat, th))
    # out of j
    xs = j['x'] - dj * HALF if wrap[0] else j['x'] + dj * HALF
    if wrap[0]:
        arc = [(xs - dj * R * math.sin(math.pi * k / 10), j['y'], j['z'] - R + R * math.cos(math.pi * k / 10)) for k in range(11)]
        me.merge(ribbon([(j['x'], j['y'], j['z'])] + arc, [(0, sj, 0)], 2 * h))
    strip((xs, j['y']), (dj, 0), (0, 1, sj), p1, c1, z1)
    # the run: flat at each fold, the level change between
    la = lb = 1.2 * h + 1.0
    sa = (p1[0] + ur[0] * la, p1[1] + ur[1] * la); sb = (p2[0] - ur[0] * lb, p2[1] - ur[1] * lb)
    strip(sa, (-ur[0], -ur[1]), (pr[0], pr[1], sig), p1, c1, za)
    strip(sb, ur, (pr[0], pr[1], sig), p2, c2, zb)
    y0, y1 = zs or (m['y'] - h - 45.0, m['y'] - h - 8.0)
    def zrun(y):
        v = min(1.0, max(0.0, (y - y0) / (y1 - y0))); return za + (zb - za) * v * v * (3 - 2 * v)
    path = []
    for k in range(65):
        x, y = sa[0] + (sb[0] - sa[0]) * k / 64, sa[1] + (sb[1] - sa[1]) * k / 64
        path.append((x, y, zrun(y)))
    me.merge(ribbon(path, [(pr[0], pr[1], 0)], 2 * h, stripe=sig))
    rise = sum(math.dist(a, b) for a, b in zip(path, path[1:])) - math.dist(sa, sb)
    # into m: flat from the second fold to where the leg is full width, then (wrapped) under the socket and round its cover
    near, far = m['x'] - dm * HALF, m['x'] + dm * HALF
    ex = max(dm * _hit((xm, m['y'] + o), (dm, 0), p2, c2)[0] for o in (-h, h))
    xf = dm * max(ex, dm * near)
    strip((xf, m['y']), (-dm, 0), (0, 1, sm), p2, c2, z2)
    path = []
    if wrap[1]:
        for k in range(13):
            v = k / 12; path.append((xf + (far - xf) * v, m['y'], z2 + (ze - z2) * v * v * (3 - 2 * v)))
        path += [(far + dm * R * math.sin(math.pi * k / 10), m['y'], ze + R - R * math.cos(math.pi * k / 10)) for k in range(1, 11)]
        path.append((m['x'], m['y'], m['z']))
    elif abs(near - xf) > 1e-6: path = [(xf, m['y'], z2), (near, m['y'], z2)]
    if path: me.merge(ribbon(path, [(0, sm, 0)], 2 * h))
    length = abs(xj - j['x']) + run + rise + abs(xm - m['x']) + sum(wrap) * (2 * HALF + math.pi * R)
    return me, dict(dj=dj, dm=dm, xj=xj, xm=xm, stripe='left' if sr[0] < 0 else 'right', length=length, rejected=why,
                    z=dict(leg1=z1, run1=za, run2=zb, leg2=z2, under_m=ze), zrun=zrun)


def smooth(points, k=8):
    """Catmull-Rom through control points [(x, y, z)], k samples per span."""
    P = [points[0]] + list(points) + [points[-1]]; out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for j in range(k):
            t = j / k; t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * (2 * p1[c] + (-p0[c] + p2[c]) * t + (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c]) * t2
                                    + (-p0[c] + 3 * p1[c] - 3 * p2[c] + p3[c]) * t3) for c in range(3)))
    out.append(points[-1])
    return out


def through(sockets, flat=3.0, tail=1.5, sag=0.05, n=16):
    """Centre line of a flat cable crimped through IDC sockets [(x, y, z)] in a row along x: flat inside each socket
    (flat = half the socket's width), a shallow bow hanging between two sockets (sag x the free length), a level
    change taken as a smooth S, cut `tail` past the end sockets. The slope is zero at every socket, so the cable
    leaves each one square, as a crimped cable does."""
    pts = [(sockets[0][0] - flat - tail,) + tuple(sockets[0][1:])]
    for i, (x, y, z) in enumerate(sockets):
        pts += [(x - flat, y, z), (x + flat, y, z)]
        if i + 1 < len(sockets):
            x1, y1, z1 = sockets[i + 1]; a, b = x + flat, x1 - flat
            for j in range(1, n):
                u = j / n; st = u * u * (3 - 2 * u)
                pts.append((a + (b - a) * u, y + (y1 - y) * st, z + (z1 - z) * st - sag * (b - a) * math.sin(math.pi * u) ** 2))
    pts.append((sockets[-1][0] + flat + tail,) + tuple(sockets[-1][1:]))
    return pts


def fillet(points, r=8.0, k=6):
    """Polyline [(x, y, z)] with every corner rounded to about radius r (less where a leg is short): the straight
    runs and bends of a stiff wire."""
    out = [tuple(points[0])]
    for a, b, c in zip(points, points[1:], points[2:]):
        u, v = _sub(a, b), _sub(c, b); lu, lv = math.sqrt(_dot(u, u)), math.sqrt(_dot(v, v))
        if lu < 1e-6 or lv < 1e-6: continue
        u, v = _mul(u, 1 / lu), _mul(v, 1 / lv); half = math.acos(max(-1.0, min(1.0, _dot(u, v)))) / 2
        if half > math.pi / 2 - 1e-3: out.append(tuple(b)); continue
        d = min(r / math.tan(half), lu / 2, lv / 2)
        p0, p1 = _add(b, _mul(u, d)), _add(b, _mul(v, d))
        for j in range(k + 1):                               # a quadratic Bezier through the corner
            t = j / k; out.append(_add(_add(_mul(p0, (1 - t) ** 2), _mul(b, 2 * t * (1 - t))), _mul(p1, t * t)))
    out.append(tuple(points[-1]))
    return out


def round_cable(path, r, mat='rubber_black', seg=16):
    """Round cable along a polyline [(x, y, z)]."""
    n = len(path); rings = []; prev_w = None
    for i, p in enumerate(path):
        t = _unit(_sub(path[min(i + 1, n - 1)], path[max(i - 1, 0)]))
        ref = prev_w or ((0, 0, 1) if abs(t[2]) < 0.9 else (1, 0, 0))
        w = _unit(_sub(ref, _mul(t, _dot(ref, t)))); h = _cross(t, w); prev_w = w
        rings.append([_add(p, _add(_mul(w, r * math.cos(2 * math.pi * k / seg)), _mul(h, r * math.sin(2 * math.pi * k / seg))))
                      for k in range(seg)])
    return Mesh().loft(rings, mat)
