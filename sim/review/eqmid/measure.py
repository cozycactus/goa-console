"""EQM1: the mid bands measured on the strip netlist (tools/sim_netlist.py's deck: channel_strip.net + jack board): f0,
boost / cut and Q of each band at five rotations of its frequency pot, the other band's gain at centre.
usage: python3 sim/review/eqmid/measure.py"""
import os, re, sys, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..', '..', '..')
SRC = open(os.path.join(ROOT, 'tools', 'sim_netlist.py')).read()
G = {'__file__': os.path.join(ROOT, 'tools', 'sim_netlist.py'), '__name__': 'eqlib'}
sys.argv = [sys.argv[0], os.path.join(ROOT, 'boards', 'channel_strip', 'channel_strip.net'), os.path.join(ROOT, 'boards', 'jack_board', 'jack_board.net')]
exec(compile(SRC[:SRC.index('\nON = {')], 'sim_netlist', 'exec'), G)
deck = G['deck']
ON = {'SW4': True, 'SW12': True, 'SW14': True, 'SW5': True}
def meas(pos):
    with tempfile.TemporaryDirectory() as td:
        cir = os.path.join(td, 'd.cir')
        open(cir, 'w').write(deck({'RV1': 1.0, **pos}, ON, '.control\nset noaskquit\nac dec 400 20 30k\nlet g = db(v(PRE)/0.7746)\n'
                                  'meas ac pk max g\nmeas ac mn min g\nlet gn = g - pk + 3\nmeas ac flo when gn=0 rise=1\n'
                                  'meas ac fhi when gn=0 fall=1\n.endc'))
        out = subprocess.run(['ngspice', '-b', cir], capture_output=True, text=True).stdout
    r = {}
    for l in out.splitlines():
        m = re.match(r'^\s*(\w+)\s*=\s*([-+0-9.eE]+)(?:\s+at=\s*([-+0-9.eE]+))?', l)
        if m:
            r[m.group(1).lower()] = float(m.group(2))
            if m.group(3): r[m.group(1).lower() + '_at'] = float(m.group(3))
    return r
if __name__ == '__main__':
    for band, gain, freq, other in (('HI-MID', 'RV11', 'RV12', 'RV13'), ('LO-MID', 'RV13', 'RV14', 'RV11')):
        print(f'== {band}')
        for th in (0.0, 0.25, 0.5, 0.75, 1.0):
            b = meas({gain: 1.0, freq: th, other: 0.5}); c = meas({gain: 0.0, freq: th, other: 0.5})
            q = b['pk_at'] / (b['fhi'] - b['flo']) if b.get('fhi') and b.get('flo') else 0
            print(f'   freq {th:4.2f}: f0 {b["pk_at"]:7.0f} Hz, boost {b["pk"]:+5.2f} dB, cut {c["mn"]:+5.2f} dB, Q {q:4.2f}')
