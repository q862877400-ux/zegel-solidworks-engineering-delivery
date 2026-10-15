import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
s = Path(r"C:\swprojects\sw-skill-fork\mcp-server\server.py").read_text(encoding="utf-8")
vals = sorted(set(re.findall(r'def (\w*(?:must|required|_required)\w*)\(', s)))
print("  校验函数 %d 个:" % len(vals))
for v in vals: print("     %s" % v)
print()
print("  有没有「领域规则」类校验（草图/约束/特征合法性）:")
keys = ("sketch", "relation", "fully", "constraint", "underdefined", "geometry")
hit = [k for k in keys if re.search(k, s, re.I)]
print("     命中关键词: %s" % (hit or "无"))