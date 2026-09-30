import re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
doc = Path(r"C:\swprojects\sw-skill-fork\docs\family-coverage.json").read_text(encoding="utf-8")
import json
d = json.loads(doc)
row = next(r for r in d if r["family"] == "ISketchEllipse")
hit = set(row.get("hit_members") or [])
print("ISketchEllipse 成员总数 =", row["members"], " 命中 =", row["hit"])
# 从 sw_api_sldworks.py 里取该族全部登记名
src = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_api_sldworks.py").read_text(encoding="utf-8")
m = re.search(r"'ISketchEllipse': \{\n(.*?)\n    \},", src, re.S)
names = re.findall(r"'(\w+)':", m.group(1)) if m else []
print("索引里登记了 =", len(names))
print("登记名:", names[:8])
# 覆盖表统计的成员名来自哪里？
print()
print("family_members 取自:", "C:\\swapi\\types\\ISketchEllipse" if Path(r"C:\swapi\types\ISketchEllipse").is_dir() else "反射")
