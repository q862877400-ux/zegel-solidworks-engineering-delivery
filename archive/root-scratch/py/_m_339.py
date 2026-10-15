import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

W = Path(r"D:\AI\SW")
K = W / "docs" / "known-facts.md"
body = (W / "_fact339.txt").read_text(encoding="utf-8").strip().replace("\n", " ")
tk = K.read_text(encoding="utf-8")
print("(1) " + ("wrote 339" if "| 339 |" not in tk else "already"))
if "| 339 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + body + "\n", encoding="utf-8")

EV = ("python \u771f\u673a\uff08\u8f6e 425\uff09\u2605 **PASS** \u2014\u2014 \u521a\u6027\u8fde\u63a5\u4ef6\uff08B \u7ec4\u7b2c\u4e00\u6761\uff09\u3002"
      "\u771f\u673a\uff08\u8d70 `sw_guard`\uff0c6.4 s \u65e0\u5f39\u7a97\uff09\uff1a\u53cc\u4f53\u96f6\u4ef6\u4e0a"
      "\u2605 **\u8ba1\u6570 0\u21921**\uff08\u5224\u636e\uff1a\u56de\u8bfb\u8ba1\u6570**\u6070\u597d +1**\uff09\u3002"
      "\u8bc1\u636e output/rigid-twobody-evidence.json\u3002"
      "\u2605\u2605 \u800c\u5b83\u4e00\u6b21\u8bc1\u5b9e\u4e86\u524d\u9762**\u4e24\u6761**\u94fe\u4e0a\u7684\u5047\u8bbe\uff1a"
      "\u2460 \u5d29\u7684\u771f\u56e0\u662f\u300c**\u8bfb\u9009\u533a\u53ea\u62ff\u5f97\u5230\u7b2c 1 \u4e2a\u5b9e\u4f53**\u300d"
      "\uff08\u4e8b\u5b9e 336/337\uff1a`GetSelectedObject6`/`4`/`5`/`GetSelectedObjectsFace` **\u4e94\u4e2a\u5165\u53e3\u90fd\u8bd5\u8fc7**\uff0c"
      "\u800c `Count2(-1)` \u5982\u5b9e\u62a5 2\uff09\u21d2 \u6362\u6210\u300c**\u6309\u5df2\u77e5\u5b9e\u4f53\u6e05\u5355\u88c5\u6570\u7ec4**\u300d\uff08\u4e0d\u8bfb\u9009\u533a\uff09\u540e**\u4e0d\u518d\u5d29**\uff1b"
      "\u2461 \u5b83**\u8981\u4e24\u4e2a\u4f53**\uff08\u4e8b\u5b9e 338\uff1a\u540c\u65cf\u5f62\u53c2\u540d\u5199\u7740 `Comp1`/`Comp2`\uff09"
      "\u2014\u2014 \u5355\u4f53\u96f6\u4ef6\u4e0a\u5b83**\u6210\u529f\u8fd4\u56de\u5374\u4e0d\u5efa**\uff08\u8ba1\u6570 0\u21920\u3001\u65e0\u9519\u8bef\uff09\uff0c\u90a3\u662f**\u5e94\u7136\u7684**\u3002"
      "\u2605\u2605 \u56e0\u6b64\u672c\u5de5\u5177**\u4e0d\u8bfb\u9009\u533a**\uff0c\u800c\u662f\u81ea\u5df1\u6309**\u5e8f\u53f7**\u628a\u4e24\u7ec4\u5b9e\u4f53\u88c5\u597d\uff0c"
      "\u4e14**\u4e24\u4fa7\u4f53\u53f7\u53ef\u5206\u522b\u6307\u5b9a**\u3002")

LIM = ("\u26a0 2026-10-03\uff08\u8f6e 425\uff09\u2605\u2605 **\u8fde\u63a5\u4ef6\u4e00\u65cf\u6709\u4e24\u6761\u786c\u524d\u63d0**\uff0c\u9010\u6761\u8bb0\uff1a"
       "\u2460 **\u5b83\u4eec\u8981\u4e24\u4e2a\u4e1c\u897f**\uff08\u540c\u65cf\u5f62\u53c2\u540d `Comp1`/`Comp2`\uff09"
       "\u2014\u2014 \u5355\u4f53\u4e0a\u4f1a**\u6210\u529f\u8fd4\u56de\u800c\u4e0d\u5efa**\uff08\u8ba1\u6570\u4e0d\u6da8\u3001\u4e5f\u4e0d\u62a5\u9519\uff09\uff1b"
       "\u2461 **\u4e0d\u8981\u4ece\u9009\u533a\u8bfb\u591a\u5b9e\u4f53**\uff08\u4e8b\u5b9e 336/337\uff1a`ISelectionMgr` \u4e0a\u201c\u6309\u5e8f\u53f7\u53d6\u5bf9\u8c61\u201d\u90a3\u4e00\u65cf"
       "\u53ea\u56de\u5f97\u5230\u7b2c 1 \u4e2a\uff0c\u800c `Count2(-1)` \u5982\u5b9e\u62a5\u6570\uff09"
       "\u2014\u2014 \u8bf7\u7528\u672c\u5de5\u5177\uff08\u5b83\u6309**\u5e8f\u53f7**\u81ea\u5df1\u88c5\u6570\u7ec4\uff09\u3002"
       "\u2605 \u540c\u65cf\u5c1a\u672a\u6ce8\u518c\u7684\uff1a`AddPinConnector` / `AddSpringConnector` / `AddBoltConnector` / "
       "`AddSpotWeldConnector` / `AddEdgeWeldConnector` \u2014\u2014 \u2605 \u5b83\u4eec\u8981\u7684\u662f**\u4e24\u4e2a\u96f6\u4ef6**\uff08\u88c5\u914d\u4f53\uff09\uff0c\u5c1a\u672a\u9a8c\u3002")

c = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(c.read_text(encoding="utf-8"))
y = None
for z in d["capabilities"]:
    if "solidworks_simulation_apply_pressure" in (z.get("mcp_tools") or []):
        y = z
        break
if y is None:
    print("(2) **\u672a\u627e\u5230\u4eff\u771f\u8f7d\u8377\u6761\u76ee**")
else:
    ts = list(y.get("mcp_tools") or [])
    if "solidworks_simulation_apply_rigid_connector" not in ts:
        ts.append("solidworks_simulation_apply_rigid_connector")
    y["mcp_tools"] = ts
    ev = list(y.get("evidence") or [])
    if not any("B \u7ec4\u7b2c\u4e00\u6761" in s for s in ev):
        ev.insert(0, EV)
    y["evidence"] = ev
    lim = list(y.get("limitations") or [])
    if not any("\u8fde\u63a5\u4ef6\u4e00\u65cf\u6709\u4e24\u6761\u786c\u524d\u63d0" in s for s in lim):
        lim.insert(0, LIM)
    y["limitations"] = lim
    c.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("(2) %s tools=%d ev=%d lim=%d" % (y["id"], len(ts), len(ev), len(lim)))
