"""Phones composite variants over pot / load cases. usage: run_phv.py VARIANT [lme-json] [stage]"""
import json, sys
from mstab import run_config
V = {
 'asis': {},
 'cf_drv': dict(omit=['C136', 'C142'], extra=[('CFX1', 'PH_DRVL', 'PH_NL', '100p'), ('CFX2', 'PH_DRVR', 'PH_NR', '100p')]),
 'cf_drv47': dict(omit=['C136', 'C142'], extra=[('CFX1', 'PH_DRVL', 'PH_NL', '47p'), ('CFX2', 'PH_DRVR', 'PH_NR', '47p')]),
 'cf_drv_in22': dict(omit=['C136', 'C142'], extra=[('CFX1', 'PH_DRVL', 'PH_NL', '100p'), ('CFX2', 'PH_DRVR', 'PH_NR', '100p'),
                    ('CIX1', 'PH_INL', '0', '22p'), ('CIX2', 'PH_INR', '0', '22p')]),
 'cf_drv_in10': dict(omit=['C136', 'C142'], extra=[('CFX1', 'PH_DRVL', 'PH_NL', '100p'), ('CFX2', 'PH_DRVR', 'PH_NR', '100p'),
                    ('CIX1', 'PH_INL', '0', '10p'), ('CIX2', 'PH_INR', '0', '10p')]),
 'cf10_pho': dict(omit=['C136', 'C142'], extra=[('CFX1', 'PHO_L', 'PH_NL', '10p'), ('CFX2', 'PHO_R', 'PH_NR', '10p')]),
 'cf22_pho': dict(omit=['C136', 'C142'], extra=[('CFX1', 'PHO_L', 'PH_NL', '22p'), ('CFX2', 'PHO_R', 'PH_NR', '22p')]),
 'cf_drv_r47': dict(omit=['C136', 'C142'], pinmove={('U26', '1'): 'PHDL_O', ('U26', '7'): 'PHDR_O'},
                    extra=[('RSX1', 'PHDL_O', 'PH_DRVL', '47'), ('RSX2', 'PHDR_O', 'PH_DRVR', '47'),
                           ('CFX1', 'PHDL_O', 'PH_NL', '100p'), ('CFX2', 'PHDR_O', 'PH_NR', '100p')]),
}
# R channel as placed: U26B at y 280, U28 (LME) at y 167: 113 mm op-amp -> LME (PH_DRVR) and 113 mm back (PHO_R to the 4K7).
# Trace = 2-section LC (0.6 nH/mm, 0.065 pF/mm per section half)
def trc(a, b, mm, nm):
    L = 0.6e-9 * mm / 2; C = 0.065e-12 * mm / 2
    return [(f'L{nm}1', a, f'{nm}m', f'{L}'), (f'C{nm}1', f'{nm}m', '0', f'{C}'), (f'L{nm}2', f'{nm}m', b, f'{L}'), (f'C{nm}2', b, '0', f'{C}')]
TR = dict(pinmove={('U26', '7'): 'PHDR_O', ('R124', '1'): 'PHO_RF'}, extra=trc('PHDR_O', 'PH_DRVR', 113, 'TD') + trc('PHO_R', 'PHO_RF', 113, 'TF'))
V['asis_trace'] = dict(pinmove=TR['pinmove'], extra=TR['extra'] + [('CFX2', 'PHO_RF', 'PH_NR', '100p')], omit=['C142'])
V['fix_trace'] = dict(pinmove=TR['pinmove'], omit=['C136', 'C142'], extra=TR['extra'] + [('CFX2', 'PHDR_O', 'PH_NR', '100p'), ('CIX2', 'PH_INR', '0', '22p'),
                      ('CFX1', 'PH_DRVL', 'PH_NL', '100p'), ('CIX1', 'PH_INL', '0', '22p')])
var = sys.argv[1]; lme = json.loads(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2] else {}
ST = sys.argv[3].split(',') if len(sys.argv) > 3 else ['U26A']
cases = {}
for p in (0.0, 0.75, 1.0):
    pos = {'RV6': p, 'RV5': 0.75}
    cases[f'pot{p}_32R_220p'] = dict(pos=pos, phones=(32, 220e-12))
    cases[f'pot{p}_32R_1n'] = dict(pos=pos, phones=(32, 1e-9))
    cases[f'pot{p}_300R_220p'] = dict(pos=pos, phones=(300, 220e-12))
    cases[f'pot{p}_open'] = dict(pos=pos, phones=(None, 0))
    cases[f'pot{p}_K6off'] = dict(pos=pos, phones=(32, 220e-12), relays=False)
res = {}; worst = None
for k, c in cases.items():
    c = dict(c, **V[var]); 
    if lme: c['lme'] = lme
    tag = f'phv_{var}_{k}'.replace('.', 'p')
    r = run_config(tag, c, ST); res[k] = r
    for s in ST:
        x = r[s]
        if worst is None or x.get('pm', -999) < worst[0]: worst = (x.get('pm', -999), k, s)
    print(f'{var:12s} {k:18s}', '  '.join(f"{s}: pm {r[s].get('pm')} fc {r[s].get('fc')} n{r[s].get('ncross')} clpk {r[s].get('clpk')}@{r[s].get('fclpk')} gm {r[s].get('gm')}" for s in ST), flush=True)
print('WORST', var, lme, worst)
json.dump(res, open(f'res_phv_{var}{"_lme" if lme else ""}.json', 'w'), indent=1)
