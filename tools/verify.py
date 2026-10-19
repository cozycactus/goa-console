import re, json, sys, collections

def sexp(text):  # minimal s-expression parser; handles KiCad 7 (one-line) and KiCad 8+ (indented) netlists
    stack, cur = [], []
    for tok in re.finditer(r'\(|\)|"((?:[^"\\]|\\.)*)"|[^\s()"]+', text):
        t = tok.group(0)
        if t == '(': stack.append(cur); cur = []
        elif t == ')': done = cur; cur = stack.pop(); cur.append(done)
        else: cur.append(tok.group(1) if tok.group(1) is not None else t)
    return cur[0]

def field(node, key):
    return next((c[1] for c in node[1:] if isinstance(c, list) and c and c[0] == key), None)

if __name__ == '__main__':
    tree = sexp(open(sys.argv[1]).read()); want = json.load(open(sys.argv[2]))
    nets = next(c for c in tree[1:] if isinstance(c, list) and c[0] == 'nets')
    got = {}
    for n in nets[1:]:
        name = field(n, 'name').lstrip('/')
        for nd in n[1:]:
            if isinstance(nd, list) and nd[0] == 'node': got[f"{field(nd, 'ref')}.{field(nd, 'pin')}"] = name
    bad = []
    for k, n in want.items():
        if k.startswith('#FLG'): continue
        g = got.get(k)
        if n == 'NC':
            if g is not None and not g.startswith('unconnected'): bad.append((k, n, g))
        elif g != n: bad.append((k, n, g))
    # pins present in netlist but not intended
    extra = [k for k in got if k not in want and not k.startswith('#')]
    nets = collections.Counter(v for k, v in want.items() if v != 'NC' and not k.startswith('#FLG'))
    single = [n for n, c in nets.items() if c == 1]
    print('pins checked:', len(want), ' mismatches:', len(bad), ' unexpected pins:', len(extra))
    for b in bad[:20]: print('  MISMATCH', b)
    for e in extra[:20]: print('  UNEXPECTED', e, got[e])
    print('nets with a single pin (check intent):', single)
    sys.exit(1 if bad or extra else 0)
