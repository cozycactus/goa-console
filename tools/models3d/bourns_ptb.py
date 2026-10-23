"""Bourns PTB0143-2010APA103 / PTB0144-2010APA103 slide potentiometer: 100 mm travel (01), no dust cover (4), single /
dual gang (3 / 4), PC pins down (2), no detent (0), 10 mm lever (10), AP metal lever (4.0 split fork, for standard 4 mm
fader knobs), audio taper, 10K.
Datasheet: Bourns PTB series, REV. 08/20, https://www.bourns.com/docs/Product-Datasheets/ptb.pdf (PTB100 drawing on
page 2, lever styles on page 1); overall size 128 x 16 x 8 mm also on DigiKey's listing. Undimensioned details are
scaled from the drawing (side view about 22 px/mm at 1200 dpi).
Footprint (tools/footprints.py): pin 1 at the origin, pins 1, 2 (1', 2') at x 0, pin 3 (3') at x -127.5, body and slot
centred on (-63.75, -1.9), kinked mounting tabs 38.8 / 43.7 either side of the centre (towards pin 3 / pin 1).
Spec 16.2 stack: 3.5 mm spacers on the two M3 holes from the 8.0 mm cover top to the panel underside at 11.5, M3 pan
head screws (length assumed 8 mm) from the panel top; the lever ends 10.0 above the cover = 5.0 above the panel top.
Leads are cut at z -3 (the drawing has 3.9 below the seating plane)."""
import math
from .geom import Mesh
from . import STACK
from .knob import CAPS

NAME = 'Bourns PTB0143 / PTB0144-2010APA103 slide pot, 100 mm, AP lever (Bourns PTB datasheet REV. 08/20)'
FOOTPRINTS = {'Potentiometer_Bourns_PTB0143_Slide_100mm': dict(dual=False),
              'Potentiometer_Bourns_PTB0144_Slide_100mm_Dual': dict(dual=True)}
FEATURE = (-63.75, -1.9)
MOUNT = 'main'
TRAVEL = 100.0
XC, YC = FEATURE
L, W, H, T = 128.0, 15.0, 8.0, 0.6     # cover 128.0 x 15.0, seating plane to cover top 8.0 (drawing); sheet ~0.6
WB, BX = 16.0, 64.3                    # base flange 16.0 wide (end view, DigiKey), 0.3 past the cover ends (side view)
SLOT, SW, HOLE = 57.0, 3.1, 60.0       # slot to 2.9 short of the holes, 3.1 wide; 2 x M3 x 0.5 holes 120.0 apart
ZB, ZS, ZW = 1.85, 1.35, 3.15          # base flange bottom, substrate bottom, flange top = cover wall bottom
CUT = 6.2                              # cover side walls cut back to z 4.05 for 6.2 mm at each end (side view)
CRIMP = (-55.2, -28.1, 0.0, 28.1, 55.2)   # cover tabs crimped under the substrate (side view)
TABS = ((-38.8, -1), (43.7, 1))        # snap-in legs from the centre (hole layout), kink direction
FOOT = 40.0                            # cover feet to the seating plane, 3.0 wide, at +-40.0 (side view, both walls in end view)


def pins(dual=False):
    p = [(0.0, 0.0), (0.0, 3.8), (-127.5, 0.0)] + ([(0.0, -3.8), (0.0, -7.6), (-127.5, -3.8)] if dual else [])
    return p + [(XC + dx, YC) for dx, _ in TABS]


def _xprism(m, prof, x0, x1, mat):
    """Profile [(y, z)] extruded along x."""
    return m.merge(Mesh().prism([(-z, y) for y, z in prof], x0, x1, mat).rotate('y', 90))


def _yprism(m, prof, y0, y1, mat):
    """Profile [(x, z)] extruded along y."""
    return m.merge(Mesh().prism(list(prof), -y1, -y0, mat).rotate('x', 90))


def _holed(rect, hole, w0, w1, mat, to_xyz, seg=16):
    """Plate (u0, v0, u1, v1) from w0 to w1 with a round hole (cu, cv, r); to_xyz maps (u, v, w) to the frame."""
    (u0, v0, u1, v1), (cu, cv, r) = rect, hole
    cn = [math.atan2(b - cv, a - cu) % (2 * math.pi) for a, b in ((u1, v1), (u0, v1), (u0, v0), (u1, v0))]
    angs = sorted(cn + [a for a in (2 * math.pi * k / seg for k in range(seg)) if min(abs(a - c) for c in cn) > 1e-6])
    def ray(a):
        dx, dy = math.cos(a), math.sin(a); ts = []
        if abs(dx) > 1e-9: ts.append(((u1 if dx > 0 else u0) - cu) / dx)
        if abs(dy) > 1e-9: ts.append(((v1 if dy > 0 else v0) - cv) / dy)
        t = min(ts); return cu + t * dx, cv + t * dy
    n = len(angs); inner = [(cu + r * math.cos(a), cv + r * math.sin(a)) for a in angs]; outer = [ray(a) for a in angs]
    verts = [to_xyz(u, v, w) for w in (w0, w1) for ring in (inner, outer) for u, v in ring]
    faces = []
    for k in range(n):
        k1 = (k + 1) % n
        faces += [(k, k1, n + k1, n + k), (2 * n + k, 2 * n + k1, 3 * n + k1, 3 * n + k),
                  (k, k1, 2 * n + k1, 2 * n + k), (n + k, n + k1, 3 * n + k1, 3 * n + k)]
    return Mesh().add(verts, faces, mat)


def _cover(m):
    """Steel cover: top plate with the slot and two M3 holes, side walls with rounded top edges, end walls, crimp tabs."""
    def side(x0, x1, s, y_in, zb, r=0.8):
        yo = YC + s * W / 2
        arc = [(yo - s * r + s * r * math.cos(math.radians(a)), H - r + r * math.sin(math.radians(a))) for a in range(0, 91, 18)]
        _xprism(m, [(yo, zb)] + arc + [(YC + s * y_in, H), (YC + s * y_in, H - T), (yo - s * T, H - T), (yo - s * T, zb)],
                x0, x1, 'metal_steel')
    for s in (-1, 1):
        side(XC - SLOT, XC + SLOT, s, SW / 2, ZW)
        for e in (-1, 1):
            a, b, c = XC + e * SLOT, XC + e * (L / 2 - CUT), XC + e * L / 2
            side(min(a, b), max(a, b), s, 2.5, ZW); side(min(b, c), max(b, c), s, 2.5, 4.05)
    for e in (-1, 1):
        x0, x1 = sorted((XC + e * SLOT, XC + e * L / 2))
        m.merge(_holed((x0, YC - 2.5, x1, YC + 2.5), (XC + e * HOLE, YC, 1.25), H - T, H, 'metal_steel', lambda u, v, w: (u, v, w)))
        m.box(XC + e * (L / 2 - T), YC - W / 2 + T, 4.05, XC + e * L / 2, YC + W / 2 - T, H - T, 'metal_steel')
    for cx in CRIMP:
        for s in (-1, 1):
            m.box(XC + cx - 0.5, YC + s * (W / 2 - 0.4), 1.05, XC + cx + 0.5, YC + s * W / 2, ZW, 'metal_steel')
            m.box(XC + cx - 0.5, YC + s * (W / 2 - 1.5), 1.05, XC + cx + 0.5, YC + s * W / 2, ZS, 'metal_steel')


def _base(m):
    """Moulded base flange (16.0 wide, notched for the crimp tabs and cover feet), phenolic substrate, end blocks."""
    notches = sorted([(XC + c - 0.7, XC + c + 0.7) for c in CRIMP] + [(XC + e * FOOT - 1.6, XC + e * FOOT + 1.6) for e in (-1, 1)])
    y0, y1 = YC - WB / 2, YC + WB / 2
    pts = [(XC - BX, y0)]
    for a, b in notches: pts += [(a, y0), (a, y0 + 1.0), (b, y0 + 1.0), (b, y0)]
    pts += [(XC + BX, y0), (XC + BX, y1)]
    for a, b in reversed(notches): pts += [(b, y1), (b, y1 - 1.0), (a, y1 - 1.0), (a, y1)]
    m.prism(pts + [(XC - BX, y1)], ZB, ZW, 'plastic_white')
    m.box(XC - L / 2, YC - 7.4, ZS, XC + L / 2, YC + 7.4, ZB, 'plastic_dark')
    for e in (-1, 1):
        m.box(XC + e * (L / 2 - T), YC - 6.4, ZW, XC + e * (L / 2 - CUT), YC + 6.4, 4.05, 'plastic_white')
        m.box(XC + e * 14.0 - 1.6, YC - 1.0, 0.0, XC + e * 14.0 + 1.6, YC + 1.0, ZS, 'plastic_white')   # standoffs (side view)


def _tab(m, dx, o):
    """Cover foot down both side walls to the board at +-FOOT with a bridge under the substrate; kinked snap-in leg on
    the centreline at the tab hole, hanging from the substrate (the -38.8 leg lies under its foot, the 43.7 one does not)."""
    xt, xf = XC + dx, XC + math.copysign(FOOT, dx)
    for s in (-1, 1): m.box(xf - 1.5, YC + s * (W / 2 - 0.4), 0.0, xf + 1.5, YC + s * W / 2, ZW, 'metal_steel')
    m.box(xf - 1.5, YC - W / 2, 1.0, xf + 1.5, YC + W / 2, ZS, 'metal_steel')
    path = [(0.0, ZS), (0.0, -0.3), (0.9 * o, -2.2), (0.39 * o, -3.0)]    # kink 0.9 out at z -2.2 (side view)
    _yprism(m, [(xt + x - 0.25, z) for x, z in path] + [(xt + x + 0.25, z) for x, z in reversed(path)],
            YC - 0.8, YC + 0.8, 'metal_steel')


def _terminal(m, x, y):
    """Flat PC terminal (1.3 x 0.6, shoulder 2.1 wide to the seating plane) riveted through the substrate."""
    i = 1 if x < XC else -1
    m.loft([[(x + a * 0.2, y + b * 0.35, -3.0) for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))],
            [(x + a * 0.3, y + b * 0.65, -2.6) for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))]], 'metal_tin')
    m.box(x - 0.3, y - 0.65, -2.6, x + 0.3, y + 0.65, 0.0, 'metal_tin')
    m.box(x - 0.3, y - 1.05, 0.0, x + 0.3, y + 1.05, ZS, 'metal_tin')
    m.box(x + i * 0.6, y - 0.8, 1.05, x + i * 3.4, y + 0.8, ZS, 'metal_tin')
    m.box(x - i * 0.3, y - 0.8, ZW, x + i * 4.0, y + 0.8, ZW + 0.35, 'metal_tin')


def build(dual=False, pos=0.75):
    """pos: lever position, 0 = pin-1 end (bottom of travel) .. 1 = pin-3 end."""
    m = Mesh(); pz = STACK['panel_z0']
    _cover(m); _base(m)
    for dx, o in TABS: _tab(m, dx, o)
    for x, y in pins(dual)[:-2]: _terminal(m, x, y)
    m.box(XC - SLOT, YC - 2.4, 6.3, XC + SLOT, YC + 2.4, 6.5, 'plastic_black')            # slider rail, seen in the slot
    lx = XC + TRAVEL / 2 - TRAVEL * pos
    m.box(lx - 6.0, YC - SW / 2 + 0.05, 6.5, lx + 6.0, YC + SW / 2 - 0.05, H - T - 0.05, 'plastic_dark')   # slider, 12.0 (top view)
    m.merge(_ap_lever().translate(lx, YC, 0.0))
    for e in (-1, 1):
        hx = XC + e * HOLE
        m.tube(hx, YC, H, pz, 2.5, 1.6, 'metal_alu', 32)                                  # 3.5 mm spacer, 5 OD
        m.cyl(hx, YC, H - 3.0, pz + STACK['panel_t'], 1.45, 'metal_zinc', 16)             # M3 x 8 shank
    return m


def _ap_lever(seg=8):
    """AP lever (datasheet p. 1): 5.0 wide root to 8.8 below the top, then a 4.0 wide fork with a 1.0 slit, round-ended
    prongs, 10.0 above the cover, 1.3 thick (across the travel); from z 6.9 in the slider. Centred on x 0, y 0."""
    zb, zt, t = H + 10.0 - 8.8, H + 10.0, 1.3
    arc = lambda cu, cw, r, a0, a1: [(cu + r * math.cos(math.radians(a0 + (a1 - a0) * k / seg)),
                                      cw + r * math.sin(math.radians(a0 + (a1 - a0) * k / seg))) for k in range(seg + 1)]
    out = ([(-2.5, 6.9), (2.5, 6.9), (2.5, zb), (2.0, zb)] + arc(1.25, zt - 0.75, 0.75, 0, 180)
           + arc(0.0, zb + 0.5, 0.5, 0, -180) + arc(-1.25, zt - 0.75, 0.75, 0, 180) + [(-2.0, zb), (-2.5, zb)])
    return Mesh().prism(out, -t / 2, t / 2, 'metal_gold').rotate('x', 90)       # profile (u, w) -> x, z; thickness in y


def _screw():
    m = Mesh().lathe([(2.75, 0.0), (2.75, 1.2), (2.55, 1.8), (2.1, 2.2), (1.2, 2.4), (0.0, 2.4)], 'metal_zinc', seg=28)
    m.box(-1.3, -0.3, 2.25, 1.3, 0.3, 2.42, 'plastic_black'); m.box(-0.3, -1.3, 2.25, 0.3, 1.3, 2.42, 'plastic_black')
    return m


def panel(dual=False, colour='grey', pos=0.75):
    """Fader knob on the lever (placeholder: 12 x 22 cap with a finger dish and a coloured line, bottom 0.8 above the
    panel, socket for the 4.0 x 1.3 AP fork) and the two M3 pan head screws; FEATURE frame, z = 0 on the panel top."""
    m = Mesh(); dx = TRAVEL / 2 - TRAVEL * pos
    dish = [(4.4 - 0.88 * k, 12.6 - 1.1 * (1 - ((4.4 - 0.88 * k) / 4.4) ** 2)) for k in range(11)]
    _yprism(m, [(-6.0, 0.8), (6.0, 0.8), (6.0, 2.6), (4.8, 12.0), (4.6, 12.6)] + dish + [(-4.6, 12.6), (-4.8, 12.0), (-6.0, 2.6)],
            -11.0, 11.0, 'plastic_black')
    line = CAPS.get(colour, 'plastic_grey')
    m.box(-0.35, -11.02, 11.45, 0.35, 11.02, 11.55, line)
    for s in (-1, 1): m.box(-0.35, s * 11.0, 3.0, 0.35, s * 11.05, 11.5, line)
    m.translate(dx)
    for e in (-1, 1): m.merge(_screw().translate(e * HOLE))
    return m
