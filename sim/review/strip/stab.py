"""Loop stability of every OPA1612 unit on the strip, TI OPA161x macromodel, in the full strip network.
Per configuration (pot positions / switch states) and per unit:
  Tian probe at the op-amp output: run V (VTI ac 1) and run I (ITI ac 1);
    Tv = -v(x)/v(y), Ti = (1 - i(VTI))/i(VTI), T = (Tv*Ti - 1)/(Tv + Ti + 2)
  -> crossover fc, phase margin (min over 0 dB crossings), gain margin, closed-loop peaking max|T/(1+T)| (f >= 1 MHz)
  noise-gain run (VST ac 1 in series with + input): v(out)/vst, peak above 1 MHz relative to its 100 kHz value
  optional transient: 10 mV step on VST, overshoot % of the settled step.
usage (lib): from stab import run_config"""
import os, json, numpy as np
from stripdeck import deck, ngspice, units, node, HERE

U = units()
UNITS = {u[0]: u for u in U}
FSTART, FSTOP, PPD = 1e3, 300e6, 60

def outnet(nm):
    u = UNITS[nm]; return node(u[1], u[4])

def ctl_ac(stages, tag):
    L = ['.control', 'set noaskquit', 'set wr_singlescale', 'set wr_vecnames']
    for s in stages:
        o = outnet(s)
        f = f'{HERE}/raw/{tag}_{s}'
        L += [f'alter @VTI_{s}[acmag] = 1', f'ac dec {PPD} {FSTART} {FSTOP}', f'wrdata {f}_v.txt v({s}_ox) v({o})',
              f'alter @VTI_{s}[acmag] = 0', 'destroy all',
              f'alter @ITI_{s}[acmag] = 1', f'ac dec {PPD} {FSTART} {FSTOP}', f'wrdata {f}_i.txt i(VTI_{s})',
              f'alter @ITI_{s}[acmag] = 0', 'destroy all',
              f'alter @VST_{s}[acmag] = 1', f'ac dec {PPD} {FSTART} {FSTOP}', f'wrdata {f}_n.txt v({o})',
              f'alter @VST_{s}[acmag] = 0', 'destroy all']
    L += ['.endc']
    return '\n'.join(L)

def ctl_tran(stages, tag, amp=0.01):
    L = ['.control', 'set noaskquit', 'set wr_singlescale', 'set wr_vecnames']
    for s in stages:
        o = outnet(s)
        L += [f'alter @VST_{s}[pulse] = [ 0 {amp} 200n 1n 1n 10u 20u ]', 'tran 0.25n 2.2u 0 0.25n',
              f'wrdata {HERE}/raw/{tag}_{s}_t.txt v({o})',
              f'alter @VST_{s}[pulse] = [ 0 0 0 1n 1n 1 2 ]', 'destroy all']
    L += ['.endc']
    return '\n'.join(L)

def load(fn):
    with open(fn) as f:
        head = f.readline().split()
        d = np.array([[float(x) for x in l.split()] for l in f if l.strip()])
    return head, d

def analyse(tag, s):
    _, dv = load(f'{HERE}/raw/{tag}_{s}_v.txt')
    _, di = load(f'{HERE}/raw/{tag}_{s}_i.txt')
    _, dn = load(f'{HERE}/raw/{tag}_{s}_n.txt')
    f = dv[:, 0]
    vx = dv[:, 1] + 1j * dv[:, 2]; vy = dv[:, 3] + 1j * dv[:, 4]
    ii = di[:, 1] + 1j * di[:, 2]
    Tv = -vx / vy
    Ti = (1 - ii) / ii
    T = (Tv * Ti - 1) / (Tv + Ti + 2)
    mag = 20 * np.log10(np.abs(T)); ph = np.degrees(np.unwrap(np.angle(T)))
    ph -= 360 * np.round(ph[0] / 360)                # start within +-180
    res = {}
    cross = [k for k in range(len(f) - 1) if mag[k] >= 0 > mag[k + 1]]
    pms = []
    for k in cross:
        a = mag[k] / (mag[k] - mag[k + 1])
        fc = 10 ** (np.log10(f[k]) + a * (np.log10(f[k + 1]) - np.log10(f[k])))
        p = ph[k] + a * (ph[k + 1] - ph[k])
        pms.append(((180 + p + 180) % 360 - 180, fc))
    if pms:
        pm, fc = min(pms); res.update(pm=round(float(pm), 1), fc=round(float(fc) / 1e6, 2), ncross=len(pms))
    # gain margin: |T| where phase crosses -180 (first one above the last 0 dB crossing region)
    w = lambda x: (x + 180) % 360 - 180
    gms = [(-mag[k], f[k]) for k in range(len(f) - 1) if mag[k] < 0 and w(ph[k] + 180) * w(ph[k + 1] + 180) <= 0 and abs(ph[k+1]-ph[k]) < 90]
    if gms: res['gm'] = round(float(min(gms)[0]), 1); res['fgm'] = round(float(min(gms)[1]) / 1e6, 1)
    cl = 20 * np.log10(np.abs(T / (1 + T)))
    sel = f >= 1e6
    k = np.argmax(cl[sel]); res['clpk'] = round(float(cl[sel][k]), 2); res['fclpk'] = round(float(f[sel][k]) / 1e6, 2)
    n = np.abs(dn[:, 1] + 1j * dn[:, 2]); ref = np.interp(1e5, f, n)
    kn = np.argmax(n[sel]); res['ngpk'] = round(float(20 * np.log10(n[sel][kn] / ref)), 2)
    res['fngpk'] = round(float(f[sel][kn]) / 1e6, 2); res['ng100k'] = round(float(20 * np.log10(ref)), 2)
    return res

def overshoot(tag, s):
    _, d = load(f'{HERE}/raw/{tag}_{s}_t.txt')
    t, v = d[:, 0], d[:, 1]
    v0 = np.interp(190e-9, t, v)
    w = (t > 200e-9)
    vf = np.mean(v[(t > 1.9e-6) & (t < 2.2e-6)])
    step = vf - v0
    if abs(step) < 1e-6: return None
    vv = (v[w] - v0) / step
    os_ = (vv.max() - 1) * 100
    # ringing after the first peak: peak-to-peak beyond 300 ns after the step
    late = (v[(t > 500e-9)] - v0) / step
    return dict(os=round(float(os_), 1), step_mv=round(float(step) * 1e3, 2), late_pp=round(float(late.max() - late.min()) * 100, 1))

def run_config(tag, pos, sw, extra=(), src='50', loads=(), stages=None, tran=False):
    stages = stages or [u[0] for u in U]
    os.makedirs(f'{HERE}/raw', exist_ok=True)
    out = ngspice(deck(pos, sw, ctl_ac(stages, tag), extra=extra, src=src, loads=loads), tag)
    res = {}
    for s in stages:
        try: res[s] = analyse(tag, s)
        except Exception as e: res[s] = {'err': str(e)}; print(out[-2000:])
    if tran:
        out = ngspice(deck(pos, sw, ctl_tran(stages, tag), extra=extra, src=src, loads=loads), tag + 't')
        for s in stages:
            try: res[s].update(overshoot(tag, s) or {})
            except Exception as e: res[s]['terr'] = str(e); print(out[-2000:])
    return res
