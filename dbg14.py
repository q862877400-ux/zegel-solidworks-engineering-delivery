import sys, json, re, ast
from collections import defaultdict
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
CENSUS = Path(r"D:\AI\SW\interop-dimension-census.json")
SCRIPTS = Path(r"C:\swprojects\sw-skill-fork\scripts")
rows = json.loads(CENSUS.read_text(encoding="utf-8"))
def short(t):
    n = t.split(".")[-1]; return n[:-5] if n.endswith("Class") else n
ro, wo, hid, disp = defaultdict(set), defaultdict(set), defaultdict(set), defaultdict(dict)
for r in rows:
    f, n = short(r["type"]), r["name"]
    if r.get("hidden"): hid[f].add(n)
    raw = r.get("disp_id")
    if raw is not None:
        try: disp[f][n] = int(str(raw).lstrip("="))
        except (TypeError, ValueError): pass
    if r["kind"] != "property": continue
    if r["can_write"] and not r["can_read"]: wo[f].add(n)
    elif r["can_read"] and not r["can_write"]: ro[f].add(n)
p = SCRIPTS / "sw_api_sldworks.py"
src = p.read_text(encoding="utf-8")
fams = re.findall(r"^    '(I\w+)': \{", src, re.M)
out = [src.rstrip("\n"), ""]
for label, pool_map in (("READONLY", ro), ("WRITEONLY", wo), ("HIDDEN", hid)):
    lines = []
    for f in fams:
        pool = pool_map.get(f)
        if not pool: continue
        for k in sorted(pool): lines.append("    %r: (%r,)," % (f, k))
    if lines: out.append("%s: dict[str, tuple[str, ...]] = {" % label)
    if lines: out.append("\n".join(lines))
    if lines: out.append("}")
    out.append("")
lines = []
for f in fams:
    d = disp.get(f)
    if not d: continue
    lines.append("    %r: {" % f)
    for k, v in sorted(d.items()): lines.append("        %r: %d," % (k, v))
    lines.append("    },")
out.append("DISPID: dict[str, dict[str, int]] = {")
out.append("\n".join(lines))
out.append("}")
text = "\n".join(out) + "\n"
Path(r"D:\AI\SW\_merged_test.py").write_text(text, encoding="utf-8")
try:
    ast.parse(text); print("  合并结果语法 OK，总行数", len(text.splitlines()))
except SyntaxError as e:
    ls = text.splitlines()
    print("  语法错:", e)
    a = max(0, e.lineno - 4)
    for i in range(a, min(e.lineno + 3, len(ls))):
        mark = ">>" if i + 1 == e.lineno else "  "
        print("   %s %5d| %s" % (mark, i + 1, ls[i][:100]))