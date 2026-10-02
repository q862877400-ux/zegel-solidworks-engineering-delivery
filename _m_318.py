import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

K = Path(r"D:\AI\SW\docs\known-facts.md")
body = Path(r"D:\AI\SW\_fact318.txt").read_text(encoding="utf-8").strip().replace("\n", " ")
tk = K.read_text(encoding="utf-8")
print("(1) " + ("wrote 318" if "| 318 |" not in tk else "already"))
if "| 318 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + body + "\n", encoding="utf-8")

EV = ("python \u771f\u673a\uff08\u8f6e 403\uff09\u2605 **PASS** \u2014\u2014 24h \u8ba1\u5212 v2 \u6bb5 6\uff08\u5bfc\u51fa\uff09\uff1a"
      "`solidworks_export_image`\uff08`sw_export.export_image_report`\uff09\u3002"
      "\u771f\u673a\uff08\u8d70 `sw_guard`\uff0c4.0 s \u65e0\u5f39\u7a97\uff09\uff1a\u4e00\u5f20 PNG \u21d2 **`exists=true` \u00b7 "
      "`size_bytes=67997` \u00b7 `grew_or_created=true`**\uff1b\u8d1f\u4f8b\uff08\u975e\u6cd5\u76ee\u5f55\uff09\u21d2 `ok=false`\u3002"
      "\u2605 \u5224\u636e**\u590d\u7528\u672c\u6a21\u5757\u65e2\u6709\u7684 `_export_report`**\uff08\u56de\u8bfb\u6587\u4ef6\uff1a\u5b58\u5728\u4e14 size>0\uff0c"
      "\u5e76\u8bb0 `size_before` / `grew_or_created`\uff09\u2014\u2014 \u4e0d\u53e6\u9020\u4e00\u5957\u3002"
      "\u8bc1\u636e output/export-two-evidence.json\u3002"
      "\u2605\u2605 \u540c\u8f6e\u771f\u673a\u6293\u5230\u4e00\u4e2a\u771f bug \u5e76\u4fee\u6389\uff1a`export_to_image` \u91cc\u7528\u4e86 `out_i4()`\uff08\u6807\u91cf\u51fa\u53c2\u5305\u88c5\uff09"
      "\u800c\u672c\u6a21\u5757**\u6f0f\u4e86\u5bfc\u5165** \u21d2 \u4e00\u8c03\u5c31 `NameError`\uff08\u2605 **\u800c\u8fd9\u6b63\u662f\u5b83\u4e00\u76f4\u6ca1\u88ab\u6302\u7684\u539f\u56e0**\uff09\u3002")

c = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(c.read_text(encoding="utf-8"))
y = None
for z in d["capabilities"]:
    ts = z.get("mcp_tools") or []
    if any("export_step" in t for t in ts):
        y = z
        break
if y is None:
    print("(2) **\u672a\u627e\u5230\u5bfc\u51fa\u6761\u76ee**")
else:
    ts = list(y.get("mcp_tools") or [])
    if "solidworks_export_image" not in ts:
        ts.append("solidworks_export_image")
    y["mcp_tools"] = ts
    ev = list(y.get("evidence") or [])
    if not any("export_image" in s for s in ev):
        ev.insert(0, EV)
    y["evidence"] = ev
    lim = list(y.get("limitations") or [])
    LIM = ("\u26a0 2026-10-03\uff08\u8f6e 403\uff09\u2605 `solidworks_export_image` **\u5c3a\u5bf8\u4e0d\u53ef\u6307\u5b9a**"
           "\uff08`SaveAs3` \u6ca1\u6709\u5c3a\u5bf8\u5165\u53c2\uff09\u21d2 \u6309**\u5f53\u524d\u89c6\u56fe**\uff1b"
           "\u2605 \u8981\u6307\u5b9a\u50cf\u7d20\u5c3a\u5bf8\u8bf7\u7528 `solidworks_export_bmp`\u3002"
           "\u2605 \u53e6\uff1a`export_flat_pattern_dxf` **\u672c\u6279\u672a\u6ce8\u518c** \u2014\u2014 \u5b83\u7684\u524d\u7f6e\u662f**\u94a3\u91d1\u4ef6**\uff0c"
           "\u800c\u975e\u94a3\u91d1\u4ef6\u4e0a\u771f\u673a\u5f97\u5230\u7684\u662f**\u6b63\u786e\u7684\u663e\u5f0f\u62d2\u7edd**"
           "\uff08`ValueError: \u5bfc\u51fa\u5c55\u5f00 DXF \u524d\u5fc5\u987b\u5148\u4fdd\u5b58\u94a3\u91d1\u96f6\u4ef6`\uff09\u21d2 \u6309\u786c\u7ea6\u675f\u2465 \u56de\u9000\uff0c"
           "\u2605 \u5305\u88c5\u4e0e\u63a2\u9488\u4fdd\u7559\u3002")
    if not any("export_flat_pattern_dxf" in s and "\u672c\u6279\u672a\u6ce8\u518c" in s for s in lim):
        lim.insert(0, LIM)
    y["limitations"] = lim
    c.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("(2) %s tools=%d ev=%d lim=%d" % (y["id"], len(ts), len(ev), len(lim)))
