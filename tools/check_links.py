"""Footprint-symbol links: every symbol in a board's schematic netlist has a footprint whose path is the symbol's full
path (sheet tstamps + its own uuid), the link KiCad's cross-probing and Update PCB use. Parity DRC doesn't catch a broken
path (it falls back to matching by reference), so run this after any placement. Run with KiCad's Python:
  $KPY tools/check_links.py channel_strip jack_board group group_jack_board master master_jack_board psu jig_master_stub jig_load_board
Each name is a project folder boards/<name>/: <name>.net (exported from <name>.kicad_sch) against <name>.kicad_pcb. Exits non-zero on a break."""
import os, sys
import pcbnew
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verify import sexp, field

ok = True
for name in sys.argv[1:]:
    tree = sexp(open(os.path.join(ROOT, 'boards', name, name + '.net')).read())
    comps = next(c for c in tree[1:] if isinstance(c, list) and c[0] == 'components')
    want = {}
    for c in comps[1:]:
        ts = next((x for x in c[1:] if isinstance(x, list) and x[0] == 'tstamps'), None)
        sp = next((x for x in c[1:] if isinstance(x, list) and x[0] == 'sheetpath'), None)
        want[field(c, 'ref')] = (field(sp, 'tstamps') if sp else '/') + ts[1]
    have = {f.GetReference(): f.GetPath().AsString() for f in pcbnew.LoadBoard(os.path.join(ROOT, 'boards', name, name + '.kicad_pcb')).GetFootprints()}
    bad = [r for r in want if have.get(r) != want[r]]
    print(f'{name:18s} {len(want) - len(bad):4d} / {len(want)} symbols linked; board-only: {sorted(r for r in have if r not in want)}'
          + (f'; UNLINKED {bad[:8]}' if bad else ''))
    ok &= not bad
sys.exit(0 if ok else 1)
