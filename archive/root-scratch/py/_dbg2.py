import io, sys, importlib.util
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
spec = importlib.util.spec_from_file_location("b", r"D:\AI\SW\build_complete_index.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
import re
# 只生成第一个程序集看看
asm, path = "fworks", m.SRC["fworks"]
fams, cur = {}, None
for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
    if raw.startswith("## "):
        cur = raw[3:].strip(); fams.setdefault(cur, {"methods": [], "props": []}); continue
    if not cur or not raw.strip(): continue
    g = m.SIG.match(raw.strip())
    if not g: continue
    name, params = g.group(1), g.group(2)
    if name.startswith(("get_","set_")):
        fams[cur]["props"].append(name[4:]); continue
    if m.INTERNAL.match(name): continue
    real = len([a for a in (p.strip() for p in params.split(",")) if a and not a.endswith("&")])
    fams[cur]["methods"].append((name, real))
order = sorted(f for f,v in fams.items() if v["methods"] or v["props"])
nm = sum(len(fams[f]["methods"]) for f in order)
body = m.HEADER.format(asm=asm, domain=m.DESC[asm], n_fam=len(order), n_members=nm,
                        refl=path, dll=m.DLL[asm])
lines = body.splitlines()
print("HEADER 行数 =", len(lines))
for i in (len(lines)-6, len(lines)-5, len(lines)-4, len(lines)-3, len(lines)-2, len(lines)-1):
    print("  %3d| %s" % (i+1, lines[i]))
