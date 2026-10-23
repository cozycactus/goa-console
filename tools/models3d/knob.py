"""Panel knob for the pot shafts (placeholder: the knob part is not decided). Delta-like skirted collet knob: skirt with a
white pointer line, fluted body, coloured cap over the collet nut with a pointer line. Frame: z = 0 on the panel top,
pointer towards -y at angle 0 (positive angle turns it clockwise on the panel, as Mesh.rotate('z')).
It sits on the shaft above the pot's nut: the skirt (Ø15, Ø18 big) clears the panel by 0.6 mm and hides the M7 nut
(10 AF, 11.55 across corners, 2.0 thick) in a Ø12.4 x 2.4 recess; the bore (Ø6.35 for the Alpha R1 shaft, or Ø6) starts
2.4 above the panel, so a 15 mm shaft (12.0 above the panel on the 16.2 stack) engages 9.6 mm, the collet's length."""
import math
from .geom import Mesh

CAPS = {'red': 'plastic_red', 'blue': 'plastic_blue', 'dblue': 'plastic_blue', 'yellow': 'plastic_yellow',
        'green': 'plastic_green', 'white': 'plastic_white', 'grey': 'plastic_grey', 'orange': 'plastic_orange',
        'black': 'plastic_black'}
Z_SKIRT, Z_RECESS, R_RECESS = 0.6, 2.4, 6.2      # skirt clearance above the panel, nut recess (nut top 2.0, r 5.77)


def _fluted(m, z0, z1, r_out, r_in, n, taper, mat):
    """Fluted body: n round-bottomed flutes, open at the bottom (it stands on the skirt)."""
    pts = []
    for k in range(n):
        for j, f in enumerate((0.0, 0.18, 0.5, 0.82)):                    # land, flank, flute bottom, flank
            r = (r_out, (r_out + r_in) / 2, r_in, (r_out + r_in) / 2)[j]
            pts.append((r, 2 * math.pi * (k + f) / n))
    ring = lambda z, s: [(r * s * math.cos(a), r * s * math.sin(a), z) for r, a in pts]
    return m.loft([ring(z0, 1.0), ring(z1, taper)], mat, cap0=False, cap1=True)


def build(colour='grey', big=False, angle=0.0, bore=6.35):
    k = 1.2 if big else 1.0
    r_sk, r_b, h = 7.5 * k, 6.0 * k, 12.8 + (1.0 if big else 0.0)          # skirt, body, body top
    m = Mesh()
    m.lathe([(bore / 2, h - 0.8), (bore / 2, Z_RECESS), (R_RECESS, Z_RECESS), (R_RECESS, Z_SKIRT), (r_sk, Z_SKIRT),
             (r_sk, 2.4), (r_sk - 0.2, 2.6), (r_b - 0.6, 2.6)], 'plastic_black', seg=48, cap1=False)
    _fluted(m, 2.6, h, r_b, r_b - 0.45, 20, 0.92, 'plastic_black')
    rt = r_b * 0.92
    m.lathe([(rt - 0.1, h), (rt - 0.6, h + 0.6), (rt - 1.0, h + 0.6)], 'plastic_black', seg=48, cap0=False, cap1=False)
    rc = rt - 1.1                                                             # cap in the top recess
    m.lathe([(rc, h + 0.2), (rc, h + 1.3), (rc - 0.3, h + 1.6), (0.0, h + 1.6)], CAPS.get(colour, 'plastic_grey'), seg=40)
    m.box(-0.35, -(rc - 0.5), h + 1.58, 0.35, -0.9, h + 1.64, 'print_white')                 # cap pointer
    m.box(-0.4, -(r_sk - 0.25), 2.58, 0.4, -(r_b + 0.1), 2.66, 'print_white')               # skirt pointer, top
    m.box(-0.4, -(r_sk + 0.03), Z_SKIRT + 0.3, 0.4, -(r_sk - 0.05), 2.4, 'print_white')     # and down its side
    if angle: m.rotate('z', angle)
    return m
