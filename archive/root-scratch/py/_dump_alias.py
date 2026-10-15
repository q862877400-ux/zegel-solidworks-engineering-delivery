import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\docs\union-gap-triage.md")
lines = P.read_text(encoding="utf-8").splitlines()
for tag in ("别名（强）", "别名（弱）"):
    i = next((k for k, l in enumerate(lines) if tag in l and l.startswith("#")), None)
    if i is None:
        print("  **找不到 %s 节**" % tag)
        continue
    j = next((k for k in range(i + 1, len(lines)) if lines[k].startswith("#")), len(lines))
    rows = []
    for l in lines[i:j]:
        m = re.match(r"^\|\s*`([^`]+)`\s*\|\s*(.+?)\s*\|\s*$", l)
        if m:
            rows.append((m.group(1), m.group(2)))
    print("=== %s：%d 条 ===" % (tag, len(rows)))
    for n, (gap, ours) in enumerate(rows, 1):
        print("%2d. %-34s -> %s" % (n, gap, ours))
    print()
