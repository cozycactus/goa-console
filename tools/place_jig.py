"""Component placement for the test-jig boards (test_jig_spec.md v0.2). Placement only: no copper.
  KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3
  $KPY tools/place_jig.py      # -> jig_master_stub.kicad_pcb, jig_load_board.kicad_pcb
Bench boards, no panel: connectors on the edges, four M3 corner holes for standoffs. Zones follow the
schematic's functional blocks and decoupling pairs from jig_*_parts.json, written by tools/gen_jig.py.
Engine: placer.py."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from placer import place, PROJ
from verify import sexp, field

def blocks(name):
    d = json.load(open(os.path.join(PROJ, name + '_parts.json')))
    seen, out = set(), []
    for title, refs in d['blocks']:              # a package shared by two blocks stays in the first
        out.append((title.split('  ')[0], [r for r in refs if not (r in seen or seen.add(r))]))
    return dict(out), d['near']

def netlist(name):
    """{ref: {pin: net, 'value': value}}, {net: {refs}} from <name>.net, so layouts follow parts by function."""
    t = sexp(open(os.path.join(PROJ, name + '.net')).read())
    parts = {field(c, 'ref'): {'value': field(c, 'value')}
             for c in next(c for c in t[1:] if isinstance(c, list) and c[0] == 'components')[1:]}
    on = {}
    for n in next(c for c in t[1:] if isinstance(c, list) and c[0] == 'nets')[1:]:
        nm = field(n, 'name').lstrip('/')
        for x in n[1:]:
            if isinstance(x, list) and x[0] == 'node':
                r = field(x, 'ref'); on.setdefault(nm, set()).add(r); parts[r][field(x, 'pin')] = nm
    return parts, on

def corners(w, h, m=4.0): return [(m, m), (w - m, m), (m, h - m), (w - m, h - m)]

# ================================================================ master stub, 160 x 125 mm
W, H = 160.0, 125.0
B, near = blocks('jig_master_stub')
BNC_X = [16 + 18 * k for k in range(6)]          # MIX L, MIX R, SUB 1, AUX 1, AUX 2, PFL
fix = {'CN2': (6.5, 14.0, 0, 'F'),                # ribbon header on the left edge, pins along y
       'J1': (138.0, 7.0, 0, 'F'),                # bench supply terminal, top right
       'CN1': (126.0, 8.0, 0, 'F'),               # ground spade beside it
       'JP1': (62.0, 5.0, 0, 'F'), 'JP2': (80.0, 5.0, 0, 'F'),     # GC REF (3-pin), 22R TIE (2-pin)
       'J8': (127.0, H - 0.3 - 21.02, 0, 'F')}    # MIX L balanced XLR, front edge
for k, x in enumerate(BNC_X):                     # BNC J2..J7, front edge, body to the edge (rot 180)
    fix[f'J{k + 2}'] = (x, H - 0.3 - 33.84, 180, 'F')
PARTS, ON = netlist('jig_master_stub')
for k in range(6):                                # 100R output resistors beside their BNC
    bnc = f'J{k + 2}'; near.update({r: bnc for r in ON[PARTS[bnc]['1']] if r.startswith('R')})
DRV = next(r for r, p in PARTS.items() if p['value'] == 'DRV134')
near[DRV] = 'J8'                                  # DRV134 at the XLR; its caps are in near (gen_jig / drv134())
BAL = [DRV] + sorted((r for r, a in near.items() if a == DRV), key=lambda r: int(r[1:]))
take = lambda name, *drop: [r for r in B[name] if r not in fix and r not in drop]
zones = [('power in', (90, 1, 159, 40), take('POWER IN'), 'F'),
         ('config + GC buffer', (54, 10, 92, 32), take('CONFIG'), 'F'),
         ('bus amps', (14, 14, 159, 72), take('BUS AMPS'), 'F'),
         ('PFL detect', (110, 40, 159, 85), take('PFL DETECT'), 'F', 1.5),     # room for the DO-35s' cathode marks
         ('balanced out (DRV134 at the XLR)', (114, 86, 159, 101), BAL, 'F'),
         ('outputs', (1, 60, 159, 85), take('OUTPUTS', *BAL), 'F'),
         ('test points', (14, 60, 159, 85), take('TEST POINTS'), 'F')]
labels = [(x, 87.2, n, 1.5) for x, n in zip(BNC_X, ('MIX L', 'MIX R', 'SUB 1', 'AUX 1', 'AUX 2', 'PFL'))]
labels += [(127 + 3.8, 101.0, 'MIX L BAL', 1.5), (62.0, 12.5, 'GC REF', 1.2), (62.0, 14.3, '1-2 D  2-3 A', 1.0),
           (80.0, 10.0, 'TIE 22R', 1.2), (138.0 + 5.08, 14.2, '+V   0V   -V', 1.2), (6.5, 62.5, 'RIBBON', 1.2)]
place(os.path.join(PROJ, 'jig_master_stub.net'), os.path.join(PROJ, 'jig_master_stub.kicad_pcb'),
      dict(board=(0, 0, W, H), fix=fix, holes=corners(W, H), hole_value='M3 standoff', zones=zones, near=near,
           labels=labels, attach=True, notes=((20, 'TEST JIG MASTER STUB'), (30, 'BNC + XLR on the front edge'))))

# ================================================================ load board, 120 x 85 mm
W, H = 120.0, 85.0
B, near = blocks('jig_load_board')
BUSES, GROUPS = ('MIX L', 'MIX R', 'SUB 1', 'AUX 1', 'PFL'), ('+1', '+3', '+4', '+12')
COL_X, ROW_Y = [32 + 20 * j for j in range(4)], [24 + 11 * i for i in range(5)]
fix = {'CN1': (6.5, 14.0, 0, 'F'),                # ribbon header on the left edge
       'CN2': (20.0, 8.0, 0, 'F'),                # ground spade
       'J1': (98.0, 7.0, 0, 'F')}                 # dummy wing-load terminal, top right
for i, y in enumerate(ROW_Y):                     # SW1..SW20: bus i, group j; resistor R(2 + 4i + j) beside it
    for j, x in enumerate(COL_X):
        fix[f'SW{1 + 4 * i + j}'] = (x, y, 0, 'F')
        near[f'R{2 + 4 * i + j}'] = f'SW{1 + 4 * i + j}'
take = lambda name: [r for r in B[name] if r not in fix]
zones = [('ribbon + ground', (12, 1, 60, 20), take('RIBBON'), 'F'),
         ('dummy channels', (24, 18, 112, 80), take('DUMMY CHANNELS'), 'F'),
         ('bus capacitance', (100, 20, 119, 80), take('BUS CAPACITANCE'), 'F'),
         ('dummy load', (80, 1, 119, 20), take('DUMMY WING LOAD'), 'F')]
labels = [(19.0, y, n, 1.3) for y, n in zip(ROW_Y, BUSES)] + [(x + 2.0, 17.0, g, 1.3) for x, g in zip(COL_X, GROUPS)]
labels += [(98 + 5.08, 14.2, '+V   0V   -V  LOAD', 1.1), (109.0, 18.0, '+1 nF', 1.2), (6.5, 62.5, 'RIBBON', 1.2)]
place(os.path.join(PROJ, 'jig_load_board.net'), os.path.join(PROJ, 'jig_load_board.kicad_pcb'),
      dict(board=(0, 0, W, H), fix=fix, holes=corners(W, H), hole_value='M3 standoff', zones=zones, near=near,
           labels=labels, attach=True, notes=((20, 'TEST JIG LOAD BOARD'), (30, 'switch up = channels on the bus'))))
