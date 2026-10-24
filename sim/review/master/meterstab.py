"""Tian loop gain of the meter-L TL072 units in a meter-only deck (master deck lines on ML_* nets), CRSB_L driven by
an ideal DC source (meter_dc). Cases: TL072 model x jumper x diode state; fix variants (follower on PK1, 220R)."""
import sys, re, json, numpy as np
from masterdeck import deck
from tian import ngspice, load, loopgain, margins, HERE
ST = ['U29A', 'U29B', 'U30A', 'U30B']
OUTN = {'U29A': 'ML_U1O', 'U29B': 'ML_X2', 'U30A': 'ML_U3O', 'U30B': 'ML_DET'}
KEEP = lambda n: n == '0' or n.startswith(('ML_', 'MTR_L', 'U29', 'U30')) or n in ('PVM', 'MVM', 'CRSB_L')
def apply_var(txt, var):
    for p in var.split('_'):
        if p == 'pk1': txt = txt.replace('RJP1 ML_PK ML_JSEL 0.01', 'RJP1 ML_PK1 ML_JSEL 0.01')
        elif p.startswith('r'): txt = re.sub(r'^(R\S+ ML_PK1 ML_PK) 1000\.0$', r'\g<1> ' + p[1:], txt, flags=re.M)
        elif p.startswith('cx'): pass
        elif p.startswith('cf'): txt += f'\nCFPK ML_U3O ML_N4 {p[2:]}\n'
        elif p.startswith('det'):
            txt = txt.replace('VTI_U30B U30B_ox ML_DET ', 'VTI_U30B U30B_ox ML_DETO ').replace('XU30B U30B_pp ML_DET ', 'XU30B U30B_pp ML_DETO ')
            txt += f'\nRISOD ML_DETO ML_DET {p[3:]}\n'
        elif p == 'bat':
            txt = txt.replace('DD25 ML_U3O ML_PK1 D1N4148', 'DD25 ML_U3O ML_PK1 DBAT').replace('DD26 ML_N4 ML_U3O D1N4148', 'DD26 ML_N4 ML_U3O DBAT')
            txt += '\n.model DBAT D(IS=2e-7 N=1.04 RS=2.5 CJO=10p BV=30)\n'
    return txt
def mdeck(cfg, ctl, var='asis'):
    d = deck(cfg, '')
    out = []; skip = False
    for line in d.splitlines():
        if line.startswith('.subckt LME49600M'): skip = True
        if skip:
            if line.startswith('.ends'): skip = False
            continue
        t = line.split()
        if not t or line.startswith(('*', '.')):
            if not line.startswith(('.options', '.end')) or line.startswith('.ends'): out.append(line)
            continue
        if t[0][0] == 'X': nodes = t[1:-1]
        elif t[0][0] in 'RCDVI' and len(t) >= 3: nodes = t[1:3]
        else: continue
        if all(KEEP(n) for n in nodes): out.append(line)
    txt = '\n'.join(out)
    txt = apply_var(txt, var)
    txt += f"\nVCRS CRSB_L 0 DC {cfg.get('meter_dc', 0)}\n"
    if cfg.get('attack_ma'): txt += f"IATK ML_PK 0 DC {cfg['attack_ma']*1e-3}\n"
    if cfg.get('pk_hold_ua'): txt += f"IPKH 0 ML_PK DC {cfg['pk_hold_ua']*1e-6}\n"
    txt += '.options itl1=500\n' + ctl + '\n.end'
    return txt
def ctl(tag):
    L = ['.control', 'set noaskquit', 'set wr_singlescale', 'set wr_vecnames']
    for s in ST:
        o = OUTN[s] if not (s == 'U30B' and '_det' in tag) else 'ML_DETO'; f = f'{HERE}/raw/{tag}_{s}'
        L += [f'alter @VTI_{s}[acmag] = 1', 'ac dec 40 10 300meg', f'wrdata {f}_v.txt v({s}_ox) v({o})',
              f'alter @VTI_{s}[acmag] = 0', 'destroy all', f'alter @ITI_{s}[acmag] = 1', 'ac dec 40 10 300meg',
              f'wrdata {f}_i.txt i(VTI_{s})', f'alter @ITI_{s}[acmag] = 0', 'destroy all']
    return '\n'.join(L + ['.endc'])
if __name__ == '__main__':
    TRIM = {'PK': 0.16, 'AV': 0.8}
    res = {}
    for var in (sys.argv[1].split(',') if len(sys.argv) > 1 else ('asis', 'pk1_r220', 'pk1_r1k')):
        for tl in ('old', 'H'):
            for jp in ('PK', 'AV'):
                if jp == 'AV' and var != 'asis': continue
                base = dict(tl=tl, jp={'JP1': jp}, pos={'RV7': TRIM[jp]})
                cases = {'idle': {}, 'pos': dict(meter_dc=0.5), 'neg': dict(meter_dc=-0.5)}
                if jp == 'PK': cases.update(attack1mA=dict(meter_dc=0.5, attack_ma=1.0), attack10uA=dict(meter_dc=0.5, attack_ma=0.01),
                                            hold=dict(pk_hold_ua=2.0), det47p=dict(meter_dc=0.5, loads={'ML_DET': 47e-12}))
                else: cases.update(det47p=dict(meter_dc=0.5, loads={'ML_DET': 47e-12}))
                for k, c in cases.items():
                    tag = f'ms_{var}_{tl}_{jp}_{k}'
                    out = ngspice(mdeck(dict(base, **c), ctl(tag), var), tag)
                    r = {}
                    for s in ST:
                        try:
                            f, T = loopgain(f'{HERE}/raw/{tag}_{s}_v.txt', f'{HERE}/raw/{tag}_{s}_i.txt'); r[s] = margins(f, T, 1e3)
                        except Exception as e: r[s] = {'err': str(e)[:80]}
                    res[tag] = r
                    print(f'{var:8s} {tl:3s} {jp} {k:10s}', '  '.join(f"{s}: pm {r[s].get('pm')} fc {r[s].get('fc')} pk {r[s].get('clpk')}@{r[s].get('fclpk')}" for s in ST), flush=True)
    json.dump(res, open(f'res/meterstab_{sys.argv[1] if len(sys.argv) > 1 else "base"}.json', 'w'), indent=1)
