import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
B = Path(r"D:\Program Files\SOLIDWORKS Corp\JLCFA Parts Library Plugin Full Version v2.4.1-20260918-1\ForFaceSelector")
pat = re.compile(rb"(?:[ -~]\x00){5,120}")
for dll in ("sw-fa-prod-selector35.DAL.dll", "sw-fa-prod-selector35.Model.dll",
            "sw-fa-prod-selector35.dll", "sw-fa-prod-selector35.BLL.dll"):
    p = B / dll
    if not p.is_file(): continue
    raw = p.read_bytes()
    ss = set()
    for m in pat.findall(raw):
        try: s = m.decode("utf-16le")
        except Exception: continue
        if re.search(r"(model|zip|path|file|dir|select |from |where )", s, re.I):
            ss.add(s.strip())
    print("### %s (%d)" % (dll, len(ss)))
    for s in sorted(ss)[:20]:
        print("   ", s[:100])
    print()