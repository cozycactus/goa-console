"""SPICE deck of the whole master module (master.net + master_jack_board.net joined by the CN5 link) for loop-stability
work. Every op-amp unit (OPA1612 -> TI OPA161x, OPA1656 -> TI OPA1656, TL072 -> TI SLOJ067 Boyle or TI TL07xH) gets a
Tian probe at its output (VTI_<u> in series, ITI_<u> into the output pin) and a source in series with its + input
(VST_<u>); the LME49600s get a macro model (no vendor model exists) and their own probe; the DRV134s get TI's model.
All probes idle unless altered in .control.

cfg keys (all optional):
  pos     {RV: 0..1}       pot positions (A law as tools/sim_netlist.py; RV7/RV8 trims linear)
  sw      {SW: bool}       PVA2 latched (SW3 True = EXT)
  pfl_on  bool             DG413 logic (True = PFL pressed)
  relays  bool             mute relays energised (True = playing)
  jp      {JP: 'PK'|'AV'}  meter jumpers
  ins     {'L'|'R': None | (rs, csrc, rload, cload)}   insert plug: None = no plug (normalled)
  ext     {'L'|'R': None | (rs, c)}                    EXT plug, balanced source rs per leg; R None = normalled to L
  phones  (rload_ohm or None, ccable)                   per side; None = no headphones
  outload (r, c)          per leg on every DRV134 output connector
  bus     {BUS: (N, Rsrc, Cbus)}  N sources of Rsrc to ground on the bus plus Cbus
  gc      'strips' | 'none'      GCANCEL: 10R/28 to ground, or only the 100K keeper
  extra   [(name, n1, n2, value)]   added parts (fixes)
  loads   {net: C}                  capacitance to ground on nets (trace estimates, test loads)
  tl      'old' | 'H'               TL072 model
  lme     dict(fn, q, td, ro, lo, cin) LME49600 macro parameters
  meter_dc  V   DC level forced at CRS_L/R (meter diode states); attack_ma: DC sink at M*_PK (attack state)
"""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
M = os.environ.get('TI_MODELS', os.path.join(HERE, 'models'))   # TI's models stay out of the repo (licence)
sys.path.insert(0, HERE)
from netlib import load, REPO

comps, pins_raw, nets = load(REPO + '/master.net')
# EXT R receiver: gen_master.py names its output EXT_RR, the same net as the R jack's ring (stereo_in('EXT', ..., 'EXT_RR')).
# The fixed deck (default) splits the receiver-side pins onto EXT_RRO, as the intended circuit.
# Master v0.8 (MG1) names the outputs EXT_BL/BR; the split only applies to a v0.7 netlist.
EXTFIX = {('U17', '7'): 'EXT_RRO', ('R84', '2'): 'EXT_RRO', ('C90', '2'): 'EXT_RRO', ('C93', '1'): 'EXT_RRO'}
if not all(pins_raw.get(k) == 'EXT_RR' for k in EXTFIX): EXTFIX = {}
pins_fix = dict(pins_raw); pins_fix.update(EXTFIX)
pins = pins_fix
jcomps, jpins, jnets = load(REPO + '/master_jack_board.net')

GROUND = {'GNDA', 'GNDD', 'GNDM', 'PHONESGND', 'CHASSIS'}
RAILS = {'+VA': 16.9, '-VA': -16.9, '+VP': 16.8, '-VP': -16.8, '+VM': 16.45, '-VM': -16.45, '+VL': 16.75, '-VL': -16.75,
         '+VBUS': 17.0, '-VBUS': -17.0, '+5VL': 5.1}

def san(n):
    if n in GROUND: return '0'
    return re.sub(r'[^A-Za-z0-9_]', lambda m: {'+': 'P', '-': 'M'}.get(m.group(0), '_'), n)

def node(ref, pin):
    n = pins.get((ref, str(pin)))
    return san(n) if n else f'nc_{ref}_{pin}'

def jnode(ref, pin):
    n = jpins.get((ref, str(pin)))
    return san(n) if n else f'jnc_{ref}_{pin}'

def value(text):
    t = text.split()[0]
    m = re.fullmatch(r'(\d+)([RKkMpnuµ])(\d*)', t) or re.fullmatch(r'(\d+\.?\d*)([RKkMpnuµ])()', t)
    if not m: raise ValueError(text)
    mult = {'R': 1, 'K': 1e3, 'k': 1e3, 'M': 1e6, 'p': 1e-12, 'n': 1e-9, 'u': 1e-6, 'µ': 1e-6}[m.group(2)]
    return float(m.group(1) + ('.' + m.group(3) if m.group(3) else '')) * mult

def law(taper, th):
    a = lambda x: 0.30 * x if x <= 0.5 else 0.15 + 1.70 * (x - 0.5)
    return {'A': a(th), 'B': th, 'L': th}[taper]

OPMODEL = {'OPA1612AxD': 'OPA161x', 'OPA1656ID': 'OPA1656'}
PINS = {1: (3, 2, 1), 2: (5, 6, 7)}

def units():
    out = []
    for ref, c in comps.items():
        if c['part'] in ('OPA1612AxD', 'OPA1656ID', 'TL072'):
            for u, (p_, m_, o_) in PINS.items():
                if (ref, str(o_)) in pins: out.append((f'{ref}{"AB"[u-1]}', ref, p_, m_, o_, c['part']))
        if c['part'] == 'LME49600':
            out.append((ref, ref, 2, None, 4, 'LME49600'))
    return sorted(out, key=lambda t: (int(t[1][1:]), t[0]))

UNITS = {u[0]: u for u in units()}

def outnet(u):
    t = UNITS[u]; return node(t[1], t[4])

LME_DEF = dict(fn=85e6, q=2.5, td=0, ro=6, lo=5e-9, cin=3e-12)   # fitted to SNAS422E figs 12-17 (lmefit.py)

def lme_sub(p):
    # unity-gain buffer: 200R internal input resistor, Cin, 7.5M; second-order section (fn, q) + delay; Ro + Lo out.
    w = 2 * 3.141592653589793 * p['fn']; C = 1e-12; L = 1 / (w * w * C); R = (L / C) ** 0.5 / p['q']
    td = max(p['td'], 1e-12)
    return f""".subckt LME49600M in vcc vee out
Rin in n1 200
Cin n1 0 {p['cin']}
Rdc n1 0 7.5meg
E1 n2 0 n1 0 1
R2 n2 n3 {R}
L2 n3 n4 {L}
C2 n4 0 {C}
E2 n5 0 n4 0 1
T1 n5 0 n6 0 Z0=50 TD={td}
RT n6 0 50
E3 n7 0 n6 0 1
Ro n7 n8 {p['ro']}
Lo n8 out {max(p['lo'], 1e-12)}
.ends"""

def deck(cfg, ctl=''):
    global pins
    pins = dict(pins_raw if cfg.get('ext_bug') else pins_fix)
    for k, n in cfg.get('pinmove', {}).items(): pins[k] = n      # {(ref, pin): new net}: splits a net (trace models, fixes)
    omit = set(cfg.get('omit', ()))                            # refs left out (moved or removed parts)
    if cfg.get('no_meter'):                                    # transient runs: the meter detectors stall the time step
        omit |= {r for r, c in comps.items() if c['part'] in ('TL072', 'LM2901') or
                 (c['part'] == '1N4148' and any(pins.get((r, k), '').startswith(('ML_', 'MR_')) for k in ('1', '2')))}
    pos = cfg.get('pos', {}); sw = cfg.get('sw', {}); pfl_on = cfg.get('pfl_on', False); relays = cfg.get('relays', True)
    jp = cfg.get('jp', {}); tl = cfg.get('tl', 'old')
    lme = dict(LME_DEF, **cfg.get('lme', {}))
    L = ['* master module deck (masterdeck.py)',
         f'.include {M}/OPA161x.LIB', f'.include {M}/OPA1656.LIB', f'.include {M}/DRV134.LIB',
         f'.include {M}/TL072_boyle.lib' if tl == 'old' else f'.include {M}/tl07xh_tl08xh.lib',
         lme_sub(lme),
         '.model D1N4148 D(IS=2.52n RS=0.568 N=1.752 CJO=4p M=0.4 TT=20n BV=100)']
    tlsub = 'TL072' if tl == 'old' else 'TL07XH_TL08XH'
    for n, v in RAILS.items(): L.append(f'V{san(n)} {san(n)} 0 DC {v}')
    # link ribbon: main CN5 pin k <-> jack board CN1 pin k
    for k in range(1, 41):
        a, b = node('CN5', k), jnode('CN1', k)
        if a != '0' or b != '0': L.append(f'RLINK{k} {a} {b} 0.01')
    # ---- master board parts
    for ref, c in comps.items():
        if c['dnp'] or ref in omit: continue
        part, v = c['part'], c['value']
        if part == 'R': L.append(f'R{ref} {node(ref,1)} {node(ref,2)} {value(v)}')
        elif part in ('C', 'C_Polarized'): L.append(f'C{ref} {node(ref,1)} {node(ref,2)} {value(v)}')
        elif part in ('R_Potentiometer', 'R_Potentiometer_Dual', 'R_Potentiometer_Trim'):
            r = 10e3; taper = 'L' if part.endswith('Trim') else 'A'
            x = law(taper, pos.get(ref, 0.5 if taper == 'L' else 0.75))
            for g in ((1, 2, 3), (4, 5, 6)) if part.endswith('Dual') else ((1, 2, 3),):
                L.append(f'R{ref}_{g[0]}a {node(ref,g[0])} {node(ref,g[1])} {r*x+0.01}')
                L.append(f'R{ref}_{g[0]}b {node(ref,g[1])} {node(ref,g[2])} {r*(1-x)+0.01}')
        elif part == 'SW_DPDT_x2':
            on = sw.get(ref, False)
            for c_, t_on, t_off in ((2, 1, 3), (5, 4, 6)):
                L.append(f'R{ref}_{c_} {node(ref,c_)} {node(ref, t_on if on else t_off)} 0.02')
        elif part.startswith('SolderJumper_3'):
            a = 3 if jp.get(ref, 'PK') == 'AV' else 1
            L.append(f'R{ref} {node(ref,a)} {node(ref,2)} 0.01')
        elif part == 'FerriteBead':      # 220R@100MHz 0805: 0.6 uH || 250R || 1.5 pF + 50 mR
            a, b = node(ref, 1), node(ref, 2)
            L += [f'R{ref}_dc {a} {ref}_m 0.05', f'L{ref} {ref}_m {b} 0.6u', f'R{ref}_p {ref}_m {b} 250', f'C{ref}_p {ref}_m {b} 1.5p']
        elif part == 'G6K-2':             # COM 3/6, NO 4/5, NC 2/7
            for com, no, nc in ((3, 4, 2), (6, 5, 7)):
                L.append(f'R{ref}_{com} {node(ref,com)} {node(ref, no if relays else nc)} 0.05')
                L.append(f'C{ref}_{com} {node(ref, nc if relays else no)} 0 1p')
        elif part == 'DG413xY':           # SW1/SW4 NO (closed with IN high), SW2/SW3 NC
            for in_, d_, s_, no in ((1, 2, 3, True), (8, 7, 6, True), (16, 15, 14, False), (9, 10, 11, False)):
                closed = (pfl_on == no)
                if closed:
                    L += [f'R{ref}_{in_} {node(ref,d_)} {node(ref,s_)} 25', f'C{ref}_{in_}d {node(ref,d_)} 0 17p',
                          f'C{ref}_{in_}s {node(ref,s_)} 0 17p']
                else:
                    L += [f'C{ref}_{in_}d {node(ref,d_)} 0 9p', f'C{ref}_{in_}s {node(ref,s_)} 0 9p',
                          f'C{ref}_{in_}x {node(ref,d_)} {node(ref,s_)} 0.5p']
        elif part in OPMODEL or part == 'TL072':
            sub = OPMODEL.get(part, tlsub); vp, vm = node(ref, 8), node(ref, 4)
            for u, (p_, m_, o_) in PINS.items():
                if (ref, str(o_)) not in pins: continue
                nm = f'{ref}{"AB"[u-1]}'
                L.append(f'X{nm} {nm}_pp {node(ref,m_)} {vp} {vm} {nm}_ox {sub}')
                L.append(f'VST_{nm} {nm}_pp {node(ref,p_)} DC 0 AC 0 PULSE(0 0 0 1n 1n 1 2)')
                L.append(f'VTI_{nm} {nm}_ox {node(ref,o_)} DC 0 AC 0')
                L.append(f'ITI_{nm} 0 {nm}_ox DC 0 AC 0')
        elif part == 'LME49600':
            nm = ref
            L.append(f'X{nm} {nm}_pp {node(ref,5)} {node(ref,3)} {nm}_ox LME49600M')
            L.append(f'VST_{nm} {nm}_pp {node(ref,2)} DC 0 AC 0 PULSE(0 0 0 1n 1n 1 2)')
            L.append(f'VTI_{nm} {nm}_ox {node(ref,4)} DC 0 AC 0')
            L.append(f'ITI_{nm} 0 {nm}_ox DC 0 AC 0')
        elif part == 'DRV134':
            L.append(f'X{ref} ' + ' '.join(node(ref, k) for k in range(1, 9)) + ' DRV134')
        elif part == '1N4148' and any(n.startswith(('ML_', 'MR_')) for n in (pins.get((ref, '1'), ''), pins.get((ref, '2'), ''))):
            L.append(f'D{ref} {node(ref,2)} {node(ref,1)} D1N4148')
        elif part == 'LM2901':            # only the inputs matter here: 2 pF from each input to GNDM
            for p_ in (4, 5, 6, 7, 8, 9, 10, 11):
                n = pins.get((ref, str(p_)))
                if n and n.endswith('_DET'): L.append(f'C{ref}_{p_} {node(ref,p_)} 0 2p')
    # ---- jack board: jacks
    ins = cfg.get('ins', {}); ext = cfg.get('ext', {}); ph = cfg.get('phones', (32, 220e-12)); ol = cfg.get('outload', (10e3, 1e-9))
    for side, j in (('L', 'J1'), ('R', 'J2')):
        p = ins.get(side)
        if p is None: L.append(f'RJ{j}_n {jnode(j,"R")} {jnode(j,"RN")} 0.01')
        else:
            rs, cs, rl, cl = p
            L += [f'RJ{j}_l {jnode(j,"T")} 0 {rl}', f'CJ{j}_l {jnode(j,"T")} 0 {cl}', f'CJ{j}_s {jnode(j,"R")} 0 {cs}']
            if rs: L.append(f'RJ{j}_s {jnode(j,"R")} 0 {rs}')
    for side, j in (('L', 'J8'), ('R', 'J9')):
        p = ext.get(side)
        if p is None:
            if j == 'J9': L += [f'RJ9_tn {jnode(j,"T")} {jnode(j,"TN")} 0.01', f'RJ9_rn {jnode(j,"R")} {jnode(j,"RN")} 0.01']
        else:
            rs, c = p
            L += [f'RJ{j}_t {jnode(j,"T")} 0 {rs}', f'RJ{j}_r {jnode(j,"R")} 0 {rs}',
                  f'CJ{j}_t {jnode(j,"T")} 0 {c}', f'CJ{j}_r {jnode(j,"R")} 0 {c}']
    if ph is not None:
        rl, cc = ph
        for pn in ('T', 'R'):
            if rl: L.append(f'RJ12_{pn} {jnode("J12",pn)} 0 {rl}')
            if cc: L.append(f'CJ12_{pn} {jnode("J12",pn)} 0 {cc}')
    for j in ('J3', 'J4', 'J5'):
        for pn in ('2', '3'): L += [f'RJ{j}_{pn} {jnode(j,pn)} 0 {ol[0]}', f'CJ{j}_{pn} {jnode(j,pn)} 0 {ol[1]}']
    for j in ('J6', 'J7', 'J10', 'J11'):
        for pn in ('T', 'R'): L += [f'RJ{j}_{pn} {jnode(j,pn)} 0 {ol[0]}', f'CJ{j}_{pn} {jnode(j,pn)} 0 {ol[1]}']
    # ---- buses and GCANCEL
    bus = {'MIXL': (24, 4.7e3, 1e-9), 'MIXR': (24, 4.7e3, 1e-9), 'AUX5': (24, 22e3 + 2.5e3, 1e-9),
           'AUX6': (24, 22e3 + 2.5e3, 1e-9), 'PFL': (1, 22e3, 1e-9)}
    bus.update(cfg.get('bus', {}))
    for b, (n, r, c) in bus.items():
        if n: L.append(f'RBUS_{b} {san(b)} 0 {r / n}')
        if c: L.append(f'CBUS_{b} {san(b)} 0 {c}')
    if cfg.get('gc', 'strips') == 'strips': L.append('RGC GCANCEL 0 0.357')
    # ---- meter DC states
    if cfg.get('meter_dc'):
        for s in ('L', 'R'): L.append(f'IMDC_{s} 0 CRS_{s} DC {cfg["meter_dc"] / 90.9e3}')
    if cfg.get('attack_ma'):
        for s in ('L', 'R'): L.append(f'IATK_{s} M{s}_PK 0 DC {cfg["attack_ma"] * 1e-3}')
    if cfg.get('pk_hold_ua'):
        for s in ('L', 'R'): L.append(f'IPKH_{s} 0 M{s}_PK DC {cfg["pk_hold_ua"] * 1e-6}')
    for nm, a, b, val in cfg.get('extra', []): L.append(f'{nm} {a} {b} {val}')
    for i, (n, c) in enumerate(cfg.get('loads', {}).items()): L.append(f'CLD{i} {san(n)} 0 {c}')
    # leak every node to ground (floating nodes from parts left out)
    nodes = set()
    for line in L:
        t = line.split()
        if not t or line.startswith(('.', '*')) or t[0][0] not in 'RCLVIXDE': continue
        if t[0][0] == 'X': nodes.update(t[1:-1])
        else: nodes.update(t[1:3])
    nodes.discard('0')
    L += [f'RLEAK{i} {n} 0 1e9' for i, n in enumerate(sorted(nodes))]
    L += [cfg.get('opts', '.options itl1=500 noopiter'), ctl, '.end']
    return '\n'.join(L)

if __name__ == '__main__':
    for u in UNITS.values(): print(u, outnet(u[0]))
