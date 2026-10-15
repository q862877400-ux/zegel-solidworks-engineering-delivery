import re, sys, io
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
SW = Path(r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt")
SIG = re.compile(r"^\S+\s+(\w+)\s*\((.*)\)$")
pool = {}
for fam in ("IView",):
    cur = None
    for raw in SW.read_text(encoding="utf-8", errors="replace").splitlines():
        if raw.startswith("## "):
            if cur == fam: break
            cur = raw[3:].strip()
            if cur == fam: pool = {}
        elif cur == fam and raw.strip():
            m = SIG.match(raw.strip())
            if m:
                nm = re.sub(r"^(get|set)_", "", m.group(1))
                ps = [a.strip() for a in m.group(2).split(",") if a.strip()]
                n = len([a for a in ps if not a.endswith("&")])
                lst = pool.setdefault(nm, [])
                if n not in lst: lst.append(n)
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_drawing_view.py")
lines = p.read_text(encoding="utf-8").splitlines()
ROW = re.compile(r"^(\s+)(['\"])([A-Za-z_]\w*)\2(\s*:\s*)(\d+)(\s*,?\s*)$")
n = 0
for i, line in enumerate(lines):
    rm = ROW.match(line)
    if not rm: continue
    mem, old = rm.group(3), int(rm.group(5))
    real = pool.get(mem)
    if not real or old in real: continue
    lines[i] = f"{rm.group(1)}{rm.group(2)}{mem}{rm.group(2)}{rm.group(4)}{real[0]}{rm.group(6)}"
    print("  %-32s %d -> %s" % (mem, old, real))
    n += 1
p.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("共修", n)
