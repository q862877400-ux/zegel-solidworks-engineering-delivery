import re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
for p in [r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt"]:
    txt = Path(p).read_text(encoding="utf-8", errors="replace")
SIG = re.compile(r"^\S+\s+(\w+)\s*\((.*)\)$")
cur=None
print("=== 全程序集里含 Orient 的成员 ===")
for l in txt.splitlines():
    if l.startswith("## "): cur=l[3:].strip(); continue
    h = SIG.match(l.strip())
    if not h: continue
    if "orient" in h.group(1).lower():
        ps=[a.strip() for a in h.group(2).split(",") if a.strip()]
        print("   %-28s %-34s %d 参" % (cur, h.group(1), len([a for a in ps if not a.endswith("&")])))
