"""看 pattern 各段的性质：哪些是枚举（有限可选）、哪些是自由输入。"""
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

print("  ★ pattern 的段长分布（第 N 段取值的字符长度）")
seg_len = Counter()
n = 0
for (pat,) in c.execute("SELECT model_pattern FROM se_product_code_model_pattern "
                        "WHERE model_pattern IS NOT NULL LIMIT 200000"):
    n += 1
    for seg in re.split(r"[-*]", pat):
        if seg and seg != "None":
            seg_len[(len(seg), seg.isdigit())] += 1
print("    样本 %d 条 pattern" % n)
for (L, isnum), cnt in seg_len.most_common(10):
    print("      长度=%d 全数字=%-5s %6d 次" % (L, isnum, cnt))

print()
print("  ★ BFJA-C2E1-6 各段的可选值（D 和 L 各有多少种）")
for tag, pat in (("D", "BFJA-C2E1-6-D%"), ("L", "BFJA-C2E1-6-D4-L%")):
    vals = Counter()
    for (p,) in c.execute("SELECT model_pattern FROM se_product_code_model_pattern "
                          "WHERE model_pattern LIKE ?", (pat,)):
        segs = re.split(r"[-*]", p)
        idx = 1 if tag == "D" else 2
        if len(segs) > idx and segs[idx]:
            vals[segs[idx]] += 1
    print("      %s 段: %d 种  例 %s" % (tag, len(vals), list(vals)[:10]))

print()
print("  ★ 参数可选值表里 BFJA-C2E1-6 有什么")
for r in c.execute("""
  SELECT a.name, v.value
  FROM se_product_code pc
  JOIN se_product_code_attribute_value v ON v.product_code_id = pc.id
  LEFT JOIN se_serices_attribute a ON a.id = v.serices_attribute_id
  WHERE pc.code_name = 'BFJA-C2E1-6' LIMIT 20"""):
    print("      %-26s %s" % (r[0], r[1]))
