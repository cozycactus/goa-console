"""Audio-band cost of a fix set: AC 20 Hz-20 kHz (TI model) over pot/switch states, none vs fixset.
usage: python3 audio.py <fixset>  -> max |delta dB| and |delta deg| per node, and the state where it occurs"""
import sys, os, re, json, itertools, numpy as np
from stripdeck import deck, ngspice, node, HERE
from fixes import FIXSETS
from configs import ON
fx = sys.argv[1]; model = sys.argv[2] if len(sys.argv) > 2 else 'ti'
NODES = ['RECV', 'GOUT', 'HOUT', 'EQ_O3', 'EQ_O4', 'EQ_O5', 'EQ_O6', 'EQ_MP', 'EQ_LP', 'EQ_MHP', 'EQ_LHP', 'EQ_FP',
         'BUF1', 'PRE', 'MUTEOUT', 'FPOST', 'POST', 'PBL', 'PBR', 'DOUT', node('J5', 'T'), 'MIXL_O', 'MIXR_O']
S = {}
S['flat'] = ({'RV1': 1.0}, ON)
for g in (0, 1):
    for f in (0, 0.5, 1):
        S[f'HM g{g} f{f}'] = ({'RV1': 1.0, 'RV11': g, 'RV12': f}, ON)
        S[f'LM g{g} f{f}'] = ({'RV1': 1.0, 'RV13': g, 'RV14': f}, ON)
    S[f'HF g{g}'] = ({'RV1': 1.0, 'RV10': g}, ON); S[f'LF g{g}'] = ({'RV1': 1.0, 'RV15': g}, ON)
    for f in (0, 1):
        S[f'all g{g} f{f}'] = ({'RV1': 1.0, 'RV10': g, 'RV11': g, 'RV13': g, 'RV15': g, 'RV12': f, 'RV14': f}, ON)
S['gain CCW'] = ({'RV1': 1.0, 'RV9': 0}, ON); S['gain CW'] = ({'RV1': 1.0, 'RV9': 1}, ON)
S['HPF in, phase'] = ({'RV1': 1.0}, {**ON, 'SW11': True, 'SW15': True})
S['EQ out'] = ({'RV1': 1.0, 'RV10': 1, 'RV11': 1}, {**ON, 'SW12': False})
S['fader 0'] = ({'RV1': 0.6}, ON); S['fader mid'] = ({'RV1': 0.5}, ON)
S['pan L'] = ({'RV1': 1.0, 'RV8': 0}, ON); S['pan R'] = ({'RV1': 1.0, 'RV8': 1}, ON)
S['DIR aux6 mid'] = ({'RV1': 1.0, 'RV7': 0.5}, {**ON, 'SW13': True, 'SW10': True})
S['DIR aux6 top'] = ({'RV1': 1.0, 'RV7': 1.0}, {**ON, 'SW13': True, 'SW10': True})
os.makedirs(f'{HERE}/raw', exist_ok=True)
def sweep(extra, tag):
    out = {}
    for i, (name, (pos, sw)) in enumerate(S.items()):
        fn = f'{HERE}/raw/aud_{tag}_{i}.txt'
        ctl = '\n'.join(['.control', 'set noaskquit', 'set wr_singlescale', 'alter @VSRC[acmag] = 1',
                         'ac dec 40 20 20k', f'wrdata {fn} ' + ' '.join(f'v({n})' for n in NODES), '.endc'])
        ngspice(deck(pos, sw, ctl, model=model, extra=extra), 'aud')
        d = np.loadtxt(fn); f = d[:, 0]
        out[name] = (f, {n: d[:, 1 + 2 * k] + 1j * d[:, 2 + 2 * k] for k, n in enumerate(NODES)})
    return out
safe = re.sub(r'[^A-Za-z0-9]', '_', fx)
A = sweep([], 'none_' + safe + '_' + model); B = sweep(FIXSETS[fx], safe + '_' + model)
res = {}
print(f'fixset {fx} ({model}): max |delta| 20 Hz-20 kHz over {len(S)} states (state)')
for n in NODES:
    worst = (0, '', 0, 0, '')
    for st in S:
        a, b = A[st][1][n], B[st][1][n]
        ok = np.abs(a) > 0.01 * np.abs(a).max()
        if not ok.any(): continue
        dd = np.abs(20 * np.log10(np.abs(b[ok]) / np.abs(a[ok])))
        dp = np.abs(np.degrees(np.angle(b[ok] / a[ok])))
        if dd.max() > worst[0]: worst = (dd.max(), st, A[st][0][ok][dd.argmax()], dp.max(), st)
        if dp.max() > worst[3]: worst = (worst[0], worst[1], worst[2], dp.max(), st)
    res[n] = worst
    print(f'  {n:10} {worst[0]:.4f} dB at {worst[2]:7.0f} Hz ({worst[1]});  {worst[3]:.2f} deg ({worst[4]})')
# the strip at PRE: deviation at 20 kHz per state
print('PRE at 20 kHz, none -> fix (dB):', '; '.join(f"{st}: {20*np.log10(abs(A[st][1]['PRE'][-1])):.3f}->{20*np.log10(abs(B[st][1]['PRE'][-1])):.3f}" for st in S if 'g1' in st or st == 'flat'))
