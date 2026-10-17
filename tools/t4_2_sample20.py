"""★ T4-2 抽样表：258 个「与我们有关」的成员里，取条目最多的 20 个，抽齐判读材料。"""
from __future__ import annotations

import ast
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

d = json.loads((ROOT / "specs" / "204-bunny-moat-batches" / "recon"
                / "c4-merged.json").read_text(encoding="utf-8"))
ms: dict = defaultdict(list)
for cap in d["results"]:
    for e in (cap.get("example_more_specific") or []):
        ms[cap.get("member")].append(e)

#: ★ 单遍建索引（★ 事实 536 的教训：先建索引再查）
sites: dict = defaultdict(list)
for dd in ("scripts", "mcp-server", "tools"):
    for f in sorted((ROOT / dd).rglob("*.py")):
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

ours = {m: sites[m] for m in ms if sites.get(m)}
top = sorted(ours, key=lambda m: (-len(ms[m]), m))[:20]
print("★ 与我们有关的成员 %d 个 ⇒ 抽条目最多的 **%d** 个" % (len(ours), len(top)))
print()

L = [
    "# T4-2 抽样表：条目最多的 **20** 个「与我们有关」的成员",
    "",
    "> 生成物 —— 由 `tools/t4_2_sample20.py` 产出，不要手改。",
    "> ★ 用途：`example_more_specific` 共 **3806** 条 / **2242** 个成员，其中 **258** 个我们真调用过。",
    "> ★★ 本表从那 258 里取**条目最多的 20 个**，把判读材料抽齐 ⇒ **判读变成小范围阅读** ✓",
    "",
    "## 一 · 口径（★ 先说清楚）",
    "",
    "| 项 | 值 |",
    "|---|---|",
    "| 全量 `example_more_specific` | **3806** 条（★ 目标写 3709，★ 实量以此为准）|",
    "| 涉及成员 | **2242** |",
    "| ★ 我们真调用过的 | **258** |",
    "| ★★ 本表抽样 | **20**（★ 按条目数降序，与 D-1 的抽检量一致）|",
    "",
    "★★ **本表「不算什么」**（★ 缺了它会被误用）：",
    "",
    "- ★★ **不等于**「这 20 条是缺陷」—— 该字段语义是「**示例比 Remarks 更具体**」，",
    "  ★ 那是**中性的** ⇒ ★ 判读要问的是**「示例多给的信息是否改变调用形状」** ✓；",
    "- ★ 抽样**不随机**（★ 按条目数取头部）⇒ ★★ **不能**用它估计全量的缺陷率；",
    "  ★ 要估率得**随机抽**（★ 那是另一件事）✓；",
    "- ★ 判读材料来自另一个对话的 `conditional_pass` 产出 ⇒ ★ **采纳前须回查官方页** ✓",
    "",
    "---",
    "",
]

for i, m in enumerate(top, 1):
    items = ms[m]
    L += ["## %d · `%s`（%d 条 · 我们的调用点 `%s:%d`）"
          % (i, m, len(items), ours[m][0][0], ours[m][0][1]), ""]
    for j, e in enumerate(items[:6], 1):
        if isinstance(e, dict):
            L.append("- **%d)** %s" % (j, json.dumps(e, ensure_ascii=False)[:420]))
        else:
            L.append("- **%d)** %s" % (j, str(e)[:420]))
    if len(items) > 6:
        L.append("- ★ 其余 %d 条见 `c4-merged.json` ✓" % (len(items) - 6))
    L.append("")

L += [
    "## ★ 判读模板（★ 每条填一行；★ 只关心「是否改变调用形状」）",
    "",
    "| 成员 | 条目数 | ★ 示例多给的信息**是否改变调用形状** | 结论 | 证据 |",
    "|---|---:|---|---|---|",
]
for m in top:
    L.append("| `%s` | %d | （待填）| （待填）| （待填）|" % (m, len(ms[m])))
L += ["", "★ **定案要求**（★ 沿用 T4-1 的经验）：★ 机械表只给材料，",
      "★★ **必须读我们那一行代码才能定案**（事实 535：看着像缺陷的读完可能会反转）✓", ""]
out = ROOT / "docs" / "recon-206" / "more-specific-sample20.md"
out.write_text("\n".join(L) + "\n", encoding="utf-8")
print("★ 写出 %s（%d 行）" % (out.name, len(L)))
for m in top:
    print("   %-34s %d 条" % (m, len(ms[m])))
