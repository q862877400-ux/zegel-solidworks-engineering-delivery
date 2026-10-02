import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
Q = chr(34)
root = Path(r"D:\AI\SW\AI Solidworks\官方文档\SWhelp")
f = list(root.rglob("*swconst~*swStructureSystemMemberCreationType_e.html"))[0]
t = f.read_text(encoding="utf-8", errors="replace")
t2 = (t.replace("\\n", "\n").replace("\\u003c", "<").replace("\\u003e", ">")
       .replace("\\" + Q, Q).replace("\\u0026nbsp;", " "))
t2 = re.sub(r"<[^>]+>", " ", t2)
t2 = re.sub(r"[ \t]+", " ", t2)
seen = set()
out = []
for l in (x.strip() for x in t2.splitlines()):
    if not l or len(l) < 2 or l in seen:
        continue
    seen.add(l)
    out.append(l)
print("  去重后 %d 行；含 'Structure' 或 '=' 的：" % len(out))
for l in out:
    if "Structure" in l or "=" in l or "Primary" in l or "Secondary" in l:
        print("    " + l[:120])
print()
print("  --- 最后 12 行（★ 常有 See Also / Remarks）---")
for l in out[-12:]:
    print("    " + l[:120])
