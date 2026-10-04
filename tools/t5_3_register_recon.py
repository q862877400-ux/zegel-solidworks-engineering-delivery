"""★ T5-3：登记两个 recon 目录的原始 JSON 为**只读数据集**（★ 建议稿，不替主线做决定）。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(r"D:\AI\SW")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DIRS = [("203", sorted((ROOT.glob("specs/203-*/recon/*.json")))),
        ("204", sorted((ROOT.glob("specs/204-*/recon/*.json"))))]

#: ★ 每个文件的用途（★ 从已知事实/交接节里来的，不是我现编的）
ROLE = {
    "b2-defects.json": "★ 官方源缺陷 970 条（verified 964）—— `check_official_source_defects` 的输入",
    "c3-merged.json": "★ 前置对账 98 能力 / 534 条前置 —— T2 的输入",
    "c4-merged.json": "★ 内部冲突 598 条（`unit_diff`/`mark_diff` 等）—— T4 的输入",
    "c5-gap-handcheck.json": "★ 换名已有 24 行 —— T1 别名表的输入",
    "a-task-ifaces.json": "★ A 路：任务→接口映射",
    "b1-merged.json": "★ B1：合并后的扫描结果",
    "b2-deadlinks.json": "★ 死链候选 212 条",
    "c1-truth.json": "★ C1 真值集",
    "c2-calls-verified.json": "★ C2 调用核验",
    "c5-triage.json": "★ C5 分诊",
}

L = [
    "# recon 原始数据集（★ **只读**）—— 登记与使用说明",
    "",
    "> 生成物 —— 由 `tools/t5_3_register_recon.py` 产出，不要手改。",
    "> ★ 目的：把另一个对话那两批扫描的**原始 JSON** 登记成**只读数据集**，",
    "> 使后来的人知道**它们是什么、谁维护、能不能改** ✓",
    "",
    "## 一 · ★ 铁律（★ 三条，违反其一就会破坏可复核性）",
    "",
    "```",
    "① ★★ 这两个目录【只读】—— 它们是【另一个对话】的写盘范围，",
    "   本线（规格 206）**只读复用**，绝不改写、绝不提交（★ 见规格 206 的 git 纪律）✓",
    "② ★★ **不重跑**已跑过的扫描 —— 那些扫描（Bunny 逐页核对）花了对方大量算力，",
    "   重跑既浪费又会产生**与基线不一致的第二份真值** ⇒ ★ 只读现成的 JSON ✓",
    "③ ★★ 引用它们的数据时必须带**口径**：这些是 `conditional_pass` 产出",
    "   （★ 对方 REPORT §七 自陈：C4 只覆盖 91% 箱、丢箱系统偏向尾部 等）",
    "   ⇒ **一律当候选队列，逐条过闸才采纳**（规格 206 的 D-4）✓",
    "```",
    "",
    "## 二 · 清单（★ **%d** 个 JSON）" % sum(len(v) for _k, v in DIRS),
    "",
]
for tag, files in DIRS:
    L += ["### 规格 %s 的那批（**%d** 个）" % (tag, len(files)), "",
          "| 文件 | 大小 | ★ 已知用途 |", "|---|---:|---|"]
    for f in files:
        kb = f.stat().st_size / 1024.0
        L.append("| `%s` | %.1f KB | %s |" % (f.name, kb, ROLE.get(f.name, "（未标注）")))
    L.append("")
L += [
    "## 三 · ★ 本线（规格 206）已经从它们里榨出了什么",
    "",
    "| 产出 | 用了哪个 JSON | 落在哪 |",
    "|---|---|---|",
    "| 别名表（三道闸 → 留 5 条）| `c5-gap-handcheck.json` | `docs/tool-aliases.md` |",
    "| 前置缺口清单（可机检 102 条）| `c3-merged.json` | `docs/precondition-coverage-gaps.md` |",
    "| 官方源缺陷门禁（修 5 处真断链）| `b2-defects.json` | `scripts/check_official_source_defects.py` |",
    "| 错拼→正确名 130 对 | `b2-defects.json` | `docs/recon-206/spelling-pairs.md` |",
    "| 25 条冲突 + 逐条核 + 判读材料 | `c4-merged.json` | `docs/recon-206/conflicts-25*.md` |",
    "| ★ 写码前必查表（368 成员 / 424 条）| `c4-merged.json` | `docs/recon-206/pre-code-conflict-lookup.md` |",
    "",
    "## 四 · ★ 还没榨的（★ 留给接手的人）",
    "",
    "- ★ `c4-merged.json` 的 **3709 条 `example_more_specific`**（★ T4-2：对方自标只过单侧闸、10–25% 需复核）",
    "- ★ `c4-merged.json` 的 **`precondition_diff` 324 条**（★ 已进必查表，但未逐条判）",
    "- ★ `c2-calls-verified.json`（812 KB）**本线一次都没用**（★ 可能的用途：与我们自己的调用点对账）",
    "",
    "★ **给主线的建议**（★ 只出建议，不替它决定）：",
    "★ 若要把这两个目录固化成数据集，建议**加一条门禁**：断言它们**未被修改**",
    "（如记下各文件的 sha256，改动即报）—— ★ 但那是主线的决定，本文件只登记 ✓",
]
out = ROOT / "docs" / "recon-206" / "README.md"
out.write_text("\n".join(L) + "\n", encoding="utf-8")
print("★ 写出 %s（%d 行）" % (out.name, len(L)))
print("★ 登记 %d 个 JSON（203: %d · 204: %d）"
      % (sum(len(v) for _k, v in DIRS), len(DIRS[0][1]), len(DIRS[1][1])))
