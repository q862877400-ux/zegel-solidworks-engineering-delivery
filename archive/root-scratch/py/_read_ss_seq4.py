import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
Q = chr(34)
root = Path(r"D:\AI\SW\AI Solidworks\官方文档\SWhelp")
f = list(root.rglob("Access_Structure_System_Corner_Treatments_Example_VB.htm"))[0]
t = f.read_text(encoding="utf-8", errors="replace")
t2 = (t.replace("\\u003c", "<").replace("\\u003e", ">")
       .replace("\\" + Q, Q).replace("\\u0026nbsp;", " ").replace("\\u0026amp;", "&")
       .replace("\\u0026quot;", Q).replace("\\u0026lt;", "<").replace("\\u0026gt;", ">"))
t2 = re.sub(r"(?i)<br\s*/?>", " ", t2)
t2 = re.sub(r"(?i)</p>", " ", t2)
t2 = re.sub(r"<[^>]+>", " ", t2)
t2 = t2.replace("&nbsp;", " ")
t2 = re.sub(r"[ \t]+", " ", t2)
i = t2.find("CreateStructureSystemMemberData (0)")
j = t2.find("CreateStructureSystem memDataArray")
seg = t2[i:j + 120] if 0 < i < j else t2[max(0, i - 100):i + 2600]
seg = seg.replace("&quot;", Q)
print("  ==== 从 MemberData 到 CreateStructureSystem 之间（%d 字符）====" % len(seg))
#: ★ 按 VBA 语句切
for s in re.split(r"(?=(?:Set |stat = |profDef\.|segments\(|memData|Debug\.Print|For |Next|Dim ))", seg):
    s = s.strip()
    if s and len(s) > 2:
        print("    " + s[:170])
