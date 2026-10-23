"""Keystone 1287-ST 0.250" (6.35 mm) PC quick-fit male terminal, Sturdi-Mount: Keystone catalog M75 p. 65,
https://www.keyelco.com/userAssets/file/K75p65.pdf. One piece of 0.032" (0.81) tin-plated brass in the footprint's
x-z plane: tab with a 0.070" hole and a bevelled lead-in, wider shoulder, two legs 0.200" (5.08) apart in 0.052"
(1.3) holes, and the Sturdi-Mount lance formed out of the shoulder to both sides (3.1 REF) as the seating feet. The
stamped legs end 3.8 below the seating plane, as drawn (not cut to 3)."""
import math
from .geom import Mesh

NAME = 'Keystone 1287-ST quick-fit tab (Sturdi-Mount)'
FOOTPRINTS = {'Keystone_1287-ST_FastOn_Tab_6.35mm': {}}
FEATURE = None
MOUNT = 'main'
MAT = 'metal_tin'

T = 0.81 / 2                 # half the 0.032" stock
TAB, SH = 6.35 / 2, 7.9 / 2  # 0.250" tab, 0.312" shoulder (half widths)
LEG = 3.8                    # 0.150" of leg below the seating plane (shoulder bottom)
TOP = 14.0 - LEG             # 0.552" overall: tab tip 10.2 above the board
SH_TOP = TOP - 7.9           # 0.312" from the tip down to the shoulder: 2.3
HOLE_Z, HOLE_R = TOP - 4.5, 1.8 / 2   # 0.070" hole, centre 0.178" below the tip
FOOT = 3.1 / 2               # Sturdi-Mount lance, 0.120" REF across both sides


def pins():
    return [(-2.54, 0.0), (2.54, 0.0)]


def _flat(m, outline):
    """Outline [(x, z)] cut from the 0.81 stock (y -T..T)."""
    m.merge(Mesh().prism(outline, -T, T, MAT).rotate('x', 90))


def _leg(cx):
    """Leg outline, seating plane down and back up: 0.050" (1.27, .045" min) wide, straight for 1.45, tapering to a
    round tip (drawing)."""
    r, zt = 0.45, -LEG + 0.45
    pts = [(cx - 0.635, 0.0), (cx - 0.635, -1.45), (cx - r, zt)]
    pts += [(cx - r * math.cos(math.pi * k / 8), zt - r * math.sin(math.pi * k / 8)) for k in range(1, 8)]
    return pts + [(cx + r, zt), (cx + 0.635, -1.45), (cx + 0.635, 0.0)]


def _holed(m, z0, z1, seg=32):
    """Tab section x -TAB..TAB, z z0..z1 (square, so the corners fall on the ring) with the round through hole."""
    zc, h = (z0 + z1) / 2, (z1 - z0) / 2
    ang = [2 * math.pi * k / seg for k in range(seg)]
    hole = [(HOLE_R * math.cos(a), zc + HOLE_R * math.sin(a)) for a in ang]
    edge = [(h * math.cos(a) / max(abs(math.cos(a)), abs(math.sin(a))),
             zc + h * math.sin(a) / max(abs(math.cos(a)), abs(math.sin(a)))) for a in ang]
    v = [(x, y, z) for y in (-T, T) for x, z in hole + edge]        # front hole 0.., front edge seg.., back +2seg
    f = []
    for k in range(seg):
        k1 = (k + 1) % seg
        for b in (0, 2 * seg):
            f.append((b + k, b + k1, b + seg + k1, b + seg + k))                  # faces
        f.append((k, k1, 2 * seg + k1, 2 * seg + k))                             # hole wall
        if abs(abs(edge[k][0]) - h) < 1e-9 and abs(abs(edge[k1][0]) - h) < 1e-9 and edge[k][0] * edge[k1][0] > 0:
            f.append((seg + k, seg + k1, 3 * seg + k1, 3 * seg + k))             # tab sides
    m.add(v, f, MAT)


def _lance(m, x0, x1, side, round0, round1):
    """Sturdi-Mount foot on face `side` (-1 front, +1 back) over x0..x1: a hood formed out of the shoulder, quarter-
    round in side view (about 2.0 high at the face, out to FOOT), its ends rounded over round0 / round1 mm."""
    d0 = T - 0.05                                # starts just inside the stock
    t_face = math.acos(T / FOOT)
    prof = [(d0, 0.0), (FOOT, 0.0), (FOOT, 0.45)]
    prof += [(FOOT * math.cos(t), 0.45 + FOOT * math.sin(t)) for t in (t_face * k / 6 for k in range(1, 7))]
    prof += [(d0, prof[-1][1])]
    xs = [x0 + round0 * (1 - math.cos(math.pi / 2 * k / 4)) for k in range(5)] if round0 else [x0]
    xs += [x1 - round1 * (1 - math.cos(math.pi / 2 * k / 4)) for k in range(4, -1, -1)] if round1 else [x1]
    rings = []
    for x in xs:
        s = 1.0
        if round0 and x - x0 < round0: s = math.sqrt(max(0.0, 1 - ((round0 - (x - x0)) / round0) ** 2))
        if round1 and x1 - x < round1: s = math.sqrt(max(0.0, 1 - ((round1 - (x1 - x)) / round1) ** 2))
        rings.append([(side * (d0 + (d - d0) * s), z * s, x) for d, z in prof])     # lofted along x, capped in y-z
    h = Mesh().loft(rings, MAT)
    h.v = [(x, y, z) for y, z, x in h.v]
    m.merge(h)


def build():
    m = Mesh()
    z0 = HOLE_Z - TAB                                                              # square holed section
    _flat(m, [(-SH, SH_TOP), (-SH, 0.0)] + _leg(-2.54) + _leg(2.54) + [(SH, 0.0), (SH, SH_TOP), (TAB, SH_TOP), (TAB, z0),
                                                                      (-TAB, z0), (-TAB, SH_TOP)])
    _holed(m, z0, HOLE_Z + TAB)
    zb, c = TOP - 0.7, 0.45                    # lead-in: both faces bevelled over the top 0.7, corners chamfered 0.45
    rings = []
    for z, hx, hy in ((HOLE_Z + TAB, TAB, T), (zb, TAB, T), (TOP - c, TAB, T - 0.2 * (TOP - c - zb) / 0.7), (TOP, TAB - c, 0.2)):
        rings.append([(-hx, -hy, z), (hx, -hy, z), (hx, hy, z), (-hx, hy, z)])
    m.loft(rings, MAT)
    _lance(m, -1.73, -0.15, -1, 0.8, 0.0)       # formed forward, rounded hood (catalog photo / front view)
    _lance(m, -0.05, 0.75, 1, 0.0, 0.35)        # formed backward, narrow tongue
    return m


def panel():
    return None
