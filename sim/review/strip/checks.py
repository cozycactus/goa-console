"""The 30 checks of tools/sim_netlist.py, run on stripdeck.deck() (model ti|sp, optional extra caps).
usage: python3 checks.py ti|sp [fixset]   -> prints each check with its value (4 decimals) and a JSON line."""
import sys, re, json
from stripdeck import deck, ngspice, node
from fixes import FIXSETS

MODEL = sys.argv[1] if len(sys.argv) > 1 else 'ti'
EXTRA = FIXSETS[sys.argv[2]] if len(sys.argv) > 2 else []

def run(pos, sw, analysis, measures):
    ctl = '.control\nset noaskquit\nalter @VSRC[acmag] = 0.7746\n' + analysis + '\n' + '\n'.join(measures) + '\n.endc'
    out = ngspice(deck(pos, sw, ctl, model=MODEL, extra=EXTRA), 'chk')
    res = {}
    for line in out.splitlines():
        m = re.match(r'^(\w+)\s+=\s+([-+0-9.eE]+)', line)
        if m: res[m.group(1).lower()] = float(m.group(2))
    return res

ON = {'SW4': True, 'SW12': True, 'SW14': True, 'SW5': True}
TOP = {'RV1': 1.0}
checks = []; vals = {}
def check(name, got, lo, hi, unit='dB'):
    ok = got is not None and lo <= got <= hi
    checks.append(ok); vals[name] = got
    print(f"{'ok  ' if ok else 'FAIL'} {name}: {got if got is None else round(got, 4)} {unit} (expected {lo} .. {hi})", flush=True)

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
r = run(TOP, {**ON, 'SW11': True}, 'ac dec 100 5 20k', ['let g = db(v(PRE)/0.7746)', 'meas ac f3 when g=-3 rise=1'])
check('HPF in: -3 dB frequency at PRE', r.get('f3'), 80, 95, 'Hz')
for ref, pos_, at, lo, hi, label in (('RV10', 1, 12e3, 10.5, 12.5, 'HF CW at 12 kHz'), ('RV10', 0, 12e3, -12.5, -10.5, 'HF CCW at 12 kHz'),
                                     ('RV11', 1, 670, 13.5, 15.5, 'HI-MID CW, freq CCW, at 670 Hz'),
                                     ('RV13', 1, 148, 13.5, 15.5, 'LO-MID CW, freq CCW, at 148 Hz'),
                                     ('RV15', 1, 54, 13.3, 15.3, 'LF CW at 54 Hz'), ('RV15', 0, 54, -15.3, -13.3, 'LF CCW at 54 Hz')):
    r = run({**TOP, ref: pos_, 'RV12': 0.0, 'RV14': 0.0}, ON, f'ac lin 1 {at} {at}', [dbu('PRE'), 'print x_PRE'])
    check(label, r.get('x_pre'), lo, hi)
for ref, at, lo, hi, label in (('RV12', 10.5e3, 13.5, 15.5, 'HI-MID CW, freq CW, at 10.5 kHz'),
                               ('RV14', 2.31e3, 13.5, 15.5, 'LO-MID CW, freq CW, at 2.31 kHz')):
    gain = 'RV11' if ref == 'RV12' else 'RV13'
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
print('JSON', json.dumps(vals))
