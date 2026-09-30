import sys, json, re, ast
from collections import defaultdict
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
rows = json.loads(Path(r"D:\AI\SW\interop-dimension-census.json").read_text(encoding="utf-8"))
def short(t):
    n = t.split(".")[-1]
    return n[:-5] if n.endswith("Class") else n
ro, wo, hid, disp = defaultdict(set), defaultdict(set), defaultdict(set), defaultdict(dict)
for r in rows:
    f, n = short(r["type"]), r["name"]
    if r.get("hidden"): hid[f].add(n)
    if r.get("disp_id") is not None: disp[f][n] = r["disp_id"]
    if r["kind"] != "property": continue
    if r["can_write"] and not r["can_read"]: wo[f].add(n)
    elif r["can_read"] and not r["can_write"]: ro[f].add(n)
src = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_api_sldworks.py").read_text(encoding="utf-8")
fams = re.findall(r"^    '(I\w+)': \{", src, re.M)
# 手工拼一个最小的 WRITEONLY 表看看格式
lines = []
for f in fams:
    pool = wo.get(f)
    if not pool: continue
    for k in sorted(pool): lines.append("    %r: (%r,)," % (f, k))
body = "\n".join(lines) + "\n"
text = "WRITEONLY: dict[str, tuple[str, ...]] = {" + body + "}\n"
print("拼接片段（前后各 3 行）:")
ls = text.splitlines()
for i in range(0, min(6, len(ls))): print("  %3d| %s" % (i+1, ls[i]))
print("  ...")
for i in range(max(0,len(ls)-4), len(ls)): print("  %3d| %s" % (i+1, ls[i]))
try:
    ast.parse(text); print("  ✅ 这一段语法 OK")
except SyntaxError as e:
    print("  ❌ 语法错:", e)