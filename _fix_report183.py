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
out = subprocess.run([sys.executable, str(R / "scripts" / "check_report_freshness.py")],
                     cwd=str(R), capture_output=True, text=True, encoding="utf-8",
                     errors="replace").stdout
need = [l.strip() for l in out.splitlines() if "偏离上游：" in l]
if not need:
    print("  ⚠ 没拿到期望值"); sys.exit(1)
val = "> " + need[0].lstrip("> ").strip()
P.write_text(t[:m.start()] + val + t[m.end():], encoding="utf-8")
print("  改后: %s" % val)
