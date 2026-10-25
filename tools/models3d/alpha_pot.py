"""Alpha RD901F-40 (single) / RD902F-40 (dual) 9 mm vertical potentiometer with bracket, metal M7 bushing and round
1/4" shaft, as fitted: RD901F-40-15R1-A10K / -B10K-0CD, RD902F-40-15R1-A10K (spec 16.1). "15" = shaft length L 15 mm from
the mounting face, "R1" = round shaft Ø6.35, bushing code blank = M7 x 0.75 x 5 mm, "-40" = vertical PC mount.
Single: Alpha drawing SLH-211-414 "RD901F-40-(L)R1-XXX-0XD" (2022-06-24) in spec SP26020021 (2026-02-04,
https://www.taydaelectronics.com/datasheets/files/SP26020021_RD901F-40-15R1-B10K-0CD-1.pdf). Dual: outline RD902F-40-00D in
Alpha's "9mm Single Metal Shaft, Multi-Ganged Series" catalogue (2024-11-11,
http://www.taiwanalpha.com.tw/downloads?target=products&id=113); R1 shaft, nut and terminals as the single.
Frame: shaft axis at (7.5, 2.5); u = x - 7.5 (towards +x away from the terminals), v = y - 2.5 (towards the tabs).
On the 16.2 stack the mounting face (10 mm) meets the 1.5 mm spacer washer under the panel exactly; the 5 mm bushing
leaves 2.0 mm of thread above the panel, the nut's own thickness, so the supplied 0.4 mm washer is left out."""
import math
from .geom import Mesh
from . import STACK
from . import knob as _knob

NAME = 'Alpha RD901F-40 / RD902F-40 9 mm vertical pot, M7 bushing, 15 mm R1 shaft'
FOOTPRINTS = {'Potentiometer_Alpha_RD901F-40-00D_Single_Vertical': dict(dual=False),
              'Potentiometer_Alpha_RD902F-40-00D_Dual_Vertical': dict(dual=True)}
FEATURE = (7.5, 2.5)
MOUNT = 'main'
AX, AY = FEATURE
FACE, BUSH, L, D_SHAFT = 10.0, 5.0, 15.0, 6.35      # mounting face above the seating plane, bushing, shaft (SLH-211-414)
NUT_AF, NUT_T = 10.0, 2.0                           # M7 x 0.75 hex nut, across flats / thick (SLH-211-414)
SPACER = (7.2, 10.0, 1.5)                           # spec 16.2 M7 spacer washer: bore (= panel hole), OD (ours), thick


def tab_v(dual):
    """Case-tab slot centres from the shaft axis: 11.4 / 11.3 over the 1.8 slots -> 9.6 / 9.5 apart."""
    return 4.75 if dual else 4.8


def pins(dual=False):
    p = [(0.0, 0.0), (0.0, 2.5), (0.0, 5.0)] + ([(-2.5, 0.0), (-2.5, 2.5), (-2.5, 5.0)] if dual else [])
    return p + [(AX, AY - tab_v(dual)), (AX, AY + tab_v(dual))]


def _yz_prism(m, poly, x0, x1, mat):
    """Polygon [(y, z)] (convex) extruded along x from x0 to x1."""
    n = len(poly); v = [(x0, y, z) for y, z in poly] + [(x1, y, z) for y, z in poly]
    f = [(k, (k + 1) % n, n + (k + 1) % n, n + k) for k in range(n)]
    f += [(0, k, k + 1) for k in range(1, n - 1)] + [(n, n + k + 1, n + k) for k in range(1, n - 1)]
    return m.add(v, f, mat)


def _terminal(m, x, y, ze):
    """Flat PC terminal, 0.3 thick: leaves the body's terminal face (u -6.5) at height ze, bends down at x; 1.8 wide
    down to 1.0 above the board, then 0.9 wide with a round end (terminal detail: 4.5 mm, 3.5 of it below the seating
    plane; cut at z = -3 here as every lead in this package)."""
    t, w, wt = 0.15, 0.9, 0.45
    m.box(x + t, y - w, ze - t, AX - 6.1, y + w, ze + t, 'metal_tin')
    m.hcyl('y', x + t, ze - t, y - w, y + w, 2 * t, 'metal_tin', 12)         # 90 deg bend
    m.box(x - t, y - w, 1.3, x + t, y + w, ze - t, 'metal_tin')
    m.loft([[(x - t, y - w, 1.3), (x + t, y - w, 1.3), (x + t, y + w, 1.3), (x - t, y + w, 1.3)],
            [(x - t, y - wt, 1.0), (x + t, y - wt, 1.0), (x + t, y + wt, 1.0), (x - t, y + wt, 1.0)]], 'metal_tin')
    m.box(x - t, y - wt, -3.0 + wt, x + t, y + wt, 1.0, 'metal_tin')
    m.hcyl('x', y, -3.0 + wt, x - t, x + t, wt, 'metal_tin', 10)


def _case_tab(m, side, dual, zb, zc):
    """Bracket PC tab: 3.0 wide shoulder from the body's rear face down to the seating plane, 1.0 wide tip with a round
    end (side view), sprung outwards below the board (the outline shows the tabs to 12.0 overall). The body sides are
    the plastic housing (no side plate in SLH-211-414 or in Alpha's catalogue pictures)."""
    yc = AY + side * tab_v(dual); t = 0.15
    m.box(AX - 1.5, yc - t, 0.0, AX + 1.5, yc + t, zb + 0.3, 'metal_tin')              # shoulder, 3.0 wide
    m.box(AX - 0.5, yc - t, -2.5, AX + 0.5, yc + t, 0.0, 'metal_tin')                  # tip, 1.0 wide
    m.hcyl('y', AX, -2.5, yc - t, yc + t, 0.5, 'metal_tin', 12)
    o = yc + side * t
    _yz_prism(m, [(o, -1.75), (o + side * 1.05, -1.95), (o + side * 0.2, -2.55), (o, -2.55)], AX - 0.5, AX + 0.5, 'metal_tin')


def _thread(z0, z1, r_maj, pitch, end_chamfer=0.3):
    """Lathe profile of a fine external thread (V grooves) from z0 to z1, plain first 0.3 mm, chamfered end."""
    r_min = r_maj - 0.54 * pitch; prof = [(r_maj, z0), (r_maj, z0 + 0.3)]
    z = z0 + 0.3; k = 0
    while z + pitch / 2 < z1 - end_chamfer:
        z += pitch / 2; k += 1; prof.append((r_min if k % 2 else r_maj, z))
    return prof + [(r_maj - end_chamfer, z1)]


def build(dual=False):
    m = Mesh(); pz = STACK['panel_z0']
    x0, x1, y0, y1 = AX - 6.5, AX + 4.85, AY - 4.75, AY + 4.75     # 9.5 x (6.5 + 4.85) outline (front view)
    zb, zc = (1.0, 7.4) if dual else (2.5, 7.6)                     # body underside, front cover joint (side views)
    if dual:
        m.box(x0 + 0.05, y0 + 0.05, zb, x1 - 0.05, y1 - 0.05, 3.5, 'plastic_black', r=0.4)    # rear gang (R2)
        m.box(x0 + 0.05, y0 + 0.05, 3.5, x1 - 0.05, y1 - 0.05, zc, 'plastic_dark', r=0.4)     # front gang (R1)
    else:
        m.box(x0 + 0.05, y0 + 0.05, zb, x1 - 0.05, y1 - 0.05, zc, 'plastic_black', r=0.4)
    m.box(x0, y0, zc, x1, y1, FACE, 'metal_tin', r=0.6, chamfer=0.15)                        # metal front cover
    for s in (-1, 1):
        _case_tab(m, s, dual, zb, zc)
    for u, v in ((3.7, 3.9), (-3.5, -4.0)):                                                   # corner rivets (front view)
        m.cyl(AX + u, AY + v, 0.0, zb, 0.5, 'metal_nickel', 12)                               # tails = standoff feet
        m.cyl(AX + u, AY + v, FACE - 0.01, FACE + 0.02, 0.95, 'plastic_black', 16)
        m.tube(AX + u, AY + v, FACE, FACE + 0.15, 0.55, 0.25, 'metal_nickel', 12)
    m.box(AX - 6.4, AY - 1.0, FACE, AX - 5.6, AY + 1.0, FACE + 0.8, 'metal_tin')              # anti-rotation lug, 2 x 0.8, r 6
    m.lathe(_thread(FACE, FACE + BUSH, 3.5, 0.75) + [(2.65, FACE + BUSH), (2.65, FACE + BUSH - 0.6)],
            'metal_nickel', AX, AY, 40, cap0=False)                                           # M7 x 0.75 bushing
    rs, zt = D_SHAFT / 2, FACE + L
    m.lathe([(2.5, FACE + BUSH - 0.6), (2.5, FACE + BUSH + 0.3), (rs, FACE + BUSH + 0.3), (rs, zt - 0.5),
             (rs - 0.5, zt)], 'metal_steel', AX, AY, 40, cap0=False)                          # journal, Ø6.35 shaft, C0.5
    rows = ((0.0, 2.35), (-2.5, 4.85)) if dual else ((0.0, 5.1),)                             # (x, exit height): R2, R1
    for x, ze in rows:
        for y in (0.0, 2.5, 5.0): _terminal(m, x, y, ze)
    m.tube(AX, AY, FACE, pz, SPACER[1] / 2, SPACER[0] / 2, 'metal_steel', 40)                 # 1.5 mm spacer washer
    return m


def nut():
    """M7 x 0.75 hex nut, 10 across flats, 2.0 thick, both faces chamfered (corners only), on z = 0."""
    n, rc, rb = 48, NUT_AF / 2 + 0.1, 3.45
    def hexr(a):
        return NUT_AF / 2 / math.cos((a % (math.pi / 3)) - math.pi / 6)
    ang = [2 * math.pi * k / n for k in range(n)]
    ring = lambda z, clip=99.0: [(min(hexr(a), clip) * math.cos(a), min(hexr(a), clip) * math.sin(a), z) for a in ang]
    bore = lambda z: [(rb * math.cos(a), rb * math.sin(a), z) for a in ang]
    m = Mesh()
    m.loft([ring(0.0, rc), ring(0.45), ring(NUT_T - 0.45), ring(NUT_T, rc)], 'metal_nickel', False, False)
    m.loft([bore(NUT_T), bore(0.0)], 'metal_nickel', False, False)
    for z in (0.0, NUT_T):
        m.loft([ring(z, rc), bore(z)], 'metal_nickel', False, False)
    return m


def panel(dual=False, colour='grey', angle=0.0):
    """Nut on the panel (the bushing ends flush with it) and the knob on the shaft above it."""
    return nut().merge(_knob.build(colour=colour, angle=angle))
