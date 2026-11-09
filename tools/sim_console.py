"""Simulate the whole console from the generated netlists: 24 strips, 4 group modules and the master module, each
with its jack board, joined by the 34-way motherloom ribbon. usage: python3 tools/sim_console.py [check ...]
(no argument: every check; `--list` prints their names). Exits non-zero if a check fails.

Model (console_architecture.md 2, master_section_spec.md 24-26):
- Each module is flattened from its own netlist (channel_strip.net + jack_board.net, group.net + group_jack_board.net,
  master.net + master_jack_board.net); a jack board joins its main board only through its link header, pin for pin.
- Ground: every module has its own local ground node (GNDA = GNDD = GNDM on that module); the master's star (CN1) is
  the global 0 V. A module's ground reaches the star through the ribbon's eight ground conductors (pins 2-16) and its
  6.3 mm spade wire (14 AWG under the motherloom, its real length: SPADE_WIRE). Op-amp outputs, DRV134s and buffers
  are referenced to their module's ground, so signal currents return through the real ground paths and GCANCEL
  (pin 26) has something to cancel.
- Ribbon: the master sits in the middle; each wing runs master header -> group, group, strip 1 ... strip 12. Per
  conductor and 41 mm segment (8 HP): 28 AWG resistance plus inductance, and capacitance to the next conductor
  (ribbon conductor = pin number). Contacts 20 mOhm.
- Power: +-17 V at the master's J1, the PTCs, the ribbon's power conductors and each module's own filters.
- Op-amps: single-pole (OPA1612 40 MHz, OPA1656 53 MHz) with datasheet voltage and current noise; DRV134 a +-1
  differential driver on its Sense nodes (10K input); LME49600 a buffer; relays in their energised state (mute
  released). Left out: comparators, LEDs, diodes, transistors and the meter detectors (each meter feed sees its
  6.7 kOhm virtual-earth load instead). DG413s follow their logic: the strips' from the PVA2 contacts on +5VL, the
  master's PFL switcher from whether any PFL / AFL key is latched.
Stability is not checked here (single-pole models): it is done per module with TI's models (sim/review/)."""
import os, re, sys, math, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verify import sexp, field
import netnames

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
GROUNDS = {'GNDA', 'GNDD', 'GNDM', 'PHONESGND', 'CHASSIS'}
OMIT = {'LED', '1N4148', 'BZX84Cxx', 'BAT54W', 'D_Zener', 'D_Schottky', 'LM393', 'LM2901', 'MMBT3904', 'BCP53',
        'TL072', 'NetTie_2', 'Screw_Terminal_01x07', 'R_Potentiometer_Trim'}
FADER0 = 0.5 + (10 ** (-10 / 20) - 0.15) / 1.7       # A-law position of the fader's "0" mark (-10 dB, then +10 dB)

def load(path):
    tree = sexp(open(path).read()); comps, pins = {}, {}; rn = netnames.renames(path)   # drawn schematics' unlabelled nets
    for c in next(x for x in tree[1:] if isinstance(x, list) and x[0] == 'components')[1:]:
        ls = next(x for x in c[1:] if isinstance(x, list) and x[0] == 'libsource')
        dnp = any(isinstance(x, list) and x[0] == 'property' and field(x, 'name') == 'dnp' for x in c[1:])
        comps[field(c, 'ref')] = dict(value=field(c, 'value') or '', lib=field(ls, 'part'), dnp=dnp)
    for n in next(x for x in tree[1:] if isinstance(x, list) and x[0] == 'nets')[1:]:
        for nd in n[1:]:
            if isinstance(nd, list) and nd[0] == 'node':
                nm = field(n, 'name').lstrip('/'); pins[(field(nd, 'ref'), field(nd, 'pin'))] = rn.get(nm, nm)
    return comps, pins

def value(text):
    t = text.split()[0]
    m = re.fullmatch(r'(\d+)([RKkMpnuµ])(\d*)', t) or re.fullmatch(r'(\d+\.?\d*)([RKkMpnuµ])()', t)
    if not m: raise ValueError(text)
    mult = {'R': 1, 'K': 1e3, 'k': 1e3, 'M': 1e6, 'p': 1e-12, 'n': 1e-9, 'u': 1e-6, 'µ': 1e-6}[m.group(2)]
    return float(m.group(1) + ('.' + m.group(3) if m.group(3) else '')) * mult

def law(lin, x):
    if lin: return x
    return 0.30 * x if x <= 0.5 else 0.15 + 1.70 * (x - 0.5)      # Alpha / Bourns A: two slopes, 15 % at mid travel

class Board:
    """A module's main board and jack board as one part list; jack-board refs and nets get a JB_ prefix."""
    def __init__(self, main, jack):
        self.comps, self.pins = load(os.path.join(ROOT, main))
        jc, jp = load(os.path.join(ROOT, jack))
        for r, c in jc.items(): self.comps['JB_' + r] = c
        for (r, p), n in jp.items(): self.pins[('JB_' + r, p)] = n if n in GROUNDS else 'JB_' + n
        link = [r for r, c in self.comps.items() if 'link' in c['value'].lower()]
        side = lambda r: self.comps[r]['value'].lower().split('board link')[1]  # 'Jack / Main board link [2] 2xN'
        self.link = [(m, j) for m in link if not m.startswith('JB_') for j in link
                     if j.startswith('JB_') and side(j) == side(m)]             # (main header, jack-board header) pairs

STRIP = Board('channel_strip.net', 'jack_board.net')
GROUP = Board('group.net', 'group_jack_board.net')
MASTER = Board('master.net', 'master_jack_board.net')
HEADER = {'strip': 'CN1', 'group': 'CN2'}
SPADE = {'strip': 'CN4', 'group': 'CN1'}

OPA_DEF = """.subckt OPA1612N inp inn out gnd
* single-pole 40 MHz; 1.1 nV/rtHz, 1.7 pA/rtHz per input (SBOS450C)
Rnv nv gnd 73.0
Env inp_i inp nv gnd 1
Rni1 ni1 gnd 1k
Gni1 gnd inp ni1 gnd 4.18e-4
Rni2 ni2 gnd 1k
Gni2 gnd inn ni2 gnd 4.18e-4
G1 gnd n1 inp_i inn 1
R1 n1 gnd 1e6
C1 n1 gnd 3.98n
E1 out gnd n1 gnd 1
.ends
.subckt OPA1656N inp inn out gnd
* single-pole 53 MHz; 3.75 nV/rtHz averaged over the audio band (1/f-rich), negligible current noise (SBOS901C)
Rnv nv gnd 849
Env inp_i inp nv gnd 1
G1 gnd n1 inp_i inn 1
R1 n1 gnd 1e6
C1 n1 gnd 3.0n
E1 out gnd n1 gnd 1
.ends
.model JMOD NJF(VTO=-2.5 BETA=6m LAMBDA=0.01)"""

class Module:
    """One instance: its parts as SPICE lines with nodes prefixed, given pot positions, switches, plugs and jumpers."""
    def __init__(self, kind, name, board, pos=None, sw=None, jp=None, plugs=None):
        self.kind, self.name, self.b = kind, name, board
        self.pos, self.sw, self.jp, self.plugs = pos or {}, sw or {}, jp or {}, plugs or {}
        self.gnd = '0' if kind == 'master' else f'{name}_G'

    def node(self, ref, pin):
        n = self.b.pins.get((ref, str(pin)))
        if n is None: return f'{self.name}_nc_{ref}_{pin}'
        return self.net(n)

    def net(self, n):
        if n in GROUNDS: return self.gnd
        s = re.sub(r'[^A-Za-z0-9_]', lambda m: {'+': 'P', '-': 'M'}.get(m.group(0), '_'), n)
        return s if self.kind == 'master' else f'{self.name}_{s}'

    def latched_keys(self):
        return [r for r, c in self.b.comps.items() if c['lib'] == 'SW_DPDT_x2' and self.sw.get(r)
                and any(k in c['value'] for k in ('PFL', 'AFL'))]

    def lines(self, pfl_on=False):
        b, L, G = self.b, [], self.gnd
        # logic level of each net: high if the closed PVA2 contacts join it to +5VL (the strip's DG413 control lines)
        group = {}
        def root(n):
            while group.setdefault(n, n) != n: n = group[n]
            return n
        for ref, c in b.comps.items():
            if c['lib'] == 'SW_DPDT_x2':
                on = self.sw.get(ref, False)
                for c_, t_on, t_off in ((2, 1, 3), (5, 4, 6)):
                    x, y = b.pins.get((ref, str(c_))), b.pins.get((ref, str(t_on if on else t_off)))
                    if x and y: group[root(x)] = root(y)
        high = lambda n: n is not None and root(n) == root('+5VL')
        meter = lambda ref: self.kind == 'master' and any(re.match(r'M[LR]', b.pins.get((ref, p), ''))
                                                          for p in [k[1] for k in b.pins if k[0] == ref])
        for (main, jack) in b.link:
            npins = max(int(p) for (r, p) in b.pins if r == main)
            for p in range(1, npins + 1):
                a, c = self.node(main, p), self.node(jack, p)
                if a != c: L.append(f"R{self.name}_{main}_LINK{p} {a} {c} 0.01")
        for ref, c in b.comps.items():
            lib, v, X = c['lib'], c['value'], f'{self.name}_{ref}'
            if ref.startswith('#') or c['dnp'] or lib in OMIT or meter(ref): continue
            nd = lambda p: self.node(ref, p)
            if lib == 'R': L.append(f'R{X} {nd(1)} {nd(2)} {value(v)}')
            elif lib in ('C', 'C_Polarized'): L.append(f'C{X} {nd(1)} {nd(2)} {value(v)}')
            elif lib in ('R_Potentiometer', 'R_Potentiometer_Dual'):
                x = law('lin' in v or 'pan' in v.lower(), self.pos.get(ref, 0.5))     # pans are linear (B)
                for g in ((1, 2, 3), (4, 5, 6)) if lib.endswith('Dual') else ((1, 2, 3),):
                    L.append(f'R{X}_{g[0]}a {nd(g[0])} {nd(g[1])} {10e3 * x + 0.01}')
                    L.append(f'R{X}_{g[0]}b {nd(g[1])} {nd(g[2])} {10e3 * (1 - x) + 0.01}')
            elif lib in ('OPA1612AxD', 'OPA1656ID'):
                sub = 'OPA1656N' if lib == 'OPA1656ID' else 'OPA1612N'
                for u, (p_, m_, o_) in ((1, (3, 2, 1)), (2, (5, 6, 7))):
                    if (ref, str(o_)) in b.pins: L.append(f'X{X}_{u} {nd(p_)} {nd(m_)} {nd(o_)} {G} {sub}')
            elif lib == 'LME49600': L += [f'E{X} {X}_o {G} {nd(2)} {G} 1', f'R{X}_o {X}_o {nd(4)} 1']
            elif lib == 'DRV134':         # +-1 on the Sense nodes (the loop's result), 10K input, ~63 nV/rtHz per leg
                L += [f'R{X}_in {nd(4)} {nd(3)} 10k', f'R{X}_nv {X}_nv {nd(3)} 240k',
                      f'E{X}_p {X}_p {nd(3)} {nd(4)} {nd(3)} 1', f'E{X}_n {X}_n {nd(3)} {nd(4)} {nd(3)} -1',
                      f'E{X}_pn {X}_p2 {X}_p {X}_nv {nd(3)} 1', f'R{X}_op {X}_p2 {nd(7)} 1', f'R{X}_on {X}_n {nd(2)} 1']
            elif lib == 'MMBFJ112': L.append(f'J{X} {nd(1)} {nd(3)} {nd(2)} JMOD')
            elif lib == 'SW_DPDT_x2':
                on = self.sw.get(ref, False)
                for c_, t_on, t_off in ((2, 1, 3), (5, 4, 6)):
                    L.append(f'R{X}_{c_} {nd(c_)} {nd(t_on if on else t_off)} 0.02')
            elif lib.startswith('SolderJumper_3'):
                L.append(f'R{X} {nd(1 if self.jp.get(ref, 12) == 12 else 3)} {nd(2)} 0.01')
            elif lib.startswith('SolderJumper_2'):
                if self.jp.get(ref, lib.endswith('Bridged')): L.append(f'R{X} {nd(1)} {nd(2)} 0.01')
            elif lib == 'DG413xY':        # SW1/SW4 on at logic 1, SW2/SW3 at logic 0
                for in_, d_, s_, no in ((1, 2, 3, True), (8, 7, 6, True), (9, 10, 11, False), (16, 15, 14, False)):
                    n_in = b.pins.get((ref, str(in_)))
                    if n_in is None: continue
                    state = pfl_on if n_in == 'PFL_ON' else high(n_in)
                    if state == no: L.append(f'R{X}_{in_} {nd(d_)} {nd(s_)} 25')
            elif lib == 'G6K-2':          # energised (mute released): COM 3/6 to NO 4/5
                L += [f'R{X}_3 {nd(3)} {nd(4)} 0.05', f'R{X}_6 {nd(6)} {nd(5)} 0.05']
            elif lib == 'FerriteBead':
                L += [f'R{X}_dc {nd(1)} {X}_m 0.05', f'L{X} {X}_m {nd(2)} 0.6u', f'R{X}_p {X}_m {nd(2)} 250']
            elif lib == 'Polyfuse': L.append(f'R{X} {nd(1)} {nd(2)} 0.1')
            elif lib in ('AudioJack3_SwitchTR', 'AudioJack3', 'XLR3'):
                L += self.jack(ref, lib, nd)
        if self.kind == 'master':     # meter feeds: the rectifier's virtual earths, 10K || 20K
            L += [f'RMTRL MTR_L 0 6.67k', f'RMTRR MTR_R 0 6.67k']
        return L

    def jack(self, ref, lib, nd):
        """Unplugged switched jacks close their normals; a plug is ('src', amplitude, ohms, balanced),
        ('load', ohms) or ('short',)."""
        p, X = self.plugs.get(ref), f'{self.name}_{ref}'
        tip, ring, sl = ('2', '3', '1') if lib == 'XLR3' else ('T', 'R', 'S')
        if p is None:
            if lib == 'AudioJack3_SwitchTR':
                return [f'R{X}_tn {nd("T")} {nd("TN")} 0.01', f'R{X}_rn {nd("R")} {nd("RN")} 0.01']
            return []
        if p[0] == 'src':
            _, amp, rs, bal = p                 # balanced: amp is the differential level (half on each leg)
            out = [f'V{X} {X}_s {nd(sl)} DC 0 AC {amp / 2 if bal else amp}', f'R{X}_t {X}_s {nd(tip)} {rs}']
            if bal: out += [f'E{X}_r {X}_r {nd(sl)} {X}_s {nd(sl)} -1', f'R{X}_r {X}_r {nd(ring)} {rs}']
            else: out.append(f'R{X}_r {nd(ring)} {nd(sl)} {rs}')
            return out
        if p[0] == 'load': return [f'R{X}_t {nd(tip)} {nd(sl)} {p[1]}', f'R{X}_r {nd(ring)} {nd(sl)} {p[1]}']
        if p[0] == 'short': return [f'R{X}_t {nd(tip)} {nd(sl)} 0.01', f'R{X}_r {nd(ring)} {nd(sl)} 0.01']
        return []

# ---------------------------------------------------------------- the console
def SPADE_WIRE(wing, k):
    """(ohms, henries) of the k-th module's spade wire from the master (docs/studies/ground_study.md G1, cut list): 14 AWG stranded
    (8.28 mOhm/m, r 0.82 mm) tied under the motherloom; 264 / 237 mm for the first module (left / right wing: the
    master's headers sit at x 5.5 / 72), +40.64 mm per module."""
    l = (0.264 if wing == 'L' else 0.237) + 0.04064 * k
    return 0.00828 * l, 2e-7 * l * (math.log(2 * l / 0.82e-3) - 0.75)

def console(strips, groups, master, gnd_inject=None, spade=None, spade_emf=None):
    """strips: 24 Modules (12 per wing, wing order outward), groups: 4 (2 per wing), master: 1. Returns the deck body.
    spade: {module name: (ohms, henries)} for its spade wire (default: the harness of docs/studies/ground_study.md G1, 14 AWG under
    the motherloom, SPADE_WIRE); spade_emf: {module name: volts AC}
    induced in series with it (a mains field through the loop of spade wire and ribbon grounds; sim/review/ground)."""
    mods = [master] + groups + strips
    pfl_on = any(m.latched_keys() for m in mods)
    L = ['* goa-console: whole console (tools/sim_console.py)', OPA_DEF, 'VPBUS PVBUS 0 DC 17', 'VMBUS MVBUS 0 DC -17']
    for m in mods: L += m.lines(pfl_on)
    # ribbon: per 41 mm segment, 28 AWG (0.213 ohm/m) and ~0.6 uH/m; 2.5 pF to the next conductor per segment
    SEG_R, SEG_L, SEG_C, CONTACT = 0.213 * 0.041, 0.6e-6 * 0.041, 2.5e-12, 0.02
    for wing, hdr in (('L', 'CN2'), ('R', 'CN3')):
        chain = [m for m in groups[:2]] + strips[:12] if wing == 'L' else [m for m in groups[2:]] + strips[12:]
        prev = {p: master.node(hdr, p) for p in range(1, 35)}
        for k, m in enumerate(chain):
            here = {p: f'rb{wing}{k}_{p}' for p in range(1, 35)}
            for p in range(1, 35):
                L += [f'Rrb{wing}{k}_{p} {prev[p]} rb{wing}{k}_{p}m {SEG_R}', f'Lrb{wing}{k}_{p} rb{wing}{k}_{p}m {here[p]} {SEG_L}']
                if p < 34: L.append(f'Crb{wing}{k}_{p} {here[p]} {here[p + 1]} {SEG_C}')
                n = m.b.pins.get((HEADER[m.kind], str(p)))
                if n and n != 'NC': L.append(f'Rhd{m.name}_{p} {here[p]} {m.node(HEADER[m.kind], p)} {CONTACT}')
            prev = here
            # spade wire to the star's bar: the G1 harness by the module's place on the wing (or as given)
            rs, ls = (spade or {}).get(m.name) or SPADE_WIRE(wing, k); emf = (spade_emf or {}).get(m.name)
            end = f'{m.name}_spe' if emf else '0'
            L += [f'Rsp{m.name} {m.gnd} {m.name}_spm {rs}', f'Lsp{m.name} {m.name}_spm {end} {ls}']
            if emf: L.append(f'Vemf{m.name} {end} 0 DC 0 AC {emf}')
    master_rails = ['RJ1P PVBUS ' + master.net('+VBUS') + ' 0.005', 'RJ1M MVBUS ' + master.net('-VBUS') + ' 0.005']
    L += master_rails
    for i, (mname, amps) in enumerate(gnd_inject or ()):   # AC current into a module's ground, returning via 0 V
        L.append(f'IGINJ{i} 0 {mname}_G DC 0 AC {amps}')
    nodes = set()
    for line in L:
        t = line.split()
        if not t or line.startswith(('.', '*')) or t[0][0] not in 'RCLVEXJI': continue
        nodes.update(t[1:5] if t[0][0] in 'EX' else t[1:4] if t[0][0] == 'J' else t[1:3])
    nodes -= {'0', 'inp', 'inn', 'out', 'gnd'}
    L += [f'RLEAK{i} {n} 0 1e9' for i, n in enumerate(sorted(nodes))]
    return L

def default_console(strip_cfg=None, group_cfg=None, master_cfg=None):
    """A console set up as for mixing: every strip ON, assigned L-R, pan centre, EQ flat (EQ in), gain at the detent,
    fader at "0", inputs terminated (50 ohm); group n sums SUB n and AUX n, faders at "0", sub not to MIX; master fader
    at "0", aux 5/6, solo, C/Room and phones at the top. strip_cfg(i) etc. return overrides {pos, sw, plugs, jp}."""
    strips = []
    for i in range(24):
        c = dict(pos={'RV1': FADER0, **{f'RV{k}': 0.0 for k in range(2, 8)}}, sw={'SW4': True, 'SW5': True, 'SW12': True, 'SW14': True},
                 plugs={'JB_J1': ('src', 0, 50, False)})
        o = strip_cfg(i) if strip_cfg else {}
        for k in ('pos', 'sw', 'plugs', 'jp'): c[k] = {**c.get(k, {}), **o.get(k, {})}
        strips.append(Module('strip', f's{i + 1:02d}', STRIP, **c))
    groups = []
    for g in range(4):
        c = dict(pos={'RV1': FADER0, 'RV3': 1.0, 'RV4': FADER0}, jp={f'JP{g + 1}': True, f'JP{g + 5}': True})
        o = group_cfg(g) if group_cfg else {}
        for k in ('pos', 'sw', 'plugs', 'jp'): c[k] = {**c.get(k, {}), **o.get(k, {})}
        groups.append(Module('group', f'g{g + 1}', GROUP, **c))
    c = dict(pos={'RV1': FADER0, 'RV2': 1.0, 'RV3': 1.0, 'RV4': 1.0, 'RV5': 1.0, 'RV6': 1.0},
             plugs={j: ('load', 10e3) for j in ('JB_J3', 'JB_J4', 'JB_J5', 'JB_J6', 'JB_J7', 'JB_J10', 'JB_J11')})
    c['plugs']['JB_J12'] = ('load', 32)
    o = master_cfg or {}
    for k in ('pos', 'sw', 'plugs', 'jp'): c[k] = {**c.get(k, {}), **o.get(k, {})}
    return strips, groups, Module('master', 'm', MASTER, **c)

def run(body, control):
    d = '\n'.join(body + ['.options noopiter gmin=1e-12', '.control', 'set noaskquit'] + control + ['.endc', '.end'])
    with tempfile.NamedTemporaryFile('w', suffix='.cir', delete=False) as f: f.write(d); fn = f.name
    p = subprocess.run(['ngspice', '-b', fn], capture_output=True, text=True)
    res = {}
    for line in (p.stdout + p.stderr).splitlines():
        m = re.match(r'^\s*(\w+)\s+=\s+([-+0-9.eE]+)', line)
        if m: res[m.group(1).lower()] = float(m.group(2))
    if os.environ.get('KEEP'): print('deck:', fn)
    else: os.unlink(fn)
    return res, p.stdout

# ---------------------------------------------------------------- measurement helpers
M = lambda net: MASTER_NODE(net)
def MASTER_NODE(net):
    return re.sub(r'[^A-Za-z0-9_]', lambda m: {'+': 'P', '-': 'M'}.get(m.group(0), '_'), net)
XLR = {'L': ('JB_MAIN_L_XP', 'JB_MAIN_L_XN'), 'R': ('JB_MAIN_R_XP', 'JB_MAIN_R_XN'), 'M': ('JB_MAIN_M_XP', 'JB_MAIN_M_XN')}
def diff(pair): return f'v({pair[0]},{pair[1]})'
def dbu(expr, name): return [f'let {name} = db(mag({expr})/0.7746 + 1e-20)', f'print {name}']
def deg(expr, name): return [f'let {name} = ph({expr})*180/pi', f'print {name}']
SRC = 0.7746                                          # 0 dBu
# Expected levels follow the gain structure. Unity through a strip and the master at their faders' "0" marks is
# -0.8 dB here: each "0" mark gives -10.19 dB (the wiper's ~2.2 kohm drives the post-amp's 100K), each post-amp
# +9.93 dB (1 + 4K7/2K2), and the master's insert 75R and post-amp 47R build-outs -0.18 dB. The DRV134 adds +6 dB
# differential, the CRS build-out -0.3 dB. UNITY assumes the old -6 dB pan centre; since CS2 (docs/proposals/cs2_proposal.md, the
# Delta's law) a strip's pan sits PANC higher at centre (-2.7 dB, not -6) and PANH above POST hard over.
UNITY = -0.82
PANC, PANH = 3.27, 1.68
GPANC = 3.32                                          # CS2b (docs/proposals/cs2b_proposal.md): the group's sub pan, the same law

checks = []
def check(name, got, lo, hi, unit='dB'):
    ok = got is not None and lo <= got <= hi
    checks.append(ok)
    f = lambda x: 'any' if abs(x) >= 400 else f'{x:g}' if x == int(x) else f'{x:.2f}'
    print(f"{'ok  ' if ok else 'FAIL'} {name}: {got if got is None else round(got, 2)} {unit} (expected {f(lo)} .. {f(hi)})", flush=True)

# ---------------------------------------------------------------- checks
AC1K = ['ac lin 1 1k 1k']
def one(i, pos=None, sw=None, src=SRC, plugs=None, jp=None):
    """Overrides for strip i only: the test source on its input, the rest terminated."""
    def f(k):
        if k != i: return {}
        return dict(pos=pos or {}, sw=sw or {}, jp=jp or {}, plugs={'JB_J1': ('src', src, 50, False), **(plugs or {})})
    return f

def t_levels():
    """0 dBu into strip 1 (pan centre, every fader at "0") through MIX to the main XLRs, mono, C/Room and phones."""
    s, g, m = default_console(one(0))
    r, _ = run(console(s, g, m), AC1K + dbu(diff(XLR['L']), 'ml') + dbu(diff(XLR['R']), 'mr') + dbu(diff(XLR['M']), 'mm')
               + deg(diff(XLR['L']), 'pl') + dbu('v(JB_CRL_XP,JB_CRL_XN)', 'cr') + dbu('v(JB_PHJ_L)', 'ph'))
    check('main L (XLR differential), 0 dBu in, pan centre (-2.7 dB), faders at "0"', r.get('ml'), UNITY + PANC - 0.2, UNITY + PANC + 0.2)
    check('main R', r.get('mr'), UNITY + PANC - 0.2, UNITY + PANC + 0.2)
    check('main L polarity: XLR pin 2 in phase with the input tip', abs(r.get('pl', 99)), 0, 5, 'deg')
    check('main mono (L + R of a centre-panned source: +6 dB)', r.get('mm'), UNITY + PANC + 5.8, UNITY + PANC + 6.2)
    check('C/Room L (TRS differential, C/ROOM at the top; CRS build-out -0.3 dB)', r.get('cr'), UNITY + PANC - 0.5, UNITY + PANC - 0.1)
    check('phones L into 32 ohm (PHONES at the top, single-ended, +9.9 dB)', r.get('ph'), UNITY + PANC - 0.3 - 6.02 + 9.93 - 0.3, UNITY + PANC - 0.3 - 6.02 + 9.93 + 0.3)

def t_pan():
    s, g, m = default_console(one(0, pos={'RV8': 0.0}))
    r, _ = run(console(s, g, m), AC1K + dbu(diff(XLR['L']), 'ml') + dbu(diff(XLR['R']), 'mr'))
    check('pan hard left: main L (+4.4 dB against centre: the Delta\'s law)', r.get('ml'), UNITY + 6.02 + PANH - 0.2, UNITY + 6.02 + PANH + 0.2)
    check('pan hard left: main R (pan rejection)', r.get('mr'), -400, -60)

def t_mute_route():
    s, g, m = default_console(one(0, sw={'SW4': False}))
    r, _ = run(console(s, g, m), AC1K + dbu(diff(XLR['L']), 'ml'))
    check('strip ON unlatched (muted): main L', r.get('ml'), -400, -75)
    s, g, m = default_console(one(0, sw={'SW5': False}))
    r, _ = run(console(s, g, m), AC1K + dbu(diff(XLR['L']), 'ml'))
    check('strip L-R unassigned: main L', r.get('ml'), -400, -75)

def t_sub():
    """Strip 1 routed 1-2 (not L-R), pan centre -> group 1 (SUB 1) -> sub out; then sub to MIX."""
    s, g, m = default_console(one(0, sw={'SW5': False, 'SW6': True}))
    r, _ = run(console(s, g, m), AC1K + dbu('v(g1_JB_S_OP,g1_JB_S_ON)', 'so') + dbu(diff(XLR['L']), 'ml'))
    check('strip 1 to SUB 1: group 1 sub out (TRS differential, sub fader at "0")', r.get('so'), -1.2 + PANC, -0.6 + PANC)
    check('SUB not routed to MIX: main L', r.get('ml'), -400, -75)
    s, g, m = default_console(one(0, sw={'SW5': False, 'SW6': True}), group_cfg=lambda k: dict(sw={'SW1': True}) if k == 0 else {})
    r, _ = run(console(s, g, m), AC1K + dbu(diff(XLR['L']), 'ml') + dbu(diff(XLR['R']), 'mr'))
    check('SUB 1 to MIX (sub pan centre, -2.7 dB since CS2b): main L', r.get('ml'), -7.7 + PANC + GPANC, -7.0 + PANC + GPANC)
    check('SUB 1 to MIX: main R', r.get('mr'), -7.7 + PANC + GPANC, -7.0 + PANC + GPANC)
    # every SUB bus positively, through its own group (a swapped header pin or an open feed would pass the name-joined
    # sims otherwise, docs/reviews/project_review.md RV11.2): 1-2 feeds SUB 1 / SUB 2 (pan L / R), 3-4 feeds SUB 3 / SUB 4
    s, g, m = default_console(one(0, sw={'SW5': False, 'SW6': True, 'SW7': True}))
    r, _ = run(console(s, g, m), AC1K + [x for k in (2, 3, 4) for x in dbu(f'v(g{k}_JB_S_OP,g{k}_JB_S_ON)', f's{k}')])
    for k in (2, 3, 4):
        check(f'strip 1 to SUB {k} (pan centre): group {k} sub out', r.get(f's{k}'), -1.2 + PANC, -0.6 + PANC)

def t_aux():
    s, g, m = default_console(one(0, pos={'RV2': 1.0, 'RV6': 1.0}, sw={'SW8': True, 'SW10': True}))
    r, _ = run(console(s, g, m), AC1K + dbu('v(g1_JB_A_OP,g1_JB_A_ON)', 'a1') + dbu('v(JB_A5_OP,JB_A5_ON)', 'a5')
               + dbu('v(g2_JB_A_OP,g2_JB_A_ON)', 'a2'))
    check('aux 1 send at the top (pre): group 1 aux out (TRS differential, master at the top)', r.get('a1'), 5.5, 6.5)
    check('aux 5 send at the top (pre): master aux 5 out', r.get('a5'), 5.5, 6.5)
    check('aux 2 (send at 0): group 2 aux out silent', r.get('a2'), -400, -75)
    # every aux bus positively (RV11.2): sends 2 / 3 / 4 to groups 2 / 3 / 4, send 6 to the master's aux 6 out
    s, g, m = default_console(one(0, pos={'RV3': 1.0, 'RV4': 1.0, 'RV5': 1.0, 'RV7': 1.0}, sw={'SW8': True, 'SW9': True, 'SW10': True}))
    r, _ = run(console(s, g, m), AC1K + [x for k in (2, 3, 4) for x in dbu(f'v(g{k}_JB_A_OP,g{k}_JB_A_ON)', f'a{k}')]
               + dbu('v(JB_A6_OP,JB_A6_ON)', 'a6'))
    for k in (2, 3, 4):
        check(f'aux {k} send at the top (pre): group {k} aux out', r.get(f'a{k}'), 5.5, 6.5)
    check('aux 6 send at the top (pre): master aux 6 out', r.get('a6'), 5.5, 6.5)

def t_pfl():
    """Strip 1 PFL latched: the master's switcher moves C/Room and phones from MIX to PFL; the mix is untouched."""
    s, g, m = default_console(one(0, pos={'RV1': 0.0}, sw={'SW3': True}))
    r, _ = run(console(s, g, m), AC1K + dbu('v(JB_CRL_XP,JB_CRL_XN)', 'cr') + dbu(diff(XLR['L']), 'ml')
               + dbu('v(JB_PHJ_L)', 'ph'))
    check('PFL (fader down): C/Room L, solo level at the top (PRE + 6 dB DRV134 - 0.3 dB build-out)', r.get('cr'), 5.3, 5.9)
    check('PFL: phones L (+9.9 dB)', r.get('ph'), 9.2, 9.8)
    check('PFL (fader down): main L silent', r.get('ml'), -400, -75)

def t_return():
    """A balanced 0 dBu source into group 1's return L only (R normalled), return to MIX, return level at the top
    (unity: a return has no post-amp, so its "0" mark is a plain -10 dB)."""
    s, g, m = default_console(group_cfg=lambda k: dict(pos={'RV4': 1.0}, sw={'SW4': True},
                                                       plugs={'JB_J4': ('src', SRC, 50, True)}) if k == 0 else {})
    r, _ = run(console(s, g, m), AC1K + dbu(diff(XLR['L']), 'ml') + dbu(diff(XLR['R']), 'mr'))
    check('return 1 L (0 dBu balanced, normalled to R) to MIX, level at the top: main L (master -0.44 dB, +6 dB)',
          r.get('ml'), UNITY + 6.2, UNITY + 6.6)
    check('return 1 to MIX: main R', r.get('mr'), UNITY + 6.2, UNITY + 6.6)

def t_return2():
    """Group 1's second return (docs/reviews/feature_gaps.md RET1): the same as return 1 to MIX, and routed to 1-2 it reaches SUB 1
    exactly as return 1 does."""
    s, g, m = default_console(group_cfg=lambda k: dict(pos={'RV5': 1.0}, sw={'SW8': True},
                                                       plugs={'JB_J6': ('src', SRC, 50, True)}) if k == 0 else {})
    r, _ = run(console(s, g, m), AC1K + dbu(diff(XLR['L']), 'ml') + dbu(diff(XLR['R']), 'mr'))
    check('return 2 L (0 dBu balanced, normalled to R) to MIX, level at the top: main L', r.get('ml'), UNITY + 6.2, UNITY + 6.6)
    check('return 2 to MIX: main R', r.get('mr'), UNITY + 6.2, UNITY + 6.6)
    sub = {}
    for n, (pot, key, jk) in ((1, ('RV4', 'SW5', 'JB_J4')), (2, ('RV5', 'SW9', 'JB_J6'))):
        s, g, m = default_console(group_cfg=lambda k: dict(pos={pot: 1.0}, sw={key: True},
                                                           plugs={jk: ('src', SRC, 50, True)}) if k == 0 else {})
        r, _ = run(console(s, g, m), AC1K + dbu('v(g1_JB_S_OP,g1_JB_S_ON)', 'so'))
        sub[n] = r.get('so')
    print(f'     routed 1-2: SUB 1 out {sub[1]:.2f} dBu from return 1, {sub[2]:.2f} dBu from return 2')
    check('return 2 routed 1-2: SUB 1 out against return 1 the same way (dB)', sub[2] - sub[1], -0.05, 0.05)

def t_ext():
    s, g, m = default_console(master_cfg=dict(sw={'SW3': True}, plugs={'JB_J8': ('src', SRC, 50, True)}))
    r, _ = run(console(s, g, m), AC1K + dbu('v(JB_CRL_XP,JB_CRL_XN)', 'cl') + dbu('v(JB_CRR_XP,JB_CRR_XN)', 'cr'))
    check('EXT L only (0 dBu balanced, R normalled), EXT selected: C/Room L', r.get('cl'), 5.3, 5.9)
    check('EXT L only: C/Room R', r.get('cr'), 5.3, 5.9)

def t_dim():
    """CS7 (docs/proposals/cs7_proposal.md): DIM latched takes C/Room 20 dB down (C/ROOM at the top: -20.75 dB, sim/review/cs7/dim.py);
    phones and meters keep CRSB (+0.09 dB: the C/ROOM pot no longer loads the 100R build-out)."""
    out = {}
    for dim in (False, True):
        s, g, m = default_console(master_cfg=dict(sw={'SW3': True, 'SW4': dim}, plugs={'JB_J8': ('src', SRC, 50, True)}))
        out[dim], _ = run(console(s, g, m), AC1K + dbu('v(JB_CRL_XP,JB_CRL_XN)', 'cl') + dbu('v(JB_CRR_XP,JB_CRR_XN)', 'cr')
                          + dbu('v(JB_PHJ_L)', 'ph'))
    delta = lambda k: None if k not in out[True] or k not in out[False] else out[True][k] - out[False][k]   # a missing node fails
    check('DIM latched: C/Room L against released (C/ROOM at the top)', delta('cl'), -21.1, -20.4)
    check('DIM latched: C/Room R against released', delta('cr'), -21.1, -20.4)
    check('DIM latched: phones L against released', delta('ph'), -0.05, 0.2)

def t_crosstalk():
    """Strip 1 hard left at 0 dBu: what leaks into main R, SUB 1 and AUX 1 (ribbon capacitance, ground impedance)."""
    s, g, m = default_console(one(0, pos={'RV8': 0.0}))
    meas = ['ac lin 3 1k 20k'] + [f'let lr = db(mag({diff(XLR["R"])})/mag({diff(XLR["L"])}))', 'print lr[2]',
            f'let ls = db(mag(v(g1_JB_S_OP,g1_JB_S_ON))/mag({diff(XLR["L"])}))', 'print ls[2]',
            f'let la = db(mag(v(g1_JB_A_OP,g1_JB_A_ON))/mag({diff(XLR["L"])}))', 'print la[2]']
    r, out = run(console(s, g, m), meas)
    v = {k: float(x) for k, x in re.findall(r'(lr|ls|la)\[2\]\s*=\s*([-+0-9.eE]+)', out)}
    check('crosstalk, 20 kHz: MIX L -> main R', v.get('lr'), -400, -80)
    check('crosstalk, 20 kHz: MIX L -> SUB 1 out', v.get('ls'), -400, -80)
    check('crosstalk, 20 kHz: MIX L -> AUX 1 out', v.get('la'), -400, -80)

def t_ground():
    """Ground currents, 24 strips routed. (a) 10 mA into strip 24's ground alone (a synth's shield, a hum loop): what
    reaches main L. GCANCEL averages the strip grounds, so one strip's own offset is not cancelled; it is kept small by
    the ground conductors and the spade. (b) A common shift: 1 mA into every strip's ground (24 mA through the shared
    ribbon grounds and spades). GCANCEL is meant for this: main L against the mean strip-ground voltage."""
    s, g, m = default_console()
    for f in (50, 1000):
        r, _ = run(console(s, g, m, gnd_inject=[('s24', 10e-3)]), [f'ac lin 1 {f} {f}']
                   + dbu(diff(XLR['L']), 'ml') + dbu('v(s24_G)', 'vg'))
        print(f'     {f} Hz: strip 24 ground {r.get("vg"):.1f} dBu for 10 mA')
        check(f'10 mA into strip 24 ground at {f} Hz: main L', r.get('ml'), -400, -85, 'dBu')
    # (b) 1 mA into every strip and group, as built and with the master summers referenced to master ground instead of
    # GCANCEL (pin 26 tied to 0 V at the master): the improvement is what ground cancel buys
    res = {}
    for tie in (False, True):
        body = console(s, g, m, gnd_inject=[(x.name, 1e-3) for x in s + g]) + (['RTIE GCANCEL 0 0.001'] if tie else [])
        r, _ = run(body, AC1K + dbu(diff(XLR['L']), 'ml'))
        res[tie] = r.get('ml')
    print(f'     1 mA into every module: main L {res[False]:.1f} dBu with ground cancel, {res[True]:.1f} dBu tied to master ground')
    check('ground cancel against a master-ground reference (1 mA per module)', res[True] - res[False], 15, 400)

def t_noise():
    """Main L output noise, 20 Hz-20 kHz unweighted, inputs terminated in 50 ohm, faders at "0": 24 strips routed L-R,
    then a single strip routed (the others unassigned)."""
    # a strip's PRE noise with EQ in is -92.9 dBu: -96.7 from its resistors, the rest the OPA1612's 1.7 pA/rtHz current
    # noise in the 22K EQ and KHN networks. 24 such strips at pan centre sum to -84.9 dBu on MIX L; +6 dB DRV134
    for label, f, lo, hi in (('24 strips routed', None, -81 + PANC, -77 + PANC), ('1 strip routed', lambda k: dict(sw={'SW5': k == 0}), -93 + PANC, -89 + PANC)):
        s, g, m = default_console(f)
        s[0].plugs['JB_J1'] = ('src', 1, 50, False)
        r, out = run(console(s, g, m), [f'noise {diff(XLR["L"])} v{s[0].name}_JB_J1 dec 20 20 20k', 'setplot noise2',
                                         'let nd = db(onoise_total/0.7746)', 'print nd'])
        check(f'main L noise, {label}', r.get('nd'), lo, hi, 'dBu')

CHECKS = {f.__name__[2:]: f for f in (t_levels, t_pan, t_mute_route, t_sub, t_aux, t_pfl, t_return, t_return2, t_ext, t_dim, t_crosstalk,
                                       t_ground, t_noise)}
if __name__ == '__main__':
    if '--list' in sys.argv: print(' '.join(CHECKS)); sys.exit(0)
    for name in [a for a in sys.argv[1:] if not a.startswith('-')] or list(CHECKS):
        print(f'== {name}: {CHECKS[name].__doc__.split(chr(10))[0] if CHECKS[name].__doc__ else ""}', flush=True)
        CHECKS[name]()
    print(f'{sum(checks)}/{len(checks)} checks passed')
    sys.exit(0 if all(checks) else 1)
