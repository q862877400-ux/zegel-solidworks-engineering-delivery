"""★ T4-1 第三步（机械抽取）：把那 8 个「我们用到」的成员的判读材料抽到一处。"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
rows = json.loads((ROOT / "specs" / "204-bunny-moat-batches" / "recon"
                   / "c4-merged.json").read_text(encoding="utf-8"))["results"]
WANT = ("unit_diff", "mark_diff")

#: ★ 25 条冲突（带两侧原文）
conf: dict = defaultdict(list)
for cap in rows:
    for c in (cap.get("conflicts") or []):
        if str(c.get("kind")) in WANT:
            conf[cap.get("member")].append({
                "kind": c.get("kind"),
                "remarks": c.get("remarks_quote") or "",
                "example": c.get("example_quote") or "",
                "file": c.get("example_file") or "",
                "why": c.get("why") or "",
            })

#: ★ 上一轮查出的「我们用到」的 8 个（★ 硬编码自 conflicts-25-crosscheck.md §二）
USED = ["AutoDimension2", "FeatureCircularPattern4", "FeatureLinearPattern4",
        "InsertProtrusionBlend2", "InsertSewRefSurface", "InsertWeldmentTrimFeature2",
        "SetSystemValue3", "SetupSheet6"]

SRC = []
for d in ("scripts", "mcp-server", "tools"):
    SRC += sorted((ROOT / d).rglob("*.py"))

L = [
    "# T4-1 第三步 · 判读材料齐备版：8 个「我们用到」的成员",
    "",
    "> 生成物 —— 由 tools/t4_judge_materials.py 产出，不要手改。",
    "> ★ 目的：把判读所需的**三样材料**（我们的调用点 / 官方 Remarks 原文 / 官方示例原文）抽到一处，",
    "> 使判读变成小范围阅读，而不必再翻 2.6 MB 的原始 JSON。",
    "",
    "本表不算什么：",
    "",
    "- ★ 它**不判**对错（判读是人/模型的事，须读下面三样材料后下结论）；",
    "- ★ 我们那一行的**上下文**只给该行与前后各一行，可能不足以判 —— 需读全函数时另行打开；",
    "- ★ 官方侧的原文来自另一个对话的产出（`conditional_pass`），★ 采纳前须回查官方页 ✓",
    "",
    "---",
    "",
]

for i, m in enumerate(USED, 1):
    L.append("## %d · `%s`" % (i, m))
    L.append("")
    #: ① 我们的调用点
    sites = []
    for f in SRC:
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except Exception:                                          # noqa: BLE001
            continue
        for mm in re.finditer(r'get_com_member\([^,]+,\s*"%s"|\.%s\b|"%s"'
                              % (re.escape(m), re.escape(m), re.escape(m)), text):
            ln = text[:mm.start()].count("\n") + 1
            lines = text.splitlines()
            ctx = lines[max(0, ln - 2):ln + 1]
            sites.append((str(f.relative_to(ROOT)), ln, " / ".join(x.strip()[:110] for x in ctx)))
            break
    L.append("### ① 我们的调用点（%d 处）" % len(sites))
    L.append("")
    for f, ln, ctx in sites[:4]:
        L.append("- `%s:%d`" % (f, ln))
        L.append("  ```")
        L.append("  %s" % ctx[:300])
        L.append("  ```")
    if not sites:
        L.append("- ★ 没找到（上一轮说用到了，可能是注释里的提及）")
    L.append("")
    #: ② / ③ 官方两侧
    for j, c in enumerate(conf.get(m, []), 1):
        L.append("### ② 冲突 %d · `%s`" % (j, c["kind"]))
        L.append("")
        L.append("- ★ **官方 `## Remarks` 说**：%s" % (c["remarks"][:600] or "（空）"))
        L.append("- ★ **官方示例写**：`%s`" % (c["example"][:400] or "（空）"))
        L.append("- ★ 示例文件：`%s`" % c["file"])
        L.append("- ★ 另一个对话的判读：%s" % (c["why"][:300]))
        L.append("")
    L.append("---")
    L.append("")

L += [
    "## ★ 判读模板（★ 每条填一行；三态：成立 / 不成立 / 查不到）",
    "",
    "| 成员 | 类 | 我们用的是示例写法还是 Remarks 写法 | 结论 | 证据 |",
    "|---|---|---|---|---|",
]
for m in USED:
    for c in conf.get(m, []):
        L.append("| `%s` | %s | （待填）| （待填）| （待填）|" % (m, c["kind"]))
out = ROOT / "docs" / "recon-206" / "conflicts-8-judge-materials.md"
out.write_text("\n".join(L) + "\n", encoding="utf-8")
print("★ 写出 %s（%d 行）" % (out.name, len(L)))
print("★ 覆盖成员 %d 个 · 冲突条目 %d 条"
      % (len(USED), sum(len(conf.get(m, [])) for m in USED)))
print()
for m in USED:
    print("   %-30s 冲突 %d 条" % (m, len(conf.get(m, []))))
