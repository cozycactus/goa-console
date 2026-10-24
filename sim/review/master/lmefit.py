"""Fit the LME49600 macro (masterdeck.lme_sub) to SNAS422E low-IQ-mode curves (Figs 12/13/16/17), 50 ohm source."""
import numpy as np, itertools, subprocess, os
from masterdeck import lme_sub
from tian import ngspice, load, HERE
# (RL, CL): [(f, gain dB, phase deg)] read off the figures (None = not read)
DATA = {
 (1e3, 0):      [(10e6, 0.0, -5), (25e6, 0.3, -10), (38e6, 1.0, -20), (65e6, 4.5, -50)],
 (100, 0):      [(10e6, -0.5, -5), (18e6, -0.3, -10), (30e6, 0.3, -20), (50e6, 2.0, -40), (60e6, 3.5, -50)],
 (1e3, 50e-12): [(20e6, 0.5, -10), (32e6, 1.5, -20), (55e6, 7.0, -50)],
 (1e3, 200e-12):[(15e6, 0.3, -10), (22e6, 1.0, -20), (42e6, None, -50)],
 (1e3, 1e-9):   [(5e6, -0.2, -10), (8e6, -0.4, -20), (10e6, -0.8, None), (17e6, None, -50), (25e6, -5.0, None)],
}
def resp(p):
    out = {}
    for (rl, cl), pts in DATA.items():
        d = f"""* fit
{lme_sub(p)}
VS s 0 DC 0 AC 1
RS s in 50
X1 in vcc vee out LME49600M
RL out 0 {rl}
CL out 0 {cl if cl else 1e-15}
.control
ac dec 40 1meg 200meg
wrdata {HERE}/raw/lf.txt v(out)
.endc
.end"""
        ngspice(d, 'lf'); _, a = load(f'{HERE}/raw/lf.txt')
        f = a[:, 0]; h = a[:, 1] + 1j * a[:, 2]
        out[(rl, cl)] = (f, 20*np.log10(abs(h)), np.degrees(np.unwrap(np.angle(h))))
    return out
def err(p, verbose=False):
    r = resp(p); e = 0
    for k, pts in DATA.items():
        f, g, ph = r[k]
        for fp, gd, pd in pts:
            gi, pi = np.interp(fp, f, g), np.interp(fp, f, ph)
            if gd is not None: e += (gi - gd)**2
            if pd is not None: e += ((pi - pd)/5)**2
            if verbose: print(k, f'{fp/1e6:5.1f}MHz gain {gi:6.2f} ({gd}) phase {pi:6.1f} ({pd})')
        pk = np.argmax(g); 
        if verbose: print('   peak', round(g[pk],1), 'dB at', round(f[pk]/1e6,1), 'MHz')
    return e
if __name__ == '__main__':
    best = None
    for fn, q, td, ro, lo in itertools.product((70e6, 85e6, 100e6), (1.2, 1.8, 2.5), (0.3e-9, 0.8e-9, 1.3e-9), (4, 6, 8), (5e-9, 20e-9, 40e-9)):
        p = dict(fn=fn, q=q, td=td, ro=ro, lo=lo, cin=3e-12)
        e = err(p)
        if best is None or e < best[0]: best = (e, p); print(round(e,1), p, flush=True)
    print('BEST', best); err(best[1], True)
