"""10 mV step overshoot of the key stages, as designed vs fix set, at the stress configs."""
import json, sys
from mstab import run_config
from configs import CONFIGS
from fixes import FIXES
U = ['U13A', 'U19A', 'U21A', 'U23A', 'U2B', 'U1A']
fix = sys.argv[1]; cfgs = sys.argv[2].split(',')
for c in cfgs:
    cfg = dict(CONFIGS[c], no_meter=True)
    for k, v in FIXES[fix].items():
        if k == 'extra': cfg['extra'] = cfg.get('extra', []) + v
        elif k == 'omit': cfg['omit'] = list(cfg.get('omit', [])) + v
        elif k == 'loads': cfg['loads'] = dict(cfg.get('loads', {}), **v)
        else: cfg[k] = v
    r = run_config(f'st_{fix}_{c}', cfg, U, tran=True)
    json.dump(r, open(f'res/steps_{fix}_{c}.json', 'w'), indent=1)
    print(fix, c, {u: (r[u].get('pm'), r[u].get('os'), r[u].get('late_pp')) for u in U}, flush=True)
