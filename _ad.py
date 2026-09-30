import sys, io, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
c = type(sys)("sw_connect"); c.get_com_member = lambda o,n,*a,**k: getattr(o,n,None)
sys.modules["sw_connect"] = c
spec = importlib.util.spec_from_file_location("ad", r"C:\swprojects\sw-skill-fork\scripts\sw_assembly_doc.py")
m = importlib.util.module_from_spec(spec); sys.modules["ad"] = m
spec.loader.exec_module(m)
print("  能力 %d / 属性 %d" % (len(m.ASSEMBLY_DOC_ARITY), len(m.ASSEMBLY_DOC_PROPERTIES)))
print("  显式封装引用的成员是否在表里：")
for n in ("SuppressMate2","MoveComponent","FixComponent","DissolveAll","GetPathName",
          "GetTitle","GetComponentCount","GetSuppressions","GetLightweightComponentCount"):
    print("    %-32s %s" % (n, n in m.ASSEMBLY_DOC_ARITY or n in m.ASSEMBLY_DOC_PROPERTIES))
