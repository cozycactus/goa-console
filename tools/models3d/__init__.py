"""goa-console part models: one module per part that KiCad's library has no 3D model for, shared by KiCad (VRML,
goa-console.3dshapes/) and Blender (tools/console_3d.py).

Each part module defines
  NAME        human-readable part name and the datasheet it follows
  FOOTPRINTS  {footprint name: build keyword arguments}
  FEATURE     (x, y) of the panel feature (shaft, plunger, jack nose, XLR barrel, fader slot centre) in the
              footprint frame, or None
  MOUNT       'main' (main board: panel underside STACK['panel_z0'] above the board top) or 'jack' (jack board:
              panel underside STACK['jack_z0'] above it)
  build(**kw) the part as mounted on the TOP side of its board, footprint frame (x right, y down, mm), origin =
              footprint origin, z = 0 on the board top, leads down to z = -3. Everything between the board and the
              panel, and whatever passes through the panel (bushing, plunger, shaft, lever).
  panel(**kw) what sits on top of the panel (knob, cap, nut, flange, fader knob), centred on FEATURE, z = 0 on the
              panel top; None if nothing. Keyword 'colour' picks a cap colour where it applies.
  pins(**kw)  lead centres [(x, y)] in the footprint frame: every through-hole pad of the footprint gets one.
The panel stack is spec 16.2: panel underside 11.5 mm above the main board, panel 1.5 mm thick, jack board top
24.0 mm under the panel underside: Neutrik's NJ*FD-V family drawing and NJ3FD-V CAD (flange front 24.00 above the PCB)
and the NC3MAV drawing (index C: PCB to housing front 24), so 24.0 mm standoffs."""
import importlib

STACK = dict(panel_z0=11.5, panel_t=1.5, jack_z0=24.0)
MODULES = ['alpha_pot', 'alps_rk09l', 'ck_pva2', 'neutrik_nj6fd_v', 'neutrik_nc3mav', 'bourns_ptb', 'keystone_1287', 'bourns_mfrx']


def registry():
    """{footprint name: (module, kwargs)} for every modelled footprint."""
    reg = {}
    for name in MODULES:
        mod = importlib.import_module(f'{__name__}.{name}')
        for fp, kw in mod.FOOTPRINTS.items(): reg[fp] = (mod, kw)
    return reg


def lookup(fpid):
    """(module, kwargs) for a footprint id ('Lib:Name' or 'Name'), or None."""
    return registry().get(fpid.split(':')[-1])
