"""Configuration matrix for the master stability runs."""
import json
from masterdeck import UNITS, outnet
L = json.load(open('master_len.json'))
POTS = ('RV1', 'RV2', 'RV3', 'RV4', 'RV5', 'RV6')
def pots(p): return {r: p for r in POTS}
# trace estimate: 0.065 pF per mm of pad-to-pad MST (0.5 pF/cm x 1.3 routing factor), nets over 20 mm
PLACED = {n: round(v['mst'] * 0.065e-12, 15) for n, v in L.items() if v['mst'] > 20 and n not in
          ('GNDA', 'GNDD', 'GNDM', 'PHONESGND', 'CHASSIS', '+VA', '-VA', '+VP', '-VP', '+VM', '-VM', '+VL', '-VL', '+VBUS', '-VBUS',
           '+5VL', 'RLY_DRV')}
NONPH = [u for u in UNITS if u not in ('U26A', 'U26B', 'U27', 'U28')]
OUTS = {u: outnet(u) for u in NONPH}
FAR = {'MST_L_FPOST': 'POST_L', 'MST_R_FPOST': 'POST_R', 'MIX_L_RBUF': 'PRE_L', 'MIX_R_RBUF': 'PRE_R',
       # master v0.8: the long net is beyond each build-out (MG1, MG3, MG6, MG9)
       'CRSB_LO': 'CRSB_L', 'CRSB_RO': 'CRSB_R', 'PFL_SIGO': 'PFL_SIG', 'EXT_BL': 'EXT_L', 'EXT_BR': 'EXT_R',
       'ML_DETO': 'ML_DET', 'MR_DETO': 'MR_DET'}   # the long net is beyond the 220u
def outload(c): return {FAR.get(OUTS[u], OUTS[u]): c for u in NONPH if 'SPARE' not in OUTS[u]}
INS_UNIT = (100, 300e-12, 10e3, 300e-12)
CONFIGS = {
 'p000': dict(pos=pots(0.0)),
 'p050': dict(pos=pots(0.5)),
 'p075': dict(pos=pots(0.75)),
 'p100': dict(pos=pots(1.0)),
 'p075_pfl_afl': dict(pos=pots(0.75), pfl_on=True, sw={'SW1': True, 'SW2': True}),
 'p100_pfl_afl': dict(pos=pots(1.0), pfl_on=True, sw={'SW1': True, 'SW2': True}),
 'p075_extsel_Lplug': dict(pos=pots(0.75), sw={'SW3': True}, ext={'L': (50, 1e-9)}),
 'p075_extsel_open': dict(pos=pots(0.75), sw={'SW3': True}),
 'p075_ext600_both': dict(pos=pots(0.75), sw={'SW3': True}, ext={'L': (600, 1e-9), 'R': (600, 1e-9)}),
 'p075_ins_unit': dict(pos=pots(0.75), ins={'L': INS_UNIT, 'R': INS_UNIT}),
 'p075_ins_dead': dict(pos=pots(0.75), ins={'L': (None, 300e-12, 10e3, 300e-12), 'R': (None, 300e-12, 10e3, 300e-12)}),
 'p075_ins_2k5': dict(pos=pots(0.75), ins={'L': (2.5e3, 100e-12, 10e3, 100e-12), 'R': (2.5e3, 100e-12, 10e3, 100e-12)}),
 'p075_relays_off': dict(pos=pots(0.75), relays=False),
 'bus_min': dict(pos=pots(0.75), bus={'MIXL': (1, 4.7e3, 220e-12), 'MIXR': (1, 4.7e3, 220e-12), 'AUX5': (24, 22e3, 220e-12),
                                      'AUX6': (24, 22e3, 220e-12), 'PFL': (0, 22e3, 220e-12)}),
 'bus_max': dict(pos=pots(0.75), bus={'MIXL': (32, 4.7e3, 2.2e-9), 'MIXR': (32, 4.7e3, 2.2e-9), 'AUX5': (28, 22e3, 2.2e-9),
                                      'AUX6': (28, 22e3, 2.2e-9), 'PFL': (4, 22e3, 2.2e-9)}),
 'bus_pfl1_small': dict(pos=pots(0.75), bus={'PFL': (1, 22e3, 220e-12)}),
 'gc_none': dict(pos=pots(0.75), gc='none'),
 'p075_out22': dict(pos=pots(0.75), loads=outload(22e-12)),
 'p075_out47': dict(pos=pots(0.75), loads=outload(47e-12)),
 'p100_out47': dict(pos=pots(1.0), loads=outload(47e-12)),
 'p050_out47': dict(pos=pots(0.5), loads=outload(47e-12)),
 'p075_placed': dict(pos=pots(0.75), loads=PLACED),
 'p075_pfl_out47': dict(pos=pots(0.75), pfl_on=True, sw={'SW1': True, 'SW2': True}, loads=outload(47e-12)),
}
CONFIGS.update({
 'p100_placed': dict(pos=pots(1.0), loads=PLACED),
 'p050_placed': dict(pos=pots(0.5), loads=PLACED),
 'p100_pfl_placed': dict(pos=pots(1.0), pfl_on=True, sw={'SW1': True, 'SW2': True}, loads=PLACED),
 'p075_pfl_placed': dict(pos=pots(0.75), pfl_on=True, sw={'SW1': True, 'SW2': True}, loads=PLACED),
 'p100_pfl_out47': dict(pos=pots(1.0), pfl_on=True, sw={'SW1': True, 'SW2': True}, loads=outload(47e-12)),
 'p090_out47': dict(pos=pots(0.9), loads=outload(47e-12)),
 'p075_ext600_out47': dict(pos=pots(0.75), sw={'SW3': True}, ext={'L': (600, 1e-9), 'R': (600, 1e-9)}, loads=outload(47e-12)),
 'p100_ext600_out47': dict(pos=pots(1.0), sw={'SW3': True}, ext={'L': (600, 1e-9), 'R': (600, 1e-9)}, loads=outload(47e-12)),
})
