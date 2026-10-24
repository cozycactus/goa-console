"""PRE noise with the HPF out / in at CCW, mid, CW (hpf_proposal.md). Run from the repo root of a tree with
hpf_proposal.patch applied (needs channel_strip.net with RV16); "base" runs the current Sallen-Key rows instead."""
import sys, os
sys.path.insert(0, os.getcwd() + '/sim/review/strip_noise'); os.chdir(os.getcwd())
import noise as N
rows = [('HPF out', {}, {}), ('HPF in, CCW', {'RV16': 0.0}, {'SW11': True}), ('HPF in, mid', {'RV16': 0.5}, {'SW11': True}),
        ('HPF in, CW', {'RV16': 1.0}, {'SW11': True})]
if 'base' in sys.argv: rows = [('HPF out', {}, {}), ('HPF in (87 Hz)', {}, {'SW11': True})]
for nm, pos, sw in rows:
    a = N.noise(N.strip_deck(pos=pos, sw=sw))
    b = N.noise(N.strip_deck(pos=pos, sw={**sw, 'SW12': False}))
    c = N.noise(N.strip_deck(pos=pos, sw=sw, default='none'))
    print(f'{nm:14s} EQ in {a:7.2f}   EQ bypassed {b:7.2f}   (EQ in, resistors only {c:7.2f}) dBu', flush=True)
