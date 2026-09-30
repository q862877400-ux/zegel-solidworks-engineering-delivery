import sys, subprocess, re
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
R = Path(r"D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\redist")
r = subprocess.run(["pwsh","-NoProfile","-File",r"D:\AI\SW\_t3.ps1","-Dll",
                    str(R/"SolidWorks.Interop.swdimxpert.dll")],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
names = [l[3:].strip() for l in (r.stdout or "").splitlines() if l.strip()]
tol = [n for n in names if n.endswith("Tolerance") or n.endswith("DimTol") or "Gtol" in n]
feat = [n for n in names if n.endswith("Feature")]
rest = [n for n in names if n not in tol and n not in feat and not n.startswith("sw")]
print("公差类 %d 个 / 特征类 %d 个 / 其它 %d 个" % (len(tol), len(feat), len(rest)))
print()
print("公差类（自动标注要生成的符号）:")
for n in tol[:10]: print("   " + n)
print("特征类（要被标注的零件要素）:")
for n in feat[:10]: print("   " + n)
print("其它:")
for n in rest[:12]: print("   " + n)