import json, sys
from groupdeck import ROLE
R = json.load(open(sys.argv[1]))
units = sorted({u for r in R.values() for u in r}, key=lambda u: (int(u[1:-1]), u))
for u in units:
    rows = [(r[u].get('pm', 999), nm, r[u]) for nm, r in R.items() if u in r and 'pm' in r[u]]
    lo = min(rows); hi = max(rows)
    pk = max(rows, key=lambda x: x[2].get('clpk', -99)); ng = max(rows, key=lambda x: x[2].get('ngpk', -99))
    os_ = max(rows, key=lambda x: x[2].get('os', -99))
    gm = min(rows, key=lambda x: x[2].get('gm', 99))
    print(f"{u} {ROLE[u]:22s} PM {lo[0]:6.1f}..{hi[0]:6.1f} (min @ {lo[1]}, fc {lo[2].get('fc')} MHz) | CLpk {pk[2]['clpk']:5.2f} dB @{pk[2]['fclpk']} MHz [{pk[1]}] | NGpk {ng[2]['ngpk']:5.2f} | GM {gm[2].get('gm')} | OS {os_[2].get('os')}% [{os_[1]}]")
