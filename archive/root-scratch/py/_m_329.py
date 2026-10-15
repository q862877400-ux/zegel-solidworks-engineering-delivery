import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

W = Path(r"D:\AI\SW")
K = W / "docs" / "known-facts.md"
body = (W / "_fact329.txt").read_text(encoding="utf-8").strip().replace("\n", " ")
tk = K.read_text(encoding="utf-8")
print("(1) " + ("wrote 329" if "| 329 |" not in tk else "already"))
if "| 329 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + body + "\n", encoding="utf-8")

EV = ("python \u771f\u673a\uff08\u8f6e 414\uff09\u2605 **PASS** \u2014\u2014 24h \u8ba1\u5212 v2 \u6bb5 5\uff08A \u7ec4\u6536\u5c3e\uff09\uff1a"
      "`solidworks_simulation_apply_distributed_mass` \u4e0e `solidworks_simulation_apply_force`\u3002"
      "\u771f\u673a\uff08\u8d70 `sw_guard`\uff0c4.0 s \u65e0\u5f39\u7a97\uff09\uff1a\u5728 **\u9759\u529b\u7b97\u4f8b**\u4e0a"
      "\u2605 **distributed_mass \u8ba1\u6570 0\u21921** \u00b7 **force \u8ba1\u6570 1\u21922**\uff08**\u5355\u8c03\u5e8f\u5217**\uff09\u3002"
      "\u8bc1\u636e output/loads-groupa3-evidence.json\u3002"
      "\u2605\u2605 \u800c\u771f\u56e0\u503c\u5f97\u5355\u8bb0\uff1a\u7b2c\u4e00\u7248\u7528\u4e86**\u56fa\u5b9a\u7b97\u4f8b\u540d** \u21d2 "
      "\u56de\u8bfb\u8ba1\u6570\u53d8 `-1`\uff08`_loads_count` \u5bf9\u201c\u53d6\u4e0d\u5230\u201d\u7684\u7ea6\u5b9a\uff09\u21d2 **\u5224\u636e\u5047\u7ea2**\uff1b"
      "\u2605 \u800c\u8bca\u65ad\u63a2\u9488\u8bc1\u660e `Count` \u5728**\u9759\u529b\u4e0e\u70ed\u4e24\u79cd\u7b97\u4f8b\u4e0a\u90fd\u6b63\u5e38**"
      "\u21d2 \u771f\u56e0\u662f**\u7b97\u4f8b\u540d\u91cd\u590d**\uff08\u4ed3\u91cc\u81ea\u6ce8\u201c\u80fd\u529b\u5c42\u4e0d\u68c0\u67e5\u91cd\u540d\u201d\uff09"
      "\u21d2 \u6539\u6210**\u5e26\u65f6\u95f4\u6233\u7684\u552f\u4e00\u540d**\u540e\u7acb\u523b pass\u3002"
      "\u2605 \u8fd9\u4e24\u6761\u4e0e\u70ed\u8f7d\u8377\u90a3 4 \u6761**\u76f8\u53cd**\uff1a\u5b83\u4eec\u8981 **static**\uff08\u5404\u8f7d\u8377\u5bf9\u7b97\u4f8b\u7c7b\u578b\u8981\u6c42\u4e0d\u540c\uff09\u3002"
      "\u26a0 `remote_load` **\u4ecd\u4e0d\u6ce8\u518c**\uff1a\u62a5\u7f3a\u5fc5\u586b\u53c2\u6570\uff0c\u2605 \u800c\u4ed3\u91cc\u6765\u6e90\u5757\u8bb0\u7684\u5b98\u65b9\u58f0\u660e\u4e0e"
      "`_check` \u4e00\u81f4 \u21d2 \u2605 \u5acc\u7591 CHM\uff082021 \u7248\uff09\u8fc7\u65f6\uff0c\u4e0e `AddTemperature` \u540c\u5f62"
      "\uff08\u53cd\u5c04 dump \u91cc\u4e24\u4e2a\u540d\u5b57\u90fd\u6ca1\u6709\uff09\u21d2 \u6309\u94c1\u5f8b 5 \u4e0d\u731c\u3002")

LIM = ("\u26a0 2026-10-03\uff08\u8f6e 414\uff09\u2605 **\u5404\u8f7d\u8377\u5bf9\u7b97\u4f8b\u7c7b\u578b\u7684\u8981\u6c42\u4e0d\u540c**\uff08\u9010\u6761\u8bb0\uff09\uff1a"
       "\u2605 `convection`/`heat_flux`/`heat_power`/`radiation` \u8981 **thermal**\uff1b"
       "\u2605 \u800c `elastic_connector` \u4e0e\u672c\u8f6e\u7684 `distributed_mass`/`force` \u8981 **static**\uff1b"
       "\u2605 \u800c `temperature` \u4e0e `remote_load` \u62a5\u7f3a\u5fc5\u586b\u53c2\u6570\uff08\u770b\u4e0d\u51fa\u7b97\u4f8b\u7c7b\u578b\u95ee\u9898\uff09"
       "\u2014\u2014 \u5acc\u7591 CHM\uff082021 \u7248\uff09\u4e0e\u672c\u673a\uff082026\uff09\u7b7e\u540d\u4e0d\u4e00\u81f4\uff0c\u800c\u53cd\u5c04 dump \u91cc\u6ca1\u6709\u8fd9\u4e24\u4e2a\u540d\u5b57\u3002"
       "\u2605 \u53e6\uff1a**\u5efa\u7b97\u4f8b\u5fc5\u987b\u7528\u552f\u4e00\u540d** \u2014\u2014 \u91cd\u540d\u4f1a\u8ba9\u8ba1\u6570\u56de\u8bfb\u53d8 `-1`\uff08\u5047\u7ea2\uff09\u3002")

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
    for t in ("solidworks_simulation_apply_distributed_mass", "solidworks_simulation_apply_force"):
        if t not in ts:
            ts.append(t)
    y["mcp_tools"] = ts
    ev = list(y.get("evidence") or [])
    if not any("A \u7ec4\u6536\u5c3e" in s for s in ev):
        ev.insert(0, EV)
    y["evidence"] = ev
    lim = list(y.get("limitations") or [])
    if not any("\u5efa\u7b97\u4f8b\u5fc5\u987b\u7528\u552f\u4e00\u540d" in s for s in lim):
        lim.insert(0, LIM)
    y["limitations"] = lim
    c.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("(2) %s tools=%d ev=%d lim=%d" % (y["id"], len(ts), len(ev), len(lim)))
