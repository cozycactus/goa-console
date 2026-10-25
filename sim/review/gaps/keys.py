"""Clicks from the strip's keys (2026-10-25): the DC step each panel key puts on the buses when it switches, with the
op-amps' real DC errors. One strip (tools/sim_console.py's module from channel_strip.net + jack_board.net) on ideal
virtual-earth summers (MIX L/R, SUB 1-4: 4K7; AUX 1-6, PFL: 22K), input terminated in 50 ohm, no programme. The key
under test is toggled at 0.3 s; the largest excursion of each summer output after it is the click.
Op-amp DC errors drawn per unit (Monte Carlo, uniform): OPA1612 Vos +-500 uV (datasheet max), bias current 60-250 nA
into both inputs with +-25 nA offset; OPA1656 (U16) Vos +-1.5 mV, no bias current. The PVA2 contacts switch in 1 us.
Routing keys are not here: their DG413s switch with logic (sim/routing_switch.cir covers that click).
usage: python3 sim/review/gaps/keys.py [samples]   (since K1 the PFL send's C96 is in the netlist itself)"""
import os, re, sys, math, random, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'tools'))
import sim_console as sc

BUSES = {'MIXL': 4.7e3, 'MIXR': 4.7e3, 'SUB1': 4.7e3, 'SUB2': 4.7e3, 'SUB3': 4.7e3, 'SUB4': 4.7e3,
         'AUX1': 22e3, 'AUX2': 22e3, 'AUX3': 22e3, 'AUX4': 22e3, 'AUX5': 22e3, 'AUX6': 22e3, 'PFL': 22e3}
KEYS = [('SW4', 'ON'), ('SW3', 'PFL'), ('SW8', 'PRE 1-2'), ('SW9', 'PRE 3-4'), ('SW10', 'PRE 5-6'), ('SW11', 'HPF IN'),
        ('SW12', 'EQ IN'), ('SW13', 'DIR'), ('SW14', 'PAN'), ('SW15', 'phase')]
BASE_SW = {'SW4': True, 'SW5': True, 'SW12': True, 'SW14': True}           # ON, L-R, EQ in, PAN
POS = {'RV1': sc.FADER0, **{f'RV{k}': 0.5 for k in range(2, 8)}}            # fader at "0", aux sends at mid
TSW = 0.3

def deck(key, rnd):
    on0 = BASE_SW.get(key, False)
    m = sc.Module('strip', 's', sc.STRIP, pos=POS, sw={**BASE_SW, key: on0}, plugs={'JB_J1': ('src', 0, 50, False)})
    m.gnd = '0'
    out = ['* strip key clicks (sim/review/gaps/keys.py)', sc.OPA_DEF, 'VPB s_PVBUS 0 DC 17', 'VMB s_MVBUS 0 DC -17',
           '.model SWK SW(VT=0.5 VH=0.01 RON=0.02 ROFF=1e10)',
           f'VKEY key 0 PWL(0 {1 if on0 else 0} {TSW} {1 if on0 else 0} {TSW + 1e-6} {0 if on0 else 1})']
    for line in m.lines():
        mx = re.match(r'^(Xs_(U\d+)_\d) (\S+) (\S+) (\S+) (\S+) (OPA1612N|OPA1656N)$', line)
        if mx:
            name, unit, p, n, o, g, sub = mx.groups()
            vos = rnd.uniform(-1.5e-3, 1.5e-3) if sub == 'OPA1656N' else rnd.uniform(-500e-6, 500e-6)
            ib = 0 if sub == 'OPA1656N' else rnd.uniform(60e-9, 250e-9); io = 0 if sub == 'OPA1656N' else rnd.uniform(-25e-9, 25e-9)
            out += [f'V{name}_os {name}_p {p} DC {vos}', f'{name} {name}_p {n} {o} {g} {sub}',
                    f'I{name}_bp {p} 0 DC {ib + io / 2}', f'I{name}_bn {n} 0 DC {ib - io / 2}']
            continue
        mk = re.match(rf'^Rs_{key}_(\d) (\S+) (\S+) 0\.02$', line)
        if mk:                                             # the key's contacts become switches on VKEY
            c = int(mk.group(1)); t_on, t_off = {2: (1, 3), 5: (4, 6)}[c]
            com, a, b = m.node(key, c), m.node(key, t_on), m.node(key, t_off)
            out += [f'S{key}_{c}on {com} {a} key 0 SWK', f'S{key}_{c}off {com} {b} 0 key SWK']
            continue
        out.append(line)
    for bus, rf in BUSES.items():                          # virtual-earth summers (ideal), output = -sum
        nb = f's_{bus}'
        out += [f'E{bus} {bus}_O 0 0 {nb} 1e6', f'RF{bus} {bus}_O {nb} {rf}']
    nodes = set()
    for line in out:
        t = line.split()
        if t and not line.startswith(('.', '*')) and t[0][0] in 'RCLVEIJXS':
            nodes.update(t[1:5] if t[0][0] in 'EXS' else t[1:4] if t[0][0] == 'J' else t[1:3])
    nodes -= {'0', 'inp', 'inn', 'out', 'gnd', 'key'}
    out += [f'RLEAK{i} {nn} 0 1e9' for i, nn in enumerate(sorted(nodes))]
    probes = ' '.join(f'v({b}_O)' for b in BUSES)
    return out, probes

def run(key, seed):
    body, probes = deck(key, random.Random(seed))
    ctl = ['.options method=gear', f'tran 50u {TSW + 0.25} {TSW - 0.05} 50u uic' if False else f'tran 50u {TSW + 0.25} 0 50u',
           f'wrdata /tmp/keys_{key}.txt {probes}']
    sc.run(body, ctl)
    rows = [list(map(float, l.split())) for l in open(f'/tmp/keys_{key}.txt') if l.strip() and l.split()[0][0] in '0123456789']
    worst = {}
    for i, bus in enumerate(BUSES):
        before = [r[2 * i + 1] for r in rows if TSW - 0.02 < r[0] < TSW]
        after = [r[2 * i + 1] for r in rows if TSW < r[0]]
        if before and after:
            ref = sum(before) / len(before)
            worst[bus] = max(abs(x - ref) for x in after)
    return worst

if __name__ == '__main__':
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    print(f'{n} offset draws per key; largest step on any bus output (mV, and dBu peak-equivalent), and which bus')
    for key, name in KEYS:
        res = [run(key, s) for s in range(n)]
        w = max(((v, b) for r in res for b, v in r.items()), default=(0, '-'))
        med = sorted(max(r.values()) for r in res)[n // 2]
        print(f'  {key:5s} {name:8s}: worst {w[0] * 1e3:7.3f} mV on {w[1]:5s} ({20 * math.log10(max(w[0], 1e-12) / math.sqrt(2) / 0.7746):6.1f} dBu), median {med * 1e3:6.3f} mV', flush=True)
