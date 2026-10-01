import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
W = Path(r"D:\AI\SW")

#: ① 修 T-12602 的命令（精确替换；短串直接内联，无引号冲突）
P = W / "specs" / "126-view-selection-batch" / "tasks.md"
t = P.read_text(encoding="utf-8")
OLD = "-Pattern 'ActiveView|sw_view'`（**空**）"
NEW = ("-Pattern 'ActiveView|sw_view' | Where-Object { $_.Filename -ne 'tool_specs_batch14.py' }`"
       "（**空**；⚠ 必须排除本批产物，见 known-facts 147）")
assert OLD in t, "锚点不符"
P.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
print("  ok T-12602 已精确修好")
print("  核对（精确）:", "Where-Object { $_.Filename -ne 'tool_specs_batch14.py' }" in P.read_text(encoding="utf-8"))

#: ② converge 补说明（**从独立文件读**，事实 48 定则①）
C = W / "specs" / "126-view-selection-batch" / "converge.md"
c = C.read_text(encoding="utf-8")
add = (W / "_conv126_add.txt").read_text(encoding="utf-8")
if "判据曾被自己的产物污染" not in c:
    C.write_text(c.rstrip() + "\n" + add, encoding="utf-8")
    print("  ok converge 已补两条说明")
print("  核对（精确）:", "判据曾被自己的产物污染" in C.read_text(encoding="utf-8"))

#: ③ known-facts 147（从独立文件读）
K = W / "docs" / "known-facts.md"
tk = K.read_text(encoding="utf-8")
body = (W / "_fact147.txt").read_text(encoding="utf-8").strip().replace("\n", " ")
if "| 147 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + body + "\n", encoding="utf-8")
    print("  ok known-facts 已加 147")
print("  核对（精确）:", "| 147 |" in K.read_text(encoding="utf-8"))

#: ④ ROADMAP 游标（从独立文件读）
R = W / "docs" / "ROADMAP.md"
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None
before = "".join(lines)
blk = (W / "_cursor_696.txt").read_text(encoding="utf-8")
if re.search(r"^\s+696 ", before, re.M):
    print("  游标 696 已在")
else:
    new = "".join(lines[:i]) + blk + "".join(lines[i:])
    assert new.replace(blk, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
r2 = R.read_text(encoding="utf-8")
print("  核对（精确）: 696 =", re.search(r"^\s+696 ", r2, re.M) is not None,
      "· 700 =", re.search(r"^\s+700 ", r2, re.M) is not None)
