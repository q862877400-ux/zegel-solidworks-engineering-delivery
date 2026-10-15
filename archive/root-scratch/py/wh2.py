import sys, subprocess
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
R = Path(r"D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\redist")
for a in ("swpublished","gtswutilities","swbrowser","dsgnchk",
          "sldtoolboxconfigureaddin","sw3dprinter"):
    r = subprocess.run(["pwsh","-NoProfile","-File",r"D:\AI\SW\_t3.ps1","-Dll",
                        str(R/f"SolidWorks.Interop.{a}.dll")],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    names = [l[3:].strip() for l in (r.stdout or "").splitlines() if l.strip()]
    iface = [n for n in names if n.startswith("I")]
    enums = [n for n in names if n.startswith("sw")]
    print("=== %s  (%d 接口 / %d 枚举)" % (a, len(iface), len(enums)))
    for n in iface[:9]: print("   I  " + n)
    for n in enums[:4]: print("   E  " + n)
    print()