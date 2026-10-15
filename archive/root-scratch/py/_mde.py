import sys, io, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
c = type(sys)("sw_connect"); c.get_com_member = lambda o,n,*a,**k: None
sys.modules["sw_connect"] = c
p = type(sys)("sw_part"); p._select_by_id = lambda *a, **k: True
sys.modules["sw_part"] = p
spec = importlib.util.spec_from_file_location("mde", r"C:\swprojects\sw-skill-fork\scripts\sw_model_doc_extension.py")
m = importlib.util.module_from_spec(spec); sys.modules["mde"] = m
spec.loader.exec_module(m)
m.get_com_member = lambda o,n,*a,**k: (0 if n.startswith("NeedsRebuild") else 3)
print("  证据回读:", m.collect_extension_evidence(object()))
print("  select_all:", m.select_all(object()))
print("  cpm:", m.get_custom_property_manager(object(), ""))
print("  select_by_id 转发:", m.select_by_id(object(), "Face1", "FACE"))
for fn, args in ((m.get_custom_property_manager, ()), (m.select_all, (1,))):
    try:
        fn(object(), *args); print("  [FAIL] 错 arity 未被拦:", fn.__name__)
    except ValueError as e:
        print("  [OK] 错 arity 被拦:", fn.__name__)
