"""Tian-probe helpers: run ngspice decks, analyse loop gain (as sim/review/strip/stab.py)."""
import os, subprocess, tempfile, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
M = os.environ.get('TI_MODELS', os.path.join(HERE, 'models'))   # TI's models stay out of the repo (licence)
FSTART, FSTOP, PPD = 1e3, 1e9, 50

def ngspice(text, tag='x', keep=False):
    os.makedirs(f'{HERE}/raw', exist_ok=True)
    with tempfile.NamedTemporaryFile('w', suffix='.cir', delete=False, dir=f'{HERE}/raw', prefix=tag + '_') as f:
        f.write(text); fn = f.name
    try:
        p = subprocess.run(['ngspice', '-b', fn], capture_output=True, text=True, cwd=HERE, timeout=float(os.environ.get('NG_TIMEOUT', 600)))
        txt = p.stdout + p.stderr
    except subprocess.TimeoutExpired: txt = 'TIMEOUT'
    if not keep: os.unlink(fn)
    return txt

def load(fn):
    with open(fn) as f:
        head = f.readline().split()
        d = np.array([[float(x) for x in l.split()] for l in f if l.strip()])
    return head, d

def loopgain(fv, fi):
    _, dv = load(fv); _, di = load(fi)
    f = dv[:, 0]; vx = dv[:, 1] + 1j * dv[:, 2]; vy = dv[:, 3] + 1j * dv[:, 4]; ii = di[:, 1] + 1j * di[:, 2]
    Tv = -vx / vy; Ti = (1 - ii) / ii
    return f, (Tv * Ti - 1) / (Tv + Ti + 2)

def margins(f, T, fmin_cl=1e6):
    mag = 20 * np.log10(np.abs(T)); ph = np.degrees(np.unwrap(np.angle(T))); ph -= 360 * np.round(ph[0] / 360)
    res = {}
    cross = [k for k in range(len(f) - 1) if mag[k] >= 0 > mag[k + 1]]
    pms = []
    for k in cross:
        a = mag[k] / (mag[k] - mag[k + 1])
        fc = 10 ** (np.log10(f[k]) + a * (np.log10(f[k + 1]) - np.log10(f[k])))
        p = ph[k] + a * (ph[k + 1] - ph[k])
        pms.append((((180 + p + 180) % 360 - 180), fc))
    if pms:
        pm, fc = min(pms); res.update(pm=round(float(pm), 1), fc=round(float(fc) / 1e6, 2), ncross=len(pms))
    w = lambda x: (x + 180) % 360 - 180
    gms = [(-mag[k], f[k]) for k in range(len(f) - 1) if mag[k] < 0 and w(ph[k] + 180) * w(ph[k + 1] + 180) <= 0
           and abs(w(ph[k] + 180)) < 90 and abs(w(ph[k + 1] + 180)) < 90]
    if gms: res['gm'] = round(float(min(gms)[0]), 1); res['fgm'] = round(float(min(gms)[1]) / 1e6, 1)
    cl = 20 * np.log10(np.abs(T / (1 + T))); sel = f >= fmin_cl
    k = np.argmax(cl[sel]); res['clpk'] = round(float(cl[sel][k]), 2); res['fclpk'] = round(float(f[sel][k]) / 1e6, 2)
    return res
