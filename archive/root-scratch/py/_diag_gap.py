import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"C:\swprojects\sw-skill-fork\docs\union-gap-triage.md")
t = p.read_text(encoding="utf-8")
m = re.search(r"## 真缺（(\d+)）", t)
print("  真缺档: %s 条" % (m.group(1) if m else "?"))
seg = t[t.index("## 真缺"):]
rows = re.findall(r"(?m)^\|\s*`([^`]+)`\s*\|(.*?)\|", seg)
print("  表内行数: %d" % len(rows))
filled = [(n, c.strip()) for n, c in rows if c.strip() not in ("—", "", "-")]
print("  标了「我们的候选」的: %d 条" % len(filled))
for n, c in filled[:14]:
    print("     %-32s %s" % (n, c[:54]))
print("  ==> 132 条里已补 %d 条；剩 %d 条仍标空缺" % (len(filled), len(rows) - len(filled)))
print()
#: 那个「后缀候选 144」呢
m2 = re.search(r"## 后缀候选（需人工核）（(\d+)）", t)
print("  后缀候选档: %s 条（144 = 需人工核）" % (m2.group(1) if m2 else "?"))
for m3 in re.finditer(r"(?m)^\|.*(已核|已看|核完|未核).*$", t):
    pass
