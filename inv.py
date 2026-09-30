import sys, importlib, warnings
from pathlib import Path
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
warnings.filterwarnings("ignore")
mods = sorted(Path(r"C:\swprojects\sw-skill-fork\scripts").glob("sw_api_*.py"))
tot_f = tot_m = 0
print("%-28s %6s %8s" % ("程序集索引", "族", "成员"))
for p in mods:
    try:
        m = importlib.import_module(p.stem)
        f = len(getattr(m, "FAMILIES", {}))
        mem = sum(len(v) for v in getattr(m, "FAMILIES", {}).values()) if isinstance(getattr(m,"FAMILIES",{}), dict) else 0
        if mem == 0:
            mem = sum(len(v) for v in getattr(m, "ARITY", {}).values()) if hasattr(m,"ARITY") else 0
        tot_f += f; tot_m += mem
        print("%-28s %6d %8d" % (p.stem, f, mem))
    except Exception as e:
        print("%-28s 导入失败 %s" % (p.stem, str(e)[:30]))
print()
print("合计: %d 个程序集索引 · %d 族 · %d 成员" % (len(mods), tot_f, tot_m))