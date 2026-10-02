"""★ 消除 plan-next.md 里「批 A1」与验收判据「A1」的同名歧义。"""

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"D:\AI\SW\docs\plan-next.md")
src = p.read_text(encoding="utf-8")
out = []
n_head = n_row = 0
for line in src.splitlines():
    #: ★ 表头首列 `| 批 |` ⇒ `| 批次 |`
    if re.match(r"^\|\s*批\s*\|", line):
        line = re.sub(r"^\|\s*批\s*\|", "| 批次 |", line)
        n_head += 1
    #: ★ 表行首列 `| **A1** |` ⇒ `| **第 1 批** |`（★ 只在**表格行**里、且**首列**）
    m = re.match(r"^\|\s*\*\*A(\d+)\*\*\s*\|", line)
    if m:
        line = re.sub(r"^\|\s*\*\*A(\d+)\*\*\s*\|", "| **第 %s 批** |" % m.group(1), line)
        n_row += 1
    out.append(line)
new = "\n".join(out) + ("\n" if src.endswith("\n") else "")
p.write_text(new, encoding="utf-8")
print("  表头改写 %d 处 · 表行改写 %d 处" % (n_head, n_row))
for i, l in enumerate(new.splitlines()):
    if "批次" in l and l.startswith("|"):
        print("    L%-4d %s" % (i + 1, l[:100]))
