"""Render each part model for review, in Blender (headless):
  /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python tools/models3d/preview.py -- render/parts [module ...]
Per footprint: the part on a 1.6 mm board slab with its pads (copper rings at the footprint's pad positions), the
panel plate (translucent) at its stack height and the panel piece (knob, cap, nut, flange, fader knob) on the panel
feature. Writes <out>/<footprint>_{iso,front,side,bottom}.png; front looks along +y (footprint frame), side along -x,
bottom from below (leads through their pads). A 1 mm grid on the slab gives the scale."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import bpy
from mathutils import Vector
from models3d import registry, STACK
from models3d.geom import Mesh
from models3d.blend import to_mesh, S
from models3d.pads import pads
from models3d.check import lib_of

ARGV = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['render/parts']
OUT = os.path.abspath(ARGV[0]); ONLY = set(ARGV[1:])
os.makedirs(OUT, exist_ok=True)


def mat(name, rgb, alpha=1.0, metal=0.0, rough=0.5):
    m = bpy.data.materials.new(name); m.use_nodes = True; p = m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = (*rgb, 1); p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = rough; p.inputs['Alpha'].default_value = alpha
    if alpha < 1:
        try: m.surface_render_method = 'BLENDED'
        except AttributeError: m.blend_method = 'BLEND'
    return m


def obj(name, me, loc=(0, 0, 0)):
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o); o.location = loc; return o


def aim(o, target):
    o.rotation_euler = (Vector(target) - o.location).to_track_quat('-Z', 'Y').to_euler()


def scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    for eng in ('BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT'):
        try: sc.render.engine = eng; break
        except TypeError: pass
    sc.view_settings.view_transform = 'AgX'
    w = bpy.data.worlds.new('w'); w.use_nodes = True
    w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.55, 0.57, 0.6, 1)
    w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.35
    sc.world = w
    sc.render.resolution_x, sc.render.resolution_y = 1200, 900
    sc.render.film_transparent = False
    return sc


def build_part(fp, mod, kw):
    sc = scene()
    m = mod.build(**kw); (x0, y0, z0), (x1, y1, z1) = m.bounds()
    obj('part', to_mesh(m, fp))
    top = STACK['jack_z0' if mod.MOUNT == 'jack' else 'panel_z0']; pt = STACK['panel_t']
    fr4 = mat('FR4', (0.05, 0.25, 0.1), rough=0.4); cu = mat('pad', (0.8, 0.55, 0.3), metal=1, rough=0.3)
    grid = mat('grid', (0.6, 0.65, 0.6)); al = mat('panel', (0.75, 0.77, 0.8), alpha=0.28, metal=0.6, rough=0.3)
    pad = 3.0
    slab = Mesh().box(x0 - pad, y0 - pad, -1.6, x1 + pad, y1 + pad, 0, 'plastic_green')
    me = to_mesh(slab, 'slab'); me.materials.clear(); me.materials.append(fr4); obj('board', me)
    ring = Mesh()
    for n, k, px, py, sx, sy, d in pads(f'{lib_of(fp)}:{fp}'):
        if k == 'thru_hole':
            ring.tube(px, py, 0.0, 0.035, max(sx, sy) / 2, d / 2, 'metal_gold', 24)
            ring.tube(px, py, -1.635, -1.6, max(sx, sy) / 2, d / 2, 'metal_gold', 24)
        elif k == 'np_thru_hole':
            ring.tube(px, py, -1.6, 0.0, d / 2 + 0.05, d / 2, 'plastic_black', 24)
    if ring.v:
        me = to_mesh(ring, 'pads'); me.materials.clear(); me.materials.append(cu); obj('pads', me)
    g = Mesh()                                          # 1 mm grid lines along the slab edge (front)
    for k in range(int(x0 - pad), int(x1 + pad) + 1):
        L = 1.2 if k % 5 else 2.4
        g.box(k - 0.04, y1 + pad - L, 0.0, k + 0.04, y1 + pad, 0.02, 'print_white')
    me = to_mesh(g, 'grid'); me.materials.clear(); me.materials.append(grid); obj('grid', me)
    if mod.FEATURE:
        fx, fy = mod.FEATURE
        plate = Mesh().box(x0 - pad, y0 - pad, top, x1 + pad, y1 + pad, top + pt, 'metal_alu')
        me = to_mesh(plate, 'panel'); me.materials.clear(); me.materials.append(al); obj('panel', me)
        pm = mod.panel(**kw)
        if pm: obj('panel part', to_mesh(pm, fp + ' panel'), (fx * S, -fy * S, (top + pt) * S))
    return sc, (x0, y0, z0), (x1, y1, max(z1, top + pt + 16))


def light(name, loc, target, energy, size):
    ld = bpy.data.lights.new(name, 'AREA'); ld.energy = energy; ld.size = size
    o = bpy.data.objects.new(name, ld); bpy.context.scene.collection.objects.link(o); o.location = loc; aim(o, target)


def render(sc, fp, lo, hi):
    c = Vector(((lo[0] + hi[0]) / 2 * S, -(lo[1] + hi[1]) / 2 * S, (lo[2] + hi[2]) / 2 * S))
    span = max(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]) * S
    light('key', c + Vector((-1.5, -2, 2.5)) * span, c, 140 * span * span, span * 2)
    light('fill', c + Vector((2, -1, 0.5)) * span, c, 50 * span * span, span * 2)
    light('under', c + Vector((0.5, 1, -2)) * span, c, 60 * span * span, span * 2)
    cd = bpy.data.cameras.new('cam'); cd.clip_start = span * 0.01; cd.clip_end = span * 50
    cam = bpy.data.objects.new('cam', cd); sc.collection.objects.link(cam); sc.camera = cam
    w, h = (hi[0] - lo[0]) * S, (hi[1] - lo[1]) * S; z = (hi[2] - lo[2]) * S
    views = {'iso': (c + Vector((-1.1, -1.6, 1.2)) * span * 1.15, None),
             'front': (c + Vector((0, -3 * span, 0)), max(w, z) * 1.25),
             'side': (c + Vector((-3 * span, 0, 0)), max(h, z) * 1.25),
             'bottom': (c + Vector((0, 0, -3 * span)), max(w, h) * 1.3)}
    for name, (loc, ortho) in views.items():
        cam.location = loc
        if name == 'bottom': cam.rotation_euler = (math.pi, 0, 0)
        else: aim(cam, c)
        if ortho: cd.type = 'ORTHO'; cd.ortho_scale = ortho
        else: cd.type = 'PERSP'; cd.lens = 50
        sc.render.filepath = os.path.join(OUT, f'{fp}_{name}.png')
        bpy.ops.render.render(write_still=True)
        print('rendered', sc.render.filepath)


for fp, (mod, kw) in sorted(registry().items()):
    if ONLY and mod.__name__.split('.')[-1] not in ONLY and fp not in ONLY: continue
    sc, lo, hi = build_part(fp, mod, kw)
    render(sc, fp, lo, hi)
