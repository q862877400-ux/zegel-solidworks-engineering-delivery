import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
t = P.read_text(encoding="utf-8")
d = json.loads(t)
print("  顶层键: %s" % sorted(d.keys()))
caps = d.get("capabilities") or []
print("  能力条目: %d" % len(caps))
import collections
print("  level 分布: %s" % dict(collections.Counter(c.get("level") for c in caps)))
for c in caps:
    if c.get("level") == "stitched":
        print()
        print("  ── stitched 样例: %s ──" % c.get("id"))
        print(json.dumps(c, ensure_ascii=False, indent=2)[:1400])
        break
# 最后一个条目的 id（用于插在哪）
print()
print("  最后一个条目 id: %s" % (caps[-1].get("id") if caps else None))
