import sys, io, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
c = type(sys)("sw_connect"); c.get_com_member = lambda o,n,*a,**k: None
sys.modules["sw_connect"] = c
spec = importlib.util.spec_from_file_location("ad", r"C:\swprojects\sw-skill-fork\scripts\sw_assembly_doc.py")
m = importlib.util.module_from_spec(spec); sys.modules["ad"] = m
spec.loader.exec_module(m)
print("  能力 = %d (期望 133)" % len(m.ASSEMBLY_DOC_ARITY))
print("  属性 = %d (期望 13)" % len(m.ASSEMBLY_DOC_PROPERTIES))
