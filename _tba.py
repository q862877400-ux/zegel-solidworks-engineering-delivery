import sys, io, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
c = type(sys)("sw_connect"); c.get_com_member = lambda o,n,*a,**k: None
sys.modules["sw_connect"] = c
spec = importlib.util.spec_from_file_location("tba", r"C:\swprojects\sw-skill-fork\scripts\sw_table_annotations.py")
m = importlib.util.module_from_spec(spec); sys.modules["tba"] = m
spec.loader.exec_module(m)
seen = []
m.get_com_member = lambda o, n, *a, **k: seen.append((n, a))
for fam, mem in m.list_registered_families().items():
    for name in mem:
        m.underlying_features(object(), fam, name)
print("  登记族:", len(m.TABLE_ANNOTATION_ARITY), "项能力调用全部通过护栏")
print("  调用序列:", [n for n, _ in seen])
try:
    m.underlying_features(object(), "ITableAnnotation", "GetText")
    print("  [FAIL] 未登记族未拦")
except KeyError as e:
    print("  [OK] 未登记族被拦")
try:
    m.sort_table(object(), "IBendTableAnnotation", 0, True)
    print("  [FAIL] 无 Sort 的族未拦")
except KeyError:
    print("  [OK] 无 Sort 的族被拦")
