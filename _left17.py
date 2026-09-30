import importlib.util, io, re, sys, types
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
REPO = Path(r"C:\swprojects\sw-skill-fork")
SW = Path(r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt")
txt = SW.read_text(encoding="utf-8", errors="replace")
SIG = re.compile(r"^\S+\s+(\w+)\s*\((.*)\)$")
def com(n): return re.sub(r"^(get|set)_", "", n)
# 按族建池
pool = {}
cur = None
for raw in txt.splitlines():
    if raw.startswith("## "):
        cur = raw[3:].strip()
    elif cur and raw.strip():
        m = SIG.match(raw.strip())
        if m:
            params=[a.strip() for a in m.group(2).split(",") if a.strip()]
            pool.setdefault(cur, {}).setdefault(com(m.group(1)), []).append(
                len([a for a in params if not a.endswith("&")]))
def load(n):
    c=types.ModuleType("sw_connect"); c.get_com_member=lambda o,nm,*a,**k: None
    sys.modules.setdefault("sw_connect",c)
    sp=importlib.util.spec_from_file_location(n, REPO/"scripts"/f"{n}.py")
    m=importlib.util.module_from_spec(sp); sys.modules[n]=m; sp.loader.exec_module(m); return m
for mod in ("sw_drawing_annotations","sw_part_features","sw_sketch_sheetmetal","sw_geometry"):
    m = load(mod)
    src = (REPO/"scripts"/f"{mod}.py").read_text(encoding="utf-8")
    for fam in sorted(set(re.findall(r"'(\w+)':\s*\{", src))):
        if fam not in pool: continue
        for member, arity in list(m.__dict__.items()): pass
        # 从模块常量里取
        for attr in dir(m):
            v = getattr(m, attr)
            if not isinstance(v, dict): continue
            sub = v.get(fam) if all(isinstance(x, dict) for x in v.values() if x) else v
            if not isinstance(sub, dict): continue
            for mem, ar in sub.items():
                if mem in pool[fam] and ar not in pool[fam][mem]:
                    print("  %-24s %-30s %-30s 表%d 反射%s" % (mod, fam, mem, ar, pool[fam][mem]))
