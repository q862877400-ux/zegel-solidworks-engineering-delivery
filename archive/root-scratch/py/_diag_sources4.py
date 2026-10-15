import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
d = json.load(open(r"C:\swprojects\sw-skill-fork\tools\union-sources.json", encoding="utf-8"))
for s in d["sources"]:
    print("── %s (%s) · tool_count=%s · operation_count=%s" %
          (s["repo"], s["license"], s.get("tool_count"), s.get("operation_count")))
    print("   note: %s" % str(s.get("note"))[:400])
    doms = s.get("domains")
    if isinstance(doms, dict):
        print("   domains(%d): %s" % (len(doms), list(doms.items())[:6]))
    elif isinstance(doms, list):
        print("   domains(%d): %s" % (len(doms), doms[:8]))
    print()
