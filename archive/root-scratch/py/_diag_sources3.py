import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
d = json.load(open(r"C:\swprojects\sw-skill-fork\tools\union-sources.json", encoding="utf-8"))
print("  schema_version=%s · union_size=%s" % (d["schema_version"], d["union_size"]))
print()
tot = 0
for s in d["sources"]:
    tools = s.get("tools") or []
    tot += len(tools)
    print("    %-36s %-11s %4d 个工具名" % (s.get("repo"), s.get("license"), len(tools)))
    print("         declared_verified = %r" % s.get("declared_verified"))
    print("         字段: %s" % sorted(s.keys()))
print("  ── 相加 %d（有重名）· 去重后 union_size = %d" % (tot, d["union_size"]))
