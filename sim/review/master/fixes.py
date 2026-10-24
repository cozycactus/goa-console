"""Candidate fix sets (parts added to the master deck)."""
PH = dict(omit=['C136', 'C142'], extra=[('CFX1', 'PH_DRVL', 'PH_NL', '100p'), ('CFX2', 'PH_DRVR', 'PH_NR', '100p')])
INS = ['MST_L_FIN', 'MST_R_FIN', 'A5_LIN', 'A6_LIN', 'PFL_FIN', 'CR_FINL', 'CR_FINR', 'PH_INL', 'PH_INR']
def incap(v, nets=INS): return [(f'CIN_{n}', n, '0', v) for n in nets]
def iso(r):
    return dict(pinmove={('U21', '1'): 'CRSB_LO', ('U21', '2'): 'CRSB_LO', ('U21', '6'): 'CRSB_RO', ('U21', '7'): 'CRSB_RO'},
                extra=[('RISO_L', 'CRSB_LO', 'CRSB_L', r), ('RISO_R', 'CRSB_RO', 'CRSB_R', r)])
def merge(*ds):
    out = {}
    for d in ds:
        for k, v in d.items():
            if k in ('extra', 'omit'): out[k] = out.get(k, []) + list(v)
            elif k in ('pinmove', 'loads'): out[k] = {**out.get(k, {}), **v}
            else: out[k] = v
    return out
FIXES = {
 'none': {},
 'ph': PH,
 'in10': merge(PH, dict(extra=incap('10p'))),
 'in22': merge(PH, dict(extra=incap('22p'))),
 'in22_iso47': merge(PH, dict(extra=incap('22p')), iso('47')),
 'in22_iso100': merge(PH, dict(extra=incap('22p')), iso('100')),
 'in10_iso47': merge(PH, dict(extra=incap('10p')), iso('47')),
}
def iso_solo(r): return dict(pinmove={('U19', '1'): 'PFL_SIGO', ('U19', '2'): 'PFL_SIGO'}, extra=[('RISO_P', 'PFL_SIGO', 'PFL_SIG', r)])
def iso_post(r): return dict(pinmove={('C31', '1'): 'MST_L_FX', ('C34', '1'): 'MST_R_FX'},
                             extra=[('RISO_FL', 'MST_L_FPOST', 'MST_L_FX', r), ('RISO_FR', 'MST_R_FPOST', 'MST_R_FX', r)])
INS22 = [n for n in INS if n not in ('MST_L_FIN', 'MST_R_FIN')]
FIXES.update({
 'B1': merge(PH, dict(extra=incap('22p')), iso('47')),
 'B2': merge(PH, dict(extra=incap('22p')), iso('47'), iso_solo('100'), iso_post('47')),
 'B3': merge(PH, dict(extra=incap('22p', INS22) + incap('47p', ['MST_L_FIN', 'MST_R_FIN'])), iso('47'), iso_solo('100')),
 'B4': merge(PH, dict(extra=incap('22p')), iso('100'), iso_solo('100'), iso_post('47')),
})
INS10 = ['MST_L_FIN', 'MST_R_FIN']
FIXES.update({
 'B5': merge(PH, dict(extra=incap('22p', INS22) + incap('10p', INS10)), iso('47'), iso_solo('100'), iso_post('47')),
 'B6': merge(PH, dict(extra=incap('22p', INS22) + incap('10p', INS10)), iso('100'), iso_solo('100'), iso_post('47')),
})
IN_CRS = ['CR_FINL', 'CR_FINR', 'PH_INL', 'PH_INR']
INS_B8 = [n for n in INS22 if n not in IN_CRS]
FIXES.update({
 'B7': merge(PH, dict(extra=incap('22p', INS22) + incap('10p', INS10)), iso('220'), iso_solo('100'), iso_post('47')),
 'B8': merge(PH, dict(extra=incap('22p', INS_B8) + incap('10p', INS10 + IN_CRS)), iso('100'), iso_solo('100'), iso_post('47')),
 'B9': merge(PH, dict(extra=incap('22p', INS_B8) + incap('10p', INS10 + IN_CRS)), iso('150'), iso_solo('100'), iso_post('47')),
})

# ---- merged set (both boards share post_amp / level_buffer / insert): B6 + insert return 1K + 100p (strip T8) and a
# 75R build-out between the insert return buffer and its 220u
INSM = dict(pinmove={('U2', '5'): 'MIX_L_RETIN', ('U4', '3'): 'MIX_R_RETIN', ('C17', '1'): 'MIX_L_RBO', ('C26', '1'): 'MIX_R_RBO'},
            extra=[('RIN_L', 'MIX_L_RET', 'MIX_L_RETIN', '1k'), ('CINR_L', 'MIX_L_RETIN', '0', '100p'),
                   ('RIN_R', 'MIX_R_RET', 'MIX_R_RETIN', '1k'), ('CINR_R', 'MIX_R_RETIN', '0', '100p'),
                   ('RBO_L', 'MIX_L_RBUF', 'MIX_L_RBO', '75'), ('RBO_R', 'MIX_R_RBUF', 'MIX_R_RBO', '75')])
INS_A = ['A5_LIN', 'A6_LIN']
INS_OTHER = [n for n in INS22 if n not in INS_A]
FIXES.update({     # MG = the recommended set (master_group_review.md MG2-MG7); MG22 has 22p in level_buffer() instead of 10p
 'MG': merge(PH, dict(extra=incap('22p', INS_OTHER) + incap('10p', INS10 + INS_A)), iso('100'), iso_solo('100'), iso_post('47'), INSM),
 'MG22': merge(PH, dict(extra=incap('22p', INS22) + incap('10p', INS10)), iso('100'), iso_solo('100'), iso_post('47'), INSM),
})
