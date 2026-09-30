import sys, io, importlib.util, re
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
c = type(sys)("sw_connect"); c.get_com_member = lambda o,n,*a,**k: None
sys.modules["sw_connect"] = c
spec = importlib.util.spec_from_file_location("lg", r"C:\swprojects\sw-skill-fork\scripts\sw_sldworks_lastgap.py")
m = importlib.util.module_from_spec(spec); sys.modules["lg"] = m
spec.loader.exec_module(m)
print("  sw_sldworks_lastgap: %d 族 / 能力 %d / 属性 %d / 分组覆盖=%s" % (
    len(m.FAMILIES), sum(len(v) for v in m.ARITY.values()),
    sum(len(v) for v in m.PROPERTIES.values()),
    set(f for g in m.GROUPS.values() for f in g) == set(m.FAMILIES)))
