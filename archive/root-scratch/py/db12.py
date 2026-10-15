import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"C:\swprojects\sw-skill-fork\scripts\jlcfa_index.json")
d = json.loads(p.read_text(encoding="utf-8"))
print("  型号总数:", len(d["parts"]))
for kw in ("铝型材", "电磁阀", "导轨", "工业铝型材"):
    n_code = sum(1 for x in d["parts"] if kw in x["code"])
    n_prod = sum(1 for x in d["parts"] if kw in x["product"])
    n_name = sum(1 for x in d["parts"] if kw in x["name"])
    print("  %-10s code=%-6d name=%-6d product=%-6d" % (kw, n_code, n_name, n_prod))
print()
print("  ★ 样例：product 字段长什么样")
for x in d["parts"][:3]:
    print("    code=%-26s product=%s" % (x["code"], x["product"][:50]))
print()
print("  ★ 型号 → 分类的连接丢了？索引里没有 category 字段")
print("    字段:", list(d["parts"][0].keys()))
print()
print("  ★ 型号与分类的关系在 se_category_product（8207 行）里")
print("    那是 product 级，型号挂在 product 下 ⇒ 分类可经 product 推出")
