"""Strip headroom at every op-amp output (2026-10-25): for each setting, the input level at which the first op-amp
output reaches its swing limit, 20 Hz-20 kHz, and which node it is, so an internal node (KHN integrators, the EQ's
inverting stages) that clips before PRE or POST shows up. One strip from the netlists (single-pole op-amps), AC.
Swing limit: +-15.5 V peak (OPA1612 / OPA1656 at +-17 V into >= 2K, about 1.5 V from the rails) = +23.0 dBu.
usage: python3 sim/review/gaps/headroom.py"""
import os, re, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mc import strip, body, NOMINAL
import sim_console as sc

VSW = 15.5
SET = [('unity: gain detent, EQ flat, fader "0"', {}, {}),
       ('fader at the top (+10 dB post-amp)', {'RV1': 1.0}, {}),
       ('gain +15 dB, fader "0"', {'RV9': 1.0}, {}),
       ('gain +15 dB, fader at the top', {'RV9': 1.0, 'RV1': 1.0}, {}),
       ('every EQ band +15 dB, freqs mid, fader "0"', {'RV10': 1, 'RV11': 1, 'RV13': 1, 'RV15': 1}, {}),
       ('EQ +15 dB, HI/LO-MID freqs CCW', {'RV10': 1, 'RV11': 1, 'RV13': 1, 'RV15': 1, 'RV12': 0, 'RV14': 0}, {}),
       ('EQ +15 dB, HI/LO-MID freqs CW', {'RV10': 1, 'RV11': 1, 'RV13': 1, 'RV15': 1, 'RV12': 1, 'RV14': 1}, {}),
       ('HPF in at CW (403 Hz), EQ flat', {'RV16': 1.0}, {'SW11': True}),
       ('DIR on, aux 6 at the top', {'RV7': 1.0}, {'SW13': True, 'SW10': True}),
       ('aux sends at the top, PRE', {f'RV{k}': 1.0 for k in range(2, 8)}, {'SW8': True, 'SW9': True, 'SW10': True})]

def outs(lines):
    return sorted({m.group(1) for l in lines for m in [re.match(r'^Xs_U\d+_\d \S+ \S+ (\S+) \S+ OPA16\d\dN$', l)] if m})

if __name__ == '__main__':
    print(f'swing limit +-{VSW} V peak ({20 * math.log10(VSW / math.sqrt(2) / 0.7746):.1f} dBu); input level that clips first, and where')
    for name, pos, sw in SET:
        m = strip(pos, sw); b = body(m, NOMINAL); nodes = outs(b)
        ctl = ['ac dec 12 20 20k'] + [f'let m{i} = vecmax(mag(v({n})))' for i, n in enumerate(nodes)] + \
              [f'print m{i}' for i in range(len(nodes))]
        r, _ = sc.run(b, ctl)
        g = max((r.get(f'm{i}', 0), n) for i, n in enumerate(nodes))       # input is 1 V peak (AC 1)
        clip = 20 * math.log10(VSW / g[0] / math.sqrt(2) / 0.7746)
        nxt = sorted(((r.get(f'm{i}', 0), n) for i, n in enumerate(nodes)), reverse=True)[1]
        print(f'  {name:44s} clips at {clip:6.1f} dBu in, first at {g[1]} (gain {20 * math.log10(g[0]):5.1f} dB); next {nxt[1]} {20 * math.log10(nxt[0]):5.1f} dB', flush=True)
