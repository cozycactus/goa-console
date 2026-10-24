"""Drawing fragments for the master_lib circuits (group and master schematics). A circuit function registers
schgen.frag(b, w, h, fn): fn(d) draws its parts with schdraw.Drawing calls in grid units from the fragment's
top-left corner; the block lays its fragments out in rows (schgen.flow) and puts any part no fragment drew in labelled
rows under them. Op-amp pins per unit: PP[unit] = (+, -, out); comparators of the LM2901 have their own (CPP)."""
PP = {1: (3, 2, 1), 2: (5, 6, 7)}
CPP = {1: (5, 4, 2), 2: (7, 6, 1), 3: (11, 10, 13), 4: (9, 8, 14)}


def pins(u, lm2901=False):
    return (CPP if lm2901 else PP)[u[1]]


def inv(d, src, out, u, rin, rf, cf, plus, src2=None, rin2=None):
    """Inverting stage (summer): src -> rin -> - input (and src2 -> rin2), rf // cf over the top, + to the net
    'plus' (a ground symbol when it is a ground). Parts turned by their nets.  24 x 15"""
    p = pins(u); node = d.nets(u[0])[str(p[1])]
    d.at(u[0], 16, 9, mirror='x', unit=u[1])
    d.h(rin, 3.5, 8, left=src, text='D'); d.w((0, 8), (2, 8)); d.port(src, (0, 8)); d.w((5, 8), (u[0], p[1]))
    d.w((9, 2), (9, 12 if rin2 else 8))
    d.h(rf, 12.5, 5, left=node, text='D'); d.w((9, 5), (11, 5)); d.w((14, 5), (20, 5))
    d.h(cf, 12.5, 2, left=node, text='U'); d.w((9, 2), (11, 2)); d.w((14, 2), (20, 2))
    d.w((20, 2), (20, 9)); d.w((u[0], p[2]), (23, 9)); d.port(out, (23, 9), 'R')
    if rin2:
        d.h(rin2, 3.5, 12, left=src2, text='D'); d.w((0, 12), (2, 12)); d.port(src2, (0, 12)); d.w((5, 12), (9, 12))
    if plus in ('GNDA', 'GNDD', 'GNDM'): d.w((u[0], p[0]), (12, 10), (12, 11)); ground(d, (12, 11), plus)
    else: d.w((u[0], p[0]), (11, 10)); d.port(plus, (11, 10))


def wiper_follower(d, src, out, u, cin, rsh, csh, rbo=None, final=None):
    """Follower on a pot wiper: src -> cin -> +, rsh and csh to ground; optional build-out rbo to 'final'.  24 x 10"""
    p = pins(u)
    d.at(u[0], 15, 4, unit=u[1])
    d.h(cin, 3.5, 3, left=src, text='U'); d.w((0, 3), (2, 3)); d.port(src, (0, 3)); d.w((5, 3), (u[0], p[0]))
    d.v(rsh, 7, 4.5, top=d.nets(cin)['2'] if d.nets(cin)['1'] == src else d.nets(cin)['1'], text='L'); d.at(csh, 10, 4.5)
    d.w((u[0], p[2]), (19, 4), (19, 7), (11.5, 7), (11.5, 5), (u[0], p[1]))
    if rbo:
        d.h(rbo, 21.5, 4, left=d.nets(u[0])[str(p[2])], text='U'); d.w((19, 4), (20, 4))
        d.w((23, 4), (26, 4)); d.port(final, (26, 4), 'R')
    else:
        d.w((19, 4), (22, 4)); d.port(out, (22, 4), 'R')


def phones(d, src, u, cin, rsh, csh, buf, rout, rf, cf, rg, caps, out):
    """Headphone composite: wiper follower-style input, OPA1612 driving the LME49600 inside the loop, 2R2 out; the
    4K7 from the output (after the 2R2) and the 100p from the op-amp's own output to the - node, 2K2 to ground.  40 x 20"""
    p = pins(u); fin = d.nets(u[0])[str(p[0])]; fn = d.nets(u[0])[str(p[1])]; drv = d.nets(u[0])[str(p[2])]
    d.at(u[0], 16, 4, unit=u[1])
    d.h(cin, 3.5, 3, left=src, text='U'); d.w((0, 3), (2, 3)); d.port(src, (0, 3)); d.w((5, 3), (u[0], p[0]))
    d.v(rsh, 7, 4.5, top=fin, text='L'); d.at(csh, 10, 4.5)
    d.at(buf, 25, 4)                                                   # LME49600: in (2) left, out (4) right
    d.w((u[0], p[2]), (buf, 2))
    d.h(rout, 33.5, 4, left=d.nets(buf)['4'], text='U'); d.w((buf, 4), (32, 4)); d.w((35, 4), (39, 4)); d.port(out, (39, 4), 'R')
    d.w((u[0], p[1]), (13, 5), (13, 14))
    d.h(cf, 16.5, 10, left=fn, text='D'); d.w((13, 10), (15, 10)); d.w((18, 10), (20, 10), (20, 4))
    d.h(rf, 22.5, 14, left=fn, text='D'); d.w((13, 14), (21, 14)); d.w((24, 14), (37, 14), (37, 4))
    d.v(rg, 13, 15.5, top=fn, text='L')
    for i, c in enumerate(caps): d.at(c, 27 + 4 * i, 18)


def part(d, r, x, y, unit=None):
    """One part, its pins labelled (connectors, headers, single parts)."""
    d.at(r, x, y, unit=unit)



def diff(d, inn, inp, out, u, r1, r2, r3, r4, c0, c1, shunts=(), c0n=2):
    """Difference amplifier (re-inverter, balanced receiver): inn -> r1 -> -, r2 // c0 over the top; inp -> r3 -> +,
    r4 and c1 from + to ground. shunts: (ring cap, tip cap, tip 1M) of a receiver's inputs.  30 x 18"""
    p = pins(u)
    d.at(u[0], 22, 9, mirror='x', unit=u[1])
    d.at(r1, 10.5, 8, rot=90, text='U'); d.w((0, 8), (r1, 1)); d.port(inn, (0, 8)); d.w((r1, 2), (u[0], p[1]))
    d.w((14, 2), (14, 8))
    d.at(r2, 18.5, 5, rot=90, text='D'); d.w((14, 5), (r2, 1)); d.w((r2, 2), (26, 5))
    d.at(c0, 18.5, 2, rot=270 if c0n == 2 else 90, text='U'); d.w((14, 2), (c0, c0n)); d.w((c0, 3 - c0n), (26, 2))
    d.w((26, 2), (26, 9)); d.w((u[0], p[2]), (29, 9)); d.port(out, (29, 9), 'R')
    d.at(r3, 10.5, 14, rot=90, text='U'); d.w((0, 14), (r3, 1)); d.port(inp, (0, 14))
    d.w((r3, 2), (15, 14), (15, 10), (u[0], p[0]))
    d.at(r4, 15, 15.5, text='L'); d.w((15, 14), (17, 14)); d.at(c1, 17, 15.5)
    if shunts:
        cr, ct, rt = shunts
        d.at(cr, 3, 9.5, text='L'); d.at(ct, 3, 15.5, text='L'); d.at(rt, 6, 15.5)


def noninv(d, src, out, u, cin, rsh, csh, rf, cf, rg, rb=None, cout=None, rout=None, post=None):
    """Non-inverting stage on a pot wiper: src -> cin -> +, rsh and csh to ground; - node with cf and rf to the output
    line below the stage and rg to ground. With rb / cout / rout: 47R build-out, coupler, 47K, then 'post'.  38 x 17"""
    p = pins(u)
    d.at(u[0], 18, 4, unit=u[1])
    d.at(cin, 3.5, 3, rot=90, text='U'); d.w((0, 3), (cin, 1)); d.port(src, (0, 3)); d.w((cin, 2), (u[0], p[0]))
    d.at(rsh, 7, 4.5, text='L'); d.at(csh, 11, 4.5, text='L')
    d.w((u[0], p[1]), (13, 5), (13, 13))
    d.at(cf, 16.5, 9, rot=270, text='D'); d.w((13, 9), (cf, 2)); d.w((cf, 1), (22, 9))
    d.at(rf, 16.5, 13, rot=270, text='D'); d.w((13, 13), (rf, 2)); d.w((rf, 1), (22, 13))
    d.at(rg, 13, 14.5, text='L')
    d.w((u[0], p[2]), (22, 4), (22, 13))
    if rb:
        d.at(rb, 25.5, 4, rot=90, text='U'); d.w((22, 4), (rb, 1))
        d.at(cout, 30.5, 4, rot=90, text='U'); d.w((rb, 2), (cout, 1))
        d.w((cout, 2), (37, 4)); d.port(post, (37, 4), 'R'); d.at(rout, 35, 5.5)
    else:
        d.w((22, 4), (25, 4)); d.port(out, (25, 4), 'R')


def follower(d, src, out, u, cap=None):
    """Unity follower, + on top, the loop under it; cap: a C from + to ground.  16 x 9"""
    p = pins(u)
    d.at(u[0], 8, 3, unit=u[1])
    d.w((0, 2), (u[0], p[0])); d.port(src, (0, 2))
    d.w((u[0], p[2]), (12, 3), (12, 6), (4, 6), (4, 4), (u[0], p[1]))
    d.w((12, 3), (15, 3)); d.port(out, (15, 3), 'R')
    if cap: d.at(cap, 2, 3.5, text='L')


def insert(d, src, send, rr, dst, rs, cin, rin, rprot, cprot, u, rbo, cout, rout):
    """Insert: send through 75R; return: coupler, 47K, 1K + 100p, follower, 75R build-out, coupler, 47K.  39 x 12"""
    d.at(rs, 3.5, 1, rot=90); d.w((0, 1), (rs, 1)); d.port(src, (0, 1)); d.w((rs, 2), (8, 1)); d.port(send, (8, 1), 'R')
    d.at(cin, 3.5, 6, rot=90, text='U'); d.w((0, 6), (cin, 1)); d.port(rr, (0, 6))
    d.w((cin, 2), (7, 6)); d.at(rin, 7, 7.5, text='L')
    d.at(rprot, 10.5, 6, rot=90, text='U'); d.w((7, 6), (rprot, 1))
    d.at(cprot, 14, 7.5, text='L')
    p = pins(u)
    d.at(u[0], 20, 7, unit=u[1]); d.w((rprot, 2), (u[0], p[0]))
    d.w((u[0], p[2]), (24, 7), (24, 10), (16, 10), (16, 8), (u[0], p[1]))
    d.at(rbo, 26.5, 7, rot=90, text='U'); d.w((24, 7), (rbo, 1))
    d.at(cout, 31.5, 7, rot=90, text='U'); d.w((rbo, 2), (cout, 1))
    d.w((cout, 2), (38, 7)); d.port(dst, (38, 7), 'R'); d.at(rout, 36, 8.5)


def drv134(d, inp, op, on, u, cs_p, cs_n, cv_p, cv_n):
    """DRV134 line driver: 10u NP from each Sense pin to its output, supply decoupling beside.  30 x 15"""
    d.at(u, 8, 8)
    d.w((0, 8), (u, 4)); d.port(inp, (0, 8))
    d.w((u, 3), (3, 10), (3, 11)); d.gnd((3, 11))
    d.at(cs_p, 15.5, 4, rot=90, text='U'); d.w((u, 8), (13, 6), (13, 4), (cs_p, 1))
    d.w((u, 7), (18, 7)); d.w((cs_p, 2), (18, 4), (18, 7)); d.w((18, 7), (21, 7)); d.port(op, (21, 7), 'R')
    d.at(cs_n, 15.5, 12, rot=90, text='D'); d.w((u, 1), (13, 10), (13, 12), (cs_n, 1))
    d.w((u, 2), (18, 9)); d.w((cs_n, 2), (18, 12), (18, 9)); d.w((18, 9), (21, 9)); d.port(on, (21, 9), 'R')
    d.at(cv_p, 25, 5.5); d.at(cv_n, 28, 5.5, rot=180)


def relay(d, k, rcoil, dfly, nc_net):
    """G6K-2F-Y mute relay: coil from +VBUS through rcoil, flyback diode across the coil, driver at the bottom;
    contacts labelled (NO = driver side, COM = connector side, NC grounded).  24 x 15"""
    d.at(k, 9, 8)
    d.at(rcoil, 5, 2.5); d.w((rcoil, 1), (5, 0)); d.port('+VBUS', (5, 0), 'U'); d.w((rcoil, 2), (k, 1))
    d.at(dfly, 1, 8, rot=270); d.w((dfly, 1), (1, 5), (k, 1)); d.w((dfly, 2), (1, 11), (k, 8))
    d.w((k, 8), (5, 13)); d.port('RLY_DRV', (5, 13), 'D')
    for pn in (2, 7):                               # NC contacts: ground (or the relay's own return net)
        if nc_net in ('GNDA', 'GNDD'): d.gnd((k, pn), nc_net, 'U')
        else: d.port(nc_net, (k, pn), 'U')


def routing(d, srcl, srcr, busl, busr, rl, rr, sw):
    """Strip-style routing switch: 4K7 to the switch common, assigned = bus, off = ground.  16 x 11"""
    for (src, r, unit, com, bus_pin, gnd_pin, bus, y) in ((srcl, rl, 1, 2, 1, 3, busl, 2), (srcr, rr, 2, 5, 4, 6, busr, 8)):
        d.at(r, 3.5, y, rot=90); d.w((0, y), (r, 1)); d.port(src, (0, y))
        d.at(sw, 9, y, unit=unit); d.w((r, 2), (sw, com))
        d.w((sw, bus_pin), (14, y - 1)); d.port(bus, (14, y - 1), 'R')
        d.w((sw, gnd_pin), (12, y + 1), (12, y + 2)); d.gnd((12, y + 2))


def afl(d, junction, sw, r_det, r_led, led):
    """PFL / AFL key: pole A puts the junction on the PFL bus (else ground), pole B lights the LED and pulls PFLDET.  20 x 15"""
    d.at(sw, 6, 2, unit=1); d.w((0, 2), (sw, 2)); d.port(junction, (0, 2))
    d.w((sw, 1), (11, 1)); d.port('PFL', (11, 1), 'R'); d.w((sw, 3), (9, 3), (9, 4)); d.gnd((9, 4))
    d.at(sw, 6, 8, unit=2); d.w((sw, 5), (1, 8)); d.port('+VL', (1, 8))
    d.w((sw, 4), (10, 7)); d.at(r_det, 14.5, 7, rot=90, text='U'); d.w((10, 7), (r_det, 1))
    d.w((r_det, 2), (19, 7)); d.port('PFLDET', (19, 7), 'R')
    d.at(r_led, 10, 8.5); d.at(led, 10, 11.5, rot=90); d.gnd((led, 1), 'GNDD')


def power_unit(d, u, cp, cn):
    """An IC's power unit with its two decouplers (labels and ground symbols).  12 x 10"""
    d.at(u[0], 3, 5, unit=u[1]); d.at(cp, 7, 5); d.at(cn, 10, 5, rot=180)


def chain(d, start, elems, end=None):
    """A signal line from the net 'start': ('s', ref) a series part, ('g', ref) a part from the line to its other net
    (ground or a rail, drawn down from the line); parts are turned by their nets. 'end' labels the far end."""
    d.port(start, (0, 2)); x = 0; net = start
    for i, (kind, r) in enumerate(elems):
        if kind == 's':
            nxt = d.h(r, x + 3.5, 2, left=net, text='U'); d.w((x, 2), (x + 2, 2)); x += 5; net = nxt
        else:
            d.w((x, 2), (x + 2, 2)); d.v(r, x + 2, 3.5, top=net)
            x += 2
            if i + 1 < len(elems) and elems[i + 1][0] == 'g': d.w((x, 2), (x + 4, 2)); x += 4   # room for the texts
    if end: d.w((x, 2), (x + 3, 2)); d.port(end, (x + 3, 2), 'R'); x += 3
    return x


def chain_w(elems, end=True):
    return sum(5 if k == 's' else 6 for k, _ in elems) + (3 if end else 0) + 5


def pot(d, r, top, wiper):
    """A pot (pin 1 = ground end) drawn vertically: hot end up, wiper to the right.  12 x 9"""
    d.at(r, 3, 4, mirror='x'); d.w((r, 3), (3, 1)); d.port(top, (3, 1), 'U')
    d.w((r, 2), (8, 4)); d.port(wiper, (8, 4), 'R')


def pot2(d, r):
    """A dual pot, its pins labelled.  14 x 8"""
    d.at(r, 6, 4)


GROUNDS = ('GNDA', 'GNDD', 'GNDM')


def ground(d, pt, net):
    """A ground symbol (GNDA / GNDD), or a label pointing down for a ground with no symbol (GNDM)."""
    if net in ('GNDA', 'GNDD'): d.gnd(pt, net)
    else: d.port(net, pt, 'D')


def comparators(d, units, out=None):
    """Comparators stacked 8 grid apart, each input wired to its label (or a ground symbol); out: the shared output
    net of a wired-AND pair, joined on a vertical. units: [((ref, unit), lm2901)].  18 x 8 per unit"""
    for k, (u, lm) in enumerate(units):
        y = 4 + 8 * k; p = pins(u, lm); n = d.nets(u[0])
        d.at(u[0], 8, y, unit=u[1])
        for pn, yy in ((p[0], y - 1), (p[1], y + 1)):
            net = n[str(pn)]
            if net in GROUNDS: d.w((u[0], pn), (4, yy), (4, yy + 1)); ground(d, (4, yy + 1), net)
            else: d.w((u[0], pn), (1, yy)); d.port(net, (1, yy))
        if out: d.w((u[0], p[2]), (13, y))
        else: d.w((u[0], p[2]), (15, y)); d.port(n[str(p[2])], (15, y), 'R')
    if out:
        d.w((13, 4), (13, 4 + 8 * (len(units) - 1))); d.w((13, 4), (16, 4)); d.port(out, (16, 4), 'R')


def npn(d, q):
    """NPN switch: base, collector and emitter to their labels (emitter to a ground symbol).  10 x 9"""
    n = d.nets(q)
    d.at(q, 4, 4); d.w((q, 1), (1, 4)); d.port(n['1'], (1, 4))
    d.w((q, 3), (5, 1)); d.port(n['3'], (5, 1), 'U')
    if n['2'] in GROUNDS: d.w((q, 2), (5, 7)); ground(d, (5, 7), n['2'])
    else: d.w((q, 2), (5, 8)); d.port(n['2'], (5, 8), 'D')


def dg_pair(d, u, a, b):
    """Two DG413 sections into one D node (PFL switcher): a, b = (unit, S pin, D pin, IN pin); S from the left,
    the D sides joined on the right, IN labelled.  16 x 12"""
    for (unit, s, dd, c), y in ((a, 2), (b, 7)):
        sx = d.pins_of('DG', unit)[str(s)][0]
        d.at(u, 7, y, mirror='y' if sx > 0 else None, unit=unit)
        n = d.nets(u)
        d.w((u, s), (1, y)); d.port(n[str(s)], (1, y))
        d.w((u, c), (7, y + 3), (3, y + 3)); d.port(n[str(c)], (3, y + 3))
    d.w((u, a[2]), (12, 2), (12, 7), (u, b[2])); d.w((12, 2), (15, 2)); d.port(d.nets(u)[str(a[2])], (15, 2), 'R')


def halfwave(d, u, rin, da, db, rf):
    """Precision half-wave rectifier: inverting, db in the feedback, da to the HW output, rf from HW back to the
    - node.  26 x 12"""
    p = pins(u); n = d.nets(u[0]); node, out = n[str(p[1])], n[str(p[2])]
    src = d.nets(rin)['1'] if d.nets(rin)['2'] == node else d.nets(rin)['2']
    hw = d.nets(rf)['1'] if d.nets(rf)['2'] == node else d.nets(rf)['2']
    d.at(u[0], 12, 8, mirror='x', unit=u[1])
    d.h(rin, 4.5, 7, left=src, text='D'); d.w((0, 7), (3, 7)); d.port(src, (0, 7)); d.w((6, 7), (u[0], p[1]))
    d.w((7, 1), (7, 7))
    d.h(db, 11, 4, left=node); d.w((7, 4), (9.5, 4)); d.w((12.5, 4), (16, 4))
    d.h(rf, 11, 1, left=node, text='U'); d.w((7, 1), (9.5, 1)); d.w((12.5, 1), (20, 1))
    d.w((16, 4), (16, 8)); d.w((u[0], p[2]), (16, 8))
    d.h(da, 18, 6, left=out); d.w((16, 6), (16.5, 6)); d.w((19.5, 6), (20, 6)); d.w((20, 1), (20, 6))
    d.w((20, 1), (24, 1)); d.port(hw, (24, 1), 'R')
    d.w((u[0], p[0]), (8, 9), (8, 10)); ground(d, (8, 10), n[str(p[0])])


def meter_sum(d, u, ra, rb, rfx, trim, cf):
    """Meter summer: two inputs, rfx + the calibration trim (as a rheostat) and cf in the feedback.  26 x 15"""
    p = pins(u); n = d.nets(u[0]); node, out = n[str(p[1])], n[str(p[2])]
    other = lambda r: d.nets(r)['1'] if d.nets(r)['2'] == node else d.nets(r)['2']
    d.at(u[0], 16, 9, mirror='x', unit=u[1])
    d.h(ra, 3.5, 8, left=other(ra), text='D'); d.w((0, 8), (2, 8)); d.port(other(ra), (0, 8)); d.w((5, 8), (u[0], p[1]))
    d.h(rb, 3.5, 12, left=other(rb), text='D'); d.w((0, 12), (2, 12)); d.port(other(rb), (0, 12)); d.w((5, 12), (9, 12))
    d.w((9, 2), (9, 12))
    d.h(cf, 12.5, 2, left=node, text='U'); d.w((9, 2), (11, 2)); d.w((14, 2), (20, 2))
    d.at(trim, 11.5, 5, rot=270); d.w((9, 5), (trim, 3)); d.w((trim, 2), (11.5, 7), (9, 7))
    rg = d.nets(trim)['1']
    d.h(rfx, 15.5, 5, left=rg, text='U'); d.w((trim, 1), (14, 5)); d.w((17, 5), (20, 5))
    d.w((20, 2), (20, 9)); d.w((u[0], p[2]), (23, 9)); d.port(out, (23, 9), 'R')
    d.w((u[0], p[0]), (12, 10), (12, 11)); ground(d, (12, 11), n[str(p[0])])


def peak(d, u3, dpk, rpk, cpk, c22, r330, r220, r10, dcl, ravg, cavg, jp, u4, rbo):
    """Meter detector: U3 + diode precision peak (220R / 1u, 330K / 220K bleed), the RC average, the PEAK / AVG jumper,
    the U4 follower and its 470R build-out to DET; R10K from DETO and the clamp diode close U3's loop.  38 x 19"""
    p = pins(u3); n = d.nets(u3[0]); x2, node, u3o = n[str(p[0])], n[str(p[1])], n[str(p[2])]
    d.at(u3[0], 8, 4, unit=u3[1])
    d.w((0, 3), (u3[0], p[0])); d.port(x2, (0, 3))
    d.w((u3[0], p[1]), (4, 5), (4, 11))
    deto = d.nets(r10)['1'] if d.nets(r10)['2'] == node else d.nets(r10)['2']
    d.h(r10, 1.5, 9, left=deto, text='D'); d.w((-2, 9), (0, 9)); d.port(deto, (-2, 9)); d.w((3, 9), (4, 9))
    d.h(c22, 7.5, 7, left=node, text='D'); d.w((4, 7), (6, 7)); d.w((9, 7), (13, 7))
    d.h(dcl, 8, 11, left=node); d.w((4, 11), (6.5, 11)); d.w((9.5, 11), (13, 11))
    d.w((u3[0], p[2]), (13, 4), (13, 11))
    pk1 = d.h(dpk, 15.5, 4, left=u3o); d.w((13, 4), (14, 4))
    pk = d.h(rpk, 19.5, 4, left=pk1, text='U'); d.w((17, 4), (18, 4))
    d.v(cpk, 23, 5.5, top=pk); pkr = d.h(r330, 25.5, 4, left=pk, text='U'); d.w((21, 4), (24, 4))
    d.v(r220, 28, 5.5, top=pkr); d.w((27, 4), (28, 4))
    d.at(jp, 19, 10); d.w((17, 4), (17, 10))
    av = d.nets(jp)['3']
    d.w((21, 10), (26, 10)); d.v(cavg, 24, 11.5, top=av)
    xs = d.h(ravg, 27.5, 10, left=av, text='U'); d.w((29, 10), (32, 10)); d.port(xs, (32, 10), 'R')
    q = pins(u4)
    d.at(u4[0], 24, 17, unit=u4[1]); d.w((jp, 2), (19, 16), (u4[0], q[0]))
    d.w((u4[0], q[2]), (28, 17), (28, 20), (20, 20), (20, 18), (u4[0], q[1])); d.port(deto, (28, 20), 'R')
    det = d.h(rbo, 30.5, 17, left=deto, text='U'); d.w((28, 17), (29, 17)); d.w((32, 17), (35, 17)); d.port(det, (35, 17), 'R')
