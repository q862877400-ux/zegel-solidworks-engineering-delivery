import sys, io, importlib.util, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
c = type(sys)("sw_connect"); c.get_com_member = lambda o,n,*a,**k: getattr(o,n,None)
sys.modules["sw_connect"] = c
spec = importlib.util.spec_from_file_location("ad", r"C:\swprojects\sw-skill-fork\scripts\sw_assembly_doc.py")
m = importlib.util.module_from_spec(spec); sys.modules["ad"] = m
spec.loader.exec_module(m)
print("  与「配合/移动/固定/解散/路径」相关的真实表项：")
for n, a in sorted(m.ASSEMBLY_DOC_ARITY.items()):
    if re.search(r"Suppress|Move|Fix|Dissolve|Path|Title|PathName|Component|Select", n):
        print("    %-38s %d" % (n, a))
print("  属性表：", list(m.ASSEMBLY_DOC_PROPERTIES))
