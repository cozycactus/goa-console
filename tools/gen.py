"""Generate the channel-strip schematic from its netlist (the P(...) calls below), and the jack-board
schematic (jack_board.kicad_sch, written next to it). Builder and part maps are in schgen.py."""
import os, sys
import schgen, strip_draw
from schgen import P, build, FADER_FP, CAP_FP, SYM, FP
def block(title): return schgen.block(title, draw=strip_draw.for_title(title))   # drawn blocks: strip_draw.py

SYM.update({'CONN6': ('Connector_Generic', 'Conn_01x06'), 'CONN2': ('Connector_Generic', 'Conn_01x02'),
            'LINK': ('Connector_Generic', 'Conn_02x05_Odd_Even'),
            'DG': ('Analog_Switch', 'DG413xY'), 'ZEN': ('Diode', 'BZX84Cxx'), 'SCH': ('Diode', 'BAT54W'),
            'LED2': ('Device', 'LED_Dual_AKA'), 'PNP': ('Transistor_BJT', 'MMBT3906'), 'DD': ('Diode', 'BAV99'), 'DSK': ('Device', 'D_Schottky')})
schgen.MPN.update({'LED2': 'Kingbright WP3VEGW', 'PNP': 'onsemi MMBT3906LT1G', 'DD': 'Nexperia BAV99,215', 'DSK': 'Nexperia PMEG4010CEH,115',
                   'DG': 'Vishay DG413DY-E3', 'ZEN': 'Nexperia BZX84-C5V1,215', 'SCH': 'Nexperia BAT54W,115',
                   'OPA': 'TI OPA1612AIDR', 'CMP': 'TI LM393BIDR', 'JFET': 'onsemi MMBFJ112', 'D': 'Vishay 1N4148-TAP'})
# strip_parts_review.md T9/T10: ceramics >= 25 V (50 V X7R here), anti-surge resistors where the power is marginal
CAP_MPN = {'100n': 'Samsung CL21B104KBCNNNC (X7R 50V)', '10n': 'Samsung CL21B103KBANNNC (X7R 50V)',   # 10n: E6
           '1u': 'Murata GRM21BR71H105KA12L (X7R 50V)',
           '220n': 'Samsung CL21B224KBFNNNE (X7R 50V)',
           # every strip C0G sits on the 1206 footprint (C0G below); a value's voltage is its minimum rating
           '10p C0G': 'KEMET C1206C100J5GACTU', '22p C0G': 'KEMET C1206C220J5GACTU', '33p C0G': 'KEMET C1206C330J5GACTU',
           '100p C0G': 'KEMET C1206C101J5GACTU', '2n2 C0G': 'KEMET C1206C222J5GACTU', '4n7 C0G': 'KEMET C1206C472J5GACTU',
           '10n C0G': 'KEMET C1206C103J5GACTU', '22n C0G': 'KEMET C1206C223J5GACTU', '100n C0G': 'Murata GRM31C5C1H104JA01L',
           # rail reservoirs in the strip's own footprints (D8 P3.5, D6.3 P2.5; the master's UPW parts are larger)
           '220u 25V': 'Rubycon 35ZLH220MEFC8X11.5 (35V)', '47u 25V': 'Panasonic EEU-FR1H470 (50V)',
           '150n film': 'WIMA MKS2D031501C00KSSD (PET 100V; 3.5 x 8.5 x 7.2, the 63 V KSSD code has no stock)',
           '2.2u film': 'WIMA MKS2C042201K00KSSD (PET 63V)',
           # audio bipolars, Nichicon MUSE ES 25 V, in the existing footprints (film_np_proposal.md)
           '33u NP 25V': 'Nichicon UES1E330MPM (MUSE ES)', '100u NP 25V': 'Nichicon UES1E101MPM (MUSE ES)'}
RX_MPN = 'Panasonic ERA-6AEB103V'          # 10K 0.1 % 0805, as the master's receivers
FILM_2U2 = 'Capacitor_THT:C_Rect_L7.2mm_W7.2mm_P5.00mm_FKS2_FKP2_MKS2_MKP2'
LED_MPN = {'red': 'Kingbright WP710A10ID', 'green': 'Kingbright WP710A10GD', 'yellow': 'Kingbright WP710A10YD'}
FP.update({'LED2': 'goa-console:LED_D3.0mm-3_P2.00mm', 'PNP': 'Package_TO_SOT_SMD:SOT-23', 'DD': 'Package_TO_SOT_SMD:SOT-23', 'DSK': 'Diode_SMD:D_SOD-123F',
           'CONN6': 'Connector_PinSocket_2.54mm:PinSocket_1x06_P2.54mm_Vertical',
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
# CS10 (console_survey.md §7): a reverse Schottky across each audio rail. If one supply rail is lost (a wing PTC trips,
# a ribbon conductor opens), the op-amps' ~87 mA keeps flowing into the dead rail and drives it past ground: C1 / C3
# would sit reversed by up to ~13 V and the ICs' pin-protection diodes carry the current (sim/review/cs10/rail_loss.py).
# PMEG4010CEH (40 V, 1 A; 0.34 V at 100 mA) holds the dead rail within 0.36 V of ground
P(b,'D16','DSK','PMEG4010CEH',{1:'+VA',2:'GNDA'}); P(b,'D17','DSK','PMEG4010CEH',{1:'GNDA',2:'-VA'})
P(b,'R3','R','10R',{1:'+VBUS',2:'+VL'}); P(b,'C5','CP','47u 25V',{1:'+VL',2:'GNDD'},fp='Capacitor_THT:CP_Radial_D6.3mm_P2.50mm')
P(b,'R4','R','10R',{1:'-VBUS',2:'-VL'}); P(b,'C6','CP','47u 25V',{1:'GNDD',2:'-VL'},fp='Capacitor_THT:CP_Radial_D6.3mm_P2.50mm')
P(b,'NT1','NT','AGND-LGND star',{1:'GNDA',2:'GNDD'})
P(b,'CN4','TAB','Ground spade 6.3mm',{1:'GNDA'})
P(b,'R5','R','10R GND cancel',{1:'GNDA',2:'GCANCEL'})
for i,(ref,cp,cn) in enumerate([('U1','C20','C21'),('U2','C22','C23'),('U3','C24','C25'),('U5','C29','C30'),
                                  ('U6','C31','C32'),('U7','C33','C34'),('U8','C35','C36'),
                                  ('U12','C63','C64'),('U13','C65','C66'),('U14','C67','C68'),('U15','C89','C90')]):
    P(b,ref,'OPA','OPA1612',{8:'+VA',4:'-VA'},unit=3)
    P(b,cp,'C','100n',{1:'+VA',2:'GNDA'}); P(b,cn,'C','100n',{1:'GNDA',2:'-VA'})
P(b,'U16','OPA1656','OPA1656',{8:'+VA',4:'-VA'},unit=3)   # input followers (ground_study.md G3)
P(b,'C92','C','100n',{1:'+VA',2:'GNDA'}); P(b,'C93','C','100n',{1:'GNDA',2:'-VA'})
P(b,'U4','CMP','LM393',{8:'+VL',4:'GNDD'},unit=3); P(b,'C26','C','100n',{1:'+VL',2:'GNDD'})
P(b,'U17','CMP','LM393',{8:'+VL',4:'GNDD'},unit=3); P(b,'C98','C','100n',{1:'+VL',2:'GNDD'})   # signal detector (MET1)
P(b,'U18','CMP','LM393',{8:'+VL',4:'GNDD'},unit=3); P(b,'C104','C','100n',{1:'+VL',2:'GNDD'})  # negative overload (CS1)
for i,n in enumerate(['+VA','-VA','+VL','-VL','GNDA','GNDD']):
    P(b,f'#FLG0{i+1}','FLAG','PWR_FLAG',{1:n})

hdr = {1:'NC',3:'NC',5:'NC',7:'NC',19:'NC',9:'SUB4',11:'SUB3',13:'SUB2',15:'SUB1',
       17:'MIXR',18:'MIXL',20:'AUX6',21:'AUX5',22:'AUX4',23:'AUX3',24:'AUX1',25:'AUX2',26:'GCANCEL',
       27:'PFL',28:'NC',29:'PFLDET',30:'-VBUS',31:'-VBUS',32:'+VBUS',33:'+VBUS',34:'+VBUS'}   # 34: third +V conductor (wing_power_proposal.md W1)
hdr.update({k:'GNDA' for k in range(2,17,2)})
b = block('MOTHERLOOM  (Delta pinout; one header, crimped socket on a daisy-chained ribbon)')
P(b,'CN1','HDR','Bus 2x17',hdr,mpn='Wurth 61203421621 (2x17 box header)')

b = block('LINE INPUT - buffered ground-compensated receiver (inverting), Ø switch  SW15: latched = phase reversed')
P(b,'CN3','LINK','Jack board link 2x5',LINK,mpn=LINK_MPN)   # J1/J2/J5 and the RF caps C8/C9 are on the jack board
# G3 (ground_study.md, signed off 2026-10-25): OPA1656 followers with 1M bias per leg raise the common-mode input
# impedance from 20K to 1M, so a synth's 1K output no longer unbalances the bridge (CMRR 26 -> 54 dB, worst 5 %);
# 220R limit the fault current into the inputs' protection diodes. J1's normals short both legs when unplugged.
P(b,'R10','R','1M',{1:'IN_T',2:'GNDA'}); P(b,'R112','R','1M',{1:'IN_R',2:'GNDA'})
P(b,'R110','R','220R',{1:'IN_T',2:'IN_TB'}); P(b,'R111','R','220R',{1:'IN_R',2:'IN_RB'})
# 100p at each + input: with the 220R alone the OPA1656's 9.1 pF input capacitance cost the follower ~10 deg (3.3 dB
# closed-loop peaking on the fitted model); with it, no peaking (and a 7 MHz RF low-pass)
P(b,'C94','C','100p C0G',{1:'IN_TB',2:'GNDA'}); P(b,'C95','C','100p C0G',{1:'IN_RB',2:'GNDA'})
P(b,'U16','OPA1656','OPA1656',{3:'IN_TB',2:'U16_OT',1:'U16_OT'},unit=1)
P(b,'U16','OPA1656','OPA1656',{5:'IN_RB',6:'U16_OR',7:'U16_OR'},unit=2)
# 100R build-outs: >= 48.5 deg for any load capacitance (52 deg unloaded; sim/review/ground/follower_stab.py)
P(b,'R113','R','100R',{1:'U16_OT',2:'BUF_T'}); P(b,'R114','R','100R',{1:'U16_OR',2:'BUF_R'})
P(b,'SW15','SW','Phase',{2:'INV_IN',3:'BUF_T',1:'BUF_R'},unit=1)     # normal: tip to the inverting leg
P(b,'SW15','SW','Phase',{5:'NINV_IN',6:'BUF_R',4:'BUF_T'},unit=2)
P(b,'R6','R','10K 0.1%',{1:'INV_IN',2:'U1A_N'},mpn=RX_MPN); P(b,'R7','R','10K 0.1%',{1:'U1A_N',2:'RECV'},mpn=RX_MPN)
P(b,'C7','C','33p C0G',{1:'U1A_N',2:'RECV'})
P(b,'R8','R','10K 0.1%',{1:'NINV_IN',2:'U1A_P'},mpn=RX_MPN); P(b,'R9','R','10K 0.1%',{1:'U1A_P',2:'GNDA'},mpn=RX_MPN)
P(b,'C78','C','33p C0G',{1:'U1A_P',2:'GNDA'},fp=C0G)   # matches C7 across R7: balance and stability
P(b,'U1','OPA','OPA1612',{3:'U1A_P',2:'U1A_N',1:'RECV'},unit=1)

b = block('GAIN  -15..+15 dB, 0 dB at the detent (inverting; pot pin 3 = CW = input end)')
P(b,'R45','R','2K2 1%',{1:'RECV',2:'GA'})
P(b,'RV9','POT','Gain 10K lin CD',{3:'GA',2:'GV',1:'GC'},mpn=POTB)
P(b,'R46','R','2K2 1%',{1:'GC',2:'GOUT'}); P(b,'C37','C','22p C0G',{1:'GOUT',2:'GV'})
P(b,'U1','OPA','OPA1612',{5:'GNDA',6:'GV',7:'GOUT'},unit=2)
P(b,'C38','C','33u NP 25V',{1:'GOUT',2:'HIN'},fp=CAP_FP['47u'])
# C91 doubles C38: with the HPF out SW11 feeds HIN straight to the EQ (~2.5 kohm), 66 uF keeps PRE's LF corner ~1 Hz
P(b,'C91','C','33u NP 25V',{1:'GOUT',2:'HIN'},fp=CAP_FP['47u']); P(b,'R47','R','47K',{1:'HIN',2:'GNDA'})

# Sweepable HPF (hpf_proposal.md): a state-variable high-pass, unity gain, non-inverting, Q 0.707, 21-403 Hz, tuned by
# an A10K dual as the mid bands (430R -> 330R for a 19:1 range). Summer: + from HIN (4K99) and BP (2K49), - from LP
# (2K49) and HP (4K99): gain 1, Q 1/sqrt2. 10p / 22p: 6.6 deg phase margin without them (TI OPA161x), 80 with
b = block('HPF  sweepable 21-403 Hz, state-variable (KHN) high-pass, Q 0.707  SW11: latched = HPF in, else HIN')
P(b,'R100','R','4K99 1%',{1:'HIN',2:'H_SP'}); P(b,'R101','R','2K49 1%',{1:'H_BP',2:'H_SP'})
P(b,'C85','C','22p C0G',{1:'H_SP',2:'GNDA'},fp=C0G)
P(b,'R102','R','2K49 1%',{1:'H_LP',2:'H_SM'}); P(b,'R103','R','4K99 1%',{1:'HP',2:'H_SM'})
P(b,'C86','C','10p C0G',{1:'HP',2:'H_SM'},fp=C0G)
P(b,'U5','OPA','OPA1612',{3:'H_SP',2:'H_SM',1:'HP'},unit=1)
P(b,'RV16','POT2','HPF freq 10K A dual',{3:'HP',2:'H_D1',1:'H_R1',6:'H_BP',5:'H_D2',4:'H_R2'},mpn=POT2A)
P(b,'R104','R','330R 1%',{1:'H_R1',2:'GNDA'}); P(b,'R107','R','330R 1%',{1:'H_R2',2:'GNDA'})
P(b,'R105','R','13K 1%',{1:'HP',2:'H_D1'}); P(b,'R108','R','13K 1%',{1:'H_BP',2:'H_D2'})
P(b,'R106','R','5K6 1%',{1:'H_D1',2:'H_I1'}); P(b,'R109','R','5K6 1%',{1:'H_D2',2:'H_I2'})
P(b,'C87','C','100n C0G',{1:'H_BP',2:'H_I1'},fp=C0G); P(b,'C88','C','100n C0G',{1:'H_LP',2:'H_I2'},fp=C0G)
P(b,'U15','OPA','OPA1612',{3:'GNDA',2:'H_I1',1:'H_BP'},unit=1)
P(b,'U15','OPA','OPA1612',{5:'GNDA',6:'H_I2',7:'H_LP'},unit=2)
P(b,'SW11','SW','HPF',{2:'HOUT',1:'HP',3:'HIN'},unit=1)
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

# LF (U7A): + input from the RV15 bridge network
P(b,'R66','R','22K',{1:'EQ_O5',2:'EQ_F4'}); P(b,'R67','R','22K',{1:'EQ_O6',2:'EQ_F4'})
P(b,'C73','C','22p C0G',{1:'EQ_O6',2:'EQ_F4'},fp=C0G)   # one 22p (not a pair): it drives the insert send, cables
P(b,'U7','OPA','OPA1612',{3:'EQ_FP',2:'EQ_F4',1:'EQ_O6'},unit=1)
P(b,'R62','R','3K3',{1:'EQ_O5',2:'EQ_F1'}); P(b,'R63','R','3K3',{1:'EQ_F2',2:'EQ_O6'})
P(b,'RV15','POT','LF 10K lin CD',{1:'EQ_F1',2:'EQ_WLF',3:'EQ_F2'},mpn=POTB)
P(b,'C48','C','150n film',{1:'EQ_F1',2:'EQ_F2'},fp=FILM_S)
P(b,'R64','R','1K5',{1:'EQ_WLF',2:'EQ_F3'}); P(b,'C49','C','2.2u film',{1:'EQ_F3',2:'EQ_FP'},fp=FILM_2U2)   # MPN from CAP_MPN
P(b,'C50','C','100n C0G',{1:'EQ_FP',2:'GNDA'},fp=C0G); P(b,'R65','R','5K1',{1:'EQ_FP',2:'GNDA'})

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

b = block('OVERLOAD DETECTOR (~+18 dBu, ~150 ms hold) + SIGNAL (~-20 dBu): one red / green LED')
# K3 (gaps_proposal.md, signed off 2026-10-25): C12 100n for a 0.1 ms attack (1u needed ~20 cycles, so short peaks
# never lit the LED); U4A now discharges a hold cap and U4B, the package's spare half, lights the LED while the hold
# node is below VREF: ~150 ms after the last overload (sim/review/gaps/ol_fix.py)
# CS1 (console_survey.md): five taps, both polarities. Each tap -> 1K -> a BAV99's middle (pin 3; pin 1 anode, pin 2
# cathode, Nexperia): the top diode charges PK on positive peaks, the bottom one pulls OL_NN down on negative peaks.
# Taps: the receiver, the gain stage, the EQ out, PRESRC (as before) and the post-amp: the stages that clip first
# (sim/review/gaps/headroom.py); one threshold for all, +18.4 dBu, 4.6 dB below their swing (sim/review/cs1/ol_multi.py)
P(b,'R39','R','1K',{1:'PRESRC',2:'PKA'}); P(b,'D1','DD','BAV99',{1:'OL_NN',3:'PKA',2:'PK'})
for r_, d_, tap, x_ in (('R128','D12','RECV','PKR'),('R129','D13','GOUT','PKG'),('R130','D14','EQOUT','PKE'),
                        ('R131','D15','FPOST','PKF')):
    P(b,r_,'R','1K',{1:tap,2:x_}); P(b,d_,'DD','BAV99',{1:'OL_NN',3:x_,2:'PK'})
P(b,'C12','C','100n',{1:'PK',2:'GNDA'}); P(b,'R14','R','470K',{1:'PK',2:'GNDA'})
P(b,'R40','R','10K',{1:'+VL',2:'VREF'}); P(b,'R41','R','10K',{1:'VREF',2:'GNDA'})
# P2 (met1_ret1_review.md, signed off 2026-10-27): 100 nF on VREF at the divider; VREF runs ~215 mm to U17
P(b,'C100','C','100n',{1:'VREF',2:'GNDA'})
# P1 (met1_ret1_review.md, signed off 2026-10-27): a 1K between each discharge output and its 220n hold cap keeps the
# LM393B's output under its 25 mA rating (17 mA peak); thresholds unchanged (sim/review/gaps/ol.py)
P(b,'U4','CMP','LM393',{2:'PK',3:'VREF',1:'OL_DIS'},unit=1); P(b,'R126','R','1K',{1:'OL_DIS',2:'OL_HOLD'})
# CS1 negative side, PK's mirror: OL_NN rests at ~0.5 V (C103 // R134 to GNDA, as C12 // R14); OL_NC = 2/3 +VL + 1/3
# OL_NN falls below VREF when OL_NN < -VL / 2, and U18A discharges OL_HOLD through R135 (wired-OR with U4A). Ratios of
# +VL only, so the rails' switching order can't light it (the first try, biased from -VL, flashed at power-down)
P(b,'R132','R','4M99 1%',{1:'+VL',2:'OL_NC'}); P(b,'R133','R','10M 1%',{1:'OL_NC',2:'OL_NN'})
P(b,'R134','R','470K',{1:'OL_NN',2:'GNDA'}); P(b,'C103','C','100n',{1:'OL_NN',2:'GNDA'})
P(b,'U18','CMP','LM393',{3:'OL_NC',2:'VREF',1:'OL_NDIS'},unit=1); P(b,'R135','R','1K',{1:'OL_NDIS',2:'OL_HOLD'})
P(b,'U18','CMP','LM393',{5:'VREF',6:'GNDD',7:'NC'},unit=2)        # spare half: + above -, output off
P(b,'R115','R','1M',{1:'+VL',2:'OL_HOLD'}); P(b,'C97','C','220n',{1:'OL_HOLD',2:'GNDD'})
P(b,'U4','CMP','LM393',{5:'OL_HOLD',6:'VREF',7:'OL_K'},unit=2)
# MET1 (feature_gaps.md, signed off 2026-10-26): D2 is a red / green bicolour (Kingbright WP3VEGW, common cathode) in the
# OL LED's place. Red = overload as before; green = signal present from ~-20 dBu with the same ~150 ms hold (U17, as
# U4: U17A against VTH = VREF / 76 = 0.11 V, the -20 dBu peak, discharges SIG_HOLD; U17B lights green while it is
# below VREF). Each colour has a PNP high-side switch, so it draws current only while lit; Q5, from U4B's output, holds
# Q4's base at +VL while the red is on, so an overload shows red alone (and the green draws nothing). 47K bases: ~0.33 mA,
# forced beta ~10 at 3 mA. PRESRC reaches U17A through 47K with a BAT54W clamp to GNDD (sim/review/gaps/ol.py).
P(b,'R116','R','47K',{1:'OL_K',2:'OL_B'}); P(b,'R117','R','47K',{1:'+VL',2:'OL_B'})
P(b,'Q3','PNP','MMBT3906',{1:'OL_B',2:'+VL',3:'OL_C'})
# E6 (emc_placement_study.md, signed off 2026-10-27): 10 nF base to emitter on each LED switch: with the 47K base the
# LED current ramps over ~0.5 ms, so no MET1 line switches fast
P(b,'C101','C','10n',{1:'OL_B',2:'+VL'})
P(b,'R15','R','4K7',{1:'OL_C',2:'OL_A'})                                   # ~3 mA, as the other LEDs
P(b,'R118','R','47K',{1:'PRESRC',2:'SIG_IN'}); P(b,'D11','SCH','BAT54W',{1:'GNDD',3:'SIG_IN',2:'NC'})
P(b,'R119','R','750K',{1:'VREF',2:'VTH'}); P(b,'R120','R','10K',{1:'VTH',2:'GNDA'})   # 760K: loads VREF by 0.7 %
P(b,'U17','CMP','LM393',{2:'SIG_IN',3:'VTH',1:'SIG_DIS'},unit=1); P(b,'R127','R','1K',{1:'SIG_DIS',2:'SIG_HOLD'})
P(b,'R121','R','1M',{1:'+VL',2:'SIG_HOLD'}); P(b,'C99','C','220n',{1:'SIG_HOLD',2:'GNDD'})
P(b,'U17','CMP','LM393',{5:'SIG_HOLD',6:'VREF',7:'SIG_K'},unit=2)
P(b,'R122','R','47K',{1:'SIG_K',2:'SIG_B'}); P(b,'R123','R','47K',{1:'+VL',2:'SIG_B'})
P(b,'Q4','PNP','MMBT3906',{1:'SIG_B',2:'+VL',3:'SIG_C'}); P(b,'C102','C','10n',{1:'SIG_B',2:'+VL'})   # E6
P(b,'R124','R','4K7',{1:'SIG_C',2:'SIG_A'})
P(b,'R125','R','47K',{1:'OL_K',2:'GATE_B'}); P(b,'Q5','PNP','MMBT3906',{1:'GATE_B',2:'+VL',3:'SIG_B'})
P(b,'D2','LED2','OL red / SIG green',{1:'OL_A',2:'GNDD',3:'SIG_A'})

b = block('PFL (pre-fade)  SW3: A-B = ON')
# K1 (gaps_proposal.md, signed off 2026-10-25): DC block in the PFL send. U3B's bias current leaves PRE 3-14 mV off
# ground, which the PFL key put on the PFL bus as a tick (up to 11.5 mV); 22K + 2.2u film: 3.3 Hz
P(b,'C96','C','2.2u film',{1:'PRE',2:'PFL_C'},fp=FILM_2U2)
P(b,'R32','R','22K',{1:'PFL_C',2:'PFL_S'})
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
P(b,'U2','OPA','OPA1612',{5:'GNDA',6:'U2B_O',7:'U2B_O'},unit=2)   # spare half, tied off (PAN1: pan L moved to U8B)
P(b,'C82','C','10p C0G',{1:'FPIN',2:'GNDA'},fp=C0G)   # not above 22p: it sits on U3B's output with the fader at top
P(b,'R19','R','4K7',{1:'FPOST',2:'U2A_N'}); P(b,'C14','C','100p C0G',{1:'FPOST',2:'U2A_N'})
P(b,'R38','R','2K2',{1:'U2A_N',2:'GNDA'})
P(b,'C15','C','100u NP 25V',{1:'FPOST',2:'POST'},fp=CAP_FP['220u']); P(b,'R35','R','47K',{1:'POST',2:'GNDA'})

b = block('AUX SENDS  PRE switch per pair (latched = pre); jumpers 1-2 = pre-fader after ON, 2-3 = pre-EQ.  SW13 DIR: aux 6 pot -> direct out')
# Q1 (design_review.md, 2026-10-25): the pre-fader taps come from MUTEOUT (after the J112 mute, before the fader), so ON
# mutes the pre sends and the direct out too; the pre-EQ jumper setting (HOUT) stays ahead of the mute
for jp,sw,n in (('JP2','SW8','12'),('JP3','SW9','34'),('JP4','SW10','56')):
    P(b,jp,'SJ3',f'Aux{n[0]}/{n[1]} pre source',{1:'MUTEOUT',3:'HOUT',2:f'PSRC{n}'})
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

b = block('PAN + PAN BUFFERS (AC-coupled outputs)')
# ALPS RK09L1240015: the stocked vertical dual 10K B with a centre detent (no Alpha one exists); M9 bushing, 6 mm D shaft
P(b,'RV8','POT2','Pan 10K lin dual CD',{1:'POST',3:'GNDA',2:'PANWL',4:'GNDA',6:'POST',5:'PANWR'},
  fp='Potentiometer_THT:Potentiometer_Alps_RK09L_Double_Vertical',mpn='ALPS RK09L1240015')
# PAN1 (pan_buffer_proposal.md): pan buffer L in U8B (it was the spare), beside the pan pot; U2B at the fader end is
# the spare now, so the pan L wiper no longer runs 165 mm to the fader end
P(b,'U8','OPA','OPA1612',{5:'PANWL',6:'PBL',7:'PBL'},unit=2); P(b,'C79','C','10p C0G',{1:'PANWL',2:'GNDA'},fp=C0G)
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
        if pt['key'] in ('C', 'CP') and not pt['mpn']: pt['mpn'] = CAP_MPN.get(pt['value'], '')
build(OUT, 'channel_strip', 'Channel strip - goa console',
      {1: 'Generated from channel_strip_schematic_spec.md v5.1', 2: 'Drawn by tools/strip_draw.py; labels join the blocks',
       3: 'A Delta Theatre input without the mic stage'},
      paper='auto', revision='5.1', pages=dict(paper='A4', folder='strip_sheets'), **strip_draw.SHEET)   # A4 sub-sheets
if os.environ.get('PILOT'):                     # only the drawn blocks, on a sheet of their own (layout review)
    build(os.environ['PILOT'], 'pilot', 'Channel strip - drawn blocks (pilot)', {1: 'tools/strip_draw.py', 2: ''},
          paper='auto', revision='5.1', only=lambda t: strip_draw.for_title(t) is not None, **strip_draw.SHEET)

# ---------------------------------------------------------------- jack board (its own PCB; same net names)
schgen.blocks.clear()
b = block('JACK BOARD  (3 x NJ6FD-V ~24 mm under the panel; 10-way IDC ribbon to CN3 on the main board)')
# G2 (ground_study.md): the balanced jacks' sleeves (line in, direct out) on CHASSIS, bonded through the plated
# standoff holes H1 / H2 to the panel, so cable-shield currents stay out of GNDA; the insert (single-ended) keeps GNDA.
# J1's normals short tip and ring to GNDA when nothing is plugged in (the 1M bias would hiss otherwise).
P(b,'J1','JACKSW','Line in TRS',{'T':'IN_T','R':'IN_R','S':'CHASSIS','TN':'GNDA','RN':'GNDA'},fp=JACK_V,mpn=JACK_V_MPN)
P(b,'C8','C','100p C0G',{1:'IN_T',2:'CHASSIS'},mpn='KEMET C0805C101J5GACTU'); P(b,'C9','C','100p C0G',{1:'IN_R',2:'CHASSIS'},mpn='KEMET C0805C101J5GACTU')   # RF shunt at the jack
P(b,'J2','JACKSW','Insert TRS switched',{'T':'SEND','RN':'SEND','R':'RET_RAW','TN':'NC','S':'GNDA'},fp=JACK_V,mpn=JACK_V_MPN)
P(b,'J5','JACKSW','Direct out TRS',{'T':'DO_T','R':'DO_R','S':'CHASSIS','TN':'NC','RN':'NC'},fp=JACK_V,mpn=JACK_V_MPN)
P(b,'H1','MHPAD','M3 standoff to panel',{1:'CHASSIS'}); P(b,'H2','MHPAD','M3 standoff to panel',{1:'CHASSIS'})
P(b,'CN5','LINK','Main board link 2x5',LINK,mpn=LINK_MPN)
P(b,'#FLG01','FLAG','PWR_FLAG',{1:'GNDA'})
build(JB_OUT, 'jack_board', 'Jack board - goa console channel strip (line in, insert, direct out)',
      {1: 'Generated by tools/gen.py together with channel_strip.kicad_sch (link pinout: LINK)',
       2: 'Spec: channel_strip_schematic_spec.md 16.4'}, paper='A4', revision='4.0')
