"""★ T4-1 机械判读：mark_diff 冲突下，我们的调用点是否用了「能带 mark 的选择 API」。"""
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
marks: dict = defaultdict(list)
for cap in rows:
    for c in (cap.get("conflicts") or []):
        if str(c.get("kind")) == "mark_diff":
            marks[cap.get("member")].append({
                "remarks": (c.get("remarks_quote") or "")[:200],
                "example": (c.get("example_quote") or "")[:160],
                "why": (c.get("why") or "")[:160]})
members = sorted(marks)
print("★ mark_diff 涉及成员: %d 个 %s" % (len(members), ", ".join(members)))
print()

SRC = []
for d in ("scripts", "mcp-server", "tools"):
    SRC += sorted((ROOT / d).rglob("*.py"))


def sites_of(member: str) -> list:
    """★ 真调用点（ast 判 —— 事实 528：文本命中 ≠ 真调用）。"""
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


#: ★★ 机械判据：调用点前后 12 行里，有没有「能带 mark 的选择」——
#:   `SelectByID2(` 的第 6 个实参是 mark（★ 本仓 `_select_by_id` 包了它）；
#:   `Select4(` **没有 mark 形参**（★ 已知事实 32）⇒ 只有 Select4 而没有 mark ⇒ 缺 ✓
HAS_MARK = re.compile(r"mark\s*=|SelectByID2\(|_select_by_id\(")
ONLY_SELECT4 = re.compile(r"\.Select4\(|Select4\(")

L = ["# mark_diff 冲突的机械判读：我们的调用点用没用「能带 mark 的选择 API」", "",
     "> 生成物 —— 由 `tools/t4_mark_audit.py` 产出，不要手改。",
     "> 输入：`c4-merged.json`（只读）+ 本仓 `scripts/` `mcp-server/` `tools/`。", "",
     "## 一 · 口径（★ 先说判据，再说数）", "",
     "| 项 | 值 |", "|---|---|",
     "| `mark_diff` 冲突 | **%d** 条 |" % sum(len(v) for v in marks.values()),
     "| 涉及成员 | **%d** 个 |" % len(members),
     "| ★ 判据 | 真调用点（`ast` 判）前后 **12 行**内：有 `mark=` / `SelectByID2(` / `_select_by_id(` ⇒ **带 mark**；"
     "**只有** `Select4(` ⇒ **不带 mark**（★ `Select4` 没有 mark 形参，已知事实 32）|",
     "",
     "★★ **本表「不算什么」**（★ 缺了它这张表会被误用）：",
     "",
     "- ★ **不等于**「我们写错了」—— 它只说**我们的调用点带不带 mark**；",
     "  ★ 官方那一侧的 `mark_diff` 是 **Remarks 与示例互相矛盾** ⇒ ★★ **两类各自都可能对**，",
     "  ★ 结论要**逐条读官方页**才能下（★ 本表只给机械事实）；",
     "- ★ **窗口 12 行**是启发式 ⇒ ★ 调用点离选择很远时会误判（★ 标 `unknown`）；",
     "- ★ 只覆盖**我们真调用过**的成员 —— ★ 没调用的不在表里 ✓",
     "",
     "## 二 · 逐成员", ""]

for m in members:
    st = sites_of(m)
    cs = marks[m]
    L += ["### `%s`（%d 条冲突）" % (m, len(cs)), ""]
    for c in cs:
        L.append("- ★ `Remarks`：%s" % c["remarks"].replace("|", "/"))
        L.append("- ★ 示例：`%s`" % c["example"].replace("|", "/"))
    L.append("")
    if not st:
        L.append("★ **我们没真调用过** ⇒ 这条冲突对我们当前无直接影响 ✓")
        L.append("")
        continue
    for f, ln in st[:4]:
        text = (ROOT / f).read_text(encoding="utf-8", errors="replace").splitlines()
        win = "\n".join(text[max(0, ln - 12):ln + 12])
        verdict = ("★ 窗口内有带 mark 的选择" if HAS_MARK.search(win)
                   else ("★★ 窗口内只有 Select4（不带 mark）" if ONLY_SELECT4.search(win)
                         else "★ 窗口内看不出选择 API ⇒ unknown"))
        L.append("- 调用点 `%s:%d` ⇒ %s" % (f, ln, verdict))
    L.append("")

L += ["## 三 · ★ 下一步（★ 仍需人读官方页的那部分）", "",
      "★ 对每条：读该成员的官方 `## Remarks` ⇒ 判「它要求的 mark 是不是**必须**的」；",
      "★ 若必须、而我们窗口内没有 ⇒ ★ **这才是真缺陷**（★ 且要找真机证据才改）✓", ""]
out = ROOT / "docs" / "recon-206" / "mark-audit.md"
out.write_text("\n".join(L) + "\n", encoding="utf-8")
print("★ 写出 %s（%d 行）" % (out.name, len(L)))
for m in members:
    print("   %-30s 真调用 %d 处" % (m, len(sites_of(m))))
