"""Ground-and-hum study (2026-10-25): the heavy-ground harness, magnetic loop pickup, LED / logic return currents and
synth ground loops, each referred to main L and set against the console's noise floor. Report: docs/studies/ground_study.md.

usage: python3 sim/review/ground/ground_study.py [geom|gauge|mag|led|synth|all]   (default all)
Results are also written to sim/review/ground/results.json.

Model:
- Geometry from the 3D build (tools/console_3d.py, render/*.json): modules at 40.64 mm pitch, 12 strips, G1, G2,
  master (2 pitches), G3, G4, 12 strips; each strip / group's spade tab (Keystone 1287) at (5.0, 358.0), tip 10.2 mm
  under its board; bus header at (31.46, 345.64), the ribbon ~9 mm under the boards; the master's M4 star stud at
  (39.3, 214.0), its bus headers at x 5.5 / 72.0. Two harness routes:
    'tub'    as drawn in the 3D model: down to the tub floor (z -41), along it to the star's y, across to the star;
    'ribbon' each spade wire tied under the motherloom (3.5 mm below it) to the master's header, then along the master
             board's underside to the star.
  The ground loop of a module = its spade wire out, the ribbon's ground conductors (pins 2-16) and the master board
  back; its vector area (m^2) gives the flux of a uniform field.
- Ground currents and induced EMFs go through the whole-console deck of tools/sim_console.py (24 strips + 4 groups +
  master from the netlists, the ribbon segment by segment), with each module's spade wire as R + L from its length.
- The synth receiver (strip U1A: R6-R9 10K 0.1 %, C7 / C78 33p, R10 1M, C8 / C9 100p) is solved exactly (ideal op-amp)
  for the Monte Carlo over resistor tolerance; the shield / ground-loop network around it is solved in closed form.
- Noise floor: main L, 20 Hz-20 kHz, 24 strips routed -79 dBu (sim_console t_noise); target: every source <= -89 dBu.
  The single-strip floor (-91 dBu) is quoted too."""
import os, sys, math, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'tools'))
import sim_console as sc

FLOOR, TARGET, FLOOR1 = -79.0, -89.0, -91.0
RES = os.path.join(HERE, 'results.json')
out = json.load(open(RES)) if os.path.exists(RES) else {}

# ---------------------------------------------------------------- geometry
PITCH, ZB = 40.64, -1.6                   # module pitch; board underside (boards' top at z 0)
SPADE, HDR, Z_TAB, Z_RIB = (5.0, 358.0), (31.46, 345.64), ZB - 10.2, ZB - 9.0
STAR, MHDR = (14 * PITCH + 39.3, 214.0), {'L': 14 * PITCH + 5.5, 'R': 14 * PITCH + 72.0}
Z_FLOOR = -41.0
AWG = {18: 0.0210, 16: 0.0132, 14: 0.00828, 12: 0.00521}       # ohm / m, stranded copper
R_WIRE = {18: 0.51e-3, 16: 0.65e-3, 14: 0.82e-3, 12: 1.03e-3}  # conductor radius, m
SLACK = 0.06                              # receptacle, ring lug and dressing, m

def modules():
    """[(sim name, wing, x of the module's left edge)], in the sim's chain order (nearest the master first)."""
    L = ['g1', 'g2'] + [f's{i:02d}' for i in range(1, 13)]
    R = ['g3', 'g4'] + [f's{i:02d}' for i in range(13, 25)]
    return [(n, 'L', (13 - k) * PITCH) for k, n in enumerate(L)] + [(n, 'R', (16 + k) * PITCH) for k, n in enumerate(R)]

def paths(wing, x, route):
    """(spade wire polyline, return polyline) in mm; the wire runs tab -> star, the return star -> tab."""
    tx, ty = x + SPADE[0], SPADE[1]; sx, sy = STAR; hx = MHDR[wing]; side = -1 if tx < sx else 1
    if route == 'tub':
        wire = [(tx, ty, Z_TAB), (tx, ty, Z_FLOOR), (tx, sy, Z_FLOOR), (sx + side * 25, sy, Z_FLOOR),
                (sx + side * 8, sy, Z_FLOOR), (sx, sy, ZB - 5.0), (sx, sy, ZB)]
    else:
        zr = Z_RIB - 3.5
        wire = [(tx, ty, Z_TAB), (tx, ty, zr), (tx, HDR[1] + 4, zr), (hx, HDR[1] + 4, zr), (hx, HDR[1] + 4, ZB - 3.5),
                (sx, sy, ZB - 3.5), (sx, sy, ZB)]
    ret = [(sx, sy, ZB), (hx, HDR[1], ZB), (hx, HDR[1], Z_RIB), (x + HDR[0], HDR[1], Z_RIB), (x + HDR[0], HDR[1], ZB),
           (tx, ty, ZB), (tx, ty, Z_TAB)]
    return wire, ret

def length(p): return sum(math.dist(a, b) for a, b in zip(p, p[1:])) / 1000.0
def area(p):
    """Vector area (m^2) of the closed polygon p (mm), right-hand rule along p."""
    a = np.zeros(3)
    for i in range(len(p)): a += np.cross(p[i], p[(i + 1) % len(p)])
    return a / 2 * 1e-6

def wire_l(l, awg):
    """Partial self-inductance of a straight round wire, H (Rosa)."""
    r = R_WIRE[awg]; return 2e-7 * l * (math.log(2 * l / r) - 0.75)

def geometry():
    g = {}
    for route in ('tub', 'ribbon'):
        for n, wing, x in modules():
            w, r = paths(wing, x, route)
            g[f'{route}:{n}'] = dict(len=length(w) + SLACK, area=list(area(w + r[1:-1])))
    return g

def spade(route, awg, g):
    d = {}
    for n, _, _ in modules():
        l = g[f'{route}:{n}']['len']; d[n] = (AWG[awg] * l, wire_l(l, awg))
    return d

def t_geom():
    g = geometry(); out['geom'] = g
    print('module  route   wire m   |A| cm^2   Ax / Ay / Az cm^2')
    for route in ('tub', 'ribbon'):
        for n in ('g1', 'g2', 's01', 's06', 's12', 'g3', 's24'):
            e = g[f'{route}:{n}']; a = np.array(e['area']) * 1e4
            print(f'{n:6s}  {route:6s}  {e["len"]:6.3f}  {np.linalg.norm(a):9.1f}   {a[0]:7.1f} {a[1]:7.1f} {a[2]:7.1f}')
        ls = [g[f'{route}:{n}']['len'] for n, _, _ in modules()]
        print(f'        {route}: total wire {sum(ls):.1f} m, longest {max(ls):.2f} m')
    return g

# ---------------------------------------------------------------- console runs
CASES = [('as modelled (0.3 m, 18 AWG)', None, None)] + [(f'{r} route, {a} AWG', r, a) for r in ('tub', 'ribbon') for a in (18, 16, 14)] + [('ribbon route, 12 AWG', 'ribbon', 12)]
PROBE = ['s12', 's06', 's01', 'g1', 's24']
STRIPS = [m for m in PROBE if m[0] == 's']

def deck(sp, **kw):
    s, g, m = sc.default_console(); return sc.console(s, g, m, spade=sp, **kw)

def transfer(sp, mod, freqs=(50, 1000, 10000)):
    """Main L (V) and the module's ground (V) per A into its ground, at each frequency."""
    ctl = []
    for f in freqs:
        ctl += [f'ac lin 1 {f} {f}', f'let ml{f} = mag({sc.diff(sc.XLR["L"])})', f'print ml{f}',
                f'let vg{f} = mag(v({mod}_G))', f'print vg{f}']
    r, _ = sc.run(deck(sp, gnd_inject=[(mod, 1.0)]), ctl)
    return {f: (r[f'ml{f}'], r[f'vg{f}']) for f in freqs}

def dbu(v): return 20 * math.log10(max(v, 1e-30) / sc.SRC)

def t_gauge():
    """Each harness case: per module, main L per A into its ground; and the 1 mA-per-module common case."""
    g = out.get('geom') or geometry()
    res = {}
    print(f'{"case":28s} ' + ' '.join(f'{m:>14s}' for m in PROBE) + '   all@1mA   (main L mOhm at 50 Hz / 10 kHz; dBu)')
    for label, route, awg in CASES:
        sp = spade(route, awg, g) if route else None
        tr = {m: transfer(sp, m) for m in PROBE}
        s, gg, mm = sc.default_console()
        r, _ = sc.run(sc.console(s, gg, mm, spade=sp, gnd_inject=[(x.name, 1e-3) for x in s + gg]),
                      ['ac lin 1 50 50', f'let ml = mag({sc.diff(sc.XLR["L"])})', 'print ml'])
        res[label] = dict(tr={m: {str(f): v for f, v in t.items()} for m, t in tr.items()}, common=r['ml'])
        print(f'{label:28s} ' + ' '.join(f'{tr[m][50][0] * 1e3:6.2f}/{tr[m][10000][0] * 1e3:6.2f}' for m in PROBE)
              + f'   {dbu(r["ml"]):6.1f}')
    out['gauge'] = res
    return res

def t_mag():
    """Uniform 50 / 150 Hz field through every module's ground loop: main L per uT."""
    g = out.get('geom') or geometry()
    res = {}
    print('main L for 1 uT (dBu); 10 uT is +20 dB')
    for label, route, awg in CASES[1:]:
        sp = spade(route, awg, g); row = {}
        for pat in ('x', 'y', 'z', 'aligned'):
            for f in (50, 150):
                w = 2 * math.pi * f * 1e-6
                emf = {}
                for n, _, _ in modules():
                    a = np.array(g[f'{route}:{n}']['area'])
                    emf[n] = w * (np.linalg.norm(a) if pat == 'aligned' else a['xyz'.index(pat)])
                r, _ = sc.run(deck(sp, spade_emf=emf), [f'ac lin 1 {f} {f}', f'let ml = mag({sc.diff(sc.XLR["L"])})', 'print ml',
                                                        'let vg = mag(v(s12_G))', 'print vg'])
                row[f'{pat}{f}'] = r['ml']
        res[label] = row
        print(f'{label:24s} ' + '  '.join(f'{p}: {dbu(row[p + "50"]):6.1f}/{dbu(row[p + "150"]):6.1f}' for p in ('x', 'y', 'z', 'aligned')))
    out['mag'] = res
    return res

# ---------------------------------------------------------------- LED and logic returns
def led_current(vf):
    """A strip / group LED: +VL (17 V less R3's 10R drop) through 4K7."""
    return (16.9 - vf) / 4.7e3

def t_led():
    """Key LEDs return to GNDD, which joins GNDA at NT1: each key press is a current step into the module's ground,
    supplied from +VBUS through R3 / C5 (470 us). Steps referred to main L through the worst module's transfer."""
    gres = out.get('gauge') or t_gauge()
    i1 = led_current(2.0)
    events = [('one key LED (ON, PFL, EQ, routing; group AFL)', i1), ('two keys at once', 2 * i1),
              ('OL LED flashing with programme', led_current(1.9))]
    res = {}
    for label in (CASES[0][0], 'tub route, 18 AWG', 'ribbon route, 14 AWG'):
        tr = gres[label]['tr']
        worst = max(PROBE, key=lambda m: tr[m]['50'][0])
        z50, z1k = tr[worst]['50'][0], tr[worst]['1000'][0]
        row = {e: dbu(i * max(z50, z1k)) for e, i in events}
        res[label] = dict(worst=worst, **row)
        print(f'{label:28s} worst {worst}: ' + '; '.join(f'{e}: {v:.1f} dBu' for e, v in row.items()))
    res['events'] = {e: i for e, i in events}
    out['led'] = res
    return res

# ---------------------------------------------------------------- synth ground loops: the receiver
F = 50.0
def receiver(r6, r7, r8, r9, zt, zr, f=F, zcm=None):
    """Strip input receiver U1A (ideal op-amp), SW15 normal: tip to the inverting leg (R6 / R7 + C7), ring to the
    non-inverting leg (R8 / R9 + C78). zt, zr: source impedances of the tip and ring legs. zcm: input buffers with this
    bias resistance (to GNDA) in front of the receiver instead. Returns (differential gain, common-mode gain)."""
    w = 2j * math.pi * f
    z7 = 1 / (1 / r7 + w * 33e-12); z9 = 1 / (1 / r9 + w * 33e-12)
    def resp(vt, vr):
        if zcm is not None:                      # followers: each leg sees its bias R || 100 pF, then a stiff drive
            yb = 1 / zcm + w * 100e-12
            vt = vt / (1 + zt * yb); vr = vr / (1 + zr * yb); zt_, zr_ = 0.0, 0.0
        else:
            zt_, zr_ = zt, zr
        yrl = 1 / (r8 + z9) + w * 100e-12        # ring node: R8 + Z9, C9
        v_r = vr / (1 + zr_ * yrl)
        vp = v_r * z9 / (r8 + z9)
        # tip node: source, C8, R10 1M, R6 to the summing node at vp
        v_t = (vt / zt_ + vp / r6) / (1 / zt_ + w * 100e-12 + 1e-6 + 1 / r6) if zt_ else vt
        return vp - z7 * (v_t - vp) / r6
    return resp(1, 0), resp(1, 1)

def mc(tol, zt, zr, n=4000, seed=1, zcm=None):
    """CMRR (dB, |dm / cm|) over n draws of R6-R9 uniform within +-tol; returns (median, 5th percentile = worst 5 %)."""
    rng = np.random.default_rng(seed); c = []
    for _ in range(n):
        r = 10e3 * (1 + rng.uniform(-tol, tol, 4))
        dm, cm = receiver(*r, zt, zr, zcm=zcm); c.append(20 * math.log10(abs(dm) / abs(cm)))
    c = np.array(c); return float(np.median(c)), float(np.percentile(c, 5))

R_EARTH, R_SH, R_RING, R_LINK, R_CH = 0.2, 0.05, 0.05, 0.010, 0.010
STRIP_GAIN = 10 ** (sc.UNITY / 20)       # strip input to main L at the detents, pan centre

def loop(vgl, cable, sleeve, zsrc, zg, tmain, cmrr_db, rg=10.0):
    """One earthed synth on one strip. vgl: earth potential difference (V) between the synth and the console's star,
    through R_EARTH; cable 'ts' (ring shorted to sleeve at the plug) or 'trs' (pseudo-balanced: ring to the synth's
    ground at the far end); sleeve 'gnda' (as built), 'chassis' (panel / frame to the star) or 'rg' (GNDA via rg).
    zg: strip ground to star (ohm), tmain: main L per A into the strip ground. Returns main L (V): receiver part,
    ground-injection part, total (in-phase sum)."""
    r_gnda = {'gnda': R_LINK, 'chassis': R_CH, 'rg': rg + R_LINK}[sleeve]   # jack sleeve to the receiver's GNDA
    i = vgl / (R_EARTH + R_SH + r_gnda + (0.0 if sleeve == 'chassis' else zg))
    v_sg = i * (R_SH + r_gnda)                  # the synth's ground, relative to the strip GNDA at the receiver
    v_js = v_sg - i * R_SH                      # the jack sleeve
    cmr = 10 ** (-cmrr_db / 20)
    v_dm, v_cm = (v_sg - v_js, v_js) if cable == 'ts' else (0.0, v_sg)
    v_rx = abs(v_dm) + abs(v_cm) * cmr
    inj = 0.0 if sleeve == 'chassis' else i * tmain
    return v_rx * STRIP_GAIN, inj, v_rx * STRIP_GAIN + inj

def t_synth():
    gres = out.get('gauge') or t_gauge()
    res = {'cmrr': {}, 'loops': {}}
    print('receiver CMRR at 50 Hz (dB): median / worst 5 % over R6-R9 tolerance')
    for zcm_label, zcm in (('as built (20K CM per leg)', None), ('buffered, 1M bias', 1e6)):
        for tol in (0.001, 0.01):
            for zs in (0.0, 50.0, 100.0, 1000.0):
                med, w5 = mc(tol, zs, R_RING if zs else 0.0, zcm=zcm, n=2000 if zcm else 4000)
                res['cmrr'][f'{zcm_label}|{tol}|{zs}'] = (med, w5)
                print(f'  {zcm_label:26s} tol {tol * 100:4.1f} %  source {zs:6.0f} ohm: {med:6.1f} / {w5:6.1f}')
    for label in (CASES[0][0], 'tub route, 18 AWG', 'ribbon route, 14 AWG'):
        tr = gres[label]['tr']; worst = max(STRIPS, key=lambda m: tr[m]['50'][0])
        tmain, zg = tr[worst]['50']
        rows = {}
        for rx in ('as built (20K CM per leg)', 'buffered, 1M bias'):
            for zs in (100.0, 1000.0):
                cm = res['cmrr'][f'{rx}|0.001|{zs}'][1]
                for cable in ('ts', 'trs'):
                    for sleeve in ('gnda', 'chassis', 'rg'):
                        for vgl in (0.01, 0.1, 1.0):
                            rx_, inj, tot = loop(vgl, cable, sleeve, zs, zg, tmain, cm)
                            rows[f'{rx}|{zs}|{cable}|{sleeve}|{vgl}'] = (dbu(rx_), dbu(inj) if inj else None, dbu(tot))
        res['loops'][label] = dict(worst=worst, zg=zg, tmain=tmain, rows=rows)
    lab = 'ribbon route, 14 AWG'; L = res['loops'][lab]
    print(f'\nmain L (dBu) for an earthed synth on {L["worst"]} ({lab}: strip ground {L["zg"] * 1e3:.2f} mOhm, '
          f'{L["tmain"] * 1e3:.2f} mOhm to main L); source 1K, 0.1 % resistors, worst 5 %; Vgl 10 mV / 100 mV / 1 V')
    for rx in ('as built (20K CM per leg)', 'buffered, 1M bias'):
        for cable in ('ts', 'trs'):
            for sleeve in ('gnda', 'chassis', 'rg'):
                v = [L['rows'][f'{rx}|1000.0|{cable}|{sleeve}|{g}'][2] for g in (0.01, 0.1, 1.0)]
                print(f'  {rx:26s} {cable:3s} sleeve {sleeve:7s}: ' + ' / '.join(f'{x:6.1f}' for x in v))
    out['synth'] = res
    return res

# ---------------------------------------------------------------- two-cable loop (stereo synth on two strips)
def t_stereo():
    """A stereo synth on two strips: synth ground -> cable A shield -> strip A -> console ground -> strip B -> cable B
    shield. Driven by the field through the loop the two cables enclose (3 m cables, 0.1 m / 0.5 m apart)."""
    res = {}
    for sep in (0.0, 0.1, 0.5):
        for b in (1e-6, 10e-6):
            a = 3.0 * sep; emf = 2 * math.pi * 50 * b * a
            i = emf / (2 * R_SH + 2 * R_LINK + 0.004)
            res[f'{sep}|{b}'] = dict(ts=dbu(i * R_SH * STRIP_GAIN), trs=dbu(i * R_SH * 10 ** (-26 / 20) * STRIP_GAIN))
            print(f'  cables {sep * 100:3.0f} cm apart, {b * 1e6:4.0f} uT: TS {res[f"{sep}|{b}"]["ts"]:7.1f} dBu, '
                  f'pseudo-balanced {res[f"{sep}|{b}"]["trs"]:7.1f} dBu per strip at main L')
    out['stereo'] = res
    return res

STEPS = dict(geom=t_geom, gauge=t_gauge, mag=t_mag, led=t_led, synth=t_synth, stereo=t_stereo)
if __name__ == '__main__':
    for name in sys.argv[1:] or ['all']:
        for n, f in (STEPS.items() if name == 'all' else [(name, STEPS[name])]):
            print(f'== {n}', flush=True); f()
            json.dump(out, open(RES, 'w'), indent=1)
