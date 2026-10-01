import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ── ① 签名审计表：sw_connect.py 21 → 23（门禁指定的数字）──────────────
P = Path(r"C:\swprojects\sw-skill-fork\docs\signature-audit.md")
t = P.read_text(encoding="utf-8")
lines = t.splitlines(keepends=True)
hit = 0
for k, l in enumerate(lines):
    if l.startswith("| `sw_connect.py`"):
        print("  改前: %s" % l.strip())
        lines[k] = "| `sw_connect.py` | 23 | **23** | 0 | 0 |\n"
        hit += 1
        print("  改后: %s" % lines[k].strip())
assert hit == 1, "命中 %d 行（应为 1）" % hit
P.write_text("".join(lines), encoding="utf-8")

# ── ② 报告数字：偏离上游那行（**每个数字都改了**，不是只改一个）───────
P2 = Path(r"C:\swprojects\sw-skill-fork\docs\harvest-report.md")
t2 = P2.read_text(encoding="utf-8")
NEW = "> 偏离上游：323 个文件 / +151,594 行 / -332 行 · 284 个 commit · 工作区 clean"
m = re.search(r"(?m)^> 偏离上游：.*$", t2)
assert m, "报告里没找到『偏离上游』行"
print("  报告改前: %s" % m.group(0))
t2 = t2[:m.start()] + NEW + t2[m.end():]
P2.write_text(t2, encoding="utf-8")
print("  报告改后: %s" % NEW)
