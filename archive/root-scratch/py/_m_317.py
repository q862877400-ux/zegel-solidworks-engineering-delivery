import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

K = Path(r"D:\AI\SW\docs\known-facts.md")
body = Path(r"D:\AI\SW\_fact317.txt").read_text(encoding="utf-8").strip().replace("\n", " ")
tk = K.read_text(encoding="utf-8")
print("(1) " + ("wrote 317" if "| 317 |" not in tk else "already"))
if "| 317 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + body + "\n", encoding="utf-8")

EV = ("python \u771f\u673a\uff08\u8f6e 402\uff09\u2605 **PASS** \u2014\u2014 24h \u8ba1\u5212 v2 \u6bb5 5\uff08\u4eff\u771f\u8f7d\u8377\u65cf\uff09\uff1a"
      "`solidworks_simulation_apply_elastic_connector`\uff08`sw_simulation_loads.apply_elastic_connector_report`\uff09\u3002"
      "\u2605 \u8c03\u7528\u8d70**\u5de5\u5177\u5c42\u540c\u5e8f**\uff08`inject` \u2192 `pre_call` \u2192 `derived_args`\uff09\uff0c"
      "\u2605\u2605 \u800c\u4e14\u7167\u65e2\u6709\u811a\u672c\u7559\u4e0b\u7684**\u5148\u4f8b\u8b66\u544a**\uff1a\u6bcf\u6b21**\u5148 `ClearSelection2(True)`** "
      "\uff08`select_face_at` \u7684 `append=False` \u53ea\u8868\u793a\u201c\u4e0d\u8ffd\u52a0\u201d\u3001**\u4e0d\u6e05\u7a7a**\uff09\u3002"
      "\u771f\u673a\uff1a\u8f7d\u8377\u8ba1\u6570 **0 \u2192 1**\uff08\u2605 \u5224\u636e\u662f\u56de\u8bfb\u8ba1\u6570\u6070\u597d +1\uff0c\u4e0d\u662f\u8fd4\u56de\u503c\uff09\u3002"
      "\u8bc1\u636e output/loads-simple6-evidence.json\u3002"
      "\u26a0 **\u540c\u6279\u53e6 5 \u6761\uff08convection / heat_flux / heat_power / temperature / radiation\uff09"
      "\u771f\u673a\u672a\u5efa\u6210** \u21d2 \u6309\u786c\u7ea6\u675f\u2465 **\u56de\u9000\u6ce8\u518c**\uff08\u2605 \u5305\u88c5\u4e0e\u63a2\u9488\u4fdd\u7559\uff09\uff1b"
      "\u2605 \u771f\u56e0\uff1a\u8fd9\u4e00\u65cf\u91cc**\u5403\u5355\u5b9e\u4f53 / \u5403\u6570\u7ec4 / \u53c2\u6570\u66f4\u591a**\u4e09\u79cd\u6df7\u5728\u4e00\u8d77\uff0c"
      "\u2605 \u800c\u4ed3\u91cc\u7684\u6765\u6e90\u5757**\u53ea\u6284\u4e86 4 \u6761\u5b98\u65b9\u58f0\u660e**\uff08\u4e8b\u5b9e 317\uff09\u3002")

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
    if "solidworks_simulation_apply_elastic_connector" not in ts:
        ts.append("solidworks_simulation_apply_elastic_connector")
    y["mcp_tools"] = ts
    ev = list(y.get("evidence") or [])
    if not any("elastic_connector" in s for s in ev):
        ev.insert(0, EV)
    y["evidence"] = ev
    lim = list(y.get("limitations") or [])
    LIM = ("\u26a0 2026-10-03\uff08\u8f6e 402\uff09**\u540c\u6279 5 \u6761\u8f7d\u8377\u771f\u673a\u672a\u5efa\u6210**\uff08convection / heat_flux / "
           "heat_power / temperature / radiation\uff09\u21d2 \u2605 **\u5df2\u56de\u9000\u6ce8\u518c**\uff08\u5305\u88c5\u4e0e\u63a2\u9488\u4fdd\u7559\uff09\u3002"
           "\u2605 \u771f\u56e0\uff1a\u8fd9\u4e00\u65cf\u91cc**\u5403\u5355\u5b9e\u4f53 / \u5403\u6570\u7ec4 / \u53c2\u6570\u66f4\u591a**\u6df7\u5728\u4e00\u8d77\uff0c"
           "\u2605 \u800c\u4ed3\u91cc\u7684\u6765\u6e90\u5757**\u53ea\u6284\u4e86 4 \u6761\u5b98\u65b9 VB \u58f0\u660e**\uff08Gravity / "
           "CentrifugalForce / DistributedMass / RemoteLoad\uff09\u2014\u2014 \u2605 **\u672c\u6279\u8fd9 5 \u6761\u7684\u6ca1\u6284**\u3002"
           "\u2605 \u4e0b\u4e00\u6b65\uff1a\u628a\u90a3 5 \u6761\u7684\u5b98\u65b9\u58f0\u660e**\u9010\u6761\u6284\u4e0b\u6765**\u518d\u5bf9\u7740\u5199\uff0c\u2605 \u4e0d\u7ee7\u7eed\u8bd5\u53c2\u6570\u3002")
    if not any("5 \u6761\u8f7d\u8377\u771f\u673a\u672a\u5efa\u6210" in s for s in lim):
        lim.insert(0, LIM)
    y["limitations"] = lim
    c.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("(2) %s tools=%d ev=%d lim=%d" % (y["id"], len(ts), len(ev), len(lim)))
