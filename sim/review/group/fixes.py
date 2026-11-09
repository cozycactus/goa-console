"""Candidate fixes: (name, node1, node2, value) added to the deck."""
FOLLOW_IN = ('S_FIN', 'S_PWL', 'S_PWR', 'A_LIN', 'RTL_LIN', 'RTR_LIN')
def shunt(nodes, v, tag): return [(f'CFIX_{tag}_{n}', n, '0', v) for n in nodes]
FIX = {'none': [],
       'f10': shunt(FOLLOW_IN, '10p', 'a'),
       'f22': shunt(FOLLOW_IN, '22p', 'a'),
       'f33': shunt(FOLLOW_IN, '33p', 'a'),
       'f47': shunt(FOLLOW_IN, '47p', 'a'),
}
# recommended set: 10p at every follower + input on a pot wiper, 75R build-out between U2B (insert return buffer)
# and C13, R13 placed beside C13 (S_PRE MST 292 -> 121 mm)
REC = dict(extra=FIX['f10'] + [('RSER_U2B', 'SUB_RBUF', 'SUB_RBO', 75)], repin={('C13', '1'): 'SUB_RBO'}, mst={'S_PRE': 121})
REC47 = dict(extra=FIX['f10'] + [('RSER_U2B', 'SUB_RBUF', 'SUB_RBO', 47)], repin={('C13', '1'): 'SUB_RBO'}, mst={'S_PRE': 121})
FIX['rec'] = REC; FIX['rec47'] = REC47
def apply(cfg, fx):
    """The fix sets were written for group rev 0.1. MG4-MG8 are in the schematic since rev 0.2 (2026-10-24) and the
    drawn schematic leaves those nets unnamed, so on today's netlist use 'none': a set whose parts hang on nets the
    netlist no longer has would re-wire pins onto floating nodes and the deck finds no operating point."""
    f = FIX[fx]
    if fx != 'none':
        from groupdeck import pins, clean
        have = {clean(n) for n in pins.values()}
        new = set(f.get('repin', {}).values()) if isinstance(f, dict) else set()
        parts = f['extra'] if isinstance(f, dict) else f
        missing = sorted({n for _, a, b, _ in parts for n in (a, b) if n != '0' and n not in have and n not in new})
        if missing:
            raise SystemExit(f"fix set '{fx}' refers to nets not in group.net ({', '.join(missing)}): it was written "
                             "for group rev 0.1 and is applied in the schematic since rev 0.2; use 'none'")
    if isinstance(f, dict):
        cfg['extra'] = list(f['extra']); cfg['repin'] = dict(f.get('repin', {})); cfg['mst'] = dict(f.get('mst', {}))
    else: cfg['extra'] = list(f)
    return cfg

# ---- mg = the recommended set (docs/reviews/master_group_review.md MG4-MG7; post_amp / level_buffer / insert are shared with the
# master): rec + 47R post-amp build-out (C18 moves to S_FX) + insert return 1K + 100p (strip T8; U2 pin 5 on SUB_RETIN)
MGX = [('RPOST', 'S_FPOST', 'S_FX', 47), ('RIN_RET', 'SUB_RET', 'SUB_RETIN', 1000), ('CIN_RET', 'SUB_RETIN', '0', '100p'),
       ('RSER_U2B', 'SUB_RBUF', 'SUB_RBO', 75)]
MGREPIN = {('C13', '1'): 'SUB_RBO', ('C18', '1'): 'S_FX', ('U2', '5'): 'SUB_RETIN'}
LB = ('A_LIN', 'RTL_LIN', 'RTR_LIN')
FIX['mg'] = dict(extra=FIX['f10'] + MGX, repin=MGREPIN, mst={'S_PRE': 121})
# alternative with 22p in level_buffer(): worse here (U6B 44 deg, U8A/B 47 deg with +47 pF on every output)
FIX['mg22'] = dict(extra=shunt([n for n in FOLLOW_IN if n not in LB], '10p', 'a') + shunt(LB, '22p', 'b') + MGX,
                   repin=MGREPIN, mst={'S_PRE': 121})
