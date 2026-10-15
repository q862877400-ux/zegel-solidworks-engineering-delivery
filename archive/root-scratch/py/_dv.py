import sys, io, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
c = type(sys)("sw_connect"); c.get_com_member = lambda o,n,*a,**k: getattr(o,n,None)
sys.modules["sw_connect"] = c
spec = importlib.util.spec_from_file_location("dv", r"C:\swprojects\sw-skill-fork\scripts\sw_drawing_view.py")
m = importlib.util.module_from_spec(spec); sys.modules["dv"] = m
spec.loader.exec_module(m)
print("  能力登记表 %d 项 / 属性名 %d 项" % (len(m.VIEW_MEMBER_ARITY), len(m.VIEW_PROPERTY_NAMES)))
print("  零参能力数 =", sum(1 for v in m.VIEW_MEMBER_ARITY.values() if v == 0))
print("  前 6 项:", list(m.VIEW_MEMBER_ARITY)[:6])
print("  属性前 6 项:", list(m.VIEW_PROPERTY_NAMES)[:6])
