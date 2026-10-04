"""★ T4-2 机械复核（单遍版）：3709 条 example_more_specific 分类 + 与我们真调用交叉。

★ 与上一版的差别：**只解析每个文件一次**（上一版对每个成员都重解析全部文件 ⇒ O(n×m) 跑不完）✓
"""
from __future__ import annotations

import ast
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"D:\AI\SW")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

d = json.loads((ROOT / "specs" / "204-bunny-moat-batches" / "recon"
                / "c4-merged.json").read_text(encoding="utf-8"))
rows = d["results"]
print("★ c4 tallies:", json.dumps(d.get("tallies"), ensure_ascii=False))

ms: dict = defaultdict(list)
n_total = 0
for cap in rows:
    for e in (cap.get("example_more_specific") or []):
        n_total += 1
        ms[cap.get("member")].append(e)
print("★★ example_more_specific 实量: **%d** 条 / **%d** 个成员" % (n_total, len(ms)))

#: ★ 单遍：解析每个 .py 一次，收集「成员 → 调用点」
SRC = []
for dd in ("scripts", "mcp-server", "tools"):
    SRC += sorted((ROOT / dd).rglob("*.py"))
sites: dict = defaultdict(list)
for f in SRC:
    try:
        tree = ast.parse(f.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        continue
    rel = str(f.relative_to(ROOT))
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            fn = n.func
            nm = fn.id if isinstance(fn, ast.Name) else (
                fn.attr if isinstance(fn, ast.Attribute) else "")
            if nm == "get_com_member" and len(n.args) >= 2:
                a = n.args[1]
                if isinstance(a, ast.Constant) and isinstance(a.value, str):
                    sites[a.value].append((rel, n.lineno))
        elif isinstance(n, ast.Attribute):
            sites[n.attr].append((rel, n.lineno))
print("★ 单遍扫出被指名引用的 COM 成员: **%d** 个" % len(sites))

ours = {m: sites[m] for m in ms if sites.get(m)}
print("★★★ 交叉：**%d / %d** 个成员我们真调用过" % (len(ours), len(ms)))
print("   ★ 我们真调用、且条目最多的 top 12:")
for m, n in sorted(((m, len(ms[m])) for m in ours), key=lambda x: -x[1])[:12]:
    print("      %-34s %d 条（%s:%d）" % (m, n, ours[m][0][0], ours[m][0][1]))

L = [
    "# T4-2 机械复核：`example_more_specific` 的分类与「与我们有关」的那一撮",
    "",
    "> 生成物 —— 由 `tools/t4_2_more_specific_b.py` 产出，不要手改。",
    "> 输入：`c4-merged.json`（只读）+ 本仓 `scripts/` `mcp-server/` `tools/`。",
    "",
    "## 一 · 口径",
    "",
    "| 项 | 值 |",
    "|---|---|",
    "| `example_more_specific` 条目 | **%d**（★ 另一对话的 tally 写 3806；★ **实量以此为准**）|" % n_total,
    "| 涉及成员 | **%d** |" % len(ms),
    "| ★★ 其中我们真调用过的成员 | **%d** |" % len(ours),
    "",
    "★★ **本表「不算什么」**（★ 缺了它会被误用）：",
    "",
    "- ★ **不等于**「这 %d 条都是缺陷」—— 该字段的语义是「**示例比 Remarks 更具体**」，" % n_total,
    "  ★★ 那是**中性的**（示例给了更多信息 ≠ 官方自相矛盾）⇒ ★ 本表**不判对错** ✓；",
    "- ★ 另一对话自标它**只过了单侧闸**、**10–25% 需复核** ⇒ ★ 真缺陷率**未被独立验证** ✓；",
    "- ★ 「我们真调用过」用 `ast` 判（事实 528）⇒ ★ 只覆盖两种形态，`getattr` 动态取用会漏 ✓；",
    "- ★★ **本表把这批收窄到「与我们有关」的子集** —— 那才是值得花时间的部分 ✓",
    "",
    "## 二 · ★★ 与我们有关的成员（**%d** 个 · 按条目数排序）" % len(ours),
    "",
    "| 成员 | 条目数 | 我们的调用点 |",
    "|---|---:|---|",
]
for m, n in sorted(((m, len(ms[m])) for m in ours), key=lambda x: -x[1]):
    L.append("| `%s` | %d | `%s:%d` |" % (m, n, ours[m][0][0], ours[m][0][1]))
L += ["", "## 三 · ★ 下一步（★ 仍需人读的那部分）", "",
      "★ 对第二节那 %d 个成员：逐条读 `Remarks` 与示例 ⇒ 判「示例多给的信息**是否改变调用形状**」；" % len(ours),
      "★ 只有**改变调用形状**的才值得动（★ 单纯「说得更细」不用管）✓", "",
      "★ **抽样建议**（★ 留给下一步）：先抽第二节里条目最多的 **20 条**人工判，",
      "★ 得「真改变形状」的比例后，再决定是否全量复核 ✓", ""]
out = ROOT / "docs" / "recon-206" / "more-specific-audit.md"
out.write_text("\n".join(L) + "\n", encoding="utf-8")
print()
print("★ 写出 %s（%d 行）" % (out.name, len(L)))
