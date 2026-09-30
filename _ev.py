import sys, io, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
c = type(sys)("sw_connect"); c.get_com_member = lambda o,n,*a,**k: 0
sys.modules["sw_connect"] = c
spec = importlib.util.spec_from_file_location("h", r"C:\swprojects\sw-skill-fork\scripts\sw_hubs.py")
m = importlib.util.module_from_spec(spec); sys.modules["h"] = m
spec.loader.exec_module(m)
m.get_com_member = lambda o,n,*a,**k: 0
for fn, arg in ((m.collect_feature_manager_evidence, object()),
                (m.collect_drawing_doc_evidence, object())):
    try:
        r = fn(arg)
        print("  %s -> %s" % (fn.__name__, r))
    except Exception as e:
        print("  %s 失败: %s" % (fn.__name__, e))
