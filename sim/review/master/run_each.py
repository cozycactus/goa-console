"""Run the master stability configurations one at a time, so progress shows and nothing is left running.
usage: TI_MODELS=<folder> python3 run_each.py FIXSET [cfg1,cfg2,... | all] [timeout_s per config, default 1200]
Each configuration is `run_all.py FIXSET cfg` in its own process group (killed whole on timeout); results go to
res/<fixset>_<cfg>.json as with run_all.py. Prints a line per configuration: time, worst unit, its phase margin."""
import os, re, signal, subprocess, sys, time
from configs import CONFIGS

fix = sys.argv[1]
cfgs = sys.argv[2].split(',') if len(sys.argv) > 2 and sys.argv[2] != 'all' else list(CONFIGS)
limit = float(sys.argv[3]) if len(sys.argv) > 3 else 1200
t_all = time.time()
for i, c in enumerate(cfgs, 1):
    print(f'[{i}/{len(cfgs)}] {c} ...', end=' ', flush=True)
    t0 = time.time()
    p = subprocess.Popen([sys.executable, 'run_all.py', fix, c], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         text=True, env={**os.environ, 'NJ': '1'}, start_new_session=True)
    try:
        out, _ = p.communicate(timeout=limit)
    except subprocess.TimeoutExpired:
        os.killpg(p.pid, signal.SIGKILL); p.communicate()
        print(f'TIMEOUT after {limit:.0f} s (killed)', flush=True); continue
    line = next((l for l in out.splitlines() if l.startswith(f'{fix} {c} ')), None)
    if not line:
        print(f'FAILED after {time.time() - t0:.0f} s: ' + ' | '.join(out.strip().splitlines()[-3:]), flush=True); continue
    pm = [(float(m.group(2)), m.group(1)) for m in re.finditer(r'(U\d+[AB]):([\d.]+)/', line)]
    nodata = len(re.findall(r'U\d+[AB]:None', line))
    worst = min(pm) if pm else (None, '-')
    print(f'{time.time() - t0:.0f} s, worst {worst[1]} {worst[0]}°' + (f', {nodata} units without data' if nodata else ''),
          flush=True)
print(f'done: {len(cfgs)} configurations in {(time.time() - t_all) / 60:.1f} min')
