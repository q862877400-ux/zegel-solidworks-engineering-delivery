import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\docs\obsolete-member-candidates.md")
t = P.read_text(encoding="utf-8")
A = "## 四之三、⚠ 那 7 条真候选：查清后继形状后 —— **全部不换**（2026-10-01 轮 114）"
B = "## 四之二、**台账总账（全部处置完毕）**"
assert A in t and B in t, "锚点不符"
t = t.replace(A, "@@SEVEN@@", 1).replace(B, "@@TOTAL@@", 1)
t = t.replace("@@SEVEN@@", "## 四之二、⚠ 那 7 条真候选：查清后继形状后 —— **全部不换**（2026-10-01 轮 114）", 1)
t = t.replace("@@TOTAL@@", "## 四之三、**台账总账（全部处置完毕）**", 1)
P.write_text(t, encoding="utf-8")
print("  ok 已重编号")
for m in re.finditer(r"(?m)^## .*$", t):
    print("    %s" % m.group(0)[:70])
