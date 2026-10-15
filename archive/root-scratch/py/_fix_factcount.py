"""★ 把 AGENTS.md §六 的「共 N 条」与速查行数，按产物重算。"""

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW")
facts = R / "docs" / "known-facts.md"
agents = R / "AGENTS.md"

#: ★ \u4e8b\u5b9e\u6761\u6570\uff1a`docs/known-facts.md` \u91cc\u5f62\u5982 `| 367 | ...` \u7684\u884c
ft = facts.read_text(encoding="utf-8")
nums = [int(m.group(1)) for m in re.finditer(r"^\|\s*(\d+)\s*\|", ft, re.M)]
total = max(nums) if nums else 0
print("  known-facts.md\uff1a\u5165\u5e93\u4e8b\u5b9e **%d** \u6761\uff08\u6700\u5927\u7f16\u53f7 %d\uff09" % (len(nums), total))

at = agents.read_text(encoding="utf-8")
#: \u2605 \u901f\u67e5\u8868\u884c\u6570\uff1a`### \u901f\u67e5` \u4e4b\u540e\u3001`| # |` \u8868\u5934\u4e0b\uff0c\u5230\u7a7a\u884c\u4e3a\u6b62\u7684 `| n |` \u884c
m = re.search(r"### \u901f\u67e5.*?\n\n(\| # \|.*?)\n\n", at, re.S)
rows = len(re.findall(r"^\|\s*\d+\s*\|", m.group(1), re.M)) if m else 0
print("  AGENTS.md \u901f\u67e5\u8868\uff1a**%d** \u884c" % rows)

n = 0
a = "**\u5171 63 \u6761**\uff0c\u5168\u6587\u5728"
b = "**\u5171 %d \u6761**\uff0c\u5168\u6587\u5728" % total
if a in at:
    at = at.replace(a, b, 1)
    n += 1
a2 = "\u672c\u8282\u53ea\u7559**\u6700\u5e38\u67e5\u7684 21 \u6761**\u505a\u901f\u67e5"
b2 = "\u672c\u8282\u53ea\u7559**\u6700\u5e38\u67e5\u7684 %d \u6761**\u505a\u901f\u67e5" % rows
if a2 in at:
    at = at.replace(a2, b2, 1)
    n += 1
a3 = "### \u901f\u67e5\uff08\u6700\u5e38\u67e5\u7684 21 \u6761\uff09"
b3 = "### \u901f\u67e5\uff08\u6700\u5e38\u67e5\u7684 %d \u6761\uff09" % rows
if a3 in at:
    at = at.replace(a3, b3, 1)
    n += 1
agents.write_text(at, encoding="utf-8")
raw = agents.read_bytes()
print("  \u6539\u4e86 %d \u5904 \u00b7 AGENTS.md \u73b0 **%d** \u5b57\u8282 / 65536\uff08%.1f%%\uff09\u00b7 \u4f59\u989d %d" % (
    n, len(raw), 100.0 * len(raw) / 65536, 65536 - len(raw)))
#: \u2605 \u56de\u8bfb\uff08\u4e8b\u5b9e 48 \u5b9a\u5219\u2461\uff09
chk = agents.read_text(encoding="utf-8")
print("  \u56de\u8bfb\uff1a\u542b\u300c\u5171 %d \u6761\u300d\uff1a%s \u00b7 \u542b\u300c21 \u6761\u300d\uff1a%s" % (
    total, ("\u5171 %d \u6761" % total) in chk, "21 \u6761" in chk))
