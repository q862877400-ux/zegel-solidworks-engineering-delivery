import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
B = Path(r"D:\Program Files\SOLIDWORKS Corp\JLCFA Parts Library Plugin Full Version v2.4.1-20260918-1\ForFaceSelector")
# 找 URL/路径拼接相关的字符串（.NET 会以 UTF-16 存字面量）
pat = re.compile(rb"(?:[ -~]\x00){6,90}")
KEY = re.compile(r"(model|zip|path|file|dir|unpack|extract|sw|cfg|config)", re.I)
hits = {}
for dll in sorted(B.glob("*.dll")):
    raw = dll.read_bytes()
    for m in pat.findall(raw):
        try: s = m.decode("utf-16le")
        except Exception: continue
        if KEY.search(s) and ("/" in s or "\\" in s or "zip" in s.lower()):
            hits.setdefault(dll.name, set()).add(s.strip())
for name, ss in sorted(hits.items(), key=lambda kv: -len(kv[1]))[:8]:
    print("### %s  (%d 条)" % (name, len(ss)))
    for s in sorted(ss)[:14]:
        print("   ", s[:88])