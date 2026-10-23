"""usage: python3 run_all.py <fixset> [tran]  -> results_<fixset>.json"""
import sys, json, time, re
from stab import run_config
from configs import CONFIGS
from fixes import FIXSETS
fx = sys.argv[1] if len(sys.argv) > 1 else 'none'
only = sys.argv[2].split(',') if len(sys.argv) > 2 and sys.argv[2] != '-' else None
R = {}
safe = re.sub(r'[^A-Za-z0-9]', '_', fx)
for name, (pos, sw, kw) in CONFIGS.items():
    if only and name not in only: continue
    t = time.time()
    R[name] = run_config(f'{safe}_{name}', pos, sw, extra=FIXSETS[fx], **kw)
    print(name, round(time.time() - t, 1), 's', flush=True)
json.dump(R, open(f'results_{safe}.json', 'w'), indent=1)
