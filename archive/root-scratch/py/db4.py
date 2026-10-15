import sqlite3, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
D = Path(r"D:\Program Files\SOLIDWORKS Corp\JLCFA Parts Library Plugin Full Version v2.4.1-20260918-1\ForFaceSelector\ForFaceSelectorData\DB")
con = sqlite3.connect("file:%s?mode=ro" % (D/"sw-fa-prod-selector"), uri=True)
cur = con.cursor()
tabs = [r[0] for r in cur.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
print("  表数:", len(tabs))
for t in tabs:
    try:
        n = cur.execute("SELECT COUNT(*) FROM [%s]" % t).fetchone()[0]
    except Exception as e:
        n = "?"
    print("    %-38s %s" % (t, n))