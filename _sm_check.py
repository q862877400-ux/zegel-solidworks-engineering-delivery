import sys, types, io, importlib.util, dataclasses, inspect
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
R = r"C:\swprojects\sw-skill-fork"
c = types.ModuleType("sw_connect"); c.get_com_member = lambda o, n, *a, **k: getattr(o, n, None)
sys.modules["sw_connect"] = c
p = types.ModuleType("sw_part"); p._ensure_sketch_selected = lambda *a, **k: None
sys.modules["sw_part"] = p
spec = importlib.util.spec_from_file_location("sm", R + r"\scripts\sw_sheet_metal.py")
m = importlib.util.module_from_spec(spec)
sys.modules["sm"] = m
spec.loader.exec_module(m)
print("  FM ids: DRAFT=%d ONE_BEND=%d EDGE_FLANGE=%d SWEPT_FLANGE=%d GUSSET=%d (BASE_FLANGE=%d)"
      % (m.SW_FM_DRAFT, m.SW_FM_ONE_BEND, m.SW_FM_EDGE_FLANGE, m.SW_FM_SWEPT_FLANGE, m.SW_FM_SM_GUSSET, m.SW_FM_BASE_FLANGE))
for f in ("create_one_bend", "create_edge_flange", "create_draft", "create_gusset"):
    print("  %s%s" % (f, inspect.signature(getattr(m, f))))
for cls in ("OneBendSpec", "EdgeFlangeSpec", "DraftFeatureSpec", "GussetSpec"):
    print("  %s: %s" % (cls, [f.name for f in dataclasses.fields(getattr(m, cls))]))
for bad, msg in ((m.EdgeFlangeSpec(bend_radius=0.001, flange_length=0.0), "flange_length=0"),
                 (m.OneBendSpec(bend_radius=0.001, angle=400), "angle=400"),
                 (m.GussetSpec(thickness=0.0, profile_distance_1=0.01), "thickness=0")):
    try:
        bad.validate(); print("  [FAIL] %s 未被拒绝" % msg)
    except ValueError:
        print("  [OK] %s 被拒绝" % msg)
print("  [OK] 合法参数通过: %s" % (m.EdgeFlangeSpec(0.001, 0.02).validate() is None))
