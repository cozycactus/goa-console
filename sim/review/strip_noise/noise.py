"""Strip noise budget: which op-amp stages (and which part of their noise) set the PRE noise, and what other op-amps or
lower impedances would do. Built from channel_strip.net + jack_board.net with tools/sim_console.py's module builder.
usage: python3 noise.py n1   (strip v4.4: attribution, the N1 package set, PRE and console noise)"""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'tools'))
import sim_console as sc

# op-amp noise models: en (nV/rtHz) and in (pA/rtHz), band-averaged over 20 Hz-20 kHz (a 1/f corner near 100 Hz adds
# ~0.2 dB unweighted; OPA1656's 3.75 nV is its datasheet 0.53 uVrms over the band, 1/f included)
PARTS = {'OPA1612': (1.1, 1.7), 'none': (0, 0), 'en_only': (1.1, 0), 'in_only': (0, 1.7),
         'OPA1656': (3.75, 0.006), 'NE5534A': (3.5, 0.4), 'LM4562': (2.7, 1.6), 'OPA1642': (5.1, 0.0008)}
K4T = 1.656e-20                                            # 4kT at 27 C

def subckt(name, en, inn):
    """Single-pole 40 MHz op-amp with white input voltage noise en and current noise inn on each input, as noise-only
    sources (a resistor on an isolated node, copied by a controlled source)."""
    L = [f'.subckt {name} inp inn out gnd']
    L += [f'Rnv nv gnd {max(en * en * 1e-18 / K4T, 1e-9)}', 'Env inp_i inp nv gnd 1']
    if inn:
        gm = inn * 1e-12 / (K4T * 1e3) ** 0.5
        L += ['Rni1 ni1 gnd 1k', f'Gni1 gnd inp ni1 gnd {gm}', 'Rni2 ni2 gnd 1k', f'Gni2 gnd inn ni2 gnd {gm}']
    L += ['G1 gnd n1 inp_i inn 1', 'R1 n1 gnd 1e6', 'C1 n1 gnd 3.98n', 'E1 out gnd n1 gnd 1', '.ends']
    return '\n'.join(L)

def strip_deck(pos=None, sw=None, assign=None, default='OPA1612', resistors=None):
    """One strip, its input terminated in 50 ohm (the noise analysis' reference source), rails at +-17 V, its ground
    = 0 V. assign {unit name 'U6_1': part} picks each op-amp unit's noise model. resistors {ref: ohms} overrides values."""
    m = sc.Module('strip', 's', sc.STRIP, pos={'RV1': sc.FADER0, **{f'RV{k}': 0.0 for k in range(2, 8)}, **(pos or {})},
                  sw={'SW4': True, 'SW5': True, 'SW12': True, 'SW14': True, **(sw or {})},
                  plugs={'JB_J1': ('src', 1, 50, False)})
    m.gnd = '0'
    L = m.lines()
    out = []
    for line in L:
        mm = re.match(r'^Xs_(U\d+)_(\d) (.*) (OPA1612N|OPA1656N)$', line)
        if mm:                     # a unit fitted as OPA1656 (U16, strip v4.4) keeps that part unless assigned
            unit = f'{mm.group(1)}_{mm.group(2)}'
            part = (assign or {}).get(unit, default if mm.group(4) == 'OPA1612N' else 'OPA1656')
            out.append(f'Xs_{unit} {mm.group(3)} N_{part.replace(" ", "_")}')
            continue
        mr = re.match(r'^Rs_(R\d+) (\S+) (\S+) (\S+)$', line)
        if mr and resistors and mr.group(1) in resistors:
            out.append(f'Rs_{mr.group(1)} {mr.group(2)} {mr.group(3)} {resistors[mr.group(1)]}'); continue
        out.append(line)
    subs = [subckt('N_' + k.replace(' ', '_'), *v) for k, v in PARTS.items()]
    rails = ['VPB s_PVBUS 0 DC 17', 'VMB s_MVBUS 0 DC -17', '.model JMOD NJF(VTO=-2.5 BETA=6m LAMBDA=0.01)']
    nodes = set()
    for line in out:
        tk = line.split()
        if tk and tk[0][0] in 'RCLVEJX' and not line.startswith(('.', '*')):
            nodes.update(tk[1:5] if tk[0][0] in 'EX' else tk[1:4] if tk[0][0] == 'J' else tk[1:3])
    nodes -= {'0'}
    leaks = [f'RLEAK{i} {n} 0 1e9' for i, n in enumerate(sorted(n for n in nodes if not n.startswith('N_')))]
    return ['* strip noise deck (sim/review/strip_noise/noise.py)'] + subs + rails + out + leaks

def noise(body, node='s_PRE'):
    r, out = sc.run(body, [f'noise v({node}) vs_JB_J1 dec 20 20 20k', 'setplot noise2',
                           'let nd = db(onoise_total/0.7746)', 'print nd'])
    return r.get('nd')

UNITS = None
def units():
    global UNITS
    if UNITS is None:
        UNITS = sorted({re.match(r'^Xs_(U\d+_\d)', l).group(1) for l in strip_deck() if re.match(r'^Xs_U\d+_\d', l)},
                       key=lambda u: (int(u.split('_')[0][1:]), u))
    return UNITS

# impedance scaling of the EQ (response unchanged: every R and pot x k, every C / k)
EQ_R = ['R50', 'R51', 'R52', 'R53', 'R54', 'R55', 'R58', 'R59', 'R62', 'R63', 'R64', 'R65', 'R66', 'R67']
EQ_C = ['C41', 'C42', 'C43', 'C48', 'C49', 'C50', 'C69', 'C70', 'C71', 'C72', 'C73']
EQ_POT = ['RV10', 'RV11', 'RV13', 'RV15']
def scale_eq(body, k):
    out = []
    for line in body:
        t = line.split()
        if t and re.match(r'^[RC]s_(' + '|'.join(EQ_R + EQ_C) + r')$', t[0]):
            v = float(t[3]); out.append(' '.join(t[:3] + [str(v * k if t[0][0] == 'R' else v / k)])); continue
        if t and re.match(r'^Rs_(' + '|'.join(EQ_POT) + r')_\d[ab]$', t[0]):
            out.append(' '.join(t[:3] + [str(float(t[3]) * k)])); continue
        out.append(line)
    return out

# ---------------------------------------------------------------- N1 on strip v4.4 (2026-10-25)
N1 = ['U1', 'U5', 'U6', 'U7', 'U12', 'U13', 'U14', 'U15']      # high-impedance packages; U16 is already OPA1656
SETTINGS = [('gain 0 dB, EQ in', {}, {}), ('gain 0 dB, EQ in, HPF in (mid)', {'RV16': 0.5}, {'SW11': True}),
            ('gain 0 dB, EQ bypassed', {}, {'SW12': False}), ('gain +15 dB, EQ in', {'RV9': 1.0}, {}),
            ('gain +15 dB, EQ bypassed', {'RV9': 1.0}, {'SW12': False}),
            ('EQ in, every band +15 dB', {'RV10': 1, 'RV11': 1, 'RV13': 1, 'RV15': 1}, {}),
            ('EQ in, every band -15 dB', {'RV10': 0, 'RV11': 0, 'RV13': 0, 'RV15': 0}, {})]
FLAT = {'RV10': 0.5, 'RV11': 0.5, 'RV13': 0.5, 'RV15': 0.5, 'RV12': 0.5, 'RV14': 0.5, 'RV9': 0.5}

def n1_set(units_, part='OPA1656'):
    return {u: part for u in units_ if u.split('_')[0] in N1}

def t_n1():
    us = units()
    base = noise(strip_deck(pos=FLAT))
    res = noise(strip_deck(pos=FLAT, default='none', assign={u: 'none' for u in us}))
    print(f'PRE, gain 0 dB, EQ in (flat): as built {base:.1f} dBu, resistors only {res:.1f} dBu')
    print('unit contributions above the resistor floor (only that unit noisy), EQ in:')
    rows = []
    for u in us:
        part = 'OPA1656' if u.startswith('U16') else 'OPA1612'
        v = noise(strip_deck(pos=FLAT, assign={**{x: 'none' for x in us}, u: part}))
        add = 10 * __import__('math').log10(max(10 ** (v / 10) - 10 ** (res / 10), 1e-30))
        rows.append((add, u, part))
    for add, u, part in sorted(rows, reverse=True)[:12]: print(f'  {u:6s} {part}: {add:7.1f} dBu')
    print('PRE noise (dBu): setting | as built | N1 (OPA1656 in ' + ', '.join(N1) + ') | N1 with OPA1642')
    for label, pos, sw in SETTINGS:
        p = {**FLAT, **pos}
        a = noise(strip_deck(pos=p, sw=sw))
        b = noise(strip_deck(pos=p, sw=sw, assign=n1_set(us)))
        c = noise(strip_deck(pos=p, sw=sw, assign=n1_set(us, 'OPA1642')))
        print(f'  {label:32s} {a:7.1f} {b:7.1f} {c:7.1f}')

if __name__ == '__main__' and sys.argv[1:] == ['n1']:
    t_n1()
