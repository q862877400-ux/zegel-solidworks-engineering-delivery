import sys, json, re, ast, importlib.util
from collections import defaultdict
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
rows = json.loads(Path(r"D:\AI\SW\interop-dimension-census.json").read_text(encoding="utf-8"))
def short(t):
    n = t.split(".")[-1]; return n[:-5] if n.endswith("Class") else n
wo, hid, disp = defaultdict(set), defaultdict(set), defaultdict(dict)
for r in rows:
    f, n = short(r["type"]), r["name"]
    if r.get("hidden"): hid[f].add(n)
    raw = r.get("disp_id")
    if raw is not None:
        try: disp[f][n] = int(str(raw).lstrip("="))
        except (TypeError, ValueError): pass
    if r["kind"] == "property" and r["can_write"] and not r["can_read"]: wo[f].add(n)
src = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_api_sldworks.py").read_text(encoding="utf-8")
ast.parse(src); print("  原始文件语法 OK，行数", len(src.splitlines()))
fams = re.findall(r"^    '(I\w+)': \{", src, re.M)
print("  族数", len(fams))
print("  其中有 DISPID 的族:", sum(1 for f in fams if disp.get(f)))
print("  其中有 HIDDEN 的族:", sum(1 for f in fams if hid.get(f)))
# 只拼 DISPID 试
lines = []
for f in fams:
    d = disp.get(f)
    if not d: continue
    lines.append("    %r: {" % f)
    for k, v in sorted(d.items()): lines.append("        %r: %d," % (k, v))
    lines.append("    },")
t = "DISPID: dict[str, dict[str, int]] = {\n" + "\n".join(lines) + "\n}\n"
ast.parse(t); print("  DISPID 表单独语法 OK，行数", len(lines))