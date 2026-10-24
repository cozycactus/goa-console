"""Drawing fragments for the master_lib circuits (group and master schematics). A circuit function registers
schgen.frag(b, w, h, fn): fn(d) draws its parts with schdraw.Drawing calls in grid units from the fragment's
top-left corner; the block lays its fragments out in rows (schgen.flow) and puts any part no fragment drew in labelled
rows under them. Op-amp pins per unit: PP[unit] = (+, -, out); comparators of the LM2901 have their own (CPP)."""
PP = {1: (3, 2, 1), 2: (5, 6, 7)}
CPP = {1: (5, 4, 2), 2: (7, 6, 1), 3: (11, 10, 13), 4: (9, 8, 14)}


def pins(u, lm2901=False):
    return (CPP if lm2901 else PP)[u[1]]


def inv(d, src, out, u, rin, rf, cf, plus, rin_label=None):
    """Inverting stage (summer): src -> rin -> - input, rf // cf over the top, + to the net 'plus'.  24 x 13"""
    p = pins(u)
    d.at(u[0], 16, 9, mirror='x', unit=u[1])
    d.at(rin, 3.5, 8, rot=90, text='D'); d.w((0, 8), (rin, 1)); d.port(src, (0, 8)); d.w((rin, 2), (u[0], p[1]))
    d.w((9, 2), (9, 8))
    d.at(rf, 12.5, 5, rot=270, text='D'); d.w((9, 5), (rf, 2)); d.w((rf, 1), (20, 5))
    d.at(cf, 12.5, 2, rot=270, text='U'); d.w((9, 2), (cf, 2)); d.w((cf, 1), (20, 2))
    d.w((20, 2), (20, 9)); d.w((u[0], p[2]), (23, 9)); d.port(out, (23, 9), 'R')
    d.w((u[0], p[0]), (11, 10)); d.port(plus, (11, 10))


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
    """A signal line from the net 'start': ('s', ref) a series part (pin 1 upstream), ('g', ref) a part from the line
    to ground (pin 1 on the line); 'end' labels the far end. Returns its width (grid)."""
    d.port(start, (0, 2)); x = 0
    for kind, r in elems:
        if kind == 's':
            d.at(r, x + 3.5, 2, rot=90, text='U'); d.w((x, 2), (r, 1)); x += 5
        else:
            d.w((x, 2), (x + 3, 2)); d.at(r, x + 2, 3.5); x += 3
    if end: d.w((x, 2), (x + 3, 2)); d.port(end, (x + 3, 2), 'R'); x += 3
    return x


def chain_w(elems, end=True):
    return sum(5 if k == 's' else 3 for k, _ in elems) + (3 if end else 0) + 4


def pot(d, r, top, wiper):
    """A pot (pin 1 = ground end) drawn vertically: hot end up, wiper to the right.  12 x 9"""
    d.at(r, 3, 4, mirror='x'); d.w((r, 3), (3, 1)); d.port(top, (3, 1), 'U')
    d.w((r, 2), (8, 4)); d.port(wiper, (8, 4), 'R')


def pot2(d, r):
    """A dual pot, its pins labelled.  14 x 8"""
    d.at(r, 6, 4)
