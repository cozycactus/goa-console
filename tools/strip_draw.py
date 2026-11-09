"""Drawn blocks of the channel-strip schematic (schdraw.Drawing). One function per block, keyed by the start of its
title in gen.py. Grid units (2.54 mm), y down; op-amps mirrored 'x' so the - input is on top, as on the Delta sheets."""
import frags


def receiver(d):
    """CN3 link, U16 input followers (1M bias, 220R in, 100R build-out), Ø switch (SW15), U1A ground-compensated receiver."""
    d.shift(0, 3)
    frags.header(d, 'CN3', 14, 26)
    for port, rs, rb, (u, n), ro, cin, y in (('IN_T', 'R110', 'R10', ('U16', 1), 'R113', 'C94', 0),
                                             ('IN_R', 'R111', 'R112', ('U16', 2), 'R114', 'C95', 14)):
        d.at(rs, 6.5, y, rot=90, text='U'); d.at(rb, 3.5, y + 1.5, text='L'); d.at(cin, 9, y + 1.5, text='L')
        d.w((1, y), (rs, 1)); d.port(port, (1, y))
        p = follower(d, (u, n), 14, y + 1); d.w((rs, 2), (u, p[0]))
        d.at(ro, 21.5, y + 1, rot=90, text='U'); d.w((18, y + 1), (ro, 1))
    S = 16                                       # the receiver, right of the followers
    d.at('SW15', S + 16, 4, mirror='y', unit=1, text='U'); d.at('SW15', S + 16, 12, mirror='y', unit=2)
    d.w(('SW15', 3), (S + 11, 5), (S + 11, 11), ('SW15', 4)); d.w(('R113', 2), (S + 11, 1), (S + 11, 5))
    d.w(('SW15', 1), (S + 9, 3), (S + 9, 13), ('SW15', 6)); d.w(('R114', 2), (S + 9, 15), (S + 9, 13))
    d.at('U1', S + 30, 8, mirror='x', unit=1)
    d.at('R6', S + 22.5, 4, rot=90); d.w(('SW15', 2), ('R6', 1)); d.w(('R6', 2), (S + 25, 4))
    d.w((S + 25, -1), (S + 25, 7), ('U1', 2))
    d.at('R7', S + 30.5, 3, rot=90); d.w((S + 25, 3), ('R7', 1)); d.w(('R7', 2), (S + 35, 3))
    d.at('C7', S + 30.5, -1, rot=90); d.w((S + 25, -1), ('C7', 1)); d.w(('C7', 2), (S + 35, -1), (S + 35, 8))
    d.w(('U1', 1), (S + 38, 8)); d.port('RECV', (S + 38, 8), 'R')
    d.at('R8', S + 22.5, 12, rot=90); d.w(('SW15', 5), ('R8', 1)); d.w(('R8', 2), (S + 27, 12), ('U1', 3))
    d.at('R9', S + 27, 13.5); d.at('C78', S + 33, 13.5); d.w((S + 27, 12), ('C78', 1))


def link_clamps(d):
    """CS4: a BAV199 per jack signal at CN3 (pin 3 to the signal, pin 2 to +VA, pin 1 to -VA)."""
    d.shift(0, 4)
    for k, (dd, net) in enumerate((('D18', 'IN_T'), ('D19', 'IN_R'), ('D20', 'RET_RAW'), ('D21', 'SEND'), ('D22', 'DO_T'), ('D23', 'DO_R'))):
        x = 2 + 14 * k
        d.at(dd, x + 3, 2)
        d.w((dd, 1), (x, 0)); d.port('-VA', (x, 0), 'U')
        d.w((dd, 2), (x + 6, 0)); d.port('+VA', (x + 6, 0), 'U')
        d.w((dd, 3), (x + 3, 6)); d.port(net, (x + 3, 6), 'D')


def gain(d):
    """U1B inverting gain stage: RV9 between the two 2K2s, wiper to the - input; C38 / C91 couplers to HIN."""
    d.w((1, 4), (3, 4)); d.port('RECV', (1, 4))
    d.at('R45', 4.5, 4, rot=90); d.w((3, 4), ('R45', 1))
    d.at('RV9', 9.5, 4, rot=270); d.w(('R45', 2), ('RV9', 3))
    d.at('R46', 13.5, 4, rot=90, text='U'); d.w(('RV9', 1), ('R46', 1))
    d.at('U1', 17, 10, mirror='x', unit=2)
    d.w(('R46', 2), (20, 4), (20, 10)); d.w(('U1', 7), (23, 10))
    d.w(('RV9', 2), (9.5, 9), ('U1', 6))
    d.at('C37', 16.5, 7, rot=270, text='U'); d.w((9.5, 7), ('C37', 2)); d.w(('C37', 1), (20, 7))
    d.at('R142', 15.5, 15, rot=90, text='D'); d.w((11.5, 9), (11.5, 15), ('R142', 1)); d.w(('R142', 2), (20, 15), (20, 10))   # RV4
    d.w(('U1', 5), (13, 11), (13, 12)); d.gnd((13, 12))
    d.at('C38', 24.5, 10, rot=90, text='U'); d.at('C91', 24.5, 13, rot=90, text='D')
    d.w((23, 10), ('C91', 1)); d.w(('C91', 2), (26, 10))
    d.w(('C38', 2), (31, 10)); d.port('HIN', (31, 10), 'R')
    d.at('R47', 28, 11.5)


SHEET = dict(col_height=520, last=('POWER ENTRY', 'MOTHERLOOM'))   # columns on one sheet, signal order
PP = {1: (3, 2, 1), 2: (5, 6, 7)}             # op-amp / comparator unit: (+, -, out) pins


def svf_core(d, ui1, ui2, rb1, ci1, rb2, ci2, pot, r0a, r0b, rta, rtb, lp_end, bp_end, hp_end=27.5):
    """State-variable integrators and their tuning: the summer sits at grid 16 with its output (HP) running down x = 20
    to y = 22. Integrator 1 (HP -> BP) at 33, integrator 2 (BP -> LP) at 47, both with the cap over the top; the dual
    pot under them, wipers up into the integrators through rb1 / rb2, gang ends down to r0a / r0b. LP returns along the
    top to lp_end, BP along the bottom (y = 24) to bp_end."""
    (u1, n1), (u2, n2) = ui1, ui2; p1, p2 = PP[n1], PP[n2]
    d.at(u1, 33, 8, mirror='x', unit=n1); d.at(u2, 47, 8, mirror='x', unit=n2)
    d.at(rb1, 27.5, 7, rot=90); d.w((rb1, 2), (u1, p1[1]))
    d.at(ci1, 32.5, 4, rot=270); d.w((rb1, 2), (29, 4), (ci1, 2)); d.w((ci1, 1), (37, 4))
    d.w((u1, p1[2]), (37, 8)); d.w((u1, p1[0]), (29, 9), (29, 10)); d.gnd((29, 10))
    d.at(rb2, 41.5, 7, rot=90); d.w((rb2, 2), (u2, p2[1]))
    d.at(ci2, 46.5, 4, rot=270); d.w((rb2, 2), (43, 4), (ci2, 2)); d.w((ci2, 1), (51, 4), (51, 8))
    d.w((u2, p2[2]), (51, 8)); d.w((u2, p2[0]), (43, 9), (43, 10)); d.gnd((43, 10))
    d.w((51, 4), (51, -3), 'h', lp_end)
    d.w((37, 4), (37, 24), 'h', bp_end)
    d.at(pot, 28.5, 15, text='W')                   # value left of the summer's output line
    d.w((pot, 2), (rb1, 1))
    d.w((pot, 5), (31, 12), (40, 12), (rb2, 1))
    d.w((pot, 1), (24.5, 17)); d.at(r0a, 24.5, 18.5, text='L')
    d.w((pot, 4), (29.5, 17)); d.at(r0b, 29.5, 18.5)
    d.w((pot, 3), (27.5, 22)); d.w((20, 22), (hp_end, 22))
    d.w((pot, 6), (37, 16))
    d.at(rta, 21.5, 11, rot=90); d.w((rta, 2), (26, 11))
    d.at(rtb, 38.5, 10, rot=90)
    d.note('INTEGRATOR 1', (30, 0), 1.27); d.note('INTEGRATOR 2', (44, 0), 1.27)


def summer_top(d, u, rfb, cfb, rlp):
    """Summer op-amp at grid 16, - input on top with rfb // cfb, LP into the - node through rlp from the top."""
    (r, n) = u; p = PP[n]
    d.at(r, 16, 8, mirror='x', unit=n)
    d.w((12, 0), (12, 7), (r, p[1]))
    d.at(rfb, 15.5, 4, rot=270); d.w((12, 4), (rfb, 2)); d.w((rfb, 1), (20, 4))
    d.at(cfb, 15.5, 0, rot=270); d.w((12, 0), (cfb, 2)); d.w((cfb, 1), (20, 0))
    d.w((20, 0), (20, 22)); d.w((r, p[2]), (20, 8))
    d.at(rlp, 10, -1.5, text='L'); d.w((rlp, 2), (12, 0))
    d.note('SUMMER', (13, -5), 1.27)
    return p


def hpf(d):
    """Sweepable HPF: U5A summer, U15A / U15B integrators, RV16 dual as dividers into their virtual earths."""
    d.shift(0, 5)
    p = summer_top(d, ('U5', 1), 'R103', 'C86', 'R102')
    d.at('R100', -2, 9, rot=90); d.w((-6, 9), ('R100', 1)); d.port('HIN', (-6, 9)); d.w(('R100', 2), ('U5', p[0]))
    d.at('C85', 4.5, 10.5, text='L'); d.at('R101', 11.5, 10.5, rot=180, text='L')
    svf_core(d, ('U15', 1), ('U15', 2), 'R106', 'C87', 'R109', 'C88', 'RV16', 'R104', 'R107', 'R105', 'R108',
             ('R102', 1), ('R101', 1), hp_end=54)
    d.at('SW11', 56, 23, mirror='y', unit=1); d.at('SW11', 56, 29, mirror='y', unit=2)
    d.w(('SW11', 3), (52, 24)); d.port('HIN', (52, 24))
    d.w(('SW11', 2), (60, 23)); d.port('HOUT', (60, 23), 'R')
    d.note('RV16 HPF FREQ: A10K dual, CW = higher', (21, 27), 1.27)


def inv_stage(d, X, Y, u, rin, rf, cin=None, cf=None, pot=None, pot_in=1):
    """Inverting EQ stage, op-amp at (X+10, Y), - input on top: rin (// cin) from the input line x = X+1, rf (// cf)
    over the top to the output line x = X+14. pot: the band's gain pot under the stage between the two lines, wiper
    down; pot_in = the pot pin on the input side (1 or 3). Returns the op-amp's (+, -, out) pins."""
    (r, n) = u; p = PP[n]
    d.at(r, X + 10, Y, mirror='x', unit=n)
    d.at(rin, X + 2.5, Y - 1, rot=90, text='D' if cin else None)
    if cin:
        d.at(cin, X + 2.5, Y - 3, rot=90, text='U'); d.w((cin, 1), (rin, 1)); d.w((cin, 2), (X + 5, Y - 3))
    d.w((rin, 2), (r, p[1]))
    top = Y - 7 if cf else Y - 5
    d.w((X + 5, top), (X + 5, Y - 1))
    d.at(rf, X + 9.5, Y - 5, rot=270, text='D' if cf else None); d.w((X + 5, Y - 5), (rf, 2)); d.w((rf, 1), (X + 14, Y - 5))
    if cf:
        d.at(cf, X + 9.5, Y - 7, rot=270, text='U'); d.w((X + 5, Y - 7), (cf, 2)); d.w((cf, 1), (X + 14, Y - 7))
    low = Y + 10 if pot else Y
    d.w((X + 14, top), (X + 14, low)); d.w((r, p[2]), (X + 14, Y))
    d.w((X + 1, Y - 3 if cin else Y - 1), (X + 1, low))
    if pot:
        if pot_in == 1: d.at(pot, X + 7.5, Y + 10, rot=90, mirror='x')
        else: d.at(pot, X + 7.5, Y + 10, rot=270)
        d.w((X + 1, Y + 10), (pot, pot_in)); d.w((pot, 4 - pot_in), (X + 14, Y + 10))
    return p


def eq(d):
    """The Delta EQ: HF shelf (U5B), HI-MID (U6A), LO-MID (U6B), LF (U7A), four inverting stages in a row."""
    d.shift(0, 9); Y = 8
    # HF: shelf network from the wiper into the virtual earth
    p = inv_stage(d, 0, Y, ('U5', 2), 'R50', 'R51', cf='C41', pot='RV10', pot_in=3)
    d.textside[('RV10', 1)] = d.textside['RV10'] = 'R'   # texts run right, clear of R53's line
    d.w((-3, Y - 1), (1, Y - 1)); d.port('EQIN', (-3, Y - 1))
    d.w(('U5', p[0]), (7, Y + 2)); d.gnd((7, Y + 2))
    d.w((5, Y - 1), (5, Y + 13)); d.at('R53', 5, Y + 14.5, rot=180, text='L')
    d.at('C43', 6.5, Y + 16, rot=270, text='D'); d.at('C42', 11.5, Y + 16, rot=270, text='U')
    d.w(('C43', 1), ('C42', 2)); d.at('R52', 9, Y + 17.5)
    d.w(('RV10', 2), (7.5, Y + 13), (13, Y + 13), ('C42', 1))
    # HI-MID and LO-MID: + input from the KHN band-pass, gain pot between input and output
    for X, u, rin, rf, cin, cf, pot, bp in ((18, ('U6', 1), 'R54', 'R55', 'C69', 'C70', 'RV11', 'EQ_MP'),
                                            (36, ('U6', 2), 'R58', 'R59', 'C71', 'C72', 'RV13', 'EQ_LP')):
        p = inv_stage(d, X, Y, u, rin, rf, cin, cf, pot)
        d.w((u[0], p[0]), (X + 7, Y + 3)); d.port(bp, (X + 7, Y + 3), 'D')
        d.w((pot, 2), (X + 7.5, Y + 13)); d.port('EQ_WHM' if pot == 'RV11' else 'EQ_WLM', (X + 7.5, Y + 13), 'D')
        d.w((X - 4, Y), (X + 1, Y))                    # previous stage's output
    # LF: the + input network (RV15 bridge, 1K5 + 2.2u into 100n // 5K1), joined by its label
    p = inv_stage(d, 54, Y, ('U7', 1), 'R66', 'R67', cf='C73')
    d.w((50, Y), (55, Y)); d.w((55, Y), (55, Y + 10)); d.w((68, Y), (68, Y + 10))
    d.w(('U7', p[0]), (61, Y + 3)); d.port('EQ_FP', (61, Y + 3), 'D')
    d.at('RV15', 62, Y + 10, rot=90, mirror='x')
    d.at('R62', 57.5, Y + 10, rot=90); d.w((55, Y + 10), ('R62', 1)); d.w(('R62', 2), ('RV15', 1))
    d.at('R63', 65.5, Y + 10, rot=90); d.w(('RV15', 3), ('R63', 1)); d.w(('R63', 2), (68, Y + 10))
    d.at('C48', 62, Y + 19, rot=90, text='D'); d.w(('RV15', 1), ('C48', 1)); d.w(('RV15', 3), ('C48', 2))
    d.at('R64', 66.5, Y + 13, rot=90); d.w(('RV15', 2), (62, Y + 13), ('R64', 1))
    d.at('C49', 69.5, Y + 13, rot=90, text='U'); d.w(('R64', 2), ('C49', 1))
    d.w(('C49', 2), (77, Y + 13)); d.port('EQ_FP', (77, Y + 13), 'R')
    d.w((72, Y + 13), (72, Y + 14)); d.at('C50', 72, Y + 15.5, text='L'); d.at('R65', 75, Y + 14.5)
    d.w((68, Y), (71, Y)); d.port('EQ_O6', (71, Y), 'R')
    for X, nm in ((0, 'HF'), (18, 'HI-MID'), (36, 'LO-MID'), (54, 'LF')): d.note(nm, (X + 1, -2), 1.5)


KHN_BANDS = (('HI-MID', 'EQ_WHM', 'EQ_MP', ('U12', 1), ('U12', 2), ('U13', 1),
              ('R81', 'R82', 'R83', 'R84', 'R85', 'R86', 'R87', 'R88', 'R89'), 'RV12', 'C44', 'C45', 'R56', 'R57', ('C74', 'C75')),
             ('LO-MID', 'EQ_WLM', 'EQ_LP', ('U13', 2), ('U14', 1), ('U14', 2),
              ('R90', 'R91', 'R92', 'R93', 'R94', 'R95', 'R96', 'R97', 'R98'), 'RV14', 'C46', 'C47', 'R60', 'R61', ('C76', 'C77')))


def khn_band(k):
    """Mid-band tuning, one band: a KHN band-pass (summer, two integrators, A10K dual), BP out to U6's + input."""
    def draw(d):
        nm, wip, bp, sm_u, ui1, ui2, rs, pot, ci1, ci2, rb1, rb2, cs = KHN_BANDS[k]
        d.shift(0, 9 if k == 0 else 46)
        rin, rlp, rfb, r4, r5, r0a, r0b, rta, rtb = rs
        p = summer_top(d, sm_u, rfb, cs[0], rlp)
        d.at(rin, 9.5, 6, rot=90); d.w((5, 6), (rin, 1)); d.port(wip, (5, 6)); d.w((rin, 2), (12, 6))
        d.w((1, 9), (sm_u[0], p[0]))
        d.at(cs[1], 1, 10.5, text='L'); d.at(r5, 6.5, 10.5, text='L'); d.at(r4, 11.5, 10.5, rot=180, text='L')
        svf_core(d, ui1, ui2, rb1, ci1, rb2, ci2, pot, r0a, r0b, rta, rtb, (rlp, 1), (r4, 1))
        d.w((37, 24), (41, 24)); d.port(bp, (41, 24), 'R')
        d.note(f'{nm} BAND-PASS (KHN), {pot} {nm} FREQ: A10K dual, CW = higher', (0, -9), 1.5)
        d.shift(0, -9 if k == 0 else -46)
    return draw


def led_chain(d, sw, X, Y, rled, dled, src='+VL', mirror=None):
    """Switch pole B (common = src) -> rled -> LED -> GNDD, switch at (X, Y), pole B pins 5 / 4 / 6."""
    d.at(sw, X, Y, unit=2)
    d.w((sw, 5), (X - 4, Y)); d.port(src, (X - 4, Y))
    d.at(rled, X + 4.5, Y - 1, rot=90); d.w((sw, 4), (rled, 1))
    d.at(dled, X + 8.5, Y - 1, rot=180); d.w((rled, 2), (dled, 2))
    d.w((dled, 1), (X + 11, Y - 1), (X + 11, Y)); d.gnd((X + 11, Y), 'GNDD')


def follower(d, u, X, Y):
    """Unity follower, + on top: op-amp at (X, Y), feedback looped under it. Returns (+, out) pins."""
    (r, n) = u; p = PP[n]
    d.at(r, X, Y, unit=n)
    d.w((r, p[2]), (X + 4, Y), (X + 4, Y + 3), (X - 4, Y + 3), (X - 4, Y + 1), (r, p[1]))
    return p


def eq_in(d):
    d.shift(0, 3)
    d.at('SW12', 6, 4, mirror='y', unit=1)
    d.w(('SW12', 1), (1, 3)); d.port('EQ_O6', (1, 3)); d.w(('SW12', 3), (1, 5)); d.port('EQIN', (1, 5))
    d.at('C51', 10.5, 4, rot=90, text='U'); d.w(('SW12', 2), ('C51', 1))
    d.w(('C51', 2), (17, 4)); d.port('EQOUT', (17, 4), 'R'); d.at('R68', 14, 5.5)
    led_chain(d, 'SW12', 32, 4, 'R69', 'D5')


def insert(d):
    d.shift(0, 3)
    d.at('R11', 3.5, 0, rot=90); d.w((0, 0), ('R11', 1)); d.port('INS_SRC', (0, 0))
    d.w(('R11', 2), (8, 0)); d.port('SEND', (8, 0), 'R')
    d.at('C10', 3.5, 7, rot=90, text='U'); d.w((0, 7), ('C10', 1)); d.port('RET_RAW', (0, 7))
    d.w((6, 7), (6, 8)); d.at('R12', 6, 9.5, text='L'); d.at('R99', 9.5, 7, rot=90, text='U'); d.w(('C10', 2), ('R99', 1))
    d.at('C84', 12, 8.5, text='L')
    p = follower(d, ('U7', 2), 17, 8); d.w(('R99', 2), ('U7', p[0]))
    d.w((21, 8), (24, 8)); d.port('BUF1', (24, 8), 'R')
    d.at('C11', 3.5, 15, rot=90, text='U'); d.w((0, 15), ('C11', 1)); d.port('PRESRC', (0, 15))
    d.w(('C11', 2), (9, 15)); d.port('PRE', (9, 15), 'R'); d.at('R13', 7, 16.5)


def overload(d):
    d.shift(0, 6)
    d.at('R39', 3.5, 4, rot=90); d.w((0, 4), ('R39', 1)); d.port('PRESRC', (0, 4))
    # CS1: D1 is a BAV99 (pin 3 the middle): the top diode charges PK, the bottom one pulls OL_NN down
    d.at('D1', 6, 1); d.w(('R39', 2), (6, 4), ('D1', 3)); d.w(('D1', 1), (3, -1)); d.port('OL_NN', (3, -1), 'U')
    d.at('U4', 21, 5, mirror='x', unit=1)
    d.w(('D1', 2), (9, 4), ('U4', 2)); d.port('PK', (13, 4), 'U')
    d.at('C12', 11, 5.5, text='L'); d.at('R14', 15, 5.5, text='L')
    d.w(('U4', 3), (16, 6), (16, 9)); d.at('R41', 16, 10.5)
    d.at('R40', 12.5, 9, rot=90); d.w((8, 9), ('R40', 1)); d.port('+VL', (8, 9)); d.w(('R40', 2), (16, 9))
    d.at('C100', 20, 10.5, text='R'); d.w((16, 9), (20, 9))                                      # P2
    # hold stage (K3): U4A discharges OL_HOLD (R115 to +VL, C97 to GNDD); U4B lights D2 while it is below VREF
    d.at('U4', 40, 6, unit=2)
    d.at('R126', 25.5, 5, rot=90); d.w(('U4', 1), ('R126', 1)); d.w(('R126', 2), (37, 5)); d.w((37, 5), ('U4', 5))   # P1
    d.at('R115', 28, 3.5, text='R'); d.w(('R115', 1), (28, 0)); d.port('+VL', (28, 0), 'U')
    d.at('C97', 31, 6.5, text='L'); d.gnd(('C97', 2), 'GNDD'); d.port('OL_HOLD', (34, 5), 'U')
    d.w((15, 9), (15, 14), (35, 14), (35, 7), ('U4', 6))          # VREF to U4B's - input, under the hold network
    # MET1: U4B drives the red half of the bicolour D2 through the PNP Q3 (R116 base, R117 pull-up, R15 to the anode)
    d.w(('U4', 7), (46, 6)); d.at('R116', 49.5, 6, rot=90); d.w((46, 6), ('R116', 1))
    d.at('Q3', 56, 6, mirror='x'); d.w(('R116', 2), ('Q3', 1))                  # emitter up to +VL, collector down
    d.at('R117', 53, 2.5); d.w(('R117', 2), (53, 6)); d.w(('R117', 1), (53, 0)); d.port('+VL', (53, 0), 'U')
    d.port('+VL', ('Q3', 2), 'U')
    d.at('C101', 53, 9.5, text='L'); d.w(('C101', 1), (53, 6)); d.port('+VL', ('C101', 2), 'D')   # E6: base to emitter
    d.at('R15', 57, 12.5); d.w(('Q3', 3), ('R15', 1)); d.port('OL_A', ('R15', 2), 'D')
    d.at('D2', 66, 14); d.port('OL_A', ('D2', 1), 'R'); d.gnd(('D2', 2), 'GNDD'); d.port('SIG_A', ('D2', 3), 'R')
    # the signal detector (U17, as U4 one level lower) and the green driver, in a row below
    Y = 24
    d.at('R118', 3.5, Y, rot=90); d.w((0, Y), ('R118', 1)); d.port('PRESRC', (0, Y))
    d.at('U17', 21, Y + 1, mirror='x', unit=1)
    d.w(('R118', 2), ('U17', 2)); d.at('D11', 9, Y + 4)
    d.port('SIG_IN', ('D11', 3), 'U'); d.gnd(('D11', 1), 'GNDD')
    d.at('R119', 13, Y + 6); d.w(('R119', 1), (13, Y + 3)); d.port('VREF', (13, Y + 3), 'L')
    d.at('R120', 13, Y + 10); d.w(('R119', 2), ('R120', 1)); d.gnd(('R120', 2))
    d.w(('U17', 3), (16, Y + 2), (16, Y + 8), (13, Y + 8))
    d.at('U17', 40, Y + 2, unit=2)
    d.at('R127', 25.5, Y + 1, rot=90); d.w(('U17', 1), ('R127', 1)); d.w(('R127', 2), (37, Y + 1)); d.w((37, Y + 1), ('U17', 5))   # P1
    d.at('R121', 28, Y - 2.5, text='L'); d.w(('R121', 2), (28, Y + 1)); d.w(('R121', 1), (28, Y - 5)); d.port('+VL', (28, Y - 5), 'U')
    d.at('C99', 31, Y + 2.5, text='L'); d.gnd(('C99', 2), 'GNDD')
    d.port('VREF', ('U17', 6), 'L')
    d.w(('U17', 7), (46, Y + 2)); d.at('R122', 49.5, Y + 2, rot=90); d.w((46, Y + 2), ('R122', 1))
    d.at('Q4', 56, Y + 2, mirror='x'); d.w(('R122', 2), ('Q4', 1))
    d.at('R123', 53, Y - 1.5); d.w(('R123', 2), (53, Y + 2)); d.w(('R123', 1), (53, Y - 4)); d.port('+VL', (53, Y - 4), 'U')
    d.port('+VL', ('Q4', 2), 'U')
    d.at('C102', 51, Y + 5.5, text='L'); d.w(('C102', 1), (51, Y + 2)); d.port('+VL', ('C102', 2), 'D')   # E6
    d.at('R124', 57, Y + 8.5); d.w(('Q4', 3), ('R124', 1)); d.port('SIG_A', ('R124', 2), 'D')
    # Q5 holds Q4's base at +VL while U4B lights the red (base from U4B's output, OL_K), so an overload shows red alone
    d.port('SIG_B', (53, Y + 2), 'D')
    d.at('Q5', 70, Y + 2, mirror='x'); d.port('+VL', ('Q5', 2), 'U'); d.port('SIG_B', ('Q5', 3), 'D')
    d.at('R125', 64.5, Y + 2, rot=90); d.w(('R125', 2), ('Q5', 1)); d.w(('R125', 1), (63, Y - 2)); d.port('OL_K', (63, Y - 2), 'U')
    d.port('OL_K', (46, 6), 'D')


def overload_cs1(d):
    """CS1 (docs/studies/console_survey.md), the overload detector's second piece: four more taps and the negative side."""
    d.shift(0, 44)
    # CS1: the other four taps (receiver, gain stage, EQ out, post-amp), each 1K into a BAV99 like D1
    Y2 = 4
    for k, (r_, d_, tap) in enumerate((('R128', 'D12', 'RECV'), ('R129', 'D13', 'GOUT'), ('R130', 'D14', 'EQOUT'),
                                       ('R131', 'D15', 'FPOST'))):
        x0 = 18 * k
        d.at(r_, x0 + 3.5, Y2, rot=90); d.w((x0, Y2), (r_, 1)); d.port(tap, (x0, Y2))
        d.at(d_, x0 + 8, Y2 - 2); d.w((r_, 2), (d_, 3))
        d.w((d_, 1), (x0 + 5, Y2 - 4)); d.port('OL_NN', (x0 + 5, Y2 - 4), 'U')
        d.w((d_, 2), (x0 + 11, Y2 - 4)); d.port('PK', (x0 + 11, Y2 - 4), 'U')
    # CS1 negative side, PK's mirror: OL_NN (R134 // C103 to GNDA); U18A trips when OL_NC (2/3 +VL + 1/3 OL_NN) falls
    # below VREF, i.e. OL_NN < -VL / 2, and discharges OL_HOLD through R135 like U4A through R126
    Y3 = 14
    d.at('U18', 21, Y3 + 1, mirror='x', unit=1)
    d.w(('U18', 2), (16, Y3)); d.port('VREF', (16, Y3), 'U')
    d.v('R132', 12, Y3 + 0.5, top='+VL', text='L'); d.w(('R132', 1), (12, Y3 - 3)); d.port('+VL', (12, Y3 - 3), 'U')
    d.w(('U18', 3), (12, Y3 + 2))
    d.v('R133', 12, Y3 + 3.5, top='OL_NC', text='R')
    d.w(('R133', 2), (3, Y3 + 5)); d.port('OL_NN', (3, Y3 + 5), 'L')
    d.v('C103', 9, Y3 + 6.5, text='R'); d.gnd(('C103', 2)); d.v('R134', 5.5, Y3 + 6.5, text='L'); d.gnd(('R134', 2))
    d.at('R135', 25.5, Y3 + 1, rot=90); d.w(('U18', 1), ('R135', 1)); d.w(('R135', 2), (30, Y3 + 1)); d.port('OL_HOLD', (30, Y3 + 1), 'R')
    d.at('U18', 40, Y3 + 2, unit=2)                                   # spare half: + on VREF, - on GNDD, output off
    d.port('VREF', ('U18', 5), 'L'); d.w(('U18', 6), (35, Y3 + 3), (35, Y3 + 4)); d.gnd((35, Y3 + 4), 'GNDD')


def pfl(d):
    d.shift(0, 3)
    d.at('C96', 3.5, 4, rot=90, text='U'); d.w((0, 4), ('C96', 1)); d.port('PRE', (0, 4))     # K1: DC block
    d.at('R32', 8.5, 4, rot=90); d.w(('C96', 2), ('R32', 1))
    d.at('SW3', 14, 4, unit=1); d.w(('R32', 2), ('SW3', 2))
    d.w(('SW3', 1), (19, 3)); d.port('PFL', (19, 3), 'R')
    d.w(('SW3', 3), (17, 5), (17, 6)); d.gnd((17, 6))
    d.at('SW3', 14, 11, unit=2); d.w(('SW3', 5), (9, 11)); d.port('+VL', (9, 11))
    d.w(('SW3', 4), (18, 10)); d.at('R33', 23.5, 10, rot=90); d.w((18, 10), ('R33', 1))
    d.w(('R33', 2), (27, 10)); d.port('PFLDET', (27, 10), 'R')
    d.at('R34', 18, 11.5); d.at('D3', 18, 14.5, rot=90); d.gnd(('D3', 1), 'GNDD')


def mute(d):
    d.shift(6, 4)
    d.at('R16', 3.5, 2, rot=90); d.w((0, 2), ('R16', 1)); d.port('PRE', (0, 2))
    d.at('Q1', 7, 4); d.at('R17', 11.5, 2, rot=90); d.w(('R16', 2), ('R17', 1))
    d.at('Q2', 15, 4); d.at('C81', 18, 3.5)
    p = follower(d, ('U3', 2), 27, 3); d.w(('R17', 2), ('U3', p[0]))
    d.w((31, 3), (34, 3)); d.port('MUTEOUT', (34, 3), 'R')
    d.w(('Q1', 3), (5, 8), (13, 8), ('Q2', 3))
    d.at('C28', 9, 9.5); d.at('R42', 5, 9.5, rot=180, text='L')
    d.at('SW4', 1, 13, mirror='y', unit=1); d.w(('SW4', 2), (5, 13), ('R42', 1))
    d.w(('SW4', 1), (-4, 12)); d.port('-VL', (-4, 12)); d.w(('SW4', 3), (-2, 14), (-2, 15)); d.gnd((-2, 15), 'GNDD')
    led_chain(d, 'SW4', 14, 14, 'R43', 'D4')


def fader(d):
    d.shift(0, 4)
    d.at('RV1', 3, 5, mirror='x', text='L'); d.w((3, 1), ('RV1', 3)); d.port('MUTEOUT', (3, 1), 'U')
    d.at('C13', 7, 5, rot=90, text='U'); d.w(('RV1', 2), ('C13', 1))
    d.at('JP1', 14, 5); d.w(('C13', 2), ('JP1', 1))
    d.at('U2', 27, 6, unit=1, text='U'); d.w(('JP1', 2), ('U2', 3))
    d.at('R18', 17.5, 6.5, text='L'); d.at('C82', 19.5, 6.5)
    d.w(('U2', 2), (24, 15)); d.at('R38', 24, 16.5, text='L')
    d.at('R19', 27.5, 12, rot=270, text='U'); d.w((24, 12), ('R19', 2)); d.w(('R19', 1), (31, 12))
    d.at('C14', 27.5, 15, rot=270, text='D'); d.w((24, 15), ('C14', 2)); d.w(('C14', 1), (31, 15))
    d.w((31, 6), (31, 15)); d.at('C15', 34.5, 6, rot=90, text='U'); d.w(('U2', 1), ('C15', 1))
    d.w(('C15', 2), (40, 6)); d.port('POST', (40, 6), 'R'); d.at('R35', 38, 7.5)
    d.at('J3', 4, 22); d.at('J4', 14, 22); d.at('R44', 20, 22)
    d.note('VCA module option (DNP): J3, J4, R44; JP1 bridged without it', (0, 28), 1.27)
    p = follower(d, ('U2', 2), 36, 22); d.w(('U2', p[0]), (31, 21), (31, 22)); d.gnd((31, 22))
    d.note('U2B: spare half, tied off', (32, 27), 1.27)


def aux(d):
    d.shift(0, 4)
    pots = (('RV2', 'R20'), ('RV3', 'R21'), ('RV4', 'R22'), ('RV5', 'R23'), ('RV6', 'R24'), ('RV7', 'R25'))
    for k, (jp, sw) in enumerate((('JP2', 'SW8'), ('JP3', 'SW9'), ('JP4', 'SW10'))):
        X = k * 30
        d.at(jp, X + 3, 3); d.at(sw, X + 7, 8, mirror='y', unit=1); d.at(sw, X + 7, 17, mirror='y', unit=2, text='D')
        d.w((jp, 2), (X + 3, 7), (sw, 1)); d.w((sw, 3), (X + 2, 9)); d.port('POST', (X + 2, 9))
        d.w((sw, 2), (X + 22, 8))
        for j, x in enumerate((X + 12, X + 22)):
            pot, r = pots[2 * k + j]
            d.at(pot, x, 12, mirror='x', text='L'); d.w((x, 8), (pot, 3))
            if pot == 'RV7':
                d.at('SW13', x + 6, 12, unit=1); d.w((pot, 2), ('SW13', 2))
                d.at(r, x + 9, 15.5); d.w(('SW13', 3), 'h', (x + 9, 14)); d.w((r, 2), (x + 9, 18)); d.port('AUX6', (x + 9, 18), 'D')
                d.at('SW13', x + 6, 22, unit=2)
            else:
                d.at(r, x + 2, 16.5); d.w((pot, 2), (x + 2, 12), (r, 1))
                d.w((r, 2), (x + 2, 19)); d.port(f'AUX{2 * k + j + 1}', (x + 2, 19), 'D')


def direct_out(d):
    d.shift(8, 3)
    p = follower(d, ('U8', 1), 8, 5); d.w((-9, 4), ('U8', p[0])); d.port('DIRSRC', (-9, 4))
    d.at('R70', -6, 5.5, text='L'); d.at('C83', -2, 5.5)
    d.at('R71', 14.5, 5, rot=90); d.w((12, 5), ('R71', 1))
    d.at('C52', 18.5, 5, rot=90, text='U'); d.w(('R71', 2), ('C52', 1))
    d.w(('C52', 2), (25, 5)); d.port('DO_T', (25, 5), 'R'); d.at('R72', 22, 6.5)
    d.at('R73', 22, 11.5); d.w(('R73', 1), (27, 10)); d.port('DO_R', (27, 10), 'R')
    d.at('R143', 25, 11.5)                                                # RV3b: 47K bleed on the ring, as R72
    d.at('C107', 22, 14.5, text='L'); d.w(('R73', 2), ('C107', 1))     # RV3



def pan(d):
    d.shift(0, 5)
    d.at('RV8', 12, 14)
    for pn, x in (('3', 11), ('4', 13)): d.w(('RV8', pn), (x, 16)); d.gnd((x, 16))
    d.w(('RV8', 1), (8, 18), (16, 18), ('RV8', 6)); d.w((8, 18), (5, 18)); d.port('POST', (5, 18))
    d.at('U8', 8, 6, mirror='x', unit=2)
    # CS2: 1.22x (R137 2K2 / R138 10K) and R136 3K3 back to the wiper: the Delta's -4.4 dB law
    d.at('R137', 10.5, 3, rot=90, text='U'); d.w(('U8', 7), (12, 6), (12, 3), ('R137', 2))
    d.w(('R137', 1), (4, 3), (4, 5), ('U8', 6))
    d.at('R138', 2.5, 3, rot=90, text='U'); d.w(('R138', 2), (4, 3)); d.w(('R138', 1), (1, 4)); d.gnd((1, 4))
    d.at('C105', 10.5, 1, rot=90, text='U'); d.w((9, 3), (9, 1), ('C105', 1)); d.w(('C105', 2), (12, 1), (12, 3))
    d.w(('U8', 5), (3, 7), (3, 10), (9.5, 10), ('RV8', 2)); d.at('C79', 3, 11.5, text='L')
    d.at('R136', 12, 8.5, text='R'); d.w((12, 6), ('R136', 1)); d.w(('R136', 2), (12, 10), (9.5, 10))
    d.at('C16', 15.5, 6, rot=90, text='U'); d.w((12, 6), ('C16', 1))
    d.w(('C16', 2), (21, 6)); d.port('PANL', (21, 6), 'R'); d.at('R36', 18, 7.5)
    d.at('U3', 36, 6, mirror='x', unit=1)
    d.at('R140', 38.5, 3, rot=90, text='U'); d.w(('U3', 1), (40, 6), (40, 3), ('R140', 2))
    d.w(('R140', 1), (32, 3), (32, 5), ('U3', 2))
    d.at('R141', 30.5, 3, rot=90, text='U'); d.w(('R141', 2), (32, 3)); d.w(('R141', 1), (29, 4)); d.gnd((29, 4))
    d.at('C106', 38.5, 1, rot=90, text='U'); d.w((37, 3), (37, 1), ('C106', 1)); d.w(('C106', 2), (40, 1), (40, 3))
    d.w(('U3', 3), (31, 7), (31, 11), (14.5, 11), ('RV8', 5)); d.at('C80', 31, 12.5)
    d.at('R139', 40, 8.5, text='R'); d.w((40, 6), ('R139', 1)); d.w(('R139', 2), (40, 11), (31, 11))
    d.at('C17', 43.5, 6, rot=90, text='U'); d.w((40, 6), ('C17', 1))
    d.w(('C17', 2), (49, 6)); d.port('PANR', (49, 6), 'R'); d.at('R37', 46, 7.5)


def pan_switch(d):
    d.shift(0, 3)
    d.at('SW14', 5, 3, mirror='y', unit=1); d.at('SW14', 5, 9, mirror='y', unit=2)
    d.w(('SW14', 3), (1, 4), (1, 10), ('SW14', 6)); d.w((1, 4), (-2, 4)); d.port('POST', (-2, 4))


def routing_vl(d):
    """+5VL for the DG413 logic: 4K7 from +VA, BZX84C5V1, 1u, BAT54W back to +VA."""
    d.shift(0, 10)
    d.at('R80', 3.5, -4, rot=90, text='D'); d.w((0, -4), ('R80', 1)); d.port('+VA', (0, -4))
    d.w(('R80', 2), (20, -4)); d.port('+5VL', (20, -4), 'R')
    d.at('D9', 6.5, -2.5, rot=270); d.at('C62', 13.5, -2.5); d.at('#FLG07', 17, -4)
    d.at('D10', 3.5, -7, mirror='x', text='U'); d.w(('D10', 3), (2, -7), ('R80', 1)); d.w(('D10', 1), (5, -7), ('R80', 2))


ASSIGNS = (('SW5', 'U9', 'R26', 'R27', 'PANL', 'PANR', 'MIXL', 'MIXR', 'R74', 'R75', 'D6', ('C53', 'C54', 'C55')),
           ('SW6', 'U10', 'R28', 'R29', 'SUBSRC_L', 'SUBSRC_R', 'SUB1', 'SUB2', 'R76', 'R77', 'D7', ('C56', 'C57', 'C58')),
           ('SW7', 'U11', 'R30', 'R31', 'SUBSRC_L', 'SUBSRC_R', 'SUB3', 'SUB4', 'R78', 'R79', 'D8', ('C59', 'C60', 'C61')))


def routing_assign(k):
    """One assign key: two DG413 pairs move the 4K7s' bus ends between bus and ground, the key's LED."""
    def draw(d):
        sw, u, rl, rr, sl, sr, bl, br, rpd, rled, dled, cs = ASSIGNS[k]
        d.shift(0, 10)
        X = 22 + k * 44
        for (r, net, y, ub, ug, pb, ps, pc, gs, gg, gc) in (
                (rl, sl, 2, 1, 4, 2, 3, 1, 14, 15, 16), (rr, sr, 14, 2, 3, 7, 6, 8, 11, 10, 9)):
            d.at(r, X + 3.5, y, rot=90); d.w((X, y), (r, 1)); d.port(net, (X, y))
            d.at(u, X + 10, y, mirror='y' if ub == 1 else None, unit=ub)
            d.at(u, X + 10, y + 5, mirror='y', unit=ug)
            d.w((r, 2), (u, ps)); d.w((X + 6, y), (X + 6, y + 5), (u, gs))
            d.w((u, pb), (X + 16, y)); d.port(bl if ub == 1 else br, (X + 16, y), 'R')
            d.w((u, gg), (X + 14, y + 5), (X + 14, y + 6)); d.gnd((X + 14, y + 6))
            ctl = d.nets(u)[str(pc)]       # the switch's control line: labelled at each IN, no wire across the bus outputs
            d.w((u, pc), (X + 10, y + 3), (X + 13, y + 3)); d.port(ctl, (X + 13, y + 3), 'R')
            d.w((u, gc), (X + 10, y + 8), (X + 8, y + 8)); d.port(ctl, (X + 8, y + 8), 'L')    # left, clear of the ground
        d.at(sw, X + 19, 26, unit=1); d.w((X + 17, 23), (sw, 2)); d.port(ctl, (X + 17, 23), 'U')
        d.at(rpd, X + 13, 25.5); d.w((X + 17, 24), (X + 13, 24))
        led_chain(d, sw, X + 19, 32, rled, dled)
        frags.dg_supply(d, u, X + 26, 12)
        for j, c in enumerate(cs): d.at(c, X + 30 + 4.5 * j, 10)
        d.note(f'ASSIGN {bl}/{br}' if k == 0 else f'ASSIGN {bl}-{br}', (X, -2), 1.5)
    return draw


def power_rails(d):
    """Rail filters (10R + reservoir per rail) with their PWR_FLAGs, grounds, the spade and the GCANCEL 10R."""
    d.shift(0, 6)
    for k, (r, cb, cs, src, out, flag, neg) in enumerate((
            ('R1', 'C1', 'C2', '+VBUS', '+VA', '#FLG01', False), ('R2', 'C3', 'C4', '-VBUS', '-VA', '#FLG02', True),
            ('R3', 'C5', None, '+VBUS', '+VL', '#FLG03', False), ('R4', 'C6', None, '-VBUS', '-VL', '#FLG04', True))):
        y = k * 8
        d.at(r, 3.5, y, rot=90, text='U'); d.w((0, y), (r, 1)); d.port(src, (0, y))
        d.w((r, 2), (19, y)); d.port(out, (19, y), 'R')
        d.at(cb, 8, y + 1.5, rot=180 if neg else 0, text='L')
        if cs: d.at(cs, 11, y + 1.5, rot=180 if neg else 0)
        if k == 0: d.v('D16', 14.5, y + 1.5, top=out, text='R')               # CS10: reverse Schottky, K on +VA
        if k == 1: d.at('D17', 14.5, y + 1.5, rot=270, mirror='x', text='R')  # CS10: A on -VA (D16's text layout)
        d.at(flag, 16, y)
    d.at('#FLG05', 24, 2); d.at('#FLG06', 24, 10)
    d.at('NT1', 30, 2); d.at('CN4', 38, 10); d.at('R5', 30, 17)
    d.note('GNDA-GNDD: one net tie (NT1) beside the spade', (26, 22), 1.27)


OPS = [('U1', 'C20', 'C21'), ('U2', 'C22', 'C23'), ('U3', 'C24', 'C25'), ('U5', 'C29', 'C30'), ('U6', 'C31', 'C32'),
       ('U7', 'C33', 'C34'), ('U8', 'C35', 'C36'), ('U12', 'C63', 'C64'), ('U13', 'C65', 'C66'),
       ('U14', 'C67', 'C68'), ('U15', 'C89', 'C90'), ('U16', 'C92', 'C93')]
X0, YP, P = 52, 8, 9                     # op-amp supply rows: origin, pitch


def power_ops(lo, hi):
    """Op-amp supply units lo..hi-1 on +VA / -VA, each with its two decouplers."""
    def draw(d):
        d.shift(0, 6); Y = YP
        d.w((X0 + P * lo - 3, Y - 5), (X0 + P * (hi - 1) + 3, Y - 5)); d.port('+VA', (X0 + P * lo - 3, Y - 5))
        d.w((X0 + P * lo - 3, Y + 5), (X0 + P * (hi - 1) + 3, Y + 5)); d.port('-VA', (X0 + P * lo - 3, Y + 5))
        for k, (u, cp, cn) in enumerate(OPS[lo:hi], lo):
            X = X0 + P * k
            d.at(u, X, Y, unit=3); d.w((u, 8), (X - 1, Y - 5)); d.w((u, 4), (X - 1, Y + 5))
            d.at(cp, X + 3, Y - 3.5); d.at(cn, X + 3, Y + 3.5)
            d.w((cp, 2), (cn, 1)); d.w((X + 3, Y), (X + 1.5, Y), (X + 1.5, Y + 0.5)); d.gnd((X + 1.5, Y + 0.5))
    return draw


def power_vl(d):
    """The comparators' (U4, U17, U18) logic supply."""
    d.shift(0, 6); Y = YP
    X = X0 + P * len(OPS) + 2
    for u, c, X in (('U4', 'C26', X), ('U17', 'C98', X + 9), ('U18', 'C104', X + 18)):   # U17 MET1, U18 CS1
        d.at(u, X, Y, unit=3); d.at(c, X + 3, Y)
        d.w((u, 8), (X - 1, Y - 5), (X + 3, Y - 5), (c, 1)); d.port('+VL', (X + 3, Y - 5), 'R')
        d.w((u, 4), (X - 1, Y + 5), (X + 3, Y + 5), (c, 2)); d.gnd((X + 3, Y + 5), 'GNDD')


def motherloom(d):
    frags.header(d, 'CN1', 20, 12)


def jumpers(d):
    d.shift(0, 4)
    for k, jp in enumerate(('JP6', 'JP5', 'JP7')): d.at(jp, 6 + 20 * k, 2)


# a list: the block's pieces, drawn in turn on one sheet, packed separately on pages (schgen.build pages=)
DRAWINGS = {'JACK LINK CLAMPS': link_clamps, 'LINE INPUT': receiver, 'GAIN': gain, 'HPF': hpf, 'EQ  ': eq, 'EQ MID TUNING': [khn_band(0), khn_band(1)],
            'EQ IN': eq_in, 'INSERT (': insert, 'OVERLOAD': [overload, overload_cs1], 'PFL': pfl, 'ON / SOFT MUTE': mute, 'FADER': fader,
            'AUX SENDS': aux, 'DIRECT OUT': direct_out, 'PAN + PAN': pan, 'PAN SWITCH': pan_switch,
            'ROUTING': [routing_vl] + [routing_assign(k) for k in range(3)],
            'POWER ENTRY': [power_rails, power_ops(0, 6), power_ops(6, len(OPS)), power_vl], 'MOTHERLOOM': motherloom,
            'INSERT POSITION': jumpers}


def for_title(title):
    return next((f for k, f in DRAWINGS.items() if title.startswith(k)), None)
