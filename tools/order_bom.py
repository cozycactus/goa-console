"""Console-wide order list from the nine board BOMs (sourcing.md): each board's BOM times the number of boards built,
grouped by MPN, with spares. Plain 0805 resistors (no MPN in the schematic) get the sourcing rule's Yageo
RC0805FR-07<value>L. DNP parts and mounting holes are left out; the jig's four strips are four of the 24, and the
OPA1656 A/B variant (test_jig_spec.md 4.2: 8 parts on each of two strips) is added as extra parts.
usage: python3 tools/order_bom.py   ->  order_bom.csv"""
import csv, math, os, re, collections

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
BOARDS = [('channel_strip', 'strip', 24), ('jack_board', 'strip jack', 24), ('group', 'group', 4),
          ('group_jack_board', 'group jack', 4), ('master', 'master', 1), ('master_jack_board', 'master jack', 1),
          ('psu', 'psu', 1), ('jig_master_stub', 'jig stub', 1), ('jig_load_board', 'jig load', 1)]
EXTRA = [('TI OPA1656IDR', 'OPA1656 (jig A/B variant)', 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'jig A/B', 16)]

def spares(fp, need):
    """Spares by kind: cheap SMD passives +10 % (at least 10), semis +5 % (at least 2), panel / THT parts +3 %
    (at least 1), electrolytics and film +5 % (at least 2)."""
    f = fp.split(':')[0]
    if f in ('Resistor_SMD', 'Capacitor_SMD', 'Inductor_SMD'): return max(10, math.ceil(need * 0.10))
    if f in ('Package_SO', 'Package_TO_SOT_SMD', 'Diode_SMD', 'Diode_THT', 'LED_THT', 'Relay_SMD'):
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

if __name__ == '__main__':
    main()
