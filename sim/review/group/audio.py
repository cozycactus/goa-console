"""Audio-band cost of a fix set: drive SUB1 (via 4K7), AUX1 (via 22K) and both return jacks (tip, 50R), read every
stage output 20 Hz-20 kHz with and without the fixes; print max |delta dB| and delta phase at 20 kHz per output.
usage: python3 audio.py <fixset> [board]"""
import sys, numpy as np
from groupdeck import deck, ngspice, HERE
from fixes import FIX, apply
OUTS = ['GC_BUF', 'S_SUM', 'S_MIX', 'SUB_RBUF', 'S_FPOST', 'S_POST', 'S_PBL', 'S_PBR', 'A_SUM', 'A_MIX', 'A_OUT', 'RT_L', 'RT_R', 'RT_BL', 'RT_BR']
def resp(fx, pos, board):
    cfg = apply(dict(pos=pos, src={'SUB1': 4.7e3, 'AUX1': 22e3, 'Return_LT': 50, 'Return_RT': 50}, board=board), fx)
    tag = f'aud_{fx}_{pos["RV1"]}_{pos["RV2"]}_{board}'.replace('.', 'p')
    ctl = '\n'.join(['.control', 'set wr_singlescale', 'set wr_vecnames', 'ac dec 40 20 20k',
                     f'wrdata {HERE}/raw/{tag}.txt ' + ' '.join(f'v({o})' for o in OUTS), '.endc'])
    ngspice(deck(cfg, ctl), tag)
    d = np.loadtxt(f'{HERE}/raw/{tag}.txt', skiprows=1)
    f = d[:, 0]; return f, {o: d[:, 1 + 2 * i] + 1j * d[:, 2 + 2 * i] for i, o in enumerate(OUTS)}
if __name__ == '__main__':
    fx = sys.argv[1]; board = float(sys.argv[2]) if len(sys.argv) > 2 else 0
    for p, pan in ((0.706, 0.5), (1.0, 1.0), (0.3, 0.0), (1.0, 0.5)):
        pos = {'RV1': p, 'RV3': p, 'RV4': p, 'RV2': pan}
        f, a = resp('none', pos, board); f, b = resp(fx, pos, board)
        print(f'pots {p} pan {pan}:', '  '.join(f"{o} {np.max(np.abs(20*np.log10(np.abs(b[o]/a[o])))):.4f}dB/{np.degrees(np.angle(b[o][-1]/a[o][-1])):.2f}deg" for o in OUTS))
