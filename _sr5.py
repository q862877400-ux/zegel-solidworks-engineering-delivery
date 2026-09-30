import sys, io, importlib.util, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
c = type(sys)("sw_connect"); c.get_com_member = lambda o,n,*a,**k: None
sys.modules["sw_connect"] = c
spec = importlib.util.spec_from_file_location("sr", r"C:\swprojects\sw-skill-fork\scripts\sw_sldworks_remaining.py")
m = importlib.util.module_from_spec(spec); sys.modules["sr"] = m
spec.loader.exec_module(m)
print("  该模块族数 =", len(m.FAMILIES))
