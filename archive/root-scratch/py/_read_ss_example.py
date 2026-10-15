import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
Q = chr(34)
root = Path(r"D:\AI\SW\AI Solidworks\官方文档\SWhelp")
f = list(root.rglob("Access_Structure_System_Corner_Treatments_Example_VB.htm"))[0]
t = f.read_text(encoding="utf-8", errors="replace")
print("  文件 %d 字节" % len(t))
#: ★ 这份是 .htm 原文；把转义还原，再把 <br>/<p> 之类换成换行
t2 = (t.replace("\\u003c", "<").replace("\\u003e", ">")
       .replace("\\" + Q, Q).replace("\\u0026nbsp;", " ").replace("\\u0026amp;", "&"))
t2 = re.sub(r"(?i)<br\s*/?>", "\n", t2)
t2 = re.sub(r"(?i)</p>", "\n", t2)
t2 = re.sub(r"<[^>]+>", "", t2)
lines = [l.rstrip() for l in t2.splitlines()]
#: ★ 只印"像代码"的行
keys = ("StructureSystem", "Structure", "swStructure", "Member", "CreateStructure",
        "Set ", "Dim ", "swSelMgr", "Extension", "GetSpecificFeature", "Corner")
shown = 0
for i, l in enumerate(lines):
    s = l.strip()
    if not s or len(s) < 4:
        continue
    if any(k in s for k in keys):
        print("    %s" % s[:126])
        shown += 1
        if shown >= 46:
            break
print("\n  \u5171\u5370 %d \u884c\uff08\u53bb\u6807\u7b7e\u540e\u5168\u6587 %d \u884c\uff09" % (shown, len(lines)))
