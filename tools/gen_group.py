"""Generate the group module schematic (docs/studies/master_panel_study.md, option M1): sub n + two stereo returns + aux n
master on one 8 HP board (the second return: docs/reviews/feature_gaps.md RET1, 2026-10-26) that sits on the ribbon like a strip. Four identical boards; on each, close one SUB
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
b = bpw = block('POWER AND GROUNDS  (as a strip: 10R + 220u per audio rail, 10R + 47u logic rails, spade, 10R ground cancel)')
for rail, cv, g in (('VA', '220u 25V', 'GNDA'), ('VL', '47u 25V', 'GNDD')):
    # CS6 (docs/proposals/cs6_proposal.md): fusible, as strip R1-R4 (was an anti-surge 0805 on VA, MG17): a short behind one opens it
    k = dict(fp='Resistor_SMD:R_1206_3216Metric', mpn='Vishay M251206BB1009JP500')
    r1 = R(b, '10R', '+VBUS', '+' + rail, **k); c1 = CP(b, cv, '+' + rail, g)
    r2 = R(b, '10R', '-VBUS', '-' + rail, **k); c2 = CP(b, cv, g, '-' + rail)
    chain(b, '+VBUS', [('s', r1), ('g', c1)], '+' + rail); chain(b, '-VBUS', [('s', r2), ('g', c2)], '-' + rail)
nt = ref('NT'); P(b, nt, 'NT', 'AGND-LGND star', {1: 'GNDA', 2: 'GNDD'})
tab = ref('CN'); P(b, tab, 'TAB', 'Ground spade 6.3mm', {1: 'GNDA'})
rgc = R(b, '10R GND cancel', 'GNDA', 'GCANCEL')
frag(b, 22, 10, lambda d: frags.grounds(d, nt, tab, rgc))
for i, n in enumerate(['+VBUS', '-VBUS', '+VA', '-VA', '+VL', '-VL', 'GNDA', 'GNDD']):
    P(b, f'#FLG{i + 1:02d}', 'FLAG', 'PWR_FLAG', {1: n})
frag(b, 40, 9, lambda d: frags.flags(d, [f'#FLG{i + 1:02d}' for i in range(8)], per=8), last=True)

b = block('RIBBON  one 34-pin header, Delta pinout (as a strip); AUX 5-6 are summed on the master module')
hdr = {1: 'NC', 3: 'NC', 5: 'NC', 7: 'NC', 19: 'NC', 9: 'SUB4', 11: 'SUB3', 13: 'SUB2', 15: 'SUB1',
       17: 'MIXR', 18: 'MIXL', 20: 'NC', 21: 'NC', 22: 'AUX4', 23: 'AUX3', 24: 'AUX1', 25: 'AUX2', 26: 'GCANCEL',
       27: 'PFL', 28: 'NC', 29: 'PFLDET', 30: '-VBUS', 31: '-VBUS', 32: '+VBUS', 33: '+VBUS', 34: '+VBUS'}   # 34: third +V (W1)
hdr.update({k: 'GNDA' for k in range(2, 17, 2)})
cn = ref('CN'); P(b, cn, 'HDR', 'Bus 2x17', hdr); frag(b, 40, 22, lambda d: frags.header(d, cn, 18, 10))

# two boards on one bus would share a summing node with separate feedbacks: the difference mode has no feedback and
# both summers rail (docs/reviews/master_group_review.md MG19). One SUB and one AUX jumper per board, unique across the four
b = block('BUS SELECT  close ONE SUB jumper and ONE AUX jumper: group n sums SUB n and AUX n (all open = summer idle)')
for sel in ('SUB', 'AUX'):
    jps = [ref('JP') for k in range(4)]
    for k, jp in enumerate(jps, 1): P(b, jp, 'SJO', f'{sel} {k} select', {1: f'{sel}_SEL', 2: f'{sel}{k}'})
    frag(b, 16, 16, lambda d, j=jps, s=sel: frags.select(d, j, f'{s}_SEL'))

b = block('GROUND CANCEL BUFFER  (local, for this module\'s re-inverters; summing amps use the raw GCANCEL line)')
amp(b, 'GCANCEL', 'GC_BUF', 'GC_BUF'); gcu = LAST[0]
frag(b, 16, 9, lambda d: frags.follower(d, 'GCANCEL', 'GC_BUF', gcu))

b = block('SUBGROUP: sum (selected SUB bus), re-invert, insert, fader + post-amp, DRV134 out, pan to MIX, AFL  [spec 12]')
s = 'S'
summer(b, 'SUB_SEL', s + '_SUM', '4K7', '100p')
reinv(b, s + '_SUM', s + '_MIX', gref='GC_BUF')
insert(b, s + '_MIX', s + '_PRE', 'SUB')
rv = ref('RV'); P(b, rv, 'POT', 'Sub fader 10K log 100mm', {1: 'GNDA', 3: s + '_PRE', 2: s + '_W'}, fp=FADER_FP, mpn='Bourns PTB0143-2010BPA103')
frag(b, 12, 9, lambda d: frags.pot(d, rv, s + '_PRE', s + '_W'))
post_amp(b, s + '_W', s + '_POST', s)
drv134(b, s + '_POST', s + '_OP', s + '_ON')
jack(b, 'JACK', 'Sub out TRS', {'T': s + '_OP', 'R': s + '_ON', 'S': 'CHASSIS'})   # G2b
rp = ref('RV'); P(b, rp, 'POT2', 'Sub pan 10K lin dual CD', {1: s + '_POST', 3: 'GNDA', 2: s + '_PWL', 4: 'GNDA', 6: s + '_POST', 5: s + '_PWR'},
                  fp='Potentiometer_THT:Potentiometer_Alps_RK09L_Double_Vertical', mpn='ALPS RK09L1240015')   # as strip RV8 (docs/reviews/design_review.md R2)
frag(b, 14, 8, lambda d: frags.pot2(d, rp))
# CS2b (docs/proposals/cs2b_proposal.md): the Delta's pan law on the sub pan too, as the strip's (CS2): each buffer at 1.22x with a 3K3
# law resistor back to its wiper, -2.7 dB at centre, +1.7 dB hard over; the R / C are made last (after drv_loop_rs())
LAW = []
for sd in 'LR':                 # 10p against the pan wiper's Cdiff lag (MG5)
    pc = C(b, '10p C0G', f'{s}_PW{sd}', 'GNDA'); near(pc, amp(b, f'{s}_PW{sd}', f'{s}_PBN{sd}', f'{s}_PB{sd}'))
    LAW.append((b, sd, LAST[0], []))
    frag(b, 16, 14, lambda d, u=LAST[0], c=pc, sd=sd, ps=LAW[-1][3]: frags.law_buffer(d, f'{s}_PW{sd}', f'{s}_PB{sd}', u, c, ps))
for sd in 'LR':
    chain(b, f'{s}_PB{sd}', [('s', C(b, '220u NP 25V', f'{s}_PB{sd}', f'{s}_PAN{sd}')), ('g', R(b, '47K', f'{s}_PAN{sd}', 'GNDA'))], f'{s}_PAN{sd}')
routing(b, s + '_PANL', s + '_PANR', 'MIXL', 'MIXR', 'Sub to MIX')
chain(b, s + '_POST', [('s', R(b, '22K', s + '_POST', s + '_AFLJ'))], s + '_AFLJ'); afl(b, s + '_AFLJ', 'Sub AFL')

b = block('AUX MASTER: OPA1612 sum (selected AUX bus, 22K || 100p) + re-invert, level, buffer, DRV134 out, AFL  [spec 13]')
a = 'A'
with new_package():                     # every strip's 22K is always on the aux bus: noise gain 25, so the OPA1612
    summer(b, 'AUX_SEL', a + '_SUM', '22K', '100p')
    reinv(b, a + '_SUM', a + '_MIX', gref='GC_BUF')
chain(b, a + '_MIX', [('s', C(b, '47u NP 25V', a + '_MIX', a + '_PT'))], a + '_PT')
ra = ref('RV'); P(b, ra, 'POT', 'Aux master 10K log', {1: 'GNDA', 3: a + '_PT', 2: a + '_W'})
frag(b, 12, 9, lambda d: frags.pot(d, ra, a + '_PT', a + '_W'))
level_buffer(b, a + '_W', a + '_OUT', a)
drv134(b, a + '_OUT', a + '_OP', a + '_ON')
jack(b, 'JACK', 'Aux out TRS', {'T': a + '_OP', 'R': a + '_ON', 'S': 'CHASSIS'})   # G2b
chain(b, a + '_AFLC', [('s', R(b, '22K', a + '_AFLC', a + '_AFLJ'))], a + '_AFLJ'); afl(b, a + '_AFLJ', 'Aux AFL')   # RV7, as the master's
LATE_AFL = (b, a)                                 # the film is made last (after CS2b)

def stereo_return(title, r, name):
    """A stereo return as on the master (spec 16): receivers (R normalled to L), level, buffers, MIX / 1-2 / 3-4 onto
    the ribbon, PFL. r: net prefix; name: what the jacks, keys and pot are called."""
    b = block(title)
    stereo_in(b, name.replace(' ', ''), r + '_L', r + '_R', label=name)
    for sd in 'LR':
        chain(b, f'{r}_{sd}', [('s', C(b, '47u NP 25V', f'{r}_{sd}', f'{r}_PRE{sd}')), ('g', R(b, '47K', f'{r}_PRE{sd}', 'GNDA'))], f'{r}_PRE{sd}')
    rr2 = ref('RV'); P(b, rr2, 'POT2', f'{name} level 10K log dual', {1: 'GNDA', 3: r + '_PREL', 2: r + '_WL', 4: 'GNDA', 6: r + '_PRER', 5: r + '_WR'}, mpn=POT2A_MPN)
    frag(b, 14, 8, lambda d: frags.pot2(d, rr2))
    for sd in 'LR':
        level_buffer(b, f'{r}_W{sd}', f'{r}_B{sd}', f'{r}{sd}')
        chain(b, f'{r}_B{sd}', [('s', C(b, '220u NP 25V', f'{r}_B{sd}', f'{r}_RTN{sd}')), ('g', R(b, '47K', f'{r}_RTN{sd}', 'GNDA'))], f'{r}_RTN{sd}')
    for busl, busr, nm in (('MIXL', 'MIXR', 'MIX'), ('SUB1', 'SUB2', '1-2'), ('SUB3', 'SUB4', '3-4')):
        routing(b, r + '_RTNL', r + '_RTNR', busl, busr, f'{name} {nm}')
    for sd in 'LR': chain(b, f'{r}_PRE{sd}', [('s', R(b, '43K', f'{r}_PRE{sd}', r + '_PFLJ'))], r + '_PFLJ')
    afl(b, r + '_PFLJ', f'{name} PFL')
    return b

stereo_return('STEREO RETURN: receivers (R normalled to L), level, buffers, MIX / 1-2 / 3-4 onto the ribbon, PFL  [spec 16]',
              'RT', 'Return')
while DEFER: DEFER.pop(0)()                     # return 1's followers here, so every part of the board before RET1 keeps its ref
# RET1 (docs/reviews/feature_gaps.md, signed off 2026-10-26): a second stereo return on every group module, eight in the console
b = stereo_return('STEREO RETURN 2: as return 1 (receivers, level, buffers, MIX / 1-2 / 3-4, PFL)  [spec 16]', 'RT2', 'Return 2')
spares(b)

JACKS = collected(); NL, LINK = link_pins(JACKS[:5], skip=('CHASSIS',))   # CHASSIS: standoffs to the panel
b = block(f'JACK BOARD LINK  2x{NL} IDC ribbon to the group jack board (sub, insert, aux, return 1); bottom side, as the strip\'s CN3')
link_header(b, NL, LINK, f'Jack board link 2x{NL}')
# RET1: return 2 has a link of its own. A 2x13 for all seven jacks is 43 mm long; the jack board's one free slot (right
# of AUX OUT, between the jacks' pads) takes ~29 mm, enough for the 2x8 and, beside it, a 2x5
NL2, LINK2 = link_pins(JACKS[5:], skip=('CHASSIS',))
b = block(f'JACK BOARD LINK 2  2x{NL2} IDC ribbon to the group jack board (return 2); bottom side, beside the first')
link_header(b, NL2, LINK2, f'Jack board link 2 2x{NL2}')

# CS10 (docs/studies/console_survey.md §7): a reverse Schottky across each audio rail, as the strip's D16 / D17: a lost supply rail
# (a wing PTC trips) would otherwise be driven past ground by the op-amps' quiescent current (sim/review/cs10/rail_loss.py).
# Created last so every other ref stays; drawn in the power block
dsp, dsn = ref('D'), ref('D')
P(bpw, dsp, 'DSK', 'MBR140SFT1G', {1: '+VA', 2: 'GNDA'}); P(bpw, dsn, 'DSK', 'MBR140SFT1G', {1: 'GNDA', 2: '-VA'})
def _rail_diodes(d):                            # as the strip's D16 / D17 (strip_draw.power_rails): K on +VA, A on -VA
    d.port('+VA', (0, 0)); d.w((0, 0), (4, 0)); d.v(dsp, 4, 1.5, top='+VA', text='R')
    d.port('-VA', (14, 0)); d.w((14, 0), (18, 0)); d.at(dsn, 18, 1.5, rot=270, mirror='x', text='R')
frag(bpw, 28, 6, _rail_diodes)

# CS4b (docs/proposals/cs4b_proposal.md): a BAV199 rail clamp on every jack-link signal at CN3 / CN4, as the strip's D18-D22 (ESD
# and phantom on the jacks; sim/review/cs4/jack_protect.py, jack_protect_mg.py). Created last: no other ref moves
b = block('JACK LINK CLAMPS: a BAV199 to the audio rails on every jack signal at the links (CS4b)')
link_clamps(b, list(LINK.values()) + list(LINK2.values()))
# CS4c (docs/proposals/cs4c_proposal.md): 22R inside each DRV135 loop, drawn with its driver; created last as well
drv_loop_rs()
# CS2b: the sub pan buffers' law network, made last so every other ref stays
for bb, sd, u, ps in LAW:
    ps += [R(bb, '3K3', f'{s}_PW{sd}', f'{s}_PB{sd}'), R(bb, '2K2', f'{s}_PBN{sd}', f'{s}_PB{sd}'),
           R(bb, '10K', f'{s}_PBN{sd}', 'GNDA'), C(bb, '22p C0G', f'{s}_PBN{sd}', f'{s}_PB{sd}')]
# docs/proposals/clicks_proposal.md RV7 (signed off 2026-10-28): the aux AFL film, made last so every ref above stays
C(LATE_AFL[0], '2.2u', LATE_AFL[1] + '_OUT', LATE_AFL[1] + '_AFLC')

project_file(OUT); parts_sidecar(OUT)
build(OUT, 'group', 'Group module - goa console (sub + return + aux master)',
      {1: 'Generated by tools/gen_group.py (master_lib.py; master spec 12, 13, 16)',
       2: 'Four identical boards; close one SUB and one AUX select jumper per board'},
      paper='auto', perrow=22, revision='0.12', flowed=True, last=('POWER AND GROUNDS', 'RIBBON'),   # group v0.12 (RET1) + CS2b / CS4b / CS4c / CS6 / CS10
      pages=dict(paper='A4', folder='group_sheets'))       # A4 sub-sheets under a root sheet (prints on A4)

jack_board(os.path.join(ROOT, 'group_jack_board.kicad_sch'), 'group_jack_board',
           'Group module jack board - goa console (sub out, insert, aux out, return 1 and 2 L/R)', JACKS, NL, LINK, holes=2,
           more=[(NL2, LINK2, f'Main board link 2 2x{NL2}')])
