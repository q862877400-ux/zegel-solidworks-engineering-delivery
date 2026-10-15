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
#: ★ 按语句切开：★ Set / stat = / Debug / For / Next / If …
parts = re.split(r"(?=(?:Set |stat = |Debug\.Print|For |Next|End |If |Else|With |Dim ))", t2)
seq = [p.strip() for p in parts if p.strip()]
print("  切成 %d 段（★ 原文 451 行 / 71 KB）" % len(seq))
for s in seq:
    if any(k in s for k in ("MemberProfile", "ProfileStandard", "ProfileType", "ProfileSize",
                            "CreateStructureSystem", "memData", "PrimaryMember",
                            "PathSegment", "StructureSystemMemberType", "GetSpecificFeature")):
        print("    " + s[:190].replace("\n", " "))
