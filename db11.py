import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
B = Path("D:\\Program Files\\SOLIDWORKS Corp\\JLCFA Parts Library Plugin "
         "Full Version v2.4.1-20260918-1\\ForFaceSelector\\ForFaceSelectorData\\DB")
con = sqlite3.connect("file:%s?mode=ro" % (B / "sw-fa-prod-selector"), uri=True)
c = con.cursor()

rel_keys = {r[0] for r in c.execute(
    "SELECT DISTINCT product_model_key_id "
    "FROM se_fa_product_model_third_party_relation WHERE delete_flag=0")}
print("  relation 的键 %d 个，样例 %s"
      % (len(rel_keys), sorted(rel_keys)[:5]))

pc_ids = {r[0] for r in c.execute("SELECT id FROM se_product_code")}
p_ids = {r[0] for r in c.execute("SELECT id FROM se_product")}
print("  se_product_code.id %d，se_product.id %d" % (len(pc_ids), len(p_ids)))
print("  relation 键 ∩ product_code.id =", len(rel_keys & pc_ids))
print("  relation 键 ∩ product.id      =", len(rel_keys & p_ids))
print("  relation 键全是数字串?",
      all(str(k).isdigit() for k in rel_keys if k is not None))

con.execute("ATTACH DATABASE ? AS builder", ("file:%s?mode=ro" % (B / "sw-fa-prod-builder"),))
bm = {r[0] for r in con.execute("SELECT id FROM builder.bu_model")}
print("  builder.bu_model.id %d" % len(bm))
print("  relation 键 ∩ bu_model.id =", len(rel_keys & bm))
print()
print("  ★ se_fa_product_code 里有没有指向模型的列：")
for r in c.execute("PRAGMA table_info(se_fa_product_code)"):
    print("      %-30s %s" % (r[1], r[2]))
