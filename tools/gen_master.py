"""Generate the master module schematic from master_section_spec.md (16 HP, master_panel_study.md M1):
power entry and both wing headers, MIX L/R, master fader, mono, main outputs, power-on mute, aux masters
5-6, monitoring, PFL and meters. Subgroups, aux masters 1-4 and returns are on the group modules (gen_group.py).
Same builder as the strip (schgen.py). The parts, reference allocation and circuit blocks are in
master_lib.py (shared with gen_jig.py); this file is the master's netlist."""
import sys
from master_lib import *

OUT = sys.argv[1] if len(sys.argv) > 1 else 'master.kicad_sch'
collect_jacks()                 # panel jacks and XLRs go on the master jack board (master_jack_board.kicad_sch)

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
# VA: anti-surge 0805 for the PSU-lead hot-plug pulse; VP: 2512, a mono plug in the phones jack can hold an LME49600
# at its current limit, DC, through one of these (master_group_review.md MG11 / MG17)
RAIL_RES = {'VA': dict(mpn='Panasonic ERJ-P06J1R0V'), 'VP': dict(fp=RES_2512, mpn='Vishay CRCW25122R20FKEGHP')}
for rail, rv, cv, g in (('VA', '1R', '470u 25V', 'GNDA'), ('VP', '2R2', '1000u 25V', 'GNDA'),
                        ('VM', '10R', '47u 25V', 'GNDM'), ('VL', '10R', '47u 25V', 'GNDD')):
    R(b, rv, '+VBUS', '+' + rail, **RAIL_RES.get(rail, {})); CP(b, cv, '+' + rail, g)
    R(b, rv, '-VBUS', '-' + rail, **RAIL_RES.get(rail, {})); CP(b, cv, g, '-' + rail)
R(b, '4K7', '+VL', 'PWR_LA'); P(b, ref('D'), 'LED', 'Power green', {2: 'PWR_LA', 1: 'GNDD'}, mpn=LED_MPN['green'])
for i, n in enumerate(['+VBUS', '-VBUS', '+VA', '-VA', '+VP', '-VP', '+VM', '-VM', '+VL', '-VL', 'GNDA', 'GNDD', 'GNDM', 'PHONESGND']):
    P(b, f'#FLG{i + 1:02d}', 'FLAG', 'PWR_FLAG', {1: n})

b = block('MOTHERLOOM  (master in the centre: CN1 = left wing, CN2 = right wing; Delta pinout)')
for w in 'LR':
    hdr = {1: 'SPARE1', 3: 'SPARE3', 5: 'SPARE5', 7: 'SPARE7', 19: 'SPARE19', 9: 'SUB4', 11: 'SUB3', 13: 'SUB2', 15: 'SUB1',
           17: 'MIXR', 18: 'MIXL', 20: 'AUX6', 21: 'AUX5', 22: 'AUX4', 23: 'AUX3', 24: 'AUX1', 25: 'AUX2', 26: 'GCANCEL',
           27: 'PFL', 28: 'PFLN', 29: 'PFLDET', 30: f'-VBUS_{w}', 31: f'-VBUS_{w}', 32: f'+VBUS_{w}', 33: f'+VBUS_{w}', 34: 'P48V_NC'}
    hdr.update({k: 'GNDA' for k in range(2, 17, 2)})
    P(b, ref('CN'), 'HDR', f'Bus {w} wing 2x17', hdr)

b = block('GROUND CANCEL BUFFER  (feeds every re-inverter; summing amps use the raw GCANCEL line; 100K keeper)')
amp(b, 'GCANCEL', 'GCANCEL_BUF', 'GCANCEL_BUF')     # output straight to the net: no series R outside the loop, <= 50 pF
R(b, '100K', 'GCANCEL', 'GNDA')     # keeper: defines the line with no strip or group on a wing; leaks -79 dB at N = 32

# ================================================================ PART 1: stereo mix  [1-8]
for side, bus in (('L', 'MIXL'), ('R', 'MIXR')):
    b = block(f'MIX {side}: summing amp (GCANCEL-referenced), re-inverter, master insert')
    summer(b, bus, f'SUM_{side}', '4K7', '100p')
    reinv(b, f'SUM_{side}', f'MIX_{side}')
    insert(b, f'MIX_{side}', f'PRE_{side}', f'MIX_{side}')
b = block('MASTER FADER (dual 100 mm A10K, pin 1 = GNDA) + post-amps +10 dB')
P(b, ref('RV'), 'POT2', 'Master fader 10K log 100mm dual', {1: 'GNDA', 3: 'PRE_L', 2: 'MW_L', 4: 'GNDA', 6: 'PRE_R', 5: 'MW_R'},
  fp=FADER2_FP, mpn='Bourns PTB0144-2010BPA103')
with new_package():                     # both post-amps in one OPA1612, beside the fader wiper
    post_amp(b, 'MW_L', 'POST_L', 'MST_L'); post_amp(b, 'MW_R', 'POST_R', 'MST_R')
b = block('MONO: inverting sum of POST L+R, re-inverter')
R(b, '10K', 'POST_L', 'MONO_N'); R(b, '10K', 'POST_R', 'MONO_N')
amp(b, 'GNDA', 'MONO_N', 'MONO_INV'); R(b, '10K', 'MONO_INV', 'MONO_N'); C(b, '100p C0G', 'MONO_INV', 'MONO_N')
R(b, '10K', 'MONO_INV', 'MONO_N2'); R(b, '10K', 'MONO_N2', 'MONO'); c = C(b, '22p C0G', 'MONO', 'MONO_N2')
near(c, amp(b, 'GNDA', 'MONO_N2', 'MONO'))              # 22p: stability against the input capacitance, at the pins
spares(b)       # the summer area's odd op-amp half stays a spare: a later block would pull its package to another zone
b = block('MAIN OUTPUTS: DRV134 -> 10u NP in the Sense loop -> mute relay (NO; NC grounds the line) -> XLR male, pin 2 hot')
for src, nm in (('POST_L', 'MAIN_L'), ('POST_R', 'MAIN_R'), ('MONO', 'MAIN_M')):
    u = drv134(b, src, nm + '_P', nm + '_N')
    relay(b, nm + '_P', nm + '_XP', nm + '_N', nm + '_XN', anchor=u)
    jack(b, 'XLR3', nm.replace('_', ' ') + ' out', {1: 'CHASSIS', 2: nm + '_XP', 3: nm + '_XN'})

b = block('POWER-ON MUTE: rails > ~14 V for ~2.7 s closes all six relays; either rail low opens them at once')
dz = ref('D'); P(b, dz, 'DZ', 'BZT52C6V2', {2: 'GNDD', 1: 'VREF6'}, mpn='Diodes BZT52C6V2-7-F'); rz = R(b, '4K7', '+VBUS', 'VREF6')
R(b, '56K', '+VBUS', 'SENSE_P'); R(b, '47K', 'SENSE_P', 'GNDD')       # +V < 13.6 V -> fault
rn = R(b, '22K', 'VREF6', 'SENSE_N'); R(b, '51K', 'SENSE_N', '-VBUS')     # -V above -14.4 V -> fault
uc = cmp(b, 'SENSE_P', 'VREF6', 'RAIL_OK'); cmp(b, 'GNDD', 'SENSE_N', 'RAIL_OK')
for x in (dz, rz, rn): near(x, uc)     # the 6.2 V reference beside both comparators that read it (it ran ~110 mm)
R(b, '10K', '+VL', 'RAIL_OK', mpn='Panasonic ERJ-P06J103V')   # ~33 V across in a one-rail brown-out (MG12)
# timer and Schmitt: values from sim/mute.cir (closes 2.6-2.8 s after both rails pass threshold; contacts open
# <= ~8.5 ms after either rail drops; any fault longer than ~8 ms re-arms the full delay). The reset and fast-release
# resistors are 4K7, not 2K2: at a one-rail loss one LM393 output sinks ~12 mA instead of ~23 mA
R(b, '2M2', 'RAIL_OK', 'MUTE_T')
P(b, ref('C'), 'C', '2.2u film 63V', {1: 'MUTE_T', 2: 'GNDD'}, fp='Capacitor_THT:C_Rect_L7.2mm_W8.5mm_P5.00mm_FKP2_FKP2_MKS2_MKP2', mpn='WIMA MKS2 2.2uF 63V')
D(b, 'MUTE_T', 'MUTE_TX'); R(b, '4K7', 'MUTE_TX', 'RAIL_OK'); D(b, 'GNDD', 'MUTE_T')   # reset path, clamp at -0.7 V
near(cmp(b, 'MUTE_T', 'VREF6', 'MUTE_GO'), uc); R(b, '22M', 'MUTE_GO', 'MUTE_T')
R(b, '4K7', '+VL', 'MUTE_GO', mpn='Panasonic ERJ-P06J472V')   # MUTE_GO sinks to -VL: 230 mW per power-up (MG12)
R(b, '4K7', 'MUTE_GO', 'RLY_B')
D(b, 'RLY_B', 'RLY_BX'); R(b, '4K7', 'RLY_BX', 'RAIL_OK'); D(b, 'GNDD', 'RLY_B')      # fast release, base clamp
P(b, ref('Q'), 'NPN', 'MMBT3904', {1: 'RLY_B', 2: 'GNDD', 3: 'RLY_DRV'})

# ================================================================ PART 2: aux masters 5-6  [13]
# Subgroups 1-4, aux masters 1-4 and stereo returns 1-4 are on the four group modules (tools/gen_group.py,
# master_panel_study.md M1); they sit on the ribbon like strips and sum their own buses.
for n in range(5, 7):
    a = f'A{n}'
    b = block(f'AUX MASTER {n}: OPA1612 sum (22K || 100p) + re-invert, level, buffer, DRV134 out, AFL')
    with new_package():                 # all 24 strips' 22K are always on an aux bus: noise gain 25, so the OPA1612
        summer(b, f'AUX{n}', a + '_SUM', '22K', '100p')
        reinv(b, a + '_SUM', a + '_MIX')
    C(b, '47u NP 25V', a + '_MIX', a + '_PT')
    P(b, ref('RV'), 'POT', f'Aux {n} master 10K log', {1: 'GNDA', 3: a + '_PT', 2: a + '_W'})
    level_buffer(b, a + '_W', a + '_OUT', a)
    drv134(b, a + '_OUT', a + '_OP', a + '_ON')
    jack(b, 'JACK', f'Aux {n} out TRS', {'T': a + '_OP', 'R': a + '_ON', 'S': 'GNDA'})
    R(b, '22K', a + '_OUT', a + '_AFLJ'); afl(b, a + '_AFLJ', f'Aux {n} AFL')

# ================================================================ PART 4: monitoring  [17-22]
b = block('EXT INPUT (2-track / DAW) and MIX / EXT monitor select  (SW latched = EXT)')
# outputs EXT_BL/BR (EXT_RR was the R jack's ring: master_group_review.md MG1); 100R build-out at the pin, because
# with EXT selected the receivers drive the EXT -> SW -> MON -> DG413 run
for sd, u in zip('LR', stereo_in(b, 'EXT', 'EXT_BL', 'EXT_BR')):
    near(R(b, '100R', f'EXT_B{sd}', f'EXT_B{sd}O'), u)
    C(b, '47u NP 25V', f'EXT_B{sd}O', f'EXT_{sd}'); R(b, '47K', f'EXT_{sd}', 'GNDA')
sw = ref('SW')
P(b, sw, 'SW', 'EXT select', {2: 'MON_L', 1: 'EXT_L', 3: 'POST_L'}, unit=1)
P(b, sw, 'SW', 'EXT select', {5: 'MON_R', 4: 'EXT_R', 6: 'POST_R'}, unit=2)

b = block('PFL / AFL: OPA1656 sum (22K || 100p) + re-invert, SOLO LEVEL, follower')
summer(b, 'PFL', 'PFL_SUM', '22K', '100p', 'OPA1656')      # switched bus, 1-4 sources: the CMOS part is quieter
reinv(b, 'PFL_SUM', 'PFL_MIX', 'OPA1656')
C(b, '47u NP 25V', 'PFL_MIX', 'PFL_PT')
P(b, ref('RV'), 'POT', 'Solo level 10K log', {1: 'GNDA', 3: 'PFL_PT', 2: 'PFL_W'})
C(b, '2.2u', 'PFL_W', 'PFL_FIN'); R(b, '100K', 'PFL_FIN', 'GNDA')
# 22p against the wiper's Cdiff lag; 100R build-out at the pin: with a key pressed two DG413 on-switches and both CRS
# inputs hang on PFL_SIG, and the bare follower oscillated (master_group_review.md MG3)
u = amp(b, 'PFL_FIN', 'PFL_SIGO', 'PFL_SIGO')
near(C(b, '22p C0G', 'PFL_FIN', 'GNDA'), u); near(R(b, '100R', 'PFL_SIGO', 'PFL_SIG'), u)

b = block('PFL SWITCHER: DG413 (PFL pressed = SW1/SW4, else SW2/SW3; break-before-make) -> CRS L/R OPA1656 followers')
# +5VL for the DG413 logic, as on the strip: from +VA so VL never exceeds V+
net5 = [R(b, '4K7', '+VA', '+5VL'), ref('D')]
P(b, net5[1], 'ZEN', 'BZX84C5V1', {3: '+5VL', 1: 'GNDD', 2: 'NC'}); net5.append(C(b, '1u', '+5VL', 'GNDD'))
net5.append(ref('D')); P(b, net5[-1], 'SCH', 'BAT54W', {1: '+5VL', 3: '+VA', 2: 'NC'})   # VL <= V+ + 0.3 V at power-down
P(b, '#FLG15', 'FLAG', 'PWR_FLAG', {1: '+5VL'})
for src, s in (('MON_L', 'SWML_S'), ('PFL_SIG', 'SWPL_S'), ('MON_R', 'SWMR_S'), ('PFL_SIG', 'SWPR_S')):
    net5 += [C(b, '47u NP 25V', src, s), R(b, '1M', s, 'GNDA')]
dg = ref('U')                   # CRS on the D side: it sees ~5 pC of charge injection, the S side ~25 pC
P(b, dg, 'DG', 'DG413', {1: 'PFL_ON', 3: 'SWPL_S', 2: 'CRS_L'}, unit=1)      # SW1 (NO): PFL to L
P(b, dg, 'DG', 'DG413', {16: 'PFL_ON', 14: 'SWML_S', 15: 'CRS_L'}, unit=4)   # SW2 (NC): MON L
P(b, dg, 'DG', 'DG413', {8: 'PFL_ON', 6: 'SWPR_S', 7: 'CRS_R'}, unit=2)      # SW4 (NO): PFL to R
P(b, dg, 'DG', 'DG413', {9: 'PFL_ON', 11: 'SWMR_S', 10: 'CRS_R'}, unit=3)    # SW3 (NC): MON R
P(b, dg, 'DG', 'DG413', {13: '+VA', 4: '-VA', 12: '+5VL', 5: 'GNDD'}, unit=5)
for x in [C(b, '100n', '+5VL', 'GNDD'), C(b, '100n', '+VA', 'GNDA'), C(b, '100n', 'GNDA', '-VA')] + net5: near(x, dg)
for sd in 'LR':                 # FET-input followers: an OPA1612's bias current would step CRS at every switch
    R(b, '100K', f'CRS_{sd}', 'GNDA')
    u = amp(b, f'CRS_{sd}', f'CRSB_{sd}O', f'CRSB_{sd}O', 'OPA1656'); near(u, dg)
    near(R(b, '100R', f'CRSB_{sd}O', f'CRSB_{sd}'), u)    # build-out at the pin: CRSB runs ~214 mm (MG6)

b = block('PFL DETECT (0.92 V per press vs 0.50 V; 2 x 1N4148 clamp, 1u debounce) and DG413 logic, beside the switcher')
# The clamp keeps PFLDET from back-feeding the released keys' 100K + 4K7 + LED paths (24 presses read 1.29 V, released
# LEDs <= 20 nA); the 1u filters the PVA2's <= 3 ms bounce (one threshold crossing per press); 10M adds ~20 mV
# hysteresis. Both comparators sink while no key is pressed: A is the DG413 logic (MON), B holds the flasher off
R(b, '10K', 'PFLDET', 'GNDD'); R(b, '330K', '+VL', 'PFL_REF'); R(b, '10K', 'PFL_REF', 'GNDD')
D(b, 'PFLDET', 'PFL_CL'); D(b, 'PFL_CL', 'GNDD'); C(b, '1u', 'PFLDET', 'GNDD')
with new_package('LM393', 'VL'):        # one package for both, beside the DG413 so PFL_ON_RAW stays short
    pc = cmp(b, 'PFLDET', 'PFL_REF', 'PFL_ON_RAW'); cmp(b, 'PFLDET', 'PFL_REF', 'FL_HOLD')
near(R(b, '100K', '+5VL', 'PFL_ON_RAW'), pc); near(R(b, '10M', 'PFL_ON_RAW', 'PFLDET'), pc)   # logic level, hysteresis
r = R(b, '10K', 'PFL_ON_RAW', 'PFL_ON'); near(r, dg); near(pc, r)    # bounds IN clamp current while rails settle

b = block('RUDE SOLO: ~2 Hz flasher, PFL ACTIVE LED; held off through FL_N while no key is pressed')
# while released, the hold comparator pulls FL_N to about -VL through the 1N4148, so FL_OUT stays high (LED off); on a
# press it lets go, the first flash comes ~0.6 s later, then ~0.17 s on every ~0.53 s (sim/flasher.cir)
R(b, '100K', '+VL', 'FL_P'); R(b, '100K', 'FL_P', 'GNDD'); R(b, '100K', 'FL_OUT', 'FL_P')
R(b, '1M', 'FL_OUT', 'FL_N'); C(b, '330n', 'FL_N', 'GNDD'); D(b, 'FL_N', 'FL_HOLD')
cmp(b, 'FL_P', 'FL_N', 'FL_OUT')
R(b, '10K', '+VL', 'FL_OUT')
R(b, '3K3', '+VL', 'FL_LA', mpn='Panasonic ERJ-P06J332V')     # the LED returns to -VL: ~31 V, 297 mW peak (MG13)
P(b, ref('D'), 'LED', 'PFL ACTIVE red 5mm', {2: 'FL_LA', 1: 'FL_OUT'}, fp='LED_THT:LED_D5.0mm', mpn='Kingbright WP7113ID')

b = block('CONTROL ROOM: C/ROOM dual A10K, followers, DRV134, mute relays, TRS outs')
P(b, ref('RV'), 'POT2', 'C/Room level 10K log dual', {1: 'GNDA', 3: 'CRSB_L', 2: 'CRW_L', 4: 'GNDA', 6: 'CRSB_R', 5: 'CRW_R'}, mpn=POT2A_MPN)
with new_package():                     # both C/Room followers in one dual, in the C/Room area
    for sd in 'LR':
        C(b, '2.2u', f'CRW_{sd}', f'CR_FIN{sd}'); R(b, '100K', f'CR_FIN{sd}', 'GNDA')
        u = amp(b, f'CR_FIN{sd}', f'CRO_{sd}', f'CRO_{sd}')
        near(C(b, '22p C0G', f'CR_FIN{sd}', 'GNDA'), u)    # against the wiper's Cdiff lag (MG5)
for sd in 'LR':
    u = drv134(b, f'CRO_{sd}', f'CR{sd}_P', f'CR{sd}_N')
    relay(b, f'CR{sd}_P', f'CR{sd}_XP', f'CR{sd}_N', f'CR{sd}_XN', anchor=u)
    jack(b, 'JACK', f'C/Room {sd} out TRS', {'T': f'CR{sd}_XP', 'R': f'CR{sd}_XN', 'S': 'GNDA'})

b = block('HEADPHONES: PHONES dual A10K, OPA1612 + LME49600 composite (+9.9 dB), 2R2 out, mute relay, PHONESGND')
P(b, ref('RV'), 'POT2', 'Phones level 10K log dual', {1: 'GNDA', 3: 'CRSB_L', 2: 'PHW_L', 4: 'GNDA', 6: 'CRSB_R', 5: 'PHW_R'}, mpn=POT2A_MPN)
for sd in 'LR':
    pin, pn, drv, buf, out = f'PH_IN{sd}', f'PH_N{sd}', f'PH_DRV{sd}', f'PH_BUF{sd}', f'PHO_{sd}'
    C(b, '2.2u', f'PHW_{sd}', pin); R(b, '100K', pin, 'GNDA')
    ua = amp(b, pin, pn, drv, rail='VP')
    near(C(b, '22p C0G', pin, 'GNDA'), ua)
    u = ref('U'); P(b, u, 'LME49600', 'LME49600', {2: drv, 4: buf, 5: '+VP', 3: '-VP', 1: 'NC'}); near(u, ua)
    # 2R2 in 2512: a mono plug grounds PHO_R and holds the LME49600 at its current limit, programme or not (MG11)
    for x in (C(b, '100n', '+VP', 'GNDA'), C(b, '100n', 'GNDA', '-VP'), C(b, '10u NP 25V', '+VP', 'GNDA'),
              C(b, '10u NP 25V', 'GNDA', '-VP'), R(b, '2R2', buf, out, fp=RES_2512, mpn='Vishay CRCW25122R20FKEGHP')):
        near(x, u)
    # the 100p from the op-amp's output, not from PHO: the LME49600 stays out of the HF loop (hand-over at 339 kHz);
    # from PHO the composite was unstable (master_group_review.md MG2)
    R(b, '4K7', out, pn); near(C(b, '100p C0G', drv, pn), ua); R(b, '2K2', pn, 'GNDA')
# the composite is DC-coupled: a one-rail fault would hold ~1 V DC on the phones, so they get a mute relay too;
# the contacts sit after the feedback tap (<= 0.1 ohm outside the loop)
relay(b, 'PHO_L', 'PHJ_L', 'PHO_R', 'PHJ_R', gnd='PHONESGND')
jack(b, 'JACK', 'Phones TRS', {'T': 'PHJ_L', 'R': 'PHJ_R', 'S': 'PHONESGND'})

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
    rv = ref('RV'); P(b, rv, 'TRIM', 'Cal 10K', {1: m + '_RG', 2: m + '_N2', 3: m + '_N2'}, mpn='Bourns 3296W-1-103LF')
    u2 = amp(b, 'GNDM', m + '_N2', m + '_X2', 'TL072', 'VM')
    near(rv, u2); near(C(b, '22p C0G', m + '_X2', m + '_N2'), u2)     # short summing junction (MG9)
    R(b, '33K', m + '_X2', m + '_AV'); C(b, '2.2u', m + '_AV', 'GNDM')
    u3 = amp(b, m + '_X2', m + '_N4', m + '_U3O', 'TL072', 'VM')
    # peak: the follower reads the diode cathode (PK1), so its loop holds one integrator, not the op-amp plus
    # 1K / 1u (0-1.5 deg, +5 dB on 10 kHz at -20 dBu); 220R: 0.22 ms first-order attack (master_group_review.md MG8)
    D(b, m + '_U3O', m + '_PK1'); R(b, '220R', m + '_PK1', m + '_PK'); C(b, '1u', m + '_PK', 'GNDM')
    near(C(b, '22p C0G', m + '_U3O', m + '_N4'), u3)
    R(b, '330K', m + '_PK', m + '_PKR'); R(b, '220K', m + '_PKR', 'GNDM')
    # the 10K back to U3's - input from the follower's pin side: through the 470R the clamp current would read
    # 0.4 dB low and ripple 0.5 dB (MG9)
    R(b, '10K', m + '_DETO', m + '_N4'); D(b, m + '_N4', m + '_U3O')
    P(b, ref('JP'), 'SJ3', 'PEAK(1-2) / AVG', {1: m + '_PK1', 3: m + '_AV', 2: m + '_JSEL'})
    u4 = amp(b, m + '_JSEL', m + '_DETO', m + '_DETO', 'TL072', 'VM')
    near(R(b, '470R', m + '_DETO', m + '_DET'), u4)       # build-out: DET drives 20 comparator inputs + ~165 mm
    # threshold ladder: +VM - 16K - T20 ... T1 - 91R - GNDM
    R(b, '16K', '+VM', f'{m}_T20')
    for k, rv in zip(range(20, 1, -1), LADDER): R(b, fmt_r(rv), f'{m}_T{k}', f'{m}_T{k - 1}')
    R(b, '91R', f'{m}_T1', 'GNDM')
    # two series LED strings, each from a PNP current source; comparator k pulls the anode of LED k to -VM (its GND
    # pin), bypassing the rest of the string, so the source current is constant. Dark, a source holds ~32 V: SOT-223
    # with >= 1 cm2 collector copper, 120R for ~4.9 mA (4.2-5.7 mA over junction tolerances, under the 6 mA IOL)
    for s0, ks in (('A', range(1, 11)), ('B', range(11, 21))):
        src = f'{m}{s0}_0'; base, emit = f'{m}{s0}_QB', f'{m}{s0}_QE'
        R(b, '120R', '+VM', emit); D(b, '+VM', f'{m}{s0}_D1'); D(b, f'{m}{s0}_D1', base); R(b, '27K', base, '-VM')
        q = ref('Q'); P(b, q, 'PNP', 'BCP53-16', {1: base, 2: src, 3: emit, 4: src})
        for i, k in enumerate(ks):
            node = f'{m}{s0}_{i}'; nxt = f'{m}{s0}_{i + 1}' if i < 9 else '-VM'
            led = ref('D'); P(b, led, 'LED', f'{COLOUR[k - 1]} {-20 + 2 * (k - 1):+d} dB', {2: node, 1: nxt}, mpn=LED_MPN[COLOUR[k - 1]])
            if i == 0: near(q, led)     # current source at the top of its string (the collector node is the string's)
            u = cmp(b, f'{m}_DET', f'{m}_T{k}', node, 'LM2901', 'VM')
            if u not in decoupling: near(u, led)        # each LM2901 beside the first LED it drives
spares(b)

import os
JACKS = collected(); NL, LINK = link_pins(JACKS)
b = block(f'JACK BOARD LINK  2x{NL} IDC ribbon to the master jack board (9 jacks, 3 XLRs)')
link_header(b, NL, LINK, f'Jack board link 2x{NL}')
parts_sidecar(OUT)
build(OUT, 'master', 'Master section - goa console',
      {1: 'Generated by tools/gen_master.py from master_section_spec.md v0.8',
       2: 'Nets joined by labels; refs auto-assigned'}, paper='auto', perrow=30, revision='0.8')

jack_board(os.path.join(os.path.dirname(os.path.abspath(OUT)), 'master_jack_board.kicad_sch'), 'master_jack_board',
           'Master module jack board - goa console (main XLRs, inserts, EXT, C/Room, phones, aux 5-6)', JACKS, NL, LINK)
