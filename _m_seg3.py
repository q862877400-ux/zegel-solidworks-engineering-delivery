import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

# ① \u4e8b\u5b9e\u8868
K = Path(r"D:\AI\SW\docs\known-facts.md")
body = Path(r"D:\AI\SW\_fact314.txt").read_text(encoding="utf-8").strip().replace("\n", " ")
tk = K.read_text(encoding="utf-8")
if "| 314 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + body + "\n", encoding="utf-8")
    print("(1) wrote 314")

# ② capabilities\uff08\u4e24\u6761\u5404\u81ea\u63a5\u4e0a\uff09
EV_Q = ("python \u771f\u673a\uff08\u8f6e 399\uff09\u2605 **PASS** \u2014\u2014 24h \u8ba1\u5212 v2 \u6bb5 3\uff1a"
        "`solidworks_current_sketch_name`\uff08\u8bfb\u5f53\u524d\u6d3b\u52a8\u8349\u56fe\u540d\uff09\u3002"
        "\u771f\u673a\uff08\u8d70 `sw_guard`\uff09\uff1a\u8349\u56fe\u6253\u5f00\u65f6\u56de **\u300c\u8349\u56fe1\u300d**\uff08**\u771f\u540d**\uff0c"
        "\u4e0d\u662f English fallback\uff09\uff1b\u8349\u56fe**\u5173\u95ed\u540e** + \u81ea\u5b9a\u4e49\u56de\u9000\u503c \u21d2 \u56de**\u90a3\u4e2a\u56de\u9000\u503c**\uff08\u2605 \u9a8c\u8bc1\u7684\u662f"
        "**\u5df2\u6587\u6863\u5316\u7684\u5c40\u9650**\uff1a\u2605 \u56de\u9000\u503c \u2260 \u771f\u540d \u21d2 \u522b\u62ff\u5b83\u53bb\u6309\u540d\u53d6\u8349\u56fe\uff09\u3002"
        "\u8bc1\u636e output/part-read-dimension-evidence.json\uff08`verdict: pass` 4/4\uff09\u3002"
        "\u2605 \u540c\u8f6e\u5206\u8bca\u8865\u4e86**\u7b2c\u56db/\u4e94\u5c42\u8bc1\u636e**\uff1a`*_report` \u5305\u88c5\u5df2\u66b4\u9732\u21d2\u4e0d\u662f\u7f3a\u53e3\uff08\u6b64\u524d\u628a "
        "`sw_selection_spec` \u7684 2 \u6761\u8bef\u5224\u4e3a\u7f3a\u53e3\uff09\uff1b**\u7a7a\u5b58\u6839**\uff08`pass`-only\uff09\u21d2\u4e0d\u505a\u3002")
EV_B = ("python \u771f\u673a\uff08\u8f6e 399\uff09\u2605 **PASS** \u2014\u2014 24h \u8ba1\u5212 v2 \u6bb5 3\uff1a"
        "`solidworks_auto_dimension_sketch`\uff08\u6309\u5b98\u65b9 `ISketch.AutoDimension2` \u7ed9\u5f53\u524d\u8349\u56fe\u5efa**\u771f\u5b9e\u6a21\u578b\u5c3a\u5bf8**\uff09\u3002"
        "\u771f\u673a\uff1a\u6709\u6d3b\u52a8\u8349\u56fe\u65f6 \u21d2 **status=pass \u00b7 status_code=0 \u00b7 selected=2**\uff1b"
        "\u8d1f\u4f8b\uff08**\u6ca1\u6709\u6d3b\u52a8\u8349\u56fe**\uff09\u21d2 **status=blocked \u00b7 error_code=SKETCH_NOT_ACTIVE**\u3002"
        "\u8bc1\u636e output/part-read-dimension-evidence.json\u3002"
        "\u2605 \u5b83\u5efa\u7684\u662f**\u771f\u5b9e\u7684 `DisplayDimension`**\uff08\u2605 \u53ef\u88ab\u5de5\u7a0b\u56fe\u5bfc\u5165\u590d\u6838\uff09\uff0c\u4e0d\u662f\u8349\u56fe\u91cc\u753b\u51e0\u6761\u7ebf\u3002")

c = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(c.read_text(encoding="utf-8"))
for cid, tool, ev_text in (("sketch_query", "solidworks_current_sketch_name", EV_Q),
                           ("sketch_build", "solidworks_auto_dimension_sketch", EV_B)):
    y = next((z for z in d["capabilities"] if z["id"] == cid), None)
    if y is None:
        print("(2) **\u672a\u627e\u5230 %s**" % cid)
        continue
    ts = list(y.get("mcp_tools") or [])
    if tool not in ts:
        ts.append(tool)
    y["mcp_tools"] = ts
    ev = list(y.get("evidence") or [])
    if not any(tool in s for s in ev):
        ev.insert(0, ev_text)
    y["evidence"] = ev
    print("(2) %-14s tools=%d ev=%d" % (cid, len(ts), len(ev)))
c.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
