import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\docs\union-gap-triage.md")
lines = P.read_text(encoding="utf-8").splitlines()
i = next((k for k, l in enumerate(lines) if "真缺" in l and l.startswith("#")), None)
print("真缺节起始行: %s" % i)
j = next((k for k in range(i + 1, len(lines)) if lines[k].startswith("#")), len(lines))
ops = []
for l in lines[i:j]:
    m = re.match(r"^\|\s*`?([^`|]+?)`?\s*\|", l)
    if m and not set(m.group(1).strip()) <= set("-: "):
        v = m.group(1).strip()
        if v and v not in ("缺口操作",):
            ops.append(v)
print("真缺条数: %d" % len(ops))
print()
# 每 6 取 1 抽样 22 条
s = ops[::6][:22]
for n, o in enumerate(s, 1):
    print("%2d. %s" % (n, o))
