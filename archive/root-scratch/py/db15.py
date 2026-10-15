import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
B = Path("D:\\Program Files\\SOLIDWORKS Corp\\JLCFA Parts Library Plugin "
         "Full Version v2.4.1-20260918-1\\ForFaceSelector\\ForFaceSelectorData\\DB")
con = sqlite3.connect("file:%s?mode=ro" % (B / "sw-fa-prod-selector"), uri=True)
c = con.cursor()

n = c.execute("""SELECT COUNT(*) FROM se_product_code_model_pattern m
                 JOIN se_product_code pc ON pc.id = m.product_code_id""").fetchone()[0]
tot = c.execute("SELECT COUNT(*) FROM se_product_code_model_pattern").fetchone()[0]
print("  pattern 总行 %d，与型号表对上的 %d" % (tot, n))
print()
print("  ★ 完整链：型号 -> pattern -> relation -> 模型包名")
rows = c.execute("""
  SELECT pc.code_name, m.model_pattern, r.third_party_model
  FROM se_product_code pc
  JOIN se_product_code_model_pattern m ON m.product_code_id = pc.id
  LEFT JOIN se_fa_product_model_third_party_relation r
         ON r.product_model_key_id = m.product_code_id AND r.delete_flag = 0
  AND r.third_party_model IS NOT NULL AND r.third_party_model <> '空白'
  LIMIT 6""").fetchall()
for r in rows:
    print("     %-26s %-32s %s" % (r[0][:26], r[1][:32], r[2]))
print()
c2 = c.execute("""
  SELECT COUNT(*) FROM se_product_code pc
  JOIN se_product_code_model_pattern m ON m.product_code_id = pc.id""").fetchone()[0]
print("  有 pattern 的型号:", c2)
print("  3D 型号标记分布:", list(
    c.execute("SELECT is_3d, COUNT(*) FROM se_product_code_model_pattern GROUP BY is_3d")))
print()
print("  ★ se_segment_source（32 万行，可能是型号↔文件清单）")
for r in c.execute("PRAGMA table_info(se_segment_source)"):
    print("      %-30s %s" % (r[1], r[2]))
