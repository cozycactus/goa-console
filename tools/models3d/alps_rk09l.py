"""ALPS RK09L1240015: 9 mm vertical dual-unit pot (10 kOhm 1B, centre detent), snap-in bracket, metal M9 bushing and a
6 mm flatted shaft: the strip's pan pot RV8 (spec 12, 16.1; decided 2026-10-25). Drawing No.7 of ALPS's "Rotary
Potentiometer (Metal shaft type)" catalogue (RV01, update 2510, tech.alpsalpine.com/assets/catalog/product-catalog-rv-01.en.pdf):
L1 15 (shaft from the mounting face), LB 5 (bushing), l1 7 (flat), M9 x 0.75, shaft Ø6 with the flat at 4.5, body 10.7
wide, 6.5 / 4.85 from the shaft axis to the terminal side / the far side (front view), 10 from the seating plane to the
mounting face (side view), terminals 2 x 3 at 2.5, snap-in legs 9.5 apart in 1.8 x 1.1 slots.
Frame: KiCad's Potentiometer_Alps_RK09L_Double_Vertical: shaft axis at (10, 2.5) from pin 1; pins 1-3 in the row at
x 0 (rear gang), 4-6 at x 2.5. The nut (M9: not dimensioned in the catalogue) is drawn 12 AF x 2.0 thick: check a
sample; on the 16.2 stack (1.5 spacer + 1.5 panel) the 5 mm bushing leaves 2.0 for it, as with the Alpha pots."""
import math
from .geom import Mesh
from . import STACK
from . import knob as _knob

NAME = 'ALPS RK09L1240015 9 mm vertical dual pot, centre detent, M9 bushing, 6 mm D shaft (catalogue RV01 Drawing No.7)'
FOOTPRINTS = {'Potentiometer_Alps_RK09L_Double_Vertical': dict()}
FEATURE = (10.0, 2.5)
MOUNT = 'main'
AX, AY = FEATURE
FACE, BUSH, L, D_SHAFT, FLAT, L_FLAT = 10.0, 5.0, 15.0, 6.0, 4.5, 7.0
NUT_AF, NUT_T = 12.0, 2.0                           # M9 x 0.75 hex nut (assumed: not in the catalogue)
SPACER = (9.5, 11.0, 1.5)                           # spec 16.2 spacer washer for M9: bore (= panel hole), OD, thick
HOLE = 9.5                                          # panel hole


def pins():
    return [(x, y) for x in (0.0, 2.5) for y in (0.0, 2.5, 5.0)] + [(AX, AY - 4.75), (AX, AY + 4.75)]


def _thread(z0, z1, r_maj, pitch, end_chamfer=0.3):
    r_min = r_maj - 0.54 * pitch; prof = [(r_maj, z0), (r_maj, z0 + 0.3)]
    z = z0 + 0.3; k = 0
    while z + pitch / 2 < z1 - end_chamfer:
        z += pitch / 2; k += 1; prof.append((r_min if k % 2 else r_maj, z))
    return prof + [(r_maj - end_chamfer, z1)]


def _terminal(m, x, y, ze):
    """Flat PC terminal from the body's terminal face (x AX - 6.5) at height ze, bent down at x to the board."""
    t, w = 0.15, 0.45
    m.box(x - t, y - w, ze - t, AX - 6.4, y + w, ze + t, 'metal_tin')
    m.box(x - t, y - w, -3.0, x + t, y + w, ze + t, 'metal_tin')


def _snap_leg(m, side):
    """Snap-in leg in its 1.8 x 1.1 slot: a strip from the body down through the board, a barb under it."""
    yc = AY + side * 4.75; t = 0.25
    m.box(AX - 0.8, yc - t, -2.2, AX + 0.8, yc + t, 3.0, 'metal_tin')
    m.box(AX - 0.8, yc + side * t - (0.35 if side > 0 else 0), -1.9,
          AX + 0.8, yc + side * t + (0.35 if side < 0 else 0), -1.4, 'metal_tin')


def _shaft(m):
    """Ø6 shaft from the bushing to its top, the last 7 mm flatted to 4.5 across (flat towards -y, the pointer)."""
    r = D_SHAFT / 2; z1 = FACE + L; zf = z1 - L_FLAT
    m.lathe([(r - 0.6, FACE + BUSH - 0.6), (r - 0.6, FACE + BUSH + 0.3), (r, FACE + BUSH + 0.3), (r, zf)],
            'metal_steel', AX, AY, 40, cap0=False, cap1=False)
    cut = FLAT - r                                  # the flat lies this far from the axis
    ring = lambda z, rr: [(AX + rr * math.cos(a), AY + max(rr * math.sin(a), -cut), z)
                          for a in [2 * math.pi * k / 40 for k in range(40)]]
    m.loft([ring(zf, r), ring(z1 - 0.4, r), ring(z1, r - 0.4)], 'metal_steel', cap0=False, cap1=True)


def build():
    m = Mesh(); pz = STACK['panel_z0']
    x0, x1, y0, y1 = AX - 6.5, AX + 4.85, AY - 5.35, AY + 5.35         # 10.7 wide, 6.5 / 4.85 about the axis
    m.box(x0 + 0.05, y0 + 0.05, 0.6, x1 - 0.05, y1 - 0.05, 3.6, 'plastic_black', r=0.4)   # rear gang (pins 1-3)
    m.box(x0 + 0.05, y0 + 0.05, 3.6, x1 - 0.05, y1 - 0.05, 7.2, 'plastic_dark', r=0.4)    # front gang (pins 4-6)
    m.box(x0, y0, 7.2, x1, y1, FACE, 'metal_tin', r=0.6, chamfer=0.15)                   # metal frame / detent cover
    for s in (-1, 1): _snap_leg(m, s)
    for x, ze in ((0.0, 2.1), (2.5, 5.7)):                                                # rear row lower, front higher
        for y in (0.0, 2.5, 5.0): _terminal(m, x, y, ze)
    m.lathe(_thread(FACE, FACE + BUSH, 4.5, 0.75) + [(3.1, FACE + BUSH), (3.1, FACE + BUSH - 0.6)],
            'metal_nickel', AX, AY, 48, cap0=False)                                       # M9 x 0.75 bushing
    _shaft(m)
    m.tube(AX, AY, FACE, pz, SPACER[1] / 2, SPACER[0] / 2, 'metal_steel', 40)            # 1.5 mm spacer washer
    return m


def nut():
    """M9 x 0.75 hex nut, NUT_AF across flats, NUT_T thick, corners chamfered, on z = 0."""
    n, rc, rb = 48, NUT_AF / 2 + 0.1, 4.45
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


def panel(colour='grey', angle=0.0):
    """Nut on the panel and the knob (6 mm bore: the same knob family as the 1/4" pots, its 6 mm version)."""
    return nut().merge(_knob.build(colour=colour, angle=angle, bore=D_SHAFT))
