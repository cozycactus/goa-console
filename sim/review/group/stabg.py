"""Loop stability of the group module's OPA1612 units (method of sim/review/strip/stab.py).
Tian probe at each output: run V (VTI ac 1), run I (ITI ac 1); Tv = -v(ox)/v(out), Ti = (1 - i(VTI))/i(VTI),
T = (Tv*Ti - 1)/(Tv + Ti + 2) -> phase margin (min over 0 dB crossings), gain margin, closed-loop peaking
max|T/(1+T)| above 1 MHz; noise-gain run (VST ac 1 at the + input): v(out)/vst peak above 1 MHz relative to 100 kHz;
transient: 10 mV step on VST, overshoot % and late ringing."""
import os, numpy as np
from groupdeck import deck, ngspice, outnet, UNITS, HERE

FSTART, FSTOP, PPD = 1e3, 300e6, 60
RAW = os.path.join(HERE, 'raw'); os.makedirs(RAW, exist_ok=True)

def ctl_ac(stages, tag):
    L = ['.control', 'set noaskquit', 'set wr_singlescale', 'set wr_vecnames']
    for s in stages:
        o = outnet(s); f = f'{RAW}/{tag}_{s}'
        L += [f'alter @VTI_{s}[acmag] = 1', f'ac dec {PPD} {FSTART} {FSTOP}', f'wrdata {f}_v.txt v({s}_ox) v({o})',
              f'alter @VTI_{s}[acmag] = 0', 'destroy all',
              f'alter @ITI_{s}[acmag] = 1', f'ac dec {PPD} {FSTART} {FSTOP}', f'wrdata {f}_i.txt i(VTI_{s})',
              f'alter @ITI_{s}[acmag] = 0', 'destroy all',
              f'alter @VST_{s}[acmag] = 1', f'ac dec {PPD} {FSTART} {FSTOP}', f'wrdata {f}_n.txt v({o})',
              f'alter @VST_{s}[acmag] = 0', 'destroy all']
    return '\n'.join(L + ['.endc'])

def ctl_tran(stages, tag, amp=0.01):
    L = ['.control', 'set noaskquit', 'set wr_singlescale', 'set wr_vecnames']
    for s in stages:
        o = outnet(s)
        L += [f'alter @VST_{s}[pulse] = [ 0 {amp} 200n 1n 1n 10u 20u ]', 'tran 0.25n 2.2u 0 0.25n',
              f'wrdata {RAW}/{tag}_{s}_t.txt v({o})', f'alter @VST_{s}[pulse] = [ 0 0 0 1n 1n 1 2 ]', 'destroy all']
    return '\n'.join(L + ['.endc'])

def load(fn):
    with open(fn) as f:
        f.readline(); return np.array([[float(x) for x in l.split()] for l in f if l.strip()])

def loopgain(tag, s):
    dv, di = load(f'{RAW}/{tag}_{s}_v.txt'), load(f'{RAW}/{tag}_{s}_i.txt')
    f = dv[:, 0]; vx = dv[:, 1] + 1j * dv[:, 2]; vy = dv[:, 3] + 1j * dv[:, 4]; ii = di[:, 1] + 1j * di[:, 2]
    Tv = -vx / vy; Ti = (1 - ii) / ii
    return f, (Tv * Ti - 1) / (Tv + Ti + 2)

def analyse(tag, s):
    f, T = loopgain(tag, s)
    dn = load(f'{RAW}/{tag}_{s}_n.txt')
    mag = 20 * np.log10(np.abs(T)); ph = np.degrees(np.unwrap(np.angle(T))); ph -= 360 * np.round(ph[0] / 360)
    res = {}; pms = []
    for k in range(len(f) - 1):
        if mag[k] >= 0 > mag[k + 1]:
            a = mag[k] / (mag[k] - mag[k + 1])
            fc = 10 ** (np.log10(f[k]) + a * (np.log10(f[k + 1]) - np.log10(f[k])))
            p = ph[k] + a * (ph[k + 1] - ph[k])
            pms.append(((180 + p + 180) % 360 - 180, fc))
    if pms:
        pm, fc = min(pms); res.update(pm=round(float(pm), 1), fc=round(float(fc) / 1e6, 2), ncross=len(pms))
    w = lambda x: (x + 180) % 360 - 180
    u = w(ph + 180)          # 0 where T = -|T| (phase -180 mod 360); skip the wrap at phase 0 mod 360
    gms = [(-mag[k], f[k]) for k in range(len(f) - 1)
           if mag[k] < 0 and u[k] * u[k + 1] <= 0 and abs(u[k + 1] - u[k]) < 90]
    if gms: res['gm'] = round(float(min(gms)[0]), 1); res['fgm'] = round(float(min(gms)[1]) / 1e6, 1)
    cl = 20 * np.log10(np.abs(T / (1 + T))); sel = f >= 1e6
    k = np.argmax(cl[sel]); res['clpk'] = round(float(cl[sel][k]), 2); res['fclpk'] = round(float(f[sel][k]) / 1e6, 2)
    n = np.abs(dn[:, 1] + 1j * dn[:, 2]); ref = np.interp(1e5, f, n)
    kn = np.argmax(n[sel]); res['ngpk'] = round(float(20 * np.log10(n[sel][kn] / ref)), 2)
    res['fngpk'] = round(float(f[sel][kn]) / 1e6, 2); res['ng100k'] = round(float(20 * np.log10(ref)), 2)
    return res

def overshoot(tag, s):
    d = load(f'{RAW}/{tag}_{s}_t.txt'); t, v = d[:, 0], d[:, 1]
    v0 = np.interp(190e-9, t, v); vf = np.mean(v[(t > 1.9e-6) & (t < 2.2e-6)]); step = vf - v0
    if abs(step) < 1e-6: return None
    vv = (v[t > 200e-9] - v0) / step; late = (v[t > 500e-9] - v0) / step
    return dict(os=round(float((vv.max() - 1) * 100), 1), step_mv=round(float(step) * 1e3, 2),
                late_pp=round(float(late.max() - late.min()) * 100, 1))

def run(tag, cfg, stages=None, tran=False):
    stages = stages or list(UNITS)
    out = ngspice(deck(cfg, ctl_ac(stages, tag)), tag)
    res = {}
    for s in stages:
        try: res[s] = analyse(tag, s)
        except Exception as e: res[s] = {'err': str(e)}; print(out[-3000:])
    if tran:
        out = ngspice(deck(cfg, ctl_tran(stages, tag)), tag + 't')
        for s in stages:
            try: res[s].update(overshoot(tag, s) or {})
            except Exception as e: res[s]['terr'] = str(e); print(out[-3000:])
    return res
