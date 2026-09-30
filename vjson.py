"""验 se_product_code_attribute_value.values_json 是否含完整可选值。"""
import json
import re
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
B = Path("D:\\Program Files\\SOLIDWORKS Corp\\JLCFA Parts Library Plugin "
         "Full Version v2.4.1-20260918-1\\ForFaceSelector\\ForFaceSelectorData\\DB")
con = sqlite3.connect("file:%s?mode=ro" % (B / "sw-fa-prod-selector"), uri=True)
c = con.cursor()

print("  ★ 样本：随便 3 行 values_json")
for r in c.execute("SELECT id, pattern_id, values_json "
                   "FROM se_product_code_attribute_value LIMIT 3"):
    print("    id=%s" % r[0])
    print("    pattern_id=%s" % r[1])
    print("    values_json=%s" % (r[2] or "")[:220])
    try:
        j = json.loads(r[2])
        print("    -> 可解析 JSON，类型=%s，键/元素=%s"
              % (type(j).__name__, list(j)[:8] if isinstance(j, dict) else j[:4]))
    except Exception as e:
        print("    -> 不是 JSON: %s" % str(e)[:50])
    print()

print("  ★ BFJA-C2E1-6 的全部属性值（经 pattern_id 关联）")
n = c.execute("""
  SELECT COUNT(*) FROM se_product_code_attribute_value v
  JOIN se_product_code_model_pattern m ON m.id = v.pattern_id
  JOIN se_product_code pc ON pc.id = m.product_code_id
  WHERE pc.code_name = 'BFJA-C2E1-6'""").fetchone()[0]
print("    命中 %d 行" % n)
for r in c.execute("""
  SELECT v.values_json FROM se_product_code_attribute_value v
  JOIN se_product_code_model_pattern m ON m.id = v.pattern_id
  JOIN se_product_code pc ON pc.id = m.product_code_id
  WHERE pc.code_name = 'BFJA-C2E1-6' LIMIT 6"""):
    try:
        j = json.loads(r[0])
        keys = list(j)[:10] if isinstance(j, dict) else j[:4]
        print("      %s" % str(keys)[:160])
    except Exception as e:
        print("      原样: %s  (%s)" % ((r[0] or "")[:90], str(e)[:30]))
