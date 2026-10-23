"""C&K PVA2 EE H1 1.7N V2 latching pushbutton (DPDT, PC pins) with a C&K PV cap (PVGY grey; PVRD, PVGR, PVBK, PVWH).
C&K (Littelfuse) "PVA Series Short Stroke Key Switches", revised VL 02/20/25, https://www.ckswitches.com/media/1343/pva.pdf;
its drawings are those of the 23 Feb 2018 issue (pp. D-15..D-17), which were measured here.
H1 = total height 17.54 +-0.2, seating plane to the plunger top (released): KiCad's "h=17.5mm". EE travel 2.4 mm total,
1.5 mm to latch. First-angle views: the moulded "2 0 1" face is y+ with "2" over x = 0 (pads 1/4, spec 16.1), the
moulded circle-X on the cover sits at the pad-1 corner, the clips are on the x faces (9.8 over them, 9.2 across y).
PV cap: d7.4 x 7, square 3.3 socket, slit skirt; PV fits H1 and H3 only. It seats on the plunger step 3.9 below the
plunger top: cap top 17.54 - 3.9 + 7 = 20.64 above the board (drawing: 9.7 above the body top, 11 + 9.7 = 20.7)."""
import math
from .geom import Mesh, rrect
from . import STACK
from .knob import CAPS

NAME = 'C&K PVA2 EE H1 1.7N V2 + PV cap (C&K PVA datasheet rev. 02/20/25)'
FOOTPRINTS = {'SW_Push_2P2T_Toggle_CK_PVA2xxH1xxxxxxV2': {}}
FEATURE = (2.5, 3.0)
MOUNT = 'main'

CX, CY = FEATURE
H1 = 17.54            # seating plane to the plunger top, released
BODY = 11.0           # seating plane to the top of the collar ("11")
LATCH = 1.5           # EE latching travel
SEAT = 3.9            # plunger step (cap seat) below the plunger top ("3,9")
PV_R, PV_H = 3.7, 7.0
PV = {'red': 'plastic_red', 'green': 'plastic_green', 'black': 'plastic_black', 'white': 'plastic_white',
      'grey': 'plastic_grey'}  # the PV colours (RD, GR, BK, WH, GY); others fall back to the knob colours
SEG7 = {'2': 'abged', '0': 'abcdef', '1': 'bc'}


def pins():
    return [(x, y) for y in (0.0, 6.0) for x in (0.0, 2.5, 5.0)]


def _yz(m, pts, x0, x1, mat):
    """Outline [(y, z)] extruded along x from x0 to x1."""
    return m.merge(Mesh().prism(pts, x0, x1, mat).rotate('y', 90).rotate('x', 90))


def _xz(m, pts, y0, y1, mat):
    """Outline [(x, z)] extruded along y from y0 to y1."""
    return m.merge(Mesh().prism(pts, -y1, -y0, mat).rotate('x', 90))


def _block(m, x0, y0, x1, y1, z0, z1, mat, r=0.0, top=0.0, bot=0.0):
    """Box with vertical edges rounded to r and the top / bottom edges bevelled by top / bot."""
    def ring(d, z): return [(x, y, z) for x, y in rrect(x0 + d, y0 + d, x1 - d, y1 - d, r, 3)]
    return m.loft(([ring(bot, z0)] if bot else []) + [ring(0, z0 + bot), ring(0, z1 - top)] + ([ring(top, z1)] if top else []), mat)


def _clip():
    """Cover latch on the x- face, 0.8 thick: frame over two housing lugs and a slit tongue down to z 3.1."""
    m = Mesh(); xo, xi = CX - 4.95, CX - 4.15
    _yz(m, rrect(CY - 2.75, 7.3, CY + 2.75, 8.55, 0.4, 3), xo, xi, 'plastic_white')
    _yz(m, [(CY - 1.52, 7.3), (CY - 0.75, 7.3), (CY - 0.6, 4.8), (CY + 0.6, 4.8), (CY + 0.75, 7.3), (CY + 1.52, 7.3),
            (CY + 1.48, 4.06), (CY + 1.0, 3.57), (CY + 1.0, 3.09), (CY - 1.0, 3.09), (CY - 1.0, 3.57), (CY - 1.48, 4.06)],
        xo, xi, 'plastic_white')
    for y0 in (CY - 2.92, CY + 1.5): m.box(CX - 4.9, y0, 6.15, CX - 4.0, y0 + 1.42, 7.3, 'plastic_grey')
    return m.box(CX - 4.5, CY - 0.55, 4.9, CX - 4.0, CY + 0.55, 7.0, 'plastic_grey')     # latch bump in the slit


def _digit(m, ch, cx, z0, w=0.6, h=1.0, t=0.13):
    """Moulded terminal number on the y+ face (read from y+, x to the right)."""
    y0, y1, zm = CY + 4.6, CY + 4.66, z0 + h / 2
    seg = dict(a=(-w / 2, w / 2, z0 + h - t, z0 + h), b=(w / 2 - t, w / 2, zm, z0 + h), c=(w / 2 - t, w / 2, z0, zm),
               d=(-w / 2, w / 2, z0, z0 + t), e=(-w / 2, -w / 2 + t, z0, zm), f=(-w / 2, -w / 2 + t, zm, z0 + h),
               g=(-w / 2, w / 2, zm - t / 2, zm + t / 2))
    for s in SEG7[ch]:
        xa, xb, za, zb = seg[s]; m.box(cx + xa, y0, za, cx + xb, y1, zb, 'print_white')


def build(latched=False):
    m = Mesh()
    _xz(m, [(CX - 4.0, 0.0), (CX - 3.35, 0.0), (CX - 3.35, 0.3), (CX + 3.35, 0.3), (CX + 3.35, 0.0), (CX + 4.0, 0.0),
            (CX + 4.0, 7.3), (CX - 4.0, 7.3)], CY - 4.6, CY + 4.6, 'plastic_grey')     # housing, 0.3 channel under the pins
    _block(m, CX - 4.15, CY - 4.6, CX + 4.15, CY + 4.6, 7.3, 8.9, 'plastic_white', r=0.3, top=0.3, bot=0.1)   # cover
    _block(m, CX - 2.75, CY - 2.5, CX + 2.75, CY + 2.5, 8.9, BODY, 'plastic_white', r=0.3, top=0.3)          # collar
    c = _clip(); m.merge(c.copy()).merge(c.mirror_x(CX))
    for ch, x in zip('201', (0.0, 2.5, 5.0)): _digit(m, ch, x, 0.6)
    mx, my = CX - 2.7, CY - 3.45                                                       # circle-X at the pad-1 corner
    m.tube(mx, my, 8.9, 8.94, 0.75, 0.62, 'plastic_grey', 20)
    for a in (45, -45): m.merge(Mesh().box(-0.5, -0.06, 8.9, 0.5, 0.06, 8.94, 'plastic_grey').rotate('z', a).translate(mx, my))
    p = Mesh()                                                                         # plunger, square 3.3
    p.box(CX - 1.65, CY - 1.65, 9.5, CX + 2.14, CY + 1.65, H1 - SEAT, 'plastic_grey')  # key on x+: the cap stop
    p.box(CX - 1.65, CY - 1.65, H1 - SEAT, CX + 1.65, CY + 1.65, H1 - 3.1, 'plastic_grey')
    p.box(CX - 1.25, CY - 1.25, H1 - 3.1, CX + 1.25, CY + 1.25, H1 - 2.1, 'plastic_grey')  # 1 mm snap neck, 2.5 square
    _yz(p, [(CY - 1.65, H1 - 2.1), (CY + 1.65, H1 - 2.1), (CY + 1.65, H1 - 0.4), (CY + 1.25, H1), (CY + 0.8, H1),
            (CY + 0.8, H1 - 0.27), (CY - 0.8, H1 - 0.27), (CY - 0.8, H1), (CY - 1.25, H1), (CY - 1.65, H1 - 0.4)],
        CX - 1.65, CX + 1.65, 'plastic_grey')                                          # head: 2.1 high, groove along x
    m.merge(p.translate(dz=-LATCH if latched else 0.0))
    for x, y in pins():                     # 0.55 x 0.4 PC pins, V tip; 3.5 long on the drawing, cut at z -3 (model frame)
        _xz(m, [(x - 0.275, 0.3), (x + 0.275, 0.3), (x + 0.275, -2.7), (x, -3.0), (x - 0.275, -2.7)], y - 0.2, y + 0.2, 'metal_tin')
    return m


def _skirt(m, yc, z0, z1, mat, s=1.65, seg=48):
    """The two halves of the cap's skirt around the square socket, split by a slit 2 yc wide along x."""
    a0 = math.asin(yc / PV_R); step = 2 * math.pi / seg
    angs = [a0] + [k * step for k in range(seg) if a0 + 1e-6 < k * step < math.pi - a0 - 1e-6] + [math.pi - a0]
    pts = [(PV_R * math.cos(a), PV_R * math.sin(a)) for a in angs] + [(-s, yc), (-s, s), (s, s), (s, yc)]
    for sg in (1, -1): m.prism([(x, sg * y) for x, y in pts], z0, z1, mat)


def _ring(m, z0, z1, mat, s=1.65, seg=48):
    """Cap wall between the slit and the socket ceiling: d7.4 outside, square socket inside."""
    a = [2 * math.pi * k / seg for k in range(seg)]
    out = [(PV_R * math.cos(t), PV_R * math.sin(t)) for t in a]
    inn = [(s * math.cos(t) / max(abs(math.cos(t)), abs(math.sin(t))), s * math.sin(t) / max(abs(math.cos(t)), abs(math.sin(t)))) for t in a]
    def at(pts, z): return [(x, y, z) for x, y in pts]
    return m.loft([at(inn, z0), at(out, z0), at(out, z1), at(inn, z1), at(inn, z0)], mat, cap0=False, cap1=False)


def panel(colour='grey', latched=False):
    """PV cap on the plunger, relative to FEATURE, z = 0 on the panel top."""
    mat = PV.get(colour) or CAPS.get(colour, 'plastic_grey')
    m = Mesh()
    _skirt(m, 0.3, 0.0, 3.0, mat)                       # 0.6 x 3.0 slit through both walls
    _ring(m, 3.0, SEAT, mat)
    m.lathe([(PV_R, SEAT), (PV_R, PV_H - 0.45), (PV_R - 0.45, PV_H)], mat, seg=48)    # 0.45 x 45 top chamfer
    return m.translate(dz=H1 - SEAT - STACK['panel_z0'] - STACK['panel_t'] - (LATCH if latched else 0.0))
