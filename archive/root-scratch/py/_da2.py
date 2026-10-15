import sys, io, importlib.util, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
c = type(sys)("sw_connect"); c.get_com_member = lambda o,n,*a,**k: getattr(o,n,None)
sys.modules["sw_connect"] = c
spec = importlib.util.spec_from_file_location("da", r"C:\swprojects\sw-skill-fork\scripts\sw_drawing_annotations.py")
m = importlib.util.module_from_spec(spec); sys.modules["da"] = m
spec.loader.exec_module(m)
known = {n for v in m.ANNOTATION_ARITY.values() for n in v} | {n for v in m.ANNOTATION_PROPERTIES.values() for n in v}
src = open(r"C:\swprojects\sw-skill-fork\scripts\sw_drawing_annotations.py", encoding="utf-8").read()
print("  能力 %d / 属性 %d" % (sum(len(v) for v in m.ANNOTATION_ARITY.values()),
      sum(len(v) for v in m.ANNOTATION_PROPERTIES.values())))
bad = []
for fam, mem in sorted(set(re.findall(r'call_annotation\([^,]+,\s*"(\w+)",\s*"(\w+)"', src))):
    ok = mem in m.ANNOTATION_ARITY[fam]
    print("    %-20s %-22s %s" % (fam, mem, "OK" if ok else "❌ 不在表里"))
    if not ok: bad.append((fam, mem))
for mem in ("RowCount","ColumnCount","LeaderLineStyle","OwnerType","Color","Layer","Style"):
    print("    直读 %-18s %s" % (mem, "OK" if mem in known else "❌ 不在表里"))
    if mem not in known: bad.append(("-", mem))
print("  不一致 =", len(bad))
