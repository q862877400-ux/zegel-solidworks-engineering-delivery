import sys, io, re
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW\tools")
import gen_family_coverage as g
c = Counter()
where = {}
for dom, fams in g.DOMAIN_FAMILIES.items():
    for f in fams:
        c[f] += 1
        where.setdefault(f, []).append(dom)
dupes = {k: v for k, v in where.items() if len(v) > 1}
print("  被重复登记的族 =", len(dupes))
for k, v in sorted(dupes.items()):
    print("    %-28s -> %s" % (k, " / ".join(v)))
