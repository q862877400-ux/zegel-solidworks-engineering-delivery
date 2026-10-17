"""★ T4-3：建「写码前必查表」+ 量 AGENTS.md 的指令预算余量（★ 超预算会静默截断）。"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BUDGET = 65536                                  #: ★ 指令预算（本仓已知约束）

agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
nb = len(agents.encode("utf-8"))
print("★ AGENTS.md: %d 字节 / 预算 %d ⇒ 已用 **%.1f%%**" % (nb, BUDGET, 100.0 * nb / BUDGET))
print("★ 余量: **%d** 字节 ⇒ ★ 加一行（约 150–250 字节）%s"
      % (BUDGET - nb, "**可行**" if BUDGET - nb > 400 else "★★ **不可行（会挤掉别的内容）**"))
print()

d = json.loads((ROOT / "specs" / "204-bunny-moat-batches" / "recon"
                / "c4-merged.json").read_text(encoding="utf-8"))
rows = d["results"]
allc = []
for cap in rows:
    for c in (cap.get("conflicts") or []):
        allc.append({"member": cap.get("member"), "kind": c.get("kind"),
                     "remarks": c.get("remarks_quote") or "",
                     "example": c.get("example_quote") or "",
                     "file": c.get("example_file") or "",
                     "why": c.get("why") or ""})
print("★ 全量冲突: **%d** 条" % len(allc))
print("   ★ 按类: %s" % dict(Counter(c["kind"] for c in allc)))
print("   ★ 另一对话 qa 口径: quote_ok=%s · quote_bad=%s（★ 过引文闸后 544）"
      % (d.get("quote_ok"), d.get("quote_bad")))

#: ★★ 「写码前必查表」：按成员归并，只留**最需要查**的那几类
PRIORITY = ("unit_diff", "mark_diff", "return_shape_diff", "precondition_diff")
by_member: dict = defaultdict(list)
for c in allc:
    if c["kind"] in PRIORITY and c["member"]:
        by_member[c["member"]].append(c)
print()
print("★ 优先四类涉及成员: **%d** 个 · 条目 **%d** 条"
      % (len(by_member), sum(len(v) for v in by_member.values())))

L = [
    "# 写码前必查表：这些官方成员的 `Remarks` 与官方示例**不能同时成立**",
    "",
    "> 生成物 —— 由 `tools/t4_3_build_lookup.py` 产出，不要手改。",
    "> 输入：`specs/204-bunny-moat-batches/recon/c4-merged.json`（另一个对话的 C4 产出，只读复用）。",
    "> ★ 用法：**动手碰下表中任一成员之前，先看一眼它这一行** —— 它是官方文档内部的两侧对不上。",
    "",
    "## 一 · 口径（★ 与数字一起读）",
    "",
    "| 项 | 值 |",
    "|---|---|",
    "| 全量冲突 | **%d** 条（另一对话的机械报出）|" % len(allc),
    "| 过引文闸 | **%s**（★ 其 `quote_ok`）|" % d.get("quote_ok"),
    "| ★ 本表取的类 | `unit_diff` · `mark_diff` · `return_shape_diff` · `precondition_diff` |",
    "| ★ 涉及成员 | **%d** 个 · 条目 **%d** 条 |"
    % (len(by_member), sum(len(v) for v in by_member.values())),
    "",
    "★★ **本表「不算什么」**（★ 缺了它，这张表会被误用）：",
    "",
    "- ★ **不等于**「官方文档错了、示例对」—— 它只记**两侧不能同时成立**，★ **谁对要逐条判**；",
    "- ★★ **不等于**「我们的实现错了」—— ★ 要用 `ast` 判**我们有没有真调用**"
    "（★ 事实 528：文本命中 ≠ 真调用）；",
    "- ★ ★ 不取 `other_conflict`(174) —— ★ 另一对话的 V1 抽检：12 条里只 4 条真互斥，"
    "**其余是「详略差异」不是矛盾** ⇒ 真冲突约 220–270 ✓",
    "- ★ 来源全程 `conditional_pass`（该规格 REPORT §七：C4 只覆盖 **91%** 箱、**丢箱系统偏向尾部**）；",
    "  ★★ **且本表未回查官方页原文** ⇒ ★ **采纳前须回查** ✓",
    "",
    "## 二 · 按类分列（★ 先看最危险的 `unit_diff` / `mark_diff`）",
    "",
]
for kind in ("unit_diff", "mark_diff", "return_shape_diff", "precondition_diff"):
    items = [c for c in allc if c["kind"] == kind]
    if not items:
        continue
    L.append("### `%s`（%d 条）" % (kind, len(items)))
    L.append("")
    for c in items[:60]:
        L.append("- **`%s`**" % c["member"])
        L.append("  - ★ `Remarks`：%s" % (c["remarks"][:260] or "（空）"))
        L.append("  - ★ 示例：`%s`（`%s`）" % (c["example"][:160] or "（空）", c["file"][:70]))
        L.append("  - ★ 判读：%s" % (c["why"][:200] or "（空）"))
    if len(items) > 60:
        L.append("- ★ 其余 %d 条见 `c4-merged.json` ✓" % (len(items) - 60))
    L.append("")
L += [
    "## 三 · ★ 我们**真调用**过的成员（★ 优先查这批 —— 用 `ast` 判，事实 528）",
    "",
    "★ 见 `docs/recon-206/conflicts-25-crosscheck.md` §五（真调用 7 个 / 只出现在文本里 1 个 / 没出现 11 个）✓",
    "",
    "## 四 · ★ 怎么用（★ 接进哪一步）",
    "",
    "★ 本表是「官方文档是第 0 步」那条链的**第 0.5 步**：",
    "```",
    "① 官方页（签名 + Remarks）→ ② ★★ **本表（先看这个成员有没有内部冲突）** →",
    "③ docs/dead-ends.md → ④ 该能力的 limitations → ⑤ known-facts.md → ⑥ 动手",
    "```",
    "⚠ ★★ **本表暂不写进 `AGENTS.md`** —— 因为该文件的指令预算是 65536 字节、",
    "当前已用 **%.1f%%**（余量 %d 字节），★ 加行有**静默截断最新条目**的风险" % (100.0 * nb / BUDGET, BUDGET - nb),
    "（★ 本仓自己记过这个坑）⇒ ★ **改由本文件自荐 + 交接节指向**，等 `AGENTS.md` 腾出空间再挂 ✓",
]
out = ROOT / "docs" / "recon-206" / "pre-code-conflict-lookup.md"
out.write_text("\n".join(L) + "\n", encoding="utf-8")
print()
print("★ 写出 %s（%d 行）" % (out.name, len(L)))
