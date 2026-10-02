import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

LIM = ("\u26a0 2026-10-03\uff08\u8f6e 407\uff09**`export_flat_pattern_dxf` \u5728\u672c\u8ba1\u5212\u7684\u7ea2\u7ebf\u5185\u9a8c\u4e0d\u4e86**"
       "\uff08\u2605 \u56e0\u6b64**\u4ecd\u4e0d\u6ce8\u518c**\uff09\u3002\u2605\u2605 \u771f\u524d\u7f6e\u4e0d\u662f\u300c\u94a3\u91d1\u4ef6\u300d\u800c\u662f"
       "\u300c**\u5df2\u4fdd\u5b58**\u7684\u94a3\u91d1\u4ef6\u300d\u2014\u2014 \u8f6e 407 **\u771f\u9020\u4e86\u4e00\u4e2a\u94a3\u91d1\u4ef6**"
       "\uff08\u56de\u8bfb `has_base_flange` / `has_sheet_metal_feature` / `all_solid_bodies_are_sheet_metal` **\u4e09\u9879\u5168 true**\uff09"
       "\u800c `ExportToDWG2` **\u4ecd\u62d2\u7edd**\uff1a`ValueError: \u5bfc\u51fa\u5c55\u5f00 DXF \u524d\u5fc5\u987b\u5148\u4fdd\u5b58\u94a3\u91d1\u96f6\u4ef6`\u3002"
       "\u2605 \u800c**\u4fdd\u5b58\u662f\u786c\u7ea6\u675f\u2466 \u660e\u7981**\u7684\u9ad8\u98ce\u9669\u5199\u64cd\u4f5c \u21d2 \u2605\u2605 **\u4e0d\u7ed5\u3001\u4e0d\u8c41\u514d\u3001"
       "\u4e0d\u5077\u5077\u4fdd\u5b58**\uff1b\u2605 \u5305\u88c5\u4e0e\u63a2\u9488\u4fdd\u7559\uff0c\u2605 \u7f3a\u7684\u662f\u90a3\u4e00\u6761**\u6b63\u4f8b**"
       "\uff08\u4e8b\u5b9e 322\uff09\u3002")

c = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(c.read_text(encoding="utf-8"))
y = None
for z in d["capabilities"]:
    ts = z.get("mcp_tools") or []
    if any("export_step" in t for t in ts):
        y = z
        break
if y is None:
    print("**\u672a\u627e\u5230\u5bfc\u51fa\u6761\u76ee**")
else:
    lim = list(y.get("limitations") or [])
    if not any("export_flat_pattern_dxf" in s and "\u9a8c\u4e0d\u4e86" in s for s in lim):
        lim.insert(0, LIM)
    y["limitations"] = lim
    c.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("%s lim=%d" % (y["id"], len(lim)))
