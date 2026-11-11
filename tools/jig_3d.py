"""The test jig on a bench, in Blender (test_jig_spec.md v0.11, the full build of stage C: four strips, the master
stub, the load board, the 0.6 m ribbon, the ground bar, a bench supply and an analyser). Run headless:
  /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python tools/jig_3d.py -- render
Writes render/jig.blend and render/jig*.png. A picture of how the jig goes together, not a drawing to build from.

The builders (KiCad GLB import, the tools/models3d parts, the strip module, sockets, cables) are console_3d.py's:
this script runs that file up to the point where it builds the console, and its render-setup block. The strip is
the console's module with its panel; the two jig boards are their KiCad boards as placed, on 10 mm M3 feet.
Read from the boards: every position, the bus headers' pin 1 (the ribbon's red stripe), the spades, the bench
terminal, the BNCs. NOT in the spec, drawn as a plausible bench: where each board lies, the two battens that carry
the panels (the console's rail lines), the supply and the analyser (generic boxes), the cable routes.
Every bus header has pin 1 at the front (fader) end, the strips' on the bottom side, the jig boards' on the top
side (place_jig.py, 2026-11-11): one flat ribbon runs straight through, the load board at its left end (header on
its right edge), the stub at its right end (header on its left edge), every board the same way up."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, 'console_3d.py')).read()
_cut = _src.index("strip = module('strip')")
_r0 = _src.rindex('\n', 0, _src.index('render setup\n')) + 1
exec(compile(_src[:_cut], os.path.join(HERE, 'console_3d.py'), 'exec'))            # scene, materials, builders

KPY = os.environ.get('KPY', '/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3')
scene.name = 'jig'
NS = 4                                             # strips on the jig
RH = panel_layout.RAIL_H                           # the battens are as high as the console's rails
BENCH = PANEL_Z0 - RH                              # bench top, in the strip's z (main board top = 0)
FOOT = 10.0                                        # M3 feet under the jig boards
ZJ = BENCH + FOOT + 1.6                            # their top side
M.update(bench=mat('bench top', (0.085, 0.09, 0.10), rough=0.7), batten=mat('batten', (0.62, 0.47, 0.27), rough=0.6),
         label=mat('label', (0.95, 0.95, 0.9), rough=0.8, emit=0.6), inst=mat('instrument case', (0.10, 0.11, 0.13), rough=0.45),
         face=mat('instrument front', (0.55, 0.56, 0.58), rough=0.5), disp=mat('display', (0.05, 0.6, 0.25), emit=1.5),
         red=mat('post red', (0.7, 0.04, 0.03), rough=0.35), blue=mat('post blue', (0.03, 0.12, 0.55), rough=0.35))

def bx(name, x0, y0, z0, x1, y1, z1, m, c, bevel=0.0):
    g = Geo([m]); g.box(x0, y0, z0, x1, y1, z1, 0, bevel)
    o = bpy.data.objects.new(name, g.mesh(name)); c.objects.link(o); return o
def wire(name, pts, r, m, c, k=6, stiff=False):
    """Round cable through control points (mm), material a tools/models3d name; stiff = straight runs with round
    bends (a 14 AWG wire) instead of a curve through the points (a flexible lead)."""
    path = cable.fillet(pts) if stiff else cable.smooth(pts, k)
    o = bpy.data.objects.new(name, to_mesh(cable.round_cable(path, r, m, 12), name)); c.objects.link(o); return o
def instance(name, src, x, c):
    e = bpy.data.objects.new(name, None); e.instance_type = 'COLLECTION'; e.instance_collection = src
    e.location = (x * S, 0, 0); c.objects.link(e); return e

# ---------------------------------------------------------------- the four strips, on two battens
strip = module('strip')
jig = coll('jig')
strips = coll('strips', jig)
panels = [instance(f'strip {k + 1} panel', bpy.data.collections[strip.name + ' panel'], k * PITCH, strips) for k in range(NS)]
for k in range(NS): instance(f'strip {k + 1} boards', bpy.data.collections[strip.name + ' boards'], k * PITCH, strips)
layer_collection(strip).exclude = True
bench = coll('bench', jig)
bx('bench top', -700, -500, BENCH - 30, 1100, 1000, BENCH, M['bench'], bench)
for yc in panel_layout.RAIL_LINES:
    bx(f'batten {yc:.0f}', -14, yc - 9, BENCH, NS * PITCH + 14, yc + 9, PANEL_Z0, M['batten'], bench, 0.8)
YB, ZS, P1 = BUS['strip'][0][1:]                   # bus header: centre y, the ribbon's z at the socket, pin-1 y
SX = [k * PITCH + BUS['strip'][0][0] for k in range(NS)]

# ---------------------------------------------------------------- the two jig boards
def board_json(board):
    pcb = os.path.join('boards', board, board + '.kicad_pcb'); out = os.path.join(OUTDIR, board + '.json')
    if not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(os.path.join(PROJ, pcb)):
        with open(out, 'w') as f: subprocess.run([KPY, os.path.join('tools', 'export_3d.py'), pcb], check=True, stdout=f, cwd=PROJ)
        print('exported', out)
    return json.load(open(out))[0]

def jig_board(board, x0, turned):
    """A jig board from KiCad on its feet, left edge at x0, its bus header on the strips' header line; turned = by
    180 degrees (not used since the headers were turned). Returns its parts {ref: part}, KiCad's models {ref: empty} and at(x, y, z): board mm to jig mm."""
    d = board_json(board); c = coll(board, jig); refs = import_board(c, board, 0.0)
    w, h = d['x0'] + d['x1'], d['y0'] + d['y1']
    g = Geo([M['plastic'], M['steel'], M['brass']]); parts = {p['ref']: p for p in d['parts']}; bus = None
    for p in d['parts']:
        fp, ref = p['fp'], p['ref']; reg = lookup(fp)
        if 'IDC-Header_2x17' in fp:
            l, t, r, b = p['box']; cx, cy = (l + r) / 2, (t + b) / 2; px, py = p['pin1']
            me, zr = cable.idc_socket(17, cx, cy, 3.0, 'y', False, 1 if px > cx else -1)
            put(f'{ref} IDC socket', to_mesh(me, f'{board} {ref} socket'), c, 0, 0, 0); bus = (cx, cy, zr, py)
        if p['model']: continue
        if reg:
            mod, kw = reg
            for ch in (refs[ref].children_recursive if ref in refs else ()): bpy.data.objects.remove(ch)
            me = shared(('part', fp, False), lambda: to_mesh(mod.build(**part_kw(mod.build, kw)), fp.split(':')[-1]))
            put(f'{ref} {mod.__name__.rsplit(".", 1)[-1]}', me, c, p['x'], p['y'], 0.0, p['rot'])
        elif 'MountingHole' in fp:
            g.cyl(p['x'], p['y'], -1.6 - FOOT, -1.6, 3.0, 2, 6); g.cyl(p['x'], p['y'], 0.0, 2.0, 2.8, 1, 16)
        elif 'XLR' in fp:                           # NC3MAH: KiCad has no STEP for it; its housing and barrel
            l, t, r, b = p['box']; g.box(l + 0.5, t + 0.5, 0.0, r - 0.5, b - 0.5, 26.0, 0, 0.8)
            g.disc_y((l + r) / 2, b - 0.2, 13.0, 9.6, 1.6, 1)
        elif not ('NetTie' in fp or 'SolderJumper' in fp):
            l, t, r, b = p['box']; g.box(l + 0.3, t + 0.3, 0.0, r - 0.3, b - 0.3, 1.0, 0)
    put(f'{board} feet', g.mesh(f'{board} feet'), c, 0, 0, 0)
    e = bpy.data.objects.new(board + ' origin', None); c.objects.link(e)
    for o in c.objects:
        if o.parent is None and o is not e: o.parent = e
    y0 = YB - (h - bus[1] if turned else bus[1])
    e.location = ((x0 + w) * S, -(y0 + h) * S, ZJ * S) if turned else (x0 * S, -y0 * S, ZJ * S)
    if turned: e.rotation_euler[2] = math.pi
    bpy.context.view_layer.update()
    def at(x, y, z=0.0):
        v = e.matrix_world @ Vector((x * S, -y * S, z * S)); return (v.x / S, -v.y / S, v.z / S)
    return dict(parts=parts, refs=refs, at=at, bus=at(*bus[:3]), pin1=at(bus[0], bus[3])[1], x=(x0, x0 + w), y=(y0, y0 + h))

def wbox(e):
    """Jig-mm bounding box (x0, y0, z0, x1, y1, z1) of a KiCad model."""
    pts = [ch.matrix_world @ Vector(cr) for ch in e.children_recursive if ch.type == 'MESH' for cr in ch.bound_box]
    xs, ys, zs = [p.x / S for p in pts], [-p.y / S for p in pts], [p.z / S for p in pts]
    return min(xs), min(ys), min(zs), max(xs), max(ys), max(zs)

load = jig_board('jig_load_board', -220.0, False)
stub = jig_board('jig_master_stub', 300.0, False)
for name, bd in (('load board', load), ('stub', stub)):
    assert (bd['pin1'] > YB) == (P1 > YB), name + ': pin 1 on the wrong edge of the ribbon'

# ---------------------------------------------------------------- the 34-way ribbon
cables = coll('cables', jig)
(lx, _, lz), (tx, _, tz) = load['bus'], stub['bus']
path = cable.through([(lx, YB, lz)] + [(x, YB, ZS) for x in SX] + [(tx, YB, tz)])     # flat in every socket, a shallow bow between
me = cable.ribbon(path, [(0, 1, 0)], 2.54 * 17, stripe=1 if P1 > YB else -1)
cables.objects.link(bpy.data.objects.new('bus ribbon 34-way', to_mesh(me, 'bus ribbon')))
ribbon_len = sum((Vector(a) - Vector(b)).length for a, b in zip(path, path[1:]))

# ---------------------------------------------------------------- ground bar: one wire per board, radially
BARY, ZBAR, R = 440.0, BENCH + 9.0, 1.45
taps = [('load board', load['at'](load['parts']['CN2']['x'], load['parts']['CN2']['y'], 10.2), 1)]
taps += [(f'strip {k + 1}', (k * PITCH + SPADES['strip'][0][0], SPADES['strip'][0][1], SPADES['strip'][0][2]), -1) for k in range(NS)]
taps += [('stub', stub['at'](stub['parts']['CN1']['x'], stub['parts']['CN1']['y'], 10.2), 1)]
LUG = [176.0 + 16.0 * k for k in range(len(taps))]
g = Geo([M['copper'], M['tin'], M['steel'], M['plastic']])
g.box(LUG[0] - 12, BARY - 6, ZBAR - 3, LUG[-1] + 12, BARY + 6, ZBAR, 0, 0.3)
for xf in (LUG[0] - 8, LUG[-1] + 8): g.box(xf - 3, BARY - 6, BENCH, xf + 3, BARY + 6, ZBAR - 3, 3)
zb = BENCH + R + 0.2                               # a wire lying on the bench
for k, ((name, (sx_, sy_, sz_), up), xl) in enumerate(zip(taps, LUG)):
    g.box(xl - 3.5, BARY - 12, ZBAR, xl + 3.5, BARY + 4, ZBAR + 0.8, 1); g.box(xl - 2.2, BARY - 17, ZBAR, xl + 2.2, BARY - 10, ZBAR + 3.6, 1)
    g.cyl(xl, BARY, ZBAR + 0.8, ZBAR + 3.6, 3.4, 2, 16)
    g.box(sx_ - 3.6, sy_ - 4.5, sz_ - 4.0 if up > 0 else sz_ - 3.0, sx_ + 3.6, sy_ + 4.5, sz_ + 3.0 if up > 0 else sz_ + 4.0, 1)   # receptacle
    end = [(xl, BARY - 40, zb), (xl, BARY - 26, ZBAR + 1.8), (xl, BARY - 17, ZBAR + 1.8)]
    if name.startswith('strip'):                    # straight down from the tab under the board, then its lane along the bench
        lane = 380.0 - 3.4 * (k - 1)
        pts = [(sx_, sy_, sz_ - 3.0), (sx_, sy_, zb), (sx_, lane, zb), (xl, lane, zb)]
    elif name == 'load board':                      # up off the tab, over the back edge, round the board's right side under the ribbon
        ye, xe = load['y'][0], load['x'][1]; lane = 383.4
        pts = [(sx_, sy_, sz_ + 3.0), (sx_, sy_, sz_ + 15), (sx_, ye - 12, sz_ + 15), (sx_, ye - 12, zb), (xe + 14, ye - 12, zb), (xe + 14, lane, zb), (xl, lane, zb)]
    else:                                           # the same off the stub's back edge, round its left side under the ribbon
        ye = stub['y'][0]; xs = stub['x'][0] - 14
        pts = [(sx_, sy_, sz_ + 3.0), (sx_, sy_, sz_ + 15), (sx_, ye - 12, sz_ + 15), (sx_, ye - 12, zb), (xs, ye - 12, zb), (xs, BARY - 40, zb)]
    wire(f'ground wire {name}', pts + end, R, 'wire_yellow', cables, stiff=True)
o = bpy.data.objects.new('ground bar', g.mesh('ground bar')); cables.objects.link(o)

# ---------------------------------------------------------------- bench supply to the stub's terminal
inst = coll('instruments', jig)
PX0, PX1, PY0, PY1, PH = 340.0, 540.0, -70.0, 190.0, 110.0
g = Geo([M['inst'], M['face'], M['red'], M['knob'], M['blue'], M['disp']])
g.box(PX0, PY0, BENCH + 6, PX1, PY1, BENCH + PH, 0, 2.0); g.box(PX0 + 3, PY1, BENCH + 9, PX1 - 3, PY1 + 1.0, BENCH + PH - 3, 1)
for xd in (PX0 + 30, PX0 + 108): g.box(xd, PY1 + 1.0, BENCH + 66, xd + 62, PY1 + 1.6, BENCH + 94, 5)
for xk in (PX0 + 50, PX0 + 128): g.disc_y(xk, PY1 + 6, BENCH + 44, 9.0, 10.0, 3)
POST = [(PX0 + 60.0, 2), (PX0 + 100.0, 3), (PX0 + 140.0, 4)]              # +V red, 0 V black, -V blue
for xp, mi in POST: g.disc_y(xp, PY1 + 8, BENCH + 22, 5.5, 14.0, mi)
for xf in (PX0 + 20, PX1 - 20):
    for yf in (PY0 + 20, PY1 - 20): g.cyl(xf, yf, BENCH, BENCH + 6, 8.0, 3, 16)
inst.objects.link(bpy.data.objects.new('bench supply', g.mesh('bench supply')))
j1 = stub['parts']['J1']; l, t, r, b = j1['box']
entry = 1 if b - j1['y'] > j1['y'] - t else -1     # the wire-entry face: the side the body reaches further
for k, ((xp, _), m) in enumerate(zip(POST, ('wire_red', 'wire_black', 'wire_blue'))):
    px, py, pz = stub['at'](j1['x'] + 5.08 * k, j1['y'] + entry * 5.0, 5.0)
    ye = stub['y'][0]
    pts = [(xp, PY1 + 15, BENCH + 22), (xp, PY1 + 30, BENCH + 20), (xp + 4, PY1 + 55, BENCH + 3), ((xp + px) / 2, (PY1 + ye) / 2 + 12, BENCH + 3)]
    pts += [(px, ye - 14, BENCH + 5), (px, ye - 3, pz + 10), (px, py - 6, pz + 13), (px, py + 1, pz + 6), (px, py, pz)] if entry > 0 else \
           [(px, ye - 14, BENCH + 5), (px, ye - 4, pz + 2), (px, py, pz)]
    wire(f'supply wire {m[5:]}', pts, 1.3, m, cables)

# ---------------------------------------------------------------- analyser: two BNC leads from the stub, a source lead to strip 1
AX0, AX1, AY0, AY1, AH = 360.0, 550.0, 530.0, 660.0, 46.0
g = Geo([M['inst'], M['face'], M['nickel'], M['plastic'], M['disp']])
g.box(AX0, AY0, BENCH + 4, AX1, AY1, BENCH + AH, 0, 1.5); g.disc_y(AX1 - 22, AY0 - 0.5, BENCH + 25, 3.0, 1.0, 4)
za = BENCH + 25; IN = [AX0 + 60.0, AX0 + 90.0]; OUTX = AX0 + 18.0
for xi in IN + [OUTX]: g.disc_y(xi, AY0 - 5, za, 5.0, 10.0, 2)
for k, (ref, xi) in enumerate(zip(('J2', 'J3'), IN)):                      # MIX L, MIX R
    x0_, y0_, z0_, x1_, y1_, z1_ = wbox(stub['refs'][ref]); xc, zc = (x0_ + x1_) / 2, z0_ + (z1_ - z0_) * 0.55
    g.disc_y(xc, y1_ + 9, zc, 7.2, 22.0, 2); g.disc_y(xc, y1_ + 24, zc, 4.0, 10.0, 3)          # plug and its boot
    g.disc_y(xi, AY0 - 16, za, 7.2, 20.0, 2); g.disc_y(xi, AY0 - 30, za, 4.0, 10.0, 3)
    wire(f'BNC lead {ref}', [(xc, y1_ + 27, zc), (xc, y1_ + 42, zc - 2), ((xc + xi) / 2, (y1_ + AY0) / 2, BENCH + 6 + 5 * k),
                             (xi, AY0 - 46, za - 2), (xi, AY0 - 33, za)], 2.5, 'rubber_black', cables)
jx, jy = strip_in = next(p['feature'] for p in json.load(open(os.path.join(OUTDIR, 'strip.json')))[1]['parts'] if p['ref'] == 'J1')   # LINE IN
g.cyl(jx, jy, PANEL_Z1 + 1.0, PANEL_Z1 + 9.0, 6.0, 2, 24); g.cyl(jx, jy, PANEL_Z1 + 9.0, PANEL_Z1 + 42.0, 7.5, 3, 24)
g.cyl(jx, jy, PANEL_Z1 + 42.0, PANEL_Z1 + 54.0, 4.0, 3, 16)
g.disc_y(OUTX, AY0 - 16, za, 7.2, 20.0, 2); g.disc_y(OUTX, AY0 - 30, za, 4.0, 10.0, 3)
xr = -48.0; zc = BENCH + 2.7
wire('source lead to LINE IN 1', [(jx, jy, PANEL_Z1 + 52), (jx, jy, PANEL_Z1 + 66), (jx - 14, jy + 2, PANEL_Z1 + 78), (xr + 10, jy + 8, PANEL_Z1 + 60),
                                  (xr, jy + 22, zc + 30), (xr, jy + 45, zc + 6), (xr, jy + 60, zc), (xr, 200, zc), (xr, 350, zc), (xr, 384, zc + 6),
                                  (xr, 420, zc), (xr, 570, zc), (xr + 30, 604, zc), (150, 606, zc), (290, 606, zc), (330, 580, zc), (342, 520, zc),
                                  (OUTX - 20, AY0 - 62, zc + 14), (OUTX, AY0 - 46, za - 2), (OUTX, AY0 - 33, za)], 2.6, 'rubber_black', cables)
inst.objects.link(bpy.data.objects.new('analyser and plugs', g.mesh('analyser and plugs')))

# ---------------------------------------------------------------- labels, lying on the bench
labels = coll('labels', jig)
ZL = BENCH + 0.3
for s, x, y, z, size in (('ПЛАТА НАГРУЗКИ  120 × 85', sum(load['x']) / 2, load['y'][1] + 36, ZL, 13),
                         ('КАНАЛЫ 1–4  (панель 8 HP, плата 38 × 400 + плата гнёзд)', NS * PITCH / 2, panel_layout.RAIL_LINES[1] + 40, ZL, 13),
                         ('МАСТЕР-СТАБ  160 × 125', sum(stub['x']) / 2 + 175, sum(stub['y']) / 2, ZL, 13),
                         ('ШЛЕЙФ 34 ж., 0,6 м', (SX[-1] + tx) / 2, YB - 40, ZL, 11),
                         ('ШИНА ЗЕМЛИ  M4', (LUG[0] + LUG[-1]) / 2 + 14, BARY + 22, ZL, 11),
                         ('ПИТАНИЕ  ±17 В', (PX0 + PX1) / 2, (PY0 + PY1) / 2, BENCH + PH + 0.3, 15),
                         ('АНАЛИЗАТОР', (AX0 + AX1) / 2, (AY0 + AY1) / 2, BENCH + AH + 0.3, 15)):
    text('label ' + s.split('  ')[0], s, x, y, z, size, M['label'], labels)

# ---------------------------------------------------------------- lights, cameras, renders
exec(compile(_src[_r0:_src.index('def panels_visible')], os.path.join(HERE, 'console_3d.py'), 'exec'))   # world, setup, light, camera, shot
def J(x, y, z): return Vector((x * S, -y * S, z * S))
setup(scene)
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.02, 0.022, 0.026, 1)
mid = J(150, 310, -10)
light(scene, 'key', 'AREA', mid + Vector((-0.8, -0.9, 1.5)), mid, 90, 1.4)
light(scene, 'fill', 'AREA', mid + Vector((1.3, -0.5, 1.0)), mid, 40, 2.0)
light(scene, 'rim', 'AREA', mid + Vector((0.2, 1.3, 1.1)), mid, 45, 2.0)
cam = camera(scene, 'jig camera')
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUTDIR, 'jig.blend'))
print('saved jig.blend; ribbon', round(ribbon_len), 'mm; stub terminal entry', entry, '; boards', load['x'], load['y'], stub['x'], stub['y'])
if 'norender' not in ARGV[1:]:
    shot(scene, cam, 'jig.png', mid + Vector((-0.22, -1.02, 0.86)), mid + Vector((0.0, -0.02, -0.03)), lens=37, res=(2400, 1350))
    shot(scene, cam, 'jig_plan.png', J(150, 295, 2000), None, ortho=1.02, res=(2600, 2300), rot=(0, 0, 0))
    c = J(350, 350, -20)
    shot(scene, cam, 'jig_stub.png', c + Vector((-0.10, -0.42, 0.34)), c, lens=35, res=(2400, 1350))
    for e in panels: e.hide_render = True          # the same bench with the panels off
    c = J(120, 330, -15)
    shot(scene, cam, 'jig_open.png', c + Vector((-0.42, -0.62, 0.50)), c, lens=35, res=(2400, 1350))
    for e in panels: e.hide_render = False
    hidden = list(bench.objects) + list(labels.objects)                    # from below: the ribbon through the bus sockets, the ground wires
    for o in hidden: o.hide_render = True
    c = J(80, 325, -12); under = light(scene, 'under', 'AREA', c + Vector((0.0, -0.1, -0.7)), c, 40, 1.5)
    shot(scene, cam, 'jig_under.png', c + Vector((-0.16, -0.22, -0.26)), c, lens=35, res=(2400, 1350))
    under.hide_render = True
    for o in hidden: o.hide_render = False
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUTDIR, 'jig.blend'))
