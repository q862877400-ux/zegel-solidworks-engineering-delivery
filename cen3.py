import json, sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
rows = json.loads(Path(r"D:\AI\SW\interop-dimension-census.json").read_text(encoding="utf-8"))
props = [r for r in rows if r["kind"] == "property"]
wo = [r for r in props if r["can_write"] and not r["can_read"]]
hid = [r for r in rows if r["hidden"]]
print("  属性总数 =", len(props))
print("    只读  =", sum(1 for r in props if r["can_read"] and not r["can_write"]))
print("    读写  =", sum(1 for r in props if r["can_read"] and r["can_write"]))
print("    只写  =", len(wo))
print()
print("  ★ 只写属性清单（去重 IXxx/XxxClass 后）：")
names = sorted({(r["type"].split(".")[-1].replace("Class",""), r["name"]) for r in wo})
seen = set()
for t, n in names:
    if n in seen: continue
    seen.add(n)
    print("    %-30s %s" % (t, n))
print()
print("  内部使用(hidden)成员 =", len(hid), "去重后:",
      len({(r['type'].split('.')[-1].replace('Class',''), r['name']) for r in hid}))
# 落到我的索引上：多少条能被配上维度
import re
tot = 0
for p in sorted(Path(r"C:\swprojects\sw-skill-fork\scripts").glob("sw_api_*.py")):
    tot += len(re.findall(r"^        '(\w+)': \d+,$", p.read_text(encoding="utf-8"), re.M))
print()
print("  我的索引能力成员数 =", tot, "（普查里 property 类 =", len(props), "）")