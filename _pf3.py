import sys, io, importlib.util, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
c = type(sys)("sw_connect"); c.get_com_member = lambda o,n,*a,**k: getattr(o,n,None)
sys.modules["sw_connect"] = c
spec = importlib.util.spec_from_file_location("pf", r"C:\swprojects\sw-skill-fork\scripts\sw_part_features.py")
m = importlib.util.module_from_spec(spec); sys.modules["pf"] = m
spec.loader.exec_module(m)
src = open(r"C:\swprojects\sw-skill-fork\scripts\sw_part_features.py", encoding="utf-8").read()
bad = []
for mem in sorted(set(re.findall(r'call_feature_data\([^,]+,\s*family,\s*"(\w+)"', src))):
    ok = any(mem in t for t in m.FEATURE_DATA_ARITY.values())
    print("    feature(动态族) %-28s %s" % (mem, "OK" if ok else "❌"))
    if not ok: bad.append(mem)
for mem in sorted(set(re.findall(r'call_entity\([^,]+,\s*"(IFace2|IBody2)",\s*"(\w+)"', src)) and
                      [x[1] for x in re.findall(r'call_entity\([^,]+,\s*"(IFace2|IBody2)",\s*"(\w+)"', src)])):
    tab = m.GEOMETRY_ENTITY_ARITY
    ok = any(mem in t for t in tab.values())
    print("    entity              %-28s %s" % (mem, "OK" if ok else "❌"))
    if not ok: bad.append(mem)
for mem in ("AutoSelect","FeatureScope"):
    known = {n for v in m.FEATURE_DATA_PROPERTIES.values() for n in v}
    print("    直读 %-22s %s" % (mem, "OK" if mem in known else "❌"))
    if mem not in known: bad.append(mem)
print("  不一致 =", len(bad), bad)
