"""TI-model stability of U1B, U5A/B, U15A/B with the HPF in (hpf_proposal.md). Copy to sim/review/strip of a tree with
archive/patches/hpf_proposal.patch applied and run there: python3 trial_stab.py <RV16 rotation 0..1> eq|byp  (needs OPA161X_LIB)."""
import sys, json
from stab import run_config
th = float(sys.argv[1]); eq = sys.argv[2] == 'eq'
ON = {'SW4': True, 'SW12': eq, 'SW14': True, 'SW5': True, 'SW11': True}
tag = f'hpf_{sys.argv[1].replace(".", "")}_{sys.argv[2]}'
r = run_config(tag, {'RV1': 1.0, 'RV16': th}, ON, stages=['U1B', 'U5A', 'U5B', 'U15A', 'U15B'])
print(tag, json.dumps({u: (v.get('pm'), v.get('clpk'), v.get('err')) for u, v in r.items()}), flush=True)
