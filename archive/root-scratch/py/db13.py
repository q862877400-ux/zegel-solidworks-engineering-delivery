import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
B = Path("D:\\Program Files\\SOLIDWORKS Corp\\JLCFA Parts Library Plugin "
         "Full Version v2.4.1-20260918-1\\ForFaceSelector\\ForFaceSelectorData\\DB")
con = sqlite3.connect("file:%s?mode=ro" % (B / "sw-fa-prod-selector"), uri=True)
c = con.cursor()
print("  se_category_product 列:")
for r in c.execute("PRAGMA table_info(se_category_product)"):
    print("      %-28s %s" % (r[1], r[2]))
print()
print("  样例:")
for r in c.execute("SELECT * FROM se_category_product LIMIT 3"):
    print("     ", r)
