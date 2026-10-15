import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
B = Path(r"D:\Program Files\SOLIDWORKS Corp\JLCFA Parts Library Plugin Full Version v2.4.1-20260918-1")
for p in sorted(B.rglob("*.exe")):
    if p.stat().st_size > 40_000_000: continue
    raw = p.read_bytes()
    hits = set()
    for m in re.findall(rb"(?:[ -~]\x00){5,80}", raw):
        try: s = m.decode("utf-16le").strip()
        except Exception: continue
        if re.search(r"^(--|/|/p |arg|param|command|build|model|export|generate)", s, re.I):
            hits.add(s)
    if hits:
        print("### %s" % p.name)
        for h in sorted(hits)[:12]:
            print("   ", h[:76])