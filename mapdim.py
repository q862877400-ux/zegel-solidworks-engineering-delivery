import json, sys
from pathlib import Path
from collections import defaultdict
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
rows = json.loads(Path(r"D:\AI\SW\interop-dimension-census.json").read_text(encoding="utf-8"))
# 按 (接口简名, 成员名) 归一，去掉 coclass 重复
def short(t):
    n = t.split(".")[-1]
    return n[:-5] if n.endswith("Class") else n
wo, ro, rw, hid, disp = defaultdict(set), defaultdict(set), defaultdict(set), defaultdict(set), {}
for r in rows:
    f, n = short(r["type"]), r["name"]
    if r["hidden"]: hid[f].add(n)
    if r.get("disp_id") is not None: disp[(f, n)] = r["disp_id"]
    if r["kind"] == "property":
        if r["can_write"] and not r["can_read"]: wo[f].add(n)
        elif r["can_read"] and not r["can_write"]: ro[f].add(n)
        elif r["can_read"]: rw[f].add(n)
print("  只写 %d / 只读 %d / 读写 %d / 内部使用 %d" % (
    sum(len(v) for v in wo.values()), sum(len(v) for v in ro.values()),
    sum(len(v) for v in rw.values()), sum(len(v) for v in hid.values())))
# 与我的索引对表：能配上多少
import re
S = Path(r"C:\swprojects\sw-skill-fork\scripts")
allf = {}
for p in sorted(S.glob("sw_api_*.py")):
    src = p.read_text(encoding="utf-8")
    for m in re.finditer(r"^    '(I\w+)': \{\n(.*?)\n    \},", src, re.M | re.S):
        f = m.group(1)
        meth = set(re.findall(r"^        '(\w+)': \d+,$", m.group(2), re.M))
        allf[f] = (p.name, meth)
print("  我的索引族数 =", len(allf))
# 只写/内部成员 落在哪些族
hit_wo = {f: sorted(wo[f] & allf[f][1]) for f in allf if wo[f] & allf[f][1]}
hit_hid = {f: sorted(hid[f] & allf[f][1]) for f in allf if hid[f] & allf[f][1]}
print()
print("  只写成员在我索引里能找到的族:", list(hit_wo) or "（只写都是属性，索引在 PROPERTIES 表里）")
print("  内部使用成员在我索引里的命中：")
for f, v in list(hit_hid.items())[:8]:
    print("    %-32s %s" % (f, ", ".join(v[:6])))
# 抽查 PROPERTIES 表能否配上
n_prop = 0; n_wo = 0
for p in S.glob("sw_api_*.py"):
    src = p.read_text(encoding="utf-8")
    for m in re.finditer(r"^    '(I\w+)': \(\n(.*?)\n    \),", src, re.M | re.S):
        f = m.group(1); props = set(re.findall(r"^        '(\w+)',$", m.group(2), re.M))
        n_prop += len(props); n_wo += len(props & wo.get(f, set()))
print()
print("  我的属性表共 %d 条，其中能标出只写的 %d 条" % (n_prop, n_wo))