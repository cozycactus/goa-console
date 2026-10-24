import pcbnew, json, sys
b = pcbnew.LoadBoard(sys.argv[1])
out = {}
for fp in b.GetFootprints():
    for p in fp.Pads():
        n = p.GetNetname()
        if not n: continue
        pos = p.GetPosition()
        out.setdefault(n, []).append([fp.GetReference(), p.GetNumber(), pos.x/1e6, pos.y/1e6, 'B' if fp.IsFlipped() else 'F'])
json.dump(out, open(sys.argv[2], 'w'), indent=0)
print(len(out))
