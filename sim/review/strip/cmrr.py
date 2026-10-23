"""Receiver CMRR at RECV: common-mode source (tip and ring driven together, 50 R each) vs differential, none vs fix."""
import sys, re, numpy as np
from stripdeck import deck, ngspice, node, HERE
from fixes import FIXSETS
from configs import ON
for fs in ('none', 'CB_U1A=33p'):
    res = {}
    for mode in ('dm', 'cm'):
        d = deck({'RV1': 1.0}, ON, '', extra=FIXSETS[fs])
        if mode == 'cm':   # ring driven like the tip
            d = d.replace(f"RSR {node('J1','R')} {node('J1','S')} 50", f"RSR {node('J1','R')} src 50")
        fn = f'{HERE}/raw/cmrr_{mode}_{re.sub("[^A-Za-z0-9]","_",fs)}.txt'
        ctl = f'.control\nset noaskquit\nset wr_singlescale\nalter @VSRC[acmag] = 1\nac dec 10 100 100k\nwrdata {fn} v(RECV)\n.endc'
        ngspice(d.replace('\n.end', '\n' + ctl + '\n.end'), 'cm')
        dd = np.loadtxt(fn); res[mode] = (dd[:, 0], np.abs(dd[:, 1] + 1j * dd[:, 2]))
    f = res['dm'][0]; c = 20 * np.log10(res['dm'][1] / res['cm'][1])
    print(fs, ' '.join(f'{f[i]:.0f}Hz:{c[i]:.1f}dB' for i in range(0, len(f), 5)))
