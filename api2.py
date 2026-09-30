import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
B = Path(r"D:\Program Files\SOLIDWORKS Corp\JLCFA Parts Library Plugin Full Version v2.4.1-20260918-1\ForFaceSelector")
# 3) 所有 DLL 里的 URL 与端点（含 ASCII 与 UTF-16）
print("=== 全部 DLL 的 URL/端点（去重）===")
seen = set()
for p in sorted(B.glob("*.dll")):
    if p.stat().st_size > 7_000_000: continue
    raw = p.read_bytes()
    hits = set()
    for m in re.findall(rb"(?:[ -~]\x00){8,140}", raw):
        try: s = m.decode("utf-16le").strip()
        except Exception: continue
        if re.search(r"https?://[a-z0-9]|/api/|/biz/|forface3d|jlc", s, re.I):
            hits.add(s)
    for m in re.findall(rb"https?://[a-zA-Z0-9._/\-]{10,110}", raw):
        hits.add(m.decode())
    if hits:
        print("### %s" % p.name)
        for u in sorted(hits)[:12]:
            if u in seen: continue
            seen.add(u)
            print("   ", u[:96])