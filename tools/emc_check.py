"""Placement-level EMC check of a placed board (no copper needed). Run with KiCad's Python:
  $KPY tools/emc_check.py board.kicad_pcb [more boards ...]
Nets are classified from the board's own pads:
  victims    nets on an op-amp input pin (OPA1612 / OPA1656 / TL072 pins 2, 3, 5, 6), not supplies or grounds;
  aggressors nets on an LED, on a comparator output (LM393 / LM2901), on a DG413 logic input (IN1-IN4), on a
             relay coil (pins 1 / 8; the contacts carry audio), on a small-signal transistor (MMBT3904 / 3906, BCP53), and the logic supply +5VL;
  entries    signal nets on a connector (CNx link / bus headers, Jx jacks), not supplies or grounds.
Prints, per board:
  1. entry runs: each entry net's distance from the connector pad to the first filter part on it (a series R or a
     shunt C to a ground) and to the first active pin (op-amp input or output);
  2. coupling: the closest aggressor pad to each victim net (pad to pad, same or other side);
  3. long aggressors: aggressor nets whose pads span more than 60 mm (switching lines across the board);
  4. supply entry: each bus supply pin to its first series R / reservoir cap.
Distances are pad centre to pad centre in mm. They are placement facts, not field calculations: they show where
routing has no choice but to run sensitive and noisy nets together, or long."""
import math, sys
import pcbnew

SUPPLY = {'+VA', '-VA', '+VL', '-VL', '+VP', '-VP', '+VM', '-VM', '+VBUS', '-VBUS', '+5VL', '+V', '-V'}
GROUND = {'GNDA', 'GNDD', 'GNDM', 'PHONESGND', 'CHASSIS', 'GND'}
OPAMP = ('OPA1612', 'OPA1656', 'TL072')

def load(path):
    b = pcbnew.LoadBoard(path)
    parts, nets = {}, {}
    for f in b.GetFootprints():
        r = f.GetReference(); side = 'B' if f.IsFlipped() else 'F'
        pads = []
        for p in f.Pads():
            n = p.GetNetname().lstrip('/')
            if not n or n.startswith('unconnected'): continue
            xy = (pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y))
            pads.append((p.GetNumber(), n, xy))
            nets.setdefault(n, []).append((r, p.GetNumber(), xy, side))
        parts[r] = dict(value=f.GetValue(), fp=f.GetFPIDAsString(), side=side, pads=pads)
    return parts, nets

def quiet(n): return n in SUPPLY or n in GROUND

def classify(parts):
    vict, agg, entry = {}, {}, {}
    for r, c in parts.items():
        v, fp = c['value'], c['fp']
        for num, n, xy in c['pads']:
            if quiet(n): continue
            if any(v.startswith(o) for o in OPAMP) and num in ('2', '3', '5', '6'): vict.setdefault(n, set()).add(f'{r}.{num}')
            if 'LED' in fp: agg.setdefault(n, set()).add(f'{r} LED')
            if v.startswith(('LM393', 'LM2901')) and num in ('1', '7', '2', '13', '14'):
                if (v.startswith('LM393') and num in ('1', '7')) or (v.startswith('LM2901') and num in ('1', '2', '13', '14')):
                    agg.setdefault(n, set()).add(f'{r}.{num} comparator out')
            if v.startswith('DG413') and num in ('1', '8', '9', '16'): agg.setdefault(n, set()).add(f'{r}.{num} DG413 logic')
            if r.startswith('K') and num in ('1', '8'): agg.setdefault(n, set()).add(f'{r} relay coil')   # G6K: 1 / 8 coil; contacts carry audio
            if v.startswith(('MMBT39', 'BCP53')): agg.setdefault(n, set()).add(f'{r} transistor')
            if r.startswith(('CN', 'J')) and not r.startswith('JP'): entry.setdefault(n, set()).add(f'{r}.{num}')
    agg.setdefault('+5VL', set()).add('logic supply')
    for n in list(vict):
        if n in agg: del vict[n]                 # a comparator input that is also its own output network
    return vict, agg, entry

def mind(a, b):
    best = None
    for p in a:
        for q in b:
            d = math.dist(p[2], q[2])
            if best is None or d < best[0]: best = (d, p, q)
    return best

def report(path):
    parts, nets = load(path)
    vict, agg, entry = classify(parts)
    print(f'=== {path}: {len(parts)} parts, {len(vict)} victim nets, {len(agg)} aggressor nets, {len(entry)} entry nets')
    print('-- 1. entry runs: connector pad -> first filter part / first active pin (mm)')
    for n in sorted(entry):
        pins = [p for p in nets[n] if p[0].startswith(('CN', 'J')) and not p[0].startswith('JP')]
        filt = [p for p in nets[n] if (p[0].startswith('R') and not p[0].startswith('RV')) or
                (p[0].startswith('C') and not p[0].startswith('CN') and any(q[1] in GROUND for q in parts[p[0]]['pads']))]
        act = [p for p in nets[n] if p[0].startswith('U')]
        f, a = mind(pins, filt), mind(pins, act)
        if not f and not a: continue
        print(f'  {n:14s} filter {f[0]:6.1f} ({f[2][0]})' if f else f'  {n:14s} filter   none', end='')
        print(f'   active {a[0]:6.1f} ({a[2][0]}.{a[2][1]})' if a else '   active none')
    print('-- 2. coupling: closest aggressor pad to each victim net (12 closest)')
    rows = []
    for v in vict:
        best = None
        for a in agg:
            m = mind(nets.get(v, []), nets.get(a, []))
            if m and (best is None or m[0] < best[0]): best = (m[0], a, m[1], m[2])
        if best: rows.append((best[0], v, best))
    for d, v, (_, a, p, q) in sorted(rows)[:12]:
        print(f'  {d:5.1f}  {v:16s} ({",".join(sorted(vict[v]))})  <- {a:14s} [{",".join(sorted(agg[a]))}]  at {q[0]}.{q[1]} ({q[3]})')
    print('-- 3. long aggressor nets (pad span > 60 mm)')
    for a in sorted(agg):
        ps = nets.get(a, [])
        if len(ps) < 2: continue
        span = max(math.dist(p[2], q[2]) for p in ps for q in ps)
        if span > 60: print(f'  {a:14s} {span:6.1f} mm  [{",".join(sorted(agg[a]))}]  {sorted({p[0] for p in ps})[:8]}')
    print('-- 4. supply entry: bus pin -> first series R / reservoir (mm)')
    for n in ('+VBUS', '-VBUS', '+V', '-V'):
        pins = [p for p in nets.get(n, []) if p[0].startswith('CN') or p[0].startswith('J')]
        rs = [p for p in nets.get(n, []) if p[0].startswith(('R', 'F', 'L', 'FB'))]
        cs = [p for p in nets.get(n, []) if p[0].startswith('C') and not p[0].startswith('CN')]
        if pins:
            r, c = mind(pins, rs), mind(pins, cs)
            print(f'  {n:6s} series {r[0]:6.1f} ({r[2][0]})' if r else f'  {n:6s} series none', end='')
            print(f'   cap {c[0]:6.1f} ({c[2][0]})' if c else '   cap none')

if __name__ == '__main__':
    for p in sys.argv[1:]: report(p)
