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
       .replace("\\u0026quot;", Q))
t2 = re.sub(r"(?i)<br\s*/?>", "\n", t2)
t2 = re.sub(r"(?i)</p>", "\n", t2)
t2 = re.sub(r"<[^>]+>", "", t2)
raw = [l.strip() for l in t2.splitlines()]
#: ★ 把断行接起来（★ 原文被 <br> 切碎了）
lines = []
buf = ""
for l in raw:
    if not l:
        continue
    l = l.replace("&nbsp;", "").strip()
    if not l:
        continue
    if l.endswith((",", "_", "&", "=")) or l.startswith(("Set ", "Dim ", "stat ", "Debug")):
        buf = (buf + " " + l).strip() if buf else l
        continue
    buf = (buf + " " + l).strip() if buf and not l.startswith(("Set ", "Dim ", "stat ", "Debug", "'")) else (buf or l)
    lines.append(buf)
    buf = ""
if buf:
    lines.append(buf)
print("  拼接后 %d 行（★ 原文 451 行）" % len(lines))
for i, l in enumerate(lines):
    if 8 <= i <= 46:
        print("   L%-3d %s" % (i, l[:128]))
