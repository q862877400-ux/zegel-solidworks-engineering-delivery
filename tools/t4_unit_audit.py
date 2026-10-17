"""★ T4-1 机械判读（unit_diff）：我们的调用点附近有没有单位换算，换算方向是什么。"""
from __future__ import annotations

import ast
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

rows = json.loads((ROOT / "specs" / "204-bunny-moat-batches" / "recon"
                   / "c4-merged.json").read_text(encoding="utf-8"))["results"]
units: dict = defaultdict(list)
for cap in rows:
    for c in (cap.get("conflicts") or []):
        if str(c.get("kind")) == "unit_diff":
            units[cap.get("member")].append({
                "remarks": (c.get("remarks_quote") or "")[:220],
                "example": (c.get("example_quote") or "")[:160],
                "why": (c.get("why") or "")[:180]})
members = sorted(units)
print("★ unit_diff 涉及成员: %d 个" % len(members))
for m in members:
    print("   %s" % m)
print()

SRC = []
for d in ("scripts", "mcp-server", "tools"):
    SRC += sorted((ROOT / d).rglob("*.py"))


def sites_of(member: str) -> list:
    out = []
    for f in SRC:
        try:
            tree = ast.parse(f.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        for n in ast.walk(tree):
            hit = None
            if isinstance(n, ast.Call):
                fn = n.func
                nm = fn.id if isinstance(fn, ast.Name) else (
                    fn.attr if isinstance(fn, ast.Attribute) else "")
                if nm == "get_com_member" and len(n.args) >= 2:
                    a = n.args[1]
                    if isinstance(a, ast.Constant) and a.value == member:
                        hit = n.lineno
            elif isinstance(n, ast.Attribute) and n.attr == member:
                hit = n.lineno
            if hit:
                out.append((str(f.relative_to(ROOT)), hit))
    return out


#: ★★ 机械判据：调用点前后 15 行里**出现的换算形态**
CONV = (
    ("度→弧度", re.compile(r"math\.radians\(|\bdeg\(|radians\(")),
    ("弧度→度", re.compile(r"math\.degrees\(|\*\s*57\.3|/\s*0\.01745")),
    ("毫米→米", re.compile(r"/\s*1000(\.0)?\b|\*\s*0\.001\b")),
    ("米→毫米", re.compile(r"\*\s*1000(\.0)?\b|/\s*0\.001\b")),
    ("毫米→英寸", re.compile(r"/\s*25\.4\b")),
)

L = ["# unit_diff 冲突的机械判读：我们的调用点附近有没有单位换算", "",
     "> 生成物 —— 由 `tools/t4_unit_audit.py` 产出，不要手改。",
     "> 输入：`c4-merged.json`（只读）+ 本仓 `scripts/` `mcp-server/` `tools/`。", "",
     "## 一 · 口径（★ 先说判据）", "",
     "| 项 | 值 |", "|---|---|",
     "| `unit_diff` 冲突 | **%d** 条 |" % sum(len(v) for v in units.values()),
     "| 涉及成员 | **%d** 个 |" % len(members),
     "| ★ 判据 | 真调用点（`ast` 判）前后 **15 行**内出现的换算形态（度↔弧度 / 毫米↔米 / 毫米↔英寸）|",
     "",
     "★★ **本表「不算什么」**（★ 缺了它会被误用）：",
     "",
     "- ★ **不等于**「我们单位用错了」—— 它只说**窗口内有没有换算**；",
     "  ★★ 而「有没有换算」与「换算对不对」是**两件事** ⇒ ★ 结论必须**逐条对照官方 Remarks 的单位**才能下；",
     "- ★ **窗口内没有换算 ≠ 错** —— ★ 可能我们**本来就按官方要求的单位传**（那才是对的）；",
     "- ★ **窗口 15 行是启发式** ⇒ 换算写在别处（如上游调用方）时会误判；",
     "- ★ 只覆盖**我们真调用过**的成员 ✓",
     "",
     "## 二 · 逐成员", ""]

n_called = 0
for m in members:
    st = sites_of(m)
    cs = units[m]
    L += ["### `%s`（%d 条冲突）" % (m, len(cs)), ""]
    for c in cs:
        L.append("- ★ `Remarks`：%s" % c["remarks"].replace("|", "/"))
        L.append("- ★ 示例：`%s`" % c["example"].replace("|", "/"))
        L.append("- ★ 判读：%s" % c["why"].replace("|", "/"))
    L.append("")
    if not st:
        L.append("★ **我们没真调用过** ⇒ 该冲突对我们当前无直接影响 ✓")
        L.append("")
        continue
    n_called += 1
    for f, ln in st[:4]:
        text = (ROOT / f).read_text(encoding="utf-8", errors="replace").splitlines()
        win = "\n".join(text[max(0, ln - 15):ln + 15])
        found = [name for name, pat in CONV if pat.search(win)]
        L.append("- 调用点 `%s:%d` ⇒ %s"
                 % (f, ln, ("★ 窗口内有换算: " + " · ".join(found)) if found
                    else "★★ 窗口内**没有**换算（★ 可能本来就按官方单位传 ⇒ 不一定错）"))
    L.append("")

L += ["## 三 · ★ 小结", "",
      "★ 15 个 `unit_diff` 成员里 **%d 个我们真调用过** ✓" % n_called,
      "",
      "★ **下一步（★ 仍需人读官方页）**：对每个调用点读官方 `## Remarks` 的**单位声明** ⇒",
      "★ 判「我们传的值是不是那个单位」—— ★★ 本表只给「有没有换算」这个机械事实，**不判对错** ✓",
      "★ 成立且有证据的才改；★ 按 D-3，改之前上真机一次一条 ✓", ""]
out = ROOT / "docs" / "recon-206" / "unit-audit.md"
out.write_text("\n".join(L) + "\n", encoding="utf-8")
print("★ 写出 %s（%d 行）" % (out.name, len(L)))
print("★ 真调用过的成员: %d / %d" % (n_called, len(members)))
for m in members:
    print("   %-32s 真调用 %d 处" % (m, len(sites_of(m))))
