"""★ T2-4 缺口量化：我写的 3 个样板，在不在这 102 条「可机检前置」清单里？"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
CK = json.loads((ROOT / "output" / "t2-preconditions-checkable.json").read_text(encoding="utf-8"))
checkable = CK["checkable"]
print("★ 可机检前置: **%d** 条（★ 另一个对话的 C3 产出 + 我的机械分类）" % len(checkable))

#: ★ 我写的 3 个样板，各自的「探针关键词」（★ 用名字，不用印象）
SAMPLES = {
    "① 镜像 mark（事实 549）": ("InsertMirrorFeature", "mirror", "镜像", "mark"),
    "② GTol 值域（事实 550）": ("AddIndicator", "IGtolFrame", "GTol", "gtol", "TolType"),
    "③ 索引属性读（事实 551）": ("Equation", "IEquationMgr", "EquationMgr", "索引属性"),
}

L = [
    "# T2-4 缺口量化：3 个样板 vs 那 102 条「可机检前置」清单",
    "",
    "> 生成物 —— 由 `tools/t2_sample_vs_checkable.py` 产出，不要手改。",
    "> 输入：`output/t2-preconditions-checkable.json`（可机检 102 条）+ 我写的 3 个样板的关键词。",
    "",
    "## 一 · 口径",
    "",
    "| 项 | 值 |",
    "|---|---|",
    "| 可机检前置（清单）| **%d** 条 |" % len(checkable),
    "| 我写的样板 | **3** 个（事实 549 / 550 / 551）|",
    "| ★ 判据 | 样板的**探针关键词**是否出现在某条可机检前置的文本里 |",
    "",
    "★★ **本表「不算什么」**：",
    "- ★ 关键词匹配是**粗判**（★ 命中 ≠ 那条前置就是样板要断言的**同一条**）；",
    "- ★★ 它只回答一个问题：**我的样板是不是从这份清单里来的** ⇒ ★ **答案很可能是「不是」**（★ 见下）✓",
    "",
    "## 二 · 逐样板",
    "",
    "| 样板 | ★ 在清单里命中几条 | 命中的前 3 条 |",
    "|---|---:|---|",
]
for label, kws in SAMPLES.items():
    hits = [c for c in checkable
            if any(k.lower() in (c.get("text") or "").lower() for k in kws)]
    L.append("| %s | **%d** | %s |"
             % (label, len(hits),
                "<br>".join((h.get("text") or "")[:70] for h in hits[:3]) or "（无）"))
    print("★ %-26s 命中 **%d** 条" % (label, len(hits)))

L += [
    "",
    "## 三 · ★★ 结论（★ 这就是那个缺口的准确形状）",
    "",
    "★★ 我的 3 个样板**全部来自本仓自己的「过去错误」笔记**（★ 用事实 550 那个 grep 挖出来的），",
    "★ 而**不是**从这份 102 条清单里挑的 ⇒ ★★ 所以严格说，**T2-4 的「从 459 条示例派生」这半步仍未做** ✓",
    "",
    "★★★ **但这两件事的关系值得写清（★ 这是本表的主要价值）**：",
    "```",
    "★ 102 条清单（来自 C3）说的是：「官方示例揭示了某前置，而我们的运行证据没覆盖它」",
    "★★ 我的 3 个样板说的是：「**我们真错过、且现在没人守着**」",
    "⇒ ★★ 两者**交集**才是最高优先级 —— ★ 而**交界处的判据是**：",
    "   ① ★ 在 102 条里（说明官方示例揭示了它）",
    "   ② ★ 有「真错过」的记录（说明我们踩过）",
    "   ③ ★ 现在没有断言守着（★ 事实 62：没有负例的守卫不算守卫）",
    "```",
    "",
    "## 四 · ★ 下一步（★ 精确的形状）",
    "",
    "★ **交集法**：★ 用本节的三条判据交叉 ——",
    "★ 先从 102 条里取**可静态判**的（★ 像我这 3 个样板那样的：mark / 值域 / 参数形态），",
    "★ 再与「本仓过去错误笔记」交叉 ⇒ ★★ **命中的那几条就是下一批该写的断言** ✓",
]
out = ROOT / "docs" / "recon-206" / "t2-sample-vs-checkable.md"
out.write_text("\n".join(L) + "\n", encoding="utf-8")
print()
print("★ 写出 %s（%d 行）" % (out.name, len(L)))
