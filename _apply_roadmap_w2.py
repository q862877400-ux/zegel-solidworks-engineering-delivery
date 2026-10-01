import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"D:\AI\SW\docs\ROADMAP.md")
lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
ADD = Path(r"D:\AI\SW\_roadmap_w2.txt").read_text(encoding="utf-8")
if "十小时计划的第二批" in "".join(lines):
    print("  已在，跳过")
else:
    i = next(k for k, l in enumerate(lines) if l.strip().startswith("阻塞:"))
    lines.insert(i, ADD)
    p.write_text("".join(lines), encoding="utf-8")
    print("  ✓ 已插入 %d 行（在 L%d 之前）" % (ADD.count("\n"), i + 1))
t = p.read_text(encoding="utf-8")
print("  核对: 含 W2 段 =", "十小时计划的第二批" in t)
print("  核对: 阻塞行仍在 =", "阻塞:" in t)
print("  核对: 含 W1 段 =", "十小时计划的第一批" in t)
