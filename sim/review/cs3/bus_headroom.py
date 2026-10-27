"""CS3 (console_survey.md §5): headroom of the MIX summers and the master chain, from the whole-console model
(tools/sim_console.py: 24 strips, 4 groups, master, ribbon). AC at 1 kHz, 0 dBu into strip 1, pan centre, every fader
at its "0" mark: the level each stage carries per source. Every op-amp output swings +-15.5 V = +23.0 dBu
(sim/review/gaps/headroom.py). usage: python3 sim/review/cs3/bus_headroom.py"""
import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools'))
import sim_console as sc

CLIP = 20 * math.log10(15.5 / math.sqrt(2) / 0.7746)
XLR_CLIP = 27.0                                       # DRV134 / DRV135 balanced output, TI datasheet: +27 dBu
NODES = [('strip PRE', 'v(s01_PRE)'), ('strip POST (fader "0", +10 dB post-amp)', 'v(s01_POST)'),
         ('strip PANL (pan centre)', 'v(s01_PANL)'), ('master SUM_L (summer out)', 'v(SUM_L)'),
         ('master MIX_L (re-inverter)', 'v(MIX_L)'), ('master PRE_L (fader top)', 'v(PRE_L)'),
         ('master post-amp out (MST_L_FPOST)', 'v(MST_L_FPOST)'), ('main L XLR (differential)', sc.diff(sc.XLR['L']))]

def levels(strip_over=None, master_pos=None):
    s, g, m = sc.default_console(sc.one(0, pos=strip_over or {}), master_cfg={'pos': master_pos} if master_pos else None)
    ctl = sc.AC1K
    for i, (_, e) in enumerate(NODES): ctl = ctl + sc.dbu(e, f'n{i}')
    r, _ = sc.run(sc.console(s, g, m), ctl)
    return [r.get(f'n{i}') for i in range(len(NODES))]

if __name__ == '__main__':
    lv = levels()
    print(f'per source: 0 dBu in, pan centre, faders at "0" (clip {CLIP:.1f} dBu at any op-amp output)')
    for (n, _), l in zip(NODES, lv):
        c = XLR_CLIP if 'XLR' in n else CLIP
        print(f'  {n:44s} {l:6.1f} dBu   headroom {c - l:5.1f} dB')
    sumL, xlr = lv[3], lv[7]
    print('\nN strips at their nominal level (PRE 0 dBu), pan centre, uncorrelated (sine-equivalent rms), master fader at "0":')
    for n in (1, 8, 16, 24):
        add = 10 * math.log10(n)
        print(f'  {n:2d} strips: summer {sumL + add:5.1f} dBu (margin {CLIP - sumL - add:4.1f} dB), main XLR {xlr + add:5.1f} dBu '
              f'(margin {XLR_CLIP - xlr - add:4.1f} dB)')
    d = (CLIP - sumL) - (XLR_CLIP - xlr)
    print(f'\nwith the master fader at "0" the summer has {d:+.1f} dB more margin than the XLR output; it becomes the first')
    print(f'stage to clip only with the master fader more than {d:.1f} dB below "0" (the meters, after the fader, then read low)')
