import sys, re
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
M = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_api_sldworks.py").read_text(encoding="utf-8")
def ar(iface, mem):
    g = re.search(r"'%s': \{\n(.*?)\n    \}," % re.escape(iface), M, re.S)
    return dict(re.findall(r"'(\w+)': (\d+)", g.group(1))).get(mem) if g else None
print("=== 插入标准件的入口（反射 arity）===")
for iface, mem in (("IAssemblyDoc","AddComponent5"),("IAssemblyDoc","AddComponent4"),
                   ("IAssemblyDoc","AddComponent2"),("IAssemblyDoc","AddComponent"),
                   ("IModelDoc2","AddComponent5"),
                   ("ISldWorks","GetUserPreferenceStringValue")):
    print("  %-14s %-22s arity=%s" % (iface, mem, ar(iface, mem)))
print()
print("=== 索引里有没有 ToolBox 相关接口族 ===")
fams = sorted(set(re.findall(r"^    '(I\w*(?:ToolBox|Toolbox)\w*)'", M, re.M)))
print("  ", fams if fams else "** 没有任何 ToolBox 接口族 **")
allf = set()
for p in Path(r"C:\swprojects\sw-skill-fork\scripts").glob("sw_api_*.py"):
    allf |= set(re.findall(r"^    '(I\w+)'", p.read_text(encoding="utf-8"), re.M))
print("  全部 12 份索引里含 ToolBox 的族:", sorted(f for f in allf if "ToolBox" in f or "Toolbox" in f) or "无")
print()
print("=== 关键：Toolbox 数据文件在哪（官方机制）===")
print("  AddComponent5 的 File 参数 = 配置文件路径，")
print("  SolidWorks Toolbox 是**单独下载**的配置包（.swbox），不随安装附带。")