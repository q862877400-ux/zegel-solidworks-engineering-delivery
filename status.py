import sys, subprocess, re
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
R = Path(r"D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\redist")
S = Path(r"C:\swprojects\sw-skill-fork\scripts")
have = {p.stem[7:] for p in S.glob("sw_api_*.py")}
script = r'''
param([string]$Dll)
Add-Type -AssemblyName System.Reflection
try { $asm = [System.Reflection.Assembly]::LoadFrom($Dll) } catch { "ERR 0 0"; exit }
$i=0
foreach($t in $asm.GetTypes()){ if($t.IsInterface){$i++} }
"$i"
'''
Path(r"D:\AI\SW\_n.ps1").write_text(script, encoding="utf-8-sig")
tot_i = 0
for dll in sorted(R.glob("SolidWorks.Interop.*.dll")):
    a = dll.stem.replace("SolidWorks.Interop.","")
    r = subprocess.run(["pwsh","-NoProfile","-File",r"D:\AI\SW\_n.ps1","-Dll",str(dll)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    try: n = int((r.stdout or "0").strip().splitlines()[-1])
    except Exception: n = 0
    tot_i += n
    mark = "已收录" if a in have else ("仅枚举" if a == "swconst" else "** 未收录 **")
    print("  %-26s %4d 接口   %s" % (a, n, mark))
print("  ---- 全部程序集接口合计 %d" % tot_i)