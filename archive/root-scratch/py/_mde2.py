import sys, io, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
c = type(sys)("sw_connect"); c.get_com_member = lambda o,n,*a,**k: None
sys.modules["sw_connect"] = c
p = type(sys)("sw_part"); p._select_by_id = lambda *a, **k: True
sys.modules["sw_part"] = p
spec = importlib.util.spec_from_file_location("mde", r"C:\swprojects\sw-skill-fork\scripts\sw_model_doc_extension.py")
m = importlib.util.module_from_spec(spec); sys.modules["mde"] = m
spec.loader.exec_module(m)
m.get_com_member = lambda o,n,*a,**k: 0
print("  arity 表:", {k: v for k, v in list(m.MDE_ARITY.items())[:5]}, "...")
# 直接打护栏
for member, bad in (("SelectByID2", 3), ("GetCustomPropertyManager", 5), ("SelectAll", 2)):
    try:
        m._checked(object(), member, *range(bad))
        print("  [FAIL] %s 错 arity 未被拦" % member)
    except ValueError as e:
        print("  [OK] %s 被拦" % member)
# None 目标
for member in ("SelectAll", "GetWhatsWrongCount"):
    try:
        m._checked(None, member); print("  [FAIL] None 未被拦")
    except ValueError:
        print("  [OK] None 被拦:", member)
