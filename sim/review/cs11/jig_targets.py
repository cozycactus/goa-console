"""CS11 (docs/studies/console_survey.md §7): targets for the five jig tests it adds to test_jig_spec.md.
1. Output balance of a DRV135 output (TI's DRV134 model, SBOM004A): each leg into 1 kohm 0.1 % to ground, the common-
   mode part (V+ + V-) / 2 against the differential V+ - V-; the jig stub as built (10 uF NP per leg, no loop resistor)
   and the console's (22R inside the loop, CS4c), with the two 10 uF at nominal and 20 % apart.
2. Line-input CMR of a strip from the exported netlists (the strip + jack board, ideal resistors: what the layout's
   capacitors leave, C8 / C9 at the jack and C94 / C95 at the followers), against a 1 kohm source on the tip leg and a
   matched pair of 100 ohm; the resistor tolerance is docs/studies/ground_study.md §5.2's Monte Carlo (worst 5 % at 50 Hz).
3. Fader breakthrough and pan isolation against the pots' end resistance (the wiper at its end stop).
4. MIX L noise with N channels routed and every fader down (the summer, 4K7 per source and feedback, OPA1612; the
   stub's re-inverter; 20 Hz-20 kHz), N = 4...24 on the load board.
5. The GCANCEL conductor's current: each strip's 10R R5 to the line, the line held at the mean of the strip grounds.
usage: TI_MODELS=<folder> python3 sim/review/cs11/jig_targets.py   (section 1 needs TI's model; skipped without)"""
import os, re, sys, math, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
M = os.environ.get('TI_MODELS', '')
K, T = 1.380649e-23, 300.0
BW = 20e3 - 20

def ng(deck, cwd=None):
    with tempfile.NamedTemporaryFile('w', suffix='.cir', delete=False) as f: f.write(deck)
    out = subprocess.run(['ngspice', '-b', f.name], capture_output=True, text=True, cwd=cwd)
    os.unlink(f.name)
    return {k.lower(): float(v) for k, v in re.findall(r'^(\w+)\s+=\s+([-+0-9.eE]+)', out.stdout, re.M)}

def balance(rx, cn):
    """dB of the common-mode part against the differential output, at 100 Hz / 1 kHz / 20 kHz"""
    d = f"""* drv135 output balance
.include {M}/DRV134.LIB
VP vp 0 16.9
VM vm 0 -16.9
VIN in 0 DC 0 AC 1
RS in vin 47
X1 von sn 0 vin vm vp sp vop DRV134
RXP vop vopr {max(rx, 1e-3)}
RXN von vonr {max(rx, 1e-3)}
CP vopr sp 10u
CN vonr sn {cn}
RLP sp 0 1k
RLN sn 0 1k
.control
ac lin 3 100 100
let a1 = db(abs((v(sp)+v(sn))/2)/abs(v(sp)-v(sn)))
print a1
ac lin 1 1k 1k
let a2 = db(abs((v(sp)+v(sn))/2)/abs(v(sp)-v(sn)))
print a2
ac lin 1 20k 20k
let a3 = db(abs((v(sp)+v(sn))/2)/abs(v(sp)-v(sn)))
print a3
.endc
.end"""
    r = ng(d, cwd=os.path.join(ROOT, 'sim', 'review', 'cs4'))       # its .spiceinit sets PSpice compatibility
    return r.get('a1'), r.get('a2'), r.get('a3')

def netlist_ns():
    """sim_netlist.py's deck builder without its checks: the source up to its first measurement, run here"""
    src = open(os.path.join(ROOT, 'tools', 'sim_netlist.py')).read()
    cut = src.index("r = run(TOP, ON, AC1K")
    sys.path.insert(0, os.path.join(ROOT, 'tools'))
    ns = {'__name__': 'cs11', '__file__': os.path.join(ROOT, 'tools', 'sim_netlist.py')}
    argv = sys.argv; sys.argv = ['sim_netlist.py', os.path.join(ROOT, 'channel_strip.net'), os.path.join(ROOT, 'jack_board.net')]
    exec(compile(src[:cut], 'sim_netlist.py', 'exec'), ns); sys.argv = argv
    return ns

def cmr(ns, src, f):
    node = ns['node']
    if src == '1k':
        lines = [f"VSRC src {node('J1','S')} DC 0 AC 0.7746", f"RST src {node('J1','T')} 1k", f"RSR src {node('J1','R')} 0.05"]
    else:
        lines = [f"VSRC src {node('J1','S')} DC 0 AC 0.7746", f"RST src {node('J1','T')} 100", f"RSR src {node('J1','R')} 100.01"]
    ns['SOURCE'] = lambda: lines
    r = ns['run'](ns['TOP'], ns['ON'], f'ac lin 1 {f} {f}', ['let x = db(mag(v(PRE))/0.7746 + 1e-15)', 'print x'])
    return -r.get('x', float('nan'))              # PRE is at unity for a differential signal: CMR = 0 dBu - PRE

def summer_noise(n):
    """V rms at MIX L: summer with n sources of 4K7 (the strips' and the load board's), Rf 4K7, OPA1612 (1.1 nV, 1.7 pA),
    then the stub's re-inverter (2K2 x 4, OPA1612, noise gain 2)"""
    en, inn, r = 1.1e-9, 1.7e-12, 4.7e3
    er = math.sqrt(4 * K * T * r)
    s2 = ((1 + n) * en) ** 2 + (inn * r) ** 2 + n * er ** 2 + er ** 2
    e22 = math.sqrt(4 * K * T * 2.2e3)
    r2 = (2 * en) ** 2 + 2 * e22 ** 2 + (2 * math.sqrt(4 * K * T * 1.1e3)) ** 2 + (inn * 2.2e3) ** 2
    return math.sqrt((s2 + r2) * BW)

if __name__ == '__main__':
    print('1. DRV135 output balance, 1 kohm 0.1 % per leg: common mode against differential (dB) at 100 Hz / 1 kHz / 20 kHz')
    if M and os.path.exists(f'{M}/DRV134.LIB'):
        for rx, name in ((0, 'jig stub (no loop resistor)'), (22, 'console (22R in the loop, CS4c)')):
            for cn, cname in ((10e-6, 'both 10 uF'), (8e-6, '10 / 8 uF (20 % apart)')):
                a = balance(rx, cn)
                print(f'   {name:32s} {cname:24s}: ' + ' / '.join(f'{x:6.1f}' for x in a), flush=True)
    else: print('   (set TI_MODELS: skipped)')

    print('\n2. Line-input CMR of a strip (netlist, ideal resistors: the capacitors\' limit), dB')
    ns = netlist_ns()
    for src, name in (('1k', '1 kohm on the tip leg (a synth)'), ('100', 'matched 100 ohm pair (0.01 %)')):
        print(f'   {name:34s}: ' + ', '.join(f'{f:5d} Hz {cmr(ns, src, f):5.1f}' for f in (50, 1000, 10000, 20000)), flush=True)
    print('   with 0.1 % bridge resistors (ground_study.md §5.2, 50 Hz, median / worst 5 %): 1 kohm 60.0 / 54.1, 100 ohm 68.0 / 58.7')

    print('\n3. End-stop residuals against the pot\'s end resistance r (dB)')
    a0 = 10 ** (-10.19 / 20)                     # the fader's "0" mark: the wiper at ~31 % of the track
    for r in (0.1, 0.3, 1, 3, 10, 20):
        fb = 20 * math.log10(r / (10e3 * a0)); pan = 20 * math.log10(r / 10e3)
        print(f'   r {r:5.1f} ohm: fader down against its "0" mark {fb:6.1f} dB;  pan hard over, the far side {pan:6.1f} dB')

    print('\n4. MIX L noise, every fader down, N channels routed (4 strips + the load board), 20 Hz-20 kHz unweighted')
    for n in (4, 8, 12, 16, 20, 24):
        v = summer_noise(n)
        print(f'   N {n:2d}: {20 * math.log10(v / 0.7746):6.1f} dBu')

    print('\n5. GCANCEL: each module\'s 10R R5 to the line; the master end draws nothing (100K keeper, follower inputs).')
    print('   A module whose ground sits dV from the mean of the others drives dV / (10 + 10 / (m - 1)) through its R5.')
    for m, dv, what in ((5, 1e-4, 'normal running: ~0.1 mV between strip grounds (spade wires, return currents)'),
                        (5, 0.1, 'test 2: 100 mV injected in one strip\'s spade lead')):
        i = dv / (10 + 10 / (m - 1))
        print(f'   {what}: {m} modules on the line (4 strips + load board): {i * 1e3:6.3f} mA in that strip\'s R5, '
              f'{i * 10 * 1e3:6.3f} mV across it')
