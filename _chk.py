import sys, io, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
c = type(sys)("sw_connect"); c.get_com_member = lambda o,n,*a,**k: None
sys.modules["sw_connect"] = c
spec = importlib.util.spec_from_file_location("sr", r"C:\swprojects\sw-skill-fork\scripts\sw_simulation_registry.py")
m = importlib.util.module_from_spec(spec); sys.modules["sr"] = m
spec.loader.exec_module(m)
seen = []
for g in (m.STUDY_AND_LOADS_FAMILIES, m.MESH_AND_RESULTS_FAMILIES, m.SOLVER_OPTION_FAMILIES):
    seen += list(g)
print("  族 %d / 三组合计 %d / 覆盖全部 = %s" % (len(m.SIM_FAMILIES), len(seen), set(seen) == set(m.SIM_FAMILIES)))
print("  未覆盖:", sorted(set(m.SIM_FAMILIES) - set(seen)))
