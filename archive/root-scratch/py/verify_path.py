import importlib.util
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sp = importlib.util.spec_from_file_location(
    "j", r"C:\swprojects\sw-skill-fork\scripts\sw_jlcfa_index.py")
m = importlib.util.module_from_spec(sp)
sys.modules["j"] = m
sp.loader.exec_module(m)

CODE = "BFJA-C2E1-6-D4-L200"
hits = m.search(CODE)
print("  在我的 63,234 型号索引里查 %s -> %d 条" % (CODE, len(hits)))
for h in hits[:3]:
    print("     ", h)

# 型号主体（去掉参数段）
base = "BFJA-C2E1"
h2 = m.search(base)
print()
print("  只用型号主体 %s -> %d 条" % (base, len(h2)))
for h in h2[:3]:
    print("     ", h)

# 数据库侧：pattern 长什么样
B = Path("D:\\Program Files\\SOLIDWORKS Corp\\JLCFA Parts Library Plugin "
         "Full Version v2.4.1-20260918-1\\ForFaceSelector\\ForFaceSelectorData\\DB")
con = sqlite3.connect("file:%s?mode=ro" % (B / "sw-fa-prod-selector"), uri=True)
c = con.cursor()
print()
print("  数据库里这个型号的 pattern:")
for r in c.execute("""
  SELECT pc.code_name, pc.code_show_name, m.model_pattern
  FROM se_product_code pc
  JOIN se_product_code_model_pattern m ON m.product_code_id = pc.id
  WHERE pc.code_name LIKE 'BFJA-C2E1%' LIMIT 4"""):
    print("     %-22s %-30s %s" % (r[0][:22], (r[1] or "")[:30], r[2]))
