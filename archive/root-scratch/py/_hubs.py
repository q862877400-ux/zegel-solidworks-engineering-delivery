import sys, io, importlib.util, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
c = type(sys)("sw_connect"); c.get_com_member = lambda o,n,*a,**k: getattr(o,n,None)
sys.modules["sw_connect"] = c
spec = importlib.util.spec_from_file_location("hubs", r"C:\swprojects\sw-skill-fork\scripts\sw_hubs.py")
m = importlib.util.module_from_spec(spec); sys.modules["hubs"] = m
spec.loader.exec_module(m)
print("  能力 %d / 族 %s" % (sum(len(v) for v in m.HUB_ARITY.values()), list(m.HUB_ARITY)))
src = open(r"C:\swprojects\sw-skill-fork\scripts\sw_hubs.py", encoding="utf-8").read()
refs = set(re.findall(r'call_hub\([^,]+,\s*"(\w+)",\s*"(\w+)"', src))
known = {n for t in m.HUB_ARITY.values() for n in t} | {n for v in m.HUB_PROPERTIES.values() for n in v}
print("  call_hub 引用:", sorted(refs))
for fam, mem in sorted(refs):
    ok = mem in m.HUB_ARITY.get(fam, {})
    print("    %-18s %-24s 在表里=%s" % (fam, mem, ok))
# 证据回读里的成员
for mem in ("FeatureCount","GetSolidFeatureCount","GetSurfaceFeatureCount","DefinitionTemplate",
            "GetPathName","GetTitle","GetSheetCount","GetCurrentSheet","GetFirstView","GetNextView"):
    print("    直读 %-24s %s" % (mem, "在某个表里" if mem in known else "❌ 不在表里"))
