import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
root = Path(r"D:\AI\SW\AI Solidworks\官方文档\SWhelp")
f = list(root.rglob("*IModelDocExtension~CreateStructureSystem.html"))[0]
t = f.read_text(encoding="utf-8", errors="replace")
Q = chr(34)
t2 = (t.replace("\\n", "\n").replace("\\u003c", "<").replace("\\u003e", ">")
       .replace("\\" + Q, Q).replace("\\u0026nbsp;", " "))
t2 = re.sub(r"<[^>]+>", " ", t2)
t2 = re.sub(r"[ \t]+", " ", t2)
lines = [l.strip() for l in t2.splitlines() if l.strip() and len(l.strip()) > 2]
print("  文件 %d 字节 / 去标签后 %d 行" % (f.stat().st_size, len(lines)))
seen = set()
keys = ("Syntax", "Function", "ByVal", "ByRef", "Return", "Remarks", "Example",
        "Parameters", "Array", "Member", "error", "Description", "structure")
for l in lines:
    if l in seen:
        continue
    seen.add(l)
    if any(k in l for k in keys):
        print("    " + l[:132])
