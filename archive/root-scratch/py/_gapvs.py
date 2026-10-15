import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
t = Path(r"C:\swprojects\sw-skill-fork\docs\union-coverage-matrix.md").read_text(encoding="utf-8")

print("  17 个域：缺口 vs 我们已有的函数（判断「缺」是真缺，还是只是没挂）")
print("  %-30s %10s %10s   %s" % ("域", "缺口(MCP)", "能力面", "判断"))
tot_gap = tot_have = 0
rows = []
for l in t.splitlines():
    cells = [c.strip() for c in l.strip().strip("|").split("|")] if l.startswith("|") else []
    if len(cells) >= 9 and re.match(r"^[①-⑰]", cells[0]):
        dom = cells[0]
        try:
            gap = int(cells[8].replace("*", "").replace("✓", "").strip() or 0)
        except ValueError:
            gap = 0
        capr = cells[6]
        marked = "⚠" in capr
        try:
            cap = int(capr.replace("⚠", "").replace("*", "").strip())
        except ValueError:
            cap = 0
        tot_gap += gap
        tot_have += cap
        verdict = ("我们有实现，只是没挂" if marked else ("真缺" if gap else "已齐"))
        rows.append((dom, gap, cap, verdict))
for dom, gap, cap, v in rows:
    print("  %-30s %10d %10d   %s" % (dom[:28], gap, cap, v))
print("  %-30s %10d %10d" % ("合计", tot_gap, tot_have))

n_marked = sum(1 for _d, _g, _c, v in rows if v == "我们有实现，只是没挂")
gap_marked = sum(g for _d, g, _c, v in rows if v == "我们有实现，只是没挂")
print("")
print("  ★ 17 个域里，**标了「有实现只是没挂」的: %d 个域**，涉及缺口 **%d 个名字**" % (n_marked, gap_marked))
print("  ★ 其余域的缺口合计: %d 个名字" % (tot_gap - gap_marked))
