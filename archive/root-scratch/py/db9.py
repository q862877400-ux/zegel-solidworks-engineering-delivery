import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
D = Path(r"D:\Program Files\SOLIDWORKS Corp\JLCFA Parts Library Plugin "
         r"Full Version v2.4.1-20260918-1\ForFaceSelector\ForFaceSelectorData\DB")
con = sqlite3.connect("file:%s?mode=ro" % (D / "sw-fa-prod-builder"), uri=True)
c = con.cursor()
tabs = [r[0] for r in c.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
print("  sw-fa-prod-builder 表数:", len(tabs))
for t in tabs:
    try:
        n = c.execute("SELECT COUNT(*) FROM [%s]" % t).fetchone()[0]
    except Exception:
        n = "?"
    print("    %-42s %s" % (t, n))
print()
for t in tabs:
    try:
        cols = [r[1] for r in c.execute("PRAGMA table_info([%s])" % t)]
    except Exception:
        continue
    if not any("model" in x.lower() for x in cols):
        continue
    print("  === %s" % t)
    for r in c.execute("PRAGMA table_info([%s])" % t):
        print("      %-36s %s" % (r[1], r[2]))
    try:
        for row in c.execute("SELECT * FROM [%s] LIMIT 2" % t):
            print("      样例:", [str(x)[:26] for x in row][:8])
    except Exception as e:
        print("      读样例失败:", str(e)[:50])
    print()
