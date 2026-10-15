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
    print("    feature(dyn) %-26s %s" % (mem, "OK" if ok else "MISSING"))
    if not ok: bad.append(mem)
for fam, mem in sorted(set(re.findall(r'call_entity\([^,]+,\s*"(IFace2|IBody2)",\s*"(\w+)"', src))):
    ok = mem in m.GEOMETRY_ENTITY_ARITY[fam]
    print("    entity %-9s %-22s %s" % (fam, mem, "OK" if ok else "MISSING"))
    if not ok: bad.append((fam, mem))
known = {n for v in m.FEATURE_DATA_PROPERTIES.values() for n in v}
for mem in ("AutoSelect", "FeatureScope"):
    print("    direct %-24s %s" % (mem, "OK" if mem in known else "MISSING"))
    if mem not in known: bad.append(mem)
print("  mismatches =", len(bad), bad)
