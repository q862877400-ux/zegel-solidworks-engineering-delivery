"""段位按 pattern 实际结构对齐（不用猜下标，直接看完整分段）。"""
import re
import sqlite3
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
B = Path("D:\\Program Files\\SOLIDWORKS Corp\\JLCFA Parts Library Plugin "
         "Full Version v2.4.1-20260918-1\\ForFaceSelector\\ForFaceSelectorData\\DB")
con = sqlite3.connect("file:%s?mode=ro" % (B / "sw-fa-prod-selector"), uri=True)
c = con.cursor()

pats = [r[0] for r in c.execute(
    "SELECT model_pattern FROM se_product_code_model_pattern "
    "WHERE model_pattern LIKE 'BFJA-C2E1-6-%'")]
print("  BFJA-C2E1-6 的 pattern 共 %d 条:" % len(pats))
for p in pats[:8]:
    print("     %-34s 分段=%s" % (p, re.split(r"(-)", p)))
print()

# 段位：把字母段和数字段分开统计
print("  ★ 同型号下，各位置段取值的种类数（判断哪些是枚举）")
cols = {}
for p in pats:
    for i, seg in enumerate(re.split(r"[-*]", p)):
        if not seg or seg == "None":
            continue
        cols.setdefault(i, set()).add(seg)
for i in sorted(cols):
    v = sorted(cols[i])
    kind = "枚举" if len(v) <= 12 else "自由(%d+)" % len(v)
    print("     第%d段  %-6s %-12s 例 %s" % (i, kind, len(v), v[:6]))
print()

print("  ★ se_product_code_attribute_value 的列名（上次 v.value 报错了）")
for r in c.execute("PRAGMA table_info(se_product_code_attribute_value)"):
    print("      %-32s %s" % (r[1], r[2]))
print()
print("  ★ se_serices_attribute 的列名")
for r in c.execute("PRAGMA table_info(se_serices_attribute)"):
    print("      %-32s %s" % (r[1], r[2]))
