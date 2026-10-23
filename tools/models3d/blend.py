"""Blender adapter for the part models: Mesh (footprint mm, y down) -> bpy mesh in metres with Blender Y = -y, one
material per MATERIALS entry, smooth shading with edges sharper than 35 degrees kept sharp."""
import math
import bpy, bmesh
from .geom import MATERIALS

S = 0.001


def material(name):
    m = bpy.data.materials.get('part ' + name)
    if m: return m
    rgb, metal, rough = MATERIALS[name]
    m = bpy.data.materials.new('part ' + name); m.use_nodes = True
    p = m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = (*rgb, 1); p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = rough
    m.diffuse_color = (*rgb, 1)
    return m


def to_mesh(mesh, name, smooth_angle=35.0):
    names = sorted(set(mesh.m)); idx = {n: i for i, n in enumerate(names)}
    me = bpy.data.meshes.new(name)
    me.from_pydata([(x * S, -y * S, z * S) for x, y, z in mesh.v], [], [list(f) for f in mesh.f])
    for n in names: me.materials.append(material(n))
    me.polygons.foreach_set('material_index', [idx[m] for m in mesh.m])
    me.validate(clean_customdata=False)
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    me.shade_smooth(); me.set_sharp_from_angle(angle=math.radians(smooth_angle))
    return me
