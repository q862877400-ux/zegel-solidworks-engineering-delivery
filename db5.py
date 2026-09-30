import sqlite3, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
D = Path(r"D:\Program Files\SOLIDWORKS Corp\JLCFA Parts Library Plugin Full Version v2.4.1-20260918-1\ForFaceSelector\ForFaceSelectorData\DB")
con = sqlite3.connect("file:%s?mode=ro" % (D/"sw-fa-prod-selector"), uri=True)
c = con.cursor()
def cols(t):
    return [(r[1], r[2]) for r in c.execute("PRAGMA table_info([%s])" % t)]
print("  === se_fa_product_model_third_party_relation 列结构")
for n, t in cols("se_fa_product_model_third_party_relation"): print("     %-34s %s" % (n, t))
print()
print("  === se_category 前 12 行（找丝杆/导轨/型材）")
for r in c.execute("SELECT * FROM se_category LIMIT 3"):
    print("    ", [str(x)[:28] for x in r][:6])
print()
print("  === 分类名里含关键词的")
for kw in ("丝杆", "导轨", "型材", "直线", "光轴", "轴承"):
    n = c.execute("SELECT COUNT(*) FROM se_category WHERE CAST(name AS TEXT) LIKE ?", ("%"+kw+"%",)).fetchone()[0]
    print("     %-6s %d 个分类" % (kw, n))