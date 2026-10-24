"""PRE low-frequency corner with the HPF out (hpf_proposal.md, C38 / C91). Run from the repo root."""
import sys, os
sys.path.insert(0, os.getcwd() + '/sim/review/strip_noise')
import noise as N, sim_console as sc
for nm, sw in (('HPF out, EQ in', {}), ('HPF out, EQ bypassed', {'SW12': False})):
    body = N.strip_deck(sw=sw, default='none')
    body = [l.replace('vs_JB_J1', 'vs_JB_J1') for l in body]
    r, out = sc.run(body, ['ac dec 100 0.05 2k', 'let g = db(mag(v(s_PRE)))', 'let g0 = g[length(g)-1]', 'let gn = g - g0',
                           'meas ac f3 when gn=-3 rise=1', 'meas ac g20 find gn at=20', 'let ph = 180/pi*(ph(v(s_PRE)) - ph(v(s_PRE))[length(g)-1])', 'meas ac p20 find ph at=20'])
    print(nm, {k: round(v, 3) for k, v in r.items()})
