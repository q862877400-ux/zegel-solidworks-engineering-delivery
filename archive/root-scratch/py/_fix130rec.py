import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
W = Path(r"D:\AI\SW")

K = W / "docs" / "known-facts.md"
tk = K.read_text(encoding="utf-8")
body = (W / "_fact151.txt").read_text(encoding="utf-8").strip().replace("\n", " ")
if "| 151 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + body + "\n", encoding="utf-8")
    print("  ok known-facts 已加 151")
else:
    print("  151 已在")
print("  核对（精确）:", "| 151 |" in K.read_text(encoding="utf-8"))

R = W / "docs" / "ROADMAP.md"
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None
before = "".join(lines)
blk = (W / "_cursor_716.txt").read_text(encoding="utf-8")
if re.search(r"^\s+716 ", before, re.M):
    print("  游标 716 已在")
else:
    new = "".join(lines[:i]) + blk + "".join(lines[i:])
    assert new.replace(blk, "") == before, "除插入块外还有别的改动"
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
r2 = R.read_text(encoding="utf-8")
print("  核对（精确）: 716 =", re.search(r"^\s+716 ", r2, re.M) is not None,
      "· 721 =", re.search(r"^\s+721 ", r2, re.M) is not None)
print("  specs/130 五件:",
      sorted(p.name for p in (W / "specs" / "130-angle-deg-boundary").glob("*.md")))
