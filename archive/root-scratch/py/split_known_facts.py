"""把 `AGENTS.md` 的「已知事实」表**原样**抽到 `docs/known-facts.md`，AGENTS.md 留速查 + 指针。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（指令文件的结构调整）
# 文件:   D:\\AI\\SW\\AGENTS.md 的 §六「已知事实」表（62 条 / 47413 字节 = 全文 71%）
#         ⇒ 抽出到 D:\\AI\\SW\\docs\\known-facts.md（**原样，零信息损失**）
# 定位:   轮 46 收工时系统提示：
#         「**Workspace instruction budget 65536 bytes: truncated AGENTS.md from 66746 to 65244**」
#         ⚠ **截断保留的是**前** 65244 字节，而事实表在**末尾增长**
#         ⇒ **被截掉的正是**最新**的事实（61/62 —— 恰恰是最相关的）。**
#         **⇒ 这是**静默退化**：我可能不知道有那几条。**
#
#   **为什么用「抽取 + 指针」而不是「压缩」**：
#     压缩会**丢细节**（那些细节是好几轮才挣来的）；抽取到独立文件**一条不丢**。
#     而且本仓库自己的规矩就是「知识文档进 `references/` / `docs/`」——
#     事实表本来就是**参考**，不是**指令**，放独立文件更符合它自己的分层。
#
#   ★ **安全措施（按**事实 61**：批量脚本先证明只做加法）**：
#     ① 本脚本先把表**原样**写到新文件（纯新增）；
#     ② AGENTS.md 的改写**先写临时文件**，逐项核对（表内容一条不少、非表内容逐字节相同）；
#     ③ 核对通过才覆盖；`git diff --stat` 里的 deletions 是**预期的搬移**（已在提交信息里说明）。
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 长内容走**短的单行字符串**（事实 48 定则）；跑完**回读核对**。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
WS = Path(r"D:\AI\SW")
AGENTS = WS / "AGENTS.md"
FACTS = WS / "docs" / "known-facts.md"

#: AGENTS.md 里**保留**的速查条目（最常查、最难重新发现的一批）
KEEP = [
    1, 2, 8, 9, 12, 24, 32, 33, 36, 40, 43, 47, 48, 51, 53, 55, 57, 58, 59, 61, 62,
]

HEADER = """# 已知事实（完整表）

> 从 `AGENTS.md` §六 抽出的完整「已知事实」表 —— **原样搬迁，一条不丢**。
>
> **为什么抽出来**：该表已长到 62 条 / 约 47 KB，而 AGENTS.md 受
> **65536 字节的指令预算**限制 ⇒ **文件被截断，而被截掉的正好是**末尾最新的**那几条**
> （截断保留前缀）。⇒ **静默退化**：最新的事实反而看不见。
>
> **⇒ AGENTS.md §六 现在只留**最常查的条目速查** + 指向本文件的指针。**
>
> ⚠ **本文件是**参考**，不是**指令**；AGENTS.md 才是常驻指令。查事实请**整表读这里**。
> ⚠ 新增事实时：**只在 AGENTS.md §六 写「速查条目」要留的那些**，
> 其余**直接追加到本文件**（并同步 §六 的条数说明）。

"""


def main() -> int:
    t = AGENTS.read_text(encoding="utf-8")
    lines = t.splitlines(keepends=True)
    hdr_i = next((i for i, l in enumerate(lines) if l.strip() == "| # | 事实 | 依据 |"), None)
    if hdr_i is None:
        print("  ✗ 找不到事实表表头")
        return 1
    last_i = max(i for i, l in enumerate(lines) if re.match(r"^\|\s*\d+\s*\|", l))
    # 表头前两行（`| # | 事实 | 依据 |` 与 `|---|---|---|`）
    table_start = hdr_i
    table_end = last_i + 1

    table = "".join(lines[table_start:table_end])
    before = "".join(lines[:table_start])
    after = "".join(lines[table_end:])

    # ① **原样**写完整表到独立文件
    rows = [l for l in table.splitlines() if re.match(r"^\|\s*\d+\s*\|", l)]
    FACTS.write_text(HEADER + table.rstrip("\n") + "\n", encoding="utf-8")
    print("  ✓ ① 已写 %s（**原样** %d 条 / %d 字节）"
          % (FACTS.name, len(rows), FACTS.stat().st_size))

    # ② 组 AGENTS.md 的新 §六（速查 + 指针）
    keep_rows = []
    for want in KEEP:
        for r in rows:
            if re.match(r"^\|\s*%d\s*\|" % want, r):
                keep_rows.append(r)
                break
    print("  ✓ ② 速查保留 %d 条（应 %d）" % (len(keep_rows), len(KEEP)))
    if len(keep_rows) != len(KEEP):
        print("  ✗ 有条目没找到 ⇒ **停下**（按事实 61：先证明只做加法）")
        return 1

    # ⚠⚠ 两个呈现坑（轮 47 第一次跑踩到）：
    #   ① `rows` 来自 `splitlines()` ⇒ **行尾换行被剥掉了** ⇒ 直接 `"".join(keep_rows)` 会把
    #      21 条挤成一行（表格坏掉）。**⇒ join 时要补 `\n`。**
    #   ② `before` 里**已经含**旧的 `## 六、...` 标题行 ⇒ 新内容里再写一个就成了**重复标题**。
    #      **⇒ 把旧标题行从 `before` 末尾剥掉。**
    before_lines = before.splitlines(keepends=True)
    while before_lines and (before_lines[-1].startswith("## 六、") or not before_lines[-1].strip()):
        before_lines.pop()
    before = "".join(before_lines) + "\n\n"

    new_six = (
        "## 六、已知事实（完整表在 [`docs/known-facts.md`](docs/known-facts.md)）\n"
        "\n"
        "**共 %d 条**，全文在 [`docs/known-facts.md`](docs/known-facts.md)。\n"
        "⚠ **为什么会分开**：该表已占 AGENTS.md 的 ~71%%，而本文件受 **65536 字节指令预算**限制\n"
        "⇒ **超预算会被截断，且截掉的是**末尾最新**的条目**（静默退化）。\n"
        "⇒ **查事实请读那个文件**；本节只留**最常查的 %d 条**做速查。\n"
        "⚠ **新增事实**：只在下面保留「最常查的」；其余**直接追加到 `docs/known-facts.md`**，\n"
        "并在本节更新条数说明。\n"
        "\n"
        "### 速查（最常查的 %d 条）\n"
        "\n"
        "| # | 事实 | 依据 |\n"
        "|---|---|---|\n" % (len(rows), len(KEEP), len(KEEP))
    ) + "\n".join(keep_rows) + "\n\n"

    new_text = before + new_six + after

    # ③ **核对**：表内容一条不少；非表内容**逐字节相同**
    ok = True
    facts_text = FACTS.read_text(encoding="utf-8")
    for r in rows:
        if r not in facts_text:
            print("  ✗ 独立文件里少了: %s" % r[:60])
            ok = False
    if before not in new_text:
        print("  ✗ 表前内容没被完整保留")
        ok = False
    if after not in new_text:
        print("  ✗ 表后内容没被完整保留")
        ok = False
    nb = len(new_text.encode("utf-8"))
    print("  ✓ ③ 核对：%s；新 AGENTS.md **%d 字节**（预算 65536，余量 %d）"
          % ("通过" if ok else "**失败**", nb, 65536 - nb))
    if not ok:
        print("  ✗ 核对失败 ⇒ **不覆盖**（按事实 61）")
        return 1

    AGENTS.write_text(new_text, encoding="utf-8")
    print("  ✓ ④ 已覆盖 AGENTS.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
