import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
D = Path(r"D:\AI\SW\cadir")
for f in sorted(D.glob("*.json")):
    if "fidelity" in f.name:
        continue
    d = json.loads(f.read_text(encoding="utf-8"))
    print("=== %s" % f.name[:56])
    print("    顶层键:", list(d)[:12])

    def walk(o, path="", depth=0):
        if depth > 4:
            return
        if isinstance(o, dict):
            for k, v in o.items():
                p = f"{path}.{k}" if path else k
                if re.search(r"config|param|equation|variable|size", k, re.I):
                    s = json.dumps(v, ensure_ascii=False)[:150]
                    print("    %-46s %s" % (p[:46], s))
                walk(v, p, depth + 1)
        elif isinstance(o, list):
            for i, v in enumerate(o[:12]):
                walk(v, f"{path}[{i}]", depth + 1)

    walk(d)
    print()
