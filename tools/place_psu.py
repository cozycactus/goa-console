"""Component placement for the PSU regulator board (psu_spec.md v0.2). Placement only: no copper.
  /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 tools/place_psu.py
+V rail on the left half, -V rail on the right; LDOs and SCRs in a row on the top edge with their tabs
1.68 mm proud of the edge (through the PSU case's front panel onto the heatsink) (insulating pads: the tabs sit at +V, 0 V and -V); DC inputs, earth and the
7-way output on the bottom edge with their wire openings outwards. Engine: placer.py."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from placer import place, PROJ

W, H = 120.0, 60.0
# TO-220 vertical: tab side 3.44 mm behind pin 1. The tabs stand 1.68 mm proud of the board edge (docs/proposals/psu_case_proposal.md,
# 2026-10-26): with the edge 0.3 mm inside the 1.63 mm front panel, they reach the heatsink through a 0.25 mm pad
OVERHANG = 1.68
TOP = 3.44 - OVERHANG
BOT = H - 0.3 - 5.75                  # MKDS turned 180: wire openings 5.75 mm beyond the pins; pin 1 now on the right
fix = {'U1': (12, TOP, 0, 'F'), 'Q2': (36, TOP, 0, 'F'),          # +V LDO, +V crowbar SCR
       'U3': (72, TOP, 0, 'F'), 'Q4': (96, TOP, 0, 'F'),          # -V LDO, -V crowbar SCR
       'J1': (17, BOT, 180, 'F'), 'J4': (35, BOT, 180, 'F'),      # SMPS #1 in (left), earth stud
       'J3': (75.24, BOT, 180, 'F'),                              # console out (7-way), centred between the rails
       'J2': (103, BOT, 180, 'F')}                                # SMPS #2 in (right)
pos = ['L1', 'C1', 'C2', 'R1', 'R2', 'C3', 'D1', 'D2', 'C4', 'C5', 'D3', 'R3', 'D4']
pos_cb = ['R4', 'R5', 'C6', 'U2', 'R6', 'R7', 'Q1', 'R8', 'R9']
neg = ['L2', 'C7', 'C8', 'R10', 'R11', 'C9', 'D5', 'D6', 'C10', 'C11', 'D7', 'R12', 'D8']
neg_cb = ['R13', 'R14', 'C12', 'U4', 'R15', 'R16', 'Q3', 'R17', 'R18']
near = {r: 'U1' for r in ('C1', 'C2', 'R1', 'R2', 'C3', 'D1', 'D2', 'C4', 'C5', 'D3')}
near.update({r: 'U3' for r in ('C7', 'C8', 'R10', 'R11', 'C9', 'D5', 'D6', 'C10', 'C11', 'D7')})
near.update({r: 'Q2' for r in pos_cb}); near.update({r: 'Q4' for r in neg_cb})
near.update({'L1': 'J1', 'L2': 'J2'})
zones = [('+V rail', (1, 9, 59, 44), pos, 'F'), ('+V crowbar', (1, 9, 59, 44), pos_cb, 'F'),
         ('-V rail', (61, 9, 119, 44), neg, 'F'), ('-V crowbar', (61, 9, 119, 44), neg_cb, 'F')]
labels = [(25, 45.3, '+V RAIL (OUT +V, RTN 0V)', 1.2), (95, 45.3, '-V RAIL (OUT 0V, RTN -V)', 1.2),
          (14.5, 47.6, 'SMPS1 -  +', 1.0), (32.5, 47.6, 'EARTH', 1.0), (100.5, 47.6, 'SMPS2 -  +', 1.0),
          (60.0, 47.6, '-V  -V  0V  0V  +V  +V  E', 1.0), (60, 11, 'HEATSINK EDGE: INSULATE TABS', 1.0)]
place(os.path.join(PROJ, 'boards', 'psu', 'psu.net'), os.path.join(PROJ, 'boards', 'psu', 'psu.kicad_pcb'),
      dict(board=(0, 0, W, H), fix=fix, holes=[(4, 4), (W - 4, 4), (4, H - 4), (W - 4, H - 4)],
           hole_value='M3 standoff', zones=zones, near=near, grounds=(), labels=labels,
           notes=((10, 'PSU REGULATOR BOARD'), (20, 'top edge: heatsink bar'), (30, 'bottom edge: wiring'))))
