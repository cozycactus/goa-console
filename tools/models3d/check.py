"""Check the part models against their footprints and write the VRML models KiCad uses.
  python3 tools/models3d/check.py [--wrl]
For each modelled footprint: every through-hole pad has a lead from pins() within 0.25 mm and every lead lands on a
pad; the body below the panel stays inside the courtyard (reported with the overhang); the panel feature lies inside
the body outline. --wrl writes goa-console.3dshapes/<footprint>.wrl (KiCad's 3D viewer) and its .step twin (KiCad's
GLB/STEP export with --subst-models). --kicad then has kicad-cli load every STEP (a scratch board, GLB export): OCCT
drops a whole model on one bad facet. Exits non-zero on a pad mismatch or a model KiCad does not load."""
import json, math, os, struct, subprocess, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from models3d import registry, STACK, vrml, step
from models3d.pads import pads, path, PROJ
from verify import sexp

TOL = 0.25


def courtyard(fpid):
    """Bounding box (x0, y0, x1, y1) of the front courtyard, or None."""
    xs, ys = [], []
    for it in sexp(open(path(fpid)).read())[1:]:
        if not (isinstance(it, list) and it and it[0] in ('fp_line', 'fp_rect', 'fp_circle', 'fp_poly', 'fp_arc')): continue
        if not any(isinstance(x, list) and x[0] == 'layer' and x[1] == 'F.CrtYd' for x in it): continue
        for x in it:
            if isinstance(x, list) and x[0] in ('start', 'end', 'center', 'mid'):
                xs.append(float(x[1])); ys.append(float(x[2]))
            if isinstance(x, list) and x[0] == 'pts':
                for p in x[1:]: xs.append(float(p[1])); ys.append(float(p[2]))
        if it[0] == 'fp_circle':
            c = next(x for x in it if isinstance(x, list) and x[0] == 'center'); e = next(x for x in it if isinstance(x, list) and x[0] == 'end')
            r = math.hypot(float(e[1]) - float(c[1]), float(e[2]) - float(c[2]))
            xs += [float(c[1]) - r, float(c[1]) + r]; ys += [float(c[2]) - r, float(c[2]) + r]
    return (min(xs), min(ys), max(xs), max(ys)) if xs else None


def lib_of(fp):
    p = path(fp)
    return os.path.basename(os.path.dirname(p)).replace('.pretty', '')


def main():
    wrl = '--wrl' in sys.argv; bad = 0
    outdir = os.path.join(PROJ, 'goa-console.3dshapes')
    for fp, (mod, kw) in sorted(registry().items()):
        fpid = f'{lib_of(fp)}:{fp}'
        th = [(n, x, y) for n, k, x, y, *_ in pads(fpid) if k == 'thru_hole']
        leads = mod.pins(**kw)
        miss = [f'{n or "tab"}@({x:g},{y:g})' for n, x, y in th if not any(math.hypot(x - a, y - b) <= TOL for a, b in leads)]
        extra = [f'({a:g},{b:g})' for a, b in leads if not any(math.hypot(x - a, y - b) <= TOL for n, x, y in th)]
        m = mod.build(**kw); top = STACK['jack_z0' if mod.MOUNT == 'jack' else 'panel_z0']
        body = [(x, y) for x, y, z in m.v if 0.05 < z < top - 0.05]
        bx0, by0 = min(p[0] for p in body), min(p[1] for p in body); bx1, by1 = max(p[0] for p in body), max(p[1] for p in body)
        cy = courtyard(fpid); over = ''
        if cy:
            o = max(cy[0] - bx0, cy[1] - by0, bx1 - cy[2], by1 - cy[3])
            over = f'courtyard {cy[0]:g},{cy[1]:g} .. {cy[2]:g},{cy[3]:g}; body {bx0:.2f},{by0:.2f} .. {bx1:.2f},{by1:.2f}' + (f'  OVERHANG {o:.2f} mm' if o > TOL else '')
        feat = ''
        if mod.FEATURE and not (bx0 <= mod.FEATURE[0] <= bx1 and by0 <= mod.FEATURE[1] <= by1): feat = '  FEATURE OUTSIDE BODY'
        (mx0, my0, mz0), (mx1, my1, mz1) = m.bounds()
        status = 'ok' if not (miss or extra) else 'PAD MISMATCH'
        bad += bool(miss or extra)
        print(f'{fp} {kw or ""}: {status}; {len(th)} pads, {len(leads)} leads; height {mz1:.2f} mm; {len(m.f)} faces')
        if miss: print('   pads without a lead:', ' '.join(miss))
        if extra: print('   leads without a pad:', ' '.join(extra))
        if over: print('   ' + over + feat)
        if wrl:
            os.makedirs(outdir, exist_ok=True)
            vrml.write(m, os.path.join(outdir, fp + '.wrl'), mod.NAME)
            step.write(m, os.path.join(outdir, fp + '.step'), fp)
    if wrl: print('wrote', outdir)
    if '--kicad' in sys.argv: bad += kicad_loads(outdir)
    sys.exit(1 if bad else 0)


def kicad_loads(outdir, kc=os.environ.get('KICAD_CLI', '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli')):
    steps = sorted(f for f in os.listdir(outdir) if f.endswith('.step'))
    with tempfile.TemporaryDirectory() as d:
        fps = ''.join(f'  (footprint "t:{f[:-5]}" (layer "F.Cu") (at {20 + 40 * k} 50) (model "{os.path.join(outdir, f)}"))\n'
                      for k, f in enumerate(steps))
        open(os.path.join(d, 't.kicad_pcb'), 'w').write(
            '(kicad_pcb (version 20240108) (generator "check")\n  (general (thickness 1.6))\n'
            '  (layers (0 "F.Cu" signal) (31 "B.Cu" signal) (44 "Edge.Cuts" user))\n'
            f'  (gr_rect (start 0 0) (end {40 * len(steps) + 20} 100) (layer "Edge.Cuts") (stroke (width 0.1) (type solid)))\n'
            + fps + ')\n')
        r = subprocess.run([kc, 'pcb', 'export', 'glb', '--force', '-o', os.path.join(d, 't.glb'), os.path.join(d, 't.kicad_pcb')],
                           capture_output=True, text=True)
        g = open(os.path.join(d, 't.glb'), 'rb').read(); n = struct.unpack('<I', g[12:16])[0]
        names = {nd.get('name') for nd in json.loads(g[20:20 + n])['nodes']}
    missing = [f for f in steps if f[:-5] not in names or f[:-5] in r.stdout + r.stderr and 'without geometry' in r.stdout + r.stderr]
    print(f'KiCad loads {len(steps) - len(missing)} / {len(steps)} STEP models' + (': MISSING ' + ' '.join(missing) if missing else ''))
    return len(missing)


if __name__ == '__main__':
    main()
