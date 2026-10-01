import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\docs\union-gap-triage.md")
t = P.read_text(encoding="utf-8")
lines = t.splitlines()
# 找「后缀候选」那节的表
i = next(k for k, l in enumerate(lines) if "后缀候选" in l and l.startswith("#"))
j = next((k for k in range(i + 1, len(lines)) if lines[k].startswith("#")), len(lines))
rows = []
for l in lines[i:j]:
    m = re.match(r"^\|\s*`([^`]+)`\s*\|\s*(.+?)\s*\|\s*$", l)
    if m:
        rows.append((m.group(1), m.group(2)))
print("后缀候选总数: %d" % len(rows))
print()
# 系统性抽样：每 6 条取 1，得 24 条
sample = rows[::6][:24]
print("抽样 %d 条（每 6 取 1）：" % len(sample))
for n, (gap, ours) in enumerate(sample, 1):
    print("%2d. %-34s -> %s" % (n, gap, ours))
