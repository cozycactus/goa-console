"""VRML 2.0 writer for KiCad 3D models: 1 unit = 0.1 in (2.54 mm), KiCad model frame x right, y up, z up."""
from collections import defaultdict
from .geom import MATERIALS, srgb, oriented


def write(mesh, path, title=''):
    groups = defaultdict(list)                     # faces wound outwards in KiCad's frame (y up: a mirror of ours)
    for f, m in zip(oriented([(x, -y, z) for x, y, z in mesh.v], mesh.f), mesh.m): groups[m].append(f)
    out = ['#VRML V2.0 utf8', f'# {title} - goa-console part model (tools/models3d), 1 unit = 0.1 in']
    for m, faces in sorted(groups.items()):
        used = sorted({i for f in faces for i in f}); remap = {i: k for k, i in enumerate(used)}
        (r, g, b), metal, rough = MATERIALS[m]; r, g, b = srgb(r), srgb(g), srgb(b)
        spec = (r, g, b) if metal else (0.15, 0.15, 0.15)
        out.append('Shape {')
        out.append(f' appearance Appearance {{ material Material {{ diffuseColor {r:.3f} {g:.3f} {b:.3f} '
                   f'specularColor {spec[0]:.3f} {spec[1]:.3f} {spec[2]:.3f} shininess {max(0.05, 1 - rough):.2f} '
                   f'ambientIntensity 0.3 }} }}')
        out.append(' geometry IndexedFaceSet { solid FALSE creaseAngle 0.6')
        pts = [mesh.v[i] for i in used]
        out.append('  coord Coordinate { point [ ' + ', '.join(f'{x / 2.54:.5f} {-y / 2.54:.5f} {z / 2.54:.5f}' for x, y, z in pts) + ' ] }')
        out.append('  coordIndex [ ' + ' '.join(' '.join(str(remap[i]) for i in f) + ' -1' for f in faces) + ' ]')
        out.append(' }')
        out.append('}')
    with open(path, 'w') as fh: fh.write('\n'.join(out) + '\n')
