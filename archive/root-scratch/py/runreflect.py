import subprocess, sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
# ⚑ 用 -Command 而不是 -File：-File 模式对 [string[]] 数组参数支持有限，
#   实测只反射了第一个程序集，$Out 还被覆写成 "swpublished"。
T = ["swdimxpert","swpublished","gtswutilities","dsgnchk",
     "sldtoolboxconfigureaddin","sustainability"]
arr = ",".join("'%s'" % t for t in T)
cmd = "& 'D:\\AI\\SW\\tools\\reflect-interop.ps1' -Targets @(%s)" % arr
r = subprocess.run(["pwsh","-NoProfile","-Command",cmd],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
print(r.stdout)
if r.stderr.strip():
    print("--- stderr ---")
    for l in r.stderr.splitlines()[:10]: print("  " + l)