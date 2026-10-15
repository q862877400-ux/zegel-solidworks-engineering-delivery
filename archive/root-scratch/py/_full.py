import sys, io, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
c = type(sys)("sw_connect"); c.get_com_member = lambda o,n,*a,**k: None
sys.modules["sw_connect"] = c
for name, path in (("sw_simulation_full", "sw_simulation_full.py"),
                   ("sw_pdm_full", "sw_pdm_full.py")):
    spec = importlib.util.spec_from_file_location(name, r"C:\swprojects\sw-skill-fork\scripts" + "\\" + path)
    m = importlib.util.module_from_spec(spec); sys.modules[name] = m
    spec.loader.exec_module(m)
    covered = [f for g in m.GROUPS.values() for f in g]
    print("  %-22s 族 %d / 组覆盖 %d / 恰好划分=%s / 能力 %d" % (
        name, len(m.FAMILIES), len(covered), set(covered) == set(m.FAMILIES),
        sum(len(v) for v in m.ARITY.values())))
    m.get_com_member = lambda o,n,*a,**k: None
    f0 = m.FAMILIES[0]
    ev = m.collect_evidence(object(), f0)
    print("     collect_evidence(%s) -> %s" % (f0, sorted(ev)[:4]))
