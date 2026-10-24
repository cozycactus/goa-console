"""Bourns MF-RX160/72 and MF-RX185/72 Multifuse PPTC, radial leaded: MF-RX/72 series data sheet rev. W 09/26,
https://www.bourns.com/docs/product-datasheets/mf-rx72.pdf, p. 2 (product dimensions, style 2) and p. 1 (photo).
Style 2 = square epoxy-coated chip on STRAIGHT leads (kinked leads are the -14 option): A 13.94 max wide, B 19.94 max
from the top to the end of the lead coating, E 3.1 max thick over the coated leads, C 5.1 +-0.7 lead spacing, D 7.6 min
bare lead, leads 0.81 tinned copper. Each lead is soldered to one face of the chip (front lead diagonal up the face, as
in the photo), so the two leads leave the coating about 1.9 mm apart front to back; they are joggled into the in-line
holes 5.08 apart, with the coating ending 1.5 mm above the board (no seating feature on straight leads).
MF-RX185/72 (master wing fuses since 2026-10-24): the same, A 15.18 / B 21.18 max."""
import math
from .geom import Mesh, rrect

NAME = 'Bourns MF-RX/72 PTC'
FOOTPRINTS = {'Fuse_Bourns_MF-RX160-72_Radial_P5.08mm': dict(a=13.94, b=19.94),
              'Fuse_Bourns_MF-RX185-72_Radial_P5.08mm': dict(a=15.18, b=21.18)}
FEATURE = None
MOUNT = 'main'

E, LEAD = 3.1, 0.81                        # max thickness, lead diameter (A, B: the outline, per footprint)
CX = 2.54                                  # body centred between the leads
TB = 0.9                                   # half thickness of the coated chip; the coated leads bulge out to E / 2
YL = E / 2 - 0.2 - LEAD / 2                # lead centre off the mid-plane: 0.2 coating over the lead
ZC = 1.5                                   # end of the lead coating above the board
COAT = 'ptc_yellow'


def pins(**kw):
    return [(0.0, 0.0), (5.08, 0.0)]


def _sweep(m, path, ra, rb, mat, seg=12):
    """Tube along a path [(x, y, z)] (never running along y): elliptic section, semi-axis ra[i] across the path parallel
    to the x-z plane, rb[i] perpendicular to that."""
    rings = []
    for i, p in enumerate(path):
        a, b = path[max(i - 1, 0)], path[min(i + 1, len(path) - 1)]
        t = [b[k] - a[k] for k in range(3)]; L = math.sqrt(sum(c * c for c in t)); t = [c / L for c in t]
        u = (t[2], 0.0, -t[0]); Lu = math.hypot(u[0], u[2]); u = (u[0] / Lu, 0.0, u[2] / Lu)       # (0, 1, 0) x t
        n = (u[1] * t[2] - u[2] * t[1], u[2] * t[0] - u[0] * t[2], u[0] * t[1] - u[1] * t[0])     # u x t
        rings.append([tuple(p[k] + ra[i] * math.cos(2 * math.pi * j / seg) * u[k] + rb[i] * math.sin(2 * math.pi * j / seg) * n[k]
                            for k in range(3)) for j in range(seg)])
    m.loft(rings, mat)


def _body(m, A, ZB):
    """Coated chip: A x A rounded square (front view), edges fully rounded over the thickness (side view)."""
    x0, x1, z0, z1 = CX - A / 2, CX + A / 2, ZB, ZB + A
    rings = []
    for k in range(9):
        t = math.pi * (k / 8 - 0.5)
        d = TB * (1 - math.cos(t))                                # inset of the edge round
        rings.append([(x, TB * math.sin(t), z) for x, z in rrect(x0 + d, z0 + d, x1 - d, z1 - d, max(0.8 - d, 0.05), 5)])
    body = Mesh().loft([[(x, z, y) for x, y, z in r] for r in rings], COAT)   # loft along y, capped in x-z
    body.v = [(x, y, z) for x, z, y in body.v]
    m.merge(body)


def build(a=13.94, b=19.94):
    ZB = ZC + b - a                                                            # body bottom (B - A = 6.0 of coated lead)
    m = Mesh()
    _body(m, a, ZB)
    for x, side, x_top in ((5.08, -1, CX - 2.0), (0.0, 1, CX + 2.0)):           # front lead runs up-left (photo)
        y = side * YL
        z_top = ZB + 5.6
        n = 6                                                                  # coated lead on the face, diagonal
        path = [(x + (x_top - x) * k / n, y, ZB + 0.6 + (z_top - ZB - 0.6) * k / n) for k in range(n + 1)]
        _sweep(m, path, [0.75] * n + [0.4], [E / 2 - YL] * n + [0.3], COAT)
        zs = [ZB + 0.9] + [ZB - (ZB - ZC) * k / 5 for k in range(6)]               # coating run, straight taper
        f = [max(0.0, (ZB - z) / (ZB - ZC)) for z in zs]
        _sweep(m, [(x, y, z) for z in zs] + [(x, y, ZC - 0.12)], [1.0 - 0.55 * v for v in f] + [0.3],
               [E / 2 - YL - (E / 2 - YL - 0.45) * v for v in f] + [0.3], COAT, 16)
        path = [(x, y, ZC + 0.5)]                                              # bare lead: joggle to the hole
        path += [(x, y * (0.5 + 0.5 * math.cos(math.pi * k / 6)), ZC - (ZC - 0.2) * k / 6) for k in range(7)]
        path += [(x, 0.0, -3.0)]
        _sweep(m, path, [LEAD / 2] * len(path), [LEAD / 2] * len(path), 'metal_tin')
    return m


def panel(**kw):
    return None
