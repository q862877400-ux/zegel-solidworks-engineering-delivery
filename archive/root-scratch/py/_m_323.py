import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

W = Path(r"D:\AI\SW")
K = W / "docs" / "known-facts.md"
body = (W / "_fact323.txt").read_text(encoding="utf-8").strip().replace("\n", " ")
tk = K.read_text(encoding="utf-8")
print("(1) " + ("wrote 323" if "| 323 |" not in tk else "already"))
if "| 323 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + body + "\n", encoding="utf-8")

EV = ("python \u771f\u673a\uff08\u8f6e 408\uff09\u2605 **PASS** \u2014\u2014 24h \u8ba1\u5212 v2 \u6bb5 5\uff08\u4eff\u771f\u8f7d\u8377\u65cf\uff09\uff1a"
      "**4 \u6761\u70ed\u8f7d\u8377\u6062\u590d\u6ce8\u518c**\uff08convection / heat_flux / heat_power / radiation\uff09\u3002"
      "\u2605 \u8d77\u70b9\u662f**\u6284\u5b98\u65b9\u58f0\u660e**\uff08\u6536\u655b\u62a5\u544a\u5199\u7684\u4e0b\u4e00\u6b65\uff09\uff1aCHM \u91cc\u516d\u6761 VB \u58f0\u660e"
      "**\u4e00\u6a21\u4e00\u6837**\uff08`AddXxx(DispArray As Object, ByRef ErrorCode)`\uff09\u4e14\u4e0e**\u5df2\u80fd\u7528\u7684** `AddElasticConnector` \u540c\u5f62"
      "\u21d2 \u5f62\u6001\u6ca1\u9519\u3002\u2605\u2605 \u800c\u7ebf\u7d22\u6765\u81ea**\u8f7d\u8377\u7684\u6027\u8d28**\uff1a\u8fd9\u4e94\u6761\u662f**\u70ed\u8f7d\u8377**\uff0c"
      "\u800c\u8f6e 402 \u6211\u4e00\u76f4\u5728 **`static`** \u7b97\u4f8b\u4e0a\u8bd5\u5b83\u4eec\u3002"
      "\u771f\u673a\uff08\u8d70 `sw_guard`\uff0c4.9 s \u65e0\u5f39\u7a97\uff09\uff1a\u5efa **thermal\uff08`study_type=3`\uff09** \u7b97\u4f8b\u540e "
      "\u2605 **convection 0\u21921 \u00b7 heat_flux 1\u21922 \u00b7 heat_power 2\u21923 \u00b7 radiation 3\u21924**\uff08\u9010\u6761 +1\uff09\u3002"
      "\u8bc1\u636e output/thermal-loads-evidence.json\u3002"
      "\u2605 \u5404\u8f7d\u8377\u5bf9\u7b97\u4f8b\u7c7b\u578b\u7684\u8981\u6c42**\u4e0d\u540c**\uff1a\u8fd9 4 \u6761\u8981 **thermal**\uff0c"
      "\u800c `elastic_connector` \u76f8\u53cd\uff08\u5728 **static** \u4e0b\u6210\u3001\u5728 thermal \u4e0b\u4e0d\u6210\uff09\u3002"
      "\u26a0 `temperature` **\u4ecd\u4e0d\u6ce8\u518c**\uff1a\u62a5 `-2147352561 \u975e\u9009\u62e9\u6027\u7684\u53c2\u6570`\uff08\u7f3a\u5fc5\u586b\uff09"
      "\u2014\u2014 CHM \u90a3\u9875\u662f **2021 \u7248**\u3001\u672c\u673a\u662f 2026\uff1b\u800c\u53cd\u5c04 dump \u4e0e arity \u8868\u91cc**\u90fd\u6ca1\u6709\u8fd9\u4e2a\u540d\u5b57**"
      "\u21d2 \u6309\u94c1\u5f8b 5 \u4e0d\u731c\uff0c\u4e0b\u4e00\u6b65\u67e5 CHM \u7684**\u793a\u4f8b\u4ee3\u7801**\u6216\u6d3b\u7684\u7c7b\u578b\u5e93\u3002")

LIM = ("\u26a0 2026-10-03\uff08\u8f6e 408\uff09**\u5404\u4eff\u771f\u8f7d\u8377\u5bf9\u7b97\u4f8b\u7c7b\u578b\u7684\u8981\u6c42**\u4e0d\u540c**"
       "\uff0c\u5fc5\u987b\u9010\u6761\u8bb0\uff1a\u2605 `convection` / `heat_flux` / `heat_power` / `radiation` "
       "\u8981\u300c**\u70ed\u7b97\u4f8b**\u300d\uff08`study_type=3`\uff09\uff0c\u5728**\u9759\u529b**\u7b97\u4f8b\u4e0a\u5b9e\u6d4b**\u4e0d\u6da8\u8ba1\u6570**\uff1b"
       "\u2605 \u800c `elastic_connector` **\u76f8\u53cd**\uff08\u5728 static \u4e0b\u6210\u3001\u5728 thermal \u4e0b\u4e0d\u6210\uff09\u3002"
       "\u2605 \u53e6\uff1a`temperature` **\u4ecd\u672a\u6ce8\u518c** \u2014\u2014 \u62a5\u300c\u7f3a\u5fc5\u586b\u53c2\u6570\u300d"
       "\uff08`-2147352561`\uff09\uff0c\u800c CHM \u90a3\u9875\u662f 2021 \u7248\u3001\u672c\u673a\u662f 2026\uff1b"
       "\u2605 \u53cd\u5c04 dump \u4e0e arity \u8868\u91cc\u90fd\u6ca1\u6709\u8be5\u540d\u5b57 \u21d2 \u6309\u94c1\u5f8b 5 \u4e0d\u731c\uff0c"
       "\u4e0b\u4e00\u6b65\u67e5 CHM \u7684**\u793a\u4f8b\u4ee3\u7801**\u6216\u6d3b\u7684\u7c7b\u578b\u5e93\u3002")

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
    for t in ("solidworks_simulation_apply_convection", "solidworks_simulation_apply_heat_flux",
              "solidworks_simulation_apply_heat_power", "solidworks_simulation_apply_radiation"):
        if t not in ts:
            ts.append(t)
    y["mcp_tools"] = ts
    ev = list(y.get("evidence") or [])
    if not any("4 \u6761\u70ed\u8f7d\u8377\u6062\u590d\u6ce8\u518c" in s for s in ev):
        ev.insert(0, EV)
    y["evidence"] = ev
    lim = list(y.get("limitations") or [])
    if not any("\u5bf9\u7b97\u4f8b\u7c7b\u578b" in s for s in lim):
        lim.insert(0, LIM)
    y["limitations"] = lim
    c.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("(2) %s tools=%d ev=%d lim=%d" % (y["id"], len(ts), len(ev), len(lim)))
