"""Neutrik NC3MAV 3-pole male XLR receptacle, vertical PCB, A series (not D-size): plastic housing (UL94 V-0) mounted
BEHIND the panel, its 21.8 nose through a >= 22 cut-out, two self-tapping screws from the front into the diagonal
bosses (>= 3.2 panel holes 19.8 x 19.8 apart), separate ground contact G. Drawing ST-NC3MAV index C (Neutrik AG,
12.01.10), https://datasheet.lcsc.com/lcsc/1912111437_Neutrik-NC3MAV_C368483.pdf: PCB to panel underside 24, housing
16.2 deep behind the panel, nose 2.7, flange 12.5 / 12.8 from the axis, pins 3.5 into the board. The pin depth of the
mating face and the insert are not dimensioned (estimated). Footprint frame: barrel axis at (3.81, 0) on the pin 1-2
line, pin 3 and G towards +y (the drawing's front view as it stands)."""
import math
from .geom import Mesh

NAME = 'Neutrik NC3MAV'
FOOTPRINTS = {'Jack_XLR_Neutrik_NC3MAV_Vertical': {}}
FEATURE = (3.81, 0.0)
MOUNT = 'jack'

AX, AY = FEATURE
Z_PANEL = 24.0                  # PCB top to panel underside / housing front face
Z_BACK = Z_PANEL - 16.2         # contact block rear face, 7.8 above the PCB (the pins span the rest)
Z_BODY, Z_BOSS = 12.3, (17.8, 19.5)   # housing rear wall; screw boss steps (side view)
NOSE, R_NOSE, R_BORE = 2.7, 10.9, 7.8  # nose 21.8 x 2.7, bore 15.6 (front view)
Z_INSERT = 15.7                 # insert face, 11 below the nose front (estimate)
EARS = ((-9.9, -9.9), (9.9, 9.9))     # screw bosses, 19.8 x 19.8 diagonal (upper left / lower right from the front)
LEADS = ((0.0, 0.0), (7.62, 0.0), (3.81, 3.81))
G = (3.81, 8.25)
MATING = ((-4.05, 0.0), (4.05, 0.0), (0.0, 3.95))   # contact pins on the insert, from the axis (front view)
N = 72                          # samples round the axis; the ears fall on samples (45 / 225 degrees)
ANG = [2 * math.pi * k / N for k in range(N)]


def pins():
    return list(LEADS) + [G]


def _smin(a, b, k):
    h = max(k - abs(a - b), 0.0) / k
    return min(a, b) - h * h * k / 4


def _round(u, v):
    """Housing behind the flange: 22.9 round with flats 21.8 apart (rear view), the top cut at 11.3, bottom at 10.5."""
    return max(math.hypot(u, v) - 11.45, abs(u) - 10.9, -v - 11.3, v - 10.5)


def _flange(u, v, re):
    """Front of the housing: the flats run out into the two screw bosses (radii re, per ear), filleted (front view)."""
    box = max(abs(u) - 10.9, -v - 11.3, v - 10.5)
    d = min(_round(u, v), max(box, u, v), max(box, -u, -v))
    return _smin(d, min(math.hypot(u - cu, v - cv) - r for (cu, cv), r in zip(EARS, re)), 1.2)


def _radii(sdf):
    """Outline as a radius per sample angle (the shapes are star-shaped about the axis): outermost zero of sdf."""
    out = []
    for a in ANG:
        c, s = math.cos(a), math.sin(a); t = 17.0
        while sdf(t * c, t * s) > 0: t -= 0.1
        lo, hi = t, t + 0.1
        for _ in range(16):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if sdf(mid * c, mid * s) <= 0 else (lo, mid)
        out.append(lo)
    return out


def _bore(a, front):
    """Bore radius: key groove at the top (4.7 wide), and at the front the latch notch at the bottom (front view)."""
    c, s = math.cos(a), math.sin(a)
    if s < 0 and abs(c) < 0.30: return 8.05
    if front and s > 0 and abs(c) < 0.16: return 8.3
    return R_BORE


def _ring(rs, z):
    return [(AX + r * math.cos(a), AY + r * math.sin(a), z) for r, a in zip(rs, ANG)]


def _yz(m, pts, x0, x1, mat):
    """Outline [(y, z)] extruded along x from x0 to x1."""
    m.merge(Mesh().prism([(-z, y) for y, z in pts], x0, x1, mat).rotate('y', 90))


def _housing(m):
    # upper-left boss R2.6 then R2.9 (12.8 from the axis), lower-right R2.6 (12.5; rear view, NC3MAV-1 front view)
    rnd, fl1, fl2 = _radii(_round), _radii(lambda u, v: _flange(u, v, (2.6, 2.6))), _radii(lambda u, v: _flange(u, v, (2.9, 2.6)))
    circ = lambda r: [r] * N
    key, front = [_bore(a, False) for a in ANG], [_bore(a, True) for a in ANG]
    zf = Z_PANEL + NOSE
    rings = [_ring(rnd, Z_BODY), _ring(rnd, Z_BOSS[0]), _ring(fl1, Z_BOSS[0]), _ring(fl1, Z_BOSS[1]),
             _ring(fl2, Z_BOSS[1]), _ring(fl2, Z_PANEL), _ring(circ(R_NOSE), Z_PANEL), _ring(circ(R_NOSE), zf - 0.25),
             _ring(circ(R_NOSE - 0.25), zf), _ring([r + 0.25 for r in front], zf), _ring(front, zf - 0.25),
             _ring(front, zf - 2.2), _ring(key, zf - 2.2), _ring(key, Z_INSERT)]
    m.loft(rings, 'plastic_black')                                                 # caps: rear wall, insert face
    for u, v in MATING:                                                            # contact pins 2.38, tip edge to 2.17
        m.lathe([(0.0, Z_INSERT), (1.19, Z_INSERT), (1.19, zf - 2.53), (1.085, zf - 2.42), (0.0, zf - 2.42)],
                'metal_nickel', AX + u, AY + v, 20)


def _contact_block(m):
    """Rear of the housing: a boss round each PCB pin joined by a cross rib, the rib rising to the top (rear view),
    and the lower step the ground contact enters (side view)."""
    for x, y in LEADS: m.cyl(x, y, Z_BACK, Z_BODY, 2.2, 'plastic_black', 24)
    m.box(LEADS[0][0], -0.7, Z_BACK, LEADS[1][0], 0.7, Z_BODY, 'plastic_black')
    m.box(AX - 0.7, 0.0, Z_BACK, AX + 0.7, LEADS[2][1], Z_BODY, 'plastic_black')
    _yz(m, [(-0.7, Z_BACK), (-2.15, Z_BACK), (-5.0, Z_BODY), (-0.7, Z_BODY)], AX - 0.6, AX + 0.6, 'plastic_black')
    m.box(AX - 5.0, 7.9, 10.8, AX + 5.0, 10.45, Z_BODY, 'plastic_black')


def _foot(m):
    """Seating bar under the housing with two split snap pegs (the shared horizontal-PCB moulding; on the vertical
    part they stand off the board edge-on). Pegs drawn at u -/+3.81 (front view) and at two depths (side view);
    taken as one at each, diagonally."""
    m.box(AX - 6.5, 10.4, 5.0, AX + 8.2, 12.3, 15.1, 'plastic_black', chamfer=0.3)
    m.box(AX - 6.5, 10.4, 15.1, AX + 8.2, 11.6, Z_PANEL, 'plastic_black')
    for u, z0, z1, base in ((-3.81, 14.35, 16.0, 12.3), (3.81, 19.4, 21.1, 11.6)):
        x0, x1 = AX + u - 0.62, AX + u + 0.62
        for za, zb, out in ((z0, z0 + 0.45, -0.2), (z1 - 0.45, z1, 0.2)):
            m.box(x0, base - 0.1, za, x1, 13.1, zb, 'plastic_black')
            m.box(x0, 13.1, min(za, za + out), x1, 13.75, max(zb, zb + out), 'plastic_black')
            m.box(x0, 13.75, za + 0.05, x1, 14.0, zb - 0.05, 'plastic_black')


def _pcb_pins(m):
    """Contacts 1-3 below the housing: 1.7 shank standing on the board, 1.0 neck, 1.54 teardrop snap tip 3.5 down."""
    for x, y in LEADS:
        m.lathe([(0.0, -3.5), (0.45, -3.42), (0.66, -3.2), (0.76, -2.9), (0.77, -2.2), (0.5, -0.47), (0.5, 0.0),
                 (0.85, 0.0), (0.85, Z_BACK - 1.0), (0.93, Z_BACK - 1.0), (0.93, Z_BACK + 0.1)], 'metal_nickel', x, y, 16)


def _ground(m):
    """Ground contact G: 1.0 x 0.5 strip from the board, jogged 1.8 outwards and up into the housing's lower step."""
    zs = [-3.5, 4.3] + [4.3 + 2.9 * k / 8 for k in range(1, 9)] + [10.8]
    rings = []
    for z in zs:
        t = min(max((z - 4.3) / 2.9, 0.0), 1.0)
        v = G[1] + 1.8 * t * t * (3 - 2 * t)
        rings.append([(G[0] - 0.5, v - 0.25, z), (G[0] + 0.5, v - 0.25, z), (G[0] + 0.5, v + 0.25, z), (G[0] - 0.5, v + 0.25, z)])
    m.loft(rings, 'metal_tin')


def build():
    m = Mesh()
    _housing(m); _contact_block(m); _foot(m); _pcb_pins(m); _ground(m)
    return m


def panel():
    """On the panel top (z = 0), around the barrel axis: the two M3 pan-head self-tapping screws into the bosses
    (the nose, 1.2 proud of a 1.5 panel, is part of build())."""
    m = Mesh()
    for u, v in EARS:
        m.lathe([(0.0, 1.8), (1.4, 1.78), (2.3, 1.55), (2.75, 1.05), (2.8, 0.6), (2.8, 0.0)], 'metal_zinc', u, v, 24)
        m.box(u - 1.2, v - 0.25, 1.62, u + 1.2, v + 0.25, 1.83, 'plastic_black')
        m.box(u - 0.25, v - 1.2, 1.62, u + 0.25, v + 1.2, 1.83, 'plastic_black')
    return m
