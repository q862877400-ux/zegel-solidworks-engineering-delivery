import sys, json, re, ast
from collections import defaultdict
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
spec = importlib.util.spec_from_file_location("md", r"D:\AI\SW\merge_dims2.py")
md = importlib.util.module_from_spec(spec); sys.modules["md"]=md
try: spec.loader.exec_module(md)
except SystemExit: pass
rows = json.loads(md.CENSUS.read_text(encoding="utf-8"))
short = md.short
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
src = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_api_sldworks.py").read_text(encoding="utf-8")
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
print("  生成行数:", len(ls))
for i in range(3092, min(3106, len(ls))): print("  %5d| %s" % (i+1, ls[i][:100]))