import sys, io, importlib.util, types
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
c = type(sys)("sw_connect"); c.get_com_member = lambda o,n,*a,**k: getattr(o,n,None)
sys.modules["sw_connect"] = c
p = type(sys)("sw_part"); p._select_by_id = lambda *a, **k: True
sys.modules["sw_part"] = p
spec = importlib.util.spec_from_file_location("dc", r"C:\swprojects\sw-skill-fork\scripts\sw_document_core.py")
m = importlib.util.module_from_spec(spec); sys.modules["dc"] = m
spec.loader.exec_module(m)
print("  arity 表 %d 项 / 导出 %d 个" % (len(m.DOC_CORE_ARITY), len(m.__all__)))
seen = []
m.get_com_member = lambda o, n, *a, **k: (seen.append((n, a)) or "X")
class D: pass
m.collect_document_evidence(D())
print("  证据回读调用:", [n for n, _ in seen])
print("  select_by_id 转发:", m.select_by_id(D(), "Face1", "FACE"))
