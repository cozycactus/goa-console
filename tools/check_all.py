"""Every project check in one run, without changing a tracked file (netlists, reports and panel outputs go to a temp
folder). Plain Python 3:
  python3 tools/check_all.py [--full]          (--full adds the overload / signal sims, ~3 min)
Per board: KiCad netlist vs its intended JSON (verify.py), pins vs footprint pads (check_fp.py), ERC (0 errors), parity
DRC (0 violations, footprint-internal KNOWN items of fab_out.py aside, 0 parity issues), footprint-symbol links
(check_links.py). Then: sim_netlist (strip + jack board through the ribbon), sim_console (the whole console),
netrules_test (every DRC rule fires), route_check_test (the post-route checker finds its planted faults),
route_check on every board (0 ERR), panel_fab's checks; --full: sim/review/gaps/ol.py and
sim/review/cs1/ol_multi.py --quick (the red from a negative and a positive pulse). Prints one line per check and a summary; exit 1 on any FAIL."""
import json, os, re, subprocess, sys, tempfile, time

TOOLS = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(TOOLS)
KC = os.environ.get('KC', '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli')
KPY = os.environ.get('KPY', '/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3')
VPY = os.path.join(ROOT, '.venv', 'bin', 'python')
BOARDS = ['channel_strip', 'jack_board', 'group', 'group_jack_board', 'master', 'master_jack_board',
          'jig_master_stub', 'jig_load_board', 'psu']
sys.path.insert(0, TOOLS)
from fab_out import is_known

results = []
def run(cmd, timeout=1800):
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT, timeout=timeout)
    return r.returncode, r.stdout + r.stderr
def report(name, ok, detail):
    results.append((name, ok)); print(f'{"pass" if ok else "FAIL"}  {name:42s} {detail}', flush=True)

def main():
    full = '--full' in sys.argv
    tmp = tempfile.mkdtemp(prefix='check_all_'); t0 = time.time()
    for b in BOARDS:
        sch, pcb = os.path.join(ROOT, b + '.kicad_sch'), os.path.join(ROOT, b + '.kicad_pcb')
        net = os.path.join(tmp, b + '.net')
        run([KC, 'sch', 'export', 'netlist', '-o', net, sch])
        intended = os.path.join(ROOT, b + '_intended.json')
        if os.path.exists(intended):
            code, out = run([VPY, os.path.join(TOOLS, 'verify.py'), net, intended])
            m = re.search(r'pins checked: (\d+)\s+mismatches: (\d+)\s+unexpected pins: (\d+)', out)
            report(f'{b}: netlist vs intended', code == 0 and m and m.group(2) == '0' and m.group(3) == '0',
                   m.group(0) if m else out.strip()[-120:])
        code, out = run(['python3', os.path.join(TOOLS, 'check_fp.py'), net, ROOT])
        m = re.search(r'components checked: (\d+)\s+problems: (\d+)', out)
        report(f'{b}: pins vs footprints', bool(m) and m.group(2) == '0', m.group(0) if m else out.strip()[-120:])
        erc = os.path.join(tmp, b + '_erc.json')
        run([KC, 'sch', 'erc', '--format', 'json', '--severity-all', '-o', erc, sch])
        e = json.load(open(erc)); nerc = sum(len(s.get('violations', [])) for s in e.get('sheets', []))
        report(f'{b}: ERC', nerc == 0, f'{nerc} violations')
        drc = os.path.join(tmp, b + '_drc.json')
        run([KC, 'pcb', 'drc', '--format', 'json', '--schematic-parity', '--severity-all', '-o', drc, pcb])
        d = json.load(open(drc))
        other = [v for v in d.get('violations', []) if not is_known(b, v)]
        par = d.get('schematic_parity', [])
        report(f'{b}: parity DRC', not other and not par,
               f'{len(d.get("violations", []))} violations ({len(d.get("violations", [])) - len(other)} known), {len(par)} parity, '
               f'{len(d.get("unconnected_items", []))} unrouted')
        code, out = run([KPY, os.path.join(TOOLS, 'check_links.py'), b])
        m = re.search(r'(\d+) / (\d+) symbols linked', out)
        report(f'{b}: footprint links', bool(m) and m.group(1) == m.group(2), m.group(0) if m else out.strip()[-120:])
        code, out = run([KPY, os.path.join(TOOLS, 'route_check.py'), pcb])
        m = re.findall(r'(\d+) ERR, (\d+) WARN', out)
        report(f'{b}: route_check', bool(m) and m[-1][0] == '0', f'{m[-1][0]} ERR, {m[-1][1]} WARN' if m else out.strip()[-120:])
    sn = os.path.join(tmp, 'channel_strip.net'), os.path.join(tmp, 'jack_board.net')
    code, out = run(['python3', os.path.join(TOOLS, 'sim_netlist.py'), *sn])
    m = re.search(r'(\d+)/(\d+) checks passed', out); report('sim_netlist (strip + jack board)', bool(m) and m.group(1) == m.group(2), m.group(0) if m else out.strip()[-120:])
    code, out = run(['python3', os.path.join(TOOLS, 'sim_console.py')])
    m = re.search(r'(\d+)/(\d+) checks passed', out); report('sim_console (whole console)', bool(m) and m.group(1) == m.group(2), m.group(0) if m else out.strip()[-120:])
    code, out = run([KPY, os.path.join(TOOLS, 'netrules_test.py')])
    last = [l for l in out.splitlines() if 'rules fire' in l or 'NOT FIRING' in l]
    report('netrules_test (every DRC rule fires)', code == 0 and 'all rules fire' in out, last[-1] if last else out.strip()[-120:])
    code, out = run([KPY, os.path.join(TOOLS, 'route_check_test.py')])
    m = re.search(r'expected faults found: (\d+) of (\d+) ; known-good cases flagged: (\d+)', out)
    report('route_check_test (planted faults)', code == 0 and bool(m), m.group(0) if m else out.strip()[-120:])
    code, out = run([VPY, os.path.join(TOOLS, 'panel_fab.py'), os.path.join(tmp, 'panels')])
    probs = re.findall(r'(\w+): .*?; (\d+) problems', out)
    report('panel_fab checks', code == 0 and probs and all(p == '0' for _, p in probs), ', '.join(f'{k} {p}' for k, p in probs) or out.strip()[-120:])
    if full:
        code, out = run(['python3', os.path.join(ROOT, 'sim', 'review', 'gaps', 'ol.py')], timeout=900)
        m = re.search(r'1000 Hz: red\s+([\d.]+) dBu, green\s+([-\d.]+) dBu', out)
        report('ol.py (overload / signal LED)', code == 0 and bool(m) and 17.5 < float(m.group(1)) < 19.5 and -21 < float(m.group(2)) < -18,
               f'red {m.group(1)} dBu, green {m.group(2)} dBu at 1 kHz' if m else out.strip()[-120:])
        code, out = run(['python3', os.path.join(ROOT, 'sim', 'review', 'cs1', 'ol_multi.py'), '--quick'], timeout=900)
        m = re.search(r'pulse thresholds: \+([\d.]+) V / -([\d.]+) V', out)
        report('ol_multi.py (OL from both polarities)', code == 0 and bool(m) and 8.5 < float(m.group(1)) < 9.6 and 8.5 < float(m.group(2)) < 9.8,
               f'10 % pulse lights the red at +{m.group(1)} / -{m.group(2)} V' if m else out.strip()[-120:])
    bad = [n for n, ok in results if not ok]
    print(f'\n{len(results) - len(bad)} / {len(results)} checks pass in {time.time() - t0:.0f} s' + (f'; FAILED: {", ".join(bad)}' if bad else ''))
    sys.exit(1 if bad else 0)

if __name__ == '__main__':
    main()
