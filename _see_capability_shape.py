import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
d = json.loads(Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml").read_text(encoding="utf-8"))
caps = d["capabilities"]
print("  顶层键: %s" % list(d.keys()))
print()
#: 找一个 verified 的条目当模板
for c in caps:
    if c.get("id") == "sketch_query":
        print("  ── 模板（sketch_query）的键 ──")
        for k, v in c.items():
            t = type(v).__name__
            n = len(v) if isinstance(v, (list, str)) else ""
            print("    %-22s %s %s" % (k, t, ("(%d)" % n) if n != "" else ""))
        print()
        print("    level = %r" % c.get("level"))
        break
print()
print("  ── 所有条目的 level 分布 ──")
from collections import Counter
print("   ", dict(Counter(c.get("level") for c in caps)))
print()
print("  ── 一个 verified 条目的完整样子（取最短的）──")
vs = [c for c in caps if c.get("level") == "verified"]
vs.sort(key=lambda c: len(json.dumps(c, ensure_ascii=False)))
print(json.dumps(vs[0], ensure_ascii=False, indent=2)[:1200] if vs else "  （没有 verified）")
