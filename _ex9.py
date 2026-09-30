import sys, types, io, importlib.util, inspect
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
R = r"C:\swprojects\sw-skill-fork"
c = types.ModuleType("sw_connect")
c.get_com_member = lambda o, n, *a, **k: getattr(o, n, None)
c.connect_solidworks = lambda *a, **k: (None, False)
c.new_document = lambda *a, **k: None
c.mm = lambda v: v
c.deg = lambda v: v
sys.modules["sw_connect"] = c
p = types.ModuleType("sw_part"); p._ensure_sketch_selected = lambda *a, **k: None
p._select_by_id = lambda *a, **k: True
p.start_sketch = lambda *a, **k: None
sys.modules["sw_part"] = p
sys.path.insert(0, R + r"\scripts")
for mod, names in (("sw_part", ["_select_by_id"]), ("sw_sheet_metal", ["create_base_flange","create_swept_flange","sheet_metal_evidence"]), ("sw_connect", ["connect_solidworks","new_document"])):
    m = importlib.import_module(mod)
    for n in names:
        f = getattr(m, n, None)
        print("  %-22s %s" % (mod + "." + n, inspect.signature(f) if f else "❌ 不存在"))
import dataclasses, sw_sheet_metal as sm
for cls in ("BaseFlangeSpec", "SweptFlangeSpec"):
    k = getattr(sm, cls)
    req = [fl.name for fl in dataclasses.fields(k) if fl.default is dataclasses.MISSING]
    print("  %-22s 必填字段: %s" % (cls, req))
