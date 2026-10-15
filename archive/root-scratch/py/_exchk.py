import sys, types, io, importlib.util, inspect, ast
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, str(R / "scripts"))
c = types.ModuleType("sw_connect")
c.get_com_member = lambda o, n, *a, **k: getattr(o, n, None)
c.connect_solidworks = lambda *a, **k: (None, None)
c.new_document = lambda *a, **k: None
c.mm = lambda v: v; c.deg = lambda v: v
sys.modules["sw_connect"] = c
p = types.ModuleType("sw_part")
p._ensure_sketch_selected = lambda *a, **k: None
p._select_by_id = lambda *a, **k: True
p.start_sketch = lambda *a, **k: None
sys.modules["sw_part"] = p
mods = {}
for name in ("sw_part", "sw_sheet_metal", "sw_surface", "sw_simulation", "sw_connect"):
    mods[name] = importlib.import_module(name)
bad = 0
for f in ("09_sheet_metal", "10_surface_geometry", "11_simulation_study"):
    tree = ast.parse((R / "examples" / (f + ".py")).read_text(encoding="utf-8"))
    names = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom):
            names |= {a.name for a in n.names}
    for nm in sorted(names):
        ok = any(hasattr(m, nm) for m in mods.values())
        if not ok: bad += 1
        print("  %-28s %s" % (f + ":" + nm, "OK" if ok else "缺失"))
print("  缺失总数 =", bad)
