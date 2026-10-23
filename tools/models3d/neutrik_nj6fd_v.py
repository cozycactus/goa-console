"""Neutrik NJ6FD-V 1/4" stereo jack, 3 x switching (T/TN/R/RN/S/SN), vertical PCB, all plastic, rear mounted through
a >= 12.0 panel hole and held by its snap-on / twist-off POM cap (no thread, no nut). Neutrik's own NJ6FD-V drawing
(nj6fd-v-2.pdf) could not be fetched (neutrik.com 503, not archived), so the housing follows the NJ*FD-V family drawing
(* = 2, 3, 5, 6) in Neutrik's product guide "02 Neutrik PG E - Section Plugs & Jacks - 202104-V22", p. 17
(https://www.neutrik.com/media/10096/download/, archive.org 2024-06-29), and the NJ3FD-V drawing 3102 St 07 15
(03.02.98, https://www.neutrik.com/media/8597/download/nj3fd-v-3.pdf, archive.org 2023-06-06): PCB to panel underside
24.0, panel 1.2-1.5, cap front 9.0 above the panel underside, 4.0 of lead below the PCB, body 12.8 x 15.0, cap
14.5 / SW12; product page (archive.org 2025-07-03): cap POM, rear mounting. Leads at the KiCad footprint's pads
(its R, S, T and peg pattern is the NJ3FD-V layout turned 180 degrees; TN, RN, SN are unverified). Footprint frame:
jack axis at (0, 5.72), T side towards -y."""
import math
from .geom import Mesh
from . import STACK

NAME = 'Neutrik NJ6FD-V'
FOOTPRINTS = {'Jack_6.35mm_Neutrik_NJ6FD-V_Vertical': {}}
FEATURE = (0.0, 5.72)
MOUNT = 'jack'

CY = FEATURE[1]
Z_PANEL = 24.0                      # PCB top to panel underside (= flange front), family drawing
CAP_FRONT = 9.0                     # cap front above the panel underside, fixed: the cap lip takes up the 1.2-1.5 panel
HW, Y0, Y1 = 6.0, CY - 7.5, CY + 7.5    # housing 12.0 wide (NJ3FD-V front view) x 15.0; the feet make the 12.8
R_NOSE, R_BORE = 5.95, 3.25         # nose in the 12.0 hole; plug opening 6.5
LEADS = {'T': (0.0, 0.0), 'TN': (-5.08, 0.64), 'R': (5.08, 5.72), 'S': (-5.08, 5.72),
         'RN': (4.45, 10.17), 'SN': (-4.45, 10.17)}
PEGS = ((3.81, 1.91, 2.0), (-3.18, 12.07, 1.5))   # plastic locating pegs in the 2.1 / 1.6 NPTH holes
GOLD = 'metal_gold'


def pins():
    return list(LEADS.values())


OUTLINE = [(-HW + 0.7, Y0), (HW - 0.7, Y0), (HW, Y0 + 0.7), (HW, Y1), (-HW, Y1), (-HW, Y0 + 0.7)]   # T corners 0.7


def _tag(m, x, y, wx, wy, z_tip, point):
    """Flat solder tag from under the housing (z 0.5) to z_tip; narrowed over its last 1.2 mm (point: to a lance)."""
    rect = lambda z, a, b: [(x - a, y - b, z), (x + a, y - b, z), (x + a, y + b, z), (x - a, y + b, z)]
    tip = (wx / 2, wy / 2 * 0.35) if point else (wx / 2 * 0.55, wy / 2)
    m.loft([rect(z_tip, *tip), rect(z_tip + 1.2, wx / 2, wy / 2), rect(0.5, wx / 2, wy / 2)], GOLD)


def _vee(m, side, yc, zc, dy, dz, w=0.35):
    """Stamped barb of a side contact: a V in the side face (x = side * 6.0) with its apex dy off the strip edge yc."""
    for s in (-1, 1):
        q = [(yc, zc + s * dz), (yc, zc + s * (dz - 1.6 * w)), (yc + dy - math.copysign(w, dy), zc), (yc + dy, zc)]
        x0, x1 = sorted((side * HW, side * (HW + 0.1)))
        m.merge(Mesh().prism([(-z, y) for y, z in q], x0, x1, GOLD).rotate('y', 90))


def _side(m, side):
    """Contacts showing on a side face: R (+x) / S (-x) on the jack axis, RN / SN below it, barbs, and the bends
    under the housing to their tags."""
    x0, x1 = sorted((side * HW, side * (HW + 0.1)))
    m.box(x0, CY - 1.0, 0.3, x1, CY + 1.0, 21.0, GOLD)
    m.box(x0, CY + 1.4, 0.3, x1, CY + 2.8, 17.1, GOLD)
    for zc in (6.2, 1.8):
        _vee(m, side, CY - 1.0, zc, -1.6, 1.3)
        _vee(m, side, CY + 1.0, zc, 0.35, 1.3)
    for zc in (15.0, 6.3):
        _vee(m, side, CY + 2.8, zc, 1.3, 1.2)
    xr, xn = LEADS['R'][0] * side, LEADS['RN'][0] * side
    m.box(xr, CY - 0.65, 0.3, x1 if side > 0 else x0, CY + 0.65, 0.5, GOLD)
    m.box(xn, CY + 1.6, 0.3, x1 if side > 0 else x0, LEADS['RN'][1] + 0.15, 0.5, GOLD)


def build():
    m = Mesh()
    for sx in (-1, 1):                                                        # standoff feet, RN/SN-side corners
        m.box(sx * 5.0, CY + 5.93, 0.0, sx * 6.4, Y1, 1.2, 'plastic_black')
    m.prism(OUTLINE, 0.5, 15.96, 'plastic_black')                              # contact block
    m.box(-HW, 0.06, 15.96, HW, Y1, 17.95, 'plastic_black')                    # slot over the T contact (side view)
    m.prism(OUTLINE, 17.95, 19.0, 'plastic_black')
    m.box(-HW, CY + 5.05, 19.0, HW, Y1, 20.0, 'plastic_black')                 # RN/SN side runs on to 20.0 (side views)
    m.box(-HW, CY - 5.05, 19.0, HW, CY + 5.05, 22.96, 'plastic_black', r=1.0)   # neck behind the flange
    m.prism(OUTLINE, 22.96, Z_PANEL, 'plastic_black', chamfer=0.15)            # flange, 1.04 thick
    m.tube(0.0, CY, Z_PANEL, Z_PANEL + 2.9, R_NOSE, R_BORE, 'plastic_black', 48)  # nose, through the panel into the cap
    m.box(-1.0, -0.15, 0.3, 1.0, 0.15, 19.0, GOLD)                              # T contact, seen in the slot
    for side in (1, -1): _side(m, side)
    for n, (x, y) in LEADS.items():
        if n in ('R', 'S'): _tag(m, x, y, 0.4, 1.3, -2.9, True)                  # lance tags (NJ3FD-V side view)
        else: _tag(m, x, y, 0.8, 0.3, -4.0, False)                               # 4.0 below the PCB (family drawing)
    for x, y, d in PEGS:
        m.lathe([(0.0, -1.62), (d / 2 - 0.3, -1.62), (d / 2, -1.32), (d / 2, 0.5)], 'plastic_black', x, y, 20)
    return m


def panel():
    """The POM cap on the panel top (z = 0), around the jack axis: lip, collar 14.5, hex SW12 with its corners towards
    T and RN/SN, domed front 10.1 with the plug opening. Its front sits CAP_FRONT above the panel underside whatever the
    panel thickness; the lip (0.8 high on a 1.2 panel, NJ3FD-V DXF nj3fd-v-4) is compressed by the rest."""
    lip = 0.8 - (STACK['panel_t'] - 1.2)
    top = CAP_FRONT - STACK['panel_t']
    hexr = lambda cap: lambda a: min(6.0 / math.cos(a - math.radians(60) * round(a / math.radians(60))), cap)
    circ = lambda r: lambda a: r
    prof = [(circ(R_BORE), 0.0), (circ(6.8), 0.0), (circ(6.8), lip), (circ(7.05), lip), (circ(7.25), lip + 0.2),
            (circ(7.25), lip + 2.25), (circ(7.05), lip + 2.45), (hexr(6.15), lip + 2.45), (hexr(9.0), lip + 2.9),
            (hexr(9.0), lip + 5.06), (hexr(6.15), lip + 5.51), (circ(5.05), lip + 5.51), (circ(5.05), top - 0.55),
            (circ(4.85), top - 0.2), (circ(4.45), top), (circ(3.65), top), (circ(R_BORE), top - 0.4),
            (circ(R_BORE), 0.0)]
    ang = [2 * math.pi * k / 48 for k in range(48)]
    return Mesh().loft([[(r(a) * math.cos(a), r(a) * math.sin(a), z) for a in ang] for r, z in prof], 'plastic_black',
                       cap0=False, cap1=False)
