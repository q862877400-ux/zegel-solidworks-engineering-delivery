import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
D = Path(r"D:\Program Files\SOLIDWORKS Corp\JLCFA Parts Library Plugin "
         r"Full Version v2.4.1-20260918-1\ForFaceSelector\ForFaceSelectorData\DB")
con = sqlite3.connect("file:%s?mode=ro" % (D / "sw-fa-prod-selector"), uri=True)
c = con.cursor()
for t in ("se_product", "se_product_code", "se_fa_product_serial",
          "se_fa_product_code", "se_category_product", "se_category",
          "se_product_brand"):
    print("  ===", t)
    for r in c.execute("PRAGMA table_info([%s])" % t):
        print("      %-34s %s" % (r[1], r[2]))
    print()
