import sys, io, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
c = type(sys)("sw_connect"); c.get_com_member = lambda o,n,*a,**k: getattr(o,n,None)
sys.modules["sw_connect"] = c
p = type(sys)("sw_part"); p._select_by_id = lambda *a, **k: True
sys.modules["sw_part"] = p
spec = importlib.util.spec_from_file_location("dc", r"C:\swprojects\sw-skill-fork\scripts\sw_document_core.py")
m = importlib.util.module_from_spec(spec); sys.modules["dc"] = m
spec.loader.exec_module(m)
INT_MEMBERS = {"GetUnits"}
seen = []
def fake(o, n, *a, **k):
    seen.append((n, a))
    if n in INT_MEMBERS: return 4
    return "VAL"
m.get_com_member = fake
class D: pass
print("  证据回读:", m.collect_document_evidence(D()))
print("  调用序列:", [n for n, _ in seen])
print("  select_by_id 转发:", m.select_by_id(D(), "Face1", "FACE"))
# 护栏：错 arity 应被拦
try:
    m.get_open_document(D())
    print("  [FAIL] 错 arity 未被拦")
except ValueError as e:
    print("  [OK] 错 arity 被拦:", str(e)[:50])
