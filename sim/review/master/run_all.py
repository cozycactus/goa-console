"""usage: run_all.py FIXSET [cfg1,cfg2,... | all] [unit1,unit2,...]  -> res/<fixset>_<cfg>.json
Configs run in parallel (NJ processes, default 3). Units default to every unit but the phones composite (run_phv.py)."""
import json, sys, time, os
from concurrent.futures import ProcessPoolExecutor
from configs import CONFIGS, NONPH
fix = sys.argv[1]
cfgs = sys.argv[2].split(',') if len(sys.argv) > 2 and sys.argv[2] != 'all' else list(CONFIGS)
units = sys.argv[3].split(',') if len(sys.argv) > 3 else NONPH
os.makedirs('res', exist_ok=True)
def job(c):
    from mstab import run_config
    from configs import CONFIGS
    from fixes import FIXES
    t0 = time.time(); cfg = dict(CONFIGS[c]); f = FIXES[fix]
    for k, v in f.items():
        if k == 'extra': cfg['extra'] = cfg.get('extra', []) + v
        elif k == 'omit': cfg['omit'] = list(cfg.get('omit', [])) + v
        elif k in ('loads', 'pinmove'): cfg[k] = {**cfg.get(k, {}), **v}
        else: cfg[k] = v
    r = run_config(f'{fix}_{c}', cfg, units)
    json.dump(r, open(f'res/{fix}_{c}.json', 'w'), indent=1)
    return c, time.time() - t0, {u: (x.get('pm'), x.get('clpk')) for u, x in r.items()}
if __name__ == '__main__':
    with ProcessPoolExecutor(int(os.environ.get('NJ', '3'))) as ex:
        for c, dt, r in ex.map(job, cfgs):
            print(f'{fix} {c} {dt:.0f}s ' + ' '.join(f'{u}:{p if p is None else round(p, 1)}/{k if k is None else round(k, 2)}' for u, (p, k) in sorted(r.items())), flush=True)
