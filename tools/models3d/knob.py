"""Panel knob for the pot shafts (placeholder: the knob part is not decided). Delta-like skirted collet knob: skirt with a
white pointer line, fluted body, coloured cap over the collet nut with a pointer line. Frame: z = 0 on the panel top,
pointer towards -y at angle 0 (positive angle turns it clockwise on the panel, as Mesh.rotate('z')).
Diameters Ø13 (Ø16 big): the Delta used 14 mm push-on knobs (12.5 mm on the MID frequency pot; 200 Delta spare parts,
p. 151), and our two pot columns are 20.32 mm apart. A Ø16 skirt clears the panel by 0.6 mm and hides the M7 nut (10 AF,
11.55 across corners, 2.0 thick) in a Ø12.4 x 2.4 recess; a Ø13 knob has no room for that recess and sits 0.4 mm above
the nut. Either way the bore (Ø6.35 for the Alpha R1 shaft, or Ø6) starts 2.4 above the panel, so a 15 mm shaft (12.0
above the panel on the 16.2 stack) engages 9.6 mm, the collet's length."""
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


D_KNOB, D_BIG = 13.0, 16.0


def build(colour='grey', big=False, angle=0.0, bore=6.35, d=None):
    r_sk = (d or (D_BIG if big else D_KNOB)) / 2; r_b = 0.8 * r_sk               # skirt, body
    recess = r_sk - R_RECESS >= 0.8                                              # room to hide the nut under the skirt
    z0 = Z_SKIRT if recess else Z_RECESS                                         # else it sits on top of the nut
    h = Z_RECESS + 12.2 + (1.0 if big else 0.0)                                  # body top: the big one 1.0 higher
    m = Mesh()
    m.lathe(([(bore / 2, h - 0.8), (bore / 2, Z_RECESS), (R_RECESS, Z_RECESS), (R_RECESS, z0)] if recess else
             [(bore / 2, h - 0.8), (bore / 2, z0)]) + [(r_sk, z0), (r_sk, z0 + 1.8), (r_sk - 0.2, z0 + 2.0),
                                                       (r_b - 0.6, z0 + 2.0)], 'plastic_black', seg=48, cap1=False)
    _fluted(m, z0 + 2.0, h, r_b, r_b - 0.45, 20, 0.92, 'plastic_black')
    rt = r_b * 0.92
    m.lathe([(rt - 0.1, h), (rt - 0.6, h + 0.6), (rt - 1.0, h + 0.6)], 'plastic_black', seg=48, cap0=False, cap1=False)
    rc = rt - 1.1                                                             # cap in the top recess
    m.lathe([(rc, h + 0.2), (rc, h + 1.3), (rc - 0.3, h + 1.6), (0.0, h + 1.6)], CAPS.get(colour, 'plastic_grey'), seg=40)
    m.box(-0.35, -(rc - 0.5), h + 1.58, 0.35, -0.9, h + 1.64, 'print_white')                 # cap pointer
    m.box(-0.4, -(r_sk - 0.25), z0 + 1.98, 0.4, -(r_b + 0.1), z0 + 2.06, 'print_white')     # skirt pointer, top
    m.box(-0.4, -(r_sk + 0.03), z0 + 0.3, 0.4, -(r_sk - 0.05), z0 + 1.8, 'print_white')     # and down its side
    if angle: m.rotate('z', angle)
    return m
