"""CS7 (docs/proposals/cs7_proposal.md): the C/Room dim. The CRS follower drives CRSB through its 100R build-out (MG6); CRSB feeds the
C/ROOM pot (now through RD, 91K, shorted by the released DIM key), the PHONES pot and the meter feed (100R into the
rectifier's 10K). The C/ROOM wiper sees 2.2 uF + 100K (the follower's bias). Pots: A10K, the decks' two-slope law
(0.30 x to the middle, then 0.15 + 1.70 (x - 0.5)). Solved per position by nodal analysis at 1 kHz (the 2.2 uF is 72 ohm
there against 100K: left out).
  1. dim depth against the C/ROOM position (released / latched), and RD's tolerance;
  2. what the dim does to CRSB (phones, meters);
  3. the switching step: DC on CRSB moves the wiper's DC when RD goes in or out, and the 2.2 uF / 100K passes it as a
     step (tau 0.22 s);
  4. RD's thermal noise at the follower against the dimmed programme.
usage: python3 sim/review/cs7/dim.py"""
import math

RB, RD, RP, RL = 100.0, 91e3, 10e3, 100e3          # build-out, dim resistor, pots, wiper load (bias resistor)
VOS = 0.498e-3      # the CRS follower's output DC: TI's OPA1656 model, + input on 100K // 1M (ngspice .op, 2026-10-28)
R_PH, R_MTR = 10e3, 100.0 + 10e3                    # PHONES pot top (wiper load aside), meter feed
law = lambda x: 0.30 * x if x <= 0.5 else 0.15 + 1.70 * (x - 0.5)
db = lambda v: 20 * math.log10(v)

def solve(x, dim, rd=RD, rcontact=0.05):
    """(V_CRSB, V_wiper) for 1 V at the follower output; C/ROOM at rotation x (0..1)."""
    a = max(law(x), 1e-6); r_low, r_high = a * RP, (1 - a) * RP + 1e-3
    r_series = rd if dim else rcontact
    # nodes: S (CRSB), T (pot top), W (wiper); conductances
    gB, gS, gH, gLo, gL = 1 / RB, 1 / r_series, 1 / r_high, 1 / r_low, 1 / RL
    gX = 1 / R_PH + 1 / R_MTR
    # [S T W] matrix
    M = [[gB + gX + gS, -gS, 0.0],
         [-gS, gS + gH, -gH],
         [0.0, -gH, gH + gLo + gL]]
    b = [gB, 0.0, 0.0]
    # Gaussian elimination (3 x 3)
    for i in range(3):
        for j in range(i + 1, 3):
            f = M[j][i] / M[i][i]
            for k in range(i, 3): M[j][k] -= f * M[i][k]
            b[j] -= f * b[i]
    v = [0.0] * 3
    for i in (2, 1, 0): v[i] = (b[i] - sum(M[i][k] * v[k] for k in range(i + 1, 3))) / M[i][i]
    return v[0], v[2]

if __name__ == '__main__':
    print('1. dim depth at the C/ROOM wiper (latched against released), RD 91K')
    print('   C/ROOM rotation   wiper released   dim depth    RD 1 % low / high')
    for x in (1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1):
        _, w0 = solve(x, False); _, w1 = solve(x, True)
        lo, hi = solve(x, True, rd=RD * 0.99)[1], solve(x, True, rd=RD * 1.01)[1]
        print(f'   {x:4.1f}             {db(w0):7.2f} dB      {db(w1 / w0):6.2f} dB   {db(lo / w0):6.2f} / {db(hi / w0):6.2f}')
    print('   (L / R match: two 1 % resistors differ by <= 0.17 dB, the dual pot\'s own tracking is larger)')
    s0, _ = solve(1.0, False); s1, _ = solve(1.0, True)
    print(f'\n2. CRSB (phones and meters): {db(s1 / s0):+.3f} dB when dimmed (the C/ROOM pot no longer loads the 100R build-out)')
    print('\n3. switching step: per 1 mV of DC on CRSB (the CRS follower\'s offset; its input sits on 100K // 1M to GNDA)')
    for x in (1.0, 0.7, 0.5):
        a = law(x)
        d0 = solve(x, False)[1] / 1.0; d1 = solve(x, True)[1] / 1.0      # DC divides as the signal does (no load cap at DC
        # on the wiper side of the 2.2 uF: the DC step reaches the follower through it, then decays with 2.2 uF x 100K)
        step = 1e-3 * abs(d0 - d1); st = VOS * abs(d0 - d1)
        print(f'   C/ROOM {x:3.1f}: step {step * 1e3:.2f} mV at the C/Room follower = {db(step / 0.7746):6.1f} dBu peak, '
              f'{db(2 * step / 0.7746):6.1f} dBu at the TRS output (DRV135 +6 dB); decays with tau 0.22 s')
        print(f'               with TI\'s model ({VOS * 1e3:.2f} mV): {st * 1e3:.2f} mV, {db(st / 0.7746):6.1f} dBu at the follower, '
              f'{db(2 * st / 0.7746):6.1f} dBu at the TRS output')
    print('   a step whose spectrum falls 6 dB / octave: mostly LF. For the PFL switcher\'s ticks see master spec section 19')
    print('\n4. noise: RD\'s Johnson noise at the follower, C/ROOM at the top, dimmed (20 Hz - 20 kHz, 300 K)')
    rw = 1 / (1 / (RD + RB) + 1 / RP + 1 / RL)
    vn = math.sqrt(4 * 1.380649e-23 * 300 * rw * 19980)
    print(f'   source {rw / 1e3:.1f}K at the wiper: {db(vn / 0.7746):.1f} dBu ({db(2 * vn / 0.7746):.1f} dBu at the TRS output); '
          f'released: {db(math.sqrt(4 * 1.380649e-23 * 300 * RB * 19980) / 0.7746):.1f} dBu')
