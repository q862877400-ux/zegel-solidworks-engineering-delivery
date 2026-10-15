import sys, subprocess, os
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
BF = Path("D:\\Program Files\\SOLIDWORKS Corp\\JLCFA Parts Library Plugin "
          "Full Version v2.4.1-20260918-1\\ForFaceSelector\\BuildFile")
CM = os.path.expandvars(r"%USERPROFILE%\.cargo\bin\cadmpeg.exe")
files = sorted([p for p in BF.iterdir() if p.is_file() and not p.name.startswith("~$")],
               key=lambda p: p.stat().st_mtime, reverse=True)
print("  BuildFile 共 %d 个，最新 3 个:" % len(files))
for p in files[:3]:
    print("    %s  %.1f KB" % (p.name[:66], p.stat().st_size/1024))
newest = files[0]
print()
print("  ★ 用 cadmpeg 读刚生成的这个（不启动 SolidWorks）:")
r = subprocess.run([CM, "inspect", str(newest)], capture_output=True, text=True,
                   encoding="utf-8", errors="replace", timeout=90)
print("\n".join((r.stdout or r.stderr or "").splitlines()[:10]))