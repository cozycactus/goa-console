"""Group module (group.net) -> ngspice deck with TI's OPA161x macromodel per OPA1612 unit, a Tian probe at every
unit's output (VTI_<u> in series, ITI_<u> injecting into the op-amp side) and a source in series with every + input
(VST_<u>). Everything off the board is modelled here: the bus ribbon (SUB1 / AUX1 with N strip resistors and a lumped
bus capacitance, the other buses as virtual earths), GCANCEL (local 10R + the ribbon to every other 10R), the jack
board (insert jack with its ring normal, return jacks with the R->L normals) and the DRV134 input (10K).
cfg keys (all optional):
  pos {RVn: 0..1}, sw {SWn: bool}, jp set of closed jumpers, nsub, cbus_sub, naux, cbus_aux, rib_l (H, ribbon L
  between header and lumped bus C), fb ('model' | 'short' | (L, R, C)), gc ('stiff' | 'local'),
  ins ('open' unplugged | dict(rs=, cret=, csend=, rin=) plugged, rs=None: return leg open),
  ret ('open' | dict(rs=, cc=)), board (trace C per net from the placement MST, pF/mm), loads {net: F},
  extra [(name, n1, n2, value)], rdiff (add the datasheet's 20k differential input resistance)"""
import os, re, sys, json, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
TI_LIB = os.path.join(os.environ.get('TI_MODELS', HERE), 'OPA161x.LIB')   # TI's model stays out of the repo (licence)
TI56_LIB = os.path.join(os.environ.get('TI_MODELS', HERE), 'OPA1656.LIB')   # the return receivers' followers (G3b)
OPS = {'OPA1612AxD': 'OPA161x', 'OPA1656ID': 'OPA1656'}
# OPA1656_FIT=<models_cd.inc>: the OPA1656 parts use the datasheet-fitted macro OPA1656M instead; the OPA1612s keep TI's model.
# Not needed since 2026-11-04: TI's OPA1656 + OPA161x converge with .options itl1=500 (stabg.py OPTS)
OPA1656_FIT = os.environ.get('OPA1656_FIT')
# OPA1612_SIMPLE=1: the OPA1612 units get the deck's single-pole OPA (40 MHz GBW; no input capacitance or output
# resistance) in place of TI's OPA161x. Only the OPA1656 units' results of such a run mean anything (the 2026-10-28 check of the
# followers on TI's model, before itl1=500 was found).
OPA1612_SIMPLE = os.environ.get('OPA1612_SIMPLE')
sys.path.insert(0, os.path.join(REPO, 'tools'))
from verify import sexp, field

NET = os.path.join(REPO, 'boards', 'group', 'group.net')
comps, pins = {}, {}
tree = sexp(open(NET).read())
for c in next(x for x in tree[1:] if isinstance(x, list) and x[0] == 'components')[1:]:
    comps[field(c, 'ref')] = c
for n in next(x for x in tree[1:] if isinstance(x, list) and x[0] == 'nets')[1:]:
    name = field(n, 'name').lstrip('/')
    for nd in n[1:]:
        if isinstance(nd, list) and nd[0] == 'node': pins[(field(nd, 'ref'), field(nd, 'pin'))] = name

def clean(n):
    n = {'GNDA': '0', 'GNDD': '0'}.get(n, n)
    return re.sub(r'[^A-Za-z0-9_]', lambda m: {'+': 'P', '-': 'M'}.get(m.group(0), '_'), n)

def node(ref, pin):
    if (ref, str(pin)) in REPIN: return REPIN[(ref, str(pin))]
    return clean(pins.get((ref, str(pin)), f'nc_{ref}_{pin}'))

def value(text):
    t = text.split()[0]
    m = re.fullmatch(r'(\d+)([RKkMpnuµ])(\d*)', t) or re.fullmatch(r'(\d+\.?\d*)([RKkMpnuµ])()', t)
    if not m: raise ValueError(text)
    mult = {'R': 1, 'K': 1e3, 'k': 1e3, 'M': 1e6, 'p': 1e-12, 'n': 1e-9, 'u': 1e-6, 'µ': 1e-6}[m.group(2)]
    return float(m.group(1) + ('.' + m.group(3) if m.group(3) else '')) * mult

def law(taper, th):
    a = lambda x: 0.30 * x if x <= 0.5 else 0.15 + 1.70 * (x - 0.5)
    return {'A': a(th), 'B': th}[taper]

TAPER = {'RV1': 'A', 'RV2': 'B', 'RV3': 'A', 'RV4': 'A', 'RV5': 'A'}
libname = lambda c: field(next(x for x in c[1:] if isinstance(x, list) and x[0] == 'libsource'), 'part')
isdnp = lambda c: any(isinstance(x, list) and x[0] == 'property' and field(x, 'name') == 'dnp' for x in c[1:])

ROLE = {'U1A': 'GC buffer', 'U1B': 'sub summer', 'U2A': 'sub re-inverter', 'U2B': 'insert return buffer',
        'U3A': 'sub post-amp', 'U3B': 'pan buffer L', 'U5A': 'pan buffer R', 'U5B': 'aux level buffer',
        'U6A': 'aux summer', 'U6B': 'aux re-inverter', 'U8A': 'return receiver L', 'U8B': 'return receiver R',
        'U9A': 'return level buffer L', 'U9B': 'return level buffer R',
        'U10A': 'return L tip follower', 'U10B': 'return L ring follower', 'U11A': 'return R tip follower',
        'U11B': 'return R ring follower',
        # return 2 (docs/reviews/feature_gaps.md RET1, 2026-10-26): the same circuit
        'U12A': 'return 2 receiver L', 'U12B': 'return 2 receiver R', 'U13A': 'return 2 level buffer L',
        'U13B': 'return 2 level buffer R', 'U14A': 'return 2 L tip follower', 'U14B': 'return 2 L ring follower',
        'U15A': 'return 2 R tip follower', 'U15B': 'return 2 R ring follower'}

def units():
    out = []
    for ref, c in sorted(comps.items()):
        if libname(c) in OPS:
            for u, (p_, m_, o_) in ((1, (3, 2, 1)), (2, (5, 6, 7))):
                if (ref, str(o_)) in pins: out.append((f'{ref}{"AB"[u-1]}', ref, p_, m_, o_))
    return sorted(out, key=lambda t: (int(t[1][1:]), t[0]))
UNITS = {u[0]: u for u in units()}
def outnet(nm): u = UNITS[nm]; return node(u[1], u[4])
def pnet(nm): u = UNITS[nm]; return node(u[1], u[2])
def nnet(nm): u = UNITS[nm]; return node(u[1], u[3])

# placement MST (Manhattan, mm) per net from group.kicad_pcb, for board trace capacitance
MST = {}
_mp = os.path.join(HERE, 'mst_all.json')
if os.path.exists(_mp): MST = json.load(open(_mp))

REPIN = {}
def deck(cfg, ctl=''):
    REPIN.clear(); REPIN.update(cfg.get('repin', {}))
    MSTX = dict(MST); MSTX.update(cfg.get('mst', {}))
    pos, sw, jp = cfg.get('pos', {}), cfg.get('sw', {}), cfg.get('jp', {'JP1', 'JP5'})
    L = ['* generated from ' + NET, f'.include {TI_LIB}', f'.include {OPA1656_FIT or TI56_LIB}',
         '.subckt OPA inp inn out', 'G1 0 n1 inp inn 1', 'R1 n1 0 1e6', 'C1 n1 0 3.98n', 'E1 out 0 n1 0 1', '.ends',
         'VPVA PVA 0 DC 16.8', 'VMVA MVA 0 DC -16.8', 'VPVL PVL 0 DC 16.8', 'VMVL MVL 0 DC -16.8',
         'VPVBUS PVBUS 0 DC 17', 'VMVBUS MVBUS 0 DC -17']
    fb = cfg.get('fb', 'model')
    if fb == 'model': fbp = (0.8e-6, 280, 1e-12)
    elif fb == 'short': fbp = None
    else: fbp = fb
    for ref, c in comps.items():
        if ref.startswith('#') or isdnp(c): continue
        v = field(c, 'value') or ''; lib = libname(c)
        if lib == 'R':
            if node(ref, 1) in ('PVA', 'MVA', 'PVL', 'MVL') or node(ref, 2) in ('PVA', 'MVA', 'PVL', 'MVL'): continue
            L.append(f'R{ref} {node(ref,1)} {node(ref,2)} {value(v)}')
        elif lib in ('C', 'C_Polarized'):
            a, b = node(ref, 1), node(ref, 2)
            if {a, b} & {'PVA', 'MVA', 'PVL', 'MVL'}: continue
            if {a, b} & {'S_OP', 'S_ON', 'A_OP', 'A_ON', 'S_OP_VO', 'S_ON_VO', 'A_OP_VO', 'A_ON_VO'}: continue  # DRV134 outputs
            L.append(f'C{ref} {a} {b} {value(v)}')
        elif lib in ('R_Potentiometer', 'R_Potentiometer_Dual'):
            r = 10e3; x = law(TAPER[ref], pos.get(ref, 0.5))
            for g in ((1, 2, 3), (4, 5, 6)) if lib.endswith('Dual') else ((1, 2, 3),):
                L.append(f'R{ref}_{g[0]}a {node(ref,g[0])} {node(ref,g[1])} {r*x+0.01}')
                L.append(f'R{ref}_{g[0]}b {node(ref,g[1])} {node(ref,g[2])} {r*(1-x)+0.01}')
        elif lib in OPS:
            for u, (p_, m_, o_) in ((1, (3, 2, 1)), (2, (5, 6, 7))):
                if (ref, str(o_)) in pins:
                    nm = f'{ref}{"AB"[u-1]}'
                    if lib == 'OPA1612AxD' and OPA1612_SIMPLE:
                        L.append(f'X{nm} {nm}_pp {node(ref,m_)} {nm}_ox OPA')
                    elif lib == 'OPA1656ID' and OPA1656_FIT:
                        L.append(f'X{nm} {nm}_pp {node(ref,m_)} {nm}_ox {nm}_pp {node(ref,m_)} OPA1656M')
                    else:
                        L.append(f'X{nm} {nm}_pp {node(ref,m_)} PVA MVA {nm}_ox {OPS[lib]}')
                    if cfg.get('rdiff'): L.append(f'RDIF_{nm} {nm}_pp {node(ref,m_)} 20k')
                    L.append(f'VST_{nm} {nm}_pp {node(ref,p_)} DC 0 AC 0 PULSE(0 0 0 1n 1n 1 2)')
                    L.append(f'VTI_{nm} {nm}_ox {node(ref,o_)} DC 0 AC 0')
                    L.append(f'ITI_{nm} 0 {nm}_ox DC 0 AC 0')
        elif lib == 'SW_DPDT_x2':
            on = sw.get(ref, False)
            for c_, t_on, t_off in ((2, 1, 3), (5, 4, 6)):
                a, b = node(ref, c_), node(ref, t_on if on else t_off)
                if 'nc_' in b or 'unconnected' in b: continue
                L.append(f'R{ref}_{c_} {a} {b} 0.01')
        elif lib.startswith('SolderJumper_2'):
            if ref in jp: L.append(f'R{ref} {node(ref,1)} {node(ref,2)} 0.01')
        elif lib == 'FerriteBead':
            a, b = node(ref, 1), node(ref, 2)
            if fbp is None: L.append(f'R{ref} {a} {b} 0.01')
            else:
                fl, fr, fc = fbp
                L += [f'R{ref}dc {a} {ref}_m 0.05', f'L{ref} {ref}_m {b} {fl}', f'R{ref}p {ref}_m {b} {fr}']
                if fc: L.append(f'C{ref}p {ref}_m {b} {fc}')
        elif lib == 'DRV134':        # behavioural: 10 kohm input impedance (datasheet) + 3 pF pin
            L += [f'R{ref}_in {node(ref,4)} 0 10k', f'C{ref}_in {node(ref,4)} 0 3p']
        # LED, NetTie, connectors, flags: not in the AC model
    # ---- off-board: bus ribbon
    ribl = cfg.get('rib_l', 0)
    def busnode(net, cb, nres, rr):
        n = clean(net)
        if ribl:
            L.append(f'LRIB_{n} {n} {n}_far {ribl}'); L.append(f'RRIB_{n} {n} {n}_far 50')  # damping of the ribbon L
            n2 = n + '_far'
        else: n2 = n
        if cb: L.append(f'CBUS_{n} {n2} 0 {cb}')
        if nres: L.append(f'RBUS_{n} {n2} 0 {rr / nres}')
    busnode('SUB1', cfg.get('cbus_sub', 470e-12), cfg.get('nsub', 24), 4.7e3 + 25)
    busnode('AUX1', cfg.get('cbus_aux', 470e-12), cfg.get('naux', 24), 22e3)
    for bus, rf in (('MIXL', 4.7e3), ('MIXR', 4.7e3), ('SUB2', 4.7e3), ('SUB3', 4.7e3), ('SUB4', 4.7e3), ('PFL', 22e3)):
        L += [f'X{bus} 0 {bus} {bus}_O OPA', f'RF{bus} {bus}_O {bus} {rf}', f'CF{bus} {bus}_O {bus} 100p', f'CB{bus} {bus} 0 470p']
    # GCANCEL: local R5 is in the netlist; the ribbon to every other 10R (~27 in parallel)
    gc = cfg.get('gc', 'stiff')
    if gc == 'stiff': L += ['LGC GCANCEL gc_far 0.3u', 'RGC gc_far 0 0.37']
    # ---- jack board
    ins = cfg.get('ins', 'open')
    L.append('CLINK_SEND SUB_SEND 0 5p'); L.append('CLINK_RET SUB_RETRAW 0 5p')
    if ins == 'open': L.append('RJ1_RN SUB_SEND SUB_RETRAW 0.05')
    else:
        L.append(f"CSENDCAB SUB_SEND 0 {ins.get('csend', 470e-12)}"); L.append(f"RSENDIN SUB_SEND 0 {ins.get('rin', 10e3)}")
        if ins.get('rs') is not None:
            L.append(f"RRETSRC SUB_RETRAW 0 {ins['rs']}")
        L.append(f"CRETCAB SUB_RETRAW 0 {ins.get('cret', 470e-12)}")
    # return 1 (J4 / J5) and return 2 (J6 / J7; 'ret2', default as 'ret')
    for j, pre, ret in (('J5', 'Return', cfg.get('ret', 'open')), ('J7', 'Return2', cfg.get('ret2', cfg.get('ret', 'open')))):
        legs = [pre + s for s in ('_LT', '_LR', '_RT', '_RR')]
        for n in legs: L.append(f'CLINK_{n} {n} 0 5p')
        if ret == 'open':      # nothing in either jack: R normalled to L, L open
            L += [f'R{j}_TN {pre}_RT {pre}_LT 0.05', f'R{j}_RN {pre}_RR {pre}_LR 0.05']
        else:                  # both plugged, each leg from rs, cable cc
            for n in legs:
                L += [f"RS_{n} {n} 0 {ret['rs']}", f"CC_{n} {n} 0 {ret.get('cc', 470e-12)}"]
    # ---- board trace capacitance (placement MST x pF/mm)
    if cfg.get('board'):
        k = cfg['board']
        for net, mm in MSTX.items():
            n = clean(net)
            if n in ('0', 'PVA', 'MVA', 'PVL', 'MVL', 'PVBUS', 'MVBUS') or 'unconnected' in net: continue
            if mm > 0: L.append(f'CTR_{n} {n} 0 {k * mm * 1e-12:.4g}')
    for i, (net, val) in enumerate(cfg.get('loads', {}).items()): L.append(f'CLOAD{i} {net} 0 {val}')
    for i, (net, r) in enumerate(cfg.get('src', {}).items()):     # audio drive: 1 V AC through r into net
        L += [f'VAUD{i} aud{i} 0 DC 0 AC 1', f'RAUD{i} aud{i} {net} {r}']
    for nm, a, b, val in cfg.get('extra', ()): L.append(f'{nm} {a} {b} {val}')
    nodes = set()
    for line in L:
        t = line.split()
        if t and t[0][0] in 'RCLVIG' and not line.startswith(('.', '*')): nodes.update(t[1:3])
        if t and t[0][0] == 'X' and not line.startswith(('.', '*')): nodes.update(t[1:-1])
    nodes = {n for n in nodes if not re.fullmatch(r'[-\d.e]+', n)}
    L += [f'RLEAK{i} {n} 0 1e9' for i, n in enumerate(sorted(nodes - {'0', 'inp', 'inn', 'out', 'n1', 'PVA', 'MVA',
                                                                       'PVL', 'MVL', 'PVBUS', 'MVBUS'}))]
    L += [cfg.get('opts', '.options srcsteps=50 gminsteps=50'), ctl, '.end']
    return '\n'.join(L)

def ngspice(text, tag='x', keep=False):
    with tempfile.NamedTemporaryFile('w', suffix='.cir', delete=False, dir=HERE, prefix=tag + '_') as f:
        f.write(text); fn = f.name
    try:
        p = subprocess.run(['ngspice', '-b', fn], capture_output=True, text=True, cwd=HERE, timeout=float(os.environ.get('NG_TIMEOUT', 600)))
        txt = p.stdout + p.stderr
    except subprocess.TimeoutExpired: txt = 'TIMEOUT'
    if not keep: os.unlink(fn)
    return txt
