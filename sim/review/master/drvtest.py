"""DRV134 (TI SBOM004A model) as on the master: 10u NP in each Sense loop, relay contact, cable C + 10K per leg."""
import numpy as np
from tian import ngspice, load, HERE, M
for cl in (0, 1e-9, 10e-9, 47e-9):
    for rl in (10e3, 600):
        d = f"""* drv134
.include {M}/DRV134.LIB
VP vp 0 16.9
VM vm 0 -16.9
VIN in 0 DC 0 AC 1 PULSE(0 0.1 1u 10n 10n 50u 100u)
RS in vin 10
X1 vo_n sn 0 vin vm vp sp vo_p DRV134
C1 vo_p sp 10u
C2 vo_n sn 10u
RK1 sp xp 0.05
RK2 sn xn 0.05
RL1 xp 0 {rl}
RL2 xn 0 {rl}
CL1 xp 0 {cl if cl else 1e-15}
CL2 xn 0 {cl if cl else 1e-15}
.control
set wr_singlescale
set wr_vecnames
ac dec 40 10 100meg
wrdata {HERE}/raw/drv_ac.txt v(xp) v(xn)
tran 2n 30u 0 2n
wrdata {HERE}/raw/drv_tr.txt v(xp) v(xn)
.endc
.end"""
        out = ngspice(d, 'drv')
        try:
            _, a = load(f'{HERE}/raw/drv_ac.txt'); f = a[:, 0]; hp = a[:, 1] + 1j*a[:, 2]; hn = a[:, 3] + 1j*a[:, 4]
            hd = hp - hn; g = 20*np.log10(abs(hd)); ref = np.interp(1e3, f, g)
            k = np.argmax(g); i20 = np.argmin(abs(f - 20e3)); f3 = f[np.argmax(g < ref - 3)] if (g < ref - 3).any() else None
            _, t = load(f'{HERE}/raw/drv_tr.txt'); tt = t[:, 0]; vd = t[:, 1] - t[:, 2]
            v0 = np.interp(0.9e-6, tt, vd); vf = np.mean(vd[(tt > 20e-6) & (tt < 30e-6)]); os_ = (vd[tt > 1e-6].max() - vf) / (vf - v0) * 100
            print(f'RL {rl:6.0f} CL {cl*1e9:5.1f} nF: diff gain {ref:+.2f} dB, peak {g[k]-ref:+.2f} dB @ {f[k]/1e6:.2f} MHz, 20k {g[i20]-ref:+.3f} dB, '
                  f'-3 dB {f3/1e6 if f3 else 0:.2f} MHz, step overshoot {os_:.1f} %')
        except Exception as e: print('ERR', e, out[-800:])
