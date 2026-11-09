"""Sweepable HPF study for the strip (proposal docs/proposals/hpf_proposal.md): a state-variable (KHN) high-pass, unity gain,
non-inverting, Q 0.707, tuned by an A10K dual as the mid bands are (strip spec 6.2): each gang a divider from the
driving op-amp (pin 3) to R0 (pin 1), RT from top to wiper, wiper -> RB -> integrator.
Summer: + input from the signal (RIN) and BP (RBP), - input from LP (RLP) and HP (RF); RF = 2 RLP, RIN = 2 RBP gives
H = s^2 / (s^2 + s w0/Q + w0^2) with gain 1 and Q 1/sqrt(2), w0 = sqrt(2) / tau.
usage: python3 khn_hpf.py [law | resp | mismatch | noise | stab]   (stab needs TI_MODELS with OPA161x.LIB)"""
import os, re, sys, math, subprocess, tempfile
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'master'))

V = dict(R0=330, RT=13e3, RB=5.6e3, C=100e-9, RF=4.99e3, RLP=2.49e3, RIN=4.99e3, RBP=2.49e3, POT=10e3,
         CF=10e-12, CP=22e-12)          # CF across RF, CP from the summer's + input to ground (stability)
alaw = lambda x: 0.30 * x if x <= 0.5 else 0.15 + 1.70 * (x - 0.5)
K4T = 1.656e-20

def law(th, v=V):
    """Analytic f0 of the tuned SVF at rotation th (0 = CCW = lowest frequency)."""
    x = alaw(th); ru = v['POT'] * (1 - x) + 1e-3; rl = v['POT'] * x + v['R0']
    rup = 1 / (1 / ru + 1 / v['RT'])
    vw = (1 / rup) / (1 / rup + 1 / rl + 1 / v['RB'])            # wiper voltage per volt, into the virtual earth
    k = vw / v['RB']                                             # current per volt into the integrator
    return math.sqrt(v['RF'] / v['RLP']) * k / (2 * math.pi * v['C'])

OPA = """.subckt OPAN inp inn out gnd
Rnv nv gnd {rnv}
Env inp_i inp nv gnd 1
{inoise}
G1 gnd n1 inp_i inn 1
R1 n1 gnd 1e6
C1 n1 gnd 3.98n
E1 out gnd n1 gnd 1
.ends"""
def opa(en=1.1, inn=1.7):
    ino = ''
    if inn:
        gm = inn * 1e-12 / (K4T * 1e3) ** 0.5
        ino = f'Rni1 ni1 gnd 1k\nGni1 gnd inp ni1 gnd {gm}\nRni2 ni2 gnd 1k\nGni2 gnd inn ni2 gnd {gm}'
    return OPA.format(rnv=max(en * en * 1e-18 / K4T, 1e-9), inoise=ino)

def khn(th, v=V, mism=1.0, model='OPA1612', probes=False):
    """The filter from a 0-ohm source through 33u (the strip's C38 into HIN, 47K bias). model 'OPA1612' / 'OPA1656' / 'none' (single-pole with noise) or
    'ti' (TI OPA161x, Tian probes on the three units). mism scales gang B's divider (tracking error)."""
    x = alaw(th)
    L = ['* KHN HPF', 'VS src 0 DC 0 AC 1', 'CIN src hin 33u', 'RBIAS hin 0 47k']
    L += [f'RIN hin sp {v["RIN"]}', f'RBP bp sp {v["RBP"]}', f'CP sp 0 {v["CP"]}',
          f'RLP lp sm {v["RLP"]}', f'RF hp sm {v["RF"]}', f'CF hp sm {v["CF"]}']
    for nm, src, ve, out, m in (('a', 'hp', 'i1', 'bp', 1.0), ('b', 'bp', 'i2', 'lp', mism)):
        xm = min(max(x * m, 0), 1)
        L += [f'RU{nm} {src} w{nm} {v["POT"] * (1 - xm) + 1e-3}', f'RL{nm} w{nm} r{nm} {v["POT"] * xm + 1e-3}',
              f'R0{nm} r{nm} 0 {v["R0"]}', f'RT{nm} {src} w{nm} {v["RT"]}', f'RB{nm} w{nm} {ve} {v["RB"]}',
              f'CI{nm} {out} {ve} {v["C"]}']
    units = (('UA', 'sp', 'sm', 'hp'), ('UB', '0', 'i1', 'bp'), ('UC', '0', 'i2', 'lp'))
    if model == 'ti':
        M = os.environ.get('TI_MODELS', '')
        L.insert(1, f'.include {M}/OPA161x.LIB')
        L += ['VCC vcc 0 DC 16.9', 'VEE vee 0 DC -16.9']
        for u, p, n, o in units:
            L += [f'X{u} {u}_pp {n} vcc vee {u}_ox OPA161x', f'VST_{u} {u}_pp {p} DC 0 AC 0',
                  f'VTI_{u} {u}_ox {o} DC 0 AC 0', f'ITI_{u} 0 {u}_ox DC 0 AC 0']
    else:
        L.insert(1, opa(*({'OPA1612': (1.1, 1.7), 'OPA1656': (3.75, 0.006), 'none': (0, 0)}[model])))
        for u, p, n, o in units: L.append(f'X{u} {p} {n} {o} 0 OPAN')
    nodes = {t for l in L[2:] for t in l.split()[1:3] if not l.startswith(('.', '*', 'X', 'V', 'I'))}
    L += [f'RLK{i} {n} 0 1e9' for i, n in enumerate(sorted(nodes - {'0'}))]
    return L

def run(L, ctl):
    d = '\n'.join(L + ['.control', 'set noaskquit'] + ctl + ['.endc', '.end'])
    with tempfile.NamedTemporaryFile('w', suffix='.cir', delete=False, dir=HERE) as f: f.write(d); fn = f.name
    p = subprocess.run(['ngspice', '-b', fn], capture_output=True, text=True, cwd=HERE); os.unlink(fn)
    return {m.group(1).lower(): float(m.group(2)) for m in re.finditer(r'^\s*(\w+)\s+=\s+([-+0-9.eE]+)', p.stdout, re.M)}, p.stdout

def resp(th, **kw):
    r, _ = run(khn(th, **kw), ['ac dec 100 2 30k', 'let g = db(mag(v(hp)))', 'meas ac f3 when g=-3 rise=1',
                               'meas ac gmax max g', 'meas ac g1k find g at=1k', 'meas ac g20k find g at=20k',
                               'let p = ph(v(hp))*180/pi', 'meas ac p1k find p at=1k'])
    return r

if __name__ == '__main__':
    what = sys.argv[1] if len(sys.argv) > 1 else 'resp'
    if what in ('law', 'resp'):
        print(' rotation   f0 (law)   -3 dB (sim)   peak    1 kHz   20 kHz   phase 1 kHz')
        for th in (0, 0.1, 0.25, 0.4, 0.5, 0.6, 0.75, 0.9, 1.0):
            r = resp(th)
            print(f'   {th:4.2f}   {law(th):7.1f} Hz   {r.get("f3", 0):7.1f} Hz   {r.get("gmax", 0):+5.2f}   {r.get("g1k", 0):+5.2f}   '
                  f'{r.get("g20k", 0):+5.2f}   {r.get("p1k", 0):+6.2f}')
    if what == 'mismatch':
        for m in (0.8, 0.9, 1.0, 1.1, 1.2):
            r = [resp(th, mism=m) for th in (0.25, 0.5, 0.75)]
            print(f'gang B x{m}: -3 dB ' + ', '.join(f'{x.get("f3", 0):.1f}' for x in r) + ' Hz; peak ' +
                  ', '.join(f'{x.get("gmax", 0):+.2f}' for x in r) + ' dB')
    if what == 'noise':
        for model in ('none', 'OPA1612', 'OPA1656'):
            vals = []
            for th in (0, 0.5, 1.0):
                r, _ = run(khn(th, model=model), ['noise v(hp) vs dec 20 20 20k', 'setplot noise2',
                                                   'let nd = db(onoise_total/0.7746)', 'print nd'])
                vals.append(r.get('nd'))
            print(f'{model:8s} HPF output noise (dBu, 20 Hz-20 kHz) at CCW / mid / CW: ' + ' / '.join(f'{x:.1f}' for x in vals))
    if what == 'stab':
        from tian import loopgain, margins
        os.makedirs(f'{HERE}/raw', exist_ok=True)
        for th in (0, 0.5, 1.0):
            for cf, cp in ((0, 0), (V['CF'], V['CP'])):
                v = dict(V, CF=max(cf, 1e-18), CP=max(cp, 1e-18))
                ctl = ['set wr_singlescale', 'set wr_vecnames']
                for u, o in (('UA', 'hp'), ('UB', 'bp'), ('UC', 'lp')):
                    f = f'{HERE}/raw/hpf_{u}'
                    for fl in (f + '_v.txt', f + '_i.txt'):
                        if os.path.exists(fl): os.unlink(fl)
                    ctl += [f'alter @VTI_{u}[acmag] = 1', 'ac dec 30 1e4 1e9', f'wrdata {f}_v.txt v({u}_ox) v({o})',
                            f'alter @VTI_{u}[acmag] = 0', 'destroy all', f'alter @ITI_{u}[acmag] = 1', 'ac dec 30 1e4 1e9',
                            f'wrdata {f}_i.txt i(VTI_{u})', f'alter @ITI_{u}[acmag] = 0', 'destroy all']
                _, out = run(khn(th, v=v, model='ti'), ctl)
                if 'could not be simulated' in out: print('operating point failed'); continue
                res = {u: margins(*loopgain(f'{HERE}/raw/hpf_{u}_v.txt', f'{HERE}/raw/hpf_{u}_i.txt')) for u in ('UA', 'UB', 'UC')}
                print(f'rotation {th}, CF {cf * 1e12:.0f}p CP {cp * 1e12:.0f}p: ' +
                      '  '.join(f'{u} {r.get("pm")} deg ({r.get("clpk")} dB)' for u, r in res.items()))
