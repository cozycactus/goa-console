"""The strip's EQ and HPF response curves from the netlist (tools/sim_netlist.py's deck: channel_strip.net + the jack
board, ideal-ish op-amps), drawn like the families of curves in the service manuals: one chart per band, the gain pot
stepped from full cut to full boost; the swept mids at full boost / cut over the frequency range; the HPF at its sweep.
Writes SVG + PNG (rsvg-convert) to the folder given. usage: python3 sim/eq_curves.py OUTDIR"""
import os, re, sys, subprocess, tempfile, math
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = open(os.path.join(HERE, '..', 'tools', 'sim_netlist.py')).read()
G = {'__file__': os.path.join(HERE, '..', 'tools', 'sim_netlist.py'), '__name__': 'eqlib'}
OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
sys.argv = [sys.argv[0], os.path.join(HERE, '..', 'channel_strip.net'), os.path.join(HERE, '..', 'jack_board.net')]
exec(compile(SRC[:SRC.index('\nON = {')], 'sim_netlist', 'exec'), G)   # the deck builder, not its checks
deck = G['deck']
ON = {'SW4': True, 'SW12': True, 'SW14': True, 'SW5': True}            # channel on, EQ in
TOP = {'RV1': 1.0}

def sweep(pos, sw=ON):
    """PRE / input in dB, 10 Hz - 30 kHz (0 dBu in, gain at the detent)."""
    with tempfile.TemporaryDirectory() as td:
        fn = os.path.join(td, 'r.txt')
        d = deck({**TOP, **pos}, sw, '.control\nset noaskquit\nset wr_singlescale\nac dec 60 10 30k\n'
                 f'let g = db(v(PRE)/0.7746)\nwrdata {fn} g\n.endc')
        cir = os.path.join(td, 'd.cir'); open(cir, 'w').write(d)
        subprocess.run(['ngspice', '-b', cir], capture_output=True, text=True)
        return [tuple(map(float, l.split()[:2])) for l in open(fn) if l.strip() and not l.startswith(('f', ' f'))]

# ---------------------------------------------------------------- SVG chart in the manuals' style
W, H, L, R, T, B = 760, 440, 62, 20, 46, 46
F0, F1, D0, D1 = 10, 30e3, -18, 18
fx = lambda f: L + (math.log10(f) - math.log10(F0)) / (math.log10(F1) - math.log10(F0)) * (W - L - R)
dy = lambda g: T + (D1 - g) / (D1 - D0) * (H - T - B)
def chart(title, curves, note=''):
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="Helvetica, Arial, sans-serif">',
         f'<rect width="{W}" height="{H}" fill="white"/>', f'<text x="{L}" y="26" font-size="15" font-weight="bold">{title}</text>']
    if note: s.append(f'<text x="{W - R}" y="26" font-size="11" text-anchor="end" fill="#444">{note}</text>')
    for dec in range(1, 6):
        for m in range(1, 10):
            f = m * 10 ** dec
            if F0 <= f <= F1:
                x = fx(f); s.append(f'<line x1="{x:.1f}" y1="{T}" x2="{x:.1f}" y2="{H - B}" stroke="{"#999" if m == 1 else "#ddd"}" stroke-width="{1 if m == 1 else 0.6}"/>')
    for f, lab in ((10, '10'), (20, '20'), (50, '50'), (100, '100'), (200, '200'), (500, '500'), (1e3, '1k'), (2e3, '2k'),
                   (5e3, '5k'), (10e3, '10k'), (20e3, '20k')):
        s.append(f'<text x="{fx(f):.1f}" y="{H - B + 16}" font-size="11" text-anchor="middle">{lab}</text>')
    for g in range(D0, D1 + 1, 3):
        y = dy(g); s.append(f'<line x1="{L}" y1="{y:.1f}" x2="{W - R}" y2="{y:.1f}" stroke="{"#666" if g == 0 else ("#bbb" if g % 6 == 0 else "#e6e6e6")}" stroke-width="{1.2 if g == 0 else 0.6}"/>')
        if g % 6 == 0: s.append(f'<text x="{L - 6}" y="{y + 4:.1f}" font-size="11" text-anchor="end">{g:+d}</text>')
    s.append(f'<text x="{(L + W - R) / 2}" y="{H - 8}" font-size="11" text-anchor="middle">Hz</text>')
    s.append(f'<text x="16" y="{(T + H - B) / 2}" font-size="11" transform="rotate(-90 16 {(T + H - B) / 2})" text-anchor="middle">dB</text>')
    s.append(f'<rect x="{L}" y="{T}" width="{W - L - R}" height="{H - T - B}" fill="none" stroke="#333"/>')
    for pts, colour, width in curves:
        p = ' '.join(f'{fx(f):.1f},{dy(max(D0, min(D1, g))):.1f}' for f, g in pts if F0 <= f <= F1)
        s.append(f'<polyline points="{p}" fill="none" stroke="{colour}" stroke-width="{width}"/>')
    return '\n'.join(s + ['</svg>'])

def save(name, svg):
    p = os.path.join(OUT, name + '.svg'); open(p, 'w').write(svg)
    subprocess.run(['rsvg-convert', '-w', str(W * 2), p, '-o', p[:-4] + '.png'])
    print('wrote', p[:-4] + '.png')

STEPS = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]       # gain pot CCW (cut) .. CW (boost)
def family(ref, extra=None):
    out = []
    for th in STEPS:
        c = '#c0392b' if th > 0.5 else ('#1f4e9e' if th < 0.5 else '#000')
        out.append((sweep({ref: th, **(extra or {})}), c, 1.6 if th in (0.0, 0.5, 1.0) else 0.9))
    return out
def swept(gain, freq, other):
    out = []
    for g, c in ((1.0, '#c0392b'), (0.0, '#1f4e9e')):
        for fr in (0.0, 0.25, 0.5, 0.75, 1.0):
            out.append((sweep({gain: g, freq: fr, other: 0.5}), c, 1.6 if fr in (0.0, 1.0) else 0.9))
    out.append((sweep({}), '#000', 1.2))
    return out

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    save('eq_hf', chart('HF shelf (RV10): gain pot CCW to CW in tenths', family('RV10'), 'red boost, blue cut, black flat'))
    save('eq_lf', chart('LF shelf (RV15): gain pot CCW to CW in tenths', family('RV15'), 'red boost, blue cut, black flat'))
    save('eq_himid', chart('HI-MID (RV11 / RV12): full boost and cut, FREQ CCW .. CW', swept('RV11', 'RV12', 'RV14'),
                           'FREQ at 0, 1/4, 1/2, 3/4, 1 of its rotation'))
    save('eq_lomid', chart('LO-MID (RV13 / RV14): full boost and cut, FREQ CCW .. CW', swept('RV13', 'RV14', 'RV12'),
                           'FREQ at 0, 1/4, 1/2, 3/4, 1 of its rotation'))
    hpf = [(sweep({'RV16': th}, {**ON, 'SW11': True}), '#000', 1.6 if th in (0.0, 1.0) else 0.9) for th in STEPS]
    save('hpf', chart('HPF (RV16, HPF IN): FREQ CCW .. CW in tenths', hpf, '21 - 403 Hz, 12 dB / octave'))
    allb = [(sweep({'RV10': g, 'RV11': g, 'RV13': g, 'RV15': g, 'RV12': 0.5, 'RV14': 0.5}), c, 1.6)
            for g, c in ((1.0, '#c0392b'), (0.0, '#1f4e9e'))] + [(sweep({}), '#000', 1.2)]
    save('eq_all', chart('All four bands at full boost / full cut (mids at mid rotation)', allb))
