"""Generate the master-section schematic from master_section_spec.md v0.5.
Same builder as the strip (schgen.py). The parts, reference allocation and circuit blocks are in
master_lib.py (shared with gen_jig.py); this file is the master's netlist."""
import sys
from master_lib import *

OUT = sys.argv[1] if len(sys.argv) > 1 else 'master.kicad_sch'

# ================================================================ PART 5: power entry, grounding  [24-26]
b = block('POWER ENTRY  (7-pin XLR NC7MD-LX on the rear panel, two 5 A contacts per rail, 18 AWG to this terminal; +-17 V PSU)')
# terminal = XLR pin: 1 earth (pin 1 mates first), 2-3 +V, 4-5 0 V, 6-7 -V; up to ~3.8 A per rail (spec 27)
P(b, ref('J'), 'PWRIN', 'PSU in (NC7MD-LX)', {1: 'CHASSIS', 2: '+VBUS', 3: '+VBUS', 4: 'GNDA', 5: 'GNDA',
                                              6: '-VBUS', 7: '-VBUS'})
P(b, ref('D'), 'DS', 'SS54', {1: '+VBUS', 2: 'GNDA'}); P(b, ref('D'), 'DS', 'SS54', {1: 'GNDA', 2: '-VBUS'})
P(b, ref('CN'), 'TAB', 'Ground bar M4 (star point)', {1: 'GNDA'}, fp='MountingHole:MountingHole_4.3mm_M4_Pad', mpn='')
for n in ('GNDD', 'GNDM', 'PHONESGND', 'CHASSIS'):
    P(b, ref('NT'), 'NT', f'Star GNDA-{n}', {1: 'GNDA', 2: n})
b = block('DISTRIBUTION  (PTC per wing per rail, 1.6 A hold, 72 V; local branches VA audio, VP phones, VM meters, VL logic)')
for w in 'LR':
    P(b, ref('F'), 'PTC', 'MF-RX160/72', {1: '+VBUS', 2: f'+VBUS_{w}'}); P(b, ref('F'), 'PTC', 'MF-RX160/72', {1: '-VBUS', 2: f'-VBUS_{w}'})
for rail, rv, cv, g in (('VA', '1R', '470u 25V', 'GNDA'), ('VP', '2R2', '1000u 25V', 'GNDA'),
                        ('VM', '10R', '47u 25V', 'GNDM'), ('VL', '10R', '47u 25V', 'GNDD')):
    R(b, rv, '+VBUS', '+' + rail); CP(b, cv, '+' + rail, g)
    R(b, rv, '-VBUS', '-' + rail); CP(b, cv, g, '-' + rail)
R(b, '4K7', '+VL', 'PWR_LA'); P(b, ref('D'), 'LED', 'Power green', {2: 'PWR_LA', 1: 'GNDD'})
for i, n in enumerate(['+VBUS', '-VBUS', '+VA', '-VA', '+VP', '-VP', '+VM', '-VM', '+VL', '-VL', 'GNDA', 'GNDD', 'GNDM', 'PHONESGND']):
    P(b, f'#FLG{i + 1:02d}', 'FLAG', 'PWR_FLAG', {1: n})

b = block('MOTHERLOOM  (master in the centre: CN1 = left wing, CN2 = right wing; Delta pinout)')
for w in 'LR':
    hdr = {1: 'SPARE1', 3: 'SPARE3', 5: 'SPARE5', 7: 'SPARE7', 19: 'SPARE19', 9: 'SUB4', 11: 'SUB3', 13: 'SUB2', 15: 'SUB1',
           17: 'MIXR', 18: 'MIXL', 20: 'AUX6', 21: 'AUX5', 22: 'AUX4', 23: 'AUX3', 24: 'AUX1', 25: 'AUX2', 26: 'GCANCEL',
           27: 'PFL', 28: 'PFLN', 29: 'PFLDET', 30: f'-VBUS_{w}', 31: f'-VBUS_{w}', 32: f'+VBUS_{w}', 33: f'+VBUS_{w}', 34: 'P48V_NC'}
    hdr.update({k: 'GNDA' for k in range(2, 17, 2)})
    P(b, ref('CN'), 'HDR', f'Bus {w} wing 2x17', hdr)

b = block('GROUND CANCEL BUFFER  (feeds every re-inverter; summing amps use the raw GCANCEL line)')
amp(b, 'GCANCEL', 'GCANCEL_BUF', 'GCANCEL_BUF')

# ================================================================ PART 1: stereo mix  [1-8]
for side, bus in (('L', 'MIXL'), ('R', 'MIXR')):
    b = block(f'MIX {side}: summing amp (GCANCEL-referenced), re-inverter, master insert')
    summer(b, bus, f'SUM_{side}', '4K7', '100p')
    reinv(b, f'SUM_{side}', f'MIX_{side}')
    insert(b, f'MIX_{side}', f'PRE_{side}', f'MIX_{side}')
b = block('MASTER FADER (dual 100 mm A10K, pin 1 = GNDA) + post-amps +10 dB')
P(b, ref('RV'), 'POT2', 'Master fader 10K log 100mm dual', {1: 'GNDA', 3: 'PRE_L', 2: 'MW_L', 4: 'GNDA', 6: 'PRE_R', 5: 'MW_R'},
  fp=FADER2_FP, mpn='Bourns PTB0144-2010BPA103')
post_amp(b, 'MW_L', 'POST_L', 'MST_L'); post_amp(b, 'MW_R', 'POST_R', 'MST_R')
b = block('MONO: inverting sum of POST L+R, re-inverter')
R(b, '10K', 'POST_L', 'MONO_N'); R(b, '10K', 'POST_R', 'MONO_N')
amp(b, 'GNDA', 'MONO_N', 'MONO_INV'); R(b, '10K', 'MONO_INV', 'MONO_N'); C(b, '100p C0G', 'MONO_INV', 'MONO_N')
R(b, '10K', 'MONO_INV', 'MONO_N2'); R(b, '10K', 'MONO_N2', 'MONO')
amp(b, 'GNDA', 'MONO_N2', 'MONO')
b = block('MAIN OUTPUTS: DRV134 -> 10u NP in the Sense loop -> mute relay (NO) -> XLR male, pin 2 hot')
for src, nm in (('POST_L', 'MAIN_L'), ('POST_R', 'MAIN_R'), ('MONO', 'MAIN_M')):
    drv134(b, src, nm + '_P', nm + '_N')
    relay(b, nm + '_P', nm + '_XP', nm + '_N', nm + '_XN')
    P(b, ref('J'), 'XLR3', nm.replace('_', ' ') + ' out', {1: 'CHASSIS', 2: nm + '_XP', 3: nm + '_XN'})

b = block('POWER-ON MUTE: rails > ~14 V for ~2 s closes all five relays; either rail low opens them at once')
P(b, ref('D'), 'DZ', 'BZX84C6V2', {2: 'GNDD', 1: 'VREF6'}, mpn='BZX84C6V2'); R(b, '4K7', '+VBUS', 'VREF6')
R(b, '56K', '+VBUS', 'SENSE_P'); R(b, '47K', 'SENSE_P', 'GNDD')       # +V < 13.6 V -> fault
R(b, '22K', 'VREF6', 'SENSE_N'); R(b, '51K', 'SENSE_N', '-VBUS')     # -V above -14.4 V -> fault
cmp(b, 'SENSE_P', 'VREF6', 'RAIL_OK'); cmp(b, 'GNDD', 'SENSE_N', 'RAIL_OK')
R(b, '10K', '+VL', 'RAIL_OK')
# timer and Schmitt: values from sim/mute.cir (closes 2.8 s after both rails pass threshold; opens ~2 ms after
# either rail drops; any fault longer than ~10 ms re-arms the full delay)
R(b, '2M2', 'RAIL_OK', 'MUTE_T')
P(b, ref('C'), 'C', '2.2u film 63V', {1: 'MUTE_T', 2: 'GNDD'}, fp='Capacitor_THT:C_Rect_L7.2mm_W8.5mm_P5.00mm_FKP2_FKP2_MKS2_MKP2', mpn='WIMA MKS2 2.2uF 63V')
D(b, 'MUTE_T', 'MUTE_TX'); R(b, '2K2', 'MUTE_TX', 'RAIL_OK'); D(b, 'GNDD', 'MUTE_T')   # reset path, clamp at -0.7 V
cmp(b, 'MUTE_T', 'VREF6', 'MUTE_GO'); R(b, '22M', 'MUTE_GO', 'MUTE_T')
R(b, '4K7', '+VL', 'MUTE_GO'); R(b, '4K7', 'MUTE_GO', 'RLY_B')
D(b, 'RLY_B', 'RLY_BX'); R(b, '2K2', 'RLY_BX', 'RAIL_OK'); D(b, 'GNDD', 'RLY_B')      # fast release, base clamp
P(b, ref('Q'), 'NPN', 'MMBT3904', {1: 'RLY_B', 2: 'GNDD', 3: 'RLY_DRV'})

# ================================================================ PART 2: subgroups, aux masters  [12-13]
SUBPIN = {1: 'SUB1', 2: 'SUB2', 3: 'SUB3', 4: 'SUB4'}
for n in range(1, 5):
    s = f'S{n}'
    b = block(f'SUBGROUP {n}: sum, re-invert, insert, fader + post-amp, DRV134 out, pan to MIX, AFL')
    summer(b, SUBPIN[n], s + '_SUM', '4K7', '100p')
    reinv(b, s + '_SUM', s + '_MIX')
    insert(b, s + '_MIX', s + '_PRE', s)
    P(b, ref('RV'), 'POT', f'Sub {n} fader 10K log 100mm', {1: 'GNDA', 3: s + '_PRE', 2: s + '_W'}, fp=FADER_FP, mpn='Bourns PTB0143-2010BPA103')
    post_amp(b, s + '_W', s + '_POST', s)
    drv134(b, s + '_POST', s + '_OP', s + '_ON')
    P(b, ref('J'), 'JACK', f'Sub {n} out TRS', {'T': s + '_OP', 'R': s + '_ON', 'S': 'GNDA'})
    P(b, ref('RV'), 'POT2', f'Sub {n} pan 10K dual', {1: s + '_POST', 3: 'GNDA', 2: s + '_PWL', 4: 'GNDA', 6: s + '_POST', 5: s + '_PWR'})
    amp(b, s + '_PWL', s + '_PBL', s + '_PBL'); amp(b, s + '_PWR', s + '_PBR', s + '_PBR')
    C(b, '220u NP 25V', s + '_PBL', s + '_PANL'); R(b, '47K', s + '_PANL', 'GNDA')
    C(b, '220u NP 25V', s + '_PBR', s + '_PANR'); R(b, '47K', s + '_PANR', 'GNDA')
    routing(b, s + '_PANL', s + '_PANR', 'MIXL', 'MIXR', f'Sub {n} to MIX')
    R(b, '22K', s + '_POST', s + '_AFLJ'); afl(b, s + '_AFLJ', f'Sub {n} AFL')

for n in range(1, 7):
    a = f'A{n}'
    b = block(f'AUX MASTER {n}: OPA1656 sum (22K || 100p) + re-invert, level, buffer, DRV134 out, AFL')
    summer(b, f'AUX{n}', a + '_SUM', '22K', '100p', 'OPA1656')
    reinv(b, a + '_SUM', a + '_MIX', 'OPA1656')
    C(b, '47u NP 25V', a + '_MIX', a + '_PT')
    P(b, ref('RV'), 'POT', f'Aux {n} master 10K log', {1: 'GNDA', 3: a + '_PT', 2: a + '_W'})
    level_buffer(b, a + '_W', a + '_OUT', a)
    drv134(b, a + '_OUT', a + '_OP', a + '_ON')
    P(b, ref('J'), 'JACK', f'Aux {n} out TRS', {'T': a + '_OP', 'R': a + '_ON', 'S': 'GNDA'})
    R(b, '22K', a + '_OUT', a + '_AFLJ'); afl(b, a + '_AFLJ', f'Aux {n} AFL')

# ================================================================ PART 3: stereo returns  [16]
for n in range(1, 5):
    r = f'RT{n}'
    b = block(f'STEREO RETURN {n}: receivers (R normalled to L), level, buffers, MIX / 1-2 / 3-4, PFL')
    stereo_in(b, f'Return {n}', r + '_L', r + '_R')
    for sd in 'LR':
        C(b, '47u NP 25V', f'{r}_{sd}', f'{r}_PRE{sd}'); R(b, '47K', f'{r}_PRE{sd}', 'GNDA')
    P(b, ref('RV'), 'POT2', f'Return {n} level 10K log dual', {1: 'GNDA', 3: r + '_PREL', 2: r + '_WL', 4: 'GNDA', 6: r + '_PRER', 5: r + '_WR'}, mpn=POT2A_MPN)
    for sd in 'LR':
        level_buffer(b, f'{r}_W{sd}', f'{r}_B{sd}', f'{r}{sd}')
        C(b, '220u NP 25V', f'{r}_B{sd}', f'{r}_RTN{sd}'); R(b, '47K', f'{r}_RTN{sd}', 'GNDA')
    for busl, busr, nm in (('MIXL', 'MIXR', 'MIX'), ('SUB1', 'SUB2', '1-2'), ('SUB3', 'SUB4', '3-4')):
        routing(b, r + '_RTNL', r + '_RTNR', busl, busr, f'Return {n} {nm}')
    R(b, '43K', r + '_PREL', r + '_PFLJ'); R(b, '43K', r + '_PRER', r + '_PFLJ')
    afl(b, r + '_PFLJ', f'Return {n} PFL')

# ================================================================ PART 4: monitoring  [17-22]
b = block('EXT INPUT (2-track / DAW) and MIX / EXT monitor select  (SW latched = EXT)')
stereo_in(b, 'EXT', 'EXT_RL', 'EXT_RR')
for sd in 'LR':
    C(b, '47u NP 25V', f'EXT_R{sd}', f'EXT_{sd}'); R(b, '47K', f'EXT_{sd}', 'GNDA')
sw = ref('SW')
P(b, sw, 'SW', 'EXT select', {2: 'MON_L', 1: 'EXT_L', 3: 'POST_L'}, unit=1)
P(b, sw, 'SW', 'EXT select', {5: 'MON_R', 4: 'EXT_R', 6: 'POST_R'}, unit=2)

b = block('PFL / AFL: OPA1656 sum (22K || 100p) + re-invert, SOLO LEVEL, follower')
summer(b, 'PFL', 'PFL_SUM', '22K', '100p', 'OPA1656')
reinv(b, 'PFL_SUM', 'PFL_MIX', 'OPA1656')
C(b, '47u NP 25V', 'PFL_MIX', 'PFL_PT')
P(b, ref('RV'), 'POT', 'Solo level 10K log', {1: 'GNDA', 3: 'PFL_PT', 2: 'PFL_W'})
C(b, '2.2u', 'PFL_W', 'PFL_FIN'); R(b, '100K', 'PFL_FIN', 'GNDA')
amp(b, 'PFL_FIN', 'PFL_SIG', 'PFL_SIG')

b = block('PFL DETECT (1.5 V per press vs 0.74 V), complementary ramps, rude-solo flasher')
R(b, '10K', 'PFLDET', 'GNDD'); R(b, '220K', '+VL', 'PFL_REF'); R(b, '10K', 'PFL_REF', 'GNDD')
cmp(b, 'PFLDET', 'PFL_REF', 'PFL_ON_RAW'); cmp(b, 'PFL_REF', 'PFLDET', 'MON_ON_RAW')
R(b, '10K', '+VL', 'PFL_ON_RAW'); R(b, '10K', '+VL', 'MON_ON_RAW')
R(b, '100K', 'PFL_ON_RAW', 'PFL_ON'); C(b, '100n', 'PFL_ON', 'GNDD')
R(b, '100K', 'MON_ON_RAW', 'MON_ON'); C(b, '100n', 'MON_ON', 'GNDD')
R(b, '100K', '+VL', 'FL_P'); R(b, '100K', 'FL_P', 'GNDD'); R(b, '100K', 'FL_OUT', 'FL_P')
D(b, 'MON_ON_RAW', 'FL_P')                                   # PFL inactive: holds the flasher off
R(b, '1M', 'FL_OUT', 'FL_N'); C(b, '330n', 'FL_N', 'GNDD')
cmp(b, 'FL_P', 'FL_N', 'FL_OUT')
R(b, '10K', '+VL', 'FL_OUT'); R(b, '3K3', '+VL', 'FL_LA')
P(b, ref('D'), 'LED', 'PFL ACTIVE red 5mm', {2: 'FL_LA', 1: 'FL_OUT'}, fp='LED_THT:LED_D5.0mm')

b = block('PFL SWITCHER: series J112 (Delta ED2780 sh.1) -> CRS L/R followers')
for sd in 'LR':
    jfet_switch(b, f'MON_{sd}', f'CRS_{sd}', 'MON_ON', f'SWM{sd}')
    jfet_switch(b, 'PFL_SIG', f'CRS_{sd}', 'PFL_ON', f'SWP{sd}')
    R(b, '100K', f'CRS_{sd}', 'GNDA')
    amp(b, f'CRS_{sd}', f'CRSB_{sd}', f'CRSB_{sd}')

b = block('CONTROL ROOM: C/ROOM dual A10K, followers, DRV134, mute relays, TRS outs')
P(b, ref('RV'), 'POT2', 'C/Room level 10K log dual', {1: 'GNDA', 3: 'CRSB_L', 2: 'CRW_L', 4: 'GNDA', 6: 'CRSB_R', 5: 'CRW_R'}, mpn=POT2A_MPN)
for sd in 'LR':
    C(b, '2.2u', f'CRW_{sd}', f'CR_FIN{sd}'); R(b, '100K', f'CR_FIN{sd}', 'GNDA')
    amp(b, f'CR_FIN{sd}', f'CRO_{sd}', f'CRO_{sd}')
    drv134(b, f'CRO_{sd}', f'CR{sd}_P', f'CR{sd}_N')
    relay(b, f'CR{sd}_P', f'CR{sd}_XP', f'CR{sd}_N', f'CR{sd}_XN')
    P(b, ref('J'), 'JACK', f'C/Room {sd} out TRS', {'T': f'CR{sd}_XP', 'R': f'CR{sd}_XN', 'S': 'GNDA'})

b = block('HEADPHONES: PHONES dual A10K, OPA1612 + LME49600 composite (+9.9 dB), 2R2 out, PHONESGND')
P(b, ref('RV'), 'POT2', 'Phones level 10K log dual', {1: 'GNDA', 3: 'CRSB_L', 2: 'PHW_L', 4: 'GNDA', 6: 'CRSB_R', 5: 'PHW_R'}, mpn=POT2A_MPN)
for sd in 'LR':
    pin, pn, drv, buf, out = f'PH_IN{sd}', f'PH_N{sd}', f'PH_DRV{sd}', f'PH_BUF{sd}', f'PHO_{sd}'
    C(b, '2.2u', f'PHW_{sd}', pin); R(b, '100K', pin, 'GNDA')
    amp(b, pin, pn, drv, rail='VP')
    P(b, ref('U'), 'LME49600', 'LME49600', {2: drv, 4: buf, 5: '+VP', 3: '-VP', 1: 'NC'})
    C(b, '100n', '+VP', 'GNDA'); C(b, '100n', 'GNDA', '-VP'); C(b, '10u NP 25V', '+VP', 'GNDA'); C(b, '10u NP 25V', 'GNDA', '-VP')
    R(b, '2R2', buf, out); R(b, '4K7', out, pn); C(b, '100p C0G', out, pn); R(b, '2K2', pn, 'GNDA')
P(b, ref('J'), 'JACK', 'Phones TRS', {'T': 'PHO_L', 'R': 'PHO_R', 'S': 'PHONESGND'})

b = block('REMOTE METER HEADER (for a meter bridge)')
P(b, ref('CN'), 'HDR5', 'Remote meter', {1: 'MTR_L', 2: 'MTR_R', 3: '+VM', 4: 'GNDM', 5: '-VM'})

LADDER = [1500, 1100, 910, 680, 620, 470, 330, 300, 220, 180, 150, 110, 91, 68, 62, 47, 33, 27, 20]   # Delta R310-R328
COLOUR = ['green'] * 11 + ['amber'] * 5 + ['red'] * 4                                                  # LED 1 (-20 dB) .. 20 (+18 dB)
def fmt_r(v): return f'{v}R' if v < 1000 else (f'{v // 1000}K{v % 1000 // 100}' if v % 1000 else f'{v // 1000}K')
for sd in 'LR':
    m = f'M{sd}'
    b = block(f'METER {sd}: full-wave rectifier, precision peak / average, follower (TL072), 2 dB ladder, 2 x 10-LED strings')
    R(b, '100R', f'CRSB_{sd}', f'MTR_{sd}')
    R(b, '10K', f'MTR_{sd}', m + '_N1'); R(b, '10K', m + '_N1', m + '_HW')
    amp(b, 'GNDM', m + '_N1', m + '_U1O', 'TL072', 'VM')
    D(b, m + '_HW', m + '_U1O'); D(b, m + '_U1O', m + '_N1')
    R(b, '20K', f'MTR_{sd}', m + '_N2'); R(b, '10K', m + '_HW', m + '_N2')
    R(b, '10K', m + '_X2', m + '_RG')
    P(b, ref('RV'), 'TRIM', 'Cal 10K', {1: m + '_RG', 2: m + '_N2', 3: m + '_N2'}, mpn='Bourns 3296W-1-103')
    amp(b, 'GNDM', m + '_N2', m + '_X2', 'TL072', 'VM')
    R(b, '33K', m + '_X2', m + '_AV'); C(b, '2.2u', m + '_AV', 'GNDM')
    amp(b, m + '_X2', m + '_N4', m + '_U3O', 'TL072', 'VM')
    D(b, m + '_U3O', m + '_PK1'); R(b, '1K', m + '_PK1', m + '_PK'); C(b, '1u', m + '_PK', 'GNDM')
    R(b, '330K', m + '_PK', m + '_PKR'); R(b, '220K', m + '_PKR', 'GNDM')
    R(b, '10K', m + '_DET', m + '_N4'); D(b, m + '_N4', m + '_U3O')
    P(b, ref('JP'), 'SJ3', 'PEAK(1-2) / AVG', {1: m + '_PK', 3: m + '_AV', 2: m + '_JSEL'})
    amp(b, m + '_JSEL', m + '_DET', m + '_DET', 'TL072', 'VM')
    # threshold ladder: +VM - 16K - T20 ... T1 - 91R - GNDM
    R(b, '16K', '+VM', f'{m}_T20')
    for k, rv in zip(range(20, 1, -1), LADDER): R(b, fmt_r(rv), f'{m}_T{k}', f'{m}_T{k - 1}')
    R(b, '91R', f'{m}_T1', 'GNDM')
    # two series LED strings, each from a PNP current source; comparator k shorts the string at the node before LED k
    for s0, ks in (('A', range(1, 11)), ('B', range(11, 21))):
        src = f'{m}{s0}_0'; base, emit = f'{m}{s0}_QB', f'{m}{s0}_QE'
        R(b, '75R', '+VM', emit); D(b, '+VM', f'{m}{s0}_D1'); D(b, f'{m}{s0}_D1', base); R(b, '27K', base, '-VM')
        P(b, ref('Q'), 'PNP', 'MMBT3906', {1: base, 2: emit, 3: src})
        for i, k in enumerate(ks):
            node = f'{m}{s0}_{i}'; nxt = f'{m}{s0}_{i + 1}' if i < 9 else '-VM'
            P(b, ref('D'), 'LED', f'{COLOUR[k - 1]} {-20 + 2 * (k - 1):+d} dB', {2: node, 1: nxt})
            cmp(b, f'{m}_DET', f'{m}_T{k}', node, 'LM2901', 'VM')

build(OUT, 'master', 'Master section - goa console',
      {1: 'Generated by tools/gen_master.py from master_section_spec.md v0.5',
       2: 'Nets joined by labels; refs auto-assigned'}, paper='auto', perrow=30, revision='0.5')
