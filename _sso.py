import sys, io, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
R = r"C:\swprojects\sw-skill-fork"
c = type(sys)("sw_connect"); c.get_com_member = lambda o,n,*a,**k: getattr(o,n,None)
sys.modules["sw_connect"] = c
spec = importlib.util.spec_from_file_location("sso", R + r"\scripts\sw_simulation_study_options.py")
m = importlib.util.module_from_spec(spec); sys.modules["sso"] = m
spec.loader.exec_module(m)
tot = sum(len(v) for v in m.STUDY_OPTION_SETTERS.values())
bt  = sum(len(v) for v in m.BOOLEAN_SETTERS.values())
print("  族 %d 个 / setter %d 个 / 布尔型 %d 个 / arity 表 %d 条"
      % (len(m.STUDY_OPTION_SETTERS), tot, bt, len(m.ARITY_TABLE)))
print("  静态研究族前 6 项:", list(m.STUDY_OPTION_SETTERS["ICWStaticStudyOptions"])[:6])
print("  静态研究布尔型:", m.BOOLEAN_SETTERS["ICWStaticStudyOptions"][:5])
