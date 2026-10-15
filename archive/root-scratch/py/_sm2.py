import sys, types, io, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
R = r"C:\swprojects\sw-skill-fork"
c = types.ModuleType("sw_connect"); c.get_com_member = lambda o, n, *a, **k: getattr(o, n, None)
sys.modules["sw_connect"] = c
p = types.ModuleType("sw_part"); p._ensure_sketch_selected = lambda *a, **k: None
sys.modules["sw_part"] = p
spec = importlib.util.spec_from_file_location("sm", R + r"\scripts\sw_sheet_metal.py")
m = importlib.util.module_from_spec(spec); sys.modules["sm"] = m
spec.loader.exec_module(m)
for bad, label in (
    (m.SweptFlangeSpec(thickness=0.001, start_offset=0.0, end_offset=0.1), "start_offset=0"),
    (m.SweptFlangeSpec(thickness=0.0, start_offset=0.1, end_offset=0.1), "thickness=0"),
    (m.SweptFlangeSpec(thickness=0.001, start_offset=0.1, end_offset=0.1, relief_ratio=0.0), "relief_ratio=0"),
):
    try:
        bad.validate(); print("  [FAIL] %s 未被拒绝" % label)
    except ValueError:
        print("  [OK] %s 被拒绝" % label)
ok = m.SweptFlangeSpec(thickness=0.001, start_offset=0.1, end_offset=0.2)
ok.validate(); print("  [OK] 合法参数通过")
