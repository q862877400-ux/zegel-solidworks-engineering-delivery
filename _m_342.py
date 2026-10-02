import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
W = Path(r"D:\AI\SW")
R = Path(r"C:\swprojects\sw-skill-fork")

#: \u2460 \u4e8b\u5b9e 342
K = W / "docs" / "known-facts.md"
body = (W / "_fact342.txt").read_text(encoding="utf-8").strip().replace("\n", " ")
tk = K.read_text(encoding="utf-8")
print("(1) " + ("wrote 342" if "| 342 |" not in tk else "already"))
if "| 342 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + body + "\n", encoding="utf-8")

#: \u2461 capabilities\uff1a\u65b0\u589e\u5de5\u5177 + **\u4fee\u6b63\u8f6e 364 \u90a3\u6761 limitation**
EV = ("python \u771f\u673a\uff08\u8f6e 428\uff09\u2605 **PASS** \u2014\u2014 **\u7ed3\u6784\u6784\u4ef6**\uff08\u710a\u4ef6\u65cf\u7b2c\u4e00\u6761\uff09\u3002"
      "\u771f\u673a\uff08\u8d70 `sw_guard`\uff0c\u65e0\u5f39\u7a97\uff09\uff1a\u524d\u89c6\u57fa\u51c6\u9762\u4e0a\u4e00\u6bb5 100 mm \u76f4\u7ebf\u4f5c\u8def\u5f84 + "
      "**GB \u65b9\u7ba1\u8f6e\u5ed3**\uff08`GB\\square-rods.sldlfp`\uff09\u21d2 **\u5efa\u6210 `square-rods (1)`**\uff0c"
      "\u2605 \u5224\u636e\u662f**\u7279\u5f81\u6811**\uff08\u4e0d\u662f\u8ba1\u6570\uff09\uff1a`new_type_names` = "
      "**[\"WeldMemberFeat\", \"WeldmentFeature\"]**\u3002"
      "\u8bc1\u636e output/structural-member-evidence.json\u3002"
      "\u2605\u2605 \u800c\u672c\u8f6e\u63a2\u67e5**\u63a8\u7ffb\u4e86**\u4e00\u6761\u65e2\u6709\u7ed3\u8bba\uff1a"
      "`capabilities.yaml` \u91cc\u8f6e 364 \u8bb0\u7684\u300c**\u672c\u673a\u6ca1\u88c5\u710a\u4ef6\u8f6e\u5ed3\u5e93**\u300d"
      "\u2605 **\u4e0d\u6210\u7acb** \u2014\u2014 \u672c\u673a "
      "`C:\\ProgramData\\SOLIDWORKS\\SOLIDWORKS 2026\\weldment profiles` \u4e0b\u6709 **111 \u4e2a** `.sldlfp`"
      "\uff08ansi / GB / iso / DIN / JIS \u2026\uff09\u3002"
      "\u2605 \u5de5\u5177\u4e0d\u8bfb\u9009\u533a\u4e5f\u4e0d\u4f9d\u8d56\u9009\u4e2d\u72b6\u6001\uff1a\u5b83\u81ea\u5df1\u6309**\u8349\u56fe\u540d**\u53d6\u7ebf\u6bb5\u3001\u5efa\u6784\u4ef6\u3001\u5e76**\u7528\u7279\u5f81\u6811\u56de\u8bfb**\u3002")

LIM_FIX = ("\u2605\u2605\u2605 2026-10-03\uff08\u8f6e 428\uff09**\u63a8\u7ffb\u8f6e 364 \u90a3\u6761\u7ed3\u8bba**\uff1a"
           "\u5b83\u5199\u7684\u662f\u300c**\u672c\u673a\u6ca1\u88c5\u300c\u710a\u4ef6\u8f6e\u5ed3\u5e93\u300d**\u300d\uff0c"
           "\u2605 \u800c\u672c\u8f6e\u91cd\u6838\u53d1\u73b0\uff1a"
           "`C:\\ProgramData\\SOLIDWORKS\\SOLIDWORKS 2026\\weldment profiles` **\u5728**\uff0c\u4e14\u6709 "
           "**111 \u4e2a** `.sldlfp`\uff08ansi / **GB** / iso / DIN / JIS / BSI / CISC / AS\uff09"
           "\u21d2 \u2605**\u524d\u7f6e\u73b0\u5728\u662f\u9f50\u7684**\uff0c\u5df2\u771f\u673a\u5efa\u6210\u7ed3\u6784\u6784\u4ef6\uff08"
           "`output/structural-member-evidence.json` PASS\uff09\u3002"
           "\u2605 \u6559\u8bad\uff1a**\u4e00\u6761\u300c\u73af\u5883\u7f3a X\u300d\u7684\u7ed3\u8bba\u4e5f\u4f1a\u8fc7\u671f**"
           "\uff08\u800c\u5b83\u6070\u597d\u662f\u6700\u5bb9\u6613\u88ab\u5f53\u771f\u7684\u90a3\u79cd\uff09"
           "\u21d2 \u4e0b\u6b21\u52a8\u624b\u524d**\u91cd\u6838 X**\u3002")

c = R / "capabilities.yaml"
d = json.loads(c.read_text(encoding="utf-8"))
n_fix = 0
n_tool = 0
for y in d["capabilities"]:
    tools = list(y.get("mcp_tools") or [])
    #: \u2605 \u4fee\u6b63\u90a3\u6761 limitation\uff08\u6309\u5185\u5bb9\u627e\uff09
    lims = list(y.get("limitations") or [])
    for i, s in enumerate(lims):
        if "\u672c\u673a\u6ca1\u88c5\u300c\u710a\u4ef6\u8f6e\u5ed3\u5e93\u300d" in str(s):
            lims[i] = LIM_FIX
            n_fix += 1
    if n_fix and lims != list(y.get("limitations") or []):
        y["limitations"] = lims
    #: \u2605 \u628a\u65b0\u5de5\u5177\u6302\u5230\u710a\u4ef6\u90a3\u6761\u80fd\u529b\u4e0a
    if y.get("id") in ("weldments", "weldment_cut_list"):
        if "solidworks_weldment_create_structural_member" not in tools:
            tools.append("solidworks_weldment_create_structural_member")
            y["mcp_tools"] = tools
            n_tool += 1
        ev = list(y.get("evidence") or [])
        if not any("\u7ed3\u6784\u6784\u4ef6" in s and "\u710a\u4ef6\u65cf\u7b2c\u4e00\u6761" in s for s in ev):
            ev.insert(0, EV)
        y["evidence"] = ev
        break
c.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("(2) limitation \u4fee\u6b63 %d \u5904\uff1b\u65b0\u5de5\u5177\u6302\u4e0a %d \u6761" % (n_fix, n_tool))
