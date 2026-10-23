"""PFLDET line with T PFL/AFL switches on it (master_lib.afl() / strip SW3 topology), N of them pressed.
Pressed: +VL -> 100K -> PFLDET, ON node also feeds 4K7 + red LED to GNDD.
Released: pole B open, so the ON node floats: PFLDET -> 100K -> ON -> 4K7 -> LED -> GNDD (back-feed path).
Master: 10K PFLDET -> GNDD, comparator threshold +VL * 10K/230K. Optional series diode (1N4148) in each 100K branch.
Runs ngspice -b per case; prints PFLDET, threshold, current in one released LED, current in one pressed LED."""
import subprocess, sys, re, os
HERE = os.path.dirname(os.path.abspath(__file__))
VL = 16.9          # +VBUS 17.0 V less ~10 mA through the module's 10R
LEDS = {'AlGaInP-like (2.0V@20mA, n=2)': 'D(IS=3.2e-19 N=2 RS=10)',
        'low-Vf red (1.8V@20mA, n=1.8)': 'D(IS=3.2e-19 N=1.8 RS=10)'}
def run(T, N, led, diode=False):
    L = ['* pfldet', f'.model LED {led}', '.model D4148 D(IS=2.52n N=1.752 RS=0.568)',
         f'VL vl 0 {VL}', 'RPD det 0 10K', 'RA vl ref 220K', 'RB ref 0 10K']
    for k in range(T):
        on = f'on{k}'
        if k < N: L.append(f'Rsrc{k} vl {on} 1m')            # pressed: pole B joins +VL to ON
        if diode: L += [f'D{k} {on} x{k} D4148', f'R{k} x{k} det 100K']
        else: L.append(f'R{k} {on} det 100K')
        L += [f'RL{k} {on} la{k} 4.7K', f'DL{k} la{k} 0 LED']
    L += ['.op', '.control', 'op', 'print v(det) v(ref) i(VL)', 'let irel = (v(on%d)-v(la%d))/4.7k' % (T-1, T-1),
          'let ipr = (v(on0)-v(la0))/4.7k', 'print irel ipr', '.endc', '.end']
    p = os.path.join(HERE, 'pfldet_case.cir'); open(p, 'w').write('\n'.join(L) + '\n')
    out = subprocess.run(['/opt/homebrew/bin/ngspice', '-b', p], capture_output=True, text=True).stdout
    g = lambda k: float(re.search(k + r'\s*=\s*([-\d.e+]+)', out).group(1))
    return g(r'v\(det\)'), g(r'v\(ref\)'), g('irel'), g('ipr') if N else 0.0
if __name__ == '__main__':
    for diode in (False, True):
        for name, led in LEDS.items():
            print(f'\n=== LED model: {name}; series diode in 100K branch: {diode}')
            print(' T  N   PFLDET V  ideal V   thresh V  I(released LED) uA  I(pressed LED) mA')
            for T in (34, 38):
                for N in (0, 1, 2, 3, 4, 8, 12, 24):
                    v, ref, irel, ipr = run(T, N, led, diode)
                    vd = 0.6 if diode else 0.0
                    ideal = (VL - vd) * (10e3 / (100e3 / N + 10e3)) / 1 if N else 0.0
                    ideal = (VL - vd) * 10e3 / (100e3 / N + 10e3) if N else 0.0
                    print(f'{T:2d} {N:2d}   {v:7.3f}   {ideal:7.3f}   {ref:7.3f}   {irel*1e6:9.3f}          {ipr*1e3:6.3f}')
