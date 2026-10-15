import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
raw = json.load(open(r"C:\swprojects\sw-skill-fork\tools\union-sources.json", encoding="utf-8"))
print("  顶层类型: %s" % type(raw).__name__)
if isinstance(raw, list):
    print("  元素类型: %s" % {type(x).__name__ for x in raw})
    for x in raw:
        print("    %r" % (x if not isinstance(x, (list, dict)) else str(x)[:80]))
elif isinstance(raw, dict):
    print("  键: %s" % list(raw.keys())[:10])
    for k, v in list(raw.items())[:6]:
        print("    %-24s %s" % (k, str(v)[:90]))
