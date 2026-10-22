"""Build the goa console in Blender from the placed boards (render/strip.json, group.json, master.json from
tools/export_3d.py).
  /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python tools/console_3d.py -- render
Writes render/goa_console.blend (scenes 'console' and 'strip bench') and renders console.png, console_plan.png
(orthographic, square to the panel), closeup_strips.png, closeup_master.png, strip_side.png (orthographic
elevation of one strip: panel / main board / jack board stack), strip_under.png and master_under.png.
Strip, group and master are exact: every footprint at its placed position and side, the panel features (pot
shafts, switches, LEDs, jacks, XLRs, faders, meters) on their panel coordinates, each jack board 24 mm under its
panel. Each module is a collection, instanced along the console (24 strips, 4 groups, 1 master).
Board coordinates are mm, y down; Blender X = x, Y = -y, Z up, in metres. Main board top at z = 0, panel
underside at 11.5, jack board top at -12.5. The console sits 9 degrees tilted (fader end lower) in a tub with
walnut cheeks; panel finish and cap colours are placeholders, not decisions."""
import bpy, bmesh, json, math, os, sys
from mathutils import Vector

ARGV = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['render']
OUTDIR = os.path.abspath(ARGV[0])
S = 0.001
PANEL_Z0, PANEL_Z1, JB_Z = 11.5, 13.0, -12.5
HP = 5.08; PITCH = 8 * HP                      # 40.64 mm per 8 HP module

# ---------------------------------------------------------------- scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene; scene.name = 'console'
scene.unit_settings.system = 'METRIC'; scene.unit_settings.length_unit = 'MILLIMETERS'

def coll(name, parent=None):
    c = bpy.data.collections.new(name); (parent or scene.collection).children.link(c); return c

MATS = {}
def mat(name, rgb, metal=0.0, rough=0.5, emit=0.0, alpha=1.0):
    if name in MATS: return MATS[name]
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = (*rgb, 1); p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = rough
    if emit:
        p.inputs['Emission Color'].default_value = (*rgb, 1); p.inputs['Emission Strength'].default_value = emit
    if alpha < 1:
        p.inputs['Alpha'].default_value = alpha
    MATS[name] = m; return m

M = dict(pcb=mat('pcb green', (0.02, 0.16, 0.06), rough=0.35), panel=mat('panel anodised', (0.03, 0.032, 0.036), metal=0.3, rough=0.45),
         legend=mat('legend white', (0.9, 0.9, 0.88), rough=0.6), chip=mat('ic black', (0.015, 0.015, 0.015), rough=0.4),
         res=mat('resistor', (0.04, 0.04, 0.04), rough=0.5), cap=mat('ceramic cap', (0.45, 0.33, 0.2), rough=0.5),
         elko=mat('electrolytic', (0.05, 0.1, 0.35), rough=0.35), alu=mat('aluminium', (0.8, 0.8, 0.82), metal=1, rough=0.25),
         film=mat('film cap red', (0.6, 0.05, 0.04), rough=0.4), hdr=mat('header black', (0.02, 0.02, 0.02), rough=0.6),
         pot=mat('pot body', (0.12, 0.12, 0.13), metal=0.5, rough=0.4), knob=mat('knob black', (0.02, 0.02, 0.022), rough=0.45),
         jack=mat('jack black', (0.03, 0.03, 0.03), rough=0.55), brass=mat('brass', (0.8, 0.6, 0.3), metal=1, rough=0.3),
         sw=mat('switch body', (0.06, 0.06, 0.06), rough=0.5), wood=mat('walnut', (0.18, 0.09, 0.045), rough=0.55),
         slot=mat('slot', (0.0, 0.0, 0.0), rough=0.9), floor=mat('desk', (0.035, 0.035, 0.038), rough=0.7))
CAP = {'red': mat('cap red', (0.7, 0.04, 0.03), rough=0.35), 'blue': mat('cap blue', (0.05, 0.2, 0.7), rough=0.35),
       'dblue': mat('cap dark blue', (0.03, 0.06, 0.25), rough=0.35), 'yellow': mat('cap yellow', (0.85, 0.65, 0.05), rough=0.35),
       'green': mat('cap green', (0.05, 0.5, 0.12), rough=0.35), 'white': mat('cap white', (0.85, 0.85, 0.82), rough=0.35),
       'grey': mat('cap grey', (0.35, 0.36, 0.38), rough=0.4), 'orange': mat('cap orange', (0.9, 0.35, 0.04), rough=0.35)}
LED = {'red': mat('led red', (1, 0.05, 0.02), emit=4), 'green': mat('led green', (0.1, 1, 0.15), emit=4),
       'yellow': mat('led yellow', (1, 0.8, 0.05), emit=4), 'amber': mat('led amber', (1, 0.45, 0.02), emit=4),
       'off': mat('led off', (0.25, 0.02, 0.02), rough=0.2)}

def obj(name, me, c, m):
    o = bpy.data.objects.new(name, me); c.objects.link(o)
    if m: o.data.materials.append(m)
    return o

def box(name, x0, y0, z0, x1, y1, z1, m, c):
    """Axis-aligned box, board coordinates (mm, y down)."""
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector(((x0 + x1) / 2 + v.co.x * abs(x1 - x0), -((y0 + y1) / 2 + v.co.y * abs(y1 - y0)), (z0 + z1) / 2 + v.co.z * abs(z1 - z0))) * S
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    return obj(name, me, c, m)

def cyl(name, cx, cy, z0, z1, r, m, c, n=32):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r, depth=abs(z1 - z0))
    for v in bm.verts: v.co = Vector((cx + v.co.x, -cy - v.co.y, (z0 + z1) / 2 + v.co.z)) * S
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for f in me.polygons: f.use_smooth = True
    return obj(name, me, c, m)

def text(name, s, x, y, z, size, m, c, align='CENTER', rot=0):
    cu = bpy.data.curves.new(name, 'FONT'); cu.body = s; cu.size = size * S; cu.align_x = align; cu.align_y = 'CENTER'
    o = bpy.data.objects.new(name, cu); c.objects.link(o); o.location = (x * S, -y * S, z * S); o.rotation_euler[2] = rot
    o.data.materials.append(m); return o

# ---------------------------------------------------------------- panel controls (shared by every module)
def knob(c, name, x, y, colour, big=False):
    r = 7.0 if not big else 8.0
    cyl(name + ' skirt', x, y, PANEL_Z1, PANEL_Z1 + 2.5, r + 0.6, M['knob'], c)
    cyl(name + ' knob', x, y, PANEL_Z1 + 2.5, PANEL_Z1 + 15.5, r - 0.5, M['knob'], c)
    cyl(name + ' cap', x, y, PANEL_Z1 + 15.5, PANEL_Z1 + 16.2, r - 1.6, CAP[colour], c)
    box(name + ' line', x - 0.35, y - r + 0.9, PANEL_Z1 + 2.5, x + 0.35, y - r + 3.8, PANEL_Z1 + 16.3, M['legend'], c)

def switch_cap(c, name, x, y, colour):
    box(name + ' cap', x - 3.7, y - 3.7, PANEL_Z1 + 0.5, x + 3.7, y + 3.7, PANEL_Z1 + 6.0, CAP[colour], c)

def led(c, name, x, y, colour, big=False):
    k = 5 / 3 if big else 1.0
    cyl(name + ' bezel', x, y, PANEL_Z1, PANEL_Z1 + 0.8, 2.3 * k, M['alu'], c)
    cyl(name + ' lens', x, y, PANEL_Z1, PANEL_Z1 + 2.2, 1.5 * k, LED[colour], c, 16)

def jack_nut(c, name, x, y):
    cyl(name + ' nut', x, y, PANEL_Z1, PANEL_Z1 + 3.0, 7.2, M['jack'], c, 6)
    cyl(name + ' socket', x, y, PANEL_Z1 + 2.9, PANEL_Z1 + 3.05, 3.4, M['slot'], c)

def xlr(c, name, x, y):
    cyl(name + ' flange', x, y, PANEL_Z1, PANEL_Z1 + 1.2, 12.0, M['alu'], c)
    cyl(name + ' insert', x, y, PANEL_Z1 + 1.1, PANEL_Z1 + 1.3, 8.5, M['jack'], c)
    for k in range(3):
        a = math.radians(90 + 120 * k)
        cyl(name + f' pin {k + 1}', x + 4.4 * math.cos(a), y - 4.4 * math.sin(a), PANEL_Z1 + 1.2, PANEL_Z1 + 1.35, 0.9, M['slot'], c, 12)

def fader(c, name, x, ytop, ybot, pos, colour='grey', dual=False):
    box(name + ' slot', x - 1.0, ytop, PANEL_Z1, x + 1.0, ybot, PANEL_Z1 + 0.05, M['slot'], c)
    for k in range(11):
        yy = ytop + (ybot - ytop) * k / 10
        w = 3.0 if k in (0, 3, 10) else 1.8
        box(name + f' tick {k}', x - 5.5 - w, yy - 0.2, PANEL_Z1, x - 5.5, yy + 0.2, PANEL_Z1 + 0.05, M['legend'], c)
    y = ytop + (ybot - ytop) * (1 - pos)
    wdt = 11 if not dual else 14
    box(name + ' knob', x - wdt / 2, y - 6, PANEL_Z1 + 1.5, x + wdt / 2, y + 6, PANEL_Z1 + 12, M['knob'], c)
    box(name + ' knob line', x - wdt / 2 - 0.01, y - 0.4, PANEL_Z1 + 1.5, x + wdt / 2 + 0.01, y + 0.4, PANEL_Z1 + 12.05, CAP[colour], c)

def panel(c, name, x0, width, label=None):
    box(name + ' panel', x0 + 0.15, -11, PANEL_Z0, x0 + width - 0.15, 503, PANEL_Z1, M['panel'], c)
    for yy in (-8, 500):                                       # rail screws, 7.5 mm from the panel ends
        for xx in ((x0 + 7.5,) if width < 50 else (x0 + 7.5, x0 + width - 7.5)):
            cyl(name + f' screw {xx:.0f} {yy}', xx, yy, PANEL_Z1, PANEL_Z1 + 1.2, 2.8, M['alu'], c, 16)
    if label: text(name + ' label', label, x0 + width / 2, 494, PANEL_Z1 + 0.02, 3.0, M['legend'], c)

def legend(c, s, x, y, size=2.0):
    text('legend ' + s + f' {x:.0f} {y:.0f}', s, x, y, PANEL_Z1 + 0.02, size, M['legend'], c)

# ---------------------------------------------------------------- modules from their placed boards
# panel names and cap colours per module: {ref: (legend, colour)}; jacks and XLRs: {ref: (legend, None)}
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
ELKO_H = {'5.0': 11.0, '6.3': 11.0, '8.0': 11.5, '10.0': 16.0, '12.5': 20.0, '16.0': 25.0}
M.update(relay=mat('relay case', (0.78, 0.76, 0.7), rough=0.5), term=mat('terminal green', (0.05, 0.35, 0.12), rough=0.5),
         trim=mat('trimmer blue', (0.05, 0.15, 0.6), rough=0.4), ptc=mat('PTC yellow', (0.75, 0.55, 0.05), rough=0.5),
         diode=mat('glass diode', (0.7, 0.3, 0.1), rough=0.2))

def led_state(p, names):
    """(legend, colour) of an LED: from the names, or a meter LED from its value ('green -20 dB' ... 'red +18 dB')."""
    if p['ref'] in names: return names[p['ref']]
    v = p['value'].split()
    if len(v) == 3 and v[2] == 'dB':
        return None, (v[0] if int(v[1]) <= 4 else 'off')          # a static picture: lit up to +4 dB
    return None, 'off'

def part_3d(c, p, z_top, z_bot, names):
    """One placed footprint as a simple solid. z_top: board top surface; z_bot: bottom surface."""
    fp, ref = p['fp'], p['ref']
    l, t, r, b = p['box']; sx = 0.25 if (r - l) > 2 else 0.0
    l, t, r, b = l + sx, t + sx, r - sx, b - sx
    up = p['side'] == 'F'
    def slab(h, m, inset=0.0):
        z0, z1 = (z_top, z_top + h) if up else (z_bot - h, z_bot)
        return box(ref, l + inset, t + inset, z0, r - inset, b - inset, z1, m, c)
    cx, cy = (l + r) / 2, (t + b) / 2
    name, colour = names.get(ref, ('', 'grey'))
    if 'MountingHole_4.3mm_M4' in fp:                                    # ground stud: M4 bolt and nut
        cyl(ref + ' nut', p['x'], p['y'], z_top, z_top + 3.2, 3.6, M['alu'], c, 6)
        cyl(ref + ' bolt', p['x'], p['y'], z_bot - 12, z_top + 4.5, 2.0, M['alu'], c, 16)
    elif 'MountingHole' in fp:
        cyl(ref + ' standoff', p['x'], p['y'], z_top, PANEL_Z0, 2.75, M['alu'], c, 6)
    elif 'Resistor_SMD' in fp: slab(0.55, M['res'], 0.35)
    elif 'Capacitor_SMD' in fp: slab(0.9, M['cap'], 0.35)
    elif 'Inductor_SMD' in fp: slab(0.9, M['hdr'], 0.35)
    elif 'SOIC' in fp or 'SOT-23' in fp or 'D_SMA' in fp or 'D_SMC' in fp or 'SOD' in fp: slab(1.5 if 'SOIC' in fp else 1.1, M['chip'], 0.6)
    elif 'TO-263' in fp: slab(4.5, M['chip'], 0.8)
    elif 'Relay' in fp: slab(5.2, M['relay'], 0.4)
    elif 'DO-35' in fp: slab(1.9, M['diode'], 1.2)
    elif 'Fuse_Bourns' in fp: slab(12.0, M['ptc'], 0.5)
    elif 'TerminalBlock' in fp: slab(10.0, M['term'], 0.3)
    elif 'Potentiometer_Bourns_3296' in fp: slab(10.0, M['trim'], 0.3)
    elif 'CP_Radial' in fp:
        d = fp.split('_D')[1].split('mm')[0]; h = ELKO_H.get(d, 12.0); rr = float(d) / 2
        z0, z1 = (z_top, z_top + h) if up else (z_bot - h, z_bot)
        cyl(ref, cx, cy, z0, z1, rr, M['elko'], c)
        cyl(ref + ' top', cx, cy, (z1 - 0.3) if up else z0 - 0.01, (z1 + 0.01) if up else z0 + 0.3, rr * 0.92, M['alu'], c)
    elif 'C_Rect' in fp: slab(9.0, M['film'], 0.6)
    elif 'IDC-Header' in fp or 'PinSocket' in fp or 'PinHeader' in fp: slab(8.8, M['hdr'], 0.3)
    elif 'Keystone_1287' in fp: slab(8.0, M['alu'], 1.0)
    elif 'Potentiometer_Alpha' in fp:
        dual = 'Dual' in fp; slab(11.5 if dual else 6.5, M['pot'], 0.6)
        fx, fy = p['feature']; z1 = z_top + (11.5 if dual else 6.5)
        cyl(ref + ' bushing', fx, fy, z1, PANEL_Z0, 3.5, M['alu'], c)
        cyl(ref + ' shaft', fx, fy, PANEL_Z0, PANEL_Z1 + 3, 3.0, M['alu'], c)
        knob(c, ref, fx, fy, colour or 'grey', big=name == 'C/ROOM'); legend(c, name, fx, fy - 9.6)
    elif 'PVA2' in fp:
        slab(9.0, M['sw'], 0.5)
        fx, fy = p['feature']
        cyl(ref + ' actuator', fx, fy, z_top + 9, PANEL_Z1 + 0.6, 1.6, M['sw'], c, 12)
        switch_cap(c, ref, fx, fy, colour or 'grey'); legend(c, name, fx, fy - 5.6, 1.7)
    elif 'LED_D3.0mm' in fp or 'LED_D5.0mm' in fp:
        fx, fy = p['feature']; big = 'D5.0' in fp
        cyl(ref + ' spacer', fx, fy, z_top, z_top + 7.6, 3.0 if big else 2.0, M['hdr'], c, 12)
        name, colour = led_state(p, names); led(c, ref, fx, fy, colour, big)
        if name: legend(c, name, fx, fy - (5.0 if big else 3.8), 1.6)
    elif 'PTB014' in fp:
        dual = 'Dual' in fp; slab(9.5, M['pot'], 0.4)
        fx, fy = p['feature']
        fader(c, ref, fx, fy - 50.0, fy + 50.0, 0.75, colour or 'grey', dual)
        if name: legend(c, name, fx, fy + 60.0, 2.4 if dual else 2.0)
    elif 'NJ6FD-V' in fp:
        fx, fy = p['feature']
        box(ref + ' body', fx - 6.4, fy - 7.5, z_top, fx + 6.4, fy + 7.5, PANEL_Z0, M['jack'], c)
        jack_nut(c, ref, fx, fy); legend(c, name, fx, fy - 9.8, 1.8)
    elif 'NC3MAV' in fp:
        fx, fy = p['feature']
        cyl(ref + ' body', fx, fy, z_top, PANEL_Z0, 11.0, M['jack'], c)
        xlr(c, ref, fx, fy); legend(c, name, fx, fy - 14.5, 1.8)
    elif 'NetTie' in fp or 'SolderJumper' in fp: pass
    else: slab(1.0, M['chip'])

def module(title, key, names, width, label=None):
    """A module from render/<key>.json: main board at z 0, jack board (starts at y 0) 24 mm under the panel."""
    c = coll(title)
    for bd in json.load(open(os.path.join(OUTDIR, key + '.json'))):
        jackboard = bd['y0'] < 10
        zt = JB_Z if jackboard else 0.0
        box(('jack board PCB' if jackboard else 'main board PCB') + ' ' + key, bd['x0'], bd['y0'], zt - 1.6, bd['x1'], bd['y1'], zt, M['pcb'], c)
        for p in bd['parts']: part_3d(c, p, zt, zt - 1.6, names)
    panel(c, key, -1.15, width, label)
    return c

strip = module('channel strip', 'strip', STRIP, 8 * HP - 0.34)
group = module('group module', 'group', GROUP, 8 * HP - 0.34)
master = module('master module', 'master', MASTER, 16 * HP - 0.34, 'MASTER')
for side, x in (('L', 18.0), ('R', 60.6)):                       # meter legends: channel letter, dB scale outboard
    legend(master, side, x, 318.5, 2.4)
    for v in (18, 12, 6, 0, -6, -12, -20):
        legend(master, f'{v:+d}' if v else '0', x + (-6.0 if side == 'L' else 6.2), 422.0 - 5.0 * (v + 20) / 2, 1.5)

# ---------------------------------------------------------------- console: 12 strips | 2 groups | master | 2 groups | 12 strips
console = coll('console')
root = bpy.data.objects.new('console root', None); console.objects.link(root)
modules = coll('modules', console)
order = ['S'] * 12 + ['G1', 'G2', 'M', 'G3', 'G4'] + ['S'] * 12
def instance(name, src, x):
    e = bpy.data.objects.new(name, None); e.instance_type = 'COLLECTION'; e.instance_collection = src
    e.location = (x * S, 0, 0); modules.objects.link(e); e.parent = root
x, n = 0.0, 0
strip_x, group_x, master_x = [], [], 0.0
for item in order:
    if item == 'S':
        n += 1; strip_x.append(x); instance(f'strip {n}', strip, x)
        text(f'strip number {n}', str(n), x + 19.0, 494.0, PANEL_Z1 + 0.03, 3.0, M['legend'], modules).parent = root
        x += PITCH
    elif item == 'M':
        master_x = x; instance('master', master, x); x += 2 * PITCH
    else:
        group_x.append(x); instance(f'group {item[1]}', group, x)
        text(f'group label {item[1]}', f'GROUP {item[1]}', x + 19.0, 494.0, PANEL_Z1 + 0.03, 3.0, M['legend'], modules).parent = root
        x += PITCH
width = x
for src in (strip, group, master):                 # the sources; the instances render
    bpy.context.view_layer.layer_collection.children[src.name].exclude = True
# tub in module coordinates: panel-end rails, floor; walnut front arm-rest and back trim
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
    """Prism along world X (metres) over a world (Y, Z) profile."""
    bm = bmesh.new()
    a = [bm.verts.new((xw0, y, z)) for y, z in prof]; b = [bm.verts.new((xw1, y, z)) for y, z in prof]
    bm.faces.new(a); bm.faces.new(b[::-1])
    for i in range(len(prof)):
        j = (i + 1) % len(prof); bm.faces.new((a[i], b[i], b[j], a[j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    return obj(name, me, c, m)
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
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
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

setup(scene)
mid = W(width / 2, 250, PANEL_Z1)
light(scene, 'key', 'AREA', mid + Vector((-0.9, -1.1, 1.5)), mid, 55, 1.4)
light(scene, 'fill', 'AREA', mid + Vector((1.4, -0.6, 1.0)), mid, 18, 2.0)
light(scene, 'rim', 'AREA', mid + Vector((0.2, 1.4, 1.1)), mid, 30, 2.0)
cam = camera(scene, 'console camera')

# a second scene with one strip on the bench, for the stack views
bench = bpy.data.scenes.new('strip bench'); bench.collection.children.link(strip)
bench.unit_settings.system = 'METRIC'; bench.unit_settings.length_unit = 'MILLIMETERS'
setup(bench)
sm = Vector((0.019, -0.25, 0.0))
light(bench, 'key', 'AREA', sm + Vector((-0.5, -0.3, 0.6)), sm, 12, 0.6)
light(bench, 'under', 'AREA', sm + Vector((-0.4, 0.1, -0.5)), sm, 6, 0.8)
light(bench, 'fill', 'AREA', sm + Vector((0.6, 0.2, 0.2)), sm, 5, 0.8)
bcam = camera(bench, 'bench camera')

# and the master module on its own bench, for the view from underneath (main board + jack board)
mbench = bpy.data.scenes.new('master bench'); mbench.collection.children.link(master)
mbench.unit_settings.system = 'METRIC'; mbench.unit_settings.length_unit = 'MILLIMETERS'
setup(mbench)
mm_ = Vector((0.039, -0.25, 0.0))
light(mbench, 'key', 'AREA', mm_ + Vector((-0.5, -0.3, 0.6)), mm_, 14, 0.6)
light(mbench, 'under', 'AREA', mm_ + Vector((-0.3, 0.2, -0.6)), mm_, 9, 0.8)
light(mbench, 'fill', 'AREA', mm_ + Vector((0.6, 0.2, -0.2)), mm_, 6, 0.8)
mcam = camera(mbench, 'master bench camera')

n = root.matrix_world.to_3x3() @ Vector((0, 0, 1))
shot(scene, cam, 'console.png', mid + Vector((-0.75, -1.45, 1.0)), mid + Vector((0.0, -0.03, -0.05)), lens=36)
shot(scene, cam, 'console_plan.png', W(width / 2, 252, PANEL_Z1) + n * 2.0, None, ortho=1.36, res=(3200, 1480),
     rot=(math.radians(TILT), 0, 0))
c = W(strip_x[1] + 20, 150, PANEL_Z1)
shot(scene, cam, 'closeup_strips.png', c + Vector((-0.20, -0.36, 0.22)), c, lens=50)
c = W(master_x + 39.3, 235, PANEL_Z1)
shot(scene, cam, 'closeup_master.png', c + Vector((0.06, -0.46, 0.42)), c, lens=34)
shot(bench, bcam, 'strip_side.png', (-1.0, -0.252, 0.0), None, ortho=0.56, res=(2400, 440),
     rot=(math.radians(90), 0, math.radians(-90)))
shot(bench, bcam, 'strip_under.png', (-0.16, 0.07, -0.14), (0.019, -0.11, 0.0), lens=30)
shot(mbench, mcam, 'master_under.png', (-0.17, 0.09, -0.21), (0.039, -0.17, -0.005), lens=30)

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUTDIR, 'goa_console.blend'))
print('saved', os.path.join(OUTDIR, 'goa_console.blend'), 'width', round(width, 1), 'mm')
