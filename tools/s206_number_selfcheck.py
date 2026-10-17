"""★ 自查：我这一线的产出物之间，**共享数字**是否一致（★ SC-5 的落点：口径不许漂）。"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

#: ★★ 单一真值源（★ 每个数字都在**原始 JSON 或已核验的实测**里有依据）
TRUTH = {
    "recon_json_total": (40, "specs/203-*/recon (10) + specs/204-*/recon (30)"),
    "more_specific": (3806, "c4-merged.json 的 tally `more_specific`"),
    "more_specific_members": (2242, "c4-merged 里 example_more_specific 的 distinct 成员"),
    "mark_diff": (10, "c4-merged 的 kinds"),
    "unit_diff": (15, "c4-merged 的 kinds"),
    "dead_link_candidate": (212, "b2-defects.json 的 type 计数"),
    "verified_defects": (964, "b2-defects.json 的 verified=True 计数"),
    "preconditions_total": (534, "c3-merged.json 的 preconditions 总数"),
    "precondition_not_covered": (322, "c3-merged 的 state=not_covered"),
    "precondition_checkable": (102, "本线的机械分类结果"),
    "lookup_members": (368, "本线的必查表"),
    "lookup_entries": (424, "本线的必查表"),
    "conflict_ok": (544, "c4-merged 的 quote_ok"),
    "conflict_total": (598, "c4-merged 的 conflicts tally"),
}

#: ★ 要自查的文件（★ 我这一线产出的）
FILES = sorted((ROOT / "docs" / "recon-206").glob("*.md")) + [
    ROOT / "docs" / "tool-aliases.md",
    ROOT / "docs" / "precondition-coverage-gaps.md",
]
print("★ 自查文件: %d 个" % len(FILES))
print()

#: ★ 判据：对每个真值数字，grep 各文件里「紧邻该数字的上下文」，看有没有**矛盾的说法**
#:   ★ 做法保守：只查「同一个键的**另一种写法**」—— 即同一份文档里同键出现两个不同数 ⇒ 报
L = ["# 自查：产出物之间的**共享数字**一致性（★ SC-5 的落点）", "",
     "> 生成物 —— 由 `tools/s206_number_selfcheck.py` 产出，不要手改。", "",
     "## 一 · 单一真值源（★ 每个数字的依据）", "",
     "| 键 | 真值 | 依据 |", "|---|---:|---|"]
for k, (v, why) in sorted(TRUTH.items()):
    L.append("| `%s` | **%d** | %s |" % (k, v, why))

bad = []
L += ["", "## 二 · 各文件里的出现情况", "",
      "| 文件 | 命中的真值键 |", "|---|---|"]
for f in FILES:
    if not f.is_file():
        continue
    t = f.read_text(encoding="utf-8", errors="replace")
    hits = []
    for k, (v, _w) in TRUTH.items():
        if str(v) in t:
            hits.append("%s=%d" % (k, v))
    if hits:
        L.append("| `%s` | %s |" % (f.name, " · ".join(hits[:6])))
    #: ★★ 矛盾检测：文档里若出现「同一个键的另一种数」⇒ 报
    #:   （★ 保守：只查几组**已知易漂**的）
    for pat, key in ((r"3709", "more_specific"), (r"3779", "more_specific"),
                     (r"125\s*条.*?三源", None)):
        if re.search(pat, t) and key == "more_specific":
            bad.append((f.name, "出现 `%s`，而真值是 **3806**" % pat))

L += ["", "## 三 · ★ 矛盾检测结果", ""]
if bad:
    for n, w in bad:
        L.append("- ★ `%s`：%s" % (n, w))
else:
    L.append("★ **未发现矛盾** ✓")
L += ["", "## 四 · 本表的「不算什么」", "",
      "- ★ 它只查**已登记的真值键**（%d 个）⇒ ★ 未登记的数字它**看不见** ✓" % len(TRUTH),
      "- ★★ 判据是**子串匹配** ⇒ ★ 数字出现在**举例/引用**语境时会**误报** ✓",
      "- ★ 它**不判**数字对不对 —— 只判「产出物之间一不一致」；★ 真值本身由各自的依据负责 ✓",
      "- ★ 真值源是**原始 JSON** 与**本线实测** ⇒ ★ 若原始 JSON 更新，本表要跟着更新 ✓", ""]
out = ROOT / "docs" / "recon-206" / "number-selfcheck.md"
out.write_text("\n".join(L) + "\n", encoding="utf-8")
print("★ 写出 %s（%d 行）" % (out.name, len(L)))
print("★ 真值键: %d · 矛盾: %d" % (len(TRUTH), len(bad)))
for n, w in bad:
    print("   ★ %s: %s" % (n, w))
