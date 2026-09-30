import sys, json, re
from collections import defaultdict
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.argv = ["x"]
import importlib.util
spec = importlib.util.spec_from_file_location("md", r"D:\AI\SW\merge_dims2.py")
md = importlib.util.module_from_spec(spec)
sys.modules["md"] = md
try:
    spec.loader.exec_module(md)
except SystemExit:
    pass
except Exception as e:
    pass
# 复现生成但落盘前先看
rows = json.loads(md.CENSUS.read_text(encoding="utf-8"))
short = md.short
ro, wo, hid, disp = defaultdict(set), defaultdict(set), defaultdict(set), defaultdict(dict)
for r in rows:
    f, n = short(r["type"]), r["name"]
    if r.get("hidden"): hid[f].add(n)
    if r.get("disp_id") is not None: disp[f][n] = r["disp_id"]
    if r["kind"] != "property": continue
    if r["can_write"] and not r["can_read"]: wo[f].add(n)
    elif r["can_read"] and not r["can_write"]: ro[f].add(n)
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_api_sldworks.py")
src = p.read_text(encoding="utf-8")
fams = re.findall(r"^    '(I\w+)': \{", src, re.M)
out = [src.rstrip("\n"), "", "", md.DOC.rstrip("\n"), ""]
for name, desc, ann in md.TABLES:
    lines = []
    for f in fams:
        if name == "DISPID":
            d = disp.get(f)
            if not d: continue
            lines.append("    %r: {" % f)
            for k, v in sorted(d.items()): lines.append("        %r: %d," % (k, v))
            lines.append("    },")
        else:
            pool = {"READONLY": ro, "WRITEONLY": wo, "HIDDEN": hid}[name].get(f)
            if not pool: continue
            for k in sorted(pool): lines.append("    %r: (%r,)," % (f, k))
    if not lines: continue
    out.append(md.render(name, desc, ann, "\n".join(lines) + "\n").rstrip("\n"))
text = "\n".join(out) + "\n"
ls = text.splitlines()
print("  生成总行数:", len(ls))
for i in range(3094, min(3108, len(ls))): print("  %5d| %s" % (i+1, ls[i]))