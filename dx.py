import sys, subprocess
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
R = Path(r"D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\redist")
script = r'''
param([string]$Dll)
Add-Type -AssemblyName System.Reflection
$asm = [System.Reflection.Assembly]::LoadFrom($Dll)
foreach($t in ($asm.GetTypes() | Sort-Object Name)){
  if($t.IsInterface){ "I  " + $t.Name }
  elseif($t.IsEnum){ "E  " + $t.Name }
}
'''
Path(r"D:\AI\SW\_t3.ps1").write_text(script, encoding="utf-8-sig")
r = subprocess.run(["pwsh","-NoProfile","-File",r"D:\AI\SW\_t3.ps1","-Dll",
                    str(R/"SolidWorks.Interop.swdimxpert.dll")],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
lines = [l for l in (r.stdout or "").splitlines() if l.strip()]
for l in lines[:34]: print("  " + l)
print("  ... 共 %d 项" % len(lines))