import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

W = Path(r"D:\AI\SW")
K = W / "docs" / "known-facts.md"
body = (W / "_fact330.txt").read_text(encoding="utf-8").strip().replace("\n", " ")
tk = K.read_text(encoding="utf-8")
print("(1) " + ("wrote 330" if "| 330 |" not in tk else "already"))
if "| 330 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + body + "\n", encoding="utf-8")

EV = ("python \u771f\u673a\uff08\u8f6e 415\uff09\u2605 **PASS** \u2014\u2014 \u25c6 \u70ed\u8f7d\u8377\u7ec4\uff1a"
      "convection 0\u21921 \u00b7 heat_flux 1\u21922 \u00b7 heat_power 2\u21923 \u00b7 **temperature 3\u21924** \u00b7 radiation 4\u21925\uff1b"
      "\u25c6 \u7ed3\u6784\u8f7d\u8377\u7ec4\uff1adistributed_mass 0\u21921 \u00b7 force 1\u21922 \u00b7 **remote_load 2\u21923**\u3002"
      "\u2605 \u800c\u771f\u56e0**\u4e0d\u5728\u63a2\u9488**\uff1a\u80fd\u529b\u5c42\u91cc\u4e00\u5f20**\u624b\u6284 CHM \u7684\u540d\u5355**"
      "`_ERRORCODE_MEMBERS` **\u6f0f\u4e86 `AddTemperature` \u4e0e `AddRemoteLoad`** \u21d2 "
      "`_wants_error_code` \u56de False \u21d2 **\u4e0d\u8865 `out_i4()`** \u21d2 "
      "`com_error(-2147352561, \u975e\u9009\u62e9\u6027\u7684\u53c2\u6570)`\u3002"
      "\u2605 \u800c\u5b9a\u4f4d\u5b83\u7528\u7684\u662f**\u51fa\u5382\u7c7b\u578b\u5e93**\uff1a"
      "**PowerShell  \u7684\u7eaf\u5143\u6570\u636e\u53cd\u5c04**\uff08`[Reflection.Assembly]::LoadFrom` "
      "\u2192 `SolidWorks.Interop.cosworks.dll` **34.4.1.1011**\uff09"
      "\u2014\u2014 \u2605 **\u96f6\u4f9d\u8d56\u3001\u4e0d\u9700\u8981 SolidWorks \u5b9e\u4f8b**\uff1b"
      "\u5b83\u7ed9\u51fa\u2605\u2605 **\u5168\u90e8 35 \u4e2a `Add*` \u90fd\u5e26 `ErrorCode:Int32&`**\uff08\u4e0d\u5e26\u7684 0 \u4e2a\uff09"
      "\u21d2 \u540d\u5355\u6539\u4e3a\u90a3 35 \u4e2a\uff08\u4e00\u6761\u6539\u52a8\u4fee\u597d\u4e24\u4e2a\u540d\u5b57\uff09\u3002"
      "\u8bc1\u636e output/thermal-loads-evidence.json \u4e0e output/loads-groupa3-evidence.json\u3002")

LIM = ("\u26a0 2026-10-03\uff08\u8f6e 415\uff09\u2605 \u5404\u8f7d\u8377\u5bf9\u7b97\u4f8b\u7c7b\u578b\u7684\u8981\u6c42**\u9010\u6761\u4e0d\u540c**\uff0c\u73b0\u5df2\u9a8c\u7684\uff1a"
       "**thermal** \u21d0 convection / heat_flux / heat_power / temperature / radiation\uff1b"
       "**static** \u21d0 elastic_connector / distributed_mass / force / remote_load\u3002"
       "\u2605 \u53e6\uff1a\u80fd\u529b\u5c42\u91cc\u51e1\u300c**\u624b\u6284\u7684\u540d\u5355/\u8868**\u300d\uff0c\u90fd\u8981\u5199\u6e05\u5b83\u6284\u81ea\u54ea\u4e00\u7248\uff1b"
       "\u2605 \u800c\u53ea\u8981\u51fa\u5382\u6e90\u80fd\u5728\u76d8\u4e0a\u8bfb\u5230\uff0c\u5c31\u8be5**\u76f4\u63a5\u5bf9\u5b83\u6838**"
       "\uff08\u2605 \u672c\u8f6e\u7528\u7684\u662f PowerShell \u7684 .NET \u5143\u6570\u636e\u53cd\u5c04\uff0c\u96f6\u4f9d\u8d56\uff09\u3002")

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
    for t in ("solidworks_simulation_apply_temperature", "solidworks_simulation_apply_remote_load"):
        if t not in ts:
            ts.append(t)
    y["mcp_tools"] = ts
    ev = list(y.get("evidence") or [])
    if not any("_ERRORCODE_MEMBERS" in s for s in ev):
        ev.insert(0, EV)
    y["evidence"] = ev
    lim = list(y.get("limitations") or [])
    #: \u2605 \u65e7\u7684\u90a3\u6761\uff08\u8bf4 temperature/remote_load \u62a5\u7f3a\u53c2\u3001\u5acc\u7591 CHM \u8fc7\u65f6\uff09\u5df2\u88ab\u672c\u8f6e\u63a8\u7ffb \u21d2 \u6362\u6389
    lim = [s for s in lim if "CHM\uff082021 \u7248\uff09\u4e0e\u672c\u673a\uff082026\uff09\u7b7e\u540d\u4e0d\u4e00\u81f4" not in s]
    if not any("\u9010\u6761\u4e0d\u540c" in s and "\u73b0\u5df2\u9a8c" in s for s in lim):
        lim.insert(0, LIM)
    y["limitations"] = lim
    c.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("(2) %s tools=%d ev=%d lim=%d" % (y["id"], len(ts), len(ev), len(lim)))
