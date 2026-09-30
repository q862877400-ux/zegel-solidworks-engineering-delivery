import sys, types, io, importlib.util, dataclasses, inspect
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
R = r"C:\swprojects\sw-skill-fork"
c = types.ModuleType("sw_connect"); c.get_com_member = lambda o, n, *a, **k: getattr(o, n, None)
sys.modules["sw_connect"] = c
p = types.ModuleType("sw_part"); p._ensure_sketch_selected = lambda *a, **k: None
sys.modules["sw_part"] = p
spec = importlib.util.spec_from_file_location("sm", R + r"\scripts\sw_sheet_metal.py")
m = importlib.util.module_from_spec(spec); sys.modules["sm"] = m
spec.loader.exec_module(m)
print("  SWS_SWEPT_FLANGE_POSITIONS:", m.SWS_SWEPT_FLANGE_POSITIONS)
print("  SweptFlangeSpec fields:", [f.name for f in dataclasses.fields(m.SweptFlangeSpec)])
print("  create_swept_flange%s" % (inspect.signature(m.create_swept_flange),))
# 默认（复现官方：thickness=None 表示从基体法兰继承）
m.SweptFlangeSpec(start_offset=0.0).validate(); print("  [OK] 官方默认（thickness=None, start_offset=0）通过")
for bad, lbl in ((m.SweptFlangeSpec(start_offset=-1), "start_offset=-1"),
                 (m.SweptFlangeSpec(start_offset=0, thickness=0), "thickness=0"),
                 (m.SweptFlangeSpec(start_offset=0, flange_position=9), "flange_position=9")):
    try:
        bad.validate(); print("  [FAIL] %s 未被拒绝" % lbl)
    except ValueError: print("  [OK] %s 被拒绝" % lbl)
