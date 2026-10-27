"""CS2 (console_survey.md §5): the strip's pan law, as built (a linear 10K dual into unity followers: -6 dB at centre) and
with the Delta's network (ED3344C: each buffer at 1.22x, 2K2 / 10K, and 3K3 from its output back to its wiper).
The wiper of a linear pot at x (0 = ground end) is a source x * Vin behind Rth = x (1 - x) 10K; the 3K3 from the
buffer's output (G * W) feeds back: W = x Vin / (1 + Rth (1 - G) / 3K3). Also the constant-power (-3 dB) law for
reference, the power sum L^2 + R^2 across the travel, and what the level change does to the bus and the buffers'
headroom (sim/review/cs3/bus_headroom.py's figures). usage: python3 sim/review/cs2/pan_law.py"""
import math

R, RF, G = 10e3, 3.3e3, 1 + 2.2e3 / 10e3

def side(x, delta=True):
    if not delta: return x
    rth = x * (1 - x) * R
    return G * x / (1 + rth * (1 - G) / RF)

db = lambda v: 20 * math.log10(v) if v > 0 else -999

if __name__ == '__main__':
    print('1. one side against the pan position (0 = hard to the other side, 0.5 = centre, 1 = hard to this side), dB')
    print('   pos   as built   Delta    Delta - hard   const. power (sin/cos)')
    for k in range(11):
        x = k / 10
        a, d, cp = side(x, False), side(x), math.sin(x * math.pi / 2)
        print(f'   {x:4.1f}  {db(a):7.2f}  {db(d):7.2f}  {db(d) - db(side(1)):9.2f}     {db(cp):7.2f}')
    c, h = side(0.5), side(1.0)
    print(f'\n   centre {db(c):+.2f} dB, hard {db(h):+.2f} dB: the law {db(h) - db(c):.2f} dB (as built 6.02, constant power 3.01)')
    print('   power sum L^2 + R^2 against hard over, dB (0 = constant power):')
    for k in (0, 1, 2, 3, 4, 5):
        x = k / 10
        for name, f in (('as built', lambda y: side(y, False)), ('Delta', side)):
            p = (f(x) ** 2 + f(1 - x) ** 2) / f(1) ** 2
            print(f'     pos {x:3.1f} {name:8s}: {10 * math.log10(p):+6.2f} dB')
    print('\n2. levels and headroom (0 dBu in, gain at the detent, faders at "0"; cs3/bus_headroom.py, sim_console.py)')
    dc, dh = db(c) - db(0.5), db(h)
    print(f'   mix and subs per source: {dc:+.2f} dB at centre, {dh:+.2f} dB hard over (PAN off: unchanged, POST)')
    print(f'   summer per centred source: -6.4 -> {-6.4 + dc:.1f} dBu (29.5 -> {29.5 - dc:.1f} dB to clip)')
    print(f'   24 strips at nominal: summer +7.4 -> {7.4 + dc:.1f} dBu ({15.7 - dc:.1f} dB margin); main XLR +12.9 -> {12.9 + dc:.1f} dBu')
    print(f'   main L, one centred source at unity: -0.8 -> {-0.82 + 3.27:.1f} dBu (sim_console {2.45:+.2f})')
    print(f'   the pan buffers clip {dh:.1f} dB before POST when hard over: the overload LED (taps FPOST) misses that window')
