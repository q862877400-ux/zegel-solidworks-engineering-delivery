import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

K = Path(r"D:\AI\SW\docs\known-facts.md")
body = Path(r"D:\AI\SW\_fact320.txt").read_text(encoding="utf-8").strip().replace("\n", " ")
tk = K.read_text(encoding="utf-8")
print("(1) " + ("wrote 320" if "| 320 |" not in tk else "already"))
if "| 320 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + body + "\n", encoding="utf-8")

EV = ("python \u771f\u673a\uff08\u8f6e 405\uff09\u2605 **PASS** \u2014\u2014 24h \u8ba1\u5212 v2 \u6bb5 3 \u6536\u5c3e\uff1a"
      "`solidworks_add_dimension`\uff08`sw_part.add_dimension_report`\uff09\u3002"
      "\u2605\u2605 \u5224\u636e\u7528\u4e86\u4e8b\u5b9e 53 \u7684\u5904\u65b9\uff1a**\u628a\u731c\u6d4b\u53d8\u6210\u4e00\u5f20\u7a77\u4e3e\u8868** \u2014\u2014 "
      "\u5bf9\u76d2\u4f53 12 \u6761\u8fb9\u7684**\u4e24\u4e24\u5171 66 \u5bf9**\u9010\u4e00\u8bd5\u3002"
      "\u771f\u673a\uff08\u8d70 `sw_guard`\uff0c7.1 s \u65e0\u5f39\u7a97\uff09\uff1a\u6210\u529f\u7684\u8fb9\u5bf9\u662f "
      "`[0,1] [0,2] [0,3] [0,4] [0,7] [0,8] [0,11] [1,2]`\uff08**8/8**\uff0c\u5230\u4e0a\u9650\u5c31\u505c\uff09"
      "\u2014\u2014 \u2605\u2605 **\u542b\u8fb9 0 \u7684\u7ec4\u5408\u90fd\u6210\uff0c\u8fde `[0,1]` \u8fd9\u79cd\u76f8\u90bb\u8fb9\u90fd\u6210**\u3002"
      "\u8bc1\u636e output/dimension-edge-pairs-evidence.json\u3002"
      "\u2605\u2605 \u800c\u8f6e 400 \u7528**\u540c\u6837**\u7684 `[0,1]` \u5374\u5931\u8d25 \u2014\u2014 \u552f\u4e00\u5dee\u522b\u662f"
      "\u672c\u8f6e**\u6bcf\u6b21\u9009\u4e4b\u524d\u90fd `ClearSelection2(True)`** \u21d2 "
      "\u2605 \u771f\u56e0\u662f**\u63a2\u9488\u9009\u533a\u4e0d\u5e72\u51c0**\uff0c\u4e0d\u662f\u80fd\u529b\u574f\u4e86\u3002"
      "\u26a0 **\u5df2\u77e5\u9650\u5236\uff08\u672a\u9694\u79bb\uff09**\uff1a\u540c\u4e00\u5305\u88c5\u5728**\u677f + \u51f8\u53f0**\u7684\u6a21\u578b\u4e0a"
      "\u5931\u8d25\uff08\u8fde\u8bd5 3 \u6b21\u540e\u6309\u4e8b\u5b9e 53 \u505c\u6b62\u9694\u79bb\uff09\uff1b"
      "\u5b98\u65b9\u53e6\u6ce8\u300conly use on visible documents\u300d\u4e14\u5c3a\u5bf8**\u6309\u4f4d\u7f6e**\u653e\u7f6e\u3002")

c = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(c.read_text(encoding="utf-8"))
y = next((z for z in d["capabilities"] if z["id"] == "part_and_features"), None)
if y is None:
    print("(2) **\u672a\u627e\u5230 part_and_features**")
else:
    ts = list(y.get("mcp_tools") or [])
    if "solidworks_add_dimension" not in ts:
        ts.append("solidworks_add_dimension")
    y["mcp_tools"] = ts
    ev = list(y.get("evidence") or [])
    if not any("add_dimension" in s and "PASS" in s for s in ev):
        ev.insert(0, EV)
    y["evidence"] = ev
    lim = list(y.get("limitations") or [])
    NEW = ("\u26a0 2026-10-03\uff08\u8f6e 405\uff09**`solidworks_add_dimension` \u7684\u4e00\u6761\u672a\u9694\u79bb\u9650\u5236**\uff1a"
           "\u7eaf\u76d2\u4f53\u4e0a **8/8 \u8fb9\u5bf9**\u90fd\u6210\uff0c\u2605 \u800c\u5728**\u677f + \u51f8\u53f0**\u7684\u6a21\u578b\u4e0a\u5931\u8d25"
           "\uff08\u8fde\u8bd5 3 \u6b21\u540e\u6309\u4e8b\u5b9e 53 \u505c\u6b62\u9694\u79bb\uff09\u3002"
           "\u2605 \u5b98\u65b9\u53e6\u6ce8\uff1a**only use on visible documents** \u4e14\u5c3a\u5bf8**\u6309\u4f4d\u7f6e**\u653e\u7f6e"
           "\uff08\u4f4d\u7f6e\u4e0d\u843d\u5728\u53ef\u89c1\u6a21\u578b\u4e0a\u65f6\u53ef\u80fd\u5c31\u5efa\u4e0d\u51fa\u6765\uff09\u3002"
           "\u2605 \u53e6\uff1a`linear_pattern` **\u4ecd\u672a\u6ce8\u518c** \u2014\u2014 \u5361\u70b9\u6536\u655b\u4e3a"
           "\u300c`DName1`/`DName2` \u662f**\u65b9\u5411\u7ef4\u5ea6\u7684\u540d\u5b57**\uff0c\u7a7a\u5b57\u7b26\u4e32 = \u6ca1\u6709\u65b9\u5411\u300d"
           "\u21d2 \u4e0b\u4e00\u6b65\u5148\u9020/\u9009\u4e00\u4e2a\u80fd\u5f53\u65b9\u5411\u57fa\u51c6\u7684\u5b9e\u4f53\u3002")
    if not any("\u672a\u9694\u79bb\u9650\u5236" in s and "add_dimension" in s for s in lim):
        lim.insert(0, NEW)
    y["limitations"] = lim
    c.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("(2) %s tools=%d ev=%d lim=%d" % (y["id"], len(ts), len(ev), len(lim)))
