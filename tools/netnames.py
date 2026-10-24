"""Intended names for unlabelled nets. A drawn schematic (tools/schdraw.py) labels a net only where it leaves its
drawing, so KiCad names the others Net-(...). Such a net gets its name back from <board>_intended.json (written by
the generator next to the schematic) when it holds exactly that net's pins. Used by the netlist readers (verify.py,
sim_netlist.py, sim_console.py, sim/review/strip/stripdeck.py)."""
import collections, json, os, re


def renames(net_path, nets=None):
    """{auto name: intended name} for the netlist at net_path. nets: {name: {'REF.PIN', ...}} if already parsed."""
    want_path = re.sub(r'\.net$', '_intended.json', net_path)
    if not os.path.exists(want_path): return {}
    want = json.load(open(want_path))
    if nets is None:
        from verify import sexp, field
        tree = sexp(open(net_path).read()); nets = {}
        for n in next(c for c in tree[1:] if isinstance(c, list) and c[0] == 'nets')[1:]:
            nets[field(n, 'name').lstrip('/')] = {f"{field(x, 'ref')}.{field(x, 'pin')}" for x in n[1:]
                                                  if isinstance(x, list) and x[0] == 'node'}
    by_pins = collections.defaultdict(set)
    for k, n in want.items():
        if n != 'NC' and not k.startswith('#'): by_pins[n].add(k)
    lookup = {frozenset(v): n for n, v in by_pins.items()}
    return {n: lookup[frozenset(p)] for n, p in nets.items() if n.startswith('Net-(') and frozenset(p) in lookup}
