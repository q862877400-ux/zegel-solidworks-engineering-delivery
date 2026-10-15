import json, sys, io
sys.path.insert(0, r"D:\AI\SW\tools")
from build_union_map import _our_operations, DOMAIN_LABELS
d = json.load(open(r"D:\AI\SW\tools\union-sources.json", encoding="utf-8"))
sources = d["sources"]
ours = _our_operations()
dom = "other"
cells = {s["repo"]: set(s["domains"].get(dom, [])) for s in sources}
cells["本仓库"] = {op for op, dd in ours.items() if dd == dom}
u = set()
for v in cells.values(): u |= v
gap = sorted(u - cells["本仓库"])
ext_union = set()
for s in sources: ext_union |= set(s["domains"].get(dom, []))
exclusive = []
for op in sorted(u):
    owners = [k for k, v in cells.items() if op in v]
    if len(owners) == 1 and owners[0] != "本仓库":
        exclusive.append((op, owners[0]))
o = io.StringIO()
o.write("DOMAIN %s (%s)\n" % (dom, DOMAIN_LABELS[dom]))
for k, v in cells.items(): o.write("  cell %-36s %d\n" % (k, len(v)))
o.write("  external_union=%d  u=%d  our_cell=%d\n" % (len(ext_union), len(u), len(cells["本仓库"])))
o.write("  gap(u-ours)=%d   exclusive=%d\n" % (len(gap), len(exclusive)))
o.write("\n=== GAP %d (op | owners | in_our_MCP) ===\n" % len(gap))
for op in gap:
    ow = [k.split("/")[0] for k, v in cells.items() if op in v]
    o.write("%-32s | %-42s | ourMCP=%s\n" % (op, ",".join(ow), op in cells["本仓库"]))
o.write("\n=== EXCLUSIVE %d (op | sole owner) ===\n" % len(exclusive))
for op, owner in exclusive:
    o.write("%-32s | %s | in_gap=%s\n" % (op, owner, op in gap))
from collections import Counter
o.write("\n=== exclusive owner histogram ===\n%s\n" % Counter(x[1].split("/")[0] for x in exclusive))
o.write("\n=== ALL %d our 'other'-domain MCP ops ===\n%s\n" % (len(cells["本仓库"]), sorted(cells["本仓库"])))
open(r"D:\AI\SW\_probe_dom17.txt","w",encoding="utf-8").write(o.getvalue())
print("written")
