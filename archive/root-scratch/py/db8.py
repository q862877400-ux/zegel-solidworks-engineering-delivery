import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
D = Path(r"D:\Program Files\SOLIDWORKS Corp\JLCFA Parts Library Plugin "
         r"Full Version v2.4.1-20260918-1\ForFaceSelector\ForFaceSelectorData\DB")
con = sqlite3.connect("file:%s?mode=ro" % (D / "sw-fa-prod-selector"), uri=True)
c = con.cursor()

tabs = [r[0] for r in c.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
print("  找含 '1195749' 的表:")
for t in tabs:
    cols = [r[1] for r in c.execute("PRAGMA table_info([%s])" % t)]
    for col in cols:
        try:
            n = c.execute("SELECT COUNT(*) FROM [%s] WHERE CAST([%s] AS TEXT)='1195749'"
                          % (t, col)).fetchone()[0]
        except Exception:
            continue
        if n:
            print("    ★ %s.%s  命中 %d" % (t, col, n))
print()
print("  se_product_code.id 的样例（雪花）:", 
      [r[0] for r in c.execute("SELECT id FROM se_product_code LIMIT 3")])
print("  se_product.id 的样例:",
      [r[0] for r in c.execute("SELECT id FROM se_product LIMIT 3")])
