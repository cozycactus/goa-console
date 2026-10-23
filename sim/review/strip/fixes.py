"""Candidate capacitors (name, node1, node2, value)."""
FB = (('CF_U6A', 'EQ_O4', 'EQ_M4'),     # across R55 (U6A feedback 22K)
      ('CF_U6B', 'EQ_O5', 'EQ_L4'),     # across R59 (U6B feedback 22K)
      ('CF_U7A', 'EQ_O6', 'EQ_F4'),     # across R67 (U7A feedback 22K)
      ('CF_U12A', 'EQ_MHP', 'EQ_MSM'),  # across R83 (KHN summer feedback 10K)
      ('CF_U13B', 'EQ_LHP', 'EQ_LSM'))  # across R92
GND = (('CG_U2B', 'PANWL', '0'), ('CG_U3A', 'PANWR', '0'), ('CG_U3B', 'M2', '0'),
       ('CG_U2A', 'FPIN', '0'), ('CG_U8A', 'DIRSRC', '0'))
RX = (('CB_U1A', 'U1A_P', '0'),)       # across R9: balances C7 33p across R7

def mk(fb=None, gnd=None, rx=None, only=None):
    L = []
    if fb: L += [(n, a, b, fb) for n, a, b in FB if not only or n in only]
    if gnd: L += [(n, a, b, gnd) for n, a, b in GND if not only or n in only]
    if rx: L += [(n, a, b, rx) for n, a, b in RX]
    return L

FIXSETS = {'none': []}
for v in ('10p', '22p', '33p', '47p', '100p'):
    FIXSETS[f'fb{v}'] = mk(fb=v)
for v in ('22p', '47p', '100p', '220p'):
    FIXSETS[f'gnd{v}'] = mk(gnd=v)
for v in ('22p', '33p', '47p', '100p'):
    FIXSETS[f'rx{v}'] = mk(rx=v)

# ad-hoc sets: 'CF_U12A=10p+CP_U12A=47p' etc.
NODES = {n: (a, b) for n, a, b in FB + GND + RX}
NODES.update({'CP_U12A': ('EQ_MSP', '0'), 'CP_U13B': ('EQ_LSP', '0'),           # + node of the KHN summers to AGND
              'CS_U12A': ('EQ_MP', 'EQ_MSP'), 'CS_U13B': ('EQ_LP', 'EQ_LSP'),  # across R84 / R93
              'CM_U12A': ('EQ_MSM', '0'), 'CM_U13B': ('EQ_LSM', '0'),
              'CI_U6A': ('EQ_O3', 'EQ_M4'), 'CI_U6B': ('EQ_O4', 'EQ_L4'), 'CI_U7A': ('EQ_O5', 'EQ_F4'),   # across R54 / R58 / R66
              'CI1_U12A': ('EQ_WHM', 'EQ_MSM'), 'CI2_U12A': ('EQ_MLP', 'EQ_MSM'),                       # across R81 / R82
              'CI1_U13B': ('EQ_WLM', 'EQ_LSM'), 'CI2_U13B': ('EQ_LLP', 'EQ_LSM')})                      # across R90 / R91
class _FS(dict):
    def __missing__(self, key):
        out = []
        for item in key.split('+'):
            n, v = item.split('=')
            if n == 'FB': out += [(m, a, b, v) for m, a, b in FB]
            elif n == 'KHN': out += [(m, a, b, v) for m, a, b in FB if m in ('CF_U12A', 'CF_U13B')]
            elif n == 'EQ': out += [(m, a, b, v) for m, a, b in FB if m in ('CF_U6A', 'CF_U6B', 'CF_U7A')]
            elif n == 'GND': out += [(m, a, b, v) for m, a, b in GND]
            elif n == 'CP': out += [(m, *NODES[m], v) for m in ('CP_U12A', 'CP_U13B')]
            elif n == 'CS': out += [(m, *NODES[m], v) for m in ('CS_U12A', 'CS_U13B')]
            elif n == 'CI': out += [(m, *NODES[m], v) for m in ('CI_U6A', 'CI_U6B', 'CI_U7A')]
            elif n == 'CIK': out += [(m, *NODES[m], v) for m in ('CI1_U12A', 'CI2_U12A', 'CI1_U13B', 'CI2_U13B')]
            else: out.append((n, *NODES[n], v))
        d = {}
        for x in out: d[x[0]] = x          # a later entry overrides an earlier one
        return list(d.values())
FIXSETS = _FS(FIXSETS)

FINAL = 'EQ=10p+KHN=10p+CP=22p+GND=10p+CB_U1A=33p'
FINAL22 = 'CF_U6A=10p+CF_U6B=10p+CF_U7A=22p+KHN=10p+CP=22p+GND=10p+CB_U1A=33p'
REC = ('CF_U6A=10p+CI_U6A=10p+CF_U6B=10p+CI_U6B=10p+CF_U7A=10p+CI_U7A=10p+CF_U12A=10p+CP_U12A=22p+CF_U13B=10p+CP_U13B=22p'
       '+CB_U1A=33p+CG_U2B=10p+CG_U3A=10p+CG_U3B=10p+CG_U2A=10p+CG_U8A=22p')
FIXSETS['rec'] = FIXSETS[REC]
REC1 = ('CF_U6A=10p+CF_U6B=10p+CF_U7A=10p+CF_U12A=10p+CP_U12A=22p+CF_U13B=10p+CP_U13B=22p'
        '+CB_U1A=33p+CG_U2B=10p+CG_U3A=10p+CG_U3B=10p+CG_U2A=10p+CG_U8A=22p')
FIXSETS['rec1'] = FIXSETS[REC1]      # single feedback cap on the Delta EQ stages (moves the EQ by <= 0.27 dB)
RECF = ('CF_U6A=10p+CI_U6A=10p+CF_U6B=10p+CI_U6B=10p+CF_U7A=22p+CF_U12A=10p+CP_U12A=22p+CF_U13B=10p+CP_U13B=22p'
        '+CB_U1A=33p+CG_U2B=10p+CG_U3A=10p+CG_U3B=10p+CG_U2A=10p+CG_U8A=22p')
FIXSETS['recF'] = FIXSETS[RECF]
