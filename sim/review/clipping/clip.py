"""Clipping waveforms: the Delta DLX's op-amps against ours, on +-17 V, driven past the rails (2026-10-29).
Unity follower (the Delta's gain-pot buffer, HPF, post-amp and direct-out buffer are non-inverting; our U16 receiver
followers, pan buffers, insert return) and a unity inverter (EQ stages, summers, mute inverter), 1 kHz, 10 kohm load,
14 / 16 / 18 V peak in (+22.0 / +23.3 / +24.3 dBu).
Models (TI's, from $TI_MODELS, default ./models, not in the repo):
  TL072 classic  = TI's 1989 TL072 macromodel + the JFET input stage's phase reversal (tl072_classic.lib: no vendor model
                   has it; threshold V- + 3 V, the datasheet's typical VICR)
  TL072 1989     = the same macromodel bare (output clipping only, as TI published it)
  TL07xH         = TI's 2020 model of the redesigned die (TL07xH: no reversal, rail-to-rail-ish input clamp)
  OPA1612        = OPA161x.LIB (ours in the path and on the sums)
  OPA1656        = OPA1656.LIB (ours in the input followers, PFL sum, CRS followers)
usage: .venv/bin/python sim/review/clipping/clip.py [outdir]     (ngspice 42 with the PSpice compatibility mode; writes
       outdir/clip_follower.png, clip_inverting.png, clip_zoom.png and prints the peak table)"""
import os, sys, subprocess, tempfile, math
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
M = os.environ.get('TI_MODELS', os.path.join(HERE, 'models'))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', '..', '..', 'docs', 'clipping')
MODELS = [  # name, include lines, subckt, pin order kind
    ('TL072 classic (1989 macro + reversal)', [f'.include {M}/TL072_1989.LIB', f'.include {HERE}/tl072_classic.lib'], 'TL072R'),
    ('TL072 1989 macro (TI, as published)', [f'.include {M}/TL072_1989.LIB'], 'TL072'),
    ('TL07xH (TI 2020, new die)', [f'.include {M}/TL07xH.LIB'], 'TL07XH_TL08XH'),
    ('OPA1612 (ours, path / sums)', [f'.include {M}/OPA161x.LIB'], 'OPA161x'),
    ('OPA1656 (ours, followers)', [f'.include {M}/OPA1656.LIB'], 'OPA1656'),
]
AMPS = [14, 16, 18]
F = 1e3

def dbu(vpk): return 20 * math.log10(vpk / math.sqrt(2) / 0.7746)

OPTS = ['', '.options method=gear reltol=0.005 abstol=1e-10 vntol=1e-6 gmin=1e-11 itl4=200',
        '.options method=gear reltol=0.01 abstol=1e-9 vntol=1e-5 gmin=1e-10 itl4=500']   # retry ladder: the 1989
# macro's ideal clamp diodes stall the timestep when an inverter is driven hard; the looser runs are checked to give
# the same peaks (within 10 mV) where both converge

def deck(incl, sub, cfg, vpk, opt=''):
    stage = f'X1 in out vp vn out {sub}\n' if cfg == 'fol' else f'R1 in n 10k\nR2 n out 10k\nX1 0 n vp vn out {sub}\n'
    return f"""* clip {sub} {cfg} {vpk}
{chr(10).join(incl)}
{opt}
VP vp 0 17
VN vn 0 -17
VIN in 0 SIN(0 {vpk} {F})
{stage}RL out 0 10k
.tran 1u 3m 0 0.5u
.control
set noaskquit
run
wrdata out.txt v(out) v(in)
quit
.endc
.end
"""

def run(incl, sub, cfg, vpk):
    for k, opt in enumerate(OPTS):
        with tempfile.TemporaryDirectory() as d:
            open(os.path.join(d, '.spiceinit'), 'w').write('set ngbehavior=psa\n')
            open(os.path.join(d, 'd.cir'), 'w').write(deck(incl, sub, cfg, vpk, opt))
            p = subprocess.run(['ngspice', '-b', 'd.cir'], cwd=d, capture_output=True, text=True, timeout=600)
            fn = os.path.join(d, 'out.txt')
            a = np.loadtxt(fn) if os.path.exists(fn) else np.zeros((0, 4))
        if len(a) and a[-1, 0] >= 2.99e-3:
            t, vo, vi = a[:, 0], a[:, 1], a[:, 3]
            w = (t >= 1e-3) & (t <= 3e-3)
            if k: print(f'   ({sub} {cfg} {vpk}: converged with option set {k})')
            return t[w] * 1e3, vo[w], vi[w]
    raise SystemExit(f'{sub} {cfg} {vpk}: ngspice failed on every option set\n{p.stdout[-600:]}')

def main():
    os.makedirs(OUT, exist_ok=True)
    res = {}
    print(f'{"model":40s} {"cfg":4s} {"in Vpk":>7s} {"in dBu":>7s} {"out max":>8s} {"out min":>8s}')
    for name, incl, sub in MODELS:
        for cfg in ('fol', 'inv'):
            for vpk in AMPS:
                t, vo, vi = run(incl, sub, cfg, vpk)
                res[(name, cfg, vpk)] = (t, vo, vi)
                print(f'{name:40s} {cfg:4s} {vpk:7.1f} {dbu(vpk):7.1f} {vo.max():8.2f} {vo.min():8.2f}')
    for cfg, title, fn in (('fol', 'Unity follower (non-inverting), +-17 V, 10 k load, 1 kHz', 'clip_follower.png'),
                           ('inv', 'Unity inverter (10K / 10K), +-17 V, 10 k load, 1 kHz', 'clip_inverting.png')):
        fig, axs = plt.subplots(len(MODELS), len(AMPS), figsize=(13, 2.3 * len(MODELS)), sharex=True, sharey=True)
        for i, (name, _, _) in enumerate(MODELS):
            for j, vpk in enumerate(AMPS):
                t, vo, vi = res[(name, cfg, vpk)]
                ax = axs[i, j]
                ax.plot(t, vi if cfg == 'fol' else -vi, 'k--', lw=0.7, label='ideal (in)')
                ax.plot(t, vo, color='C3' if 'classic' in name else ('C0' if 'ours' in name else 'C1'), lw=1.2, label='out')
                ax.axhline(17, color='0.6', lw=0.5); ax.axhline(-17, color='0.6', lw=0.5)
                ax.set_ylim(-19.5, 19.5); ax.grid(alpha=0.3)
                if i == 0: ax.set_title(f'{vpk} V peak in = {dbu(vpk):+.1f} dBu', fontsize=10)
                if j == 0: ax.set_ylabel(name, fontsize=8)
                if i == len(MODELS) - 1: ax.set_xlabel('ms')
        axs[0, 0].legend(fontsize=7, loc='lower left')
        fig.suptitle(title); fig.tight_layout(); fig.savefig(os.path.join(OUT, fn), dpi=110); plt.close(fig)
    # zoom: one negative half-cycle of the follower at 16 V peak
    fig, ax = plt.subplots(figsize=(9, 4.5))
    t, vo, vi = res[(MODELS[0][0], 'fol', 16)]
    ax.plot(t, vi, 'k--', lw=0.8, label='input, 16 V peak (+23.3 dBu)')
    for name, _, _ in MODELS:
        t, vo, vi = res[(name, 'fol', 16)]
        ax.plot(t, vo, lw=1.3, label=name)
    ax.set_xlim(1.45, 2.05); ax.set_ylim(-18, 18); ax.axhline(17, color='0.6', lw=0.5); ax.axhline(-17, color='0.6', lw=0.5)
    ax.axhline(-14, color='C3', lw=0.5, ls=':'); ax.text(1.46, -13.6, 'TL072 input range ends (V- + 3 V)', color='C3', fontsize=8)
    ax.set_xlabel('ms'); ax.set_ylabel('V'); ax.grid(alpha=0.3); ax.legend(fontsize=8, loc='upper right')
    ax.set_title('Follower, negative half-cycle: the classic TL072 reverses 1.5 V before its output would clip; ours clip')
    fig.tight_layout(); fig.savefig(os.path.join(OUT, 'clip_zoom.png'), dpi=110); plt.close(fig)
    print('written', OUT)

if __name__ == '__main__':
    main()
