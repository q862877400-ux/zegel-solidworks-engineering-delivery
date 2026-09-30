"""验第 3 条：pattern(BFJA-C2E1-6-D4-L*) 能否直接展开出实际文件名。"""
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
B = Path("D:\\Program Files\\SOLIDWORKS Corp\\JLCFA Parts Library Plugin "
         "Full Version v2.4.1-20260918-1\\ForFaceSelector\\ForFaceSelectorData\\DB")
con = sqlite3.connect("file:%s?mode=ro" % (B / "sw-fa-prod-selector"), uri=True)
c = con.cursor()

print("  BFJA-C2E1-6 的全部 pattern:")
rows = list(c.execute("""
  SELECT m.model_pattern FROM se_product_code pc
  JOIN se_product_code_model_pattern m ON m.product_code_id = pc.id
  WHERE pc.code_name = 'BFJA-C2E1-6'"""))
for r in rows:
    print("     ", r[0])
print()

print("  ★ 参数值表里有没有 L200 / D4？")
for kw in ("L200", "D4"):
    n = c.execute("SELECT COUNT(*) FROM se_fa_product_param_value "
                  "WHERE CAST(value AS TEXT) LIKE ?", ("%" + kw + "%",)).fetchone()[0]
    print("     value 含 %-5s -> %d 条" % (kw, n))

print()
print("  ★ se_fa_product_param / _value 的列:")
for t in ("se_fa_product_param", "se_fa_product_param_value"):
    print("    ===", t)
    for r in c.execute("PRAGMA table_info([%s])" % t):
        print("        %-30s %s" % (r[1], r[2]))

print()
print("  ★ 属性表里 BFJA-C2E1-6 的参数（D4 / L 段对应哪个属性）:")
for r in c.execute("""
  SELECT a.name, v.value
  FROM se_product_code pc
  JOIN se_product_code_attribute_value v ON v.product_code_id = pc.id
  LEFT JOIN se_serices_attribute a ON a.id = v.serices_attribute_id
  WHERE pc.code_name = 'BFJA-C2E1-6' LIMIT 15"""):
    print("        %-28s %s" % (r[0], r[1]))
