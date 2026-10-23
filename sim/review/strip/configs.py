from stripdeck import node
ON = {'SW4': True, 'SW12': True, 'SW14': True, 'SW5': True}
EQB = {'RV10': 1, 'RV11': 1, 'RV13': 1, 'RV15': 1}
EQC = {'RV10': 0, 'RV11': 0, 'RV13': 0, 'RV15': 0}
LOADS = ((node('J2', 'T'), 2e-9), (node('J5', 'T'), 2e-9))
CONFIGS = {
 'c01_nominal':            ({'RV1': 1.0}, ON, {}),
 'c02_gainCCW':            ({'RV1': 1.0, 'RV9': 0.0}, ON, {}),
 'c03_gainCW':             ({'RV1': 1.0, 'RV9': 1.0}, ON, {}),
 'c04_EQboost_fCCW':       ({'RV1': 1.0, **EQB, 'RV12': 0, 'RV14': 0}, ON, {}),
 'c05_EQcut_fCW':          ({'RV1': 1.0, **EQC, 'RV12': 1, 'RV14': 1}, ON, {}),
 'c06_EQboost_fCW':        ({'RV1': 1.0, **EQB, 'RV12': 1, 'RV14': 1}, ON, {}),
 'c07_EQcut_fCCW':         ({'RV1': 1.0, **EQC, 'RV12': 0, 'RV14': 0}, ON, {}),
 'c08_EQgain.25_f.25':     ({'RV1': 1.0, 'RV10': .25, 'RV11': .25, 'RV13': .25, 'RV15': .25, 'RV12': .25, 'RV14': .25}, ON, {}),
 'c09_EQout_HPFin_phase':  ({'RV1': 1.0}, {**ON, 'SW12': False, 'SW11': True, 'SW15': True}, {}),
 'c10_fader0_panL_PANoff_PRE_auxTop': ({'RV1': 0.6, 'RV8': 0.0, **{f'RV{i}': 1.0 for i in range(2, 8)}},
                           {**ON, 'SW14': False, 'SW6': True, 'SW7': True, 'SW8': True, 'SW9': True, 'SW10': True}, {}),
 'c11_faderBot_DIR_auxMid_panR': ({'RV1': 0.0, 'RV8': 1.0, **{f'RV{i}': 0.5 for i in range(2, 8)}},
                           {**ON, 'SW13': True, 'SW6': True}, {}),
 'c12_muted_PFL':          ({'RV1': 1.0}, {**ON, 'SW4': False, 'SW3': True}, {}),
 'c13_inputOpen_cables_DIRtop': ({'RV1': 1.0, 'RV7': 1.0}, {**ON, 'SW13': True, 'SW10': True}, {'src': 'open', 'loads': LOADS}),
 'c14_faderMid_DIR_auxMid_PRE': ({'RV1': 0.5, **{f'RV{i}': 0.5 for i in range(2, 8)}},
                           {**ON, 'SW13': True, 'SW8': True, 'SW9': True, 'SW10': True}, {}),
 'c15_gainCW_EQboost_fMid':({'RV1': 1.0, 'RV9': 1.0, **EQB}, ON, {}),
}
for cl in ('470p', '2n', '10n'):
    v = {'470p': 470e-12, '2n': 2e-9, '10n': 10e-9}[cl]
    CONFIGS[f'k_cable{cl}_DIRtop'] = ({'RV1': 1.0, 'RV7': 1.0}, {**ON, 'SW13': True, 'SW10': True},
                                      {'loads': ((node('J2', 'T'), v), (node('J5', 'T'), v))})
    CONFIGS[f'k_cable{cl}_DIRmid'] = ({'RV1': 1.0, 'RV7': 0.5}, {**ON, 'SW13': True, 'SW10': True},
                                      {'loads': ((node('J2', 'T'), v), (node('J5', 'T'), v))})
