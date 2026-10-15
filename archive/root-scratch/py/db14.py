import re
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
B = Path("D:\\Program Files\\SOLIDWORKS Corp\\JLCFA Parts Library Plugin "
         "Full Version v2.4.1-20260918-1\\ForFaceSelector\\ForFaceSelectorData\\DB")
con = sqlite3.connect("file:%s?mode=ro" % (B / "sw-fa-prod-selector"), uri=True)
c = con.cursor()

print("  ★ DAL.dll 里出现过的 SQL 片段拼出的表/列:")
for t in ("se_product_code_model_pattern", "se_segment", "se_product_attribute_value"):
    try:
        print("  ===", t)
        for r in c.execute("PRAGMA table_info([%s])" % t):
            print("      %-32s %s" % (r[1], r[2]))
        print()
    except Exception as e:
        print("   ", e)

print("  ★ se_product_code_model_pattern 样例:")
for r in c.execute("SELECT * FROM se_product_code_model_pattern LIMIT 3"):
    print("     ", [str(x)[:30] for x in r][:10])
