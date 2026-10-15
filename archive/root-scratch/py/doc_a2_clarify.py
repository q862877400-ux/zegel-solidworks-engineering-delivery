"""消解 A2 的**措辞歧义**：把「并入条目」明确到两层，并记录哪一层由谁把关。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（验收判据的澄清）
# 文件:   scripts/check_union_conventions.py 的 L155 / L188-L191 ——
#           「**`provenance` 的触发条件只有 `source_verified`**（裁断修正 B2）」
#           「R6：**只有来源派生的 `source_verified` 强制要 provenance**」
#         tools/union-sources.json —— **来源级** provenance（4 家，字段齐全，**门禁查这里**）
#         capabilities.yaml —— **能力级** provenance（29 条里 1 条）
# 定位:   ⚠ **更正我自己的已知事实 41。** 那条说「A2 的真实缺口是 29 条里 28 条未被分类」，
#         并据此打算「给每条加 source 标记」。**查了门禁之后发现前提不全**：
#
#   **A2 原文「每个**并入条目**带 `provenance`」里的「条目」有**两种读法**，答案相反：**
#     · **来源条目** ⇒ `tools/union-sources.json` 里 **4/4 完整**（repo/license/
#       declared_verified/note 四项齐全）⇒ **满足**
#     · **能力条目** ⇒ `capabilities[].provenance` **1/29** ⇒ 不满足
#   **而门禁实现的是**窄读法**：只有 `level == source_verified` 才强制。
#   本仓库 **`source_verified` 条目数为 0**（分布：verified=22 / stitched=6 /
#   not_implemented=1）⇒ **门禁层面零要求，所以门禁一直绿。**
#
#   **⇒ 正解不是「给 29 条硬编分类」（那是**带额外步骤的归属造假**），
#     而是**把这个歧义消解掉**：明确「条目」指哪一层、各由什么把关。**
#
#   ★ 另有一层认识：`level: verified` 说的是「**有我们自己的运行证据**」，
#     **不是**「这份代码是我们写的」。⇒ **上游代码经我们真机验证后标 verified 是**正确**的**，
#     A2 关心的「出处」由**来源级** provenance 承载。**两条线不该混。**
#
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 长内容走**短的单行字符串**（事实 48 定则）；跑完核对落盘。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
WS = Path(r"D:\AI\SW")

FACT41_FIX = (
    "**⚠ 2026-10-01 更正（查了门禁之后）**：那条「28 条未被分类」的结论**前提不全** —— "
    "A2 原文的「并入条目」有**两种读法**，答案相反：**来源条目**读法下 "
    "`tools/union-sources.json` **4/4 完整**（repo/license/declared_verified/note 四项齐全）⇒ **满足**；"
    "**能力条目**读法下 `capabilities[].provenance` **1/29** ⇒ 不满足。"
    "**而门禁（`check_union_conventions.py` L155/L189）实现的是**窄读法**："
    "「`provenance` 的触发条件**只有** `source_verified`」——**而本仓库 `source_verified` 条目数为 0**"
    "（level 分布 verified=22 / stitched=6 / not_implemented=1）⇒ **门禁层面零要求，所以它一直绿**。"
    "**⇒ 正解不是给 29 条硬编分类，而是**消解这个措辞歧义**。**"
    "★ 另一层认识：`level: verified` 说的是「**有我们自己的运行证据**」，**不是**「代码是我们写的」"
    "⇒ **上游代码经我们真机验证后标 verified 是**正确**的**；A2 关心的「出处」由**来源级** provenance 承载，"
    "**两条线不该混**。工具 `tools/propose_capability_sources.py` 仍有用（它给出的 "
    "**21/29 有证据分类**可作人工复核的起点，且它**纠正了**我对 `sw_weldment.py`/`sw_sheet_metal.py` 的误认）"
)

SECTION = ""


def main() -> int:
    # ① 把更正追加到 AGENTS.md 的事实 41 那一行**之后**（作为紧跟的说明行）
    f = WS / "AGENTS.md"
    t = f.read_text(encoding="utf-8")
    i = t.find("| 41 |")
    if i < 0:
        print("  ✗ 找不到 | 41 |"); return 1
    if "更正（查了门禁之后）" in t:
        print("  ⚠ 事实 41 的更正已存在")
    else:
        e = t.find("\n", i) + 1
        t = t[:e] + FACT41_FIX + "\n" + t[e:]
        f.write_text(t, encoding="utf-8")
        print("  ✓ AGENTS.md 事实 41 已加更正")

    # ② ROADMAP：把 ⑩ 那条的说法改准
    r = WS / "docs" / "ROADMAP.md"
    rt = r.read_text(encoding="utf-8")
    old = "               ⇒ **A2 的下一步**：拿这份提案逐条人工确证后写入 `capabilities[].source`\n"
    new = ("               ⇒ **⚠ 但 2026-10-01 查门禁后更正**：A2 的「并入条目」有**两种读法** ——\n"
           "                 **来源条目**读法下 `tools/union-sources.json` **4/4 完整** ⇒ **满足**；\n"
           "                 **能力条目**读法下 `capabilities[].provenance` 1/29 ⇒ 不满足；\n"
           "                 而**门禁实现的是窄读法**（只有 `source_verified` 才强制，**本仓库 0 条**）\n"
           "                 ⇒ **正解是消解措辞歧义**，不是给 29 条硬编分类\n"
           "               ⇒ 那份提案仍有用：作**人工复核的起点**（21/29 有证据）\n")
    if "但 2026-10-01 查门禁后更正" in rt:
        print("  ⚠ ROADMAP 已更正")
    elif old in rt:
        r.write_text(rt.replace(old, new, 1), encoding="utf-8")
        print("  ✓ ROADMAP 该条已改准")
    else:
        print("  ⚠ ROADMAP 找不到锚点")

    # ③ 落盘核对（事实 48 第 ② 条）
    t2 = f.read_text(encoding="utf-8")
    rt2 = r.read_text(encoding="utf-8")
    print()
    print("  ── 落盘核对 ──")
    print("    AGENTS.md 含「更正（查了门禁之后）」: %s"
          % ("是" if "更正（查了门禁之后）" in t2 else "**否**"))
    print("    ROADMAP 含「查门禁后更正」: %s"
          % ("是" if "查门禁后更正" in rt2 else "**否**"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
