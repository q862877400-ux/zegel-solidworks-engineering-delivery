import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

K = Path(r"D:\AI\SW\docs\known-facts.md")
body = Path(r"D:\AI\SW\_fact316.txt").read_text(encoding="utf-8").strip().replace("\n", " ")
tk = K.read_text(encoding="utf-8")
if "| 316 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + body + "\n", encoding="utf-8")
    print("(1) wrote 316")

EV = ("python \u771f\u673a\uff08\u8f6e 401\uff09\u2605 **PASS 4/4** \u2014\u2014 24h \u8ba1\u5212 v2 \u6bb5 4\uff08\u5b54\u65cf\uff09\uff1a"
      "`solidworks_hole_pattern`\uff08`scripts/sw_hole_features.hole_pattern_report`\uff09\u3002"
      "\u5b83\u628a `create_hole_pattern` \u7684 **`creator` \u53ef\u8c03\u7528\u5bf9\u8c61**\u6362\u6210"
      "**\u5177\u540d\u7684 `kind`**\uff08\u2605 MCP \u5c42\u7ed9\u4e0d\u51fa\u51fd\u6570\uff09\u3002"
      "\u771f\u673a\uff08\u8d70 `sw_guard`\uff0c14.4 s \u65e0\u5f39\u7a97\uff09\uff1a**4 \u4e2a\u901a\u5b54 \u21d2 "
      "requested=4 \u00b7 holes=4 \u00b7 \u7279\u5f81\u6811 7 \u2192 15**\uff08`\u5b54_1`..`\u5b54_4`\uff0c\u6bcf\u4e2a\u5404\u5e26\u4e00\u5f20\u8349\u56fe\uff09\uff1b"
      "\u4e09\u6761\u8d1f\u4f8b\u5168\u90e8\u88ab\u62d2\uff08`kind=counterbore` \u00b7 `kind=blind` \u7f3a `depth_mm` \u00b7 "
      "\u7a7a\u5b54\u4f4d\u8868\uff09\u3002\u8bc1\u636e output/hole-pattern-evidence.json\u3002"
      "\u2605 \u540c\u65cf\u7684 `configure_straight_tap` / `configure_tapered_tap` **\u4e0d\u6302** \u2014\u2014 "
      "\u5b83\u4eec\u5403 `IStraightTapElementData` / `ITaperedTapElementData` **COM \u5143\u7d20**\uff0c"
      "\u2605 \u800c\u672c\u4ed3**\u6ca1\u6709\u8def\u5f84\u80fd\u4ece\u5b54\u7279\u5f81\u62ff\u5230\u90a3\u4e2a\u5143\u7d20**"
      "\uff08\u53ea\u5728 mock \u6d4b\u8bd5\u91cc\u51fa\u73b0\u8fc7\uff09\u21d2 \u6302\u51fa\u53bb\u5c31\u662f\u4e00\u4e2a\u6c38\u8fdc\u8c03\u4e0d\u901a\u7684\u6309\u94ae\u3002"
      "\u2605 \u5951\u7ea6\u6d4b\u8bd5 tests/test_sw_hole_pattern_contract.py\uff089 passed\uff09\u3002")

c = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(c.read_text(encoding="utf-8"))
y = next((z for z in d["capabilities"] if z["id"] == "holes_and_finishing"), None)
if y is None:
    print("(2) **\u672a\u627e\u5230 holes_and_finishing**")
else:
    ts = list(y.get("mcp_tools") or [])
    if "solidworks_hole_pattern" not in ts:
        ts.append("solidworks_hole_pattern")
    y["mcp_tools"] = ts
    ev = list(y.get("evidence") or [])
    if not any("hole_pattern" in s for s in ev):
        ev.insert(0, EV)
    y["evidence"] = ev
    LIM = ("\u26a0 2026-10-03\uff08\u8f6e 401\uff09\u2605 `solidworks_hole_pattern` **\u53ea\u652f\u6301 "
           "`through` / `blind`**\uff1a\u2605 `counterbore` / `countersink` \u53e6\u6709\u5fc5\u586b\u53c2\u6570\uff0c"
           "**\u672c\u5de5\u5177\u672a\u66b4\u9732**\uff08\u8c03\u4f1a\u88ab\u62d2\u5e76\u8bf4\u660e\uff09\u3002"
           "\u2605 \u53e6\uff1a\u540c\u65cf\u7684 `configure_straight_tap` / `configure_tapered_tap` **\u4e0d\u6302** \u2014\u2014 "
           "\u5b83\u4eec\u5403 **COM \u5143\u7d20\u5bf9\u8c61**\uff0c\u2605 \u800c\u672c\u4ed3**\u6ca1\u6709\u8def\u5f84\u80fd\u4ece\u5b54\u7279\u5f81\u62ff\u5230\u5b83**"
           "\uff08\u53ea\u5728 mock \u6d4b\u8bd5\u91cc\u51fa\u73b0\u8fc7\uff09\u21d2 MCP \u5c42\u7ed9\u4e0d\u51fa\u5b9e\u53c2\u3002")
    lim = list(y.get("limitations") or [])
    if not any("hole_pattern" in s by_ for by_ in [""]) and not any("只支持 `through`" in s for s in lim):
        lim.insert(0, LIM)
    y["limitations"] = lim
    c.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("(2) holes_and_finishing tools=%d ev=%d lim=%d" % (len(ts), len(ev), len(lim)))
