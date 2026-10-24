"""Generate the channel-strip schematic from its netlist (the P(...) calls below), and the jack-board
schematic (jack_board.kicad_sch, written next to it). Builder and part maps are in schgen.py."""
import os, sys
import schgen
from schgen import block, P, build, FADER_FP, CAP_FP, SYM, FP

SYM.update({'CONN6': ('Connector_Generic', 'Conn_01x06'), 'CONN2': ('Connector_Generic', 'Conn_01x02'),
            'LINK': ('Connector_Generic', 'Conn_02x05_Odd_Even'),
            'DG': ('Analog_Switch', 'DG413xY'), 'ZEN': ('Diode', 'BZX84Cxx'), 'SCH': ('Diode', 'BAT54W')})
schgen.MPN.update({'DG': 'Vishay DG413DY-E3', 'ZEN': 'BZX84C5V1', 'SCH': 'Nexperia BAT54W',
                   'OPA': 'TI OPA1612AIDR', 'CMP': 'TI LM393BIDR', 'JFET': 'onsemi MMBFJ112'})
# strip_parts_review.md T9/T10: ceramics >= 25 V (50 V X7R here), anti-surge resistors where the power is marginal
CAP_MPN = {'100n': 'Samsung CL21B104KBCNNNC (X7R 50V)', '1u': 'Murata GRM21BR71H105KA12 (X7R 50V)',
           '2.2u film': 'WIMA MKS2C042201K00KSSD (PET 63V)',
           # audio bipolars, Nichicon MUSE ES 25 V, in the existing footprints (film_np_proposal.md)
           '33u NP 25V': 'Nichicon UES1E330MPM (MUSE ES)', '100u NP 25V': 'Nichicon UES1E101MPM (MUSE ES)'}
FILM_2U2 = 'Capacitor_THT:C_Rect_L7.2mm_W7.2mm_P5.00mm_FKS2_FKP2_MKS2_MKP2'
LED_MPN = {'red': 'Kingbright WP710A10ID', 'green': 'Kingbright WP710A10GD', 'yellow': 'Kingbright WP710A10YD'}
FP.update({'CONN6': 'Connector_PinSocket_2.54mm:PinSocket_1x06_P2.54mm_Vertical',
           'CONN2': 'Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical',
           'LINK': 'Connector_IDC:IDC-Header_2x05_P2.54mm_Vertical'})
LINK_MPN = 'Wurth 61201021621 (2x5 box header)'
C0G = 'Capacitor_SMD:C_1206_3216Metric'                                     # C0G up to 100n
FILM_S = 'Capacitor_THT:C_Rect_L7.2mm_W4.5mm_P5.00mm_FKS2_FKP2_MKS2_MKP2'     # 150n film
FILM_L = 'Capacitor_THT:C_Rect_L7.2mm_W8.5mm_P5.00mm_FKP2_FKP2_MKS2_MKP2'     # 2.2u film (KiCad's spelling)
POTB = 'Alpha RD901F-40-15R1-B10K-0CD (centre detent)'
# front-panel jacks (Eurorack-style 12U panel, no rear apron): vertical, all-plastic (PA shell, POM cap) = isolated.
# A 1/4" plug goes ~30 mm deep, so the jacks sit on their own board ~24 mm under the panel (the main board is at
# 11.5 mm), joined to the main board by a 10-way IDC ribbon: CN3 (main board, bottom side) <-> CN5 (jack board).
JACK_V = 'Connector_Audio:Jack_6.35mm_Neutrik_NJ6FD-V_Vertical'; JACK_V_MPN = 'Neutrik NJ6FD-V'
# ribbon conductor = pin number: each pair adjacent, grounds between input, send, return and direct out
LINK = {1: 'IN_T', 2: 'IN_R', 3: 'GNDA', 4: 'SEND', 5: 'GNDA', 6: 'RET_RAW', 7: 'GNDA', 8: 'DO_T', 9: 'DO_R', 10: 'GNDA'}
POT2A = 'Alpha RD902F-40-15R1-A10K (dual, log)'

OUT = sys.argv[1] if len(sys.argv) > 1 else 'channel_strip.kicad_sch'
JB_OUT = os.path.join(os.path.dirname(OUT), 'jack_board.kicad_sch')

# ---------------------------------------------------------------- netlist
b = block('POWER ENTRY, LOGIC SUPPLY, GROUNDS, DECOUPLING')
P(b,'R1','R','10R',{1:'+VBUS',2:'+VA'},mpn='Panasonic ERJ-P06J100V'); P(b,'C1','CP','220u 25V',{1:'+VA',2:'GNDA'})
P(b,'C2','C','100n',{1:'+VA',2:'GNDA'})
P(b,'R2','R','10R',{1:'-VBUS',2:'-VA'},mpn='Panasonic ERJ-P06J100V'); P(b,'C3','CP','220u 25V',{1:'GNDA',2:'-VA'})
P(b,'C4','C','100n',{1:'GNDA',2:'-VA'})
P(b,'R3','R','10R',{1:'+VBUS',2:'+VL'}); P(b,'C5','CP','47u 25V',{1:'+VL',2:'GNDD'},fp='Capacitor_THT:CP_Radial_D6.3mm_P2.50mm')
P(b,'R4','R','10R',{1:'-VBUS',2:'-VL'}); P(b,'C6','CP','47u 25V',{1:'GNDD',2:'-VL'},fp='Capacitor_THT:CP_Radial_D6.3mm_P2.50mm')
P(b,'NT1','NT','AGND-LGND star',{1:'GNDA',2:'GNDD'})
P(b,'CN4','TAB','Ground spade 6.3mm',{1:'GNDA'})
P(b,'R5','R','10R GND cancel',{1:'GNDA',2:'GCANCEL'})
for i,(ref,cp,cn) in enumerate([('U1','C20','C21'),('U2','C22','C23'),('U3','C24','C25'),('U5','C29','C30'),
                                  ('U6','C31','C32'),('U7','C33','C34'),('U8','C35','C36'),
                                  ('U12','C63','C64'),('U13','C65','C66'),('U14','C67','C68')]):
    P(b,ref,'OPA','OPA1612',{8:'+VA',4:'-VA'},unit=3)
    P(b,cp,'C','100n',{1:'+VA',2:'GNDA'}); P(b,cn,'C','100n',{1:'GNDA',2:'-VA'})
P(b,'U4','CMP','LM393',{8:'+VL',4:'GNDD'},unit=3); P(b,'C26','C','100n',{1:'+VL',2:'GNDD'})
for i,n in enumerate(['+VA','-VA','+VL','-VL','GNDA','GNDD']):
    P(b,f'#FLG0{i+1}','FLAG','PWR_FLAG',{1:n})

hdr = {1:'NC',3:'NC',5:'NC',7:'NC',19:'NC',9:'SUB4',11:'SUB3',13:'SUB2',15:'SUB1',
       17:'MIXR',18:'MIXL',20:'AUX6',21:'AUX5',22:'AUX4',23:'AUX3',24:'AUX1',25:'AUX2',26:'GCANCEL',
       27:'PFL',28:'NC',29:'PFLDET',30:'-VBUS',31:'-VBUS',32:'+VBUS',33:'+VBUS',34:'NC'}
hdr.update({k:'GNDA' for k in range(2,17,2)})
b = block('MOTHERLOOM  (Delta pinout; one header, crimped socket on a daisy-chained ribbon)')
P(b,'CN1','HDR','Bus 2x17',hdr,mpn='Wurth 61203421621 (2x17 box header)')

b = block('LINE INPUT - ground-compensated receiver (inverting), Ø switch  SW15: latched = phase reversed')
P(b,'CN3','LINK','Jack board link 2x5',LINK,mpn=LINK_MPN)   # J1/J2/J5 and the RF caps C8/C9 are on the jack board
P(b,'R10','R','1M',{1:'IN_T',2:'GNDA'})
P(b,'SW15','SW','Phase',{2:'INV_IN',3:'IN_T',1:'IN_R'},unit=1)     # normal: tip to the inverting leg
P(b,'SW15','SW','Phase',{5:'NINV_IN',6:'IN_R',4:'IN_T'},unit=2)
P(b,'R6','R','10K 0.1%',{1:'INV_IN',2:'U1A_N'}); P(b,'R7','R','10K 0.1%',{1:'U1A_N',2:'RECV'})
P(b,'C7','C','33p C0G',{1:'U1A_N',2:'RECV'})
P(b,'R8','R','10K 0.1%',{1:'NINV_IN',2:'U1A_P'}); P(b,'R9','R','10K 0.1%',{1:'U1A_P',2:'GNDA'})
P(b,'C78','C','33p C0G',{1:'U1A_P',2:'GNDA'},fp=C0G)   # matches C7 across R7: balance and stability
P(b,'U1','OPA','OPA1612',{3:'U1A_P',2:'U1A_N',1:'RECV'},unit=1)

b = block('GAIN  -15..+15 dB, 0 dB at the detent (inverting; pot pin 3 = CW = input end)')
P(b,'R45','R','2K2 1%',{1:'RECV',2:'GA'})
P(b,'RV9','POT','Gain 10K lin CD',{3:'GA',2:'GV',1:'GC'},mpn=POTB)
P(b,'R46','R','2K2 1%',{1:'GC',2:'GOUT'}); P(b,'C37','C','22p C0G',{1:'GOUT',2:'GV'})
P(b,'U1','OPA','OPA1612',{5:'GNDA',6:'GV',7:'GOUT'},unit=2)
P(b,'C38','C','33u NP 25V',{1:'GOUT',2:'HIN'},fp=CAP_FP['47u']); P(b,'R47','R','47K',{1:'HIN',2:'GNDA'})

b = block('HPF  unity Sallen-Key Butterworth, -3 dB 87 Hz  SW11: latched = HPF in (unlatched shorts the caps)')
P(b,'C39','C','47n C0G',{1:'HIN',2:'H1'},fp=C0G); P(b,'C40','C','47n C0G',{1:'H1',2:'HP'},fp=C0G)
P(b,'R48','R','27K',{1:'H1',2:'HOUT'}); P(b,'R49','R','56K',{1:'HP',2:'GNDA'})
P(b,'U5','OPA','OPA1612',{3:'HP',2:'HOUT',1:'HOUT'},unit=1)
P(b,'SW11','SW','HPF',{2:'HIN',3:'HP',1:'NC'},unit=1)
P(b,'SW11','SW','HPF',{5:'NC',4:'NC',6:'NC'},unit=2)

b = block('INSERT POSITION JUMPERS  1-2 = insert post-EQ (default);  2-3 on all three = insert pre-EQ')
P(b,'JP6','SJ3','EQ input',{1:'HOUT',3:'BUF1',2:'EQIN'})
P(b,'JP5','SJ3','Insert send source',{1:'EQOUT',3:'HOUT',2:'INS_SRC'})
P(b,'JP7','SJ3','PRE source',{1:'BUF1',3:'EQOUT',2:'PRESRC'})

b = block('EQ  Delta ED3344A/ED3151 values: HF shelf (U5B), HI-MID (U6A), LO-MID (U6B), LF (U7A); CW = boost')
P(b,'R50','R','33K',{1:'EQIN',2:'EQ_V3'}); P(b,'R51','R','33K',{1:'EQ_O3',2:'EQ_V3'}); P(b,'C41','C','33p C0G',{1:'EQ_O3',2:'EQ_V3'})
P(b,'U5','OPA','OPA1612',{5:'GNDA',6:'EQ_V3',7:'EQ_O3'},unit=2)
P(b,'RV10','POT','HF 10K lin CD',{3:'EQIN',2:'EQ_WHF',1:'EQ_O3'},mpn=POTB)
P(b,'C42','C','4n7 C0G',{1:'EQ_WHF',2:'EQ_T1'},fp=C0G); P(b,'R52','R','5K6',{1:'EQ_T1',2:'GNDA'})
P(b,'C43','C','4n7 C0G',{1:'EQ_T1',2:'EQ_T2'},fp=C0G); P(b,'R53','R','6K8',{1:'EQ_T2',2:'EQ_V3'})
P(b,'R54','R','22K',{1:'EQ_O3',2:'EQ_M4'}); P(b,'R55','R','22K',{1:'EQ_O4',2:'EQ_M4'})
# 10p across both 22Ks: ~0 deg phase margin without (TI OPA161x model); equal caps leave the EQ unchanged
P(b,'C69','C','10p C0G',{1:'EQ_O3',2:'EQ_M4'},fp=C0G); P(b,'C70','C','10p C0G',{1:'EQ_O4',2:'EQ_M4'},fp=C0G)
P(b,'U6','OPA','OPA1612',{3:'EQ_MP',2:'EQ_M4',1:'EQ_O4'},unit=1)
P(b,'RV11','POT','HI-MID gain 10K lin CD',{3:'EQ_O4',2:'EQ_WHM',1:'EQ_O3'},mpn=POTB)
P(b,'R58','R','22K',{1:'EQ_O4',2:'EQ_L4'}); P(b,'R59','R','22K',{1:'EQ_O5',2:'EQ_L4'})
P(b,'C71','C','10p C0G',{1:'EQ_O4',2:'EQ_L4'},fp=C0G); P(b,'C72','C','10p C0G',{1:'EQ_O5',2:'EQ_L4'},fp=C0G)
P(b,'U6','OPA','OPA1612',{5:'EQ_LP',6:'EQ_L4',7:'EQ_O5'},unit=2)
P(b,'RV13','POT','LO-MID gain 10K lin CD',{3:'EQ_O5',2:'EQ_WLM',1:'EQ_O4'},mpn=POTB)

# Mid bands: the Delta's Wien band-pass (needs a 100K C-law dual, not stocked) replaced by a KHN state-variable
# band-pass with the same response (peak 0.407, Q 0.275, in phase) into U6A/U6B's + input, tuned by a stocked
# A10K dual: each gang a divider from the driving op-amp (pin 3) to 430R (pin 1), 13K wiper-to-top, wiper -> 4K7
# -> integrator. CW = higher frequency, within 0.3 octave of a log sweep. sim/mid_tuning.py, strip spec 6.2.
b = block('EQ MID TUNING  KHN band-pass per mid band: summer (10K x3, BP via 2K2/10K), two integrators, A10K dual')
for (nm, wip, bp, sm, sp, hp, lp, d1, d2, r1, r2, i1, i2, pot, ci1, ci2, c1v, c2v, rb1, rb2, rs, us, ui1, ui2, cs) in (
        ('HI-MID', 'EQ_WHM', 'EQ_MP', 'EQ_MSM', 'EQ_MSP', 'EQ_MHP', 'EQ_MLP', 'EQ_MD1', 'EQ_MD2', 'EQ_MR1', 'EQ_MR2',
         'EQ_MI1', 'EQ_MI2', 'RV12', 'C44', 'C45', '2n2 C0G', '4n7 C0G', 'R56', 'R57',
         ('R81', 'R82', 'R83', 'R84', 'R85', 'R86', 'R87', 'R88', 'R89'), ('U12', 1), ('U12', 2), ('U13', 1), ('C74', 'C75')),
        ('LO-MID', 'EQ_WLM', 'EQ_LP', 'EQ_LSM', 'EQ_LSP', 'EQ_LHP', 'EQ_LLP', 'EQ_LD1', 'EQ_LD2', 'EQ_LR1', 'EQ_LR2',
         'EQ_LI1', 'EQ_LI2', 'RV14', 'C46', 'C47', '10n C0G', '22n C0G', 'R60', 'R61',
         ('R90', 'R91', 'R92', 'R93', 'R94', 'R95', 'R96', 'R97', 'R98'), ('U13', 2), ('U14', 1), ('U14', 2), ('C76', 'C77'))):
    rin, rlp, rfb, r4, r5, r0a, r0b, rta, rtb = rs
    P(b,rin,'R','10K 1%',{1:wip,2:sm}); P(b,rlp,'R','10K 1%',{1:lp,2:sm}); P(b,rfb,'R','10K 1%',{1:hp,2:sm})
    P(b,r4,'R','2K2 1%',{1:bp,2:sp}); P(b,r5,'R','10K 1%',{1:sp,2:'GNDA'})
    # ~3 deg phase margin without these: 10p across the feedback 10K, 22p on the + input (its 1.8 kohm lags through Cdiff)
    P(b,cs[0],'C','10p C0G',{1:hp,2:sm},fp=C0G); P(b,cs[1],'C','22p C0G',{1:sp,2:'GNDA'},fp=C0G)
    pp = {1: (3, 2, 1), 2: (5, 6, 7)}
    P(b,us[0],'OPA','OPA1612',dict(zip(pp[us[1]], (sp, sm, hp))),unit=us[1])            # summer: HP out
    # integrator 1 (HP -> BP) through gang A, integrator 2 (BP -> LP) through gang B
    P(b,pot,'POT2',f'{nm} freq 10K A dual',{3:hp,2:d1,1:r1,6:bp,5:d2,4:r2},mpn=POT2A)
    P(b,r0a,'R','430R 1%',{1:r1,2:'GNDA'}); P(b,r0b,'R','430R 1%',{1:r2,2:'GNDA'})
    P(b,rta,'R','13K 1%',{1:hp,2:d1}); P(b,rtb,'R','13K 1%',{1:bp,2:d2})
    P(b,rb1,'R','4K7 1%',{1:d1,2:i1}); P(b,rb2,'R','4K7 1%',{1:d2,2:i2})
    P(b,ci1,'C',c1v,{1:bp,2:i1},fp=C0G); P(b,ci2,'C',c2v,{1:lp,2:i2},fp=C0G)
    P(b,ui1[0],'OPA','OPA1612',dict(zip(pp[ui1[1]], ('GNDA', i1, bp))),unit=ui1[1])
    P(b,ui2[0],'OPA','OPA1612',dict(zip(pp[ui2[1]], ('GNDA', i2, lp))),unit=ui2[1])
P(b,'R66','R','22K',{1:'EQ_O5',2:'EQ_F4'}); P(b,'R67','R','22K',{1:'EQ_O6',2:'EQ_F4'})
P(b,'C73','C','22p C0G',{1:'EQ_O6',2:'EQ_F4'},fp=C0G)   # one 22p (not a pair): it drives the insert send, cables
P(b,'U7','OPA','OPA1612',{3:'EQ_FP',2:'EQ_F4',1:'EQ_O6'},unit=1)
P(b,'R62','R','3K3',{1:'EQ_O5',2:'EQ_F1'}); P(b,'R63','R','3K3',{1:'EQ_F2',2:'EQ_O6'})
P(b,'RV15','POT','LF 10K lin CD',{1:'EQ_F1',2:'EQ_WLF',3:'EQ_F2'},mpn=POTB)
P(b,'C48','C','150n film',{1:'EQ_F1',2:'EQ_F2'},fp=FILM_S)
P(b,'R64','R','1K5',{1:'EQ_WLF',2:'EQ_F3'}); P(b,'C49','C','2.2u film',{1:'EQ_F3',2:'EQ_FP'},fp=FILM_L)   # MPN from CAP_MPN
P(b,'C50','C','100n C0G',{1:'EQ_FP',2:'GNDA'},fp=C0G); P(b,'R65','R','5K1',{1:'EQ_FP',2:'GNDA'})

b = block('EQ IN  SW12: latched = EQ in (unlatched = bypass from the EQ input); green EQ LED')
P(b,'SW12','SW','EQ',{2:'EQSEL',1:'EQ_O6',3:'EQIN'},unit=1)
P(b,'SW12','SW','EQ',{5:'+VL',4:'EQ_ON',6:'NC'},unit=2)
P(b,'R69','R','4K7',{1:'EQ_ON',2:'EQ_LA'}); P(b,'D5','LED','EQ green',{2:'EQ_LA',1:'GNDD'},mpn=LED_MPN['green'])
P(b,'C51','C','33u NP 25V',{1:'EQSEL',2:'EQOUT'},fp=CAP_FP['47u']); P(b,'R68','R','47K',{1:'EQOUT',2:'GNDA'})

b = block('INSERT (send = tip, return = ring, ring normalled to send) + return buffer')
P(b,'R11','R','75R',{1:'INS_SRC',2:'SEND'},mpn='Panasonic ERJ-P06J750V')
P(b,'C10','C','33u NP 25V',{1:'RET_RAW',2:'RET'},fp=CAP_FP['47u']); P(b,'R12','R','47K',{1:'RET',2:'GNDA'})
P(b,'R99','R','1K',{1:'RET',2:'RET_IN'})   # bounds the input-diode current on a jack fault (+0.013 dB noise)
P(b,'C84','C','100p C0G',{1:'RET_IN',2:'GNDA'},fp=C0G)   # with R99 a follower on 1K: lags without it (40 deg); RF too
P(b,'U7','OPA','OPA1612',{5:'RET_IN',6:'BUF1',7:'BUF1'},unit=2)
P(b,'C11','C','100u NP 25V',{1:'PRESRC',2:'PRE'},fp=CAP_FP['220u']); P(b,'R13','R','47K',{1:'PRE',2:'GNDA'})

b = block('OVERLOAD DETECTOR (~+18 dBu)')
P(b,'R39','R','1K',{1:'PRESRC',2:'PKA'}); P(b,'D1','D','1N4148',{2:'PKA',1:'PK'})
P(b,'C12','C','1u',{1:'PK',2:'GNDA'}); P(b,'R14','R','470K',{1:'PK',2:'GNDA'})
P(b,'R40','R','10K',{1:'+VL',2:'VREF'}); P(b,'R41','R','10K',{1:'VREF',2:'GNDA'})
P(b,'U4','CMP','LM393',{2:'PK',3:'VREF',1:'OL_K'},unit=1)
P(b,'R15','R','4K7',{1:'+VL',2:'OL_A'}); P(b,'D2','LED','OL red',{2:'OL_A',1:'OL_K'},mpn=LED_MPN['red'])   # ~3 mA, as the other LEDs
P(b,'U4','CMP','LM393',{5:'GNDD',6:'+VL',7:'NC'},unit=2)

b = block('PFL (pre-fade)  SW3: A-B = ON')
P(b,'R32','R','22K',{1:'PRE',2:'PFL_S'})
P(b,'SW3','SW','PFL',{2:'PFL_S',1:'PFL',3:'GNDA'},unit=1)
P(b,'SW3','SW','PFL',{5:'+VL',4:'PFL_ON',6:'NC'},unit=2)
P(b,'R33','R','100K',{1:'PFL_ON',2:'PFLDET'})
P(b,'R34','R','4K7',{1:'PFL_ON',2:'PFL_LA'}); P(b,'D3','LED','PFL red',{2:'PFL_LA',1:'GNDD'},mpn=LED_MPN['red'])

b = block('ON / SOFT MUTE (2x J112 shunt, ~20 ms ramp)  SW4: latched = channel ON, green LED')
P(b,'R16','R','4K7',{1:'PRE',2:'M1'}); P(b,'Q1','JFET','MMBFJ112',{1:'M1',2:'GNDA',3:'MGATE'})
P(b,'R17','R','4K7',{1:'M1',2:'M2'}); P(b,'Q2','JFET','MMBFJ112',{1:'M2',2:'GNDA',3:'MGATE'})
P(b,'U3','OPA','OPA1612',{5:'M2',6:'MUTEOUT',7:'MUTEOUT'},unit=2)
P(b,'C81','C','10p C0G',{1:'M2',2:'GNDA'},fp=C0G)   # followers on 1-5 kohm sources: 10p at + (strip review T4)
P(b,'SW4','SW','ON',{2:'MSW',1:'-VL',3:'GNDD'},unit=1)
P(b,'R42','R','220K',{1:'MSW',2:'MGATE'}); P(b,'C28','C','100n',{1:'MGATE',2:'GNDA'})
P(b,'SW4','SW','ON',{5:'+VL',4:'ON_SW',6:'NC'},unit=2)
P(b,'R43','R','4K7',{1:'ON_SW',2:'ON_LA'}); P(b,'D4','LED','ON green',{2:'ON_LA',1:'GNDD'},mpn=LED_MPN['green'])

b = block('FADER + POST-AMP (+10 dB; omit R38 for unity)  JP1 = VCA bypass')
P(b,'RV1','POT','Fader 10K log 100mm',{1:'GNDA',3:'MUTEOUT',2:'WIPER'},fp=FADER_FP,mpn='Bourns PTB0143-2010BPA103')
P(b,'C13','C','2.2u film',{1:'WIPER',2:'VCAIN'},fp=FILM_2U2)
P(b,'JP1','SJ2','VCA bypass',{1:'VCAIN',2:'FPIN'}); P(b,'R18','R','100K',{1:'FPIN',2:'GNDA'})
# VCA module option (spec 7.1): SSI2162 + I/V + inverter on a plug-in module; JP1 bridged when not fitted
P(b,'J3','CONN6','VCA module socket',{1:'VCAIN',2:'FPIN',3:'VCA_CTRL',4:'+VA',5:'GNDA',6:'-VA'},dnp=True)
P(b,'J4','CONN2','VCA control in',{1:'VCA_CTRL',2:'GNDA'},dnp=True); P(b,'R44','R','100K',{1:'VCA_CTRL',2:'GNDA'},dnp=True)
P(b,'U2','OPA','OPA1612',{3:'FPIN',2:'U2A_N',1:'FPOST'},unit=1)
P(b,'C82','C','10p C0G',{1:'FPIN',2:'GNDA'},fp=C0G)   # not above 22p: it sits on U3B's output with the fader at top
P(b,'R19','R','4K7',{1:'FPOST',2:'U2A_N'}); P(b,'C14','C','100p C0G',{1:'FPOST',2:'U2A_N'})
P(b,'R38','R','2K2',{1:'U2A_N',2:'GNDA'})
P(b,'C15','C','100u NP 25V',{1:'FPOST',2:'POST'},fp=CAP_FP['220u']); P(b,'R35','R','47K',{1:'POST',2:'GNDA'})

b = block('AUX SENDS  PRE switch per pair (latched = pre); jumpers 1-2 = pre-fader, 2-3 = pre-EQ.  SW13 DIR: aux 6 pot -> direct out')
for jp,sw,n in (('JP2','SW8','12'),('JP3','SW9','34'),('JP4','SW10','56')):
    P(b,jp,'SJ3',f'Aux{n[0]}/{n[1]} pre source',{1:'PRE',3:'HOUT',2:f'PSRC{n}'})
    P(b,sw,'SW',f'PRE {n[0]}-{n[1]}',{2:f'SRC{n}',1:f'PSRC{n}',3:'POST'},unit=1)
    P(b,sw,'SW',f'PRE {n[0]}-{n[1]}',{5:'NC',4:'NC',6:'NC'},unit=2)
for n,(rv,r,src) in enumerate([('RV2','R20','SRC12'),('RV3','R21','SRC12'),('RV4','R22','SRC34'),
                              ('RV5','R23','SRC34'),('RV6','R24','SRC56'),('RV7','R25','SRC56')],1):
    P(b,rv,'POT',f'Aux{n} 10K log',{1:'GNDA',3:src,2:f'A{n}W'})   # A taper: pin 1 = ground end
    P(b,r,'R','22K',{1:f'A{n}W' if n < 6 else 'A6R',2:f'AUX{n}'})
P(b,'SW13','SW','DIR',{2:'A6W',3:'A6R',1:'DIRSRC'},unit=1)
P(b,'SW13','SW','DIR',{5:'A6R',4:'GNDA',6:'NC'},unit=2)   # DIR: R25 grounded, aux 6 bus sees no floating resistor

b = block('DIRECT OUT  (level = aux 6 pot when DIR is latched; impedance-balanced TRS)')
P(b,'R70','R','100K',{1:'DIRSRC',2:'GNDA'})
P(b,'U8','OPA','OPA1612',{3:'DIRSRC',2:'DOUT',1:'DOUT'},unit=1)
P(b,'C83','C','22p C0G',{1:'DIRSRC',2:'GNDA'},fp=C0G)   # 22p (short direct-out leads); more would load U7B
P(b,'R71','R','75R',{1:'DOUT',2:'DO1'},mpn='Panasonic ERJ-P06J750V'); P(b,'C52','C','33u NP 25V',{1:'DO1',2:'DO_T'},fp=CAP_FP['47u'])
P(b,'R72','R','47K',{1:'DO_T',2:'GNDA'}); P(b,'R73','R','75R',{1:'DO_R',2:'GNDA'})
P(b,'U8','OPA','OPA1612',{5:'GNDA',6:'U8B_O',7:'U8B_O'},unit=2)   # spare half, tied off

b = block('PAN + PAN BUFFERS (AC-coupled outputs)')
P(b,'RV8','POT2','Pan 10K dual',{1:'POST',3:'GNDA',2:'PANWL',4:'GNDA',6:'POST',5:'PANWR'})
P(b,'U2','OPA','OPA1612',{5:'PANWL',6:'PBL',7:'PBL'},unit=2); P(b,'C79','C','10p C0G',{1:'PANWL',2:'GNDA'},fp=C0G)
P(b,'U3','OPA','OPA1612',{3:'PANWR',2:'PBR',1:'PBR'},unit=1); P(b,'C80','C','10p C0G',{1:'PANWR',2:'GNDA'},fp=C0G)
P(b,'C16','C','100u NP 25V',{1:'PBL',2:'PANL'},fp=CAP_FP['220u']); P(b,'R36','R','47K',{1:'PANL',2:'GNDA'})
P(b,'C17','C','100u NP 25V',{1:'PBR',2:'PANR'},fp=CAP_FP['220u']); P(b,'R37','R','47K',{1:'PANR',2:'GNDA'})

b = block('PAN SWITCH  SW14: latched = subgroups panned; unlatched = subgroups get POST, unpanned (MIX always panned)')
P(b,'SW14','SW','PAN',{2:'SUBSRC_L',1:'PANL',3:'POST'},unit=1)
P(b,'SW14','SW','PAN',{5:'SUBSRC_R',4:'PANR',6:'POST'},unit=2)

b = block('ROUTING MATRIX  4K7 summing; DG413 at the bus end: assigned = bus, off = AGND. PVA2: pole A logic, pole B LED')
P(b,'R80','R','4K7',{1:'+VA',2:'+5VL'})                  # DG413 logic supply VL, from +VA so VL never exceeds V+
P(b,'D9','ZEN','BZX84C5V1',{3:'+5VL',1:'GNDD',2:'NC'}); P(b,'C62','C','1u',{1:'+5VL',2:'GNDD'})
P(b,'D10','SCH','BAT54W',{1:'+5VL',3:'+VA',2:'NC'})   # VL <= V+ + 0.3 V at power-down too (DG413 abs max)
P(b,'#FLG07','FLAG','PWR_FLAG',{1:'+5VL'})
for sw,u,rl,rr,sl,sr,bl,br,nm,rpd,rled,dled,cs in [
        ('SW5','U9','R26','R27','PANL','PANR','MIXL','MIXR','L-R','R74','R75','D6',('C53','C54','C55')),
        ('SW6','U10','R28','R29','SUBSRC_L','SUBSRC_R','SUB1','SUB2','1-2','R76','R77','D7',('C56','C57','C58')),
        ('SW7','U11','R30','R31','SUBSRC_L','SUBSRC_R','SUB3','SUB4','3-4','R78','R79','D8',('C59','C60','C61'))]:
    k = nm.replace('-', ''); ctl, rtl, rtr = f'RTE_{k}', f'RT_{rl}', f'RT_{rr}'
    P(b,rl,'R','4K7 1%',{1:sl,2:rtl}); P(b,rr,'R','4K7 1%',{1:sr,2:rtr})
    # S = 4K7 end (common), D = bus or AGND: the bus sees the D-side charge injection (~5 pC at 0 V; S side ~30)
    P(b,u,'DG','DG413',{1:ctl,3:rtl,2:bl},unit=1)             # SW1 (NO): left to the bus
    P(b,u,'DG','DG413',{16:ctl,14:rtl,15:'GNDA'},unit=4)      # SW2 (NC): left to AGND
    P(b,u,'DG','DG413',{8:ctl,6:rtr,7:br},unit=2)             # SW4 (NO): right to the bus
    P(b,u,'DG','DG413',{9:ctl,11:rtr,10:'GNDA'},unit=3)       # SW3 (NC): right to AGND
    P(b,u,'DG','DG413',{13:'+VA',4:'-VA',12:'+5VL',5:'GNDD'},unit=5)
    P(b,cs[0],'C','100n',{1:'+VA',2:'GNDA'}); P(b,cs[1],'C','100n',{1:'GNDA',2:'-VA'})
    P(b,cs[2],'C','100n',{1:'+5VL',2:'GNDD'})
    P(b,sw,'SW',f'Assign {nm}',{2:ctl,1:'+5VL',3:'GNDD'},unit=1)          # pole A: DG413 logic
    P(b,sw,'SW',f'Assign {nm}',{5:'+VL',4:f'RTLED_{k}',6:'NC'},unit=2)    # pole B: routing LED
    P(b,rpd,'R','100K',{1:ctl,2:'GNDD'})                                  # holds IN low through the PVA2's break
    P(b,rled,'R','4K7',{1:f'RTLED_{k}',2:f'RTLA_{k}'}); P(b,dled,'LED',f'{nm} yellow',{2:f'RTLA_{k}',1:'GNDD'},mpn=LED_MPN['yellow'])

for _, ps in schgen.blocks:                     # ceramic MPNs by value (X7R 50 V; C0G parts keep their value text)
    for pt in ps:
        if pt['key'] == 'C' and not pt['mpn']: pt['mpn'] = CAP_MPN.get(pt['value'], '')
build(OUT, 'channel_strip', 'Channel strip - goa console (Delta Theatre input without the mic stage)',
      {1: 'Generated from channel_strip_schematic_spec.md v4.2', 2: 'Nets joined by labels; tidy wiring in Eeschema as needed'},
      paper='auto', revision='4.2')

# ---------------------------------------------------------------- jack board (its own PCB; same net names)
schgen.blocks.clear()
b = block('JACK BOARD  (3 x NJ6FD-V ~24 mm under the panel; 10-way IDC ribbon to CN3 on the main board)')
P(b,'J1','JACKSW','Line in TRS',{'T':'IN_T','R':'IN_R','S':'GNDA','TN':'NC','RN':'NC'},fp=JACK_V,mpn=JACK_V_MPN)
P(b,'C8','C','100p C0G',{1:'IN_T',2:'GNDA'}); P(b,'C9','C','100p C0G',{1:'IN_R',2:'GNDA'})   # RF shunt at the jack
P(b,'J2','JACKSW','Insert TRS switched',{'T':'SEND','RN':'SEND','R':'RET_RAW','TN':'NC','S':'GNDA'},fp=JACK_V,mpn=JACK_V_MPN)
P(b,'J5','JACKSW','Direct out TRS',{'T':'DO_T','R':'DO_R','S':'GNDA','TN':'NC','RN':'NC'},fp=JACK_V,mpn=JACK_V_MPN)
P(b,'CN5','LINK','Main board link 2x5',LINK,mpn=LINK_MPN)
P(b,'#FLG01','FLAG','PWR_FLAG',{1:'GNDA'})
build(JB_OUT, 'jack_board', 'Jack board - goa console channel strip (line in, insert, direct out)',
      {1: 'Generated by tools/gen.py together with channel_strip.kicad_sch (link pinout: LINK)',
       2: 'Spec: channel_strip_schematic_spec.md 16.4'}, paper='A4', revision='4.0')
