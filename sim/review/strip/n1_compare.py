"""Compare the N1 stability sweeps (n1_stab.py): per op-amp unit, the worst phase margin over the 21 states and its
state, the worst closed-loop peaking, for TI as built, fitted as built and fitted N1; and how far the fitted macros sit
from TI's models on the as-built strip. usage: python3 n1_compare.py"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
R = {k: json.load(open(os.path.join(HERE, f'results_n1_{k}.json'))) for k in ('ti_built', 'fit_built', 'fit_n1')}
N1 = ('U1', 'U5', 'U6', 'U7', 'U12', 'U13', 'U14', 'U15')

def worst(res, unit, key='pm', low=True):
    vals = [(st[unit][key], name) for name, st in res.items() if unit in st and key in st[unit]]
    if not vals: return None, None
    return min(vals) if low else max(vals)

units = sorted({u for st in R['ti_built'].values() for u in st}, key=lambda u: (int(u[1:-1]), u))
errs = {k: sum(1 for st in r.values() for v in st.values() if 'err' in v) for k, r in R.items()}
print('errors per sweep:', errs)
print(f'{"unit":5s} {"TI built":>16s} {"fit built":>16s} {"fit N1":>16s}  {"fit-TI":>7s}  peaking dB (TI / fit / N1)')
deltas = []
for u in units:
    a, b, c = (worst(R[k], u) for k in ('ti_built', 'fit_built', 'fit_n1'))
    pa, pb, pc = (worst(R[k], u, 'clpk', low=False)[0] for k in ('ti_built', 'fit_built', 'fit_n1'))
    d = b[0] - a[0] if a[0] is not None and b[0] is not None else None
    if d is not None: deltas.append(d)
    mark = ' *' if u[:-1] in N1 else ''
    f = lambda x: f'{x[0]:5.1f} {x[1][:9]:9s}' if x[0] is not None else '   --          '
    print(f'{u:5s} {f(a)} {f(b)} {f(c)}  {d if d is None else round(d, 1):>7}  {pa} / {pb} / {pc}{mark}')
print(f'fitted minus TI, as built: {min(deltas):.1f} .. {max(deltas):.1f} deg (median {sorted(deltas)[len(deltas) // 2]:.1f})')
n1u = [u for u in units if u[:-1] in N1]
w = min((worst(R['fit_n1'], u)[0], u) for u in n1u)
print(f'N1 units, worst fitted margin: {w[0]:.1f} deg ({w[1]}); change from fitted as built per unit:')
for u in n1u:
    print(f'  {u}: {worst(R["fit_built"], u)[0]:.1f} -> {worst(R["fit_n1"], u)[0]:.1f}')

# TI's own models (2026-11-04, n1_stab.py ti u16 / ti n1): as built with U16 on TI's OPA1656, against N1. The states with no operating point
# with TI's models on all units come from the run with U2, U3, U8 single-pole (only its OPA1656 units count)
names = [os.path.join(HERE, f'results_n1_ti_{k}.json') for k in ('u16', 'n1', 'n1_simple')]
if all(os.path.exists(f) for f in names):
    B, M, S = (json.load(open(f)) for f in names)
    filled = 0
    for st, r in S.items():
        for u, v in r.items():
            if 'pm' in v and 'pm' not in M[st].get(u, {}): M[st][u] = v; filled += 1
    miss = [(st, u) for st, r in M.items() for u, v in r.items() if 'pm' not in v]
    print(f"\nTI's models, 21 states: {filled} unit results from the single-pole run, {len(miss)} not measured: {sorted({u for _, u in miss})} in {sorted({s[:3] for s, _ in miss})}")
    print(f'{"unit":5s} {"as built":>16s} {"N1":>16s}  peaking dB')
    for u in units:
        a, b = worst(B, u), worst(M, u)
        print(f'{u:5s} {a[0]:5.1f} {a[1][:9]:9s}  {b[0]:5.1f} {b[1][:9]:9s}  {worst(B, u, "clpk", low=False)[0]} / {worst(M, u, "clpk", low=False)[0]}' + (' *' if u[:-1] in N1 else ''))
