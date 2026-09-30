import re, subprocess, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
d = subprocess.run(["git","diff","HEAD"], capture_output=True, text=True,
                   encoding="utf-8").stdout
gone = {g for g in re.findall(r"^-\s*def (\w+)\s*\(", d, re.M) if not g.startswith("_")}
print("从 git diff HEAD 取到已删短名 %d 个" % len(gone))
print("样例:", ", ".join(sorted(gone)[:12]))
Path(r"D:\AI\SW\_gone.txt").write_text("\n".join(sorted(gone)), encoding="utf-8")
