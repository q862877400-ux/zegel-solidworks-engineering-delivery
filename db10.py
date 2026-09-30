import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
B = Path("D:\\Program Files\\SOLIDWORKS Corp\\JLCFA Parts Library Plugin "
         "Full Version v2.4.1-20260918-1\\ForFaceSelector\\ForFaceSelectorData\\DB")
con = sqlite3.connect("file:%s?mode=ro" % (B / "sw-fa-prod-selector"), uri=True)
con.execute("ATTACH DATABASE ? AS builder", ("file:%s?mode=ro" % (B / "sw-fa-prod-builder"),))
c = con.cursor()
print("  bu_model.id 样例     :", [r[0] for r in c.execute("SELECT id FROM builder.bu_model LIMIT 4")])
print("  relation 键样例      :", [r[0] for r in c.execute(
    "SELECT DISTINCT product_model_key_id FROM se_fa_product_model_third_party_relation LIMIT 4")])
print("  se_product_code.id  :", [r[0] for r in c.execute("SELECT id FROM se_product_code LIMIT 3")])
print("  se_product.id       :", [r[0] for r in c.execute("SELECT id FROM se_product LIMIT 3")])
print()
for a, b, label in (
    ("se_product_code", "id", "product_code.id"),
    ("se_product", "id", "product.id"),
):
    n = c.execute("""SELECT COUNT(*) FROM se_fa_product_model_third_party_relation r
                     JOIN %s t ON CAST(t.%s AS TEXT)=CAST(r.product_model_key_id AS TEXT)
                     WHERE r.delete_flag=0""" % (a, b)).fetchone()[0]
    print("  relation ⋈ %-24s 命中 %d" % (label, n))
n = c.execute("""SELECT COUNT(*) FROM se_fa_product_model_third_party_relation r
                 JOIN builder.bu_model m ON m.id = r.product_model_key_id
                 WHERE r.delete_flag=0 AND r.third_party_model<>'空白'""").fetchone()[0]
print("  relation ⋈ builder.bu_model.id 命中", n)
print()
print("  ★ relation 表里到底有没有能对上型号的键？列全列一遍:")
for r in c.execute("PRAGMA table_info(se_fa_product_model_third_party_relation)"):
    print("      %-36s %s" % (r[1], r[2]))
