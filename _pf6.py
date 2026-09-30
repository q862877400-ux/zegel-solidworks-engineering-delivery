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
    if not any(mem in t for t in m.FEATURE_DATA_ARITY.values()): bad.append(mem)
for fam, mem in sorted(set(re.findall(r'call_entity\([^,]+,\s*"(IFace2|IBody2)",\s*"(\w+)"', src))):
    if mem not in m.GEOMETRY_ENTITY_ARITY[fam]: bad.append((fam, mem))
print("  能力: 特征参数 %d / 几何遍历 %d；属性 %d" % (
    sum(len(v) for v in m.FEATURE_DATA_ARITY.values()),
    sum(len(v) for v in m.GEOMETRY_ENTITY_ARITY.values()),
    sum(len(v) for v in m.FEATURE_DATA_PROPERTIES.values())))
print("  引用不一致 =", len(bad), bad)
# 事务族是否真的都有 AccessSelections / ReleaseSelectionAccess
for f in m.SELECTION_FAMILIES:
    t = m.FEATURE_DATA_ARITY[f]
    print("    %-28s AccessSelections=%s ReleaseSelectionAccess=%s" % (
        f, t.get("AccessSelections"), t.get("ReleaseSelectionAccess")))
