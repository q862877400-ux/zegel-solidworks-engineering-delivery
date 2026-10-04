"""★ T4-1：从 C4 的 2.6 MB 产出里抽出 `unit_diff`(15) + `mark_diff`(10) 共 25 条，出逐条表。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(r"D:\AI\SW")
SRC = ROOT / "specs" / "204-bunny-moat-batches" / "recon" / "c4-merged.json"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
d = json.loads(SRC.read_text(encoding="utf-8"))
print("★ c4-merged 顶层:", list(d.keys()))
print("★ kinds:", json.dumps(d.get("kinds"), ensure_ascii=False)[:200])
print("★ n_boxes:", d.get("n_boxes"), "· tallies:", json.dumps(d.get("tallies"), ensure_ascii=False)[:160])
res = d["results"]
print("★ results: %s 条" % len(res))
print("★ 首条键:", sorted(res[0].keys()) if res else "-")

WANT = {"unit_diff", "mark_diff"}
#: ★★ `kind` 在**嵌套的 `conflicts` 列表里**（顶层每条只有 member/remarks_empty/
#:    example_more_specific/examples_actually_used）⇒ 必须先展开 ✓
#:    （★ 我第一版直接按顶层 kind 过滤 ⇒ 抽到 0 条，靠打印结构才发现）
flat = []
for cap in res:
    for c in (cap.get("conflicts") or []):
        if str(c.get("kind")) in WANT:
            flat.append({"member": cap.get("member"),
                         "examples_used": cap.get("examples_actually_used"),
                         **{k: v for k, v in c.items()}})
rows = flat
print("★★ 抽到 %d 条（unit_diff + mark_diff）" % len(rows))
print("   分类:", {k: sum(1 for r in rows if str(r.get("kind")) == k) for k in WANT})
print()
if rows:
    print("★ 首条全文（★ 看有哪些字段可用）:")
    print(json.dumps(rows[0], ensure_ascii=False, indent=1)[:1200])

#: ★ T4-1 的交付物：25 条逐条表（★ 供逐条判读；★ 按 D-4 是**候选队列**）
from collections import Counter
lines = [
    "# C4 的两类致命冲突：`unit_diff`(15) + `mark_diff`(10) —— 逐条表",
    "",
    "> **生成物** —— 由 `tools/t4_extract_unit_mark_conflicts.py` 产出，**不要手改**。",
    "> 输入：`specs/204-bunny-moat-batches/recon/c4-merged.json`（另一个对话的 C4 产出，**只读复用**）。",
    "",
    "## 一 · 为什么先做这两类",
    "",
    "★ C4 共报 598 条冲突（过引文闸 544），分类：`precondition_diff` 324 · `other_conflict` 174 ·",
    "`return_shape_diff` 75 · **`unit_diff` 15** · **`mark_diff` 10**。",
    "★★ 本表只取**后两类** —— 因为**单位写错、选择 mark 写错**会**直接让工具算错或选错**，",
    "★ 而前几类多半是「详略差异」（★ 另一对话的 V1 抽检：12 条里只 4 条真互斥 ⇒ 真冲突约 220–270）✓",
    "",
    "★★ **本表「不算什么」**：",
    "- ★ **不等于**「官方文档错了就一定是示例错」—— 本表只记**两侧不能同时成立**，谁对要逐条判；",
    "- ★ **不构成**任何「我们的实现是错的」结论 —— 要先看我们**实际怎么调**（另一步）；",
    "- ★ 来源全程 `conditional_pass`（该规格 REPORT §七 自陈 C4 只覆盖 91% 箱、丢箱偏向尾部）",
    "  ⇒ ★★ **候选队列，逐条过闸才采纳** ✓",
    "",
    "## 二 · 逐条（%d 条）" % len(rows),
    "",
    "| # | 成员 | 类 | ★ `Remarks` 说 | ★ 示例写 | 示例文件 | 判读 |",
    "|---:|---|---|---|---|---|---|",
]
for i, r in enumerate(rows, 1):
    def esc(x):
        return str(x or "").replace("|", "\\|").replace("\n", " ")[:170]
    lines.append("| %d | `%s` | %s | %s | %s | `%s` | %s |"
                 % (i, r.get("member"), r.get("kind"), esc(r.get("remarks_quote")),
                    esc(r.get("example_quote")), esc(r.get("example_file")), esc(r.get("why"))))
lines += ["", "## 三 · 成员分布", ""]
for m, n in Counter(r.get("member") for r in rows).most_common():
    lines.append("- `%s` × %d" % (m, n))
lines += ["", "## 四 · 下一步（T4-1 的「逐条核」）", "",
          "★ 对每条判三态：**成立**（我们照示例写会错）/ **不成立**（我们没照示例写）/ **查不到**；",
          "★ 成立的 ⇒ 核**我们实际怎么调**（`scripts/` 里对应实现），有证据才改 ✓"]
OUT = ROOT / "docs" / "recon-206"
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "conflicts-25.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print()
print("★ 写出 %s（%d 行 · %d 条）" % (OUT / "conflicts-25.md", len(lines), len(rows)))
print("★ 涉及 %d 个成员" % len({r.get("member") for r in rows}))
