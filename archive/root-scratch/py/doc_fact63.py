"""按新 §六 的规矩加事实 63：**写进 `known-facts.md`**，AGENTS.md 只更新条数。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（纪律记录）
# 文件:   D:\\AI\\SW\\docs\\known-facts.md（事实 63 追加到这里）
#         D:\\AI\\SW\\AGENTS.md §六（只更新「共 N 条」的计数）
# 定位:   轮 47 发现 **AGENTS.md 超出 65536 字节指令预算被截断**，
#         而**截断保留前缀 ⇒ 被截掉的正是末尾最新的条目**（静默退化）。
#         ⇒ 把 62 条事实**原样**抽到独立文件，AGENTS.md 留 21 条速查 + 指针。
#         **本文件按**新规矩**演示：新事实只进 known-facts.md，AGENTS.md 只改计数。**
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 长内容走**短的单行字符串**（事实 48 定则）；跑完核对落盘。
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

F63 = (
    "| 63 | **AGENTS.md 有 65536 字节的**指令预算**；超了会被**截断，且截掉的是**末尾最新**的条目**"
    "（静默退化 —— 最新的事实反而看不见）** —— 2026-10-01（轮 47）实测：文件到 **66746 字节**时，"
    "系统提示 `truncated AGENTS.md from 66746 to 65244 bytes`。"
    "**⇒ 处理办法（零信息损失）：把「已知事实」表**原样**抽到本文件，"
    "AGENTS.md §六 只留**最常查的 21 条速查** + 指向本文件的指针**"
    "（抽完 AGENTS.md 从 66746 → **40475 字节**，余量 25 KB）。"
    "**⚠ 为什么用「抽取 + 指针」而不是「压缩」**：压缩会丢细节（那些是好幾轮挣来的）；"
    "抽取一条不丢。而且本仓库自己的规矩就是「知识文档进 `references/` / `docs/`」——"
    "**事实表本来就是**参考**，不是**指令****，放独立文件更符合它自己的分层。"
    "★ **新规矩（本文件生效）**：**新增事实直接追加到本文件**，"
    "AGENTS.md §六 只改「共 N 条」的计数，**除非**那条属于「最常查的」那一批。"
    "⚠ 同轮还踩到两个**呈现**坑（数据没丢）：① `splitlines()` 剥掉行尾换行 ⇒ "
    "`\"\".join(rows)` 会把 21 条挤成一行；② 旧 `## 六、` 标题行在新内容里重复出现。"
    "**⇒ 抽取类脚本必须**回读目标文件核对格式**（事实 48 定则②），不能只看「核对通过」。** | "
    "`D:\\AI\\SW\\docs\\known-facts.md`；轮 47 的 `split_known_facts.py`（含两处**覆盖前**的守卫）|"
)


def main() -> int:
    # ① 追加到 known-facts.md（**新规矩**）
    t = FACTS.read_text(encoding="utf-8")
    if "| 63 |" in t:
        print("  ⚠ 事实 63 已存在")
    else:
        FACTS.write_text(t.rstrip("\n") + "\n" + F63 + "\n", encoding="utf-8")
        print("  ✓ ① 事实 63 已追加到 known-facts.md")

    # ② AGENTS.md 只更新计数
    a = AGENTS.read_text(encoding="utf-8")
    nums = sorted(set(int(m.group(1)) for m in re.finditer(r"^\|\s*(\d+)\s*\|", FACTS.read_text(encoding="utf-8"), re.M)))
    total = max(nums)
    a2 = re.sub(r"\*\*共 \d+ 条\*\*", "**共 %d 条**" % total, a, count=1)
    if a2 == a:
        print("  ⚠ 计数没变（可能已是 %d）" % total)
    else:
        AGENTS.write_text(a2, encoding="utf-8")
        print("  ✓ ② AGENTS.md §六 计数更新为 %d 条" % total)

    # ③ 落盘核对
    f2 = FACTS.read_text(encoding="utf-8")
    a3 = AGENTS.read_text(encoding="utf-8")
    fn = sorted(set(int(m.group(1)) for m in re.finditer(r"^\|\s*(\d+)\s*\|", f2, re.M)))
    ab = len(a3.encode("utf-8"))
    print()
    print("  ── 落盘核对 ──")
    print("    known-facts.md: %d 条，1..%d 里缺 %r" % (len(fn), max(fn), [n for n in range(1, max(fn)+1) if n not in fn] or "无 ✓"))
    print("    AGENTS.md: %d 字节（预算 65536，余量 %d）%s" % (ab, 65536-ab, "✓" if ab < 65536 else "**⚠ 超**"))
    print("    AGENTS.md §六 计数行: %s" % [l for l in a3.splitlines() if l.startswith("**共 ")])
    print("    §六 标题数（应 1）: %d" % sum(1 for l in a3.splitlines() if l.startswith("## 六、")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
