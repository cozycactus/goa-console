"""Mesh geometry for the goa-console part models, independent of Blender and KiCad.
A Mesh holds vertices and polygons in footprint-local millimetres, in KiCad's footprint frame: x to the right,
y DOWN (as in the .kicad_mod file), z up from the board surface the part sits on. Every polygon carries a material
name from MATERIALS. Builders return the mesh, so calls chain. Polygon winding is not guaranteed: the Blender adapter
recomputes normals and the VRML writer marks shapes solid FALSE."""
import math

# name: (rgb, metallic, roughness); shared by the Blender adapter and the VRML writer
MATERIALS = {
    'plastic_black': ((0.025, 0.025, 0.027), 0.0, 0.5),
    'plastic_dark': ((0.06, 0.06, 0.065), 0.0, 0.45),
    'plastic_grey': ((0.25, 0.25, 0.27), 0.0, 0.45),
    'plastic_white': ((0.86, 0.86, 0.83), 0.0, 0.4),
    'plastic_blue': ((0.05, 0.2, 0.7), 0.0, 0.35),
    'plastic_red': ((0.7, 0.04, 0.03), 0.0, 0.35),
    'plastic_green': ((0.05, 0.5, 0.12), 0.0, 0.35),
    'plastic_yellow': ((0.85, 0.65, 0.05), 0.0, 0.35),
    'plastic_orange': ((0.9, 0.35, 0.04), 0.0, 0.35),
    'rubber_black': ((0.015, 0.015, 0.016), 0.0, 0.7),
    'ptc_yellow': ((0.85, 0.6, 0.05), 0.0, 0.5),
    'metal_nickel': ((0.7, 0.68, 0.64), 1.0, 0.25),
    'metal_steel': ((0.75, 0.75, 0.76), 1.0, 0.3),
    'metal_zinc': ((0.6, 0.6, 0.58), 1.0, 0.35),
    'metal_black': ((0.05, 0.05, 0.055), 1.0, 0.35),       # black-chromed / black-zinc housings
    'metal_brass': ((0.8, 0.6, 0.3), 1.0, 0.3),
    'metal_tin': ((0.8, 0.8, 0.78), 1.0, 0.3),
    'metal_gold': ((0.85, 0.65, 0.25), 1.0, 0.25),
    'metal_alu': ((0.8, 0.8, 0.82), 1.0, 0.25),
    'print_white': ((0.92, 0.92, 0.9), 0.0, 0.6),          # pointer lines, markings
    'ribbon_grey': ((0.5, 0.51, 0.53), 0.0, 0.55),          # flat cable
    'ribbon_red': ((0.55, 0.04, 0.03), 0.0, 0.55),          # pin-1 stripe
    'wire_red': ((0.6, 0.03, 0.02), 0.0, 0.4), 'wire_blue': ((0.03, 0.12, 0.55), 0.0, 0.4),
    'wire_black': ((0.02, 0.02, 0.02), 0.0, 0.4), 'wire_green': ((0.1, 0.4, 0.08), 0.0, 0.4),
}


def srgb(c):
    """Linear colour component (MATERIALS, Blender) to sRGB (VRML and STEP colours, which KiCad reads as sRGB)."""
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def rrect(x0, y0, x1, y1, r, seg=4):
    """Rounded rectangle outline (x, y) with corner radius r, counter-clockwise in the footprint frame."""
    r = max(0.0, min(r, (x1 - x0) / 2, (y1 - y0) / 2))
    if r == 0:
        return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for k in range(seg + 1):
            a = math.radians(a0 + 90 * k / seg)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def circle(cx, cy, r, seg=32, phase=0.0):
    return [(cx + r * math.cos(phase + 2 * math.pi * k / seg), cy + r * math.sin(phase + 2 * math.pi * k / seg)) for k in range(seg)]


def offset(pts, d):
    """Shrink (d > 0) or grow (d < 0) a convex outline towards its centroid by roughly d."""
    cx = sum(p[0] for p in pts) / len(pts); cy = sum(p[1] for p in pts) / len(pts)
    out = []
    for x, y in pts:
        dx, dy = x - cx, y - cy; L = math.hypot(dx, dy) or 1.0
        out.append((x - d * dx / L, y - d * dy / L))
    return out


def _ear_clip(pts):
    """Triangulate a simple polygon (list of (x, y)); returns index triples."""
    n = len(pts)
    idx = list(range(n))
    area = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n))
    ccw = area > 0
    tris = []
    def inside(p, a, b, c):
        def s(p1, p2, p3): return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
        d1, d2, d3 = s(p, a, b), s(p, b, c), s(p, c, a)
        return not ((d1 < 0 or d2 < 0 or d3 < 0) and (d1 > 0 or d2 > 0 or d3 > 0))
    guard = 0
    while len(idx) > 3 and guard < 10000:
        guard += 1
        for k in range(len(idx)):
            i0, i1, i2 = idx[k - 1], idx[k], idx[(k + 1) % len(idx)]
            a, b, c = pts[i0], pts[i1], pts[i2]
            cross = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
            if (cross > 0) != ccw or abs(cross) < 1e-12: continue
            if any(inside(pts[j], a, b, c) for j in idx if j not in (i0, i1, i2)): continue
            tris.append((i0, i1, i2)); idx.pop(k); break
        else:
            break
    if len(idx) == 3: tris.append(tuple(idx))
    return tris


def oriented(verts, faces):
    """Faces rewound consistently across shared edges, each connected piece turned outwards (positive volume), for
    writers whose readers shade by winding (KiCad's VRML and STEP). verts in the output frame."""
    from collections import defaultdict, deque
    edges = defaultdict(list)
    for fi, f in enumerate(faces):
        for k in range(len(f)):
            a, b = f[k], f[(k + 1) % len(f)]
            if a != b: edges[(min(a, b), max(a, b))].append(fi)
    out = [list(f) for f in faces]; seen = [False] * len(faces)
    for seed in range(len(faces)):
        if seen[seed]: continue
        seen[seed] = True; piece = [seed]; q = deque([seed])
        while q:
            f = out[q.popleft()]
            for k in range(len(f)):
                a, b = f[k], f[(k + 1) % len(f)]
                nb = edges.get((min(a, b), max(a, b)), ())
                if a == b or len(nb) != 2: continue                  # open or non-manifold edge: no propagation
                for g in nb:
                    if seen[g]: continue
                    gf = out[g]
                    if any(gf[j] == a and gf[(j + 1) % len(gf)] == b for j in range(len(gf))): out[g] = gf[::-1]
                    seen[g] = True; piece.append(g); q.append(g)
        vol = 0.0
        for fi in piece:
            f = out[fi]; p0 = verts[f[0]]
            for k in range(1, len(f) - 1):
                p1, p2 = verts[f[k]], verts[f[k + 1]]
                vol += (p0[0] * (p1[1] * p2[2] - p1[2] * p2[1]) - p0[1] * (p1[0] * p2[2] - p1[2] * p2[0])
                        + p0[2] * (p1[0] * p2[1] - p1[1] * p2[0]))
        if vol < 0:
            for fi in piece: out[fi] = out[fi][::-1]
    return out


class Mesh:
    def __init__(self):
        self.v, self.f, self.m = [], [], []

    # ------------------------------------------------------------ low level
    def add(self, verts, faces, mat):
        if mat not in MATERIALS: raise ValueError(f'unknown material {mat}')
        b = len(self.v); self.v += [tuple(map(float, p)) for p in verts]
        self.f += [tuple(b + i for i in f) for f in faces]; self.m += [mat] * len(faces)
        return self

    def merge(self, other):
        b = len(self.v); self.v += other.v; self.f += [tuple(b + i for i in f) for f in other.f]; self.m += other.m
        return self

    def copy(self):
        c = Mesh(); c.v, c.f, c.m = list(self.v), list(self.f), list(self.m); return c

    def translate(self, dx=0.0, dy=0.0, dz=0.0):
        self.v = [(x + dx, y + dy, z + dz) for x, y, z in self.v]; return self

    def rotate(self, axis, deg, about=(0.0, 0.0, 0.0)):
        """Rotate about an axis through `about` (footprint frame; for 'z', positive turns +x towards +y)."""
        a = math.radians(deg); c, s = math.cos(a), math.sin(a); ox, oy, oz = about
        out = []
        for x, y, z in self.v:
            x, y, z = x - ox, y - oy, z - oz
            if axis == 'x': y, z = y * c - z * s, y * s + z * c
            elif axis == 'y': x, z = x * c + z * s, -x * s + z * c
            else: x, y = x * c - y * s, x * s + y * c
            out.append((x + ox, y + oy, z + oz))
        self.v = out; return self

    def mirror_x(self, x0=0.0):
        self.v = [(2 * x0 - x, y, z) for x, y, z in self.v]; return self

    def bounds(self):
        xs, ys, zs = zip(*self.v)
        return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))

    # ------------------------------------------------------------ primitives
    def loft(self, rings, mat, cap0=True, cap1=True):
        """Surface through closed rings of equal length [(x, y, z), ...]; caps ear-clipped in the ring's own plane (in plan
        for a horizontal ring), none for a degenerate ring (a point or a line)."""
        n = len(rings[0]); verts = [p for r in rings for p in r]; faces = []
        for i in range(len(rings) - 1):
            for k in range(n):
                a, b = i * n + k, i * n + (k + 1) % n
                faces.append((a, b, b + n, a + n))
        for cap, ring_i in ((cap0, 0), (cap1, len(rings) - 1)):
            if not cap: continue
            ring = rings[ring_i]; nx = ny = nz = 0.0                      # Newell normal of the ring
            for k in range(n):
                a, b = ring[k], ring[(k + 1) % n]
                nx += (a[1] - b[1]) * (a[2] + b[2]); ny += (a[2] - b[2]) * (a[0] + b[0]); nz += (a[0] - b[0]) * (a[1] + b[1])
            L = math.sqrt(nx * nx + ny * ny + nz * nz)
            if L < 1e-9: continue
            nx, ny, nz = nx / L, ny / L, nz / L
            if abs(nz) > 0.999:
                plan = [(p[0], p[1]) for p in ring]
            else:                                                         # basis (u, v) in the ring's plane
                ux, uy = -ny, nx; Lu = math.hypot(ux, uy); ux, uy = ux / Lu, uy / Lu
                vx, vy, vz = ny * 0 - nz * uy, nz * ux - nx * 0, nx * uy - ny * ux
                plan = [(p[0] * ux + p[1] * uy, p[0] * vx + p[1] * vy + p[2] * vz) for p in ring]
            if len(set((round(p[0], 6), round(p[1], 6)) for p in plan)) < 3: continue
            faces += [tuple(ring_i * n + t for t in tri) for tri in _ear_clip(plan)]
        return self.add(verts, faces, mat)

    def prism(self, pts, z0, z1, mat, chamfer=0.0):
        """Outline (x, y) extruded from z0 to z1; chamfer insets the top and bottom edges (convex outlines)."""
        if chamfer <= 0:
            return self.loft([[(x, y, z0) for x, y in pts], [(x, y, z1) for x, y in pts]], mat)
        c = min(chamfer, abs(z1 - z0) / 2.01); inner = offset(pts, c)
        return self.loft([[(x, y, z0) for x, y in inner], [(x, y, z0 + c) for x, y in pts],
                          [(x, y, z1 - c) for x, y in pts], [(x, y, z1) for x, y in inner]], mat)

    def box(self, x0, y0, z0, x1, y1, z1, mat, r=0.0, chamfer=0.0):
        """Axis-aligned box; r rounds the vertical edges, chamfer bevels top and bottom edges."""
        x0, x1 = min(x0, x1), max(x0, x1); y0, y1 = min(y0, y1), max(y0, y1)
        return self.prism(rrect(x0, y0, x1, y1, r) if r else [(x0, y0), (x1, y0), (x1, y1), (x0, y1)],
                          min(z0, z1), max(z0, z1), mat, chamfer)

    def lathe(self, profile, mat, cx=0.0, cy=0.0, seg=32, cap0=True, cap1=True, phase=0.0):
        """Surface of revolution about a vertical axis at (cx, cy) through profile [(radius, z), ...]."""
        rings = [[(cx + r * math.cos(phase + 2 * math.pi * k / seg), cy + r * math.sin(phase + 2 * math.pi * k / seg), z)
                  for k in range(seg)] for r, z in profile]
        return self.loft(rings, mat, cap0, cap1)

    def cyl(self, cx, cy, z0, z1, r, mat, seg=32, r_top=None):
        return self.lathe([(r, z0), (r if r_top is None else r_top, z1)], mat, cx, cy, seg)

    def tube(self, cx, cy, z0, z1, r_out, r_in, mat, seg=32):
        """Hollow cylinder (a nut's bore, a sleeve)."""
        o0 = circle(cx, cy, r_out, seg); i0 = circle(cx, cy, r_in, seg); n = seg
        verts = [(x, y, z0) for x, y in o0] + [(x, y, z1) for x, y in o0] + [(x, y, z0) for x, y in i0] + [(x, y, z1) for x, y in i0]
        faces = []
        for k in range(n):
            k1 = (k + 1) % n
            faces += [(k, k1, n + k1, n + k), (2 * n + k, 3 * n + k, 3 * n + k1, 2 * n + k1),
                      (k, 2 * n + k, 2 * n + k1, k1), (n + k, n + k1, 3 * n + k1, 3 * n + k)]
        return self.add(verts, faces, mat)

    def hexagon(self, cx, cy, z0, z1, across_flats, mat, chamfer=0.0):
        r = across_flats / 2 / math.cos(math.pi / 6)
        return self.prism(circle(cx, cy, r, 6, math.pi / 6), z0, z1, mat, chamfer)

    def star(self, cx, cy, z0, z1, r_out, r_in, n, mat, taper=1.0):
        """Fluted / knurled body: 2n-point star outline, top scaled by taper."""
        pts = [(r_out if k % 2 == 0 else r_in, math.pi * k / n) for k in range(2 * n)]
        lo = [(cx + r * math.cos(a), cy + r * math.sin(a), z0) for r, a in pts]
        hi = [(cx + r * taper * math.cos(a), cy + r * taper * math.sin(a), z1) for r, a in pts]
        return self.loft([lo, hi], mat)

    def hcyl(self, axis, c1, c2, a0, a1, r, mat, seg=24):
        """Horizontal cylinder: axis 'x' (from x a0 to a1, centre y c1, z c2) or 'y' (y a0..a1, centre x c1, z c2)."""
        t = Mesh().cyl(0, 0, 0, a1 - a0, r, mat, seg)
        if axis == 'x':
            t.rotate('y', 90).translate(a0, c1, c2)
        else:
            t.rotate('x', -90).translate(c1, a0, c2)
        return self.merge(t)

    def pin(self, x, y, d, z_top, z_bot=-3.0, mat='metal_tin', square=False):
        """A through-hole lead from z_top down through the board to z_bot (below the bottom surface)."""
        if square: return self.box(x - d / 2, y - d / 2, z_bot, x + d / 2, y + d / 2, z_top, mat)
        return self.cyl(x, y, z_bot, z_top, d / 2, mat, 12)
