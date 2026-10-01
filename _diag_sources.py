import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
d = json.load(open(r"C:\swprojects\sw-skill-fork\tools\union-sources.json", encoding="utf-8"))
print("  逐家：工具名清单 + 许可 + 自述验证环境")
tot = 0
for s in d:
    tools = s.get("tools") or []
    tot += len(tools)
    print("    %-36s %-11s %4d 个工具   declared=%r" %
          (s.get("repo"), s.get("license"), len(tools), s.get("declared_verified", "")))
    print("         note: %s" % str(s.get("note", ""))[:100])
print("  ── 四家工具名合计 %d（有重复名，并集 424）" % tot)
print()
print("  ⚠ 表里**只有名字**吗？看第一条的全部字段:")
print("    %s" % sorted(d[0].keys()))
