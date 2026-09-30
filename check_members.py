import ast, re, sys
sys.stdout.reconfigure(encoding="utf-8")
src = open(r"C:\swprojects\sw-skill-fork\scripts\sw_topology.py", encoding="utf-8").read()
tree = ast.parse(src)
names = []
for n in ast.walk(tree):
    if isinstance(n, ast.Call):
        f = n.func
        nm = getattr(f, "id", None) or getattr(f, "attr", None)
        if nm == "get_com_member" and len(n.args) >= 2:
            a = n.args[1]
            if isinstance(a, ast.Constant) and isinstance(a.value, str):
                names.append(a.value)
names = sorted(set(names))
refl = open(r"D:\AI\SW\_raw\topo-reflect\iface_cosworks.txt", encoding="utf-8").read()
sld  = open(r"D:\AI\SW\_raw\topo-sldworks\iface_sldworks.txt", encoding="utf-8").read()
both = refl + "\n" + sld
print("模块调用的成员 %d 个：" % len(names))
missing = []
for nm in names:
    ok = re.search(r"\b%s\s*\(" % re.escape(nm), both) is not None
    print("   %s %s" % ("✓" if ok else "✗", nm))
    if not ok: missing.append(nm)
print()
print("反射里查不到的: %s" % (missing or "无 ✓"))