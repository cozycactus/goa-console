"""STEP (AP214) writer for the part models: every facet a planar face with a poly-loop bound, one open shell per
material with its colour, in millimetres in KiCad's model frame (x right, y up, z up). KiCad's GLB/STEP board export
takes STEP only (--subst-models swaps a VRML for its STEP twin of the same name), so tools/models3d/check.py --wrl
writes both: the VRML for KiCad's 3D viewer, the STEP for mechanical export."""
import math
from collections import defaultdict
from .geom import MATERIALS, srgb, oriented


def _f(v):
    s = f'{v:.6g}'
    return s if ('.' in s or 'e' in s or 'E' in s) else s + '.'


def _newell(P):
    nx = ny = nz = 0.0
    for k in range(len(P)):
        a, b = P[k], P[(k + 1) % len(P)]
        nx += (a[1] - b[1]) * (a[2] + b[2]); ny += (a[2] - b[2]) * (a[0] + b[0]); nz += (a[0] - b[0]) * (a[1] + b[1])
    return nx, ny, nz


def clean(V, faces, mats, tol=1e-4):
    """Faces OCCT accepts (one bad facet makes it drop the whole model): points within tol welded, repeated and
    near-coincident consecutive points dropped, loops under 3 points or of no area left out, non-planar loops split
    into triangles. Returns (faces as index lists into V, materials)."""
    rep, seen = [], {}
    for i, p in enumerate(V): rep.append(seen.setdefault(tuple(round(c, 3) for c in p), i))
    near = lambda i, j: sum((V[i][k] - V[j][k]) ** 2 for k in range(3)) < tol * tol
    F, M = [], []
    for f, m in zip(faces, mats):
        loop = []
        for i in f:
            j = rep[i]
            if not (loop and near(j, loop[-1])): loop.append(j)
        while len(loop) > 1 and near(loop[0], loop[-1]): loop.pop()
        if len(loop) < 3: continue
        P = [V[i] for i in loop]; n = _newell(P); L = math.sqrt(sum(c * c for c in n))
        if L < 1e-9: continue
        d0 = sum(n[k] * P[0][k] for k in range(3)) / L
        if len(loop) > 3 and max(abs(sum(n[k] * p[k] for k in range(3)) / L - d0) for p in P) > 1e-3:
            for k in range(1, len(loop) - 1):                   # warped: fan into triangles
                t = [loop[0], loop[k], loop[k + 1]]; tn = _newell([V[i] for i in t])
                if sum(c * c for c in tn) > 1e-18: F.append(t); M.append(m)
        else:
            F.append(loop); M.append(m)
    return F, M


def write(mesh, path, title='part'):
    ents = []
    def e(text):
        ents.append(text); return f'#{len(ents)}'
    ctx = e("APPLICATION_CONTEXT('core data for automotive mechanical design processes')")
    e(f"APPLICATION_PROTOCOL_DEFINITION('international standard','automotive_design',2000,{ctx})")
    pc = e(f"PRODUCT_CONTEXT('',{ctx},'mechanical')")
    prod = e(f"PRODUCT('{title}','{title}','',({pc}))")
    pdf = e(f"PRODUCT_DEFINITION_FORMATION('','',{prod})")
    pdc = e(f"PRODUCT_DEFINITION_CONTEXT('part definition',{ctx},'design')")
    pd = e(f"PRODUCT_DEFINITION('design','',{pdf},{pdc})")
    pds = e(f"PRODUCT_DEFINITION_SHAPE('','',{pd})")
    lu = e("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
    au = e("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
    su = e("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
    unc = e(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-06),{lu},'distance_accuracy_value','confusion accuracy')")
    gc = e(f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT(({unc}))"
           f"GLOBAL_UNIT_ASSIGNED_CONTEXT(({lu},{au},{su}))REPRESENTATION_CONTEXT('','3D'))")
    o = e("CARTESIAN_POINT('',(0.,0.,0.))"); dz = e("DIRECTION('',(0.,0.,1.))"); dx = e("DIRECTION('',(1.,0.,0.))")
    origin = e(f"AXIS2_PLACEMENT_3D('',{o},{dz},{dx})")
    V = [(x, -y, z) for x, y, z in mesh.v]
    F, M = clean(V, mesh.f, mesh.m)
    pts = {i: e(f"CARTESIAN_POINT('',({_f(V[i][0])},{_f(V[i][1])},{_f(V[i][2])}))") for i in sorted({i for f in F for i in f})}
    groups = defaultdict(list)
    for f, m in zip(oriented(V, F), M): groups[m].append(f)
    shells, styles = [], []
    for m, faces in sorted(groups.items()):
        fs = []
        for f in faces:
            P = [V[i] for i in f]
            nx, ny, nz = _newell(P); L = math.sqrt(nx * nx + ny * ny + nz * nz)   # outwards (oriented())
            nx, ny, nz = nx / L, ny / L, nz / L
            rx, ry, rz = (P[1][0] - P[0][0], P[1][1] - P[0][1], P[1][2] - P[0][2])
            d = rx * nx + ry * ny + rz * nz; rx, ry, rz = rx - d * nx, ry - d * ny, rz - d * nz
            Lr = math.sqrt(rx * rx + ry * ry + rz * rz)
            if Lr < 1e-12: continue
            n = e(f"DIRECTION('',({_f(nx)},{_f(ny)},{_f(nz)}))"); r = e(f"DIRECTION('',({_f(rx / Lr)},{_f(ry / Lr)},{_f(rz / Lr)}))")
            pl = e(f"PLANE('',{e(f'AXIS2_PLACEMENT_3D({chr(39)}{chr(39)},{pts[f[0]]},{n},{r})')})")
            loop = e(f"POLY_LOOP('',({','.join(pts[i] for i in f)}))")
            fs.append(e(f"FACE_SURFACE('',({e(f'FACE_OUTER_BOUND({chr(39)}{chr(39)},{loop},.T.)')}),{pl},.T.)"))
        if not fs: continue
        sh = e(f"OPEN_SHELL('{m}',({','.join(fs)}))"); shells.append(sh)
        (cr, cg, cb), metal, rough = MATERIALS[m]; cr, cg, cb = srgb(cr), srgb(cg), srgb(cb)
        col = e(f"COLOUR_RGB('{m}',{_f(cr)},{_f(cg)},{_f(cb)})")
        fill = e(f"FILL_AREA_STYLE('',({e(f'FILL_AREA_STYLE_COLOUR({chr(39)}{chr(39)},{col})')}))")
        side = e(f"SURFACE_SIDE_STYLE('',({e(f'SURFACE_STYLE_FILL_AREA({fill})')}))")
        psa = e(f"PRESENTATION_STYLE_ASSIGNMENT(({e(f'SURFACE_STYLE_USAGE(.BOTH.,{side})')}))")
        styles.append((psa, sh))
    model = e(f"SHELL_BASED_SURFACE_MODEL('',({','.join(shells)}))")
    rep = e(f"MANIFOLD_SURFACE_SHAPE_REPRESENTATION('{title}',({origin},{model}),{gc})")
    e(f"SHAPE_DEFINITION_REPRESENTATION({pds},{rep})")
    si = [e(f"STYLED_ITEM('',({psa}),{sh})") for psa, sh in styles]
    e(f"MECHANICAL_DESIGN_GEOMETRIC_PRESENTATION_REPRESENTATION('',({','.join(si)}),{gc})")
    with open(path, 'w') as fh:
        fh.write("ISO-10303-21;\nHEADER;\nFILE_DESCRIPTION(('goa-console part model, tools/models3d'),'2;1');\n"
                 f"FILE_NAME('{title}','2026-10-23T00:00:00',(''),(''),'tools/models3d/step.py','','');\n"
                 "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 1 1 1 1 }'));\nENDSEC;\nDATA;\n")
        for k, t in enumerate(ents, 1): fh.write(f'#{k}={t};\n')
        fh.write('ENDSEC;\nEND-ISO-10303-21;\n')
