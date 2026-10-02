import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

W = Path(r"D:\AI\SW")
K = W / "docs" / "known-facts.md"
body = (W / "_fact334.txt").read_text(encoding="utf-8").strip().replace("\n", " ")
tk = K.read_text(encoding="utf-8")
print("(1) " + ("wrote 334" if "| 334 |" not in tk else "already"))
if "| 334 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + body + "\n", encoding="utf-8")

#: \u2605 \u628a"\u5224\u636e\u4e0d\u7a33"\u5199\u8fdb capabilities \u7684 limitations\uff08\u2605 \u90a3\u662f\u7ed9\u7528\u6237\u7684\uff09
LIM = ("\u26a0 2026-10-03\uff08\u8f6e 419\uff09**B \u7ec4\uff08\u591a\u9762 / \u591a\u9876\u70b9\u8fde\u63a5\u4ef6\uff09\u7684\u5224\u636e\u5728\u8fd9\u6761\u8def\u4e0a"
       "**\u95f4\u6b47\u6027\u4e0d\u7a33**\uff1a**\u540c\u4e00\u6bb5\u4ee3\u7801\u3001\u540c\u4e00\u53f0\u673a\u3001\u540c\u4e00\u5929** \u51fa\u73b0\u8fc7 "
       "\u300c\u6210 / \u4e0d\u6210 / \u6210\u300d\u3002\u2605 \u5177\u4f53\u5f62\u6001\uff1a`_report` \u7684\u56de\u8bfb\uff08"
       "`ICWLoadsAndRestraintsManager.Count`\uff09\u5728\u6d89\u53ca**\u9876\u70b9\u9009\u62e9**\u7684\u573a\u666f\u91cc"
       "\u6709\u65f6\u8fd4 **-1**\uff08\u53d6\u4e0d\u5230\uff09\uff0c\u6709\u65f6\u62a5 `0x80010105`\uff08\u670d\u52a1\u5668\u51fa\u73b0\u610f\u5916\u60c5\u51b5\uff09"
       "\u6216 `0x800706BA`\uff08\u8fdc\u7a0b\u8fc7\u7a0b\u8c03\u7528\u5931\u8d25\uff09\u3002\u2605 \u5df2\u5426\u6389\u4e94\u6761\u5047\u8bbe"
       "\uff08\u7d2f\u79ef / \u5224\u636e\u9009\u62e9 / \u9648\u65e7\u5f15\u7528 / \u4f1a\u8bdd\u72b6\u6001 / \u300c\u7b2c\u4e00\u4e2a\u8f7d\u8377\u300d\uff09"
       "\u21d2 \u2605 **\u610f\u5473\u7740\u8fd9\u4e24\u6761\u80fd\u529b\u5e76\u672a\u88ab\u8bc1\u4f2a\uff0c\u53ea\u662f\u5224\u636e\u4e0d\u53ef\u7528**\uff1b"
       "\u2605 \u6545**\u672a\u6ce8\u518c**\uff08\u786c\u7ea6\u675f\u2465\uff09\u3002\u2605 \u4e0b\u4e00\u6b65\uff1a\u6362\u4e00\u4e2a**\u4e0d\u4f9d\u8d56 `Count`**"
       "\u7684\u56de\u8bfb\uff08\u5982\u6570 `GetLoadsAndRestraints(i, out_i4())`\uff0c\u2605 \u800c\u5b83\u540c\u6837\u4e0d\u7a33 \u21d2 "
       "\u5148\u5728**\u5df2\u77e5\u6210\u529f**\u573a\u666f\u4e0a\u9a8c\u5b83\uff09\u3002")

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
    lim = list(y.get("limitations") or [])
    if not any("B \u7ec4" in s and "\u95f4\u6b47\u6027\u4e0d\u7a33" in s for s in lim):
        lim.insert(0, LIM)
    y["limitations"] = lim
    c.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("(2) %s lim=%d" % (y["id"], len(lim)))
