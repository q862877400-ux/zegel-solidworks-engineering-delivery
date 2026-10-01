"""修 **我自己引入的表格格式缺陷**：把「事实 41 的更正」并回同一行。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（文档格式修复）
# 文件:   D:\\AI\\SW\\AGENTS.md 的「已知事实」表
# 定位:   ⚠ 上一补丁把一段更正**插成了独立的一行**，而那行**没有前导 `|`**
#         ⇒ **它把 markdown 表格截断了**（第 41 行与第 42 行之间多了一行非表格文本）。
#         **⇒ 本补丁把它并回第 41 行的**同一物理行**，恢复表格合法。**
#         ⚠ 教训：往**表格**里加内容，必须加在 `|` 行内；跨行就是**破表**。
#         **⇒ 这与事实 48（长内容不内联）是同一族问题：**形式必须随之匹配**。**
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 跑完核对落盘（事实 48 第 ② 条）。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
AGENTS = Path(r"D:\AI\SW\AGENTS.md")

MARK = "**⚠ 2026-10-01 更正（查了门禁之后）**"


def main() -> int:
    lines = AGENTS.read_text(encoding="utf-8").splitlines(keepends=True)
    # 找那行独立更正 + 它前面的 | 41 | 行
    idx_fix = None
    for i, l in enumerate(lines):
        if l.startswith(MARK):
            idx_fix = i
            break
    if idx_fix is None:
        print("  ⚠ 找不到独立更正行（可能已修）")
        return 0
    # 往前找最近的表格行
    idx_row = None
    for j in range(idx_fix - 1, -1, -1):
        if lines[j].lstrip().startswith("|"):
            idx_row = j
            break
    if idx_row is None:
        print("  ✗ 找不到上一行表格行")
        return 1
    row = lines[idx_row].rstrip("\n")
    fix = lines[idx_fix].strip()
    # 并回同一行（去掉更正行）
    merged = row + fix + "\n"
    print("  · 表格行: %s…" % row[:60])
    print("  · 更正行: %s…" % fix[:60])
    new_lines = lines[:idx_row] + [merged] + lines[idx_row + 1:idx_fix] + lines[idx_fix + 1:]
    AGENTS.write_text("".join(new_lines), encoding="utf-8")
    print("  ✓ 已并回同一物理行（表格恢复合法）")

    # 落盘核对
    t = AGENTS.read_text(encoding="utf-8")
    print()
    print("  ── 落盘核对 ──")
    print("    含独立更正行（应**否**）: %s"
          % ("**是（仍有问题）**" if any(l.startswith(MARK) for l in t.splitlines()) else "否 ✓"))
    print("    第 41 行含更正（应**是**）: %s"
          % ("是 ✓" if any(l.lstrip().startswith("| 41 |") and MARK in l for l in t.splitlines())
             else "**否**"))
    # 表格连续性：事实 41..49 的行是否都是 | 开头
    ks = [i for i, l in enumerate(t.splitlines()) if l.lstrip().startswith("| 41 |")]
    if ks:
        seg = t.splitlines()[ks[0]:ks[0] + 9]
        bad = [l[:40] for l in seg if l.strip() and not l.lstrip().startswith("|")]
        print("    事实 41 起 9 行里的非表格行: %s"
              % ("无 ✓" if not bad else "**有 %r**" % bad))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
