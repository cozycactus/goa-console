"""CS2b (docs/proposals/cs2b_proposal.md): the group's sub pan to MIX. As built: the linear 10K dual RV2 (ALPS RK09L) into unity
followers U3B / U5A, a plain -6 dB. CS2b: the strip's network (CS2, ED3344C): each buffer at 1.22x with 3K3 from its
output back to its wiper (pan_law.side()). For reference the parent's group module, ED2778A "MONITOR PAN": passive, a
10K LIN CD dual with 3K9 from the source to each wiper and 8K2 from the wiper into the MIX virtual earth (no buffer).
Wiper of that network at x (0 = ground end): (V - W) (1/3K9 + 1/((1 - x) 10K)) = W (1/(x 10K) + 1/8K2).
Also the level through a group (strip pan, then sub pan, both centred) against a strip routed to MIX directly.
usage: python3 sim/review/cs2/group_pan.py"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pan_law import side, db

def ed2778(x, rs=3.9e3, r=10e3, rb=8.2e3):
    if x >= 1: return 1.0
    if x <= 0: return 0.0
    g_top = 1 / rs + 1 / ((1 - x) * r)
    return g_top / (g_top + 1 / (x * r) + 1 / rb)

if __name__ == '__main__':
    print('1. one side of the sub pan against the position (0 = hard to the other side, 0.5 = centre, 1 = hard to this side), dB')
    print('   pos   as built   CS2b    CS2b - hard   ED2778A (passive, to hard)')
    for k in range(11):
        x = k / 10
        print(f'   {x:4.1f}  {db(x):7.2f}  {db(side(x)):7.2f}  {db(side(x)) - db(side(1)):9.2f}     {db(ed2778(x)):7.2f}')
    c, h, e = side(0.5), side(1.0), ed2778(0.5)
    print(f'\n   law (hard over against centre): as built 6.02 dB, CS2b {db(h) - db(c):.2f} dB, ED2778A {-db(e):.2f} dB')
    print('   power sum L^2 + R^2 at centre against hard over: as built '
          f'{10 * math.log10(2 * 0.25):+.2f}, CS2b {10 * math.log10(2 * c * c / (h * h)):+.2f}, ED2778A {10 * math.log10(2 * e * e):+.2f} dB')
    dc, dh = db(c) - db(0.5), db(h)
    print(f'\n2. levels (0 dBu in, faders at "0"): sub to MIX {dc:+.2f} dB at centre, {dh:+.2f} dB hard over')
    print('   a strip centred into SUB 1, the sub centred into MIX, against the same strip routed to MIX directly:')
    for name, pc, gc in (('as built (before CS2)', 0.5, 0.5), ('strip v5.4 (CS2), group as built', c, 0.5), ('CS2b', c, c)):
        print(f'     {name:34s}: via the group {db(pc) + db(gc):+6.2f} dB, direct {db(pc):+6.2f} dB, '
              f'the group path {-db(gc):.2f} dB below')
    print(f'   hard over the pan buffers carry S_POST {dh:+.1f} dB: they clip {dh:.1f} dB before the sub post-amp')
