import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

K = Path(r"D:\AI\SW\docs\known-facts.md")
body = Path(r"D:\AI\SW\_fact315.txt").read_text(encoding="utf-8").strip().replace("\n", " ")
tk = K.read_text(encoding="utf-8")
if "| 315 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + body + "\n", encoding="utf-8")
    print("(1) wrote 315")

LIM = ("\u26a0 2026-10-03\uff08\u8f6e 400\uff09**\u4e24\u6761\u771f\u7f3a\u53e3\u8bd5\u8fc7\u800c\u672a\u653b\u4e0b**\uff08\u2605 \u5df2\u56de\u9000\u5de5\u5177\u6ce8\u518c\uff0c"
       "\u2605 \u800c\u5305\u88c5\u4e0e\u63a2\u9488\u4fdd\u7559\uff09\uff1a\u2460 `add_dimension` \u2014\u2014 \u5355\u4f4d\u5df2\u67e5\u6e05"
       "\uff08\u5b98\u65b9\u53eb**\u7c73**\uff09\u3001\u524d\u7f6e\u5df2\u505a\uff08\u5148\u9009\u4e2d\u5b9e\u4f53\uff09\uff0c\u2605 \u800c\u9009\u4e2d **2 \u6761\u8fb9**\u540e "
       "`AddDimension2` **\u4ecd\u56de None**\uff08\u2605 \u5c3a\u5bf8\u6ca1\u5efa\u6210\uff09\uff1b\u2461 `linear_pattern` \u2014\u2014 "
       "\u53c2\u6570\u4e2a\u6570\u5df2\u4fee\u5bf9\uff08**10 \u53c2**\uff09\u3001\u95f4\u8ddd\u5355\u4f4d\u5df2\u6362\u7b97\u6b63\u786e\uff0c"
       "\u2605 \u800c\u771f\u673a\u4e0a**\u4e0d\u62a5\u9519\u800c\u7279\u5f81\u6811\u4e0d\u53d8**\uff089\u21929\uff09\u3002"
       "\u2605 **\u4e0b\u4e00\u6b21\u4ece\u8fd9\u91cc\u63a5**\uff08\u2605 \u4e8b\u5b9e 315 \u6709\u5b8c\u6574\u5361\u70b9\uff09\uff0c\u2605 \u4e0d\u4ece\u96f6\u91cd\u731c\u3002")

c = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(c.read_text(encoding="utf-8"))
y = next((z for z in d["capabilities"] if z["id"] == "part_and_features"), None)
if y is None:
    print("(2) **\u672a\u627e\u5230 part_and_features**")
else:
    lim = list(y.get("limitations") or [])
    if not any("add_dimension" in s and "\u56de\u9000\u5de5\u5177\u6ce8\u518c" in s for s in lim):
        lim.insert(0, LIM)
    y["limitations"] = lim
    c.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("(2) part_and_features lim=%d" % len(lim))
