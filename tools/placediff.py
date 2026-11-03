"""Placement diff: which footprints were added, removed, moved, turned or flipped between two versions of a board.
After a `moves_only` change (CLAUDE.md, Rules) it must list the new parts and nothing else.
usage: python3 tools/placediff.py OLD.kicad_pcb NEW.kicad_pcb
       python3 tools/placediff.py NEW.kicad_pcb            (OLD = the committed version, git HEAD:<file>)
       python3 tools/placediff.py REV NEW.kicad_pcb        (OLD = git REV:<file>, e.g. HEAD~2)
Exit 1 when anything differs, so a script can require it to list only the expected references."""
import os, re, subprocess, sys

def fps(text):
    out = {}
    for m in re.finditer(r'\(footprint "([^"]+)"(.*?)\n\t\)\n', text, re.S):
        blk = m.group(2)
        ref = re.search(r'\(property "Reference" "([^"]+)"', blk)
        at = re.search(r'\n\t\t\(at ([^)]+)\)', blk)
        layer = re.search(r'\(layer "([^"]+)"\)', blk)
        if ref: out[ref.group(1)] = (m.group(1).split(':')[-1][:24], at.group(1) if at else None, layer.group(1) if layer else None)
    return out

def git_show(rev, path):
    top = subprocess.run(['git', 'rev-parse', '--show-toplevel'], capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(path))).stdout.strip()
    rel = os.path.relpath(os.path.abspath(path), top)
    return subprocess.run(['git', 'show', f'{rev}:{rel}'], capture_output=True, text=True, cwd=top, check=True).stdout

args = sys.argv[1:]
if len(args) == 1: old, new = git_show('HEAD', args[0]), open(args[0]).read()
elif len(args) == 2 and not os.path.exists(args[0]): old, new = git_show(args[0], args[1]), open(args[1]).read()
elif len(args) == 2: old, new = open(args[0]).read(), open(args[1]).read()
else: sys.exit(__doc__)
a, b = fps(old), fps(new)
diff = [(r, a.get(r), b.get(r)) for r in sorted(set(a) | set(b)) if a.get(r) != b.get(r)]
print('changed:', len(diff))
for r, was, now in diff: print(f'  {r:8s} {was} -> {now}')
sys.exit(1 if diff else 0)
