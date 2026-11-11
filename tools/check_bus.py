"""The motherloom pinout on every board that carries it, pin by pin against the Delta map (docs/decisions_summary.md, Bus decision):
  python3 tools/check_bus.py channel_strip.net group.net master.net jig_master_stub.net
Each 2x17 bus header (value 'Bus ...') must put the right net on every pin: even 2-16 GNDA; 9 / 11 / 13 / 15 SUB4..1;
17 MIX R, 18 MIX L; 20-25 AUX6, AUX5, AUX4, AUX3, AUX1, AUX2; 26 GCANCEL; 27 PFL; 29 PFL DET; 30-31 -V; 32-34 +V;
1 / 3 / 5 / 7 (reserved for SUB 5-8), 19 and 28 unconnected (the master joins its two wings on them as SPAREn, 28 as
PFLN). A board that doesn't use a bus leaves the pin open (the group's AUX 5 / 6) or, on the jig stub, on its AGND
stand-in. The generators' header dicts are written by hand (gen.py, gen_group.py, gen_master.py, gen_jig.py) and
sim_netlist / sim_console join the buses by name, so a slip in one dict would pass every other check. Exits 1 on any
wrong pin."""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verify import sexp, field

MAP = {9: 'SUB4', 11: 'SUB3', 13: 'SUB2', 15: 'SUB1', 17: 'MIXR', 18: 'MIXL', 20: 'AUX6', 21: 'AUX5', 22: 'AUX4',
       23: 'AUX3', 24: 'AUX1', 25: 'AUX2', 26: 'GCANCEL', 27: 'PFL', 29: 'PFLDET'}
MAP.update({k: 'GNDA' for k in range(2, 17, 2)})
MAP.update({k: '-VBUS' for k in (30, 31)}); MAP.update({k: '+VBUS' for k in (32, 33, 34)})
OPEN = {1, 3, 5, 7, 19, 28}
BUSES = {n for n in MAP.values() if n not in ('GNDA', '-VBUS', '+VBUS')}

def nc(name): return name is None or name == 'NC' or name.startswith('unconnected-')

def check(path):
    tree = sexp(open(path).read()); bad = []
    comps = {field(c, 'ref'): field(c, 'value') or '' for c in next(x for x in tree[1:] if isinstance(x, list) and x[0] == 'components')[1:]}
    pins = {}
    for n in next(x for x in tree[1:] if isinstance(x, list) and x[0] == 'nets')[1:]:
        for nd in n[1:]:
            if isinstance(nd, list) and nd[0] == 'node': pins[(field(nd, 'ref'), field(nd, 'pin'))] = field(n, 'name').lstrip('/')
    headers = sorted(r for r, v in comps.items() if r.startswith('CN') and v.startswith('Bus'))
    master, jig = 'master' in os.path.basename(path), 'jig' in os.path.basename(path)
    for cn in headers:
        for p in range(1, 35):
            got = pins.get((cn, str(p)))
            if p in OPEN:
                ok = nc(got) or (master and re.fullmatch(r'SPARE\d+|PFLN', got or ''))
            else:
                want = MAP[p]
                ok = got == want or (master and re.fullmatch(re.escape(want) + r'_[LR]', got or ''))
                if not ok and want in BUSES: ok = nc(got) or (jig and got == 'GNDA')     # a bus the board doesn't use
            if not ok: bad.append(f'{cn} pin {p}: {got} (want {MAP.get(p, "open")})')
        print(f'{os.path.basename(path):22s} {cn}: {"ok" if not any(b.startswith(cn + " ") for b in bad) else "WRONG"}')
    if not headers: bad.append('no bus header (value "Bus ...") found')
    for b in bad: print('  ' + b)
    return not bad

if __name__ == '__main__':
    ok = all([check(p) for p in sys.argv[1:]])
    print('bus headers:', 'all pins as the Delta map' if ok else 'WRONG PINS')
    sys.exit(0 if ok else 1)
