"""Simulate the channel strip straight from KiCad's exported netlist, so the schematic (not a hand-written
deck) is what gets checked. usage: python3 tools/sim_netlist.py channel_strip.net jack_board.net
The jack board's nets get a JB_ prefix (its ground too) and join the main board only through the ribbon
(CN5 pin n to CN3 pin n), so the source drives J1 and the direct out is read at J5: the link is tested as well.
Each test sets pot positions and switch states, writes an ngspice deck, runs an AC analysis and prints the
result next to the expected value from sim/strip_v4.cir. Exits non-zero if any check fails.
Models: op-amps single-pole 40 MHz (power unit ignored); J112 as in sim/strip.cir; comparator, LEDs, 1N4148
and DNP parts left out; buses are ideal summing amps (4K7 MIX/SUB, 22K AUX/PFL) referenced to ground.
Pot pins: 1 = CCW end, 2 = wiper, 3 = CW end (4/5/6 the same for the second gang). Switch convention:
pin 2 common, latched = 2-1 (and 5-4), unlatched = 2-3 (and 5-6). Solder jumpers: default bridges (1-2)."""
import os, re, sys, math, subprocess, tempfile
sys.path.insert(0, os.path.dirname(__file__))
from verify import sexp, field
import netnames

if len(sys.argv) != 3: raise SystemExit(__doc__)
NET, JNET = sys.argv[1], sys.argv[2]
comps, pins = {}, {}
for path, prefix in ((NET, ''), (JNET, 'JB_')):
    tree = sexp(open(path).read()); rn = netnames.renames(path)     # unlabelled nets of a drawn schematic
    for c in next(x for x in tree[1:] if isinstance(x, list) and x[0] == 'components')[1:]:
        if field(c, 'ref') in comps: raise SystemExit(f"{field(c, 'ref')} is on both boards")
        comps[field(c, 'ref')] = c
    for n in next(x for x in tree[1:] if isinstance(x, list) and x[0] == 'nets')[1:]:
        name = field(n, 'name').lstrip('/'); name = prefix + rn.get(name, name)
        for nd in n[1:]:
            if isinstance(nd, list) and nd[0] == 'node': pins[(field(nd, 'ref'), field(nd, 'pin'))] = name

def node(ref, pin):
    n = pins.get((ref, str(pin)), f'nc_{ref}_{pin}')
    n = {'GNDA': '0', 'GNDD': '0'}.get(n, n)
    return re.sub(r'[^A-Za-z0-9_]', lambda m: {'+': 'P', '-': 'M'}.get(m.group(0), '_'), n)

def value(text):
    """'2K2 1%' -> 2200, '4n7 C0G' -> 4.7e-9, '75R' -> 75, '47u NP 25V' -> 47e-6, '2.2u film' -> 2.2e-6"""
    t = text.split()[0]
    m = re.fullmatch(r'(\d+)([RKkMpnuµ])(\d*)', t) or re.fullmatch(r'(\d+\.?\d*)([RKkMpnuµ])()', t)
    if not m: raise ValueError(text)
    mult = {'R': 1, 'K': 1e3, 'k': 1e3, 'M': 1e6, 'p': 1e-12, 'n': 1e-9, 'u': 1e-6, 'µ': 1e-6}[m.group(2)]
    return float(m.group(1) + ('.' + m.group(3) if m.group(3) else '')) * mult

def law(taper, th):
    a = lambda x: 0.30 * x if x <= 0.5 else 0.15 + 1.70 * (x - 0.5)   # Alpha A: two slopes, 15 % at mid travel
    return {'A': a(th), 'B': th, 'C': 1 - a(1 - th)}[taper]

TAPER = {'RV1': 'A', 'RV2': 'A', 'RV3': 'A', 'RV4': 'A', 'RV5': 'A', 'RV6': 'A', 'RV7': 'A',
         'RV8': 'B', 'RV9': 'B', 'RV10': 'B', 'RV11': 'B', 'RV12': 'A', 'RV13': 'B', 'RV14': 'A', 'RV15': 'B', 'RV16': 'A'}
POTR = {}                                     # pot values other than 10K
DG_RON = 25                                   # DG413 on-resistance, typical (Vishay, +/-15 V)
libname = lambda c: field(next(x for x in c[1:] if isinstance(x, list) and x[0] == 'libsource'), 'part')

def deck(pos, sw, extra=''):
    L = ['* generated from ' + NET, '.subckt OPA inp inn out', 'G1 0 n1 inp inn 1', 'R1 n1 0 1e6', 'C1 n1 0 3.98n',
         'E1 out 0 n1 0 1', '.ends', '.model JMOD NJF(VTO=-2.5 BETA=6m LAMBDA=0.01)',
         'VPVA PVA 0 DC 16.5', 'VMVA MVA 0 DC -16.5', 'VPVL PVL 0 DC 16.5', 'VMVL MVL 0 DC -16.5',
         f"VSRC src {node('J1','S')} DC 0 AC 0.7746", f"RST src {node('J1','T')} 50", f"RSR {node('J1','R')} {node('J1','S')} 50"]
    L += [f'RLINK{p} {node("CN3", p)} {node("CN5", p)} 0.01' for p in range(1, 11)]     # the ribbon
    # logic level of each net: high if the closed PVA2 contacts join it to +5VL (the DG413 control lines)
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
    k = 0
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
                if (ref, str(o_)) in pins: k += 1; L.append(f'X{ref}_{u} {node(ref,p_)} {node(ref,m_)} {node(ref,o_)} OPA')
        elif lib == 'MMBFJ112': L.append(f'J{ref} {node(ref,1)} {node(ref,3)} {node(ref,2)} JMOD')
        elif lib == 'SW_DPDT_x2':
            on = sw.get(ref, False)
            for c_, t_on, t_off in ((2, 1, 3), (5, 4, 6)):
                L.append(f'R{ref}_{c_} {node(ref,c_)} {node(ref, t_on if on else t_off)} 0.01')
        elif lib.startswith('SolderJumper_3'): L.append(f'R{ref} {node(ref,1)} {node(ref,2)} 0.01')
        elif lib.startswith('SolderJumper_2'): L.append(f'R{ref} {node(ref,1)} {node(ref,2)} 0.01')
        elif lib == 'DG413xY':                                   # SW1/SW4 on at logic 1, SW2/SW3 at logic 0
            for in_, d_, s_, no in ((1, 2, 3, True), (8, 7, 6, True), (9, 10, 11, False), (16, 15, 14, False)):
                if (ref, str(in_)) in pins and high(pins[(ref, str(in_))]) == no:
                    L.append(f'R{ref}_{in_} {node(ref,d_)} {node(ref,s_)} {DG_RON}')
        elif lib == 'NetTie_2': pass
        elif lib in ('AudioJack3_SwitchTR', 'AudioJack3'):
            if ref == 'J2':                                      # insert, nothing plugged: ring normal closed
                L.append(f'R{ref}_n {node(ref,"R")} {node(ref,"RN")} 0.01')
    # buses: ideal summing amps referenced to ground
    for bus, rf in (('MIXL', 4.7e3), ('MIXR', 4.7e3), ('SUB1', 4.7e3), ('SUB2', 4.7e3), ('SUB3', 4.7e3), ('SUB4', 4.7e3),
                    ('AUX1', 22e3), ('AUX6', 22e3), ('PFL', 22e3)):
        L += [f'X{bus} 0 {bus} {bus}_O OPA', f'RF{bus} {bus}_O {bus} {rf}']
    nodes = set()
    for line in L:
        t = line.split()
        if t and t[0][0] in 'RCJX' and not line.startswith(('.', '*')):
            nodes.update(t[1:4] if t[0][0] in 'JX' else t[1:3])
    L += [f'RLEAK{i} {n} 0 1e9' for i, n in enumerate(sorted(nodes - {'0', 'inp', 'inn', 'out', 'n1', 'OPA', 'JMOD'}))]
    L += [extra, '.end']
    return '\n'.join(L)

def run(pos, sw, analysis, measures):
    d = deck(pos, sw, '.control\nset noaskquit\n' + analysis + '\n' + '\n'.join(measures) + '\n.endc')
    with tempfile.NamedTemporaryFile('w', suffix='.cir', delete=False) as f: f.write(d); fn = f.name
    out = subprocess.run(['ngspice', '-b', fn], capture_output=True, text=True).stdout
    os.unlink(fn)
    res = {}
    for line in out.splitlines():
        m = re.match(r'^(\w+)\s+=\s+([-+0-9.eE]+)', line)
        if m: res[m.group(1).lower()] = float(m.group(2))
    return res

ON = {'SW4': True, 'SW12': True, 'SW14': True, 'SW5': True}          # channel on, EQ in, PAN on, L-R assigned
TOP = {'RV1': 1.0}
checks = []
def check(name, got, lo, hi, unit='dB'):
    ok = got is not None and lo <= got <= hi
    checks.append(ok); print(f"{'ok  ' if ok else 'FAIL'} {name}: {got if got is None else round(got, 2)} {unit} (expected {lo} .. {hi})")

AC1K = 'ac lin 1 1k 1k'
dbu = lambda n: f'let x_{n} = db(mag(v({n}))/0.7746 + 1e-15)'
r = run(TOP, ON, AC1K, [dbu('PRE'), dbu('POST'), dbu('MIXL_O'), 'print x_PRE', 'print x_POST', 'print x_MIXL_O', 'let ph = ph(v(PRE))*180/pi', 'print ph'])
check('PRE, 0 dBu in, gain at detent, EQ flat', r.get('x_pre'), -0.3, 0.3)
check('PRE phase (tip = hot)', r.get('ph'), -5, 5, 'deg')
check('POST, fader at top (+10 dB post-amp)', r.get('x_post'), 9.5, 10.3)
check('MIX L bus out, pan centre', r.get('x_mixl_o'), 3.3, 4.3)
for th, lo, hi in ((0.0, -15.5, -14.5), (1.0, 14.3, 15.3)):
    r = run({**TOP, 'RV9': th}, ON, AC1K, [dbu('PRE'), 'print x_PRE'])
    check(f'gain pot at {"CCW" if th == 0 else "CW"}', r.get('x_pre'), lo, hi)
r = run(TOP, {**ON, 'SW15': True}, AC1K, ['let ph = ph(v(PRE))*180/pi', 'print ph'])
check('Ø latched: PRE phase', abs(r.get('ph', 0)), 175, 185, 'deg')
for th, lo, hi, label in ((0.5, 80, 95, 'mid rotation'), (0.0, 19, 24, 'CCW'), (1.0, 380, 430, 'CW')):
    r = run({**TOP, 'RV16': th}, {**ON, 'SW11': True}, 'ac dec 100 5 20k',
            ['let g = db(v(PRE)/0.7746)', 'meas ac f3 when g=-3 rise=1', 'meas ac gmax max g'])
    check(f'HPF in, freq {label}: -3 dB frequency at PRE', r.get('f3'), lo, hi, 'Hz')
    check(f'HPF in, freq {label}: no peaking', r.get('gmax'), -0.5, 0.3)
for ref, pos_, at, lo, hi, label in (('RV10', 1, 12e3, 10.5, 12.5, 'HF CW at 12 kHz'), ('RV10', 0, 12e3, -12.5, -10.5, 'HF CCW at 12 kHz'),
                                     ('RV11', 1, 670, 13.5, 15.5, 'HI-MID CW, freq CCW, at 670 Hz'),
                                     ('RV13', 1, 148, 13.5, 15.5, 'LO-MID CW, freq CCW, at 148 Hz'),
                                     ('RV15', 1, 54, 13.3, 15.3, 'LF CW at 54 Hz'), ('RV15', 0, 54, -15.3, -13.3, 'LF CCW at 54 Hz')):
    r = run({**TOP, ref: pos_, 'RV12': 0.0, 'RV14': 0.0}, ON, f'ac lin 1 {at} {at}', [dbu('PRE'), 'print x_PRE'])
    check(label, r.get('x_pre'), lo, hi)
for ref, at, lo, hi, label in (('RV12', 10.5e3, 13.5, 15.5, 'HI-MID CW, freq CW, at 10.5 kHz'),
                               ('RV14', 2.31e3, 13.5, 15.5, 'LO-MID CW, freq CW, at 2.31 kHz')):
    gain = 'RV11' if ref == 'RV12' else 'RV13'                  # boost only the band under test
    r = run({**TOP, gain: 1, ref: 1.0, ('RV14' if ref == 'RV12' else 'RV12'): 0.5}, ON,
            f'ac lin 1 {at} {at}', [dbu('PRE'), 'print x_PRE'])
    check(label, r.get('x_pre'), lo, hi)
for ref, gain, at, label in (('RV12', 'RV11', 2.2e3, 'HI-MID CW, freq at mid rotation (law), at 2.2 kHz'),
                              ('RV14', 'RV13', 480, 'LO-MID CW, freq at mid rotation (law), at 480 Hz')):
    r = run({**TOP, gain: 1, ref: 0.5, ('RV14' if ref == 'RV12' else 'RV12'): 0.5}, ON,
            f'ac lin 1 {at} {at}', [dbu('PRE'), 'print x_PRE'])
    check(label, r.get('x_pre'), 13.5, 15.5)
r = run({**TOP, 'RV10': 1, 'RV11': 1, 'RV13': 1, 'RV15': 1}, {**ON, 'SW12': False}, 'ac dec 20 20 20k',
        ['let g = db(v(PRE)/0.7746)', 'meas ac gmax max g', 'meas ac gmin min g'])
check('EQ out (all bands at full boost): max deviation', max(abs(r.get('gmax', 99)), abs(r.get('gmin', 99))), 0, 0.5)
r = run(TOP, {**ON, 'SW4': False}, AC1K, [dbu('POST'), 'print x_POST'])
check('ON unlatched (muted): POST', r.get('x_post'), -100, -70)
r = run({**TOP, 'RV7': 1.0}, {**ON, 'SW13': True, 'SW10': True}, AC1K, [dbu(node('J5','T')), dbu('AUX6_O'), f"print x_{node('J5','T')}", 'print x_AUX6_O'])
check('DIR + PRE 5-6, aux 6 at top: direct out at J5', r.get('x_' + node('J5','T').lower()), -0.5, 0.5)
check('DIR: aux 6 bus silent', r.get('x_aux6_o'), -400, -60)
r = run({**TOP, 'RV2': 1.0}, {**ON, 'SW8': True}, AC1K, [dbu('AUX1_O'), 'print x_AUX1_O'])
check('PRE 1-2 + aux 1 at top: aux 1 bus out (pre-fader)', r.get('x_aux1_o'), -0.5, 0.5)
r = run({**TOP, 'RV2': 1.0}, ON, AC1K, [dbu('AUX1_O'), 'print x_AUX1_O'])
check('PRE 1-2 off: aux 1 bus out (post-fader, fader at top)', r.get('x_aux1_o'), 9.5, 10.3)
r = run(TOP, {**ON, 'SW6': True}, AC1K, [dbu('SUB1_O'), 'print x_SUB1_O'])
check('PAN on, routed 1-2: SUB 1 out (panned, centre)', r.get('x_sub1_o'), 3.3, 4.3)
r = run(TOP, {**ON, 'SW6': True, 'SW14': False}, AC1K, [dbu('SUB1_O'), 'print x_SUB1_O'])
check('PAN off, routed 1-2: SUB 1 out (POST, unpanned)', r.get('x_sub1_o'), 9.4, 10.3)
r = run(TOP, {**ON, 'SW7': True}, AC1K, [dbu('SUB4_O'), 'print x_SUB4_O'])
check('routed 3-4: SUB 4 out (right side, panned, centre)', r.get('x_sub4_o'), 3.3, 4.3)
r = run(TOP, {**ON, 'SW5': False}, AC1K, [dbu('MIXL_O'), dbu('MIXR_O'), 'print x_MIXL_O', 'print x_MIXR_O'])
check('L-R off: MIX L silent (4K7 end to AGND through the DG413)', r.get('x_mixl_o'), -400, -60)
check('L-R off: MIX R silent', r.get('x_mixr_o'), -400, -60)
r = run(TOP, {**ON, 'SW3': True}, AC1K, [dbu('PFL_O'), 'print x_PFL_O'])
check('PFL latched: PFL bus out (pre-fade)', r.get('x_pfl_o'), -0.5, 0.5)
print(f'{sum(checks)}/{len(checks)} checks passed')
sys.exit(0 if all(checks) else 1)
