"""Check that every symbol pin in a KiCad netlist lands on a pad of the assigned footprint.
usage: check_fp.py channel_strip.net [project_dir]"""
import os, re, sys, collections
sys.path.insert(0, os.path.dirname(__file__))
from verify import sexp, field   # noqa: E402  (verify.py guards its main code)

FPDIRS = [os.environ.get('KICAD_FOOTPRINT_DIR', ''), '/usr/share/kicad/footprints/',
          '/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/']
proj = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.abspath(sys.argv[1]))

def fp_file(fpid):
    lib, name = fpid.split(':', 1)
    for d in [os.path.join(proj, lib + '.pretty')] + [os.path.join(d, lib + '.pretty') for d in FPDIRS if d]:
        f = os.path.join(d, name + '.kicad_mod')
        if os.path.isfile(f): return f

tree = sexp(open(sys.argv[1]).read())
comps = next(c for c in tree[1:] if isinstance(c, list) and c[0] == 'components')
nets = next(c for c in tree[1:] if isinstance(c, list) and c[0] == 'nets')
pins = collections.defaultdict(set)
for n in nets[1:]:
    for nd in n[1:]:
        if isinstance(nd, list) and nd[0] == 'node': pins[field(nd, 'ref')].add(field(nd, 'pin'))
bad, notes = 0, []
for c in comps[1:]:
    ref, fpid = field(c, 'ref'), field(c, 'footprint')
    if ref.startswith('#'): continue
    if not fpid: print(f'{ref}: no footprint'); bad += 1; continue
    f = fp_file(fpid)
    if not f: print(f'{ref}: footprint {fpid} not found'); bad += 1; continue
    # pad names are quoted in KiCad 8+ library files, bare in KiCad 7's; mechanical pads ("", MP, NPTH) have no pin
    pads = {}
    for m in re.finditer(r'\(pad\s+(?:"([^"]*)"|([^\s()"]+))\s+(\w+)', open(f).read()):
        pads[m.group(1) if m.group(1) is not None else m.group(2)] = m.group(3)          # name: pad type
    electrical = {p for p, k in pads.items() if p and k != 'np_thru_hole' and not p.startswith('MP')}
    missing = pins[ref] - set(pads)
    if missing: print(f'{ref}: pins {sorted(missing)} have no pad in {fpid} (pads {sorted(pads)})'); bad += 1
    extra = electrical - pins[ref]
    if extra and not missing:
        if any(p.isdigit() for p in extra): print(f'{ref}: pads {sorted(extra)} of {fpid} have no pin (a bigger package than the symbol?)'); bad += 1
        else: notes.append(f'{ref}: pads {sorted(extra)} of {fpid} have no pin')   # named contacts a symbol may leave (a jack's SN, an XLR's G)
for n in notes: print('note:', n)
print('components checked:', sum(1 for c in comps[1:] if not field(c, 'ref').startswith('#')), ' problems:', bad)
sys.exit(1 if bad else 0)
