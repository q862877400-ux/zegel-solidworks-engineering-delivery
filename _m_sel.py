import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

# ① \u4e8b\u5b9e\u8868
K = Path(r"D:\AI\SW\docs\known-facts.md")
body = Path(r"D:\AI\SW\_fact312.txt").read_text(encoding="utf-8").strip().replace("\n", " ")
tk = K.read_text(encoding="utf-8")
if "| 312 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + body + "\n", encoding="utf-8")
    print("(1) wrote 312")
else:
    print("(1) already")

# ② capabilities\uff1aselection_helpers + 6 \u4e2a\u5de5\u5177 + evidence
EV = Path(r"D:\AI\SW\_sel_ev.txt").read_text(encoding="utf-8").strip()
NEW_TOOLS = ["solidworks_selection_count", "solidworks_select_entity_by_index",
             "solidworks_resolve_selection", "solidworks_selection_point",
             "solidworks_select_by_selector", "solidworks_resolve_entity"]
c = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(c.read_text(encoding="utf-8"))
x = next(y for y in d["capabilities"] if y["id"] == "selection_helpers")
tools = list(x.get("mcp_tools") or [])
for t in NEW_TOOLS:
    if t not in tools:
        tools.append(t)
x["mcp_tools"] = tools
ev = list(x.get("evidence") or [])
if not any("PASS 9/9" in s for s in ev):
    ev.insert(0, EV)
x["evidence"] = ev
LIM = ("\u26a0 2026-10-03\uff08\u8f6e 397\uff09\u771f\u673a\u8bed\u4e49\uff1a`selection_point` \u8bfb\u7684\u662f"
       "**\u9009\u62e9\u65f6\u9f20\u6807\u843d\u5728\u300c\u9762\u300d\u4e0a\u7684\u4f4d\u7f6e** \u2014\u2014 "
       "\u2605 \u9009\u4e2d **VERTEX** \u65f6 `GetSelectionPoint2` \u7684 **6 \u79cd (Index, Mark) \u7ec4\u5408\u5168\u90e8\u56de None**"
       "\uff08\u2605 \u4e0d\u662f bug\uff0c\u662f\u8bed\u4e49\uff1a\u9876\u70b9\u6ca1\u6709\u9762\u53ef\u6295\u5f71\uff09\uff1b"
       "\u2605 \u800c\u5b83**\u4e0d\u62a5\u9519\u3001\u53ea\u56de None** \u21d2 \u7528\u4e4b\u524d\u8981\u770b `ok`\u3002"
       "\u2605 \u53e6\uff1a`GetSelectionPoint(AtIndex)` \u662f **1 \u53c2**\u3001`GetSelectionPoint2(Index, Mark)` \u662f **2 \u53c2**"
       "\uff08\u2605 \u5148\u524d\u4e24\u4e2a\u90fd\u4f20 `(1, -1)` \u662f\u4e2a\u771f bug\uff0c\u5df2\u4fee \u2014\u2014 \u4e8b\u5b9e 312\uff09\u3002")
lim = list(x.get("limitations") or [])
if not any("selection_point" in t and "鼠标落在" in t for t in lim):
    lim.insert(0, LIM)
x["limitations"] = lim
c.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("(2) selection_helpers tools=%d ev=%d lim=%d level=%s" % (len(tools), len(ev), len(lim), x.get("level")))
