import json, re
from pathlib import Path
data = json.loads(Path(r"D:\AI\SW\output\orphan-capabilities.json").read_text(encoding="utf-8"))
rows = data["orphans"]
IDENT = re.compile(r"^[A-Za-z_]\w*$")
bad = [r for r in rows if any(not IDENT.match(p) for p in r["params"]) if r["params"]]
print("rows with a non-identifier 'param' token:", len(bad), "/", len(rows))
for r in bad[:15]:
    print("   %-28s %-38s %r" % (r["module"], r["function"], r["params"]))
print("... total", len(bad))
