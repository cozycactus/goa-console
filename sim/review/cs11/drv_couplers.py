"""CS11b: the DRV135's output balance against its two Sense-loop couplers (TI's DRV134 model, SBOM004A, with CS4c's
22R in each loop, each leg into 1 kohm 0.1 % after the relay and link). jig_targets.py found the balance set by how
well the two couplers match: the DRV's cross-coupled loop floats the outputs, so a coupler mismatch comes out as common
mode. Here:
1. common mode against differential, at 50 Hz / 100 Hz / 1 kHz, against the mismatch (0-40 %) and the value (10, 22,
   47, 100 uF);
2. a Monte Carlo of pairs drawn from the part's tolerance (+-20 %, uniform) and of sorted pairs (pairs within 2 % / 5 %);
3. the differential low end (-0.5 dB and -3 dB points, the level at 20 Hz) and its peaking, by value;
4. the cross-coupled loop at low frequency (Tian probe at VO+): the deepest dip of |1 + T| below 20 kHz, by value
   (by design small: the loop sits just under unity; a lower value would mean LF peaking);
5. the stock that sorting takes: the console's 15 DRV135s need 15 pairs within 2 %; how many parts to buy so that
   sorting (pairing neighbours in value) gives them, for a uniform +-20 % spread and a normal one (sigma 5 %).
usage: TI_MODELS=<folder> python3 sim/review/cs11/drv_couplers.py"""
import os, re, sys, math, random, subprocess, tempfile
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
M = os.environ.get('TI_MODELS', '')
CWD = os.path.join(ROOT, 'sim', 'review', 'cs4')            # its .spiceinit: PSpice compatibility for TI's model

def ng(deck):
    with tempfile.NamedTemporaryFile('w', suffix='.cir', delete=False, dir=CWD) as f: f.write(deck)
    out = subprocess.run(['ngspice', '-b', f.name], capture_output=True, text=True, cwd=CWD)
    os.unlink(f.name)
    return out.stdout + out.stderr

def circuit(cp, cn, probe=False, rl=1e3):
    L = [f'.include {M}/DRV134.LIB', 'VP vp 0 16.9', 'VM vm 0 -16.9', 'VIN in 0 DC 0 AC 1', 'RS in vin 47',
         'X1 von sn 0 vin vm vp sp vopx DRV134']
    L += ['VTI vopx vop DC 0 AC 0', 'ITI 0 vopx DC 0 AC 0'] if probe else ['VTI vopx vop DC 0']
    for leg, vo, s, c in (('p', 'vop', 'sp', cp), ('n', 'von', 'sn', cn)):
        L += [f'RX{leg} {vo} {vo}r 22', f'C{leg} {vo}r {s} {c}', f'RK{leg} {s} k{leg} 0.05', f'LL{leg} k{leg} j{leg} 100n',
              f'RL{leg} j{leg} 0 {rl}', f'CL{leg} j{leg} 0 1n']
    return '\n'.join(L)

def balance(cp, cn, freqs=(50, 100, 1000)):
    out = []
    for f in freqs:
        o = ng(f"""* bal
{circuit(cp, cn)}
.control
ac lin 1 {f} {f}
let a = db(abs((v(jp)+v(jn))/2)/abs(v(jp)-v(jn)))
print a
.endc
.end""")
        m = re.search(r'^a\s+=\s+([-+0-9.eE]+)', o, re.M); out.append(float(m.group(1)) if m else float('nan'))
    return out

def lowend(c):
    o = ng(f"""* lf
{circuit(c, c)}
.control
ac dec 50 1 100k
let g = db(abs(v(jp)-v(jn)))
meas ac gref find g at=1k
let gn = g - gref
meas ac f05 when gn=-0.5 rise=1
meas ac f3 when gn=-3 rise=1
meas ac g20 find gn at=20
meas ac gpk max gn
.endc
.end""")
    r = {k: float(v) for k, v in re.findall(r'^(\w+)\s+=\s+([-+0-9.eE]+)', o, re.M)}
    return r.get('f05'), r.get('f3'), r.get('g20'), r.get('gpk')

def loopdip(c):
    raw = os.path.join(HERE, 'raw'); os.makedirs(raw, exist_ok=True); fv, fi = f'{raw}/v.txt', f'{raw}/i.txt'
    ng(f"""* loop
{circuit(c, c, probe=True)}
.control
set wr_singlescale
alter @VTI[acmag] = 1
ac dec 50 1 100k
wrdata {fv} v(vopx) v(vop)
alter @VTI[acmag] = 0
destroy all
alter @ITI[acmag] = 1
ac dec 50 1 100k
wrdata {fi} i(VTI)
.endc
.end""")
    dv, di = np.loadtxt(fv), np.loadtxt(fi)
    f = dv[:, 0]; vx = dv[:, 1] + 1j * dv[:, 2]; vy = dv[:, 3] + 1j * dv[:, 4]; ii = di[:, 1] + 1j * di[:, 2]
    Tv, Ti = -vx / vy, (1 - ii) / ii; T = (Tv * Ti - 1) / (Tv + Ti + 2)
    a = abs(1 + T); k = int(np.argmin(a[f < 20e3]))
    return float(a[k]), float(f[k])

if __name__ == '__main__':
    if not M or not os.path.exists(f'{M}/DRV134.LIB'): sys.exit('set TI_MODELS to the folder with DRV134.LIB')
    print('1. common mode against differential (dB) at 50 Hz / 100 Hz / 1 kHz, the minus leg\'s coupler (1 - m) x C')
    table = {}
    for c in (10e-6, 22e-6, 47e-6, 100e-6):
        for m in (0.0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.4):
            b = balance(c, c * (1 - m)); table[(c, m)] = b
            print(f'   {c * 1e6:4.0f} uF, {m * 100:4.0f} % apart: ' + ' / '.join(f'{x:6.1f}' for x in b), flush=True)
    print('\n2. Monte Carlo (2000 pairs): the 1 kHz and 100 Hz balance, median / worst 5 %, interpolated in the mismatch')
    rng = random.Random(1)
    def interp(c, m, k):
        ms = [0.0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.4]
        v = [10 ** (table[(c, x)][k] / 20) for x in ms]
        return 20 * math.log10(max(np.interp(m, ms, v), 1e-9))
    for c in (10e-6, 47e-6, 100e-6):
        for label, draw in (('+-20 %, as bought', lambda: abs(rng.uniform(0.8, 1.2) / rng.uniform(0.8, 1.2) - 1)),
                            ('sorted, within 5 %', lambda: rng.uniform(0, 0.05)),
                            ('sorted, within 2 %', lambda: rng.uniform(0, 0.02))):
            ms = sorted(draw() for _ in range(2000))
            r = [(interp(c, ms[1000], k), interp(c, ms[1899], k)) for k in (2, 1)]
            print(f'   {c * 1e6:4.0f} uF {label:20s}: 1 kHz {r[0][0]:6.1f} / {r[0][1]:6.1f}, 100 Hz {r[1][0]:6.1f} / {r[1][1]:6.1f}',
                  flush=True)
    print('\n3. differential low end: -0.5 dB, -3 dB, the level at 20 Hz, peaking')
    for c in (10e-6, 22e-6, 47e-6, 100e-6):
        f05, f3, g20, pk = lowend(c)
        print(f'   {c * 1e6:4.0f} uF: -0.5 dB at {f05 or 0:6.2f} Hz, -3 dB at {f3 or 0:6.2f} Hz, 20 Hz {g20:+6.2f} dB, peak {pk:+5.2f} dB',
              flush=True)
    print('\n4. the cross-coupled loop below 20 kHz: deepest |1 + T| (by design small: the loop sits just under unity)')
    for c in (10e-6, 22e-6, 47e-6, 100e-6):
        a, f = loopdip(c)
        print(f'   {c * 1e6:4.0f} uF: |1 + T| {a:5.3f} at {f:8.1f} Hz', flush=True)
    print('\n5. sorting stock: chance that n parts give the 15 pairs within 2 % (4000 draws each)')
    def pairs(vals, tol=0.02):
        v, n, i = sorted(vals), 0, 0
        while i < len(v) - 1:
            if v[i + 1] / v[i] - 1 <= tol: n, i = n + 1, i + 2
            else: i += 1
        return n
    rng2 = random.Random(2)
    for dist, draw in (('uniform +-20 %', lambda: rng2.uniform(0.8, 1.2)), ('normal, sigma 5 %', lambda: rng2.gauss(1.0, 0.05))):
        print(f'   {dist:18s}: ' + ', '.join(f'{n} parts {sum(pairs([draw() for _ in range(n)]) >= 15 for _ in range(4000)) / 40:5.1f} %'
                                          for n in (30, 34, 36, 40)), flush=True)
