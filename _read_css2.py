import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
root = Path(r"D:\AI\SW\AI Solidworks\官方文档\SWhelp")
Q = chr(34)
for pat in ("*IModelDocExtension~CreateStructureSystemMemberData.html",
            "*IStructureSystemMemberFeatureData.html",
            "*IPrimaryMemberPointLengthFeatureData.html"):
    hits = list(root.rglob(pat))
    print("  ===== %s  ⇒ %d 个 =====" % (pat, len(hits)))
    if not hits:
        continue
    f = hits[0]
    t = f.read_text(encoding="utf-8", errors="replace")
    t2 = (t.replace("\\n", "\n").replace("\\u003c", "<").replace("\\u003e", ">")
           .replace("\\" + Q, Q).replace("\\u0026nbsp;", " "))
    t2 = re.sub(r"<[^>]+>", " ", t2)
    t2 = re.sub(r"[ \t]+", " ", t2)
    seen = set()
    n = 0
    for l in (x.strip() for x in t2.splitlines()):
        if not l or len(l) < 3 or l in seen:
            continue
        seen.add(l)
        if any(k in l for k in ("Syntax", "Function", "ByVal", "ByRef", "Return",
                                "Remarks", "Example", "Parameters", "Array", "Description",
                                "creates", "Creates", "Type", "Get")):
            print("      " + l[:126])
            n += 1
            if n >= 14:
                break
    print()
