"""★ T4-2 机械复核：3709 条 example_more_specific 分类 + 与我们真调用交叉。"""
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

#: ★ 3709 条在每条 result 的 `example_more_specific` 里
ms: dict = defaultdict(list)
n_total = 0
for cap in rows:
    for e in (cap.get("example_more_specific") or []):
        n_total += 1
        ms[cap.get("member")].append(e)
print("★★ example_more_specific 总数: **%d**（★ 对方 tally 说是 3806；★ 实量以此为准）" % n_total)
print("★★ 涉及成员: **%d** 个" % len(ms))

#: ★ 形态分类（★ 从条目自身的字段/文本推，不编）
shape = Counter()
for m, items in ms.items():
    for e in items:
        if isinstance(e, dict):
            shape["dict: %s" % ",".join(sorted(e.keys())[:3])] += 1
        else:
            shape["str"] += 1
for k, v in shape.most_common(6):
    print("   %-40s %d" % (k, v))
print()

SRC = []
for dd in ("scripts", "mcp-server", "tools"):
    SRC += sorted((ROOT / dd).rglob("*.py"))


def called(member: str) -> list:
    """★ 我们真调用过的证据（ast 判 —— 事实 528）。"""
    out = []
    for f in SRC:
        try:
            tree = ast.parse(f.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        for n in ast.walk(tree):
            if isinstance(n, ast.Call):
                fn = n.func
                nm = fn.id if isinstance(fn, ast.Name) else (
                    fn.attr if isinstance(fn, ast.Attribute) else "")
                if nm == "get_com_member" and len(n.args) >= 2:
                    a = n.args[1]
                    if isinstance(a, ast.Constant) and a.value == member:
                        out.append((str(f.relative_to(ROOT)), n.lineno))
            elif isinstance(n, ast.Attribute) and n.attr == member:
                out.append((str(f.relative_to(ROOT)), n.lineno))
    return out


hot = {m: called(m) for m in ms}
ours = {m: v for m, v in hot.items() if v}
print("★★★ 与「我们真调用过」交叉：**%d / %d** 个成员我们真调用" % (len(ours), len(ms)))
print("   ★ 我们真调用的、且有条目的 top 12:")
for m, n in sorted(((m, len(ms[m])) for m in ours), key=lambda x: -x[1])[:12]:
    print("      %-34s %d 条（调用点 %s:%d）" % (m, n, ours[m][0][0], ours[m][0][1]))

L = [
    "# T4-2 机械复核：`example_more_specific` 的分类与「与我们有关」的那一撮",
    "",
    "> 生成物 —— 由 `tools/t4_2_more_specific.py` 产出，不要手改。",
    "> 输入：`c4-merged.json`（只读）+ 本仓 `scripts/` `mcp-server/` `tools/`。",
    "",
    "## 一 · 口径",
    "",
    "| 项 | 值 |",
    "|---|---|",
    "| `example_more_specific` 条目 | **%d**（★ 另一对话的 tally 写 3806；★ **实量以此为准**）|" % n_total,
    "| 涉及成员 | **%d** |" % len(ms),
    "| ★★ 其中**我们真调用过**的成员 | **%d** |" % len(ours),
    "",
    "★★ **本表「不算什么」**（★ 缺了它会被误用）：",
    "",
    "- ★ **不等于**「这 %d 条都是缺陷」—— `example_more_specific` 的**语义是「示例比 Remarks 更具体」**，" % n_total,
    "  ★★ 那是**中性的**（示例给了更多信息，不等于官方自相矛盾）⇒ ★ 本表**不判对错**；",
    "- ★ 另一对话自标它**只过了单侧闸**、**10–25% 需复核** ⇒ ★ 这批的**真缺陷率未被独立验证** ✓；",
    "- ★ 「我们真调用过」用的是 `ast` 判据（事实 528）⇒ ★ **只覆盖两种调用形态**，`getattr` 动态取用会漏 ✓",
    "",
    "## 二 · ★★ 与我们有关的成员（**%d** 个 · 按条目数排序）" % len(ours),
    "",
    "| 成员 | 条目数 | 我们的调用点 |",
    "|---|---:|---|",
]
for m, n in sorted(((m, len(ms[m])) for m in ours), key=lambda x: -x[1]):
    L.append("| `%s` | %d | `%s:%d` |" % (m, n, ours[m][0][0], ours[m][0][1]))
L += ["", "## 三 · ★ 下一步（★ 仍需人读的那部分）", "",
      "★ 对第二节那 %d 个成员：逐条读 `Remarks` 与示例 ⇒ 判「示例多给的信息是否**改变调用形状**」；" % len(ours),
      "★ 只有**改变调用形状**的才值得动（★ 单纯「说得更细」不用管）✓", "",
      "★ **抽样建议**（★ 留给下一步）：先抽第二节里条目最多的 **20 条**人工判，",
      "★ 得「真改变形状」的比例后，再决定是否全量复核 ✓", ""]
out = ROOT / "docs" / "recon-206" / "more-specific-audit.md"
out.write_text("\n".join(L) + "\n", encoding="utf-8")
print()
print("★ 写出 %s（%d 行）" % (out.name, len(L)))
