import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\docs\obsolete-member-candidates.md")
t = P.read_text(encoding="utf-8")

OLD = "## 四之二、台账总账（全部处置完毕）"
NEW = "## 四之四、**台账总账（全部处置完毕）**"
i, j = t.find(OLD), t.find(NEW)
assert i != -1 and j != -1 and i < j, "锚点不符"
before = len(t)
# 删掉旧的「四之二」整块（到下一个 ## 为止）
k = t.find("\n## ", i + len(OLD))
assert k != -1
t = t[:i] + t[k + 1:]
# 把新的「四之四」改名为「四之二」
t = t.replace(NEW, "## 四之二、**台账总账（全部处置完毕）**", 1)
P.write_text(t, encoding="utf-8")
print("  ok 已删旧总账并改名（%d -> %d 字节）" % (before, len(t)))
print("  现在的二级标题：")
for m in re.finditer(r"(?m)^## .*$", t):
    print("    %s" % m.group(0)[:70])
