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
    d.h(rin, 3.5, 8, left=src, text='U' if rin.startswith('FB') else 'D'); d.w((0, 8), (2, 8)); d.port(src, (0, 8)); d.w((5, 8), (9, 8), (u[0], p[1]))
    d.w((9, 1), (9, 12 if rin2 else 8))
    d.h(rf, 12.5, 5, left=node, text='U'); d.w((9, 5), (11, 5)); d.w((14, 5), (20, 5))
    d.h(cf, 12.5, 1, left=node, text='U'); d.w((9, 1), (11, 1)); d.w((14, 1), (20, 1))
    d.w((20, 1), (20, 9)); d.w((u[0], p[2]), (23, 9)); d.port(out, (23, 9), 'R')
    if rin2:
        d.h(rin2, 3.5, 12, left=src2, text='D'); d.w((0, 12), (2, 12)); d.port(src2, (0, 12)); d.w((5, 12), (9, 12))
    if plus in ('GNDA', 'GNDD', 'GNDM'): d.w((u[0], p[0]), (12, 10), (12, 11)); ground(d, (12, 11), plus)
    else: d.w((u[0], p[0]), (11, 10)); d.port(plus, (11, 10))


def wiper_follower(d, src, out, u, cin, rsh, csh, rbo=None, final=None):
    """Follower on a pot wiper: src -> cin -> +, rsh and csh to ground; optional build-out rbo to 'final'.  24 x 10"""
    p = pins(u)
    d.at(u[0], 15, 4, unit=u[1], text='U')
    d.h(cin, 3.5, 3, left=src, text='U'); d.w((0, 3), (2, 3)); d.port(src, (0, 3)); d.w((5, 3), (u[0], p[0]))
    d.w((5, 3), (5, 4)); d.v(rsh, 5, 5.5, top=d.nets(cin)['2'] if d.nets(cin)['1'] == src else d.nets(cin)['1'], text='L')
    d.at(csh, 10.5, 4.5, text='L')
    d.w((u[0], p[2]), (19, 4), (19, 7), (12, 7), (u[0], p[1]))
    if rbo:
        d.h(rbo, 21.5, 4, left=d.nets(u[0])[str(p[2])], text='U'); d.w((19, 4), (20, 4))
        d.w((23, 4), (26, 4)); d.port(final, (26, 4), 'R')
    else:
        d.w((19, 4), (22, 4)); d.port(out, (22, 4), 'R')


def phones(d, src, u, cin, rsh, csh, buf, rout, rf, cf, rg, caps, out):
    """Headphone composite: wiper follower-style input, OPA1612 driving the LME49600 inside the loop, 2R2 out; the
    4K7 from the output (after the 2R2) and the 100p from the op-amp's own output to the - node, 2K2 to ground.  40 x 20"""
    p = pins(u); fin = d.nets(u[0])[str(p[0])]; fn = d.nets(u[0])[str(p[1])]; drv = d.nets(u[0])[str(p[2])]
    d.at(u[0], 16, 4, unit=u[1], text='U')
    d.h(cin, 3.5, 3, left=src, text='U'); d.w((0, 3), (2, 3)); d.port(src, (0, 3)); d.w((5, 3), (u[0], p[0]))
    d.w((5, 3), (5, 4)); d.v(rsh, 5, 5.5, top=fin, text='L'); d.at(csh, 11, 4.5, text='L')
    d.at(buf, 25, 4)                                                   # LME49600: in (2) left, out (4) right
    d.w((u[0], p[2]), (buf, 2))
    d.h(rout, 33.5, 4, left=d.nets(buf)['4'], text='U'); d.w((buf, 4), (32, 4)); d.w((35, 4), (39, 4)); d.port(out, (39, 4), 'R')
    d.w((u[0], p[1]), (13, 5), (13, 14))
    d.h(cf, 16.5, 10, left=fn, text='D'); d.w((13, 10), (15, 10)); d.w((18, 10), (20, 10), (20, 4))
    d.h(rf, 22.5, 14, left=fn, text='D'); d.w((13, 14), (21, 14)); d.w((24, 14), (37, 14), (37, 4))
    d.v(rg, 13, 15.5, top=fn, text='L')
    for i, c in enumerate(caps): d.at(c, 27 + 7 * i, 18, rot=180 if d.nets(c)['1'] in GROUNDS else 0)


def part(d, r, x, y, unit=None):
    """One part, its pins labelled (connectors, headers, single parts)."""
    d.at(r, x, y, unit=unit)



def diff(d, inn, inp, out, u, r1, r2, r3, r4, c0, c1, shunts=(), c0n=2):
    """Difference amplifier (re-inverter, balanced receiver): inn -> r1 -> -, r2 // c0 over the top; inp -> r3 -> +,
    r4 and c1 from + to ground. shunts: (ring cap, tip cap, tip 1M) of a receiver's inputs.  30 x 18"""
    p = pins(u)
    d.at(u[0], 22, 9, mirror='x', unit=u[1])
    d.at(r1, 10.5, 8, rot=90, text='U'); d.w((0, 8), (r1, 1)); d.port(inn, (0, 8)); d.w((r1, 2), (u[0], p[1]))
    d.w((14, 1), (14, 8))
    d.at(r2, 18.5, 5, rot=90, text='U'); d.w((14, 5), (r2, 1)); d.w((r2, 2), (26, 5))
    d.at(c0, 18.5, 1, rot=270 if c0n == 2 else 90, text='U'); d.w((14, 1), (c0, c0n)); d.w((c0, 3 - c0n), (26, 1))
    d.w((26, 1), (26, 9)); d.w((u[0], p[2]), (29, 9)); d.port(out, (29, 9), 'R')
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
    d.at(u[0], 18, 4, unit=u[1], text='U')
    d.at(cin, 3.5, 3, rot=90, text='U'); d.w((0, 3), (cin, 1)); d.port(src, (0, 3)); d.w((cin, 2), (u[0], p[0]))
    d.w((5, 3), (5, 4)); d.at(rsh, 5, 5.5, text='L'); d.at(csh, 11, 4.5, text='L')
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
    d.at(u[0], 8, 3, unit=u[1], text='U')
    d.w((0, 2), (u[0], p[0])); d.port(src, (0, 2))
    d.w((u[0], p[2]), (12, 3), (12, 6), (4, 6), (4, 4), (u[0], p[1]))
    d.w((12, 3), (15, 3)); d.port(out, (15, 3), 'R')
    if cap: d.at(cap, 2, 3.5, text='L')


def law_buffer(d, src, out, u, cap, parts):
    """The Delta's pan buffer (ED3344C, CS2 / CS2b): + on top, 1.22x (rf 2K2 // cf 22p out -> -, rg 10K - -> ground),
    rlaw 3K3 from the output back to the + input (the wiper); cap: a C from + to ground. parts: [rlaw, rf, rg, cf],
    filled when they are created (last, so no other ref moves).  16 x 14"""
    p = pins(u); rlaw, rf, rg, cf = parts
    d.at(u[0], 8, 3, unit=u[1], text='U')
    d.w((0, 2), (u[0], p[0])); d.port(src, (0, 2))
    d.w((u[0], p[2]), (12, 3)); d.w((12, 3), (15, 3)); d.port(out, (15, 3), 'R')
    d.at(rf, 8, 7, rot=90, text='U'); d.w((12, 3), (12, 7), (rf, 2)); d.w((rf, 1), (4, 7), (4, 4), (u[0], p[1]))
    d.at(cf, 8, 9, rot=90, text='D'); d.w((6.5, 7), (6.5, 9), (cf, 1)); d.w((cf, 2), (9.5, 9), (9.5, 7))
    d.at(rg, 4, 8.5, text='L'); d.gnd((rg, 2))
    d.at(rlaw, 7.5, -2, rot=90, text='U'); d.w((12, 3), (12, -2), (rlaw, 2)); d.w((rlaw, 1), (2, -2), (2, 2))
    if cap: d.at(cap, 2, 3.5, text='L')


def dim(d, src, dst, r, sw, unit):
    """C/Room dim, one side (CS7): r from src to dst with one pole of the DIM key across it; released, the pole shorts
    r (full level), latched it leaves r in (-20 dB into the C/ROOM pot). The latched throw is unconnected.  16 x 8"""
    com, rel = (2, 3) if unit == 1 else (5, 6)
    d.at(r, 7.5, 6, rot=90, text='D'); d.w((0, 6), (r, 1)); d.port(src, (0, 6)); d.w((r, 2), (15, 6)); d.port(dst, (15, 6), 'R')
    d.at(sw, 7.5, 2, unit=unit, text='U'); d.w((sw, com), (3, 2), (3, 6)); d.w((sw, rel), (12, 3), (12, 6))


def rx_buffers(d, tip, ring, tb, rb, ut, ur, st, sr, rt, rr, ot, orr, ct, cr):
    """Balanced receiver's input followers (docs/studies/ground_study.md G3b): per leg 1M to ground, 220R, 100p at the + input, a
    unity follower, a 100R build-out to the bridge.  32 x 17"""
    for src, dst, u, rs, rbias, cs, ro, y in ((tip, tb, ut, st, rt, ct, ot, 0), (ring, rb, ur, sr, rr, cr, orr, 9)):
        p = pins(u)
        d.at(rs, 7.5, y + 2, rot=90, text='U'); d.w((0, y + 2), (rs, 1)); d.port(src, (0, y + 2))
        d.at(rbias, 3, y + 3.5, text='L'); d.at(cs, 11, y + 3.5, text='L')
        d.at(u[0], 18, y + 3, unit=u[1], text='U'); d.w((rs, 2), (u[0], p[0]))
        d.w((u[0], p[2]), (22, y + 3), (22, y + 6), (14, y + 6), (14, y + 4), (u[0], p[1]))
        d.at(ro, 25.5, y + 3, rot=90, text='U'); d.w((22, y + 3), (ro, 1))
        d.w((ro, 2), (30, y + 3)); d.port(dst, (30, y + 3), 'R')


def insert(d, src, send, rr, dst, rs, cin, rin, rprot, cprot, u, rbo, cout, rout):
    """Insert: send through 75R; return: coupler, 47K, 1K + 100p, follower, 75R build-out, coupler, 47K.  39 x 12"""
    d.at(rs, 3.5, 1, rot=90); d.w((0, 1), (rs, 1)); d.port(src, (0, 1)); d.w((rs, 2), (8, 1)); d.port(send, (8, 1), 'R')
    d.at(cin, 3.5, 6, rot=90, text='U'); d.w((0, 6), (cin, 1)); d.port(rr, (0, 6))
    d.w((cin, 2), (7, 6)); d.at(rin, 7, 7.5, text='L')
    d.at(rprot, 10.5, 6, rot=90, text='U'); d.w((7, 6), (rprot, 1))
    d.at(cprot, 14, 7.5, text='L')
    p = pins(u)
    d.at(u[0], 20, 7, unit=u[1], text='U'); d.w((rprot, 2), (u[0], p[0]))
    d.w((u[0], p[2]), (24, 7), (24, 10), (16, 10), (16, 8), (u[0], p[1]))
    d.at(rbo, 26.5, 7, rot=90, text='U'); d.w((24, 7), (rbo, 1))
    d.at(cout, 31.5, 7, rot=90, text='U'); d.w((rbo, 2), (cout, 1))
    d.w((cout, 2), (38, 7)); d.port(dst, (38, 7), 'R'); d.at(rout, 36, 8.5)


def drv134(d, inp, op, on, u, cs_p, cs_n, cv_p, cv_n, rs=()):
    """DRV134 line driver: 10u NP from each Sense pin to its output, supply decoupling beside; rs: the CS4c resistors
    (output pin -> rs -> 10u), drawn in the loop ahead of each 10u.  30 x 15, 35 x 15 with rs"""
    k = 5 if rs else 0
    d.at(u, 8, 8)
    d.w((0, 8), (u, 4)); d.port(inp, (0, 8))
    d.w((u, 3), (3, 10), (3, 11)); d.gnd((3, 11))
    for (c, r, pin, sp, y, ys, side) in ((cs_p, rs[0] if rs else None, 8, 7, 4, 7, 'U'), (cs_n, rs[1] if rs else None, 1, 2, 12, 9, 'D')):
        d.at(c, 15.5 + k, y, rot=90, text=side)
        if r:
            d.at(r, 15.5, y, rot=90, text=side); d.w((u, pin), (13, (6 if pin == 8 else 10)), (13, y), (r, 1)); d.w((r, 2), (c, 1))
        else: d.w((u, pin), (13, (6 if pin == 8 else 10)), (13, y), (c, 1))
        d.w((u, sp), (18 + k, ys)); d.w((c, 2), (18 + k, y), (18 + k, ys)); d.w((18 + k, ys), (21 + k, ys))
        d.port(op if pin == 8 else on, (21 + k, ys), 'R')
    d.at(cv_p, 28 + k, 5.5); d.at(cv_n, 33 + k, 5.5, rot=180)


def relay(d, k, rcoil, dfly, nc_net):
    """G6K-2F-Y mute relay: coil from +VBUS through rcoil, flyback diode across the coil, driver at the bottom;
    contacts labelled (NO = driver side, COM = connector side, NC grounded).  24 x 15"""
    d.at(k, 9, 8)
    d.at(rcoil, 5, 2.5); d.w((rcoil, 1), (5, 0)); d.port('+VBUS', (5, 0), 'U'); d.w((rcoil, 2), (k, 1))
    d.at(dfly, 1, 8, rot=270, text='L'); d.w((dfly, 1), (1, 5), (k, 1)); d.w((dfly, 2), (1, 11), (k, 8))
    d.w((k, 8), (5, 13)); d.port('RLY_DRV', (5, 13), 'D')
    if True:                                        # NC contacts to ground: lifted clear of the contact labels, one symbol
        (x2, y2), (x7, y7) = d.pin(k, 2), d.pin(k, 7)
        g = lambda x, y: ((x - d.ox) / 2.54, (y - d.oy) / 2.54 - 4)
        d.w((k, 2), g(x2, y2), g(x7, y7)); d.w((k, 7), g(x7, y7)); d.gnd(g(x7, y7), nc_net, 'U')


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
    """An IC's power unit with its two decouplers (labels and ground symbols).  16 x 10"""
    d.at(u[0], 3, 5, unit=u[1]); d.at(cp, 7, 5); d.at(cn, 12, 5, rot=180)


def chain(d, start, elems, end=None, flag=None):
    """A signal line from the net 'start': ('s', ref) a series part, ('g', ref) a part from the line to its other net
    (ground or a rail, drawn down from the line); parts are turned by their nets. 'end' labels the far end."""
    d.port(start, (0, 2)); x = 0; net = start
    for i, (kind, r) in enumerate(elems):
        if kind == 's':
            val = next(p['value'] for p in d.parts if p['ref'] == r); pad = max(0, int(0.45 * len(val) / 2 - 1.5))
            led = next(p['key'] for p in d.parts if p['ref'] == r) == 'LED'    # its light arrows rise into texts above
            nxt = d.h(r, x + pad + 3.5, 2, left=net, text=None if led else 'U'); d.w((x, 2), (x + pad + 2, 2))
            if pad: d.w((x + pad + 5, 2), (x + 2 * pad + 5, 2))
            x += 5 + 2 * pad; net = nxt
        else:
            d.w((x, 2), (x + 2, 2)); d.v(r, x + 2, 3.5, top=net)
            x += 2
            if i + 1 < len(elems):                       # room for the texts
                gap = max(4, int(0.45 * len(next(p['value'] for p in d.parts if p['ref'] == r))) + 2)
                d.w((x, 2), (x + gap, 2)); x += gap
    if flag: d.w((x, 2), (x + 3, 2)); d.at(flag, x + 2, 2); x += 3          # PWR_FLAG on the end node
    if end: d.w((x, 2), (x + 3, 2)); d.port(end, (x + 3, 2), 'R'); x += 3
    return x


def chain_w(elems, end=True):
    return sum(5 if k == 's' else 6 for k, _ in elems) + (3 if end else 0) + 5


def pot(d, r, top, wiper):
    """A pot (pin 1 = ground end) drawn vertically: hot end up, wiper to the right.  12 x 9"""
    val = next(p['value'] for p in d.parts if p['ref'] == r); x = max(3, int(0.45 * len(val)) + 2)
    d.at(r, x, 4, mirror='x', text='L'); d.w((r, 3), (x, 1)); d.port(top, (x, 1), 'U')
    d.w((r, 2), (x + 5, 4)); d.port(wiper, (x + 5, 4), 'R')


def pot2(d, r):
    """A dual pot: wipers up, the track ends down, each on a stub to its label or ground.  24 x 12"""
    val = next(p['value'] for p in d.parts if p['ref'] == r)
    d.at(r, max(11, round(6 + 0.45 * len(val))), 5); n = d.nets(r)
    for pn, net in n.items():
        x, y = d.pin(r, pn); gx = (x - d.ox) / 2.54; gy = (y - d.oy) / 2.54
        up = gy < 5; ey = gy - 2 if up else gy + 2
        d.w((gx, gy), (gx, ey))
        if net in GROUNDS: d.gnd((gx, ey), net, 'U' if up else 'D')
        else: d.port(net, (gx, ey), 'U' if up else 'D')


GROUNDS = ('GNDA', 'GNDD', 'GNDM', 'PHONESGND')


def ground(d, pt, net):
    """A ground symbol (GNDM / PHONESGND are project power symbols that show their name)."""
    d.gnd(pt, net)


def comparators(d, units, out=None):
    """Comparators stacked 8 grid apart, each input wired to its label (or a ground symbol); out: the shared output
    net of a wired-AND pair, joined on a vertical. units: [((ref, unit), lm2901)].  18 x 8 per unit"""
    for k, (u, lm) in enumerate(units):
        y = 4 + 8 * k; p = pins(u, lm); n = d.nets(u[0])
        d.at(u[0], 8, y, unit=u[1])
        for pn, yy in ((p[0], y - 1), (p[1], y + 1)):
            net = n[str(pn)]
            if net in GROUNDS: d.w((u[0], pn), (2, yy)); d.gnd((2, yy), net, 'L')
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
    for (unit, s, dd, c), y in ((a, 2), (b, 8)):
        sx = d.pins_of('DG', unit)[str(s)][0]
        d.at(u, 7, y, mirror='y' if sx > 0 else None, unit=unit)
        n = d.nets(u)
        d.w((u, s), (1, y)); d.port(n[str(s)], (1, y))
        d.w((u, c), (7, y + 3), (3, y + 3)); d.port(n[str(c)], (3, y + 3))
    d.w((u, a[2]), (12, 2), (12, 8), (u, b[2])); d.w((12, 2), (15, 2)); d.port(d.nets(u)[str(a[2])], (15, 2), 'R')


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
    d.h(ra, 3.5, 8, left=other(ra), text='D'); d.w((0, 8), (2, 8)); d.port(other(ra), (0, 8)); d.w((5, 8), (9, 8), (u[0], p[1]))
    d.h(rb, 3.5, 12, left=other(rb), text='D'); d.w((0, 12), (2, 12)); d.port(other(rb), (0, 12)); d.w((5, 12), (9, 12))
    d.w((9, 0), (9, 12))
    d.h(cf, 12.5, 0, left=node, text='U'); d.w((9, 0), (11, 0)); d.w((14, 0), (20, 0))
    d.at(trim, 11.5, 5, rot=270); d.w((9, 5), (trim, 3)); d.w((trim, 2), (11.5, 7), (9, 7))
    rg = d.nets(trim)['1']
    d.h(rfx, 15.5, 5, left=rg, text='U'); d.w((trim, 1), (14, 5)); d.w((17, 5), (20, 5))
    d.w((20, 0), (20, 9)); d.w((u[0], p[2]), (23, 9)); d.port(out, (23, 9), 'R')
    d.w((u[0], p[0]), (12, 10), (12, 11)); ground(d, (12, 11), n[str(p[0])])


def peak(d, u3, dpk, rpk, cpk, c22, r330, r220, r10, dcl, ravg, cavg, jp, u4, rbo):
    """Meter detector: U3 + diode precision peak (220R / 1u, 330K / 220K bleed), the RC average, the PEAK / AVG jumper,
    the U4 follower and its 470R build-out to DET; R10K from DETO and the clamp diode close U3's loop.  38 x 19"""
    p = pins(u3); n = d.nets(u3[0]); x2, node, u3o = n[str(p[0])], n[str(p[1])], n[str(p[2])]
    d.at(u3[0], 8, 4, unit=u3[1], text='U')
    d.w((0, 3), (u3[0], p[0])); d.port(x2, (0, 3))
    d.w((u3[0], p[1]), (4, 5), (4, 12))
    deto = d.nets(r10)['1'] if d.nets(r10)['2'] == node else d.nets(r10)['2']
    d.h(r10, 1.5, 9, left=deto, text='D'); d.w((-2, 9), (0, 9)); d.port(deto, (-2, 9)); d.w((3, 9), (4, 9))
    d.h(c22, 7.5, 7, left=node, text='D'); d.w((4, 7), (6, 7)); d.w((9, 7), (13, 7))
    d.h(dcl, 8, 12, left=node); d.w((4, 12), (6.5, 12)); d.w((9.5, 12), (13, 12))
    d.w((u3[0], p[2]), (13, 4), (13, 12))
    pk1 = d.h(dpk, 15.5, 4, left=u3o, text='U'); d.w((13, 4), (14, 4))
    pk = d.h(rpk, 19.5, 4, left=pk1, text='U'); d.w((17, 4), (18, 4))
    d.v(cpk, 23, 5.5, top=pk); pkr = d.h(r330, 25.5, 4, left=pk, text='U'); d.w((21, 4), (24, 4))
    d.v(r220, 28, 5.5, top=pkr); d.w((27, 4), (28, 4))
    d.at(jp, 19, 11, text='R'); d.w((17, 4), (17, 11))
    av = d.nets(jp)['3']
    d.w((21, 11), (26, 11)); d.v(cavg, 24, 12.5, top=av)
    xs = d.h(ravg, 30.5, 11, left=av, text='D'); d.w((26, 11), (29, 11)); d.w((32, 11), (35, 11)); d.port(xs, (35, 11), 'R')
    q = pins(u4)
    d.at(u4[0], 30, 18, unit=u4[1], text='U'); d.w((jp, 2), (19, 17), (u4[0], q[0]))
    d.w((u4[0], q[2]), (35, 18), (35, 21), (26, 21), (26, 19), (u4[0], q[1])); d.port(deto, (35, 21), 'R')
    det = d.h(rbo, 37.5, 18, left=deto, text='U'); d.w((35, 18), (36, 18)); d.w((39, 18), (42, 18)); d.port(det, (42, 18), 'R')


def spare(d, u):
    """An unused op-amp half: + to ground, output tied to -.  14 x 8"""
    p = pins(u); n = d.nets(u[0])
    d.at(u[0], 8, 3, unit=u[1], text='U')
    d.w((u[0], p[0]), (2, 2), (2, 3)); ground(d, (2, 3), n[str(p[0])])
    d.w((u[0], p[2]), (12, 3), (12, 6), (4, 6), (4, 4), (u[0], p[1]))


def bar(d, q, leds, cmps, per=10):
    """Meter LED string: the PNP current source on top (emitter up, collector into the string), LEDs down to -VM;
    comparator k beside the anode of LED k, its output pulling that node; + inputs on one DET line per column.
    per: LEDs per column; a longer string continues at the top of the next column, the node between joined by its
    label.  26 x 93 (per=10), 58 x 53 (per=5)"""
    n = d.nets(q)
    d.at(q, 17, 3, mirror='x'); d.w((q, 3), (18, -1), (21, -1)); d.port(n['3'], (21, -1), 'R')
    d.w((q, 1), (13, 3)); d.port(n['1'], (13, 3))
    y0 = 9; d.w((q, 2), (18, y0)); d.w((q, 4), (19, 6), (18, 6))
    det = d.nets(cmps[0][0])[str(pins(cmps[0], True)[0])]
    for c in range(0, len(leds), per):
        X = 32 * (c // per); col = list(zip(leds, cmps))[c:c + per]
        if c:                                                    # the string's node from the previous column, by label
            d.port(d.nets(col[0][0])['2'], (X + 18, y0 - 2), 'U'); d.w((X + 18, y0 - 2), (X + 18, y0))
        for i, (led, u) in enumerate(col):
            y = y0 + 8 * i; p = pins(u, True); nu = d.nets(u[0])
            d.at(u[0], X + 8, y, unit=u[1])
            d.w((u[0], p[0]), (X + 3, y - 1)); d.w((u[0], p[1]), (X, y + 1)); d.port(nu[str(p[1])], (X, y + 1))
            d.w((u[0], p[2]), (X + 18, y))
            node = d.nets(led)['2']; d.v(led, X + 18, y + 4, top=node)
            d.w((X + 18, y), (X + 18, y + 2.5)); d.w((X + 18, y + 5.5), (X + 18, y + 8))
        yl = y0 + 8 * (len(col) - 1)
        d.w((X, y0 - 3), (X + 3, y0 - 3), (X + 3, yl - 1)); d.port(det, (X, y0 - 3))
        d.port(d.nets(col[-1][0])['1'], (X + 18, yl + 8), 'D')


def vl_supply(d, r, dz, c, ds, flag):
    """+5VL from +VA: 4K7, BZX84C5V1 and 1u to GNDD, BAT54W back to +VA, PWR_FLAG.  30 x 9"""
    d.port('+VA', (0, 4)); d.h(r, 3.5, 4, left='+VA', text='U'); d.w((0, 4), (2, 4)); d.w((5, 4), (31, 4))
    d.port('+5VL', (31, 4), 'R')
    d.at(dz, 7, 5.5, rot=270); d.gnd((dz, 1), 'GNDD')
    d.v(c, 14, 5.5, top='+5VL'); d.gnd((c, 2), 'GNDD')
    d.at(ds, 21, 2.5, rot=270); d.w((ds, 3), (21, 0)); d.port('+VA', (21, 0), 'U')
    d.at(flag, 28, 4)


def dg_supply(d, u, x, y):
    """A DG413's supply unit at (x, y): pins labelled, GND taken left on a stub, clear of the V- label beside it."""
    d.at(u, x, y, unit=5); d.w((u, 5), (x, y + 6), (x - 2, y + 6), (x - 2, y + 7)); d.gnd((x - 2, y + 7), 'GNDD')
    n = d.nets(u)                                   # short stubs: a label straight on a pin runs into its number
    for pn, dy, side in (('13', -1, 'U'), ('12', -1, 'U'), ('4', 1, 'D')):
        px, py = d.pin(u, pn); gx, gy = (px - d.ox) / 2.54, (py - d.oy) / 2.54
        d.w((gx, gy), (gx, gy + dy)); d.port(n[pn], (gx, gy + dy), side)


def dg_power(d, u, caps):
    """A DG413's supply unit (pins labelled) with its decouplers.  24 x 14"""
    dg_supply(d, u[0], 5, 7)
    for i, c in enumerate(caps): d.at(c, 10 + 5 * i, 7, rot=180 if d.nets(c)['2'] not in GROUNDS else 0)


def power_entry(d, j, d1, d2, tab, nts, flags=None):
    """PSU terminal (pin 1 chassis, 2-3 +VBUS, 4-5 GNDA, 6-7 -VBUS), SS54 reverse clamps, the M4 star tab on GNDA
    and the net ties from GNDA to each other ground.  58 x 26"""
    d.at(j, 4, 8, mirror='y')
    d.w((j, 1), (8, 5)); d.port('CHASSIS', (8, 5), 'R')
    d.w((j, 3), (12, 7), (12, 2)); d.w((j, 2), (12, 6)); d.w((12, 2), (30, 2)); d.port('+VBUS', (30, 2), 'R')
    d.w((j, 5), (14, 9), (14, 8)); d.w((j, 4), (44, 8)); d.w((30, 8), (30, 9)); d.gnd((30, 9))
    d.w((j, 7), (12, 11), (12, 10)); d.w((j, 6), (12, 10)); d.w((12, 11), (12, 14), (26, 14)); d.port('-VBUS', (26, 14), 'R')
    d.v(d1, 16, 5, top='+VBUS'); d.w((16, 2), (16, 3.5)); d.w((16, 6.5), (16, 8))
    d.v(d2, 16, 11, top='GNDA'); d.w((16, 8), (16, 9.5)); d.w((16, 12.5), (16, 14))
    d.at(tab, 24, 11); d.w((22, 8), (tab, 1))
    fl = flags or {}
    for net, pt in (('+VBUS', (21, 2)), ('-VBUS', (21, 14)), ('GNDA', (38, 8))):
        if net in fl: d.at(fl[net], *pt)
    d.w((44, 8), (44, 8 + 5 * (len(nts) - 1)))
    for i, nt in enumerate(nts):
        y = 8 + 5 * i; other = d.nets(nt)['2']
        d.at(nt, 46, y, text='R'); d.w((44, y), (nt, 1))
        d.w((nt, 2), (57, y))
        if other in GROUNDS: d.w((57, y), (57, y + 1)); d.gnd((57, y + 1), other)
        else: d.port(other, (57, y), 'R')
        if other in fl: d.at(fl[other], 54, y)


def flags(d, refs, per=7):
    """PWR_FLAGs in rows, each on a short wire to its power symbol or label.  5 x 7 per flag"""
    for i, r in enumerate(refs):
        x, y = 2 + 5 * (i % per), 2 + 7 * (i // per); net = d.nets(r)['1']
        d.at(r, x, y); d.w((x, y), (x, y + 2))
        if net in GROUNDS: ground(d, (x, y + 2), net)
        else: d.port(net, (x, y + 2), 'D')


def header(d, r, x, y, stub=3):
    """A connector with every pin on a short stub to a horizontal label (left pins left, right pins right); a run of
    neighbouring pins on one net is joined on a vertical and labelled once (grounds get one symbol)."""
    d.at(r, x, y); cx = d.xy(x, y)[0]; n = d.nets(r)
    G = 2.54; side = {'L': [], 'R': []}
    for pn in n:
        px, py = d.pin(r, pn); side['L' if px < cx else 'R'].append((py, px, pn))
    for s, pins_ in side.items():
        pins_.sort(); runs = []
        for py, px, pn in pins_:
            if runs and runs[-1][0] == n[pn] and abs(py - runs[-1][1][-1][0] - G) < 0.01: runs[-1][1].append((py, px, pn))
            else: runs.append((n[pn], [(py, px, pn)]))
        far = int(max([len(n_) for n_, _ in runs if n_ not in GROUNDS + ('NC',)] or [0]) * 0.45 + 2.5)
        for net, ps in runs:
            if net == 'NC': continue                     # left bare: the builder puts its no-connect flag on the pin
            gx = lambda px: (px - cx) / G + x + (-stub if s == 'L' else stub)
            for py, px, pn in ps: d.w((r, pn), (gx(px), (py - d.oy) / G))
            ex, y0, y1 = gx(ps[0][1]), (ps[0][0] - d.oy) / G, (ps[-1][0] - d.oy) / G
            if len(ps) > 1: d.w((ex, y0), (ex, y1))
            if net in GROUNDS:
                gx = ex - far if s == 'L' else ex + far; d.w((ex, y0), (gx, y0)); d.gnd((gx, y0), net, s)
            else: d.port(net, (ex, y0), s)


def grounds(d, nt, tab, rgc):
    """A module's ground star: the GNDA-GNDD net tie, the ground spade on GNDA and the 10R to the GCANCEL line.  22 x 10"""
    d.at(nt, 5, 2); d.w((1, 2), (nt, 1)); d.w((1, 2), (1, 3)); d.gnd((1, 3))
    d.w((nt, 2), (10, 2), (10, 3)); d.gnd((10, 3), 'GNDD')
    d.at(tab, 5, 7); d.w((tab, 1), (3, 8)); d.gnd((3, 8))
    top = d.v(rgc, 15, 4, top='GCANCEL'); d.w((15, 1), (15, 2.5)); d.port('GCANCEL', (15, 1), 'U')
    d.w((15, 5.5), (15, 6)); d.gnd((15, 6))


def select(d, jps, common):
    """Solder jumpers from one common node (a vertical line) to their buses, one per row.  16 x 16"""
    d.port(common, (0, 2)); d.w((0, 2), (3, 2), (3, 2 + 4 * (len(jps) - 1)))
    for i, jp in enumerate(jps):
        y = 2 + 4 * i; d.at(jp, 7, y); d.w((3, y), (jp, 1)); d.w((jp, 2), (12, y)); d.port(d.nets(jp)['2'], (12, y), 'R')
