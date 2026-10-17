"""★ T4-1 逐条核（机械部分）：25 条冲突涉及的成员，我们的代码用没用到、用在哪。"""
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
members = sorted({cap.get("member") for cap in rows
                  for c in (cap.get("conflicts") or [])
                  if str(c.get("kind")) in WANT and cap.get("member")})
print("★ 25 条冲突涉及 %d 个成员" % len(members))

SRC = []
for d in ("scripts", "mcp-server", "tools"):
    SRC += sorted((ROOT / d).rglob("*.py"))

hit_at: dict = defaultdict(list)
for f in SRC:
    try:
        text = f.read_text(encoding="utf-8", errors="replace")
    except Exception:                                              # noqa: BLE001
        continue
    for m in members:
        for pat, what in ((r'get_com_member\([^,]+,\s*"%s"' % re.escape(m), "get_com_member"),
                          (r'\.%s\b' % re.escape(m), "attr_access"),
                          (r'"%s"' % re.escape(m), "literal")):
            hit = None
            for mm in re.finditer(pat, text):
                hit = (str(f.relative_to(ROOT)), text[:mm.start()].count("\n") + 1, what)
                break
            if hit:
                hit_at[m].append(hit)
                break

used = [m for m in members if hit_at.get(m)]
unused = [m for m in members if not hit_at.get(m)]
print("★★ 我们用了的成员: %d" % len(used))
print("★★ 我们没用到的成员: %d" % len(unused))
print()
for m in used:
    f0, l0, w0 = hit_at[m][0]
    print("   %-32s %s:%d (%s) 共 %d 处" % (m, f0, l0, w0, len(hit_at[m])))
print()
print("★ 没用到的: " + ", ".join(unused))

L = [
    "# T4-1 逐条核（机械部分）：25 条冲突的成员，我们用了没、用在哪",
    "",
    "> 生成物 —— 由 tools/t4_member_crosscheck.py 产出，不要手改。",
    "> 输入：c4-merged.json（只读复用）+ 本仓 scripts/ mcp-server/ tools/。",
    "",
    "## 一 · 口径",
    "",
    "| 项 | 值 |",
    "|---|---|",
    "| 冲突条目 | **25**（unit_diff 15 + mark_diff 10）|",
    "| 涉及成员 | **%d** |" % len(members),
    "| ★ 我们用了的成员 | **%d** |" % len(used),
    "| ★ 我们没用到的成员 | **%d** |" % len(unused),
    "",
    "本表不算什么：",
    "",
    "- ★ 不判我们调得对不对 —— 它只说用没用、用在哪（判对错要读那一行代码加官方页）；",
    "- ★ 没用到的成员不等于无影响 —— 若将来实现同一能力，该冲突届时才触发；",
    "- ★ 匹配有三种写法（get_com_member / 属性访问 / 字符串字面量），",
    "  第三种会把注释与文档里的提及也算进来，可能高估用了没。",
    "",
    "## 二 · 我们用了的（%d 个，需要人核的那批）" % len(used),
    "",
    "| 成员 | 引用处 | 方式 |",
    "|---|---|---|",
]
for m in used:
    for f, l, w in hit_at[m][:6]:
        L.append("| `%s` | `%s:%d` | %s |" % (m, f, l, w))
L += ["", "## 三 · 我们没用到的（%d 个）" % len(unused), ""]
for m in unused:
    L.append("- `%s`" % m)
L += ["", "## 四 · 下一步", "",
      "★ 对第二节那 %d 个成员逐条：读我们那一行代码加官方页 Remarks，"
      "判我们用的是示例写法还是 Remarks 写法；有证据的才改。" % len(used)]
out = ROOT / "docs" / "recon-206" / "conflicts-25-crosscheck.md"
out.write_text("\n".join(L) + "\n", encoding="utf-8")
print()
print("★ 写出 %s（%d 行）" % (out.name, len(L)))
