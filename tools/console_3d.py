"""Build the goa console in Blender from the placed boards. Run headless:
  /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python tools/console_3d.py -- render
Each module (strip, group, master) is:
  - its two boards as KiCad exports them (kicad-cli pcb export glb: every footprint's KiCad 3D model, pads, solder
    mask, silkscreen), cached in render/glb/ and re-exported when a .kicad_pcb is newer;
  - the parts KiCad has no 3D model for (Alpha RD901F/RD902F pots, C&K PVA2, Neutrik NJ6FD-V and NC3MAV, Bourns PTB
    faders and MF-RX PTCs, Keystone 1287-ST tabs, M3 standoffs, the M4 star stud), built here from their footprints
    and datasheet dimensions (tools/footprints.py) and the panel stack of spec 16.2, with pins at their pads;
  - the panel layer (plate, knobs, caps, LED lenses, nuts, XLR flanges, fader knobs, legends) in its own collection.
Positions come from render/<module>.json (tools/export_3d.py, KiCad's Python). Each module is a collection,
instanced along the console. Writes render/goa_console.blend (scenes 'console', 'strip bench', 'master bench') and
PNG views, including two with the panel layer hidden.
Board coordinates are mm, y down; Blender X = x, Y = -y, Z up, in metres. Main board top at z = 0, panel
underside at 11.5, jack board top at -12.5. The console sits 9 degrees tilted (fader end lower) in a tub with
walnut cheeks; panel finish and cap colours are placeholders, not decisions."""
import bpy, bmesh, json, math, os, subprocess, sys
from mathutils import Vector, Matrix

ARGV = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['render']
OUTDIR = os.path.abspath(ARGV[0])
PROJ = os.path.dirname(OUTDIR)
KC = os.environ.get('KICAD_CLI', '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli')
S = 0.001
PANEL_Z0, PANEL_Z1, JB_Z = 11.5, 13.0, -12.5
H_JB = PANEL_Z0 - JB_Z                         # jack-board top to panel underside: 24 mm
HP = 5.08; PITCH = 8 * HP                      # 40.64 mm per 8 HP module

# ---------------------------------------------------------------- scene, materials
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene; scene.name = 'console'
scene.unit_settings.system = 'METRIC'; scene.unit_settings.length_unit = 'MILLIMETERS'

def coll(name, parent=None):
    c = bpy.data.collections.new(name); (parent or scene.collection).children.link(c); return c

MATS = {}
def mat(name, rgb, metal=0.0, rough=0.5, emit=0.0):
    if name in MATS: return MATS[name]
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = (*rgb, 1); p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = rough
    if emit:
        p.inputs['Emission Color'].default_value = (*rgb, 1); p.inputs['Emission Strength'].default_value = emit
    m.diffuse_color = (*rgb, 1)
    MATS[name] = m; return m

M = dict(panel=mat('panel anodised', (0.03, 0.032, 0.036), metal=0.3, rough=0.45),
         legend=mat('legend white', (0.9, 0.9, 0.88), rough=0.6), knob=mat('knob black', (0.018, 0.018, 0.02), rough=0.3),
         plastic=mat('moulded black', (0.025, 0.025, 0.027), rough=0.5), sw=mat('PVA2 body', (0.05, 0.05, 0.055), rough=0.45),
         swtop=mat('PVA2 frame', (0.22, 0.22, 0.24), rough=0.4), potcase=mat('pot case zinc', (0.6, 0.6, 0.58), metal=1, rough=0.35),
         nickel=mat('nickel', (0.7, 0.68, 0.64), metal=1, rough=0.25), steel=mat('steel', (0.75, 0.75, 0.76), metal=1, rough=0.3),
         tin=mat('tin', (0.8, 0.8, 0.78), metal=1, rough=0.3), brass=mat('brass', (0.8, 0.6, 0.3), metal=1, rough=0.3),
         alu=mat('aluminium', (0.8, 0.8, 0.82), metal=1, rough=0.25), ptc=mat('PTC yellow', (0.85, 0.6, 0.05), rough=0.5),
         jack=mat('jack black', (0.03, 0.03, 0.03), rough=0.55), slot=mat('slot', (0.0, 0.0, 0.0), rough=0.9),
         wood=mat('walnut', (0.18, 0.09, 0.045), rough=0.55), hdr=mat('base black', (0.02, 0.02, 0.02), rough=0.6),
         floor=mat('desk', (0.035, 0.035, 0.038), rough=0.7),
         substrate=mat('FR4 edge', (0.42, 0.45, 0.29), rough=0.8), mask=mat('solder mask green', (0.03, 0.2, 0.09), rough=0.3),
         silk=mat('silkscreen', (0.92, 0.92, 0.9), rough=0.8), pad=mat('HASL', (0.76, 0.76, 0.75), metal=1, rough=0.35))
CAP = {'red': mat('cap red', (0.7, 0.04, 0.03), rough=0.35), 'blue': mat('cap blue', (0.05, 0.2, 0.7), rough=0.35),
       'dblue': mat('cap dark blue', (0.03, 0.06, 0.25), rough=0.35), 'yellow': mat('cap yellow', (0.85, 0.65, 0.05), rough=0.35),
       'green': mat('cap green', (0.05, 0.5, 0.12), rough=0.35), 'white': mat('cap white', (0.85, 0.85, 0.82), rough=0.35),
       'grey': mat('cap grey', (0.35, 0.36, 0.38), rough=0.4), 'orange': mat('cap orange', (0.9, 0.35, 0.04), rough=0.35)}
LED = {'red': mat('led red', (1, 0.05, 0.02), emit=4), 'green': mat('led green', (0.1, 1, 0.15), emit=4),
       'yellow': mat('led yellow', (1, 0.8, 0.05), emit=4), 'amber': mat('led amber', (1, 0.45, 0.02), emit=4),
       'off': mat('led off', (0.25, 0.02, 0.02), rough=0.2)}

# ---------------------------------------------------------------- mesh building
class Geo:
    """Mesh in footprint-local mm (KiCad x, y down, z up from the board surface); faces carry material indices."""
    def __init__(self, mats):
        self.bm = bmesh.new(); self.mats = mats
    def _add(self, t, mi, smooth=False):
        for f in t.faces:
            f.material_index = mi
            if smooth is not None: f.smooth = smooth
        me = bpy.data.meshes.new('_tmp'); t.to_mesh(me); t.free()
        self.bm.from_mesh(me); bpy.data.meshes.remove(me)
    def box(self, x0, y0, z0, x1, y1, z1, mi=0, bevel=0.0):
        t = bmesh.new(); bmesh.ops.create_cube(t, size=1.0)
        for v in t.verts:
            v.co = Vector(((x0 + x1) / 2 + v.co.x * abs(x1 - x0), -(y0 + y1) / 2 + v.co.y * abs(y1 - y0),
                           (z0 + z1) / 2 + v.co.z * abs(z1 - z0)))
        if bevel: bmesh.ops.bevel(t, geom=t.edges[:], offset=bevel, segments=2, affect='EDGES', profile=0.5)
        self._add(t, mi)
    def cyl(self, cx, cy, z0, z1, r, mi=0, seg=24, r_top=None):
        t = bmesh.new()
        bmesh.ops.create_cone(t, cap_ends=True, segments=seg, radius1=r, radius2=r if r_top is None else r_top, depth=abs(z1 - z0))
        for v in t.verts: v.co = Vector((cx + v.co.x, -cy + v.co.y, (z0 + z1) / 2 + v.co.z))
        for f in t.faces: f.smooth = seg > 8 and len(f.verts) == 4
        self._add(t, mi, smooth=None)
    def disc_y(self, cx, cy, cz, r, thick, mi=0, seg=32):
        """Disc standing on edge, faces towards +-y (a radial PTC)."""
        t = bmesh.new(); bmesh.ops.create_cone(t, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=thick)
        bmesh.ops.transform(t, matrix=Matrix.Rotation(math.radians(90), 4, 'X'), verts=t.verts)
        for v in t.verts: v.co += Vector((cx, -cy, cz))
        for f in t.faces: f.smooth = len(f.verts) == 4
        self._add(t, mi, smooth=None)
    def prism(self, pts, z0, z1, mi=0):
        t = bmesh.new()
        a = [t.verts.new((x, -y, z0)) for x, y in pts]; b = [t.verts.new((x, -y, z1)) for x, y in pts]
        t.faces.new(a); t.faces.new(b)
        for i in range(len(pts)):
            j = (i + 1) % len(pts); t.faces.new((a[i], a[j], b[j], b[i]))
        bmesh.ops.recalc_face_normals(t, faces=t.faces)
        self._add(t, mi)
    def fluted(self, r_out, r_in, z0, z1, taper, n, mi=0):
        """Knurled knob body: 2n-sided star prism, tapering to taper * r at the top."""
        t = bmesh.new(); lo, hi = [], []
        for k in range(2 * n):
            a = math.pi * k / n; rr = r_out if k % 2 == 0 else r_in
            lo.append(t.verts.new((rr * math.cos(a), rr * math.sin(a), z0)))
            hi.append(t.verts.new((rr * taper * math.cos(a), rr * taper * math.sin(a), z1)))
        m = len(lo)
        for k in range(m): t.faces.new((lo[k], lo[(k + 1) % m], hi[(k + 1) % m], hi[k]))
        t.faces.new(hi); t.faces.new(lo[::-1])
        bmesh.ops.recalc_face_normals(t, faces=t.faces)
        self._add(t, mi)
    def mesh(self, name):
        bmesh.ops.scale(self.bm, vec=Vector((S, S, S)), verts=self.bm.verts)
        me = bpy.data.meshes.new(name); self.bm.to_mesh(me); self.bm.free()
        for m in self.mats: me.materials.append(m)
        return me

def rrect(x0, y0, x1, y1, r, seg=5):
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for k in range(seg + 1):
            a = math.radians(a0 + 90 * k / seg); pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts

SHARED = {}
def shared(key, build):
    if key not in SHARED: SHARED[key] = build()
    return SHARED[key]

def put(name, me, c, x, y, z, rot=0.0, flip=False):
    """An object for a mesh built in footprint-local coordinates, at board (x, y), height z; flip = bottom side."""
    o = bpy.data.objects.new(name, me); c.objects.link(o)
    o.location = (x * S, -y * S, z * S); o.rotation_euler[2] = math.radians(rot)
    if flip: o.scale = (-1, 1, -1)
    return o

def text(name, s, x, y, z, size, m, c):
    cu = bpy.data.curves.new(name, 'FONT'); cu.body = s; cu.size = size * S; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
    o = bpy.data.objects.new(name, cu); c.objects.link(o); o.location = (x * S, -y * S, z * S)
    o.data.materials.append(m); return o

def legend(c, s, x, y, size=2.0):
    if s: text(f'legend {s} {x:.0f} {y:.0f}', s, x, y, PANEL_Z1 + 0.02, size, M['legend'], c)

# ---------------------------------------------------------------- parts KiCad has no model for
def pot_mesh(dual):
    """Alpha RD901F / RD902F, vertical: case centred on the shaft (7.5, 2.5) from pin 1, mounting face 10.0 mm above
    the board, then the 1.5 mm spacer washer to the panel (spec 16.2); M7 bushing, 6 mm shaft."""
    g = Geo([M['plastic'], M['potcase'], M['nickel'], M['steel'], M['tin']])
    x0, x1, y0, y1 = 2.6, 12.4, -2.4, 7.4
    g.box(x0, y0, 0, x1, y1, 1.6, 0, 0.2)
    if dual:
        g.box(x0, y0, 1.6, x1, y1, 5.6, 1, 0.3); g.box(x0, y0, 5.6, x1, y1, 6.2, 0, 0.2); g.box(x0, y0, 6.2, x1, y1, 10.0, 1, 0.3)
    else:
        g.box(x0, y0, 1.6, x1, y1, 10.0, 1, 0.3)
    for ty in (-2.25, 7.25):                                              # case tabs into the board
        g.box(7.0, ty - 0.25, -1.4, 8.0, ty + 0.25, 2.0, 1)
    for px in ((0.0, -2.5) if dual else (0.0,)):
        for py in (0.0, 2.5, 5.0):
            g.box(px - 0.3, py - 0.4, -1.4, px + 0.3, py + 0.4, 1.2, 4)
            g.box(px - 0.3, py - 0.4, 0.9, x0 + 0.1, py + 0.4, 1.3, 4)
    g.cyl(7.5, 2.5, 10.0, PANEL_Z0, 4.8, 3, 28)                          # spacer washer
    g.cyl(7.5, 2.5, 10.0, PANEL_Z1 + 1.6, 3.5, 2, 28)                    # bushing through the panel
    g.cyl(7.5, 2.5, PANEL_Z1 + 1.6, PANEL_Z1 + 13.0, 3.0, 3, 24)         # shaft, inside the knob
    return g.mesh('Alpha RD902F' if dual else 'Alpha RD901F')

def pva2_mesh():
    """C&K PVA2 H1: 9.8 x 9.8 body, plunger at (2.5, 3.0) from pin 1 through the panel (PV cap on top)."""
    g = Geo([M['sw'], M['swtop'], M['tin']])
    g.box(-2.4, -1.9, 0, 7.4, 7.9, 8.4, 0, 0.3)
    g.box(-1.9, -1.4, 8.4, 6.9, 7.4, 9.0, 1, 0.2)
    g.box(1.2, 1.7, 9.0, 3.8, 4.3, PANEL_Z1 + 1.0, 0, 0.2)
    return g.mesh('C&K PVA2')

def jack_mesh():
    """Neutrik NJ6FD-V on the jack board: body up to the panel underside (24 mm, the open depth check), 12 mm
    threaded bushing through the panel, plug opening; the nut belongs to the panel layer."""
    g = Geo([M['jack'], M['nickel'], M['slot']])
    g.box(-7.5, -2.0, 0, 7.5, 13.4, H_JB - 4.0, 0, 0.4)
    g.cyl(0, 5.72, H_JB - 4.0, H_JB, 7.4, 0, 32)
    g.cyl(0, 5.72, H_JB, H_JB + 4.0, 5.9, 1, 32)
    g.cyl(0, 5.72, H_JB + 3.95, H_JB + 4.05, 3.3, 2, 24)
    return g.mesh('Neutrik NJ6FD-V')

def xlr_mesh():
    """Neutrik NC3MAV on the jack board: pin block and round housing up to the panel (barrel at (3.81, 0))."""
    g = Geo([M['jack']])
    g.box(-8.5, -9.5, 0, 16.1, 11.0, 6.0, 0, 0.5)
    g.cyl(3.81, 0, 6.0, H_JB, 11.0, 0, 40)
    return g.mesh('Neutrik NC3MAV')

def fader_mesh():
    """Bourns PTB0143/0144: body 128 x 15 x 8 on the slot centreline (y -1.9 from pin 1), pins 1, 2 at x 0, pin 3 at
    -127.5; 3.5 mm spacers up to the panel (spec 16.2). Lever separate."""
    g = Geo([M['steel'], M['plastic'], M['slot']])
    x0, x1, y0, y1 = -127.75, 0.25, -9.4, 5.6
    g.box(x0, y0, 0, x1, y1, 0.6, 0)
    g.box(x0, y0, 0, x1, y0 + 0.6, 8.0, 0); g.box(x0, y1 - 0.6, 0, x1, y1, 8.0, 0)
    g.box(x0 + 6.5, y0, 7.4, x1 - 6.5, -2.5, 8.0, 0); g.box(x0 + 6.5, -1.3, 7.4, x1 - 6.5, y1, 8.0, 0)
    g.box(x0 + 6.5, -2.5, 6.0, x1 - 6.5, -1.3, 6.4, 2)
    g.box(x0, y0, 0, x0 + 6.5, y1, 8.3, 1, 0.3); g.box(x1 - 6.5, y0, 0, x1, y1, 8.3, 1, 0.3)
    for sx in (-63.75 - 38.8, -63.75 + 43.7):
        g.box(sx - 3.0, y0 + 0.5, 8.0, sx + 3.0, y1 - 0.5, PANEL_Z0, 1)
    return g.mesh('Bourns PTB fader')

def tab_mesh():
    """Keystone 1287-ST: foot and 6.35 x 0.8 mm tab in line with the legs at (+-2.54, 0)."""
    g = Geo([M['tin']])
    g.box(-3.6, -1.55, 0, 3.6, 1.55, 0.6, 0)
    g.box(-3.175, -0.41, 0.6, 3.175, 0.41, 8.6, 0, 0.15)
    return g.mesh('Keystone 1287-ST')

def ptc_mesh():
    """Bourns MF-RX160/72: 13.9 x 3.1 mm disc on kinked leads, pins at (0, 0) and (5.08, 0)."""
    g = Geo([M['ptc'], M['tin']])
    g.disc_y(2.54, 0, 12.0, 6.7, 3.0, 0)
    for px in (0.0, 5.08): g.box(px - 0.4, -0.4, -1.4, px + 0.4, 0.4, 7.0, 1)
    return g.mesh('Bourns MF-RX160/72')

def standoff_mesh(h):
    g = Geo([M['brass'], M['steel']])
    g.cyl(0, 0, 0, h, 2.75, 0, 6)
    g.cyl(0, 0, -1.6 - 2.0, -1.6, 2.7, 1, 20)                             # M3 screw head under the board
    return g.mesh(f'M3 standoff {h:g} mm')

def stud_mesh():
    g = Geo([M['steel'], M['tin']])
    g.cyl(0, 0, -1.6 - 2.8, -1.6, 3.5, 0, 6)
    g.cyl(0, 0, -1.6, 12.0, 2.0, 0, 20)
    g.cyl(0, 0, 0, 0.8, 5.0, 1, 28)
    g.cyl(0, 0, 0.8, 4.0, 3.6, 0, 6); g.cyl(0, 0, 6.0, 9.2, 3.6, 0, 6)
    return g.mesh('M4 star stud')

def spacer_mesh(big):
    g = Geo([M['plastic']]); g.cyl(0, 0, 0, 7.6, 3.0 if big else 2.0, 0, 16)
    return g.mesh('LED spacer 7.6 mm')

# ---------------------------------------------------------------- the panel layer
def knob_mesh(big):
    r = 8.0 if big else 7.0
    g = Geo([M['knob'], M['legend']])
    g.cyl(0, 0, 0, 1.4, r + 0.8, 0, 40)
    g.cyl(0, 0, 1.4, 2.2, r + 0.8, 0, 40, r_top=r - 0.3)
    g.fluted(r - 0.35, r - 0.85, 2.2, 13.6, 0.93, 20)
    g.cyl(0, 0, 13.6, 14.4, (r - 0.35) * 0.93, 0, 40, r_top=(r - 0.35) * 0.93 - 1.0)
    g.box(-0.4, -(r + 0.8), 0.9, 0.4, -(r - 0.4), 1.55, 1)                  # pointer on the skirt
    g.box(-0.45, -((r - 0.35) * 0.93 - 1.2), 14.3, 0.45, -2.6, 14.5, 1)      # pointer on the top
    return g.mesh('knob big' if big else 'knob')

def knob_cap_mesh(colour, big):
    r = (((8.0 if big else 7.0) - 0.35) * 0.93 - 1.0) - 0.6
    g = Geo([CAP[colour]]); g.cyl(0, 0, 14.4, 14.7, r, 0, 32)
    return g.mesh(f'knob cap {colour}')

def swcap_mesh(colour):
    g = Geo([CAP[colour]]); g.box(-3.7, -3.7, 0, 3.7, 3.7, 5.5, 0, 0.6)
    return g.mesh(f'PV cap {colour}')

def lens_mesh(state, big):
    k = 5 / 3 if big else 1.0
    g = Geo([M['alu'], LED[state]])
    g.cyl(0, 0, 0, 0.8, 2.4 * k, 0, 24)
    g.cyl(0, 0, 0, 1.6, 1.5 * k, 1, 20); g.cyl(0, 0, 1.6, 2.3, 1.5 * k, 1, 20, r_top=0.6 * k)
    return g.mesh(f'LED lens {state}{" 5 mm" if big else ""}')

def nut_mesh():
    g = Geo([M['nickel']]); g.cyl(0, 0, 0, 0.5, 8.2, 0, 32); g.cyl(0, 0, 0.5, 3.0, 7.4, 0, 6)
    return g.mesh('NJ6FD-V nut')

def flange_mesh():
    """NC3MAV D-size front: 26 x 28 flange with two M3 screws, shell ring, insert and three male pins."""
    g = Geo([M['nickel'], M['jack'], M['steel']])
    g.prism(rrect(-13.0, -14.0, 13.0, 14.0, 3.0), 0, 1.2, 0)
    for sx, sy in ((9.5, -12.0), (-9.5, 12.0)): g.cyl(sx, sy, 1.2, 1.8, 1.7, 2, 16)
    g.cyl(0, 0, 1.2, 1.6, 9.6, 0, 40); g.cyl(0, 0, 1.2, 1.7, 8.6, 1, 40)
    for a in (150, 30, 270): g.cyl(4.75 * math.cos(math.radians(a)), -4.75 * math.sin(math.radians(a)), 1.7, 5.5, 0.8, 2, 12)
    return g.mesh('NC3MAV flange')

def fader_knob_mesh(colour, dual):
    w = 14.0 if dual else 11.0
    g = Geo([M['knob'], CAP[colour]])
    g.box(-w / 2, -6.5, 0, w / 2, 6.5, 10.5, 0, 1.0)
    g.box(-w / 2 - 0.02, -0.45, 1.0, w / 2 + 0.02, 0.45, 10.55, 1)
    return g.mesh(f'fader knob {colour}{" dual" if dual else ""}')

def panel(c, name, width, label=None):
    """Plate in module coordinates: x -1.15 .. width - 1.15, y -11 .. 503; M3 screws on the end rails."""
    x0 = -1.15
    g = Geo([M['panel']]); g.box(x0 + 0.15, -11, 0, x0 + width - 0.15, 503, PANEL_Z1 - PANEL_Z0, 0)
    put(name + ' panel', g.mesh(name + ' panel'), c, 0, 0, PANEL_Z0)
    def screw():
        g = Geo([M['alu']]); g.cyl(0, 0, 0, 1.2, 2.8, 0, 16); return g.mesh('panel screw')
    for yy in (-8, 500):
        for xx in ((x0 + 7.5,) if width < 50 else (x0 + 7.5, x0 + width - 7.5)):
            put(f'{name} screw {xx:.0f} {yy}', shared('screw', screw), c, xx, yy, PANEL_Z1)
    if label: text(name + ' label', label, x0 + width / 2, 494, PANEL_Z1 + 0.02, 3.0, M['legend'], c)

# ---------------------------------------------------------------- legends and colours per module
STRIP = {'RV9': ('GAIN', 'red'), 'RV10': ('HF', 'white'), 'RV11': ('HI-MID', 'white'), 'RV12': ('FREQ', 'dblue'),
         'RV13': ('LO-MID', 'white'), 'RV14': ('FREQ', 'dblue'), 'RV15': ('LF', 'white'), 'RV2': ('AUX 1', 'yellow'),
         'RV3': ('AUX 2', 'yellow'), 'RV4': ('AUX 3', 'green'), 'RV5': ('AUX 4', 'green'), 'RV6': ('AUX 5', 'orange'),
         'RV7': ('AUX 6', 'orange'), 'RV8': ('PAN', 'grey'),
         'SW15': ('Ø', 'grey'), 'SW11': ('HPF', 'grey'), 'SW12': ('EQ', 'grey'), 'SW8': ('PRE', 'yellow'),
         'SW9': ('PRE', 'green'), 'SW10': ('PRE', 'orange'), 'SW14': ('PAN', 'grey'), 'SW13': ('DIR', 'orange'),
         'SW5': ('L-R', 'white'), 'SW6': ('1-2', 'white'), 'SW7': ('3-4', 'white'), 'SW3': ('PFL', 'red'), 'SW4': ('ON', 'green'),
         'D2': ('OL', 'red'), 'D3': (None, 'off'), 'D4': (None, 'green'), 'D5': (None, 'green'), 'D6': (None, 'yellow'),
         'D7': (None, 'off'), 'D8': (None, 'off'),
         'J1': ('LINE IN', None), 'J2': ('INSERT', None), 'J5': ('DIRECT', None), 'RV1': ('', 'white')}
GROUP = {'RV4': ('RETURN', 'blue'), 'RV3': ('AUX', 'yellow'), 'RV2': ('SUB PAN', 'grey'),
         'SW7': ('PFL', 'red'), 'SW3': ('AFL', 'red'), 'SW1': ('MIX', 'white'), 'SW4': ('MIX', 'white'),
         'SW5': ('1-2', 'white'), 'SW6': ('3-4', 'white'), 'SW2': ('AFL', 'red'),
         'D1': (None, 'off'), 'D2': (None, 'off'), 'D3': (None, 'off'),
         'J2': ('SUB OUT', None), 'J1': ('INSERT', None), 'J3': ('AUX OUT', None), 'J4': ('RET L', None),
         'J5': ('RET R', None), 'RV1': ('SUB', 'white')}
MASTER = {'RV2': ('AUX 5', 'orange'), 'RV3': ('AUX 6', 'orange'), 'RV5': ('C/ROOM', 'white'), 'RV6': ('PHONES', 'white'),
          'RV4': ('SOLO', 'red'), 'SW1': ('AFL', 'red'), 'SW2': ('AFL', 'red'), 'SW3': ('EXT', 'grey'),
          'D12': (None, 'off'), 'D13': (None, 'off'), 'D3': ('POWER', 'green'), 'D15': ('PFL', 'off'),
          'J1': ('INS L', None), 'J2': ('INS R', None), 'J10': ('C/R L', None), 'J11': ('C/R R', None),
          'J8': ('EXT L', None), 'J9': ('EXT R', None), 'J6': ('AUX 5', None), 'J7': ('AUX 6', None),
          'J12': ('PHONES', None), 'J3': ('MAIN L', None), 'J4': ('MAIN R', None), 'J5': ('MONO', None), 'RV1': ('MIX', 'red')}
KNOB_ANGLE = {'AUX': -50.0, 'RETURN': 40.0, 'C/ROOM': 30.0, 'PHONES': 20.0}

def led_state(p, names):
    if p['ref'] in names: return names[p['ref']]
    v = p['value'].split()
    if len(v) == 3 and v[2] == 'dB': return None, (v[0] if int(v[1]) <= 4 else 'off')   # meters: lit up to +4 dB
    return None, 'off'

# ---------------------------------------------------------------- KiCad boards (GLB)
def glb(board):
    pcb = os.path.join(PROJ, board + '.kicad_pcb'); out = os.path.join(OUTDIR, 'glb', board + '.glb')
    if not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(pcb):
        os.makedirs(os.path.dirname(out), exist_ok=True)
        subprocess.run([KC, 'pcb', 'export', 'glb', '--force', '--subst-models', '--include-pads', '--include-silkscreen',
                        '--include-soldermask', '--user-origin', '0x0mm', '-o', out, pcb], check=True, capture_output=True)
        print('exported', out)
    return out

def layer_collection(c, lc=None):
    lc = lc or bpy.context.view_layer.layer_collection
    if lc.collection == c: return lc
    for ch in lc.children:
        r = layer_collection(c, ch)
        if r: return r

def fix_material(m):
    """KiCad's GLB marks every material metallic; keep metal for pins, leads, gold and electrolytic tops."""
    p = m.node_tree.nodes.get('Principled BSDF') if m.node_tree else None
    if not p: return
    r, g, b = p.inputs['Base Color'].default_value[:3]
    hi, lo = max(r, g, b), min(r, g, b)
    metal = (0.4 <= hi <= 0.7 and hi - lo < 0.3 * hi) or (r >= 0.45 and g >= 0.15 and b <= 0.25 and r > g > b)
    p.inputs['Metallic'].default_value = 1.0 if metal else 0.0
    p.inputs['Roughness'].default_value = 0.3 if metal else 0.42

def import_board(c, board, z_top):
    """KiCad's GLB of one board into collection c, board top at z_top; returns {reference: empty}."""
    bpy.context.view_layer.active_layer_collection = layer_collection(c)
    before, mats_before = set(bpy.data.objects), set(bpy.data.materials)
    bpy.ops.import_scene.gltf(filepath=glb(board))
    new = [o for o in bpy.data.objects if o not in before]
    for o in new:
        for u in list(o.users_collection):
            if u != c: u.objects.unlink(o)
        if c not in o.users_collection: c.objects.link(o)
    for m in set(bpy.data.materials) - mats_before: fix_material(m)
    root = next(o for o in new if o.parent is None)
    root.name = f'{board} (KiCad 3D)'; root.location.z = (z_top - 1.6) * S
    refs = {}
    for o in new:
        if o.type == 'EMPTY' and o.parent == root:
            ref = o.name.split('.')[0]; refs[ref] = o; o.name = f'{board}:{ref}'
            for i, ch in enumerate(o.children): ch.name = f'{board}:{ref} {i}'
        elif o.type == 'MESH' and o.parent == root:              # board layers: own materials
            layer = o.data.name.rsplit('_', 1)[-1].split('.')[0]
            lm = {'PCB': M['substrate'], 'soldermask': M['mask'], 'silkscreen': M['silk'], 'pad': M['pad']}.get(layer)
            if lm: o.data.materials.clear(); o.data.materials.append(lm)
            o.name = f'{board}:{layer}'
    return refs

# ---------------------------------------------------------------- one module
def module(key, names, width, label=None):
    c = coll({'strip': 'channel strip', 'group': 'group module', 'master': 'master module'}[key])
    cb, cp = coll(c.name + ' boards', c), coll(c.name + ' panel', c)
    pins = Geo([M['tin']])
    for bd in json.load(open(os.path.join(OUTDIR, key + '.json'))):
        board = os.path.splitext(os.path.basename(bd['file']))[0]
        jackboard = bd['y0'] < 10
        zt = JB_Z if jackboard else 0.0; zb = zt - 1.6
        refs = import_board(cb, board, zt)
        bpy.context.view_layer.update()
        for p in bd['parts']:
            fp, ref = p['fp'], p['ref']
            name, colour = names.get(ref, ('', 'grey'))
            f = p.get('feature')
            for px, py in p.get('pads', ()):                    # pins of the parts built here
                pins.cyl(px, py, zb - 1.2, zt + 0.4, 0.45, 0, 8)
            if 'LED_D' in fp:
                big = 'D5.0' in fp
                if ref in refs:                     # KiCad's model stands on its leads: lift it so its top sits just
                    e = refs[ref]                   # under the panel top, on the 7.6 mm spacer (spec 16.2)
                    top = max((ch.matrix_world @ Vector(cr)).z for ch in e.children_recursive if ch.type == 'MESH'
                              for cr in ch.bound_box)
                    e.location.z += (zt + PANEL_Z1 - 0.1) * S - top
                put(f'{ref} spacer', shared(('spacer', big), lambda: spacer_mesh(big)), cb, f[0], f[1], zt)
                lg, st = led_state(p, names)
                put(f'{ref} lens', shared(('lens', st, big), lambda: lens_mesh(st, big)), cp, f[0], f[1], PANEL_Z1)
                if lg: legend(cp, lg, f[0], f[1] - (5.0 if big else 3.8), 1.6)
            if p['model']: continue
            if 'MountingHole_4.3mm_M4' in fp:
                put(f'{ref} star stud', shared('stud', stud_mesh), cb, p['x'], p['y'], zt)
            elif 'MountingHole' in fp:
                h = PANEL_Z0 - zt
                put(f'{ref} standoff', shared(('standoff', h), lambda: standoff_mesh(h)), cb, p['x'], p['y'], zt)
            elif 'Potentiometer_Alpha' in fp:
                dual = 'Dual' in fp
                put(f'{ref} pot', shared(('pot', dual), lambda: pot_mesh(dual)), cb, p['x'], p['y'], zt, p['rot'])
                big = name == 'C/ROOM'
                k = put(f'{ref} knob', shared(('knob', big), lambda: knob_mesh(big)), cp, f[0], f[1], PANEL_Z1)
                k.rotation_euler[2] = math.radians(KNOB_ANGLE.get(name.split()[0] if name else '', 0.0))
                put(f'{ref} knob cap', shared(('kcap', colour, big), lambda: knob_cap_mesh(colour, big)), cp, f[0], f[1], PANEL_Z1)
                legend(cp, name, f[0], f[1] - 9.8)
            elif 'PVA2' in fp:
                put(f'{ref} PVA2', shared('pva2', pva2_mesh), cb, p['x'], p['y'], zt, p['rot'])
                put(f'{ref} cap', shared(('swcap', colour), lambda: swcap_mesh(colour)), cp, f[0], f[1], PANEL_Z1 + 0.5)
                legend(cp, name, f[0], f[1] - 5.8, 1.7)
            elif 'NJ6FD-V' in fp:
                put(f'{ref} NJ6FD-V', shared('jack', jack_mesh), cb, p['x'], p['y'], zt, p['rot'])
                put(f'{ref} nut', shared('nut', nut_mesh), cp, f[0], f[1], PANEL_Z1)
                legend(cp, name, f[0], f[1] - 10.2, 1.8)
            elif 'NC3MAV' in fp:
                put(f'{ref} NC3MAV', shared('xlr', xlr_mesh), cb, p['x'], p['y'], zt, p['rot'])
                put(f'{ref} flange', shared('flange', flange_mesh), cp, f[0], f[1], PANEL_Z1)
                legend(cp, name, f[0], f[1] - 16.2, 1.8)
            elif 'PTB014' in fp:
                dual = 'Dual' in fp
                put(f'{ref} fader', shared('fader', fader_mesh), cb, p['x'], p['y'], zt, p['rot'])
                y = f[1] + 50.0 - 100.0 * 0.75                              # knob at 75 % travel
                g = Geo([M['steel']]); g.box(-0.5, -1.5, 7.4, 0.5, 1.5, PANEL_Z1 + 5.0, 0)
                put(f'{ref} lever', g.mesh(f'{ref} lever'), cb, f[0], y, zt)
                g = Geo([M['slot'], M['legend']])
                g.box(-1.0, -50.0, 0, 1.0, 50.0, 0.05, 0)
                for kk in range(11):
                    w = 3.0 if kk in (0, 3, 10) else 1.8; yy = -50.0 + 10.0 * kk
                    g.box(-5.5 - w, yy - 0.2, 0, -5.5, yy + 0.2, 0.05, 1)
                put(f'{ref} slot', g.mesh(f'{ref} slot'), cp, f[0], f[1], PANEL_Z1)
                put(f'{ref} knob', shared(('fknob', colour, dual), lambda: fader_knob_mesh(colour or 'grey', dual)), cp, f[0], y, PANEL_Z1 + 2.0)
                legend(cp, name, f[0], f[1] + 60.0, 2.4 if dual else 2.0)
            elif 'Keystone_1287' in fp:
                put(f'{ref} spade', shared('tab', tab_mesh), cb, p['x'], p['y'], zb if p['side'] == 'B' else zt, p['rot'], p['side'] == 'B')
            elif 'Fuse_Bourns' in fp:
                put(f'{ref} PTC', shared('ptc', ptc_mesh), cb, p['x'], p['y'], zb if p['side'] == 'B' else zt, p['rot'], p['side'] == 'B')
            elif not ('NetTie' in fp or 'SolderJumper' in fp):
                l, t, r, b = p['box']
                g = Geo([M['plastic']]); g.box(l + 0.3, t + 0.3, 0, r - 0.3, b - 0.3, 1.0, 0)
                put(ref, g.mesh(ref), cb, 0, 0, zt if p['side'] == 'F' else zb - 1.0)
    put(f'{key} pins', pins.mesh(f'{key} pins'), cb, 0, 0, 0)
    panel(cp, key, width, label)
    return c

strip = module('strip', STRIP, 8 * HP - 0.34)
group = module('group', GROUP, 8 * HP - 0.34)
master = module('master', MASTER, 16 * HP - 0.34, 'MASTER')
mpanel = bpy.data.collections['master module panel']
for side, x in (('L', 18.0), ('R', 60.6)):                          # meter legends: channel letter, dB scale outboard
    legend(mpanel, side, x, 318.5, 2.4)
    for v in (18, 12, 6, 0, -6, -12, -20):
        legend(mpanel, f'{v:+d}' if v else '0', x + (-6.0 if side == 'L' else 6.2), 422.0 - 5.0 * (v + 20) / 2, 1.5)

# ---------------------------------------------------------------- console: 12 strips | 2 groups | master | 2 groups | 12 strips
console = coll('console')
root = bpy.data.objects.new('console root', None); console.objects.link(root)
modules = coll('modules', console)
order = ['S'] * 12 + ['G1', 'G2', 'M', 'G3', 'G4'] + ['S'] * 12
def instance(name, src, x):
    e = bpy.data.objects.new(name, None); e.instance_type = 'COLLECTION'; e.instance_collection = src
    e.location = (x * S, 0, 0); modules.objects.link(e); e.parent = root
x, n = 0.0, 0
strip_x, master_x = [], 0.0
for item in order:
    if item == 'S':
        n += 1; strip_x.append(x); instance(f'strip {n}', strip, x)
        text(f'strip number {n}', str(n), x + 19.0, 494.0, PANEL_Z1 + 0.03, 3.0, M['legend'], modules).parent = root
        x += PITCH
    elif item == 'M':
        master_x = x; instance('master', master, x); x += 2 * PITCH
    else:
        instance(f'group {item[1]}', group, x)
        text(f'group label {item[1]}', f'GROUP {item[1]}', x + 19.0, 494.0, PANEL_Z1 + 0.03, 3.0, M['legend'], modules).parent = root
        x += PITCH
width = x
for src in (strip, group, master):                 # the sources; the instances render
    layer_collection(src).exclude = True
def box(name, x0, y0, z0, x1, y1, z1, m, c):
    g = Geo([m]); g.box(x0, y0, z0, x1, y1, z1, 0)
    o = bpy.data.objects.new(name, g.mesh(name)); c.objects.link(o); return o
frame = coll('frame', console)
TUB = -45.0                                       # tub floor: side-B parts reach z -27 (16 mm elko), jack board -14
for y0, y1 in ((-12, -3), (495, 504)):
    box(f'rail {y0}', -2, y0, PANEL_Z0 - 10, width + 2, y1, PANEL_Z0, M['alu'], frame).parent = root
box('tub floor', -2, -12, TUB - 2, width + 2, 504, TUB, M['hdr'], frame).parent = root
box('arm-rest', -22, 504, TUB, width + 22, 548, PANEL_Z1 + 6, M['wood'], frame).parent = root
box('back trim', -22, -40, TUB, width + 22, -12, PANEL_Z1 + 10, M['wood'], frame).parent = root
TILT = 9.0                                        # front (fader end) lower, towards the engineer
root.rotation_euler[0] = math.radians(TILT)
root.location = (-width / 2 * S, 0.25, 0.14)
bpy.context.view_layer.update()
def W(px, py, pz):
    """World position of a point in module coordinates (mm, board y down)."""
    return root.matrix_world @ Vector((px * S, -py * S, pz * S))
def prism(name, xw0, xw1, prof, m, c):
    bm = bmesh.new()
    a = [bm.verts.new((xw0, y, z)) for y, z in prof]; b = [bm.verts.new((xw1, y, z)) for y, z in prof]
    bm.faces.new(a); bm.faces.new(b[::-1])
    for i in range(len(prof)):
        j = (i + 1) % len(prof); bm.faces.new((a[i], b[i], b[j], a[j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(m)
    o = bpy.data.objects.new(name, me); c.objects.link(o); return o
def wedge(name, x0, x1, z_back, z_front, m):
    """Wedge from the desk (z = 0) up to the tilted console, module x x0..x1 (mm)."""
    tb, tf = W(0, -40, z_back), W(0, 548, z_front)
    return prism(name, root.location.x + x0 * S, root.location.x + x1 * S, [(tb.y, tb.z), (tf.y, tf.z), (tf.y, 0.0), (tb.y, 0.0)], m, frame)
wedge('base', -2, width + 2, TUB, TUB, M['hdr'])
for xc in (-22.0, width + 2.0):
    wedge(f'cheek {xc:.0f}', xc, xc + 20, PANEL_Z1 + 24, PANEL_Z1 + 8, M['wood'])
box('desk', -3000, -2500, -20, 3000, 2500, 0, M['floor'], scene.collection)

# ---------------------------------------------------------------- render setup
world = bpy.data.worlds.new('studio'); world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.03, 0.032, 0.036, 1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.0
def setup(sc):
    sc.world = world
    for eng in ('BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT'):
        try: sc.render.engine = eng; break
        except TypeError: pass
    for k, v in (('taa_render_samples', 64), ('use_raytracing', True), ('use_shadows', True)):
        try: setattr(sc.eevee, k, v)
        except AttributeError: pass
    sc.view_settings.view_transform = 'AgX'
    try: sc.view_settings.look = 'AgX - Medium High Contrast'
    except TypeError: pass
def aim(o, target):
    o.rotation_euler = (Vector(target) - o.location).to_track_quat('-Z', 'Y').to_euler()
def light(sc, name, kind, loc, target, energy, size=1.0):
    ld = bpy.data.lights.new(name, kind); ld.energy = energy
    if kind == 'AREA': ld.size = size
    o = bpy.data.objects.new(name, ld); sc.collection.objects.link(o); o.location = loc; aim(o, target)
def camera(sc, name):
    cd = bpy.data.cameras.new(name); cd.clip_start = 0.002; cd.clip_end = 50
    o = bpy.data.objects.new(name, cd); sc.collection.objects.link(o); sc.camera = o; return o
def shot(sc, cam, fn, loc, target, lens=None, ortho=None, res=(1920, 1080), rot=None):
    cam.location = loc
    if rot is None: aim(cam, target)
    else: cam.rotation_euler = rot
    if ortho: cam.data.type = 'ORTHO'; cam.data.ortho_scale = ortho
    else: cam.data.type = 'PERSP'; cam.data.lens = lens
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = os.path.join(OUTDIR, fn)
    bpy.ops.render.render(write_still=True, scene=sc.name)
    print('rendered', fn)
def panels_visible(on):
    for src in (strip, group, master):              # instances follow the child collection, not its objects' flags
        bpy.data.collections[src.name + ' panel'].hide_render = not on
    for o in modules.objects:
        if o.type == 'FONT': o.hide_render = not on

setup(scene)
mid = W(width / 2, 250, PANEL_Z1)
light(scene, 'key', 'AREA', mid + Vector((-0.9, -1.1, 1.5)), mid, 55, 1.4)
light(scene, 'fill', 'AREA', mid + Vector((1.4, -0.6, 1.0)), mid, 18, 2.0)
light(scene, 'rim', 'AREA', mid + Vector((0.2, 1.4, 1.1)), mid, 30, 2.0)
cam = camera(scene, 'console camera')

bench = bpy.data.scenes.new('strip bench'); bench.collection.children.link(strip)
bench.unit_settings.system = 'METRIC'; bench.unit_settings.length_unit = 'MILLIMETERS'
setup(bench)
sm = Vector((0.019, -0.25, 0.0))
light(bench, 'key', 'AREA', sm + Vector((-0.5, -0.3, 0.6)), sm, 12, 0.6)
light(bench, 'under', 'AREA', sm + Vector((-0.4, 0.1, -0.5)), sm, 6, 0.8)
light(bench, 'fill', 'AREA', sm + Vector((0.6, 0.2, 0.2)), sm, 5, 0.8)
bcam = camera(bench, 'bench camera')

mbench = bpy.data.scenes.new('master bench'); mbench.collection.children.link(master)
mbench.unit_settings.system = 'METRIC'; mbench.unit_settings.length_unit = 'MILLIMETERS'
setup(mbench)
mm_ = Vector((0.039, -0.25, 0.0))
light(mbench, 'key', 'AREA', mm_ + Vector((-0.5, -0.3, 0.6)), mm_, 14, 0.6)
light(mbench, 'under', 'AREA', mm_ + Vector((-0.3, 0.2, -0.6)), mm_, 9, 0.8)
light(mbench, 'fill', 'AREA', mm_ + Vector((0.6, 0.2, -0.2)), mm_, 6, 0.8)
mcam = camera(mbench, 'master bench camera')

nrm = root.matrix_world.to_3x3() @ Vector((0, 0, 1))
if 'norender' not in ARGV[1:]:                     # '-- render norender': build and save only
    shot(scene, cam, 'console.png', mid + Vector((-0.75, -1.45, 1.0)), mid + Vector((0.0, -0.03, -0.05)), lens=36)
    shot(scene, cam, 'console_plan.png', W(width / 2, 252, PANEL_Z1) + nrm * 2.0, None, ortho=1.36, res=(3200, 1480),
         rot=(math.radians(TILT), 0, 0))
    c = W(strip_x[1] + 20, 150, PANEL_Z1)
    shot(scene, cam, 'closeup_strips.png', c + Vector((-0.20, -0.36, 0.22)), c, lens=50)
    c = W(master_x + 39.3, 235, PANEL_Z1)
    shot(scene, cam, 'closeup_master.png', c + Vector((0.06, -0.46, 0.42)), c, lens=34)
    panels_visible(False)                          # the inside: panel layer hidden
    c = W(master_x + 39.3, 250, 0)
    shot(scene, cam, 'internals.png', c + Vector((-0.42, -0.62, 0.48)), c, lens=40)
    c = W(master_x + 39.3, 150, -5)
    shot(scene, cam, 'internals_closeup.png', c + Vector((-0.16, -0.20, 0.16)), c, lens=35)
    panels_visible(True)
    shot(bench, bcam, 'strip_side.png', (-1.0, -0.252, 0.0), None, ortho=0.56, res=(2400, 440),
         rot=(math.radians(90), 0, math.radians(-90)))
    shot(bench, bcam, 'strip_under.png', (-0.16, 0.07, -0.14), (0.019, -0.11, 0.0), lens=30)
    shot(mbench, mcam, 'master_under.png', (-0.17, 0.09, -0.21), (0.039, -0.17, -0.005), lens=30)

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUTDIR, 'goa_console.blend'))
print('saved', os.path.join(OUTDIR, 'goa_console.blend'), 'width', round(width, 1), 'mm')
