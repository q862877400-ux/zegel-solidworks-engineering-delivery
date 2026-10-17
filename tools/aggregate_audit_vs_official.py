"""★ 批量抽 bunny 那 30 路对比稿的**结构与计数**，找规律（★ 业主指令：等对比稿到齐后批量总结）。"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(Path(__file__).resolve().parents[1])
D = REPO / "specs" / "202-user-coverage-gaps" / "recon" / "audit-vs-official"

rows = []
for f in sorted(D.glob("audit-*.md")):
    t = f.read_text(encoding="utf-8", errors="replace")
    L = t.splitlines()
    #: ★ 文件名 → 域 / 核对面
    m = re.match(r"audit-(\d+)-([a-z0-9\-]+)-([ABC])\.md", f.name)
    dom, chk = (m.group(2), m.group(3)) if m else ("?", "?")
    #: ★ 结尾三行：都核了几处 / 报了几条 / 高置信几条
    def _num(pat):
        mm = re.search(pat, t)
        return int(mm.group(1)) if mm else None
    checked = _num(r"都核了\s*\**(\d+)\**\s*处")
    reported = _num(r"报了\s*\**(\d+)\**\s*条")
    #: ★ 分歧表的行数（以 `| 数字 |` 开头的行）
    table_rows = len([l for l in L if re.match(r"\|\s*\d+\s*\|", l)])
    #: ★ 「查不到」段的条数
    try:
        i0 = next(i for i, l in enumerate(L) if l.startswith("## 查不到"))
        i1 = next((i for i, l in enumerate(L) if i > i0 and l.startswith("## ")), len(L))
        notfound = len([l for l in L[i0:i1] if l.strip().startswith(("-", "*"))])
    except StopIteration:
        notfound = 0
    rows.append({"file": f.name, "domain": dom, "check": chk,
                 "checked": checked, "reported": reported,
                 "table_rows": table_rows, "notfound": notfound})

print("★ bunny 对比稿：**%d** 片（★ 应到 30 + 1 合并）" % len(rows))
print()
print("%-30s %-6s %-6s %-8s %-8s %-8s %s" % ("文件", "域", "面", "核了几处", "表行数", "查不到", "占比"))
print("-" * 108)
tot_c = tot_r = tot_nf = 0
for r in rows:
    c = r["checked"] or 0
    rep = r["table_rows"]
    tot_c += c
    tot_r += rep
    tot_nf += r["notfound"]
    pct = ("%.0f%%" % (100.0 * rep / c)) if c else "—"
    print("%-30s %-6s %-6s %-8s %-8s %-8s %s" % (r["file"][:29], r["domain"][:5], r["check"],
                                                 c, rep, r["notfound"], pct))
print("-" * 108)
print("★ 合计：核了 **%d** 处 · 分歧 **%d** 条 · 查不到 **%d** 段 ⇒ ★ **分歧率 %.1f%%**"
      % (tot_c, tot_r, tot_nf, (100.0 * tot_r / tot_c) if tot_c else 0.0))
print()
#: ★ 按核对面聚合
bychk: dict = {}
for r in rows:
    k = r["check"]
    a = bychk.setdefault(k, {"files": 0, "checked": 0, "rows": 0})
    a["files"] += 1
    a["checked"] += r["checked"] or 0
    a["rows"] += r["table_rows"]
print("★ 按核对面：")
for k in sorted(bychk):
    a = bychk[k]
    pct = (100.0 * a["rows"] / a["checked"]) if a["checked"] else 0.0
    print("   %s：%d 片 · 核 %d 处 · 分歧 %d 条 ⇒ **%.1f%%**" % (k, a["files"], a["checked"], a["rows"], pct))
