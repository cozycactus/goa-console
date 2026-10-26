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
import bpy, bmesh, inspect, json, math, os, subprocess, sys
from mathutils import Vector, Matrix
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from models3d import lookup, STACK, cable
from models3d.blend import to_mesh
import panel_layout
from panel_layout import NAMES, POTS, KNOB_ANGLE, led_state, HP

ARGV = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['render']
OUTDIR = os.path.abspath(ARGV[0])
PROJ = os.path.dirname(OUTDIR)
KC = os.environ.get('KICAD_CLI', '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli')
S = 0.001
PANEL_Z0 = STACK['panel_z0']; PANEL_Z1 = PANEL_Z0 + STACK['panel_t']; JB_Z = PANEL_Z0 - STACK['jack_z0']
H_JB = PANEL_Z0 - JB_Z                         # jack-board top to panel underside: 24 mm
PITCH = 8 * HP                      # 40.64 mm per 8 HP module

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
         legend=mat('legend cream', (0.80, 0.74, 0.56), rough=0.6), knob=mat('knob black', (0.018, 0.018, 0.02), rough=0.3),
         plastic=mat('moulded black', (0.025, 0.025, 0.027), rough=0.5), sw=mat('PVA2 body', (0.05, 0.05, 0.055), rough=0.45),
         swtop=mat('PVA2 frame', (0.22, 0.22, 0.24), rough=0.4), potcase=mat('pot case zinc', (0.6, 0.6, 0.58), metal=1, rough=0.35),
         nickel=mat('nickel', (0.7, 0.68, 0.64), metal=1, rough=0.25), steel=mat('steel', (0.75, 0.75, 0.76), metal=1, rough=0.3),
         tin=mat('tin', (0.8, 0.8, 0.78), metal=1, rough=0.3), brass=mat('brass', (0.8, 0.6, 0.3), metal=1, rough=0.3),
         alu=mat('aluminium', (0.8, 0.8, 0.82), metal=1, rough=0.25), ptc=mat('PTC yellow', (0.85, 0.6, 0.05), rough=0.5),
         jack=mat('jack black', (0.03, 0.03, 0.03), rough=0.55), slot=mat('slot', (0.0, 0.0, 0.0), rough=0.9),
         wood=mat('walnut', (0.18, 0.09, 0.045), rough=0.55), hdr=mat('base black', (0.02, 0.02, 0.02), rough=0.6),
         floor=mat('desk', (0.035, 0.035, 0.038), rough=0.7),
         substrate=mat('FR4 edge', (0.42, 0.45, 0.29), rough=0.8), mask=mat('solder mask green', (0.03, 0.2, 0.09), rough=0.3),
         silk=mat('silkscreen', (0.92, 0.92, 0.9), rough=0.8), pad=mat('HASL', (0.76, 0.76, 0.75), metal=1, rough=0.35),
         copper=mat('copper', (0.93, 0.47, 0.3), metal=1, rough=0.3))
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
    if flip: o.scale = (1, -1, -1)                  # KiCad flips top to bottom: footprint y mirrored, then rotated
    return o

FONT = []
def panel_font():
    """Condensed sans for the panel print (the Delta's legends are a condensed grotesque); Blender's own font if absent."""
    if not FONT:
        f = '/System/Library/Fonts/Supplemental/Arial Narrow.ttf'
        FONT.append(bpy.data.fonts.load(f) if os.path.exists(f) else None)
    return FONT[0]

def text(name, s, x, y, z, size, m, c):
    cu = bpy.data.curves.new(name, 'FONT'); cu.body = s; cu.size = size * S; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
    if panel_font(): cu.font = panel_font()
    o = bpy.data.objects.new(name, cu); c.objects.link(o); o.location = (x * S, -y * S, z * S)
    o.data.materials.append(m); return o

# ---------------------------------------------------------------- generic hardware (the parts are tools/models3d)
def standoff_mesh(h):
    g = Geo([M['brass'], M['steel']])
    g.cyl(0, 0, 0, h, 2.75, 0, 6)
    g.cyl(0, 0, -1.6 - 2.0, -1.6, 2.7, 1, 20)                             # M3 screw head under the board
    return g.mesh(f'M3 standoff {h:g} mm')

def stud_mesh():
    g = Geo([M['steel'], M['tin']])
    g.cyl(0, 0, -1.6 - 2.8, -1.6, 3.5, 0, 6)
    g.cyl(0, 0, -1.6, PANEL_Z0 - 1.5, 2.0, 0, 20)                         # M4 shank, clear of the panel
    g.cyl(0, 0, 0, 0.8, 5.0, 1, 28)
    g.cyl(0, 0, 0.8, 4.0, 3.6, 0, 6); g.cyl(0, 0, 6.0, 9.2, 3.6, 0, 6)
    return g.mesh('M4 star stud')

def spacer_mesh(big):
    h = 4.3 if big else 7.6                       # 3 mm LED: 7.6 spacer (spec 16.2); 5 mm LED: 8.6 tall, so 4.3
    g = Geo([M['plastic']]); g.cyl(0, 0, 0, h, 3.0 if big else 2.0, 0, 16)
    return g.mesh(f'LED spacer {h} mm')

# ---------------------------------------------------------------- the panel layer
def lens_mesh(state, big):
    k = 5 / 3 if big else 1.0
    g = Geo([M['alu'], LED[state]])
    g.cyl(0, 0, 0, 0.8, 2.4 * k, 0, 24)
    g.cyl(0, 0, 0, 1.6, 1.5 * k, 1, 20); g.cyl(0, 0, 1.6, 2.3, 1.5 * k, 1, 20, r_top=0.6 * k)
    return g.mesh(f'LED lens {state}{" 5 mm" if big else ""}')

def panel(c, P):
    """Plate with its cut-outs (tools/panel_layout.py) in module coordinates; M3 screws on the end rails."""
    t = PANEL_Z1 - PANEL_Z0; name = P.key
    g = Geo([M['panel']]); g.box(P.x0 + 0.15, P.y0, 0, P.x1 - 0.15, P.y1, t, 0)       # 0.15 a side: the gap shows
    plate = put(name + ' panel', g.mesh(name + ' panel'), c, 0, 0, PANEL_Z0)
    circles, slots = P.cut()
    cut = Geo([M['panel']])
    for x, y, d in circles:
        if (x, y) not in P.screws: cut.cyl(x, y, -1, t + 1, d / 2, 0, 48 if d > 15 else 40 if d > 4 else 16)
    for x, y, ln, w, a in slots:
        ca, sa = math.cos(math.radians(a)), -math.sin(math.radians(a))
        cut.prism([(x + u * ca - v * sa, y + u * sa + v * ca) for u, v in rrect(-ln / 2, -w / 2, ln / 2, w / 2, w / 2 - 0.01)], -1, t + 1)
    if circles or slots:
        co = put(name + ' cutter', cut.mesh(name + ' cutter'), c, 0, 0, PANEL_Z0)
        bo = plate.modifiers.new('cut-outs', 'BOOLEAN'); bo.operation = 'DIFFERENCE'; bo.object = co; bo.solver = 'EXACT'
        bpy.context.view_layer.update()
        me = bpy.data.meshes.new_from_object(plate.evaluated_get(bpy.context.evaluated_depsgraph_get()))
        plate.modifiers.clear(); old = plate.data; plate.data = me; me.name = name + ' panel'
        bpy.data.meshes.remove(old); bpy.data.objects.remove(co)
    def screw():
        g = Geo([M['alu']]); g.cyl(0, 0, 0, 1.2, 2.8, 0, 16); return g.mesh('panel screw')
    for xx, yy in P.screws:
        put(f'{name} screw {xx:.0f} {yy:.0f}', shared('screw', screw), c, xx, yy, PANEL_Z1)

def panel_print(c, P):
    """The panel print of tools/panel_layout.py: texts (bold where marked) and the ink rectangles as one mesh."""
    for s, x, y, size, bold in P.texts:
        o = text(f'print {P.key} {s} {x:.1f} {y:.1f}', s, x, y, PANEL_Z1 + 0.02, size, M['legend'], c)
        if bold and bold_font(): o.data.font = bold_font()
    g = Geo([M['legend']])
    for x0, y0, x1, y1 in P.rects: g.box(x0, y0, 0, x1, y1, 0.03, 0)
    put(f'{P.key} panel print', g.mesh(f'{P.key} panel print'), c, 0, 0, PANEL_Z1)

# names, colours, cut-out sizes and the print rules: tools/panel_layout.py

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
FADER_POS = 0.75                              # lever position shown: 75 % of the travel
LATCHED = {'strip': ('SW4', 'SW5')}           # switches shown pressed: ON and L-R (their LEDs are lit)

BOLD = []
def bold_font():
    if not BOLD:
        f = '/System/Library/Fonts/Supplemental/Arial Narrow Bold.ttf'
        BOLD.append(bpy.data.fonts.load(f) if os.path.exists(f) else None)
    return BOLD[0]

BUS = {}                                      # module key: bus-header sockets [(x, y, ribbon z, pin-1 y)] for the motherloom
SPADES, STAR = {}, {}                         # module key: ground-spade tab tips [(x, y, z)]; the master's M4 star stud (x, y, z)

def part_kw(fn, kw, **extra):
    """kw plus those of the extra keyword arguments that fn takes."""
    ps = inspect.signature(fn).parameters
    return dict(kw, **{k: v for k, v in extra.items() if k in ps})

def link_ribbon(c, name, j, m, dz=0.0):
    """Jack-board link: flat cable from the jack board's IDC socket j to the main board's socket m (dicts: n, x, y,
    z = ribbon centre, along, y1 = the jack board's far edge, pin1). Long side along x: the cable leaves along y and
    loops up past the jack board's edge. Along y: it leaves along x, bends down, turns a quarter twist into a run along y
    below both boards, then twists back into a main-board socket along y, or rises straight into one along x. Red
    stripe on the pin-1 edge. dz: a further drop for the run under the boards (a second link beside the first)."""
    w = 2.54 * j['n']
    if j['along'] == 'x':
        r = (m['z'] - j['z']) / 2; yt = max(m['y'], j['y1']) + 4.0
        arc = [(j['x'], yt + r * math.sin(math.pi * k / 10), j['z'] + r - r * math.cos(math.pi * k / 10)) for k in range(11)]
        me = cable.ribbon([(j['x'], j['y'], j['z'])] + arc + [(m['x'], m['y'], m['z'])], [(1, 0, 0)], w,
                          stripe=1 if j['pin1'][0] > j['x'] else -1)
    else:
        sj = 1 if j['pin1'][1] > j['y'] else -1                                         # pin-1 edge at each end
        dj = -1 if m['x'] < j['x'] else 1; zl = min(j['z'], m['z']) - 8.0 + dz
        ctrl = [((j['x'], j['y'], j['z']), (0, sj, 0)), ((j['x'] + 4 * dj, j['y'], j['z']), (0, sj, 0)),
                ((j['x'] + 7 * dj, j['y'] + 2, j['z'] - 5), (0, sj, 0))]
        if m['along'] == 'y':          # into a main-board socket along y: twist back, enter it along x
            sm = 1 if m['pin1'][1] > m['y'] else -1; xr = (j['x'] + m['x']) / 2
            ctrl += [((xr, j['y'] + 9, zl), (1, 0, 0)), ((xr, m['y'] - 9, zl), (1, 0, 0)),
                     ((m['x'] - 7 * dj, m['y'] - 2, m['z'] - 5), (0, sm, 0)), ((m['x'] - 4 * dj, m['y'], m['z']), (0, sm, 0)),
                     ((m['x'], m['y'], m['z']), (0, sm, 0))]
        else:                          # into a socket along x: run under it and rise into it along y
            sm = 1 if m['pin1'][0] > m['x'] else -1
            ctrl += [((m['x'], j['y'] + 9, zl), (sm, 0, 0)), ((m['x'], m['y'] - 12, zl), (sm, 0, 0)),
                     ((m['x'], m['y'] - 5, m['z'] - 3), (sm, 0, 0)), ((m['x'], m['y'], m['z']), (sm, 0, 0))]
        path = cable.smooth([p for p, _ in ctrl], 8); k = 8
        wd = []                                   # width direction blended between the control points
        for i in range(len(path)):
            a = min(i // k, len(ctrl) - 1); b = min(a + 1, len(ctrl) - 1); t = (i - a * k) / k if a < len(ctrl) - 1 else 0.0
            wd.append(tuple((1 - t) * ctrl[a][1][q] + t * ctrl[b][1][q] for q in range(3)))
        me = cable.ribbon(path, wd, w)
    put(name, to_mesh(me, name), c, 0, 0, 0)

WIRE = ['wire_green', 'wire_red', 'wire_red', 'wire_black', 'wire_black', 'wire_blue', 'wire_blue']   # J1 pins 1-7:
                                              # CHASSIS, +VBUS x2, GNDA x2, -VBUS x2 (master.net)
def psu_cable(c, p, e, zb, z_floor=-41.5):
    """Supply cable to the master's 7-way terminal J1 (bottom side; the wires enter on the footprint's front, board +y):
    seven wires out of a jacket from the NC7MD-LX in the plenum's rear wall, through the back rail's vent slot
    CABLE_SLOT (tub_proposal.md TB3) and along the tub floor. Master-module coordinates."""
    lo = min((ch.matrix_world @ Vector(cr)).z for ch in e.children_recursive if ch.type == 'MESH' for cr in ch.bound_box) / S
    ze = zb - 0.45 * (zb - lo); ye = p['box'][3] - 0.5; xm = p['x'] - 3 * 5.08
    mx = 14 * PITCH                                                   # the master's x in the console
    xn = panel_layout.NC7_X - mx
    xs = panel_layout.rail_span()[0] + panel_layout.vent_slots()[panel_layout.CABLE_SLOT] - mx
    zn = (panel_layout.FLOOR_TOP - panel_layout.FLOOR_T + panel_layout.PLENUM_CAP_Z) / 2
    zs = panel_layout.PANEL_Z0 - panel_layout.RAIL_H / 2                # the slot's centre
    yr = panel_layout.RAIL_LINES[0]
    me = cable.round_cable(cable.smooth([(xn, -40, zn), (xn, -26, zn), (xs, -24, zs), (xs, yr - 8, zs), (xs, yr + 8, zs),
                                         (xs, 25, zs - 8), (xs, 45, z_floor), (xm, 120, z_floor), (xm, ye + 14, z_floor)], 6), 3.5)
    for k, wm in enumerate(WIRE):
        xk = p['x'] - 5.08 * k
        me.merge(cable.round_cable(cable.smooth([(xk, ye - 4, ze), (xk, ye + 4, ze), (xk + 0.5 * (xm - xk), ye + 9, ze - 10),
                                                 (xm + (k - 3) * 0.9, ye + 13, z_floor + 3), (xm + (k - 3) * 0.6, ye + 15, z_floor)], 6), 1.0, wm, 10))
    put('power cable', to_mesh(me, 'power cable'), c, 0, 0, 0)

def module(key):
    c = coll({'strip': 'channel strip', 'group': 'group module', 'master': 'master module'}[key])
    cb, cp = coll(c.name + ' boards', c), coll(c.name + ' panel', c)
    names = NAMES[key]; data = json.load(open(os.path.join(OUTDIR, key + '.json')))
    pins = Geo([M['tin']]); sockets = []
    for bd in data:
        board = os.path.splitext(os.path.basename(bd['file']))[0]
        jackboard = bd['y0'] < 10
        zt = JB_Z if jackboard else 0.0; zb = zt - 1.6
        refs = import_board(cb, board, zt)
        bpy.context.view_layer.update()
        for p in bd['parts']:
            fp, ref = p['fp'], p['ref']
            name, colour = names.get(ref, ('', 'grey'))
            f = p.get('feature'); reg = lookup(fp); flip = p['side'] == 'B'
            if 'Keystone_1287' in fp and not jackboard:      # the module's ground spade: its tab tip
                SPADES.setdefault(key, []).append((p['x'], p['y'], zb - 10.2 if flip else zt + 10.2))
            if 'MountingHole_4.3mm_M4' in fp: STAR[key] = (p['x'], p['y'], zb)
            if not reg:
                for px, py in p.get('pads', ()):                # pins of the generic parts built here
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
            if 'IDC-Header_2x' in fp:               # crimped socket on the header; the cable is added below
                n = int(fp.split('IDC-Header_2x')[1][:2]); l, t, r, b = p['box']
                along = 'x' if r - l > b - t else 'y'; cx, cy = (l + r) / 2, (t + b) / 2; px, py = p['pin1']
                keyside = (1 if py > cy else -1) if along == 'x' else (1 if px > cx else -1)     # the notch: pin-1 column
                me, zr = cable.idc_socket(n, cx, cy, zb - 3.0 if flip else zt + 3.0, along, flip, keyside)
                put(f'{ref} IDC socket', to_mesh(me, f'{board} {ref} socket'), cb, 0, 0, 0)
                sockets.append(dict(n=n, x=cx, y=cy, z=zr, along=along, jack=jackboard, y1=bd['y1'], pin1=(px, py)))
            if key == 'master' and ref == 'J1' and not jackboard and ref in refs:
                psu_cable(cb, p, refs[ref], zb)
            if p['model']: continue
            if reg:                                 # a part from tools/models3d, and its panel piece
                mod, kw = reg; kind = mod.__name__.rsplit('.', 1)[-1]; short = fp.split(':')[-1]
                for ch in (refs[ref].children_recursive if ref in refs else ()):     # KiCad's copy (its STEP twin)
                    bpy.data.objects.remove(ch)
                lat = ref in LATCHED.get(key, ())
                me = shared(('part', fp, lat), lambda: to_mesh(mod.build(**part_kw(mod.build, kw, pos=FADER_POS, latched=lat)), short))
                put(f'{ref} {kind}', me, cb, p['x'], p['y'], zb if flip else zt, p['rot'], flip)
                if not (mod.FEATURE and f): continue
                pk = part_kw(mod.panel, kw, colour=colour or 'grey', pos=FADER_POS, latched=lat)
                pm = shared(('panel', fp, tuple(sorted(pk.items()))),
                            lambda: (lambda g: g and to_mesh(g, f'{short} panel {colour or ""}'))(mod.panel(**pk)))
                if pm:
                    o = put(f'{ref} {kind} panel', pm, cp, f[0], f[1], PANEL_Z1, p['rot'])
                    if kind in POTS:
                        o.rotation_euler[2] = math.radians(KNOB_ANGLE.get(name.split()[0] if name else '', 0.0))
                continue
            if 'MountingHole_4.3mm_M4' in fp:
                put(f'{ref} star stud', shared('stud', stud_mesh), cb, p['x'], p['y'], zt)
            elif 'MountingHole' in fp:
                h = PANEL_Z0 - zt
                put(f'{ref} standoff', shared(('standoff', h), lambda: standoff_mesh(h)), cb, p['x'], p['y'], zt)
            elif not ('NetTie' in fp or 'SolderJumper' in fp):
                l, t, r, b = p['box']
                g = Geo([M['plastic']]); g.box(l + 0.3, t + 0.3, 0, r - 0.3, b - 0.3, 1.0, 0)
                put(ref, g.mesh(ref), cb, 0, 0, zt if p['side'] == 'F' else zb - 1.0)
    for k, j in enumerate(sorted((q for q in sockets if q['jack']), key=lambda q: -q['n'])):   # the group has two (RET1)
        m = next((q for q in sockets if not q['jack'] and q['n'] == j['n']), None)
        if m: link_ribbon(cb, f'{key} jack-board link' + (f' {k + 1}' if k else ''), j, m, dz=-4.0 * k)
    BUS[key] = sorted((q['x'], q['y'], q['z'], q['pin1'][1]) for q in sockets if not q['jack'] and q['n'] == 17)
    put(f'{key} pins', pins.mesh(f'{key} pins'), cb, 0, 0, 0)
    P = panel_layout.layout(key, data)              # cut-outs, screws and print: the fabrication drawings' source
    panel_print(cp, P)
    panel(cp, P)
    return c

strip = module('strip')
group = module('group')
master = module('master')

# ---------------------------------------------------------------- console: 12 strips | 2 groups | master | 2 groups | 12 strips
console = coll('console')
root = bpy.data.objects.new('console root', None); console.objects.link(root)
modules = coll('modules', console)
order = panel_layout.ORDER
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
cables = coll('cables', console)
def motherloom(name, bus):
    """One wing's 34-way bus ribbon through its modules' bus-header sockets [(x, y, ribbon z, pin-1 y)], sagging
    between them and cut 1.5 mm past the end sockets (master spec 25: one ribbon per wing)."""
    y, z = bus[0][1], bus[0][2]; pts = [(bus[0][0] - 4.5, y, z)]
    for k, (xs, _, _, _) in enumerate(bus):
        pts += [(xs - 3.0, y, z), (xs + 3.0, y, z)]
        if k + 1 < len(bus):
            gap = bus[k + 1][0] - xs - 6.0
            pts.append(((xs + bus[k + 1][0]) / 2, y, z - min(9.0, 0.16 * gap)))
    pts.append((bus[-1][0] + 4.5, y, z))
    me = cable.ribbon(cable.smooth(pts, 6), [(0, 1, 0)], 2.54 * 17, stripe=1 if bus[0][3] > y else -1)   # red: pin 1
    o = bpy.data.objects.new(name, to_mesh(me, name)); cables.objects.link(o); o.parent = root
bus, x = [], 0.0
for item in order:
    key = {'S': 'strip', 'M': 'master'}.get(item, 'group')
    bus += [(x + bx, by, bz, p1) for bx, by, bz, p1 in BUS[key]]
    x += 2 * PITCH if item == 'M' else PITCH
motherloom('motherloom L', sorted(q for q in bus if q[0] < master_x + PITCH))     # master CN2 ends the left wing,
motherloom('motherloom R', sorted(q for q in bus if q[0] >= master_x + PITCH))    # CN3 starts the right one
def ground_harness(x_of):
    """The heavy audio ground (master spec 26, architecture 3.4; route and gauge ground_study.md G1): one 14 AWG wire per
    module from its 6.3 mm spade (a receptacle on the tab), radially (no daisy chain). Each wire drops to just under
    its wing's motherloom and runs tied under it to the master, so its loop with the ribbon's ground conductors stays
    a few cm^2; down the master's free edge strip (x 0.3-4.3 / 74.3-78.3) to below the bottom-side parts, and onto a
    tab of its wing's copper bar (two rows of seven 6.3 mm tabs) bolted under the M4 star stud on a threaded spacer.
    The PSU 0 V reaches the same star through J1 and the net ties; GCANCEL (ribbon pin 26) never goes to the bars.
    x_of: [(module key, its x)]."""
    hc = coll('ground harness', console)
    mx = next(x for k, x in x_of if k == 'master'); sx, sy, szb = STAR['master']; sx += mx
    yr, zr = BUS['strip'][0][1], BUS['strip'][0][2]           # motherloom: header y, ribbon z at the sockets
    zw, zbar, R = zr - 8.0, -26.0, 1.45                       # bundle under the ribbon's sag, bars, 14 AWG insulated
    g = Geo([M['steel'], M['tin'], M['copper']])
    g.cyl(sx, sy, zbar, szb - 4.4, 2.0, 0, 16)                # M4 thread + spacer down to the bars
    g.cyl(sx, sy, zbar + 2.0, zbar + 14.0, 3.5, 0, 6)         # hex spacer
    arms = {'L': (sx - 18.0, sx - 8.0), 'R': (sx + 8.0, sx + 18.0)}
    g.box(sx - 18.0, sy - 6.0, zbar - 2.0, sx + 18.0, sy + 6.0, zbar, 2)     # the bars' common foot under the stud
    for x0, x1 in arms.values(): g.box(x0, sy - 6.0, zbar - 2.0, x1, sy + 66.0, zbar, 2)
    n = 0
    for wing, side in (('L', -1), ('R', 1)):
        tabs = sorted(((x + tx, ty, tz) for k, x in x_of if k != 'master' for tx, ty, tz in SPADES.get(k, ())
                       if (x + tx < sx) == (side < 0)), key=lambda q: abs(q[0] - sx))
        xe = mx + (0.9 if side < 0 else 77.7)                 # the master's edge strip
        for k, (tx, ty, tz) in enumerate(tabs):
            g.box(tx - 3.6, ty - 4.5, tz - 3.0, tx + 3.6, ty + 4.5, tz + 4.0, 1)        # receptacle on the spade tab
            ax = arms[wing][1 if k % 2 else 0]; ay = sy + 4.0 + 9.0 * (k // 2)       # its tab on the bar
            g.box(ax - 0.4, ay - 3.15, zbar - 10.0, ax + 0.4, ay + 3.15, zbar - 2.0, 1)
            g.box(ax - 1.8, ay - 3.8, zbar - 14.0, ax + 1.8, ay + 3.8, zbar - 7.0, 1)   # its receptacle
            ys = yr - 19.0 + 2.9 * k                                                # its place under the ribbon
            xk, zk = xe - side * 2.4 * (k % 2), -4.0 - 2.9 * (k // 2)              # its place in the edge bundle
            out = ax + 4.0 * (1 if (k % 2) == (side > 0) else -1)
            path = [(tx, ty, tz - 3.0), (tx, ty, zw), (tx, ys, zw), (xk - side * 6.0, ys, zw), (xk, ys - 8.0, zk),
                    (xk, ay + 6.0, zk), (xk, ay, zbar - 16.0), (out, ay, zbar - 16.0), (ax, ay, zbar - 14.0)]
            me = cable.round_cable(cable.smooth(path, 6), R, 'wire_yellow', 10)
            n += 1; o = bpy.data.objects.new(f'ground wire {n}', to_mesh(me, f'ground wire {n}')); hc.objects.link(o); o.parent = root
    o = bpy.data.objects.new('star bars', g.mesh('star bars')); hc.objects.link(o); o.parent = root
    return n
def box(name, x0, y0, z0, x1, y1, z1, m, c):
    g = Geo([m]); g.box(x0, y0, z0, x1, y1, z1, 0)
    o = bpy.data.objects.new(name, g.mesh(name)); c.objects.link(o); return o
frame = coll('frame', console)
TUB = -45.0                                       # tub floor: side-B parts reach z -27 (16 mm elko), jack board -14
xs_, x = [], 0.0
for item in order:
    xs_.append(({'S': 'strip', 'M': 'master'}.get(item, 'group'), x)); x += 2 * PITCH if item == 'M' else PITCH
print('ground wires', ground_harness(xs_))
for yc in panel_layout.RAIL_LINES:                  # 10 x 50 flat-bar rails, 2 mm into each cheek (frame_proposal.md)
    (r0, r1), rw, rh = panel_layout.rail_span(), panel_layout.RAIL_W, panel_layout.RAIL_H
    y0r, y1r = yc - rw / 2, yc + rw / 2
    if yc != panel_layout.RAIL_LINES[0]:
        box(f'rail {yc:.0f}', r0, y0r, PANEL_Z0 - rh, r1, y1r, PANEL_Z0, M['alu'], frame).parent = root
        continue
    zs0, zs1 = PANEL_Z0 - rh / 2 - panel_layout.VENT_H / 2, PANEL_Z0 - rh / 2 + panel_layout.VENT_H / 2   # back rail: vent slots
    box('rail back top', r0, y0r, zs1, r1, y1r, PANEL_Z0, M['alu'], frame).parent = root
    box('rail back bottom', r0, y0r, PANEL_Z0 - rh, r1, y1r, zs0, M['alu'], frame).parent = root
    xs = [r0] + [r0 + c + s * panel_layout.VENT_W / 2 for c in panel_layout.vent_slots() for s in (-1, 1)] + [r1]
    for k in range(0, len(xs), 2):                    # the webs between the slots
        box(f'rail back web {k // 2}', xs[k], y0r, zs0, xs[k + 1], y1r, zs1, M['alu'], frame).parent = root
PL = panel_layout                                 # the tub (tub_proposal.md TB1-TB4): floor with inlet slots, arm-rest, plenum
fz0, fz1 = PL.FLOOR_TOP - PL.FLOOR_T, PL.FLOOR_TOP
fx0, fx1 = -PL.CHEEK_GAP - PL.DADO, width + PL.CHEEK_GAP + PL.DADO
rows = sorted(PL.INLET_ROWS); ys = [PL.FLOOR_Y[0]]
for r in rows: ys += [r - PL.INLET_W / 2, r + PL.INLET_W / 2]
ys.append(PL.FLOOR_Y[1])
for k in range(0, len(ys), 2):                    # solid strips between the slot rows
    box(f'tub floor {k // 2}', fx0, ys[k], fz0, fx1, ys[k + 1], fz1, M['hdr'], frame).parent = root
for r in rows:                                    # the bridges between the slots of each row
    sl = sorted((a, b) for a, b, y in PL.inlet_slots() if y == r)
    edges = [fx0] + [v for a, b in sl for v in (a, b)] + [fx1]
    for k in range(0, len(edges), 2):
        box(f'tub floor bridge {r:.0f} {k // 2}', edges[k], r - PL.INLET_W / 2, fz0, edges[k + 1], r + PL.INLET_W / 2, fz1, M['hdr'], frame).parent = root
box('arm-rest', -PL.CHEEK_GAP, PL.ARM_Y[0], fz0, width + PL.CHEEK_GAP, PL.ARM_Y[1], PL.ARM_TOP, M['wood'], frame).parent = root
box('plenum rear wall', -PL.CHEEK_GAP, PL.PLENUM_WALL_Y[0], fz0, width + PL.CHEEK_GAP, PL.PLENUM_WALL_Y[1], PL.PLENUM_CAP_Z, M['wood'], frame).parent = root
box('plenum cap', -PL.CHEEK_GAP, PL.PLENUM_CAP_Y[0], PL.PLENUM_CAP_Z, width + PL.CHEEK_GAP, PL.PLENUM_CAP_Y[1], PL.PLENUM_CAP_Z + PL.PLENUM_CAP_T, M['wood'], frame).parent = root
zn = (fz0 + PL.PLENUM_CAP_Z) / 2                  # the NC7MD-LX on the rear wall's outside (D-size flange and barrel)
box('NC7MD-LX flange', PL.NC7_X - 13, PL.PLENUM_WALL_Y[0] - 2.5, zn - 15.5, PL.NC7_X + 13, PL.PLENUM_WALL_Y[0], zn + 15.5, M['steel'], frame).parent = root
box('NC7MD-LX body', PL.NC7_X - 11, PL.PLENUM_WALL_Y[1], zn - 11, PL.NC7_X + 11, PL.PLENUM_WALL_Y[1] + 19, zn + 11, M['plastic'], frame).parent = root
TILT = PL.TILT_DEG                                # front (fader end) lower, towards the engineer
root.rotation_euler[0] = math.radians(TILT)
root.location = (-width / 2 * S, PL.MOUNT_Y * S, PL.MOUNT_Z * S)
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
for xc in (-PL.CHEEK_GAP - PL.CHEEK_T, width + PL.CHEEK_GAP):  # cheeks: the shared outline (on the desk; nothing under the floor)
    prism(f'cheek {xc:.0f}', root.location.x + xc * S, root.location.x + (xc + PL.CHEEK_T) * S,
          [(yy * S, zz * S) for yy, zz in PL.cheek_outline()], M['wood'], frame)
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
    o = bpy.data.objects.new(name, ld); sc.collection.objects.link(o); o.location = loc; aim(o, target); return o
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
    for fn, xc, yc, sc_, res in (('panel_strip.png', strip_x[0] + 19.0, 172.0, 0.30, (1300, 2800)),
                                 ('panel_strip_top.png', strip_x[0] + 19.0, 95.0, 0.12, (900, 1500)),   # gain to LF
                                 ('panel_master.png', master_x + 39.3, 168.0, 0.30, (1700, 2800))):
        shot(scene, cam, fn, W(xc, yc, PANEL_Z1) + nrm * 1.0, None, ortho=sc_, res=res, rot=(math.radians(TILT), 0, 0))
    panels_visible(False)                          # the inside: panel layer hidden
    c = W(master_x + 39.3, 250, 0)
    shot(scene, cam, 'internals.png', c + Vector((-0.42, -0.62, 0.48)), c, lens=40)
    c = W(master_x + 39.3, 150, -5)
    shot(scene, cam, 'internals_closeup.png', c + Vector((-0.16, -0.20, 0.16)), c, lens=35)
    frame.hide_render = True                       # the wiring from below: tub, frame and desk hidden, lit from below
    desk = bpy.data.objects['desk']; desk.hide_render = True
    c = W(master_x + 39.3, 300, -20)
    under = light(scene, 'under', 'AREA', c + Vector((0.3, -0.4, -0.9)), c, 60, 2.0)
    shot(scene, cam, 'wiring.png', c + Vector((-0.55, 0.35, -0.55)), c, lens=28, res=(2400, 1350))
    frame.hide_render = desk.hide_render = False; under.hide_render = True
    panels_visible(True)
    shot(bench, bcam, 'strip_side.png', (-1.0, -0.252, 0.0), None, ortho=0.56, res=(2400, 440),
         rot=(math.radians(90), 0, math.radians(-90)))
    shot(bench, bcam, 'strip_under.png', (-0.16, 0.07, -0.14), (0.019, -0.11, 0.0), lens=30)
    shot(mbench, mcam, 'master_under.png', (-0.17, 0.09, -0.21), (0.039, -0.17, -0.005), lens=30)

def flythrough(sc, fps=30):
    """Fly camera (30 s): establishing shot and an arc across the front, a low glide along the strips over the knobs, the
    master up close, straight down over it while the panels vanish, the inside, then under the console (tub, frame
    and desk hidden, lit from below) for the ground harness and the PSU cable. The camera tracks an empty; both are
    keyframed with smooth (auto-clamped) curves. tools/fly_render.py renders it (preview / final)."""
    mc = master_x + 39.3; Z = PANEL_Z1; V = Vector
    keys = [   # frame, camera, target, lens
        (1, mid + V((-1.7, -1.7, 1.3)), mid, 35),
        (150, mid + V((0.0, -2.0, 1.1)), mid, 35),
        (260, mid + V((1.5, -1.3, 0.75)), W(width * 0.7, 250, Z), 40),
        (340, W(width + 60, 570, Z + 45), W(width - 160, 300, Z), 26),
        (480, W(-60, 570, Z + 45), W(160, 300, Z), 26),
        (560, W(mc, 560, Z) + nrm * 0.14, W(mc, 250, Z), 30),
        (640, W(mc, 250, Z) + nrm * 0.95, W(mc, 252, Z), 35),
        (700, W(mc, 250, Z) + nrm * 0.80, W(mc, 252, Z), 35),
        (770, W(mc, 250, 0) + V((-0.42, -0.62, 0.48)), W(mc, 250, 0), 40),
        (820, W(mc, 760, -30), W(mc, 300, -20), 30),
        (870, W(mc, 300, -20) + V((-0.55, 0.35, -0.55)), W(mc, 300, -20), 28),
        (900, W(mc, 300, -20) + V((0.45, 0.45, -0.70)), W(mc, 300, -20), 28)]
    cam_d = bpy.data.cameras.new('fly camera'); cam_d.clip_start = 0.005; cam_d.clip_end = 50
    fc = bpy.data.objects.new('fly camera', cam_d); sc.collection.objects.link(fc)
    ft = bpy.data.objects.new('fly target', None); sc.collection.objects.link(ft)
    tr = fc.constraints.new('TRACK_TO'); tr.target = ft; tr.track_axis = 'TRACK_NEGATIVE_Z'; tr.up_axis = 'UP_Y'
    ed = bpy.context.preferences.edit                    # smooth moves: Bezier keys with auto-clamped handles
    ed.keyframe_new_interpolation_type = 'BEZIER'; ed.keyframe_new_handle_type = 'AUTO_CLAMPED'
    for f, cl, tg, lens in keys:
        fc.location = cl; fc.keyframe_insert('location', frame=f)
        ft.location = tg; ft.keyframe_insert('location', frame=f)
        cam_d.lens = lens; cam_d.keyframe_insert('lens', frame=f)
    def hide(ids, on_from, off_from=None):
        """Hidden (render and viewport) from frame on_from (to off_from); booleans step."""
        for it in ids:
            for f, h in ((1, False), (on_from, True)) + (((off_from, False),) if off_from else ()):
                it.hide_render = h; it.keyframe_insert('hide_render', frame=f)
                if hasattr(it, 'hide_viewport'): it.hide_viewport = h; it.keyframe_insert('hide_viewport', frame=f)
    objs = lambda c: list(c.all_objects)                 # collections' own flags can't be keyframed: their objects'
    hide([o for s in (strip, group, master) for o in objs(bpy.data.collections[s.name + ' panel'])] +
         [o for o in modules.objects if o.type == 'FONT'], 610)                        # the reveal
    hide(objs(frame) + [bpy.data.objects['desk']], 800)                                # under the console
    ul = light(sc, 'fly under light', 'AREA', W(mc, 300, -20) + V((0.3, -0.4, -0.9)), W(mc, 300, -20), 60, 2.0)
    ul.hide_render = True; ul.keyframe_insert('hide_render', frame=1)
    ul.hide_render = False; ul.keyframe_insert('hide_render', frame=800)
    sc.frame_start, sc.frame_end, sc.render.fps = 1, 900, fps
    sc.camera = fc; sc.frame_set(1)
flythrough(scene)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUTDIR, 'goa_console.blend'))
print('saved', os.path.join(OUTDIR, 'goa_console.blend'), 'width', round(width, 1), 'mm')
