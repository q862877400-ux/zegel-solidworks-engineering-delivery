import json
import sys
from collections import Counter
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

d = json.loads(Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml").read_text(encoding="utf-8"))
caps = d["capabilities"]
lv = Counter(c.get("level") for c in caps)
print("  能力 %d 条 · level: %s" % (len(caps), dict(lv)))

# NOTICE 的断言：source_verified 条目数 = 0
sv = [c["id"] for c in caps if c.get("level") == "source_verified"]
print("  `source_verified` 条目: %d %s" % (len(sv), sv))

# 有没有别的条目带 provenance？
withprov = [c["id"] for c in caps if c.get("provenance")]
print("  带 `provenance` 字段的条目: %d %s" % (len(withprov), withprov[:8]))

# source / source_evidence 里提到外部 owner/repo 的
import re
OWNERS = ("Eduardof0nt", "andrewbartels1", "vespo92", "Slacker-LLC", "wzyn20051216", "microsoft/UFO")
hits = {}
for c in caps:
    blob = json.dumps(c, ensure_ascii=False)
    for o in OWNERS:
        if o in blob:
            hits.setdefault(o, []).append(c["id"])
print()
print("  哪些外部来源被**能力条目**提到（按 owner 分组）:")
for o, ids in hits.items():
    print("    %-22s %d 条: %s" % (o, len(ids), ids[:5]))
if not hits:
    print("    （没有任何能力条目提到外部 owner）")
