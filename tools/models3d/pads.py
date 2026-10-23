"""Pads of a footprint, read from its .kicad_mod (KiCad library or goa-console.pretty), without pcbnew."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from verify import sexp

KLIB = '/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/'
if not os.path.isdir(KLIB): KLIB = '/usr/share/kicad/footprints/'
PROJ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


def path(fpid):
    lib, name = fpid.split(':', 1) if ':' in fpid else (None, fpid)
    if lib == 'goa-console' or (lib is None and os.path.exists(os.path.join(PROJ, 'goa-console.pretty', name + '.kicad_mod'))):
        return os.path.join(PROJ, 'goa-console.pretty', name + '.kicad_mod')
    if lib is None:
        for d in os.listdir(KLIB):
            p = os.path.join(KLIB, d, name + '.kicad_mod')
            if os.path.exists(p): return p
    return os.path.join(KLIB, lib + '.pretty', name + '.kicad_mod')


def pads(fpid):
    """[(number, kind, x, y, size_x, size_y, drill)] with kind 'thru_hole' / 'np_thru_hole' / 'smd'."""
    t = sexp(open(path(fpid)).read())
    out = []
    for item in t[1:]:
        if not (isinstance(item, list) and item and item[0] == 'pad'): continue
        num, kind = item[1], item[2]
        at = next(x for x in item if isinstance(x, list) and x[0] == 'at')
        size = next((x for x in item if isinstance(x, list) and x[0] == 'size'), ['size', 0, 0])
        drill = next((x for x in item if isinstance(x, list) and x[0] == 'drill'), None)
        d = 0.0
        if drill:
            nums = [v for v in drill[1:] if not isinstance(v, list) and v != 'oval']
            d = float(nums[0]) if nums else 0.0
        out.append((num, kind, float(at[1]), float(at[2]), float(size[1]), float(size[2]), d))
    return out
