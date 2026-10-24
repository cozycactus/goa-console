"""Peak-mode readings: as designed (follower on M_PK) vs follower on M_PK1 (diode cathode, before the 1K) with 1K / 220R.
usage: meterburst2.py MODEL"""
import sys, numpy as np
from metertran import meter_deck
from tian import ngspice, load, HERE
tl = sys.argv[1]
VAR = sys.argv[2].split(',') if len(sys.argv) > 2 else ['asis', 'pk1_r1k', 'pk1_r220']
from meterstab import apply_var
import masterdeck
def run(var, src, tstop):
    masterdeck_pins = dict(masterdeck.pins_fix)
    cfg_extra = []
    d = meter_deck(tl, 'PK', 0.16, src, tstop, step='0.5u')
    d = d.replace('\n.options', apply_var('', var) + '\n.options', 1) if 'cf' in var else d
    if 'bat' in var:
        d = d.replace('DD25 ML_U3O ML_PK1 D1N4148', 'DD25 ML_U3O ML_PK1 DBAT').replace('DD26 ML_N4 ML_U3O D1N4148', 'DD26 ML_N4 ML_U3O DBAT')
        d = d.replace('\n.options', '\n.model DBAT D(IS=2e-7 N=1.04 RS=2.5 CJO=10p BV=30)\n.options', 1)
    if 'u3opa' in var:
        import masterdeck as md
        d = d.replace('\n.options', f'\n.include {md.M}/OPA1656.LIB\n.options', 1)
        d = '\n'.join((l.rsplit(' ', 1)[0] + ' OPA1656') if l.startswith('XU30A ') else l for l in d.splitlines())
    for p in var.split('_'):
        if p == 'pk1': d = d.replace('RJP1 ML_PK ML_JSEL 0.01', 'RJP1 ML_PK1 ML_JSEL 0.01')
        elif p.startswith('r'):
            import re; d = re.sub(r'^(R\S+ ML_PK1 ML_PK) 1000\.0$', r'\g<1> ' + p[1:], d, flags=re.M)
    out = ngspice(d, 'mb2')
    h, a = load(f'{HERE}/raw/mtr.txt'); return a
for f, amp, dur in ((1e3, 1.0, 5e-3), (1e3, 0.1, 5e-3), (1e3, 1.0, 10e-3), (10e3, 1.0, 2e-3), (10e3, 0.1, 2e-3), (10e3, 0.1, 20e-3), (1e3, 0.1, 50e-3)):
    src = f'{amp}*sin(2*pi*{f}*(time-1m))*(time>1m)*(time<{1e-3+dur})'
    line = f'{f/1e3:4.0f} kHz {amp:4.1f} V {dur*1e3:3.0f} ms {tl:5s}:'
    for var in VAR:
        try:
            a = run(var, src, 1e-3 + dur + 2e-3)
            t, det, x2 = a[:, 0], a[:, 1], a[:, 3]
            rd = det[t > 1e-3 + dur + 0.2e-3].max(); tp = x2.max()
            line += f'  {var} {20*np.log10(rd/tp):+.2f} dB'
        except Exception as e: line += f'  {var} ERR'
    print(line, flush=True)
