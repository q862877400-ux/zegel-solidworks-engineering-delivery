import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
D = Path(r"D:\Program Files\SOLIDWORKS Corp\JLCFA Parts Library Plugin "
         r"Full Version v2.4.1-20260918-1\ForFaceSelector\ForFaceSelectorData\DB")
con = sqlite3.connect("file:%s?mode=ro" % (D / "sw-fa-prod-selector"), uri=True)
c = con.cursor()

print("  se_product_code.status 分布:",
      list(c.execute("SELECT status, COUNT(*) FROM se_product_code GROUP BY status")))
print("  is_3d 分布:",
      list(c.execute("SELECT is_3d, COUNT(*) FROM se_product_code GROUP BY is_3d")))
print()
print("  型号表样例（前 5 行 code_name / product_id）:")
for r in c.execute("SELECT id, code_name, product_id, status, is_3d "
                   "FROM se_product_code LIMIT 5"):
    print("    ", r)
print()
print("  ★ relation 表的 product_model_key_id 样例:")
for r in c.execute("SELECT product_model_key_id, third_party_model, delete_flag "
                   "FROM se_fa_product_model_third_party_relation LIMIT 5"):
    print("    ", r)
print()
print("  ★ 两个键的交集（这是 join 能不能通的关键）:")
n = c.execute("""
  SELECT COUNT(*) FROM se_fa_product_model_third_party_relation m
  JOIN se_product_code pc ON pc.id = m.product_model_key_id
  WHERE m.delete_flag = 0""").fetchone()[0]
print("     relation JOIN product_code 命中:", n)
print()
print("  ★ relation 的 delete_flag 分布:",
      list(c.execute("SELECT delete_flag, COUNT(*) "
                     "FROM se_fa_product_model_third_party_relation "
                     "GROUP BY delete_flag LIMIT 5")))
