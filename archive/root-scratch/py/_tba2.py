import sys, io, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
c = type(sys)("sw_connect"); c.get_com_member = lambda o,n,*a,**k: None
sys.modules["sw_connect"] = c
spec = importlib.util.spec_from_file_location("tba", r"C:\swprojects\sw-skill-fork\scripts\sw_table_annotations.py")
m = importlib.util.module_from_spec(spec); sys.modules["tba"] = m
spec.loader.exec_module(m)
seen = []
m.get_com_member = lambda o, n, *a, **k: seen.append((n, a))
n = 0
for fam, table in m.TABLE_ANNOTATION_ARITY.items():
    for name, arity in table.items():
        m._call(object(), fam, name, *range(arity)); n += 1
print("  %d 项能力全部通过 arity 护栏；调用序列 %s" % (n, [x[0] for x in seen]))
for fn, args, label in (
    (m.underlying_features, (object(), "IHoleTableAnnotation", "Sort"), "错 arity(带法 Sort)"),
    (m.underlying_features, (object(), "ITableAnnotation", "GetText"), "未登记族"),
    (m.sort_table, (object(), "IBendTableAnnotation", 0, True), "无 Sort 的族"),
    (m.underlying_features, (None, "IFamilyTableAnnotation", "GetSheet"), "None 目标"),
):
    try:
        fn(*args); print("  [FAIL] %s 未拦" % label)
    except (KeyError, ValueError):
        print("  [OK] %s 被拦" % label)
