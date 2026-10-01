import re
import sys
sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\mcp-server")
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path

ROOT = Path(r"C:\swprojects\sw-skill-fork")
NAME_LITERAL = re.compile(r'name\s*=\s*"((?:solidworks|cadstudio)_[a-z0-9_]+)"')

#: ① server.py 里的
declared = NAME_LITERAL.findall((ROOT / "mcp-server" / "server.py").read_text(encoding="utf-8"))
#: ② batch 模块里的（从 specs 取，那是权威）
import register_capabilities as rc
batch_names = [s.name for s in rc.all_specs()]

print("  server.py 声明: %d（去重后 %d）" % (len(declared), len(set(declared))))
print("  batch 模块声明: %d（去重后 %d）" % (len(batch_names), len(set(batch_names))))
print()

#: ③ 两个来源之间的**交集** = 重名 ⇒ 谁赢？
overlap = sorted(set(declared) & set(batch_names))
print("  ★★ **两个注册路径都声明了的**（重名）: %d %s" % (len(overlap), overlap or ""))
print()

#: ④ 每个来源**内部**有没有重复
for label, names in (("server.py", declared), ("batch 模块", batch_names)):
    from collections import Counter
    dup = {k: v for k, v in Counter(names).items() if v > 1}
    print("  ★ %s **内部重复**: %d %s" % (label, len(dup), dup or ""))
