import re
import subprocess
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")
P = R / "docs" / "harvest-report.md"
t = P.read_text(encoding="utf-8")
m = re.search(r"(?m)^> 偏离上游：.*$", t)
assert m
print("  改前: %s" % m.group(0))
#: ★ 数字每次都要**重取**（工作树一直在变）
out = subprocess.run(["python", str(R / "scripts" / "check_report_freshness.py")],
                     cwd=str(R), capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
need = None
for l in out.splitlines():
    if "偏离上游：" in l:
        need = l.strip().lstrip("> ").strip()
        if need.startswith("偏离上游："):
            need = "> " + need
        break
if need and need.startswith("> 偏离上游："):
    P.write_text(t[:m.start()] + need + t[m.end():], encoding="utf-8")
    print("  改后: %s" % need)
else:
    print("  ⚠ 没拿到期望值，看门禁输出：")
    print(out[-800:])
