"""Sanity check of each op-amp model: unity-gain follower loop (Tian), Zo, input C."""
from tian import *
MODELS = {'OPA1612': (f'.include {M}/OPA161x.LIB', 'OPA161x'), 'OPA1656': (f'.include {M}/OPA1656.LIB', 'OPA1656'),
          'TL072old': (f'.include {M}/TL072_boyle.lib', 'TL072'), 'TL07xH': (f'.include {M}/tl07xh_tl08xh.lib', 'TL07XH_TL08XH')}
for name, (inc, sub) in MODELS.items():
    for cl in (0, 20e-12, 100e-12):
        d = f"""* {name} follower
{inc}
VCC vcc 0 17
VEE vee 0 -17
VIN inp 0 0
X1 inp out_x vcc vee out_x_o {sub}
VTI out_x_o out_x DC 0 AC 0
ITI 0 out_x_o DC 0 AC 0
RL out_x 0 10k
CL out_x 0 {cl}
.control
set wr_singlescale
set wr_vecnames
alter @VTI[acmag] = 1
ac dec 50 1k 1g
wrdata {HERE}/raw/mt_v.txt v(out_x_o) v(out_x)
destroy all
alter @VTI[acmag] = 0
alter @ITI[acmag] = 1
ac dec 50 1k 1g
wrdata {HERE}/raw/mt_i.txt i(VTI)
.endc
.end"""
        out = ngspice(d, 'mt')
        try:
            f, T = loopgain(f'{HERE}/raw/mt_v.txt', f'{HERE}/raw/mt_i.txt')
            print(name, f'CL={cl*1e12:.0f}p', margins(f, T))
        except Exception as e: print(name, 'ERR', e, out[-1500:])
