"""Console-wide order list from the nine board BOMs (sourcing.md): each board's BOM times the number of boards built,
grouped by MPN, with spares. Plain 0805 resistors (no MPN in the schematic) get the sourcing rule's Yageo
RC0805FR-07<value>L. DNP parts and mounting holes are left out; the jig's four strips are four of the 24, and the
OPA1656 A/B variant (test_jig_spec.md 4.2: 8 parts on each of two strips) is added as extra parts.
usage: python3 tools/order_bom.py   ->  order_bom.csv
       python3 tools/order_bom.py phase1   ->  order_phase1.csv: the staged hardware test (test_jig_spec.md 1.1). Stage A:
       one strip + its jack board, merged with sample_order.md (a part on both lists is bought once, the larger number),
       the N1 op-amp swap, the bench-power lead; stage B: the jig stub, load board, jig ribbons and test fixtures; an
       optional second strip. Spares per stage, as the console list's rule."""
import csv, math, os, re, collections

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
BOARDS = [('channel_strip', 'strip', 24), ('jack_board', 'strip jack', 24), ('group', 'group', 4),
          ('group_jack_board', 'group jack', 4), ('master', 'master', 1), ('master_jack_board', 'master jack', 1),
          ('psu', 'psu', 1), ('jig_master_stub', 'jig stub', 1), ('jig_load_board', 'jig load', 1)]
EXTRA = [('TI OPA1656IDR', 'OPA1656 (jig A/B variant)', 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'jig A/B', 16),
         # CS11b: 40 bought for the 30 DRV135 couplers sorted into 15 pairs within 2 % (sim/review/cs11/drv_couplers.py)
         ('Panasonic ECE-A1EN100U', '10u NP 25V', 'Capacitor_THT:CP_Radial_D5.0mm_P2.00mm', 'pair-sorting stock', 10)]

def spares(fp, need):
    """Spares by kind: cheap SMD passives +10 % (at least 10), semis +5 % (at least 2), panel / THT parts +3 %
    (at least 1), electrolytics and film +5 % (at least 2)."""
    f = fp.split(':')[0]
    if f in ('Resistor_SMD', 'Capacitor_SMD', 'Inductor_SMD'): return max(10, math.ceil(need * 0.10))
    if f in ('Package_SO', 'Package_TO_SOT_SMD', 'Diode_SMD', 'Diode_THT', 'LED_THT', 'Relay_SMD') or 'LED_D' in fp:
        return max(2, math.ceil(need * 0.05))
    if f == 'Capacitor_THT': return max(2, math.ceil(need * 0.05))
    return max(1, math.ceil(need * 0.03))

def resistor_mpn(value):
    tok = value.split()[0]
    return f'Yageo RC0805FR-07{tok}L' if re.fullmatch(r'\d+[RKM]\d*', tok) else ''

def rows():
    for name, label, n in BOARDS:
        with open(os.path.join(ROOT, f'{name}_BOM.csv'), newline='') as f:
            for r in csv.DictReader(f):
                if r['DNP'] or r['Footprint'].startswith('MountingHole'): continue
                mpn = r['MPN'] or (resistor_mpn(r['Value']) if r['Footprint'] == 'Resistor_SMD:R_0805_2012Metric' else '')
                yield mpn, r['Value'], r['Footprint'], label, int(r['Qty']) * n, int(r['Qty'])
    for mpn, value, fp, label, q in EXTRA: yield mpn, value, fp, label, q, q

def main():
    g = collections.OrderedDict()
    for mpn, value, fp, label, q, per in rows():
        k = (mpn.split(' (')[0] or f'(no MPN) {value}', fp)        # one line per order code, whatever the note
        e = g.setdefault(k, dict(values=[], need=0, where=[], notes=[]))
        note = mpn[len(k[0]):].strip(' ()')
        if note and note not in e['notes']: e['notes'].append(note)
        if value not in e['values']: e['values'].append(value)
        e['need'] += q; e['where'].append(f'{label} {per}' if label == 'jig A/B' else f'{label} {q // per}x{per}' if q != per else f'{label} {per}')
    out = os.path.join(ROOT, 'order_bom.csv')
    with open(out, 'w', newline='') as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL)
        w.writerow(['Order', 'Need', 'Spares', 'MPN', 'Values', 'Footprint', 'Where (boards x per board)', 'Notes'])
        for (mpn, fp), e in sorted(g.items(), key=lambda kv: (kv[0][1], kv[0][0])):
            s = spares(fp, e['need'])
            w.writerow([e['need'] + s, e['need'], s, mpn, ' / '.join(e['values']), fp, ', '.join(e['where']), '; '.join(e['notes'])])
    print(f'{out}: {len(g)} lines, {sum(e["need"] for e in g.values())} parts needed')
    print('boards to fabricate:', ', '.join(f'{label} x{n}' for _, label, n in BOARDS))

# ---------------------------------------------------------------- phase 1 (staged hardware test)
# sample_order.md, by order code: (qty, check). A code that is also on the strip's BOM is bought once (the larger number:
# the samples are the build's parts, checked before they're soldered)
SAMPLES = [('Bourns PTB0143-2010BPA103', 'Fader, strip / group', 2, '1, 9'), ('Bourns PTB0144-2010BPA103', 'Fader, master', 1, '1'),
           ('Sifam LK111 01', 'Fader cap, black, white line', 3, '2'), ('Sifam LK110 tang 01 (RS 281-7197)', 'Fader cap, plain', 2, '2'),
           ('(rule) 8 x 1.2 mm slot fader cap, white / red / yellow', 'Fader cap, coloured trial', 6, '2'),
           ('C&K PVA2 EE H1 1.7N V2', 'Key switch', 4, '3'),
           ('Alpha RD901F-40-15R1-A10K', 'Pot, single A10K', 2, '4, 7'), ('Alpha RD901F-40-15R1-B10K-0CD', 'Pot, B10K detent', 1, '4, 7'),
           ('Alpha RD902F-40-15R1-A10K', 'Pot, dual A10K', 1, '4, 7'), ('ALPS RK09L1240015', 'Pan pot', 2, '5, 7'),
           ('Elma 021-3525', 'Knob, 1/4"', 3, '7'), ('Elma 021-3425', 'Knob, 6 mm', 1, '7'),
           ('Elma 040-3035', 'Knob cap red', 1, '7'), ('Elma 040-3015', 'Knob cap grey', 1, '7'), ('Elma 040-3045', 'Knob cap blue', 1, '7'),
           ('Elma 040-3055', 'Knob cap yellow', 1, '7'), ('Elma 040-3065', 'Knob cap green', 1, '7'), ('Elma 040-3025', 'Knob cap black', 1, '7'),
           ('Neutrik NJ6FD-V', 'Jack', 2, '6'), ('Kingbright WP3VEGW', 'Signal / OL LED', 5, '8'),
           ('Kingbright WP710A10ID', 'Panel LED red', 3, '8'), ('Kingbright WP710A10GD', 'Panel LED green', 3, '8'),
           ('Kingbright WP710A10YD', 'Panel LED yellow', 3, '8')]
# off-board parts per stage (offboard_bom.md codes; '(rule)' = any part meeting the rule): (code, what, A, B, B2, note)
OFFBOARD = [
    ('C&K PVGY', 'PV key cap grey', 8, 0, 0, 'strip: PRE x3, HPF, EQ, DIR, PAN, Phase (KC1); samples check 3'),
    ('C&K PVWH', 'PV key cap white', 3, 0, 0, 'routing L-R / 1-2 / 3-4'),
    ('C&K PVRD', 'PV key cap red', 2, 0, 0, 'PFL; one more for check 3'),
    ('C&K PVBK', 'PV key cap black', 2, 0, 0, 'ON; one more for check 3'),
    ('(rule) strip panel blank, cut only, from panels/strip.dxf', 'Panel, 1.5 mm aluminium', 1, 0, 0,
     'mechanical checks on the real board; the printed prototype waits for the fader law (panels/README.md)'),
    ('(rule) M3 F-F standoff 11.5 mm', 'Main-board standoff', 6, 0, 0, 'plus 6 M3 screws'),
    ('(rule) M3 F-F standoff 24.0 mm, metal', 'Jack-board standoff', 2, 0, 0, 'plus 2 M3 screws, 2 M3 star washers'),
    ('(rule) M7 washer 1.5 x ID 7.2 x OD < 11.2', 'Pot spacer washer', 14, 0, 0, ''),
    ('(rule) M9 washer 9.5 / 11 x 1.5', 'Pan pot spacer washer', 2, 0, 0, ''),
    ('(rule) 3.5 mm M3 spacer', 'Fader spacer', 2, 0, 0, 'plus 2 M3 fader screws'),
    ('(rule) 3 mm LED spacer 7.6 mm', 'LED spacer', 6, 0, 0, ''),
    ('(rule) 3-lead 3 mm LED spacer 7.2 mm, 2.0 pitch', 'LED spacer, WP3VEGW', 3, 0, 0, 'or a 2-hole one opened up'),
    ('Wurth 61203423021', '34-way IDC socket', 1, 6, 2,
     'A: a bench-power lead on the strip header (pins 30-31 -V, 32-34 +V, even 2-16 GND); B: 0.6 m and 3 m jig ribbons '
     '(strip, stub, load board each); B2: the second strip on both'),
    ('(rule) 34-way 1.27 mm flat cable, 28 AWG', '34-way flat cable, m', 1, 4, 0, 'B: 0.6 m wing ribbon + 3 m hum-test ribbon (test 4)'),
    ('Wurth 61201023021', '10-way IDC socket', 2, 0, 2, 'jack-board link'),
    ('(rule) 10-way 1.27 mm flat cable', '10-way flat cable, m', 1, 0, 0, 'one strip link is ~136 mm'),
    ('(rule) 6.3 mm insulated receptacle, blue', 'Spade receptacle', 2, 6, 2, 'ground spades to the bench / the ground bar'),
    ('(rule) 14 AWG stranded wire', '14 AWG wire, m', 1, 2, 0, ''),
    ('(rule) copper bar ~15 x 2 mm with 6.3 mm tabs, M4 lug', 'Ground bar (jig star point)', 0, 1, 0, 'test_jig_spec.md 1'),
    ('(rule) 100R 0.01 % matched pair', 'Test 14: CMR source pair', 1, 0, 0, 'test_jig_spec.md test 14 (a)'),
    ('(rule) 1K 1 %', 'Test 14: 1 kohm tip resistor', 1, 0, 0, 'test 14 (b)'),
    ('(rule) 1K 0.1 %', 'Test 13: leg loads', 0, 2, 0, 'test 13'),
    ('(rule) 10K 0.01 % matched pair', 'Test 13: common-mode sum', 0, 1, 0, 'test 13'),
    ('(rule) 0.1R 3 W', 'Test 2: spade-lead shunt', 0, 1, 0, 'test 2'),
    ('(rule) 1:1 audio isolation transformer', 'Test 2: ground injection', 0, 1, 0, 'test 2 (any 50 Hz-1 kHz 1:1)'),
]
N1_SWAP = ('TI OPA1656IDR', 'OPA1656 (N1 swap on strip 1)', 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 8)   # test_jig_spec.md 4.2
PHASE1_PCBS = [('channel_strip', 'strip main, 4 layers'), ('jack_board', 'strip jack board'),
               ('jig_master_stub', 'jig master stub'), ('jig_load_board', 'jig load board')]

def board_lines(name, label):
    with open(os.path.join(ROOT, f'{name}_BOM.csv'), newline='') as f:
        for r in csv.DictReader(f):
            if r['DNP'] or r['Footprint'].startswith('MountingHole'): continue
            mpn = r['MPN'] or (resistor_mpn(r['Value']) if r['Footprint'] == 'Resistor_SMD:R_0805_2012Metric' else '')
            yield (mpn.split(' (')[0] or f'(no MPN) {r["Value"]}', r['Footprint']), mpn, r['Value'], label, int(r['Qty'])

def phase1():
    stages = {'A': [('channel_strip', 'strip'), ('jack_board', 'strip jack')],
              'B': [('jig_master_stub', 'jig stub'), ('jig_load_board', 'jig load')],
              'B2': [('channel_strip', 'strip 2'), ('jack_board', 'strip 2 jack')]}
    g = collections.OrderedDict()
    def entry(k):
        return g.setdefault(k, dict(values=[], need={'A': 0, 'B': 0, 'B2': 0}, extra={'A': 0, 'B': 0, 'B2': 0},
                                    where=collections.Counter(), notes=[], board=False))
    for st, boards in stages.items():
        for name, label in boards:
            for k, mpn, value, lab, q in board_lines(name, label):
                e = entry(k); e['board'] = True; e['need'][st] += q; e['where'][lab] += q
                note = mpn[len(k[0]):].strip(' ()')
                if note and note not in e['notes']: e['notes'].append(note)
                if value not in e['values']: e['values'].append(value)
    k = (N1_SWAP[0], N1_SWAP[2]); e = entry(k); e['need']['A'] += N1_SWAP[3]; e['where']['N1 swap'] += N1_SWAP[3]
    if N1_SWAP[1] not in e['values']: e['values'].append(N1_SWAP[1])
    fp_of = {kk[0]: kk[1] for kk in g}
    for code, what, q, chk in SAMPLES:          # bought once: the larger of the strip's order and the sample count
        k = (code, fp_of.get(code, '(sample)')); e = entry(k)
        e['extra']['A'] = max(e['extra']['A'], q); e['where'][f'samples (check {chk})'] += q
        if what not in e['values']: e['values'].append(what)
    rows_ = []
    for (code, fp), e in g.items():
        orders = {}
        for st in ('A', 'B', 'B2'):
            n = e['need'][st]; o = n + (spares(fp, n) if n else 0)
            orders[st] = max(o, e['extra'][st])
        rows_.append([orders['A'], orders['B'], orders['B2'], code, ' / '.join(e['values']), fp, ', '.join(f'{w} {n}' for w, n in e['where'].items()), '; '.join(e['notes'])])
    for code, what, a, b, b2, note in OFFBOARD:
        rows_.append([a, b, b2, code, what, '(off-board)', 'offboard_bom.md / test_jig_spec.md', note])
    rows_.sort(key=lambda r: (r[5] == '(off-board)', r[5], r[3]))
    out = os.path.join(ROOT, 'order_phase1.csv')
    with open(out, 'w', newline='') as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL)
        w.writerow(['Stage A', 'Stage B', 'Stage B: 2nd strip (optional)', 'MPN / code', 'Values / what', 'Footprint',
                    'Where', 'Notes'])
        w.writerows(rows_)
    tot = lambda i: sum(r[i] for r in rows_ if r[5] != '(off-board)')
    print(f'{out}: {len(rows_)} lines; board parts to order: stage A {tot(0)}, stage B {tot(1)}, 2nd strip {tot(2)}')
    print('PCBs (order all in stage A, 5 of each, the fab minimum): ' + ', '.join(f'{lab} ({n})' for n, lab in PHASE1_PCBS))

if __name__ == '__main__':
    import sys
    phase1() if sys.argv[1:] == ['phase1'] else main()
