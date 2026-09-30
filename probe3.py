import sys, re
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
# 用另一条路核实：这些 DLL 到底有没有接口？（枚举 vs 接口）
import subprocess
R = Path(r"D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\redist")
probe = ["dsgnchk","gtswutilities","sldtoolboxconfigureaddin","sw3dprinter",
         "swbrowser","swcommands","swdimxpert","swpublished"]
script = r'''
param([string]$Dll)
Add-Type -AssemblyName System.Reflection
$asm = [System.Reflection.Assembly]::LoadFrom($Dll)
$i=0; $e=0; $c=0
foreach($t in $asm.GetTypes()){
  if($t.IsInterface){$i++} elseif($t.IsEnum){$e++} else {$c++}
}
"$i interfaces, $e enums, $c classes"
'''
Path(r"D:\AI\SW\_t.ps1").write_text(script, encoding="utf-8-sig")
for a in probe:
    dll = R / f"SolidWorks.Interop.{a}.dll"
    if not dll.is_file(): continue
    r = subprocess.run(["pwsh","-NoProfile","-File",r"D:\AI\SW\_t.ps1","-Dll",str(dll)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    print("  %-28s %s" % (a, (r.stdout or "").strip().splitlines()[-1] if r.stdout else "FAILED"))