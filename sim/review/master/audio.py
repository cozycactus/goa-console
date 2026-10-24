"""Audio-band cost of a fix set: transfer functions 10 Hz - 20 kHz (and to 200 kHz) with and without the fixes.
Each path is driven from an upstream unit's VST source (AC 1 in series with its + input) and read at a node.
usage: audio.py FIXSET [cfgname]"""
import sys, json, numpy as np
from masterdeck import deck
import masterdeck
from tian import ngspice, load, HERE
from configs import CONFIGS
from fixes import FIXES

PATHS = {   # name: (driving VST, output node)
 'phones L (CRS -> PHO_L)':        ('U21A', 'PHO_L'),
 'phones L at the jack':           ('U21A', 'PHJ_L'),
 'post-amp L (RBUF -> POST_L)':    ('U2B', 'POST_L'),
 'C/Room L (CRS -> CRO_L)':        ('U21A', 'CRO_L'),
 'C/Room L XLR leg (CRS -> CRL_XP)': ('U21A', 'CRL_XP'),
 'aux 5 (A5 re-inv -> A5_OUT)':    ('U12B', 'A5_OUT'),
 'aux 6 (A6 re-inv -> A6_OUT)':    ('U15B', 'A6_OUT'),
 'solo (PFL re-inv -> PFL_SIG)':   ('U18B', 'PFL_SIG'),
 'CRS L (solo -> CRSB_L, PFL on)': ('U19A', 'CRSB_L'),
 'MIX L (summer -> MIX_L)':        ('U1B', 'MIX_L'),
 'mono (POST_L -> MONO)':          ('U5A', 'MONO'),
 'EXT R (tip -> EXT_RRO)':         (None, 'EXT_RRO'),
 'meter L X2':                     ('U21A', 'ML_X2'),
}

def run(cfg, tag):
    out = {}
    L = ['.control', 'set noaskquit', 'set wr_singlescale', 'set wr_vecnames']
    drivers = sorted({d for d, _ in PATHS.values() if d})
    for d in drivers:
        nodes = ' '.join(f'v({n})' for k, (dd, n) in PATHS.items() if dd == d)
        L += [f'alter @VST_{d}[acmag] = 1', 'ac dec 40 10 200k', f'wrdata {HERE}/raw/au_{tag}_{d}.txt {nodes}',
              f'alter @VST_{d}[acmag] = 0', 'destroy all']
    L += ['.endc']
    c = dict(cfg)
    c.setdefault('ext', {'L': (50, 1e-9), 'R': (50, 1e-9)})
    # EXT path: drive the R jack tip with an AC source through the 50R plug model
    c['extra'] = c.get('extra', []) + [('VEXTAC', 'extac', '0', 'DC 0 AC 1'), ('REXTAC', 'extac', 'EXT_RT', '1')]
    import os
    L2 = ['.control', 'set wr_singlescale', 'set wr_vecnames', 'ac dec 40 10 200k', f'wrdata {HERE}/raw/au_{tag}_ext.txt v(EXT_RRO)', '.endc']
    for ctl, chk in (('\n'.join(L), f'{HERE}/raw/au_{tag}_{drivers[-1]}.txt'), ('\n'.join(L2), f'{HERE}/raw/au_{tag}_ext.txt')):
        for o in ('.options itl1=500 noopiter', '.options itl1=500', '.options itl1=1000 gminsteps=100 srcsteps=100', '.options itl1=500 noopiter gmin=1e-11'):
            if os.path.exists(chk): os.unlink(chk)
            ngspice(deck(dict(c, opts=o), ctl), 'au')
            if os.path.exists(chk): break
    for k, (d, n) in PATHS.items():
        fn = f'{HERE}/raw/au_{tag}_{d}.txt' if d else f'{HERE}/raw/au_{tag}_ext.txt'
        head, a = load(fn)
        cols = [h for h in head[1:] if not h.startswith('frequency')]
        names = [k2 for k2, (dd, nn) in PATHS.items() if dd == d] if d else [k]
        idx = names.index(k)
        f = a[:, 0]; h = a[:, 1 + 2 * idx] + 1j * a[:, 2 + 2 * idx]
        out[k] = (f, h)
    return out

if __name__ == '__main__':
    fix = sys.argv[1]; cname = sys.argv[2] if len(sys.argv) > 2 else 'p075'
    base = dict(CONFIGS[cname])
    masterdeck.pins = masterdeck.pins_fix
    a = run(base, 'base')
    c = dict(base)
    for k, v in FIXES[fix].items():
        if k == 'extra': c['extra'] = c.get('extra', []) + v
        elif k == 'omit': c['omit'] = list(c.get('omit', [])) + v
        elif k == 'loads': c['loads'] = dict(c.get('loads', {}), **v)
        else: c[k] = v
    for k2, v2 in c.get('pinmove', {}).items(): masterdeck.pins[k2] = v2
    b = run(c, 'fix')
    print(f'audio-band cost of {fix} ({cname}): fixed / as designed')
    for k in PATHS:
        f, ha = a[k]; _, hb = b[k]
        r = hb / ha; sel = f <= 20e3
        db = 20 * np.log10(np.abs(r)); ph = np.degrees(np.angle(r))
        i20 = np.argmin(abs(f - 20e3)); i1 = np.argmin(abs(f - 1e3))
        lvl = 20 * np.log10(abs(ha[i1]))
        print(f'  {k:34s} level {lvl:+7.2f} dB @1k | change max {db[sel].max():+.4f} / min {db[sel].min():+.4f} dB in 20-20k, '
              f'{db[i20]:+.4f} dB {ph[i20]:+.2f} deg @20k')
