import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(p.read_text(encoding="utf-8"))
ids = [x["id"] for x in d["capabilities"]]
print("  36 条能力里的「标准件 / Toolbox」条目：")
hit = [i for i in ids if any(k in i.lower() for k in ("toolbox", "standard", "fastener"))]
print("    %s" % (hit or "**没有**"))
blob = p.read_text(encoding="utf-8")
print("  capabilities.yaml 里 'toolbox' 出现: %d 次 · 'sw_toolbox' 出现: %d 次"
      % (blob.lower().count("toolbox"), blob.count("sw_toolbox")))
print()
print("  ⇒ 与轮 117 发现的 `sw_sketch` 是同一类：**有实现、有能力，但没有条目**")
