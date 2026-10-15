import sys, io, importlib.util, re
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
spec = importlib.util.spec_from_file_location("tbi", r"C:\swprojects\sw-skill-fork\scripts\sw_toolbox_index.py")
m = importlib.util.module_from_spec(spec); sys.modules["tbi"]=m; spec.loader.exec_module(m)
idx = m.load_index()
# 找一个结构简单、路径干净的零件做端到端
cands = [i for i in idx["parts"] if i["standard"]=="GB" and "washer" in i["part"].lower()][:5]
for c in cands:
    print("  %-46s %s" % (c["part"], c["path"]))
print()
# AddComponent5 的 arity（我索引里的）
spec2 = importlib.util.spec_from_file_location("swapi", r"C:\swprojects\sw-skill-fork\scripts\sw_api_sldworks.py")
sw = importlib.util.module_from_spec(spec2); sys.modules["swapi"]=sw; spec2.loader.exec_module(sw)
print("  IAssemblyDoc 登记成员数:", len(sw.ARITY.get("IAssemblyDoc", {})))
for k in ("AddComponent5","AddComponent4","AddComponent2"):
    print("    %-14s arity=%s" % (k, sw.ARITY.get("IAssemblyDoc",{}).get(k)))
print()
# 反射里 AddComponent5 的真实参数类型
txt = Path(r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt").read_text(encoding="utf-8", errors="replace")
mm = re.search(r"(?ms)^## IAssemblyDoc\s*\r?\n(.*?)(?=\r?\n## |\Z)", txt)
for l in mm.group(1).splitlines():
    if re.search(r"\bAddComponent5?\b", l) and "(" in l:
        print("  反射:", l.strip()[:150])