import sys, io, importlib.util, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
c = type(sys)("sw_connect"); c.get_com_member = lambda o,n,*a,**k: getattr(o,n,None)
sys.modules["sw_connect"] = c
spec = importlib.util.spec_from_file_location("ss", r"C:\swprojects\sw-skill-fork\scripts\sw_sketch_sheetmetal.py")
m = importlib.util.module_from_spec(spec); sys.modules["ss"] = m
spec.loader.exec_module(m)
m.get_com_member = lambda o,n,*a,**k: None
print("  草图 %d 族 / 钣金 %d 族 / 能力 %d / 属性 %d / 事务族 %d" % (
    len(m.SKETCH_ARITY), len(m.SHEET_METAL_ARITY),
    sum(len(v) for v in m.SKETCH_ARITY.values())+sum(len(v) for v in m.SHEET_METAL_ARITY.values()),
    sum(len(v) for v in m.SKETCH_PROPERTIES.values())+sum(len(v) for v in m.SHEET_METAL_PROPERTIES.values()),
    len(m.SHEET_METAL_SELECTION_FAMILIES)))
for f, a in ((m.collect_sketch_evidence, ()), (m.collect_sheet_metal_evidence, ("IBaseFlangeFeatureData",))):
    try:
        print("    %s -> %s" % (f.__name__, f(object(), *a)))
    except Exception as e:
        print("    %s 失败: %s" % (f.__name__, e))
