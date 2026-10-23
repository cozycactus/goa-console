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
