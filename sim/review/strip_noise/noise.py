"""Strip noise budget: which op-amp stages (and which part of their noise) set the PRE noise, and what other op-amps or
lower impedances would do. Built from channel_strip.net + jack_board.net with tools/sim_console.py's module builder.
usage: python3 noise.py [attrib | parts | eqset]"""
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
        mm = re.match(r'^Xs_(U\d+)_(\d) (.*) OPA1612N$', line)
        if mm:
            unit = f'{mm.group(1)}_{mm.group(2)}'
            out.append(f'Xs_{unit} {mm.group(3)} N_{(assign or {}).get(unit, default).replace(" ", "_")}')
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
