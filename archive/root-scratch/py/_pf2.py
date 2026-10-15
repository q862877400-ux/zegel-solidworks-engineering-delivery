import sys, io, importlib.util, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
c = type(sys)("sw_connect"); c.get_com_member = lambda o,n,*a,**k: getattr(o,n,None)
sys.modules["sw_connect"] = c
spec = importlib.util.spec_from_file_location("pf", r"C:\swprojects\sw-skill-fork\scripts\sw_part_features.py")
m = importlib.util.module_from_spec(spec); sys.modules["pf"] = m
spec.loader.exec_module(m)
print("  特征参数族 %d / 几何遍历族 %d / 事务族 %d" % (
    len(m.FEATURE_DATA_ARITY), len(m.GEOMETRY_ENTITY_ARITY), len(m.SELECTION_FAMILIES)))
print("  事务族:", m.SELECTION_FAMILIES)
src = open(r"C:\swprojects\sw-skill-fork\scripts\sw_part_features.py", encoding="utf-8").read()
bad = []
for fam, mem in sorted(set(re.findall(r'call_feature_data\(\s*[^,]+,\s*(?:self\._family|"(\w+)"),\s*"(\w+)"', src))):
    pass
for fam, mem in sorted(set(re.findall(r'call_feature_data\([^,]+,\s*family,\s*"(\w+)"', src))):
    ok = mem in m.FEATURE_DATA_ARITY.get(fam, {})
    print("    feature %-28s %-28s %s" % (fam, mem, "OK" if ok else "❌"))
    if not ok: bad.append((fam, mem))
for mem in ("GetGuideCurvesCount","GetBodyType","GetNormal"):
    tab = m.FEATURE_DATA_ARITY if mem=="GetGuideCurvesCount" else m.GEOMETRY_ENTITY_ARITY
    fam = "ISweepFeatureData" if mem=="GetGuideCurvesCount" else ("IBody2" if mem=="GetBodyType" else "IFace2")
    ok = mem in tab[fam]
    print("    %-16s in %-12s %s" % (mem, fam, "OK" if ok else "❌"))
    if not ok: bad.append((fam, mem))
for mem in ("AutoSelect","FeatureScope"):
    known = {n for v in m.FEATURE_DATA_PROPERTIES.values() for n in v}
    print("    直读 %-16s %s" % (mem, "OK" if mem in known else "❌ 不在属性表"))
print("  不一致 =", len(bad))
