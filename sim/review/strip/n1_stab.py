"""N1 stability (strip_noise_proposal.md, 2026-10-25): every op-amp unit over the 21 states of configs.py, with the
model set and op-amp assignment given. usage:
  OPA161X_LIB=... python3 n1_stab.py ti built          TI OPA161x everywhere (U16 too): the calibration reference
  OPA_FIT_LIB=... python3 n1_stab.py fit built         datasheet-fitted OPA1612M everywhere, U16 OPA1656M
  OPA_FIT_LIB=... python3 n1_stab.py fit n1            OPA1656M in U1, U5, U6, U7, U12-U16
  OPA161X_LIB=... OPA1656_LIB=... python3 n1_stab.py ti u16     as built on TI's real models: OPA1656 in U16 (since 2026-11-04, stab.py OPTS)
  OPA161X_LIB=... OPA1656_LIB=... python3 n1_stab.py ti n1      TI's OPA1656 in U1, U5, U6, U7, U12-U16
A third argument lists the states to run. OPA1612_SIMPLE=1 (with ti n1): U2, U3, U8 on the deck's single-pole op-amp, for the states that have
no operating point otherwise; only the OPA1656 units' results of such a run mean anything; -> ..._simple.json.
NJ=<n> runs n states at a time. -> results_n1_<model>_<set>.json"""
import os, sys, json, time
from concurrent.futures import ProcessPoolExecutor
model, which = sys.argv[1], sys.argv[2]
os.environ['OPA_MODEL'] = model
if which == 'n1': os.environ['OPA1656_UNITS'] = 'U1,U5,U6,U7,U12,U13,U14,U15'
if which == 'u16': os.environ['OPA1656_UNITS'] = 'U16'
from stab import run_config
from configs import CONFIGS
SUF = '_simple' if os.environ.get('OPA1612_SIMPLE') else ''
NAMES = sys.argv[3].split(',') if len(sys.argv) > 3 else list(CONFIGS)

def job(name):
    pos, sw, kw = CONFIGS[name]
    t = time.time()
    r = run_config(f'n1_{model}_{which}{SUF}_{name}', pos, sw, **kw)
    return name, r, time.time() - t

if __name__ == '__main__':
    R = {}
    with ProcessPoolExecutor(int(os.environ.get('NJ', '1'))) as ex:
        for name, r, dt in ex.map(job, NAMES):
            R[name] = r
            print(name, round(dt, 1), 's', flush=True)
    json.dump(R, open(f'results_n1_{model}_{which}{SUF}.json', 'w'), indent=1)
    print('done', flush=True)
