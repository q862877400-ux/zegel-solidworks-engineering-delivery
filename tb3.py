import os, sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
BASE = Path(r"C:\ProgramData\SolidWorks\SOLIDWORKS 2026\design library")
# ① 现有库里各类零件的扩展名分布 —— 看出它是「参数化配置」还是「固定模型」
ext = {}
for d, dn, fn in os.walk(BASE):
    for f in fn:
        e = Path(f).suffix.lower()
        if e: ext[e] = ext.get(e, 0) + 1
print("=== design library 里的文件类型（按扩展名）===")
for e, n in sorted(ext.items(), key=lambda x: -x[1])[:12]:
    print("  %-12s %4d" % (e, n))
print()
# ② 有没有 .swbox（Toolbox 配置包）—— 有就说明装了 Toolbox
swbox = list(BASE.rglob("*.swbox"))
sldlfp = list(BASE.rglob("*.sldlfp"))
print("=== Toolbox 特征文件 ===")
print("  .swbox  (Toolbox 配置包)  :", len(swbox))
print("  .sldlfp (配置特征)        :", len(sldlfp))
print()
# ③ 装没装的另一个判据：注册表里的 Toolbox 相关项
import winreg
for hive, path in ((winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\SolidWorks"),
                   (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\SolidWorks")):
    try:
        k = winreg.OpenKey(hive, path)
        subs = []
        i = 0
        while True:
            try: subs.append(winreg.EnumKey(k, i)); i += 1
            except OSError: break
        print("  注册表 %s -> %d 个子键" % (path, len(subs)))
        hits = [s for s in subs if "Toolbox" in s or "Library" in s]
        if hits: print("     命中:", hits)
    except OSError as e:
        print("  注册表 %s 读不到: %s" % (path, str(e)[:40]))