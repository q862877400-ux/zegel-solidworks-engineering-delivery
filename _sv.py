import sys, io, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
c = type(sys)("sw_connect"); c.get_com_member = lambda o,n,*a,**k: None
sys.modules["sw_connect"] = c
spec = importlib.util.spec_from_file_location("sv", r"C:\swprojects\sw-skill-fork\scripts\sw_section_view.py")
m = importlib.util.module_from_spec(spec); sys.modules["sv"] = m
spec.loader.exec_module(m)
seen = []
def fake(o, n, *a, **k):
    seen.append((n, a))
    return {"FirstOffset": 2.5, "FirstRotationX": 30.0, "FirstRotationY": 0.0,
            "GetSnapShotNames": ["a", "b"], "GetAnnotationCount": 4}.get(n, None)
m.get_com_member = fake
print("  剖视证据:", m.collect_section_evidence(object()))
print("  读到的属性序列:", [n for n, _ in seen])
seen.clear()
print("  快照列表:", m.list_snapshots(object()))
print("  加快照实参:", seen[-1], " <- 确认是 AddSnapShot 大写 S")
try:
    m._call(m.MODEL_VIEW_MANAGER_ARITY, object(), "ActivateModelTab", 1)
    print("  [FAIL] 错 arity 未拦")
except ValueError:
    print("  [OK] 错 arity 被拦")
try:
    m._call(m.ANNOTATION_VIEW_ARITY, None, "Activate")
    print("  [FAIL] None 未拦")
except ValueError:
    print("  [OK] None 被拦")
