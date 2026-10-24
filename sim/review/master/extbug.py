"""EXT input as generated (R receiver output on the R jack's ring net) vs fixed: L plug only (balanced 1 V diff,
50R per leg) and both plugs (L and R driven separately); levels at the receiver outputs and MON (EXT selected)."""
import numpy as np
from masterdeck import deck
import masterdeck
from tian import ngspice, load, HERE
def run(bug, both, cold_gnd=False):
    masterdeck.pins = masterdeck.pins_raw if bug else masterdeck.pins_fix
    ext = {'L': (1e9, 0)} if not both else {'L': (1e9, 0), 'R': (1e9, 0)}
    extra = [('VLT', 'vlt', '0', 'DC 0 AC 0.5'), ('VLR', 'vlr', '0', 'DC 0 AC 0.5 180'), ('RLT', 'vlt', 'EXT_LT', '50'),
             ('RLR', 'vlr' if not cold_gnd else '0', 'EXT_LR', '50')]
    if both: extra += [('VRT', 'vrt', '0', 'DC 0 AC 0.25'), ('VRR', 'vrr', '0', 'DC 0 AC 0.25 180'), ('RRT', 'vrt', 'EXT_RT', '50'), ('RRR', 'vrr', 'EXT_RR', '50')]
    ro = 'EXT_RR' if bug else 'EXT_RRO'
    ctl = f".control\nset wr_singlescale\nset wr_vecnames\nac lin 1 1k 1k\nwrdata {HERE}/raw/eb.txt v(EXT_RL) v({ro}) v(EXT_LR) v(MON_L) v(MON_R)\n.endc"
    out = ngspice(deck(dict(pos={}, sw={'SW3': True}, ext=ext, extra=extra, ext_bug=bug), ctl), 'eb')
    h, a = load(f'{HERE}/raw/eb.txt')
    vals = [a[0, 1 + 2*i] + 1j*a[0, 2 + 2*i] for i in range(5)]
    return vals
for both in (False, True):
    for cold in (False, True):
        if both and cold: continue
        for bug in (True, False):
            v = run(bug, both, cold)
            lab = ('L+R plugs (L 1 V, R 0.5 V diff)' if both else 'L plug only, R normalled') + (', L source unbalanced (cold to ground)' if cold else '')
            print(f"{'as generated' if bug else 'fixed       '} | {lab}: EXT L out {abs(v[0]):.3f} V, EXT R out {abs(v[1]):.3f} V, "
                  f"L ring node {abs(v[2]):.3f} V (source drives 0.5), MON L {abs(v[3]):.3f}, MON R {abs(v[4]):.3f}")
