"""Load a KiCad netlist (master.net / group.net): comps {ref: dict(value, lib, part, dnp)}, pins {(ref,pin): net},
nets {net: [(ref,pin)]}."""
import os, re, sys
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
sys.path.insert(0, os.path.join(REPO, 'tools'))
from verify import sexp, field

def load(path):
    tree = sexp(open(path).read())
    comps, pins, nets = {}, {}, {}
    for c in next(x for x in tree[1:] if isinstance(x, list) and x[0] == 'components')[1:]:
        ls = next(x for x in c[1:] if isinstance(x, list) and x[0] == 'libsource')
        dnp = any(isinstance(x, list) and x[0] == 'property' and field(x, 'name') == 'dnp' for x in c[1:])
        comps[field(c, 'ref')] = dict(value=field(c, 'value') or '', lib=field(ls, 'lib'), part=field(ls, 'part'),
                                      fp=field(c, 'footprint'), dnp=dnp)
    for n in next(x for x in tree[1:] if isinstance(x, list) and x[0] == 'nets')[1:]:
        name = field(n, 'name').lstrip('/')
        for nd in n[1:]:
            if isinstance(nd, list) and nd[0] == 'node':
                pins[(field(nd, 'ref'), field(nd, 'pin'))] = name
                nets.setdefault(name, []).append((field(nd, 'ref'), field(nd, 'pin')))
    return comps, pins, nets
