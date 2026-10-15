import re, io, sys
from pathlib import Path
sys.path.insert(0, r"D:\AI\SW\tools")
from build_union_sources import _normalize, _domain
SRC = Path(r"C:\swprojects\SolidworksMCP-TS\src")
tools = []
for p in sorted(SRC.rglob("*.ts")):
    if "__tests__" in str(p) or p.name.endswith(".test.ts"): continue
    t = p.read_text(encoding="utf-8", errors="ignore")
    for m in re.finditer(r"name:\s*'([a-zA-Z0-9_]+)'", t):
        tools.append((m.group(1), p.name))
o = io.StringIO()
o.write("total tool-name literals found: %d\n" % len(tools))
targets = {"advanced_features","api_automation","custom_prop","error_handling","operations",
           "pdm_operations","security","security_info","update_sheet_format","view_grayscale_enhanced"}
o.write("\n=== tools whose normalized op is in domain 'other' (10) ===\n")
for name, f in tools:
    op = _normalize(name)
    if op in targets:
        o.write("%-40s -> %-26s  domain=%s  file=%s\n" % (name, op, _domain(op), f))
o.write("\n=== vespo92 'other' domain as recorded in union-sources.json ===\n")
import json
d = json.load(open(r"D:\AI\SW\tools\union-sources.json", encoding="utf-8"))
for s in d["sources"]:
    if "vespo92" in s["repo"]:
        for op in s["domains"]["other"]:
            o.write("  %s\n" % op)
o.write("\n=== all 103 vespo92 tools (name -> op -> domain) ===\n")
seen=set()
for name, f in sorted(set(tools)):
    seen.add(name)
for name in sorted(seen):
    o.write("%-44s -> %-28s %s\n" % (name, _normalize(name), _domain(_normalize(name))))
open(r"D:\AI\SW\_probe_vespo.txt","w",encoding="utf-8").write(o.getvalue())
print("ok, literals=%d unique=%d" % (len(tools), len(seen)))
