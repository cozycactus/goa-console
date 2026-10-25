"""Strip Monte Carlo over part tolerances (2026-10-25): how far real strips spread from each other.
One strip (tools/sim_console.py's module from the netlists, single-pole op-amps), every R / C / pot drawn per run:
  resistors: 0.1 % where the value says so, else 1 %; C0G 5 %, X7R 10 %, film 10 %, MUSE ES and other bipolars 20 %;
  pots: track +-20 % (Alpha / ALPS / Bourns), the two gangs of a dual tracking within +-10 %.
Measured per run (1 kHz unless stated): PRE gain at the gain detent (EQ in, flat), gain at CW / CCW, each EQ band at
full boost at its frequency, the HPF -3 dB at mid rotation, pan centre L - R, POST with the fader at "0".
usage: python3 sim/review/gaps/mc.py [runs]   -> spread table (mean, sd, min, max)"""
import os, re, sys, math, random, statistics
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'tools'))
import sim_console as sc

ON = {'SW4': True, 'SW5': True, 'SW12': True, 'SW14': True}
FLAT = {'RV9': 0.5, 'RV10': 0.5, 'RV11': 0.5, 'RV13': 0.5, 'RV15': 0.5, 'RV12': 0.5, 'RV14': 0.5, 'RV16': 0.5, 'RV8': 0.5}
FADER0 = {'RV1': sc.FADER0}

def tol(value):
    v = value.upper()
    if '0.1%' in v: return 0.001
    if 'C0G' in v: return 0.05
    if 'FILM' in v or 'MKS' in v: return 0.10
    if ' NP' in v or 'MUSE' in v or v.endswith('25V'): return 0.20
    return None

def draw_lines(lines, comps, rnd):
    """Perturb R / C values (by the part's tolerance) and pots (track and gang)."""
    pot = {}
    out = []
    for line in lines:
        t = line.split()
        m = re.match(r'^([RC])s_(R\d+|C\d+) ', line)
        if m and len(t) == 4:
            ref = m.group(2); val = comps.get(ref, '')
            k = tol(val) or (0.01 if ref[0] == 'R' else 0.10)
            out.append(' '.join(t[:3] + [str(float(t[3]) * (1 + rnd.uniform(-k, k)))])); continue
        mp = re.match(r'^Rs_(RV\d+)_(\d)([ab]) ', line)
        if mp and len(t) == 4:
            ref, g = mp.group(1), mp.group(2)
            if ref not in pot: pot[ref] = (1 + rnd.uniform(-0.2, 0.2), {})
            track, gangs = pot[ref]
            gk = gangs.setdefault(g, 1 + (rnd.uniform(-0.1, 0.1) if g != '1' else 0))
            out.append(' '.join(t[:3] + [str(float(t[3]) * track * gk)])); continue
        out.append(line)
    return out

def strip(pos=None, sw=None):
    m = sc.Module('strip', 's', sc.STRIP, pos={**FLAT, **FADER0, **(pos or {})}, sw={**ON, **(sw or {})},
                  plugs={'JB_J1': ('src', 1, 50, False)})
    m.gnd = '0'
    return m

def body(m, rnd):
    comps = {r: c['value'] for r, c in m.b.comps.items()}
    L = draw_lines(m.lines(), comps, rnd)
    out = ['* strip Monte Carlo', sc.OPA_DEF, 'VPB s_PVBUS 0 DC 17', 'VMB s_MVBUS 0 DC -17'] + L
    for bus, rf in (('MIXL', 4.7e3), ('MIXR', 4.7e3)):
        out += [f'E{bus} {bus}_O 0 0 s_{bus} 1e6', f'RF{bus} {bus}_O s_{bus} {rf}']
    nodes = set()
    for line in out:
        t = line.split()
        if t and not line.startswith(('.', '*')) and t[0][0] in 'RCLVEIJX':
            nodes.update(t[1:5] if t[0][0] in 'EX' else t[1:4] if t[0][0] == 'J' else t[1:3])
    nodes -= {'0', 'inp', 'inn', 'out', 'gnd'}
    return out + [f'RLEAK{i} {n} 0 1e9' for i, n in enumerate(sorted(nodes))]

DB = lambda node: f'db(mag(v({node})))'
TESTS = [  # name, pos, sw, control lines (each prints 'x')
 ('PRE, gain detent (dB)', {}, {}, ['ac lin 1 1k 1k', f'let x = {DB("s_PRE")}', 'print x']),
 ('PRE, gain CW (dB)', {'RV9': 1.0}, {}, ['ac lin 1 1k 1k', f'let x = {DB("s_PRE")}', 'print x']),
 ('PRE, gain CCW (dB)', {'RV9': 0.0}, {}, ['ac lin 1 1k 1k', f'let x = {DB("s_PRE")}', 'print x']),
 ('HF full boost @ 12 kHz (dB)', {'RV10': 1.0}, {}, ['ac lin 1 12k 12k', f'let x = {DB("s_PRE")}', 'print x']),
 ('HI-MID boost, freq mid, @ 2.2 kHz (dB)', {'RV11': 1.0}, {}, ['ac lin 1 2.2k 2.2k', f'let x = {DB("s_PRE")}', 'print x']),
 ('LO-MID boost, freq mid, @ 480 Hz (dB)', {'RV13': 1.0}, {}, ['ac lin 1 480 480', f'let x = {DB("s_PRE")}', 'print x']),
 ('LF full boost @ 54 Hz (dB)', {'RV15': 1.0}, {}, ['ac lin 1 54 54', f'let x = {DB("s_PRE")}', 'print x']),
 ('HPF mid, -3 dB (Hz)', {}, {'SW11': True}, ['ac dec 100 5 20k', 'let g = db(v(s_PRE))', 'meas ac x when g=-3 rise=1']),
 ('EQ flat, max deviation 20 Hz-20 kHz (dB)', {}, {}, ['ac dec 20 20 20k', 'let g = db(v(s_PRE))', 'meas ac a max g', 'meas ac b min g', 'let x = max(abs(a), abs(b))', 'print x']),
 ('pan centre, MIX L - MIX R (dB)', {}, {}, ['ac lin 1 1k 1k', f'let x = {DB("MIXL_O")} - {DB("MIXR_O")}', 'print x']),
 ('POST, fader at "0" (dB)', {}, {}, ['ac lin 1 1k 1k', f'let x = {DB("s_POST")}', 'print x']),
]

class NOMINAL:
    uniform = staticmethod(lambda a, b: 0.0)

if __name__ == '__main__':
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    print(f'{n} runs; nominal, then mean / sd / min / max')
    for name, pos, sw, ctl in TESTS:
        m = strip(pos, sw)
        vals = []
        for k in range(n + 1):                             # run 0: nominal (every draw 0)
            rnd = random.Random(1000 + k) if k else NOMINAL
            r, _ = sc.run(body(m, rnd), ctl)
            vals.append(r.get('x'))
        nomv, xs = vals[0], [x for x in vals[1:] if x is not None]
        print(f'  {name:42s} {nomv:8.3f} | {statistics.mean(xs):8.3f} {statistics.pstdev(xs):6.3f} {min(xs):8.3f} {max(xs):8.3f}', flush=True)
