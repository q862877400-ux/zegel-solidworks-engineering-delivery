import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
d = json.loads(Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml").read_text(encoding="utf-8"))
for cid in ("topology_optimization",):
    for c in d["capabilities"]:
        if c.get("id") != cid:
            continue
        print("══ %s（%s）" % (cid, c.get("label")))
        print("   level = **%s**" % c.get("level"))
        print("   backends = %s" % c.get("backends"))
        print("   verified_versions = %s" % c.get("verified_versions"))
        print("   evidence (%d 条):" % len(c.get("evidence") or []))
        for s in (c.get("evidence") or []):
            print("      · %s" % str(s)[:170])
        print("   limitations (%d 条):" % len(c.get("limitations") or []))
        for i, s in enumerate((c.get("limitations") or [])[:5], 1):
            print("      %d) %s" % (i, str(s)[:190]))
print()
print("  ── 全仓库拓扑相关的脚本/测试/工具 ──")
R = Path(r"C:\swprojects\sw-skill-fork")
for pat in ("scripts/sw_topology*.py", "tools/*topolog*", "tests/*topolog*", "mcp-server/*topolog*"):
    for f in sorted(R.glob(pat)):
        print("    %-46s %d 行" % (f.name, f.read_text(encoding='utf-8').count(chr(10))))
