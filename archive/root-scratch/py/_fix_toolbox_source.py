import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
Q = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(Q.read_text(encoding="utf-8"))
n = 0
for c in d["capabilities"]:
    if c.get("id") == "standard_parts_toolbox":
        #: ⚠ 门禁「R12 · 清单形状」当场抓到：`source` 必须取自枚举
        #: ⇒ 本条目是**我们自己写的**（照本机 Toolbox 目录生成索引）⇒ 正确值是 `original`
        c["source"] = "original"
        n += 1
        print("  ok source 已改成 'original'（枚举内的值）")
Q.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("  改了 %d 处" % n)
