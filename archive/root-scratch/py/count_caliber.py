import json, sys
sys.stdout.reconfigure(encoding="utf-8")
R = r"C:\swprojects\sw-skill-fork"
src = json.load(open(R + r"\tools\union-sources.json", encoding="utf-8"))

four = set()
for s in src["sources"]:
    four |= set(s["operations"])
print("  349?  四家并集（不含本仓库）      = %d" % len(four))

import re, subprocess
srv = open(R + r"\mcp-server\server.py", encoding="utf-8").read()
ours_raw = sorted(set(re.findall(r'@mcp\.tool\(\s*\n?\s*name\s*=\s*"([^"]+)"', srv)))
sys.path.insert(0, R + r"\tools")
from build_union_sources import _normalize
ours = {_normalize(t) for t in ours_raw}
print("  384?  四家 ∪ 本仓库              = %d" % len(four | ours))
print("  339?  并集里本仓库缺的            = %d" % len((four | ours) - ours))
print()
print("  ⇒ 三个数各是各的量，不是『漂』；但我确实没写清口径 —— 这条我认")