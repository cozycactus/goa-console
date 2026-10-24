"""Loop stability of master op-amp units in the full master deck (masterdeck.py), as sim/review/strip/stab.py:
Tian probe per unit -> phase margin, crossover, gain margin, closed-loop peak above 1 MHz; noise-gain peaking from
VST; optional 10 mV step overshoot."""
import os, json, numpy as np
from masterdeck import deck, outnet, UNITS, HERE
from tian import ngspice, load, loopgain, margins

FSTART, FSTOP, PPD = 1e4, 1e9, 30
TL = lambda s: s[:3] in ('U29', 'U30', 'U36', 'U37')

def ctl_ac(stages, tag):
    L = ['.control', 'set noaskquit', 'set wr_singlescale', 'set wr_vecnames']
    for s in stages:
        o = outnet(s); f = f'{HERE}/raw/{tag}_{s}'
        fs = 10 if TL(s) else FSTART
        L += [f'alter @VTI_{s}[acmag] = 1', f'ac dec {PPD} {fs} {FSTOP}', f'wrdata {f}_v.txt v({s}_ox) v({o})',
              f'alter @VTI_{s}[acmag] = 0', 'destroy all',
              f'alter @ITI_{s}[acmag] = 1', f'ac dec {PPD} {fs} {FSTOP}', f'wrdata {f}_i.txt i(VTI_{s})',
              f'alter @ITI_{s}[acmag] = 0', 'destroy all',
              f'alter @VST_{s}[acmag] = 1', f'ac dec {PPD} {fs} {FSTOP}', f'wrdata {f}_n.txt v({o})',
              f'alter @VST_{s}[acmag] = 0', 'destroy all']
    L += ['.endc']
    return '\n'.join(L)

def ctl_tran(stages, tag, amp=0.01, tstop=2.2e-6):
    L = ['.control', 'set noaskquit', 'set wr_singlescale', 'set wr_vecnames']
    for s in stages:
        o = outnet(s)
        L += [f'alter @VST_{s}[pulse] = [ 0 {amp} 200n 1n 1n 10u 20u ]', f'tran 0.25n {tstop} 0 0.25n',
              f'wrdata {HERE}/raw/{tag}_{s}_t.txt v({o})',
              f'alter @VST_{s}[pulse] = [ 0 0 0 1n 1n 1 2 ]', 'destroy all']
    L += ['.endc']
    return '\n'.join(L)

def analyse(tag, s):
    f, T = loopgain(f'{HERE}/raw/{tag}_{s}_v.txt', f'{HERE}/raw/{tag}_{s}_i.txt')
    res = margins(f, T, 1e5 if TL(s) else 1e6)
    _, dn = load(f'{HERE}/raw/{tag}_{s}_n.txt')
    n = np.abs(dn[:, 1] + 1j * dn[:, 2]); ref = np.interp(1e4 if TL(s) else 1e5, f, n); sel = f >= (1e5 if TL(s) else 1e6)
    kn = np.argmax(n[sel]); res['ngpk'] = round(float(20 * np.log10(n[sel][kn] / ref)), 2)
    res['fngpk'] = round(float(f[sel][kn]) / 1e6, 2); res['ng100k'] = round(float(20 * np.log10(ref)), 2)
    return res

def overshoot(tag, s, tstop=2.2e-6):
    _, d = load(f'{HERE}/raw/{tag}_{s}_t.txt')
    t, v = d[:, 0], d[:, 1]
    v0 = np.interp(190e-9, t, v); vf = np.mean(v[(t > 0.85 * tstop) & (t <= tstop)]); step = vf - v0
    if abs(step) < 1e-6: return None
    vv = (v[t > 200e-9] - v0) / step
    late = (v[t > 500e-9] - v0) / step
    return dict(os=round(float((vv.max() - 1) * 100), 1), step_mv=round(float(step) * 1e3, 2),
                late_pp=round(float(late.max() - late.min()) * 100, 1))

def run_config(tag, cfg, stages=None, tran=False):
    import masterdeck
    masterdeck.pins = dict(masterdeck.pins_raw if cfg.get('ext_bug') else masterdeck.pins_fix)
    for k, n in cfg.get('pinmove', {}).items(): masterdeck.pins[k] = n
    stages = stages or list(UNITS)
    OPTS = [cfg.get('opts', '.options itl1=500 noopiter'), '.options itl1=500', '.options itl1=1000 gminsteps=100 srcsteps=100',
            '.options itl1=500 noopiter gmin=1e-11']
    for o in OPTS:
        out = ngspice(deck(dict(cfg, opts=o), ctl_ac(stages, tag)), tag)
        res = {}
        for s in stages:
            try: res[s] = analyse(tag, s)
            except Exception as e: res[s] = {'err': str(e)}
        if not any('err' in v for v in res.values()): break
    else: print('OP FAILED', tag, out[-1500:])
    cfg = dict(cfg, opts=o)
    if tran:
        out = ngspice(deck(cfg, ctl_tran(stages, tag)), tag + 't')
        for s in stages:
            try: res[s].update(overshoot(tag, s) or {})
            except Exception as e: res[s]['terr'] = str(e); print(out[-2000:])
    return res

if __name__ == '__main__':
    import sys, time
    t0 = time.time()
    st = sys.argv[1].split(',') if len(sys.argv) > 1 else None
    r = run_config('dbg', {}, st)
    for k, v in r.items(): print(f'{k:6s} {outnet(k):14s} {v}')
    print(f'{time.time()-t0:.0f} s')
