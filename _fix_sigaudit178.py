import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\docs\signature-audit.md")
lines = P.read_text(encoding="utf-8").splitlines(keepends=True)
hit = 0
for k, l in enumerate(lines):
    if l.startswith("| `sw_mold.py`"):
        print("  改前: %s" % l.strip())
        lines[k] = "| `sw_mold.py` | 16 | **16** | 0 | 0 |\n"
        hit += 1
        print("  改后: %s" % lines[k].strip())
assert hit == 1, "命中 %d" % hit
P.write_text("".join(lines), encoding="utf-8")
