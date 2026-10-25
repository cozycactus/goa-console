"""N1 stability (strip_noise_proposal.md, 2026-10-25): every op-amp unit over the 21 states of configs.py, with the
model set and op-amp assignment given. usage:
  OPA161X_LIB=... python3 n1_stab.py ti built          TI OPA161x everywhere (U16 too): the calibration reference
  OPA_FIT_LIB=... python3 n1_stab.py fit built         datasheet-fitted OPA1612M everywhere, U16 OPA1656M
  OPA_FIT_LIB=... python3 n1_stab.py fit n1            OPA1656M in U1, U5, U6, U7, U12-U16
-> results_n1_<model>_<set>.json"""
import os, sys, json, time
model, which = sys.argv[1], sys.argv[2]
os.environ['OPA_MODEL'] = model
if which == 'n1': os.environ['OPA1656_UNITS'] = 'U1,U5,U6,U7,U12,U13,U14,U15'
from stab import run_config
from configs import CONFIGS
R = {}
for name, (pos, sw, kw) in CONFIGS.items():
    t = time.time()
    R[name] = run_config(f'n1_{model}_{which}_{name}', pos, sw, **kw)
    print(name, round(time.time() - t, 1), 's', flush=True)
json.dump(R, open(f'results_n1_{model}_{which}.json', 'w'), indent=1)
print('done', flush=True)
