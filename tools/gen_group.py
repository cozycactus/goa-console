"""Generate the group module schematic (master_panel_study.md, option M1): sub n + stereo return n + aux n
master on one 8 HP board that sits on the ribbon like a strip. Four identical boards; on each, close one SUB
and one AUX solder jumper to pick which buses it sums (group 1: SUB 1 + AUX 1, ... group 4: SUB 4 + AUX 4).
The circuits are the master's own (master_lib.py, master_section_spec.md sections 12, 13, 16).
usage: .venv/bin/python tools/gen_group.py group.kicad_sch   (also writes group_jack_board.kicad_sch)"""
import json, os, sys
from master_lib import *

OUT = sys.argv[1] if len(sys.argv) > 1 else 'group.kicad_sch'
ROOT = os.path.dirname(os.path.abspath(OUT))
SYM.update({'SJO': ('Jumper', 'SolderJumper_2_Open')})
FP.update({'SJO': 'Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm'})

reset(); collect_jacks()                     # panel jacks go on the group's jack board
b = block('POWER AND GROUNDS  (as a strip: 10R + 220u per audio rail, 10R + 47u logic rails, spade, 10R ground cancel)')
for rail, cv, g in (('VA', '220u 25V', 'GNDA'), ('VL', '47u 25V', 'GNDD')):
    k = dict(mpn='Panasonic ERJ-P06J100V') if rail == 'VA' else {}     # anti-surge, as strip R1/R2 (MG17)
    R(b, '10R', '+VBUS', '+' + rail, **k); CP(b, cv, '+' + rail, g)
    R(b, '10R', '-VBUS', '-' + rail, **k); CP(b, cv, g, '-' + rail)
P(b, ref('NT'), 'NT', 'AGND-LGND star', {1: 'GNDA', 2: 'GNDD'})
P(b, ref('CN'), 'TAB', 'Ground spade 6.3mm', {1: 'GNDA'})
R(b, '10R GND cancel', 'GNDA', 'GCANCEL')
for i, n in enumerate(['+VBUS', '-VBUS', '+VA', '-VA', '+VL', '-VL', 'GNDA', 'GNDD']):
    P(b, f'#FLG{i + 1:02d}', 'FLAG', 'PWR_FLAG', {1: n})

b = block('RIBBON  one 34-pin header, Delta pinout (as a strip); AUX 5-6 are summed on the master module')
hdr = {1: 'NC', 3: 'NC', 5: 'NC', 7: 'NC', 19: 'NC', 9: 'SUB4', 11: 'SUB3', 13: 'SUB2', 15: 'SUB1',
       17: 'MIXR', 18: 'MIXL', 20: 'NC', 21: 'NC', 22: 'AUX4', 23: 'AUX3', 24: 'AUX1', 25: 'AUX2', 26: 'GCANCEL',
       27: 'PFL', 28: 'NC', 29: 'PFLDET', 30: '-VBUS', 31: '-VBUS', 32: '+VBUS', 33: '+VBUS', 34: 'NC'}
hdr.update({k: 'GNDA' for k in range(2, 17, 2)})
P(b, ref('CN'), 'HDR', 'Bus 2x17', hdr)

# two boards on one bus would share a summing node with separate feedbacks: the difference mode has no feedback and
# both summers rail (master_group_review.md MG19). One SUB and one AUX jumper per board, unique across the four
b = block('BUS SELECT  close ONE SUB jumper and ONE AUX jumper: group n sums SUB n and AUX n (all open = summer idle)')
for k in range(1, 5):
    P(b, ref('JP'), 'SJO', f'SUB {k} select', {1: 'SUB_SEL', 2: f'SUB{k}'})
for k in range(1, 5):
    P(b, ref('JP'), 'SJO', f'AUX {k} select', {1: 'AUX_SEL', 2: f'AUX{k}'})

b = block('GROUND CANCEL BUFFER  (local, for this module\'s re-inverters; summing amps use the raw GCANCEL line)')
amp(b, 'GCANCEL', 'GC_BUF', 'GC_BUF')

b = block('SUBGROUP: sum (selected SUB bus), re-invert, insert, fader + post-amp, DRV134 out, pan to MIX, AFL  [spec 12]')
s = 'S'
summer(b, 'SUB_SEL', s + '_SUM', '4K7', '100p')
reinv(b, s + '_SUM', s + '_MIX', gref='GC_BUF')
insert(b, s + '_MIX', s + '_PRE', 'SUB')
P(b, ref('RV'), 'POT', 'Sub fader 10K log 100mm', {1: 'GNDA', 3: s + '_PRE', 2: s + '_W'}, fp=FADER_FP, mpn='Bourns PTB0143-2010BPA103')
post_amp(b, s + '_W', s + '_POST', s)
drv134(b, s + '_POST', s + '_OP', s + '_ON')
jack(b, 'JACK', 'Sub out TRS', {'T': s + '_OP', 'R': s + '_ON', 'S': 'GNDA'})
P(b, ref('RV'), 'POT2', 'Sub pan 10K dual', {1: s + '_POST', 3: 'GNDA', 2: s + '_PWL', 4: 'GNDA', 6: s + '_POST', 5: s + '_PWR'})
for sd in 'LR':                 # 10p against the pan wiper's Cdiff lag (MG5)
    near(C(b, '10p C0G', f'{s}_PW{sd}', 'GNDA'), amp(b, f'{s}_PW{sd}', f'{s}_PB{sd}', f'{s}_PB{sd}'))
C(b, '220u NP 25V', s + '_PBL', s + '_PANL'); R(b, '47K', s + '_PANL', 'GNDA')
C(b, '220u NP 25V', s + '_PBR', s + '_PANR'); R(b, '47K', s + '_PANR', 'GNDA')
routing(b, s + '_PANL', s + '_PANR', 'MIXL', 'MIXR', 'Sub to MIX')
R(b, '22K', s + '_POST', s + '_AFLJ'); afl(b, s + '_AFLJ', 'Sub AFL')

b = block('AUX MASTER: OPA1612 sum (selected AUX bus, 22K || 100p) + re-invert, level, buffer, DRV134 out, AFL  [spec 13]')
a = 'A'
with new_package():                     # every strip's 22K is always on the aux bus: noise gain 25, so the OPA1612
    summer(b, 'AUX_SEL', a + '_SUM', '22K', '100p')
    reinv(b, a + '_SUM', a + '_MIX', gref='GC_BUF')
C(b, '47u NP 25V', a + '_MIX', a + '_PT')
P(b, ref('RV'), 'POT', 'Aux master 10K log', {1: 'GNDA', 3: a + '_PT', 2: a + '_W'})
level_buffer(b, a + '_W', a + '_OUT', a)
drv134(b, a + '_OUT', a + '_OP', a + '_ON')
jack(b, 'JACK', 'Aux out TRS', {'T': a + '_OP', 'R': a + '_ON', 'S': 'GNDA'})
R(b, '22K', a + '_OUT', a + '_AFLJ'); afl(b, a + '_AFLJ', 'Aux AFL')

b = block('STEREO RETURN: receivers (R normalled to L), level, buffers, MIX / 1-2 / 3-4 onto the ribbon, PFL  [spec 16]')
r = 'RT'
stereo_in(b, 'Return', r + '_L', r + '_R')
for sd in 'LR':
    C(b, '47u NP 25V', f'{r}_{sd}', f'{r}_PRE{sd}'); R(b, '47K', f'{r}_PRE{sd}', 'GNDA')
P(b, ref('RV'), 'POT2', 'Return level 10K log dual', {1: 'GNDA', 3: r + '_PREL', 2: r + '_WL', 4: 'GNDA', 6: r + '_PRER', 5: r + '_WR'}, mpn=POT2A_MPN)
for sd in 'LR':
    level_buffer(b, f'{r}_W{sd}', f'{r}_B{sd}', f'{r}{sd}')
    C(b, '220u NP 25V', f'{r}_B{sd}', f'{r}_RTN{sd}'); R(b, '47K', f'{r}_RTN{sd}', 'GNDA')
for busl, busr, nm in (('MIXL', 'MIXR', 'MIX'), ('SUB1', 'SUB2', '1-2'), ('SUB3', 'SUB4', '3-4')):
    routing(b, r + '_RTNL', r + '_RTNR', busl, busr, f'Return {nm}')
R(b, '43K', r + '_PREL', r + '_PFLJ'); R(b, '43K', r + '_PRER', r + '_PFLJ')
afl(b, r + '_PFLJ', 'Return PFL')
spares(b)

JACKS = collected(); NL, LINK = link_pins(JACKS)
b = block(f'JACK BOARD LINK  2x{NL} IDC ribbon to the group jack board (5 jacks); bottom side, as the strip\'s CN3')
link_header(b, NL, LINK, f'Jack board link 2x{NL}')

project_file(OUT); parts_sidecar(OUT)
build(OUT, 'group', 'Group module (sub + stereo return + aux master) - goa console',
      {1: 'Generated by tools/gen_group.py; circuits from master_section_spec.md 12, 13, 16 (master_lib.py)',
       2: 'Four identical boards; close one SUB and one AUX select jumper per board'},
      paper='auto', perrow=22, revision='0.2')

jack_board(os.path.join(ROOT, 'group_jack_board.kicad_sch'), 'group_jack_board',
           'Group module jack board - goa console (sub out, insert, aux out, return L/R)', JACKS, NL, LINK)
