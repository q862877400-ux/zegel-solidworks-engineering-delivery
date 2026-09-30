import json, sys
from pathlib import Path
from collections import Counter
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
d = json.loads(Path(r"D:\AI\SW\interop-dimension-census.json").read_text(encoding="utf-8"))
print("  条数:", len(d))
if d: print("  首条的键:", list(d[0].keys()))
for key in d[0].keys():
    vals = Counter()
    for r in d:
        v = r.get(key)
        if isinstance(v, list): vals["<list %d>" % len(v)] += 1
        else: vals[str(v)] += 1
    top = ", ".join(f"{k}={n}" for k, n in vals.most_common(5))
    print("   %-22s %s" % (key, top[:96]))