"""Variant of tools/sim_netlist.py (deck() and its helpers, copied) that instantiates TI's OPA161x macromodel
per OPA1612 unit (+/-17 V) with a Tian probe (VTI_<unit> in series with the output, ITI_<unit> into the
output pin) and a step/AC source in series with the + input (VST_<unit>). All probes are idle (0) unless
switched on with alter in the .control section. extra = list of (name, n1, n2, value) parts added to the deck
(proposed feedback caps). model='sp' gives the original single-pole subckt for comparison."""
import os, re, sys, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
# TI's OPA161x PSpice macromodel (SBOM396G, ti.com): its licence keeps it out of the repo; point OPA161X_LIB at it
TI_LIB = os.environ.get('OPA161X_LIB', os.path.join(HERE, 'OPA161x.LIB'))
# OPA1656_UNITS=U1,U5,...: those packages use TI's OPA1656 model instead (OPA1656_LIB points at it; same pinout)
OPA1656_LIB = os.environ.get('OPA1656_LIB', os.path.join(HERE, 'OPA1656.LIB'))
OPA1656_UNITS = set(filter(None, os.environ.get('OPA1656_UNITS', '').split(',')))
sys.path.insert(0, os.path.join(REPO, 'tools'))
from verify import sexp, field

NET, JNET = os.path.join(REPO, 'channel_strip.net'), os.path.join(REPO, 'jack_board.net')
comps, pins = {}, {}
for path, prefix in ((NET, ''), (JNET, 'JB_')):
    tree = sexp(open(path).read())
    for c in next(x for x in tree[1:] if isinstance(x, list) and x[0] == 'components')[1:]:
        if field(c, 'ref') in comps: raise SystemExit(f"{field(c, 'ref')} is on both boards")
        comps[field(c, 'ref')] = c
    for n in next(x for x in tree[1:] if isinstance(x, list) and x[0] == 'nets')[1:]:
        name = prefix + field(n, 'name').lstrip('/')
        for nd in n[1:]:
            if isinstance(nd, list) and nd[0] == 'node': pins[(field(nd, 'ref'), field(nd, 'pin'))] = name

def node(ref, pin):
    n = pins.get((ref, str(pin)), f'nc_{ref}_{pin}')
    n = {'GNDA': '0', 'GNDD': '0'}.get(n, n)
    return re.sub(r'[^A-Za-z0-9_]', lambda m: {'+': 'P', '-': 'M'}.get(m.group(0), '_'), n)

def value(text):
    t = text.split()[0]
    m = re.fullmatch(r'(\d+)([RKkMpnuµ])(\d*)', t) or re.fullmatch(r'(\d+\.?\d*)([RKkMpnuµ])()', t)
    if not m: raise ValueError(text)
    mult = {'R': 1, 'K': 1e3, 'k': 1e3, 'M': 1e6, 'p': 1e-12, 'n': 1e-9, 'u': 1e-6, 'µ': 1e-6}[m.group(2)]
    return float(m.group(1) + ('.' + m.group(3) if m.group(3) else '')) * mult

def law(taper, th):
    a = lambda x: 0.30 * x if x <= 0.5 else 0.15 + 1.70 * (x - 0.5)
    return {'A': a(th), 'B': th, 'C': 1 - a(1 - th)}[taper]

TAPER = {'RV1': 'A', 'RV2': 'A', 'RV3': 'A', 'RV4': 'A', 'RV5': 'A', 'RV6': 'A', 'RV7': 'A',
         'RV8': 'B', 'RV9': 'B', 'RV10': 'B', 'RV11': 'B', 'RV12': 'A', 'RV13': 'B', 'RV14': 'A', 'RV15': 'B'}
POTR = {}
DG_RON = 25
libname = lambda c: field(next(x for x in c[1:] if isinstance(x, list) and x[0] == 'libsource'), 'part')

def units():
    out = []
    for ref, c in sorted(comps.items()):
        if libname(c) == 'OPA1612AxD':
            for u, (p_, m_, o_) in ((1, (3, 2, 1)), (2, (5, 6, 7))):
                if (ref, str(o_)) in pins: out.append((f'{ref}{"AB"[u-1]}', ref, p_, m_, o_))
    return sorted(out, key=lambda t: (int(t[1][1:]), t[0]))

def deck(pos, sw, extra_ctl='', model='ti', extra=(), src='50', loads=()):
    L = ['* generated from ' + NET, '.subckt OPA inp inn out', 'G1 0 n1 inp inn 1', 'R1 n1 0 1e6', 'C1 n1 0 3.98n',
         'E1 out 0 n1 0 1', '.ends', '.model JMOD NJF(VTO=-2.5 BETA=6m LAMBDA=0.01)',
         'VPVA PVA 0 DC 16.5', 'VMVA MVA 0 DC -16.5', 'VPVL PVL 0 DC 16.5', 'VMVL MVL 0 DC -16.5',
         'VCC17 vcc17 0 DC 17', 'VEE17 vee17 0 DC -17']
    if model == 'ti': L.insert(1, f'.include {TI_LIB}')
    if model == 'ti' and OPA1656_UNITS: L.insert(2, f'.include {OPA1656_LIB}')   # after OPA161x: the libraries share global model names
    if src == 'open':     # nothing plugged: the jack's tip/ring left to the jack board (C8/C9, R10)
        L += [f"VSRC src 0 DC 0 AC 0"]
    else:
        L += [f"VSRC src {node('J1','S')} DC 0 AC 0", f"RST src {node('J1','T')} {src}", f"RSR {node('J1','R')} {node('J1','S')} {src}"]
    L += [f'RLINK{p} {node("CN3", p)} {node("CN5", p)} 0.01' for p in range(1, 11)]
    group = {}
    def root(n):
        while group.setdefault(n, n) != n: n = group[n]
        return n
    for ref, c in comps.items():
        if libname(c) == 'SW_DPDT_x2':
            on = sw.get(ref, False)
            for c_, t_on, t_off in ((2, 1, 3), (5, 4, 6)):
                a, b = pins.get((ref, str(c_))), pins.get((ref, str(t_on if on else t_off)))
                if a and b: group[root(a)] = root(b)
    high = lambda n: n is not None and root(n) == root('+5VL')
    for ref, c in comps.items():
        if ref.startswith('#') or any(isinstance(x, list) and x[0] == 'property' and field(x, 'name') == 'dnp' for x in c[1:]): continue
        v = field(c, 'value') or ''; lib = libname(c)
        if lib == 'R':   L.append(f'R{ref} {node(ref,1)} {node(ref,2)} {value(v)}')
        elif lib in ('C', 'C_Polarized'): L.append(f'C{ref} {node(ref,1)} {node(ref,2)} {value(v)}')
        elif lib in ('R_Potentiometer', 'R_Potentiometer_Dual'):
            r = POTR.get(ref, 10e3); x = law(TAPER[ref], pos.get(ref, 0.5))
            for g in ((1, 2, 3), (4, 5, 6)) if lib.endswith('Dual') else ((1, 2, 3),):
                L.append(f'R{ref}_{g[0]}a {node(ref,g[0])} {node(ref,g[1])} {r*x+0.01}')
                L.append(f'R{ref}_{g[0]}b {node(ref,g[1])} {node(ref,g[2])} {r*(1-x)+0.01}')
        elif lib == 'OPA1612AxD':
            for u, (p_, m_, o_) in ((1, (3, 2, 1)), (2, (5, 6, 7))):
                if (ref, str(o_)) in pins:
                    nm = f'{ref}{"AB"[u-1]}'
                    if model == 'ti':
                        L.append(f'X{nm} {nm}_pp {node(ref,m_)} vcc17 vee17 {nm}_ox {"OPA1656" if ref in OPA1656_UNITS else "OPA161x"}')
                    else:
                        L.append(f'X{nm} {nm}_pp {node(ref,m_)} {nm}_ox OPA')
                    L.append(f'VST_{nm} {nm}_pp {node(ref,p_)} DC 0 AC 0 PULSE(0 0 0 1n 1n 1 2)')
                    L.append(f'VTI_{nm} {nm}_ox {node(ref,o_)} DC 0 AC 0')
                    L.append(f'ITI_{nm} 0 {nm}_ox DC 0 AC 0')
        elif lib == 'MMBFJ112': L.append(f'J{ref} {node(ref,1)} {node(ref,3)} {node(ref,2)} JMOD')
        elif lib == 'SW_DPDT_x2':
            on = sw.get(ref, False)
            for c_, t_on, t_off in ((2, 1, 3), (5, 4, 6)):
                L.append(f'R{ref}_{c_} {node(ref,c_)} {node(ref, t_on if on else t_off)} 0.01')
        elif lib.startswith('SolderJumper_3'): L.append(f'R{ref} {node(ref,1)} {node(ref,2)} 0.01')
        elif lib.startswith('SolderJumper_2'): L.append(f'R{ref} {node(ref,1)} {node(ref,2)} 0.01')
        elif lib == 'DG413xY':
            for in_, d_, s_, no in ((1, 2, 3, True), (8, 7, 6, True), (9, 10, 11, False), (16, 15, 14, False)):
                if (ref, str(in_)) in pins and high(pins[(ref, str(in_))]) == no:
                    L.append(f'R{ref}_{in_} {node(ref,d_)} {node(ref,s_)} {DG_RON}')
        elif lib == 'NetTie_2': pass
        elif lib in ('AudioJack3_SwitchTR', 'AudioJack3'):
            if ref == 'J2':
                L.append(f'R{ref}_n {node(ref,"R")} {node(ref,"RN")} 0.01')
    for nm, a, b, val in extra: L.append(f'{nm} {a} {b} {val}')
    for i, (a, val) in enumerate(loads): L.append(f'CLOAD{i} {a} 0 {val}')
    for bus, rf in (('MIXL', 4.7e3), ('MIXR', 4.7e3), ('SUB1', 4.7e3), ('SUB2', 4.7e3), ('SUB3', 4.7e3), ('SUB4', 4.7e3),
                    ('AUX1', 22e3), ('AUX6', 22e3), ('PFL', 22e3)):
        L += [f'X{bus} 0 {bus} {bus}_O OPA', f'RF{bus} {bus}_O {bus} {rf}']
    nodes = set()
    for line in L:
        t = line.split()
        if t and t[0][0] in 'RCJXVI' and not line.startswith(('.', '*')):
            nodes.update(t[1:4] if t[0][0] == 'J' else t[1:-1] if t[0][0] == 'X' else t[1:3])
    nodes = {n for n in nodes if not n.replace('.', '').replace('e', '').replace('-', '').isdigit()}
    L += [f'RLEAK{i} {n} 0 1e9' for i, n in enumerate(sorted(nodes - {'0', 'inp', 'inn', 'out', 'n1', 'OPA', 'JMOD', 'OPA161x', 'OPA1656'}))]
    L += ['.options srcsteps=50 gminsteps=50', extra_ctl, '.end']
    return '\n'.join(L)

def ngspice(deck_text, tag='x', keep=False):
    with tempfile.NamedTemporaryFile('w', suffix='.cir', delete=False, dir=HERE, prefix=tag + '_') as f:
        f.write(deck_text); fn = f.name
    p = subprocess.run(['ngspice', '-b', fn], capture_output=True, text=True, cwd=HERE)
    if not keep: os.unlink(fn)
    return p.stdout + p.stderr
