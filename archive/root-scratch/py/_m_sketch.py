import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

# ① \u4e8b\u5b9e\u8868
K = Path(r"D:\AI\SW\docs\known-facts.md")
body = Path(r"D:\AI\SW\_fact313.txt").read_text(encoding="utf-8").strip().replace("\n", " ")
tk = K.read_text(encoding="utf-8")
print("(1) " + ("wrote 313" if "| 313 |" not in tk else "already"))
if "| 313 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + body + "\n", encoding="utf-8")

# ② capabilities\uff1a\u627e\u5230\u8349\u56fe\u65cf\u90a3\u6761\uff0c\u52a0 5 \u4e2a\u5de5\u5177 + evidence
EV = ("python \u771f\u673a\uff08\u8f6e 398\uff09\u2605 **PASS** \u2014\u2014 24h \u8ba1\u5212 v2 \u6bb5 2\u300c\u8349\u56fe\u56fe\u5143\u300d"
      "5 \u4e2a\u5de5\u5177\uff08`mcp-server/tool_specs_batch54.py`\uff09\uff1a`solidworks_sketch_add_arc` \u00b7 "
      "`solidworks_sketch_add_ellipse` \u00b7 `solidworks_sketch_add_polygon` \u00b7 "
      "`solidworks_sketch_add_slot` \u00b7 `solidworks_sketch_add_centerline`\u3002"
      "\u771f\u673a\uff08\u8d70 `sw_guard`\uff09\u5224\u636e\u662f**\u6bb5\u6570**\uff08\u72ec\u7acb\u4e8e\u8fd4\u56de\u503c \u2014\u2014 "
      "`CreateArc` \u90a3\u4e9b\u56de COM \u5bf9\u8c61\u800c\u201c\u56de\u5bf9\u8c61\u201d\u2260\u201c\u56fe\u5f62\u5728\u201d\uff09\uff1a"
      "arc [0\u21921] \u00b7 ellipse [0\u21921] \u00b7 polygon [0\u21927] \u00b7 slot [0\u21925] \u00b7 centerline [0\u21921]\uff1b"
      "\u8d1f\u4f8b\uff08**\u4e0d\u5b58\u5728\u7684\u8349\u56fe\u540d**\uff09\u21d2 **\u629b RuntimeError**\u3002"
      "\u8bc1\u636e output/sketch-primitives-evidence.json\u3002"
      "\u2605\u2605 \u540c\u8f6e\u6293\u5230\u4e24\u4e2a\u771f bug\uff1a\u2460 `sw_sketch.resolve_sketch` \u5bf9**\u975e\u7a7a\u4f46\u627e\u4e0d\u5230**"
      "\u7684\u540d\u5b57**\u9759\u9ed8\u56de\u9000**\u5230\u300c\u7279\u5f81\u6811\u91cc\u6700\u540e\u4e00\u4e2a\u8349\u56fe\u300d"
      "\uff08\u4f1a\u8ba9\u8c03\u7528\u65b9\u5728**\u53e6\u4e00\u4e2a\u8349\u56fe**\u4e0a\u8bfb/\u5199\uff09\u2014\u2014 \u5df2\u4fee\uff08\u515c\u5e95\u53ea\u5bf9\u7a7a\u540d\u5b57\u6210\u7acb\uff09\uff1b"
      "\u2461 \u672c\u6279 5 \u6761 ToolSpec **\u6f0f\u4e86 `inject=\\\"model\\\"`**\uff08\u4f1a\u8ba9\u5de5\u5177\u62ff\u4e0d\u5230\u6587\u6863\u5bf9\u8c61\u3001"
      "\u4e00\u8c03\u5c31 TypeError\uff09\u2014\u2014 **\u5951\u7ea6\u6d4b\u8bd5\u5f53\u573a\u6293\u5230**\uff0c\u5df2\u8865\u3002")

NEW_TOOLS = ["solidworks_sketch_add_arc", "solidworks_sketch_add_ellipse",
             "solidworks_sketch_add_polygon", "solidworks_sketch_add_slot",
             "solidworks_sketch_add_centerline"]
c = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(c.read_text(encoding="utf-8"))
x = None
for y in d["capabilities"]:
    if "solidworks_sketch_add_line" in (y.get("mcp_tools") or []):
        x = y
        break
if x is None:
    print("(2) **\u672a\u627e\u5230\u8349\u56fe\u65cf\u6761\u76ee**")
else:
    tools = list(x.get("mcp_tools") or [])
    for t in NEW_TOOLS:
        if t not in tools:
            tools.append(t)
    x["mcp_tools"] = tools
    ev = list(x.get("evidence") or [])
    if not any("PASS" in s and "sketch_add_arc" in s for s in ev):
        ev.insert(0, EV)
    x["evidence"] = ev
    lim = list(x.get("limitations") or [])
    LIM = ("\u26a0 2026-10-03\uff08\u8f6e 398\uff09\u2605 `sketch_spline` **\u4e0d\u505a**\uff08\u672a\u6302\u6210\u5de5\u5177\uff09\uff1a"
           "\u4f9d\u636e\u662f\u8f6e 141 \u771f\u673a\u7ed3\u8bba \u2014\u2014 `CreateSpline2` \u8fd4\u56de None\u3001\u91cd\u7ed8\u540e\u4ecd 0 \u6bb5\u3001"
           "\u65e7\u7248 `CreateSpline` \u5728\u8fdf\u5230\u7ed1\u5b9a\u91cc\u4e0d\u5b58\u5728\uff1b\u800c\u540e\u7ee7 `CreateSpline3` \u672b\u53c2\u662f "
           "**BYREF `Object&`** \u21d2 \u4e8b\u5b9e 47/68 \u67b6\u6784\u9650\u5236\u3002"
           "\u2605 \u53e6\uff1a`polygon` \u5b9e\u6d4b\u7ed9 **7** \u6bb5\u3001`slot` \u7ed9 **5** \u6bb5\uff08\u2605 \u6bd4\u51e0\u4f55\u76f4\u89c9\u591a\uff0c"
           "\u591a\u51fa\u7684\u90a3\u51e0\u6bb5**\u672a\u67e5**\uff09\uff1b\u8fb9\u6570 < 3 \u65f6\u5b9e\u6d4b\u4ecd\u4f1a\u5efa\u51fa 4 \u6bb5\uff08\u2605 \u5b98\u65b9\u4e0b\u9650\u672a\u67e5\u5230\uff0c"
           "\u4e0d\u81c6\u65ad\uff09\u3002")
    if not any("sketch_spline" in s for s in lim):
        lim.insert(0, LIM)
    x["limitations"] = lim
    c.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("(2) %s tools=%d ev=%d lim=%d" % (x["id"], len(tools), len(ev), len(lim)))
