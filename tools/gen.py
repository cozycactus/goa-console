"""Generate the channel-strip schematic from its netlist (the P(...) calls below).
Builder and part maps are in schgen.py."""
import sys
from schgen import block, P, build, FADER_FP, CAP_FP, SYM, FP

SYM.update({'CONN6': ('Connector_Generic', 'Conn_01x06'), 'CONN2': ('Connector_Generic', 'Conn_01x02')})
FP.update({'CONN6': 'Connector_PinSocket_2.54mm:PinSocket_1x06_P2.54mm_Vertical',
           'CONN2': 'Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical'})

OUT = sys.argv[1] if len(sys.argv) > 1 else 'channel_strip.kicad_sch'

# ---------------------------------------------------------------- netlist
b = block('POWER ENTRY, LOGIC SUPPLY, GROUNDS, DECOUPLING')
P(b,'R1','R','10R',{1:'+VBUS',2:'+VA'}); P(b,'C1','CP','220u 25V',{1:'+VA',2:'GNDA'})
P(b,'C2','C','100n',{1:'+VA',2:'GNDA'})
P(b,'R2','R','10R',{1:'-VBUS',2:'-VA'}); P(b,'C3','CP','220u 25V',{1:'GNDA',2:'-VA'})
P(b,'C4','C','100n',{1:'GNDA',2:'-VA'})
P(b,'R3','R','10R',{1:'+VBUS',2:'+VL'}); P(b,'C5','CP','47u 25V',{1:'+VL',2:'GNDD'},fp='Capacitor_THT:CP_Radial_D6.3mm_P2.50mm')
P(b,'R4','R','10R',{1:'-VBUS',2:'-VL'}); P(b,'C6','CP','47u 25V',{1:'GNDD',2:'-VL'},fp='Capacitor_THT:CP_Radial_D6.3mm_P2.50mm')
P(b,'NT1','NT','AGND-LGND star',{1:'GNDA',2:'GNDD'})
P(b,'CN4','TAB','Ground spade 6.3mm',{1:'GNDA'})
P(b,'R5','R','10R GND cancel',{1:'GNDA',2:'GCANCEL'})
for i,(ref,cp,cn) in enumerate([('U1','C20','C21'),('U2','C22','C23'),('U3','C24','C25')]):
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
P(b,'CN1','HDR','Bus 2x17',hdr)

b = block('LINE INPUT - ground-compensated differential receiver')
P(b,'J1','JACKSW','Line in TRS',{'T':'IN_T','R':'IN_R','S':'GNDA','TN':'NC','RN':'NC'})
P(b,'C8','C','100p C0G',{1:'IN_T',2:'GNDA'}); P(b,'C9','C','100p C0G',{1:'IN_R',2:'GNDA'})
P(b,'R10','R','1M',{1:'IN_T',2:'GNDA'})  # tip = hot, non-inverting
P(b,'R6','R','10K 0.1%',{1:'IN_R',2:'U1A_N'}); P(b,'R7','R','10K 0.1%',{1:'U1A_N',2:'RECV'})
P(b,'C7','C','33p C0G',{1:'U1A_N',2:'RECV'})
P(b,'R8','R','10K 0.1%',{1:'IN_T',2:'U1A_P'}); P(b,'R9','R','10K 0.1%',{1:'U1A_P',2:'GNDA'})
P(b,'U1','OPA','OPA1612',{3:'U1A_P',2:'U1A_N',1:'RECV'},unit=1)

b = block('INSERT (send = tip, return = ring, ring normalled to send) + post-insert buffer')
P(b,'R11','R','75R',{1:'RECV',2:'SEND'})
P(b,'J2','JACKSW','Insert TRS switched',{'T':'SEND','RN':'SEND','R':'RET_RAW','TN':'NC','S':'GNDA'})
P(b,'C10','C','47u NP 25V',{1:'RET_RAW',2:'RET'},fp=CAP_FP['47u']); P(b,'R12','R','47K',{1:'RET',2:'GNDA'})
P(b,'U1','OPA','OPA1612',{5:'RET',6:'BUF1',7:'BUF1'},unit=2)
P(b,'C11','C','220u NP 25V',{1:'BUF1',2:'PRE'},fp=CAP_FP['220u']); P(b,'R13','R','47K',{1:'PRE',2:'GNDA'})

b = block('OVERLOAD DETECTOR (~+18 dBu)')
P(b,'R39','R','1K',{1:'BUF1',2:'PKA'}); P(b,'D1','D','1N4148',{2:'PKA',1:'PK'})
P(b,'C12','C','1u',{1:'PK',2:'GNDA'}); P(b,'R14','R','470K',{1:'PK',2:'GNDA'})
P(b,'R40','R','10K',{1:'+VL',2:'VREF'}); P(b,'R41','R','10K',{1:'VREF',2:'GNDA'})
P(b,'U4','CMP','LM393',{2:'PK',3:'VREF',1:'OL_K'},unit=1)
P(b,'R15','R','1K',{1:'+VL',2:'OL_A'}); P(b,'D2','LED','OL red',{2:'OL_A',1:'OL_K'})
P(b,'U4','CMP','LM393',{5:'GNDD',6:'+VL',7:'NC'},unit=2)

b = block('PFL (pre-fade)  SW3: A-B = ON')
P(b,'R32','R','22K',{1:'PRE',2:'PFL_S'})
P(b,'SW3','SW','PFL',{2:'PFL_S',1:'PFL',3:'GNDA'},unit=1)
P(b,'SW3','SW','PFL',{5:'+VL',4:'PFL_ON',6:'NC'},unit=2)
P(b,'R33','R','100K',{1:'PFL_ON',2:'PFLDET'})
P(b,'R34','R','4K7',{1:'PFL_ON',2:'PFL_LA'}); P(b,'D3','LED','PFL red',{2:'PFL_LA',1:'GNDD'})

b = block('SOFT MUTE (2x J112 shunt, ~20 ms ramp)  SW4: A-B = MUTE')
P(b,'R16','R','4K7',{1:'PRE',2:'M1'}); P(b,'Q1','JFET','J112',{1:'M1',2:'GNDA',3:'MGATE'})
P(b,'R17','R','4K7',{1:'M1',2:'M2'}); P(b,'Q2','JFET','J112',{1:'M2',2:'GNDA',3:'MGATE'})
P(b,'U3','OPA','OPA1612',{5:'M2',6:'MUTEOUT',7:'MUTEOUT'},unit=2)
P(b,'SW4','SW','MUTE',{2:'MSW',1:'GNDD',3:'-VL'},unit=1)
P(b,'R42','R','220K',{1:'MSW',2:'MGATE'}); P(b,'C28','C','100n',{1:'MGATE',2:'GNDA'})
P(b,'SW4','SW','MUTE',{5:'+VL',4:'MUTE_ON',6:'NC'},unit=2)
P(b,'R43','R','4K7',{1:'MUTE_ON',2:'MUTE_LA'}); P(b,'D4','LED','MUTE amber',{2:'MUTE_LA',1:'GNDD'})

b = block('FADER + POST-AMP (+10 dB; omit R38 for unity)  JP1 = VCA bypass')
P(b,'RV1','POT','Fader 10K log 100mm',{1:'GNDA',3:'MUTEOUT',2:'WIPER'},fp=FADER_FP,mpn='Bourns PTB0143-2010BPA103')
P(b,'C13','C','2.2u',{1:'WIPER',2:'VCAIN'},fp=CAP_FP['2.2u'])
P(b,'JP1','SJ2','VCA bypass',{1:'VCAIN',2:'FPIN'}); P(b,'R18','R','100K',{1:'FPIN',2:'GNDA'})
# VCA module option (spec 7.1): SSI2162 + I/V + inverter on a plug-in module; JP1 bridged when not fitted
P(b,'J3','CONN6','VCA module socket',{1:'VCAIN',2:'FPIN',3:'VCA_CTRL',4:'+VA',5:'GNDA',6:'-VA'},dnp=True)
P(b,'J4','CONN2','VCA control in',{1:'VCA_CTRL',2:'GNDA'},dnp=True); P(b,'R44','R','100K',{1:'VCA_CTRL',2:'GNDA'},dnp=True)
P(b,'U2','OPA','OPA1612',{3:'FPIN',2:'U2A_N',1:'FPOST'},unit=1)
P(b,'R19','R','4K7',{1:'FPOST',2:'U2A_N'}); P(b,'C14','C','100p C0G',{1:'FPOST',2:'U2A_N'})
P(b,'R38','R','2K2',{1:'U2A_N',2:'GNDA'})
P(b,'C15','C','220u NP 25V',{1:'FPOST',2:'POST'},fp=CAP_FP['220u']); P(b,'R35','R','47K',{1:'POST',2:'GNDA'})

b = block('AUX SENDS  (JP2: 1-2 = PRE;  JP3, JP4: 1-2 = POST)')
P(b,'JP2','SJ3','Aux1/2 source',{1:'PRE',3:'POST',2:'SRC12'})
P(b,'JP3','SJ3','Aux3/4 source',{1:'POST',3:'PRE',2:'SRC34'})
P(b,'JP4','SJ3','Aux5/6 source',{1:'POST',3:'PRE',2:'SRC56'})
for n,(rv,r,src) in enumerate([('RV2','R20','SRC12'),('RV3','R21','SRC12'),('RV4','R22','SRC34'),
                              ('RV5','R23','SRC34'),('RV6','R24','SRC56'),('RV7','R25','SRC56')],1):
    P(b,rv,'POT',f'Aux{n} 10K log',{1:'GNDA',3:src,2:f'A{n}W'})   # A taper: pin 1 = ground end
    P(b,r,'R','22K',{1:f'A{n}W',2:f'AUX{n}'})

b = block('PAN + PAN BUFFERS (AC-coupled outputs)')
P(b,'RV8','POT2','Pan 10K dual',{1:'POST',3:'GNDA',2:'PANWL',4:'GNDA',6:'POST',5:'PANWR'})
P(b,'U2','OPA','OPA1612',{5:'PANWL',6:'PBL',7:'PBL'},unit=2)
P(b,'U3','OPA','OPA1612',{3:'PANWR',2:'PBR',1:'PBR'},unit=1)
P(b,'C16','C','220u NP 25V',{1:'PBL',2:'PANL'},fp=CAP_FP['220u']); P(b,'R36','R','47K',{1:'PANL',2:'GNDA'})
P(b,'C17','C','220u NP 25V',{1:'PBR',2:'PANR'},fp=CAP_FP['220u']); P(b,'R37','R','47K',{1:'PANR',2:'GNDA'})

b = block('ROUTING MATRIX  (A-B = assigned; off grounds the resistor)  4K7 summing')
for sw,rl,rr,bl,br,nm in [('SW5','R26','R27','MIXL','MIXR','L-R'),('SW6','R28','R29','SUB1','SUB2','1-2'),
                          ('SW7','R30','R31','SUB3','SUB4','3-4')]:
    P(b,rl,'R','4K7 1%',{1:'PANL',2:f'RT_{rl}'}); P(b,rr,'R','4K7 1%',{1:'PANR',2:f'RT_{rr}'})
    P(b,sw,'SW',f'Assign {nm}',{2:f'RT_{rl}',1:bl,3:'GNDA'},unit=1)
    P(b,sw,'SW',f'Assign {nm}',{5:f'RT_{rr}',4:br,6:'GNDA'},unit=2)

build(OUT, 'channel_strip', 'Channel strip - goa console (Delta-style motherloom)',
      {1: 'Generated from channel_strip_schematic_spec.md v3.0', 2: 'Nets joined by labels; tidy wiring in Eeschema as needed'})
