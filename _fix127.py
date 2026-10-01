import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
W = Path(r"D:\AI\SW")

#: ① known-facts 148（**从独立文件搬运**，事实 48 定则①）
K = W / "docs" / "known-facts.md"
tk = K.read_text(encoding="utf-8")
body = (W / "_fact148.txt").read_text(encoding="utf-8").strip().replace("\n", " ")
if "| 148 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + body + "\n", encoding="utf-8")
    print("  ok known-facts 已加 148")
else:
    print("  148 已在")
print("  核对（精确）:", "| 148 |" in K.read_text(encoding="utf-8"))

#: ② ROADMAP 游标（**从独立文件搬运**）
R = W / "docs" / "ROADMAP.md"
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到锚点"
before = "".join(lines)
blk = (W / "_cursor_701.txt").read_text(encoding="utf-8")
if re.search(r"^\s+701 ", before, re.M):
    print("  游标 701 已在")
else:
    new = "".join(lines[:i]) + blk + "".join(lines[i:])
    assert new.replace(blk, "") == before, "除了插入块以外还有别的改动！"
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
r2 = R.read_text(encoding="utf-8")
print("  核对（精确）: 701 =", re.search(r"^\s+701 ", r2, re.M) is not None,
      "· 705 =", re.search(r"^\s+705 ", r2, re.M) is not None)
