import sys, io, importlib.util, inspect
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
R = r"C:\swprojects\sw-skill-fork"
c = type(sys)("sw_connect"); c.get_com_member = lambda o,n,*a,**k: getattr(o,n,None)
sys.modules["sw_connect"] = c
spec = importlib.util.spec_from_file_location("sll", R + r"\scripts\sw_simulation_loads.py")
m = importlib.util.module_from_spec(spec); sys.modules["sll"] = m
spec.loader.exec_module(m)
print("  导出 %d 个" % len(m.__all__))
print("  签名表 %d 项" % len(m.OFFICIAL_LOAD_SIGNATURES))
for k in ("SWS_RESTRAINT_TYPES","SWS_FORCE_TYPES","SWS_PRESSURE_TYPES","SWS_RADIATION_TYPES","SWS_SPRING_SUBTYPES"):
    d = getattr(m,k); print("  %-24s %d 项  抽查 %s" % (k, len(d), list(d.items())[:2]))
print("  夹具:", m.SWS_RESTRAINT_TYPES["fixed"], m.SWS_RESTRAINT_TYPES["reference_geometry"])
# arity 校核器是否真的生效（故意传错个数）
try:
    m.add_pressure(object.__new__(object), "E")
    print("  [FAIL] 校核器没拦住")
except AttributeError:
    print("  [OK] 校核器在调用前就拦住了（还没碰 COM）")
