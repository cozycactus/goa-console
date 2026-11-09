"""Console tub thermal study (2026-10-26): how warm the air inside the console gets, closed and with vents.

A lumped model, steady state. The console dissipates P inside the tub. Heat leaves through:
  - the aluminium panels (inside air -> panel underside -> panel top -> room: convection + radiation, anodised black);
  - the floor and walls (wood: inside film, conduction, outside film);
  - vents, when there are any: a chimney between a low inlet and a high outlet, driven by the warm air's buoyancy.
Geometry from the 3D model (console_3d.py): 1219 x 516 mm of panel, 56.5 mm from the panel underside to the floor,
9 degrees of tilt (the back is higher). Film coefficients are ranges, not single values, because an enclosed cavity
full of boards is not a textbook case; every result is given for the low / middle / high end.
usage: python3 sim/review/thermal/tub_thermal.py"""
import math

P_TYP = 17.0 * (3.09 + 2.67)          # W: master spec 27, typical console current on +-17 V
P_HOT = 17.0 * (3.64 + 3.20)          # W: every op-amp at maximum supply current (no LEDs counted)
W, D, H = 1.2192, 0.516, 0.0565        # m: panel area, cavity height (panel underside to floor)
TILT = math.radians(9.0)
A_PANEL = W * D * 0.93                 # m2: less the holes
A_FLOOR = (W + 0.04) * D               # m2
A_WALL = 2 * (D * H) + 2 * (W * H)     # m2: cheeks, back, front
WOOD_R = 0.018 / 0.15                  # m2K/W: 18 mm ply / MDF
SIGMA, EPS = 5.67e-8, 0.85             # black anodised panel
RHO_CP, G, T0 = 1.2 * 1005.0, 9.81, 298.0

def h_out_panel(dt, t_room=298.0):
    """Panel top: free convection off a warm plate facing up (about 1.5 dT^(1/3)) plus radiation."""
    t = t_room + dt
    return 1.52 * max(dt, 0.1) ** (1 / 3) + EPS * SIGMA * (t ** 4 - t_room ** 4) / max(dt, 0.1)

def solve(p, h_in, h_floor_in, vent_area=0.0, stack=0.0, cd=0.6):
    """Inside-air rise above the room (K) for dissipation p. h_in: inside air to the panel underside; h_floor_in: to the
    floor and walls (stable stratification there, so lower). vent_area: effective free area of the chimney path (m2)."""
    lo, hi = 0.0, 200.0
    for _ in range(80):
        dt = (lo + hi) / 2
        # panel path: inside film in series with the outside film (outside depends on the panel's own rise)
        tp = dt * 0.3
        for _ in range(30):                                   # panel temperature
            q = (dt - tp) * h_in * A_PANEL
            tp = q / (h_out_panel(tp) * A_PANEL)
        q_panel = (dt - tp) * h_in * A_PANEL
        u_wood = 1 / (1 / h_floor_in + WOOD_R + 1 / 7.0)      # outside: about 7 W/m2K (convection + radiation)
        q_wood = dt * u_wood * (A_FLOOR + A_WALL)
        q_vent = 0.0
        if vent_area:
            v = cd * math.sqrt(2 * G * stack * dt / T0)       # chimney: buoyancy head over the stack height
            q_vent = RHO_CP * vent_area * v * dt
        if q_panel + q_wood + q_vent > p: hi = dt
        else: lo = dt
    return dt, q_panel, q_wood, q_vent

def eff_area(*areas):
    """Openings in series (inlet, any passage, outlet): 1 / A^2 adds."""
    return 1 / math.sqrt(sum(1 / a ** 2 for a in areas))

STACK = D * math.sin(TILT) + H           # m: a front-low inlet to a back-high outlet
CASES = [('closed tub', 0.0),
         ('slots 1.2 m x 6 mm in and out', eff_area(1.2 * 0.006, 1.2 * 0.006)),
         ('slots 1.2 m x 12 mm in and out', eff_area(1.2 * 0.012, 1.2 * 0.012)),
         ('slots 1.2 m x 20 mm in and out', eff_area(1.2 * 0.020, 1.2 * 0.020))]
# the real path with the 10 x 50 frame rails (docs/proposals/frame_proposal.md) under both panel ends: air enters through floor slots
# just inside the front rail (y 445-490, free floor behind the strips' fader end), rises along the tilted cavity, and
# leaves through slots on the back rail's neutral axis (a slot h tall on the axis removes 10 h^3 / 12 of the bar's
# 104 167 mm4 there: 2.7 % for 15 mm, 12.5 % for 25 mm, over the slotted 73 % of the length) into a plenum in the back trim with a slot on its top; the slots are openings in series
RAIL_SLOTS = 30 * 0.030 * 0.015                       # 30 slots 30 x 15 mm per rail
CASES += [('floor 20 mm + rail slots + trim 20 mm', eff_area(1.2 * 0.020, RAIL_SLOTS, 1.2 * 0.020)),
          ('as above, rail slots 30 x 25 mm', eff_area(1.2 * 0.020, 30 * 0.030 * 0.025, 1.2 * 0.020))]
FANS = [('fan 15 m3/h (one 80 mm at ~5 V)', 15 / 3600), ('fan 30 m3/h (one 120 mm at ~5 V)', 30 / 3600)]
FILMS = {'low': (2.0, 1.0), 'mid': (3.5, 1.5), 'high': (5.0, 2.5)}   # inside: to the panel, to the floor (W/m2K)

def life(t, l85=1000.0):
    """Electrolytic life (h) from an 85 degC rating, doubling every 10 K below it."""
    return l85 * 2 ** ((85.0 - t) / 10.0)

if __name__ == '__main__':
    print(f'dissipation {P_TYP:.0f} W typical, {P_HOT:.0f} W with every op-amp at maximum current; stack {STACK * 1000:.0f} mm')
    print(f'{"case":34s} ' + '  '.join(f'{k:>16s}' for k in FILMS) + '   (inside-air rise, K)')
    for name, a in CASES:
        row = []
        for k, (hi_, hf) in FILMS.items():
            dt, qp, qw, qv = solve(P_TYP, hi_, hf, a, STACK)
            row.append(f'{dt:5.1f} ({qv / P_TYP * 100:3.0f}% vent)')
        print(f'{name:34s} ' + '  '.join(f'{r:>16s}' for r in row))
    for name, q in FANS:                                  # forced flow: the fan's air carries rho cp Q dT
        row = []
        for k, (hi_, hf) in FILMS.items():
            lo, hi = 0.0, 100.0
            for _ in range(60):
                dt = (lo + hi) / 2; _, qp, qw, _ = solve(P_TYP, hi_, hf); f = dt / max(solve(P_TYP, hi_, hf)[0], 1e-9)
                tot = (qp + qw) * f + RHO_CP * q * dt
                if tot > P_TYP: hi = dt
                else: lo = dt
            row.append(f'{dt:5.1f} (fan)      ')
        print(f'{name:34s} ' + '  '.join(f'{r:>16s}' for r in row))
    print('\nMUSE ES life (1000 h at 85 degC), parts ~5 K above the inside air, 25 degC room:')
    for name, a in CASES:
        dt = solve(P_TYP, *FILMS['mid'], a, STACK)[0]
        t = 25 + dt + 5
        print(f'  {name:34s} part {t:4.1f} degC: {life(t):7.0f} h = {life(t) / (4 * 365):5.1f} years at 4 h a day, '
              f'{life(t) / 8760:4.1f} years 24/7')
