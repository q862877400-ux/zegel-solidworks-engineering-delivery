import subprocess, sys, os
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
BF = Path("D:\\Program Files\\SOLIDWORKS Corp\\JLCFA Parts Library Plugin "
          "Full Version v2.4.1-20260918-1\\ForFaceSelector\\BuildFile")
CM = os.path.expandvars(r"%USERPROFILE%\.cargo\bin\cadmpeg.exe")
for p in sorted(BF.iterdir()):
    if not p.is_file() or p.name.startswith("~$"):
        continue
    print("=== %s" % p.name[:70])
    for sub in (["inspect", str(p)], ["--help"]):
        if sub[0] == "--help":
            continue
        r = subprocess.run([CM] + sub, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=120)
        out = (r.stdout or r.stderr or "").strip()
        print(out[:1400] if out else "  (无输出, rc=%d)" % r.returncode)
        break
    print()