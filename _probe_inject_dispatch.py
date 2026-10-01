import sys
sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\mcp-server")
sys.stdout.reconfigure(encoding="utf-8")
from collections import Counter
import register_capabilities as rc
from tool_registry import effective_inject

specs = rc.all_specs()
used = Counter(effective_inject(s) for s in specs)
print("  ① 每条 spec 用到的注入名:")
for k, v in sorted(used.items()):
    print("      %-10s %d 条" % (k or "(空)", v))

print()
print("  ② `RESOLVERS` 里登记了、却**没有任何 spec 用**的:")
for name in rc.RESOLVERS:
    if name not in used:
        print("      ★ %s" % name)
if all(n in used for n in rc.RESOLVERS):
    print("      （无 —— 三个都被用到）")

print()
print("  ③ 用了、却**没有解析器**的（会在调用时炸）:")
bad = [k for k in used if k and k not in rc.RESOLVERS]
for k in bad:
    print("      ✗ %s（%d 条 spec）" % (k, used[k]))
if not bad:
    print("      （无）")

print()
print("  ④ 顺带：`server.py` 里 dispatch 表的大小 vs all_specs()")
import re
from pathlib import Path
src = Path(r"C:\swprojects\sw-skill-fork\mcp-server\server.py").read_text(encoding="utf-8")
m = re.search(r"(?m)^_TOOLS\s*[:=].*$|(?m)^_DISPATCH\s*[:=].*$", src)
print("      all_specs(): %d 条" % len(specs))
print("      server.py 里找到 dispatch 表: %s" % (m.group(0)[:80] if m else "（没找到，表可能是别的名字）"))
