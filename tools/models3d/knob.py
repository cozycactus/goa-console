"""Panel knob for the pot shafts: Elma classic collet knob, Ø14.5, matt black with a line (021-3525 for the Alpha 1/4"
shafts, 021-3425 for the ALPS 6 mm D shaft), and an Elma 040-30x5 matt cap without a line (knob_proposal.md KN1-KN3,
signed off 2026-10-25). Elma datasheet "classic collet knobs", Ø14.5 page: body Ø14.5, about 16-17 high with the cap,
collet engagement 7.0 for 6 / 6.35 mm shafts; cap Ø11 / Ø7, 3.8 + 1 high. No nut cover (the 044-3xxx skirt is Ø17-18.7,
too wide for the 20.32 mm column pitch). Frame: z = 0 on the panel top, pointer towards -y at angle 0 (positive angle
turns it clockwise on the panel, as Mesh.rotate('z')). The knob sits 0.4 mm above the M7 nut (10 AF, 2.0 thick), which
it hides from above (11.55 across corners), so a 15 mm shaft (12.0 above the panel on the 16.2 stack) engages 9.6 mm."""
import math
from .geom import Mesh

CAPS = {'red': 'plastic_red', 'blue': 'plastic_blue', 'dblue': 'plastic_blue', 'yellow': 'plastic_yellow',
        'green': 'plastic_green', 'white': 'plastic_white', 'grey': 'plastic_grey', 'orange': 'plastic_orange',
        'black': 'plastic_black'}
Z_RECESS = 2.4                                    # the knob's seat: 0.4 above the M7 nut (top 2.0)


def _fluted(m, z0, z1, r_out, r_in, n, taper, mat):
    """Fluted body: n round-bottomed flutes, open at the bottom (it stands on its base ring)."""
    pts = []
    for k in range(n):
        for j, f in enumerate((0.0, 0.18, 0.5, 0.82)):                    # land, flank, flute bottom, flank
            r = (r_out, (r_out + r_in) / 2, r_in, (r_out + r_in) / 2)[j]
            pts.append((r, 2 * math.pi * (k + f) / n))
    ring = lambda z, s: [(r * s * math.cos(a), r * s * math.sin(a), z) for r, a in pts]
    return m.loft([ring(z0, 1.0), ring(z1, taper)], mat, cap0=False, cap1=True)


D_KNOB = 14.5
H_BODY, H_CAP = 15.0, 1.0                         # body above its seat, cap proud of the body top


def build(colour='grey', angle=0.0, bore=6.35, d=None, **_):
    """The knob on its shaft. Extra keywords (an old 'big') are ignored: every pot takes the same knob."""
    r = (d or D_KNOB) / 2; z0 = Z_RECESS; h = z0 + H_BODY
    m = Mesh()
    m.lathe([(bore / 2, h - 0.8), (bore / 2, z0), (r - 0.3, z0), (r, z0 + 0.3)], 'plastic_black', seg=48, cap1=False)
    _fluted(m, z0 + 0.3, h, r, r - 0.4, 24, 0.94, 'plastic_black')
    rt = r * 0.94
    m.lathe([(rt - 0.1, h), (rt - 0.5, h + 0.3), (rt - 0.9, h + 0.3)], 'plastic_black', seg=48, cap0=False, cap1=False)
    rc = 5.5                                                                  # cap Ø11 in the top recess
    m.lathe([(rc, h - 0.5), (rc, h + H_CAP - 0.3), (rc - 0.3, h + H_CAP), (0.0, h + H_CAP)], CAPS.get(colour, 'plastic_grey'), seg=40)
    m.box(-0.4, -(rt - 0.2), h + 0.28, 0.4, -(rc + 0.1), h + 0.34, 'print_white')            # line, top rim
    m.box(-0.4, -(r + 0.03), z0 + 0.5, 0.4, -(r - 0.05), h - 0.3, 'print_white')              # and down the side
    if angle: m.rotate('z', angle)
    return m
